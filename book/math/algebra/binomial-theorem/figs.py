# -*- coding: utf-8 -*-
"""Фігури для статті «Біноміальна теорема: від комбінаторного розкладу до нескінченних степеневих рядів».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os

# Шлях до scripts/ у корені репо (чотири рівні вгору від book/math/algebra/binomial-theorem)
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
# Фігура 1 — Дерево виборів для (a + b)³
# ─────────────────────────────────────────────────────────────────────────
def fig_combinatorial_tree():
    W, H = 820, 400
    p = []

    p.append(text(W/2, 26, "Дерево комбінаторних виборів при розкритті (a + b)³", size=16, bold=True))
    p.append(text(W/2, 46, "З кожної з 3 дужок обираємо доданок a або b; вибір k разів b дає доданок a³⁻ᵏ · bᵏ", size=12, color=MUTED, italic=True))

    # Корінь
    rx, ry = 80, 210
    p.append(rect(rx - 35, ry - 18, 70, 36, fill=GRAY_FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(rx, ry + 5, "(a + b)³", size=13, bold=True))

    # Дужка 1, 2, 3 колонки
    cols_x = [210, 370, 530]
    
    # 8 кінцевих результатів (у порядку зверху вниз)
    outcomes = [
        ("a", "a", "a", "aaa = a³", 0, ORANGE_FILL, POS),
        ("a", "a", "b", "aab = a²b", 1, BLUE_FILL, NEG),
        ("a", "b", "a", "aba = a²b", 1, BLUE_FILL, NEG),
        ("a", "b", "b", "abb = ab²", 2, PURPLE_FILL, INK),
        ("b", "a", "a", "baa = a²b", 1, BLUE_FILL, NEG),
        ("b", "a", "b", "bab = ab²", 2, PURPLE_FILL, INK),
        ("b", "b", "a", "bba = ab²", 2, PURPLE_FILL, INK),
        ("b", "b", "b", "bbb = b³", 3, GREEN_FILL, FIELD),
    ]

    y_positions = [80 + i * 38 for i in range(8)]

    # Малюємо гілки дерева
    # Рівень 1: 2 вузли
    y_l1 = [(y_positions[0] + y_positions[3])/2, (y_positions[4] + y_positions[7])/2]
    # Рівень 2: 4 вузли
    y_l2 = [
        (y_positions[0] + y_positions[1])/2, (y_positions[2] + y_positions[3])/2,
        (y_positions[4] + y_positions[5])/2, (y_positions[6] + y_positions[7])/2
    ]

    # Корінь -> Рівень 1
    p.append(line(rx + 35, ry, cols_x[0] - 25, y_l1[0], color=LINE, sw=1.5))
    p.append(text((rx + cols_x[0])/2 - 10, (ry + y_l1[0])/2 - 6, "a", size=12, bold=True, color=POS))
    p.append(line(rx + 35, ry, cols_x[0] - 25, y_l1[1], color=LINE, sw=1.5))
    p.append(text((rx + cols_x[0])/2 - 10, (ry + y_l1[1])/2 + 14, "b", size=12, bold=True, color=NEG))

    # Рівень 1 малювання вузлів
    for idx, (y_node, label) in enumerate(zip(y_l1, ["Дужка 1: a", "Дужка 1: b"])):
        clr = POS if idx == 0 else NEG
        f_clr = ORANGE_FILL if idx == 0 else BLUE_FILL
        p.append(rect(cols_x[0] - 30, y_node - 14, 60, 28, fill=f_clr, stroke=clr, sw=1.2, rx=4))
        p.append(text(cols_x[0], y_node + 4, "a" if idx == 0 else "b", size=12, bold=True, color=clr))

    # Рівень 1 -> Рівень 2
    l2_choices = ["a", "b", "a", "b"]
    for i in range(4):
        parent_y = y_l1[i // 2]
        target_y = y_l2[i]
        clr = POS if i % 2 == 0 else NEG
        p.append(line(cols_x[0] + 30, parent_y, cols_x[1] - 25, target_y, color=LINE, sw=1.2))
        p.append(text((cols_x[0] + cols_x[1])/2, (parent_y + target_y)/2 + (-4 if i % 2 == 0 else 10), l2_choices[i], size=11, bold=True, color=clr))

    # Рівень 2 малювання вузлів
    for i in range(4):
        clr = POS if i % 2 == 0 else NEG
        f_clr = ORANGE_FILL if i % 2 == 0 else BLUE_FILL
        p.append(rect(cols_x[1] - 25, y_l2[i] - 12, 50, 24, fill=f_clr, stroke=clr, sw=1.2, rx=4))
        p.append(text(cols_x[1], y_l2[i] + 4, l2_choices[i], size=12, bold=True, color=clr))

    # Рівень 2 -> Результати
    for i in range(8):
        parent_y = y_l2[i // 2]
        target_y = y_positions[i]
        clr = POS if i % 2 == 0 else NEG
        p.append(line(cols_x[1] + 25, parent_y, cols_x[2] - 25, target_y, color=LINE, sw=1.0))
        
        # Результат розкриття
        b_count = outcomes[i][4]
        res_text = outcomes[i][3]
        f_clr = outcomes[i][5]
        s_clr = outcomes[i][6]

        p.append(rect(cols_x[2] - 25, target_y - 12, 100, 24, fill=f_clr, stroke=s_clr, sw=1.2, rx=4))
        p.append(text(cols_x[2] + 25, target_y + 4, res_text, size=11, bold=True))

    # Підсумок справа (коефіцієнти C(3, k))
    x_sum = 680
    p.append(text(x_sum + 50, 68, "Згруповані коефіцієнти", size=13, bold=True))

    groups = [
        ("C(3, 0) = 1", "1 · a³", ORANGE_FILL, POS, 80),
        ("C(3, 1) = 3", "3 · a²b", BLUE_FILL, NEG, 140),
        ("C(3, 2) = 3", "3 · ab²", PURPLE_FILL, INK, 235),
        ("C(3, 3) = 1", "1 · b³", GREEN_FILL, FIELD, 346),
    ]

    for label_c, term_text, f_clr, s_clr, y_c in groups:
        p.append(rect(x_sum, y_c - 14, 110, 32, fill=f_clr, stroke=s_clr, sw=1.5, rx=6))
        p.append(text(x_sum + 55, y_c + 2, label_c, size=11, bold=True, color=s_clr))
        p.append(text(x_sum + 55, y_c + 14, term_text, size=10, italic=True))

    render(os.path.join(IMG, "combinatorial-tree.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — Трикутник Паскаля та рекурентність C(n,k) = C(n-1,k-1) + C(n-1,k)
# ─────────────────────────────────────────────────────────────────────────
def fig_pascal_triangle():
    W, H = 820, 380
    p = []

    p.append(text(W/2, 26, "Трикутник Паскаля та рекурентне правило додавання", size=16, bold=True))
    p.append(text(W/2, 46, "Кожне число дорівнює сумі двох чисел безпосередньо над ним: C(n, k) = C(n-1, k-1) + C(n-1, k)", size=12, color=MUTED, italic=True))

    # Значення трикутника Паскаля до n = 5
    triangle = [
        [1],
        [1, 1],
        [1, 2, 1],
        [1, 3, 3, 1],
        [1, 4, 6, 4, 1],
        [1, 5, 10, 10, 5, 1]
    ]

    y0 = 80
    row_h = 48
    cx = 360

    for n, row in enumerate(triangle):
        py = y0 + n * row_h
        k_count = len(row)
        step_x = 56
        start_x = cx - (k_count - 1) * step_x / 2

        # Позначка n зліва
        p.append(text(70, py + 5, f"n = {n}", size=13, bold=True, anchor="start", color=MUTED))

        for k, val in enumerate(row):
            px = start_x + k * step_x
            
            # Підсвічуємо додавання C(4, 1) + C(4, 2) = C(5, 2)
            if (n == 4 and k == 1) or (n == 4 and k == 2):
                f_clr = ORANGE_FILL
                s_clr = POS
                sw_v = 2.0
            elif n == 5 and k == 2:
                f_clr = GREEN_FILL
                s_clr = FIELD
                sw_v = 2.2
            else:
                f_clr = GRAY_FILL
                s_clr = LINE
                sw_v = 1.0

            p.append(rect(px - 22, py - 16, 44, 32, fill=f_clr, stroke=s_clr, sw=sw_v, rx=6))
            p.append(text(px, py + 4, str(val), size=13, bold=(n >= 4)))

    # Стрілки додавання від C(4,1)=4 та C(4,2)=6 до C(5,2)=10
    p.append(line(304, 288, 332, 304, color=POS, sw=2))
    p.append(line(360, 288, 332, 304, color=POS, sw=2))

    # Інформаційна панель справа
    px_info = 570
    py_info = 140
    p.append(rect(px_info, py_info, 220, 150, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(px_info + 110, py_info + 25, "Приклад рекурентності:", size=12, bold=True, color=NEG))
    p.append(text(px_info + 110, py_info + 55, "C(4, 1) + C(4, 2) = C(5, 2)", size=12, bold=True))
    p.append(text(px_info + 110, py_info + 80, "4  +  6  =  10", size=14, bold=True, color=FIELD))
    p.append(text(px_info + 110, py_info + 115, "Сума рядка n = 2ⁿ", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "pascal-triangle.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — Наближення функції √(1 + x) узагальненим біноміальним рядом
# ─────────────────────────────────────────────────────────────────────────
def fig_newton_series_convergence():
    W, H = 820, 400
    p = []

    p.append(text(W/2, 26, "Збіжність узагальненого біноміального ряду Ньютона для √(1 + x)", size=16, bold=True))
    p.append(text(W/2, 46, "Багаточлени Тейлора P₁(x), P₂(x), P₃(x) усе точніше наближають √(1 + x) в інтервалі |x| < 1", size=12, color=MUTED, italic=True))

    # Область графіку
    gx, gy = 100, 70
    gw, gh = 520, 260

    p.append(rect(gx, gy, gw, gh, fill=BG, stroke=LINE, sw=1.0))

    # Вісі координат
    x_zero = gx + gw / 2
    y_scale = gh / 1.3
    y_base = gy + gh - 40

    def to_svg(x_val, y_val):
        sx = x_zero + (x_val / 0.9) * (gw / 2)
        sy = y_base - (y_val - 0.4) * y_scale
        return sx, sy

    # Пунктирні лінії інтервалу
    sx_m1, _ = to_svg(-0.8, 0.4)
    sx_p1, _ = to_svg(0.8, 0.4)
    p.append(line(sx_m1, gy, sx_m1, gy + gh, color=MUTED, sw=1.0, dash="4 4"))
    p.append(line(sx_p1, gy, sx_p1, gy + gh, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(sx_m1 + 25, gy + 18, "x = -0.8", size=10, color=MUTED))
    p.append(text(sx_p1 - 25, gy + 18, "x = +0.8", size=10, color=MUTED))

    # Вісь X
    sx_start, sy_axis = to_svg(-0.85, 0.4)
    sx_end, _ = to_svg(0.85, 0.4)
    p.append(line(sx_start, sy_axis, sx_end, sy_axis, color=INK, sw=1.2))
    p.append(text(sx_end + 15, sy_axis + 4, "x", size=12, bold=True))

    # Вісь Y
    _, sy_top = to_svg(0, 1.45)
    _, sy_bot = to_svg(0, 0.35)
    p.append(line(x_zero, sy_bot, x_zero, sy_top, color=INK, sw=1.2))
    p.append(text(x_zero + 12, sy_top - 5, "y", size=12, bold=True))

    # Засічки на осі X
    for xv in [-0.5, 0.0, 0.5]:
        tx, ty = to_svg(xv, 0.4)
        p.append(line(tx, ty - 4, tx, ty + 4, color=INK, sw=1.0))
        p.append(text(tx, ty + 16, f"{xv}", size=10))

    # Побудова кривих
    import math
    steps = 40
    pts_exact = []
    pts_p1 = []
    pts_p2 = []
    pts_p3 = []

    for i in range(steps + 1):
        xv = -0.8 + (1.6 * i / steps)
        y_ex = math.sqrt(1 + xv)
        y_1 = 1 + 0.5 * xv
        y_2 = 1 + 0.5 * xv - 0.125 * (xv ** 2)
        y_3 = 1 + 0.5 * xv - 0.125 * (xv ** 2) + 0.0625 * (xv ** 3)

        pts_exact.append(to_svg(xv, y_ex))
        pts_p1.append(to_svg(xv, y_1))
        pts_p2.append(to_svg(xv, y_2))
        pts_p3.append(to_svg(xv, y_3))

    def make_path_d(pts):
        res = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
        for pt in pts[1:]:
            res.append(f"L {pt[0]:.1f},{pt[1]:.1f}")
        return " ".join(res)

    def path_elem(d_val, fill="none", stroke=LINE, sw=1.5, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<path d="{d_val}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

    p.append(path_elem(make_path_d(pts_exact), fill="none", stroke=POS, sw=3.0))
    p.append(path_elem(make_path_d(pts_p1), fill="none", stroke=NEG, sw=1.5, dash="6 3"))
    p.append(path_elem(make_path_d(pts_p2), fill="none", stroke=INK, sw=1.5, dash="3 3"))
    p.append(path_elem(make_path_d(pts_p3), fill="none", stroke=FIELD, sw=2.0))

    # Легенда праворуч
    lx = 640
    ly = 100
    p.append(rect(lx, ly, 160, 160, fill=GRAY_FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(lx + 80, ly + 22, "Легенда кривих", size=11, bold=True))

    items = [
        ("f(x) = √(1+x)", POS, "3.0", "none"),
        ("P₁(x) = 1 + x/2", NEG, "1.5", "6 3"),
        ("P₂(x) = P₁ - x²/8", INK, "1.5", "3 3"),
        ("P₃(x) = P₂ + x³/16", FIELD, "2.0", "none"),
    ]

    for idx, (lbl, clr, sw_str, d_str) in enumerate(items):
        iy = ly + 48 + idx * 28
        p.append(line(lx + 15, iy, lx + 45, iy, color=clr, sw=float(sw_str), dash=d_str if d_str != "none" else None))
        p.append(text(lx + 55, iy + 4, lbl, size=10, anchor="start", bold=(idx == 0)))

    render(os.path.join(IMG, "newton-series-convergence.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 4 — Властивість Фробеніуса у кільці характеристики p: (a + b)ᵖ ≡ aᵖ + bᵖ
# ─────────────────────────────────────────────────────────────────────────
def fig_frobenius_endomorphism():
    W, H = 820, 360
    p = []

    p.append(text(W/2, 26, "Ендоморфізм Фробеніуса у кільці характеристики p", size=16, bold=True))
    p.append(text(W/2, 46, "Усі проміжні біноміальні коефіцієнти C(p, k) діляться на p, тому проміжні члени зникають mod p", size=12, color=MUTED, italic=True))

    y0 = 90
    
    p.append(rect(60, y0, 700, 65, fill=GRAY_FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, y0 + 24, "Розклад у звичайній алгебрі для p = 5:", size=12, color=MUTED))
    p.append(text(410, y0 + 46, "(a + b)⁵ = a⁵  +  5·a⁴b  +  10·a³b²  +  10·a²b³  +  5·ab⁴  +  b⁵", size=14, bold=True))

    y_terms = y0 + 100
    terms_info = [
        ("a⁵", "Залишається", GREEN_FILL, FIELD, 120),
        ("5·a⁴b", "5 ≡ 0 (mod 5)", ORANGE_FILL, POS, 230),
        ("10·a³b²", "10 ≡ 0 (mod 5)", ORANGE_FILL, POS, 340),
        ("10·a²b³", "10 ≡ 0 (mod 5)", ORANGE_FILL, POS, 450),
        ("5·ab⁴", "5 ≡ 0 (mod 5)", ORANGE_FILL, POS, 560),
        ("b⁵", "Залишається", GREEN_FILL, FIELD, 670),
    ]

    for val_str, mod_note, f_clr, s_clr, tx in terms_info:
        p.append(rect(tx - 45, y_terms - 15, 90, 48, fill=f_clr, stroke=s_clr, sw=1.2, rx=6))
        p.append(text(tx, y_terms + 4, val_str, size=11, bold=True))
        p.append(text(tx, y_terms + 22, mod_note, size=9, color=s_clr if s_clr == POS else MUTED))

    y_res = y_terms + 75
    p.append(rect(160, y_res, 500, 56, fill=GREEN_FILL, stroke=FIELD, sw=2.0, rx=8))
    p.append(text(410, y_res + 23, "Результат у кільці характеристики p (модулярна алгебра):", size=11, color=MUTED))
    p.append(text(410, y_res + 44, "(a + b)ᵖ  ≡  aᵖ + bᵖ  (mod p)", size=16, bold=True, color=FIELD))

    render(os.path.join(IMG, "frobenius-endomorphism.svg"), W, H, *p)


if __name__ == "__main__":
    fig_combinatorial_tree()
    fig_pascal_triangle()
    fig_newton_series_convergence()
    fig_frobenius_endomorphism()
    print("Успішно згенеровано 4 фігури у ./img/")
