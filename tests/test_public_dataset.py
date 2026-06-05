import json
from http.client import IncompleteRead
from pathlib import Path

from campusai.datasets.fireroad import FireRoadSourceAdapter
from campusai.datasets.local_rules import LocalRulesAdapter
from campusai.fetch_public_dataset import build_manifest


def test_manifest_structure_uses_expected_fields(tmp_path):
    local_rules = tmp_path / "campusai_local_advisor_rules.md"
    local_rules.write_text("rules", encoding="utf-8")

    manifest = build_manifest(
        str(local_rules),
        fireroad_result=type("Result", (), {"requirement_detail_paths": ("one.json", "two.json")})(),
        berkeley_result=type("Result", (), {})(),
    )

    assert manifest[0]["source_id"] == "local_rules"
    assert manifest[0]["authority_level"] == "heuristic"
    assert manifest[1]["source_id"] == "berkeley_cs_guide_html"
    assert manifest[3]["source_id"] == "mit_fireroad_catalog"
    assert manifest[-1]["source_id"] == "mit_fireroad_requirement_2"


def test_fireroad_requirement_markdown_wraps_json():
    adapter = FireRoadSourceAdapter(raw_root=Path("data/raw/api/mit_fireroad"))
    markdown = adapter.requirement_markdown({"title": "Course 6 requirements", "units": 12})

    assert markdown.startswith("# Course 6 requirements")
    assert "```json" in markdown
    assert json.dumps({"title": "Course 6 requirements", "units": 12}, indent=2) in markdown


def test_fireroad_download_handles_incomplete_read(monkeypatch, tmp_path):
    class PartialResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            raise IncompleteRead(b"{", 100)

    def fake_urlopen(request, *, timeout):
        return PartialResponse()

    monkeypatch.setattr("campusai.datasets.fireroad.urlopen", fake_urlopen)

    adapter = FireRoadSourceAdapter(raw_root=tmp_path)
    destination = tmp_path / "catalog.json"

    result = adapter._download_json("https://example.test/catalog", destination, timeout=1)

    assert result is None
    assert not destination.exists()


def test_local_rules_file_exists():
    result = LocalRulesAdapter().ensure_exists()
    assert Path(result.path).exists()
