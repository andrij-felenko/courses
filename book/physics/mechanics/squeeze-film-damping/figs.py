# -*- coding: utf-8 -*-
"""Фігури до теми «Squeeze-film демпфування».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GAS = "#cfe8f5"     # газовий прошарок
GASD = "#8fc7e6"
PRESS = "#f6d3ce"   # заливка тиску
ORANGE = "#e08e0b"
GREEN = FIELD


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def logsp(a, b, n):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=PRESS, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


def ground(x1, x2, y, color=INK, sw=2):
    out = [line(x1, y, x2, y, color=color, sw=sw)]
    n = 13
    for i in range(n):
        xx = x1 + (x2 - x1) * i / (n - 1)
        out.append(line(xx, y, xx - 11, y + 12, color=color, sw=1.2))
    return "".join(out)


# ── Фігура 1: механізм — опір бічній втечі народжує тиск ─────────────────────
def fig_mechanism():
    W, H = 860, 520
    F = []
    xL, xR = 190, 670
    xc = (xL + xR) / 2
    half = (xR - xL) / 2

    # осьова лінія-баз для профілю тиску
    base = 196
    peak = 96
    # заливка-парабола тиску
    poly = []
    for x in frange(xL, xR, 80):
        y = base - (base - peak) * (1 - ((x - xc) / half) ** 2)
        poly.append((x, y))
    shade = [(xL, base)] + poly + [(xR, base)]
    F.append(polygon(shade, fill=PRESS))
    F.append(polyline(poly, color=POS, sw=2.8))
    F.append(line(xL, base, xR, base, color=MUTED, sw=1.4))
    F.append(text(xc, peak - 12, "тиск у прошарку  p(x)", size=14, color=POS, bold=True))
    F.append(text(xc, peak + 26, "максимум у центрі", size=12, color=POS))
    F.append(text(xL - 12, base + 5, "0", size=12.5, color=MUTED, anchor="end"))
    F.append(text(xR + 12, base + 5, "0", size=12.5, color=MUTED, anchor="start"))

    # дашки-прив'язки країв профілю до пластин
    F.append(line(xL, base, xL, 250, color="#d0d5db", sw=1.2, dash="4 5"))
    F.append(line(xR, base, xR, 250, color="#d0d5db", sw=1.2, dash="4 5"))

    # верхня (рухома) пластина
    F.append(rect(xL, 250, xR - xL, 20, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
    F.append(text(xc, 264, "рухома пластина", size=12.5, color="#ffffff", bold=True))
    # прошарок газу
    F.append(rect(xL, 270, xR - xL, 92, fill=GAS, stroke=GASD, sw=1.4, rx=2))
    # нижня (нерухома) пластина
    F.append(rect(xL, 362, xR - xL, 20, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
    F.append(text(xc, 376, "нерухома пластина", size=12.5, color="#ffffff", bold=True))
    F.append(ground(xL, xR, 382))

    # стрілка зближення v
    F.append(arrow(xc, 220, xc, 248, color=POS, sw=3.2))
    F.append(text(xc + 16, 236, "v — пластина йде вниз", size=13, color=POS, bold=True, anchor="start"))

    # бічні стрілки витікання газу
    F.append(arrow(415, 306, 200, 306, color=NEG, sw=2.6))
    F.append(arrow(445, 306, 660, 306, color=NEG, sw=2.6))
    F.append(text(xc, 340, "газ виштовхується вбік крізь вузьку щілину", size=12.5, color=NEG))

    # підсумок
    F.append(fitbox(xL, 430, xR - xL, 62,
                    "тонкий зазор гальмує втечу газу (в'язкість) → у центрі росте тиск\n"
                    "→ виникає сила проти руху, пропорційна ШВИДКОСТІ зближення",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "squeeze-mechanism.svg"), W, H, *F,
           title="Стиснення прошарку: тиск народжується з опору бічній втечі")


# ── Фігура 2: закон куба зазору 1/h³ проти звичайного тертя 1/h ──────────────
def fig_gap_cube():
    W, H = 860, 540
    F = []
    x0, x1 = 118, 720
    yt, yb = 84, 430
    hmin, hmax = 1.0, 100.0
    cmin, cmax = 1.0, 1.0e6
    lhmin, lhmax = math.log10(hmin), math.log10(hmax)
    lcmin, lcmax = math.log10(cmin), math.log10(cmax)

    def X(h):
        return x0 + (math.log10(h) - lhmin) / (lhmax - lhmin) * (x1 - x0)

    def Y(c):
        c = min(max(c, cmin), cmax)
        return yb - (math.log10(c) - lcmin) / (lcmax - lcmin) * (yb - yt)

    def c_sq(h):
        return (100.0 / h) ** 3

    def c_sh(h):
        return 100.0 / h

    # зона мікрозазорів
    F.append(rect(X(hmin), yt, X(3.0) - X(hmin), yb - yt, fill="#fdf2ef", stroke="none", sw=0, rx=0))
    F.append(text(X(1.7), yt + 18, "мікрозазори", size=12.5, color=POS, italic=True, bold=True))

    # мітки осей (без наскрізних ліній-сітки, щоб написи стояли поза лініями)
    for h in [1, 3, 10, 30, 100]:
        F.append(line(X(h), yb, X(h), yb + 6, color=MUTED, sw=1.1))
        F.append(text(X(h), yb + 24, ("%g" % h), size=12, color=MUTED))
    ylabs = [(1, "1"), (10, "10"), (100, "100"), (1e3, "10³"), (1e4, "10⁴"), (1e5, "10⁵"), (1e6, "10⁶")]
    for c, lb in ylabs:
        F.append(line(x0 - 6, Y(c), x0, Y(c), color=MUTED, sw=1.1))
        F.append(text(x0 - 12, Y(c) + 4, lb, size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "зазор  h, мкм  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 16, "коефіцієнт демпфування (відн.)", size=12.5, color=MUTED, anchor="start"))

    # криві
    sq = [(X(h), Y(c_sq(h))) for h in logsp(hmin, hmax, 160)]
    sh = [(X(h), Y(c_sh(h))) for h in logsp(hmin, hmax, 160)]
    F.append(polyline(sq, color=GREEN, sw=3.2))
    F.append(polyline(sh, color=NEG, sw=2.6, dash="7 5"))
    F.append(text(X(2.0) + 6, Y(c_sq(2.0)) - 14, "squeeze-film:  c ∝ 1/h³", size=13.5, color=GREEN, bold=True, anchor="start"))
    F.append(text(X(11) + 8, Y(c_sh(11)) + 22, "звичайне зсувне тертя:  c ∝ 1/h", size=13, color=NEG, anchor="start"))

    # позначка ×2 → ×8
    h1, h2 = 4.0, 2.0
    F.append(circle(X(h1), Y(c_sq(h1)), 5, fill=GREEN, stroke=GREEN))
    F.append(circle(X(h2), Y(c_sq(h2)), 5, fill=GREEN, stroke=GREEN))
    F.append(line(X(h2), Y(c_sq(h1)), X(h2), Y(c_sq(h2)), color=POS, sw=1.6, dash="4 4"))
    F.append(line(X(h1), Y(c_sq(h1)), X(h2), Y(c_sq(h1)), color=POS, sw=1.6, dash="4 4"))
    F.append(fitbox(X(4.6), Y(4.0e5), 232, 48,
                    "удвічі вужчий зазор\n→ у 8 разів більше демпфування",
                    size=12.5, bold=True, fill="#fdecea", stroke=POS, pad=8))

    render(os.path.join(IMG, "gap-cube-law.svg"), W, H, *F,
           title="Закон куба зазору: демпфування злітає в мікросвіті")


# ── Фігура 3: демпфер чи пружина — залежно від числа стиснення σ ─────────────
def fig_regimes():
    W, H = 860, 500
    F = []
    x0, x1 = 120, 720
    yt, yb = 90, 396
    smin, smax = 0.1, 100.0
    lsmin, lsmax = math.log10(smin), math.log10(smax)
    sc = 10.0  # ~ π²

    def X(s):
        return x0 + (math.log10(s) - lsmin) / (lsmax - lsmin) * (x1 - x0)

    def Y(v):  # v у [0,1]
        return yb - v * (yb - yt) / 1.05

    def cdamp(s):
        return 1.0 / (1.0 + (s / sc) ** 2)

    def kspring(s):
        r = (s / sc) ** 2
        return r / (1.0 + r)

    # зони
    F.append(rect(x0, yt, X(sc) - x0, yb - yt, fill="#eafaf0", stroke="none", sw=0, rx=0))
    F.append(rect(X(sc), yt, x1 - X(sc), yb - yt, fill="#fff6e8", stroke="none", sw=0, rx=0))
    F.append(text(X(0.9), yt + 22, "ДЕМПФЕР", size=15, color=GREEN, bold=True))
    F.append(text(X(0.9), yt + 42, "газ устигає витекти", size=12, color=GREEN, italic=True))
    F.append(text(X(40), yt + 22, "ПРУЖИНА", size=15, color=ORANGE, bold=True))
    F.append(text(X(40), yt + 42, "газ замкнено й стиснуто", size=12, color=ORANGE, italic=True))

    # мітки осей (без наскрізних ліній-сітки)
    for s in [0.1, 0.3, 1, 3, 10, 30, 100]:
        F.append(line(X(s), yb, X(s), yb + 6, color=MUTED, sw=1.0))
        F.append(text(X(s), yb + 24, ("%g" % s), size=12, color=MUTED))
    for v in [0, 0.5, 1.0]:
        F.append(line(x0 - 6, Y(v), x0, Y(v), color=MUTED, sw=1.0))
        F.append(text(x0 - 12, Y(v) + 4, ("%g" % v), size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "число стиснення  σ = 12 μ ω L² / (p₀ h₀²)   (росте з частотою)  →",
                  size=13.5, color=INK))
    F.append(text(x0 - 6, yt - 18, "частка сили (відн.)", size=12.5, color=MUTED, anchor="start"))

    # вертикаль переходу
    F.append(line(X(sc), yt, X(sc), yb, color=INK, sw=1.6, dash="6 5"))
    F.append(text(X(sc), yt - 6, "σ ~ π²  (перехід)", size=12.5, color=INK, bold=True))

    # криві
    cd = [(X(s), Y(cdamp(s))) for s in logsp(smin, smax, 170)]
    ks = [(X(s), Y(kspring(s))) for s in logsp(smin, smax, 170)]
    F.append(polyline(cd, color=NEG, sw=3.2))
    F.append(polyline(ks, color=ORANGE, sw=3.2))
    F.append(text(X(0.16), Y(cdamp(0.16)) - 12, "демпфування", size=13, color=NEG, bold=True, anchor="start"))
    F.append(text(X(62), Y(kspring(62)) - 12, "жорсткість (газова пружина)", size=13, color=ORANGE, bold=True, anchor="end"))

    # точка перетину
    F.append(circle(X(sc), Y(0.5), 5.5, fill=INK, stroke=INK))

    render(os.path.join(IMG, "damper-spring-regimes.svg"), W, H, *F,
           title="Той самий прошарок: демпфер на низькій частоті, пружина на високій")


# ── Фігура 4: перфорація вкорочує шлях втечі → менше демпфування ─────────────
def fig_perforation():
    W, H = 860, 480
    F = []
    F.append(line(430, 74, 430, 402, color="#d0d5db", sw=1.5, dash="4 5"))

    def panel(cx, holes):
        out = []
        pL, pR = cx - 150, cx + 150
        py = 158       # верх пластини
        pth = 20       # товщина
        gap_b = 258    # низ прошарку
        # прошарок
        out.append(rect(pL, py + pth, pR - pL, gap_b - (py + pth), fill=GAS, stroke=GASD, sw=1.3, rx=2))
        # підкладка
        out.append(rect(pL, gap_b, pR - pL, 18, fill="#3a4149", stroke=INK, sw=1.4, rx=3))
        if not holes:
            # суцільна пластина
            out.append(rect(pL, py, pR - pL, pth, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
            # довгі бічні стрілки втечі
            ym = (py + pth + gap_b) / 2
            out.append(arrow(cx - 18, ym, pL + 8, ym, color=NEG, sw=2.4))
            out.append(arrow(cx + 18, ym, pR - 8, ym, color=NEG, sw=2.4))
            out.append(text(cx, gap_b + 46, "довгий шлях убік", size=12.5, color=NEG))
        else:
            # пластина з отворами: сегменти + канали
            xs = [cx - 90, cx - 30, cx + 30, cx + 90]
            hw = 9
            edges = [pL] + [v for x in xs for v in (x - hw, x + hw)] + [pR]
            for i in range(0, len(edges), 2):
                a, b = edges[i], edges[i + 1]
                if b - a > 1:
                    out.append(rect(a, py, b - a, pth, fill="#3a4149", stroke=INK, sw=1.5, rx=2))
            # вертикальні стрілки вгору крізь отвори
            for x in xs:
                out.append(arrow(x, gap_b - 8, x, py - 30, color=NEG, sw=2.4))
            out.append(text(cx, gap_b + 46, "короткий шлях угору крізь отвори", size=12, color=NEG))
        return out

    # ліворуч — суцільна
    F.extend(panel(240, holes=False))
    F.append(text(240, 118, "суцільна пластина", size=14.5, bold=True))
    F.append(textbox(240, 360, "сильне демпфування", size=13, bold=True,
                     fill="#fdecea", stroke=POS, pad=9)[0])

    # праворуч — перфорована
    F.extend(panel(620, holes=True))
    F.append(text(620, 118, "перфорована пластина", size=14.5, bold=True))
    F.append(textbox(620, 360, "слабке демпфування", size=13, bold=True,
                     fill="#eafaf0", stroke=GREEN, pad=9)[0])

    F.append(fitbox(150, 418, 560, 44,
                    "коротший шлях втечі газу → менший тиск у прошарку → менше демпфування:\n"
                    "саме тому рухомі пластини MEMS роблять із отворами-перфорацією",
                    size=12.5, bold=True, fill="#f4f6f8", stroke=LINE, pad=8))

    render(os.path.join(IMG, "perforation-escape.svg"), W, H, *F,
           title="Перфорація: отвори вкорочують шлях втечі й гасять демпфування")


# ── Фігура 5 (історія): часоряд від «позірної адгезії» до MEMS ────────────────
def fig_timeline():
    W, H = 1140, 590
    F = []
    base = 336
    xA, xB = 130, 1010

    # вісь часу: справжні позиції років → видно порожнє «століття сну»
    y0, y1 = 1865, 1995
    def X(yr):
        return xA + (yr - y0) / (y1 - y0) * (xB - xA)

    # смуга «доба MEMS» позаду базової лінії (1975–1990)
    mx0, mx1 = X(1975), X(1990)
    F.append(rect(mx0, base - 20, mx1 - mx0, 40, fill="#eef4ff", stroke="#c7d8f7", sw=1.2, rx=6))
    F.append(text((mx0 + mx1) / 2, 250, "1980-ті", size=13.5, color=NEG, bold=True))
    F.append(text((mx0 + mx1) / 2, 268, "доба MEMS", size=12, color=NEG))
    F.append(line((mx0 + mx1) / 2, 276, (mx0 + mx1) / 2, base - 22, color="#c7d8f7", sw=1.2, dash="3 4"))

    # базова лінія
    F.append(line(xA, base, xB, base, color=INK, sw=2.2))
    F.append(arrow(xB - 2, base, xB + 26, base, color=INK, sw=2.2))
    F.append(text(xB + 30, base + 5, "час", size=13, color=MUTED, anchor="start"))

    CW = 214
    def card(dotyr, cx, cy, above, yr, lines, accent):
        out = []
        dx = X(dotyr)
        # картка (фіксована ширина, шрифт сам влазить)
        out.append(fitbox(cx - CW / 2, cy - 46, CW, 92, lines,
                          size=13, pad=9, fill="#f8fafc", stroke=accent, sw=1.8))
        # виноска дот→картка
        if above:
            out.append(line(dx, base - 13, cx, cy + 46 + 2, color=MUTED, sw=1.3))
            out.append(text(dx, base + 26, yr, size=15, color=accent, bold=True))
        else:
            out.append(line(dx, base + 13, cx, cy - 46 - 2, color=MUTED, sw=1.3))
            out.append(text(dx, base - 16, yr, size=15, color=accent, bold=True))
        # дот на осі
        out.append(circle(dx, base, 7, fill=accent, stroke=INK, sw=1.6))
        return out

    F += card(1874, 190, 150, True, "1874",
              "Йозеф Стефан\n«позірна адгезія»:\nвичавлюваний прошарок,\nF ∝ μR⁴v / h³", FIELD)
    F += card(1886, 300, 486, False, "1886",
              "Осборн Рейнольдс\nтеорія змащування;\nsqueeze — один член\nрівняння Рейнольдса", NEG)
    F += card(1962, 690, 150, True, "1962",
              "В. Е. Ланглуа\nстисливі плівки для\nгазових підшипників;\nчисло стиснення", ORANGE)
    F += card(1983, 918, 486, False, "1983",
              "Дж. Дж. Блех\nізотермічний аналіз:\nдемпфер + пружина —\nканон MEMS донині", POS)

    # анотація «століття сну» над порожнім прогоном 1886→1962
    F.append(textbox((X(1886) + X(1962)) / 2, base - 44,
                     "≈ століття майже без уваги —\nлише світ підшипників і змащування",
                     size=12.5, pad=10, fill="#fdf2ef", stroke="#f0c9c0", color="#8a5a4a")[0])

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *F,
           title="Часоряд: та сама фізика, від «позірної адгезії» 1874 р. до ворога MEMS")


# ── Фігура 6 (калькулятор): розгортка зазору — урвище 1/h³ і згин розрідження ─
def fig_calc_gapsweep():
    W, H = 900, 560
    F = []
    x0, x1 = 138, 748
    yt, yb = 96, 436
    hmin, hmax = 0.1, 10.0
    cmin, cmax = 1e-6, 1e2
    lhmin, lhmax = math.log10(hmin), math.log10(hmax)
    lcmin, lcmax = math.log10(cmin), math.log10(cmax)

    def X(h):
        return x0 + (math.log10(h) - lhmin) / (lhmax - lhmin) * (x1 - x0)

    def Y(c):
        c = min(max(c, cmin), cmax)
        return yb - (math.log10(c) - lcmin) / (lcmax - lcmin) * (yb - yt)

    LAM = 0.068  # мкм — довжина вільного пробігу повітря при атмосфері
    MU = 1.8e-5
    LW = 200e-6

    def mu_eff(h):
        Kn = LAM / h
        return MU / (1.0 + 9.638 * Kn ** 1.159)

    def c_cont(h):        # суцільна формула: чистий 1/h³
        hm = h * 1e-6
        return 0.42 * MU * LW * LW ** 3 / hm ** 3

    def c_corr(h):        # з поправкою на розрідження (μ_eff)
        hm = h * 1e-6
        return 0.42 * mu_eff(h) * LW * LW ** 3 / hm ** 3

    # зона розрідження: Kn > 0.1  ⇔  h < 0.68 мкм
    hk = LAM / 0.1
    F.append(rect(x0, yt, X(hk) - x0, yb - yt, fill="#fdf2ef", stroke="none", sw=0, rx=0))
    F.append(text((x0 + X(hk)) / 2, yt + 18, "розрідження суттєве", size=12.5, color=POS, italic=True, bold=True))
    F.append(text((x0 + X(hk)) / 2, yt + 36, "Kn = λ/h > 0.1", size=11.5, color=POS, italic=True))
    F.append(line(X(hk), yt, X(hk), yb, color=POS, sw=1.3, dash="5 5"))

    # мітки осей (без наскрізної сітки)
    for h in [0.1, 0.3, 1, 3, 10]:
        F.append(line(X(h), yb, X(h), yb + 6, color=MUTED, sw=1.1))
        F.append(text(X(h), yb + 24, ("%g" % h), size=12, color=MUTED))
    ylabs = [(1e-6, "10⁻⁶"), (1e-4, "10⁻⁴"), (1e-2, "10⁻²"), (1, "1"), (1e2, "10²")]
    for c, lb in ylabs:
        F.append(line(x0 - 6, Y(c), x0, Y(c), color=MUTED, sw=1.1))
        F.append(text(x0 - 12, Y(c) + 4, lb, size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "зазор  h, мкм  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 18, "коеф. демпфування  c₀, Н·с/м", size=12.5, color=MUTED, anchor="start"))

    # криві
    cont = [(X(h), Y(c_cont(h))) for h in logsp(hmin, hmax, 150)]
    corr = [(X(h), Y(c_corr(h))) for h in logsp(hmin, hmax, 150)]
    F.append(polyline(cont, color=NEG, sw=2.4, dash="7 5"))
    F.append(polyline(corr, color=GREEN, sw=3.4))
    F.append(text(X(0.62), Y(c_cont(0.62)) - 12, "суцільна формула:  c ∝ 1/h³", size=13, color=NEG, bold=True, anchor="start"))
    F.append(text(X(1.7), Y(c_corr(1.7)) + 24, "з поправкою на розрідження (μ_eff)", size=12.5, color=GREEN, bold=True, anchor="start"))

    # розбіжність на лівому краю: дужка ×7
    xb = X(0.1) + 8
    F.append(line(xb, Y(c_cont(0.1)), xb, Y(c_corr(0.1)), color=POS, sw=2.0))
    F.append(line(xb - 4, Y(c_cont(0.1)), xb + 4, Y(c_cont(0.1)), color=POS, sw=2.0))
    F.append(line(xb - 4, Y(c_corr(0.1)), xb + 4, Y(c_corr(0.1)), color=POS, sw=2.0))
    F.append(text(xb + 12, (Y(c_cont(0.1)) + Y(c_corr(0.1))) / 2 + 4, "×7", size=14, color=POS, bold=True, anchor="start"))

    # зразкова точка h = 2 мкм
    F.append(circle(X(2), Y(c_corr(2)), 5.5, fill=GREEN, stroke=INK, sw=1.5))
    F.append(text(X(2) + 12, Y(c_corr(2)) + 5, "зразок  h = 2 мкм", size=11.5, color=INK, anchor="start"))

    # пояснення в порожньому нижньому куті
    F.append(fitbox(X(1.55), Y(3.0e-5), 268, 52,
                    "що вужчий зазор, то більше газ прослизає\n"
                    "біля стінок — і то дужче суцільна 1/h³\n"
                    "завищує реальні втрати",
                    size=11.5, bold=True, fill="#f4f6f8", stroke=LINE, pad=8))

    render(os.path.join(IMG, "calc-gap-rarefaction.svg"), W, H, *F,
           title="Розгортка зазору: урвище 1/h³ і де його згинає розрідження")


# ── Фігура (math): течія Пуазейля — витрата й корінь степенів h ──────────────
def fig_poiseuille():
    W, H = 900, 520
    F = []
    xL, xR = 120, 520
    yTop, yBot = 162, 346          # низ верхньої / верх нижньої пластини
    hpx = yBot - yTop
    xb = 210                       # ліва база профілю
    Umax = 168                     # макс. довжина стрілки

    def prof(f):
        return Umax * 4.0 * f * (1.0 - f)

    # градієнт тиску над верхньою пластиною
    F.append(text(xL, 84, "вищий тиск", size=12.5, color=POS, bold=True, anchor="start"))
    F.append(text(xR, 84, "нижчий тиск", size=12.5, color=NEG, bold=True, anchor="end"))
    F.append(arrow(xL + 18, 100, xR - 18, 100, color=MUTED, sw=2.2))
    F.append(text((xL + xR) / 2, 122, "тиск падає уздовж щілини  (dp/dx)", size=12.5, color=MUTED))

    # пластини
    F.append(rect(xL, yTop - 18, xR - xL, 18, fill="#3a4149", stroke=INK, sw=1.4, rx=3))
    F.append(rect(xL, yBot, xR - xL, 18, fill="#3a4149", stroke=INK, sw=1.4, rx=3))

    # заливка-профіль (площа = витрата) + обвідна
    env = [(xb, yTop)]
    for f in frange(0.0, 1.0, 44):
        env.append((xb + prof(f), yTop + f * hpx))
    env.append((xb, yBot))
    F.append(polygon(env, fill=PRESS))
    F.append(polyline(env[1:-1], color=POS, sw=2.6))
    F.append(line(xb, yTop, xb, yBot, color=MUTED, sw=1.4))

    # стрілки швидкості
    for f in [0.12, 0.26, 0.4, 0.5, 0.6, 0.74, 0.88]:
        y = yTop + f * hpx
        F.append(arrow(xb, y, xb + prof(f), y, color=NEG, sw=2.2))

    F.append(text(xb + 6, yTop + 14, "u = 0 (прилипання)", size=10.5, color=MUTED, anchor="start"))
    F.append(text(xb + 6, yBot - 6, "u = 0 (прилипання)", size=10.5, color=MUTED, anchor="start"))
    F.append(text(xb + Umax + 10, (yTop + yBot) / 2 + 4, "профіль u(z)", size=13, color=POS, bold=True, anchor="start"))

    # розмір h
    F.append(arrow(152, yTop, 152, yBot, color=INK, sw=1.7))
    F.append(arrow(152, yBot, 152, yTop, color=INK, sw=1.7))
    F.append(text(140, (yTop + yBot) / 2 + 5, "h", size=16, color=INK, bold=True, italic=True, anchor="end"))

    # підпис витрати
    F.append(fitbox(xL, 378, xR - xL, 52,
                    "витрата  q = ∫ u dz  =  площа під профілем\n"
                    "q = − h³ / (12μ) · dp/dx",
                    size=13.5, bold=True, fill="#fdecea", stroke=POS, pad=8))

    # права колонка — розклад степенів h
    bx0, bw = 588, 292
    F.append(rect(bx0, 150, bw, 246, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    cx = bx0 + bw / 2
    F.append(text(cx, 180, "звідки три степені h", size=14.5, bold=True))
    F.append(text(bx0 + 20, 220, "u ~ (dp/dx) · h² / μ", size=13.5, anchor="start", bold=True))
    F.append(text(bx0 + 20, 240, "гальмування стінок  → h²", size=11.5, anchor="start", color=MUTED))
    F.append(text(bx0 + 20, 278, "q = u · h", size=13.5, anchor="start", bold=True))
    F.append(text(bx0 + 20, 298, "× переріз каналу  → ще h", size=11.5, anchor="start", color=MUTED))
    F.append(line(bx0 + 20, 318, bx0 + bw - 20, 318, color=LINE, sw=1.2))
    F.append(text(cx, 346, "разом  q ∝ h³", size=15.5, bold=True, color=POS))
    F.append(text(cx, 374, "→ сила демпфування ∝ 1/h³", size=12, color=MUTED))

    render(os.path.join(IMG, "poiseuille-flux.svg"), W, H, *F,
           title="Течія Пуазейля крізь щілину: витрата й корінь степенів h")


# ── Фігура (math): геометричний множник β від відношення сторін W/L ──────────
def fig_beta_aspect():
    W, H = 900, 540
    F = []
    x0, x1 = 140, 560
    yt, yb = 96, 430

    def bser(r):
        if r < 1e-6:
            return 1.0
        s = 0.0
        for n in range(1, 60, 2):
            s += (1.0 / n ** 5) * math.tanh(n * math.pi / (2.0 * r))
        return 1.0 - (192.0 / math.pi ** 5) * r * s

    def X(r):
        return x0 + r * (x1 - x0)

    def Y(b):
        return yb - b * (yb - yt)

    # мітки осей
    for r in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        F.append(line(X(r), yb, X(r), yb + 6, color=MUTED, sw=1.0))
        F.append(text(X(r), yb + 24, ("%.1f" % r), size=12, color=MUTED))
    for b in [0, 0.2, 0.42, 0.6, 0.8, 1.0]:
        F.append(line(x0 - 6, Y(b), x0, Y(b), color=MUTED, sw=1.0))
        lab = "0.42" if abs(b - 0.42) < 1e-6 else ("%.1f" % b)
        F.append(text(x0 - 12, Y(b) + 4, lab, size=12, color=MUTED, anchor="end"))
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "відношення сторін  W / L  →", size=13.5, color=INK))
    F.append(text(x0 - 6, yt - 16, "геометричний множник  β", size=12.5, color=MUTED, anchor="start"))

    # крива β(W/L)
    pts = [(X(r), Y(bser(r))) for r in frange(0.001, 1.0, 220)]
    F.append(polyline(pts, color=FIELD, sw=3.2))

    # позначки кінців
    F.append(circle(X(0.0), Y(1.0), 5.5, fill=FIELD, stroke=INK, sw=1.5))
    F.append(text(X(0.02) + 8, Y(1.0) + 4, "смуга:  β = 1", size=12.5, color=FIELD, bold=True, anchor="start"))
    F.append(circle(X(1.0), Y(0.4217), 5.5, fill=ORANGE, stroke=INK, sw=1.5))
    F.append(text(X(0.98) - 8, Y(0.4217) - 12, "квадрат:  β ≈ 0.42", size=12.5, color=ORANGE, bold=True, anchor="end"))

    # ── права панель зі схемами витікання ──
    pcx = 740
    # смуга
    F.append(text(pcx, 128, "нескінченна смуга", size=13.5, bold=True))
    F.append(rect(pcx - 78, 158, 156, 18, fill=GAS, stroke=GASD, sw=1.3, rx=2))
    F.append(arrow(pcx, 156, pcx, 134, color=NEG, sw=2.0))
    F.append(arrow(pcx, 178, pcx, 200, color=NEG, sw=2.0))
    F.append(text(pcx, 222, "газ тікає лише впоперек", size=11.5, color=NEG))
    # квадрат
    F.append(text(pcx, 300, "квадрат", size=13.5, bold=True))
    F.append(rect(pcx - 28, 322, 56, 56, fill=GAS, stroke=GASD, sw=1.3, rx=3))
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        F.append(arrow(pcx + dx * 30, 350 + dy * 30, pcx + dx * 54, 350 + dy * 54, color=NEG, sw=2.0))
    F.append(text(pcx, 430, "газ тікає на всі чотири боки", size=11.5, color=ORANGE))

    F.append(fitbox(x0, yb + 66, 720, 40,
                    "кожен додатковий вихід зрізає купол тиску: що ближче до квадрата, "
                    "то менший β і слабше демпфування",
                    size=12.5, bold=True, fill="#f4f6f8", stroke=LINE, pad=8))

    render(os.path.join(IMG, "beta-aspect.svg"), W, H, *F,
           title="Геометричний множник β: від смуги (β=1) до квадрата (β≈0.42)")


if __name__ == "__main__":
    fig_mechanism()
    fig_gap_cube()
    fig_regimes()
    fig_perforation()
    fig_timeline()
    fig_calc_gapsweep()
    fig_poiseuille()
    fig_beta_aspect()
    print("OK: 8 SVG ->", IMG)
