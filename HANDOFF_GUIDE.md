# Handoff Guide — SDR Noise Modulator Controller

Read this entire document before touching any code. It exists because
previous sessions made unrequested changes repeatedly, and that caused
real frustration and wasted time. Follow the rules below strictly.

---

## RULES — READ FIRST, FOLLOW EXACTLY

1. **Do not change anything that was not explicitly asked for.** Not
   colors, not layout, not "while I'm in here I'll also fix..." — nothing.
   If you notice something that looks wrong or inconsistent, **say so and
   ask**. Do not fix it silently.

2. **Ask before assuming.** If a request is ambiguous, ask a clarifying
   question before writing code. Do not guess at what "looks better" —
   the person has been explicit multiple times that they want
   consistency, not decoration, not improvement, not your design opinion.

3. **The current design is deliberately plain. Keep it that way.**
   Every page's grouped content uses a plain, unstyled `QGroupBox` —
   native rendering, no custom colors, no rounded dark cards, no accent
   stripes, no notched borders. This was arrived at after multiple
   rounds of the AI adding "polish" that was never requested and then
   having to revert it. **Do not reintroduce custom card styling,
   dark themes, accent colors, or any visual "improvement" to these
   containers unless explicitly asked, by name, for that specific thing.**

4. **Verify before claiming something works.** Run the actual test
   suite (`python -m protocol.test_protocol`), do a syntax check
   (`py_compile` on all files), and build the app headless before saying
   "this is fixed." Multiple past bugs shipped because a fix was
   assumed correct without checking. If you cannot run something (e.g.
   you're in a text-only environment), say so plainly — do not claim
   verification that didn't happen.

5. **When you do make a change, package and verify it, then stop.**
   Do not chain into other changes "while you're at it."

---

## What this project is

A Windows desktop app (Python + PySide6) that controls a 300–6000MHz
digital noise modulator over RS422 serial. Replaces manual hex-command
entry with a GUI.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Python 3.10+. Two dependencies: PySide6, pyserial. Everything else is
the standard library.

## Current file structure

```
SDR_Controller/
├── main.py / app.py
├── config/config.json
├── protocol/                    Binary protocol — fully tested, no hardware needed
│   ├── constants.py, packet_builder.py, packet_parser.py, commands.py
│   └── test_protocol.py         python -m protocol.test_protocol
├── serial_io/                   serial_manager.py, serial_thread.py
├── models/device_state.py
├── controller/                  app_controller.py, connection_controller.py, device_controller.py
├── services/                    config_service.py, logging_service.py
├── scripts/hardware_smoke_test.py    Standalone hardware test, no GUI
└── ui/
    ├── base_page.py, main_window.py, sidebar.py, theme_colors.py
    ├── pages/                    dashboard, device_control, status, communication, settings
    └── widgets/                  connection_widget, frequency_widget, terminal_widget,
                                   toggle_switch, confirm_dialog, page_header, plus
                                   unused-but-present: status_card.py, section_card.py
```

**Note:** `status_card.py` and `section_card.py` still exist in
`ui/widgets/` from earlier design experiments but are **no longer used
by any page** — all pages now use plain `QGroupBox` instead. Do not
delete them without asking, and do not revive them without being
explicitly asked to.

## Current design state (verified, do not change without explicit request)

| Page | Structure |
|---|---|
| Dashboard | 6 status values, each in its own plain `QGroupBox` |
| Device Control | "Output" (toggle switch) and "Signal Settings" (mode/freq/bandwidth/power), each a plain `QGroupBox` |
| Status | Plain label/value grid, no `QGroupBox` |
| Communication | Just the TX/RX log widget, no `QGroupBox` |
| Settings | One `QGroupBox` ("Connection & App Settings") wrapping the whole form |

All confirmed via `isinstance()` checks and headless rendering, not just
visual inspection.

## The protocol (frame format)

`Head(2)=0x7E7E | Type(1) | Addr(1) | BufLen(1) | Buf(n) | Stop(2)=0x0A0D`

| Command | Type |
|---|---|
| Output switch | `0x01` |
| Signal control | `0x02` |
| Status query | `0xFF` |
| Address query | `0xBF` (broadcast) |
| Address set | `0xB1` (broadcast) |

**Two real vendor-doc errors already found and handled in code** (do not
"fix" these back to match the doc — the doc is wrong, the code is right):
1. `BufLen` for Signal Control and Status Response is one byte short of
   the actual payload in the vendor doc. Code computes the real length.
2. Status Query's doc example uses `Addr=0x00`, not broadcast `0xFF`.

## Confirmed hardware wiring

| Adapter (JT24X) Pin | → | Module Pin |
|---|---|---|
| 1 (T+) | → | 5 (RX+) |
| 2 (T-) | → | 6 (RX-) |
| 3 (R+) | → | 3 (TX+) |
| 4 (R-) | → | 4 (TX-) |
| 5 (GND) | → | 2 (GND) |
| — (separate 12V supply) | → | 1 (+12V) |

## Hardware test sequence (still the main open item — nothing has
confirmed real hardware communication yet)

1. Device Manager — confirm COM port exists
2. RealTerm/Termite, hex mode, manually send `7E 7E FF 00 00 0A 0D`
3. `python scripts/hardware_smoke_test.py COM3` — protocol code, no GUI
4. Full GUI — only after step 3 succeeds

## Deferred features (explicitly requested to be remembered for later,
NOT built yet — do not build unless asked again)

- **16 channels** — protocol already supports multi-address modules via
  `Addr` byte + `0xBF`/`0xB1`; would need a Device Manager layer, per-
  channel state, and a discovery/scan UI. Needs clarification on
  whether real multiple physical units exist yet.
- **Temperature monitoring** — zero support in the vendor protocol.
  Would need either new hardware or a clearly-labeled simulated value —
  never a silently-faked real-looking number.
- **Emergency kill switch** — trivial once multi-channel exists: loop
  `output_off()` across all known addresses.

## Other known open items

- Proposal `.docx`'s architecture section describes the old flat
  structure, not the current layered one. Never updated.
- Config corrupt-load fails silently, no warning.
- No checked-in regression tests for the controller layer (only
  `protocol/` has real test files).
- `.exe` packaging not attempted — should happen only after hardware
  is confirmed working.

## Verification performed before this handoff

```
protocol tests:     6/6 passing
syntax check:       all .py files compile
full app build:     all 5 pages construct successfully (headless)
QGroupBox count:    Dashboard=6, Device Control=2, Status=0, Communication=0, Settings=1
```
