"""CLI for fetching public CampusAI dataset sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from campusai.datasets import BerkeleySourceAdapter, FireRoadSourceAdapter, LocalRulesAdapter


MANIFEST_PATH = Path("data/processed/source_manifest.json")


def build_manifest(local_rules_path: str, fireroad_result, berkeley_result) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = [
        {
            "source_id": "local_rules",
            "name": "CampusAI local advisor heuristics",
            "type": "markdown",
            "url_or_path": local_rules_path,
            "authority_level": "heuristic",
            "use_for": ["study_path_context", "fallback_advice"],
            "notes": "Heuristic guidance only; not official university policy.",
        },
        {
            "source_id": "berkeley_cs_guide_html",
            "name": "UC Berkeley Computer Science Guide (HTML)",
            "type": "html",
            "url_or_path": "https://guide.berkeley.edu/undergraduate/degree-programs/computer-science/",
            "authority_level": "public_reference",
            "use_for": ["academic_reference", "degree_structure_examples"],
            "notes": "Public guide page; not official TDTU data.",
        },
        {
            "source_id": "berkeley_cs_guide_pdf",
            "name": "UC Berkeley Computer Science Guide (PDF)",
            "type": "pdf",
            "url_or_path": "https://guide.berkeley.edu/undergraduate/degree-programs/computer-science/computer-science.pdf",
            "authority_level": "public_reference",
            "use_for": ["academic_reference", "document_ingestion"],
            "notes": "Public PDF source; download may require manual fallback.",
        },
        {
            "source_id": "mit_fireroad_catalog",
            "name": "MIT FireRoad course catalog",
            "type": "json",
            "url_or_path": "https://fireroad-dev.mit.edu/courses/all?full=true",
            "authority_level": "public_reference",
            "use_for": ["structured_course_demo", "curriculum_examples"],
            "notes": "Structured public dataset for demo and normalization experiments.",
        },
        {
            "source_id": "mit_fireroad_requirements_list",
            "name": "MIT FireRoad requirements list",
            "type": "json",
            "url_or_path": "https://fireroad-dev.mit.edu/requirements/list_reqs",
            "authority_level": "public_reference",
            "use_for": ["structured_course_demo", "requirement_examples"],
            "notes": "Requirement list endpoint used to discover selected requirement IDs.",
        },
    ]

    for index, path in enumerate(getattr(fireroad_result, "requirement_detail_paths", ()), start=1):
        manifest.append(
            {
                "source_id": f"mit_fireroad_requirement_{index}",
                "name": f"MIT FireRoad requirement detail {index}",
                "type": "json",
                "url_or_path": path,
                "authority_level": "public_reference",
                "use_for": ["requirement_examples"],
                "notes": "Selected requirement detail fetched from the public MIT FireRoad API.",
            }
        )

    return manifest


def write_manifest(manifest: list[dict[str, object]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_public_dataset(*, timeout: int = 20, skip_network: bool = False, max_courses: int | None = None) -> dict[str, object]:
    print("Ensuring local advisor rules...", flush=True)
    local_rules = LocalRulesAdapter().ensure_exists()
    fireroad = FireRoadSourceAdapter()
    berkeley = BerkeleySourceAdapter()

    if skip_network:
        print("Skipping public network fetches.", flush=True)
        fireroad_result = type(
            "FireRoadSkippedResult",
            (),
            {
                "catalog_path": None,
                "requirements_list_path": None,
                "requirement_detail_paths": (),
                "selected_requirement_ids": (),
                "notes": ("Network fetches skipped by --skip-network.",),
            },
        )()
        berkeley_result = type(
            "BerkeleySkippedResult",
            (),
            {
                "html_path": None,
                "pdf_path": None,
                "notes": ("Network fetches skipped by --skip-network.",),
            },
        )()
    else:
        fireroad_result = fireroad.fetch(timeout=timeout, max_courses=max_courses)
        berkeley_result = berkeley.fetch(timeout=timeout)

    manifest = build_manifest(local_rules.path, fireroad_result, berkeley_result)
    write_manifest(manifest)

    return {
        "local_rules": local_rules,
        "fireroad": fireroad_result,
        "berkeley": berkeley_result,
        "manifest_path": str(MANIFEST_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public CampusAI dataset sources.")
    parser.add_argument("--dry-run", action="store_true", help="Do not fetch; print planned sources only.")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds for each public fetch.")
    parser.add_argument("--skip-network", action="store_true", help="Generate local files and manifest without public HTTP fetches.")
    parser.add_argument("--max-courses", type=int, default=None, help="Limit saved MIT FireRoad catalog courses after download.")
    args = parser.parse_args()

    if args.dry_run:
        print("Planned sources: MIT FireRoad, Berkeley CS Guide, and local heuristic rules.")
        return

    result = fetch_public_dataset(timeout=args.timeout, skip_network=args.skip_network, max_courses=args.max_courses)
    fireroad = result["fireroad"]
    berkeley = result["berkeley"]
    local_rules = result["local_rules"]

    print(f"Local rules: {local_rules.path} (created={local_rules.created})")
    print(f"MIT FireRoad catalog: {fireroad.catalog_path}")
    print(f"MIT FireRoad requirements list: {fireroad.requirements_list_path}")
    print(f"MIT FireRoad requirements selected: {len(fireroad.selected_requirement_ids)}")
    print(f"Berkeley HTML: {berkeley.html_path}")
    print(f"Berkeley PDF: {berkeley.pdf_path}")
    print(f"Manifest: {result['manifest_path']}")

    for note in tuple(getattr(fireroad, "notes", ())) + tuple(getattr(berkeley, "notes", ())):
        print(f"Note: {note}")


if __name__ == "__main__":
    main()
