# Runbook: CI

## Workflow
- File: `.github/workflows/ci.yml`
- Triggers: `push`/`pull_request` on `main`

## What Runs
- Ruff lint/format check
- Backend tests via Docker
- Bridge tests via venv
- Coverage XML generation + artifacts + summary

## Local Repro
```bash
make ci
make coverage-check
```

## Failure Triage
1. Re-run local commands.
2. Fix lint/test failures first.
3. Check coverage summary and artifacts in Actions.
