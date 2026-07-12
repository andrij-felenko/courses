# -*- coding: utf-8 -*-
"""Фігури для кроку «Варіант А: потік на кожне з'єднання» (progarch / concurrency-models)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_BG = "#e9f7ef"
RED_BG = "#fdecea"


# ── Фігура 1: потік на з'єднання — дешево на десятках, стіна на десятках тисяч ──
def fig_wall():
    W, H = 920, 500
    f = []

    # ── ліва панель: десятки з'єднань ──
    f.append(rect(40, 55, 400, 415, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(240, 88, "Десятки з'єднань", size=15, bold=True))

    rows = [130, 197, 264]
    for i, cy in enumerate(rows):
        lbl = "хаб" if i == 0 else ""
        if lbl:
            f.append(text(80, cy - 20, lbl, size=11, color=MUTED))
        f.append(circle(80, cy, 10, fill=GREEN_BG, stroke=FIELD, sw=1.8))
        f.append(arrow(96, cy, 150, cy, color=LINE))
        f.append(fitbox(155, cy - 24, 250, 48, "потік · стек ≈ 1 МБ",
                        size=14, fill=FILL, stroke=LINE))

    f.append(fitbox(60, 322, 360, 128,
                    "Кілька потоків — планувальникові легко.\n"
                    "Стеки в пам'яті — дрібниця.\n"
                    "Код просто працює.",
                    size=14, fill=GREEN_BG, stroke=FIELD))

    # ── права панель: десятки тисяч ──
    f.append(rect(480, 55, 400, 415, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(680, 88, "Десятки тисяч з'єднань", size=15, bold=True))
    f.append(text(680, 110, "кожна клітинка — потік зі своїм стеком", size=12, color=MUTED))

    xs = [508, 568, 628, 688, 748, 808]
    ys = [128, 168, 208]
    for gy in ys:
        for gx in xs:
            f.append(rect(gx, gy, 48, 28, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    f.append(text(680, 252, "… ще × 10 000", size=14, bold=True))

    f.append(fitbox(505, 272, 350, 178,
                    "Стеки ≈ 10 ГБ —\n"
                    "лише щоб потоки стояли.\n"
                    "Планувальник більше перемикає\n"
                    "контексти, ніж рахує.",
                    size=14, fill=RED_BG, stroke=POS))

    render(os.path.join(IMG, "threads-wall.svg"), W, H, *f,
           title="Потік на з'єднання: дешево на десятках, стіна на десятках тисяч")


# ── Фігура 2: спільний стан за одним замком — потоки шикуються в чергу ──
def fig_lock():
    W, H = 920, 470
    f = []

    # стек потоків ліворуч
    tops = [95, 150, 205, 260, 315]
    f.append(text(105, 80, "5 потоків → один стан", size=13, color=MUTED))
    gate_x, gate_yc = 408, 220
    for i, ty in enumerate(tops):
        cy = ty + 21
        active = (i == 0)
        fill = GREEN_BG if active else FILL
        stroke = FIELD if active else LINE
        f.append(rect(45, ty, 120, 42, fill=fill, stroke=stroke, sw=1.8))
        f.append(text(105, cy + 5, "потік %d" % (i + 1), size=13))
        if active:
            f.append(arrow(165, cy, gate_x - 2, gate_yc - 4, color=FIELD, sw=2.2))
        else:
            f.append(line(165, cy, gate_x - 2, gate_yc + 4, color=MUTED, sw=1.4, dash="5,4"))

    # замок (ворота — по одному)
    f.append(text(700, 150, "критична секція: рівно один потік усередині",
                  size=12, color=FIELD))
    f.append(rect(408, 185, 84, 70, fill=FILL, stroke=INK, sw=2))
    f.append(text(450, 214, "замок", size=14, bold=True))
    f.append(text(450, 236, "по одному", size=11, color=MUTED))

    # замок → спільний стан
    f.append(arrow(492, gate_yc, 593, gate_yc, color=FIELD, sw=2.2))
    f.append(rect(595, 178, 270, 84, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(730, 212, "спільний стан", size=14, bold=True))
    f.append(text(730, 236, "реєстр пристроїв", size=12, color=MUTED))

    # легенда
    f.append(rect(45, 375, 18, 18, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=3))
    f.append(text(72, 389, "тримає замок", size=12, anchor="start"))
    f.append(rect(210, 375, 18, 18, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    f.append(text(237, 389, "у черзі", size=12, anchor="start"))

    f.append(fitbox(120, 408, 680, 52,
                    "Що більше потоків — то довша черга біля замка: замок стає "
                    "послідовною часткою, і Амдал вирахує її зі стелі прискорення.",
                    size=13, fill=RED_BG, stroke=POS))

    render(os.path.join(IMG, "lock-serializes.svg"), W, H, *f,
           title="Спільний стан за одним замком — потоки шикуються в чергу")


# ── Фігура 3 (вставка hist): дві дороги від стіни C10K ──────────────────────
def fig_two_roads():
    W, H = 1060, 610
    BLUE_BG = "#eaf0fd"
    f = []

    y_main = 300
    wall_x = 440
    y_up = 172
    y_lo = 436

    # ── лінія до стіни: CGI → сервлети ──
    bodyA, wA, hA = textbox(128, y_main, "1993 · CGI\nпроцес на запит",
                            size=14, fill=BLUE_BG, stroke=NEG)
    bodyB, wB, hB = textbox(316, y_main, "Apache → сервлети\nпотік на з'єднання",
                            size=14, fill=BLUE_BG, stroke=NEG)
    f += [bodyA, bodyB]
    f.append(arrow(128 + wA / 2, y_main, 316 - wB / 2 - 3, y_main, color=LINE, sw=2))
    f.append(arrow(316 + wB / 2, y_main, wall_x - 16, y_main, color=LINE, sw=2))

    # ── стіна C10K ──
    f.append(rect(wall_x - 11, 118, 22, 366, fill="#f7cfc8", stroke=POS, sw=2.5, rx=3))
    tbW, wW, hW = textbox(wall_x, 84, "1999 · стіна C10K\nДен Кегель",
                          size=14, fill=RED_BG, stroke=POS, bold=True)
    f.append(tbW)

    # ── банер дороги 1 (згори) ──
    f.append(fitbox(500, 114, 500, 30,
                    "Дорога 1 — викинути блокування: цикл подій, колбеки",
                    size=13, fill=RED_BG, stroke=POS))
    # вузли дороги 1
    bU1, wU1, hU1 = textbox(628, y_up, "2004 · nginx\nІгор Сисоєв",
                            size=14, fill=RED_BG, stroke=POS)
    bU2, wU2, hU2 = textbox(838, y_up, "2009 · Node.js\nРаян Дал",
                            size=14, fill=RED_BG, stroke=POS)
    f += [bU1, bU2]
    f.append(arrow(wall_x + 11, 240, 628 - wU1 / 2 - 4, y_up + 14, color=POS, sw=2))
    f.append(arrow(628 + wU1 / 2, y_up, 838 - wU2 / 2 - 3, y_up, color=POS, sw=2))
    f.append(text(838, y_up + hU2 / 2 + 22, "стек-трейс порожній, керування у колбеках",
                  size=12, color=MUTED))

    # ── банер дороги 2 (знизу) ──
    f.append(fitbox(500, 504, 512, 30,
                    "Дорога 2 — зберегти блокування, здешевити сам потік",
                    size=13, fill=GREEN_BG, stroke=FIELD))
    # вузли дороги 2
    bL1, wL1, hL1 = textbox(636, y_lo, "2012–14 · ґорутини Go\nстек 2 КБ, росте",
                            size=14, fill=GREEN_BG, stroke=FIELD)
    bL2, wL2, hL2 = textbox(870, y_lo, "2023 · віртуальні потоки\nJava · JDK 21",
                            size=14, fill=GREEN_BG, stroke=FIELD)
    f += [bL1, bL2]
    f.append(arrow(wall_x + 11, 362, 636 - wL1 / 2 - 4, y_lo - 14, color=FIELD, sw=2))
    f.append(arrow(636 + wL1 / 2, y_lo, 870 - wL2 / 2 - 3, y_lo, color=FIELD, sw=2))
    f.append(text(636, y_lo - hL1 / 2 - 16, "блокуючий код той самий, згори вниз",
                  size=12, color=FIELD))

    render(os.path.join(IMG, "hist-two-roads.svg"), W, H, *f,
           title="Дві дороги від стіни C10K: викинути блокування — чи здешевити потік")


if __name__ == "__main__":
    fig_wall()
    fig_lock()
    fig_two_roads()
    print("OK: threads-wall.svg, lock-serializes.svg, hist-two-roads.svg")
