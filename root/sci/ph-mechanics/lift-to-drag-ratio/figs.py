# -*- coding: utf-8 -*-
"""Фігури до теми «Аеродинамічна якість (L/D)».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def polyline(pts, color=INK, sw=2.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


# ── Фігура 1: трикутник планування — L/D = d/h = 1/tan γ ─────────────────────
def fig_glide_ratio():
    W, H = 810, 420
    F = []
    P0 = (165, 100)      # апарат угорі ліворуч
    P1 = (615, 322)      # низ праворуч (кінець планування)
    BL = (165, 322)      # нижній лівий кут трикутника

    # катети (пунктиром) і гіпотенуза-траєкторія (суцільна)
    F.append(line(P0[0], P0[1], BL[0], BL[1], color=MUTED, sw=1.6, dash="5 5"))   # h
    F.append(line(BL[0], BL[1], P1[0], P1[1], color=MUTED, sw=1.6, dash="5 5"))   # d
    F.append(line(P0[0], P0[1], P1[0], P1[1], color=INK, sw=2.6))                 # шлях

    # підписи катетів
    F.append(text(128, 205, "h", size=17, color=INK, anchor="end", bold=True))
    F.append(text(128, 225, "зниження", size=12, color=MUTED, anchor="end"))
    F.append(text((BL[0] + P1[0]) / 2, 352, "d — відстань уперед", size=14, color=INK))

    # напрям шляху (одиничний) і перпендикуляр (угору)
    dx, dy = P1[0] - P0[0], P1[1] - P0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = uy, -ux              # перпендикуляр «угору» від траєкторії

    # апарат на траєкторії
    P = (P0[0] + 0.20 * dx, P0[1] + 0.20 * dy)
    F.append(line(P[0] - 24 * ux, P[1] - 24 * uy, P[0] + 24 * ux, P[1] + 24 * uy,
                  color=INK, sw=5))                        # фюзеляж уздовж шляху
    F.append(line(P[0] - 15 * px, P[1] - 15 * py, P[0] + 15 * px, P[1] + 15 * py,
                  color=INK, sw=8))                        # крило (ребром)

    # три сили з апарата (фізично: L⊥шлях, D назад уздовж шляху, W вниз)
    lenL = 92.0
    lenD = lenL * (0.489)         # D/L = tan γ ≈ h/d
    lenW = lenL / (0.898)         # W = L / cos γ
    F.append(arrow(P[0], P[1], P[0] + lenL * px, P[1] + lenL * py, color=FIELD, sw=3.2))
    F.append(text(P[0] + lenL * px + 8, P[1] + lenL * py - 2, "Підйом L",
                  size=15, color=FIELD, anchor="start", bold=True))
    F.append(arrow(P[0], P[1], P[0] - lenD * ux, P[1] - lenD * uy, color=INK, sw=3.2))
    F.append(text(P[0] - lenD * ux + 30, P[1] - lenD * uy - 12, "Опір D",
                  size=15, color=INK, anchor="middle", bold=True))
    F.append(arrow(P[0], P[1], P[0], P[1] + lenW, color=POS, sw=3.2))
    F.append(text(P[0], P[1] + lenW + 20, "Вага W", size=15, color=POS, bold=True))

    # дуга кута планування γ біля P1
    arc = []
    for k in range(9):
        phi = math.radians(180 + 26.1 * k / 8)
        arc.append((P1[0] + 46 * math.cos(phi), P1[1] + 46 * math.sin(phi)))
    F.append(polyline(arc, color=NEG, sw=2.0))
    F.append(text(P1[0] - 66, P1[1] - 12, "γ", size=17, color=NEG, bold=True, italic=True))
    F.append(text(P1[0] - 74, P1[1] + 8, "кут планування", size=11.5, color=MUTED, anchor="end"))

    # формула у вільному верхньо-правому куті
    F.append(textbox(590, 118, "L/D  =  d / h  =  1 / tan γ", size=16, pad=12,
                     bold=True, fill="#eafaf0", stroke=FIELD)[0])
    F.append(text(590, 156, "стільки метрів уперед", size=13, color=MUTED))
    F.append(text(590, 174, "на кожен метр зниження", size=13, color=MUTED))

    render(os.path.join(IMG, "glide-ratio.svg"), W, H, *F,
           title="Аеродинамічна якість — це кут планування навпаки")


# ── Фігура 2: два опори від швидкості → відро з дном (макс L/D) ───────────────
def fig_drag_bucket():
    W, H = 830, 470
    F = []
    x0, x1 = 115, 720
    yb, yt = 356, 82
    vmin, vmax = 0.45, 2.0
    dmax = 2.1

    def X(v):
        return x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)

    def Y(d):
        return yb - d / dmax * (yb - yt)

    def Di(v):   # індуктивний ∝ 1/v²
        return 0.5 / v ** 2

    def Dp(v):   # паразитний ∝ v²
        return 0.5 * v ** 2

    def Dt(v):
        return Di(v) + Dp(v)

    # осі
    F.append(line(x0, yt - 6, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1 + 6, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 92, "швидкість польоту V  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 14, "опір D  (менше — краще)", size=13,
                  color=MUTED, anchor="start"))

    # криві
    di = [(X(v), Y(Di(v))) for v in frange(0.49, vmax, 90) if Di(v) <= dmax]
    dp = [(X(v), Y(Dp(v))) for v in frange(vmin, vmax, 90) if Dp(v) <= dmax]
    dt = [(X(v), Y(Dt(v))) for v in frange(0.55, 1.95, 90) if Dt(v) <= dmax]
    F.append(polyline(di, color=NEG, sw=2.6))
    F.append(polyline(dp, color=POS, sw=2.6))
    F.append(polyline(dt, color=INK, sw=3.4))

    # підписи кривих із лідерами
    F.append(text(198, 150, "індуктивний опір", size=13.5, color=NEG, anchor="start", bold=True))
    F.append(text(198, 168, "(∝ 1/v²)", size=12.5, color=NEG, anchor="start"))
    F.append(line(196, 158, X(0.70), Y(Di(0.70)), color=NEG, sw=1.1, dash="3 3"))
    F.append(text(602, 168, "паразитний опір", size=13.5, color=POS, anchor="end", bold=True))
    F.append(text(602, 186, "(∝ v²)", size=12.5, color=POS, anchor="end"))
    F.append(line(604, 176, X(1.72), Y(Dp(1.72)), color=POS, sw=1.1, dash="3 3"))
    F.append(text(X(1.55), Y(Dt(1.55)) - 16, "повний опір", size=13.5, color=INK, bold=True))

    # мінімум = макс L/D
    F.append(line(X(1.0), Y(Dt(1.0)), X(1.0), yb, color=INK, sw=1.5, dash="4 4"))
    F.append(circle(X(1.0), Y(Dt(1.0)), 6, fill=INK, stroke=INK))
    F.append(fitbox(X(1.0) - 250, yb + 26, 500, 46,
                    "швидкість найкращого планування:\n"
                    "опір найменший  →  якість L/D найбільша",
                    size=13.5, fill="#eafaf0", stroke=FIELD))
    F.append(line(X(1.0), yb, X(1.0), yb + 26, color=FIELD, sw=1.3, dash="3 3"))

    render(os.path.join(IMG, "drag-bucket.svg"), W, H, *F,
           title="Два опори змагаються — якість найвища на дні «відра»")


# ── Фігура 3: типові значення аеродинамічної якості (стовпчики) ───────────────
def fig_typical_ld():
    W, H = 790, 430
    F = []
    rows = [
        ("Цеглина / парашутист", 1, MUTED),
        ("Легкий літак (Cessna)", 10, NEG),
        ("Пасажирський лайнер", 18, NEG),
        ("Альбатрос", 22, FIELD),
        ("Спортивний планер", 50, FIELD),
        ("Рекордний планер", 70, FIELD),
    ]
    xb0, xbmax = 262, 742
    vmax = 70.0
    scale = (xbmax - xb0) / vmax
    y0, pitch, bh = 76, 54, 32

    # сітка + числа знизу
    ytop, ybot = 66, y0 + len(rows) * pitch - (pitch - bh) + 6
    for g in range(0, 71, 10):
        gx = xb0 + g * scale
        F.append(line(gx, ytop, gx, ybot, color="#e3e7ec", sw=1.2))
        F.append(text(gx, ybot + 20, str(g), size=11.5, color=MUTED))
    F.append(line(xb0, ytop, xb0, ybot, color=INK, sw=1.6))
    F.append(text(xbmax, ybot + 20, "L/D →", size=13, color=INK, anchor="end"))

    for i, (name, val, col) in enumerate(rows):
        yt = y0 + i * pitch
        F.append(text(xb0 - 12, yt + bh / 2 + 5, name, size=14, color=INK, anchor="end"))
        F.append(rect(xb0, yt, val * scale, bh, fill=col, stroke=col, sw=1, rx=4))
        F.append(text(xb0 + val * scale + 10, yt + bh / 2 + 5, "≈ %d" % val,
                      size=14, color=col, anchor="start", bold=True))

    render(os.path.join(IMG, "typical-ld.svg"), W, H, *F,
           title="Аеродинамічна якість: від цеглини до рекордного планера")


def _arc(cx, cy, r, a0, a1, n=10, color=INK, sw=2.0):
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return polyline(pts, color=color, sw=sw)


# ── Вставка math-drag-polar, фіг.1: поляра й дотична з початку координат ──────
def fig_polar_tangent():
    W, H = 860, 470
    F = []
    ox, oy = 120, 372          # піксель точки (CD=0, CL=0)
    xr, yt = 720, 74
    cd_max, cl_max = 0.048, 1.20
    sx = (xr - ox) / cd_max
    sy = (oy - yt) / cl_max

    def X(cd):
        return ox + cd * sx

    def Y(cl):
        return oy - cl * sy

    CD0, k = 0.014, 0.022
    CLs = (CD0 / k) ** 0.5     # оптимальний CL — точка дотику
    CDs = 2 * CD0             # опір у точці дотику

    # осі
    F.append(line(ox, yt - 6, ox, oy, color=INK, sw=1.8))
    F.append(line(ox, oy, xr + 8, oy, color=INK, sw=1.8))
    F.append(text(126, yt - 12, "коефіцієнт підйому  CL ↑", size=13, color=MUTED, anchor="start"))
    F.append(text(xr, oy + 34, "коефіцієнт опору  CD →", size=13.5, color=INK, anchor="end"))

    # парабола CD = CD0 + k·CL²
    pts = []
    for i in range(0, 121):
        cl = cl_max * i / 120.0
        cd = CD0 + k * cl * cl
        if cd <= cd_max:
            pts.append((X(cd), Y(cl)))
    F.append(polyline(pts, color=INK, sw=3.0))
    clab = 1.13
    F.append(text(X(CD0 + k * clab * clab) + 8, Y(clab), "поляра",
                  size=13.5, color=INK, anchor="start", bold=True))
    F.append(text(X(CD0 + k * clab * clab) + 8, Y(clab) + 17,
                  "CD = CD₀ + CL²/(π·e·Λ)", size=12, color=MUTED, anchor="start"))

    # дотична з початку координат
    tx, ty = X(CDs), Y(CLs)
    ex = ox + 1.28 * (tx - ox)
    ey = oy + 1.28 * (ty - oy)
    F.append(line(ox, oy, ex, ey, color=FIELD, sw=2.6))
    F.append(text(175, 358, "нахил прямої = CL/CD = L/D",
                  size=13.5, color=FIELD, anchor="start", bold=True))

    # точка дотику + винесений підпис із лідером
    F.append(circle(tx, ty, 6, fill=FIELD, stroke=FIELD))
    F.append(line(tx, ty, 505, 205, color=MUTED, sw=1.1, dash="3 3"))
    F.append(text(510, 202, "максимум якості:", size=13, color=INK, anchor="start", bold=True))
    F.append(text(510, 220, "CL = CL* = √(CD₀·π·e·Λ)", size=12, color=MUTED, anchor="start"))

    # вертикаль від точки дотику вниз до позначок опору
    ybr = oy + 12
    F.append(line(tx, ty, tx, ybr + 6, color=MUTED, sw=1.2, dash="4 4"))

    # ніс параболи (CL=0 → CD=CD0)
    nx = X(CD0)
    F.append(circle(nx, oy, 4, fill=INK, stroke=INK))

    # дві РІВНІ позначки опору: паразитний [0..CD0] та індуктивний [CD0..2CD0]
    yb2 = ybr + 6
    F.append(line(ox, yb2, nx, yb2, color=NEG, sw=5))
    F.append(line(nx, yb2, tx, yb2, color=POS, sw=5))
    for xx, cc in ((ox, NEG), (nx, INK), (tx, POS)):
        F.append(line(xx, yb2 - 5, xx, yb2 + 5, color=cc, sw=1.6))
    F.append(text((ox + nx) / 2, yb2 + 20, "паразитний CD₀", size=12.5, color=NEG, bold=True))
    F.append(text((nx + tx) / 2, yb2 + 20, "індуктивний CD_i", size=12.5, color=POS, bold=True))
    F.append(text((ox + tx) / 2, yb2 + 40, "у точці максимуму  CD_i = CD₀  (половини рівні)",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "polar-tangent.svg"), W, H, *F,
           title="Максимум якості — дотична до поляри з початку координат")


# ── Вставка math-drag-polar, фіг.2: скіс нахиляє підйом → індуктивний опір ────
def fig_induced_vector():
    W, H = 880, 400
    F = []
    O = (300, 250)
    a = 22.0                   # показовий кут скосу (перебільшений для наочності)
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))

    # профіль крила (ребром) у точці O
    F.append('<ellipse cx="300" cy="250" rx="34" ry="9" '
             'transform="rotate(-8 300 250)" fill="#eef1f4" stroke="%s" stroke-width="1.4"/>' % INK)

    # вільний потік V∞ (горизонталь) і істинна вертикаль (перпендикуляр до V∞)
    F.append(line(O[0], O[1], 300, 84, color=MUTED, sw=1.3, dash="5 4"))
    F.append(arrow(O[0], O[1], 505, O[1], color=MUTED, sw=1.8))
    F.append(text(470, 240, "V∞", size=15, color=MUTED, anchor="start", bold=True, italic=True))
    F.append(text(470, 266, "(вільний потік)", size=11.5, color=MUTED, anchor="start"))

    # місцевий потік Vloc — вниз на α_i
    lx, ly = O[0] + 175 * ca, O[1] + 175 * sa
    F.append(arrow(O[0], O[1], lx, ly, color=INK, sw=2.4))
    F.append(text(lx + 6, ly + 6, "місцевий потік Vloc", size=12.5, color=INK, anchor="start", bold=True))
    F.append(text(lx + 6, ly + 23, "(нахилений скосом на α_i)", size=11.5, color=MUTED, anchor="start"))

    # скіс w — вертикальний доданок місцевого потоку
    F.append(arrow(lx, O[1], lx, ly, color=NEG, sw=2.0))
    F.append(text(lx + 8, (O[1] + ly) / 2 + 4, "скіс w", size=12.5, color=NEG, anchor="start", bold=True))

    # підйом L — перпендикуляр до Vloc, угору-праворуч (нахилений на α_i від вертикалі)
    L = 195
    Lx, Ly = O[0] + L * sa, O[1] - L * ca
    F.append(arrow(O[0], O[1], Lx, Ly, color=FIELD, sw=3.0))
    F.append(text(Lx + 10, Ly - 14, "Підйом L", size=14, color=FIELD, anchor="start", bold=True))

    # розклад L: вертикальний (корисний) і горизонтальний (індуктивний опір)
    F.append(line(O[0], O[1], O[0], Ly, color=FIELD, sw=1.4, dash="4 4"))
    F.append(line(O[0], Ly, Lx, Ly, color=POS, sw=4))
    F.append(text(Lx + 8, Ly + 4, "D_i = L·sin α_i", size=13, color=POS, anchor="start", bold=True))
    F.append(text(O[0] - 10, (O[1] + Ly) / 2, "корисний", size=12, color=FIELD, anchor="end"))
    F.append(text(O[0] - 10, (O[1] + Ly) / 2 + 16, "підйом ≈ L", size=12, color=FIELD, anchor="end"))

    # дуга α_i між вертикаллю (вгору) і підйомом L
    F.append(_arc(O[0], O[1], 72, -90, -90 + a, color=INK, sw=2.0))
    F.append(text(320, 150, "α_i", size=14, color=INK, bold=True, italic=True))

    # ланцюг причин праворуч
    F.append(text(720, 120, "Чому CD_i ∝ CL²", size=14.5, color=INK, bold=True))
    F.append(fitbox(585, 138, 278, 150,
                    "α_i = CL / (π·Λ)\n"
                    "D_i = L·sin α_i ≈ L·α_i\n"
                    "CD_i = CL·α_i = CL² / (π·Λ)\n"
                    "з поправкою e:  CD_i = CL²/(π·e·Λ)",
                    size=13, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "induced-drag-vector.svg"), W, H, *F,
           title="Скіс потоку нахиляє підйом — і народжує індуктивний опір")


# ── Вставка math-drag-polar, фіг.3: (L/D)max від видовження — два важелі ──────
def fig_ld_vs_aspect():
    W, H = 840, 470
    F = []
    x0, x1 = 110, 740
    yb, yt = 392, 72
    amax, vmax = 42.0, 62.0

    def X(aa):
        return x0 + aa / amax * (x1 - x0)

    def Y(v):
        return yb - v / vmax * (yb - yt)

    def LDmax(aa, CD0, e):
        return 0.5 * (math.pi * e * aa / CD0) ** 0.5

    # сітка
    for g in range(0, 43, 10):
        gx = X(g)
        F.append(line(gx, yt, gx, yb, color="#e3e7ec", sw=1.1))
        F.append(text(gx, yb + 20, str(g), size=11.5, color=MUTED))
    for v in range(0, 63, 20):
        gy = Y(v)
        F.append(line(x0, gy, x1, gy, color="#e3e7ec", sw=1.1))
        F.append(text(x0 - 10, gy + 4, str(v), size=11.5, color=MUTED, anchor="end"))
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 44, "видовження  Λ = b²/S  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 14, "(L/D)max ↑", size=13, color=INK, anchor="start"))

    # криві
    A = [(X(aa), Y(LDmax(aa, 0.036, 0.76))) for aa in frange(1, amax, 100)]
    B = [(X(aa), Y(LDmax(aa, 0.010, 0.92))) for aa in frange(1, amax, 100)]
    F.append(polyline(A, color=POS, sw=3.0))
    F.append(polyline(B, color=FIELD, sw=3.0))

    # формула + легенда
    F.append(text(x0 + 8, 104, "(L/D)max = ½·√(π·e·Λ / CD₀)   ∝ √Λ",
                  size=14, color=INK, anchor="start", bold=True))
    F.append(line(x0 + 12, 132, x0 + 42, 132, color=FIELD, sw=3.0))
    F.append(text(x0 + 50, 136, "CD₀ = 0.010 — гладка ламінарна обшивка",
                  size=12.5, color=FIELD, anchor="start"))
    F.append(line(x0 + 12, 154, x0 + 42, 154, color=POS, sw=3.0))
    F.append(text(x0 + 50, 158, "CD₀ = 0.036 — брудна (шасі, стійки, заклепки)",
                  size=12.5, color=POS, anchor="start"))

    # точки
    def dot(aa, CD0, e, col, hollow=False):
        x, y = X(aa), Y(LDmax(aa, CD0, e))
        F.append(circle(x, y, 6, fill=(BG if hollow else col), stroke=col, sw=2))
        return x, y

    px, py = dot(7.4, 0.036, 0.76, POS)
    F.append(line(px, py, px + 18, py + 26, color=MUTED, sw=1.1, dash="3 3"))
    F.append(text(px + 22, py + 30, "легкий літак: Λ≈7, L/D≈11", size=12.5, color=INK, anchor="start"))

    px, py = dot(25, 0.010, 0.92, FIELD)
    F.append(line(px, py, px - 18, py - 22, color=MUTED, sw=1.1, dash="3 3"))
    F.append(text(px - 22, py - 26, "планер: Λ≈25, L/D≈43", size=12.5, color=INK, anchor="end", bold=True))

    px, py = dot(40, 0.010, 0.92, FIELD, hollow=True)
    F.append(line(px, py, px - 14, py + 20, color=MUTED, sw=1.1, dash="3 3"))
    F.append(text(px - 18, py + 24, "рекордний клас: Λ≈40", size=12.5, color=INK, anchor="end"))

    render(os.path.join(IMG, "ld-vs-aspect.svg"), W, H, *F,
           title="Стеля якості росте як √Λ — і окремо від чистоти обшивки")


# ── Вставка proj-speed-to-fly: поляра «зниження–швидкість» і швидкість-щоб-летіти ─
def fig_speed_to_fly():
    W, H = 880, 545
    F = []
    # той самий 18-метровий планер, що у вставці-калькуляторі
    m, S, b, CD0, e, rho, g = 500.0, 11.4, 18.0, 0.0095, 0.90, 1.225, 9.81
    Wt = m * g
    Lam = b * b / S
    k = 1.0 / (math.pi * e * Lam)

    def sink(v):
        CL = 2 * Wt / (rho * v * v * S)
        return v * (CD0 + k * CL * CL) / CL

    CLs = math.sqrt(CD0 / k)
    Vbg = math.sqrt(2 * Wt / (rho * S * CLs))    # найкраще планування
    Vms = Vbg / 3 ** 0.25                         # мінімальне зниження
    Vw = 10.0                                     # зустрічний вітер
    Vstf, best = Vbg, -1.0                         # швидкість-щоб-летіти
    v = 16.0
    while v < 52:
        gr = (v - Vw) / sink(v)
        if gr > best:
            best, Vstf = gr, v
        v += 0.02

    x0, x1 = 105, 800
    yt, yb = 108, 430
    Vmax, smax = 52.0, 1.92
    X = lambda v: x0 + v / Vmax * (x1 - x0)
    Y = lambda s: yt + s / smax * (yb - yt)

    # осі (швидкість згори, зниження вниз — як заведено в полярі планера)
    F.append(line(x0, yt, x1 + 8, yt, color=INK, sw=1.8))
    F.append(line(x0, yt, x0, yb + 8, color=INK, sw=1.8))
    F.append(text(x1 + 4, yt - 34, "швидкість V, м/с  →", size=13.5, color=INK, anchor="end"))
    F.append(text(x0 + 8, yb + 30, "зниження (sink), м/с  ↓", size=13, color=MUTED, anchor="start"))
    for vv in range(0, 51, 10):
        F.append(line(X(vv), yt - 5, X(vv), yt + 5, color=INK, sw=1.3))
        F.append(text(X(vv), yt - 15, str(vv), size=11.5, color=MUTED))
    for ss in (0.5, 1.0, 1.5):
        F.append(line(x0 - 5, Y(ss), x0 + 5, Y(ss), color=INK, sw=1.3))
        F.append(text(x0 - 12, Y(ss) + 4, "%.1f" % ss, size=11.5, color=MUTED, anchor="end"))

    # крива поляри
    pol = [(X(v), Y(sink(v))) for v in frange(19.5, 49.0, 140) if sink(v) <= smax]
    F.append(polyline(pol, color=INK, sw=3.4))
    F.append(text(X(20.3), Y(0.28), "поляра sink(V)", size=12.5, color=INK,
                  anchor="start", bold=True))

    ex = 1.13  # трохи продовжити дотичні за точку дотику

    # дотична з початку координат → найкраще планування (макс. дальність у штиль)
    sbg = sink(Vbg)
    F.append(line(X(0), Y(0), X(0) + (X(Vbg) - X(0)) * ex, Y(0) + (Y(sbg) - Y(0)) * ex,
                  color=NEG, sw=2.2))
    F.append(circle(X(0), Y(0), 4, fill=INK, stroke=INK))
    F.append(circle(X(Vbg), Y(sbg), 6.5, fill=NEG, stroke=NEG))

    # дно поляри → мінімальне зниження (макс. час у повітрі)
    F.append(circle(X(Vms), Y(sink(Vms)), 6.5, fill=FIELD, stroke=FIELD))

    # дотична зі зсувом на вітер → швидкість-щоб-летіти (макс. дальність над землею)
    sstf = sink(Vstf)
    F.append(circle(X(Vw), Y(0), 5, fill=POS, stroke=POS))
    F.append(text(X(Vw) - 10, Y(0) - 9, "вітер w", size=11.5, color=POS, anchor="end"))
    F.append(line(X(Vw), Y(0), X(Vw) + (X(Vstf) - X(Vw)) * ex, Y(0) + (Y(sstf) - Y(0)) * ex,
                  color=POS, sw=2.2))
    F.append(circle(X(Vstf), Y(sstf), 6.5, fill=POS, stroke=POS))

    # легенда: колір точки → зміст (у вільному нижньому лівому куті)
    lx, ly = X(2.5), Y(1.42)
    for i, (col, s) in enumerate([
            (FIELD, "мінімальне зниження V_ms — дно поляри (найдовше в повітрі)"),
            (NEG,   "найкраще планування V_bg — дотична з початку 0 (найдалі у штиль)"),
            (POS,   "швидкість-щоб-летіти V_stf — дотична з точки вітру (найдалі над землею)")]):
        yy = ly + i * 26
        F.append(circle(lx, yy - 4, 6, fill=col, stroke=col))
        F.append(text(lx + 16, yy, s, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "speed-to-fly.svg"), W, H, *F,
           title="Поляра планера: три швидкості з однієї кривої")


if __name__ == "__main__":
    fig_glide_ratio()
    fig_drag_bucket()
    fig_typical_ld()
    fig_polar_tangent()
    fig_induced_vector()
    fig_ld_vs_aspect()
    fig_speed_to_fly()
    print("OK: 7 SVG ->", IMG)
