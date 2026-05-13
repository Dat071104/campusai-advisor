"""Citation formatting utilities for RAG answers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from campusai.rag.retriever import RetrievedChunk


@dataclass(frozen=True)
class Citation:
    source: str
    chunk_id: str
    page_number: int | None
    chunk_index: int | None
    authority_level: str
    authority_label: str
    source_path: str | None = None
    distance: float | None = None
    excerpt: str | None = None


def load_source_manifest(path: str | Path = "data/processed/source_manifest.json") -> dict[str, dict[str, Any]]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    entries: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key in ("sources", "entries", "files"):
            value = payload.get(key)
            if isinstance(value, list):
                entries = [item for item in value if isinstance(item, dict)]
                break
        if not entries and all(isinstance(value, dict) for value in payload.values()):
            entries = [value for value in payload.values() if isinstance(value, dict)]
    elif isinstance(payload, list):
        entries = [item for item in payload if isinstance(item, dict)]

    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        for field in ("source", "name", "filename", "path", "source_path", "local_path"):
            value = entry.get(field)
            if value:
                indexed[str(value).lower()] = entry
                indexed[Path(str(value)).name.lower()] = entry
    return indexed


def build_citations(
    chunks: list[RetrievedChunk],
    *,
    manifest: dict[str, dict[str, Any]] | None = None,
    max_citations: int | None = None,
) -> list[Citation]:
    manifest = manifest if manifest is not None else load_source_manifest()
    citations: list[Citation] = []
    seen: set[str] = set()

    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        authority = chunk.authority_level or infer_authority_level(chunk, manifest)
        citations.append(
            Citation(
                source=chunk.source,
                chunk_id=chunk.id,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                authority_level=authority,
                authority_label=authority_label(authority),
                source_path=chunk.source_path,
                distance=chunk.distance,
                excerpt=_excerpt(chunk.content),
            )
        )
        if max_citations and len(citations) >= max_citations:
            break
    return citations


def infer_authority_level(chunk: RetrievedChunk, manifest: dict[str, dict[str, Any]] | None = None) -> str:
    manifest = manifest or {}
    candidates = [chunk.source, chunk.source_path or "", Path(chunk.source_path or chunk.source).name]
    for candidate in candidates:
        entry = manifest.get(candidate.lower())
        if entry:
            value = entry.get("authority_level") or entry.get("authority") or entry.get("source_type") or entry.get("type")
            if value:
                return normalize_authority(str(value))

    haystack = " ".join(candidates).lower()
    if any(token in haystack for token in ("berkeley", "guide", "catalog", "pdf")):
        return "official"
    if any(token in haystack for token in ("fireroad", "mit", "api")):
        return "public_demo_structured"
    if any(token in haystack for token in ("local", "advisor", "heuristic", "rule")):
        return "heuristic_local"
    return "unknown"


def normalize_authority(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"official", "catalog", "catalog_style", "official_catalog", "university"}:
        return "official"
    if normalized in {"public", "demo", "structured", "api", "public_demo_structured"}:
        return "public_demo_structured"
    if normalized in {"heuristic", "local", "local_heuristic", "heuristic_local", "advisor_rule"}:
        return "heuristic_local"
    return normalized or "unknown"


def authority_label(authority_level: str) -> str:
    labels = {
        "official": "Official/catalog-style source",
        "public_demo_structured": "Public demo structured source",
        "heuristic_local": "Heuristic local advisor source (not official policy)",
        "unknown": "Unknown source authority",
    }
    return labels.get(authority_level, authority_level.replace("_", " ").title())


def format_citations_for_prompt(citations: list[Citation]) -> str:
    if not citations:
        return "Không có trích dẫn."
    lines: list[str] = []
    for idx, citation in enumerate(citations, start=1):
        page = f", page {citation.page_number}" if citation.page_number is not None else ""
        lines.append(f"[{idx}] {citation.source}{page}, chunk {citation.chunk_id}, {citation.authority_label}")
    return "\n".join(lines)


def _excerpt(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 1].rstrip()}…"
