# -*- coding: utf-8 -*-
"""Фігури до вставки «Матрична форма контурного методу»
(book/electronics/analog/mesh-analysis/math-mesh-matrix.md).
Три фігури:
  matrix-build.svg   — як зі схеми-драбини виростає симетрична стрічкова матриця R
  symmetry.svg       — звідки симетрія: спільний опір кладе −R у ДВА рівняння однаково;
                       кероване джерело псує її, додаючи доданок лише в ОДНЕ рівняння
  loop-count.svg     — розмір системи = число незалежних контурів = b − n + 1
Запуск:  python figs-matrix.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── локальні символи ─────────────────────────────────────────────────────────
def node_dot(x, y, color=INK):
    return circle(x, y, 3.0, fill=color, stroke=color)


def resistor_h(x0, x1, y, label=None, above=True, color=INK, lab_color=None):
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 6
    out.append(line(x0, y, x0 + seg, y, color=color, sw=1.7))
    xx = x0 + seg
    prev = y
    for i in range(n):
        ny = y - amp if i % 2 == 0 else y + amp
        out.append(line(xx, prev, xx + seg, ny, color=color, sw=1.7))
        xx += seg
        prev = ny
    out.append(line(xx, prev, x1, y, color=color, sw=1.7))
    if label:
        ly = y - 13 if above else y + 19
        out.append(text((x0 + x1) / 2, ly, label, size=12,
                        color=lab_color or color, bold=True))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="right", color=INK, lab_color=None):
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    amp = 6
    out.append(line(x, y0, x, y0 + seg, color=color, sw=1.7))
    yy = y0 + seg
    prev = x
    for i in range(n):
        nx = x + amp if i % 2 == 0 else x - amp
        out.append(line(prev, yy, nx, yy + seg, color=color, sw=1.7))
        yy += seg
        prev = nx
    out.append(line(prev, yy, x, y1, color=color, sw=1.7))
    if label:
        lx = x + 14 if side == "right" else x - 14
        an = "start" if side == "right" else "end"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12,
                        color=lab_color or color, bold=True, anchor=an))
    return "".join(out)


def loop_arrow(cx, cy, r, color, label=None, cw=True, lab_dy=0):
    import math
    a0, a1 = (-50, 250) if cw else (250, -50)
    pts = []
    steps = 32
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    out = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.2" '
           'marker-end="url(#arrow)" opacity="0.9"/>' % (d, color)]
    if label:
        out.append(text(cx, cy + lab_dy + 5, label, size=14, color=color, bold=True))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. matrix-build.svg — драбина з 3 вікон → симетрична стрічкова матриця
# ════════════════════════════════════════════════════════════════════════════
def fig_matrix_build():
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 30, "Зі схеми-драбини виростає симетрична стрічкова матриця",
                  size=15, bold=True))

    # ── ліворуч: схема-драбина з трьох вікон ────────────────────────────────
    x0, x1, x2, x3 = 50, 140, 230, 320
    yT, yB = 95, 250
    # верх і низ
    f.append(resistor_h(x0 + 14, x1 - 14, yT, label="R₁"))
    f.append(resistor_h(x1 + 14, x2 - 14, yT, label="R₃"))
    f.append(resistor_h(x2 + 14, x3 - 14, yT, label="R₅"))
    f.append(line(x0, yB, x3, yB, color=INK, sw=1.7))
    # стики верх
    for (a, b) in [(x0, x0 + 14), (x1 - 14, x1), (x1, x1 + 14),
                   (x2 - 14, x2), (x2, x2 + 14), (x3 - 14, x3)]:
        f.append(line(a, yT, b, yT, color=INK, sw=1.7))
    # вертикалі: ліва — джерело (просто лінія+підпис), середні — спільні R₂,R₄, права — R₆
    f.append(line(x0, yT, x0, yB, color=INK, sw=1.7))
    f.append(text(x0 - 8, (yT + yB) / 2 + 4, "V", size=12, color=NEG, bold=True, anchor="end"))
    f.append(resistor_v(x1, yT + 8, yB - 8, label="R₂", side="right", color=POS))
    f.append(resistor_v(x2, yT + 8, yB - 8, label="R₄", side="right", color=POS))
    f.append(resistor_v(x3, yT + 8, yB - 8, label="R₆", side="left"))
    for (x, y) in [(x0, yT), (x1, yT), (x2, yT), (x3, yT),
                   (x0, yB), (x1, yB), (x2, yB), (x3, yB)]:
        f.append(node_dot(x, y))
    # контурні струми
    f.append(loop_arrow((x0 + x1) / 2, (yT + yB) / 2 + 4, 32, NEG, label="I₁", lab_dy=-4))
    f.append(loop_arrow((x1 + x2) / 2, (yT + yB) / 2 + 4, 32, FIELD, label="I₂", lab_dy=-4))
    f.append(loop_arrow((x2 + x3) / 2, (yT + yB) / 2 + 4, 32, MUTED, label="I₃", lab_dy=-4))
    f.append(text((x0 + x3) / 2, yB + 30, "три вікна → три невідомі", size=11, color=MUTED))
    f.append(text((x0 + x3) / 2, yB + 48, "спільні: R₂ (вікна 1·2), R₄ (вікна 2·3)",
                  size=10, color=POS))

    # ── праворуч: матриця R (3×3) ───────────────────────────────────────────
    mx, my = 430, 120
    cellw, cellh = 86, 46
    # рядки матриці
    rows = [
        ["R₁+R₂", "−R₂",      "0"],
        ["−R₂",   "R₂+R₃+R₄", "−R₄"],
        ["0",     "−R₄",      "R₄+R₅+R₆"],
    ]
    # кольори клітинок: діагональ — зелена рамка, позаосьові спільні — червона, нулі — сіра
    diag = FIELD
    offd = POS
    zero = MUTED
    for i in range(3):
        for j in range(3):
            cx = mx + j * cellw
            cy = my + i * cellh
            val = rows[i][j]
            if i == j:
                stk, col = diag, FIELD
            elif val == "0":
                stk, col = "#cfd6dd", MUTED
            else:
                stk, col = offd, POS
            fillc = "#eef7f0" if i == j else ("#fdecea" if val != "0" else "#f6f7f9")
            f.append(rect(cx, cy, cellw - 6, cellh - 6, fill=fillc, stroke=stk, sw=1.6, rx=6))
            f.append(text(cx + (cellw - 6) / 2, cy + (cellh - 6) / 2 + 4, val,
                          size=12, color=col, bold=True))
    # дужки матриці
    bx0 = mx - 8
    bx1 = mx + 3 * cellw - 6 + 8
    by0 = my - 6
    by1 = my + 3 * cellh - 6 + 6
    for bx in (bx0, bx1):
        tick = 9 if bx == bx0 else -9
        f.append(line(bx, by0, bx, by1, color=INK, sw=2.0))
        f.append(line(bx, by0, bx + tick, by0, color=INK, sw=2.0))
        f.append(line(bx, by1, bx + tick, by1, color=INK, sw=2.0))
    f.append(text(mx + 3 * cellw / 2 - 3, my - 16, "R  (симетрична: Rᵢⱼ = Rⱼᵢ)",
                  size=12, color=INK, bold=True))

    # підписи-пояснення під матрицею
    ly = my + 3 * cellh + 24
    f.append(rect(mx - 8, ly, 3 * cellw + 8, 70, fill=FILL, stroke=MUTED, sw=1.3, rx=8))
    f.append(text(mx + 6, ly + 22,
                  "діагональ Rᵢᵢ = сума опорів навколо контуру i",
                  size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(mx + 6, ly + 42,
                  "поза нею Rᵢⱼ = − (опір, спільний контурам i та j)",
                  size=11, color=POS, anchor="start", bold=True))
    f.append(text(mx + 6, ly + 60,
                  "0 — контури не дотикаються (не мають спільної гілки)",
                  size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "matrix-build.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. symmetry.svg — чому симетрія тримається й чим її ламає кероване джерело
# ════════════════════════════════════════════════════════════════════════════
def fig_symmetry():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 30, "Симетрія: спільна гілка діє на два рівняння однаково — "
                             "кероване джерело ні", size=14, bold=True))

    # ── ліва панель: чиста R — симетрично ───────────────────────────────────
    lx = 30
    f.append(rect(lx, 60, 320, 290, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(lx + 160, 86, "Лише опори → симетрично", size=13, color=FIELD, bold=True))

    # спільна гілка R_k між контуром i (зліва) та j (справа)
    xm = lx + 160
    yt, yb = 120, 240
    f.append(resistor_v(xm, yt, yb, label="Rₖ", side="left", color=POS))
    f.append(node_dot(xm, yt)); f.append(node_dot(xm, yb))
    f.append(loop_arrow(xm - 78, (yt + yb) / 2, 40, NEG, label="Iᵢ"))
    f.append(loop_arrow(xm + 78, (yt + yb) / 2, 40, FIELD, label="Iⱼ"))
    f.append(text(lx + 160, yb + 36, "спад на Rₖ = Rₖ·(Iᵢ − Iⱼ)", size=12, color=INK, bold=True))
    # два рядки-внески
    f.append(text(lx + 14, yb + 60, "у рівняння i:  … − Rₖ·Iⱼ …", size=11, color=NEG, anchor="start"))
    f.append(text(lx + 14, yb + 78, "у рівняння j:  … − Rₖ·Iᵢ …", size=11, color=FIELD, anchor="start"))
    f.append(text(lx + 160, yb + 96, "однаковий −Rₖ ⇒ Rᵢⱼ = Rⱼᵢ", size=11, color=POS, bold=True))

    # ── права панель: кероване джерело — асиметрія ──────────────────────────
    rx = 370
    f.append(rect(rx, 60, 320, 290, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    f.append(text(rx + 160, 86, "Кероване джерело → асиметрія", size=13, color=POS, bold=True))

    # джерело, кероване чужим струмом (ромб) у гілці контуру i
    xs = rx + 160
    yt2, yb2 = 120, 240
    # ромб-джерело
    cyd = (yt2 + yb2) / 2
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="#fff3e0" stroke="%s" stroke-width="2"/>' %
             (xs, yt2 + 18, xs + 20, cyd, xs, yb2 - 18, xs - 20, cyd, POS))
    f.append(line(xs, yt2, xs, yt2 + 18, color=INK, sw=1.7))
    f.append(line(xs, yb2 - 18, xs, yb2, color=INK, sw=1.7))
    f.append(node_dot(xs, yt2)); f.append(node_dot(xs, yb2))
    f.append(text(xs, cyd + 5, "g·Iⱼ", size=12, color=POS, bold=True))
    f.append(loop_arrow(xs - 78, cyd, 40, NEG, label="Iᵢ"))
    f.append(loop_arrow(xs + 78, cyd, 40, FIELD, label="Iⱼ"))
    f.append(text(rx + 160, yb2 + 36, "напруга залежить від ЧУЖОГО Iⱼ", size=11, color=INK, bold=True))
    f.append(text(rx + 14, yb2 + 60, "у рівняння i:  … + (g − Rₖ)·Iⱼ …", size=11, color=NEG, anchor="start"))
    f.append(text(rx + 14, yb2 + 78, "у рівняння j:  … − Rₖ·Iᵢ …",       size=11, color=FIELD, anchor="start"))
    f.append(text(rx + 160, yb2 + 96, "Rᵢⱼ ≠ Rⱼᵢ — симетрії немає", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "symmetry.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. loop-count.svg — розмір системи = b − n + 1 = число незалежних контурів
# ════════════════════════════════════════════════════════════════════════════
def fig_loop_count():
    W, H = 700, 350
    f = []
    f.append(text(W / 2, 30, "Скільки рівнянь? Стільки, скільки незалежних контурів: "
                             "L = b − n + 1", size=14, bold=True))

    # граф схеми: 2 вікна (як драбина), порахуємо гілки й вузли
    x0, x1, x2 = 90, 230, 370
    yT, yB = 110, 250
    # гілки (b): верх×2, низ×2, вертикалі×3  → 7? зробимо чітку драбину 2 вікон:
    # вузли: 4 верхні-нижні кути? намалюємо як 2 вікна → 6 вузлів, 7 гілок
    edges = [
        (x0, yT, x1, yT), (x1, yT, x2, yT),     # верх 2
        (x0, yB, x1, yB), (x1, yB, x2, yB),     # низ 2
        (x0, yT, x0, yB), (x1, yT, x1, yB), (x2, yT, x2, yB),  # вертикалі 3
    ]
    for (a, b, c, d) in edges:
        f.append(line(a, b, c, d, color=INK, sw=2.0))
    nodes = [(x0, yT), (x1, yT), (x2, yT), (x0, yB), (x1, yB), (x2, yB)]
    for (x, y) in nodes:
        f.append(node_dot(x, y, INK))
    # нумерація вузлів
    labs = ["1", "2", "3", "4", "5", "6"]
    offs = [(-12, -8), (0, -14), (12, -8), (-12, 18), (0, 22), (12, 18)]
    for (x, y), lb, (dx, dy) in zip(nodes, labs, offs):
        f.append(text(x + dx, y + dy, lb, size=11, color=NEG, bold=True))
    # два вікна-контури
    f.append(loop_arrow((x0 + x1) / 2, (yT + yB) / 2, 30, FIELD, label="I₁"))
    f.append(loop_arrow((x1 + x2) / 2, (yT + yB) / 2, 30, FIELD, label="I₂"))

    # підрахунок праворуч
    bx = 470
    f.append(rect(bx, 70, 210, 210, fill=FILL, stroke=MUTED, sw=1.5, rx=10))
    lines = [
        ("гілок  b = 7", INK, False),
        ("вузлів  n = 6", INK, False),
        ("", INK, False),
        ("L = b − n + 1", NEG, True),
        ("L = 7 − 6 + 1 = 2", FIELD, True),
        ("", INK, False),
        ("⇒ рівно 2 рівняння,", INK, False),
        ("    2 контурні струми,", INK, False),
        ("    матриця R — 2×2", POS, True),
    ]
    yy = 96
    for txt, col, b in lines:
        f.append(text(bx + 16, yy, txt, size=12, color=col, anchor="start", bold=b))
        yy += 22

    f.append(text((x0 + x2) / 2, yB + 40,
                  "для плоскої схеми L = число «вікон» (обмежених граней)",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "loop-count.svg"), W, H, *f)


if __name__ == "__main__":
    fig_matrix_build()
    fig_symmetry()
    fig_loop_count()
    print("OK: 3 фігури у", IMG)
