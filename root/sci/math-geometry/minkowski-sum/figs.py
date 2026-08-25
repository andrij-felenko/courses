# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Сума Мінковського: роздування однієї фігури іншою».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Спільна геометрія (усе рахуємо в математичних координатах, y вгору) ──────
def poly_pts(pts, sx, sy):
    """Рядок points= для <polygon>: список математичних точок → екранні."""
    return " ".join("%.1f,%.1f" % (sx(x), sy(y)) for x, y in pts)


def offset_convex(poly, r, step=10):
    """Межа poly ⊕ круг радіуса r для опуклого poly (CCW): ребра відсунуті на r,
    вершини з'єднані дугами. Повертає список точок (дуги дискретизовані)."""
    n = len(poly)
    out = []
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        xp, yp = poly[i - 1]
        a_in = math.atan2(y0 - yp, x0 - xp) - math.pi / 2   # нормаль попереднього ребра
        a_out = math.atan2(y1 - y0, x1 - x0) - math.pi / 2  # нормаль наступного ребра
        while a_out < a_in:
            a_out += 2 * math.pi
        k = max(2, int((a_out - a_in) / math.radians(step)) + 1)
        for j in range(k + 1):
            a = a_in + (a_out - a_in) * j / k
            out.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))
    return out


def lowest_first(poly):
    """Циклічно переставити опуклий CCW-багатокутник так, щоб він починався
    з найнижчої (за нею — найлівішої) вершини."""
    k = min(range(len(poly)), key=lambda i: (poly[i][1], poly[i][0]))
    return poly[k:] + poly[:k]


def mink_convex(P, Q):
    """Сума Мінковського двох опуклих CCW-багатокутників — злиття списків ребер
    за напрямом (той самий алгоритм, що описано в статті)."""
    P, Q = lowest_first(P), lowest_first(Q)
    P = P + P[:2]
    Q = Q + Q[:2]
    res, i, j = [], 0, 0
    while i < len(P) - 2 or j < len(Q) - 2:
        res.append((P[i][0] + Q[j][0], P[i][1] + Q[j][1]))
        cx = ((P[i + 1][0] - P[i][0]) * (Q[j + 1][1] - Q[j][1]) -
              (P[i + 1][1] - P[i][1]) * (Q[j + 1][0] - Q[j][0]))
        if cx >= 0 and i < len(P) - 2:
            i += 1
        if cx <= 0 and j < len(Q) - 2:
            j += 1
    return res


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def shift(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


# ── Фігура 1. Роздута перешкода: тіло робота переїжджає в перешкоду ──────────
# Ідея: зліва робот радіуса r ковзає впритул до перешкоди, його центр малює
# криву; справа та сама крива вже є межею роздутої перешкоди, а робот — точка.
def fig_cspace():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 32, "Роздування перешкоди: тіло робота переходить у перешкоду, робот стає точкою",
                  size=17, bold=True))

    obst = [(0, 0), (128, -12), (156, 92), (62, 134), (-24, 84)]
    r = 40

    # ---- ліва панель ----
    ox, oy = 210, 300
    sx = lambda x: ox + x
    sy = lambda y: oy - y
    P.append(text(210, 74, "робот ковзає впритул", size=13, bold=True, color=MUTED))

    ring = offset_convex(obst, r)
    P.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-dasharray="7 5"/>' % (poly_pts(ring, sx, sy), NEG))
    P.append('<polygon points="%s" fill="#e8eaed" stroke="%s" stroke-width="2.2"/>'
             % (poly_pts(obst, sx, sy), LINE))
    P.append(text(sx(62), sy(58), "перешкода", size=13, bold=True))

    # чотири положення робота впритул + центри
    for t in (0.30, 0.62, 0.86, 0.06):
        k = int(t * len(ring)) % len(ring)
        cx, cy = ring[k]
        P.append(circle(sx(cx), sy(cy), r, fill="rgba(0,0,0,0)", stroke=FIELD, sw=1.8))
        P.append(circle(sx(cx), sy(cy), 3.6, fill=NEG, stroke=NEG, sw=1.2))
    P.append(text(sx(-96), sy(160), "робот радіуса r", size=12, color=FIELD, bold=True, anchor="start"))
    P.append(text(sx(-96), sy(-92), "слід центра", size=12, color=NEG, bold=True, anchor="start"))

    # ---- права панель ----
    ox2, oy2 = 690, 300
    sx2 = lambda x: ox2 + x
    sy2 = lambda y: oy2 - y
    P.append(text(690, 74, "заборонена зона для центра", size=13, bold=True, color=MUTED))

    P.append('<polygon points="%s" fill="#eaf0fd" stroke="%s" stroke-width="2.2"/>'
             % (poly_pts(ring, sx2, sy2), NEG))
    P.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="5 4"/>' % (poly_pts(obst, sx2, sy2), MUTED))
    P.append(text(sx2(62), sy2(58), "перешкода ⊕ круг", size=13, bold=True, color=NEG))

    # робот-точка веде шлях повз роздуту зону
    px = [(-150, 190), (-40, 150), (72, 168), (176, 132), (232, 44)]
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (poly_pts(px, sx2, sy2), FIELD))
    P.append(circle(sx2(72), sy2(168), 5.2, fill=FIELD, stroke=FIELD, sw=1.5))
    P.append(text(sx2(72), sy2(186), "робот — точка", size=12, color=FIELD, bold=True))

    render("img/cspace.svg", W, H, *P)


# ── Фігура 2. Опуклі багатокутники: злиття ребер за напрямом ─────────────────
# Ідея: у опуклого багатокутника ребра впорядковані за напрямом; сума —
# це один відсортований список ребер обох, зі складанням однаково напрямлених.
def fig_edge_merge():
    W, H = 980, 520
    P = []
    P.append(text(W / 2, 32, "Сума двох опуклих: ребра обох вишикувано за напрямом в один список",
                  size=17, bold=True))

    u = 26  # пікселів на одиницю
    A = [(0, 0), (4, 0), (0, 3)]
    B = [(0, 0), (1, 0), (1, 1), (0, 1)]
    S = mink_convex(A, B)

    # ---- ліва колонка: A і B ----
    ax, ay = 60, 210
    sxA = lambda x: ax + x * u
    syA = lambda y: ay - y * u
    P.append('<polygon points="%s" fill="#eaf0fd" stroke="%s" stroke-width="2.2"/>'
             % (poly_pts(A, sxA, syA), NEG))
    P.append(text(ax + 42, ay - 96, "A", size=15, bold=True, color=NEG))
    P.append(text(ax + 4, ay + 24, "катети 4 і 3", size=11.5, color=MUTED, anchor="start"))

    bx, by = 60, 400
    sxB = lambda x: bx + x * u
    syB = lambda y: by - y * u
    P.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2.2"/>'
             % (poly_pts(B, sxB, syB), POS))
    P.append(text(bx + 46, by - 12, "B — квадрат 1×1", size=13, bold=True, color=POS, anchor="start"))

    # ---- середина: таблиця напрямів ----
    c0, c1, c2, c3 = 250, 350, 452, 556
    y0 = 128
    P.append(text(c0, y0, "напрям", size=12.5, bold=True, color=MUTED, anchor="start"))
    P.append(text(c1, y0, "ребро A", size=12.5, bold=True, color=NEG, anchor="start"))
    P.append(text(c2, y0, "ребро B", size=12.5, bold=True, color=POS, anchor="start"))
    P.append(text(c3, y0, "ребро суми", size=12.5, bold=True, anchor="start"))
    P.append(line(c0 - 8, y0 + 10, c3 + 96, y0 + 10, color=MUTED, sw=1))

    rows = [("0°", "(4, 0)", "(1, 0)", "(5, 0)"),
            ("90°", "—", "(0, 1)", "(0, 1)"),
            ("143.1°", "(−4, 3)", "—", "(−4, 3)"),
            ("180°", "—", "(−1, 0)", "(−1, 0)"),
            ("270°", "(0, −3)", "(0, −1)", "(0, −4)")]
    for i, (d, a, b, s) in enumerate(rows):
        yy = y0 + 44 + i * 34
        P.append(text(c0, yy, d, size=13, anchor="start"))
        P.append(text(c1, yy, a, size=13, color=NEG if a != "—" else MUTED, anchor="start"))
        P.append(text(c2, yy, b, size=13, color=POS if b != "—" else MUTED, anchor="start"))
        P.append(text(c3, yy, s, size=13, bold=True, anchor="start"))

    P.append(text(c0, y0 + 44 + 5 * 34 + 20,
                  "однаково напрямлені ребра складаються — тому вершин 5, а не 7",
                  size=12, color=MUTED, anchor="start"))

    # ---- права колонка: результат ----
    rx, ry = 720, 400
    sxS = lambda x: rx + x * u
    syS = lambda y: ry - y * u
    P.append('<polygon points="%s" fill="#eefaf2" stroke="%s" stroke-width="2.4"/>'
             % (poly_pts(S, sxS, syS), FIELD))
    P.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="5 4"/>' % (poly_pts(A, sxS, syS), NEG))
    P.append(text(sxS(2.6), syS(1.4), "A ⊕ B", size=15, bold=True, color=FIELD))

    for (vx, vy), (dx, dy, anc) in zip(S, [(-8, 16, "end"), (10, 16, "start"),
                                           (14, 6, "start"), (14, -8, "start"),
                                           (-8, -10, "end")]):
        P.append(circle(sxS(vx), syS(vy), 3.4, fill=BG, stroke=FIELD, sw=2))
        P.append(text(sxS(vx) + dx, syS(vy) + dy, "(%g, %g)" % (vx, vy),
                      size=11.5, color=MUTED, anchor=anc))

    render("img/edge-merge.svg", W, H, *P)


# ── Фігура 3. Різниця Мінковського: перетин ⇄ початок координат у різниці ────
def fig_difference():
    W, H = 940, 620
    P = []
    P.append(text(W / 2, 32, "Перевірка перетину: чи накрив A ⊕ (−B) початок координат",
                  size=17, bold=True))

    A = [(0, 0), (86, 18), (66, 96), (-10, 68)]
    B = [(0, 0), (66, -10), (76, 58), (18, 66)]
    negB = [(-x, -y) for x, y in B]
    base = mink_convex(A, negB)

    def row(tB, ytop, caption, verdict, show_dist):
        Ap = A
        Bp = shift(B, tB[0], tB[1])
        cso = shift(base, -tB[0], -tB[1])

        # ліва панель — самі фігури
        ox, oy = 150, ytop + 175
        sx = lambda x: ox + x * 0.78
        sy = lambda y: oy - y * 0.78
        P.append('<polygon points="%s" fill="#eaf0fd" stroke="%s" stroke-width="2.2"/>'
                 % (poly_pts(Ap, sx, sy), NEG))
        P.append('<polygon points="%s" fill="rgba(192,57,43,0.18)" stroke="%s" stroke-width="2.2"/>'
                 % (poly_pts(Bp, sx, sy), POS))
        P.append(text(sx(34), sy(48), "A", size=15, bold=True, color=NEG))
        P.append(text(sx(tB[0] + 46), sy(tB[1] + 30), "B", size=15, bold=True, color=POS))
        P.append(text(60, ytop + 44, caption, size=13.5, bold=True, anchor="start"))

        # права панель — множина різниць
        x0, y0, x1, y1 = bbox(cso)
        cx0, cy0 = 700, ytop + 175
        k = 0.62
        px = lambda x: cx0 + (x - (x0 + x1) / 2) * k
        py = lambda y: cy0 - (y - (y0 + y1) / 2) * k
        P.append('<polygon points="%s" fill="#eefaf2" stroke="%s" stroke-width="2.2"/>'
                 % (poly_pts(cso, px, py), FIELD))
        P.append(text(px((x0 + x1) / 2), py((y0 + y1) / 2) + 5, "A ⊕ (−B)",
                      size=14, bold=True, color=FIELD))

        # початок координат
        P.append(line(px(0) - 13, py(0), px(0) + 13, py(0), color=INK, sw=2))
        P.append(line(px(0), py(0) - 13, px(0), py(0) + 13, color=INK, sw=2))
        P.append(text(px(0), py(0) + 30, "0", size=13, bold=True))
        P.append(text(520, ytop + 44, verdict, size=13.5, bold=True, anchor="start",
                      color=FIELD if show_dist is None else POS))

        if show_dist is not None:
            qx, qy = show_dist
            P.append(line(px(0), py(0), px(qx), py(qy), color=POS, sw=2, dash="6 4"))
            P.append(text((px(0) + px(qx)) / 2 + 6, (py(0) + py(qy)) / 2 - 12,
                          "= відстань між A і B", size=12, color=POS, bold=True, anchor="start"))

    def closest_on_poly(poly):
        best, bd = None, 1e18
        n = len(poly)
        for i in range(n):
            ax_, ay_ = poly[i]
            bx_, by_ = poly[(i + 1) % n]
            dx, dy = bx_ - ax_, by_ - ay_
            t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, -(ax_ * dx + ay_ * dy) / (dx * dx + dy * dy)))
            qx, qy = ax_ + t * dx, ay_ + t * dy
            d = qx * qx + qy * qy
            if d < bd:
                best, bd = (qx, qy), d
        return best

    row((44, 22), 60, "A і B перекриваються", "0 всередині → перетин є", None)
    cso2 = shift(base, -168, -34)
    row((168, 34), 350, "A і B не дотикаються", "0 поза множиною → перетину немає",
        closest_on_poly(cso2))

    render("img/difference-origin.svg", W, H, *P)


# ── Фігура 4 (вставка math). Опорна функція складається ──────────────────────
# Ідея: один і той самий напрям u у трьох панелях; відстань від початку
# координат до опорної прямої для суми дорівнює сумі таких відстаней.
def fig_support_add():
    W, H = 990, 478
    P = []
    P.append(text(W / 2, 30, "Опорна функція в одному напрямі: h(A ⊕ B) = h(A) + h(B)",
                  size=17, bold=True))
    P.append(text(W / 2, 54, "напрям u нахилений на 55° і той самий у всіх трьох панелях",
                  size=12.5, color=MUTED))

    th = math.radians(55)
    ux, uy = math.cos(th), math.sin(th)
    u_unit = 30.0

    A = [(0, 0), (4, 0), (0, 3)]
    B = [(0, 0), (1, 0), (1, 1), (0, 1)]
    S = mink_convex(A, B)

    def panel(ox, oy, poly, fill, col, half, caption):
        sx = lambda x: ox + x * u_unit
        sy = lambda y: oy - y * u_unit
        h = max(ux * x + uy * y for x, y in poly)
        top = max(poly, key=lambda p: ux * p[0] + uy * p[1])

        # опорна пряма: через точку h·u, напрямний вектор (−sin, cos)
        fx, fy = h * ux, h * uy
        t = half / u_unit
        P.append(line(sx(fx - t * uy), sy(fy + t * ux),
                      sx(fx + t * uy), sy(fy - t * ux), color=MUTED, sw=1.8))

        P.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2.2"/>'
                 % (poly_pts(poly, sx, sy), fill, col))

        # відрізок від початку координат до опорної прямої = h
        P.append(line(sx(0), sy(0), sx(fx), sy(fy), color=POS, sw=2, dash="6 4"))
        P.append(line(sx(0) - 9, sy(0), sx(0) + 9, sy(0), color=INK, sw=1.6))
        P.append(line(sx(0), sy(0) - 9, sx(0), sy(0) + 9, color=INK, sw=1.6))

        # стрілка напряму u
        P.append(arrow(sx(0), sy(0), sx(0) + 52 * ux, sy(0) - 52 * uy, color=POS, sw=2))

        # рекордсмен
        P.append(circle(sx(top[0]), sy(top[1]), 4.2, fill=BG, stroke=col, sw=2.4))

        P.append(mtext(ox + 20, 385, caption + ["h = %.3f" % h],
                       size=12.5, color=col, lh=1.35))
        return h

    hA = panel(150, 322, A, "#eaf0fd", NEG, 100,
               ["A — трикутник (0,0), (4,0), (0,3)", "рекордсмен — вершина (0, 3)"])
    hB = panel(455, 322, B, "#fdecea", POS, 62,
               ["B — квадрат 1×1", "рекордсмен — вершина (1, 1)"])
    hS = panel(700, 322, S, "#eefaf2", FIELD, 118,
               ["A ⊕ B — п'ятикутник", "рекордсмен (1, 4) = (0,3) + (1,1)"])

    P.append(text(352, 250, "⊕", size=26, bold=True, color=MUTED))
    P.append(text(632, 250, "=", size=26, bold=True, color=MUTED))
    P.append(text(W / 2, 448, "%.3f + %.3f = %.3f" % (hA, hB, hS),
                  size=15, bold=True, color=POS))

    render("img/support-add.svg", W, H, *P)


# ── Фігура 5 (вставка math). Розбиття для формули Штайнера ───────────────────
def fig_steiner():
    W, H = 940, 480
    P = []
    P.append(text(W / 2, 30, "Формула Штайнера: з чого складається K ⊕ rD",
                  size=17, bold=True))

    cx, cy, u = 250, 258, 58

    def sector(x0, y0, r, a0, a1):
        p0 = (x0 + r * math.cos(math.radians(a0)), y0 - r * math.sin(math.radians(a0)))
        p1 = (x0 + r * math.cos(math.radians(a1)), y0 - r * math.sin(math.radians(a1)))
        return ('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f Z" '
                'fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
                % (x0, y0, p0[0], p0[1], r, r, p1[0], p1[1], POS))

    # смуги вздовж сторін
    for x, y, w, hh in ((cx + u, cy - u, u, 2 * u), (cx - u, cy - 2 * u, 2 * u, u),
                        (cx - 2 * u, cy - u, u, 2 * u), (cx - u, cy + u, 2 * u, u)):
        P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eefaf2" '
                 'stroke="%s" stroke-width="1.8"/>' % (x, y, w, hh, FIELD))
    # сектори в кутах
    for x0, y0, a0 in ((cx + u, cy - u, 0), (cx - u, cy - u, 90),
                       (cx - u, cy + u, 180), (cx + u, cy + u, 270)):
        P.append(sector(x0, y0, u, a0, a0 + 90))
    # сам квадрат
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eaf0fd" '
             'stroke="%s" stroke-width="2.2"/>' % (cx - u, cy - u, 2 * u, 2 * u, NEG))

    P.append(text(cx, cy + 5, "K", size=17, bold=True, color=NEG))
    P.append(text(cx + int(1.5 * u), cy + 5, "|e|·r", size=12.5, color=FIELD, bold=True))
    P.append(text(cx, cy - int(1.5 * u) + 5, "|e|·r", size=12.5, color=FIELD, bold=True))
    P.append(text(cx - int(1.5 * u), cy + 5, "|e|·r", size=12.5, color=FIELD, bold=True))
    P.append(text(cx, cy + int(1.5 * u) + 5, "|e|·r", size=12.5, color=FIELD, bold=True))
    P.append(text(cx + u + 26, cy - u - 22, "θᵢ", size=13.5, color=POS, bold=True))

    P.append(mtext(cx, 408, ["чотири смуги |eᵢ|·r і чотири сектори",
                             "покривають K ⊕ rD без накладань"],
                   size=12.5, color=MUTED, lh=1.35))

    # права панель — сектори склалися в круг
    dx, dy = 726, 258
    P.append(circle(dx, dy, u, fill="#fdecea", stroke=POS, sw=2.2))
    for a in (0, 90, 180, 270):
        P.append(line(dx, dy, dx + u * math.cos(math.radians(a)),
                      dy - u * math.sin(math.radians(a)), color=POS, sw=1.4, dash="5 4"))
    P.append(arrow(430, dy, 630, dy, color=MUTED, sw=2))
    P.append(text(530, dy - 22, "кути збираються", size=12.5, color=MUTED, bold=True))
    P.append(mtext(dx, 356, ["зовнішні кути опуклого", "багатокутника дають 2π,",
                             "тож сектори складаються в круг πr²"],
                   size=12.5, color=MUTED, lh=1.35))

    P.append(text(W / 2, 452, "area(K ⊕ rD) = area(K) + r·perim(K) + πr²",
                  size=15.5, bold=True))

    render("img/steiner.svg", W, H, *P)


# ── Фігура (вставка proj). Належність початку координат: пошук по віялу ──────
# Ідея: з опорної вершини v0 багатокутник розбито на сектори, промені яких ідуть
# за зростанням кута; потрібний сектор знаходиться двійковим пошуком, і лишається
# одна перевірка — з якого боку останнього ребра лежить точка.
def fig_fan_search():
    W, H = 1010, 545
    P = []
    P.append(text(W / 2, 30, "Чи накрив опуклий багатокутник початок координат — за O(log n)",
                  size=17, bold=True))

    V = [(-3, -4), (2, -4), (5, -1), (6, 3), (4, 6), (0, 7), (-3, 5), (-4, 0)]
    n = len(V)
    u = 30.0
    ox, oy = 250, 335
    sx = lambda x: ox + x * u
    sy = lambda y: oy - y * u

    P.append(text(250, 66, "віяло з опорної вершини v0", size=13, bold=True, color=MUTED))

    # сектор, що лишився після пошуку
    P.append('<polygon points="%s" fill="#eefaf2" stroke="none"/>'
             % poly_pts([V[0], V[3], V[4]], sx, sy))
    P.append('<polygon points="%s" fill="rgba(36,87,214,0.06)" stroke="%s" stroke-width="2.4"/>'
             % (poly_pts(V, sx, sy), NEG))

    for k in range(1, n):
        hot = k in (3, 4)
        P.append(line(sx(V[0][0]), sy(V[0][1]), sx(V[k][0]), sy(V[k][1]),
                      color=FIELD if hot else MUTED, sw=2.2 if hot else 1.1,
                      dash=None if hot else "4 4"))
    # ребро, на якому все вирішується
    P.append(line(sx(V[3][0]), sy(V[3][1]), sx(V[4][0]), sy(V[4][1]), color=FIELD, sw=3.4))

    lab = [(-22, 20), (16, 22), (22, 12), (24, 2), (18, -14), (2, -18), (-22, -12), (-24, 4)]
    for k, (vx, vy) in enumerate(V):
        P.append(circle(sx(vx), sy(vy), 4.0, fill=BG, stroke=NEG, sw=2))
        dx, dy = lab[k]
        P.append(text(sx(vx) + dx, sy(vy) + dy, "v%d" % k, size=12.5, bold=True,
                      color=FIELD if k in (0, 3, 4) else MUTED))

    P.append(line(sx(0) - 13, sy(0), sx(0) + 13, sy(0), color=POS, sw=2.4))
    P.append(line(sx(0), sy(0) - 13, sx(0), sy(0) + 13, color=POS, sw=2.4))
    P.append(text(sx(0) - 34, sy(0) - 16, "0", size=14, bold=True, color=POS))

    # ---- трасування пошуку ----
    tx = 600
    P.append(text(tx, 66, "три порівняння замість восьми", size=13, bold=True,
                  color=MUTED, anchor="start"))
    cols = [tx, tx + 82, tx + 152, tx + 214]
    for c, s in zip(cols, ("крок", "lo…hi", "mid", "знак і що звузили")):
        P.append(text(c, 114, s, size=12.5, bold=True, color=MUTED, anchor="start"))
    P.append(line(tx - 8, 126, tx + 372, 126, color=MUTED, sw=1))

    for i, r in enumerate([("1", "1…7", "4", "−    hi = 4"),
                           ("2", "1…4", "2", "+    lo = 2"),
                           ("3", "2…4", "3", "+    lo = 3")]):
        yy = 158 + i * 34
        for c, s in zip(cols, r):
            P.append(text(c, yy, s, size=13, anchor="start"))

    P.append(text(tx, 296, "сектор звужено до пари v3, v4", size=13.5, bold=True,
                  color=FIELD, anchor="start"))
    P.append(mtext(tx, 332, ["лишилась одна перевірка — з якого",
                             "боку ребра v3 → v4 лежить точка:"],
                   size=12.5, color=MUTED, anchor="start", lh=1.45))
    P.append(text(tx, 402, "(v4 − v3) × (0 − v3) = 24 > 0", size=14, bold=True, anchor="start"))
    P.append(mtext(tx, 436, ["зліва від ребра, тобто всередині —",
                             "початок координат накрито"],
                   size=12.5, color=MUTED, anchor="start", lh=1.45))

    render("img/fan-search.svg", W, H, *P)


if __name__ == "__main__":
    fig_cspace()
    fig_edge_merge()
    fig_difference()
    fig_support_add()
    fig_steiner()
    fig_fan_search()
    print("OK: 6 figures -> img/")
