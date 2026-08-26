# -*- coding: utf-8 -*-
"""Фігури теми «Перший давач від нуля до числа»
(root/course/embedded/pershyi-davach-vid-nulia-do-chysla).
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle,
                    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. i2c-sensor-schematic.svg ─────────────────────────────────────────────
def fig_i2c_sensor_schematic():
    W, H = 740, 290
    parts = []

    # Блок МК (ліворуч)
    mcu_x, mcu_y, mcu_w, mcu_h = 24, 40, 160, 210
    parts.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(mcu_x + mcu_w / 2, mcu_y + 24, "Мікроконтролер", size=13, color=INK, bold=True))
    parts.append(text(mcu_x + mcu_w / 2, mcu_y + 40, "(Master, 3.3 В)", size=11, color=MUTED))

    # Виводи МК
    pin_y_vcc = mcu_y + 65
    pin_y_scl = mcu_y + 105
    pin_y_sda = mcu_y + 145
    pin_y_gnd = mcu_y + 185

    parts.append(text(mcu_x + mcu_w - 12, pin_y_vcc + 4, "3V3", size=11, color=POS, anchor="end", bold=True))
    parts.append(text(mcu_x + mcu_w - 12, pin_y_scl + 4, "SCL", size=11, color=INK, anchor="end", bold=True))
    parts.append(text(mcu_x + mcu_w - 12, pin_y_sda + 4, "SDA", size=11, color=INK, anchor="end", bold=True))
    parts.append(text(mcu_x + mcu_w - 12, pin_y_gnd + 4, "GND", size=11, color=NEG, anchor="end", bold=True))

    # Блок Сенсора (праворуч)
    sns_x, sns_y, sns_w, sns_h = 520, 40, 196, 210
    parts.append(rect(sns_x, sns_y, sns_w, sns_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(sns_x + sns_w / 2, sns_y + 24, "Сенсор SHT3x", size=13, color=INK, bold=True))
    parts.append(text(sns_x + sns_w / 2, sns_y + 40, "(I2C Slave, 0x44)", size=11, color=FIELD, bold=True))

    # Виводи сенсора
    parts.append(text(sns_x + 12, pin_y_vcc + 4, "VDD", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(sns_x + 12, pin_y_scl + 4, "SCL", size=11, color=INK, anchor="start", bold=True))
    parts.append(text(sns_x + 12, pin_y_sda + 4, "SDA", size=11, color=INK, anchor="start", bold=True))
    parts.append(text(sns_x + 12, pin_y_gnd + 4, "VSS / GND", size=11, color=NEG, anchor="start", bold=True))
    parts.append(text(sns_x + sns_w - 12, pin_y_sda + 4, "ADDR (GND)", size=10, color=MUTED, anchor="end"))
    parts.append(text(sns_x + sns_w - 12, pin_y_gnd + 4, "RESET (3V3)", size=10, color=MUTED, anchor="end"))

    # Шина живлення 3.3V
    parts.append(line(mcu_x + mcu_w, pin_y_vcc, sns_x, pin_y_vcc, color=POS, sw=1.8))
    # Шина Землі GND
    parts.append(line(mcu_x + mcu_w, pin_y_gnd, sns_x, pin_y_gnd, color=NEG, sw=1.8))

    # Сигнальні лінії SCL та SDA
    parts.append(line(mcu_x + mcu_w, pin_y_scl, sns_x, pin_y_scl, color=INK, sw=1.5))
    parts.append(line(mcu_x + mcu_w, pin_y_sda, sns_x, pin_y_sda, color=INK, sw=1.5))

    # Підтяжки (Pull-up resistors) на шині I2C
    r1_x, r2_x = 260, 320
    # З'єднання з VDD
    parts.append(line(r1_x, pin_y_vcc, r1_x, pin_y_scl - 18, color=POS, sw=1.2))
    parts.append(circle(r1_x, pin_y_vcc, 3, fill=POS, stroke="none"))
    parts.append(rect(r1_x - 10, pin_y_scl - 18, 20, 14, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    parts.append(text(r1_x, pin_y_scl - 22, "R_p 4.7k", size=10, color=INK))
    parts.append(line(r1_x, pin_y_scl - 4, r1_x, pin_y_scl, color=INK, sw=1.2))
    parts.append(circle(r1_x, pin_y_scl, 3, fill=INK, stroke="none"))

    parts.append(line(r2_x, pin_y_vcc, r2_x, pin_y_sda - 18, color=POS, sw=1.2))
    parts.append(circle(r2_x, pin_y_vcc, 3, fill=POS, stroke="none"))
    parts.append(rect(r2_x - 10, pin_y_sda - 18, 20, 14, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    parts.append(text(r2_x, pin_y_sda - 22, "R_p 4.7k", size=10, color=INK))
    parts.append(line(r2_x, pin_y_sda - 4, r2_x, pin_y_sda, color=INK, sw=1.2))
    parts.append(circle(r2_x, pin_y_sda, 3, fill=INK, stroke="none"))

    # Блокувальний конденсатор 100 нФ біля сенсора
    c_x = 470
    parts.append(line(c_x, pin_y_vcc, c_x, pin_y_vcc + 38, color=POS, sw=1.2))
    parts.append(circle(c_x, pin_y_vcc, 3, fill=POS, stroke="none"))
    # Обкладки конденсатора
    parts.append(line(c_x - 12, pin_y_vcc + 38, c_x + 12, pin_y_vcc + 38, color=LINE, sw=1.8))
    parts.append(line(c_x - 12, pin_y_vcc + 44, c_x + 12, pin_y_vcc + 44, color=LINE, sw=1.8))
    parts.append(line(c_x, pin_y_vcc + 44, c_x, pin_y_gnd, color=NEG, sw=1.2))
    parts.append(circle(c_x, pin_y_gnd, 3, fill=NEG, stroke="none"))
    parts.append(text(c_x + 18, pin_y_vcc + 42, "C_dec 100 нФ", size=10, color=FIELD, anchor="start", bold=True))
    parts.append(text(c_x + 18, pin_y_vcc + 56, "(MLCC X7R)", size=9, color=MUTED, anchor="start"))

    # З'єднання ADDR та RESET всередині сенсора
    parts.append(line(sns_x + sns_w - 60, pin_y_sda, sns_x + sns_w - 20, pin_y_sda, color=MUTED, sw=1))
    parts.append(line(sns_x + sns_w - 60, pin_y_gnd, sns_x + sns_w - 20, pin_y_gnd, color=MUTED, sw=1))

    # Пояснення знизу
    parts.append(rect(130, 258, 480, 24, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    parts.append(text(370, 274, "Підтяжки R_p задають фронти I2C; ємність C_dec гасить стрибки струму АЦП", size=10, color=INK))

    render(out("i2c-sensor-schematic.svg"), W, H, *parts)


# ── 2. i2c-transaction-frame.svg ────────────────────────────────────────────
def fig_i2c_transaction_frame():
    W, H = 760, 290
    parts = []

    # Заголовок блоку 1: Запис команди запуску перетворення
    parts.append(text(20, 24, "1. Запуск вимірювання (Write Command: High Repeatability)", size=12, color=INK, anchor="start", bold=True))

    y1 = 38
    blocks_w = [
        ("S", 34, "#e2e8f0", INK, "START"),
        ("0x44 + W (0x88)", 130, "#dbeafe", NEG, "Адреса + Запис"),
        ("A", 32, "#dcfce7", FIELD, "ACK"),
        ("CMD MSB (0x24)", 116, "#fef3c7", "#92400e", "Команда ст."),
        ("A", 32, "#dcfce7", FIELD, "ACK"),
        ("CMD LSB (0x00)", 116, "#fef3c7", "#92400e", "Команда мол."),
        ("A", 32, "#dcfce7", FIELD, "ACK"),
        ("P", 34, "#e2e8f0", INK, "STOP")
    ]

    cur_x = 20
    for label, bw, bg_col, txt_col, desc in blocks_w:
        parts.append(rect(cur_x, y1, bw, 32, fill=bg_col, stroke=LINE, sw=1.2, rx=3))
        parts.append(text(cur_x + bw / 2, y1 + 18, label, size=11, color=txt_col, bold=True))
        parts.append(text(cur_x + bw / 2, y1 + 44, desc, size=9, color=MUTED))
        cur_x += bw + 3

    # Блок паузи перетворення t_meas
    y_gap = 100
    parts.append(rect(20, y_gap, W - 40, 24, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(W / 2, y_gap + 16, "Пауза перетворення t_meas = 15 мс (сенсор вимірює T і RH, шина вільна)", size=11, color="#334155", bold=True))

    # Заголовок блоку 2: Зчитування результатів і CRC
    parts.append(text(20, 148, "2. Зчитування 6 байтів результату з двома сумами CRC-8", size=12, color=INK, anchor="start", bold=True))

    y2 = 162
    blocks_r = [
        ("S", 28, "#e2e8f0", INK),
        ("0x44 + R", 74, "#dbeafe", NEG),
        ("A", 26, "#dcfce7", FIELD),
        ("T_MSB", 62, "#fee2e2", POS),
        ("A", 26, "#dcfce7", FIELD),
        ("T_LSB", 62, "#fee2e2", POS),
        ("A", 26, "#dcfce7", FIELD),
        ("CRC_T", 58, "#fef08a", "#854d0e"),
        ("A", 26, "#dcfce7", FIELD),
        ("RH_MSB", 66, "#e0f2fe", NEG),
        ("A", 26, "#dcfce7", FIELD),
        ("RH_LSB", 66, "#e0f2fe", NEG),
        ("A", 26, "#dcfce7", FIELD),
        ("CRC_RH", 62, "#fef08a", "#854d0e"),
        ("N", 26, "#fee2e2", POS),
        ("P", 28, "#e2e8f0", INK)
    ]

    cur_x = 20
    for label, bw, bg_col, txt_col in blocks_r:
        parts.append(rect(cur_x, y2, bw, 32, fill=bg_col, stroke=LINE, sw=1.2, rx=3))
        parts.append(text(cur_x + bw / 2, y2 + 18, label, size=10, color=txt_col, bold=True))
        cur_x += bw + 2

    # Підписи блоків даних знизу
    parts.append(rect(154, y2 + 38, 204, 18, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    parts.append(text(256, y2 + 51, "Температура: 16 біт + CRC8", size=9, color=POS, bold=True))

    parts.append(rect(414, y2 + 38, 214, 18, fill="#e0f2fe", stroke=NEG, sw=1, rx=3))
    parts.append(text(521, y2 + 51, "Відносна вологість: 16 біт + CRC8", size=9, color=NEG, bold=True))

    # Виноска валідації
    parts.append(rect(20, 246, W - 40, 28, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    parts.append(text(W / 2, 264, "МК перевіряє CRC окремо для кожного параметра: невідповідність суми відкидає вимірювання", size=10, color=INK))

    render(out("i2c-transaction-frame.svg"), W, H, *parts)


# ── 3. crc8-hardware-lfsr.svg ───────────────────────────────────────────────
def fig_crc8_hardware_lfsr():
    W, H = 740, 240
    parts = []

    parts.append(text(W / 2, 22, "Апаратний автомат CRC-8 Sensirion (поліном 0x31: x^8 + x^5 + x^4 + 1)", size=13, color=INK, bold=True))

    # Схема зсувного регістра: комірки b7, b6, b5, b4, b3, b2, b1, b0
    cell_w, cell_h = 44, 38
    y_reg = 80
    xs = [60 + i * 72 for i in range(8)]  # b7 .. b0 зліва направо

    # Вхідний потік бітів
    in_x = 24
    parts.append(text(in_x, y_reg + 20, "Data In", size=11, color=POS, anchor="start", bold=True))
    parts.append(arrow(in_x + 48, y_reg + 18, xs[0] - 22, y_reg + 18, color=POS, sw=1.5))

    # Перший XOR між вхідним бітом і MSB (b7 out)
    xor0_x = xs[0] - 14
    parts.append(circle(xor0_x, y_reg + 18, 8, fill="#ffffff", stroke=LINE, sw=1.4))
    parts.append(text(xor0_x, y_reg + 22, "⊕", size=13, color=LINE, bold=True))

    # Лінія зворотного зв'язку Feedback від b7
    fb_y = 160
    parts.append(line(xs[0] + cell_w / 2, y_reg + cell_h, xs[0] + cell_w / 2, fb_y, color=NEG, sw=1.5))
    parts.append(line(xs[0] + cell_w / 2, fb_y, xor0_x, fb_y, color=NEG, sw=1.5))
    parts.append(arrow(xor0_x, fb_y, xor0_x, y_reg + 26, color=NEG, sw=1.5))
    parts.append(text(280, fb_y + 16, "Лінія зворотного зв'язку (Feedback = b7 ⊕ Data_Bit)", size=10, color=NEG, bold=True))

    # Комірки регістра
    for idx, x in enumerate(xs):
        bit_num = 7 - idx
        parts.append(rect(x, y_reg, cell_w, cell_h, fill="#f1f5f9", stroke=LINE, sw=1.4, rx=4))
        parts.append(text(x + cell_w / 2, y_reg + 16, "b%d" % bit_num, size=11, color=INK, bold=True))
        parts.append(text(x + cell_w / 2, y_reg + 30, "D-FF", size=9, color=MUTED))

    # Зв'язки між комірками
    parts.append(arrow(xor0_x + 8, y_reg + 18, xs[0], y_reg + 18, color=LINE, sw=1.4))

    # Taps полінома: x^5 (між b5 і b4), x^4 (між b4 і b3)
    for idx in range(7):
        x_from = xs[idx] + cell_w
        x_to = xs[idx + 1]
        mid_x = (x_from + x_to) / 2
        bit_curr = 7 - idx

        if bit_curr in (5, 4):  # Taps для x^5 та x^4
            parts.append(circle(mid_x, y_reg + 18, 7, fill="#fef08a", stroke="#854d0e", sw=1.2))
            parts.append(text(mid_x, y_reg + 22, "⊕", size=11, color="#854d0e", bold=True))
            parts.append(line(x_from, y_reg + 18, mid_x - 7, y_reg + 18, color=LINE, sw=1.3))
            parts.append(arrow(mid_x + 7, y_reg + 18, x_to, y_reg + 18, color=LINE, sw=1.3))
            # Відгалуження від feedback лінії до XOR
            parts.append(line(mid_x, fb_y, mid_x, y_reg + 25, color=NEG, sw=1.2))
            parts.append(circle(mid_x, fb_y, 2.5, fill=NEG, stroke="none"))
        else:
            parts.append(arrow(x_from, y_reg + 18, x_to, y_reg + 18, color=LINE, sw=1.3))

    # Пояснення знизу
    parts.append(rect(20, 196, W - 40, 28, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    parts.append(text(W / 2, 214, "Ініціалізація: 0xFF. При кожному такті біт зсувається, а при feedback=1 додається маска 0x31", size=10, color=INK))

    render(out("crc8-hardware-lfsr.svg"), W, H, *parts)


# ── 4. sensor-dynamics-response.svg ─────────────────────────────────────────
def fig_sensor_dynamics_response():
    W, H = 740, 260
    parts = []

    # Ліва панель: Динамічний відгук на подих
    p1_x, p1_y, p1_w, p1_h = 20, 20, 335, 220
    parts.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(p1_x + p1_w / 2, p1_y + 20, "1. Динаміка відгуку на подих (Breath Test)", size=11, color=INK, bold=True))

    # Осі графіка
    ax1_x, ax1_y, ax1_w, ax1_h = p1_x + 36, p1_y + 40, 270, 130
    parts.append(line(ax1_x, ax1_y + ax1_h, ax1_x + ax1_w, ax1_y + ax1_h, color=LINE, sw=1.2))
    parts.append(line(ax1_x, ax1_y, ax1_x, ax1_y + ax1_h, color=LINE, sw=1.2))
    parts.append(text(ax1_x + ax1_w, ax1_y + ax1_h + 14, "Час t (с)", size=9, color=MUTED, anchor="end"))
    parts.append(text(ax1_x - 4, ax1_y + 10, "RH %", size=9, color=NEG, anchor="end", bold=True))

    # Крива вологості: стрибок від 45% до 88%, потім спад
    path_rh = "M %d %d Q %d %d %d %d Q %d %d %d %d" % (
        ax1_x, ax1_y + 80,
        ax1_x + 40, ax1_y + 10,
        ax1_x + 70, ax1_y + 15,
        ax1_x + 160, ax1_y + 70,
        ax1_x + ax1_w, ax1_y + 78
    )
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_rh, NEG))
    parts.append(text(ax1_x + 70, ax1_y + 32, "RH: 88% (стрибок)", size=9, color=NEG, bold=True))

    # Крива температури: повільніший стрибок на 1.5 градуса
    path_t = "M %d %d Q %d %d %d %d Q %d %d %d %d" % (
        ax1_x, ax1_y + 110,
        ax1_x + 60, ax1_y + 90,
        ax1_x + 100, ax1_y + 88,
        ax1_x + 180, ax1_y + 105,
        ax1_x + ax1_w, ax1_y + 110
    )
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' % (path_t, POS))
    parts.append(text(ax1_x + 110, ax1_y + 100, "T: +1.5 °C (інерція)", size=9, color=POS))

    parts.append(text(p1_x + p1_w / 2, p1_y + p1_h - 12, "Вологість реагує миттєво (τ ~ 2 с), температура інерційна", size=9, color=MUTED))

    # Права панель: Самонагрів кристала через високу частоту опитування
    p2_x, p2_y, p2_w, p2_h = 375, 20, 345, 220
    parts.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(p2_x + p2_w / 2, p2_y + 20, "2. Помилка самонагріву (Self-Heating Effect)", size=11, color=INK, bold=True))

    # Стовпчики порівняння: 1 вимір/хв vs 100 вимірів/с
    col1_x, col2_x = p2_x + 60, p2_x + 200
    base_y = p2_y + 170

    # 1 вимір на секунду (норма)
    parts.append(rect(col1_x, base_y - 70, 50, 70, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    parts.append(text(col1_x + 25, base_y - 78, "24.0 °C", size=10, color=FIELD, bold=True))
    parts.append(mtext(col1_x + 25, base_y + 14, ["1 вимір/с", "I_avg ≈ 1 мкА"], size=9, color=MUTED))

    # 100 вимірів на секунду (самонагрів кристала)
    parts.append(rect(col2_x, base_y - 110, 50, 110, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    parts.append(text(col2_x + 25, base_y - 118, "25.8 °C (+1.8 °C)", size=10, color=POS, bold=True))
    parts.append(mtext(col2_x + 25, base_y + 14, ["100 вимірів/с", "I_avg ≈ 800 мкА"], size=9, color=MUTED))

    # Різниця RH
    parts.append(rect(p2_x + 20, p2_y + 42, p2_w - 40, 26, fill="#fff7ed", stroke="#fdba74", sw=1, rx=4))
    parts.append(text(p2_x + p2_w / 2, p2_y + 58, "Самонагрів на +1.8 °C занижує виміряну вологість на ~5.2% RH!", size=9, color="#9a3412", bold=True))

    render(out("sensor-dynamics-response.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_i2c_sensor_schematic()
    fig_i2c_transaction_frame()
    fig_crc8_hardware_lfsr()
    fig_sensor_dynamics_response()
    print("All figures generated successfully.")
