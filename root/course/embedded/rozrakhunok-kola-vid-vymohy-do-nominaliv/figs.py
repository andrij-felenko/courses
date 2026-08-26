# -*- coding: utf-8 -*-
"""Фігури до теми «Розрахунок кола від вимоги до номіналів»
(root/course/embedded/rozrakhunok-kola-vid-vymohy-do-nominaliv).
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Логарифмічний розподіл номіналів E12 та перекриття допусків ───────────
def fig_e_series_spacing():
    W, H = 840, 420
    f = [text(W / 2, 26, "Ряд E12: логарифмічний крок і безперервне перекриття смуг допуску (±10%)",
              size=16, bold=True)]

    # Фонова панель
    f.append(rect(16, 46, W - 32, H - 60, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))

    # Вісь декади 10..100 Ом (логарифмічна шкала)
    ox = 60
    oy = 135
    w_axis = 720
    f.append(line(ox, oy, ox + w_axis, oy, color=LINE, sw=2))
    f.append(arrow(ox + w_axis, oy, ox + w_axis + 12, oy, color=LINE, sw=2))
    f.append(text(ox + w_axis + 16, oy + 4, "Ом", size=12, bold=True, anchor="start"))

    # Номінали E12
    e12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82, 100]

    def log_pos(val):
        return ox + (math.log10(val) - 1.0) * w_axis

    # Малюємо смуги допуску ±10% для кожного номіналу
    for i, val in enumerate(e12):
        cx = log_pos(val)
        lo_val = val * 0.90
        hi_val = val * 1.10
        x_lo = log_pos(lo_val)
        x_hi = log_pos(hi_val)
        bw = max(2.0, x_hi - x_lo)

        # Смуга чергується по висоті для наочності
        band_y = oy - 52 if (i % 2 == 0) else oy - 28
        fill_col = "#d5e8d4" if (i % 2 == 0) else "#dae8fc"
        stroke_col = "#27ae60" if (i % 2 == 0) else "#2457d6"

        f.append(rect(x_lo, band_y - 8, bw, 16, fill=fill_col, stroke=stroke_col, sw=1.2, rx=3))
        f.append(line(cx, oy - 4, cx, oy + 4, color=LINE, sw=1.5))
        f.append(text(cx, oy + 18, str(val), size=11, bold=True, color=INK))

        # Дрібний підпис меж для перших двох номіналів як зразок
        if val == 10:
            f.append(text(cx, band_y - 12, "10 ±10% [9.0..11.0]", size=9.5, color=FIELD, bold=True))
        elif val == 12:
            f.append(text(cx, band_y - 12, "12 ±10% [10.8..13.2]", size=9.5, color=NEG, bold=True))

    # Покажчик перекриття між 10 і 12 (лінії та стрілки без блоку, що налізає)
    ov_x1 = log_pos(10.8)
    ov_x2 = log_pos(11.0)
    ov_mid = (ov_x1 + ov_x2) / 2
    f.append(line(ov_mid, oy - 62, ov_mid + 60, oy - 72, color="#b45f06", sw=1.2))
    f.append(text(ov_mid + 65, oy - 70, "Стик смуг: 10.8 .. 11.0 Ом", size=10, bold=True, anchor="start", color="#b45f06"))

    # Нижня частина: порівняння логарифмічного і лінійного рядів
    card_w = 370
    # Картка 1: Лінійна сітка (дефект)
    f.append(rect(36, 210, card_w, 175, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(36 + card_w / 2, 232, "Лінійний крок (наприклад, +10 Ом)", size=13, bold=True, color=POS))
    f.append(text(50, 260, "• Між 10 і 20 Ом: крок становить +100% (величезна діра)", size=11, anchor="start", color=INK))
    f.append(text(50, 285, "• Між 100 і 110 Ом: крок становить +10%", size=11, anchor="start", color=INK))
    f.append(text(50, 310, "• Між 1000 і 1010 Ом: крок становить +1% (надлишкова густота)", size=11, anchor="start", color=INK))
    f.append(text(50, 345, "Висновок: лінійна шкала дає або дірки внизу, або тонни зайвих деталей угорі.", size=10.5, italic=True, anchor="start", color=MUTED))

    # Картка 2: Геометричний ряд Ренара (перевага)
    f.append(rect(434, 210, card_w, 175, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(434 + card_w / 2, 232, "Геометричний ряд IEC 60063 (r = 10^(1/12))", size=13, bold=True, color=FIELD))
    f.append(text(448, 260, "• Сталий відносний крок між усіма сусідами: ~ +21.15%", size=11, anchor="start", color=INK))
    f.append(text(448, 285, "• З допуском ±10% сусідні смуги надійно стикаються", size=11, anchor="start", color=INK))
    f.append(text(448, 310, "• Будь-який розрахунковий опір відхиляється не більше ніж на ±10%", size=11, anchor="start", color=INK))
    f.append(text(448, 345, "Висновок: мінімальна кількість стандартних номіналів накриває весь діапазон.", size=10.5, italic=True, anchor="start", color=MUTED))

    render(os.path.join(IMG, "e-series-spacing.svg"), W, H, *f)


# ── 2. Світлодіодний індикатор та графік зниження потужності ─────────────────
def fig_led_power_derating():
    W, H = 840, 400
    f = [text(W / 2, 26, "Струмообмеження LED і теплове зниження номінальної потужності резистора",
              size=16, bold=True)]

    # Ліва панель: Схема LED
    p1_x, p1_y, p1_w, p1_h = 16, 50, 390, 335
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill=BG, stroke=LINE, sw=1.5, rx=10))
    f.append(text(p1_x + p1_w / 2, p1_y + 24, "Схема струмообмеження", size=13.5, bold=True, color=INK))

    # Схема живлення
    vx = p1_x + 80
    vcc_y = p1_y + 65
    gnd_y = p1_y + 265
    bus_x = p1_x + 195

    f.append(plus(vx, vcc_y, 11))
    f.append(text(vx, vcc_y - 20, "Vcc = 3.3 В", size=11.5, bold=True, color=INK))
    f.append(line(vx + 11, vcc_y, bus_x, vcc_y, color=LINE, sw=2))
    f.append(line(bus_x, vcc_y, bus_x, vcc_y + 25, color=LINE, sw=2))

    # Резистор R
    rx_y = vcc_y + 25
    f.append(rect(bus_x - 14, rx_y, 28, 48, fill="#eef2f7", stroke=LINE, sw=1.8, rx=3))
    f.append(text(bus_x, rx_y + 24, "R", size=13, bold=True, color=FIELD))
    f.append(text(bus_x + 38, rx_y + 16, "270 Ом", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(bus_x + 38, rx_y + 34, "(E24, 5%)", size=10, color=MUTED, anchor="start"))

    # Світлодіод
    led_top = rx_y + 48
    led_mid = led_top + 30
    f.append(line(bus_x, led_top, bus_x, led_mid, color=LINE, sw=2))

    # Трикутник анода діода
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="%s" stroke-width="1.8"/>' %
             (bus_x - 14, led_mid, bus_x + 14, led_mid, bus_x, led_mid + 24, POS))
    # Катодна риска
    f.append(line(bus_x - 14, led_mid + 24, bus_x + 14, led_mid + 24, color=POS, sw=2))
    f.append(text(bus_x + 38, led_mid + 12, "LED (Vf ≈ 2.0 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(bus_x + 38, led_mid + 28, "If = 4.81 мА", size=10.5, color=INK, anchor="start"))

    # Стрілочки світла
    f.append(arrow(bus_x + 16, led_mid + 8, bus_x + 28, led_mid - 4, color=POS, sw=1.5))
    f.append(arrow(bus_x + 16, led_mid + 18, bus_x + 28, led_mid + 6, color=POS, sw=1.5))

    # Дріт до землі
    f.append(line(bus_x, led_mid + 24, bus_x, gnd_y, color=LINE, sw=2))
    f.append(line(bus_x - 14, gnd_y, bus_x + 14, gnd_y, color=LINE, sw=2.2))
    f.append(line(bus_x - 9, gnd_y + 4, bus_x + 9, gnd_y + 4, color=LINE, sw=1.8))
    f.append(line(bus_x - 4, gnd_y + 8, bus_x + 4, gnd_y + 8, color=LINE, sw=1.4))
    f.append(text(bus_x, gnd_y + 22, "GND (0 В)", size=10.5, color=MUTED))

    # Блок теплового розрахунку внизу картки
    f.append(rect(p1_x + 14, p1_y + 250, p1_w - 28, 70, fill="#f8f9fa", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p1_x + 24, p1_y + 270, "P_calc = (3.3 - 2.0)^2 / 270 = 6.25 мВт", size=11, bold=True, anchor="start", color=INK))
    f.append(text(p1_x + 24, p1_y + 292, "Корпус 0603 (100 мВт) або 0805 (125 мВт)", size=10.5, anchor="start", color=FIELD))
    f.append(text(p1_x + 24, p1_y + 308, "Коефіцієнт навантаження: 6.25 мВт / 100 мВт = 6.25% (холодний)", size=10, italic=True, anchor="start", color=MUTED))

    # Права панель: Крива Derating
    p2_x, p2_y, p2_w, p2_h = 434, 50, 390, 335
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill=BG, stroke=LINE, sw=1.5, rx=10))
    f.append(text(p2_x + p2_w / 2, p2_y + 24, "Крива зниження номінальної потужності (Derating)", size=13, bold=True, color=INK))

    # Графік Derating
    gx0 = p2_x + 55
    gy0 = p2_y + 220
    gw = 290
    gh = 140

    # Осі
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(arrow(gx0 + gw, gy0, gx0 + gw + 12, gy0, color=LINE, sw=1.8))
    f.append(text(gx0 + gw + 16, gy0 + 4, "T (°C)", size=11, bold=True, anchor="start"))

    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.8))
    f.append(arrow(gx0, gy0 - gh, gx0, gy0 - gh - 12, color=LINE, sw=1.8))
    f.append(text(gx0 - 10, gy0 - gh - 6, "P / P_ном (%)", size=11, bold=True, anchor="end"))

    # Позначки шкали
    x_70 = gx0 + 140
    x_155 = gx0 + 260
    y_100 = gy0 - gh + 20
    y_50 = gy0 - gh / 2 + 10

    f.append(line(gx0 - 4, y_100, gx0, y_100, color=LINE, sw=1.5))
    f.append(text(gx0 - 8, y_100 + 4, "100%", size=10, anchor="end", color=MUTED))

    f.append(line(gx0 - 4, y_50, gx0, y_50, color=LINE, sw=1.5))
    f.append(text(gx0 - 8, y_50 + 4, "50%", size=10, anchor="end", color=FIELD, bold=True))

    f.append(line(x_70, gy0, x_70, gy0 + 4, color=LINE, sw=1.5))
    f.append(text(x_70, gy0 + 16, "70°C", size=10, color=INK, bold=True))

    f.append(line(x_155, gy0, x_155, gy0 + 4, color=LINE, sw=1.5))
    f.append(text(x_155, gy0 + 16, "155°C", size=10, color=POS, bold=True))

    # Пунктир 50% запасу
    f.append(line(gx0, y_50, gx0 + gw, y_50, color=FIELD, sw=1.2, dash="4,4"))
    f.append(rect(gx0 + 10, y_50 + 4, 180, 24, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    f.append(text(gx0 + 100, y_50 + 19, "Інженерний запас (Derating 50%)", size=9.5, color=FIELD, bold=True))

    # Ламана лінія derating: (gx0, y_100) -> (x_70, y_100) -> (x_155, gy0)
    f.append(line(gx0, y_100, x_70, y_100, color=POS, sw=2.5))
    f.append(line(x_70, y_100, x_155, gy0, color=POS, sw=2.5))
    f.append(circle(x_70, y_100, 3.5, fill=POS, stroke=POS))
    f.append(circle(x_155, gy0, 3.5, fill=POS, stroke=POS))

    # Текст пояснення
    f.append(rect(p2_x + 14, p2_y + 255, p2_w - 28, 65, fill="#f8f9fa", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p2_x + 24, p2_y + 275, "До 70°C резистор тримає 100% номіналу.", size=10.5, anchor="start", color=INK))
    f.append(text(p2_x + 24, p2_y + 293, "Вище 70°C потужність лінійно спадає до 0 при 155°C.", size=10.5, anchor="start", color=POS))
    f.append(text(p2_x + 24, p2_y + 310, "Практичне правило: P_rated >= 2 * P_calc (коефіцієнт 0.5).", size=10, italic=True, anchor="start", color=FIELD, bold=True))

    render(os.path.join(IMG, "led-power-derating.svg"), W, H, *f)


# ── 3. Резистивний дільник під АЦП та буферний конденсатор ───────────────────
def fig_adc_divider_sampling():
    W, H = 840, 420
    f = [text(W / 2, 26, "Резистивний дільник напруги під вхід АЦП: вплив вихідного опору та буферний конденсатор",
              size=16, bold=True)]

    # Загальна рамка
    f.append(rect(16, 46, W - 32, H - 56, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=10))

    # Схема зліва направо: Дільник -> C_ext -> Ключ і C_sh АЦП
    v_in_x = 60
    div_x = 160
    adc_pin_x = 360
    sw_x = 510
    c_sh_x = 680
    gnd_y = 310
    rail_y = 110

    # Джерело напруги батареї
    f.append(plus(v_in_x, rail_y, 11))
    f.append(text(v_in_x, rail_y - 20, "Vin = 4.2 В", size=11.5, bold=True, color=INK))
    f.append(line(v_in_x + 11, rail_y, div_x, rail_y, color=LINE, sw=2))

    # Верхнє плече R1
    f.append(line(div_x, rail_y, div_x, rail_y + 20, color=LINE, sw=2))
    f.append(rect(div_x - 14, rail_y + 20, 28, 48, fill="#eef2f7", stroke=LINE, sw=1.8, rx=3))
    f.append(text(div_x, rail_y + 44, "R1", size=12, bold=True, color=INK))
    f.append(text(div_x - 22, rail_y + 44, "100 кОм", size=10.5, anchor="end", color=MUTED))

    # Центральний вузол дільника Vout
    node_y = rail_y + 90
    f.append(line(div_x, rail_y + 68, div_x, node_y, color=LINE, sw=2))
    f.append(circle(div_x, node_y, 3.5, fill=INK, stroke=INK))

    # Нижнє плече R2
    f.append(line(div_x, node_y, div_x, node_y + 20, color=LINE, sw=2))
    f.append(rect(div_x - 14, node_y + 20, 28, 48, fill="#eef2f7", stroke=LINE, sw=1.8, rx=3))
    f.append(text(div_x, node_y + 44, "R2", size=12, bold=True, color=INK))
    f.append(text(div_x - 22, node_y + 44, "200 кОм", size=10.5, anchor="end", color=MUTED))
    f.append(line(div_x, node_y + 68, div_x, gnd_y, color=LINE, sw=2))

    # Земля дільника
    f.append(line(div_x - 12, gnd_y, div_x + 12, gnd_y, color=LINE, sw=2))
    f.append(line(div_x - 7, gnd_y + 4, div_x + 7, gnd_y + 4, color=LINE, sw=1.6))
    f.append(line(div_x - 3, gnd_y + 8, div_x + 3, gnd_y + 8, color=LINE, sw=1.2))

    # Тевененівський еквівалент
    f.append(rect(40, 335, 230, 48, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=5))
    f.append(text(155, 353, "R_th = R1 || R2 = 66.7 кОм", size=11, bold=True, color="#b45f06"))
    f.append(text(155, 370, "I_div = 4.2 В / 300 кОм = 14 мкА", size=10, color="#b45f06"))

    # Дріт від дільника до АЦП
    f.append(line(div_x, node_y, adc_pin_x, node_y, color=LINE, sw=2))

    # Зовнішній конденсатор C_ext (паралельно R2)
    c_ext_x = 270
    f.append(circle(c_ext_x, node_y, 3.5, fill=INK, stroke=INK))
    f.append(line(c_ext_x, node_y, c_ext_x, node_y + 25, color=LINE, sw=2))
    # Обкладки C_ext
    f.append(line(c_ext_x - 14, node_y + 25, c_ext_x + 14, node_y + 25, color=FIELD, sw=2.2))
    f.append(line(c_ext_x - 14, node_y + 33, c_ext_x + 14, node_y + 33, color=FIELD, sw=2.2))
    f.append(line(c_ext_x, node_y + 33, c_ext_x, gnd_y, color=LINE, sw=2))
    f.append(circle(c_ext_x, gnd_y, 3.5, fill=INK, stroke=INK))
    f.append(line(div_x, gnd_y, c_ext_x, gnd_y, color=LINE, sw=1.8))
    f.append(text(c_ext_x + 20, node_y + 29, "C_ext = 100 нФ", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(c_ext_x + 20, node_y + 45, "(буфер заряду)", size=9.5, color=MUTED, anchor="start"))

    # Межа мікроконтролера (MCU Boundary)
    mcu_x, mcu_y, mcu_w, mcu_h = adc_pin_x + 40, 75, 410, 290
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f4f7fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(adc_pin_x + 240, 95, "Всередині мікроконтролера (Вхід АЦП)", size=12.5, bold=True, color=NEG))

    # Вхідний пін
    f.append(circle(adc_pin_x, node_y, 5, fill=NEG, stroke=LINE, sw=1.5))
    f.append(text(adc_pin_x, node_y - 12, "ADC_IN", size=11, bold=True, color=INK))

    # Ключ вибірки (Sampling Switch R_sw)
    f.append(line(adc_pin_x, node_y, sw_x - 40, node_y, color=LINE, sw=2))
    # Малюємо перемикач
    f.append(circle(sw_x - 40, node_y, 3, fill=INK, stroke=INK))
    f.append(line(sw_x - 40, node_y, sw_x + 10, node_y - 18, color=POS, sw=2.2))
    f.append(circle(sw_x + 18, node_y, 3, fill=INK, stroke=INK))
    f.append(text(sw_x - 10, node_y - 28, "Ключ вибірки (R_sw ≈ 2 кОм)", size=10.5, bold=True, color=POS))
    f.append(text(sw_x - 10, node_y - 14, "t_sample ≈ 1..5 мкс", size=9.5, color=MUTED))

    # Конденсатор вибірки C_sh
    f.append(line(sw_x + 18, node_y, c_sh_x, node_y, color=LINE, sw=2))
    f.append(circle(c_sh_x, node_y, 3.5, fill=INK, stroke=INK))
    f.append(line(c_sh_x, node_y, c_sh_x, node_y + 25, color=LINE, sw=2))
    # Обкладки C_sh
    f.append(line(c_sh_x - 12, node_y + 25, c_sh_x + 12, node_y + 25, color=NEG, sw=2.2))
    f.append(line(c_sh_x - 12, node_y + 33, c_sh_x + 12, node_y + 33, color=NEG, sw=2.2))
    f.append(line(c_sh_x, node_y + 33, c_sh_x, gnd_y, color=LINE, sw=2))
    f.append(text(c_sh_x + 18, node_y + 29, "C_sh ≈ 10 пФ", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(c_sh_x + 18, node_y + 45, "(ємність Sample&Hold)", size=9.5, color=MUTED, anchor="start"))

    # Земля всередині MCU
    f.append(line(c_sh_x - 10, gnd_y, c_sh_x + 10, gnd_y, color=LINE, sw=2))
    f.append(line(c_sh_x - 6, gnd_y + 4, c_sh_x + 6, gnd_y + 4, color=LINE, sw=1.5))
    f.append(line(c_sh_x - 2, gnd_y + 8, c_sh_x + 2, gnd_y + 8, color=LINE, sw=1))

    # Нижній висновок: чому C_ext рятує ситуацію
    f.append(rect(adc_pin_x + 55, 230, 380, 115, fill="#ffffff", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(adc_pin_x + 65, 252, "Чому C_ext вирішує проблему:", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(adc_pin_x + 65, 272, "1. Без C_ext: tau = (66.7 кОм + 2 кОм) * 10 пФ = 687 нс.", size=10, anchor="start", color=INK))
    f.append(text(adc_pin_x + 65, 290, "   Для 12-біт точності треба 9 * tau ≈ 6.2 мкс (АЦП занижує).", size=10, anchor="start", color=POS))
    f.append(text(adc_pin_x + 65, 310, "2. З C_ext: заряд перетікає з C_ext (100 нФ) у C_sh (10 пФ).", size=10, anchor="start", color=INK))
    f.append(text(adc_pin_x + 65, 328, "   Просідання напруги: 10 пФ / 100 нФ = 0.01% (< 0.5 LSB).", size=10, bold=True, anchor="start", color=FIELD))

    render(os.path.join(IMG, "adc-divider-sampling.svg"), W, H, *f)


# ── 4. Похибки дільника: Worst-Case та RSS аналіз ────────────────────────────
def fig_worst_case_divider():
    W, H = 840, 400
    f = [text(W / 2, 26, "Аналіз найгіршого випадку (WCA) проти статистичного (RSS) для дільника напруги",
              size=16, bold=True)]

    # Загальна фонова панель
    f.append(rect(16, 46, W - 32, H - 56, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))

    # Ліва частина: Графік смуг розкиду
    gx0 = 60
    gy0 = 210
    gw = 360
    gh = 130

    f.append(text(gx0 + gw / 2, 75, "Розподіл вихідної напруги Vout", size=13, bold=True, color=INK))

    # Горизонтальна вісь напруги
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(arrow(gx0 + gw, gy0, gx0 + gw + 12, gy0, color=LINE, sw=1.8))
    f.append(text(gx0 + gw + 16, gy0 + 4, "Vout", size=11, bold=True, anchor="start"))

    cx = gx0 + gw / 2

    # Номінальна лінія V_nom
    f.append(line(cx, gy0 - gh, cx, gy0 + 8, color=FIELD, sw=2, dash="3,3"))
    f.append(text(cx, gy0 + 22, "V_nom (ідеал)", size=10.5, bold=True, color=FIELD))

    # Смуга RSS (3-sigma, ±0.7%)
    rss_w = 70
    f.append(rect(cx - rss_w, gy0 - gh + 20, rss_w * 2, gh - 20, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(cx, gy0 - gh + 36, "Статистична смуга 3σ (RSS)", size=10.5, bold=True, color=FIELD))
    f.append(text(cx, gy0 - gh + 52, "±0.71% (99.7% партії)", size=10, color=FIELD))

    # Межі Worst-Case (WCA, ±1.0%) показані обмежувальними маркерами
    wca_w = 125
    f.append(line(cx - wca_w, gy0 - gh + 60, cx - wca_w, gy0, color=POS, sw=1.8, dash="4,3"))
    f.append(line(cx + wca_w, gy0 - gh + 60, cx + wca_w, gy0, color=POS, sw=1.8, dash="4,3"))
    f.append(line(cx - wca_w, gy0 - gh + 60, cx + wca_w, gy0 - gh + 60, color=POS, sw=1.4))
    f.append(text(cx - wca_w, gy0 + 22, "V_min (WCA)", size=10, bold=True, color=POS))
    f.append(text(cx + wca_w, gy0 + 22, "V_max (WCA)", size=10, bold=True, color=POS))
    f.append(text(cx, gy0 - gh + 72, "Межі WCA (±1.0%)", size=9.5, bold=True, color=POS))

    # Дзвін Гаусса для наочності
    pts = []
    for step in range(-35, 36):
        x = cx + step * (wca_w / 35.0)
        # нормальний розподіл
        y = gy0 - (gh - 15) * math.exp(-0.5 * (step / 11.0) ** 2)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), NEG))
    f.append(text(cx + 80, gy0 - gh + 92, "Гауссів розподіл", size=9.5, color=NEG, italic=True))

    # Нижня плашка під графіком
    f.append(rect(gx0, 255, gw, 110, fill="#f8f9fa", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(gx0 + 10, 275, "Worst-Case (WCA): R1(min) і R2(max)", size=10.5, bold=True, anchor="start", color=POS))
    f.append(text(gx0 + 10, 293, "• Сумує найгірші відхилення: Δk/k ≈ (1-k)·(δ1 + δ2)", size=10, anchor="start", color=INK))
    f.append(text(gx0 + 10, 313, "Root-Sum-Square (RSS): незалежні випадкові змінні", size=10.5, bold=True, anchor="start", color=FIELD))
    f.append(text(gx0 + 10, 331, "• δ_rss = √((δ_tol)² + (δ_temp)² + (δ_age)²)", size=10, anchor="start", color=INK))
    f.append(text(gx0 + 10, 349, "• Дає реалістичну оцінку для серійного виробництва", size=9.5, italic=True, anchor="start", color=MUTED))

    # Права частина: Таблиця компонентів похибки
    tx0 = 460
    ty0 = 75
    tw = 340
    f.append(text(tx0 + tw / 2, ty0, "Бюджет похибок прецизійного резистора", size=13, bold=True, color=INK))

    # Таблиця
    row_h = 36
    header_y = ty0 + 15
    f.append(rect(tx0, header_y, tw, row_h, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    f.append(text(tx0 + 60, header_y + 22, "Джерело похибки", size=10.5, bold=True, color=INK))
    f.append(text(tx0 + 190, header_y + 22, "Типове 1% SMD", size=10.5, bold=True, color=INK))
    f.append(text(tx0 + 290, header_y + 22, "Прецизійне 0.1%", size=10.5, bold=True, color=FIELD))

    rows_data = [
        ("Початковий допуск", "±1.0%", "±0.1%"),
        ("Температурний дрейф (ΔT=50°C)", "±0.5% (100 ppm)", "±0.05% (10 ppm)"),
        ("Старіння (1000 год при 70°C)", "±0.5%", "±0.05%"),
        ("Вологість та паяння", "±0.25%", "±0.02%"),
    ]

    for i, (src_name, val_std, val_prec) in enumerate(rows_data):
        ry = header_y + (i + 1) * row_h
        f.append(rect(tx0, ry, tw, row_h, fill=(BG if i % 2 == 0 else "#fafbfc"), stroke="#d0d7de", sw=1))
        f.append(text(tx0 + 10, ry + 22, src_name, size=10, anchor="start", color=INK))
        f.append(text(tx0 + 190, ry + 22, val_std, size=10, color=POS))
        f.append(text(tx0 + 290, ry + 22, val_prec, size=10, color=FIELD, bold=True))

    # Підсумок таблиці
    total_y = header_y + 5 * row_h + 8
    f.append(rect(tx0, total_y, tw, 72, fill="#fdfbf0", stroke="#d6b656", sw=1.2, rx=6))
    f.append(text(tx0 + 10, total_y + 20, "Підсумок для 1% резистора:", size=10.5, bold=True, anchor="start", color="#b45f06"))
    f.append(text(tx0 + 10, total_y + 38, "• WCA найгірший випадок: ±(1.0 + 0.5 + 0.5 + 0.25)% = ±2.25%", size=10, anchor="start", color=POS))
    f.append(text(tx0 + 10, total_y + 56, "• RSS статистична похибка: √(1.0² + 0.5² + 0.5² + 0.25²) ≈ ±1.25%", size=10, bold=True, anchor="start", color=FIELD))

    render(os.path.join(IMG, "worst-case-divider.svg"), W, H, *f)


if __name__ == "__main__":
    fig_e_series_spacing()
    fig_led_power_derating()
    fig_adc_divider_sampling()
    fig_worst_case_divider()
    print("All figures generated successfully.")
