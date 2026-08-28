# -*- coding: utf-8 -*-
"""Фігури до теми «Карта пінів: розподіл функцій до першої лінії схеми» (root/hw/hw-pcb/karta-piniv).
Дві фігури:
  af-multiplexing-matrix.svg  — внутрішня структура GPIO-паду та мультиплексора альтернативних функцій (AF0..AF15)
  pinout-pcb-allocation.svg   — топологічний розподіл функціональних груп пінів по периметру чіпа для оптимізації трасування на платі
Запуск: python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. af-multiplexing-matrix.svg — Внутрішня апаратна структура виводу GPIO
# ════════════════════════════════════════════════════════════════════════════
def fig_af_multiplexing_matrix():
    W, H = 840, 520
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 28, "Внутрішня структура виводу GPIO та селектора функцій мікроконтролера", size=16, bold=True))

    # Ліва колонка — джерела периферії (AF0..AF15) та системні регістри
    col_periph_x, col_periph_w = 40, 160
    f.append(rect(col_periph_x, 60, col_periph_w, 420, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(col_periph_x + col_periph_w / 2, 82, "Периферія та шини", size=13, bold=True, color=INK))

    periph_blocks = [
        (115, "AF0: SYSTEM (SWD/JTAG)", "#eef2fb", NEG),
        (175, "AF1..AF3: TIM1..TIM8 PWM", "#fdf0ea", POS),
        (235, "AF4..AF6: I2C1..3 / SPI1..3", "#eef7f0", FIELD),
        (295, "AF7..AF9: USART1..6 / CAN", "#fef9c3", "#854d0e"),
        (355, "GPIO_ODR / GPIO_IDR", "#f1f5f9", LINE),
        (415, "Аналоговий комутатор ADC", "#fce7f3", "#9d174d"),
    ]

    for py, ptxt, pfill, pstroke in periph_blocks:
        f.append(rect(col_periph_x + 10, py - 18, col_periph_w - 20, 36, fill=pfill, stroke=pstroke, sw=1.4, rx=6))
        f.append(text(col_periph_x + col_periph_w / 2, py + 5, ptxt, size=10, bold=True, color=pstroke))

    # Центральна секція — Мультиплексор альтернативних функцій (AF MUX)
    mux_x, mux_w = 260, 150
    f.append(rect(mux_x, 90, mux_w, 240, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=10))
    f.append(text(mux_x + mux_w / 2, 115, "Селектор AF MUX", size=14, bold=True, color=FIELD))
    f.append(text(mux_x + mux_w / 2, 135, "16-входовий комутатор", size=11, color=MUTED))

    # Лінії керування від регістрів AFR[0] / AFR[1]
    afr_box, _, _ = textbox(mux_x + mux_w / 2, 175, "Регістр AFR[x]\n(4 біти: AF0..AF15)", size=10, pad=6, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD)
    f.append(afr_box)

    f.append(text(mux_x + mux_w / 2, 235, "MODER[2y+1:2y]", size=11, bold=True, color=INK))
    f.append(mtext(mux_x + mux_w / 2, 255, ["00: Input | 01: Output", "10: AF    | 11: Analog"], size=9, color=MUTED))

    # З'єднувальні стрілки від периферії до MUX
    f.append(arrow(col_periph_x + col_periph_w, 115, mux_x, 130, color=NEG, sw=1.5))
    f.append(arrow(col_periph_x + col_periph_w, 175, mux_x, 160, color=POS, sw=1.5))
    f.append(arrow(col_periph_x + col_periph_w, 235, mux_x, 190, color=FIELD, sw=1.5))
    f.append(arrow(col_periph_x + col_periph_w, 295, mux_x, 220, color="#854d0e", sw=1.5))
    f.append(arrow(col_periph_x + col_periph_w, 355, mux_x, 250, color=LINE, sw=1.5))

    # Секція вихідного каскаду та схеми керування піном (Pad Logic)
    pad_x, pad_w = 470, 200
    f.append(rect(pad_x, 60, pad_w, 420, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    f.append(text(pad_x + pad_w / 2, 82, "Вихідний/вхідний драйвер паду", size=13, bold=True, color=INK))

    # Вихідний драйвер: Push-Pull / Open-Drain FETs
    f.append(rect(pad_x + 15, 105, pad_w - 30, 80, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    f.append(text(pad_x + pad_w / 2, 125, "Вихідні ключі (FETs)", size=11, bold=True, color=INK))
    f.append(mtext(pad_x + pad_w / 2, 145, ["P-MOS (VDD) / N-MOS (VSS)", "Режими: Push-Pull / Open-Drain", "Керування: OTYPER + OSPEEDR"], size=9, color=MUTED))

    # Підтягувальні резистори: Pull-up / Pull-down
    f.append(rect(pad_x + 15, 195, pad_w - 30, 60, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    f.append(text(pad_x + pad_w / 2, 215, "Підтяжка: PUPDR", size=11, bold=True, color=INK))
    f.append(mtext(pad_x + pad_w / 2, 235, ["R_PU ≈ 40 кОм до VDD", "R_PD ≈ 40 кОм до VSS"], size=9, color=MUTED))

    # Вхідний каскад: тригер Шмітта
    f.append(rect(pad_x + 15, 265, pad_w - 30, 60, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    f.append(text(pad_x + pad_w / 2, 285, "Вхід: Тригер Шмітта", size=11, bold=True, color=INK))
    f.append(mtext(pad_x + pad_w / 2, 305, ["Гістерезис для захисту від шуму", "Читання в регістр IDR"], size=9, color=MUTED))

    # ESD захист (діоди до VDD та VSS)
    f.append(rect(pad_x + 15, 335, pad_w - 30, 60, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    f.append(text(pad_x + pad_w / 2, 355, "Захисні ESD діоди", size=11, bold=True, color=POS))
    f.append(mtext(pad_x + pad_w / 2, 375, ["Клампінг до VDD/VDDA та VSS", "5V-tolerant (FT) vs 3.3V (TT)"], size=9, color=MUTED))

    # Аналоговий вхід (обхід цифрового буфера)
    f.append(rect(pad_x + 15, 405, pad_w - 30, 60, fill="#fdf2f8", stroke="#9d174d", sw=1.4, rx=6))
    f.append(text(pad_x + pad_w / 2, 425, "Аналоговий тракт (ADC/DAC)", size=11, bold=True, color="#9d174d"))
    f.append(mtext(pad_x + pad_w / 2, 445, ["Відключення тригера Шмітта", "Прямий канал до вхідного MUX ADC"], size=9, color=MUTED))

    # Стрілка від AF MUX до драйверів
    f.append(arrow(mux_x + mux_w, 200, pad_x + 15, 145, color=FIELD, sw=2.0))
    f.append(arrow(pad_x + 15, 295, mux_x + mux_w, 280, color=LINE, sw=1.8))

    # Аналогова лінія в обхід
    f.append(line(col_periph_x + col_periph_w, 415, pad_x + 15, 435, color="#9d174d", sw=2.0, dash="4 4"))

    # Фізичний пін мікроконтролера (справа)
    pin_x = 730
    f.append(rect(pin_x, 210, 80, 70, fill="#fef3c7", stroke="#d97706", sw=2.2, rx=8))
    f.append(text(pin_x + 40, 238, "PIN PAD", size=12, bold=True, color="#b45309"))
    f.append(text(pin_x + 40, 260, "(PX_n)", size=12, bold=True, color=INK))

    # Зв'язок від блоку драйверів до фізичного паду
    f.append(line(pad_x + pad_w - 15, 145, pin_x, 235, color=LINE, sw=2.2))
    f.append(line(pad_x + pad_w - 15, 225, pin_x, 245, color=MUTED, sw=1.5))
    f.append(line(pad_x + pad_w - 15, 295, pin_x, 255, color=LINE, sw=1.8))
    f.append(line(pad_x + pad_w - 15, 435, pin_x, 265, color="#9d174d", sw=2.0, dash="4 4"))

    # Пояснювальний рядок унизу
    f.append(text(W / 2, 502, "Конфігурація MODER, AFR та PUPDR комутує фізичний пін між цифровою периферією, GPIO або АЦП", size=11, color=MUTED))

    render(os.path.join(IMG, "af-multiplexing-matrix.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. pinout-pcb-allocation.svg — Топологічний розподіл пінів по сторонах чіпа
# ════════════════════════════════════════════════════════════════════════════
def fig_pinout_pcb_allocation():
    W, H = 840, 560
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 28, "Топологічний розподіл функцій пінів по периметру MCU та пряме трасування", size=16, bold=True))

    # Центральний мікроконтролер (QFP / QFN корпус)
    mcu_cx, mcu_cy, mcu_s = W / 2, H / 2 + 10, 180
    f.append(rect(mcu_cx - mcu_s / 2, mcu_cy - mcu_s / 2, mcu_s, mcu_s, fill="#1e293b", stroke="#0f172a", sw=2.5, rx=12))
    f.append(text(mcu_cx, mcu_cy - 20, "STM32 / MCU", size=16, bold=True, color="#ffffff"))
    f.append(text(mcu_cx, mcu_cy + 5, "LQFP-64 / QFN-64", size=12, color="#94a3b8"))
    f.append(text(mcu_cx, mcu_cy + 30, "Матриця пінів", size=11, color="#38bdf8"))

    # 4 функціональні сектори навколо чіпа

    # 1. ПІВНІЧ (North): Швидкісна цифрова шина (Шина пам'яті / QSPI / SDIO / SPI Flash)
    mem_box_x, mem_box_y, mem_box_w, mem_box_h = mcu_cx - 130, 60, 260, 65
    f.append(rect(mem_box_x, mem_box_y, mem_box_w, mem_box_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(mcu_cx, mem_box_y + 24, "ШВИДКІСНА ПАМ'ЯТЬ (QSPI Flash / SDIO)", size=11, bold=True, color=NEG))
    f.append(text(mcu_cx, mem_box_y + 46, "Короткі паралельні лінії, узгодження довжин без переходів", size=9, color=MUTED))

    # Доріжки трасування на північ
    for offset_x in [-60, -30, 0, 30, 60]:
        f.append(line(mcu_cx + offset_x, mcu_cy - mcu_s / 2, mcu_cx + offset_x, mem_box_y + mem_box_h, color=NEG, sw=2.0))
    f.append(text(mcu_cx + 85, mcu_cy - mcu_s / 2 - 15, "CLK, IO0..IO3, CS", size=9, color=NEG))

    # 2. СХІД (East): Комунікаційні інтерфейси (CAN, RS-485, USART, Роз'єми)
    comm_box_x, comm_box_y, comm_box_w, comm_box_h = W - 190, mcu_cy - 70, 160, 140
    f.append(rect(comm_box_x, comm_box_y, comm_box_w, comm_box_h, fill="#fefce8", stroke="#ca8a04", sw=1.8, rx=8))
    f.append(text(comm_box_x + comm_box_w / 2, comm_box_y + 25, "ЗОВНІШНІ ІНТЕРФЕЙСИ", size=11, bold=True, color="#854d0e"))
    f.append(mtext(comm_box_x + comm_box_w / 2, comm_box_y + 55, ["Трансивер CAN / RS-485", "USART роз'єм HMI", "Вихід на роз'єм плати"], size=9, color=MUTED))

    # Доріжки трасування на схід
    for offset_y in [-40, -15, 15, 40]:
        f.append(line(mcu_cx + mcu_s / 2, mcu_cy + offset_y, comm_box_x, mcu_cy + offset_y, color="#ca8a04", sw=2.0))
    f.append(text(mcu_cx + mcu_s / 2 + 35, mcu_cy - 50, "TX / RX / CAN", size=9, color="#854d0e"))

    # 3. ПІВДЕНЬ (South): Чутливий аналоговий кластер (АЦП, ЦАП, ОП, датчики, ізольована AGND)
    ana_box_x, ana_box_y, ana_box_w, ana_box_h = mcu_cx - 130, H - 105, 260, 65
    f.append(rect(ana_box_x, ana_box_y, ana_box_w, ana_box_h, fill="#fdf2f8", stroke="#db2777", sw=1.8, rx=8))
    f.append(text(mcu_cx, ana_box_y + 24, "АНАЛОГОВИЙ ОСТРІВ (ADC, VREF+, ОП)", size=11, bold=True, color="#9d174d"))
    f.append(text(mcu_cx, ana_box_y + 46, "Захищений від цифрових завад, чиста земля AGND", size=9, color=MUTED))

    # Доріжки трасування на південь
    for offset_x in [-50, -20, 20, 50]:
        f.append(line(mcu_cx + offset_x, mcu_cy + mcu_s / 2, mcu_cx + offset_x, ana_box_y, color="#db2777", sw=2.0))
    f.append(text(mcu_cx + 85, mcu_cy + mcu_s / 2 + 20, "IN0..IN3, VREF+", size=9, color="#9d174d"))

    # 4. ЗАХІД (West): Живлення, блокувальні конденсатори, кварци (HSE/LSE), SWD
    pwr_box_x, pwr_box_y, pwr_box_w, pwr_box_h = 30, mcu_cy - 85, 170, 170
    f.append(rect(pwr_box_x, pwr_box_y, pwr_box_w, pwr_box_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(pwr_box_x + pwr_box_w / 2, pwr_box_y + 25, "ЖИВЛЕННЯ ТА ТАКТУВАННЯ", size=11, bold=True, color=FIELD))
    f.append(mtext(pwr_box_x + pwr_box_w / 2, pwr_box_y + 55, ["Кварц HSE (8-25 МГц)", "Конденсатори C_dec < 3 мм", "Кварц LSE (32.768 кГц)", "SWD (SWCLK / SWDIO)"], size=9, color=MUTED))

    # Доріжки трасування на захід
    for offset_y in [-50, -25, 0, 25, 50]:
        f.append(line(pwr_box_x + pwr_box_w, mcu_cy + offset_y, mcu_cx - mcu_s / 2, mcu_cy + offset_y, color=FIELD, sw=2.0))
    f.append(text(mcu_cx - mcu_s / 2 - 35, mcu_cy - 60, "VDD, OSC, SWD", size=9, color=FIELD))

    # Кутові мітки переваг
    f.append(text(W / 2, H - 20, "Прямий розподіл виводів за сторонами усуває перехрещення шин і мінімізує кількість перехідних отворів", size=11, color=MUTED))

    render(os.path.join(IMG, "pinout-pcb-allocation.svg"), W, H, *f)


if __name__ == '__main__':
    fig_af_multiplexing_matrix()
    fig_pinout_pcb_allocation()
    print("All figures successfully generated in img/")
