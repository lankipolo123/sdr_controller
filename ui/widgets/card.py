from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Qt

from ..theme_colors import card_shadow


def make_card(title: str) -> QGroupBox:
    """A QGroupBox styled as an elevated card (see theme_colors.GLOBAL_QSS
    for the fill/border/radius, and card_shadow() for the drop shadow) —
    use this instead of a bare QGroupBox so every card in the app gets the
    same treatment automatically."""
    box = QGroupBox(title)
    box.setAttribute(Qt.WA_StyledBackground, True)
    box.setGraphicsEffect(card_shadow())
    return box
