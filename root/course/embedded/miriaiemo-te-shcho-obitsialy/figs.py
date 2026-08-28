# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. current-profile-measurement: Динамічний профіль споживання струму ───────
def fig_current_profile():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 24, "Профіль динамічного споживання струму та схема вимірювання", size=15, bold=True, color=INK))

    # Ліва частина: Графік струму в часі
    p.append(rect(30, 50, 470, 390, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(265, 75, "Динамічний профіль струму i(t)", size=13, bold=True, color=INK))

    # Осі
    p.append(line(70, 390, 470, 390, color=LINE, sw=1.5)) # X axis (час)
    p.append(line(70, 390, 70, 95, color=LINE, sw=1.5))   # Y axis (струм)
    p.append(text(470, 408, "t, мс", size=11, bold=True, color=MUTED, anchor="end"))
    p.append(text(65, 90, "I, мА", size=11, bold=True, color=MUTED, anchor="end"))

    # Сітка та мітки Y
    y_levels = [(390, "0"), (330, "15 мкА"), (260, "10 мА"), (180, "40 мА"), (115, "100 мА")]
    for y_pos, label in y_levels:
        p.append(line(65, y_pos, 465, y_pos, color="#eaedf0", sw=1, dash="3,3"))
        p.append(text(62, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    # Крива струму (Sleep -> Wakeup -> Sensor Read -> Radio Tx -> Sleep)
    pts = [
        (70, 330), (120, 330),       # Deep Sleep (15 uA)
        (122, 230), (135, 230),      # Wakeup MCU clock (20 mA)
        (136, 280), (190, 280),      # Sensor Read I2C (8 mA)
        (192, 115), (280, 115),      # Radio TX burst (95 mA)
        (282, 245), (320, 245),      # Processing & Flash write (18 mA)
        (322, 330), (460, 330)       # Return to Deep Sleep (15 uA)
    ]
    path_d = ["M %.1f %.1f" % pts[0]]
    for x, y in pts[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), POS))

    # Заливка інтегралу енергії під TX сплеском
    tx_fill_pts = [(192, 390), (192, 115), (280, 115), (280, 390)]
    tx_d = "M %g %g L %g %g L %g %g L %g %g Z" % (tx_fill_pts[0][0], tx_fill_pts[0][1], tx_fill_pts[1][0], tx_fill_pts[1][1], tx_fill_pts[2][0], tx_fill_pts[2][1], tx_fill_pts[3][0], tx_fill_pts[3][1])
    p.append('<path d="%s" fill="#fdecea" opacity="0.6"/>' % tx_d)

    # Анотації фаз
    p.append(text(95, 355, "Deep Sleep", size=10, bold=True, color=NEG))
    p.append(text(130, 215, "Старт", size=10, bold=True, color=INK))
    p.append(text(163, 265, "Датчик", size=10, bold=True, color=INK))
    p.append(text(236, 103, "Радіоканал (TX)", size=11, bold=True, color=POS))
    p.append(text(301, 230, "Flash", size=10, bold=True, color=INK))
    p.append(text(390, 355, "Deep Sleep (15 мкА)", size=10, bold=True, color=NEG))

    # Права частина: Схема підключення вимірювального інструменту
    p.append(rect(520, 50, 390, 390, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(715, 75, "Методика вимірювання струму", size=13, bold=True, color=INK))

    # Блок 1: Помилка звичайного мультиметра (Burden Voltage)
    p.append(rect(535, 95, 360, 140, fill="#fff5f5", stroke=POS, sw=1.4, rx=5))
    p.append(text(545, 115, "Пастка DMM: Burden Voltage (падіння на шунті)", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(545, 136, "• Діапазон мкА: R_shunt = 1..10 кОм", size=10, color=INK, anchor="start"))
    p.append(text(545, 154, "• При стрибку до 50 мА: ΔV = 50 мА · 1 кОм = 50 В (відсічка!)", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(545, 172, "• Результат: Brown-Out Reset та постійний ребут МК", size=10, color=INK, anchor="start"))
    p.append(text(545, 190, "• Низька частота вибірки (3–10 Sps) втрачає піки", size=10, color=MUTED, anchor="start"))
    p.append(text(545, 218, "Звичайний мультиметр не придатний для DVT", size=10, bold=True, color=POS, anchor="start", italic=True))

    # Блок 2: Динамічний профілювальник (PPK2 / Joulescope)
    p.append(rect(535, 250, 360, 175, fill="#f4fcf6", stroke=FIELD, sw=1.4, rx=5))
    p.append(text(545, 270, "Профілювальник (PPK2 / Joulescope / SMU)", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(545, 292, "• Безрозривне автоперемикання шунтів (Auto-ranging)", size=10, color=INK, anchor="start"))
    p.append(text(545, 310, "• Частота дискретизації: 100 kSps .. 2 MSps", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(545, 328, "• Динамічний діапазон: від 100 нА до 500 мА", size=10, color=INK, anchor="start"))
    p.append(text(545, 346, "• 4-провідне підключення Кельвіна (Kelvin Sense)", size=10, color=INK, anchor="start"))
    p.append(text(545, 364, "• Інтегрування заряду (Кулони Q = ∫ i dt)", size=10, color=INK, anchor="start"))
    p.append(text(545, 395, "Оцінка життєвого циклу батареї на основі площі заряду", size=10, bold=True, color=FIELD, anchor="start", italic=True))

    p.append(text(W / 2, 465, "Вимірювання охоплює 6 порядків струму: від десятків наноамперів у сні до сотень міліамперів у TX",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "current-profile-measurement.svg"), W, H, *p,
           title="Профіль динамічного споживання струму та схема вимірювання")


# ── 2. power-rail-ripple-measurement: Вимірювання пульсацій живлення ─────────
def fig_ripple_measurement():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 24, "Методика вимірювання пульсацій та шуму шин живлення (Ripple & Noise)", size=15, bold=True, color=INK))

    # Ліва колонка: Неправильне підключення (Земляний крокодил)
    p.append(rect(30, 50, 425, 370, fill="#fdfefe", stroke=POS, sw=1.5, rx=6))
    p.append(text(242, 75, "НЕПРАВИЛЬНО: Земляний дріт («крокодил»)", size=12, bold=True, color=POS))

    # Схема антени
    p.append(rect(50, 95, 385, 125, fill="#fff5f5", stroke="#f5c6cb", sw=1.2, rx=4))
    p.append(text(65, 118, "Щуп осцилографа з довгим земляним дротом (12 см)", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(65, 138, "1. Довгий дріт утворює індуктивну петлю-антену", size=10, color=INK, anchor="start"))
    p.append(text(65, 156, "2. Ловить магнітне поле перемикання котушки DC-DC (B-field)", size=10, color=POS, anchor="start"))
    p.append(text(65, 174, "3. Власна паразитна індуктивність L_loop ≈ 100..150 нГн", size=10, color=INK, anchor="start"))
    p.append(text(65, 195, "Покази осцилографа: V_pp = 180..300 мВ (Хибний шум)", size=10, bold=True, color=POS, anchor="start"))

    # Осцилограма з хибним шумом
    p.append(rect(50, 235, 385, 165, fill="#1a1a1a", stroke="#333333", sw=1.5, rx=4))
    p.append(line(50, 317, 435, 317, color="#333333", sw=1, dash="4,4")) # середина
    p.append('<path d="M 60 317 Q 80 317 100 317 L 105 250 L 110 370 L 115 280 L 120 335 L 125 317 L 220 317 L 225 250 L 230 370 L 235 280 L 240 335 L 245 317 L 340 317 L 345 250 L 350 370 L 355 280 L 360 335 L 365 317 L 425 317" fill="none" stroke="#e74c3c" stroke-width="1.8"/>')
    p.append(text(242, 255, "Хибний дзвін від наведень на петлю щупа", size=10, color="#f1948a", bold=True))
    p.append(text(242, 385, "Показано 220 мВ замість реальних 15 мВ", size=10, color="#ffffff", bold=True))

    # Права колонка: Правильне підключення (Коротка пружинка)
    p.append(rect(485, 50, 425, 370, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(697, 75, "ПРАВИЛЬНО: Коротка земляна пружинка (Ground Spring)", size=12, bold=True, color=FIELD))

    # Схема правильного щупа
    p.append(rect(505, 95, 385, 125, fill="#f4fcf6", stroke="#c3e6cb", sw=1.2, rx=4))
    p.append(text(520, 118, "Знятий пластиковий ковпачок + коаксіальна пружина", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(520, 138, "1. Контакт безпосередньо на виводах вихідного MLCC", size=10, color=INK, anchor="start"))
    p.append(text(520, 156, "2. Площа контуру прямує до нуля (L_loop < 2 нГн)", size=10, color=FIELD, anchor="start"))
    p.append(text(520, 174, "3. Увімкнено апаратний фільтр смуги 20 МГц (BW Limit)", size=10, color=INK, anchor="start"))
    p.append(text(520, 195, "Покази осцилографа: V_pp = 12..18 мВ (Істинна пульсація)", size=10, bold=True, color=FIELD, anchor="start"))

    # Осцилограма з чистими пульсаціями
    p.append(rect(505, 235, 385, 165, fill="#1a1a1a", stroke="#333333", sw=1.5, rx=4))
    p.append(line(505, 317, 890, 317, color="#333333", sw=1, dash="4,4")) # середина
    p.append('<path d="M 515 317 L 545 305 L 575 329 L 605 305 L 635 329 L 665 305 L 695 329 L 725 305 L 755 329 L 785 305 L 815 329 L 845 305 L 875 329" fill="none" stroke="#2ecc71" stroke-width="2"/>')
    p.append(text(697, 255, "Істинна фундаментальна пульсація DC-DC (500 кГц)", size=10, color="#a9dfbf", bold=True))
    p.append(text(697, 385, "Реальний розмах пульсацій: 14 мВ (Норма ТЗ < 30 мВ)", size=10, color="#ffffff", bold=True))

    p.append(text(W / 2, 442, "Довгий земляний провід спотворює вимірювання в 10–20 разів через електромагнітне наведення",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "power-rail-ripple-measurement.svg"), W, H, *p,
           title="Методика вимірювання пульсацій та шуму шин живлення")


# ── 3. signal-integrity-spi-ringing: Дзвін на швидкісних шинах ────────────────
def fig_spi_ringing():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 24, "Цілісність сигналів шини SPI/QSPI: Дзвін, відбиття та демпфування", size=15, bold=True, color=INK))

    # Лівий блок: Без резистора (Unterminated / Fast Slew Rate)
    p.append(rect(30, 50, 425, 370, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(242, 75, "Без демпфування (Fast Slew Rate, R_s = 0)", size=12, bold=True, color=POS))

    # Осцилограма дзвону
    p.append(rect(50, 95, 385, 180, fill="#1a1a1a", stroke="#333333", sw=1.5, rx=4))
    # Рівні VDD (3.3V) та GND
    p.append(line(50, 150, 435, 150, color="#555555", sw=1, dash="3,3")) # 3.3V
    p.append(line(50, 235, 435, 235, color="#555555", sw=1, dash="3,3")) # 0V
    p.append(line(50, 192, 435, 192, color="#777777", sw=1, dash="2,2")) # Поріг V_ih / V_il (1.65V)
    p.append(text(55, 142, "VDD (3.3V)", size=9, color="#888888", anchor="start"))
    p.append(text(55, 228, "GND (0V)", size=9, color="#888888", anchor="start"))
    p.append(text(55, 185, "Поріг (1.65V)", size=9, color="#888888", anchor="start"))

    # Крива з Overshoot, Undershoot і хибним перетином порогу
    p.append('<path d="M 60 235 L 100 235 L 120 110 L 135 180 L 150 135 L 165 160 L 180 150 L 240 150 L 260 270 L 275 205 L 290 250 L 305 225 L 320 235 L 420 235" fill="none" stroke="#e74c3c" stroke-width="2.2"/>')

    # Анотація overshoot
    p.append(text(125, 105, "Overshoot: 4.2V (+0.9V)", size=10, bold=True, color="#f1948a"))
    p.append(text(265, 282, "Undershoot: -0.7V", size=10, bold=True, color="#f1948a"))
    p.append(text(142, 198, "Хибний глітч такту!", size=10, bold=True, color="#ffffff"))

    # Пояснення дефекту
    p.append(rect(50, 285, 385, 120, fill="#fff5f5", stroke="#f5c6cb", sw=1.2, rx=4))
    p.append(text(65, 305, "Причини та наслідки відсутності узгодження:", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(65, 323, "• Драйвер МК має R_out ≈ 15 Ом, імпеданс лінії Z_0 ≈ 60 Ом", size=9, color=INK, anchor="start"))
    p.append(text(65, 341, "• Відбиття сигналу від високого імпедансу приймача", size=9, color=INK, anchor="start"))
    p.append(text(65, 359, "• Відкриття вхідних ESD діодів чіпа (стрес кремнію)", size=9, color=POS, anchor="start"))
    p.append(text(65, 377, "• Помилкові тактові імпульси (False Clocking) на SCK SPI", size=9, bold=True, color=POS, anchor="start"))
    p.append(text(65, 395, "• Помилки зчитування QSPI Flash та спотворення даних", size=9, color=INK, anchor="start"))

    # Правий блок: З демпферним резистором (Series Damped R_s = 22..33 Ом)
    p.append(rect(485, 50, 425, 370, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(697, 75, "З послідовним резистором R_s = 27 Ом + Medium Slew", size=12, bold=True, color=FIELD))

    # Осцилограма чистого сигналу
    p.append(rect(505, 95, 385, 180, fill="#1a1a1a", stroke="#333333", sw=1.5, rx=4))
    p.append(line(505, 150, 890, 150, color="#555555", sw=1, dash="3,3")) # 3.3V
    p.append(line(505, 235, 890, 235, color="#555555", sw=1, dash="3,3")) # 0V
    p.append(line(505, 192, 890, 192, color="#777777", sw=1, dash="2,2")) # 1.65V
    p.append(text(510, 142, "VDD (3.3V)", size=9, color="#888888", anchor="start"))
    p.append(text(510, 228, "GND (0V)", size=9, color="#888888", anchor="start"))
    p.append(text(510, 185, "Поріг (1.65V)", size=9, color="#888888", anchor="start"))

    # Крива монотонного наростання
    p.append('<path d="M 515 235 L 555 235 Q 575 235 585 170 Q 595 150 610 150 L 700 150 Q 720 150 730 215 Q 740 235 755 235 L 875 235" fill="none" stroke="#2ecc71" stroke-width="2.2"/>')

    p.append(text(605, 138, "Монотонний фронт без дзвону", size=10, bold=True, color="#a9dfbf"))
    p.append(text(715, 255, "Плавний спад без викидів нижче GND", size=10, bold=True, color="#a9dfbf"))

    # Пояснення рішення
    p.append(rect(505, 285, 385, 120, fill="#f4fcf6", stroke="#c3e6cb", sw=1.2, rx=4))
    p.append(text(520, 305, "Фізика правильного узгодження лінії:", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(520, 323, "• R_out + R_s = 15 Ом + 27 Ом = 42 Ом ≈ Z_0 (лінія узгоджена)", size=9, bold=True, color=INK, anchor="start"))
    p.append(text(520, 341, "• Зниження швидкості виводу (GPIO Speed = Medium) обмежує dI/dt", size=9, color=INK, anchor="start"))
    p.append(text(520, 359, "• Резистор гасить енергію відбитої хвилі на виході джерела", size=9, color=INK, anchor="start"))
    p.append(text(520, 377, "• Setup Time та Hold Time гарантовано виконуються", size=9, bold=True, color=FIELD, anchor="start"))
    p.append(text(520, 395, "• Нульовий рівень бітових помилок на частотах до 80 МГц", size=9, color=INK, anchor="start"))

    p.append(text(W / 2, 442, "Послідовний демпфер 22–33 Ом біля виходу драйвера ліквідує дзвін та паразитно збуджені такти",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "signal-integrity-spi-ringing.svg"), W, H, *p,
           title="Цілісність сигналів шини SPI/QSPI")


# ── 4. thermal-drift-verification: Кліматичні випробування та дрейф ───────────
def fig_thermal_drift():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 24, "Кліматичні випробування в термокамері (-40..+85 °C) та температурний дрейф", size=15, bold=True, color=INK))

    # Верхній блок: Температурний профіль термокамери (Profile)
    p.append(rect(30, 48, 880, 165, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(50, 70, "Профіль випробувань у кліматичній камері (Thermal Cycling Profile)", size=11, bold=True, color=INK, anchor="start"))

    # Осі графіка температури
    p.append(line(80, 185, 870, 185, color=LINE, sw=1.2)) # t axis
    p.append(line(80, 185, 80, 80, color=LINE, sw=1.2))   # T axis

    p.append(text(75, 90, "+85 °C", size=10, bold=True, color=POS, anchor="end"))
    p.append(text(75, 135, "+25 °C", size=10, bold=True, color=MUTED, anchor="end"))
    p.append(text(75, 175, "−40 °C", size=10, bold=True, color=NEG, anchor="end"))
    p.append(text(870, 198, "Час (години)", size=10, color=MUTED, anchor="end"))

    # Сітка
    p.append(line(80, 90, 860, 90, color="#fdecea", sw=1, dash="2,2"))
    p.append(line(80, 135, 860, 135, color="#f4f6f8", sw=1, dash="2,2"))
    p.append(line(80, 175, 860, 175, color="#eaf0fd", sw=1, dash="2,2"))

    # Профіль зміни температури
    temp_pts = [
        (80, 135), (140, 135),       # Кімнатна +25°C
        (220, 175), (340, 175),      # Холодний soak -40°C (холодний старт)
        (460, 90), (580, 90),        # Гарячий soak +85°C (гарячий старт)
        (660, 175), (740, 175),      # Другий холодний цикл
        (820, 135), (860, 135)       # Повернення до +25°C
    ]
    p_d = ["M %g %g" % temp_pts[0]]
    for x, y in temp_pts[1:]:
        p_d.append("L %g %g" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(p_d), "#8e44ad"))

    # Маркери перевірок на графіку
    p.append(circle(280, 175, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    p.append(text(280, 163, "Холодний старт (−40 °C)", size=10, bold=True, color=NEG))

    p.append(circle(520, 90, 4, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(520, 78, "Гарячий старт (+85 °C)", size=10, bold=True, color=POS))

    p.append(text(700, 163, "Термоцикли (BGA/QFN стрес)", size=10, bold=True, color="#8e44ad"))

    # Нижня ліва частина: Дрейф кварцового резонатора
    p.append(rect(30, 225, 425, 215, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(242, 248, "Дрейф частоти RTC-кварцу 32.768 кГц", size=11, bold=True, color=INK))

    # Парабола кварцу: Δf/f = -0.04 * (T - 25)^2 ppm
    p.append(line(75, 400, 430, 400, color=LINE, sw=1.2)) # PPM 0
    p.append(line(245, 425, 245, 260, color=LINE, sw=1.2)) # T = +25°C

    p.append(text(245, 438, "+25 °C", size=10, bold=True, color=MUTED))
    p.append(text(95, 438, "−40 °C", size=10, bold=True, color=NEG))
    p.append(text(395, 438, "+85 °C", size=10, bold=True, color=POS))

    p.append(text(70, 400, "0 ppm", size=9, color=MUTED, anchor="end"))
    p.append(text(70, 335, "−60 ppm", size=9, color=MUTED, anchor="end"))
    p.append(text(70, 270, "−170 ppm", size=9, color=POS, anchor="end"))

    # Малювання параболи: від (95, 270) до вершини (245, 400) і до (395, 285)
    p.append('<path d="M 95 270 Q 245 440 395 285" fill="none" stroke="#2980b9" stroke-width="2.2"/>')
    # Написи розміщуємо повністю поза лінією параболи
    p.append(text(125, 262, "При −40 °C: −169 ppm", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(310, 275, "При +85 °C: −144 ppm", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(245, 380, "Вершина параболи (+25 °C)", size=10, color=FIELD))

    # Нижня права частина: Дрейф опорної напруги АЦП (VREF)
    p.append(rect(485, 225, 425, 215, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(697, 248, "Температурний дрейф опори АЦП (VREF)", size=11, bold=True, color=INK))

    p.append(rect(505, 265, 385, 75, fill="#fff5f5", stroke=POS, sw=1.2, rx=4))
    p.append(text(520, 285, "Внутрішній Bandgap МК (30..50 ppm/°C):", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(520, 303, "• ΔT = 60 °C → дрейф опори досягає ±0.3..0.5%", size=9, color=INK, anchor="start"))
    p.append(text(520, 321, "• 12-бітний АЦП втрачає до 15–20 LSB точності", size=9, bold=True, color=POS, anchor="start"))

    p.append(rect(505, 348, 385, 75, fill="#f4fcf6", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(520, 368, "Зовнішній прецизійний ІОН (2..5 ppm/°C):", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(520, 386, "• Дрейф у всьому діапазоні не перевищує 0.03%", size=9, color=INK, anchor="start"))
    p.append(text(520, 404, "• Гарантована абсолютна похибка < 1 LSB", size=9, bold=True, color=FIELD, anchor="start"))

    p.append(text(W / 2, 465, "Кліматичні тести виявляють крайові відмови: зрив генерації кварцу, дрейф АЦП та деградацію ESR батареї",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thermal-drift-verification.svg"), W, H, *p,
           title="Кліматичні випробування в термокамері та температурний дрейф")


if __name__ == "__main__":
    fig_current_profile()
    fig_ripple_measurement()
    fig_spi_ringing()
    fig_thermal_drift()
    print("All 4 figures generated successfully.")
