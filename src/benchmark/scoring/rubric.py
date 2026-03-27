"""Governance assessment scoring rubric."""

from __future__ import annotations

from typing import TYPE_CHECKING

from benchmark.types import (
    ArchitectureScore,
    FeasibilityLevel,
    ScoringRubric,
)

if TYPE_CHECKING:
    from benchmark.types import CascadeTrace, FeasibilityMatrix, GovernanceGap

# Named constants for feasibility level scores (no magic numbers).
_FEASIBILITY_SCORES: dict[FeasibilityLevel, float] = {
    FeasibilityLevel.FILLABLE: 1.0,
    FeasibilityLevel.PARTIALLY_FILLABLE: 0.5,
    FeasibilityLevel.UNFILLABLE: 0.1,
    FeasibilityLevel.OPAQUE: 0.0,
}


def default_rubric() -> ScoringRubric:
    """Return the default scoring rubric.

    Returns
    -------
    ScoringRubric
        Rubric with feasibility=0.5, cascade=0.3, gap_penalty=0.2.
    """
    return ScoringRubric(
        feasibility_weight=0.5,
        cascade_weight=0.3,
        gap_penalty_weight=0.2,
    )


def score_feasibility(matrix: FeasibilityMatrix) -> float:
    """Compute feasibility score from a feasibility matrix.

    Parameters
    ----------
    matrix : FeasibilityMatrix
        The feasibility assessment.

    Returns
    -------
    float
        Weighted average feasibility score in [0, 1].
    """
    total = sum(_FEASIBILITY_SCORES[e.level] for e in matrix.entries)
    return total / len(matrix.entries)


def score_gaps(gaps: tuple[GovernanceGap, ...], *, max_gaps: int = 6) -> float:
    """Compute gap penalty score.

    Parameters
    ----------
    gaps : tuple[GovernanceGap, ...]
        Identified governance gaps.
    max_gaps : int
        Maximum possible gaps (number of Decision Event Schema properties). Default 6.

    Returns
    -------
    float
        Gap score in [0, 1] where 1.0 means no gaps.
    """
    if not gaps:
        return 1.0
    total_severity = sum(g.severity for g in gaps)
    return max(0.0, 1.0 - total_severity / max_gaps)


def score_cascade(trace: CascadeTrace | None) -> float | None:
    """Compute cascade score from a cascade trace.

    Parameters
    ----------
    trace : CascadeTrace or None
        The cascade trace, or None if architecture has no cascades.

    Returns
    -------
    float or None
        Cascade score in [0, 1] where 1.0 means no cascade severity.
        None if no trace provided.
    """
    if trace is None:
        return None

    from benchmark.scoring.cascade import compute_cascade_severity

    return max(0.0, 1.0 - compute_cascade_severity(trace))


def score_scenario(
    matrix: FeasibilityMatrix,
    gaps: tuple[GovernanceGap, ...],
    rubric: ScoringRubric,
    *,
    cascade_trace: CascadeTrace | None = None,
) -> ArchitectureScore:
    """Score a scenario using the rubric.

    Parameters
    ----------
    matrix : FeasibilityMatrix
        Feasibility assessment for the scenario.
    gaps : tuple[GovernanceGap, ...]
        Identified governance gaps.
    rubric : ScoringRubric
        Scoring weights.
    cascade_trace : CascadeTrace or None
        Cascade trace if applicable.

    Returns
    -------
    ArchitectureScore
        Computed score with breakdown.
    """
    feasibility = score_feasibility(matrix)
    gap = score_gaps(gaps)
    cascade = score_cascade(cascade_trace)

    # Compute overall score. If no cascade, redistribute its weight to feasibility.
    if cascade is not None:
        overall = (
            rubric.feasibility_weight * feasibility
            + rubric.cascade_weight * cascade
            + rubric.gap_penalty_weight * gap
        )
    else:
        # Redistribute cascade weight proportionally
        adjusted_feas_weight = rubric.feasibility_weight + rubric.cascade_weight
        overall = adjusted_feas_weight * feasibility + rubric.gap_penalty_weight * gap

    # Clamp to [0, 1]
    overall = max(0.0, min(1.0, overall))

    breakdown: dict[str, float] = {
        e.property_name: _FEASIBILITY_SCORES[e.level] for e in matrix.entries
    }

    return ArchitectureScore(
        architecture_type=matrix.architecture_type,
        overall_score=round(overall, 6),
        feasibility_score=round(feasibility, 6),
        cascade_score=round(cascade, 6) if cascade is not None else None,
        gap_score=round(gap, 6),
        breakdown=breakdown,
    )
