"""
Reusable page header. Spans the full width of the page (BasePage gives it
a zero-margin outer layout to make this true) — same navy background as
the sidebar, with a thin bottom divider. Height matches the sidebar's
active row height (50px, confirmed via Sidebar.visualItemRect) so the
header lines up visually with the sidebar rather than having an
arbitrary height of its own.

Includes a Close Application button on the right — emits `close_requested`
so whatever owns this header (BasePage) decides what closing actually
means (this widget itself has no app/connection knowledge). It's a plain
icon button, not a logout — this app has no accounts/sessions, so
"logout" never described what it actually does.
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, Signal, QSize

from ..theme_colors import NAVY, TEXT_LIGHT, BORDER_SUBTLE_DARK, STATUS_ERROR

_ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "pages")

_ICON_FILES = {
    "dashboard": "dashboard.png",
    "device_control": "device_control.png",
    "communication": "communication.png",
}

ICON_SIZE = 22
CLOSE_ICON_SIZE = 18
CLOSE_BTN_SIZE = 34
DEFAULT_HEIGHT = 50  # only used as a fallback if never synced to the real sidebar height


def _tint_pixmap(pixmap: QPixmap, color: str) -> QPixmap:
    """Recolor a monochrome icon's opaque pixels to `color`, keeping its alpha."""
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.transparent)
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color))
    painter.end()
    return tinted


class PageHeader(QWidget):
    close_requested = Signal()

    def __init__(self, title: str, icon_key: str, parent=None):
        super().__init__(parent)
        # Plain QWidget subclasses don't paint stylesheet background/border
        # by default — this attribute is required or the rule below does
        # nothing (confirmed previously by rendering + pixel check).
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setObjectName("PageHeader")
        self.setStyleSheet(
            f"#PageHeader {{ background: {NAVY}; "
            f"border-bottom: 1px solid {BORDER_SUBTLE_DARK}; }}"
        )
        self.setFixedHeight(DEFAULT_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 6, 16, 6)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_path = os.path.join(_ICON_DIR, _ICON_FILES.get(icon_key, ""))
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(
                ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {TEXT_LIGHT}; font-size: 17px; font-weight: 700; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addStretch()

        self.close_btn = QPushButton()
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Close Application")
        self.close_btn.setFixedSize(CLOSE_BTN_SIZE, CLOSE_BTN_SIZE)
        close_icon_path = os.path.join(_ICON_DIR, "logout.png")
        if os.path.exists(close_icon_path):
            red_icon = _tint_pixmap(
                QPixmap(close_icon_path).scaled(
                    CLOSE_ICON_SIZE, CLOSE_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ),
                STATUS_ERROR,
            )
            self.close_btn.setIcon(QIcon(red_icon))
            self.close_btn.setIconSize(QSize(CLOSE_ICON_SIZE, CLOSE_ICON_SIZE))
        self.close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"border-radius: {CLOSE_BTN_SIZE // 2}px; }}"
            f"QPushButton:hover {{ background: rgba(176, 0, 32, 30); }}"
            f"QPushButton:pressed {{ background: rgba(176, 0, 32, 60); }}"
        )
        self.close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_btn)
