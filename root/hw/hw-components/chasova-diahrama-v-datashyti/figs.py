# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Часова діаграма в даташиті»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_anatomy():
    """Фігура 1: Анатомія часових діаграм: тактові фронти, валідні рівні, Hi-Z, шинні переходи."""
    w, h = 840, 420
    f = []

    # Фонові смуги для розділення сигналів
    f.append(rect(15, 45, 810, 75, fill="#fbfcfd", stroke="#e5e7eb", rx=4))
    f.append(rect(15, 125, 810, 75, fill="#ffffff", stroke="#e5e7eb", rx=4))
    f.append(rect(15, 205, 810, 85, fill="#fbfcfd", stroke="#e5e7eb", rx=4))
    f.append(rect(15, 295, 810, 85, fill="#ffffff", stroke="#e5e7eb", rx=4))

    # Мітки сигналів ліворуч
    f.append(text(80, 87, "CLK", size=13, bold=True, color=INK))
    f.append(text(80, 167, "DATA (1-біт)", size=13, bold=True, color=INK))
    f.append(text(80, 252, "Шина D[7:0]", size=13, bold=True, color=INK))
    f.append(text(80, 342, "Лінія з Hi-Z", size=13, bold=True, color=INK))

    # Розділювач міток і діаграми
    f.append(line(150, 45, 150, 380, color="#d1d5db", sw=1.5, dash="4,4"))

    # 1. Сигнал CLK (Періодичний тактовий сигнал)
    clk_path = (
        "M 170 105 L 210 105 L 225 65 L 285 65 L 300 105 L 360 105 "
        "L 375 65 L 435 65 L 450 105 L 510 105 L 525 65 L 585 65 "
        "L 600 105 L 660 105 L 675 65 L 735 65 L 750 105 L 790 105"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (clk_path, INK))

    # Рівні напруги на тактовому сигналі
    f.append(line(170, 85, 790, 85, color=MUTED, sw=1, dash="3,3"))
    f.append(text(805, 88, "50% V_DD", size=10, color=MUTED, anchor="start"))
    
    # Стрілки фронтів
    f.append(arrow(225, 115, 225, 95, color=POS, sw=1.5))
    f.append(text(225, 127, "Фронт наростання", size=10, color=POS, bold=True))
    f.append(arrow(300, 55, 300, 75, color=NEG, sw=1.5))
    f.append(text(300, 47, "Зріз спаду", size=10, color=NEG, bold=True))

    # 2. Сигнал DATA (1-бітний цифровий сигнал)
    data_path = (
        "M 170 185 L 260 185 L 275 145 L 485 145 L 500 185 L 630 185 L 645 145 L 790 145"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (data_path, FIELD))
    
    # Пороги логічних рівнів
    f.append(line(170, 145, 790, 145, color="#d1d5db", sw=0.8, dash="2,2"))
    f.append(line(170, 185, 790, 185, color="#d1d5db", sw=0.8, dash="2,2"))
    f.append(text(805, 148, "V_IH / V_OH (Лог. 1)", size=10, color=FIELD, anchor="start"))
    f.append(text(805, 188, "V_IL / V_OL (Лог. 0)", size=10, color=FIELD, anchor="start"))

    # 3. Паралельна шина даних D[7:0]
    bus_top = (
        "M 170 225 L 270 225 L 290 265 L 490 265 L 510 225 L 620 225 L 640 265 L 790 265"
    )
    bus_bot = (
        "M 170 265 L 270 265 L 290 225 L 490 225 L 510 265 L 620 265 L 640 225 L 790 225"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (bus_top, INK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (bus_bot, INK))
    
    # Заливка стабільних областей
    f.append(rect(175, 227, 90, 36, fill="#eafaf1", stroke="none"))
    f.append(text(220, 249, "Дані: 0x55", size=11, bold=True, color=FIELD))
    
    f.append(rect(295, 227, 190, 36, fill="#eafaf1", stroke="none"))
    f.append(text(390, 249, "Валідні дані: Байт 1 (0xAA)", size=11, bold=True, color=FIELD))
    
    f.append(rect(515, 227, 100, 36, fill="#fdecea", stroke="none"))
    f.append(text(565, 249, "Зміна шини", size=11, bold=True, color=POS))

    f.append(rect(645, 227, 140, 36, fill="#eafaf1", stroke="none"))
    f.append(text(715, 249, "Валідні дані: Байт 2", size=11, bold=True, color=FIELD))

    # 4. Лінія з Hi-Z
    hiz_active1 = "M 170 315 L 280 315 L 295 338"
    hiz_float = "M 295 338 L 545 338"
    hiz_active2 = "M 545 338 L 560 360 L 790 360"
    
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (hiz_active1, INK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (hiz_float, MUTED))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (hiz_active2, INK))
    
    f.append(textbox(420, 338, "Високоімпедансний стан (Hi-Z / Tri-State)\nВихід відключено, лінія пливе або підтягнута", size=11, fill="#f4f6f8", color=MUTED)[0])

    f.append(arrow(280, 212, 280, 235, color=POS, sw=1.3))
    f.append(text(280, 202, "Шинний перехід", size=10, color=POS, bold=True))

    return render(os.path.join(OUT_DIR, "timing-diagram-anatomy.svg"), w, h, *f)


def fig_setup_hold():
    """Фігура 2: Час встановлення (t_setup), час утримання (t_hold) та апертурне вікно."""
    w, h = 840, 380
    f = []

    f.append(rect(15, 20, 810, 340, fill="#ffffff", stroke="#e5e7eb", rx=6))

    # Вертикальна лінія активного тактового фронту
    edge_x = 430
    f.append(line(edge_x, 35, edge_x, 330, color=POS, sw=2, dash="5,3"))
    f.append(textbox(edge_x, 35, "АКТИВНИЙ ТАКТОВИЙ ФРОНТ (Строб зчитування)", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # Область t_setup (тільки верхня частина, щоб не перетинати нижній аварійний блок)
    f.append(rect(270, 70, 160, 175, fill="#eafaf1", stroke="#a3e4d7", sw=1.2, rx=4))
    
    # Область t_hold
    f.append(rect(430, 70, 130, 175, fill="#ebf5fb", stroke="#aed6f1", sw=1.2, rx=4))

    # Стрілки інтервалів t_setup та t_hold
    f.append(line(270, 85, 430, 85, color=FIELD, sw=2))
    f.append(line(270, 78, 270, 92, color=FIELD, sw=2))
    f.append(line(430, 78, 430, 92, color=FIELD, sw=2))
    f.append(text(350, 78, "t_setup (Час встановлення)", size=12, bold=True, color=FIELD))

    f.append(line(430, 85, 560, 85, color=NEG, sw=2))
    f.append(line(560, 78, 560, 92, color=NEG, sw=2))
    f.append(text(495, 78, "t_hold (Час утримання)", size=12, bold=True, color=NEG))

    # 1. Сигнал такту CLK
    f.append(text(80, 140, "Тактовий сигнал CLK", size=12, bold=True, color=INK))
    clk_path = "M 130 160 L 415 160 L 430 115 L 750 115"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (clk_path, INK))

    # 2. Валідний сигнал даних
    f.append(text(80, 215, "Дані на вході D_IN\n(Коректний режим)", size=11, bold=True, color=FIELD))
    data_ok_top = "M 130 235 L 250 235 L 270 195 L 560 195 L 580 235 L 750 235"
    data_ok_bot = "M 130 195 L 250 195 L 270 235 L 560 235 L 580 195 L 750 195"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (data_ok_top, FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (data_ok_bot, FIELD))
    f.append(text(415, 218, "Дані ГАРАНТОВАНО СТАБІЛЬНІ (Valid Data Window)", size=11, bold=True, color=FIELD))

    # 3. Некоректний сигнал
    f.append(text(80, 285, "Дані з порушенням\n(Збій таймінгу)", size=11, bold=True, color=POS))
    data_bad_top = "M 130 305 L 370 305 L 390 265 L 470 265 L 490 305 L 750 305"
    data_bad_bot = "M 130 265 L 370 265 L 390 305 L 470 305 L 490 265 L 750 265"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % (data_bad_top, POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % (data_bad_bot, POS))
    
    # Виділення зони збою (на рівні y=255..305, де немає фонових rect)
    f.append(rect(360, 255, 140, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(430, 276, "ЗМІНА ПІД ЧАС СТРОБУ!", size=10, bold=True, color=POS))
    f.append(text(430, 292, "Небезпека метастабільності", size=9.5, color=POS))

    # Підсумковий інформаційний блок
    f.append(textbox(430, 345, "Вікно апертури: t_aperture = t_setup + t_hold. Будь-яка зміна даних усередині цього вікна веде до збою стану або помилкового біта.", size=11, fill="#f8f9fa", color=INK)[0])

    return render(os.path.join(OUT_DIR, "setup-and-hold-margins.svg"), w, h, *f)


def fig_clock_params():
    """Фігура 3: Часові параметри тактового імпульсу: t_cyc, t_high, t_low, t_rise, t_fall, jitter."""
    w, h = 840, 370
    f = []

    f.append(rect(15, 20, 810, 330, fill="#ffffff", stroke="#e5e7eb", rx=6))

    # Горизонтальні рівні напруги
    f.append(line(90, 86, 760, 86, color="#e5e7eb", sw=1, dash="4,4"))
    f.append(line(90, 150, 760, 150, color=MUTED, sw=1, dash="3,3"))
    f.append(line(90, 214, 760, 214, color="#e5e7eb", sw=1, dash="4,4"))

    f.append(text(80, 89, "90% V_DD", size=10, color=MUTED, anchor="end"))
    f.append(text(80, 153, "50% V_DD", size=10, bold=True, color=INK, anchor="end"))
    f.append(text(80, 217, "10% V_DD", size=10, color=MUTED, anchor="end"))

    # Хвильова форма такту
    clk_wave = (
        "M 110 230 L 170 230 "
        "C 180 230, 185 200, 190 150 "
        "C 195 100, 200 70, 215 70 "
        "L 385 70 "
        "C 395 70, 405 100, 410 150 "
        "C 415 200, 420 230, 435 230 "
        "L 605 230 "
        "C 615 230, 625 200, 630 150 "
        "C 635 100, 640 70, 655 70 "
        "L 750 70"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (clk_wave, INK))

    # t_rise (10% -> 90%)
    f.append(line(174, 214, 174, 275, color=FIELD, sw=1.2, dash="3,2"))
    f.append(line(206, 86, 206, 275, color=FIELD, sw=1.2, dash="3,2"))
    f.append(line(174, 265, 206, 265, color=FIELD, sw=1.8))
    f.append(line(174, 260, 174, 270, color=FIELD, sw=1.8))
    f.append(line(206, 260, 206, 270, color=FIELD, sw=1.8))
    f.append(text(190, 290, "t_rise (10%→90%)", size=11, bold=True, color=FIELD))

    # t_fall (90% -> 10%)
    f.append(line(394, 86, 394, 275, color=POS, sw=1.2, dash="3,2"))
    f.append(line(426, 214, 426, 275, color=POS, sw=1.2, dash="3,2"))
    f.append(line(394, 265, 426, 265, color=POS, sw=1.8))
    f.append(line(394, 260, 394, 270, color=POS, sw=1.8))
    f.append(line(426, 260, 426, 270, color=POS, sw=1.8))
    f.append(text(410, 290, "t_fall (90%→10%)", size=11, bold=True, color=POS))

    # t_high (50% -> 50%)
    f.append(line(190, 150, 190, 45, color=NEG, sw=1.2, dash="3,2"))
    f.append(line(410, 150, 410, 45, color=NEG, sw=1.2, dash="3,2"))
    f.append(line(190, 52, 410, 52, color=NEG, sw=1.8))
    f.append(line(190, 47, 190, 57, color=NEG, sw=1.8))
    f.append(line(410, 47, 410, 57, color=NEG, sw=1.8))
    f.append(text(300, 44, "t_high (Тривалість високого рівня)", size=11, bold=True, color=NEG))

    # t_low (50% -> 50%)
    f.append(line(630, 150, 630, 45, color=NEG, sw=1.2, dash="3,2"))
    f.append(line(410, 52, 630, 52, color=NEG, sw=1.8))
    f.append(line(630, 47, 630, 57, color=NEG, sw=1.8))
    f.append(text(520, 44, "t_low (Тривалість низького рівня)", size=11, bold=True, color=NEG))

    # T_clk / t_cyc
    f.append(line(190, 325, 630, 325, color=INK, sw=2))
    f.append(line(190, 317, 190, 333, color=INK, sw=2))
    f.append(line(630, 317, 630, 333, color=INK, sw=2))
    f.append(text(410, 343, "T_clk = t_cyc = 1 / f_clk (Період тактового циклу)", size=12, bold=True, color=INK))

    # Джиттер
    f.append(rect(615, 135, 30, 30, fill="#fdecea", stroke=POS, sw=1, rx=3))
    f.append(text(690, 145, "t_jitter (Фазове", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(690, 158, "тремтіння фронту)", size=10, bold=True, color=POS, anchor="start"))

    return render(os.path.join(OUT_DIR, "clock-waveform-parameters.svg"), w, h, *f)


def fig_timing_budget():
    """Фігура 4: Аналіз часового бюджету (Timing Margin Budget) синхронної шини."""
    w, h = 860, 400
    f = []

    f.append(rect(15, 20, 830, 360, fill="#ffffff", stroke="#e5e7eb", rx=6))

    # Ліва колонка: Передавач
    f.append(rect(35, 40, 180, 90, fill="#f4f6f8", stroke=INK, sw=1.8, rx=6))
    f.append(text(125, 65, "ПЕРЕДАВАЧ (Tx)", size=12, bold=True, color=INK))
    f.append(text(125, 85, "MCU / FPGA / Master", size=10, color=MUTED))
    f.append(text(125, 105, "Затримка: t_co(max)", size=11, bold=True, color=POS))

    # Центральна колонка: Друкована плата
    f.append(rect(275, 40, 270, 90, fill="#fbfcfd", stroke="#d1d5db", sw=1.5, rx=6))
    f.append(text(410, 65, "ДРУКОВАНА ПЛАТА (PCB)", size=12, bold=True, color=INK))
    f.append(text(410, 85, "Довжина траси: L = 100 мм", size=10, color=MUTED))
    f.append(text(410, 105, "t_flight = L · 6.5 пс/мм = 0.65 нс", size=11, bold=True, color=FIELD))

    # Права колонка: Приймач
    f.append(rect(605, 40, 220, 90, fill="#f4f6f8", stroke=INK, sw=1.8, rx=6))
    f.append(text(715, 65, "ПРИЙМАЧ (Rx)", size=12, bold=True, color=INK))
    f.append(text(715, 85, "SPI Flash / Sensor / Slave", size=10, color=MUTED))
    f.append(text(715, 105, "Вимога: t_setup, t_hold", size=11, bold=True, color=NEG))

    # З'єднувальні стрілки
    f.append(arrow(215, 85, 275, 85, color=INK, sw=2))
    f.append(arrow(545, 85, 605, 85, color=INK, sw=2))

    # Часовий розклад
    f.append(text(430, 160, "РОЗКЛАД БЮДЖЕТУ ТАКТОВОГО ПЕРІОДУ (T_clk = 20 нс при 50 МГц)", size=13, bold=True, color=INK))

    # 1. t_co
    f.append(rect(50, 180, 259, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(179, 203, "t_co(max) = 7.0 нс", size=11, bold=True, color=POS))
    f.append(text(179, 218, "Затримка передавача", size=9.5, color=POS))

    # 2. t_flight
    f.append(rect(309, 180, 37, 50, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(327, 203, "t_fl", size=10, bold=True, color=FIELD))
    f.append(text(327, 218, "1.0нс", size=9.5, color=FIELD))

    # 3. t_setup
    f.append(rect(346, 180, 148, 50, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=4))
    f.append(text(420, 203, "t_setup = 4.0 нс", size=11, bold=True, color=NEG))
    f.append(text(420, 218, "Вимога приймача", size=9.5, color=NEG))

    # 4. t_skew + jitter
    f.append(rect(494, 180, 55, 50, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=4))
    f.append(text(521, 203, "t_unc", size=10, bold=True, color="#b7950b"))
    f.append(text(521, 218, "1.5 нс", size=9.5, color="#b7950b"))

    # 5. Setup Margin
    f.append(rect(549, 180, 241, 50, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=4))
    f.append(text(669, 203, "ПОЗИТИВНИЙ ЗАПАС (Slack) = +6.5 нс", size=11, bold=True, color="#1e8449"))
    f.append(text(669, 218, "Шина надійна: t_margin > 0", size=10, color="#1e8449"))

    # Повна розмірна лінія T_clk
    f.append(line(50, 245, 790, 245, color=INK, sw=2))
    f.append(line(50, 238, 50, 252, color=INK, sw=2))
    f.append(line(790, 238, 790, 252, color=INK, sw=2))
    f.append(text(420, 262, "Повний тактовий період T_clk = 20.0 нс (100% бюджету)", size=12, bold=True, color=INK))

    # Нерівність
    f.append(textbox(430, 315, "Основна умова безпомилкової передачі (Setup Constraint):\nT_clk ≥ t_co(max) + t_flight + t_setup + t_skew + t_jitter\nЯкщо T_clk менший за суму — виникає негативний запас (Negative Slack) і збій даних.", size=11, fill="#f8f9fa", stroke="#d1d5db", color=INK)[0])

    return render(os.path.join(OUT_DIR, "timing-budget-analysis.svg"), w, h, *f)


def fig_flash_read():
    """Фігура 5: Часова діаграма читання SPI Flash (Winbond W25Q / Fast Read 0x0B)."""
    w, h = 860, 420
    f = []

    f.append(rect(15, 20, 830, 380, fill="#ffffff", stroke="#e5e7eb", rx=6))

    # 4 сигнали: CS#, SCK, SI/MOSI, SO/MISO
    f.append(text(75, 78, "CS# (Вибір чипа)", size=11, bold=True, color=INK))
    f.append(text(75, 158, "SCK (Тактовий такт)", size=11, bold=True, color=INK))
    f.append(text(75, 248, "SI (Команда/Адреса)", size=11, bold=True, color=FIELD))
    f.append(text(75, 338, "SO (Вихід даних)", size=11, bold=True, color=NEG))

    f.append(line(160, 35, 160, 370, color="#d1d5db", sw=1.5, dash="4,4"))

    # 1. CS# Waveform
    cs_path = "M 170 60 L 210 60 L 220 90 L 740 90 L 750 60 L 810 60"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (cs_path, INK))
    
    # t_CSS
    f.append(line(220, 95, 220, 120, color=POS, sw=1.2, dash="3,2"))
    f.append(line(260, 135, 260, 120, color=POS, sw=1.2, dash="3,2"))
    f.append(line(220, 115, 260, 115, color=POS, sw=1.5))
    f.append(text(240, 110, "t_CSS", size=10, bold=True, color=POS))

    # t_CS
    f.append(line(750, 60, 750, 45, color=POS, sw=1.2, dash="3,2"))
    f.append(line(810, 60, 810, 45, color=POS, sw=1.2, dash="3,2"))
    f.append(line(750, 50, 810, 50, color=POS, sw=1.5))
    f.append(text(780, 42, "t_CS (Recovery)", size=10, bold=True, color=POS))

    # 2. SCK Waveform
    sck_path = (
        "M 170 170 L 260 170 "
        "L 270 140 L 290 140 L 300 170 L 320 170 L 330 140 L 350 140 L 360 170 "
        "L 380 170 L 390 140 L 410 140 L 420 170 "
        "L 450 170 L 460 140 L 480 140 L 490 170 L 510 170 L 520 140 L 540 140 L 550 170 "
        "L 580 170 L 590 140 L 610 140 L 620 170 L 640 170 L 650 140 L 670 140 L 680 170 "
        "L 700 170 L 710 140 L 730 140 L 740 170 L 810 170"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (sck_path, INK))

    # 3. SI (MOSI)
    f.append(rect(260, 230, 160, 30, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(340, 250, "Опкод Fast Read (0x0B)", size=11, bold=True, color=FIELD))
    
    f.append(rect(420, 230, 100, 30, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(470, 250, "Адреса A[23:0]", size=10, bold=True, color=FIELD))

    f.append(rect(520, 230, 60, 30, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    f.append(text(550, 250, "Dummy", size=10, bold=True, color="#b7950b"))

    f.append(line(580, 245, 740, 245, color=MUTED, sw=1.5, dash="4,3"))

    # 4. SO (MISO)
    f.append(line(170, 335, 580, 335, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(375, 325, "Високоімпедансний стан SO (Hi-Z)", size=10, color=MUTED))

    f.append(rect(595, 320, 145, 30, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=3))
    f.append(text(667, 340, "Дані з пам'яті: Байт D0", size=11, bold=True, color=NEG))

    # t_CLQV
    f.append(line(580, 170, 580, 365, color=POS, sw=1.2, dash="3,2"))
    f.append(line(595, 335, 595, 365, color=POS, sw=1.2, dash="3,2"))
    f.append(line(580, 360, 595, 360, color=POS, sw=1.5))
    f.append(text(587, 375, "t_CLQV (Затримка валідності даних ≤ 6–8 нс)", size=10, bold=True, color=POS))

    # t_SHZ
    f.append(line(750, 335, 810, 335, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(780, 325, "t_SHZ (Hi-Z)", size=9.5, color=MUTED))

    return render(os.path.join(OUT_DIR, "flash-memory-read-timing.svg"), w, h, *f)


def fig_display_parallel():
    """Фігура 6: Часова діаграма паралельного 8080 інтерфейсу дисплея (ST7789 / ILI9341)."""
    w, h = 860, 400
    f = []

    f.append(rect(15, 20, 830, 360, fill="#ffffff", stroke="#e5e7eb", rx=6))

    # Сигнали: CS#, D/CX, WR#, D[7:0]
    f.append(text(75, 68, "CS# (Chip Select)", size=11, bold=True, color=INK))
    f.append(text(75, 138, "D/CX (Команда/Дані)", size=11, bold=True, color=FIELD))
    f.append(text(75, 218, "WR# (Строб запису)", size=11, bold=True, color=POS))
    f.append(text(75, 308, "Шина D[7:0]", size=11, bold=True, color=NEG))

    f.append(line(160, 35, 160, 350, color="#d1d5db", sw=1.5, dash="4,4"))

    # 1. CS#
    cs_p = "M 170 55 L 210 55 L 220 75 L 750 75 L 760 55 L 810 55"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (cs_p, INK))

    # 2. D/CX
    dc_p = "M 170 145 L 420 145 L 435 125 L 810 125"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (dc_p, FIELD))
    f.append(text(300, 140, "D/CX = 0 (Запис КОМАНДИ)", size=10, bold=True, color=FIELD))
    f.append(text(620, 120, "D/CX = 1 (Запис ДАНИХ / Пікселів)", size=10, bold=True, color=FIELD))

    # 3. WR#
    wr_p = (
        "M 170 205 L 260 205 L 270 225 L 340 225 L 350 205 "
        "L 480 205 L 490 225 L 560 225 L 570 205 L 810 205"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (wr_p, POS))

    f.append(line(270, 225, 340, 225, color=POS, sw=1.5))
    f.append(line(270, 220, 270, 230, color=POS, sw=1.5))
    f.append(line(340, 220, 340, 230, color=POS, sw=1.5))
    f.append(text(305, 240, "t_WRL (≥15 нс)", size=10, bold=True, color=POS))

    f.append(line(350, 205, 480, 205, color=POS, sw=1.5))
    f.append(line(350, 200, 350, 210, color=POS, sw=1.5))
    f.append(line(480, 200, 480, 210, color=POS, sw=1.5))
    f.append(text(415, 195, "t_WRH (≥15 нс)", size=10, bold=True, color=POS))

    # Повний цикл запису t_CYCW
    f.append(line(260, 260, 480, 260, color=INK, sw=1.8))
    f.append(line(260, 253, 260, 267, color=INK, sw=1.8))
    f.append(line(480, 253, 480, 267, color=INK, sw=1.8))
    f.append(text(370, 275, "t_CYCW (Повний цикл запису ≥ 66 нс → f_max ≤ 15 МГц)", size=11, bold=True, color=INK))

    # 4. Шина D[7:0]
    f.append(rect(250, 290, 120, 30, fill="#eafaf1", stroke=NEG, sw=1.5, rx=3))
    f.append(text(310, 310, "Опкод (0x2C)", size=11, bold=True, color=NEG))

    f.append(rect(470, 290, 120, 30, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=3))
    f.append(text(530, 310, "Колір пікселя", size=11, bold=True, color=NEG))

    f.append(line(350, 185, 350, 335, color=POS, sw=1.5, dash="4,3"))
    f.append(arrow(350, 185, 350, 200, color=POS, sw=1.8))
    f.append(text(350, 175, "Фіксація за висхідним фронтом WR#", size=10, bold=True, color=POS))

    f.append(line(250, 335, 350, 335, color=NEG, sw=1.5))
    f.append(text(300, 350, "t_DST (Setup ≥ 10 нс)", size=10, bold=True, color=NEG))

    f.append(line(350, 335, 370, 335, color=NEG, sw=1.5))
    f.append(text(395, 350, "t_DHT (≥10нс)", size=9.5, color=NEG))

    return render(os.path.join(OUT_DIR, "display-controller-parallel-timing.svg"), w, h, *f)


if __name__ == "__main__":
    print("Генерація SVG-фігур для часових діаграм...")
    fig_anatomy()
    fig_setup_hold()
    fig_clock_params()
    fig_timing_budget()
    fig_flash_read()
    fig_display_parallel()
    print("Всі 6 фігур згенеровано успішно у ./img/")
