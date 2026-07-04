# -*- coding: utf-8 -*-
"""Фігури для статті GY-MAX30102 (давач пульсу/SpO2). Вивід у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: принцип — світло крізь палець, пульсова хвиля у відбитому світлі ─
def fig_ppg():
    W, H = 940, 620
    frags = []

    # Палець (напівовал зверху)
    fx, fy, fw, fh = 300, 90, 340, 150
    frags.append(rect(fx, fy, fw, fh, fill="#fdeceb", stroke="#c98b86", sw=2, rx=60))
    frags.append(text(fx + fw / 2, fy + 34, "палець (тканина + кров)", size=14, bold=True))
    frags.append(text(fx + fw / 2, fy + 56, "у судинах — пульсова хвиля крові", size=12, color=MUTED))

    # Червоні кульки-«кров» усередині
    for cx in (360, 420, 480, 540):
        frags.append(circle(cx, fy + 100, 7, fill="#e0554c", stroke="#c0392b", sw=1.5))

    # Світлодіоди знизу зліва: RED і IR
    b, wr, hr = textbox(250, 330, "RED\n660 нм\n(червоний)", size=12, bold=True,
                        fill="#fdecea", stroke=POS, min_w=120)
    frags.append(b)
    b, wi, hi = textbox(400, 330, "IR\n880 нм\n(інфрачервоний)", size=12, bold=True,
                        fill="#eef2ff", stroke=NEG, min_w=140)
    frags.append(b)

    # Промені вгору в палець
    frags.append(arrow(250, 330 - hr / 2, 300, fy + fh + 6, color=POS, sw=2.0))
    frags.append(arrow(400, 330 - hi / 2, 430, fy + fh + 6, color=NEG, sw=2.0))

    # Фотодіод справа знизу — ловить ВІДБИТЕ світло
    b, wp, hp = textbox(600, 330, "фотодіод\nловить ВІДБИТЕ\nсвітло", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=170)
    frags.append(b)
    frags.append(arrow(540, fy + fh + 6, 600, 330 - hp / 2, color=FIELD, sw=2.0))

    # Підпис «відбивна схема»
    frags.append(text(W / 2, 232 + fh + 40, "усі три — на ОДНОМУ боці пальця (відбивна схема, не просвіт)",
                      size=12, color=MUTED))

    # Крива PPG знизу — пульсова хвиля
    gx, gy, gw, gh = 70, 470, W - 140, 110
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(gx + 10, gy + 20, "світло на фотодіоді в часі →", size=12, color=MUTED, anchor="start"))
    # проста хвиля з різкими підйомами (систола)
    import math
    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        x = gx + 20 + t * (gw - 40)
        # серцебиття: різкий пік раз на «удар»
        phase = (t * 3.0) % 1.0
        base = math.exp(-((phase - 0.15) ** 2) / 0.004) * 0.8
        dic = math.exp(-((phase - 0.42) ** 2) / 0.010) * 0.28
        y = gy + gh - 22 - (base + dic) * (gh - 44)
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(pts), POS))
    frags.append(text(gx + gw - 12, gy + gh - 8,
                      "кожен пік = удар серця; висота піків RED vs IR → SpO2",
                      size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "ppg.svg"), W, H, *frags,
           title="Як MAX30102 бачить пульс: світло, кров, відбитий сигнал")


# ── Фігура 2: устрій модуля — чип, регулятори на борту, шина I²C ─────────────
def fig_inside():
    W, H = 940, 560
    frags = []

    # Контур плати
    frags.append(rect(30, 62, W - 60, H - 96, fill="#fbfcfd", stroke=MUTED, sw=2, rx=14))
    frags.append(text(180, 86, "плата модуля GY-MAX30102", size=13, color=MUTED))
    frags.append(text(770, 86, "VIN терпить 3.3–5 В", size=12, color=POS))

    # Регулятори на борту (ліворуч) — головна відмінність від «голих» GY-плат
    b, wreg, hreg = textbox(200, 200, "регулятори НА БОРТУ\n1.8 В — для чипа\n(окремо живить світлодіоди)\n→ VIN 3.3…5 В безпечно", size=12,
                            bold=True, fill="#fff7e6", stroke="#b8860b", min_w=300)
    frags.append(b)

    # VIN зверху
    b, wv, hv = textbox(200, 120, "VIN 3.3–5 В", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=140)
    frags.append(b)
    frags.append(line(200, 120 + hv / 2, 200, 200 - hreg / 2, color=POS, sw=2.2))

    # Центральний чип MAX30102
    b, wc, hc = textbox(560, 250, "MAX30102\nчип Maxim\nRED+IR світлодіоди\n+ фотодіод\n+ 18-біт АЦП\n+ FIFO на 32", size=13,
                        bold=True, fill="#eef2ff", stroke=NEG, min_w=210)
    frags.append(b)

    # 1.8В від регулятора до чипа
    frags.append(arrow(200 + wreg / 2, 200, 560 - wc / 2, 250, color="#b8860b", sw=2.0))
    frags.append(text((200 + wreg / 2 + 560 - wc / 2) / 2, 214, "1.8 В", size=11, color="#b8860b"))

    # GND знизу під чипом
    b, wg, hg = textbox(560, 430, "GND", size=13, bold=True,
                        fill="#f4f6f8", stroke=INK, min_w=120)
    frags.append(b)
    frags.append(line(560, 250 + hc / 2, 560, 430 - hg / 2, color=INK, sw=2.2))

    # Лінії I²C праворуч
    x_from = 560 + wc / 2
    frags.append(line(x_from, 225, 720, 225, color=FIELD, sw=2.0))
    b, wS, hS = textbox(800, 225, "SCL\n(такт I2C)", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=140)
    frags.append(b)
    frags.append(line(720, 225, 800 - wS / 2, 225, color=FIELD, sw=2.0))

    frags.append(line(x_from, 275, 720, 275, color=FIELD, sw=2.0))
    b, wD, hD = textbox(800, 275, "SDA\n(дані I2C)", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=140)
    frags.append(b)
    frags.append(line(720, 275, 800 - wD / 2, 275, color=FIELD, sw=2.0))

    # INT — окремою лінією нижче
    frags.append(line(x_from, 335, 720, 335, color=NEG, sw=2.0))
    b, wN, hN = textbox(800, 345, "INT\nсигнал «дані готові»\n(активний низьким)", size=12,
                        bold=True, fill="#ffffff", stroke=NEG, min_w=210)
    frags.append(b)
    frags.append(line(720, 335, 800 - wN / 2, 345, color=NEG, sw=2.0))

    # Адреса — окремою рамкою внизу зліва
    b, _, _ = textbox(200, 380, "адреса I2C — одна\n0x57 (7-біт), незмінна\n→ один чип на шину", size=12,
                      bold=True, fill="#eef2ff", stroke=NEG, min_w=260)
    frags.append(b)

    render(os.path.join(IMG, "inside.svg"), W, H, *frags,
           title="Устрій GY-MAX30102: чип, регулятори на борту, шина I2C")


# ── Фігура 3: підключення пін-у-пін по I²C ──────────────────────────────────
def fig_wiring():
    W, H = 860, 470
    frags = []

    # МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 92, 230, 300
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "мікроконтролер", size=14, bold=True))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "3.3 В або 5 В — обидва добре", size=11, color=POS))

    # Модуль (праворуч)
    mod_x, mod_y, mod_w, mod_h = 560, 92, 240, 300
    frags.append(rect(mod_x, mod_y, mod_w, mod_h, fill="#fbfcfd", stroke=MUTED, sw=2, rx=12))
    frags.append(text(mod_x + mod_w / 2, mod_y + 26, "GY-MAX30102", size=15, bold=True))
    frags.append(text(mod_x + mod_w / 2, mod_y + 46, "7 контактів", size=11, color=MUTED))

    rows = [
        ("3.3/5 В", "VIN", POS, "живлення (є регулятор)"),
        ("GND", "GND", INK, "спільна земля"),
        ("SCL", "SCL", FIELD, "такт I2C"),
        ("SDA", "SDA", FIELD, "дані I2C"),
        ("GPIO", "INT", NEG, "переривання (не обов'язково)"),
    ]
    y0 = mcu_y + 92
    dy = 48
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
        frags.append(text((xL + xR) / 2, y - 12, lbl, size=11, color=MUTED))

    # застереження знизу
    b, _, _ = textbox(W / 2, 436,
                      "піни RD/IRD (керування світлодіодами) лишаємо вільними — усім керує чип по I2C",
                      size=12, bold=True, fill="#eafaf0", stroke=FIELD, min_w=700)
    frags.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення GY-MAX30102 по I2C (VIN терпить 3.3–5 В)")


if __name__ == "__main__":
    fig_ppg()
    fig_inside()
    fig_wiring()
    print("OK: ppg.svg, inside.svg, wiring.svg")
