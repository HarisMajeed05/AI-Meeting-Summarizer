# -*- mode: python ; coding: utf-8 -*-

# Add ffmpeg binaries
ffmpeg_binaries = [
    ('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin'),
    ('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin'),
    ('ffmpeg/bin/ffplay.exe', 'ffmpeg/bin'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=ffmpeg_binaries,        # <-- IMPORTANT
    datas=[
        ('meeting_summarizer', 'meeting_summarizer'),
        ('core', 'core'),
        ('webapp', 'webapp'),
        ('webapp/templates', 'webapp/templates')
    ],
    hiddenimports=[
        'django',
        'django.contrib',
        'django.contrib.staticfiles',
        'django.template'
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
    a.binaries,
    a.datas,
    [],
    name='AI-Meeting-Summarizer',
    icon='myicon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
