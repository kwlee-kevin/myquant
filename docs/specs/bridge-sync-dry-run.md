# Bridge Sync Dry-Run

- Status: Approved
- Owner: MyQuant-v2
- Date: 2026-02-28

## Problem / Context
Bridge sync currently supports stock sync execution, but dry-run behavior should be explicit, testable, and safe for repeated validation without backend writes.

## Goals (In-scope)
- Support `bridge sync --dry-run` CLI flow.
- Perform fetch + normalization + mapping in dry-run.
- Produce deterministic change summary output.
- Guarantee no backend write path is executed in dry-run.

## Non-goals (Out-of-scope)
- Changing Kiwoom API behavior.
- Changing backend upsert contract.
- Adding new dependencies or new persistence paths.

## User Stories / Use Cases
- As a developer, I want to preview normalized records and summary stats before syncing.
- As an operator, I want a safe command that never writes to backend in dry-run mode.

## Proposed Solution (High-level)
- Add `sync` command alias in bridge CLI while keeping `sync-stocks` compatibility.
- Add pure function `compute_change_summary()` in `bridge.sync`.
- In dry-run mode:
  - print total + `change_summary=...` JSON + first 3 normalized items.
  - skip backend health check and backend upsert.

## API/Interface Changes (if any)
- CLI command additions:
  - `bridge sync --dry-run [--limit N] [--verbose]`
  - Existing `sync-stocks` remains supported.

## Data model / migrations (if any)
- None.

## Risks & Mitigations
- Risk: behavior regressions in existing sync output.
  Mitigation: preserve existing summary line format and add targeted tests.
- Risk: accidental backend write in dry-run.
  Mitigation: explicit branching + tests that fail on backend write path calls.

## Test Plan (unit/integration) + Coverage expectation
- Unit tests:
  - CLI parsing/dispatch for `sync` and `sync-stocks`.
  - `compute_change_summary()` deterministic counts.
  - Dry-run path skips backend write methods.
- Coverage expectation:
  - Bridge coverage stays at or above current threshold and improves with added tests.

## Rollout / Backward compatibility
- Backward compatible:
  - Existing `sync-stocks` command remains valid.
  - No backend/API contract changes.

## Open Questions
- None.
