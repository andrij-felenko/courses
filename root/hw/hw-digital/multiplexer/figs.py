# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SEL = "#8e44ad"   # колір лінії вибору


# ── 1. Мультиплексор як поворотний перемикач + символ-коробка ────────────────
def fig_selector():
    W, H = 720, 400
    f = []
    # -- ліворуч: механічна інтуїція (поворотний перемикач) --
    cx, cy, R = 190, 210, 78
    f.append(text(190, 60, "Інтуїція: поворотний перемикач", size=16, bold=True))
    # чотири входи-контакти по дузі ліворуч
    ins = [("D0", 150), ("D1", 190), ("D2", 230), ("D3", 270)]  # кути в градусах
    import math
    for name, ang in ins:
        a = math.radians(ang)
        px, py = cx + R * math.cos(a), cy - R * math.sin(a)
        f.append(circle(px, py, 6, fill="#eaf0fd", stroke=NEG, sw=2))
        f.append(text(px - 34, py + 5, name, size=13, color=NEG, bold=True))
        f.append(line(px - 26, py, px - 6, py, color=MUTED, sw=1.5))
    # вісь і повзунок, що вказує на D1
    f.append(circle(cx, cy, 8, fill=FILL, stroke=INK, sw=2))
    sel_a = math.radians(190)
    tx, ty = cx + (R - 8) * math.cos(sel_a), cy - (R - 8) * math.sin(sel_a)
    f.append(line(cx, cy, tx, ty, color=SEL, sw=4))
    # вихід
    f.append(line(cx, cy, cx, cy + 70, color=INK, sw=2.5))
    f.append(circle(cx, cy + 70, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx + 24, cy + 74, "Y", size=14, color=POS, bold=True))
    f.append(text(cx, cy + 104, "повзунок вибирає ОДИН вхід", size=12, color=MUTED))

    # -- праворуч: символ-коробка з лінією вибору --
    bx, by, bw, bh = 470, 120, 150, 200
    f.append(text(545, 60, "Умовне позначення", size=16, bold=True))
    # трапеція-коробка мультиплексора
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx, by, bx + bw, by + 40, bx + bw, by + bh - 40, bx, by + bh, FILL, LINE))
    f.append(text(bx + bw / 2, by + bh / 2 - 6, "MUX", size=17, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 16, "4 → 1", size=13, color=MUTED))
    # входи D0..D3 ліворуч
    for i, nm in enumerate(["D0", "D1", "D2", "D3"]):
        yy = by + 30 + i * 44
        f.append(line(bx - 40, yy, bx, yy, color=NEG, sw=1.8))
        f.append(text(bx - 50, yy + 5, nm, size=12, color=NEG, bold=True, anchor="end"))
    # вихід Y праворуч
    ym = by + bh / 2
    f.append(line(bx + bw, ym, bx + bw + 40, ym, color=POS, sw=1.8))
    f.append(text(bx + bw + 50, ym + 5, "Y", size=13, color=POS, bold=True, anchor="start"))
    # лінія вибору знизу
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 34, color=SEL, sw=2))
    f.append(text(bx + bw / 2, by + bh + 52, "S1 S0", size=13, color=SEL, bold=True))
    f.append(text(bx + bw / 2, by + bh + 70, "адреса входу", size=11, color=MUTED))

    render(os.path.join(OUT, 'mux-selector.svg'), W, H, *f)


# ── 2. Побудова 2→1 із вентилів ──────────────────────────────────────────────
def fig_gates():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 34, "2→1 мультиплексор із вентилів: Y = (A·S̄) + (B·S)", size=15, bold=True))

    # входи
    f.append(line(60, 90, 130, 90, color=NEG, sw=1.8));  f.append(text(48, 95, "A", size=13, color=NEG, bold=True, anchor="end"))
    f.append(line(60, 250, 130, 250, color=NEG, sw=1.8)); f.append(text(48, 255, "B", size=13, color=NEG, bold=True, anchor="end"))
    f.append(line(60, 170, 100, 170, color=SEL, sw=1.8)); f.append(text(48, 175, "S", size=13, color=SEL, bold=True, anchor="end"))

    # інвертор S̄
    f.append('<polygon points="100,158 100,182 124,170" fill="%s" stroke="%s" stroke-width="1.5"/>' % (FILL, LINE))
    f.append(circle(128, 170, 4, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(112, 200, "НЕ", size=11, color=MUTED))
    # S̄ вгору до верхнього AND, S вниз до нижнього AND
    f.append(line(132, 170, 150, 170, color=SEL, sw=1.6))
    f.append(line(150, 170, 150, 110, color=SEL, sw=1.6)); f.append(line(150, 110, 175, 110, color=SEL, sw=1.6))
    f.append(text(160, 104, "S̄", size=12, color=SEL, bold=True))
    f.append(line(100, 170, 100, 230, color=SEL, sw=1.6)); f.append(line(100, 230, 175, 230, color=SEL, sw=1.6))
    f.append(text(120, 224, "S", size=12, color=SEL, bold=True))
    # A до верхнього AND
    f.append(line(130, 90, 175, 90, color=NEG, sw=1.6))
    # B до нижнього AND
    f.append(line(130, 250, 175, 250, color=NEG, sw=1.6))

    # верхній AND
    def and_gate(x, y, lbl):
        s = ('<path d="M%d %d L%d %d A24 24 0 0 1 %d %d L%d %d Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x, y - 24, x + 20, y - 24, x + 20, y + 24, x, y + 24, FILL, LINE))
        s += text(x + 10, y + 5, "&", size=15, bold=True)
        return s
    f.append(and_gate(175, 100, "&"))   # верхній: A·S̄
    f.append(and_gate(175, 240, "&"))   # нижній: B·S
    # виходи AND до OR
    f.append(line(219, 100, 250, 100, color=LINE, sw=1.6))
    f.append(line(219, 240, 250, 240, color=LINE, sw=1.6))
    f.append(line(250, 100, 250, 150, color=LINE, sw=1.6)); f.append(line(250, 240, 250, 190, color=LINE, sw=1.6))
    f.append(line(250, 150, 300, 150, color=LINE, sw=1.6)); f.append(line(250, 190, 300, 190, color=LINE, sw=1.6))

    # OR
    f.append('<path d="M300 138 Q322 138 344 170 Q322 202 300 202 Q312 170 300 138 Z" fill="%s" stroke="%s" stroke-width="1.6"/>' % (FILL, LINE))
    f.append(text(320, 175, "≥1", size=13, bold=True))
    # вихід Y
    f.append(line(344, 170, 400, 170, color=POS, sw=1.8))
    f.append(circle(400, 170, 5, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(414, 175, "Y", size=14, color=POS, bold=True, anchor="start"))

    # таблиця праворуч
    tx, ty = 470, 90
    f.append(fitbox(tx, ty, 200, 44, "S = 0  →  Y = A", size=14, fill="#eaf0fd", stroke=NEG, bold=True))
    f.append(fitbox(tx, ty + 60, 200, 44, "S = 1  →  Y = B", size=14, fill="#fdecea", stroke=POS, bold=True))
    f.append(text(tx + 100, ty + 140, "S лише перемикає,", size=12, color=MUTED))
    f.append(text(tx + 100, ty + 158, "яке з A/B пройде на Y", size=12, color=MUTED))

    render(os.path.join(OUT, 'mux-gates.svg'), W, H, *f)


# ── 3. Дерево 2→1 → 4→1 та збірна шина ───────────────────────────────────────
def fig_tree():
    W, H = 720, 380
    f = []
    f.append(text(200, 34, "Дерево: три 2→1 дають 4→1", size=15, bold=True))

    def small_mux(x, y, a, b, sel, out_lbl, sel_lbl):
        # маленька трапеція 2→1
        w, h = 46, 70
        f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            x, y, x + w, y + 14, x + w, y + h - 14, x, y + h, FILL, LINE))
        f.append(text(x + w / 2, y + h / 2 + 4, "2→1", size=11, bold=True))
        # входи
        f.append(text(x - 6, y + 22, a, size=11, color=NEG, bold=True, anchor="end"))
        f.append(line(x - 4, y + 18, x, y + 18, color=NEG, sw=1.4))
        f.append(text(x - 6, y + h - 14, b, size=11, color=NEG, bold=True, anchor="end"))
        f.append(line(x - 4, y + h - 18, x, y + h - 18, color=NEG, sw=1.4))
        # вибір
        f.append(line(x + w / 2, y + h, x + w / 2, y + h + 16, color=SEL, sw=1.6))
        f.append(text(x + w / 2, y + h + 30, sel_lbl, size=11, color=SEL, bold=True))
        # вихід
        f.append(line(x + w, y + h / 2, x + w + 24, y + h / 2, color=LINE, sw=1.6))
        return x + w + 24, y + h / 2

    # два верхні 2→1
    o1x, o1y = small_mux(120, 70, "D0", "D1", "S0", "m0", "S0")
    o2x, o2y = small_mux(120, 210, "D2", "D3", "S0", "m1", "S0")
    # фінальний 2→1
    fx, fy = 300, 150
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        fx, fy, fx + 46, fy + 14, fx + 46, fy + 70 - 14, fx, fy + 70, FILL, LINE))
    f.append(text(fx + 23, fy + 39, "2→1", size=11, bold=True))
    # з'єднання виходів верхніх у фінальний
    f.append(line(o1x, o1y, fx, fy + 18, color=LINE, sw=1.6))
    f.append(line(o2x, o2y, fx, fy + 70 - 18, color=LINE, sw=1.6))
    # вибір S1
    f.append(line(fx + 23, fy + 70, fx + 23, fy + 86, color=SEL, sw=1.6))
    f.append(text(fx + 23, fy + 100, "S1", size=11, color=SEL, bold=True))
    # вихід Y
    f.append(line(fx + 46, fy + 35, fx + 90, fy + 35, color=POS, sw=1.8))
    f.append(circle(fx + 90, fy + 35, 5, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(fx + 104, fy + 40, "Y", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(200, 350, "S1 обирає пару, S0 — вхід у парі", size=12, color=MUTED))

    # роздільник
    f.append(line(500, 60, 500, 330, color="#dddddd", sw=1.2, dash="4,4"))

    # -- праворуч: збірна шина трьома tri-state --
    f.append(text(610, 34, "Мультиплексор ⇒ шина", size=15, bold=True))
    busx = 640
    f.append(line(busx, 80, busx, 300, color=INK, sw=3))
    f.append(text(busx + 14, 74, "спільний дріт", size=11, color=MUTED, anchor="start"))
    srcs = [("джерело A", 110), ("джерело B", 190), ("джерело C", 270)]
    for nm, yy in srcs:
        f.append(fitbox(520, yy - 16, 96, 32, nm, size=11, fill=FILL, stroke=LINE))
        # tri-state буфер (трикутник) до шини
        f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            620, yy - 10, 620, yy + 10, 636, yy, FILL, LINE))
        f.append(line(636, yy, busx, yy, color=LINE, sw=1.6))
        # лінія дозволу зверху
        f.append(line(628, yy - 8, 628, yy - 20, color=SEL, sw=1.4))
    f.append(text(628, 60, "лише ОДИН увімкнено", size=11, color=SEL, bold=True))
    f.append(text(610, 322, "решта — у Hi-Z (відпущено)", size=11, color=MUTED))

    render(os.path.join(OUT, 'mux-tree-bus.svg'), W, H, *f)


# ── 4. Розклад Шеннона: 2→1 = розклад за однією змінною ──────────────────────
def fig_shannon():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 32, "Розклад Шеннона за x  =  один 2→1 мультиплексор", size=15, bold=True))

    # формула зверху
    f.append(text(W / 2, 66, "f  =  x̄·f|x=0  +  x·f|x=1", size=17, bold=True, color=INK))

    # трапеція 2→1 у центрі
    bx, by, bw, bh = 300, 110, 120, 150
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx, by, bx + bw, by + 30, bx + bw, by + bh - 30, bx, by + bh, FILL, LINE))
    f.append(text(bx + bw / 2, by + bh / 2 - 4, "2→1", size=16, bold=True))

    # два входи-кофактори ліворуч
    f.append(line(bx - 130, by + 34, bx, by + 34, color=NEG, sw=1.8))
    f.append(fitbox(bx - 220, by + 18, 92, 32, "f|x=0", size=14, fill="#eaf0fd", stroke=NEG, bold=True))
    f.append(text(bx - 174, by + 8, "гілка x=0", size=10, color=MUTED))

    f.append(line(bx - 130, by + bh - 34, bx, by + bh - 34, color=POS, sw=1.8))
    f.append(fitbox(bx - 220, by + bh - 50, 92, 32, "f|x=1", size=14, fill="#fdecea", stroke=POS, bold=True))
    f.append(text(bx - 174, by + bh - 58, "гілка x=1", size=10, color=MUTED))

    # адреса = x знизу
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 34, color=SEL, sw=2.2))
    f.append(text(bx + bw / 2, by + bh + 54, "x", size=16, color=SEL, bold=True))
    f.append(text(bx + bw / 2, by + bh + 72, "керуюча змінна", size=11, color=MUTED))

    # вихід f праворуч
    f.append(line(bx + bw, by + bh / 2, bx + bw + 60, by + bh / 2, color=INK, sw=2))
    f.append(circle(bx + bw + 60, by + bh / 2, 6, fill=FILL, stroke=INK, sw=2))
    f.append(text(bx + bw + 76, by + bh / 2 + 5, "f", size=16, bold=True, anchor="start"))

    # пояснення праворуч
    f.append(text(600, 150, "x=0 → пройде f|x=0", size=12, color=NEG))
    f.append(text(600, 172, "x=1 → пройде f|x=1", size=12, color=POS))
    f.append(text(600, 210, "мультиплексор сам", size=11, color=MUTED))
    f.append(text(600, 226, "робить розгалуження", size=11, color=MUTED))
    f.append(text(600, 242, "«якщо x»", size=11, color=MUTED))

    render(os.path.join(OUT, 'mux-shannon.svg'), W, H, *f)


# ── 5. Рекурсія до листя: 2ⁿ→1 дерево з константами на входах ─────────────────
def fig_recursion():
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 30, "Рекурсія за всіма змінними: дерево 2→1 з константами на листі", size=14, bold=True))

    def node(x, y, sel):
        w, h = 40, 54
        f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.4"/>' % (
            x, y, x + w, y + 11, x + w, y + h - 11, x, y + h, FILL, LINE))
        # мітка керуючої змінної біля вузла
        f.append(text(x + w / 2, y + h + 15, sel, size=11, color=SEL, bold=True))
        return (x, y + 18), (x, y + h - 18), (x + w, y + h / 2)  # верх-вхід, низ-вхід, вихід

    # корінь (керує x1)
    (rt, rb, ro) = node(70, 180, "x1")
    # вихід кореня → f
    f.append(line(ro[0], ro[1], ro[0] + 40, ro[1], color=INK, sw=2))
    f.append(circle(ro[0] + 40, ro[1], 6, fill=FILL, stroke=INK, sw=2))
    f.append(text(ro[0] + 56, ro[1] + 5, "f", size=15, bold=True, anchor="start"))

    # ярус 2 (керує x2): два вузли
    (a_t, a_b, a_o) = node(200, 100, "x2")
    (b_t, b_b, b_o) = node(200, 260, "x2")
    f.append(line(a_o[0], a_o[1], rt[0], rt[1], color=LINE, sw=1.4))
    f.append(line(b_o[0], b_o[1], rb[0], rb[1], color=LINE, sw=1.4))

    # ярус 3 (керує x3): чотири вузли
    ys3 = [60, 140, 220, 300]
    outs3 = []
    for yy in ys3:
        (t3, b3, o3) = node(340, yy, "x3")
        outs3.append((t3, b3, o3))
    # з'єднати ярус3 → ярус2
    f.append(line(outs3[0][2][0], outs3[0][2][1], a_t[0], a_t[1], color=LINE, sw=1.3))
    f.append(line(outs3[1][2][0], outs3[1][2][1], a_b[0], a_b[1], color=LINE, sw=1.3))
    f.append(line(outs3[2][2][0], outs3[2][2][1], b_t[0], b_t[1], color=LINE, sw=1.3))
    f.append(line(outs3[3][2][0], outs3[3][2][1], b_b[0], b_b[1], color=LINE, sw=1.3))

    # листя: 8 констант 0/1 (таблиця істинності) праворуч від ярусу3
    bits = ["1", "0", "0", "1", "1", "1", "0", "1"]
    lx = 430
    bi = 0
    for (t3, b3, o3) in outs3:
        for anchor in (t3, b3):
            v = bits[bi]; bi += 1
            col = POS if v == "1" else NEG
            fillc = "#fdecea" if v == "1" else "#eaf0fd"
            f.append(line(lx, anchor[1], anchor[0], anchor[1], color=col, sw=1.4))
            f.append(circle(lx + 12, anchor[1], 10, fill=fillc, stroke=col, sw=1.6))
            f.append(text(lx + 12, anchor[1] + 5, v, size=13, color=col, bold=True))

    f.append(text(lx + 12, 40, "константи 0/1", size=11, color=MUTED))
    f.append(text(lx + 12, 400, "= стовпчик таблиці істинності f(x1,x2,x3)", size=11, color=MUTED))
    f.append(text(150, 400, "n ярусів → 2ⁿ листків → будь-яка функція n змінних", size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'mux-recursion.svg'), W, H, *f)


# ── 6. Мультиплексор як таблиця відповідей (LUT) для XOR ──────────────────────
def fig_lut():
    W, H = 720, 452
    f = []
    f.append(text(W / 2, 30, "Мультиплексор 8→1 як таблиця істинності: приклад XOR трьох змінних",
                  size=15, bold=True))

    # -- ліворуч: таблиця істинності a,b,c -> a⊕b⊕c --
    tx, ty = 40, 72
    rows = [("000", "0"), ("001", "1"), ("010", "1"), ("011", "0"),
            ("100", "1"), ("101", "0"), ("110", "0"), ("111", "1")]
    rowh = 34
    f.append(text(tx + 58, ty - 12, "адреса a b c", size=12, color=SEL, bold=True))
    f.append(text(tx + 150, ty - 12, "Y", size=12, color=POS, bold=True))
    for i, (adr, val) in enumerate(rows):
        yy = ty + i * rowh
        vc = POS if val == "1" else MUTED
        vf = "#fdecea" if val == "1" else "#eef1f4"
        f.append(fitbox(tx, yy, 116, rowh - 6, "D%d = %s" % (i, adr),
                        size=12, fill=FILL, stroke=LINE, color=INK))
        f.append(fitbox(tx + 126, yy, 40, rowh - 6, val, size=13,
                        fill=vf, stroke=LINE, color=vc, bold=True))

    # -- праворуч: коробка мультиплексора 8→1 --
    bx, by, bw, bh = 380, 64, 150, 300
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx, by, bx + bw, by + 46, bx + bw, by + bh - 46, bx, by + bh, FILL, LINE))
    f.append(text(bx + bw / 2, by + bh / 2 - 6, "MUX", size=16, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 14, "8 → 1", size=12, color=MUTED))

    # входи даних D0..D7 з таблиці -> ліворуч у коробку
    for i, (adr, val) in enumerate(rows):
        yy = ty + i * rowh + (rowh - 6) / 2
        vc = POS if val == "1" else MUTED
        f.append(line(tx + 166, yy, bx, by + 30 + i * ((bh - 60) / 7),
                      color=vc, sw=1.2))
    for i in range(8):
        yy = by + 30 + i * ((bh - 60) / 7)
        f.append(text(bx - 6, yy + 4, "D%d" % i, size=10, color=NEG, anchor="end"))

    # вихід Y праворуч
    ym = by + bh / 2
    f.append(line(bx + bw, ym, bx + bw + 40, ym, color=POS, sw=1.8))
    f.append(circle(bx + bw + 40, ym, 5, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(bx + bw + 54, ym + 5, "Y = a⊕b⊕c", size=12, color=POS, bold=True, anchor="start"))

    # лінії вибору знизу: a b c
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 30, color=SEL, sw=2))
    f.append(text(bx + bw / 2, by + bh + 48, "a  b  c", size=13, color=SEL, bold=True))
    f.append(text(bx + bw / 2, by + bh + 66, "змінні на адресу", size=11, color=MUTED))

    f.append(fitbox(560, 306, 150, 54,
                    "out = data[sel]:\nадреса читає рядок", size=12,
                    fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, 'mux-lut-xor.svg'), W, H, *f)


# ── 7. Економія входів: пара рядків таблиці → один вхід 0/1/c/c̄ ──────────────
def fig_decompose():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 30, "Економія входів: пари рядків таблиці стискають 8→1 до 4→1 з даними 0/1/c",
                  size=14, bold=True))

    tx, ty = 40, 70
    # приклад-функція: більшість голосів maj(a,b,c)
    pairs = [
        ("00", "0", "0", "0"),
        ("01", "0", "1", "c"),
        ("10", "0", "1", "c"),
        ("11", "1", "1", "1"),
    ]
    rowh = 40
    f.append(text(tx + 24, ty - 12, "a b", size=11, color=SEL, bold=True))
    f.append(text(tx + 78, ty - 12, "c=0", size=11, color=MUTED))
    f.append(text(tx + 118, ty - 12, "c=1", size=11, color=MUTED))
    f.append(text(tx + 178, ty - 12, "вхід Dᵢ", size=11, color=FIELD, bold=True))
    for i, (ab, v0, v1, di) in enumerate(pairs):
        yy = ty + i * rowh
        f.append(fitbox(tx, yy, 52, rowh - 8, ab, size=13, fill=FILL, stroke=LINE, bold=True))
        f.append(fitbox(tx + 60, yy, 36, rowh - 8, v0, size=12, fill="#eef1f4", stroke=LINE, color=MUTED))
        f.append(fitbox(tx + 100, yy, 36, rowh - 8, v1, size=12, fill="#eef1f4", stroke=LINE, color=MUTED))
        col = FIELD if di == "c" else (POS if di == "1" else MUTED)
        fillc = "#eef7f0" if di == "c" else ("#fdecea" if di == "1" else "#eef1f4")
        f.append(fitbox(tx + 150, yy, 60, rowh - 8, di, size=13, fill=fillc, stroke=LINE, color=col, bold=True))

    f.append(text(tx + 100, ty + 4 * rowh + 16, "пара рядків з однаковими a,b → один вхід", size=11, color=MUTED))

    # праворуч: 4→1 mux, дані = 0/c/c/1, адреса = a b
    bx, by, bw, bh = 440, 74, 130, 200
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx, by, bx + bw, by + 34, bx + bw, by + bh - 34, bx, by + bh, FILL, LINE))
    f.append(text(bx + bw / 2, by + bh / 2 - 4, "MUX", size=15, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 16, "4 → 1", size=12, color=MUTED))

    din = [("D0", "0", MUTED), ("D1", "c", FIELD), ("D2", "c", FIELD), ("D3", "1", POS)]
    for i, (nm, val, col) in enumerate(din):
        yy = by + 28 + i * ((bh - 56) / 3)
        f.append(line(bx - 30, yy, bx, yy, color=col, sw=1.6))
        f.append(text(bx - 36, yy + 4, "%s=%s" % (nm, val), size=12, color=col, bold=True, anchor="end"))

    ym = by + bh / 2
    f.append(line(bx + bw, ym, bx + bw + 34, ym, color=POS, sw=1.8))
    f.append(text(bx + bw + 44, ym + 5, "Y = maj(a,b,c)", size=12, color=POS, bold=True, anchor="start"))
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 26, color=SEL, sw=2))
    f.append(text(bx + bw / 2, by + bh + 44, "a  b", size=12, color=SEL, bold=True))

    f.append(fitbox(600, 250, 110, 54, "c на вхід —\nтри змінні,\nмалий mux", size=11,
                    fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, 'mux-decompose.svg'), W, H, *f)


if __name__ == '__main__':
    fig_selector()
    fig_gates()
    fig_tree()
    fig_shannon()
    fig_recursion()
    fig_lut()
    fig_decompose()
    print("ok: 7 figures")
