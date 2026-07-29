from PySide6.QtWidgets import (
    QFormLayout, QComboBox, QSpinBox, QCheckBox, QHBoxLayout,
    QLineEdit, QPushButton, QMessageBox, QGroupBox, QVBoxLayout, QLabel
)

from serial_io import list_com_ports
from ui.base_page import BasePage

PARITY_OPTIONS = [
    ("None", "N"),
    ("Odd", "O"),
    ("Even", "E"),
    ("Mark", "M"),
    ("Space", "S"),
]

BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 2000000]

DATA_BITS_OPTIONS = [5, 6, 7, 8]


class SettingsPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Settings", "settings", app_controller, parent)
        config = self.app.config
        self.app.device_state.changed.connect(self._on_state_changed)

        layout = self.content_layout

        settings_box = QGroupBox("Connection & App Settings")
        box_layout = QVBoxLayout(settings_box)
        form = QFormLayout()

        self.port_combo = QComboBox()
        self.port_combo.addItems(list_com_ports())
        if config.get("com_port"):
            self.port_combo.setCurrentText(config.get("com_port"))
        form.addRow("COM Port:", self.port_combo)

        self.baud_combo = QComboBox()
        for baud in BAUD_OPTIONS:
            self.baud_combo.addItem(str(baud), baud)
        saved_baud = config.get("baud_rate", 115200)
        idx = self.baud_combo.findData(saved_baud)
        self.baud_combo.setCurrentIndex(idx if idx >= 0 else self.baud_combo.findData(115200))
        form.addRow("Baud Rate:", self.baud_combo)

        self.data_bits_combo = QComboBox()
        for bits in DATA_BITS_OPTIONS:
            self.data_bits_combo.addItem(str(bits), bits)
        saved_data_bits = config.get("data_bits", 8)
        idx = self.data_bits_combo.findData(saved_data_bits)
        self.data_bits_combo.setCurrentIndex(idx if idx >= 0 else self.data_bits_combo.findData(8))
        form.addRow("Data Bits:", self.data_bits_combo)

        self.parity_combo = QComboBox()
        for label, code in PARITY_OPTIONS:
            self.parity_combo.addItem(label, code)
        saved_parity = config.get("parity", "N")
        idx = self.parity_combo.findData(saved_parity)
        self.parity_combo.setCurrentIndex(idx if idx >= 0 else 0)
        form.addRow("Parity:", self.parity_combo)

        unconfirmed_note = QLabel(
            "Baud rate, data bits, and parity options here match the real "
            "vendor V1.1 software's dropdowns exactly. Only None parity / "
            "115200 baud / 8 data bits has actually been used against real "
            "hardware so far — other combinations are UI-ready but untested "
            "on the device itself. See PLANNING_v1.1_COMPARISON.md section 4."
        )
        unconfirmed_note.setWordWrap(True)
        unconfirmed_note.setStyleSheet(
            "color: #92400e; background: #fef3c7; border: 1px solid #f59e0b; "
            "border-radius: 6px; padding: 8px; font-weight: 600;"
        )
        address_row = QHBoxLayout()
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 199)
        self.address_spin.setValue(config.get("module_address", 0))
        address_row.addWidget(self.address_spin)
        self.query_addr_btn = QPushButton("Query")
        self.query_addr_btn.clicked.connect(self.app.device.query_address)
        address_row.addWidget(self.query_addr_btn)
        self.set_addr_btn = QPushButton("Set")
        self.set_addr_btn.clicked.connect(self._on_set_address)
        address_row.addWidget(self.set_addr_btn)
        form.addRow("Module Address:", address_row)

        self.auto_connect_check = QCheckBox()
        self.auto_connect_check.setChecked(config.get("auto_connect", False))
        form.addRow("Auto Connect:", self.auto_connect_check)

        self.log_folder_edit = QLineEdit(config.get("log_folder", "logs"))
        form.addRow("Log Folder:", self.log_folder_edit)

        box_layout.addLayout(form)
        box_layout.addWidget(unconfirmed_note)

        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self._on_save)
        box_layout.addWidget(save_btn)

        layout.addWidget(settings_box)
        layout.addStretch()

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
