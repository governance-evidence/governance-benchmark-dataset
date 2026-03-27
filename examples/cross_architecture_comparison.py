"""Cross-architecture governance comparison example.

Loads seed scenarios from all four architecture types, scores each one,
and produces ranked score tables and raw feasibility level tables.
"""

from datetime import UTC, datetime
from pathlib import Path

from benchmark.comparison.cross_architecture import compare_architectures
from benchmark.comparison.tables import (
    generate_feasibility_level_table,
    generate_score_breakdown_table,
    generate_summary_table,
)
from benchmark.loaders.scenario import load_scenarios
from benchmark.scoring.rubric import default_rubric, score_scenario
from benchmark.types import ArchitectureScore, ArchitectureType

DATASET_ROOT = Path(__file__).parent.parent / "dataset"
RUBRIC = default_rubric()

_ARCH_LABELS = {
    ArchitectureType.DETERMINISTIC_RULES.value: "det_rules",
    ArchitectureType.HYBRID_ML_RULES.value: "hybrid",
    ArchitectureType.STREAMING_FEATURES.value: "streaming",
    ArchitectureType.AGENTIC_AI.value: "agentic",
}

_LEVEL_LABELS = {
    "fillable": "fill",
    "partially_fillable": "partial",
    "unfillable": "unfill",
    "opaque": "opaque",
}


def _print_table(title: str, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Render rows as a compact markdown table."""
    if not rows:
        print(f"\n--- {title} ---")
        print("(no rows)")
        return

    string_rows = [
        {column: "" if row.get(column) is None else str(row.get(column)) for column in columns}
        for row in rows
    ]
    widths = [max(len(column), *(len(row[column]) for row in string_rows)) for column in columns]

    print(f"\n--- {title} ---")
    print(
        "|"
        + "|".join(column.ljust(width) for column, width in zip(columns, widths, strict=True))
        + "|"
    )
    print("|" + "|".join("-" * width for width in widths) + "|")
    for row in string_rows:
        print(
            "|"
            + "|".join(
                row[column].ljust(width) for column, width in zip(columns, widths, strict=True)
            )
            + "|"
        )


def _display_columns(columns: list[str]) -> list[str]:
    """Return compact display labels for table columns."""
    return [_ARCH_LABELS.get(column, column) for column in columns]


def _remap_row_keys(row: dict[str, object], columns: list[str]) -> dict[str, object]:
    """Map internal column names to compact display labels."""
    display_columns = _display_columns(columns)
    return {
        display_column: row[column]
        for column, display_column in zip(columns, display_columns, strict=True)
    }


def aggregate_architecture_scores(
    architecture_type: ArchitectureType,
    scenario_scores: list[ArchitectureScore],
) -> ArchitectureScore:
    """Aggregate multiple scenario scores into one per architecture."""
    cascade_scores = [
        score.cascade_score for score in scenario_scores if score.cascade_score is not None
    ]
    breakdown_keys = {key for score in scenario_scores for key in score.breakdown}

    return ArchitectureScore(
        architecture_type=architecture_type,
        overall_score=sum(score.overall_score for score in scenario_scores) / len(scenario_scores),
        feasibility_score=(
            sum(score.feasibility_score for score in scenario_scores) / len(scenario_scores)
        ),
        cascade_score=(sum(cascade_scores) / len(cascade_scores)) if cascade_scores else None,
        gap_score=sum(score.gap_score for score in scenario_scores) / len(scenario_scores),
        breakdown={
            key: sum(score.breakdown[key] for score in scenario_scores if key in score.breakdown)
            / sum(1 for score in scenario_scores if key in score.breakdown)
            for key in sorted(breakdown_keys)
        },
    )


def main() -> None:
    scores = []
    matrices = []
    for arch in ArchitectureType:
        scenario_dir = DATASET_ROOT / "architectures" / arch.value / "scenarios"
        scenarios = load_scenarios(scenario_dir)
        scenario_scores = []
        for scenario in scenarios:
            if scenario.feasibility_matrix is not None:
                matrices.append(scenario.feasibility_matrix)
                score = score_scenario(
                    scenario.feasibility_matrix,
                    scenario.identified_gaps,
                    RUBRIC,
                )
                scenario_scores.append(score)

        if scenario_scores:
            scores.append(aggregate_architecture_scores(arch, scenario_scores))

    if scores:
        comparison = compare_architectures(scores, timestamp=datetime.now(tz=UTC))
        summary_table = generate_summary_table(comparison)
        score_table = generate_score_breakdown_table(comparison)
        level_table = generate_feasibility_level_table(matrices)

        print("\nLabels: det_rules=deterministic_rules, hybrid=hybrid_ml_rules")
        print("        streaming=streaming_features, agentic=agentic_ai")

        formatted_summary = [
            {
                "rank": row["rank"],
                "architecture": _ARCH_LABELS.get(
                    str(row["architecture"]), str(row["architecture"])
                ),
                "overall": f"{row['overall_score']:.3f}",
                "feasibility": f"{row['feasibility_score']:.3f}",
                "cascade": "-" if row["cascade_score"] is None else f"{row['cascade_score']:.3f}",
                "gap": f"{row['gap_score']:.3f}",
            }
            for row in summary_table
        ]
        _print_table(
            "Summary Table",
            formatted_summary,
            ["rank", "architecture", "overall", "feasibility", "cascade", "gap"],
        )

        breakdown_columns = ["property_name"] + [arch.value for arch in ArchitectureType]
        formatted_score_rows = [
            {
                column: (row[column] if column == "property_name" else f"{float(row[column]):.3f}")
                for column in breakdown_columns
            }
            for row in score_table[:3]
        ]
        _print_table(
            "Score Breakdown Table",
            [_remap_row_keys(row, breakdown_columns) for row in formatted_score_rows],
            _display_columns(breakdown_columns),
        )

        level_columns = ["property_name"] + [arch.value for arch in ArchitectureType]
        formatted_level_rows = [
            {
                column: (
                    row[column]
                    if column == "property_name"
                    else _LEVEL_LABELS.get(str(row[column]), str(row[column]))
                )
                for column in level_columns
            }
            for row in level_table[:3]
        ]
        _print_table(
            "Feasibility Level Table",
            [_remap_row_keys(row, level_columns) for row in formatted_level_rows],
            _display_columns(level_columns),
        )


if __name__ == "__main__":
    main()
