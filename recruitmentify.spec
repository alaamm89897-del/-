# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Changed from admin.py to main.py
    pathex=['C:/Users/Suliman/Desktop/companies'],  # Path to your project
    binaries=[],
    datas=[
        ('recruitmentify.json', '.'),  # Include Firebase credentials
        ('session.json', '.'),  # Include session data
    ],
    hiddenimports=[
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.db',
        'firebase_connection',
        'session_handler',
        'jops_panel',
        'dashboard',
        'admin',  # Added admin as an import
        'login',  # Added login as an import
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
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

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Recruitmentify',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    icon=None,  # You can add an icon file here if you have one
)
