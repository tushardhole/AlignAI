# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Use relative paths since build.py always runs from repo root
src_path = 'src'
main_py = os.path.join(src_path, 'alignai', 'main.py')

# Try to find agents package data (optional - will work without it for now)
datas_list = []
try:
    venv_lib = os.path.join('.venv', 'lib')
    if os.path.exists(venv_lib):
        for python_dir in sorted(os.listdir(venv_lib)):
            agents_path = os.path.join(venv_lib, python_dir, 'site-packages', 'agents')
            if os.path.exists(agents_path):
                datas_list.append((agents_path, 'agents'))
                break
except Exception:
    # If we can't find agents data, continue without it
    pass

a = Analysis(
    [main_py],
    pathex=[src_path],
    binaries=[],
    datas=datas_list,
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
