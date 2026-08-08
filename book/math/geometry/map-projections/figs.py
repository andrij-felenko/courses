# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

R_EARTH = 6371.0


def arcpath(cx, cy, r, a0, a1, color=INK, sw=2.5, dash=None):
    """Дуга кола від кута a0 до a1 (градуси, 0 = вгору, за годинниковою стрілкою)."""
    def pt(a):
        t = math.radians(a)
        return cx + r * math.sin(t), cy - r * math.cos(t)
    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw, d))


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=2.0):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))


def dot(x, y, r=4.5, color=POS):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, color)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ───────────────────────────────────────────────────────────────────────────
def curvature_from_inside():
    """Вимір, який відрізняє кулю від площини, не виходячи з поверхні:
    коло радіусом r має на кулі меншу довжину, ніж 2πr."""
    W, H = 900, 470
    frags = []

    # ── ліва панель: площина ──────────────────────────────────────────
    cx, cy, r = 205, 200, 88
    frags.append(text(cx, 78, "на площині", size=15, bold=True))
    frags.append(circle(cx, cy, r, fill="none", stroke=NEG, sw=2.6))
    frags.append(dot(cx, cy, 4, INK))
    frags.append(line(cx, cy, cx + r, cy, color=MUTED, sw=1.6))
    frags.append(text(cx + r / 2, cy - 12, "r", size=15, bold=True, color=MUTED))
    frags.append(text(cx, cy + r + 34, "довжина = 2π·r", size=15, color=NEG))

    # ── права панель: куля в розрізі ──────────────────────────────────
    ox, oy, RR = 645, 258, 118
    th = 62.0                      # центральний кут r/R у градусах
    px = ox + RR * math.sin(math.radians(th))
    py = oy - RR * math.cos(math.radians(th))
    frags.append(text(ox, 78, "на кулі радіуса R", size=15, bold=True))
    frags.append(circle(ox, oy, RR, fill="none", stroke=MUTED, sw=1.6))
    frags.append(line(ox, oy, ox, oy - RR, color=MUTED, sw=1.3))
    frags.append(line(ox, oy, px, py, color=MUTED, sw=1.3))
    frags.append(arcpath(ox, oy, RR, 0, th, color=POS, sw=4.0))
    frags.append(dot(ox, oy - RR, 4.5, POS))
    frags.append(dot(px, py, 4.5, POS))
    frags.append(line(ox, py, px, py, color=NEG, sw=2.2, dash="6 4"))
    frags.append(text(ox + 55, py - 12, "R·sin(r/R)", size=14, bold=True, color=NEG))
    frags.append(text(px + 52, py + 26, "r — по поверхні", size=14, color=POS))
    frags.append(text(ox - 14, oy + 6, "O", size=14, color=MUTED))
    frags.append(text(ox + 26, oy - 34, "r/R", size=13, color=MUTED))
    frags.append(text(ox, oy + RR + 34, "довжина = 2π·R·sin(r/R)", size=15, color=NEG))

    # ── нижня смуга з числами ─────────────────────────────────────────
    rows = []
    for rr in (1000.0, 5000.0):
        x = rr / R_EARTH
        cp = 2 * math.pi * rr
        cs = 2 * math.pi * R_EARTH * math.sin(x)
        rows.append("r = %d км:  2π·r = %.1f км,  на кулі %.1f км\n"
                    "коло коротше на %.1f км (%.2f %%)"
                    % (rr, cp, cs, cp - cs, 100 * (cp - cs) / cp))
    b1, w1, h1 = textbox(240, 418, rows[0], size=13, fill="#eef3ff", stroke=NEG)
    b2, w2, h2 = textbox(660, 418, rows[1], size=13, fill="#eef3ff", stroke=NEG)
    frags += [b1, b2]

    render(os.path.join(IMG, "curvature-from-inside.svg"), W, H, *frags,
           title="Куля відрізняється від площини вимірами, зробленими всередині поверхні")


# ───────────────────────────────────────────────────────────────────────────
def tissot_two_numbers():
    """Мале коло на місцевості після проєкції: коло → еліпс із півосями a і b."""
    W, H = 930, 420
    frags = []

    PW, TOP, PH = 268, 78, 232
    XS = (24, 331, 638)
    U = 30.0                       # одиниця масштабу в пікселях

    def panel(i, head):
        x = XS[i]
        out = [rect(x, TOP, PW, PH, fill="#fbfcfd", stroke=MUTED, sw=1.4),
               text(x + PW / 2, TOP - 14, head, size=14, bold=True)]
        return out, x + PW / 2, TOP + PH / 2 + 6

    def rays(cx, cy, sx, sy, color):
        dx, dy = U * math.cos(math.radians(45)), U * math.sin(math.radians(45))
        return [line(cx, cy, cx + dx * sx, cy - dy * sy, color=color, sw=2.0),
                line(cx, cy, cx + dx * sx, cy + dy * sy, color=color, sw=2.0)]

    # A — на місцевості
    out, cx, cy = panel(0, "мала ділянка на місцевості")
    out.append(circle(cx, cy, U, fill="#eef7ef", stroke=FIELD, sw=2.4))
    out += rays(cx, cy, 1, 1, FIELD)
    out.append(text(cx - 52, cy + 4, "90°", size=14, bold=True, color=FIELD))
    out.append(text(cx, TOP + PH - 16, "коло радіусом 1", size=14))
    frags += out

    # B — конформна: a = b = 2
    out, cx, cy = panel(1, "конформна: a = b = 2")
    out.append(circle(cx, cy, 2 * U, fill="#fdecea", stroke=POS, sw=2.4))
    out += rays(cx, cy, 2, 2, POS)
    out.append(text(cx - 84, cy + 4, "90°", size=14, bold=True, color=POS))
    out.append(text(cx, TOP + PH - 16, "кут цілий, площа ×4", size=14, color=POS))
    frags += out

    # C — рівновелика: a = 2, b = 0.5
    out, cx, cy = panel(2, "рівновелика: a = 2, b = 0.5")
    out.append(ellipse(cx, cy, 2 * U, 0.5 * U, fill="#eef3ff", stroke=NEG, sw=2.4))
    out += rays(cx, cy, 2, 0.5, NEG)
    out.append(text(cx - 84, cy + 4, "28°", size=14, bold=True, color=NEG))
    out.append(text(cx, TOP + PH - 16, "площа ціла, прямий кут зім'ято", size=13, color=NEG))
    frags += out

    frags.append(text(W / 2, H - 26,
                      "a·b — у скільки разів роздуто площу;  a = b — кути цілі;  "
                      "a = b = 1 водночас — неможливо",
                      size=14, color=MUTED))

    render(os.path.join(IMG, "tissot-two-numbers.svg"), W, H, *frags,
           title="Проєкція перетворює мале коло на еліпс — і всі властивості карти "
                 "стають умовами на його півосі")


# ───────────────────────────────────────────────────────────────────────────
def tangent_secant():
    """Дотик проти січення: чому UTM бере k₀ = 0.9996, а не 1."""
    W, H = 940, 500
    frags = []

    # ── ліворуч: два розрізи ──────────────────────────────────────────
    def globe(cy, d, head, note):
        cxg, rg = 158, 62
        out = [text(cxg, cy - rg - 26, head, size=14, bold=True),
               circle(cxg, cy, rg, fill="#fbfcfd", stroke=MUTED, sw=1.8)]
        xl = cxg + d
        out.append(line(xl, cy - rg - 16, xl, cy + rg + 16, color=POS, sw=2.6))
        if d >= rg:
            out.append(dot(cxg + rg, cy))
        else:
            hh = math.sqrt(rg * rg - d * d)
            out.append(dot(xl, cy - hh))
            out.append(dot(xl, cy + hh))
        out.append(text(cxg, cy + rg + 44, note, size=13, color=MUTED))
        return out

    frags += globe(150, 62, "дотична поверхня", "одна лінія істинного масштабу")
    frags += globe(350, 40, "січна поверхня", "дві лінії істинного масштабу")

    # ── праворуч: графік масштабного коефіцієнта ──────────────────────
    GX0, GX1 = 500, 900
    GY0, GY1 = 110, 392                 # верх / низ поля графіка
    KLO, KHI = 0.99930, 1.00160
    XC = (GX0 + GX1) / 2
    SPAN = 334.0                        # півширина зони на екваторі, км

    def gx(km):
        return XC + km / SPAN * (GX1 - GX0) / 2

    def gy(k):
        return GY1 - (k - KLO) / (KHI - KLO) * (GY1 - GY0)

    frags.append(rect(GX0 - 16, GY0 - 22, (GX1 - GX0) + 32, (GY1 - GY0) + 66,
                      fill="#fbfcfd", stroke=MUTED, sw=1.3))
    frags.append(line(GX0, gy(1.0), GX1, gy(1.0), color=MUTED, sw=1.4, dash="5 4"))
    frags.append(text(GX0 - 4, gy(1.0) - 8, "k = 1", size=13, color=MUTED, anchor="start"))

    def curve(k0, color, dash=None):
        pts = []
        km = -SPAN
        while km <= SPAN + 0.1:
            pts.append((gx(km), gy(k0 * math.cosh(km / R_EARTH))))
            km += 8
        return polyline(pts, color=color, sw=2.8, dash=dash)

    frags.append(curve(1.0, POS, dash="7 5"))
    frags.append(curve(0.9996, NEG))

    frags.append(text(XC, GY0 + 26, "дотична (k₀ = 1):  від 0 до +1374 ppm",
                      size=13, bold=True, color=POS))
    frags.append(text(XC, GY0 + 52, "січна (k₀ = 0.9996):  від −400 до +974 ppm",
                      size=13, bold=True, color=NEG))

    for km in (-180.0, 180.0):
        frags.append(dot(gx(km), gy(0.9996 * math.cosh(km / R_EARTH)), 4.5, NEG))
    frags.append(text(gx(-180), gy(1.0) - 46, "істинний масштаб на ±180 км",
                      size=13, color=NEG))

    frags.append(text(gx(0), GY1 + 26, "центр зони", size=13, color=MUTED))
    frags.append(text(gx(SPAN), GY1 + 26, "край зони 6°", size=13, color=MUTED, anchor="end"))
    frags.append(text(gx(-SPAN), GY1 + 26, "край зони 6°", size=13, color=MUTED, anchor="start"))

    frags.append(text(W / 2 + 60, H - 22,
                      "Січна поверхня втискає карту всередині смуги, щоб на краю вона "
                      "розтягла менше.", size=14, color=MUTED))

    render(os.path.join(IMG, "tangent-secant.svg"), W, H, *frags,
           title="Спотворення не зникає — його переставляють: дотик проти січення")


# ───────────────────────────────────────────────────────────────────────────
def step_size_valley():
    """Вибір кроку центральної різниці: усічення проти втрати значущих цифр."""
    W, H = 940, 520
    frags = []

    # виміряно: Меркатор ∂y/∂φ при φ = 60°, порівняно з точним R·sec φ
    MEAS = [(-1, -1.924), (-2, -3.932), (-3, -5.932), (-4, -7.933),
            (-5, -9.896), (-6, -10.034), (-7, -9.105), (-8, -8.851),
            (-9, -7.243), (-10, -6.693), (-11, -5.338), (-12, -4.577),
            (-13, -3.070), (-14, -2.224), (-15, -0.771), (-16, 0.0)]

    GX0, GX1 = 132, 880
    GY0, GY1 = 96, 404
    XLO, XHI = -16.6, 0.4
    YLO, YHI = -11.0, 1.0

    def gx(v):
        return GX0 + (v - XLO) / (XHI - XLO) * (GX1 - GX0)

    def gy(v):
        return GY1 - (v - YLO) / (YHI - YLO) * (GY1 - GY0)

    SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
           "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}

    def pow10(v):
        return "1" if v == 0 else "10" + "".join(SUP[c] for c in str(v))

    # осі
    frags.append(line(GX0, GY0 - 8, GX0, GY1, color=MUTED, sw=1.4))
    frags.append(line(GX0, GY1, GX1 + 8, GY1, color=MUTED, sw=1.4))
    for v in range(-16, 1, 2):
        frags.append(line(gx(v), GY1, gx(v), GY1 + 6, color=MUTED, sw=1.2))
        frags.append(text(gx(v), GY1 + 26, pow10(v), size=12, color=MUTED))
    for v in range(-10, 1, 2):
        frags.append(line(GX0 - 6, gy(v), GX0, gy(v), color=MUTED, sw=1.2))
        frags.append(text(GX0 - 12, gy(v) + 4, pow10(v), size=12, color=MUTED, anchor="end"))
    frags.append(text((GX0 + GX1) / 2, GY1 + 56, "крок h, радіан", size=14, color=INK))
    frags.append(text(GX0 - 56, GY0 - 30, "відносна похибка", size=13, color=INK, anchor="start"))

    # асимптоти: усічення 2·lg h + 0.07, шум −16.4 − lg h; обрізано по нижній межі поля
    frags.append(polyline([(gx(-5.535), gy(-11.0)), (gx(-0.4), gy(-0.73))],
                          color=POS, sw=2.0, dash="8 6"))
    frags.append(polyline([(gx(-16.4), gy(0.0)), (gx(-5.4), gy(-11.0))],
                          color=NEG, sw=2.0, dash="8 6"))

    frags.append(polyline([(gx(x), gy(y)) for x, y in sorted(MEAS)], color=INK, sw=3.0))
    for x, y in MEAS:
        frags.append(dot(gx(x), gy(y), 3.4, INK))

    # западина
    frags.append(line(gx(-6), gy(-10.6), gx(-6), gy(0.6), color=FIELD, sw=1.8, dash="5 5"))
    frags.append(line(GX0 + 4, gy(-10.034), gx(-6.4), gy(-10.034), color=FIELD, sw=1.6, dash="5 5"))
    frags.append(dot(gx(-6), gy(-10.034), 6.0, FIELD))

    frags.append(text(gx(-3.6), gy(-2.4), "усічення ∝ h²", size=14, bold=True, color=POS))
    frags.append(text(gx(-13.2), gy(-1.2), "втрата значущих цифр ∝ 1/h",
                      size=14, bold=True, color=NEG))
    frags.append(text(gx(-6), gy(0.9) - 4, "h ≈ ε ^ (1/3) ≈ 6·10⁻⁶", size=13, bold=True, color=FIELD))
    frags.append(text(gx(-11.4), gy(-10.034) - 14, "дно западини ≈ ε ^ (2/3) ≈ 4·10⁻¹¹",
                      size=13, color=FIELD))

    frags.append(text(W / 2, H - 34,
                      "Виміряно на Меркаторі: похідна y по широті при φ = 60°, "
                      "проти точного R·sec φ.", size=14, color=MUTED))
    frags.append(text(W / 2, H - 14,
                      "Скільки крок не зменшуй, третину значущих цифр числова похідна "
                      "забирає назавжди.", size=14, color=MUTED))

    render(os.path.join(IMG, "step-size-valley.svg"), W, H, *frags,
           title="Крок різниці: два джерела похибки тягнуть у різні боки")


# ───────────────────────────────────────────────────────────────────────────
def candidates_compared():
    """Чотири кандидати над Україною, зміряні тією самою сіткою."""
    W, H = 960, 400
    frags = []

    ROWS = [("Меркатора",             39.6,  0.00),
            ("рівновелика Ламберта",   0.0, 10.26),
            ("конічна конформна",      0.6,  0.00),
            ("азимутальна рівнопроміжна", 0.3, 0.17)]

    LX = 254                      # права межа стовпця підписів
    P1, P2 = 288, 664             # початок першої / другої панелі
    BW = 258                      # довжина панелі
    A_MAX, W_MAX = 40.0, 10.5

    frags.append(text(P1, 84, "розкид площі по району, %", size=14, bold=True, color=POS,
                      anchor="start"))
    frags.append(text(P2, 84, "найгірший кут ω, градусів", size=14, bold=True, color=NEG,
                      anchor="start"))

    y = 128
    for name, area, om in ROWS:
        frags.append(text(LX, y + 18, name, size=14, color=INK, anchor="end"))
        for x0, val, vmax, col, fmt in ((P1, area, A_MAX, POS, "%.1f"),
                                        (P2, om, W_MAX, NEG, "%.2f")):
            frags.append(line(x0, y - 4, x0, y + 32, color=MUTED, sw=1.2))
            w = val / vmax * BW
            if w > 1.5:
                frags.append(rect(x0, y, w, 28, fill=col, stroke=col, sw=1.0, rx=3))
            frags.append(text(x0 + max(w, 2) + 9, y + 19, fmt % val, size=13,
                              color=col, bold=True, anchor="start"))
        y += 62

    frags.append(text(W / 2, H - 34,
                      "Сітка 61×61 над прямокутником φ 44.0…52.5°, λ 22.0…40.5°; "
                      "площу взято після калібрування.", size=14, color=MUTED))
    frags.append(text(W / 2, H - 14,
                      "Дві глобальні проєкції валять по одному числу кожна, дві "
                      "місцеві не валять жодного.", size=14, color=MUTED))

    render(os.path.join(IMG, "candidates-compared.svg"), W, H, *frags,
           title="Вибір проєкції під район, зроблений числами")


# ───────────────────────────────────────────────────────────────────────────
def _major_dir(a11, a12, a21, a22, steps=3600):
    """Напрям НА КАРТІ, у якому розтяг найбільший (велика піввісь еліпса Тіссо)."""
    best_t, best_len = 0.0, -1.0
    for i in range(steps):
        t = math.pi * i / steps
        vx = a11 * math.cos(t) + a12 * math.sin(t)
        vy = a21 * math.cos(t) + a22 * math.sin(t)
        L = math.hypot(vx, vy)
        if L > best_len:
            best_len, best_t = L, t
    vx = a11 * math.cos(best_t) + a12 * math.sin(best_t)
    vy = a21 * math.cos(best_t) + a22 * math.sin(best_t)
    return vx / best_len, vy / best_len


def tissot_from_jacobian():
    """Одиничне коло на місцевості → еліпс на карті: h, k, θ′ і головні масштаби a, b.
    Числа справжні: синусоїдальна проєкція на φ = 45°, за 90° довготи від осьового меридіана."""
    W, H = 920, 480
    U = 78.0
    frags = []

    t_shear = (math.pi / 2) * math.sin(math.radians(45.0))    # λ·sin φ
    a11, a12 = 1.0, t_shear          # стовпець «схід», стовпець «північ»
    a21, a22 = 0.0, 1.0

    k = math.hypot(a11, a21)
    h = math.hypot(a12, a22)
    det = abs(a11 * a22 - a12 * a21)
    th = math.atan2(a22, a12)                       # кут між образами схід/північ
    A = (math.sqrt(h*h + k*k + 2*det) + math.sqrt(h*h + k*k - 2*det)) / 2
    B = (math.sqrt(h*h + k*k + 2*det) - math.sqrt(h*h + k*k - 2*det)) / 2
    mx, my = _major_dir(a11, a12, a21, a22)

    def P(cx, cy, ux, uy):
        return (cx + U * ux, cy - U * uy)

    # ── ліва панель: місцевість ───────────────────────────────────────
    LX, LY = 195.0, 235.0
    frags.append(text(LX, 80, "на місцевості", size=15, bold=True))
    ref = [(LX + U*math.cos(2*math.pi*i/144), LY - U*math.sin(2*math.pi*i/144))
           for i in range(145)]
    frags.append(polyline(ref, color=MUTED, sw=2.2))
    frags.append(arrow(LX, LY, LX + U, LY, color=POS, sw=2.6))
    frags.append(arrow(LX, LY, LX, LY - U, color=NEG, sw=2.6))
    frags.append(dot(LX, LY, 4.0, INK))
    frags.append(text(LX + U/2, LY + 26, "1 м на схід", size=13, bold=True, color=POS))
    frags.append(text(LX - 14, LY - U/2, "1 м на північ", size=13, bold=True,
                      color=NEG, anchor="end"))
    frags.append(text(LX, LY + U + 46, "коло радіусом 1 м", size=13, color=MUTED))

    # ── права панель: карта ───────────────────────────────────────────
    RX, RY = 620.0, 235.0
    frags.append(text(RX, 80, "на карті", size=15, bold=True))

    pg = [P(RX, RY, 0, 0), P(RX, RY, a11, a21),
          P(RX, RY, a11 + a12, a21 + a22), P(RX, RY, a12, a22)]
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.13" stroke="none"/>'
                 % (" ".join("%.1f,%.1f" % q for q in pg), FIELD))

    ell = []
    for i in range(145):
        t = 2 * math.pi * i / 144
        c, s = math.cos(t), math.sin(t)
        ell.append(P(RX, RY, a11*c + a12*s, a21*c + a22*s))
    frags.append(polyline(ell, color=INK, sw=2.8))

    ex, ey = P(RX, RY, a11, a21)
    nx, ny = P(RX, RY, a12, a22)
    frags.append(arrow(RX, RY, ex, ey, color=POS, sw=2.6))
    frags.append(arrow(RX, RY, nx, ny, color=NEG, sw=2.6))
    frags.append(text(738, 241, "k = %.3f" % k, size=13, bold=True, color=POS))
    frags.append(text(744, 132, "h = %.3f" % h, size=13, bold=True, color=NEG))

    arc = [(RX + 44*math.cos(th*j/40), RY - 44*math.sin(th*j/40)) for j in range(41)]
    frags.append(polyline(arc, color=MUTED, sw=1.8))
    frags.append(text(674, 218, "θ′ = %.0f°" % math.degrees(th), size=13, color=MUTED))

    frags.append(line(RX, RY, *P(RX, RY, -A*mx, -A*my), color=FIELD, sw=2.6, dash="8 5"))
    frags.append(line(RX, RY, *P(RX, RY, B*my, -B*mx), color=FIELD, sw=2.6, dash="8 5"))
    frags.append(text(469, 324, "a = %.3f" % A, size=13, bold=True, color=FIELD))
    frags.append(text(660, 302, "b = %.3f" % B, size=13, bold=True, color=FIELD))

    frags.append(text(W/2, 396,
                      "a² + b² = h² + k²   —   сума квадратів чотирьох чисел матриці",
                      size=15, bold=True))
    frags.append(text(W/2, 424,
                      "a · b = h · k · sin θ′ = |det|   —   площа зафарбованого паралелограма",
                      size=15, bold=True))
    frags.append(text(W/2, 452,
                      "тут  h = %.3f,  k = %.3f,  θ′ = %.1f°   →   a = %.3f,  b = %.3f,  a·b = %.3f"
                      % (h, k, math.degrees(th), A, B, A*B), size=14, color=MUTED))

    render(os.path.join(IMG, "tissot-from-jacobian.svg"), W, H, *frags,
           title="Від якобіана до еліпса: одиничне коло стає еліпсом із півосями a і b")


def tissot_at_60():
    """Три проєкції в одному місці (60° пн. ш.): еліпси Тіссо в спільному масштабі."""
    W, H = 900, 445
    U = 42.0
    CY = 218.0
    frags = []

    panels = [
        (158.0, "Меркатора", "конформна", 2.0, 2.0, POS,
         ["a = b = 2.000", "площа a·b = 4.000", "ω = 0°"]),
        (450.0, "Ламберта", "циліндрична рівновелика", 2.0, 0.5, NEG,
         ["a = 2.000,  b = 0.500", "площа a·b = 1.000", "ω = 73.74°"]),
        (742.0, "рівнопроміжна від полюса", "азимутальна", 1.047198, 1.0, FIELD,
         ["a = 1.047,  b = 1.000", "площа a·b = 1.047", "ω = 2.64°"]),
    ]

    for cx, name, sub, ra, rb, col, lines in panels:
        frags.append(text(cx, 86, name, size=15, bold=True))
        frags.append(text(cx, 108, sub, size=13, color=MUTED))
        ref = [(cx + U*math.cos(2*math.pi*i/120), CY - U*math.sin(2*math.pi*i/120))
               for i in range(121)]
        frags.append(polyline(ref, color=MUTED, sw=1.5, dash="5 6"))
        frags.append(ellipse(cx, CY, U*ra, U*rb, stroke=col, sw=3.0))
        frags.append(dot(cx, CY, 3.5, INK))
        for j, s in enumerate(lines):
            frags.append(text(cx, 334 + 24*j, s, size=13,
                              color=col if j == 0 else INK, bold=(j == 0)))

    frags.append(text(W/2, 414,
                      "горизонталь — уздовж паралелі, вертикаль — уздовж меридіана; "
                      "сірий пунктир — коло без спотворення", size=13, color=MUTED))

    render(os.path.join(IMG, "tissot-at-60.svg"), W, H, *frags,
           title="Одна широта, три проєкції: 60° пн. ш. у спільному масштабі")


if __name__ == "__main__":
    curvature_from_inside()
    tissot_two_numbers()
    tangent_secant()
    step_size_valley()
    candidates_compared()
    tissot_from_jacobian()
    tissot_at_60()
    print("ok")
