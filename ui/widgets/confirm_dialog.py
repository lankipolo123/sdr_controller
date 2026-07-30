"""
Reusable themed confirmation dialog — replaces the default OS QMessageBox
(which looked out of place against the app's theme) with a clean,
frameless, rounded panel matching the rest of the UI.

Usage:
    if ConfirmDialog.ask(self, "Close Application",
                          "This will disconnect and close the app.",
                          confirm_text="Close", danger=True):
        ...
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..theme_colors import DIALOG_BG, TEXT_DARK, TEXT_MUTED, ACCENT_BLUE, STATUS_ERROR, BORDER_SUBTLE


class ConfirmDialog(QDialog):
    def __init__(self, parent, title: str, message: str,
                 confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                 danger: bool = False):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self._confirmed = False
        # Explicit minimum size — without this, Qt computes the dialog's
        # size from its contents, which can collapse much smaller than
        # intended on some platforms (confirmed: this caused button labels
        # to render clipped/illegible on a real machine even though it
        # looked fine in testing). Never rely on implicit sizing for
        # anything that needs to stay legible.
        self.setMinimumWidth(340)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)  # room for the drop shadow

        panel = QLabel()  # plain container widget, not actually showing text
        panel.setObjectName("ConfirmPanel")
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setMinimumWidth(340)
        panel.setStyleSheet(
            f"#ConfirmPanel {{ background: {DIALOG_BG}; border-radius: 12px; "
            f"border: 1px solid {BORDER_SUBTLE}; }}"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        panel.setGraphicsEffect(shadow)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(24, 20, 24, 20)
        panel_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {TEXT_DARK}; font-size: 17px; font-weight: 700; background: transparent;"
        )
        panel_layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setMinimumWidth(292)  # 340 - (24+24) panel margins
        message_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        panel_layout.addWidget(message_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumSize(90, 32)
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {TEXT_DARK}; "
            f"border: 1px solid {BORDER_SUBTLE}; border-radius: 4px; padding: 6px 16px; }}"
            f"QPushButton:hover {{ border-color: {TEXT_DARK}; }}"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        confirm_color = STATUS_ERROR if danger else ACCENT_BLUE
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setMinimumSize(90, 32)
        confirm_btn.setStyleSheet(
            f"QPushButton {{ background: {confirm_color}; color: white; "
            f"border: none; border-radius: 4px; padding: 6px 16px; font-weight: 600; }}"
            f"QPushButton:hover {{ background: {confirm_color}; }}"
        )
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn)

        panel_layout.addLayout(btn_row)
        outer.addWidget(panel)

    def _on_confirm(self):
        self._confirmed = True
        self.accept()

    @staticmethod
    def ask(parent, title: str, message: str,
            confirm_text: str = "Confirm", cancel_text: str = "Cancel",
            danger: bool = False) -> bool:
        dialog = ConfirmDialog(parent, title, message, confirm_text, cancel_text, danger)
        dialog.exec()
        return dialog._confirmed
