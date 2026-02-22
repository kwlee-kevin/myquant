import requests

from bridge import sync


def _set_required_env(monkeypatch):
    monkeypatch.setenv("KIWOOM_BASE_URL", "https://kiwoom.example")
    monkeypatch.setenv("KIWOOM_APP_KEY", "key")
    monkeypatch.setenv("KIWOOM_APP_SECRET", "secret")
    monkeypatch.setenv("BACKEND_API_BASE", "http://localhost:8000")
    monkeypatch.setenv("BRIDGE_API_KEY", "bridge-key")


class DummySession:
    def post(self, *args, **kwargs):  # pragma: no cover - not used in tests with monkeypatch
        raise AssertionError("Unexpected network call")


def test_health_check_failure_returns_3(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: DummySession())
    monkeypatch.setattr(sync, "_fetch_token", lambda *args, **kwargs: ("Bearer", "token"))
    monkeypatch.setattr(
        sync,
        "_fetch_market_list",
        lambda *args, **kwargs: [{"code": "005930", "name": "삼성전자"}],
    )
    monkeypatch.setattr(sync, "_check_backend_health", lambda base: False)

    code = sync.sync_stocks(dry_run=False, limit=1, verbose=False)

    assert code == 3
    out = capsys.readouterr().out
    assert "Backend not running at http://localhost:8000" in out
    assert "summary" in out


def test_upsert_network_failure_returns_4(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: DummySession())
    monkeypatch.setattr(sync, "_fetch_token", lambda *args, **kwargs: ("Bearer", "token"))
    monkeypatch.setattr(
        sync,
        "_fetch_market_list",
        lambda *args, **kwargs: [{"code": "005930", "name": "삼성전자"}],
    )
    monkeypatch.setattr(sync, "_check_backend_health", lambda base: True)

    def raise_conn(*args, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(sync, "_post_json", raise_conn)

    code = sync.sync_stocks(dry_run=False, limit=1, verbose=False)

    assert code == 4
    out = capsys.readouterr().out
    assert "Backend upsert failed url=http://localhost:8000/api/internal/stocks:upsert" in out
    assert "summary" in out


def test_verbose_and_summary_output(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: DummySession())
    monkeypatch.setattr(sync, "_fetch_token", lambda *args, **kwargs: ("Bearer", "token"))

    def fake_fetch_market_list(*args, **kwargs):
        mrkt_tp = args[-1]
        return [{"code": f"C{mrkt_tp}", "name": f"Name{mrkt_tp}"}]

    monkeypatch.setattr(sync, "_fetch_market_list", fake_fetch_market_list)

    code = sync.sync_stocks(dry_run=True, limit=2, verbose=True)

    assert code == 0
    out = capsys.readouterr().out
    assert "mrkt_tp=0 received=1" in out
    assert "quality listed_date_parsed=" in out
    assert "summary fetched_markets=9" in out
    assert "limited_to=2" in out
