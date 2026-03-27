# Architecture Types

The benchmark covers four decision system architecture types, each with distinct
governance evidence characteristics.

## 1. Deterministic Rule Engines

Full decision path enumerability via rule engines (e.g. OPA/Rego).

- **Governance coverage**: All Decision Event Schema properties fully fillable by construction
- **Primary collapse modality**: Coverage erosion (rules proliferate, evidence
  collection does not keep pace)
- **Cascade traces**: Not applicable (no probabilistic components)

## 2. Hybrid ML + Rules Systems

ML scores feed into rule-based decisions. The validated domain of the N4 framework.

- **Governance coverage**: `decision_context` partially fillable (ML features
  known, learned boundaries opaque)
- **Primary collapse modalities**: Metric erosion + ground truth delay
- **Cascade traces**: Yes -- feature incorrectness propagates through false
  negatives to untraceable decisions

## 3. Streaming Feature-Driven Systems

Real-time feature computation with high decision velocity.

- **Governance coverage**: `temporal_metadata` under pressure (latency vs
  completeness tradeoff)
- **Primary collapse modality**: Content staleness (features computed from
  stale data under load)
- **Cascade traces**: Not applicable

## 4. Agentic AI Systems

Multi-step autonomous decision chains with tool use. The novel contribution
of the benchmark.

- **Governance coverage**: Three structural breaks make standard framework
  properties insufficient
- **Structural breaks**:
  1. **Decision diffusion** -- no single decision point, instead a delegation tree
  2. **Evidence fragmentation** -- governance artifacts scattered across
     agent-local contexts
  3. **Responsibility ambiguity** -- accountability cannot flow through
     delegation chains
- **Primary collapse modality**: All modalities simultaneously
- **Cascade traces**: Yes -- all five stages compounded by structural breaks
