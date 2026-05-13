"""Public dataset adapters for CampusAI Advisor."""

from campusai.datasets.berkeley import BerkeleySourceAdapter
from campusai.datasets.fireroad import FireRoadSourceAdapter
from campusai.datasets.local_rules import LocalRulesAdapter

__all__ = [
    "BerkeleySourceAdapter",
    "FireRoadSourceAdapter",
    "LocalRulesAdapter",
]
