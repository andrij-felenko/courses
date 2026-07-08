# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RADIO = "#e8f0ff"   # блок повітряного модуля
UART  = "#eafaf0"   # лінія UART
AIRC  = "#fff4e6"   # ефір / радіоканал
GND_C = "#eef2fe"
PWR_C = "#fdeeee"


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: одна радіолінія несе І керування вгору, І телеметрію вниз;
# нутро повітряного блоку (Semtech + MCU) і що він віддає на FC.
# ─────────────────────────────────────────────────────────────────────────────
def fig_link():
    W, H = 940, 520
    frags = []

    # --- Земля (ліворуч): пульт + JR-модуль ---------------------------------
    frags.append(text(175, 52, "ЗЕМЛЯ (пілот)", size=15, bold=True, color=MUTED))

    tx = fitbox(40, 96, 118, 150, "ПУЛЬТ\n(EdgeTX)\n\nстіки, екран,\nтелеметрія",
                size=12, fill=FILL, bold=False)
    frags.append(tx)

    # наземний модуль у JR-відсіку
    gmx, gmy, gmw, gmh = 186, 96, 120, 150
    frags.append(rect(gmx, gmy, gmw, gmh, fill=RADIO, stroke="#3b6fd4", sw=2))
    frags.append(text(gmx + gmw / 2, gmy + 26, "НАЗЕМНИЙ", size=12, bold=True, color="#274b8f"))
    frags.append(text(gmx + gmw / 2, gmy + 44, "МОДУЛЬ", size=12, bold=True, color="#274b8f"))
    frags.append(text(gmx + gmw / 2, gmy + 68, "(у JR-відсіку", size=10.5, color="#33517f"))
    frags.append(text(gmx + gmw / 2, gmy + 84, "пульта)", size=10.5, color="#33517f"))
    frags.append(text(gmx + gmw / 2, gmy + 112, "той самий", size=10.5, color="#33517f"))
    frags.append(text(gmx + gmw / 2, gmy + 128, "трансивер", size=10.5, color="#33517f"))

    # пульт ↔ наземний (CRSF)
    frags.append(text(172, 165, "CRSF", size=10.5, color=FIELD, bold=True))
    frags.append(arrow(158, 176, 186, 176, color=FIELD, sw=2.2))

    # антена наземна
    gay = gmy + 40
    frags.append(line(gmx + gmw, gay, gmx + gmw + 24, gay, color=INK, sw=2))
    frags.append(line(gmx + gmw + 24, gay, gmx + gmw + 24, gay - 34, color=INK, sw=2))
    frags.append(text(gmx + gmw + 24, gay - 42, "ANT", size=11, bold=True))

    # --- Ефір (посередині): одна лінія, два потоки --------------------------
    ex = gmx + gmw + 24
    bx = 640              # ліва межа бортового блоку
    midy = 168
    frags.append(rect(ex + 8, midy - 60, bx - ex - 16, 208, fill=AIRC, stroke="#e0a04a", sw=1.4))
    frags.append(text((ex + bx) / 2, midy - 38, "ОДНА РАДІОЛІНІЯ", size=13, bold=True, color="#b06f1e"))
    frags.append(text((ex + bx) / 2, midy - 18, "2.4 ГГц (SX1280) або 900 МГц (SX127x)", size=10.5, color="#8a5a1a"))
    # керування вгору (на борт)
    frags.append(arrow(ex + 20, midy + 12, bx - 20, midy + 12, color="#c0392b", sw=2.6))
    frags.append(text((ex + bx) / 2, midy + 4, "керування (стіки) на борт  →", size=10.5, color="#8a3a24"))
    # телеметрія вниз (на землю)
    frags.append(arrow(bx - 20, midy + 56, ex + 20, midy + 56, color="#2457d6", sw=2.6))
    frags.append(text((ex + bx) / 2, midy + 48, "←  телеметрія на землю", size=10.5, color="#22357f"))
    frags.append(text((ex + bx) / 2, midy + 84, "повний дуплекс,", size=10.5, color="#8a5a1a"))
    frags.append(text((ex + bx) / 2, midy + 102, "співвідношення 1:2", size=10.5, color="#8a5a1a"))
    frags.append(text((ex + bx) / 2, midy + 128, "прив'язка (binding) робить", size=10.5, color="#8a5a1a"))
    frags.append(text((ex + bx) / 2, midy + 144, "пару своєю", size=10.5, color="#8a5a1a"))

    # --- Борт (праворуч): повітряний блок + FC ------------------------------
    frags.append(text(795, 52, "БОРТ (у повітрі)", size=15, bold=True, color=MUTED))

    # антена бортова
    bay = midy
    frags.append(line(bx - 24, bay, bx, bay, color=INK, sw=2))
    frags.append(line(bx - 24, bay, bx - 24, bay - 34, color=INK, sw=2))
    frags.append(text(bx - 24, bay - 42, "ANT", size=11, bold=True))

    # повітряний блок — рамка з нутром
    mx, my, mw, mh = 648, 90, 208, 250
    frags.append(rect(mx, my, mw, mh, fill=RADIO, stroke="#3b6fd4", sw=2))
    frags.append(text(mx + mw / 2, my + 22, "ПОВІТРЯНИЙ БЛОК", size=12.5, bold=True, color="#274b8f"))
    frags.append(text(mx + mw / 2, my + 40, "(приймач на борту)", size=10.5, color="#33517f"))

    b1 = fitbox(mx + 18, my + 56, 82, 62, "радіочип\nSX1280 /\nSX127x", size=10.5)
    b2 = fitbox(mx + 110, my + 56, 82, 62, "MCU\nESP32 /\nSTM32", size=10.5)
    frags.append(b1)
    frags.append(b2)
    frags.append(arrow(mx + 100, my + 87, mx + 110, my + 87, color=INK))

    b3 = fitbox(mx + 18, my + 132, 174, 40, "PA / LNA — підсилювачі", size=10.5, fill="#f0f4fb")
    frags.append(b3)
    b5 = fitbox(mx + 18, my + 184, 174, 40, "живлення 5 В → 3.3 В (внутр.)", size=10, fill=PWR_C)
    frags.append(b5)

    # FC під блоком
    fc = fitbox(648, 372, 208, 74, "ПОЛЬОТНИЙ КОНТРОЛЕР\n\nCRSF / SBUS / MAVLink по UART",
                size=11, fill=FILL, bold=False)
    frags.append(fc)
    # блок ↔ FC
    frags.append(text(760, 356, "UART", size=10.5, color=FIELD, bold=True))
    frags.append(arrow(752, 340, 752, 372, color=FIELD, sw=2.2))
    frags.append(arrow(772, 372, 772, 340, color=FIELD, sw=2.2))

    # підпис унизу
    frags.append(text(W / 2, H - 20, "Той самий маленький приймач тягне керування вгору і телеметрію вниз по одній лінії — окреме радіо телеметрії не потрібне.",
                      size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'link.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: розводка приймача пін-у-пін до польотного контролера
# (CRSF — дві лінії перехрещено; SBUS — одна лінія, TX)
# ─────────────────────────────────────────────────────────────────────────────
def fig_pinout():
    W, H = 860, 560
    frags = []
    frags.append(text(W / 2, 34, "Приймач ExpressLRS → польотний контролер: живлення й серійний порт", size=15, bold=True))

    rxx = 165      # центр стовпця приймача
    fcx = 660      # центр стовпця FC
    top = 96
    dy = 60

    # рядки: (пад приймача, підпис-стрілка, пад FC, колір, заливка)
    pins = [
        ("5V",  "живлення 5 В →",        "5V",  POS,   PWR_C),
        ("GND", "спільна земля",         "GND", NEG,   GND_C),
        ("TX",  "керування (RC) →",      "RX",  FIELD, UART),
        ("RX",  "← телеметрія з FC",     "TX",  FIELD, UART),
    ]

    frags.append(text(rxx, top - 26, "ПРИЙМАЧ ELRS", size=12.5, bold=True, color="#274b8f"))
    frags.append(text(fcx, top - 26, "ПОЛЬОТНИЙ КОНТРОЛЕР (UART)", size=12.5, bold=True, color="#274b8f"))

    frags.append(rect(rxx - 80, top - 10, 160, dy * 4 + 4, fill="none", stroke="#3b6fd4", sw=1.6))
    frags.append(rect(fcx - 80, top - 10, 160, dy * 4 + 4, fill="none", stroke="#3b6fd4", sw=1.6))

    for i, (rl, desc, fl, col, fill) in enumerate(pins):
        y = top + i * dy + dy / 2
        # пад приймача
        frags.append(rect(rxx - 76, y - 21, 152, 42, fill=fill, stroke=col, sw=1.6))
        frags.append(text(rxx, y + 5, rl, size=14, bold=True, color=col))
        # пад FC
        frags.append(rect(fcx - 76, y - 21, 152, 42, fill=fill, stroke=col, sw=1.6))
        frags.append(text(fcx, y + 5, fl, size=14, bold=True, color=col))
        # провід із підписом посередині (повз написи)
        frags.append(line(rxx + 76, y, fcx - 76, y, color=col, sw=2))
        frags.append(text((rxx + fcx) / 2, y - 9, desc, size=11, color=MUTED))

    # виноски
    ny = top + dy * 4 + 30
    frags.append(text(W / 2, ny, "CRSF (типово): TX↔RX і RX↔TX ПЕРЕХРЕЩЕНО, повний дуплекс — дві лінії. Рівні — 3.3 В, живлення — 5 В.",
                      size=11.5, color=INK, bold=True))
    frags.append(text(W / 2, ny + 24, "SBUS (для старих плат): лише одна лінія TX приймача → RX контролера, сигнал інвертований.",
                      size=11.5, color=MUTED, italic=True))

    # маленька таблиця протоколів/швидкостей унизу — окремим блоком, з запасом
    tbx, tby, tbw = 150, ny + 52, W - 300
    frags.append(rect(tbx, tby, tbw, 96, fill="#f7f9fc", stroke=LINE, sw=1.4))
    frags.append(text(W / 2, tby + 24, "серійний вихід і швидкість", size=12, bold=True, color=INK))
    frags.append(text(W / 2, tby + 46, "CRSF ≈ 420000 бод (повний дуплекс, RX+TX)", size=11, color="#274b8f"))
    frags.append(text(W / 2, tby + 66, "MAVLink — 460800 бод (повний дуплекс, RX+TX)", size=11, color="#274b8f"))
    frags.append(text(W / 2, tby + 86, "SBUS — 100000 бод, інвертований (лише TX)", size=11, color=MUTED))

    render(os.path.join(IMG, 'pinout.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_link()
    fig_pinout()
    print("ok")
