"""Feasibility matrix computation and cross-architecture comparison."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from benchmark.types import (
        ArchitectureType,
        FeasibilityLevel,
        FeasibilityMatrix,
    )


def compute_cross_architecture_feasibility(
    matrices: Sequence[FeasibilityMatrix],
) -> Mapping[str, Mapping[ArchitectureType, FeasibilityLevel]]:
    """Compute cross-architecture feasibility comparison.

    For each Decision Event Schema property, shows its feasibility level across all architectures.

    Parameters
    ----------
    matrices : Sequence[FeasibilityMatrix]
        One matrix per architecture type.

    Returns
    -------
    Mapping[str, Mapping[ArchitectureType, FeasibilityLevel]]
        Property name -> architecture type -> feasibility level.
    """
    result: dict[str, dict[ArchitectureType, FeasibilityLevel]] = {}

    for matrix in matrices:
        for entry in matrix.entries:
            if entry.property_name not in result:
                result[entry.property_name] = {}
            result[entry.property_name][matrix.architecture_type] = entry.level

    return result


def feasibility_summary(
    matrices: Sequence[FeasibilityMatrix],
) -> Mapping[ArchitectureType, Mapping[str, float]]:
    """Summarize feasibility ratios per architecture.

    Parameters
    ----------
    matrices : Sequence[FeasibilityMatrix]
        One matrix per architecture type.

    Returns
    -------
    Mapping[ArchitectureType, Mapping[str, float]]
        Architecture type -> {fillable_ratio, opaque_ratio, entry_count}.
    """
    return {
        m.architecture_type: {
            "fillable_ratio": m.fillable_ratio,
            "opaque_ratio": m.opaque_ratio,
            "entry_count": float(len(m.entries)),
        }
        for m in matrices
    }
