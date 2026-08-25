# -*- coding: utf-8 -*-
"""Фігури до статті «Префіксні суми».
Запуск: python figs.py -> пише SVG у ./img/
  prefix-sum-1d, difference-array, modular-pigeonhole, prefix-sum-2d
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
ROW       = "#f4f6f8"

# ── 1. 1D префіксні суми та запит на відрізку ─────────────────────────────
def fig_prefix_sum_1d():
    W, H = 860, 360
    f = [
        text(W / 2, 28, "1D префіксні суми: від лінійного підсумовування до O(1)", size=18, bold=True),
        text(W / 2, 50, "Обчислення суми підмасиву A[3..6] через різницю префіксів P[6] - P[2]",
             size=13, color=MUTED, italic=True)
    ]

    # Вихідний масив A (1-based індексація для наочності)
    f.append(text(70, 105, "Масив A:", size=14, bold=True, anchor="start"))
    a_vals = [3, 1, 4, 1, 5, 9, 2, 6]
    cell_w, cell_h = 75, 42
    start_x, start_y = 160, 80

    for i, val in enumerate(a_vals):
        idx = i + 1
        x = start_x + i * cell_w
        is_in_query = (3 <= idx <= 6)
        bg = GREENFILL if is_in_query else BG
        st = FIELD if is_in_query else LINE
        f.append(rect(x, start_y, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if is_in_query else 1.2, rx=4))
        f.append(text(x + cell_w / 2, start_y + 26, str(val), size=16, bold=is_in_query, color=FIELD if is_in_query else INK))
        f.append(text(x + cell_w / 2, start_y - 8, f"i={idx}", size=11, color=MUTED))

    # Рамка запиту на відрізку
    f.append(rect(start_x + 2 * cell_w - 4, start_y - 4, 4 * cell_w + 8, cell_h + 8, fill="none", stroke=FIELD, sw=2.2, rx=6))
    f.append(text(start_x + 4 * cell_w, start_y + cell_h + 22, "Відрізок підсумовування A[3..6] = 4 + 1 + 5 + 9 = 19", size=13, bold=True, color=FIELD))

    # Масив префіксних сум P (0-based індексація, P[0]=0)
    f.append(text(70, 245, "Префікси P:", size=14, bold=True, anchor="start"))
    p_vals = [0, 3, 4, 8, 9, 14, 23, 25, 31]
    p_start_y = 220
    p_cell_w = 68

    for i, val in enumerate(p_vals):
        x = start_x + i * p_cell_w - 10
        is_r = (i == 6)
        is_l = (i == 2)
        bg = REDFILL if is_r else (BLUEFILL if is_l else BG)
        st = POS if is_r else (NEG if is_l else LINE)
        f.append(rect(x, p_start_y, p_cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if (is_r or is_l) else 1.2, rx=4))
        f.append(text(x + p_cell_w / 2, p_start_y + 26, str(val), size=15, bold=(is_r or is_l), color=POS if is_r else (NEG if is_l else INK)))
        f.append(text(x + p_cell_w / 2, p_start_y + cell_h + 16, f"P[{i}]", size=11, color=POS if is_r else (NEG if is_l else MUTED)))

    # Сполучні лінії різниці
    x_p6 = start_x + 6 * p_cell_w - 10 + p_cell_w / 2
    x_p2 = start_x + 2 * p_cell_w - 10 + p_cell_w / 2

    f.append(line(x_p6, p_start_y, x_p6, p_start_y - 25, color=POS, sw=1.8, dash="3,2"))
    f.append(line(x_p2, p_start_y, x_p2, p_start_y - 25, color=NEG, sw=1.8, dash="3,2"))
    f.append(line(x_p2, p_start_y - 25, x_p6, p_start_y - 25, color=INK, sw=1.8))

    f.append(text(W / 2, 335, "Сума відрізка: Sum(3..6) = P[6] − P[2] = 23 − 4 = 19   [Запит за O(1)]", size=14, bold=True, color=INK))

    render(os.path.join(IMG, "prefix-sum-1d.svg"), W, H, *f)


# ── 2. Різницевий масив та групове оновлення відрізка ───────────────────────
def fig_difference_array():
    W, H = 860, 380
    f = [
        text(W / 2, 28, "Різницевий масив D: оновлення відрізка за O(1)", size=18, bold=True),
        text(W / 2, 50, "Додавання значення v=+4 на відрізку [2..4] змінює лише 2 елементи масиву D",
             size=13, color=MUTED, italic=True)
    ]

    cell_w, cell_h = 75, 40
    start_x = 180

    # Секція 1: Початковий стан
    f.append(text(60, 105, "Початковий A:", size=13, bold=True, anchor="start"))
    a_init = [5, 5, 8, 8, 8, 2]
    d_init = [5, 0, 3, 0, 0, -6]

    for i in range(6):
        x = start_x + i * cell_w
        f.append(rect(x, 85, cell_w, cell_h, fill=BG, stroke=LINE, sw=1.2, rx=4))
        f.append(text(x + cell_w / 2, 110, str(a_init[i]), size=14, color=INK))

    f.append(text(60, 160, "Різницевий D:", size=13, bold=True, anchor="start"))
    for i in range(6):
        x = start_x + i * cell_w
        f.append(rect(x, 140, cell_w, cell_h, fill=ROW, stroke=LINE, sw=1.2, rx=4))
        f.append(text(x + cell_w / 2, 165, str(d_init[i]), size=14, color=INK))

    # Секція 2: Операція оновлення D[2] += 4, D[5] -= 4
    f.append(line(50, 200, W - 50, 200, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text(W / 2, 222, "Операція: Додати +4 до A[2..4]  ⇒  D[2] += 4,  D[5] -= 4", size=14, bold=True, color=POS))

    # Секція 3: Модифікований стан
    d_mod = [5, 0, 7, 0, 0, -10]
    a_mod = [5, 5, 12, 12, 12, 2]

    f.append(text(60, 275, "Оновлений D':", size=13, bold=True, anchor="start"))
    for i in range(6):
        x = start_x + i * cell_w
        is_l = (i == 2)
        is_r = (i == 5)
        bg = GREENFILL if is_l else (REDFILL if is_r else ROW)
        st = FIELD if is_l else (POS if is_r else LINE)
        f.append(rect(x, 255, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if (is_l or is_r) else 1.2, rx=4))
        val_str = str(d_mod[i])
        f.append(text(x + cell_w / 2, 280, val_str, size=14, bold=(is_l or is_r), color=FIELD if is_l else (POS if is_r else INK)))

    f.append(text(60, 330, "Підсумковий A':", size=13, bold=True, anchor="start"))
    for i in range(6):
        x = start_x + i * cell_w
        is_updated = (2 <= i <= 4)
        bg = BLUEFILL if is_updated else BG
        st = NEG if is_updated else LINE
        f.append(rect(x, 310, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if is_updated else 1.2, rx=4))
        f.append(text(x + cell_w / 2, 335, str(a_mod[i]), size=14, bold=is_updated, color=NEG if is_updated else INK))

    render(os.path.join(IMG, "difference-array.svg"), W, H, *f)


# ── 3. Модульні префіксні суми та принцип Діріхле ──────────────────────────
def fig_modular_pigeonhole():
    W, H = 860, 370
    f = [
        text(W / 2, 28, "Модульні префіксні суми та подільність підмасивів", size=18, bold=True),
        text(W / 2, 50, "У масиві з N=6 елементів за модулем m=5 принаймні дві суми P[i] та P[j] збігаються (колізія 1 ≡ 1)",
             size=13, color=MUTED, italic=True)
    ]

    cell_w, cell_h = 72, 42
    start_x = 160

    # Вихідний масив
    f.append(text(50, 105, "Масив A:", size=14, bold=True, anchor="start"))
    a_vals = [4, 2, 7, 3, 5, 1]
    for i, val in enumerate(a_vals):
        x = start_x + i * cell_w + 30
        is_sub = (2 <= i <= 3) # A[2..3] = [7, 3] sum=10
        bg = GREENFILL if is_sub else BG
        st = FIELD if is_sub else LINE
        f.append(rect(x, 80, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if is_sub else 1.2, rx=4))
        f.append(text(x + cell_w / 2, 106, str(val), size=15, bold=is_sub, color=FIELD if is_sub else INK))
        f.append(text(x + cell_w / 2, 72, f"i={i+1}", size=11, color=MUTED))

    # Сума підмасиву
    f.append(text(start_x + 2.5 * cell_w + 30, 142, "Підмасив A[3..4] = [7, 3],  Сума = 10 ≡ 0 (mod 5)", size=12.5, bold=True, color=FIELD))

    # Префікси мод 5
    f.append(text(50, 215, "P[k] mod 5:", size=14, bold=True, anchor="start"))
    p_mod_vals = [0, 4, 1, 3, 1, 1, 2] # P[0]=0, P[1]=4, P[2]=1, P[3]=3, P[4]=1, P[5]=1, P[6]=2
    for k, val in enumerate(p_mod_vals):
        x = start_x + k * cell_w
        is_col = (k == 2 or k == 4)
        bg = REDFILL if is_col else BG
        st = POS if is_col else LINE
        f.append(rect(x, 190, cell_w, cell_h, fill=bg, stroke=st, sw=2.0 if is_col else 1.2, rx=4))
        f.append(text(x + cell_w / 2, 216, str(val), size=16, bold=is_col, color=POS if is_col else INK))
        f.append(text(x + cell_w / 2, 248, f"P[{k}]", size=11, color=POS if is_col else MUTED))

    # Дуга колізії між P[2] та P[4]
    x2 = start_x + 2 * cell_w + cell_w / 2
    x4 = start_x + 4 * cell_w + cell_w / 2
    f.append(f'<path d="M {x2:.1f} 260 C {x2:.1f} 310, {x4:.1f} 310, {x4:.1f} 260" stroke="{POS}" stroke-width="2.0" fill="none" stroke-dasharray="4,3"/>')
    f.append(text((x2 + x4) / 2, 325, "Збіг залишків: P[4] ≡ P[2] ≡ 1 (mod 5)  ⇒  P[4] − P[2] ≡ 0 (mod 5)", size=13, bold=True, color=POS))

    render(os.path.join(IMG, "modular-pigeonhole.svg"), W, H, *f)


# ── 4. 2D префіксні суми та геометрія включень-виключень ────────────────────
def fig_prefix_sum_2d():
    W, H = 860, 400
    f = [
        text(W / 2, 28, "2D префіксні суми: геометрія включень-виключень", size=18, bold=True),
        text(W / 2, 50, "Обчислення суми прямокутника D = P[r2][c2] − P[r1-1][c2] − P[r2][c1-1] + P[r1-1][c1-1]",
             size=13, color=MUTED, italic=True)
    ]

    # Сітка матриці (геометричні прямокутники A, B, C, D)
    grid_x, grid_y = 120, 90
    w_left, w_right = 160, 220
    h_top, h_bottom = 120, 140

    # Область A (топ-ліво)
    f.append(rect(grid_x, grid_y, w_left, h_top, fill="#e8edf8", stroke=NEG, sw=1.5))
    f.append(text(grid_x + w_left / 2, grid_y + h_top / 2, "A (P[r1-1][c1-1])", size=13, bold=True, color=NEG))

    # Область B (топ-право)
    f.append(rect(grid_x + w_left, grid_y, w_right, h_top, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(grid_x + w_left + w_right / 2, grid_y + h_top / 2, "B", size=14, bold=True, color=POS))

    # Область C (бот-ліво)
    f.append(rect(grid_x, grid_y + h_top, w_left, h_bottom, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(grid_x + w_left / 2, grid_y + h_top + h_bottom / 2, "C", size=14, bold=True, color=POS))

    # Область D (цільовий прямокутник [r1..r2] x [c1..c2])
    f.append(rect(grid_x + w_left, grid_y + h_top, w_right, h_bottom, fill=GREENFILL, stroke=FIELD, sw=2.2))
    f.append(text(grid_x + w_left + w_right / 2, grid_y + h_top + h_bottom / 2, "D (Шукана сума)", size=16, bold=True, color=FIELD))

    # Підписи координат на осях
    f.append(text(grid_x + w_left, grid_y - 12, "c1-1", size=12, color=MUTED))
    f.append(text(grid_x + w_left + w_right, grid_y - 12, "c2", size=12, color=MUTED))
    f.append(text(grid_x - 20, grid_y + h_top, "r1-1", size=12, color=MUTED, anchor="end"))
    f.append(text(grid_x - 20, grid_y + h_top + h_bottom, "r2", size=12, color=MUTED, anchor="end"))

    # Формула справа
    fx = 540
    f.append(rect(fx, 90, 280, 260, fill=ROW, stroke=LINE, sw=1.2, rx=8))
    f.append(text(fx + 140, 120, "Баланс областей:", size=15, bold=True, color=INK))

    f.append(text(fx + 20, 160, "P[r2][c2] = A + B + C + D", size=13, anchor="start", color=INK))
    f.append(text(fx + 20, 190, "− P[r1-1][c2] = −(A + B)", size=13, anchor="start", color=POS))
    f.append(text(fx + 20, 220, "− P[r2][c1-1] = −(A + C)", size=13, anchor="start", color=POS))
    f.append(text(fx + 20, 250, "+ P[r1-1][c1-1] = + A", size=13, anchor="start", color=NEG))

    f.append(line(fx + 15, 270, fx + 265, 270, color=LINE, sw=1.2))
    f.append(text(fx + 140, 305, "Результат: D", size=16, bold=True, color=FIELD))

    render(os.path.join(IMG, "prefix-sum-2d.svg"), W, H, *f)


if __name__ == "__main__":
    fig_prefix_sum_1d()
    fig_difference_array()
    fig_modular_pigeonhole()
    fig_prefix_sum_2d()
    print("Успішно згенеровано 4 фігури SVG у ./img/")
