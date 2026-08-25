# -*- coding: utf-8 -*-
"""Фігури до теми «Просторовий індекс: R-дерево і квадродерево»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def rnd(seed):
    """Детермінований лінійний конгруентний генератор — щоб фігури не мінялися між запусками."""
    x = seed
    while True:
        x = (1103515245 * x + 12345) % (1 << 31)
        yield x / float(1 << 31)


def dot(x, y, r=2.7, color=INK):
    return circle(x, y, r, fill=color, stroke=color, sw=0.6)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def polyline(pts, color=POS, sw=2.6):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


# ── 1. Чому порядок за однією координатою не рятує ──────────────────────────
def fig_stripe():
    W, H = 780, 430
    X0, Y0, S = 60, 80, 300
    g = rnd(20240808)
    pts = []
    for _ in range(150):
        px = X0 + 8 + next(g) * (S - 16)
        py = Y0 + 8 + next(g) * (S - 16)
        pts.append((px, py))

    sx1, sx2 = X0 + 130, X0 + 170          # смуга за x
    wy1, wy2 = Y0 + 130, Y0 + 170          # вікно всередині смуги

    frags = [
        # смуга (під точками)
        rect(sx1, Y0, sx2 - sx1, S, fill="#e8effb", stroke=NEG, sw=1.2, rx=0),
        rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.6, rx=0),
    ]
    frags += [dot(px, py) for px, py in pts]
    frags.append(rect(sx1, wy1, sx2 - sx1, wy2 - wy1, fill="#e6f7ec", stroke=FIELD, sw=2.2, rx=0))
    frags += [dot(px, py, color=FIELD) for px, py in pts if sx1 < px < sx2 and wy1 < py < wy2]
    frags.append(text(sx1, Y0 + S + 26, "x₁", size=13, color=NEG))
    frags.append(text(sx2, Y0 + S + 26, "x₂", size=13, color=NEG))

    frags.append(tb(570, 120,
                    "вікно запиту, сторона s\n≈ s²·N точок — це відповідь",
                    size=13, fill="#e6f7ec", stroke=FIELD))
    frags.append(tb(570, 225,
                    "смуга за x, s на всю висоту\n≈ s·N точок — стільки перевіримо",
                    size=13, fill="#e8effb", stroke=NEG))
    frags.append(tb(570, 330,
                    "зайвого — у 1/s разів більше,\nі що менше вікно, то гірше",
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'stripe.svg'), W, H, *frags,
           title="Упорядкування за однією координатою бачить лише один вимір")


# ── 2. Квадродерево: сітка, задана наперед ──────────────────────────────────
def fig_quadtree():
    W, H = 880, 600
    X0, Y0, S = 50, 90, 320
    xm, ym = X0 + S / 2, Y0 + S / 2                 # 210, 250
    nx, ny = X0 + S / 2, Y0 + S / 4                 # верх-праворуч: подальший поділ

    frags = [rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.8, rx=0)]
    # перший поділ
    frags.append(line(xm, Y0, xm, Y0 + S, color=LINE, sw=1.4))
    frags.append(line(X0, ym, X0 + S, ym, color=LINE, sw=1.4))
    # другий поділ (північно-східний квадрант)
    frags.append(line(xm + S / 4, Y0, xm + S / 4, ym, color=MUTED, sw=1.1))
    frags.append(line(xm, Y0 + S / 4, X0 + S, Y0 + S / 4, color=MUTED, sw=1.1))
    # третій поділ (південно-західна комірка того квадранта)
    frags.append(line(xm + S / 8, Y0 + S / 4, xm + S / 8, ym, color=MUTED, sw=0.9))
    frags.append(line(xm, Y0 + 3 * S / 8, xm + S / 4, Y0 + 3 * S / 8, color=MUTED, sw=0.9))

    g = rnd(777)
    frags += [dot(X0 + 10 + next(g) * (S - 20), Y0 + 10 + next(g) * (S - 20), r=2.5)
              for _ in range(26)]
    for _ in range(22):                              # щільне скупчення
        frags.append(dot(xm + 4 + next(g) * 36, Y0 + S / 4 + 4 + next(g) * 36, r=2.5))

    frags.append(polyline([(120, 150), (205, 238), (282, 300), (350, 382)]))

    # те саме як дерево (вузли без написів — форма й так усе каже)
    TX = 645
    frags.append(text(TX, 66, "те саме як дерево", size=12, color=MUTED))
    frags.append(rect(TX - 22, 90, 44, 22, fill=FILL, stroke=LINE, sw=1.4))
    lvl1 = [480, 590, 700, 810]
    for cx in lvl1:
        frags.append(line(TX, 112, cx, 160, color=MUTED, sw=1.0))
        frags.append(rect(cx - 19, 160, 38, 20, fill=FILL, stroke=LINE, sw=1.3))
    lvl2 = [500, 560, 620, 680]
    for cx in lvl2:
        frags.append(line(590, 180, cx, 230, color=MUTED, sw=1.0))
        frags.append(rect(cx - 15, 230, 30, 18, fill=FILL, stroke=LINE, sw=1.2))
    lvl3 = [578, 606, 634, 662]
    for cx in lvl3:
        frags.append(line(620, 248, cx, 292, color=MUTED, sw=1.0))
        frags.append(rect(cx - 11, 292, 22, 16, fill=FILL, stroke=LINE, sw=1.1))

    frags.append(tb(645, 372,
                    "Сітка задана наперед: межі комірок\nне залежать від того, де лежать точки.",
                    size=13, fill="#e8effb", stroke=NEG))
    frags.append(tb(645, 458,
                    "Скупчення тягне поділ углиб — глибина\nйде від густини, а не від кількості.",
                    size=13, fill=FILL, stroke=MUTED))
    frags.append(tb(645, 544,
                    "Ламана перетинає центр: жодна дрібна\nкомірка не вміщає її цілком.",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'quadtree.svg'), W, H, *frags,
           title="Квадродерево ділить простір, а не дані")


# ── 3. R-дерево: коробки, підігнані під дані ────────────────────────────────
def fig_rtree():
    W, H = 900, 500
    X0, Y0, S = 50, 80, 340

    leaves = [(70, 100, 110, 90), (150, 150, 110, 100),
              (215, 230, 120, 95), (80, 290, 115, 100)]
    inner = [(70, 100, 190, 150), (80, 230, 255, 160)]

    frags = [rect(X0, Y0, S, S, fill="none", stroke=MUTED, sw=1.4, rx=0)]
    g = rnd(4242)
    for (bx, by, bw, bh) in inner:
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" '
                     'stroke="%s" stroke-width="2.2" stroke-dasharray="7,5"/>' % (bx, by, bw, bh, NEG))
    for (bx, by, bw, bh) in leaves:
        frags.append(rect(bx, by, bw, bh, fill="none", stroke=LINE, sw=1.5, rx=3))
        for _ in range(9):
            frags.append(dot(bx + 12 + next(g) * (bw - 24), by + 12 + next(g) * (bh - 24), r=2.6))

    frags.append(text(100, 118, "R1", size=13, color=LINE))
    frags.append(text(240, 168, "R2", size=13, color=LINE))
    frags.append(text(310, 248, "R3", size=13, color=LINE))
    frags.append(text(110, 308, "R4", size=13, color=LINE))
    frags.append(text(230, 128, "A", size=15, color=NEG, bold=True))
    frags.append(text(252, 372, "B", size=15, color=NEG, bold=True))

    frags.append(dot(170, 240, r=5.5, color=POS))
    frags.append(line(170, 246, 170, 430, color=POS, sw=1.0, dash="4,4"))
    frags.append(text(170, 448, "точка запиту", size=13, color=POS))

    # дерево
    frags.append(rect(645 - 24, 96, 48, 24, fill=FILL, stroke=LINE, sw=1.4))
    frags.append(text(645, 113, "корінь", size=12, color=INK))
    for cx, name, col in ((545, "A", NEG), (775, "B", NEG)):
        frags.append(rect(cx - 18, 176, 36, 22, fill=FILL, stroke=col, sw=1.6))
        frags.append(text(cx, 192, name, size=13, color=col, bold=True))
    for cx, name in ((470, "R1"), (620, "R2"), (700, "R3"), (850, "R4")):
        frags.append(rect(cx - 20, 258, 40, 22, fill=FILL, stroke=LINE, sw=1.3))
        frags.append(text(cx, 274, name, size=12, color=INK))
    frags.append(line(645, 120, 545, 176, color=POS, sw=2.2))
    frags.append(line(645, 120, 775, 176, color=POS, sw=2.2))
    frags.append(line(545, 198, 470, 258, color=MUTED, sw=1.1))
    frags.append(line(545, 198, 620, 258, color=POS, sw=2.2))
    frags.append(line(775, 198, 700, 258, color=MUTED, sw=1.1))
    frags.append(line(775, 198, 850, 258, color=MUTED, sw=1.1))
    frags.append(text(848, 152, "марний спуск", size=12, color=MUTED))

    frags.append(tb(660, 350,
                    "Точка лежить одразу в A і в B —\nпошук роздвоюється вже в корені.",
                    size=13, fill="#fdecea", stroke=POS))
    frags.append(tb(660, 436,
                    "У B нічого немає: обидві його комірки\nмимо. Спуск оплачено даремно.",
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'rtree.svg'), W, H, *frags,
           title="R-дерево: коробки підігнані під дані — і тому перекриваються")


# ── 4. Розщеплення переповненого листка: квадратичне проти «за порядком» ────
def fig_split():
    W, H = 830, 480
    UX, UY = 70.0, 60.0                      # пікселів на одиницю світу
    X0 = 62

    # прямокутники набору: (ім'я, x1, y1, x2, y2)
    BOXES = [("A", 0, 0, 1, 1), ("B", 1, 0, 2, 1), ("C", 0, 1, 1, 2),
             ("D", 1, 1, 2, 2), ("E", 8, 0, 9, 1)]

    def dashrect(x, y, w, h, color, sw=2.0):
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
                'fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-dasharray="7 5"/>' % (x, y, w, h, color, sw))

    def panel(top, groups, members, header, summary):
        """top — екранний y для v=2; groups: [(x1,y1,x2,y2, колір, підпис, lx, ly)]"""
        def X(u):
            return X0 + u * UX

        def Y(v):
            return top + (2 - v) * UY

        out = [text(X0, top - 22, header, size=14, anchor="start", bold=True)]
        for gx1, gy1, gx2, gy2, col, lab, lx, ly in groups:
            out.append(dashrect(X(gx1) - 4, Y(gy2) - 4, (gx2 - gx1) * UX + 8,
                                (gy2 - gy1) * UY + 8, col))
            out.append(text(X(lx), Y(ly) + 5, lab, size=13, color=col, bold=True))
        for name, x1, y1, x2, y2 in BOXES:
            col = members[name]
            out.append(rect(X(x1) + 7, Y(y2) + 7, (x2 - x1) * UX - 14,
                            (y2 - y1) * UY - 14, fill=FILL, stroke=col, sw=1.6, rx=3))
            out.append(text((X(x1) + X(x2)) / 2, (Y(y1) + Y(y2)) / 2 + 5,
                            name, size=14, color=col, bold=True))
        out.append(text(X0, Y(0) + 34, summary, size=13, anchor="start", color=INK))
        return out

    frags = []
    # верхня панель — квадратичне розщеплення
    frags += panel(
        88,
        [(0, 0, 2, 2, NEG, "G₁", -0.45, 1.0),
         (1, 0, 9, 1, POS, "G₂", 5.0, 0.5)],
        {"A": NEG, "C": NEG, "D": NEG, "B": POS, "E": POS},
        "Квадратичне розщеплення: зерна C і E (d = 16), далі D, A → G₁, B віддано G₂ через m",
        "площі 4 + 8 = 12 · перетин G₁ ∩ G₂ = 1")
    # нижня панель — розкладка за порядком вставки
    frags += panel(
        300,
        [(0, 0, 2, 2, NEG, "H₁", -0.45, 1.0),
         (1, 0, 9, 2, POS, "H₂", 5.0, 1.0)],
        {"A": NEG, "B": NEG, "C": NEG, "D": POS, "E": POS},
        "Розкладка за порядком вставки: перші три в один вузол, решта — у другий",
        "площі 4 + 16 = 20 · перетин H₁ ∩ H₂ = 2")

    render(os.path.join(OUT, 'split.svg'), W, H, *frags,
           title="Ті самі п'ять записів, дві розкладки на два вузли")


# ── Дві родоводні лінії просторового індексу (до вставки hist-) ─────────────
def fig_lineages():
    W, H = 1010, 510
    X0, PPY = 150, 28          # x року 1966 і пікселів на рік

    def xy(year):
        return X0 + (year - 1966) * PPY

    lanes = [
        (140, NEG, "Сітка ділить простір: правило поділу придумане наперед",
         [(1966, +1, "Morton, IBM Canada:\nчерез-бітова адреса\nклітинки"),
          (1971, -1, "Klinger:\nрегулярна декомпозиція\nкартинки"),
          (1974, +1, "Finkel і Bentley:\nназва «quad tree»"),
          (1984, -1, "Samet:\nоглядова стаття\nу Computing Surveys")]),
        (380, POS, "Дані ділять себе: коробки підігнані під об'єкти",
         [(1972, +1, "Bayer і McCreight:\nB-дерево, вузол = сторінка"),
          (1982, +1, "Guttman і Stonebraker:\nдані САПР в INGRES"),
          (1984, -1, "Guttman:\nR-дерево, SIGMOD"),
          (1987, +1, "R⁺-дерево:\nбез перекриття"),
          (1990, -1, "R*-дерево:\nпереставляння\nпри поділі"),
          (1994, +1, "Hilbert R-tree")]),
    ]

    frags = []
    for lane_y, color, caption, nodes in lanes:
        frags.append(line(130, lane_y, 965, lane_y, color=MUTED, sw=1.4))
        frags.append(text(20, lane_y - 112, caption, size=14,
                          color=color, anchor="start", bold=True))
        for year, side, label in nodes:
            nx = xy(year)
            frags.append(dot(nx, lane_y, r=4.5, color=color))
            frags.append(line(nx, lane_y + side * 12, nx, lane_y + side * 32,
                              color=MUTED, sw=1.1))
            frags.append(tb(nx, lane_y + side * 68, "%d\n%s" % (year, label),
                            size=12, fill=FILL, stroke=color))

    render(os.path.join(OUT, 'lineages.svg'), W, H, *frags,
           title="Дві незалежні лінії, що зійшлися на просторовому запиті")


# ── Роздута коробка: чотири доданки формули вартості ────────────────────────
def fig_minkowski():
    W, H = 880, 420
    X0, Y0 = 110, 95          # лівий верхній кут рамки допустимих положень
    QW, QH = 75, 60           # розміри вікна запиту
    RW, RH = 215, 165         # розміри коробки

    frags = []
    frags.append(rect(X0, Y0 + RH, QW, QH, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    frags.append(rect(X0, Y0, QW, RH, fill="#e8effb", stroke=NEG, sw=1.2, rx=0))
    frags.append(rect(X0 + QW, Y0 + RH, RW, QH, fill="#e8effb", stroke=NEG, sw=1.2, rx=0))
    frags.append(rect(X0 + QW, Y0, RW, RH, fill="#e6f7ec", stroke=FIELD, sw=2.2, rx=0))
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" fill="none" '
                 'stroke="%s" stroke-width="2.4" stroke-dasharray="7,5"/>'
                 % (X0, Y0, QW + RW, RH + QH, NEG))

    # зразок вікна запиту — осторонь, щоб нічого не перекривати
    frags.append(rect(X0, 20, 55, 44, fill="none", stroke=POS, sw=2.0, rx=0))
    frags.append(dot(X0, 64, r=3.4, color=POS))
    frags.append(text(X0 + 70, 48, "вікно запиту qw × qh", size=13, color=POS, anchor="start"))

    frags.append(text(X0 + QW + RW / 2, Y0 + RH / 2 - 8, "коробка R:  w × h",
                      size=14, color=INK, bold=True))
    frags.append(text(X0 + QW + RW / 2, Y0 + RH / 2 + 18, "w·h", size=15, color=FIELD, bold=True))
    frags.append(text(X0 + QW / 2, Y0 + RH / 2, "h·qw", size=13, color=NEG))
    frags.append(text(X0 + QW + RW / 2, Y0 + RH + QH / 2, "w·qh", size=13, color=NEG))
    frags.append(text(X0 + QW / 2, Y0 + RH + QH / 2, "qw·qh", size=12, color=POS))

    frags.append(text(X0 + QW / 2, Y0 - 9, "qw", size=12, color=NEG))
    frags.append(text(X0 + QW + RW / 2, Y0 - 9, "w", size=12, color=MUTED))
    frags.append(text(X0 - 12, Y0 + RH + QH / 2 + 4, "qh", size=12, color=NEG, anchor="end"))
    frags.append(text(X0 + QW + RW + 14, Y0 + RH / 2 + 4, "h", size=12, color=MUTED, anchor="start"))

    frags.append(text(255, 356, "рамка — усі положення кута вікна, за яких воно зачіпає R",
                      size=13, color=MUTED))
    frags.append(text(255, 380, "її площа = (w + qw)(h + qh)", size=13, color=MUTED))

    frags.append(tb(660, 120, "(w + qw)(h + qh) =\nw·h + h·qw + w·qh + qw·qh",
                    size=13, fill=FILL, stroke=LINE))
    frags.append(tb(660, 210, "w·h — площа коробки: єдине, що\nлишається при точковому запиті",
                    size=13, fill="#e6f7ec", stroke=FIELD))
    frags.append(tb(660, 292, "h·qw + w·qh — за квадратного вікна\nце q·(w + h), тобто півпериметр",
                    size=13, fill="#e8effb", stroke=NEG))
    frags.append(tb(660, 374, "qw·qh — площа вікна: від коробки\nне залежить узагалі",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'minkowski.svg'), W, H, *frags,
           title="Чотири доданки формули — чотири шматки роздутої коробки")


# ── Комірки сітки, які перетинає вікно ──────────────────────────────────────
def fig_grid_cells():
    W, H = 880, 410
    GX, GY, g = 70, 90, 34
    NC, NR = 8, 7
    qx1, qy1 = GX + 1.4 * g, GY + 1.3 * g
    qx2, qy2 = qx1 + 5.2 * g, qy1 + 4.4 * g

    frags = []
    for c in range(NC):
        for r in range(NR):
            x, y = GX + c * g, GY + r * g
            inside = (x >= qx1 - 0.01 and x + g <= qx2 + 0.01
                      and y >= qy1 - 0.01 and y + g <= qy2 + 0.01)
            touched = (x < qx2 and x + g > qx1 and y < qy2 and y + g > qy1)
            fl = "#e6f7ec" if inside else ("#fdecea" if touched else "#ffffff")
            frags.append(rect(x, y, g, g, fill=fl, stroke=MUTED, sw=0.8, rx=0))

    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" fill="none" '
                 'stroke="%s" stroke-width="2.6"/>' % (qx1, qy1, qx2 - qx1, qy2 - qy1, NEG))

    frags.append(text(GX + g / 2, GY - 12, "g", size=12, color=MUTED))
    frags.append(text(206, 356, "у цьому положенні: 6 × 5 = 30 комірок, з них 12 усередині",
                      size=13, color=MUTED))
    frags.append(text(206, 380, "усереднено за положеннями: 6.2 · 5.4 ≈ 33.5",
                      size=13, color=MUTED))

    frags.append(tb(690, 120, "E[комірок] = (qw/g + 1)·(qh/g + 1)", size=13,
                    fill=FILL, stroke=LINE))
    frags.append(tb(690, 200, "нутро: qw·qh/g² — комірки, які\nвікно накрило цілком",
                    size=13, fill="#e6f7ec", stroke=FIELD))
    frags.append(tb(690, 282, "облямівка: (qw + qh)/g — півпериметр\nвікна, поділений на крок сітки",
                    size=13, fill="#fdecea", stroke=POS))
    frags.append(tb(690, 364, "відношення облямівки до нутра —\n2g/q: дрібнити сітку без міри марно",
                    size=13, fill="#e8effb", stroke=NEG))

    render(os.path.join(OUT, 'grid-cells.svg'), W, H, *frags,
           title="Комірки сітки, які перетинає вікно: нутро й облямівка")


if __name__ == '__main__':
    fig_stripe()
    fig_quadtree()
    fig_rtree()
    fig_split()
    fig_lineages()
    fig_minkowski()
    fig_grid_cells()
    print("ok")
