"""Core data types for governance benchmark evaluation.

All types are frozen dataclasses -- immutable value objects.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime


# --------------------------------------------------------------------------- #
#  Enums
# --------------------------------------------------------------------------- #


class ArchitectureType(Enum):
    """Four decision system architecture types covered by the benchmark."""

    DETERMINISTIC_RULES = "deterministic_rules"
    HYBRID_ML_RULES = "hybrid_ml_rules"
    STREAMING_FEATURES = "streaming_features"
    AGENTIC_AI = "agentic_ai"


class FeasibilityLevel(Enum):
    """Governance evidence feasibility level for a Decision Event Schema property."""

    FILLABLE = "fillable"
    PARTIALLY_FILLABLE = "partially_fillable"
    UNFILLABLE = "unfillable"
    OPAQUE = "opaque"


class CollapseModality(Enum):
    """SAC governance artifact degradation types.

    Each modality describes a distinct way governance evidence quality degrades.
    """

    COVERAGE_EROSION = "coverage_erosion"
    METRIC_EROSION = "metric_erosion"
    GROUND_TRUTH_DELAY = "ground_truth_delay"
    CONTENT_STALENESS = "content_staleness"
    SCHEMA_DRIFT = "schema_drift"
    OVERRIDE_ACCUMULATION = "override_accumulation"


class CascadeStage(Enum):
    """Five stages of the cascade of uncertainty model.

    Governance failures propagate serially through these stages:
    feature incorrectness -> false negatives -> untraceable decisions
    -> undetectable degradation -> cumulative losses.
    """

    FEATURE_INCORRECTNESS = "feature_incorrectness"
    FALSE_NEGATIVES = "false_negatives"
    UNTRACEABLE_DECISIONS = "untraceable_decisions"
    UNDETECTABLE_DEGRADATION = "undetectable_degradation"
    CUMULATIVE_LOSSES = "cumulative_losses"


class StructuralBreak(Enum):
    """Three structural breaks that agentic AI systems introduce.

    These breaks are qualitative governance failures that cannot be resolved
    by tuning existing framework parameters.
    """

    DECISION_DIFFUSION = "decision_diffusion"
    EVIDENCE_FRAGMENTATION = "evidence_fragmentation"
    RESPONSIBILITY_AMBIGUITY = "responsibility_ambiguity"


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

CASCADE_ARCHITECTURES: frozenset[ArchitectureType] = frozenset(
    {
        ArchitectureType.HYBRID_ML_RULES,
        ArchitectureType.AGENTIC_AI,
    }
)

_RATIO_TOLERANCE = 1e-3


def _validate_unit_float(name: str, value: float) -> None:
    """Validate that *value* is a finite float in [0, 1]."""
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        msg = f"{name} must be in [0, 1], got {value}"
        raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Architecture metadata
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ArchitectureMetadata:
    """Metadata describing a decision system architecture type.

    Attributes
    ----------
    architecture_type : ArchitectureType
        Which architecture this metadata describes.
    description : str
        Human-readable description of the architecture.
    primary_collapse_modalities : tuple[CollapseModality, ...]
        Dominant governance degradation types for this architecture.
    structural_breaks : tuple[StructuralBreak, ...]
        Structural breaks (non-empty only for agentic AI).
    decision_path_enumerable : bool
        Whether all decision paths can be enumerated exhaustively.
    has_cascade_traces : bool
        Whether cascade of uncertainty traces apply.
    """

    architecture_type: ArchitectureType
    description: str
    primary_collapse_modalities: tuple[CollapseModality, ...]
    structural_breaks: tuple[StructuralBreak, ...] = ()
    decision_path_enumerable: bool = False
    has_cascade_traces: bool = False

    def __post_init__(self) -> None:
        if not self.description:
            msg = "description must be non-empty"
            raise ValueError(msg)
        if not self.primary_collapse_modalities:
            msg = "primary_collapse_modalities must be non-empty"
            raise ValueError(msg)
        if self.has_cascade_traces and self.architecture_type not in CASCADE_ARCHITECTURES:
            msg = (
                f"has_cascade_traces=True only valid for "
                f"{[a.value for a in CASCADE_ARCHITECTURES]}, "
                f"got {self.architecture_type.value}"
            )
            raise ValueError(msg)
        if self.structural_breaks and self.architecture_type is not ArchitectureType.AGENTIC_AI:
            msg = "structural_breaks are only valid for agentic_ai"
            raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Feasibility
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FeasibilityEntry:
    """Feasibility assessment for a single Decision Event Schema property.

    Attributes
    ----------
    property_name : str
        Decision Event Schema property path (e.g. ``decision_context``).
    level : FeasibilityLevel
        Assessed feasibility level.
    recovery_cost : float
        Estimated cost of recovering this property post-hoc, in [0, 1].
    notes : str
        Optional notes on the assessment.
    """

    property_name: str
    level: FeasibilityLevel
    recovery_cost: float = 0.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.property_name:
            msg = "property_name must be non-empty"
            raise ValueError(msg)
        _validate_unit_float("recovery_cost", self.recovery_cost)


@dataclass(frozen=True)
class FeasibilityMatrix:
    """Feasibility matrix for a scenario within an architecture.

    Attributes
    ----------
    architecture_type : ArchitectureType
        Architecture this matrix belongs to.
    scenario_id : str
        Identifier of the assessed scenario.
    entries : tuple[FeasibilityEntry, ...]
        Per-property feasibility assessments.
    timestamp : datetime
        When the assessment was performed.
    fillable_ratio : float
        Fraction of entries at FILLABLE level, in [0, 1].
    opaque_ratio : float
        Fraction of entries at OPAQUE level, in [0, 1].
    """

    architecture_type: ArchitectureType
    scenario_id: str
    entries: tuple[FeasibilityEntry, ...]
    timestamp: datetime
    fillable_ratio: float
    opaque_ratio: float

    def __post_init__(self) -> None:
        if not self.scenario_id:
            msg = "scenario_id must be non-empty"
            raise ValueError(msg)
        if not self.entries:
            msg = "entries must be non-empty"
            raise ValueError(msg)
        _validate_unit_float("fillable_ratio", self.fillable_ratio)
        _validate_unit_float("opaque_ratio", self.opaque_ratio)
        if self.fillable_ratio + self.opaque_ratio > 1.0 + 1e-9:
            msg = (
                f"fillable_ratio + opaque_ratio must be <= 1.0, "
                f"got {self.fillable_ratio} + {self.opaque_ratio}"
            )
            raise ValueError(msg)
        entry_count = len(self.entries)
        actual_fillable_ratio = (
            sum(1 for entry in self.entries if entry.level is FeasibilityLevel.FILLABLE)
            / entry_count
        )
        actual_opaque_ratio = (
            sum(1 for entry in self.entries if entry.level is FeasibilityLevel.OPAQUE) / entry_count
        )
        if abs(self.fillable_ratio - actual_fillable_ratio) > _RATIO_TOLERANCE:
            msg = (
                "fillable_ratio must match entries, "
                f"got {self.fillable_ratio}, expected {actual_fillable_ratio}"
            )
            raise ValueError(msg)
        if abs(self.opaque_ratio - actual_opaque_ratio) > _RATIO_TOLERANCE:
            msg = (
                "opaque_ratio must match entries, "
                f"got {self.opaque_ratio}, expected {actual_opaque_ratio}"
            )
            raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Cascade of uncertainty
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CascadeStep:
    """A single stage in a cascade of uncertainty trace.

    Attributes
    ----------
    stage : CascadeStage
        Which cascade stage this step represents.
    description : str
        What happened at this stage.
    severity : float
        Severity of failure at this stage, in [0, 1].
    evidence_available : bool
        Whether governance evidence was available at this stage.
    contributing_factors : tuple[str, ...]
        Factors that contributed to the failure.
    """

    stage: CascadeStage
    description: str
    severity: float
    evidence_available: bool
    contributing_factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.description:
            msg = "description must be non-empty"
            raise ValueError(msg)
        _validate_unit_float("severity", self.severity)


@dataclass(frozen=True)
class CascadeTrace:
    """A cascade of uncertainty trace for a scenario.

    Only valid for hybrid ML + rules and agentic AI architectures.

    Attributes
    ----------
    architecture_type : ArchitectureType
        Must be HYBRID_ML_RULES or AGENTIC_AI.
    scenario_id : str
        Identifier of the traced scenario.
    steps : tuple[CascadeStep, ...]
        Ordered cascade steps from feature incorrectness to cumulative losses.
    total_severity : float
        Aggregate cascade severity, in [0, 1].
    timestamp : datetime
        When the trace was recorded.
    """

    architecture_type: ArchitectureType
    scenario_id: str
    steps: tuple[CascadeStep, ...]
    total_severity: float
    timestamp: datetime

    def __post_init__(self) -> None:
        if self.architecture_type not in CASCADE_ARCHITECTURES:
            msg = (
                f"CascadeTrace only valid for "
                f"{[a.value for a in CASCADE_ARCHITECTURES]}, "
                f"got {self.architecture_type.value}"
            )
            raise ValueError(msg)
        if not self.scenario_id:
            msg = "scenario_id must be non-empty"
            raise ValueError(msg)
        if not self.steps:
            msg = "steps must be non-empty"
            raise ValueError(msg)
        _validate_unit_float("total_severity", self.total_severity)


# --------------------------------------------------------------------------- #
#  Governance gaps
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class GovernanceGap:
    """An identified governance evidence gap in a scenario.

    Attributes
    ----------
    property_name : str
        Decision Event Schema property where the gap exists.
    gap_type : str
        Category: ``missing``, ``delayed``, ``unreliable``, or ``opaque``.
    severity : float
        Gap severity, in [0, 1].
    description : str
        What the gap means for governance.
    """

    property_name: str
    gap_type: str
    severity: float
    description: str

    _VALID_GAP_TYPES = frozenset({"missing", "delayed", "unreliable", "opaque"})

    def __post_init__(self) -> None:
        if not self.property_name:
            msg = "property_name must be non-empty"
            raise ValueError(msg)
        if self.gap_type not in self._VALID_GAP_TYPES:
            msg = f"gap_type must be one of {sorted(self._VALID_GAP_TYPES)}, got {self.gap_type!r}"
            raise ValueError(msg)
        _validate_unit_float("severity", self.severity)
        if not self.description:
            msg = "description must be non-empty"
            raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Scenario records
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ScenarioRecord:
    """A documented decision event with governance assessment.

    Attributes
    ----------
    scenario_id : str
        Unique scenario identifier.
    architecture_type : ArchitectureType
        Which architecture this scenario belongs to.
    decision_event : Mapping[str, object]
        Raw Decision Event Schema-conformant decision event dict.
    ground_truth_assessment : Mapping[str, object]
        Expert governance assessment.
    feasibility_matrix : FeasibilityMatrix
        Feasibility assessment for this scenario.
    identified_gaps : tuple[GovernanceGap, ...]
        Governance gaps found.
    timestamp : datetime
        When the scenario was recorded.
    metadata : Mapping[str, object]
        Additional metadata.
    """

    scenario_id: str
    architecture_type: ArchitectureType
    decision_event: Mapping[str, object] = field(default_factory=dict)
    ground_truth_assessment: Mapping[str, object] = field(default_factory=dict)
    feasibility_matrix: FeasibilityMatrix | None = None
    identified_gaps: tuple[GovernanceGap, ...] = ()
    timestamp: datetime | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scenario_id:
            msg = "scenario_id must be non-empty"
            raise ValueError(msg)
        # Freeze mutable mappings
        object.__setattr__(self, "decision_event", MappingProxyType(dict(self.decision_event)))
        object.__setattr__(
            self, "ground_truth_assessment", MappingProxyType(dict(self.ground_truth_assessment))
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if self.feasibility_matrix is not None:
            if self.feasibility_matrix.scenario_id != self.scenario_id:
                msg = (
                    "feasibility_matrix.scenario_id must match scenario_id, "
                    f"got {self.feasibility_matrix.scenario_id!r} vs {self.scenario_id!r}"
                )
                raise ValueError(msg)
            if self.feasibility_matrix.architecture_type is not self.architecture_type:
                msg = (
                    "feasibility_matrix.architecture_type must match architecture_type, "
                    f"got {self.feasibility_matrix.architecture_type.value!r} vs "
                    f"{self.architecture_type.value!r}"
                )
                raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Scoring rubric
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ScoringRubric:
    """Weights and parameters for governance benchmark scoring.

    Attributes
    ----------
    feasibility_weight : float
        Weight for feasibility component, in [0, 1].
    cascade_weight : float
        Weight for cascade component, in [0, 1].
    gap_penalty_weight : float
        Weight for gap penalty component, in [0, 1].
    """

    feasibility_weight: float = 0.5
    cascade_weight: float = 0.3
    gap_penalty_weight: float = 0.2

    def __post_init__(self) -> None:
        for name, val in [
            ("feasibility_weight", self.feasibility_weight),
            ("cascade_weight", self.cascade_weight),
            ("gap_penalty_weight", self.gap_penalty_weight),
        ]:
            _validate_unit_float(name, val)
        total = self.feasibility_weight + self.cascade_weight + self.gap_penalty_weight
        if abs(total - 1.0) > 1e-6:
            msg = f"Weights must sum to 1.0, got {total}"
            raise ValueError(msg)


# --------------------------------------------------------------------------- #
#  Architecture scores
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ArchitectureScore:
    """Governance benchmark score for a single architecture.

    Attributes
    ----------
    architecture_type : ArchitectureType
        Which architecture was scored.
    overall_score : float
        Weighted composite governance score, in [0, 1].
    feasibility_score : float
        Feasibility component score, in [0, 1].
    cascade_score : float | None
        Cascade component score, in [0, 1]. None for architectures without cascades.
    gap_score : float
        Gap penalty component score, in [0, 1] (1 = no gaps).
    breakdown : Mapping[str, float]
        Per-property or per-dimension score breakdown.
    """

    architecture_type: ArchitectureType
    overall_score: float
    feasibility_score: float
    cascade_score: float | None
    gap_score: float
    breakdown: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_unit_float("overall_score", self.overall_score)
        _validate_unit_float("feasibility_score", self.feasibility_score)
        if self.cascade_score is not None:
            _validate_unit_float("cascade_score", self.cascade_score)
        _validate_unit_float("gap_score", self.gap_score)
        object.__setattr__(self, "breakdown", MappingProxyType(dict(self.breakdown)))


# --------------------------------------------------------------------------- #
#  Cross-architecture comparison
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CrossArchitectureComparison:
    """Result of comparing governance scores across architectures.

    Attributes
    ----------
    scores : tuple[ArchitectureScore, ...]
        Per-architecture scores.
    ranking : tuple[ArchitectureType, ...]
        Architectures ranked from best to worst governance coverage.
    timestamp : datetime
        When the comparison was computed.
    """

    scores: tuple[ArchitectureScore, ...]
    ranking: tuple[ArchitectureType, ...]
    timestamp: datetime

    def __post_init__(self) -> None:
        if not self.scores:
            msg = "scores must be non-empty"
            raise ValueError(msg)
        if len(self.ranking) != len(self.scores):
            msg = (
                f"ranking length ({len(self.ranking)}) must match "
                f"scores length ({len(self.scores)})"
            )
            raise ValueError(msg)
        score_types = [score.architecture_type for score in self.scores]
        ranking_types = list(self.ranking)
        if len(set(score_types)) != len(score_types):
            msg = "scores must contain unique architecture types"
            raise ValueError(msg)
        if len(set(ranking_types)) != len(ranking_types):
            msg = "ranking must contain unique architecture types"
            raise ValueError(msg)
        if set(score_types) != set(ranking_types):
            msg = (
                "ranking types must match score types, "
                f"got {set(ranking_types)} vs {set(score_types)}"
            )
            raise ValueError(msg)
