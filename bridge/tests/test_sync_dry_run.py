from __future__ import annotations

import json

from bridge import sync


class DummySession:
    pass


def _set_required_env(monkeypatch):
    monkeypatch.setenv("KIWOOM_BASE_URL", "https://kiwoom.example")
    monkeypatch.setenv("KIWOOM_APP_KEY", "key")
    monkeypatch.setenv("KIWOOM_APP_SECRET", "secret")
    monkeypatch.setenv("BACKEND_API_BASE", "http://localhost:8000")
    monkeypatch.setenv("BRIDGE_API_KEY", "bridge-key")


def test_compute_change_summary_counts_are_deterministic():
    normalized = [
        {
            "code": "005930",
            "market": "KOSPI",
            "listed_date": "1975-06-11",
            "category_l1": "전기전자",
        },
        {"code": "000660", "market": "KOSPI", "listed_date": None, "category_l1": None},
        {"code": "035420", "market": "KOSDAQ", "listed_date": None, "category_l1": "IT"},
    ]
    selected = normalized[:2]

    summary = sync.compute_change_summary(
        fetched_markets=9,
        raw_count_total=5,
        normalized_items=normalized,
        selected_items=selected,
        dry_run=True,
        push_result="skipped",
    )

    assert summary["fetched_markets"] == 9
    assert summary["raw_count_total"] == 5
    assert summary["normalized_unique"] == 3
    assert summary["limited_to"] == 2
    assert summary["dry_run"] is True
    assert summary["push_result"] == "skipped"
    assert summary["quality"]["listed_date_parsed"] == "1/3"
    assert summary["quality"]["category_l1_missing"] == "1/3"
    assert summary["quality"]["per_market_counts"] == {"KOSPI": 2, "KOSDAQ": 1}


def test_sync_dry_run_skips_backend_write_paths(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: DummySession())
    monkeypatch.setattr(sync, "_fetch_token", lambda *args, **kwargs: ("Bearer", "token"))
    monkeypatch.setattr(
        sync,
        "_fetch_market_list",
        lambda *args, **kwargs: [
            {"code": "005930", "name": "삼성전자", "regDay": "19750611", "upName": "전기전자"},
            {"code": "005930", "name": "삼성전자"},  # duplicate
            {"code": "000660", "name": "SK하이닉스"},
        ],
    )

    def fail_health(*args, **kwargs):
        raise AssertionError("backend health check should not run during dry-run")

    def fail_post(*args, **kwargs):
        raise AssertionError("backend upsert should not run during dry-run")

    monkeypatch.setattr(sync, "_check_backend_health", fail_health)
    monkeypatch.setattr(sync, "_post_json", fail_post)

    code = sync.sync_stocks(dry_run=True, limit=1, verbose=False)

    assert code == 0
    out = capsys.readouterr().out
    assert "total=1" in out
    assert "change_summary=" in out
    assert "summary fetched_markets=9" in out

    summary_line = next(line for line in out.splitlines() if line.startswith("change_summary="))
    payload = json.loads(summary_line.split("=", 1)[1])
    assert payload["dry_run"] is True
    assert payload["push_result"] == "skipped"
    assert payload["limited_to"] == 1
