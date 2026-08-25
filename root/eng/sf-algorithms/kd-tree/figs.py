# -*- coding: utf-8 -*-
"""Фігури до теми «kd-дерево: поділ площини по черзі за координатами»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def rnd(seed):
    """Детермінований генератор — щоб фігури не мінялися між запусками."""
    x = seed
    while True:
        x = (1103515245 * x + 12345) % (1 << 31)
        yield x / float(1 << 31)


def dot(x, y, r=2.6, color=INK):
    return circle(x, y, r, fill=color, stroke=color, sw=0.6)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def dashcircle(cx, cy, r, color=POS, sw=2.0, dash="6,5"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, color, sw, dash))


# ── 1. Чергування осей: комірка дрібнішає в обидва боки ─────────────────────
def fig_alternate():
    W, H = 990, 590
    X0, Y0, S = 50, 70, 330
    xr = X0 + 0.46 * S                      # розріз кореня, вісь x
    yl = Y0 + 0.55 * S                      # розріз лівої половини, вісь y
    yrt = Y0 + 0.40 * S                     # розріз правої половини, вісь y

    frags = [rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.8, rx=0)]

    g = rnd(31337)
    for _ in range(44):
        frags.append(dot(X0 + 12 + next(g) * (S - 24), Y0 + 12 + next(g) * (S - 24)))

    # рівень 1 — x
    frags.append(line(xr, Y0, xr, Y0 + S, color=NEG, sw=2.6))
    # рівень 2 — y
    frags.append(line(X0, yl, xr, yl, color=FIELD, sw=2.0))
    frags.append(line(xr, yrt, X0 + S, yrt, color=FIELD, sw=2.0))
    # рівень 3 — x
    frags.append(line(X0 + 0.22 * S, Y0, X0 + 0.22 * S, yl, color=NEG, sw=1.2))
    frags.append(line(X0 + 0.28 * S, yl, X0 + 0.28 * S, Y0 + S, color=NEG, sw=1.2))
    frags.append(line(X0 + 0.70 * S, Y0, X0 + 0.70 * S, yrt, color=NEG, sw=1.2))
    frags.append(line(X0 + 0.76 * S, yrt, X0 + 0.76 * S, Y0 + S, color=NEG, sw=1.2))

    frags.append(text(xr, Y0 - 14, "x", size=14, color=NEG, bold=True))
    frags.append(text(X0 - 12, yl + 5, "y", size=14, color=FIELD, bold=True, anchor="end"))
    frags.append(text(X0 + S + 12, yrt + 5, "y", size=14, color=FIELD, bold=True, anchor="start"))

    # ── те саме як дерево
    TX = 705
    frags.append(text(TX, Y0 - 14, "те саме як дерево", size=12, color=MUTED))
    lv = (100, 178, 256)
    frags.append(rect(TX - 21, lv[0], 42, 22, fill=FILL, stroke=NEG, sw=1.8))
    l2 = (615, 795)
    for cx in l2:
        frags.append(line(TX, lv[0] + 22, cx, lv[1], color=MUTED, sw=1.0))
        frags.append(rect(cx - 19, lv[1], 38, 20, fill=FILL, stroke=FIELD, sw=1.7))
    l3 = (570, 660, 750, 840)
    for i, cx in enumerate(l3):
        frags.append(line(l2[i // 2], lv[1] + 20, cx, lv[2], color=MUTED, sw=1.0))
        frags.append(rect(cx - 16, lv[2], 32, 18, fill=FILL, stroke=NEG, sw=1.4))
    leaves = [536, 588, 626, 678, 716, 768, 806, 858]
    for i, cx in enumerate(leaves):
        frags.append(line(l3[i // 2], lv[2] + 18, cx, 326, color=MUTED, sw=0.9))
        frags.append(rect(cx - 13, 326, 26, 15, fill="#e8effb", stroke=MUTED, sw=1.0))

    frags.append(text(470, lv[0] + 15, "ріже x", size=12, color=NEG, anchor="start"))
    frags.append(text(470, lv[1] + 14, "ріже y", size=12, color=FIELD, anchor="start"))
    frags.append(text(470, lv[2] + 13, "ріже x", size=12, color=NEG, anchor="start"))
    frags.append(text(470, 338, "комірки", size=12, color=MUTED, anchor="start"))

    frags.append(tb(180, 480, "Вузол ріже свою комірку однією\nпрямою, перпендикулярною до осі.",
                    size=12, fill=FILL, stroke=LINE))
    frags.append(tb(500, 480, "Після L рівнів на кожну вісь\nприпадає близько L/2 розрізів.",
                    size=12, fill="#e8effb", stroke=NEG))
    frags.append(tb(820, 480, "Сторона комірки — 2^(−L/2)\nпо кожній осі, тож вона квадратна.",
                    size=12, fill="#e6f7ec", stroke=FIELD))

    render(os.path.join(OUT, 'alternate.svg'), W, H, *frags,
           title="Осі чергуються, тому комірка дрібнішає в обидва боки")


# ── 2. Відсікання при пошуку найближчого ────────────────────────────────────
def fig_nn_prune():
    W, H = 950, 530
    X0, Y0, S = 50, 90, 340
    s1 = X0 + 200                  # вертикальний розріз (вісь x)
    s2 = Y0 + 170                  # горизонтальний розріз лівої половини (вісь y)
    s3 = Y0 + 120                  # горизонтальний розріз правої половини
    qx, qy = X0 + 160, Y0 + 240
    px, py = X0 + 130, Y0 + 205
    r = ((qx - px) ** 2 + (qy - py) ** 2) ** 0.5      # = 46.1

    frags = [rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.6, rx=0)]
    frags.append(rect(X0, s2, s1 - X0, Y0 + S - s2, fill="#e6f7ec", stroke="none", sw=0, rx=0))

    g = rnd(20260808)
    for _ in range(30):
        frags.append(dot(X0 + 14 + next(g) * (S - 28), Y0 + 14 + next(g) * (S - 28)))

    frags.append(line(s1, Y0, s1, Y0 + S, color=NEG, sw=2.6))
    frags.append(line(X0, s2, s1, s2, color=FIELD, sw=2.4))
    frags.append(line(s1, s3, X0 + S, s3, color=MUTED, sw=1.4))

    frags.append(dashcircle(qx, qy, r))
    frags.append(dot(qx, qy, r=5.0, color=POS))
    frags.append(dot(px, py, r=4.2, color=INK))
    frags.append(text(qx + 4, qy + 26, "q", size=14, color=POS, bold=True))
    frags.append(text(px - 16, py - 4, "p", size=13, color=INK, bold=True))

    frags.append(text(s1, Y0 - 14, "s₁", size=14, color=NEG, bold=True))
    frags.append(text(X0 - 12, s2 + 5, "s₂", size=14, color=FIELD, bold=True, anchor="end"))
    frags.append(text(X0 + S / 2, Y0 + S + 26, "комірка листка, у який привів спуск",
                      size=12, color=MUTED))

    frags.append(tb(700, 130, "d(q,p)² = Σ (qᵢ − pᵢ)² ≥ (q_a − s)²\nвідстань не менша за різницю\nв одній координаті",
                    size=12, fill=FILL, stroke=LINE))
    frags.append(tb(700, 262, "|q.x − s₁| = 40 < r = 46\nкуля заходить за межу — другу\nполовину доведеться перевірити",
                    size=12, fill="#fdecea", stroke=POS))
    frags.append(tb(700, 394, "|q.y − s₂| = 70 > r = 46\nусе піддерево відкинуто\nодним відніманням",
                    size=12, fill="#e6f7ec", stroke=FIELD))

    render(os.path.join(OUT, 'nn-prune.svg'), W, H, *frags,
           title="Куля радіуса r проти площини розрізу")


# ── 3. Розмірність з'їдає розрізи ───────────────────────────────────────────
def fig_dimension():
    W, H = 970, 530
    AX, AY, A = 60, 120, 260
    BX, BY, B = 390, 120, 260

    frags = []

    # ліва панель — дрібна сітка
    step = A / 8.0
    for i in range(1, 8):
        frags.append(line(AX + i * step, AY, AX + i * step, AY + A, color=MUTED, sw=0.7))
        frags.append(line(AX, AY + i * step, AX + A, AY + i * step, color=MUTED, sw=0.7))
    frags.append(rect(AX, AY, A, A, fill="none", stroke=LINE, sw=1.6, rx=0))
    q1x, q1y = AX + 3.7 * step, AY + 4.5 * step
    frags.append(dashcircle(q1x, q1y, 12.0))
    frags.append(dot(q1x, q1y, r=3.6, color=POS))

    # права панель — один розріз на вісь
    frags.append(line(BX + B / 2, BY, BX + B / 2, BY + B, color=NEG, sw=2.2))
    frags.append(line(BX, BY + B / 2, BX + B, BY + B / 2, color=NEG, sw=2.2))
    frags.append(rect(BX, BY, B, B, fill="none", stroke=LINE, sw=1.6, rx=0))
    q2x, q2y = BX + 0.60 * B, BY + 0.62 * B
    frags.append(dashcircle(q2x, q2y, 92.0))
    frags.append(dot(q2x, q2y, r=3.6, color=POS))

    frags.append(text(AX + A / 2, AY - 26, "d = 2: по 10 розрізів на вісь",
                      size=13, color=INK, bold=True))
    frags.append(text(BX + B / 2, BY - 26, "d = 20: по 1 розрізу на вісь",
                      size=13, color=INK, bold=True))
    frags.append(text(AX + A / 2, AY + A + 26, "куля торкається однієї сусідньої комірки",
                      size=12, color=MUTED))
    frags.append(text(BX + B / 2, BY + B + 26, "куля перетинає кожну площину розрізу",
                      size=12, color=MUTED))

    frags.append(tb(800, 180, "Той самий мільйон точок\nі та сама глибина 20.",
                    size=12, fill=FILL, stroke=LINE))
    frags.append(tb(800, 292, "Розрізи діляться між осями:\nна вісь припадає log₂N / d.",
                    size=12, fill="#e8effb", stroke=NEG))
    frags.append(tb(800, 404, "Щоб кожна вісь дістала m\nрозрізів, треба N ≥ 2^(m·d).",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'dimension.svg'), W, H, *frags,
           title="Що більше вимірів, то менше розрізів дістається кожній осі")


# ── 4. Дві форми kd-дерева: 1975 і 1977 ─────────────────────────────────────
def fig_two_forms():
    W, H = 990, 470
    frags = []

    frags.append(text(255, 46, "1975: багатовимірне дерево пошуку", size=13,
                      color=INK, bold=True))
    frags.append(text(735, 46, "1977: форма, звична підручникам", size=13,
                      color=INK, bold=True))
    frags.append(line(495, 66, 495, 318, color=MUTED, sw=1.0, dash="5,6"))

    # ── ліворуч: запис у кожному вузлі, вісь = рівень mod k
    lv = (100, 175, 250)
    root = (280, lv[0])
    mid = ((190, lv[1]), (370, lv[1]))
    low = ((145, lv[2]), (235, lv[2]), (325, lv[2]), (415, lv[2]))
    for i, m in enumerate(mid):
        frags.append(line(root[0], root[1], m[0], m[1], color=MUTED, sw=1.0))
        for c in low[2 * i:2 * i + 2]:
            frags.append(line(m[0], m[1], c[0], c[1], color=MUTED, sw=1.0))
    names = ("A", "B", "C", "D", "E", "F", "G")
    pts = (root,) + mid + low
    for i, p in enumerate(pts):
        col = NEG if p[1] != lv[1] else FIELD
        frags.append(circle(p[0], p[1], 16, fill=FILL, stroke=col, sw=1.8))
        frags.append(text(p[0], p[1] + 5, names[i], size=12, color=INK, bold=True))
    frags.append(text(48, lv[0] + 5, "рівень 1 → x", size=11, color=NEG, anchor="start"))
    frags.append(text(48, lv[1] + 5, "рівень 2 → y", size=11, color=FIELD, anchor="start"))
    frags.append(text(48, lv[2] + 5, "рівень 3 → x", size=11, color=NEG, anchor="start"))

    # ── праворуч: розріз по медіані, кошики в листках
    rroot = (735, lv[0])
    rmid = ((645, lv[1]), (825, lv[1]))
    rlow = (600, 690, 780, 870)
    for i, m in enumerate(rmid):
        frags.append(line(rroot[0], rroot[1], m[0], m[1], color=MUTED, sw=1.0))
        for cx in rlow[2 * i:2 * i + 2]:
            frags.append(line(m[0], m[1], cx, lv[2], color=MUTED, sw=1.0))
    frags.append(rect(rroot[0] - 42, rroot[1] - 14, 84, 28, fill=FILL, stroke=NEG, sw=1.8))
    frags.append(text(rroot[0], rroot[1] + 5, "x = 42", size=12, color=INK, bold=True))
    for m, s in zip(rmid, ("y = 17", "y = 63")):
        frags.append(rect(m[0] - 38, m[1] - 13, 76, 26, fill=FILL, stroke=FIELD, sw=1.7))
        frags.append(text(m[0], m[1] + 5, s, size=12, color=INK, bold=True))
    g = rnd(7)
    for cx in rlow:
        frags.append(rect(cx - 28, lv[2] - 17, 56, 34, fill="#e8effb", stroke=MUTED, sw=1.2))
        for _ in range(6):
            frags.append(dot(cx - 22 + next(g) * 44, lv[2] - 11 + next(g) * 22, r=2.2))
    frags.append(text(735, lv[2] + 40, "кошики по 8–32 точки", size=11, color=MUTED))

    frags.append(tb(255, 385, "Запис лежить у кожному вузлі,\n"
                              "вісь — це номер рівня за модулем k,\n"
                              "а форму диктує порядок вставки.",
                    size=12, fill=FILL, stroke=LINE))
    frags.append(tb(735, 385, "У вузлі лише розріз по медіані,\n"
                              "вісь беруть за найбільшим розкидом,\n"
                              "точки лежать у листках.",
                    size=12, fill="#e8effb", stroke=NEG))

    render(os.path.join(OUT, 'two-forms.svg'), W, H, *frags,
           title="Дві форми kd-дерева: робота 1975 року і робота 1977 року")


# ── 5. Лема про пряму: через два рівні лишається дві чверті з чотирьох ──────
def fig_stab_recurrence():
    W, H = 980, 560
    X0, Y0, S = 55, 85, 300
    xr = X0 + 0.55 * S                  # розріз кореня за x
    yl = Y0 + 0.52 * S                  # розріз лівої половини за y
    yrt = Y0 + 0.40 * S                 # розріз правої половини за y
    cx = X0 + 0.26 * S                  # сама пряма ℓ

    GREEN, GREY, BLUE = "#e6f7ec", "#efefef", "#e8effb"
    frags = []
    # перетнуті чверті
    frags.append(rect(X0, Y0, xr - X0, yl - Y0, fill=GREEN, stroke="none", sw=0, rx=0))
    frags.append(rect(X0, yl, xr - X0, Y0 + S - yl, fill=GREEN, stroke="none", sw=0, rx=0))
    # незачеплена половина
    frags.append(rect(xr, Y0, X0 + S - xr, S, fill=GREY, stroke="none", sw=0, rx=0))

    frags.append(rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.8, rx=0))
    frags.append(line(xr, Y0, xr, Y0 + S, color=NEG, sw=2.6))
    frags.append(line(X0, yl, xr, yl, color=FIELD, sw=2.2))
    frags.append(line(xr, yrt, X0 + S, yrt, color=FIELD, sw=2.2))
    frags.append(line(cx, Y0 - 20, cx, Y0 + S + 20, color=POS, sw=2.8, dash="7,5"))

    frags.append(text(cx, Y0 - 30, "ℓ : x = c", size=13, color=POS, bold=True))
    frags.append(text(xr, Y0 - 8, "s", size=13, color=NEG, bold=True))
    frags.append(text(X0 + S + 10, yrt + 5, "y", size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(190, (Y0 + yl) / 2 + 5, "n/4", size=13, color=INK, bold=True))
    frags.append(text(190, (yl + Y0 + S) / 2 + 5, "n/4", size=13, color=INK, bold=True))
    frags.append(mtext(287, 288, ["права половина —", "не зачеплена"], size=11, color=MUTED))

    # ── те саме як дерево
    lv = (112, 192, 276)
    root, kids, grand = 680, (590, 790), (545, 640, 745, 840)
    for i, kx in enumerate(kids):
        frags.append(line(root, lv[0] + 13, kx, lv[1] - 13, color=MUTED, sw=1.0))
        for gx in grand[2 * i:2 * i + 2]:
            frags.append(line(kx, lv[1] + 13, gx, lv[2] - 13, color=MUTED, sw=1.0))
    frags.append(tb(root, lv[0], "ріже x", size=12, fill=GREEN, stroke=NEG, sw=2.0))
    frags.append(tb(kids[0], lv[1], "ріже y", size=12, fill=GREEN, stroke=FIELD, sw=2.0))
    frags.append(tb(kids[1], lv[1], "ріже y", size=12, fill=GREY, stroke=MUTED, sw=1.2))
    for i, gx in enumerate(grand):
        col = (GREEN, MUTED) if i < 2 else (GREY, MUTED)
        frags.append(tb(gx, lv[2], "n/4" if i < 2 else "—", size=12,
                        fill=col[0], stroke=col[1], sw=1.2, min_w=52))
    for i, nm in enumerate(("рівень 0", "рівень 1", "рівень 2")):
        frags.append(text(505, lv[i] + 5, nm, size=11, color=MUTED, anchor="end"))
    frags.append(text(680, 330, "зелене — комірку перетинає ℓ", size=11, color=MUTED))

    frags.append(tb(175, 460, "Розріз за x: пряма x = c лежить\n"
                              "строго в одній половині —\n"
                              "друга не зачеплена зовсім.",
                    size=12, fill=BLUE, stroke=NEG))
    frags.append(tb(500, 460, "Розріз за y: обидві половини\n"
                              "мають ту саму ширину по x,\n"
                              "тож пряма ріже обидві.",
                    size=12, fill=GREEN, stroke=FIELD))
    frags.append(tb(825, 460, "Через два рівні лишається 2\n"
                              "комірки по n/4 точок:\n"
                              "Q(n) = 2 + 2·Q(n/4).",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, 'stab-recurrence.svg'), W, H, *frags,
           title="Скільки комірок перетинає одна вертикальна пряма")


# ── 6. Три роди комірок у віконному запиті ──────────────────────────────────
def fig_window_cost():
    W, H = 980, 560
    X0, Y0, S = 55, 85, 336
    c = S / 8.0
    wx0, wx1 = X0 + 1.6 * c, X0 + 5.4 * c
    wy0, wy1 = Y0 + 1.7 * c, Y0 + 5.6 * c

    GREEN, GREY, BLUE = "#e6f7ec", "#f7f7f7", "#e8effb"
    frags = []
    for i in range(8):
        for j in range(8):
            x1, y1 = X0 + i * c, Y0 + j * c
            x2, y2 = x1 + c, y1 + c
            if x1 >= wx0 and x2 <= wx1 and y1 >= wy0 and y2 <= wy1:
                fill = GREEN
            elif x2 <= wx0 or x1 >= wx1 or y2 <= wy0 or y1 >= wy1:
                fill = GREY
            else:
                fill = BLUE
            frags.append(rect(x1, y1, c, c, fill=fill, stroke="#c9ced6", sw=0.8, rx=0))
    frags.append(rect(X0, Y0, S, S, fill="none", stroke=LINE, sw=1.8, rx=0))

    for x in (wx0, wx1):
        frags.append(line(x, Y0 - 12, x, Y0 + S + 12, color=POS, sw=1.2, dash="5,4"))
    for y in (wy0, wy1):
        frags.append(line(X0 - 12, y, X0 + S + 12, y, color=POS, sw=1.2, dash="5,4"))
    frags.append(rect(wx0, wy0, wx1 - wx0, wy1 - wy0, fill="none", stroke=POS, sw=2.8, rx=0))
    frags.append(text((wx0 + wx1) / 2, Y0 - 26, "вікно запиту", size=13, color=POS, bold=True))

    frags.append(tb(690, 140, "Комірка цілком у вікні:\n"
                              "усе піддерево — у відповідь,\n"
                              "разом це рівно k точок.",
                    size=12, fill=GREEN, stroke=FIELD))
    frags.append(tb(690, 245, "Комірка на межі: лише тут\n"
                              "рекурсія триває — і саме\n"
                              "таких комірок O(√N).",
                    size=12, fill=BLUE, stroke=NEG))
    frags.append(tb(690, 350, "Комірка поза вікном:\n"
                              "одне порівняння — і геть\n"
                              "разом з усім піддеревом.",
                    size=12, fill=GREY, stroke=MUTED))

    frags.append(tb(490, 475, "Межа вікна лежить на чотирьох прямих; кожна ріже "
                              "щонайбільше 3·√N − 2 комірок.",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, 'window-cost.svg'), W, H, *frags,
           title="Ціну віконного запиту роблять комірки, крізь які проходить межа")


# ── 7. Розкладка в пам'яті: три масиви й жодної алокації на вузол ───────────
def fig_layout():
    W, H = 1010, 520
    X0, CW, N = 140, 54, 12
    frags = []

    def cellrow(y, h, labels, w, fill, stroke, size):
        out = []
        for i, s in enumerate(labels):
            x = X0 + i * w
            out.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, rx=3))
            out.append(text(x + w / 2.0, y + h / 2.0 + 4, s, size=size, color=INK))
        return out

    # ── pts_ : порядок недоторканий
    frags.append(text(56, 44, "pts_ — точки лежать, як прийшли; побудова їх не рухає",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(100, 78, "pts_", size=12, color=INK, anchor="end", bold=True))
    frags += cellrow(58, 30, ["p%d" % i for i in range(N)], CW, FILL, MUTED, 11)

    # ── idx_ : переставлений, піддерево = суцільний відрізок
    frags.append(text(56, 128,
                      "idx_ — ті самі номери, переставлені nth_element; "
                      "піддерево володіє суцільним відрізком",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(100, 162, "idx_", size=12, color=INK, anchor="end", bold=True))
    perm = ["7", "2", "9", "0", "5", "11", "1", "3", "8", "4", "6", "10"]
    frags += cellrow(142, 30, perm, CW, "#e8effb", NEG, 11)

    # дужки рівня 1
    for (a, b, lab) in ((0, 6, "вузол 1 → [0,6)"), (6, 12, "вузол 4 → [6,12)")):
        xa, xb = X0 + a * CW, X0 + b * CW
        frags.append(line(xa + 3, 186, xb - 3, 186, color=NEG, sw=1.6))
        frags.append(line(xa + 3, 180, xa + 3, 190, color=NEG, sw=1.6))
        frags.append(line(xb - 3, 180, xb - 3, 190, color=NEG, sw=1.6))
        frags.append(text((xa + xb) / 2.0, 205, lab, size=11, color=NEG))

    # дужки рівня 2 — листки
    for (a, b, lab) in ((0, 3, "листок 2"), (3, 6, "листок 3"),
                        (6, 9, "листок 5"), (9, 12, "листок 6")):
        xa, xb = X0 + a * CW, X0 + b * CW
        frags.append(line(xa + 3, 226, xb - 3, 226, color=FIELD, sw=1.6))
        frags.append(line(xa + 3, 220, xa + 3, 230, color=FIELD, sw=1.6))
        frags.append(line(xb - 3, 220, xb - 3, 230, color=FIELD, sw=1.6))
        frags.append(text((xa + xb) / 2.0, 247, lab, size=11, color=FIELD))

    # ── nodes_ : один суцільний масив у порядку обходу згори
    frags.append(text(56, 284,
                      "nodes_ — один суцільний масив; лівий нащадок завжди наступний, "
                      "тож зберігаємо лише правий",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(100, 324, "nodes_", size=12, color=INK, anchor="end", bold=True))
    cells = [("0 · вісь x", "[0,12) →4"), ("1 · вісь y", "[0,6) →3"),
             ("2 · листок", "[0,3)"), ("3 · листок", "[3,6)"),
             ("4 · вісь y", "[6,12) →6"), ("5 · листок", "[6,9)"),
             ("6 · листок", "[9,12)")]
    for i, s in enumerate(cells):
        x = X0 + i * 100
        col = NEG if "вісь" in s[0] else FIELD
        frags.append(rect(x, 300, 100, 46, fill=FILL, stroke=col, sw=1.4, rx=3))
        frags.append(mtext(x + 50, 319, list(s), size=10, color=INK))

    frags.append(tb(250, 445, "Жодної алокації на вузол:\nдва масиви — і все дерево.",
                    size=12, fill=FILL, stroke=LINE))
    frags.append(tb(555, 445, "Піддерево — суцільний відрізок idx_,\n"
                              "тож накрите вікном іде у відповідь гуртом.",
                    size=12, fill="#e8effb", stroke=NEG))
    frags.append(tb(855, 445, "Лівий нащадок — наступна\nкомірка nodes_, тож спуск\n"
                              "у ближчу половину йде вперед.",
                    size=12, fill="#e6f7ec", stroke=FIELD))

    render(os.path.join(OUT, 'layout.svg'), W, H, *frags,
           title="Розкладка kd-дерева в пам'яті: pts_, idx_ і nodes_")


if __name__ == '__main__':
    fig_alternate()
    fig_nn_prune()
    fig_dimension()
    fig_two_forms()
    fig_stab_recurrence()
    fig_window_cost()
    fig_layout()
    print("ok")
