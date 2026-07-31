from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QComboBox, QPushButton

from protocol import constants as c
from ..theme_colors import TEXT_DARK, STATUS_OK, STATUS_OK_DARK, STATUS_ERROR, STATUS_ERROR_DARK

STEP_OPTIONS_MHZ = [1, 10, 50, 100]


class FrequencyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Center Frequency:")
        label.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        layout.addWidget(label)
        self.spin = QSpinBox()
        self.spin.setRange(c.FREQ_MIN_MHZ, c.FREQ_MAX_MHZ)
        self.spin.setValue(2450)
        self.spin.setSuffix(" MHz")
        layout.addWidget(self.spin)

        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedWidth(36)
        self.minus_btn.setStyleSheet(
            f"QPushButton {{ background: {STATUS_ERROR}; color: white; border: none; "
            f"border-radius: 5px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {STATUS_ERROR_DARK}; }}"
            f"QPushButton:pressed {{ background: {STATUS_ERROR_DARK}; }}"
        )
        self.minus_btn.clicked.connect(self._step_down)
        layout.addWidget(self.minus_btn)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedWidth(36)
        self.plus_btn.setStyleSheet(
            f"QPushButton {{ background: {STATUS_OK}; color: white; border: none; "
            f"border-radius: 5px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {STATUS_OK_DARK}; }}"
            f"QPushButton:pressed {{ background: {STATUS_OK_DARK}; }}"
        )
        self.plus_btn.clicked.connect(self._step_up)
        layout.addWidget(self.plus_btn)

        step_label = QLabel("Step:")
        step_label.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        layout.addWidget(step_label)
        self.step_combo = QComboBox()
        for mhz in STEP_OPTIONS_MHZ:
            self.step_combo.addItem(f"{mhz} MHz", mhz)
        self.step_combo.setCurrentIndex(1)  # 10 MHz default
        layout.addWidget(self.step_combo)

        layout.addStretch()

    def value(self) -> int:
        return self.spin.value()

    def set_value(self, mhz: int):
        self.spin.setValue(mhz)

    def _step_up(self):
        self.spin.setValue(self.spin.value() + self.step_combo.currentData())

    def _step_down(self):
        self.spin.setValue(self.spin.value() - self.step_combo.currentData())