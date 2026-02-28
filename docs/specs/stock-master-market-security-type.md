# Stock Master Market + Security Type

- Status: Approved
- Owner: MyQuant-v2
- Date: 2026-02-28

## Problem / Context
Stock master currently stores market only and mixes managed/unmanaged market scopes. We need explicit market scope management and security type classification for reliable filtering and UI display.

## Goals (In-scope)
- Manage market with explicit scope: `KOSPI`, `KOSDAQ`, `KONEX` only.
- Add security type classification from Kiwoom `marketCode`.
- Exclude unmanaged markets from bridge normalization payload.
- Expose and filter by `market` and `security_type` in backend list API.
- Show and filter by these fields in frontend stock list UI.

## Non-goals (Out-of-scope)
- Expanding managed market scope beyond `mrkt_tp` `0/10/50`.
- Changing backend upsert endpoint contract shape beyond additive fields.

## Mapping Rules
### Market (`mrkt_tp`)
- `0` -> `KOSPI`
- `10` -> `KOSDAQ`
- `50` -> `KONEX`
- others -> excluded (not normalized, not upserted)

### Security Type (`marketCode`)
- `60` -> `ETN`
- `70` -> `ETN_LOSS_LIMIT`
- `80` -> `GOLD_SPOT`
- `90` -> `ETN_VOLATILITY`
- `2` -> `INFRA_FUND`
- `3` -> `ELW`
- `4` -> `MUTUAL_FUND`
- `5` -> `WARRANT`
- `6` -> `REIT`
- `7` -> `WARRANT_CERT`
- `8` -> `ETF`
- `9` -> `HIGH_YIELD_FUND`
- otherwise -> `COMMON_STOCK`

## Backend/API Changes
- `stock_master` fields:
  - `market` (choices: `KOSPI/KOSDAQ/KONEX`)
  - `security_type` (choices above, indexed)
  - optional raw fields: `mrkt_tp_raw`, `market_code_raw`
- `GET /api/stocks` supports repeated params:
  - `markets=...`
  - `security_types=...`
- List/detail serializers include `security_type` (and raw fields in detail).

## Bridge Changes
- Normalize items with:
  - `market`, `security_type`, `mrkt_tp_raw`, `market_code_raw`
- Filter out unmanaged markets during normalization.
- Keep payload shape additive for backend upsert.

## Frontend Changes
- Stock list table adds `security_type` column.
- Filter UI adds `security_type` multi-select checkboxes.
- Query params include repeated `security_types`.
- Detail page shows `security_type` and raw code fields.

## Risks & Mitigations
- Risk: Legacy records with unmanaged market values may conflict with model choices.
  - Mitigation: bridge only sends managed values; migration defaults `security_type`.
- Risk: API/UI mismatch for new filter key.
  - Mitigation: backend and frontend both standardize on `security_types`.

## Test Plan
- Backend:
  - list filtering by repeated `security_types`
  - upsert still supports insert/update/unchanged metrics with new fields
- Bridge:
  - mapping tests for market/security type
  - normalization excludes unmanaged market
- Existing `make ci` and `make coverage-check` remain green.
