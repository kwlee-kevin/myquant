# Developer Workflow

## Branching
Use short topic branches from `main`:
- `feat/<topic>`
- `fix/<topic>`
- `refactor/<topic>`
- `docs/<topic>`
- `test/<topic>`
- `chore/<topic>`

## Required Local Gates
```bash
git checkout main && git pull
git checkout -b <type>/<topic>
make lint
make ci
make coverage-check
```

## PR Process
1. Link one of: `docs/specs/...`, `docs/adr/...`, or `N/A (reason)`.
2. Fill `.github/pull_request_template.md`.
3. Ensure required checks pass.
4. Verify coverage summary (Job Summary + sticky PR comment).
5. Merge only after review/approval.

## Docs Gate (CI enforcement)
- On pull requests, CI checks changed paths.
- If PR changes code paths (`backend/`, `bridge/`, `frontend/`, `scripts/`, `.github/workflows/`) and does not change docs paths (`docs/`, `README.md`, `.github/pull_request_template.md`), CI fails.
- Exemption: add label `docs-not-needed` and include justification in PR description.

## Coverage Policy
Current thresholds (enforced by `make coverage-check`):
- backend: >= 85%
- bridge: >= 55%

## Pre-commit Expectations
```bash
make tools
make precommit
make precommit-run
```

## Codex Usage Guardrails
### Do
- Keep changes scoped to requested goal.
- Update specs/docs when behavior, API, or operations change.
- Add or update tests with implementation changes.
- Run local gates before proposing merge.

### Do Not
- Commit secrets (`.env`, credentials, tokens).
- Mix unrelated refactors/features in one PR.
- Bypass failing checks.
- Change CI behavior without documenting impact in specs/protocol.
