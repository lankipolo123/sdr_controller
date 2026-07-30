from PySide6.QtWidgets import QGridLayout, QLabel, QHBoxLayout, QSizePolicy

from ui.base_page import BasePage, CONTENT_SPACING
from ui.widgets import ConnectionWidget, HexLineDisplay, make_card
from ui.theme_colors import TEXT_DARK, TEXT_MUTED, ACCENT_BLUE, TX_ACCENT, RX_ACCENT
from protocol import constants as c


class DashboardPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Dashboard", "dashboard", app_controller, parent)
        self.app.device_state.changed.connect(self._refresh)
        self.app.device.command_timeout.connect(self._on_command_timeout)
        self.app.connection.frame_received.connect(self._clear_warning)

        layout = self.content_layout

        connection_row = ConnectionWidget(self.app.connection, self.app.config)
        connection_row.connect_btn.setObjectName("PrimaryButton")
        layout.addWidget(connection_row)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet(
            "color: #92400e; background: #fef3c7; border: 1px solid #f59e0b; "
            "border-radius: 6px; padding: 6px 8px; font-weight: 600;"
        )
        self.warning_label.setVisible(False)
        self.warning_label.setWordWrap(True)
        layout.addWidget(self.warning_label)

        grid = QGridLayout()
        grid.setSpacing(CONTENT_SPACING)
        self.card_connection, self.value_connection = self._make_status_card(
            "Connection", "fa5s.plug")
        self.card_output, self.value_output = self._make_status_card(
            "Output State", "fa5s.power-off")
        self.card_frequency, self.value_frequency = self._make_status_card(
            "Frequency", "fa5s.wave-square")
        self.card_bandwidth, self.value_bandwidth = self._make_status_card(
            "Bandwidth", "fa5s.chart-bar")
        self.card_power, self.value_power = self._make_status_card(
            "Power", "fa5s.bolt")
        self.card_mode, self.value_mode = self._make_status_card(
            "Current Mode", "fa5s.sliders-h")

        cards = [self.card_connection, self.card_output, self.card_frequency,
                 self.card_bandwidth, self.card_power, self.card_mode]
        for i, card in enumerate(cards):
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)

        self.last_command_label = QLabel("Last Command: —")
        self.last_command_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        layout.addWidget(self.last_command_label)

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
        layout.addStretch()

        self.app.connection.raw_tx.connect(self.tx_display.show_bytes)
        self.app.connection.raw_rx.connect(self.rx_display.show_bytes)

        self._refresh()

    def _make_status_card(self, title: str, icon=None):
        """Card styled as a compact stat tile: a small muted header above
        one large, bold value — not just a plain box with same-size text
        throughout. Icon is tinted TEXT_MUTED (not the bold accent blue)
        so it reads as a light, secondary decoration rather than competing
        with the value text for attention."""
        box = make_card(title, icon=icon, accent=TEXT_MUTED)
        value_label = QLabel("—")
        value_label.setStyleSheet(
            f"color: {TEXT_DARK}; font-size: 17px; font-weight: 700; background: transparent;"
        )
        box.body_layout.addWidget(value_label)
        return box, value_label

    def _refresh(self):
        d = self.app.device_state.data
        self.value_connection.setText("Connected" if d.connected else "Disconnected")
        self.value_connection.setStyleSheet(
            f"color: {'#087F23' if d.connected else '#B00020'}; "
            f"font-size: 17px; font-weight: 700; background: transparent;"
        )
        self.value_output.setText("ON" if d.output_on else "OFF")
        self.value_output.setStyleSheet(
            f"color: {ACCENT_BLUE if d.output_on else TEXT_MUTED}; "
            f"font-size: 17px; font-weight: 700; background: transparent;"
        )
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