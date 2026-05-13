"""RAG answer orchestration for CampusAI."""

from __future__ import annotations

from dataclasses import dataclass

from campusai.config import Settings, get_settings
from campusai.rag.citations import Citation, build_citations
from campusai.rag.prompts import SYSTEM_PROMPT, build_rag_prompt
from campusai.rag.retriever import (
    RetrievedChunk,
    Retriever,
    chunk_matches_local_advisor_source,
    is_study_path_prerequisite_query,
)
from campusai.services.groq_client import ChatClient, GroqChatClient

NO_CONTEXT_MESSAGE = (
    "The indexed documents do not contain enough relevant context to answer this question with confidence. "
    "I should not invent prerequisites, graduation requirements, or official policy. "
    "Try a more specific question, or index additional catalog or syllabus sources that match your topic."
)

_STUDY_PATH_MISSING_LOCAL_NOTE = (
    "Study-path / prerequisites style question: none of the retrieved chunks above appear to come from the "
    "packaged heuristic local advisor rules file. Do not treat unrelated scheduling or policy snippets as "
    "evidence for study ordering or ML prerequisites. If the snippets do not support the question, say indexed "
    "context is insufficient instead of forcing a confident answer."
)


def _study_path_retrieval_note(question: str, chunks: list[RetrievedChunk]) -> str | None:
    if not is_study_path_prerequisite_query(question):
        return None
    if any(chunk_matches_local_advisor_source(c) for c in chunks):
        return None
    return _STUDY_PATH_MISSING_LOCAL_NOTE


@dataclass(frozen=True)
class AnswerResult:
    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    prompt: str | None
    used_live_api: bool
    missing_api_key: bool
    no_context: bool
    error: str | None = None


class RAGAnswerChain:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        retriever: Retriever | None = None,
        chat_client: ChatClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.retriever = retriever or Retriever(self.settings)
        self.chat_client = chat_client or GroqChatClient(self.settings)

    def answer_question(self, question: str, student_profile: dict[str, str] | None = None) -> AnswerResult:
        cleaned_question = question.strip()
        if not cleaned_question:
            return AnswerResult(
                answer="Enter a question about courses, prerequisites, policy, or study planning.",
                citations=[],
                retrieved_chunks=[],
                prompt=None,
                used_live_api=False,
                missing_api_key=False,
                no_context=True,
            )

        chunks = self.retriever.retrieve(cleaned_question, top_k=self.settings.rag_top_k)
        citations = build_citations(chunks)
        if not chunks:
            return AnswerResult(
                answer=NO_CONTEXT_MESSAGE,
                citations=[],
                retrieved_chunks=[],
                prompt=None,
                used_live_api=False,
                missing_api_key=False,
                no_context=True,
            )

        prompt = build_rag_prompt(
            question=cleaned_question,
            chunks=chunks,
            citations=citations,
            student_profile=student_profile or {},
            retrieval_quality_note=_study_path_retrieval_note(cleaned_question, chunks),
        )
        response = self.chat_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        return AnswerResult(
            answer=response.content,
            citations=citations,
            retrieved_chunks=chunks,
            prompt=prompt,
            used_live_api=response.used_live_api,
            missing_api_key=response.error == "missing_api_key",
            no_context=False,
            error=response.error,
        )
