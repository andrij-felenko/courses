# -*- coding: utf-8 -*-
"""Фігури до статті «Множина Кантора».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Fig 1: Ітеративна побудова триадної множини Кантора ────────────────────────
def fig_cantor_construction():
    W, H = 820, 480
    f = []

    PL, PW = 60, 620
    PT, PH = 60, 370
    max_level = 5

    def get_cantor_intervals(level):
        intervals = [(0.0, 1.0)]
        for _ in range(level):
            next_inv = []
            for a, b in intervals:
                third = (b - a) / 3.0
                next_inv.append((a, a + third))
                next_inv.append((b - third, b))
            intervals = next_inv
        return intervals

    row_h = 48
    bar_height = 18

    for lvl in range(max_level + 1):
        y_center = PT + lvl * row_h + 20
        y_top = y_center - bar_height / 2.0

        f.append(text(PL - 15, y_center + 4, "E%d" % lvl, size=13, bold=True, anchor="end", color=INK))
        f.append(line(PL, y_center, PL + PW, y_center, color="#e1e4e8", sw=0.8, dash="2,2"))

        intervals = get_cantor_intervals(lvl)
        for a, b in intervals:
            x1 = PL + a * PW
            w = (b - a) * PW
            col = "#0969da" if lvl < 5 else "#cf222e"
            f.append(rect(x1, y_top, max(w, 1.5), bar_height, fill=col, stroke="none", rx=2))

        num_intervals = 2 ** lvl
        measure_str = "(2/3)⁰ = 1" if lvl == 0 else "(2/3)^%d ≈ %.3f" % (lvl, (2.0/3.0)**lvl)
        info = "n = %d | міра: %s" % (num_intervals, measure_str)
        f.append(text(PL + PW + 15, y_center + 4, info, size=11, color=MUTED, anchor="start"))

    y_axis = PT + max_level * row_h + 45
    f.append(line(PL, y_axis, PL + PW, y_axis, color=INK, sw=1.2))
    ticks = [(0.0, "0"), (1/9, "1/9"), (2/9, "2/9"), (1/3, "1/3"), (1/2, "1/2"), (2/3, "2/3"), (7/9, "7/9"), (8/9, "8/9"), (1.0, "1")]
    for val, label in ticks:
        tx = PL + val * PW
        f.append(line(tx, y_axis, tx, y_axis + 6, color=INK, sw=1.0))
        f.append(text(tx, y_axis + 20, label, size=11, color=MUTED))

    f.append(text(PL + PW / 2, y_axis + 38, "Координата x на відрізку [0, 1]", size=12, bold=True))

    f.append(rect(PL, y_axis + 50, 14, 14, fill="#0969da", rx=2))
    f.append(text(PL + 22, y_axis + 62, "Залишок покриття Eₖ", size=11, color=MUTED, anchor="start"))
    f.append(rect(PL + 180, y_axis + 50, 14, 14, fill="#cf222e", rx=2))
    f.append(text(PL + 202, y_axis + 62, "Гранична множина C (Канторів пил)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "cantor-construction.svg"), W, H, *f, title="Ітеративна побудова триадної множини Кантора (E₀ ... E₅)")


# ── Fig 2: Перетин Пуанкаре та фрактальні шари у фазовому просторі ────────────
def fig_cantor_poincare_section():
    W, H = 820, 520
    f = []

    PL1, PW1 = 50, 340
    PT, PH = 60, 400

    f.append(rect(PL1, PT, PW1, PH, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))
    f.append(text(PL1 + PW1 / 2, PT + 24, "Фазовий простір та секуча Σ", size=13, bold=True))

    path_hs1 = []
    for i in range(100):
        t = i / 99.0
        x = PL1 + 40 + t * 260
        y = PT + 80 + 120 * math.sin(t * math.pi)
        path_hs1.append((x, y))

    path_hs2 = []
    for i in range(100):
        t = i / 99.0
        x = PL1 + 55 + t * 230
        y = PT + 105 + 100 * math.sin(t * math.pi)
        path_hs2.append((x, y))

    path_hs3 = []
    for i in range(100):
        t = i / 99.0
        x = PL1 + 70 + t * 200
        y = PT + 130 + 80 * math.sin(t * math.pi)
        path_hs3.append((x, y))

    def make_path_str(pts):
        return "M " + " L ".join(["%.1f,%.1f" % p for p in pts])

    f.append('<path d="%s" fill="none" stroke="#0969da" stroke-width="2.5" opacity="0.85"/>' % make_path_str(path_hs1))
    f.append('<path d="%s" fill="none" stroke="#0969da" stroke-width="1.8" opacity="0.75"/>' % make_path_str(path_hs2))
    f.append('<path d="%s" fill="none" stroke="#0969da" stroke-width="1.2" opacity="0.65"/>' % make_path_str(path_hs3))

    sec_x = PL1 + 180
    f.append(line(sec_x, PT + 40, sec_x, PT + PH - 30, color="#cf222e", sw=2.0, dash="5,3"))
    f.append(text(sec_x + 10, PT + 55, "Перетин Σ", size=12, color="#cf222e", bold=True))

    intersect_ys = [PT + 95, PT + 112, PT + 152, PT + 168, PT + 240, PT + 254, PT + 290, PT + 302]
    for iy in intersect_ys:
        f.append('<circle cx="%.1f" cy="%.1f" r="4.0" fill="#cf222e" stroke="#ffffff" stroke-width="1.2"/>' % (sec_x, iy))

    f.append(text(PL1 + PW1 / 2, PT + PH - 10, "Розтягування + стискання + складка", size=11, color=MUTED))

    PL2, PW2 = 440, 330
    f.append(rect(PL2, PT, PW2, PH, fill="#ffffff", stroke="#0969da", sw=1.5, rx=4))
    f.append(text(PL2 + PW2 / 2, PT + 24, "Трансверсальний зріз: Канторів пил", size=13, color="#0969da", bold=True))

    f.append(line(sec_x + 5, PT + 85, PL2, PT + 60, color="#cf222e", sw=0.8, dash="3,3"))
    f.append(line(sec_x + 5, PT + 310, PL2, PT + PH - 40, color="#cf222e", sw=0.8, dash="3,3"))

    f.append(line(PL2 + 60, PT + 60, PL2 + 60, PT + PH - 50, color=INK, sw=1.2))
    f.append(text(PL2 + 60, PT + 45, "Координата y", size=11, bold=True))

    def get_cantor_y_pts(y_min, y_max, depth):
        if depth == 0:
            return [(y_min, y_max)]
        h = (y_max - y_min) / 3.0
        left = get_cantor_y_pts(y_min, y_min + h, depth - 1)
        right = get_cantor_y_pts(y_max - h, y_max, depth - 1)
        return left + right

    cant_segments = get_cantor_y_pts(PT + 70, PT + PH - 60, 4)
    for y1, y2 in cant_segments:
        cy = (y1 + y2) / 2.0
        f.append(line(PL2 + 55, cy, PL2 + 65, cy, color="#cf222e", sw=2.0))
        f.append(line(PL2 + 80, cy, PL2 + 280, cy, color="#0969da", sw=1.0))

    f.append(text(PL2 + 180, PT + PH - 20, "Нескінченна кількість ізольованих шарів", size=11, color=MUTED))

    render(os.path.join(IMG, "cantor-poincare-section.svg"), W, H, *f, title="Формування Канторової структури у перетині Пуанкаре хаотичної системи")


# ── Fig 3: Диявольські сходи (функція Кантора) ────────────────────────────────
def fig_cantor_staircase():
    W, H = 820, 520
    f = []

    PL, PW = 80, 480
    PT, PH = 60, 380

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    def cantor_function(x, depth=8):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        if depth == 0: return x
        if x < 1/3.0:
            return 0.5 * cantor_function(3.0 * x, depth - 1)
        elif x > 2/3.0:
            return 0.5 + 0.5 * cantor_function(3.0 * x - 2.0, depth - 1)
        else:
            return 0.5

    y_ticks = [(0.0, "0"), (0.25, "1/4"), (0.5, "1/2"), (0.75, "3/4"), (1.0, "1")]
    for yv, ylbl in y_ticks:
        gy = PT + PH - yv * PH
        f.append(line(PL, gy, PL + PW, gy, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(PL - 12, gy + 4, ylbl, size=11, color=MUTED, anchor="end"))

    x_ticks = [(0.0, "0"), (1/9, "1/9"), (1/3, "1/3"), (1/2, "1/2"), (2/3, "2/3"), (8/9, "8/9"), (1.0, "1")]
    for xv, xlbl in x_ticks:
        gx = PL + xv * PW
        f.append(line(gx, PT, gx, PT + PH, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(gx, PT + PH + 18, xlbl, size=11, color=MUTED))

    pts = []
    num_pts = 600
    for i in range(num_pts + 1):
        x_val = i / float(num_pts)
        y_val = cantor_function(x_val, depth=7)
        px = PL + x_val * PW
        py = PT + PH - y_val * PH
        pts.append((px, py))

    path_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts])
    f.append('<path d="%s" fill="none" stroke="#0969da" stroke-width="2.5"/>' % path_str)

    p1_x1, p1_x2 = PL + (1/3.0) * PW, PL + (2/3.0) * PW
    p1_y = PT + PH - 0.5 * PH
    f.append(line(p1_x1, p1_y, p1_x2, p1_y, color="#cf222e", sw=3.5))

    p2_x1, p2_x2 = PL + (1/9.0) * PW, PL + (2/9.0) * PW
    p2_y = PT + PH - 0.25 * PH
    f.append(line(p2_x1, p2_y, p2_x2, p2_y, color="#cf222e", sw=3.0))

    p3_x1, p3_x2 = PL + (7/9.0) * PW, PL + (8/9.0) * PW
    p3_y = PT + PH - 0.75 * PH
    f.append(line(p3_x1, p3_y, p3_x2, p3_y, color="#cf222e", sw=3.0))

    f.append(text(PL + PW / 2, PT + PH + 40, "Аргумент x ∈ [0, 1]", size=12, bold=True))
    f.append(text(PL - 45, PT + PH / 2, "F(x)", size=12, bold=True, italic=True))

    PL3, PW3 = PL + PW + 30, 200
    f.append(rect(PL3, PT, PW3, PH, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=4))
    f.append(text(PL3 + PW3 / 2, PT + 24, "Властивості F(x)", size=13, bold=True))

    prop_texts = [
        "• Неперервна на [0, 1]",
        "• Монотонно неспадаюча",
        "• F(0) = 0, F(1) = 1",
        "• Похідна F'(x) = 0",
        "  майже скрізь (на вилучених",
        "  інтервалах міри 1)",
        "• Зростає ЛИШЕ на",
        "  множині Кантора C",
        "  міри 0!"
    ]
    for idx, pt in enumerate(prop_texts):
        col = "#cf222e" if "майже скрізь" in pt or "міри 0" in pt else INK
        f.append(text(PL3 + 12, PT + 60 + idx * 26, pt, size=11, color=col, anchor="start"))

    render(os.path.join(IMG, "cantor-staircase.svg"), W, H, *f, title="Функція Кантора («Диявольські сходи»)")


if __name__ == "__main__":
    fig_cantor_construction()
    fig_cantor_poincare_section()
    fig_cantor_staircase()
    print("Figures created successfully in ./img/")
