# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Конструкція, яку не зібрати неправильно'."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_poka_yoke_layers():
    """Фігура 1: Чотири рівні апаратного Poka-Yoke."""
    w, h = 840, 500
    frags = []

    frags.append(text(w / 2, 28, "Ешелонований апаратний захист від людських помилок", size=16, bold=True))

    layers = [
        ("Рівень 1: Механічна неможливість помилки",
         "Ключовані роз'єми, асиметричні корпуси, напрямні штифти, несумісні форм-фактори",
         "Помилкове з'єднання фізично заблоковано до появи електричного контакту",
         "#eaf5ea", "#27ae60"),
        ("Рівень 2: Електрична стійкість схемотехніки",
         "P-MOSFET / ідеальні діоди на вході живлення, струмообмежувальні резистори, TVS-діоди",
         "Якщо кабель приєднано силою — схема витримує переполюсовку та 24 В на лініях даних",
         "#eaf0fd", "#2457d6"),
        ("Рівень 3: Однозначний візуальний зворотний зв'язок",
         "Маркування Pin 1 поза межами корпусу, підписи сигналів на платі, колірне кодування джгутів",
         "Монтажник і оператор бачать розпіновку та полярність без звернення до креслень",
         "#fef9e7", "#d4ac0d"),
        ("Рівень 4: Програмне самотестування та ізоляція",
         "Безпечне зондування ліній малим струмом, перевірка сигнатур, автоперемикання або Fault-стан",
         "Прошивка виявляє переплутані канали (TX/RX, SDA/SCL) і блокує роботу силових кіл",
         "#fdf2e9", "#e67e22")
    ]

    y_start = 55
    box_h = 96
    gap = 12

    for i, (title, desc, takeaway, fill_c, stroke_c) in enumerate(layers):
        y = y_start + i * (box_h + gap)
        frags.append(rect(30, y, 780, box_h, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        frags.append(text(50, y + 26, title, size=14, color=INK, anchor="start", bold=True))
        frags.append(text(50, y + 50, desc, size=12, color=INK, anchor="start"))
        frags.append(text(50, y + 76, f"→ {takeaway}", size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG_DIR, "poka-yoke-layers.svg"), w, h, *frags)


def fig_connector_keying():
    """Фігура 2: Механічні ключі, роз'єми та асиметрія плати."""
    w, h = 900, 430
    frags = []

    frags.append(text(w / 2, 28, "Механічні бар'єри: ключування, поляризація та асиметрія", size=16, bold=True))

    # Секція 1: Ключований роз'єм (JST / Molex)
    x1, y1, w1, h1 = 30, 55, 270, 355
    frags.append(rect(x1, y1, w1, h1, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x1 + w1 / 2, y1 + 24, "Поляризовані роз'єми", size=14, bold=True))

    cx1 = x1 + w1 / 2
    # Корпус вилки
    frags.append(rect(cx1 - 65, y1 + 48, 130, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    # Піни всередині
    for p in range(4):
        px = cx1 - 45 + p * 30
        frags.append(circle(px, y1 + 85, 4, fill="#f39c12", stroke=LINE, sw=1))

    # Ключова защіпка зверху над корпусом без налізання
    frags.append(rect(cx1 - 30, y1 + 36, 60, 10, fill="#bdc3c7", stroke=LINE, sw=1.5, rx=2))

    frags.append(text(cx1, y1 + 145, "Molex Micro-Fit / JST GH", size=12, bold=True))
    frags.append(text(cx1, y1 + 170, "• Асиметричні напрямні ребра", size=11, color=INK))
    frags.append(text(cx1, y1 + 192, "• Защіпка (latch) від вібрацій", size=11, color=INK))
    frags.append(text(cx1, y1 + 214, "• Неможливо вставити з поворотом", size=11, color=INK))
    frags.append(text(cx1, y1 + 236, "• Захист контактів від торкання", size=11, color=INK))
    frags.append(rect(x1 + 15, y1 + 265, w1 - 30, 75, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=4))
    frags.append(text(cx1, y1 + 288, "Результат:", size=11, color="#27ae60", bold=True))
    frags.append(text(cx1, y1 + 308, "Фізична заборона зсуву чи перевороту", size=10.5, color=INK))
    frags.append(text(cx1, y1 + 326, "навіть при монтажі наосліп", size=10.5, color=MUTED, italic=True))

    # Секція 2: Диференціація роз'ємів за функціями
    x2, y2, w2, h2 = 315, 55, 270, 355
    frags.append(rect(x2, y2, w2, h2, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x2 + w2 / 2, y2 + 24, "Різні калібри та гнізда", size=14, bold=True))

    cx2 = x2 + w2 / 2
    # Креслення 2 різних роз'ємів
    frags.append(rect(cx2 - 100, y2 + 48, 85, 55, fill="#ffffff", stroke="#c0392b", sw=1.5, rx=3))
    frags.append(text(cx2 - 58, y2 + 72, "24 В Сила", size=11, color="#c0392b", bold=True))
    frags.append(text(cx2 - 58, y2 + 90, "2-pin / 3.81 мм", size=10, color=MUTED))

    frags.append(rect(cx2 + 15, y2 + 48, 85, 55, fill="#ffffff", stroke="#2457d6", sw=1.5, rx=3))
    frags.append(text(cx2 + 58, y2 + 72, "3.3 В Давачі", size=11, color="#2457d6", bold=True))
    frags.append(text(cx2 + 58, y2 + 90, "4-pin / 1.25 мм", size=10, color=MUTED))

    frags.append(text(cx2, y2 + 145, "Несумісні лінії — різні роз'єми", size=12, bold=True))
    frags.append(text(cx2, y2 + 170, "• Різний крок виводів (pitch)", size=11, color=INK))
    frags.append(text(cx2, y2 + 192, "• Різна кількість контактів (pin count)", size=11, color=INK))
    frags.append(text(cx2, y2 + 214, "• Заборона однакових роз'ємів для", size=11, color=INK))
    frags.append(text(cx2, y2 + 234, "  силових 24 В і чутливих 3.3 В ліній", size=11, color=INK))
    frags.append(rect(x2 + 15, y2 + 265, w2 - 30, 75, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=4))
    frags.append(text(cx2, y2 + 288, "Результат:", size=11, color="#27ae60", bold=True))
    frags.append(text(cx2, y2 + 308, "Силовий кабель 24 В неможливо", size=10.5, color=INK))
    frags.append(text(cx2, y2 + 326, "встромити в гніздо інтерфейсів", size=10.5, color=MUTED, italic=True))

    # Секція 3: Асиметрія кріплень та плати
    x3, y3, w3, h3 = 600, 55, 270, 355
    frags.append(rect(x3, y3, w3, h3, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x3 + w3 / 2, y3 + 24, "Асиметрія плати та отворів", size=14, bold=True))

    cx3 = x3 + w3 / 2
    # Креслення плати зі зсунутим отвором
    frags.append(rect(cx3 - 85, y3 + 45, 170, 75, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(circle(cx3 - 65, y3 + 60, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(circle(cx3 + 65, y3 + 60, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(circle(cx3 - 65, y3 + 105, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(circle(cx3 + 40, y3 + 95, 5, fill="#ffffff", stroke="#c0392b", sw=2))
    frags.append(text(cx3 + 40, y3 + 114, "зсув отвору", size=9.5, color="#c0392b", bold=True))

    frags.append(text(cx3, y3 + 145, "Геометричний захист монтажу", size=12, bold=True))
    frags.append(text(cx3, y3 + 170, "• Зсув координат одного монтажного отвору", size=11, color=INK))
    frags.append(text(cx3, y3 + 192, "• Напрямні штифти різного діаметра", size=11, color=INK))
    frags.append(text(cx3, y3 + 214, "• Скошений кут (chamfer) плати", size=11, color=INK))
    frags.append(text(cx3, y3 + 236, "• Неможливо встановити догори дном", size=11, color=INK))
    frags.append(rect(x3 + 15, y3 + 265, w3 - 30, 75, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=4))
    frags.append(text(cx3, y3 + 288, "Результат:", size=11, color="#27ae60", bold=True))
    frags.append(text(cx3, y3 + 308, "Плата фізично не сідає на стійки при", size=10.5, color=INK))
    frags.append(text(cx3, y3 + 326, "помилковій орієнтації монтажника", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, "connector-keying-mechanisms.svg"), w, h, *frags)


def fig_reverse_polarity_circuits():
    """Фігура 3: Схеми захисту від переполюсовки живлення."""
    w, h = 880, 440
    frags = []

    frags.append(text(w / 2, 28, "Порівняння схемотехнічних рішень захисту від переполюсовки", size=16, bold=True))

    # Схема A: Діод Шотткі
    xa, ya, wa, ha = 30, 55, 395, 175
    frags.append(rect(xa, ya, wa, ha, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(xa + 20, ya + 24, "А. Послідовний діод Шотткі", size=13, color=INK, anchor="start", bold=True))

    frags.append(line(xa + 25, ya + 65, xa + 85, ya + 65, color=LINE, sw=2))
    frags.append(text(xa + 25, ya + 55, "VIN+", size=11, color=POS, bold=True))
    frags.append(rect(xa + 85, ya + 50, 45, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(xa + 107, ya + 70, "D1", size=12, color=INK, bold=True))
    frags.append(line(xa + 130, ya + 65, xa + 195, ya + 65, color=LINE, sw=2))
    frags.append(text(xa + 195, ya + 55, "VOUT+", size=11, color=POS, bold=True))
    # Навантаження
    frags.append(rect(xa + 180, ya + 75, 45, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(xa + 202, ya + 102, "RL", size=11, color=INK, bold=True))
    frags.append(line(xa + 202, ya + 120, xa + 202, ya + 140, color=LINE, sw=2))
    frags.append(line(xa + 25, ya + 140, xa + 202, ya + 140, color=LINE, sw=2))
    frags.append(text(xa + 25, ya + 158, "GND (VIN−)", size=11, color=NEG, bold=True))

    frags.append(text(xa + wa - 15, ya + 60, "Спад напруги: 0.35–0.55 В", size=11, color=POS, anchor="end", bold=True))
    frags.append(text(xa + wa - 15, ya + 80, "Втрати: P = I · Vf (при 4 А → 1.8 Вт)", size=10.5, color=INK, anchor="end"))
    frags.append(text(xa + wa - 15, ya + 100, "Плюс: 1 деталь, надійно, дешево", size=10.5, color=FIELD, anchor="end"))
    frags.append(text(xa + wa - 15, ya + 120, "Мінус: нагрів, непридатний для батарей", size=10.5, color=POS, anchor="end"))

    # Схема B: Паралельний діод + PPTC самовідновний запобіжник
    xb, yb, wb, hb = 455, 55, 395, 175
    frags.append(rect(xb, yb, wb, hb, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(xb + 20, yb + 24, "Б. Паралельний діод + самовідновний PPTC", size=13, color=INK, anchor="start", bold=True))

    frags.append(line(xb + 25, yb + 65, xb + 70, yb + 65, color=LINE, sw=2))
    frags.append(text(xb + 25, yb + 55, "VIN+", size=11, color=POS, bold=True))
    frags.append(rect(xb + 70, yb + 53, 50, 24, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(xb + 95, yb + 69, "PPTC", size=10.5, color=INK, bold=True))
    frags.append(line(xb + 120, yb + 65, xb + 195, yb + 65, color=LINE, sw=2))
    frags.append(line(xb + 155, yb + 65, xb + 155, yb + 82, color=LINE, sw=1.5))
    frags.append(rect(xb + 140, yb + 82, 30, 26, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(xb + 155, yb + 99, "D1", size=10.5, color=INK, bold=True))
    frags.append(line(xb + 155, yb + 108, xb + 155, yb + 140, color=LINE, sw=1.5))
    frags.append(line(xb + 25, yb + 140, xb + 195, yb + 140, color=LINE, sw=2))
    frags.append(text(xb + 25, yb + 158, "GND (VIN−)", size=11, color=NEG, bold=True))
    frags.append(text(xb + 200, yb + 55, "VOUT+", size=11, color=POS, bold=True))

    frags.append(text(xb + wb - 15, yb + 60, "Спад напруги: 0.05–0.15 В", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(xb + wb - 15, yb + 80, "При переполюсовці: КЗ → PPTC гріється", size=10.5, color=INK, anchor="end"))
    frags.append(text(xb + wb - 15, yb + 100, "Плюс: малий спад у штатному режимі", size=10.5, color=FIELD, anchor="end"))
    frags.append(text(xb + wb - 15, yb + 120, "Мінус: стрес джерела, спрацювання 0.5 с", size=10.5, color=POS, anchor="end"))

    # Схема C: P-канальний MOSFET у плюсовій шині (High-Side)
    xc, yc, wc, hc = 30, 245, 395, 180
    frags.append(rect(xc, yc, wc, hc, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(xc + 20, yc + 24, "В. P-канальний MOSFET (High-Side)", size=13, color=INK, anchor="start", bold=True))

    frags.append(line(xc + 25, yc + 65, xc + 75, yc + 65, color=LINE, sw=2))
    frags.append(text(xc + 25, yc + 55, "VIN+", size=11, color=POS, bold=True))
    frags.append(rect(xc + 75, yc + 48, 65, 35, fill="#ffffff", stroke="#2457d6", sw=1.8, rx=4))
    frags.append(text(xc + 107, yc + 70, "P-MOS", size=11, color="#2457d6", bold=True))
    frags.append(line(xc + 140, yc + 65, xc + 195, yc + 65, color=LINE, sw=2))
    frags.append(text(xc + 195, yc + 55, "VOUT+", size=11, color=POS, bold=True))
    frags.append(line(xc + 90, yc + 83, xc + 90, yc + 115, color=LINE, sw=1.5))
    frags.append(rect(xc + 75, yc + 115, 30, 22, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(xc + 90, yc + 130, "R_gs", size=10, color=INK))
    frags.append(line(xc + 90, yc + 137, xc + 90, yc + 155, color=LINE, sw=1.5))
    frags.append(line(xc + 25, yc + 155, xc + 195, yc + 155, color=LINE, sw=2))
    frags.append(text(xc + 25, yc + 172, "GND (VIN−)", size=11, color=NEG, bold=True))

    frags.append(text(xc + wc - 15, yc + 60, "Спад напруги: 0.01–0.03 В (I · Rds_on)", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(xc + wc - 15, yc + 80, "Rds(on) = 15–30 мОм, нульовий нагрів", size=10.5, color=INK, anchor="end"))
    frags.append(text(xc + wc - 15, yc + 100, "Плюс: спільна нерозривна шина GND", size=10.5, color=FIELD, anchor="end"))
    frags.append(text(xc + wc - 15, yc + 120, "Захист затвора: стабілітрон ZD 12–15 В", size=10.5, color=INK, anchor="end"))

    # Схема D: Контролер ідеального діода (Ideal Diode Controller)
    xd, yd, wd, hd = 455, 245, 395, 180
    frags.append(rect(xd, yd, wd, hd, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(xd + 20, yd + 24, "Г. Контролер «ідеального діода» (LM74700-Q)", size=13, color=INK, anchor="start", bold=True))

    frags.append(line(xd + 25, yd + 65, xd + 75, yd + 65, color=LINE, sw=2))
    frags.append(text(xd + 25, yd + 55, "VIN+", size=11, color=POS, bold=True))
    frags.append(rect(xd + 75, yd + 48, 65, 35, fill="#ffffff", stroke="#27ae60", sw=1.8, rx=4))
    frags.append(text(xd + 107, yd + 70, "N-MOS", size=11, color="#27ae60", bold=True))
    frags.append(line(xd + 140, yd + 65, xd + 195, yd + 65, color=LINE, sw=2))
    frags.append(text(xd + 195, yd + 55, "VOUT+", size=11, color=POS, bold=True))
    frags.append(rect(xd + 75, yd + 102, 95, 38, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    frags.append(text(xd + 122, yd + 120, "LM74700-Q", size=10.5, color=INK, bold=True))
    frags.append(text(xd + 122, yd + 133, "Charge Pump", size=9.5, color=MUTED))
    frags.append(line(xd + 25, yd + 155, xd + 195, yd + 155, color=LINE, sw=2))
    frags.append(text(xd + 25, yd + 172, "GND (VIN−)", size=11, color=NEG, bold=True))

    frags.append(text(xd + wd - 15, yd + 60, "Регульований спад: 20 мВ", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(xd + wd - 15, yd + 80, "Час блокування зворотного струму: < 0.5 мкс", size=10.5, color=INK, anchor="end"))
    frags.append(text(xd + wd - 15, yd + 100, "Плюс: мінімальний опір дешевого N-MOS", size=10.5, color=FIELD, anchor="end"))
    frags.append(text(xd + wd - 15, yd + 120, "Застосування: сервери, автоелектроніка, БПЛА", size=10.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG_DIR, "reverse-polarity-circuits.svg"), w, h, *frags)


def fig_bus_protection():
    """Фігура 4: Захист ліній зв'язку від перенапруг та переплутаних кабелів."""
    w, h = 840, 370
    frags = []

    frags.append(text(w / 2, 28, "Схема захисту сигнальних ліній при помилковому потраплянні 24 В", size=16, bold=True))

    # Секція зліва: Зовнішній вхідний роз'єм
    frags.append(rect(30, 60, 145, 280, fill="#fdedec", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(text(102, 88, "Зовнішній роз'єм", size=13, color="#c0392b", bold=True))
    frags.append(text(102, 108, "(ризик 24 В / КЗ)", size=11, color=MUTED))

    frags.append(line(102, 160, 220, 160, color=LINE, sw=2))
    frags.append(circle(102, 160, 5, fill="#c0392b", stroke=LINE, sw=1.5))
    frags.append(text(90, 152, "Лінія даних", size=11, color=INK, anchor="end"))

    frags.append(line(102, 280, 760, 280, color=LINE, sw=2))
    frags.append(circle(102, 280, 5, fill="#2457d6", stroke=LINE, sw=1.5))
    frags.append(text(90, 275, "GND", size=11, color=NEG, anchor="end", bold=True))

    # Центральна секція: Ланцюг захисту
    frags.append(rect(205, 60, 365, 280, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(text(387, 88, "Каскад апаратного захисту", size=13, color="#27ae60", bold=True))

    # 1. Послідовний резистор / PTC
    frags.append(rect(225, 146, 65, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(257, 164, "R_lim", size=11, color=INK, bold=True))
    frags.append(text(257, 136, "100–330 Ом", size=10, color=MUTED))
    frags.append(line(290, 160, 365, 160, color=LINE, sw=2))

    # 2. TVS діод на землю
    frags.append(line(365, 160, 365, 200, color=LINE, sw=1.5))
    frags.append(rect(348, 200, 34, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(365, 220, "TVS", size=10.5, color=INK, bold=True))
    frags.append(line(365, 230, 365, 280, color=LINE, sw=1.5))
    frags.append(text(365, 258, "зріз сплесків", size=9.5, color=MUTED))

    frags.append(line(365, 160, 470, 160, color=LINE, sw=2))

    # 3. Діоди фіксації (Rail-to-Rail Clamping BAT54S)
    frags.append(line(470, 115, 470, 280, color=LINE, sw=1.5))
    frags.append(rect(453, 120, 34, 26, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(470, 137, "D_hi", size=10, color=INK))
    frags.append(text(470, 108, "+3.3V VDD", size=10, color=POS, bold=True))

    frags.append(rect(453, 215, 34, 26, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(470, 232, "D_lo", size=10, color=INK))

    frags.append(line(470, 160, 595, 160, color=LINE, sw=2))

    # Секція справа: Мікроконтролер / Трансивер
    frags.append(rect(595, 60, 215, 280, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(702, 88, "Чутливий МК / PHY", size=13, color=INK, bold=True))
    frags.append(text(702, 108, "(допустимо 0 .. 3.6 В)", size=11, color=MUTED))

    frags.append(rect(625, 140, 155, 40, fill="#ffffff", stroke="#2457d6", sw=1.5, rx=4))
    frags.append(text(702, 165, "GPIO / UART / I2C", size=11, color="#2457d6", bold=True))

    frags.append(text(702, 215, "Струм обмежено:", size=11, color=FIELD, bold=True))
    frags.append(text(702, 235, "I_inj = (24V − 3.6V)/R", size=10.5, color=INK))
    frags.append(text(702, 255, "≤ 2–5 мА (безпечно)", size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "bus-miswire-protection.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_poka_yoke_layers()
    fig_connector_keying()
    fig_reverse_polarity_circuits()
    fig_bus_protection()
    print("All figures successfully generated in img/")
