# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
         ('assets/file/uiautomator2', 'uiautomator2'),
         ('assets/images', 'assets/images'),
         ('web/static', 'web/static'),
         ('web/templates', 'web/templates')
    ],
    hiddenimports=[
        'modules.exp.hard_task.stage_data.nt_7',
        'modules.exp.hard_task.stage_data.nt_8',
        'modules.exp.hard_task.stage_data.nt_9',
        'modules.exp.hard_task.stage_data.nt_10',
        'modules.exp.normal_task.stage_data.nt_4',
        'modules.exp.normal_task.stage_data.nt_5',
        'modules.exp.normal_task.stage_data.nt_6',
        'modules.exp.normal_task.stage_data.nt_7',
        'modules.exp.normal_task.stage_data.nt_8',
        'modules.exp.normal_task.stage_data.nt_9',
        'modules.exp.normal_task.stage_data.nt_10',
        'modules.exp.normal_task.stage_data.nt_11',
        'modules.exp.normal_task.stage_data.nt_12',
        'modules.exp.normal_task.stage_data.nt_13',
        'modules.exp.normal_task.stage_data.nt_14',
        'modules.exp.normal_task.stage_data.nt_15'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='baas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\images\\common\\ba.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='baas',
)
