# Scoring Rubric

The governance benchmark uses a weighted composite score to compare architectures.

## Three Components

### 1. Feasibility Score (default weight: 0.5)

Weighted average of Decision Event Schema property feasibility levels:

| Level | Score |
|---|---|
| Fillable | 1.0 |
| Partially Fillable | 0.5 |
| Unfillable | 0.1 |
| Opaque | 0.0 |

### 2. Cascade Score (default weight: 0.3)

Inverse of compounding cascade severity: `cascade_score = 1 - severity`.

For architectures without cascades (deterministic, streaming), the cascade
weight is redistributed to the feasibility component.

### 3. Gap Penalty (default weight: 0.2)

Measures absence of governance evidence:
`gap_score = 1 - (sum of gap severities / max possible gaps)`.

A score of 1.0 means no governance gaps were identified.

## Overall Score

```text
overall = w_feas * feasibility + w_casc * cascade + w_gap * gap_score
```

Weights must sum to 1.0. The default rubric (0.5 / 0.3 / 0.2) reflects the
primacy of evidence feasibility in governance assessment.
