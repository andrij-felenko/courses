# -*- coding: utf-8 -*-
"""
Фігури для вставки 4.7.6c — «Зовнішній ЦАП MCP4725-класу (I²C)».
Окремий файл; не чіпає наявний figs.py розділу.
Вивід → ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *  # noqa: F401,F403  textbox, fitbox, arrow, mtext, render, ...

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.7.6c.1  —  Блок-схема плати MCP4725-класу
# fig-25-6c-1-board.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_6c1_board():
    W, H = 860, 380

    frags = []

    # ── Заголовок ──────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Усередині модуля MCP4725: «ЦАП у коробочці» з пам'яттю",
                       size=16, bold=True))
    frags.append(text(W / 2, 50,
                       "дві лінії I²C → регістр → драбина ЦАП → буфер → вихід; EEPROM зберігає значення між увімкненнями",
                       size=11, color=MUTED))

    # ── Блок VCC/GND (ліво) ────────────────────────────────────────────────
    tb, tw, th = textbox(80, 190, "VCC / GND\n(живлення = Vref)",
                          size=12, fill=FILL, stroke=LINE, pad=10)
    frags.append(tb)

    # ── I²C-інтерфейс ──────────────────────────────────────────────────────
    tb2, tw2, th2 = textbox(80, 290, "SDA / SCL\n(I²C, до 400 кГц)",
                              size=12, fill="#e8f0fe", stroke=NEG, pad=10)
    frags.append(tb2)

    # ── Стрілки від I²C у 12-бітний регістр ───────────────────────────────
    frags.append(arrow(140, 290, 270, 240, color=NEG))

    # ── 12-бітний ЦАП-регістр ─────────────────────────────────────────────
    tb3, tw3, th3 = textbox(340, 220, "12-бітний\nЦАП-регістр\n(0…4095)",
                              size=13, fill="#fff7e6", stroke="#b8860b", pad=12, bold=False)
    frags.append(tb3)

    # ── EEPROM (нижче, зі стрілкою вверх у регістр) ────────────────────────
    tb4, tw4, th4 = textbox(340, 320, "EEPROM\n(зберігає значення\nміж увімкненнями)",
                              size=11, fill="#f0fff0", stroke=FIELD, pad=10)
    frags.append(tb4)
    frags.append(arrow(340, 303, 340, 255, color=FIELD))
    frags.append(text(350, 285, "відновлює\nпри старті", size=9, color=FIELD, anchor="start"))

    # ── Стрілка: регістр → Драбина ЦАП ───────────────────────────────────
    frags.append(arrow(340 + tw3 / 2, 220, 530, 220, color="#b8860b"))

    # ── R-2R Драбина (символічно) ─────────────────────────────────────────
    tb5, tw5, th5 = textbox(600, 220, "Драбина\nR-2R\n(аналогова\nсхема)",
                              size=12, fill=FILL, stroke=LINE, pad=10)
    frags.append(tb5)

    # ── Буфер → OUT ───────────────────────────────────────────────────────
    frags.append(arrow(600 + tw5 / 2, 220, 730, 220, color=LINE))
    tb6, tw6, th6 = textbox(790, 220, "OUT\n0…VCC",
                              size=13, fill="#fdecea", stroke=POS, pad=10, bold=True)
    frags.append(tb6)

    # ── Підпис вузла: буфер ────────────────────────────────────────────────
    frags.append(text(730, 208, "буфер", size=10, color=MUTED, anchor="middle"))

    # ── Стрілка VCC ↓ до регістра (Vref) ──────────────────────────────────
    frags.append(arrow(140, 190, 270, 215, color=MUTED))
    frags.append(text(200, 196, "Vref = VCC", size=10, color=MUTED, anchor="middle"))

    # ── Примітка знизу ────────────────────────────────────────────────────
    note = fitbox(100, 340, W - 200, 28,
                  "Vref = VCC: точність виходу прямо залежить від стабільності живлення.",
                  size=11, fill="#fff8e6", stroke="#cca43a")
    frags.append(note)

    render(os.path.join(OUT, "fig-25-6c-1-board.svg"), W, H, *frags,
           title=None)
    print("wrote fig-25-6c-1-board.svg")


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.7.6c.2  —  Схема підключення модуля до ESP32
# fig-25-6c-2-wiring.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_6c2_wiring():
    W, H = 920, 400

    frags = []

    # ── Заголовок ──────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Підключення MCP4725 до ESP32: дві лінії I²C + єдиний вихід",
                       size=16, bold=True))
    frags.append(text(W / 2, 50,
                       "VCC=Vref; A0→GND → адреса 0x60; OUT → чисту напругу 0…3.3 В без RC-фільтра",
                       size=11, color=MUTED))


    # ── Блок ESP32 ─────────────────────────────────────────────────────────
    frags.append(fitbox(40, 80, 180, 240,
                         "ESP32\n──────\nSDA = 21\nSCL = 22\nVCC (3.3 В)\nGND",
                         size=13, fill="#e8f0fe", stroke=NEG))

    # ── Підтяжки (між ESP32 і MCP4725) ────────────────────────────────────
    frags.append(fitbox(290, 130, 90, 44,
                         "4.7 кОм\n(підтяжки)",
                         size=10, fill="#fff7e6", stroke="#b8860b"))
    frags.append(text(335, 116, "SDA", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(335, 188, "SCL", size=11, color=NEG, anchor="middle", bold=True))

    # ── Горизонтальні лінії I²C ───────────────────────────────────────────
    # SDA: ESP32 → підтяжка → MCP4725
    frags.append(line(220, 155, 290, 145, color=NEG, sw=2))
    frags.append(line(380, 145, 480, 145, color=NEG, sw=2))
    # SCL: ESP32 → підтяжка → MCP4725
    frags.append(line(220, 185, 290, 165, color=NEG, sw=2))
    frags.append(line(380, 165, 480, 165, color=NEG, sw=2))

    # ── Блок MCP4725 ───────────────────────────────────────────────────────
    frags.append(fitbox(480, 80, 160, 240,
                         "MCP4725\n──────\nSDA\nSCL\nVCC=Vref\nGND\nA0→GND\n(0x60)",
                         size=12, fill="#fff7e6", stroke="#b8860b"))

    # ── VCC та GND ─────────────────────────────────────────────────────────
    frags.append(line(220, 105, 480, 105, color=POS, sw=2))
    frags.append(text(350, 98, "VCC 3.3 В (= Vref)", size=10, color=POS, anchor="middle", bold=True))
    frags.append(line(220, 300, 480, 300, color=MUTED, sw=2))
    frags.append(text(350, 316, "GND", size=10, color=MUTED, anchor="middle"))

    # ── A0 → GND (усередині блоку MCP показано текстом «A0→GND») ──────────
    # просто додаткова анотація поряд з OUT
    frags.append(text(565, 348, "адреса = 0x60", size=10, color="#b8860b", anchor="middle"))

    # ── OUT → навантаження ────────────────────────────────────────────────
    frags.append(arrow(640, 200, 720, 200, color=FIELD, sw=2))
    tb_out, _, _ = textbox(810, 200, "OUT\n0…3.3 В\n(чиста напруга,\nбез RC-фільтра)",
                             size=11, fill="#f0fff0", stroke=FIELD, pad=9)
    frags.append(tb_out)

    # ── Порівняльна нотатка: відміна від §4.7.4 ───────────────────────────
    note = fitbox(60, 348, W - 80, 36,
                  "На відміну від «ЦАП для бідних» (§4.7.4): жодного RC-фільтра — вихід одразу чистий. Працює навіть там, де вбудованого ЦАП нема (S3/C3/C6).",
                  size=10, fill="#f0fff0", stroke=FIELD)
    frags.append(note)

    render(os.path.join(OUT, "fig-25-6c-2-wiring.svg"), W, H, *frags,
           title=None)
    print("wrote fig-25-6c-2-wiring.svg")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_6c1_board()
    fig_6c2_wiring()
    print("done.")
