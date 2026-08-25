# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── Спільна геометрія «перерізу еліпсоїда» для двох фігур ───────────────────
OX, OY = 185.0, 300.0        # центр (центр мас)
AA, BB = 300.0, 205.0        # півосі в px — сплюснутість СИЛЬНО перебільшена
T_P = 45.0                   # параметр точки P на чверть-дузі


def _ellipse_pt(t_deg):
    a = math.radians(t_deg)
    return (OX + AA * math.cos(a), OY - BB * math.sin(a))


def _quarter_arc(step=1.0):
    pts, d = [], 0.0
    while d <= 90.0 + 1e-9:
        pts.append(_ellipse_pt(d))
        d += step
    return pts


def _normal_dir():
    """Одиничний вектор зовнішньої нормалі в точці P (екранні координати)."""
    a = math.radians(T_P)
    nx, ny = math.cos(a) / AA, math.sin(a) / BB      # градієнт x²/a² + y²/b²
    m = math.hypot(nx, ny)
    return nx / m, -ny / m                           # y на екрані росте вниз


def _axis_hit(px, py, ux, uy):
    """Точка, де нормаль, продовжена всередину, перетинає вісь обертання x = OX."""
    s = (px - OX) / ux                               # рухаємось назад по нормалі
    return (OX, py + s * uy)


def _poly(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Фігура 1: геодезична широта — кут нормалі, а не напряму на центр ────────
def geodetic_latitude():
    W, H = 820, 580
    px, py = _ellipse_pt(T_P)
    ux, uy = _normal_dir()
    ax, ay = _axis_hit(px, py, ux, uy)

    f = [text(W / 2, 28, "Широта — кут нормалі до еліпсоїда, а не напряму на центр",
              size=16, bold=True)]

    # вісь обертання і площина екватора
    f.append(line(OX, ay + 18, OX, 80, color=MUTED, sw=1.4, dash="6,5"))
    f.append(line(135, OY, 505, OY, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(168, 72, "вісь обертання", size=12, color=MUTED, anchor="end"))
    f.append(text(430, 322, "площина екватора", size=12, color=MUTED))

    # чверть перерізу еліпсоїда
    f.append(_poly(_quarter_arc(), INK, 2.8))

    # нормаль: від перетину з віссю через P і далі назовні
    f.append(line(ax, ay, px, py, color=POS, sw=2.4))
    f.append(arrow(px, py, px + ux * 105, py + uy * 105, color=POS, sw=2.4))
    f.append(text(462, 66, "нормаль до еліпсоїда", size=13, color=POS, anchor="start"))

    # радіус із центра
    f.append(line(OX, OY, px, py, color=NEG, sw=2.2))

    # кути: φ біля перетину з віссю (проти горизонталі), ψ біля центра
    f.append(line(OX, ay, OX + 120, ay, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(OX + 36, ay - 10, "φ", size=17, bold=True, color=POS))
    f.append(text(OX + 50, OY - 9, "ψ", size=17, bold=True, color=NEG))

    # точки
    f.append(circle(OX, OY, 5, fill=INK, stroke=INK))
    f.append(text(168, 296, "центр мас", size=12, color=INK, anchor="end"))
    f.append(circle(px, py, 5.5, fill=POS, stroke=POS))
    f.append(text(370, 132, "P", size=15, bold=True, color=POS))
    f.append(circle(ax, ay, 4.5, fill=POS, stroke=POS))

    f.append(fitbox(520, 300, 285, 190, "\n".join([
        "φ — геодезична широта: кут",
        "між нормаллю до еліпсоїда",
        "й площиною екватора.",
        "ψ — геоцентрична широта:",
        "кут напряму з центра.",
        "Нормаль не проходить крізь",
        "центр, тому φ ≠ ψ.",
        "На Землі різниця сягає",
        "11.5′ ≈ 21 км по поверхні.",
    ]), size=13, fill="#fdf3f2", stroke=POS, sw=1.6))
    render(os.path.join(IMG, "geodetic-latitude.svg"), W, H, *f)


# ── Фігура 2: місцева підгонка проти глобальної ─────────────────────────────
def datum_fit():
    W, H = 840, 440
    X0, X1 = 70.0, 610.0
    BASE = 250.0

    def geoid(x):
        u = (x - X0) / (X1 - X0) * 5.4
        return BASE + 26.0 * math.sin(u) + 11.0 * math.sin(2.7 * u + 0.8)

    def fit_line(xa, xb, n=200):
        """Пряма найменших квадратів до «справжньої поверхні» на [xa, xb]."""
        xs = [xa + (xb - xa) * i / (n - 1) for i in range(n)]
        ys = [geoid(x) for x in xs]
        mx = sum(xs) / n
        my = sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        k = sxy / sxx
        return (lambda x, k=k, mx=mx, my=my: my + k * (x - mx))

    local = fit_line(170.0, 320.0)     # підігнано під ОДИН регіон
    globl = fit_line(X0, X1)           # підігнано під усе разом

    f = [text(W / 2, 28, "Місцевий еліпсоїд підганяють під свій регіон, "
                         "геоцентричний — під усю планету", size=16, bold=True)]

    step = 4.0
    xs = []
    x = X0
    while x <= X1 + 1e-9:
        xs.append(x)
        x += step
    f.append(_poly([(x, geoid(x)) for x in xs], INK, 2.8))
    f.append(_poly([(x, local(x)) for x in xs], NEG, 2.4, dash="9,5"))
    f.append(_poly([(x, globl(x)) for x in xs], POS, 2.4))

    # регіон підгонки місцевого датума
    f.append(line(170, 372, 320, 372, color=NEG, sw=2.0))
    f.append(line(170, 366, 170, 378, color=NEG, sw=2.0))
    f.append(line(320, 366, 320, 378, color=NEG, sw=2.0))
    f.append(text(245, 394, "регіон підгонки", size=12, color=NEG))

    # міра розбіжності на краю
    xm = 580.0
    f.append(line(xm, geoid(xm), xm, local(xm), color=NEG, sw=1.8, dash="4,3"))
    f.append(text(566, 128, "тут місцевий", size=12, color=NEG, anchor="end"))
    f.append(text(566, 144, "уже далеко", size=12, color=NEG, anchor="end"))

    f.append(text(96, 196, "справжня поверхня", size=12, color=INK, anchor="start"))
    f.append(text(96, 336, "геоцентричний", size=12, color=POS, anchor="start"))

    f.append(fitbox(630, 190, 196, 176, "\n".join([
        "Обидві криві —",
        "законні еліпсоїди.",
        "Різні в них не форми,",
        "а прив'язки: центр",
        "місцевого відсунуто",
        "від центра мас на",
        "сотні метрів.",
        "Звідси й розбіжність",
        "координат.",
    ]), size=12, fill="#f7fbf8", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "datum-fit.svg"), W, H, *f)


# ── Фігура 3: два радіуси кривини в одній точці ─────────────────────────────
def radii_mn():
    W, H = 840, 580
    px, py = _ellipse_pt(T_P)
    ux, uy = _normal_dir()
    ax, ay = _axis_hit(px, py, ux, uy)
    Npx = math.hypot(px - ax, py - ay)

    # M/N = (1 − e²) / (1 − e² sin²φ) для НАМАЛЬОВАНОГО (перебільшеного) еліпса
    e2 = 1.0 - (BB * BB) / (AA * AA)
    phi = math.atan2(-uy, ux)
    ratio = (1.0 - e2) / (1.0 - e2 * math.sin(phi) ** 2)
    Mpx = Npx * ratio
    cmx, cmy = px - ux * Mpx, py - uy * Mpx

    f = [text(W / 2, 28, "В одній точці еліпсоїда — два різні радіуси кривини",
              size=16, bold=True)]
    f.append(line(OX, ay + 18, OX, 80, color=MUTED, sw=1.4, dash="6,5"))
    f.append(line(135, OY, 505, OY, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(168, 72, "вісь обертання", size=12, color=MUTED, anchor="end"))
    f.append(text(430, 322, "площина екватора", size=12, color=MUTED))
    f.append(_poly(_quarter_arc(), INK, 2.8))

    # коло кривини меридіана
    th0 = math.atan2(py - cmy, px - cmx)
    arcpts = []
    k = -25.0
    while k <= 25.0 + 1e-9:
        a = th0 + math.radians(k)
        arcpts.append((cmx + Mpx * math.cos(a), cmy + Mpx * math.sin(a)))
        k += 1.0
    f.append(_poly(arcpts, FIELD, 2.0, dash="7,5"))
    f.append(text(492, 232, "коло кривини меридіана", size=12, color=FIELD, anchor="start"))

    # нормаль з відкладеними M і N
    f.append(line(ax, ay, px, py, color=POS, sw=2.4))
    f.append(circle(px, py, 5.5, fill=POS, stroke=POS))
    f.append(circle(ax, ay, 5.0, fill=POS, stroke=POS))
    f.append(circle(cmx, cmy, 5.0, fill=FIELD, stroke=FIELD))

    # підписи довжин — перпендикулярно до нормалі, у чисте поле
    perp = (-uy, ux)
    mx0, my0 = (px + cmx) / 2, (py + cmy) / 2
    f.append(text(mx0 - perp[0] * 42, my0 - perp[1] * 42, "M", size=17, bold=True, color=FIELD))
    nx0, ny0 = (px + ax) / 2, (py + ay) / 2
    f.append(text(nx0 + perp[0] * 46, ny0 + perp[1] * 46, "N", size=17, bold=True, color=POS))

    f.append(text(370, 132, "P", size=15, bold=True, color=POS))

    f.append(fitbox(535, 300, 285, 200, "\n".join([
        "M — радіус кривини вздовж",
        "меридіана: по ньому кривий",
        "переріз «північ–південь».",
        "N — від точки рівно до осі",
        "обертання; це радіус кривини",
        "перерізу «схід–захід».",
        "Завжди M ≤ N.",
        "На широті 50°:",
        "M ≈ 6 372 956 м, N ≈ 6 390 702 м.",
    ]), size=13, fill="#fdf3f2", stroke=POS, sw=1.6))
    render(os.path.join(IMG, "radii-mn.svg"), W, H, *f)


# ── Фігура 4 (вставка hist): чому довший градус на півночі = сплюснута Земля ─
def arc_degree():
    W, H = 880, 520
    ox, oy = 300.0, 270.0
    A, B = 210.0, 148.0          # сплюснутість СИЛЬНО перебільшена
    e2 = 1.0 - (B * B) / (A * A)

    def pt(phi_deg):
        p = math.radians(phi_deg)
        n = A / math.sqrt(1.0 - e2 * math.sin(p) ** 2)
        return (ox + n * math.cos(p), oy - n * (1.0 - e2) * math.sin(p))

    def curv_center(phi_deg):
        p = math.radians(phi_deg)
        m = A * (1.0 - e2) / (1.0 - e2 * math.sin(p) ** 2) ** 1.5
        x, y = pt(phi_deg)
        return (x - m * math.cos(p), y + m * math.sin(p), m)

    def arc_pts(p0, p1, step=1.0):
        out, d = [], p0
        while d <= p1 + 1e-9:
            out.append(pt(d))
            d += step
        return out

    f = []
    # повний меридіанний переріз
    full = [pt(d) for d in range(-90, 271)] if False else None
    ell = []
    d = 0.0
    while d <= 360.0 + 1e-9:
        r = math.radians(d)
        ell.append((ox + A * math.cos(r), oy - B * math.sin(r)))
        d += 1.0
    f.append(_poly(ell, MUTED, sw=1.8))

    # осі
    f.append(line(ox, oy - B - 46, ox, oy + B + 34, color=MUTED, sw=1.2, dash="5 5"))
    f.append(line(ox - A - 34, oy, ox + A + 44, oy, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(ox, oy - B - 56, "вісь обертання", size=13, color=MUTED))
    f.append(text(ox + A + 46, oy - 12, "екватор", size=13, color=MUTED, anchor="start"))

    # дві однакові за широтою дуги: біля полюса й на екваторі
    P0, P1 = 68.0, 90.0
    E0, E1 = 0.0, 22.0
    f.append(_poly(arc_pts(P0, P1), NEG, sw=6.0))
    f.append(_poly(arc_pts(E0, E1), POS, sw=6.0))

    # нормалі й центри кривини
    for phi, col in ((P0, NEG), (P1, NEG), (E0, POS), (E1, POS)):
        x, y = pt(phi)
        cx, cy, _ = curv_center(phi)
        f.append(line(x, y, cx, cy, color=col, sw=1.4, dash="4 4"))
    cxp, cyp, mp = curv_center((P0 + P1) / 2)
    cxe, cye, me = curv_center((E0 + E1) / 2)
    f.append(circle(cxp, cyp, 4.0, fill=NEG, stroke=NEG))
    f.append(circle(cxe, cye, 4.0, fill=POS, stroke=POS))
    f.append(text(cxp - 14, cyp + 5, "Rпол", size=14, bold=True, color=NEG, anchor="end"))
    f.append(text(cxe + 6, cye + 26, "Rекв", size=14, bold=True, color=POS, anchor="start"))

    # підписи дуг — у чисте поле, з відступом
    xp, yp = pt((P0 + P1) / 2)
    f.append(text(xp - 96, yp - 24, "той самий 1° широти", size=13, color=NEG, anchor="middle"))
    f.append(text(xp - 96, yp - 6, "— ДОВША дуга", size=13, bold=True, color=NEG, anchor="middle"))
    xe, ye = pt((E0 + E1) / 2)
    f.append(text(xe + 74, ye + 40, "той самий 1° широти", size=13, color=POS, anchor="middle"))
    f.append(text(xe + 74, ye + 58, "— КОРОТША дуга", size=13, bold=True, color=POS, anchor="middle"))

    f.append(fitbox(600, 60, 260, 150, "\n".join([
        "Сплюснута Земля:",
        "біля полюса поверхня пряміша,",
        "радіус кривини більший —",
        "щоб нормаль повернулась на 1°,",
        "треба пройти довший шлях.",
    ]), size=13, fill="#eef2fd", stroke=NEG, sw=1.6))

    f.append(fitbox(600, 246, 260, 210, "\n".join([
        "Що виміряли:",
        "Лапландія (1736–37)",
        "1° ≈ 57 400 туазів",
        "Франція, Париж",
        "1° ≈ 57 060 туазів",
        "Перу, екватор (1735–44)",
        "1° ≈ 56 750 туазів",
        "Довший градус — на півночі.",
    ]), size=13, fill="#fdf3f2", stroke=POS, sw=1.6))

    f.append(text(600, 486, "сплюснутість на рисунку перебільшена в десятки разів",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "arc-degree.svg"), W, H, *f)


# ═══ Фігури вставки math-radii-of-curvature ════════════════════════════════
GX, GY = 250.0, 360.0        # центр перерізу
GA, GB = 330.0, 225.0        # півосі в px — сплюснутість СИЛЬНО перебільшена
GE2 = 1.0 - (GB * GB) / (GA * GA)


def _g_pt(phi_deg):
    """Точка еліпса за ГЕОДЕЗИЧНОЮ широтою + довжина нормалі N (у px)."""
    p = math.radians(phi_deg)
    w = math.sqrt(1.0 - GE2 * math.sin(p) ** 2)
    n = GA / w
    return GX + n * math.cos(p), GY - n * (1.0 - GE2) * math.sin(p), n, p


def _g_arc(step=1.0):
    pts, d = [], 0.0
    while d <= 90.0 + 1e-9:
        x, y, _, _ = _g_pt(d)
        pts.append((x, y))
        d += step
    return pts


def _ang_arc(cx, cy, r, a0, a1, color=INK, sw=1.6, step=2.0):
    """Дуга кута: градуси, відлік проти годинникової від осі +x (екранний y — вниз)."""
    pts, a = [], a0
    up = a1 >= a0
    while (a <= a1 + 1e-9) if up else (a >= a1 - 1e-9):
        r_ = math.radians(a)
        pts.append((cx + r * math.cos(r_), cy - r * math.sin(r_)))
        a += step if up else -step
    return _poly(pts, color, sw)


# ── Фігура 5: два відрізки на одній нормалі — N і N(1−e²) ───────────────────
def normal_segments():
    W, H = 960, 600
    PHI = 42.0
    px, py, n, p = _g_pt(PHI)
    ux, uy = -math.cos(p), math.sin(p)            # напрям УСЕРЕДИНУ по нормалі
    qx, qy = px + ux * n, py + uy * n             # перетин з віссю обертання
    ex, ey = px + ux * n * (1 - GE2), py + uy * n * (1 - GE2)   # з площиною екватора

    f = [text(W / 2, 28, "На одній нормалі: до площини екватора — N(1−e²), до осі — N",
              size=16, bold=True)]

    # вісь обертання і площина екватора
    f.append(line(GX, 110, GX, qy + 25, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(238, 100, "вісь обертання", size=12, color=MUTED, anchor="end"))
    f.append(line(130, GY, 600, GY, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(120, 382, "площина екватора", size=12, color=MUTED, anchor="start"))

    # чверть меридіанного перерізу
    f.append(_poly(_g_arc(), INK, 2.8))

    # нормаль: назовні від P і всередину аж до осі
    f.append(line(qx, qy, px, py, color=POS, sw=2.4))
    f.append(arrow(px, py, px - ux * 95, py - uy * 95, color=POS, sw=2.4))
    f.append(text(612, 172, "нормаль", size=13, color=POS, anchor="start"))

    # горизонталь від P до осі — катет p
    f.append(line(px, py, GX, py, color=FIELD, sw=2.0, dash="7,5"))
    f.append(text((px + GX) / 2, py - 18, "p = N·cos φ", size=14, color=FIELD))

    # кут φ між горизонталлю й нормаллю
    f.append(_ang_arc(px, py, 55, 180.0, 180.0 + PHI, color=POS, sw=1.6))
    aa = math.radians(180.0 + PHI / 2)
    f.append(text(px + 72 * math.cos(aa), py - 72 * math.sin(aa) + 5,
                  "φ", size=17, bold=True, color=POS))

    # прямий кут біля основи катета
    f.append(_poly([(GX + 14, py), (GX + 14, py + 14), (GX, py + 14)], MUTED, 1.4))

    # мітки довжин уздовж нормалі
    t1x, t1y = px + ux * n * 0.33, py + uy * n * 0.33
    f.append(text(t1x - 42 * math.sin(p), t1y - 42 * math.cos(p),
                  "N(1−e²)", size=15, bold=True, color=FIELD))
    t2x, t2y = px + ux * n * 0.72, py + uy * n * 0.72
    f.append(text(t2x + 30 * math.sin(p), t2y + 30 * math.cos(p),
                  "N", size=17, bold=True, color=POS))

    # глибина пробою осі під центром
    f.append(line(GX - 18, GY, GX - 18, qy, color=NEG, sw=2.0))
    f.append(line(GX - 25, GY, GX - 11, GY, color=NEG, sw=2.0))
    f.append(line(GX - 25, qy, GX - 11, qy, color=NEG, sw=2.0))
    f.append(text(GX - 32, (GY + qy) / 2 + 5, "N·e²·sin φ", size=13, color=NEG, anchor="end"))

    # точки
    f.append(circle(px, py, 5.5, fill=POS, stroke=POS))
    f.append(text(px + 18, py - 10, "P", size=15, bold=True, color=POS))
    f.append(circle(ex, ey, 5.0, fill=FIELD, stroke=FIELD))
    f.append(text(ex + 16, ey - 12, "E", size=14, bold=True, color=FIELD))
    f.append(circle(qx, qy, 5.0, fill=POS, stroke=POS))
    f.append(text(qx + 16, qy + 14, "Q", size=14, bold=True, color=POS, anchor="start"))
    f.append(circle(GX, GY, 5.0, fill=INK, stroke=INK))
    f.append(text(GX + 12, GY + 20, "центр", size=12, color=INK, anchor="start"))

    f.append(fitbox(665, 205, 270, 220, "\n".join([
        "Трикутник P–C–Q прямокутний,",
        "кут при P дорівнює φ.",
        "Тому PQ = p / cos φ = a/W = N,",
        "а PE = z / sin φ = N(1−e²).",
        "",
        "WGS-84, φ = 50°:",
        "N = 6 390 702 м",
        "N(1−e²) = 6 347 920 м",
        "p = 4 107 864 м",
        "вісь пробито на 32 773 м",
        "нижче за центр мас.",
    ]), size=13, fill="#fdf3f2", stroke=POS, sw=1.6))

    f.append(text(480, 570, "сплюснутість на рисунку перебільшена в десятки разів",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "normal-segments.svg"), W, H, *f)


# ── Фігура 6: три широти однієї точки ───────────────────────────────────────
def three_latitudes():
    W, H = 900, 620
    ox, oy = 290.0, 380.0
    A, B = 270.0, 185.0
    beta = math.radians(45.0)
    pxx, pyy = ox + A * math.cos(beta), oy - B * math.sin(beta)      # на еліпсі
    cxx, cyy = ox + A * math.cos(beta), oy - A * math.sin(beta)      # на колі
    psi = math.atan2(B * math.sin(beta), A * math.cos(beta))
    phi = math.atan((A / B) * math.tan(beta))
    qy = pyy + (pxx - ox) * math.tan(phi)

    f = [text(W / 2, 28, "Одна точка — три широти: φ, β і ψ", size=16, bold=True)]

    f.append(line(ox, 75, ox, qy + 30, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(275, 70, "вісь обертання", size=12, color=MUTED, anchor="end"))
    f.append(line(150, oy, ox + A + 50, oy, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(160, 402, "площина екватора", size=12, color=MUTED, anchor="start"))

    # допоміжне коло радіуса a та чверть еліпса
    circ, ell, d = [], [], 0.0
    while d <= 90.0 + 1e-9:
        r_ = math.radians(d)
        circ.append((ox + A * math.cos(r_), oy - A * math.sin(r_)))
        ell.append((ox + A * math.cos(r_), oy - B * math.sin(r_)))
        d += 1.0
    f.append(_poly(circ, MUTED, 1.8, dash="8,5"))
    f.append(_poly(ell, INK, 2.8))
    f.append(text(360, 108, "допоміжне коло радіуса a", size=12, color=MUTED, anchor="start"))

    # знесення точки з еліпса на коло
    f.append(line(pxx, pyy, cxx, cyy, color=MUTED, sw=1.6, dash="5,4"))

    # промені й нормаль
    f.append(line(ox, oy, cxx, cyy, color=NEG, sw=2.2))
    f.append(line(ox, oy, pxx, pyy, color=FIELD, sw=2.2))
    f.append(line(ox, qy, pxx, pyy, color=POS, sw=2.4))
    f.append(line(ox, qy, ox + 150, qy, color=MUTED, sw=1.2, dash="4,4"))

    # дуги кутів
    f.append(_ang_arc(ox, oy, 112, 0.0, math.degrees(psi), color=FIELD))
    f.append(_ang_arc(ox, oy, 186, 0.0, 45.0, color=NEG))
    f.append(_ang_arc(ox, qy, 88, 0.0, math.degrees(phi), color=POS))

    a1 = math.radians(math.degrees(psi) / 2)
    f.append(text(ox + 132 * math.cos(a1), oy - 132 * math.sin(a1) + 5,
                  "ψ", size=17, bold=True, color=FIELD))
    a2 = math.radians(22.5)
    f.append(text(ox + 206 * math.cos(a2), oy - 206 * math.sin(a2) + 5,
                  "β", size=17, bold=True, color=NEG))
    a3 = math.radians(math.degrees(phi) / 2)
    f.append(text(ox + 106 * math.cos(a3), qy - 106 * math.sin(a3) + 5,
                  "φ", size=17, bold=True, color=POS))

    # точки
    f.append(circle(pxx, pyy, 5.5, fill=FIELD, stroke=FIELD))
    f.append(text(pxx + 18, pyy + 6, "P", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(circle(cxx, cyy, 5.5, fill=NEG, stroke=NEG))
    f.append(text(cxx + 18, cyy + 6, "P′", size=15, bold=True, color=NEG, anchor="start"))
    f.append(circle(ox, oy, 5.0, fill=INK, stroke=INK))
    f.append(text(ox - 14, oy + 22, "O", size=14, bold=True, color=INK, anchor="end"))
    f.append(circle(ox, qy, 5.0, fill=POS, stroke=POS))

    f.append(fitbox(600, 165, 280, 235, "\n".join([
        "P — точка на еліпсі;",
        "P′ — знесена вертикально",
        "на коло радіуса a.",
        "",
        "β — параметрична широта",
        "ψ — геоцентрична",
        "φ — геодезична",
        "",
        "tan β = (b/a)·tan φ",
        "tan ψ = (b/a)·tan β",
        "Тангенси трьох широт —",
        "геометрична прогресія.",
    ]), size=13, fill="#eef2fd", stroke=NEG, sw=1.6))

    f.append(text(470, 590, "сплюснутість на рисунку перебільшена в десятки разів",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "three-latitudes.svg"), W, H, *f)


# ── Фігура 7: наскільки розходяться три широти ──────────────────────────────
def latitude_difference():
    W, H = 900, 500
    X0, X1 = 110.0, 790.0
    Y0, Y1 = 400.0, 90.0          # y для 0′ і для 14′
    YMAX = 14.0
    a_, invf = 6378137.0, 298.257223563
    ff = 1.0 / invf
    e2 = 2 * ff - ff * ff
    k1, k2 = 1.0 - e2, math.sqrt(1.0 - e2)

    def sx(phi_deg):
        return X0 + (X1 - X0) * phi_deg / 90.0

    def sy(arcmin):
        return Y0 + (Y1 - Y0) * arcmin / YMAX

    def curve(k):
        pts, d = [], 0.0
        while d <= 90.0 + 1e-9:
            p = math.radians(d)
            q = math.atan(k * math.tan(p)) if d < 89.999 else p
            pts.append((sx(d), sy(math.degrees(p - q) * 60.0)))
            d += 0.5
        return pts

    f = [text(W / 2, 34, "Розбіжність широт: найбільша біля 45°, на полюсах і екваторі — нуль",
              size=16, bold=True)]

    # осі й поділки
    f.append(line(X0, Y0, X1 + 14, Y0, color=INK, sw=1.8))
    f.append(line(X0, Y0, X0, Y1 - 6, color=INK, sw=1.8))
    for d in range(0, 91, 15):
        f.append(line(sx(d), Y0, sx(d), Y0 + 7, color=INK, sw=1.4))
        f.append(text(sx(d), Y0 + 24, "%d°" % d, size=12, color=INK))
    for v in range(0, 15, 2):
        f.append(line(X0 - 7, sy(v), X0, sy(v), color=INK, sw=1.4))
        f.append(text(X0 - 13, sy(v) + 5, "%d′" % v, size=12, color=INK, anchor="end"))
    f.append(text(X0, 66, "різниця, кутові хвилини", size=13, color=INK, anchor="start"))
    f.append(text((X0 + X1) / 2, Y0 + 50, "геодезична широта φ", size=13, color=INK))

    f.append(_poly(curve(k1), POS, 2.8))
    f.append(_poly(curve(k2), NEG, 2.8))

    # легенда — у вільному верхньому лівому куті поля
    f.append(line(150, 102, 186, 102, color=POS, sw=3.0))
    f.append(text(194, 107, "φ − ψ  (геодезична мінус геоцентрична)",
                  size=13, color=POS, anchor="start"))
    f.append(line(150, 130, 186, 130, color=NEG, sw=3.0))
    f.append(text(194, 135, "φ − β  (геодезична мінус параметрична)",
                  size=13, color=NEG, anchor="start"))

    # максимум
    pm = math.atan(1.0 / math.sqrt(k1))
    dm = math.degrees(pm - math.atan(k1 * math.tan(pm))) * 60.0
    mx, my = sx(math.degrees(pm)), sy(dm)
    f.append(circle(mx, my, 5.5, fill=POS, stroke=POS))
    f.append(line(mx + 6, my - 4, 566, 112, color=MUTED, sw=1.2))
    f.append(text(572, 116, "11.545′ при φ = 45°05′46″", size=13, color=POS, anchor="start"))

    f.append(text((X0 + X1) / 2, Y0 + 76,
                  "верхня крива рівно вдвічі вища за нижню: параметрична широта лягає посередині",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "latitude-difference.svg"), W, H, *f)


# ── Ланцюг переходу між датумами (до вставки proj-datum-shift) ─────────────
def datum_chain():
    W, H = 1180, 330
    f = []

    cx = [120.0, 430.0, 740.0, 1050.0]
    cy = 165.0
    half = 87.5                                   # піврозмір рамки (min_w = 175)

    labels = [
        ["φ, λ, h", "у СК-42"],
        ["X, Y, Z", "у СК-42"],
        ["X, Y, Z", "у WGS-84"],
        ["φ, λ, h", "у WGS-84"],
    ]
    tints = [("#f4f6f8", LINE), ("#eef2fd", NEG), ("#eef2fd", NEG), ("#eefaf1", FIELD)]
    for x, ls, (fill, stroke) in zip(cx, labels, tints):
        body, _, _ = textbox(x, cy, ls, size=15, min_w=2 * half,
                             fill=fill, stroke=stroke, sw=1.8, bold=True)
        f.append(body)

    # Стрілки між рамками; середня (Гельмерт) виділена зеленим і товщою.
    steps = [
        (["еліпсоїд Красовського", "a = 6 378 245 м,  1/f = 298.3"], LINE, 2.0),
        (["Гельмерт: три зсуви,", "три повороти, масштаб"], FIELD, 3.0),
        (["еліпсоїд WGS-84,", "формула Боурінґа"], LINE, 2.0),
    ]
    for i, (txt, color, sw) in enumerate(steps):
        x0 = cx[i] + half + 8
        x1 = cx[i + 1] - half - 8
        f.append(arrow(x0, cy, x1, cy, color=color, sw=sw))
        f.append(mtext((x0 + x1) / 2, 90, txt, size=12, color=color))

    # Нижній перекреслений шлях: прямо з кутів у кути дороги немає.
    yb = 262.0
    f.append(line(cx[0], cy + 32, cx[0], yb, color=POS, sw=1.4, dash="4,4"))
    f.append(line(cx[3], yb, cx[3], cy + 32, color=POS, sw=1.4, dash="4,4"))

    note = "прямої лінійної дороги між кутами немає"
    mid = (cx[0] + cx[3]) / 2
    nb, nw, _ = textbox(mid, yb, note, size=13, fill=BG, stroke=POS, sw=1.6, color=POS)
    gap = nw / 2 + 12
    f.append(line(cx[0], yb, mid - gap, yb, color=POS, sw=1.8, dash="7,5"))
    f.append(arrow(mid + gap, yb, cx[3], yb, color=POS, sw=1.8))
    f.append(nb)

    # Перекреслення на лівому відтинку.
    xx, r = 250.0, 11.0
    f.append(line(xx - r, yb - r, xx + r, yb + r, color=POS, sw=2.6))
    f.append(line(xx - r, yb + r, xx + r, yb - r, color=POS, sw=2.6))

    render(os.path.join(IMG, "datum-chain.svg"), W, H, *f)


# ── Дві конвенції знаків поворотів (до вставки proj-datum-shift) ───────────
def helmert_conventions():
    W, H = 1000, 450
    f = []
    ANG = 30.0          # напрям на точку P
    TURN = 24.0         # поворот, СИЛЬНО перебільшений (насправді 0.736″)
    RAD = 145.0
    AX = 175.0
    oy = 265.0

    def pt(ox, oy_, ang, r):
        a = math.radians(ang)
        return ox + r * math.cos(a), oy_ - r * math.sin(a)

    def axes(ox, ang, color, dash, lx, ly):
        g = []
        xe = pt(ox, oy, ang, AX)
        ye = pt(ox, oy, ang + 90.0, AX)
        if dash:
            g.append(_poly([(ox, oy), xe], color, sw=2.0, dash=dash))
            g.append(_poly([(ox, oy), ye], color, sw=2.0, dash=dash))
        else:
            g.append(arrow(ox, oy, xe[0], xe[1], color=color, sw=2.0))
            g.append(arrow(ox, oy, ye[0], ye[1], color=color, sw=2.0))
        g.append(text(xe[0] + 22, xe[1] + 6, lx, size=15, color=color, bold=True))
        g.append(text(ye[0] - 8, ye[1] - 18, ly, size=15, color=color, bold=True))
        return g

    # ── ліворуч: повертають вектор положення, осі стоять ──
    ox = 245.0
    f.append(text(ox, 60, "position vector · EPSG 9606", size=16, bold=True))
    f.append(text(ox, 86, "повертають ТОЧКУ, осі стоять", size=13, color=MUTED))
    f += axes(ox, 0.0, INK, None, "X", "Y")
    p0 = pt(ox, oy, ANG, RAD)
    p1 = pt(ox, oy, ANG + TURN, RAD)
    f.append(_poly([(ox, oy), p0], MUTED, sw=2.0, dash="5,4"))
    f.append(circle(p0[0], p0[1], 5.5, fill=MUTED, stroke=MUTED))
    f.append(text(p0[0] + 24, p0[1] + 18, "P", size=15, color=MUTED, bold=True))
    f.append(_poly([(ox, oy), p1], POS, sw=2.6))
    f.append(circle(p1[0], p1[1], 5.5, fill=POS, stroke=POS))
    f.append(text(p1[0] - 6, p1[1] - 18, "P′", size=15, color=POS, bold=True))
    arc = [pt(ox, oy, ANG + TURN * k / 12.0, RAD + 26.0) for k in range(13)]
    f.append(_poly(arc, POS, sw=2.0))
    f.append(arrow(arc[-2][0], arc[-2][1], arc[-1][0], arc[-1][1], color=POS, sw=2.0))
    f.append(text(ox + 200, oy - 108, "+Rz", size=14, color=POS, bold=True))

    # ── праворуч: повертають осі, точка стоїть ──
    ox2 = 745.0
    f.append(text(ox2, 60, "coordinate frame · EPSG 9607", size=16, bold=True))
    f.append(text(ox2, 86, "повертають ОСІ, точка стоїть", size=13, color=MUTED))
    f += axes(ox2, 0.0, MUTED, "5,4", "X", "Y")
    f += axes(ox2, TURN, NEG, None, "X′", "Y′")
    q = pt(ox2, oy, ANG, RAD)
    f.append(_poly([(ox2, oy), q], INK, sw=2.6))
    f.append(circle(q[0], q[1], 5.5, fill=INK, stroke=INK))
    f.append(text(q[0] + 24, q[1] + 18, "P", size=15, bold=True))
    arc2 = [pt(ox2, oy, TURN * k / 12.0, AX + 30.0) for k in range(13)]
    f.append(_poly(arc2, NEG, sw=2.0))
    f.append(arrow(arc2[-2][0], arc2[-2][1], arc2[-1][0], arc2[-1][1], color=NEG, sw=2.0))
    f.append(text(ox2 + 250, oy - 56, "+Rz", size=14, color=NEG, bold=True))

    # ── перший рядок матриці: уся різниця в знаках ──
    b1, _, _ = textbox(ox, 388, "X′ = X − Rz·Y + Ry·Z", size=15,
                       fill="#fdf3f2", stroke=POS, sw=1.8, min_w=330)
    b2, _, _ = textbox(ox2, 388, "X′ = X + Rz·Y − Ry·Z", size=15,
                       fill="#eef2fd", stroke=NEG, sw=1.8, min_w=330)
    f.append(b1)
    f.append(b2)
    f.append(text(W / 2, 436, "той самий зв'язок двох систем; поворот на рисунку "
                              "перебільшено в сотні тисяч разів", size=12, color=MUTED))

    render(os.path.join(IMG, "helmert-conventions.svg"), W, H, *f)


if __name__ == "__main__":
    geodetic_latitude()
    datum_fit()
    radii_mn()
    arc_degree()
    normal_segments()
    three_latitudes()
    latitude_difference()
    datum_chain()
    helmert_conventions()
    print("ok")
