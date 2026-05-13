"""Local heuristic academic advising rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_LOCAL_RULES = """# CampusAI Local Advisor Heuristics

Status: heuristic context only. This is not an official university policy document.

## Suggested prerequisite heuristics

- Data Structures and Algorithms before Machine Learning when possible.
- Probability / Statistics and Linear Algebra before Machine Learning.
- Operating Systems, Networking, and Databases are useful before backend-heavy work.
- Python, data handling, and scripting are useful for AI engineering workflows.

## Scope note

These heuristics are meant to help with study-path suggestions when the official documents do not provide enough detail.
They do not replace curriculum rules, departmental policies, or official degree audit systems.
"""


@dataclass(frozen=True)
class LocalRulesResult:
    path: str
    created: bool


class LocalRulesAdapter:
    def __init__(self, rules_path: str | Path = "data/raw/documents/local/campusai_local_advisor_rules.md") -> None:
        self.rules_path = Path(rules_path)

    def ensure_exists(self) -> LocalRulesResult:
        self.rules_path.parent.mkdir(parents=True, exist_ok=True)
        created = False
        if not self.rules_path.exists():
            self.rules_path.write_text(DEFAULT_LOCAL_RULES, encoding="utf-8")
            created = True
        return LocalRulesResult(path=str(self.rules_path), created=created)
