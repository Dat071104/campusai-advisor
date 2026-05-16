"""FastAPI backend for CampusAI Advisor local Docker/runtime mode."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from campusai.config import get_settings
from campusai.ingestion.indexer import index_local_documents
from campusai.rag.answer_chain import RAGAnswerChain
from campusai.rag.retriever import Retriever, index_exists

app = FastAPI(
    title="CampusAI Advisor API",
    version="0.1.0",
    description="Local FastAPI backend for CampusAI retrieval, indexing, and question answering.",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    student_profile: dict[str, str] = Field(default_factory=dict)


class DebugRetrievalRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/status")
def status() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "has_index": index_exists(settings),
        "has_groq_key": settings.has_groq_key,
        "raw_data_path": settings.raw_data_path,
        "vector_store_path": settings.vector_store_path,
        "chroma_collection": settings.chroma_collection,
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "groq_model": settings.groq_model,
        "rag_top_k": settings.rag_top_k,
    }


@app.post("/status/build-index")
def build_index(reset: bool = True) -> dict[str, Any]:
    settings = get_settings()
    result = index_local_documents(settings=settings, reset=reset)
    return {
        "message": result.message,
        "chunks_indexed": result.chunks_indexed,
        "pages_loaded": result.pages_loaded,
        "pdf_files_found": result.pdf_files_found,
        "text_files_found": result.text_files_found,
    }


@app.post("/debug/retrieval")
def debug_retrieval(payload: DebugRetrievalRequest) -> dict[str, Any]:
    settings = get_settings()
    chunks = Retriever(settings).retrieve(payload.question, top_k=payload.top_k)
    return {
        "question": payload.question,
        "chunks": [
            {
                "id": chunk.id,
                "content": chunk.content,
                "source": chunk.source,
                "source_path": chunk.source_path,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "distance": chunk.distance,
                "authority_level": chunk.authority_level,
                "source_type": chunk.source_type,
                "university": chunk.university,
                "country": chunk.country,
                "language": chunk.language,
            }
            for chunk in chunks
        ],
    }


@app.post("/ask")
def ask(payload: AskRequest) -> dict[str, Any]:
    result = RAGAnswerChain().answer_question(payload.question, payload.student_profile)
    return {
        "answer": result.answer,
        "citations": [
            {
                "source": citation.source,
                "chunk_id": citation.chunk_id,
                "page_number": citation.page_number,
                "chunk_index": citation.chunk_index,
                "authority_level": citation.authority_level,
                "authority_label": citation.authority_label,
                "source_path": citation.source_path,
                "distance": citation.distance,
                "excerpt": citation.excerpt,
            }
            for citation in result.citations
        ],
        "retrieved_chunks": [
            {
                "id": chunk.id,
                "content": chunk.content,
                "source": chunk.source,
                "source_path": chunk.source_path,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "distance": chunk.distance,
                "authority_level": chunk.authority_level,
                "source_type": chunk.source_type,
                "university": chunk.university,
                "country": chunk.country,
                "language": chunk.language,
            }
            for chunk in result.retrieved_chunks
        ],
        "used_live_api": result.used_live_api,
        "missing_api_key": result.missing_api_key,
        "no_context": result.no_context,
        "error": result.error,
    }
