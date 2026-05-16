"""PDF loading utilities with page-level metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPage:
    text: str
    source: str
    page_number: int
    source_path: str
    document_type: str | None = None
    authority: str | None = None
    source_type: str | None = None
    is_official_policy: bool | None = None
    university: str | None = None
    country: str | None = None
    language: str | None = None


def find_pdf_files(raw_data_dir: str | Path) -> list[Path]:
    root = Path(raw_data_dir)
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.pdf") if path.is_file())


def load_pdf_pages(pdf_path: str | Path) -> list[DocumentPage]:
    path = Path(pdf_path)

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF loading. Install the project dependencies.") from exc

    pages: list[DocumentPage] = []
    with fitz.open(path) as document:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if not text:
                continue
            pages.append(
                DocumentPage(
                    text=text,
                    source=path.name,
                    page_number=index,
                    source_path=str(path),
                    document_type="pdf",
                )
            )
    return pages
