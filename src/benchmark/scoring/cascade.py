"""Cascade of uncertainty analysis.

Only applicable to hybrid ML + rules and agentic AI architectures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from benchmark.types import CASCADE_ARCHITECTURES, CascadeStage

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from benchmark.types import ArchitectureType, CascadeTrace

# Compounding factor: each stage amplifies severity of subsequent stages.
_COMPOUNDING_FACTOR = 1.15


def validate_cascade_architecture(architecture_type: ArchitectureType) -> None:
    """Raise ValueError if architecture does not support cascades.

    Parameters
    ----------
    architecture_type : ArchitectureType
        Architecture to validate.

    Raises
    ------
    ValueError
        If architecture is not hybrid_ml_rules or agentic_ai.
    """
    if architecture_type not in CASCADE_ARCHITECTURES:
        msg = (
            f"Cascade analysis only valid for "
            f"{[a.value for a in CASCADE_ARCHITECTURES]}, "
            f"got {architecture_type.value}"
        )
        raise ValueError(msg)


def compute_cascade_severity(trace: CascadeTrace) -> float:
    """Compute compounding cascade severity.

    Each stage amplifies the severity of subsequent stages by a compounding
    factor, reflecting how governance failures propagate and compound.

    Parameters
    ----------
    trace : CascadeTrace
        A cascade of uncertainty trace.

    Returns
    -------
    float
        Compounding severity score in [0, 1].
    """
    validate_cascade_architecture(trace.architecture_type)

    compounded = 0.0
    for i, step in enumerate(trace.steps):
        compounded += step.severity * (_COMPOUNDING_FACTOR**i)

    # Normalize by the maximum possible compounded severity
    max_compounded = sum(_COMPOUNDING_FACTOR**i for i in range(len(trace.steps)))
    return min(1.0, compounded / max_compounded)


def detect_cascade_acceleration(
    traces: Sequence[CascadeTrace],
) -> Mapping[CascadeStage, float]:
    """Detect per-stage severity trends across multiple traces.

    Parameters
    ----------
    traces : Sequence[CascadeTrace]
        Multiple cascade traces to analyze.

    Returns
    -------
    Mapping[CascadeStage, float]
        Average severity per cascade stage.
    """
    stage_sums: dict[CascadeStage, float] = dict.fromkeys(CascadeStage, 0.0)
    stage_counts: dict[CascadeStage, int] = dict.fromkeys(CascadeStage, 0)

    for trace in traces:
        validate_cascade_architecture(trace.architecture_type)
        for step in trace.steps:
            stage_sums[step.stage] += step.severity
            stage_counts[step.stage] += 1

    return {
        stage: stage_sums[stage] / stage_counts[stage]
        for stage in CascadeStage
        if stage_counts[stage] > 0
    }


def cascade_summary(
    traces: Sequence[CascadeTrace],
) -> Mapping[str, object]:
    """Summary statistics for cascade analysis.

    Parameters
    ----------
    traces : Sequence[CascadeTrace]
        Cascade traces to summarize.

    Returns
    -------
    Mapping[str, object]
        Summary with trace_count, avg_severity, max_severity, stage_averages.
    """
    if not traces:
        return {
            "trace_count": 0,
            "avg_severity": 0.0,
            "max_severity": 0.0,
            "stage_averages": {},
        }

    severities = [compute_cascade_severity(t) for t in traces]
    return {
        "trace_count": len(traces),
        "avg_severity": sum(severities) / len(severities),
        "max_severity": max(severities),
        "stage_averages": detect_cascade_acceleration(traces),
    }
