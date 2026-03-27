"""Load scenario records, architecture metadata, and validate against schemas."""

from __future__ import annotations

import json
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING, Any

from benchmark.types import (
    ArchitectureMetadata,
    ArchitectureType,
    CollapseModality,
    FeasibilityEntry,
    FeasibilityLevel,
    FeasibilityMatrix,
    GovernanceGap,
    ScenarioRecord,
    StructuralBreak,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime


def _parse_datetime(value: str) -> datetime:
    """Parse ISO 8601 datetime string to timezone-aware datetime."""
    from datetime import datetime as dt

    parsed = dt.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _get_float(data: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Extract a float from a JSON dict safely."""
    raw = data.get(key, default)
    return float(raw) if raw is not None else default


def _get_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    """Extract a dict from a JSON dict with defensive check."""
    raw = data.get(key, {})
    if not isinstance(raw, dict):  # pragma: no cover
        msg = f"{key} must be a dict"
        raise TypeError(msg)
    return raw


def _get_list(data: dict[str, Any], key: str) -> list[Any]:
    """Extract a list from a JSON dict with defensive check."""
    raw = data.get(key, [])
    if not isinstance(raw, list):  # pragma: no cover
        msg = f"{key} must be a list"
        raise TypeError(msg)
    return raw


def _parse_feasibility_entry(data: dict[str, Any]) -> FeasibilityEntry:
    """Parse a feasibility entry from a JSON dict."""
    return FeasibilityEntry(
        property_name=str(data["property_name"]),
        level=FeasibilityLevel(str(data["level"])),
        recovery_cost=_get_float(data, "recovery_cost"),
        notes=str(data.get("notes", "")),
    )


def _parse_feasibility_matrix(data: dict[str, Any]) -> FeasibilityMatrix:
    """Parse a feasibility matrix from a JSON dict."""
    entries_raw = _get_list(data, "entries")
    entries = tuple(_parse_feasibility_entry(e) for e in entries_raw)
    return FeasibilityMatrix(
        architecture_type=ArchitectureType(str(data["architecture_type"])),
        scenario_id=str(data["scenario_id"]),
        entries=entries,
        timestamp=_parse_datetime(str(data.get("timestamp", "2026-01-01T00:00:00Z"))),
        fillable_ratio=_get_float(data, "fillable_ratio"),
        opaque_ratio=_get_float(data, "opaque_ratio"),
    )


def _parse_governance_gap(data: dict[str, Any]) -> GovernanceGap:
    """Parse a governance gap from a JSON dict."""
    return GovernanceGap(
        property_name=str(data["property_name"]),
        gap_type=str(data["gap_type"]),
        severity=float(data["severity"]),
        description=str(data["description"]),
    )


def load_scenario(path: Path) -> ScenarioRecord:
    """Load a single scenario record from a JSON file.

    Parameters
    ----------
    path : Path
        Path to a scenario JSON file.

    Returns
    -------
    ScenarioRecord
        The parsed scenario.
    """
    with path.open() as f:
        data: dict[str, Any] = json.load(f)

    feasibility_raw = data.get("feasibility_matrix")
    feasibility = (
        _parse_feasibility_matrix(feasibility_raw) if isinstance(feasibility_raw, dict) else None
    )

    gaps_raw = _get_list(data, "identified_gaps")
    gaps = tuple(_parse_governance_gap(g) for g in gaps_raw)

    ts_raw = data.get("timestamp")
    timestamp = _parse_datetime(str(ts_raw)) if ts_raw else None

    return ScenarioRecord(
        scenario_id=str(data["scenario_id"]),
        architecture_type=ArchitectureType(str(data["architecture_type"])),
        decision_event=_get_dict(data, "decision_event"),
        ground_truth_assessment=_get_dict(data, "ground_truth_assessment"),
        feasibility_matrix=feasibility,
        identified_gaps=gaps,
        timestamp=timestamp,
        metadata=_get_dict(data, "metadata"),
    )


def load_scenarios(directory: Path) -> Sequence[ScenarioRecord]:
    """Load all scenario records from a directory of JSON files.

    Parameters
    ----------
    directory : Path
        Directory containing scenario JSON files.

    Returns
    -------
    Sequence[ScenarioRecord]
        All loaded scenarios, sorted by scenario_id.
    """
    return [load_scenario(p) for p in sorted(directory.glob("*.json"))]


def load_architecture_metadata(path: Path) -> ArchitectureMetadata:
    """Load architecture metadata from a JSON file.

    Parameters
    ----------
    path : Path
        Path to a metadata.json file.

    Returns
    -------
    ArchitectureMetadata
        The parsed metadata.
    """
    with path.open() as f:
        data: dict[str, Any] = json.load(f)

    collapse_raw = _get_list(data, "primary_collapse_modalities")
    collapse = tuple(CollapseModality(str(c)) for c in collapse_raw)

    breaks_raw = _get_list(data, "structural_breaks")
    breaks = tuple(StructuralBreak(str(b)) for b in breaks_raw)

    return ArchitectureMetadata(
        architecture_type=ArchitectureType(str(data["architecture_type"])),
        description=str(data["description"]),
        primary_collapse_modalities=collapse,
        structural_breaks=breaks,
        decision_path_enumerable=bool(data.get("decision_path_enumerable", False)),
        has_cascade_traces=bool(data.get("has_cascade_traces", False)),
    )


def validate_scenario_against_schema(
    data: dict[str, object],
    *,
    schema_path: Path | None = None,
) -> None:
    """Validate scenario data against the JSON schema.

    Parameters
    ----------
    data : dict
        Scenario data to validate.
    schema_path : Path or None
        Path to scenario schema. Defaults to bundled schema.

    Raises
    ------
    ImportError
        If jsonschema is not installed.
    jsonschema.ValidationError
        If data does not conform to the schema.
    """
    import jsonschema

    if schema_path is None:
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "dataset"
            / "schemas"
            / "scenario.schema.json"
        )

    with schema_path.open() as f:
        schema = json.load(f)

    jsonschema.validate(instance=data, schema=schema)
