"""Parquet loader and writer for feasibility matrices.

Requires the ``parquet`` extra: ``pip install governance-benchmark-dataset[parquet]``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from benchmark.types import (
    ArchitectureType,
    FeasibilityEntry,
    FeasibilityLevel,
    FeasibilityMatrix,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def save_feasibility_parquet(
    matrices: Sequence[FeasibilityMatrix],
    path: Path,
) -> None:
    """Save feasibility matrices to a Parquet file.

    Parameters
    ----------
    matrices : Sequence[FeasibilityMatrix]
        Matrices to save.
    path : Path
        Output Parquet file path.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    rows: list[dict[str, object]] = [
        {
            "architecture_type": matrix.architecture_type.value,
            "scenario_id": matrix.scenario_id,
            "property_name": entry.property_name,
            "level": entry.level.value,
            "recovery_cost": entry.recovery_cost,
            "notes": entry.notes,
            "fillable_ratio": matrix.fillable_ratio,
            "opaque_ratio": matrix.opaque_ratio,
            "timestamp": matrix.timestamp.isoformat(),
        }
        for matrix in matrices
        for entry in matrix.entries
    ]

    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


def load_feasibility_parquet(
    path: Path,
) -> Sequence[FeasibilityMatrix]:
    """Load feasibility matrices from a Parquet file.

    Parameters
    ----------
    path : Path
        Path to Parquet file.

    Returns
    -------
    Sequence[FeasibilityMatrix]
        Loaded matrices, one per (architecture_type, scenario_id) pair.
    """
    import pyarrow.parquet as pq

    from benchmark.loaders.scenario import _parse_datetime

    table = pq.read_table(path)
    if table.num_rows == 0:
        return []
    df = table.to_pydict()

    # Group rows by (architecture_type, scenario_id)
    groups: dict[tuple[str, str], list[int]] = {}
    for i in range(len(df["architecture_type"])):
        key = (df["architecture_type"][i], df["scenario_id"][i])
        groups.setdefault(key, []).append(i)

    matrices: list[FeasibilityMatrix] = []
    for (arch_str, scenario_id), indices in groups.items():
        entries = tuple(
            FeasibilityEntry(
                property_name=df["property_name"][i],
                level=FeasibilityLevel(df["level"][i]),
                recovery_cost=float(df["recovery_cost"][i]),
                notes=str(df["notes"][i]),
            )
            for i in indices
        )
        first = indices[0]
        matrices.append(
            FeasibilityMatrix(
                architecture_type=ArchitectureType(arch_str),
                scenario_id=scenario_id,
                entries=entries,
                timestamp=_parse_datetime(df["timestamp"][first]),
                fillable_ratio=float(df["fillable_ratio"][first]),
                opaque_ratio=float(df["opaque_ratio"][first]),
            )
        )

    return matrices
