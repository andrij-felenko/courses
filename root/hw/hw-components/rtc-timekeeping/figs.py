# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми rtc-timekeeping.
Запуск: python figs.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_rtc_architecture():
    """Блок-схема внутрішньої архітектури мікросхеми RTC."""
    w, h = 900, 420
    out = []

    # Верхній заголовок схеми
    out.append(text(w / 2, 28, "Внутрішня функціональна архітектура годинника реального часу (RTC)", size=16, bold=True, anchor="middle", color=INK))

    # Лівий блок: Генератор і дільник
    out.append(rect(20, 55, 260, 340, fill="#f8fafc", stroke=LINE, rx=6))
    out.append(text(150, 80, "Тактовий генератор і дільник", size=13, bold=True, anchor="middle", color=INK))

    # Генератор 32768 Гц
    out.append(fitbox(40, 95, 220, 55, ["Генератор Пірса", "32 768 Гц (кварц)"], size=12, fill=FILL, stroke=LINE))

    # Стрілка вниз до прескалера
    out.append(arrow(150, 150, 150, 185, color=LINE))
    out.append(text(158, 170, "32.768 кГц", size=10, color=MUTED, anchor="start"))

    # 15-каскадний дільник
    out.append(fitbox(40, 185, 220, 65, ["15-розрядний дільник", "(2¹⁵ Ripple Counter)", "32 768 Гц → 1 Гц"], size=12, fill=FILL, stroke=LINE))

    # Стрілка вниз до виходу 1 Гц
    out.append(arrow(150, 250, 150, 285, color=LINE))

    # Блок стробу 1 Гц
    out.append(fitbox(40, 285, 220, 85, ["Секундний строб (1 Гц)", "Digital Trimming / Calib", "Фазове підстроювання"], size=11, fill="#e8f4fd", stroke=NEG))

    # Стрілка від дільника до лічильників
    out.append(arrow(260, 325, 305, 325, color=LINE))
    out.append(text(282, 315, "1 Гц", size=11, bold=True, color=NEG, anchor="middle"))

    # Центральний блок: Календарні лічильники BCD
    out.append(rect(305, 55, 280, 340, fill="#f8fafc", stroke=LINE, rx=6))
    out.append(text(445, 80, "Календарний блок BCD", size=13, bold=True, anchor="middle", color=INK))

    out.append(fitbox(325, 95, 240, 42, ["Секунди (00..59) & Хвилини (00..59)"], size=11, fill=FILL, stroke=LINE))
    out.append(arrow(445, 137, 445, 150, color=LINE))

    out.append(fitbox(325, 150, 240, 42, ["Години (00..23 / 12 AM/PM)"], size=11, fill=FILL, stroke=LINE))
    out.append(arrow(445, 192, 445, 205, color=LINE))

    out.append(fitbox(325, 205, 240, 42, ["День тижня (1..7) & Число (01..31)"], size=11, fill=FILL, stroke=LINE))
    out.append(arrow(445, 247, 445, 260, color=LINE))

    out.append(fitbox(325, 260, 240, 42, ["Місяць & Рік (00..99)"], size=11, fill=FILL, stroke=LINE))
    out.append(arrow(445, 302, 445, 315, color=LINE))

    out.append(fitbox(325, 315, 240, 60, ["Логіка високосного року", "Апаратна корекція 28/29 лютого", "Працює коректно до 2099 року"], size=10, fill="#edf7ed", stroke=FIELD))

    # Правий блок: Будильники, пам'ять та інтерфейс
    out.append(rect(605, 55, 275, 340, fill="#f8fafc", stroke=LINE, rx=6))
    out.append(text(742, 80, "Керування, будильники, зв'язок", size=13, bold=True, anchor="middle", color=INK))

    # Будильники
    out.append(fitbox(625, 95, 235, 50, ["Регістри будильників", "Alarm 1 / Alarm 2 (маски)"], size=11, fill=FILL, stroke=LINE))

    # Вихід переривання
    out.append(arrow(860, 120, 890, 120, color=POS))
    out.append(text(875, 110, "INT/SQW", size=10, bold=True, color=POS, anchor="end"))

    # Регістри та SRAM
    out.append(fitbox(625, 160, 235, 50, ["Регістри конфігурації / статусу", "Резервна пам'ять (SRAM)"], size=11, fill=FILL, stroke=LINE))

    # Тіньові регістри / Time-hold
    out.append(fitbox(625, 225, 235, 55, ["Time-Hold Latching", "Фіксація даних під час читання"], size=11, fill="#fef9e7", stroke="#d4ac0d"))

    # Інтерфейс зв'язку I2C / SPI
    out.append(fitbox(625, 295, 235, 80, ["Цифровий інтерфейс", "Шина I²C (SDA, SCL) / SPI", "Адресація та регістровий доступ"], size=11, fill="#e8f4fd", stroke=NEG))

    # Двосторонній зв'язок між лічильниками та інтерфейсом
    out.append(arrow(565, 250, 625, 250, color=LINE))
    out.append(arrow(625, 255, 565, 255, color=LINE))

    # Зв'язок будильника з лічильниками
    out.append(arrow(565, 120, 625, 120, color=LINE))

    render(os.path.join(IMG, "rtc-architecture.svg"), w, h, "".join(out))


def fig_temp_drift_parabola():
    """Параболічний температурний дрейф кварцу та компенсація TCXO."""
    w, h = 840, 440
    out = []

    out.append(text(w / 2, 26, "Температурна похибка 32.768 кГц кварцу та компенсація TCXO", size=16, bold=True, anchor="middle", color=INK))

    # Область графіка
    gx, gy, gw, gh = 100, 65, 680, 290

    # Сітка та осі
    out.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE))

    # Вертикальні лінії температури (-40, -20, 0, 25, 50, 70, 85)
    temps = [-40, -20, 0, 25, 50, 70, 85]
    def t_to_x(t):
        return gx + (t - (-40)) / (85 - (-40)) * gw

    def ppm_to_y(ppm):
        # Діапазон ppm від +10 до -160
        return gy + (10 - ppm) / (10 - (-160)) * gh

    for t in temps:
        x = t_to_x(t)
        out.append(line(x, gy, x, gy + gh, color="#e2e8f0", dash="3 3"))
        out.append(text(x, gy + gh + 18, "%d °C" % t, size=11, color=MUTED, anchor="middle"))

    # Горизонтальні лінії ppm (0, -20, -50, -100, -150)
    ppms = [0, -20, -50, -100, -150]
    for p in ppms:
        y = ppm_to_y(p)
        out.append(line(gx, y, gx + gw, y, color="#e2e8f0", dash="3 3"))
        out.append(text(gx - 10, y + 4, "%d" % p, size=11, color=MUTED, anchor="end"))

    # Вісь нульової похибки (0 ppm)
    y0 = ppm_to_y(0)
    out.append(line(gx, y0, gx + gw, y0, color="#94a3b8", sw=1.5))

    # Побудова параболи: df/f = -0.035 * (T - 25)^2
    pts_parabola = []
    for t_step in range(-40, 86, 2):
        ppm_val = -0.035 * ((t_step - 25) ** 2)
        pts_parabola.append((t_to_x(t_step), ppm_to_y(ppm_val)))

    # Малюємо криву камертонного кварцу
    for i in range(len(pts_parabola) - 1):
        x1, y1 = pts_parabola[i]
        x2, y2 = pts_parabola[i + 1]
        out.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Малюємо смугу TCXO компенсації (±2 ppm)
    y_tcxo_top = ppm_to_y(2)
    y_tcxo_bot = ppm_to_y(-2)
    out.append(rect(gx, y_tcxo_top, gw, y_tcxo_bot - y_tcxo_top, fill="#dcfce7", stroke=FIELD, sw=1.5))

    # Ключові точки на параболі
    # Вершина (25 °C, 0 ppm)
    out.append(circle(t_to_x(25), ppm_to_y(0), 4, fill=POS))
    out.append(text(t_to_x(25), ppm_to_y(0) - 10, "T₀ = 25 °C (максимум)", size=11, bold=True, color=POS, anchor="middle"))

    # Точка -20 °C (відхилення 45 °C -> -71 ppm)
    out.append(circle(t_to_x(-20), ppm_to_y(-70.875), 4, fill=POS))
    out.append(text(t_to_x(-20) - 10, ppm_to_y(-70.875) - 8, "-70.9 ppm (~6.1 с/добу)", size=10, bold=True, color=POS, anchor="end"))

    # Точка +70 °C (відхилення 45 °C -> -71 ppm)
    out.append(circle(t_to_x(70), ppm_to_y(-70.875), 4, fill=POS))
    out.append(text(t_to_x(70) + 10, ppm_to_y(-70.875) - 8, "-70.9 ppm", size=10, bold=True, color=POS, anchor="start"))

    # Точка -40 °C (-148 ppm)
    out.append(circle(t_to_x(-40), ppm_to_y(-147.875), 4, fill=POS))
    out.append(text(t_to_x(-40) + 10, ppm_to_y(-147.875) + 15, "-147.9 ppm (~12.8 с/добу)", size=10, bold=True, color=POS, anchor="start"))

    # Підписи осей
    out.append(text(gx + gw / 2, gy + gh + 38, "Температура навколишнього середовища T (°C)", size=12, bold=True, anchor="middle", color=INK))
    out.append('<text x="%d" y="%d" font-family="%s" font-size="12" font-weight="700" fill="%s" text-anchor="middle" transform="rotate(-90 %d %d)">Відхилення частоти Δf / f₀ (ppm)</text>' % (gx - 45, gy + gh / 2, FONT, INK, gx - 45, gy + gh / 2))

    # Легенда праворуч зверху
    out.append(rect(gx + 20, gy + 125, 340, 85, fill=FILL, stroke=LINE, rx=4))
    out.append(line(gx + 30, gy + 145, gx + 65, gy + 145, color=POS, sw=2.5))
    out.append(text(gx + 75, gy + 149, "Камертонний кварц: Δf/f₀ = -0.035·(T-25)²", size=11, bold=True, color=POS, anchor="start"))

    out.append(rect(gx + 30, gy + 165, 35, 14, fill="#dcfce7", stroke=FIELD))
    out.append(text(gx + 75, gy + 177, "Термокомпенсований RTC (TCXO): ±2 ppm", size=11, bold=True, color=FIELD, anchor="start"))
    out.append(text(gx + 75, gy + 195, "(±2 ppm відповідає похибці ≤ 1 хвилина на рік)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "temp-drift-parabola.svg"), w, h, "".join(out))


def fig_pierce_circuit_pcb():
    """Схема генератора Пірса та топологія друкованої плати з Guard Ring."""
    w, h = 900, 410
    out = []

    out.append(text(w / 2, 26, "Схемотехніка генератора Пірса та топологія охоронного кільця (Guard Ring)", size=16, bold=True, anchor="middle", color=INK))

    # Ліва частина: Електрична принципова схема
    out.append(rect(20, 55, 420, 335, fill="#f8fafc", stroke=LINE, rx=6))
    out.append(text(230, 80, "Електрична схема ультрамікроспоживчого генератора", size=13, bold=True, anchor="middle", color=INK))

    # Мікросхема RTC (інвертор)
    out.append(rect(40, 105, 140, 180, fill=FILL, stroke=LINE, rx=4))
    out.append(text(110, 125, "Мікросхема RTC", size=11, bold=True, anchor="middle", color=INK))

    # Піни OSC_IN та OSC_OUT
    out.append(text(170, 160, "OSC_IN", size=10, bold=True, anchor="end", color=INK))
    out.append(text(170, 240, "OSC_OUT", size=10, bold=True, anchor="end", color=INK))

    # Інвертор усередині
    out.append('<polygon points="70,180 70,220 105,200" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    out.append(circle(110, 200, 3, fill="#ffffff", stroke=LINE, sw=1.5))

    # Лінії від інвертора до пінів
    out.append(line(55, 160, 55, 200, color=LINE))
    out.append(line(55, 200, 70, 200, color=LINE))
    out.append(line(113, 200, 125, 200, color=LINE))
    out.append(line(125, 200, 125, 240, color=LINE))
    out.append(line(125, 160, 180, 160, color=LINE))
    out.append(line(125, 240, 180, 240, color=LINE))

    # Резистор зворотного зв'язку Rf (всередині чи зовні)
    out.append(line(145, 160, 145, 180, color=LINE))
    out.append(line(145, 220, 145, 240, color=LINE))
    out.append(rect(138, 180, 14, 40, fill="#ffffff", stroke=LINE))
    out.append(text(130, 203, "Rf", size=10, bold=True, anchor="end", color=MUTED))
    out.append(text(130, 215, "10-22M", size=9, color=MUTED, anchor="end"))

    # Демпфуючий резистор Rext на виході OSCOUT
    out.append(line(180, 240, 210, 240, color=LINE))
    out.append(rect(210, 233, 30, 14, fill="#ffffff", stroke=LINE))
    out.append(text(225, 225, "Rext", size=10, bold=True, anchor="middle", color=INK))
    out.append(line(240, 240, 280, 240, color=LINE))

    # Лінія OSCIN
    out.append(line(180, 160, 280, 160, color=LINE))

    # Конденсатор C1 (біля OSCIN)
    out.append(line(250, 160, 250, 180, color=LINE))
    out.append(line(240, 180, 260, 180, color=LINE, sw=2))
    out.append(line(240, 186, 260, 186, color=LINE, sw=2))
    out.append(line(250, 186, 250, 200, color=LINE))
    out.append(line(250, 200, 250, 210, color=LINE))
    out.append(line(243, 210, 257, 210, color=LINE))
    out.append(line(246, 214, 254, 214, color=LINE))
    out.append(line(248, 218, 252, 218, color=LINE))
    out.append(text(268, 185, "C₁", size=11, bold=True, anchor="start", color=INK))

    # Конденсатор C2 (біля OSCOUT)
    out.append(line(270, 240, 270, 260, color=LINE))
    out.append(line(260, 260, 280, 260, color=LINE, sw=2))
    out.append(line(260, 266, 280, 266, color=LINE, sw=2))
    out.append(line(270, 266, 270, 280, color=LINE))
    out.append(line(263, 280, 277, 280, color=LINE))
    out.append(line(266, 284, 274, 284, color=LINE))
    out.append(line(268, 288, 272, 288, color=LINE))
    out.append(text(288, 265, "C₂", size=11, bold=True, anchor="start", color=INK))

    # Кварцовий резонатор 32.768 кГц
    out.append(line(280, 160, 310, 160, color=LINE))
    out.append(line(280, 240, 310, 240, color=LINE))
    out.append(line(310, 160, 310, 185, color=LINE))
    out.append(line(310, 215, 310, 240, color=LINE))

    # Символ кварцу
    out.append(line(300, 185, 320, 185, color=LINE, sw=2))
    out.append(rect(304, 189, 12, 22, fill="#ffffff", stroke=LINE))
    out.append(line(300, 215, 320, 215, color=LINE, sw=2))
    out.append(text(340, 200, "32.768 кГц", size=11, bold=True, anchor="start", color=POS))
    out.append(text(340, 215, "(C_L = 6-12.5 пФ)", size=10, color=MUTED, anchor="start"))

    # Формула CL унизу зліва
    out.append(fitbox(35, 295, 390, 80, ["Ємність навантаження:", "C_L = (C₁ · C₂) / (C₁ + C₂) + C_stray", "де C_stray ≈ 2..5 пФ (паразитна ємність плати й виводів)"], size=10, fill="#edf7ed", stroke=FIELD))

    # Права частина: Топологія друкованої плати та Guard Ring
    out.append(rect(460, 55, 420, 335, fill="#f8fafc", stroke=LINE, rx=6))
    out.append(text(670, 80, "Топологія трасування та охоронне кільце", size=13, bold=True, anchor="middle", color=INK))

    # Корпус мікросхеми на платі
    out.append(rect(480, 110, 100, 120, fill="#334155", stroke=LINE, rx=3))
    out.append(text(530, 170, "RTC IC", size=12, bold=True, anchor="middle", color="#ffffff"))

    # Контактні площадки мікросхеми
    out.append(rect(580, 130, 14, 10, fill="#f59e0b"))
    out.append(text(572, 138, "OSCI", size=9, bold=True, anchor="end", color="#ffffff"))
    out.append(rect(580, 180, 14, 10, fill="#f59e0b"))
    out.append(text(572, 188, "OSCO", size=9, bold=True, anchor="end", color="#ffffff"))
    out.append(rect(580, 210, 14, 10, fill="#38bdf8"))
    out.append(text(572, 218, "GND", size=9, bold=True, anchor="end", color="#ffffff"))

    # Охоронне кільце Guard Ring (зелена лінія навколо)
    guard_d = "M 594,215 L 640,215 L 640,245 L 830,245 L 830,105 L 640,105 L 640,125 L 594,125 L 594,145 L 630,145 L 630,175 L 594,175 L 594,195 L 630,195 L 630,215 Z"
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (guard_d, FIELD))

    # Доріжки від IC до кварцу
    out.append(line(594, 135, 700, 135, color="#ea580c", sw=2.5))
    out.append(line(594, 185, 670, 185, color="#ea580c", sw=2.5))

    # Резистор Rext SMD
    out.append(rect(670, 180, 20, 10, fill="#cbd5e1", stroke=LINE))
    out.append(line(690, 185, 700, 185, color="#ea580c", sw=2.5))

    # Конденсатори C1, C2 SMD
    out.append(rect(700, 130, 12, 10, fill="#cbd5e1", stroke=LINE))
    out.append(line(706, 140, 706, 155, color=LINE))
    out.append(circle(706, 155, 3, fill=FIELD))

    out.append(rect(700, 180, 12, 10, fill="#cbd5e1", stroke=LINE))
    out.append(line(706, 190, 706, 205, color=LINE))
    out.append(circle(706, 205, 3, fill=FIELD))

    # Доріжки до кварцу
    out.append(line(712, 135, 740, 135, color="#ea580c", sw=2.5))
    out.append(line(712, 185, 740, 185, color="#ea580c", sw=2.5))

    # SMD Кварц
    out.append(rect(740, 120, 70, 80, fill="#94a3b8", stroke=LINE, rx=4))
    out.append(rect(744, 124, 62, 72, fill="#e2e8f0", stroke="#64748b"))
    out.append(text(775, 155, "32.768k", size=10, bold=True, anchor="middle", color=INK))
    out.append(text(775, 170, "SMD XTAL", size=9, color=MUTED, anchor="middle"))

    # Пояснювальний текст для Guard Ring
    out.append(text(735, 95, "Охоронне кільце (GND Guard Ring)", size=11, bold=True, color=FIELD, anchor="middle"))
    out.append(text(735, 260, "Захищає високоомні вузли OSCI/OSCO від витоків струму", size=10, color=MUTED, anchor="middle"))
    out.append(text(735, 275, "та наведень від сусідніх швидкісних шин", size=10, color=MUTED, anchor="middle"))

    # Попередження про заборонені траси
    out.append(fitbox(475, 295, 390, 80, ["Правила трасування:", "1. Жодних швидкісних сигналів (SPI, ШІМ) під кварцом.", "2. Суцільний земляний шар на нижньому шарі.", "3. Змивання залишків флюсу (витік 10 МОм зриває генерацію)."], size=10, fill="#fef2f2", stroke=POS))

    render(os.path.join(IMG, "pierce-circuit-pcb.svg"), w, h, "".join(out))


def fig_power_switchover():
    """Схема перемикання живлення Power Switchover VCC <-> VBAT."""
    w, h = 900, 410
    out = []

    out.append(text(w / 2, 26, "Схема автоматичного перемикання резервного живлення (Power Switchover)", size=16, bold=True, anchor="middle", color=INK))

    # Основна рамка схеми
    out.append(rect(30, 55, 840, 335, fill="#f8fafc", stroke=LINE, rx=6))

    # Вхід VCC (основне живлення)
    out.append(text(60, 105, "VCC (3.3V / 5V)", size=12, bold=True, anchor="start", color=POS))
    out.append(arrow(50, 115, 120, 115, color=POS))

    # Дільник для контролю напруги VCC
    out.append(line(120, 115, 120, 160, color=LINE))
    out.append(rect(113, 160, 14, 25, fill="#ffffff", stroke=LINE))
    out.append(line(120, 185, 120, 205, color=LINE))
    out.append(rect(113, 205, 14, 25, fill="#ffffff", stroke=LINE))
    out.append(line(120, 230, 120, 245, color=LINE))
    out.append(line(113, 245, 127, 245, color=LINE))

    # Компаратор напруги з гістерезисом
    out.append('<polygon points="200,170 200,230 250,200" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    out.append(text(210, 190, "+", size=12, bold=True, color=POS))
    out.append(text(210, 218, "−", size=12, bold=True, color=NEG))

    # Зв'язок дільника з неінвертуючим входом
    out.append(line(120, 185, 200, 185, color=LINE))

    # Джерело опорної напруги Vref
    out.append(fitbox(135, 215, 55, 30, ["V_ref", "1.25V"], size=9, fill=FILL, stroke=LINE))
    out.append(line(190, 220, 200, 220, color=LINE))

    # Логіка керування перемиканням (Power Control Logic)
    out.append(fitbox(280, 165, 140, 75, ["Логіка вибору", "та захист від", "брязкоту (Hysteresis)"], size=10, fill="#fef9e7", stroke="#d4ac0d"))
    out.append(arrow(250, 200, 280, 200, color=LINE))

    # Верхній ключ PMOS (для VCC)
    out.append(line(120, 115, 450, 115, color=POS, sw=2))
    out.append(rect(450, 95, 60, 40, fill="#ffffff", stroke=LINE, rx=3))
    out.append(text(480, 115, "P-MOS", size=11, bold=True, anchor="middle", color=INK))
    out.append(text(480, 128, "(SW1)", size=9, color=MUTED, anchor="middle"))

    # Нижній ключ PMOS (для VBAT)
    out.append(rect(450, 265, 60, 40, fill="#ffffff", stroke=LINE, rx=3))
    out.append(text(480, 285, "P-MOS", size=11, bold=True, anchor="middle", color=INK))
    out.append(text(480, 298, "(SW2)", size=9, color=MUTED, anchor="middle"))

    # Сигнали керування ключами від логіки
    out.append(line(350, 165, 350, 115, color=LINE, dash="3 3"))
    out.append(arrow(350, 115, 450, 115, color=LINE))
    out.append(text(400, 108, "Ctrl VCC", size=9, color=MUTED, anchor="middle"))

    out.append(line(350, 240, 350, 285, color=LINE, dash="3 3"))
    out.append(arrow(350, 285, 450, 285, color=LINE))
    out.append(text(400, 278, "Ctrl VBAT", size=9, color=MUTED, anchor="middle"))

    # Вхід VBAT (Батарейка або Суперконденсатор)
    out.append(text(60, 275, "VBAT (CR2032 / Supercap)", size=12, bold=True, anchor="start", color=NEG))
    out.append(arrow(50, 285, 120, 285, color=NEG))
    out.append(line(120, 285, 450, 285, color=NEG, sw=2))

    # Вихід об'єднаного живлення V_RTC
    out.append(line(510, 115, 600, 115, color=LINE, sw=2))
    out.append(line(510, 285, 600, 285, color=LINE, sw=2))
    out.append(line(600, 115, 600, 285, color=LINE, sw=2))
    out.append(arrow(600, 200, 660, 200, color=LINE))

    # Внутрішній RTC Core
    out.append(fitbox(660, 160, 180, 85, ["Ядро RTC (V_RTC)", "Генератор 32 кГц", "Дільник & Лічильники", "I_core ≈ 150-300 нА"], size=11, fill="#e8f4fd", stroke=NEG))

    # Схема підзаряду суперконденсатора (Trickle Charger)
    out.append(rect(200, 80, 170, 50, fill="#edf7ed", stroke=FIELD, rx=3))
    out.append(text(285, 98, "Trickle Charger (опція)", size=10, bold=True, anchor="middle", color=FIELD))
    out.append(text(285, 116, "Діод + Резистор (250Ω - 4kΩ)", size=9, color=MUTED, anchor="middle"))

    # Підписи режимів роботи
    out.append(fitbox(40, 315, 390, 55, ["Режим 1: VCC > V_th → SW1 закрито, SW2 відкрито.", "RTC живиться від мережі, батарейка розвантажена."], size=10, fill=FILL, stroke=LINE))
    out.append(fitbox(450, 315, 400, 55, ["Режим 2: VCC < V_th → SW1 відкрито, SW2 закрито.", "RTC безшовно перемикається на батарейку VBAT."], size=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "power-switchover.svg"), w, h, "".join(out))


if __name__ == '__main__':
    fig_rtc_architecture()
    fig_temp_drift_parabola()
    fig_pierce_circuit_pcb()
    fig_power_switchover()
    print("Всі фігури згенеровано успішно.")
