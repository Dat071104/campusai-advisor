"""Prompt templates for CampusAI RAG answering."""

from __future__ import annotations

from campusai.rag.citations import Citation, format_citations_for_prompt
from campusai.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = """Bạn là CampusAI Advisor, trợ lý học thuật cho sinh viên Computer Science.
Mặc định trả lời bằng tiếng Việt, trừ khi người dùng yêu cầu ngôn ngữ khác.

Quy tắc bắt buộc:
- Chỉ dùng ngữ cảnh truy xuất được để khẳng định các quy định học thuật, prerequisite, graduation requirement, hoặc chính sách chính thức.
- Nếu tài liệu không đủ bằng chứng, nói rõ: tài liệu hiện có chưa đủ thông tin để kết luận.
- Không bao giờ biến local advisor heuristic thành chính sách chính thức của trường.
- Nếu nguồn official/catalog-style mâu thuẫn với heuristic local advisor, ưu tiên nguồn official/catalog-style.
- Tách bạch lời khuyên học tập/nghề nghiệp tổng quát với kết luận dựa trên tài liệu.
- Câu trả lời nên ngắn gọn, hữu ích cho sinh viên CS hỏi về study path, prerequisites, và career direction.
- Luôn đưa mục "Nguồn" với citation id khi có ngữ cảnh.
"""


def build_rag_prompt(
    *,
    question: str,
    chunks: list[RetrievedChunk],
    citations: list[Citation],
    student_profile: dict[str, str],
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

    context_text = "\n\n".join(context_blocks) if context_blocks else "Không có ngữ cảnh truy xuất được."
    profile_text = _format_profile(student_profile)
    citation_text = format_citations_for_prompt(citations)

    return f"""{SYSTEM_PROMPT}

Hồ sơ sinh viên:
{profile_text}

Câu hỏi của sinh viên:
{question.strip()}

Ngữ cảnh truy xuất:
{context_text}

Danh sách citation hợp lệ:
{citation_text}

Hãy trả lời theo cấu trúc:
1. Trả lời ngắn gọn
2. Vì sao áp dụng cho sinh viên này
3. Nguồn
4. Lưu ý / phần chưa đủ bằng chứng
""".strip()


def _format_profile(student_profile: dict[str, str]) -> str:
    if not student_profile:
        return "- Chưa cung cấp hồ sơ."
    lines = []
    for key, value in student_profile.items():
        cleaned = str(value).strip()
        if cleaned:
            lines.append(f"- {key}: {cleaned}")
    return "\n".join(lines) if lines else "- Chưa cung cấp hồ sơ."
