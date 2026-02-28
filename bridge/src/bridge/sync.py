from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MARKET_TYPES = ["0", "10", "50", "8", "3", "5", "4", "6", "9"]


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    load_dotenv()


def _create_retry_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "POST"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _safe_response_snippet(response: requests.Response, limit: int = 500) -> str:
    try:
        text = (response.text or "").strip()
    except Exception:
        text = ""
    return text[:limit]


def _map_market(mrkt_tp: str) -> str:
    if mrkt_tp == "0":
        return "KOSPI"
    if mrkt_tp == "10":
        return "KOSDAQ"
    if mrkt_tp == "50":
        return "KONEX"
    if mrkt_tp == "8":
        return "ETF"
    return "ETN"


def _normalize_ka10099_item(raw: dict[str, Any], mrkt_tp: str) -> dict[str, Any] | None:
    code = str(raw.get("code") or raw.get("stk_cd") or "").strip().upper()
    name_kr = str(raw.get("name") or raw.get("stk_nm") or "").strip()
    if not code or not name_kr:
        return None

    reg_day = str(raw.get("regDay") or "").strip()
    listed_date = None
    if reg_day:
        try:
            listed_date = datetime.strptime(reg_day, "%Y%m%d").date().isoformat()
        except ValueError:
            listed_date = None

    category_l1 = str(raw.get("upName") or "").strip() or None
    category_l2 = str(raw.get("companyClassName") or "").strip() or None

    return {
        "code": code,
        "name_kr": name_kr,
        "name_en": None,
        "market": _map_market(mrkt_tp),
        "category_l1": category_l1,
        "category_l2": category_l2,
        "is_active": True,
        "listed_date": listed_date,
        "delisted_date": None,
    }


def _normalize_and_dedup(
    records_by_market: list[tuple[str, list[dict[str, Any]]]],
) -> list[dict[str, Any]]:
    by_code: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for mrkt_tp, records in records_by_market:
        for raw in records:
            normalized = _normalize_ka10099_item(raw, mrkt_tp)
            if normalized is None:
                continue
            code = normalized["code"]
            if code in by_code:
                continue
            by_code[code] = normalized
            order.append(code)

    return [by_code[code] for code in order]


def _post_json(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    response = session.post(url, headers=headers, json=body, timeout=timeout)
    if not response.ok:
        snippet = _safe_response_snippet(response)
        raise requests.HTTPError(
            f"HTTP error status={response.status_code} url={url} body={snippet}",
            response=response,
        )
    data = response.json()
    if not isinstance(data, dict):
        return {}
    return data


def _fetch_token(
    session: requests.Session,
    base_url: str,
    app_key: str,
    app_secret: str,
) -> tuple[str, str]:
    """Fetch Kiwoom REST access token.

    Kiwoom may return different field names depending on environment/version.
    - Success fields: token_type + token (sometimes access_token)
    - Failure fields: return_code / return_msg

    Raise RuntimeError with useful context (no secrets).
    """
    token_url = f"{base_url.rstrip('/')}/oauth2/token"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "api-id": "au10001",
    }
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "secretkey": app_secret,
    }

    resp = session.post(token_url, headers=headers, json=body, timeout=10)
    try:
        data = resp.json()
    except Exception:
        data = {"_non_json_body": (resp.text or "").strip()[:500]}

    if resp.status_code < 200 or resp.status_code >= 300:
        snippet = _safe_response_snippet(resp)
        raise RuntimeError(
            f"Kiwoom token HTTP error: status={resp.status_code} keys={list(data.keys())} body={snippet}"
        )

    token_type = data.get("token_type") or data.get("tokenType") or "Bearer"
    token = data.get("token") or data.get("access_token") or data.get("accessToken")

    if not token:
        rc = data.get("return_code") or data.get("returnCode") or data.get("code")
        rm = data.get("return_msg") or data.get("returnMsg") or data.get("message")
        raise RuntimeError(
            "Kiwoom token response missing token field. "
            f"status={resp.status_code} return_code={rc} return_msg={rm} keys={list(data.keys())}"
        )

    token_type = str(token_type).strip() or "Bearer"
    token = str(token).strip()
    return token_type, token


def _fetch_market_list(
    session: requests.Session,
    base_url: str,
    token_type: str,
    token: str,
    mrkt_tp: str,
) -> list[dict[str, Any]]:
    list_url = f"{base_url.rstrip('/')}/api/dostk/stkinfo"
    list_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "api-id": "ka10099",
        "authorization": f"{token_type} {token}",
    }
    list_body = {"mrkt_tp": mrkt_tp}
    data = _post_json(session, list_url, list_headers, list_body, timeout=20)

    raw_list = data.get("list")
    if isinstance(raw_list, list):
        return [item for item in raw_list if isinstance(item, dict)]

    for key in ["items", "data", "output", "stkinfo"]:
        candidate = data.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]

    for value in data.values():
        if isinstance(value, list):
            dict_items = [item for item in value if isinstance(item, dict)]
            if dict_items:
                return dict_items

    return []


def _check_backend_health(backend_api_base: str) -> bool:
    health_url = f"{backend_api_base}/health"
    try:
        health_resp = requests.get(health_url, timeout=2)
        if health_resp.status_code != 200:
            return False
        health_data = health_resp.json()
        return isinstance(health_data, dict) and health_data.get("status") == "ok"
    except (requests.ConnectionError, requests.Timeout, ValueError):
        return False


def compute_change_summary(
    *,
    fetched_markets: int,
    raw_count_total: int,
    normalized_items: list[dict[str, Any]],
    selected_items: list[dict[str, Any]],
    dry_run: bool,
    push_result: str | dict[str, Any],
) -> dict[str, Any]:
    normalized_unique = len(normalized_items)
    listed_date_parsed = sum(1 for item in normalized_items if item.get("listed_date") is not None)
    category_l1_missing = sum(1 for item in normalized_items if item.get("category_l1") is None)
    per_market_counts: dict[str, int] = {}
    for item in normalized_items:
        market = str(item.get("market", "UNKNOWN"))
        per_market_counts[market] = per_market_counts.get(market, 0) + 1

    return {
        "fetched_markets": fetched_markets,
        "raw_count_total": raw_count_total,
        "normalized_unique": normalized_unique,
        "limited_to": len(selected_items),
        "dry_run": dry_run,
        "push_result": push_result,
        "quality": {
            "listed_date_parsed": f"{listed_date_parsed}/{normalized_unique}",
            "category_l1_missing": f"{category_l1_missing}/{normalized_unique}",
            "per_market_counts": per_market_counts,
        },
    }


def sync_stocks(dry_run: bool, limit: int | None, verbose: bool = False) -> int:
    raw_count_total = 0
    push_result: str | dict[str, Any] = "not_started"

    def print_summary(
        items_for_summary: list[dict[str, Any]], all_normalized: list[dict[str, Any]]
    ) -> None:
        summary = compute_change_summary(
            fetched_markets=len(MARKET_TYPES),
            raw_count_total=raw_count_total,
            normalized_items=all_normalized,
            selected_items=items_for_summary,
            dry_run=dry_run,
            push_result=push_result,
        )
        summary["quality"] = json.dumps(
            summary["quality"], ensure_ascii=False, separators=(",", ":")
        )
        print("summary " + " ".join(f"{key}={summary[key]}" for key in summary))

    _load_dotenv_if_available()

    base_url = os.getenv("KIWOOM_BASE_URL", "").strip()
    app_key = os.getenv("KIWOOM_APP_KEY", "").strip()
    app_secret = os.getenv("KIWOOM_APP_SECRET", "").strip()
    backend_api_base = os.getenv("BACKEND_API_BASE", "http://localhost:8000").strip().rstrip("/")
    bridge_api_key = os.getenv("BRIDGE_API_KEY", "dev-bridge-key").strip() or "dev-bridge-key"

    if not app_key or not app_secret:
        print("Missing required env vars: KIWOOM_APP_KEY and/or KIWOOM_APP_SECRET")
        print_summary([], [])
        return 2
    if not base_url:
        print("Missing required env var: KIWOOM_BASE_URL")
        print_summary([], [])
        return 2

    session = _create_retry_session()

    try:
        token_type, token = _fetch_token(session, base_url, app_key, app_secret)
    except Exception as e:
        print(f"Failed to fetch Kiwoom token: {e}")
        print_summary([], [])
        return 1

    records_by_market: list[tuple[str, list[dict[str, Any]]]] = []
    for mrkt_tp in MARKET_TYPES:
        records = _fetch_market_list(session, base_url, token_type, token, mrkt_tp)
        raw_count_total += len(records)
        records_by_market.append((mrkt_tp, records))
        if verbose:
            print(f"mrkt_tp={mrkt_tp} received={len(records)}")

    normalized_items = _normalize_and_dedup(records_by_market)
    if verbose:
        pre_summary = compute_change_summary(
            fetched_markets=len(MARKET_TYPES),
            raw_count_total=raw_count_total,
            normalized_items=normalized_items,
            selected_items=normalized_items,
            dry_run=dry_run,
            push_result=push_result,
        )
        quality = pre_summary["quality"]
        print(
            "quality "
            f"listed_date_parsed={quality['listed_date_parsed']} "
            f"category_l1_missing={quality['category_l1_missing']} "
            f"per_market_counts={json.dumps(quality['per_market_counts'], ensure_ascii=False)}"
        )

    items = normalized_items
    if limit is not None:
        items = items[:limit]

    push_result = "skipped"

    if dry_run:
        print(f"total={len(items)}")
        print(
            "change_summary="
            + json.dumps(
                compute_change_summary(
                    fetched_markets=len(MARKET_TYPES),
                    raw_count_total=raw_count_total,
                    normalized_items=normalized_items,
                    selected_items=items,
                    dry_run=True,
                    push_result=push_result,
                ),
                ensure_ascii=False,
            )
        )
        print(json.dumps(items[:3], ensure_ascii=False, indent=2))
    else:
        if not _check_backend_health(backend_api_base):
            print(
                f"Backend not running at {backend_api_base}. Start docker compose and verify with curl {backend_api_base}/health"
            )
            push_result = "health_check_failed"
            print_summary(items, normalized_items)
            return 3

        upsert_url = f"{backend_api_base}/api/internal/stocks:upsert"
        upsert_headers = {
            "Content-Type": "application/json",
            "X-Bridge-Key": bridge_api_key,
        }
        payload = {"items": items}

        try:
            result = _post_json(session, upsert_url, upsert_headers, payload, timeout=30)
            print(json.dumps(result, ensure_ascii=False))
            push_result = result
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            print(f"Backend upsert failed url={upsert_url} status={status_code}")
            push_result = f"upsert_error_status_{status_code}"
            print_summary(items, normalized_items)
            return 4

    print_summary(items, normalized_items)
    return 0
