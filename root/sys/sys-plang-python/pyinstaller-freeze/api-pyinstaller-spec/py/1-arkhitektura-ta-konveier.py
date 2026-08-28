# Приклад розширеного app.spec для комбінованого застосунку
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

# 1. ЕТАП: Статичний аналіз коду, парсинг AST та агрегація залежностей
a = Analysis(
    ['src/entrypoint.py'],
    pathex=['src'],
    binaries=[
        ('vendor/libcustom.so', '.')            # Кортеж: (вихідний шлях на хості, цільова тека в бандлі)
    ],
    datas=[
        ('config/*.yaml', 'config'),
        ('assets/logo.png', 'assets')
    ] + collect_data_files('certifi') + copy_metadata('cryptography'),
    hiddenimports=[
        'pkg_resources.py2_warn',
        'sqlalchemy.dialects.sqlite'
    ] + collect_submodules('my_plugins'),
    hookspath=['build_hooks'],
    hooksconfig={},
    runtime_hooks=['build_hooks/runtime_init.py'],
    excludes=['tkinter', 'unittest', 'pytest', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# 2. ЕТАП: Компіляція та компресія чистого Python-байткоду в PYZ-контейнер
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# 3. ЕТАП: Компонування двійкового завантажувача з PYZ та прапорцями виконання
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,                       # True для режиму onedir, False для режиму onefile
    name='my_application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,                                # Видалення налагоджувальних символів через strip
    upx=True,                                   # Стиснення бінарників алгоритмом UPX
    upx_exclude=['vcruntime140.dll'],           # Виключення нестабільних DLL з UPX-компресії
    runtime_tmpdir=None,                        # Перевизначення базового каталогу для _MEIxxxxxx
    console=True,                               # Запуск у консолі (True) або прихований GUI-режим (False)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico'
)

# 4. ЕТАП: Формування кінцевого каталогу розгортання (використовується лише для --onedir)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='my_application'
)
