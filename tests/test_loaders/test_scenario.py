"""Tests for scenario loaders."""

import json
from pathlib import Path

import pytest

from benchmark.loaders.scenario import (
    load_architecture_metadata,
    load_scenario,
    load_scenarios,
    validate_scenario_against_schema,
)
from benchmark.types import ArchitectureType

_DATASET_ROOT = Path(__file__).parent.parent.parent / "dataset"
_ARCH = _DATASET_ROOT / "architectures"

_ARCH_NAMES = (
    "deterministic_rules",
    "hybrid_ml_rules",
    "streaming_features",
    "agentic_ai",
)


@pytest.mark.integration
class TestLoadScenario:
    def test_load_deterministic(self):
        path = _ARCH / "deterministic_rules" / "scenarios"
        scenario = load_scenario(path / "dr-001-policy-engine.json")
        assert scenario.scenario_id == "dr-001-policy-engine"
        assert scenario.architecture_type == ArchitectureType.DETERMINISTIC_RULES
        assert scenario.feasibility_matrix is not None
        assert scenario.feasibility_matrix.fillable_ratio == 1.0
        assert len(scenario.identified_gaps) == 0

    def test_load_hybrid(self):
        path = _ARCH / "hybrid_ml_rules" / "scenarios"
        scenario = load_scenario(path / "hm-001-fraud-scoring.json")
        assert scenario.architecture_type == ArchitectureType.HYBRID_ML_RULES
        assert len(scenario.identified_gaps) == 2

    def test_load_streaming(self):
        path = _ARCH / "streaming_features" / "scenarios"
        scenario = load_scenario(path / "sf-001-realtime-risk.json")
        assert scenario.architecture_type == ArchitectureType.STREAMING_FEATURES
        assert len(scenario.identified_gaps) == 3

    def test_load_agentic(self):
        path = _ARCH / "agentic_ai" / "scenarios"
        scenario = load_scenario(path / "aa-001-fraud-investigation.json")
        assert scenario.architecture_type == ArchitectureType.AGENTIC_AI
        assert len(scenario.identified_gaps) == 4
        assert scenario.feasibility_matrix is not None
        assert scenario.feasibility_matrix.opaque_ratio == pytest.approx(0.333, abs=0.01)


@pytest.mark.integration
class TestLoadScenarios:
    def test_load_all_deterministic(self):
        directory = _ARCH / "deterministic_rules" / "scenarios"
        scenarios = load_scenarios(directory)
        assert len(scenarios) >= 1
        assert all(s.architecture_type == ArchitectureType.DETERMINISTIC_RULES for s in scenarios)

    def test_load_empty_directory(self, tmp_path):
        scenarios = load_scenarios(tmp_path)
        assert len(scenarios) == 0


@pytest.mark.integration
class TestLoadArchitectureMetadata:
    def test_load_all_four(self):
        for arch_name in _ARCH_NAMES:
            path = _ARCH / arch_name / "metadata.json"
            meta = load_architecture_metadata(path)
            assert meta.architecture_type == ArchitectureType(arch_name)

    def test_deterministic_enumerable(self):
        path = _ARCH / "deterministic_rules" / "metadata.json"
        meta = load_architecture_metadata(path)
        assert meta.decision_path_enumerable is True
        assert meta.has_cascade_traces is False

    def test_agentic_structural_breaks(self):
        path = _ARCH / "agentic_ai" / "metadata.json"
        meta = load_architecture_metadata(path)
        assert len(meta.structural_breaks) == 3
        assert meta.has_cascade_traces is True


class TestParseDatetime:
    def test_naive_datetime_gets_utc(self, tmp_path):
        """Timestamps without timezone info should get UTC."""
        scenario_data = {
            "scenario_id": "test-naive-ts",
            "architecture_type": "deterministic_rules",
            "decision_event": {
                "schema_version": "0.3.0",
                "decision_id": "test",
                "timestamp": "2026-01-01T00:00:00",
                "decision_type": "automated",
                "decision_context": {
                    "decision_id": "test",
                    "decision_type": "aml_compliance",
                },
                "decision_logic": {
                    "logic_type": "rule_based",
                    "output": "approve",
                },
                "human_override_record": {
                    "override_occurred": False,
                },
                "temporal_metadata": {
                    "event_timestamp": "2026-01-01T00:00:00",
                    "sequence_number": 1,
                    "hash_chain": {
                        "previous_hash": None,
                        "current_hash": "test-hash",
                        "algorithm": "SHA-256",
                    },
                    "evidence_tier": "lightweight",
                },
            },
            "ground_truth_assessment": {},
            "feasibility_matrix": None,
            "identified_gaps": [],
            "timestamp": "2026-01-01T12:00:00",
            "metadata": {},
        }
        p = tmp_path / "test.json"
        p.write_text(json.dumps(scenario_data))
        scenario = load_scenario(p)
        assert scenario.timestamp is not None
        assert scenario.timestamp.tzinfo is not None


@pytest.mark.integration
class TestValidateScenario:
    def test_valid_scenario_passes(self):
        path = _ARCH / "deterministic_rules" / "scenarios"
        with (path / "dr-001-policy-engine.json").open() as f:
            data = json.load(f)
        validate_scenario_against_schema(data)

    def test_valid_with_explicit_schema_path(self):
        path = _ARCH / "deterministic_rules" / "scenarios"
        schema = _DATASET_ROOT / "schemas" / "scenario.schema.json"
        with (path / "dr-001-policy-engine.json").open() as f:
            data = json.load(f)
        validate_scenario_against_schema(data, schema_path=schema)

    def test_invalid_scenario_fails(self):
        import jsonschema

        with pytest.raises(jsonschema.ValidationError):
            validate_scenario_against_schema({"invalid": "data"})
