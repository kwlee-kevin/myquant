# Development Checklists

## Feature Checklist
- Spec updated and acceptance criteria clear.
- DB constraints and indexes reviewed.
- API filters/pagination/ordering tested.
- SSR/network boundary considered for Docker execution.
- Error handling and timeout/retry behavior implemented.
- Unit/integration tests written and passing.
- Docs/runbook updated.

## Refactor Checklist
- Refactor scope isolated (no feature behavior mixing).
- Existing tests pass before refactor starts.
- New/updated tests validate unchanged behavior.
- Query/API performance checked for regressions.
- Any architectural tradeoff documented in ADR when needed.
- Rollback path identified.

## Release Checklist
- Target version and changelog entries prepared.
- Migration and compatibility impact reviewed.
- Test suites green (backend/bridge/frontend critical flows).
- Deployment and rollback commands validated.
- Monitoring/alerts reviewed for release window.
- Runbook links attached in release note.

## Incident Checklist
- Confirm incident scope, impact, and affected services.
- Stabilize first (mitigation/rollback/traffic guardrails).
- Capture timeline, logs, and failing requests/exit codes.
- Identify root cause and permanent fix.
- Add regression tests and runbook updates.
- Record postmortem action items and owners.
