from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from ui.base_page import BasePage, CONTENT_SPACING
from ui.widgets import ActivityChart, HexLineDisplay, TerminalWidget, make_card
from ui.theme_colors import TX_ACCENT, RX_ACCENT


class CommunicationPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Communication", "communication", app_controller, parent)

        layout = self.content_layout

        self.chart = ActivityChart()
        self.chart.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self.chart, 5)

        boxes_row = QHBoxLayout()
        boxes_row.setSpacing(CONTENT_SPACING)

        tx_box = make_card("Data Sending", icon="fa5s.arrow-up", accent=TX_ACCENT)
        tx_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.tx_display = HexLineDisplay()
        tx_box.body_layout.addWidget(self.tx_display)
        boxes_row.addWidget(tx_box)

        rx_box = make_card("Data Receiving", icon="fa5s.arrow-down", accent=RX_ACCENT)
        rx_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.rx_display = HexLineDisplay()
        rx_box.body_layout.addWidget(self.rx_display)
        boxes_row.addWidget(rx_box)

        layout.addLayout(boxes_row)

        log_box = make_card("Activity Log", icon="fa5s.terminal")
        self.log = TerminalWidget()
        log_box.body_layout.addWidget(self.log)
        layout.addWidget(log_box, 5)

        self.log.cleared.connect(self.chart.clear)
        self.log.cleared.connect(self.tx_display.clear)
        self.log.cleared.connect(self.rx_display.clear)

        self.app.connection.raw_tx.connect(self._on_tx)
        self.app.connection.raw_rx.connect(self._on_rx)
        self.app.connection.frame_received.connect(lambda f: self.log.log_info(f.describe()))
        self.app.connection.error.connect(self.log.log_error)
        self.app.device.command_timeout.connect(self.log.log_error)
        self.app.device.command_failed.connect(self.log.log_error)
        self.app.connection.connected_changed.connect(
            lambda c: self.log.log_info("Connected" if c else "Disconnected")
        )

    def _on_tx(self, data: bytes):
        self.tx_display.show_bytes(data)
        self.chart.add_tx(data)
        self.log.log_tx(data)

    def _on_rx(self, data: bytes):
        self.rx_display.show_bytes(data)
        self.chart.add_rx(data)
        self.log.log_rx(data)
