import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, QSize

from ..theme_colors import NAVY, TEXT_LIGHT, BORDER_SUBTLE_DARK, STATUS_ERROR_LIGHT
from .icon_utils import nav_icon_pixmap, tint_pixmap

_ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "pages")

ICON_SIZE = 20
CLOSE_ICON_SIZE = 24
CLOSE_BTN_SIZE = 40
DEFAULT_HEIGHT = 50


class PageHeader(QWidget):
    close_requested = Signal()

    def __init__(self, title: str, icon_key: str, parent=None):
        super().__init__(parent)
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
        icon_label.setPixmap(nav_icon_pixmap(icon_key, ICON_SIZE, TEXT_LIGHT))
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
            from PySide6.QtGui import QPixmap
            red_icon = tint_pixmap(
                QPixmap(close_icon_path).scaled(
                    CLOSE_ICON_SIZE, CLOSE_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ),
                STATUS_ERROR_LIGHT,
            )
            self.close_btn.setIcon(QIcon(red_icon))
            self.close_btn.setIconSize(QSize(CLOSE_ICON_SIZE, CLOSE_ICON_SIZE))
        self.close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"border-radius: {CLOSE_BTN_SIZE // 2}px; }}"
            f"QPushButton:hover {{ background: rgba(248, 113, 113, 30); }}"
            f"QPushButton:pressed {{ background: rgba(248, 113, 113, 60); }}"
        )
        self.close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_btn)