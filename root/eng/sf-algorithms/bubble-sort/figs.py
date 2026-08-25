# -*- coding: utf-8 -*-
"""Фігури для статті «Сортування бульбашкою (Bubble Sort)».
Генерує чотири SVG у ./img:
  1. bubble-sort-pass.svg — анатомія одного проходу: попарне порівняння та спливання максимуму.
  2. bubble-sort-invariants.svg — поділ масиву на активну невідсортовану зону та фінальний відсортований суфікс.
  3. bubble-optimizations.svg — механізм прапорця swapped та стрибок межі через last_swap_index.
  4. rabbits-and-turtles.svg — асиметрія швидкості переміщення: кролики проти черепах та реверсний прохід.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

ZONE_SORTED = "#e6f7ee"     # світло-зелений (відсортована фінальна зона)
ZONE_UNSORT = "#eef2f7"     # світло-сірий (активна невідсортована зона)
SWAP_ACTIVE = "#fdecea"     # світло-червоний (пара під час обміну)
COMP_ACTIVE = "#fbf4e6"     # світло-жовтий (пара під час порівняння без обміну)
COLOR_GREEN = "#1e824c"
COLOR_BLUE  = "#2457d6"
COLOR_RED   = "#c0392b"
COLOR_PURPLE = "#8e44ad"


def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5, val, size=15, color=tc, bold=True))


# ── Фігура 1: Анатомія одного проходу ─────────────────────────────────────────
def fig_pass():
    W, H = 760, 360
    cw, ch = 48, 38
    x0 = 210
    y0 = 60

    steps = [
        ("Початковий стан", [5, 1, 4, 2, 8], -1, -1, False, "Початок проходу"),
        ("Порівняння A[0], A[1]", [1, 5, 4, 2, 8], 0, 1, True, "5 > 1 → обмін (5 рухається праворуч)"),
        ("Порівняння A[1], A[2]", [1, 4, 5, 2, 8], 1, 2, True, "5 > 4 → обмін (5 рухається праворуч)"),
        ("Порівняння A[2], A[3]", [1, 4, 2, 5, 8], 2, 3, True, "5 > 2 → обмін (5 рухається праворуч)"),
        ("Порівняння A[3], A[4]", [1, 4, 2, 5, 8], 3, 4, False, "5 < 8 → без обміну, 8 — новий лідер"),
    ]

    f = []
    f.append(text(x0 - 20, y0 - 15, "Крок порівняння", size=13, anchor="end", color=MUTED, bold=True))
    for i in range(5):
        f.append(text(x0 + i * cw + cw / 2, y0 - 15, "[%d]" % i, size=13, anchor="middle", color=MUTED))
    f.append(text(x0 + 5 * cw + 20, y0 - 15, "Локальна операція та наслідок", size=13, anchor="start", color=MUTED, bold=True))

    y = y0
    for label, vals, p1, p2, did_swap, note in steps:
        f.append(text(x0 - 20, y + ch / 2 + 5, label, size=13, anchor="end", color=INK, bold=True))
        for i, v in enumerate(vals):
            if i == p1 or i == p2:
                fill = SWAP_ACTIVE if did_swap else COMP_ACTIVE
                tc = COLOR_RED if did_swap else COLOR_PURPLE
            elif i == 4 and p1 == 3:
                fill = ZONE_SORTED
                tc = COLOR_GREEN
            else:
                fill = ZONE_UNSORT
                tc = INK
            f.append(cell(x0 + i * cw, y, cw, ch, str(v), fill=fill, tc=tc))

        f.append(text(x0 + 5 * cw + 20, y + ch / 2 + 5, note, size=12, anchor="start", color=COLOR_BLUE))
        y += 52

    f.append(text(W / 2, y + 16, "Результат: найбільший елемент (8) гарантовано сплив на позицію [4]", size=13, color=COLOR_GREEN, bold=True))

    render(os.path.join(IMG, "bubble-sort-pass.svg"), W, H, *f,
           title="Анатомія одного проходу: попарне порівняння та спливання максимуму")


# ── Фігура 2: Інваріант циклу та поділ масиву ─────────────────────────────────
def fig_invariants():
    W, H = 700, 310
    cw, ch = 54, 44
    x0 = 170
    rows = [
        ("Початок (k = 0)", [5, 2, 8, 1, 9, 4], 6, "Суфікс порожній"),
        ("Ітерація 1 (k = 1)", [2, 5, 1, 8, 4, 9], 5, "Елемент 9 закріплено на позиції [5]"),
        ("Ітерація 2 (k = 2)", [2, 1, 5, 4, 8, 9], 4, "Елементи {8, 9} на фінальних місцях"),
        ("Ітерація 3 (k = 3)", [1, 2, 4, 5, 8, 9], 3, "Елементи {5, 8, 9} на фінальних місцях"),
    ]
    f = []

    # Легенда
    ly = 50
    f.append(rect(140, ly - 13, 16, 16, fill=ZONE_UNSORT, stroke=LINE, sw=1.2, rx=3))
    f.append(text(162, ly, "активна невідсортована зона A[0..N-1-k]", size=12, anchor="start", color=MUTED))
    f.append(rect(430, ly - 13, 16, 16, fill=ZONE_SORTED, stroke=LINE, sw=1.2, rx=3))
    f.append(text(452, ly, "фінальний відсортований суфікс A[N-k..N-1]", size=12, anchor="start", color=MUTED))

    y = 86
    for label, vals, unsorted_cnt, note in rows:
        f.append(text(x0 - 16, y + ch / 2 + 5, label, size=13, anchor="end", color=MUTED, bold=True))
        for idx, v in enumerate(vals):
            is_sorted = (idx >= unsorted_cnt)
            fill = ZONE_SORTED if is_sorted else ZONE_UNSORT
            tc = COLOR_GREEN if is_sorted else INK
            f.append(cell(x0 + idx * cw, y, cw, ch, str(v), fill=fill, tc=tc))

        if unsorted_cnt < len(vals):
            bx = x0 + unsorted_cnt * cw
            f.append(line(bx, y - 6, bx, y + ch + 6, color=COLOR_RED, sw=3.0))

        f.append(text(x0 + len(vals) * cw + 18, y + ch / 2 + 5, note, size=12, anchor="start", color=COLOR_BLUE))
        y += 54

    f.append(text(W / 2, y + 14, "Інваріант: кожен елемент суфікса ≥ за будь-який елемент невідсортованого префікса", size=13,
                  anchor="middle", color=COLOR_RED, bold=True))

    render(os.path.join(IMG, "bubble-sort-invariants.svg"), W, H, *f,
           title="Інваріант сортування: активна зона та фінальний суфікс")


# ── Фігура 3: Оптимізації (прапорець та last_swap_index) ─────────────────────
def fig_optimizations():
    W, H = 760, 340
    cw, ch = 48, 40
    f = []

    f.append(text(W / 2, 48, "Оптимізація 1: Ранній вихід за прапорцем swapped = false", size=14, bold=True, color=COLOR_BLUE))

    x1 = 150
    y1 = 68
    vals1 = [1, 2, 3, 5, 4, 6, 7]
    for i, v in enumerate(vals1):
        f.append(cell(x1 + i * cw, y1, cw, ch, str(v), fill=ZONE_UNSORT))
    f.append(text(x1 + len(vals1) * cw + 15, y1 + ch / 2 + 5, "Прохід 1: swap(5, 4) → swapped = true", size=12, anchor="start", color=COLOR_RED))

    y2 = 122
    vals2 = [1, 2, 3, 4, 5, 6, 7]
    for i, v in enumerate(vals2):
        f.append(cell(x1 + i * cw, y2, cw, ch, str(v), fill=ZONE_SORTED, tc=COLOR_GREEN))
    f.append(text(x1 + len(vals2) * cw + 15, y2 + ch / 2 + 5, "Прохід 2: 0 обмінів → swapped = false → STOP!", size=12, anchor="start", color=COLOR_GREEN, bold=True))

    f.append(line(50, 180, W - 50, 180, color=LINE, sw=1.0, dash="4,4"))

    f.append(text(W / 2, 204, "Оптимізація 2: Стрибок межі через індекс останнього обміну last_swap", size=14, bold=True, color=COLOR_PURPLE))

    y3 = 224
    vals3 = [3, 1, 2, 4, 5, 6, 7]
    for i, v in enumerate(vals3):
        fill = SWAP_ACTIVE if i <= 2 else ZONE_SORTED
        tc = COLOR_RED if i <= 2 else COLOR_GREEN
        f.append(cell(x1 + i * cw, y3, cw, ch, str(v), fill=fill, tc=tc))

    f.append(arrow(x1 + 2 * cw + cw / 2, y3 + ch + 28, x1 + 2 * cw + cw / 2, y3 + ch + 4, color=COLOR_RED, sw=2.0))
    f.append(text(x1 + 2 * cw + cw / 2, y3 + ch + 42, "Останній обмін на idx=1 (last_swap = 2)", size=12, color=COLOR_RED, bold=True))

    f.append(text(x1 + len(vals3) * cw + 15, y3 + ch / 2 + 5, "Наступний прохід обмежено N=2 замість N=6", size=12, anchor="start", color=COLOR_PURPLE, bold=True))

    render(os.path.join(IMG, "bubble-optimizations.svg"), W, H, *f,
           title="Оптимізації: прапорець переривання та стрибок межі")


# ── Фігура 4: Кролики, черепахи та двонаправлений шейкер ───────────────────────
def fig_rabbits_turtles():
    W, H = 760, 360
    cw, ch = 48, 38
    x0 = 170
    f = []

    f.append(text(W / 2, 44, "Асиметрія: «Кролик» (великий зліва) vs «Черепаха» (малий справа)", size=14, bold=True))

    # Схема кролика
    y_r = 64
    vals_r = [9, 2, 3, 4, 5]
    f.append(text(x0 - 16, y_r + ch / 2 + 5, "Кролик (9 на [0]):", size=12, anchor="end", color=COLOR_RED, bold=True))
    for i, v in enumerate(vals_r):
        fill = SWAP_ACTIVE if i == 0 else ZONE_UNSORT
        tc = COLOR_RED if i == 0 else INK
        f.append(cell(x0 + i * cw, y_r, cw, ch, str(v), fill=fill, tc=tc))
    f.append(arrow(x0 + cw / 2, y_r - 12, x0 + 4 * cw + cw / 2, y_r - 12, color=COLOR_RED, sw=2.0))
    f.append(text(x0 + 2 * cw + cw / 2, y_r - 20, "1 прохід → 9 перелітає на позицію [4]", size=11, color=COLOR_RED, bold=True))
    f.append(text(x0 + 5 * cw + 15, y_r + ch / 2 + 5, "Швидкість: N-1 кроків за 1 прохід", size=12, anchor="start", color=COLOR_RED))

    # Схема черепахи
    y_t = 142
    vals_t1 = [2, 3, 4, 5, 1]
    f.append(text(x0 - 16, y_t + ch / 2 + 5, "Черепаха (1 на [4]):", size=12, anchor="end", color=COLOR_BLUE, bold=True))
    for i, v in enumerate(vals_t1):
        fill = SWAP_ACTIVE if i == 4 else ZONE_UNSORT
        tc = COLOR_BLUE if i == 4 else INK
        f.append(cell(x0 + i * cw, y_t, cw, ch, str(v), fill=fill, tc=tc))
    f.append(arrow(x0 + 4 * cw + cw / 2, y_t + ch + 12, x0 + 3 * cw + cw / 2, y_t + ch + 12, color=COLOR_BLUE, sw=2.0))
    f.append(text(x0 + 3.5 * cw, y_t + ch + 26, "зсув лише на 1 позицію вліво", size=11, color=COLOR_BLUE, bold=True))
    f.append(text(x0 + 5 * cw + 15, y_t + ch / 2 + 5, "Потрібно N-1 = 4 повні проходи!", size=12, anchor="start", color=COLOR_BLUE))

    f.append(line(50, 206, W - 50, 206, color=LINE, sw=1.0, dash="4,4"))

    # Розв'язання через Cocktail Shaker
    y_s = 230
    f.append(text(W / 2, y_s, "Розв'язання у Cocktail Shaker Sort: реверсний прохід тягне черепаху вліво", size=13, color=COLOR_GREEN, bold=True))
    y_s2 = 250
    vals_s = [1, 2, 3, 4, 5]
    f.append(text(x0 - 16, y_s2 + ch / 2 + 5, "Зворотний прохід:", size=12, anchor="end", color=COLOR_GREEN, bold=True))
    for i, v in enumerate(vals_s):
        f.append(cell(x0 + i * cw, y_s2, cw, ch, str(v), fill=ZONE_SORTED, tc=COLOR_GREEN))
    f.append(arrow(x0 + 4 * cw + cw / 2, y_s2 - 12, x0 + cw / 2, y_s2 - 12, color=COLOR_GREEN, sw=2.0))
    f.append(text(x0 + 2 * cw + cw / 2, y_s2 - 20, "1 реверсний прохід → 1 миттєво стає на позицію [0]", size=11, color=COLOR_GREEN, bold=True))
    f.append(text(x0 + 5 * cw + 15, y_s2 + ch / 2 + 5, "Всього 2 проходи замість 4", size=12, anchor="start", color=COLOR_GREEN, bold=True))

    render(os.path.join(IMG, "rabbits-and-turtles.svg"), W, H, *f,
           title="Асиметрія швидкості та двонаправлений рух у Cocktail Shaker Sort")


if __name__ == "__main__":
    fig_pass()
    fig_invariants()
    fig_optimizations()
    fig_rabbits_turtles()
    print("OK: generated SVGs successfully")
