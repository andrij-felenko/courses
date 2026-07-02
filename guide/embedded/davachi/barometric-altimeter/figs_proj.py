# -*- coding: utf-8 -*-
"""Фігури ПРОЄКТУ «Комплементарний фільтр вертикалі» (proj-baro-vertical-fusion.md).
Окремий файл, щоб не колідувати з паралельним письмом figs.py; пише в ту саму ./img/.
Запуск: python figs_proj.py  → ./img/{fusion-pipeline,tau-tradeoff}.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фіг.P1 — повний конвеєр обробки: від сирого акселерометра до висоти ────────
def fig_fusion_pipeline():
    """Ланцюжок кроків прошивки: сире прискорення -> зняти зсув -> обернути у
    світ -> відняти g -> двічі проінтегрувати; окремо баро -> висота; злиття."""
    W, H = 760, 470
    frs = []

    ax0, ay = 40, 92
    steps_a = [
        "сире a\n(тіло, м/с²)", "− зсув\n(калібр.)", "обернути\nу СВІТ",
        "− g\n(9.81)", "∫ →  vz\n∫ →  h",
    ]
    bw, bh, gap = 118, 60, 22
    x = ax0
    prev = None
    for s in steps_a:
        frs.append(fitbox(x, ay, bw, bh, s, size=12, fill="#fdecea", stroke=POS, color=POS))
        if prev is not None:
            frs.append(arrow(prev + bw, ay + bh / 2, x, ay + bh / 2, color=INK, sw=1.8))
        prev = x
        x += bw + gap
    frs.append(text(ax0 + 2.5 * (bw + gap) - gap / 2, ay - 16,
                    "АКСЕЛЕРОМЕТР — швидко, але ДРЕЙФУЄ (високі частоти)",
                    size=12, color=POS, bold=True, anchor="middle"))

    by = 300
    steps_b = ["тиск p\n(Па)", "формула\nвисоти", "baro_alt\n(м)"]
    x = ax0
    prev = None
    for s in steps_b:
        frs.append(fitbox(x, by, bw, bh, s, size=12, fill="#eaf0fd", stroke=NEG, color=NEG))
        if prev is not None:
            frs.append(arrow(prev + bw, by + bh / 2, x, by + bh / 2, color=INK, sw=1.8))
        prev = x
        x += bw + gap
    frs.append(text(ax0 + 1.5 * (bw + gap) - gap / 2, by + bh + 24,
                    "БАРОМЕТР — повільно й шумно, зате АБСОЛЮТНО (низькі частоти)",
                    size=12, color=NEG, bold=True, anchor="middle"))

    sx, sy = 606, (ay + bh / 2 + by + bh / 2) / 2
    frs.append(circle(sx, sy, 30, fill="#ffffff", stroke=INK, sw=2))
    frs.append(text(sx, sy + 9, "+", size=30, color=INK, bold=True))
    frs.append(mtext(sx, sy - 40, "комплементарне\nзлиття", size=11, color=MUTED))
    frs.append(arrow(ax0 + 5 * bw + 4 * gap, ay + bh / 2, sx - 24, sy - 15, color=POS, sw=2))
    frs.append(arrow(ax0 + 3 * bw + 2 * gap, by + bh / 2, sx - 24, sy + 15, color=NEG, sw=2))
    frs.append(arrow(sx + 30, sy, sx + 74, sy, color=FIELD, sw=2.6))
    frs.append(fitbox(sx + 76, sy - 34, 54, 68, "h\nvz", size=13, fill="#eafaf0",
                      stroke=FIELD, color=FIELD, bold=True))

    frs.append(fitbox(150, 402, 470, 46,
        "Прогноз рухом (верх) — швидко й чуйно; корекція тиском (низ) — повільно "
        "й без дрейфу. Стала часу tau вирішує, кому більше вірити на цьому кроці.",
        size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "fusion-pipeline.svg"), W, H, *frs,
           title="Конвеєр вертикалі: акселерометр (швидко) + барометр (абсолютно)")


# ── Фіг.P2 — вибір tau: малий пускає шум баро, великий — дрейф акселерометра ──
def fig_tau_tradeoff():
    """Похибка оцінки висоти як функція сталої часу tau: замалий tau -> лізе шум
    барометра; завеликий -> лізе квадратичний дрейф акселерометра; є мінімум."""
    W, H = 720, 430
    x0, y0 = 100, 66
    gw, gh = 470, 280
    xb, yb = x0, y0 + gh
    frs = []

    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 42,
                    "стала часу tau (с)  →  більше довіри акселерометру",
                    size=12, color=MUTED))
    frs.append(mtext(x0 - 58, y0 + gh / 2 - 8, "похибка\nвисоти", size=12, color=MUTED))

    tmin, tmax = math.log10(0.2), math.log10(20)
    def X(t): return xb + (math.log10(t) - tmin) / (tmax - tmin) * gw
    for t in (0.2, 0.5, 1, 2, 5, 10, 20):
        xx = X(t)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.2))
        frs.append(text(xx, yb + 20, "%g" % t, size=11, color=INK))

    def Y(v): return yb - v * gh

    def v_noise(t): return 0.9 / (1 + 2.2 * t)      # шум баро: спадає з tau
    def v_drift(t): return 0.045 * t                # дрейф accel: росте з tau

    ptn = []
    for i in range(101):
        t = 10 ** (tmin + (tmax - tmin) * i / 100.0)
        ptn.append("%.1f,%.1f" % (X(t), Y(v_noise(t))))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
               'stroke-dasharray="8 5"/>' % (" ".join(ptn), NEG))

    ptd = []
    for i in range(101):
        t = 10 ** (tmin + (tmax - tmin) * i / 100.0)
        ptd.append("%.1f,%.1f" % (X(t), Y(min(v_drift(t), 0.98))))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
               'stroke-dasharray="3 4"/>' % (" ".join(ptd), POS))

    pts = []
    best = (1e9, 0.0)
    for i in range(101):
        t = 10 ** (tmin + (tmax - tmin) * i / 100.0)
        v = (v_noise(t) ** 2 + v_drift(t) ** 2) ** 0.5
        pts.append("%.1f,%.1f" % (X(t), Y(min(v, 0.99))))
        if v < best[0]:
            best = (v, t)
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
               % (" ".join(pts), FIELD))

    vstar, tstar = best
    frs.append(circle(X(tstar), Y(vstar), 6, fill=FIELD, stroke=INK, sw=1.6))
    frs.append(line(X(tstar), Y(vstar), X(tstar), yb, color=FIELD, sw=1, dash="3 4"))
    frs.append(text(X(tstar), Y(vstar) - 14, "золота середина", size=11, color=FIELD,
                    bold=True))

    frs.append(fitbox(X(0.2) + 4, Y(0.9), 176, 40,
        "шум БАРОМЕТРА\n(малий tau — лізе)", size=11, fill="#eaf0fd", stroke=NEG,
        color=NEG))
    frs.append(fitbox(X(5.6), Y(0.92), 178, 40,
        "ДРЕЙФ акселерометра\n(великий tau — лізе)", size=11, fill="#fdecea",
        stroke=POS, color=POS))
    frs.append(fitbox(X(1.05), Y(0.30), 150, 38,
        "сумарна похибка\n(мінімум)", size=11, fill="#eafaf0", stroke=FIELD,
        color=FIELD, bold=True))

    render(os.path.join(IMG, "tau-tradeoff.svg"), W, H, *frs,
           title="Вибір сталої часу tau: між шумом баро й дрейфом акселерометра")


if __name__ == "__main__":
    fig_fusion_pipeline()
    fig_tau_tradeoff()
    print("OK: proj figures written to", IMG)
