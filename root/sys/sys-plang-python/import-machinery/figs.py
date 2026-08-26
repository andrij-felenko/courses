# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Механіка імпорту' (import-machinery)."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_import_pipeline():
    """Етапи виконання інструкції import від виклику до розміщення в sys.modules."""
    w, h = 980, 580
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Конвеєр виконання імпорту в CPython (PEP 451)", size=16, bold=True))

    stages = [
        ("1. Запит і перевірка кешу", [
            "Інструкція IMPORT_NAME / __import__()",
            "Захоплення блокування імпорту",
            "Пошук ключа у словнику sys.modules",
            "Знайдено -> повернення модуля"
        ], "#eaf0fd", NEG),

        ("2. Пошук специфікації (Finders)", [
            "Обхід знахідників у sys.meta_path",
            "Виклик finder.find_spec(name, path)",
            "Пошук: Builtin -> Frozen -> PathFinder",
            "Формування об'єкта ModuleSpec"
        ], "#fdecea", POS),

        ("3. Створення об'єкта модуля", [
            "Виклик spec.loader.create_module()",
            "Алокація об'єкта types.ModuleType",
            "Ініціалізація __name__, __spec__",
            "Попередній запис у sys.modules"
        ], "#e8f8f0", FIELD),

        ("4. Виконання коду (Execution)", [
            "Виклик spec.loader.exec_module()",
            "Компіляція або читання байткоду .pyc",
            "Виконання PyCodeObject у dict модуля",
            "Помилка -> відкат із sys.modules"
        ], "#fef9e7", "#b78103")
    ]

    bx, bw, bh = 40, 200, 210
    gap = 40
    y_top = 70

    for i, (title, points, fill_c, stroke_c) in enumerate(stages):
        cur_x = bx + i * (bw + gap)
        frags.append(rect(cur_x, y_top, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        frags.append(text(cur_x + bw / 2, y_top + 28, title, size=12, bold=True, color=stroke_c))
        frags.append(line(cur_x + 10, y_top + 42, cur_x + bw - 10, y_top + 42, color=stroke_c, sw=1))

        py = y_top + 66
        for pt in points:
            frags.append(circle(cur_x + 16, py - 4, 3, fill=stroke_c, stroke=stroke_c))
            frags.append(text(cur_x + 26, py, pt, size=10, anchor="start", color=INK))
            py += 34

        # Стрілка до наступного блоку
        if i < len(stages) - 1:
            arr_x1 = cur_x + bw + 4
            arr_x2 = cur_x + bw + gap - 4
            frags.append(arrow(arr_x1, y_top + bh / 2, arr_x2, y_top + bh / 2, color=MUTED, sw=2))

    # Нижній блок: ключові системні структури та інваріанти
    frags.append(rect(40, 320, 900, 230, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(490, 348, "Ключові структури середовища та їхня взаємодія", size=14, bold=True))

    sub_cards = [
        (60, 370, 260, 160, "sys.modules", [
            "Глобальний словник-кеш (dict)",
            "Зберігає всі завантажені модулі",
            "Запобігає повторному парсингу",
            "Розв'язує циклічні залежності"
        ], NEG),
        (360, 370, 260, 160, "ModuleSpec (PEP 451)", [
            "name: кваліфікована назва",
            "loader: виконавець завантаження",
            "origin: джерело (файл / пам'ять)",
            "submodule_search_locations"
        ], FIELD),
        (660, 370, 260, 160, "sys.meta_path", [
            "Список об'єктів MetaPathFinder",
            "1. BuiltinImporter (C-модулі)",
            "2. FrozenImporter (байткод ядра)",
            "3. PathFinder (файлова система)"
        ], POS),
    ]

    for sx, sy, sw_c, sh_c, stitle, slines, scolor in sub_cards:
        frags.append(rect(sx, sy, sw_c, sh_c, fill=BG, stroke=scolor, sw=1.5, rx=6))
        frags.append(text(sx + sw_c / 2, sy + 24, stitle, size=12, bold=True, color=scolor))
        frags.append(line(sx + 10, sy + 36, sx + sw_c - 10, sy + 36, color=scolor, sw=0.8))
        s_py = sy + 58
        for sl in slines:
            frags.append(circle(sx + 16, s_py - 4, 2.5, fill=scolor, stroke=scolor))
            frags.append(text(sx + 26, s_py, sl, size=11, anchor="start", color=INK))
            s_py += 24

    render(os.path.join(OUT_DIR, "fig-import-pipeline.svg"), w, h, *frags)


def fig_meta_path_traversal():
    """Схема обходу знахідників у sys.meta_path та делегування PathFinder."""
    w, h = 960, 520
    frags = []

    frags.append(text(w / 2, 28, "Диспетчеризація знахідників у sys.meta_path", size=16, bold=True))

    # Лівий блок: виклик
    frags.append(rect(40, 70, 200, 100, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(140, 105, "Запит імпорту", size=13, bold=True, color=NEG))
    frags.append(text(140, 130, "import pkg.module", size=12, color=INK))
    frags.append(text(140, 150, "fullname = 'pkg.module'", size=10, color=MUTED))

    frags.append(arrow(240, 120, 310, 120, color=LINE, sw=2))
    frags.append(text(275, 110, "пошук", size=11, color=MUTED))

    # Центральний стовпчик: sys.meta_path
    frags.append(rect(310, 55, 310, 440, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(465, 82, "sys.meta_path (список Finders)", size=14, bold=True))

    finders = [
        ("1. BuiltinImporter", "Пошук у compiled-in C модулях\n(sys, builtins, _ast)", "#fdecea", POS),
        ("2. FrozenImporter", "Пошук у байткоді ядра CPython\n(_frozen_importlib, _bootstrap)", "#e8f8f0", FIELD),
        ("3. PathFinder", "Пошук на диску через sys.path\nабо батьківський pkg.__path__", "#eaf0fd", NEG),
    ]

    fy = 100
    for fname, fdesc, ffill, fstroke in finders:
        frags.append(rect(325, fy, 280, 78, fill=ffill, stroke=fstroke, sw=1.5, rx=6))
        frags.append(text(465, fy + 22, fname, size=12, bold=True, color=fstroke))
        desc_lines = fdesc.split("\n")
        frags.append(text(465, fy + 44, desc_lines[0], size=10, color=INK))
        frags.append(text(465, fy + 60, desc_lines[1], size=10, color=MUTED))
        fy += 92

    # Додатковий користувацький знахідник
    frags.append(rect(325, fy, 280, 78, fill="#fef9e7", stroke="#b78103", sw=1.5, rx=6))
    frags.append(text(465, fy + 22, "4. Користувацький Finder", size=12, bold=True, color="#b78103"))
    frags.append(text(465, fy + 44, "Імпорт із zip, пам'яті, мережі", size=10, color=INK))
    frags.append(text(465, fy + 60, "sys.meta_path.insert(0, ...)", size=10, color=MUTED))

    # Стрілка від PathFinder праворуч
    frags.append(arrow(605, 323, 680, 323, color=NEG, sw=2))
    frags.append(text(642, 312, "делегує", size=11, color=NEG))

    # Правий блок: механіка PathFinder
    frags.append(rect(680, 220, 240, 260, fill=BG, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(800, 246, "Механізм PathFinder", size=13, bold=True, color=NEG))
    frags.append(line(695, 258, 905, 258, color=NEG, sw=0.8))

    pf_steps = [
        ("sys.path_hooks", "Список фабрик для шляхів"),
        ("sys.path_importer_cache", "Кеш екземплярів знахідників"),
        ("FileFinder", "Сканує файловий каталог"),
        ("SourceFileLoader", "Завантажує .py файли"),
        ("ExtensionFileLoader", "Завантажує .so / .pyd")
    ]

    pf_y = 282
    for stitle, ssub in pf_steps:
        frags.append(circle(700, pf_y - 4, 3, fill=NEG, stroke=NEG))
        frags.append(text(710, pf_y, stitle, size=11, bold=True, anchor="start", color=INK))
        frags.append(text(710, pf_y + 14, ssub, size=9, anchor="start", color=MUTED))
        pf_y += 34

    # Вихід унизу
    frags.append(rect(40, 240, 200, 110, fill="#e8f8f0", stroke=FIELD, sw=2, rx=8))
    frags.append(text(140, 272, "Результат пошуку", size=13, bold=True, color=FIELD))
    frags.append(text(140, 298, "Повертає ModuleSpec", size=12, color=INK))
    frags.append(text(140, 322, "або None (не знайдено)", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "fig-meta-path-traversal.svg"), w, h, *frags)


def fig_module_vs_package():
    """Порівняння структури файлового модуля, звичайного пакунка та Namespace-пакунка."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Порівняння структури модулів і пакунків у CPython", size=16, bold=True))

    cards = [
        (40, 70, 275, 410, "1. Звичайний модуль (Leaf)", [
            ("Файл", "math.py або regex.so"),
            ("Ознака", "Окремий файл без каталогу"),
            ("__path__", "Відсутній (атрибут не задано)"),
            ("Підмодулі", "Не може мати дочірніх модулів"),
            ("Завантажувач", "SourceFileLoader / ExtensionLoader"),
            ("origin", "Повний шлях до .py / .so файлу")
        ], NEG, "#eaf0fd"),

        (352, 70, 275, 410, "2. Регулярний пакунок", [
            ("Каталог", "pkg/ з файлом __init__.py"),
            ("Ознака", "Наявність файлу __init__.py"),
            ("__path__", "Список із одного шляху: ['pkg/']"),
            ("Підмодулі", "Пошук ведеться всередині pkg/"),
            ("Завантажувач", "SourceFileLoader для __init__.py"),
            ("origin", "Шлях до pkg/__init__.py")
        ], FIELD, "#e8f8f0"),

        (665, 70, 275, 410, "3. Просторовий пакунок (PEP 420)", [
            ("Каталоги", "Каталоги без __init__.py по sys.path"),
            ("Ознака", "Відсутність __init__.py"),
            ("__path__", "_NamespacePath з кількох каталогів"),
            ("Підмодулі", "Пошук об'єднує всі каталоги"),
            ("Завантажувач", "_NamespaceLoader (без коду)"),
            ("origin", "None (немає фізичного файлу)")
        ], POS, "#fdecea")
    ]

    for cx, cy, cw, ch, ctitle, cfields, ccolor, cfill in cards:
        frags.append(rect(cx, cy, cw, ch, fill=cfill, stroke=ccolor, sw=2, rx=8))
        frags.append(text(cx + cw / 2, cy + 30, ctitle, size=13, bold=True, color=ccolor))
        frags.append(line(cx + 12, cy + 45, cx + cw - 12, cy + 45, color=ccolor, sw=1))

        fy = cy + 72
        for ftitle, fval in cfields:
            frags.append(rect(cx + 12, fy - 16, cw - 24, 46, fill=BG, stroke=LINE, sw=0.8, rx=4))
            frags.append(text(cx + 20, fy - 2, ftitle, size=10, bold=True, anchor="start", color=ccolor))
            frags.append(text(cx + 20, fy + 16, fval, size=10, anchor="start", color=INK))
            fy += 54

    render(os.path.join(OUT_DIR, "fig-module-vs-package.svg"), w, h, *frags)


def fig_pyc_format():
    """Бінарна структура кешованого файлу .pyc у каталозі __pycache__."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Бінарна структура файлу байткоду .pyc (Python 3.7+)", size=16, bold=True))

    # Загальний контейнер
    frags.append(rect(40, 65, 900, 420, fill=FILL, stroke=LINE, sw=1.5, rx=8))

    # Секція заголовка: 16 байтів
    frags.append(rect(60, 95, 860, 190, fill=BG, stroke=NEG, sw=2, rx=6))
    frags.append(text(490, 122, "Заголовок файлу .pyc (16 байтів / 4 слова по 32 біти)", size=13, bold=True, color=NEG))

    fields = [
        (80, 145, 185, 115, "Байти 0..3 (4B)", "Magic Number", [
            "2B: версія байткоду",
            "2B: константа \\r\\n",
            "Приклад: 0x0A0D0D34"
        ], NEG),

        (285, 145, 185, 115, "Байти 4..7 (4B)", "Bit Field (Прапорці)", [
            "біт 0: 0=mtime, 1=hash",
            "біт 1: check / uncheck",
            "Стандарт PEP 552"
        ], FIELD),

        (490, 145, 210, 115, "Байти 8..11 (4B)", "Timestamp / Hash[0..3]", [
            "Час модифікації (mtime)",
            "або перші 4 байти",
            "хешу SIPHASH-24"
        ], POS),

        (720, 145, 180, 115, "Байти 12..15 (4B)", "File Size / Hash[4..7]", [
            "Розмір .py файлу (bytes)",
            "або другі 4 байти",
            "хешу SIPHASH-24"
        ], "#b78103")
    ]

    for fx, fy, fw, fh, fbytes, ftitle, fdesc, fcolor in fields:
        frags.append(rect(fx, fy, fw, fh, fill="#f8fafc", stroke=fcolor, sw=1.2, rx=5))
        frags.append(text(fx + fw / 2, fy + 20, fbytes, size=10, bold=True, color=MUTED))
        frags.append(text(fx + fw / 2, fy + 38, ftitle, size=11, bold=True, color=fcolor))
        frags.append(line(fx + 8, fy + 48, fx + fw - 8, fy + 48, color=fcolor, sw=0.6))
        d_y = fy + 64
        for dl in fdesc:
            frags.append(text(fx + fw / 2, d_y, dl, size=9.5, color=INK))
            d_y += 16

    # Секція тіла: PyCodeObject
    frags.append(rect(60, 305, 860, 155, fill=BG, stroke=POS, sw=2, rx=6))
    frags.append(text(490, 332, "Корисне навантаження: маршалізований PyCodeObject (Байти 16..кінець)", size=13, bold=True, color=POS))

    code_fields = [
        (80, 352, 255, 90, "marshal.dump(code_object)", [
            "Серіалізована структура коду",
            "Константи co_consts, імена co_names",
            "Таблиця рядків co_linetable"
        ]),
        (360, 352, 255, 90, "co_code (Байткод-інструкції)", [
            "Послідовність 16-бітних слів інструкцій",
            "Опокоди: LOAD_FAST, STORE_NAME...",
            "Таблиця переходів та обробників"
        ]),
        (640, 352, 260, 90, "Десеріалізація через C-API", [
            "PyMarshal_ReadObjectFromString()",
            "Швидке відновлення без парсингу тексту",
            "Перевірка цілісності об'єкта"
        ])
    ]

    for cx, cy, cw, ch, ctitle, cdesc in code_fields:
        frags.append(rect(cx, cy, cw, ch, fill="#fdf2f2", stroke=POS, sw=1, rx=5))
        frags.append(text(cx + cw / 2, cy + 22, ctitle, size=11, bold=True, color=POS))
        frags.append(line(cx + 8, cy + 32, cx + cw - 8, cy + 32, color=POS, sw=0.6))
        c_y = cy + 48
        for cdl in cdesc:
            frags.append(text(cx + cw / 2, c_y, cdl, size=9.5, color=INK))
            c_y += 16

    render(os.path.join(OUT_DIR, "fig-pyc-format.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_import_pipeline()
    fig_meta_path_traversal()
    fig_module_vs_package()
    fig_pyc_format()
    print("Всі 4 фігури успішно згенеровано у", OUT_DIR)
