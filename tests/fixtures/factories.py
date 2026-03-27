"""Deterministic factory functions for test data."""

from datetime import UTC, datetime

from benchmark.types import (
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

_TS = datetime(2026, 3, 25, 12, 0, 0, tzinfo=UTC)

# -- Decision Event Schema properties --------------------------------------------------------

DECISION_EVENT_PROPERTIES = (
    "decision_context",
    "decision_logic",
    "decision_boundary",
    "decision_quality_indicators",
    "human_override_record",
    "temporal_metadata",
)

# -- Architecture metadata ---------------------------------------------------


def make_deterministic_metadata() -> ArchitectureMetadata:
    return ArchitectureMetadata(
        architecture_type=ArchitectureType.DETERMINISTIC_RULES,
        description="Full decision path enumerability via rule engine",
        primary_collapse_modalities=(CollapseModality.COVERAGE_EROSION,),
        structural_breaks=(),
        decision_path_enumerable=True,
        has_cascade_traces=False,
    )


def make_hybrid_metadata() -> ArchitectureMetadata:
    return ArchitectureMetadata(
        architecture_type=ArchitectureType.HYBRID_ML_RULES,
        description="ML scores feed into rule-based decisions",
        primary_collapse_modalities=(
            CollapseModality.METRIC_EROSION,
            CollapseModality.GROUND_TRUTH_DELAY,
        ),
        structural_breaks=(),
        decision_path_enumerable=False,
        has_cascade_traces=True,
    )


def make_streaming_metadata() -> ArchitectureMetadata:
    return ArchitectureMetadata(
        architecture_type=ArchitectureType.STREAMING_FEATURES,
        description="Real-time feature computation with high decision velocity",
        primary_collapse_modalities=(CollapseModality.CONTENT_STALENESS,),
        structural_breaks=(),
        decision_path_enumerable=False,
        has_cascade_traces=False,
    )


def make_agentic_metadata() -> ArchitectureMetadata:
    return ArchitectureMetadata(
        architecture_type=ArchitectureType.AGENTIC_AI,
        description="Multi-step autonomous decision chains with tool use",
        primary_collapse_modalities=(
            CollapseModality.COVERAGE_EROSION,
            CollapseModality.METRIC_EROSION,
            CollapseModality.GROUND_TRUTH_DELAY,
            CollapseModality.CONTENT_STALENESS,
            CollapseModality.SCHEMA_DRIFT,
            CollapseModality.OVERRIDE_ACCUMULATION,
        ),
        structural_breaks=(
            StructuralBreak.DECISION_DIFFUSION,
            StructuralBreak.EVIDENCE_FRAGMENTATION,
            StructuralBreak.RESPONSIBILITY_AMBIGUITY,
        ),
        decision_path_enumerable=False,
        has_cascade_traces=True,
    )


# -- Feasibility entries & matrices ------------------------------------------


def make_feasibility_entries_deterministic() -> tuple[FeasibilityEntry, ...]:
    return tuple(
        FeasibilityEntry(
            property_name=prop,
            level=FeasibilityLevel.FILLABLE,
            recovery_cost=0.0,
        )
        for prop in DECISION_EVENT_PROPERTIES
    )


def make_feasibility_entries_agentic() -> tuple[FeasibilityEntry, ...]:
    levels = [
        FeasibilityLevel.PARTIALLY_FILLABLE,
        FeasibilityLevel.OPAQUE,
        FeasibilityLevel.UNFILLABLE,
        FeasibilityLevel.OPAQUE,
        FeasibilityLevel.UNFILLABLE,
        FeasibilityLevel.PARTIALLY_FILLABLE,
    ]
    return tuple(
        FeasibilityEntry(
            property_name=prop,
            level=level,
            recovery_cost=0.8,
        )
        for prop, level in zip(DECISION_EVENT_PROPERTIES, levels, strict=True)
    )


def make_feasibility_matrix(
    architecture_type: ArchitectureType = ArchitectureType.DETERMINISTIC_RULES,
    *,
    scenario_id: str = "scenario-001",
) -> FeasibilityMatrix:
    if architecture_type == ArchitectureType.DETERMINISTIC_RULES:
        entries = make_feasibility_entries_deterministic()
        fillable = 1.0
        opaque = 0.0
    else:
        entries = make_feasibility_entries_agentic()
        total = len(entries)
        fillable = sum(1 for e in entries if e.level == FeasibilityLevel.FILLABLE) / total
        opaque = sum(1 for e in entries if e.level == FeasibilityLevel.OPAQUE) / total

    return FeasibilityMatrix(
        architecture_type=architecture_type,
        scenario_id=scenario_id,
        entries=entries,
        timestamp=_TS,
        fillable_ratio=fillable,
        opaque_ratio=opaque,
    )


# -- Cascade traces ----------------------------------------------------------


def make_cascade_steps() -> tuple[CascadeStep, ...]:
    return (
        CascadeStep(
            stage=CascadeStage.FEATURE_INCORRECTNESS,
            description="Stale features used due to cache lag",
            severity=0.2,
            evidence_available=True,
            contributing_factors=("cache_latency", "high_throughput"),
        ),
        CascadeStep(
            stage=CascadeStage.FALSE_NEGATIVES,
            description="Stale features cause model to miss fraud",
            severity=0.4,
            evidence_available=True,
            contributing_factors=("feature_staleness",),
        ),
        CascadeStep(
            stage=CascadeStage.UNTRACEABLE_DECISIONS,
            description="Decision trace incomplete due to async pipeline",
            severity=0.6,
            evidence_available=False,
            contributing_factors=("async_pipeline", "missing_trace"),
        ),
        CascadeStep(
            stage=CascadeStage.UNDETECTABLE_DEGRADATION,
            description="No label-free signal detects the decline",
            severity=0.7,
            evidence_available=False,
            contributing_factors=("monitoring_gap",),
        ),
        CascadeStep(
            stage=CascadeStage.CUMULATIVE_LOSSES,
            description="Losses accumulate undetected for 14 days",
            severity=0.9,
            evidence_available=False,
            contributing_factors=("ground_truth_delay", "batch_review_cycle"),
        ),
    )


def make_cascade_trace(
    architecture_type: ArchitectureType = ArchitectureType.HYBRID_ML_RULES,
    *,
    scenario_id: str = "scenario-001",
) -> CascadeTrace:
    return CascadeTrace(
        architecture_type=architecture_type,
        scenario_id=scenario_id,
        steps=make_cascade_steps(),
        total_severity=0.85,
        timestamp=_TS,
    )


# -- Governance gaps ---------------------------------------------------------


def make_governance_gaps() -> tuple[GovernanceGap, ...]:
    return (
        GovernanceGap(
            property_name="decision_context",
            gap_type="delayed",
            severity=0.3,
            description="Context only available 24h after decision",
        ),
        GovernanceGap(
            property_name="decision_logic",
            gap_type="opaque",
            severity=0.8,
            description="ML model internals not inspectable",
        ),
    )


# -- Scenario records --------------------------------------------------------


def make_scenario_record(
    architecture_type: ArchitectureType = ArchitectureType.DETERMINISTIC_RULES,
    *,
    scenario_id: str = "scenario-001",
) -> ScenarioRecord:
    return ScenarioRecord(
        scenario_id=scenario_id,
        architecture_type=architecture_type,
        decision_event={
            "decision_id": f"{scenario_id}-event",
            "timestamp": "2026-03-25T12:00:00Z",
            "decision_type": "automated",
        },
        ground_truth_assessment={"overall_quality": "adequate"},
        feasibility_matrix=make_feasibility_matrix(architecture_type, scenario_id=scenario_id),
        identified_gaps=(
            make_governance_gaps()
            if architecture_type != ArchitectureType.DETERMINISTIC_RULES
            else ()
        ),
        timestamp=_TS,
        metadata={"source": "test_factory"},
    )


# -- Scoring -----------------------------------------------------------------


def make_rubric() -> ScoringRubric:
    return ScoringRubric(
        feasibility_weight=0.5,
        cascade_weight=0.3,
        gap_penalty_weight=0.2,
    )


def make_architecture_score(
    architecture_type: ArchitectureType = ArchitectureType.DETERMINISTIC_RULES,
) -> ArchitectureScore:
    scores_by_type = {
        ArchitectureType.DETERMINISTIC_RULES: (0.95, 1.0, None, 1.0),
        ArchitectureType.HYBRID_ML_RULES: (0.60, 0.65, 0.40, 0.70),
        ArchitectureType.STREAMING_FEATURES: (0.55, 0.60, None, 0.50),
        ArchitectureType.AGENTIC_AI: (0.25, 0.20, 0.15, 0.30),
    }
    overall, feasibility, cascade, gap = scores_by_type[architecture_type]
    # Include per-property breakdown so table generation has data
    breakdown = dict.fromkeys(DECISION_EVENT_PROPERTIES, feasibility)
    return ArchitectureScore(
        architecture_type=architecture_type,
        overall_score=overall,
        feasibility_score=feasibility,
        cascade_score=cascade,
        gap_score=gap,
        breakdown=breakdown,
    )


def make_cross_architecture_comparison() -> CrossArchitectureComparison:
    scores = tuple(make_architecture_score(at) for at in ArchitectureType)
    ranking = tuple(
        s.architecture_type for s in sorted(scores, key=lambda s: s.overall_score, reverse=True)
    )
    return CrossArchitectureComparison(
        scores=scores,
        ranking=ranking,
        timestamp=_TS,
    )
