from bridge.normalize import map_market, normalize_item


def test_market_mapping_explicit_values():
    assert map_market("0") == "KOSPI"
    assert map_market("10") == "KOSDAQ"
    assert map_market("50") == "KONEX"
    assert map_market("8") == "ETF"


def test_market_mapping_fallback_to_etn():
    assert map_market("3") == "ETN"
    assert map_market("5") == "ETN"
    assert map_market("4") == "ETN"
    assert map_market("6") == "ETN"
    assert map_market("9") == "ETN"
    assert map_market("999") == "ETN"


def test_normalize_item_shape_matches_backend_spec():
    record = {
        "stk_cd": "005930",
        "stk_nm": "삼성전자",
        "eng_nm": "Samsung Electronics",
    }

    normalized = normalize_item(record, "0")

    assert normalized == {
        "code": "005930",
        "name_kr": "삼성전자",
        "name_en": "Samsung Electronics",
        "market": "KOSPI",
        "category_l1": None,
        "category_l2": None,
        "is_active": True,
        "listed_date": None,
        "delisted_date": None,
    }


def test_normalize_item_drops_invalid_records():
    assert normalize_item({"stk_nm": "이름만있음"}, "0") is None
    assert normalize_item({"stk_cd": "005930"}, "0") is None
