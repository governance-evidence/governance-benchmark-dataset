"""Tests for feasibility matrix computation."""

from benchmark.scoring.feasibility import (
    compute_cross_architecture_feasibility,
    feasibility_summary,
)
from benchmark.types import ArchitectureType, FeasibilityLevel
from tests.fixtures.factories import make_feasibility_matrix


class TestCrossArchitectureFeasibility:
    def test_basic_comparison(self):
        det = make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES)
        agt = make_feasibility_matrix(ArchitectureType.AGENTIC_AI)
        result = compute_cross_architecture_feasibility([det, agt])

        assert "decision_context" in result
        ctx = result["decision_context"]
        assert ctx[ArchitectureType.DETERMINISTIC_RULES] == FeasibilityLevel.FILLABLE
        assert ctx[ArchitectureType.AGENTIC_AI] == FeasibilityLevel.PARTIALLY_FILLABLE

    def test_empty_input(self):
        result = compute_cross_architecture_feasibility([])
        assert result == {}


class TestFeasibilitySummary:
    def test_summary_structure(self):
        det = make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES)
        agt = make_feasibility_matrix(ArchitectureType.AGENTIC_AI)
        result = feasibility_summary([det, agt])

        assert ArchitectureType.DETERMINISTIC_RULES in result
        assert result[ArchitectureType.DETERMINISTIC_RULES]["fillable_ratio"] == 1.0
        assert result[ArchitectureType.AGENTIC_AI]["opaque_ratio"] > 0
