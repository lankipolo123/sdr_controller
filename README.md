# SDR Noise Generator Controller

Desktop control application for the 300–6000 MHz digital noise modulator,
over RS422 at 115200 baud.

[![Download for Windows](https://img.shields.io/github/v/release/lankipolo123/sdr_controller?label=Download%20for%20Windows&style=for-the-badge)](../../releases/latest)

## Install (Windows)

1. Click the download badge above (or go to the repo's [Releases](../../releases)
   page, or the **Actions** tab → "Build Windows Installer" → a completed
   run's Artifacts for a build that isn't tagged as a release yet) and
   download `SDR_Controller_Setup.exe`.
2. Double-click it and go through the installer — Start Menu shortcut,
   optional desktop shortcut, and an uninstaller are all set up for you.
3. Launch it from the Start Menu like any other app.

No Python, no terminal, nothing else to install.

## Development setup

```bash
pip install -r requirements.txt
python main.py
```

## Layout

```
main.py / app.py            entry point + bootstrap
controller/                 coordination layer (never touches bytes or ports directly)
  app_controller.py           composition root — wires everything together
  connection_controller.py    connect/disconnect lifecycle, exposes Qt signals only
  device_controller.py        the only place that calls protocol.commands
protocol/                   binary RS422 protocol
  constants.py, packet_builder.py, packet_parser.py, commands.py
  test_protocol.py            run: python -m protocol.test_protocol
serial_io/                  physical I/O (named serial_io, not serial — see note below)
  serial_manager.py            open/close/read/write, no threading
  serial_thread.py             background read loop (QThread)
models/
  device_state.py              single source of truth; pages subscribe to `changed`
services/
  config_service.py            JSON config load/save
  logging_service.py           rotating file logger
  app_paths.py                 writable config/log paths (dev vs. packaged build)
ui/
  main_window.py, sidebar.py
  pages/                        Dashboard, Device Control, Communication
  widgets/                      Card, ComboBox, ToggleSwitch, EmergencyStopButton,
                                 FrequencyWidget, ActivityChart, HexLineDisplay,
                                 TerminalWidget, ConfirmDialog, and more
build.spec                  PyInstaller build config
installer.iss               Inno Setup script that wraps the build into Setup.exe
.github/workflows/          CI that builds the installer on a real Windows runner
```

## Design note: why `serial_io/` instead of `serial/`

The original architecture spec named this folder `serial/`. That collides
with the third-party `pyserial` package, which is also imported as
`import serial` — a local `serial/` package on the Python path would shadow
it and break every serial import in the project. Renamed to `serial_io/`
to avoid that; nothing else about the design changed.

## Building the installer yourself

Push a version tag to trigger a build automatically:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions builds the executable with PyInstaller, wraps it with Inno
Setup on a Windows runner, and attaches `SDR_Controller_Setup.exe` to the
resulting GitHub Release. You can also trigger a one-off build without
tagging a release from the **Actions** tab → "Build Windows Installer" →
**Run workflow**.

## Known open items

- Real hardware validation over the actual RS422 link is the next
  milestone — see `scripts/hardware_smoke_test.py` for a protocol-only
  test against real hardware, no GUI involved.
- Multi-channel/multi-address support and temperature monitoring are
  deferred — the protocol has no field for temperature at all currently.
