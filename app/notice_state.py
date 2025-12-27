from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.storage_paths import get_settings_dir


NOTICE_STATE_FILE = "notice_state.json"


def _state_path() -> Path:
    return get_settings_dir() / NOTICE_STATE_FILE


def save_last_seen(created_at: str) -> None:
    path = _state_path()
    path.write_text(json.dumps({"last_seen": created_at}), encoding="utf-8")


def load_last_seen() -> Optional[str]:
    path = _state_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("last_seen")
    except Exception:
        return None


def is_newer(created_at: str, last_seen: Optional[str]) -> bool:
    if not created_at:
        return False
    if not last_seen:
        return True
    try:
        return datetime.fromisoformat(created_at) > datetime.fromisoformat(last_seen)
    except Exception:
        return False
