# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми pyinstaller-freeze."""

import sys
import os

# Імпорт спільних помічників svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_frozen_executable_anatomy():
    """Фігура 1: Анатомія замороженого двійкового файлу (One-File executable)."""
    w, h = 880, 520
    frags = []

    # Заголовок блоків
    frags.append(text(220, 35, "Структура автономного бінарного файлу (.exe / ELF)", size=16, bold=True))
    frags.append(text(660, 35, "Призначення та обробка компонента", size=16, bold=True))

    # Секції двійкового образу зліва (вертикальний стек)
    y_start = 65
    box_w = 340

    sections = [
        ("Заголовок образу (ELF / PE / Mach-O)", 45, "#e8eaf6", "#3949ab",
         "Містить точку входу, заголовки секцій і розмітку віртуальної пам'яті для ОС."),
        ("Завантажувач (Bootloader на C)", 65, "#e3f2fd", "#1e88e5",
         "Скомпільований нативний код: шукає хвіст архіву, розпаковує файли та викликає CPython API."),
        ("Зміст архіву (Table of Contents / TOC)", 55, "#f3e5f5", "#8e24aa",
         "Карта зміщених блоків: імена файлів, розміри, прапорці стиснення та цільові підкаталоги."),
        ("Спільні бібліотеки (.so / .dll) та C-розширення (.pyd)", 65, "#e0f2f1", "#00897b",
         "Бінарні залежності: libpython, C-модулі (numpy, cryptography) та системні DLL."),
        ("Архів байткоду (PYZ / ZlibArchive)", 65, "#fff8e1", "#f57f17",
         "Стиснені скомпільовані модулі .pyc стандартної бібліотеки та застосунку без сирців."),
        ("Ресурси даних (Data Files & Assets)", 55, "#fbe9e7", "#d84315",
         "Вбудовані небінарні файли: конфігурації, іконки, SSL-сертифікати, статичні шаблони."),
        ("Кінцева мітка (Cookie / Trailer)", 45, "#ffebee", "#c62828",
         "Службовий хвіст: зміщення до TOC, магічний рядок MEI, версія пакувальника.")
    ]

    cur_y = y_start
    for title, bh, fill_c, stroke_c, desc in sections:
        # Лівий блок бінарника
        bx = 50
        frags.append(fitbox(bx, cur_y, box_w, bh, title, size=13, fill=fill_c, stroke=stroke_c, bold=True))
        
        # Стрілка зв'язку
        mid_y = cur_y + bh / 2
        frags.append(arrow(bx + box_w + 10, mid_y, bx + box_w + 60, mid_y, color=stroke_c))

        # Правий блок опису
        frags.append(fitbox(bx + box_w + 70, cur_y, 400, bh, desc, size=12, fill="#fafafa", stroke="#cfd8dc"))

        cur_y += bh + 8

    render(os.path.join(OUT_DIR, "frozen-executable-anatomy.svg"), w, h, *frags)


def fig_onedir_vs_onefile_lifecycle():
    """Фігура 2: Життєвий цикл One-Folder проти One-File."""
    w, h = 900, 480
    frags = []

    # Ліва колонка: One-Folder
    col1_x = 40
    col_w = 390
    frags.append(text(col1_x + col_w / 2, 35, "Режим One-Folder (--onedir)", size=16, bold=True, color="#1565c0"))
    frags.append(rect(col1_x, 50, col_w, 410, fill="#f8fafc", stroke="#94a3b8", rx=8))

    onedir_steps = [
        ("1. Запуск двійкового файлу в каталозі", 48,
         "Користувач запускає ./my_app. Бінарник лежить поруч із каталогом _internal."),
        ("2. Пряме завантаження DLL / .so на місці", 56,
         "Завантажувач налаштовує шляхи пошуку бібліотек на локальний каталог без копіювання."),
        ("3. Ініціалізація CPython і запуск коду", 56,
         "sys.frozen=True, sys._MEIPASS вказує на поточну теку застосунку. Байткод читається з PYZ."),
        ("4. Миттєвий старт без I/O накладних витрат", 52,
         "Дисковий ввід/вивід мінімальний: файли не розпаковуються у тимчасові теки.")
    ]

    sy = 70
    for title, bh, desc in onedir_steps:
        frags.append(fitbox(col1_x + 15, sy, col_w - 30, bh, f"{title}\n{desc}", size=11, fill="#ffffff", stroke="#0288d1"))
        if sy + bh + 30 < 450:
            frags.append(arrow(col1_x + col_w / 2, sy + bh + 2, col1_x + col_w / 2, sy + bh + 18, color="#0288d1"))
        sy += bh + 22

    # Права колонка: One-File
    col2_x = 470
    frags.append(text(col2_x + col_w / 2, 35, "Режим One-File (--onefile)", size=16, bold=True, color="#c2410c"))
    frags.append(rect(col2_x, 50, col_w, 410, fill="#fffaf5", stroke="#fdba74", rx=8))

    onefile_steps = [
        ("1. Запуск єдиного саморозпаковного файлу", 48,
         "Завантажувач вичитує зміщення з власного хвоста і знаходить вбудований TOC."),
        ("2. Створення тимчасового каталогу _MEIxxxxxx", 56,
         "У /tmp або %TEMP% створюється унікальна тека, куди розпаковуються .so, DLL та ресурси."),
        ("3. Ініціалізація CPython із sys._MEIPASS", 56,
         "sys._MEIPASS вказує на _MEIxxxxxx. Імпортер монтує PYZ, виконується точка входу."),
        ("4. Завершення процесу та очищення", 52,
         "При коректному виході завантажувач рекурсивно видаляє теку _MEI. При збої тека лишається.")
    ]

    sy = 70
    for title, bh, desc in onefile_steps:
        frags.append(fitbox(col2_x + 15, sy, col_w - 30, bh, f"{title}\n{desc}", size=11, fill="#ffffff", stroke="#ea580c"))
        if sy + bh + 30 < 450:
            frags.append(arrow(col2_x + col_w / 2, sy + bh + 2, col2_x + col_w / 2, sy + bh + 18, color="#ea580c"))
        sy += bh + 22

    render(os.path.join(OUT_DIR, "onedir-vs-onefile-lifecycle.svg"), w, h, *frags)


def fig_dependency_analysis_pipeline():
    """Фігура 3: Конвеєр статичного аналізу, хуків та збирання образу."""
    w, h = 920, 460
    frags = []

    frags.append(text(w / 2, 30, "Конвеєр виявлення залежностей і компонування замороженого застосунку", size=16, bold=True))

    # 4 етапи горизонтального конвеєра
    stages = [
        ("1. Статичний аналіз коду", 40, 60, 190, 360, "#eff6ff", "#3b82f6", [
            ("Вхідний скрипт", 40, "Головний файл entrypoint.py"),
            ("Розбір AST", 50, "Побудова графа імпортів через modulegraph (import, from...)"),
            ("Виявлені модулі", 45, "Стандартна бібліотека та явні пакети проєкту")
        ]),
        ("2. Система хуків (Hooks)", 260, 60, 190, 360, "#fdf4ff", "#c084fc", [
            ("Динамічний імпорт", 45, "importlib.import_module не видно в AST"),
            ("Сценарії hook-*.py", 55, "hiddenimports, collect_submodules, collect_data_files"),
            ("Повний граф", 40, "Доповнений список модулів і плагінів")
        ]),
        ("3. Збір бінарників і даних", 480, 60, 190, 360, "#f0fdf4", "#22c55e", [
            ("ldd / dumpbin", 50, "Трасування динамічних спільних бібліотек (.so / .dll)"),
            ("C-розширення", 45, "Пошук скомпільованих модулів .pyd / .so"),
            ("Ресурси --add-data", 45, "Копіювання конфігурацій, сертифікатів та картинок")
        ]),
        ("4. Пакування та компонування", 700, 60, 190, 360, "#fff7ed", "#f97316", [
            ("Генерація PYZ", 45, "Компіляція в .pyc та стиснення zlib"),
            ("Зшивання Bootloader", 50, "Об'єднання бінарного завантажувача, PYZ, DLL та TOC"),
            ("Готовий виконуваний файл", 45, "Автономний артефакт (ELF або PE .exe)")
        ])
    ]

    for title, sx, sy, sw, sh, bg_c, stroke_c, inner_boxes in stages:
        # Зовнішня картка етапу
        frags.append(rect(sx, sy, sw, sh, fill=bg_c, stroke=stroke_c, sw=1.5, rx=8))
        frags.append(text(sx + sw / 2, sy + 25, title, size=13, bold=True, color=stroke_c))

        # Внутрішні блоки дій
        iny = sy + 45
        for in_title, in_h, in_desc in inner_boxes:
            frags.append(fitbox(sx + 10, iny, sw - 20, in_h, f"{in_title}\n{in_desc}", size=11, fill="#ffffff", stroke="#cbd5e1"))
            iny += in_h + 16

        # Стрілка до наступного етапу
        if sx + sw < 700:
            frags.append(arrow(sx + sw + 3, sy + sh / 2, sx + sw + 17, sy + sh / 2, color="#64748b", sw=2))

    render(os.path.join(OUT_DIR, "dependency-analysis-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_frozen_executable_anatomy()
    fig_onedir_vs_onefile_lifecycle()
    fig_dependency_analysis_pipeline()
    print("Всі фігури успішно згенеровано.")
