# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми "Запас тяги й що він купує"."""

import os
import sys

# Підключення svgkit із кореневої теки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_twr_spectrum():
    """Спектр TWR та розподіл авторитету моторів."""
    w, h = 900, 360
    frags = []

    # Заголовок
    frags.append(text(w / 2, 25, "Спектр TWR і розподіл динамічного авторитету моторів", size=16, bold=True))

    # Стовпчик 1: Вантажний / Картографічний (TWR = 1.6)
    bx1 = 60
    bw = 140
    frags.append(fitbox(bx1, 55, bw, 22, "Вантажний (TWR 1.6)", size=12, bold=True, fill="#edf2f7", stroke=LINE))
    frags.append(rect(bx1, 80, bw, 75, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(bx1 + bw / 2, 115, ["Запас на PID / вітер", "37.5% (малий)"], size=11, color=POS, bold=True))
    frags.append(rect(bx1, 155, bw, 125, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(mtext(bx1 + bw / 2, 215, ["Тяга висіння", "62.5% газу", "(базова вага)"], size=11, color=NEG, bold=True))
    frags.append(mtext(bx1 + bw / 2, 305, ["Критичний нахил: 51°", "Ризик насичення: високий"], size=11, color=INK))

    # Стовпчик 2: Тактичний / Вітростійкий (TWR = 3.5)
    bx2 = 250
    frags.append(fitbox(bx2, 55, bw, 22, "Тактичний (TWR 3.5)", size=12, bold=True, fill="#edf2f7", stroke=LINE))
    frags.append(rect(bx2, 80, bw, 143, fill="#eafaf1", stroke=FIELD, sw=1.5))
    frags.append(mtext(bx2 + bw / 2, 145, ["Запас авторитету PID", "71.4% (оптимальний)", "Швидке парирування поривів"], size=11, color=FIELD, bold=True))
    frags.append(rect(bx2, 223, bw, 57, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(mtext(bx2 + bw / 2, 252, ["Висіння 28.6%", "(комфортна точка)"], size=11, color=NEG, bold=True))
    frags.append(mtext(bx2 + bw / 2, 305, ["Критичний нахил: 73°", "Стійкість до вітру: >18 м/с"], size=11, color=INK))

    # Стовпчик 3: Спортивний FPV (TWR = 10.0)
    bx3 = 440
    frags.append(fitbox(bx3, 55, bw, 22, "FPV акро (TWR 10.0)", size=12, bold=True, fill="#edf2f7", stroke=LINE))
    frags.append(rect(bx3, 80, bw, 180, fill="#fef9e7", stroke="#d4ac0d", sw=1.5))
    frags.append(mtext(bx3 + bw / 2, 160, ["Надлишковий авторитет", "90.0% динаміки", "Прискорення > 9 g"], size=11, color="#7d6608", bold=True))
    frags.append(rect(bx3, 260, bw, 20, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(bx3 + bw / 2, 274, "10% висіння", size=10, color=NEG, bold=True))
    frags.append(mtext(bx3 + bw / 2, 305, ["Чутливий стік газу", "Високі комутаційні втрати"], size=11, color=INK))

    # Права інформаційна панель
    px = 630
    pw = 230
    frags.append(fitbox(px, 55, pw, 280,
                        "Інженерний компроміс TWR\n\n"
                        "• Низький TWR (1.2–1.8):\n"
                        "  + Максимальна енергоефективність\n"
                        "  − Моторне насичення при вітрі\n"
                        "  − Неможливість різкого маневру\n\n"
                        "• Оптимальний TWR (2.5–4.0):\n"
                        "  + Баланс тривалості та керованості\n"
                        "  + Стабільність у шквальний вітер\n"
                        "  + М'яка лінійна зона ШІМ\n\n"
                        "• Екстремальний TWR (>8.0):\n"
                        "  + Миттєвий вихід із піке\n"
                        "  − Стрибки напруги й пульсації ESC\n"
                        "  − Падіння тривалості польоту",
                        size=11, pad=10, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, "twr-spectrum-and-authority.svg"), w, h, *frags)


def fig_tilt_vector():
    """Векторне розкладання тяги при нахилі рами та потрібний TWR."""
    w, h = 900, 380
    frags = []

    frags.append(text(w / 2, 25, "Векторне розкладання тяги при нахилі рами (Pitch / Roll)", size=16, bold=True))

    cx, cy = 200, 200
    frags.append(line(cx - 90, cy + 60, cx + 90, cy - 60, color=LINE, sw=3))
    frags.append(circle(cx - 90, cy + 60, 8, fill=FILL, stroke=LINE, sw=2))
    frags.append(circle(cx + 90, cy - 60, 8, fill=FILL, stroke=LINE, sw=2))
    frags.append(circle(cx, cy, 14, fill="#edf2f7", stroke=LINE, sw=2))

    tx, ty = cx + 92, cy - 92
    frags.append(arrow(cx, cy, tx, ty, color=POS, sw=2.5))
    frags.append(text(tx + 15, ty - 5, "Повна тяга T_total", size=12, color=POS, bold=True))

    frags.append(arrow(cx, cy, cx, cy - 92, color=FIELD, sw=2))
    frags.append(text(cx - 15, cy - 50, "T_vert = T·cos(θ)", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(cx - 15, cy - 35, "(= m·g для висіння)", size=10, color=FIELD, anchor="end"))

    frags.append(arrow(cx, cy, cx + 92, cy, color=NEG, sw=2))
    frags.append(text(cx + 46, cy + 18, "T_horiz = T·sin(θ)", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(cx + 46, cy + 32, "(рух уперед / опір вітру)", size=10, color=NEG, anchor="middle"))

    frags.append(line(tx, ty, cx, cy - 92, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(tx, ty, cx + 92, cy, color=MUTED, sw=1, dash="4,4"))

    frags.append(arrow(cx, cy, cx, cy + 90, color=INK, sw=2))
    frags.append(text(cx - 12, cy + 85, "Вага m·g", size=12, color=INK, anchor="end", bold=True))

    frags.append(text(cx + 18, cy - 60, "θ = 45°", size=11, color=LINE, bold=True))

    rx = 450
    rw = 410
    frags.append(fitbox(rx, 55, rw, 290,
                        "Залежність потрібної тяги від кута нахилу θ\n\n"
                        "Щоб апарат не втрачав висоту, вертикальна складова\n"
                        "мусить дорівнювати вазі: T · cos(θ) = m · g\n"
                        "Отже, мінімальний необхідний TWR = 1 / cos(θ)\n\n"
                        "• θ = 0°  (висіння):      TWR_min = 1.00  (базовий баланс)\n"
                        "• θ = 30° (плавний рух):   TWR_min = 1.15  (+15% тяги)\n"
                        "• θ = 45° (швидкий політ): TWR_min = 1.41  (+41% тяги)\n"
                        "• θ = 60° (порив вітру):   TWR_min = 2.00  (+100% тяги)\n"
                        "• θ = 70° (екстрений кут): TWR_min = 2.92  (+192% тяги)\n"
                        "• θ = 80° (акробатика):    TWR_min = 5.76  (+476% тяги)\n\n"
                        "Якщо TWR платформи дорівнює 1.5, при нахилі понад 48°\n"
                        "навіть 100% газу не втримають висоту — дрон неминуче падає.",
                        size=11, pad=10, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, "tilt-angle-thrust-vector.svg"), w, h, *frags)


def fig_esc_duty_cycle():
    """ШІМ, комутаційні втрати та пульсації струму на малому газі."""
    w, h = 900, 360
    frags = []

    frags.append(text(w / 2, 25, "Вплив надлишкового TWR на режим роботи ESC і пульсації струму", size=16, bold=True))

    x1 = 50
    w_box = 370
    frags.append(fitbox(x1, 55, w_box, 20, "Надлишковий TWR = 8.0 (Duty cycle D ≈ 12%)", size=11, bold=True, fill="#fdecea", stroke=POS))

    frags.append(rect(x1, 85, w_box, 130, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(line(x1, 150, x1 + w_box, 150, color="#edf2f7", sw=1))
    frags.append(line(x1 + 100, 85, x1 + 100, 215, color="#edf2f7", sw=1))
    frags.append(line(x1 + 200, 85, x1 + 200, 215, color="#edf2f7", sw=1))
    frags.append(line(x1 + 300, 85, x1 + 300, 215, color="#edf2f7", sw=1))

    for px in [x1 + 20, x1 + 100, x1 + 180, x1 + 260]:
        frags.append(rect(px, 105, 12, 80, fill="#fdecea", stroke=POS, sw=1.5))

    frags.append(text(x1 + 60, 100, "Короткі піки струму I_pk", size=10, color=POS, bold=True))
    frags.append(text(x1 + w_box / 2, 205, "Низький Duty Cycle: високі комутаційні втрати MOSFET", size=10, color=MUTED))

    frags.append(fitbox(x1, 225, w_box, 110,
                        "Пастки надлишкового TWR при висінні:\n"
                        "• Високий пульсуючий струм I_ripple = I_motor · √(D·(1-D))\n"
                        "• Нагрів електролітичних конденсаторів через ESR\n"
                        "• Нелінійність тяги на низьких обертах (важко тримати висоту)\n"
                        "• Комутаційні перешкоди (EMI) на лініях датчиків IMU",
                        size=10, pad=6, fill="#f8fafc", stroke=LINE))

    x2 = 470
    frags.append(fitbox(x2, 55, w_box, 20, "Оптимальний TWR = 2.5 (Duty cycle D ≈ 45%)", size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    frags.append(rect(x2, 85, w_box, 130, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(line(x2, 150, x2 + w_box, 150, color="#edf2f7", sw=1))
    frags.append(line(x2 + 100, 85, x2 + 100, 215, color="#edf2f7", sw=1))
    frags.append(line(x2 + 200, 85, x2 + 200, 215, color="#edf2f7", sw=1))
    frags.append(line(x2 + 300, 85, x2 + 300, 215, color="#edf2f7", sw=1))

    for px in [x2 + 20, x2 + 100, x2 + 180, x2 + 260]:
        frags.append(rect(px, 105, 36, 80, fill="#eafaf1", stroke=FIELD, sw=1.5))

    frags.append(text(x2 + 70, 100, "Збалансований струм", size=10, color=FIELD, bold=True))
    frags.append(text(x2 + w_box / 2, 205, "Оптимальний Duty Cycle: високий ККД силового каскаду", size=10, color=MUTED))

    frags.append(fitbox(x2, 225, w_box, 110,
                        "Переваги узгодженого TWR:\n"
                        "• Силова частина працює в зоні високого ККД силових ключів\n"
                        "• Мінімальне теплове навантаження на ключі ESC\n"
                        "• Лінійний відгук обертів на зміну сигналу керування\n"
                        "• Чиста силова шина без критичних імпульсних викидів",
                        size=10, pad=6, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, "esc-duty-cycle-and-ripple.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_twr_spectrum()
    fig_tilt_vector()
    fig_esc_duty_cycle()
    print("All figures generated successfully.")
