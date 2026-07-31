from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from ..theme_colors import DIALOG_BG, BORDER_SUBTLE, TEXT_LIGHT


class SectionCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("SectionCard")
        self.setStyleSheet(
            f"#SectionCard {{ background: {DIALOG_BG}; border: 1px solid {BORDER_SUBTLE}; "
            f"border-radius: 8px; }}"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {TEXT_LIGHT}; font-size: 13px; font-weight: 700; background: transparent;"
        )
        outer.addWidget(title_label)

        self.body_layout = QVBoxLayout()
        self.body_layout.setSpacing(10)
        outer.addLayout(self.body_layout)
