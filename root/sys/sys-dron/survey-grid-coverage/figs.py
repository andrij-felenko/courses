# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── спільна геометрія: розсічення полігона паралельними прямими ────────────────
# Саме те, що робить генератор галсів: повертаємо систему так, щоб галси стали
# горизонтальними, ріжемо полігон горизонталями й беремо парні проміжки.

def rot(pts, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def scanlines(poly, ang, spacing):
    """Список відрізків-галсів у вихідній системі, у порядку проходу."""
    R = rot(poly, -ang)
    ys = [p[1] for p in R]
    y0, y1 = min(ys), max(ys)
    n = max(1, int(math.ceil((y1 - y0) / spacing)))
    step = (y1 - y0) / n
    segs = []
    for i in range(n):
        y = y0 + (i + 0.5) * step
        xs = []
        for j in range(len(R)):
            ax, ay = R[j]
            bx, by = R[(j + 1) % len(R)]
            if (ay <= y < by) or (by <= y < ay):
                t = (y - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            segs.append(((xs[k], y), (xs[k + 1], y)))
    back = rot([p for s in segs for p in s], ang)
    return [(back[2 * i], back[2 * i + 1]) for i in range(len(segs))]


def poly_str(pts):
    return " ".join("%.1f,%.1f" % p for p in pts)


# ── swath: звідки береться відстань між галсами ───────────────────────────────
# Ідея: сенсор бачить під собою смугу шириною w. Дві сусідні лінії кладуть
# дві смуги, які мусять налягати одна на одну — інакше між ними лишається
# непокрита щілина. Відстань між лініями d = w·(1 − перекриття).

def fig_swath():
    W, H = 820, 470
    p = []
    gy = 372.0                     # рівень землі
    ay = 148.0                     # висота апарата на малюнку
    half = 200.0                   # пів-ширини смуги
    d = 160.0                      # відстань між лініями (перекриття 60 %)
    x1 = 250.0
    x2 = x1 + d

    # земля
    p.append(line(40, gy, W - 40, gy, color=INK, sw=2.2))
    p.append(text(W - 44, gy + 20, "земля", size=11, color=MUTED, anchor="end", italic=True))

    # смуга перекриття — світла заливка між смугами
    ox1, ox2 = x2 - half, x1 + half
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" '
             'stroke="none"/>' % (ox1, gy - 26, ox2 - ox1, 26))

    # конуси зору двох галсів
    for cx, col in ((x1, NEG), (x2, POS)):
        p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
                 'stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
                 % (cx, ay, cx - half, gy, cx + half, gy, col))
        p.append(circle(cx, ay, 6, fill=col, stroke=col, sw=1))

    # смуги на землі (товсті відрізки трохи нижче лінії землі)
    p.append(line(x1 - half, gy + 8, x1 + half, gy + 8, color=NEG, sw=5))
    p.append(line(x2 - half, gy + 16, x2 + half, gy + 16, color=POS, sw=5))
    p.append(text(x1 - half - 6, gy + 12, "смуга галса 1", size=11, color=NEG, anchor="end", bold=True))
    p.append(text(x2 + half + 6, gy + 20, "смуга галса 2", size=11, color=POS, anchor="start", bold=True))

    # ширина смуги w — розмірна лінія знизу
    wy = gy + 54
    p.append(line(x1 - half, wy, x1 + half, wy, color=INK, sw=1.3))
    p.append(line(x1 - half, wy - 6, x1 - half, wy + 6, color=INK, sw=1.3))
    p.append(line(x1 + half, wy - 6, x1 + half, wy + 6, color=INK, sw=1.3))
    p.append(text(x1, wy + 20, "w — ширина смуги", size=12, color=INK, bold=True))

    # відстань між лініями d — угорі, між апаратами
    dy = ay - 44
    p.append(line(x1, dy, x2, dy, color=FIELD, sw=1.6))
    p.append(line(x1, dy - 6, x1, dy + 6, color=FIELD, sw=1.6))
    p.append(line(x2, dy - 6, x2, dy + 6, color=FIELD, sw=1.6))
    p.append(text((x1 + x2) / 2, dy - 12, "d", size=14, color=FIELD, bold=True, italic=True))

    # висота H
    p.append(line(120, ay, 120, gy, color=MUTED, sw=1.3, dash="4 4"))
    p.append(line(114, ay, 126, ay, color=MUTED, sw=1.3))
    p.append(line(114, gy, 126, gy, color=MUTED, sw=1.3))
    p.append(text(112, (ay + gy) / 2, "H", size=14, color=MUTED, anchor="end", bold=True, italic=True))

    # підпис перекриття
    p.append(text((ox1 + ox2) / 2, gy - 36, "перекриття", size=11, color=FIELD, bold=True))

    fb, fw, fh = textbox(672, 128, "d = w · (1 − перекриття)\nw = 2·H·tg(поле зору / 2)",
                         size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=12)
    p.append(fb)
    p.append(text(672, 128 + fh / 2 + 18, "перекриття — не розкіш, а запас", size=10, color=MUTED))

    render(os.path.join(OUT, "swath.svg"), W, H, *p,
           title="Смуга сенсора диктує відстань між галсами")


# ── direction: та сама пряма довжина, різна кількість розворотів ───────────────
# Ідея: сумарна довжина прямих ≈ площа/крок і від напрямку НЕ залежить.
# Залежить кількість галсів — вона дорівнює ширині полігона поперек напрямку,
# поділеній на крок. Тож напрямок обирають за найменшою шириною фігури.

FIELD_POLY = [(60, 250), (200, 96), (430, 74), (520, 168), (380, 292), (150, 320)]


def _best_angle(poly):
    """Напрямок галсів, за якого ширина полігона поперек них найменша."""
    best, bang = None, 0.0
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        ang = math.atan2(by - ay, bx - ax)
        R = rot(poly, -ang)
        wdt = max(q[1] for q in R) - min(q[1] for q in R)
        if best is None or wdt < best:
            best, bang = wdt, ang
    return bang, best


def _panel(poly, ang, step, ox, oy, tint, label):
    """Один полігон із галсами; повертає (фрагменти, кількість галсів)."""
    p = []
    pts = [(x + ox, y + oy) for x, y in poly]
    p.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>'
             % (poly_str(pts), tint, INK))
    segs = scanlines(poly, ang, step)
    path = []
    flip = False
    for a, b in segs:
        if flip:
            a, b = b, a
        path.append((a[0] + ox, a[1] + oy))
        path.append((b[0] + ox, b[1] + oy))
        flip = not flip
    if path:
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (poly_str(path), POS))
        p.append(circle(path[0][0], path[0][1], 5, fill="#fff", stroke=FIELD, sw=2.4))
    p.append(text(ox + 290, oy + 360, label, size=12, color=INK, anchor="middle", bold=True))
    return p, len(segs)


def fig_direction():
    W, H = 1180, 470
    p = []
    step = 34.0
    ang, _ = _best_angle(FIELD_POLY)

    a_frags, n_a = _panel(FIELD_POLY, ang, step, 20, 60, "#f2f7f2",
                          "уздовж найменшої ширини")
    b_frags, n_b = _panel(FIELD_POLY, ang + math.pi / 2, step, 600, 60, "#f7f2f2",
                          "поперек неї")
    p += a_frags
    p += b_frags

    p.append(line(590, 70, 590, 420, color=MUTED, sw=1.2, dash="4 5"))

    p.append(text(310, 448, "%d галсів · %d розворотів" % (n_a, n_a - 1),
                  size=13, color=FIELD, bold=True))
    p.append(text(890, 448, "%d галсів · %d розворотів" % (n_b, n_b - 1),
                  size=13, color=POS, bold=True))
    p.append(text(W / 2, 62, "сумарна довжина прямих однакова — площа / крок",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "direction.svg"), W, H, *p,
           title="Напрямок галсів міняє не довжину, а кількість розворотів")


# ── turns: коли розворот не влазить між сусідніми галсами ──────────────────────
# Ідея: півколо розвороту має діаметр d. Якщо мінімальний радіус апарата більший
# за d/2, сусідній перехід неможливий — лінії обходять з пропуском, і діаметр
# розвороту стає кратним кроку.

def fig_turns():
    W, H = 1120, 430
    p = []
    top, bot = 130.0, 330.0
    d = 46.0
    n = 8

    def draw_lines(ox, col):
        out = []
        for i in range(n):
            x = ox + i * d
            out.append(line(x, top, x, bot, color=MUTED, sw=2.4))
            out.append(text(x, bot + 18, "%d" % (i + 1), size=11, color=MUTED))
        return out

    # ліва панель: сусідній розворот, радіус d/2 — замалий
    oxL = 70.0
    p += draw_lines(oxL, MUTED)
    for i in range(0, n - 1):
        x = oxL + i * d
        y = top if i % 2 == 0 else bot
        sw = 1 if i % 2 == 0 else 0
        p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2"/>' % (x, y, d / 2, d / 2, sw, x + d, y, POS))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4 4"/>' % (oxL + 3.5 * d, top - 90, 78, POS))
    p.append(text(oxL + 3.5 * d, top - 176, "коло найменшого радіуса апарата",
                  size=11, color=POS, bold=True))
    p.append(text(oxL + 3.5 * d, bot + 62, "розворот на сусідній галс: діаметр = d",
                  size=12, color=POS, bold=True))
    p.append(text(oxL + 3.5 * d, bot + 84, "d < 2·R — апарат так не вміє",
                  size=12, color=POS))

    # права панель: пропуск через один, діаметр 2d
    oxR = 620.0
    p += draw_lines(oxR, MUTED)
    order = [0, 2, 4, 6, 7, 5, 3, 1]
    for k in range(len(order) - 1):
        i, j = order[k], order[k + 1]
        xi, xj = oxR + i * d, oxR + j * d
        y = top if k % 2 == 0 else bot
        r = abs(xj - xi) / 2
        sw = 1 if (xj > xi) == (y == top) else 0
        p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2"/>' % (xi, y, r, r, sw, xj, y, FIELD))
    p.append(text(oxR + 3.5 * d, bot + 62, "порядок 1·3·5·7·8·6·4·2: діаметр = 2·d",
                  size=12, color=FIELD, bold=True))
    p.append(text(oxR + 3.5 * d, bot + 84, "лишається один вузький перехід 7→8",
                  size=12, color=FIELD))

    p.append(line(560, 100, 560, 380, color=MUTED, sw=1.2, dash="4 5"))

    render(os.path.join(OUT, "turns.svg"), W, H, *p,
           title="Розворот не влазить між сусідніми лініями — галси обходять з пропуском")


# ── cells: чому один прохід не працює на невипуклій фігурі ─────────────────────
# Ідея: коли січна лінія входить у фігуру двічі, галс розривається. Точки, де
# кількість шматків міняється, ріжуть фігуру на комірки; всередині комірки
# розріз завжди один, тож комірку покриває проста змійка.

CELL_POLY = [(60, 300), (60, 90), (250, 90), (250, 190), (420, 190),
             (420, 90), (610, 90), (610, 300)]


def fig_cells():
    W, H = 860, 520
    p = []
    ox, oy = 60, 40
    pts = [(x + ox, y + oy) for x, y in CELL_POLY]

    # три комірки — вертикальні смуги, розділені критичними вершинами
    for x0, x1, col in ((60, 250, "#eef4ff"), (250, 420, "#fdf6e3"), (420, 610, "#eafaf0")):
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="none"/>'
                 % (x0 + ox, 90 + oy, x1 - x0, 210, col))
    # накриваємо виїмку білим, щоб заливка не вилазила за фігуру
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="none"/>'
             % (250 + ox, 90 + oy, 170, 100, BG))

    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (poly_str(pts), INK))

    # січна лінія в середній комірці — два шматки
    sx = 330 + ox
    p.append(line(sx, 60 + oy, sx, 330 + oy, color=NEG, sw=2, dash="5 4"))
    p.append(text(sx, 48 + oy, "січна лінія", size=11, color=NEG, italic=True))

    # критичні вершини
    for cx, cy in ((250, 190), (420, 190)):
        p.append(circle(cx + ox, cy + oy, 6, fill="#fff", stroke=POS, sw=2.6))
    p.append(text(250 + ox - 10, 176 + oy, "критична вершина", size=11, color=POS,
                  anchor="end", bold=True))
    p.append(text(420 + ox + 10, 176 + oy, "тут кількість шматків міняється",
                  size=11, color=POS, anchor="start", bold=True))

    # підписи комірок
    p.append(text(155 + ox, 210 + oy, "A", size=20, color=NEG, bold=True))
    p.append(text(335 + ox, 260 + oy, "B", size=20, color="#b7791f", bold=True))
    p.append(text(515 + ox, 210 + oy, "C", size=20, color=FIELD, bold=True))

    # змійка всередині кожної комірки
    for x0, x1, col in ((66, 244, NEG), (256, 414, "#b7791f"), (426, 604, FIELD)):
        ytop = 96 if col != "#b7791f" else 196
        segs = []
        y = ytop
        flip = False
        while y < 296:
            a = (x0 + ox, y + oy)
            b = (x1 + ox, y + oy)
            segs.append((b, a) if flip else (a, b))
            flip = not flip
            y += 26
        path = [q for s in segs for q in s]
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
                 'stroke-linejoin="round"/>' % (poly_str(path), col))

    # граф сусідства
    gy = 430
    nodes = {"A": (200, gy), "B": (430, gy), "C": (660, gy)}
    for nm, (nx, ny) in nodes.items():
        p.append(circle(nx, ny, 20, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(nx, ny + 6, nm, size=15, color=INK, bold=True))
    p.append(line(220, gy, 410, gy, color=INK, sw=1.6))
    p.append(line(450, gy, 640, gy, color=INK, sw=1.6))
    p.append(text(430, gy + 46, "граф сусідства комірок: обійти всі — і фігуру покрито",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "cells.svg"), W, H, *p,
           title="Невипукла фігура: критичні вершини ріжуть її на комірки")


# ── фігури до вставки proj-coverage-c.md ──────────────────────────────────────
# Той самий полігон, що й у прогоні коду: у місцевій системі (як прийшов) і
# після повороту на кут галсів, де січні — просто y = const.

DEMO_WORLD = [(16, 12), (272, 204), (128, 396), (48, 336),
              (108, 256), (12, 184), (-48, 264), (-128, 204)]
DEMO_GALS = [(20, 0), (340, 0), (340, 240), (240, 240),
             (240, 140), (120, 140), (120, 240), (20, 240)]
DEMO_LINES = [20.0, 60.0, 100.0, 140.0, 180.0, 220.0]
# галси (y, x0, x1) у порядку обходу, як їх видав код
DEMO_ORDER = [(20, 20, 340, 0), (100, 20, 340, 0), (60, 20, 340, 0),
              (140, 20, 120, 1), (220, 20, 120, 1), (180, 20, 120, 1),
              (140, 240, 340, 2), (220, 240, 340, 2), (180, 240, 340, 2)]
CELL_COL = {0: NEG, 1: FIELD, 2: "#b7791f"}


def fig_cut_parity():
    W, H = 940, 560
    p = []

    # ── ліворуч: полігон у місцевій системі ───────────────────────────────────
    s1 = 0.50
    axl, ayb = 60.0, 400.0          # лівий край і низ панелі, px
    wx0, wy0 = -128.0, 12.0

    def A(pt):
        return (axl + (pt[0] - wx0) * s1, ayb - (pt[1] - wy0) * s1)

    p.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>'
             % (poly_str([A(q) for q in DEMO_WORLD]), INK))
    p.append(text(axl + 100, 118, "полігон, як прийшов", size=13, color=INK, bold=True))
    p.append(text(axl + 100, 138, "вершини в метрах", size=11, color=MUTED))
    # напрямок галсів усередині фігури
    c, s = 0.8, 0.6
    gx, gy = A((60, 190))
    p.append(arrow(gx, gy, gx + 110 * c, gy - 110 * s, color=POS, sw=2.2))
    p.append(text(axl + 120, 182, "напрямок галсів 36.9°", size=11, color=POS, bold=True))

    # ── стрілка переходу ──────────────────────────────────────────────────────
    p.append(arrow(348, 300, 420, 300, color=INK, sw=2.2))
    p.append(text(384, 270, "поворот", size=12, color=INK, bold=True))
    p.append(text(384, 288, "на −36.9°", size=12, color=INK, bold=True))

    # ── праворуч: система галсів ──────────────────────────────────────────────
    s2 = 0.72
    bxl, byb = 470.0, 400.0
    gx0, gy0 = 20.0, 0.0

    def B(pt):
        return (bxl + (pt[0] - gx0) * s2, byb - (pt[1] - gy0) * s2)

    p.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>'
             % (poly_str([B(q) for q in DEMO_GALS]), INK))
    p.append(text(bxl + 118, 118, "система галсів: січні — це y = const",
                  size=13, color=INK, bold=True))
    p.append(text(bxl + 118, 138, "уся робота стає одновимірною", size=11, color=MUTED))

    for y in DEMO_LINES:
        xa, ya = B((gx0 - 14, y))
        xb, _ = B((340 + 14, y))
        p.append(line(xa, ya, xb, ya, color=MUTED, sw=1.2, dash="5 5"))
        p.append(text(xb + 8, ya + 4, "y=%d" % y, size=11, color=MUTED, anchor="start"))
        segs = [(20, 340)] if y < 140 else [(20, 120), (240, 340)]
        for x0, x1 in segs:
            p0, p1 = B((x0, y)), B((x1, y))
            p.append(line(p0[0], p0[1], p1[0], p1[1], color=NEG, sw=3.2))
            p.append(circle(p0[0], p0[1], 3.4, fill=POS, stroke=POS, sw=1))
            p.append(circle(p1[0], p1[1], 3.4, fill=POS, stroke=POS, sw=1))

    # ── унизу: розбір січної y = 140 ──────────────────────────────────────────
    ly = 480.0
    s3 = 1.65
    lx0 = 190.0

    def L(x):
        return lx0 + (x - 0.0) * s3

    p.append(text(120, ly + 5, "січна y = 140:", size=13, color=INK,
                  anchor="end", bold=True))
    p.append(line(L(0), ly, L(360), ly, color=MUTED, sw=1.4))
    for i, x in enumerate((20, 120, 240, 340)):
        p.append(line(L(x), ly - 9, L(x), ly + 9, color=INK, sw=2))
        p.append(text(L(x), ly - 16, "x=%d" % x, size=11, color=INK))
    for x0, x1, col, cap in ((20, 120, NEG, "галс"), (120, 240, POS, "діра — пропускаємо"),
                             (240, 340, NEG, "галс")):
        p.append(line(L(x0) + 3, ly + 24, L(x1) - 3, ly + 24, color=col, sw=3))
        p.append(text((L(x0) + L(x1)) / 2, ly + 44, cap, size=11, color=col, bold=True))
    p.append(text(L(180), ly + 74, "перетини йдуть парами: 1↔2 і 3↔4 — усередині, 2↔3 — зовні",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "cut-parity.svg"), W, H, *p,
           title="Поворот системи й розсічення: чотири перетини дають два галси")


def fig_route_order():
    W, H = 960, 470
    p = []
    s = 1.42
    oxl, oyb = 80.0, 400.0
    gx0 = -5.0

    def G(pt):
        return (oxl + (pt[0] - gx0) * s, oyb - pt[1] * s)

    p.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>'
             % (poly_str([G(q) for q in DEMO_GALS]), INK))

    prev_end = None
    legs = []
    for i, (y, x0, x1, cell) in enumerate(DEMO_ORDER):
        col = CELL_COL[cell]
        a, b = x0 - 25.0, x1 + 25.0
        # напрямок: входимо тим кінцем, що ближче до місця, де скінчився попередній
        if prev_end is not None and abs(b - prev_end) < abs(a - prev_end):
            a, b = b, a
        legs.append((a, b, y, cell, col))
        prev_end = b

    # переходи між галсами: сірі — широкі, червоні — вузькі (менше за 2R)
    for i in range(1, len(legs)):
        pa_, pb_, ya, ca, _ = legs[i - 1]
        na, nb, yb_, cb, _ = legs[i]
        q0, q1 = G((pb_, ya)), G((na, yb_))
        same = (ca == cb)
        narrow = same and abs(yb_ - ya) < 2 * 30.0
        p.append(line(q0[0], q0[1], q1[0], q1[1],
                      color=(POS if narrow else MUTED), sw=(2.8 if narrow else 1.6),
                      dash=(None if same else "3 4")))

    for i, (a, b, y, cell, col) in enumerate(legs):
        x0, x1 = min(a, b) + 25.0, max(a, b) - 25.0
        pa, pb = G((a, y)), G((b, y))
        ha, hb = G((x0, y)), G((x1, y))
        p.append(line(ha[0], ha[1], hb[0], hb[1], color=col, sw=3.4))
        p.append(line(pa[0], pa[1], G((x0 if a < b else x1, y))[0], pa[1],
                      color=col, sw=1.6, dash="4 4"))
        p.append(line(G((x1 if a < b else x0, y))[0], pb[1], pb[0], pb[1],
                      color=col, sw=1.6, dash="4 4"))
        mid = (pa[0] + pb[0]) / 2
        step = 14 if a < b else -14
        p.append(arrow(mid - step, pa[1], mid + step, pa[1], color=col, sw=2.2))
        # номер у порядку обходу — з боку входу, за межею хвоста
        nx = pa[0] + (-16 if a < b else 16)
        p.append(circle(nx, pa[1], 10, fill="#ffffff", stroke=col, sw=1.8))
        p.append(text(nx, pa[1] + 4, "%d" % (i + 1), size=11, color=col, bold=True))

    lx, ly = G((180.0, 205.0))
    p.append(text(lx, ly, "40 м", size=12, color=POS, bold=True))
    p.append(line(lx + 4, ly + 6, G((215.0, 200.0))[0] - 3, G((215.0, 200.0))[1],
                  color=POS, sw=1.2, dash="3 3"))
    p.append(text(700, 100, "червоне — вузький перехід:", size=12,
                  color=POS, anchor="start", bold=True))
    p.append(text(700, 120, "зміна пасажу, 40 м замість 60", size=12,
                  color=POS, anchor="start"))
    p.append(text(700, 150, "пунктир — подовжені кінці, 25 м", size=12,
                  color=MUTED, anchor="start"))
    p.append(text(700, 170, "колір — комірка, 1…9 — порядок", size=12,
                  color=MUTED, anchor="start"))

    render(os.path.join(OUT, "route-order.svg"), W, H, *p,
           title="Порядок обходу з пропуском k = 2 і подовжені кінці галсів")


# ── фігури до вставки math-min-width.md ───────────────────────────────────────
# Наскрізний п'ятикутник: означення ширини, крива W(θ) і тест «стопи».
# Координати модельні; на екран лягають з масштабом s і перевернутою віссю y.

PENT = [(0.0, 0.0), (60.0, 0.0), (80.0, 40.0), (30.0, 70.0), (-10.0, 30.0)]
SUBS = ["₀", "₁", "₂", "₃", "₄"]


def _nm(i):
    return "P" + SUBS[i]


def _rot2(q, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (q[0] * c - q[1] * s, q[0] * s + q[1] * c)


def _width(th):
    """W(θ) та індекси опорних вершин (max, min) для п'ятикутника PENT."""
    v = (math.cos(math.radians(th)), math.sin(math.radians(th)))
    ps = [q[0] * v[0] + q[1] * v[1] for q in PENT]
    return max(ps) - min(ps), ps.index(max(ps)), ps.index(min(ps))


def fig_width_caliper():
    """Означення W(v): полотно повернуто так, щоб v дивився вгору."""
    W, H = 860, 566
    p = []
    th = 65.0                                   # довільний, «нетиповий» напрямок
    R = [_rot2(q, 90.0 - th) for q in PENT]      # тепер v — вертикаль екрана
    s, ox, oy = 4.2, 300.0, 420.0
    S = [(ox + s * x, oy - s * y) for x, y in R]
    ytop = min(q[1] for q in S)
    ybot = max(q[1] for q in S)
    itop = min(range(len(S)), key=lambda i: S[i][1])

    p.append('<polygon points="%s" fill="#eaf1fa" stroke="%s" stroke-width="2.2"/>'
             % (poly_str(S), INK))

    d_px = 12.0 * s                              # крок галсів у тих самих одиницях
    segs = scanlines(S, 0.0, d_px)
    for a, b in segs:
        p.append(line(a[0], a[1], b[0], b[1], color=POS, sw=1.7))

    for yy in (ytop, ybot):                      # опорні прямі — «губки»
        p.append(line(120, yy, 700, yy, color=INK, sw=2.2, dash="7 5"))

    p.append(arrow(150, ybot, 150, ytop, color=NEG, sw=2.0))
    p.append(arrow(150, ytop, 150, ybot, color=NEG, sw=2.0))
    p.append(text(192, (ytop + ybot) / 2 + 5, "W(v)", size=16, color=NEG, bold=True))

    p.append(arrow(660, ybot - 26, 660, ybot - 168, color=FIELD, sw=2.6))
    p.append(text(688, ybot - 92, "v", size=17, color=FIELD, bold=True))

    for q in S:
        p.append(circle(q[0], q[1], 4.6, fill="#fff", stroke=INK, sw=1.8))
    p.append(text(300, ytop - 20, _nm(itop) + " — max pᵢ·v", size=14, color=INK, bold=True))
    p.append(text(300, ybot + 30, _nm(0) + " — min pᵢ·v", size=14, color=INK, bold=True))
    p.append(text(S[1][0] + 26, S[1][1] + 6, _nm(1), size=13, color=MUTED))
    p.append(text(S[2][0] + 26, S[2][1] - 4, _nm(2), size=13, color=MUTED))
    p.append(text(S[4][0] - 24, S[4][1] + 6, _nm(4), size=13, color=MUTED))
    p.append(text(598, ytop - 20, "опорні прямі ⊥ v", size=13, color=MUTED, italic=True))

    p.append(text(430, 498, "W(v) = max pᵢ·v − min pᵢ·v", size=16, color=INK, bold=True))
    p.append(text(430, 526, "галси ‖ губок, їх кількість = ⌈W(v)/d⌉ = %d" % len(segs),
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "width-caliper.svg"), W, H, *p,
           title="Ширина в напрямку v — відстань між двома опорними прямими")


def fig_width_curve():
    """W(θ) на [0°,180°): шість дуг косинуса, злами на нормалях сторін."""
    W, H = 900, 584
    p = []
    XL, XR = 105.0, 835.0
    WLO, WHI = 62.0, 94.0
    YB, YT = 470.0, 92.0

    def SX(t):
        return XL + (XR - XL) * t / 180.0

    def SY(w):
        return YB - (w - WLO) * (YB - YT) / (WHI - WLO)

    p.append(line(95, YB, 848, YB, color=INK, sw=1.8))
    p.append(line(XL, YB, XL, 88, color=INK, sw=1.8))
    for t in (0, 30, 60, 90, 120, 150, 180):
        p.append(line(SX(t), YB, SX(t), YB + 6, color=INK, sw=1.4))
        p.append(text(SX(t), YB + 22, "%d°" % t, size=12, color=MUTED))
    for w in (65, 70, 75, 80, 85, 90):
        p.append(line(XL - 6, SY(w), XL, SY(w), color=INK, sw=1.4))
        p.append(text(XL - 14, SY(w) + 4, "%d" % w, size=12, color=MUTED, anchor="end"))

    p.append(line(XL, SY(72), XR, SY(72), color=FIELD, sw=1.8, dash="6 5"))
    p.append(text(252, SY(72) - 16, "W = 6·d = 72", size=13, color=FIELD, bold=True))

    for a, b in ((85.822, 94.178), (132.219, 137.781)):
        p.append(line(SX(a), YB - 9, SX(b), YB - 9, color=FIELD, sw=7))
    p.append(text(262, 420, "тут галсів рівно 6", size=13, color=FIELD, bold=True))
    p.append(arrow(336, 424, 450, 456, color=FIELD, sw=1.6))

    pts = []
    n = 720
    for i in range(n + 1):
        t = 180.0 * i / n
        pts.append((SX(t), SY(_width(t)[0])))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (poly_str(pts), NEG))

    brk = [(18.4349, 88.5438, 4, 0), (59.0362, 75.4594, 2, 3), (90.0, 70.0, 0, 1),
           (135.0, 70.7107, 3, 4), (153.4349, 76.0263, 1, 2)]
    for t, w, a, b in brk:
        x, y = SX(t), SY(w)
        p.append(line(x, y + 7, x, YB, color=MUTED, sw=1.2, dash="4 4"))
        p.append(circle(x, y, 5.2, fill="#fff", stroke=POS, sw=2.4))
        p.append(text(x, 512, _nm(a) + _nm(b), size=13, color=INK, bold=True))
        p.append(text(x, 532, "%.2f" % w, size=12, color=MUTED))
    p.append(text(SX(90.0), 558, "↓ мінімум", size=13, color=POS, bold=True))

    render(os.path.join(OUT, "width-curve.svg"), W, H, *p,
           title="W(θ) п'ятикутника: шість дуг косинуса, злами — на нормалях сторін")


def _kink_panel(rot_deg, edge, apex, ox, oy, s, cap, verdict, vcol):
    """Одна панель: сторона лягла на губку, вершина — навпроти неї."""
    p = []
    R = [_rot2(q, rot_deg) for q in PENT]
    S = [(ox + s * x, oy - s * y) for x, y in R]
    ya = S[edge[0]][1]                        # губка зі стороною
    yb = S[apex][1]                           # губка з вершиною
    xs = [q[0] for q in S]
    x0, x1 = min(xs) - 48, max(xs) + 48
    p.append('<polygon points="%s" fill="#eaf1fa" stroke="%s" stroke-width="2.2"/>'
             % (poly_str(S), INK))
    p.append(line(x0, ya, x1, ya, color=INK, sw=2.2, dash="7 5"))
    p.append(line(x0, yb, x1, yb, color=INK, sw=2.2, dash="7 5"))
    fx = S[apex][0]                           # перпендикуляр із вершини на пряму
    p.append(line(fx, yb, fx, ya + 30, color=MUTED, sw=1.5, dash="4 4"))
    p.append(rect(fx - 5, ya - 5, 10, 10, fill=POS, stroke=POS, sw=1.2, rx=0))
    for i in (edge[0], edge[1], apex):
        p.append(circle(S[i][0], S[i][1], 4.6, fill="#fff", stroke=INK, sw=1.8))
    p.append(text(S[apex][0], yb - 16, _nm(apex), size=13, color=INK, bold=True))
    p.append(text(S[edge[0]][0] - 22, ya + 22, _nm(edge[0]), size=13, color=INK, bold=True))
    p.append(text(S[edge[1]][0] + 22, ya + 22, _nm(edge[1]), size=13, color=INK, bold=True))
    p.append(text((x0 + x1) / 2, 68, cap, size=14, color=INK, bold=True))
    p.append(text((x0 + x1) / 2, 466, verdict, size=13, color=vcol, bold=True))
    return p


def fig_width_kink():
    """Злам — мінімум лише тоді, коли основа перпендикуляра лягла в межі сторони."""
    W, H = 920, 512
    p = []
    p += _kink_panel(0.0, (0, 1), 3, 112.0, 400.0, 2.7,
                     "основа перпендикуляра — ВСЕРЕДИНІ сторони P₀P₁",
                     "W′₋ = −30 < 0 < +30 = W′₊ — мінімум", FIELD)
    p += _kink_panel(-63.4349, (1, 2), 4, 566.0, 255.1, 2.7,
                     "основа перпендикуляра — ПОЗА стороною P₁P₂",
                     "W′₋ = +4.47 і W′₊ = +49.19 — не мінімум", POS)
    render(os.path.join(OUT, "width-kink.svg"), W, H, *p,
           title="Коли злам ширини — справді мінімум")


if __name__ == "__main__":
    fig_swath()
    fig_direction()
    fig_turns()
    fig_cells()
    fig_cut_parity()
    fig_route_order()
    fig_width_caliper()
    fig_width_curve()
    fig_width_kink()
    print("OK: figures written to", OUT)
