# -*- coding: utf-8 -*-
"""Фігури для статті vychytka-skhemy-do-rozvodky
(«Вичитка схеми до розводки: ERC, звірка з даташитом, чужі очі»).

Генерація:
    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. erc-pin-matrix: Матриця ERC та механіка PWR_FLAG ───────────────────────
def fig_erc_pin_matrix():
    W, H = 820, 420
    p = []

    # Заголовок блоку 1: Логіка перевірки типів виводів
    p.append(text(205, 28, "Матриця сумісності пінів в ERC", size=14, bold=True, color=INK))
    
    # Спрощена матриця
    cols = ["Input", "Output", "Pwr Out", "Passive"]
    rows = ["Input", "Output", "Pwr In", "Passive"]
    ox, oy = 40, 50
    cw, rh = 75, 42

    # Заголовки стовпців
    for j, c in enumerate(cols):
        p.append(rect(ox + (j + 1) * cw, oy, cw, rh, fill="#e8ecf2", stroke=LINE, sw=1.2, rx=0))
        p.append(text(ox + (j + 1) * cw + cw / 2, oy + 26, c, size=11, bold=True, color=INK))

    # Заголовки рядків і клітинки
    matrix_res = [
        # In,    Out,   PwrOut, Pass
        [("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD)],   # Input
        [("OK", "#d4edda", FIELD), ("КОНФЛІКТ", "#f8d7da", POS), ("КОНФЛІКТ", "#f8d7da", POS), ("OK", "#d4edda", FIELD)], # Output
        [("ПОМИЛКА", "#f8d7da", POS), ("ПОМИЛКА", "#f8d7da", POS), ("OK", "#d4edda", FIELD), ("УВАГА", "#fff3cd", "#b78103")], # Pwr In
        [("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD), ("OK", "#d4edda", FIELD)]    # Passive
    ]

    for i, r in enumerate(rows):
        # Рядок заголовок
        p.append(rect(ox, oy + (i + 1) * rh, cw, rh, fill="#e8ecf2", stroke=LINE, sw=1.2, rx=0))
        p.append(text(ox + cw / 2, oy + (i + 1) * rh + 26, r, size=11, bold=True, color=INK))
        # Клітинки
        for j in range(len(cols)):
            lbl, bg_col, txt_col = matrix_res[i][j]
            p.append(rect(ox + (j + 1) * cw, oy + (i + 1) * rh, cw, rh, fill=bg_col, stroke=LINE, sw=1.0, rx=0))
            p.append(text(ox + (j + 1) * cw + cw / 2, oy + (i + 1) * rh + 26, lbl, size=10, bold=True, color=txt_col))

    # Пояснення під матрицею
    p.append(rect(ox, oy + 5 * rh + 12, 4 * cw + cw, 80, fill=FILL, stroke=MUTED, sw=1.0, rx=4))
    p.append(text(ox + 12, oy + 5 * rh + 32, "• Output до Output: пряме коротке замикання двох виходів (помилка)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(ox + 12, oy + 5 * rh + 52, "• Power In без Power Out: лінія живлення знеструмлена (помилка)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(ox + 12, oy + 5 * rh + 72, "• Passive до всього: ERC вважає дозволеним, навіть якщо там КЗ", size=11, color=INK, anchor="start"))

    # Розділювач
    p.append(line(435, 20, 435, 400, color=MUTED, sw=1.0, dash="4 4"))

    # Блок 2: Механіка PWR_FLAG
    rx0 = 455
    p.append(text(rx0 + 170, 28, "Чому виникає помилка «Power In not driven»", size=14, bold=True, color=INK))

    # Схема 1: Помилка через ферит/діод
    p.append(text(rx0, 60, "1. Схема без PWR_FLAG (хибна помилка ERC):", size=12, bold=True, color=POS, anchor="start"))
    
    # LDO
    b1, _, _ = textbox(rx0 + 50, 105, "LDO\n3.3V", size=10, pad=6, fill="#e8f4f8", stroke=LINE, min_w=65)
    p.append(b1)
    p.append(text(rx0 + 85, 95, "PwrOut", size=9, color=FIELD, anchor="start"))

    # Лінія до фериту
    p.append(line(rx0 + 83, 105, rx0 + 140, 105, color=LINE, sw=1.8))
    
    # Феритова намистина
    p.append(rect(rx0 + 140, 93, 45, 24, fill="#fff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(rx0 + 162, 109, "FB1", size=10, bold=True, color=INK))
    p.append(text(rx0 + 162, 85, "Passive", size=9, color=MUTED))

    # Лінія до МК
    p.append(line(rx0 + 185, 105, rx0 + 260, 105, color=POS, sw=1.8))
    p.append(text(rx0 + 215, 95, "VDDA", size=10, bold=True, color=POS))

    # МК
    b2, _, _ = textbox(rx0 + 295, 105, "MCU\nVDDA", size=10, pad=6, fill="#f8e8e8", stroke=POS, min_w=65)
    p.append(b2)
    p.append(text(rx0 + 262, 118, "PwrIn", size=9, color=POS, anchor="end"))

    # Пояснення помилки
    p.append(rect(rx0, 140, 345, 52, fill="#fdedec", stroke=POS, sw=1.0, rx=4))
    p.append(text(rx0 + 10, 158, "ERC лається: «VDDA is Power Input, but not driven».", size=11, color=POS, anchor="start", bold=True))
    p.append(text(rx0 + 10, 178, "Пасивний FB1 розірвав властивість Power Output!", size=10, color=INK, anchor="start"))

    # Схема 2: Виправлення через PWR_FLAG
    p.append(text(rx0, 220, "2. Правильне рішення: маркер PWR_FLAG", size=12, bold=True, color=FIELD, anchor="start"))
    
    # LDO
    b3, _, _ = textbox(rx0 + 50, 275, "LDO\n3.3V", size=10, pad=6, fill="#e8f4f8", stroke=LINE, min_w=65)
    p.append(b3)
    p.append(line(rx0 + 83, 275, rx0 + 140, 275, color=LINE, sw=1.8))

    # Ферит
    p.append(rect(rx0 + 140, 263, 45, 24, fill="#fff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(rx0 + 162, 279, "FB1", size=10, bold=True, color=INK))

    # Лінія з прапорцем
    p.append(line(rx0 + 185, 275, rx0 + 260, 275, color=FIELD, sw=1.8))
    p.append(text(rx0 + 215, 265, "VDDA", size=10, bold=True, color=FIELD))

    # PWR_FLAG
    p.append(line(rx0 + 225, 275, rx0 + 225, 320, color=FIELD, sw=1.5))
    p.append(circle(rx0 + 225, 275, 3, fill=FIELD, stroke=FIELD))
    p.append(rect(rx0 + 195, 320, 60, 22, fill="#d4edda", stroke=FIELD, sw=1.2, rx=2))
    p.append(text(rx0 + 225, 335, "PWR_FLAG", size=9, bold=True, color=FIELD))

    # МК
    b4, _, _ = textbox(rx0 + 295, 275, "MCU\nVDDA", size=10, pad=6, fill="#e8f8e8", stroke=FIELD, min_w=65)
    p.append(b4)

    # Пояснення виправлення
    p.append(rect(rx0, 355, 345, 48, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(rx0 + 10, 373, "PWR_FLAG оголошує ERC, що ланцюг заживлено.", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(rx0 + 10, 391, "Тепер перевірка проходить успішно (0 помилок).", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "erc-pin-matrix.svg"), W, H, *p)


# ── 2. footprint-pinout-traps: Просторові та полярні пастки ───────────────────
def fig_footprint_pinout_traps():
    W, H = 840, 360
    p = []

    # Секція А: Top View vs Bottom View (QFN / BGA)
    ax0 = 20
    p.append(text(ax0 + 130, 25, "Пастка 1: Вигляд зверху vs знизу", size=13, bold=True, color=INK))
    
    # QFN Top View
    p.append(rect(ax0 + 10, 50, 110, 110, fill="#2c3e50", stroke=LINE, sw=1.5, rx=4))
    p.append(circle(ax0 + 25, 65, 4, fill="#f1c40f", stroke="#f1c40f")) # Pin 1 dot
    p.append(text(ax0 + 65, 110, "QFN (Топ)\nВигляд на плату", size=9, color="#ffffff", bold=True))
    p.append(text(ax0 + 25, 44, "1", size=10, bold=True, color=POS))
    p.append(text(ax0 + 105, 44, "16", size=10, color=MUTED))
    p.append(text(ax0 + 25, 172, "4", size=10, color=MUTED))
    p.append(text(ax0 + 105, 172, "13", size=10, color=MUTED))
    p.append(text(ax0 + 65, 195, "Нумерація проти годинника", size=10, color=FIELD, bold=True))

    # QFN Bottom View
    p.append(rect(ax0 + 150, 50, 110, 110, fill="#34495e", stroke=LINE, sw=1.5, rx=4))
    p.append(rect(ax0 + 175, 75, 60, 60, fill="#7f8c8d", stroke=LINE, sw=1.0, rx=2)) # Thermal Pad
    p.append(text(ax0 + 205, 105, "Exposed\nPad (EP)", size=9, color="#ffffff", bold=True))
    p.append(circle(ax0 + 245, 65, 4, fill="#f1c40f", stroke="#f1c40f")) # Pin 1 dot on bottom is mirrored!
    p.append(text(ax0 + 245, 44, "1 (Дно)", size=10, bold=True, color=POS))
    p.append(text(ax0 + 165, 44, "16", size=10, color=MUTED))
    p.append(text(ax0 + 205, 195, "Дзеркало! За годинником", size=10, color=POS, bold=True))

    # Пояснення під А
    p.append(fitbox(ax0, 220, 260, 120, 
                    "УВАГА: Якщо розробник креслить футпринт\nза кресленням «Bottom View» даташиту\nбез дзеркалювання, усі піни виявляються\nдзеркально переплутаними. Плата йде у смітник.",
                    size=10, fill="#fdfefe", stroke=MUTED, pad=6))

    p.append(line(295, 15, 295, 345, color=MUTED, sw=1.0, dash="3 3"))

    # Секція Б: Роз'єми (IDC / штирі) — нумерація
    bx0 = 310
    p.append(text(bx0 + 120, 25, "Пастка 2: Роз'єми 2-рядні", size=13, bold=True, color=INK))

    # Зигзаг (IDC)
    p.append(rect(bx0 + 10, 50, 100, 120, fill="#eef2f7", stroke=LINE, sw=1.2, rx=3))
    p.append(text(bx0 + 60, 68, "IDC / Шлейф", size=10, bold=True, color=INK))
    zigzag_pins = [(1, 2), (3, 4), (5, 6), (7, 8)]
    for idx, (p1, p2) in enumerate(zigzag_pins):
        py = 85 + idx * 20
        p.append(circle(bx0 + 35, py, 7, fill="#fff", stroke=LINE))
        p.append(text(bx0 + 35, py + 3.5, str(p1), size=9, bold=True, color=INK))
        p.append(circle(bx0 + 85, py, 7, fill="#fff", stroke=LINE))
        p.append(text(bx0 + 85, py + 3.5, str(p2), size=9, bold=True, color=INK))
    p.append(text(bx0 + 60, 185, "Зигзаг: 1-2, 3-4...", size=10, bold=True, color=FIELD))

    # Послідовна (Штирі SIP / деякі конектори)
    p.append(rect(bx0 + 130, 50, 100, 120, fill="#eef2f7", stroke=LINE, sw=1.2, rx=3))
    p.append(text(bx0 + 180, 68, "Послідовна", size=10, bold=True, color=INK))
    seq_pins = [(1, 5), (2, 6), (3, 7), (4, 8)]
    for idx, (p1, p2) in enumerate(seq_pins):
        py = 85 + idx * 20
        p.append(circle(bx0 + 155, py, 7, fill="#fff", stroke=LINE))
        p.append(text(bx0 + 155, py + 3.5, str(p1), size=9, bold=True, color=INK))
        p.append(circle(bx0 + 205, py, 7, fill="#fff", stroke=LINE))
        p.append(text(bx0 + 205, py + 3.5, str(p2), size=9, bold=True, color=INK))
    p.append(text(bx0 + 180, 185, "По рядах: 1..4, 5..8", size=10, bold=True, color=POS))

    # Пояснення під Б
    p.append(fitbox(bx0, 220, 230, 120,
                    "Невідповідність розпіновки роз'єму:\nв схемі символ може мати послідовну\nнумерацію, а футпринт — зигзаг.\nЯк наслідок: шини живлення та сигналів\nпотрапляють на чужі штирі.",
                    size=10, fill="#fdfefe", stroke=MUTED, pad=6))

    p.append(line(560, 15, 560, 345, color=MUTED, sw=1.0, dash="3 3"))

    # Секція В: Полярність конденсаторів
    cx0 = 575
    p.append(text(cx0 + 125, 25, "Пастка 3: Маркування конденсаторів", size=13, bold=True, color=INK))

    # Тантал
    p.append(rect(cx0 + 15, 60, 95, 60, fill="#d4ac0d", stroke=LINE, sw=1.5, rx=3))
    p.append(rect(cx0 + 15, 60, 22, 60, fill="#7d6608", stroke=LINE, sw=1.0, rx=0))
    p.append(text(cx0 + 26, 95, "+", size=16, bold=True, color="#fff"))
    p.append(text(cx0 + 65, 95, "Тантал", size=10, bold=True, color="#fff"))
    p.append(text(cx0 + 62, 135, "Смуга = ПЛЮС (+)", size=10, bold=True, color=POS))

    # Алюмінієвий електроліт
    p.append(circle(cx0 + 180, 90, 32, fill="#bdc3c7", stroke=LINE, sw=1.5))
    p.append(rect(cx0 + 148, 60, 20, 60, fill="#2c3e50", stroke=LINE, sw=1.0, rx=0))
    p.append(text(cx0 + 158, 95, "−", size=16, bold=True, color="#fff"))
    p.append(text(cx0 + 195, 95, "Електроліт", size=9, bold=True, color=INK))
    p.append(text(cx0 + 180, 135, "Смуга = МІНУС (−)", size=10, bold=True, color=NEG))

    # Пояснення під В
    p.append(fitbox(cx0, 165, 250, 175,
                    "СМЕРТЕЛЬНА ПЛУТАНИНА:\nНа танталових SMD-конденсаторах смужка\nпозначає ПОЗИТИВНИЙ вивід (+).\nНа алюмінієвих SMD/DIP — НЕГАТИВНИЙ (−).\n\nЗапаяний навпаки тантал вибухає або\nйде в коротке замикання з вогнем\nу перші ж секунди подачі живлення.",
                    size=10, fill="#fef9e7", stroke="#f1c40f", pad=6))

    render(os.path.join(OUT, "footprint-pinout-traps.svg"), W, H, *p)


# ── 3. phantom-powering-diode: Паразитне живлення через ESD діоди ─────────────
def fig_phantom_powering():
    W, H = 760, 340
    p = []

    p.append(text(380, 25, "Механізм паразитного живлення (Phantom Powering) через захисні діоди", size=14, bold=True, color=INK))

    # Джерело сигналу (Активний датчик / 3.3V)
    p.append(rect(40, 70, 160, 190, fill="#eaf2f8", stroke=LINE, sw=1.5, rx=5))
    p.append(text(120, 95, "Активний пристрій", size=12, bold=True, color=INK))
    p.append(text(120, 115, "(VDD_EXT = 3.3 В)", size=11, color=FIELD, bold=True))
    p.append(text(120, 165, "Вихідний пін TX/GPIO\nрівень ЛОГ. 1 (+3.3 В)", size=10, color=INK))

    # Лінія сигналу
    p.append(line(200, 180, 370, 180, color=POS, sw=2.5))
    p.append(arrow(260, 180, 290, 180, color=POS, sw=2.5))
    p.append(text(285, 170, "I_leak (струм витоку)", size=10, bold=True, color=POS))

    # Мікроконтролер (Знеструмлений / VDD = 0V)
    p.append(rect(370, 55, 350, 220, fill="#fdfefe", stroke=LINE, sw=1.5, rx=5))
    p.append(text(545, 80, "Знеструмлений МК (VDD_MCU вимкнено)", size=12, bold=True, color=POS))

    # Вхідний пін RX
    p.append(circle(370, 180, 4, fill=POS, stroke=LINE))
    p.append(text(395, 175, "RX / GPIO", size=10, bold=True, color=INK))

    # Шина VDD всередині МК
    p.append(line(460, 110, 680, 110, color=POS, sw=2.0, dash="4 2"))
    p.append(text(620, 100, "Внутрішня шина VDD", size=10, bold=True, color=POS))
    p.append(text(620, 125, "U_vdd ≈ 3.3 В − 0.6 В = 2.7 В!", size=10, bold=True, color=POS))

    # Шина GND всередині МК
    p.append(line(460, 250, 680, 250, color=LINE, sw=2.0))
    p.append(text(620, 240, "Шина GND (0 В)", size=10, color=MUTED))

    # Захисний діод верхній (ESD clamp до VDD)
    p.append(line(460, 180, 460, 140, color=POS, sw=2.0))
    p.append(arrow(460, 160, 460, 135, color=POS, sw=2.0))
    # Малюємо діод (трикутник + планка)
    p.append('<polygon points="452,140 468,140 460,126" fill="%s" stroke="%s" stroke-width="1.2"/>' % (POS, LINE))
    p.append(line(452, 126, 468, 126, color=LINE, sw=1.5))
    p.append(line(460, 126, 460, 110, color=POS, sw=2.0))
    p.append(text(505, 140, "ESD діод\n(відкритий)", size=9, bold=True, color=POS))

    # Захисний діод нижній (ESD clamp до GND - закритий)
    p.append(line(460, 180, 460, 205, color=LINE, sw=1.5))
    p.append('<polygon points="452,220 468,220 460,205" fill="#fff" stroke="%s" stroke-width="1.2"/>' % LINE)
    p.append(line(452, 205, 468, 205, color=LINE, sw=1.5))
    p.append(line(460, 220, 460, 250, color=LINE, sw=1.5))
    p.append(text(505, 220, "ESD діод\n(закритий)", size=9, color=MUTED))

    # Блокувальний конденсатор, який заряджається струмом паразитного живлення
    p.append(line(560, 110, 560, 165, color=POS, sw=1.5))
    p.append(line(545, 165, 575, 165, color=LINE, sw=2.0))
    p.append(line(545, 173, 575, 173, color=LINE, sw=2.0))
    p.append(line(560, 173, 560, 250, color=LINE, sw=1.5))
    p.append(text(595, 172, "C_decoupling\n(заряджається)", size=9, color=INK))

    # Пояснення внизу
    p.append(rect(40, 285, 680, 45, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    p.append(text(380, 303, "НАСЛІДКИ: 1) МК починає хаотично стартувати на заниженій напрузі 2.7 В (нестабільний Brown-out).", size=10, color=POS, bold=True))
    p.append(text(380, 320, "2) Перегрів або пробій ESD-діода струмом усього ядра. 3) Ризик тригерного ефекту (Latch-up).", size=10, color=POS))

    render(os.path.join(OUT, "phantom-powering-diode.svg"), W, H, *p)


# ── 4. testability-layout: Організація тестових точок та розривів ─────────────
def fig_testability_layout():
    W, H = 780, 320
    p = []

    p.append(text(390, 25, "Анатомія контрольної зони на схемі: тестові точки та вимірювальні перемички", size=14, bold=True, color=INK))

    # Блок живлення / Вхідна шина
    p.append(rect(30, 60, 130, 120, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(95, 90, "Джерело 3.3V\n(LDO / Buck)", size=11, bold=True, color=FIELD))
    p.append(text(95, 140, "Вихідна шина", size=10, color=MUTED))

    # Провідник живлення
    p.append(line(160, 100, 240, 100, color=FIELD, sw=2.5))
    p.append(text(195, 90, "+3V3_RAW", size=9, bold=True, color=FIELD))

    # Нульовий резистор / Джемпер для вимірювання струму
    p.append(rect(240, 88, 45, 24, fill="#fff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(262, 104, "R_ISO", size=9, bold=True, color=INK))
    p.append(text(262, 75, "0R (0603)", size=9, color=MUTED))
    p.append(text(262, 130, "Розрив для\nамперметра", size=9, bold=True, color=POS))

    # Продовження шини живлення
    p.append(line(285, 100, 420, 100, color=FIELD, sw=2.5))
    p.append(text(340, 90, "+3V3_MCU", size=9, bold=True, color=FIELD))

    # Тестова точка напруги живлення
    p.append(line(370, 100, 370, 160, color=FIELD, sw=1.5))
    p.append(circle(370, 100, 3, fill=FIELD, stroke=FIELD))
    p.append(circle(370, 165, 8, fill="#fff", stroke=FIELD, sw=2.0))
    p.append(text(370, 169, "TP1", size=9, bold=True, color=FIELD))
    p.append(text(370, 190, "TP_3V3\n(Тестова точка)", size=9, bold=True, color=INK))

    # Навантаження (MCU)
    p.append(rect(420, 60, 130, 120, fill="#fdfefe", stroke=LINE, sw=1.5, rx=4))
    p.append(text(485, 90, "Споживач\n(MCU VDD)", size=11, bold=True, color=INK))
    p.append(text(485, 140, "Ядро та периферія", size=10, color=MUTED))

    # Блок швидкісного сигналу (наприклад, SPI_CLK)
    p.append(text(195, 230, "Швидкісна шина (SPI_SCK / I2C_SCL / UART_TX):", size=11, bold=True, color=INK, anchor="start"))
    p.append(line(200, 260, 460, 260, color=LINE, sw=2.0))
    p.append(text(250, 250, "SPI_CLK_10MHz", size=9, color=INK))

    # Тестова точка сигналу
    p.append(line(340, 260, 340, 285, color=LINE, sw=1.5))
    p.append(circle(340, 260, 3, fill=LINE, stroke=LINE))
    p.append(circle(340, 290, 8, fill="#fff", stroke=POS, sw=2.0))
    p.append(text(340, 294, "TP2", size=9, bold=True, color=POS))
    p.append(text(340, 312, "Сигнал", size=9, bold=True, color=POS))

    # Локальна земляна точка поруч!
    p.append(circle(390, 290, 8, fill="#e8ecf2", stroke=LINE, sw=2.0))
    p.append(text(390, 294, "TP3", size=9, bold=True, color=INK))
    p.append(text(390, 312, "GND (земля)", size=9, bold=True, color=MUTED))

    # Відстань між точками
    p.append(line(348, 275, 382, 275, color=MUTED, sw=1.0))
    p.append(line(348, 271, 348, 279, color=MUTED, sw=1.0))
    p.append(line(382, 271, 382, 279, color=MUTED, sw=1.0))
    p.append(text(365, 270, "≤ 5..8 мм", size=9, bold=True, color=FIELD))

    # Пружинка щупа осцилографа (коментар)
    p.append(rect(580, 80, 180, 190, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(670, 105, "Чому потрібна пара\nTP_SIG + TP_GND?", size=11, bold=True, color=INK))
    p.append(fitbox(590, 130, 160, 130,
                    "Довгий 15-см земляний\n«крокодил» щупа має\nпаразитну індуктивність\nL ≈ 150 нГн.\n\nНа фронтах 10 МГц це\nвикликає фальшивий дзвін\nта спотворення сигналу.\nКоротка пружинка між\nTP2 і TP3 дає чистий сигнал!",
                    size=9, fill="#fff", stroke=MUTED, pad=4))

    render(os.path.join(OUT, "testability-layout.svg"), W, H, *p)


if __name__ == "__main__":
    fig_erc_pin_matrix()
    fig_footprint_pinout_traps()
    fig_phantom_powering()
    fig_testability_layout()
    print("Всі 4 фігури успішно згенеровано.")
