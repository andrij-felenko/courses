# -*- coding: utf-8 -*-
"""Фігури до теми «TP4056».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Плата TP4056-класу: один резистор задає струм ─────────────────────────────
def fig_board():
    W, H = 760, 400
    f = [text(W / 2, 28, "Плата TP4056-класу: один резистор задає струм CC",
              size=16, bold=True)]
    cy = 175

    # силовий тракт: вхід 5 В → чип → комірка
    bx, _, _ = textbox(95, cy, "USB 5 В\n(вхід)", size=12, fill="#fdecea", stroke=POS, min_w=110)
    f.append(bx)
    chip = rect(240, cy - 56, 200, 112, fill=FILL, stroke=INK, sw=2)
    f.append(chip)
    f.append(text(340, cy - 30, "TP4056", size=15, bold=True))
    f.append(mtext(340, cy - 4, "лінійний CC/CV\nдо 4.2 В · автономно",
                   size=11, color=MUTED))
    cl, _, _ = textbox(645, cy, "комірка\nLi 1S", size=12, fill="#e9f7ef", stroke=FIELD, min_w=110)
    f.append(cl)
    f.append(arrow(152, cy, 238, cy, color=POS, sw=2.2))
    f.append(text(195, cy - 12, "VCC", size=11, color=POS, bold=True))
    f.append(arrow(442, cy, 586, cy, color=POS, sw=2.2))
    f.append(text(515, cy - 12, "BAT", size=11, color=POS, bold=True))

    # Rprog знизу до чипа
    f.append(line(300, cy + 56, 300, cy + 92, color=NEG, sw=1.6))
    rb = rect(276, cy + 92, 48, 26, fill=BG, stroke=NEG, sw=1.8)
    f.append(rb)
    f.append(text(300, cy + 109, "Rprog", size=11, color=NEG, bold=True))
    f.append(line(300, cy + 118, 300, cy + 132, color=INK, sw=1.6))
    f.append(line(288, cy + 132, 312, cy + 132, color=INK, sw=2))  # земля
    f.append(text(300, cy + 150, "PROG → задає Iзар", size=11, color=NEG))

    # TEMP від комірки (опційно)
    f.append(line(560, cy + 56, 560, cy + 92, color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(560, cy + 109, "TEMP → термістор", size=10.5, color=MUTED))
    f.append(text(560, cy + 124, "(часто вимкнено)", size=10, color=MUTED))

    # світлодіоди CHRG/STDBY угору
    f.append(line(310, cy - 56, 310, cy - 86, color=FIELD, sw=1.6))
    f.append(circle(310, cy - 94, 7, fill=BG, stroke=FIELD, sw=1.8))
    f.append(line(370, cy - 56, 370, cy - 86, color=FIELD, sw=1.6))
    f.append(circle(370, cy - 94, 7, fill=BG, stroke=FIELD, sw=1.8))
    f.append(text(340, cy - 112, "CHRG / STDBY (відкритий стік)", size=11, color=FIELD))

    # підпис унизу
    b, _, _ = textbox(W / 2, 372,
                      "вихід до системи з'єднано прямо з BAT — power-path немає; захист DW01+8205 (на «захищених» платах) — окремий вузол",
                      size=10.5, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "board.svg"), W, H, *f)


# ── PROG: вивід не «обмежує», а ВИМІРЮЄ зразковий струм і дзеркалить ───────────
def fig_prog():
    W, H = 760, 360
    f = [text(W / 2, 28, "PROG: чип міряє зразковий струм і збільшує його у ~1200 разів",
              size=16, bold=True)]
    cy = 180

    # ліворуч: опорне 1 В на Rprog → крихітний зразковий струм
    f.append(text(150, 78, "вивід PROG тримає 1.000 В", size=12, color=NEG, bold=True))
    bref, _, _ = textbox(150, cy - 18, "опорне\n1.000 В", size=12, fill="#eef3fb", stroke=NEG, min_w=110)
    f.append(bref)
    f.append(line(150, cy + 6, 150, cy + 48, color=NEG, sw=1.8))
    rb = rect(124, cy + 48, 52, 28, fill=BG, stroke=NEG, sw=1.8)
    f.append(rb)
    f.append(text(150, cy + 66, "Rprog", size=11, color=NEG, bold=True))
    f.append(line(150, cy + 76, 150, cy + 90, color=INK, sw=1.6))
    f.append(line(138, cy + 90, 162, cy + 90, color=INK, sw=2))
    f.append(text(150, cy + 112, "I_prog = 1 В / Rprog", size=11.5, color=NEG))
    f.append(text(150, cy + 130, "(~міліампер)", size=10.5, color=MUTED))

    # дзеркало посередині
    f.append(arrow(230, cy - 18, 360, cy - 18, color=INK, sw=2))
    box, _, _ = textbox(440, cy - 18, "струмове\nдзеркало\n× ~1200", size=12, fill=FILL, stroke=INK, min_w=130)
    f.append(box)

    # праворуч: великий струм у комірку
    f.append(arrow(520, cy - 18, 620, cy - 18, color=POS, sw=2.6))
    f.append(text(570, cy - 30, "Iзар", size=11, color=POS, bold=True))
    bc, _, _ = textbox(680, cy - 18, "у комірку\nIзар (~ампер)", size=12, fill="#e9f7ef", stroke=FIELD, min_w=120)
    f.append(bc)

    # головна формула знизу
    b, _, _ = textbox(W / 2, 322,
                      "Iзар ≈ 1200 / Rprog  ·  подвоїш Rprog — удвічі менший зразок — удвічі менший заряд",
                      size=12, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "prog.svg"), W, H, *f)


if __name__ == "__main__":
    fig_board()
    fig_prog()
    print("OK: 2 figures ->", IMG)
