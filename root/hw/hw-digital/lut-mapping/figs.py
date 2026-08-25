# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SEL = "#8e44ad"   # лінія вибору / керівний біт
Z0  = NEG         # гілка «0»
Z1  = INK         # гілка «1»


def node(cx, cy, label, r=16, ring=None):
    """Вузол-питання: коло з літерою змінної; ring — колір підсвітки."""
    out = ""
    if ring:
        out += circle(cx, cy, r + 5, fill="none", stroke=ring, sw=3)
    out += circle(cx, cy, r, fill=FILL, stroke=INK, sw=1.8)
    out += text(cx, cy + 5, label, size=15, bold=True)
    return out


def leaf(cx, cy, val, w=30, h=26, ring=None):
    """Листок-термінал 0/1."""
    out = ""
    if ring:
        out += rect(cx - w/2 - 4, cy - h/2 - 4, w + 8, h + 8, fill="none", stroke=ring, sw=3, rx=6)
    fill = "#eaf0fd" if val == "0" else "#fdecea"
    col = NEG if val == "0" else POS
    out += rect(cx - w/2, cy - h/2, w, h, fill=fill, stroke=col, sw=1.8, rx=5)
    out += text(cx, cy + 5, val, size=15, color=col, bold=True)
    return out


def branch(x1, y1, x2, y2, kind):
    """kind=0 — штрихова синя гілка; kind=1 — суцільна темна."""
    if kind == 0:
        return line(x1, y1, x2, y2, color=Z0, sw=1.7, dash="5,4")
    return line(x1, y1, x2, y2, color=Z1, sw=1.9)


# ── 1. Розклад Шеннона = 2:1 мультиплексор ──────────────────────────────────
def fig_shannon():
    W, H = 780, 440
    f = [text(W/2, 26, "Розклад Шеннона за змінною = мультиплексор", size=17, bold=True)]

    # формула зверху
    f.append(text(210, 78, "f = ¬a·f₀ + a·f₁", size=17, bold=True))

    # ── ліва частина: вузол a з двома кофакторами ──
    ax, ay = 210, 140
    f.append(node(ax, ay, "a", r=20))
    # гілки
    lx, rx, cy = 118, 302, 258
    f.append(branch(ax - 8, ay + 16, lx, cy - 24, 0))
    f.append(branch(ax + 8, ay + 16, rx, cy - 24, 1))
    f.append(text(112, 196, "a = 0", size=12, color=Z0, bold=True, anchor="end"))
    f.append(text(308, 196, "a = 1", size=12, color=Z1, bold=True, anchor="start"))
    b1, _, _ = textbox(lx, cy, "f₀ = c", size=15, pad=12, fill="#eaf0fd", stroke=NEG, bold=True)
    b2, _, _ = textbox(rx, cy, "f₁ = b + c", size=15, pad=12, fill="#fdecea", stroke=POS, bold=True)
    f.append(b1); f.append(b2)
    f.append(text(210, 320, "кофактори — простіші функції", size=12, color=MUTED))
    f.append(text(210, 338, "від решти змінних", size=12, color=MUTED))

    # ── знак рівності ──
    f.append(text(430, 200, "≡", size=40, color=MUTED, bold=True))

    # ── права частина: символ 2:1 MUX ──
    x0, x1 = 545, 632
    yt, yb = 120, 320
    dy = 30
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.9"/>' % (
        x0, yt, x1, yt + dy, x1, yb - dy, x0, yb, FILL, LINE))
    f.append(text((x0 + x1)/2, (yt + yb)/2 - 4, "MUX", size=15, bold=True))
    f.append(text((x0 + x1)/2, (yt + yb)/2 + 16, "2:1", size=12, color=MUTED))
    # входи
    f.append(line(495, 165, x0, 165, color=NEG, sw=1.8))
    f.append(text(486, 169, "f₀", size=13, color=NEG, bold=True, anchor="end"))
    f.append(line(495, 275, x0, 275, color=POS, sw=1.8))
    f.append(text(486, 279, "f₁", size=13, color=POS, bold=True, anchor="end"))
    # вибір
    xm = (x0 + x1)/2
    f.append(line(xm, yb - dy/2, xm, 372, color=SEL, sw=2))
    f.append(text(xm, 390, "a", size=14, color=SEL, bold=True))
    f.append(text(xm, 408, "керівний біт", size=11, color=MUTED))
    # вихід
    f.append(line(x1, 220, 700, 220, color=INK, sw=1.8))
    f.append(text(712, 224, "f", size=14, bold=True, anchor="start"))

    render(os.path.join(OUT, 'shannon-split.svg'), W, H, *f)


# ── 2. Повне дерево рішень → скорочена діаграма (BDD) ────────────────────────
def fig_tree_to_bdd():
    W, H = 1020, 500
    f = [text(W/2, 26, "Згортання: дерево рішень → діаграма рішень (BDD)", size=17, bold=True)]
    f.append(text(240, 54, "Повне дерево рішень", size=14, bold=True, color=MUTED))
    f.append(text(775, 54, "Скорочена діаграма", size=14, bold=True, color=MUTED))

    # легенда
    f.append(line(700, 470, 730, 470, color=Z0, sw=1.7, dash="5,4"))
    f.append(text(736, 474, "гілка 0", size=11, color=MUTED, anchor="start"))
    f.append(line(820, 470, 850, 470, color=Z1, sw=1.9))
    f.append(text(856, 474, "гілка 1", size=11, color=MUTED, anchor="start"))

    # ── ЛІВЕ: повне дерево, порядок a,b,c ──
    ya, yb, yc, yl = 92, 178, 264, 352
    ax = 240
    b0x, b1x = 130, 350
    c0x, c1x, c2x, c3x = 80, 195, 305, 415       # чотири вузли c
    lx = [58, 108, 173, 223, 283, 333, 393, 443]  # вісім листків
    lv = ["0", "1", "0", "1", "0", "1", "1", "1"]

    # ребра a->b
    f.append(branch(ax - 10, ya + 12, b0x, yb - 16, 0))
    f.append(branch(ax + 10, ya + 12, b1x, yb - 16, 1))
    # ребра b->c
    f.append(branch(b0x - 8, yb + 14, c0x, yc - 15, 0))
    f.append(branch(b0x + 8, yb + 14, c1x, yc - 15, 1))
    f.append(branch(b1x - 8, yb + 14, c2x, yc - 15, 0))
    f.append(branch(b1x + 8, yb + 14, c3x, yc - 15, 1))
    # ребра c->листки
    cxs = [c0x, c1x, c2x, c3x]
    for i, cx in enumerate(cxs):
        f.append(branch(cx - 7, yc + 13, lx[2*i], yl - 13, 0))
        f.append(branch(cx + 7, yc + 13, lx[2*i+1], yl - 13, 1))
    # вузли
    f.append(node(ax, ya, "a"))
    f.append(node(b0x, yb, "b", ring=POS))       # зайвий: обидві гілки однакові
    f.append(node(b1x, yb, "b"))
    f.append(node(c0x, yc, "c"))
    f.append(node(c1x, yc, "c"))
    f.append(node(c2x, yc, "c"))
    f.append(node(c3x, yc, "c", ring=POS))       # зайвий: обидва листки = 1
    for i in range(8):
        f.append(leaf(lx[i], yl, lv[i]))
    # надмірності позначено червоними кільцями на вузлах (пояснення — у підписі)

    # ── стрілка-перехід посередині ──
    f.append(arrow(468, 250, 556, 250, color=INK, sw=2.2))
    mb, _, _ = textbox(512, 210, ["два", "правила"], size=11, pad=6, fill=BG, stroke=MUTED, color=MUTED)
    f.append(mb)

    # ── ПРАВЕ: скорочена BDD ──
    A = (778, 96); B = (852, 196); C = (712, 300)
    T0 = (668, 404); T1 = (836, 404)
    # ребра
    f.append(branch(A[0] - 8, A[1] + 12, C[0] + 6, C[1] - 16, 0))   # a-0-> c
    f.append(branch(A[0] + 8, A[1] + 12, B[0] - 8, B[1] - 14, 1))   # a-1-> b
    f.append(branch(B[0] - 8, B[1] + 12, C[0] + 12, C[1] - 15, 0))  # b-0-> c
    f.append(branch(B[0] + 6, B[1] + 14, T1[0], T1[1] - 17, 1))     # b-1-> 1
    f.append(branch(C[0] - 7, C[1] + 13, T0[0], T0[1] - 17, 0))     # c-0-> 0
    f.append(branch(C[0] + 8, C[1] + 12, T1[0] - 10, T1[1] - 17, 1))# c-1-> 1
    # вузли
    f.append(node(*A, "a"))
    f.append(node(*B, "b"))
    f.append(node(*C, "c"))
    f.append(leaf(*T0, "0"))
    f.append(leaf(*T1, "1"))
    f.append(text(775, 452, "3 вузли-питання, 2 листки", size=11.5, color=MUTED))

    render(os.path.join(OUT, 'tree-to-bdd.svg'), W, H, *f)


# ── 3. LUT-дерево з двох 2-входових LUT ─────────────────────────────────────
def fig_lut_tree():
    W, H = 740, 430
    f = [text(W/2, 26, "LUT-дерево для f = a·b + c", size=17, bold=True)]

    # входи
    def pin(x, y, name, col):
        return circle(x, y, 6, fill=FILL, stroke=col, sw=2) + \
               text(x - 16, y + 5, name, size=13, color=col, bold=True, anchor="end")
    ay, by, cy = 120, 176, 300
    f.append(pin(70, ay, "a", NEG))
    f.append(pin(70, by, "b", NEG))
    f.append(pin(70, cy, "c", NEG))

    # LUT_g
    gx, gy, gw, gh = 175, 96, 165, 104
    f.append(rect(gx, gy, gw, gh, fill="#f0f7f1", stroke=FIELD, sw=1.8))
    f.append(mtext(gx + gw/2, gy + 30, ["LUT (a, b)", "g = a·b"], size=13, bold=False))
    f.append(text(gx + gw/2, gy + 82, "біти  0 0 0 1", size=13, color=FIELD, bold=True))
    f.append(line(70 + 6, ay, gx, ay, color=NEG, sw=1.7))
    f.append(line(70 + 6, by, gx, by, color=NEG, sw=1.7))
    goutx, gouty = gx + gw, gy + gh/2
    f.append(line(goutx, gouty, goutx + 46, gouty, color=INK, sw=1.9))
    f.append(text(goutx + 24, gouty - 8, "g", size=13, bold=True))

    # LUT_f
    fx, fy, fw, fh = 430, 176, 165, 104
    f.append(rect(fx, fy, fw, fh, fill="#f0f7f1", stroke=FIELD, sw=1.8))
    f.append(mtext(fx + fw/2, fy + 30, ["LUT (g, c)", "f = g + c"], size=13, bold=False))
    f.append(text(fx + fw/2, fy + 82, "біти  0 1 1 1", size=13, color=FIELD, bold=True))
    # g -> LUT_f верхній вхід
    f.append(line(goutx + 46, gouty, fx, fy + 30, color=INK, sw=1.7))
    # c -> LUT_f нижній вхід
    f.append(line(70 + 6, cy, fx, fy + 74, color=NEG, sw=1.7))
    # вихід f
    foutx, fouty = fx + fw, fy + fh/2
    f.append(line(foutx, fouty, foutx + 60, fouty, color=POS, sw=2))
    f.append(circle(foutx + 60, fouty, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(foutx + 60, fouty - 14, "f", size=14, color=POS, bold=True))

    f.append(text(W/2, 400, "вихід одного LUT живить вхід другого — це і є дерево табличок",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'lut-tree.svg'), W, H, *f)


# ── 4. Устрій LUT: таблиця в комірках + дерево мультиплексорів ───────────────
def mux_tri(cx, cy, sel_col=SEL, sel_label=None, sel_down=34):
    """Маленький 2:1 MUX-трикутник, вершина-вихід праворуч; повертає (svg, outx, outy)."""
    x0, x1 = cx - 15, cx + 13
    yt, yb = cy - 22, cy + 22
    dy = 8
    s = '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
        x0, yt, x1, yt + dy, x1, yb - dy, x0, yb, FILL, LINE)
    s += line(cx, yb - dy - 2, cx, cy + 22 + sel_down - 22, color=sel_col, sw=1.5)
    if sel_label:
        s += text(cx, yb + sel_down - 8, sel_label, size=12, color=sel_col, bold=True)
    return s, x1, cy


def fig_lut_inside():
    W, H = 840, 540
    f = [text(W/2, 26, "Устрій LUT: таблиця істинності + дерево мультиплексорів", size=16.5, bold=True)]
    f.append(text(150, 56, "комірки (біти f)", size=12, bold=True, color=MUTED))

    addrs = ["000", "001", "010", "011", "100", "101", "110", "111"]
    vals  = ["0",   "1",   "0",   "1",   "0",   "1",   "1",   "1"]
    cellx, cellw, cellh = 60, 132, 40
    cy0, step = 74, 54
    cellcy = [cy0 + i*step for i in range(8)]
    for i in range(8):
        y = cellcy[i] - cellh/2
        col = NEG if vals[i] == "0" else POS
        fill = "#eaf0fd" if vals[i] == "0" else "#fdecea"
        f.append(rect(cellx, y, cellw, cellh, fill=fill, stroke=col, sw=1.6, rx=5))
        f.append(text(cellx + 14, cellcy[i] + 5, "abc=" + addrs[i], size=11.5, color=MUTED, anchor="start"))
        f.append(text(cellx + cellw - 16, cellcy[i] + 5, vals[i], size=15, color=col, bold=True, anchor="start"))

    # рівень c: 4 mux
    cxx = 300
    cmux_y = [(cellcy[0]+cellcy[1])/2, (cellcy[2]+cellcy[3])/2,
              (cellcy[4]+cellcy[5])/2, (cellcy[6]+cellcy[7])/2]
    couts = []
    for i, my in enumerate(cmux_y):
        # лінії від пари комірок до mux
        f.append(line(cellx + cellw, cellcy[2*i],   cxx - 15, my - 6, color=LINE, sw=1.3))
        f.append(line(cellx + cellw, cellcy[2*i+1], cxx - 15, my + 6, color=LINE, sw=1.3))
        s, ox, oy = mux_tri(cxx, my, sel_label=("c" if i == 3 else None))
        f.append(s); couts.append((ox, oy))

    # рівень b: 2 mux
    bxx = 470
    bmux_y = [(cmux_y[0]+cmux_y[1])/2, (cmux_y[2]+cmux_y[3])/2]
    bouts = []
    for i, my in enumerate(bmux_y):
        f.append(line(couts[2*i][0], couts[2*i][1], bxx - 15, my - 6, color=LINE, sw=1.3))
        f.append(line(couts[2*i+1][0], couts[2*i+1][1], bxx - 15, my + 6, color=LINE, sw=1.3))
        s, ox, oy = mux_tri(bxx, my, sel_label=("b" if i == 1 else None))
        f.append(s); bouts.append((ox, oy))

    # рівень a: 1 mux
    axx = 640
    amux_y = (bmux_y[0] + bmux_y[1]) / 2
    f.append(line(bouts[0][0], bouts[0][1], axx - 15, amux_y - 6, color=LINE, sw=1.3))
    f.append(line(bouts[1][0], bouts[1][1], axx - 15, amux_y + 6, color=LINE, sw=1.3))
    s, ox, oy = mux_tri(axx, amux_y, sel_label="a")
    f.append(s)
    # вихід
    f.append(line(ox, oy, 762, oy, color=POS, sw=2))
    f.append(circle(762, oy, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(762, oy - 14, "f", size=14, color=POS, bold=True))

    # підписи рівнів
    f.append(text(cxx, 500, "вибір c", size=11.5, color=MUTED))
    f.append(text(bxx, 500, "вибір b", size=11.5, color=MUTED))
    f.append(text(axx, 500, "вибір a", size=11.5, color=MUTED))
    f.append(text(W/2, 524, "адреса abc пропускає до виходу рівно одну комірку — це повне дерево рішень у кремнії",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, 'lut-inside.svg'), W, H, *f)


# ── 5. Горловина make_node: обидва правила на вході ─────────────────────────
def fig_make_node():
    W, H = 990, 540
    f = [text(W/2, 28, "make_node — горловина, крізь яку народжується кожен вузол",
              size=16.5, bold=True)]

    # роздільник панелей
    f.append(line(612, 56, 612, 500, color="#d5d9de", sw=1.4, dash="6,5"))

    # ── ЛІВА панель: потік ──
    cx = 168
    b, _, _ = textbox(cx, 88, "make_node(var, lo, hi)", size=13.5, pad=11,
                      fill="#f0f7f1", stroke=FIELD, bold=True)
    f.append(b)

    # крок 1
    f.append(arrow(cx, 112, cx, 152, color=INK, sw=1.8))
    b, w1, h1 = textbox(cx, 176, "lo == hi ?", size=13.5, pad=11, min_w=178,
                        fill=FILL, stroke=LINE, bold=True)
    f.append(b)
    f.append(arrow(cx + w1/2, 176, 336, 176, color=POS, sw=1.8))
    f.append(text(cx + w1/2 + 34, 166, "так", size=11.5, color=POS, bold=True))
    b, _, _ = textbox(452, 176, ["правило 1: зайве питання", "поверни lo — вузла не буде"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, color=POS)
    f.append(b)

    # крок 2
    f.append(arrow(cx, 200, cx, 244, color=INK, sw=1.8))
    f.append(text(cx - 14, 226, "ні", size=11.5, color=MUTED, anchor="end"))
    b, w2, h2 = textbox(cx, 278, ["ключ (var, lo, hi)", "уже в таблиці ?"], size=13.5,
                        pad=11, min_w=178, fill=FILL, stroke=LINE, bold=True)
    f.append(b)
    f.append(arrow(cx + w2/2, 278, 336, 278, color=POS, sw=1.8))
    f.append(text(cx + w2/2 + 34, 268, "так", size=11.5, color=POS, bold=True))
    b, _, _ = textbox(452, 278, ["правило 2: без дублікатів", "поверни наявний id"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, color=POS)
    f.append(b)

    # крок 3
    f.append(arrow(cx, 308, cx, 352, color=INK, sw=1.8))
    f.append(text(cx - 14, 334, "ні", size=11.5, color=MUTED, anchor="end"))
    b, _, _ = textbox(cx, 386, ["новий id, записати", "ключ у таблицю"], size=13,
                      pad=11, min_w=178, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    f.append(b)
    f.append(text(cx, 452, "лише тут виникає новий вузол", size=11.5, color=MUTED))
    f.append(text(cx, 472, "— тому обидва правила тримаються самі", size=11.5, color=MUTED))

    # ── ПРАВА панель: унікальна таблиця ──
    tx = 800
    f.append(text(tx, 80, "унікальна таблиця для f = a·b + c", size=13, bold=True, color=MUTED))
    rows = [("(c, 0, 1)", "#2"), ("(b, #2, 1)", "#3"), ("(a, #2, #3)", "#4")]
    rw, rh = 300, 44
    y0 = 116
    f.append(text(tx - rw/2 + 66, y0 - 8, "ключ", size=11.5, color=MUTED))
    f.append(text(tx + rw/2 - 52, y0 - 8, "id", size=11.5, color=MUTED))
    for i, (k, v) in enumerate(rows):
        y = y0 + i * (rh + 12)
        f.append(rect(tx - rw/2, y, rw, rh, fill=FILL, stroke=LINE, sw=1.5))
        f.append(line(tx + rw/2 - 96, y, tx + rw/2 - 96, y + rh, color="#d5d9de", sw=1.2))
        f.append(text(tx - rw/2 + 22, y + rh/2 + 5, k, size=13.5, anchor="start", bold=True))
        f.append(text(tx + rw/2 - 48, y + rh/2 + 5, v, size=13.5, color=FIELD,
                      anchor="middle", bold=True))
    f.append(mtext(tx, 300, ["Три записи — і це вже вся діаграма.",
                             "Ключ каже: «яку змінну питаю",
                             "і куди веду за 0 та за 1».",
                             "Однаковий ключ → той самий id,",
                             "хоч би скільки разів його просили."],
                   size=12.5, color=MUTED, lh=1.45))
    f.append(text(tx, 452, "id 0 і 1 — термінали, спільні на весь усесвіт",
                  size=11.5, color=NEG))
    render(os.path.join(OUT, 'make-node-waist.svg'), W, H, *f)


# ── 6. Робота проти результату: 2ⁿ викликів → 18 вузлів ─────────────────────
def fig_calls_vs_nodes():
    W, H = 980, 520
    f = [text(W/2, 28, "Унікальна таблиця стискає результат, а не роботу", size=16.5, bold=True)]
    f.append(text(258, 60, "виклики рекурсії (дерево)", size=13, bold=True, color=MUTED))
    f.append(text(760, 60, "діаграма-результат", size=13, bold=True, color=MUTED))

    # ── ліворуч: дерево викликів ──
    top_y, dy = 92, 66
    levels = [1, 2, 4, 8, 16]
    span = 400
    prev = []
    for li, cnt in enumerate(levels):
        y = top_y + li * dy
        step = span / cnt
        xs = [58 + step/2 + i*step for i in range(cnt)]
        if prev:
            for i, x in enumerate(xs):
                f.append(line(prev[i//2], y - dy + 7, x, y - 7, color="#b9bfc7", sw=1.1))
        r = 7 if li < 3 else 5
        for x in xs:
            f.append(circle(x, y, r, fill=FILL, stroke=LINE, sw=1.3))
        prev = xs
    f.append(text(258, top_y + 4*dy + 34, "… і так до 2²ⁿ листків", size=12, color=MUTED))

    b, _, _ = textbox(258, 424, ["n = 8  (16 змінних)", "131 071 виклик"], size=14,
                      pad=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(b)

    # ── стрілка ──
    f.append(arrow(500, 240, 588, 240, color=INK, sw=2.2))
    b, _, _ = textbox(544, 200, ["унікальна", "таблиця"], size=11, pad=6,
                      fill=BG, stroke=MUTED, color=MUTED)
    f.append(b)

    # ── праворуч: вузька драбинка BDD ──
    lx, rx = 706, 812
    ys = [110, 168, 226, 284]
    for i, y in enumerate(ys):
        f.append(node(lx, y, "x%d" % (i+1), r=15))
        f.append(node(rx, y + 29, "y%d" % (i+1), r=15))
        f.append(branch(lx + 8, y + 12, rx - 10, y + 29 - 12, 1))
        if i < len(ys) - 1:
            f.append(branch(rx - 6, y + 29 + 14, lx + 6, ys[i+1] - 13, 0))
    f.append(text(760, 336, "⋮", size=22, color=MUTED))
    f.append(leaf(706, 372, "0"))
    f.append(leaf(846, 372, "1"))
    f.append(branch(rx + 10, 284 + 29, 838, 360, 1))

    b, _, _ = textbox(768, 424, ["той самий n = 8", "18 вузлів"], size=14,
                      pad=12, fill="#f0f7f1", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)

    f.append(text(W/2, 484, "Діаграма мала — але щоб її дістати згори вниз, рекурсія все одно "
                            "обійшла все дерево входів",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'calls-vs-nodes.svg'), W, H, *f)


# ── 7. Порядок змінних: 2n+2 проти 2ⁿ⁺¹ ─────────────────────────────────────
def fig_order_growth():
    import math
    W, H = 920, 540
    f = [text(W/2, 28, "Той самий вираз, інший порядок: f = x₁·y₁ + … + xₙ·yₙ",
              size=16.5, bold=True)]

    X0, X1 = 132, 700
    Y0, Y1 = 434, 92          # Y0 — низ (4 вузли), Y1 — верх (512)
    LO, HI = 2.0, 9.0         # log₂ від 4 до 512

    def px(n): return X0 + (n - 1) * (X1 - X0) / 7.0
    def py(c): return Y0 + (math.log(c, 2) - LO) * (Y1 - Y0) / (HI - LO)

    # сітка + вісь Y
    for p in range(2, 10):
        y = py(2 ** p)
        f.append(line(X0 - 6, y, X1 + 16, y, color="#e6e9ed", sw=1))
        f.append(text(X0 - 18, y + 4, str(2 ** p), size=11.5, color=MUTED, anchor="end"))
    f.append(line(X0 - 6, Y0, X0 - 6, Y1 - 18, color=LINE, sw=1.5))
    f.append(line(X0 - 6, Y0, X1 + 16, Y0, color=LINE, sw=1.5))
    f.append(text(X0 - 18, Y1 - 34, "вузлів", size=12, color=MUTED, anchor="end", bold=True))
    f.append(text(X0 - 18, Y1 - 18, "(log₂)", size=11, color=MUTED, anchor="end"))

    # вісь X
    for n in range(1, 9):
        f.append(text(px(n), Y0 + 22, str(n), size=12, color=MUTED))
    f.append(text((X0 + X1) / 2, Y0 + 48, "n — кількість пар (змінних удвічі більше)",
                  size=12, color=MUTED))

    # крива «окремо» — 2^(n+1)
    pts = [(px(n), py(2 ** (n + 1))) for n in range(1, 9)]
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=POS, sw=2.4))
    for x, y in pts:
        f.append(circle(x, y, 4.5, fill=POS, stroke=POS, sw=1))

    # крива «чергування» — 2n+2
    pts2 = [(px(n), py(2 * n + 2)) for n in range(1, 9)]
    for i in range(len(pts2) - 1):
        f.append(line(pts2[i][0], pts2[i][1], pts2[i+1][0], pts2[i+1][1], color=FIELD, sw=2.4))
    for x, y in pts2:
        f.append(circle(x, y, 4.5, fill=FIELD, stroke=FIELD, sw=1))

    # підписи кривих
    b, _, _ = textbox(806, py(512) + 4, ["окремо:", "x₁…xₙ, y₁…yₙ", "2ⁿ⁺¹ = 512"],
                      size=12, pad=9, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(b)
    b, _, _ = textbox(806, py(18) - 2, ["чергування:", "x₁,y₁,…,xₙ,yₙ", "2n+2 = 18"],
                      size=12, pad=9, fill="#f0f7f1", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)

    # виноска про розрив при n=8
    f.append(line(px(8) + 8, py(512), px(8) + 8, py(18), color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(px(8) + 20, (py(512) + py(18)) / 2, "×28", size=13, color=MUTED,
                  anchor="start", bold=True))

    f.append(text(W/2, 500, "Одна й та сама функція. Порядок вирішує, чи діаграма росте "
                            "прямою, чи подвоюється на кожному кроці.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'order-growth.svg'), W, H, *f)


# ── 8. Родовід: що саме додавав кожен крок (hist-bdd) ───────────────────────
def fig_bdd_lineage():
    W, H = 1140, 616
    f = [text(W/2, 30, "Тридцять років: що додавав кожен крок", size=17, bold=True)]

    C1X, C1W = 52, 300
    C2X, C2W = 366, 380
    C3X, C3W = 760, 328

    f.append(text(C1X + 14, 74, "рік · хто · де", size=12, color=MUTED, anchor="start", bold=True))
    f.append(text(C2X + 14, 74, "що додав", size=12, color=MUTED, anchor="start", bold=True))
    f.append(text(C3X + 14, 74, "чого ще бракувало", size=12, color=MUTED, anchor="start", bold=True))

    rows = [
        ("1854 · Джордж Буль", "тотожність: f = ¬x·f₀ + x·f₁", "це алгебра, а не структура даних", None),
        ("1937 · Клод Шеннон · MIT", "булева алгебра ↔ релейні схеми", "функція живе як формула", None),
        ("1959 · Ч. Лі · Bell Labs", "форма: ланцюг умовних переходів", "ні порядку, ні скорочень", None),
        ("1976 · Бут (Гент) · Убар (Таллінн)", "машина-виконавець; графи для тестів", "кожен під свою задачу", None),
        ("1978 · Ш. Акерс · GE", "діаграма і сама назва «BDD»", "на одну функцію — багато діаграм", None),
        ("1986 · Рендел Брайант", "порядок + скорочення = канонічність", "ціна: вибір порядку; множення", FIELD),
        ("1990 · Берч · Кларк · Макміллан", "10²⁰ станів: символьна перевірка", "нічого — канон уже був", NEG),
    ]

    y0, rowh, step = 96, 58, 68
    for i, (c1, c2, c3, hl) in enumerate(rows):
        y = y0 + i * step
        fill = FILL
        stroke = "#d5d9de"
        col = INK
        if hl == FIELD:
            fill, stroke, col = "#f0f7f1", FIELD, FIELD
        elif hl == NEG:
            fill, stroke, col = "#eaf0fd", NEG, NEG
        f.append(rect(C1X, y, 1088 - C1X, rowh, fill=fill, stroke=stroke, sw=1.4))
        f.append(text(C1X + 14, y + rowh/2 + 5, c1, size=12, color=col,
                      anchor="start", bold=True))
        f.append(text(C2X + 14, y + rowh/2 + 5, c2, size=12.5, color=col, anchor="start"))
        f.append(text(C3X + 14, y + rowh/2 + 5, c3, size=12.5, color=MUTED if not hl else col,
                      anchor="start"))

    f.append(text(W/2, 594, "Форма з'явилася 1959-го, назва — 1978-го. Бракувало не механізму, "
                            "а запитання, заради якого варто щось заборонити.",
                  size=12.5, color=MUTED))
    render(os.path.join(OUT, 'bdd-lineage.svg'), W, H, *f)


# ── 9. Чому проривом стала заборона (hist-bdd) ──────────────────────────────
def _diag_abc(ox, oy):
    """Діаграма f = a·b + c у порядку a → b → c. ox,oy — зсув."""
    A = (ox, oy); B = (ox + 62, oy + 92); C = (ox - 50, oy + 184)
    L0 = (ox - 90, oy + 280); L1 = (ox + 50, oy + 280)
    g = []
    g.append(branch(A[0] - 9, A[1] + 13, C[0] + 7, C[1] - 17, 0))
    g.append(branch(A[0] + 9, A[1] + 13, B[0] - 8, B[1] - 15, 1))
    g.append(branch(B[0] - 10, B[1] + 13, C[0] + 13, C[1] - 15, 0))
    g.append(branch(B[0] + 5, B[1] + 15, L1[0], L1[1] - 17, 1))
    g.append(branch(C[0] - 8, C[1] + 13, L0[0], L0[1] - 17, 0))
    g.append(branch(C[0] + 9, C[1] + 13, L1[0] - 12, L1[1] - 17, 1))
    g.append(node(*A, "a", r=15)); g.append(node(*B, "b", r=15)); g.append(node(*C, "c", r=15))
    g.append(leaf(*L0, "0")); g.append(leaf(*L1, "1"))
    return g


def _diag_cab(ox, oy):
    """Та сама функція у порядку c → a → b."""
    C = (ox, oy); A = (ox - 50, oy + 92); B = (ox + 8, oy + 184)
    L0 = (ox - 90, oy + 280); L1 = (ox + 70, oy + 280)
    g = []
    g.append(branch(C[0] - 9, C[1] + 13, A[0] + 7, A[1] - 16, 0))
    g.append(branch(C[0] + 9, C[1] + 13, L1[0] - 8, L1[1] - 17, 1))
    g.append(branch(A[0] - 9, A[1] + 13, L0[0], L0[1] - 17, 0))
    g.append(branch(A[0] + 8, A[1] + 14, B[0] - 9, B[1] - 15, 1))
    g.append(branch(B[0] - 10, B[1] + 13, L0[0] + 13, L0[1] - 17, 0))
    g.append(branch(B[0] + 9, B[1] + 13, L1[0] - 10, L1[1] - 17, 1))
    g.append(node(*C, "c", r=15)); g.append(node(*A, "a", r=15)); g.append(node(*B, "b", r=15))
    g.append(leaf(*L0, "0")); g.append(leaf(*L1, "1"))
    return g


def fig_why_order():
    W, H = 1080, 596
    f = [text(W/2, 30, "Чому проривом стала ЗАБОРОНА, а не нова можливість", size=17, bold=True)]

    f.append(line(700, 58, 700, 508, color="#d5d9de", sw=1.4, dash="6,5"))

    # ── ЛІВОРУЧ: до 1986 ──
    f.append(text(370, 78, "Правила Акерса (1978): порядок — на розсуд автора",
                  size=13, color=POS, bold=True))
    f.append(text(200, 106, "порядок a → b → c", size=12, color=MUTED))
    f.append(text(520, 106, "порядок c → a → b", size=12, color=MUTED))
    f.extend(_diag_abc(200, 150))
    f.extend(_diag_cab(520, 150))
    f.append(text(370, 466, "обидві правильні · обидві задають ту саму f = a·b + c",
                  size=12.5, color=MUTED))
    b, _, _ = textbox(370, 500, "два малюнки — одна функція: порівняти не можна",
                      size=12.5, pad=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(b)

    # ── ПРАВОРУЧ: після 1986 ──
    f.append(text(890, 78, "Правило Брайанта (1986): порядок ЗАФІКСОВАНО",
                  size=13, color=FIELD, bold=True))
    f.append(text(890, 106, "a → b → c + обидва скорочення", size=12, color=MUTED))
    f.extend(_diag_abc(890, 150))
    f.append(text(890, 466, "єдина можлива діаграма", size=12.5, color=MUTED))
    b, _, _ = textbox(890, 500, "збіг = та сама функція", size=12.5, pad=11,
                      fill="#f0f7f1", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)

    # легенда
    f.append(line(392, 556, 422, 556, color=Z0, sw=1.7, dash="5,4"))
    f.append(text(430, 560, "гілка 0", size=11.5, color=MUTED, anchor="start"))
    f.append(line(514, 556, 544, 556, color=Z1, sw=1.9))
    f.append(text(552, 560, "гілка 1", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'why-order.svg'), W, H, *f)


if __name__ == "__main__":
    fig_shannon()
    fig_tree_to_bdd()
    fig_lut_tree()
    fig_lut_inside()
    fig_make_node()
    fig_calls_vs_nodes()
    fig_order_growth()
    fig_bdd_lineage()
    fig_why_order()
    print("OK: figures written to", OUT)
