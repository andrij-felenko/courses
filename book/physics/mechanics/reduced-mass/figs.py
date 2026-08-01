# -*- coding: utf-8 -*-
"""Фігури до теми «Зведена маса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, color, sw, d))


# ── Фігура 1: задача двох тіл зводиться до однієї частинки маси μ ──────────────
def fig_reduction():
    W, H = 920, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Задача двох тіл зводиться до руху однієї частинки маси μ",
                  size=17, bold=True))

    yb = 236.0                       # спільна лінія тіл
    dl = 360.0                       # розмірна лінія відстані r

    # ── ЛІВА панель: справжня пара навколо спільного центра мас ──
    f.append(text(235, 72, "справжня пара: обидва кружляють навколо центра мас",
                  size=13, color=MUTED))
    cmx = 235.0
    m1x, m2x = 180.0, 335.0          # важче тіло — ближче до центра мас
    # центр мас — зелена крапка з підписом ЗВЕРХУ
    f.append(text(cmx, 190, "центр мас", size=12, bold=True, color=FIELD))
    f.append(line(cmx, 202, cmx, yb - 10, color=MUTED, sw=0.8, dash="3 4"))
    f.append(circle(cmx, yb, 6, fill=FIELD, stroke=FIELD, sw=1))
    # тіла (важче — більший кружок)
    f.append(circle(m1x, yb, 27, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(m1x, yb + 6, "m₁", size=17, bold=True, color=NEG))
    f.append(circle(m2x, yb, 17, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(m2x, yb + 5, "m₂", size=14, bold=True, color=NEG))
    # розмірна лінія r (відстань між тілами) — унизу
    f.append(line(m1x, yb + 29, m1x, dl - 6, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(m2x, yb + 19, m2x, dl - 6, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(m1x, dl, m2x, dl, color=INK, sw=1.4))
    f.append(line(m1x, dl - 6, m1x, dl + 6, color=INK, sw=1.4))
    f.append(line(m2x, dl - 6, m2x, dl + 6, color=INK, sw=1.4))
    f.append(text((m1x + m2x) / 2, dl + 20, "r — відстань між тілами", size=12))

    # ── роздільник із розривом навколо знака «≡» ──
    f.append(line(462, 96, 462, 186, color=MUTED, sw=1.0, dash="4 6"))
    f.append(line(462, 252, 462, 366, color=MUTED, sw=1.0, dash="4 6"))
    f.append(text(462, 226, "≡", size=46, bold=True, color=INK))

    # ── ПРАВА панель: одна уявна частинка μ навколо нерухомого центра ──
    f.append(text(690, 72, "рівносильно: одне тіло μ навколо нерухомого центра",
                  size=13, color=MUTED))
    px, mux = 620.0, 775.0
    # нерухомий центр — зелена крапка з підписом ЗВЕРХУ
    f.append(text(px, 190, "нерухомий центр", size=12, bold=True, color=FIELD))
    f.append(line(px, 202, px, yb - 10, color=MUTED, sw=0.8, dash="3 4"))
    f.append(circle(px, yb, 6, fill=FIELD, stroke=FIELD, sw=1))
    # частинка μ
    f.append(circle(mux, yb, 21, fill="#eef6ef", stroke=FIELD, sw=2.2))
    f.append(text(mux, yb + 6, "μ", size=19, bold=True, color=FIELD))
    # сила взаємодії — червона стрілка від μ до центра
    f.append(arrow(mux - 26, yb - 34, mux - 96, yb - 34, color=POS, sw=2.4))
    f.append(text(mux - 61, yb - 44, "F", size=15, bold=True, color=POS))
    # розмірна лінія r
    f.append(line(px, yb + 12, px, dl - 6, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(mux, yb + 23, mux, dl - 6, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(px, dl, mux, dl, color=INK, sw=1.4))
    f.append(line(px, dl - 6, px, dl + 6, color=INK, sw=1.4))
    f.append(line(mux, dl - 6, mux, dl + 6, color=INK, sw=1.4))
    f.append(text((px + mux) / 2, dl + 20, "той самий r", size=12))

    b0, _, _ = textbox(W / 2, H - 26,
                       "μ = m₁·m₂ / (m₁ + m₂)   —   зведена маса пари",
                       size=15, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b0)
    return render(os.path.join(IMG, "two-body-to-one-body.svg"), W, H, *f)


# ── Фігура 2: μ як функція відношення мас (завжди менша за меншу масу) ─────────
def fig_curve():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Зведена маса завжди менша за меншу з двох мас",
                  size=17, bold=True))

    x0, x1 = 100.0, 730.0        # px для m₂/m₁ = 0 .. 10
    y0, y1 = 372.0, 92.0         # px для μ/m₁ = 0 .. 1
    XMAX = 10.0

    def PX(x):
        return x0 + (x / XMAX) * (x1 - x0)

    def PY(y):
        return y0 + y * (y1 - y0)

    # осі
    f.append(line(x0, y0, x1 + 8, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, x0, y1 - 8, color=INK, sw=1.6))
    f.append(text((x0 + x1) / 2, 410, "відношення мас   m₂ / m₁", size=13))
    f.append(text(x0, 74, "μ / m₁", size=13, bold=True))

    # горизонтальна асимптота μ = m₁ (менша маса)
    f.append(line(x0, PY(1.0), x1, PY(1.0), color=FIELD, sw=1.6, dash="6 6"))
    f.append(text(x1, PY(1.0) - 12, "стеля: μ = менша маса", size=12,
                  color=FIELD, anchor="end", bold=True))

    # позначки на осях
    for xv in (0, 1, 2, 5, 10):
        f.append(line(PX(xv), y0, PX(xv), y0 + 6, color=INK, sw=1.2))
        f.append(text(PX(xv), y0 + 22, str(xv), size=12, color=MUTED))
    for yv, lab in ((0.0, "0"), (0.5, "0.5 m₁"), (1.0, "m₁")):
        f.append(line(x0 - 6, PY(yv), x0, PY(yv), color=INK, sw=1.2))
        f.append(text(x0 - 12, PY(yv) + 4, lab, size=12, color=MUTED, anchor="end"))

    # дотична біля нуля: μ ≈ m₂ (нахил 1) + підпис у вільній зоні вгорі
    f.append(line(PX(0), PY(0), PX(1.0), PY(1.0), color=NEG, sw=1.4, dash="4 5"))
    f.append(line(156, 134, 205, 135, color=NEG, sw=0.9, dash="3 3"))
    f.append(text(210, 138, "μ ≈ m₂  (мала m₂)", size=12, color=NEG, anchor="start"))

    # крива μ/m₁ = x/(1+x)
    pts = []
    n = 120
    for i in range(n + 1):
        x = XMAX * i / n
        pts.append((PX(x), PY(x / (1.0 + x))))
    f.append(polyline(pts, color=INK, sw=2.8))

    # точка рівних мас (x=1, y=0.5) — підпис у вільній зоні під кривою
    ex, ey = PX(1.0), PY(0.5)
    f.append(line(ex, ey, 300, 316, color=MUTED, sw=0.9, dash="3 3"))
    f.append(circle(ex, ey, 6, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(306, 320, "рівні маси → μ = m/2", size=12,
                  color=POS, bold=True, anchor="start"))

    b0, _, _ = textbox(W / 2, H - 26,
                       "Хоч би яким важким було друге тіло, μ упирається в стелю — меншу масу пари.",
                       size=13, pad=10, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b0)
    return render(os.path.join(IMG, "reduced-mass-curve.svg"), W, H, *f)


# ── Фігура 3: мас-зважені осі — розклад енергії як теорема Піфагора ────────────
def fig_mass_weighted():
    import math
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Розклад кінетичної енергії — Піфагор у мас-зважених осях",
                  size=17, bold=True))

    ox, oy, s = 300.0, 300.0, 24.0          # початок координат і масштаб, px на одиницю
    m1, m2, v1, v2 = 2.0, 3.0, 6.0, 1.0     # ті самі числа, що в тексті
    M = m1 + m2
    mu = m1 * m2 / M
    u1, u2 = math.sqrt(m1) * v1, math.sqrt(m2) * v2
    e1 = (math.sqrt(m1 / M), math.sqrt(m2 / M))          # вісь центра мас
    e2 = (math.sqrt(mu / m1), -math.sqrt(mu / m2))       # вісь відстані

    def SX(x):
        return ox + x * s

    def SY(y):
        return oy - y * s

    def along(e, px):                        # точка на осі e за px пікселів від початку
        return (ox + px * e[0], oy - px * e[1])

    # ── вихідні мас-зважені осі ──
    f.append(arrow(250, oy, 830, oy, color=MUTED, sw=1.4))
    f.append(arrow(ox, oy, ox, 82, color=MUTED, sw=1.4))
    f.append(text(824, oy + 26, "u₁ = √m₁ · v₁", size=13, color=MUTED, anchor="end"))
    f.append(text(ox, 62, "u₂ = √m₂ · v₂", size=13, color=MUTED))

    # ── повернуті осі: центра мас (зелена) і відстані (червона) ──
    a1 = along(e1, 250)
    a2 = along(e2, 250)
    f.append(arrow(ox, oy, a1[0], a1[1], color=FIELD, sw=2.4))
    f.append(arrow(ox, oy, a2[0], a2[1], color=POS, sw=2.4))
    f.append(mtext(a1[0] + 14, a1[1] - 6, ["вісь центра мас", "проєкція = √M · V"],
                   size=13, color=FIELD, anchor="start", bold=True))
    f.append(mtext(a2[0] + 14, a2[1] - 4, ["вісь відстані", "проєкція = √μ · v"],
                   size=13, color=POS, anchor="start", bold=True))

    # прямий кут між новими осями
    k = 34.0
    c1 = along(e1, k)
    c2 = along(e2, k)
    cc = (ox + k * (e1[0] + e2[0]), oy - k * (e1[1] + e2[1]))
    f.append(polyline([c1, cc, c2], color=INK, sw=1.2))

    # ── сам вектор u та його проєкції ──
    ux, uy = SX(u1), SY(u2)
    p1 = u1 * e1[0] + u2 * e1[1]
    p2 = u1 * e2[0] + u2 * e2[1]
    f1 = along(e1, p1 * s)
    f2 = along(e2, p2 * s)
    f.append(line(ux, uy, f1[0], f1[1], color=MUTED, sw=1.0, dash="4 4"))
    f.append(line(ux, uy, f2[0], f2[1], color=MUTED, sw=1.0, dash="4 4"))
    f.append(line(ox, oy, ux, uy, color=INK, sw=2.6))
    f.append(circle(f1[0], f1[1], 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(circle(f2[0], f2[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(circle(ux, uy, 7, fill=INK, stroke=INK, sw=1))
    f.append(text(ux + 14, uy - 12, "u = (√m₁·v₁ , √m₂·v₂)", size=13,
                  color=INK, anchor="start", bold=True))

    b0, _, _ = textbox(W / 2, 520,
                       "|u|² = (u·e₁)² + (u·e₂)² = M·V² + μ·v²   ⇒   T = ½·M·V² + ½·μ·v²",
                       size=15, pad=12, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b0)
    return render(os.path.join(IMG, "mass-weighted-rotation.svg"), W, H, *f)


# ── Фігура 4: замкнена й вільна частки повної кінетичної енергії ───────────────
def fig_energy_budget():
    W, H = 900, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Витратити на себе пара може лише другу дужку",
                  size=17, bold=True))

    x0, x1, yb, hb = 100.0, 800.0, 150.0, 66.0
    xs = x0 + (x1 - x0) * 22.5 / 37.5        # межа між частками

    f.append(rect(x0, yb, xs - x0, hb, fill="#eef2fb", stroke=NEG, sw=2, rx=4))
    f.append(text((x0 + xs) / 2, yb + 42, "½·M·V² = 22.5 Дж", size=17, bold=True, color=NEG))
    f.append(text((x0 + xs) / 2, yb - 22, "замкнено збереженням імпульсу",
                  size=13, color=MUTED))

    f.append(rect(xs, yb, x1 - xs, hb, fill="#eef6ef", stroke=FIELD, sw=2, rx=4))
    f.append(text((xs + x1) / 2, yb + 42, "½·μ·v² = 15.0 Дж", size=17, bold=True, color=FIELD))
    f.append(text((xs + x1) / 2, yb - 22, "усе, що пара витрачає на себе",
                  size=13, color=MUTED))

    yd = 250.0
    f.append(line(x0, yd, x1, yd, color=INK, sw=1.4))
    for xv in (x0, x1):
        f.append(line(xv, yd - 7, xv, yd + 7, color=INK, sw=1.4))
    f.append(line(x0, yb + hb + 6, x0, yd - 8, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(x1, yb + hb + 6, x1, yd - 8, color=MUTED, sw=0.8, dash="3 4"))
    f.append(text((x0 + x1) / 2, yd + 24, "повна кінетична енергія в лабораторії:  T = 37.5 Дж",
                  size=13))

    b0, _, _ = textbox(W / 2, 320,
                       "Абсолютно непружний удар: у тепло йде рівно ½·μ·v² — і ніяк не більше.",
                       size=14, pad=11, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b0)
    return render(os.path.join(IMG, "energy-budget-split.svg"), W, H, *f)


# ── Фігура 5: бюджет похибок числового досліду ────────────────────────────────
# Дані порахував two_body_vs_reduced (10 обертів Юпітера, швидкісний Верле,
# крок h = 1e-3 року): (час у роках, |r_чесна − r_зведена|, |r(h) − r(h/10)|), а.о.
BUDGET = [
    (1.70, 5.063e-15, 1.617e-07), (3.39, 2.402e-14, 3.919e-07),
    (5.08, 5.227e-14, 1.036e-06), (6.78, 6.823e-14, 1.951e-06),
    (8.47, 1.204e-13, 2.667e-06), (10.17, 2.685e-13, 2.932e-06),
    (11.87, 3.301e-13, 2.843e-06), (13.56, 2.474e-13, 2.694e-06),
    (15.26, 2.331e-13, 2.859e-06), (16.95, 4.335e-13, 3.556e-06),
    (18.64, 4.810e-13, 4.565e-06), (20.34, 3.033e-13, 5.391e-06),
    (22.04, 3.600e-13, 5.742e-06), (23.73, 5.832e-13, 5.685e-06),
    (25.43, 6.400e-13, 5.504e-06), (27.12, 4.308e-13, 5.584e-06),
    (28.82, 1.554e-13, 6.206e-06), (30.51, 1.672e-14, 7.223e-06),
    (32.20, 7.139e-14, 8.123e-06), (33.90, 1.376e-13, 8.553e-06),
    (35.59, 2.332e-13, 8.528e-06), (37.29, 6.044e-13, 8.315e-06),
    (38.98, 1.128e-12, 8.317e-06), (40.68, 1.613e-12, 8.871e-06),
    (42.38, 1.780e-12, 9.890e-06), (44.07, 1.667e-12, 1.086e-05),
    (45.77, 1.671e-12, 1.136e-05), (47.46, 2.076e-12, 1.137e-05),
    (49.16, 2.757e-12, 1.113e-05), (50.85, 3.491e-12, 1.105e-05),
    (52.55, 4.074e-12, 1.154e-05), (54.24, 4.395e-12, 1.256e-05),
    (55.94, 4.591e-12, 1.359e-05), (57.63, 4.902e-12, 1.418e-05),
    (59.33, 5.521e-12, 1.421e-05), (61.02, 6.367e-12, 1.394e-05),
    (62.72, 7.379e-12, 1.379e-05), (64.41, 8.283e-12, 1.421e-05),
    (66.11, 8.696e-12, 1.523e-05), (67.80, 8.799e-12, 1.633e-05),
    (69.50, 9.015e-12, 1.699e-05), (71.19, 9.671e-12, 1.706e-05),
    (72.89, 1.079e-11, 1.675e-05), (74.58, 1.210e-11, 1.652e-05),
    (76.28, 1.309e-11, 1.688e-05), (77.97, 1.335e-11, 1.790e-05),
    (79.67, 1.300e-11, 1.907e-05), (81.36, 1.268e-11, 1.980e-05),
    (83.06, 1.292e-11, 1.990e-05), (84.75, 1.376e-11, 1.956e-05),
    (86.45, 1.481e-11, 1.926e-05), (88.14, 1.531e-11, 1.956e-05),
    (89.84, 1.482e-11, 2.058e-05), (91.53, 1.383e-11, 2.180e-05),
    (93.23, 1.315e-11, 2.261e-05), (94.92, 1.323e-11, 2.274e-05),
    (96.62, 1.401e-11, 2.237e-05), (98.31, 1.469e-11, 2.200e-05),
    (100.00, 1.464e-11, 2.223e-05), (101.70, 1.356e-11, 2.325e-05),
    (103.39, 1.220e-11, 2.454e-05), (105.09, 1.146e-11, 2.542e-05),
    (106.78, 1.162e-11, 2.558e-05), (108.48, 1.234e-11, 2.518e-05),
    (110.17, 1.297e-11, 2.473e-05), (111.87, 1.284e-11, 2.490e-05),
    (113.56, 1.182e-11, 2.592e-05), (115.26, 1.061e-11, 2.728e-05),
    (116.95, 1.012e-11, 2.823e-05), (118.65, 1.022e-11, 2.843e-05),
]


def fig_error_budget():
    import math
    W, H = 1000, 505
    X0, X1, Y0, Y1 = 110.0, 690.0, 78.0, 388.0
    LO, HI, TMAX = -16.0, -3.0, 120.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    def PX(t):
        return X0 + t / TMAX * (X1 - X0)

    def PY(v):
        return Y1 - (math.log10(v) - LO) / (HI - LO) * (Y1 - Y0)

    f.append(text(X0, 58, "відхилення |Δr| в астрономічних одиницях, шкала логарифмічна",
                  size=12, color=MUTED, anchor="start"))

    # сітка по декадах і осі
    for d, lab in ((-15, "10⁻¹⁵"), (-12, "10⁻¹²"), (-9, "10⁻⁹"), (-6, "10⁻⁶"), (-3, "10⁻³")):
        y = PY(10.0 ** d)
        f.append(line(X0, y, X1, y, color=MUTED, sw=0.7, dash="3 6"))
        f.append(text(X0 - 10, y + 4, lab, size=12, color=MUTED, anchor="end"))
    f.append(line(X0, Y1, X1, Y1, color=INK, sw=1.6))
    f.append(line(X0, Y1, X0, Y0 - 4, color=INK, sw=1.6))
    for tv in (0, 20, 40, 60, 80, 100, 120):
        f.append(line(PX(tv), Y1, PX(tv), Y1 + 6, color=INK, sw=1.2))
        f.append(text(PX(tv), Y1 + 24, str(tv), size=12, color=MUTED))
    f.append(text((X0 + X1) / 2, Y1 + 52,
                  "час, роки   (один оберт Юпітера ≈ 11.87 року)", size=13))

    # криві
    f.append(polyline([(PX(t), PY(ds)) for t, _, ds in BUDGET], color=POS, sw=2.6))
    f.append(polyline([(PX(t), PY(dr)) for t, dr, _ in BUDGET], color=NEG, sw=2.6))

    # прямі підписи праворуч, навпроти кінців кривих
    y_up, y_dn = PY(BUDGET[-1][2]), PY(BUDGET[-1][1])
    b1, w1, _ = textbox(845, y_up, "власна похибка кроку — 4 300 км",
                        size=13, pad=9, fill="#fdecea", stroke=POS, sw=1.6, color=POS)
    f.append(line(X1 + 3, y_up, 845 - w1 / 2 - 4, y_up, color=POS, sw=1.0, dash="3 3"))
    f.append(b1)
    b2, w2, _ = textbox(845, y_dn, "розбіжність двох способів — 1.5 м",
                        size=13, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG)
    f.append(line(X1 + 3, y_dn, 845 - w2 / 2 - 4, y_dn, color=NEG, sw=1.0, dash="3 3"))
    f.append(b2)

    # подвійна стрілка через прірву між кривими, підпис — у правій колонці
    xg, ymid = PX(105), (y_up + y_dn) / 2
    f.append(arrow(xg, ymid, xg, PY(BUDGET[-5][2]) + 10, color=INK, sw=1.6))
    f.append(arrow(xg, ymid, xg, PY(BUDGET[-5][1]) - 10, color=INK, sw=1.6))
    b3, w3, _ = textbox(845, ymid, "прірва ≈ 3 000 000 разів", size=13, pad=9, sw=1.4)
    f.append(line(xg + 10, ymid, 845 - w3 / 2 - 4, ymid, color=MUTED, sw=0.9, dash="3 3"))
    f.append(b3)

    b0, _, _ = textbox(W / 2, H - 26,
                       "Зведення не додає до відповіді нічого свого: його слід тоне глибоко "
                       "під похибкою самого кроку.",
                       size=13, pad=10, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b0)
    return render(os.path.join(IMG, "reduction-error-budget.svg"), W, H, *f,
                  title="Чого вартий перехід до зведеної маси: бюджет похибок")


# ── Фігура (до вставки hist-deuterium): супутник лінії Hα за 1.79 Å ───────────
def fig_deuterium_lines():
    W, H = 900, 448
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Слід зведеної маси у спектрі: супутник лінії Hα",
                  size=17, bold=True))

    x0, x1 = 150.0, 800.0            # px для 6559.5 .. 6564.5 Å
    L0, L1 = 6559.5, 6564.5
    LH, LD = 6562.79, 6561.00

    def PX(lam):
        return x0 + (lam - L0) / (L1 - L0) * (x1 - x0)

    PLATE = "#23262b"                # «фотопластинка»
    BRIGHT = "#ffffff"
    HALO = "#4a5058"
    FAINT = "#767e8a"
    STRONG = "#dfe4ea"

    def strip(ytop, label, over, dline):
        """ytop — верх смужки; over — передержка; dline — колір лінії D або None."""
        f.append(text(x0, ytop - 12, label, size=13, color=MUTED, anchor="start"))
        f.append(rect(x0, ytop, x1 - x0, 46, fill=PLATE, stroke=MUTED, sw=1.0, rx=3))
        xh = PX(LH)
        if over:                     # передержана лінія розпливається в пляму
            f.append(line(xh, ytop + 5, xh, ytop + 41, color=HALO, sw=26))
            f.append(line(xh, ytop + 5, xh, ytop + 41, color=BRIGHT, sw=9))
        else:
            f.append(line(xh, ytop + 5, xh, ytop + 41, color=BRIGHT, sw=5))
        if dline:
            f.append(line(PX(LD), ytop + 5, PX(LD), ytop + 41,
                          color=dline, sw=3 if dline == STRONG else 2))

    strip(84, "звичайний водень, звичайна витримка: сама лінія H, і нічого поруч",
          False, None)
    strip(176, "той самий водень, витримка в тисячі разів довша: ледь помітний слід",
          True, FAINT)
    strip(268, "залишок рідкого водню, випареного біля потрійної точки: слід подужчав",
          True, STRONG)

    # ── унизу: де саме стоять обидві лінії і яка між ними відстань ──
    yb = 314.0
    f.append(line(PX(LD), yb, PX(LD), yb + 26, color=MUTED, sw=0.9, dash="3 4"))
    f.append(line(PX(LH), yb, PX(LH), yb + 26, color=MUTED, sw=0.9, dash="3 4"))
    f.append(text(PX(LD) - 12, yb + 20, "6561.0 Å   D", size=12,
                  color=NEG, anchor="end", bold=True))
    f.append(text(PX(LH) + 12, yb + 20, "H   6562.8 Å", size=12,
                  color=POS, anchor="start", bold=True))

    yl = yb + 34
    f.append(line(PX(LD), yl, PX(LH), yl, color=INK, sw=1.4))
    f.append(line(PX(LD), yl - 6, PX(LD), yl + 6, color=INK, sw=1.4))
    f.append(line(PX(LH), yl - 6, PX(LH), yl + 6, color=INK, sw=1.4))
    f.append(text((PX(LD) + PX(LH)) / 2, yl + 22, "Δλ = 1.79 Å", size=14, bold=True))

    b0, _, _ = textbox(W / 2, H - 26,
                       "Місце супутника задане наперед: 1.79 Å — це та сама зведена "
                       "маса, перекладена в довжину хвилі.",
                       size=13, pad=10, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b0)
    return render(os.path.join(IMG, "deuterium-line-shift.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_reduction(), fig_curve(), fig_mass_weighted(), fig_energy_budget(),
          fig_error_budget(), fig_deuterium_lines()]
    print("written:")
    for p in ps:
        print("  ", p)
