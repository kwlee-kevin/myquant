# Bridge (Kiwoom -> Backend Upsert)

## Required Environment Variables
- `KIWOOM_BASE_URL`
- `KIWOOM_APP_KEY`
- `KIWOOM_APP_SECRET`
- `BACKEND_API_BASE` (optional, default: `http://localhost:8000`)
- `BRIDGE_API_KEY`

## Market Mapping (mrkt_tp -> backend market)
- `0` -> `KOSPI`
- `10` -> `KOSDAQ`
- `50` -> `KONEX`
- `8` -> `ETF`
- `3, 5, 4, 6, 9` and all other values -> `ETN`

## Install
```bash
cd bridge
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
pytest -q
```

Fallback (if editable install is not available in your environment):
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install pytest pytest-mock requests python-dotenv "urllib3<2"
PYTHONPATH=src python -m pytest -q
```

## Run
Bring up backend stack first:
```bash
cd ..
docker compose up -d
curl http://localhost:8000/health
```

Dry run (fetch + normalize only, no backend upsert):
```bash
cd bridge
python -m bridge.cli sync-stocks --dry-run
```

Dry run with limit:
```bash
python -m bridge.cli sync-stocks --dry-run --limit 100
```

Dry run alias (`--no-push`):
```bash
python -m bridge.cli sync-stocks --no-push --limit 100
```

Dry run with verbose logs:
```bash
python -m bridge.cli sync-stocks --dry-run --limit 100 --verbose
```

Real sync (upsert to backend):
```bash
python -m bridge.cli sync-stocks
```

Real sync with limit:
```bash
python -m bridge.cli sync-stocks --limit 100
```

Real sync with verbose logs:
```bash
python -m bridge.cli sync-stocks --limit 100 --verbose
```
