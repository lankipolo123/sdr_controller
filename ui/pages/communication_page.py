from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QVBoxLayout, QSizePolicy

from ui.base_page import BasePage
from ui.widgets import ActivityChart, HexLineDisplay


class CommunicationPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Communication", "communication", app_controller, parent)

        layout = self.content_layout

        self.chart = ActivityChart()
        layout.addWidget(self.chart, 7)

        boxes_row = QHBoxLayout()

        tx_box = QGroupBox("Data Sending")
        tx_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        tx_layout = QVBoxLayout(tx_box)
        self.tx_display = HexLineDisplay()
        tx_layout.addWidget(self.tx_display)
        boxes_row.addWidget(tx_box)

        rx_box = QGroupBox("Data Receiving")
        rx_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        rx_layout = QVBoxLayout(rx_box)
        self.rx_display = HexLineDisplay()
        rx_layout.addWidget(self.rx_display)
        boxes_row.addWidget(rx_box)

        layout.addLayout(boxes_row)
        layout.addStretch()

        self.app.connection.raw_tx.connect(self._on_tx)
        self.app.connection.raw_rx.connect(self._on_rx)

    def _on_tx(self, data: bytes):
        self.tx_display.show_bytes(data)
        self.chart.add_tx(data)

    def _on_rx(self, data: bytes):
        self.rx_display.show_bytes(data)
        self.chart.add_rx(data)
