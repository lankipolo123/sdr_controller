from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QRadioButton, QButtonGroup, QComboBox, QMessageBox
)

from ui.base_page import BasePage
from ui.widgets import FrequencyWidget, ToggleSwitch
from protocol import constants as c
from protocol.packet_builder import ProtocolError


class DeviceControlPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Device Control", "device_control", app_controller, parent)

        layout = self.content_layout

        # Output controls
        output_box = QGroupBox("Output")
        output_row = QHBoxLayout(output_box)
        self.output_toggle = ToggleSwitch()
        self.output_toggle.toggled.connect(self._on_output_toggled)
        output_label = QLabel("Output ON/OFF")
        output_row.addWidget(self.output_toggle)
        output_row.addWidget(output_label)
        output_row.addStretch()
        layout.addWidget(output_box)

        # Signal settings
        signal_box = QGroupBox("Signal Settings")
        signal_layout = QVBoxLayout(signal_box)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_group = QButtonGroup(self)
        self.rb_white = QRadioButton("White Noise")
        self.rb_sweep = QRadioButton("Linear Sweep")
        self.rb_comb = QRadioButton("Comb Spectrum")
        self.rb_white.setChecked(True)
        for i, rb in enumerate([self.rb_white, self.rb_sweep, self.rb_comb]):
            self.mode_group.addButton(rb, i)
            mode_row.addWidget(rb)
        mode_row.addStretch()
        signal_layout.addLayout(mode_row)

        self.freq_widget = FrequencyWidget()
        signal_layout.addWidget(self.freq_widget)

        bw_row = QHBoxLayout()
        bw_row.addWidget(QLabel("Bandwidth:"))
        self.bw_combo = QComboBox()
        for mhz in c.BANDWIDTH_CODES.keys():
            self.bw_combo.addItem(f"{mhz} MHz", mhz)
        self.bw_combo.setCurrentIndex(3)  # 100 MHz default
        bw_row.addWidget(self.bw_combo)
        bw_row.addStretch()
        signal_layout.addLayout(bw_row)

        power_row = QHBoxLayout()
        power_row.addWidget(QLabel("Power:"))
        self.power_combo = QComboBox()
        for db in c.POWER_CODES.keys():
            self.power_combo.addItem("0 dB (max)" if db == 0 else f"{db} dB", db)
        power_row.addWidget(self.power_combo)
        power_row.addStretch()
        signal_layout.addLayout(power_row)

        btn_row = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.read_btn = QPushButton("Read Device")
        self.apply_btn.clicked.connect(self._on_apply)
        self.read_btn.clicked.connect(self.app.device.read_device)
        btn_row.addWidget(self.apply_btn)
        btn_row.addWidget(self.read_btn)
        btn_row.addStretch()
        signal_layout.addLayout(btn_row)

        layout.addWidget(signal_box)
        layout.addStretch()

    def _on_apply(self):
        if self.rb_white.isChecked():
            mode = c.MODE_WHITE_NOISE
        elif self.rb_sweep.isChecked():
            mode = c.MODE_LINEAR_SWEEP
        else:
            mode = c.MODE_COMB_SPECTRUM

        try:
            self.app.device.apply_signal_settings(
                mode,
                self.freq_widget.value(),
                self.bw_combo.currentData(),
                self.power_combo.currentData(),
            )
        except ProtocolError as e:
            QMessageBox.warning(self, "Invalid settings", str(e))

    def _on_output_toggled(self, checked: bool):
        if checked:
            self.app.device.turn_output_on()
        else:
            self.app.device.turn_output_off()
