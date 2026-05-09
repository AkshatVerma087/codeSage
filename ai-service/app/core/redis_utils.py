from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings


def job_key(job_id: str) -> str:
    return f"jobs:{job_id}"


def job_progress_key(job_id: str) -> str:
    return f"jobs:{job_id}:progress"


def repo_lock_key(repo_id: str) -> str:
    return f"repo_lock:{repo_id}"


def rate_limit_key(api_key_digest: str) -> str:
    return f"rate_limit:{api_key_digest}"


async def set_job_state(redis: Redis[str], job_id: str, payload: dict[str, Any]) -> None:
    await redis.set(job_key(job_id), json.dumps(payload), ex=settings.job_ttl_seconds)


async def get_job_state(redis: Redis[str], job_id: str) -> dict[str, Any] | None:
    raw_value = await redis.get(job_key(job_id))
    if not raw_value:
        return None
    return json.loads(raw_value)


async def set_job_progress(redis: Redis[str], job_id: str, payload: dict[str, Any]) -> None:
    await redis.set(job_progress_key(job_id), json.dumps(payload), ex=settings.job_ttl_seconds)


async def get_job_progress(redis: Redis[str], job_id: str) -> dict[str, Any] | None:
    raw_value = await redis.get(job_progress_key(job_id))
    if not raw_value:
        return None
    return json.loads(raw_value)


async def cache_json(redis: Redis[str], key: str, payload: dict[str, Any], ttl_seconds: int | None = None) -> None:
    await redis.set(key, json.dumps(payload), ex=ttl_seconds or settings.redis_cache_ttl_seconds)


async def get_cached_json(redis: Redis[str], key: str) -> dict[str, Any] | None:
    raw_value = await redis.get(key)
    if not raw_value:
        return None
    return json.loads(raw_value)


async def acquire_repo_lock(redis: Redis[str], repo_id: str) -> bool:
    return bool(await redis.set(repo_lock_key(repo_id), "1", ex=settings.repo_lock_ttl_seconds, nx=True))


async def release_repo_lock(redis: Redis[str], repo_id: str) -> None:
    await redis.delete(repo_lock_key(repo_id))
