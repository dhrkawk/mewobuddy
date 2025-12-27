from __future__ import annotations

from __future__ import annotations

from typing import Optional, Callable

from PyQt6.QtCore import QObject, QThread, QTimer
import requests

from app.api_client import ApiClient
from app.notice_state import is_newer, load_last_seen, save_last_seen
from app.worker import Worker


class NoticePoller(QObject):
    """Poll notices periodically and trigger indicator when new items exist."""

    def __init__(self, on_new_notice: Callable[[bool], None], interval_ms: int = 10000) -> None:
        super().__init__()
        self.on_new_notice = on_new_notice
        self.interval_ms = interval_ms
        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self._tick)
        self.api = ApiClient()
        self.current_thread: Optional[QThread] = None
        self.latest_created_at: Optional[str] = None

    def set_token(self, token: Optional[str]) -> None:
        self.api.set_token(token)

    def start(self) -> None:
        if not self.timer.isActive():
            self.timer.start()

    def stop(self) -> None:
        self.timer.stop()
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.quit()
            self.current_thread.wait()
        self.current_thread = None

    def mark_seen(self) -> None:
        if self.latest_created_at:
            save_last_seen(self.latest_created_at)
        self.on_new_notice(False)

    def _tick(self) -> None:
        if self.current_thread and self.current_thread.isRunning():
            return

        def fetch():
            return self.api.get_notices()

        self._run_in_thread(fetch, self._on_finished)

    def _run_in_thread(self, fn, on_done) -> None:
        thread = QThread()
        worker = Worker(fn)
        worker.moveToThread(thread)
        worker.finished.connect(lambda result, error: on_done(thread, worker, result, error))
        thread.started.connect(worker.run)
        thread.start()
        self.current_thread = thread

    def _on_finished(self, thread: QThread, worker: Worker, result, error) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.current_thread = None

        if error:
            if isinstance(error, requests.exceptions.HTTPError) and error.response is not None and error.response.status_code == 401:
                self.on_new_notice(False)
            return

        if not result:
            self.on_new_notice(False)
            return
        latest = result[0].get("created_at")
        self.latest_created_at = latest
        last_seen = load_last_seen()
        has_new = bool(latest and is_newer(latest, last_seen))
        self.on_new_notice(has_new)
