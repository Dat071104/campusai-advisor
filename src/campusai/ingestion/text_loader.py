"""Load plain-text and Markdown documents as single-page DocumentPage rows."""

from __future__ import annotations

from pathlib import Path
import re

from campusai.ingestion.pdf_loader import DocumentPage

LOCAL_ADVISOR_RULES_FILENAME = "campusai_local_advisor_rules.md"
_YAML_FENCE_RE = re.compile(r"```yaml\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)


def _coerce_metadata_value(value: str) -> str | bool:
    normalized = value.strip()
    lowered = normalized.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return normalized


def _parse_simple_yaml_metadata_block(text: str) -> dict[str, str | bool]:
    match = _YAML_FENCE_RE.search(text)
    if not match:
        return {}

    metadata: dict[str, str | bool] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace("-", "_")
        if not key:
            continue
        parsed = _coerce_metadata_value(value)
        metadata[key] = parsed
    return metadata


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


def _metadata_for_path(
    path: Path,
    parsed_metadata: dict[str, str | bool],
) -> tuple[str, str | None, str | None, bool | None, str | None, str | None, str | None]:
    suffix = path.suffix.lower()
    if suffix == ".md":
        doc_type = "markdown"
    elif suffix == ".txt":
        doc_type = "text"
    else:
        doc_type = "text"

    if path.name == LOCAL_ADVISOR_RULES_FILENAME:
        return doc_type, "heuristic", "local_advisor_rules", False, None, None, None

    authority = _optional_text(parsed_metadata.get("source_authority"))
    source_type = _optional_text(parsed_metadata.get("source_type"))
    is_official = _optional_bool(parsed_metadata.get("official_policy"))
    university = _optional_text(parsed_metadata.get("university"))
    country = _optional_text(parsed_metadata.get("country"))
    language = _optional_text(parsed_metadata.get("language"))
    return doc_type, authority, source_type, is_official, university, country, language


def _optional_text(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _optional_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def load_text_document_pages(path: str | Path) -> list[DocumentPage]:
    """Read one UTF-8 file as a single logical page (page_number=1)."""

    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    parsed_metadata = _parse_simple_yaml_metadata_block(text)
    document_type, authority, source_type, is_official, university, country, language = _metadata_for_path(
        file_path,
        parsed_metadata,
    )
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
            university=university,
            country=country,
            language=language,
        )
    ]
