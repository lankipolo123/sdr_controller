# Planning Doc — Comparing Our App vs. Vendor's Real "V1.1" Software

**Status: PLANNING ONLY. Nothing in this document has been implemented.**
This exists so that when the next session starts, there's a clear,
specific plan to review and approve *before* any code is touched —
consistent with the handoff rule: ask before changing anything.

Source of truth for this comparison: 7 photos of the vendor's actual
"Digital Interference Source Configuration Software-V1.1" running
against real hardware (Addr=2), including real TX/RX byte frames.

---

## 1. CONFIRMED — no action needed, just documented proof

The real device's TX bytes for a Signal Control command exactly match
what our `packet_builder.py` already produces:

```
7E 7E 02 02 05 00 15 4A 05 00 0A 0D
```
Head | Type=02 | Addr=02 | BufLen=**05** | Mode=00(NOISE) | Freq=0x154A(5450) | BW=05 | Power=00 | Stop

This is real-world proof that our earlier fix (vendor PDF said
`BufLen=04`, we use the actual byte count `05`) was correct. No change
needed — just note this as validated.

**New observation to remember, not yet acted on:** the control response
frame `7E 7E 02 00 01 FF 0A 0D` came back with `Addr=00`, even though
the request was sent to `Addr=02`. Don't assume response Addr always
mirrors request Addr — worth confirming with a real device test before
relying on it anywhere.

---

## 2. Modulation modes — real device has 4, we have 3

**Real device dropdown:** NOISE, CHIRP, CIC, SINGLE
**Our app (`protocol/constants.py`, `device_control_page.py`):** White Noise, Linear Sweep, Comb Spectrum (3 only)

**Needs confirmation before touching code:** what do CHIRP/CIC/SINGLE's
actual byte values map to? Our current guess (unconfirmed):
- NOISE = 0x00 (matches "White Noise" already in our constants)
- CHIRP = ? (possibly what we called "Linear Sweep")
- CIC = ? (possibly what we called "Comb Spectrum")
- SINGLE = a 4th mode we don't have at all

**Where this would change if confirmed:**
- `protocol/constants.py` — MODE_* constants and MODE_NAMES dict
- `ui/pages/device_control_page.py` — the 3 QRadioButtons become 4, naming updated
- `protocol/test_protocol.py` — add a test for the new mode if byte value confirmed

**Do not rename/remap existing modes without confirming byte values
match real hardware — guessing wrong here would silently send the wrong
mode to a real device.**

---

## 3. Bandwidth — real device has 8 options up to 300MHz, we have 7 up to 250MHz

**Real device dropdown:** 10, 20, 50, 100, 150, 200, 250, **300** MHz
**Our app (`protocol/constants.py` BANDWIDTH_CODES):** 10, 20, 50, 100, 150, 200, 250 MHz (7 total, missing 300)

**Where this would change:**
- `protocol/constants.py` — add `300: 0x07` to `BANDWIDTH_CODES` (guessing the next sequential code; **needs confirmation**, not assumed)
- `ui/pages/device_control_page.py` — bandwidth dropdown picks up the new entry automatically since it iterates the dict

This one is lower-risk than the mode question — the existing codes
0x00–0x06 are already confirmed correct, we'd just be adding one more
sequential entry. Still needs the real 0x07 (or whatever it is)
confirmed rather than guessed, ideally via the real device's query
response or the vendor.

---

## 4. Serial settings — parity and baud rate are more flexible on the real device

**Real device:** Parity dropdown (None/Odd/Even/Mark/Space), Baud rate
preset dropdown (9600 up to 2,000,000)
**Our app (`ui/pages/settings_page.py`):** Baud is a free-entry QSpinBox
capped at 921600, no parity option at all — hardcoded to
`serial.PARITY_NONE` in `serial_io/serial_manager.py`

**Where this would change:**
- `serial_io/serial_manager.py` — `open()` currently hardcodes
  `parity=serial.PARITY_NONE`; would need a parameter
- `services/config_service.py` — add a `parity` key to `DEFAULT_CONFIG`
- `ui/pages/settings_page.py` — add a parity dropdown; consider
  changing baud from free-entry to a preset dropdown matching the
  real device's list, or at minimum raise the cap to 2,000,000

**Question to ask before doing this:** does our specific noise
modulator actually support anything other than None parity / 115200
baud, or is the vendor software just generic across their whole product
line (i.e., other devices they sell might use parity/other bauds, but
maybe not ours)? Worth checking the original protocol PDF's opening
line again: *"baud rate is 115200 Bps, with 8 bits of parity"* — that
line is actually a bit ambiguous ("8 bits of parity" doesn't quite
parse) and might be worth re-reading closely before assuming this
device supports anything other than what we already have.

---

## 5. Frequency step +/- buttons — not in our app at all

**Real device:** a "Test step" dropdown (e.g. 10MHz) plus `+`/`-`
buttons next to center frequency, letting you increment/decrement by
that step without retyping the number.
**Our app:** `FrequencyWidget` is just a raw spinbox, no step control.

**Where this would change:**
- `ui/widgets/frequency_widget.py` — add a step-size dropdown and +/- buttons
- Low protocol risk — this is purely a UI convenience, doesn't change
  what gets sent (still just a frequency value in the existing Signal
  Control frame)

This is the lowest-risk item on this whole list — worth doing first
if/when we resume, since it can't break protocol correctness.

---

## 6. Address query/set — protocol already exists, no GUI uses it yet

**Real device:** dedicated "Settings" and "query" buttons next to the
Addr field.
**Our app:** `protocol/commands.py` already has `query_address()` and
`set_address()` (Types 0xBF/0xB1) — fully implemented and tested in
`protocol/test_protocol.py` — but no page in the GUI calls them.

**Where this would change:**
- Likely `ui/pages/settings_page.py` (Address is already a settings
  field there) — add "Query" and "Set" buttons wired to
  `commands.query_address()` / `commands.set_address()`
- This is really a UI-wiring task, not new protocol work — the hard
  part (protocol correctness) is already done and tested.

---

## Suggested order if/when resumed (lowest risk first)

1. Frequency step +/- buttons (pure UI, zero protocol risk)
2. Address query/set GUI wiring (protocol already tested, just wire it up)
3. Bandwidth 300MHz option (needs one byte value confirmed)
4. Parity/baud settings expansion (needs a decision on whether it's relevant to this specific device)
5. Modulation mode 4th option + CHIRP/CIC naming (needs byte values confirmed — highest risk of the group, don't guess)

**Reminder per the handoff guide: do not implement any of this without
explicit go-ahead, and confirm the guessed/unconfirmed byte values
before writing them into protocol code.**
