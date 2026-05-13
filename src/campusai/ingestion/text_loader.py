"""Load plain-text and Markdown documents as single-page DocumentPage rows."""

from __future__ import annotations

from pathlib import Path

from campusai.ingestion.pdf_loader import DocumentPage

LOCAL_ADVISOR_RULES_FILENAME = "campusai_local_advisor_rules.md"


def find_markdown_and_text_files(raw_data_dir: str | Path) -> list[Path]:
    root = Path(raw_data_dir)
    if not root.exists():
        return []
    seen: set[Path] = set()
    out: list[Path] = []
    for pattern in ("*.md", "*.txt"):
        for path in root.rglob(pattern):
            if path.is_file():
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    out.append(path)
    return sorted(out, key=lambda p: str(p).lower())


def _metadata_for_path(path: Path) -> tuple[str, str | None, str | None, bool | None]:
    suffix = path.suffix.lower()
    if suffix == ".md":
        doc_type = "markdown"
    elif suffix == ".txt":
        doc_type = "text"
    else:
        doc_type = "text"

    if path.name == LOCAL_ADVISOR_RULES_FILENAME:
        return doc_type, "heuristic", "local_advisor_rules", False
    return doc_type, None, None, None


def load_text_document_pages(path: str | Path) -> list[DocumentPage]:
    """Read one UTF-8 file as a single logical page (page_number=1)."""

    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    document_type, authority, source_type, is_official = _metadata_for_path(file_path)
    return [
        DocumentPage(
            text=text,
            source=file_path.name,
            page_number=1,
            source_path=str(file_path),
            document_type=document_type,
            authority=authority,
            source_type=source_type,
            is_official_policy=is_official,
        )
    ]
