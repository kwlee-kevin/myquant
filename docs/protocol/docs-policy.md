# Documentation Synchronization Policy

This repository enforces documentation updates alongside code changes.

## Core Principle
Code and documentation must evolve together.

## When Documentation Is Required

### 1. Environment or Configuration Changes
Trigger examples:
- `.env.example` modified
- New environment variables added
- Bridge config logic updated

Must update:
- `.env.example`
- `docs/runbooks/local-dev.md`
- Relevant runbooks

### 2. Bridge CLI or Sync Logic Changes
Trigger examples:
- `bridge/src/bridge/cli.py`
- `bridge/src/bridge/sync.py`

Must update:
- `docs/runbooks/bridge-sync.md`
- README examples if applicable

### 3. Backend Model / API / Schema Changes
Trigger examples:
- `backend/**/models.py`
- `serializers.py`, `views.py`, `urls.py`
- Migrations

Must update:
- Relevant spec in `docs/specs/`
- ADR if architectural decision is involved

### 4. CI / Quality Gate Changes
Trigger examples:
- `.github/workflows/**`
- `Makefile`
- `.pre-commit-config.yaml`

Must update:
- `docs/runbooks/ci.md`
- README command references

## CI Enforcement (Docs Gate)
Pull requests that modify code but do not modify documentation will fail CI unless labeled:

`docs-not-required`

Use this label only when:
- Change is purely internal refactor
- Change does not alter behavior, configuration, API, CLI, or workflow

Abuse of this label reduces system reliability.

## Team Workflow
- All PRs must pass `make ci`
- Documentation updates are reviewed like code
- Specs describe WHAT
- Runbooks describe HOW
- ADRs describe WHY
