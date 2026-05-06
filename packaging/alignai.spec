# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Get absolute path to the repo root
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, 'src')

a = Analysis(
    [os.path.join(src_path, 'alignai', 'main.py')],
    pathex=[src_path],
    binaries=[],
    datas=[],
    hiddenimports=[
        'agents',
        'openai',
        'PySide6',
        'platformdirs',
        'keyring',
        'pypdf',
        'playwright',
    ],
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
    name='alignai',
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
    name='alignai',
)

# macOS app bundle (ignored on Windows/Linux)
import sys

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='alignai.app',
        icon=None,
        bundle_identifier=None,
    )
