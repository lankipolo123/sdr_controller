"""
Drop-in replacement for QComboBox that fixes Qt's default popup direction:
Qt tries to position the popup so the *currently selected row* lines up
with the box — which, for an item near the bottom of the list, can make
the popup open upward or jump to an unexpected position instead of just
appearing directly below the box like a normal dropdown. showPopup() is
overridden here to always move the popup to directly beneath the box
after Qt opens it.

The current value is shown via the popup's own selection highlight
(GLOBAL_QSS's selection-background-color) rather than an extra icon.

Use this instead of QComboBox everywhere in the app for a consistent feel.
"""

from PySide6.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        popup.move(self.mapToGlobal(self.rect().bottomLeft()))