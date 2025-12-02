import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication

from desktopcat.core.asset_manager import AssetManager
from desktopcat.core.config_loader import ConfigLoader
from desktopcat.core.context_config import ContextRulesLoader
from desktopcat.core.context_manager import ContextManager
from desktopcat.ui.widget import CatWidget


def _resolve_override_path(args: list[str]) -> Optional[Path]:
    if len(args) > 1:
        candidate = Path(args[1]).expanduser()
        return candidate
    return None


def run() -> None:
    app = QApplication(sys.argv)

    config_loader = ConfigLoader()
    asset_manager = AssetManager(config_loader)
    context_rules_loader = ContextRulesLoader()
    override_path = _resolve_override_path(sys.argv)
    try:
        asset = asset_manager.resolve_asset(override_path=override_path)
    except Exception as exc:  # noqa: BLE001 - show helpful startup error
        print(f"Failed to load asset: {exc}")
        sys.exit(1)

    widget = CatWidget(asset)
    widget.show()

    context_manager: Optional[ContextManager] = None
    if override_path is None:
        context_manager = ContextManager(widget, asset_manager, context_rules_loader)
        context_manager.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()
