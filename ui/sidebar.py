from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from .theme_colors import NAVY, ACCENT_BLUE, TEXT_LIGHT, SIDEBAR_SELECTED_TEXT, BORDER_SUBTLE_DARK
from .widgets.icon_utils import nav_icon_pixmap

PAGES = ["Dashboard", "Device Control", "Communication"]

_ICON_KEYS = {
    "Dashboard": "dashboard",
    "Device Control": "device_control",
    "Communication": "communication",
}

_ICON_SIZE = 20


def _build_icon(icon_key: str) -> QIcon:
    icon = QIcon()
    icon.addPixmap(nav_icon_pixmap(icon_key, _ICON_SIZE, ACCENT_BLUE), QIcon.Normal, QIcon.Off)
    icon.addPixmap(nav_icon_pixmap(icon_key, _ICON_SIZE, SIDEBAR_SELECTED_TEXT), QIcon.Selected, QIcon.Off)
    return icon


class Sidebar(QListWidget):
    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        self.setStyleSheet(
            f"QListWidget {{ background: {NAVY}; color: {TEXT_LIGHT}; border: none; "
            f"border-right: 1px solid {BORDER_SUBTLE_DARK}; font-size: 14px; outline: 0; }}"
            f"QListWidget::item {{ padding: 14px 16px; border: none; outline: 0; }}"
            f"QListWidget::item:selected {{ background: {ACCENT_BLUE}; color: {SIDEBAR_SELECTED_TEXT}; font-weight: 700; border: none; outline: 0; }}"
            f"QListWidget::item:focus {{ border: none; outline: 0; }}"
        )
        for name in PAGES:
            item = QListWidgetItem(name)
            item.setIcon(_build_icon(_ICON_KEYS[name]))
            self.addItem(item)
        self.setCurrentRow(0)
        self.currentTextChanged.connect(self.page_selected.emit)

    def row_height(self) -> int:
        if self.count() > 0:
            return self.sizeHintForRow(0)
        return 50
