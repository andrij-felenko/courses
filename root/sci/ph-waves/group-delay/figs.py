# -*- coding: utf-8 -*-
"""Фігури до статті «Групова затримка». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def wave(xa, xb, fn, color, sw=1.8, n=900, dash=None):
    """Полілінія y=fn(x) по пікселях x∈[xa,xb]."""
    pts = []
    for i in range(n + 1):
        x = xa + (xb - xa) * i / n
        pts.append("%.1f,%.1f" % (x, fn(x)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s"/>'
            % (color, sw, d, " ".join(pts)))


# ── Фігура 1: обвідна приходить пізніше за гребінь ───────────────────────────
def fig_envelope_late():
    W, H = 940, 600
    x0, xr = 90, 850
    yc1, yc2 = 150, 390          # центри верхньої та нижньої панелей
    A = 66
    wpx = 92.0                    # півширина обвідної (гаусова)
    per = 46.0                    # період носія, px
    f = 1.0 / per

    x_in = x0 + 0.26 * (xr - x0)  # пік обвідної та гребінь на вході (збігаються)
    shift_phi = 92.0              # фазова затримка (гребінь носія)
    shift_g = 178.0              # групова затримка (обвідна)
    x_phi = x_in + shift_phi
    x_g = x_in + shift_g

    def env(x, xc):
        return math.exp(-((x - xc) / wpx) ** 2)

    base1 = line(x0, yc1, xr, yc1, MUTED, 1.0, dash="3,5")
    base2 = line(x0, yc2, xr, yc2, MUTED, 1.0, dash="3,5")

    # вхід: обвідна й носій із піком/гребенем у x_in
    in_env_t = wave(x0, xr, lambda x: yc1 - A * env(x, x_in), FIELD, 1.6, dash="6,5")
    in_env_b = wave(x0, xr, lambda x: yc1 + A * env(x, x_in), FIELD, 1.6, dash="6,5")
    in_car = wave(x0, xr, lambda x: yc1 - A * env(x, x_in) * math.cos(2 * math.pi * f * (x - x_in)), INK, 1.8)

    # вихід: обвідна з піком у x_g, носій із гребенем у x_phi
    out_env_t = wave(x0, xr, lambda x: yc2 - A * env(x, x_g), FIELD, 1.6, dash="6,5")
    out_env_b = wave(x0, xr, lambda x: yc2 + A * env(x, x_g), FIELD, 1.6, dash="6,5")
    out_car = wave(x0, xr, lambda x: yc2 - A * env(x, x_g) * math.cos(2 * math.pi * f * (x - x_phi)), INK, 1.8)

    cap1 = text(x0, 72, "Вхід: пік обвідної й гребінь носія збігаються", size=15, color=INK, anchor="start", bold=True)
    leg_env = text(xr, 72, "− − обвідна", size=13, color=FIELD, anchor="end", bold=True)
    cap2 = text(xr, 300, "Вихід: обвідна зсунулась далі за гребінь", size=15, color=INK, anchor="end", bold=True)

    # вертикальні орієнтири (закінчуються над смугою розмірів)
    g_in = line(x_in, 96, x_in, 498, NEG, 1.2, dash="2,5")
    g_phi = line(x_phi, yc2 - A, x_phi, 498, MUTED, 1.1, dash="2,5")
    g_g = line(x_g, yc2 - A, x_g, 498, FIELD, 1.3, dash="2,5")

    # розмірні лінії затримок унизу (нижче орієнтирів)
    yd1, yd2 = 516, 552
    dphi = arrow(x_in, yd1, x_phi, yd1, NEG, 1.8)
    dg = arrow(x_in, yd2, x_g, yd2, FIELD, 2.0)
    lphi = text(x_phi + 12, yd1 + 5, "τ_φ  — фазова затримка (гребінь)", size=14, color=NEG, anchor="start", bold=True)
    lg = text(x_g + 12, yd2 + 5, "τ_g  — групова затримка (обвідна)", size=14, color=FIELD, anchor="start", bold=True)

    render(os.path.join(IMG, "envelope-late.svg"), W, H,
           base1, in_env_t, in_env_b, in_car, cap1, leg_env,
           base2, out_env_t, out_env_b, out_car, cap2,
           g_in, g_phi, g_g, dphi, dg, lphi, lg,
           title="Обвідна запізнюється не так, як гребені носія")


# ── Фігура 2: дві затримки як нахили на графіку фази ─────────────────────────
def fig_phase_slopes():
    W, H = 920, 560
    ox, oy = 130, 90             # початок координат (фаза вниз — від'ємна)
    axw, axh = 610, 380

    # опукла крива фази вниз: φ(x) = a·u + c·u²  (u = x−ox), у пікселях вниз
    a, c = 0.16, 0.00092
    def phy(x):
        u = x - ox
        return oy + a * u + c * u * u

    xp = ox + 372                # точка P (ω₀)
    yp = phy(xp)

    ax_w = arrow(ox, oy, ox + axw, oy, INK, 1.8)          # вісь ω
    ax_h = arrow(ox, oy, ox, oy + axh, INK, 1.8)          # вісь φ (вниз)
    lab_w = text(ox + axw - 4, oy - 12, "частота  ω", size=14, color=INK, anchor="end", bold=True)
    lab_h = text(ox - 18, oy + axh - 4, "фаза  φ", size=14, color=INK, anchor="end", bold=True)
    o_lbl = text(ox - 12, oy - 10, "0", size=13, color=MUTED, anchor="end")

    curve = wave(ox, ox + 560, phy, INK, 2.2)

    # хорда з початку координат крізь P (фазова затримка) — продовжити
    def chord_y(x):
        return oy + (yp - oy) * (x - ox) / (xp - ox)
    xc_end = ox + axw - 20
    chord = line(ox, oy, xc_end, chord_y(xc_end), NEG, 2.0)

    # дотична в P (групова затримка): нахил = a + 2c·u
    slope = a + 2 * c * (xp - ox)
    def tan_y(x):
        return yp + slope * (x - xp)
    xt1, xt2 = xp - 150, xp + 165
    tang = line(xt1, tan_y(xt1), xt2, tan_y(xt2), POS, 2.0)

    # точка P та опущені пунктири
    pdot = circle(xp, yp, 5, fill=INK, stroke=INK)
    drop_v = line(xp, oy, xp, yp, MUTED, 1.1, dash="2,5")
    drop_h = line(ox, yp, xp, yp, MUTED, 1.1, dash="2,5")
    w0 = text(xp, oy - 10, "ω₀", size=14, color=INK, bold=True)
    phi0 = text(ox - 12, yp + 5, "φ(ω₀)", size=13, color=MUTED, anchor="end")

    # короткі підписи нахилів у вільних місцях праворуч
    lt = text(xt2 + 10, tan_y(xt2) + 4, "дотична:  τ_g = −dφ/dω", size=14, color=POS, anchor="start", bold=True)
    lc = text(xc_end + 8, chord_y(xc_end) + 4, "хорда:  τ_φ = −φ/ω", size=14, color=NEG, anchor="start", bold=True)

    render(os.path.join(IMG, "phase-slopes.svg"), W, H,
           ax_w, ax_h, lab_w, lab_h, o_lbl, curve,
           chord, tang, drop_v, drop_h, pdot, w0, phi0, lt, lc,
           title="Групова затримка — дотична, фазова — хорда")


# ── Фігура 3: стала затримка vs затримка, що залежить від частоти ────────────
def fig_flat_vs_varying():
    W, H = 940, 560
    x0, xr = 90, 850
    A = 52
    per = 40.0
    f = 1.0 / per

    y1, y2, y3 = 130, 300, 470
    w_in = 60.0
    xin = x0 + 0.22 * (xr - x0)

    def env(x, xc, w):
        return math.exp(-((x - xc) / w) ** 2)

    b1 = line(x0, y1, xr, y1, MUTED, 1.0, dash="3,5")
    b2 = line(x0, y2, xr, y2, MUTED, 1.0, dash="3,5")
    b3 = line(x0, y3, xr, y3, MUTED, 1.0, dash="3,5")

    # 1 — вхідний різкий пакет
    in_w = wave(x0, xr, lambda x: y1 - A * env(x, xin, w_in) * math.cos(2 * math.pi * f * (x - xin)), INK, 1.8)

    # 2 — стала затримка: та сама форма, зсунута
    xc2 = xin + 320
    flat = wave(x0, xr, lambda x: y2 - A * env(x, xc2, w_in) * math.cos(2 * math.pi * f * (x - xc2)), FIELD, 1.8)

    # 3 — затримка залежить від частоти: розтягнутий, нижчий, «чирп»
    xc3 = xin + 330
    w3 = 150.0
    def disp(x):
        u = x - xc3
        ph = 2 * math.pi * f * u + 0.0016 * u * u   # частота росте вздовж пакета
        return y3 - 0.42 * A * env(x, xc3, w3) * math.cos(ph)
    warp = wave(x0, xr, disp, POS, 1.8)

    c1 = text(x0, y1 - 66, "Вхід — різкий імпульс", size=15, color=INK, anchor="start", bold=True)
    c2 = text(x0, y2 - 66, "Стала затримка → форма збережена, лише пізніше", size=15, color=FIELD, anchor="start", bold=True)
    c3 = text(x0, y3 - 70, "Затримка залежить від частоти → пакет розповзається", size=15, color=POS, anchor="start", bold=True)

    render(os.path.join(IMG, "flat-vs-varying.svg"), W, H,
           b1, in_w, c1, b2, flat, c2, b3, warp, c3,
           title="Що робить із імпульсом рівна й нерівна групова затримка")


# ── Фігура 4: пилка atan2 і піки наївної різниці (до вставки proj) ───────────
def ramps(xa, xb, fn, color, sw=1.9, n=1400, jump=30.0):
    """Полілінія з розривами: де |Δy| > jump — лінія рветься, стрибок пунктиром."""
    segs, cur, jumps = [], [], []
    prev = None
    for i in range(n + 1):
        x = xa + (xb - xa) * i / n
        y = fn(x)
        if prev is not None and abs(y - prev) > jump:
            segs.append(cur)
            jumps.append((x, prev, y))
            cur = []
        cur.append("%.1f,%.1f" % (x, y))
        prev = y
    segs.append(cur)
    out = []
    for s in segs:
        if len(s) > 1:
            out.append('<polyline fill="none" stroke="%s" stroke-width="%.1f" '
                       'points="%s"/>' % (color, sw, " ".join(s)))
    for (x, y1, y2) in jumps:
        out.append(line(x, y1, x, y2, MUTED, 1.0, dash="2,4"))
    return "".join(out)


def fig_wrap_spikes():
    W, H = 960, 600
    x0, xr = 118, 908
    nwrap = 4.5
    P = (xr - x0) / nwrap              # період повного оберту фази, px
    wraps = [x0 + P * m for m in range(1, 5)]

    # A — сира фаза atan2: спадні пандуси зі стрибками −π → +π
    yA0, amp = 148.0, 50.0
    def sawA(x):
        frac = ((x - x0) / P) % 1.0
        return yA0 - amp * (1.0 - 2.0 * frac)

    capA = text(x0, 62, "Сира фаза atan2 — пилка: на кожному оберті −π перескакує в +π",
                size=15, color=INK, anchor="start", bold=True)
    axA = line(x0, yA0, xr, yA0, MUTED, 1.0, dash="3,5")
    sawline = ramps(x0, xr, sawA, INK, 1.9)
    lpi = text(x0 - 14, 102, "+π", size=12, color=MUTED, anchor="end")
    lmpi = text(x0 - 14, 202, "−π", size=12, color=MUTED, anchor="end")

    # B — наївна різниця сирих фаз: правильна пряма + провал на кожному стрибку
    yB_tau, yB_zero, yB_bot = 286.0, 306.0, 420.0
    capB = text(x0, 250, "Різниця сирих фаз ÷ Δω: правильна затримка й провал на кожному стрибку",
                size=15, color=INK, anchor="start", bold=True)
    zeroB = line(x0, yB_zero, xr, yB_zero, MUTED, 1.0, dash="3,5")
    flatB = line(x0, yB_tau, xr, yB_tau, INK, 2.0)
    l0B = text(x0 - 12, yB_zero + 4, "0", size=12, color=MUTED, anchor="end")
    tauB = text(xr, yB_tau - 10, "τ_g = 15.2 нс", size=13, color=INK, anchor="end", bold=True)
    spikes = "".join(line(x, yB_tau, x, yB_bot, POS, 1.8) +
                     circle(x, yB_bot, 4, fill=POS, stroke=POS, sw=1.0) for x in wraps)
    noteB = text(x0, 446, "точка падає рівно на 1/Δf = 267 нс — на один «пропущений» оберт фази",
                 size=13, color=POS, anchor="start", bold=True)

    # C — приріст через добуток зі спряженим: та сама пряма без провалів
    yC_tau, yC_zero = 540.0, 560.0
    capC = text(x0, 486, "arg(H(k+1)·conj(H(k))) ÷ Δω: та сама пряма, стрибків нема",
                size=15, color=INK, anchor="start", bold=True)
    zeroC = line(x0, yC_zero, xr, yC_zero, MUTED, 1.0, dash="3,5")
    flatC = line(x0, yC_tau, xr, yC_tau, FIELD, 2.4)
    l0C = text(x0 - 12, yC_zero + 4, "0", size=12, color=MUTED, anchor="end")
    tauC = text(xr, yC_tau - 10, "τ_g = 15.2 нс", size=13, color=FIELD, anchor="end", bold=True)

    render(os.path.join(IMG, "wrap-spikes.svg"), W, H,
           capA, axA, sawline, lpi, lmpi,
           capB, zeroB, flatB, spikes, l0B, tauB, noteB,
           capC, zeroC, flatC, l0C, tauC,
           title="Та сама вимірювальна таблиця, три способи взяти похідну")


# ── Фігура 5: апертура — шум проти роздільності ──────────────────────────────
def fig_aperture():
    W, H = 940, 540
    ox, base, top = 118.0, 452.0, 130.0
    xend = 900.0
    y_base = 400.0
    xc = ox + 0.42 * (xend - ox)
    pk, wpk = 220.0, 24.0
    B = 62.0                            # півширина широкої апертури, px

    def true_y(x):
        return y_base - pk / (1.0 + ((x - xc) / wpk) ** 2)

    def wide_y(x):                      # усереднення по апертурі ±B
        n, s = 40, 0.0
        for i in range(n + 1):
            s += true_y(x - B + 2 * B * i / n)
        return s / (n + 1)

    def noise(i):                       # відтворюваний псевдошум
        return (math.sin(i * 12.9898) * 43758.5453) % 1.0 - 0.5

    ax_x = arrow(ox, base, xend, base, INK, 1.8)
    ax_y = arrow(ox, base, ox, top - 4, INK, 1.8)
    lab_x = text(xend - 4, base + 24, "частота ω", size=14, color=INK, anchor="end", bold=True)
    lab_y = text(ox + 12, top - 10, "групова затримка τ_g", size=14, color=INK, anchor="start", bold=True)

    truec = wave(ox + 4, xend - 10, true_y, INK, 1.6, dash="7,5")
    widec = wave(ox + 4, xend - 10, wide_y, NEG, 2.6)

    pts = []
    i = 0
    x = ox + 6
    while x < xend - 10:
        pts.append("%.1f,%.1f" % (x, true_y(x) + 26.0 * noise(i)))
        x += 6.0
        i += 1
    narrow = ('<polyline fill="none" stroke="%s" stroke-width="1.2" points="%s"/>'
              % (POS, " ".join(pts)))

    # легенда трьома рядками вгорі (з полями, поза полем графіка)
    leg = []
    for k, (col, dash, txt) in enumerate([
            (INK, "7,5", "справжня τ_g(ω)"),
            (POS, None, "вузька апертура — пік видно, але шум"),
            (NEG, None, "широка апертура — гладко, але пік з'їдено")]):
        y = 54 + 22 * k
        leg.append(line(118, y - 5, 148, y - 5, col, 2.4, dash=dash))
        leg.append(text(158, y, txt, size=13, color=col, anchor="start", bold=True))

    ap1 = arrow(xc, base + 18, xc - B, base + 18, NEG, 1.6)
    ap2 = arrow(xc, base + 18, xc + B, base + 18, NEG, 1.6)
    apl = text(xc, base + 42, "апертура B", size=13, color=NEG, bold=True)

    render(os.path.join(IMG, "aperture-tradeoff.svg"), W, H,
           ax_x, ax_y, lab_x, lab_y, widec, truec, narrow,
           "".join(leg), ap1, ap2, apl,
           title="Апертура: чим ширша, тим менше шуму — і тим більше з'їдено")


# ── Фігура (вставка hist): роз'єднані маятники Рейнольдса ───────────────────
def fig_reynolds_pendulums():
    W, H = 940, 610
    x0, x1 = 90, 860
    A = 52.0
    lam = 96.0                     # довжина хвилі носія, px
    elam = 384.0                   # довжина хвилі обвідної, px
    k = 2 * math.pi / lam
    ke = 2 * math.pi / elam
    yc1, yc2 = 210, 440
    ph2 = 0.75 * math.pi           # зсув фази між панелями

    def envf(x):
        return math.cos(ke * (x - x0))

    def prof(x, ph):
        return A * envf(x) * math.cos(k * (x - x0) - ph)

    def panel(yc, ph):
        out = [line(x0 - 14, yc, x1 + 14, yc, MUTED, 1.2)]
        out.append(wave(x0, x1, lambda x: yc - A * envf(x), FIELD, 1.6, dash="7,5"))
        out.append(wave(x0, x1, lambda x: yc + A * envf(x), FIELD, 1.6, dash="7,5"))
        n = 54
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = yc - prof(x, ph)
            out.append(line(x, yc, x, y, MUTED, 1.0))
            out.append(circle(x, y, 4.5, fill=INK, stroke=INK, sw=1.0))
        return "".join(out)

    xnode = 378.0                  # вузол обвідної
    xcr1 = 474.0                   # гребінь у верхній панелі
    xcr2 = xcr1 + ph2 / k          # той самий гребінь у нижній

    marks = [
        line(xnode, yc1 - A - 8, xnode, yc1 + A + 8, FIELD, 1.4, dash="3,4"),
        line(xnode, yc2 - A - 8, xnode, yc2 + A + 8, FIELD, 1.4, dash="3,4"),
        line(xcr1, yc1 - A - 8, xcr1, yc1 + A + 8, POS, 1.4, dash="3,4"),
        line(xcr2, yc2 - A - 8, xcr2, yc2 + A + 8, POS, 1.4, dash="3,4"),
        line(xnode, yc2 + A + 10, xnode, 548, FIELD, 1.2, dash="3,4"),
    ]

    labs = [
        text(x0 - 14, yc1 - A - 30, "мить t", size=14, anchor="start", bold=True),
        text(x0 - 14, yc2 - A - 30, "мить t + 3/8 періоду", size=14, anchor="start", bold=True),
        line(700, 126, 734, 126, FIELD, 1.8, dash="7,5"),
        text(742, 130, "обвідна — на місці", size=13, color=FIELD, anchor="start", bold=True),
        arrow(xcr1, 520, xcr2, 520, POS, 2.0),
        text(xcr2 + 12, 524, "гребінь зсунувся вперед", size=13, color=POS, anchor="start", bold=True),
        text(330, 562, "вузол: цей маятник не рухається ніколи", size=13, color=FIELD, bold=True),
    ]

    render(os.path.join(IMG, "reynolds-pendulums.svg"), W, H,
           panel(yc1, 0.0), panel(yc2, ph2), "".join(marks), "".join(labs),
           title="Роз'єднані маятники: хвиля біжить, група стоїть")


# ── Фігура (вставка hist): побудова Ламба для групової швидкості ────────────
def fig_lamb_construction():
    W, H = 900, 540
    ox, oy = 130, 450              # початок координат
    xend, ytop = 830, 110
    a = 12.0                       # c = a·√λ
    lam0 = 400.0                   # робоча довжина хвилі, px
    c0 = a * math.sqrt(lam0)       # 240
    slope = a / (2 * math.sqrt(lam0))   # dc/dλ = 0.3
    xp, yp = ox + lam0, oy - c0

    curve = wave(ox, ox + 700, lambda x: oy - a * math.sqrt(max(x - ox, 0.0)), NEG, 2.4)
    tang = line(ox, oy - (c0 - slope * lam0), ox + 680, oy - (c0 + slope * 280.0), POS, 2.0)

    ax = arrow(ox, oy, xend, oy, INK, 1.6) + arrow(ox, oy, ox, ytop, INK, 1.6)
    dash = (line(xp, yp, xp, oy, MUTED, 1.2, dash="4,4") +
            line(ox, yp, xp, yp, MUTED, 1.2, dash="4,4"))
    dots = (circle(xp, yp, 5, fill=NEG, stroke=NEG, sw=1.0) +
            circle(ox, oy - c0 / 2, 5, fill=POS, stroke=POS, sw=1.0))

    legend = (line(160, 150, 196, 150, POS, 2.0) +
              text(204, 154, "дотична до кривої", size=13, color=POS, anchor="start", bold=True) +
              line(160, 180, 196, 180, NEG, 2.4) +
              text(204, 184, "c(λ) — швидкість гребенів", size=13, color=NEG, anchor="start", bold=True))

    labs = (text(xp, oy + 26, "λ₀", size=14) +
            text(ox - 10, yp + 4, "c₀", size=14, anchor="end", color=NEG, bold=True) +
            text(ox - 10, oy - c0 / 2 + 4, "U", size=14, anchor="end", color=POS, bold=True) +
            text(xend - 6, oy + 26, "λ — довжина хвилі", size=14, anchor="end") +
            text(ox + 8, ytop + 4, "c — швидкість", size=14, anchor="start") +
            text(xp + 30, 250, "c₀ — швидкість гребенів при λ₀", size=13,
                 color=NEG, anchor="start", bold=True))

    box, _, _ = textbox(680, 395, "для c ∝ √λ відтинок рівно вдвічі\nменший за ординату: U = c₀/2",
                        size=13)

    render(os.path.join(IMG, "lamb-construction.svg"), W, H,
           ax, curve, tang, dash, dots, legend, labs, box,
           title="Побудова Ламба: групова швидкість — відтинок дотичної на осі c")


if __name__ == "__main__":
    fig_envelope_late()
    fig_phase_slopes()
    fig_flat_vs_varying()
    fig_wrap_spikes()
    fig_aperture()
    fig_reynolds_pendulums()
    fig_lamb_construction()
    print("OK: 7 fig ->", IMG)
