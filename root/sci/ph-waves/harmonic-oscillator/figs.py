# -*- coding: utf-8 -*-
"""Фігури до теми «Гармонічний осцилятор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── допоміжні деталі схеми (пружина, стіна, підлога) ─────────────────────────
def spring(x1, x2, y, coils=8, amp=12, lead=14):
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def wall(x, y1, y2, side=1):
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.4))
        yy += 14
    return "".join(out)


def ground(x1, x2, y):
    out = [line(x1, y, x2, y, color=INK, sw=3)]
    xx = x1 + 6
    while xx < x2:
        out.append(line(xx, y, xx - 12, y + 12, color=MUTED, sw=1.4))
        xx += 14
    return "".join(out)


# ── Фігура 1: дно будь-якої ями — парабола → лінійна повертальна сила ─────────
def fig_well():
    W, H = 840, 610
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Дно будь-якої гладкої ями — парабола: тому кожна рівновага «пружинить»",
                  size=16, bold=True))

    xmin, xmax = -2.1, 3.5
    L, R = 96, 560
    def PX(x):
        return L + (R - L) * (x - xmin) / (xmax - xmin)
    eqpx = PX(0.0)

    # потенціал Морзе: асиметрична гладка яма з параболічним дном
    D, a = 1.0, 0.9
    def U(x):
        return D * (1 - math.exp(-a * x)) ** 2
    k = 2 * D * a * a                       # кривина дна → жорсткість
    def Upar(x):
        return 0.5 * k * x * x
    def Ftrue(x, h=1e-4):
        return -(U(x + h) - U(x - h)) / (2 * h)
    def Flin(x):
        return -k * x

    # смуга «малого відхилення» — спільна для обох панелей (позаду всього)
    bandL, bandR = PX(-0.65), PX(0.65)
    f.append(rect(bandL, 66, bandR - bandL, 494, fill="#eef6ff", stroke='none', sw=0, rx=0))
    f.append(text((bandL + bandR) / 2, 80, "мале відхилення", size=11, color=NEG))

    N = 260

    # ── панель A: потенціальна яма U(x) ──
    aTop, aBot, Umax = 96, 260, 1.75
    def PYu(u):
        return aBot - (aBot - aTop) * (u / Umax)
    f.append(arrow(L - 16, aBot, R + 12, aBot, color=INK, sw=1.6))
    f.append(text(R + 10, aBot + 16, "x →", size=12, anchor="end"))
    f.append(arrow(eqpx, aBot + 6, eqpx, aTop - 8, color=INK, sw=1.6))
    f.append(text(eqpx + 8, aTop - 2, "U(x)  — потенціальна енергія", size=12, italic=True, anchor="start"))

    tru, par = [], []
    for i in range(N + 1):
        x = xmin + (xmax - xmin) * i / N
        tru.append((PX(x), PYu(min(Umax, U(x)))))
        if -1.55 <= x <= 1.55:
            par.append((PX(x), PYu(min(Umax, Upar(x)))))
    d = "M %.1f %.1f " % tru[0] + " ".join("L %.1f %.1f" % p for p in tru[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, INK))
    d = "M %.1f %.1f " % par[0] + " ".join("L %.1f %.1f" % p for p in par[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.3" stroke-dasharray="7,6"/>' % (d, FIELD))

    f.append(circle(eqpx, PYu(0), 4.6, fill=INK, stroke=INK, sw=1))
    f.append(text(eqpx, PYu(0) + 22, "рівновага — дно ями", size=12, color=INK))
    f.append(text(PX(1.42), PYu(Upar(1.28)) - 6, "парабола ½k·x²", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(PX(2.75), PYu(U(2.75)) + 20, "справжня яма U(x)", size=12, color=INK, anchor="middle"))

    # ── панель B: повертальна сила F(x) = −dU/dx ──
    bTop, bBot, Fmax = 316, 500, 1.7
    fmid = (bTop + bBot) / 2
    def PYf(v):
        return fmid - (fmid - bTop) * (max(-Fmax, min(Fmax, v)) / Fmax)
    f.append(arrow(L - 16, fmid, R + 12, fmid, color=INK, sw=1.6))
    f.append(text(R + 10, fmid + 16, "x →", size=12, anchor="end"))
    f.append(arrow(eqpx, bBot + 6, eqpx, bTop - 8, color=INK, sw=1.6))
    f.append(text(eqpx + 8, bTop - 2, "F(x)  — повертальна сила", size=12, italic=True, anchor="start"))

    trf, lnf = [], []
    for i in range(N + 1):
        x = xmin + (xmax - xmin) * i / N
        trf.append((PX(x), PYf(Ftrue(x))))
        lnf.append((PX(x), PYf(Flin(x))))
    d = "M %.1f %.1f " % trf[0] + " ".join("L %.1f %.1f" % p for p in trf[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, INK))
    d = "M %.1f %.1f " % lnf[0] + " ".join("L %.1f %.1f" % p for p in lnf[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.3" stroke-dasharray="7,6"/>' % (d, POS))
    f.append(text(PX(2.15), PYf(Flin(1.0)) + 4, "F = −k·x  (біля дна)", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(PX(2.65), PYf(Ftrue(2.65)) - 12, "справжня сила", size=12, color=INK, anchor="middle"))

    b, bw, bh = textbox(W / 2, 566,
                        "Біля рівноваги:  U ≈ ½k·x²   ⇒   F ≈ −k·x  — лінійна повертальна сила.  Це і є гармонічний осцилятор.",
                        size=13, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "well.svg"), W, H, *f)


# ── Фігура 2: маса на пружині → синусоїда; період не залежить від амплітуди ───
def fig_spring_motion():
    W, H = 900, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Маса на пружині рухається синусоїдою — і період той самий за будь-якого розмаху",
                  size=16, bold=True))

    # ── верх ліворуч: схема маса–пружина ──
    gy = 176
    wx = 66
    f.append(wall(wx, 92, gy))
    f.append(ground(wx, 470, gy))
    eqx = 250
    f.append(line(eqx, 96, eqx, gy, color=MUTED, sw=1.3, dash="4,6"))
    f.append(text(eqx, 88, "рівновага", size=12, color=MUTED))

    mw, mh = 78, 62
    mx = 330                       # маса відхилена праворуч
    my = gy - mh / 2
    f.append(spring(wx, mx, my))
    f.append(rect(mx, gy - mh, mw, mh, fill="#e8edf3", stroke=INK, sw=2, rx=6))
    f.append(text(mx + mw / 2, gy - mh / 2 + 8, "m", size=24, bold=True))

    cxm = mx + mw / 2
    # зміщення x
    f.append(arrow(eqx, gy + 22, cxm, gy + 22, color=INK, sw=1.5))
    f.append(text((eqx + cxm) / 2, gy + 38, "x", size=14, italic=True))
    # повертальна сила −k·x (проти відхилення)
    fy = gy - mh - 16
    f.append(arrow(cxm, fy, cxm - 88, fy, color=POS, sw=2.8))
    f.append(text(cxm - 92, fy + 4, "−k·x", size=14, bold=True, color=POS, anchor="end"))
    f.append(text(cxm - 44, fy - 12, "тягне назад", size=11, color=POS))

    # ── верх праворуч: формули ──
    b, bw, bh = textbox(700, 128,
                        "власна частота    ω = √(k/m)\nперіод                 T = 2π·√(m/k)\n\nзалежать лише від k і m —\nне від амплітуди A",
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b)

    # ── низ: x(t) — дві амплітуди, той самий період ──
    ox, rx = 80, 850
    oy = 366
    amp = 78
    tmax = 4 * math.pi          # два повні періоди (ω=1)
    def PX(t):
        return ox + (rx - ox) * (t / tmax)
    def PY(x):
        return oy - amp * x

    f.append(arrow(ox, oy, rx + 8, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy + amp + 20, ox, oy - amp - 20, color=INK, sw=1.6))
    f.append(text(rx + 6, oy + 22, "час t →", size=12, anchor="end"))
    f.append(text(ox - 10, oy - amp - 16, "x(t) = A·cos(ω·t)", size=12, italic=True, anchor="start"))

    N = 500
    big, small = [], []
    for i in range(N + 1):
        t = tmax * i / N
        big.append((PX(t), PY(1.0 * math.cos(t))))
        small.append((PX(t), PY(0.5 * math.cos(t))))
    d = "M %.1f %.1f " % big[0] + " ".join("L %.1f %.1f" % p for p in big[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    d = "M %.1f %.1f " % small[0] + " ".join("L %.1f %.1f" % p for p in small[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))

    # позначки періоду: піки обох кривих збігаються (t=0 і t=2π)
    for tp in (0.0, 2 * math.pi):
        f.append(line(PX(tp), oy - amp - 10, PX(tp), oy + amp + 10, color=MUTED, sw=1.2, dash="4,6"))
    ybar = oy + amp + 12
    f.append(arrow(PX(0), ybar, PX(2 * math.pi), ybar, color=INK, sw=1.4))
    f.append(arrow(PX(2 * math.pi), ybar, PX(0), ybar, color=INK, sw=1.4))
    f.append(text(PX(math.pi), ybar + 17, "період T — однаковий для обох", size=12, bold=True))

    # амплітуди
    f.append(line(PX(math.pi) - 0, oy, PX(math.pi), PY(-1.0), color=POS, sw=1.3, dash="3,4"))
    f.append(text(PX(math.pi) + 8, (oy + PY(-1.0)) / 2, "A", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(PX(3 * math.pi) + 6, PY(0.5 * math.cos(3 * math.pi)) - 8,
                  "малий розмах", size=12, color=NEG, anchor="start"))
    f.append(text(PX(3 * math.pi) + 6, PY(1.0 * math.cos(3 * math.pi)) + 16,
                  "великий розмах", size=12, color=POS, anchor="start"))
    return render(os.path.join(IMG, "spring-motion.svg"), W, H, *f)


# ── Фігура 3: енергія переливається — потенціальна ½kx² ↔ кінетична ½mv² ──────
def fig_energy():
    W, H = 840, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Енергія переливається: потенціальна ½k·x² ↔ кінетична ½m·v², а сума стала",
                  size=16, bold=True))

    L, R = 120, 620
    def PX(x):
        return (L + R) / 2 + (R - L) / 2 * (x / 1.25)
    base, topE = 392, 96
    k, A = 1.0, 1.0
    E = 0.5 * k * A * A
    def PY(u):
        return base - (base - topE) * (u / (E * 1.18))
    def Upar(x):
        return 0.5 * k * x * x

    # осі
    f.append(arrow(L - 20, base, R + 20, base, color=INK, sw=1.6))
    f.append(text(R + 18, base + 16, "x →", size=12, anchor="end"))
    f.append(arrow(PX(0), base + 6, PX(0), topE - 10, color=INK, sw=1.6))
    f.append(text(PX(0) + 8, topE - 2, "енергія", size=12, italic=True, anchor="start"))

    # парабола U = ½kx²
    N = 220
    par = []
    for i in range(N + 1):
        x = -1.22 + 2.44 * i / N
        par.append((PX(x), PY(Upar(x))))
    d = "M %.1f %.1f " % par[0] + " ".join("L %.1f %.1f" % p for p in par[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, NEG))
    f.append(text(PX(-1.12), PY(Upar(1.05)) - 6, "U = ½k·x²", size=13, bold=True, color=NEG, anchor="start"))

    # лінія повної енергії E
    Ey = PY(E)
    f.append(line(PX(-1.25), Ey, PX(1.25), Ey, color=MUTED, sw=1.7, dash="7,6"))
    f.append(text(PX(0), Ey - 9, "повна енергія E = ½k·A²  (стала)", size=12, bold=True, color=MUTED))

    # точки повороту x = ±A (де U = E, тіло завмирає)
    for xs in (-1.0, 1.0):
        f.append(circle(PX(xs * A), Ey, 5.0, fill="#fff", stroke=NEG, sw=2.2))
    f.append(text(PX(1.0), base + 18, "край x = +A", size=11, color=INK))
    f.append(text(PX(-1.0), base + 18, "край x = −A", size=11, color=INK))
    f.append(text(PX(0.0), base + 18, "центр x = 0", size=11, color=INK))

    # розклад енергії у проміжній точці xs
    xs = 0.62
    pe = Upar(xs)
    xcol = PX(xs)
    f.append(line(xcol, base, xcol, PY(pe), color=NEG, sw=8))            # потенціальна (низ)
    f.append(line(xcol, PY(pe), xcol, Ey, color=POS, sw=8))              # кінетична (верх)
    f.append(circle(xcol, PY(pe), 7, fill=INK, stroke=INK, sw=1))        # «кулька» на параболі
    f.append(text(xcol + 14, (base + PY(pe)) / 2, "½k·x²", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(xcol + 14, (PY(pe) + Ey) / 2, "½m·v²", size=12, bold=True, color=POS, anchor="start"))

    # підписи-висновки праворуч
    b, bw, bh = textbox(720, 150,
                        "край:\nвся енергія —\nпотенціальна,\nмаса завмерла", size=12, pad=9,
                        fill="#eaf0fd", stroke=NEG, sw=1.3, color=INK)
    f.append(b)
    b, bw, bh = textbox(720, 300,
                        "центр:\nвся енергія —\nкінетична,\nмаса найшвидша", size=12, pad=9,
                        fill="#fdecea", stroke=POS, sw=1.3, color=INK)
    f.append(b)
    return render(os.path.join(IMG, "energy.svg"), W, H, *f)


# ── Фігура 4 (вставка): зум у дно ями — розбіжність із параболою тане ─────────
def fig_zoom_parabola():
    W, H = 1000, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Звужуємо вікно навколо дна — і будь-яка гладка яма стає параболою",
                  size=16, bold=True))

    # легенда
    f.append(line(288, 54, 324, 54, color=INK, sw=2.5))
    f.append(text(330, 58, "справжня яма U(r)", size=12, anchor="start"))
    f.append(line(520, 54, 556, 54, color=FIELD, sw=2.3, dash="7,6"))
    f.append(text(562, 58, "парабола ½·k·(r−r₀)²", size=12, anchor="start"))

    # яма Леннард-Джонса у зведених одиницях: r₀ = 1, U/ε = r⁻¹² − 2·r⁻⁶ (дно −1, U″ = 72)
    def dU(r):
        return r ** -12 - 2.0 * r ** -6 + 1.0

    def par(d):
        return 36.0 * d * d

    ptop, ph, pw = 98, 232, 292
    for i, half in enumerate((0.30, 0.06, 0.012)):
        x0 = 42 + i * 312
        f.append(rect(x0, ptop, pw, ph, fill="#fbfcfd", stroke=LINE, sw=1.3, rx=4))
        pl, pr = x0 + 26, x0 + pw - 20
        pb, pt = ptop + ph - 30, ptop + 22
        ymax = max(par(half), dU(1 + half)) * 1.55

        def PX(r, pl=pl, pr=pr, half=half):
            return pl + (pr - pl) * (r - (1 - half)) / (2 * half)

        def PY(u, pb=pb, pt=pt, ymax=ymax):
            return pb - (pb - pt) * (u / ymax)

        f.append(line(pl - 8, pb, pr + 8, pb, color=INK, sw=1.4))
        f.append(line(PX(1.0), pb + 5, PX(1.0), pt - 8, color=MUTED, sw=1.1, dash="4,5"))
        f.append(text(PX(1.0), pb + 19, "r₀", size=12, color=MUTED))

        N = 420
        real, para = [], []
        for j in range(N + 1):
            r = (1 - half) + 2 * half * j / N
            if dU(r) <= ymax:
                real.append((PX(r), PY(dU(r))))
            para.append((PX(r), PY(min(par(r - 1.0), ymax))))
        d = "M %.1f %.1f " % para[0] + " ".join("L %.1f %.1f" % p for p in para[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.3" stroke-dasharray="7,6"/>' % (d, FIELD))
        d = "M %.1f %.1f " % real[0] + " ".join("L %.1f %.1f" % p for p in real[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, INK))

        f.append(text(x0 + pw / 2, ptop - 13, "вікно  r₀ ± %g·r₀" % half, size=13, bold=True))
        dev = max(abs(dU(1 + half) - par(half)), abs(dU(1 - half) - par(half))) / par(half)
        f.append(text(x0 + pw / 2, ptop + ph + 27,
                      "похибка параболи на краю: %.0f %%" % (dev * 100), size=12, color=POS))

    b, bw, bh = textbox(W / 2, 420,
                        "Вікно вужче вп'ятеро (±0.06 → ±0.012·r₀) — похибка впала вшестеро (56 % → 9 %):\n"
                        "вона тане разом із вікном. Ось у якому сенсі дно ями «є» парабола.",
                        size=13, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "zoom-parabola.svg"), W, H, *f)


# ── Фігура 5 (вставка): знак другої похідної вирішує долю рівноваги ───────────
def _quartic_traj(A, tmax, n=1600):
    """ẍ = −x³ (яма ¼x⁴) — чисельно, RK4."""
    x, v, dt = A, 0.0, tmax / n
    out = [(0.0, x)]
    for i in range(n):
        k1x, k1v = v, -x ** 3
        k2x, k2v = v + 0.5 * dt * k1v, -(x + 0.5 * dt * k1x) ** 3
        k3x, k3v = v + 0.5 * dt * k2v, -(x + 0.5 * dt * k2x) ** 3
        k4x, k4v = v + dt * k3v, -(x + dt * k3x) ** 3
        x += dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        out.append((dt * (i + 1), x))
    return out


def fig_curvature_sign():
    W, H = 1000, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Долю рівноваги вирішує знак другої похідної U″ у самій точці рівноваги",
                  size=16, bold=True))

    cols = [
        ("U″ > 0  —  мінімум", "U ≈ ½·k·x²,   k = U″ > 0", FIELD,
         lambda x: 0.5 * 4.0 * x * x, "x(t) = A·cos(ω·t),  ω = √(k/m)",
         "період не залежить від розмаху"),
        ("U″ < 0  —  максимум", "U ≈ −½·|k|·x²", POS,
         lambda x: -0.5 * 4.0 * x * x, "x(t) ~ e^(t/τ),  τ = √(m/|k|)",
         "не коливання, а втеча"),
        ("U″ = 0  —  виродження", "U ≈ ¼·γ·x⁴", NEG,
         lambda x: 0.25 * 9.0 * x ** 4, "розмах більший — період КОРОТШИЙ",
         "T ∝ 1/A: ізохронності немає"),
    ]

    for i, (head, formula, col, Ufun, mlab, note) in enumerate(cols):
        x0 = 40 + i * 320
        cx = x0 + 150
        f.append(text(cx, 62, head, size=14, bold=True, color=col))
        b, bw, bh = textbox(cx, 92, formula, size=13, pad=8, fill=FILL, stroke=col, sw=1.3)
        f.append(b)

        # верхня панель: форма ями
        utop, ubot = 122, 250
        f.append(rect(x0, utop, 300, ubot - utop, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=4))
        umid = (utop + ubot) / 2 + 32
        f.append(line(x0 + 14, umid, x0 + 286, umid, color=MUTED, sw=1.1))

        def UX(x, x0=x0):
            return x0 + 150 + 130 * x

        def UY(u, umid=umid):
            return umid - 46 * u

        pts = []
        for j in range(161):
            xx = -1.0 + 2.0 * j / 160
            yy = UY(Ufun(xx))
            if utop + 6 <= yy <= ubot - 6:
                pts.append((UX(xx), yy))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))
        f.append(circle(UX(0), UY(0), 5.0, fill="#fff", stroke=INK, sw=2))

        # нижня панель: рух x(t)
        mtop, mbot = 286, 402
        f.append(rect(x0, mtop, 300, mbot - mtop, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=4))
        my = (mtop + mbot) / 2
        f.append(line(x0 + 14, my, x0 + 286, my, color=MUTED, sw=1.1))
        f.append(text(x0 + 292, my - 8, "t", size=12, color=MUTED, anchor="end", italic=True))

        def MX(t, x0=x0, tmax=16.0):
            return x0 + 16 + 268 * t / tmax

        def MY(x, my=my):
            return my - 44 * x

        curves = []
        if i == 0:
            curves.append(([(MX(16.0 * s / 300), MY(math.cos(2 * math.pi * (16.0 * s / 300) / 6.0)))
                            for s in range(301)], col, 2.6))
        elif i == 1:
            curves.append(([(MX(16.0 * s / 300), MY(0.055 * math.cosh(0.62 * (16.0 * s / 300))))
                            for s in range(301) if 0.055 * math.cosh(0.62 * (16.0 * s / 300)) <= 1.15], col, 2.6))
        else:
            for A, cc in ((1.0, col), (0.5, MUTED)):
                tr = _quartic_traj(A, 16.0)
                curves.append(([(MX(t), MY(x)) for t, x in tr[::4]], cc, 2.6))
        for pts2, cc, sw in curves:
            d = "M %.1f %.1f " % pts2[0] + " ".join("L %.1f %.1f" % p for p in pts2[1:])
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, cc, sw))

        f.append(text(cx, 428, mlab, size=12))
        f.append(text(cx, 450, note, size=12, bold=True, color=col))

    b, bw, bh = textbox(W / 2, 478,
                        "Гармонічне коливання дає лише ліва колонка — і тільки якщо U″ у точці рівноваги не нуль.",
                        size=13, pad=8, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "curvature-sign.svg"), W, H, *f)


# ── Фігура 6 (вставка): наскільки «мале» мале — період маятника від розмаху ───
def _agm(a, b, n=8):
    for _ in range(n):
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return a


def fig_period_vs_amplitude():
    W, H = 900, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ціна наближення: наскільки період маятника відходить від гармонічного",
                  size=16, bold=True))

    L, R, TOP, BOT = 96, 780, 88, 400
    ylo, yhi = 1.0, 1.40
    thmax = 120.0

    def PX(th):
        return L + (R - L) * th / thmax

    def PY(y):
        return BOT - (BOT - TOP) * (y - ylo) / (yhi - ylo)

    # табличка значень (рахуємо наперед — сітка обійде її стороною)
    tab, tw, th_ = textbox(300, 250,
                           "розмах θ₀      період довший на\n"
                           "   10°                    +0.19 %\n"
                           "   30°                    +1.7 %\n"
                           "   90°                    +18 %",
                           size=13, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    tabL, tabR = 300 - tw / 2 - 8, 300 + tw / 2 + 8
    tabT, tabB = 250 - th_ / 2 - 6, 250 + th_ / 2 + 6

    # сітка (горизонталі розриваються там, де стоїть табличка)
    for gy in (1.0, 1.1, 1.2, 1.3, 1.4):
        y = PY(gy)
        if tabT <= y <= tabB:
            f.append(line(L, y, tabL, y, color="#e5e7eb", sw=1.1))
            f.append(line(tabR, y, R, y, color="#e5e7eb", sw=1.1))
        else:
            f.append(line(L, y, R, y, color="#e5e7eb", sw=1.1))
        f.append(text(L - 12, y + 5, "%.1f" % gy, size=12, color=MUTED, anchor="end"))
    for gt in (0, 30, 60, 90, 120):
        f.append(line(PX(gt), BOT, PX(gt), BOT + 6, color=INK, sw=1.2))
        f.append(text(PX(gt), BOT + 22, "%d°" % gt, size=12, color=MUTED))
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
    f.append(line(L, BOT, R + 10, BOT, color=INK, sw=1.5))
    f.append(text(L - 6, TOP - 14, "T / T₀", size=13, italic=True, anchor="start"))
    f.append(text(R - 2, BOT - 16, "розмах θ₀ →", size=12, anchor="end"))

    ex, se = [], []
    for j in range(241):
        th = thmax * j / 240
        rad = math.radians(th)
        ex.append((PX(th), PY(1.0 / _agm(1.0, math.cos(rad / 2)))))
        se.append((PX(th), PY(1.0 + rad * rad / 16.0)))
    f.append(line(L, PY(1.0), R, PY(1.0), color=NEG, sw=2.6))
    d = "M %.1f %.1f " % se[0] + " ".join("L %.1f %.1f" % p for p in se[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,6"/>' % (d, FIELD))
    d = "M %.1f %.1f " % ex[0] + " ".join("L %.1f %.1f" % p for p in ex[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, INK))

    for th in (30.0, 90.0):
        f.append(circle(PX(th), PY(1.0 / _agm(1.0, math.cos(math.radians(th) / 2))), 5.0,
                        fill="#fff", stroke=INK, sw=2.2))

    # легенда
    f.append(line(120, 102, 156, 102, color=NEG, sw=2.6))
    f.append(text(162, 106, "гармонічне наближення: T = T₀", size=12, anchor="start"))
    f.append(line(120, 124, 156, 124, color=FIELD, sw=2.4, dash="7,6"))
    f.append(text(162, 128, "поправка  T = T₀·(1 + θ₀²/16)", size=12, anchor="start"))
    f.append(line(120, 146, 156, 146, color=INK, sw=2.8))
    f.append(text(162, 150, "точний період (еліптичний інтеграл)", size=12, anchor="start"))

    f.append(tab)

    b, bw, bh = textbox(W / 2, 455,
                        "Маятниковий годинник: розмах спав із 5° до 3° — період скоротився на 3·10⁻⁴ від себе.\n"
                        "Це +26 секунд за добу: похибка «малих коливань» видима на око.",
                        size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "period-vs-amplitude.svg"), W, H, *f)


# ── Фігура 7 (вставка hist): щоки Гюйгенса — коло проти циклоїди ─────────────
def fig_hist_cycloid():
    W, H = 940, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Гюйгенс проти колового ходу: щоки, які змушують нитку йти циклоїдою",
                  size=16, bold=True))

    # ── ліва панель: пристрій ────────────────────────────────────────────────
    f.append(text(245, 58, "Щоки біля підвісу", size=13, bold=True))
    Px, Py, Lc = 245.0, 80.0, 235.0

    # довідкова дуга кола (шлях звичайного маятника)
    arc = []
    for j in range(91):
        a = math.radians(-45 + 90.0 * j / 90)
        arc.append((Px + Lc * math.sin(a), Py + Lc * math.cos(a)))
    d = "M %.1f %.1f " % arc[0] + " ".join("L %.1f %.1f" % p for p in arc[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="6,6"/>' % (d, MUTED))

    # щоки: дві короткі циклоїди від точки підвісу
    rc, tmax = 15.0, 1.6
    for side in (1, -1):
        pts = [(Px + side * rc * (t * tmax / 24 + math.sin(t * tmax / 24)),
                Py + rc * (1 - math.cos(t * tmax / 24))) for t in range(25)]
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (d, FIELD))

    # нитка, обгорнута об праву щоку, і тягарець на широкому розмаху
    cx_end = Px + rc * (tmax + math.sin(tmax))
    cy_end = Py + rc * (1 - math.cos(tmax))
    ux, uy = 1 + math.cos(tmax), math.sin(tmax)
    un = math.hypot(ux, uy)
    rest = Lc - 4 * rc * math.sin(tmax / 2)
    bx, by = cx_end + rest * ux / un, cy_end + rest * uy / un
    wrap = [(Px + rc * (t * tmax / 24 + math.sin(t * tmax / 24)),
             Py + rc * (1 - math.cos(t * tmax / 24))) for t in range(25)] + [(bx, by)]
    d = "M %.1f %.1f " % wrap[0] + " ".join("L %.1f %.1f" % p for p in wrap[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, INK))
    f.append(circle(bx, by, 11, fill="#fdecea", stroke=POS, sw=2.4))

    # нитка й тягарець у спокої
    f.append(line(Px, Py, Px, Py + Lc, color=INK, sw=2))
    f.append(circle(Px, Py + Lc, 11, fill=FILL, stroke=INK, sw=2.2))
    f.append(circle(Px, Py, 4.5, fill=INK, stroke=INK, sw=1))

    f.append(line(298, 82, 287, 92, color=MUTED, sw=1.2))
    f.append(text(302, 78, "циклоїдні щоки", size=11, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(52, 358, 386, 80,
                    "На широкій дузі нитка лягає на щоку й тим сама вкорочується,\n"
                    "тож тягарець іде вже не колом, а циклоїдою — і період\n"
                    "перестає залежати від розмаху. Пунктир — шлях без щік.",
                    size=11.5, pad=9, fill=FILL, stroke=LINE, sw=1.3))

    # ── права панель: коло проти циклоїди ────────────────────────────────────
    f.append(text(695, 58, "Коло проти циклоїди", size=13, bold=True))
    Ox, Oy, r = 695.0, 340.0, 57.0

    cyc = []
    for j in range(121):
        u = -math.pi + 2 * math.pi * j / 120
        cyc.append((Ox + r * (u + math.sin(u)), Oy - r * (1 - math.cos(u))))
    Rc = 4 * r
    cir = []
    for j in range(121):
        x = -179.0 + 358.0 * j / 120
        cir.append((Ox + x, Oy - (Rc - math.sqrt(Rc * Rc - x * x))))
    d = "M %.1f %.1f " % cir[0] + " ".join("L %.1f %.1f" % p for p in cir[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,6"/>' % (d, MUTED))
    d = "M %.1f %.1f " % cyc[0] + " ".join("L %.1f %.1f" % p for p in cyc[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, FIELD))
    f.append(circle(Ox, Oy, 5.5, fill="#fff", stroke=INK, sw=2))

    f.append(line(560, 101, 596, 101, color=MUTED, sw=2.4, dash="7,6"))
    f.append(text(602, 105, "коло — шлях звичайного маятника", size=12, anchor="start"))
    f.append(line(560, 128, 596, 128, color=FIELD, sw=2.8))
    f.append(text(602, 132, "циклоїда — рівні часи з будь-якої висоти", size=12, anchor="start"))

    f.append(fitbox(500, 358, 400, 80,
                    "Біля самого низу криві збігаються — саме тому малий\n"
                    "розмах і без щік майже ізохронний. Розходяться вони\n"
                    "на краях: циклоїда крутіша, і це вирівнює час спуску.",
                    size=11.5, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.3))
    return render(os.path.join(IMG, "hist-cycloid.svg"), W, H, *f)


# ── Фігура 8 (вставка hist): чим осцилятор ставав на кожному кроці ───────────
def fig_hist_timeline():
    W, H = 960, 812
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Одне поняття, десять перевтілень", size=17, bold=True))
    f.append(text(W / 2, 62, "праворуч — чим гармонічний осцилятор ставав після кожного кроку",
                 size=12, color=MUTED))

    rows = [
        ("1602", "Ґалілей — лист із Падуї до даль Монте",
         "період — властивість маятника, а не розмаху", "РІЧ", FIELD, "#eafaf1"),
        ("1636", "Мерсенн — «Harmonie universelle»",
         "тон уперше стає числом: f = (1/2L)·√(F/μ)", "ЧИСЛО", FIELD, "#eafaf1"),
        ("1657", "Гюйгенс — маятниковий годинник, потім циклоїда",
         "15 хв/добу → 15 с/добу; коло не ізохронне", "КРИВА", FIELD, "#eafaf1"),
        ("1678", "Гук — «ut tensio, sic vis»",
         "повертальна сила без участі тяжіння", "ПРУЖНІСТЬ", FIELD, "#eafaf1"),
        ("1687", "Ньютон — «Principia»",
         "сила перекладається у прискорення", "ЗАКОН", NEG, "#eaf0fd"),
        ("1739", "Ейлер — «De novo genere oscillationum»",
         "резонанс знайдено на папері, а не в досліді", "РІВНЯННЯ", NEG, "#eaf0fd"),
        ("1788", "Лаґранж — «Mécanique analytique»",
         "будь-яка система біля рівноваги = сума мод", "МОДИ", NEG, "#eaf0fd"),
        ("1853", "Томсон (Кельвін) — теорія розряду банки",
         "контур коливається зовсім без маси", "ПОЛЕ", POS, "#fdecea"),
        ("1900", "Планк — резонатори в стінках чорного тіла",
         "енергія міняється порціями E = h·ν", "КВАНТ", POS, "#fdecea"),
        ("1925", "Гайзенберг — матрична механіка",
         "Eₙ = ħω(n + ½): найнижчий стан уже дрижить", "НУЛЬОВА ЕНЕРГІЯ", POS, "#fdecea"),
    ]

    y0, step, lane = 100.0, 72.0, 250.0
    f.append(line(lane, y0 - 22, lane, y0 + step * (len(rows) - 1) + 24, color=MUTED, sw=2))
    for i, (year, who, what, tag, col, fill) in enumerate(rows):
        y = y0 + i * step
        f.append(text(225, y + 5, year, size=14, bold=True, color=col, anchor="end"))
        f.append(circle(lane, y, 7, fill=fill, stroke=col, sw=2.4))
        f.append(text(282, y + 5, who, size=13, bold=True, anchor="start"))
        f.append(text(282, y + 26, what, size=12, color=MUTED, anchor="start"))
        b, bw, bh = textbox(800, y + 6, tag, size=12, pad=10, fill=fill, stroke=col,
                            sw=1.4, color=col, bold=True, min_w=150)
        f.append(b)
    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_well(), fig_spring_motion(), fig_energy(),
          fig_zoom_parabola(), fig_curvature_sign(), fig_period_vs_amplitude(),
          fig_hist_cycloid(), fig_hist_timeline()]
    print("written:")
    for p in ps:
        print("  ", p)
