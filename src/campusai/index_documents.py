"""Command-line entrypoint for indexing local PDFs, Markdown, and text files."""

from __future__ import annotations

import argparse

from campusai.ingestion.indexer import index_local_documents


def main() -> int:
    parser = argparse.ArgumentParser(description="Index PDF, Markdown, and .txt files under RAW_DATA_DIR.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the Chroma collection before upserting (use after PDF-only indexes).",
    )
    args = parser.parse_args()

    try:
        result = index_local_documents(reset=args.reset)
    except RuntimeError as exc:
        print(f"Indexing failed: {exc}")
        return 1

    print(result.message)
    if result.skipped_files:
        print("Skipped files:")
        for path in result.skipped_files:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
