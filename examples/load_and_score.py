"""Load a single scenario and compute its governance score.

Demonstrates the basic scoring workflow: load scenario from disk,
compute feasibility + gap scores, print breakdown.
"""

from pathlib import Path

from benchmark.loaders.scenario import load_scenario
from benchmark.scoring.rubric import default_rubric, score_scenario

DATASET_ROOT = Path(__file__).parent.parent / "dataset"
RUBRIC = default_rubric()


def main() -> None:
    # Load the agentic AI scenario (worst governance coverage)
    path = (
        DATASET_ROOT
        / "architectures"
        / "agentic_ai"
        / "scenarios"
        / "aa-001-fraud-investigation.json"
    )
    scenario = load_scenario(path)

    print(f"Scenario:     {scenario.scenario_id}")
    print(f"Architecture: {scenario.architecture_type.value}")
    print(f"Gaps found:   {len(scenario.identified_gaps)}")
    print()

    if scenario.feasibility_matrix is not None:
        score = score_scenario(
            scenario.feasibility_matrix,
            scenario.identified_gaps,
            RUBRIC,
        )

        print(f"Overall score:     {score.overall_score:.3f}")
        print(f"Feasibility score: {score.feasibility_score:.3f}")
        print(f"Gap score:         {score.gap_score:.3f}")
        print()

        print("Per-property breakdown:")
        for prop, val in sorted(score.breakdown.items()):
            print(f"  {prop:40s} {val:.1f}")

        print()
        for gap in scenario.identified_gaps:
            print(f"  GAP: {gap.property_name} ({gap.gap_type}, severity={gap.severity:.1f})")
            print(f"       {gap.description}")


if __name__ == "__main__":
    main()
