from __future__ import annotations

import asyncio
import importlib
import threading
from typing import Any, Sequence

import numpy as np

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class Encoder:
    _instance: Encoder | None = None
    _lock = threading.Lock()

    def __new__(cls) -> Encoder:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    sentence_transformers_module = importlib.import_module("sentence_transformers")
                    instance.model = sentence_transformers_module.SentenceTransformer(
                        settings.embedding_model,
                        device=settings.embedding_device,
                    )
                    instance.embedding_dim = int(instance.model.get_sentence_embedding_dimension())
                    instance.code_prefix = "Represent this code for retrieval: "
                    instance.query_prefix = "Represent this query for retrieval: "
                    cls._instance = instance
                    logger.info(
                        "Embedding model loaded",
                        extra={
                            "model": settings.embedding_model,
                            "device": settings.embedding_device,
                            "embedding_dim": instance.embedding_dim,
                        },
                    )
        return cls._instance

    def _normalize_input(self, texts: str | Sequence[str]) -> list[str]:
        if isinstance(texts, str):
            return [texts]
        return [text for text in texts if text]

    def encode_texts(self, texts: str | Sequence[str], batch_size: int | None = None) -> np.ndarray:
        normalized_texts = self._normalize_input(texts)
        if not normalized_texts:
            return np.empty((0, self.embedding_dim), dtype=np.float32)

        vectors = self.model.encode(
            normalized_texts,
            batch_size=batch_size or settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)

    async def encode_texts_async(
        self,
        texts: str | Sequence[str],
        batch_size: int | None = None,
    ) -> np.ndarray:
        return await asyncio.to_thread(self.encode_texts, texts, batch_size)

    def encode_query(self, query: str) -> np.ndarray:
        vectors = self.encode_texts(f"{self.query_prefix}{query}")
        return vectors[0]

    def encode_chunks(self, chunks: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        texts = [f"{self.code_prefix}{chunk.get('source_code', chunk.get('text', ''))}" for chunk in chunks]
        vectors = self.encode_texts(texts)
        result = list(chunks)
        for chunk, vector in zip(result, vectors, strict=False):
            chunk["embedding"] = vector
        return result
