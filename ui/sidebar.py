import os
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from .theme_colors import SURFACE, ACCENT_BLUE, TEXT_DARK, SIDEBAR_SELECTED_TEXT, BORDER_SUBTLE

PAGES = ["Dashboard", "Device Control", "Communication"]

_ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "pages")
_ICON_DIR_DARK = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "pages_dark")
_ICON_FILES = {
    "Dashboard": "dashboard.png",
    "Device Control": "device_control.png",
    "Communication": "communication.png",
}


def _build_icon(filename: str) -> QIcon:
    """
    Blue icon for the normal (unselected) state, dark navy icon for the
    Selected state — the row's background flips to accent-blue when
    selected, so the icon needs to flip to dark too, or it just blends
    into the highlight and disappears.
    """
    icon = QIcon()
    normal_path = os.path.join(_ICON_DIR, filename)
    selected_path = os.path.join(_ICON_DIR_DARK, filename)
    size = QSize(64, 64)
    if os.path.exists(normal_path):
        icon.addFile(normal_path, size, QIcon.Normal, QIcon.Off)
    if os.path.exists(selected_path):
        icon.addFile(selected_path, size, QIcon.Selected, QIcon.Off)
    return icon


class Sidebar(QListWidget):
    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.setFocusPolicy(Qt.NoFocus)  # stops Qt drawing a focus box around the selected item
        self.setIconSize(QSize(20, 20))
        self.setStyleSheet(
            f"QListWidget {{ background: {SURFACE}; color: {TEXT_DARK}; border: none; "
            f"border-right: 1px solid {BORDER_SUBTLE}; font-size: 14px; outline: 0; }}"
            f"QListWidget::item {{ padding: 14px 16px; border: none; outline: 0; }}"
            f"QListWidget::item:selected {{ background: {ACCENT_BLUE}; color: {SIDEBAR_SELECTED_TEXT}; font-weight: 700; border: none; outline: 0; }}"
            f"QListWidget::item:focus {{ border: none; outline: 0; }}"
        )
        for name in PAGES:
            item = QListWidgetItem(name)
            item.setIcon(_build_icon(_ICON_FILES[name]))
            self.addItem(item)
        self.setCurrentRow(0)
        self.currentTextChanged.connect(self.page_selected.emit)

    def row_height(self) -> int:
        """
        The real, live-computed height of a sidebar row — depends on font
        metrics and padding, which vary by OS/DPI/font rendering. Query
        this directly rather than hardcoding a number measured on one
        machine, or the page header will drift out of alignment with the
        sidebar on any machine that computes row height differently.
        """
        if self.count() > 0:
            return self.sizeHintForRow(0)
        return 50  # fallback only reached if the sidebar has no items yet
