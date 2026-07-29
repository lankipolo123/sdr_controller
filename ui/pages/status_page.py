from PySide6.QtWidgets import QGridLayout, QLabel

from ui.base_page import BasePage
from protocol import constants as c


class StatusPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Status", "status", app_controller, parent)
        self.app.device_state.changed.connect(self._refresh)

        layout = self.content_layout

        grid = QGridLayout()
        rows = ["Device Address", "Current Frequency", "Current Mode",
                "Current Bandwidth", "Current Power", "Output Status"]
        self.value_labels = {}
        for i, label in enumerate(rows):
            grid.addWidget(QLabel(f"{label}:"), i, 0)
            value_label = QLabel("—")
            value_label.setStyleSheet("font-weight: 600;")
            grid.addWidget(value_label, i, 1)
            self.value_labels[label] = value_label
        layout.addLayout(grid)
        layout.addStretch()

        self._refresh()

    def _refresh(self):
        d = self.app.device_state.data
        self.value_labels["Device Address"].setText(str(d.address))
        self.value_labels["Current Frequency"].setText(f"{d.frequency_mhz} MHz" if d.frequency_mhz else "—")
        self.value_labels["Current Mode"].setText(c.MODE_NAMES.get(d.mode, "—") if d.mode is not None else "—")
        self.value_labels["Current Bandwidth"].setText(f"{d.bandwidth_mhz} MHz" if d.bandwidth_mhz else "—")
        self.value_labels["Current Power"].setText(f"{d.power_db} dB" if d.power_db is not None else "—")
        self.value_labels["Output Status"].setText("ON" if d.output_on else "OFF")
