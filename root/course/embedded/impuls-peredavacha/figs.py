# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. power-delivery-network.svg: Еквівалентна схема мережі живлення ───────────
def fig_power_delivery_network():
    W, H = 940, 480
    p = []

    # Заголовок / область живлення
    p.append(rect(40, 50, 860, 390, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(60, 78, "Мережа розподілу живлення (PDN) автономного вузла", size=13, color=INK, anchor="start", bold=True))

    # Блок 1: Хімічне джерело (Батарея CR2032)
    p.append(rect(60, 110, 200, 290, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(160, 136, "Хімічне джерело", size=12, color=POS, bold=True))
    p.append(text(160, 154, "(CR2032, 3.0 В)", size=11, color=POS))

    # Елементи батареї: ЕРС + R_int
    p.append(circle(160, 210, 24, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(160, 206, "V_bat", size=11, color=POS, bold=True))
    p.append(text(160, 222, "3.0 В", size=10, color=MUTED))

    p.append(line(160, 234, 160, 260, color=POS, sw=1.8))
    
    # Резистор R_int
    p.append(rect(142, 260, 36, 60, fill="#ffffff", stroke=POS, sw=1.5, rx=2))
    p.append(text(160, 288, "R_int", size=11, color=POS, bold=True))
    p.append(text(160, 306, "10-40 Ω", size=10, color=POS))
    p.append(text(160, 355, "Високий опір", size=10, color=MUTED))
    p.append(text(160, 372, "деградує на холоді", size=10, color=MUTED))

    # Шина живлення V_bus (верхня) і GND (нижня)
    p.append(line(160, 186, 160, 170, color=POS, sw=1.8))
    p.append(line(160, 170, 310, 170, color=POS, sw=2.2))

    p.append(line(160, 320, 160, 380, color=NEG, sw=1.8))
    p.append(line(160, 380, 840, 380, color=NEG, sw=2.2))

    # Паразитна індуктивність та опір доріжок
    p.append(rect(310, 152, 90, 36, fill="#ffffff", stroke=LINE, sw=1.4, rx=3))
    p.append(text(355, 174, "R_trace, L_tr", size=10, color=INK, bold=True))
    p.append(line(400, 170, 480, 170, color=POS, sw=2.2))

    # Блок 2: Буферний конденсатор C_bulk
    p.append(rect(430, 110, 140, 290, fill="#eef7ee", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(500, 136, "Буферна ємність", size=12, color=FIELD, bold=True))
    p.append(text(500, 154, "(C_bulk + ESR)", size=11, color=FIELD))

    # Схема конденсатора з ESR
    p.append(line(500, 170, 500, 205, color=FIELD, sw=1.8))
    p.append(rect(486, 205, 28, 45, fill="#ffffff", stroke=FIELD, sw=1.4, rx=2))
    p.append(text(500, 226, "ESR", size=10, color=FIELD, bold=True))
    p.append(text(500, 240, "<50 mΩ", size=9, color=FIELD))

    p.append(line(500, 250, 500, 275, color=FIELD, sw=1.8))
    # Обкладки конденсатора
    p.append(line(482, 275, 518, 275, color=FIELD, sw=2.5))
    p.append(line(482, 283, 518, 283, color=FIELD, sw=2.5))
    p.append(text(500, 308, "C_bulk", size=11, color=FIELD, bold=True))
    p.append(text(500, 324, "100-470 µF", size=10, color=FIELD))
    p.append(line(500, 283, 500, 380, color=NEG, sw=1.8))

    p.append(line(480, 170, 620, 170, color=POS, sw=2.2))

    # Блок 3: Мікроконтролер (MCU)
    p.append(rect(610, 110, 120, 290, fill="#f0f4f8", stroke="#4b6b94", sw=1.5, rx=6))
    p.append(text(670, 136, "МК (ядро)", size=12, color="#4b6b94", bold=True))
    p.append(text(670, 154, "I_mcu = 15 мА", size=10, color=MUTED))
    p.append(line(670, 170, 670, 210, color="#4b6b94", sw=1.8))
    
    p.append(rect(635, 210, 70, 80, fill="#ffffff", stroke="#4b6b94", sw=1.4, rx=4))
    p.append(text(670, 240, "BOR", size=11, color=POS, bold=True))
    p.append(text(670, 258, "Детектор", size=9, color=MUTED))
    p.append(text(670, 274, "V_th=2.0 В", size=9, color=POS, bold=True))
    p.append(line(670, 290, 670, 380, color=NEG, sw=1.8))

    # Лінія далі до радіомодуля
    p.append(line(670, 170, 760, 170, color=POS, sw=2.2))

    # Блок 4: Радіомодуль (PA)
    p.append(rect(750, 110, 130, 290, fill="#fff8ee", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(815, 136, "Радіо PA", size=12, color="#d97706", bold=True))
    p.append(text(815, 154, "SX1262 / nRF24", size=10, color=MUTED))

    # Ключ передавача RF Switch
    p.append(line(815, 170, 815, 205, color="#d97706", sw=1.8))
    p.append(line(815, 205, 802, 230, color=POS, sw=2.0))
    p.append(circle(815, 236, 3, fill=POS, stroke=POS, sw=1))
    p.append(text(856, 218, "TX ON", size=9, color=POS, bold=True))

    p.append(rect(775, 244, 80, 56, fill="#ffffff", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(815, 266, "Стрибок струму", size=9, color="#d97706"))
    p.append(text(815, 284, "120 мА / 10 мс", size=10, color=POS, bold=True))

    p.append(line(815, 300, 815, 380, color=NEG, sw=1.8))

    # Підписи шин
    p.append(text(440, 160, "V_DD (Шина живлення)", size=10, color=POS, bold=True))
    p.append(text(440, 396, "GND (Спільна шина повернення струму)", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "power-delivery-network.svg"), W, H, *p,
           title="Еквівалентна схема мережі живлення та імпульсного навантаження")


# ── 2. transient-pulse-drop.svg: Осцилограма струму та провалу напруги ─────────
def fig_transient_pulse_drop():
    W, H = 940, 520
    p = []

    p.append(rect(30, 30, 880, 460, fill="#ffffff", stroke="#e1e4e8", sw=1.5, rx=8))
    p.append(text(50, 58, "Динаміка провалу напруги шини під час 10-мс імпульсу передавача (120 мА)", size=13, color=INK, anchor="start", bold=True))

    # Вісь часу (спільна горизонтальна)
    t_start, t_end = 120, 840
    p.append(line(t_start, 240, t_end, 240, color="#8c959f", sw=1.2))
    p.append(line(t_start, 440, t_end, 440, color="#8c959f", sw=1.2))

    # Вертикальні осі
    p.append(line(t_start, 80, t_start, 240, color="#8c959f", sw=1.2))
    p.append(line(t_start, 280, t_start, 440, color="#8c959f", sw=1.2))

    # Позначки струму
    p.append(text(110, 244, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(110, 210, "15 мА", size=10, color=MUTED, anchor="end"))
    p.append(text(110, 115, "120 мА", size=11, color=POS, anchor="end", bold=True))
    p.append(text(75, 95, "Струм I(t)", size=11, color=POS, bold=True))

    # Позначки напруги
    p.append(text(110, 444, "0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(110, 375, "2.0 В (V_BOR)", size=10, color=POS, anchor="end", bold=True))
    p.append(text(110, 340, "2.4 В", size=10, color=MUTED, anchor="end"))
    p.append(text(110, 295, "3.0 В", size=11, color=FIELD, anchor="end", bold=True))
    p.append(text(75, 295, "Напруга V(t)", size=11, color=INK, bold=True))

    # Фази часу
    p.append(line(260, 80, 260, 440, color="#e1e4e8", sw=1.0, dash="4,4"))
    p.append(line(360, 80, 360, 440, color="#e1e4e8", sw=1.0, dash="4,4"))
    p.append(line(620, 80, 620, 440, color="#e1e4e8", sw=1.0, dash="4,4"))

    p.append(text(210, 72, "Сон (10 мкА)", size=10, color=MUTED))
    p.append(text(310, 72, "МК активний", size=10, color=MUTED))
    p.append(text(490, 72, "Імпульс передачі TX (10 мс)", size=11, color=POS, bold=True))
    p.append(text(720, 72, "Відновлення заряду", size=10, color=FIELD))

    # Графік струму I(t)
    p.append('<path d="M 120,239 L 260,239 L 260,210 L 360,210 L 361,115 L 620,115 L 621,210 L 670,210 L 670,239 L 840,239" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)

    # Поріг BOR (горизонтальна штрихова)
    p.append(line(120, 375, 840, 375, color=POS, sw=1.5, dash="6,4"))
    p.append(text(845, 375, "Поріг BOR (2.0 В)", size=10, color=POS, anchor="start", bold=True))

    # Крива 1: Без буферної ємності (аварійний провал і ресет) - червона
    p.append('<path d="M 120,295 L 260,295 L 260,305 L 360,305 L 361,415 L 380,415 L 381,298 L 840,298" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="3,3"/>' % POS)
    p.append(text(410, 428, "Без C_bulk: провал до 1.5 В -> Ресет МК!", size=10, color=POS, bold=True))

    # Крива 2: З розрахованою ємністю C_bulk = 330 мкФ (безпечна робота) - зелена
    p.append('<path d="M 120,295 L 260,295 L 260,302 L 360,302 L 361,315 L 620,345 L 621,332 Q 680,300 820,295" fill="none" stroke="%s" stroke-width="2.6"/>' % FIELD)
    
    # Виноски на графіку напруги
    p.append(text(380, 310, "ΔV_esr = I·ESR", size=9, color=FIELD, bold=True))
    p.append(text(540, 335, "ΔV_cap = (I·Δt)/C", size=10, color=FIELD, bold=True))
    p.append(text(720, 316, "Заряд: τ = R_int · C", size=10, color=FIELD))

    # Пояснення запасу
    p.append(rect(450, 455, 380, 26, fill="#f4fbf5", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(640, 472, "Запас до BOR при C=330 мкФ: 2.4 В > 2.0 В (безпечно)", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "transient-pulse-drop.svg"), W, H, *p,
           title="Осцилограма стрибка струму та реакції напруги шини живлення")


# ── 3. brownout-bootloop.svg: Діаграма пастки циклічного перезавантаження ──────
def fig_brownout_bootloop():
    W, H = 940, 460
    p = []

    p.append(rect(30, 30, 880, 400, fill="#ffffff", stroke="#e1e4e8", sw=1.5, rx=8))
    p.append(text(50, 58, "Анатомія пастки циклічного перезавантаження (Brown-out Bootloop)", size=13, color=INK, anchor="start", bold=True))

    # 4 основні вузли кільця циклу
    # Вузол 1: Сон і пробудження (ліворуч вгорі)
    b1, w1, h1 = textbox(210, 130, "1. Пробудження зі сну\n• I = 10 мкА -> 15 мА\n• Батарея має 3.0 В (відпочила)", size=11, pad=10, fill="#f0f4f8", stroke="#4b6b94", sw=1.5)
    p.append(b1)

    # Вузол 2: Підготовка та запуск TX (праворуч вгорі)
    b2, w2, h2 = textbox(720, 130, "2. Запуск радіопередавача\n• I_tx = 120 мА за 2 мкс\n• Стрибок навантаження у 8000 разів", size=11, pad=10, fill="#fff8ee", stroke="#d97706", sw=1.5)
    p.append(b2)

    # Вузол 3: Аварійне просідання напруги (праворуч внизу)
    b3, w3, h3 = textbox(720, 310, "3. Провал напруги та BOR\n• ΔV = 120 мА · 25 Ом = 3.0 В\n• V_DD падає до 1.2 В < 2.0 В\n• BOR апаратно скидає ядро", size=11, pad=10, fill="#fdf2f2", stroke=POS, sw=1.8)
    p.append(b3)

    # Вузол 4: Скидання периферії та підйом напруги (ліворуч внизу)
    b4, w4, h4 = textbox(210, 310, "4. Скидання TX і рестарт\n• Радіо вимкнулось, I падає\n• Напруга повертається до 3.0 В\n• МК знову починає Bootloader", size=11, pad=10, fill="#fdf2f2", stroke=POS, sw=1.5)
    p.append(b4)

    # Стрілки по колу
    p.append(arrow(330, 130, 580, 130, color="#d97706", sw=2.2))
    p.append(text(455, 118, "Зчитування датчика, старт TX", size=10, color="#d97706", bold=True))

    p.append(arrow(720, 185, 720, 250, color=POS, sw=2.2))
    p.append(text(795, 220, "2..5 мкс", size=10, color=POS, bold=True))

    p.append(arrow(580, 310, 340, 310, color=POS, sw=2.2))
    p.append(text(460, 298, "Апаратний скид (Reset Vector)", size=10, color=POS, bold=True))

    p.append(arrow(210, 250, 210, 185, color=POS, sw=2.2))
    p.append(text(140, 220, "Повторний запуск", size=10, color=POS, bold=True))

    # Центральна плашка наслідків
    p.append(rect(360, 175, 200, 80, fill="#2b2b2b", stroke="#000000", sw=1.5, rx=6))
    p.append(text(460, 200, "НАСЛІДОК ПАСТКИ:", size=11, color="#f87171", bold=True))
    p.append(text(460, 220, "• Пакет не відправлено", size=10, color="#ffffff"))
    p.append(text(460, 238, "• Батарея виснажена за добу", size=10, color="#ffffff"))

    render(os.path.join(OUT, "brownout-bootloop.svg"), W, H, *p,
           title="Нескінченний цикл перезавантаження через скид по напрузі (Brown-out)")


# ── 4. dc-bias-derating.svg: Деградація ємності керамічних конденсаторів ───────
def fig_dc_bias_derating():
    W, H = 940, 480
    p = []

    p.append(rect(30, 30, 880, 420, fill="#ffffff", stroke="#e1e4e8", sw=1.5, rx=8))
    p.append(text(50, 58, "Ефект зміщення постійною напругою (DC Bias): втрата ємності MLCC кераміки", size=13, color=INK, anchor="start", bold=True))

    # Графік: X = Напруга (0..16 В), Y = Залишкова ємність (0..100 %)
    gx, gy, gw, gh = 100, 100, 580, 280

    # Осі
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color="#8c959f", sw=1.4))
    p.append(line(gx, gy, gx, gy + gh, color="#8c959f", sw=1.4))

    # Сітка та підписи по Y (0, 20, 40, 60, 80, 100 %)
    for pct in range(0, 101, 20):
        y = gy + gh - (pct / 100.0) * gh
        p.append(line(gx, y, gx + gw, y, color="#f0f2f5", sw=1.0))
        p.append(text(gx - 10, y + 4, "%d%%" % pct, size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 45, gy + gh / 2, "Залишкова ємність (%)", size=11, color=INK, bold=True))

    # Сітка та підписи по X (0, 2, 3.3, 6.3, 10, 16 В)
    voltages = [(0, 0), (2, 2), (3.3, 3.3), (6.3, 6.3), (10, 10), (16, 16)]
    for v_val, v_label in voltages:
        x = gx + (v_val / 16.0) * gw
        p.append(line(x, gy, x, gy + gh, color="#f0f2f5", sw=1.0))
        p.append(text(x, gy + gh + 18, "%.1f В" % v_val if v_val == 3.3 or v_val == 6.3 else "%d В" % v_val, size=10, color=MUTED))
    p.append(text(gx + gw / 2, gy + gh + 42, "Прикладена робоча напруга шини V_DD (В)", size=11, color=INK, bold=True))

    # Робоча точка 3.3 В (штрихова лінія)
    x_3v3 = gx + (3.3 / 16.0) * gw
    p.append(line(x_3v3, gy, x_3v3, gy + gh, color=POS, sw=1.2, dash="4,4"))
    p.append(text(x_3v3, gy - 10, "Шина 3.3 В", size=10, color=POS, bold=True))

    # Криві:
    # 1. C0G / NP0 (Ідеальна пряма 100%)
    p.append(line(gx, gy, gx + gw, gy, color=FIELD, sw=2.5))

    # 2. X7R 1206 (10 мкФ 16В) - падіння до 75% при 3.3В, 50% при 16В
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (gx, gy, gx + 200, gy + 50, gx + gw, gy + 140, "#2457d6"))

    # 3. X5R 0805 (10 мкФ 6.3В) - падіння до 45% при 3.3В, 20% при 6.3В
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (gx, gy, gx + 150, gy + 140, gx + gw, gy + 240, "#d97706"))

    # 4. X5R 0402 (10 мкФ 6.3В) - критичне падіння до 20% при 3.3В!
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (gx, gy, gx + 80, gy + 210, gx + gw, gy + 265, POS))

    # Легенда праворуч
    lx = 710
    p.append(rect(lx, 110, 190, 250, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(lx + 95, 132, "Типи діелектриків", size=11, color=INK, bold=True))

    p.append(line(lx + 15, 160, lx + 45, 160, color=FIELD, sw=2.5))
    p.append(text(lx + 55, 164, "C0G / NP0 (100%)", size=10, color=FIELD, anchor="start", bold=True))

    p.append(line(lx + 15, 200, lx + 45, 200, color="#2457d6", sw=2.5))
    p.append(text(lx + 55, 204, "X7R (1206, 16 В)", size=10, color="#2457d6", anchor="start", bold=True))
    p.append(text(lx + 55, 218, "Залишок: ~75% при 3.3 В", size=9, color=MUTED, anchor="start"))

    p.append(line(lx + 15, 250, lx + 45, 250, color="#d97706", sw=2.5))
    p.append(text(lx + 55, 254, "X5R (0805, 6.3 В)", size=10, color="#d97706", anchor="start", bold=True))
    p.append(text(lx + 55, 268, "Залишок: ~45% при 3.3 В", size=9, color=MUTED, anchor="start"))

    p.append(line(lx + 15, 300, lx + 45, 300, color=POS, sw=2.5))
    p.append(text(lx + 55, 304, "X5R (0402, 6.3 В)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(lx + 55, 318, "Залишок: ~20% при 3.3 В!", size=9, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "dc-bias-derating.svg"), W, H, *p,
           title="Залежність ємності керамічних конденсаторів від постійної напруги зміщення")


# ── 5. software-mitigation-flow.svg: Комплекс програмних технік ───────────────
def fig_software_mitigation_flow():
    W, H = 940, 440
    p = []

    p.append(rect(30, 30, 880, 380, fill="#ffffff", stroke="#e1e4e8", sw=1.5, rx=8))
    p.append(text(50, 58, "Послідовність безпечної передачі пакета: програмне збереження шини живлення", size=13, color=INK, anchor="start", bold=True))

    # 4 етапи послідовності
    steps = [
        ("1. Аудит живлення", "Pre-TX Check", "• Зчитування V_bat під навантаженням\n• Якщо V < 2.5 В -> відкласти або зменшити TX\n• Перевірка BOR прапорця в RCC/PMU", "#eef4fb", "#3b82f6"),
        ("2. Зниження F_cpu", "Clock Throttling", "• Зниження CPU: 80 МГц -> 2 МГц\n• Економія: мінус 15-25 мА струму ядра\n• Вивільнення заряду C_bulk для PA", "#f0fdf4", FIELD),
        ("3. Плавний пуск PA", "Power Ramping", "• PA Ramp Time: 10..40 мкс\n• Зниження di/dt індуктивного удару\n• Ступінчастий підйом вихідної потужності", "#fffbeb", "#d97706"),
        ("4. Відновлення", "Post-TX Recharge", "• Вимкнення PA -> Сон ядра\n• Пауза t_recharge = 3..5·τ\n• Повний заряд C_bulk до наступного TX", "#fdf2f2", POS)
    ]

    x_start = 55
    card_w = 195
    gap = 25

    for i, (title_s, sub_s, desc_s, fill_c, stroke_c) in enumerate(steps):
        cx = x_start + i * (card_w + gap)
        # Картка
        p.append(rect(cx, 100, card_w, 260, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(cx + card_w / 2, 126, title_s, size=11, color=stroke_c, bold=True))
        p.append(text(cx + card_w / 2, 144, sub_s, size=10, color=MUTED))

        p.append(line(cx + 15, 158, cx + card_w - 15, 158, color=stroke_c, sw=1.0))

        # Опис
        lines = desc_s.split("\n")
        for j, ln in enumerate(lines):
            p.append(text(cx + 12, 185 + j * 24, ln, size=9.5, color=INK, anchor="start"))

        # Стрілка між кроками
        if i < 3:
            ax = cx + card_w + 3
            p.append(arrow(ax, 230, ax + gap - 6, 230, color="#94a3b8", sw=2.0))

    # Нижня часова шкала економії струму
    p.append(rect(55, 375, 830, 25, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(470, 392, "Сумарний ефект: піковий струм плати зменшено на 20-30 мА, виключено індуктивні викиди L·di/dt та усунуто Bootloop", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "software-mitigation-flow.svg"), W, H, *p,
           title="Покроковий алгоритм безпечної передачі радіопакета в умовах слабкого живлення")


if __name__ == "__main__":
    fig_power_delivery_network()
    fig_transient_pulse_drop()
    fig_brownout_bootloop()
    fig_dc_bias_derating()
    fig_software_mitigation_flow()
    print("All 5 figures generated successfully.")
