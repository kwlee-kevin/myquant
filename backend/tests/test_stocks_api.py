import pytest
from rest_framework.test import APIClient
from stocks.models import StockMaster


@pytest.fixture
def client():
    return APIClient()


def create_stock(**kwargs):
    defaults = {
        "code": "005930",
        "name_kr": "삼성전자",
        "name_en": "Samsung Electronics",
        "market": "KOSPI",
        "security_type": "COMMON_STOCK",
        "category_l1": "반도체",
        "category_l2": None,
        "is_active": True,
    }
    defaults.update(kwargs)
    return StockMaster.objects.create(**defaults)


@pytest.mark.django_db
def test_keywords_and_vs_or(client):
    create_stock(code="005930", name_kr="삼성전자")
    create_stock(code="028260", name_kr="삼성물산")

    and_response = client.get("/api/stocks", {"keywords": "삼성 전자", "op": "and"})
    assert and_response.status_code == 200
    assert and_response.json()["count"] == 1
    assert and_response.json()["results"][0]["code"] == "005930"

    or_response = client.get("/api/stocks", {"keywords": "삼성 전자", "op": "or"})
    assert or_response.status_code == 200
    codes = {item["code"] for item in or_response.json()["results"]}
    assert codes == {"005930", "028260"}


@pytest.mark.django_db
def test_categories_and_markets_repeated_params(client):
    create_stock(
        code="005930",
        market="KOSPI",
        security_type="COMMON_STOCK",
        category_l1="반도체",
        category_l2=None,
    )
    create_stock(
        code="000660",
        market="KOSPI",
        security_type="ETF",
        category_l1="IT",
        category_l2="반도체",
    )
    create_stock(
        code="035420",
        market="KOSDAQ",
        security_type="COMMON_STOCK",
        category_l1="인터넷",
        category_l2=None,
    )

    response = client.get(
        "/api/stocks",
        {
            "categories": ["반도체", "자동차"],
            "markets": ["KOSPI"],
        },
    )

    assert response.status_code == 200
    codes = {item["code"] for item in response.json()["results"]}
    assert codes == {"005930", "000660"}


@pytest.mark.django_db
def test_security_type_repeated_filter(client):
    create_stock(code="A00001", market="KOSPI", security_type="COMMON_STOCK")
    create_stock(code="A00002", market="KOSPI", security_type="ETF")
    create_stock(code="A00003", market="KOSDAQ", security_type="REIT")

    response = client.get(
        "/api/stocks",
        {"security_types": ["COMMON_STOCK", "ETF"], "markets": ["KOSPI", "KOSDAQ"]},
    )
    assert response.status_code == 200
    codes = {item["code"] for item in response.json()["results"]}
    assert codes == {"A00001", "A00002"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"op": "xor"},
        {"ordering": "market"},
        {"page": "0"},
        {"page": "abc"},
        {"page_size": "0"},
        {"page_size": "101"},
    ],
)
def test_validation_400_cases(client, params):
    response = client.get("/api/stocks", params)
    assert response.status_code == 400


@pytest.mark.django_db
def test_detail_200_and_404(client):
    create_stock(code="005930")

    ok_response = client.get("/api/stocks/005930")
    assert ok_response.status_code == 200
    assert ok_response.json()["code"] == "005930"

    not_found_response = client.get("/api/stocks/999999")
    assert not_found_response.status_code == 404


@pytest.mark.django_db
def test_upsert_requires_bridge_key(client, monkeypatch):
    monkeypatch.setenv("BRIDGE_API_KEY", "valid-key")
    payload = {
        "items": [
            {
                "code": "005930",
                "name_kr": "삼성전자",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
            }
        ]
    }

    missing_key = client.post("/api/internal/stocks:upsert", payload, format="json")
    assert missing_key.status_code == 401

    invalid_key = client.post(
        "/api/internal/stocks:upsert",
        payload,
        format="json",
        HTTP_X_BRIDGE_KEY="wrong-key",
    )
    assert invalid_key.status_code == 401


@pytest.mark.django_db
def test_upsert_insert_then_update_counts(client, monkeypatch):
    monkeypatch.setenv("BRIDGE_API_KEY", "valid-key")

    first_payload = {
        "items": [
            {
                "code": "005930",
                "name_kr": "삼성전자",
                "name_en": "Samsung Electronics",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
                "category_l1": "반도체",
                "is_active": True,
            },
            {
                "code": "000660",
                "name_kr": "SK하이닉스",
                "name_en": "SK hynix",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
                "category_l1": "반도체",
                "is_active": True,
            },
        ]
    }

    first_response = client.post(
        "/api/internal/stocks:upsert",
        first_payload,
        format="json",
        HTTP_X_BRIDGE_KEY="valid-key",
    )
    assert first_response.status_code == 200
    assert first_response.json() == {"received": 2, "inserted": 2, "updated": 0, "unchanged": 0}

    second_payload = {
        "items": [
            {
                "code": "005930",
                "name_kr": "삼성전자(수정)",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
                "category_l1": "반도체",
                "is_active": True,
            },
            {
                "code": "035420",
                "name_kr": "NAVER",
                "market": "KOSDAQ",
                "security_type": "COMMON_STOCK",
                "category_l1": "인터넷",
                "is_active": True,
            },
        ]
    }

    second_response = client.post(
        "/api/internal/stocks:upsert",
        second_payload,
        format="json",
        HTTP_X_BRIDGE_KEY="valid-key",
    )
    assert second_response.status_code == 200
    assert second_response.json() == {"received": 2, "inserted": 1, "updated": 1, "unchanged": 0}

    updated = StockMaster.objects.get(code="005930")
    assert updated.name_kr == "삼성전자(수정)"


@pytest.mark.django_db
def test_upsert_unchanged_and_updated_metrics(client, monkeypatch):
    monkeypatch.setenv("BRIDGE_API_KEY", "valid-key")
    initial_payload = {
        "items": [
            {
                "code": "005930",
                "name_kr": "삼성전자",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
                "category_l1": "반도체",
                "is_active": True,
            }
        ]
    }
    initial = client.post(
        "/api/internal/stocks:upsert",
        initial_payload,
        format="json",
        HTTP_X_BRIDGE_KEY="valid-key",
    )
    assert initial.status_code == 200
    assert initial.json() == {"received": 1, "inserted": 1, "updated": 0, "unchanged": 0}

    same_again = client.post(
        "/api/internal/stocks:upsert",
        initial_payload,
        format="json",
        HTTP_X_BRIDGE_KEY="valid-key",
    )
    assert same_again.status_code == 200
    assert same_again.json() == {"received": 1, "inserted": 0, "updated": 0, "unchanged": 1}

    changed_payload = {
        "items": [
            {
                "code": "005930",
                "name_kr": "삼성전자(변경)",
                "market": "KOSPI",
                "security_type": "COMMON_STOCK",
                "category_l1": "반도체",
                "is_active": True,
            }
        ]
    }
    changed = client.post(
        "/api/internal/stocks:upsert",
        changed_payload,
        format="json",
        HTTP_X_BRIDGE_KEY="valid-key",
    )
    assert changed.status_code == 200
    assert changed.json() == {"received": 1, "inserted": 0, "updated": 1, "unchanged": 0}


@pytest.mark.django_db
def test_list_ordering_and_filters_with_large_dataset(client):
    rows = []
    for i in range(200):
        rows.append(
            StockMaster(
                code=f"{100000 + i}",
                name_kr=f"종목{i:03d}",
                name_en=None,
                market="KOSPI" if i % 2 == 0 else "KOSDAQ",
                security_type="COMMON_STOCK",
                category_l1="반도체" if i % 3 == 0 else "자동차",
                category_l2=None,
                is_active=True,
            )
        )
    StockMaster.objects.bulk_create(rows)

    response = client.get(
        "/api/stocks",
        {
            "markets": ["KOSPI"],
            "categories": ["반도체"],
            "ordering": "name_kr",
            "page": 1,
            "page_size": 100,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] > 0
    result_names = [item["name_kr"] for item in payload["results"]]
    assert result_names == sorted(result_names)


@pytest.mark.django_db
def test_stats_endpoint_returns_market_and_top_category_counts(client):
    StockMaster.objects.bulk_create(
        [
            StockMaster(code="A00001", name_kr="A1", market="KOSPI", category_l1="반도체"),
            StockMaster(code="A00002", name_kr="A2", market="KOSPI", category_l1="반도체"),
            StockMaster(code="A00003", name_kr="A3", market="KOSDAQ", category_l1="자동차"),
            StockMaster(code="A00004", name_kr="A4", market="KONEX", category_l1=None),
        ]
    )

    response = client.get("/api/stocks/stats")
    assert response.status_code == 200
    payload = response.json()

    assert payload["by_market"]["KOSPI"] == 2
    assert payload["by_market"]["KOSDAQ"] == 1
    assert payload["by_market"]["KONEX"] == 1
    assert payload["top_category_l1"][0] == {"category_l1": "반도체", "count": 2}
