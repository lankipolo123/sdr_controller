from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal


@dataclass
class DeviceStateData:
    connected: bool = False
    address: int = 0
    output_on: bool = False
    mode: int | None = None
    frequency_mhz: int | None = None
    bandwidth_mhz: int | None = None
    power_db: int | None = None
    last_command: str = "—"


class DeviceState(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.data = DeviceStateData()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.data, k, v)
        self.changed.emit()
