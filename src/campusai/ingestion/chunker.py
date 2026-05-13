"""Text chunking for page-level document content."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from campusai.ingestion.pdf_loader import DocumentPage


@dataclass(frozen=True)
class TextChunk:
    id: str
    text: str
    source: str
    page_number: int
    chunk_index: int
    source_path: str

    @property
    def metadata(self) -> dict[str, str | int]:
        return {
            "source": self.source,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "source_path": self.source_path,
        }


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_pages(
    pages: Iterable[DocumentPage],
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    for page in pages:
        text = normalize_text(page.text)
        if not text:
            continue

        start = 0
        chunk_index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(_make_chunk(page, chunk_text, chunk_index))
                chunk_index += 1
            if end == len(text):
                break
            start = max(0, end - chunk_overlap)

    return chunks


def _make_chunk(page: DocumentPage, text: str, chunk_index: int) -> TextChunk:
    digest = hashlib.sha1(
        f"{page.source}:{page.page_number}:{chunk_index}:{text[:120]}".encode("utf-8")
    ).hexdigest()[:12]
    return TextChunk(
        id=f"{page.source}:p{page.page_number}:c{chunk_index}:{digest}",
        text=text,
        source=page.source,
        page_number=page.page_number,
        chunk_index=chunk_index,
        source_path=page.source_path,
    )
