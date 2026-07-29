from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QFont


class HexLineDisplay(QLineEdit):
    """Read-only single line showing the most recent raw hex frame only,
    matching the vendor software's Data Sending/Data Receiving boxes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Courier New"))

    def show_bytes(self, data: bytes):
        self.setText(data.hex(" ").upper())
