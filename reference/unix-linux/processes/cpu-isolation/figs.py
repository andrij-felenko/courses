# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARMF  = "#fdecea"
COOLF  = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"


# ── 1. Вісь часу ядра до і після ізоляції ─────────────────────────────────────
def fig_core_timeline():
    W, H = 1180, 560
    p = []

    # ---- звичайне ядро ----
    p.append(text(120, 126, "ЗВИЧАЙНЕ ЯДРО", size=16, bold=True, anchor="start"))

    events = [
        (300, 160, "чужа задача", WARMF, POS),
        (560, 190, "переривання диска", COOLF, NEG),
        (830, 170, "службовий потік", PALE, MUTED),
    ]
    for x, w, label, fill, col in events:
        p.append(fitbox(x, 142, w, 38, label, size=13, fill=fill, stroke=col, sw=1.5))
        p.append(line(x + w / 2, 180, x + w / 2, 198, color=col, sw=1.2))

    p.append(line(120, 200, 1100, 200, color=INK, sw=2))
    for x in range(140, 1101, 35):
        p.append(line(x, 188, x, 212, color=POS, sw=2))
    p.append(text(120, 246, "тік щомілісекунди: тисяча пауз на секунду, кожна в довільний момент",
                  size=13, color=POS, anchor="start"))

    # ---- ізольоване ядро ----
    p.append(text(120, 348, "ІЗОЛЬОВАНЕ ЯДРО", size=16, bold=True, anchor="start"))
    p.append(fitbox(140, 366, 960, 38, "ваша задача — без перерв", size=14,
                    fill=GREENF, stroke=FIELD, sw=1.8))

    p.append(line(120, 420, 1100, 420, color=INK, sw=2))
    for x, col in ((520, MUTED), (900, NEG)):
        p.append(line(x, 408, x, 432, color=col, sw=2))
    p.append(mtext(520, 458, ["поодинокі таймери, замовлені", "самою задачею"],
                   size=13, color=MUTED))
    p.append(mtext(900, 458, ["міжпроцесорне переривання:", "вимикача немає"],
                   size=13, color=NEG))

    p.append(text(120, 524, "зникли: періодичний тік, чужі задачі, переривання пристроїв, службові потоки",
                  size=13, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "core-timeline.svg"), W, H, *p)


# ── 2. Куди переїжджає робота з ізольованих ядер ──────────────────────────────
def fig_housekeeping_move():
    W, H = 1200, 580
    p = []

    p.append(rect(50, 96, 320, 400, fill=GREENF, stroke=FIELD, sw=2))
    p.append(text(210, 76, "ІЗОЛЬОВАНІ ЯДРА", size=16, bold=True))
    for i in range(4):
        p.append(fitbox(80, 126 + i * 92, 260, 62,
                        "ядро %d\nлише ваша задача" % (4 + i), size=13,
                        fill=BG, stroke=FIELD, sw=1.5))

    p.append(rect(830, 96, 320, 400, fill=WARMF, stroke=POS, sw=2))
    p.append(text(990, 76, "СЛУЖБОВІ ЯДРА", size=16, bold=True))
    for i in range(2):
        p.append(fitbox(860, 126 + i * 92, 260, 62,
                        "ядро %d\nсвоя робота + звезена" % i, size=13,
                        fill=BG, stroke=POS, sw=1.5))
    p.append(fitbox(860, 320, 260, 152,
                    "тут вартість\nусього звезеного\nдодається до\nвласного навантаження",
                    size=13, fill=BG, stroke=MUTED, sw=1.5, color=MUTED))

    moved = [
        (140, "незв'язані таймери"),
        (208, "незв'язані робочі черги"),
        (276, "зворотні виклики RCU"),
        (344, "оновлення лічильників пам'яті"),
        (412, "сторожовий пес"),
        (472, "залишковий тік раз на секунду"),
    ]
    for y, label in moved:
        body, w, h = textbox(600, y, label, size=13, fill=SOFT, stroke=MUTED, sw=1.3)
        p.append(arrow(384, y, 600 - w / 2 - 14, y, color=MUTED))
        p.append(body)
        p.append(arrow(600 + w / 2 + 14, y, 816, y, color=MUTED))

    p.append(text(600, 546, "робота не зникає — вона змінює адресу", size=15, bold=True))

    render(os.path.join(OUT, "housekeeping-move.svg"), W, H, *p)


# ── 3. Постійний податок тіка проти податку на кожному звертанні ──────────────
def fig_tick_tradeoff():
    W, H = 1020, 620
    p = []

    X0, X1 = 150, 910
    Y0, Y1 = 470, 140          # Y0 — нуль, Y1 — 3000 мкс/с
    p.append(line(X0, Y0, X1, Y0, color=INK, sw=2))
    p.append(line(X0, Y0, X0, Y1 - 20, color=INK, sw=2))
    p.append(text(150, 108, "мкс, витрачених за секунду", size=13,
                  color=MUTED, anchor="start"))

    # горизонталь: постійна вартість тіка (1500 мкс/с)
    YT = Y0 - (1500.0 / 3000.0) * (Y0 - Y1)
    p.append(line(X0, YT, X1, YT, color=POS, sw=2.4))
    p.append(text(160, YT - 22, "тік: 1500 мкс/с, хоч би що робила програма",
                  size=13, color=POS, anchor="start"))

    # похила: 0.3 мкс на кожне звертання до ядра
    p.append(line(X0, Y0, X1, Y1, color=NEG, sw=2.4))
    body, bw, bh = textbox(560, 176, ["облік на межі:", "0.3 мкс за кожне звертання"],
                           size=13, fill=COOLF, stroke=NEG, sw=1.3, color=NEG)
    p.append(body)

    # точка рівноваги
    XC = (X0 + X1) / 2.0
    p.append(line(XC, YT, XC, Y0, color=MUTED, sw=1.2, dash="5,5"))
    p.append(circle(XC, YT, 7, fill=BG, stroke=INK, sw=2))
    body, bw, bh = textbox(770, 384, ["рівновага:", "≈5000 звертань за секунду"],
                           size=13, fill=SOFT, stroke=INK, sw=1.3)
    p.append(body)

    for x, lab in ((X0, "0"), (XC, "5 000"), (X1, "10 000")):
        p.append(line(x, Y0, x, Y0 + 8, color=INK, sw=1.5))
        p.append(text(x, Y0 + 28, lab, size=13, color=MUTED))
    p.append(text((X0 + X1) / 2, Y0 + 56, "звертань до ядра за секунду", size=13, color=MUTED))

    p.append(fitbox(120, 528, 340, 46, "ліворуч: nohz_full дешевший", size=13,
                    fill=GREENF, stroke=FIELD, sw=1.5))
    p.append(fitbox(600, 528, 340, 46, "праворуч: звичайний тік дешевший", size=13,
                    fill=WARMF, stroke=POS, sw=1.5))

    render(os.path.join(OUT, "tick-tradeoff.svg"), W, H, *p)


fig_core_timeline()
fig_housekeeping_move()
fig_tick_tradeoff()
print("ok")
