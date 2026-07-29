# SDR Noise Generator Controller — v1.0

Dashboard-style desktop control application for the 300–6000 MHz digital
noise modulator, over RS422 at 115200 baud.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Layout

```
main.py / app.py          entry point + bootstrap
controller/                coordination layer (never touches bytes or ports directly)
  app_controller.py         composition root — wires everything together
  connection_controller.py  connect/disconnect lifecycle, exposes Qt signals only
  device_controller.py      the only place that calls protocol.commands
protocol/                  binary protocol (unchanged from prior verified build)
  constants.py, packet_builder.py, packet_parser.py, commands.py
  test_protocol.py          run: python -m protocol.test_protocol
serial_io/                  physical I/O (named serial_io, not serial — see note below)
  serial_manager.py          open/close/read/write, no threading
  serial_thread.py           background read loop (QThread)
models/
  device_state.py            single source of truth; pages subscribe to `changed`
services/
  config_service.py          JSON config load/save
  logging_service.py         rotating file logger (logs/sdr_controller.log)
ui/
  main_window.py, sidebar.py
  pages/                     Dashboard, Device Control, Status, Communication, Settings
  widgets/                   StatusCard, ConnectionWidget, FrequencyWidget, TerminalWidget
```

## Design note: why `serial_io/` instead of `serial/`

The original architecture spec named this folder `serial/`. That collides
with the third-party `pyserial` package, which is also imported as
`import serial` — a local `serial/` package on the Python path would shadow
it and break every serial import in the project. Renamed to `serial_io/`
to avoid that; nothing else about the design changed.

## Verified so far

- **Protocol layer:** all automated tests pass (`python -m protocol.test_protocol`),
  including the corrected BufLen handling for the signal-control and
  status-response frames (see prior proposal doc, Section 7.3).
- **Full application:** constructs and runs end-to-end under a headless Qt
  platform; all 5 pages load, and a full command round-trip (Device
  Control → Device Controller → Protocol → Device State → Dashboard)
  runs without errors.
- **Disconnected-state safety:** sending a command with no device connected
  raises a clean error signal instead of crashing.
- **Settings persistence:** Settings page saves actually round-trip to
  `config/config.json` (baud rate, module address, etc. all verified).
- **Logging:** rotating file logger confirmed writing to `logs/sdr_controller.log`.
- **Auto-connect:** implemented and wired up — if `auto_connect: true` and a
  valid `com_port` are saved, the app connects automatically at startup
  before the window is even shown.
- Not yet verified: real hardware over the actual RS422 link. That's the
  next step, using the wiring map already confirmed (adapter DB9 pins 1–5
  ↔ module pins 5/6/3/4/2, output crossed per RS422 convention).

## Two bugs found and fixed during this validation pass

1. **Baud rate was cosmetic only.** The Settings page let you set a baud
   rate and it saved to config, but the Dashboard's Connect button always
   used a hardcoded 115200 regardless. Fixed: `ConnectionWidget` now reads
   the saved baud rate from config when connecting.
2. **Auto-connect/widget ordering bug.** `AppController` builds the
   connection (and now auto-connects) *before* `MainWindow` and its
   `ConnectionWidget` exist. If auto-connect succeeded, the widget would
   never receive that `connected_changed` signal and would incorrectly
   show "Disconnected" on screen. Fixed: `ConnectionWidget` now checks the
   real connection state directly when it's constructed, not just future
   signals.

## New: response timeout detection (added for bench testing)

Previously, if a command got no response at all — wrong module address,
bad wiring, module unpowered — the app would sit silently with no
indication anything was wrong. Now:

- Every sent command starts a 2-second response timer.
- If a real response frame arrives in time, the timer is cancelled — no
  false alarms.
- If nothing arrives within 2 seconds, a visible amber warning banner
  appears on the Dashboard ("No response within 2000ms for: ...") and the
  same message is written to the Communication log and the file log.

This was specifically added so that during your first bench test, a wiring
or addressing problem shows up immediately as an on-screen warning instead
of the app just looking "stuck" with no explanation. Verified with 5
targeted tests: no phantom timer on a failed/disconnected send, a real
timeout firing correctly when nothing responds, correct cancellation when
a real response does arrive, and the Dashboard banner showing/hiding
correctly in both directions.

## Suggested first bench test sequence

1. Confirm wiring per Appendix B / Section 6 of the proposal doc (adapter
   DB9 pins 1–5 crossed to module pins 5/6/3/4/2).
2. Power the module (+12V to pin 1, GND to pin 2) — independent of the USB link.
3. Launch the app, open Settings, set the correct COM port and save.
4. Go to Dashboard, click Connect.
5. Go to Device Control, click "Read Device."
6. Watch the Dashboard: either the status cards populate with real values
   (success), or the amber warning banner appears within 2 seconds
   (something's wrong — check the Communication log for the exact command
   that got no answer, then check wiring/address/power in that order).
7. Ideally, verify with a spectrum analyzer on the module's RF output that
   a frequency/power change via "Apply" actually produces the expected
   physical signal — the software can only confirm the *bytes* match the
   protocol document, not that the resulting RF output is correct.

## A third bug found in the protocol layer itself

`build_status_query()`'s default address was `constants.BROADCAST_ADDR`
(0xFF), but the vendor doc's own docstring-quoted fixed example uses
`Addr = 0x00`: `7E 7E FF 00 00 0A 0D`. The code's default and its own
comment contradicted each other — and unlike the address query/set
commands (0xBF/0xB1), the vendor doc never actually calls this a
"broadcast" command. Fixed the default to `0x00` to match the literal
vendor example, and added a test that checks the built frame against
that exact documented byte sequence rather than against our own prior
assumption. Confirmed this doesn't affect real usage: `DeviceController`
always passes the module's actual configured address explicitly, so this
default was never hit by the running app — only by the test suite,
which was quietly testing our own earlier mistake against itself.

## Theme setting now actually works

Previously the Theme dropdown in Settings saved to config but was never
applied anywhere — a dead setting. Fixed: `services/theme_service.py`
applies a real Fusion-style dark/light palette app-wide. Switching it in
Settings changes it live (no restart needed), it persists to config.json,
and a fresh launch picks up whatever was last saved. Verified with 4
tests: real color change, dark is actually darker than light, persistence
across a simulated restart, and reversibility back to light.

## Fixed: sidebar focus box + missing window icon

- Qt was drawing its own default focus-rectangle outline on top of the
  selected sidebar item, showing as a distracting box around just the text.
  Fixed with `setFocusPolicy(Qt.NoFocus)` plus explicit `outline: 0` in the
  stylesheet. Verified by actually rendering the sidebar widget to an image
  and confirming visually — not just checking the property.
- Added a real window/taskbar icon (`assets/icons/app_icon.png` /
  `app_icon.ico`), wired up in `app.py` via `setWindowIcon`.

## Colors matched to the app icon

Added `ui/theme_colors.py` as a single shared palette so colors aren't
scattered as hardcoded hex values across every widget. Icon-derived:
- Sidebar background: `#1F2937` (matches icon background exactly — this
  was already true before this pass)
- Sidebar selected item + status card accent stripe: `#64AAFF` (the
  icon's bar color, previously an unrelated gray/no accent at all)
- Page titles: navy (`#1F2937`) instead of default black

Deliberately left unchanged: green/red connection status colors — those
carry real meaning (connected/disconnected) and shouldn't be sacrificed
for brand-matching. Verified by rendering the sidebar and a status card
to actual images and visually confirming the new colors, not just
trusting the code.

The icon itself (`assets/icons/app_icon.png` / `.ico`) is fully original —
generated from scratch with basic shape-drawing code, not copied or
adapted from any existing artwork or icon pack. No licensing restriction
of any kind; use/modify/ship it freely.

## Per-page sidebar icons added

Each of the 5 sidebar items now has its own small icon
(`assets/icons/pages/*.png`), generated to match the accent-blue palette:
grid for Dashboard, sliders for Device Control, checkmark-circle for
Status, chat bubble for Communication, gear (dot-ring style) for Settings.
Verified by rendering the sidebar to an actual image, checking every
item's icon is non-null, and visually confirming each icon is distinct
and legible at real display size — not just assumed from the generation
code.

## New reusable component: PageHeader

`ui/widgets/page_header.py` — used at the top of all 5 pages now, replacing
the old plain text titles. Matches the sidebar's navy background exactly,
with the page's icon in a light accent-blue circular badge (dark navy icon
on light chip, so it's actually visible — a dark icon directly on the dark
header background would disappear), plus a left border and bottom border
in accent blue.

**Bug found and fixed while building this:** the header's navy background
and both borders silently failed to render at all — confirmed by pixel-
checking the rendered output, not just eyeballing it. Cause: plain
`QWidget` subclasses don't paint stylesheet `background`/`border` by
default in Qt; it needs `setAttribute(Qt.WA_StyledBackground, True)`,
which was missing. Fixed, then re-verified pixel-by-pixel on all 5 pages
that the navy background, badge, left border, and bottom border are all
actually present — not just assumed from the code.

## Light/dark theme system removed

Per explicit request: the Theme dropdown, `apply_theme()`, and
`services/theme_service.py` have all been fully removed — not disabled,
deleted. The app now uses whatever Qt's default native style is on your
OS, with no forced Fusion style or custom palette. `config.json` no
longer has a `theme` key at all.

**Honest note on verification:** I tested the sidebar/header color match
and title text color both *before* and *after* removing the theme system,
in this sandbox (headless Linux), and both came back correct in both
cases — pixel-identical navy background, correctly light title text. I
could not reproduce the visual mismatch that was reported on a real
Windows machine from here. Removing the theme system is still the right
call since it was explicitly unwanted, and forcing Fusion style is a
known source of subtle QSS rendering differences from native Windows
style — but if the header/sidebar still look inconsistent after this
update, it's worth a fresh screenshot to pin down the actual remaining
cause, since headless testing here has a real blind spot for
platform-specific native rendering.

## Sidebar icon now darkens when selected

Previously, the selected row's background turned accent-blue but the icon
stayed accent-blue too, so it blended in and was effectively invisible.
Fixed using Qt's built-in icon state support: each sidebar icon is now a
`QIcon` with two registered pixmaps — the normal blue variant for
`QIcon.Normal`, the dark navy variant (from `assets/icons/pages_dark/`)
for `QIcon.Selected`. Qt automatically shows the right one based on
selection state. Verified by scanning the actual rendered pixels of both
a selected and an unselected row for their respective exact colors
(navy `(31,41,55)` on selected, accent-blue `(100,170,255)` on
unselected) — not just assumed from the code.

## New layout file: ui/base_page.py — header now genuinely full-width

Added `ui/base_page.py` with a `BasePage` class every page now subclasses,
instead of each page building its own `QVBoxLayout(self)` independently
(which left default margins around the header — it looked "contained
inside" the page rather than spanning edge-to-edge like the sidebar
spans full height). `BasePage` uses a zero-margin outer layout so the
header genuinely touches the top/left/right edges, with a separate
`content_layout` (with its own padding) for each page's actual widgets.
Verified by rendering the full window and pixel-checking: header now
starts at y=0 (true top edge) and connects to the sidebar with zero gap.

Also removed the circular badge from `PageHeader` per request — icons
are now shown plainly against the navy header (same accent-blue variant
used in the sidebar), no light chip behind them. Verified by checking
that the area around each icon is plain navy, not an accent-blue circle.

## Borders simplified — subtle grey instead of thick accent blue

Per feedback, the thick accent-blue left+bottom borders on `PageHeader`
were too heavy. Replaced with:
- A single thin (1px) neutral grey divider (`BORDER_SUBTLE`, `#4B5563`)
  on the sidebar's right edge, separating it from the content area.
- The same thin grey as the header's bottom border only — the left
  border was removed entirely.

Verified pixel-exact: sidebar divider found at exactly `(75,85,99)` =
`BORDER_SUBTLE`; header's former left-border region now reads pure navy
with no accent-blue anywhere; header bottom edge shows the thin grey
line instead of the old 2px accent-blue bar.

## Logout button + header height now matches sidebar

`PageHeader` now has a Logout button on the right (outlined, matching the
subtle divider color, accent-blue on hover). Clicking it asks for
confirmation (`BasePage._on_logout_requested`) — if confirmed, it
disconnects the device (only if actually connected) and quits the app.
Verified with 3 targeted tests: clicking "No" does nothing, clicking
"Yes" while connected disconnects then quits, clicking "Yes" while
already disconnected skips the redundant disconnect call but still quits.

Header height changed from an arbitrary fixed value to exactly 50px,
matching the sidebar's actual row height (confirmed via
`Sidebar.visualItemRect`, not assumed) — so the header now lines up
visually with the sidebar instead of having its own unrelated height.

`BasePage` now takes `app_controller` directly (all 5 pages updated to
pass it through), since the logout handler needs it to know whether
there's an active connection to close.

## New reusable component: ConfirmDialog

`ui/widgets/confirm_dialog.py` — replaces the plain OS-default
`QMessageBox` (which looked jarring against the app's navy/accent theme)
with a frameless, rounded, drop-shadowed panel matching the rest of the
UI. Reusable anywhere a yes/no confirmation is needed, not just logout:

```python
if ConfirmDialog.ask(self, "Title", "Message", confirm_text="Do it", danger=True):
    ...
```

`danger=True` makes the confirm button red instead of accent-blue, for
destructive actions. `BasePage`'s logout flow now uses this instead of
`QMessageBox.question`. Verified: all 3 logout scenarios (cancel,
confirm-while-connected, confirm-while-disconnected) still pass with the
new dialog wired in, and the dialog's own rendering was pixel-checked —
confirmed the panel background color and the red confirm button both
render correctly.

## Fixed: header height was hardcoded, not derived — real root cause

The previous "header height matches sidebar" fix was a lie of sorts: I
measured the sidebar's row height once in my own test environment (got
50px) and hardcoded that number into `PageHeader`. Qt computes list row
height from font metrics + padding, which can come out differently on a
different OS/DPI/font-rendering setup — so the hardcoded 50 could easily
mismatch on a real machine even though it matched in my sandbox. That's
exactly what got reported.

Real fix: `Sidebar.row_height()` queries the sidebar's actual, live
`sizeHintForRow(0)` — not a remembered number. `MainWindow._sync_header_heights()`
runs once at startup, reads that real value, and applies it directly to
every page's header via `setFixedHeight()`. This is now correct by
construction on any machine, not just the one it happened to be measured
on. Verified all 5 headers report the sidebar's actual live height, not
a hardcoded fallback.

## Fixed: ConfirmDialog collapsed too small on a real machine, clipping button text

Reported: on a real Windows run, the dialog rendered far narrower than
intended, and the Cancel/Logout button labels showed as clipped garbage
("inc" / "go"). Cause: no explicit minimum size was set anywhere — the
dialog's size was entirely computed by Qt from its contents, which
collapsed much smaller on that machine than it had in testing here. Same
category of bug as the earlier header-height issue: never trust implicit
sizing for anything that needs to stay legible.

Fixed: explicit `setMinimumWidth(340)` on the dialog and panel,
`setMinimumSize(90, 32)` on both buttons, and a `setMinimumWidth(292)` on
the message label so word-wrap can't collapse it into a narrow column.
Also shortened the logout message from a long wrapped sentence to a
single short question, so it reads as a compact dialog rather than a
tall narrow one. Verified: measured the actual rendered button width
(89px, matching the enforced minimum) rather than just trusting the
property was set.

## Logout button is now icon-only

Replaced the "Logout" text button with a small icon-only button (34×34,
door + exit-arrow icon in `assets/icons/pages/logout.png`), with a
`setToolTip("Logout")` so the action is still discoverable without
needing a hover — tooltips are the standard accessibility fallback for
icon-only buttons. Same click behavior as before (confirm dialog →
disconnect if connected → quit). Verified: button has empty text, a
real non-null icon, correct 34×34 size, and the icon's actual pixels
were found rendering inside the button (not just an empty bordered box).
Re-ran the full logout click-through test to confirm nothing broke in
the swap from text to icon.

## Logout button is now a red circle

Changed from a bordered square (transparent, grey outline) to a solid
red circle (`STATUS_ERROR` background, `border-radius: 17px` on the
34×34 button — exactly half its size, which is what makes a square
button render as a perfect circle in Qt). Darker red on hover/press.
Verified: measured the rendered button's bounding box and confirmed the
*corners* of that box are background-colored, not red — proving it's
genuinely circular and not just a red square. Logout click-through
behavior re-verified unchanged.

## Logout icon changed to a proper power symbol

Replaced the door+arrow "exit" glyph with the standard power-button
symbol (circle with a gap at the top, vertical line through the gap) —
per reference image request. Verified geometrically, not just visually:
checked that the gap at the top is genuinely transparent on both sides
of the vertical line (not just visually appearing that way), confirmed
the circle's arc is actually present on the left/bottom, and confirmed
the vertical line passes through the gap as intended. Same red circular
button, same click behavior — only the icon artwork changed.

## Hardware test plan (the actual next milestone)

16-channel support, temperature monitoring, and the kill switch are
noted for a future phase — not needed for the current test. Right now
the only thing that matters is confirming real communication, isolated
one variable at a time:

1. **Port exists?** Check Device Manager for the COM port. If nothing
   shows up, stop here — it's a driver/USB problem, not a software one.
2. **Raw wiring test, no code at all.** RealTerm/Termite at 115200-8-N-1,
   manually send `7E 7E FF 00 00 0A 0D` (the vendor doc's literal status
   query example). Any bytes back — even garbage — means the physical
   link is alive.
3. **`scripts/hardware_smoke_test.py` — protocol layer against the real
   device, no GUI at all.** Isolates "is our byte format correct" from
   any possible GUI bug:
   ```
   python scripts/hardware_smoke_test.py COM3
   python scripts/hardware_smoke_test.py COM3 --address 5 --timeout 5
   ```
   Prints TX/RX bytes, the parsed result, and a clear SUCCESS/TIMEOUT/
   PARTIAL verdict with a specific next step for each outcome. Verified
   with 3 simulated scenarios (port-open failure, timeout, valid
   response) before relying on it — all 3 behave correctly.
4. **Only after step 3 succeeds, test the full GUI.** By then, real
   communication is already proven, so any remaining issue is purely in
   the GUI/Qt layer — a much smaller thing to debug in isolation.

## StatusCard redesigned + Output is now a real toggle switch

**StatusCard:** title is now a plain text label sitting ABOVE the card,
matching the app's other label-above-box convention (e.g. the "Output"
group box) — instead of the title and value both being stacked inside
one frame. Verified by scanning the actual rendered pixels: found two
separate bordered-frame regions (the cards) with a genuine gap between
them (no border) — exactly where each title label sits.

**Output toggle:** replaced the separate "Output ON"/"Output OFF"
buttons with a single sliding toggle switch (`ui/widgets/toggle_switch.py`,
built on `QCheckBox` with fully custom painting — track + circular knob).
Verified: rendered the switch in isolation in both states and confirmed
the knob's actual pixel position — left side when OFF (x=3-24 of 52),
right side when ON (x=27-48) — and confirmed toggling it fires
`turn_output_on()`/`turn_output_off()` correctly in order.

## Fixed: stray "(" bracket artifact on StatusCard corners

Root cause, explained properly this time: the card's accent stripe was
a thick `border-left: 4px` QSS property on the SAME frame that also had
`border-radius: 8px`. Mixing one very thick side with rounded corners
makes Qt render that corner's arc disproportionately — it looked like a
stray curved bracket sitting in front of the text. Moving the title text
out (previous fix) never addressed this — the frame still had the same
conflicting border properties.

Real fix: the accent stripe is now a **separate rectangular child
widget** (own `QFrame`, no competing border-radius fight), sitting
inside the card via layout, not a thick side-border on the same element
as the rounded corners. The outer card frame now has a clean, uniform
1px border + 8px radius with nothing to distort it. Verified pixel-by-
pixel at the corner: smooth transition, no distorted shape, stripe
correctly positioned at x=2-4 (matches enforced 4px width) spanning the
full card height.

## Fixed: StatusCard was still light-themed, clashing with the dark app

Real answer to "why is this still light": leftover from an early design
pass, never revisited after the sidebar/header shifted to dark navy.
Cards now use `DIALOG_BG` (the same dark surface color as the confirm
dialog) with light text, instead of a bright white card. Verified:
background pixel-matches `DIALOG_BG` exactly when sampled away from
text, corner remains clean (no reintroduction of the earlier bracket
bug), accent stripe still correct.

**Note on page background:** since the light/dark theme system was
removed entirely per an earlier request, the page's own background
(behind the cards, not the cards themselves) now follows whatever the
OS's native theme is — dark on a dark-mode Windows machine, light
otherwise. The sidebar/header/cards are intentionally hardcoded dark
regardless of OS setting. On a dark-mode OS this reads as one
consistent theme; on a light-mode OS the dark UI elements would sit on
a lighter page background. Flagging this now rather than silently
assuming — worth a follow-up if that combination ever comes up.

## New reusable component: SectionCard, replacing native QGroupBox

Native QGroupBox rendering (thin default border, label overlapping the
border) never matched the app's actual dark design language — it was
just Qt's unstyled default, never touched. `ui/widgets/section_card.py`
replaces it everywhere: same dark surface as StatusCard/ConfirmDialog,
consistent title styling, rounded border. `DeviceControlPage`'s Output
and Signal Settings boxes both now use this instead of QGroupBox.

**Real bug found and fixed while doing this:** after switching to the
dark `SectionCard` background, I set `background: transparent` on the
body labels (Output ON/OFF, Mode:, Bandwidth:, Power:, and
`FrequencyWidget`'s "Center Frequency:") but never set an explicit text
*color* — they fell back to a dark default, nearly invisible against
the new dark card. Confirmed by pixel-scanning the exact label region:
zero light-colored pixels found, only dark near-background blends
(the text was there, just unreadable). Fixed by adding explicit
`color: {TEXT_LIGHT}` to every one of those labels — re-ran the same
pixel scan afterward and confirmed light text pixels now present in
both the Output and Signal Settings sections.

## Packaging (Phase 6)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name SDR_Controller main.py
```

The resulting executable will be in `dist/`. Test it on the actual target
lab PC, not just the dev machine, before considering it done.
