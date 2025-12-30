from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView  # type: ignore
    from PyQt6.QtWebEngineCore import QWebEngineSettings  # type: ignore
    _WEBENGINE_IMPORT_ERROR: Optional[Exception] = None
except Exception as e:  # noqa: BLE001
    QWebEngineView = None  # type: ignore
    QWebEngineSettings = None  # type: ignore
    _WEBENGINE_IMPORT_ERROR = e

from app.api_client import ApiClient
from app.token_store import clear_token, load_token, save_token
from app.worker import Worker


class DashboardWindow(QWidget):
    logged_in = pyqtSignal(str, str)  # token, user_id
    logged_out = pyqtSignal()
    session_invalid = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MeowBuddy Dashboard")
        # 로그인 전 기본 크기
        self.resize(960, 720)
        self.setMinimumSize(900, 600)
        self._set_window_icon()

        self.api = ApiClient()
        self.login_thread: Optional[QThread] = None
        self.me_thread: Optional[QThread] = None
        self.web_view: Optional[QWebEngineView] = None  # type: ignore[valid-type]

        self._build_ui()
        self._load_token_auto()

    def _set_window_icon(self) -> None:
        candidates = [
            Path(__file__).resolve().parent / "web" / "dist" / "favicon.svg",
            Path(__file__).resolve().parent / "web" / "public" / "favicon.svg",
        ]
        for p in candidates:
            if p.exists():
                self.setWindowIcon(QIcon(str(p)))
                break

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # Login panel
        self.login_panel = QWidget()
        login_layout = QVBoxLayout(self.login_panel)

        title = QLabel("Login")
        title.setStyleSheet("font-weight:600; font-size:16px;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.login_btn = QPushButton("Login")
        self.login_status = QLabel("")
        self.login_status.setStyleSheet("color:#c00;")

        self.login_btn.clicked.connect(self._on_login_clicked)

        login_layout.addWidget(title)
        login_layout.addWidget(self.email_input)
        login_layout.addWidget(self.login_btn)
        login_layout.addWidget(self.login_status)
        login_layout.addStretch()

        # Web container
        self.web_container = QWidget()
        web_layout = QVBoxLayout(self.web_container)
        web_layout.setContentsMargins(0, 0, 0, 0)

        self.web_status = QLabel("")
        self.web_status.setStyleSheet("color:#555;")
        web_layout.addWidget(self.web_status)

        if not self._ensure_web_view():
            msg = (
                "WebEngine이 없어 대시보드를 표시할 수 없습니다.\n\n"
                "1) venv에서 설치: pip install -U PyQt6 PyQt6-WebEngine\n\n"
                f"Import error: {_WEBENGINE_IMPORT_ERROR}"
            )
            self.web_status.setText(msg)
        else:
            web_layout.addWidget(self.web_view, stretch=1)  # type: ignore[arg-type]

        layout.addWidget(self.login_panel)
        layout.addWidget(self.web_container, stretch=1)

        # 초기에는 로그인 화면만 보여줌
        self.web_container.setVisible(False)
        self.setLayout(layout)

    def _ensure_web_view(self) -> bool:
        if self.web_view is not None:
            return True
        if QWebEngineView is None:
            return False

        self.web_view = QWebEngineView()

        if QWebEngineSettings is not None:
            s = self.web_view.settings()
            web_attr = getattr(QWebEngineSettings, "WebAttribute", None)

            def set_attr(name: str, value: bool) -> None:
                if not web_attr:
                    return
                attr = getattr(web_attr, name, None)
                if attr is not None:
                    s.setAttribute(attr, value)

            set_attr("WebGLEnabled", False)
            set_attr("Accelerated2dCanvasEnabled", False)
            set_attr("LocalContentCanAccessFileUrls", True)
            set_attr("LocalContentCanAccessRemoteUrls", True)
            set_attr("DeveloperExtrasEnabled", False)

        self.web_view.loadFinished.connect(self._on_load_finished)
        try:
            self.web_view.renderProcessTerminated.connect(self._on_render_terminated)  # type: ignore[attr-defined]
        except Exception:
            pass

        return True

    # ---- Auth ----
    def _load_token_auto(self) -> None:
        token = load_token()
        if not token:
            return
        self.api.set_token(token)
        self._fetch_me(token)

    def _on_login_clicked(self) -> None:
        email = self.email_input.text().strip()
        if not email:
            self.login_status.setText("Email is required.")
            return
        if self.login_thread and self.login_thread.isRunning():
            self.login_status.setText("Loading...")
            return
        self.login_status.setText("Loading...")

        login_thread = QThread()
        worker = Worker(lambda: self.api.login(email))
        worker.moveToThread(login_thread)
        worker.finished.connect(lambda result, error: self._on_login_finished(login_thread, worker, result, error))
        login_thread.started.connect(worker.run)
        login_thread.start()
        self.login_thread = login_thread

    def _on_login_finished(self, thread: QThread, worker: Worker, result, error) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.login_thread = None

        if error:
            self.login_status.setText(f"Login failed: {error}")
            return

        token = (result or {}).get("access_token")
        if not token:
            self.login_status.setText("Login failed: token missing.")
            return

        save_token(token)
        self.api.set_token(token)
        self.login_status.setText("")
        self._fetch_me(token)

    def _fetch_me(self, token: str) -> None:
        if self.me_thread and self.me_thread.isRunning():
            self.me_thread.quit()
            self.me_thread.wait()

        thread = QThread()
        worker = Worker(self.api.me)
        worker.moveToThread(thread)
        worker.finished.connect(lambda result, error: self._on_me_finished(thread, worker, result, error, token))
        thread.started.connect(worker.run)
        thread.start()
        self.me_thread = thread

    def _on_me_finished(self, thread: QThread, worker: Worker, result, error, token: str) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.me_thread = None

        if error:
            clear_token()
            self.api.set_token(None)
            self.session_invalid.emit()
            self.login_status.setText(f"Session invalid: {error}")
            return

        user_id = (result or {}).get("user_id", "")
        self.logged_in.emit(token, user_id)

        self.login_panel.setVisible(False)
        self.web_container.setVisible(True)
        # 로그인 후 한눈에 보이도록 확대
        if self.width() < 1200:
            self.resize(1280, 900)
        if self.minimumWidth() < 1100 or self.minimumHeight() < 800:
            self.setMinimumSize(1100, 800)

        self.open_home()

    # ---- Web ----
    def open_home(self) -> None:
        if self.web_view is None:
            return

        dev_url = os.environ.get("MEOWBUDDY_DASHBOARD_URL", "").strip()
        if dev_url:
            self.web_view.setUrl(QUrl(dev_url))
            self.web_status.setText("")
            return

        dist_index = Path(__file__).resolve().parent / "web" / "dist" / "index.html"
        if not dist_index.exists():
            self.web_status.setText(
                "대시보드 빌드 파일이 없습니다.\n"
                "app/web에서 npm run build 실행 후 다시 시도해주세요.\n\n"
                f"expected: {dist_index}"
            )
            return

        self.web_view.setUrl(QUrl.fromLocalFile(str(dist_index)))
        self.web_status.setText("")

    def _on_load_finished(self, ok: bool) -> None:
        if ok:
            return
        url = self.web_view.url().toString() if self.web_view else ""
        QMessageBox.warning(self, "Dashboard Load Failed", f"Failed to load:\n{url}")

    def _on_render_terminated(self, *args, **kwargs) -> None:  # noqa: ANN001, D401
        # 렌더 프로세스 종료 시 단순히 상태만 보여줌
        QMessageBox.warning(self, "Dashboard", "렌더러가 중단되어 페이지를 다시 로드합니다.")
        self.open_home()

    def logout(self) -> None:
        clear_token()
        self.api.set_token(None)
        self.logged_out.emit()
        self.web_container.setVisible(False)
        self.login_panel.setVisible(True)

    def show_login(self) -> None:
        self.logout()
