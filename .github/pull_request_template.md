## Summary (What changed / Why)
- What changed (high level):
- Why (problem being solved):
- Impacted areas (backend / bridge / frontend / CI / docs):

## Linked Spec
Provide one of the following:
- Spec: `docs/specs/...`
- ADR (if any): `docs/adr/...`
- `N/A (reason)` for tiny changes only

Reference:
- Docs index: `docs/README.md`
- Spec guide: `docs/specs/README.md`
- Workflow/checklists: `docs/protocol/developer-workflow.md`, `docs/protocol/checklists.md`

## Spec-First Compliance (Required for features)
For new features:
- [ ] Spec PR was created first (`docs/specs/...`)
- [ ] This PR strictly implements the approved spec
- [ ] Spec was not modified in this implementation PR

If this is not a feature (e.g., fix/refactor), briefly explain:

---

## Type
- [ ] feat
- [ ] fix
- [ ] refactor
- [ ] docs
- [ ] test
- [ ] chore

## Test Evidence
Commands run:
```bash
# e.g.
# make lint
# make ci
```

Results:
```text
# paste key output lines
```

## Coverage Evidence
`make coverage-check` result:
```text
# paste backend/bridge coverage summary lines
```

## Documentation Sync (CI enforced)
- [ ] Relevant spec updated (`docs/specs/`)
- [ ] Relevant runbook updated (`docs/runbooks/`)
- [ ] README updated if entry-point commands changed
- [ ] ADR added if architectural decision changed
- [ ] docs-not-required label applied (only for pure refactor / internal change)

If using `docs-not-required`, explain why:

---

## Risk & Rollback Plan
- Risk level:
- Potential impact:
- Rollback steps:

## Notes (optional)
- Additional context for reviewers:
