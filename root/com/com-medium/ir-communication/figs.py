# -*- coding: utf-8 -*-
"""Фігури до теми «ІЧ-зв'язок».
Запуск: python figs.py  → створює SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Додаткові кольори
OPTICAL   = "#9b59b6"  # інфрачервоне випромінювання (фіолетовий спектр)
SUN_NOISE = "#e67e22"  # оптичний шум / сонячна засвітка (помаранчевий)
CARRIER   = "#2980b9"  # тримальна частота (синій)
SIGNAL_HI = "#27ae60"  # корисний демодульований сигнал (зелений)
CHIP_BG   = "#f8fafc"  # фон мікросхеми
DARK_EPX  = "#2d3748"  # темний компаунд приймача
BORDER    = INK

# ── 1. Фізика оптичного каналу: фонова засвітка та модульована тримальна ──────
def fig_ir_optical_channel():
    W, H = 840, 420
    f = [text(W / 2, 26, "Фонова оптична засвітка та модуляція тримальної частоти", size=15, bold=True)]

    # Ліва колонка: Немодульований сигнал (Baseband)
    f.append(rect(20, 50, 390, 270, fill="#fdfefe", stroke=MUTED, sw=1, rx=8))
    f.append(text(215, 75, "Пряма передача (Baseband без модуляції)", size=12, bold=True, color=POS))

    # Сонце та лампи (шум)
    f.append(circle(65, 115, 18, fill="#fef3c7", stroke=SUN_NOISE, sw=1.5))
    f.append(text(65, 119, "☀", size=16, color=SUN_NOISE))
    f.append(text(160, 112, "Постійне сонце (I_dc ≈ 100..500 мкА)", size=10, color=SUN_NOISE))
    f.append(text(160, 126, "Мерехтіння ламп (100 Гц, 30..50 кГц)", size=10, color=MUTED))

    # Сигнали на графіку
    f.append(line(50, 185, 380, 185, color=MUTED, sw=1, dash="2,2"))
    f.append(text(50, 175, "Струм I_ph", size=9, color=MUTED, anchor="start"))
    
    # Сумарний шумний сигнал
    pts_noise = [(60, 205), (100, 195), (140, 215), (180, 190), 
                 (200, 150), (240, 145), (260, 195), (300, 210), (340, 198), (380, 205)]
    for i in range(len(pts_noise)-1):
        f.append(line(pts_noise[i][0], pts_noise[i][1], pts_noise[i+1][0], pts_noise[i+1][1], color=SUN_NOISE, sw=1.8))
    
    f.append(text(230, 140, "Слабкий сигнал потонув у шумі", size=10, bold=True, color=POS))
    f.append(line(190, 225, 270, 225, color=POS, sw=1.5))
    f.append(text(230, 240, "Поріг компаратора не спрацьовує", size=10, color=POS))

    f.append(text(215, 295, "Результат: неможливість виділити дані на фоні світла", size=10, bold=True, color=POS))

    # Права колонка: Модуляція тримальної частоти (38 кГц)
    f.append(rect(430, 50, 390, 270, fill="#fcfdfd", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(625, 75, "Модуляція тримальної (Burst 38 кГц)", size=12, bold=True, color=FIELD))

    # Спектральний розподіл
    f.append(line(460, 200, 790, 200, color=MUTED, sw=1)) # вісь f
    f.append(text(780, 215, "Частота f", size=9, color=MUTED))
    
    # Спектр шуму (біля 0 Гц та 100 Гц)
    f.append(rect(470, 140, 50, 60, fill="#feebc8", stroke=SUN_NOISE, sw=1, rx=3))
    f.append(text(495, 130, "Шум 0..1 кГц", size=9, color=SUN_NOISE))

    # Смуговий фільтр приймача (BPF) на 38 кГц
    f.append(rect(630, 100, 70, 100, fill="#e6fffa", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(665, 92, "Смуга BPF (38 кГц)", size=10, bold=True, color=FIELD))

    # Пачка 38 кГц всередині фільтра
    f.append(line(665, 110, 665, 198, color=CARRIER, sw=3))
    f.append(text(665, 150, "Сигнал", size=10, bold=True, color=CARRIER))

    f.append(text(625, 240, "Смуговий фільтр Q ≈ 15 відкидає I_dc і 100 Гц", size=10, color=FIELD))
    f.append(text(625, 260, "Детектор обвідної відновлює прямокутний біт", size=10, color=INK))
    f.append(text(625, 295, "Результат: стабільний прийом при яскравому сонці", size=10, bold=True, color=FIELD))

    # Пояснювальна картка
    f.append(fitbox(20, 335, 800, 65,
                    "Постійне світло сонця створює постійний фоновий струм фотодіода (DC), а лампи — низькочастотні завади.\n"
                    "Передача сигналів пачками піднесучої 36–40 кГц дозволяє смуговому фільтру приймача повністю придушити\n"
                    "фонову засвітку та виділити корисний інформаційний імпульс.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "ir-optical-channel.svg"), W, H, *f)


# ── 2. Внутрішня структура приймача TSOP ──────────────────────────────────────
def fig_tsop_internal_block_diagram():
    W, H = 840, 380
    f = [text(W / 2, 26, "Внутрішня архітектура інтегрованого ІЧ-приймача (TSOP/SFH)", size=15, bold=True)]

    # Корпус мікросхеми
    f.append(rect(30, 50, 780, 240, fill=CHIP_BG, stroke=DARK_EPX, sw=2, rx=10))
    f.append(text(120, 72, "Корпус TSOP (епоксидний ІЧ-фільтр)", size=11, bold=True, color=DARK_EPX))

    # PIN-фотодіод
    f.append(rect(50, 110, 80, 100, fill="#2d3748", stroke=OPTICAL, sw=2, rx=6))
    f.append(text(90, 150, "PIN", size=12, bold=True, color=BG))
    f.append(text(90, 168, "Фотодіод", size=10, color="#cbd5e0"))
    f.append(text(90, 195, "λ=940нм", size=9, color="#a0aec0"))

    # Стрілка світла
    f.append(arrow(10, 160, 45, 160, color=OPTICAL, sw=2.5))
    f.append(text(25, 145, "ІЧ", size=10, bold=True, color=OPTICAL))

    # Блок 1: Підсилювач TIA з АРП (AGC)
    f.append(arrow(130, 160, 165, 160, color=INK, sw=1.8))
    f.append(rect(170, 110, 110, 100, fill="#edf2f7", stroke=INK, sw=1.5, rx=6))
    f.append(text(225, 145, "Трансімпедансний", size=10, bold=True, color=INK))
    f.append(text(225, 160, "підсилювач", size=10, bold=True, color=INK))
    f.append(text(225, 175, "(TIA + AGC)", size=10, color=CARRIER))
    f.append(text(225, 195, "Авторегулювання", size=9, color=MUTED))

    # Блок 2: Смуговий фільтр BPF
    f.append(arrow(280, 160, 315, 160, color=INK, sw=1.8))
    f.append(rect(320, 110, 100, 100, fill="#e6fffa", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(370, 145, "Смуговий", size=11, bold=True, color=FIELD))
    f.append(text(370, 162, "фільтр (BPF)", size=11, bold=True, color=FIELD))
    f.append(text(370, 182, "f₀ = 38 кГц", size=10, bold=True, color=CARRIER))
    f.append(text(370, 198, "Q ≈ 10..15", size=9, color=MUTED))

    # Блок 3: Демодулятор / Детектор обвідної
    f.append(arrow(420, 160, 455, 160, color=INK, sw=1.8))
    f.append(rect(460, 110, 110, 100, fill="#fefcbf", stroke=SUN_NOISE, sw=1.5, rx=6))
    f.append(text(515, 145, "Демодулятор", size=11, bold=True, color=SUN_NOISE))
    f.append(text(515, 162, "Детектор", size=10, color=INK))
    f.append(text(515, 178, "обвідної", size=10, color=INK))
    f.append(text(515, 195, "Інтегратор", size=9, color=MUTED))

    # Блок 4: Тригер Шмітта та вихідний ключ
    f.append(arrow(570, 160, 605, 160, color=INK, sw=1.8))
    f.append(rect(610, 110, 110, 100, fill="#fed7d7", stroke=POS, sw=1.5, rx=6))
    f.append(text(665, 145, "Тригер Шмітта", size=10, bold=True, color=POS))
    f.append(text(665, 162, "Компаратор", size=10, color=INK))
    f.append(text(665, 180, "Open-Drain / NPN", size=9, color=MUTED))
    f.append(text(665, 195, "Active-LOW", size=9, bold=True, color=POS))

    # Вихідний сигнал OUT
    f.append(arrow(720, 160, 800, 160, color=POS, sw=2))
    f.append(circle(800, 160, 4, fill=POS, stroke=POS))
    f.append(text(770, 145, "OUT", size=11, bold=True, color=POS))
    f.append(text(765, 180, "(до MCU)", size=9, color=MUTED))

    # Виводи живлення
    f.append(line(225, 50, 225, 110, color=POS, sw=1.5))
    f.append(text(225, 42, "Vs (+3.3V / +5V)", size=10, bold=True, color=POS))
    f.append(line(515, 210, 515, 290, color=INK, sw=1.5))
    f.append(text(515, 302, "GND (Земля)", size=10, bold=True, color=INK))

    # Нижня картка
    f.append(fitbox(20, 315, 800, 50,
                    "Тракт TSOP повністю автономний: TIA перетворює фотострум у напругу, AGC регулює підсилення,\n"
                    "BPF виділяє частоту 38 кГц, а демодулятор видає чистий логічний рівень LOW під час прийому пачки.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "tsop-internal-block-diagram.svg"), W, H, *f)


# ── 3. Часові діаграми кодування протоколів NEC та RC-5 ───────────────────────
def fig_nec_rc5_pulse_encoding():
    W, H = 840, 430
    f = [text(W / 2, 26, "Формати кодування: NEC (Pulse Distance) та Philips RC-5 (Manchester)", size=15, bold=True)]

    # 1. Протокол NEC
    f.append(rect(20, 50, 800, 175, fill="#fdfefe", stroke=INK, sw=1.5, rx=8))
    f.append(text(120, 72, "Протокол NEC: Pulse Distance Modulation (38 кГц)", size=12, bold=True, color=CARRIER))

    # Лінія преамбули
    y0 = 130
    f.append(line(40, y0+20, 40, y0-20, color=CARRIER, sw=2))   # фронт
    f.append(line(40, y0-20, 140, y0-20, color=CARRIER, sw=2)) # 9 мс Burst
    f.append(line(140, y0-20, 140, y0+20, color=CARRIER, sw=2)) # спад
    f.append(line(140, y0+20, 200, y0+20, color=CARRIER, sw=2)) # 4.5 мс Space
    f.append(text(90, y0-26, "Пачка 9 мс (AGC)", size=9, bold=True, color=CARRIER))
    f.append(text(170, y0+35, "Пауза 4.5 мс", size=9, color=MUTED))

    # Біт '0': 560 мкс пачка + 560 мкс пауза (разом 1.125 мс)
    f.append(line(200, y0+20, 200, y0-20, color=FIELD, sw=2))
    f.append(line(200, y0-20, 230, y0-20, color=FIELD, sw=2)) # 560us
    f.append(line(230, y0-20, 230, y0+20, color=FIELD, sw=2))
    f.append(line(230, y0+20, 260, y0+20, color=FIELD, sw=2)) # 560us
    f.append(text(230, y0-26, "Біт '0'", size=11, bold=True, color=FIELD))
    f.append(text(230, y0+35, "1.125 мс", size=9, color=MUTED))

    # Біт '1': 560 мкс пачка + 1.69 мс пауза (разом 2.25 мс)
    f.append(line(260, y0+20, 260, y0-20, color=POS, sw=2))
    f.append(line(260, y0-20, 290, y0-20, color=POS, sw=2)) # 560us
    f.append(line(290, y0-20, 290, y0+20, color=POS, sw=2))
    f.append(line(290, y0+20, 380, y0+20, color=POS, sw=2)) # 1690us
    f.append(text(320, y0-26, "Біт '1'", size=11, bold=True, color=POS))
    f.append(text(335, y0+35, "2.25 мс (довга пауза 1.69 мс)", size=9, color=POS))

    # Структура кадру NEC (32 біти)
    f.append(rect(420, 95, 380, 50, fill="#edf2f7", stroke=INK, sw=1, rx=4))
    f.append(text(610, 112, "Кадр NEC: 8-біт Адреса + 8-біт ~Адреса + 8-біт Команда + 8-біт ~Команда", size=9, bold=True, color=INK))
    f.append(text(610, 132, "Контроль цілісності: побітове доповнення (Address ^ ~Address == 0xFF)", size=9, color=FIELD))

    f.append(text(410, 195, "Особливість NEC: значення біта кодується ТРИВАЛІСТЮ ПАУЗИ між пачками однакової ширини 560 мкс.", size=10, color=INK))

    # 2. Протокол Philips RC-5
    f.append(rect(20, 235, 800, 140, fill="#fcfdfd", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(130, 255, "Протокол Philips RC-5: Манчестерське кодування (36 кГц)", size=12, bold=True, color=FIELD))

    y1 = 300
    # Біт '1' у RC-5
    f.append(line(40, y1+15, 90, y1+15, color=FIELD, sw=2))
    f.append(line(90, y1+15, 90, y1-15, color=FIELD, sw=2))
    f.append(line(90, y1-15, 140, y1-15, color=FIELD, sw=2))
    f.append(line(140, y1-15, 140, y1+15, color=FIELD, sw=2))
    f.append(text(90, y1-22, "Біт '1' (Low→High)", size=10, bold=True, color=FIELD))
    f.append(text(90, y1+30, "1.778 мс (64 такти)", size=9, color=MUTED))

    # Біт '0' у RC-5
    f.append(line(160, y1+15, 160, y1-15, color=SUN_NOISE, sw=2))
    f.append(line(160, y1-15, 210, y1-15, color=SUN_NOISE, sw=2))
    f.append(line(210, y1-15, 210, y1+15, color=SUN_NOISE, sw=2))
    f.append(line(210, y1+15, 260, y1+15, color=SUN_NOISE, sw=2))
    f.append(text(210, y1-22, "Біт '0' (High→Low)", size=10, bold=True, color=SUN_NOISE))
    f.append(text(210, y1+30, "1.778 мс (64 такти)", size=9, color=MUTED))

    # Структура кадру RC-5 (14 бітів)
    f.append(rect(300, 275, 490, 45, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    f.append(text(545, 292, "Кадр RC-5 (14 бітів): S1 (1) + S2 (1/Cmd5) + Toggle (1) + Адреса (5) + Команда (6)", size=9, bold=True, color=INK))
    f.append(text(545, 308, "Toggle-біт інвертується при кожному новому натисканні клавіші", size=9, color=FIELD))

    f.append(text(410, 355, "Особливість RC-5: фіксований бітовий інтервал 1.778 мс, напрямок перепаду визначає значення біта.", size=10, color=INK))

    # Нижня плашка
    f.append(fitbox(20, 385, 800, 35,
                    "NEC кодує дані відстанню між імпульсами (PDM), а RC-5 — фазою перепаду в центрі бітового інтервалу (Манчестер).",
                    size=10, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "nec-rc5-pulse-encoding.svg"), W, H, *f)


# ── 4. Принципова схема передавача та приймача ────────────────────────────────
def fig_ir_transceiver_schematic():
    W, H = 840, 420
    f = [text(W / 2, 26, "Апаратна реалізація: вихідний ІЧ-драйвер та підключення TSOP", size=15, bold=True)]

    # Ліва частина: Передавач (ІЧ-світлодіод + транзисторний ключ)
    f.append(rect(20, 50, 390, 310, fill="#fdfefe", stroke=INK, sw=1.5, rx=8))
    f.append(text(215, 75, "ІЧ-передавач (імпульсний форсований струм)", size=12, bold=True, color=CARRIER))

    # Джерело VCC (+5V)
    f.append(line(215, 95, 215, 115, color=POS, sw=2))
    f.append(text(215, 90, "+5V (VCC)", size=10, bold=True, color=POS))

    # Обмежувальний резистор R_limit
    f.append(rect(205, 115, 20, 40, fill="#edf2f7", stroke=INK, sw=1.5, rx=2))
    f.append(text(245, 138, "R_lim = 4.7..10 Ом", size=10, bold=True, color=INK))

    # ІЧ-світлодіод
    f.append(line(215, 155, 215, 175, color=INK, sw=2))
    f.append(circle(215, 190, 14, fill="#f3e8ff", stroke=OPTICAL, sw=2))
    f.append(text(215, 194, "LED", size=9, bold=True, color=OPTICAL))
    f.append(text(265, 185, "940 нм", size=10, bold=True, color=OPTICAL))
    f.append(text(265, 200, "I_peak ≈ 300..500 мА", size=9, color=POS))

    # N-MOSFET / NPN ключ
    f.append(line(215, 205, 215, 235, color=INK, sw=2))
    f.append(rect(195, 235, 40, 32, fill="#fed7d7", stroke=POS, sw=1.5, rx=4))
    f.append(text(215, 250, "2N7002", size=9, bold=True, color=POS))
    f.append(text(215, 262, "N-MOSFET", size=9, color=INK))

    # Вхід від MCU (ШІМ 38 кГц)
    f.append(line(60, 250, 195, 250, color=CARRIER, sw=2))
    f.append(circle(60, 250, 3, fill=CARRIER, stroke=CARRIER))
    f.append(text(120, 240, "ШІМ 38 кГц (MCU)", size=9, bold=True, color=CARRIER))

    # Земля витоку
    f.append(line(215, 265, 215, 295, color=INK, sw=2))
    f.append(line(200, 295, 230, 295, color=INK, sw=2))
    f.append(line(205, 300, 225, 300, color=INK, sw=1.5))
    f.append(text(215, 315, "GND", size=9, color=INK))

    f.append(text(215, 345, "Шпаруватість 1/3 (33%) захищає LED від перегріву", size=9, bold=True, color=FIELD))

    # Права частина: Приймач TSOP з RC-фільтром
    f.append(rect(430, 50, 390, 310, fill="#fcfdfd", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(625, 75, "Підключення приймача TSOP4838", size=12, bold=True, color=FIELD))

    # Модуль TSOP
    f.append(rect(580, 140, 90, 120, fill=DARK_EPX, stroke=INK, sw=2, rx=6))
    f.append(text(625, 175, "TSOP4838", size=11, bold=True, color=BG))
    f.append(text(625, 195, "38 кГц", size=10, color="#a0aec0"))

    # Фільтр живлення RC
    f.append(line(460, 105, 520, 105, color=POS, sw=2))
    f.append(text(485, 95, "+3.3V/+5V", size=10, bold=True, color=POS))
    f.append(rect(520, 95, 35, 20, fill="#edf2f7", stroke=INK, sw=1.5, rx=2))
    f.append(text(537, 108, "100Ω", size=9, bold=True, color=INK))
    f.append(line(555, 105, 600, 105, color=POS, sw=2))
    f.append(line(600, 105, 600, 140, color=POS, sw=2)) # до піна Vs
    f.append(text(600, 152, "Vs", size=9, color=BG))

    # Конденсатор C_filt на землю
    f.append(line(575, 105, 575, 125, color=POS, sw=1.5))
    f.append(rect(565, 125, 20, 12, fill="#feb2b2", stroke=POS, sw=1, rx=2))
    f.append(text(545, 134, "4.7 мкФ", size=9, color=POS))
    f.append(line(575, 137, 575, 280, color=INK, sw=1.5))

    # Земляний пін GND
    f.append(line(625, 260, 625, 280, color=INK, sw=2))
    f.append(line(570, 280, 680, 280, color=INK, sw=2))
    f.append(text(625, 252, "GND", size=9, color=BG))
    f.append(text(625, 298, "GND", size=9, color=INK))

    # Вихідний пін OUT з Pull-Up
    f.append(line(650, 140, 650, 125, color=SIGNAL_HI, sw=2))
    f.append(text(650, 152, "OUT", size=9, color=BG))
    f.append(line(650, 125, 780, 125, color=SIGNAL_HI, sw=2))
    f.append(circle(780, 125, 3, fill=SIGNAL_HI, stroke=SIGNAL_HI))
    f.append(text(735, 115, "До Input Capture MCU", size=9, bold=True, color=SIGNAL_HI))

    # Підтягувальний резистор 10к
    f.append(line(700, 125, 700, 105, color=SIGNAL_HI, sw=1.5))
    f.append(rect(692, 85, 16, 20, fill="#edf2f7", stroke=INK, sw=1, rx=2))
    f.append(text(725, 97, "10k (Pull-up)", size=9, color=MUTED))
    f.append(line(700, 85, 700, 70, color=POS, sw=1.5))

    f.append(text(625, 335, "RC-ланка 100 Ом + 4.7 мкФ усуває збої TIA від просідання живлення", size=9, bold=True, color=FIELD))

    # Нижня картка
    f.append(fitbox(20, 370, 800, 40,
                    "Передавач форсує імпульсний струм діода до 500 мА завдяки малій шпаруватості (duty cycle 30%),\n"
                    "а приймач потребує локального RC-декаплінгу для захисту внутрішнього чутливого підсилювача.",
                    size=10, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "ir-transceiver-schematic.svg"), W, H, *f)


# ── 5. Просторова діаграма випромінювання Ламберта ────────────────────────────
def fig_lambertian_radiation_pattern():
    W, H = 840, 390
    f = [text(W / 2, 26, "Діаграма спрямованості ІЧ-випромінювача за законом Ламберта", size=15, bold=True)]

    cx, cy = 420, 240
    R = 170

    # Сітка полярних координат
    f.append(line(cx - R - 20, cy, cx + R + 20, cy, color=MUTED, sw=1)) # горизонталь 90 град
    f.append(line(cx, cy, cx, cy - R - 20, color=MUTED, sw=1))          # вертикаль 0 град

    for deg in [-60, -30, 30, 60]:
        rad = math.radians(deg)
        x2 = cx + (R + 15) * math.sin(rad)
        y2 = cy - (R + 15) * math.cos(rad)
        f.append(line(cx, cy, x2, y2, color="#e2e8f0", sw=1, dash="3,3"))
        f.append(text(x2, y2 - 5, "%d°" % deg, size=9, color=MUTED))

    f.append(text(cx, cy - R - 26, "0° (Головна оптична вісь)", size=10, bold=True, color=INK))

    # Концентричні кола інтенсивності 0.5 та 1.0
    f.append(circle(cx, cy, R * 0.5, fill="none", stroke="#cbd5e0", sw=1))
    f.append(text(cx + R * 0.5 + 15, cy - 6, "50%", size=9, color=MUTED))
    f.append(circle(cx, cy, R, fill="none", stroke="#cbd5e0", sw=1))
    f.append(text(cx + R + 15, cy - 6, "100%", size=9, color=MUTED))

    # 1. Широкий промінь (m = 1, cos(θ), θ_1/2 = ±60°)
    pts_m1 = []
    for a in range(-85, 86, 5):
        rad = math.radians(a)
        r_val = R * math.cos(rad)
        px = cx + r_val * math.sin(rad)
        py = cy - r_val * math.cos(rad)
        pts_m1.append((px, py))
    
    for i in range(len(pts_m1)-1):
        f.append(line(pts_m1[i][0], pts_m1[i][1], pts_m1[i+1][0], pts_m1[i+1][1], color=SUN_NOISE, sw=2))

    # 2. Вузький спрямований промінь (m = 10, cos^10(θ), θ_1/2 = ±20°)
    pts_m10 = []
    for a in range(-50, 51, 2):
        rad = math.radians(a)
        r_val = R * (math.cos(rad) ** 8)
        px = cx + r_val * math.sin(rad)
        py = cy - r_val * math.cos(rad)
        pts_m10.append((px, py))

    for i in range(len(pts_m10)-1):
        f.append(line(pts_m10[i][0], pts_m10[i][1], pts_m10[i+1][0], pts_m10[i+1][1], color=CARRIER, sw=2.5))

    # Розташування світлодіода в центрі
    f.append(circle(cx, cy, 6, fill=OPTICAL, stroke=INK, sw=1.5))
    f.append(text(cx, cy + 18, "ІЧ-світлодіод", size=10, bold=True, color=OPTICAL))

    # Легенда
    f.append(rect(30, 60, 240, 80, fill="#fdfefe", stroke=INK, sw=1, rx=4))
    f.append(line(45, 80, 85, 80, color=SUN_NOISE, sw=2))
    f.append(text(150, 84, "Дифузний діод (±60°)", size=10, bold=True, color=SUN_NOISE))
    f.append(line(45, 110, 85, 110, color=CARRIER, sw=2.5))
    f.append(text(155, 114, "Лінзований діод (±20°)", size=10, bold=True, color=CARRIER))
    f.append(text(150, 130, "Вища дальність по осі", size=9, color=MUTED))

    # Формула закону Ламберта праворуч
    f.append(rect(570, 60, 240, 80, fill="#fdfefe", stroke=FIELD, sw=1, rx=4))
    f.append(text(690, 80, "Закон Ламберта:", size=11, bold=True, color=FIELD))
    f.append(text(690, 100, "I_e(θ) = I_e(0) · cosᵐ(θ)", size=11, bold=True, color=INK))
    f.append(text(690, 120, "m = -ln(2) / ln(cos θ₁/₂)", size=9, color=MUTED))

    # Нижня плашка
    f.append(fitbox(20, 325, 800, 50,
                    "Лінзовані діоди з малим кутом половинної потужності (θ₁/₂ ≈ ±15..20°) концентрують потік уздовж осі,\n"
                    "забезпечуючи дальність понад 10–15 м, тоді як безлінзові світлодіоди дозволяють керувати відбитими променями.",
                    size=10, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "lambertian-radiation-pattern.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ir_optical_channel()
    fig_tsop_internal_block_diagram()
    fig_nec_rc5_pulse_encoding()
    fig_ir_transceiver_schematic()
    fig_lambertian_radiation_pattern()
    print("Фігури успішно згенеровано в ./img/")
