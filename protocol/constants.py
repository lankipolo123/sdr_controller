"""
Constants for the 300-6000MHz Digital Noise Modulator communication protocol.

All values taken directly from the vendor protocol document.
NOTE: see README.md "Known protocol doc issues" section — the BufLen field
documented for T=0x02 and T=0xFF-response appears to under-count the payload
by 1 byte. This module does not hardcode those BufLen values; packet_builder
computes BufLen from the actual payload length instead.
"""

HEAD = b"\x7E\x7E"
STOP = b"\x0A\x0D"

BROADCAST_ADDR = 0xFF

# ---- Instruction types (T) ----
TYPE_OUTPUT_SWITCH = 0x01
TYPE_SIGNAL_CONTROL = 0x02
TYPE_STATUS_QUERY = 0xFF          # same byte value used for query + response
TYPE_ADDR_QUERY = 0xBF
TYPE_ADDR_SET = 0xB1

# ---- Output switch (T=0x01) ----
OUTPUT_OFF = 0x00
OUTPUT_ON = 0x01

# ---- Modulation mode (T=0x02, byte 1 of payload) ----
MODE_WHITE_NOISE = 0x00
MODE_LINEAR_SWEEP = 0x01
MODE_COMB_SPECTRUM = 0x02
# UNCONFIRMED: vendor's real V1.1 software has a 4th mode, "SINGLE", that
# we don't have byte-value proof for. 0x03 is a sequential guess (see
# PLANNING_v1.1_COMPARISON.md section 2). Do not trust this against real
# hardware until verified.
MODE_SINGLE = 0x03

MODE_NAMES = {
    MODE_WHITE_NOISE: "White Noise",
    MODE_LINEAR_SWEEP: "Linear Sweep",
    MODE_COMB_SPECTRUM: "Comb Spectrum",
    MODE_SINGLE: "Single",
}

# Modes whose byte value is a guess, not confirmed against real hardware.
MODES_UNCONFIRMED = frozenset({MODE_SINGLE})

# ---- Bandwidth codes (MHz -> code) ----
BANDWIDTH_CODES = {
    10: 0x00,
    20: 0x01,
    50: 0x02,
    100: 0x03,
    150: 0x04,
    200: 0x05,
    250: 0x06,
    # UNCONFIRMED: real device has a 300MHz option; 0x07 is a sequential
    # guess following the confirmed 0x00-0x06 pattern (see
    # PLANNING_v1.1_COMPARISON.md section 3). Not verified against real
    # hardware.
    300: 0x07,
}
BANDWIDTH_CODES_REV = {v: k for k, v in BANDWIDTH_CODES.items()}

# Bandwidth values whose byte code is a guess, not confirmed against real hardware.
BANDWIDTH_UNCONFIRMED = frozenset({300})

# ---- Power codes (dB -> code) ----
POWER_CODES = {
    0: 0x00,   # -0 dB, i.e. max output
    -6: 0x01,
    -12: 0x02,
}
POWER_CODES_REV = {v: k for k, v in POWER_CODES.items()}

# ---- Response codes ----
RESP_FAILED = 0x01
RESP_SUCCESS = 0xFF

FREQ_MIN_MHZ = 300
FREQ_MAX_MHZ = 6000

ADDR_MIN = 0
ADDR_MAX = 199
