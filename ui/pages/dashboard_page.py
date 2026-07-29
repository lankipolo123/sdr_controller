from PySide6.QtWidgets import QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout

from ui.base_page import BasePage
from ui.widgets import ConnectionWidget, HexLineDisplay
from protocol import constants as c


class DashboardPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Dashboard", "dashboard", app_controller, parent)
        self.app.device_state.changed.connect(self._refresh)
        self.app.device.command_timeout.connect(self._on_command_timeout)
        self.app.connection.frame_received.connect(self._clear_warning)

        layout = self.content_layout

        layout.addWidget(ConnectionWidget(self.app.connection, self.app.config))

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet(
            "color: #92400e; background: #fef3c7; border: 1px solid #f59e0b; "
            "border-radius: 6px; padding: 8px; font-weight: 600;"
        )
        self.warning_label.setVisible(False)
        self.warning_label.setWordWrap(True)
        layout.addWidget(self.warning_label)

        grid = QGridLayout()
        self.card_connection, self.value_connection = self._make_status_card("Connection")
        self.card_output, self.value_output = self._make_status_card("Output State")
        self.card_frequency, self.value_frequency = self._make_status_card("Frequency")
        self.card_bandwidth, self.value_bandwidth = self._make_status_card("Bandwidth")
        self.card_power, self.value_power = self._make_status_card("Power")
        self.card_mode, self.value_mode = self._make_status_card("Current Mode")

        cards = [self.card_connection, self.card_output, self.card_frequency,
                 self.card_bandwidth, self.card_power, self.card_mode]
        for i, card in enumerate(cards):
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)

        self.last_command_label = QLabel("Last Command: —")
        layout.addWidget(self.last_command_label)

        boxes_row = QHBoxLayout()

        tx_box = QGroupBox("Data Sending")
        tx_layout = QVBoxLayout(tx_box)
        self.tx_display = HexLineDisplay()
        tx_layout.addWidget(self.tx_display)
        boxes_row.addWidget(tx_box)

        rx_box = QGroupBox("Data Receiving")
        rx_layout = QVBoxLayout(rx_box)
        self.rx_display = HexLineDisplay()
        rx_layout.addWidget(self.rx_display)
        boxes_row.addWidget(rx_box)

        layout.addLayout(boxes_row)
        layout.addStretch()

        self.app.connection.raw_tx.connect(self.tx_display.show_bytes)
        self.app.connection.raw_rx.connect(self.rx_display.show_bytes)

        self._refresh()

    def _make_status_card(self, title: str):
        """Plain QGroupBox, same as Output/Signal Settings on Device
        Control — no separate custom card design."""
        box = QGroupBox(title)
        box_layout = QVBoxLayout(box)
        value_label = QLabel("—")
        box_layout.addWidget(value_label)
        return box, value_label

    def _refresh(self):
        d = self.app.device_state.data
        self.value_connection.setText("Connected" if d.connected else "Disconnected")
        self.value_output.setText("ON" if d.output_on else "OFF")
        self.value_frequency.setText(f"{d.frequency_mhz} MHz" if d.frequency_mhz else "—")
        self.value_bandwidth.setText(f"{d.bandwidth_mhz} MHz" if d.bandwidth_mhz else "—")
        self.value_power.setText(f"{d.power_db} dB" if d.power_db is not None else "—")
        self.value_mode.setText(c.MODE_NAMES.get(d.mode, "—") if d.mode is not None else "—")
        self.last_command_label.setText(f"Last Command: {d.last_command}")

    def _on_command_timeout(self, message: str):
        self.warning_label.setText(f"⚠ {message}")
        self.warning_label.setVisible(True)

    def _clear_warning(self, *_):
        self.warning_label.setVisible(False)
