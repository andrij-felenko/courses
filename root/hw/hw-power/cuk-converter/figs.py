#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми 'Перетворювач Ćuk' (cuk-converter).
Створює діаграми:
1. topology.svg — базова принципова схема перетворювача Ćuk з позначенням вузлів і полярностей.
2. two-phases.svg — дві фази комутації (Фаза 1: Q1 ON, D1 OFF; Фаза 2: Q1 OFF, D1 ON).
3. waveforms.svg — часові діаграми струмів і напруг ключових елементів (v_gate, i_L1, i_L2, i_Q1, i_D1, v_C1, v_SW1, v_SW2).
4. coupled-core.svg — принцип зв'язаних індуктивностей на спільному осерді та скидання пульсацій (ripple steering).
5. stress-comparison.svg — порівняння навантаження на ключі й конденсатори між основними топологіями.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def draw_topology():
    """Схема перетворювача Ćuk з усіма компонентами, вузлами та полярностями."""
    w, h = 880, 480
    frags = []

    # Заголовок блоків
    frags.append(text(w / 2, 32, "Принципова схема топології Ćuk", size=18, bold=True))
    frags.append(text(w / 2, 54, "Передача енергії через ємність C1 при безперервних вхідному та вихідному струмах", size=13, color=MUTED))

    # Рамка всієї схеми
    frags.append(rect(30, 75, 820, 380, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Джерело вхідної напруги
    frags.append(circle(90, 240, 24, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(90, 235, "Vвх", size=15, bold=True))
    frags.append(text(90, 253, "+ / −", size=12, color=MUTED))

    # Шина землі (знизу)
    frags.append(line(90, 380, 790, 380, color=LINE, sw=2.5))
    frags.append(text(440, 404, "Спільна шина 0 В (GND)", size=13, bold=True, color=MUTED))
    # Позначення заземлення
    for gx in [90, 440, 790]:
        frags.append(line(gx, 380, gx, 394, color=LINE, sw=2))
        frags.append(line(gx - 10, 394, gx + 10, 394, color=LINE, sw=2))
        frags.append(line(gx - 6, 398, gx + 6, 398, color=LINE, sw=1.5))
        frags.append(line(gx - 2, 402, gx + 2, 402, color=LINE, sw=1.2))

    # З'єднання від джерела до вхідного вузла
    frags.append(line(90, 216, 90, 140, color=LINE, sw=2))
    frags.append(line(90, 140, 150, 140, color=LINE, sw=2))
    frags.append(line(90, 264, 90, 380, color=LINE, sw=2))

    # Вхідний фільтруючий конденсатор Свх
    frags.append(line(130, 140, 130, 215, color=LINE, sw=1.5))
    frags.append(line(116, 215, 144, 215, color=LINE, sw=2.5))
    frags.append(line(116, 225, 144, 225, color=LINE, sw=2.5))
    frags.append(line(130, 225, 130, 380, color=LINE, sw=1.5))
    frags.append(text(158, 224, "Свх", size=13, bold=True))

    # Вхідна індуктивність L1
    frags.append(line(130, 140, 180, 140, color=LINE, sw=2))
    frags.append(rect(180, 122, 90, 36, fill="#eef3fc", stroke=NEG, sw=2, rx=4))
    frags.append(text(225, 145, "L1 (вхідна)", size=13, bold=True, color=NEG))
    frags.append(line(270, 140, 330, 140, color=LINE, sw=2))

    # Вузол SW1 (Вузол A)
    frags.append(circle(330, 140, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(330, 118, "Вузол SW1 (A)", size=12, bold=True, color=POS))

    # Ключ Q1 (MOSFET / транзисторний перемикач до GND)
    frags.append(line(330, 140, 330, 195, color=LINE, sw=2))
    frags.append(rect(290, 195, 80, 50, fill="#fff5f5", stroke=POS, sw=2, rx=4))
    frags.append(text(330, 218, "Ключ Q1", size=13, bold=True, color=POS))
    frags.append(text(330, 235, "(N-MOSFET)", size=11, color=MUTED))
    frags.append(line(330, 245, 330, 380, color=LINE, sw=2))

    # Проміжний накопичувальний конденсатор C1
    frags.append(line(330, 140, 405, 140, color=LINE, sw=2))
    frags.append(line(405, 120, 405, 160, color=POS, sw=3.5))
    frags.append(line(420, 120, 420, 160, color=NEG, sw=3.5))
    frags.append(text(412, 105, "C1 (передавальний)", size=13, bold=True))
    frags.append(text(395, 132, "+", size=16, bold=True, color=POS))
    frags.append(text(432, 132, "−", size=16, bold=True, color=NEG))
    frags.append(text(412, 180, "V_C1 = Vвх + |Vвих|", size=12, bold=True, color=INK))
    frags.append(line(420, 140, 495, 140, color=LINE, sw=2))

    # Вузол SW2 (Вузол B)
    frags.append(circle(495, 140, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(495, 118, "Вузол SW2 (B)", size=12, bold=True, color=NEG))

    # Діод D1 (або синхронний ключ) між вузлом B і GND
    frags.append(line(495, 140, 495, 200, color=LINE, sw=2))
    frags.append(rect(455, 200, 80, 50, fill="#f0f4ff", stroke=NEG, sw=2, rx=4))
    frags.append(text(495, 222, "Діод D1", size=13, bold=True, color=NEG))
    frags.append(text(495, 239, "Анод B → Катод GND", size=10, color=MUTED))
    frags.append(line(495, 250, 495, 380, color=LINE, sw=2))

    # Вихідна індуктивність L2
    frags.append(line(495, 140, 555, 140, color=LINE, sw=2))
    frags.append(rect(555, 122, 95, 36, fill="#eef3fc", stroke=NEG, sw=2, rx=4))
    frags.append(text(602, 145, "L2 (вихідна)", size=13, bold=True, color=NEG))
    frags.append(line(650, 140, 715, 140, color=LINE, sw=2))

    # Вихідний вузол Vвих (інвертований, від'ємний!)
    frags.append(circle(715, 140, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(715, 118, "Вихідний вузол", size=12, bold=True, color=NEG))

    # Вихідний конденсатор Свих
    frags.append(line(715, 140, 715, 215, color=LINE, sw=2))
    frags.append(line(701, 215, 729, 215, color=NEG, sw=2.5))
    frags.append(line(701, 225, 729, 225, color=POS, sw=2.5))
    frags.append(line(715, 225, 715, 380, color=LINE, sw=2))
    frags.append(text(678, 224, "Свих", size=13, bold=True))
    frags.append(text(738, 212, "−", size=15, bold=True, color=NEG))
    frags.append(text(738, 234, "+", size=15, bold=True, color=POS))

    # Навантаження Rнав
    frags.append(line(715, 140, 790, 140, color=LINE, sw=2))
    frags.append(line(790, 140, 790, 205, color=LINE, sw=2))
    frags.append(rect(772, 205, 36, 70, fill="#ffffff", stroke=LINE, sw=2, rx=2))
    frags.append(text(790, 244, "Rнав", size=13, bold=True))
    frags.append(line(790, 275, 790, 380, color=LINE, sw=2))

    # Позначення вихідної напруги
    frags.append(text(790, 118, "Vвих < 0 (інвертована)", size=13, bold=True, color=NEG))

    # Стрілки струмів
    frags.append(arrow(145, 130, 175, 130, color=FIELD, sw=2))
    frags.append(text(160, 120, "i_вх (L1)", size=11, bold=True, color=FIELD))

    frags.append(arrow(665, 130, 695, 130, color=FIELD, sw=2))
    frags.append(text(680, 120, "i_L2", size=11, bold=True, color=FIELD))

    # Пояснювальні плашки внизу
    frags.append(fitbox(50, 420, 370, 42, "Вхідний порт: L1 згладжує i_вх\nСтрум від джерела безперервний", size=11, fill="#f0faf4", stroke=FIELD))
    frags.append(fitbox(460, 420, 370, 42, "Вихідний порт: L2 згладжує i_вих\nСтрум у навантаження безперервний", size=11, fill="#f0faf4", stroke=FIELD))

    return render(os.path.join(OUT_DIR, "topology.svg"), w, h, *frags)


def draw_two_phases():
    """Дві фази роботи комутатора перетворювача Ćuk."""
    w, h = 900, 520
    frags = []

    frags.append(text(w / 2, 28, "Два стани комутації перетворювача Ćuk (режим CCM)", size=18, bold=True))
    frags.append(text(w / 2, 48, "Фаза 1: Q1 замкнений (D·T); Фаза 2: Q1 розімкнений ((1−D)·T)", size=13, color=MUTED))

    # Ліва половина — Фаза 1 (Q1 ON)
    frags.append(rect(20, 68, 415, 430, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    frags.append(text(227, 95, "Фаза 1: Ключ Q1 ON, Діод D1 OFF", size=15, bold=True, color=POS))
    frags.append(text(227, 115, "Тривалість: t ∈ [0, D·T]", size=12, color=MUTED))

    # Схема Фази 1
    frags.append(circle(60, 210, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(60, 215, "Vвх", size=11, bold=True))
    frags.append(line(60, 194, 60, 150, color=LINE, sw=1.5))
    frags.append(line(60, 150, 95, 150, color=LINE, sw=1.5))
    frags.append(line(60, 226, 60, 330, color=LINE, sw=1.5))
    frags.append(line(60, 330, 395, 330, color=LINE, sw=2))  # GND

    # L1
    frags.append(rect(95, 138, 55, 24, fill="#eef3fc", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(122, 154, "L1", size=12, bold=True))
    frags.append(line(150, 150, 195, 150, color=LINE, sw=1.5))

    # Q1 (замкнений провідник!)
    frags.append(circle(195, 150, 4, fill=POS, stroke=POS, sw=1))
    frags.append(line(195, 150, 195, 330, color=POS, sw=3))  # замкнено
    frags.append(text(168, 240, "Q1 ON", size=12, bold=True, color=POS))
    frags.append(text(168, 255, "(0 В)", size=11, color=MUTED))

    # C1 (розряджається в L2)
    frags.append(line(195, 150, 240, 150, color=LINE, sw=1.5))
    frags.append(line(240, 135, 240, 165, color=POS, sw=2.5))
    frags.append(line(248, 135, 248, 165, color=NEG, sw=2.5))
    frags.append(text(244, 125, "C1", size=11, bold=True))
    frags.append(line(248, 150, 290, 150, color=LINE, sw=1.5))

    # D1 (розімкнений!)
    frags.append(circle(290, 150, 4, fill=NEG, stroke=NEG, sw=1))
    frags.append(line(290, 150, 290, 210, color=LINE, sw=1.5, dash="4,3"))
    frags.append(line(290, 260, 290, 330, color=LINE, sw=1.5, dash="4,3"))
    frags.append(text(326, 235, "D1 OFF", size=12, bold=True, color=MUTED))
    frags.append(text(326, 250, "(розрив)", size=10, color=MUTED))

    # L2
    frags.append(line(290, 150, 325, 150, color=LINE, sw=1.5))
    frags.append(rect(325, 138, 55, 24, fill="#eef3fc", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(352, 154, "L2", size=12, bold=True))
    frags.append(line(380, 150, 395, 150, color=LINE, sw=1.5))

    # Навантаження та Cout
    frags.append(line(395, 150, 395, 330, color=LINE, sw=1.5))
    frags.append(text(400, 240, "Cout || R", size=11, bold=True))

    # Струми Фази 1 (контури)
    frags.append(arrow(110, 175, 150, 175, color=FIELD, sw=2))
    frags.append(text(130, 192, "Заряд L1", size=11, bold=True, color=FIELD))

    frags.append(arrow(260, 175, 305, 175, color=FIELD, sw=2))
    frags.append(text(285, 192, "Розряд C1 в L2", size=11, bold=True, color=FIELD))

    # Текстовий підсумок Фази 1
    p1_desc = (
        "• L1 підключена прямо до Vвх: струм i_L1 зростає зі швидкістю +Vвх / L1.\n"
        "• Ліва обкладка C1 сідає на GND: права обкладка падає до −(Vвх + |Vвих|).\n"
        "• D1 закритий зворотною напругою V_D = −(Vвх + |Vвих|).\n"
        "• C1 розряджається в L2 і навантаження: струм i_L2 зростає."
    )
    frags.append(fitbox(30, 350, 395, 135, p1_desc, size=11, fill="#fbfcfd", stroke=MUTED))

    # Права половина — Фаза 2 (Q1 OFF)
    frags.append(rect(465, 68, 415, 430, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(672, 95, "Фаза 2: Ключ Q1 OFF, Діод D1 ON", size=15, bold=True, color=NEG))
    frags.append(text(672, 115, "Тривалість: t ∈ [D·T, T]", size=12, color=MUTED))

    # Схема Фази 2
    frags.append(circle(505, 210, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(505, 215, "Vвх", size=11, bold=True))
    frags.append(line(505, 194, 505, 150, color=LINE, sw=1.5))
    frags.append(line(505, 150, 540, 150, color=LINE, sw=1.5))
    frags.append(line(505, 226, 505, 330, color=LINE, sw=1.5))
    frags.append(line(505, 330, 840, 330, color=LINE, sw=2))  # GND

    # L1
    frags.append(rect(540, 138, 55, 24, fill="#eef3fc", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(567, 154, "L1", size=12, bold=True))
    frags.append(line(595, 150, 640, 150, color=LINE, sw=1.5))

    # Q1 (розімкнений!)
    frags.append(circle(640, 150, 4, fill=POS, stroke=POS, sw=1))
    frags.append(line(640, 150, 640, 210, color=LINE, sw=1.5, dash="4,3"))
    frags.append(line(640, 260, 640, 330, color=LINE, sw=1.5, dash="4,3"))
    frags.append(text(612, 235, "Q1 OFF", size=12, bold=True, color=MUTED))
    frags.append(text(612, 250, "(розрив)", size=10, color=MUTED))

    # C1 (заряджається від L1)
    frags.append(line(640, 150, 685, 150, color=LINE, sw=1.5))
    frags.append(line(685, 135, 685, 165, color=POS, sw=2.5))
    frags.append(line(693, 135, 693, 165, color=NEG, sw=2.5))
    frags.append(text(689, 125, "C1", size=11, bold=True))
    frags.append(line(693, 150, 735, 150, color=LINE, sw=1.5))

    # D1 (замкнений провідник!)
    frags.append(circle(735, 150, 4, fill=NEG, stroke=NEG, sw=1))
    frags.append(line(735, 150, 735, 330, color=NEG, sw=3))  # замкнено
    frags.append(text(766, 240, "D1 ON", size=12, bold=True, color=NEG))
    frags.append(text(766, 255, "(0 В)", size=11, color=MUTED))

    # L2
    frags.append(line(735, 150, 770, 150, color=LINE, sw=1.5))
    frags.append(rect(770, 138, 55, 24, fill="#eef3fc", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(797, 154, "L2", size=12, bold=True))
    frags.append(line(825, 150, 840, 150, color=LINE, sw=1.5))

    # Навантаження та Cout
    frags.append(line(840, 150, 840, 330, color=LINE, sw=1.5))
    frags.append(text(845, 240, "Cout || R", size=11, bold=True))

    # Струми Фази 2 (контури)
    frags.append(arrow(600, 175, 675, 175, color=FIELD, sw=2))
    frags.append(text(640, 192, "L1 заряджає C1", size=11, bold=True, color=FIELD))

    frags.append(arrow(755, 175, 805, 175, color=FIELD, sw=2))
    frags.append(text(780, 192, "L2 розряджається", size=11, bold=True, color=FIELD))

    # Текстовий підсумок Фази 2
    p2_desc = (
        "• D1 відкривається і фіксує вузол SW2 на потенціалі 0 В (GND).\n"
        "• Струм i_L1 тече через C1 і D1 у землю, дозаряджаючи C1 енергією з входу.\n"
        "• Напруга на SW1 злітає до V_C1 = Vвх + |Vвих|.\n"
        "• Котушка L2 замикається через D1 і підтримує струм у навантаженні."
    )
    frags.append(fitbox(475, 350, 395, 135, p2_desc, size=11, fill="#fbfcfd", stroke=MUTED))

    return render(os.path.join(OUT_DIR, "two-phases.svg"), w, h, *frags)


def draw_waveforms():
    """Часові епюри струмів і напруг ключових вузлів за два періоди комутації."""
    w, h = 880, 600
    frags = []

    frags.append(text(w / 2, 28, "Часові епюри перетворювача Ćuk в усталеному режимі (CCM)", size=18, bold=True))
    frags.append(text(w / 2, 48, "Безперервний струм на обох котушках (i_L1, i_L2) проти імпульсних струмів ключів", size=13, color=MUTED))

    # Часова вісь: 2 періоди.
    x_start = 220
    t_dt1 = 360
    t_t1 = 500
    t_dt2 = 640
    t_t2 = 780

    # Вертикальні фонові смуги для фази Q1 ON
    frags.append(rect(x_start, 70, t_dt1 - x_start, 480, fill="#fbf2f2", stroke="none"))
    frags.append(rect(t_t1, 70, t_dt2 - t_t1, 480, fill="#fbf2f2", stroke="none"))

    frags.append(text((x_start + t_dt1) / 2, 85, "Q1 ON (D·T)", size=11, bold=True, color=POS))
    frags.append(text((t_dt1 + t_t1) / 2, 85, "Q1 OFF ((1−D)·T)", size=11, bold=True, color=NEG))
    frags.append(text((t_t1 + t_dt2) / 2, 85, "Q1 ON", size=11, bold=True, color=POS))
    frags.append(text((t_dt2 + t_t2) / 2, 85, "Q1 OFF", size=11, bold=True, color=NEG))

    # 5 сигналів
    # 1. v_gate (керування)
    y1 = 130
    frags.append(text(110, y1, "v_gate (Q1)", size=13, bold=True))
    frags.append(line(x_start - 20, y1, t_t2 + 30, y1, color=MUTED, sw=1))
    frags.append(line(x_start, y1 - 25, t_dt1, y1 - 25, color=POS, sw=2))
    frags.append(line(t_dt1, y1 - 25, t_dt1, y1, color=POS, sw=2))
    frags.append(line(t_dt1, y1, t_t1, y1, color=POS, sw=2))
    frags.append(line(t_t1, y1, t_t1, y1 - 25, color=POS, sw=2))
    frags.append(line(t_t1, y1 - 25, t_dt2, y1 - 25, color=POS, sw=2))
    frags.append(line(t_dt2, y1 - 25, t_dt2, y1, color=POS, sw=2))
    frags.append(line(t_dt2, y1, t_t2, y1, color=POS, sw=2))

    # 2. i_L1 (вхідний струм, безперервний!)
    y2 = 220
    frags.append(text(110, y2, "i_L1 (i_вх, гладкий)", size=13, bold=True, color=FIELD))
    frags.append(line(x_start - 20, y2, t_t2 + 30, y2, color=MUTED, sw=1))
    # трикутні пульсації
    frags.append(line(x_start, y2 + 12, t_dt1, y2 - 18, color=FIELD, sw=2.5))
    frags.append(line(t_dt1, y2 - 18, t_t1, y2 + 12, color=FIELD, sw=2.5))
    frags.append(line(t_t1, y2 + 12, t_dt2, y2 - 18, color=FIELD, sw=2.5))
    frags.append(line(t_dt2, y2 - 18, t_t2, y2 + 12, color=FIELD, sw=2.5))
    frags.append(text(t_t2 + 45, y2 - 4, "I_вх (DC)", size=11, color=FIELD))

    # 3. i_L2 (вихідний струм, безперервний!)
    y3 = 310
    frags.append(text(110, y3, "i_L2 (i_вих, гладкий)", size=13, bold=True, color=FIELD))
    frags.append(line(x_start - 20, y3, t_t2 + 30, y3, color=MUTED, sw=1))
    frags.append(line(x_start, y3 + 12, t_dt1, y3 - 18, color=FIELD, sw=2.5))
    frags.append(line(t_dt1, y3 - 18, t_t1, y3 + 12, color=FIELD, sw=2.5))
    frags.append(line(t_t1, y3 + 12, t_dt2, y3 - 18, color=FIELD, sw=2.5))
    frags.append(line(t_dt2, y3 - 18, t_t2, y3 + 12, color=FIELD, sw=2.5))
    frags.append(text(t_t2 + 45, y3 - 4, "I_вих (DC)", size=11, color=FIELD))

    # 4. i_C1 (струм перенесення через конденсатор C1)
    y4 = 405
    frags.append(text(110, y4 - 10, "i_C1 (струм C1)", size=13, bold=True))
    frags.append(text(110, y4 + 8, "знакозмінний RMS", size=10, color=MUTED))
    frags.append(line(x_start - 20, y4, t_t2 + 30, y4, color=MUTED, sw=1))
    # ON: -i_L2, OFF: +i_L1
    frags.append(line(x_start, y4 + 20, t_dt1, y4 + 20, color=POS, sw=2))
    frags.append(line(t_dt1, y4 + 20, t_dt1, y4 - 20, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(t_dt1, y4 - 20, t_t1, y4 - 20, color=NEG, sw=2))
    frags.append(line(t_t1, y4 - 20, t_t1, y4 + 20, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(t_t1, y4 + 20, t_dt2, y4 + 20, color=POS, sw=2))
    frags.append(line(t_dt2, y4 + 20, t_dt2, y4 - 20, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(t_dt2, y4 - 20, t_t2, y4 - 20, color=NEG, sw=2))
    frags.append(text(285, y4 + 35, "−i_L2 (розряд)", size=10, color=POS))
    frags.append(text(425, y4 - 28, "+i_L1 (заряд)", size=10, color=NEG))

    # 5. v_SW1 (напруга на ключі Q1)
    y5 = 500
    frags.append(text(110, y5, "v_SW1 (напруга Q1)", size=13, bold=True, color=POS))
    frags.append(line(x_start - 20, y5, t_t2 + 30, y5, color=MUTED, sw=1))
    frags.append(line(x_start, y5, t_dt1, y5, color=POS, sw=2))
    frags.append(line(t_dt1, y5, t_dt1, y5 - 32, color=POS, sw=2))
    frags.append(line(t_dt1, y5 - 32, t_t1, y5 - 32, color=POS, sw=2))
    frags.append(line(t_t1, y5 - 32, t_t1, y5, color=POS, sw=2))
    frags.append(line(t_t1, y5, t_dt2, y5, color=POS, sw=2))
    frags.append(line(t_dt2, y5, t_dt2, y5 - 32, color=POS, sw=2))
    frags.append(line(t_dt2, y5 - 32, t_t2, y5 - 32, color=POS, sw=2))
    frags.append(text(430, y5 - 40, "V_pk = Vвх + |Vвих|", size=11, bold=True, color=POS))

    # Пояснення внизу
    frags.append(fitbox(50, 550, 780, 36, "Головна властивість: i_L1 та i_L2 не спадають до нуля й не рвуться; весь імпульсний струм замкнений усередині через C1", size=11, fill="#f0faf4", stroke=FIELD))

    return render(os.path.join(OUT_DIR, "waveforms.svg"), w, h, *frags)


def draw_coupled_core():
    """Принцип зв'язаних індуктивностей (coupled inductors) та скидання пульсацій (ripple steering)."""
    w, h = 880, 520
    frags = []

    frags.append(text(w / 2, 28, "Магнітне об'єднання L1 і L2: режим нульових пульсацій", size=18, bold=True))
    frags.append(text(w / 2, 48, "Керування пульсацією (ripple steering) через коефіцієнт зв'язку k та зазор в осерді", size=13, color=MUTED))

    # Лівий блок — Фізична структура осердя
    frags.append(rect(30, 75, 400, 420, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(230, 102, "Спільне магнітне осердя (E-E / E-I)", size=15, bold=True))

    # E-осердя
    frags.append(rect(80, 130, 300, 180, fill="#e2e8f0", stroke="#475569", sw=2, rx=6))
    # Вирізи для вікон обмоток
    frags.append(rect(140, 160, 60, 120, fill="#ffffff", stroke="#475569", sw=1.5, rx=2))
    frags.append(rect(260, 160, 60, 120, fill="#ffffff", stroke="#475569", sw=1.5, rx=2))

    # Центральне керно з повітряним зазором
    frags.append(rect(198, 215, 64, 12, fill="#ffffff", stroke=POS, sw=1.8, rx=1))
    frags.append(text(230, 224, "Зазор", size=10, bold=True, color=POS))

    # Обмотка 1 (L1) на лівому керні
    frags.append(rect(100, 175, 42, 90, fill="#fee2e2", stroke=POS, sw=2, rx=3))
    frags.append(text(121, 212, "W1 (L1)", size=12, bold=True, color=POS))
    frags.append(text(121, 230, "Вхід", size=10, color=MUTED))

    # Обмотка 2 (L2) на правому керні
    frags.append(rect(318, 175, 42, 90, fill="#dbeafe", stroke=NEG, sw=2, rx=3))
    frags.append(text(339, 212, "W2 (L2)", size=12, bold=True, color=NEG))
    frags.append(text(339, 230, "Вихід", size=10, color=MUTED))

    # Магнітні потоки
    frags.append(arrow(110, 145, 340, 145, color=FIELD, sw=2))
    frags.append(text(230, 140, "Спільний потік Φ_m", size=11, bold=True, color=FIELD))

    # Пояснення геометрії
    core_desc = (
        "• Обидві котушки бачать однакову змінну напругу v_ac.\n"
        "• Зв'язок M = k·√(L1·L2) індукує зустрічну ЕРС.\n"
        "• Зазор в осерді плавно підбирає коефіцієнт зв'язку k."
    )
    frags.append(fitbox(45, 335, 370, 145, core_desc, size=12, fill="#f8fafc", stroke=MUTED))

    # Правий блок — Еквівалентна схема та умова нульових пульсацій
    frags.append(rect(450, 75, 400, 420, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(650, 102, "Умова нульових пульсацій (Δi = 0)", size=15, bold=True, color=FIELD))

    # Плашки умов
    u1 = (
        "Вихід без пульсацій (Δi_L2 = 0):\n"
        "Коефіцієнт трансформації n = k\n"
        "(де n = N2/N1, k = M/√(L1·L2) < 1)\n"
        "Вся змінна пульсація зганяється у вхід L1"
    )
    frags.append(fitbox(470, 120, 360, 90, u1, size=11, fill="#f0faf4", stroke=FIELD, bold=False))

    u2 = (
        "Вхід без пульсацій (Δi_L1 = 0):\n"
        "Коефіцієнт трансформації n = 1 / k\n"
        "(де n = N2/N1 > 1)\n"
        "Вся змінна пульсація зганяється у вихід L2"
    )
    frags.append(fitbox(470, 225, 360, 90, u2, size=11, fill="#eff6ff", stroke=NEG, bold=False))

    # Пояснення фізичного сенсу
    u3 = (
        "Фізика явища (Ripple Steering):\n"
        "Індукована через M змінна напруга в точності\n"
        "компенсує прикладену напругу v_ac.\n"
        "Падіння напруги на індуктивності витоку:\n"
        "v_Lleak = v_ac − (M/L1)·v_ac = 0  ⇒  di/dt = 0"
    )
    frags.append(fitbox(470, 330, 360, 150, u3, size=11, fill="#fafafa", stroke=MUTED))

    return render(os.path.join(OUT_DIR, "coupled-core.svg"), w, h, *frags)



def draw_stress_comparison():
    """Порівняння навантаження на ключі, струмів і фільтрації між 4 основними топологіями."""
    w, h = 880, 460
    frags = []

    frags.append(text(w / 2, 28, "Порівняння перетворювача Ćuk з класичними топологіями", size=18, bold=True))
    frags.append(text(w / 2, 48, "Чим платить інженер за ідеальну гладкість струмів на обох портах", size=13, color=MUTED))

    # Таблиця-карточки 4 топологій
    topos = [
        {
            "name": "Buck (знижувальний)",
            "ratio": "Vвих = D · Vвх",
            "iin": "Імпульсний (рваний)",
            "iout": "Безперервний (гладкий)",
            "vstress": "Vвх",
            "cap": "Тільки фільтри",
            "stroke": MUTED,
            "fill": "#ffffff"
        },
        {
            "name": "Boost (підвищувальний)",
            "ratio": "Vвих = Vвх / (1 − D)",
            "iin": "Безперервний (гладкий)",
            "iout": "Імпульсний (рваний)",
            "vstress": "Vвих",
            "cap": "Тільки фільтри",
            "stroke": MUTED,
            "fill": "#ffffff"
        },
        {
            "name": "Інвертувальний Buck-Boost",
            "ratio": "|Vвих| = Vвх · D / (1 − D)",
            "iin": "Імпульсний (рваний)",
            "iout": "Імпульсний (рваний)",
            "vstress": "Vвх + |Vвих|",
            "cap": "Тільки фільтри",
            "stroke": MUTED,
            "fill": "#ffffff"
        },
        {
            "name": "Перетворювач Ćuk",
            "ratio": "|Vвих| = Vвх · D / (1 − D)",
            "iin": "БЕЗПЕРЕРВНИЙ (L1)",
            "iout": "БЕЗПЕРЕРВНИЙ (L2)",
            "vstress": "Vвх + |Vвих|",
            "cap": "С1 несе ВСЮ потужність",
            "stroke": FIELD,
            "fill": "#f0faf4"
        }
    ]

    col_w = 195
    start_x = 35

    for idx, t_info in enumerate(topos):
        cx = start_x + idx * (col_w + 13)
        frags.append(rect(cx, 75, col_w, 320, fill=t_info["fill"], stroke=t_info["stroke"], sw=2 if idx == 3 else 1.2, rx=6))

        # Заголовок
        frags.append(fitbox(cx + 8, 85, col_w - 16, 40, t_info["name"], size=12, bold=True, fill="#ffffff" if idx != 3 else "#e2f7ea", stroke="none"))

        # Дані
        y_pos = 135
        frags.append(text(cx + col_w / 2, y_pos, "Передатна характеристика:", size=10, color=MUTED))
        frags.append(text(cx + col_w / 2, y_pos + 16, t_info["ratio"], size=11, bold=True))

        y_pos = 180
        frags.append(text(cx + col_w / 2, y_pos, "Вхідний струм (i_вх):", size=10, color=MUTED))
        frags.append(text(cx + col_w / 2, y_pos + 16, t_info["iin"], size=11, bold=True, color=FIELD if "БЕЗПЕРЕРВНИЙ" in t_info["iin"] or "гладкий" in t_info["iin"] else POS))

        y_pos = 225
        frags.append(text(cx + col_w / 2, y_pos, "Вихідний струм (i_вих):", size=10, color=MUTED))
        frags.append(text(cx + col_w / 2, y_pos + 16, t_info["iout"], size=11, bold=True, color=FIELD if "БЕЗПЕРЕРВНИЙ" in t_info["iout"] or "гладкий" in t_info["iout"] else POS))

        y_pos = 270
        frags.append(text(cx + col_w / 2, y_pos, "Стрес напруги на ключах:", size=10, color=MUTED))
        frags.append(text(cx + col_w / 2, y_pos + 16, t_info["vstress"], size=11, bold=True, color=POS if "+" in t_info["vstress"] else INK))

        y_pos = 315
        frags.append(text(cx + col_w / 2, y_pos, "Навантаження на конденсатор:", size=10, color=MUTED))
        frags.append(text(cx + col_w / 2, y_pos + 16, t_info["cap"], size=10, bold=True, color=POS if idx == 3 else INK))

    # Висновок під таблицею
    frags.append(fitbox(35, 405, 810, 40, "Висновок: Ćuk усуває пульсації струмів на обох портах ціною підвищеної напруги на ключах та високого RMS-струму через C1", size=11, fill="#f8fafc", stroke=MUTED))

    return render(os.path.join(OUT_DIR, "stress-comparison.svg"), w, h, *frags)


def main():
    print("Генерація SVG діаграм для теми cuk-converter...")
    draw_topology()
    draw_two_phases()
    draw_waveforms()
    draw_coupled_core()
    draw_stress_comparison()
    print("Усі 5 діаграм згенеровано успішно у ./img/")


if __name__ == "__main__":
    main()
