# -*- coding: utf-8 -*-
"""Фігури об'єкта «Bluetooth-модуль HC-05/HC-06» (catalog/connect/radio).
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: устрій модуля — платка-донька на платі-носії ────────────────────
# Донька: BC417 + flash + антена (усе на 3.3 В). Носій: регулятор 3.3 В, дільник
# на RX, підтяжки. MCU говорить із модулем звичайним UART.
def fig_block():
    W, H = 760, 400
    parts = []

    # MCU зліва
    parts.append(fitbox(30, 165, 118, 70, "Ваш MCU\n(Arduino, ESP32,\nSTM32…)",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))

    # межа плати-носія — пунктирна рамка
    parts.append(rect(210, 70, 470, 280, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(445, 58, "плата-носій (breakout: ZS-040 / JY-MCU)", 12, MUTED, "middle"))

    # регулятор 3.3 В на носії
    parts.append(fitbox(232, 285, 150, 46, "регулятор 3.3 В\n(тому VCC = 3.6…6 В)",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    # платка-донька (екранована, на 3.3 В)
    parts.append(rect(420, 95, 236, 175, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    parts.append(text(538, 112, "платка-донька (уся на 3.3 В)", 11, FIELD, "middle", bold=True))

    # чип BC417
    parts.append(fitbox(438, 128, 118, 66, "CSR BC417\n(радіо + ядро +\nстек Bluetooth)",
                        size=11, fill="#ffffff", stroke=INK, sw=1.6, color=INK, bold=True))
    # flash
    parts.append(fitbox(438, 210, 118, 40, "flash: прошивка\n(HC-05 / HC-06)",
                        size=10, fill="#ffffff", stroke=INK, sw=1.3, color=INK))
    # антена (доріжкова, символом праворуч усередині доньки)
    ax = 622
    parts.append(line(ax, 150, ax, 205, color=POS, sw=2.4))
    parts.append(line(ax, 150, ax - 14, 132, color=POS, sw=2.4))
    parts.append(line(ax, 150, ax + 14, 132, color=POS, sw=2.4))
    parts.append(text(ax, 224, "антена\nна платі", 10, POS, "middle"))
    parts.append(line(556, 161, ax - 6, 161, color=POS, sw=1.8))

    # шина UART MCU↔носій (двобічна) — рознесені стрілки, підписи поза лініями
    parts.append(arrow(148, 150, 210, 150, color=NEG, sw=2.0))
    parts.append(arrow(210, 182, 148, 182, color=NEG, sw=2.0))
    parts.append(text(179, 138, "UART", 11, NEG, "middle", bold=True))
    parts.append(text(179, 205, "+ VCC / GND", 10, MUTED, "middle"))

    # від носія до доньки — 3.3 В логіка
    parts.append(arrow(382, 150, 420, 150, color=NEG, sw=1.8))
    parts.append(text(401, 138, "3.3 В", 9, MUTED, "middle"))

    render(os.path.join(IMG, "block.svg"), W, H, *parts,
           title="Устрій HC-05/HC-06: платка-донька з чипом CSR на платі-носії")


# ── Фігура 2: розпіновка 6-контактної плати-носія ────────────────────────────
# Стандартні 6 виводів: EN(KEY), VCC, GND, TXD, RXD, STATE.
def fig_pinout():
    W, H = 720, 430
    parts = []
    bx, by, bw, bh = 300, 78, 120, 300
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(bx + bw / 2, by - 16, "HC-05 / HC-06 (breakout)", 12, INK, "middle", bold=True))

    rows = [
        # (підпис, колір, опис праворуч)
        ("EN",    FIELD, "high при старті → режим AT-команд"),
        ("VCC",   POS,   "живлення 3.6…6 В (на носії є регулятор)"),
        ("GND",   INK,   "спільна земля"),
        ("TXD",   NEG,   "дані з модуля → RX мікроконтролера (3.3 В)"),
        ("RXD",   NEG,   "дані в модуль ← TX MCU (лише 3.3 В! див. дільник)"),
        ("STATE", MUTED, "0 = не з'єднано, 1 = з'єднано"),
    ]
    n = len(rows)
    y0 = by + 34
    step = (bh - 60) / (n - 1)
    for i, (pin, col, desc) in enumerate(rows):
        y = y0 + i * step
        parts.append(line(bx, y, bx - 20, y, color=col, sw=2.2))
        parts.append(circle(bx - 20, y, 3.6, fill=col, stroke=INK, sw=1))
        parts.append(text(bx + 10, y + 4, pin, 12, col, "start", bold=True))
        parts.append(line(bx + bw, y, bx + bw + 18, y, color=MUTED, sw=1.2))
        parts.append(text(bx + bw + 24, y + 4, desc, 10.5, INK, "start"))

    # підказка про кнопку/STATE знизу-ліворуч, поза лініями виводів
    parts.append(fitbox(40, by + 96, 210, 74,
                        "На платі ще є кнопка\n(тримати → EN у high для AT)\n"
                        "і світлодіод стану:\nблимає — чекає, рідко — з'єднано.",
                        size=10.5, fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    render(os.path.join(IMG, "pinout.svg"), W, H, *parts,
           title="Розпіновка плати-носія: EN · VCC · GND · TXD · RXD · STATE")


# ── Фігура 3: підключення до 5-В MCU — дільник на RXD (головна пастка) ────────
# TXD модуля → RX MCU напряму (3.3 В читається як 1). TX MCU (5 В) → RXD модуля
# ТІЛЬКИ через дільник 1к/2к, бо RXD не толерантний до 5 В.
def fig_wiring():
    W, H = 760, 400
    parts = []
    # MCU 5 В
    parts.append(fitbox(30, 150, 150, 90, "MCU на 5 В\n(Arduino Uno/Nano)\nTX і RX — 5-В логіка",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
    # модуль
    parts.append(fitbox(560, 150, 170, 90, "HC-05 / HC-06\nживиться 5 В (VCC),\nале RXD — лише 3.3 В",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # TXD модуля → RX MCU (напряму, безпечно)
    parts.append(arrow(560, 172, 180, 172, color=FIELD, sw=2.2))
    parts.append(text(370, 160, "TXD (3.3 В) → RX MCU — напряму, ок", 11, FIELD, "middle", bold=True))

    # TX MCU → RXD модуля через дільник
    yL = 214
    parts.append(line(180, yL, 300, yL, color=NEG, sw=2.2))          # TX MCU до верху дільника
    parts.append(text(240, yL - 10, "TX MCU (5 В)", 10, NEG, "middle"))
    # дільник: R1 послідовно, R2 на землю
    parts.append(fitbox(300, yL - 16, 70, 32, "R1 1к", size=11, fill="#ffffff", stroke=INK, sw=1.4, color=INK))
    node = 400
    parts.append(line(370, yL, node, yL, color=NEG, sw=2.2))
    parts.append(circle(node, yL, 3.5, fill=INK, stroke=INK, sw=1))
    # R2 вниз на землю
    parts.append(fitbox(node - 35, yL + 26, 70, 32, "R2 2к", size=11, fill="#ffffff", stroke=INK, sw=1.4, color=INK))
    parts.append(line(node, yL, node, yL + 26, color=INK, sw=2.0))
    parts.append(line(node, yL + 58, node, yL + 84, color=INK, sw=2.0))
    parts.append(text(node, yL + 100, "GND", 10, INK, "middle"))
    # вузол → RXD модуля (уже 3.3 В)
    parts.append(arrow(node, yL, 560, yL, color=NEG, sw=2.2))
    parts.append(text(480, yL - 10, "≈3.3 В → RXD", 10, NEG, "middle"))

    # пояснення-пастка знизу
    parts.append(fitbox(70, 322, 620, 60,
                        "Пастка: подати 5-В TX прямо на RXD → з часом псується вхід модуля.\n"
                        "Дільник 1к/2к опускає 5 В до ≈3.3 В; зустрічний бік (TXD→RX MCU) його не потребує.",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Підключення до 5-В MCU: дільник на RXD — головна пастка")


# ── Фігура 4: два порти на Uno — USB-монітор вільний, модуль на SoftwareSerial ─
# Апаратний Serial (D0/D1) лишається на USB→комп'ютер; модуль висить на двох
# інших ніжках через SoftwareSerial. Скетч перекладає байти між двома портами.
def fig_softserial():
    W, H = 780, 360
    parts = []

    # комп'ютер (монітор порту)
    parts.append(fitbox(28, 150, 150, 74, "Комп'ютер\nмонітор порту\n(USB)",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
    # Arduino Uno посередині
    parts.append(rect(250, 70, 250, 230, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(375, 58, "Arduino Uno (ATmega328)", 12, MUTED, "middle", bold=True))
    parts.append(fitbox(272, 96, 206, 40, "апаратний Serial → D0/D1",
                        size=11, fill="#eaf0fd", stroke=NEG, sw=1.3, color=INK, bold=True))
    parts.append(fitbox(272, 150, 206, 46, "скетч: перекладає байти\nміж двома портами",
                        size=11, fill="#ffffff", stroke=INK, sw=1.4, color=INK))
    parts.append(fitbox(272, 214, 206, 40, "SoftwareSerial → D10/D11",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.3, color=INK, bold=True))
    # модуль справа
    parts.append(fitbox(566, 150, 186, 74, "HC-05 / HC-06\n(RXD через дільник,\nTXD напряму)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # USB зв'язок комп'ютер ↔ апаратний Serial
    parts.append(arrow(178, 116, 272, 116, color=NEG, sw=2.0))
    parts.append(arrow(272, 128, 178, 128, color=NEG, sw=2.0))
    parts.append(text(225, 104, "USB", 10, NEG, "middle", bold=True))
    # SoftwareSerial ↔ модуль
    parts.append(arrow(478, 234, 566, 234, color=FIELD, sw=2.0))
    parts.append(arrow(566, 246, 478, 246, color=FIELD, sw=2.0))
    parts.append(text(522, 224, "радіобайти", 10, FIELD, "middle", bold=True))

    parts.append(fitbox(70, 300, 640, 44,
                        "Навіщо два порти: апаратний Serial зайнятий друком у монітор і прошивкою по USB.\n"
                        "Повісити модуль ще й на D0/D1 → монітор ловитиме кашу. SoftwareSerial дає модулю окрему пару.",
                        size=10.5, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    render(os.path.join(IMG, "softserial.svg"), W, H, *parts,
           title="Дві лінії на Uno: USB-монітор вільний, модуль на SoftwareSerial")


# ── Фігура 5: два життя модуля з боку коду — прозорий міст vs режим AT ─────────
# EN low → байти летять наскрізь. EN high на старті → модуль слухає AT-команди
# на 38400 з \r\n; скетч шле команду й розбирає відповідь до "OK".
def fig_twomodes():
    W, H = 800, 380
    parts = []

    # ЛІВА колонка: прозорий міст (EN low)
    parts.append(rect(30, 66, 350, 288, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=10))
    parts.append(text(205, 56, "EN = low → прозорий міст", 12.5, FIELD, "middle", bold=True))
    parts.append(fitbox(56, 92, 298, 40, "робоча швидкість (типово 9600)",
                        size=11, fill="#ffffff", stroke=INK, sw=1.2, color=INK))
    parts.append(fitbox(56, 150, 130, 56, "ваш байт\nу RXD",
                        size=11, fill="#ffffff", stroke=INK, sw=1.3, color=INK))
    parts.append(arrow(186, 178, 250, 178, color=FIELD, sw=2.2))
    parts.append(fitbox(250, 150, 104, 56, "летить\nпо радіо",
                        size=11, fill="#ffffff", stroke=FIELD, sw=1.3, color=INK, bold=True))
    parts.append(fitbox(56, 232, 298, 46, "жодних команд: код лише\nчитає й пише байти",
                        size=11, fill="#f4f6f8", stroke=MUTED, sw=1.2, color=INK))
    parts.append(fitbox(56, 296, 298, 40, "STATE = 1 ⟺ напарник з'єднаний",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    # ПРАВА колонка: режим AT (EN high)
    parts.append(rect(420, 66, 350, 288, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=10))
    parts.append(text(595, 56, "EN = high на старті → режим AT", 12.5, NEG, "middle", bold=True))
    parts.append(fitbox(446, 92, 298, 40, "командна швидкість HC-05: 38400 (фікс.)",
                        size=11, fill="#ffffff", stroke=INK, sw=1.2, color=INK))
    parts.append(fitbox(446, 150, 150, 54, "скетч шле\nAT+NAME=Robot\\r\\n",
                        size=10.5, fill="#ffffff", stroke=INK, sw=1.3, color=INK))
    parts.append(arrow(596, 177, 660, 177, color=NEG, sw=2.2))
    parts.append(fitbox(660, 150, 84, 54, "модуль:\nOK\\r\\n",
                        size=10.5, fill="#ffffff", stroke=NEG, sw=1.3, color=INK, bold=True))
    parts.append(fitbox(446, 230, 298, 46, "код читає до \\r\\n і звіряє:\n\"OK\" → успіх, \"ERROR\" → ні",
                        size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.2, color=INK))
    parts.append(fitbox(446, 296, 298, 40, "NAME · PSWD · UART · ROLE",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    render(os.path.join(IMG, "twomodes.svg"), W, H, *parts,
           title="Два життя модуля з боку коду: міст (EN low) vs AT (EN high)")


fig_block()
fig_pinout()
fig_wiring()
fig_softserial()
fig_twomodes()
print("Done. SVG in", IMG)
