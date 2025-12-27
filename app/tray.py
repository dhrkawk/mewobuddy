from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QAction, QGuiApplication, QIcon
from PyQt6.QtWidgets import QMenu, QMessageBox, QStyle, QSystemTrayIcon

from desktopcat.core.context_manager import ContextManager
from desktopcat.ui.widget import CatWidget
from app.dashboard import DashboardWindow


class TrayManager(QObject):
    """System tray icon and menu."""

    def __init__(
        self,
        cat_widget: CatWidget,
        dashboard: DashboardWindow,
        context_manager: Optional[ContextManager] = None,
    ) -> None:
        super().__init__()
        self.cat_widget = cat_widget
        self.dashboard = dashboard
        self.context_manager = context_manager

        self.tray = QSystemTrayIcon(self._default_icon(), self)
        self.tray.setToolTip("MeowBuddy")

        self.menu = QMenu()
        self.action_open_dashboard = QAction("Open Dashboard", self)
        self.action_open_dashboard.triggered.connect(self._show_dashboard)
        self.menu.addAction(self.action_open_dashboard)

        self.action_toggle_cat = QAction(self._toggle_text(), self)
        self.action_toggle_cat.triggered.connect(self._toggle_cat_visibility)
        self.menu.addAction(self.action_toggle_cat)

        self.action_check_updates = QAction("Check Updates", self)
        self.action_check_updates.triggered.connect(self._check_updates)
        self.menu.addAction(self.action_check_updates)

        self.menu.addSeparator()

        self.action_quit = QAction("Quit", self)
        self.action_quit.triggered.connect(self._quit)
        self.menu.addAction(self.action_quit)

        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def _default_icon(self) -> QIcon:
        app = QGuiApplication.instance()
        if app:
            return app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        return QIcon()

    def _show_dashboard(self) -> None:
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def _toggle_text(self) -> str:
        return "Hide Cat" if self.cat_widget.isVisible() else "Show Cat"

    def _toggle_cat_visibility(self) -> None:
        now_visible = not self.cat_widget.isVisible()
        self.cat_widget.setVisible(now_visible)
        self.action_toggle_cat.setText(self._toggle_text())

    def _check_updates(self) -> None:
        QMessageBox.information(None, "Updates", "Update check not implemented yet.")

    def _quit(self) -> None:
        if self.context_manager:
            self.context_manager.stop()
        self.cat_widget.close()
        self.dashboard.close()
        self.tray.hide()
        app = QGuiApplication.instance()
        if app:
            app.quit()
