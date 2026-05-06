# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files and submodules for packages with non-Python data
# (PyInstaller only bundles .py files automatically)
agents_datas = collect_data_files('agents', include_py_files=False)
agents_submodules = collect_submodules('agents')

# trafilatura ships a settings.cfg used by its config parser
trafilatura_datas = collect_data_files('trafilatura', include_py_files=False)

# justext (used by trafilatura) ships language stoplist .txt files
justext_datas = collect_data_files('justext', include_py_files=False)

# certifi ships cacert.pem for HTTPS certificate validation
certifi_datas = collect_data_files('certifi', include_py_files=False)

# Bundle alignai package data files (templates, prompts)
alignai_datas = [
    ('../src/alignai/infra/templates', 'alignai/infra/templates'),
    ('../src/alignai/agents/prompts', 'alignai/agents/prompts'),
]

a = Analysis(
    ['../src/alignai/main.py'],
    pathex=['../src'],
    binaries=[],
    datas=(
        agents_datas
        + trafilatura_datas
        + justext_datas
        + certifi_datas
        + alignai_datas
    ),
    hiddenimports=[
        'openai',
        'PySide6',
        'platformdirs',
        'keyring',
        'keyring.backends.macOS',
        'keyring.backends.Windows',
        'keyring.backends.SecretService',
        'keyring.backends.kwallet',
        'pypdf',
        'docx',
        'jinja2',
        'playwright',
        'trafilatura',
        'justext',
        'certifi',
        'httpx',
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
