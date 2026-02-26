.PHONY: help lint test test-backend test-bridge ci format

help:
	@echo "Available commands:"
	@echo "  make lint          - Run ruff lint + format check"
	@echo "  make format        - Auto-format code with ruff"
	@echo "  make test          - Run all tests (backend + bridge)"
	@echo "  make test-backend  - Run backend tests via docker"
	@echo "  make test-bridge   - Run bridge tests via venv"
	@echo "  make ci            - Run lint + all tests (CI equivalent)"

lint:
	ruff check .
	ruff format --check .

format:
	ruff check . --fix
	ruff format .

test: test-backend test-bridge

test-backend:
	docker compose run --rm backend pytest -q

test-bridge:
	cd bridge && PYTHONPATH=src ./.venv/bin/python -m pytest -q

ci: lint test
