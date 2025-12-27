from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    logout_clicked = pyqtSignal()

    def __init__(self, app_version: str = "v0.1.0") -> None:
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-weight: 600; font-size: 16px;")
        layout.addWidget(title)

        version = QLabel(f"App Version: {app_version}")
        layout.addWidget(version)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(logout_btn)

        layout.addStretch()
        self.setLayout(layout)
