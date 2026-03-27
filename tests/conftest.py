"""Shared fixtures for governance benchmark tests."""

import pytest

from benchmark.types import (
    ArchitectureMetadata,
    ArchitectureScore,
    ArchitectureType,
    CascadeTrace,
    CrossArchitectureComparison,
    FeasibilityMatrix,
    ScenarioRecord,
    ScoringRubric,
)
from tests.fixtures.factories import (
    make_agentic_metadata,
    make_architecture_score,
    make_cascade_trace,
    make_cross_architecture_comparison,
    make_deterministic_metadata,
    make_feasibility_matrix,
    make_hybrid_metadata,
    make_rubric,
    make_scenario_record,
    make_streaming_metadata,
)


@pytest.fixture
def deterministic_meta() -> ArchitectureMetadata:
    return make_deterministic_metadata()


@pytest.fixture
def hybrid_meta() -> ArchitectureMetadata:
    return make_hybrid_metadata()


@pytest.fixture
def streaming_meta() -> ArchitectureMetadata:
    return make_streaming_metadata()


@pytest.fixture
def agentic_meta() -> ArchitectureMetadata:
    return make_agentic_metadata()


@pytest.fixture
def deterministic_matrix() -> FeasibilityMatrix:
    return make_feasibility_matrix(ArchitectureType.DETERMINISTIC_RULES)


@pytest.fixture
def agentic_matrix() -> FeasibilityMatrix:
    return make_feasibility_matrix(ArchitectureType.AGENTIC_AI)


@pytest.fixture
def hybrid_cascade() -> CascadeTrace:
    return make_cascade_trace(ArchitectureType.HYBRID_ML_RULES)


@pytest.fixture
def deterministic_scenario() -> ScenarioRecord:
    return make_scenario_record(ArchitectureType.DETERMINISTIC_RULES)


@pytest.fixture
def rubric() -> ScoringRubric:
    return make_rubric()


@pytest.fixture
def deterministic_score() -> ArchitectureScore:
    return make_architecture_score(ArchitectureType.DETERMINISTIC_RULES)


@pytest.fixture
def comparison() -> CrossArchitectureComparison:
    return make_cross_architecture_comparison()
