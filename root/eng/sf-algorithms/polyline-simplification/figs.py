# -*- coding: utf-8 -*-
"""Фігури до теми «Спрощення ламаної: Дуглас–Пекер і жадібні проходи»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def dot(x, y, r=4.0, c=INK):
    return circle(x, y, r, fill=c, stroke=c, sw=0.5)


def polyline_tag(pts, c=POS, sw=2.2, dash=None):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    extra = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, c, sw, extra))


def polygon_tag(pts, fill=FILL, stroke=LINE, sw=1.0):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw))


# ── 1. Кроки алгоритму Дугласа–Пекера (4 фази) ──────────────────────────────
def fig_douglas_peucker_steps():
    W, H = 840, 520
    frags = []

    panels = [
        ("1. Початкова хорда P₀P₇ та пошук d_max", 40, 40),
        ("2. Розбиття на дві підзадачі у точці P₃", 440, 40),
        ("3. Відсікання точок із відхиленням ≤ ε", 40, 280),
        ("4. Спрощена ламана (4 вершини з 8)", 440, 280),
    ]

    raw_pts = [
        (30, 160),
        (75, 110),
        (130, 140),
        (185, 55),
        (240, 95),
        (295, 40),
        (335, 120),
        (370, 150),
    ]

    for idx, (p_title, px, py) in enumerate(panels):
        frags.append(rect(px, py, 360, 210, fill="#fbfcfd", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(px + 180, py + 22, p_title, size=12, bold=True, color=INK))

        pts = [(px + x, py + y) for (x, y) in raw_pts]

        if idx == 0:
            frags.append(polyline_tag(pts, c="#94a3b8", sw=2.0))
            frags.append(line(pts[0][0], pts[0][1], pts[7][0], pts[7][1], color=NEG, sw=2.2))
            for i in range(1, 7):
                t = i / 7.0
                hx = pts[0][0] + t * (pts[7][0] - pts[0][0])
                hy = pts[0][1] + t * (pts[7][0] - pts[0][1])
                is_max = (i == 3)
                col = POS if is_max else "#64748b"
                dash = None if is_max else "3,3"
                sw = 2.0 if is_max else 1.0
                frags.append(line(pts[i][0], pts[i][1], hx, hy, color=col, sw=sw, dash=dash))
            
            frags.append(text(pts[3][0] + 8, pts[3][1] + 45, "d_max > ε", size=11, bold=True, color=POS, anchor="start"))

            for i, p in enumerate(pts):
                c_dot = POS if i == 3 else (NEG if i in (0, 7) else "#64748b")
                frags.append(dot(p[0], p[1], r=3.5, c=c_dot))
                lbl = "P%d" % i
                frags.append(text(p[0], p[1] - 8, lbl, size=10, bold=(i in (0, 3, 7)), color=INK))

        elif idx == 1:
            frags.append(polyline_tag(pts, c="#cbd5e1", sw=1.8))
            frags.append(line(pts[0][0], pts[0][1], pts[3][0], pts[3][1], color=NEG, sw=2.0))
            frags.append(line(pts[3][0], pts[3][1], pts[7][0], pts[7][1], color=NEG, sw=2.0))

            t_r = (5 - 3) / 4.0
            hx5 = pts[3][0] + t_r * (pts[7][0] - pts[3][0])
            hy5 = pts[3][1] + t_r * (pts[7][0] - pts[3][1])
            frags.append(line(pts[5][0], pts[5][1], hx5, hy5, color=POS, sw=2.0))
            frags.append(text(pts[5][0] + 8, pts[5][1] + 35, "d_max > ε", size=11, bold=True, color=POS, anchor="start"))

            for i, p in enumerate(pts):
                c_dot = POS if i in (3, 5) else (NEG if i in (0, 7) else "#64748b")
                frags.append(dot(p[0], p[1], r=3.5, c=c_dot))
                frags.append(text(p[0], p[1] - 8, "P%d" % i, size=10, bold=(i in (0, 3, 5, 7)), color=INK))

        elif idx == 2:
            frags.append(polyline_tag(pts, c="#e2e8f0", sw=1.5))
            frags.append(line(pts[0][0], pts[0][1], pts[3][0], pts[3][1], color=FIELD, sw=2.0))
            frags.append(line(pts[3][0], pts[3][1], pts[5][0], pts[5][1], color=FIELD, sw=2.0))
            frags.append(line(pts[5][0], pts[5][1], pts[7][0], pts[7][1], color=FIELD, sw=2.0))

            for i, p in enumerate(pts):
                if i in (1, 2, 4, 6):
                    frags.append(circle(p[0], p[1], r=4.0, fill="#ffffff", stroke="#94a3b8", sw=1.0))
                    frags.append(line(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3, color=POS, sw=1.2))
                    frags.append(line(p[0] - 3, p[1] + 3, p[0] + 3, p[1] - 3, color=POS, sw=1.2))
                    frags.append(text(p[0], p[1] + 16, "≤ ε", size=9, color="#64748b"))
                else:
                    frags.append(dot(p[0], p[1], r=4.0, c=FIELD))
                    frags.append(text(p[0], p[1] - 8, "P%d" % i, size=10, bold=True, color=FIELD))

        elif idx == 3:
            frags.append(polyline_tag(pts, c="#e2e8f0", sw=1.5, dash="3,3"))
            simp_pts = [pts[0], pts[3], pts[5], pts[7]]
            frags.append(polyline_tag(simp_pts, c=FIELD, sw=3.0))

            for i, p in enumerate(simp_pts):
                frags.append(dot(p[0], p[1], r=5.0, c=FIELD))
                orig_idx = [0, 3, 5, 7][i]
                frags.append(text(p[0], p[1] - 10, "P%d" % orig_idx, size=11, bold=True, color=INK))

            frags.append(text(px + 180, py + 195, "Збережено ключові екстремуми контуру", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'douglas-peucker-steps.svg'), W, H, *frags)


# ── 2. Геометрія відстані від точки до відрізка ──────────────────────────────
def fig_point_segment_distance():
    W, H = 800, 380
    frags = []

    AX, AY = 250, 220
    BX, BY = 550, 220

    frags.append(line(80, AY, AX, AY, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(line(BX, BY, 720, BY, color="#94a3b8", sw=1.2, dash="4,4"))

    frags.append(line(AX, AY, BX, BY, color=INK, sw=3.0))
    frags.append(dot(AX, AY, r=6.0, c=INK))
    frags.append(dot(BX, BY, r=6.0, c=INK))
    frags.append(text(AX, AY + 26, "A (t = 0)", size=14, bold=True, color=INK))
    frags.append(text(BX, BY + 26, "B (t = 1)", size=14, bold=True, color=INK))

    frags.append(arrow(AX + 40, AY - 12, BX - 40, BY - 12, color="#475569", sw=1.8))
    frags.append(text((AX + BX) / 2, AY - 22, "Вектор v = B − A", size=12, color="#475569", bold=True))

    P1X, P1Y = 160, 90
    frags.append(dot(P1X, P1Y, r=5.0, c=NEG))
    frags.append(text(P1X, P1Y - 12, "P₁ (t < 0)", size=13, bold=True, color=NEG))
    frags.append(line(P1X, P1Y, AX, AY, color=NEG, sw=2.0, dash="3,3"))
    frags.append(text(P1X - 25, (P1Y + AY) / 2, "dist = |P₁ − A|", size=11, bold=True, color=NEG, anchor="end"))

    frags.append(line(P1X, P1Y, P1X, AY, color="#cbd5e1", sw=1.0, dash="2,2"))
    frags.append(circle(P1X, AY, r=3.0, fill="#ffffff", stroke="#94a3b8", sw=1.0))
    frags.append(text(P1X, AY + 18, "H₁ (поза AB)", size=10, color="#64748b"))

    P2X, P2Y = 400, 70
    H2X, H2Y = 400, 220
    frags.append(dot(P2X, P2Y, r=5.0, c=POS))
    frags.append(text(P2X, P2Y - 12, "P₂ (0 ≤ t ≤ 1)", size=13, bold=True, color=POS))
    frags.append(line(P2X, P2Y, H2X, H2Y, color=POS, sw=2.2))
    frags.append(rect(H2X - 10, H2Y - 10, 10, 10, fill="none", stroke=POS, sw=1.2, rx=0))
    frags.append(dot(H2X, H2Y, r=4.0, c=POS))
    frags.append(text(P2X + 14, (P2Y + H2Y) / 2, "dist = |P₂ − H₂| (ортогональ)", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(H2X, H2Y + 26, "H₂ = A + t·v", size=11, bold=True, color=POS))

    P3X, P3Y = 640, 100
    frags.append(dot(P3X, P3Y, r=5.0, c=NEG))
    frags.append(text(P3X, P3Y - 12, "P₃ (t > 1)", size=13, bold=True, color=NEG))
    frags.append(line(P3X, P3Y, BX, BY, color=NEG, sw=2.0, dash="3,3"))
    frags.append(text(P3X + 25, (P3Y + BY) / 2, "dist = |P₃ − B|", size=11, bold=True, color=NEG, anchor="start"))

    frags.append(line(P3X, P3Y, P3X, BY, color="#cbd5e1", sw=1.0, dash="2,2"))
    frags.append(circle(P3X, BY, r=3.0, fill="#ffffff", stroke="#94a3b8", sw=1.0))
    frags.append(text(P3X, BY + 18, "H₃ (поза AB)", size=10, color="#64748b"))

    tb, _, _ = textbox(W / 2, 335,
                       "Формула параметра проекції: t = ((P − A) · (B − A)) / |B − A|²\n"
                       "Якщо t < 0: найближча точка A;  якщо t > 1: найближча точка B;  якщо 0 ≤ t ≤ 1: основа перпендикуляра H",
                       size=12, color=INK, pad=8)
    frags.append(tb)

    render(os.path.join(OUT, 'point-segment-distance.svg'), W, H, *frags)


# ── 3. Коридор алгоритму Роймана–Віткама (Reumann–Witkam) ────────────────────
def fig_reumann_witkam_strip():
    W, H = 820, 420
    frags = []

    pts = [
        (60, 240),   # p0
        (160, 220),  # p1
        (270, 230),  # p2 (всередині смуги 1)
        (380, 215),  # p3 (всередині смуги 1)
        (470, 130),  # p4 (ВИЙШЛА зі смуги 1 -> новий сектор)
        (570, 110),  # p5 (визначає напрям смуги 2)
        (680, 120),  # p6 (всередині смуги 2)
        (760, 150),  # p7 (всередині смуги 2)
    ]

    eps = 32.0
    c1_poly = [
        (pts[0][0] - 6, pts[0][1] - eps),
        (pts[4][0] + 30, pts[4][1] - 40 - eps),
        (pts[4][0] + 30, pts[4][1] - 40 + eps),
        (pts[0][0] - 6, pts[0][1] + eps),
    ]
    frags.append(polygon_tag(c1_poly, fill="#ecfdf5", stroke="#10b981", sw=1.2))
    frags.append(line(pts[0][0], pts[0][1], pts[4][0] + 25, pts[4][1] - 40, color="#10b981", sw=1.5, dash="4,4"))

    c2_poly = [
        (pts[4][0] - 6, pts[4][1] - eps),
        (pts[7][0] + 30, pts[7][1] - 20 - eps),
        (pts[7][0] + 30, pts[7][1] - 20 + eps),
        (pts[4][0] - 6, pts[4][1] + eps),
    ]
    frags.append(polygon_tag(c2_poly, fill="#eff6ff", stroke=NEG, sw=1.2))
    frags.append(line(pts[4][0], pts[4][1], pts[7][0] + 25, pts[7][1] - 20, color=NEG, sw=1.5, dash="4,4"))

    # Початкова ламана (сіра)
    frags.append(polyline_tag(pts, c="#94a3b8", sw=1.5))

    # Спрощена ламана (товста зелена p0 -> p4 -> p7)
    simp_pts = [pts[0], pts[4], pts[7]]
    frags.append(polyline_tag(simp_pts, c=FIELD, sw=3.0))

    # Написи коридорів — акуратно розміщені вгорі
    frags.append(text(200, 60, "Коридор пошуку 1 (ширина 2ε)", size=12, bold=True, color="#059669"))
    frags.append(arrow(200, 68, 200, 180, color="#059669", sw=1.4))

    frags.append(text(620, 45, "Новий коридор 2 (від p₄)", size=12, bold=True, color=NEG))
    frags.append(arrow(620, 53, 620, 85, color=NEG, sw=1.4))

    # Вершини та підписи
    for i, p in enumerate(pts):
        if i in (0, 7):
            frags.append(dot(p[0], p[1], r=5.5, c=FIELD))
            lbl = "p%d (збережено)" % i
            frags.append(text(p[0], p[1] + 24, lbl, size=11, bold=True, color=INK))
        elif i == 4:
            frags.append(dot(p[0], p[1], r=6.0, c=POS))
            frags.append(text(p[0] + 10, p[1] - 12, "p₄ (вихід за смугу, збережено)", size=11, bold=True, color=POS, anchor="start"))
        else:
            frags.append(circle(p[0], p[1], r=3.5, fill="#ffffff", stroke="#64748b", sw=1.2))
            frags.append(text(p[0], p[1] + 18, "p%d" % i, size=10, color="#64748b"))

    tb, _, _ = textbox(W / 2, 365,
                       "Потоковий алгоритм: перші 2 точки задають промінь та смугу ±ε. Усі проміжні точки всередині смуги (p₂, p₃) відкидаються.\n"
                       "Перша точка поза смугою (p₄) фіксує новий відрізок p₀–p₄ і стає початком наступного коридору за O(1) пам'яті.",
                       size=12, color=INK, pad=8)
    frags.append(tb)

    render(os.path.join(OUT, 'reumann-witkam-strip.svg'), W, H, *frags)


# ── 4. Метод ефективної площі Вісвалінгам–Вайатта ────────────────────────────
def fig_visvalingam_effective_area():
    W, H = 800, 400
    frags = []

    pts = [
        (80, 260),   # P0
        (200, 130),  # P1
        (350, 220),  # P2
        (500, 80),   # P3 (велика площа)
        (640, 240),  # P4
        (740, 180),  # P5
    ]

    t1_poly = [pts[0], pts[1], pts[2]]
    frags.append(polygon_tag(t1_poly, fill="#fef2f2", stroke=POS, sw=1.5))
    frags.append(text(190, 220, "Площа A₁", size=12, bold=True, color=POS))

    t2_poly = [pts[1], pts[2], pts[3]]
    frags.append(polygon_tag(t2_poly, fill="#e0e7ff", stroke=NEG, sw=1.8))
    frags.append(text(350, 150, "Площа A₂ (min)", size=12, bold=True, color=NEG))

    t3_poly = [pts[2], pts[3], pts[4]]
    frags.append(polygon_tag(t3_poly, fill="#ecfdf5", stroke=FIELD, sw=1.5))
    frags.append(text(510, 190, "Площа A₃ (max)", size=12, bold=True, color=FIELD))

    frags.append(polyline_tag(pts, c=INK, sw=2.5))

    frags.append(line(pts[1][0], pts[1][1], pts[3][0], pts[3][1], color=NEG, sw=2.0, dash="4,4"))
    frags.append(text((pts[1][0] + pts[3][0]) / 2 + 10, (pts[1][1] + pts[3][1]) / 2 - 14, "Новий сегмент P₁P₃", size=11, bold=True, color=NEG))

    for i, p in enumerate(pts):
        col = NEG if i == 2 else (POS if i == 1 else (FIELD if i == 3 else INK))
        frags.append(dot(p[0], p[1], r=5.0, c=col))
        lbl = "P%d" % i
        frags.append(text(p[0], p[1] - 12, lbl, size=12, bold=True, color=INK))

    tb, _, _ = textbox(W / 2, 340,
                       "Ефективна площа трикутника: A(Pᵢ) = ½ |(Pᵢ₋₁ − Pᵢ₊₁) × (Pᵢ − Pᵢ₊₁)|\n"
                       "Пріоритетна черга послідовно видаляє вершину з найменшою площею трикутника (P₂), з'єднуючи сусідів P₁ і P₃.\n"
                       "Це згладжує дрібний шум без утворення гострих неприродних зламів.",
                       size=12, color=INK, pad=8)
    frags.append(tb)

    render(os.path.join(OUT, 'visvalingam-effective-area.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_douglas_peucker_steps()
    fig_point_segment_distance()
    fig_reumann_witkam_strip()
    fig_visvalingam_effective_area()
    print("Успішно згенеровано 4 фігури в directory img/")
