.PHONY: install lint format test cov typecheck check clean

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/ examples/ scripts/
	ruff format --check src/ tests/ examples/ scripts/

format:
	ruff check --fix src/ tests/ examples/ scripts/
	ruff format src/ tests/ examples/ scripts/

typecheck:
	mypy src/

test:
	pytest --cov=benchmark --cov-report=term-missing

cov:
	pytest --cov=benchmark --cov-report=term-missing --cov-report=html

check: lint typecheck test

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .hypothesis .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
