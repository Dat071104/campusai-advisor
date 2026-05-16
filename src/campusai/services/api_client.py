"""Small HTTP client for Streamlit-to-FastAPI backend mode."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from campusai.rag.answer_chain import AnswerResult
from campusai.rag.citations import Citation
from campusai.rag.retriever import RetrievedChunk


@dataclass(frozen=True)
class BackendStatus:
    status: str
    has_index: bool
    has_groq_key: bool
    raw_data_path: str
    vector_store_path: str
    chroma_collection: str
    embedding_provider: str
    embedding_model: str
    groq_model: str
    rag_top_k: int


class CampusAIBackendClient:
    def __init__(self, base_url: str, *, timeout_seconds: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def status(self) -> BackendStatus:
        payload = self._request("GET", "/status")
        return BackendStatus(
            status=str(payload.get("status") or "unknown"),
            has_index=bool(payload.get("has_index")),
            has_groq_key=bool(payload.get("has_groq_key")),
            raw_data_path=str(payload.get("raw_data_path") or ""),
            vector_store_path=str(payload.get("vector_store_path") or ""),
            chroma_collection=str(payload.get("chroma_collection") or ""),
            embedding_provider=str(payload.get("embedding_provider") or ""),
            embedding_model=str(payload.get("embedding_model") or ""),
            groq_model=str(payload.get("groq_model") or ""),
            rag_top_k=int(payload.get("rag_top_k") or 0),
        )

    def build_index(self, *, reset: bool = True) -> tuple[bool, str]:
        payload = self._request("POST", f"/status/build-index?reset={str(reset).lower()}")
        chunks = int(payload.get("chunks_indexed") or 0)
        message = str(payload.get("message") or "Index request completed.")
        return chunks > 0, message

    def ask_question(self, question: str, student_profile: dict[str, str]) -> AnswerResult:
        payload = self._request(
            "POST",
            "/ask",
            {"question": question, "student_profile": student_profile},
        )
        return AnswerResult(
            answer=str(payload.get("answer") or ""),
            citations=[_citation_from_payload(item) for item in _list_payload(payload.get("citations"))],
            retrieved_chunks=[_chunk_from_payload(item) for item in _list_payload(payload.get("retrieved_chunks"))],
            prompt=None,
            used_live_api=bool(payload.get("used_live_api")),
            missing_api_key=bool(payload.get("missing_api_key")),
            no_context=bool(payload.get("no_context")),
            error=payload.get("error"),
        )

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise RuntimeError(f"Backend request failed with HTTP {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Backend is not reachable at {self.base_url}: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError(f"Backend request timed out after {self.timeout_seconds}s") from exc

        try:
            parsed = json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise RuntimeError("Backend returned invalid JSON.") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("Backend returned an unexpected response shape.")
        return parsed


def _list_payload(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _citation_from_payload(payload: dict[str, Any]) -> Citation:
    return Citation(
        source=str(payload.get("source") or "unknown source"),
        chunk_id=str(payload.get("chunk_id") or ""),
        page_number=_optional_int(payload.get("page_number")),
        chunk_index=_optional_int(payload.get("chunk_index")),
        authority_level=str(payload.get("authority_level") or "unknown"),
        authority_label=str(payload.get("authority_label") or "Unknown source authority"),
        source_path=_optional_str(payload.get("source_path")),
        distance=_optional_float(payload.get("distance")),
        excerpt=_optional_str(payload.get("excerpt")),
    )


def _chunk_from_payload(payload: dict[str, Any]) -> RetrievedChunk:
    return RetrievedChunk(
        id=str(payload.get("id") or ""),
        content=str(payload.get("content") or ""),
        source=str(payload.get("source") or "unknown source"),
        source_path=_optional_str(payload.get("source_path")),
        page_number=_optional_int(payload.get("page_number")),
        chunk_index=_optional_int(payload.get("chunk_index")),
        distance=_optional_float(payload.get("distance")),
        authority_level=_optional_str(payload.get("authority_level")),
        source_type=_optional_str(payload.get("source_type")),
        university=_optional_str(payload.get("university")),
        country=_optional_str(payload.get("country")),
        language=_optional_str(payload.get("language")),
    )


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
