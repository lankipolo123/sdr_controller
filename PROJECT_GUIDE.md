# SDR Noise Modulator Controller — Complete Project Guide

## What this is

A Windows desktop app that controls a 300–6000MHz digital noise modulator
over RS422 serial, replacing manual hex-command entry with a GUI:
connect, set frequency/mode/bandwidth/power, read status, view a
communication log.

---

## 1. Setup

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+. Only two dependencies: PySide6 (GUI) and pyserial
(serial communication) — everything else is Python's standard library.

---

## 2. Project structure

```
SDR_Controller/
├── main.py / app.py            Entry point
├── config/config.json          Saved settings (COM port, baud, address, etc.)
├── protocol/                    Binary protocol — fully tested, no hardware needed
│   ├── constants.py, packet_builder.py, packet_parser.py, commands.py
│   └── test_protocol.py         Run: python -m protocol.test_protocol
├── serial_io/                   Serial port I/O
│   ├── serial_manager.py, serial_thread.py
├── models/device_state.py       Shared app state
├── controller/                  Coordination layer
│   ├── app_controller.py, connection_controller.py, device_controller.py
├── services/                    Config + logging
├── scripts/
│   └── hardware_smoke_test.py   Standalone hardware test, no GUI
└── ui/
    ├── base_page.py, main_window.py, sidebar.py, theme_colors.py
    ├── pages/                    Dashboard, Device Control, Status, Communication, Settings
    └── widgets/                  StatusCard, ConnectionWidget, ToggleSwitch, SectionCard, etc.
```

---

## 3. The communication protocol (what the device actually understands)

Frame format: `Head(2) Type(1) Addr(1) BufLen(1) Buf(n) Stop(2)`
Head is always `0x7E7E`, Stop is always `0x0A0D`.

| Command | Type | Notes |
|---|---|---|
| Output switch | `0x01` | 1 byte: `0x00` off / `0x01` on |
| Signal control | `0x02` | mode + frequency(2B) + bandwidth + power |
| Status query | `0xFF` | No payload |
| Address query | `0xBF` | Broadcast (`0xFF`) |
| Address set | `0xB1` | Broadcast (`0xFF`) |

**Two real errors found in the vendor's own documentation, both handled
by the code (computing actual byte length instead of trusting the
doc's stated numbers):**
1. `BufLen` for Signal Control and Status Response is documented as one
   byte short of the actual payload.
2. Status Query's documented fixed example uses `Addr = 0x00`, not the
   broadcast address `0xFF` — despite address query/set commands
   correctly using broadcast.

---

## 4. Confirmed hardware wiring

**JT24X USB↔RS485/422 adapter, DB9 pins:**
| Pin | Signal |
|---|---|
| 1 | T+ | 2 | T- | 3 | R+ | 4 | R- | 5 | GND | 6–9 | NC |

**Module connector pins:**
| Pin | Signal |
|---|---|
| 1 | +12V | 2 | GND | 3 | TX+ | 4 | TX- | 5 | RX+ | 6 | RX- |

**Final wiring (TX/RX crossed, as required for point-to-point RS422):**
| Adapter Pin | → | Module Pin |
|---|---|---|
| 1 (T+) | → | 5 (RX+) |
| 2 (T-) | → | 6 (RX-) |
| 3 (R+) | → | 3 (TX+) |
| 4 (R-) | → | 4 (TX-) |
| 5 (GND) | → | 2 (GND) |
| — (separate 12V supply) | → | 1 (+12V) |

---

## 5. How to actually test hardware communication (in order)

1. **Device Manager** — confirm the COM port shows up at all.
2. **RealTerm/Termite, no code** — 115200-8-N-1, hex mode, send
   `7E 7E FF 00 00 0A 0D` manually. Any bytes back = wiring is alive.
3. **`python scripts/hardware_smoke_test.py COM3`** — our protocol code
   against the real device, no GUI. Clear SUCCESS/TIMEOUT/PARTIAL verdict.
4. **Full GUI** — only after step 3 succeeds.

---

## 6. What's tested vs. what isn't

**Tested and verified (headless, automated):**
- Protocol layer: 6 automated tests, all passing
- Full GUI construction, all 5 pages
- Toggle switch, dialogs, timeout detection, logout flow
- Multiple real bugs found and fixed (listed in §7)

**Never tested — the actual open item:**
- Real hardware has never been connected and confirmed working end-to-end
- No spectrum analyzer confirmation that RF output changes as commanded

---

## 7. Real bugs found and fixed this project (not just polish)

1. Vendor doc's `BufLen` byte-count error (2 commands)
2. Vendor doc's status-query address byte assumption
3. Baud rate setting was cosmetic-only (never wired to actual connect)
4. Auto-connect/widget ordering bug (state shown before widget existed)
5. Qt `WA_StyledBackground` missing → backgrounds/borders silently not rendering
6. Header height hardcoded from one measurement → now derived live from sidebar
7. Confirm dialog collapsing too small on a real machine, clipping button text
8. Radio button indicator disappearing after adding a color-only stylesheet
9. Status card text rendering dark-on-dark after a background color change

---

## 8. Known open items / deliberately deferred

- **16 channels, temperature monitoring, kill switch** — explicitly requested
  as future features, not built. Protocol already supports multi-address
  channels (`0xBF`/`0xB1`); temperature has zero support in the protocol
  document at all — would need either new hardware or a clearly-labeled
  simulated value.
- **`.exe` packaging** — not attempted; should happen after hardware is confirmed.
- **Proposal `.docx`** — its architecture section describes the old flat
  structure, not this layered one. Never updated.
- **Config corrupt-load** — fails silently with no warning if `config.json` is malformed.
- **No checked-in regression tests for the controller layer** — only `protocol/` has real test files.

---

## 9. Everything delivered

- `NoiseModulatorGUI.zip` — earlier, simpler single-window version (superseded)
- `SDR_Controller.zip` — current layered dashboard version (this project)
- `Noise_Modulator_Project_Proposal.docx` — formal proposal (architecture section now outdated)
- This guide
