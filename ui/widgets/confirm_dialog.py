"""
Reusable themed confirmation dialog — replaces the default OS QMessageBox
(which looked out of place against the app's theme) with a clean,
rounded panel matching the rest of the UI.

Instead of a drop shadow to separate the panel from the app behind it,
this dims the *entire* app window with a translucent overlay and centers
the panel on top of that — the panel reads as "above" everything because
everything behind it is visibly dimmed, not because of a shadow.

IMPORTANT: this is deliberately NOT a separate top-level QDialog window.
An earlier version made it a frameless translucent QDialog relying on
Qt.WA_TranslucentBackground so the OS compositor would blend its alpha
with the app behind it — that turned out unreliable in practice (solid
black on one machine, fully invisible with no dim at all on another,
depending on platform/compositor quirks). This version is a plain child
QWidget parented directly onto the app's own top-level window, painted
with a semi-transparent fillRect. That's just Qt painting a translucent
color over already-rendered sibling widgets in the same window — no
OS-level window transparency involved — so it renders identically
everywhere.

Usage:
    if ConfirmDialog.ask(self, "Close Application",
                          "This will disconnect and close the app.",
                          confirm_text="Close", danger=True):
        ...
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QEventLoop
from PySide6.QtGui import QColor, QPainter

from ..theme_colors import (
    DIALOG_BG, TEXT_DARK, TEXT_MUTED, ACCENT_BLUE, ACCENT_BLUE_DARK,
    STATUS_ERROR, STATUS_ERROR_DARK, BORDER_SUBTLE,
)

# NAVY (sidebar color) at ~35% opacity. A plain QColor with alpha here,
# not a theme_colors string, because we paint it directly with QPainter
# rather than through a stylesheet.
_OVERLAY_COLOR = QColor(31, 41, 55, 90)


class ConfirmDialog(QWidget):
    def __init__(self, parent, title: str, message: str,
                 confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                 danger: bool = False):
        # Child of the app's own top-level window (not a new window of its
        # own), so it renders as part of the same window instead of a
        # separately-composited one.
        top_level = parent.window() if parent is not None else None
        super().__init__(top_level)
        self._confirmed = False
        self._loop = None

        if top_level is not None:
            self.setGeometry(top_level.rect())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QLabel()  # plain container widget, not actually showing text
        panel.setObjectName("ConfirmPanel")
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setMinimumWidth(340)
        panel.setMaximumWidth(340)
        panel.setStyleSheet(
            f"#ConfirmPanel {{ background: {DIALOG_BG}; border-radius: 12px; "
            f"border: 1px solid {BORDER_SUBTLE}; }}"
        )

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
        cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(cancel_btn)

        confirm_color = STATUS_ERROR if danger else ACCENT_BLUE
        confirm_hover_color = STATUS_ERROR_DARK if danger else ACCENT_BLUE_DARK
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setMinimumSize(90, 32)
        confirm_btn.setStyleSheet(
            f"QPushButton {{ background: {confirm_color}; color: white; "
            f"border: none; border-radius: 4px; padding: 6px 16px; font-weight: 600; }}"
            f"QPushButton:hover {{ background: {confirm_hover_color}; }}"
            f"QPushButton:pressed {{ background: {confirm_hover_color}; }}"
        )
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn)

        panel_layout.addLayout(btn_row)

        # Center the panel within the full-window overlay.
        outer.addStretch()
        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addWidget(panel)
        center_row.addStretch()
        outer.addLayout(center_row)
        outer.addStretch()

    def paintEvent(self, event):
        # Paint the dim scrim ourselves — a plain semi-transparent fill
        # over whatever's already rendered behind this widget (the rest
        # of the app window). No stylesheet, no window-level transparency.
        painter = QPainter(self)
        painter.fillRect(self.rect(), _OVERLAY_COLOR)

    def _on_confirm(self):
        self._confirmed = True
        self._close()

    def _on_cancel(self):
        self._close()

    def _close(self):
        self.hide()
        if self._loop is not None:
            self._loop.quit()

    @staticmethod
    def ask(parent, title: str, message: str,
            confirm_text: str = "Confirm", cancel_text: str = "Cancel",
            danger: bool = False) -> bool:
        dialog = ConfirmDialog(parent, title, message, confirm_text, cancel_text, danger)
        dialog.show()
        dialog.raise_()
        # Block synchronously, same calling convention as the old
        # QDialog.exec() — callers just do `if ConfirmDialog.ask(...):`.
        loop = QEventLoop()
        dialog._loop = loop
        loop.exec()
        confirmed = dialog._confirmed
        dialog.deleteLater()
        return confirmed