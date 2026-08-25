# -*- coding: utf-8 -*-
"""Фігури до вставки «74HC165» (тека теми 74HC595).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
УВАГА: пише лише файли hc165-*.svg; старі fig-16-* не чіпає."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
#  1. Дзеркало: де саме стоїть «момент» у SIPO і в PISO
# ════════════════════════════════════════════════════════════════════════════
def fig_mirror():
    W, H = 940, 620
    f = []

    # ── Верхній ряд: SIPO, момент на виході ─────────────────────────────────
    f.append(text(40, 60, "SIPO (74HC595): біти всередину по одному, назовні — всі разом",
                  size=16, bold=True, anchor="start"))
    y1 = 155
    f.append(mtext(110, 146, ["один дріт", "від МК"], size=12, color=MUTED))
    f.append(arrow(178, y1, 214, y1))
    f.append(fitbox(215, 112, 210, 86, "зсувний регістр\n8 тригерів", size=15))
    f.append(arrow(428, y1, 464, y1))
    f.append(fitbox(465, 112, 210, 86, "вихідний латч\n8 тригерів", size=15))
    for i in range(8):
        yy = 120 + i * 10
        f.append(line(677, yy, 726, yy, color=LINE, sw=1.4))
    f.append(mtext(800, 146, ["вісім паралельних", "виходів"], size=12, color=MUTED))

    f.append(arrow(570, 246, 570, 202, color=FIELD, sw=2.2))
    f.append(mtext(570, 268, ["RCLK — момент ПОКАЗУ:",
                              "латч віддає готовий байт на виходи"], size=13, color=FIELD))

    f.append(line(40, 318, 900, 318, color=MUTED, sw=1.2, dash="7 6"))

    # ── Нижній ряд: PISO, момент на вході ───────────────────────────────────
    f.append(text(40, 355, "PISO (74HC165): усі разом усередину, назовні — по одному",
                  size=16, bold=True, anchor="start"))
    y2 = 442
    for i in range(8):
        yy = 407 + i * 10
        f.append(line(176, yy, 224, yy, color=LINE, sw=1.4))
    f.append(mtext(103, 428, ["вісім", "паралельних", "входів"], size=12, color=MUTED))
    f.append(fitbox(225, 399, 450, 86,
                    "той самий зсувний регістр — 8 тригерів\n"
                    "паралельні дані вливаються просто в них", size=15))
    f.append(arrow(678, y2, 742, y2))
    f.append(mtext(818, 428, ["один дріт Q7", "до МК"], size=12, color=MUTED))

    f.append(arrow(450, 548, 450, 490, color=FIELD, sw=2.2))
    f.append(mtext(450, 572, ["PL — момент ЗНІМКА:",
                              "вісім входів фіксуються разом, ще до зсуву"],
                   size=13, color=FIELD))

    render(os.path.join(IMG, 'hc165-mirror.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  2. Цоколівка DIP-16
# ════════════════════════════════════════════════════════════════════════════
def fig_pinout():
    W, H = 760, 540
    f = []
    bx, by, bw, bh = 280, 95, 200, 390
    f.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE, sw=2, rx=8))
    # виїмка «ключа» зверху
    f.append('<path d="M 366 95 A 14 14 0 0 0 394 95" fill="%s" stroke="%s" '
             'stroke-width="2"/>' % (BG, LINE))

    ys = [135 + i * 45 for i in range(8)]

    left = [("1", "PL (SH/LD)", True), ("2", "CP (CLK)", True), ("3", "D4 (E)", False),
            ("4", "D5 (F)", False), ("5", "D6 (G)", False), ("6", "D7 (H)", False),
            ("7", "Q7n", False), ("8", "GND", False)]
    right = [("16", "VCC", False), ("15", "CE (CLK INH)", False), ("14", "D3 (D)", False),
             ("13", "D2 (C)", False), ("12", "D1 (B)", False), ("11", "D0 (A)", False),
             ("10", "DS (SER)", False), ("9", "Q7 (QH)", True)]

    for (num, name, hot), yy in zip(left, ys):
        col = FIELD if hot else LINE
        f.append(line(248, yy, bx, yy, color=col, sw=2.2 if hot else 1.6))
        f.append(text(bx + 12, yy + 4, num, size=12, color=MUTED, anchor="start"))
        f.append(text(242, yy + 4, name, size=14, color=col,
                      anchor="end", bold=hot))
    for (num, name, hot), yy in zip(right, ys):
        col = FIELD if hot else LINE
        f.append(line(bx + bw, yy, 512, yy, color=col, sw=2.2 if hot else 1.6))
        f.append(text(bx + bw - 12, yy + 4, num, size=12, color=MUTED, anchor="end"))
        f.append(text(518, yy + 4, name, size=14, color=col,
                      anchor="start", bold=hot))

    f.append(text(bx + bw / 2, 292, "74HC165", size=18, bold=True))
    f.append(text(W / 2, 518,
                  "зелені — три лінії до мікроконтролера; решта — входи, каскад і живлення",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'hc165-pinout.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  3. Ланцюг: більше входів — ті самі три лінії
# ════════════════════════════════════════════════════════════════════════════
def fig_chain():
    W, H = 900, 380
    f = []
    f.append(fitbox(40, 100, 150, 210, "мікро-\nконтролер", size=15))

    xs = [300, 500, 700]
    names = ["165 #1", "165 #2", "165 #3"]
    for x, nm in zip(xs, names):
        f.append(fitbox(x, 100, 150, 120, nm, size=15))
        # вісім входів згори
        for i in range(8):
            xx = x + 20 + i * 15.7
            f.append(line(xx, 58, xx, 100, color=LINE, sw=1.4))
        f.append(text(x + 75, 44, "8 входів", size=12, color=MUTED))

    # дані течуть праворуч наліво: Q7 → DS → ... → МК
    f.append(arrow(300, 150, 192, 150))
    f.append(text(246, 138, "Q7 → до МК", size=12, color=MUTED))
    f.append(arrow(500, 150, 452, 150))
    f.append(text(476, 138, "Q7→DS", size=12, color=MUTED))
    f.append(arrow(700, 150, 652, 150))
    f.append(text(676, 138, "Q7→DS", size=12, color=MUTED))

    # спільні PL і CP
    for yy, lbl, sx in ((260, "PL (спільна)", 330), (292, "CP (спільна)", 360)):
        f.append(line(190, yy, 790, yy, color=FIELD, sw=1.8))
        f.append(text(200, yy - 8, lbl, size=12, color=FIELD, anchor="start"))
        for x in xs:
            f.append(line(x + (sx - 300), yy, x + (sx - 300), 220, color=FIELD, sw=1.5))

    f.append(text(470, 350,
                  "три корпуси — 24 входи, а до мікроконтролера так само три лінії",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'hc165-chain.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  4. Один обмін SPI — і виходи, і входи одразу
# ════════════════════════════════════════════════════════════════════════════
def _wave(f, y, hi_h, segs, x_end, color=LINE):
    """segs — список (x, рівень 0/1); малює цифрову доріжку до x_end."""
    prev_x, prev_l = segs[0]
    for x, l in segs[1:] + [(x_end, None)]:
        yy = y - hi_h if prev_l else y
        f.append(line(prev_x, yy, x, yy, color=color, sw=2))
        if l is not None and l != prev_l:
            f.append(line(x, y, x, y - hi_h, color=color, sw=2))
        prev_x, prev_l = x, (prev_l if l is None else l)


def fig_duplex():
    W, H = 900, 480
    f = []
    x0, xe = 150, 860

    # мітки рядків
    for lbl, yy in (("STROBE", 112), ("SCK", 202), ("MOSI", 285), ("MISO", 345)):
        f.append(text(140, yy, lbl, size=13, bold=True, anchor="end"))

    # STROBE: 1 → 0 (200) → 1 (330)
    _wave(f, 120, 26, [(x0, 1), (200, 0), (330, 1)], xe, color=FIELD)

    # SCK: вісім імпульсів між 380 і 700
    segs = [(x0, 0)]
    for i in range(8):
        segs.append((380 + i * 40, 1))
        segs.append((400 + i * 40, 0))
    _wave(f, 210, 26, segs, xe)

    # смуги даних
    f.append(fitbox(380, 262, 320, 40, "MOSI: новий байт → у 595", size=13))
    f.append(fitbox(380, 322, 320, 40, "MISO: знятий байт ← з 165", size=13))

    # маркери подій
    for x, n in ((200, "1"), (330, "2"), (540, "3")):
        guide_to = 178 if n == "3" else 132
        f.append(line(x, 80, x, guide_to, color=MUTED, sw=1.2, dash="5 5"))
        f.append(circle(x, 64, 13, fill=FILL, stroke=INK, sw=1.6))
        f.append(text(x, 69, n, size=14, bold=True))

    for i, s in enumerate([
        "1 — STROBE вниз: 74HC165 фіксує стан усіх входів одним моментом.",
        "2 — STROBE вгору: 165 стає на зсув, а 595 тим же фронтом показує байт минулого кола.",
        "3 — вісім тактів SCK: один обмін SPI віддає байт у 595 і забирає байт із 165.",
    ]):
        f.append(text(60, 400 + i * 24, s, size=13, color=INK, anchor="start"))

    render(os.path.join(IMG, 'hc165-duplex.svg'), W, H, *f)


if __name__ == '__main__':
    fig_mirror()
    fig_pinout()
    fig_chain()
    fig_duplex()
    print("ok: hc165-mirror, hc165-pinout, hc165-chain, hc165-duplex")
