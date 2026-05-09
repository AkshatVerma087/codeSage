from __future__ import annotations

import asyncio
from typing import Any, Sequence

from qdrant_client.http import models

from app.core.logger import get_logger
from app.rag.embeddings.qdrant_adapter import QdrantAdapter

logger = get_logger(__name__)


def _run_sync(coro):
    """Run an async coroutine synchronously, safe for nested event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context — create a new loop in a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


class VectorStore:
    def __init__(self, embedding_dim: int, index_name: str | None = None) -> None:
        self.embedding_dim = embedding_dim
        self.index_name = index_name
        self.adapter = QdrantAdapter(embedding_dim=embedding_dim)

    async def upsert_chunks_async(
        self,
        collection_name: str,
        chunks: Sequence[dict[str, Any]],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        return await self.adapter.upsert_chunks(repo_id=collection_name, chunks=chunks, embeddings=embeddings)

    def upsert_chunks(
        self,
        collection_name: str,
        chunks: Sequence[dict[str, Any]],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        return _run_sync(self.upsert_chunks_async(collection_name, chunks, embeddings))

    async def query_async(
        self,
        collection_name: str,
        query_embedding: Sequence[float],
        top_k: int = 10,
    ) -> list[models.ScoredPoint]:
        return await self.adapter.search(repo_id=collection_name, query_vector=query_embedding, top_k=top_k)

    def query(
        self,
        collection_name: str,
        query_embedding: Sequence[float],
        top_k: int = 10,
    ) -> list[models.ScoredPoint]:
        return _run_sync(self.query_async(collection_name, query_embedding, top_k=top_k))

    async def delete_collection_async(self, collection_name: str) -> None:
        await self.adapter.delete_collection(collection_name)

    def delete_collection(self, collection_name: str) -> None:
        _run_sync(self.delete_collection_async(collection_name))

    def persist(self) -> None:
        logger.info("Qdrant persistence is handled by the vector database")

