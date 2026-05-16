"""Pydantic models for the CampusAI API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question for the RAG assistant")
    language: str = Field(default="English", description="Preferred response language")


class CitationModel(BaseModel):
    source: str
    chunk_id: str
    page_number: int | None = None
    chunk_index: int | None = None
    authority_level: str
    authority_label: str
    source_path: str | None = None
    distance: float | None = None
    excerpt: str | None = None


class SourceModel(BaseModel):
    rank: int
    source: str
    source_path: str | None = None
    authority: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None
    distance: float | None = None
    content_preview: str


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationModel] = Field(default_factory=list)
    sources: list[SourceModel] = Field(default_factory=list)
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str


class StatusResponse(BaseModel):
    service: str
    has_index: bool
    collection: str
    vector_store_path: str


class RetrievalResponse(BaseModel):
    q: str
    results: list[SourceModel]
