# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: крива σ/√N ──────────────────────────────────────────────────────
# Залишковий шум як частка від початкового падає за законом 1/√N.
# Ідея, яку важко передати словами: спад НЕЛІНІЙНИЙ — різкий на перших
# відліках, далі майже горизонтальний; кожне наступне поліпшення дорожче.
def fig_sqrt_n_curve():
    W, H = 640, 420
    ox = 78           # x для N=1 (ліва межа поля)
    oy = 350          # y для рівня 0 (низ поля)
    axw = 500         # ширина поля побудови
    axh = 270         # висота поля (рівень 1.0 угорі)
    Nmax = 100

    def px(N):  return ox + (N - 1) / (Nmax - 1) * axw     # N ∈ [1..Nmax]
    def py(f):  return oy - f * axh                        # f ∈ [0..1]

    p = []

    # осі
    p.append(line(ox, py(0), ox + axw + 14, py(0), color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, py(0), ox + axw + 18, py(0), color=MUTED, sw=1.3))
    p.append(text(ox + axw + 24, py(0) + 4, "N", 13, MUTED, "start", italic=True))
    p.append(line(ox, py(0) + 4, ox, py(1.06), color=MUTED, sw=1.3))

    # позначки по осі y: 1, 1/2, 1/4, 1/10
    for f, lab in [(1.0, "σ"), (0.5, "σ/2"), (0.25, "σ/4"), (0.1, "σ/10")]:
        p.append(line(ox - 4, py(f), ox + 4, py(f), color=MUTED, sw=1))
        p.append(line(ox, py(f), ox + axw, py(f), color="#e5e7eb", sw=1, dash="3 4"))
        p.append(text(ox - 9, py(f) + 4, lab, 11, MUTED, "end"))

    # позначки по осі x: 1, 4, 16, 100
    for N in [1, 4, 16, 100]:
        p.append(line(px(N), py(0) - 4, px(N), py(0) + 4, color=MUTED, sw=1))
        p.append(text(px(N), py(0) + 18, str(N), 11, MUTED, "middle"))

    # крива 1/√N
    pts = []
    N = 1
    while N <= Nmax:
        pts.append("%.1f,%.1f" % (px(N), py(1.0 / math.sqrt(N))))
        N += 1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))

    # маркери на круглих N з підписами «у скільки разів чистіше»
    for N, note in [(4, "÷2"), (16, "÷4"), (100, "÷10")]:
        x, y = px(N), py(1.0 / math.sqrt(N))
        p.append(circle(x, y, 4.5, fill=NEG, stroke=NEG, sw=1))
        p.append(text(x, y - 12, note, 11.5, NEG, "middle", bold=True))

    # підпис кривої
    p.append(text(px(8) + 6, py(1.0 / math.sqrt(8)) - 16,
                  "σ / √N", 15, NEG, "start", bold=True))

    # рамка-висновок: учетверо більше відліків на кожен крок якості
    p.append(fitbox(ox + 175, py(0.74), 320, 46,
                    "учетверо більше відліків — лише вдвічі чистіше",
                    size=12.5, fill="#eaf0fd", stroke=NEG, color=INK, bold=False))

    p.append(text(W / 2, H - 10,
                  "Шум падає як корінь: різко спершу, далі дедалі повільніше.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "sqrt-n-curve.svg"), W, H, *p,
           title="Виграш усереднення: залишковий шум = σ/√N")


# ── Фігура 2: підлога зсуву ───────────────────────────────────────────────────
# Дві складові похибки під усередненням. Випадкова частина (σ/√N) падає до нуля;
# систематичний зсув b — горизонтальна лінія; сумарна похибка стелиться на b.
# Ідея: усереднення тисне лише випадкове; стале не зрушує — це межа методу.
def fig_bias_floor():
    W, H = 640, 420
    ox = 78
    oy = 350
    axw = 500
    axh = 270
    Nmax = 100
    sigma = 1.0       # початковий випадковий шум (умовні одиниці)
    bias = 0.30       # сталий зсув як частка від σ

    def px(N):  return ox + (N - 1) / (Nmax - 1) * axw
    def py(f):  return oy - f * axh

    p = []

    # осі
    p.append(line(ox, py(0), ox + axw + 14, py(0), color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, py(0), ox + axw + 18, py(0), color=MUTED, sw=1.3))
    p.append(text(ox + axw + 24, py(0) + 4, "N", 13, MUTED, "start", italic=True))
    p.append(line(ox, py(0) + 4, ox, py(1.06), color=MUTED, sw=1.3))

    # позначки осі x
    for N in [1, 4, 16, 100]:
        p.append(line(px(N), py(0) - 4, px(N), py(0) + 4, color=MUTED, sw=1))
        p.append(text(px(N), py(0) + 18, str(N), 11, MUTED, "middle"))
    # рівень σ і рівень зсуву по осі y
    p.append(line(ox - 4, py(1.0), ox + 4, py(1.0), color=MUTED, sw=1))
    p.append(text(ox - 9, py(1.0) + 4, "σ", 11, MUTED, "end"))
    p.append(line(ox - 4, py(bias), ox + 4, py(bias), color=MUTED, sw=1))
    p.append(text(ox - 9, py(bias) + 4, "b", 11, POS, "end", bold=True))

    # горизонтальна лінія зсуву b (не падає)
    p.append(line(ox, py(bias), ox + axw, py(bias), color=POS, sw=2.4, dash="8 4"))
    p.append(text(ox + axw - 4, py(bias) - 9,
                  "систематичний зсув b — не падає", 11.5, POS, "end", bold=True))

    # випадкова складова σ/√N (падає до нуля)
    rnd = []
    N = 1
    while N <= Nmax:
        rnd.append("%.1f,%.1f" % (px(N), py(sigma / math.sqrt(N))))
        N += 1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="5 4"/>' % (" ".join(rnd), NEG))
    p.append(text(px(9) + 6, py(sigma / math.sqrt(9)) + 16,
                  "випадкова: σ/√N → 0", 12, NEG, "start", bold=True))

    # сумарна похибка √(b² + (σ/√N)²) — стелиться на b
    tot = []
    N = 1
    while N <= Nmax:
        e = math.sqrt(bias * bias + (sigma / math.sqrt(N)) ** 2)
        tot.append("%.1f,%.1f" % (px(N), py(e)))
        N += 1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(tot), INK))
    p.append(text(px(40), py(math.sqrt(bias * bias + (sigma / math.sqrt(40)) ** 2)) - 12,
                  "повна похибка", 12, INK, "middle", bold=True))

    # стрілка: застигає на рівні b
    ax = px(88)
    p.append(arrow(ax, py(0.62), ax, py(bias) + 6, color=MUTED, sw=1.6))
    p.append(fitbox(px(58), py(0.86), 250, 44,
                    "далі не опуститься — застигає на b",
                    size=12, fill="#fdecea", stroke=POS, color=INK, bold=False))

    p.append(text(W / 2, H - 10,
                  "Усереднення прибирає тремтіння, та не зрушує сталого зсуву — це робота калібрування.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "bias-floor.svg"), W, H, *p,
           title="Межа усереднення: випадкове падає, зсув лишається")


if __name__ == "__main__":
    fig_sqrt_n_curve()
    fig_bias_floor()
    print("Done.")
