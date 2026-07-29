"""
Owns the physical COM port. No threading, no business logic —
just open/close/send/list, exactly per the architecture's
"Serial Layer: no business logic exists here" rule.
"""

import serial
import serial.tools.list_ports

BAUD_RATE = 115200


def list_com_ports():
    return [p.device for p in serial.tools.list_ports.comports()]


class SerialManager:
    def __init__(self):
        self._port: serial.Serial | None = None

    def open(self, port_name: str, baud: int = BAUD_RATE):
        self._port = serial.Serial(
            port=port_name,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2,
        )

    def close(self):
        if self._port and self._port.is_open:
            self._port.close()
        self._port = None

    def is_open(self) -> bool:
        return self._port is not None and self._port.is_open

    def write(self, data: bytes):
        if not self.is_open():
            raise RuntimeError("Port not open")
        self._port.write(data)

    def read(self, size: int = 256) -> bytes:
        if not self.is_open():
            return b""
        return self._port.read(size)
