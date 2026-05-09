from __future__ import annotations

from typing import Any, Sequence
import uuid

from qdrant_client import AsyncQdrantClient, models

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QdrantAdapter:
    def __init__(self, embedding_dim: int) -> None:
        self.embedding_dim = embedding_dim
        self.collection_prefix = settings.qdrant_collection_prefix
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )

    def collection_name_for(self, repo_id: str) -> str:
        return f"{self.collection_prefix}_{repo_id}"

    async def ensure_collection(self, repo_id: str) -> str:
        collection_name = self.collection_name_for(repo_id)
        if await self.client.collection_exists(collection_name=collection_name):
            return collection_name

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=self.embedding_dim,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info(
            "Qdrant collection ready",
            extra={"collection": collection_name, "embedding_dim": self.embedding_dim},
        )
        return collection_name

    async def upsert_chunks(
        self,
        repo_id: str,
        chunks: Sequence[dict[str, Any]],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        collection_name = await self.ensure_collection(repo_id)
        points: list[models.PointStruct] = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
            payload = {
                "file_path": chunk.get("file_path", ""),
                "start_line": int(chunk.get("start_line", chunk.get("line_start", 0)) or 0),
                "end_line": int(chunk.get("end_line", chunk.get("line_end", 0)) or 0),
                "symbol_name": chunk.get("symbol_name", ""),
                "text": chunk.get("text", chunk.get("source_code", "")),
                "language": chunk.get("language", ""),
                "chunk_type": chunk.get("chunk_type", ""),
            }
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, str(chunk.get("id") or f"{repo_id}:{index}"))),
                    vector=list(embedding),
                    payload=payload,
                )
            )

        if not points:
            return 0

        await self.client.upsert(collection_name=collection_name, points=points)
        return len(points)

    async def search(
        self,
        repo_id: str,
        query_vector: Sequence[float],
        top_k: int = 6,
        filters: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        collection_name = self.collection_name_for(repo_id)
        return await self.client.search(
            collection_name=collection_name,
            query_vector=list(query_vector),
            limit=top_k,
            with_payload=True,
            query_filter=filters,
        )

    async def delete_collection(self, repo_id: str) -> None:
        collection_name = self.collection_name_for(repo_id)
        if await self.client.collection_exists(collection_name=collection_name):
            await self.client.delete_collection(collection_name=collection_name)
