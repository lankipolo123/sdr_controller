from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Qt

from ..theme_colors import card_shadow


def make_card(title: str, accent: str | None = None) -> QGroupBox:
    """A QGroupBox styled as an elevated card (see theme_colors.GLOBAL_QSS
    for the fill/border/radius, and card_shadow() for the drop shadow) —
    use this instead of a bare QGroupBox so every card in the app gets the
    same treatment automatically.

    Pass `accent` (a hex color) to mark a card as visually distinct from
    the rest — e.g. Data Sending vs. Data Receiving — via a colored top
    border and title. Only overrides those two properties; everything
    else still comes from the app-wide QGroupBox style."""
    box = QGroupBox(title)
    box.setAttribute(Qt.WA_StyledBackground, True)
    box.setGraphicsEffect(card_shadow())
    if accent:
        box.setStyleSheet(f"QGroupBox {{ border-top: 3px solid {accent}; color: {accent}; }}")
    return box
