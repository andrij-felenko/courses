# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_FILL = "#eef4ff"
RED_FILL  = "#fdecea"
GREY_FILL = "#eef1f5"

# мажоритарна функція maj(A,B,C) = A·B + A·C + B·C, рядки 000..111
MAJ = ["0", "0", "0", "1", "0", "1", "1", "1"]


def cell(x, y, w, h, s, fill=BG, size=14, color=INK, bold=True):
    return (rect(x, y, w, h, fill=fill, stroke=INK, sw=1.2, rx=0) +
            text(x + w / 2.0, y + h / 2.0 + size * 0.35, s, size=size, color=color, bold=bold))


def val_color(v):
    return POS if v == "1" else MUTED


def edge(x1, y1, x2, y2, r1, r2, dash=None, color=LINE, sw=1.6):
    """Відрізок між двома вузлами, підрізаний на радіуси — не заходить у вузол."""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    if d == 0:
        return ""
    ux, uy = dx / d, dy / d
    return line(x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2, color=color, sw=sw, dash=dash)


# ── 1. Кофактор = половина таблиці без свого стовпчика ───────────────────────
def fig_cofactor():
    W, H = 880, 420
    p = []
    cw, fw, rh = 40, 54, 30

    # ліворуч: повна таблиця істинності
    tx, ty = 70, 96
    heads = [("A", NEG), ("B", MUTED), ("C", MUTED)]
    for k, (s, c) in enumerate(heads):
        p.append(text(tx + cw * k + cw / 2.0, ty - 14, s, size=13, color=c, bold=True))
    p.append(text(tx + cw * 3 + fw / 2.0, ty - 14, "f", size=13, color=INK, bold=True))

    for i in range(8):
        bits = "%03d" % int(bin(i)[2:])
        block, idx = divmod(i, 4)
        yy = ty + idx * rh + block * (4 * rh + 22)
        a_fill = BLUE_FILL if block == 0 else RED_FILL
        for k in range(3):
            p.append(cell(tx + cw * k, yy, cw, rh, bits[k], size=13,
                          fill=(a_fill if k == 0 else BG),
                          color=(NEG if k == 0 and block == 0 else POS if k == 0 else INK)))
        p.append(cell(tx + cw * 3, yy, fw, rh, MAJ[i], size=13, color=val_color(MAJ[i])))

    # праворуч: дві половини вже як самостійні функції двох змінних
    rx = 590
    small = [
        (96, [("00", "0"), ("01", "0"), ("10", "0"), ("11", "1")], "f(0, B, C)  =  B · C", NEG),
        (238, [("00", "0"), ("01", "1"), ("10", "1"), ("11", "1")], "f(1, B, C)  =  B + C", POS),
    ]
    for sy, rows, cap, col in small:
        p.append(text(rx + cw / 2.0, sy - 14, "B", size=13, color=MUTED, bold=True))
        p.append(text(rx + cw + cw / 2.0, sy - 14, "C", size=13, color=MUTED, bold=True))
        p.append(text(rx + cw * 2 + fw / 2.0, sy - 14, "f", size=13, color=INK, bold=True))
        for j, (bc, v) in enumerate(rows):
            yy = sy + j * rh
            p.append(cell(rx, yy, cw, rh, bc[0], size=13))
            p.append(cell(rx + cw, yy, cw, rh, bc[1], size=13))
            p.append(cell(rx + cw * 2, yy, fw, rh, v, size=13, color=val_color(v)))
        p.append(text(rx + (cw * 2 + fw) / 2.0, sy + 4 * rh + 28, cap, size=15, color=col, bold=True))

    # стрілки: половина таблиці → кофактор
    p.append(text(427, 140, "A = 0", size=14, color=NEG, bold=True))
    p.append(arrow(280, 156, 575, 156))
    p.append(text(427, 282, "A = 1", size=14, color=POS, bold=True))
    p.append(arrow(280, 298, 575, 298))

    render(os.path.join(OUT, "cofactor.svg"), W, H, *p,
           title="Кофактор — це половина таблиці, з якої викинуто свій стовпчик")


# ── 2. Дерево мультиплексорів: розкладання, доведене до констант ─────────────
def mux(cx, cy, sel, w=56, h=64):
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    top, bot = cy - h / 2.0, cy + h / 2.0
    ins = h * 0.22
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x0, top, x1, top + ins, x1, bot - ins, x0, bot)
    out = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (pts, FILL, LINE)
    out += text(x0 + 12, cy - 10, "0", size=11, color=MUTED)
    out += text(x0 + 12, cy + 18, "1", size=11, color=MUTED)
    out += text(cx + 8, cy + 5, sel, size=15, color=NEG, bold=True)
    return out


def fig_mux():
    W, H = 740, 470
    p = []
    p.append(text(95, 70, "таблиця істинності", size=13, color=INK, bold=True))
    p.append(text(250, 70, "розклали C", size=13, color=INK, bold=True))
    p.append(text(420, 70, "потім B", size=13, color=INK, bold=True))
    p.append(text(590, 70, "потім A", size=13, color=INK, bold=True))

    ys = [100 + i * 46 for i in range(8)]
    for i, y in enumerate(ys):
        bits = "%03d" % int(bin(i)[2:])
        p.append(text(66, y + 5, bits, size=12, color=MUTED, anchor="end"))
        p.append(cell(77, y - 13, 36, 26, MAJ[i], size=14, color=val_color(MAJ[i])))

    cmux = [(ys[0] + ys[1]) / 2.0, (ys[2] + ys[3]) / 2.0, (ys[4] + ys[5]) / 2.0, (ys[6] + ys[7]) / 2.0]
    bmux = [(cmux[0] + cmux[1]) / 2.0, (cmux[2] + cmux[3]) / 2.0]
    amux = (bmux[0] + bmux[1]) / 2.0

    for k, cy in enumerate(cmux):
        p.append(line(113, ys[2 * k], 222, cy - 14))
        p.append(line(113, ys[2 * k + 1], 222, cy + 14))
        p.append(mux(250, cy, "C"))
    for k, cy in enumerate(bmux):
        p.append(line(278, cmux[2 * k], 392, cy - 14))
        p.append(line(278, cmux[2 * k + 1], 392, cy + 14))
        p.append(mux(420, cy, "B"))
    p.append(line(448, bmux[0], 562, amux - 14))
    p.append(line(448, bmux[1], 562, amux + 14))
    p.append(mux(590, amux, "A"))
    p.append(line(618, amux, 658, amux))
    p.append(text(674, amux + 6, "f", size=17, color=INK, bold=True))

    render(os.path.join(OUT, "mux.svg"), W, H, *p,
           title="Кожен трикутник — одне розкладання Шеннона")


# ── 3. Дерево рішень → діаграма (спільні піддерева злиті) ────────────────────
def node(cx, cy, s, r=18):
    return circle(cx, cy, r, fill=GREY_FILL, stroke=INK, sw=1.6) + \
           text(cx, cy + 5, s, size=15, color=INK, bold=True)


def leaf(cx, cy, s, w=30, h=26):
    return cell(cx - w / 2.0, cy - h / 2.0, w, h, s, size=14, color=val_color(s),
                fill=(RED_FILL if s == "1" else GREY_FILL))


DASH = "5,4"


def fig_bdd():
    W, H = 880, 470
    p = []
    p.append(text(256, 66, "дерево рішень: 7 вузлів, 8 листків", size=13, color=INK, bold=True))
    p.append(text(700, 66, "після злиття однакового: 4 вузли", size=13, color=INK, bold=True))

    # ── ліворуч: повне дерево ──
    lx = [60 + 56 * i for i in range(8)]
    cyx = [(lx[0] + lx[1]) / 2.0, (lx[2] + lx[3]) / 2.0, (lx[4] + lx[5]) / 2.0, (lx[6] + lx[7]) / 2.0]
    byx = [(cyx[0] + cyx[1]) / 2.0, (cyx[2] + cyx[3]) / 2.0]
    ax = (byx[0] + byx[1]) / 2.0
    YA, YB, YC, YL = 102, 192, 282, 372

    for k, cx in enumerate(cyx):
        p.append(edge(cx, YC, lx[2 * k], YL, 18, 15, dash=DASH))
        p.append(edge(cx, YC, lx[2 * k + 1], YL, 18, 15))
    for k, cx in enumerate(byx):
        p.append(edge(cx, YB, cyx[2 * k], YC, 18, 18, dash=DASH))
        p.append(edge(cx, YB, cyx[2 * k + 1], YC, 18, 18))
    p.append(edge(ax, YA, byx[0], YB, 18, 18, dash=DASH))
    p.append(edge(ax, YA, byx[1], YB, 18, 18))

    for i, x in enumerate(lx):
        p.append(leaf(x, YL, MAJ[i]))
    for cx in cyx:
        p.append(node(cx, YC, "C"))
    for cx in byx:
        p.append(node(cx, YB, "B"))
    p.append(node(ax, YA, "A"))

    # ── праворуч: зведена діаграма ──
    RA, RB0, RB1, RC = (700, 102), (640, 192), (760, 192), (700, 282)
    T0, T1 = (640, 372), (760, 372)
    p.append(edge(RA[0], RA[1], RB0[0], RB0[1], 18, 18, dash=DASH))
    p.append(edge(RA[0], RA[1], RB1[0], RB1[1], 18, 18))
    p.append(edge(RB0[0], RB0[1], T0[0], T0[1], 18, 15, dash=DASH))
    p.append(edge(RB0[0], RB0[1], RC[0], RC[1], 18, 18))
    p.append(edge(RB1[0], RB1[1], RC[0], RC[1], 18, 18, dash=DASH))
    p.append(edge(RB1[0], RB1[1], T1[0], T1[1], 18, 15))
    p.append(edge(RC[0], RC[1], T0[0], T0[1], 18, 15, dash=DASH))
    p.append(edge(RC[0], RC[1], T1[0], T1[1], 18, 15))
    p.append(node(*RA, s="A"))
    p.append(node(*RB0, s="B"))
    p.append(node(*RB1, s="B"))
    p.append(node(*RC, s="C"))
    p.append(leaf(T0[0], T0[1], "0"))
    p.append(leaf(T1[0], T1[1], "1"))

    # легенда
    p.append(line(60, 424, 96, 424, dash=DASH, sw=1.6))
    p.append(text(104, 429, "змінна = 0", size=12, color=MUTED, anchor="start"))
    p.append(line(250, 424, 286, 424, sw=1.6))
    p.append(text(294, 429, "змінна = 1", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "bdd.svg"), W, H, *p,
           title="Розкладаємо далі — і дерево стискається в діаграму")


# ── 4. Порядок змінних вирішує все (вставка proj-recursive-expansion) ────────
def fig_order():
    W, H = 1080, 600
    p = []

    # ── ліворуч: порядок «пара за парою» — драбина завширшки 1 ──
    p.append(text(215, 62, "порядок  x₁ y₁ x₂ y₂ x₃ y₃", size=14, color=INK, bold=True))
    p.append(text(215, 86, "пару прочитав — і забув: 6 вузлів", size=12, color=MUTED))

    XC, YC = 140, 230
    LV = [130, 195, 260, 325, 390, 455]
    TY = 540
    Z, O = 100, 350
    names = ["x₁", "y₁", "x₂", "y₂", "x₃", "y₃"]
    for k, yy in enumerate(LV):
        p.append(text(62, yy + 5, names[k], size=12, color=MUTED, bold=True))

    # ребра (спершу лінії, потім вузли зверху)
    p.append(edge(XC, LV[0], XC, LV[2], 18, 18, dash=DASH))          # x₁=0 → x₂
    p.append(edge(XC, LV[0], YC, LV[1], 18, 18))                     # x₁=1 → y₁
    p.append(edge(YC, LV[1], XC, LV[2], 18, 18, dash=DASH))          # y₁=0 → x₂
    p.append(edge(YC, LV[1], O, TY, 18, 15))                         # y₁=1 → 1
    p.append(edge(XC, LV[2], XC, LV[4], 18, 18, dash=DASH))          # x₂=0 → x₃
    p.append(edge(XC, LV[2], YC, LV[3], 18, 18))                     # x₂=1 → y₂
    p.append(edge(YC, LV[3], XC, LV[4], 18, 18, dash=DASH))          # y₂=0 → x₃
    p.append(edge(YC, LV[3], O, TY, 18, 15))                         # y₂=1 → 1
    p.append(edge(XC, LV[4], Z, TY, 18, 15, dash=DASH))              # x₃=0 → 0
    p.append(edge(XC, LV[4], YC, LV[5], 18, 18))                     # x₃=1 → y₃
    p.append(edge(YC, LV[5], Z, TY, 18, 15, dash=DASH))              # y₃=0 → 0
    p.append(edge(YC, LV[5], O, TY, 18, 15))                         # y₃=1 → 1

    for k, yy in enumerate(LV):
        p.append(node(XC if k % 2 == 0 else YC, yy, names[k]))
    p.append(leaf(Z, TY, "0"))
    p.append(leaf(O, TY, "1"))

    # ── праворуч: порядок «спершу всі x» — дерево станів ──
    p.append(text(757, 62, "порядок  x₁ x₂ x₃ y₁ y₂ y₃", size=14, color=INK, bold=True))
    p.append(text(757, 86, "перед першим y треба пам'ятати, які саме x були одиницями", size=12, color=MUTED))

    LEAF = [466 + 80 * i for i in range(8)]
    L3 = [(LEAF[0] + LEAF[1]) / 2.0, (LEAF[2] + LEAF[3]) / 2.0,
          (LEAF[4] + LEAF[5]) / 2.0, (LEAF[6] + LEAF[7]) / 2.0]
    L2 = [(L3[0] + L3[1]) / 2.0, (L3[2] + L3[3]) / 2.0]
    L1 = (L2[0] + L2[1]) / 2.0
    RY1, RY2, RY3, RYL = 200, 290, 380, 470

    for k, cx in enumerate(L3):
        p.append(edge(cx, RY3, LEAF[2 * k], RYL, 18, 16, dash=DASH))
        p.append(edge(cx, RY3, LEAF[2 * k + 1], RYL, 18, 16))
    for k, cx in enumerate(L2):
        p.append(edge(cx, RY2, L3[2 * k], RY3, 18, 18, dash=DASH))
        p.append(edge(cx, RY2, L3[2 * k + 1], RY3, 18, 18))
    p.append(edge(L1, RY1, L2[0], RY2, 18, 18, dash=DASH))
    p.append(edge(L1, RY1, L2[1], RY2, 18, 18))

    p.append(node(L1, RY1, "x₁"))
    for cx in L2:
        p.append(node(cx, RY2, "x₂"))
    for cx in L3:
        p.append(node(cx, RY3, "x₃"))

    # залишки: що лишилося дорахувати після трьох x
    rest = ["0", "y₃", "y₂", "y₂+y₃", "y₁", "y₁+y₃", "y₁+y₂", "y₁+y₂+y₃"]
    for i, cx in enumerate(LEAF):
        col = GREY_FILL if i == 0 else BLUE_FILL
        p.append(fitbox(cx - 38, RYL - 15, 76, 30, rest[i], size=12, fill=col, pad=5))

    p.append(text(757, 528, "усі 8 залишків різні → 7 ненульових, і кожен потребує власного вузла",
                  size=12, color=MUTED))
    p.append(text(757, 556, "разом 14 вузлів проти 6", size=13, color=POS, bold=True))

    # легенда
    p.append(line(60, 556, 96, 556, dash=DASH, sw=1.6))
    p.append(text(104, 561, "змінна = 0", size=12, color=MUTED, anchor="start"))
    p.append(line(216, 556, 252, 556, sw=1.6))
    p.append(text(260, 561, "змінна = 1", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "order.svg"), W, H, *p,
           title="Та сама функція: порядок змінних вирішує, шість вузлів чи чотирнадцять")


# ── 5. Підрахунок наборів: пропущені рівні коштують 2^k ──────────────────────
def fig_counting():
    W, H = 900, 580
    p = []
    p.append(text(430, 60, "f = x₁·y₁ + x₂·y₂ — чотири вузли, а наборів сім", size=14, color=INK, bold=True))

    LX, LY = 340, 460
    L = [120, 200, 280, 360]
    TY = 460
    Z, O = 290, 570
    names = ["x₁", "y₁", "x₂", "y₂"]
    for k, yy in enumerate(L):
        p.append(text(90, yy + 5, names[k], size=12, color=MUTED, bold=True))

    p.append(edge(LX, L[0], LX, L[2], 18, 18, dash=DASH))     # x₁=0 → x₂ (стрибок через y₁)
    p.append(edge(LX, L[0], LY, L[1], 18, 18))                # x₁=1 → y₁
    p.append(edge(LY, L[1], LX, L[2], 18, 18, dash=DASH))     # y₁=0 → x₂
    p.append(edge(LY, L[1], O, TY, 18, 15))                   # y₁=1 → 1 (стрибок через x₂,y₂)
    p.append(edge(LX, L[2], Z, TY, 18, 15, dash=DASH))        # x₂=0 → 0
    p.append(edge(LX, L[2], LY, L[3], 18, 18))                # x₂=1 → y₂
    p.append(edge(LY, L[3], Z, TY, 18, 15, dash=DASH))        # y₂=0 → 0
    p.append(edge(LY, L[3], O, TY, 18, 15))                   # y₂=1 → 1

    p.append(node(LX, L[0], "x₁"))
    p.append(node(LY, L[1], "y₁"))
    p.append(node(LX, L[2], "x₂"))
    p.append(node(LY, L[3], "y₂"))
    p.append(leaf(Z, TY, "0"))
    p.append(leaf(O, TY, "1"))

    # підписи двох стрибків
    p.append(text(306, 198, "×2  y₁ пропущено", size=12, color=POS, anchor="end", bold=True))
    p.append(text(626, 300, "×4  x₂ і y₂ пропущені", size=12, color=POS, anchor="start", bold=True))

    p.append(mtext(650, 130, [
        "скільки наборів дає 1",
        "у піддереві вузла:",
        "",
        "y₂ →  1",
        "x₂ →  1",
        "y₁ →  1 + 4 = 5",
        "x₁ →  5 + 2 = 7",
    ], size=13, anchor="start"))

    p.append(text(430, 534, "шляхів до листка «1» — три, а наборів  4 + 1 + 2 = 7",
                  size=14, color=INK, bold=True))

    render(os.path.join(OUT, "counting.svg"), W, H, *p,
           title="Пропущений рівень — це не один набір, а 2^k наборів")


# ══ фігури вставки math-cofactors.md ════════════════════════════════════════

GREEN_FILL = "#e8f8ee"


# ── 6. Дві «додавання» на тих самих двох елементах ───────────────────────────
def fig_two_algebras():
    W, H = 940, 540
    p = []

    def op_table(cx, title, vals, hl_fill, hl_stroke, hl_color, note, expansion):
        out = []
        out.append(text(cx, 70, title, size=18, bold=True))
        cw, ch = 46, 40
        tx, ty = cx - 69, 108
        out.append(text(tx + cw * 2, 96, "b", size=14, bold=True, color=MUTED))
        out.append(text(tx - 18, ty + ch * 2 + 5, "a", size=14, bold=True, color=MUTED))
        out.append(cell(tx, ty, cw, ch, "", fill=GREY_FILL))
        for j, b in enumerate(("0", "1")):
            out.append(cell(tx + cw * (j + 1), ty, cw, ch, b, fill=GREY_FILL, size=15, color=MUTED))
            out.append(cell(tx, ty + ch * (j + 1), cw, ch, b, fill=GREY_FILL, size=15, color=MUTED))
        for i in (0, 1):
            for j in (0, 1):
                hl = (i == 1 and j == 1)
                out.append(cell(tx + cw * (j + 1), ty + ch * (i + 1), cw, ch, vals[(i, j)],
                                fill=hl_fill if hl else BG, size=17,
                                color=hl_color if hl else INK))
        out.append(arrow(cx, 240, cx, 268))
        b1, _, _ = textbox(cx, 306, note, size=13, fill=hl_fill, stroke=hl_stroke, color=INK)
        out.append(b1)
        out.append(arrow(cx, 352, cx, 380))
        b2, _, _ = textbox(cx, 418, expansion, size=15, bold=True,
                           fill=BG, stroke=hl_stroke, color=INK)
        out.append(b2)
        return out

    p += op_table(250, "a + b   («або»)",
                  {(0, 0): "0", (0, 1): "1", (1, 0): "1", (1, 1): "1"},
                  RED_FILL, POS, POS,
                  "1 + 1 = 1: ґратка, а не поле.\n"
                  "Додавання незворотне — із суми\n"
                  "a + b не «відняти» назад a.",
                  "розкладання Шеннона\nf = x·f₁ + x̄·f₀")

    p += op_table(690, "a ⊕ b   («різне»)",
                  {(0, 0): "0", (0, 1): "1", (1, 0): "1", (1, 1): "0"},
                  GREEN_FILL, FIELD, FIELD,
                  "1 ⊕ 1 = 0: поле GF(2).\n"
                  "a ⊕ a = 0, тож ⊕ — це водночас\n"
                  "і додавання, і віднімання.",
                  "розкладання Давіо\nf = f₀ ⊕ x·(∂f/∂x)")

    p.append(line(470, 56, 470, 470, color=MUTED, sw=1.2, dash="6 6"))
    p.append(text(470, 505,
                  "Три клітинки з чотирьох однакові. Уся різниця — у правій нижній.",
                  size=15, bold=True))

    render(os.path.join(OUT, "two-algebras.svg"), W, H, *p,
           title="Дві дії «додавання» на тих самих двох елементах")


# ── 7. Три типи вузла розкладання ────────────────────────────────────────────
def fig_davio_nodes():
    W, H = 980, 430
    p = []

    def node(cx, title, formula, lab_l, lab_r, kid_l, kid_r, tone, note):
        out = []
        out.append(text(cx, 70, title, size=16, bold=True))
        b, _, _ = textbox(cx, 118, formula, size=15, bold=True, fill=BG, stroke=tone)
        out.append(b)
        out.append(circle(cx, 195, 24, fill=GREY_FILL, stroke=INK, sw=2))
        out.append(text(cx, 201, "x", size=18, bold=True))
        out.append(line(cx, 219, cx - 82, 280, color=INK, sw=1.6))
        out.append(line(cx, 219, cx + 82, 280, color=INK, sw=1.6))
        out.append(text(cx - 74, 236, lab_l, size=14, bold=True, color=MUTED))
        out.append(text(cx + 74, 236, lab_r, size=14, bold=True, color=MUTED))
        bl, _, _ = textbox(cx - 82, 300, kid_l, size=15, bold=True, min_w=64,
                           fill=BLUE_FILL, stroke=INK)
        out.append(bl)
        d = (kid_r == "∂f/∂x")
        br, _, _ = textbox(cx + 82, 300, kid_r, size=15, bold=True, min_w=64,
                           fill=GREEN_FILL if d else BLUE_FILL,
                           stroke=FIELD if d else INK)
        out.append(br)
        bn, _, _ = textbox(cx, 372, note, size=12, fill=BG, stroke=MUTED, color=MUTED)
        out.append(bn)
        return out

    p += node(165, "Шеннон (S)", "f = x·f₁ + x̄·f₀", "x̄", "x", "f₀", "f₁", POS,
              "обидві гілки — половини f;\nзбирає «+»")
    p += node(490, "Давіо позитивний (pD)", "f = f₀ ⊕ x·∂f/∂x", "1", "x", "f₀", "∂f/∂x", FIELD,
              "ліва гілка — половина при x = 0,\nправа — похідна; збирає «⊕»")
    p += node(815, "Давіо негативний (nD)", "f = f₁ ⊕ x̄·∂f/∂x", "1", "x̄", "f₁", "∂f/∂x", FIELD,
              "ліва гілка — половина при x = 1,\nправа — похідна; збирає «⊕»")

    p.append(line(327, 52, 327, 415, color=MUTED, sw=1.2, dash="6 6"))
    p.append(line(652, 52, 652, 415, color=MUTED, sw=1.2, dash="6 6"))

    render(os.path.join(OUT, "davio-nodes.svg"), W, H, *p,
           title="Один вузол, три способи розібрати функцію за змінною x")


# ── 8. Парність: найгірше для карти Карно, найкраще для Давіо ────────────────
def fig_parity_anf():
    W, H = 940, 440
    p = []
    GRAY = ("00", "01", "11", "10")

    tx, ty, cw = 170, 110, 52
    p.append(text(tx + cw * 2, 72, "cd", size=15, bold=True, color=MUTED))
    p.append(text(112, ty + cw * 2, "ab", size=15, bold=True, color=MUTED))
    for j, cd in enumerate(GRAY):
        p.append(text(tx + cw * j + cw / 2.0, ty - 12, cd, size=13, color=MUTED))
    for i, ab in enumerate(GRAY):
        p.append(text(148, ty + cw * i + cw / 2.0 + 5, ab, size=13, color=MUTED))
        for j, cd in enumerate(GRAY):
            v = (int(ab[0]) ^ int(ab[1])) ^ (int(cd[0]) ^ int(cd[1]))
            p.append(cell(tx + cw * j, ty + cw * i, cw, cw, str(v), size=17,
                          fill=RED_FILL if v else BG,
                          color=POS if v else MUTED))
    bn, _, _ = textbox(250, 372,
                       "8 одиниць, і жодні дві не сусідні —\n"
                       "склеювати нічого: мінімальна сума\n"
                       "добутків — усі 8 мінтермів, 32 літерали.",
                       size=13, fill=RED_FILL, stroke=POS)
    p.append(bn)

    p.append(text(690, 76, "f = a ⊕ b ⊕ c ⊕ d", size=19, bold=True, color=FIELD))
    for x, s in ((600, "a"), (660, "b"), (720, "c"), (780, "d")):
        p.append(text(x, 136, s, size=16, bold=True))
    for gx, (i1, i2) in ((630, (600, 660)), (750, (720, 780))):
        for xi in (i1, i2):
            p.append(line(xi, 146, gx, 182, color=INK, sw=1.6))
        p.append(circle(gx, 200, 18, fill=GREEN_FILL, stroke=FIELD, sw=2))
        p.append(text(gx, 207, "⊕", size=17, bold=True, color=FIELD))
    p.append(line(630, 218, 690, 252, color=INK, sw=1.6))
    p.append(line(750, 218, 690, 252, color=INK, sw=1.6))
    p.append(circle(690, 270, 18, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(text(690, 277, "⊕", size=17, bold=True, color=FIELD))
    p.append(arrow(690, 288, 690, 332))
    bg, _, _ = textbox(690, 378,
                       "3 вентилі ⊕, 4 літерали.\n"
                       "Розмір росте лінійно з n —\n"
                       "там, де сума добутків росте як 2ⁿ⁻¹.",
                       size=13, fill=GREEN_FILL, stroke=FIELD)
    p.append(bg)

    p.append(line(470, 56, 470, 415, color=MUTED, sw=1.2, dash="6 6"))

    render(os.path.join(OUT, "parity-anf.svg"), W, H, *p,
           title="Та сама функція: ліворуч — мовою «+», праворуч — мовою «⊕»")


# ── Родовід формули: хто написав, хто передав, хто дав ім'я ──────────────────
#    (вставка hist-boole-shannon)
def fig_lineage():
    W, H = 1000, 620
    p = []
    NX, NW, NH = 60, 430, 80
    ys = [64, 184, 304, 424]

    nodes = [
        (["1847 · Буль, «Математичний аналіз логіки»",
          "φ(x) = φ(1)·x + φ(0)·(1−x)"], BLUE_FILL),
        (["1854 · Буль, «Закони думки», Твердження II",
          "«розвинути функцію від логічних символів»"], BLUE_FILL),
        (["1905 · Кутюра, «Алгебра логіки», §24",
          "«Закон розвитку»: f(x) = f(1)·x + f(0)·x′"], GREY_FILL),
        (["1949 · Шеннон, «Синтез двополюсних схем», с. 62",
          "f(X₁,…) = X₁·f(1,…) + X₁′·f(0,…)"], RED_FILL),
    ]
    notes = [
        ["вивід — через степеневий ряд:", "Маклорен, а тоді xⁿ = x"],
        ["та сама тотожність; далі — «складники»", "й розвиток до 2ⁿ доданків"],
        ["сучасний запис: x′ замість (1−x);", "саме цю книжку цитуватиме Шеннон"],
        ["подає як відому загальну теорему;", "джерело [2] — Кутюра, Буля названо в тексті"],
    ]

    for i in range(3):
        p.append(arrow(275, ys[i] + NH, 275, ys[i + 1] - 6))

    for i, y in enumerate(ys):
        lines, fill = nodes[i]
        p.append(fitbox(NX, y, NW, NH, lines, size=14, fill=fill))
        p.append(mtext(540, y + 32, notes[i], size=13, color=MUTED, anchor="start"))

    p.append(arrow(210, 536, 210, 508, color=POS, sw=2.0))
    p.append(fitbox(60, 536, 300, 56, "1950-ті → «розкладання Шеннона»",
                    size=14, fill=RED_FILL, bold=True))
    p.append(text(380, 556, "ім'я чіпляється сюди —", size=13, color=POS,
                  anchor="start", bold=True))
    p.append(text(380, 578, "через 95 років після «Законів думки»", size=13,
                  color=MUTED, anchor="start"))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід формули: хто написав, хто передав, хто дав ім'я")


# ── Троє на тому самому мосту: задум і друк (вставка hist-boole-shannon) ─────
def m_open(cx, cy):
    return circle(cx, cy, 7, fill=BG, stroke=MUTED, sw=1.8)


def m_half(cx, cy):
    return circle(cx, cy, 7, fill=GREY_FILL, stroke=INK, sw=1.8)


def m_solid(cx, cy, color=INK):
    return circle(cx, cy, 7, fill=color, stroke=color, sw=1.8)


def fig_bridges():
    W, H = 1000, 450
    p = []

    def X(yr):
        return 190 + (yr - 1934) * 86.0

    AX = 360
    p.append(line(175, AX, 895, AX, color=MUTED, sw=1.4))
    for yr in range(1934, 1943):
        p.append(line(X(yr), AX, X(yr), AX + 6, color=MUTED, sw=1.2))
        p.append(text(X(yr), AX + 24, str(yr), size=12, color=MUTED))

    y = 100
    p.append(text(176, y + 5, "Накашіма", size=14, color=INK, anchor="end", bold=True))
    p.append(line(X(1934), y, X(1936.4), y, color=MUTED, sw=2.2))
    p.append(m_open(X(1934), y))
    p.append(m_solid(X(1935.7), y))
    p.append(m_solid(X(1936.4), y))
    p.append(text(X(1934), y - 16, "задум", size=12, color=MUTED))
    p.append(text(X(1935.7), y + 26, "вер. 1935 · яп.", size=12, color=INK))
    p.append(text(X(1936.4), y - 16, "трав. 1936 · англ.", size=12, color=INK))

    y = 190
    p.append(text(176, y + 5, "Шестаков", size=14, color=INK, anchor="end", bold=True))
    p.append(line(X(1935), y, X(1941), y, color=MUTED, sw=2.2))
    p.append(m_open(X(1935), y))
    p.append(m_half(X(1938), y))
    p.append(m_solid(X(1941), y))
    p.append(text(X(1935), y + 26, "задум · за свідченнями", size=12, color=MUTED))
    p.append(text(X(1938), y - 16, "дисертація 1938", size=12, color=INK))
    p.append(text(X(1941), y + 26, "друк 1941", size=12, color=INK))

    y = 280
    p.append(text(176, y + 5, "Шеннон", size=14, color=INK, anchor="end", bold=True))
    p.append(line(X(1936.5), y, X(1938.45), y, color=MUTED, sw=2.2))
    p.append(m_open(X(1936.5), y))
    p.append(m_half(X(1937.7), y))
    p.append(m_solid(X(1938.45), y, color=POS))
    p.append(text(X(1936.5), y + 26, "задум", size=12, color=MUTED))
    p.append(text(X(1937.7), y - 16, "дисертація 1937", size=12, color=INK))
    p.append(text(X(1938.45), y + 26, "друк · червень 1938", size=12, color=POS, bold=True))
    p.append(arrow(760, y, 592, y, color=POS, sw=1.8))
    p.append(text(772, y + 5, "ім'я дісталося сюди", size=13, color=POS,
                  anchor="start", bold=True))

    ly = 418
    p.append(m_open(200, ly))
    p.append(text(214, ly + 5, "задум", size=12, color=MUTED, anchor="start"))
    p.append(m_half(430, ly))
    p.append(text(444, ly + 5, "дисертація", size=12, color=MUTED, anchor="start"))
    p.append(m_solid(640, ly))
    p.append(text(654, ly + 5, "друк", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "bridges.svg"), W, H, *p,
           title="Троє вийшли на той самий міст: задум і друк")


# ── фігура вставки proj-recursive-expansion.md ──────────────────────────────
# Усі числа — виміряні тією самою машинкою, що у вставці.
def fig_explosion():
    W, H = 980, 620
    X0, X1 = 108, 828
    Y0, Y1 = 88, 512                      # 10^5 угорі, 10^0 унизу
    DEC = (Y1 - Y0) / 5.0
    NMAX = 14
    RED, ORANGE, GREEN, BLUE = "#c0392b", "#c2410c", "#1e7a46", "#2457d6"
    p = []

    def px(n):
        return X0 + (n - 1.0) / (NMAX - 1.0) * (X1 - X0)

    def py(v):
        return Y1 - math.log10(v) * DEC

    # сітка, вісь Y
    for v, s in [(1, "1"), (10, "10"), (100, "100"), (1000, "1 000"),
                 (10000, "10 000"), (100000, "100 000")]:
        yy = py(v)
        p.append(line(X0, yy, X1, yy, color="#e2e6ea", sw=1.0))
        p.append(text(X0 - 12, yy + 5, s, size=12, color=MUTED, anchor="end"))
    p.append(text(X0 - 12, Y0 - 20, "вузлів у діаграмі, логарифмічна шкала",
                  size=12, color=MUTED, anchor="start"))
    p.append(line(X0, Y0, X0, Y1, color=INK, sw=1.4))
    p.append(line(X0, Y1, X1, Y1, color=INK, sw=1.4))

    # вісь X
    for n in [1, 2, 4, 6, 8, 10, 12, 14]:
        xx = px(n)
        p.append(line(xx, Y1, xx, Y1 + 6, color=INK, sw=1.2))
        p.append(text(xx, Y1 + 26, str(n), size=12, color=MUTED))
    p.append(text((X0 + X1) / 2.0, Y1 + 54, "n — розрядність", size=13, color=INK, bold=True))

    NS = list(range(1, NMAX + 1))
    curves = [
        ([6 * n - 2 for n in NS], NS, GREEN),                    # суматор: перенос
        ([2 * n for n in NS], NS, BLUE),                         # пари, чергуючи
        ([2 ** (n + 1) - 2 for n in NS], NS, ORANGE),            # пари, групами
        ([2, 7, 14, 34, 71, 167, 379, 926, 2186, 5246, 12371, 29398],
         list(range(1, 13)), RED),                               # множник: середній біт
    ]
    for vals, ns, color in curves:
        for k in range(len(vals) - 1):
            p.append(line(px(ns[k]), py(vals[k]), px(ns[k + 1]), py(vals[k + 1]),
                          color=color, sw=2.4))
        for k, v in enumerate(vals):
            p.append(circle(px(ns[k]), py(v), 3.4, fill=color, stroke=color, sw=1.0))

    # легенда — у порожньому лівому верхньому куті, рядками (без рамки)
    legend = [
        (RED, "множник, середній біт", "≈ 2.4ⁿ — вибухає за будь-якого порядку"),
        (ORANGE, "пари, порядок групами", "2ⁿ⁺¹ − 2 — вибухає через порядок"),
        (GREEN, "суматор, вихідний перенос", "6n − 2"),
        (BLUE, "пари, порядок чергуючи", "2n"),
    ]
    ly = 112
    for color, name, formula in legend:
        p.append(line(132, ly, 176, ly, color=color, sw=2.8))
        p.append(circle(154, ly, 3.4, fill=color, stroke=color, sw=1.0))
        p.append(text(188, ly + 5, name, size=13, color=INK, anchor="start", bold=True))
        p.append(text(188, ly + 24, formula, size=12, color=MUTED, anchor="start"))
        ly += 46

    p.append(text((X0 + X1) / 2.0, H - 22,
                  "дві прямі й дві ракети — і це та сама машинка на тих самих правилах",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "explosion.svg"), W, H, *p,
           title="Що машинка тягне, а що ні: вузлів проти розрядності")


fig_cofactor()
fig_mux()
fig_bdd()
fig_order()
fig_counting()
fig_explosion()
fig_two_algebras()
fig_davio_nodes()
fig_parity_anf()
fig_lineage()
fig_bridges()
print("готово:", os.listdir(OUT))
