# Stock Information Lookup System (KRX) - MVP Spec

## 1) Architecture
- **Bridge (local PC)**: Python bridge process connected to Kiwoom OpenAPI. Responsible for fetching KRX stock master data and calling backend internal upsert API.
- **Backend (Django REST Framework + Postgres)**: Source of truth for stock master records, query/filter/search APIs, validation, pagination, and internal authenticated upsert endpoint.
- **Frontend (Next.js)**: Uses backend public APIs for search/list/detail UI. No direct Kiwoom access.

Data flow:
1. Bridge fetches/normalizes KRX stock metadata from Kiwoom.
2. Bridge sends batched upsert payloads to backend `POST /api/internal/stocks:upsert`.
3. Backend stores/upserts in Postgres `stock_master`.
4. Frontend reads via `GET /api/stocks` and `GET /api/stocks/{code}`.

## 2) Security Constraints
- Kiwoom app key/account/session credentials must exist **only** on local bridge host (local PC).
- Backend and frontend must not store, log, or require Kiwoom secrets.
- Internal upsert API is protected by `X-Bridge-Key` shared secret (backend env var, bridge local config).
- `X-Bridge-Key` comparison must be constant-time.
- Reject unauthorized internal requests with `401`.
- Use HTTPS between bridge and backend when not on same trusted host.

## 3) Data Model (Postgres)
Table: `stock_master`

Fields:
- `code` `varchar(12)` PK (KRX short code; canonical uppercase string)
- `name_kr` `varchar(120)` NOT NULL
- `name_en` `varchar(120)` NULL
- `market` `varchar(16)` NOT NULL (`KOSPI` | `KOSDAQ` | `KONEX` | `ETF` | `ETN`)
- `category_l1` `varchar(64)` NULL (sector/industry top-level)
- `category_l2` `varchar(64)` NULL (optional sub-category)
- `is_active` `boolean` NOT NULL DEFAULT true
- `listed_date` `date` NULL
- `delisted_date` `date` NULL
- `updated_at` `timestamptz` NOT NULL DEFAULT now()
- `created_at` `timestamptz` NOT NULL DEFAULT now()

Indexes:
- PK on `code`
- `idx_stock_master_market` on (`market`)
- `idx_stock_master_category_l1` on (`category_l1`)
- `idx_stock_master_is_active` on (`is_active`)
- `idx_stock_master_updated_at_desc` on (`updated_at` DESC)
- `idx_stock_master_name_kr_trgm` GIN (`name_kr` gin_trgm_ops) for keyword search
- `idx_stock_master_name_en_trgm` GIN (`name_en` gin_trgm_ops) for keyword search

Notes:
- Enable extension: `pg_trgm`.
- Optional uniqueness guard: unique (`name_kr`, `market`, `code`) is redundant with PK; no extra unique needed for MVP.

## 4) API Contract

### `GET /api/stocks`
List/search endpoint.

Query params:
- `keywords` (string, optional): space-separated tokens. Example: `keywords=삼성 전자`.
- `op` (string, optional): `and` (default) or `or` for keyword token matching.
- `categories` (multi, optional): repeated param. Example: `categories=반도체&categories=자동차`.
- `markets` (multi, optional): repeated param. Example: `markets=KOSPI&markets=KOSDAQ`.
- `page` (int, optional, default `1`)
- `page_size` (int, optional, default `20`, max `100`)
- `ordering` (string, optional): one of `code`, `-code`, `name_kr`, `-name_kr`, `updated_at`, `-updated_at`.

Behavior:
- Keyword matching target fields: `code`, `name_kr`, `name_en`.
- `op=and`: all tokens must match at least one target field.
- `op=or`: any token match.
- If `categories` provided: filter where `category_l1 IN categories OR category_l2 IN categories`.
- If `markets` provided: filter `market IN markets`.

Response `200`:
```json
{
  "count": 1234,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "code": "005930",
      "name_kr": "삼성전자",
      "name_en": "Samsung Electronics",
      "market": "KOSPI",
      "category_l1": "반도체",
      "category_l2": null,
      "is_active": true,
      "updated_at": "2026-02-19T04:00:00Z"
    }
  ]
}
```

Errors:
- `400` invalid `op`, `ordering`, or pagination values.

### `GET /api/stocks/{code}`
Fetch one stock by exact code.

Path params:
- `code` (string, required)

Response `200`:
```json
{
  "code": "005930",
  "name_kr": "삼성전자",
  "name_en": "Samsung Electronics",
  "market": "KOSPI",
  "category_l1": "반도체",
  "category_l2": null,
  "is_active": true,
  "listed_date": "1975-06-11",
  "delisted_date": null,
  "created_at": "2026-02-19T03:50:00Z",
  "updated_at": "2026-02-19T04:00:00Z"
}
```

Errors:
- `404` when not found.

### `POST /api/internal/stocks:upsert`
Internal endpoint for bridge ingestion only.

Headers:
- `X-Bridge-Key: <shared-secret>` (required)

Request body:
```json
{
  "items": [
    {
      "code": "005930",
      "name_kr": "삼성전자",
      "name_en": "Samsung Electronics",
      "market": "KOSPI",
      "category_l1": "반도체",
      "category_l2": null,
      "is_active": true,
      "listed_date": "1975-06-11",
      "delisted_date": null
    }
  ]
}
```

Behavior:
- Upsert key: `code`.
- Existing row: update mutable fields + `updated_at=now()`.
- New row: insert with `created_at`, `updated_at`.
- Process is atomic per request (single DB transaction).

Response `200`:
```json
{
  "received": 1,
  "inserted": 0,
  "updated": 1
}
```

Errors:
- `401` missing/invalid `X-Bridge-Key`.
- `400` invalid payload schema.

## 5) Acceptance Criteria
Unit tests (backend):
- `GET /api/stocks` keyword logic validates `op=and` vs `op=or`.
- Category/market multi-filter works with repeated query params.
- Pagination and ordering validation (`400` on invalid).
- `GET /api/stocks/{code}` returns `200` or `404` as expected.
- `POST /api/internal/stocks:upsert`:
  - rejects without valid `X-Bridge-Key` (`401`)
  - inserts new records
  - updates existing records by `code`
  - returns accurate `received/inserted/updated` counts

Basic E2E:
1. Start backend + DB + frontend.
2. Call internal upsert with 3 sample stocks via bridge key.
3. Open frontend list page; confirm 3 stocks visible.
4. Search by keyword with `op=and` and `op=or`; verify result difference.
5. Filter by `markets` and `categories`; verify subset.
6. Open stock detail page by code; verify fields.
