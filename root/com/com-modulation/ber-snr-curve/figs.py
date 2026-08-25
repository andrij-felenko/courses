# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

UNC = "#6b7280"     # без коду / базова крива
COD = "#c0392b"     # з кодуванням / гаряче
WALL = "#27ae60"    # межа Шеннона
BLUE = "#2457d6"


def polyline(pts, color=INK, sw=2.2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


def fill_area(pts, baseline_y, color, opacity=0.30):
    if not pts:
        return ""
    d = "M %.1f %.1f " % (pts[0][0], baseline_y)
    for x, y in pts:
        d += "L %.1f %.1f " % (x, y)
    d += "L %.1f %.1f Z" % (pts[-1][0], baseline_y)
    return '<path d="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (d, color, opacity)


def ber_bpsk(ebn0_db):
    e = 10 ** (ebn0_db / 10.0)
    return 0.5 * math.erfc(math.sqrt(e))


def ber_mqam(M, ebn0_db):
    k = math.log2(M)
    e = 10 ** (ebn0_db / 10.0)
    x = math.sqrt(3.0 * k / (M - 1) * e)
    return (4.0 / k) * (1 - 1 / math.sqrt(M)) * 0.5 * math.erfc(x / math.sqrt(2))


def ber_rayleigh(ebn0_db):
    g = 10 ** (ebn0_db / 10.0)
    return 0.5 * (1 - math.sqrt(g / (1 + g)))


# ── waterfall: головна крива + виграш кодування + межа Шеннона ────────────────

def fig_waterfall():
    W, H = 760, 520
    p = []
    px0, px1 = 104, 690
    py0, py1 = 66, 372
    smin, smax = -2.0, 12.0
    emin, emax = -1.0, -7.0     # верх 10⁻¹ … низ 10⁻⁷

    def X(s):
        return px0 + (s - smin) / (smax - smin) * (px1 - px0)

    def Y(e):
        return py0 + (emin - e) / (emin - emax) * (py1 - py0)

    # сітка декад + підписи Y
    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 12, y + 4, "10⁻%d" % k, size=11.5, color=MUTED, anchor="end"))
    # осі
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    for s in range(-2, 13, 2):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 21, str(s), size=11.5, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 44, "Eb/N0 , дБ", size=13, color=INK))
    p.append(text(px0 - 62, (py0 + py1) / 2, "BER", size=13, color=INK, bold=True))

    # межа Шеннона (−1.59 дБ)
    xs = X(-1.59)
    p.append(line(xs, py0, xs, py1, color=WALL, sw=2.2, dash="6 5"))
    p.append(text(xs + 6, py0 + 12, "межа Шеннона  −1.6 дБ", size=11, color=WALL,
                  bold=True, anchor="start"))

    # цільова BER = 10⁻⁵
    yt = Y(-5)
    p.append(line(px0, yt, px1, yt, color=INK, sw=1.1, dash="2 4"))
    p.append(text(px1 - 6, yt - 7, "цільова BER 10⁻⁵", size=11, color=INK, anchor="end", italic=True))

    # крива без коду (точна BPSK)
    unc = []
    s = smin
    while s <= smax + 1e-9:
        b = ber_bpsk(s)
        if b > 0:
            e = math.log10(b)
            if emax - 0.15 <= e <= emin + 0.02:
                unc.append((X(s), Y(e)))
        s += 0.12
    p.append(polyline(unc, color=UNC, sw=2.8))

    # крива з кодуванням (схематичний крутіший водоспад ~4.5 дБ)
    cod = [(2.0, -1), (3.0, -2.0), (3.8, -3.4), (4.3, -5.0), (4.6, -6.6)]
    p.append(polyline([(X(s), Y(e)) for s, e in cod], color=COD, sw=3.0))

    # точки перетину з цільовою BER + опускання на вісь
    for xv, col, lbl in [(9.6, UNC, "9.6"), (4.5, COD, "4.5")]:
        p.append(circle(X(xv), yt, 4.2, fill=col, stroke=col, sw=1))
        p.append(line(X(xv), yt, X(xv), py1, color=col, sw=1.0, dash="2 3"))
        p.append(text(X(xv), py1 + 34, lbl + " дБ", size=10.5, color=col, bold=True))

    # стрілка виграшу кодування (двобічна) на рівні цільової BER
    ya = yt - 16
    p.append(line(X(4.5), yt, X(4.5), ya, color=INK, sw=1.0))
    p.append(line(X(9.6), yt, X(9.6), ya, color=INK, sw=1.0))
    p.append(arrow(X(6.9), ya, X(4.6), ya, color=INK, sw=1.6))
    p.append(arrow(X(6.9), ya, X(9.5), ya, color=INK, sw=1.6))
    p.append(text(X(7.05), ya - 7, "виграш кодування ≈ 5 дБ", size=11, color=INK, bold=True))

    # легенда рядком
    ly = py1 + 66
    items = [("без коду (BPSK)", UNC), ("з кодуванням", COD)]
    lx = px0 + 30
    for label, col in items:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3.0))
        p.append(text(lx + 32, ly + 4, label, size=12, color=INK, anchor="start"))
        lx += 32 + text_width(label, 12) + 46

    render(os.path.join(OUT, "waterfall.svg"), W, H, *p,
           title="Крива надійності: водоспад BER проти Eb/N0")


# ── decision: дві гаусові гірки, поріг і хвіст-перекриття ─────────────────────

def fig_decision():
    W, H = 800, 430
    p = []

    def panel(ox, sigma, title):
        pw, ph = 300, 250
        oy = 92
        bx0, bx1 = ox + 20, ox + pw - 20      # x-домен графіка
        by = oy + ph                           # базова лінія
        top = oy + 24
        mu = 1.0
        xspan = 3.2                            # від −xspan..+xspan (в одиницях сигналу)

        def PX(v):
            return (bx0 + bx1) / 2 + v / xspan * (bx1 - bx0) / 2

        def PY(g):                             # g у 0..1 (нормована висота)
            return by - g * (by - top)

        amp = 1.0

        def gauss(v, m):
            return amp * math.exp(-((v - m) ** 2) / (2 * sigma ** 2))

        # осьова лінія
        p.append(line(bx0 - 6, by, bx1 + 6, by, color=INK, sw=1.4))
        # поріг рішення в 0
        thr = PX(0)
        p.append(line(thr, top - 6, thr, by, color=INK, sw=1.4, dash="4 4"))
        p.append(text(thr, top - 12, "поріг", size=11, color=INK, bold=True))

        # заштрихований хвіст: +1 ліворуч від порога, −1 праворуч
        def curve(m, a, b, step=0.04):
            pts = []
            v = a
            while v <= b + 1e-9:
                pts.append((PX(v), PY(gauss(v, m))))
                v += step
            return pts

        p.append(fill_area(curve(+mu, -xspan, 0), by, COD, 0.32))
        p.append(fill_area(curve(-mu, 0, xspan), by, BLUE, 0.32))

        # самі дзвоники
        p.append(polyline(curve(-mu, -xspan, xspan), color=BLUE, sw=2.4))
        p.append(polyline(curve(+mu, -xspan, xspan), color=COD, sw=2.4))

        # центри
        p.append(text(PX(-mu), by + 18, "−1", size=12, color=BLUE, bold=True))
        p.append(text(PX(+mu), by + 18, "+1", size=12, color=COD, bold=True))

        p.append(text((bx0 + bx1) / 2, oy - 8, title, size=12.5, color=INK, bold=True))

    panel(40, 0.92, "низьке Eb/N0 — гірки близько")
    panel(460, 0.46, "високе Eb/N0 — гірки нарізно")

    p.append(text(W / 2, H - 20,
                  "помилка = заштрихований хвіст за порогом; розсунеш гірки — хвіст спадає як e^(−x²/2)",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Чому водоспад крутий: поріг рішення й хвіст гаусіани")


# ── modulation-family: BPSK vs 16-QAM vs 64-QAM ──────────────────────────────

def fig_modulation():
    W, H = 760, 500
    p = []
    px0, px1 = 96, 690
    py0, py1 = 62, 360
    smin, smax = 0.0, 20.0
    emin, emax = -1.0, -7.0

    def X(s):
        return px0 + (s - smin) / (smax - smin) * (px1 - px0)

    def Y(e):
        return py0 + (emin - e) / (emin - emax) * (py1 - py0)

    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 12, y + 4, "10⁻%d" % k, size=11.5, color=MUTED, anchor="end"))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    for s in range(0, 21, 4):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 21, str(s), size=11.5, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 44, "Eb/N0 , дБ", size=13, color=INK))
    p.append(text(px0 - 60, (py0 + py1) / 2, "BER", size=13, color=INK, bold=True))

    def draw(fn, color, sw=2.8):
        pts = []
        s = smin
        while s <= smax + 1e-9:
            b = fn(s)
            if b > 0:
                e = math.log10(b)
                if emax - 0.15 <= e <= emin + 0.02:
                    pts.append((X(s), Y(e)))
            s += 0.12
        p.append(polyline(pts, color=color, sw=sw))

    draw(ber_bpsk, UNC, 2.8)
    draw(lambda s: ber_mqam(16, s), COD, 2.8)
    draw(lambda s: ber_mqam(64, s), BLUE, 2.8)

    # позначки біля кривих на рівні 10⁻⁵
    for fn, col, lbl, guess in [(ber_bpsk, UNC, "BPSK / QPSK", 9.6),
                                 (lambda s: ber_mqam(16, s), COD, "16-QAM", 13.4),
                                 (lambda s: ber_mqam(64, s), BLUE, "64-QAM", 17.8)]:
        p.append(text(X(guess), Y(-5.6), lbl, size=11.5, color=col, bold=True))

    p.append(text((px0 + px1) / 2, py1 + 74,
                  "більше біт на символ → водоспад зсувається праворуч (треба більше Eb/N0)",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "modulation-family.svg"), W, H, *p,
           title="Родина кривих: щільніша модуляція коштує децибелів")


# ── mc-overlay: виміряні точки Монте-Карло на теоретичній кривій ──────────────

def fig_mc_overlay():
    W, H = 800, 560
    p = []
    px0, px1 = 108, 700
    py0, py1 = 70, 400
    smin, smax = -0.5, 12.0
    emin, emax = -1.0, -7.0

    def X(s):
        return px0 + (s - smin) / (smax - smin) * (px1 - px0)

    def Y(e):
        return py0 + (emin - e) / (emin - emax) * (py1 - py0)

    def Yb(ber):
        return Y(math.log10(ber))

    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 12, y + 4, "10⁻%d" % k, size=11.5, color=MUTED, anchor="end"))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    for s in range(0, 13, 2):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 21, str(s), size=11.5, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 44, "Eb/N0 , дБ", size=13, color=INK))
    p.append(text(px0 - 66, (py0 + py1) / 2, "BER", size=13, color=INK, bold=True))

    # теоретична крива
    th = []
    s = smin
    while s <= smax + 1e-9:
        b = ber_bpsk(s)
        if b > 0:
            e = math.log10(b)
            if emax - 0.1 <= e <= emin + 0.02:
                th.append((X(s), Y(e)))
        s += 0.1
    p.append(polyline(th, color=UNC, sw=2.6))
    p.append(text(X(0.2), Yb(ber_bpsk(0.9)) - 24, "теорія  Q(√(2·Eb/N0))",
                  size=11.5, color=UNC, anchor="start", italic=True))

    # поріг надійності: BER = 100 / 10⁶ = 10⁻⁴
    yr = Yb(1e-4)
    p.append(line(px0, yr, px1, yr, color=FIELD, sw=1.6, dash="6 5"))
    p.append(text(px1 - 6, yr - 7, "поріг 100 помилок за N = 10⁶ біт",
                  size=10.5, color=FIELD, anchor="end", bold=True))

    def whisker(sx, ber, K, col, filled=True):
        x = X(sx)
        rel = 1.96 / math.sqrt(K)
        top = ber * (1 + rel)
        bot = ber * max(1e-9, 1 - rel)
        p.append(line(x, Yb(top), x, Yb(bot), color=col, sw=1.6))
        p.append(line(x - 4, Yb(top), x + 4, Yb(top), color=col, sw=1.6))
        p.append(line(x - 4, Yb(bot), x + 4, Yb(bot), color=col, sw=1.6))
        if filled:
            p.append(circle(x, Yb(ber), 4.4, fill=col, stroke=col, sw=1))
        else:
            p.append(circle(x, Yb(ber), 4.4, fill=BG, stroke=col, sw=2))

    # надійні точки (багато помилок) — сидять на теорії
    for sx in [0, 2, 4, 6, 8]:
        whisker(sx, ber_bpsk(sx), 1200, FIELD, True)

    # голодні точки (мало помилок) — розсипаються геть від теорії
    whisker(9.0, 5.3e-5, 28, COD, True)      # теорія 3.4e-5
    whisker(10.0, 8.4e-6, 4, COD, True)      # теорія 3.9e-6

    # 11 дБ: нуль помилок → хибне «дно» на рівні 1/N
    xf, yf = X(11.0), Yb(1e-6)
    p.append(circle(xf, yf, 5, fill=BG, stroke=COD, sw=2))
    p.append(arrow(xf, yf + 7, xf, yf + 33, color=COD, sw=1.8))
    p.append(text(xf, yf - 12, "0 помилок", size=10.5, color=COD, bold=True))
    p.append(text(xf, yf + 49, "хибне «дно» 1/N", size=10, color=COD))

    ly = py1 + 72
    p.append(circle(px0 + 22, ly, 4.4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(px0 + 34, ly + 4, "≥ 100 помилок — точці можна вірити",
                  size=11.5, color=INK, anchor="start"))
    p.append(circle(px0 + 22, ly + 22, 4.4, fill=COD, stroke=COD, sw=1))
    p.append(text(px0 + 34, ly + 26, "мало помилок — точка розсипається й бреше",
                  size=11.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "mc-overlay.svg"), W, H, *p,
           title="Виміряні точки Монте-Карло на теоретичній кривій")


# ── mc-precision: лійка точності 1/√K ────────────────────────────────────────

def fig_mc_precision():
    W, H = 780, 470
    p = []
    px0, px1 = 104, 700
    py0, py1 = 72, 360
    kmin, kmax = 8.0, 1300.0
    lk0, lk1 = math.log10(kmin), math.log10(kmax)

    def X(K):
        return px0 + (math.log10(K) - lk0) / (lk1 - lk0) * (px1 - px0)

    ymin, ymax = 0.5, 1.5

    def Y(r):
        return py1 - (r - ymin) / (ymax - ymin) * (py1 - py0)

    for r in [0.6, 0.8, 1.0, 1.2, 1.4]:
        y = Y(r)
        p.append(line(px0, y, px1, y, color="#eef1f4", sw=1.0))
        p.append(text(px0 - 10, y + 4, ("%.1f" % r).replace(".", ","),
                      size=11, color=MUTED, anchor="end"))
    p.append(line(px0, Y(1.0), px1, Y(1.0), color=INK, sw=1.6))
    p.append(text(px1 - 4, Y(1.0) - 8, "істинна BER", size=11, color=INK,
                  anchor="end", italic=True))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))

    for K in [10, 30, 100, 300, 1000]:
        x = X(K)
        p.append(line(x, py1, x, py1 + 5, color=INK, sw=1.2))
        p.append(text(x, py1 + 21, str(K), size=11.5, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 46, "K — число зібраних помилок",
                  size=13, color=INK))
    p.append(text(px0 - 62, (py0 + py1) / 2, "оцінка / істина",
                  size=12, color=INK, bold=True))

    up, dn = [], []
    K = kmin
    while K <= kmax + 1e-9:
        rel = 1 / math.sqrt(K)
        up.append((X(K), Y(min(ymax, 1 + rel))))
        dn.append((X(K), Y(max(ymin, 1 - rel))))
        K *= 1.03
    poly = up + dn[::-1]
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.08" stroke="none"/>' % (pts, BLUE))
    p.append(polyline(up, color=BLUE, sw=1.6, dash="4 4"))
    p.append(polyline(dn, color=BLUE, sw=1.6, dash="4 4"))

    for K, lbl in [(10, "±32 %"), (30, "±18 %"), (100, "±10 %"),
                   (300, "±5,8 %"), (1000, "±3,2 %")]:
        x = X(K)
        rel = 1 / math.sqrt(K)
        p.append(line(x, Y(1 + rel), x, Y(1 - rel), color=BLUE, sw=2.2))
        p.append(line(x - 4, Y(1 + rel), x + 4, Y(1 + rel), color=BLUE, sw=2.2))
        p.append(line(x - 4, Y(1 - rel), x + 4, Y(1 - rel), color=BLUE, sw=2.2))
        p.append(circle(x, Y(1.0), 3.6, fill=BLUE, stroke=BLUE, sw=1))
        ty = Y(1 - rel) + 17 if K <= 100 else Y(1 + rel) - 10
        p.append(text(x, ty, lbl, size=10.5, color=BLUE, bold=True))

    p.append(text(W / 2, H - 16,
                  "відносна похибка ≈ 1/√K — тісніє з ЧИСЛОМ помилок, не з числом бітів",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "mc-precision.svg"), W, H, *p,
           title="Чому саме 100 помилок: лійка точності 1/√K")


# ── ratio-ladder: Eb/N0 → Es/N0 → SNR, три бокси й перетворення ─────────────

def fig_ratio_ladder():
    W, H = 960, 420
    p = []
    cy = 150
    size = 13.5

    b1, w1, h1 = textbox(150, cy, ["Eb/N₀", "не залежить від Rb і B"], size=size, pad=14)
    b2, w2, h2 = textbox(480, cy, ["Es/N₀", "енергія цілого символа"], size=size, pad=14)
    b3, w3, h3 = textbox(810, cy, ["SNR", "виміряне в смузі приймача"], size=size, pad=14)
    p += [b1, b2, b3]

    top = cy - h1 / 2 - 60   # спільна горизонталь над боксами

    # вертикалі від верху кожного боксу до спільної горизонталі
    p.append(line(150, cy - h1 / 2, 150, top, color=INK, sw=1.6))
    p.append(line(480, cy - h2 / 2, 480, top, color=INK, sw=1.6))
    p.append(line(810, cy - h3 / 2, 810, top, color=INK, sw=1.6))
    # стрілки-вістря на горизонталі показують напрямок перетворення
    p.append(arrow(150 + 4, top, 476, top, color=INK, sw=1.6))
    p.append(arrow(484, top, 806, top, color=INK, sw=1.6))

    p.append(text(315, top - 14, "×k   (k = log₂M біт/символ)", size=12, color=INK, bold=True))
    p.append(text(645, top - 14, "×Rs/B   (символів у смугу)", size=12, color=INK, bold=True))

    # пряма: Eb/N0 -> SNR, дугою знизу, поза боксами
    bot = cy + h1 / 2 + 70
    xL = 150 - w1 / 2 - 30
    xR = 810 + w3 / 2 + 30
    p.append(line(150 - w1 / 2, cy + h1 / 2, xL, cy + h1 / 2, color=MUTED, sw=1.6, dash="6 4"))
    p.append(line(xL, cy + h1 / 2, xL, bot, color=MUTED, sw=1.6, dash="6 4"))
    p.append(line(xL, bot, xR, bot, color=MUTED, sw=1.6, dash="6 4"))
    p.append(line(xR, bot, xR, cy + h3 / 2, color=MUTED, sw=1.6, dash="6 4"))
    p.append(arrow(xR, cy + h3 / 2 + 4, 810 + w3 / 2, cy + h3 / 2, color=MUTED, sw=1.6))

    p.append(text((xL + xR) / 2, bot + 22, "пряма: ×(Rb/B)", size=12.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "ratio-ladder.svg"), W, H, *p,
           title="Драбина відношень: Eb/N₀ → Es/N₀ → SNR")


# ── cliff-vs-slope: гаусів обрив проти релеївського схилу ───────────────────

def fig_cliff_slope():
    W, H = 800, 500
    p = []
    px0, px1 = 100, 700
    py0, py1 = 66, 360
    smin, smax = 0.0, 40.0
    emin, emax = -1.0, -7.0

    def X(s):
        return px0 + (s - smin) / (smax - smin) * (px1 - px0)

    def Y(e):
        return py0 + (emin - e) / (emin - emax) * (py1 - py0)

    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 12, y + 4, "10⁻%d" % k, size=11.5, color=MUTED, anchor="end"))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    for s in range(0, 41, 5):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 21, str(s), size=11, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 44, "Eb/N0 , дБ", size=13, color=INK))
    p.append(text(px0 - 62, (py0 + py1) / 2, "BER", size=13, color=INK, bold=True))

    # гаусова крива (BPSK) — обрив, зникає з поля зору рано
    gpts = []
    s = smin
    while s <= smax + 1e-9:
        b = ber_bpsk(s)
        if b > 0:
            e = math.log10(b)
            if emax - 0.15 <= e <= emin + 0.02:
                gpts.append((X(s), Y(e)))
        s += 0.1
    p.append(polyline(gpts, color=COD, sw=3.0))
    gx, gy = gpts[-1]
    p.append(arrow(gx, gy, gx, min(py1 - 4, gy + 26), color=COD, sw=1.8))

    # релеївська крива — пологий схил через увесь діапазон
    rpts = []
    s = 1.0
    while s <= smax + 1e-9:
        b = ber_rayleigh(s)
        if b > 0:
            e = math.log10(b)
            if emax - 0.15 <= e <= emin + 0.02:
                rpts.append((X(s), Y(e)))
        s += 0.2
    p.append(polyline(rpts, color=BLUE, sw=3.0))

    # позначки при 10 дБ
    for s0, fn, col in [(10.0, ber_bpsk, COD), (10.0, ber_rayleigh, BLUE)]:
        b0 = fn(s0)
        e0 = math.log10(b0)
        if emax - 0.15 <= e0 <= emin + 0.02:
            p.append(circle(X(s0), Y(e0), 4.2, fill=col, stroke=col, sw=1))
    p.append(line(X(10.0), py0, X(10.0), py1, color=INK, sw=1.0, dash="2 4"))
    p.append(text(X(10.0), py0 - 6, "10 дБ", size=11, color=INK, bold=True))

    # підписи нахилів
    p.append(text(X(6.0), Y(-2.0), "гаусів обрив:", size=12, color=COD, bold=True, anchor="start"))
    p.append(text(X(6.0), Y(-2.0) + 16, "декада за ≈1 дБ, дедалі стрімкіше", size=11, color=COD, anchor="start"))

    p.append(text(X(20.0), Y(-2.5), "релеївський схил:", size=12, color=BLUE, bold=True, anchor="start"))
    p.append(text(X(20.0), Y(-2.5) + 16, "декада за 10 дБ, рівно", size=11, color=BLUE, anchor="start"))

    ly = py1 + 66
    for label, col, lx in [("гаусів канал (BPSK)", COD, px0 + 30), ("релеївське завмирання", BLUE, px0 + 30 + 32 + text_width("гаусів канал (BPSK)", 12) + 46)]:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3.0))
        p.append(text(lx + 32, ly + 4, label, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "cliff-vs-slope.svg"), W, H, *p,
           title="Обрив проти схилу: гаусів канал і релеївське завмирання")


if __name__ == "__main__":
    fig_waterfall()
    fig_decision()
    fig_modulation()
    fig_mc_overlay()
    fig_mc_precision()
    fig_ratio_ladder()
    fig_cliff_slope()
    print("figs done:", os.listdir(OUT))
