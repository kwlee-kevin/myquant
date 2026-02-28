# Specs Index

Use a spec-lite doc for changes that are likely to affect behavior, contracts, or operations.

## When to write a spec
- Any user-facing feature.
- Any data model change (schema/index/migration).
- Any API contract change.
- Any non-trivial refactor.
- Any infra/CI change that affects reliability or developer workflow.

Small fixes can use `N/A` in the PR template, with a short reason.

## Naming convention
- Recommended filename: `YYYY-MM-DD-short-title.md`
- Example: `2026-02-28-stock-sync-hardening.md`

## Approval model (solo dev)
- `Approved` means:
1. PR description links the spec.
2. Tests and required checks pass.

## PR link format example
- `Spec: docs/specs/2026-02-28-stock-sync-hardening.md`
- `ADR: docs/adr/2026-02-28-backend-health-check.md`
