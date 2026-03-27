"""Hypothesis property-based tests for scoring invariants."""

from datetime import UTC, datetime

from hypothesis import given, settings
from hypothesis import strategies as st

from benchmark.types import (
    ArchitectureType,
    CascadeStage,
    CascadeStep,
    CascadeTrace,
    FeasibilityEntry,
    FeasibilityLevel,
    FeasibilityMatrix,
    GovernanceGap,
    ScoringRubric,
)

_TS = datetime(2026, 3, 25, 12, 0, 0, tzinfo=UTC)

# -- Strategies ---------------------------------------------------------------

unit_float = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

feasibility_levels = st.sampled_from(list(FeasibilityLevel))

decision_event_properties = st.sampled_from(
    [
        "decision_context",
        "decision_logic",
        "decision_boundary",
        "decision_quality_indicators",
        "human_override_record",
        "temporal_metadata",
    ]
)

gap_types = st.sampled_from(["missing", "delayed", "unreliable", "opaque"])


@st.composite
def feasibility_entries(draw, n=6):
    props = [
        "decision_context",
        "decision_logic",
        "decision_boundary",
        "decision_quality_indicators",
        "human_override_record",
        "temporal_metadata",
    ]
    return tuple(
        FeasibilityEntry(
            property_name=props[i],
            level=draw(feasibility_levels),
            recovery_cost=draw(unit_float),
        )
        for i in range(n)
    )


@st.composite
def feasibility_matrices(draw):
    arch = draw(st.sampled_from(list(ArchitectureType)))
    entries = draw(feasibility_entries())
    total = len(entries)
    fillable = sum(1 for e in entries if e.level == FeasibilityLevel.FILLABLE) / total
    opaque = sum(1 for e in entries if e.level == FeasibilityLevel.OPAQUE) / total
    return FeasibilityMatrix(
        architecture_type=arch,
        scenario_id="prop-test",
        entries=entries,
        timestamp=_TS,
        fillable_ratio=fillable,
        opaque_ratio=opaque,
    )


@st.composite
def governance_gaps(draw, min_size=0, max_size=6):
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    return tuple(
        GovernanceGap(
            property_name=draw(decision_event_properties),
            gap_type=draw(gap_types),
            severity=draw(unit_float),
            description="property-based test gap",
        )
        for _ in range(n)
    )


@st.composite
def scoring_rubrics(draw):
    w1 = draw(st.floats(min_value=0.1, max_value=0.8, allow_nan=False, allow_infinity=False))
    max_w2 = min(0.8, 1.0 - w1 - 0.05)
    w2 = draw(
        st.floats(
            min_value=0.1,
            max_value=max_w2,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    w3 = 1.0 - w1 - w2
    if w3 < 0.0 or w3 > 1.0:
        w1, w2, w3 = 0.5, 0.3, 0.2
    return ScoringRubric(
        feasibility_weight=round(w1, 6),
        cascade_weight=round(w2, 6),
        gap_penalty_weight=round(w3, 6),
    )


# -- Property tests -----------------------------------------------------------


class TestFeasibilityScoreProperties:
    @given(matrix=feasibility_matrices())
    @settings(max_examples=50)
    def test_score_always_in_unit_range(self, matrix):
        from benchmark.scoring.rubric import score_feasibility

        score = score_feasibility(matrix)
        assert 0.0 <= score <= 1.0

    @given(matrix=feasibility_matrices())
    @settings(max_examples=50)
    def test_fillable_ratio_plus_opaque_ratio_bounded(self, matrix):
        assert matrix.fillable_ratio + matrix.opaque_ratio <= 1.0 + 1e-9


class TestGapScoreProperties:
    @given(gaps=governance_gaps())
    @settings(max_examples=50)
    def test_gap_score_in_unit_range(self, gaps):
        from benchmark.scoring.rubric import score_gaps

        score = score_gaps(gaps)
        assert 0.0 <= score <= 1.0

    @given(gaps=governance_gaps(min_size=0, max_size=0))
    def test_no_gaps_means_perfect_score(self, gaps):
        from benchmark.scoring.rubric import score_gaps

        assert score_gaps(gaps) == 1.0


class TestOverallScoreProperties:
    @given(matrix=feasibility_matrices(), gaps=governance_gaps())
    @settings(max_examples=50)
    def test_overall_score_in_unit_range(self, matrix, gaps):
        from benchmark.scoring.rubric import default_rubric, score_scenario

        score = score_scenario(matrix, gaps, default_rubric())
        assert 0.0 <= score.overall_score <= 1.0
        assert 0.0 <= score.feasibility_score <= 1.0
        assert 0.0 <= score.gap_score <= 1.0


class TestCascadeSeverityProperties:
    @given(severity=st.lists(unit_float, min_size=1, max_size=5))
    @settings(max_examples=50)
    def test_compounded_severity_in_unit_range(self, severity):
        from benchmark.scoring.cascade import compute_cascade_severity

        steps = tuple(
            CascadeStep(
                stage=list(CascadeStage)[i % 5],
                description="prop test step",
                severity=s,
                evidence_available=True,
            )
            for i, s in enumerate(severity)
        )
        trace = CascadeTrace(
            architecture_type=ArchitectureType.HYBRID_ML_RULES,
            scenario_id="prop-test",
            steps=steps,
            total_severity=max(severity),
            timestamp=_TS,
        )
        result = compute_cascade_severity(trace)
        assert 0.0 <= result <= 1.0
