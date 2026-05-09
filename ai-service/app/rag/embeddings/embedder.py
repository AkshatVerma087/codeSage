from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from app.rag.embeddings.encoder import Encoder


class Embedder:
    def __init__(self, model_name: str | None = None) -> None:
        self.encoder = Encoder()
        self.embedding_dim = self.encoder.embedding_dim
        self.model_name = model_name or self.encoder.model.__class__.__name__

    def encode(self, texts: str | Sequence[str], batch_size: int = 32, show_progress_bar: bool = False) -> np.ndarray:
        _ = show_progress_bar
        return self.encoder.encode_texts(texts, batch_size=batch_size)

    def encode_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.encoder.encode_chunks(chunks)

    def similarity(self, query: str, documents: list[str]) -> np.ndarray:
        query_emb = self.encoder.encode_texts(query)[0]
        doc_embs = self.encoder.encode_texts(documents)
        query_norm = query_emb / np.linalg.norm(query_emb)
        doc_norms = doc_embs / np.linalg.norm(doc_embs, axis=1, keepdims=True)
        return np.dot(doc_norms, query_norm).astype(np.float32)

