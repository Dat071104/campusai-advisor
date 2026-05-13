"""Prompt templates for CampusAI RAG answering."""

from __future__ import annotations

from campusai.rag.citations import Citation, format_citations_for_prompt
from campusai.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = """You are CampusAI Advisor, an academic assistant for Computer Science students.

Language:
- Answer in English by default.
- If the user explicitly asks for another language (for example Vietnamese), you may answer in that language for that turn only.

Evidence and tone:
- Use retrieved context to support claims about academic rules, prerequisites, graduation requirements, or official policy only when that context actually applies.
- If retrieved snippets are weak, off-topic, or do not support a confident answer, say clearly that indexed context is insufficient and avoid inventing requirements or policy.
- Never present heuristic local advisor text as official university policy.
- When official/catalog-style sources conflict with heuristic local advisor content, prefer the official/catalog-style source for policy-like conclusions.
- Separate general study/career guidance from document-backed conclusions.
- Keep answers concise and useful for CS students asking about study paths, prerequisites, and career direction.
- When you use retrieved context, include a "Sources" section with citation ids.
"""


def build_rag_prompt(
    *,
    question: str,
    chunks: list[RetrievedChunk],
    citations: list[Citation],
    student_profile: dict[str, str],
    retrieval_quality_note: str | None = None,
) -> str:
    context_blocks = []
    for idx, chunk in enumerate(chunks, start=1):
        citation = citations[idx - 1] if idx - 1 < len(citations) else None
        authority = citation.authority_label if citation else chunk.authority_level or "Unknown source authority"
        page = f"page {chunk.page_number}" if chunk.page_number is not None else "page unknown"
        context_blocks.append(
            f"[Context {idx}]\n"
            f"Source: {chunk.source}\n"
            f"Location: {page}, chunk {chunk.id}\n"
            f"Authority: {authority}\n"
            f"Content: {chunk.content}"
        )

    context_text = "\n\n".join(context_blocks) if context_blocks else "No retrieved context."
    profile_text = _format_profile(student_profile)
    citation_text = format_citations_for_prompt(citations)
    note_block = ""
    if retrieval_quality_note:
        note_block = f"\nRetrieval note:\n{retrieval_quality_note.strip()}\n"

    return f"""{SYSTEM_PROMPT}
{note_block}
Student profile:
{profile_text}

Student question:
{question.strip()}

Retrieved context:
{context_text}

Valid citations:
{citation_text}

Answer using this structure:
1. Short answer
2. Why it applies to this student (when evidence supports it)
3. Sources (citation ids)
4. Caveats / where evidence is insufficient
""".strip()


def _format_profile(student_profile: dict[str, str]) -> str:
    if not student_profile:
        return "- No profile fields provided."
    lines = []
    for key, value in student_profile.items():
        cleaned = str(value).strip()
        if cleaned:
            lines.append(f"- {key}: {cleaned}")
    return "\n".join(lines) if lines else "- No profile fields provided."
