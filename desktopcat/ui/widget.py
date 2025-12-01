from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl, QEvent
from PyQt6.QtGui import QGuiApplication, QMovie, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QSizeGrip, QStackedLayout, QVBoxLayout, QWidget, QSizePolicy

from desktopcat.core.asset_manager import AssetDescriptor


class CatWidget(QWidget):
    """
    Minimal floating widget:
    - Frameless, always-on-top, transparent background
    - Draggable + resizable
    - Shows PNG/JPG/GIF (animates via QMovie) or MP4 via QMediaPlayer
    - No shape masking: transparent background + rectangular window
    """

    def __init__(self, asset: AssetDescriptor, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.asset = asset
        self.dragging = False
        self.drag_position = QPoint()
        self.movie: Optional[QMovie] = None
        self.media_player: Optional[QMediaPlayer] = None
        self.audio_output: Optional[QAudioOutput] = None
        self.drag_overlay: Optional[QWidget] = None

        self._setup_window()
        self._build_ui()
        self.load_asset(asset)

        QTimer.singleShot(0, self.move_to_top_right)

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.resize(260, 260)

    def _build_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.content_widget = QWidget(self)
        self.content_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QStackedLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Image/GIF display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setScaledContents(True)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.content_layout.addWidget(self.image_label)

        # Video display
        self.video_widget = QVideoWidget(self)
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.video_widget.setStyleSheet("background: transparent;")
        self.video_widget.installEventFilter(self)
        self.content_layout.addWidget(self.video_widget)

        self.layout.addWidget(self.content_widget)

        # Size grip for resizing
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent;")
        self.layout.addWidget(self.size_grip, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Close button
        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(22, 22)
        self.close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 0, 0, 160);
                color: white;
                border: none;
                border-radius: 11px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(0, 0, 0, 200); }
            QPushButton:pressed { background-color: rgba(0, 0, 0, 230); }
            """
        )
        self.close_button.clicked.connect(self._handle_close)
        self._position_close_button()

        # Transparent overlay to capture drag over video
        self.drag_overlay = QWidget(self)
        self.drag_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.drag_overlay.setStyleSheet("background: transparent;")
        self.drag_overlay.installEventFilter(self)
        self._update_drag_overlay_geometry()
        self._raise_controls()

    def _raise_controls(self) -> None:
        self.drag_overlay.raise_()
        self.close_button.raise_()
        self.size_grip.raise_()

    def load_asset(self, asset: AssetDescriptor) -> None:
        self.asset = asset
        if asset.media_type == "video":
            self._show_video(asset.path)
        else:
            self._show_image_or_gif(asset.path, asset.media_type)

    def _show_image_or_gif(self, path: Path, media_type: str) -> None:
        self._stop_video()
        if media_type == "gif":
            self.movie = QMovie(str(path))
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.setScaledSize(self.size())
            self.image_label.setMovie(self.movie)
            self.movie.start()
        else:
            pixmap = QPixmap(str(path))
            self.image_label.setPixmap(pixmap)
            self.image_label.setMovie(None)
            self._update_scaled_media()

        self.content_layout.setCurrentWidget(self.image_label)

    def _show_video(self, path: Path) -> None:
        self._stop_gif()
        if not self.media_player:
            self.media_player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setVideoOutput(self.video_widget)

        self.media_player.setSource(QUrl.fromLocalFile(str(path)))
        loops_value = getattr(QMediaPlayer.Loops, "Infinite", 0)
        self.media_player.setLoops(loops_value)
        self.content_layout.setCurrentWidget(self.video_widget)
        self.media_player.play()

    def _stop_gif(self) -> None:
        if self.movie:
            self.movie.stop()
            self.movie = None
            self.image_label.setMovie(None)

    def _stop_video(self) -> None:
        if self.media_player:
            self.media_player.stop()

    def move_to_top_right(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geom = screen.availableGeometry()
        x = geom.right() - self.width() - 10
        y = geom.top() + 10
        self.move(x, y)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:
        self._update_scaled_media()
        self._position_close_button()
        self._update_drag_overlay_geometry()
        self._raise_controls()
        super().resizeEvent(event)

    def _update_scaled_media(self) -> None:
        if self.movie:
            self.movie.setScaledSize(self.size())
        else:
            pixmap = self.image_label.pixmap()
            if pixmap:
                scaled = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled)

    def eventFilter(self, obj, event):
        overlay = self.drag_overlay
        if obj in (self.video_widget, overlay) and event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonRelease,
        ):
            if event.type() == QEvent.Type.MouseButtonPress:
                self.mousePressEvent(event)
            elif event.type() == QEvent.Type.MouseMove:
                self.mouseMoveEvent(event)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.mouseReleaseEvent(event)
            return True
        return super().eventFilter(obj, event)

    def _position_close_button(self) -> None:
        margin = 6
        x = self.width() - self.close_button.width() - margin
        y = margin
        self.close_button.move(max(x, margin), y)

    def _handle_close(self) -> None:
        self._stop_video()
        self._stop_gif()
        app = QApplication.instance()
        if app:
            app.quit()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._stop_video()
        self._stop_gif()
        super().closeEvent(event)

    def _update_drag_overlay_geometry(self) -> None:
        self.drag_overlay.setGeometry(self.rect())
