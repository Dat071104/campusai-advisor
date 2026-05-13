"""Print top-k retrieval results for a query (embeddings + Chroma only; no Groq)."""

from __future__ import annotations

import argparse
import sys

from campusai.rag.retriever import Retriever


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Dry-run semantic retrieval: embed query, query Chroma, print ranked chunks.",
    )
    parser.add_argument(
        "question",
        nargs="?",
        default="",
        help="Question text (pass as one quoted argument).",
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=None,
        help="Override RAG_TOP_K (default: from settings).",
    )
    args = parser.parse_args(argv)

    question = (args.question or "").strip()
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()
    if not question:
        parser.error("question is required (positional argument or stdin)")

    retriever = Retriever()
    if not retriever.has_index():
        print("No vector index found (Chroma collection empty or missing). Run index_documents first.")
        return 1

    k = args.top_k
    chunks = retriever.retrieve(question, top_k=k)

    if not chunks:
        print("Retriever returned no chunks.")
        return 0

    for rank, chunk in enumerate(chunks, start=1):
        preview = (chunk.content or "").replace("\n", " ").strip()
        if len(preview) > 300:
            preview = preview[:300] + "…"
        auth = chunk.authority_level or ""
        print(f"--- rank {rank} ---")
        print(f"source: {chunk.source}")
        print(f"source_path: {chunk.source_path or ''}")
        print(f"authority: {auth}")
        print(f"page_number: {chunk.page_number}")
        print(f"chunk_index: {chunk.chunk_index}")
        print(f"distance: {chunk.distance}")
        print(f"content_preview: {preview}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
