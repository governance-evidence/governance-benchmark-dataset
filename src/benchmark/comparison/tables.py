"""Paper 16 table generation for cross-architecture comparison."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from benchmark.types import (
        ArchitectureType,
        CascadeTrace,
        CrossArchitectureComparison,
        FeasibilityMatrix,
    )


def generate_score_breakdown_table(
    comparison: CrossArchitectureComparison,
) -> Sequence[Mapping[str, object]]:
    """Generate a per-property numeric score breakdown table.

    Rows: Decision Event Schema properties. Columns: architecture types with numeric
    breakdown values derived from comparison scores.

    Parameters
    ----------
    comparison : CrossArchitectureComparison
        The cross-architecture comparison result.

    Returns
    -------
    Sequence[Mapping[str, object]]
        Table rows with property_name and per-architecture numeric values.
    """
    all_properties: set[str] = set()
    for score in comparison.scores:
        all_properties.update(score.breakdown.keys())

    rows: list[dict[str, object]] = []
    for prop in sorted(all_properties):
        row: dict[str, object] = {"property_name": prop}
        for score in comparison.scores:
            row[score.architecture_type.value] = score.breakdown.get(prop)
        rows.append(row)

    return rows


def generate_feasibility_table(
    comparison: CrossArchitectureComparison,
) -> Sequence[Mapping[str, object]]:
    """Generate a legacy per-property comparison table.

    Notes
    -----
    This function returns numeric score breakdown values, not raw
    feasibility levels. Prefer generate_score_breakdown_table for
    explicit numeric semantics or generate_feasibility_level_table
    when you need raw feasibility level values.
    """
    return generate_score_breakdown_table(comparison)


def generate_feasibility_level_table(
    matrices: Sequence[FeasibilityMatrix],
) -> Sequence[Mapping[str, object]]:
    """Generate a feasibility level table from feasibility matrices.

    Rows: Decision Event Schema properties. Columns: architecture types with raw
    feasibility level values.
    """
    rows_by_property: dict[str, dict[str, object]] = {}
    for matrix in matrices:
        for entry in matrix.entries:
            row = rows_by_property.setdefault(
                entry.property_name,
                {"property_name": entry.property_name},
            )
            row[matrix.architecture_type.value] = entry.level.value

    return [rows_by_property[prop] for prop in sorted(rows_by_property)]


def generate_summary_table(
    comparison: CrossArchitectureComparison,
) -> Sequence[Mapping[str, object]]:
    """Generate the summary comparison table for Paper 16.

    One row per architecture: overall, feasibility, cascade, gap scores, rank.

    Parameters
    ----------
    comparison : CrossArchitectureComparison
        The cross-architecture comparison result.

    Returns
    -------
    Sequence[Mapping[str, object]]
        Table rows ordered by ranking.
    """
    rank_map = {arch: i + 1 for i, arch in enumerate(comparison.ranking)}

    rows: list[dict[str, object]] = [
        {
            "architecture": score.architecture_type.value,
            "overall_score": score.overall_score,
            "feasibility_score": score.feasibility_score,
            "cascade_score": score.cascade_score,
            "gap_score": score.gap_score,
            "rank": rank_map[score.architecture_type],
        }
        for score in comparison.scores
    ]

    rows.sort(key=lambda r: int(str(r["rank"])))
    return rows


def generate_cascade_table(
    traces_by_arch: Mapping[ArchitectureType, Sequence[CascadeTrace]],
) -> Sequence[Mapping[str, object]]:
    """Generate the cascade comparison table for Paper 16.

    Rows: cascade stages. Columns: architectures with cascade support.

    Parameters
    ----------
    traces_by_arch : Mapping[ArchitectureType, Sequence[CascadeTrace]]
        Cascade traces grouped by architecture type.

    Returns
    -------
    Sequence[Mapping[str, object]]
        Table rows with stage and per-architecture average severity.
    """
    from benchmark.scoring.cascade import detect_cascade_acceleration

    # Compute per-stage averages for each architecture
    arch_stages: dict[ArchitectureType, Mapping[str, float]] = {}
    for arch, traces in traces_by_arch.items():
        if traces:
            accel = detect_cascade_acceleration(traces)
            arch_stages[arch] = {stage.value: sev for stage, sev in accel.items()}

    # Build table
    from benchmark.types import CascadeStage

    rows: list[dict[str, object]] = []
    for stage in CascadeStage:
        row: dict[str, object] = {"stage": stage.value}
        for arch, stages in arch_stages.items():
            row[arch.value] = stages.get(stage.value)
        rows.append(row)

    return rows
