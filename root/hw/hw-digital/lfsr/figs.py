# -*- coding: utf-8 -*-
"""Фігури до теми «LFSR — лінійний регістр зі зворотним зв'язком».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def cell(x, y, w, h, label):
    """Одна комірка тригера з підписом-номером."""
    out = rect(x, y, w, h, fill="#eef2f7", stroke=LINE, sw=1.6, rx=5)
    out += text(x + w / 2, y + h / 2 + 6, label, size=17, bold=True)
    return out


def xor_node(cx, cy, r=15):
    """Вузол XOR — коло зі знаком ⊕."""
    out = circle(cx, cy, r, fill="#fdf0ea", stroke=POS, sw=2.2)
    out += text(cx, cy + r * 0.45, "⊕", size=int(r * 1.5), color=POS, bold=True)
    return out


# ── Фігура 1. Будова LFSR: 4 комірки + XOR-зворотний зв'язок ─────────────────
def fig_structure():
    W, H = 720, 300
    cw, ch = 92, 66
    gap = 26
    y = 96
    x0 = 70
    labels = ["b3", "b2", "b1", "b0"]  # зліва (старший) → праворуч (молодший)
    frags = []

    # Такт зверху
    frags.append(text(W / 2, 40, "спільний такт — усі комірки зсуваються разом",
                      size=13, color=MUTED))

    xs = []
    for i, lab in enumerate(labels):
        x = x0 + i * (cw + gap)
        xs.append(x)
        frags.append(cell(x, y, cw, ch, lab))

    # Зсув: стрілки між комірками (біт їде праворуч)
    for i in range(len(xs) - 1):
        x1 = xs[i] + cw
        x2 = xs[i + 1]
        frags.append(arrow(x1, y + ch / 2, x2, y + ch / 2, color=INK, sw=2))

    # Вихід справа
    rout = xs[-1] + cw
    frags.append(line(rout, y + ch / 2, rout + 46, y + ch / 2, color=INK, sw=2))
    frags.append(text(rout + 70, y + ch / 2 + 5, "вихід", size=13, color=INK))

    # Відводи (tap) від b3 і b0 → XOR → назад у вхід зліва
    xor_x = x0 - 4
    xor_y = y + ch + 78
    frags.append(xor_node(xor_x, xor_y))

    # відвід від b0 (найправіший): униз і ліворуч до XOR
    b0x = xs[-1] + cw / 2
    frags.append(circle(b0x, y + ch, 3.5, fill=POS, stroke=POS))  # точка відводу
    frags.append(line(b0x, y + ch, b0x, xor_y, color=POS, sw=2))
    frags.append(line(b0x, xor_y, xor_x + 16, xor_y, color=POS, sw=2))

    # відвід від b3 (лівіший тап): вниз і до XOR
    b3x = xs[0] + cw / 2 + 30
    frags.append(circle(b3x, y + ch, 3.5, fill=POS, stroke=POS))
    frags.append(line(b3x, y + ch, b3x, xor_y - 30, color=POS, sw=2))
    frags.append(line(b3x, xor_y - 30, xor_x, xor_y - 30, color=POS, sw=2))
    frags.append(line(xor_x, xor_y - 30, xor_x, xor_y - 15, color=POS, sw=2))

    # XOR → вхід зліва (у комірку b3)
    frags.append(line(xor_x, xor_y + 15, xor_x, y + ch + 20, color=NEG, sw=2))
    frags.append(arrow(xor_x, y + ch + 20, xs[0] + cw / 2 - 8, y + ch, color=NEG, sw=2))

    frags.append(text(b3x + 74, y + ch + 34, "відводи (tap)", size=12, color=POS))
    frags.append(text(xor_x + 150, xor_y + 5,
                      "новий біт = b3 ⊕ b0  →  заходить зліва", size=13, color=NEG))

    render(os.path.join(IMG, "structure.svg"), W, H, *frags)


# ── Фігура 2. Кільце з 15 станів (m-послідовність x^4+x+1) ────────────────────
def fig_cycle():
    import math
    W, H = 620, 620
    cx, cy, R = W / 2, H / 2, 232

    # Порядок станів для x^4+x+1, зсув ліворуч, fb=b3^b0, seed=0001
    states = [0b0001, 0b0011, 0b0111, 0b1111, 0b1110, 0b1101, 0b1010, 0b0101,
              0b1011, 0b0110, 0b1100, 0b1001, 0b0010, 0b0100, 0b1000]
    n = len(states)
    frags = []

    pts = []
    for i, s in enumerate(states):
        ang = -math.pi / 2 + 2 * math.pi * i / n  # старт зверху, за годинником
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        pts.append((x, y))

    # стрілки по колу
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        # скоротити, щоб стрілка не залазила у вузли
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        frags.append(arrow(x1 + ux * 26, y1 + uy * 26,
                           x2 - ux * 26, y2 - uy * 26, color=MUTED, sw=1.6))

    # вузли
    for i, (x, y) in enumerate(pts):
        col = FIELD if i == 0 else "#eef2f7"
        frags.append(circle(x, y, 24, fill=col, stroke=LINE, sw=1.6))
        frags.append(text(x, y + 5, format(states[i], "04b"), size=13, bold=(i == 0)))

    # центр
    frags.append(text(cx, cy - 12, "15 станів", size=20, bold=True))
    frags.append(text(cx, cy + 12, "рівно 2⁴ − 1", size=15, color=MUTED))
    frags.append(text(cx, cy + 40, "0000 — поза кільцем", size=13, color=POS))

    render(os.path.join(IMG, "cycle.svg"), W, H, *frags)


# ── Фігура 3. Fibonacci проти Galois ─────────────────────────────────────────
def fig_fib_galois():
    W, H = 720, 340
    cw, ch = 78, 54
    gap = 20
    x0 = 78
    frags = []

    # ── Верх: Fibonacci ──
    yf = 78
    frags.append(text(x0 - 10, yf - 20, "Фібоначчі: один XOR збирає відводи ПЕРЕД входом",
                      size=13, bold=True, anchor="start"))
    xs = []
    for i in range(4):
        x = x0 + i * (cw + gap)
        xs.append(x)
        frags.append(cell(x, yf, cw, ch, ["b3", "b2", "b1", "b0"][i]))
        if i < 3:
            frags.append(arrow(x + cw, yf + ch / 2, xs[i] + cw + gap, yf + ch / 2,
                               color=INK, sw=1.8))
    # один XOR перед b3
    xf = x0 - 40
    yxor = yf + ch / 2
    frags.append(xor_node(xf, yxor, r=13))
    frags.append(arrow(xf + 13, yxor, x0 - 2, yxor, color=NEG, sw=1.8))
    # відводи від b0 і b3 у цей XOR
    b0x = xs[-1] + cw / 2
    b3x = xs[0] + cw / 2
    frags.append(circle(b0x, yf + ch, 3, fill=POS, stroke=POS))
    frags.append(line(b0x, yf + ch, b0x, yf + ch + 24, color=POS, sw=1.6))
    frags.append(line(b0x, yf + ch + 24, xf, yf + ch + 24, color=POS, sw=1.6))
    frags.append(line(xf, yf + ch + 24, xf, yxor + 13, color=POS, sw=1.6))
    frags.append(circle(b3x, yf + ch, 3, fill=POS, stroke=POS))
    frags.append(line(b3x, yf + ch, b3x, yf + ch + 10, color=POS, sw=1.6))
    frags.append(line(b3x, yf + ch + 10, xf, yf + ch + 10, color=POS, sw=1.6))
    frags.append(line(xf, yf + ch + 10, xf, yxor - 13, color=POS, sw=1.6))

    # ── Низ: Galois ──
    yg = 244
    frags.append(text(x0 - 10, yg - 20, "Галуа: XOR стоять МІЖ комірками, на шляху зсуву",
                      size=13, bold=True, anchor="start"))
    xs2 = []
    for i in range(4):
        x = x0 + i * (cw + gap)
        xs2.append(x)
        frags.append(cell(x, yg, cw, ch, ["b3", "b2", "b1", "b0"][i]))
    # зсув праворуч між комірками; XOR вбудований на одному з переходів (між b1 і b0)
    for i in range(3):
        x1 = xs2[i] + cw
        x2 = xs2[i + 1]
        midx = (x1 + x2) / 2
        if i == 2:  # вставити XOR у цей перехід (керує біт зворотного зв'язку)
            frags.append(line(x1, yg + ch / 2, midx - 12, yg + ch / 2, color=INK, sw=1.8))
            frags.append(xor_node(midx, yg + ch / 2, r=11))
            frags.append(arrow(midx + 11, yg + ch / 2, x2, yg + ch / 2, color=INK, sw=1.8))
        else:
            frags.append(arrow(x1, yg + ch / 2, x2, yg + ch / 2, color=INK, sw=1.8))
    # зворотний зв'язок від b0 (вихід) угору й назад у ланцюг та в XOR
    outx = xs2[-1] + cw
    fbY = yg + ch + 26
    frags.append(circle(outx, yg + ch / 2, 3, fill=POS, stroke=POS))
    frags.append(line(outx, yg + ch / 2, outx + 30, yg + ch / 2, color=INK, sw=1.8))
    frags.append(text(outx + 54, yg + ch / 2 + 5, "вихід", size=12))
    frags.append(line(outx, yg + ch / 2, outx, fbY, color=POS, sw=1.6))
    frags.append(line(outx, fbY, xs2[0] + cw / 2, fbY, color=POS, sw=1.6))
    frags.append(arrow(xs2[0] + cw / 2, fbY, xs2[0] + cw / 2, yg + ch, color=POS, sw=1.6))
    # відгалуження у вбудований XOR
    xrx = (xs2[2] + cw + xs2[3]) / 2
    frags.append(line(xrx, fbY, xrx, yg + ch, color=POS, sw=1.6))
    frags.append(circle(xrx, fbY, 3, fill=POS, stroke=POS))

    frags.append(text(W / 2, H - 12,
                      "той самий многочлен x⁴+x+1, ті самі 15 станів — лише інша розкладка",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "fib-galois.svg"), W, H, *frags)


# ── Фігура 4. Родовід m-послідовності: від алгебри Галуа до книги 1967 ────────
def fig_lineage():
    """Часова смуга: чужа математика й воєнні трюки сходяться в теорію Голомба."""
    W, H = 760, 380
    axisY = 118
    x0, x1 = 60, W - 60
    frags = []

    frags.append(text(W / 2, 34,
                      "поняття не з'явилося на порожньому місці", size=15, bold=True))
    frags.append(text(W / 2, 54,
                      "стара алгебра + воєнні трюки → струнка теорія", size=12, color=MUTED))

    # горизонтальна вісь часу
    frags.append(line(x0, axisY, x1, axisY, color=LINE, sw=2))
    frags.append(arrow(x1 - 2, axisY, x1 + 2, axisY, color=LINE, sw=2))

    # віхи: (частка вздовж осі 0..1, рік, підпис, вгору/вниз, колір рамки)
    marks = [
        (0.00, "1830-ті", ["Галуа: скінченні", "поля, многочлени"], +1, NEG),
        (0.30, "1940-ві", ["воєнний «шум»:", "радар, глушіння"], -1, MUTED),
        (0.50, "1954-55", ["Голомб зводить", "у теорію + звіт"], +1, POS),
        (0.72, "1961", ["радар Венери:", "далекомір по коду"], -1, FIELD),
        (1.00, "1967", ["книга Shift", "Register Sequences"], +1, POS),
    ]
    for frac, year, lines, updown, col in marks:
        cx = x0 + (x1 - x0) * frac
        # тримати рамки в межах полотна
        cx = max(x0 + 66, min(x1 - 66, cx))
        frags.append(circle(cx, axisY, 5, fill=col, stroke=col))
        frags.append(text(cx, axisY + (26 if updown < 0 else -14),
                          year, size=13, bold=True, color=col))
        boxcy = axisY + updown * 86
        body, bw, bh = textbox(cx, boxcy, "\n".join(lines), size=12, pad=8,
                               stroke=col, fill="#ffffff")
        # ніжка від осі до рамки
        edge = boxcy - updown * bh / 2
        frags.append(line(cx, axisY + updown * 40, cx, edge, color=col, sw=1.4, dash="3 3"))
        frags.append(body)

    frags.append(text(W / 2, H - 16,
                      "жоден крок не «винахід однієї людини» — Голомб дав мову й лад",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "lineage.svg"), W, H, *frags)


# ── Фігура 5 (math-max-length). Стан ↔ многочлен ─────────────────────────────
def fig_state_poly():
    """Той самий 4-бітний стан у двох записах: біти та многочлен над GF(2)."""
    W, H = 720, 300
    cw, ch = 92, 60
    gap = 22
    x0 = 130
    y = 96
    bits = ["1", "0", "1", "1"]        # b3 b2 b1 b0
    powers = ["x³", "x²", "x", "1"]
    frags = []

    frags.append(text(W / 2, 40, "той самий стан — два записи", size=16, bold=True))

    xs = []
    for i in range(4):
        x = x0 + i * (cw + gap)
        xs.append(x)
        frags.append(cell(x, y, cw, ch, bits[i]))
        # підпис позиції над коміркою
        frags.append(text(x + cw / 2, y - 12, ["b3", "b2", "b1", "b0"][i],
                          size=12, color=MUTED))
        # степінь під коміркою
        frags.append(text(x + cw / 2, y + ch + 24, "· " + powers[i], size=15, color=NEG))
        # вертикальна стрілка «біт → коефіцієнт»
        frags.append(arrow(x + cw / 2, y + ch + 2, x + cw / 2, y + ch + 8, color=MUTED, sw=1.4))

    # ліворуч підпис ряду бітів
    frags.append(text(x0 - 18, y + ch / 2 + 5, "біти", size=13, color=INK, anchor="end"))
    frags.append(text(x0 - 18, y + ch + 24, "як многочлен", size=13, color=NEG, anchor="end"))

    # підсумковий рядок-многочлен
    frags.append(text(W / 2, y + ch + 78,
                      "1·x³ + 0·x² + 1·x + 1   =   x³ + x + 1", size=18, bold=True))
    frags.append(text(W / 2, y + ch + 104,
                      "коефіцієнт при xᵏ — це біт на позиції k (коефіцієнти лише 0 і 1)",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "state-poly.svg"), W, H, *frags)


# ── Фігура 6 (math-max-length). Дільники 15 як щаблі порядку x ────────────────
def fig_order_divisors():
    """Порядок x мусить ділити 15 → лише щаблі 1, 3, 5, 15; примітивний = верх."""
    W, H = 640, 380
    frags = []

    frags.append(text(W / 2, 38, "довжина циклу = порядок x", size=16, bold=True))
    frags.append(text(W / 2, 58, "а він мусить ділити 2⁴ − 1 = 15  (теорема Лагранжа)",
                      size=12, color=MUTED))

    # щаблі знизу вгору: 1, 3, 5, 15
    steps = [("1", "вироджений: x = 1", MUTED),
             ("3", "коротка петля", MUTED),
             ("5", "незвідний, та НЕ примітивний", POS),
             ("15", "примітивний — повний обхід", FIELD)]
    baseY = 320
    dy = 66
    bx = 90
    bw = 70
    bh = 40
    cxlab = bx + bw + 24
    for i, (val, note, col) in enumerate(steps):
        y = baseY - i * dy
        frags.append(fitbox(bx, y - bh / 2, bw, bh, val, size=20, bold=True,
                            fill="#ffffff", stroke=col))
        frags.append(text(cxlab, y + 5, note, size=13, color=col, anchor="start"))
        # стрілка «вгору за порядком»
        if i < len(steps) - 1:
            frags.append(arrow(bx + bw / 2, y - bh / 2, bx + bw / 2, y - dy + bh / 2,
                               color=MUTED, sw=1.4))

    # вертикальна вісь-підказка
    frags.append(text(bx + bw / 2, baseY + 34, "дозволені лише ці 4 значення",
                      size=12, color=MUTED))
    frags.append(text(46, baseY - 1.5 * dy, "порядок x", size=12, color=INK,
                      anchor="middle"))

    render(os.path.join(IMG, "order-divisors.svg"), W, H, *frags)


# ── Фігура 7 (math-max-length). Дерево перевірки примітивності ────────────────
def fig_primitivity_test():
    """Два кроки перевірки + контрприклад, де x⁵=1 обриває на «не примітивний»."""
    W, H = 760, 420
    frags = []

    frags.append(text(W / 2, 34, "перевірка примітивності — у два кроки", size=16, bold=True))

    # ── Ліва колонка: x^4 + x + 1 (примітивний) ──
    lx = 190
    frags.append(text(lx, 70, "x⁴ + x + 1", size=17, bold=True))

    b1, _, _ = textbox(lx, 118, "1. незвідний?", size=13, pad=8, stroke=NEG, fill="#ffffff")
    frags.append(b1)
    frags.append(text(lx, 150, "p(1)=1, не ділиться на", size=11, color=MUTED))
    frags.append(text(lx, 165, "x, x+1, x²+x+1  →  так", size=11, color=MUTED))
    frags.append(arrow(lx, 175, lx, 196, color=LINE, sw=1.6))

    b2, _, _ = textbox(lx, 220, "2. порядок = 15?", size=13, pad=8, stroke=NEG, fill="#ffffff")
    frags.append(b2)
    # два кандидати
    frags.append(text(lx, 258, "15/3 → x⁵ = x²+x ≠ 1  ✓", size=12, color=FIELD))
    frags.append(text(lx, 276, "15/5 → x³ = x³   ≠ 1  ✓", size=12, color=FIELD))
    frags.append(arrow(lx, 286, lx, 308, color=FIELD, sw=1.8))

    v1, _, _ = textbox(lx, 336, "ПРИМІТИВНИЙ\nцикл = 15", size=14, pad=10,
                       stroke=FIELD, fill="#eafaf0", bold=True, color=FIELD)
    frags.append(v1)

    # роздільник
    frags.append(line(W / 2, 60, W / 2, H - 40, color=MUTED, sw=1, dash="4 4"))

    # ── Права колонка: x^4 + x^3 + x^2 + x + 1 (контрприклад) ──
    rx = 560
    frags.append(text(rx, 70, "x⁴+x³+x²+x+1", size=17, bold=True))

    r1, _, _ = textbox(rx, 118, "1. незвідний?", size=13, pad=8, stroke=NEG, fill="#ffffff")
    frags.append(r1)
    frags.append(text(rx, 150, "теж незвідний  →  так", size=11, color=MUTED))
    frags.append(arrow(rx, 165, rx, 196, color=LINE, sw=1.6))

    r2, _, _ = textbox(rx, 220, "2. порядок = 15?", size=13, pad=8, stroke=NEG, fill="#ffffff")
    frags.append(r2)
    frags.append(text(rx, 258, "(x+1)·q = x⁵+1  →  x⁵ = 1", size=12, color=POS))
    frags.append(text(rx, 276, "кандидат 15/3 спрацював!", size=12, color=POS))
    frags.append(arrow(rx, 286, rx, 308, color=POS, sw=1.8))

    v2, _, _ = textbox(rx, 336, "НЕ примітивний\nпорядок = 5", size=14, pad=10,
                       stroke=POS, fill="#fdecea", bold=True, color=POS)
    frags.append(v2)

    render(os.path.join(IMG, "primitivity-test.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_structure()
    fig_cycle()
    fig_fib_galois()
    fig_lineage()
    fig_state_poly()
    fig_order_divisors()
    fig_primitivity_test()
    print("OK: structure, cycle, fib-galois, lineage, state-poly, order-divisors, primitivity-test")
