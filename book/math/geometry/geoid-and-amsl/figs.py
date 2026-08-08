# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def _poly(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def _bar(x, y_top, y_bot, color, cap=7, sw=2.0):
    """Вертикальна мірка з поперечками на кінцях."""
    out = line(x, y_top, x, y_bot, color=color, sw=sw)
    out += line(x - cap, y_top, x + cap, y_top, color=color, sw=sw)
    out += line(x - cap, y_bot, x + cap, y_bot, color=color, sw=sw)
    return out


# ────────────────────────────────────────────────────────────────────────────
def three_surfaces():
    """Розріз: еліпсоїд, геоїд, рельєф і три висоти однієї точки."""
    W, H = 900, 520
    X0, X1 = 55, 560
    XP = 430.0
    frags = []

    def y_ell(x):
        return 400.0 + 0.0004 * (x - 300.0) ** 2

    def undul(x):
        return 25.0 + 32.0 * math.cos(2 * math.pi * (x - XP) / 320.0)

    def y_geo(x):
        return y_ell(x) - undul(x)

    xs = [X0 + i * (X1 - X0) / 120.0 for i in range(121)]
    frags.append(_poly([(x, y_ell(x)) for x in xs], NEG, sw=2.6))
    frags.append(_poly([(x, y_geo(x)) for x in xs], FIELD, sw=2.8))

    terr = [(55, 300), (110, 285), (160, 312), (215, 296), (270, 266),
            (320, 290), (375, 262), (430, 250), (485, 276), (540, 302), (560, 308)]
    frags.append(_poly(terr, INK, sw=2.2))

    yT, yG, yE = 250.0, y_geo(XP), y_ell(XP)

    # стовпчик вимірювання й винесення рівнів у чисте поле праворуч
    frags.append(line(XP, yT, XP, yE, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(circle(XP, yT, 4.5, fill=INK, stroke=INK))
    for yy in (yT, yG, yE):
        frags.append(line(XP, yy, 885, yy, color=MUTED, sw=1.0, dash="3,5"))

    frags.append(_bar(650, yT, yE, NEG))
    frags.append(_bar(730, yT, yG, INK))
    frags.append(_bar(810, yG, yE, FIELD))
    frags.append(text(634, 326, "h", size=15, bold=True, color=NEG, anchor="end"))
    frags.append(text(714, 304, "H", size=15, bold=True, color=INK, anchor="end"))
    frags.append(text(794, 382, "N", size=15, bold=True, color=FIELD, anchor="end"))

    frags.append(text(430, 215, "точка на земній поверхні", size=13, color=INK))
    frags.append(line(430, 224, 430, 242, color=MUTED, sw=1.0, dash="3,3"))

    box, _, _ = textbox(740, 120,
                        ["h — над еліпсоїдом (дає GNSS)",
                         "H — над геоїдом (це і є AMSL)",
                         "N — ундуляція геоїда",
                         "h = H + N"],
                        size=13)
    frags.append(box)

    # нижня легенда поверхонь
    for x0, color, name in ((70, NEG, "еліпсоїд"), (250, FIELD, "геоїд"), (420, INK, "рельєф")):
        frags.append(line(x0, 465, x0 + 35, 465, color=color, sw=2.8))
        frags.append(text(x0 + 42, 470, name, size=13, anchor="start"))

    render(os.path.join(IMG, "three-surfaces.svg"), W, H, *frags,
           title="Три поверхні відліку в розрізі")


# ────────────────────────────────────────────────────────────────────────────
def mass_and_geoid():
    """Чому рівнева поверхня горбата: надлишок і нестача мас."""
    W, H = 900, 500
    X0, X1 = 60, 820
    frags = []

    def y_geo(x):
        return (270.0
                - 34.0 * math.exp(-((x - 280.0) / 95.0) ** 2)
                + 28.0 * math.exp(-((x - 600.0) / 95.0) ** 2))

    frags.append(rect(60, 276, 760, 154, fill="#eef1f4", stroke=MUTED, sw=1.0, rx=4))
    frags.append(line(X0, 270, X1, 270, color=NEG, sw=2.4))
    xs = [X0 + i * (X1 - X0) / 160.0 for i in range(161)]
    frags.append(_poly([(x, y_geo(x)) for x in xs], FIELD, sw=2.8))

    frags.append(circle(280, 352, 34, fill="#f6dcd8", stroke=POS, sw=2.0))
    frags.append(text(280, 358, "+Δm", size=15, bold=True, color=POS))
    frags.append(circle(600, 352, 34, fill="#e2eaf9", stroke=NEG, sw=2.0))
    frags.append(text(600, 358, "−Δm", size=15, bold=True, color=NEG))
    frags.append(text(280, 412, "надлишок мас", size=12, color=POS))
    frags.append(text(600, 412, "нестача мас", size=12, color=NEG))

    # місцева вертикаль — нормаль до рівневої поверхні
    for x in (180, 240, 300, 360):
        yy = y_geo(x)
        d = (y_geo(x + 0.5) - y_geo(x - 0.5))
        s = math.hypot(d, 1.0)
        frags.append(line(x, yy, x + 28.0 * d / s, yy - 28.0 / s, color=POS, sw=2.0))

    frags.append(text(200, 150, "місцева вертикаль ⟂ рівневої поверхні", size=12, color=POS))
    frags.append(line(255, 159, 292, 206, color=MUTED, sw=1.0, dash="3,3"))

    frags.append(text(470, 178, "геоїд здувається вгору", size=12, color=FIELD))
    frags.append(line(430, 186, 322, 226, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(700, 212, "геоїд провисає", size=12, color=FIELD))
    frags.append(line(662, 220, 617, 288, color=MUTED, sw=1.0, dash="3,3"))

    for x0, color, name in ((70, NEG, "еліпсоїд — гладка математична форма"),
                            (420, FIELD, "геоїд — поверхня рівного потенціалу")):
        frags.append(line(x0, 457, x0 + 35, 457, color=color, sw=2.8))
        frags.append(text(x0 + 42, 462, name, size=12, anchor="start"))

    render(os.path.join(IMG, "mass-and-geoid.svg"), W, H, *frags,
           title="Чому рівнева поверхня горбата")


# ────────────────────────────────────────────────────────────────────────────
def four_altitudes():
    """Один апарат, чотири поверхні відліку — чотири різні числа висоти."""
    W, H = 940, 490
    X0, X1 = 60, 470
    frags = []

    xs = [X0 + i * (X1 - X0) / 90.0 for i in range(91)]
    frags.append(_poly([(x, 190 + 6 * math.sin((x - X0) / 62.0)) for x in xs],
                       MUTED, sw=2.2, dash="7,5"))

    terr = [(60, 300), (150, 300), (230, 300), (270, 278), (310, 300),
            (350, 262), (395, 292), (435, 274), (470, 300)]
    frags.append(_poly(terr, INK, sw=2.2))
    frags.append(_poly([(x, 385 + 4 * math.sin((x - X0) / 90.0)) for x in xs], FIELD, sw=2.6))
    frags.append(line(X0, 440, X1, 440, color=NEG, sw=2.4))

    frags.append(text(70, 168, "поверхня 1013.25 гПа", size=12, color=MUTED, anchor="start"))
    frags.append(text(70, 282, "рельєф", size=12, color=INK, anchor="start"))
    frags.append(text(70, 367, "геоїд", size=12, color=FIELD, anchor="start"))
    frags.append(text(70, 422, "еліпсоїд", size=12, color=NEG, anchor="start"))

    box, _, bh = textbox(250, 120, "апарат", size=13, fill="#eef1f4")
    frags.append(box)
    frags.append(line(250, 120 + bh / 2, 250, 440, color=MUTED, sw=1.4, dash="4,4"))
    for yy in (190, 300, 385, 440):
        frags.append(circle(250, yy, 4.0, fill=INK, stroke=INK))

    frags.append(text(390, 148, "пливе з погодою", size=11, color=MUTED))
    frags.append(arrow(390, 190, 390, 163, color=MUTED, sw=1.6))
    frags.append(arrow(390, 190, 390, 219, color=MUTED, sw=1.6))

    for yy in (120, 190, 300, 385, 440):
        frags.append(line(475, yy, 895, yy, color=MUTED, sw=1.0, dash="3,5"))

    for x, ybot, color, name in ((560, 190, MUTED, "баро"),
                                 (650, 300, INK, "AGL"),
                                 (740, 385, FIELD, "AMSL"),
                                 (830, 440, NEG, "h")):
        frags.append(_bar(x, 120, ybot, color))
        frags.append(text(x, 104, name, size=13, bold=True, color=color))

    render(os.path.join(IMG, "four-altitudes.svg"), W, H, *frags,
           title="Чотири висоти одного апарата")


# ────────────────────────────────────────────────────────────────────────────
def degree_length():
    """Чому довжина градуса широти міряє сплюснення (спір Ньютона й Кассіні)."""
    import math as m
    W, H = 900, 540
    frags = []

    def arc(cx, cy, R, t0, t1, step=1.0):
        pts = []
        t = t0
        while t <= t1 + 1e-9:
            a = m.radians(t)
            pts.append((cx + R * m.sin(a), cy - R * m.cos(a)))
            t += step
        return pts

    def group(cx, cy, R, title, sub, note_color):
        out = []
        out.append(text(cx, 62, title, size=16, bold=True, color=INK))
        out.append(text(cx, 84, sub, size=13, color=MUTED))
        out.append(_poly(arc(cx, cy, R, -15, 15), INK, sw=3.0))
        feet = []
        for t in (-8.0, 8.0):
            a = m.radians(t)
            fx, fy = cx + R * m.sin(a), cy - R * m.cos(a)
            tx, ty = fx + 118 * m.sin(a), fy - 118 * m.cos(a)
            out.append(line(fx, fy, tx, ty, color=note_color, sw=2.2))
            feet.append((fx, fy, tx, ty))
        (x1, y1, tx1, ty1), (x2, y2, tx2, ty2) = feet
        out.append(line(tx1, ty1 - 10, tx2, ty2 - 10, color=MUTED, sw=1.0, dash="4,5"))
        out.append(text(cx, ty1 - 20, "той самий поворот виска", size=12, color=MUTED))
        yb = max(y1, y2) + 52
        out.append(line(x1, y1, x1, yb + 8, color=MUTED, sw=1.0, dash="3,5"))
        out.append(line(x2, y2, x2, yb + 8, color=MUTED, sw=1.0, dash="3,5"))
        out.append(arrow(x1, yb, x2, yb, color=note_color, sw=2.0))
        out.append(arrow(x2, yb, x1, yb, color=note_color, sw=2.0))
        return out

    frags += group(215, 660, 400, "Біля полюса", "поверхня плоскіша", NEG)
    frags += group(660, 470, 195, "Біля екватора", "поверхня крутіша", POS)
    frags.append(text(215, 392, "довший відрізок меридіана", size=13, bold=True, color=NEG))
    frags.append(text(660, 392, "коротший", size=13, bold=True, color=POS))

    frags.append(textbox(450, 448,
                         "Широту дає напрям виска, а не відстань: 1° широти — це поворот виска на 1°",
                         size=14)[0])
    frags.append(text(450, 502,
                      "Лапландія 1737: 1° ≈ 57 422 туази   ·   Перу: 1° ≈ 56 734 туази",
                      size=14, bold=True, color=FIELD))

    render(os.path.join(IMG, "degree-length.svg"), W, H, *frags,
           title="Довжина градуса широти й сплюснення")


# ────────────────────────────────────────────────────────────────────────────
def grid_row_seam():
    """Чому сусід зі сходу на межі ±180° — не наступна комірка в пам'яті."""
    W, H = 1000, 450
    CW, CH, CY = 62, 46, 176
    R39 = "#eaf0fd"
    R40 = "#fdecea"
    frags = []

    def cellrow(xs, labels, fillc):
        out = []
        for x, lab in zip(xs, labels):
            out.append(rect(x, CY, CW, CH, fill=fillc, stroke=LINE, sw=1.4, rx=3))
            out.append(text(x + CW / 2.0, CY + 30, lab, size=13, bold=True))
        return out

    frags += cellrow([100, 162, 224], ["c0", "c1", "c2"], R39)
    frags.append(text(317, CY + 30, "…", size=17, color=MUTED))
    frags += cellrow([348, 410, 472], ["c357", "c358", "c359"], R39)
    frags += cellrow([534, 596, 658], ["c0", "c1", "c2"], R40)
    frags.append(text(751, CY + 30, "…", size=17, color=MUTED))

    # правильний сусід: замикання на початок ТОГО САМОГО рядка
    frags.append(line(503, CY, 503, 134, color=FIELD, sw=2.2))
    frags.append(line(503, 134, 131, 134, color=FIELD, sw=2.2))
    frags.append(arrow(131, 134, 131, CY - 6, color=FIELD, sw=2.2))
    frags.append(text(317, 120, "(col + 1) % nlon = 0 — сусід зі сходу лежить на початку ТОГО САМОГО рядка",
                      size=13, color=FIELD, bold=True))

    # хибний сусід: індекс 360 переповзає в наступний рядок
    frags.append(arrow(650, 316, 572, 232, color=POS, sw=2.2))
    box, _, _ = textbox(790, 348,
                        ["col + 1 = 360 без замикання",
                          "читає перший вузол НАСТУПНОГО рядка:",
                          "той самий файл, широта на крок південніше"],
                        size=12, color=POS, fill="#fdecea", stroke=POS)
    frags.append(box)

    for x0, fillc, name in ((100, R39, "рядок 39 — широта 50°"),
                            (470, R40, "рядок 40 — широта 49°")):
        frags.append(rect(x0, 406, 26, 18, fill=fillc, stroke=LINE, sw=1.2, rx=3))
        frags.append(text(x0 + 34, 420, name, size=12, anchor="start"))

    render(os.path.join(IMG, "grid-row-seam.svg"), W, H, *frags,
           title="Рядок сітки в пам'яті: де ховається межа ±180°")


# ────────────────────────────────────────────────────────────────────────────
def grid_cell_q8():
    """Білінійна інтерполяція комірки в арифметиці Q8 — з числами контрольної точки."""
    W, H = 1000, 560
    X0, X1, Y0, Y1 = 180.0, 540.0, 130.0, 370.0
    PX, PY = X0 + 0.75 * (X1 - X0), Y0 + 0.75 * (Y1 - Y0)   # 450, 310
    frags = []

    frags.append(rect(X0, Y0, X1 - X0, Y1 - Y0, fill="#f7f9fb", stroke=LINE, sw=1.8, rx=0))
    frags.append(line(PX, Y0, PX, Y1, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(X0, PY, X1, PY, color=MUTED, sw=1.2, dash="4,4"))

    for cx, cy in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):
        frags.append(circle(cx, cy, 5.0, fill=INK, stroke=INK))
    frags.append(text(X0 - 12, 120, "n₀₀ = 2693", size=13, bold=True, anchor="end"))
    frags.append(text(X1 + 12, 120, "n₀₁ = 2695", size=13, bold=True, anchor="start"))
    frags.append(text(X0 - 12, 390, "n₁₀ = 2770", size=13, bold=True, anchor="end"))
    frags.append(text(X1 + 12, 390, "n₁₁ = 2772", size=13, bold=True, anchor="start"))

    frags.append(circle(PX, Y0, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(text(PX, 118, "top = 2694.50 см", size=12, color=FIELD))
    frags.append(circle(PX, Y1, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(text(PX, 392, "bot = 2771.50 см", size=12, color=FIELD))

    frags.append(text(305, 180, "fx = 192  (0.750 комірки на схід)", size=12, color=NEG))
    frags.append(text(305, 206, "fy = 192  (0.750 комірки на південь)", size=12, color=NEG))

    frags.append(circle(PX, PY, 6.0, fill=POS, stroke=POS))
    frags.append(line(PX + 10, PY, 590, 300, color=MUTED, sw=1.2, dash="4,4"))
    box, _, _ = textbox(720, 300, "N = 2752.25 см → 2752", size=13,
                        bold=True, color=POS, fill="#fdecea", stroke=POS)
    frags.append(box)

    box, _, _ = textbox(500, 476,
                        ["top = 2693·(256−fx) + 2695·fx = 689 792 — це Q8, тобто см·256",
                         "bot = 2770·(256−fx) + 2772·fx = 709 504 — теж Q8",
                         "val = top·(256−fy) + bot·fy = 180 371 456 — уже Q16, тобто см·65536",
                         "N = (val + 32768) >> 16 = 2752 см = 27.52 м"],
                        size=12)
    frags.append(box)

    render(os.path.join(IMG, "grid-cell-q8.svg"), W, H, *frags,
           title="Комірка сітки й дві дії білінійної інтерполяції")


# ────────────────────────────────────────────────────────────────────────────
def bruns_geometry():
    """Геометрія формули Брунса: розклад нормального потенціалу вздовж нормалі."""
    W, H = 980, 580
    X0, X1 = 60, 500
    XP = 280.0
    frags = []

    def y_ell(x):
        return 452.0 + 0.00016 * (x - 280.0) ** 2

    def undul(x):
        return 104.0 - 0.00028 * (x - 280.0) ** 2

    def y_geo(x):
        return y_ell(x) - undul(x)

    xs = [X0 + i * (X1 - X0) / 120.0 for i in range(121)]
    frags.append(_poly([(x, y_ell(x)) for x in xs], NEG, sw=2.6))
    frags.append(_poly([(x, y_geo(x)) for x in xs], FIELD, sw=2.8))

    frags.append(arrow(XP, y_ell(XP), XP, 292, color=INK, sw=1.8))
    frags.append(circle(XP, y_ell(XP), 4.5, fill=NEG, stroke=NEG))
    frags.append(circle(XP, y_geo(XP), 4.5, fill=FIELD, stroke=FIELD))
    frags.append(_bar(322, y_geo(XP), y_ell(XP), POS))
    frags.append(text(342, 404, "N", size=16, bold=True, color=POS, anchor="start"))

    frags.append(text(256, 344, "P₀", size=14, bold=True, anchor="end"))
    frags.append(text(256, 462, "Q₀", size=14, bold=True, anchor="end"))
    frags.append(text(300, 304, "h", size=14, bold=True, anchor="start"))

    frags.append(text(170, 300, "нормаль до еліпсоїда", size=12, color=MUTED))
    frags.append(line(254, 308, 274, 324, color=MUTED, sw=1.0, dash="3,3"))

    frags.append(text(500, 320, "геоїд:  W = W₀", size=13, color=FIELD, anchor="end"))
    frags.append(text(500, 502, "еліпсоїд:  U = U₀", size=13, color=NEG, anchor="end"))

    box, _, _ = textbox(252, 172,
                        ["W = V + Φ — справжній потенціал",
                         "U — потенціал рівневого еліпсоїда",
                         "T = W − U — збурювальний потенціал",
                         "∇²T = 0 поза масами"],
                        size=13)
    frags.append(box)

    # ── врізка: U(h) уздовж нормалі ────────────────────────────────────────
    GX0, GX1, GY0, GY1 = 588, 792, 122, 300
    frags.append(line(GX0, GY0, GX0, GY1, color=MUTED, sw=1.4))
    frags.append(line(GX0, GY1, GX1 + 16, GY1, color=MUTED, sw=1.4))
    frags.append(line(GX0, 142, GX1, 288, color=NEG, sw=2.4))
    frags.append(text(GX0 - 8, 147, "U₀", size=13, color=MUTED, anchor="end"))
    frags.append(text(GX0, 108, "U", size=13, color=MUTED))
    frags.append(text(GX1 + 26, GY1 + 6, "h", size=13, color=MUTED, anchor="start"))

    XN = 722.0
    YN = 142.0 + (XN - GX0) / float(GX1 - GX0) * 146.0
    frags.append(line(XN, GY1, XN, YN, color=POS, sw=1.2, dash="4,4"))
    frags.append(line(GX0, YN, XN, YN, color=POS, sw=1.2, dash="4,4"))
    frags.append(circle(XN, YN, 4.5, fill=POS, stroke=POS))
    frags.append(text(XN, GY1 + 20, "h = N", size=12, color=POS))
    frags.append(text(GX0 - 8, YN + 5, "U₀ − γN", size=12, color=POS, anchor="end"))
    frags.append(text(806, 186, "нахил = −γ", size=12, color=NEG, anchor="start"))
    frags.append(line(802, 190, 762, 262, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(716, 348, "уздовж нормалі U спадає майже лінійно", size=12, color=MUTED))

    box, _, _ = textbox(748, 428,
                        ["U(P₀) = U₀ − γ·N − ½·(∂γ/∂h)·N²",
                         "T(P₀) = W₀ − U(P₀) = γ·N + ½·(∂γ/∂h)·N²",
                         "N = T / γ",
                         "відкинутий член < 2 мм на всій планеті"],
                        size=13)
    frags.append(box)

    box, _, _ = textbox(748, 520, "T менший за W приблизно в 60 000 разів",
                        size=12, color=MUTED)
    frags.append(box)

    render(os.path.join(IMG, "bruns-geometry.svg"), W, H, *frags,
           title="Формула Брунса як перший член розкладу")


# ────────────────────────────────────────────────────────────────────────────
def harmonic_attenuation():
    """Множник (a/r)ⁿ: чому супутник не бачить високих степенів."""
    W, H = 940, 540
    PX0, PX1, PY0, PY1 = 130, 745, 70, 430
    A_KM = 6378.137
    frags = []

    def px(h_km):
        return PX0 + h_km / 500.0 * (PX1 - PX0)

    def py(v):
        lg = math.log10(v)
        return PY0 + (-lg) / 12.0 * (PY1 - PY0)

    frags.append(line(PX0, PY0, PX0, PY1, color=MUTED, sw=1.4))
    frags.append(line(PX0, PY1, PX1 + 10, PY1, color=MUTED, sw=1.4))

    for lg, lab in ((0, "1"), (-3, "10⁻³"), (-6, "10⁻⁶"), (-9, "10⁻⁹"), (-12, "10⁻¹²")):
        yy = PY0 + (-lg) / 12.0 * (PY1 - PY0)
        frags.append(line(PX0 - 5, yy, PX0, yy, color=MUTED, sw=1.2))
        frags.append(text(PX0 - 12, yy + 5, lab, size=12, color=MUTED, anchor="end"))
    for hk in (0, 100, 200, 300, 400, 500):
        xx = px(hk)
        frags.append(line(xx, PY1, xx, PY1 + 5, color=MUTED, sw=1.2))
        frags.append(text(xx, PY1 + 24, str(hk), size=12, color=MUTED))

    frags.append(text(437, PY1 + 52, "висота над еліпсоїдом, км", size=13, color=MUTED))
    frags.append(text(196, PY0 - 40, "множник (a/r)ⁿ", size=13, color=MUTED))

    xm = px(250)
    frags.append(line(xm, PY0, xm, PY1, color=MUTED, sw=1.0, dash="5,5"))
    frags.append(text(xm, PY0 - 16, "низька навколоземна орбіта ≈ 250 км", size=12, color=MUTED))

    series = ((2, MUTED), (36, NEG), (180, FIELD), (360, INK), (2190, POS))
    for n, col in series:
        pts = []
        for i in range(0, 251):
            hk = i * 2.0
            v = (A_KM / (A_KM + hk)) ** n
            if v < 1e-12:
                break
            pts.append((px(hk), py(v)))
        frags.append(_poly(pts, col, sw=2.4))
        lx, ly = pts[-1]
        if lx > PX1 - 12:
            frags.append(text(PX1 + 16, ly + 5, "n = %d" % n, size=13,
                              bold=True, color=col, anchor="start"))
        else:
            frags.append(text(lx + 14, ly - 6, "n = %d" % n, size=13,
                              bold=True, color=col, anchor="start"))

    box, _, _ = textbox(360, 152,
                        ["(a/r)ⁿ = (1 + h/a)⁻ⁿ ≈ exp(−n·h/a)",
                         "спад у e разів — на висоті a/n"],
                        size=13)
    frags.append(box)

    render(os.path.join(IMG, "harmonic-attenuation.svg"), W, H, *frags,
           title="Спадання гармонік з висотою")


# ────────────────────────────────────────────────────────────────────────────
def geoid_spectrum():
    """Скільки метрів дає кожен степінь і скільки лишається за обривом."""
    W, H = 940, 560
    PX0, PX1, PY0, PY1 = 130, 745, 70, 430
    LG0, LG1 = math.log10(2.0), math.log10(3000.0)
    frags = []

    def px(n):
        return PX0 + (math.log10(n) - LG0) / (LG1 - LG0) * (PX1 - PX0)

    def py(v):
        return PY0 + (2.0 - math.log10(v)) / 6.0 * (PY1 - PY0)

    def rms_deg(n):
        return 63.9 * math.sqrt(2.0 * n + 1.0) / (n * n)

    def rms_tail(n):
        return 63.9 / n

    frags.append(line(PX0, PY0, PX0, PY1, color=MUTED, sw=1.4))
    frags.append(line(PX0, PY1, PX1 + 10, PY1, color=MUTED, sw=1.4))

    for lg, lab in ((2, "100 м"), (1, "10 м"), (0, "1 м"), (-1, "10 см"),
                    (-2, "1 см"), (-3, "1 мм"), (-4, "0.1 мм")):
        yy = PY0 + (2.0 - lg) / 6.0 * (PY1 - PY0)
        frags.append(line(PX0 - 5, yy, PX0, yy, color=MUTED, sw=1.2))
        frags.append(text(PX0 - 12, yy + 5, lab, size=12, color=MUTED, anchor="end"))
    for n in (2, 10, 100, 1000):
        xx = px(n)
        frags.append(line(xx, PY1, xx, PY1 + 5, color=MUTED, sw=1.2))
        frags.append(text(xx, PY1 + 24, str(n), size=12, color=MUTED))
    frags.append(text(437, PY1 + 92, "степінь n", size=13, color=MUTED))
    frags.append(text(206, PY0 - 40, "середньоквадратичний внесок у N", size=13, color=MUTED))

    for n, lab, col in ((360, "360 — EGM96", NEG), (2190, "2190 — EGM2008", POS)):
        xx = px(n)
        frags.append(line(xx, PY0, xx, PY1, color=col, sw=1.0, dash="5,5"))
        frags.append(text(xx, PY1 + 52, lab, size=12, color=col))

    ns = [2.0 * (3000.0 / 2.0) ** (i / 240.0) for i in range(241)]
    frags.append(_poly([(px(n), py(rms_deg(n))) for n in ns], INK, sw=2.6))
    frags.append(_poly([(px(n), py(rms_tail(n))) for n in ns], FIELD, sw=2.6, dash="7,5"))

    frags.append(text(430, 408, "внесок одного степеня n", size=13, bold=True, color=INK))
    frags.append(line(500, 398, 596, 328, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(652, 128, "усе, що лишилось вище n", size=13, bold=True,
                      color=FIELD, anchor="middle"))
    frags.append(line(636, 140, 568, 230, color=MUTED, sw=1.0, dash="3,3"))

    box, _, _ = textbox(252, 344,
                        ["обрив на 360  →  хвіст ≈ 18 см",
                         "обрив на 2190 →  хвіст ≈ 3 см"],
                        size=13)
    frags.append(box)

    render(os.path.join(IMG, "geoid-spectrum.svg"), W, H, *frags,
           title="Спектр геоїда й похибка обриву")


if __name__ == "__main__":
    three_surfaces()
    mass_and_geoid()
    four_altitudes()
    degree_length()
    grid_row_seam()
    grid_cell_q8()
    bruns_geometry()
    harmonic_attenuation()
    geoid_spectrum()
    print("ok")
