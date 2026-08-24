# -*- mode: python ; coding: utf-8 -*-
# build ด้วย: pyinstaller main.spec   (รันจากโฟลเดอร์หลักของโปรเจกต์)

import os

icon = 'icon.ico' if os.path.exists('icon.ico') else None

a = Analysis(
    ['mainproject/main.py'],
    pathex=['mainproject'],          # ให้หา downloader.py เจอ
    binaries=[],
    datas=[],
    hiddenimports=['downloader'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # ไม่ต้องมีหน้าต่างดำโผล่คู่กับ GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
