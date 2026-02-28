# MyQuant

Data-driven quantitative investment platform.

---

# 🚀 Project Overview

MyQuant is a structured quantitative investment research platform consisting of:

- **Backend (Django + PostgreSQL)**
- **Bridge (Kiwoom API sync layer)**
- **Frontend (Next.js)**
- **Docker-based local development**
- **CI (GitHub Actions)**

The repository enforces automated testing, linting, and guardrails to ensure reliability and long-term maintainability.

---

# 🧪 Continuous Integration (CI)

GitHub Actions workflow:

```
.github/workflows/ci.yml
```

### Triggers

- `push` to `main`
- `pull_request` targeting `main`

### Jobs

#### 1️⃣ backend-tests

```bash
docker compose build backend
docker compose run --rm backend pytest -q
```

#### 2️⃣ bridge-tests (Python 3.9)

```bash
cd bridge
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python -m pytest -q
```

No production secrets are required for CI. Dummy values are used for test execution.

---

# 🛠 Local Development

## Run Backend Tests

```bash
docker compose build backend
docker compose run --rm backend pytest -q
```

## Run Bridge Tests

```bash
cd bridge
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python -m pytest -q
```

## Coverage
Generate backend + bridge coverage reports locally:

```bash
make coverage
```

Coverage XML files are written to host path:
- `./coverage/backend-coverage.xml`
- `./coverage/bridge-coverage.xml`
- CI publishes backend/bridge coverage totals in the GitHub Actions Job Summary.
- CI also uploads coverage XML files as workflow artifacts.
- On pull requests, CI posts/updates a sticky coverage summary comment.

Optional threshold check:

```bash
make coverage-check
```

Default thresholds:
- backend: `85%`
- bridge: `55%`

---

# 🔁 Development Protocol

## Branch Naming
Use one of:
- `feat/<short-topic>`
- `fix/<short-topic>`
- `chore/<short-topic>`
- `test/<short-topic>`
- `docs/<short-topic>`

## Standard Local Workflow
```bash
git checkout main && git pull
git checkout -b <branch>
make lint
make ci
make coverage-check
```

## PR Workflow
1. Push branch.
2. Open pull request.
3. Wait for required checks.
4. Review coverage summary comment on the PR.
5. Merge after approvals and green checks.

## Repository Protection Rules
- `main` is protected.
- Pull requests are required for merge.
- Required checks must pass before merge.

## Pre-commit Usage
```bash
make tools
make precommit
make precommit-run
```

---

# 🧹 Linting & Formatting

We use **ruff** for linting and formatting.

### Auto-fix

```bash
ruff check . --fix
ruff format .
```

### Check only (CI equivalent)

```bash
ruff check .
ruff format --check .
```

---

# 📦 Standardized Dev Commands

The project includes a Makefile to unify developer workflow.

### Run lint

```bash
make lint
```

### Run format

```bash
make format
```

### Run all tests

```bash
make test
```

### Run full CI locally

```bash
make ci
```

## Quick start (recommended)

```bash
make tools
make precommit
make ci
```

---

# 🔐 Dev Guardrails

The repository enforces safety rules via:

### `.gitignore`
Blocks:
- `.DS_Store`
- `.env`
- virtual environments
- `node_modules`
- `.next`
- logs

`.env.example` remains tracked as a template.

### Pre-commit Hooks

Enforced checks:
- trailing whitespace / EOF normalization
- merge conflict markers
- private key detection
- large file blocking
- blocked path protection
- ruff linting

Install locally:

```bash
python3 -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

# 🏗 Architecture Summary

```
MyQuant
 ├── backend (Django API)
 ├── bridge (Kiwoom sync layer)
 ├── frontend (Next.js UI)
 ├── docker-compose.yml
 └── .github/workflows
```

---

# 📌 Engineering Principles

- CI must pass before merge
- Tests protect critical logic
- Lint must pass
- PR-based workflow
- No secrets in repository

---

# 🔮 Next Improvements

Planned improvements:

- Test coverage reporting
- Type safety (mypy)
- Version tagging strategy
- Release notes automation
- ADR documentation structure

---

# License

MIT (to be finalized)
