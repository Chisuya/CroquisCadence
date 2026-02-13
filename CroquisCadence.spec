# -*- mode: python ; coding: utf-8 -*-
import os

# Get the project root directory
project_root = os.path.abspath('.')

block_cipher = None

a = Analysis(
    ['gui/main_window.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'assets'), 'assets'),  # Absolute path to assets
        (os.path.join(project_root, 'README.txt'), '.'),   # Absolute path to README
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CroquisCadence',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icon.ico'),  # App icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CroquisCadence',
)
