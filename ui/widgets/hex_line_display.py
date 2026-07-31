from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QFont


class HexLineDisplay(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Courier New"))

    def show_bytes(self, data: bytes):
        self.setText(data.hex(" ").upper())
