from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis_asyncio

from app.api.health import router as health_router
from app.core.config import settings
from app.api.indexing import router as indexing_router
from app.api.query import router as query_router
from app.core.logger import get_logger

logger = get_logger(__name__)


def _parse_allowed_origins(raw_value: str) -> list[str]:
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis_asyncio.Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis_client
    try:
        await redis_client.ping()
        logger.info("redis.ready")
    except Exception as exc:
        logger.warning("redis.unavailable", extra={"error": str(exc)})
    yield
    await redis_client.aclose()


app = FastAPI(
    title="Codesage AI Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(settings.allowed_origins),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(health_router)
app.include_router(indexing_router)
app.include_router(query_router)


