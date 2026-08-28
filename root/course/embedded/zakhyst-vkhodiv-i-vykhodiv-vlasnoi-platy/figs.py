# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. esd-tvs-placement-flowthrough: Розміщення TVS-діодів ──────────────────
def fig_esd_tvs_placement_flowthrough():
    W, H = 920, 440
    p = []

    # Ліва половина: ПОГАНО (довгі stubs, далеко від роз'єму)
    p.append(rect(30, 45, 410, 320, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(235, 75, "ПОГАНО: TVS далеко, довгі відводи (stubs)", size=13, color=POS, bold=True))

    # Роз'єм USB ліворуч
    p.append(rect(50, 110, 65, 120, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(82, 160, "USB", size=12, color=INK, bold=True))
    p.append(text(82, 180, "Port", size=10.5, color=MUTED))

    # Мікроконтролер праворуч
    p.append(rect(340, 110, 80, 120, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(380, 160, "MCU /", size=12, color=INK, bold=True))
    p.append(text(380, 180, "PHY", size=12, color=INK, bold=True))

    # Сигнальні лінії D+ / D-
    p.append(line(115, 145, 340, 145, color=POS, sw=2.5))
    p.append(line(115, 195, 340, 195, color=POS, sw=2.5))
    p.append(text(220, 135, "D+ (швидкісний сигнал)", size=10, color=POS))
    p.append(text(220, 185, "D−", size=10, color=POS))

    # TVS зміщений вниз із довгими відводами (stubs)
    p.append(line(240, 145, 240, 260, color=POS, sw=2, dash="3 3"))
    p.append(line(260, 195, 260, 260, color=POS, sw=2, dash="3 3"))
    p.append(rect(220, 260, 60, 50, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(250, 285, "TVS", size=11, color=INK, bold=True))
    p.append(text(250, 300, "Array", size=9.5, color=MUTED))

    # Земляний провід від TVS
    p.append(line(250, 310, 250, 340, color=LINE, sw=2))
    p.append(line(235, 340, 265, 340, color=LINE, sw=2))
    p.append(line(240, 345, 260, 345, color=LINE, sw=1.5))
    p.append(line(245, 350, 255, 350, color=LINE, sw=1))

    # Пояснення паразитної індуктивності
    p.append(text(300, 245, "L_stub ≈ 5–10 нГн", size=10.5, color=POS, bold=True))
    p.append(text(300, 260, "V_peak = L · (di/dt)", size=10.5, color=POS))

    b1, _, _ = textbox(235, 335, "Імпульс ESD (di/dt = 30 А / 1 нс) створює сплеск у сотні вольт\nна індуктивності відводів і пробиває кристал MCU.",
                       size=10.5, fill="#ffffff", stroke=MUTED)
    p.append(b1)

    # Права половина: ДОБРЕ (flow-through трасування прямо крізь TVS біля роз'єму)
    p.append(rect(480, 45, 410, 320, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(685, 75, "ДОБРЕ: TVS на роз'ємі, Flow-Through монтаж", size=13, color=FIELD, bold=True))

    # Роз'єм USB ліворуч
    p.append(rect(500, 110, 65, 120, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(532, 160, "USB", size=12, color=INK, bold=True))
    p.append(text(532, 180, "Port", size=10.5, color=MUTED))

    # TVS упритул до роз'єму з прохідними майданчиками (flow-through)
    p.append(rect(590, 125, 60, 90, fill="#eafaf1", stroke=FIELD, sw=2))
    p.append(text(620, 165, "TVS", size=12, color=FIELD, bold=True))
    p.append(text(620, 180, "< 0.5 pF", size=10, color=FIELD))

    # Пряме коротке заземлення на шасі / суцільний GND
    p.append(line(620, 215, 620, 255, color=FIELD, sw=3))
    p.append(circle(620, 265, 8, fill="#ffffff", stroke=FIELD, sw=2))
    p.append(text(655, 268, "GND via", size=10, color=FIELD, bold=True))

    # Мікроконтролер праворуч
    p.append(rect(790, 110, 80, 120, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(830, 160, "MCU /", size=12, color=INK, bold=True))
    p.append(text(830, 180, "PHY", size=12, color=INK, bold=True))

    # Сигнальні лінії проходять прямо КРІЗЬ контактні майданчики TVS (0 мм stub)
    p.append(line(565, 145, 590, 145, color=FIELD, sw=3))
    p.append(line(650, 145, 790, 145, color=FIELD, sw=2.5))
    p.append(line(565, 195, 590, 195, color=FIELD, sw=3))
    p.append(line(650, 195, 790, 195, color=FIELD, sw=2.5))

    p.append(text(720, 135, "Чистий сигнал D+", size=10, color=FIELD))
    p.append(text(720, 185, "D−", size=10, color=FIELD))
    p.append(text(620, 112, "0 мм відвід (Flow-through)", size=10, color=FIELD, bold=True))

    b2, _, _ = textbox(685, 335, "Розряд скидається в землю ще на вході в плату.\nВідсутність відводів виключає індуктивний викид напруги.",
                       size=10.5, fill="#ffffff", stroke=MUTED)
    p.append(b2)

    # Загальний висновок унизу
    b_bot, _, _ = textbox(W / 2, 400,
                          "Золоте правило ESD-захисту: TVS-збірка монтується впритул до пінів роз'єму. Траса сигналу проходить прямо крізь\n"
                          "майданчики компонента без Т-подібних відводів (stubs), а вивід GND з'єднується з полігоном мінімальною петлею.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "esd-tvs-placement-flowthrough.svg"), W, H, *p,
           title="Розміщення TVS-діодів: трасування швидкісних ліній та шлях розряду")


# ── 2. gpio-clamping-diodes-mechanism: Захист входу GPIO/ADC ─────────────────
def fig_gpio_clamping_diodes_mechanism():
    W, H = 940, 440
    p = []

    # Текстоліт / контур схеми
    p.append(rect(30, 45, 880, 330, fill="#fdfcf7", stroke="#d1d5db", sw=1.5, rx=8))

    # Зона зовнішнього захисту (на платі)
    p.append(rect(50, 70, 400, 285, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(250, 95, "Зовнішній захист на платі (Off-Chip)", size=12.5, color=NEG, bold=True))

    # Зона кристала MCU (внутрішня структура)
    p.append(rect(480, 70, 410, 285, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(685, 95, "Внутрішня структура мікроконтролера (On-Chip)", size=12.5, color=POS, bold=True))

    # Вхідна клема (Vin)
    p.append(circle(75, 200, 7, fill=POS, stroke=INK, sw=1.5))
    p.append(text(75, 180, "Вхідний пін", size=11, color=POS, bold=True))
    p.append(text(75, 225, "Vin (+12 В аварія)", size=9.5, color=POS))

    # Послідовний резистор обмеження струму R_limit
    p.append(line(82, 200, 130, 200, color=INK, sw=2))
    p.append(rect(130, 188, 50, 24, fill="#ffffff", stroke=INK, sw=1.5))
    p.append(text(155, 204, "1 кОм", size=10, color=INK, bold=True))
    p.append(text(155, 178, "R_limit", size=10.5, color=INK, bold=True))
    p.append(line(180, 200, 240, 200, color=INK, sw=2))

    # Вузол clamping діодів (240, 200)
    p.append(circle(240, 200, 4, fill=INK, stroke=INK))

    # Зовнішній діод Шотткі на VDD (+3.3 В)
    p.append(line(240, 200, 240, 160, color=NEG, sw=2))
    p.append('<polygon points="230,160 250,160 240,140" fill="#2457d6" stroke="#2457d6" stroke-width="1.5"/>')
    p.append(line(230, 140, 250, 140, color=NEG, sw=2))
    p.append(line(230, 140, 230, 145, color=NEG, sw=1.5))
    p.append(line(250, 140, 250, 135, color=NEG, sw=1.5))
    p.append(line(240, 140, 240, 120, color=NEG, sw=2))
    p.append(line(220, 120, 260, 120, color=NEG, sw=2.5))
    p.append(text(240, 112, "VDD (+3.3 В)", size=10, color=NEG, bold=True))
    p.append(text(310, 150, "BAT54S (Шотткі)", size=10, color=NEG, bold=True))
    p.append(text(310, 165, "Vf ≈ 0.25–0.30 В", size=9.5, color=NEG))

    # Зовнішній діод Шотткі на GND
    p.append(line(240, 200, 240, 240, color=NEG, sw=2))
    p.append('<polygon points="230,260 250,260 240,240" fill="#2457d6" stroke="#2457d6" stroke-width="1.5"/>')
    p.append(line(230, 240, 250, 240, color=NEG, sw=2))
    p.append(line(230, 240, 230, 245, color=NEG, sw=1.5))
    p.append(line(250, 240, 250, 235, color=NEG, sw=1.5))
    p.append(line(240, 260, 240, 290, color=NEG, sw=2))
    p.append(line(225, 290, 255, 290, color=NEG, sw=2))
    p.append(line(230, 294, 250, 294, color=NEG, sw=1.5))
    p.append(line(235, 298, 245, 298, color=NEG, sw=1))
    p.append(text(240, 312, "GND (0 В)", size=9.5, color=NEG))

    # Фільтруючий конденсатор C_filt на землю
    p.append(line(240, 200, 370, 200, color=INK, sw=2))
    p.append(circle(370, 200, 4, fill=INK, stroke=INK))
    p.append(line(370, 200, 370, 240, color=LINE, sw=2))
    p.append(line(355, 240, 385, 240, color=LINE, sw=2.5))
    p.append(line(355, 248, 385, 248, color=LINE, sw=2.5))
    p.append(line(370, 248, 370, 290, color=LINE, sw=2))
    p.append(line(355, 290, 385, 290, color=LINE, sw=2))
    p.append(text(410, 245, "C_filt", size=10.5, color=INK, bold=True))
    p.append(text(410, 260, "10–100 нФ", size=9.5, color=MUTED))

    # Перехід на кристал MCU
    p.append(line(370, 200, 520, 200, color=INK, sw=2))
    p.append(circle(520, 200, 6, fill=POS, stroke=INK, sw=1.5))
    p.append(text(520, 180, "GPIO Pin", size=10.5, color=POS, bold=True))

    # Внутрішні кремнієві діоди кристала (PN)
    p.append(line(520, 200, 580, 200, color=POS, sw=2))
    p.append(circle(580, 200, 4, fill=POS, stroke=POS))

    # Внутрішній діод на VDD
    p.append(line(580, 200, 580, 160, color=POS, sw=1.5))
    p.append('<polygon points="570,160 590,160 580,140" fill="#fee2e2" stroke="#c0392b" stroke-width="1.5"/>')
    p.append(line(570, 140, 590, 140, color=POS, sw=1.5))
    p.append(line(580, 140, 580, 120, color=POS, sw=1.5))
    p.append(line(560, 120, 600, 120, color=POS, sw=2))
    p.append(text(580, 112, "VDD (+3.3 В)", size=9.5, color=POS))
    p.append(text(660, 145, "Кремнієвий PN", size=10, color=POS, bold=True))
    p.append(text(660, 160, "Vf ≈ 0.65–0.70 В", size=9.5, color=POS))
    p.append(text(660, 175, "(НЕ ВІДКРИВАЄТЬСЯ)", size=9.5, color=FIELD, bold=True))

    # Внутрішній діод на GND
    p.append(line(580, 200, 580, 240, color=POS, sw=1.5))
    p.append('<polygon points="570,260 590,260 580,240" fill="#fee2e2" stroke="#c0392b" stroke-width="1.5"/>')
    p.append(line(570, 240, 590, 240, color=POS, sw=1.5))
    p.append(line(580, 260, 580, 290, color=POS, sw=1.5))
    p.append(line(565, 290, 595, 290, color=POS, sw=2))
    p.append(text(580, 305, "GND (Підкладка)", size=10, color=POS))

    # Вхідний буфер / затвор КМОН
    p.append(line(580, 200, 750, 200, color=INK, sw=2))
    p.append(rect(750, 165, 120, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(810, 195, "КМОН Затвор /", size=10.5, color=INK, bold=True))
    p.append(text(810, 215, "АЦП Буфер", size=10.5, color=INK, bold=True))

    # Висновок унизу
    b_bot, _, _ = textbox(W / 2, 400,
                          "Оскільки пряме падіння на діоді Шотткі (0.25 В) значно менше за поріг кремнієвого діода чипа (0.65 В),\n"
                          "весь струм аварії перехоплюється зовнішнім BAT54S. Струм у кремнієву підкладку = 0, ризик Latch-up усунуто.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "gpio-clamping-diodes-mechanism.svg"), W, H, *p,
           title="Захист входу GPIO/АЦП: зовнішні діоди Шотткі та запобігання Latch-up")


# ── 3. flyback-vs-zener-clamp: Демпфування індуктивного навантаження ─────────
def fig_flyback_vs_zener_clamp():
    W, H = 920, 440
    p = []

    # Лівий блок: Звичайний зворотний діод (Flyback diode)
    p.append(rect(30, 45, 410, 320, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(235, 75, "Класичний зворотний діод (Flyback)", size=13, color=INK, bold=True))
    p.append(text(235, 93, "Повільне згасання струму (довгий спад)", size=10.5, color=MUTED))

    # Шина живлення +24V
    p.append(line(70, 115, 280, 115, color=POS, sw=2.5))
    p.append(text(175, 107, "+24 В (VDD)", size=10.5, color=POS, bold=True))

    # Котушка індуктивності L
    p.append(line(120, 115, 120, 140, color=INK, sw=2))
    p.append(rect(105, 140, 30, 60, fill="#edf5ff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(120, 175, "L, R", size=10.5, color=INK, bold=True))
    p.append(line(120, 200, 120, 230, color=INK, sw=2))
    p.append(text(75, 170, "Реле /", size=10, color=INK))
    p.append(text(75, 185, "Соленоїд", size=10, color=INK))

    # Зворотний діод паралельно котушці
    p.append(line(120, 125, 210, 125, color=NEG, sw=2))
    p.append(line(210, 125, 210, 150, color=NEG, sw=2))
    p.append('<polygon points="200,170 220,170 210,150" fill="#2457d6" stroke="#2457d6" stroke-width="1.5"/>')
    p.append(line(200, 150, 220, 150, color=NEG, sw=2))
    p.append(line(210, 170, 210, 215, color=NEG, sw=2))
    p.append(line(210, 215, 120, 215, color=NEG, sw=2))
    p.append(text(250, 165, "Діод 1N4007", size=10, color=NEG, bold=True))
    p.append(text(250, 180, "V_clamp = 0.7 В", size=9.5, color=NEG))

    # MOSFET внизу
    p.append(circle(120, 245, 4, fill=INK, stroke=INK))
    p.append(rect(100, 235, 40, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(120, 258, "FET", size=10, color=INK, bold=True))
    p.append(line(120, 275, 120, 305, color=LINE, sw=2))
    p.append(line(105, 305, 135, 305, color=LINE, sw=2))
    p.append(text(120, 320, "GND", size=9.5, color=MUTED))

    # Формула спаду
    b1, _, _ = textbox(300, 260, "Напруга на котушці:\n  V_L = −0.7 В\nЧас вимкнення:\n  τ = L / R_coil (великий)\nКонтакти реле горять в дузі!",
                       size=10, fill="#ffffff", stroke=POS)
    p.append(b1)

    # Правий блок: Zener Clamp / TVS (швидке розмикання)
    p.append(rect(480, 45, 410, 320, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(685, 75, "Швидкий захист (Zener / TVS Clamp)", size=13, color=FIELD, bold=True))
    p.append(text(685, 93, "Миттєве гасіння магнітної енергії соленоїда", size=10.5, color=FIELD))

    # Шина живлення +24V
    p.append(line(520, 115, 730, 115, color=POS, sw=2.5))
    p.append(text(625, 107, "+24 В (VDD)", size=10.5, color=POS, bold=True))

    # Котушка індуктивності L
    p.append(line(570, 115, 570, 140, color=INK, sw=2))
    p.append(rect(555, 140, 30, 60, fill="#edf5ff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(570, 175, "L, R", size=10.5, color=INK, bold=True))
    p.append(line(570, 200, 570, 230, color=INK, sw=2))
    p.append(text(525, 170, "Реле /", size=10, color=INK))
    p.append(text(525, 185, "Соленоїд", size=10, color=INK))

    # Зв'язка Діод + Стабілітрон (Zener)
    p.append(line(570, 125, 660, 125, color=FIELD, sw=2))
    p.append(line(660, 125, 660, 145, color=FIELD, sw=2))

    # Стабілітрон Vz (зустрічно)
    p.append('<polygon points="650,145 670,145 660,165" fill="#27ae60" stroke="#27ae60" stroke-width="1.5"/>')
    p.append(line(647, 165, 673, 165, color=FIELD, sw=2))
    p.append(line(647, 165, 647, 169, color=FIELD, sw=1.5))
    p.append(line(673, 165, 673, 161, color=FIELD, sw=1.5))

    p.append(line(660, 165, 660, 180, color=FIELD, sw=2))

    # Звичайний діод швидкої дії
    p.append('<polygon points="650,200 670,200 660,180" fill="#27ae60" stroke="#27ae60" stroke-width="1.5"/>')
    p.append(line(650, 180, 670, 180, color=FIELD, sw=2))
    p.append(line(660, 200, 660, 215, color=FIELD, sw=2))
    p.append(line(660, 215, 570, 215, color=FIELD, sw=2))

    p.append(text(710, 155, "Стабілітрон (Vz = 33 В)", size=9.5, color=FIELD, bold=True))
    p.append(text(710, 190, "Діод Шотткі", size=9.5, color=FIELD))

    # MOSFET внизу
    p.append(circle(570, 245, 4, fill=INK, stroke=INK))
    p.append(rect(550, 235, 40, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(570, 258, "FET", size=10, color=INK, bold=True))
    p.append(line(570, 275, 570, 305, color=LINE, sw=2))
    p.append(line(555, 305, 585, 305, color=LINE, sw=2))
    p.append(text(570, 320, "GND", size=9.5, color=MUTED))

    # Формула швидкого спаду
    b2, _, _ = textbox(750, 260, "Напруга на котушці:\n  V_L = −(Vz + 0.7 В)\nЧас розсіювання енергії:\n  t_off ≈ L · I₀ / Vz\nСпад у 10–50 разів швидший!",
                       size=10, fill="#ffffff", stroke=FIELD)
    p.append(b2)

    # Висновок унизу
    b_bot, _, _ = textbox(W / 2, 400,
                          "Для реле та швидких клапанів звичайний діод затягує вимкнення через повільну циркуляцію струму (L/R).\n"
                          "Додавання стабілітрона (Zener clamp) збільшує зворотну напругу, скорочуючи час спаду струму в десятки разів.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "flyback-vs-zener-clamp.svg"), W, H, *p,
           title="Захист ключа від індуктивного викиду: звичайний діод проти Zener Clamp")


# ── 4. power-protection-cascade: Повний каскад захисту живлення ───────────────
def fig_power_protection_cascade():
    W, H = 940, 430
    p = []

    # Рамка каскаду
    p.append(rect(30, 45, 880, 320, fill="#fdfcf7", stroke="#d1d5db", sw=1.5, rx=8))

    # Вхідна напруга ліворуч (Dirty Power In)
    p.append(rect(45, 120, 80, 120, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(85, 155, "БРУДНИЙ", size=10, color=POS, bold=True))
    p.append(text(85, 172, "ВХІД", size=11, color=POS, bold=True))
    p.append(text(85, 192, "12–24 В", size=10, color=INK))
    p.append(text(85, 210, "(Surge, ±)", size=9.5, color=MUTED))

    # Стрілка на каскад 1: PPTC Polyfuse
    p.append(arrow(125, 180, 155, 180, color=INK, sw=2))

    # Блок 1: PPTC Polyfuse
    p.append(rect(155, 130, 110, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(210, 155, "1. PPTC", size=11.5, color=INK, bold=True))
    p.append(text(210, 175, "Polyfuse", size=10.5, color=LINE))
    p.append(text(210, 195, "I_hold = 1.1 A", size=9.5, color=MUTED))
    p.append(text(210, 212, "Захист від КЗ", size=9.5, color=FIELD, bold=True))

    p.append(arrow(265, 180, 295, 180, color=INK, sw=2))

    # Блок 2: TVS Diode (SMCJ28CA)
    p.append(rect(295, 130, 110, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(350, 155, "2. TVS Діод", size=11.5, color=INK, bold=True))
    p.append(text(350, 175, "SMAJ / SMCJ", size=10.5, color=LINE))
    p.append(text(350, 195, "Зрізання піків", size=9.5, color=MUTED))
    p.append(text(350, 212, "ESD / сплески", size=9.5, color=FIELD, bold=True))

    p.append(arrow(405, 180, 435, 180, color=INK, sw=2))

    # Блок 3: P-MOSFET (Reverse Polarity Protection)
    p.append(rect(435, 130, 125, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(497, 155, "3. P-MOSFET", size=11.5, color=INK, bold=True))
    p.append(text(497, 175, "Ідеальний діод", size=10.5, color=LINE))
    p.append(text(497, 195, "Rds = 15 мОм", size=9.5, color=MUTED))
    p.append(text(497, 212, "Від переполюсовки", size=9.5, color=FIELD, bold=True))

    p.append(arrow(560, 180, 590, 180, color=INK, sw=2))

    # Блок 4: LC / Pi Filter & Ferrite
    p.append(rect(590, 130, 120, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(650, 155, "4. LC / π-фільтр", size=11.5, color=INK, bold=True))
    p.append(text(650, 175, "Дросель + C", size=10.5, color=LINE))
    p.append(text(650, 195, "Ферит + MLCC", size=9.5, color=MUTED))
    p.append(text(650, 212, "EMI / шум DC-DC", size=9.5, color=FIELD, bold=True))

    p.append(arrow(710, 180, 745, 180, color=FIELD, sw=2.5))

    # Вихід: Чисте живлення плати (Clean DC Bus)
    p.append(rect(745, 120, 145, 120, fill="#edfdf5", stroke=FIELD, sw=2, rx=6))
    p.append(text(817, 155, "ЧИСТА ШИНА", size=11, color=FIELD, bold=True))
    p.append(text(817, 175, "VCC_Clean", size=12, color=FIELD, bold=True))
    p.append(text(817, 198, "до DC-DC / LDO", size=10, color=INK))
    p.append(text(817, 215, "Безпечно для МК", size=9.5, color=MUTED))

    # Пояснювальні плашки під кожним етапом
    p.append(rect(60, 260, 820, 80, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(470, 285, "Послідовність реагування каскаду на різні загрози:", size=11.5, color=INK, bold=True))
    p.append(text(470, 305, "• ESD / Наносекундні сплески: миттєво зрізаються TVS-діодом (< 1 нс).", size=10.5, color=FIELD))
    p.append(text(470, 325, "• Переполюсовка: P-MOSFET миттєво закривається (Vgs = 0 В). Надструм: PPTC розігрівається й блокує коло.", size=10.5, color=FIELD))

    # Загальний висновок унизу
    b_bot, _, _ = textbox(W / 2, 395,
                          "Повний каскад вхідного захисту поєднує часові діапазони: швидкі імпульси гасяться TVS (< 1 нс), зворотна полярність\n"
                          "блокується польовим транзистором (< 100 нс), а тривале перевантаження та струм КЗ зупиняє самовідновний запобіжник PPTC.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "power-protection-cascade.svg"), W, H, *p,
           title="Повний каскад захисту вводу живлення друкованої плати")


if __name__ == "__main__":
    fig_esd_tvs_placement_flowthrough()
    fig_gpio_clamping_diodes_mechanism()
    fig_flyback_vs_zener_clamp()
    fig_power_protection_cascade()
    print("All protection figures generated successfully.")
