"""Tests for cascade analysis."""

import pytest

from benchmark.scoring.cascade import (
    cascade_summary,
    compute_cascade_severity,
    detect_cascade_acceleration,
    validate_cascade_architecture,
)
from benchmark.types import ArchitectureType, CascadeStage
from tests.fixtures.factories import make_cascade_trace


class TestValidateCascadeArchitecture:
    def test_hybrid_valid(self):
        validate_cascade_architecture(ArchitectureType.HYBRID_ML_RULES)

    def test_agentic_valid(self):
        validate_cascade_architecture(ArchitectureType.AGENTIC_AI)

    def test_deterministic_invalid(self):
        with pytest.raises(ValueError, match="Cascade analysis only valid"):
            validate_cascade_architecture(ArchitectureType.DETERMINISTIC_RULES)

    def test_streaming_invalid(self):
        with pytest.raises(ValueError, match="Cascade analysis only valid"):
            validate_cascade_architecture(ArchitectureType.STREAMING_FEATURES)


class TestComputeCascadeSeverity:
    def test_returns_unit_range(self):
        trace = make_cascade_trace()
        severity = compute_cascade_severity(trace)
        assert 0.0 <= severity <= 1.0

    def test_higher_step_severity_means_higher_total(self):
        trace1 = make_cascade_trace(ArchitectureType.HYBRID_ML_RULES)
        trace2 = make_cascade_trace(ArchitectureType.AGENTIC_AI)
        # Both use same factory steps, should give same severity
        assert compute_cascade_severity(trace1) == compute_cascade_severity(trace2)


class TestDetectCascadeAcceleration:
    def test_single_trace(self):
        trace = make_cascade_trace()
        result = detect_cascade_acceleration([trace])
        assert CascadeStage.FEATURE_INCORRECTNESS in result
        assert CascadeStage.CUMULATIVE_LOSSES in result

    def test_empty_traces(self):
        result = detect_cascade_acceleration([])
        assert result == {}


class TestCascadeSummary:
    def test_single_trace(self):
        trace = make_cascade_trace()
        summary = cascade_summary([trace])
        assert summary["trace_count"] == 1
        assert 0.0 < summary["avg_severity"] <= 1.0  # type: ignore[operator]

    def test_empty_traces(self):
        summary = cascade_summary([])
        assert summary["trace_count"] == 0
        assert summary["avg_severity"] == 0.0
