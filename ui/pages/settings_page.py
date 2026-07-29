from PySide6.QtWidgets import (
    QFormLayout, QComboBox, QSpinBox, QCheckBox,
    QLineEdit, QPushButton, QMessageBox, QGroupBox, QVBoxLayout
)

from serial_io import list_com_ports
from ui.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Settings", "settings", app_controller, parent)
        config = self.app.config

        layout = self.content_layout

        settings_box = QGroupBox("Connection & App Settings")
        box_layout = QVBoxLayout(settings_box)
        form = QFormLayout()

        self.port_combo = QComboBox()
        self.port_combo.addItems(list_com_ports())
        if config.get("com_port"):
            self.port_combo.setCurrentText(config.get("com_port"))
        form.addRow("COM Port:", self.port_combo)

        self.baud_spin = QSpinBox()
        self.baud_spin.setRange(1200, 921600)
        self.baud_spin.setValue(config.get("baud_rate", 115200))
        form.addRow("Baud Rate:", self.baud_spin)

        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 199)
        self.address_spin.setValue(config.get("module_address", 0))
        form.addRow("Module Address:", self.address_spin)

        self.auto_connect_check = QCheckBox()
        self.auto_connect_check.setChecked(config.get("auto_connect", False))
        form.addRow("Auto Connect:", self.auto_connect_check)

        self.log_folder_edit = QLineEdit(config.get("log_folder", "logs"))
        form.addRow("Log Folder:", self.log_folder_edit)

        box_layout.addLayout(form)

        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self._on_save)
        box_layout.addWidget(save_btn)

        layout.addWidget(settings_box)
        layout.addStretch()

    def _on_save(self):
        config = self.app.config
        config.set("com_port", self.port_combo.currentText())
        config.set("baud_rate", self.baud_spin.value())
        config.set("module_address", self.address_spin.value())
        config.set("auto_connect", self.auto_connect_check.isChecked())
        config.set("log_folder", self.log_folder_edit.text())
        config.save()

        self.app.device_state.update(address=self.address_spin.value())
        QMessageBox.information(self, "Settings", "Configuration saved.")
