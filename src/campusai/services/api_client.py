"""Thin HTTP client for the optional CampusAI FastAPI backend."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

import requests

from campusai.rag.answer_chain import AnswerResult
from campusai.rag.citations import Citation
from campusai.rag.retriever import RetrievedChunk


class APIClientError(RuntimeError):
    """Safe error raised when the API backend is unavailable."""


class CampusAIAPIClient:
    def __init__(self, base_url: str, *, timeout_seconds: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds

    def health(self) -> dict[str, object]:
        return self._get_json("health")

    def status(self) -> dict[str, object]:
        return self._get_json("status")

    def debug_retrieval(self, query: str) -> dict[str, object]:
        return self._get_json("debug/retrieval", params={"q": query})

    def ask(self, question: str, language: str = "English") -> AnswerResult:
        payload = {"question": question, "language": language}
        data = self._post_json("ask", json=payload)
        citations = [Citation(**item) for item in data.get("citations", []) if isinstance(item, dict)]
        sources = [self._source_to_chunk(item) for item in data.get("sources", []) if isinstance(item, dict)]
        return AnswerResult(
            answer=str(data.get("answer", "")),
            citations=citations,
            retrieved_chunks=sources,
            prompt=None,
            used_live_api=False,
            missing_api_key=data.get("error") == "missing_api_key",
            no_context=not bool(sources),
            error=data.get("error"),
        )

    def _get_json(self, path: str, *, params: dict[str, object] | None = None) -> dict[str, object]:
        try:
            response = requests.get(urljoin(self.base_url, path), params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {"data": data}
        except Exception as exc:
            raise APIClientError(self._error_message(exc)) from exc

    def _post_json(self, path: str, *, json: dict[str, object]) -> dict[str, object]:
        try:
            response = requests.post(urljoin(self.base_url, path), json=json, timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {"data": data}
        except Exception as exc:
            raise APIClientError(self._error_message(exc)) from exc

    def _source_to_chunk(self, item: dict[str, object]) -> RetrievedChunk:
        return RetrievedChunk(
            id=str(item.get("chunk_id") or item.get("id") or "unknown"),
            content=str(item.get("content_preview") or item.get("excerpt") or ""),
            source=str(item.get("source") or "unknown"),
            source_path=str(item.get("source_path")) if item.get("source_path") else None,
            page_number=_optional_int(item.get("page_number")),
            chunk_index=_optional_int(item.get("chunk_index")),
            distance=_optional_float(item.get("distance")),
            authority_level=str(item.get("authority") or item.get("authority_level")) if item.get("authority") or item.get("authority_level") else None,
            source_type=None,
        )

    def _error_message(self, exc: Exception) -> str:
        return f"CampusAI backend unavailable: {exc.__class__.__name__}"


def _optional_int(value: object) -> int | None:
    try:
        return int(value) if value is not None and value != "" else None
    except (TypeError, ValueError):
        return None


def _optional_float(value: object) -> float | None:
    try:
        return float(value) if value is not None and value != "" else None
    except (TypeError, ValueError):
        return None
