# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui\\__main__.py'],
    pathex=[],
    binaries=[('venv/Lib/site-packages/PySide6/Qt6Core.dll', 'PySide6'), ('venv/Lib/site-packages/PySide6/Qt6Gui.dll', 'PySide6'), ('venv/Lib/site-packages/PySide6/Qt6Widgets.dll', 'PySide6'), ('venv/Lib/site-packages/PySide6/Qt6Network.dll', 'PySide6'), ('venv/Lib/site-packages/PySide6/Qt6Qml.dll', 'PySide6')],
    datas=[('assets', 'assets'), ('config', 'config'), ('agent', 'agent'), ('utils', 'utils'), ('requirements.txt', '.'), ('LICENSE', '.'), ('README.md', '.')],
    hiddenimports=['PySide6', 'bluetooth', 'websockets', 'groq', 'python-dotenv', 'psutil', 'pycryptodome'],
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
    a.binaries,
    a.datas,
    [],
    name='GrootiQ_Agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\ADITYA\\Desktop\\Symbiote codebase\\assets\\logo.ico'],
)
