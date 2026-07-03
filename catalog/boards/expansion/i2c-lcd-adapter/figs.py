# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «I2C-адаптер для LCD 1602 (PCF8574)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Байт розширювача → вісім ніжок LCD (карта бітів) ───────────────────────
def fig_bit_map():
    W, H = 860, 470
    f = [text(W / 2, 30, "Один байт по I2C → вісім ніжок дисплея",
              size=16, bold=True)]

    # зліва: байт як 8 клітинок P7..P0
    bx, by = 60, 90
    cw, ch = 66, 52
    bits = [
        ("P7", "D7", FIELD),
        ("P6", "D6", FIELD),
        ("P5", "D5", FIELD),
        ("P4", "D4", FIELD),
        ("P3", "BL", POS),
        ("P2", "E",  NEG),
        ("P1", "RW", MUTED),
        ("P0", "RS", NEG),
    ]
    f.append(text(bx + 4 * cw, by - 16, "байт у PCF8574 (P7 … P0)", size=12, bold=True, anchor="middle"))
    for i, (pin, dst, col) in enumerate(bits):
        x = bx + i * cw
        f.append(rect(x, by, cw, ch, fill=BG, stroke=INK, sw=1.6, rx=6))
        f.append(text(x + cw / 2, by + 22, pin, size=12.5, bold=True))
        f.append(text(x + cw / 2, by + 40, dst, size=10, color=col, bold=True))

    # права колонка: призначення ніжок з підписами
    ry = by + ch + 60
    rowh = 44
    rows = [
        ("D4 – D7", "чотири лінії даних (4-бітний режим)", FIELD),
        ("BL", "керування підсвіткою через транзистор", POS),
        ("E  (Enable)", "строб: перепад засувує нібл у дисплей", NEG),
        ("RW", "читання/запис — на модулі завжди «запис»", MUTED),
        ("RS", "команда (0) чи символ (1)", NEG),
    ]
    lxx = 90
    for i, (nm, desc, col) in enumerate(rows):
        y = ry + i * rowh
        f.append(circle(lxx, y, 7, fill=col, stroke=col, sw=1))
        f.append(text(lxx + 22, y + 5, nm, size=12.5, bold=True, color=col, anchor="start"))
        f.append(text(lxx + 190, y + 5, desc, size=11.5, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "8-бітний байт по LCD не бʼється: старший і молодший нібли йдуть двома посилками, кожна зі стробом E",
                        size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bit-map.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: МК → адаптер → LCD ─────────────────────────────────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 30, "Чотири дроти до мікроконтролера, шістнадцять — до дисплея",
              size=16, bold=True)]

    # МК ліворуч
    mkx, mky, mkw, mkh = 50, 120, 150, 210
    f.append(rect(mkx, mky, mkw, mkh, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mkx + mkw / 2, mky + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mkx + mkw / 2, mky + 44, "(ESP32 / Arduino)", size=10, color=MUTED))
    mk_pins = [("3V3 / 5V", POS, mky + 84),
               ("GND", INK, mky + 120),
               ("SDA", NEG, mky + 156),
               ("SCL", NEG, mky + 192)]
    for lbl, col, y in mk_pins:
        f.append(text(mkx + mkw - 12, y, lbl, size=11.5, bold=True, color=col, anchor="end"))

    # адаптер у центрі
    ax, ay, aw, ah = 380, 100, 170, 250
    f.append(rect(ax, ay, aw, ah, fill="#fafbfc", stroke=MUTED, sw=1.7, rx=12))
    f.append(text(ax + aw / 2, ay + 24, "I2C-адаптер", size=12.5, bold=True))
    f.append(text(ax + aw / 2, ay + 42, "PCF8574 + транзистор", size=10, color=MUTED))
    # чотири входи ліворуч на адаптері (дзеркало МК)
    in_pins = [("VCC", POS, mky + 84),
               ("GND", INK, mky + 120),
               ("SDA", NEG, mky + 156),
               ("SCL", NEG, mky + 192)]
    for lbl, col, y in in_pins:
        f.append(text(ax + 12, y, lbl, size=11, bold=True, color=col, anchor="start"))
        f.append(line(mkx + mkw, y, ax, y, color=col, sw=2.0))

    # контраст-потенціометр і адреса-джампери — позначки на адаптері
    f.append(text(ax + aw / 2, ay + ah - 46, "потенціометр", size=9.5, color=INK))
    f.append(text(ax + aw / 2, ay + ah - 32, "контрасту", size=9.5, color=INK))
    f.append(text(ax + aw / 2, ay + ah - 14, "джампери A0·A1·A2 · перемичка BL", size=8.8, color=MUTED))

    # LCD праворуч — гребінка 16 контактів (гніздо адаптера в неї впаяне)
    lx, ly, lw, lh = 690, 90, 160, 280
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke=INK, sw=1.7, rx=10))
    f.append(text(lx + lw / 2, ly + 24, "LCD 1602", size=12.5, bold=True))
    f.append(text(lx + lw / 2, ly + 42, "16 контактів (гребінка)", size=9.5, color=MUTED))
    # 16-пінова гребінка згори адаптера в LCD — намалюємо блок роз'єму
    conx, cony = ax + aw, ay + 70
    f.append(rect(conx + 40, cony, 60, 150, fill="#fdf6e3", stroke=POS, sw=1.5, rx=6))
    f.append(text(conx + 70, cony + 74, "16-піновий", size=9.5, anchor="middle"))
    f.append(text(conx + 70, cony + 90, "роз'єм", size=9.5, anchor="middle"))
    # шина 8 керуючих/даних ліній від адаптера в роз'єм
    f.append(line(ax + aw, ay + ah / 2, conx + 40, cony + 75, color=FIELD, sw=3.0))
    f.append(text((ax + aw + conx + 40) / 2, ay + ah / 2 - 8, "RS·RW·E", size=9, color=FIELD, bold=True))
    f.append(text((ax + aw + conx + 40) / 2, ay + ah / 2 + 26, "D4–D7·BL", size=9, color=FIELD, bold=True))
    # роз'єм у LCD
    f.append(line(conx + 100, cony + 75, lx, ly + lh / 2, color=INK, sw=2.4))

    b, bw, bh = textbox(W / 2, H - 24,
                        "адаптер упаяний прямо в гребінку дисплея — назовні лишаються тільки VCC, GND, SDA, SCL",
                        size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bit_map()
    fig_wiring()
    print("OK: 2 figures ->", IMG)
