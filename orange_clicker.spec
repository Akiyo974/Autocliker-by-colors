# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Orange Clicker
# Build : python -m PyInstaller orange_clicker.spec

block_cipher = None

a = Analysis(
    ['orange_clicker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cv2',
        'mss',
        'mss.windows',
        'pyautogui',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._win32',
        'pynput.mouse',
        'pynput.mouse._win32',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'tkinter.colorchooser',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'PIL', 'PyQt5', 'wx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrangeClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=True  → requis pour --cli (affiche stdout/stderr)
    # console=False → fenêtre noire invisible pour GUI seul
    # On garde console=True pour que le mode --cli fonctionne.
    # La fenêtre console se ferme instantanément en mode GUI.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
