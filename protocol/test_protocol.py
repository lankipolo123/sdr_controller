from . import constants as c
from . import packet_builder as pb
from .packet_parser import FrameParser


def test_output_switch():
    frame = pb.build_output_switch(addr=5, on=True)
    assert frame == bytes([0x7E, 0x7E, 0x01, 0x05, 0x01, 0x01, 0x0A, 0x0D]), frame.hex()
    print("output_switch OK:", pb.to_hex_str(frame))


def test_signal_control():
    frame = pb.build_signal_control(addr=0, mode=c.MODE_WHITE_NOISE,
                                     freq_mhz=2450, bandwidth_mhz=100, power_db=-6)
    expected = bytes([0x7E, 0x7E, 0x02, 0x00, 0x05, 0x00, 0x09, 0x92, 0x03, 0x01, 0x0A, 0x0D])
    assert frame == expected, f"{frame.hex()} != {expected.hex()}"
    print("signal_control OK:", pb.to_hex_str(frame))
    print("  (note: BufLen here is 0x05, the *correct* byte count — vendor doc says 0x04)")


def test_status_query():
    frame = pb.build_status_query()
    assert frame == bytes([0x7E, 0x7E, 0xFF, 0x00, 0x00, 0x0A, 0x0D]), frame.hex()
    print("status_query OK (matches vendor's literal fixed example):", pb.to_hex_str(frame))


def test_status_query_with_explicit_address():
    frame = pb.build_status_query(addr=7)
    assert frame == bytes([0x7E, 0x7E, 0xFF, 0x07, 0x00, 0x0A, 0x0D]), frame.hex()
    print("status_query_with_explicit_address OK:", pb.to_hex_str(frame))


def test_parse_roundtrip():
    parser = FrameParser()
    resp = bytes([0x7E, 0x7E, 0xFF, 0x00, 0x06,
                  0x01, 0x00, 0x09, 0x92, 0x03, 0x01,
                  0x0A, 0x0D])
    frames = parser.feed(resp[:4])
    assert frames == []
    frames = parser.feed(resp[4:])
    assert len(frames) == 1
    f = frames[0]
    assert f.type == 0xFF
    print("parse_roundtrip OK:", f.describe())


def test_parse_with_junk_prefix():
    parser = FrameParser()
    noisy = b"\x00\xFF" + pb.build_addr_query()
    frames = parser.feed(noisy)
    assert len(frames) == 1
    assert frames[0].type == c.TYPE_ADDR_QUERY
    print("parse_with_junk_prefix OK")


if __name__ == "__main__":
    test_output_switch()
    test_signal_control()
    test_status_query()
    test_status_query_with_explicit_address()
    test_parse_roundtrip()
    test_parse_with_junk_prefix()
    print("\nAll protocol tests passed.")
