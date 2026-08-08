# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def dot(x, y, r=4.5, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, color)


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


def arcpts(cx, cy, r, a0, a1, n=90):
    """Точки дуги (кути в градусах, стандартні: 0 = праворуч, проти годинникової)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def parab(cx, cy, half, amp, n=64):
    """Парабола з вершиною (cx,cy): підйом amp на краях (amp>0 — угору)."""
    pts = []
    for i in range(n + 1):
        t = -1.0 + 2.0 * i / n
        pts.append((cx + half * t, cy - amp * t * t))
    return pts


# ───────────────────────────────────────────────────────────────────────────
def principal_sections():
    """Два головні перерізи в точці й знак їхнього добутку: чаша, циліндр, сідло."""
    W, H = 980, 420
    frags = []
    panels = [
        (165, "Чаша", 58, 32, "k₁ > 0,   k₂ > 0",
         "обидва перерізи гнуться в один бік", "K = k₁·k₂ > 0", POS),
        (490, "Циліндр", 58, 0, "k₁ = 1/R,   k₂ = 0",
         "уздовж осі поверхня пряма", "K = 0", INK),
        (815, "Сідло", 58, -42, "k₁ > 0,   k₂ < 0",
         "перерізи гнуться в різні боки", "K = k₁·k₂ < 0", NEG),
    ]
    HALF, YB = 118, 155
    for cx, title, a1, a2, l1, l2, concl, col in panels:
        frags.append(text(cx, 38, title, size=17, bold=True))
        frags.append(line(cx - HALF, YB, cx + HALF, YB, color=MUTED, sw=1.4, dash="5 6"))
        frags.append(polyline(parab(cx, YB, HALF, a1), color=POS, sw=2.8))
        if a2 == 0:
            frags.append(line(cx - HALF + 22, YB, cx + HALF - 22, YB, color=NEG, sw=2.8))
        else:
            frags.append(polyline(parab(cx, YB, HALF, a2), color=NEG, sw=2.8))
        frags.append(arrow(cx, YB - 5, cx, YB - 53, color=INK, sw=1.8))
        frags.append(text(cx + 16, 118, "нормаль", size=13, color=MUTED, anchor="start"))
        frags.append(dot(cx, YB, 4.5, INK))
        frags.append(text(cx, 252, l1, size=15))
        frags.append(text(cx, 278, l2, size=13, color=MUTED))
        b, _, _ = textbox(cx, 328, concl, size=15, bold=True, color=col,
                          stroke=col, fill="#ffffff", min_w=190)
        frags.append(b)
    frags.append(text(W / 2, 396,
                      "червона й синя криві — два взаємно перпендикулярні нормальні перерізи, "
                      "накладені на одну картинку", size=13, color=MUTED))
    render(os.path.join(IMG, "principal-sections.svg"), W, H, *frags,
           title="Головні кривини в точці й знак їхнього добутку")


# ───────────────────────────────────────────────────────────────────────────
def circle_defect():
    """Круг радіуса r, розкладений на стіл: бракує клина, збігається, зайвий клин."""
    W, H = 980, 460
    frags = []
    CY, R = 178, 78
    cxs = [165, 490, 815]

    # 1 — площина
    cx = cxs[0]
    frags.append(text(cx, 44, "Площина", size=17, bold=True))
    frags.append(polyline(arcpts(cx, CY, R, 0, 360), color=INK, sw=2.6))
    frags.append(line(cx, CY, cx + R, CY, color=MUTED, sw=1.6))
    frags.append(dot(cx, CY, 4.5, INK))
    frags.append(text(cx + 40, 156, "r", size=15, italic=True))
    frags.append(text(cx, 300, "C = 2πr", size=16, bold=True))
    frags.append(text(cx, 326, "круг лягає точно", size=13, color=MUTED))

    # 2 — купол: вирізаний клин
    cx = cxs[1]
    frags.append(text(cx, 44, "Купол,  K > 0", size=17, bold=True))
    pts = arcpts(cx, CY, R, 22, 338)
    frags.append(polyline(pts, color=POS, sw=2.6))
    frags.append(line(cx, CY, pts[0][0], pts[0][1], color=POS, sw=2.2))
    frags.append(line(cx, CY, pts[-1][0], pts[-1][1], color=POS, sw=2.2))
    frags.append(dot(cx, CY, 4.5, INK))
    frags.append(text(cx, 300, "C < 2πr", size=16, bold=True, color=POS))
    frags.append(text(cx, 326, "бракує клина", size=13, color=MUTED))

    # 3 — сідло: зайвий клин (край накладається сам на себе)
    cx = cxs[2]
    frags.append(text(cx, 44, "Сідло,  K < 0", size=17, bold=True))
    n, sweep = 150, 400.0
    sp = [(cx + (R + 15.0 * i / n) * math.cos(math.radians(-30 + sweep * i / n)),
           CY - (R + 15.0 * i / n) * math.sin(math.radians(-30 + sweep * i / n)))
          for i in range(n + 1)]
    frags.append(polyline(sp, color=NEG, sw=2.6))
    frags.append(line(cx, CY, sp[0][0], sp[0][1], color=NEG, sw=2.2))
    frags.append(line(cx, CY, sp[-1][0], sp[-1][1], color=NEG, sw=2.2))
    frags.append(dot(cx, CY, 4.5, INK))
    frags.append(text(cx, 300, "C > 2πr", size=16, bold=True, color=NEG))
    frags.append(text(cx, 326, "зайвий клин", size=13, color=MUTED))

    frags.append(text(W / 2, 384, "K = 3·(2πr − C(r)) / (π·r³)   при малому r", size=18, bold=True))
    frags.append(text(W / 2, 424,
                      "Земля, R = 6371 км:   r = 10 км → брак 2.6 см;   "
                      "r = 1000 км → брак 25.8 км", size=14, color=MUTED))
    render(os.path.join(IMG, "circle-defect.svg"), W, H, *frags,
           title="Дефіцит довжини кола як мірило гаусової кривини")


# ───────────────────────────────────────────────────────────────────────────
def bending_invariance():
    """Аркуш → циліндр (K не змінилося) → сфера (потрібен розтяг)."""
    W, H = 1000, 440
    frags = []
    cxs = [175, 500, 825]

    # аркуш
    cx = cxs[0]
    frags.append(text(cx, 52, "Аркуш", size=17, bold=True))
    frags.append(rect(cx - 92, 80, 184, 118, fill="#eef2f6", stroke=INK, sw=2.0, rx=4))
    for k in range(1, 4):
        frags.append(line(cx - 92 + 46 * k, 80, cx - 92 + 46 * k, 198, color=MUTED, sw=1.0))
    for k in range(1, 3):
        frags.append(line(cx - 92, 80 + 39.3 * k, cx + 92, 80 + 39.3 * k, color=MUTED, sw=1.0))

    # циліндр
    cx = cxs[1]
    frags.append(text(cx, 52, "Циліндр радіуса R", size=17, bold=True))
    frags.append(rect(cx - 74, 96, 148, 82, fill="#eef2f6", stroke="none", sw=0, rx=0))
    frags.append(ellipse(cx, 96, 74, 24, fill="#e3e9ef", stroke=INK, sw=2.0))
    frags.append(line(cx - 74, 96, cx - 74, 178, color=INK, sw=2.0))
    frags.append(line(cx + 74, 96, cx + 74, 178, color=INK, sw=2.0))
    frags.append(polyline([(cx - 74 + 148.0 * i / 40,
                            178 + 24 * math.sin(math.pi * i / 40)) for i in range(41)],
                          color=INK, sw=2.0))
    for k in (-37, 0, 37):
        ytop = 96 + 24 * math.sqrt(max(0.0, 1.0 - (k / 74.0) ** 2))
        frags.append(line(cx + k, ytop, cx + k, 178 + 24 * math.sqrt(max(0.0, 1.0 - (k / 74.0) ** 2)),
                          color=MUTED, sw=1.0))

    # сфера
    cx = cxs[2]
    frags.append(text(cx, 52, "Сфера радіуса R", size=17, bold=True))
    frags.append(circle(cx, 139, 71, fill="#eef2f6", stroke=INK, sw=2.0))
    for rx in (24, 48):
        frags.append(ellipse(cx, 139, rx, 71, fill="none", stroke=MUTED, sw=1.0))
    frags.append(line(cx - 71, 139, cx + 71, 139, color=MUTED, sw=1.0))

    rows = [
        ("k₁ = 0", "k₂ = 0", "H = 0", "K = 0"),
        ("k₁ = 1/R", "k₂ = 0", "H = 1/(2R)", "K = 0"),
        ("k₁ = 1/R", "k₂ = 1/R", "H = 1/R", "K = 1/R²"),
    ]
    for cx, r in zip(cxs, rows):
        for j, s in enumerate(r):
            bold = (j == 3)
            col = FIELD if (j == 3 and r[3] == "K = 0") else INK
            frags.append(text(cx, 248 + 24 * j, s, size=15, bold=bold, color=col))

    frags.append(arrow(cxs[0] + 104, 382, cxs[1] - 104, 382, color=FIELD, sw=2.0))
    frags.append(text((cxs[0] + cxs[1]) / 2, 358, "згин без розтягу", size=14, color=FIELD))
    frags.append(text((cxs[0] + cxs[1]) / 2, 410, "K лишилося нулем", size=13, color=MUTED))
    frags.append(arrow(cxs[1] + 104, 382, cxs[2] - 104, 382, color=POS, sw=2.0))
    frags.append(text((cxs[1] + cxs[2]) / 2, 358, "розтяг неминучий", size=14, color=POS))
    frags.append(text((cxs[1] + cxs[2]) / 2, 410, "K мусить змінитися", size=13, color=MUTED))

    render(os.path.join(IMG, "bending-invariance.svg"), W, H, *frags,
           title="Що переживає згин без розтягу, а що ні")


# ───────────────────────────────────────────────────────────────────────────
def angle_excess():
    """Сума кутів геодезичного трикутника: на площині, на сфері, на сідлі."""
    W, H = 960, 420
    frags = []

    def tri(cx, bulge):
        A = (cx - 82, 214)
        B = (cx + 82, 214)
        C = (cx, 92)
        cen = ((A[0] + B[0] + C[0]) / 3.0, (A[1] + B[1] + C[1]) / 3.0)
        d = []
        pts = [A, B, C]
        for i in range(3):
            P, Q = pts[i], pts[(i + 1) % 3]
            mx, my = (P[0] + Q[0]) / 2.0, (P[1] + Q[1]) / 2.0
            vx, vy = mx - cen[0], my - cen[1]
            L = math.hypot(vx, vy) or 1.0
            ctrl = (mx + vx / L * 2 * bulge, my + vy / L * 2 * bulge)
            if i == 0:
                d.append("M %.1f %.1f" % P)
            d.append("Q %.1f %.1f %.1f %.1f" % (ctrl[0], ctrl[1], Q[0], Q[1]))
        d.append("Z")
        return ('<path d="%s" fill="#eef2f6" stroke="%s" stroke-width="2.6"/>'
                % (" ".join(d), INK))

    panels = [
        (160, "Площина", 0, "Σ кутів = 180°", "K = 0", INK),
        (480, "Сфера", 24, "Σ кутів > 180°", "восьмушка сфери: 270°", POS),
        (800, "Сідло", -20, "Σ кутів < 180°", "K < 0", NEG),
    ]
    for cx, title, bulge, l1, l2, col in panels:
        frags.append(text(cx, 52, title, size=17, bold=True))
        frags.append(tri(cx, bulge))
        frags.append(text(cx, 288, l1, size=16, bold=True, color=col))
        frags.append(text(cx, 314, l2, size=13, color=MUTED))

    frags.append(text(W / 2, 366, "Σ кутів − π  =  ∬ K dA", size=19, bold=True))
    frags.append(text(W / 2, 402,
                      "восьмушка сфери:  3·(π/2) − π = π/2  =  (1/R²)·(πR²/2)",
                      size=14, color=MUTED))
    render(os.path.join(IMG, "angle-excess.svg"), W, H, *frags,
           title="Надлишок суми кутів дорівнює сумарній кривині всередині трикутника")


# ───────────────────────────────────────────────────────────────────────────
def geodesic_fan():
    """Геодезичні полярні координати: промені, кола, ширина віяла √G·dθ."""
    W, H = 940, 500
    frags = []
    px, py = 120, 258
    a0, a1, nray = -32.0, 32.0, 9
    radii = [105, 180, 255, 330]
    angs = [a0 + (a1 - a0) * i / (nray - 1) for i in range(nray)]

    frags.append(text(285, 60, "віяло геодезичних, випущених із точки p",
                      size=14, color=MUTED))

    for a in angs:
        frags.append(line(px, py,
                          px + radii[-1] * math.cos(math.radians(a)),
                          py - radii[-1] * math.sin(math.radians(a)),
                          color=MUTED, sw=1.3))

    # смуга між двома сусідніми променями
    for a in (8.0, 16.0):
        frags.append(line(px, py,
                          px + radii[-1] * math.cos(math.radians(a)),
                          py - radii[-1] * math.sin(math.radians(a)),
                          color=FIELD, sw=2.6))

    for R in radii:
        frags.append(polyline(arcpts(px, py, R, a0, a1), color=INK, sw=2.2))
    frags.append(polyline(arcpts(px, py, radii[-1], 8, 16), color=FIELD, sw=5.0))

    # промінь-мірило r
    frags.append(line(px, py, px + radii[-1], py, color=POS, sw=2.6))
    frags.append(text(240, 280, "r", size=16, color=POS, italic=True))
    # прямий кут промінь ⟂ коло
    frags.append(line(px + 180, py - 12, px + 192, py - 12, color=MUTED, sw=1.4))
    frags.append(line(px + 192, py - 12, px + 192, py, color=MUTED, sw=1.4))

    frags.append(dot(px, py, 5.5, INK))
    frags.append(text(101, 264, "p", size=17, bold=True, italic=True))

    frags.append(line(447, 185, 480, 141, color=FIELD, sw=1.4))
    frags.append(text(484, 130, "√G·dθ", size=15, color=FIELD, bold=True, anchor="start"))

    frags.append(text(575, 112, "ds² = dr² + G(r,θ)·dθ²", size=19, bold=True, anchor="start"))
    frags.append(mtext(575, 164, [
        "r — довжина вздовж променя,",
        "тож коефіцієнт при dr² дорівнює 1.",
    ], size=14, anchor="start"))
    frags.append(mtext(575, 232, [
        "Промінь перетинає коло під прямим",
        "кутом (лема Гауса) — мішаного члена",
        "dr·dθ немає, тому F = 0.",
    ], size=14, anchor="start"))
    frags.append(mtext(575, 326, [
        "√G·dθ — ширина віяла на відстані r.",
        "Біля p поверхня майже пласка, тож",
        "√G → 0  і  (√G)′ → 1  при  r → 0.",
    ], size=14, anchor="start"))
    render(os.path.join(IMG, "geodesic-fan.svg"), W, H, *frags,
           title="Геодезичні полярні координати й ширина віяла √G")


# ───────────────────────────────────────────────────────────────────────────
def jacobi_solutions():
    """Три розв'язки рівняння Якобі: sin (K>0), пряма (K=0), sinh (K<0)."""
    W, H = 940, 470
    frags = []
    x0, yb = 110, 380
    sx, sy = 126.0, 108.0
    fmax = 2.62

    frags.append(text(430, 42, "(√G)″ + K·√G = 0", size=21, bold=True))

    frags.append(arrow(x0, yb, x0 + 3.45 * sx, yb, color=MUTED, sw=1.6))
    frags.append(arrow(x0, yb, x0, yb - fmax * sy - 18, color=MUTED, sw=1.6))
    frags.append(text(x0 + 3.45 * sx + 18, yb + 6, "r", size=15, color=MUTED, italic=True))
    frags.append(text(x0 - 4, yb - fmax * sy - 30, "√G", size=15, color=MUTED, italic=True))

    def curve(f, rlim, color):
        n = 120
        pts = [(x0 + sx * rlim * i / n, yb - sy * f(rlim * i / n)) for i in range(n + 1)]
        return polyline(pts, color=color, sw=2.8)

    frags.append(curve(math.sinh, math.asinh(fmax), NEG))
    frags.append(curve(lambda t: t, fmax, INK))
    frags.append(curve(math.sin, math.pi, POS))

    xc = x0 + sx * math.pi
    frags.append(dot(xc, yb, 5.0, POS))
    frags.append(text(xc, 412, "r = πR: промені сходяться знову", size=13, color=POS))

    lx = 626
    for i, (c, s) in enumerate(((POS, "K > 0:   √G = R·sin(r/R)"),
                                (INK, "K = 0:   √G = r"),
                                (NEG, "K < 0:   √G = a·sinh(r/a)"))):
        y = 128 + 42 * i
        frags.append(line(lx, y - 5, lx + 34, y - 5, color=c, sw=3.0))
        frags.append(text(lx + 44, y, s, size=15, color=c, anchor="start"))

    frags.append(mtext(lx, 300, [
        "Усі три виходять із нуля",
        "з нахилом 1 — розбіжність",
        "з'являється аж у члені r³,",
        "і її коефіцієнт є K.",
    ], size=14, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "jacobi-solutions.svg"), W, H, *frags,
           title="Розв'язки рівняння Якобі для сталої кривини трьох знаків")


# ───────────────────────────────────────────────────────────────────────────
def _poly(pts, fill, stroke, sw=1.8, op=1.0):
    s = " ".join("%.1f,%.1f" % q for q in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="%.1f"/>' % (s, fill, op, stroke, sw))


def _circum(a, b, c):
    """Центр описаного кола трикутника (плоскі координати)."""
    d = 2.0 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    sa, sb, sc = a[0] ** 2 + a[1] ** 2, b[0] ** 2 + b[1] ** 2, c[0] ** 2 + c[1] ** 2
    return ((sa * (b[1] - c[1]) + sb * (c[1] - a[1]) + sc * (a[1] - b[1])) / d,
            (sa * (c[0] - b[0]) + sb * (a[0] - c[0]) + sc * (b[0] - a[0])) / d)


def mesh_defect():
    """Кутовий дефект у вершині сітки й дві мірки площі, що йому належить."""
    W, H = 1060, 500
    frags = []
    CY = 210

    # ── 1. Розгорнутий віяр: бракує клина ────────────────────────────────
    cx = 190
    frags.append(text(cx, 66, "Віяр, розкладений на стіл", size=16, bold=True))
    ang = [10, 68, 126, 184, 242, 300]
    rad = [96, 90, 98, 92, 96, 90]
    P = [(cx + r * math.cos(math.radians(t)), CY - r * math.sin(math.radians(t)))
         for t, r in zip(ang, rad)]
    gap = [(cx, CY), P[-1]] + arcpts(cx, CY, 93, 300, 370, 24) + [(cx, CY)]
    frags.append(_poly(gap, POS, "none", 0, 0.13))
    for q in P:
        frags.append(line(cx, CY, q[0], q[1], color=MUTED, sw=1.6))
    for k in range(len(P) - 1):
        frags.append(line(P[k][0], P[k][1], P[k + 1][0], P[k + 1][1], color=INK, sw=2.4))
    frags.append(polyline(arcpts(cx, CY, 30, 10, 68, 24), color=NEG, sw=2.0))
    frags.append(text(cx + 44, CY - 16, "θ", size=15, italic=True, color=NEG))
    frags.append(polyline(arcpts(cx, CY, 52, 300, 370, 24), color=POS, sw=2.6))
    frags.append(dot(cx, CY, 5.0, INK))
    frags.append(text(cx, 356, "Σθ  <  2π", size=17, bold=True))
    frags.append(text(cx, 386, "клин, якого бракує, —", size=13, color=MUTED))
    frags.append(text(cx, 408, "це дефект 2π − Σθ", size=13, color=POS))

    # ── спільний віяр для двох мірок площі ───────────────────────────────
    nang = [18, 82, 140, 196, 258, 318]
    nrad = [92, 84, 96, 88, 82, 94]

    def fan(cx0):
        return [(cx0 + r * math.cos(math.radians(t)), CY - r * math.sin(math.radians(t)))
                for t, r in zip(nang, nrad)]

    def draw_fan(cx0):
        out = []
        Q = fan(cx0)
        for k in range(len(Q)):
            out.append(line(cx0, CY, Q[k][0], Q[k][1], color=MUTED, sw=1.5))
            out.append(line(Q[k][0], Q[k][1], Q[(k + 1) % len(Q)][0], Q[(k + 1) % len(Q)][1],
                            color=INK, sw=2.2))
        return out, Q

    # ── 2. Барицентрична: третина кожного трикутника ─────────────────────
    cx = 610
    frags.append(text(cx, 66, "Барицентрична  A/3", size=16, bold=True))
    f2, Q = draw_fan(cx)
    C0 = (cx, CY)
    cell = []
    for k in range(len(Q)):
        nk = (k + 1) % len(Q)
        cell.append(((C0[0] + Q[k][0]) / 2, (C0[1] + Q[k][1]) / 2))
        cell.append(((C0[0] + Q[k][0] + Q[nk][0]) / 3, (C0[1] + Q[k][1] + Q[nk][1]) / 3))
    frags.append(_poly(cell, FIELD, FIELD, 2.0, 0.20))
    frags.extend(f2)
    frags.append(dot(cx, CY, 5.0, INK))
    frags.append(text(cx, 356, "кути ділять сторони й центри", size=13, color=MUTED))
    frags.append(text(cx, 380, "дешево, але на витягнутих", size=13, color=MUTED))
    frags.append(text(cx, 404, "трикутниках зміщує площу", size=13, color=MUTED))

    # ── 3. Мішана (Вороного) ─────────────────────────────────────────────
    cx = 900
    frags.append(text(cx, 66, "Мішана (Вороного)", size=16, bold=True))
    f3, Q = draw_fan(cx)
    C0 = (cx, CY)
    cell = []
    for k in range(len(Q)):
        nk = (k + 1) % len(Q)
        cell.append(((C0[0] + Q[k][0]) / 2, (C0[1] + Q[k][1]) / 2))
        cell.append(_circum(C0, Q[k], Q[nk]))
    frags.append(_poly(cell, NEG, NEG, 2.0, 0.17))
    frags.extend(f3)
    frags.append(dot(cx, CY, 5.0, INK))
    frags.append(text(cx, 356, "межа йде по серединних", size=13, color=MUTED))
    frags.append(text(cx, 380, "перпендикулярах: точки, ближчі", size=13, color=MUTED))
    frags.append(text(cx, 404, "до цієї вершини, ніж до сусідів", size=13, color=MUTED))

    frags.append(text(W / 2, 458, "K = (2π − Σθ) / A", size=19, bold=True))
    render(os.path.join(IMG, "mesh-defect.svg"), W, H, *frags,
           title="Кутовий дефект у вершині сітки й площа, яку йому приписують")


if __name__ == "__main__":
    principal_sections()
    circle_defect()
    bending_invariance()
    angle_excess()
    geodesic_fan()
    jacobi_solutions()
    mesh_defect()
    print("ok")
