"""Query endpoint for retrieval augmented generation."""

from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.security import enforce_rate_limit, verify_api_key
from app.llm.generator import LLMGenerator
from app.rag.embeddings.embedder import Embedder
from app.rag.embeddings.vector_store import VectorStore

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(prefix="/v1/query", tags=["query"])


class QueryRequest(BaseModel):
    """Request payload for repository questions."""

    repo_id: str = Field(..., description="Repository identifier to search")
    question: str = Field(..., min_length=1, description="User question")
    top_k: int = Field(6, ge=1, le=20, description="Number of context chunks to retrieve")
    max_new_tokens: int = Field(256, ge=1, le=1024, description="Max tokens to generate")
    temperature: float = Field(0.2, ge=0.0, le=2.0, description="Sampling temperature")
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional custom system prompt",
    )


class QuerySource(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    score: Optional[float] = None
    text: str


class QueryResponse(BaseModel):
    answer: str
    repo_id: str
    sources: list[QuerySource]
    latency_ms: float
    model_path: str


@router.post("", response_model=QueryResponse)
async def query_repository(
    payload: QueryRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> QueryResponse:
    redis: Redis = request.app.state.redis

    if not await enforce_rate_limit(redis, api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    start_time = perf_counter()

    embedder = Embedder()
    query_embedding = await asyncio.to_thread(embedder.encoder.encode_query, payload.question)
    query_embedding = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else list(query_embedding)

    vector_store = VectorStore(embedding_dim=embedder.embedding_dim)
    hits = await vector_store.query_async(
        collection_name=payload.repo_id,
        query_embedding=query_embedding,
        top_k=payload.top_k,
    )

    sources: list[QuerySource] = []
    context_blocks: list[str] = []
    for index, point in enumerate(hits, start=1):
        payload_data = point.payload or {}
        file_path = str(payload_data.get("file_path", "unknown"))
        start_line = int(payload_data.get("start_line", 0) or 0)
        end_line = int(payload_data.get("end_line", 0) or 0)
        symbol_name = payload_data.get("symbol_name")
        text = str(payload_data.get("text", "")).strip()
        score = float(point.score) if point.score is not None else None

        sources.append(
            QuerySource(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                symbol_name=symbol_name,
                score=score,
                text=text,
            )
        )
        context_blocks.append(
            f"[{index}] {file_path}:{start_line}-{end_line}\n{text[:1500]}"
        )

    context = "\n\n".join(context_blocks)

    if not sources:
        answer = "I could not find relevant code context for that repository."
    else:
        generator = LLMGenerator()
        answer = await asyncio.to_thread(
            generator.generate,
            payload.question,
            context,
            payload.system_prompt,
            payload.max_new_tokens,
            payload.temperature,
        )

    latency_ms = round((perf_counter() - start_time) * 1000.0, 2)

    logger.info(
        "query.completed",
        extra={
            "repo_id": payload.repo_id,
            "top_k": payload.top_k,
            "latency_ms": latency_ms,
            "source_count": len(sources),
        },
    )

    return QueryResponse(
        answer=answer,
        repo_id=payload.repo_id,
        sources=sources,
        latency_ms=latency_ms,
        model_path=settings.llm_model_path,
    )


__all__ = ["router"]
