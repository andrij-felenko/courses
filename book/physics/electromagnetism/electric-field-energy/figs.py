# -*- coding: utf-8 -*-
"""Фігури до теми «Енергія електричного поля».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Локалізація енергії у плоскому конденсаторі ──────────────────
def fig_capacitor():
    W, H = 680, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Локалізація енергії в об'ємі між пластинами", size=16, bold=True))

    # Ліва і права пластини конденсатора
    x1, x2 = 180, 480
    y_top, y_bot = 60, 240
    plate_w = 16

    # Верхня/нижня пластини
    # Верхня пластина (+)
    f.append(rect(x1 - 20, y_top - plate_w, (x2 - x1) + 40, plate_w, fill="#fdecea", stroke=POS, sw=2, rx=4))
    for px in range(x1 + 10, x2, 35):
        f.append(plus(px, y_top - plate_w / 2, 6))
    f.append(text(x2 + 45, y_top - 6, "пластина (+Q)", size=13, bold=True, color=POS, anchor="start"))

    # Нижня пластина (−)
    f.append(rect(x1 - 20, y_bot, (x2 - x1) + 40, plate_w, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    for px in range(x1 + 10, x2, 35):
        f.append(minus(px, y_bot + plate_w / 2, 6))
    f.append(text(x2 + 45, y_bot + plate_w, "пластина (−Q)", size=13, bold=True, color=NEG, anchor="start"))

    # Об'єм поля (заливка)
    f.append(rect(x1, y_top, x2 - x1, y_bot - y_top, fill="#eefaf1", stroke=FIELD, sw=1.5, rx=0))

    # Силові лінії поля (зелені стрілки вниз), оминаючи центральний текстовий блок
    for lx in (205, 245, 415, 455):
        f.append(arrow(lx, y_top + 4, lx, y_bot - 4, color=FIELD, sw=1.8))

    # Позначка напруженості поля E
    f.append(text(x1 + 15, (y_top + y_bot) / 2, "E", size=18, bold=True, color=FIELD))

    # Позначки відстані d та площі S
    f.append(line(x1 - 35, y_top, x1 - 35, y_bot, color=LINE, sw=1.4))
    f.append(line(x1 - 42, y_top, x1 - 28, y_top, color=LINE, sw=1.4))
    f.append(line(x1 - 42, y_bot, x1 - 28, y_bot, color=LINE, sw=1.4))
    f.append(text(x1 - 50, (y_top + y_bot) / 2 + 4, "d", size=14, bold=True, color=INK, anchor="end"))

    # Текстовий блок усередині поля
    cx_mid = (x1 + x2) / 2
    cy_mid = (y_top + y_bot) / 2
    b1, w1, h1 = textbox(cx_mid, cy_mid, "об'ємна густина енергії:\nw_e = ½ ε₀ E²", size=13, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True)
    f.append(b1)

    # Підсумкові формули внизу
    b2, w2, h2 = textbox(W / 2, H - 28, "Повна енергія:  W = ∫ w_e dV = w_e · (S · d) = ½ C V²", size=13, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4, bold=True)
    f.append(b2)

    return render(os.path.join(IMG, "energy-density-capacitor.svg"), W, H, *f)


# ── Фігура 2: Розбіжність власної енергії точкового заряду ───────────────
def fig_self_energy():
    W, H = 680, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Розбіжність енергії поля точкового заряду при r₀ → 0", size=16, bold=True))

    # Сфера заряду радіуса r0
    cx, cy = 200, 160
    r0 = 36
    f.append(circle(cx, cy, r0, fill="#fdecea", stroke=POS, sw=2))
    f.append(plus(cx, cy, 14))
    f.append(text(cx, cy + 4, "q", size=14, bold=True, color=POS))
    f.append(line(cx, cy, cx + r0, cy, color=POS, sw=1.4, dash="2,2"))
    f.append(text(cx + r0 / 2, cy - 8, "r₀", size=12, bold=True, color=POS))

    # Радіальні лінії поля
    import math
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x_start = cx + (r0 + 4) * math.cos(rad)
        y_start = cy + (r0 + 4) * math.sin(rad)
        x_end = cx + 110 * math.cos(rad)
        y_end = cy + 110 * math.sin(rad)
        f.append(arrow(x_start, y_start, x_end, y_end, color=FIELD, sw=1.5))

    # Графік спадання w_e(r) ~ 1/r^4 праворуч
    gx0, gy0 = 380, 240
    gw, gh = 240, 160
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.6))  # вісь r
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.6))  # вісь w_e

    f.append(text(gx0 + gw + 12, gy0 + 4, "r", size=13, bold=True, color=INK))
    f.append(text(gx0 - 10, gy0 - gh - 8, "w_e", size=13, bold=True, color=INK, anchor="end"))

    # Крива w_e = C / r^4
    pts = []
    r_min = 25
    for px in range(r_min, gw - 10):
        r_val = px / 30.0
        w_val = 1.0 / (r_val ** 4)
        py = min(gh - 10, w_val * 15)
        pts.append((gx0 + px, gy0 - py))

    path_d = ["M %.1f,%.1f" % pts[0]]
    for px, py in pts[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), POS))

    # Пунктир радіуса r0 на графіку
    f.append(line(gx0 + r_min, gy0, gx0 + r_min, gy0 - gh + 15, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(gx0 + r_min, gy0 + 16, "r₀", size=12, bold=True, color=POS))

    # Заштрихована площа зафарбована
    b1, w1, h1 = textbox(gx0 + 120, gy0 - 110, "густина поля: w_e ∝ 1/r⁴\nпри r₀ → 0  інтеграл  W → ∞", size=12, pad=7, fill="#fff5f5", stroke=POS, sw=1.3, bold=True)
    f.append(b1)

    b2, w2, h2 = textbox(W / 2, H - 22, "Класична межа: точковий заряд мав би нескінченну власну енергію", size=12, pad=6, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "self-energy-divergence.svg"), W, H, *f)


# ── Фігура 3: Сила втягування діелектрика в поле ──────────────────────────
def fig_dielectric_force():
    W, H = 680, 300
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Пондеромоторна сила втягування діелектрика", size=16, bold=True))

    x1, x2 = 140, 520
    y_top, y_bot = 80, 200
    plate_w = 14

    # Заряди пластин
    f.append(rect(x1, y_top - plate_w, x2 - x1, plate_w, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append(rect(x1, y_bot, x2 - x1, plate_w, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(x1 - 15, y_top - 2, "+Q", size=13, bold=True, color=POS, anchor="end"))
    f.append(text(x1 - 15, y_bot + plate_w, "−Q", size=13, bold=True, color=NEG, anchor="end"))

    # Діелектричний блок, втягнутий на частину x
    x_slab_start = x1 - 60
    x_slab_end = x1 + 180
    f.append(rect(x_slab_start, y_top + 3, x_slab_end - x_slab_start, y_bot - y_top - 6, fill="#e8f4fc", stroke=NEG, sw=1.8, rx=4))
    f.append(text((x_slab_start + x1) / 2, (y_top + y_bot) / 2, "діелектрик\n(εᵣ > 1)", size=12, bold=True, color=NEG))

    # Стрілка сили F_x
    f.append(arrow(x_slab_end - 40, (y_top + y_bot) / 2, x_slab_end + 50, (y_top + y_bot) / 2, color=POS, sw=2.5))
    f.append(text(x_slab_end + 55, (y_top + y_bot) / 2 + 5, "F_x", size=16, bold=True, color=POS, anchor="start"))

    # Силові лінії у порожній та заповненій частинах
    for lx in range(x1 + 30, x_slab_end - 20, 45):
        f.append(arrow(lx, y_top + 4, lx, y_bot - 4, color=FIELD, sw=1.4))
    for lx in range(x_slab_end + 30, x2 - 20, 45):
        f.append(arrow(lx, y_top + 4, lx, y_bot - 4, color=FIELD, sw=1.8))

    # Крайове викривлення поля
    f.append(text((x_slab_end + x2) / 2, y_top + 30, "вакуум (ε₀)", size=12, color=MUTED))

    # Формула сили
    b1, w1, h1 = textbox(W / 2, H - 30, "Сила:  F_x = − (∂W / ∂x)_Q = ½ V² (dC / dx) > 0   (сила втягує блок)", size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b1)

    return render(os.path.join(IMG, "dielectric-force.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_capacitor()
    p2 = fig_self_energy()
    p3 = fig_dielectric_force()
    print("written SVG figures:")
    print("  ", p1)
    print("  ", p2)
    print("  ", p3)
