# -*- coding: utf-8 -*-
"""Фігури до теми «Стандартний електродний потенціал і ряд активності»
(book/chemistry/physical-chemistry/electrode-potential)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: шкала стандартних потенціалів ────────────────────────────────
def fig_scale():
    W, H = 960, 400
    frags = []

    X0, X1 = 80, 880          # межі осі
    E0, E1 = -3.25, 1.75      # межі шкали, вольти
    AY = 200                  # рівень осі
    K = (X1 - X0) / (E1 - E0)

    def px(e):
        return X0 + (e - E0) * K

    frags.append(text(W / 2, 34,
                      "Стандартний потенціал: наскільки охоче метал віддає електрони",
                      size=17, bold=True))

    # сама вісь зі стрілками на обидва боки
    frags.append(line(X0, AY, X1, AY, color=INK, sw=2.5))
    frags.append(arrow(X0 + 30, AY, X0 - 4, AY, color=INK, sw=2.5))
    frags.append(arrow(X1 - 30, AY, X1 + 4, AY, color=INK, sw=2.5))

    # нуль — водневий електрод: пунктир на всю висоту й підпис під віссю
    xh = px(0.0)
    frags.append(line(xh, 96, xh, 300, color=FIELD, sw=2, dash="7,6"))
    body, bw, bh = textbox(xh, 330, "водень: рівно 0.00 В\n(нуль за домовленістю)",
                           size=14, bold=True, fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(body)

    # метали: підписи через один — вище й нижче осі, щоб не тіснилися
    metals = [("Li", -3.04), ("Na", -2.71), ("Mg", -2.37), ("Zn", -0.76),
              ("Fe", -0.44), ("Cu", 0.34), ("Ag", 0.80), ("Au", 1.50)]
    for i, (sym, e) in enumerate(metals):
        x = px(e)
        up = (i % 2 == 0)
        color = NEG if e < 0 else POS
        frags.append(line(x, AY - 9, x, AY + 9, color=INK, sw=2))
        frags.append(circle(x, AY, 6, fill="#ffffff", stroke=color, sw=2.5))
        if up:
            frags.append(text(x, AY - 48, sym, size=19, bold=True, color=color))
            frags.append(text(x, AY - 26, "%+.2f" % e, size=14, color=MUTED))
        else:
            frags.append(text(x, AY + 40, sym, size=19, bold=True, color=color))
            frags.append(text(x, AY + 62, "%+.2f" % e, size=14, color=MUTED))

    # що означають краї шкали
    frags.append(mtext(150, 120, "віддають електрони охоче:\nактивні метали",
                       size=14, color=MUTED))
    frags.append(mtext(790, 120, "тримають електрони міцно:\nблагородні метали",
                       size=14, color=MUTED))

    render(os.path.join(IMG, 'potential-scale.svg'), W, H, *frags)


# ── Фігура 2: звідки береться напруга ──────────────────────────────────────
def fig_voltage():
    W, H = 860, 560
    frags = []

    # вольтметр
    VX, VY, VR = 430, 72, 40
    frags.append(circle(VX, VY, VR, fill="#ffffff", stroke=INK, sw=2.5))
    frags.append(text(VX, VY + 9, "V", size=26, bold=True))
    frags.append(text(VX + 118, VY + 8, "1.10 В", size=20, bold=True, color=FIELD))

    # дроти від пластинок до вольтметра
    LX, RX = 250, 610
    frags.append(line(LX, 150, LX, VY, color=INK, sw=2.5))
    frags.append(line(LX, VY, VX - VR, VY, color=INK, sw=2.5))
    frags.append(line(RX, 150, RX, VY, color=INK, sw=2.5))
    frags.append(line(RX, VY, VX + VR, VY, color=INK, sw=2.5))
    frags.append(text(LX + 62, 98, "e⁻", size=15, bold=True, color=NEG))
    frags.append(arrow(LX + 28, 122, LX + 96, 122, color=NEG, sw=2))

    # посудина — самими лініями, щоб пластинки справді стояли в розчині
    frags.append(line(160, 190, 160, 390, color=INK, sw=2.5))
    frags.append(line(160, 390, 700, 390, color=INK, sw=2.5))
    frags.append(line(700, 190, 700, 390, color=INK, sw=2.5))
    frags.append(line(162, 224, 698, 224, color=NEG, sw=2.5))
    frags.append(text(430, 352, "розчин солі", size=15, color=MUTED))

    # пластинки
    frags.append(rect(LX - 16, 150, 32, 185, fill="#e6e8ea", stroke=INK, sw=2))
    frags.append(rect(RX - 16, 150, 32, 185, fill="#f6ddc9", stroke=INK, sw=2))

    # підписи пластинок під посудиною
    frags.append(text(LX, 428, "цинк", size=19, bold=True, color=NEG))
    frags.append(text(LX, 452, "E° = −0.76 В", size=15, color=MUTED))
    frags.append(text(RX, 428, "мідь", size=19, bold=True, color=POS))
    frags.append(text(RX, 452, "E° = +0.34 В", size=15, color=MUTED))

    # головна арифметика
    body, bw, bh = textbox(430, 500, "напруга = (+0.34) − (−0.76) = 1.10 В",
                           size=18, bold=True, fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(body)
    frags.append(text(430, 543,
                      "дві однакові пластинки: 0.34 − 0.34 = 0 — стрілка не ворухнеться",
                      size=14, color=MUTED))

    render(os.path.join(IMG, 'two-metals-voltage.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_scale()
    fig_voltage()
    print("ok")
