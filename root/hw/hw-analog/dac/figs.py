# -*- coding: utf-8 -*-
"""Фігури до вставки «Зовнішній ЦАП MCP4725-класу» (тема «ЦАП»).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#b8860b"   # колір чипа-ЦАП (тепла лінія сигналу)


# ── 1. Усередині модуля: I²C → регістр → драбина → буфер → OUT, плюс EEPROM ───
def fig_board():
    W, H = 860, 380
    f = [text(W / 2, 28, "Усередині модуля MCP4725: число по I²C стає чистою напругою",
              size=16, bold=True),
         text(W / 2, 50, "дві лінії I²C → 12-бітний регістр → драбина ЦАП → буфер → єдиний вихід; "
                         "EEPROM тримає значення між увімкненнями",
              size=11, color=MUTED)]

    # вхід: живлення (= Vref) і шина I²C
    f.append(rect(12, 166, 136, 48, fill=FILL, stroke=LINE, sw=1.5))
    f.append(mtext(80, 186, ["VCC / GND", "(живлення = Vref)"], size=12, color=INK))
    f.append(rect(12, 266, 136, 48, fill="#e8f0fe", stroke=NEG, sw=1.5))
    f.append(mtext(80, 286, ["SDA / SCL", "(I²C, до 400 кГц)"], size=12, color=INK))

    # регістр (12 біт)
    f.append(rect(287, 184, 106, 72, fill="#fff7e6", stroke=GOLD, sw=1.5))
    f.append(mtext(340, 208, ["12-бітний", "регістр", "(0…4095)"], size=13, color=INK))
    f.append(arrow(148, 290, 280, 232, color=NEG, sw=1.8))   # I²C → регістр
    f.append(arrow(148, 190, 280, 214, color=MUTED, sw=1.6))  # живлення → (Vref)
    f.append(text(205, 196, "Vref = VCC", size=10, color=MUTED))

    # EEPROM під регістром
    f.append(rect(273, 290, 134, 58, fill="#f0fff0", stroke=FIELD, sw=1.5))
    f.append(mtext(340, 309, ["EEPROM", "(тримає значення", "між увімкненнями)"], size=11, color=INK))
    f.append(arrow(340, 290, 340, 258, color=FIELD, sw=1.8))
    f.append(mtext(352, 280, ["відновлює", "при старті"], size=9, color=FIELD, anchor="start"))

    # драбина R-2R
    f.append(arrow(393, 220, 530, 220, color=GOLD, sw=1.8))
    f.append(rect(556, 180, 88, 80, fill=FILL, stroke=LINE, sw=1.5))
    f.append(mtext(600, 200, ["Драбина", "R-2R", "(аналогова", "схема)"], size=12, color=INK))

    # буфер → вихід OUT
    f.append(arrow(644, 220, 730, 220, color=LINE, sw=1.8))
    f.append(text(688, 208, "буфер", size=10, color=MUTED))
    f.append(rect(760, 195, 62, 50, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(mtext(791, 216, ["OUT", "0…VCC"], size=13, color=INK, bold=True))

    # нижня плашка: Vref = VCC
    b = fitbox(100, 340, 660, 28, "Vref = VCC: точність виходу прямо залежить від стабільності живлення.",
               size=11, fill="#fff8e6", stroke="#cca43a")
    f.append(b)

    render(os.path.join(IMG, "board.svg"), W, H, *f)


# ── 2. Підключення до ESP32: дві лінії I²C (спільні) + єдиний вихід OUT ───────
def fig_wiring():
    W, H = 920, 400
    f = [text(W / 2, 28, "Підключення MCP4725 до ESP32: дві лінії I²C і єдиний вихід",
              size=16, bold=True),
         text(W / 2, 50, "VCC = Vref; A0→GND → адреса 0x60; OUT дає чисту напругу 0…3.3 В без RC-фільтра",
              size=11, color=MUTED)]

    # ESP32 ліворуч
    f.append(rect(40, 80, 180, 240, fill="#e8f0fe", stroke=NEG, sw=1.5))
    f.append(mtext(130, 130, ["ESP32", "──────", "SDA = 21", "SCL = 22",
                              "VCC (3.3 В)", "GND"], size=13, color=INK))

    # підтяжки на шині
    f.append(rect(290, 130, 90, 44, fill="#fff7e6", stroke=GOLD, sw=1.5))
    f.append(mtext(335, 149, ["4.7 кОм", "(підтяжки)"], size=10, color=INK))
    f.append(text(335, 116, "SDA", size=11, color=NEG, bold=True))
    f.append(text(335, 190, "SCL", size=11, color=NEG, bold=True))
    f.append(line(220, 155, 290, 145, color=NEG, sw=2))
    f.append(line(380, 145, 480, 145, color=NEG, sw=2))
    f.append(line(220, 185, 290, 165, color=NEG, sw=2))
    f.append(line(380, 165, 480, 165, color=NEG, sw=2))

    # MCP4725 праворуч
    f.append(rect(480, 80, 160, 240, fill="#fff7e6", stroke=GOLD, sw=1.5))
    f.append(mtext(560, 130, ["MCP4725", "──────", "SDA", "SCL",
                              "VCC = Vref", "GND", "A0→GND (0x60)"], size=12, color=INK))

    # живлення й земля
    f.append(line(220, 105, 480, 105, color=POS, sw=2))
    f.append(text(350, 98, "VCC 3.3 В (= Vref)", size=10, color=POS, bold=True))
    f.append(line(220, 300, 480, 300, color=MUTED, sw=2))
    f.append(text(350, 316, "GND", size=10, color=MUTED))

    # вихід OUT
    f.append(line(640, 200, 720, 200, color=FIELD, sw=2))
    f.append(arrow(700, 200, 752, 200, color=FIELD, sw=2))
    f.append(rect(754, 164, 112, 72, fill="#f0fff0", stroke=FIELD, sw=1.5))
    f.append(mtext(810, 182, ["OUT", "0…3.3 В", "(чиста напруга,", "без RC-фільтра)"], size=11, color=INK))

    # нижня плашка
    b = fitbox(60, 348, 840, 36,
               "Та сама картина I²C, що й в інших модулів. Вихід чистий одразу — без RC-фільтра; "
               "працює навіть на чипах, де вбудованого ЦАП нема (S3/C3/C6).",
               size=10, fill="#f0fff0", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_board()
    fig_wiring()
    print("OK: 2 figures ->", IMG)
