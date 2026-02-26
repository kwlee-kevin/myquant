.PHONY: help lint test test-backend test-bridge ci format coverage

help:
	@echo "Available commands:"
	@echo "  make lint          - Run ruff lint + format check"
	@echo "  make format        - Auto-format code with ruff"
	@echo "  make test          - Run all tests (backend + bridge)"
	@echo "  make test-backend  - Run backend tests via docker"
	@echo "  make test-bridge   - Run bridge tests via venv"
	@echo "  make coverage      - Run backend + bridge tests with coverage XML output"
	@echo "  make ci            - Run lint + all tests (CI equivalent)"

lint:
	@command -v ruff >/dev/null 2>&1 || (echo "ruff not found. Run: make tools" && exit 1)
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

coverage:
	mkdir -p coverage
	docker compose run --rm \
		-v "$$PWD/coverage:/app/coverage" \
		backend pytest -q --cov=. \
			--cov-report=term-missing \
			--cov-report=xml:/app/coverage/backend-coverage.xml
	cd bridge && mkdir -p ../coverage && \
		PYTHONPATH=src ./.venv/bin/python -m pytest -q \
			--cov=src \
			--cov-report=term-missing \
			--cov-report=xml:../coverage/bridge-coverage.xml

ci: lint test

# --- Tooling ---------------------------------------------------------------

PIPX_BIN := $(HOME)/.local/bin
PY_USER_BIN := $(HOME)/Library/Python/3.9/bin
export PATH := $(PIPX_BIN):$(PY_USER_BIN):$(PATH)

.PHONY: tools precommit precommit-run

tools:
	@echo "==> Installing dev tools (pipx + ruff + pre-commit)"
	@python3 -m pip install -U pip pipx >/dev/null
	@python3 -m pipx ensurepath || true
	@python3 -m pipx install ruff || python3 -m pipx upgrade ruff
	@python3 -m pipx install pre-commit || python3 -m pipx upgrade pre-commit
	@echo ""
	@echo "==> If ruff/pre-commit still not found, restart terminal or run:"
	@echo "    export PATH=\"$(PIPX_BIN):$(PY_USER_BIN):$$PATH\""
	@echo ""
	@ruff --version
	@pre-commit --version

precommit:
	@echo "==> Installing git hooks (pre-commit)"
	@pre-commit install

precommit-run:
	@echo "==> Running pre-commit on all files"
	@pre-commit run -a
