# Contributing

Contributions are welcome. This document covers the development workflow.

## Setup

```bash
git clone https://github.com/solozobov/governance-benchmark-dataset.git
cd governance-benchmark-dataset
python -m venv .venv && source .venv/bin/activate
make install          # pip install -e ".[dev]"
pre-commit install    # enable pre-commit hooks
```

## Development workflow

1. Create a working branch
2. Make changes
3. Run `make check` (ruff + mypy strict + pytest with 100% coverage)
4. Commit -- pre-commit hooks enforce all quality gates automatically
5. Open a pull request

## Quality requirements

- **100% test coverage** -- every line, every branch. No exceptions.
- **mypy strict** -- full type annotations on all source code
- **ruff** -- 23 rule categories enforced (see `pyproject.toml`)
- **No `type: ignore`** in source code unless the third-party library is untyped
- **Frozen dataclasses** for all value types
- **NumPy-style docstrings** on all public functions

## Running checks

```bash
make check      # lint + typecheck + test (sequential)
make lint       # ruff check + format
make typecheck  # mypy strict
make test       # pytest with coverage
make format     # auto-fix lint + format
```

## Project structure

- `src/benchmark/` -- package source
- `tests/` -- pytest test suite
- `dataset/` -- benchmark data (JSON, schemas)
- `examples/` -- runnable usage examples
- `docs/` -- supplementary documentation

## Dual license

- Code (`src/`, `tests/`, `examples/`, `scripts/`): Apache 2.0
- Dataset (`dataset/`): CC BY 4.0
