import pytest
import requests

from bridge import sync


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text="", raise_on_json=False):
        self.status_code = status_code
        self._json_data = {} if json_data is None else json_data
        self.text = text
        self.ok = 200 <= status_code < 300
        self._raise_on_json = raise_on_json

    def json(self):
        if self._raise_on_json:
            raise ValueError("invalid json")
        return self._json_data


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.mounted = {}

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return self.response

    def mount(self, prefix, adapter):
        self.mounted[prefix] = adapter


def _set_required_env(monkeypatch):
    monkeypatch.setenv("KIWOOM_BASE_URL", "https://kiwoom.example")
    monkeypatch.setenv("KIWOOM_APP_KEY", "key")
    monkeypatch.setenv("KIWOOM_APP_SECRET", "secret")
    monkeypatch.setenv("BACKEND_API_BASE", "http://localhost:8000")
    monkeypatch.setenv("BRIDGE_API_KEY", "bridge-key")


def test_load_dotenv_handles_missing_package(monkeypatch):
    import builtins

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "dotenv":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    sync._load_dotenv_if_available()


def test_create_retry_session_mounts_http_and_https():
    session = sync._create_retry_session()
    assert isinstance(session, requests.Session)
    assert "http://" in session.adapters
    assert "https://" in session.adapters


def test_safe_response_snippet_handles_text_access_error():
    class BrokenTextResponse:
        @property
        def text(self):
            raise RuntimeError("boom")

    assert sync._safe_response_snippet(BrokenTextResponse()) == ""


def test_post_json_raises_http_error_with_body_snippet():
    response = FakeResponse(status_code=500, json_data={"x": 1}, text="server down")
    session = FakeSession(response)

    with pytest.raises(requests.HTTPError, match="status=500"):
        sync._post_json(session, "https://example.test/api", {}, {}, timeout=3)


def test_post_json_returns_empty_dict_when_json_is_not_object():
    response = FakeResponse(status_code=200, json_data=[{"x": 1}])
    session = FakeSession(response)
    data = sync._post_json(session, "https://example.test/api", {}, {}, timeout=3)
    assert data == {}


def test_fetch_token_non_json_http_error_includes_snippet():
    response = FakeResponse(status_code=401, text="unauthorized", raise_on_json=True)
    session = FakeSession(response)

    with pytest.raises(RuntimeError, match="Kiwoom token HTTP error: status=401"):
        sync._fetch_token(session, "https://kiwoom.example", "k", "s")


def test_fetch_market_list_prefers_explicit_fallback_keys(monkeypatch):
    monkeypatch.setattr(sync, "_post_json", lambda *args, **kwargs: {"items": [{"code": "A"}]})
    items = sync._fetch_market_list(FakeSession(FakeResponse()), "https://k", "Bearer", "t", "0")
    assert items == [{"code": "A"}]


def test_fetch_market_list_returns_empty_when_no_list_found(monkeypatch):
    monkeypatch.setattr(sync, "_post_json", lambda *args, **kwargs: {"meta": {"ok": True}})
    items = sync._fetch_market_list(FakeSession(FakeResponse()), "https://k", "Bearer", "t", "0")
    assert items == []


def test_check_backend_health_handles_non_200_and_bad_json(monkeypatch):
    monkeypatch.setattr(sync.requests, "get", lambda *args, **kwargs: FakeResponse(status_code=503))
    assert sync._check_backend_health("http://backend:8000") is False

    class BadJsonResponse(FakeResponse):
        def json(self):
            raise ValueError("bad json")

    monkeypatch.setattr(
        sync.requests, "get", lambda *args, **kwargs: BadJsonResponse(status_code=200)
    )
    assert sync._check_backend_health("http://backend:8000") is False


def test_check_backend_health_handles_connection_error(monkeypatch):
    def raise_conn(*args, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(sync.requests, "get", raise_conn)
    assert sync._check_backend_health("http://backend:8000") is False


def test_sync_stocks_missing_envs_returns_2(monkeypatch, capsys):
    monkeypatch.setenv("KIWOOM_MODE", "paper")
    monkeypatch.delenv("KIWOOM_APP_KEY", raising=False)
    monkeypatch.delenv("KIWOOM_APP_SECRET", raising=False)
    monkeypatch.delenv("KIWOOM_PAPER_APP_KEY", raising=False)
    monkeypatch.delenv("KIWOOM_PAPER_APP_SECRET", raising=False)
    monkeypatch.setenv("KIWOOM_PAPER_HOST_URL", "https://kiwoom.example")
    code = sync.sync_stocks(dry_run=True, limit=None, verbose=False)
    assert code == 2
    assert "Missing Kiwoom configuration for mode=paper" in capsys.readouterr().out


def test_sync_stocks_missing_base_url_returns_2(monkeypatch, capsys):
    monkeypatch.setenv("KIWOOM_MODE", "paper")
    monkeypatch.setenv("KIWOOM_PAPER_APP_KEY", "key")
    monkeypatch.setenv("KIWOOM_PAPER_APP_SECRET", "secret")
    monkeypatch.delenv("KIWOOM_HOST_URL", raising=False)
    monkeypatch.delenv("KIWOOM_BASE_URL", raising=False)
    monkeypatch.delenv("KIWOOM_PAPER_HOST_URL", raising=False)
    code = sync.sync_stocks(dry_run=True, limit=None, verbose=False)
    assert code == 2
    assert "KIWOOM_PAPER_HOST_URL" in capsys.readouterr().out


def test_sync_stocks_token_failure_returns_1(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: FakeSession(FakeResponse()))

    def fail_token(*args, **kwargs):
        raise RuntimeError("bad")

    monkeypatch.setattr(sync, "_fetch_token", fail_token)
    code = sync.sync_stocks(dry_run=True, limit=None, verbose=False)
    assert code == 1
    assert "Failed to fetch Kiwoom token: bad" in capsys.readouterr().out


def test_sync_stocks_non_dry_run_success_prints_result(monkeypatch, capsys):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(sync, "_create_retry_session", lambda: FakeSession(FakeResponse()))
    monkeypatch.setattr(sync, "_fetch_token", lambda *args, **kwargs: ("Bearer", "token"))
    monkeypatch.setattr(
        sync,
        "_fetch_market_list",
        lambda *args, **kwargs: [{"code": "005930", "name": "삼성전자"}],
    )
    monkeypatch.setattr(sync, "_check_backend_health", lambda *args, **kwargs: True)
    monkeypatch.setattr(sync, "_post_json", lambda *args, **kwargs: {"received": 1, "inserted": 1})

    code = sync.sync_stocks(dry_run=False, limit=1, verbose=False)
    assert code == 0
    out = capsys.readouterr().out
    assert '{"received": 1, "inserted": 1}' in out
    assert "summary fetched_markets=3" in out
