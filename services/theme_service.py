"""
Applies a real light/dark palette to the whole application.
Uses Qt's Fusion style, which (unlike native styles) actually respects
QPalette changes consistently across every standard widget.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


def _dark_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(30, 30, 30))
    p.setColor(QPalette.WindowText, QColor(230, 230, 230))
    p.setColor(QPalette.Base, QColor(24, 24, 24))
    p.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    p.setColor(QPalette.ToolTipBase, QColor(230, 230, 230))
    p.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
    p.setColor(QPalette.Text, QColor(230, 230, 230))
    p.setColor(QPalette.Button, QColor(45, 45, 45))
    p.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    p.setColor(QPalette.BrightText, QColor(255, 60, 60))
    p.setColor(QPalette.Link, QColor(100, 170, 255))
    p.setColor(QPalette.Highlight, QColor(70, 110, 170))
    p.setColor(QPalette.HighlightedText, Qt.white)
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    return p


def apply_theme(app: QApplication, theme: str):
    app.setStyle("Fusion")
    if theme == "dark":
        app.setPalette(_dark_palette())
    else:
        app.setPalette(app.style().standardPalette())
