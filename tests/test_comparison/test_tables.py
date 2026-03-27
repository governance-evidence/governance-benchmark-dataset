"""Tests for table generation."""

from benchmark.comparison.tables import (
    generate_cascade_table,
    generate_feasibility_level_table,
    generate_feasibility_table,
    generate_score_breakdown_table,
    generate_summary_table,
)
from benchmark.types import ArchitectureType
from tests.fixtures.factories import make_cascade_trace, make_feasibility_matrix


class TestGenerateFeasibilityTable:
    def test_has_rows(self):
        matrices = [
            make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES),
            make_feasibility_matrix(ArchitectureType.AGENTIC_AI),
        ]
        table = generate_feasibility_level_table(matrices)
        assert len(table) > 0
        assert "property_name" in table[0]

    def test_uses_feasibility_level_values(self):
        matrices = [
            make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES),
            make_feasibility_matrix(ArchitectureType.AGENTIC_AI),
        ]
        table = generate_feasibility_level_table(matrices)
        first_row = table[0]
        assert first_row[ArchitectureType.DETERMINISTIC_RULES.value] in {
            "fillable",
            "partially_fillable",
            "unfillable",
            "opaque",
        }


class TestGenerateScoreBreakdownTable:
    def test_uses_numeric_values(self, comparison):
        table = generate_score_breakdown_table(comparison)
        assert len(table) > 0
        first_row = table[0]
        assert isinstance(first_row[ArchitectureType.DETERMINISTIC_RULES.value], float)


class TestLegacyGenerateFeasibilityTable:
    def test_matches_score_breakdown_table(self, comparison):
        legacy = generate_feasibility_table(comparison)
        explicit = generate_score_breakdown_table(comparison)
        assert legacy == explicit


class TestGenerateSummaryTable:
    def test_four_rows(self, comparison):
        table = generate_summary_table(comparison)
        assert len(table) == 4
        # First row should be rank 1
        assert table[0]["rank"] == 1

    def test_has_all_fields(self, comparison):
        table = generate_summary_table(comparison)
        for row in table:
            assert "architecture" in row
            assert "overall_score" in row
            assert "feasibility_score" in row
            assert "rank" in row


class TestGenerateCascadeTable:
    def test_has_five_stages(self):
        hybrid = ArchitectureType.HYBRID_ML_RULES
        agentic = ArchitectureType.AGENTIC_AI
        traces = {
            hybrid: [make_cascade_trace(hybrid)],
            agentic: [make_cascade_trace(agentic)],
        }
        table = generate_cascade_table(traces)
        assert len(table) == 5
        assert table[0]["stage"] == "feature_incorrectness"

    def test_empty_trace_list_skipped(self):
        traces = {ArchitectureType.HYBRID_ML_RULES: []}
        table = generate_cascade_table(traces)
        assert len(table) == 5
        # No stage data since trace list is empty
        for row in table:
            assert row["stage"] is not None

    def test_empty_traces_dict(self):
        table = generate_cascade_table({})
        assert len(table) == 5
