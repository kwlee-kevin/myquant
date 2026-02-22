# MyQuant-v2

## CI
GitHub Actions workflow: `.github/workflows/ci.yml`

Trigger:
- `push` to `main`
- `pull_request` targeting `main`

Jobs:
- `backend-tests`
  - `docker compose build backend`
  - `docker compose run --rm backend pytest -q`
- `bridge-tests` (Python 3.9)
  - create venv in `bridge/`
  - install `bridge/requirements.txt`
  - `PYTHONPATH=src ./.venv/bin/python -m pytest -q`

No secrets are required in CI. Dummy environment variables are provided for test runs.

## Run The Same Commands Locally
Backend:
```bash
docker compose build backend
docker compose run --rm backend pytest -q
```

Bridge:
```bash
cd bridge
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python -m pytest -q
```

## Bridge Tests
No Kiwoom secrets are required for unit tests.

```bash
cd bridge
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python -m pytest -q
```

## Dev Guardrails
- `.gitignore` blocks local/generated artifacts (`.DS_Store`, venv caches, `node_modules`, `.next`, logs, `.env`).
- `.env.example` stays tracked as the template.
- Pre-commit hooks enforce lightweight safety checks:
  - trailing whitespace / EOF normalization
  - merge conflict markers
  - private key detection
  - large file blocking
  - blocked path check (`.env`, `.DS_Store`, venv, `node_modules`, `.next`)

Install hooks:
```bash
python3 -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```
