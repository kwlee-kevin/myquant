from __future__ import annotations

import os
from pathlib import Path

import pytest

from bridge.config import find_repo_root, load_bridge_env_files, resolve_kiwoom_config


def test_resolve_kiwoom_config_paper_mode_with_mode_specific_vars():
    cfg = resolve_kiwoom_config(
        {
            "KIWOOM_MODE": "paper",
            "KIWOOM_PAPER_APP_KEY": "paper-key",
            "KIWOOM_PAPER_APP_SECRET": "paper-secret",
            "KIWOOM_PAPER_HOST_URL": "https://mockapi.kiwoom.com",
        }
    )
    assert cfg.mode == "paper"
    assert cfg.app_key == "paper-key"
    assert cfg.app_secret == "paper-secret"
    assert cfg.host_url == "https://mockapi.kiwoom.com"


def test_resolve_kiwoom_config_real_mode_with_mode_specific_vars():
    cfg = resolve_kiwoom_config(
        {
            "KIWOOM_MODE": "real",
            "KIWOOM_REAL_APP_KEY": "real-key",
            "KIWOOM_REAL_APP_SECRET": "real-secret",
            "KIWOOM_REAL_HOST_URL": "https://api.kiwoom.com",
        }
    )
    assert cfg.mode == "real"
    assert cfg.app_key == "real-key"
    assert cfg.app_secret == "real-secret"
    assert cfg.host_url == "https://api.kiwoom.com"


def test_resolve_kiwoom_config_reports_concrete_missing_vars():
    with pytest.raises(ValueError) as excinfo:
        resolve_kiwoom_config({"KIWOOM_MODE": "paper"})
    message = str(excinfo.value)
    assert "KIWOOM_PAPER_APP_KEY" in message
    assert "KIWOOM_PAPER_APP_SECRET" in message
    assert "KIWOOM_PAPER_HOST_URL" in message


def test_resolve_kiwoom_config_invalid_mode_raises():
    with pytest.raises(ValueError, match="Invalid KIWOOM_MODE"):
        resolve_kiwoom_config({"KIWOOM_MODE": "sandbox"})


def test_load_bridge_env_files_precedence_process_then_root_then_bridge(monkeypatch, tmp_path):
    bridge_env = tmp_path / "bridge.env"
    root_env = tmp_path / "root.env"

    bridge_env.write_text(
        "\n".join(
            [
                "KIWOOM_PAPER_APP_KEY=bridge-key",
                "KIWOOM_PAPER_APP_SECRET=bridge-secret",
                "KIWOOM_PAPER_HOST_URL=https://bridge.mock",
            ]
        ),
        encoding="utf-8",
    )
    root_env.write_text(
        "\n".join(
            [
                "KIWOOM_PAPER_APP_KEY=root-key",
                "KIWOOM_PAPER_APP_SECRET=root-secret",
                "KIWOOM_PAPER_HOST_URL=https://root.mock",
            ]
        ),
        encoding="utf-8",
    )

    tracked_keys = [
        "KIWOOM_PAPER_APP_KEY",
        "KIWOOM_PAPER_APP_SECRET",
        "KIWOOM_PAPER_HOST_URL",
    ]
    originals = {key: os.environ.get(key) for key in tracked_keys}

    monkeypatch.setenv("KIWOOM_PAPER_APP_KEY", "process-key")
    monkeypatch.delenv("KIWOOM_PAPER_APP_SECRET", raising=False)
    monkeypatch.delenv("KIWOOM_PAPER_HOST_URL", raising=False)

    try:
        load_bridge_env_files(Path(bridge_env), Path(root_env))

        assert "process-key" == os.environ["KIWOOM_PAPER_APP_KEY"]
        assert "root-secret" == os.environ["KIWOOM_PAPER_APP_SECRET"]
        assert "https://root.mock" == os.environ["KIWOOM_PAPER_HOST_URL"]
    finally:
        for key, value in originals.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_find_repo_root_returns_project_root():
    root = find_repo_root()
    assert (root / "docker-compose.yml").exists()
    assert (root / "bridge").exists()
