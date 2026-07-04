# -*- coding: utf-8 -*-
"""Фігури для статті GY-BMP280 (барометр BMP280). Вивід у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: устрій — чип, два інтерфейси, роль пінів CSB/SDO ───────────────
def fig_inside():
    W, H = 900, 560
    frags = []

    # Контур плати
    frags.append(rect(30, 62, W - 60, H - 96, fill="#fbfcfd", stroke=MUTED, sw=2, rx=14))
    frags.append(text(150, 86, "плата модуля GY-BMP280", size=13, color=MUTED))
    frags.append(text(760, 86, "живлення й логіка — рівно 3.3 В", size=12, color=POS))

    # Центральний чип BMP280
    b, wc, hc = textbox(300, 250, "BMP280\nчип Bosch\n(тиск + T)\nвся математика\nвсередині", size=13,
                        bold=True, fill="#eef2ff", stroke=NEG, min_w=180)
    frags.append(b)

    # Живлення VCC 3.3 В зверху
    b, wv, hv = textbox(300, 130, "VCC 3.3 В", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=130)
    frags.append(b)
    frags.append(line(300, 130 + hv / 2, 300, 250 - hc / 2, color=POS, sw=2.2))

    # GND знизу
    b, wg, hg = textbox(300, 400, "GND", size=13, bold=True,
                        fill="#f4f6f8", stroke=INK, min_w=130)
    frags.append(b)
    frags.append(line(300, 250 + hc / 2, 300, 400 - hg / 2, color=INK, sw=2.2))

    # Блок «немає на борту» — праворуч від VCC (окремим боксом, з запасом)
    b, _, _ = textbox(690, 150, "НЕМА регулятора\nНЕМА перетворювача рівня\n→ тільки 3.3 В на все", size=12,
                      bold=True, fill="#fff7e6", stroke="#b8860b", min_w=300)
    frags.append(b)

    # Дві лінії інтерфейсу праворуч від чипа: SCL/SCK і SDA/SDI
    x_from = 300 + wc / 2
    # SCL / SCK
    frags.append(line(x_from, 220, 560, 220, color=NEG, sw=2.0))
    b, wS, hS = textbox(640, 220, "SCL / SCK\n(такт)", size=12, bold=True,
                        fill="#ffffff", stroke=NEG, min_w=150)
    frags.append(b)
    frags.append(line(560, 220, 640 - wS / 2, 220, color=NEG, sw=2.0))
    # SDA / SDI
    frags.append(line(x_from, 280, 560, 280, color=NEG, sw=2.0))
    b, wD, hD = textbox(640, 280, "SDA / SDI\n(дані від MK)", size=12, bold=True,
                        fill="#ffffff", stroke=NEG, min_w=150)
    frags.append(b)
    frags.append(line(560, 280, 640 - wD / 2, 280, color=NEG, sw=2.0))

    # SDO — подвійна роль
    frags.append(line(x_from, 340, 560, 340, color=FIELD, sw=2.0))
    b, wO, hO = textbox(690, 355, "SDO\nI2C: вибір адреси\n(низ→0x76, верх→0x77)\nSPI: вихід MISO", size=12,
                        bold=True, fill="#eafaf0", stroke=FIELD, min_w=300)
    frags.append(b)
    frags.append(line(560, 340, 690 - wO / 2, 355, color=FIELD, sw=2.0))

    # CSB — вибір інтерфейсу
    frags.append(line(x_from, 190, 560, 190, color="#b8860b", sw=2.0))
    b, wB, hB = textbox(700, 470, "CSB\nверх→I2C\nниз (такт)→SPI", size=12,
                        bold=True, fill="#fff7e6", stroke="#b8860b", min_w=250)
    frags.append(b)
    frags.append(line(560, 190, 700 - wB / 2, 470 - hB / 2, color="#b8860b", sw=1.6))

    render(os.path.join(IMG, "inside.svg"), W, H, *frags,
           title="Устрій GY-BMP280: чип, два інтерфейси, ролі CSB і SDO")


# ── Фігура 2: підключення пін-у-пін по I²C (з наголосом на 3.3 В та CSB) ─────
def fig_wiring():
    W, H = 820, 470
    frags = []

    # МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 92, 220, 300
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "мікроконтролер", size=14, bold=True))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "живлення й логіка 3.3 В", size=11, color=POS))

    # Модуль (праворуч)
    mod_x, mod_y, mod_w, mod_h = 540, 92, 220, 300
    frags.append(rect(mod_x, mod_y, mod_w, mod_h, fill="#fbfcfd", stroke=MUTED, sw=2, rx=12))
    frags.append(text(mod_x + mod_w / 2, mod_y + 26, "GY-BMP280", size=15, bold=True))
    frags.append(text(mod_x + mod_w / 2, mod_y + 46, "6 контактів", size=11, color=MUTED))

    rows = [
        ("3.3 В", "VCC", POS, "тільки 3.3 В"),
        ("GND", "GND", INK, "спільна земля"),
        ("SCL", "SCL", NEG, "такт"),
        ("SDA", "SDA", NEG, "дані"),
        ("3.3 В", "CSB", "#b8860b", "тягнемо вгору → I2C"),
        ("(нічого)", "SDO", FIELD, "вільний → адреса 0x76"),
    ]
    y0 = mcu_y + 84
    dy = 42
    for i, (lm, rm, col, lbl) in enumerate(rows):
        y = y0 + i * dy
        b, wl, hl = textbox(mcu_x + mcu_w - 4, y, lm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=104)
        frags.append(b)
        b, wr, hr = textbox(mod_x + 4, y, rm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=74)
        frags.append(b)
        xL = mcu_x + mcu_w - 4 + wl / 2
        xR = mod_x + 4 - wr / 2
        frags.append(line(xL, y, xR, y, color=col, sw=2.2))
        frags.append(text((xL + xR) / 2, y - 11, lbl, size=11, color=MUTED))

    # застереження знизу
    b, _, _ = textbox(W / 2, 436,
                      "5 В уб'є модуль: на борту нема ні регулятора, ні перетворювача рівня — живимо й керуємо тільки 3.3 В",
                      size=12, bold=True, fill="#fdecea", stroke=POS, min_w=700)
    frags.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення GY-BMP280 по I2C (6 контактів, рівень 3.3 В)")


# ── Фігура 3: лінія часу родини барометрів Bosch ────────────────────────────
def fig_family_timeline():
    W, H = 980, 470
    frags = []

    # Вісь часу
    axis_y = 150
    x0, x1 = 70, W - 40
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(text(x1 - 4, axis_y - 12, "час →", size=12, color=MUTED, anchor="end"))

    # Позиції за роками (нерівномірно — просто рознесені для читабельності)
    # (рік, назва, підпис-суть, колір рамки, «вгору»/«вниз» відносно осі)
    nodes = [
        (108, "BMP085",      "2008–09\nбарометр-на-чипі\n(спадкоємець SMD500)", NEG,   True),
        (300, "смартфон",     "2011\nGalaxy Nexus:\nбарометр → допомога GPS", "#b8860b", False),
        (470, "BMP280",      "2012\nнове покоління:\n0.16 Па, −4× струм",  POS,   True),
        (640, "BMP180",      "2013\nтой самий, але\nменший і дешевший",   MUTED, False),
        (800, "BME280",      "2014\n+ вологість\n(P → E: середовище)",     FIELD, True),
    ]
    # напрямок BMP180/BMP280 у часі трохи «змішаний» (280 вийшов раніше 180) —
    # тому 280 і 180 стоять поруч; над віссю показуємо це підписом.

    for x, name, sub, col, up in nodes:
        frags.append(circle(x, axis_y, 8, fill=col, stroke=col, sw=2))
        if up:
            cy = axis_y - 78
        else:
            cy = axis_y + 82
        b, wb, hb = textbox(x, cy, name + "\n" + sub, size=12, bold=False,
                            fill="#ffffff", stroke=col, min_w=150)
        # перший рядок (назву) зробимо жирним окремим написом поверх
        frags.append(b)
        # лінія-виноска від точки до рамки
        if up:
            frags.append(line(x, axis_y - 8, x, cy + hb / 2, color=col, sw=1.6))
        else:
            frags.append(line(x, axis_y + 8, x, cy - hb / 2, color=col, sw=1.6))

    # Наскрізна нитка знизу
    b, _, _ = textbox(W / 2, H - 34,
                      "наскрізна мета всіх поколінь: розрізнити ще дрібнішу зміну висоти — "
                      "поверх → сходинку → крок → долоню",
                      size=12, bold=True, fill="#eef2ff", stroke=NEG, min_w=760)
    frags.append(b)

    render(os.path.join(IMG, "family.svg"), W, H, *frags,
           title="Родина барометрів Bosch: від BMP085 до BME280")


# ── Фігура 4: як обирати серед варіантів ────────────────────────────────────
def fig_choose():
    W, H = 1000, 440
    frags = []

    # Питання-корінь
    b, wq, hq = textbox(W / 2, 76, "потрібна вологість повітря?", size=15, bold=True,
                        fill="#fff7e6", stroke="#b8860b", min_w=340)
    frags.append(b)

    # Гілка «так» → BME280 (ліворуч)
    b, wy, hy = textbox(210, 205, "ТАК", size=13, bold=True,
                        fill="#eaf6ec", stroke=FIELD, min_w=90)
    frags.append(b)
    frags.append(line(W / 2 - 90, 76 + hq / 2, 210, 205 - hy / 2, color=FIELD, sw=2))
    b, _, hb1 = textbox(210, 300, "BME280\nтиск + T + вологість\n(перевір 0xD0 = 0x60)", size=12,
                        bold=True, fill="#ffffff", stroke=FIELD, min_w=250)
    frags.append(b)
    frags.append(line(210, 205 + hy / 2, 210, 300 - hb1 / 2, color=FIELD, sw=1.8))

    # Гілка «ні» → далі питання про сантиметри (праворуч)
    b, wn, hn = textbox(680, 195, "НІ:\nчи ловиш сантиметри\nвисоти (дрон/ракета)?", size=12,
                        bold=True, fill="#eef2ff", stroke=NEG, min_w=250)
    frags.append(b)
    frags.append(line(W / 2 + 90, 76 + hq / 2, 680, 195 - hn / 2, color=NEG, sw=2))

    # → ні → BMP280
    b, _, hb2 = textbox(560, 335, "BMP280\nтиск + T, дешево й ощадливо\n(вибір за замовчуванням)", size=12,
                        bold=True, fill="#ffffff", stroke=POS, min_w=270)
    frags.append(b)
    frags.append(line(630, 195 + hn / 2, 560, 335 - hb2 / 2, color=POS, sw=1.8))
    frags.append(text(548, 262, "звичайна точність", size=11, color=MUTED, anchor="end"))

    # → так → BMP388/390
    b, wb3, hb3 = textbox(838, 335, "BMP388 / BMP390\n±0.5…0.25 м\n(точний висотомір)", size=12,
                          bold=True, fill="#ffffff", stroke=NEG, min_w=210)
    frags.append(b)
    frags.append(line(730, 195 + hn / 2, 838, 335 - hb3 / 2, color=NEG, sw=1.8))
    frags.append(text(838 - wb3 / 2 - 6, 262, "потрібні см", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "choose.svg"), W, H, *frags,
           title="Як обрати барометр Bosch під задачу")


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_family_timeline()
    fig_choose()
    print("OK: inside.svg, wiring.svg, family.svg, choose.svg")
