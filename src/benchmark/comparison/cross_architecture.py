"""Cross-architecture governance comparison."""

from __future__ import annotations

from typing import TYPE_CHECKING

from benchmark.types import CrossArchitectureComparison

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from benchmark.types import ArchitectureScore, ArchitectureType


def compare_architectures(
    scores: Sequence[ArchitectureScore],
    *,
    timestamp: datetime,
) -> CrossArchitectureComparison:
    """Compare governance scores across architectures.

    Parameters
    ----------
    scores : Sequence[ArchitectureScore]
        Per-architecture scores.
    timestamp : datetime
        When the comparison was computed.

    Returns
    -------
    CrossArchitectureComparison
        Comparison with ranking from best to worst.
    """
    sorted_scores = sorted(scores, key=lambda s: s.overall_score, reverse=True)
    ranking = tuple(s.architecture_type for s in sorted_scores)
    return CrossArchitectureComparison(
        scores=tuple(scores),
        ranking=ranking,
        timestamp=timestamp,
    )


def rank_by_feasibility(
    scores: Sequence[ArchitectureScore],
) -> tuple[ArchitectureType, ...]:
    """Rank architectures by feasibility score alone.

    Parameters
    ----------
    scores : Sequence[ArchitectureScore]
        Per-architecture scores.

    Returns
    -------
    tuple[ArchitectureType, ...]
        Architecture types ranked from best to worst feasibility.
    """
    sorted_scores = sorted(scores, key=lambda s: s.feasibility_score, reverse=True)
    return tuple(s.architecture_type for s in sorted_scores)


def compute_feasibility_gap(
    better: ArchitectureScore,
    worse: ArchitectureScore,
) -> float:
    """Compute the feasibility gap between two architectures.

    Parameters
    ----------
    better : ArchitectureScore
        Architecture with higher feasibility.
    worse : ArchitectureScore
        Architecture with lower feasibility.

    Returns
    -------
    float
        Absolute difference in feasibility scores.
    """
    return abs(better.feasibility_score - worse.feasibility_score)
