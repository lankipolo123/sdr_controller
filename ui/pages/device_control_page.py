from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QMessageBox,
    QFormLayout, QSpinBox, QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt

from ui.base_page import BasePage, CONTENT_SPACING
from ui.widgets import FrequencyWidget, ToggleSwitch, make_card, ComboBox
from ui.widgets.confirm_dialog import ConfirmDialog
from ui.theme_colors import RADIO_BUTTON_STYLE, STATUS_OK, TEXT_MUTED, NEUTRAL_TRACK, checkbox_style
from serial_io import list_com_ports
from protocol import constants as c
from protocol.packet_builder import ProtocolError

PARITY_OPTIONS = [
    ("None", "N"),
    ("Odd", "O"),
    ("Even", "E"),
    ("Mark", "M"),
    ("Space", "S"),
]

BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 2000000]

DATA_BITS_OPTIONS = [5, 6, 7, 8]


class DeviceControlPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Device Control", "device_control", app_controller, parent)
        config = self.app.config
        self.app.device_state.changed.connect(self._on_state_changed)

        layout = self.content_layout

        # Connection & app settings
        settings_box = make_card("Connection & App Settings", icon="fa5s.cog")
        settings_box_layout = settings_box.body_layout
        form = QFormLayout()
        form.setVerticalSpacing(6)

        self.port_combo = ComboBox()
        self.port_combo.addItems(list_com_ports())
        if config.get("com_port"):
            self.port_combo.setCurrentText(config.get("com_port"))
        form.addRow("COM Port:", self.port_combo)

        self.baud_combo = ComboBox()
        for baud in BAUD_OPTIONS:
            self.baud_combo.addItem(str(baud), baud)
        saved_baud = config.get("baud_rate", 115200)
        idx = self.baud_combo.findData(saved_baud)
        self.baud_combo.setCurrentIndex(idx if idx >= 0 else self.baud_combo.findData(115200))
        form.addRow("Baud Rate:", self.baud_combo)

        self.data_bits_combo = ComboBox()
        for bits in DATA_BITS_OPTIONS:
            self.data_bits_combo.addItem(str(bits), bits)
        saved_data_bits = config.get("data_bits", 8)
        idx = self.data_bits_combo.findData(saved_data_bits)
        self.data_bits_combo.setCurrentIndex(idx if idx >= 0 else self.data_bits_combo.findData(8))
        form.addRow("Data Bits:", self.data_bits_combo)

        self.parity_combo = ComboBox()
        for label, code in PARITY_OPTIONS:
            self.parity_combo.addItem(label, code)
        saved_parity = config.get("parity", "N")
        idx = self.parity_combo.findData(saved_parity)
        self.parity_combo.setCurrentIndex(idx if idx >= 0 else 0)
        form.addRow("Parity:", self.parity_combo)

        address_row = QHBoxLayout()
        address_row.setSpacing(8)
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 199)
        self.address_spin.setValue(config.get("module_address", 0))
        self.address_spin.setMaximumWidth(90)
        address_row.addWidget(self.address_spin)
        self.query_addr_btn = QPushButton("Query")
        self.query_addr_btn.setFixedWidth(70)
        self.query_addr_btn.clicked.connect(self.app.device.query_address)
        address_row.addWidget(self.query_addr_btn)
        self.set_addr_btn = QPushButton("Set")
        self.set_addr_btn.setObjectName("PrimaryButton")
        self.set_addr_btn.setFixedWidth(70)
        self.set_addr_btn.clicked.connect(self._on_set_address)
        address_row.addWidget(self.set_addr_btn)
        address_row.addStretch()
        form.addRow("Module Address:", address_row)

        self.auto_connect_check = QCheckBox()
        self.auto_connect_check.setStyleSheet(checkbox_style())
        self.auto_connect_check.setChecked(config.get("auto_connect", False))
        form.addRow("Auto Connect:", self.auto_connect_check)

        self.log_folder_edit = QLineEdit(config.get("log_folder", "logs"))
        form.addRow("Log Folder:", self.log_folder_edit)

        settings_box_layout.addLayout(form)

        save_btn = QPushButton("Save Configuration")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._on_save)
        settings_box_layout.addWidget(save_btn)

        layout.addWidget(settings_box)

        # Output controls — a status pill next to the switch instead of a
        # plain static label, so the card's own color communicates state
        # at a glance instead of relying on the toggle's position alone.
        output_box = make_card("Output", icon="fa5s.broadcast-tower")
        output_row = QHBoxLayout()
        output_box.body_layout.addLayout(output_row)
        self.output_toggle = ToggleSwitch()
        self.output_toggle.toggled.connect(self._on_output_toggled)
        output_row.addWidget(self.output_toggle)

        self.output_status_pill = QLabel("OFF")
        self.output_status_pill.setAlignment(Qt.AlignCenter)
        self.output_status_pill.setFixedWidth(56)
        self._style_output_pill(False)
        output_row.addWidget(self.output_status_pill)
        output_row.addStretch()
        layout.addWidget(output_box)

        # Signal settings
        signal_box = make_card("Signal Settings", icon="fa5s.satellite-dish")
        signal_layout = signal_box.body_layout

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_group = QButtonGroup(self)
        self.rb_white = QRadioButton("White Noise")
        self.rb_sweep = QRadioButton("Linear Sweep")
        self.rb_comb = QRadioButton("Comb Spectrum")
        self.rb_single = QRadioButton("Single (unconfirmed)")
        self.rb_white.setChecked(True)
        for i, rb in enumerate([self.rb_white, self.rb_sweep, self.rb_comb, self.rb_single]):
            rb.setStyleSheet(RADIO_BUTTON_STYLE)
            self.mode_group.addButton(rb, i)
            mode_row.addWidget(rb)
        mode_row.addStretch()
        signal_layout.addLayout(mode_row)

        self.freq_widget = FrequencyWidget()
        signal_layout.addWidget(self.freq_widget)

        bw_row = QHBoxLayout()
        bw_row.addWidget(QLabel("Bandwidth:"))
        self.bw_combo = ComboBox()
        for mhz in c.BANDWIDTH_CODES.keys():
            suffix = " (unconfirmed)" if mhz in c.BANDWIDTH_UNCONFIRMED else ""
            self.bw_combo.addItem(f"{mhz} MHz{suffix}", mhz)
        self.bw_combo.setCurrentIndex(3)  # 100 MHz default
        bw_row.addWidget(self.bw_combo)
        bw_row.addStretch()
        signal_layout.addLayout(bw_row)

        power_row = QHBoxLayout()
        power_row.addWidget(QLabel("Power:"))
        self.power_combo = ComboBox()
        for db in c.POWER_CODES.keys():
            self.power_combo.addItem("0 dB (max)" if db == 0 else f"{db} dB", db)
        power_row.addWidget(self.power_combo)
        power_row.addStretch()
        signal_layout.addLayout(power_row)

        btn_row = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("PrimaryButton")
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
        elif self.rb_comb.isChecked():
            mode = c.MODE_COMB_SPECTRUM
        else:
            mode = c.MODE_SINGLE

        bandwidth_mhz = self.bw_combo.currentData()
        unconfirmed = []
        if mode in c.MODES_UNCONFIRMED:
            unconfirmed.append("modulation mode")
        if bandwidth_mhz in c.BANDWIDTH_UNCONFIRMED:
            unconfirmed.append("bandwidth")

        if unconfirmed:
            proceed = ConfirmDialog.ask(
                self,
                "Unconfirmed value",
                f"The selected {' and '.join(unconfirmed)} uses a guessed "
                "protocol byte value that hasn't been verified against real "
                "hardware. Send anyway?",
                confirm_text="Send anyway",
                danger=True,
            )
            if not proceed:
                return

        try:
            self.app.device.apply_signal_settings(
                mode,
                self.freq_widget.value(),
                bandwidth_mhz,
                self.power_combo.currentData(),
            )
        except ProtocolError as e:
            QMessageBox.warning(self, "Invalid settings", str(e))

    def _on_output_toggled(self, checked: bool):
        self._style_output_pill(checked)
        if checked:
            self.app.device.turn_output_on()
        else:
            self.app.device.turn_output_off()

    def _style_output_pill(self, is_on: bool):
        self.output_status_pill.setText("ON" if is_on else "OFF")
        bg = STATUS_OK if is_on else NEUTRAL_TRACK
        color = "#FFFFFF" if is_on else TEXT_MUTED
        self.output_status_pill.setStyleSheet(
            f"background: {bg}; color: {color}; font-weight: 700; "
            f"font-size: 11px; border-radius: 9px; padding: 3px 0;"
        )

    def _on_save(self):
        config = self.app.config
        config.set("com_port", self.port_combo.currentText())
        config.set("baud_rate", self.baud_combo.currentData())
        config.set("data_bits", self.data_bits_combo.currentData())
        config.set("parity", self.parity_combo.currentData())
        config.set("module_address", self.address_spin.value())
        config.set("auto_connect", self.auto_connect_check.isChecked())
        config.set("log_folder", self.log_folder_edit.text())
        config.save()

        self.app.device_state.update(address=self.address_spin.value())
        QMessageBox.information(self, "Settings", "Configuration saved.")

    def _on_set_address(self):
        self.app.device.set_address(self.address_spin.value())

    def _on_state_changed(self):
        if not self.address_spin.hasFocus():
            self.address_spin.setValue(self.app.device_state.data.address)