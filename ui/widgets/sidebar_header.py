import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ..theme_colors import NAVY, TEXT_LIGHT, BORDER_SUBTLE_DARK

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "app_icon.png")

LOGO_SIZE = 26
HEIGHT = 56


class SidebarHeader(QWidget):
    """App logo + name, sitting above the page-selector list — gives the
    sidebar a proper branded top instead of the nav items starting right
    at the window edge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("SidebarHeader")
        self.setStyleSheet(
            f"#SidebarHeader {{ background: {NAVY}; "
            f"border-bottom: 1px solid {BORDER_SUBTLE_DARK}; "
            f"border-right: 1px solid {BORDER_SUBTLE_DARK}; }}"
        )
        self.setFixedHeight(HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 12, 8)
        layout.setSpacing(10)

        logo_label = QLabel()
        if os.path.exists(_LOGO_PATH):
            pixmap = QPixmap(_LOGO_PATH).scaled(
                LOGO_SIZE, LOGO_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
        logo_label.setStyleSheet("background: transparent;")
        layout.addWidget(logo_label)

        name_label = QLabel("SDR Controller")
        name_label.setWordWrap(True)
        name_label.setStyleSheet(
            f"color: {TEXT_LIGHT}; font-size: 12px; font-weight: 700; background: transparent;"
        )
        layout.addWidget(name_label)
        layout.addStretch()
