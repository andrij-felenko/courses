# -*- coding: utf-8 -*-
"""Фігури до статті «Принцип Діріхле».
Запуск: python figs.py -> пише SVG у ./img/
  pigeonhole-boxes, prefix-sums-mod, ramsey-r33, compression-tree
Стиль і помічники — зі спільного svgkit."""
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


# ── 1. Класична схема: n об'єктів у k комірках (n > k) ──────────────────────
def fig_pigeonhole_boxes():
    W, H = 900, 400
    f = [
        text(W / 2, 30, "Принцип Діріхле: n об'єктів у k комірках (n > k)", size=18, bold=True),
        text(W / 2, 52, "5 елементів розподіляються по 4 комірках — принаймні одна комірка містить ≥ 2 елементи",
             size=12.5, color=MUTED, italic=True)
    ]

    # Об'єкти ліворуч (5 елементів)
    f.append(text(140, 95, "Множина X (5 елементів)", size=14, bold=True, color=FIELD))
    f.append(rect(40, 110, 200, 240, fill="#fbfcfd", stroke=FIELD, sw=1.6, rx=10))

    items = [
        (140, 145, "x₁", "#27ae60"),
        (140, 190, "x₂", "#27ae60"),
        (140, 235, "x₃", "#c0392b"),
        (140, 280, "x₄", "#27ae60"),
        (140, 325, "x₅", "#c0392b")
    ]
    for x, y, lab, col in items:
        f.append(circle(x, y, 16, fill=BG, stroke=col, sw=2.0))
        f.append(text(x, y + 4, lab, size=13, bold=True, color=col))

    # Комірки праворуч (4 комірки)
    f.append(text(660, 95, "Множина Y (4 комірки)", size=14, bold=True, color=NEG))
    boxes_y = [120, 175, 230, 285]
    box_labs = ["Комірка A", "Комірка B (колізія!)", "Комірка C", "Комірка D"]

    for i, (by, blab) in enumerate(zip(boxes_y, box_labs)):
        is_collision = (i == 1)
        bg_col = REDFILL if is_collision else ROW
        st_col = POS if is_collision else LINE
        f.append(rect(540, by, 240, 46, fill=bg_col, stroke=st_col, sw=1.8 if is_collision else 1.2, rx=6))
        f.append(text(660, by + 27, blab, size=13, bold=True if is_collision else False, color=POS if is_collision else INK))

    # Стрілки відображення f: X -> Y
    arrows_data = [
        (245, 145, 535, 143, FIELD, False),
        (245, 190, 535, 190, FIELD, False),
        (245, 235, 535, 206, POS, True),
        (245, 280, 535, 253, FIELD, False),
        (245, 325, 535, 308, FIELD, False)
    ]
    for x1, y1, x2, y2, col, is_col in arrows_data:
        sw = 2.2 if is_col else 1.5
        dash = "5,3" if is_col else None
        f.append(line(x1, y1, x2, y2, color=col, sw=sw, dash=dash))
        f.append(circle(x2, y2, 3, fill=col, stroke=col, sw=1))

    # Виноска-пояснення знизу
    f.append(fitbox(450, 365, 780, 36,
                    "Ін'єкція неможлива: 5 елементів не можна розмістити в 4 комірках без збігу (f(x₂) = f(x₃) = Комірка B)",
                    size=12.5, fill=REDFILL, stroke=POS, sw=1.5, color=INK))

    render(os.path.join(IMG, "pigeonhole-boxes.svg"), W, H, *f)


# ── 2. Префіксні суми за модулем N ─────────────────────────────────────────
def fig_prefix_sums_mod():
    W, H = 920, 420
    f = [
        text(W / 2, 28, "Підмасив із сумою, кратною N (N = 5)", size=18, bold=True),
        text(W / 2, 50, "6 префіксних сум S₀..S₅ беруть 5 можливих остач (0..4) — дві остачі збігаються!",
             size=12.5, color=MUTED, italic=True)
    ]

    # Масив елементів
    f.append(text(120, 95, "Масив A (N=5):", size=13.5, bold=True, color=INK, anchor="left"))
    arr_vals = [4, 7, 2, 9, 5]
    cell_w = 110
    start_x = 260
    y_arr = 80

    for i, val in enumerate(arr_vals):
        x = start_x + i * cell_w
        f.append(rect(x, y_arr, cell_w - 6, 36, fill=ROW, stroke=LINE, sw=1.2, rx=4))
        f.append(text(x + (cell_w - 6) / 2, y_arr + 23, f"A[{i+1}] = {val}", size=13, bold=True))

    # Префіксні суми S_k
    f.append(text(60, 175, "Префіксні суми Sₖ:", size=13.5, bold=True, color=FIELD, anchor="left"))
    sums = [0, 4, 11, 13, 22, 27]
    mods = [0, 4, 1, 3, 2, 2]

    sw_box = 95
    sx2 = 220
    y_sum = 155

    for k in range(6):
        x = sx2 + k * (sw_box + 12)
        is_match = (k == 4 or k == 5)
        bg = REDFILL if is_match else GREENFILL
        st = POS if is_match else FIELD

        f.append(rect(x, y_sum, sw_box, 58, fill=bg, stroke=st, sw=1.8 if is_match else 1.2, rx=6))
        f.append(text(x + sw_box / 2, y_sum + 22, f"S{k} = {sums[k]}", size=13, bold=True))
        f.append(text(x + sw_box / 2, y_sum + 46, f"mod 5 = {mods[k]}", size=12.5, bold=True if is_match else False, color=POS if is_match else MUTED))

    # Дуга між S4 та S5
    x_s4 = sx2 + 4 * (sw_box + 12) + sw_box / 2
    x_s5 = sx2 + 5 * (sw_box + 12) + sw_box / 2

    f.append(line(x_s4, 230, x_s5, 230, color=POS, sw=3.0))
    f.append(text((x_s4 + x_s5) / 2, 252, "Збіг остач: S₄ ≡ S₅ ≡ 2 (mod 5)", size=13.5, bold=True, color=POS))

    # Пояснення суми підмасиву
    f.append(fitbox(W / 2, 335, 840, 70,
                    "Сума підмасиву A[5] = S₅ - S₄ = 27 - 22 = 5 (кратно 5!).\n"
                    "Оскільки S₄ mod 5 = S₅ mod 5, їхня різниця S₅ - S₄ ділиться на 5 без остачі.\n"
                    "Принцип Діріхле гарантує існування двох таких префіксних сум для будь-якого масиву з N елементів.",
                    size=12.5, fill="#f9fbfd", stroke=NEG, sw=1.5, color=INK))

    render(os.path.join(IMG, "prefix-sums-mod.svg"), W, H, *f)


# ── 3. Граф Рамсея R(3,3) = 6 ──────────────────────────────────────────────
def fig_ramsey_r33():
    W, H = 880, 480
    f = [
        text(W / 2, 28, "Теорема Рамсея R(3,3) = 6 та принцип Діріхле", size=18, bold=True),
        text(W / 2, 50, "У будь-якому повній графі з 6 вершин з 2-розфарбуванням ребер є одноколірний трикутник",
             size=12.5, color=MUTED, italic=True)
    ]

    cx, cy, r = 300, 250, 150
    vertices = []
    labels = ["A", "B", "C", "D", "E", "F"]
    for i in range(6):
        angle = math.pi / 2 - i * (2 * math.pi / 6)
        vx = cx + r * math.cos(angle)
        vy = cy - r * math.sin(angle)
        vertices.append((vx, vy, labels[i]))

    edges = []
    for i in range(6):
        for j in range(i + 1, 6):
            if (i, j) in [(0, 1), (0, 2), (1, 2)]:
                col = POS
                hl = True
            elif i == 0 and j == 3:
                col = POS
                hl = False
            elif i == 0:
                col = NEG
                hl = False
            elif (i, j) in [(1, 3), (2, 4), (3, 5)]:
                col = POS
                hl = False
            else:
                col = NEG
                hl = False
            edges.append((i, j, col, hl))

    for i, j, col, hl in edges:
        x1, y1, _ = vertices[i]
        x2, y2, _ = vertices[j]
        sw = 3.2 if hl else 1.2
        f.append(line(x1, y1, x2, y2, color=col, sw=sw))

    for vx, vy, lab in vertices:
        is_tri = lab in ["A", "B", "C"]
        bg = REDFILL if is_tri else BG
        st = POS if is_tri else LINE
        f.append(circle(vx, vy, 18, fill=bg, stroke=st, sw=2.2 if is_tri else 1.5))
        f.append(text(vx, vy + 5, lab, size=14, bold=True, color=POS if is_tri else INK))

    f.append(rect(500, 90, 350, 340, fill="#fbfcfd", stroke=LINE, sw=1.4, rx=8))
    f.append(text(675, 118, "Кроки доведення за Діріхле:", size=14, bold=True, color=INK))

    steps = [
        "1. Фіксуємо вершину A. В неї входить\n   5 ребер до решти вершин.",
        "2. 5 ребер фарбуємо в 2 кольори\n   (червоний / синій).",
        "3. За принципом Діріхле ⌈5/2⌉ = 3:\n   принаймні 3 ребра від A мають\n   однаковий колір (наприклад, червоний\n   до B, C, D).",
        "4. Якщо між B, C, D є хоч одне\n   червоне ребро (напр. B-C) — маємо\n   червоний трикутник A-B-C!",
        "5. Якщо всі ребра між B,C,D сині —\n   маємо синій трикутник B-C-D!"
    ]
    sy = 150
    for stp in steps:
        f.append(mtext(515, sy, stp, size=11.5, color=INK, anchor="left", lh=1.2))
        sy += 54

    render(os.path.join(IMG, "ramsey-r33.svg"), W, H, *f)


# ── 4. Неможливість універсального стиснення без втрат ──────────────────────
def fig_compression_tree():
    W, H = 880, 400
    f = [
        text(W / 2, 28, "Неможливість універсального стиснення без втрат", size=18, bold=True),
        text(W / 2, 50, "Множина N-бітових файлів (2ᴺ) більша за множину коротших файлів (2ᴺ - 1)",
             size=12.5, color=MUTED, italic=True)
    ]

    f.append(text(200, 95, "Вхідні файли (N=3 біти): 2³ = 8", size=13.5, bold=True, color=FIELD))
    f.append(rect(60, 110, 280, 240, fill="#fbfcfd", stroke=FIELD, sw=1.6, rx=8))

    in_files = ["000", "001", "010", "011", "100", "101", "110", "111"]
    in_y = [132, 160, 188, 216, 244, 272, 300, 328]

    for i, (fn, y) in enumerate(zip(in_files, in_y)):
        is_col = (i == 2 or i == 6)
        col = POS if is_col else INK
        bg = REDFILL if is_col else ROW
        f.append(rect(90, y - 12, 220, 22, fill=bg, stroke=col, sw=1.2, rx=4))
        f.append(text(200, y + 3, f"Файл {i+1}: «{fn}»", size=12, bold=is_col, color=col))

    f.append(text(660, 95, "Вихідні файли (< 3 біти): 2³ - 1 = 7", size=13.5, bold=True, color=NEG))
    f.append(rect(520, 110, 280, 240, fill="#fbfcfd", stroke=NEG, sw=1.6, rx=8))

    out_files = [
        "ε (0 біт)",
        "0 (1 біт)", "1 (1 біт)",
        "00 (2 біти)", "01 (2 біти) [колізія!]", "10 (2 біти)", "11 (2 біти)"
    ]
    out_y = [135, 168, 201, 234, 267, 300, 333]

    for j, (fn, y) in enumerate(zip(out_files, out_y)):
        is_col = (j == 4)
        col = POS if is_col else INK
        bg = REDFILL if is_col else ROW
        f.append(rect(550, y - 12, 220, 22, fill=bg, stroke=col, sw=1.2, rx=4))
        f.append(text(660, y + 3, f"Код {j+1}: «{fn}»", size=12, bold=is_col, color=col))

    f.append(line(310, 188, 550, 267, color=POS, sw=2.2, dash="5,3"))
    f.append(line(310, 300, 550, 267, color=POS, sw=2.2, dash="5,3"))
    f.append(circle(550, 267, 4, fill=POS, stroke=POS, sw=1))

    f.append(fitbox(W / 2, 370, 820, 34,
                    "За принципом Діріхле 8 вхідних файлів не можна ін'єктивно вкласти у 7 вихідних комірок.\n"
                    "Жоден алгоритм не здатний стиснути ВСІ файли без втрат: принаймні два файли матимуть однаковий код!",
                    size=12, fill=REDFILL, stroke=POS, sw=1.5, color=INK))

    render(os.path.join(IMG, "compression-tree.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pigeonhole_boxes()
    fig_prefix_sums_mod()
    fig_ramsey_r33()
    fig_compression_tree()
    print("Всі фігури згенеровано у ./img/")
