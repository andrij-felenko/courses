#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Задача про покриття множини» (set-cover)."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_universe_subsets():
    """Фігура 1: Універсум елементів та вибір підмножин (Оптимальне покриття vs Субоптимальне)."""
    w, h = 820, 360
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Універсум елементів U = {e₁, e₂, ..., e₁₀} та сімейство підмножин S", size=15, bold=True, color=INK))

    # Універсум U: 10 комірок
    u_y = 65
    cell_w, cell_h = 64, 34
    start_x = (w - (10 * cell_w + 9 * 8)) / 2

    frags.append(rect(start_x - 12, u_y - 18, 10 * cell_w + 9 * 8 + 24, cell_h + 30, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(start_x - 5, u_y + 4, "U:", size=13, bold=True, color=INK, anchor="end"))

    for i in range(10):
        cx = start_x + i * (cell_w + 8) + cell_w / 2
        cy = u_y + cell_h / 2
        frags.append(rect(cx - cell_w / 2, cy - cell_h / 2, cell_w, cell_h, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=4))
        frags.append(text(cx, cy + 4, f"e{i+1}", size=12, bold=True, color=INK))

    # Дві колонки: Ліворуч - Оптимальне покриття (3 підмножини), Праворуч - Субоптимальне
    col_w = 370
    col1_x = 30
    col2_x = 420
    cards_y = 135

    # Колонка 1: Оптимальне покриття
    frags.append(rect(col1_x, cards_y, col_w, 205, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(col1_x + col_w / 2, cards_y + 24, "Оптимальне покриття (OPT): C* = {S₁, S₄, S₅}", size=13, bold=True, color=FIELD))
    frags.append(text(col1_x + col_w / 2, cards_y + 44, "Сумарна вартість: 4 + 3 + 4 = 11 (Покрито 10 з 10)", size=11, bold=False, color=INK))

    subsets_opt = [
        ("S₁", "Вартість w₁ = 4", "{e₁, e₂, e₃, e₄, e₅}", "#dcfce7", "#16a34a"),
        ("S₄", "Вартість w₄ = 3", "{e₄, e₆, e₇, e₈}", "#dcfce7", "#16a34a"),
        ("S₅", "Вартість w₅ = 4", "{e₂, e₅, e₉, e₁₀}", "#dcfce7", "#16a34a"),
    ]

    for idx, (name, cost, elems, bg_col, brd_col) in enumerate(subsets_opt):
        sy = cards_y + 60 + idx * 45
        frags.append(rect(col1_x + 15, sy, col_w - 30, 38, fill=bg_col, stroke=brd_col, sw=1.2, rx=4))
        frags.append(text(col1_x + 30, sy + 23, name, size=13, bold=True, color=brd_col, anchor="start"))
        frags.append(text(col1_x + 65, sy + 23, cost, size=11, bold=False, color=MUTED, anchor="start"))
        frags.append(text(col1_x + col_w - 25, sy + 23, elems, size=11, bold=True, color=INK, anchor="end"))

    # Колонка 2: Субоптимальне / Неефективне покриття
    frags.append(rect(col2_x, cards_y, col_w, 205, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(col2_x + col_w / 2, cards_y + 24, "Субоптимальне покриття: C' = {S₂, S₃, S₆}", size=13, bold=True, color=POS))
    frags.append(text(col2_x + col_w / 2, cards_y + 44, "Сумарна вартість: 5 + 6 + 4 = 15 (Лише 9 елементів)", size=11, bold=False, color=INK))

    subsets_sub = [
        ("S₂", "Вартість w₂ = 5", "{e₁, e₃, e₆}", "#fee2e2", "#dc2626"),
        ("S₃", "Вартість w₃ = 6", "{e₂, e₄, e₇, e₈}", "#fee2e2", "#dc2626"),
        ("S₆", "Вартість w₆ = 4", "{e₅, e₉}", "#fee2e2", "#dc2626"),
    ]

    for idx, (name, cost, elems, bg_col, brd_col) in enumerate(subsets_sub):
        sy = cards_y + 60 + idx * 45
        frags.append(rect(col2_x + 15, sy, col_w - 30, 38, fill=bg_col, stroke=brd_col, sw=1.2, rx=4))
        frags.append(text(col2_x + 30, sy + 23, name, size=13, bold=True, color=brd_col, anchor="start"))
        frags.append(text(col2_x + 65, sy + 23, cost, size=11, bold=False, color=MUTED, anchor="start"))
        frags.append(text(col2_x + col_w - 25, sy + 23, elems, size=11, bold=True, color=INK, anchor="end"))

    render(os.path.join(OUT_DIR, "set-cover-universe-subsets.svg"), w, h, *frags)


def fig_greedy_choice_steps():
    """Фігура 2: Покроковий вибір жадібного алгоритму та динамічна питома вартість."""
    w, h = 820, 370
    frags = []

    frags.append(text(w / 2, 28, "Покрокова робота жадібного алгоритму: мінімізація питомої вартості", size=15, bold=True, color=INK))

    step_w = 240
    step_h = 300
    y_top = 50

    steps_data = [
        {
            "num": "Крок 1",
            "title": "Вибір найефективнішої S₁",
            "eval": [
                ("S₁: w=4, нових=5 → 4/5 = 0.80", True),
                ("S₂: w=5, нових=3 → 5/3 = 1.67", False),
                ("S₃: w=6, нових=4 → 6/4 = 1.50", False),
                ("S₄: w=3, нових=4 → 3/4 = 0.75", False),
            ],
            "action": "Обрано S₁ (покрито 5 ел.)",
            "covered": "Покрито: {e₁, e₂, e₃, e₄, e₅}",
            "rem": "Залишилось: 5 елементів",
            "bg": "#eff6ff",
            "stroke": NEG,
        },
        {
            "num": "Крок 2",
            "title": "Перерахунок для решти U",
            "eval": [
                ("S₄: w=3, нових=3 → 3/3 = 1.00", True),
                ("S₂: w=5, нових=1 → 5/1 = 5.00", False),
                ("S₃: w=6, нових=2 → 6/2 = 3.00", False),
                ("S₅: w=4, нових=2 → 4/2 = 2.00", False),
            ],
            "action": "Обрано S₄ (нові: e₆, e₇, e₈)",
            "covered": "Покрито: {e₁,..,e₅} ∪ {e₆,e₇,e₈}",
            "rem": "Залишилось: {e₉, e₁₀}",
            "bg": "#f0fdf4",
            "stroke": FIELD,
        },
        {
            "num": "Крок 3",
            "title": "Фінальне закриття залишку",
            "eval": [
                ("S₅: w=4, нових=2 → 4/2 = 2.00", True),
                ("S₆: w=5, нових=1 → 5/1 = 5.00", False),
                ("S₇: w=6, нових=1 → 6/1 = 6.00", False),
                ("— решта не мають нових —", False),
            ],
            "action": "Обрано S₅ (нові: e₉, e₁₀)",
            "covered": "Покрито: ВСІ 10 елементів",
            "rem": "Покриття множини ЗАВЕРШЕНО",
            "bg": "#fefce8",
            "stroke": "#ca8a04",
        }
    ]

    for i, st in enumerate(steps_data):
        x = 25 + i * (step_w + 35)
        frags.append(rect(x, y_top, step_w, step_h, fill=st["bg"], stroke=st["stroke"], sw=1.5, rx=6))

        # Заголовок кроку
        frags.append(text(x + step_w / 2, y_top + 24, st["num"], size=14, bold=True, color=st["stroke"]))
        frags.append(text(x + step_w / 2, y_top + 44, st["title"], size=11, bold=True, color=INK))

        # Розділювач
        frags.append(line(x + 10, y_top + 54, x + step_w - 10, y_top + 54, color=st["stroke"], sw=1, dash="3,3"))

        # Оцінка варіантів
        frags.append(text(x + 12, y_top + 72, "Оцінка w(S) / |S \\ C|:", size=11, bold=True, color=MUTED, anchor="start"))
        for j, (ev_text, is_best) in enumerate(st["eval"]):
            ey = y_top + 94 + j * 24
            if is_best:
                frags.append(rect(x + 8, ey - 14, step_w - 16, 20, fill="#ffffff", stroke=st["stroke"], sw=1, rx=3))
                frags.append(text(x + 12, ey, "▶ " + ev_text, size=10, bold=True, color=st["stroke"], anchor="start"))
            else:
                frags.append(text(x + 14, ey, "  " + ev_text, size=10, bold=False, color=MUTED, anchor="start"))

        # Розділювач
        frags.append(line(x + 10, y_top + 195, x + step_w - 10, y_top + 195, color=st["stroke"], sw=1, dash="3,3"))

        # Дія та результат
        tb, _, _ = textbox(x + step_w / 2, y_top + 220, st["action"], size=11, bold=True, pad=6, fill="#ffffff", stroke=st["stroke"])
        frags.append(tb)
        frags.append(text(x + step_w / 2, y_top + 256, st["covered"], size=10, bold=False, color=INK))
        frags.append(text(x + step_w / 2, y_top + 278, st["rem"], size=10, bold=True, color=st["stroke"]))

        # Стрілка переходу до наступного кроку
        if i < 2:
            arr_x1 = x + step_w + 5
            arr_x2 = arr_x1 + 25
            arr_y = y_top + step_h / 2
            frags.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))

    render(os.path.join(OUT_DIR, "greedy-choice-steps.svg"), w, h, *frags)


def fig_tightness_construction():
    """Фігура 3: Конструкція найгіршого випадку (tightness) для жадібного алгоритму: фактор Ω(ln n)."""
    w, h = 820, 350
    frags = []

    frags.append(text(w / 2, 28, "Конструкція найгіршого випадку: чому жадібний алгоритм досягає бар'єра ln(n)", size=14, bold=True, color=INK))

    # Ліва панель: Оптимальний розв'язок (2 множини)
    opt_x = 30
    opt_w = 360
    panel_y = 52
    panel_h = 280

    frags.append(rect(opt_x, panel_y, opt_w, panel_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(opt_x + opt_w / 2, panel_y + 24, "Оптимальний розв'язок (OPT = 2)", size=13, bold=True, color=FIELD))
    frags.append(text(opt_x + opt_w / 2, panel_y + 44, "Дві множини покривають весь універсум за вартість 2", size=11, color=MUTED))

    # Дві горизонтальні смуги O_1 та O_2
    frags.append(rect(opt_x + 20, panel_y + 70, opt_w - 40, 85, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(opt_x + 35, panel_y + 95, "O₁ (вартість 1)", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(opt_x + 35, panel_y + 125, "Містить n/2 лівих елементів {e₁, ..., e_{n/2}}", size=11, color=INK, anchor="start"))

    frags.append(rect(opt_x + 20, panel_y + 170, opt_w - 40, 85, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(opt_x + 35, panel_y + 195, "O₂ (вартість 1)", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(opt_x + 35, panel_y + 225, "Містить n/2 правих елементів {e_{n/2+1}, ..., e_n}", size=11, color=INK, anchor="start"))

    frags.append(text(opt_x + opt_w / 2, panel_y + 268, "Сумарна вартість OPT = 1 + 1 = 2", size=12, bold=True, color=FIELD))

    # Права панель: Жадібний розв'язок (k множин, що перетинають обидві половини)
    grd_x = 425
    grd_w = 365

    frags.append(rect(grd_x, panel_y, grd_w, panel_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(grd_x + grd_w / 2, panel_y + 24, "Вибір жадібного алгоритму (GREEDY = k)", size=13, bold=True, color=POS))
    frags.append(text(grd_x + grd_w / 2, panel_y + 44, "На кожному кроці обирається множина з трохи більшою часткою", size=11, color=MUTED))

    grd_layers = [
        ("G₁ (вартість 1)", "покриває n/2 елементів (по n/4 з O₁ та O₂)", "#fee2e2"),
        ("G₂ (вартість 1)", "покриває n/4 елементів (по n/8 з O₁ та O₂)", "#fee2e2"),
        ("G₃ (вартість 1)", "покриває n/8 елементів (по n/16 з O₁ та O₂)", "#fee2e2"),
        ("... G_k (вартість 1)", "покриває останні 2 елементи", "#fee2e2"),
    ]

    for idx, (g_name, g_desc, g_bg) in enumerate(grd_layers):
        gy = panel_y + 68 + idx * 44
        frags.append(rect(grd_x + 15, gy, grd_w - 30, 36, fill=g_bg, stroke=POS, sw=1, rx=4))
        frags.append(text(grd_x + 25, gy + 22, g_name, size=11, bold=True, color=POS, anchor="start"))
        frags.append(text(grd_x + grd_w - 25, gy + 22, g_desc, size=10, bold=False, color=INK, anchor="end"))

    frags.append(text(grd_x + grd_w / 2, panel_y + 268, "GREEDY = k = log₂(n) множин → Ratio ≈ 0.5 · ln(n)", size=12, bold=True, color=POS))

    render(os.path.join(OUT_DIR, "greedy-tightness-construction.svg"), w, h, *frags)


def fig_lp_duality_rounding():
    """Фігура 4: Лінійне релаксування, дуальність LP та прямо-двоїсте округлення."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Зв'язок прямої задачі (Primal LP) та двоїстої (Dual LP) у Set Cover", size=15, bold=True, color=INK))

    p_w = 360
    p_h = 280
    p_y = 52
    col1_x = 30
    col2_x = 430

    # Ліва колонка: Пряма релаксація (Primal LP)
    frags.append(rect(col1_x, p_y, p_w, p_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(col1_x + p_w / 2, p_y + 24, "Пряма задача (Primal LP Relaxation)", size=13, bold=True, color=NEG))
    frags.append(text(col1_x + p_w / 2, p_y + 44, "Змінні підмножин: x_S ∈ [0, 1]", size=11, bold=True, color=INK))

    p_box1 = rect(col1_x + 15, p_y + 60, p_w - 30, 48, fill="#ffffff", stroke=NEG, sw=1, rx=4)
    frags.append(p_box1)
    frags.append(text(col1_x + p_w / 2, p_y + 80, "Цільова функція: min ∑ w(S) · x_S", size=12, bold=True, color=NEG))
    frags.append(text(col1_x + p_w / 2, p_y + 98, "(мінімізація дробової вартості вибору)", size=10, color=MUTED))

    p_box2 = rect(col1_x + 15, p_y + 120, p_w - 30, 58, fill="#ffffff", stroke=NEG, sw=1, rx=4)
    frags.append(p_box2)
    frags.append(text(col1_x + p_w / 2, p_y + 142, "Обмеження покриття для кожного e ∈ U:", size=11, bold=True, color=INK))
    frags.append(text(col1_x + p_w / 2, p_y + 164, "∑_{S : e ∈ S} x_S ≥ 1", size=12, bold=True, color=NEG))

    p_box3 = rect(col1_x + 15, p_y + 190, p_w - 30, 75, fill="#dbeafe", stroke=NEG, sw=1, rx=4)
    frags.append(p_box3)
    frags.append(text(col1_x + p_w / 2, p_y + 212, "Частотне округлення (f-approximation):", size=11, bold=True, color=NEG))
    frags.append(text(col1_x + p_w / 2, p_y + 232, "Якщо e належить ≤ f множинам, то", size=10, color=INK))
    frags.append(text(col1_x + p_w / 2, p_y + 252, "обираємо S, якщо x*_S ≥ 1/f → гарантія f·OPT", size=10, bold=True, color=NEG))

    # Права колонка: Двоїста задача (Dual LP)
    frags.append(rect(col2_x, p_y, p_w, p_h, fill="#faf5ff", stroke="#7e22ce", sw=1.5, rx=6))
    frags.append(text(col2_x + p_w / 2, p_y + 24, "Двоїста задача (Dual LP Packing)", size=13, bold=True, color="#7e22ce"))
    frags.append(text(col2_x + p_w / 2, p_y + 44, "Змінні бюджету елементів: y_e ≥ 0", size=11, bold=True, color=INK))

    d_box1 = rect(col2_x + 15, p_y + 60, p_w - 30, 48, fill="#ffffff", stroke="#7e22ce", sw=1, rx=4)
    frags.append(d_box1)
    frags.append(text(col2_x + p_w / 2, p_y + 80, "Цільова функція: max ∑ y_e", size=12, bold=True, color="#7e22ce"))
    frags.append(text(col2_x + p_w / 2, p_y + 98, "(максимізація сумарного внеску елементів)", size=10, color=MUTED))

    d_box2 = rect(col2_x + 15, p_y + 120, p_w - 30, 58, fill="#ffffff", stroke="#7e22ce", sw=1, rx=4)
    frags.append(d_box2)
    frags.append(text(col2_x + p_w / 2, p_y + 142, "Бюджетне обмеження для кожної S ∈ S:", size=11, bold=True, color=INK))
    frags.append(text(col2_x + p_w / 2, p_y + 164, "∑_{e ∈ S} y_e ≤ w(S)", size=12, bold=True, color="#7e22ce"))

    d_box3 = rect(col2_x + 15, p_y + 190, p_w - 30, 75, fill="#f3e8ff", stroke="#7e22ce", sw=1, rx=4)
    frags.append(d_box3)
    frags.append(text(col2_x + p_w / 2, p_y + 212, "Прямо-двоїстий алгоритм (Primal-Dual):", size=11, bold=True, color="#7e22ce"))
    frags.append(text(col2_x + p_w / 2, p_y + 232, "Підвищуємо y_e для непокритих елементів,", size=10, color=INK))
    frags.append(text(col2_x + p_w / 2, p_y + 252, "поки ∑ y_e = w(S) (насичення) → беремо S", size=10, bold=True, color="#7e22ce"))

    # Центральний стрілковий зв'язок слабкої дуальності
    frags.append(arrow(col1_x + p_w + 6, p_y + 80, col2_x - 6, p_y + 80, color=MUTED, sw=1.5))
    frags.append(text((col1_x + p_w + col2_x) / 2, p_y + 70, "Dual ≤ Primal", size=9, bold=True, color=MUTED))

    render(os.path.join(OUT_DIR, "lp-duality-and-rounding.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_universe_subsets()
    fig_greedy_choice_steps()
    fig_tightness_construction()
    fig_lp_duality_rounding()
    print("Всі 4 SVG-фігури згенеровано успішно.")
