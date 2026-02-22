from __future__ import annotations

from typing import Any

MARKET_TYPE_TO_BACKEND = {
    "0": "KOSPI",
    "10": "KOSDAQ",
    "50": "KONEX",
    "8": "ETF",
}

CODE_KEYS = ["code", "stk_cd", "jongmok_cd", "isu_cd", "item_code", "symbol"]
NAME_KR_KEYS = ["name_kr", "stk_nm", "jongmok_nm", "isu_nm", "item_name", "name"]
NAME_EN_KEYS = ["name_en", "eng_nm", "item_name_en", "en_name"]


def map_market(mrkt_tp: str) -> str:
    return MARKET_TYPE_TO_BACKEND.get(str(mrkt_tp), "ETN")


def _pick_value(record: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip() != "":
            return value
    return None


def normalize_item(record: dict[str, Any], mrkt_tp: str) -> dict[str, Any] | None:
    raw_code = _pick_value(record, CODE_KEYS)
    raw_name_kr = _pick_value(record, NAME_KR_KEYS)
    raw_name_en = _pick_value(record, NAME_EN_KEYS)

    if raw_code is None or raw_name_kr is None:
        return None

    code = str(raw_code).strip().upper()
    name_kr = str(raw_name_kr).strip()
    if not code or not name_kr:
        return None

    name_en = str(raw_name_en).strip() if raw_name_en is not None else None
    if name_en == "":
        name_en = None

    return {
        "code": code,
        "name_kr": name_kr,
        "name_en": name_en,
        "market": map_market(str(mrkt_tp)),
        "category_l1": None,
        "category_l2": None,
        "is_active": True,
        "listed_date": None,
        "delisted_date": None,
    }
