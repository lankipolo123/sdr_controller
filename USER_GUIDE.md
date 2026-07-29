# SDR Noise Modulator Controller — User Guide

How to actually use the app, page by page. For project internals, see
`PROJECT_GUIDE.md`; for what's confirmed vs. guessed against real
hardware, see `PLANNING_v1.1_COMPARISON.md`.

---

## 1. Install and launch

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+. Only two dependencies: PySide6 (GUI) and pyserial
(serial communication).

---

## 2. First-time connection setup

Go to the **Settings** page and fill in:

| Field | What it is | Default |
|---|---|---|
| COM Port | Your USB↔RS422 adapter's port (check Windows Device Manager → Ports if unsure) | — |
| Baud Rate | Communication speed | 115200 |
| Data Bits | Serial frame size | 8 |
| Parity | Error-checking mode | None |
| Module Address | The device's internal ID (0–199) | 0 |
| Auto Connect | Connect automatically on app startup | Off |
| Log Folder | Where the rotating file log is written | `logs` |

**Only None parity / 115200 baud / 8 data bits has actually been used
against real hardware.** The other options are here because the real
vendor software exposes them too, but this specific device's firmware
hasn't been tested with anything besides the defaults — leave them
alone unless you have a specific reason to change them.

Use **Query** / **Set** next to Module Address to read or change the
device's internal address directly, instead of guessing.

Click **Save Configuration** to persist your settings — they're used
the next time you connect or auto-connect.

---

## 3. Connecting

On the **Dashboard** page, pick your port (Refresh if it's not listed)
and click **Connect**. The status label flips to "Connected" and the
button becomes "Disconnect".

If `auto_connect` is enabled and a valid COM port is saved, this
happens automatically at startup, before the window even appears.

---

## 4. Controlling the device

Go to **Device Control**:

- **Output**: a toggle switch — flips the RF output on/off immediately.
- **Signal Settings**:
  - **Mode**: White Noise, Linear Sweep, Comb Spectrum, or Single.
    *Single is marked "(unconfirmed)" — its protocol byte value is a
    guess, not proven against real hardware. Selecting it and hitting
    Apply will ask you to confirm before sending.*
  - **Center Frequency**: 300–6000 MHz, with a step-size dropdown
    (1/10/50/100 MHz) and +/- buttons for quick adjustment.
  - **Bandwidth**: 10 through 300 MHz. *300 MHz is marked
    "(unconfirmed)" for the same reason as Single mode.*
  - **Power**: 0 dB (max), -6 dB, or -12 dB. (This is what the real
    vendor software calls "attenuation" — same setting, different name.)
- **Apply**: sends the above as one Signal Control command.
- **Read Device**: queries the device's actual current status and
  refreshes the Dashboard/state from the real response.

Any time you select an unconfirmed mode or bandwidth and hit Apply,
you'll get a confirmation prompt first — this exists so a guessed
protocol value never goes out to real hardware by accident.

---

## 5. Reading status

The **Dashboard** shows live cards for Connection, Output State,
Frequency, Bandwidth, Power, and Current Mode, plus a "Last Command"
line — all update automatically whenever the device confirms a command
or you read status.

If a command gets no response within 2 seconds, an amber warning
banner appears on the Dashboard telling you which command timed out —
check wiring, module power, and module address, in that order.

---

## 6. Communication log

The **Communication** page shows a running, timestamped log: incoming
raw hex (RX), parsed frame descriptions, connection/disconnection
events, errors, and timeouts. Use **Clear** to wipe it.

---

## 7. First-time hardware bench test

Before trusting the full GUI against a device you've never connected
before, do this in order:

1. **Windows Device Manager** → Ports (COM & LPT) — confirm the adapter
   shows up at all.
2. **RealTerm/Termite, no code**: 115200-8-N-1, hex mode, send
   `7E 7E FF 00 00 0A 0D` manually. Any bytes back = wiring is alive.
3. **`python scripts/hardware_smoke_test.py COM3`** (swap in your real
   port) — runs this project's actual protocol code against the real
   device, no GUI, with a clear SUCCESS/TIMEOUT/PARTIAL verdict.
4. **Full GUI** — only after step 3 succeeds. Stick to confirmed
   settings first (White Noise/Linear Sweep/Comb Spectrum, ≤250 MHz,
   default parity/baud/data bits) before trying anything flagged
   "(unconfirmed)".
