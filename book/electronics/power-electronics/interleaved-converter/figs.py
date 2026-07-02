# -*- coding: utf-8 -*-
"""Фігури до теми «Паралельно-фазний (interleaved) перетворювач»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

PHASE_COL = ["#c0392b", "#27ae60", "#2457d6", "#8e44ad"]  # 4 фази — 4 кольори


# ── 1. Топологія: N однакових buck-комірок на спільних входах-виходах ──────────
def fig_topology():
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 26, "Три фази на спільних вхідному й вихідному конденсаторах", size=16, bold=True))

    # спільна вхідна шина (зверху) і вихідна (праворуч)
    xin = 70                 # вхідна вертикальна шина
    xnode = 300              # де сходяться котушки → вихід
    xout = 560               # вихідний вузол
    ytop, ybot = 70, 360
    # вхідна шина
    frags.append(line(xin, ytop, xin, ybot, color=INK, sw=2.5))
    frags.append(plus(xin, ytop - 4, r=8))
    frags.append(text(xin - 22, (ytop + ybot) / 2, "Vвх", size=13, color=INK, anchor="middle"))
    # вхідний конденсатор
    frags.append(line(xin, 200, xin - 40, 200, color=INK, sw=2))
    frags.append(line(xin - 40, 188, xin - 40, 212, color=INK, sw=2.5))
    frags.append(line(xin - 34, 188, xin - 34, 212, color=INK, sw=2.5))
    frags.append(text(xin - 55, 200, "Cвх", size=11, color=MUTED, anchor="end"))

    ys = [110, 200, 290]     # три ряди-фази
    for i, y in enumerate(ys):
        c = PHASE_COL[i]
        # напівміст (два ключі) — прямокутник-пара
        frags.append(line(xin, y, xin + 30, y, color=INK, sw=2))
        frags.append(rect(xin + 30, y - 16, 54, 32, fill="#f4f6f8", stroke=c, sw=2.2))
        frags.append(text(xin + 57, y + 5, "Q%d" % (i + 1), size=13, color=c, bold=True))
        # котушка
        frags.append(line(xin + 84, y, xin + 120, y, color=INK, sw=2))
        # символ котушки — три дужки
        for k in range(3):
            cx = xin + 128 + k * 20
            frags.append('<path d="M%.1f %.1f A10 10 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2"/>'
                         % (cx - 10, y, cx + 10, y, INK))
        frags.append(text(xin + 148, y - 16, "L%d" % (i + 1), size=12, color=INK, anchor="middle"))
        # від котушки до спільного вихідного вузла
        frags.append(line(xin + 188, y, xnode, y, color=c, sw=2.5))
    # спільний вузол виходу
    frags.append(line(xnode, ys[0], xnode, ys[-1], color=INK, sw=2.5))
    frags.append(circle(xnode, ys[0], 3.5, fill=INK, stroke=INK))
    frags.append(circle(xnode, ys[1], 3.5, fill=INK, stroke=INK))
    frags.append(circle(xnode, ys[-1], 3.5, fill=INK, stroke=INK))
    # до виходу
    frags.append(line(xnode, ys[1], xout, ys[1], color=INK, sw=2.5))
    # вихідний конденсатор
    frags.append(line(xout, ys[1], xout, ys[1] + 40, color=INK, sw=2))
    frags.append(line(xout - 14, ys[1] + 40, xout + 14, ys[1] + 40, color=INK, sw=2.5))
    frags.append(line(xout - 14, ys[1] + 46, xout + 14, ys[1] + 46, color=INK, sw=2.5))
    frags.append(line(xout, ys[1] + 46, xout, ybot, color=INK, sw=2))
    frags.append(text(xout + 26, ys[1] + 42, "Cвих", size=11, color=MUTED, anchor="start"))
    # вихідний вузол-мітка
    frags.append(circle(xout, ys[1], 3.5, fill=INK, stroke=INK))
    frags.append(line(xout, ys[1], xout + 90, ys[1], color=INK, sw=2.5))
    frags.append(plus(xout + 90, ys[1], r=8))
    frags.append(text(xout + 108, ys[1] + 4, "Vвих", size=13, color=INK, anchor="start"))
    # спільна земля
    frags.append(line(xin, ybot, xout, ybot, color=INK, sw=2.5))
    frags.append(line(xin - 40, 212, xin - 40, ybot, color=INK, sw=2))
    frags.append(line(xin - 40, ybot, xin, ybot, color=INK, sw=2))
    for gx in (xin, xout):
        frags.append(line(gx - 9, ybot, gx + 9, ybot, color=INK, sw=2))
    frags.append(text((xin + xout) / 2, ybot + 18, "спільна земля", size=11, color=MUTED, anchor="middle"))

    # підпис фаз-зсуву
    box = fitbox(xin + 30, 375, 300, 42,
                 "керує ОДИН контролер: фази вмикаються по черзі,\nзсунуті на 360°/3 = 120° такту",
                 size=11, fill="#eef6ff", stroke=NEG)
    frags.append(box)

    render(os.path.join(IMG, "topology.svg"), W, H, *frags)


# ── 2. Скасування пульсацій: три трикутники + їхня сума ────────────────────────
def fig_ripple_cancel():
    W, H = 720, 470
    frags = []
    frags.append(text(W / 2, 26, "Три зсунуті трикутники дають рівнішу суму", size=16, bold=True))

    n = 3
    x0, x1 = 70, 660
    span = x1 - x0
    periods = 2.0
    # трикутна хвиля фази: пилка «нагору-вниз» з розмахом amp навколо avg
    def tri(t, shift):
        # t у [0,1) — доля повного такту; shift — зсув фази у долях такту
        u = (t - shift) % 1.0
        # buck при D≈0.5: наростання пів-такту, спад пів-такту
        if u < 0.5:
            return u / 0.5          # 0..1
        return (1.0 - u) / 0.5      # 1..0

    # три верхні доріжки — окремі фази
    tops = [70, 150, 230]
    amp = 26
    N = 400
    for i in range(n):
        c = PHASE_COL[i]
        base = tops[i]
        frags.append(line(x0, base + amp + 6, x1, base + amp + 6, color="#dddddd", sw=1))
        pts = []
        for k in range(N + 1):
            tt = periods * k / N
            y = base + amp + 6 - tri(tt % 1.0, i / n) * (2 * amp)
            pts.append("%.1f,%.1f" % (x0 + span * k / N, y))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), c))
        frags.append(text(x0 - 8, base + amp - 4, "iL%d" % (i + 1), size=12, color=c, anchor="end", bold=True))

    # нижня доріжка — сума
    sy = 370
    ssp = 30
    frags.append(line(x0, sy, x1, sy, color="#dddddd", sw=1))
    pts = []
    smin, smax = 99, -99
    raw = []
    for k in range(N + 1):
        tt = periods * k / N
        s = sum(tri(tt % 1.0, i / n) for i in range(n))
        raw.append(s)
        smin = min(smin, s)
        smax = max(smax, s)
    mid = (smin + smax) / 2
    for k in range(N + 1):
        # нормуємо навколо середини, масштаб — щоб було видно малий розмах
        y = sy - (raw[k] - mid) * ssp
        pts.append("%.1f,%.1f" % (x0 + span * k / N, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))
    frags.append(text(x0 - 8, sy - 4, "Σ iL", size=13, color=INK, anchor="end", bold=True))
    # позначити розмах суми
    ytopS = sy - (smax - mid) * ssp
    ybotS = sy - (smin - mid) * ssp
    frags.append(line(x1 - 6, ytopS, x1 - 6, ybotS, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(x1 + 8, (ytopS + ybotS) / 2, "малий", size=11, color=POS, anchor="start"))

    # розділова підказка
    frags.append(text(x0, 55, "кожна фаза окремо (повний розмах ΔI):", size=12, color=MUTED, anchor="start"))
    frags.append(text(x0, 320, "сума фаз (те, що бачить конденсатор):", size=12, color=MUTED, anchor="start"))
    frags.append(fitbox(x0, 405, span, 42,
                        "розмах ↓ у кілька разів, а частота пульсації ↑ у n = 3 рази — легше для конденсатора й фільтра",
                        size=11.5, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "ripple-cancel.svg"), W, H, *frags)


# ── 3. Коефіцієнт пульсацій виходу від D для 2/3/4 фаз (нулі в D=k/n) ──────────
def fig_sweet_spots():
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 26, "Пульсація виходу падає до нуля в точках D = k/n", size=16, bold=True))

    x0, x1 = 80, 660
    y0, y1 = 340, 70      # y0 — низ (0), y1 — верх (1)
    span = x1 - x0
    hgt = y0 - y1

    # осі
    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.8))       # вісь D
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.8))       # вісь коеф.
    frags.append(text((x0 + x1) / 2, y0 + 40, "коефіцієнт заповнення D", size=13, color=INK))
    # мітки D
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        xx = x0 + span * d
        frags.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.5))
        frags.append(text(xx, y0 + 20, ("%.2f" % d), size=11, color=MUTED))
    frags.append(text(x0 - 10, y1 + 4, "1", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, y0 + 4, "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 46, (y0 + y1) / 2, "K", size=13, color=INK, anchor="middle", bold=True))

    # нормований коефіцієнт скасування K(D) для n фаз:
    # у межах між сусідніми k/n піднімається до ~1 і повертається в 0 на кожному k/n.
    # Проста інженерна апроксимація форми (для наочності нулів):
    def kfac(D, n):
        if D <= 0 or D >= 1:
            return 0.0
        m = math.floor(n * D)
        frac = n * D - m       # 0..1 між вузлами
        # дзвіночок 0→1→0 у кожному сегменті, трохи асиметричний ближче до реального
        return math.sin(math.pi * frac)

    configs = [(2, PHASE_COL[0], "n = 2"),
               (3, PHASE_COL[1], "n = 3"),
               (4, PHASE_COL[2], "n = 4")]
    N = 400
    for n, c, lab in configs:
        pts = []
        for k in range(N + 1):
            D = k / N
            v = kfac(D, n)
            pts.append("%.1f,%.1f" % (x0 + span * D, y0 - v * hgt))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), c))

    # мітки-нулі для n=4 (виразні точки D=k/4)
    for k in range(1, 4):
        D = k / 4
        xx = x0 + span * D
        frags.append(circle(xx, y0, 3.5, fill=PHASE_COL[2], stroke=PHASE_COL[2]))
    # позначка D=0.5 (нуль для 2 і 4 фаз)
    frags.append(line(x0 + span * 0.5, y0, x0 + span * 0.5, y1, color="#cccccc", sw=1, dash="4,4"))

    # легенда
    lx, ly = x1 - 96, y1 + 6
    for i, (n, c, lab) in enumerate(configs):
        yy = ly + i * 20
        frags.append(line(lx, yy, lx + 22, yy, color=c, sw=3))
        frags.append(text(lx + 28, yy + 4, lab, size=12, color=c, anchor="start", bold=True))

    frags.append(fitbox(x0, 372, span, 40,
                        "більше фаз → більше нулів і нижчі «горби» між ними: пульсація виходу мала в ширшому діапазоні D",
                        size=11.5, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(IMG, "sweet-spots.svg"), W, H, *frags)


# ── 4. Геометрія суми: як зсунуті рампи складаються в дрібнішу пилку ───────────
#   (для вставки math-ripple-cancellation) — показуємо ЧОМУ сума лягає в нуль
#   при D = k/N: сходинка сумарного струму стає рівною, коли рампи стикуються.
def fig_stacking():
    W, H = 720, 500
    frags = []
    frags.append(text(W / 2, 26, "Сума зсунутих рамп: рівна сходинка ⇔ D = k/N", size=16, bold=True))

    x0, x1 = 80, 660
    span = x1 - x0
    N = 3
    D = 1.0 / 3.0          # рівно солодка точка k=1, N=3
    periods = 1.0

    # верх: три окремі рампи (спрощена трикутна форма: наростання частку D, спад 1-D)
    def ramp(t, shift, D):
        u = (t - shift) % 1.0
        if u < D:
            return u / D                      # 0..1 угору (ключ відкритий)
        return (1.0 - u) / (1.0 - D)          # 1..0 вниз (ключ закритий)

    tops = [70, 140, 210]
    amp = 22
    M = 600
    for i in range(N):
        c = PHASE_COL[i]
        base = tops[i] + amp + 6
        frags.append(line(x0, base, x1, base, color="#e2e2e2", sw=1))
        pts = []
        for k in range(M + 1):
            tt = periods * k / M
            y = base - ramp(tt, i / N, D) * (2 * amp)
            pts.append("%.1f,%.1f" % (x0 + span * k / M, y))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), c))
        frags.append(text(x0 - 8, tops[i] + amp, "iL%d" % (i + 1), size=12, color=c, anchor="end", bold=True))
        # позначити вершини «стику» вертикальними пунктирами на межах k/N
    for k in range(1, N):
        xx = x0 + span * (k / N)
        frags.append(line(xx, tops[0] - 4, xx, 300, color="#c9c9c9", sw=1, dash="3,4"))

    # низ: сума — рівна лінія (сходинка) з ледь помітним residual
    sy = 400
    frags.append(line(x0, sy, x1, sy, color="#e2e2e2", sw=1))
    ssc = 42
    raw = []
    for k in range(M + 1):
        tt = periods * k / M
        s = sum(ramp(tt, i / N, D) for i in range(N))
        raw.append(s)
    smin, smax = min(raw), max(raw)
    mid = (smin + smax) / 2
    pts = []
    for k in range(M + 1):
        y = sy - (raw[k] - mid) * ssc
        pts.append("%.1f,%.1f" % (x0 + span * k / M, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))
    frags.append(text(x0 - 8, sy + 4, "Σ iL", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(x1 - 4, sy - 12, "рівна → ΔIΣ ≈ 0", size=12, color=FIELD, anchor="end", bold=True))

    frags.append(text(x0, 60, "три рампи, зсунуті на 1/3 такту, D = 1/3:", size=12, color=MUTED, anchor="start"))
    frags.append(text(x0, 350, "їхня сума в один вихідний вузол:", size=12, color=MUTED, anchor="start"))
    frags.append(fitbox(x0, 432, span, 46,
                        "у кожен момент рівно ОДНА фаза наростає, дві спадають — і нахили гасяться:\n"
                        "сумарний струм майже стоїть, розмах падає в нуль саме при D = k/N",
                        size=11.5, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "stacking.svg"), W, H, *frags)


# ── 5. ТОЧНА крива K(D,N) за формулою (m+1−ND)(ND−m)/[ND(1−D)] ─────────────────
def fig_kfactor():
    W, H = 720, 450
    frags = []
    frags.append(text(W / 2, 26, "Коефіцієнт скасування K(D,N) — точна формула", size=16, bold=True))

    x0, x1 = 80, 640
    y0, y1 = 350, 70
    span = x1 - x0
    hgt = y0 - y1

    # осі
    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.8))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.8))
    frags.append(text((x0 + x1) / 2, y0 + 40, "коефіцієнт заповнення D", size=13, color=INK))
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        xx = x0 + span * d
        frags.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.5))
        frags.append(text(xx, y0 + 20, ("%.2f" % d), size=11, color=MUTED))
    for kv in (0.0, 0.5, 1.0):
        yy = y0 - kv * hgt
        frags.append(line(x0 - 5, yy, x0, yy, color=INK, sw=1.5))
        frags.append(text(x0 - 10, yy + 4, ("%.1f" % kv), size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 44, (y0 + y1) / 2, "K", size=14, color=INK, anchor="middle", bold=True))

    def kfac(D, n):
        if D <= 0 or D >= 1:
            return 1.0                       # межа: одна фаза несе весь розмах
        m = math.floor(n * D)
        return ((m + 1 - n * D) * (n * D - m)) / (n * D * (1 - D))

    configs = [(2, PHASE_COL[0], "N = 2"),
               (3, PHASE_COL[1], "N = 3"),
               (6, PHASE_COL[3], "N = 6")]
    M = 1200
    for n, c, lab in configs:
        pts = []
        for k in range(M + 1):
            D = k / M
            v = min(kfac(D, n), 1.0)
            pts.append("%.1f,%.1f" % (x0 + span * D, y0 - v * hgt))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.3"/>' % (" ".join(pts), c))

    # нулі для N=6 — точки на осі
    for k in range(1, 6):
        D = k / 6
        xx = x0 + span * D
        frags.append(circle(xx, y0, 3.2, fill=PHASE_COL[3], stroke=PHASE_COL[3]))

    # легенда
    lx, ly = x1 - 90, y1 + 4
    for i, (n, c, lab) in enumerate(configs):
        yy = ly + i * 20
        frags.append(line(lx, yy, lx + 22, yy, color=c, sw=3))
        frags.append(text(lx + 28, yy + 4, lab, size=12, color=c, anchor="start", bold=True))

    # підпис-формула та висновок про зовнішні горби
    frags.append(fitbox(x0, 372, span, 24,
                        "K = (m+1 − N·D)(N·D − m) / [N·D·(1 − D)],   m = ⌊N·D⌋",
                        size=12.5, fill="#eef6ff", stroke=NEG, bold=True))
    frags.append(fitbox(x0, 402, span, 40,
                        "нулі точно в D = k/N; горби всередині падають з ростом N, але КРАЙНІ горби "
                        "(мале D) лишаються високими — тому для малого D беруть N так, щоб сісти на нуль",
                        size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(IMG, "kfactor.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_topology()
    fig_ripple_cancel()
    fig_sweet_spots()
    fig_stacking()
    fig_kfactor()
    print("figs done")
