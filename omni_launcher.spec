# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.datastruct import Tree


a = Analysis(
    ['omni_launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['ui', 'ui.backend', 'ui.backend.app'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

a.datas += Tree('ui', prefix='ui')
a.datas += Tree('domain', prefix='domain')
a.datas += Tree('metadata', prefix='metadata')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,    
    a.scripts,
    [],
    exclude_binaries=True,
    name='OmniDeck Suite',
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
    name='OmniDeck Suite',
)

app = BUNDLE(
    coll,
    name='OmniDeck Suite.app',
    icon='tools/build/assets/omnideck_icon.icns',
    bundle_identifier='com.diego.omnidecksuite',
    info_plist={
        "CFBundleName": "OmniDeck Suite",
        "CFBundleDisplayName": "OmniDeck Suite",
        "CFBundleIdentifier": "com.diego.omnidecksuite",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
        "LSUIElement": False,
    },
)
