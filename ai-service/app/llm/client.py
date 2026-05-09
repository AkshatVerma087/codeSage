"""Compatibility client that delegates to the local GGUF generator."""

from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.llm.generator import LLMGenerator


class LLMClient:
    def __init__(self) -> None:
        self.model_name = settings.llm_model_path
        self.generator = LLMGenerator()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
        backend: Optional[str] = None,
    ) -> str:
        selected_backend = (backend or settings.llm_backend).lower().strip()
        if selected_backend not in {"local", "llama-cpp", "gguf"}:
            raise ValueError(f"Unsupported backend: {selected_backend}")
        return self.generator.generate(
            question=prompt,
            context="",
            system_prompt=system_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
