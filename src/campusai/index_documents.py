"""Command-line entrypoint for indexing local PDFs."""

from __future__ import annotations

from campusai.ingestion.indexer import index_local_documents


def main() -> None:
    result = index_local_documents()
    print(result.message)
    if result.skipped_files:
        print("Skipped files:")
        for path in result.skipped_files:
            print(f"- {path}")


if __name__ == "__main__":
    main()
