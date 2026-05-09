from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.llm.client import LLMClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the local Mistral LLM path.")
    parser.add_argument(
        "--prompt",
        default="Write one sentence explaining what retrieval augmented generation is.",
        help="Prompt to send to the model.",
    )
    parser.add_argument(
        "--system-prompt",
        default="",
        help="Optional system prompt to prepend.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=64,
        help="Maximum number of tokens to generate.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for generation.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate configuration and imports without loading the model.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("AI service configuration")
    print(f"- backend: {settings.llm_backend}")
    print(f"- model: {settings.llm_model_path}")
    print(f"- embedding model: {settings.embedding_model}")

    if args.check_only:
        print("Smoke check passed: configuration loaded successfully.")
        return 0

    client = LLMClient()
    output = client.generate(
        prompt=args.prompt,
        system_prompt=args.system_prompt,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        backend="local",
    )

    print("\nModel output:\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
