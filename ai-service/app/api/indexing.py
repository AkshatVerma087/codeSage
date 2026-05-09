"""API endpoints for repository indexing."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.redis_utils import get_job_progress, get_job_state, set_job_progress, set_job_state
from app.core.security import acquire_repo_lock, enforce_rate_limit, release_repo_lock, verify_api_key
from app.tasks import index_repository

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(prefix="/v1/index", tags=["indexing"])


class IndexRequest(BaseModel):
    """Request payload for starting a repository index job."""

    repo_url: str = Field(..., description="Git repository URL")
    repo_id: str = Field(..., description="Unique repository identifier")
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub token for private repositories",
    )


class IndexResponse(BaseModel):
    """Response for index job submission."""

    job_id: str
    repo_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status query."""

    job_id: str
    repo_id: str
    status: str
    progress: Optional[int] = None
    stage: Optional[str] = None
    chunk_count: Optional[int] = None
    indexed_files: Optional[int] = None
    error_message: Optional[str] = None
    repo_url: Optional[str] = None


@router.post("", response_model=IndexResponse, status_code=202)
async def submit_index_job(
    payload: IndexRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> IndexResponse:
    redis: Redis = request.app.state.redis

    if not await enforce_rate_limit(redis, api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    lock_acquired = await acquire_repo_lock(redis, payload.repo_id)
    if not lock_acquired:
        raise HTTPException(
            status_code=409,
            detail=f"Repository {payload.repo_id} is already being indexed",
        )

    job_id = str(uuid.uuid4())

    await set_job_state(
        redis,
        job_id,
        {
            "status": "pending",
            "repo_id": payload.repo_id,
            "repo_url": payload.repo_url,
            "chunk_count": 0,
            "indexed_files": 0,
        },
    )
    await set_job_progress(redis, job_id, {"stage": "queued", "progress": 0})

    index_repository.apply_async(
        kwargs={
            "repo_url": payload.repo_url,
            "repo_id": payload.repo_id,
            "github_token": payload.github_token,
            "api_key": api_key,
        },
        task_id=job_id,
    )

    logger.info(
        "index.job.submitted",
        extra={"job_id": job_id, "repo_id": payload.repo_id},
    )

    return IndexResponse(
        job_id=job_id,
        repo_id=payload.repo_id,
        status="pending",
        message="Index job accepted and queued",
    )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, request: Request) -> JobStatusResponse:
    redis: Redis = request.app.state.redis

    job_state = await get_job_state(redis, job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    progress_state = await get_job_progress(redis, job_id) or {}

    return JobStatusResponse(
        job_id=job_id,
        repo_id=str(job_state.get("repo_id", "unknown")),
        status=str(job_state.get("status", "unknown")),
        progress=progress_state.get("progress"),
        stage=progress_state.get("stage"),
        chunk_count=job_state.get("chunk_count"),
        indexed_files=job_state.get("indexed_files"),
        error_message=job_state.get("error_message"),
        repo_url=job_state.get("repo_url"),
    )


@router.delete("/{job_id}", status_code=204)
async def cancel_job(
    job_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> None:
    redis: Redis = request.app.state.redis

    if not await enforce_rate_limit(redis, api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    job_state = await get_job_state(redis, job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    current_status = str(job_state.get("status", "unknown"))
    if current_status in {"completed", "failed", "cancelled"}:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot cancel a {current_status} job",
        )

    await set_job_state(
        redis,
        job_id,
        {
            **job_state,
            "status": "cancelled",
            "error_message": "Job cancelled by user",
        },
    )
    await set_job_progress(redis, job_id, {"stage": "cancelled", "progress": 0})

    repo_id = job_state.get("repo_id")
    if isinstance(repo_id, str) and repo_id:
        await release_repo_lock(redis, repo_id)

    logger.info(
        "index.job.cancelled",
        extra={"job_id": job_id, "repo_id": repo_id},
    )


__all__ = ["router"]
