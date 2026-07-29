from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from ..theme_colors import ACCENT_BLUE, TEXT_MUTED, TEXT_LIGHT, DIALOG_BG, BORDER_SUBTLE


class StatusCard(QWidget):
    def __init__(self, title: str, value: str = "—", parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; background: transparent;"
        )
        outer.addWidget(self.title_label)

        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.StyledPanel)
        self.card_frame.setAttribute(Qt.WA_StyledBackground, True)
        self.card_frame.setStyleSheet(
            f"QFrame {{ background: {DIALOG_BG}; border: 1px solid {BORDER_SUBTLE}; border-radius: 8px; }}"
        )
        card_row = QHBoxLayout(self.card_frame)
        card_row.setContentsMargins(0, 0, 12, 0)
        card_row.setSpacing(10)

        stripe = QFrame()
        stripe.setFixedWidth(4)
        stripe.setAttribute(Qt.WA_StyledBackground, True)
        stripe.setStyleSheet(
            f"background: {ACCENT_BLUE}; border-top-left-radius: 8px; "
            f"border-bottom-left-radius: 8px;"
        )
        card_row.addWidget(stripe)

        value_container = QVBoxLayout()
        value_container.setContentsMargins(0, 10, 0, 10)
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {TEXT_LIGHT}; font-size: 20px; font-weight: 700; background: transparent;"
        )
        self.value_label.setAlignment(Qt.AlignLeft)
        value_container.addWidget(self.value_label)
        card_row.addLayout(value_container)

        outer.addWidget(self.card_frame)

    def set_value(self, value: str):
        self.value_label.setText(value)
