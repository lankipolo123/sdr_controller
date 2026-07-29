"""
Builds outgoing byte frames for the digital noise modulator protocol.

Frame layout:  Head(2) | Type(1) | Addr(1) | BufLen(1) | Buf(n) | Stop(2)

BufLen is always computed from the actual length of Buf, not hardcoded,
so the frame we send is guaranteed to be internally consistent even where
the vendor doc's stated BufLen looks wrong (see README).
"""

import struct
from . import constants as c


class ProtocolError(ValueError):
    pass


def _frame(type_byte: int, addr: int, buf: bytes) -> bytes:
    if not (0 <= addr <= 0xFF):
        raise ProtocolError(f"Address out of range: {addr}")
    if len(buf) > 0xFF:
        raise ProtocolError("Payload too long for 1-byte BufLen field")
    return (
        c.HEAD
        + bytes([type_byte, addr, len(buf)])
        + buf
        + c.STOP
    )


def build_output_switch(addr: int, on: bool) -> bytes:
    """T=0x01 — turn RF output on/off."""
    buf = bytes([c.OUTPUT_ON if on else c.OUTPUT_OFF])
    return _frame(c.TYPE_OUTPUT_SWITCH, addr, buf)


def build_signal_control(addr: int, mode: int, freq_mhz: int,
                          bandwidth_mhz: int, power_db: int) -> bytes:
    """T=0x02 — set modulation mode, center frequency, bandwidth, power."""
    if mode not in c.MODE_NAMES:
        raise ProtocolError(f"Unknown mode: {mode}")
    if not (c.FREQ_MIN_MHZ <= freq_mhz <= c.FREQ_MAX_MHZ):
        raise ProtocolError(
            f"Frequency {freq_mhz} MHz out of range "
            f"({c.FREQ_MIN_MHZ}-{c.FREQ_MAX_MHZ})"
        )
    if bandwidth_mhz not in c.BANDWIDTH_CODES:
        raise ProtocolError(f"Unsupported bandwidth: {bandwidth_mhz} MHz")
    if power_db not in c.POWER_CODES:
        raise ProtocolError(f"Unsupported power setting: {power_db} dB")

    buf = bytes([mode]) \
        + struct.pack(">H", freq_mhz) \
        + bytes([c.BANDWIDTH_CODES[bandwidth_mhz]]) \
        + bytes([c.POWER_CODES[power_db]])
    return _frame(c.TYPE_SIGNAL_CONTROL, addr, buf)


def build_status_query(addr: int = 0x00) -> bytes:
    """T=0xFF — query current status.

    The vendor doc gives one literal fixed example frame for this command:
    7E 7E FF 00 00 0A 0D  (Addr byte = 0x00).

    Unlike the address query/set commands (0xBF/0xB1), the vendor doc never
    calls this a "broadcast" command — it doesn't use 0xFF here at all in
    its example. So the default here is 0x00 to match that literal example,
    NOT constants.BROADCAST_ADDR. In practice, callers should pass the
    actual configured module address (as DeviceController does) rather than
    relying on this default at all — this default only matters for a
    single module still at its factory address of 0.
    """
    return _frame(c.TYPE_STATUS_QUERY, addr, b"")


def build_addr_query() -> bytes:
    """T=0xBF — query module's internal ID address (always broadcast)."""
    return _frame(c.TYPE_ADDR_QUERY, c.BROADCAST_ADDR, b"")


def build_addr_set(new_addr: int) -> bytes:
    """T=0xB1 — set module's internal ID address (broadcast, payload=new addr)."""
    if not (c.ADDR_MIN <= new_addr <= c.ADDR_MAX):
        raise ProtocolError(f"Address out of range: {new_addr}")
    return _frame(c.TYPE_ADDR_SET, c.BROADCAST_ADDR, bytes([new_addr]))


def to_hex_str(data: bytes) -> str:
    """Pretty-print bytes as space-separated hex, for the TX/RX log."""
    return " ".join(f"{b:02X}" for b in data)
