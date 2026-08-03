from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Signal


class TerminalWidget(QWidget):
    cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFontFamily("Courier New")
        layout.addWidget(self.text)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.text.clear)
        clear_btn.clicked.connect(self.cleared.emit)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def log_tx(self, data: bytes):
        self._append(f"[{self._timestamp()}] TX: {data.hex(' ').upper()}")

    def log_rx(self, data: bytes):
        self._append(f"[{self._timestamp()}] RX: {data.hex(' ').upper()}")

    def log_info(self, text: str):
        self._append(f"[{self._timestamp()}]   -> {text}")

    def log_error(self, text: str):
        self._append(f"[{self._timestamp()}] ERROR: {text}")

    def _append(self, line: str):
        self.text.append(line)
        self.text.moveCursor(QTextCursor.End)
