# -*- coding: utf-8 -*-
"""Фігури для статті GY-68 / BMP180 (барометр). Вивід у ./img/.
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
    W, H = 820, 560
    frags = []

    # Рамка-контур плати
    frags.append(rect(24, 54, W - 48, H - 96, fill="#fbfcfd", stroke=MUTED, sw=2, rx=14))
    frags.append(text(W / 2, 80, "плата модуля GY-68", size=13, color=MUTED))

    # Вхідна клема живлення VCC (3.3..5 В)
    b, w1, h1 = textbox(120, 150, "VCC\n3.3–5 В", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=100)
    frags.append(b)

    # LDO-регулятор 662K -> 3.3 В
    b, w2, h2 = textbox(360, 150, "LDO 662K\n→ 3.3 В", size=13, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=130)
    frags.append(b)
    frags.append(arrow(120 + w1 / 2, 150, 360 - w2 / 2, 150))

    # Внутрішня шина 3.3 В до давача
    frags.append(line(360 + w2 / 2, 150, 660, 150, color=FIELD, sw=2.2))
    frags.append(text(560, 136, "внутрішні 3.3 В", size=12, color=FIELD))
    # живлення давача згори
    frags.append(line(660, 150, 660, 210, color=FIELD, sw=2.2))

    # Велика мікросхема давача BMP180 з внутрішніми блоками
    die_x, die_y, die_w, die_h = 470, 210, 320, 190
    frags.append(rect(die_x, die_y, die_w, die_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(die_x + die_w / 2, die_y + 22, "мікросхема BMP180", size=13, bold=True))

    # Внутрішні блоки давача
    b, _, _ = textbox(die_x + 84, die_y + 78, "п'єзо-\nрезистивна\nмембрана\n(тиск)", size=11,
                      fill="#ffffff", stroke=POS, min_w=110)
    frags.append(b)
    b, _, _ = textbox(die_x + 236, die_y + 78, "давач\nтемператури", size=11,
                      fill="#ffffff", stroke=POS, min_w=120)
    frags.append(b)
    b, _, _ = textbox(die_x + 84, die_y + 152, "АЦП +\nлогіка", size=11,
                      fill="#ffffff", stroke=MUTED, min_w=110)
    frags.append(b)
    b, _, _ = textbox(die_x + 236, die_y + 152, "E2PROM:\n11 коеф.\nкалібру­вання", size=11,
                      fill="#fff7e6", stroke="#b8860b", min_w=120)
    frags.append(b)

    # I2C-лінії від давача (3.3 В сторона) до перетворювача рівня
    frags.append(line(die_x, die_y + die_h - 30, 300, die_y + die_h - 30, color=NEG, sw=1.8))
    frags.append(text(392, die_y + die_h - 44, "SDA/SCL @3.3 В", size=11, color=NEG))

    # Перетворювач рівня (2 × MOSFET) + підтяжки
    b, w4, h4 = textbox(180, 380, "2× MOSFET\nперетворювач\nрівня\n+ підтяжки", size=12, bold=True,
                        fill="#fff7e6", stroke="#b8860b", min_w=160)
    frags.append(b)
    frags.append(line(300, die_y + die_h - 30, 180 + w4 / 2, 360, color=NEG, sw=1.8))

    # виходи назовні (сторона VCC)
    frags.append(line(180 - w4 / 2, 400, 90, 400, color=INK, sw=1.8))
    frags.append(line(90, 400, 90, 470, color=INK, sw=1.8))
    b, _, _ = textbox(220, 470, "SDA · SCL назовні — рівень як у VCC", size=12, bold=True,
                      fill="#ffffff", stroke=INK, min_w=300)
    frags.append(b)
    frags.append(line(90, 470, 220 - 150, 470, color=INK, sw=1.8))

    # Адреса на шині
    b, _, _ = textbox(620, 470, "адреса I2C  0x77  (незмінна)", size=12, bold=True,
                      fill="#eef2ff", stroke=NEG, min_w=300)
    frags.append(b)

    # Легенда-підпис знизу
    b, _, _ = textbox(W / 2, 522, "назовні лише 4 контакти:  VCC · GND · SDA · SCL", size=12,
                      fill="#f4f6f8", stroke=MUTED, min_w=420)
    frags.append(b)

    render(os.path.join(IMG, "inside.svg"), W, H, *frags,
           title="Що всередині GY-68: регулятор, давач BMP180, перетворювач рівня")


# ── Фігура 2: підключення пін-у-пін до мікроконтролера ──────────────────────
def fig_wiring():
    W, H = 720, 430
    frags = []

    # МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 90, 210, 250
    frags.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eef2ff", stroke=NEG, sw=2, rx=12))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "мікроконтролер", size=14, bold=True))
    frags.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "(будь-який I2C-master)", size=11, color=MUTED))

    # Модуль (праворуч)
    mod_x, mod_y, mod_w, mod_h = 450, 90, 210, 250
    frags.append(rect(mod_x, mod_y, mod_w, mod_h, fill="#fbfcfd", stroke=MUTED, sw=2, rx=12))
    frags.append(text(mod_x + mod_w / 2, mod_y + 26, "GY-68 (BMP180)", size=14, bold=True))
    frags.append(text(mod_x + mod_w / 2, mod_y + 46, "4 контакти", size=11, color=MUTED))

    rows = [
        ("3.3 В / 5 В", "VCC", POS, "живлення"),
        ("GND", "GND", INK, "спільна земля"),
        ("SDA (data)", "SDA", NEG, "дані"),
        ("SCL (clock)", "SCL", NEG, "такт"),
    ]
    y0 = mcu_y + 92
    dy = 52
    for i, (lm, rm, col, lbl) in enumerate(rows):
        y = y0 + i * dy
        b, wl, hl = textbox(mcu_x + mcu_w - 4, y, lm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=118)
        frags.append(b)
        b, wr, hr = textbox(mod_x + 4, y, rm, size=12, bold=True,
                            fill="#ffffff", stroke=col, min_w=72)
        frags.append(b)
        xL = mcu_x + mcu_w - 4 + wl / 2
        xR = mod_x + 4 - wr / 2
        frags.append(line(xL, y, xR, y, color=col, sw=2.2))
        frags.append(text((xL + xR) / 2, y - 12, lbl, size=11, color=MUTED))

    # примітка про підтяжки/рівень
    b, _, _ = textbox(W / 2, 392, "SDA/SCL уже підтягнуті на платі, рівень безпечний для 3.3 В і 5 В — зовнішнього нічого не треба",
                      size=11, fill="#eafaf0", stroke=FIELD, min_w=600)
    frags.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення GY-68 до мікроконтролера (I2C, 4 дроти)")


# ── Фігура 3: протокол «команда → пауза → читання» (вимір на замовлення) ────
def fig_measure_dance():
    W, H = 860, 470
    frags = []

    # Дві доріжки: температура (зверху) і тиск (знизу)
    track_x0 = 60
    track_x1 = W - 60
    yT = 150
    yP = 320

    def track(y, title, cmd, wait_txt, nbytes, regs, col):
        # підпис доріжки ліворуч, ПОЗА лінією подій
        frags.append(text(track_x0, y - 66, title, size=14, bold=True,
                          anchor="start", color=col))
        # три кроки як окремі рамки з широкими проміжками
        # 1) запис команди
        b, w1, h1 = textbox(track_x0 + 110, y, "запис у 0xF4\n" + cmd, size=12, bold=True,
                            fill="#eef2ff", stroke=col, min_w=170)
        frags.append(b)
        # 2) пауза
        b, w2, h2 = textbox(track_x0 + 355, y, "ПАУЗА\n" + wait_txt, size=12, bold=True,
                            fill="#fff7e6", stroke="#b8860b", min_w=150)
        frags.append(b)
        # 3) читання
        b, w3, h3 = textbox(track_x0 + 620, y, "читання %d байт\n%s" % (nbytes, regs), size=12, bold=True,
                            fill="#eafaf0", stroke=FIELD, min_w=185)
        frags.append(b)
        # стрілки між кроками (по осі доріжки, повз написи)
        frags.append(arrow(track_x0 + 110 + w1 / 2, y, track_x0 + 355 - w2 / 2, y, color=MUTED))
        frags.append(arrow(track_x0 + 355 + w2 / 2, y, track_x0 + 620 - w3 / 2, y, color=MUTED))

    track(yT, "Температура (команда 0x2E)", "0x2E",
          "~5 мс", 2, "0xF6·0xF7", NEG)
    track(yP, "Тиск (команда 0x34 + OSS<<6)", "0x34+OSS<<6",
          "5–26 мс за OSS", 3, "0xF6·0xF7·0xF8", POS)

    # Нижній підпис-висновок, окремо, з відступом
    b, _, _ = textbox(W / 2, H - 42,
                      "давач готує результат НА ЗАМОВЛЕННЯ: читати до кінця паузи — значить читати недороблене",
                      size=12, fill="#f4f6f8", stroke=MUTED, min_w=680)
    frags.append(b)

    render(os.path.join(IMG, "measure-dance.svg"), W, H, *frags,
           title="Вимір BMP180: команда → пауза → читання (те саме для T і P)")


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_measure_dance()
    print("OK: inside.svg, wiring.svg, measure-dance.svg")
