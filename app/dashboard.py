from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QMessageBox,
)

from app.api_client import ApiClient
from app.pages.home_page import HomePage
from app.pages.inventory_page import InventoryPage
from app.pages.settings_page import SettingsPage
from app.token_store import clear_token, load_token, save_token
from app.worker import Worker
from functools import partial


class DashboardWindow(QWidget):
    logged_in = pyqtSignal(str, str)  # token, user_id
    logged_out = pyqtSignal()
    session_invalid = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MeowBuddy Dashboard")
        self.api = ApiClient()
        self.login_thread: Optional[QThread] = None
        self.me_thread: Optional[QThread] = None

        self.home_page = HomePage()
        self.inventory_page = InventoryPage()
        self.settings_page = SettingsPage()

        self._build_ui()
        self._show_login()
        self._load_token_auto()

    def _build_ui(self) -> None:
        outer = QVBoxLayout()
        outer.setContentsMargins(12, 12, 12, 12)
        # Header with logo/title and nav
        header = QHBoxLayout()
        logo = QLabel("🐱 MeowBuddy")
        logo.setStyleSheet("font-weight: 700; font-size: 18px;")
        subtitle = QLabel("Desktop Widget Dashboard")
        subtitle.setStyleSheet("color:#555;")
        title_box = QVBoxLayout()
        title_box.addWidget(logo)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.btn_home = QPushButton("Home")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_settings = QPushButton("Settings")
        for b in (self.btn_home, self.btn_inventory, self.btn_settings):
            b.setCheckable(True)
        self.btn_home.clicked.connect(lambda: self._set_page(0))
        self.btn_inventory.clicked.connect(lambda: self._set_page(1))
        self.btn_settings.clicked.connect(lambda: self._set_page(2))
        header.addWidget(self.btn_home)
        header.addWidget(self.btn_inventory)
        header.addWidget(self.btn_settings)

        outer.addLayout(header)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.inventory_page)
        self.stack.addWidget(self.settings_page)
        outer.addWidget(self.stack, stretch=1)

        # Login panel
        self.login_panel = QWidget()
        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(12, 12, 12, 12)
        login_title = QLabel("Login")
        login_title.setStyleSheet("font-weight:600; font-size:16px;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.login_btn = QPushButton("Login")
        self.login_status = QLabel("")
        self.login_status.setStyleSheet("color:red;")
        login_layout.addWidget(login_title)
        login_layout.addWidget(self.email_input)
        login_layout.addWidget(self.login_btn)
        login_layout.addWidget(self.login_status)
        login_layout.addStretch()
        self.login_panel.setLayout(login_layout)
        outer.addWidget(self.login_panel)

        self.login_btn.clicked.connect(self._on_login_clicked)
        self.settings_page.logout_clicked.connect(self.logout)

        self.setLayout(outer)
        self._set_page(0)
        self.stack.setVisible(False)

    def _load_token_auto(self) -> None:
        self.load_token_and_login()

    def _set_page(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        self.btn_home.setChecked(idx == 0)
        self.btn_inventory.setChecked(idx == 1)
        self.btn_settings.setChecked(idx == 2)

    # Login flow (reuse previous network calls)
    def _on_login_clicked(self) -> None:
        email = self.email_input.text().strip()
        if not email:
            self.login_status.setText("Email is required.")
            return
        # Avoid overlapping login attempts
        if self.login_thread and self.login_thread.isRunning():
            self.login_status.setText("Loading...")
            return
        self.login_status.setText("Loading...")
        login_thread = QThread()
        worker = Worker(partial(self.api.login, email))
        worker.moveToThread(login_thread)
        worker.finished.connect(
            lambda result, error, t=login_thread, w=worker: self._on_login_finished(t, w, result, error)
        )
        login_thread.started.connect(worker.run)
        login_thread.start()
        self.login_thread = login_thread

    def _on_login_finished(self, thread: QThread, worker: Worker, result, error) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        if self.login_thread is thread:
            self.login_thread = None

        if error:
            self.login_status.setText(f"Login failed: {error}")
            return
        token = result.get("access_token")
        if token:
            save_token(token)
            self.api.set_token(token)
            self.home_page.set_token(token)
            self.login_status.setText("")
            self._fetch_me(token)
        else:
            self.login_status.setText("Login failed: token missing.")

    def _fetch_me(self, token: str) -> None:
        # If a previous /me call is running (e.g., auto-login), stop it and start fresh
        if self.me_thread and self.me_thread.isRunning():
            self.me_thread.quit()
            self.me_thread.wait()
            self.me_thread = None
        thread = QThread()
        worker = Worker(self.api.me)
        worker.moveToThread(thread)
        worker.finished.connect(lambda result, error, t=thread, w=worker: self._on_me_finished(t, w, result, error, token))
        thread.started.connect(worker.run)
        thread.start()
        self.me_thread = thread

    def _on_me_finished(self, thread: QThread, worker: Worker, result, error, token: str) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        if self.me_thread is thread:
            self.me_thread = None

        if error:
            self.login_status.setText(f"Login failed: {error}")
            clear_token()
            self.api.set_token(None)
            self.session_invalid.emit()
            return
        user_id = result.get("user_id", "")
        self.logged_in.emit(token, user_id)
        self.home_page.refresh_notices()
        self.login_panel.setVisible(False)
        self.stack.setVisible(True)

    def load_token_and_login(self) -> None:
        token = load_token()
        if not token:
            return
        self.api.set_token(token)
        self.home_page.set_token(token)
        self._fetch_me(token)

    def logout(self) -> None:
        clear_token()
        self.api.set_token(None)
        self.logged_out.emit()
        self._show_login()

    def _show_login(self) -> None:
        self.login_panel.setVisible(True)
        self.stack.setVisible(False)

    # Exposed for main to open Home and refresh
    def open_home(self) -> None:
        self._set_page(0)
        self.home_page.refresh_notices()
