# Cascade of Uncertainty Analysis

The cascade model shows how governance failures propagate through the N4
framework layers as a serial dependency chain.

## Five Stages

1. **Feature Incorrectness** (maps to Decision Event Specification)
   -- Input features are stale, incomplete, or incorrect
2. **False Negatives** (maps to Evidence Sufficiency)
   -- Incorrect features cause the system to miss events it should detect
3. **Untraceable Decisions** (maps to Label-Free Monitoring)
   -- Missed events produce decisions that cannot be reconstructed post-hoc
4. **Undetectable Degradation** (maps to SAC Diagnostic Theory)
   -- Monitoring signals fail to detect the declining quality
5. **Cumulative Losses** (maps to SAC Diagnostic Theory)
   -- Losses accumulate undetected until external signal arrives

## Compounding Severity

Each stage amplifies the severity of subsequent stages. The computation uses
a compounding factor (1.15) rather than simple summation:

```text
severity = sum(step_severity * factor^i) / sum(factor^i)
```

## Applicable Architectures

Cascade traces apply only to:

- **Hybrid ML + Rules**: Feature staleness propagates through ML scoring
  to untraceable decisions
- **Agentic AI**: All five stages compound, amplified by the three
  structural breaks (decision diffusion, evidence fragmentation,
  responsibility ambiguity)

Deterministic rule engines and streaming systems do not exhibit cascades
in the same sense -- their governance failures are more localized.
