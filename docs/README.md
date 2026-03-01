# Documentation Index

Use this directory as the single source of truth for product, technical, and workflow documentation.

## Structure
- `docs/specs/`: feature and implementation specs.
- `docs/adr/`: architecture decision records.
- `docs/runbooks/`: operational guides (local dev, CI, release, sync operations).
- `docs/protocol/`: development protocol, checklists, and AI-assisted workflow guidance.

## Start Here
- System overview: `docs/specs/system-overview.md`
- Spec template: `docs/specs/_template.md`
- Specs index: `docs/specs/README.md`
- ADR template: `docs/adr/_template.md`
- Developer workflow: `docs/protocol/developer-workflow.md`
- PR checklist: `docs/protocol/checklists.md`
- Bridge operations: `docs/runbooks/bridge-sync.md`

## Typical Flow
1. Draft/update spec in `docs/specs/`.
2. Implement changes and tests.
3. Run local gates (`make ci`, `make coverage-check`).
4. Open PR using `.github/pull_request_template.md` and link spec/ADR.
