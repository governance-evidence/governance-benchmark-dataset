"""Tests for scoring rubric."""

import pytest

from benchmark.scoring.cascade import compute_cascade_severity
from benchmark.scoring.rubric import (
    default_rubric,
    score_cascade,
    score_feasibility,
    score_gaps,
    score_scenario,
)
from benchmark.types import (
    ArchitectureType,
)
from tests.fixtures.factories import (
    make_cascade_trace,
    make_feasibility_matrix,
    make_governance_gaps,
)


class TestDefaultRubric:
    def test_weights_sum_to_one(self):
        rubric = default_rubric()
        total = rubric.feasibility_weight + rubric.cascade_weight + rubric.gap_penalty_weight
        assert abs(total - 1.0) < 1e-6


class TestScoreFeasibility:
    def test_all_fillable_is_one(self, deterministic_matrix):
        assert score_feasibility(deterministic_matrix) == 1.0

    def test_mixed_levels(self, agentic_matrix):
        score = score_feasibility(agentic_matrix)
        assert 0.0 < score < 1.0


class TestScoreGaps:
    def test_no_gaps_is_one(self):
        assert score_gaps(()) == 1.0

    def test_gaps_reduce_score(self):
        gaps = make_governance_gaps()
        score = score_gaps(gaps)
        assert 0.0 < score < 1.0


class TestScoreCascade:
    def test_none_returns_none(self):
        assert score_cascade(None) is None

    def test_high_severity_low_score(self):
        trace = make_cascade_trace()
        score = score_cascade(trace)
        assert score is not None
        assert 0.0 < score < 0.5  # total_severity is 0.85

    def test_uses_compounded_severity(self):
        trace = make_cascade_trace()
        score = score_cascade(trace)
        expected = 1.0 - compute_cascade_severity(trace)
        assert score == pytest.approx(expected)


class TestScoreScenario:
    def test_deterministic_high_score(self, deterministic_matrix, rubric):
        score = score_scenario(deterministic_matrix, (), rubric)
        assert score.overall_score > 0.9
        assert score.cascade_score is None
        assert score.gap_score == 1.0

    def test_with_cascade(self, rubric):
        matrix = make_feasibility_matrix(ArchitectureType.HYBRID_ML_RULES)
        trace = make_cascade_trace(ArchitectureType.HYBRID_ML_RULES)
        gaps = make_governance_gaps()
        score = score_scenario(matrix, gaps, rubric, cascade_trace=trace)
        assert score.cascade_score is not None
        assert 0.0 < score.overall_score < 1.0

    def test_breakdown_has_properties(self, deterministic_matrix, rubric):
        score = score_scenario(deterministic_matrix, (), rubric)
        assert "decision_context" in score.breakdown
        assert score.breakdown["decision_context"] == 1.0
