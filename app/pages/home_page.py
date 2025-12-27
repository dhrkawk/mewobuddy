from __future__ import annotations

from functools import partial
from typing import Optional, List, Dict

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QFrame,
)

from app.api_client import ApiClient
from app.worker import Worker


class NoticeCard(QFrame):
    def __init__(self, notice: dict):
        super().__init__()
        self.notice = notice
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            """
            QFrame {
                background: #ffffff;
                border: 1px solid #e5e5e8;
                border-radius: 12px;
            }
            """
        )
        layout = QVBoxLayout()
        title = QLabel(notice.get("title", ""))
        title.setStyleSheet("font-weight: 600; font-size: 15px;")
        content = QLabel(self._preview(notice.get("content", "")))
        content.setWordWrap(True)
        date = QLabel(notice.get("created_at", ""))
        date.setAlignment(Qt.AlignmentFlag.AlignRight)
        date.setStyleSheet("color: #777; font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(content)
        layout.addWidget(date)
        self.setLayout(layout)

    def _preview(self, text: str, length: int = 120) -> str:
        return text if len(text) <= length else text[:length] + "…"


class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.api = ApiClient()
        self.current_thread: Optional[QThread] = None
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Left: Notices + Streams placeholder
        left = QVBoxLayout()
        header = QLabel("Latest Announcements")
        header.setStyleSheet("font-weight: 600; font-size: 16px;")
        left.addWidget(header)

        self.notice_list = QListWidget()
        self.notice_list.setSpacing(8)
        self.notice_list.itemClicked.connect(self._on_notice_clicked)
        left.addWidget(self.notice_list, stretch=2)

        streams_label = QLabel("Recent Streams")
        streams_label.setStyleSheet("font-weight: 600; font-size: 16px; margin-top:8px;")
        left.addWidget(streams_label)

        self.streams_list = QListWidget()
        self.streams_list.setSpacing(6)
        left.addWidget(self.streams_list, stretch=1)

        # Right: Featured clips placeholder
        right = QVBoxLayout()
        right_header = QLabel("Featured Clips")
        right_header.setStyleSheet("font-weight: 600; font-size: 16px;")
        right.addWidget(right_header)

        self.clips_area = QScrollArea()
        self.clips_area.setWidgetResizable(True)
        clip_container = QWidget()
        clip_layout = QVBoxLayout()
        self.clip_label = QLabel("Epic Gaming Moment")
        self.clip_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.clip_image = QLabel()
        self.clip_image.setStyleSheet("background:#eceff3; border-radius:12px; min-height:200px;")
        self.clip_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clip_image.setText("Clip Placeholder")
        clip_layout.addWidget(self.clip_image)
        clip_layout.addWidget(self.clip_label)
        clip_container.setLayout(clip_layout)
        self.clips_area.setWidget(clip_container)
        right.addWidget(self.clips_area)

        main_layout.addLayout(left, stretch=3)
        main_layout.addLayout(right, stretch=2)
        self.setLayout(main_layout)

        self._load_mock_streams()

    def set_token(self, token: Optional[str]) -> None:
        self.api.set_token(token)

    def refresh_notices(self) -> None:
        if self.current_thread and self.current_thread.isRunning():
            return
        thread = QThread()
        worker = Worker(self.api.get_notices)
        worker.moveToThread(thread)
        worker.finished.connect(lambda result, error: self._on_notices_finished(thread, worker, result, error))
        thread.started.connect(worker.run)
        thread.start()
        self.current_thread = thread

    def _on_notices_finished(self, thread: QThread, worker: Worker, result, error) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.current_thread = None

        if error:
            QMessageBox.warning(self, "Notice Error", f"Failed to load notices: {error}")
            return
        self._render_notices(result or [])

    def _render_notices(self, notices: List[Dict]) -> None:
        self.notice_list.clear()
        if not notices:
            self.notice_list.addItem("아직 공지가 없습니다")
            self.notice_list.setEnabled(False)
            return
        self.notice_list.setEnabled(True)
        for notice in notices:
            item = QListWidgetItem()
            card = NoticeCard(notice)
            item.setSizeHint(card.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, notice)
            self.notice_list.addItem(item)
            self.notice_list.setItemWidget(item, card)

    def _on_notice_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return
        title = data.get("title", "")
        content = data.get("content", "")
        created_at = data.get("created_at", "")
        QMessageBox.information(self, title, f"{created_at}\n\n{content}")

    def _load_mock_streams(self) -> None:
        streams = [
            {"title": "Cozy Gaming Night - Part 3", "date": "Dec 26", "length": "2:45:30"},
            {"title": "Holiday Special Stream! 🎄", "date": "Dec 25", "length": "3:12:15"},
        ]
        self.streams_list.clear()
        for s in streams:
            item = QListWidgetItem(f"{s['title']}   ({s['date']}, {s['length']})")
            self.streams_list.addItem(item)
