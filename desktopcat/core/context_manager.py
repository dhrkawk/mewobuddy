from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, QTimer

from desktopcat.core.asset_manager import AssetManager, AssetDescriptor
from desktopcat.core.context_config import ContextRulesLoader
from desktopcat.core.window_info import get_foreground_window_info
from desktopcat.ui.widget import CatWidget


class ContextManager(QObject):
    """Poll foreground window and switch cat asset based on context rules."""

    def __init__(
        self,
        widget: CatWidget,
        asset_manager: AssetManager,
        rules_loader: Optional[ContextRulesLoader] = None,
    ) -> None:
        super().__init__(widget)
        self.widget = widget
        self.asset_manager = asset_manager
        self.rules_loader = rules_loader or ContextRulesLoader()

        self.rules: List[Dict[str, Any]] = self.rules_loader.get_rules()
        self.default_category: str = self.rules_loader.get_default_category()
        self.poll_interval_ms: int = self.rules_loader.get_poll_interval_ms()

        self.current_category: Optional[str] = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def start(self) -> None:
        self.timer.start(self.poll_interval_ms)

    def stop(self) -> None:
        self.timer.stop()

    def _tick(self) -> None:
        info = get_foreground_window_info()
        category = self._match_category(info)
        if category and category != self.current_category:
            try:
                asset: AssetDescriptor = self.asset_manager.resolve_asset(category=category)
            except Exception:
                # Fallback to default if resolution fails
                try:
                    asset = self.asset_manager.resolve_asset(category=self.default_category)
                    category = self.default_category
                except Exception:
                    return
            self.current_category = category
            self.widget.load_asset(asset)

    def _match_category(self, info) -> str:
        if info is None:
            return self.default_category

        proc = info.process_name.lower()
        title = info.window_title.lower()

        for rule in self.rules:
            processes = [p.lower() for p in rule.get("process", [])]
            title_subs = [t.lower() for t in rule.get("title_contains", [])]
            if processes and proc not in processes:
                continue
            if title_subs:
                if not any(sub in title for sub in title_subs):
                    continue
            category = rule.get("category") or self.default_category
            return category

        return self.default_category
