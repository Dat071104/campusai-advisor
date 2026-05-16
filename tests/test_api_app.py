from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

api_app = importlib.import_module("campusai.api.app")
app = api_app.app


class DummySettings:
    chroma_collection = "campusai_documents"
    vector_store_path = "data/vector_db"


class DummyRetriever:
    def retrieve(self, question: str, top_k: int | None = None):
        from campusai.rag.retriever import RetrievedChunk

        return [
            RetrievedChunk(
                id="chunk-1",
                content="TDTU Software Engineering prepares students with software development fundamentals.",
                source="tdtu_catalog.pdf",
                source_path="data/raw/tdtu_catalog.pdf",
                page_number=7,
                chunk_index=1,
                distance=0.12,
                authority_level="official",
                source_type="pdf",
            )
        ]


class DummyAnswerChain:
    def answer_question(self, question: str, student_profile: dict[str, str] | None = None):
        from campusai.rag.answer_chain import AnswerResult
        from campusai.rag.citations import Citation
        from campusai.rag.retriever import RetrievedChunk

        chunk = RetrievedChunk(
            id="chunk-1",
            content="TDTU Software Engineering prepares students with software development fundamentals.",
            source="tdtu_catalog.pdf",
            source_path="data/raw/tdtu_catalog.pdf",
            page_number=7,
            chunk_index=1,
            distance=0.12,
            authority_level="official",
            source_type="pdf",
        )
        citation = Citation(
            source="tdtu_catalog.pdf",
            chunk_id="chunk-1",
            page_number=7,
            chunk_index=1,
            authority_level="official",
            authority_label="Official/catalog-style source",
            source_path="data/raw/tdtu_catalog.pdf",
            distance=0.12,
            excerpt="TDTU Software Engineering prepares students with software development fundamentals.",
        )
        return AnswerResult(
            answer="Software Engineering at TDTU covers software development fundamentals.",
            citations=[citation],
            retrieved_chunks=[chunk],
            prompt=None,
            used_live_api=False,
            missing_api_key=False,
            no_context=False,
            error=None,
        )


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "campusai-api"}


def test_status_endpoint(monkeypatch):
    monkeypatch.setattr(api_app, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(api_app, "index_exists", lambda settings=None: True)
    response = client.get("/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "campusai-api"
    assert payload["has_index"] is True
    assert "groq" not in str(payload).lower()


def test_debug_retrieval_endpoint(monkeypatch):
    monkeypatch.setattr(api_app, "get_retriever", lambda: DummyRetriever())
    response = client.get("/debug/retrieval?q=What+is+TDTU+Software+Engineering%3F")
    assert response.status_code == 200
    payload = response.json()
    assert payload["q"] == "What is TDTU Software Engineering?"
    assert payload["results"][0]["rank"] == 1
    assert "content_preview" in payload["results"][0]


def test_ask_endpoint_without_groq(monkeypatch):
    monkeypatch.setattr(api_app, "get_answer_chain", lambda: DummyAnswerChain())
    response = client.post("/ask", json={"question": "What is TDTU Software Engineering?", "language": "English"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]
    assert payload["citations"]
    assert payload["sources"]
