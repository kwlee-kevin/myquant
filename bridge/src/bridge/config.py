from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KiwoomConfig:
    mode: str
    app_key: str
    app_secret: str
    host_url: str


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path(__file__)).resolve()
    if cursor.is_file():
        cursor = cursor.parent

    for candidate in [cursor, *cursor.parents]:
        if (candidate / "docker-compose.yml").exists() and (candidate / "bridge").exists():
            return candidate

    return Path(__file__).resolve().parents[3]


def _default_env_paths() -> tuple[Path, Path]:
    repo_root = find_repo_root()
    bridge_dir = repo_root / "bridge"
    return bridge_dir / ".env", repo_root / ".env"


def load_bridge_env_files(
    bridge_env_path: Path | None = None, root_env_path: Path | None = None
) -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    bridge_default, root_default = _default_env_paths()
    bridge_path = bridge_env_path or bridge_default
    root_path = root_env_path or root_default

    # Precedence:
    # 1) process env (already set)
    # 2) repo root .env
    # 3) bridge/.env
    if root_path.exists():
        load_dotenv(dotenv_path=root_path, override=False)
    if bridge_path.exists():
        load_dotenv(dotenv_path=bridge_path, override=False)


def resolve_kiwoom_config(env: Mapping[str, str] | None = None) -> KiwoomConfig:
    source = os.environ if env is None else env

    mode = (source.get("KIWOOM_MODE", "paper") or "paper").strip().lower()
    if mode not in {"real", "paper"}:
        raise ValueError("Invalid KIWOOM_MODE. Expected 'real' or 'paper'.")

    prefix = "KIWOOM_REAL" if mode == "real" else "KIWOOM_PAPER"
    concrete_key_var = f"{prefix}_APP_KEY"
    concrete_secret_var = f"{prefix}_APP_SECRET"
    concrete_host_var = f"{prefix}_HOST_URL"

    app_key = (source.get("KIWOOM_APP_KEY") or source.get(concrete_key_var) or "").strip()
    app_secret = (source.get("KIWOOM_APP_SECRET") or source.get(concrete_secret_var) or "").strip()
    host_url = (
        source.get("KIWOOM_HOST_URL")
        or source.get("KIWOOM_BASE_URL")
        or source.get(concrete_host_var)
        or ""
    ).strip()

    missing: list[str] = []
    if not app_key:
        missing.append(concrete_key_var)
    if not app_secret:
        missing.append(concrete_secret_var)
    if not host_url:
        missing.append(concrete_host_var)

    if missing:
        raise ValueError(
            "Missing Kiwoom configuration for "
            f"mode={mode}: {', '.join(missing)}. "
            "Set KIWOOM_MODE and mode-specific vars in .env or environment."
        )

    return KiwoomConfig(
        mode=mode,
        app_key=app_key,
        app_secret=app_secret,
        host_url=host_url,
    )
