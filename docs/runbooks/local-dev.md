# Runbook: Local Development

## Setup
```bash
cp .env.example .env
make tools
make precommit
```

## Daily Commands
```bash
make help
make ci
make coverage-check
```

## Bridge Dry-Run
```bash
cd bridge
PYTHONPATH=src ./.venv/bin/python -m bridge.cli sync --dry-run --limit 20
```
