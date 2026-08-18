from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# PyArmor replaces every obfuscated file's real content with a single
# `__pyarmor__(__name__, __file__, b'<encrypted blob>')` call - the
# actual `import`/`from X import Y` statements only exist inside that
# encrypted blob at runtime, not as literal source PyInstaller's static
# analyzer can parse. So Analysis() can only ever "see" main.py's one
# visible import (pyarmor_runtime_000000) - every module the app
# actually needs (app.py, and everything under controller/, models/,
# protocol/, serial_io/, services/, ui/) is invisible to it and has to
# be listed explicitly, or the built .exe crashes on launch with
# ModuleNotFoundError the moment it needs the first one.
# collect_submodules() walks the filesystem (not import statements) to
# enumerate every real submodule in a package, which is exactly what's
# needed here since there's nothing else to statically trace.
# It's not just this app's own modules that go dark - every import
# statement anywhere in the obfuscated tree is equally invisible,
# including the ones pulling in third-party libraries. Confirmed by
# testing: fixing the internal-package gap alone still crashed with
# "No module named 'PySide6'", because app.py's own
# `from PySide6.QtWidgets import ...` line is inside the same encrypted
# blob as everything else. So the actually-used PySide6 submodules
# (matching UNUSED_QT_MODULES below - keep this list in sync, don't
# blanket collect_submodules("PySide6") or it undoes that exclusion
# work) plus the other two third-party dependencies (requirements.txt:
# qtawesome, pyserial) need the same explicit treatment as this app's
# own packages.
OBFUSCATED_APP_PACKAGES = [
    "controller", "models", "protocol", "serial_io", "services", "ui",
]
USED_PYSIDE6_SUBMODULES = [
    "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "PySide6.QtCharts",
]
# Same invisibility problem applies to standard-library submodules that
# aren't part of PyInstaller's default base_library.zip bundling -
# logging.handlers (RotatingFileHandler, used by services/logging_service.py)
# is only pulled in via a static `from logging.handlers import ...` line
# normally, which is exactly the kind of statement that's now hidden.
STDLIB_HIDDEN_IMPORTS = ["logging.handlers"]

THIRD_PARTY_HIDDEN_IMPORTS = (
    USED_PYSIDE6_SUBMODULES
    + collect_submodules("qtawesome")
    + collect_submodules("serial")
    + STDLIB_HIDDEN_IMPORTS
)
APP_HIDDEN_IMPORTS = (
    ["app"]
    + [m for pkg in OBFUSCATED_APP_PACKAGES for m in collect_submodules(pkg)]
    + THIRD_PARTY_HIDDEN_IMPORTS
)

# PySide6's PyInstaller hook bundles the entire Qt runtime by default -
# WebEngine, Qml, Multimedia, Sql, Bluetooth, 3D, etc: dozens of modules
# this app never touches, 100MB+ on their own. Actual usage is just
# QtCharts/QtCore/QtGui/QtWidgets (confirmed via
# `grep -rh "^from PySide6\." --include='*.py' .`), plus QtCore/QtGui/
# QtWidgets pulled in by qtawesome for icons - qtawesome renders icons
# via font glyphs, not QtSvg (verified by blocking QtSvg/QtSvgWidgets
# imports and confirming icon rendering still works), so those are safe
# to exclude too.
UNUSED_QT_MODULES = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuick3D",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtSpatialAudio",
    "PySide6.QtNetwork", "PySide6.QtNetworkAuth", "PySide6.QtWebSockets", "PySide6.QtWebChannel",
    "PySide6.QtSql", "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtSerialPort", "PySide6.QtSerialBus",
    "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras",
    "PySide6.QtSvg", "PySide6.QtSvgWidgets",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets",
    "PySide6.QtSensors", "PySide6.QtPositioning", "PySide6.QtLocation",
    "PySide6.QtRemoteObjects", "PySide6.QtDesigner", "PySide6.QtUiTools", "PySide6.QtHelp",
    "PySide6.QtTest", "PySide6.QtXml", "PySide6.QtPrintSupport",
    "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets", "PySide6.QtStateMachine",
    "PySide6.QtTextToSpeech", "PySide6.QtDataVisualization", "PySide6.QtScxml",
    "PySide6.QtVirtualKeyboard", "PySide6.QtWebView", "PySide6.QtHttpServer",
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
    ],
    hiddenimports=APP_HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=UNUSED_QT_MODULES,
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SDR_Controller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX-compressed executables are a well-known antivirus/SmartScreen
    # false-positive trigger - the compression pattern resembles how
    # malware packers work, and it's compounded here by PyArmor's own
    # obfuscation doing something heuristically similar. Disabling it
    # trades a larger .exe for fewer AV/SmartScreen false flags; it
    # doesn't fully remove Windows' "unknown publisher" warning (only a
    # paid code-signing certificate does that), but it's a real, free
    # reduction in how suspicious the binary looks to heuristic scanners.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='assets/icons/app_icon.ico',
)
