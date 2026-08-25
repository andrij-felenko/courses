# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── prefix: префіксний код — коди сидять на листках, жоден не префікс іншого ───
# Ідея: бінарне дерево; ліворуч 0, праворуч 1; символи — лише на листках, тому
# дорога до одного символу ніколи не проходить крізь інший → самороздільність.

def _node(cx, cy, r, label, leaf, p):
    fill = "#f3c6bf" if leaf else "#eaf2fb"
    stroke = POS if leaf else INK
    p.append(circle(cx, cy, r, fill=fill, stroke=stroke, sw=1.8))
    p.append(text(cx, cy + 5, label, size=13, color=INK, bold=True))


def _edge(x1, y1, x2, y2, bit, p):
    p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.5))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    col = NEG if bit == "0" else POS
    p.append(text(mx + (-10 if bit == "0" else 10), my - 2, bit, size=13, color=col, bold=True))


def fig_prefix():
    W, H = 640, 360
    p = []
    r = 16
    # координати вузлів дерева ABRACADABRA: A=0, R=10, B=110, C=1110, D=1111
    root = (320, 60)
    nA = (180, 140)             # лист A (ліворуч від кореня = 0)
    n1 = (430, 140)             # внутрішній (праворуч = 1)
    nR = (330, 215)             # лист R (10)
    n11 = (520, 215)            # внутрішній (11)
    nB = (430, 290)             # лист B (110)
    n111 = (600, 290)           # внутрішній (111) — впритул до краю, лишимо як вузол
    # щоб не вилазити за полотно, гілку 111 опустимо нижче й трохи лівіше
    n111 = (560, 290)
    nC = (510, 340)             # лист C (1110)
    nD = (610, 340)             # лист D (1111)

    # ребра
    _edge(root[0], root[1] + r, nA[0], nA[1] - r, "0", p)
    _edge(root[0], root[1] + r, n1[0], n1[1] - r, "1", p)
    _edge(n1[0], n1[1] + r, nR[0], nR[1] - r, "0", p)
    _edge(n1[0], n1[1] + r, n11[0], n11[1] - r, "1", p)
    _edge(n11[0], n11[1] + r, nB[0], nB[1] - r, "0", p)
    _edge(n11[0], n11[1] + r, n111[0], n111[1] - r, "1", p)
    _edge(n111[0], n111[1] + r, nC[0], nC[1] - r, "0", p)
    _edge(n111[0], n111[1] + r, nD[0], nD[1] - r, "1", p)

    # вузли
    _node(root[0], root[1], r, "", False, p)
    _node(n1[0], n1[1], r, "", False, p)
    _node(n11[0], n11[1], r, "", False, p)
    _node(n111[0], n111[1], r, "", False, p)
    _node(nA[0], nA[1], r, "A", True, p)
    _node(nR[0], nR[1], r, "R", True, p)
    _node(nB[0], nB[1], r, "B", True, p)
    _node(nC[0], nC[1], r, "C", True, p)
    _node(nD[0], nD[1], r, "D", True, p)

    # підписи-коди біля листків
    p.append(text(nA[0] - 26, nA[1] + 5, "0", size=12, color=INK, anchor="end"))
    p.append(text(nR[0] - 24, nR[1] + 5, "10", size=12, color=INK, anchor="end"))
    p.append(text(nB[0] - 24, nB[1] + 5, "110", size=12, color=INK, anchor="end"))
    p.append(text(nC[0], nC[1] + 26, "1110", size=12, color=INK))
    p.append(text(nD[0], nD[1] + 26, "1111", size=12, color=INK))

    # легенда
    p.append(text(70, 320, "лист = символ", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(70, 338, "0 — ліворуч,  1 — праворуч", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "prefix.svg"), W, H, *p,
           title="Префіксний код: символи лише на листках")


# ── build: жадібна побудова — щоразу зливаємо два найрідші вузли ───────────────
# Ідея: чотири знімки купи частот для ABRACADABRA; на кожному кроці два
# найменші вузли зливаються в новий, сума підіймається.

def fig_build():
    W, H = 700, 360
    p = []
    col_x = [70, 250, 430, 610]
    titles = ["крок 1", "крок 2", "крок 3", "корінь"]
    # на кожному кроці — список (мітка, вага, виділено?)
    steps = [
        [("C", 1, True), ("D", 1, True), ("B", 2, False), ("R", 2, False), ("A", 5, False)],
        [("CD", 2, True), ("B", 2, True), ("R", 2, False), ("A", 5, False)],
        [("BCD", 4, True), ("R", 2, True), ("A", 5, False)],
        [("RBCD", 6, True), ("A", 5, True)],
    ]
    for ci, (cx, ttl, items) in enumerate(zip(col_x, titles, steps)):
        p.append(text(cx, 56, ttl, size=12, color=INK, bold=True))
        y = 84
        for (lab, w, hot) in items:
            fill = "#f3c6bf" if hot else "#eaf2fb"
            stroke = POS if hot else INK
            box, bw, bh = textbox(cx, y, "%s:%d" % (lab, w), size=12, bold=True,
                                  fill=fill, stroke=stroke, sw=1.6, color=INK, min_w=70)
            p.append(box)
            y += 44
        # стрілка до наступного стовпця
        if ci < 3:
            ax = cx + 50
            p.append(arrow(ax, 150, ax + 50, 150, color=MUTED, sw=1.8))

    p.append(text(W / 2, H - 18, "щоразу зливаємо два найрідші вузли в один; сума підіймається вгору",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "build.svg"), W, H, *p,
           title="Жадібна побудова: два найрідші — в один вузол")


# ── tree: підсумкове дерево з вагами й готовими кодами ────────────────────────
# Ідея: те саме дерево, але з вагами у вузлах і таблицею кодів збоку — щоб
# видно було, як частому A дістався 1 біт, а рідкісним C,D — 4.

def fig_tree():
    W, H = 700, 380
    p = []
    r = 20
    root = (300, 64)
    nA = (170, 150)
    n6 = (430, 150)
    nR = (320, 236)
    n4 = (540, 236)
    nB = (430, 318)
    n2 = (650, 318)            # вузол CD — впритул; опустимо нижче
    n2 = (600, 318)
    # внутрішні ваги
    def _wnode(cx, cy, w, p):
        p.append(circle(cx, cy, r, fill="#eaf2fb", stroke=INK, sw=1.8))
        p.append(text(cx, cy + 5, str(w), size=13, color=INK, bold=True))
    def _leaf(cx, cy, lab, w, p):
        p.append(circle(cx, cy, r, fill="#f3c6bf", stroke=POS, sw=1.8))
        p.append(text(cx, cy + 5, "%s·%d" % (lab, w), size=12, color=INK, bold=True))

    _edge(root[0], root[1] + r, nA[0], nA[1] - r, "0", p)
    _edge(root[0], root[1] + r, n6[0], n6[1] - r, "1", p)
    _edge(n6[0], n6[1] + r, nR[0], nR[1] - r, "0", p)
    _edge(n6[0], n6[1] + r, n4[0], n4[1] - r, "1", p)
    _edge(n4[0], n4[1] + r, nB[0], nB[1] - r, "0", p)
    _edge(n4[0], n4[1] + r, n2[0], n2[1] - r, "1", p)
    # листки C,D під вузлом CD
    nC = (560, 360)
    nD = (640, 360)
    _edge(n2[0], n2[1] + r, nC[0], nC[1] - r, "0", p)
    _edge(n2[0], n2[1] + r, nD[0], nD[1] - r, "1", p)

    _wnode(root[0], root[1], 11, p)
    _wnode(n6[0], n6[1], 6, p)
    _wnode(n4[0], n4[1], 4, p)
    _wnode(n2[0], n2[1], 2, p)
    _leaf(nA[0], nA[1], "A", 5, p)
    _leaf(nR[0], nR[1], "R", 2, p)
    _leaf(nB[0], nB[1], "B", 2, p)
    # C,D маленькі листки
    p.append(circle(nC[0], nC[1], r - 4, fill="#f3c6bf", stroke=POS, sw=1.8))
    p.append(text(nC[0], nC[1] + 5, "C·1", size=11, color=INK, bold=True))
    p.append(circle(nD[0], nD[1], r - 4, fill="#f3c6bf", stroke=POS, sw=1.8))
    p.append(text(nD[0], nD[1] + 5, "D·1", size=11, color=INK, bold=True))

    # таблиця кодів збоку
    rows = ["A = 0", "R = 10", "B = 110", "C = 1110", "D = 1111"]
    bx, by = 40, 120
    p.append(text(bx, by - 12, "коди:", size=12, color=INK, bold=True, anchor="start"))
    for i, rtext in enumerate(rows):
        p.append(text(bx, by + 16 + i * 22, rtext, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "tree.svg"), W, H, *p,
           title="Дерево Гаффмана для ABRACADABRA")


# ── vs-entropy: фіксована довжина vs Гаффман vs ентропія ──────────────────────
# Ідея: три стовпчики «бітів на символ» — наївні 3, Гаффман 2.09, ентропія 2.04;
# показати, що Гаффман затиснутий між H і H+1 і сидить майже на дні.

def fig_vs_entropy():
    W, H = 640, 330
    p = []
    ox, oy = 90, 270
    aw, ah = 470, 210
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 14, oy - ah - 2, "біт/символ", size=11, color=INK, bold=True, anchor="end"))

    # масштаб: 0..4 біта → ah
    scale = ah / 4.0
    bars = [("фіксована\n3 біти", 3.0, "#cfe0f5", NEG),
            ("Гаффман\nL≈2.09", 2.09, "#f3c6bf", POS),
            ("ентропія H\n≈2.04", 2.04, "#d7f0de", FIELD)]
    slot = aw / (len(bars) + 0.6)
    bw = slot * 0.5
    for i, (lab, val, fill, stroke) in enumerate(bars):
        bx = ox + 40 + i * slot
        bh = val * scale
        p.append(rect(bx, oy - bh, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=3))
        p.append(text(bx + bw / 2, oy - bh - 8, "%.2f" % val if val != 3.0 else "3.00",
                      size=11, color=stroke, bold=True))
        p.append(mtext(bx + bw / 2, oy + 16, lab, size=10, color=INK))

    # лінія дна H та межі H+1
    yH = oy - 2.04 * scale
    yH1 = oy - 3.04 * scale
    p.append(line(ox, yH, ox + aw, yH, color=FIELD, sw=1.3, dash="5,4"))
    p.append(text(ox + aw, yH - 5, "дно: H", size=10, color=FIELD, anchor="end"))
    p.append(line(ox, yH1, ox + aw, yH1, color=MUTED, sw=1.1, dash="3,4"))
    p.append(text(ox + aw, yH1 - 5, "стеля: H+1", size=10, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "vs-entropy.svg"), W, H, *p,
           title="Гаффман затиснутий між H і H+1")


# ── exchange: доказ оптимальності — два найрідші мусять бути найглибшими ───────
# Ідея: якщо рідкісний символ x сидить вище, ніж якийсь частіший y глибоко внизу,
# поміняй їх місцями — середній код стане коротший. Отже, найрідші — найглибші.

def fig_exchange():
    W, H = 680, 320
    p = []
    r = 16

    def tree(ox, title, deepA, deepB, midX, p, swapped):
        p.append(text(ox + 130, 56, title, size=12, color=INK, bold=True))
        root = (ox + 130, 84)
        L = (ox + 70, 150)
        R = (ox + 190, 150)
        LL = (ox + 40, 216)
        LR = (ox + 110, 216)
        # ребра
        for (a, b) in [(root, L), (root, R), (L, LL), (L, LR)]:
            p.append(line(a[0], a[1] + r, b[0], b[1] - r, color=MUTED, sw=1.4))
        # внутрішні
        for c in (root, L):
            p.append(circle(c[0], c[1], r, fill="#eaf2fb", stroke=INK, sw=1.6))
        # листки
        leaves = [(R, midX), (LL, deepA), (LR, deepB)]
        for (c, lab) in leaves:
            hot = lab in ("x", "y")
            p.append(circle(c[0], c[1], r, fill="#f3c6bf" if hot else "#cfe0f5",
                            stroke=POS if hot else NEG, sw=1.8))
            p.append(text(c[0], c[1] + 5, lab, size=13, color=INK, bold=True))

    # ліворуч: погане розташування (рідкісний x — неглибоко, частий y — глибоко)
    tree(20, "погано: рідкісний x вище", "y", "•", "x", p, False)
    p.append(text(150, 250, "p(x) мале, p(y) велике", size=10, color=MUTED))
    # стрілка «поміняй»
    p.append(arrow(348, 150, 392, 150, color=FIELD, sw=2.2))
    p.append(text(370, 138, "обмін", size=11, color=FIELD, bold=True))
    # праворуч: після обміну (частий y — вгору, рідкісний x — углиб)
    tree(360, "краще: частий y вгору", "x", "•", "y", p, True)
    p.append(text(490, 250, "середній код коротший", size=10, color=FIELD))

    render(os.path.join(OUT, "exchange.svg"), W, H, *p,
           title="Чому два найрідші — найглибші брати (обмінний доказ)")


# ── canonical: канонічний код з самих довжин ──────────────────────────────────
# Ідея: маючи лише довжини кодів, обидві сторони роздають коди послідовними
# числами (сорт за довжиною, потім за символом), доростаючи нулями.

def fig_canonical():
    W, H = 660, 320
    p = []
    # приклад: довжини A=1,R=2,B=3,C=4,D=4 → канонічні коди
    rows = [
        ("A", 1, "0"),
        ("R", 2, "10"),
        ("B", 3, "110"),
        ("C", 4, "1110"),
        ("D", 4, "1111"),
    ]
    x0, y0 = 90, 90
    colw = [110, 130, 200]
    heads = ["символ", "довжина", "канонічний код"]
    for j, hd in enumerate(heads):
        p.append(text(x0 + sum(colw[:j]) + colw[j] / 2, y0, hd, size=12, color=INK, bold=True))
    for i, (sym, ln, code) in enumerate(rows):
        ry = y0 + 28 + i * 38
        p.append(line(x0, ry - 14, x0 + sum(colw), ry - 14, color="#dde3ea", sw=1.0))
        p.append(text(x0 + colw[0] / 2, ry + 6, sym, size=13, color=INK, bold=True))
        p.append(text(x0 + colw[0] + colw[1] / 2, ry + 6, str(ln), size=13, color=NEG, bold=True))
        p.append(text(x0 + colw[0] + colw[1] + colw[2] / 2, ry + 6, code, size=14, color=POS, bold=True))

    p.append(text(W / 2, H - 26,
                  "передаємо лише довжини → обидві сторони відновлюють ті самі коди",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "canonical.svg"), W, H, *p,
           title="Канонічний Гаффман: код із самих довжин")


# ── adaptive: дерево оновлюється на льоту (sibling property) ───────────────────
# Ідея: декодер і кодер тримають однакове дерево й після кожного символу
# збільшують його лічильник, за потреби міняючи вузли місцями, щоб ваги
# спадали зліва направо й знизу вгору.

def fig_adaptive():
    W, H = 680, 300
    p = []
    r = 15

    def small_tree(ox, title, weights, p):
        p.append(text(ox + 120, 56, title, size=12, color=INK, bold=True))
        root = (ox + 120, 86)
        L = (ox + 70, 150)
        R = (ox + 170, 150)
        LL = (ox + 40, 214)
        LR = (ox + 100, 214)
        for (a, b) in [(root, L), (root, R), (L, LL), (L, LR)]:
            p.append(line(a[0], a[1] + r, b[0], b[1] - r, color=MUTED, sw=1.4))
        nodes = [(root, weights[0], False), (L, weights[1], False),
                 (R, weights[2], True), (LL, weights[3], True), (LR, weights[4], True)]
        for (c, w, leaf) in nodes:
            p.append(circle(c[0], c[1], r, fill="#f3c6bf" if leaf else "#eaf2fb",
                            stroke=POS if leaf else INK, sw=1.6))
            p.append(text(c[0], c[1] + 4, str(w), size=11, color=INK, bold=True))

    small_tree(20, "до символу 'R'", [5, 2, 3, 1, 1], p)
    p.append(arrow(330, 150, 374, 150, color=FIELD, sw=2.2))
    p.append(text(352, 138, "+1, обмін", size=10, color=FIELD, bold=True))
    small_tree(350, "після: лічильник R зріс", [6, 3, 3, 1, 2], p)

    p.append(text(W / 2, H - 16,
                  "жодних таблиць у файлі: обидві сторони перебудовують дерево однаково",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "adaptive.svg"), W, H, *p,
           title="Адаптивний Гаффман: дерево росте на льоту")


# ── blocking: кодування пар символів притискає до ентропії ────────────────────
# Ідея: коли одна ймовірність близька до 1, посимвольний Гаффман втрачає ~біт;
# кодуючи символи парами/трійками, надлишок ділиться на розмір блоку й тане.

def fig_blocking():
    W, H = 640, 320
    p = []
    ox, oy = 90, 250
    aw, ah = 470, 190
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 14, oy - ah - 2, "над H, біт/симв.", size=10, color=INK, bold=True, anchor="end"))
    p.append(text(ox + aw, oy + 20, "розмір блоку", size=11, color=INK, italic=True))

    # надлишок над H для блоків 1,2,3,4 (ілюстративно спадає ~1/n)
    over = [0.55, 0.27, 0.18, 0.13]
    labels = ["по 1", "по 2", "по 3", "по 4"]
    scale = ah / 0.7
    slot = aw / (len(over) + 0.6)
    bw = slot * 0.5
    for i, (v, lab) in enumerate(zip(over, labels)):
        bx = ox + 36 + i * slot
        bh = v * scale
        p.append(rect(bx, oy - bh, bw, bh, fill="#f3c6bf", stroke=POS, sw=1.6, rx=3))
        p.append(text(bx + bw / 2, oy - bh - 8, "%.2f" % v, size=10, color=POS, bold=True))
        p.append(text(bx + bw / 2, oy + 16, lab, size=11, color=INK))

    # дно H
    p.append(line(ox, oy, ox + aw, oy, color=FIELD, sw=1.4))
    p.append(text(ox + aw, oy - 6, "дно H", size=10, color=FIELD, anchor="end"))

    render(os.path.join(OUT, "blocking.svg"), W, H, *p,
           title="Кодування блоками тане надлишок над ентропією")


if __name__ == "__main__":
    fig_prefix()
    fig_build()
    fig_tree()
    fig_vs_entropy()
    fig_exchange()
    fig_canonical()
    fig_adaptive()
    fig_blocking()
    print("OK: figures written to", OUT)
