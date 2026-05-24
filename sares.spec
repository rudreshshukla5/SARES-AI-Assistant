# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['sares.py'],
    pathex=[],
    binaries=[('/Users/rudreshshukla/SARES/sares_env/lib/python3.14/site-packages/pvporcupine/lib/mac/arm64/libpv_porcupine.dylib', 'pvporcupine/lib/mac/arm64/')],
    datas=[('Buddy.ppn', '.'), ('/Users/rudreshshukla/SARES/sares_env/lib/python3.14/site-packages/pvporcupine/resources', 'pvporcupine/resources'), ('/Users/rudreshshukla/SARES/sares_env/lib/python3.14/site-packages/pvporcupine/lib/common', 'pvporcupine/lib/common')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SARES',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SARES',
)
app = BUNDLE(
    coll,
    name='SARES.app',
    icon=None,
    bundle_identifier=None,
)
