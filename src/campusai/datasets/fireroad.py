"""MIT FireRoad public dataset adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.client import IncompleteRead
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

COURSE_CATALOG_URL = "https://fireroad-dev.mit.edu/courses/all?full=true"
REQUIREMENTS_LIST_URL = "https://fireroad-dev.mit.edu/requirements/list_reqs"
REQUIREMENT_DETAIL_URL = "https://fireroad-dev.mit.edu/requirements/get_json/{list_id}"


@dataclass(frozen=True)
class FireRoadFetchResult:
    catalog_path: str | None
    requirements_list_path: str | None
    requirement_detail_paths: tuple[str, ...]
    selected_requirement_ids: tuple[str, ...]
    notes: tuple[str, ...]


class FireRoadSourceAdapter:
    """Fetch and normalize public MIT FireRoad data."""

    def __init__(self, raw_root: str | Path = "data/raw/api/mit_fireroad") -> None:
        self.raw_root = Path(raw_root)
        self.raw_root.mkdir(parents=True, exist_ok=True)

    def fetch(self, *, timeout: int = 20, limit_requirement_ids: int = 8, max_courses: int | None = None) -> FireRoadFetchResult:
        notes: list[str] = []
        catalog_path = self.raw_root / "courses_all_full.json"
        requirements_list_path = self.raw_root / "requirements_list_reqs.json"
        requirement_detail_paths: list[str] = []

        print("Fetching MIT FireRoad catalog...", flush=True)
        catalog = self._download_json(COURSE_CATALOG_URL, catalog_path, timeout=timeout, max_items=max_courses)

        print("Fetching MIT FireRoad requirements...", flush=True)
        requirements = self._download_json(REQUIREMENTS_LIST_URL, requirements_list_path, timeout=timeout)

        selected_ids = self._select_requirement_ids(requirements, limit=limit_requirement_ids)
        for list_id in selected_ids:
            detail_url = REQUIREMENT_DETAIL_URL.format(list_id=list_id)
            detail_path = self.raw_root / f"requirement_{list_id}.json"
            print(f"Fetching MIT FireRoad requirement {list_id}...", flush=True)
            detail = self._download_json(detail_url, detail_path, timeout=timeout)
            if detail is not None and detail_path.exists():
                requirement_detail_paths.append(str(detail_path))
            else:
                notes.append(f"Requirement detail fetch failed or timed out for {list_id}.")

        if not selected_ids:
            notes.append("No requirement IDs could be inferred from the public list endpoint.")

        if not catalog:
            notes.append("Course catalog download returned no usable JSON.")
        if not requirements:
            notes.append("Requirements list download returned no usable JSON.")

        return FireRoadFetchResult(
            catalog_path=str(catalog_path) if catalog_path.exists() else None,
            requirements_list_path=str(requirements_list_path) if requirements_list_path.exists() else None,
            requirement_detail_paths=tuple(requirement_detail_paths),
            selected_requirement_ids=tuple(selected_ids),
            notes=tuple(notes),
        )

    def catalog_markdown(self, catalog_data: Any) -> str:
        courses = self._extract_courses(catalog_data)
        lines = ["# MIT FireRoad Course Catalog", ""]
        for course in courses[:200]:
            code = course.get("code") or course.get("course_number") or course.get("subject") or "Unknown course"
            title = course.get("title") or course.get("name") or ""
            description = course.get("description") or course.get("summary") or ""
            lines.append(f"- **{code}** {title}".strip())
            if description:
                lines.append(f"  - {self._compact_text(str(description))}")
        return "\n".join(lines).strip() + "\n"

    def requirement_markdown(self, requirement_data: Any) -> str:
        title = self._extract_requirement_title(requirement_data)
        lines = [f"# {title}", "", "## Raw requirement payload", ""]
        lines.append("```json")
        lines.append(json.dumps(requirement_data, indent=2, ensure_ascii=False))
        lines.append("```")
        return "\n".join(lines) + "\n"

    def _download_json(self, url: str, destination: Path, *, timeout: int, max_items: int | None = None) -> Any:
        try:
            request = Request(url, headers={"User-Agent": "CampusAI/1.0"})
            with urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
        except (IncompleteRead, URLError, TimeoutError, OSError) as exc:
            print(f"Fetch failed for {url}: {exc}", flush=True)
            return None

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            print(f"Fetch returned invalid JSON for {url}: {exc}", flush=True)
            return None

        if max_items is not None and max_items >= 0:
            data = self._limit_items(data, limit=max_items)
            payload = json.dumps(data, indent=2, ensure_ascii=False)

        destination.write_text(payload, encoding="utf-8")
        return data

    def _limit_items(self, data: Any, *, limit: int) -> Any:
        if isinstance(data, list):
            return data[:limit]
        if isinstance(data, dict):
            limited = dict(data)
            for key in ("courses", "data", "items", "results"):
                value = limited.get(key)
                if isinstance(value, list):
                    limited[key] = value[:limit]
                    return limited
        return data

    def _select_requirement_ids(self, requirement_list: Any, *, limit: int) -> list[str]:
        ids: list[str] = []
        for item in requirement_list or []:
            if isinstance(item, dict):
                candidate = item.get("id") or item.get("list_id") or item.get("req_id") or item.get("name")
                if candidate is not None:
                    ids.append(str(candidate))
            elif isinstance(item, (str, int)):
                ids.append(str(item))
        return ids[:limit]

    def _extract_courses(self, catalog_data: Any) -> list[dict[str, Any]]:
        if isinstance(catalog_data, list):
            return [item for item in catalog_data if isinstance(item, dict)]
        if isinstance(catalog_data, dict):
            for key in ("courses", "data", "items", "results"):
                value = catalog_data.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    def _extract_requirement_title(self, requirement_data: Any) -> str:
        if isinstance(requirement_data, dict):
            for key in ("title", "name", "label", "description"):
                value = requirement_data.get(key)
                if value:
                    return str(value)
        return "MIT FireRoad Requirement"

    def _compact_text(self, text: str, max_length: int = 240) -> str:
        compact = " ".join(text.split())
        return compact if len(compact) <= max_length else compact[: max_length - 3] + "..."
