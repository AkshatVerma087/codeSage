from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class ChunkWindow:
    file_path: str
    symbol_name: str
    language: str
    line_start: int
    line_end: int
    source_code: str
    chunk_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "language": self.language,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "source_code": self.source_code,
            "chunk_type": self.chunk_type,
        }


class Chunker:
    def __init__(self, max_lines: int = 60, overlap_lines: int = 12) -> None:
        self.max_lines = max_lines
        self.overlap_lines = overlap_lines
        self._boundary_patterns = [
            re.compile(r"^\s*(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)"),
            re.compile(r"^\s*(export\s+)?(async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)"),
            re.compile(r"^\s*(export\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)"),
            re.compile(r"^\s*func\s+([A-Za-z_][A-Za-z0-9_]*)"),
            re.compile(r"^\s*(public|private|protected)?\s*(static\s+)?(class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)"),
        ]

    def _symbol_from_line(self, line: str, fallback: str) -> str:
        for pattern in self._boundary_patterns:
            match = pattern.match(line)
            if match:
                groups = [group for group in match.groups() if group]
                if groups:
                    return groups[-1]
        return fallback

    def chunk_file(self, file_path: Path, relative_path: str, language: str = "text") -> list[ChunkWindow]:
        try:
            source_code = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        lines = source_code.splitlines()
        if not lines:
            return []

        chunks: list[ChunkWindow] = []
        current_start = 0
        chunk_index = 0
        previous_symbol = f"chunk_{chunk_index}"

        def flush(end_index: int) -> None:
            nonlocal current_start, chunk_index, previous_symbol
            if end_index < current_start:
                return
            chunk_lines = lines[current_start : end_index + 1]
            if not chunk_lines:
                return
            chunks.append(
                ChunkWindow(
                    file_path=relative_path,
                    symbol_name=previous_symbol,
                    language=language,
                    line_start=current_start + 1,
                    line_end=end_index + 1,
                    source_code="\n".join(chunk_lines),
                    chunk_type="chunk",
                )
            )
            chunk_index += 1
            previous_symbol = f"chunk_{chunk_index}"
            current_start = max(end_index + 1 - self.overlap_lines, 0)

        for index, line in enumerate(lines):
            symbol_name = self._symbol_from_line(line, previous_symbol)
            is_boundary = bool(line.strip()) and symbol_name != previous_symbol
            reached_window = (index - current_start + 1) >= self.max_lines

            if (is_boundary and index > current_start) or reached_window:
                flush(index - 1 if is_boundary else index)
                previous_symbol = symbol_name

        if current_start < len(lines):
            chunk_lines = lines[current_start:]
            if chunk_lines:
                chunks.append(
                    ChunkWindow(
                        file_path=relative_path,
                        symbol_name=previous_symbol,
                        language=language,
                        line_start=current_start + 1,
                        line_end=len(lines),
                        source_code="\n".join(chunk_lines),
                        chunk_type="chunk",
                    )
                )

        logger.debug(
            "chunk.file",
            extra={"file_path": relative_path, "chunks": len(chunks), "language": language},
        )
        return chunks
