from pathlib import Path

from campusai.ingestion.text_loader import (
    LOCAL_ADVISOR_RULES_FILENAME,
    find_markdown_and_text_files,
    load_text_document_pages,
)


def test_find_markdown_and_text_files_discovers_local_advisor(tmp_path):
    local_dir = tmp_path / "documents" / "local"
    local_dir.mkdir(parents=True)
    target = local_dir / LOCAL_ADVISOR_RULES_FILENAME
    target.write_text("# rules\n", encoding="utf-8")
    (tmp_path / "readme.txt").write_text("hello", encoding="utf-8")

    found = find_markdown_and_text_files(tmp_path)

    assert local_dir / LOCAL_ADVISOR_RULES_FILENAME in found
    assert tmp_path / "readme.txt" in found


def test_load_local_advisor_rules_metadata():
    page = load_text_document_pages(
        Path("data/raw/documents/local") / LOCAL_ADVISOR_RULES_FILENAME
    )[0]

    assert page.source == LOCAL_ADVISOR_RULES_FILENAME
    assert page.page_number == 1
    assert page.document_type == "markdown"
    assert page.authority == "heuristic"
    assert page.source_type == "local_advisor_rules"
    assert page.is_official_policy is False


def test_load_plain_txt_has_document_type_text(tmp_path):
    p = tmp_path / "note.txt"
    p.write_text("Some note body.", encoding="utf-8")
    page = load_text_document_pages(p)[0]

    assert page.document_type == "text"
    assert page.authority is None
    assert page.source_type is None
    assert page.is_official_policy is None
