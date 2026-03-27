# Feasibility Matrix

The feasibility matrix is the core data structure of the benchmark. For each
scenario, it maps every Decision Event Schema property to a feasibility level.

## Decision Event Schema Properties

The six optional properties from the Decision Event Schema, each resisting
a specific governance degradation type:

| Property | Resists |
|---|---|
| `decision_context` | Content Staleness |
| `decision_logic` | Schema Drift |
| `decision_boundary` | Coverage Erosion |
| `decision_quality_indicators` | Metric Erosion |
| `human_override_record` | Override Accumulation |
| `temporal_metadata` | Content Staleness (temporal) |

## Four Feasibility Levels

- **Fillable**: Property can be fully populated from available system state
- **Partially Fillable**: Property can be partially populated; some aspects
  are recoverable but others require inference or replay
- **Unfillable**: Property cannot be populated; the required information
  does not exist in the system
- **Opaque**: Property cannot be populated because the underlying process
  is fundamentally not inspectable

## Cross-Architecture Pattern

The feasibility matrix reveals a governance coverage gradient:

1. **Deterministic**: All properties fillable (by construction)
2. **Hybrid ML + Rules**: Most partially fillable (ML boundaries opaque)
3. **Streaming**: Mix of partial and unfillable (velocity tradeoff)
4. **Agentic AI**: Opaque and unfillable dominate (structural breaks)
