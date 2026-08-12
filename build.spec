block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
