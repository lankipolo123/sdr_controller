import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ..theme_colors import card_shadow, TEXT_DARK, BORDER_SUBTLE, ACCENT_BLUE
from .icon_utils import tint_pixmap

_ICON_SIZE = 15
_ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons", "pages")


def _resolve_icon(icon, tint_color: str):
    """`icon` is one of:
    - a "fa5s.icon-name" string -> crisp vector icon via qtawesome (preferred:
      renders at any size with no blur, and tints natively via `color`)
    - any other string -> asset filename (e.g. "logout.png") from assets/icons/pages
    - a QStyle.StandardPixmap enum -> OS-native icon (blurry when scaled/tinted;
      only kept for back-compat, avoid for new icons)
    Returns a tinted QPixmap, or None.
    """
    if icon is None:
        return None
    if isinstance(icon, str) and icon.startswith(("fa5s.", "fa5b.", "fa5r.", "mdi.", "mdi6.")):
        import qtawesome as qta
        return qta.icon(icon, color=tint_color).pixmap(_ICON_SIZE, _ICON_SIZE)
    if isinstance(icon, str):
        path = os.path.join(_ASSET_DIR, icon)
        if not os.path.exists(path):
            return None
        pixmap = QPixmap(path).scaled(
            _ICON_SIZE, _ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
    else:
        style = QApplication.instance().style()
        pixmap = style.standardIcon(icon).pixmap(_ICON_SIZE, _ICON_SIZE)
    return tint_pixmap(pixmap, tint_color)


class Card(QFrame):
    """A real custom card — QFrame, not QGroupBox. Qt's native QGroupBox
    always renders its title cut into the border line no matter what QSS
    is layered on top, which never reads as an actual designed component.
    This builds its own icon+title header row above a body area instead.

    Usage:
        card = Card("Output", icon=QStyle.SP_MediaVolume, accent=ACCENT_BLUE)
        card.body_layout.addWidget(my_widget)
        page_layout.addWidget(card)
    """

    def __init__(self, title: str, icon=None, accent: str | None = None, parent=None):
        super().__init__(parent)
        accent = accent or ACCENT_BLUE
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("Card")
        self.setStyleSheet(
            f"#Card {{ background: #FFFFFF; border: 1px solid {BORDER_SUBTLE}; "
            f"border-radius: 10px; }}"
        )
        self.setGraphicsEffect(card_shadow())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(7)
        pixmap = _resolve_icon(icon, accent)
        if pixmap is not None:
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("background: transparent;")
            header.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {TEXT_DARK}; font-weight: 700; font-size: 12px; background: transparent;"
        )
        header.addWidget(title_label)
        header.addStretch()
        outer.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setSpacing(7)
        outer.addLayout(self.body_layout)


def make_card(title: str, icon=None, accent: str | None = None) -> Card:
    return Card(title, icon=icon, accent=accent)