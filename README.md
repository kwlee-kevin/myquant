# MyQuant

MyQuant is a stock data platform with a Django backend, a local bridge for Kiwoom ingestion, and a Next.js frontend.

## Documentation
Primary docs entry point:
- `docs/README.md`

Key docs:
- System overview: `docs/specs/system-overview.md`
- Specs index/template: `docs/specs/README.md`, `docs/specs/_template.md`
- Developer workflow: `docs/protocol/developer-workflow.md`
- Runbooks: `docs/runbooks/`

## Documentation Policy (Mandatory)
All code changes must keep documentation up to date.

Rules:
- Any feature change must update the relevant spec under `docs/specs/`.
- Any architectural or structural change must include a new ADR under `docs/adr/`.
- Any workflow/process change must update `docs/protocol/`.
- Pull Requests that modify code must also modify at least one documentation file when applicable.
- CI and review may reject PRs that introduce behavioral changes without corresponding documentation updates.

This repository follows a "docs-first or docs-with-code" development model to ensure long-term stability and AI-assisted repeatability.

CI Docs Gate:
- PRs with code-path changes must include docs changes, or use label `docs-not-needed` with justification in the PR description.

## Quick Commands
```bash
make tools
make ci
make coverage-check
```

## Bridge Sync (Dry-Run)
```bash
cd bridge
PYTHONPATH=src ./.venv/bin/python -m bridge.cli sync --dry-run --limit 20
```

## Environment
```bash
cp .env.example .env
# edit .env (local only)
```

Never commit `.env` or any secrets.
