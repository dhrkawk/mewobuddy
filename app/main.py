from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication

from app.dashboard import DashboardWindow
from app.storage_paths import ensure_app_dirs
from app.tray import TrayManager
from app.notice_poller import NoticePoller
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


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    ensure_app_dirs()

    config_loader = ConfigLoader()
    asset_manager = AssetManager(config_loader)
    context_rules_loader = ContextRulesLoader()
    override_path = _resolve_override_path(sys.argv)

    try:
        asset = asset_manager.resolve_asset(override_path=override_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load asset: {exc}")
        return 1

    cat_widget = CatWidget(asset)
    cat_widget.show()

    context_manager: Optional[ContextManager] = None
    if override_path is None:
        context_manager = ContextManager(cat_widget, asset_manager, context_rules_loader)
        context_manager.start()
        app.aboutToQuit.connect(context_manager.stop)

    dashboard = DashboardWindow()
    notice_poller: Optional[NoticePoller] = None

    def open_dashboard_home():
        dashboard.show()
        dashboard.raise_()
        dashboard.activateWindow()
        dashboard.open_home()
        if notice_poller:
            notice_poller.mark_seen()
        cat_widget.set_notice_indicator(False)

    cat_widget.set_notice_callback(open_dashboard_home)
    tray_manager = TrayManager(cat_widget, dashboard, context_manager)

    if context_manager:
        notice_poller = NoticePoller(on_new_notice=lambda has_new: cat_widget.set_notice_indicator(has_new))
        dashboard.logged_in.connect(lambda token, user_id: notice_poller.set_token(token) or notice_poller.start())
        dashboard.logged_out.connect(notice_poller.stop)
        dashboard.session_invalid.connect(notice_poller.stop)
        app.aboutToQuit.connect(notice_poller.stop)

    exit_code = app.exec()
    # Ensure clean shutdown
    if context_manager:
        context_manager.stop()
    if notice_poller:
        notice_poller.stop()
    tray_manager.tray.hide()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
