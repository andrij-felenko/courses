# -*- coding: utf-8 -*-
"""Фігури до статті «Послідовності Фарея».
Три SVG у ./img/:
  farey-tree.svg   — побудова послідовностей F1..F5 та вставка медіант
  ford-circles.svg — геометрія кіл Форда на відрізку [0, 1]
  farey-lattice.svg — ґраткова інтерпретація та детермінант Безу (площа трикутника)
"""
import sys
import os

# 4 рівні вгору від book/math/number-theory/farey-sequences до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. farey-tree.svg — побудова F1..F5 та виділення медіант
# ─────────────────────────────────────────────────────────────────────────────
def fig_farey_tree():
    W, H = 820, 420
    f = []

    f.append(text(W / 2, 28, "Побудова послідовностей Фарея від F₁ до F₅", size=17, color=INK, bold=True))
    f.append(text(W / 2, 48, "Кожен новий дріб утворюється як медіанта (a+c)/(b+d) двох сусідів з Fₙ₋₁", size=13, color=MUTED, italic=True))

    # Рівні F1..F5
    levels = [
        ("F₁", [(0, 1), (1, 1)]),
        ("F₂", [(0, 1), (1, 2), (1, 1)]),
        ("F₃", [(0, 1), (1, 3), (1, 2), (2, 3), (1, 1)]),
        ("F₄", [(0, 1), (1, 4), (1, 3), (1, 2), (2, 3), (3, 4), (1, 1)]),
        ("F₅", [(0, 1), (1, 5), (1, 4), (1, 3), (2, 5), (1, 2), (3, 5), (2, 3), (3, 4), (4, 5), (1, 1)])
    ]

    y_starts = [90, 160, 230, 300, 370]
    x_min, x_max = 100, 760

    for idx, (label, fracs) in enumerate(levels):
        y = y_starts[idx]
        # Позначка рівня
        f.append(text(50, y + 5, label, size=16, color=FIELD, bold=True))
        # Лінія відрізка [0, 1]
        f.append(line(x_min, y, x_max, y, color=LINE, sw=1.5))

        # Нанесення дробів
        for num, den in fracs:
            val = num / den
            x = x_min + val * (x_max - x_min)

            # Перевіряємо, чи цей дріб є новим на даному рівні
            is_new = (den == idx + 1) and (idx > 0)

            col = POS if is_new else INK
            r = 4.5 if is_new else 3.5

            f.append(circle(x, y, r, fill=col, stroke=col))

            # Підпис дробу (згори чи знизу, чергуємо для щільності)
            txt_y = y - 10 if is_new else y + 18
            f_str = f"{num}/{den}"
            f.append(text(x, txt_y, f_str, size=12 if not is_new else 13, color=col, bold=is_new))

            # Якщо це новий дріб, покажемо пунктирні стрілки-медіанти від батьків на вищому рівні
            if is_new:
                # Знайдемо батьків на попередньому рівні
                prev_fracs = levels[idx - 1][1]
                # Батьки — це найближчий ліворуч і праворуч дроби у prev_fracs
                left_parent = max(f for f in prev_fracs if f[0]/f[1] < val)
                right_parent = min(f for f in prev_fracs if f[0]/f[1] > val)

                x_lp = x_min + (left_parent[0]/left_parent[1]) * (x_max - x_min)
                x_rp = x_min + (right_parent[0]/right_parent[1]) * (x_max - x_min)
                y_prev = y_starts[idx - 1]

                # Стрілки від батьків
                f.append(line(x_lp, y_prev + 5, x, y - 6, color=POS, sw=1, dash="3,3"))
                f.append(line(x_rp, y_prev + 5, x, y - 6, color=POS, sw=1, dash="3,3"))

    render(os.path.join(IMG, "farey-tree.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. ford-circles.svg — геометрія кіл Форда
# ─────────────────────────────────────────────────────────────────────────────
def fig_ford_circles():
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 26, "Кола Форда для послідовності Фарея F₅", size=17, color=INK, bold=True))
    f.append(text(W / 2, 46, "Коло для p/q має радіус r = 1/(2q²) і торкається осі в точці p/q", size=13, color=MUTED, italic=True))

    y_base = 290
    x_min, x_max = 80, 740
    scale_y = 380.0  # масштаб для радіусів

    f.append(line(x_min - 20, y_base, x_max + 20, y_base, color=LINE, sw=2))

    # Дроби F5
    fracs_f5 = [(0, 1), (1, 5), (1, 4), (1, 3), (2, 5), (1, 2), (3, 5), (2, 3), (3, 4), (4, 5), (1, 1)]

    # Кольори за знаменником для наочності
    colors = {
        1: "#27ae60",
        2: "#2457d6",
        3: "#8e44ad",
        4: "#d35400",
        5: "#c0392b"
    }

    for num, den in fracs_f5:
        val = num / den
        x = x_min + val * (x_max - x_min)
        r = (1.0 / (2.0 * den * den)) * scale_y
        cy = y_base - r

        col = colors.get(den, INK)

        # Малюємо коло
        f.append(circle(x, cy, r, fill="none", stroke=col, sw=1.8))
        # Точка дотику з віссю
        f.append(circle(x, y_base, 2.5, fill=col, stroke=col))

        # Підпис дробу під віссю
        f.append(text(x, y_base + 18, f"{num}/{den}", size=12, color=col, bold=(den <= 2)))

    # Легенда кольорів за знаменниками
    f.append(text(W / 2, y_base + 45, "Знаменники: q=1 (зелений), q=2 (синій), q=3 (фіолетовий), q=4 (помаранчевий), q=5 (червоний)", size=12, color=MUTED))

    render(os.path.join(IMG, "ford-circles.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. farey-lattice.svg — ґраткова інтерпретація та детермінант Безу
# ─────────────────────────────────────────────────────────────────────────────
def fig_farey_lattice():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 26, "Ґраткова геометрія дробу: детермінант b·c − a·d = 1", size=17, color=INK, bold=True))
    f.append(text(W / 2, 46, "Вектори (b, a) та (d, c) утворюють фундаментальний паралелограм площею 1", size=13, color=MUTED, italic=True))

    ox, oy = 90, 350
    dx, dy = 115, 110  # масштаб сітки (x: знаменник b, y: чисельник a)

    # Сітка цілих точок
    for bx in range(0, 6):
        f.append(line(ox + bx * dx, oy - 0 * dy, ox + bx * dx, oy - 3 * dy, color="#e0e0e0", sw=1))
        f.append(text(ox + bx * dx, oy + 20, str(bx), size=12, color=MUTED))

    for ay in range(0, 4):
        f.append(line(ox + 0 * dx, oy - ay * dy, ox + 5 * dx, oy - ay * dy, color="#e0e0e0", sw=1))
        f.append(text(ox - 18, oy - ay * dy + 4, str(ay), size=12, color=MUTED))

    f.append(text(ox + 5.3 * dx, oy + 20, "знаменник (b)", size=12, color=INK, bold=True))
    f.append(text(ox - 18, oy - 3.3 * dy, "чисельник (a)", size=12, color=INK, bold=True))

    # Точка O=(0,0)
    # Сусідні дроби F3: 1/3 та 1/2  -> вектори (3, 1) та (2, 1)
    # Медіанта: (3+2, 1+1) = (5, 2) -> дріб 2/5 у F5
    P_orig = (ox, oy)
    P_13 = (ox + 3 * dx, oy - 1 * dy)  # дріб 1/3
    P_12 = (ox + 2 * dx, oy - 1 * dy)  # дріб 1/2
    P_25 = (ox + 5 * dx, oy - 2 * dy)  # дріб 2/5 (сума векторів)

    # Заливка трикутника/паралелограма
    poly_pts = f"{P_orig[0]},{P_orig[1]} {P_13[0]},{P_13[1]} {P_25[0]},{P_25[1]} {P_12[0]},{P_12[1]}"
    f.append(f'<polygon points="{poly_pts}" fill="#27ae60" fill-opacity="0.15" stroke="#27ae60" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Трикутник O, (3,1), (2,1)
    tri_pts = f"{P_orig[0]},{P_orig[1]} {P_13[0]},{P_13[1]} {P_12[0]},{P_12[1]}"
    f.append(f'<polygon points="{tri_pts}" fill="#c0392b" fill-opacity="0.2"/>')

    # Вектори
    f.append(arrow(P_orig[0], P_orig[1], P_13[0], P_13[1], color=NEG, sw=2.2))
    f.append(arrow(P_orig[0], P_orig[1], P_12[0], P_12[1], color=POS, sw=2.2))
    f.append(arrow(P_orig[0], P_orig[1], P_25[0], P_25[1], color=FIELD, sw=2.2))

    # Позначки точок
    f.append(circle(P_13[0], P_13[1], 5, fill=NEG, stroke=NEG))
    f.append(text(P_13[0] + 15, P_13[1] + 18, "(3, 1) ↔ 1/3", size=13, color=NEG, bold=True))

    f.append(circle(P_12[0], P_12[1], 5, fill=POS, stroke=POS))
    f.append(text(P_12[0] - 50, P_12[1] - 12, "(2, 1) ↔ 1/2", size=13, color=POS, bold=True))

    f.append(circle(P_25[0], P_25[1], 5, fill=FIELD, stroke=FIELD))
    f.append(text(P_25[0] + 15, P_25[1] - 10, "Медіанта: (5, 2) ↔ 2/5", size=13, color=FIELD, bold=True))

    # Пояснювальні тексти у вільній зоні зверху праворуч (біля x=500, y=85)
    f.append(text(460, 75, "Площа червоного трикутника = 1/2", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(460, 95, "Детермінант: 3·1 − 1·2 = 1", size=12, color=INK, anchor="start"))
    f.append(text(460, 113, "Усередині немає інших цілих точок", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "farey-lattice.svg"), W, H, *f)


if __name__ == "__main__":
    fig_farey_tree()
    fig_ford_circles()
    fig_farey_lattice()
    print("Фігури Farey успішно згенеровано!")
