# Runbook: Bridge Stock Sync

## Purpose
Operate and troubleshoot stock master sync (`Kiwoom -> Bridge -> Backend`).

## Required Env
Mode-based Kiwoom config:
- `KIWOOM_MODE=real|paper`
- `KIWOOM_REAL_APP_KEY`, `KIWOOM_REAL_APP_SECRET`, `KIWOOM_REAL_HOST_URL`
- `KIWOOM_PAPER_APP_KEY`, `KIWOOM_PAPER_APP_SECRET`, `KIWOOM_PAPER_HOST_URL`

Bridge/backend target:
- `BACKEND_API_BASE` (or `MYQUANT_BASE_URL`)
- `BRIDGE_API_KEY`

## Health Check
```bash
curl ${BACKEND_API_BASE:-http://localhost:8000}/health
```
Expected:
```json
{"status":"ok"}
```

## Commands
Dry-run:
```bash
cd bridge
PYTHONPATH=src ./.venv/bin/python -m bridge.cli sync --dry-run --limit 100 --verbose
```

Real sync:
```bash
cd bridge
PYTHONPATH=src ./.venv/bin/python -m bridge.cli sync --limit 100 --verbose
```

## Exit Codes
- `0`: success
- `1`: Kiwoom token/list fetch failure
- `2`: missing/invalid env configuration
- `3`: backend health check failed
- `4`: backend upsert failed
