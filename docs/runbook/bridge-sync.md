# Bridge Sync Runbook

## Purpose
Operate and troubleshoot bridge stock sync (Kiwoom -> backend upsert) safely.

## Environment Validation
Required env vars:
- `KIWOOM_BASE_URL`
- `KIWOOM_APP_KEY`
- `KIWOOM_APP_SECRET`
- `BACKEND_API_BASE` (default `http://localhost:8000`)
- `BRIDGE_API_KEY`

Quick check:
```bash
env | grep -E 'KIWOOM_|BACKEND_API_BASE|BRIDGE_API_KEY'
```

## Backend Health Check
```bash
curl ${BACKEND_API_BASE:-http://localhost:8000}/health
```
Expected:
```json
{"status":"ok"}
```

## Common Failures
- Missing Kiwoom credentials
  - Symptom: exit code `2`
  - Action: validate `KIWOOM_APP_KEY` and `KIWOOM_APP_SECRET`.

- Token/list fetch failure
  - Symptom: exit code `1`
  - Action: verify Kiwoom base URL, credentials, network, and API availability.

- Backend health failure
  - Symptom: exit code `3`
  - Action: start stack and recheck `/health`.

- Backend upsert failure
  - Symptom: exit code `4`
  - Action: inspect backend logs and API/internal auth key.

## Exit Codes
- `0`: success
- `1`: Kiwoom token/list fetch failure
- `2`: missing required env input
- `3`: backend health check failed
- `4`: backend upsert request failed

## Retry Behavior
Bridge uses retry with backoff for token/list requests:
- total retries: 3
- backoff factor: 0.5
- retriable statuses: 429, 500, 502, 503, 504

## Debug Commands
Dry-run with verbose quality summary:
```bash
cd bridge
PYTHONPATH=src python -m bridge.cli sync-stocks --dry-run --limit 100 --verbose
```

Real sync with verbose:
```bash
cd bridge
PYTHONPATH=src python -m bridge.cli sync-stocks --limit 100 --verbose
```

Backend tests:
```bash
docker compose exec backend pytest -q
```

Bridge tests:
```bash
cd bridge
PYTHONPATH=src python -m pytest -q tests
```
