"""Semantic retrieval over the local ChromaDB index."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from campusai.config import Settings, get_settings
from campusai.rag.embeddings import EmbeddingModel, FastEmbedEmbeddingModel
from campusai.rag.vector_store import ChromaVectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    """A document chunk returned by vector search."""

    id: str
    content: str
    source: str
    source_path: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None
    distance: float | None = None
    authority_level: str | None = None
    source_type: str | None = None


class QueryableVectorStore(Protocol):
    def query(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        """Return nearest chunks for a query embedding."""

    def count(self) -> int:
        """Return number of indexed chunks."""


class ChromaRetrieverStore:
    """Read-only query adapter for the existing Chroma vector store."""

    def __init__(self, persist_path: str, collection_name: str) -> None:
        self._store = ChromaVectorStore(persist_path=persist_path, collection_name=collection_name)
        self._collection = self._store.collection

    def count(self) -> int:
        try:
            return int(self._collection.count())
        except Exception:
            return 0

    def query(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        if top_k <= 0 or not query_embedding or self.count() == 0:
            return []

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []

        return _parse_chroma_results(results)


_ML_WORD = re.compile(r"\bml\b", re.IGNORECASE)

# Strong study-path / “what to learn before X” phrasing (avoids reranking generic “prerequisite for course Y” queries).
_STUDY_PATH_STRONG_MARKERS = (
    "before learning",
    "prepare for",
    "should i learn before",
    "should we learn before",
    "what should i learn before",
    "what should we learn before",
    "study path",
)

# Paths / filenames that identify the packaged local advisor markdown.
_LOCAL_ADVISOR_SOURCE_MARKERS = (
    "campusai_local_advisor_rules",
    "local_advisor",
    "documents/local/",
    "/local/campusai",
)

# Extra semantic retrieval breadth for study-path questions, then rerank locally.
_STUDY_PATH_FETCH_CAP = 32


def is_study_path_prerequisite_query(question: str) -> bool:
    """True when the question is about study ordering / ML prep, not generic catalog policy lookup."""

    q = (question or "").lower()
    if any(marker in q for marker in _STUDY_PATH_STRONG_MARKERS):
        return True
    if "machine learning" in q or _ML_WORD.search(q) is not None:
        if "prerequisite" in q or "prerequisites" in q:
            return True
        if "before" in q and "learn" in q:
            return True
    return False


def chunk_matches_local_advisor_source(chunk: RetrievedChunk) -> bool:
    path = (chunk.source_path or "").lower().replace("\\", "/")
    src = (chunk.source or "").lower().replace("\\", "/")
    blob = f"{path} {src}"
    return any(marker in blob for marker in _LOCAL_ADVISOR_SOURCE_MARKERS)


def rerank_study_path_chunks(chunks: list[RetrievedChunk], *, top_k: int) -> list[RetrievedChunk]:
    """Prefer local advisor / heuristic chunks for study-path queries; keep vector order as tie-breaker."""

    if top_k <= 0 or not chunks:
        return []

    def score_tuple(chunk: RetrievedChunk, position: int) -> tuple[float, int]:
        dist = chunk.distance
        base = -float(dist) if dist is not None else 0.0
        boost = 0.0
        if chunk_matches_local_advisor_source(chunk):
            boost += 2.25
        auth = (chunk.authority_level or "").lower()
        if auth in {"heuristic_local", "heuristic"}:
            boost += 0.35
        # Slight preference for heuristic-like source_type from ingestion manifest echo.
        st = (chunk.source_type or "").lower()
        if "heuristic" in st:
            boost += 0.15
        return (base + boost, -position)

    ordered = sorted(enumerate(chunks), key=lambda pair: score_tuple(pair[1], pair[0]), reverse=True)
    return [pair[1] for pair in ordered[:top_k]]


def study_path_fetch_size(requested_top_k: int) -> int:
    return min(_STUDY_PATH_FETCH_CAP, max(requested_top_k * 4, 16))


class Retriever:
    """Embeds user questions and retrieves relevant indexed chunks."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        embedding_model: EmbeddingModel | None = None,
        vector_store: QueryableVectorStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.embedding_model = embedding_model or FastEmbedEmbeddingModel(self.settings.embedding_model)
        self.vector_store = vector_store or ChromaRetrieverStore(
            persist_path=self.settings.vector_store_path,
            collection_name=self.settings.chroma_collection,
        )

    def has_index(self) -> bool:
        return self.vector_store.count() > 0

    def retrieve(self, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        normalized = question.strip()
        if not normalized or not self.has_index():
            return []
        k = top_k or self.settings.rag_top_k
        query_embedding = self.embedding_model.embed([normalized])[0]
        study_path = is_study_path_prerequisite_query(normalized)
        fetch_k = study_path_fetch_size(k) if study_path else k
        chunks = self.vector_store.query(query_embedding, fetch_k)
        if study_path:
            return rerank_study_path_chunks(chunks, top_k=k)
        return chunks[:k]


def index_exists(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    path = Path(settings.vector_store_path)
    if not path.exists():
        return False
    try:
        return ChromaRetrieverStore(settings.vector_store_path, settings.chroma_collection).count() > 0
    except Exception:
        return False


def _first_row(value: Any) -> list[Any]:
    if not value:
        return []
    if isinstance(value, list) and value and isinstance(value[0], list):
        return value[0]
    if isinstance(value, list):
        return value
    return []


def _parse_chroma_results(results: dict[str, Any]) -> list[RetrievedChunk]:
    ids = _first_row(results.get("ids"))
    documents = _first_row(results.get("documents"))
    metadatas = _first_row(results.get("metadatas"))
    distances = _first_row(results.get("distances"))

    chunks: list[RetrievedChunk] = []
    for idx, chunk_id in enumerate(ids):
        metadata = metadatas[idx] if idx < len(metadatas) and isinstance(metadatas[idx], dict) else {}
        chunks.append(
            RetrievedChunk(
                id=str(chunk_id),
                content=str(documents[idx]) if idx < len(documents) and documents[idx] is not None else "",
                source=str(metadata.get("source") or metadata.get("filename") or "unknown source"),
                source_path=_optional_str(metadata.get("source_path") or metadata.get("path")),
                page_number=_optional_int(metadata.get("page_number") or metadata.get("page")),
                chunk_index=_optional_int(metadata.get("chunk_index")),
                distance=_optional_float(distances[idx]) if idx < len(distances) else None,
                authority_level=_optional_str(metadata.get("authority_level")),
                source_type=_optional_str(metadata.get("source_type")),
            )
        )
    return chunks


def _optional_str(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
