# -*- coding: utf-8 -*-
"""Фігури до теми «Домени живлення в ядрі: genpd і спільний вимикач на групу пристроїв»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
BLUE_BG  = "#e8eefb"
GOLD     = "#b8860b"


# ── 1. Один вимикач живить групу блоків ──────────────────────────────────────
def fig_power_region():
    W, H = 1210, 566
    P = []

    # завжди жива шина
    P.append(fitbox(70, 34, 1070, 46,
                    "шина живлення кристала — під напругою, доки ввімкнено машину",
                    size=14, fill=GREY_BG, bold=True))

    # два вимикачі
    P.append(fitbox(255, 118, 200, 50, "вимикач живлення",
                    size=14, fill=WARM_BG, stroke=GOLD, bold=True))
    P.append(fitbox(835, 118, 200, 50, "вимикач живлення",
                    size=14, fill=WARM_BG, stroke=GOLD, bold=True))
    P.append(arrow(355, 80, 355, 116))
    P.append(arrow(935, 80, 935, 116))

    P.append(mtext(645, 132, ["кожним керує окремий біт", "у регістрі контролера живлення"],
                   size=12, color=MUTED))

    # регіон «дисплей»
    P.append(rect(90, 202, 560, 246, fill="#ffffff", stroke=MUTED, sw=1.5))
    P.append(text(110, 230, "регіон живлення «дисплей»", size=14, bold=True, anchor="start"))
    P.append(fitbox(110, 250, 165, 76, "контролер\nдисплея", size=13, fill=BLUE_BG))
    P.append(fitbox(292, 250, 165, 76, "передавач\nMIPI DSI", size=13, fill=BLUE_BG))
    P.append(fitbox(474, 250, 165, 76, "DMA\nдисплея", size=13, fill=BLUE_BG))
    P.append(text(370, 356, "три окремі пристрої ядра — один спільний вимикач",
                  size=12, color=MUTED))
    P.append(text(370, 394, "на межі регіону — комірки ізоляції:", size=12, color=MUTED))
    P.append(text(370, 416, "вони тримають виходи мертвого блока в певному рівні",
                  size=12, color=MUTED))
    P.append(arrow(355, 168, 355, 200))

    # регіон «USB»
    P.append(rect(692, 202, 438, 246, fill="#ffffff", stroke=MUTED, sw=1.5))
    P.append(text(712, 230, "регіон живлення «USB»", size=14, bold=True, anchor="start"))
    P.append(fitbox(712, 250, 190, 76, "USB-хост\n(xHCI)", size=13, fill=BLUE_BG))
    P.append(fitbox(920, 250, 190, 76, "USB PHY", size=13, fill=BLUE_BG))
    P.append(text(911, 356, "тут вимикач живить лише два блоки", size=12, color=MUTED))
    P.append(arrow(935, 168, 935, 200))

    # легенда: такт проти живлення
    P.append(fitbox(150, 478, 430, 62,
                    "вимкнути такт: стан збережено,\nповернення — одиниці тактів",
                    size=13, fill=GREEN_BG))
    P.append(fitbox(630, 478, 430, 62,
                    "зняти живлення: стан утрачено,\nповернення — сотні мікросекунд і більше",
                    size=13, fill=RED_BG))

    render(os.path.join(OUT, "power-region.svg"), W, H, *P)


# ── 2. Хто тримає домен увімкненим ───────────────────────────────────────────
def fig_genpd_counters():
    W, H = 1230, 636
    P = []

    # батьківський домен
    P.append(rect(60, 44, 1110, 492, fill="#fbfcfd", stroke=LINE, sw=2))
    P.append(text(82, 78, "домен «медіа»", size=15, bold=True, anchor="start"))
    P.append(fitbox(830, 54, 316, 62,
                    "активних пристроїв: 0\nувімкнених піддоменів: 1",
                    size=13, fill=WARM_BG, stroke=GOLD))

    # пристрої просто в батьківському домені
    P.append(fitbox(100, 148, 240, 88, "кодек відео\nRPM_SUSPENDED", size=13, fill=GREEN_BG))
    P.append(fitbox(370, 148, 240, 88, "апарат JPEG\nRPM_SUSPENDED", size=13, fill=GREEN_BG))

    # піддомен
    P.append(rect(100, 272, 700, 222, fill="#ffffff", stroke=MUTED, sw=1.5))
    P.append(text(120, 302, "піддомен «дисплей»", size=14, bold=True, anchor="start"))
    P.append(text(780, 302, "активних пристроїв: 1", size=13, color=GOLD,
                  bold=True, anchor="end"))
    P.append(fitbox(120, 320, 210, 88, "контролер дисплея\nRPM_ACTIVE", size=13, fill=RED_BG))
    P.append(fitbox(350, 320, 210, 88, "передавач DSI\nRPM_SUSPENDED", size=13, fill=GREEN_BG))
    P.append(fitbox(580, 320, 200, 88, "DMA дисплея\nRPM_SUSPENDED", size=13, fill=GREEN_BG))
    P.append(text(450, 456, "один активний пристрій тримає ввімкненим увесь піддомен",
                  size=12, color=MUTED))

    # пояснення праворуч
    P.append(fitbox(830, 300, 316, 130,
                    "піддомен увімкнено →\nлічильник батька не нуль →\n"
                    "вимикач батька закритий,\nхоч обидва його пристрої сплять",
                    size=13, fill=GREY_BG))

    P.append(fitbox(60, 558, 1110, 56,
                    "вмикають згори вниз: спершу батько, потім піддомен · "
                    "вимикають знизу вгору: спершу піддомен, і аж тоді батько",
                    size=13, fill=BLUE_BG))

    render(os.path.join(OUT, "genpd-counters.svg"), W, H, *P)


# ── 3. Порядок дій на засинанні та пробудженні ───────────────────────────────
def fig_callback_order():
    W, H = 1150, 712
    P = []

    P.append(text(300, 44, "пристрій засинає", size=15, bold=True))
    P.append(text(830, 44, "пристрій знову потрібен", size=15, bold=True))

    left = [
        "runtime PM: лічильник користувачів\nпристрою дійшов нуля",
        "genpd підміняє собою зворотні виклики\nпристрою й дістає керування першим",
        "виклик драйвера: зберегти стан,\nспинити залізо",
        "->stop: зняти такти з пристрою",
        "мінус один до лічильника\nактивних у домені",
        "нуль і губернатор дозволив →\n->power_off: відкрити вимикач",
    ]
    right = [
        "хтось заявив: пристрій потрібен",
        "genpd дістає керування першим —\nдо драйвера",
        "спершу ввімкнути батьківські домени,\nзгори вниз",
        "->power_on: закрити вимикач\nцього домену",
        "->start: подати такти на пристрій",
        "виклик драйвера: відновити регістри,\nбо їхній вміст утрачено",
    ]

    BW, BH, PITCH, Y0 = 430, 72, 96, 76
    for i, s in enumerate(left):
        y = Y0 + i * PITCH
        fill = RED_BG if i == len(left) - 1 else GREY_BG
        P.append(fitbox(80, y, BW, BH, s, size=13, fill=fill))
        if i:
            P.append(arrow(295, y - PITCH + BH, 295, y - 2))
    for i, s in enumerate(right):
        y = Y0 + i * PITCH
        fill = GREEN_BG if i == len(right) - 1 else GREY_BG
        P.append(fitbox(620, y, BW, BH, s, size=13, fill=fill))
        if i:
            P.append(arrow(835, y - PITCH + BH, 835, y - 2))

    P.append(fitbox(80, 642, 970, 56,
                    "порядок незворотний: звернення до блока, з якого знято живлення, — "
                    "це не помилка на шині, а зависла транзакція",
                    size=13, fill=WARM_BG, stroke=GOLD))

    render(os.path.join(OUT, "genpd-callback-order.svg"), W, H, *P)


if __name__ == "__main__":
    fig_power_region()
    fig_genpd_counters()
    fig_callback_order()
    print("ok")
