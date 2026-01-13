from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from app.storage_paths import get_settings_dir


DEFAULT_API_BASE = "https://mewobuddy-production.up.railway.app"
API_CONFIG_FILE = "api_config.json"


def _config_path() -> Path:
    return get_settings_dir() / API_CONFIG_FILE


def get_api_base_url() -> str:
    return DEFAULT_API_BASE


def save_api_base_url(url: str) -> None:
    path = _config_path()
    path.write_text(json.dumps({"api_base_url": url}), encoding="utf-8")
