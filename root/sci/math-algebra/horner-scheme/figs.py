# -*- coding: utf-8 -*-
"""Фігури для статті «Схема Горнера».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
GREEN_FILL  = "#eafaf1"
BLUE_FILL   = "#eaf0fd"
ORANGE_FILL = "#fdf1e5"
PURPLE_FILL = "#f3e8ff"
GRAY_FILL   = "#f4f6f8"

# ─────────────────────────────────────────────────────────────────────────
# Фігура 1 — Схема потоку коефіцієнтів у таблиці Горнера
# ─────────────────────────────────────────────────────────────────────────
def fig_horner_table_flow():
    W, H = 840, 360
    p = []

    p.append(text(W/2, 26, "Структура та потік обчислень у таблиці Горнера", size=16, bold=True))
    p.append(text(W/2, 46, "Кожен коефіцієнт частки bₖ = aₖ + x₀ · bₖ₊₁ обчислюється послідовно зліва направо", size=12, color=MUTED, italic=True))

    cols_x = [230, 370, 510, 650, 770]
    col_labels = ["aₙ", "aₙ₋₁", "aₙ₋₂", "...", "a₀"]
    b_labels = ["bₙ = aₙ", "bₙ₋₁", "bₙ₋₂", "...", "b₀ = P(x₀)"]
    mult_labels = ["—", "x₀·bₙ", "x₀·bₙ₋₁", "...", "x₀·b₁"]

    y_row1 = 150
    y_row2 = 230

    p.append(rect(40, y_row2 - 20, 110, 40, fill=ORANGE_FILL, stroke=POS, sw=1.8, rx=6))
    p.append(text(95, y_row2 + 4, "x = x₀", size=14, bold=True, color=POS))

    p.append(text(95, y_row1 + 4, "Коефіцієнти P(x)", size=11, color=MUTED, bold=True))
    p.append(text(95, y_row2 + 32, "(точка оцінки)", size=10, color=MUTED))

    p.append(line(30, y_row1 + 30, 810, y_row1 + 30, color=INK, sw=1.5))

    for idx in range(5):
        cx = cols_x[idx]
        
        p.append(rect(cx - 45, y_row1 - 18, 90, 36, fill=GRAY_FILL, stroke=LINE, sw=1.2, rx=4))
        p.append(text(cx, y_row1 + 5, col_labels[idx], size=13, bold=True))

        if idx > 0 and idx != 3:
            p.append(text(cx, y_row1 + 50, mult_labels[idx], size=11, italic=True, color=NEG))

        is_remainder = (idx == 4)
        f_clr = GREEN_FILL if is_remainder else (BLUE_FILL if idx < 3 else GRAY_FILL)
        s_clr = FIELD if is_remainder else (NEG if idx < 3 else LINE)
        
        p.append(rect(cx - 50, y_row2 - 18, 100, 36, fill=f_clr, stroke=s_clr, sw=1.8 if is_remainder else 1.2, rx=6))
        p.append(text(cx, y_row2 + 5, b_labels[idx], size=12, bold=True, color=FIELD if is_remainder else INK))

    p.append(line(cols_x[0] + 50, y_row2, cols_x[1] - 40, y_row1 + 50, color=POS, sw=1.8))
    p.append(text((cols_x[0] + cols_x[1])/2 - 10, y_row2 - 15, "× x₀", size=11, bold=True, color=POS))

    p.append(line(cols_x[1], y_row1 + 18, cols_x[1], y_row2 - 18, color=NEG, sw=1.8))
    p.append(text(cols_x[1] + 22, y_row1 + 38, "+", size=14, bold=True, color=NEG))

    p.append(line(cols_x[1] + 50, y_row2, cols_x[2] - 40, y_row1 + 50, color=POS, sw=1.5))
    p.append(line(cols_x[2], y_row1 + 18, cols_x[2], y_row2 - 18, color=NEG, sw=1.5))

    y_leg = 305
    p.append(rect(180, y_leg, 480, 40, fill=PURPLE_FILL, stroke=INK, sw=1.0, rx=6))
    p.append(text(420, y_leg + 24, "Рекурентна формула: bₙ = aₙ,   bₖ = aₖ + x₀ · bₖ₊₁   (для k = n-1, ..., 0)", size=12, bold=True))

    render(os.path.join(IMG, "horner-table-flow.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — Порівняння обчислювального дерева (Наївний метод vs Горнер)
# ─────────────────────────────────────────────────────────────────────────
def fig_nesting_tree():
    W, H = 840, 410
    p = []

    p.append(text(W/2, 26, "Порівняння обчислювальної складності підходів", size=16, bold=True))
    p.append(text(W/2, 46, "Наївний розрахунок виконує O(n²) операцій, схема Горнера скорочує складність до O(n)", size=12, color=MUTED, italic=True))

    # Ліва панель — Наївний метод
    lx = 40
    lw = 360
    ly = 80
    lh = 300
    p.append(rect(lx, ly, lw, lh, fill=GRAY_FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(lx + lw/2, ly + 25, "Наївний підхід: a₃x³ + a₂x² + a₁x + a₀", size=13, bold=True, color=NEG))

    ops_naive = [
        ("x³ = x · x · x", "3 множення", ORANGE_FILL),
        ("x² = x · x", "2 множення", ORANGE_FILL),
        ("a₃·x³, a₂·x², a₁·x", "3 множення", ORANGE_FILL),
        ("Сума 4 доданків", "3 додавання", BLUE_FILL)
    ]
    for idx, (expr, cost, f_clr) in enumerate(ops_naive):
        oy = ly + 52 + idx * 44
        p.append(rect(lx + 20, oy, 190, 32, fill=f_clr, stroke=LINE, sw=1.0, rx=4))
        p.append(text(lx + 115, oy + 20, expr, size=11, bold=True))
        p.append(text(lx + 280, oy + 20, cost, size=11, color=NEG, bold=True))

    p.append(rect(lx + 20, ly + 245, 320, 36, fill=ORANGE_FILL, stroke=NEG, sw=1.5, rx=6))
    p.append(text(lx + 170, ly + 267, "Разом: 8 операцій (n(n+1)/2 mult + n add)", size=11, bold=True, color=NEG))

    # Права панель — Схема Горнера
    rx = 440
    rw = 360
    p.append(rect(rx, ly, rw, lh, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx + rw/2, ly + 25, "Схема Горнера: ((a₃·x + a₂)·x + a₁)·x + a₀", size=13, bold=True, color=FIELD))

    ops_horner = [
        ("Крок 1: v₁ = a₃·x + a₂", "1 mult + 1 add", BLUE_FILL),
        ("Крок 2: v₂ = v₁·x + a₁", "1 mult + 1 add", BLUE_FILL),
        ("Крок 3: P(x) = v₂·x + a₀", "1 mult + 1 add", BLUE_FILL),
    ]
    for idx, (expr, cost, f_clr) in enumerate(ops_horner):
        oy = ly + 60 + idx * 52
        p.append(rect(rx + 20, oy, 210, 36, fill=f_clr, stroke=FIELD, sw=1.0, rx=4))
        p.append(text(rx + 125, oy + 22, expr, size=11, bold=True))
        p.append(text(rx + 285, oy + 22, cost, size=11, color=FIELD, bold=True))

    p.append(rect(rx + 20, ly + 245, 320, 36, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(rx + 170, ly + 267, "Разом: 6 операцій (n mult + n add)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "nesting-tree.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — Трикутна схема повторного застосування алгоритму Горнера
# ─────────────────────────────────────────────────────────────────────────
def fig_taylor_triangular_horner():
    W, H = 840, 380
    p = []

    p.append(text(W/2, 26, "Повторна схема Горнера для коефіцієнтів Тейлора", size=16, bold=True))
    p.append(text(W/2, 46, "Послідовні остачі вкорочених таблиць дають значення P⁽ᵏ⁾(x₀) / k!", size=12, color=MUTED, italic=True))

    y_start = 85
    row_gap = 65

    pass_data = [
        ("Прохід 1 (Оригінал)", ["a₃", "a₂", "a₁", "a₀"], "P(x₀)", GREEN_FILL, FIELD),
        ("Прохід 2 (Частка Q₁)", ["b₃", "b₂", "b₁"], "P'(x₀)", BLUE_FILL, NEG),
        ("Прохід 3 (Частка Q₂)", ["c₃", "c₂"], "P''(x₀)/2!", PURPLE_FILL, INK),
        ("Прохід 4 (Частка Q₃)", ["d₃"], "P'''(x₀)/3!", ORANGE_FILL, POS)
    ]

    x_base = 180
    col_w = 90

    for p_idx, (p_title, coeffs, rem_label, f_clr, s_clr) in enumerate(pass_data):
        py = y_start + p_idx * row_gap
        
        p.append(text(100, py + 5, p_title, size=11, bold=True, anchor="end"))
        
        for c_idx, c_val in enumerate(coeffs):
            cx = x_base + c_idx * col_w
            p.append(rect(cx - 32, py - 16, 64, 32, fill=GRAY_FILL, stroke=LINE, sw=1.0, rx=4))
            p.append(text(cx, py + 4, c_val, size=11, bold=True))

        rx = x_base + len(coeffs) * col_w
        p.append(rect(rx - 40, py - 18, 80, 36, fill=f_clr, stroke=s_clr, sw=1.8, rx=6))
        p.append(text(rx, py + 5, rem_label, size=11, bold=True, color=s_clr))

    p.append(line(575, 95, 305, 290, color=POS, sw=1.5, dash="4 4"))
    p.append(text(460, 205, "Послідовність коефіцієнтів Тейлора", size=11, bold=True, color=POS))

    render(os.path.join(IMG, "taylor-triangular-horner.svg"), W, H, *p)


if __name__ == "__main__":
    fig_horner_table_flow()
    fig_nesting_tree()
    fig_taylor_triangular_horner()
    print("Успішно згенеровано 3 фігури у ./img/")
