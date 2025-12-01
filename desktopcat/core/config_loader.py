from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """Load and provide access to asset configuration."""

    def __init__(self, config_path: Optional[Path | str] = None) -> None:
        self.project_root = Path(__file__).resolve().parents[2]
        self.config_path = Path(config_path) if config_path else self.project_root / "config" / "asset_mapping.json"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get_assets_base(self) -> Path:
        assets_base = self._config.get("assets_base", "assets/cats")
        return self.project_root / assets_base

    def get_default_category(self) -> str:
        return self._config.get("default_category", "")

    def get_category_entry(self, category: str) -> Dict[str, Any]:
        categories = self._config.get("categories", {})
        if category not in categories:
            raise KeyError(f"Category '{category}' not found in config")
        return categories[category]
