# -*- coding: utf-8 -*-
"""Фігури до теми «Закони Кеплера».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

SUN  = "#e0a800"   # Сонце / фокус — тепле золоте
ORB  = "#2457d6"   # орбіта — холодне синє
FAST = "#c0392b"   # швидко / перигелій — гаряче
SLOW = "#2457d6"   # повільно / афелій — холодне
BODY = "#eef3fb"   # заливка еліпса-орбіти


# ── Фігура 1: анатомія еліпса — перший закон ─────────────────────────────────
def fig_ellipse_anatomy():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Перший закон: орбіта — еліпс, Сонце в одному фокусі",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "будь-яка точка еліпса має сталу суму відстаней до двох фокусів",
                  size=12, color=MUTED))

    cx, cy = 400, 258
    a, b = 250, 168
    c = math.sqrt(a * a - b * b)          # ≈ 185
    F1 = (cx - c, cy)                     # Сонце — лівий фокус
    F2 = (cx + c, cy)                     # порожній фокус
    V1 = (cx - a, cy)                     # перигелій (лівий край)
    V2 = (cx + a, cy)                     # афелій (правий край)
    Bt = (cx, cy - b)                     # верхня вершина малої осі

    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
             'stroke-width="2.4"/>' % (cx, cy, a, b, BODY, ORB))
    # центр — маленький хрестик
    f.append(line(cx - 6, cy - 6, cx + 6, cy + 6, color=MUTED, sw=1.3))
    f.append(line(cx - 6, cy + 6, cx + 6, cy - 6, color=MUTED, sw=1.3))

    # b — мала піввісь (вертикаль center→верх), підпис лівіше лінії
    f.append(arrow(cx, cy, cx, Bt[1] + 2, color=FIELD, sw=2.0))
    f.append(text(cx - 15, (cy + Bt[1]) / 2 + 4, "b", size=15, bold=True, color=FIELD, anchor="end"))
    # a — велика піввісь (center→правий край, уздовж осі), підпис вище лінії
    f.append(arrow(cx, cy, V2[0], cy, color=INK, sw=1.8))
    f.append(text((cx + V2[0]) / 2, cy - 12, "a", size=15, bold=True))
    # c — center→лівий фокус, підпис нижче лінії
    f.append(arrow(cx, cy, F1[0], cy, color="#a9760a", sw=2.6))
    f.append(text((cx + F1[0]) / 2, cy + 22, "c", size=15, bold=True, color="#a9760a"))

    # порожній фокус (правий)
    f.append(circle(F2[0], F2[1], 5, fill="none", stroke=MUTED, sw=1.8))
    f.append(text(F2[0] + 4, F2[1] + 24, "порожній фокус", size=11, color=MUTED, anchor="middle"))

    # Сонце у лівому фокусі (підпис лівіше — щоб радіус r₁ не різав напис)
    f.append(circle(F1[0], F1[1], 12, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(F1[0] - 16, F1[1] - 20, "Сонце (фокус)", size=12, bold=True,
                  color="#a9760a", anchor="end"))

    # планета вгорі + два радіуси до фокусів
    t = math.radians(233)
    P = (cx + a * math.cos(t), cy + b * math.sin(t))
    f.append(line(F1[0], F1[1], P[0], P[1], color=FAST, sw=2.0))
    f.append(line(F2[0], F2[1], P[0], P[1], color=INK, sw=1.6, dash="5,4"))
    f.append(circle(P[0], P[1], 7, fill=ORB, stroke=INK, sw=1.4))
    f.append(text(P[0] - 8, P[1] - 14, "планета", size=11, bold=True, anchor="end"))
    f.append(text(213, 190, "r₁", size=13, bold=True, color=FAST, anchor="end"))
    f.append(text(420, 172, "r₂", size=13, italic=True, anchor="middle"))

    # перигелій / афелій під / над вершинами
    f.append(text(V1[0] + 6, cy + 26, "перигелій", size=11, color=FAST, anchor="middle"))
    f.append(text(V1[0] + 6, cy + 42, "(найближче)", size=10, color=MUTED, anchor="middle"))
    f.append(text(V2[0], cy - 24, "афелій", size=11, anchor="middle"))
    f.append(text(V2[0], cy - 40, "(найдальше)", size=10, color=MUTED, anchor="middle"))

    b_, _, _ = textbox(W / 2, 472,
                       ["r₁ + r₂ = 2a для будь-якої точки орбіти",
                        "a, b — півосі · c = a·e — зсув фокуса · e = c/a — витягнутість (0 — коло)"],
                       size=12, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b_)
    return render(os.path.join(IMG, "ellipse-anatomy.svg"), W, H, *f)


# ── Фігура 2: наскільки насправді витягнуті орбіти ───────────────────────────
def fig_eccentricity_gallery():
    W, H = 950, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Наскільки насправді витягнуті орбіти: майже кола зі зсунутим Сонцем",
                  size=15.5, bold=True))
    f.append(text(W / 2, 54, "та сама велика піввісь у всіх — змінюється лише ексцентриситет e",
                  size=12, color=MUTED))

    cy = 178
    rx = 66
    panels = [
        (100, 0.0,   "коло", "e = 0"),
        (290, 0.017, "Земля", "e = 0.017"),
        (480, 0.093, "Марс", "e = 0.093"),
        (670, 0.206, "Меркурій", "e = 0.206"),
        (860, 0.967, "комета Галлея", "e = 0.967"),
    ]
    for pcx, e, name, elab in panels:
        ry = rx * math.sqrt(1 - e * e)
        cc = rx * e                         # зсув фокуса від центра
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (pcx, cy, rx, ry, BODY, ORB))
        # центр
        f.append(line(pcx - 4, cy - 4, pcx + 4, cy + 4, color=MUTED, sw=1.1))
        f.append(line(pcx - 4, cy + 4, pcx + 4, cy - 4, color=MUTED, sw=1.1))
        # Сонце у фокусі (зсунуте вліво)
        f.append(circle(pcx - cc, cy, 6.5, fill="#ffe6a1", stroke=SUN, sw=2))
        f.append(text(pcx, cy + rx + 22, name, size=12.5, bold=True))
        f.append(text(pcx, cy + rx + 40, elab, size=11.5, color=MUTED))

    b_, _, _ = textbox(W / 2, 326,
                       "орбіти планет майже нерозрізнимі з колом — але Сонце помітно зсунуте у фокус; справжні витягнуті еліпси — це комети",
                       size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b_)
    return render(os.path.join(IMG, "eccentricity-gallery.svg"), W, H, *f)


# ── Фігура 3: другий закон — рівні площі за рівний час ────────────────────────
def fig_equal_areas():
    W, H = 840, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Другий закон: за рівний час радіус замітає рівну площу",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "тому біля Сонця планета мчить, а на далекому кінці ледь повзе",
                  size=12, color=MUTED))

    cx, cy = 402, 262
    a, b = 244, 166
    c = math.sqrt(a * a - b * b)
    Fx, Fy = cx - c, cy                    # Сонце — лівий фокус

    def ell(t):
        return (cx + a * math.cos(t), cy + b * math.sin(t))

    def wedge(t0, t1, n=32):
        pts = [(Fx, Fy)]
        for i in range(n + 1):
            pts.append(ell(t0 + (t1 - t0) * i / n))
        s = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0, pts

    da = 0.44
    A_aph, pts_aph = wedge(-da, da)        # афелійний сектор (правий, тонкий)
    lo, hi = 0.2, 2.7                      # перигелійний — під ту саму площу
    for _ in range(46):
        mid = (lo + hi) / 2
        Am, _ = wedge(math.pi - mid, math.pi + mid)
        if Am < A_aph:
            lo = mid
        else:
            hi = mid
    dp = (lo + hi) / 2
    _, pts_per = wedge(math.pi - dp, math.pi + dp)

    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
             'stroke-width="2.2"/>' % (cx, cy, a, b, BODY, ORB))
    WED, WEDL = "#fde6c6", "#d79b34"
    for pts in (pts_aph, pts_per):
        poly = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4" '
                 'fill-opacity="0.92"/>' % (poly, WED, WEDL))

    f.append(circle(Fx, Fy, 12, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(Fx, Fy + 26, "Сонце", size=12, bold=True, color="#a9760a"))

    pp = ell(math.pi)                      # перигелій (ліворуч)
    pa = ell(0.0)                          # афелій (праворуч)
    f.append(circle(pp[0], pp[1], 7, fill=FAST, stroke=INK, sw=1.3))
    f.append(circle(pa[0], pa[1], 7, fill=SLOW, stroke=INK, sw=1.3))
    # дотичні стрілки швидкості: довга біля Сонця, коротка вдалині
    f.append(arrow(pp[0], pp[1] - 8, pp[0], pp[1] - 84, color=FAST, sw=3.4))
    f.append(text(pp[0], pp[1] - 96, "швидко", size=12.5, bold=True, color=FAST))
    f.append(text(pp[0], pp[1] - 112, "довга дуга за Δt", size=10.5, color=FAST))
    f.append(arrow(pa[0], pa[1] - 8, pa[0], pa[1] - 40, color=SLOW, sw=3.4))
    f.append(text(pa[0], pa[1] - 52, "повільно", size=12.5, bold=True, color=SLOW))
    f.append(text(pa[0], pa[1] - 68, "коротка дуга за Δt", size=10.5, color=SLOW))

    f.append(text(pp[0] + 4, pp[1] + 26, "перигелій", size=11, color=MUTED, anchor="middle"))
    f.append(text(pa[0], pa[1] + 26, "афелій", size=11, color=MUTED, anchor="middle"))

    b_, _, _ = textbox(W / 2, 452,
                       "рівні площі за рівний час   ⟺   стала швидкість замітання dA/dt   (те саме, що збереження моменту імпульсу)",
                       size=12.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b_)
    return render(os.path.join(IMG, "equal-areas.svg"), W, H, *f)


# ── Фігура 4: третій закон — T² ∝ a³ на всіх планетах ────────────────────────
def fig_third_law():
    W, H = 850, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Третій закон: T² ∝ a³ — усі планети на одній прямій",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "у подвійному логарифмічному масштабі закон степеня 3/2 стає прямою",
                  size=12, color=MUTED))

    planets = [
        ("Меркурій", 0.387, 0.241),
        ("Венера",   0.723, 0.615),
        ("Земля",    1.000, 1.000),
        ("Марс",     1.524, 1.881),
        ("Юпітер",   5.203, 11.862),
        ("Сатурн",   9.537, 29.457),
    ]

    L, R, Tp, Bm = 108, 636, 84, 432
    axmin, axmax = -0.55, 1.08             # log10 a
    aymin, aymax = -0.78, 1.60             # log10 T

    def X(la): return L + (la - axmin) / (axmax - axmin) * (R - L)
    def Y(lt): return Bm - (lt - aymin) / (aymax - aymin) * (Bm - Tp)

    f.append(rect(L, Tp, R - L, Bm - Tp, fill="#fcfcfd", stroke=LINE, sw=1.2))

    # сітка по a
    for av in (0.5, 1, 2, 5, 10):
        xx = X(math.log10(av))
        f.append(line(xx, Tp, xx, Bm, color="#eef1f5", sw=1.0))
        f.append(line(xx, Bm, xx, Bm + 5, color=LINE, sw=1.0))
        f.append(text(xx, Bm + 20, ("%g" % av), size=11, color=MUTED))
    # сітка по T
    for tv in (0.3, 1, 3, 10, 30):
        yy = Y(math.log10(tv))
        f.append(line(L, yy, R, yy, color="#eef1f5", sw=1.0))
        f.append(text(L - 10, yy + 4, ("%g" % tv), size=11, color=MUTED, anchor="end"))

    f.append(text((L + R) / 2, Bm + 42, "велика піввісь a  (а.о., лог-шкала)", size=12.5, bold=True))
    f.append(text(L - 44, (Tp + Bm) / 2, "період T", size=12.5, bold=True, color=INK))
    f.append(text(L - 44, (Tp + Bm) / 2 + 18, "(роки, лог)", size=10.5, color=MUTED))

    # пряма нахилу 3/2 через Землю (0,0)
    la0, la1 = -0.5, 1.02
    f.append(line(X(la0), Y(1.5 * la0), X(la1), Y(1.5 * la1), color=FAST, sw=2.2))
    f.append(text(X(-0.34), Y(1.02), "нахил 3/2", size=12.5, bold=True,
                  color=FAST, anchor="start"))
    f.append(text(X(-0.34), Y(1.02) + 17, "T ∝ a^1.5", size=11, color=FAST, anchor="start"))

    # точки-планети — підписи нижче точок, поза похилою прямою
    for name, av, tv in planets:
        xx, yy = X(math.log10(av)), Y(math.log10(tv))
        f.append(circle(xx, yy, 5.5, fill=ORB, stroke=INK, sw=1.3))
        f.append(text(xx, yy + 20, name, size=11.5, bold=True, anchor="middle"))

    # бічний стовпчик: T²/a³ ≈ 1 для всіх
    sx = 664
    f.append(text(sx, 108, "T² / a³", size=13, bold=True, anchor="start"))
    f.append(text(sx, 126, "(рік² / а.о.³)", size=10.5, color=MUTED, anchor="start"))
    yy = 156
    for name, av, tv in planets:
        ratio = (tv * tv) / (av ** 3)
        f.append(text(sx, yy, name, size=11.5, anchor="start"))
        f.append(text(sx + 168, yy, "%.3f" % ratio, size=11.5, bold=True,
                      color=FIELD, anchor="end"))
        yy += 26
    f.append(line(sx, yy - 12, sx + 168, yy - 12, color=LINE, sw=1.0))
    f.append(text(sx, yy + 8, "однакове число", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(sx, yy + 24, "для кожної планети", size=11, color=MUTED, anchor="start"))

    b_, _, _ = textbox(W / 2, 476,
                       "квадрат періоду ділиться на куб півосі — і виходить те саме для всіх планет Сонця",
                       size=12.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b_)
    return render(os.path.join(IMG, "third-law.svg"), W, H, *f)


# ── Фігура 5 (hist): шлях від даних Тихо до Рудольфових таблиць ───────────────
def fig_kepler_timeline():
    W, H = 1400, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Від даних Тихо до Рудольфових таблиць: як народилися три закони",
                  size=16, bold=True))
    f.append(text(W / 2, 52, "шістдесят років — від першого виміру до надрукованих таблиць",
                  size=12, color=MUTED))

    # маленька легенда кольорів
    lg = [(SUN, "Тихо Браге (данець)"), (ORB, "Кеплер (німець)"), (FIELD, "друковані праці")]
    lx = W / 2 - 250
    for col, lab in lg:
        f.append(circle(lx, 70, 5.5, fill=col, stroke=INK, sw=1.1))
        f.append(text(lx + 12, 74, lab, size=11.5, color=INK, anchor="start"))
        lx += 175

    L, R = 80, 1320
    ymin, ymax = 1543.0, 1633.0
    base = 236

    def X(yr):
        return L + (yr - ymin) / (ymax - ymin) * (R - L)

    # вісь часу
    f.append(line(L, base, R, base, color=LINE, sw=2.0))
    for yr in (1550, 1560, 1570, 1580, 1590, 1600, 1610, 1620, 1630):
        xx = X(yr)
        f.append(line(xx, base - 4, xx, base + 4, color=MUTED, sw=1.1))

    # відрізок «війни з Марсом» 1600–1609
    f.append(line(X(1600), base, X(1609), base, color=FAST, sw=6.0))

    # віхи: (рік_позиції, сторона, колір, підпис-рік, [рядки])
    miles = [
        (1546, "up",   SUN,   "1546",    ["Тихо Браге", "народжений"]),
        (1571, "down", ORB,   "1571",    ["Кеплер", "народжений"]),
        (1600, "up",   ORB,   "1600",    ["Кеплер їде до Тихо,", "Прага; «війна з Марсом»"]),
        (1601, "down", SUN,   "1601",    ["смерть Тихо;", "дані — Кеплеру"]),
        (1609, "up",   FIELD, "1609",    ["Astronomia Nova:", "перші два закони"]),
        (1618.5, "down", FIELD, "1618–19", ["третій закон; Harmonices", "Mundi, «музика сфер»"]),
        (1627, "up",   FIELD, "1627",    ["Рудольфові таблиці", "(уже з логарифмами)"]),
        (1630, "down", ORB,   "1630",    ["смерть", "Кеплера"]),
    ]
    for yr, side, col, ylab, caps in miles:
        xx = X(yr)
        if side == "up":
            f.append(line(xx, base - 6, xx, 158, color=col, sw=1.6, dash="3,3"))
            f.append(text(xx, 122, ylab, size=14.5, bold=True, color=col))
            f.append(text(xx, 138, caps[0], size=11, color=INK))
            f.append(text(xx, 152, caps[1], size=11, color=INK))
        else:
            f.append(line(xx, base + 6, xx, 314, color=col, sw=1.6, dash="3,3"))
            f.append(text(xx, 330, ylab, size=14.5, bold=True, color=col))
            f.append(text(xx, 346, caps[0], size=11, color=INK))
            f.append(text(xx, 360, caps[1], size=11, color=INK))
        f.append(circle(xx, base, 6.0, fill=col, stroke=INK, sw=1.3))

    b_, _, _ = textbox(W / 2, 430,
                       ["червоний відрізок — «війна з Марсом»: майже десятиліття без логарифмів,",
                        "≈70 перерахунків орбіти й вісім кутових хвилин, що зламали двотисячолітнє коло"],
                       size=12, pad=10, fill="#fdecea", stroke=FAST, sw=1.4)
    f.append(b_)
    return render(os.path.join(IMG, "kepler-timeline.svg"), W, H, *f)


# ── Фігура 6 (proj): три аномалії — M, E, ν ──────────────────────────────────
def fig_anomalies():
    W, H = 940, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три аномалії: як час (M) стає кутом планети (ν)",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "рівняння Кеплера M = E − e·sinE звʼязує рівномірний час із геометрією еліпса",
                  size=12, color=MUTED))

    cx, cy = 330, 300
    a, e = 175.0, 0.5
    b = a * math.sqrt(1 - e * e)
    c = a * e
    Sx, Sy = cx + c, cy                 # Сонце — правий фокус
    Vx, Vy = cx + a, cy                 # перигелій — права вершина
    Em = math.radians(72)

    def ell(t): return (cx + a * math.cos(t), cy - b * math.sin(t))
    def cir(t): return (cx + a * math.cos(t), cy - a * math.sin(t))
    Q, P = cir(Em), ell(Em)
    nu = math.atan2(cy - P[1], P[0] - Sx)     # істинна аномалія (фізичний кут)

    # допоміжне коло (пунктир) + велика вісь
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="4,5"/>' % (cx, cy, a, MUTED))
    f.append(line(cx - a, cy, cx + a, cy, color=MUTED, sw=1.0, dash="2,4"))

    # зафарбований сектор площі S–перигелій–P (це і є M)
    sec = [(Sx, Sy)]
    for i in range(41):
        sec.append(ell(Em * i / 40))
    f.append('<polygon points="%s" fill="#fde9c8" stroke="#e7b467" '
             'stroke-width="1.2" fill-opacity="0.85"/>'
             % " ".join("%.1f,%.1f" % p for p in sec))

    # орбіта
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
             'stroke="%s" stroke-width="2.4"/>' % (cx, cy, a, b, ORB))

    # проєкція P↔Q, радіус кола O→Q, фокальний радіус S→P
    f.append(line(P[0], P[1], Q[0], Q[1], color=FAST, sw=1.6, dash="4,3"))
    f.append(line(cx, cy, Q[0], Q[1], color=INK, sw=1.5))
    f.append(line(Sx, Sy, P[0], P[1], color=FAST, sw=2.2))

    # дуга кута E при центрі
    ea = [(cx + 44 * math.cos(Em * i / 24), cy - 44 * math.sin(Em * i / 24)) for i in range(25)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in ea), INK))
    f.append(text(cx + 62 * math.cos(Em / 2), cy - 62 * math.sin(Em / 2), "E", size=15, bold=True))

    # дуга кута ν при фокусі
    na = [(Sx + 34 * math.cos(nu * i / 24), Sy - 34 * math.sin(nu * i / 24)) for i in range(25)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in na), FAST))
    f.append(text(Sx + 48 * math.cos(nu * 0.5) + 6, Sy - 48 * math.sin(nu * 0.5),
                  "ν", size=15, bold=True, color=FAST))

    # площа = M (підпис у тілі сектора, з запасом від дуг)
    f.append(text(455, 208, "площа ∝ M", size=12, bold=True, color="#a9760a"))
    f.append(text(455, 224, "(∝ час, 2-й закон)", size=10.5, color="#a9760a"))

    # точки й підписи
    f.append(circle(cx, cy, 3, fill=INK, stroke=INK, sw=1))
    f.append(text(cx - 10, cy + 18, "центр O", size=11, color=MUTED, anchor="end"))
    f.append(circle(Q[0], Q[1], 5, fill="none", stroke=INK, sw=1.6))
    f.append(text(Q[0] - 10, Q[1] - 6, "Q", size=12, bold=True, anchor="end"))
    f.append(circle(P[0], P[1], 7, fill=ORB, stroke=INK, sw=1.4))
    f.append(text(P[0] - 12, P[1] + 4, "планета P", size=11.5, bold=True, anchor="end"))
    f.append(circle(Sx, Sy, 11, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(Sx, Sy + 28, "Сонце (фокус S)", size=11.5, bold=True, color="#a9760a"))
    f.append(circle(Vx, Vy, 4, fill=FAST, stroke=INK, sw=1))
    f.append(text(Vx + 6, Vy + 20, "перигелій", size=11, color=MUTED, anchor="middle"))
    f.append(text(cx - a + 4, cy + a - 6, "допоміжне коло (радіус a)",
                  size=10.5, color=MUTED, anchor="start"))

    b_, _, _ = textbox(W / 2, 552,
                       ["M = E − e·sinE   — рівняння Кеплера: час (M) → ексцентрична аномалія E",
                        "r = a(1 − e·cosE)      x = a(cosE − e)      y = a·√(1−e²)·sinE",
                        "tan(ν/2) = √((1+e)/(1−e))·tan(E/2)   — від E до істинного кута ν"],
                       size=12.5, pad=11, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b_)
    return render(os.path.join(IMG, "anomalies.svg"), W, H, *f)


# ── Фігура 7 (proj): чому комети важкі — майже пласке рівняння ────────────────
def fig_convergence():
    W, H = 900, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Чому комети важкі: біля перигелію рівняння майже пласке",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "M(E) = E − e·sinE; для комети похідна 1−e ≈ 0 при E→0, тож обернення погано обумовлене",
                  size=12, color=MUTED))

    L, R, Tp, Bm = 92, 566, 92, 452

    def X(Ed): return L + Ed / 180.0 * (R - L)
    def Y(Md): return Bm - Md / 180.0 * (Bm - Tp)

    f.append(rect(L, Tp, R - L, Bm - Tp, fill="#fcfcfd", stroke=LINE, sw=1.2))
    for v in (0, 45, 90, 135, 180):
        xx, yy = X(v), Y(v)
        f.append(line(xx, Tp, xx, Bm, color="#eef1f5", sw=1.0))
        f.append(line(L, yy, R, yy, color="#eef1f5", sw=1.0))
        f.append(text(xx, Bm + 18, "%d°" % v, size=11, color=MUTED))
        if v:
            f.append(text(L - 8, yy + 4, "%d°" % v, size=11, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, Bm + 40, "ексцентрична аномалія E", size=12.5, bold=True))
    f.append(text(L - 52, (Tp + Bm) / 2, "M", size=13, bold=True, anchor="middle"))
    f.append(text(L - 52, (Tp + Bm) / 2 + 16, "(час)", size=10, color=MUTED, anchor="middle"))

    # діагональ M=E (орієнтир для e=0)
    f.append(line(X(0), Y(0), X(180), Y(180), color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(X(150) + 6, Y(150) + 14, "M = E  (коло, e=0)", size=10.5, color=MUTED, anchor="start"))

    def curve(e, col, sw):
        pts = []
        for k in range(0, 181, 2):
            Er = math.radians(k)
            Md = math.degrees(Er - e * math.sin(Er))
            pts.append((X(k), Y(Md)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (" ".join("%.1f,%.1f" % p for p in pts), col, sw))

    curve(0.1, ORB, 2.6)      # планета
    curve(0.967, FAST, 2.6)   # комета

    # горизонталь M=10° і дві точки-розвʼязки
    Mline = 10.0
    f.append(line(L, Y(Mline), R, Y(Mline), color=INK, sw=1.2, dash="2,3"))
    f.append(text(R - 4, Y(Mline) - 6, "той самий M = 10°", size=10.5, anchor="end"))
    Ep, Ec = 11.1, 55.85      # розвʼязки для e=0.1 і e=0.967 (з коду)
    for Ed, col, lab in ((Ep, ORB, "E≈11°"), (Ec, FAST, "E≈56°")):
        f.append(circle(X(Ed), Y(Mline), 5, fill=col, stroke=INK, sw=1.3))
        f.append(line(X(Ed), Y(Mline), X(Ed), Bm, color=col, sw=1.0, dash="2,3"))
        f.append(text(X(Ed), Y(Mline) - 10, lab, size=11, bold=True, color=col))

    # позначка «пласко» біля початку координат
    f.append(text(X(70), Y(3), "комета: тут dM/dE = 1−e ≈ 0.03 → майже пласко",
                  size=11, bold=True, color=FAST, anchor="start"))
    f.append(text(X(70), Y(3) + 15, "малий M «розтягується» у широкий діапазон E → Ньютон перестрибує",
                  size=10, color=MUTED, anchor="start"))

    # легенда
    f.append(circle(R - 150, Tp + 20, 5, fill=ORB, stroke=INK, sw=1))
    f.append(text(R - 140, Tp + 24, "планета  e = 0.1", size=11, anchor="start"))
    f.append(circle(R - 150, Tp + 40, 5, fill=FAST, stroke=INK, sw=1))
    f.append(text(R - 140, Tp + 44, "комета  e = 0.967", size=11, anchor="start"))

    b_, _, _ = textbox(W / 2, 500,
                       ["той самий крок часу M = 10°: у планети E≈11°, у комети E≈56° — обернена задача",
                        "різко чутлива; лік — стартувати з E₀ = π і спускатися монотонно, а не з E₀ = M"],
                       size=12, pad=10, fill="#fdecea", stroke=FAST, sw=1.5)
    f.append(b_)
    return render(os.path.join(IMG, "kepler-convergence.svg"), W, H, *f)


# ── Фігура 8 (math): чому b = a·√(1−e²) — прямокутний трикутник ───────────────
def fig_b_from_string():
    W, H = 900, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Чому b = a·√(1 − e²): один прямокутний трикутник",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "нитка від фокуса до кінця малої осі має довжину рівно a",
                  size=12, color=MUTED))

    cx, cy = 300, 300
    a, b = 210, 140
    c = math.sqrt(a * a - b * b)          # ≈ 156.5
    F1 = (cx - c, cy)                     # Сонце — лівий фокус
    F2 = (cx + c, cy)                     # порожній фокус
    Bt = (cx, cy - b)                     # кінець малої осі (верхівка)

    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
             'stroke-width="2.4"/>' % (cx, cy, a, b, BODY, ORB))

    # підсвічений прямокутний трикутник center–F1–Bt
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eafaf1" '
             'stroke="none"/>' % (cx, cy, F1[0], F1[1], Bt[0], Bt[1]))

    # катет c: center→лівий фокус
    f.append(line(cx, cy, F1[0], F1[1], color="#a9760a", sw=2.8))
    f.append(text((cx + F1[0]) / 2, cy + 22, "c", size=15, bold=True, color="#a9760a"))
    # катет b: center→верхівка
    f.append(line(cx, cy, Bt[0], Bt[1], color=FIELD, sw=2.6))
    f.append(text(cx - 16, (cy + Bt[1]) / 2 + 4, "b", size=15, bold=True, color=FIELD, anchor="end"))
    # гіпотенуза a: лівий фокус→верхівка (нитка)
    f.append(line(F1[0], F1[1], Bt[0], Bt[1], color=FAST, sw=2.8))
    f.append(text((F1[0] + Bt[0]) / 2 - 16, (F1[1] + Bt[1]) / 2 - 6,
                  "a", size=15, bold=True, color=FAST, anchor="end"))
    # друга нитка: правий фокус→верхівка (пунктир, теж a)
    f.append(line(F2[0], F2[1], Bt[0], Bt[1], color=INK, sw=1.6, dash="5,4"))
    f.append(text((F2[0] + Bt[0]) / 2 + 16, (F2[1] + Bt[1]) / 2 - 6,
                  "a", size=14, italic=True, anchor="start"))

    # прямий кут у центрі
    f.append(line(cx - 14, cy, cx - 14, cy - 14, color=INK, sw=1.3))
    f.append(line(cx - 14, cy - 14, cx, cy - 14, color=INK, sw=1.3))
    # центр — хрестик
    f.append(line(cx - 5, cy - 5, cx + 5, cy + 5, color=MUTED, sw=1.2))
    f.append(line(cx - 5, cy + 5, cx + 5, cy - 5, color=MUTED, sw=1.2))
    f.append(text(cx + 8, cy + 22, "центр", size=10.5, color=MUTED, anchor="start"))

    # фокуси
    f.append(circle(F1[0], F1[1], 11, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(F1[0], F1[1] + 30, "фокус (Сонце)", size=11, bold=True, color="#a9760a"))
    f.append(circle(F2[0], F2[1], 5, fill="none", stroke=MUTED, sw=1.8))
    f.append(text(F2[0], F2[1] + 28, "порожній фокус", size=10.5, color=MUTED))

    # верхівка малої осі
    f.append(circle(Bt[0], Bt[1], 6, fill=ORB, stroke=INK, sw=1.3))
    f.append(text(Bt[0], Bt[1] - 14, "кінець малої осі", size=11, anchor="middle"))
    f.append(text(Bt[0], Bt[1] - 30, "(рівновіддалений від фокусів)", size=9.5,
                  color=MUTED, anchor="middle"))

    # права панель — формули й значення
    px, pw, py, ph = 588, 296, 108, 316
    f.append(rect(px, py, pw, ph, fill="#fbfbfd", stroke=LINE, sw=1.3))
    tx = px + 20
    f.append(text(tx, py + 34, "a² = b² + c²", size=17, bold=True, anchor="start"))
    f.append(text(tx, py + 58, "гіпотенуза a, катети b і c", size=11, color=MUTED, anchor="start"))
    f.append(line(tx, py + 74, px + pw - 20, py + 74, color="#e2e6ea", sw=1.0))
    f.append(text(tx, py + 102, "b = a·√(1 − e²)", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(text(tx, py + 128, "c = a·e      e = c/a", size=14, bold=True, color="#a9760a", anchor="start"))
    f.append(line(tx, py + 146, px + pw - 20, py + 146, color="#e2e6ea", sw=1.0))
    f.append(text(tx, py + 172, "сплюснутість b/a = √(1 − e²):", size=12, bold=True, anchor="start"))
    f.append(text(tx, py + 196, "Земля   e=0.017  →  b/a = 0.99986", size=12, anchor="start"))
    f.append(text(tx, py + 220, "Марс    e=0.093  →  b/a = 0.9956", size=12, anchor="start"))
    f.append(text(tx, py + 244, "Галлея  e=0.967  →  b/a = 0.255", size=12, anchor="start"))
    f.append(text(tx, py + 274, "мале e → орбіта майже коло,", size=11, color=MUTED, anchor="start"))
    f.append(text(tx, py + 292, "але фокус помітно збоку (c = a·e)", size=11, color=MUTED, anchor="start"))

    b_, _, _ = textbox(W / 2, 496,
                       "верхівка малої осі рівновіддалена від фокусів  ⟹  кожна нитка = a  ⟹  a² = b² + c²",
                       size=12, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b_)
    return render(os.path.join(IMG, "ellipse-b-triangle.svg"), W, H, *f)


# ── Фігура 9 (math): фокальне рівняння r(θ) = p/(1+e·cosθ) ────────────────────
def fig_focal_polar():
    W, H = 900, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Опис із фокуса: r(θ) = p / (1 + e·cos θ)",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "відстань від Сонця як функція справжньої аномалії θ",
                  size=12, color=MUTED))

    e = 0.5
    a = 210.0
    c = a * e                             # 105
    b = a * math.sqrt(1 - e * e)          # 181.9
    p = a * (1 - e * e)                   # 157.5
    Fx, Fy = 250.0, 290.0                 # Сонце (лівий фокус) — початок
    ecx = Fx + c                          # центр еліпса праворуч від Сонця

    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
             'stroke-width="2.4"/>' % (ecx, Fy, a, b, BODY, ORB))

    # вісь перигелію (горизонталь крізь Сонце)
    f.append(line(Fx - (a - c) - 26, Fy, ecx + a + 26, Fy, color=MUTED, sw=1.2, dash="6,5"))

    # перигелій / афелій
    per = (Fx - (a - c), Fy)              # a(1−e) ліворуч
    aph = (ecx + a, Fy)                   # a(1+e) праворуч
    f.append(circle(per[0], per[1], 6, fill=FAST, stroke=INK, sw=1.3))
    f.append(text(per[0], per[1] + 24, "перигелій", size=11, color=FAST))
    f.append(text(per[0], per[1] + 40, "r = a(1−e)", size=10, color=MUTED))
    f.append(text(per[0] - 34, Fy - 8, "θ = 0", size=11, color=MUTED, anchor="end"))
    f.append(circle(aph[0], aph[1], 6, fill=SLOW, stroke=INK, sw=1.3))
    f.append(text(aph[0], aph[1] + 24, "афелій", size=11))
    f.append(text(aph[0], aph[1] + 40, "r = a(1+e)", size=10, color=MUTED))

    # семілатус-ректум p: вгору з Сонця (θ=90°)
    Ptop = (Fx, Fy - p)
    f.append(line(Fx, Fy, Ptop[0], Ptop[1], color=FIELD, sw=2.4))
    f.append(circle(Ptop[0], Ptop[1], 5, fill=ORB, stroke=INK, sw=1.3))
    f.append(text(Fx - 12, (Fy + Ptop[1]) / 2 + 4, "p", size=15, bold=True, color=FIELD, anchor="end"))
    f.append(text(Fx + 10, Ptop[1] - 8, "θ=90° → r = p", size=10.5, color=FIELD, anchor="start"))

    # радіус r під кутом θ до планети
    th = math.radians(65)
    r = p / (1 + e * math.cos(th))
    P = (Fx - r * math.cos(th), Fy - r * math.sin(th))
    f.append(line(Fx, Fy, P[0], P[1], color=INK, sw=2.0))
    f.append(circle(P[0], P[1], 7, fill=ORB, stroke=INK, sw=1.4))
    f.append(text(P[0] - 8, P[1] - 12, "планета", size=11, bold=True, anchor="end"))
    f.append(text((Fx + P[0]) / 2 - 8, (Fy + P[1]) / 2 - 6, "r", size=14, bold=True, anchor="end"))

    # дуга кута θ від осі перигелію до радіуса
    R = 46
    arc = []
    n = 24
    for i in range(n + 1):
        phi = th * i / n
        arc.append((Fx - R * math.cos(phi), Fy - R * math.sin(phi)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in arc), INK))
    f.append(text(Fx - (R + 16) * math.cos(th / 2), Fy - (R + 16) * math.sin(th / 2),
                  "θ", size=14, bold=True))

    # Сонце
    f.append(circle(Fx, Fy, 12, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(Fx, Fy + 26, "Сонце", size=11.5, bold=True, color="#a9760a"))
    f.append(text(Fx, Fy + 42, "(фокус = початок)", size=10, color=MUTED))

    b_, _, _ = textbox(W / 2, 512,
                       ["r(θ) = p / (1 + e·cos θ)      p = a(1 − e²) — фокальний параметр",
                        "θ=0 → a(1−e) перигелій   ·   θ=90° → p   ·   θ=180° → a(1+e) афелій"],
                       size=12.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b_)
    return render(os.path.join(IMG, "focal-polar.svg"), W, H, *f)


# ── Фігура 10 (math): одне рівняння — усі коніки ──────────────────────────────
def fig_one_equation_conics():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Одне рівняння — усі конічні перерізи",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "r = p /(1 + e·cos θ): міняємо саме лише e — і крива міняє тип",
                  size=12, color=MUTED))

    Fx, Fy = 290.0, 300.0
    P_PX = 105.0                          # спільний семілатус-ректум на екрані
    CAP = 205.0                           # обрізаємо нескінченні гілки в межах кадру

    def curve(e, col, cap=CAP, sw=2.6):
        pts, seg = [], []
        N = 720
        for i in range(N + 1):
            th = -math.pi + 2 * math.pi * i / N
            den = 1 + e * math.cos(th)
            if den <= 1e-3:
                if seg:
                    pts.append(seg)
                    seg = []
                continue
            r = P_PX / den
            if r > cap or r < 0:
                if seg:
                    pts.append(seg)
                    seg = []
                continue
            seg.append((Fx - r * math.cos(th), Fy - r * math.sin(th)))
        if seg:
            pts.append(seg)
        out = []
        for s in pts:
            out.append('<polyline points="%s" fill="none" stroke="%s" '
                       'stroke-width="%.1f"/>'
                       % (" ".join("%.1f,%.1f" % q for q in s), col, sw))
        return "".join(out)

    # вісь перигелію
    f.append(line(Fx - 150, Fy, Fx + 470, Fy, color=MUTED, sw=1.1, dash="6,5"))

    # три криві: еліпс (без обрізання), парабола, гіпербола
    f.append(curve(0.6, ORB, cap=10000))
    f.append(curve(1.0, FIELD))
    f.append(curve(1.5, FAST))

    # спільна точка p (θ=90°, вгору з фокуса)
    Ptop = (Fx, Fy - P_PX)
    f.append(line(Fx, Fy, Ptop[0], Ptop[1], color=MUTED, sw=1.4, dash="3,3"))
    f.append(circle(Ptop[0], Ptop[1], 5, fill=INK, stroke=INK, sw=1.2))
    f.append(text(Fx - 12, (Fy + Ptop[1]) / 2 + 4, "p", size=14, bold=True, anchor="end"))

    # Сонце
    f.append(circle(Fx, Fy, 11, fill="#ffe6a1", stroke=SUN, sw=2.2))
    f.append(text(Fx, Fy + 26, "фокус", size=11, bold=True, color="#a9760a"))

    # легенда
    lx = 610
    f.append(rect(lx - 18, 112, 292, 154, fill="#fbfbfd", stroke=LINE, sw=1.2))
    f.append(text(lx - 4, 138, "спільні: фокус і параметр p", size=12, bold=True, anchor="start"))
    rows = [("e = 0.6", "еліпс  (e < 1)", ORB),
            ("e = 1.0", "парабола  (e = 1)", FIELD),
            ("e = 1.5", "гіпербола  (e > 1)", FAST)]
    for i, (lab, desc, col) in enumerate(rows):
        yy = 172 + i * 32
        f.append(line(lx, yy, lx + 34, yy, color=col, sw=3.4))
        f.append(text(lx + 46, yy + 5, lab, size=13, bold=True, anchor="start"))
        f.append(text(lx + 122, yy + 5, desc, size=11.5, anchor="start"))

    b2, _, _ = textbox(W / 2, 528,
                       "e=0 коло · 0<e<1 еліпс · e=1 парабола · e>1 гіпербола — одна формула, змінюється лише e",
                       size=12.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b2)
    return render(os.path.join(IMG, "one-equation-conics.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [fig_ellipse_anatomy(), fig_eccentricity_gallery(),
            fig_equal_areas(), fig_third_law(), fig_kepler_timeline(),
            fig_anomalies(), fig_convergence(),
            fig_b_from_string(), fig_focal_polar(), fig_one_equation_conics()]
    print("written:")
    for p in outs:
        print("  ", p)
