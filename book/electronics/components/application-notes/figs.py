#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор технічних діаграм для теми application-notes."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_doc_hierarchy():
    """Ієрархія інженерної документації виробника напівпровідників."""
    w, h = 820, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Ієрархія технічної документації напівпровідникових компонентів", size=16, bold=True))

    # 1. Silicon Errata (Червоний статус - найвищий пріоритет правди)
    b_errata, bw, bh = textbox(410, 80, "Silicon Errata (Лист апаратних помилок)\nАпаратні баги кристала, обмеження ревізій та обхідні шляхи (Workarounds)", size=12, pad=10, fill="#fdecea", stroke=POS, bold=True, min_w=680)
    frags.append(b_errata)

    # 2. Datasheet (Офіційний паспорт)
    b_ds, bw, bh = textbox(410, 160, "Datasheet (Паспорт компонента)\nЮридичні межі: Absolute Max, Guaranteed Min/Typ/Max, розпіновка, корпуси", size=12, pad=10, fill="#f4f6f8", stroke=LINE, bold=True, min_w=680)
    frags.append(b_ds)

    # 3. Application Notes (Методологія та розрахунки)
    b_an, bw, bh = textbox(410, 245, "Application Notes (AN / Прикладні інженерні нотатки)\nРозрахунок кіл компенсації (Type II/III), правила PCB Layout, боротьба з EMI", size=12, pad=10, fill="#eaf0fd", stroke=NEG, bold=True, min_w=680)
    frags.append(b_an)

    # 4. Reference Designs & EVB Manuals
    b_rd, bw, bh = textbox(240, 345, "Reference Design (RD)\nПовний проєкт: схема, BOM,\nGerber, теплові карти й EMI-тести", size=12, pad=10, fill="#eafaf1", stroke=FIELD, bold=True, min_w=320)
    frags.append(b_rd)

    b_evb, bw, bh = textbox(580, 345, "Evaluation Board (EVB/EVK)\nМануал налагоджувальної плати:\nджампери, тестові точки, виміри", size=12, pad=10, fill="#fef9e7", stroke="#d4ac0d", bold=True, min_w=320)
    frags.append(b_evb)

    # 5. White Papers & Vendor Simulators
    b_sim, bw, bh = textbox(410, 430, "Vendor Simulators & White Papers (LTspice, WEBENCH, ADIsim)\nКонцептуальні статті, макромоделі та параметричний синтез", size=11, pad=8, fill="#f9f9f9", stroke=MUTED, min_w=680)
    frags.append(b_sim)

    # Стрілки ієрархії пріоритету правди (зверху вниз)
    frags.append(arrow(410, 110, 410, 135, color=POS, sw=2))
    frags.append(arrow(410, 190, 410, 218, color=LINE, sw=2))
    frags.append(arrow(320, 280, 250, 310, color=NEG, sw=1.8))
    frags.append(arrow(500, 280, 570, 310, color=NEG, sw=1.8))
    frags.append(arrow(410, 385, 410, 410, color=MUTED, sw=1.5))

    render(os.path.join(OUT_DIR, "doc-hierarchy.svg"), w, h, *frags)


def fig_hot_loop():
    """Силовий контур Hot Loop у DCDC-стабілізаторі: паразитна індуктивність та EMI."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 26, "Мінімізація площі силового контуру (Hot Loop) у Step-Down DCDC", size=15, bold=True))

    # Зліва: Погане трасування (Велика площа контуру)
    frags.append(rect(30, 55, 360, 360, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(210, 80, "НЕПРАВИЛЬНО: Велика площа Hot Loop", size=13, color=POS, bold=True))

    # Елементи зліва
    frags.append(rect(50, 110, 60, 40, fill="#ffffff", stroke=LINE))
    frags.append(text(80, 135, "C_IN", size=11, bold=True))

    frags.append(rect(280, 110, 80, 70, fill="#ffffff", stroke=LINE))
    frags.append(text(320, 140, "DCDC IC", size=11, bold=True))
    frags.append(text(320, 160, "VIN / SW", size=10, color=MUTED))

    frags.append(rect(170, 270, 80, 40, fill="#ffffff", stroke=LINE))
    frags.append(text(210, 295, "D1 / GND", size=11, bold=True))

    # Довгі доріжки - великий контур
    frags.append(line(110, 130, 280, 130, color=POS, sw=3))
    frags.append(line(320, 180, 320, 290, color=POS, sw=3))
    frags.append(line(320, 290, 250, 290, color=POS, sw=3))
    frags.append(line(170, 290, 80, 290, color=POS, sw=3))
    frags.append(line(80, 290, 80, 150, color=POS, sw=3))

    # Позначення площі та випромінювання
    frags.append(circle(200, 200, 45, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(200, 195, "Велика площа S", size=11, color=POS, bold=True))
    frags.append(text(200, 215, "L_loop ≈ 15 нГн", size=11, color=POS))
    frags.append(text(210, 350, "Високий сплеск V = L·(dI/dt)", size=11, color=POS, bold=True))
    frags.append(text(210, 372, "Потужне випромінювання EMI (радіозавади)", size=10, color=INK))
    frags.append(text(210, 392, "Дзвін на вузлі SW руйнує польові ключі", size=10, color=INK))

    # Справа: Правильне трасування (Компактний контур)
    frags.append(rect(430, 55, 360, 360, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(610, 80, "ПРАВИЛЬНО: Мінімізований Hot Loop", size=13, color=FIELD, bold=True))

    # Елементи справа (впритул)
    frags.append(rect(460, 130, 60, 50, fill="#ffffff", stroke=LINE))
    frags.append(text(490, 160, "C_IN", size=11, bold=True))

    frags.append(rect(540, 130, 90, 70, fill="#ffffff", stroke=LINE))
    frags.append(text(585, 160, "DCDC IC", size=11, bold=True))
    frags.append(text(585, 180, "VIN  PGND", size=10, color=MUTED))

    # Короткий контур
    frags.append(rect(470, 120, 150, 90, fill="none", stroke=FIELD, sw=3, rx=4))
    frags.append(circle(535, 165, 20, fill="#d5f5e3", stroke=FIELD, sw=1.5))
    frags.append(text(535, 168, "S min", size=10, color=FIELD, bold=True))

    # Вихідний фільтр дросель + Cout
    frags.append(rect(660, 140, 50, 40, fill="#ffffff", stroke=LINE))
    frags.append(text(685, 165, "L1", size=11, bold=True))
    frags.append(rect(730, 140, 50, 40, fill="#ffffff", stroke=LINE))
    frags.append(text(755, 165, "C_OUT", size=11, bold=True))
    frags.append(line(630, 160, 660, 160, color=LINE, sw=2))
    frags.append(line(710, 160, 730, 160, color=LINE, sw=2))

    frags.append(text(610, 260, "Кераміка C_IN стоїть упритул до VIN і PGND", size=11, color=FIELD, bold=True))
    frags.append(text(610, 285, "Зворотний струм іде прямою широкою міддю", size=10, color=INK))
    frags.append(text(610, 310, "L_loop < 1.5 нГн → сплески придушено на 80%", size=10, color=FIELD, bold=True))
    frags.append(text(610, 350, "Суцільний суміжний полігон GND під верхнім шаром", size=10, color=INK))
    frags.append(text(610, 372, "Магнітне поле замикається в мікрооб'ємі", size=10, color=INK))
    frags.append(text(610, 392, "Повна відповідність стандартам CISPR 32 / EN 55032", size=10, color=FIELD))

    render(os.path.join(OUT_DIR, "hot-loop-parasitics.svg"), w, h, *frags)


def fig_kelvin_thermal():
    """Кельвінове підключення зворотного зв'язку та теплові перехідні отвори."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 26, "Рекомендації AN: Кельвінове трасування FB та тепловідведення", size=15, bold=True))

    # Зліва: Кельвінове підключення зворотного зв'язку
    frags.append(rect(30, 55, 360, 345, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(210, 80, "Трасування Sense / Feedback (FB)", size=13, bold=True))

    # Компоненти схеми
    frags.append(rect(50, 110, 70, 50, fill="#eaf0fd", stroke=NEG))
    frags.append(text(85, 140, "IC (FB)", size=11, bold=True))

    frags.append(rect(290, 110, 80, 50, fill="#f4f6f8", stroke=LINE))
    frags.append(text(330, 135, "C_OUT", size=11, bold=True))
    frags.append(text(330, 150, "(Навантаження)", size=9, color=MUTED))

    frags.append(rect(150, 200, 60, 35, fill="#ffffff", stroke=LINE))
    frags.append(text(180, 222, "R_TOP", size=10, bold=True))

    frags.append(rect(150, 255, 60, 35, fill="#ffffff", stroke=LINE))
    frags.append(text(180, 277, "R_BOT", size=10, bold=True))

    # Доріжка Sense - прямо від пінів C_OUT
    frags.append(line(330, 160, 330, 218, color=FIELD, sw=2))
    frags.append(line(330, 218, 210, 218, color=FIELD, sw=2))
    frags.append(line(150, 218, 85, 218, color=NEG, sw=2))
    frags.append(line(85, 218, 85, 160, color=NEG, sw=2))
    frags.append(line(180, 235, 180, 255, color=NEG, sw=2))
    frags.append(line(180, 290, 180, 310, color=LINE, sw=2))
    frags.append(text(180, 325, "AGND (Тиха земля)", size=10, color=MUTED))

    frags.append(text(210, 355, "Sense-доріжка йде в обхід силових струмів", size=10, color=FIELD, bold=True))
    frags.append(text(210, 375, "R_top/R_bot стоять УПРИТУЛ до виводу FB чипа", size=10, color=INK))
    frags.append(text(210, 392, "Виключає помилку IR-падіння напруги на міді", size=10, color=INK))

    # Справа: Тепловий полігон з матрицею отворів (Thermal Vias)
    frags.append(rect(430, 55, 360, 345, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(610, 80, "Тепловий полігон PowerPAD / QFN EP", size=13, bold=True))

    # Корпус QFN з відкритим майданчиком
    frags.append(rect(510, 110, 200, 140, fill="#fdf2e9", stroke=POS, sw=1.5, rx=4))
    frags.append(text(610, 130, "QFN Exposed Thermal Pad", size=11, color=POS, bold=True))

    # Сітка перехідних отворів (Thermal vias)
    for row in range(3):
        for col in range(5):
            vx = 540 + col * 35
            vy = 155 + row * 28
            frags.append(circle(vx, vy, 6, fill="#c0392b", stroke="#922b21", sw=1.5))

    frags.append(text(610, 275, "Матриця перехідних отворів 3×5 (d = 0.3 мм)", size=10, color=POS, bold=True))
    frags.append(text(610, 298, "Прямий контакт із внутрішніми шарами GND (2 oz)", size=10, color=INK))
    frags.append(text(610, 320, "Знижує θ_JA з 65 °C/Вт до 28 °C/Вт", size=11, color=FIELD, bold=True))
    frags.append(text(610, 355, "Без перехідних отворів чип іде в Thermal Shutdown", size=10, color=POS))
    frags.append(text(610, 375, "Крок між отворами 1.0…1.2 мм запобігає витоку припою", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "kelvin-and-thermal.svg"), w, h, *frags)


def fig_evb_vs_real():
    """Порівняння Evaluation Board (EVB) виробника та бюджетної 2-шарової плати."""
    w, h = 820, 430
    frags = []

    frags.append(text(w / 2, 26, "Оптимізм Evaluation Board проти реальності 2-шарової плати", size=15, bold=True))

    # Зліва: Демо-плата виробника (EVB)
    frags.append(rect(30, 55, 360, 350, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(210, 80, "Evaluation Board виробника (EVB)", size=13, color=FIELD, bold=True))

    frags.append(textbox(210, 125, "Конструкція плати:\n• 4-6 шарів, товста мідь 2 oz (70 мкм)\n• Діелектрик prepreg 0.1 мм до суцільної GND\n• Паразитна індуктивність L_loop < 0.8 нГн", size=10, pad=8, min_w=320)[0])

    frags.append(textbox(210, 215, "Компонентна база:\n• Преміум MLCC Murata X7R (0805/1206)\n• Екранований дросель Coilcraft (низький DCR)\n• Ідеальні роз'єми SMA / Kelvin test points", size=10, pad=8, min_w=320)[0])

    frags.append(rect(50, 290, 320, 95, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(210, 310, "Результати в даташиті / AN:", size=11, color=FIELD, bold=True))
    frags.append(text(210, 332, "ККД = 95.2 % при струмі 5 А (25 °C, 200 LFM)", size=10, color=INK))
    frags.append(text(210, 352, "Пульсації виходу: V_ripple < 12 мВ", size=10, color=INK))
    frags.append(text(210, 372, "Температура кристала: Tj = 55 °C", size=10, color=INK))

    # Справа: Бюджетна 2-шарова плата
    frags.append(rect(430, 55, 360, 350, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    frags.append(text(610, 80, "Реальна серійна 2-шарова плата", size=13, color=POS, bold=True))

    frags.append(textbox(610, 125, "Конструкція плати:\n• 2 шари, стандартна мідь 1 oz (35 мкм)\n• Товстий FR-4 1.6 мм, розірваний полігон GND\n• Паразитна індуктивність L_loop = 6…12 нГн", size=10, pad=8, min_w=320)[0])

    frags.append(textbox(610, 215, "Компонентна база:\n• Бюджетні MLCC 0603 (-60% ємності від DC bias!)\n• Неекранований дросель (наводить шуми на FB)\n• Довгі силові клеми та роз'єми", size=10, pad=8, min_w=320)[0])

    frags.append(rect(450, 290, 320, 95, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(610, 310, "Реальні виміри на столі:", size=11, color=POS, bold=True))
    frags.append(text(610, 332, "ККД = 88.5 % (втрати на паразитах і DCR)", size=10, color=POS))
    frags.append(text(610, 352, "Пульсації виходу: V_ripple = 140 мВ (дзвін)", size=10, color=POS))
    frags.append(text(610, 372, "Температура кристала: Tj > 115 °C (Thermal Shutdown)", size=10, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "evb-vs-real-board.svg"), w, h, *frags)


def fig_compensation_types():
    """Частотна характеристика та компенсатори Type II та Type III."""
    w, h = 820, 430
    frags = []

    frags.append(text(w / 2, 26, "Частотна корекція контуру регулювання: Type II vs Type III", size=15, bold=True))

    # Зліва: Діаграма Боде (Некомпенсована система vs Скомпенсована)
    frags.append(rect(30, 55, 420, 350, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(240, 80, "ЛАЧХ та ЛФЧ імпульсного перетворювача", size=12, bold=True))

    # Осі
    frags.append(line(60, 220, 420, 220, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(80, 215, "0 dB", size=10, color=MUTED))
    frags.append(line(60, 95, 60, 370, color=LINE, sw=1.5))
    frags.append(line(60, 370, 420, 370, color=LINE, sw=1.5))
    frags.append(text(410, 388, "f (Hz)", size=10, color=MUTED))

    # Крива підсилення некомпенсованого LC фільтра
    frags.append(line(65, 120, 160, 125, color=MUTED, sw=2))
    frags.append(line(160, 125, 220, 220, color=MUTED, sw=2))
    frags.append(line(220, 220, 340, 340, color=MUTED, sw=2, dash="4,2"))
    frags.append(text(215, 140, "LC-полюс (-40 dB/dec)", size=9, color=MUTED))

    # Скомпенсована крива (Type III)
    frags.append(line(65, 110, 140, 145, color=FIELD, sw=2.5))
    frags.append(line(140, 145, 270, 220, color=FIELD, sw=2.5))
    frags.append(line(270, 220, 390, 310, color=FIELD, sw=2.5))
    frags.append(circle(270, 220, 4, fill=POS, stroke=POS))
    frags.append(text(270, 205, "f_c (Crossover)", size=10, color=POS, bold=True))

    # Фазовий підйом
    frags.append(rect(70, 290, 340, 65, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(240, 310, "Фазовий запас (Phase Margin) > 50° на частоті f_c", size=10, color=FIELD, bold=True))
    frags.append(text(240, 330, "Type III додає 2 нулі перед f_LC та піднімає фазу на +120°", size=9, color=INK))
    frags.append(text(240, 346, "Запобігає генерації та перерегулюванню при стрибках струму", size=9, color=INK))

    # Справа: Порівняння Type II та Type III схемотехнічно
    frags.append(rect(470, 55, 320, 350, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(630, 80, "Сфери застосування компенсаторів", size=12, bold=True))

    # Type II
    frags.append(textbox(630, 150, "Type II (1 нуль, 2 полюси):\n• Струмовий режим (Current-Mode Control)\n• 1 полюс навантаження + 1 ESR-нуль\n• Кола: Rc, Cc, Cp на виводі COMP\n• Фазовий підйом: до +90°", size=10, pad=8, fill="#eaf0fd", stroke=NEG, min_w=290)[0])

    # Type III
    frags.append(textbox(630, 290, "Type III (2 нулі, 3 полюси):\n• Режим за напругою (Voltage-Mode)\n• Компенсує подвійний LC-полюс кераміки\n• Кола: R1, R2, R3, C1, C2, C3\n• Фазовий підйом: до +160°", size=10, pad=8, fill="#eafaf1", stroke=FIELD, min_w=290)[0])

    render(os.path.join(OUT_DIR, "type2-type3-compensation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_doc_hierarchy()
    fig_hot_loop()
    fig_kelvin_thermal()
    fig_evb_vs_real()
    fig_compensation_types()
    print("Всі фігури згенеровано успішно.")
