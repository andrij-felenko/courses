# -*- coding: utf-8 -*-
"""Фігури для статті GY-63 (барометр MS5611). Вивід у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині модуля (устрій GY-63) ────────────────────────────
def fig_inside():
    W, H = 840, 470
    frags = []

    # Рамка-контур плати
    frags.append(rect(28, 58, W - 56, H - 108, fill="#fbfcfd", stroke=MUTED, sw=2, rx=14))
    frags.append(text(W / 2, 82, "плата модуля GY-63", size=13, color=MUTED))

    # Вхідна клема живлення VCC (3.3..5.5 В)
    b, w1, h1 = textbox(120, 150, "VCC\n3.3–5.5 В", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=100)
    frags.append(b)

    # LDO-регулятор -> 3.3 В
    b, w2, h2 = textbox(330, 150, "LDO 662K\n→ 3.3 В", size=13, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=120)
    frags.append(b)
    frags.append(arrow(120 + w1 / 2, 150, 330 - w2 / 2, 150))

    # Внутрішня шина 3.3 В
    frags.append(line(330 + w2 / 2, 150, 660, 150, color=FIELD, sw=2.2))
    frags.append(text(540, 137, "внутрішні 3.3 В", size=12, color=FIELD))

    # Мікросхема давача MS5611
    b, w3, h3 = textbox(700, 270, "MS5611\nдавач тиску\n+ 24-біт ΔΣ АЦП\n+ PROM-калібр.", size=12, bold=True,
                        fill="#eef2ff", stroke=NEG, min_w=175)
    frags.append(b)
    frags.append(line(700, 150, 700, 270 - h3 / 2, color=FIELD, sw=2.2))

    # Підтяжки на 3.3 В
    frags.append(text(560, 250, "підтяжки", size=11, color=MUTED))
    frags.append(text(560, 266, "SDA/SCL", size=11, color=MUTED))
    frags.append(line(560, 275, 560, 300, color=FIELD, sw=1.4))
    frags.append(line(546, 300, 574, 300, color=FIELD, sw=1.4))

    # Лінії давача (3.3 В сторона) до перетворювача рівня
    frags.append(line(700 - w3 / 2, 305, 560, 305, color=NEG, sw=1.6))
    frags.append(text(645, 320, "шина @3.3 В", size=11, color=NEG))

    # Перетворювач рівня (MOSFET-и)
    b, w4, h4 = textbox(330, 345, "перетворювач\nрівня\n3.3 ↔ VCC", size=12, bold=True,
                        fill="#fff7e6", stroke="#b8860b", min_w=150)
    frags.append(b)
    frags.append(arrow(560, 305, 330 + w4 / 2, 325))
    # виходи назовні
    frags.append(line(330 - w4 / 2, 345, 150, 345, color=INK, sw=1.6))
    frags.append(text(215, 332, "SCL·SDA·SDO·CSB·PS", size=11, bold=True))
    frags.append(text(215, 360, "рівень як у VCC", size=11, color=MUTED))

    # Легенда знизу
    b, _, _ = textbox(W / 2, 435, "назовні 7 контактів: VCC · GND · SCL · SDA · CSB · SDO · PS", size=12,
                      fill="#f4f6f8", stroke=MUTED, min_w=470)
    frags.append(b)

    render(os.path.join(IMG, "inside.svg"), W, H, *frags,
           title="Устрій GY-63: регулятор, давач MS5611, перетворювач рівня")


# ── Фігура 2: підключення пін-у-пін (два режими) ────────────────────────────
def fig_wiring():
    W, H = 860, 470
    frags = []

    # МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 92, 210, 300
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "мікроконтролер", size=14, bold=True))

    # Модуль (праворуч)
    mod_x, mod_y, mod_w, mod_h = 590, 92, 210, 300
    frags.append(rect(mod_x, mod_y, mod_w, mod_h, fill="#fbfcfd", stroke=MUTED, sw=2, rx=12))
    frags.append(text(mod_x + mod_w / 2, mod_y + 26, "GY-63", size=15, bold=True))
    frags.append(text(mod_x + mod_w / 2, mod_y + 46, "7 контактів", size=11, color=MUTED))

    # I2C-рядки (суцільні) + SPI-довідка (штрих)
    rows = [
        ("3.3 / 5 В", "VCC", POS, "живлення", "solid"),
        ("GND", "GND", INK, "спільна земля", "solid"),
        ("SCL", "SCL", NEG, "такт", "solid"),
        ("SDA", "SDA", NEG, "дані (I2C)", "solid"),
        ("→ VCC або нічого", "CSB", MUTED, "вибір адреси 0x76/0x77", "dash"),
    ]
    y0 = mcu_y + 92
    dy = 46
    for i, (lm, rm, col, lbl, style) in enumerate(rows):
        y = y0 + i * dy
        b, wl, hl = textbox(mcu_x + mcu_w - 4, y, lm, size=11, bold=True,
                            fill="#ffffff", stroke=col, min_w=120)
        frags.append(b)
        b, wr, hr = textbox(mod_x + 4, y, rm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=64)
        frags.append(b)
        xL = mcu_x + mcu_w - 4 + wl / 2
        xR = mod_x + 4 - wr / 2
        dash = "5,4" if style == "dash" else None
        frags.append(line(xL, y, xR, y, color=col, sw=2.0, dash=dash))
        frags.append(text((xL + xR) / 2, y - 11, lbl, size=10, color=MUTED))

    # Примітка про PS та SDO (лишити вільними в I2C)
    b, _, _ = textbox(W / 2, 428, "PS лишаємо вільним (I2C за замовчуванням); SDO у режимі I2C не задіяний. Підтяжки вже на платі.",
                      size=11, fill="#eafaf0", stroke=FIELD, min_w=640)
    frags.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення GY-63 по I2C (4 дроти + CSB для адреси)")


# ── Фігура 3: конвеєр вимірювання (команда → пауза → читання → компенсація) ──
def fig_flow():
    W, H = 860, 300
    frags = []

    steps = [
        ("1. Скид\n0x1E", "#fdecea", POS),
        ("2. Читання PROM\nC1…C6 (0xA0…)", "#eef2ff", NEG),
        ("3. Запуск D1/D2\n0x40 / 0x50", "#eafaf0", FIELD),
        ("4. Пауза\n(за OSR)", "#fff7e6", "#b8860b"),
        ("5. Читання АЦП\n0x00 → 24 біти", "#eef2ff", NEG),
        ("6. Компенсація\nT і тиск", "#f4f6f8", INK),
    ]
    n = len(steps)
    bw = 128
    gap = (W - 60 - n * bw) / (n - 1)
    y = 120
    xs = []
    for i, (label, fill, stroke) in enumerate(steps):
        x = 30 + i * (bw + gap) + bw / 2
        xs.append(x)
        b, _, _ = textbox(x, y, label, size=12, bold=True, fill=fill, stroke=stroke, min_w=bw)
        frags.append(b)
    for i in range(n - 1):
        frags.append(arrow(xs[i] + bw / 2, y, xs[i + 1] - bw / 2, y))

    # петля 3→5 (повторюємо для D1 і D2)
    frags.append(text(W / 2, 205, "кроки 3–5 виконуємо двічі: окремо для тиску (D1) і температури (D2)",
                      size=12, color=MUTED))
    frags.append(text(W / 2, 232, "скид і читання PROM — один раз при старті; далі лише цикл вимірювання",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "flow.svg"), W, H, *frags,
           title="Конвеєр одного вимірювання MS5611")


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_flow()
    print("OK: inside.svg, wiring.svg, flow.svg")
