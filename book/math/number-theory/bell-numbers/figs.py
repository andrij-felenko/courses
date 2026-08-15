# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def draw_curved_arrow(x1, y1, x2, y2, color=NEG, sw=1.5, dash="4,3"):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M {x1:.1f} {y1:.1f} C {x1+35:.1f} {y1:.1f}, {x2-35:.1f} {y2:.1f}, {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{sw:.1f}"{d} marker-end="url(#arrow)"/>')


# ── bell-triangle: трикутник Ейткена / трикутник Белла
def fig_bell_triangle():
    W, H = 820, 560
    p = []

    p.append(text(W / 2, 35, "Трикутник Ейткена (Трикутник Белла) для B₀ … B₅", size=15, bold=True))
    p.append(text(W / 2, 60, "Кожен рядок починається з останнього числа попереднього рядка", size=13, color=MUTED))

    rows = [
        [1],
        [1, 2],
        [2, 3, 5],
        [5, 7, 10, 15],
        [15, 20, 27, 37, 52]
    ]

    Y0 = 105
    DY = 70
    BOX_W = 65
    BOX_H = 46

    for r_idx, row in enumerate(rows):
        y = Y0 + r_idx * DY
        n_elems = len(row)
        total_row_w = n_elems * BOX_W + (n_elems - 1) * 18
        start_x = (W - total_row_w) / 2

        p.append(text(start_x - 55, y + 27, f"n = {r_idx}", size=13, bold=True, color=NEG, anchor="end"))

        for c_idx, val in enumerate(row):
            x = start_x + c_idx * (BOX_W + 18)

            is_bell = (c_idx == n_elems - 1)
            fill_col = "#dcfce7" if is_bell else "#f8fafc"
            stroke_col = FIELD if is_bell else LINE
            sw = 1.8 if is_bell else 1.2

            p.append(rect(x, y, BOX_W, BOX_H, fill=fill_col, stroke=stroke_col, sw=sw, rx=6))
            p.append(text(x + BOX_W / 2, y + 28, str(val), size=14, bold=True if is_bell else False))

            if is_bell:
                p.append(text(x + BOX_W / 2, y - 8, f"B{r_idx}", size=11, bold=True, color=FIELD))

    for r_idx in range(len(rows) - 1):
        y_from = Y0 + r_idx * DY + BOX_H / 2
        y_to = Y0 + (r_idx + 1) * DY + BOX_H / 2

        n_from = len(rows[r_idx])
        w_from = n_from * BOX_W + (n_from - 1) * 18
        x_from = (W - w_from) / 2 + (n_from - 1) * (BOX_W + 18) + BOX_W

        n_to = len(rows[r_idx + 1])
        w_to = n_to * BOX_W + (n_to - 1) * 18
        x_to = (W - w_to) / 2

        p.append(draw_curved_arrow(x_from, y_from, x_to, y_to, color=NEG, sw=1.5, dash="4,3"))

    b, _, _ = textbox(W / 2, H - 40, [
        "Правило побудови: 1) A(n, 1) = A(n−1, n−1) — перенесення останнього елемента;",
        "2) A(n, k) = A(n, k−1) + A(n−1, k−1) — додавання лівого та верхньо-лівого сусідів.",
        "Правий край утворює послідовність чисел Белла: B₀=1, B₁=1, B₂=2, B₃=5, B₄=15, B₅=52."
    ], size=12.5, pad=10, fill="#fbfbfc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "bell-triangle.svg"), W, H, *p,
           title="Трикутник Ейткена для обчислення чисел Белла")


# ── set-partition-tree: дерево розбиттів 4-елементної множини
def fig_set_partition_tree():
    W, H = 840, 500
    p = []

    p.append(text(W / 2, 35, "Комбінаторне розбиття множини з n = 4 елементів: B₄ = 15", size=15, bold=True))
    p.append(text(W / 2, 60, "Класифікація розбиттів {1, 2, 3, 4} за кількістю блоків k (числа Стірлінга S(4, k))", size=13, color=MUTED))

    categories = [
        ("k = 1 блок\nS(4,1) = 1", [
            "{1, 2, 3, 4}"
        ], "#eff6ff", "#93c5fd"),
        ("k = 2 блоки\nS(4,2) = 7", [
            "{1} {2,3,4}", "{2} {1,3,4}",
            "{3} {1,2,4}", "{4} {1,2,3}",
            "{1,2} {3,4}", "{1,3} {2,4}",
            "{1,4} {2,3}"
        ], "#f0fdf4", "#86efac"),
        ("k = 3 блоки\nS(4,3) = 6", [
            "{1,2} {3} {4}", "{1,3} {2} {4}",
            "{1,4} {2} {3}", "{2,3} {1} {4}",
            "{2,4} {1} {3}", "{3,4} {1} {2}"
        ], "#fefce8", "#fde047"),
        ("k = 4 блоки\nS(4,4) = 1", [
            "{1} {2} {3} {4}"
        ], "#faf5ff", "#d8b4fe")
    ]

    X0 = 40
    COL_W = 175
    SPACING = 20
    Y0 = 100

    for i, (title_str, items, bg_color, border_color) in enumerate(categories):
        x = X0 + i * (COL_W + SPACING)

        lines = title_str.split("\n")
        p.append(rect(x, Y0, COL_W, 50, fill=bg_color, stroke=border_color, sw=1.5, rx=6))
        p.append(text(x + COL_W / 2, Y0 + 20, lines[0], size=13, bold=True))
        p.append(text(x + COL_W / 2, Y0 + 38, lines[1], size=12, color=MUTED))

        item_y0 = Y0 + 65
        for j, item in enumerate(items):
            iy = item_y0 + j * 36
            p.append(rect(x, iy, COL_W, 30, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
            p.append(text(x + COL_W / 2, iy + 19, item, size=12))

    b, _, _ = textbox(W / 2, H - 45, [
        "Загальне число розбиттів дорівнює сумі за всіма можливими кількостями блоків k:",
        "B₄ = S(4,1) + S(4,2) + S(4,3) + S(4,4) = 1 + 7 + 6 + 1 = 15 способів."
    ], size=13, pad=10, fill="#fbfbfc", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "set-partition-tree.svg"), W, H, *p,
           title="Розбиття множини з 4 елементів на блоки")


# ── modular-periodicity: порівняння Тушара та періодичність B_n mod p
def fig_modular_periodicity():
    W, H = 820, 480
    p = []

    p.append(text(W / 2, 35, "Періодичність чисел Белла за модулем p = 3", size=15, bold=True))
    p.append(text(W / 2, 60, "За порівнянням Тушара Bₙ₊₃ ≡ Bₙ₊₁ + Bₙ (mod 3), довжина періоду N₃ = 13", size=13, color=MUTED))

    mod_vals = [1, 1, 2, 2, 0, 1, 2, 1, 0, 0, 1, 0, 0, 1, 1, 2]

    X0 = 45
    CELL_W = 44
    CELL_H = 50
    Y0 = 120

    p.append(rect(X0 - 5, Y0 - 30, 13 * (CELL_W + 4) + 6, CELL_H + 50, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(X0 + 6.5 * CELL_W + 20, Y0 - 12, "Перший повний період (13 елементів)", size=13, bold=True, color=FIELD))

    p.append(rect(X0 + 13 * (CELL_W + 4) + 10, Y0 - 30, 3 * (CELL_W + 4) + 6, CELL_H + 50, fill="#eff6ff", stroke="#93c5fd", sw=1.8, rx=8))
    p.append(text(X0 + 14.5 * CELL_W + 25, Y0 - 12, "Новий період", size=13, bold=True, color=NEG))

    for n, val in enumerate(mod_vals):
        x = X0 + n * (CELL_W + 4)
        if n >= 13:
            x += 15

        p.append(text(x + CELL_W / 2, Y0 + 5, f"n={n}", size=11, color=MUTED))

        bg = "#ffffff"
        p.append(rect(x, Y0 + 15, CELL_W, CELL_H, fill=bg, stroke=LINE, sw=1.2, rx=4))
        p.append(text(x + CELL_W / 2, Y0 + 44, str(val), size=15, bold=True))

    Y_REC = 260
    p.append(rect(60, Y_REC, 700, 100, fill="#f8fafc", stroke=LINE, sw=1.3, rx=8))
    p.append(text(W / 2, Y_REC + 28, "Приклад обчислення за рекурентним порівнянням Тушара:", size=13, bold=True))

    eq_lines = [
        "B₅ ≡ B₃ + B₂ (mod 3)  ⇒  52 ≡ 5 + 2 ≡ 7 ≡ 1 (mod 3)",
        "B₆ ≡ B₄ + B₃ (mod 3)  ⇒  203 ≡ 15 + 5 ≡ 20 ≡ 2 (mod 3)"
    ]
    for i, eline in enumerate(eq_lines):
        p.append(text(W / 2, Y_REC + 55 + i * 26, eline, size=13, color=INK))

    b, _, _ = textbox(W / 2, H - 40, [
        "Теорема Радемахера-Левіна: період послідовності (Bₙ mod p) завжди є дільником (pᵖ − 1)/(p − 1).",
        "Для p = 2 період дорівнює 3 (1, 1, 0, 1, 1, 0...); для p = 3 період дорівнює 13; для p = 5 період дорівнює 781."
    ], size=12.5, pad=10, fill="#fbfbfc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "modular-periodicity.svg"), W, H, *p,
           title="Порівняння Тушара та періодичність чисел Белла за модулем 3")


if __name__ == "__main__":
    fig_bell_triangle()
    fig_set_partition_tree()
    fig_modular_periodicity()
    print("Figures generated successfully!")
