# -*- coding: utf-8 -*-
"""Фігури до статті «Дерево Фенвіка».
Запуск: python figs.py -> пише SVG у ./img/
  tree-structure, lsb-decomposition, update-query-paths, range-update-dual
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL   = "#fdecea"
BLUEFILL  = "#eaf0fd"
PURPLEFILL = "#f3e8ff"
ROW       = "#f4f6f8"

# ── 1. Деревоподібна структура інтервалів дерева Фенвіка ──────────────────
def fig_tree_structure():
    W, H = 860, 420
    f = [
        text(W / 2, 28, "Ієрархія покриття інтервалів у дереві Фенвіка (N = 8)", size=18, bold=True),
        text(W / 2, 50, "Кожен елемент T[i] відповідає півінтервалу (i - LSB(i), i] довжиною LSB(i)",
             size=13, color=MUTED, italic=True)
    ]

    # Нижній шар: вихідні елементи масиву A[1..8]
    start_x, start_y = 110, 340
    cell_w, cell_h = 75, 36
    
    f.append(text(50, start_y + 22, "Елементи A:", size=13, bold=True, anchor="start"))
    a_vals = [3, 1, 4, 1, 5, 9, 2, 6]
    for i in range(8):
        x = start_x + i * cell_w
        f.append(rect(x, start_y, cell_w, cell_h, fill=BG, stroke=LINE, sw=1.2, rx=4))
        f.append(text(x + cell_w / 2, start_y + 22, f"A[{i+1}]={a_vals[i]}", size=12, color=INK))

    intervals = [
        (1, 0, 1, 3, 110, 270, cell_w, BLUEFILL, FIELD),
        (2, 0, 2, 4, 110, 210, cell_w * 2, GREENFILL, FIELD),
        (3, 2, 3, 4, 110 + 2 * cell_w, 270, cell_w, BLUEFILL, FIELD),
        (4, 0, 4, 9, 110, 150, cell_w * 4, PURPLEFILL, FIELD),
        (5, 4, 5, 5, 110 + 4 * cell_w, 270, cell_w, BLUEFILL, FIELD),
        (6, 4, 6, 14, 110 + 4 * cell_w, 210, cell_w * 2, GREENFILL, FIELD),
        (7, 6, 7, 2, 110 + 6 * cell_w, 270, cell_w, BLUEFILL, FIELD),
        (8, 0, 8, 31, 110, 90, cell_w * 8, REDFILL, POS)
    ]

    f.append(text(50, 110, "Вузли T[i]:", size=13, bold=True, anchor="start"))

    for idx, l, r, val, x, y, w, fill_c, stroke_c in intervals:
        f.append(rect(x + 2, y, w - 4, 38, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        lbl = f"T[{idx}] = {val}  (({l},{r}])"
        f.append(text(x + w / 2, y + 23, lbl, size=12, bold=True, color=INK))

    for i in range(9):
        x = start_x + i * cell_w
        f.append(line(x, 80, x, 340, color=MUTED, sw=0.8, dash="2,3"))

    render(os.path.join(IMG, "tree-structure.svg"), W, H, *f)


# ── 2. Механіка виділення наймолодшого біта LSB(i) = i & (-i) ──────────────
def fig_lsb_decomposition():
    W, H = 860, 360
    f = [
        text(W / 2, 28, "Алгебра побітового виділення LSB: i & (-i)", size=18, bold=True),
        text(W / 2, 50, "Операція доповняльного коду -i = (~i) + 1 інвертує старші біти та зберігає наймолодшу одиницю",
             size=13, color=MUTED, italic=True)
    ]

    start_x = 220
    box_w, box_h = 420, 36

    f.append(text(60, 95, "Число i = 12:", size=14, bold=True, anchor="start"))
    f.append(rect(start_x, 75, box_w, box_h, fill=BG, stroke=LINE, sw=1.2, rx=4))
    f.append(text(start_x + box_w / 2, 98, "0 0 0 0   1 1 0 0_2", size=16, bold=True, color=INK))

    f.append(text(60, 150, "Побітове НІ ~i:", size=14, bold=True, anchor="start"))
    f.append(rect(start_x, 130, box_w, box_h, fill=ROW, stroke=LINE, sw=1.2, rx=4))
    f.append(text(start_x + box_w / 2, 153, "1 1 1 1   0 0 1 1_2", size=16, color=MUTED))

    f.append(text(60, 205, "Число -i = (~i) + 1:", size=14, bold=True, color=POS, anchor="start"))
    f.append(rect(start_x, 185, box_w, box_h, fill=REDFILL, stroke=POS, sw=1.6, rx=4))
    f.append(text(start_x + box_w / 2, 208, "1 1 1 1   0 1 0 0_2", size=16, bold=True, color=POS))

    f.append(line(50, 238, W - 50, 238, color=MUTED, sw=1.0, dash="4,4"))

    f.append(text(60, 280, "Результат i & (-i):", size=14, bold=True, color=FIELD, anchor="start"))
    f.append(rect(start_x, 260, box_w, box_h, fill=GREENFILL, stroke=FIELD, sw=2.0, rx=4))
    f.append(text(start_x + box_w / 2, 283, "0 0 0 0   0 1 0 0_2  =  4", size=17, bold=True, color=FIELD))

    f.append(rect(start_x + 236, 263, 65, 30, fill="none", stroke=POS, sw=2.0, rx=3))
    f.append(text(start_x + 268, 320, "Єдиний спільний 1-біт (LSB = 4)", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "lsb-decomposition.svg"), W, H, *f)


# ── 3. Шляхи обходу: Запит префіксної суми vs Оновлення елемента ─────────
def fig_update_query_paths():
    W, H = 860, 390
    f = [
        text(W / 2, 28, "Двонаправлений обхід дерева Фенвіка: Запит vs Оновлення", size=18, bold=True),
        text(W / 2, 50, "Запит віднімає LSB(i) для підсумовування; Оновлення додає LSB(i) для підйому до батьків",
             size=13, color=MUTED, italic=True)
    ]

    qx = 60
    f.append(rect(qx, 85, 340, 265, fill=BLUEFILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(qx + 170, 115, "Запит префікса Pref(7)", size=15, bold=True, color=FIELD))
    f.append(text(qx + 170, 138, "Кроки: i = i - LSB(i)", size=13, color=MUTED, italic=True))

    steps_q = [
        ("1. i = 7 (0111_2), LSB=1", "Додати T[7]  (інтервал (6,7])"),
        ("2. i = 6 (0110_2), LSB=2", "Додати T[6]  (інтервал (4,6])"),
        ("3. i = 4 (0100_2), LSB=4", "Додати T[4]  (інтервал (0,4])"),
        ("4. i = 0 (0000_2)", "Зупинка!  Сума = T[7]+T[6]+T[4]")
    ]

    for idx, (st, desc) in enumerate(steps_q):
        y = 165 + idx * 42
        f.append(rect(qx + 15, y, 310, 34, fill=BG, stroke=FIELD if idx<3 else LINE, sw=1.2, rx=4))
        f.append(text(qx + 25, y + 21, st, size=11.5, bold=True, anchor="start", color=FIELD if idx<3 else INK))
        f.append(text(qx + 315, y + 21, desc, size=11, anchor="end", color=INK))

    ux = 460
    f.append(rect(ux, 85, 340, 265, fill=REDFILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(ux + 170, 115, "Точкове оновлення Add(3, +v)", size=15, bold=True, color=POS))
    f.append(text(ux + 170, 138, "Кроки: i = i + LSB(i)", size=13, color=MUTED, italic=True))

    steps_u = [
        ("1. i = 3 (0011_2), LSB=1", "Оновити T[3] += v"),
        ("2. i = 4 (0100_2), LSB=4", "Оновити T[4] += v"),
        ("3. i = 8 (1000_2), LSB=8", "Оновити T[8] += v"),
        ("4. i = 16 > N=8", "Зупинка! Оновлено 3 вузли")
    ]

    for idx, (st, desc) in enumerate(steps_u):
        y = 165 + idx * 42
        f.append(rect(ux + 15, y, 310, 34, fill=BG, stroke=POS if idx<3 else LINE, sw=1.2, rx=4))
        f.append(text(ux + 25, y + 21, st, size=11.5, bold=True, anchor="start", color=POS if idx<3 else INK))
        f.append(text(ux + 315, y + 21, desc, size=11, anchor="end", color=INK))

    render(os.path.join(IMG, "update-query-paths.svg"), W, H, *f)


# ── 4. Двохмасивне дерево Фенвіка для Range Update & Range Query ──────────
def fig_range_update_dual():
    W, H = 860, 380
    f = [
        text(W / 2, 28, "Двохмасивна структура для оновлення та запиту відрізка", size=18, bold=True),
        text(W / 2, 50, "Розклад префіксної суми сумарного різницевого масиву через два дерева T1 та T2",
             size=13, color=MUTED, italic=True)
    ]

    f.append(rect(70, 85, 720, 75, fill=ROW, stroke=LINE, sw=1.2, rx=6))
    f.append(text(430, 115, "Формула префіксної суми відрізка:  Pref(p) = ∑_{i=1}^p A[i] = p · ∑_{i=1}^p D[i]  −  ∑_{i=1}^p (i − 1) · D[i]",
                  size=14, bold=True, color=INK))
    f.append(text(430, 142, "Де D[i] — різницевий масив: D[i] = A[i] − A[i-1]", size=12.5, color=MUTED, italic=True))

    f.append(rect(70, 185, 340, 160, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(240, 215, "Перше дерево Фенвіка T1", size=15, bold=True, color=FIELD))
    f.append(text(240, 242, "Зберігає чисто різницеві значення D[i]", size=12.5, color=INK))
    f.append(text(240, 275, "При RangeUpdate(l, r, v):", size=12, bold=True, color=FIELD))
    f.append(text(240, 298, "T1.Add(l, v),   T1.Add(r + 1, -v)", size=12, color=INK))

    f.append(rect(450, 185, 340, 160, fill=PURPLEFILL, stroke=POS, sw=1.5, rx=8))
    f.append(text(620, 215, "Друге дерево Фенвіка T2", size=15, bold=True, color=POS))
    f.append(text(620, 242, "Зберігає зважені значення (i − 1) · D[i]", size=12.5, color=INK))
    f.append(text(620, 275, "При RangeUpdate(l, r, v):", size=12, bold=True, color=POS))
    f.append(text(620, 298, "T2.Add(l, (l-1)·v),   T2.Add(r + 1, -r·v)", size=12, color=INK))

    render(os.path.join(IMG, "range-update-dual.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tree_structure()
    fig_lsb_decomposition()
    fig_update_query_paths()
    fig_range_update_dual()
    print("Успішно згенеровано 4 фігури SVG у ./img/")
