"""RAG answer orchestration for CampusAI."""

from __future__ import annotations

from dataclasses import dataclass

from campusai.config import Settings, get_settings
from campusai.rag.citations import Citation, build_citations
from campusai.rag.prompts import SYSTEM_PROMPT, build_rag_prompt
from campusai.rag.retriever import RetrievedChunk, Retriever
from campusai.services.groq_client import ChatClient, GroqChatClient

NO_CONTEXT_MESSAGE = (
    "Tài liệu đã lập chỉ mục hiện chưa có đủ thông tin liên quan để trả lời chắc chắn. "
    "Mình không nên tự bịa prerequisite, requirement, hoặc chính sách chính thức. "
    "Bạn có thể thử hỏi cụ thể hơn hoặc lập chỉ mục thêm catalog/syllabus phù hợp."
)


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
                answer="Hãy nhập một câu hỏi về course, prerequisite, policy, hoặc định hướng học tập.",
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
