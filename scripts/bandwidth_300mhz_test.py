"""
Standalone test for the unconfirmed 300MHz bandwidth byte value.

BANDWIDTH_CODES[300] = 0x07 in protocol/constants.py is a guess - a
sequential continuation of the vendor doc's confirmed 0x00-0x06 pattern,
never verified against real hardware. This script settles it for real:

1. Sends a Signal Control command with bandwidth=300MHz and checks whether
   the module's own response says success or failure.
2. Sends a Status Query right after and checks whether the module echoes
   back bandwidth=300MHz - not just "success", but the actual value stuck.

Bypasses the GUI entirely - just the already-tested protocol/ and
serial_io/ code talking directly to the port, same approach as
hardware_smoke_test.py.

Usage:
    python scripts/bandwidth_300mhz_test.py COM3
    python scripts/bandwidth_300mhz_test.py COM3 --address 0
"""

import sys
import os
import time
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import serial
from protocol import commands, constants as c, packet_builder as pb
from protocol.packet_parser import FrameParser


def wait_for_frame(ser, parser_state, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        chunk = ser.read(256)
        if chunk:
            print(f"RX (raw): {' '.join(f'{b:02X}' for b in chunk)}")
            frames = parser_state.feed(chunk)
            if frames:
                return frames[0]
    return None


def main():
    parser = argparse.ArgumentParser(description="Test whether the 300MHz bandwidth byte (0x07) is actually correct.")
    parser.add_argument("port", help="COM port, e.g. COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--address", type=int, default=0, help="Module address (default 0)")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    print(f"Opening {args.port} at {args.baud} baud, 8-N-1...")
    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2,
        )
    except serial.SerialException as e:
        print(f"FAILED to open port: {e}")
        sys.exit(1)

    parser_state = FrameParser()

    print("\n--- Step 1: Apply Signal Control with bandwidth=300MHz ---")
    frame = commands.set_signal(args.address, c.MODE_WHITE_NOISE, freq_mhz=2450, bandwidth_mhz=300, power_db=0)
    print(f"TX: {pb.to_hex_str(frame)}")
    ser.write(frame)

    reply = wait_for_frame(ser, parser_state, args.timeout)
    if reply is None:
        print("\nRESULT: INCONCLUSIVE - no response at all to the Apply command.")
        print("-> Not a bandwidth-specific answer - check connection/wiring first, this isn't about 300MHz.")
        ser.close()
        sys.exit(1)

    print(f"PARSED: {reply.describe()}")
    if reply.type == c.TYPE_SIGNAL_CONTROL and len(reply.buf) == 1:
        if reply.buf[0] == c.RESP_FAILED:
            print("\nRESULT: FAIL - module explicitly rejected bandwidth=300MHz (0x07).")
            print("-> 0x07 is confirmed WRONG. The real byte value is something else.")
            ser.close()
            sys.exit(1)
        elif reply.buf[0] != c.RESP_SUCCESS:
            print(f"\nRESULT: INCONCLUSIVE - unexpected response code 0x{reply.buf[0]:02X}.")
            ser.close()
            sys.exit(1)

    print("\n--- Step 2: Status Query to confirm it actually stuck ---")
    time.sleep(0.2)
    frame = commands.query_status(args.address)
    print(f"TX: {pb.to_hex_str(frame)}")
    ser.write(frame)

    reply = wait_for_frame(ser, parser_state, args.timeout)
    ser.close()

    if reply is None:
        print("\nRESULT: INCONCLUSIVE - Apply said success, but Status Query got no response.")
        sys.exit(1)

    print(f"PARSED: {reply.describe()}")
    if reply.type == c.TYPE_STATUS_QUERY and len(reply.buf) >= 6:
        bw_code = reply.buf[4]
        reported_mhz = c.BANDWIDTH_CODES_REV.get(bw_code)
        if reported_mhz == 300:
            print("\nRESULT: PASS - module confirms bandwidth=300MHz. 0x07 is CORRECT.")
            print("-> Tell Claude to remove 300 from BANDWIDTH_UNCONFIRMED in protocol/constants.py.")
            sys.exit(0)
        else:
            print(f"\nRESULT: FAIL - module reports bandwidth={reported_mhz}MHz (code 0x{bw_code:02X}), not 300.")
            print("-> 0x07 is confirmed WRONG.")
            sys.exit(1)

    print("\nRESULT: INCONCLUSIVE - got a response but couldn't parse a bandwidth field from it.")
    sys.exit(1)


if __name__ == "__main__":
    main()
