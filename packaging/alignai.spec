# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files and submodules from packages with non-Python data
agents_datas = collect_data_files('agents', include_py_files=False)
agents_submodules = collect_submodules('agents')

a = Analysis(
    ['../src/alignai/main.py'],
    pathex=['../src'],
    binaries=[],
    datas=agents_datas,
    hiddenimports=[
        'openai',
        'PySide6',
        'platformdirs',
        'keyring',
        'pypdf',
        'playwright',
    ] + agents_submodules,
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

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='alignai.app',
        icon=None,
        bundle_identifier=None,
    )
