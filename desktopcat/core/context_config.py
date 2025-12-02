from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextRulesLoader:
    """Load context-matching rules from JSON."""

    def __init__(self, config_path: Optional[Path | str] = None) -> None:
        self.project_root = Path(__file__).resolve().parents[2]
        self.config_path = Path(config_path) if config_path else self.project_root / "config" / "context_rules.json"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Context rules file not found at {self.config_path}")
        with self.config_path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    def get_poll_interval_ms(self) -> int:
        return int(self._config.get("poll_interval_ms", 1000))

    def get_default_category(self) -> str:
        return self._config.get("default_category", "idle")

    def get_rules(self) -> List[Dict[str, Any]]:
        return self._config.get("rules", [])
