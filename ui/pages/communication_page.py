from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QVBoxLayout

from ui.base_page import BasePage
from ui.widgets import TerminalWidget, ActivityChart


class CommunicationPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Communication", "communication", app_controller, parent)

        layout = self.content_layout

        self.chart = ActivityChart()
        layout.addWidget(self.chart, 7)

        boxes_row = QHBoxLayout()

        tx_box = QGroupBox("Data Sending")
        tx_layout = QVBoxLayout(tx_box)
        self.tx_terminal = TerminalWidget()
        tx_layout.addWidget(self.tx_terminal)
        boxes_row.addWidget(tx_box)

        rx_box = QGroupBox("Data Receiving")
        rx_layout = QVBoxLayout(rx_box)
        self.rx_terminal = TerminalWidget()
        rx_layout.addWidget(self.rx_terminal)
        boxes_row.addWidget(rx_box)

        layout.addLayout(boxes_row, 3)

        self.app.connection.raw_tx.connect(self._on_tx)
        self.app.connection.raw_rx.connect(self._on_rx)
        self.app.connection.frame_received.connect(lambda f: self.rx_terminal.log_info(f.describe()))
        self.app.connection.error.connect(self.tx_terminal.log_error)
        self.app.device.command_timeout.connect(self.tx_terminal.log_error)
        self.app.connection.connected_changed.connect(
            lambda c: self.rx_terminal.log_info("Connected" if c else "Disconnected")
        )

        self._last_seen_command = None
        self.app.device_state.changed.connect(self._maybe_log_tx_label)

    def _on_tx(self, data: bytes):
        self.tx_terminal.log_tx(data)
        self.chart.add_tx(data)

    def _on_rx(self, data: bytes):
        self.rx_terminal.log_rx(data)
        self.chart.add_rx(data)

    def _maybe_log_tx_label(self):
        cmd = self.app.device_state.data.last_command
        if cmd != self._last_seen_command:
            self._last_seen_command = cmd
            self.tx_terminal.log_info(f"Command issued: {cmd}")
