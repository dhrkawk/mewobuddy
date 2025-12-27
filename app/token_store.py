from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.storage_paths import get_tokens_dir


TOKEN_FILE = "access_token.json"


def _token_path() -> Path:
    return get_tokens_dir() / TOKEN_FILE


def save_token(token: str) -> None:
    path = _token_path()
    path.write_text(json.dumps({"access_token": token}), encoding="utf-8")


def load_token() -> Optional[str]:
    path = _token_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("access_token")
    except Exception:
        return None


def clear_token() -> None:
    path = _token_path()
    if path.exists():
        path.unlink()
