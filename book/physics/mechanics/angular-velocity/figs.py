# -*- coding: utf-8 -*-
"""Фігури до теми «Кутова швидкість і прискорення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def vec(x1, y1, x2, y2, color=INK, sw=2.6, head=12):
    """Кольорова стрілка-вектор із власним наконечником у кольорі лінії."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x2 - ux * head, y2 - uy * head
    nx, ny = -uy, ux
    hw = head * 0.5
    ln = line(x1, y1, bx, by, color=color, sw=sw)
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x2, y2, bx + nx * hw, by + ny * hw, bx - nx * hw, by - ny * hw, color))
    return ln + h


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=FIELD, sw=2.6, head=10):
    """Дуга-стрілка на колі від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    Lh = math.hypot(tx, ty); tx, ty = tx / Lh, ty / Lh
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    back = 2.0
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.6):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))


def ellipse_arc_arrow(cx, cy, rx, ry, f0_deg, f1_deg, color=FIELD, sw=3.0, head=12, n=40):
    """Дуга-стрілка по еліпсу від параметра f0 до f1 (градуси; x=cx+rx·cosφ, y=cy+ry·sinφ)."""
    pts = []
    for i in range(n + 1):
        f = math.radians(f0_deg + (f1_deg - f0_deg) * i / n)
        pts.append((cx + rx * math.cos(f), cy + ry * math.sin(f)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    path = '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)
    (x2, y2) = pts[-1]; (xp, yp) = pts[-2]
    dx, dy = x2 - xp, y2 - yp
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x2 - ux * head, y2 - uy * head
    nx, ny = -uy, ux
    hw = head * 0.5
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x2, y2, bx + nx * hw, by + ny * hw, bx - nx * hw, by - ny * hw, color))
    return path + h


# ── Фігура 1: карусель — спільна ω, різні v ─────────────────────────────────
def fig_carousel():
    W, H = 820, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Та сама кутова швидкість — різні лінійні швидкості",
                  size=17, bold=True))

    cx, cy = 280, 245
    r_car = 150
    a = math.radians(42)
    r1, r2 = 62, 140

    # диск каруселі
    f.append(circle(cx, cy, r_car, fill="#fbfcfe", stroke=MUTED, sw=1.8))
    f.append(circle(cx, cy, 9, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 26, "вісь", size=12, color=MUTED))

    # радіус до краю
    xe, ye = cx + r_car * math.cos(a), cy - r_car * math.sin(a)
    f.append(line(cx, cy, xe, ye, color="#cbd2dc", sw=1.6, dash="5,5"))

    # два «пасажири»
    P1 = (cx + r1 * math.cos(a), cy - r1 * math.sin(a))
    P2 = (cx + r2 * math.cos(a), cy - r2 * math.sin(a))
    f.append(circle(P1[0], P1[1], 8, fill=NEG, stroke=INK, sw=1.4))
    f.append(circle(P2[0], P2[1], 8, fill=POS, stroke=INK, sw=1.4))
    f.append(text(P1[0] + 14, P1[1] + 16, "ближня", size=11, color=NEG, anchor="start"))
    f.append(text(P2[0] + 14, P2[1] + 4, "крайня", size=11, color=POS, anchor="start"))

    # дотичний напрям (CCW)
    tx, ty = -math.sin(a), -math.cos(a)
    # вектори швидкості: довжина ∝ r
    v1 = 44; v2 = 96
    f.append(vec(P1[0], P1[1], P1[0] + tx * v1, P1[1] + ty * v1, color=NEG, sw=2.8, head=12))
    f.append(vec(P2[0], P2[1], P2[0] + tx * v2, P2[1] + ty * v2, color=POS, sw=3.0, head=13))
    f.append(text(P1[0] + tx * v1 - 6, P1[1] + ty * v1 - 8, "v₁ = ω·r₁",
                  size=12, bold=True, color=NEG, anchor="end"))
    f.append(text(P2[0] + tx * v2 + 4, P2[1] + ty * v2 - 8, "v₂ = ω·r₂",
                  size=12, bold=True, color=POS, anchor="middle"))

    # ω — спільна (дуга біля осі)
    f.append(arc_arrow(cx, cy, 38, 205, 320, color=FIELD, sw=3.0, head=11))
    f.append(text(cx - 54, cy + 4, "ω", size=20, bold=True, color=FIELD, anchor="end"))

    # пояснювальна рамка праворуч
    b, w, h = textbox(650, 230,
                      "ω — спільна\nна все тіло\n\nv = ω · r\nдалі від осі —\nтим швидше",
                      size=13, pad=12, fill="#f0f6f1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "carousel-two-riders.svg"), W, H, *f)


# ── Фігура 2: дві складові прискорення точки на ободі ────────────────────────
def fig_accel():
    W, H = 700, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дві складові прискорення точки, що обертається",
                  size=17, bold=True))

    cx, cy = 300, 260
    R = 150
    f.append(circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.8))
    f.append(circle(cx, cy, 8, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 24, "вісь", size=12, color=MUTED))

    # напрям обертання
    f.append(arc_arrow(cx, cy, R, 120, 60, color=FIELD, sw=2.6, head=10))
    f.append(text(cx - R - 6, cy - 8, "ω", size=18, bold=True, color=FIELD, anchor="end"))

    # точка P на ободі
    a = math.radians(58)
    P = (cx + R * math.cos(a), cy - R * math.sin(a))
    f.append(circle(P[0], P[1], 8, fill=INK, stroke=INK, sw=1))
    f.append(text(P[0] + 12, P[1] - 10, "точка на ободі", size=11, color=INK, anchor="start"))

    # доосьове (центрострімке): до центра
    ux, uy = (cx - P[0]), (cy - P[1])
    Lc = math.hypot(ux, uy); ux, uy = ux / Lc, uy / Lc
    ac = 96
    f.append(vec(P[0], P[1], P[0] + ux * ac, P[1] + uy * ac, color=NEG, sw=3.0, head=13))
    mc = (P[0] + ux * ac * 0.55, P[1] + uy * ac * 0.55)
    f.append(text(mc[0] + 12, mc[1] + 4, "a_ц = ω²r", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(mc[0] + 12, mc[1] + 22, "(до осі, завжди)", size=11, color=NEG, anchor="start"))

    # дотичне (тангенційне): уздовж руху (CCW)
    tx, ty = -math.sin(a), -math.cos(a)
    at = 92
    f.append(vec(P[0], P[1], P[0] + tx * at, P[1] + ty * at, color=POS, sw=3.0, head=13))
    mt = (P[0] + tx * at, P[1] + ty * at)
    f.append(text(mt[0] - 8, mt[1] - 10, "a_t = αr", size=13, bold=True, color=POS, anchor="middle"))
    f.append(text(mt[0] - 8, mt[1] - 28, "(лише коли міняються оберти)", size=11, color=POS, anchor="middle"))

    # підсумкова рамка знизу
    b, w, h = textbox(cx, H - 26,
                      "a_ц міняє напрям швидкості  ·  a_t міняє її величину",
                      size=13, pad=9, fill="#f6f8fc", stroke=MUTED, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "tangential-centripetal.svg"), W, H, *f)


# ── Фігура 3: вектор кутової швидкості вздовж осі (правило правої руки) ───────
def fig_axis():
    W, H = 700, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Кутова швидкість — вектор уздовж осі обертання",
                  size=17, bold=True))

    cx, cy = 300, 290
    rx, ry = 150, 50

    # вісь (нижня частина — вал)
    f.append(line(cx, cy, cx, cy + 66, color=MUTED, sw=3))
    # диск у перспективі
    f.append(ellipse(cx, cy, rx, ry, fill="#eef3fb", stroke=NEG, sw=2.0))
    f.append(circle(cx, cy, 7, fill=INK, stroke=INK, sw=1))

    # спін по передньому ободу (зелений), рух праворуч→ліворуч по фронту
    f.append(ellipse_arc_arrow(cx, cy, rx, ry, -25, 205, color=FIELD, sw=3.2, head=13, n=48))

    # точка P на ободі (фронт-право) + r та v
    fP = math.radians(20)
    P = (cx + rx * math.cos(fP), cy + ry * math.sin(fP))
    f.append(vec(cx, cy, P[0], P[1], color=MUTED, sw=2.2, head=10))
    f.append(text((cx + P[0]) / 2 + 4, (cy + P[1]) / 2 + 16, "r", size=14, bold=True,
                  italic=True, color=MUTED))
    f.append(circle(P[0], P[1], 6, fill=INK, stroke=INK, sw=1))
    # v — дотична до еліпса в P (у бік зростання φ)
    tvx, tvy = -rx * math.sin(fP), ry * math.cos(fP)
    Lv = math.hypot(tvx, tvy); tvx, tvy = tvx / Lv, tvy / Lv
    f.append(vec(P[0], P[1], P[0] + tvx * 74, P[1] + tvy * 74, color=INK, sw=2.8, head=12))
    f.append(text(P[0] + tvx * 74 - 6, P[1] + tvy * 74 + 18, "v = ω × r", size=13, bold=True,
                  color=INK, anchor="middle"))

    # вектор ω угору по осі
    f.append(vec(cx, cy, cx, cy - 175, color=FIELD, sw=3.4, head=15))
    f.append(text(cx + 14, cy - 168, "ω", size=22, bold=True, color=FIELD, anchor="start"))

    # рамка з правилом правої руки
    b, w, h = textbox(cx, H - 24,
                      "пальці правої руки — за обертанням, великий палець — куди дивиться ω",
                      size=12, pad=9, fill="#f0f6f1", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "omega-axis-vector.svg"), W, H, *f)


# ── Фігура 4: чому 360 — число, що ділиться націло ───────────────────────────
def fig_why360():
    W, H = 780, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому 360, а не 100: число, яке ділиться націло", size=17, bold=True))
    f.append(text(W / 2, 52, "поділ кола на рівні частини — скільки в кожній", size=12.5, color=MUTED))

    x_d, x_360, x_100 = 180, 410, 610
    y_head = 96
    y_first = 130
    step = 34
    n = 9
    # фонові смуги колонок
    f.append(rect(x_360 - 90, y_head - 24, 180, step * n + 34, fill="#eef7f0", stroke="none", sw=0, rx=8))
    f.append(rect(x_100 - 80, y_head - 24, 160, step * n + 34, fill="#f5f7fb", stroke="none", sw=0, rx=8))
    # заголовки колонок
    f.append(text(x_d, y_head, "поділити на", size=13.5, bold=True, color=INK))
    f.append(text(x_360, y_head, "360°", size=16, bold=True, color=FIELD))
    f.append(text(x_100, y_head, "100 частин", size=15, bold=True, color=MUTED))

    rows = [
        (2, "180", True, "50", True),
        (3, "120", True, "33.3…", False),
        (4, "90", True, "25", True),
        (5, "72", True, "20", True),
        (6, "60", True, "16.7…", False),
        (8, "45", True, "12.5", False),
        (9, "40", True, "11.1…", False),
        (10, "36", True, "10", True),
        (12, "30", True, "8.3…", False),
    ]
    yy = y_first
    for (d, a, aw, b, bw) in rows:
        f.append(text(x_d, yy, "÷ %d" % d, size=13.5, color=INK))
        f.append(text(x_360, yy, a + "°", size=14, bold=True, color=FIELD))
        f.append(text(x_100, yy, b, size=14, bold=(not bw), color=(MUTED if bw else POS)))
        yy += step

    b, w, h = textbox(W / 2, H - 42,
                      "360 = 2·2·2·3·3·5  →  24 дільники: 2, 3, 4, 5, 6, 8, 9, 10, 12 …\n"
                      "100 = 2·2·5·5  →  лише 9 дільників",
                      size=12.5, pad=11, fill="#fbfcfe", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "degrees-divisibility.svg"), W, H, *f)


# ── Фігура 5: поняття 1714 → назва 1873 (часова лінія) ───────────────────────
def fig_timeline():
    W, H = 1060, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Поняття народилося 1714-го, назву дістало 1873-го", size=17, bold=True))

    axis_y = 300
    f.append(line(70, axis_y, W - 40, axis_y, color=MUTED, sw=2))

    cw = 146
    ms = [
        (112, "1714", "Котс: природна\nміра кута", NEG),
        (268, "1722", "Сміт друкує\n57.2957…°", NEG),
        (424, "1765", "Ойлер: радіанна\nугода у формулах", NEG),
        (636, "1869", "Мюр вагається\nміж rad і radian", FIELD),
        (792, "1873", "Томсон друкує\n«radian», Белфаст", FIELD),
        (948, "1874", "Мюр усталює\n«radian»", FIELD),
    ]
    for (cx, yr, cap, col) in ms:
        f.append(line(cx, 250, cx, axis_y - 6, color="#cbd2dc", sw=1.4))
        f.append(circle(cx, axis_y, 6, fill=col, stroke=col, sw=1))
        f.append(text(cx, 150, yr, size=16, bold=True, color=col))
        f.append(fitbox(cx - cw / 2, 160, cw, 84, cap, size=12.5, pad=8,
                        fill=("#fbfcfe" if col == NEG else "#f2fbf5"),
                        stroke=col, sw=1.4, color=INK))

    # проміжок мовчання між 1765 і 1869
    gx0, gx1 = 424 + cw / 2, 636 - cw / 2
    gmid = (gx0 + gx1) / 2
    f.append(line(gx0, axis_y, gx1, axis_y, color=POS, sw=2.6, dash="2,7"))
    b, w, h = textbox(gmid, axis_y + 36, "104 роки:\nпоняття є, назви — нема",
                      size=11.5, pad=8, fill="#fdf0ee", stroke=POS, sw=1.3, bold=True, color=POS)
    f.append(b)

    # верхня дужка 1714 → 1873
    bx0, bx1, by = 112, 792, 92
    f.append(line(bx0, by, bx1, by, color=MUTED, sw=1.6))
    f.append(line(bx0, by, bx0, by + 10, color=MUTED, sw=1.6))
    f.append(line(bx1, by, bx1, by + 10, color=MUTED, sw=1.6))
    f.append(text((bx0 + bx1) / 2, by - 8,
                  "від відкриття міри (1714) до надрукованої назви (1873) — 159 років",
                  size=13, bold=True, color=INK))

    # легенда
    f.append(circle(310, H - 22, 6, fill=NEG, stroke=NEG, sw=1))
    f.append(text(324, H - 18, "поняття (ще без назви)", size=12, color=NEG, anchor="start"))
    f.append(circle(600, H - 22, 6, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(614, H - 18, "поява й усталення слова «radian»", size=12, color=FIELD, anchor="start"))
    return render(os.path.join(IMG, "radian-name-timeline.svg"), W, H, *f)


# ── Фігура: некомутативність скінченних поворотів (кубик) ────────────────────
def fig_noncommute():
    W, H = 880, 585
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ті самі два повороти в різному порядку — різна орієнтація",
                  size=17, bold=True))

    # кольори шести граней (колір «їде» з гранню)
    COL = {'+z': "#e0685c", '-z': "#f0b45a", '+x': "#5b90d6",
           '-x': "#b07ad0", '+y': "#5cb87c", '-y': "#4bc0cc"}
    faces = [
        ('+x', [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)]),
        ('-x', [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]),
        ('+y', [(-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)]),
        ('-y', [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)]),
        ('+z', [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]),
        ('-z', [(-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)]),
    ]
    NRM = {'+x': (1, 0, 0), '-x': (-1, 0, 0), '+y': (0, 1, 0),
           '-y': (0, -1, 0), '+z': (0, 0, 1), '-z': (0, 0, -1)}

    def iso(p, cx, cy, s):
        x, y, z = p
        return (cx + (x - y) * s * 0.866, cy + (x + y) * s * 0.5 - z * s)

    def Rx(p): x, y, z = p; return (x, -z, y)
    def Rz(p): x, y, z = p; return (-y, x, z)

    def app(seq, p):
        for R in seq:
            p = R(p)
        return p

    def cube(cx, cy, s, seq):
        out = []
        for key, corners in faces:
            n = app(seq, NRM[key])
            if n[0] + n[1] + n[2] > 0.01:            # грань дивиться на глядача
                pts = [iso(app(seq, c), cx, cy, s) for c in corners]
                d = "M " + " L ".join("%.1f %.1f" % pt for pt in pts) + " z"
                out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>'
                           % (d, COL[key], INK))
        return "".join(out)

    s = 36
    xs = [152, 448, 744]        # старт · після 1-го · після 2-го повороту
    yA, yB = 170, 398

    # тріада осей (легенда) у лівому верхньому куті
    tx, ty, ts = 58, 84, 20
    f.append(vec(tx, ty, tx + 0.866 * ts, ty + 0.5 * ts, color=MUTED, sw=2, head=8))
    f.append(vec(tx, ty, tx - 0.866 * ts, ty + 0.5 * ts, color=MUTED, sw=2, head=8))
    f.append(vec(tx, ty, tx, ty - ts, color=MUTED, sw=2, head=8))
    f.append(text(tx + 0.866 * ts + 7, ty + 0.5 * ts + 5, "X", size=11, color=MUTED, anchor="start"))
    f.append(text(tx - 0.866 * ts - 7, ty + 0.5 * ts + 5, "Y", size=11, color=MUTED, anchor="end"))
    f.append(text(tx, ty - ts - 5, "Z", size=11, color=MUTED))

    # підписи рядів (по центру над першим кубиком)
    f.append(text(xs[0], yA - 84, "порядок A", size=13, bold=True, color=INK))
    f.append(text(xs[0], yB - 84, "порядок B", size=13, bold=True, color=INK))

    # кубики
    f.append(cube(xs[0], yA, s, []))
    f.append(cube(xs[1], yA, s, [Rx]))
    f.append(cube(xs[2], yA, s, [Rx, Rz]))
    f.append(cube(xs[0], yB, s, []))
    f.append(cube(xs[1], yB, s, [Rz]))
    f.append(cube(xs[2], yB, s, [Rz, Rx]))

    # стрілки-операції з підписами
    def op(x1, x2, y, label):
        f.append(vec(x1, y, x2, y, color=INK, sw=2.4, head=12))
        f.append(text((x1 + x2) / 2, y - 15, label, size=12, bold=True, color=INK))
    op(xs[0] + 66, xs[1] - 66, yA, "×90° навколо X")
    op(xs[1] + 66, xs[2] - 66, yA, "×90° навколо Z")
    op(xs[0] + 66, xs[1] - 66, yB, "×90° навколо Z")
    op(xs[1] + 66, xs[2] - 66, yB, "×90° навколо X")

    b, w, h = textbox(W / 2, H - 30,
                      "Однакові повороти, різний порядок → різні орієнтації: повороти НЕ комутують",
                      size=14, pad=11, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "rotations-noncommute.svg"), W, H, *f)


# ── Фігура: v = ω × r для точки поза віссю (ρ = r·sinφ) ──────────────────────
def fig_omega_cross_r():
    W, H = 720, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Точка поза віссю: v = ω × r,  |v| = ω·r·sinφ",
                  size=17, bold=True))

    axx = 290
    O = (axx, 392)
    f.append(line(axx, 96, axx, 410, color=MUTED, sw=1.6, dash="6,6"))     # вісь
    f.append(vec(axx, O[1], axx, 120, color=FIELD, sw=3.2, head=14))       # ω
    f.append(text(axx + 15, 132, "ω", size=22, bold=True, color=FIELD, anchor="start"))

    phi = math.radians(42)
    Rlen = 208
    P = (axx + Rlen * math.sin(phi), O[1] - Rlen * math.cos(phi))
    f.append(vec(O[0], O[1], P[0], P[1], color=INK, sw=2.8, head=13))      # r
    mid = ((O[0] + P[0]) / 2, (O[1] + P[1]) / 2)
    f.append(text(mid[0] - 15, mid[1] - 2, "r", size=16, bold=True, italic=True, color=INK, anchor="end"))

    # кут φ між віссю (вгору) і r
    rr = 50
    x0, y0 = O[0], O[1] - rr
    x1 = O[0] + rr * math.cos(math.radians(48))
    y1 = O[1] - rr * math.sin(math.radians(48))
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8"/>' % (x0, y0, rr, rr, x1, y1, INK))
    f.append(text(O[0] + 13, O[1] - 40, "φ", size=16, italic=True, color=INK))

    # перпендикуляр до осі: ρ = r·sinφ
    C = (axx, P[1])
    f.append(line(C[0], C[1], P[0], P[1], color=NEG, sw=2.0, dash="4,4"))
    f.append(line(C[0], C[1] + 11, C[0] + 11, C[1] + 11, color=NEG, sw=1.6))   # прямий кут
    f.append(line(C[0] + 11, C[1] + 11, C[0] + 11, C[1], color=NEG, sw=1.6))
    f.append(text((C[0] + P[0]) / 2, C[1] - 11, "ρ = r·sinφ", size=13, bold=True, color=NEG))

    # орбіта точки — еліпс у перспективі
    rho = P[0] - axx
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="5,5"/>'
             % (axx, P[1], rho, rho * 0.30, MUTED))
    f.append(text(axx, P[1] + rho * 0.30 + 20, "коло радіуса ρ", size=11, color=MUTED))

    # v — перпендикулярна до площини (ω, r): у сторінку (⊗)
    f.append(circle(P[0], P[1], 12, fill=BG, stroke=POS, sw=2.4))
    f.append(line(P[0] - 8.5, P[1] - 8.5, P[0] + 8.5, P[1] + 8.5, color=POS, sw=2.0))
    f.append(line(P[0] - 8.5, P[1] + 8.5, P[0] + 8.5, P[1] - 8.5, color=POS, sw=2.0))
    f.append(text(P[0] + 22, P[1] - 5, "v = ω × r", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(P[0] + 22, P[1] + 14, "(⊥ до ω і до r)", size=11, color=POS, anchor="start"))

    b, w, h = textbox(200, H - 34, "|v| = ω·ρ = ω·r·sinφ", size=15, pad=11,
                      fill="#f0f6f1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "omega-cross-r-derivation.svg"), W, H, *f)


# ── Фігура (вставка proj): зсув гіроскопа накопичується в дрейф кута ──────────
def fig_bias_drift():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Сталий зсув гіроскопа інтеграл перетворює на дрейф кута",
                  size=16.5, bold=True))

    L, R, T, B = 100, 690, 82, 400
    tmax, dmax = 120.0, 60.0

    def X(t): return L + (t / tmax) * (R - L)
    def Y(d): return B - (d / dmax) * (B - T)

    for d in (15, 30, 45, 60):
        f.append(line(L, Y(d), R, Y(d), color="#eceff3", sw=1))
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for d in (0, 15, 30, 45, 60):
        f.append(line(L - 5, Y(d), L, Y(d), color=INK, sw=1.4))
        f.append(text(L - 12, Y(d) + 4, str(d), size=11, color=MUTED, anchor="end"))
    for t in (0, 30, 60, 90, 120):
        f.append(line(X(t), B, X(t), B + 5, color=INK, sw=1.4))
        f.append(text(X(t), B + 22, str(int(t)), size=11, color=MUTED))
    f.append(text(L - 48, T - 16, "похибка кута, °", size=12, color=MUTED, anchor="middle"))
    f.append(text((L + R) / 2, B + 44, "час, с", size=12.5, color=MUTED))

    # Лінія 1: некалібрований зсув 1.8 °/с — вилітає за верх
    t_top = dmax / 1.8
    f.append(line(X(0), Y(0), X(t_top), Y(dmax), color=POS, sw=3.4))
    f.append(vec(X(t_top), Y(dmax), X(t_top) + 22, Y(dmax) - 30, color=POS, sw=3.0, head=12))
    # Лінія 2: залишок після калібрування 0.1 °/с
    f.append(line(X(0), Y(0), X(tmax), Y(0.1 * tmax), color=NEG, sw=3.2))
    # Лінія 3: зшитий з акселерометром — обмежений
    pts = []
    for i in range(0, 73):
        t = tmax * i / 72
        d = 2.6 + 1.4 * math.sin(t / 6.5)
        pts.append((X(t), Y(d)))
    dpath = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (dpath, FIELD))

    # легенда у вільному верхньому куті поля
    lx, ly, dy = 316, 116, 30
    rows = [(POS, "некалібрований зсув  ≈ 1.8 °/с  →  108 °/хв"),
            (NEG, "після калібрування  ≈ 0.1 °/с  →  6 °/хв"),
            (FIELD, "зшитий з акселерометром — обмежений")]
    for (col, s) in rows:
        f.append(line(lx, ly, lx + 34, ly, color=col, sw=3.4))
        f.append(text(lx + 44, ly + 4, s, size=12, color=col, anchor="start", bold=True))
        ly += dy

    b, w, h = textbox(R + 108, 168,
                      "θ_похибка = b · t\n\nсталий зсув b\nросте ЛІНІЙНО\nй не спиняється\n\nкалібрування\nзбиває нахил,\nта не в нуль\n\nакселерометр\nставить стелю",
                      size=11.5, pad=12, fill=FILL, stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "gyro-bias-drift.svg"), W, H, *f)


# ── Фігура (вставка proj): комплементарний фільтр — зшити гіро й акселерометр ──
def fig_comp_blend():
    W, H = 940, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Комплементарний фільтр: гіро тримає швидке, акселерометр — повільне",
                  size=15.5, bold=True))

    def box(cx, cy, w, h, s, stroke, size=12.5):
        f.append(fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, pad=8,
                        fill=FILL, stroke=stroke, sw=1.8, bold=True, color=INK))
        return (cx, cy, w, h)

    gyro = box(112, 118, 156, 62, "гіроскоп\nω [рад/с]", NEG)
    accel = box(112, 320, 176, 62, "акселерометр\na [м/с²]", FIELD)
    integ = box(378, 118, 192, 62, "інтегратор\nθ ← θ + ω·dt", NEG)
    atanb = box(378, 320, 192, 62, "нахил\nθ_a = atan2(a)", FIELD)
    blend = box(640, 219, 198, 98, "зшивач\nα·(θ + ω·dt)\n+ (1−α)·θ_a", INK)
    out = box(858, 219, 118, 66, "кут θ", MUTED)

    def edge_r(bx): return (bx[0] + bx[2] / 2, bx[1])
    def edge_l(bx): return (bx[0] - bx[2] / 2, bx[1])

    f.append(vec(*edge_r(gyro), *edge_l(integ), color=NEG, sw=2.6, head=11))
    f.append(vec(*edge_r(accel), *edge_l(atanb), color=FIELD, sw=2.6, head=11))
    f.append(vec(edge_r(integ)[0], edge_r(integ)[1], blend[0] - blend[2] / 2, blend[1] - 27,
                 color=NEG, sw=2.6, head=11))
    f.append(vec(edge_r(atanb)[0], edge_r(atanb)[1], blend[0] - blend[2] / 2, blend[1] + 27,
                 color=FIELD, sw=2.6, head=11))
    f.append(vec(*edge_r(blend), *edge_l(out), color=INK, sw=2.8, head=12))

    f.append(text(500, 96, "вага α ≈ 0.98", size=12, color=NEG, bold=True))
    f.append(text(500, 348, "вага 1 − α", size=12, color=FIELD, bold=True))
    f.append(text(378, 170, "гладко, але дрейфує", size=11.5, color=MUTED))
    f.append(text(378, 368, "абсолютно, але шумно", size=11.5, color=MUTED))

    b, w, h = textbox(W / 2, H - 28,
                      "гіроскоп точний на коротких часах (дрейф ще не набіг) · "
                      "акселерометр точний надовго (бачить, де низ, і не тікає)",
                      size=11.5, pad=9, fill="#f6f8fc", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "complementary-blend.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_carousel(), fig_accel(), fig_axis(), fig_why360(), fig_timeline(),
          fig_noncommute(), fig_omega_cross_r(),
          fig_bias_drift(), fig_comp_blend()]
    print("written:")
    for p in ps:
        print("  ", p)
