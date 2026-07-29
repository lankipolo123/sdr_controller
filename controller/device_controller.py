import struct

from PySide6.QtCore import QObject, QTimer, Signal

from protocol import commands, constants as c
from protocol.packet_parser import ParsedFrame
from models import DeviceState

RESPONSE_TIMEOUT_MS = 2000


class DeviceController(QObject):
    """
    The only place that calls protocol.commands. GUI pages call methods
    here; they never build packets or touch ConnectionController directly.
    """

    command_timeout = Signal(str)   # fires if a sent command gets no response in time

    def __init__(self, connection_controller, device_state: DeviceState, logger=None):
        super().__init__()
        self.conn = connection_controller
        self.state = device_state
        self.logger = logger
        self.conn.frame_received.connect(self._on_frame)
        self.conn.connected_changed.connect(self._on_connected_changed)
        self._pending_timer: QTimer | None = None
        self._pending_label = None
        self._pending_state_update: dict | None = None

    # ---- outgoing commands ----

    def turn_output_on(self):
        self._send(commands.output_on(self.state.data.address), "Output ON",
                   {"output_on": True})

    def turn_output_off(self):
        self._send(commands.output_off(self.state.data.address), "Output OFF",
                   {"output_on": False})

    def apply_signal_settings(self, mode: int, freq_mhz: int, bandwidth_mhz: int, power_db: int):
        frame = commands.set_signal(self.state.data.address, mode, freq_mhz, bandwidth_mhz, power_db)
        self._send(frame, f"Signal: mode={mode} f={freq_mhz}MHz bw={bandwidth_mhz}MHz p={power_db}dB",
                   {"mode": mode, "frequency_mhz": freq_mhz, "bandwidth_mhz": bandwidth_mhz, "power_db": power_db})

    def read_device(self):
        self._send(commands.query_status(self.state.data.address), "Status query")

    def query_address(self):
        self._send(commands.query_address(), "Query address")

    def set_address(self, new_addr: int):
        self._send(commands.set_address(new_addr), f"Set address to {new_addr}",
                   {"address": new_addr})

    def _send(self, frame: bytes, label: str, state_update: dict | None = None):
        self.state.update(last_command=label)
        if self.logger:
            self.logger.info(f"TX ({label}): {frame.hex(' ').upper()}")

        sent = self.conn.send(frame)
        if not sent:
            return  # ConnectionController already emitted an error; nothing to wait for

        self._cancel_pending_timeout()
        self._pending_label = label
        self._pending_state_update = state_update
        self._pending_timer = QTimer()
        self._pending_timer.setSingleShot(True)
        self._pending_timer.timeout.connect(self._on_response_timeout)
        self._pending_timer.start(RESPONSE_TIMEOUT_MS)

    def _cancel_pending_timeout(self):
        if self._pending_timer is not None:
            self._pending_timer.stop()
            self._pending_timer = None
            self._pending_label = None
            self._pending_state_update = None

    def _on_response_timeout(self):
        msg = (
            f"No response within {RESPONSE_TIMEOUT_MS}ms for: {self._pending_label} "
            f"(check wiring, module power, and module address — see wiring reference)"
        )
        if self.logger:
            self.logger.warning(msg)
        self.command_timeout.emit(msg)
        self._pending_timer = None
        self._pending_label = None

    # ---- incoming ----

    def _on_connected_changed(self, connected: bool):
        self.state.update(connected=connected)

    def _on_frame(self, frame: ParsedFrame):
        pending_update = self._pending_state_update
        self._cancel_pending_timeout()
        if self.logger:
            self.logger.info(f"RX: {frame.raw.hex(' ').upper()} -> {frame.describe()}")

        if frame.type in (c.TYPE_OUTPUT_SWITCH, c.TYPE_SIGNAL_CONTROL, c.TYPE_ADDR_SET) \
                and len(frame.buf) == 1:
            if frame.buf[0] == c.RESP_SUCCESS and pending_update:
                self.state.update(**pending_update)
        elif frame.type == c.TYPE_STATUS_QUERY and len(frame.buf) >= 6:
            output = frame.buf[0]
            mode = frame.buf[1]
            freq = struct.unpack(">H", frame.buf[2:4])[0]
            bw_code = frame.buf[4]
            pw_code = frame.buf[5]
            self.state.update(
                output_on=bool(output),
                mode=mode,
                frequency_mhz=freq,
                bandwidth_mhz=c.BANDWIDTH_CODES_REV.get(bw_code),
                power_db=c.POWER_CODES_REV.get(pw_code),
            )
        elif frame.type == c.TYPE_ADDR_QUERY and len(frame.buf) == 1:
            self.state.update(address=frame.buf[0])
