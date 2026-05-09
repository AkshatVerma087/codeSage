from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.parser.chunker import ChunkWindow, Chunker

logger = get_logger(__name__)


class CodeChunk:
    """Semantic code unit extracted from source."""

    def __init__(
        self,
        file_path: str,
        symbol_name: str,
        language: str,
        line_start: int,
        line_end: int,
        source_code: str,
        chunk_type: str,
    ) -> None:
        self.file_path = file_path
        self.symbol_name = symbol_name
        self.language = language
        self.line_start = line_start
        self.line_end = line_end
        self.source_code = source_code
        self.chunk_type = chunk_type

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "language": self.language,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "source_code": self.source_code,
            "chunk_type": self.chunk_type,
        }


class TreeSitterParser:
    """Parse source code for semantic extraction."""

    SUPPORTED_LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".go": "go",
        ".java": "java",
    }

    def __init__(self) -> None:
        self.parsers = {}
        self.chunker = Chunker()
        self._init_parsers()

    def _init_parsers(self) -> None:
        logger.info("TreeSitter parser initialized with chunker fallback mode")

    def _language_for(self, file_path: Path) -> str:
        return self.SUPPORTED_LANGUAGES.get(file_path.suffix, "text")

    def _convert_chunks(self, chunk_windows: list[ChunkWindow]) -> list[CodeChunk]:
        return [
            CodeChunk(
                file_path=window.file_path,
                symbol_name=window.symbol_name,
                language=window.language,
                line_start=window.line_start,
                line_end=window.line_end,
                source_code=window.source_code,
                chunk_type=window.chunk_type,
            )
            for window in chunk_windows
        ]

    def parse_file(
        self,
        file_path: Path,
        repo_base: Path,
        relative_path: str,
    ) -> List[CodeChunk]:
        language = self._language_for(file_path)
        chunk_windows = self.chunker.chunk_file(file_path, relative_path, language=language)
        return self._convert_chunks(chunk_windows)

    def parse_directory(
        self,
        repo_path: Path,
        extensions: Optional[List[str]] = None,
    ) -> List[CodeChunk]:
        extensions = extensions or settings.supported_extensions
        all_chunks: list[CodeChunk] = []

        for file_path in repo_path.rglob("*"):
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if any(part in ["node_modules", "__pycache__", "venv", ".git"] for part in file_path.parts):
                continue

            if file_path.is_file() and file_path.suffix in extensions:
                relative_path = file_path.relative_to(repo_path).as_posix()
                try:
                    chunks = self.parse_file(file_path, repo_path, relative_path)
                    all_chunks.extend(chunks)
                    logger.debug("Parsed %s: %s chunks", relative_path, len(chunks))
                except Exception as exc:
                    logger.warning("Failed to parse %s: %s", relative_path, exc)

        logger.info("Total chunks extracted: %s", len(all_chunks))
        return all_chunks
