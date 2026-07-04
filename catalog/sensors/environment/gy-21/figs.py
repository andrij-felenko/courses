# -*- coding: utf-8 -*-
"""Фігури для статті GY-21 (Si7021/HTU21D). Вивід у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині модуля (блок-схема устрою) ───────────────────────
def fig_inside():
    W, H = 760, 470
    frags = []

    # Рамка-контур плати
    frags.append(rect(30, 60, W - 60, H - 110, fill="#fbfcfd", stroke=MUTED, sw=2, rx=14))
    frags.append(text(W / 2, 84, "плата модуля GY-21", size=13, color=MUTED))

    # Вхідна клема живлення VIN (3.3..5 В)
    b, w1, h1 = textbox(120, 150, "VIN\n3.3–5 В", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=90)
    frags.append(b)

    # LDO-регулятор 662K -> 3.3 В
    b, w2, h2 = textbox(320, 150, "LDO 662K\n(XC6206)\n→ 3.3 В", size=13, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=130)
    frags.append(b)
    frags.append(arrow(120 + w1 / 2, 150, 320 - w2 / 2, 150))

    # Внутрішня шина 3.3 В (вузол)
    frags.append(line(320 + w2 / 2, 150, 600, 150, color=FIELD, sw=2.2))
    frags.append(text(510, 138, "внутрішні 3.3 В", size=12, color=FIELD))

    # Мікросхема давача
    b, w3, h3 = textbox(600, 260, "Si7021 /\nHTU21D\nдавач\nT + RH", size=13, bold=True,
                        fill="#eef2ff", stroke=NEG, min_w=140)
    frags.append(b)
    # живлення давача від 3.3 В вузла
    frags.append(line(600, 150, 600, 260 - h3 / 2, color=FIELD, sw=2.2))

    # Підтяжки на 3.3 В (два резистори до SDA/SCL з боку давача)
    frags.append(text(470, 250, "підтяжки", size=11, color=MUTED))
    frags.append(text(470, 266, "до 3.3 В", size=11, color=MUTED))
    frags.append(line(470, 275, 470, 300, color=FIELD, sw=1.4))
    frags.append(line(455, 300, 485, 300, color=FIELD, sw=1.4))

    # Дві лінії даних від давача (3.3 В сторона) до перетворювачів рівня
    # SDA-3.3 і SCL-3.3
    frags.append(line(600 - w3 / 2, 300, 470, 300, color=NEG, sw=1.6))
    frags.append(text(560, 314, "SDA/SCL @3.3 В", size=11, color=NEG))

    # Перетворювачі рівня (2 × MOSFET BSS138)
    b, w4, h4 = textbox(300, 340, "2× MOSFET\nперетворювач\nрівня\n3.3 ↔ 5 В", size=12, bold=True,
                        fill="#fff7e6", stroke="#b8860b", min_w=150)
    frags.append(b)
    frags.append(arrow(470, 300, 300 + w4 / 2, 320))
    # входи-виходи назовні (5 В сторона)
    frags.append(line(300 - w4 / 2, 340, 150, 340, color=INK, sw=1.6))
    frags.append(text(210, 328, "SDA/SCL", size=12, bold=True))
    frags.append(text(210, 356, "рівень як у VIN", size=11, color=MUTED))

    # Легенда-підпис знизу
    b, _, _ = textbox(W / 2, 435, "назовні: VIN · GND · SDA · SCL  — і все", size=12,
                      fill="#f4f6f8", stroke=MUTED, min_w=380)
    frags.append(b)

    render(os.path.join(IMG, "inside.svg"), W, H, *frags,
           title="Що всередині GY-21: регулятор, давач, перетворювач рівня")


# ── Фігура 2: підключення пін-у-пін до мікроконтролера ──────────────────────
def fig_wiring():
    W, H = 720, 430
    frags = []

    # МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 70, 90, 200, 250
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "мікроконтролер", size=14, bold=True))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "(будь-який I2C-master)", size=11, color=MUTED))

    # Модуль (праворуч)
    mod_x, mod_y, mod_w, mod_h = 450, 90, 200, 250
    frags.append(rect(mod_x, mod_y, mod_w, mod_h, fill="#fbfcfd", stroke=MUTED, sw=2, rx=12))
    frags.append(text(mod_x + mod_w / 2, mod_y + 26, "GY-21", size=15, bold=True))
    frags.append(text(mod_x + mod_w / 2, mod_y + 46, "4 контакти", size=11, color=MUTED))

    rows = [
        # (текст МК, текст модуля, колір, підпис на лінії)
        ("3.3 В / 5 В", "VIN", POS, "живлення"),
        ("GND", "GND", INK, "спільна земля"),
        ("SDA (data)", "SDA", NEG, "дані"),
        ("SCL (clock)", "SCL", NEG, "такт"),
    ]
    y0 = mcu_y + 90
    dy = 52
    for i, (lm, rm, col, lbl) in enumerate(rows):
        y = y0 + i * dy
        # площадка на МК
        b, wl, hl = textbox(mcu_x + mcu_w - 4, y, lm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=110)
        frags.append(b)
        # площадка на модулі
        b, wr, hr = textbox(mod_x + 4, y, rm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=70)
        frags.append(b)
        # провід
        xL = mcu_x + mcu_w - 4 + wl / 2
        xR = mod_x + 4 - wr / 2
        frags.append(line(xL, y, xR, y, color=col, sw=2.2))
        frags.append(text((xL + xR) / 2, y - 12, lbl, size=11, color=MUTED))

    # примітка про підтяжки
    b, _, _ = textbox(W / 2, 392, "SDA/SCL уже підтягнуті на самій платі — зовнішні резистори не потрібні",
                      size=12, fill="#eafaf0", stroke=FIELD, min_w=520)
    frags.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення GY-21 до мікроконтролера (I2C, 4 дроти)")


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    print("OK: inside.svg, wiring.svg")
