# -*- coding: utf-8 -*-
"""Фігури до теми «Доповняльний код» (two's complement).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas','DejaVu Sans Mono',monospace"


def mono(x, y, s, size=15, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s xml:space="preserve">%s</text>'
            % (x, y, MONO, size, color, anchor, w, esc(s)))


def sgn(v):
    """Знакове число з Unicode-мінусом (не ASCII-дефісом)."""
    if v > 0:
        return "+%d" % v
    if v < 0:
        return "−%d" % (-v)
    return "0"


def fig_clock():
    """Коло на 16 поділок (4 біти): верхня дуга 0..7 додатні, нижня 8..15
    читається як -8..-1. Показуємо, що -3 назад = +13 вперед."""
    W, H = 720, 500
    f = [text(W / 2, 30, "Двійкове число фіксованої ширини — це коло", size=17, bold=True)]
    f.append(text(W / 2, 52, "4 біти → 16 поділок; йти назад = йти вперед на доповнення",
                  size=12, color=MUTED, italic=True))

    cx, cy, R = W / 2, 278, 140
    n = 16
    # ободок
    f.append(circle(cx, cy, R, fill="#ffffff", stroke=LINE, sw=1.6))

    def pos(i, r=R):
        # i=0 угорі, за годинниковою стрілкою
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * math.cos(a), cy + r * math.sin(a)

    for i in range(n):
        px, py = pos(i)
        signed = i if i < 8 else i - 16
        col = FIELD if i < 8 else NEG
        # поділка
        ax = -math.pi / 2 + 2 * math.pi * i / n
        f.append(line(cx + (R - 8) * math.cos(ax), cy + (R - 8) * math.sin(ax),
                      px, py, color=MUTED, sw=1.2))
        # мітка ЗЗОВНІ: беззнакове зверху, знакове знизу
        lx, ly = cx + (R + 26) * math.cos(ax), cy + (R + 26) * math.sin(ax)
        f.append(mono(lx, ly - 2, "%02d" % i, size=12, color=MUTED, anchor="middle"))
        f.append(mono(lx, ly + 13, sgn(signed), size=12, color=col, bold=True, anchor="middle"))

    # кольорові підписи двох дуг — з боків, щоб не наскочити на числа зверху/знизу
    f.append(text(cx + R + 66, cy - R + 40, "верх:", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(cx + R + 66, cy - R + 58, "додатні", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(cx - R - 66, cy + R - 58, "низ: старший", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(cx - R - 66, cy + R - 40, "біт = 1 → −", size=13, bold=True, color=NEG, anchor="end"))

    # приклад: -3 як +13. дуга-пояснення в центрі + стрілка до поділки 13
    p13 = pos(13, R - 4)
    box, bw, bh = textbox(cx, cy, "−3 назад\n=\n+13 вперед\n(поділка 13)",
                          size=13, pad=10, fill="#eef7f0", stroke=FIELD, sw=1.6, bold=True)
    f.append(box)
    f.append(arrow(cx - bw / 2 - 4, cy - 12, p13[0] + 10, p13[1] + 6, color=POS, sw=2.2))

    render(os.path.join(OUT, 'tc-clock.svg'), W, H, *f)


def fig_weights():
    """Ваги 8 розрядів: беззнакове (усі +) проти доповняльного (старший −128).
    Знизу — приклад 1111 1011 прочитаний вагами доповняльного = −5."""
    W, H = 760, 420
    f = [text(W / 2, 30, "Доповняльний код: та сама вага скрізь, крім старшого біта",
              size=16, bold=True)]

    bits = ["b7", "b6", "b5", "b4", "b3", "b2", "b1", "b0"]
    uns = ["+128", "+64", "+32", "+16", "+8", "+4", "+2", "+1"]
    two = ["−128", "+64", "+32", "+16", "+8", "+4", "+2", "+1"]

    cw, gap = 78, 8
    total = 8 * cw + 7 * gap
    x0 = (W - total) / 2

    def row(y, label, weights, accent_first):
        f.append(text(x0 - 14, y + 24, label, size=13, bold=True, anchor="end"))
        x = x0
        for i, (b, w) in enumerate(zip(bits, weights)):
            hot = (i == 0 and accent_first)
            col = POS if hot else LINE
            fill = "#fdecea" if hot else FILL
            f.append(rect(x, y, cw, 44, fill=fill, stroke=col, sw=1.8 if hot else 1.3))
            f.append(mono(x + cw / 2, y + 18, b, size=12, color=MUTED, anchor="middle"))
            f.append(text(x + cw / 2, y + 36, w, size=14,
                          color=(POS if hot else INK), bold=hot, anchor="middle"))
            x += cw + gap

    f.append(text(x0 + total / 2, 74, "беззнакове", size=13, bold=True, color=MUTED))
    row(84, "вага", uns, accent_first=False)
    f.append(text(x0 + total / 2, 168, "доповняльний код — змінилась ОДНА вага", size=13,
                  bold=True, color=POS))
    row(178, "вага", two, accent_first=True)

    # приклад унизу: 1111 1011
    ey = 262
    f.append(rect(x0, ey, total, 118, fill="#f7f9fc", stroke=LINE, sw=1.3))
    f.append(text(x0 + total / 2, ey + 26, "приклад:  1111 1011  за вагами доповняльного коду",
                  size=14, bold=True))
    f.append(mono(x0 + total / 2, ey + 58,
                  "−128 + 64 + 32 + 16 + 8 +  0 +  2 +  1", size=15, anchor="middle"))
    f.append(mono(x0 + total / 2, ey + 84, "=  −128 + 123", size=15, anchor="middle", color=MUTED))
    f.append(text(x0 + total / 2, ey + 108, "=  −5", size=17, bold=True, color=NEG))

    render(os.path.join(OUT, 'tc-weights.svg'), W, H, *f)


def fig_timeline():
    """Одна ідея «відняти = додати доповнення» крізь три століття:
    механічні лічильники (десяткове доповнення) → двійковий злам."""
    W, H = 1040, 500
    f = [text(W / 2, 32, "Відняти = додати доповнення: одна ідея крізь століття",
              size=18, bold=True)]
    f.append(text(W / 2, 55,
                  "механічні лічильники віднімають десятковим доповненням; у двійці «9 − цифра» стає простим «НЕ» над бітом",
                  size=12, color=MUTED, italic=True))

    # горизонтальна вісь часу
    axy = 262
    x0, x1 = 55, W - 40
    f.append(line(x0, axy, x1, axy, color=LINE, sw=2))
    f.append(arrow(x1 - 2, axy, x1 + 10, axy, color=LINE, sw=2))

    BW, BH = 154, 108   # картка

    # межа двох епох (між 1938 і 1945)
    xb = 560
    f.append(line(xb, 90, xb, axy + 130, color=MUTED, sw=1.3, dash="6 5"))
    # смуги-підписи епох унизу
    f.append(text((x0 + xb) / 2 + 10, axy + 150,
                  "механічна доба · основа 10 · десяткове доповнення",
                  size=12.5, bold=True, color=FIELD))
    f.append(text((xb + x1) / 2, axy + 150,
                  "двійкова доба · основа 2 · «НЕ» над бітом + 1",
                  size=12.5, bold=True, color=NEG))

    def milestone(x, up, tag, title, sub, col, fill):
        f.append(circle(x, axy, 6, fill=col, stroke=col, sw=1.5))
        # рік — маленькою міткою просто біля вузла на осі
        f.append(text(x + (0 if up else 0), axy + (-14 if up else 22),
                      tag, size=13, bold=True, color=col))
        by = axy - 30 - BH if up else axy + 30
        # ніжка від осі до картки
        f.append(line(x, axy, x, (by + BH) if up else by, color=col, sw=1.4))
        f.append(fitbox(x - BW / 2, by, BW, BH, "%s\n%s" % (title, sub),
                        size=13, pad=9, fill=fill, stroke=col, sw=1.7))

    # десяткові (зелені), по черзі верх/низ — сусіди по різні боки осі
    milestone(140, True, "1642", "Паскаліна",
              "Паскаль (Франція)\nдев'яткове\nдоповнення", FIELD, "#eef7f0")
    milestone(300, False, "1887", "Комптометр",
              "Фелт (США)\nклавіші; 9-ве\nдоповнення", FIELD, "#eef7f0")
    milestone(460, True, "1938", "«Курта»",
              "Герцштарк\n(Австрія) · креслив\nу Бухенвальді", FIELD, "#eef7f0")

    # двійкові (сині; стандарт — червоний акцент)
    milestone(660, False, "1945", "Чернетка EDVAC",
              "фон Нейман:\nдвійковий код —\nідея на папері", NEG, "#eaf0fd")
    milestone(800, True, "1949", "EDSAC",
              "Вілкс (Кембридж)\nперша РОБОЧА\nреалізація", NEG, "#eaf0fd")
    milestone(950, False, "1964", "IBM System/360",
              "стандарт галузі:\nдоповняльний\nкод усюди", POS, "#fdecea")

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_clock()
    fig_weights()
    fig_timeline()
    print("OK: tc-clock, tc-weights, hist-timeline")
