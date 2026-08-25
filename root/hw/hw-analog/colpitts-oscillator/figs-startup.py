# -*- coding: utf-8 -*-
"""Фігури вставки math-startup-condition.md (book/electronics/analog/colpitts-oscillator).
Окремий генератор поряд із figs.py теми (щоб не конфліктувати з рештою фігур теми).
  negres.svg   — активний дільник C1–C2 з керованим струмом gm·u згортається
                 на вході у (−R послідовно з Cs): серце виведення
  balance.svg  — баланс опорів: +Rp втрат проти −R активного; поріг gm·Rp = C2/C1
                 розділяє згасання від наростання
Запуск:  python figs-startup.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ACC = "#8e44ad"   # коло зворотного зв'язку (як у figs.py теми)
TANK = "#27ae60"  # коливальний контур
NR = "#c0392b"    # від'ємний опір — джерело енергії, гаряче


def cap(cx, cy, gap=7, plate=15, lead=12, color=LINE):
    """Вертикальний конденсатор (дві пластини)."""
    out = [line(cx, cy - gap - lead, cx, cy - gap, color=color),
           line(cx - plate, cy - gap, cx + plate, cy - gap, color=color, sw=2.2),
           line(cx - plate, cy + gap, cx + plate, cy + gap, color=color, sw=2.2),
           line(cx, cy + gap, cx, cy + gap + lead, color=color)]
    return "".join(out)


def gnd(cx, cy, color=LINE):
    out = [line(cx, cy, cx, cy + 6, color=color)]
    for i, w in enumerate((16, 10, 5)):
        out.append(line(cx - w, cy + 6 + i * 4, cx + w, cy + 6 + i * 4, color=color, sw=2))
    return "".join(out)


def fig_negres():
    """Активний дільник C1–C2 з керованим струмом gm·u → (−R послідовно з Cs)."""
    W, H = 680, 420
    f = []

    # — Ліва панель: що насправді коїться на вході —
    xc = 175
    yTop, yTap, yBot = 100, 220, 340
    f.append(text(xc, 66, "погляд у вхід підсилювача", size=13, bold=True))
    f.append(line(xc, yTop, xc, (yTop + yTap) / 2 - 12, color=LINE))
    f.append(cap(xc, (yTop + yTap) / 2))
    f.append(line(xc, (yTop + yTap) / 2 + 12, xc, yTap, color=LINE))
    f.append(text(xc - 22, (yTop + yTap) / 2 + 4, "C1", size=14, bold=True, anchor="end"))
    f.append(line(xc, yTap, xc, (yTap + yBot) / 2 - 12, color=LINE))
    f.append(cap(xc, (yTap + yBot) / 2))
    f.append(line(xc, (yTap + yBot) / 2 + 12, xc, yBot, color=LINE))
    f.append(text(xc - 22, (yTap + yBot) / 2 + 4, "C2", size=14, bold=True, anchor="end"))
    f.append(circle(xc, yTop, 3, fill=LINE, stroke=LINE))
    f.append(circle(xc, yTap, 4, fill=ACC, stroke=ACC))
    f.append(line(xc, yBot, xc, yBot + 14, color=LINE))
    f.append(gnd(xc, yBot + 14))
    # вхід на відведення; проба напруги u
    f.append(line(xc, yTap, xc - 58, yTap, color=ACC, sw=2))
    f.append(circle(xc - 58, yTap, 3, fill=ACC, stroke=ACC))
    f.append(text(xc - 62, yTap + 4, "вхід u", size=11, color=ACC, anchor="end"))
    # керований струм gm·u назад у верхній вузол
    f.append(arrow(xc + 18, yTap - 8, xc + 18, yTop + 8, color=NR))
    f.append(text(xc + 26, (yTop + yTap) / 2 - 4, "gm·u", size=13, color=NR, anchor="start", italic=True))
    f.append(text(xc + 26, (yTop + yTap) / 2 + 12, "струм виходу", size=10, color=MUTED, anchor="start"))
    f.append(text(xc + 26, (yTop + yTap) / 2 + 24, "тече у C1", size=10, color=MUTED, anchor="start"))

    # — стрілка «те саме» —
    f.append(arrow(320, 220, 388, 220, color=INK, sw=2.4))
    f.append(text(354, 205, "те саме", size=12, color=MUTED))

    # — Права панель: еквівалент (−R послідовно з Cs) —
    xe = 490
    yE1, yE2, yE3 = 100, 220, 340
    f.append(text(xe, 66, "те, що бачить контур", size=13, bold=True))
    f.append(line(xe, yE1, xe, (yE1 + yE2) / 2 - 18, color=NR))
    f.append(rect(xe - 27, (yE1 + yE2) / 2 - 18, 54, 36, fill="#fdecea", stroke=NR, sw=2, rx=4))
    f.append(text(xe, (yE1 + yE2) / 2 + 5, "−R", size=16, bold=True, color=NR))
    f.append(line(xe, (yE1 + yE2) / 2 + 18, xe, yE2, color=NR))
    f.append(line(xe, yE2, xe, (yE2 + yE3) / 2 - 12, color=TANK))
    f.append(cap(xe, (yE2 + yE3) / 2, color=TANK))
    f.append(line(xe, (yE2 + yE3) / 2 + 12, xe, yE3, color=TANK))
    f.append(text(xe + 22, (yE2 + yE3) / 2 + 4, "Cs", size=14, bold=True, color=TANK, anchor="start"))
    f.append(circle(xe, yE1, 3, fill=ACC, stroke=ACC))
    f.append(line(xe, yE1, xe - 50, yE1, color=ACC, sw=2))
    f.append(text(xe - 54, yE1 + 4, "вхід u", size=11, color=ACC, anchor="end"))
    f.append(line(xe, yE3, xe, yE3 + 14, color=LINE))
    f.append(gnd(xe, yE3 + 14))

    # формули внизу — окремими рамками, рівно під панелями
    b1, w1, h1 = textbox(xe, 392, "R = gm / (ω²·C1·C2)", size=13, pad=10,
                         stroke=NR, fill="#fff", color=NR, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(xc, 392, "Cs = C1·C2 / (C1+C2)", size=13, pad=10,
                         stroke=TANK, fill="#fff", color=TANK)
    f.append(b2)

    render(os.path.join(OUT, 'negres.svg'), W, H, *f,
           title="Активний дільник на вході = від'ємний опір −R послідовно з Cs")


def fig_balance():
    """Баланс опорів: +Rp втрат проти −R активного; поріг gm·Rp = C2/C1."""
    W, H = 680, 360
    POSr = TANK
    f = []

    y0 = 158
    x0, x1 = 56, 624
    xMid = (x0 + x1) / 2
    f.append(line(x0, y0, x1, y0, color=MUTED))
    f.append(line(xMid, 86, xMid, 232, color=INK, dash="5 4"))
    f.append(text(xMid, 74, "ПОРІГ:  gm·Rp = C2/C1", size=14, bold=True))

    # ліва зона — згасання
    f.append(text(x0 + 120, 112, "gm·Rp < C2/C1", size=13, color=NEG, bold=True))
    f.append(text(x0 + 120, 130, "втрати беруть гору", size=11, color=MUTED))
    pts = []
    for i in range(0, 150):
        xx = x0 + 16 + i * 0.98
        amp = 44 * math.exp(-i / 64.0)
        yy = y0 + 64 + amp * math.sin(i / 6.6)
        pts.append((xx, yy))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))
    f.append(text(x0 + 120, y0 + 134, "коливання згасає", size=11, color=NEG))

    # права зона — наростання
    f.append(text(x1 - 120, 112, "gm·Rp > C2/C1", size=13, color=POSr, bold=True))
    f.append(text(x1 - 120, 130, "підкачка бере гору", size=11, color=MUTED))
    pts2 = []
    for i in range(0, 150):
        xx = xMid + 16 + i * 0.98
        amp = min(11 * math.exp(i / 116.0), 50)
        yy = y0 + 64 + amp * math.sin(i / 6.6)
        pts2.append((xx, yy))
    d2 = "M %.1f %.1f " % pts2[0] + " ".join("L %.1f %.1f" % p for p in pts2[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d2, POSr))
    f.append(text(x1 - 120, y0 + 134, "наростає → старт", size=11, color=POSr))

    f.append(text(xMid, 250, "−R активного входу гасить +Rp втрат контуру: хто переважить",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'balance.svg'), W, H, *f,
           title="Запуск = коли підкачка переважує втрати")


if __name__ == '__main__':
    fig_negres()
    fig_balance()
    print("OK: 2 figures (startup insert)")
