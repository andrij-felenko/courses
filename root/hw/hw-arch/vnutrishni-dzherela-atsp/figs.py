# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Внутрішні джерела АЦП: опора, датчик температури, VBAT».
Генерує 4 SVG-фігури в ./img/ за допомогою svgkit.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектура внутрішніх каналів АЦП ─────────────────────────────
def fig_internal_sources_mux():
    W, H = 820, 480
    P = [text(W / 2, 26, "Архітектура внутрішніх каналів АЦП мікроконтролера", size=16, bold=True)]

    # Зовнішній блок мікроконтролера
    P.append(rect(30, 48, 760, 416, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    P.append(text(50, 72, "Мікроконтролер (MCU Silicon Die)", size=12, color=MUTED, bold=True, anchor="start"))

    # Джерела живлення та опори
    P.append(rect(50, 92, 220, 70, fill="#f4f6f8", stroke=LINE, sw=1.2))
    P.append(text(160, 114, "Шина живлення VDDA / VREF+", size=12, bold=True))
    P.append(text(160, 134, "LDO / Батарея / DC-DC (1.8–3.6 В)", size=11, color=MUTED))
    P.append(text(160, 150, "Опорна напруга для ядра SAR АЦП", size=10, color=NEG))

    # Блок VREFINT
    P.append(rect(50, 180, 220, 76, fill="#eaf0fd", stroke=NEG, sw=1.5))
    P.append(text(160, 202, "VREFINT (Bandgap Опора)", size=12, bold=True, color=NEG))
    P.append(text(160, 222, "Типово 1.212 В ±1.5%", size=11, color=INK))
    P.append(text(160, 240, "Ключ VREFEN + буфер (Rout ≈ 15 кОм)", size=10, color=MUTED))

    # Блок Temperature Sensor
    P.append(rect(50, 274, 220, 76, fill="#fdecea", stroke=POS, sw=1.5))
    P.append(text(160, 296, "Датчик температури (TS)", size=12, bold=True, color=POS))
    P.append(text(160, 316, "PTAT/CTAT p-n перехід кремнію", size=11, color=INK))
    P.append(text(160, 334, "Ключ TSEN (Rout ≈ 100 кОм)", size=10, color=MUTED))

    # Блок VBAT Divider
    P.append(rect(50, 368, 220, 76, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    P.append(text(160, 390, "Монітор батареї VBAT", size=12, bold=True, color=FIELD))
    P.append(text(160, 410, "Дільник напруги (1/2, 1/3 або 1/4)", size=11, color=INK))
    P.append(text(160, 428, "Ключ VBATEN (вимикає витік струму)", size=10, color=MUTED))

    # Аналоговий мультиплексор (Analog MUX)
    P.append(rect(330, 160, 100, 284, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    P.append(mtext(380, 290, ["Аналоговий", "комутатор", "(Analog", "MUX)"], size=12, bold=True))

    # Лінії від блоків до MUX
    P.append(line(270, 218, 330, 218, color=NEG, sw=2))
    P.append(text(300, 210, "CH_VREF", size=10, color=NEG))

    P.append(line(270, 312, 330, 312, color=POS, sw=2))
    P.append(text(300, 304, "CH_TEMP", size=10, color=POS))

    P.append(line(270, 406, 330, 406, color=FIELD, sw=2))
    P.append(text(300, 398, "CH_VBAT", size=10, color=FIELD))

    # Зовнішні канали
    P.append(line(300, 175, 330, 175, color=MUTED, sw=1.5, dash="4 3"))
    P.append(text(290, 175, "GPIO CH0..15", size=10, color=MUTED, anchor="end"))

    # Блок Sample & Hold і SAR ADC
    P.append(rect(480, 180, 150, 150, fill="#f4f6f8", stroke=LINE, sw=1.5))
    P.append(text(555, 204, "Ядро SAR АЦП", size=13, bold=True))
    P.append(line(480, 216, 630, 216, color=MUTED, sw=1))
    P.append(text(555, 238, "Ключ вибірки Rsw", size=11))
    P.append(text(555, 258, "Ємність вибірки C_S (5 пФ)", size=11, color=MUTED))
    P.append(text(555, 282, "12-бітний SAR регістр", size=11, bold=True))
    P.append(text(555, 306, "Шкала: 0..4095", size=11, color=NEG))

    # З'єднання MUX -> SAR ADC
    P.append(arrow(430, 255, 480, 255, color=LINE, sw=2))
    P.append(text(455, 245, "Vin", size=11, bold=True))

    # Опора від VDDA до SAR ADC
    P.append(arrow(270, 127, 555, 127, color=NEG, sw=1.8))
    P.append(arrow(555, 127, 555, 180, color=NEG, sw=1.8))
    P.append(text(410, 118, "VREF+ = VDDA (опорний рівень перетворення)", size=11, color=NEG, bold=True))

    # Блок системної пам'яті Flash (System Memory Calibration)
    P.append(rect(670, 140, 100, 220, fill="#fff9db", stroke="#f59f00", sw=1.5))
    P.append(mtext(720, 170, ["Заводське", "калібрування", "Flash (ROM)"], size=11, bold=True, color="#d9480f"))
    P.append(line(670, 210, 770, 210, color="#f59f00", sw=1))
    P.append(mtext(720, 235, ["VREFINT_CAL", "(3.00 В, 30°C)"], size=10, bold=True))
    P.append(mtext(720, 275, ["TS_CAL1", "(30°C)"], size=10, color=POS, bold=True))
    P.append(mtext(720, 315, ["TS_CAL2", "(110°C)"], size=10, color=POS, bold=True))

    # Вихідний потік
    P.append(arrow(630, 255, 670, 255, color=LINE, sw=1.5))
    P.append(text(650, 245, "Raw", size=10, bold=True))

    # Програмне обчислення
    P.append(rect(480, 360, 290, 84, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    P.append(text(625, 382, "Математична компенсація у прошивці", size=12, bold=True, color=FIELD))
    P.append(text(625, 404, "VDDA = 3000 мВ × VREFINT_CAL / Raw_VREFINT", size=11, bold=True))
    P.append(text(625, 426, "Vx = VDDA × Raw_x / 4095  (точність без зовнішнього VREF)", size=10, color=INK))

    render(os.path.join(IMG, "internal-sources-mux.svg"), W, H, *P)


# ── Фігура 2: Принцип логометричної компенсації при просіданні живлення ─────
def fig_vrefint_ratiometric():
    W, H = 820, 420
    P = [text(W / 2, 26, "Логометрична компенсація: розрахунок VDDA через незмінну VREFINT", size=16, bold=True)]

    # Ліва колонка: VDDA = 3.3 В (повний заряд)
    P.append(rect(50, 60, 330, 330, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    P.append(text(215, 88, "Випадок А: Свіжа батарея (VDDA = 3.30 В)", size=13, bold=True, color=FIELD))

    # Шкала АЦП А
    P.append(rect(80, 115, 50, 220, fill="#ffffff", stroke=LINE, sw=1.2))
    P.append(rect(80, 250, 50, 85, fill="#eaf0fd", stroke=NEG, sw=1.2)) # VREFINT
    P.append(text(105, 130, "3.30 В", size=10, color=MUTED))
    P.append(text(105, 348, "0 В", size=10, color=MUTED))
    P.append(text(105, 295, "VREFINT", size=10, bold=True, color=NEG))
    P.append(text(105, 310, "1.21 В", size=9, color=NEG))

    # Підписи кодів
    P.append(text(145, 122, "Код 4095 (Шкала VDDA)", size=11, bold=True))
    P.append(line(130, 250, 175, 250, color=NEG, sw=1.5, dash="4 2"))
    P.append(text(185, 254, "Raw = 1502", size=12, bold=True, color=NEG, anchor="start"))
    P.append(text(185, 272, "1502 / 4095 = 36.7%", size=10, color=MUTED, anchor="start"))

    P.append(rect(80, 350, 270, 30, fill="#ffffff", stroke=FIELD, sw=1))
    P.append(text(215, 370, "VDDA = 3000 × 1652 / 1502 = 3300 мВ", size=11, bold=True))

    # Права колонка: VDDA = 2.60 В (розряджена батарея)
    P.append(rect(440, 60, 330, 330, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    P.append(text(605, 88, "Випадок Б: Просіле живлення (VDDA = 2.60 В)", size=13, bold=True, color=POS))

    # Шкала АЦП Б
    P.append(rect(470, 115, 50, 220, fill="#ffffff", stroke=LINE, sw=1.2))
    P.append(rect(470, 222, 50, 113, fill="#eaf0fd", stroke=NEG, sw=1.2)) # VREFINT займає більшу частку!
    P.append(text(495, 130, "2.60 В", size=10, color=MUTED))
    P.append(text(495, 348, "0 В", size=10, color=MUTED))
    P.append(text(495, 280, "VREFINT", size=10, bold=True, color=NEG))
    P.append(text(495, 295, "1.21 В", size=9, color=NEG))

    # Підписи кодів
    P.append(text(535, 122, "Код 4095 (Шкала VDDA)", size=11, bold=True))
    P.append(line(520, 222, 565, 222, color=NEG, sw=1.5, dash="4 2"))
    P.append(text(575, 226, "Raw = 1906", size=12, bold=True, color=POS, anchor="start"))
    P.append(text(575, 244, "1906 / 4095 = 46.5%", size=10, color=MUTED, anchor="start"))
    P.append(mtext(650, 285, ["Код виріс, бо опорна", "шкала стиснулася!"], size=10, color=POS, bold=True))

    P.append(rect(470, 350, 270, 30, fill="#ffffff", stroke=POS, sw=1))
    P.append(text(605, 370, "VDDA = 3000 × 1652 / 1906 = 2600 мВ", size=11, bold=True))

    render(os.path.join(IMG, "vrefint-ratiometric.svg"), W, H, *P)


# ── Фігура 3: Двоточкове заводське калібрування датчика температури ─────────
def fig_temperature_calibration():
    W, H = 820, 440
    P = [text(W / 2, 26, "Двоточкове заводське калібрування вбудованого датчика температури", size=16, bold=True)]

    # Область графіка
    ox, oy = 110, 360
    gw, gh = 640, 280

    # Осі
    P.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8)) # Вісь T
    P.append(text(ox + gw - 20, oy + 32, "Температура кристала Tj (°C)", size=12, bold=True))

    P.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8)) # Вісь ADC Code
    P.append(text(ox - 10, oy - gh + 15, "Нормалізований код АЦП (12 біт при 3.0 В)", size=11, bold=True, anchor="end"))

    # Сітка та мітки температури
    x_30 = ox + 160
    x_110 = ox + 480

    P.append(line(x_30, oy, x_30, oy - gh + 40, color=MUTED, sw=1, dash="4 3"))
    P.append(text(x_30, oy + 20, "30 °C (TS_CAL1)", size=11, bold=True, color=POS))

    P.append(line(x_110, oy, x_110, oy - gh + 40, color=MUTED, sw=1, dash="4 3"))
    P.append(text(x_110, oy + 20, "110 °C (TS_CAL2)", size=11, bold=True, color=POS))

    # Точки калібрування
    y_cal1 = oy - 70
    y_cal2 = oy - 230

    P.append(line(ox, y_cal1, x_30, y_cal1, color=MUTED, sw=1, dash="4 3"))
    P.append(text(ox - 10, y_cal1 + 4, "TS_CAL1 (≈1035)", size=10, bold=True, anchor="end"))

    P.append(line(ox, y_cal2, x_110, y_cal2, color=MUTED, sw=1, dash="4 3"))
    P.append(text(ox - 10, y_cal2 + 4, "TS_CAL2 (≈1380)", size=10, bold=True, anchor="end"))

    # Лінія ідеального заводського калібрування
    x_start = ox + 60
    y_start = y_cal1 - (y_cal2 - y_cal1) * (x_30 - x_start) / (x_110 - x_30)
    x_end = ox + 560
    y_end = y_cal2 + (y_cal2 - y_cal1) * (x_end - x_110) / (x_110 - x_30)

    P.append(line(x_start, y_start, x_end, y_end, color=POS, sw=2.5))

    # Маркери точок
    P.append(circle(x_30, y_cal1, 6, fill=POS, stroke=LINE, sw=1.5))
    P.append(circle(x_110, y_cal2, 6, fill=POS, stroke=LINE, sw=1.5))

    # Виміряна точка Tx
    x_meas = ox + 320
    y_meas = y_cal1 + (y_cal2 - y_cal1) * (x_meas - x_30) / (x_110 - x_30)
    P.append(circle(x_meas, y_meas, 7, fill=FIELD, stroke=LINE, sw=2))
    P.append(line(x_meas, oy, x_meas, y_meas, color=FIELD, sw=1.5, dash="3 3"))
    P.append(line(ox, y_meas, x_meas, y_meas, color=FIELD, sw=1.5, dash="3 3"))
    P.append(text(x_meas, oy + 20, "T_поточна", size=11, bold=True, color=FIELD))
    P.append(text(ox - 10, y_meas + 4, "TS_DATA_norm", size=10, bold=True, color=FIELD, anchor="end"))

    # Пояснення формули інтерполяції
    P.append(rect(470, 70, 310, 110, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    P.append(text(625, 94, "Формула лінійної інтерполяції:", size=12, bold=True))
    P.append(text(625, 120, "T = (110 - 30) × (TS_norm - CAL1)", size=11, color=POS, bold=True))
    P.append(text(625, 140, "     ────────────────────────  + 30 °C", size=11, color=POS, bold=True))
    P.append(text(625, 162, "          (CAL2 - CAL1)", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "temperature-calibration.svg"), W, H, *P)


# ── Фігура 4: RC-заряд ємності вибірки та час семплювання ────────────────────
def fig_sampling_time_rc():
    W, H = 820, 430
    P = [text(W / 2, 26, "Вплив внутрішнього опору джерела на час вибірки АЦП (Sample Time)", size=16, bold=True)]

    # Еквівалентна схема вгорі
    P.append(rect(50, 52, 720, 100, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    P.append(text(120, 75, "Джерело сигналу", size=11, bold=True))
    P.append(rect(70, 92, 100, 42, fill="#eaf0fd", stroke=NEG, sw=1.2))
    P.append(text(120, 110, "R_source", size=11, bold=True))
    P.append(text(120, 125, "(10..100 кОм)", size=9, color=MUTED))

    P.append(line(170, 113, 230, 113, color=LINE, sw=1.5))

    P.append(text(290, 75, "Ключ вибірки MCU", size=11, bold=True))
    P.append(rect(240, 92, 100, 42, fill="#ffffff", stroke=LINE, sw=1.2))
    P.append(text(290, 110, "R_switch", size=11, bold=True))
    P.append(text(290, 125, "(≈ 1..3 кОм)", size=9, color=MUTED))

    P.append(line(340, 113, 440, 113, color=LINE, sw=1.5))
    P.append(line(440, 113, 440, 92, color=LINE, sw=1.5))

    # Ємність вибірки C_sample
    P.append(rect(415, 92, 50, 42, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    P.append(text(440, 110, "C_S", size=11, bold=True, color=FIELD))
    P.append(text(440, 125, "5 пФ", size=9, color=FIELD))

    P.append(line(440, 134, 440, 144, color=LINE, sw=1.5))
    P.append(text(440, 148, "GND", size=9, color=MUTED))

    P.append(arrow(440, 113, 530, 113, color=LINE, sw=1.5))
    P.append(text(625, 105, "Постійна часу τ = (R_src + R_sw) × C_S", size=11, bold=True))
    P.append(text(625, 125, "Для похибки < 0.5 LSB: t_sample ≥ 9 × τ", size=11, color=NEG, bold=True))

    # Графік заряду внизу
    ox, oy = 100, 390
    gw, gh = 660, 200

    P.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    P.append(text(ox + gw - 30, oy + 25, "Час вибірки t_sample (мкс)", size=11, bold=True))

    P.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    P.append(text(ox - 10, oy - gh + 15, "Напруга на конденсаторі C_S (% Vin)", size=11, bold=True, anchor="end"))

    # Рівень 100% (Vin) та поріг 0.5 LSB (99.98%)
    P.append(line(ox, oy - 160, ox + gw - 40, oy - 160, color=LINE, sw=1, dash="4 3"))
    P.append(text(ox - 10, oy - 156, "100% Vin", size=10, color=MUTED, anchor="end"))

    # Крива 1: Низькоомне зовнішнє джерело (R_src = 1 кОм, tau ≈ 20 нс) - швидкий заряд (зелений)
    pts_fast = []
    x = 0
    while x <= 180:
        t = x / 30.0 # tau = 1
        v = 1.0 - math.exp(-t * 2.5)
        y = oy - v * 160
        pts_fast.append((ox + x, y))
        x += 5
    for i in range(1, len(pts_fast)):
        P.append(line(pts_fast[i - 1][0], pts_fast[i - 1][1], pts_fast[i][0], pts_fast[i][1], color=FIELD, sw=2.5))
    P.append(text(ox + 190, oy - 150, "Зовнішнє джерело (Rsrc = 1 кОм, t_s ≈ 0.5 мкс)", size=10, bold=True, color=FIELD, anchor="start"))

    # Крива 2: Високоомне внутрішнє джерело VREFINT/TS (R_src = 50 кОм, tau ≈ 250 нс) - повільний заряд (червоний)
    pts_slow = []
    x = 0
    while x <= 520:
        t = x / 60.0 # повільніший
        v = 1.0 - math.exp(-t * 0.55)
        y = oy - v * 160
        pts_slow.append((ox + x, y))
        x += 8
    for i in range(1, len(pts_slow)):
        P.append(line(pts_slow[i - 1][0], pts_slow[i - 1][1], pts_slow[i][0], pts_slow[i][1], color=POS, sw=2.5))

    # Зона недостатнього часу вибірки (помилка вимірювання)
    P.append(rect(ox + 20, oy - 150, 100, 140, fill="#fdecea", stroke=POS, sw=1, rx=0))
    P.append(mtext(ox + 70, oy - 80, ["Короткий t_sample:", "Недозаряд C_S!", "Похибка до 10%"], size=10, color=POS, bold=True))

    P.append(line(ox + 420, oy, ox + 420, oy - 160, color=FIELD, sw=1.5, dash="4 2"))
    P.append(text(ox + 420, oy + 20, "t_sample_min (≥ 5..10 мкс)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "sampling-time-rc.svg"), W, H, *P)


if __name__ == "__main__":
    fig_internal_sources_mux()
    fig_vrefint_ratiometric()
    fig_temperature_calibration()
    fig_sampling_time_rc()
    print("Всі фігури успішно згенеровано.")
