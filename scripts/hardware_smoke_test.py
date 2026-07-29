"""
Standalone hardware smoke test — bypasses the GUI entirely.

Purpose: answer ONE question as cheaply and unambiguously as possible —
does a real status-query command sent over the real COM port get a real
response back from the real device? Nothing else. No GUI, no threads,
no controller layer — just the already-tested protocol/ and serial_io/
code, talking directly to the port.

Run this AFTER a manual RealTerm/Termite test has already shown some
response (even garbage) at the wiring level. This script's job is to
confirm our BYTE FORMAT is correct, not to debug wiring — if this script
gets zero bytes back at all, go back to checking wiring/power/COM port
first, don't debug this script.

Usage:
    python scripts/hardware_smoke_test.py COM3
    python scripts/hardware_smoke_test.py COM3 --address 0
    python scripts/hardware_smoke_test.py COM3 --timeout 3
"""

import sys
import os
import time
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import serial
from protocol import commands, packet_builder as pb
from protocol.packet_parser import FrameParser


def main():
    parser = argparse.ArgumentParser(description="Hardware smoke test — no GUI, just raw protocol.")
    parser.add_argument("port", help="COM port, e.g. COM3 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--address", type=int, default=0,
                         help="Module address to query (default 0 — the vendor doc's literal example uses this)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Seconds to wait for a response")
    args = parser.parse_args()

    print(f"Opening {args.port} at {args.baud} baud...")
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
        print("-> This is a port/driver problem, not a protocol problem. Check Device Manager.")
        sys.exit(1)

    frame = commands.query_status(args.address)
    print(f"TX: {pb.to_hex_str(frame)}")
    ser.write(frame)

    parser_state = FrameParser()
    deadline = time.time() + args.timeout
    got_any_bytes = False

    while time.time() < deadline:
        chunk = ser.read(256)
        if chunk:
            got_any_bytes = True
            print(f"RX (raw): {' '.join(f'{b:02X}' for b in chunk)}")
            frames = parser_state.feed(chunk)
            for f in frames:
                print(f"PARSED: {f.describe()}")
                print("\nRESULT: SUCCESS — real device responded with a valid frame.")
                ser.close()
                sys.exit(0)

    ser.close()
    if got_any_bytes:
        print("\nRESULT: PARTIAL — received bytes, but never assembled into a complete/valid frame.")
        print("-> Check: is the BufLen or address byte different than expected? See README section 7.3.")
    else:
        print(f"\nRESULT: TIMEOUT — no bytes received within {args.timeout}s.")
        print("-> Check wiring (TX/RX crossed?), module power, and module address.")
        print(f"-> This script queried address {args.address}. If the module's real address is different, retry with --address N.")
    sys.exit(1)


if __name__ == "__main__":
    main()
