# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to root/scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. ground-potential-shift: Пастка спільної землі на довгій дистанції ──
def fig_ground_potential_shift():
    W, H = 880, 420
    p = []

    # Фон та контури вузлів
    # Вузол 1 (Цех А)
    p.append(rect(40, 50, 230, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(155, 80, "Вузол 1 (Цех А)", size=14, color=INK, bold=True))
    p.append(text(155, 100, "Живлення 3.3 В / GND1", size=11, color=MUTED))

    # Вихід UART TX
    p.append(rect(65, 130, 180, 70, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(155, 155, "UART TX (МК)", size=12, color=NEG, bold=True))
    p.append(text(155, 175, "Рівні: 0 В або 3.3 В", size=11, color=INK))

    # Вузол 2 (Цех Б)
    p.append(rect(610, 50, 230, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(725, 80, "Вузол 2 (Цех Б)", size=14, color=INK, bold=True))
    p.append(text(725, 100, "Поруч двигун / GND2", size=11, color=MUTED))

    # Вхід UART RX
    p.append(rect(635, 130, 180, 70, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(725, 155, "UART RX (МК)", size=12, color=POS, bold=True))
    p.append(text(725, 175, "Вхідний поріг: 1.6 В", size=11, color=INK))

    # Сигнальний дріт (100 метрів)
    p.append(line(245, 165, 635, 165, color=NEG, sw=2.5))
    p.append(arrow(400, 165, 480, 165, color=NEG, sw=2.5))
    p.append(text(440, 150, "Сигнальний дріт (100 м, TX → RX)", size=12, color=NEG, bold=True))

    # Земляний провідник
    p.append(line(155, 290, 155, 340, color=LINE, sw=2))
    p.append(line(725, 290, 725, 340, color=LINE, sw=2))
    p.append(line(155, 340, 725, 340, color=LINE, sw=2, dash="6 4"))

    # Джерело різниці потенціалів земель
    p.append(circle(440, 340, 22, fill="#fef2f2", stroke=POS, sw=2))
    p.append(text(440, 335, "ΔV_GND", size=11, color=POS, bold=True))
    p.append(text(440, 352, "+12 В", size=11, color=POS, bold=True))

    p.append(text(440, 380, "Зсув потенціалів земель через струми промислового обладнання", size=11, color=POS))

    # Позначки напруг
    b_left, _, _ = textbox(155, 240, "V_TX = 0 В .. 3.3 В\nвідносно GND1", size=11, fill="#eff6ff", stroke=NEG)
    p.append(b_left)

    b_right, _, _ = textbox(725, 240, "V_in = -12 В .. -8.7 В!\nвідносно GND2 (пробій!)", size=11, fill="#fee2e2", stroke=POS, bold=True)
    p.append(b_right)

    render(os.path.join(OUT, "ground-potential-shift.svg"), W, H, *p,
           title="Руйнування однопровідного сигналу через різницю потенціалів земель")


# ── 2. differential-common-noise: Синфазне придушення шуму в RS-485 ──────────
def fig_differential_common_noise():
    W, H = 900, 430
    p = []

    # Ліва частина: Джерело RS-485
    p.append(rect(30, 50, 200, 260, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(130, 80, "Драйвер RS-485", size=14, color=INK, bold=True))

    p.append(circle(190, 130, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(text(110, 135, "Вихід A (прямий)", size=11, color=POS, bold=True))

    p.append(circle(190, 230, 5, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(110, 235, "Вихід B (інверсний)", size=11, color=NEG, bold=True))

    # Права частина: Приймач RS-485
    p.append(rect(670, 50, 200, 260, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(770, 80, "Приймач RS-485", size=14, color=INK, bold=True))

    p.append(circle(710, 130, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(text(790, 135, "Вхід A", size=11, color=POS, bold=True))

    p.append(circle(710, 230, 5, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(790, 235, "Вхід B", size=11, color=NEG, bold=True))

    # Диференціальний компаратор всередині приймача
    p.append(rect(740, 150, 110, 60, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(795, 175, "Компаратор", size=11, color=FIELD, bold=True))
    p.append(text(795, 195, "V_out = V_A - V_B", size=10, color=INK))

    # Вита пара A і B
    # Лінія A
    p.append(line(190, 130, 350, 130, color=POS, sw=2))
    p.append(line(350, 130, 420, 230, color=POS, sw=2))
    p.append(line(420, 230, 490, 230, color=POS, sw=2))
    p.append(line(490, 230, 560, 130, color=POS, sw=2))
    p.append(arrow(560, 130, 705, 130, color=POS, sw=2))
    p.append(text(270, 120, "Провідник A (+2.5 В)", size=10.5, color=POS))

    # Лінія B
    p.append(line(190, 230, 350, 230, color=NEG, sw=2))
    p.append(line(350, 230, 420, 130, color=NEG, sw=2))
    p.append(line(420, 130, 490, 130, color=NEG, sw=2))
    p.append(line(490, 130, 560, 230, color=NEG, sw=2))
    p.append(arrow(560, 230, 705, 230, color=NEG, sw=2))
    p.append(text(270, 245, "Провідник B (-2.5 В)", size=10.5, color=NEG))

    # Джерело електромагнітної завади зверху
    p.append(rect(340, 20, 220, 50, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(450, 42, "Електромагнітна завада (ЕМІ)", size=11.5, color=POS, bold=True))
    p.append(text(450, 58, "Частотник, реле, контактор", size=10, color=MUTED))

    # Стрілки наведеного шуму однакової амплітуди
    p.append(arrow(410, 75, 410, 115, color=POS, sw=1.8))
    p.append(arrow(490, 75, 490, 115, color=POS, sw=1.8))
    p.append(text(450, 95, "+ V_шум однаково на обидва дроти", size=10, color=POS, bold=True))

    # Блок пояснення віднімання
    box_math, _, _ = textbox(450, 355,
        "Напруга на вході A: V_A + V_шум\n"
        "Напруга на вході B: V_B + V_шум\n"
        "Різниця в компараторі: (V_A + V_шум) - (V_B + V_шум) = V_A - V_B = +5 В\n"
        "Синфазний шум повністю анулюється завдяки геометричній симетрії витої пари",
        size=11.5, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    p.append(box_math)

    render(os.path.join(OUT, "differential-common-noise.svg"), W, H, *p,
           title="Придушення синфазного шуму диференціальним приймачем RS-485")


# ── 3. transmission-line-reflections: Відбиття та хвильові процеси ───────────
def fig_transmission_line_reflections():
    W, H = 900, 440
    p = []

    # 3 осцилограми поруч: Нетермінована (Open), КЗ (Short), Узгоджена (120 Ohm)
    # Блок 1: Нетермінована (Розрив, R_L = inf)
    p.append(rect(30, 45, 260, 260, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    p.append(text(160, 70, "Неузгоджена (R_L = ∞)", size=13, color=POS, bold=True))
    p.append(text(160, 90, "Коефіцієнт відбиття Γ = +1", size=11, color=MUTED))

    # Сітка осцилографа 1
    p.append(line(50, 240, 270, 240, color="#cbd5e1", sw=1))
    p.append(line(50, 180, 270, 180, color="#cbd5e1", sw=1, dash="3 3"))
    p.append(line(50, 120, 270, 120, color="#cbd5e1", sw=1, dash="3 3"))
    p.append(text(45, 240, "0В", size=9, color=MUTED, anchor="end"))
    p.append(text(45, 180, "V₀", size=9, color=MUTED, anchor="end"))
    p.append(text(45, 120, "2V₀", size=9, color=MUTED, anchor="end"))

    # Осцилограма зі дзвоном (Ringing)
    osc1 = [(50, 240), (80, 240), (85, 110), (120, 110), (125, 205), (160, 205), (165, 170), (200, 170), (205, 182), (270, 180)]
    for i in range(len(osc1)-1):
        p.append(line(osc1[i][0], osc1[i][1], osc1[i+1][0], osc1[i+1][1], color=POS, sw=2.2))
    p.append(text(160, 275, "Подвоєння напруги й дзвін\nХибні спрацьовування UART!", size=10.5, color=POS, bold=True))

    # Блок 2: Коротка лінія або КЗ (R_L = 0)
    p.append(rect(320, 45, 260, 260, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(450, 70, "Коротке замикання (R_L = 0)", size=13, color=NEG, bold=True))
    p.append(text(450, 90, "Коефіцієнт відбиття Γ = -1", size=11, color=MUTED))

    # Сітка осцилографа 2
    p.append(line(340, 240, 560, 240, color="#cbd5e1", sw=1))
    p.append(line(340, 180, 560, 180, color="#cbd5e1", sw=1, dash="3 3"))
    p.append(text(335, 240, "0В", size=9, color=MUTED, anchor="end"))
    p.append(text(335, 180, "V₀", size=9, color=MUTED, anchor="end"))

    # Осцилограма зі спадом у нуль
    osc2 = [(340, 240), (370, 240), (375, 180), (410, 180), (415, 240), (560, 240)]
    for i in range(len(osc2)-1):
        p.append(line(osc2[i][0], osc2[i][1], osc2[i+1][0], osc2[i+1][1], color=NEG, sw=2.2))
    p.append(text(450, 275, "Хвиля гасить саму себе\nСигнал падає до нуля!", size=10.5, color=NEG, bold=True))

    # Блок 3: Ідеальне узгодження (R_L = 120 Ом)
    p.append(rect(610, 45, 260, 260, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(740, 70, "Термінована (R_L = 120 Ом)", size=13, color=FIELD, bold=True))
    p.append(text(740, 90, "Коефіцієнт відбиття Γ = 0", size=11, color=MUTED))

    # Сітка осцилографа 3
    p.append(line(630, 240, 850, 240, color="#cbd5e1", sw=1))
    p.append(line(630, 180, 850, 180, color="#cbd5e1", sw=1, dash="3 3"))
    p.append(text(625, 240, "0В", size=9, color=MUTED, anchor="end"))
    p.append(text(625, 180, "V₀", size=9, color=MUTED, anchor="end"))

    # Осцилограма чиста
    osc3 = [(630, 240), (660, 240), (665, 180), (850, 180)]
    for i in range(len(osc3)-1):
        p.append(line(osc3[i][0], osc3[i][1], osc3[i+1][0], osc3[i+1][1], color=FIELD, sw=2.5))
    p.append(text(740, 275, "Хвиля повністю поглинається\nІдеальний чистий фронт!", size=10.5, color=FIELD, bold=True))

    # Нижній висновок
    box_concl, _, _ = textbox(W / 2, 375,
        "Термінатори 120 Ом ставляться строго на ДВОХ крайніх фізичних кінцях шини.\n"
        "Вони перетворюють довгу лінію на нескінченну для біжучої хвилі, повністю усуваючи відбиття.",
        size=11.5, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    p.append(box_concl)

    render(os.path.join(OUT, "transmission-line-reflections.svg"), W, H, *p,
           title="Осцилограми відбитих хвиль у довгій лінії зв'язку")


# ── 4. failsafe-biasing-network: Зміщення лінії у стані спокою ───────────────
def fig_failsafe_biasing_network():
    W, H = 880, 420
    p = []

    # Шина живлення VCC зверху
    p.append(line(100, 50, 780, 50, color=POS, sw=2.5))
    p.append(text(810, 55, "+5 В (VCC)", size=12, color=POS, bold=True, anchor="start"))

    # Шина GND знизу
    p.append(line(100, 330, 780, 330, color=LINE, sw=2.5))
    p.append(text(810, 335, "GND", size=12, color=LINE, bold=True, anchor="start"))

    # Лінії шини A і B посередині
    p.append(line(60, 130, 820, 130, color=POS, sw=2))
    p.append(text(50, 135, "Лінія A (+)", size=12, color=POS, bold=True, anchor="end"))

    p.append(line(60, 250, 250, 250, color=NEG, sw=2))
    p.append(line(250, 250, 820, 250, color=NEG, sw=2))
    p.append(text(50, 255, "Лінія B (-)", size=12, color=NEG, bold=True, anchor="end"))

    # Резистор підтяжки до VCC (Pull-up) на лінію A
    p.append(line(250, 50, 250, 75, color=POS, sw=1.8))
    p.append(rect(235, 75, 30, 40, fill="#ffffff", stroke=POS, sw=1.8, rx=3))
    p.append(text(250, 98, "R_PU", size=10, color=POS, bold=True))
    p.append(text(295, 95, "560 Ом", size=10.5, color=INK))
    p.append(line(250, 115, 250, 130, color=POS, sw=1.8))
    p.append(circle(250, 130, 4, fill=POS, stroke=INK))

    # Термінатор RT1 ліворуч (120 Ом)
    p.append(line(140, 130, 140, 170, color=LINE, sw=1.8))
    p.append(rect(125, 170, 30, 40, fill="#ffffff", stroke=FIELD, sw=1.8, rx=3))
    p.append(text(140, 193, "R_T1", size=10, color=FIELD, bold=True))
    p.append(text(95, 193, "120 Ом", size=10.5, color=INK, anchor="end"))
    p.append(line(140, 210, 140, 250, color=LINE, sw=1.8))
    p.append(circle(140, 130, 4, fill=LINE, stroke=INK))
    p.append(circle(140, 250, 4, fill=LINE, stroke=INK))

    # Термінатор RT2 праворуч (120 Ом)
    p.append(line(720, 130, 720, 170, color=LINE, sw=1.8))
    p.append(rect(705, 170, 30, 40, fill="#ffffff", stroke=FIELD, sw=1.8, rx=3))
    p.append(text(720, 193, "R_T2", size=10, color=FIELD, bold=True))
    p.append(text(765, 193, "120 Ом", size=10.5, color=INK, anchor="start"))
    p.append(line(720, 210, 720, 250, color=LINE, sw=1.8))
    p.append(circle(720, 130, 4, fill=LINE, stroke=INK))
    p.append(circle(720, 250, 4, fill=LINE, stroke=INK))

    # Резистор підтяжки до GND (Pull-down) з лінії B
    p.append(circle(250, 250, 4, fill=NEG, stroke=INK))
    p.append(line(250, 250, 250, 265, color=NEG, sw=1.8))
    p.append(rect(235, 265, 30, 40, fill="#ffffff", stroke=NEG, sw=1.8, rx=3))
    p.append(text(250, 288, "R_PD", size=10, color=NEG, bold=True))
    p.append(text(295, 288, "560 Ом", size=10.5, color=INK))
    p.append(line(250, 305, 250, 330, color=NEG, sw=1.8))

    # Пояснення напруги спокою
    box_calc, _, _ = textbox(500, 190,
        "Стан спокою (Hi-Z усіх передавачів):\n"
        "Еквівалентний опір термінації: R_T = 120 || 120 = 60 Ом\n"
        "Струм зміщення: I_bias = 5 В / (560 + 60 + 560) ≈ 4.24 мА\n"
        "Диференціальна напруга: V_AB = 4.24 мА · 60 Ом ≈ +254 мВ\n"
        "Гарантує стан '1' (UART Mark) і блокує паразитні байти шуму",
        size=11, fill="#f8fafc", stroke=FIELD, sw=1.5)
    p.append(box_calc)

    # Нижній висновок
    p.append(text(W/2, 385, "Схема Fail-Safe Biasing утримує лінію вище порогу +200 мВ за відсутності активного передавача",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "failsafe-biasing-network.svg"), W, H, *p,
           title="Схема пасивного зміщення лінії RS-485 у стані спокою (Fail-Safe)")


# ── 5. industrial-protection-stages: Багаторівневий промисловий захист ───────
def fig_industrial_protection_stages():
    W, H = 920, 420
    p = []

    # 4 каскади: Вхід лінії -> GDT/Іскровий проміжок -> PPTC/MELF -> TVS SM712 -> Гальванорозв'язка -> Трансивер
    # 1. Зовнішній роз'єм (зліва)
    p.append(rect(20, 70, 110, 240, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(75, 95, "Зовнішня", size=12, color=POS, bold=True))
    p.append(text(75, 115, "лінія", size=12, color=POS, bold=True))
    p.append(text(75, 170, "Клеми", size=11, color=INK))
    p.append(text(75, 190, "A / B / Shield", size=10, color=MUTED))
    p.append(text(75, 270, "Гроза / ESD\nдо ±15 кВ", size=10, color=POS))

    # 2. Каскад 1: Газорозрядники GDT (Грубий захист)
    p.append(rect(160, 70, 140, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(230, 95, "Каскад 1: GDT", size=12, color=INK, bold=True))
    p.append(text(230, 115, "Газорозрядник", size=11, color=MUTED))
    p.append(rect(205, 150, 50, 40, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(230, 175, "GDT", size=11, color=POS, bold=True))
    p.append(text(230, 255, "Скидає кА\nенергії на PE", size=10.5, color=INK))

    # 3. Каскад 2: Обмеження струму PPTC / MELF
    p.append(rect(330, 70, 140, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(400, 95, "Каскад 2: PPTC", size=12, color=INK, bold=True))
    p.append(text(400, 115, "Термозапобіжник", size=11, color=MUTED))
    p.append(rect(375, 150, 50, 40, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(400, 175, "PPTC", size=11, color=NEG, bold=True))
    p.append(text(400, 255, "Самовідновний\n10–20 Ом", size=10.5, color=INK))

    # 4. Каскад 3: Швидкий захист TVS (SM712)
    p.append(rect(500, 70, 150, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(575, 95, "Каскад 3: TVS", size=12, color=INK, bold=True))
    p.append(text(575, 115, "Супресор SM712", size=11, color=MUTED))
    p.append(rect(550, 150, 50, 40, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(575, 175, "TVS", size=11, color=FIELD, bold=True))
    p.append(text(575, 255, "Зрізає до\n-7 В .. +12 В", size=10.5, color=FIELD, bold=True))

    # 5. Каскад 4: Гальванічна ізоляція (ISO3082 / ADM2587E)
    p.append(rect(680, 70, 220, 240, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(790, 95, "Ізольований трансивер", size=12.5, color=NEG, bold=True))
    p.append(text(790, 115, "ISO3082 / ADM2587E", size=11, color=MUTED))

    p.append(rect(705, 145, 75, 55, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(742, 170, "Ізолятор", size=10.5, color=NEG, bold=True))
    p.append(text(742, 188, "2.5 кВ RMS", size=9.5, color=MUTED))

    p.append(rect(800, 145, 85, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(842, 170, "Драйвер RS485", size=10, color=FIELD, bold=True))
    p.append(text(842, 188, "DC-DC ізол.", size=9.5, color=MUTED))

    p.append(text(790, 260, "Повний розрив петлі GND\nЗахист МК від 2500 В", size=10.5, color=NEG, bold=True))

    # Сполучні сигнальні лінії між каскадами
    p.append(line(130, 160, 160, 160, color=POS, sw=2))
    p.append(line(300, 160, 330, 160, color=POS, sw=2))
    p.append(line(470, 160, 500, 160, color=POS, sw=2))
    p.append(line(650, 160, 680, 160, color=POS, sw=2))

    # Захисне заземлення PE
    p.append(line(230, 190, 230, 335, color=LINE, sw=1.8))
    p.append(line(575, 190, 575, 335, color=LINE, sw=1.8))
    p.append(line(200, 335, 600, 335, color=LINE, sw=2, dash="4 4"))
    p.append(text(400, 355, "Захисне заземлення (PE / Корпус приладу)", size=11, color=LINE, bold=True))

    # Нижній висновок
    p.append(text(W/2, 395, "Багаторівнева схема скидає високу енергію на корпус (PE), а тонку електроніку відокремлює бар'єром 2.5 кВ",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "industrial-protection-stages.svg"), W, H, *p,
           title="Багаторівневий захист порту RS-485 від перенапруг і завад")


if __name__ == "__main__":
    fig_ground_potential_shift()
    fig_differential_common_noise()
    fig_transmission_line_reflections()
    fig_failsafe_biasing_network()
    fig_industrial_protection_stages()
    print("All figures generated successfully.")
