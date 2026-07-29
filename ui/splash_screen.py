"""
Splash screen shown while the app initializes.

Reuses the existing app icon and theme_colors palette rather than
introducing new colors — stays consistent with the rest of the app's
plain, un-decorated visual style.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

from . import theme_colors as colors

ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "app_icon.png")

APP_NAME = "SDR Noise Modulator Controller"


class SplashScreen(QWidget):
    """
    Frameless, always-on-top splash widget: centered icon, app name,
    a status line, and a progress bar. Call set_progress() at each real
    init step — the bar reflects actual startup work, not a fake timer.
    """

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setFixedSize(440, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {colors.NAVY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 32)
        layout.setSpacing(10)
        layout.addStretch(1)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(ICON_PATH):
            pixmap = QPixmap(ICON_PATH).scaled(
                96, 96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        title_label = QLabel(APP_NAME)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"color: {colors.TEXT_LIGHT}; font-size: 15px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(title_label)

        layout.addSpacing(12)

        self._status_label = QLabel("Starting...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            f"color: {colors.TEXT_MUTED}; font-size: 11px; background: transparent;"
        )
        layout.addWidget(self._status_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {colors.BORDER_SUBTLE};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.ACCENT_BLUE};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress_bar)

        layout.addStretch(1)

        self._center_on_screen()

    def _center_on_screen(self):
        screen = self.screen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    def set_progress(self, percent: int, status: str):
        """Update progress bar and status text, then force an immediate repaint."""
        self._progress_bar.setValue(percent)
        self._status_label.setText(status)
        self.repaint()
