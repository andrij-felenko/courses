# -*- coding: utf-8 -*-
"""Фігури до статті «Математика надійності систем»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура: стеля кореляції — копії в одній зоні проти незалежних ─────────────
def fig_corr_floor():
    W, H = 720, 460
    p = []
    p.append(text(W / 2, 26, "Копії в ОДНІЙ зоні впираються в стелю β·u; у різних зонах — ні",
                  size=13, bold=True, color=MUTED))
    ox, ex, oy, ty = 92, 560, 392, 70

    def X(n): return ox + (ex - ox) * (n - 1) / 4.0
    def Y(v): return oy - (oy - ty) * v / 10.0

    for v in [0, 2, 4, 6, 8, 10]:
        yy = Y(v)
        p.append(line(ox, yy, ex, yy, color="#e5e7eb", sw=1.0))
        p.append(text(ox - 12, yy + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 26, ty - 20, "↑ дев'ятки доступності (−log₁₀ U)", size=11,
                  color=MUTED, anchor="start"))
    p.append(line(ox, ty, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ex, oy, color=INK, sw=1.6))
    for n in [1, 2, 3, 4, 5]:
        p.append(text(X(n), oy + 20, str(n), size=11, color=MUTED))
    p.append(text((ox + ex) / 2, oy + 42, "N — скільки надлишкових копій", size=12, color=INK))

    # незалежні (різні зони): nines = 2N  (бо u = 0.01 ⇒ uᴺ = 10^(−2N))
    ind = [(X(n), Y(2 * n)) for n in range(1, 6)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % pt for pt in ind), NEG))
    for pt in ind:
        p.append(circle(pt[0], pt[1], 4, fill=NEG, stroke=NEG, sw=1))

    # спільна зона (β-модель): U = β·u + ((1−β)·u)^N
    def nines_cm(N):
        U = 0.05 * 0.01 + (0.95 * 0.01) ** N
        return -math.log10(U)
    cm = [(X(n), Y(nines_cm(n))) for n in range(1, 6)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % pt for pt in cm), POS))
    for pt in cm:
        p.append(circle(pt[0], pt[1], 4, fill=POS, stroke=POS, sw=1))

    yf = Y(nines_cm(5))
    p.append(line(ox, yf, ex, yf, color=POS, sw=1.0, dash="5 4"))

    p.append(text(X(1.35), Y(9.4), "незалежні копії (різні зони):", size=11, color=NEG, anchor="start"))
    p.append(text(X(1.35), Y(8.8), "+2 дев'ятки на кожну копію", size=11, color=NEG, anchor="start"))
    p.append(text(X(2.3), Y(1.5), "одна зона (β = 0.05):", size=11, color=POS, anchor="start"))
    p.append(text(X(2.3), Y(0.9), "стеля ≈ 3.3 дев'ятки — далі копії марні", size=11, color=POS, anchor="start"))

    render(os.path.join(IMG, 'math-corr-floor.svg'), W, H, *p)


# ── Фігура: спектр «k з n» — від паралелі (k=1) до послідовності (k=n) ────────
def fig_k_of_n():
    W, H = 720, 460
    p = []
    p.append(text(W / 2, 26, "n = 5 копій, доступність за різних порогів «k з 5»",
                  size=14, bold=True, color=MUTED))
    ox, by, ty = 92, 350, 70

    def Y(v): return by - (by - ty) * v / 10.0

    for v in [0, 2, 4, 6, 8, 10]:
        yy = Y(v)
        p.append(line(ox, yy, 660, yy, color="#eef0f2", sw=1.0))
        p.append(text(ox - 12, yy + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 26, ty - 18, "↑ дев'ятки доступності", size=11, color=MUTED, anchor="start"))
    p.append(line(ox, ty, ox, by, color=INK, sw=1.6))
    p.append(line(ox, by, 660, by, color=INK, sw=1.6))

    nines = {1: 10.0, 2: 7.30, 3: 5.01, 4: 3.01, 5: 1.31}
    fills = {1: ("#eef7f0", FIELD), 2: ("#eef2ff", NEG), 3: ("#fff6e6", "#b8860b"),
             4: ("#eef2ff", NEG), 5: ("#fdecea", POS)}
    cx = {1: 150, 2: 262, 3: 374, 4: 486, 5: 598}
    for k in range(1, 6):
        v = nines[k]
        top = Y(v)
        f, s = fills[k]
        p.append(rect(cx[k] - 36, top, 72, by - top, fill=f, stroke=s, sw=1.4))
        p.append(text(cx[k], top - 8, ("%.1f" % v).rstrip('0').rstrip('.'), size=12, bold=True, color=INK))
        p.append(text(cx[k], by + 20, "k=%d" % k, size=12, bold=True, color=INK))

    p.append(text(cx[1], by + 40, "паралель", size=11, color=FIELD))
    p.append(text(cx[1], by + 56, "(будь-яка 1)", size=11, color=FIELD))
    p.append(text(cx[3], by + 40, "більшість", size=11, color="#b8860b"))
    p.append(text(cx[3], by + 56, "2f+1, f=2", size=11, color="#b8860b"))
    p.append(text(cx[5], by + 40, "послідовно", size=11, color=POS))
    p.append(text(cx[5], by + 56, "(усі 5)", size=11, color=POS))
    p.append(text(W / 2, 442, "поріг k росте — доступність падає; більшість (2f+1) — компроміс заради узгодженості",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'math-k-of-n.svg'), W, H, *p)


# ── Фігура: надлишок місткості N+k залежно від числа зон ──────────────────────
def fig_zone_overhead():
    W, H = 680, 400
    p = []
    p.append(text(W / 2, 26, "Пережити втрату однієї зони: більше зон — менший надлишок",
                  size=14, bold=True, color=MUTED))
    p.append(text(W / 2, 48, "надлишок місткості = 1/(Z−1);  кожна зона несе N/(Z−1)",
                  size=12, color=MUTED))
    by, ty = 300, 78

    def Y(pct): return by - (by - ty) * pct / 100.0

    p.append(line(70, by, 630, by, color=INK, sw=1.5))
    over = {2: 100, 3: 50, 4: 33, 5: 25}
    share = {2: "кожна: N", 3: "кожна: N/2", 4: "кожна: N/3", 5: "кожна: N/4"}
    fills = {2: ("#fdecea", POS), 3: ("#fff6e6", "#b8860b"), 4: ("#eef2ff", NEG), 5: ("#eef7f0", FIELD)}
    cx = {2: 150, 3: 290, 4: 430, 5: 570}
    for z in [2, 3, 4, 5]:
        pct = over[z]
        top = Y(pct)
        f, s = fills[z]
        p.append(rect(cx[z] - 46, top, 92, by - top, fill=f, stroke=s, sw=1.4))
        p.append(text(cx[z], top - 10, "+%d%%" % pct, size=13, bold=True, color=INK))
        p.append(text(cx[z], by + 22, ("%d зони" % z) if z < 5 else "5 зон", size=12, bold=True, color=INK))
        p.append(text(cx[z], by + 40, share[z], size=11, color=MUTED))
    p.append(text(W / 2, 380, "дві зони коштують удвічі; три — лише +50% за ту саму гарантію",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'math-zone-overhead.svg'), W, H, *p)


if __name__ == '__main__':
    fig_corr_floor()
    fig_k_of_n()
    fig_zone_overhead()
    print("done")
