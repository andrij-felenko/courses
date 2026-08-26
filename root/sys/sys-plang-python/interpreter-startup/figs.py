# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Запуск інтерпретатора й час старту'."""

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


def fig_startup_pipeline():
    """Етапи ініціалізації CPython від execve() до першого байткод-опокоду."""
    w, h = 980, 560
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Шлях виконання CPython під час запуску (python3 script.py)", size=16, bold=True))

    stages = [
        ("1. Системний виклик і точка входу", [
            "execve(/usr/bin/python3, argv, envp)",
            "Завантаження ELF, лінкування libc/libpython",
            "Виклик main() у Programs/python.c",
            "Делегування до Py_BytesMain() / pymain_main()"
        ], "#eaf0fd", NEG),
        
        ("2. Перед-ініціалізація та PyConfig (PEP 587)", [
            "Py_PreInitialize(&PyPreConfig) -> пам'ять і UTF-8",
            "PyConfig_InitPythonConfig(&config)",
            "Зчитування змінних: PYTHONHOME, PYTHONPATH...",
            "Розрахунок шляхів: _PyPathConfig (landmark search)"
        ], "#eaf0fd", NEG),
        
        ("3. Ініціалізація ядра середовища", [
            "Py_InitializeFromConfig(&config)",
            "Створення PyInterpreterState та PyThreadState",
            "Реєстрація базових типів: object, type, str...",
            "Створення builtins та словника системних констант sys"
        ], "#fdecea", POS),
        
        ("4. Бутстрап імпорту (Frozen Modules)", [
            "Ініціалізація _PyImport_InitCore()",
            "Завантаження _frozen_importlib з бінарного C-масиву",
            "Усунення потреби в I/O на ранній стадії",
            "Монтування sys.meta_path (PathFinder, FileFinder)"
        ], "#e8f8f0", FIELD),
        
        ("5. Розгортання середовища: site.py", [
            "Виконання site.py (якщо не задано -S)",
            "Пошук та обхід шляхів site-packages",
            "Обробка .pth файлів і динамічне розширення шляхів",
            "Підключення user-site (~/.local/lib/pythonX.Y)"
        ], "#fef9e7", "#b78103"),
        
        ("6. Виконання цільового скрипту", [
            "Створення модуля __main__ та словника простору імен",
            "Компіляція скрипту або читання .pyc з __pycache__",
            "Створення кореневого PyFrameObject",
            "Виконання першого байткод-опокоду (RESUME / LOAD)"
        ], "#e8f8f0", FIELD),
    ]

    card_w = 280
    card_h = 180
    x_gap = 40
    start_x = 35
    row1_y = 65
    row2_y = 315

    # Ряд 1: індекси 0, 1, 2
    for i in range(3):
        title, bullets, fill_color, stroke_color = stages[i]
        cx = start_x + i * (card_w + x_gap)
        cy = row1_y
        
        frags.append(rect(cx, cy, card_w, card_h, fill=fill_color, stroke=stroke_color, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, title, size=12, bold=True, color=stroke_color))
        frags.append(line(cx + 10, cy + 34, cx + card_w - 10, cy + 34, color=stroke_color, sw=1.0))
        
        for b_idx, bullet in enumerate(bullets):
            frags.append(text(cx + 14, cy + 56 + b_idx * 28, "• " + bullet, size=10, anchor="start", color=INK))
            
        if i < 2:
            ax1 = cx + card_w + 4
            ay1 = cy + card_h / 2
            ax2 = cx + card_w + x_gap - 4
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.8))

    frags.append(line(start_x + 2 * (card_w + x_gap) + card_w / 2, row1_y + card_h, start_x + 2 * (card_w + x_gap) + card_w / 2, row1_y + card_h + 25, color=LINE, sw=1.5, dash="4,4"))
    frags.append(line(start_x + 2 * (card_w + x_gap) + card_w / 2, row1_y + card_h + 25, start_x + card_w / 2, row1_y + card_h + 25, color=LINE, sw=1.5, dash="4,4"))
    frags.append(arrow(start_x + card_w / 2, row1_y + card_h + 25, start_x + card_w / 2, row2_y - 2, color=LINE, sw=1.8))

    # Ряд 2: індекси 3, 4, 5
    for i in range(3):
        stage_idx = 3 + i
        title, bullets, fill_color, stroke_color = stages[stage_idx]
        cx = start_x + i * (card_w + x_gap)
        cy = row2_y
        
        frags.append(rect(cx, cy, card_w, card_h, fill=fill_color, stroke=stroke_color, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, title, size=12, bold=True, color=stroke_color))
        frags.append(line(cx + 10, cy + 34, cx + card_w - 10, cy + 34, color=stroke_color, sw=1.0))
        
        for b_idx, bullet in enumerate(bullets):
            frags.append(text(cx + 14, cy + 56 + b_idx * 28, "• " + bullet, size=10, anchor="start", color=INK))
            
        if i < 2:
            ax1 = cx + card_w + 4
            ay1 = cy + card_h / 2
            ax2 = cx + card_w + x_gap - 4
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.8))

    frags.append(text(w / 2, 535, "Головне вузьке місце латентності: дисковий I/O та сканування .pth файлів у site.py (фази 4-5)", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "startup-pipeline.svg")
    render(path, w, h, *frags)


def fig_latency_breakdown():
    """Діаграма розподілу часу запуску CPython (Startup Latency Budget)."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 28, "Бюджет часу старту CPython: стандартний запуск проти оптимізованого", size=16, bold=True))

    col_w = 230
    x_gap = 50
    start_x = 55
    y_top = 70

    scenarios = [
        {
            "title": "Звичайний запуск (CLI)",
            "subtitle": "Повний імпорт: 85.0 мс",
            "segments": [
                ("execve & libc init", 2.0, "#dbeafe", NEG),
                ("PyConfig & Core C Init", 3.0, "#d1fae5", FIELD),
                ("site.py & .pth сканування", 22.0, "#fef3c7", "#b45309"),
                ("Імпорт стандартних ліб", 18.0, "#fed7aa", "#c2410c"),
                ("Імпорт важких залежностей", 40.0, "#fee2e2", POS),
            ],
            "total_ms": 85.0
        },
        {
            "title": "Запуск із прапорцем -S",
            "subtitle": "Без site.py: 27.0 мс",
            "segments": [
                ("execve & libc init", 2.0, "#dbeafe", NEG),
                ("PyConfig & Core C Init", 3.0, "#d1fae5", FIELD),
                ("Імпорт стандартних ліб", 10.0, "#fed7aa", "#c2410c"),
                ("Імпорт скрипту (direct)", 12.0, "#fee2e2", POS),
            ],
            "total_ms": 27.0
        },
        {
            "title": "Оптимізований (-S + Lazy Imports)",
            "subtitle": "Мінімальна латентність: 5.5 мс",
            "segments": [
                ("execve & libc init", 2.0, "#dbeafe", NEG),
                ("PyConfig & Deepfreeze", 2.5, "#d1fae5", FIELD),
                ("Lazy module stubs", 1.0, "#e0e7ff", "#4338ca"),
            ],
            "total_ms": 5.5
        }
    ]

    for c_idx, sc in enumerate(scenarios):
        cx = start_x + c_idx * (col_w + x_gap)
        
        frags.append(text(cx + col_w / 2, y_top + 16, sc["title"], size=13, bold=True, color=INK))
        frags.append(text(cx + col_w / 2, y_top + 34, sc["subtitle"], size=11, color=MUTED, bold=True))
        
        scale = 260.0 / 85.0
        cur_y = y_top + 55
        
        total_h = sc["total_ms"] * scale
        frags.append(rect(cx, cur_y, col_w, total_h, fill="#fafafa", stroke=LINE, sw=1.5, rx=6))
        
        seg_y = cur_y
        for seg_name, seg_val, seg_fill, seg_stroke in sc["segments"]:
            sh = seg_val * scale
            frags.append(rect(cx, seg_y, col_w, sh, fill=seg_fill, stroke=seg_stroke, sw=1.2, rx=4))
            
            if sh >= 28:
                frags.append(text(cx + col_w / 2, seg_y + sh / 2 - 4, seg_name, size=10, bold=True, color=INK))
                frags.append(text(cx + col_w / 2, seg_y + sh / 2 + 9, f"{seg_val:.1f} ms", size=9, color=MUTED))
            elif sh >= 16:
                frags.append(text(cx + col_w / 2, seg_y + sh / 2 + 3, f"{seg_name}: {seg_val:.1f} ms", size=9, bold=True, color=INK))
            else:
                frags.append(text(cx + col_w / 2, seg_y + sh / 2 + 3, f"{seg_val:.1f} ms", size=9, color=INK))
                
            seg_y += sh

    frags.append(text(w / 2, 455, "Виключення site.py (-S) та відкладення важких імпортів зменшують час старту у 15 разів", size=11, color=FIELD, bold=True))

    path = os.path.join(OUT_DIR, "latency-breakdown.svg")
    render(path, w, h, *frags)


def fig_frozen_vs_disk():
    """Порівняння імпорту з диска проти Frozen та Deep-Frozen модулів."""
    w, h = 960, 440
    frags = []

    frags.append(text(w / 2, 26, "Еволюція бутстрапу: імпорт з диска vs Frozen vs Deep-Frozen", size=16, bold=True))

    cards = [
        ("1. Звичайний імпорт з диска (.py / .pyc)", [
            "1. Пошук файлу через sys.path (десятки stat/open)",
            "2. Читання файлу в оперативну пам'ять (I/O)",
            "3. Перевірка хешу або дати у кеші __pycache__",
            "4. Компіляція .py або unmarshal файлу .pyc",
            "5. Виділення пам'яті під PyCodeObject у heap",
            "Витрати: системні виклики I/O, фрагментація heap"
        ], "#fee2e2", POS),
        
        ("2. Класичні Frozen Modules (Python 3.8-3.10)", [
            "1. Модуль скомпільовано в C-масив на етапі збирання",
            "2. Відсутність системних викликів до файлової системи",
            "3. Виклик PyMarshal_ReadObjectFromString() під час старту",
            "4. Десеріалізація створює об'єкти коду в heap",
            "5. Реєстрація модулів у словнику sys.modules",
            "Витрати: нульовий I/O, але залишається навантаження CPU"
        ], "#fef3c7", "#b45309"),
        
        ("3. Deep-Frozen Modules (Python 3.11+ Faster CPython)", [
            "1. PyCodeObject та рядки згенеровані як const C-структури",
            "2. Усі дані розміщені в .rodata сегменті бінарного файлу",
            "3. Повна відсутність десеріалізації (zero unmarshal)",
            "4. Нульові алокації в купі під час ініціалізації ядра",
            "5. Пряме виконання інструкцій із статичної пам'яті C",
            "Витрати: нульовий I/O, нульове навантаження десеріалізації"
        ], "#d1fae5", FIELD)
    ]

    card_w = 280
    card_h = 330
    x_gap = 35
    start_x = 35
    card_y = 55

    for i, (title, bullets, fill_c, stroke_c) in enumerate(cards):
        cx = start_x + i * (card_w + x_gap)
        cy = card_y
        
        frags.append(rect(cx, cy, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, title, size=11, bold=True, color=stroke_c))
        frags.append(line(cx + 10, cy + 36, cx + card_w - 10, cy + 36, color=stroke_c, sw=1.0))
        
        for b_idx, bullet in enumerate(bullets):
            is_last = (b_idx == len(bullets) - 1)
            b_color = stroke_c if is_last else INK
            b_bold = is_last
            frags.append(text(cx + 12, cy + 60 + b_idx * 44, bullet[:44], size=9, anchor="start", color=b_color, bold=b_bold))
            if len(bullet) > 44:
                frags.append(text(cx + 22, cy + 74 + b_idx * 44, bullet[44:], size=9, anchor="start", color=b_color, bold=b_bold))

    frags.append(text(w / 2, 415, "Deep-Frozen перетворює код ядра на статичні константи C, заощаджуючи час CPU та пам'ять", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "frozen-vs-disk-import.svg")
    render(path, w, h, *frags)


if __name__ == "__main__":
    fig_startup_pipeline()
    fig_latency_breakdown()
    fig_frozen_vs_disk()
    print("All figures generated successfully.")
