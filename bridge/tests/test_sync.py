from bridge.sync import (
    MARKET_TYPES,
    _map_market,
    _map_security_type,
    _normalize_and_dedup,
    _normalize_ka10099_item,
)


def test_map_market_values():
    assert _map_market("0") == "KOSPI"
    assert _map_market("10") == "KOSDAQ"
    assert _map_market("50") == "KONEX"
    assert _map_market("8") is None
    assert _map_market("3") is None


def test_map_security_type_values():
    assert _map_security_type("8") == "ETF"
    assert _map_security_type("6") == "REIT"
    assert _map_security_type("999") == "COMMON_STOCK"


def test_normalize_and_dedup_by_code_keeps_first_seen():
    records_by_market = [
        (
            "0",
            [
                {"stk_cd": "005930", "stk_nm": "삼성전자"},
                {"stk_cd": "000660", "stk_nm": "SK하이닉스"},
            ],
        ),
        (
            "10",
            [
                {"stk_cd": "005930", "stk_nm": "삼성전자(dup)"},
                {"stk_cd": "035420", "stk_nm": "NAVER"},
            ],
        ),
    ]

    items = _normalize_and_dedup(records_by_market)

    assert [item["code"] for item in items] == ["005930", "000660", "035420"]
    assert items[0]["name_kr"] == "삼성전자"
    assert items[0]["market"] == "KOSPI"


def test_limit_is_applied_after_normalization_and_dedup():
    records_by_market = [
        (
            "0",
            [
                {"stk_cd": "A1", "stk_nm": "A1"},
                {"stk_cd": "A2", "stk_nm": "A2"},
            ],
        ),
        (
            "10",
            [
                {"stk_cd": "A2", "stk_nm": "A2-dup"},
                {"stk_cd": "A3", "stk_nm": "A3"},
            ],
        ),
    ]

    items = _normalize_and_dedup(records_by_market)
    limited = items[:2]

    assert [item["code"] for item in limited] == ["A1", "A2"]


def test_market_type_list_matches_requirement():
    assert MARKET_TYPES == ["0", "10", "50"]


def test_normalize_ka10099_primary_keys_and_categories():
    raw = {
        "code": "005930",
        "name": "삼성전자",
        "regDay": "19750611",
        "marketCode": "8",
        "upName": "전기전자",
        "companyClassName": "보통주",
    }

    normalized = _normalize_ka10099_item(raw, "0")
    assert normalized == {
        "code": "005930",
        "name_kr": "삼성전자",
        "name_en": None,
        "market": "KOSPI",
        "security_type": "ETF",
        "mrkt_tp_raw": "0",
        "market_code_raw": "8",
        "category_l1": "전기전자",
        "category_l2": "보통주",
        "is_active": True,
        "listed_date": "1975-06-11",
        "delisted_date": None,
    }


def test_normalize_ka10099_fallback_keys_still_supported():
    raw = {
        "stk_cd": "000660",
        "stk_nm": "SK하이닉스",
        "regDay": "invalid",
    }
    normalized = _normalize_ka10099_item(raw, "0")
    assert normalized is not None
    assert normalized["code"] == "000660"
    assert normalized["name_kr"] == "SK하이닉스"
    assert normalized["listed_date"] is None
    assert normalized["security_type"] == "COMMON_STOCK"


def test_normalize_ka10099_excludes_unmanaged_market():
    raw = {"code": "123456", "name": "테스트"}
    assert _normalize_ka10099_item(raw, "8") is None
