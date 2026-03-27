# Governance Benchmark Dataset

![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)
![Version: v0.1.0](https://img.shields.io/badge/version-v0.1.0-blue)
![Python: 3.11-3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
[![CI](https://github.com/governance-evidence/governance-benchmark-dataset/actions/workflows/ci.yml/badge.svg)](https://github.com/governance-evidence/governance-benchmark-dataset/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19248723.svg)](https://doi.org/10.5281/zenodo.19248723)
[![License: Apache-2.0](https://img.shields.io/badge/code-Apache%202.0-green.svg)](LICENSE-CODE)
[![License: CC BY 4.0](https://img.shields.io/badge/dataset-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATASET)

Curated benchmark dataset and evaluation harness for comparing governance evidence
feasibility across four decision system architectures.

## Install

### From GitHub

Use this until the first package-index release, or when installing directly from source control:

```bash
pip install git+https://github.com/governance-evidence/governance-benchmark-dataset.git
```

Install the `parquet` extra when you need Parquet I/O helpers:

```bash
pip install "governance-benchmark-dataset[parquet] @ git+https://github.com/governance-evidence/governance-benchmark-dataset.git"
```

### From a Package Index

This will be available after the first package-index release:

```bash
pip install governance-benchmark-dataset
```

### For Contributors

Clone the repository, create a local virtual environment, and install development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Purpose

Answers: *"Does the N4 governance evidence framework generalize across decision
system architectures, and where does it structurally fail?"*

## Four Architecture Types

| Architecture | Collapse Modality | Cascade Traces |
| --- | --- | --- |
| Deterministic Rule Engines | Coverage erosion | No |
| Hybrid ML + Rules | Metric erosion, ground truth delay | Yes |
| Streaming Feature-Driven | Content staleness | No |
| Agentic AI | All modalities + 3 structural breaks | Yes |

## Quick Start

```bash
python examples/cross_architecture_comparison.py
```

## Table Helpers

The comparison helpers now distinguish between raw feasibility levels and
derived numeric score breakdowns:

- `generate_feasibility_level_table(matrices)` returns raw feasibility level
  values such as `fillable`, `partially_fillable`, `unfillable`, and `opaque`
- `generate_score_breakdown_table(comparison)` returns numeric per-property
  score values derived from the scoring rubric
- `generate_summary_table(comparison)` returns per-architecture overall,
  feasibility, cascade, and gap scores with ranking

The legacy `generate_feasibility_table(comparison)` function is still available
for backward compatibility, but it returns numeric score breakdown values rather
than raw feasibility levels. Prefer the explicit helper names above for new
code.

For an end-to-end example that loads scenarios, computes per-architecture
scores, and renders compact comparison tables, run:

```bash
python examples/cross_architecture_comparison.py
```

For the minimal single-scenario scoring flow, see:

```bash
python examples/load_and_score.py
```

## Dataset Structure

Each architecture type provides:

- **Scenario Records** -- documented decision events with Decision Event Schema events and
  governance assessments
- **Feasibility Matrix** -- per Decision Event Schema property: Fillable | Partially | Unfillable | Opaque
- **Cascade Traces** (hybrid + agentic only) -- how governance failures propagate
  through framework layers

## Development

```bash
make install    # pip install -e ".[dev]"
make check      # ruff lint + mypy strict + pytest 100% coverage
make format     # auto-fix lint + format
```

## License

- **Code** (`src/`, `tests/`, `examples/`): [Apache 2.0](LICENSE-CODE)
- **Dataset** (`dataset/`): [CC BY 4.0](LICENSE-DATASET)

## Related Projects

This benchmark is part of the [governance-evidence](https://github.com/governance-evidence) toolkit:

| Repository | Role | DOI |
|------------|------|-----|
| [decision-event-schema](https://github.com/governance-evidence/decision-event-schema) | Schema whose properties this benchmark scores | [10.5281/zenodo.18923178](https://doi.org/10.5281/zenodo.18923178) |
| [evidence-sufficiency-calc](https://github.com/governance-evidence/evidence-sufficiency-calc) | Sufficiency scoring used in benchmark evaluation | Pending |
| [governance-drift-toolkit](https://github.com/governance-evidence/governance-drift-toolkit) | Drift monitoring validated by benchmark scenarios | Pending |

## Citation

See [CITATION.cff](CITATION.cff) for citation metadata.
