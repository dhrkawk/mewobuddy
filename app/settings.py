from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from app.storage_paths import get_settings_dir


DEFAULT_API_BASE = "http://127.0.0.1:8000"
API_CONFIG_FILE = "api_config.json"


def _config_path() -> Path:
    return get_settings_dir() / API_CONFIG_FILE


def get_api_base_url() -> str:
    env_val = os.getenv("MEOWBUDDY_API_BASE")
    if env_val:
        return env_val
    path = _config_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            url = data.get("api_base_url")
            if url:
                return url
        except Exception:
            pass
    return DEFAULT_API_BASE


def save_api_base_url(url: str) -> None:
    path = _config_path()
    path.write_text(json.dumps({"api_base_url": url}), encoding="utf-8")
