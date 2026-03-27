"""Tests for cross-architecture comparison."""

from datetime import UTC, datetime

from benchmark.comparison.cross_architecture import (
    compare_architectures,
    compute_feasibility_gap,
    rank_by_feasibility,
)
from benchmark.types import ArchitectureType
from tests.fixtures.factories import make_architecture_score

_TS = datetime(2026, 3, 25, 12, 0, 0, tzinfo=UTC)


class TestCompareArchitectures:
    def test_deterministic_ranks_first(self):
        scores = [make_architecture_score(at) for at in ArchitectureType]
        comparison = compare_architectures(scores, timestamp=_TS)
        assert comparison.ranking[0] == ArchitectureType.DETERMINISTIC_RULES
        assert comparison.ranking[-1] == ArchitectureType.AGENTIC_AI

    def test_all_architectures_present(self):
        scores = [make_architecture_score(at) for at in ArchitectureType]
        comparison = compare_architectures(scores, timestamp=_TS)
        assert len(comparison.scores) == 4


class TestRankByFeasibility:
    def test_ranking_order(self):
        scores = [make_architecture_score(at) for at in ArchitectureType]
        ranking = rank_by_feasibility(scores)
        assert ranking[0] == ArchitectureType.DETERMINISTIC_RULES
        assert ranking[-1] == ArchitectureType.AGENTIC_AI


class TestComputeFeasibilityGap:
    def test_gap_is_positive(self):
        det = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        agt = make_architecture_score(ArchitectureType.AGENTIC_AI)
        gap = compute_feasibility_gap(det, agt)
        assert gap > 0.0

    def test_same_architecture_zero_gap(self):
        det = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        gap = compute_feasibility_gap(det, det)
        assert gap == 0.0
