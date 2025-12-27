from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


APP_NAME = "MeowBuddy"


def get_app_root() -> Path:
    """Resolve the root app data directory (Windows APPDATA preferred)."""
    appdata = os.getenv("APPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    return base / APP_NAME


def ensure_app_dirs() -> Dict[str, Path]:
    """Create the root and subdirectories; return their paths."""
    root = get_app_root()
    root.mkdir(parents=True, exist_ok=True)

    subdirs = {
        "tokens": root / "tokens",
        "settings": root / "settings",
        "assets_cache": root / "assets_cache",
        "logs": root / "logs",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return {"root": root, **subdirs}


def get_tokens_dir() -> Path:
    dirs = ensure_app_dirs()
    return dirs["tokens"]


def get_settings_dir() -> Path:
    dirs = ensure_app_dirs()
    return dirs["settings"]


def get_assets_cache_dir() -> Path:
    dirs = ensure_app_dirs()
    return dirs["assets_cache"]


def get_logs_dir() -> Path:
    dirs = ensure_app_dirs()
    return dirs["logs"]
