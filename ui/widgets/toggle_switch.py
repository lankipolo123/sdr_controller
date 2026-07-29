"""
A real iOS-style toggle switch — replaces separate "Output ON"/"Output OFF"
buttons with a single sliding switch. Built on QCheckBox so it keeps the
standard checked/unchecked state and `toggled(bool)` signal for free;
only the painting is custom.
"""

from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor

from ..theme_colors import ACCENT_BLUE, BORDER_SUBTLE

WIDTH = 52
HEIGHT = 28
KNOB_MARGIN = 3


class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(WIDTH, HEIGHT)
        # Suppress Qt's default checkbox indicator/text box entirely —
        # this widget paints itself completely in paintEvent below.
        self.setStyleSheet("QCheckBox::indicator { width: 0px; height: 0px; }")
        self.setText("")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_color = QColor(ACCENT_BLUE) if self.isChecked() else QColor(BORDER_SUBTLE)
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        radius = HEIGHT / 2
        painter.drawRoundedRect(QRectF(0, 0, WIDTH, HEIGHT), radius, radius)

        knob_d = HEIGHT - (KNOB_MARGIN * 2)
        knob_x = WIDTH - knob_d - KNOB_MARGIN if self.isChecked() else KNOB_MARGIN
        painter.setBrush(QColor("white"))
        painter.drawEllipse(QRectF(knob_x, KNOB_MARGIN, knob_d, knob_d))
