"""
Reusable page header. Spans the full width of the page (BasePage gives it
a zero-margin outer layout to make this true) — same navy background as
the sidebar, with a thin bottom divider. Height matches the sidebar's
active row height (50px, confirmed via Sidebar.visualItemRect) so the
header lines up visually with the sidebar rather than having an
arbitrary height of its own.

Includes a Logout button on the right — emits `logout_requested` so
whatever owns this header (BasePage) decides what logging out actually
means (this widget itself has no app/connection knowledge).
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize

from ..theme_colors import NAVY, ACCENT_BLUE, TEXT_LIGHT, BORDER_SUBTLE, STATUS_ERROR, STATUS_ERROR_DARK

_ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "pages")

_ICON_FILES = {
    "dashboard": "dashboard.png",
    "device_control": "device_control.png",
    "status": "status.png",
    "communication": "communication.png",
    "settings": "settings.png",
}

ICON_SIZE = 22
LOGOUT_ICON_SIZE = 18
LOGOUT_BTN_SIZE = 34
DEFAULT_HEIGHT = 50  # only used as a fallback if never synced to the real sidebar height


class PageHeader(QWidget):
    logout_requested = Signal()

    def __init__(self, title: str, icon_key: str, parent=None):
        super().__init__(parent)
        # Plain QWidget subclasses don't paint stylesheet background/border
        # by default — this attribute is required or the rule below does
        # nothing (confirmed previously by rendering + pixel check).
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setObjectName("PageHeader")
        self.setStyleSheet(
            f"#PageHeader {{ background: {NAVY}; "
            f"border-bottom: 1px solid {BORDER_SUBTLE}; }}"
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

        self.logout_btn = QPushButton()
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setToolTip("Logout")
        self.logout_btn.setFixedSize(LOGOUT_BTN_SIZE, LOGOUT_BTN_SIZE)
        logout_icon_path = os.path.join(_ICON_DIR, "logout.png")
        if os.path.exists(logout_icon_path):
            self.logout_btn.setIcon(QIcon(logout_icon_path))
            self.logout_btn.setIconSize(QSize(LOGOUT_ICON_SIZE, LOGOUT_ICON_SIZE))
        self.logout_btn.setStyleSheet(
            f"QPushButton {{ background: {STATUS_ERROR}; border: none; "
            f"border-radius: {LOGOUT_BTN_SIZE // 2}px; }}"
            f"QPushButton:hover {{ background: {STATUS_ERROR_DARK}; }}"
            f"QPushButton:pressed {{ background: {STATUS_ERROR_DARK}; }}"
        )
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.logout_btn)
