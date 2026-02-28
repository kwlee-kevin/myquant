from __future__ import annotations

import sys
import types

import pytest

from bridge import cli


def _install_fake_sync_module(monkeypatch, calls):
    module = types.ModuleType("bridge.sync")

    def fake_sync_stocks(*, dry_run, limit, verbose):
        calls.append({"dry_run": dry_run, "limit": limit, "verbose": verbose})
        return 0

    module.sync_stocks = fake_sync_stocks
    monkeypatch.setitem(sys.modules, "bridge.sync", module)


def test_main_sync_supports_dry_run(monkeypatch):
    calls = []
    _install_fake_sync_module(monkeypatch, calls)

    code = cli.main(["sync", "--dry-run", "--limit", "5", "--verbose"])

    assert code == 0
    assert calls == [{"dry_run": True, "limit": 5, "verbose": True}]


def test_main_sync_stocks_alias_supported(monkeypatch):
    calls = []
    _install_fake_sync_module(monkeypatch, calls)

    code = cli.main(["sync-stocks", "--no-push"])

    assert code == 0
    assert calls == [{"dry_run": True, "limit": None, "verbose": False}]


def test_main_rejects_invalid_limit(monkeypatch, capsys):
    calls = []
    _install_fake_sync_module(monkeypatch, calls)

    code = cli.main(["sync", "--limit", "0"])

    assert code == 2
    assert "--limit must be >= 1" in capsys.readouterr().out
    assert calls == []


def test_help_works_at_top_level():
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--help"])
    assert excinfo.value.code == 0


def test_help_works_for_sync_subcommand():
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["sync", "--help"])
    assert excinfo.value.code == 0
