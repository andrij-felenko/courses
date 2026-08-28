# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e0a32e"
AMBERBG = "#fff3e0"
REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"


# ── 1. resistor-ladder-cmos: Внутрішня архітектура матриці та ключів ─────────
def fig_resistor_ladder_cmos():
    W, H = 760, 420
    p = []

    # Тло мікросхеми
    p.append(rect(30, 30, 700, 360, fill="#fafbfc", stroke=LINE, sw=1.8, rx=10))
    p.append(text(380, 54, "Внутрішня архітектура цифрового потенціометра (Resistor String + CMOS)", size=13, color=INK, bold=True))

    # Виводи терміналів A і B
    p.append(line(10, 90, 80, 90, color=POS, sw=2.5))
    p.append(circle(80, 90, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(45, 80, "Термінал A", size=11, color=POS, bold=True))

    p.append(line(10, 350, 80, 350, color=NEG, sw=2.5))
    p.append(circle(80, 350, 4, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(45, 370, "Термінал B", size=11, color=NEG, bold=True))

    # Стовпчик резисторів (драбина)
    # Резистори R_0, R_1, ..., R_{N-1}
    y_nodes = [90, 140, 190, 250, 300, 350]
    labels_r = ["R_N", "R_N-1", "...", "R_1", "R_0"]

    # Вертикальна магістраль
    p.append(line(80, 90, 80, 190, color=LINE, sw=2))
    p.append(line(80, 190, 80, 250, color=LINE, sw=2, dash="4 4"))
    p.append(line(80, 250, 80, 350, color=LINE, sw=2))

    # Прямокутники резисторів
    for i in range(len(y_nodes)-1):
        if i == 2:
            p.append(text(80, 224, "• • •", size=14, color=MUTED, bold=True))
            continue
        y_mid = (y_nodes[i] + y_nodes[i+1]) / 2
        p.append(rect(68, y_mid - 14, 24, 28, fill=FILL, stroke=LINE, sw=1.5, rx=2))
        p.append(text(48, y_mid + 4, labels_r[i], size=10, color=MUTED, anchor="end"))

    # Вузли відводів та ключі
    taps = [
        (90, "Крок 255 (Top)", False),
        (140, "Крок 254", False),
        (190, "Крок 253", False),
        (250, "Крок 2", False),
        (300, "Крок 1 (ON)", True),
        (350, "Крок 0 (Bottom)", False)
    ]

    for y, lbl, is_on in taps:
        p.append(circle(80, y, 3.5, fill=LINE, stroke=LINE, sw=1))
        # лінія до ключа
        p.append(line(80, y, 160, y, color=LINE, sw=1.5))
        # блок ключа CMOS
        box_fill = GRNBG if is_on else BG
        box_stroke = FIELD if is_on else LINE
        p.append(rect(160, y - 16, 80, 32, fill=box_fill, stroke=box_stroke, sw=1.6 if is_on else 1.2, rx=4))
        p.append(text(200, y + 4, "CMOS SW" if not is_on else "КЛЮЧ ON", size=9, color=FIELD if is_on else INK, bold=is_on))

        # лінія від ключа до спільної шини повзунка
        p.append(line(240, y, 320, y, color=FIELD if is_on else MUTED, sw=2 if is_on else 1, dash=None if is_on else "3 3"))

    # Спільна шина повзунка (Wiper Bus)
    p.append(line(320, 80, 320, 360, color=FIELD, sw=2.5))
    p.append(text(320, 70, "Внутрішня шина Wiper", size=10, color=FIELD, bold=True))

    # Вихід повзунка через паразитичний опір Rw
    p.append(line(320, 300, 420, 300, color=FIELD, sw=2.5))
    p.append(circle(320, 300, 4, fill=FIELD, stroke=LINE, sw=1.5))

    # Резистор Rw
    p.append(rect(420, 286, 50, 28, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=3))
    p.append(text(445, 304, "Rw", size=11, color=AMBER, bold=True))
    p.append(text(445, 276, "Опір ключа", size=9, color=AMBER))
    p.append(text(445, 330, "≈ 50–200 Ом", size=9, color=MUTED))

    p.append(line(470, 300, 540, 300, color=LINE, sw=2.5))
    p.append(circle(540, 300, 4, fill=INK, stroke=LINE, sw=1.5))
    p.append(line(540, 300, 730, 300, color=FIELD, sw=2.5))
    p.append(text(690, 285, "Термінал W (Wiper)", size=11, color=FIELD, bold=True))

    # Дешифратор і регістр керування
    p.append(rect(430, 90, 270, 140, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(565, 114, "Цифровий блок керування", size=11, color=NEG, bold=True))
    p.append(rect(446, 128, 238, 32, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(565, 148, "Wiper Register (RAM) + EEPROM", size=10, color=INK))

    p.append(rect(446, 170, 238, 48, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(565, 190, "Дешифратор 1-з-256 (Break-Before-Make)", size=9, color=INK, bold=True))
    p.append(text(565, 208, "Запобігає КЗ суміжних щаблів", size=9, color=MUTED))

    # Стрілка від дешифратора до ключів
    p.append(arrow(430, 190, 245, 190, color=NEG, sw=1.6))
    p.append(text(370, 180, "256 ліній Select", size=9, color=NEG, bold=True))

    # Інтерфейсні виводи ззовні
    p.append(line(730, 144, 684, 144, color=NEG, sw=2))
    p.append(text(720, 134, "SPI / I2C / Up-Down", size=9, color=NEG, anchor="end", bold=True))

    render(os.path.join(OUT, "resistor-ladder-cmos.svg"), W, H, *p,
           title="Внутрішня архітектура цифрового потенціометра")


# ── 2. wiper-parasitics-bandwidth: Паразити та обмеження смуги пропускання ────
def fig_wiper_parasitics_bandwidth():
    W, H = 760, 360
    p = []

    # Ліва частина: Еквівалентна схема паразитів
    p.append(rect(30, 30, 330, 300, fill="#fafbfc", stroke=LINE, sw=1.6, rx=8))
    p.append(text(195, 56, "Еквівалентна схема виходу повзунка", size=11, color=INK, bold=True))

    # Дільник R_AW та R_BW
    p.append(line(70, 90, 120, 90, color=POS, sw=2))
    p.append(text(65, 85, "Va", size=10, color=POS, bold=True))
    p.append(rect(120, 76, 50, 28, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    p.append(text(145, 94, "R_AW", size=10, color=INK))

    p.append(line(170, 90, 195, 90, color=LINE, sw=2))
    p.append(line(195, 90, 195, 140, color=LINE, sw=2))

    p.append(line(70, 190, 120, 190, color=NEG, sw=2))
    p.append(text(65, 195, "Vb", size=10, color=NEG, bold=True))
    p.append(rect(120, 176, 50, 28, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    p.append(text(145, 194, "R_BW", size=10, color=INK))
    p.append(line(170, 190, 195, 190, color=LINE, sw=2))

    p.append(circle(195, 140, 3.5, fill=LINE, stroke=LINE, sw=1))

    # Опір ключа Rw
    p.append(line(195, 140, 220, 140, color=LINE, sw=2))
    p.append(rect(220, 126, 44, 28, fill=AMBERBG, stroke=AMBER, sw=1.6, rx=3))
    p.append(text(242, 144, "Rw", size=10, color=AMBER, bold=True))

    # Вихід W і ємність Cw
    p.append(line(264, 140, 310, 140, color=FIELD, sw=2))
    p.append(circle(310, 140, 4, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(line(310, 140, 345, 140, color=FIELD, sw=2))
    p.append(text(335, 128, "Vw", size=11, color=FIELD, bold=True))

    # Паразитна ємність Cw на землю
    p.append(line(310, 140, 310, 190, color=MUTED, sw=1.6))
    # обкладки конденсатора
    p.append(line(298, 190, 322, 190, color=MUTED, sw=2))
    p.append(line(298, 196, 322, 196, color=MUTED, sw=2))
    p.append(line(310, 196, 310, 220, color=MUTED, sw=1.6))
    # земля
    p.append(line(300, 220, 320, 220, color=MUTED, sw=1.5))
    p.append(line(304, 224, 316, 224, color=MUTED, sw=1.5))
    p.append(line(308, 228, 312, 228, color=MUTED, sw=1.5))
    p.append(text(275, 196, "Cw", size=10, color=MUTED, bold=True))
    p.append(text(275, 210, "10–50 пФ", size=9, color=MUTED))

    # Формула Тевеніна внизу
    p.append(rect(45, 246, 300, 70, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(195, 266, "R_eq = (R_AW || R_BW) + Rw", size=10, color=INK, bold=True))
    p.append(text(195, 286, "Найгірший випадок у центрі (Code 128):", size=9, color=POS))
    p.append(text(195, 302, "R_eq(max) = R_AB / 4 + Rw", size=9, color=POS, bold=True))

    # Права частина: Графік АЧХ (Частотна смуга)
    p.append(rect(380, 30, 350, 300, fill=BG, stroke=LINE, sw=1.6, rx=8))
    p.append(text(555, 56, "Спадання смуги пропускання (-3 dB)", size=11, color=INK, bold=True))

    # Осі графіка
    ax0, ay0, ax1, ay1 = 430, 260, 700, 80
    p.append(line(ax0, ay0, ax1, ay0, color=INK, sw=1.6))
    p.append(arrow(ax1 - 1, ay0, ax1, ay0, color=INK, sw=1.6))
    p.append(text(ax1 - 10, ay0 + 18, "Частота f", size=9, color=INK, bold=True))

    p.append(line(ax0, ay0, ax0, ay1, color=INK, sw=1.6))
    p.append(arrow(ax0, ay1 + 1, ax0, ay1, color=INK, sw=1.6))
    p.append(text(ax0 - 8, ay1 + 10, "дБ", size=9, color=INK, bold=True, anchor="end"))

    # Рівні 0 дБ та -3 дБ
    p.append(line(ax0, 100, ax1 - 20, 100, color=MUTED, sw=1, dash="4 3"))
    p.append(text(ax0 - 8, 104, "0 dB", size=9, color=MUTED, anchor="end"))

    p.append(line(ax0, 135, ax1 - 20, 135, color=POS, sw=1, dash="4 3"))
    p.append(text(ax0 - 8, 139, "-3 dB", size=9, color=POS, anchor="end", bold=True))

    # Криві для 10 кОм, 50 кОм, 100 кОм
    # 100 кОм (найвужча смуга)
    p.append(line(ax0, 100, 480, 100, color=POS, sw=2))
    p.append(line(480, 100, 520, 135, color=POS, sw=2))
    p.append(line(520, 135, 590, 240, color=POS, sw=2))
    p.append(text(510, 175, "100 кОм (~100 кГц)", size=9, color=POS, bold=True))

    # 10 кОм (ширша смуга)
    p.append(line(ax0, 100, 580, 100, color=FIELD, sw=2))
    p.append(line(580, 100, 630, 135, color=FIELD, sw=2))
    p.append(line(630, 135, 690, 220, color=FIELD, sw=2))
    p.append(text(630, 120, "10 кОм (~1–4 МГц)", size=9, color=FIELD, bold=True))

    p.append(text(555, 290, "f_-3dB = 1 / (2π · (R_AB/4 + Rw) · Cw)", size=10, color=INK, bold=True))
    p.append(text(555, 310, "Чим більший R_AB, тим сильніший зріз частоти", size=9, color=MUTED))

    render(os.path.join(OUT, "wiper-parasitics-bandwidth.svg"), W, H, *p,
           title="Паразити повзунка та обмеження смуги пропускання")


# ── 3. terminal-voltage-rails: Допустимі напруги на терміналах і діоди підкладки ──
def fig_terminal_voltage_rails():
    W, H = 740, 360
    p = []

    p.append(rect(30, 30, 680, 300, fill="#fafbfc", stroke=LINE, sw=1.6, rx=8))
    p.append(text(370, 54, "Заборона виходу за рейки живлення та небезпека Latch-Up", size=12, color=INK, bold=True))

    # Рейки Vdd і Vss
    p.append(rect(60, 80, 620, 26, fill=REDBG, stroke=POS, sw=1.5, rx=3))
    p.append(text(370, 97, "Шина живлення V_DD (+3.3 В / +5 В / +15 В)", size=10, color=POS, bold=True))

    p.append(rect(60, 270, 620, 26, fill=BLUEBG, stroke=NEG, sw=1.5, rx=3))
    p.append(text(370, 287, "Шина живлення V_SS / GND (0 В / −15 В)", size=10, color=NEG, bold=True))

    # Допустиме вікно для термінала
    p.append(rect(240, 120, 260, 136, fill=GRNBG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(370, 142, "ДОЗВОЛЕНЕ ВІКНО НАПРУГ", size=10, color=FIELD, bold=True))
    p.append(text(370, 162, "V_SS ≤ V_A, V_B, V_W ≤ V_DD", size=11, color=FIELD, bold=True))
    p.append(text(370, 184, "CMOS-ключі у лінійному режимі", size=9, color=INK))
    p.append(text(370, 202, "Спотворення мінімальні", size=9, color=INK))

    # Паразитні діоди до рейок
    # Верхній діод до Vdd
    p.append(line(150, 188, 150, 106, color=POS, sw=1.8))
    p.append(rect(130, 130, 40, 30, fill=BG, stroke=POS, sw=1.4, rx=3))
    p.append(text(150, 150, "▲ D1", size=10, color=POS, bold=True))
    p.append(text(150, 172, "Паразитний", size=9, color=POS))

    # Нижній діод до Vss
    p.append(line(150, 188, 150, 270, color=NEG, sw=1.8))
    p.append(rect(130, 214, 40, 30, fill=BG, stroke=NEG, sw=1.4, rx=3))
    p.append(text(150, 234, "▼ D2", size=10, color=NEG, bold=True))
    p.append(text(150, 256, "Паразитний", size=9, color=NEG))

    p.append(line(80, 188, 240, 188, color=INK, sw=2))
    p.append(circle(150, 188, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(85, 180, "Термінал (A, B, W)", size=10, color=INK, bold=True))

    # Права частина: аварійні випадки
    p.append(rect(520, 120, 170, 60, fill=REDBG, stroke=POS, sw=1.4, rx=4))
    p.append(text(605, 138, "V_сигналу > V_DD + 0.3 В", size=9, color=POS, bold=True))
    p.append(text(605, 154, "D1 відкривається →", size=9, color=POS))
    p.append(text(605, 168, "струм у шину / Latch-up", size=9, color=POS, bold=True))

    p.append(rect(520, 196, 170, 60, fill=REDBG, stroke=POS, sw=1.4, rx=4))
    p.append(text(605, 214, "V_сигналу < V_SS - 0.3 В", size=9, color=POS, bold=True))
    p.append(text(605, 230, "D2 відкривається →", size=9, color=POS))
    p.append(text(605, 244, "КЗ підкладки / вигоряння", size=9, color=POS, bold=True))

    p.append(text(370, 318, "Змінний аудіосигнал (AC) потребує постійного зміщення до V_DD / 2 або двополярного живлення (±V)", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "terminal-voltage-rails.svg"), W, H, *p,
           title="Допустимі напруги на терміналах цифрового потенціометра")


# ── 4. opamp-gain-schemes: Схеми регулювання підсилення ОП ───────────────────
def fig_opamp_gain_schemes():
    W, H = 760, 370
    p = []

    # Ліва схема: ПОМИЛКОВА (Реостат у ланцюзі зворотного зв'язку)
    p.append(rect(30, 30, 335, 310, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(197, 56, "ПОМИЛКА: Реостат у колі ЗЗ", size=11, color=POS, bold=True))

    # ОП трикутник
    p.append(line(240, 130, 240, 190, color=LINE, sw=1.8))
    p.append(line(240, 130, 290, 160, color=LINE, sw=1.8))
    p.append(line(240, 190, 290, 160, color=LINE, sw=1.8))
    p.append(text(250, 145, "−", size=14, color=LINE, bold=True))
    p.append(text(250, 180, "+", size=14, color=LINE, bold=True))

    # Вхід Vin на (+)
    p.append(line(180, 175, 240, 175, color=INK, sw=1.8))
    p.append(text(175, 172, "Vin", size=10, color=INK, bold=True, anchor="end"))

    # Вихід Vout
    p.append(line(290, 160, 340, 160, color=LINE, sw=1.8))
    p.append(circle(340, 160, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(text(348, 164, "Vout", size=10, color=INK, bold=True, anchor="start"))

    # Резистор R1 до землі
    p.append(line(200, 140, 240, 140, color=LINE, sw=1.8))
    p.append(circle(200, 140, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(line(200, 140, 200, 170, color=LINE, sw=1.8))
    p.append(rect(188, 170, 24, 34, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(175, 190, "R1", size=9, color=MUTED, anchor="end"))
    p.append(line(200, 204, 200, 220, color=LINE, sw=1.8))
    p.append(line(192, 220, 208, 220, color=LINE, sw=1.5))
    p.append(line(196, 224, 204, 224, color=LINE, sw=1.5))

    # Зворотний зв'язок: диджипот реостатом
    p.append(line(200, 140, 200, 96, color=LINE, sw=1.8))
    p.append(line(200, 96, 220, 96, color=LINE, sw=1.8))
    p.append(rect(220, 82, 44, 28, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(242, 100, "R_digi", size=9, color=INK))
    p.append(line(264, 96, 276, 96, color=LINE, sw=1.8))
    # Rw послідовно
    p.append(rect(276, 82, 32, 28, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=2))
    p.append(text(292, 100, "Rw", size=9, color=AMBER, bold=True))
    p.append(line(308, 96, 324, 96, color=LINE, sw=1.8))
    p.append(line(324, 96, 324, 160, color=LINE, sw=1.8))
    p.append(circle(324, 160, 3.5, fill=LINE, stroke=LINE, sw=1))

    p.append(rect(45, 240, 305, 86, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(197, 258, "Чому так не можна:", size=10, color=POS, bold=True))
    p.append(text(197, 276, "1. Струм ЗЗ тече крізь Rw (нелінійність)", size=9, color=INK))
    p.append(text(197, 292, "2. Температурний дрейф Rw (TCR ≈ 2000 ppm)", size=9, color=INK))
    p.append(text(197, 308, "3. K_min = 1 + Rw/R1 ≠ 1 (похибка нуля)", size=9, color=INK))

    # Права схема: ПРАВИЛЬНА (Потенціометр на вході або дільник)
    p.append(rect(395, 30, 335, 310, fill=GRNBG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(562, 56, "ПРАВИЛЬНО: Повзунок на високомний вхід", size=11, color=FIELD, bold=True))

    # ОП трикутник
    p.append(line(605, 130, 605, 190, color=LINE, sw=1.8))
    p.append(line(605, 130, 655, 160, color=LINE, sw=1.8))
    p.append(line(605, 190, 655, 160, color=LINE, sw=1.8))
    p.append(text(615, 145, "−", size=14, color=LINE, bold=True))
    p.append(text(615, 180, "+", size=14, color=LINE, bold=True))

    # Постійні резистори ЗЗ (Rf, R1)
    p.append(line(580, 140, 605, 140, color=LINE, sw=1.8))
    p.append(circle(580, 140, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(line(580, 140, 580, 170, color=LINE, sw=1.8))
    p.append(rect(568, 170, 24, 30, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(555, 188, "R1", size=9, color=MUTED, anchor="end"))
    p.append(line(580, 200, 580, 216, color=LINE, sw=1.8))
    p.append(line(572, 216, 588, 216, color=LINE, sw=1.5))
    p.append(line(576, 220, 584, 220, color=LINE, sw=1.5))

    p.append(line(580, 140, 580, 96, color=LINE, sw=1.8))
    p.append(line(580, 96, 615, 96, color=LINE, sw=1.8))
    p.append(rect(615, 82, 36, 28, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(633, 100, "Rf", size=9, color=INK))
    p.append(line(651, 96, 675, 96, color=LINE, sw=1.8))
    p.append(line(675, 96, 675, 160, color=LINE, sw=1.8))
    p.append(line(655, 160, 690, 160, color=LINE, sw=1.8))
    p.append(circle(675, 160, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(text(696, 164, "Vout", size=10, color=INK, bold=True, anchor="start"))

    # Диджипот дільником перед (+)
    p.append(line(415, 120, 445, 120, color=POS, sw=1.8))
    p.append(text(410, 116, "Vin", size=10, color=POS, bold=True, anchor="end"))
    p.append(rect(445, 110, 22, 60, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(435, 144, "DigiPot", size=9, color=MUTED, anchor="end"))

    p.append(line(456, 140, 480, 140, color=FIELD, sw=1.8))
    # Rw
    p.append(rect(480, 128, 28, 24, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=2))
    p.append(text(494, 144, "Rw", size=9, color=AMBER, bold=True))
    p.append(line(508, 140, 605, 175, color=FIELD, sw=1.8))

    p.append(line(456, 170, 456, 196, color=LINE, sw=1.8))
    p.append(line(448, 196, 464, 196, color=LINE, sw=1.5))
    p.append(line(452, 200, 460, 200, color=LINE, sw=1.5))

    p.append(rect(410, 240, 305, 86, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(562, 258, "Переваги потенціометричного входу:", size=10, color=FIELD, bold=True))
    p.append(text(562, 276, "1. Вхідний струм ОП I_B ≈ 0 → спад на Rw = 0", size=9, color=INK))
    p.append(text(562, 292, "2. Ратіометричний TCR (5 ppm) замість 500 ppm", size=9, color=INK))
    p.append(text(562, 308, "3. Ідеально лінійне регулювання 0 ... G_max", size=9, color=INK))

    render(os.path.join(OUT, "opamp-gain-schemes.svg"), W, H, *p,
           title="Схеми регулювання коефіцієнта підсилення ОП")


# ── 5. dcdc-feedback-safe-trim: Безпечне підстроювання DC-DC (FB) ────────────
def fig_dcdc_feedback_safe_trim():
    W, H = 760, 380
    p = []

    # Ліва схема: НЕБЕЗПЕЧНА
    p.append(rect(30, 30, 335, 320, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(197, 56, "СМЕРТЕЛЬНА СХЕМА (Пряме включення)", size=11, color=POS, bold=True))

    p.append(rect(60, 86, 120, 60, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    p.append(text(120, 112, "DC-DC Buck", size=10, color=INK, bold=True))
    p.append(text(120, 130, "V_FB = 0.8 В", size=9, color=MUTED))

    # Вихід Vout
    p.append(line(180, 100, 310, 100, color=POS, sw=2.2))
    p.append(circle(310, 100, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(318, 104, "Vout", size=10, color=POS, bold=True, anchor="start"))

    # Дільник до FB
    p.append(line(260, 100, 260, 126, color=LINE, sw=1.8))
    p.append(rect(248, 126, 24, 30, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(236, 144, "R_top", size=9, color=MUTED, anchor="end"))

    p.append(line(260, 156, 260, 190, color=LINE, sw=1.8))
    p.append(circle(260, 190, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(line(260, 190, 180, 130, color=NEG, sw=1.8))
    p.append(text(210, 150, "FB", size=10, color=NEG, bold=True))

    # Голий диджипот у нижньому плечі
    p.append(line(260, 190, 260, 210, color=LINE, sw=1.8))
    p.append(rect(244, 210, 32, 40, fill=REDBG, stroke=POS, sw=1.6, rx=2))
    p.append(text(260, 234, "DigiPot", size=9, color=POS, bold=True))
    p.append(line(260, 250, 260, 266, color=LINE, sw=1.8))
    p.append(line(252, 266, 268, 266, color=LINE, sw=1.5))
    p.append(line(256, 270, 264, 270, color=LINE, sw=1.5))

    p.append(rect(45, 276, 305, 60, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(197, 292, "При скиданні / обриві повзунка:", size=9, color=POS, bold=True))
    p.append(text(197, 308, "V_FB падає до 0 В → DC-DC видає V_max (24 В!)", size=9, color=POS, bold=True))
    p.append(text(197, 324, "УСЕ НАВАНТАЖЕННЯ МИТТЄВО ВИГОРАЄ", size=9, color=POS, bold=True))

    # Права схема: БЕЗПЕЧНА (Коридор регулювання)
    p.append(rect(395, 30, 335, 320, fill=GRNBG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(562, 56, "БЕЗПЕЧНА СХЕМА (Паралельне підмішування)", size=11, color=FIELD, bold=True))

    p.append(rect(425, 86, 120, 60, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    p.append(text(485, 112, "DC-DC Buck", size=10, color=INK, bold=True))
    p.append(text(485, 130, "V_FB = 0.8 В", size=9, color=MUTED))

    # Вихід Vout
    p.append(line(545, 100, 680, 100, color=POS, sw=2.2))
    p.append(circle(680, 100, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(688, 104, "Vout", size=10, color=POS, bold=True, anchor="start"))

    # Базовий дільник R1 / R2
    p.append(line(610, 100, 610, 120, color=LINE, sw=1.8))
    p.append(rect(598, 120, 24, 26, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(586, 134, "R1", size=9, color=MUTED, anchor="end"))
    p.append(line(610, 146, 610, 180, color=LINE, sw=1.8))
    p.append(circle(610, 180, 3.5, fill=LINE, stroke=LINE, sw=1))
    p.append(line(610, 180, 545, 130, color=NEG, sw=1.8))
    p.append(text(568, 150, "FB", size=10, color=NEG, bold=True))

    p.append(line(610, 180, 610, 206, color=LINE, sw=1.8))
    p.append(rect(598, 206, 24, 26, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(586, 220, "R2", size=9, color=MUTED, anchor="end"))
    p.append(line(610, 232, 610, 256, color=LINE, sw=1.8))
    p.append(line(602, 256, 618, 256, color=LINE, sw=1.5))

    # Гілка безпечного підстроювання через R_series + DigiPot
    p.append(line(610, 180, 670, 180, color=FIELD, sw=1.8))
    p.append(rect(670, 168, 28, 24, fill=FILL, stroke=LINE, sw=1.4, rx=2))
    p.append(text(684, 184, "R_s", size=9, color=MUTED))
    p.append(line(698, 180, 706, 180, color=FIELD, sw=1.8))
    p.append(rect(706, 166, 18, 56, fill=GRNBG, stroke=FIELD, sw=1.4, rx=2))
    p.append(line(715, 222, 715, 240, color=LINE, sw=1.8))
    p.append(line(708, 240, 722, 240, color=LINE, sw=1.5))

    p.append(rect(410, 276, 305, 60, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(562, 292, "Гарантований коридор безпеки:", size=9, color=FIELD, bold=True))
    p.append(text(562, 308, "Навіть при обриві/КЗ диджипота: 3.0 В ≤ Vout ≤ 3.6 В", size=9, color=INK, bold=True))
    p.append(text(562, 324, "R1 і R2 не дають напрузі вилетіти у небезпечну зону", size=9, color=MUTED))

    render(os.path.join(OUT, "dcdc-feedback-safe-trim.svg"), W, H, *p,
           title="Безпечне підстроювання вихідної напруги DC-DC перетворювача")


# ── 6. control-interfaces: Інтерфейси керування та типи пам'яті ──────────────
def fig_control_interfaces():
    W, H = 740, 360
    p = []

    p.append(rect(30, 30, 680, 300, fill="#fafbfc", stroke=LINE, sw=1.6, rx=8))
    p.append(text(370, 54, "Інтерфейси керування та організація пам'яті", size=12, color=INK, bold=True))

    # Ліва колонка: Шини (SPI, I2C)
    p.append(rect(50, 80, 310, 140, fill=BLUEBG, stroke=NEG, sw=1.6, rx=6))
    p.append(text(205, 102, "Цифрові послідовні шини", size=11, color=NEG, bold=True))
    p.append(text(70, 126, "• SPI (до 50 МГц):", size=10, color=INK, anchor="start", bold=True))
    p.append(text(85, 144, "CS, SCK, SDI, SDO (Daisy-Chain підтримка)", size=9, color=MUTED, anchor="start"))
    p.append(text(70, 168, "• I2C (100 / 400 кГц / 1 МГц):", size=10, color=INK, anchor="start", bold=True))
    p.append(text(85, 186, "SDA, SCL, адресні ніжки A0/A1 (до 4 чипів на шині)", size=9, color=MUTED, anchor="start"))
    p.append(text(205, 210, "Повний контроль, зчитування значення", size=9, color=NEG, italic=True))

    # Права колонка: Імпульсні та кнопкові
    p.append(rect(380, 80, 310, 140, fill=GRNBG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(535, 102, "Імпульсні та автономні інтерфейси", size=11, color=FIELD, bold=True))
    p.append(text(400, 126, "• Up/Down (3-провідний лічильник):", size=10, color=INK, anchor="start", bold=True))
    p.append(text(415, 144, "CS (вибір), U/D (напрям), INC (кроковий такт)", size=9, color=MUTED, anchor="start"))
    p.append(text(400, 168, "• Push-Button (прямі кнопки):", size=10, color=INK, anchor="start", bold=True))
    p.append(text(415, 186, "Кнопки UP / DOWN з вбудованим антибрязкотом", size=9, color=MUTED, anchor="start"))
    p.append(text(535, 210, "Працює без мікроконтролера", size=9, color=FIELD, italic=True))

    # Нижній блок: Організація пам'яті
    p.append(rect(50, 234, 640, 86, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(370, 254, "Архітектура пам'яті положення повзунка", size=11, color=INK, bold=True))

    p.append(rect(70, 268, 270, 42, fill=BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(205, 284, "Volatile (RAM)", size=10, color=INK, bold=True))
    p.append(text(205, 300, "POR → Mid-scale (0x80) або нуль", size=9, color=MUTED))

    p.append(arrow(345, 289, 385, 289, color=LINE, sw=1.5))

    p.append(rect(390, 268, 280, 42, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=4))
    p.append(text(530, 284, "Non-Volatile (EEPROM)", size=10, color=AMBER, bold=True))
    p.append(text(530, 300, "Автозбереження та завантаження при старті", size=9, color=INK))

    render(os.path.join(OUT, "control-interfaces.svg"), W, H, *p,
           title="Інтерфейси керування цифровими потенціометрами")


if __name__ == "__main__":
    fig_resistor_ladder_cmos()
    fig_wiper_parasitics_bandwidth()
    fig_terminal_voltage_rails()
    fig_opamp_gain_schemes()
    fig_dcdc_feedback_safe_trim()
    fig_control_interfaces()
    print("Усі 6 фігур згенеровано успішно.")
