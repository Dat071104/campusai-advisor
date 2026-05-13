from campusai.rag.citations import build_citations, format_citations_for_prompt, infer_authority_level
from campusai.rag.retriever import RetrievedChunk


def test_citation_labels_local_heuristic():
    chunk = RetrievedChunk(
        id="local-1",
        content="Heuristic advice only.",
        source="campusai_local_advisor_rules.md",
        page_number=1,
        chunk_index=0,
    )

    citation = build_citations([chunk], manifest={})[0]

    assert citation.authority_level == "heuristic_local"
    assert "not official policy" in citation.authority_label
    assert citation.chunk_id == "local-1"


def test_citation_infers_public_demo_structured():
    chunk = RetrievedChunk(
        id="mit-1",
        content="MIT FireRoad requirement data.",
        source="mit_fireroad_requirements.json",
    )

    assert infer_authority_level(chunk, {}) == "public_demo_structured"


def test_citation_uses_manifest_authority():
    chunk = RetrievedChunk(id="b-1", content="Guide text", source="berkeley_cs_guide.pdf")
    manifest = {"berkeley_cs_guide.pdf": {"authority_level": "catalog_style"}}

    citation = build_citations([chunk], manifest=manifest)[0]

    assert citation.authority_level == "official"
    assert citation.authority_label == "Official/catalog-style source"


def test_format_citations_for_prompt_empty_is_english():
    assert format_citations_for_prompt([]) == "No citations."
