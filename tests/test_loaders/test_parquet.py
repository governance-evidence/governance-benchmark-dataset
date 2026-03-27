"""Tests for parquet loader/writer."""

import pytest

pytest.importorskip("pyarrow")

from benchmark.loaders.parquet import load_feasibility_parquet, save_feasibility_parquet
from benchmark.types import ArchitectureType, FeasibilityLevel
from tests.fixtures.factories import make_feasibility_matrix


class TestParquetRoundTrip:
    def test_single_matrix(self, tmp_path):
        matrix = make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES)
        path = tmp_path / "test.parquet"

        save_feasibility_parquet([matrix], path)
        loaded = load_feasibility_parquet(path)

        assert len(loaded) == 1
        result = loaded[0]
        assert result.architecture_type == matrix.architecture_type
        assert result.scenario_id == matrix.scenario_id
        assert result.fillable_ratio == matrix.fillable_ratio
        assert result.opaque_ratio == matrix.opaque_ratio
        assert len(result.entries) == len(matrix.entries)
        for orig, loaded_e in zip(matrix.entries, result.entries, strict=True):
            assert orig.property_name == loaded_e.property_name
            assert orig.level == loaded_e.level
            assert orig.recovery_cost == loaded_e.recovery_cost

    def test_multiple_matrices(self, tmp_path):
        det = make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES)
        agt = make_feasibility_matrix(ArchitectureType.AGENTIC_AI)
        path = tmp_path / "multi.parquet"

        save_feasibility_parquet([det, agt], path)
        loaded = load_feasibility_parquet(path)

        assert len(loaded) == 2
        types = {m.architecture_type for m in loaded}
        assert types == {
            ArchitectureType.DETERMINISTIC_RULES,
            ArchitectureType.AGENTIC_AI,
        }

    def test_empty_list(self, tmp_path):
        path = tmp_path / "empty.parquet"
        save_feasibility_parquet([], path)
        loaded = load_feasibility_parquet(path)
        assert len(loaded) == 0

    def test_entries_preserve_level(self, tmp_path):
        agt = make_feasibility_matrix(ArchitectureType.AGENTIC_AI)
        path = tmp_path / "levels.parquet"

        save_feasibility_parquet([agt], path)
        loaded = load_feasibility_parquet(path)

        result = loaded[0]
        levels = {e.level for e in result.entries}
        assert FeasibilityLevel.OPAQUE in levels
        assert FeasibilityLevel.PARTIALLY_FILLABLE in levels
