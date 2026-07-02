# -*- coding: utf-8 -*-
"""Фігури до статті «Знакове розширення» (book/programming/computer-architecture)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CELL = 26   # ширина клітинки-біта
CH = 30     # висота клітинки-біта


def bitrow(x, y, bits, fills, n_new=0):
    """Ряд бітів; fills — колір заливки під кожним бітом (None = FILL).
    n_new — скільки СТАРШИХ бітів (ліворуч) підсвітити як «дописані»."""
    out = []
    for i, b in enumerate(bits):
        cx = x + i * CELL
        f = fills[i] if fills[i] else FILL
        out.append(rect(cx, y, CELL, CH, fill=f, stroke=LINE, sw=1.2, rx=3))
        out.append(text(cx + CELL / 2, y + CH * 0.68, b, size=15, bold=True))
    return "".join(out)


# ── 1. Ядро: −5 (int8) → int16, старші біти = копія знакового біта ───────────
def fig_extend_core():
    W, H = 720, 360
    e = []
    e.append(text(W / 2, 30, "−5 з 8 бітів у 16: старші вісім — копія знакового біта", size=16, bold=True))

    x8 = 470
    y1 = 70
    b8 = "11111011"
    fills8 = ["#fdecea"] + [None] * 7   # знаковий біт червоним
    e.append(text(x8 - 14, y1 + CH * 0.68, "int8", size=13, color=MUTED, anchor="end"))
    e.append(bitrow(x8, y1, b8, fills8))
    e.append(text(x8 + 8 * CELL + 14, y1 + CH * 0.68, "= −5", size=14, bold=True, anchor="start"))
    # підпис знакового біта
    e.append(text(x8 + CELL / 2, y1 - 8, "знак", size=11, color=POS, anchor="middle"))

    # стрілка вниз
    e.append(arrow(W / 2, y1 + CH + 8, W / 2, y1 + CH + 40, color=NEG, sw=2))
    e.append(text(W / 2 + 130, y1 + CH + 32, "розширення знаку", size=12, color=NEG, anchor="middle"))

    x16 = 250
    y2 = 160
    b16 = "1111111111111011"
    fills16 = ["#fdecea"] * 8 + [None] * 8   # дописані 8 старших — рожеві
    e.append(text(x16 - 14, y2 + CH * 0.68, "int16", size=13, color=MUTED, anchor="end"))
    e.append(bitrow(x16, y2, b16, fills16))
    e.append(text(x16 + 16 * CELL + 14, y2 + CH * 0.68, "= −5", size=14, bold=True, anchor="start"))
    # дужка над дописаними
    bx0 = x16
    bx1 = x16 + 8 * CELL
    e.append(line(bx0, y2 - 10, bx1, y2 - 10, color=POS, sw=1.5))
    e.append(text((bx0 + bx1) / 2, y2 - 16, "8 копій знаку", size=11, color=POS, anchor="middle"))

    # чому значення те саме — виведення ваги
    yb = 250
    box = fitbox(70, yb, W - 140, 90,
                 "Чому −5 не змінилось: у 16 бітах старший важить −32768.\n"
                 "−32768 + 16384 + 8192 + … + 8 + 2 + 1  =  −5   (той самий −5).\n"
                 "Довгий «хвіст» одиниць ліворуч сам себе гасить.",
                 size=13, fill="#eef7f0", stroke=FIELD)
    e.append(box)
    return render(os.path.join(IMG, "extend-core.svg"), W, H, *e)


# ── 2. Дві заливки: той самий байт 0xFB → нуль-розширення vs знакове ──────────
def fig_two_flavors():
    W, H = 720, 380
    e = []
    e.append(text(W / 2, 30, "Той самий байт 11111011 — два тлумачення при розширенні", size=16, bold=True))

    x8 = W / 2 - 4 * CELL
    y0 = 58
    e.append(bitrow(x8, y0, "11111011", [None] * 8))
    e.append(text(W / 2, y0 - 8, "8 бітів у пам'яті: 0xFB", size=12, color=MUTED))

    # 16-бітні результати — по центру, один під одним
    x16 = W / 2 - 8 * CELL
    yU = 150   # unsigned → zero-extend
    yS = 250   # signed → sign-extend

    e.append(arrow(W / 2, y0 + CH + 4, W / 2, yU - 8, color=NEG, sw=1.6))

    e.append(text(x16, yU - 10, "uint8_t → нуль-розширення", size=12, color=NEG, bold=True, anchor="start"))
    e.append(bitrow(x16, yU, "0000000011111011", ["#eaf0fd"] * 8 + [None] * 8))
    e.append(text(x16 + 16 * CELL + 12, yU + CH * 0.68, "= +251", size=15, bold=True, color=NEG, anchor="start"))

    e.append(text(x16, yS - 10, "int8_t → знакове розширення", size=12, color=POS, bold=True, anchor="start"))
    e.append(bitrow(x16, yS, "1111111111111011", ["#fdecea"] * 8 + [None] * 8))
    e.append(text(x16 + 16 * CELL + 12, yS + CH * 0.68, "= −5", size=15, bold=True, color=POS, anchor="start"))

    e.append(fitbox(60, 306, W - 120, 56,
                    "Біти в пам'яті однакові. Вирішує ТИП: беззнаковий дописує нулі, "
                    "знаковий — копії старшого біта. Одна помилка в типі — інше число.",
                    size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, "two-flavors.svg"), W, H, *e)


# ── 3. Ручне розширення 12-бітного знакового поля давача ─────────────────────
def fig_manual_12bit():
    W, H = 720, 340
    e = []
    e.append(text(W / 2, 30, "12-бітне знакове з давача в 16-бітному слові", size=16, bold=True))

    x = W / 2 - 8 * CELL
    y0 = 66
    # сире: старші 4 нулі, 12 значущих (візьмемо від'ємне: біт11 = 1)
    raw = "0000" + "101111111011"
    fillsraw = ["#eef7f0"] * 4 + [None] * 12
    e.append(bitrow(x, y0, raw, fillsraw))
    e.append(text(x - 12, y0 + CH * 0.68, "сире", size=12, color=MUTED, anchor="end"))
    # позначки
    e.append(line(x, y0 - 10, x + 4 * CELL, y0 - 10, color=FIELD, sw=1.5))
    e.append(text(x + 2 * CELL, y0 - 16, "0 (сміття)", size=11, color=FIELD, anchor="middle"))
    e.append(text(x + 4 * CELL + CELL / 2, y0 - 16, "біт 11 = знак", size=11, color=POS, anchor="middle"))
    e.append(line(x + 4 * CELL, y0 - 10, x + 5 * CELL, y0 - 10, color=POS, sw=1.5))

    e.append(arrow(W / 2, y0 + CH + 6, W / 2, y0 + CH + 36, color=NEG, sw=2))
    e.append(text(W / 2 + 175, y0 + CH + 30, "(v ^ 0x0800) − 0x0800", size=12, color=NEG, anchor="middle"))

    y1 = 158
    fixed = "1111" + "101111111011"
    fillsfix = ["#fdecea"] * 4 + [None] * 12
    e.append(bitrow(x, y1, fixed, fillsfix))
    e.append(text(x - 12, y1 + CH * 0.68, "готове", size=12, color=MUTED, anchor="end"))
    e.append(line(x, y1 + CH + 10, x + 4 * CELL, y1 + CH + 10, color=POS, sw=1.5))
    e.append(text(x + 2 * CELL, y1 + CH + 24, "4 копії знаку", size=11, color=POS, anchor="middle"))

    e.append(fitbox(70, 258, W - 140, 60,
                    "Давач дав 12 значущих бітів; старші 4 — нулі, тож −N виглядає як велике +.\n"
                    "Маска-віднімання «довертає» знак: якщо біт 11 стоїть, старші стають одиницями.",
                    size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, "manual-12bit.svg"), W, H, *e)


if __name__ == "__main__":
    print(fig_extend_core())
    print(fig_two_flavors())
    print(fig_manual_12bit())
