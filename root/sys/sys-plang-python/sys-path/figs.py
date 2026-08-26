# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми 'sys.path і звідки він береться'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_resolution_pipeline():
    """Шість етапів формування списку sys.path під час ініціалізації CPython."""
    w, h = 980, 640
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Шість етапів формування sys.path під час старту CPython", size=16, bold=True))

    stages = [
        ("1. Точка входу (sys.path[0])", [
            "python script.py  →  каталог скрипту",
            "python -m mod    →  поточний каталог (cwd)",
            "REPL / stdin     →  порожній рядок (\"\")",
            "python -P        →  вилучення небезпечного [0]"
        ], "#eaf0fd", NEG),

        ("2. Змінна PYTHONPATH", [
            "Зчитування з середовища процесу",
            "Розбиття за os.pathsep (: або ;)",
            "Вставка одразу після sys.path[0]",
            "Ігнорування при -E або в режимі -I"
        ], "#eaf0fd", NEG),

        ("3. Стандартна бібліотека (Landmarks)", [
            "Пошук префікса: pyvenv.cfg або landmark",
            "Додавання pythonXY.zip (якщо є)",
            "Додавання каталогу stdlib (prefix/lib/pythonX.Y)",
            "Додавання lib-dynload (C-розширення)"
        ], "#fdecea", POS),

        ("4. Модуль site.py (site-packages)", [
            "Автоматичний запуск site.main() (якщо не -S)",
            "Визначення системного prefix/lib/site-packages",
            "Виклик site.addsitedir() для кожного шляху",
            "Створення об'єктів шляхів у пам'яті"
        ], "#fef9e7", "#b78103"),

        ("5. Обробка файлів .pth", [
            "Алфавітне сканування файлів *.pth",
            "Прості рядки  →  додавання шляхів у sys.path",
            "Рядки 'import ...'  →  виконання коду",
            "Рекурсивний обхід вкладених каталогів"
        ], "#fef9e7", "#b78103"),

        ("6. Користувацькі пакунки (User Site)", [
            "Додавання ~/.local/lib/pythonX.Y/site-packages",
            "Вимкнення через PYTHONNOUSERSITE або -s",
            "Виконання хуків sitecustomize та usercustomize",
            "Формування фінального списку sys.path"
        ], "#e8f8f0", FIELD),
    ]

    card_w = 280
    card_h = 200
    x_gap = 40
    start_x = 35
    row1_y = 65
    row2_y = 370

    for i in range(3):
        title, bullets, fill_color, stroke_color = stages[i]
        cx = start_x + i * (card_w + x_gap)
        cy = row1_y

        frags.append(rect(cx, cy, card_w, card_h, fill=fill_color, stroke=stroke_color, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, title, size=12, bold=True, color=stroke_color))
        frags.append(line(cx + 10, cy + 36, cx + card_w - 10, cy + 36, color=stroke_color, sw=1.0))

        for b_idx, bullet in enumerate(bullets):
            frags.append(text(cx + 14, cy + 62 + b_idx * 30, "• " + bullet, size=10, anchor="start", color=INK))

        if i < 2:
            ax1 = cx + card_w + 4
            ay1 = cy + card_h / 2
            ax2 = cx + card_w + x_gap - 4
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.8))

    # З'єднувальна лінія між рядами (від картки 3 до картки 4)
    c3_right_x = start_x + 2 * (card_w + x_gap) + card_w / 2
    frags.append(line(c3_right_x, row1_y + card_h, c3_right_x, row1_y + card_h + 46, color=LINE, sw=1.5, dash="4,4"))
    frags.append(line(c3_right_x, row1_y + card_h + 46, start_x + card_w / 2, row1_y + card_h + 46, color=LINE, sw=1.5, dash="4,4"))
    frags.append(arrow(start_x + card_w / 2, row1_y + card_h + 46, start_x + card_w / 2, row2_y - 2, color=LINE, sw=1.8))

    for i in range(3):
        idx = 3 + i
        title, bullets, fill_color, stroke_color = stages[idx]
        cx = start_x + i * (card_w + x_gap)
        cy = row2_y

        frags.append(rect(cx, cy, card_w, card_h, fill=fill_color, stroke=stroke_color, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, title, size=12, bold=True, color=stroke_color))
        frags.append(line(cx + 10, cy + 36, cx + card_w - 10, cy + 36, color=stroke_color, sw=1.0))

        for b_idx, bullet in enumerate(bullets):
            frags.append(text(cx + 14, cy + 62 + b_idx * 30, "• " + bullet, size=10, anchor="start", color=INK))

        if i < 2:
            ax1 = cx + card_w + 4
            ay1 = cy + card_h / 2
            ax2 = cx + card_w + x_gap - 4
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.8))

    out_path = os.path.join(OUT_DIR, "sys-path-resolution-pipeline.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_script_vs_module_mode():
    """Порівняння поведінки sys.path[0] та простору імен при python script.py проти python -m module."""
    w, h = 960, 480
    frags = []

    frags.append(text(w / 2, 28, "Порівняння поведінки: python path/to/script.py проти python -m pkg.script", size=16, bold=True))

    col_w = 430
    col_h = 390
    y_start = 60

    # Ліва колонка: python app/main.py
    lx = 35
    frags.append(rect(lx, y_start, col_w, col_h, fill="#f4f6f8", stroke="#2457d6", sw=1.8, rx=8))
    frags.append(text(lx + col_w / 2, y_start + 26, "Режим скрипту: python /proj/app/main.py", size=13, bold=True, color="#2457d6"))
    frags.append(line(lx + 12, y_start + 38, lx + col_w - 12, y_start + 38, color="#2457d6", sw=1.0))

    left_rows = [
        ("Робочий каталог (cwd):", "/home/user/project"),
        ("sys.path[0]:", "/home/user/project/app (каталог файлу)"),
        ("__file__:", "'/home/user/project/app/main.py'"),
        ("__name__:", "'__main__'"),
        ("__package__:", "'' або None (немає контексту пакета)"),
        ("Відносний імпорт (from . import utils):", "❌ ValueError: attempted relative import"),
        ("Абсолютний імпорт (import app.utils):", "❌ ModuleNotFoundError: No module named 'app'"),
        ("Локальний імпорт (import utils):", "✓ Успішно (знаходить /proj/app/utils.py)"),
    ]

    for i, (label, val) in enumerate(left_rows):
        ry = y_start + 64 + i * 39
        frags.append(text(lx + 16, ry, label, size=11, bold=True, anchor="start", color=INK))
        val_color = POS if "❌" in val else (FIELD if "✓" in val else MUTED)
        frags.append(text(lx + 16, ry + 18, val, size=10, anchor="start", color=val_color))

    # Права колонка: python -m app.main
    rx_col = 495
    frags.append(rect(rx_col, y_start, col_w, col_h, fill="#f4f6f8", stroke="#27ae60", sw=1.8, rx=8))
    frags.append(text(rx_col + col_w / 2, y_start + 26, "Режим модуля: python -m app.main", size=13, bold=True, color="#27ae60"))
    frags.append(line(rx_col + 12, y_start + 38, rx_col + col_w - 12, y_start + 38, color="#27ae60", sw=1.0))

    right_rows = [
        ("Робочий каталог (cwd):", "/home/user/project"),
        ("sys.path[0]:", "/home/user/project (поточний каталог cwd)"),
        ("__file__:", "'/home/user/project/app/main.py'"),
        ("__name__:", "'__main__'"),
        ("__package__:", "'app' (повноцінний контекст пакета)"),
        ("Відносний імпорт (from . import utils):", "✓ Успішно (розпізнає пакет 'app')"),
        ("Абсолютний імпорт (import app.utils):", "✓ Успішно (знаходить app через sys.path[0])"),
        ("Локальний імпорт (import utils):", "⚠️ Шукає в cwd, а не в /proj/app/"),
    ]

    for i, (label, val) in enumerate(right_rows):
        ry = y_start + 64 + i * 39
        frags.append(text(rx_col + 16, ry, label, size=11, bold=True, anchor="start", color=INK))
        val_color = POS if "❌" in val else (FIELD if "✓" in val else (POS if "⚠️" in val else MUTED))
        frags.append(text(rx_col + 16, ry + 18, val, size=10, anchor="start", color=val_color))

    out_path = os.path.join(OUT_DIR, "script-vs-module-mode.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_module_shadowing_conflict():
    """Схема виникнення колізії імен (Module Shadowing) між локальним файлом і стандартною бібліотекою."""
    w, h = 960, 520
    frags = []

    frags.append(text(w / 2, 28, "Механізм затінення модулів (Module Shadowing) через пріоритет sys.path[0]", size=16, bold=True))

    # Лівий блок: Робочий каталог проєкту
    b1_x, b1_y, b1_w, b1_h = 40, 70, 260, 410
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fff2f0", stroke=POS, sw=1.8, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 24, "1. Каталог скрипту / cwd", size=12, bold=True, color=POS))
    frags.append(text(b1_x + b1_w / 2, b1_y + 42, "sys.path[0] = /project/workspace", size=10, color=MUTED))
    frags.append(line(b1_x + 10, b1_y + 54, b1_x + b1_w - 10, b1_y + 54, color=POS, sw=1.0))

    files_b1 = [
        ("main.py", "точка входу застосунку"),
        ("math.py", "⚠️ НЕБЕЗПЕЧНИЙ ЛОКАЛЬНИЙ ФАЙЛ"),
        ("random.py", "⚠️ ЗАТІНЯЄ STDLIB random"),
        ("test.py", "⚠️ ЗАТІНЯЄ STDLIB test"),
        ("utils.py", "користувацький модуль")
    ]
    for i, (fn, desc) in enumerate(files_b1):
        fy = b1_y + 75 + i * 65
        is_bad = "⚠️" in desc
        f_fill = "#ffdcd6" if is_bad else "#f4f6f8"
        f_stroke = POS if is_bad else LINE
        frags.append(rect(b1_x + 12, fy, b1_w - 24, 52, fill=f_fill, stroke=f_stroke, sw=1.2, rx=5))
        frags.append(text(b1_x + 22, fy + 20, fn, size=11, bold=True, anchor="start", color=POS if is_bad else INK))
        frags.append(text(b1_x + 22, fy + 38, desc, size=9, anchor="start", color=POS if is_bad else MUTED))

    # Центральний блок: Порядок пошуку PathFinder
    b2_x, b2_y, b2_w, b2_h = 350, 70, 260, 410
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f4f6f8", stroke="#2457d6", sw=1.8, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 24, "2. Ітерація по sys.path", size=12, bold=True, color="#2457d6"))
    frags.append(text(b2_x + b2_w / 2, b2_y + 42, "PathFinder шукає math.py", size=10, color=MUTED))
    frags.append(line(b2_x + 10, b2_y + 54, b2_x + b2_w - 10, b2_y + 54, color="#2457d6", sw=1.0))

    steps_b2 = [
        ("[0] /project/workspace", "Перший у списку! Знайдено math.py", POS),
        ("[1] PYTHONPATH entries", "Пропускається, бо знайдено на кроці [0]", MUTED),
        ("[2] /usr/lib/python3.12", "Каталог стандартної бібліотеки", MUTED),
        ("[3] .../lib-dynload", "math.cpython-312-x86_64-linux.so", MUTED),
        ("[4] .../site-packages", "Сторонні встановлені бібліотеки", MUTED)
    ]
    for i, (p_title, p_desc, p_col) in enumerate(steps_b2):
        py_box = b2_y + 75 + i * 65
        frags.append(rect(b2_x + 12, py_box, b2_w - 24, 52, fill="#ffffff", stroke=p_col, sw=1.2, rx=5))
        frags.append(text(b2_x + 22, py_box + 20, p_title, size=10, bold=True, anchor="start", color=p_col))
        frags.append(text(b2_x + 22, py_box + 38, p_desc, size=9, anchor="start", color=p_col))

    # Правий блок: Фатальний наслідок
    b3_x, b3_y, b3_w, b3_h = 660, 70, 260, 410
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#fff2f0", stroke=POS, sw=1.8, rx=8))
    frags.append(text(b3_x + b3_w / 2, b3_y + 24, "3. Наслідок виконання", size=12, bold=True, color=POS))
    frags.append(text(b3_x + b3_w / 2, b3_y + 42, "Помилки імпорту та аварія", size=10, color=MUTED))
    frags.append(line(b3_x + 10, b3_y + 54, b3_x + b3_w - 10, b3_y + 54, color=POS, sw=1.0))

    consequences = [
        ("Завантаження фейкового math", "Замість C-модуля завантажено локальний math.py"),
        ("Збій внутрішніх модулів", "random або datetime викликають import math і падають"),
        ("AttributeError: module 'math'...", "has no attribute 'sqrt' або 'sin'"),
        ("Крихітний захист: python -P", "Вилучає [0] та блокує локальне затінення"),
        ("Правильне рішення:", "Унікальні назви файлів + src/ layout")
    ]
    for i, (c_title, c_desc) in enumerate(consequences):
        cy_box = b3_y + 75 + i * 65
        is_fix = i >= 3
        c_fill = "#e8f8f0" if is_fix else "#ffdcd6"
        c_stroke = FIELD if is_fix else POS
        frags.append(rect(b3_x + 12, cy_box, b3_w - 24, 52, fill=c_fill, stroke=c_stroke, sw=1.2, rx=5))
        frags.append(text(b3_x + 22, cy_box + 20, c_title, size=10, bold=True, anchor="start", color=FIELD if is_fix else POS))
        frags.append(text(b3_x + 22, cy_box + 38, c_desc, size=9, anchor="start", color=INK))

    # Стрілки між блоками
    frags.append(arrow(b1_x + b1_w + 2, b1_y + 110, b2_x - 4, b2_y + 110, color=POS, sw=1.8))
    frags.append(arrow(b2_x + b2_w + 2, b2_y + 110, b3_x - 4, b3_y + 110, color=POS, sw=1.8))

    out_path = os.path.join(OUT_DIR, "module-shadowing-conflict.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_resolution_pipeline()
    fig_script_vs_module_mode()
    fig_module_shadowing_conflict()
