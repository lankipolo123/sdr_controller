from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox

from protocol import constants as c
from ..theme_colors import TEXT_LIGHT


class FrequencyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Center Frequency:")
        label.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent;")
        layout.addWidget(label)
        self.spin = QSpinBox()
        self.spin.setRange(c.FREQ_MIN_MHZ, c.FREQ_MAX_MHZ)
        self.spin.setValue(2450)
        self.spin.setSuffix(" MHz")
        layout.addWidget(self.spin)
        layout.addStretch()

    def value(self) -> int:
        return self.spin.value()

    def set_value(self, mhz: int):
        self.spin.setValue(mhz)
