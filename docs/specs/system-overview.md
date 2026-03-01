# System Overview

- Status: Approved
- Owner: MyQuant-v2
- Date: 2026-02-28

## Scope
This document describes the current end-to-end architecture for stock master sync and lookup.

## Components
- Backend (`backend/`): Django + DRF + PostgreSQL API and stock master persistence.
- Bridge (`bridge/`): local CLI that fetches Kiwoom data, normalizes it, and upserts backend stock master.
- Frontend (`frontend/`): Next.js App Router UI that server-fetches stock APIs.
- CI (`.github/workflows/ci.yml`): lint, backend/bridge tests, coverage artifacts + summary.

## Data Flow
1. Bridge authenticates to Kiwoom.
2. Bridge fetches market lists (`mrkt_tp` managed scope), normalizes fields.
3. Bridge posts normalized payload to backend internal upsert endpoint.
4. Backend upserts `stock_master` and exposes list/detail/stats APIs.
5. Frontend reads backend APIs for search/filter/detail UI.

## Stock Master Sync (Kiwoom -> Bridge -> Backend)
- Bridge maps:
  - `mrkt_tp` -> `market` (`KOSPI`, `KOSDAQ`, `KONEX`)
  - `marketCode` -> `security_type`
- Unmanaged markets are excluded at normalization stage.
- Upsert API is protected by `X-Bridge-Key`.

## Environment Variable Resolution
Bridge uses mode-based config:
- `KIWOOM_MODE=real|paper` (default: `paper`)
- mode-specific vars:
  - real: `KIWOOM_REAL_APP_KEY`, `KIWOOM_REAL_APP_SECRET`, `KIWOOM_REAL_HOST_URL`
  - paper: `KIWOOM_PAPER_APP_KEY`, `KIWOOM_PAPER_APP_SECRET`, `KIWOOM_PAPER_HOST_URL`

Bridge resolves these internally to canonical runtime values:
- `KIWOOM_APP_KEY`, `KIWOOM_APP_SECRET`, `KIWOOM_HOST_URL` (in-memory)

Env loading order:
1. Process environment
2. `bridge/.env` (optional)
3. Repo root `.env` (optional)

## Operational Gates
- Local:
  - `make ci`
  - `make coverage-check`
- CI publishes:
  - coverage XML artifacts
  - Actions Job Summary
  - PR sticky coverage comment
