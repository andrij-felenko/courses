# -*- coding: utf-8 -*-
"""Фігури до теми «Каскад подвоєння періоду й стала Фейгенбаума».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ACC = "#8e44ad"   # фіолетовий акцент
MAIN = "#2457d6"  # синій
HIGHLIGHT = "#c0392b" # червоний
GREEN = "#27ae60" # зелений


def fig_bifurcation_cascade():
    W, H = 900, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дерево біфуркацій та масштабні коефіцієнти Фейгенбаума", size=16, bold=True))

    ox, oy = 80, 400
    w_axis = 760
    h_axis = 320

    f.append(arrow(ox, oy, ox + w_axis, oy, color=LINE, sw=1.8))
    f.append(text(ox + w_axis - 10, oy + 24, "Параметр r", size=13, bold=True, anchor="end"))

    f.append(arrow(ox, oy, ox, oy - h_axis, color=LINE, sw=1.8))
    f.append(text(ox - 14, oy - h_axis + 14, "Стан x", size=13, bold=True, anchor="start"))

    r0_x = ox + 40
    r1_x = ox + 220
    r2_x = ox + 480
    r3_x = ox + 580
    r_inf_x = ox + 630

    y_center = oy - h_axis / 2

    f.append(line(r0_x, y_center, r1_x, y_center, color=MAIN, sw=2.5))
    f.append(text((r0_x + r1_x) / 2, y_center - 12, "Період 1", size=12, color=MAIN, bold=True))

    d1 = 75
    path_p2_up = f"M {r1_x:.1f} {y_center:.1f} C {r1_x+80:.1f} {y_center:.1f}, {r2_x-40:.1f} {y_center-d1:.1f}, {r2_x:.1f} {y_center-d1:.1f}"
    path_p2_dn = f"M {r1_x:.1f} {y_center:.1f} C {r1_x+80:.1f} {y_center:.1f}, {r2_x-40:.1f} {y_center+d1:.1f}, {r2_x:.1f} {y_center+d1:.1f}"
    f.append(f'<path d="{path_p2_up}" fill="none" stroke="{MAIN}" stroke-width="2.2"/>')
    f.append(f'<path d="{path_p2_dn}" fill="none" stroke="{MAIN}" stroke-width="2.2"/>')
    f.append(text((r1_x + r2_x) / 2, y_center - d1 / 2 - 15, "Період 2", size=12, color=MAIN, bold=True))

    d2 = 30
    p4_1 = f"M {r2_x:.1f} {y_center-d1:.1f} C {r2_x+40:.1f} {y_center-d1:.1f}, {r3_x-20:.1f} {y_center-d1-d2:.1f}, {r3_x:.1f} {y_center-d1-d2:.1f}"
    p4_2 = f"M {r2_x:.1f} {y_center-d1:.1f} C {r2_x+40:.1f} {y_center-d1:.1f}, {r3_x-20:.1f} {y_center-d1+d2:.1f}, {r3_x:.1f} {y_center-d1+d2:.1f}"
    p4_3 = f"M {r2_x:.1f} {y_center+d1:.1f} C {r2_x+40:.1f} {y_center+d1:.1f}, {r3_x-20:.1f} {y_center+d1-d2:.1f}, {r3_x:.1f} {y_center+d1-d2:.1f}"
    p4_4 = f"M {r2_x:.1f} {y_center+d1:.1f} C {r2_x+40:.1f} {y_center+d1:.1f}, {r3_x-20:.1f} {y_center+d1+d2:.1f}, {r3_x:.1f} {y_center+d1+d2:.1f}"
    f.append(f'<path d="{p4_1}" fill="none" stroke="{MAIN}" stroke-width="2.0"/>')
    f.append(f'<path d="{p4_2}" fill="none" stroke="{MAIN}" stroke-width="2.0"/>')
    f.append(f'<path d="{p4_3}" fill="none" stroke="{MAIN}" stroke-width="2.0"/>')
    f.append(f'<path d="{p4_4}" fill="none" stroke="{MAIN}" stroke-width="2.0"/>')
    f.append(text((r2_x + r3_x) / 2, y_center - d1 - d2 - 12, "Період 4", size=11, color=MAIN, bold=True))

    for rx, label in [(r1_x, "r₁"), (r2_x, "r₂"), (r3_x, "r₃"), (r_inf_x, "r_∞")]:
        f.append(line(rx, oy - 10, rx, oy - h_axis + 40, color=MUTED, sw=1.2, dash="3,4"))
        f.append(circle(rx, oy, 3, fill=HIGHLIGHT, stroke=HIGHLIGHT, sw=1))
        f.append(text(rx, oy + 18, label, size=13, color=HIGHLIGHT, bold=True))

    f.append(rect(r_inf_x, oy - h_axis + 40, ox + w_axis - 40 - r_inf_x, h_axis - 50, fill="#fdecea", stroke="none", sw=0, rx=2))
    f.append(text(r_inf_x + 50, oy - h_axis + 60, "Область хаосу", size=12, color=HIGHLIGHT, bold=True))

    f.append(line(r1_x, oy - 25, r2_x, oy - 25, color=GREEN, sw=1.8))
    f.append(text((r1_x + r2_x) / 2, oy - 32, "Δr₁", size=12, color=GREEN, bold=True))

    f.append(line(r2_x, oy - 25, r3_x, oy - 25, color=GREEN, sw=1.8))
    f.append(text((r2_x + r3_x) / 2, oy - 32, "Δr₂", size=11, color=GREEN, bold=True))

    f.append(textbox(r1_x + 120, oy - h_axis + 65, "δ = lim (Δrₙ / Δrₙ₊₁) ≈ 4.6692", size=12.5, pad=8, fill="#eaf0fd", stroke=MAIN, sw=1.5, color=MAIN, bold=True)[0])

    b = textbox(W / 2, 452,
                "Гілки біфуркації подвоюються на кожному кроці, а інтервали Δr звужуються в δ ≈ 4.669 раза. Ширина вилок зменшується в α ≈ 2.503 раза",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(b)

    return render(os.path.join(IMG, "bifurcation-cascade.svg"), W, H, *f)


def fig_superstable_orbits():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Павутиння ітерацій та надстійкий цикл періоду 2", size=16, bold=True))

    ox, oy = 100, 400
    size = 320

    f.append(arrow(ox, oy, ox + size + 40, oy, color=LINE, sw=1.8))
    f.append(text(ox + size + 35, oy + 22, "xₙ", size=13, bold=True, anchor="end"))

    f.append(arrow(ox, oy, ox, oy - size - 30, color=LINE, sw=1.8))
    f.append(text(ox - 15, oy - size - 15, "xₙ₊₁", size=13, bold=True, anchor="start"))

    f.append(line(ox, oy, ox + size, oy - size, color=MUTED, sw=1.5, dash="4,4"))
    f.append(text(ox + size - 20, oy - size + 15, "y = x", size=11, color=MUTED, italic=True))

    pts = []
    for i in range(101):
        x_val = i / 100.0
        y_val = 3.236 * x_val * (1.0 - x_val)
        px = ox + x_val * size
        py = oy - y_val * size
        pts.append(f"{px:.1f},{py:.1f}")

    f.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{MAIN}" stroke-width="2.5"/>')
    f.append(text(ox + size / 2, oy - 3.236 * 0.25 * size - 14, "f(x) = r·x·(1−x)", size=12, color=MAIN, bold=True))

    apex_x = ox + 0.5 * size
    apex_y = oy - (3.236 * 0.25) * size
    f.append(circle(apex_x, apex_y, 4.5, fill=HIGHLIGHT, stroke=HIGHLIGHT, sw=1.5))
    f.append(text(apex_x, apex_y - 12, "f '(x*) = 0 (вершина)", size=11, color=HIGHLIGHT, bold=True))

    x1, y1 = 0.5, 3.236 * 0.25
    x2, y2 = y1, 3.236 * y1 * (1 - y1)

    p_a = (ox + x1 * size, oy - y1 * size)
    p_b = (ox + y1 * size, oy - y1 * size)
    p_c = (ox + y1 * size, oy - x1 * size)
    p_d = (ox + x1 * size, oy - x1 * size)

    cobweb = [
        f"{p_a[0]:.1f},{p_a[1]:.1f}",
        f"{p_b[0]:.1f},{p_b[1]:.1f}",
        f"{p_c[0]:.1f},{p_c[1]:.1f}",
        f"{p_d[0]:.1f},{p_d[1]:.1f}",
        f"{p_a[0]:.1f},{p_a[1]:.1f}"
    ]
    f.append(f'<polyline points="{" ".join(cobweb)}" fill="none" stroke="{GREEN}" stroke-width="2.2"/>')

    f.append(line(apex_x, oy - 5, apex_x, oy + 5, color=LINE, sw=1.5))
    f.append(text(apex_x, oy + 18, "x = 1/2", size=12, color=INK, bold=True))

    info_x = ox + size + 70
    f.append(textbox(info_x + 100, oy - size / 2 - 20,
                     "Умова надстійкості:\n"
                     "Для циклу {x₁, x₂}: (f²)'(x₁) = f '(x₁)·f '(x₂) = 0\n\n"
                     "Оскільки похідна в вершині f '(1/2) = 0,\n"
                     "цикл проходить точнісінько через максимум.\n"
                     "Це дає строгі реперні точки для розрахунку α.",
                     size=12, pad=10, fill="#f4f6f8", stroke=ACC, sw=1.5, color=INK)[0])

    b = textbox(W / 2, 452,
                "Павутиння ітерацій приходить у замкнений прямокутник. Дотик до максимуму f '(x*)=0 робить цикл надстійким",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(b)

    return render(os.path.join(IMG, "superstable-orbits.svg"), W, H, *f)


def fig_renormalization_self_similarity():
    W, H = 960, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Самоподібність та оператор перенормування Фейгенбаума", size=16, bold=True))

    w_p, h_p = 330, 290
    p1_x, p1_y = 40, 90
    p2_x, p2_y = 590, 90

    # Панель 1: Вихідне відображення f(x)
    f.append(rect(p1_x, p1_y, w_p, h_p, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p1_x + w_p / 2, p1_y + 24, "Вихідне відображення f(x)", size=13, bold=True, color=MAIN))

    c1_x = p1_x + w_p / 2
    c1_y = p1_y + h_p / 2 + 40

    f.append(line(p1_x + 20, c1_y, p1_x + w_p - 20, c1_y, color=MUTED, sw=1.2))
    f.append(line(c1_x, p1_y + 40, c1_x, p1_y + h_p - 20, color=MUTED, sw=1.2))
    f.append(text(p1_x + w_p - 25, c1_y + 16, "x", size=12, color=MUTED, italic=True))
    f.append(text(c1_x + 12, p1_y + 50, "y", size=12, color=MUTED, italic=True))

    pts1 = []
    for i in range(-50, 51):
        x_val = i / 50.0
        y_val = 1.0 - 1.2 * x_val**2
        px = c1_x + x_val * 110
        py = c1_y - y_val * 90
        pts1.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts1)}" fill="none" stroke="{MAIN}" stroke-width="2.4"/>')
    f.append(circle(c1_x, c1_y - 90, 4, fill=HIGHLIGHT, stroke=HIGHLIGHT, sw=1))
    f.append(text(c1_x, c1_y - 104, "g(0) = 1", size=11, color=HIGHLIGHT, bold=True))

    # Стрілка перенормування між панелями та невеликий підпис ПОНАД нею
    mid_x = (p1_x + w_p + p2_x) / 2
    arrow_y = p1_y + h_p / 2
    f.append(arrow(p1_x + w_p + 15, arrow_y, p2_x - 15, arrow_y, color=HIGHLIGHT, sw=2.5))
    f.append(text(mid_x, arrow_y - 15, "Оператор T:", size=12, color=HIGHLIGHT, bold=True))
    f.append(text(mid_x, arrow_y + 25, "f ↦ −α f(f(−x/α))", size=11.5, color=HIGHLIGHT, bold=True))

    # Панель 2: Перенормована функція T f(x)
    f.append(rect(p2_x, p2_y, w_p, h_p, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p2_x + w_p / 2, p2_y + 24, "Перенормована функція g(x)", size=13, bold=True, color=ACC))

    c2_x = p2_x + w_p / 2
    c2_y = p2_y + h_p / 2 + 40

    f.append(line(p2_x + 20, c2_y, p2_x + w_p - 20, c2_y, color=MUTED, sw=1.2))
    f.append(line(c2_x, p2_y + 40, c2_x, p2_y + h_p - 20, color=MUTED, sw=1.2))
    f.append(text(p2_x + w_p - 25, c2_y + 16, "x", size=12, color=MUTED, italic=True))
    f.append(text(c2_x + 12, p2_y + 50, "g(x)", size=12, color=MUTED, italic=True))

    pts2 = []
    for i in range(-50, 51):
        x_val = i / 50.0
        y_val = 1.0 - 1.5276 * x_val**2 + 0.1048 * x_val**4
        px = c2_x + x_val * 110
        py = c2_y - y_val * 90
        pts2.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts2)}" fill="none" stroke="{ACC}" stroke-width="2.4"/>')
    f.append(circle(c2_x, c2_y - 90, 4, fill=HIGHLIGHT, stroke=HIGHLIGHT, sw=1))
    f.append(text(c2_x, c2_y - 104, "g(x) — нерухома точка", size=11, color=ACC, bold=True))

    b = textbox(W / 2, 448,
                "Подвійне ітерування та масштабування по осі x в −α ≈ −2.503 раза зберігає вигляд профілю g(x) у вершині",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(b)

    return render(os.path.join(IMG, "renormalization-self-similarity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bifurcation_cascade()
    fig_superstable_orbits()
    fig_renormalization_self_similarity()
    print("Всі фігури згенеровано успішно.")
