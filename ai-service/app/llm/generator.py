"""Local GGUF generation wrapper built on llama-cpp-python."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMGenerator:
    """Thread-safe singleton for local GGUF inference."""

    _instance: LLMGenerator | None = None
    _lock = threading.Lock()

    def __new__(cls) -> LLMGenerator:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._client = None
                    instance._model_path = Path(get_settings().llm_model_path).expanduser()
                    cls._instance = instance
        return cls._instance

    def _load(self) -> None:
        if self._client is not None:
            return

        settings = get_settings()
        model_path = self._model_path
        if not model_path.exists():
            raise FileNotFoundError(f"GGUF model not found at {model_path}")

        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "llama-cpp-python is required for local GGUF inference"
            ) from exc

        self._client = Llama(
            model_path=str(model_path),
            n_ctx=settings.llm_n_ctx,
            n_gpu_layers=settings.llm_n_gpu_layers,
            n_threads=settings.llm_n_threads,
            n_batch=settings.llm_n_batch,
            verbose=False,
        )

        logger.info(
            "llm.loaded",
            extra={
                "model_path": str(model_path),
                "backend": settings.llm_backend,
                "n_ctx": settings.llm_n_ctx,
            },
        )

    @staticmethod
    def _build_prompt(
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(system_prompt.strip())
        prompt_parts.append(
            "Use the following code context to answer the question. "
            "If the answer is not present in the context, say so clearly and briefly."
        )
        prompt_parts.append(f"Context:\n{context.strip() if context.strip() else 'No relevant context found.'}")
        prompt_parts.append(f"Question: {question.strip()}")
        prompt_parts.append("Answer:")
        return "\n\n".join(prompt_parts)

    def generate(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
    ) -> str:
        self._load()
        assert self._client is not None

        settings = get_settings()
        prompt = self._build_prompt(question, context, system_prompt=system_prompt)

        try:
            response = self._client.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt or "You are a precise code assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                top_p=settings.llm_top_p,
                max_tokens=max_new_tokens,
                repeat_penalty=settings.llm_repeat_penalty,
            )
            text = response["choices"][0]["message"]["content"]
        except Exception:
            response = self._client.create_completion(
                prompt=prompt,
                temperature=temperature,
                top_p=settings.llm_top_p,
                max_tokens=max_new_tokens,
                repeat_penalty=settings.llm_repeat_penalty,
            )
            text = response["choices"][0]["text"]

        return str(text).strip()


__all__ = ["LLMGenerator"]
