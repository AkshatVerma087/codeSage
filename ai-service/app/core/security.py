from __future__ import annotations

import hashlib
from secrets import compare_digest
from typing import Any

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import redis.asyncio as redis_asyncio

from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


def rate_limit_key(api_key: str) -> str:
    digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return f"rate_limit:{digest}"


def repo_lock_key(repo_id: str) -> str:
    return f"repo_lock:{repo_id}"


def job_key(job_id: str) -> str:
    return f"jobs:{job_id}"


def job_progress_key(job_id: str) -> str:
    return f"jobs:{job_id}:progress"


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    if not compare_digest(api_key, settings.secret_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


async def enforce_rate_limit(redis: redis_asyncio.Redis[str], api_key: str) -> bool:
    key = rate_limit_key(api_key)
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.rate_limit_window_seconds)
    return count <= settings.rate_limit_requests


async def acquire_repo_lock(redis: redis_asyncio.Redis[str], repo_id: str) -> bool:
    return bool(
        await redis.set(
            repo_lock_key(repo_id),
            "1",
            ex=settings.repo_lock_ttl_seconds,
            nx=True,
        )
    )


async def release_repo_lock(redis: redis_asyncio.Redis[str], repo_id: str) -> None:
    await redis.delete(repo_lock_key(repo_id))


async def cache_json(redis: redis_asyncio.Redis[str], key: str, value: Any, ttl_seconds: int | None = None) -> None:
    import json
    await redis.set(key, json.dumps(value), ex=ttl_seconds or settings.redis_cache_ttl_seconds)