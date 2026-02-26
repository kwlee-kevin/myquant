SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: help lint format test test-backend test-bridge ci coverage coverage-check tools precommit precommit-run

BACKEND_COV_MIN ?= 85
BRIDGE_COV_MIN ?= 55

# --- Paths / tooling -------------------------------------------------------

PIPX_DIR ?= $(HOME)/.local/bin
PY_USER_BIN ?= $(HOME)/Library/Python/3.9/bin

# Prefer installed binaries; fallback to `python3 -m pipx run ...` (no PATH dependency)
define RUN_RUFF
	if command -v ruff >/dev/null 2>&1; then \
		ruff $(1); \
	else \
		python3 -m pipx run ruff $(1); \
	fi
endef

define RUN_PRECOMMIT
	if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit $(1); \
	else \
		python3 -m pipx run pre-commit $(1); \
	fi
endef

help:
	@echo "Available commands:"
	@echo "  make tools         - Install dev tools (pipx, ruff, pre-commit)"
	@echo "  make lint          - Run ruff lint + format check"
	@echo "  make format        - Auto-format code with ruff"
	@echo "  make test          - Run all tests (backend + bridge)"
	@echo "  make test-backend  - Run backend tests via docker"
	@echo "  make test-bridge   - Run bridge tests via venv (auto-creates venv + installs deps)"
	@echo "  make coverage      - Run backend + bridge tests with coverage XML output"
	@echo "  make coverage-check - Enforce coverage thresholds (backend=$(BACKEND_COV_MIN), bridge=$(BRIDGE_COV_MIN))"
	@echo "  make ci            - Run lint + all tests (CI equivalent)"
	@echo "  make precommit     - Install pre-commit git hook"
	@echo "  make precommit-run - Run pre-commit on all files"

# --- Lint/format -----------------------------------------------------------

lint:
	@$(call RUN_RUFF,check .)
	@$(call RUN_RUFF,format --check .)

format:
	@$(call RUN_RUFF,check . --fix)
	@$(call RUN_RUFF,format .)

# --- Tests -----------------------------------------------------------------

test: test-backend test-bridge

test-backend:
	docker compose run --rm backend pytest -q

test-bridge:
	cd bridge && \
		[ -x ./.venv/bin/python ] || python3 -m venv .venv && \
		./.venv/bin/python -m pip install -U pip >/dev/null && \
		./.venv/bin/python -m pip install -r requirements.txt >/dev/null && \
		PYTHONPATH=src ./.venv/bin/python -m pytest -q

# --- Coverage --------------------------------------------------------------

coverage:
	mkdir -p coverage
	docker compose run --rm \
		-v "$$PWD/coverage:/app/coverage" \
		backend pytest -q --cov=. \
			--cov-report=term-missing \
			--cov-report=xml:/app/coverage/backend-coverage.xml
	cd bridge && mkdir -p ../coverage && \
		[ -x ./.venv/bin/python ] || python3 -m venv .venv && \
		./.venv/bin/python -m pip install -U pip >/dev/null && \
		./.venv/bin/python -m pip install -r requirements.txt >/dev/null && \
		PYTHONPATH=src ./.venv/bin/python -m pytest -q \
			--cov=src \
			--cov-report=term-missing \
			--cov-report=xml:../coverage/bridge-coverage.xml

coverage-check: coverage
	@BACKEND_COV_MIN=$(BACKEND_COV_MIN) BRIDGE_COV_MIN=$(BRIDGE_COV_MIN) \
		python3 -c "import os,sys,xml.etree.ElementTree as ET; b=float(ET.parse('coverage/backend-coverage.xml').getroot().attrib.get('line-rate','0'))*100.0; r=float(ET.parse('coverage/bridge-coverage.xml').getroot().attrib.get('line-rate','0'))*100.0; bm=float(os.getenv('BACKEND_COV_MIN','85')); rm=float(os.getenv('BRIDGE_COV_MIN','55')); verdict=lambda v,m:'OK' if v>=m else 'FAIL'; print('backend: %.2f%% (min %.2f%%) -> %s' % (b,bm,verdict(b,bm))); print('bridge:  %.2f%% (min %.2f%%) -> %s' % (r,rm,verdict(r,rm))); sys.exit(0 if (b>=bm and r>=rm) else 1)"

ci: lint test

# --- Tooling ---------------------------------------------------------------

tools:
	@echo "==> Installing dev tools (pipx + ruff + pre-commit)"
	@python3 -m pip install -U pip pipx >/dev/null
	@python3 -m pipx ensurepath >/dev/null 2>&1 || true
	@python3 -m pipx install ruff >/dev/null 2>&1 || python3 -m pipx upgrade ruff >/dev/null
	@python3 -m pipx install pre-commit >/dev/null 2>&1 || python3 -m pipx upgrade pre-commit >/dev/null
	@echo ""
	@echo "==> If you want binaries on PATH in interactive shell:"
	@echo "    export PATH=\"$(PIPX_DIR):$(PY_USER_BIN):$$PATH\""
	@echo ""
	@echo "==> Tool versions (fallback-safe):"
	@$(call RUN_RUFF,--version)
	@$(call RUN_PRECOMMIT,--version)

precommit:
	@echo "==> Installing git hooks (pre-commit)"
	@$(call RUN_PRECOMMIT,install)

precommit-run:
	@echo "==> Running pre-commit on all files"
	@$(call RUN_PRECOMMIT,run -a)
