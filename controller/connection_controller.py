import time

from PySide6.QtCore import QObject, Signal

from serial_io import SerialManager, SerialThread, list_com_ports

# Windows can briefly keep holding a COM port handle for a moment after a
# prior close() before the OS driver actually releases it - reconnecting
# right after a disconnect (or right after a previous failed connect
# attempt) can hit "Access is denied" purely from that timing, not a real
# problem with the port. One short, scoped retry clears this up instead of
# leaving the user stuck with a misleading permission error.
_TRANSIENT_ACCESS_ERROR_MARKERS = (
    "access is denied", "permissionerror", "errno 13", "winerror 5",
)


def _looks_like_transient_access_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in _TRANSIENT_ACCESS_ERROR_MARKERS)


class ConnectionController(QObject):
    connected_changed = Signal(bool)
    frame_received = Signal(object)
    raw_rx = Signal(bytes)
    raw_tx = Signal(bytes)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.manager = SerialManager()
        self.thread = SerialThread(self.manager)
        self.thread.frame_received.connect(self.frame_received.emit)
        self.thread.raw_rx.connect(self.raw_rx.emit)
        self.thread.error.connect(self.error.emit)

    @staticmethod
    def list_ports():
        return list_com_ports()

    def connect(self, port_name: str, baud: int = 115200, parity: str = "N", data_bits: int = 8) -> bool:
        last_error = None
        for attempt in range(2):
            try:
                self.manager.open(port_name, baud, parity, data_bits)
                last_error = None
                break
            except Exception as e:
                last_error = e
                if attempt == 0 and _looks_like_transient_access_error(e):
                    time.sleep(0.3)
                    continue
                break

        if last_error is not None:
            self.error.emit(f"Failed to open {port_name}: {last_error}")
            return False
        self.thread.start_reading()
        self.connected_changed.emit(True)
        return True

    def disconnect(self):
        self.thread.stop_reading()
        self.manager.close()
        self.connected_changed.emit(False)

    def is_connected(self) -> bool:
        return self.manager.is_open()

    def send(self, data: bytes) -> bool:
        if not self.is_connected():
            self.error.emit("Cannot send: not connected")
            return False
        try:
            self.manager.write(data)
            self.raw_tx.emit(data)
            return True
        except Exception as e:
            self.error.emit(f"Write failed: {e}")
            return False
