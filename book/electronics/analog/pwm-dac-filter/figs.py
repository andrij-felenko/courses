# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

import math


def poly(points, color=INK, sw=2.0, fill="none"):
    pts = " ".join("%.1f,%.1f" % (x, y) for (x, y) in points)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, fill, color, sw))


def square_wave(x0, y_hi, y_lo, period_px, duty, n_periods):
    """Список точок прямокутної ШІМ: high частку duty, далі low."""
    pts = [(x0, y_lo)]
    x = x0
    for _ in range(n_periods):
        on = period_px * duty
        pts.append((x, y_hi))           # фронт угору
        pts.append((x + on, y_hi))      # ввімкнено
        pts.append((x + on, y_lo))      # фронт униз
        pts.append((x + period_px, y_lo))  # вимкнено до кінця періоду
        x += period_px
    return pts


# ── 1. Рівні ШІМ і середнє при різних D ─────────────────────────────────────
def fig_pwm_levels():
    W, H = 820, 430
    frags = []
    x0 = 150
    plot_w = 510
    period = plot_w / 4.0          # 4 періоди в кадрі
    rows = [
        (0.25, "D = 0.25"),
        (0.50, "D = 0.50"),
        (0.75, "D = 0.75"),
    ]
    row_h = 118
    top = 70
    for i, (duty, lab) in enumerate(rows):
        baseY = top + i * row_h + 64
        hiY = baseY - 56
        # осі рівнів
        frags.append(line(x0, hiY, x0 + plot_w, hiY, color=MUTED, sw=1, dash="3,4"))
        frags.append(line(x0, baseY, x0 + plot_w, baseY, color=LINE, sw=1.4))
        frags.append(text(x0 - 12, hiY + 5, "Vdd", size=13, color=MUTED, anchor="end"))
        frags.append(text(x0 - 12, baseY + 5, "0", size=13, color=MUTED, anchor="end"))
        # прямокутник ШІМ
        pts = square_wave(x0, hiY, baseY, period, duty, 4)
        frags.append(poly(pts, color=NEG, sw=2.4))
        # лінія середнього
        avgY = baseY - 56 * duty
        frags.append(line(x0, avgY, x0 + plot_w, avgY, color=POS, sw=2.2, dash="7,5"))
        if i == 1:                 # підпис лінії середнього — один раз
            frags.append(text(x0 + plot_w + 10, avgY + 5,
                              "середнє = Vdd·D", size=12, color=POS, anchor="start"))
        # підпис рядка
        frags.append(text(x0 - 70, baseY - 26, lab, size=14, color=INK, bold=True, anchor="middle"))
    # підпис осі часу
    frags.append(text(x0 + plot_w / 2, H - 16,
                      "час  →   (період T однаковий у всіх рядках)", size=13, color=MUTED))
    return render(os.path.join(IMG, "pwm-levels.svg"), W, H, *frags,
                  title="Шпаруватість керує середнім; рівнів усе одно два")


# ── 2. ШІМ → RC-фільтр → згладжений вихід ───────────────────────────────────
def fig_rc_smoothing():
    W, H = 780, 360
    frags = []
    midY = 200

    # --- ліворуч: вхідна ШІМ ---
    ix = 60
    iw = 150
    hiY, loY = midY - 38, midY + 22
    frags.append(text(ix + iw / 2, 70, "вхід: ШІМ", size=14, bold=True))
    pts = square_wave(ix, hiY, loY, iw / 3.0, 0.5, 3)
    frags.append(poly(pts, color=NEG, sw=2.4))
    frags.append(line(ix, loY + 26, ix + iw, loY + 26, color=MUTED, sw=1, dash="3,4"))

    # стрілка у фільтр
    frags.append(arrow(ix + iw + 6, midY - 8, ix + iw + 44, midY - 8, color=LINE, sw=2))

    # --- посередині: RC-схема ---
    nodeIn = ix + iw + 50
    nodeOut = nodeIn + 150
    wireY = midY - 30
    gndY = midY + 70
    # провід вхід -> R -> вихід
    frags.append(line(nodeIn, wireY, nodeIn + 30, wireY, color=LINE, sw=2))
    # резистор (зигзаг)
    rx0 = nodeIn + 30
    rx1 = rx0 + 70
    zz = [(rx0, wireY)]
    seg = (rx1 - rx0) / 6.0
    for k in range(1, 6):
        zz.append((rx0 + seg * k, wireY + (10 if k % 2 else -10)))
    zz.append((rx1, wireY))
    frags.append(poly(zz, color=INK, sw=2.2))
    frags.append(text((rx0 + rx1) / 2, wireY - 16, "R", size=15, bold=True, color=INK))
    frags.append(line(rx1, wireY, nodeOut, wireY, color=LINE, sw=2))
    # вузол виходу -> вниз до конденсатора
    frags.append(line(nodeOut, wireY, nodeOut, wireY + 34, color=LINE, sw=2))
    # конденсатор (дві пластини)
    capY = wireY + 34
    frags.append(line(nodeOut - 16, capY, nodeOut + 16, capY, color=INK, sw=2.6))
    frags.append(line(nodeOut - 16, capY + 9, nodeOut + 16, capY + 9, color=INK, sw=2.6))
    frags.append(text(nodeOut + 26, capY + 8, "C", size=15, bold=True, color=INK))
    # від конденсатора до землі
    frags.append(line(nodeOut, capY + 9, nodeOut, gndY, color=LINE, sw=2))
    # земля
    for j, ww in enumerate((22, 14, 7)):
        frags.append(line(nodeOut - ww, gndY + j * 5, nodeOut + ww, gndY + j * 5, color=LINE, sw=2))
    # вузол виходу далі праворуч
    frags.append(line(nodeOut, wireY, nodeOut + 26, wireY, color=LINE, sw=2))
    frags.append(circle(nodeOut + 26, wireY, 3.5, fill=INK, stroke=INK))
    frags.append(arrow(nodeOut + 30, midY - 8, nodeOut + 64, midY - 8, color=LINE, sw=2))

    # --- праворуч: згладжений вихід ---
    ox = nodeOut + 72
    ow = 150
    frags.append(text(ox + ow / 2, 70, "вихід: майже рівна U", size=14, bold=True))
    base2 = midY + 22
    avg2 = midY - 12
    # пилкоподібний вихід навколо середнього
    ripple_pts = []
    n = 3
    pw = ow / n
    amp = 7
    for k in range(n):
        x = ox + k * pw
        # повзе вгору (заряд) потім униз (розряд) — спрощено трикутник
        ripple_pts.append((x, avg2 + amp))
        ripple_pts.append((x + pw * 0.5, avg2 - amp))
        ripple_pts.append((x + pw, avg2 + amp))
    frags.append(line(ox, avg2, ox + ow, avg2, color=POS, sw=1.6, dash="6,5"))
    frags.append(poly(ripple_pts, color=NEG, sw=2.4))
    frags.append(line(ox, base2 + 4, ox + ow, base2 + 4, color=MUTED, sw=1, dash="3,4"))
    frags.append(text(ox + ow + 8, avg2 + 4, "≈ Vdd·D", size=12, color=POS, anchor="start"))
    frags.append(text(ox + ow / 2, base2 + 30, "+ дрібні пульсації", size=12, color=NEG))

    return render(os.path.join(IMG, "rc-smoothing.svg"), W, H, *frags,
                  title="RC усереднює ШІМ у постійну напругу")


# ── 3. Пульсації навколо середнього + парабола D·(1−D) ──────────────────────
def fig_ripple():
    W, H = 780, 380
    frags = []

    # ── ЛІВА панель: пилка навколо середнього ──
    Lx, Ly = 70, 90
    Lw, Lh = 300, 210
    frags.append(text(Lx + Lw / 2, 64, "вихідна напруга в часі", size=14, bold=True))
    # рамка-осі
    frags.append(line(Lx, Ly, Lx, Ly + Lh, color=LINE, sw=1.6))            # вісь U
    frags.append(line(Lx, Ly + Lh, Lx + Lw, Ly + Lh, color=LINE, sw=1.6))  # вісь t
    frags.append(text(Lx - 10, Ly + 6, "U", size=13, color=MUTED, anchor="end"))
    frags.append(text(Lx + Lw, Ly + Lh + 20, "час →", size=12, color=MUTED, anchor="end"))
    avgY = Ly + Lh * 0.45
    frags.append(line(Lx, avgY, Lx + Lw, avgY, color=POS, sw=1.8, dash="7,5"))
    frags.append(text(Lx + Lw + 6, avgY + 4, "Vdd·D", size=12, color=POS, anchor="start"))
    # пилка: заряд (вгору) під час on, розряд (вниз) під час off
    saw = []
    n = 4
    pw = Lw / n
    amp = 26
    duty = 0.5
    for k in range(n):
        x = Lx + k * pw
        saw.append((x, avgY + amp))                 # низ перед фронтом
        saw.append((x + pw * duty, avgY - amp))     # повзе вгору під час on
        saw.append((x + pw, avgY + amp))            # сповзає вниз під час off
    frags.append(poly(saw, color=NEG, sw=2.4))
    # позначка розмаху Vпульс
    bx = Lx + Lw * 0.5
    frags.append(line(bx, avgY - amp, bx, avgY + amp, color=FIELD, sw=1.6))
    frags.append(line(bx - 5, avgY - amp, bx + 5, avgY - amp, color=FIELD, sw=1.6))
    frags.append(line(bx - 5, avgY + amp, bx + 5, avgY + amp, color=FIELD, sw=1.6))
    frags.append(text(bx + 12, avgY - amp - 6, "Vпульс", size=12, color=FIELD, bold=True, anchor="start"))

    # ── ПРАВА панель: парабола D·(1−D) ──
    Rx, Ry = 470, 90
    Rw, Rh = 240, 210
    frags.append(text(Rx + Rw / 2, 64, "розмах vs шпаруватість", size=14, bold=True))
    frags.append(line(Rx, Ry, Rx, Ry + Rh, color=LINE, sw=1.6))             # вісь
    frags.append(line(Rx, Ry + Rh, Rx + Rw, Ry + Rh, color=LINE, sw=1.6))   # вісь D
    frags.append(text(Rx - 8, Ry + 6, "Vпульс", size=12, color=MUTED, anchor="end"))
    frags.append(text(Rx, Ry + Rh + 20, "0", size=12, color=MUTED, anchor="middle"))
    frags.append(text(Rx + Rw / 2, Ry + Rh + 20, "0.5", size=12, color=MUTED, anchor="middle"))
    frags.append(text(Rx + Rw, Ry + Rh + 20, "1", size=12, color=MUTED, anchor="middle"))
    frags.append(text(Rx + Rw / 2, Ry + Rh + 38, "D", size=13, color=MUTED, anchor="middle", bold=True))
    # крива D(1-D), масштабована: макс 0.25 -> майже вся висота
    par = []
    steps = 60
    for s in range(steps + 1):
        d = s / steps
        val = d * (1 - d)            # 0..0.25
        x = Rx + Rw * d
        y = Ry + Rh - (val / 0.25) * (Rh - 16)
        par.append((x, y))
    frags.append(poly(par, color=NEG, sw=2.6))
    # вершина при D=0.5
    topX = Rx + Rw * 0.5
    topY = Ry + Rh - (Rh - 16)
    frags.append(line(topX, topY, topX, Ry + Rh, color=FIELD, sw=1.4, dash="4,4"))
    frags.append(circle(topX, topY, 4, fill=POS, stroke=POS))
    frags.append(text(topX, topY - 10, "макс при D=0.5", size=12, color=POS, bold=True))
    # нулі на краях
    frags.append(circle(Rx, Ry + Rh, 4, fill=MUTED, stroke=MUTED))
    frags.append(circle(Rx + Rw, Ry + Rh, 4, fill=MUTED, stroke=MUTED))

    return render(os.path.join(IMG, "ripple.svg"), W, H, *frags,
                  title="Пульсації: пилка навколо середнього, найбільша посередині")


# ── 4. Лінеаризація: експонента розряду vs її дотична-пряма ──────────────────
# (для вставки math-ripple-derivation.md — серце виводу: на короткому кроці
#  off-фази експонента майже зливається з прямою; зазор — частки відсотка)
def fig_linear_vs_exp():
    W, H = 720, 430
    frags = []
    ox, oy = 90, 64
    gw, gh = 540, 282
    bx, by = ox, oy + gh

    # навмисне роздутий крок k=(1-D)T/τ=0.5, щоб вигин узагалі побачити
    k = 0.5
    V0 = 1.0
    def vexp(s): return V0 * math.exp(-k * s)
    def vlin(s): return V0 * (1 - k * s)
    vmin = V0 * (1 - k) - 0.06
    vmax = V0 + 0.02
    def X(s): return bx + s * gw
    def Y(v): return by - (v - vmin) / (vmax - vmin) * gh

    # осі
    frags.append(line(bx, by, bx + gw, by, color=INK, sw=2))
    frags.append(line(bx, by, bx, oy, color=INK, sw=2))
    frags.append(text(bx + gw / 2, by + 44,
                      "час, частка off-фази  s = t / [(1−D)·T]", size=13, color=MUTED))
    frags.append(text(bx - 60, oy + gh / 2, "U", size=15, color=MUTED, bold=True))

    # рівень старту U0
    frags.append(line(bx, Y(V0), bx + gw, Y(V0), color="#d7dbe0", sw=1, dash="4 4"))
    frags.append(text(bx - 10, Y(V0) + 4, "U₀", size=12, color=MUTED, anchor="end"))
    frags.append(circle(X(0), Y(V0), 4, fill=INK, stroke=INK, sw=1))

    # заштрихований зазор між прямою і експонентою
    N = 60
    poly_pts = [(X(i / N), Y(vlin(i / N))) for i in range(N + 1)]
    poly_pts += [(X(i / N), Y(vexp(i / N))) for i in range(N, -1, -1)]
    pts = " ".join("%.1f,%.1f" % p for p in poly_pts)
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.20" stroke="none"/>' % (pts, POS))

    # експонента (синя суцільна) і пряма-дотична (червона штрих)
    epath = "M " + " L ".join("%.1f %.1f" % (X(i / N), Y(vexp(i / N))) for i in range(N + 1))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (epath, NEG))
    frags.append(line(X(0), Y(vlin(0)), X(1), Y(vlin(1)), color=POS, sw=2.6, dash="7 5"))

    # підписи кривих
    frags.append(fitbox(bx + 14, oy + 6, 256, 28,
                        "експонента  U₀·e^(−s·(1−D)T/τ)", size=12,
                        fill="#eaf0fd", stroke=NEG, color=NEG))
    frags.append(fitbox(bx + 248, by - 92, 274, 28,
                        "пряма-дотична  U₀·(1 − s·(1−D)T/τ)", size=12,
                        fill="#fdecea", stroke=POS, color=POS))
    frags.append(text(X(0.80) + 6, Y((vlin(0.80) + vexp(0.80)) / 2),
                      "зазор", size=11, color=POS, anchor="start"))

    note = ("Крок навмисне роздуто (k = (1−D)T/τ = 0.5), щоб вигин узагалі було видно; "
            "у робочому фільтрі k ≈ 0.05 — криві лежать одна на одній.")
    frags.append(text(W / 2, H - 14, note, size=10, color=MUTED))
    return render(os.path.join(IMG, "linear-vs-exp.svg"), W, H, *frags,
                  title="Заміна експоненти прямою: на off-фазі вони майже зливаються")


# ── 5. Геометрія нахилу: rate × time = просідання ───────────────────────────
def fig_slope_geometry():
    W, H = 420, 400
    frags = []
    Lx, Ly = 56, 86
    Lw, Lh = 300, 210
    bx, by = Lx, Ly + Lh

    frags.append(line(bx, by, bx + Lw, by, color=INK, sw=2))
    frags.append(line(bx, by, bx, Ly, color=INK, sw=2))

    D = 0.35
    midV = (Ly + by) / 2
    amp = 40
    x0 = bx + 18
    t_on = 0.30
    xpk = x0 + (bx + Lw - 18 - x0) * t_on
    xend = bx + Lw - 18
    yhi = midV - amp / 2
    ylo = midV + amp / 2

    frags.append(line(bx, midV, bx + Lw, midV, color="#d7dbe0", sw=1, dash="5 4"))
    frags.append(text(bx + Lw - 2, midV - 6, "U₀=Vdd·D", size=10, color=MUTED, anchor="end"))

    # зуб: ON ↑ (заряд), OFF ↓ (розряд)
    frags.append(line(x0, ylo, xpk, yhi, color=NEG, sw=3))
    frags.append(line(xpk, yhi, xend, ylo, color=POS, sw=3))

    # розмах Vпульс
    frags.append(line(xend + 12, yhi, xend + 12, ylo, color=FIELD, sw=1.6))
    frags.append(line(xend + 8, yhi, xend + 16, yhi, color=FIELD, sw=1.6))
    frags.append(line(xend + 8, ylo, xend + 16, ylo, color=FIELD, sw=1.6))
    frags.append(text(xend + 18, midV + 4, "Vпульс", size=11, color=FIELD, anchor="start", bold=True))

    frags.append(text((xpk + xend) / 2 + 4, yhi - 6, "нахил −Vdd·D/τ", size=10, color=POS))
    frags.append(text((x0 + xpk) / 2 - 8, ylo + 14, "+Vdd(1−D)/τ", size=10, color=NEG))

    # бази фаз
    frags.append(line(xpk, by + 8, xend, by + 8, color=MUTED, sw=1.4))
    frags.append(text((xpk + xend) / 2, by + 22, "(1−D)·T", size=10, color=MUTED))
    frags.append(line(x0, by + 8, xpk, by + 8, color=MUTED, sw=1.4))
    frags.append(text((x0 + xpk) / 2, by + 22, "D·T", size=10, color=MUTED))

    frags.append(fitbox(Lx, by + 34, Lw, 30,
                        "нахил × час = Vdd·D·(1−D)·T/τ", size=12,
                        fill=FILL, stroke=LINE, color=INK, bold=True))
    return render(os.path.join(IMG, "slope-geometry.svg"), W, H, *frags,
                  title="Просідання = нахил × тривалість off-фази")


if __name__ == "__main__":
    fig_pwm_levels()
    fig_rc_smoothing()
    fig_ripple()
    fig_linear_vs_exp()
    fig_slope_geometry()
    print("figs done:", os.listdir(IMG))
