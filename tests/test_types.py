"""Tests for benchmark.types -- enum values, dataclass validation, immutability."""

from datetime import UTC, datetime

import pytest

from benchmark.types import (
    CASCADE_ARCHITECTURES,
    ArchitectureMetadata,
    ArchitectureScore,
    ArchitectureType,
    CascadeStage,
    CascadeStep,
    CascadeTrace,
    CollapseModality,
    CrossArchitectureComparison,
    FeasibilityEntry,
    FeasibilityLevel,
    FeasibilityMatrix,
    GovernanceGap,
    ScenarioRecord,
    ScoringRubric,
    StructuralBreak,
)
from tests.fixtures.factories import (
    make_architecture_score,
    make_cascade_steps,
    make_cascade_trace,
    make_feasibility_entries_deterministic,
    make_rubric,
)

_TS = datetime(2026, 3, 25, 12, 0, 0, tzinfo=UTC)


# --------------------------------------------------------------------------- #
#  Enum completeness
# --------------------------------------------------------------------------- #


class TestEnums:
    def test_architecture_type_has_four_members(self):
        assert len(ArchitectureType) == 4

    def test_feasibility_level_has_four_members(self):
        assert len(FeasibilityLevel) == 4

    def test_collapse_modality_has_six_members(self):
        assert len(CollapseModality) == 6

    def test_cascade_stage_has_five_members(self):
        assert len(CascadeStage) == 5

    def test_structural_break_has_three_members(self):
        assert len(StructuralBreak) == 3

    def test_cascade_architectures_constant(self):
        assert isinstance(CASCADE_ARCHITECTURES, frozenset)
        assert {
            ArchitectureType.HYBRID_ML_RULES,
            ArchitectureType.AGENTIC_AI,
        } == CASCADE_ARCHITECTURES
        assert len(CASCADE_ARCHITECTURES) == 2


# --------------------------------------------------------------------------- #
#  ArchitectureMetadata
# --------------------------------------------------------------------------- #


class TestArchitectureMetadata:
    def test_valid_creation(self, deterministic_meta):
        assert deterministic_meta.architecture_type == ArchitectureType.DETERMINISTIC_RULES
        assert deterministic_meta.decision_path_enumerable is True

    def test_empty_description_rejected(self):
        with pytest.raises(ValueError, match="description must be non-empty"):
            ArchitectureMetadata(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                description="",
                primary_collapse_modalities=(CollapseModality.COVERAGE_EROSION,),
            )

    def test_empty_collapse_modalities_rejected(self):
        with pytest.raises(ValueError, match="primary_collapse_modalities must be non-empty"):
            ArchitectureMetadata(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                description="test",
                primary_collapse_modalities=(),
            )

    def test_cascade_traces_invalid_for_deterministic(self):
        with pytest.raises(ValueError, match="has_cascade_traces=True only valid"):
            ArchitectureMetadata(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                description="test",
                primary_collapse_modalities=(CollapseModality.COVERAGE_EROSION,),
                has_cascade_traces=True,
            )

    def test_cascade_traces_valid_for_hybrid(self, hybrid_meta):
        assert hybrid_meta.has_cascade_traces is True

    def test_cascade_traces_invalid_for_streaming(self):
        with pytest.raises(ValueError, match="has_cascade_traces=True only valid"):
            ArchitectureMetadata(
                architecture_type=ArchitectureType.STREAMING_FEATURES,
                description="test",
                primary_collapse_modalities=(CollapseModality.CONTENT_STALENESS,),
                has_cascade_traces=True,
            )

    def test_agentic_has_structural_breaks(self, agentic_meta):
        assert len(agentic_meta.structural_breaks) == 3

    def test_structural_breaks_invalid_for_hybrid(self):
        with pytest.raises(ValueError, match="structural_breaks are only valid"):
            ArchitectureMetadata(
                architecture_type=ArchitectureType.HYBRID_ML_RULES,
                description="test",
                primary_collapse_modalities=(CollapseModality.METRIC_EROSION,),
                structural_breaks=(StructuralBreak.DECISION_DIFFUSION,),
                has_cascade_traces=True,
            )

    def test_frozen(self, deterministic_meta):
        with pytest.raises(AttributeError):
            deterministic_meta.description = "modified"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
#  FeasibilityEntry
# --------------------------------------------------------------------------- #


class TestFeasibilityEntry:
    def test_valid_creation(self):
        entry = FeasibilityEntry(
            property_name="decision_context",
            level=FeasibilityLevel.FILLABLE,
        )
        assert entry.recovery_cost == 0.0

    def test_empty_property_name_rejected(self):
        with pytest.raises(ValueError, match="property_name must be non-empty"):
            FeasibilityEntry(property_name="", level=FeasibilityLevel.FILLABLE)

    def test_recovery_cost_out_of_range(self):
        with pytest.raises(ValueError, match="recovery_cost must be in"):
            FeasibilityEntry(
                property_name="test", level=FeasibilityLevel.FILLABLE, recovery_cost=1.5
            )

    def test_nan_recovery_cost_rejected(self):
        with pytest.raises(ValueError, match="recovery_cost must be in"):
            FeasibilityEntry(
                property_name="test", level=FeasibilityLevel.FILLABLE, recovery_cost=float("nan")
            )


# --------------------------------------------------------------------------- #
#  FeasibilityMatrix
# --------------------------------------------------------------------------- #


class TestFeasibilityMatrix:
    def test_valid_creation(self, deterministic_matrix):
        assert deterministic_matrix.fillable_ratio == 1.0
        assert deterministic_matrix.opaque_ratio == 0.0

    def test_empty_scenario_id_rejected(self):
        with pytest.raises(ValueError, match="scenario_id must be non-empty"):
            FeasibilityMatrix(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="",
                entries=make_feasibility_entries_deterministic(),
                timestamp=_TS,
                fillable_ratio=1.0,
                opaque_ratio=0.0,
            )

    def test_empty_entries_rejected(self):
        with pytest.raises(ValueError, match="entries must be non-empty"):
            FeasibilityMatrix(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="test",
                entries=(),
                timestamp=_TS,
                fillable_ratio=1.0,
                opaque_ratio=0.0,
            )

    def test_ratios_exceeding_one_rejected(self):
        with pytest.raises(ValueError, match="fillable_ratio \\+ opaque_ratio must be <= 1.0"):
            FeasibilityMatrix(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="test",
                entries=make_feasibility_entries_deterministic(),
                timestamp=_TS,
                fillable_ratio=0.7,
                opaque_ratio=0.5,
            )

    def test_fillable_ratio_must_match_entries(self):
        with pytest.raises(ValueError, match="fillable_ratio must match entries"):
            FeasibilityMatrix(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="test",
                entries=make_feasibility_entries_deterministic(),
                timestamp=_TS,
                fillable_ratio=0.5,
                opaque_ratio=0.0,
            )

    def test_opaque_ratio_must_match_entries(self):
        entries = (
            FeasibilityEntry(
                property_name="decision_context",
                level=FeasibilityLevel.FILLABLE,
            ),
            FeasibilityEntry(
                property_name="decision_logic",
                level=FeasibilityLevel.UNFILLABLE,
            ),
        )
        with pytest.raises(ValueError, match="opaque_ratio must match entries"):
            FeasibilityMatrix(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="test",
                entries=entries,
                timestamp=_TS,
                fillable_ratio=0.5,
                opaque_ratio=0.5,
            )


# --------------------------------------------------------------------------- #
#  CascadeStep / CascadeTrace
# --------------------------------------------------------------------------- #


class TestCascadeStep:
    def test_valid_creation(self):
        step = CascadeStep(
            stage=CascadeStage.FEATURE_INCORRECTNESS,
            description="test step",
            severity=0.5,
            evidence_available=True,
        )
        assert step.contributing_factors == ()

    def test_empty_description_rejected(self):
        with pytest.raises(ValueError, match="description must be non-empty"):
            CascadeStep(
                stage=CascadeStage.FEATURE_INCORRECTNESS,
                description="",
                severity=0.5,
                evidence_available=True,
            )

    def test_severity_out_of_range(self):
        with pytest.raises(ValueError, match="severity must be in"):
            CascadeStep(
                stage=CascadeStage.FEATURE_INCORRECTNESS,
                description="test",
                severity=-0.1,
                evidence_available=True,
            )


class TestCascadeTrace:
    def test_valid_hybrid(self, hybrid_cascade):
        assert hybrid_cascade.architecture_type == ArchitectureType.HYBRID_ML_RULES
        assert len(hybrid_cascade.steps) == 5

    def test_valid_agentic(self):
        trace = make_cascade_trace(ArchitectureType.AGENTIC_AI)
        assert trace.architecture_type == ArchitectureType.AGENTIC_AI

    def test_deterministic_rejected(self):
        with pytest.raises(ValueError, match="CascadeTrace only valid for"):
            CascadeTrace(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                scenario_id="test",
                steps=make_cascade_steps(),
                total_severity=0.5,
                timestamp=_TS,
            )

    def test_streaming_rejected(self):
        with pytest.raises(ValueError, match="CascadeTrace only valid for"):
            CascadeTrace(
                architecture_type=ArchitectureType.STREAMING_FEATURES,
                scenario_id="test",
                steps=make_cascade_steps(),
                total_severity=0.5,
                timestamp=_TS,
            )

    def test_empty_scenario_id_rejected(self):
        with pytest.raises(ValueError, match="scenario_id must be non-empty"):
            CascadeTrace(
                architecture_type=ArchitectureType.HYBRID_ML_RULES,
                scenario_id="",
                steps=make_cascade_steps(),
                total_severity=0.5,
                timestamp=_TS,
            )

    def test_empty_steps_rejected(self):
        with pytest.raises(ValueError, match="steps must be non-empty"):
            CascadeTrace(
                architecture_type=ArchitectureType.HYBRID_ML_RULES,
                scenario_id="test",
                steps=(),
                total_severity=0.5,
                timestamp=_TS,
            )


# --------------------------------------------------------------------------- #
#  GovernanceGap
# --------------------------------------------------------------------------- #


class TestGovernanceGap:
    def test_valid_creation(self):
        gap = GovernanceGap(
            property_name="decision_context",
            gap_type="missing",
            severity=0.5,
            description="Context unavailable",
        )
        assert gap.gap_type == "missing"

    def test_empty_property_name_rejected(self):
        with pytest.raises(ValueError, match="property_name must be non-empty"):
            GovernanceGap(
                property_name="",
                gap_type="missing",
                severity=0.5,
                description="test",
            )

    def test_invalid_gap_type(self):
        with pytest.raises(ValueError, match="gap_type must be one of"):
            GovernanceGap(
                property_name="test",
                gap_type="invalid",
                severity=0.5,
                description="test",
            )

    def test_all_valid_gap_types(self):
        for gap_type in ("missing", "delayed", "unreliable", "opaque"):
            gap = GovernanceGap(
                property_name="test",
                gap_type=gap_type,
                severity=0.5,
                description="test",
            )
            assert gap.gap_type == gap_type

    def test_empty_description_rejected(self):
        with pytest.raises(ValueError, match="description must be non-empty"):
            GovernanceGap(
                property_name="test",
                gap_type="missing",
                severity=0.5,
                description="",
            )


# --------------------------------------------------------------------------- #
#  ScenarioRecord
# --------------------------------------------------------------------------- #


class TestScenarioRecord:
    def test_valid_creation(self, deterministic_scenario):
        assert deterministic_scenario.scenario_id == "scenario-001"

    def test_empty_scenario_id_rejected(self):
        with pytest.raises(ValueError, match="scenario_id must be non-empty"):
            ScenarioRecord(
                scenario_id="",
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
            )

    def test_mappings_frozen(self, deterministic_scenario):
        with pytest.raises(TypeError):
            deterministic_scenario.decision_event["new_key"] = "value"  # type: ignore[index]

    def test_metadata_frozen(self, deterministic_scenario):
        with pytest.raises(TypeError):
            deterministic_scenario.metadata["new_key"] = "value"  # type: ignore[index]

    def test_feasibility_matrix_scenario_id_must_match(self):
        matrix = FeasibilityMatrix(
            architecture_type=ArchitectureType.DETERMINISTIC_RULES,
            scenario_id="other-scenario",
            entries=make_feasibility_entries_deterministic(),
            timestamp=_TS,
            fillable_ratio=1.0,
            opaque_ratio=0.0,
        )
        with pytest.raises(ValueError, match="feasibility_matrix.scenario_id must match"):
            ScenarioRecord(
                scenario_id="scenario-001",
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                feasibility_matrix=matrix,
            )

    def test_feasibility_matrix_architecture_type_must_match(self):
        matrix = FeasibilityMatrix(
            architecture_type=ArchitectureType.AGENTIC_AI,
            scenario_id="scenario-001",
            entries=make_feasibility_entries_deterministic(),
            timestamp=_TS,
            fillable_ratio=1.0,
            opaque_ratio=0.0,
        )
        with pytest.raises(
            ValueError,
            match="feasibility_matrix.architecture_type must match",
        ):
            ScenarioRecord(
                scenario_id="scenario-001",
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                feasibility_matrix=matrix,
            )


# --------------------------------------------------------------------------- #
#  ScoringRubric
# --------------------------------------------------------------------------- #


class TestScoringRubric:
    def test_default_weights_sum_to_one(self):
        rubric = make_rubric()
        total = rubric.feasibility_weight + rubric.cascade_weight + rubric.gap_penalty_weight
        assert abs(total - 1.0) < 1e-6

    def test_weights_not_summing_to_one(self):
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            ScoringRubric(feasibility_weight=0.5, cascade_weight=0.5, gap_penalty_weight=0.5)

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError, match="must be in"):
            ScoringRubric(feasibility_weight=-0.1, cascade_weight=0.6, gap_penalty_weight=0.5)

    def test_nan_weight_rejected(self):
        with pytest.raises(ValueError, match="must be in"):
            ScoringRubric(
                feasibility_weight=float("nan"),
                cascade_weight=0.5,
                gap_penalty_weight=0.5,
            )

    def test_inf_weight_rejected(self):
        with pytest.raises(ValueError, match="must be in"):
            ScoringRubric(
                feasibility_weight=float("inf"),
                cascade_weight=0.5,
                gap_penalty_weight=0.5,
            )


# --------------------------------------------------------------------------- #
#  ArchitectureScore
# --------------------------------------------------------------------------- #


class TestArchitectureScore:
    def test_valid_creation(self, deterministic_score):
        assert deterministic_score.cascade_score is None

    def test_breakdown_frozen(self):
        score = ArchitectureScore(
            architecture_type=ArchitectureType.DETERMINISTIC_RULES,
            overall_score=0.9,
            feasibility_score=1.0,
            cascade_score=None,
            gap_score=1.0,
            breakdown={"test": 0.5},
        )
        with pytest.raises(TypeError):
            score.breakdown["new_key"] = 0.1  # type: ignore[index]

    def test_out_of_range_score(self):
        with pytest.raises(ValueError, match="overall_score must be in"):
            ArchitectureScore(
                architecture_type=ArchitectureType.DETERMINISTIC_RULES,
                overall_score=1.5,
                feasibility_score=1.0,
                cascade_score=None,
                gap_score=1.0,
            )


# --------------------------------------------------------------------------- #
#  CrossArchitectureComparison
# --------------------------------------------------------------------------- #


class TestCrossArchitectureComparison:
    def test_valid_creation(self, comparison):
        assert len(comparison.scores) == 4
        assert comparison.ranking[0] == ArchitectureType.DETERMINISTIC_RULES

    def test_empty_scores_rejected(self):
        with pytest.raises(ValueError, match="scores must be non-empty"):
            CrossArchitectureComparison(scores=(), ranking=(), timestamp=_TS)

    def test_mismatched_lengths_rejected(self):
        score = make_architecture_score()
        with pytest.raises(ValueError, match="ranking length"):
            CrossArchitectureComparison(
                scores=(score,),
                ranking=(
                    ArchitectureType.DETERMINISTIC_RULES,
                    ArchitectureType.HYBRID_ML_RULES,
                ),
                timestamp=_TS,
            )

    def test_mismatched_types_rejected(self):
        score = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        with pytest.raises(ValueError, match="ranking types must match"):
            CrossArchitectureComparison(
                scores=(score,),
                ranking=(ArchitectureType.HYBRID_ML_RULES,),
                timestamp=_TS,
            )

    def test_duplicate_score_architectures_rejected(self):
        score_a = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        score_b = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        with pytest.raises(ValueError, match="scores must contain unique architecture types"):
            CrossArchitectureComparison(
                scores=(score_a, score_b),
                ranking=(
                    ArchitectureType.DETERMINISTIC_RULES,
                    ArchitectureType.HYBRID_ML_RULES,
                ),
                timestamp=_TS,
            )

    def test_duplicate_ranking_architectures_rejected(self):
        score_a = make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)
        score_b = make_architecture_score(ArchitectureType.HYBRID_ML_RULES)
        with pytest.raises(ValueError, match="ranking must contain unique architecture types"):
            CrossArchitectureComparison(
                scores=(score_a, score_b),
                ranking=(
                    ArchitectureType.DETERMINISTIC_RULES,
                    ArchitectureType.DETERMINISTIC_RULES,
                ),
                timestamp=_TS,
            )
