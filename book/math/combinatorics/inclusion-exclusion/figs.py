# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
from math import comb

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── venn3: три круги, у кожній ділянці — скільки разів її враховує сума |A|+|B|+|C|
# Ідея: одинарні ділянки враховано раз, попарні двічі, серцевину тричі — саме це
# й пояснює, чому попарні перетини віднімають, а серцевину повертають.
def fig_venn3():
    W, H = 780, 610
    Ax, Ay = 300, 265
    Bx, By = 480, 265
    Cx, Cy = 390, 415
    R = 135

    def tcircle(cx, cy, color):
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.12" '
                'stroke="%s" stroke-width="2"/>' % (cx, cy, R, color, color))

    p = []
    p.append(tcircle(Ax, Ay, NEG))
    p.append(tcircle(Bx, By, FIELD))
    p.append(tcircle(Cx, Cy, POS))

    # назви множин — поза кругами, щоб не налягали на числа
    p.append(text(196, 150, "A", size=22, bold=True, color=NEG))
    p.append(text(584, 150, "B", size=22, bold=True, color=FIELD))
    p.append(text(390, 588, "C", size=22, bold=True, color=POS))

    # число кратности з білим кружком-підкладкою, щоб читалося поверх тонів
    def num(x, y, s, col):
        return (circle(x, y, 17, fill=BG, stroke=BG, sw=0) +
                text(x, y + 8, s, size=23, bold=True, color=col))

    # одинарні — раз (нейтрально); попарні — двічі, серцевина — тричі (перебір, гаряче)
    p.append(num(215, 220, "1", INK))       # лише A
    p.append(num(565, 220, "1", INK))       # лише B
    p.append(num(390, 490, "1", INK))       # лише C
    p.append(num(390, 205, "2", POS))       # A∩B без C
    p.append(num(288, 360, "2", POS))       # A∩C без B
    p.append(num(492, 360, "2", POS))       # B∩C без A
    p.append(num(390, 312, "3", POS))       # A∩B∩C

    render(os.path.join(OUT, "venn3.svg"), W, H, *p,
           title="Скільки разів сума |A| + |B| + |C| рахує кожну ділянку")


# ── collapse: чергована сума біномів для елемента в m множинах завжди = 1
# Ідея: C(m,1) − C(m,2) + … = 1, бо це переставлена рівність (1−1)^m = 0.
def fig_collapse():
    W, H = 830, 430
    p = []
    p.append(mtext(W / 2, 58,
                   ["Елемент лежить у m множинах. Скільки разів його враховує формула:"],
                   size=14.5, color=MUTED))

    rowy = [118, 190, 262, 334]
    slot0, dslot = 232, 118          # центр першого доданка й крок
    eqx, onex = 686, 748             # позиції «=» та зеленої «1»

    for r, m in enumerate([1, 2, 3, 4]):
        y = rowy[r]
        p.append(rect(36, y - 30, W - 72, 60, fill="#fafbfc", stroke="#eef1f4", sw=1))
        p.append(text(88, y + 6, "m = %d" % m, size=16, bold=True, anchor="middle"))
        for k in range(1, m + 1):
            cx = slot0 + (k - 1) * dslot
            val = comb(m, k)
            if k % 2 == 1:                          # непарний рівень — додаємо (+, червоне)
                p.append(plus(cx - 40, y, r=12))
                col = POS
            else:                                   # парний рівень — віднімаємо (−, синє)
                p.append(minus(cx - 40, y, r=12))
                col = NEG
            box, _, _ = textbox(cx, y, "C(%d,%d)=%d" % (m, k, val),
                                size=13.5, pad=8, stroke=col, color=col)
            p.append(box)
        p.append(text(eqx, y + 7, "=", size=20, bold=True))
        one, _, _ = textbox(onex, y, "1", size=18, bold=True,
                            fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=40)
        p.append(one)

    render(os.path.join(OUT, "collapse.svg"), W, H, *p,
           title="Кожен елемент об'єднання зараховано рівно один раз")


# ── derangement-limit: D(n)/n! швидко осідає на 1/e
# Ідея: чи то 4 капелюхи, чи 4 мільйони — шанс «жоден не свій» той самий, ~37%.
def fig_derangement_limit():
    W, H = 780, 470
    # точні значення D(n)/n!
    Dn = [1, 0, 1, 2, 9, 44, 265, 1854, 14833]     # D(0..8)
    fact = [1, 1, 2, 6, 24, 120, 720, 5040, 40320]
    ns = list(range(1, 9))
    vals = [Dn[n] / fact[n] for n in ns]
    INV_E = 0.3678794

    x0, x1 = 128, 690
    ytop, ybot = 78, 388
    vmax = 0.55

    def X(n): return x0 + (n - 1) / 7 * (x1 - x0)
    def Y(v): return ybot - v / vmax * (ybot - ytop)

    p = []
    # горизонтальні сітки й підписи осі Y
    for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        yy = Y(t)
        p.append(line(x0, yy, x1, yy, color="#eef1f4", sw=1))
        p.append(text(x0 - 16, yy + 4.5, "%.1f" % t, size=12.5, color=MUTED, anchor="end"))

    # осі
    p.append(line(x0, ytop - 8, x0, ybot, color=LINE, sw=1.6))
    p.append(line(x0, ybot, x1 + 10, ybot, color=LINE, sw=1.6))

    # цільова лінія 1/e
    ye = Y(INV_E)
    p.append(line(x0, ye, x1, ye, color=FIELD, sw=2, dash="7,5"))
    p.append(text(x1 + 6, ye + 4.5, "1/e ≈ 0.368", size=13.5, color=FIELD,
                  anchor="start", bold=True))

    # ламана між точками — показує згасання коливань
    pts = [(X(n), Y(v)) for n, v in zip(ns, vals)]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        p.append(line(xa, ya, xb, yb, color="#c7ccd3", sw=1.4))

    # точки й підписи осі X
    for n, v in zip(ns, vals):
        xx, yy = X(n), Y(v)
        p.append(circle(xx, yy, 5.5, fill=NEG, stroke=NEG, sw=1))
        p.append(text(xx, ybot + 22, str(n), size=13, color=MUTED))
    p.append(text((x0 + x1) / 2, ybot + 46, "n — кількість предметів", size=13, color=MUTED))

    # підписи кількох перших точок (осторонь від ламаної)
    p.append(text(X(1) + 16, Y(0.0) - 8, "0", size=13, color=INK))
    p.append(text(X(2), Y(0.5) - 14, "0.5", size=13, color=INK))
    p.append(text(X(3) - 4, Y(1 / 3) + 22, "0.333", size=13, color=INK))
    p.append(text(X(4) + 30, Y(0.375) - 6, "0.375", size=13, color=INK))

    render(os.path.join(OUT, "derangement-limit.svg"), W, H, *p,
           title="Ймовірність безладу D(n)/n! застигає на 1/e")


# ── surjections-count: усі 2³ = 8 роздач трьох листів у дві скриньки; дві з них
# лишають скриньку порожньою → 6 сюр'єкцій. Наочно показує віднімання у
# формулі Surj(3,2) = 8 − 2 = 6.
def fig_surjections_count():
    W, H = 950, 252
    BOX1, BOX2 = "#2457d6", "#e08a1e"
    letters = ["a", "b", "c"]
    funcs = [(1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2),
             (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)]
    csz, gap = 30, 8
    cellw = 3 * csz + 2 * gap
    startx, top, pitch = 42, 100, 112
    p = []

    # легенда: якому кольору відповідає кожна скринька
    def legchip(x, s, col):
        return (rect(x, 52, 20, 20, fill=col, stroke=col, sw=1, rx=5) +
                text(x + 28, 67, s, size=13.5, color=INK, anchor="start"))
    p.append(legchip(320, "скринька 1", BOX1))
    p.append(legchip(500, "скринька 2", BOX2))

    for idx, f in enumerate(funcs):
        x0 = startx + idx * pitch
        empty = len(set(f)) == 1                     # усе в одну скриньку → інша порожня
        fill = "#fdecea" if empty else "#eafaf0"
        stroke = POS if empty else FIELD
        p.append(rect(x0 - 8, top - 12, cellw + 16, csz + 50,
                      fill=fill, stroke=stroke, sw=1.4, rx=8))
        for j, box in enumerate(f):
            xx = x0 + j * (csz + gap)
            col = BOX1 if box == 1 else BOX2
            p.append(rect(xx, top, csz, csz, fill=col, stroke=col, sw=1, rx=6))
            p.append(text(xx + csz / 2, top + csz * 0.68, letters[j],
                          size=17, bold=True, color="#ffffff"))
        p.append(text(x0 + cellw / 2, top + csz + 22,
                      "·".join(str(b) for b in f), size=12.5, color=MUTED))
        if empty:
            p.append(line(x0 - 8, top - 12, x0 + cellw + 8, top + csz + 38, color=POS, sw=2.2))
            p.append(line(x0 + cellw + 8, top - 12, x0 - 8, top + csz + 38, color=POS, sw=2.2))

    p.append(text(W / 2, 228,
                  "усіх роздач 2³ = 8      ·      порожня скринька у 2      ·      сюр'єкцій 6",
                  size=14, color=INK))
    render(os.path.join(OUT, "surjections-count.svg"), W, H, *p,
           title="Вісім роздач трьох листів у дві скриньки — дві з порожньою")


# ── stirling-labeling: сюр'єкція = непідписане розбиття на m частин + роздача
# частин по підписаних скриньках (m! способів). Для n=3, m=2: три розбиття,
# кожне дає 2! = 2 сюр'єкції, разом 6 = 2!·S(3,2), тобто S(3,2) = 3.
def fig_stirling_labeling():
    W, H = 760, 392
    BOX1, BOX2 = "#2457d6", "#e08a1e"
    parts = [(["a", "b"], ["c"]), (["a", "c"], ["b"]), (["b", "c"], ["a"])]
    rowy = [138, 232, 326]
    p = []

    p.append(text(150, 84, "непідписане розбиття", size=13.5, bold=True, color=MUTED))
    p.append(text(500, 84, "підписані сюр'єкції", size=13.5, bold=True, color=MUTED))

    def gblock(cx, cy, ls):
        s = " ".join(ls)
        w = max(40, text_width(s, 14, True) + 18)
        p.append(rect(cx - w / 2, cy - 18, w, 36, fill="#eef1f4", stroke="#c7ccd3", sw=1.4, rx=8))
        p.append(text(cx, cy + 5, s, size=14, bold=True, color=INK))
        return w

    def lbox(xl, cy, num, ls, col):
        s = " ".join(ls)
        w = max(42, text_width(s, 13.5, True) + 16)
        pr = 12
        p.append(circle(xl + pr, cy, pr, fill=col, stroke=col, sw=1))
        p.append(text(xl + pr, cy + 5, str(num), size=14, bold=True, color="#ffffff"))
        rx0 = xl + 2 * pr + 5
        p.append(rect(rx0, cy - 17, w, 34, fill="#f7f9fb", stroke=col, sw=1.4, rx=6))
        p.append(text(rx0 + w / 2, cy + 5, s, size=13.5, bold=True, color=INK))

    for (b1, b2), y in zip(parts, rowy):
        w1 = gblock(110, y, b1)
        gblock(110 + w1 / 2 + 44, y, b2)
        p.append(text(268, y - 14, "× 2!", size=14, bold=True, color=POS))
        p.append(arrow(238, y, 322, y, color=LINE, sw=1.8))
        lbox(356, y - 22, 1, b1, BOX1); lbox(356, y + 22, 2, b2, BOX2)
        lbox(560, y - 22, 1, b2, BOX1); lbox(560, y + 22, 2, b1, BOX2)

    render(os.path.join(OUT, "stirling-labeling.svg"), W, H, *p,
           title="Сюр'єкція = розбиття на частини + роздача по підписаних скриньках")


# ── timeline: народження принципу — дві нитки й прірва між ними
# Ідея: конкретну задачу (гра, безлад) розв'язали на початку XVIII ст., а
# загальний закон виписали аж у середині XIX; ім'я закон дістав від пізніх
# кодифікаторів (да Сілва, Сильвестр), а не від першого користувача (де Муавр).
def fig_timeline():
    W, H = 980, 560
    yax = 322
    x0, x1 = 90, 890

    def X(yr):
        return x0 + (yr - 1700) * (x1 - x0) / 200.0

    p = []

    # легенда: колір = нитка
    leg = [(NEG, "нитка задачі: гра, безлад"),
           (POS, "нитка загального закону"),
           (FIELD, "назва")]
    for (col, lab), lx in zip(leg, [150, 470, 760]):
        p.append(circle(lx, 54, 6, fill=col, stroke=col, sw=1))
        p.append(text(lx + 14, 58, lab, size=13, color=MUTED, anchor="start"))

    # вісь часу зі стрілкою + підписи кінців
    p.append(arrow(70, yax, 912, yax, color=LINE, sw=1.8))
    p.append(text(x0, yax + 24, "1700", size=12.5, color=MUTED))
    p.append(text(x1, yax + 24, "1900", size=12.5, color=MUTED))

    # прірва між де Муавром (1718) і да Сілвою (1854)
    gx1, gx2 = X(1718), X(1854)
    gmid = (gx1 + gx2) / 2
    p.append(arrow(gmid, 360, gx1, 360, color=MUTED, sw=1.4))
    p.append(arrow(gmid, 360, gx2, 360, color=MUTED, sw=1.4))
    gbox, _, _ = textbox(gmid, 386, "≈ 140 років без загального закону",
                         size=12.5, pad=7, fill="#f7f7f8", stroke="#e2e5e9", color=MUTED)
    p.append(gbox)

    # події: (рік, центр-y картки, ім'я, підпис, колір, заливка)
    EV = [
        (1753, 112, "Ейлер", "1753 · наново", NEG, "#eef2fc"),
        (1878, 112, "Вітворт", "1878 · субфакторіал !n", FIELD, "#eafaf0"),
        (1718, 430, "де Муавр", "1718 · перша форма", POS, "#fcecea"),
        (1854, 430, "да Сілва", "1854 · загальний закон", POS, "#fcecea"),
        (1883, 512, "Сильвестр", "1883 · перевідкриття", POS, "#fcecea"),
    ]

    cards = []
    for yr, cy, name, sub, col, tint in EV:
        x = X(yr)
        box, _, h = textbox(x, cy, name + "\n" + sub, size=13, pad=8,
                            fill=tint, stroke=col, color=INK)
        # виноска від осі до краю картки
        if cy < yax:
            p.append(line(x, yax, x, cy + h / 2, color=col, sw=1.4))
        else:
            p.append(line(x, yax, x, cy - h / 2, color=col, sw=1.4))
        p.append(circle(x, yax, 5, fill=col, stroke=BG, sw=1.5))
        cards.append(box)

    # 1708 (Монмор) і 1713 (Н. Бернуллі) — лише 5 років різниці, надто близько для
    # окремих виносок (пряма до дальшої картки неминуче йде крізь ближчу). Тому одна
    # спільна картка, а дві мітки-роки на осі сходяться до неї V-подібними лініями.
    yr1, yr2 = 1708, 1713
    x1e, x2e = X(yr1), X(yr2)
    xmid = (x1e + x2e) / 2
    cy_pair = 112
    pair_box, _, h_pair = textbox(
        xmid, cy_pair, "Монмор\n1708 · гра в 13\nН. Бернуллі\n1713 · незалежно",
        size=13, pad=8, fill="#eef2fc", stroke=NEG, color=INK)
    yjoin = cy_pair + h_pair / 2 + 26
    p.append(line(x1e, yax, xmid, yjoin, color=NEG, sw=1.4))
    p.append(line(x2e, yax, xmid, yjoin, color=NEG, sw=1.4))
    p.append(line(xmid, yjoin, xmid, cy_pair + h_pair / 2, color=NEG, sw=1.4))
    p.append(circle(x1e, yax, 5, fill=NEG, stroke=BG, sw=1.5))
    p.append(circle(x2e, yax, 5, fill=NEG, stroke=BG, sw=1.5))
    cards.append(pair_box)

    p.extend(cards)                                    # картки — поверх виносок

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Півтора століття від гри до загального закону")


# ── sieve-lattice: усі 2³ = 8 підмножин {2,3,5} у [1,1000] як ґратка за рівнями.
# Кожна підмножина — один доданок ⌊1000/добуток⌋ зі знаком за парністю розміру;
# сума 266 — взаємно прості, решта 734 — діляться бодай на одне. Наочно показує
# і перебір УСІХ підмножин (сила), і те, що їх рівно 2ʳ (ціна).
def fig_sieve_lattice():
    W, H = 940, 582
    rows = [
        [("{ }", 1, 1000)],
        [("{2}", 2, 500), ("{3}", 3, 333), ("{5}", 5, 200)],
        [("{2, 3}", 6, 166), ("{2, 5}", 10, 100), ("{3, 5}", 15, 66)],
        [("{2, 3, 5}", 30, 33)],
    ]
    xs3 = [268, 470, 672]
    rowx = [[470], xs3, xs3, [470]]
    rowy = [120, 246, 372, 498]
    levellab = ["0 простих", "1 просте", "2 прості", "3 прості"]

    p = []
    p.append(text(W / 2, 52, "усіх підмножин 2³ = 8 — по одному доданку на кожну",
                  size=13.5, color=MUTED))

    centers = {}
    for r_i, row in enumerate(rows):
        for c_i in range(len(row)):
            centers[(r_i, c_i)] = (rowx[r_i][c_i], rowy[r_i])

    # ребра булевої ґратки підмножин — світлі, позаду вузлів (їх кінці сховає рамка)
    edges = [((0, 0), (1, 0)), ((0, 0), (1, 1)), ((0, 0), (1, 2)),
             ((1, 0), (2, 0)), ((1, 0), (2, 1)),
             ((1, 1), (2, 0)), ((1, 1), (2, 2)),
             ((1, 2), (2, 1)), ((1, 2), (2, 2)),
             ((2, 0), (3, 0)), ((2, 1), (3, 0)), ((2, 2), (3, 0))]
    for a, b in edges:
        xa, ya = centers[a]
        xb, yb = centers[b]
        p.append(line(xa, ya, xb, yb, color="#e6e9ed", sw=1.3))

    # ліві підписи рівнів
    for r_i in range(4):
        p.append(text(78, rowy[r_i] + 5, levellab[r_i], size=13.5,
                      color=MUTED, anchor="middle"))

    # вузли: рамка кольору знаку + бейдж «+»/«−» у куті
    for r_i, row in enumerate(rows):
        plus_level = (r_i % 2 == 0)
        col = POS if plus_level else NEG
        fill = "#fdeeec" if plus_level else "#eef2fd"
        for c_i, (label, prod, term) in enumerate(row):
            cx, cy = centers[(r_i, c_i)]
            lbl = "%s\n⌊1000/%d⌋ = %d" % (label, prod, term)
            box, w, h = textbox(cx, cy, lbl, size=13.5, pad=9,
                                stroke=col, sw=1.6, color=INK, fill=fill)
            p.append(box)
            if plus_level:
                p.append(plus(cx - w / 2, cy - h / 2, r=10))
            else:
                p.append(minus(cx - w / 2, cy - h / 2, r=10))

    p.append(line(150, 540, W - 150, 540, color="#eef1f4", sw=1))
    p.append(text(W / 2, 564,
                  "сума = 266 взаємно прості      ·      1000 − 266 = 734 діляться бодай на одне",
                  size=14, color=INK))

    render(os.path.join(OUT, "sieve-lattice.svg"), W, H, *p,
           title="Решето {2, 3, 5} у [1, 1000]: усі 8 підмножин зі знаком")


if __name__ == "__main__":
    fig_venn3()
    fig_collapse()
    fig_derangement_limit()
    fig_surjections_count()
    fig_stirling_labeling()
    fig_timeline()
    fig_sieve_lattice()
    print("done: venn3, collapse, derangement-limit, surjections-count, stirling-labeling, timeline, sieve-lattice")
