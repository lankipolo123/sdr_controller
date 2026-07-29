from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton, QLabel


class ConnectionWidget(QWidget):
    def __init__(self, connection_controller, config_service=None, parent=None):
        super().__init__(parent)
        self.conn = connection_controller
        self.config = config_service
        self.conn.connected_changed.connect(self._on_connected_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.port_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.connect_btn = QPushButton("Connect")
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #b00020; font-weight: 600;")

        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_combo)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.refresh_ports()
        # In case the connection was already made before this widget existed
        # (e.g. auto-connect at startup), reflect the real current state now.
        self._on_connected_changed(self.conn.is_connected())

    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = self.conn.list_ports()
        self.port_combo.addItems(ports)
        if current in ports:
            self.port_combo.setCurrentText(current)

    def _on_connect_clicked(self):
        if self.conn.is_connected():
            self.conn.disconnect()
            return
        port = self.port_combo.currentText()
        baud = self.config.get("baud_rate", 115200) if self.config else 115200
        parity = self.config.get("parity", "N") if self.config else "N"
        data_bits = self.config.get("data_bits", 8) if self.config else 8
        if port:
            self.conn.connect(port, baud, parity, data_bits)

    def _on_connected_changed(self, connected: bool):
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #087f23; font-weight: 600;")
            self.connect_btn.setText("Disconnect")
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: #b00020; font-weight: 600;")
            self.connect_btn.setText("Connect")
