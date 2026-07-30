"""
Drop-in replacement for QComboBox that fixes two default Qt behaviors:

1. Popup direction: Qt's default QComboBox tries to position its popup so
   the *currently selected row* lines up with the box — which, for an item
   near the bottom of the list, can make the popup open upward or jump to
   an unexpected position instead of just appearing directly below the box
   like a normal dropdown. showPopup() is overridden here to always move
   the popup to directly beneath the box after Qt opens it.

2. Selected-item indicator: shows a checkmark next to the currently
   selected value in the list (in addition to the existing blue highlight
   from GLOBAL_QSS), like a picker — rather than relying on highlight
   color alone to show what's selected.

Use this instead of QComboBox everywhere in the app for a consistent feel.
"""

from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QIcon
import qtawesome as qta

from ..theme_colors import ACCENT_BLUE

_check_icon = None


def _checkmark_icon():
    # Built lazily (needs a live QApplication, same constraint as any
    # qtawesome icon) and cached — every ComboBox instance shares one icon.
    global _check_icon
    if _check_icon is None:
        _check_icon = qta.icon("fa5s.check", color=ACCENT_BLUE)
    return _check_icon


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentIndexChanged.connect(self._refresh_checkmark)

    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        popup.move(self.mapToGlobal(self.rect().bottomLeft()))

    def addItem(self, *args, **kwargs):
        super().addItem(*args, **kwargs)
        self._refresh_checkmark()

    def addItems(self, texts):
        super().addItems(texts)
        self._refresh_checkmark()

    def _refresh_checkmark(self, *_):
        icon = _checkmark_icon()
        empty = QIcon()
        for i in range(self.count()):
            self.setItemIcon(i, icon if i == self.currentIndex() else empty)