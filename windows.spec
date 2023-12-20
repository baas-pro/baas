# -*- mode: python ; coding: utf-8 -*-
import os
from glob import glob

# 添加一个函数来获取给定路径下的所有Python模块名称
def find_modules(base_path):
    modules = []
    spec_dir = os.getcwd()
    prefix=base_path.replace("/", ".")+"."
    base_path_cn = os.path.join(spec_dir, base_path)
    for f in glob(os.path.join(base_path, '*.py')):
        # 忽略 __init__.py 文件
        if os.path.basename(f).startswith('__'):
            continue
        # 将文件路径转换为模块名
        module_name = os.path.splitext(os.path.relpath(f, base_path))[0].replace(os.sep, '.')
        modules.append(prefix+module_name)
    return modules

hard_task_modules = find_modules('modules/exp/hard_task/stage_data')
normal_task_modules = find_modules('modules/exp/normal_task/stage_data')
p_cn = find_modules('assets/position/cn')
p_intl = find_modules('assets/position/intl')
p_jp = find_modules('assets/position/jp')


# 打印模块列表以确认它们是否符合预期
print("Hard Task Modules:", hard_task_modules)
print("Normal Task Modules:", normal_task_modules)
print("CN Position Modules:", p_cn)
print("INTL Position Modules:", p_intl)
print("JP Position Modules:", p_jp)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
         ('assets/file/uiautomator2', 'uiautomator2'),
         ('assets/file', 'assets/file'),
         ('assets/images', 'assets/images'),
         ('web/static', 'web/static'),
         ('web/templates', 'web/templates')
    ],
    hiddenimports=[
        *hard_task_modules,
        *normal_task_modules,
        *p_cn,
        *p_intl,
        *p_jp,
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
