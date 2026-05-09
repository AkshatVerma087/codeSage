from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    redis: str
    vector_db: str
    model_loaded: bool
    model_path: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    redis_status = "not_configured"
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            await redis_client.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "error"

    model_loaded = Path(settings.llm_model_path).expanduser().exists()
    status = "ok" if redis_status == "ok" else "degraded"

    return HealthResponse(
        status=status,
        redis=redis_status,
        vector_db=settings.vector_db_backend,
        model_loaded=model_loaded,
        model_path=settings.llm_model_path,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )