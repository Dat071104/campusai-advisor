"""FastAPI application for the CampusAI backend service."""

from __future__ import annotations

import inspect

from fastapi import Depends, FastAPI, Query

from campusai.config import Settings, get_settings
from campusai.rag.answer_chain import RAGAnswerChain
from campusai.rag.citations import Citation
from campusai.rag.retriever import RetrievedChunk, Retriever, index_exists

from .models import AskRequest, AskResponse, CitationModel, HealthResponse, RetrievalResponse, SourceModel, StatusResponse

app = FastAPI(title="CampusAI API", version="2.1.0")


def get_retriever(settings: Settings = Depends(get_settings)) -> Retriever:
    return Retriever(settings)


def get_answer_chain(settings: Settings = Depends(get_settings)) -> RAGAnswerChain:
    return RAGAnswerChain(settings)


def _resolve_settings() -> Settings:
    return get_settings()


def _call_factory(factory: object, settings: Settings) -> object:
    if not callable(factory):
        raise TypeError("factory must be callable")
    try:
        params = inspect.signature(factory).parameters
    except (TypeError, ValueError):
        return factory(settings)
    if len(params) == 0:
        return factory()
    return factory(settings)


def _resolve_retriever(settings: Settings = Depends(_resolve_settings)) -> Retriever:
    return _call_factory(get_retriever, settings)


def _resolve_answer_chain(settings: Settings = Depends(_resolve_settings)) -> RAGAnswerChain:
    return _call_factory(get_answer_chain, settings)


def _citation_to_model(citation: Citation) -> CitationModel:
    return CitationModel.model_validate(citation.__dict__)


def _chunk_to_source_model(chunk: RetrievedChunk, rank: int) -> SourceModel:
    preview = (chunk.content or "").replace("\n", " ").strip()
    if len(preview) > 300:
        preview = preview[:300] + "…"
    return SourceModel(
        rank=rank,
        source=chunk.source,
        source_path=chunk.source_path,
        authority=chunk.authority_level,
        page_number=chunk.page_number,
        chunk_index=chunk.chunk_index,
        distance=chunk.distance,
        content_preview=preview,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="campusai-api")


@app.get("/status", response_model=StatusResponse)
def status(settings: Settings = Depends(_resolve_settings)) -> StatusResponse:
    return StatusResponse(
        service="campusai-api",
        has_index=index_exists(settings),
        collection=settings.chroma_collection,
        vector_store_path=settings.vector_store_path,
    )


@app.get("/debug/retrieval", response_model=RetrievalResponse)
def debug_retrieval(
    q: str = Query(..., min_length=1),
    top_k: int | None = Query(default=None, ge=1),
    retriever: Retriever = Depends(_resolve_retriever),
) -> RetrievalResponse:
    chunks = retriever.retrieve(q, top_k=top_k)
    results = [_chunk_to_source_model(chunk, rank=idx) for idx, chunk in enumerate(chunks, start=1)]
    return RetrievalResponse(q=q, results=results)


@app.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    chain: RAGAnswerChain = Depends(_resolve_answer_chain),
) -> AskResponse:
    try:
        result = chain.answer_question(payload.question, {"language": payload.language})
    except Exception:
        return AskResponse(answer="CampusAI is temporarily unavailable. Please try again later.", citations=[], sources=[], error="internal_error")

    citations = [_citation_to_model(citation) for citation in result.citations]
    sources = [_chunk_to_source_model(chunk, rank=idx) for idx, chunk in enumerate(result.retrieved_chunks, start=1)]

    if result.missing_api_key:
        return AskResponse(answer=result.answer, citations=citations, sources=sources, error="missing_api_key")
    if result.error and result.error not in {"missing_api_key"}:
        return AskResponse(answer=result.answer, citations=citations, sources=sources, error=result.error)
    return AskResponse(answer=result.answer, citations=citations, sources=sources)
