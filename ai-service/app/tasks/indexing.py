"""Background task for code repository indexing."""

from __future__ import annotations

import asyncio
from typing import Optional

from celery import Task
from redis.asyncio import Redis

from app.celery_app import celery_app
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.redis_utils import cache_json, release_repo_lock, set_job_progress, set_job_state
from app.rag.embeddings.embedder import Embedder
from app.rag.embeddings.vector_store import VectorStore
from app.rag.parser.repo_loader import RepoLoader
from app.rag.parser.tree_sitter_parser import TreeSitterParser

logger = get_logger(__name__)


class IndexingTask(Task):
    """Base task class with structured logging hooks."""

    def before_start(self, task_id, args, kwargs):
        logger.info("task.start", extra={"job_id": task_id})

    def on_success(self, result, task_id, args, kwargs):
        logger.info("task.success", extra={"job_id": task_id})

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            "task.failure",
            extra={"job_id": task_id, "error": str(exc)},
        )


@celery_app.task(bind=True, base=IndexingTask, name="app.tasks.indexing.index_repository")
def index_repository(
    self,
    repo_url: str,
    repo_id: str,
    github_token: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Index a repository in the background."""
    job_id = self.request.id
    settings = get_settings()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(
            _index_repository_async(
                job_id=job_id,
                repo_url=repo_url,
                repo_id=repo_id,
                github_token=github_token,
                api_key=api_key,
                redis_url=settings.redis_url,
            )
        )
    except Exception as exc:
        logger.error(
            "task.indexing.failed",
            extra={"job_id": job_id, "repo_id": repo_id, "error": str(exc)},
        )
        loop.run_until_complete(_mark_failed(settings.redis_url, job_id, repo_id, str(exc)))
        raise
    finally:
        loop.close()


async def _mark_failed(redis_url: str, job_id: str, repo_id: str, error: str) -> None:
    redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        await set_job_state(
            redis,
            job_id,
            {
                "status": "failed",
                "repo_id": repo_id,
                "error_message": error,
            },
        )
        await set_job_progress(redis, job_id, {"stage": "failed", "progress": 100})
    finally:
        await redis.aclose()


async def _index_repository_async(
    job_id: str,
    repo_url: str,
    repo_id: str,
    github_token: Optional[str],
    api_key: Optional[str],
    redis_url: str,
) -> dict:
    redis = Redis.from_url(redis_url, decode_responses=True)
    repo_loader = RepoLoader()

    try:
        await set_job_state(
            redis,
            job_id,
            {
                "status": "indexing",
                "repo_id": repo_id,
                "repo_url": repo_url,
            },
        )
        await set_job_progress(redis, job_id, {"stage": "cloning", "progress": 5})

        repo_path = repo_loader.clone_repo(
            repo_url=repo_url,
            job_id=job_id,
            github_token=github_token,
        )

        await set_job_progress(redis, job_id, {"stage": "parsing", "progress": 20})
        parser = TreeSitterParser()
        chunks = [chunk.to_dict() for chunk in parser.parse_directory(repo_path)]

        await set_job_progress(redis, job_id, {"stage": "encoding", "progress": 50})
        embedder = Embedder()
        chunk_texts = [chunk.get("source_code", "") for chunk in chunks]
        embeddings = embedder.encode(chunk_texts)

        await set_job_progress(redis, job_id, {"stage": "upserting", "progress": 80})
        vector_store = VectorStore(embedding_dim=embedder.embedding_dim)
        indexed_files: set[str] = set()

        if chunks:
            batch_size = 100
            total_chunks = len(chunks)
            for index in range(0, total_chunks, batch_size):
                batch_chunks = chunks[index : index + batch_size]
                batch_embeddings = embeddings[index : index + batch_size]
                # Convert numpy arrays to plain lists for Qdrant
                batch_embeddings_list = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in batch_embeddings]
                await vector_store.upsert_chunks_async(
                    collection_name=repo_id,
                    chunks=batch_chunks,
                    embeddings=batch_embeddings_list,
                )
                indexed_files.update(
                    chunk.get("file_path", "unknown") for chunk in batch_chunks
                )
                progress = 80 + int((20 * min(index + batch_size, total_chunks)) / total_chunks)
                await set_job_progress(
                    redis,
                    job_id,
                    {"stage": "upserting", "progress": min(progress, 99)},
                )
        else:
            await set_job_progress(redis, job_id, {"stage": "upserting", "progress": 95})

        result = {
            "job_id": job_id,
            "repo_id": repo_id,
            "status": "completed",
            "chunk_count": len(chunks),
            "indexed_files": len(indexed_files),
            "repo_url": repo_url,
        }

        await set_job_progress(redis, job_id, {"stage": "completed", "progress": 100})
        await set_job_state(
            redis,
            job_id,
            {
                "status": "completed",
                "repo_id": repo_id,
                "repo_url": repo_url,
                "chunk_count": len(chunks),
                "indexed_files": len(indexed_files),
            },
        )
        await cache_json(redis, f"job_result:{job_id}", result, ttl_seconds=86400)

        try:
            repo_loader.cleanup(job_id)
        except Exception as cleanup_error:
            logger.warning(
                "task.cleanup.failed",
                extra={"job_id": job_id, "error": str(cleanup_error)},
            )

        return result

    except Exception as exc:
        await set_job_state(
            redis,
            job_id,
            {
                "status": "failed",
                "repo_id": repo_id,
                "repo_url": repo_url,
                "error_message": str(exc),
            },
        )
        await set_job_progress(redis, job_id, {"stage": "failed", "progress": 100})
        raise

    finally:
        try:
            await release_repo_lock(redis, repo_id)
        finally:
            await redis.aclose()


__all__ = ["index_repository"]
