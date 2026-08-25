# -*- coding: utf-8 -*-
"""Фігури теми «Доповняльний код».
svgkit імпортуємо зі scripts/ (не копіюємо); вивід — у ./img/.
Кожна фігура несе ОДНУ ідею; докладні пояснення — у підписах статті, не в полотні."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CELL = 40          # розмір клітинки біта
GAP  = 2           # проміжок між клітинками


def bits(x0, y, value, n=8, hi=None):
    """Рядок із n клітинок-бітів для цілого value.
    hi — індекс розряду (0 = старший), що його підсвітити рамкою; None — без підсвітки.
    Колір клітинки: 1 → червоняста, 0 → синювата (єдина палітра svgkit)."""
    out = []
    for i in range(n):
        b = (value >> (n - 1 - i)) & 1
        cx = x0 + i * (CELL + GAP)
        if b:
            fill, stroke = "#fdecea", POS
            col = POS
        else:
            fill, stroke = "#eaf0fd", NEG
            col = NEG
        sw = 2.6 if hi == i else 1.6
        if hi == i:
            stroke = INK
        out.append(rect(cx, y, CELL, CELL, fill=fill, stroke=stroke, sw=sw, rx=5))
        out.append(text(cx + CELL / 2, y + CELL / 2 + 6, str(b), size=18, color=col, bold=True))
    return "".join(out), x0 + n * (CELL + GAP) - GAP


# ── Фігура 1: знак-величина та дві його халепи ───────────────────────────────
# Ідея малюнка: показати, що «знак у старшому біті» дає ДВА нулі й що побітове
# додавання 5+(−5) не дає нуля. Решта пояснень — у підписі статті.

def fig_problem():
    W, H = 620, 430
    x0 = 150
    parts = []

    parts.append(text(W / 2, 30, "Знак-величина: старший біт — знак", size=17, bold=True))

    # +5 і −5 у знак-величині (єдина різниця — старший біт)
    fr, _ = bits(x0, 60, 0b00000101, hi=0)
    parts.append(text(x0 - 14, 60 + CELL / 2 + 6, "+5", size=15, anchor="end", bold=True))
    parts.append(fr)
    fr, xr = bits(x0, 60 + CELL + 16, 0b10000101, hi=0)
    parts.append(text(x0 - 14, 60 + CELL + 16 + CELL / 2 + 6, "−5", size=15, anchor="end", bold=True))
    parts.append(fr)
    parts.append(text(x0 + CELL / 2, 60 - 10, "знак", size=11, color=MUTED))

    # халепа 1: два нулі
    b1 = fitbox(70, 200, 250, 110,
                "Халепа 1: два нулі\n+0 = 00000000\n−0 = 10000000",
                size=14, fill="#fdecea", stroke=POS, sw=1.6, bold=False)
    parts.append(b1)

    # халепа 2: 5 + (−5) ≠ 0 побітово
    b2 = fitbox(340, 200, 250, 110,
                "Халепа 2: додавання не працює\n5 + (−5) →\n10001010 = −10, не 0",
                size=14, fill="#fdecea", stroke=POS, sw=1.6, bold=False)
    parts.append(b2)

    parts.append(text(W / 2, 350, "Просте для ока — незручне для заліза:",
                      size=13, color=INK, bold=True))
    parts.append(text(W / 2, 372, "два нулі й окремий «знаковий» суматор.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "sign-magnitude.svg"), W, H, *parts)


# ── Фігура 2: рецепт «інвертуй і додай 1» ────────────────────────────────────
# Ідея: показати три рядки бітів (вихідне число, інверсія, +1) і стрілки між
# ними. Це сам алгоритм у дії.

def fig_recipe():
    W, H = 620, 340
    x0 = 175
    parts = []
    parts.append(text(W / 2, 30, "−N: інвертувати всі біти й додати 1", size=17, bold=True))

    y1, y2, y3 = 64, 64 + CELL + 30, 64 + 2 * (CELL + 30)

    fr, xr = bits(x0, y1, 0b00000101)
    parts.append(text(x0 - 14, y1 + CELL / 2 + 6, "+5", size=15, anchor="end", bold=True))
    parts.append(fr)

    fr, _ = bits(x0, y2, 0b11111010)
    parts.append(text(x0 - 14, y2 + CELL / 2 + 6, "~", size=18, anchor="end", bold=True))
    parts.append(fr)

    fr, _ = bits(x0, y3, 0b11111011)
    parts.append(text(x0 - 14, y3 + CELL / 2 + 6, "+1", size=15, anchor="end", bold=True))
    parts.append(fr)

    # стрілки між рядками
    midx = x0 + 4 * (CELL + GAP)
    parts.append(arrow(midx, y1 + CELL + 2, midx, y2 - 2, color=INK, sw=1.8))
    parts.append(text(midx + 14, (y1 + CELL + y2) / 2 + 4, "інверсія", size=11, color=MUTED, anchor="start"))
    parts.append(arrow(midx, y2 + CELL + 2, midx, y3 - 2, color=INK, sw=1.8))
    parts.append(text(midx + 14, (y2 + CELL + y3) / 2 + 4, "+1", size=11, color=MUTED, anchor="start"))

    parts.append(text(xr + 20, y3 + CELL / 2 + 6, "= −5", size=15, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, "invert-add-one.svg"), W, H, *parts)


# ── Фігура 3: коло чисел (одометр) ───────────────────────────────────────────
# Ідея: 4-бітне коло з 16 поділками; верхня половина = від'ємні. ЦЕ серце теми.
# Підпис статті пояснює, чому −N стоїть на 2ⁿ−N.

def fig_circle():
    W, H = 560, 520
    cx, cy, R = 280, 250, 175
    parts = []
    parts.append(text(W / 2, 30, "Коло чисел: 4 біти, 16 позицій", size=17, bold=True))

    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (cx, cy, R, MUTED))

    # 16 значень: 0..7 угорі-праворуч (додатні), 8..15 читаємо як −8..−1
    labels = {0: "0", 1: "+1", 2: "+2", 3: "+3", 4: "+4", 5: "+5", 6: "+6", 7: "+7",
              8: "−8", 9: "−7", 10: "−6", 11: "−5", 12: "−4", 13: "−3", 14: "−2", 15: "−1"}
    for v in range(16):
        a = math.radians(90 - v * 360 / 16)      # 0 угорі, далі за годинниковою
        px = cx + R * math.cos(a)
        py = cy - R * math.sin(a)
        col = FIELD if v <= 7 else POS
        parts.append(circle(px, py, 4.5, fill=col, stroke=col, sw=1))
        lx = cx + (R + 26) * math.cos(a)
        ly = cy - (R + 26) * math.sin(a)
        parts.append(text(lx, ly + 4, labels[v], size=12, color=col, bold=True))
        # двійковий запис трохи далі
        bx = cx + (R + 52) * math.cos(a)
        by = cy - (R + 52) * math.sin(a)
        parts.append(text(bx, by + 4, format(v, "04b"), size=9, color=MUTED))

    # підписи половин усередині
    parts.append(text(cx, cy - 10, "додатні", size=13, color=FIELD, bold=True))
    parts.append(text(cx, cy + 12, "від'ємні", size=13, color=POS, bold=True))
    # межа +7 | −8 (унизу)
    parts.append(text(cx, cy + R - 24, "межа: +7 | −8", size=11, color=MUTED))

    render(os.path.join(IMG, "number-circle.svg"), W, H, *parts)


# ── Фігура 4: віднімання = додавання доповняльного коду ──────────────────────
# Ідея: стовпчик 7 + (−5) з перенесенням за межу байта, який викидають.

def fig_subtraction():
    W, H = 600, 360
    x0 = 200
    parts = []
    parts.append(text(W / 2, 30, "7 − 5 = 7 + (−5) на тому самому суматорі", size=17, bold=True))

    y1, y2, ysum = 70, 70 + CELL + 8, 70 + 2 * (CELL + 8) + 14

    fr, xr = bits(x0, y1, 0b00000111)
    parts.append(text(x0 - 14, y1 + CELL / 2 + 6, "7", size=15, anchor="end", bold=True))
    parts.append(fr)

    fr, _ = bits(x0, y2, 0b11111011)
    parts.append(text(x0 - 14, y2 + CELL / 2 + 6, "+ (−5)", size=14, anchor="end", bold=True))
    parts.append(fr)

    # риска
    parts.append(line(x0 - 36, y2 + CELL + 6, xr, y2 + CELL + 6, color=INK, sw=1.6))

    # сума: 9-й біт переносу окремою клітинкою (відкидаємо) + 8 бітів результату
    carry_x = x0 - (CELL + GAP) - 6
    parts.append(rect(carry_x, ysum, CELL, CELL, fill=BG, stroke=POS, sw=1.6, rx=5))
    parts.append(text(carry_x + CELL / 2, ysum + CELL / 2 + 6, "1", size=18, color=POS, bold=True))
    fr, xr = bits(x0, ysum, 0b00000010)
    parts.append(fr)
    parts.append(text(carry_x + CELL / 2, ysum + CELL + 20, "викинути", size=10, color=POS))
    parts.append(text(xr + 20, ysum + CELL / 2 + 6, "= 2", size=15, color=FIELD, anchor="start", bold=True))

    parts.append(text(W / 2, H - 22, "Перенос за межу байта відкидаємо — лишається 00000010 = 2.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "subtraction-as-addition.svg"), W, H, *parts)


# ── Фігура 5: старший біт як від'ємна вага ───────────────────────────────────
# Ідея: над кожним бітом 11111011 підписати його вагу; старший = −128.
# Сума ваг дає −5. Показує найшвидший спосіб читати доповняльний код.

def fig_range():
    W, H = 620, 340
    n = 8
    value = 0b11111011
    weights = [-128, 64, 32, 16, 8, 4, 2, 1]
    total_x = n * (CELL + GAP) - GAP
    x0 = (W - total_x) / 2
    parts = []
    parts.append(text(W / 2, 30, "Старший біт має від'ємну вагу", size=17, bold=True))

    yb = 90
    # ваги над клітинками
    for i in range(n):
        cx = x0 + i * (CELL + GAP) + CELL / 2
        col = POS if i == 0 else MUTED
        parts.append(text(cx, yb - 12, str(weights[i]), size=12, color=col, bold=(i == 0)))
    fr, _ = bits(x0, yb, value)
    parts.append(fr)

    # сума активних ваг
    parts.append(text(W / 2, yb + CELL + 40,
                      "−128 + 64 + 32 + 16 + 8 + 2 + 1 = −5",
                      size=16, color=INK, bold=True))

    # діапазон
    b = fitbox(80, yb + CELL + 70, W - 160, 96,
               "Діапазон знакового байта: −128 … +127\n"
               "беззнакового: 0 … 255\n"
               "старший біт 0 → читай як завжди; 1 → врахуй −128",
               size=13, fill=FILL, stroke=FIELD, sw=1.6)
    parts.append(b)

    render(os.path.join(IMG, "negative-weight.svg"), W, H, *parts)


fig_problem()
fig_recipe()
fig_circle()
fig_subtraction()
fig_range()
print("SVG figures generated in", IMG)
