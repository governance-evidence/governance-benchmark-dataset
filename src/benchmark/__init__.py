"""Governance Benchmark Dataset -- evaluation harness for cross-architecture comparison.

The package root exposes the stable public API for types, scoring, comparison,
and data loading.

Parquet support lives under ``benchmark.loaders.parquet`` and requires the
``parquet`` extra: ``pip install governance-benchmark-dataset[parquet]``.
"""

from __future__ import annotations

from benchmark.comparison.cross_architecture import (
    compare_architectures,
    compute_feasibility_gap,
    rank_by_feasibility,
)
from benchmark.comparison.tables import (
    generate_cascade_table,
    generate_feasibility_level_table,
    generate_feasibility_table,
    generate_score_breakdown_table,
    generate_summary_table,
)
from benchmark.loaders.scenario import (
    load_architecture_metadata,
    load_scenario,
    load_scenarios,
)
from benchmark.scoring.cascade import (
    cascade_summary,
    compute_cascade_severity,
    detect_cascade_acceleration,
)
from benchmark.scoring.feasibility import (
    compute_cross_architecture_feasibility,
    feasibility_summary,
)
from benchmark.scoring.rubric import (
    default_rubric,
    score_cascade,
    score_feasibility,
    score_gaps,
    score_scenario,
)
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

__version__ = "0.1.0"
ROOT_API_STABILITY = "stable"

__all__ = [
    "CASCADE_ARCHITECTURES",
    "ArchitectureMetadata",
    "ArchitectureScore",
    "ArchitectureType",
    "CascadeStage",
    "CascadeStep",
    "CascadeTrace",
    "CollapseModality",
    "CrossArchitectureComparison",
    "FeasibilityEntry",
    "FeasibilityLevel",
    "FeasibilityMatrix",
    "GovernanceGap",
    "ScenarioRecord",
    "ScoringRubric",
    "StructuralBreak",
    "cascade_summary",
    "compare_architectures",
    "compute_cascade_severity",
    "compute_cross_architecture_feasibility",
    "compute_feasibility_gap",
    "default_rubric",
    "detect_cascade_acceleration",
    "feasibility_summary",
    "generate_cascade_table",
    "generate_feasibility_level_table",
    "generate_feasibility_table",
    "generate_score_breakdown_table",
    "generate_summary_table",
    "load_architecture_metadata",
    "load_scenario",
    "load_scenarios",
    "rank_by_feasibility",
    "score_cascade",
    "score_feasibility",
    "score_gaps",
    "score_scenario",
]
