# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори для силових доменів і сигналів
HS_COL   = "#d35400"  # помаранчевий — плаваючий високовольтний домен (High-Side)
LS_COL   = "#2980b9"  # синій — низьковольтний домен прив'язки до землі (Low-Side)
LOGIC    = "#8e44ad"  # фіолетовий — цифрова логіка керування
ALERT    = "#c0392b"  # червоний — аварії, наскрізні струми, загрози
SAFE     = "#27ae60"  # зелений — захищений стан, нормальна комутація


# ── 1. bridge-architecture: Архітектура повного H-моста та його драйвера ─────
def fig_bridge_architecture():
    W, H = 840, 520
    p = []

    # Головна рамка мікросхеми драйвера
    p.append(rect(40, 50, 410, 440, fill="#fafbfc", stroke=LINE, sw=2, rx=8))
    p.append(text(245, 75, "Інтегральний драйвер H-моста", size=15, color=INK, bold=True))

    # Вхідна цифрова логіка драйвера
    b_in, _, _ = textbox(130, 130, "Вхідна логіка\n(IN_A, IN_B, EN)\n3.3 В / 5 В", size=11, fill="#f3e5f5", stroke=LOGIC, sw=1.5, pad=6)
    p.append(b_in)

    b_dt, _, _ = textbox(130, 220, "Генератор Dead-time\nта Interlock-захист\n(анти-shoot-through)", size=11, fill="#e8f8f5", stroke=SAFE, sw=1.5, pad=6)
    p.append(b_dt)

    b_uvlo, _, _ = textbox(130, 310, "UVLO-компаратори\nживлення VCC / VBS\nі логіка Fault", size=11, fill="#fef5e7", stroke=HS_COL, sw=1.5, pad=6)
    p.append(b_uvlo)

    # Зв'язки всередині логіки
    p.append(arrow(130, 160, 130, 195, color=LINE, sw=1.5))
    p.append(arrow(130, 255, 130, 285, color=LINE, sw=1.5))

    # Блоки Level Shift та вихідні драйвери (Напівміст A і Напівміст B)
    # Напівміст A (High-Side A + Low-Side A)
    b_lsa, _, _ = textbox(340, 130, "Драйвер Low-Side A\n(вихід LO_A, до 2 А)\nземля GND", size=11, fill="#ebf5fb", stroke=LS_COL, sw=1.5, pad=6)
    p.append(b_lsa)

    b_hsa, _, _ = textbox(340, 220, "Level Shifter A +\nДрайвер High-Side A\n(плаваючий VB_A / VS_A)", size=11, fill="#fbeee6", stroke=HS_COL, sw=1.5, pad=6)
    p.append(b_hsa)

    # Напівміст B (High-Side B + Low-Side B)
    b_hsb, _, _ = textbox(340, 310, "Level Shifter B +\nДрайвер High-Side B\n(плаваючий VB_B / VS_B)", size=11, fill="#fbeee6", stroke=HS_COL, sw=1.5, pad=6)
    p.append(b_hsb)

    b_lsb, _, _ = textbox(340, 400, "Драйвер Low-Side B\n(вихід LO_B, до 2 А)\nземля GND", size=11, fill="#ebf5fb", stroke=LS_COL, sw=1.5, pad=6)
    p.append(b_lsb)

    # Лінії керування від логіки до драйверів
    p.append(arrow(195, 210, 260, 140, color=LINE, sw=1.5))
    p.append(arrow(195, 220, 260, 220, color=LINE, sw=1.5))
    p.append(arrow(195, 230, 260, 310, color=LINE, sw=1.5))
    p.append(arrow(195, 240, 260, 395, color=LINE, sw=1.5))

    # ── Силова частина H-моста (справа) ──
    # Шини живлення V_bus і GND
    p.append(line(500, 60, 800, 60, color=POS, sw=3))
    p.append(text(650, 48, "+V_bus (Силова шина 24...400 В)", size=12, color=POS, bold=True))

    p.append(line(500, 480, 800, 480, color=LINE, sw=3))
    p.append(text(650, 502, "GND_power (Силова земля)", size=12, color=LINE, bold=True))

    # Стійка A (Q1 зверху, Q2 знизу)
    b_q1, _, _ = textbox(560, 140, "Q1 (HS_A)\nN-MOSFET", size=12, fill="#fef9e7", stroke=HS_COL, sw=2, pad=8)
    p.append(b_q1)

    b_q2, _, _ = textbox(560, 400, "Q2 (LS_A)\nN-MOSFET", size=12, fill="#ebf5fb", stroke=LS_COL, sw=2, pad=8)
    p.append(b_q2)

    # Стійка B (Q3 зверху, Q4 знизу)
    b_q3, _, _ = textbox(740, 140, "Q3 (HS_B)\nN-MOSFET", size=12, fill="#fef9e7", stroke=HS_COL, sw=2, pad=8)
    p.append(b_q3)

    b_q4, _, _ = textbox(740, 400, "Q4 (LS_B)\nN-MOSFET", size=12, fill="#ebf5fb", stroke=LS_COL, sw=2, pad=8)
    p.append(b_q4)

    # З'єднання стійки A
    p.append(line(560, 60, 560, 115, color=POS, sw=2))
    p.append(line(560, 165, 560, 375, color=LINE, sw=2))
    p.append(line(560, 425, 560, 480, color=LINE, sw=2))

    # З'єднання стійки B
    p.append(line(740, 60, 740, 115, color=POS, sw=2))
    p.append(line(740, 165, 740, 375, color=LINE, sw=2))
    p.append(line(740, 425, 740, 480, color=LINE, sw=2))

    # Середні точки SW_A та SW_B та навантаження
    p.append(circle(560, 270, 4, fill=INK, stroke=INK))
    p.append(text(525, 265, "SW_A", size=12, color=HS_COL, bold=True))

    p.append(circle(740, 270, 4, fill=INK, stroke=INK))
    p.append(text(775, 265, "SW_B", size=12, color=HS_COL, bold=True))

    # Навантаження (DC Motor / Інвертор)
    p.append(line(560, 270, 610, 270, color=LINE, sw=2))
    p.append(line(690, 270, 740, 270, color=LINE, sw=2))
    p.append(circle(650, 270, 30, fill="#fdfefe", stroke=INK, sw=2))
    p.append(text(650, 275, "Мотор", size=13, color=INK, bold=True))

    # Керуючі зв'язки від виходів драйвера до затворів MOSFET
    p.append(arrow(415, 130, 515, 135, color=HS_COL, sw=1.8))
    p.append(text(465, 122, "HO_A", size=10, color=HS_COL, bold=True))

    p.append(arrow(415, 220, 515, 395, color=LS_COL, sw=1.8))
    p.append(text(465, 290, "LO_A", size=10, color=LS_COL, bold=True))

    p.append(arrow(415, 310, 695, 140, color=HS_COL, sw=1.8))
    p.append(text(525, 185, "HO_B", size=10, color=HS_COL, bold=True))

    p.append(arrow(415, 400, 695, 405, color=LS_COL, sw=1.8))
    p.append(text(545, 420, "LO_B", size=10, color=LS_COL, bold=True))

    render(os.path.join(OUT, "bridge-architecture.svg"), W, H, *p,
           title="Структура драйвера повного H-моста та силових ключів")


# ── 2. bootstrap-mechanism: Двофазний цикл бутстрепного живлення ─────────────
def fig_bootstrap_mechanism():
    W, H = 840, 470
    p = []

    # Фаза 1: Нижній ключ УВІМКНЕНО (заряд C_boot)
    p.append(rect(30, 50, 375, 400, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(217, 75, "Фаза 1: LS увімкнено (SW ≈ 0 В)", size=14, color=SAFE, bold=True))

    # Джерело VCC і діод D_boot
    p.append(rect(50, 105, 75, 32, fill="#e8f8f5", stroke=SAFE, sw=1.5, rx=4))
    p.append(text(87, 125, "V_cc = 12 В", size=11, color=SAFE, bold=True))

    p.append(arrow(125, 121, 185, 121, color=SAFE, sw=2))
    p.append(text(155, 112, "I_charge", size=10, color=SAFE, bold=True))

    # Діод D_boot
    p.append(rect(190, 106, 60, 30, fill="#ffffff", stroke=SAFE, sw=1.5, rx=4))
    p.append(text(220, 125, "D_boot", size=11, color=SAFE, bold=True))

    p.append(line(250, 121, 310, 121, color=SAFE, sw=2))
    p.append(circle(310, 121, 4, fill=SAFE, stroke=SAFE))
    p.append(text(340, 116, "VB", size=12, color=HS_COL, bold=True))

    # Конденсатор C_boot
    p.append(line(310, 121, 310, 160, color=SAFE, sw=2))
    p.append(rect(285, 160, 50, 26, fill="#fef9e7", stroke=HS_COL, sw=1.5, rx=4))
    p.append(text(310, 177, "C_boot", size=11, color=HS_COL, bold=True))
    p.append(line(310, 186, 310, 220, color=SAFE, sw=2))

    p.append(circle(310, 220, 4, fill=SAFE, stroke=SAFE))
    p.append(text(355, 225, "SW = 0 В", size=11, color=SAFE, bold=True))

    # Ключі
    p.append(rect(280, 250, 60, 32, fill="#e8f8f5", stroke=SAFE, sw=1.8, rx=4))
    p.append(text(310, 271, "LS (ON)", size=11, color=SAFE, bold=True))
    p.append(line(310, 220, 310, 250, color=SAFE, sw=2))
    p.append(line(310, 282, 310, 315, color=LINE, sw=2))
    p.append(line(280, 315, 340, 315, color=LINE, sw=3))
    p.append(text(310, 335, "GND", size=11, color=LINE))

    b1, _, _ = textbox(217, 395, "C_boot заряджається через D_boot до напруги\nV_Cboot = V_cc − V_diode ≈ 11.4 В", size=10, fill="#eafaf1", stroke=SAFE, sw=1.2, pad=6)
    p.append(b1)


    # Фаза 2: Верхній ключ УВІМКНЕНО (плаваючий потенціал над V_bus)
    p.append(rect(435, 50, 375, 400, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(622, 75, "Фаза 2: HS увімкнено (SW ≈ V_bus)", size=14, color=HS_COL, bold=True))

    # Джерело VCC і закритий діод
    p.append(rect(455, 105, 75, 32, fill="#f2f3f4", stroke=MUTED, sw=1.5, rx=4))
    p.append(text(492, 125, "V_cc = 12 В", size=11, color=MUTED))

    p.append(line(530, 121, 580, 121, color=MUTED, sw=1.5, dash="4,3"))

    # Діод D_boot під зворотною напругою
    p.append(rect(585, 106, 65, 30, fill="#ffffff", stroke=ALERT, sw=1.5, rx=4))
    p.append(text(617, 125, "D_boot (OFF)", size=9.5, color=ALERT, bold=True))

    p.append(line(650, 121, 710, 121, color=HS_COL, sw=2))
    p.append(circle(710, 121, 4, fill=HS_COL, stroke=HS_COL))
    p.append(text(755, 116, "VB ≈ V_bus+12В", size=10.5, color=HS_COL, bold=True))

    # Конденсатор C_boot живить верхній драйвер
    p.append(line(710, 121, 710, 160, color=HS_COL, sw=2))
    p.append(rect(685, 160, 50, 26, fill="#fef9e7", stroke=HS_COL, sw=1.8, rx=4))
    p.append(text(710, 177, "C_boot", size=11, color=HS_COL, bold=True))
    p.append(line(710, 186, 710, 220, color=HS_COL, sw=2))

    p.append(circle(710, 220, 4, fill=HS_COL, stroke=HS_COL))
    p.append(text(760, 225, "SW = V_bus", size=11, color=HS_COL, bold=True))

    # Ключ HS увімкнений
    p.append(rect(680, 250, 60, 32, fill="#fef9e7", stroke=HS_COL, sw=1.8, rx=4))
    p.append(text(710, 271, "HS (ON)", size=11, color=HS_COL, bold=True))
    p.append(line(710, 220, 710, 250, color=HS_COL, sw=2))
    p.append(line(710, 60, 710, 95, color=POS, sw=2))
    p.append(text(755, 75, "V_bus = 400 В", size=11, color=POS, bold=True))

    b2, _, _ = textbox(622, 395, "C_boot плаває разом із вузлом SW, створюючи\nживлення затвора V_gate = V_bus + 11.4 В", size=10, fill="#fef5e7", stroke=HS_COL, sw=1.2, pad=6)
    p.append(b2)

    render(os.path.join(OUT, "bootstrap-mechanism.svg"), W, H, *p,
           title="Двофазний цикл бутстрепного живлення верхнього ключа")


# ── 3. isolation-channels: Порівняння технологій гальванічної ізоляції ───────
def fig_isolation_channels():
    W, H = 840, 450
    p = []

    # 3 колонки: Оптопара, Трансформатор без сердечника, Ємнісна ізоляція
    cols = [
        ("Оптична ізоляція\n(Optocoupler)", 160, "#34495e", [
            "Випромінювач: GaAs LED",
            "Приймач: фотодіод + ОП",
            "Затримка: 100...300 нс",
            "CMTI: 15...50 кВ/мкс",
            "Старіння LED з часом",
            "Швидкість: до 1...10 Мбіт/с"
        ]),
        ("Мікротрансформаторна\n(Coreless Transformer)", 420, "#d35400", [
            "Індуктивні планарні котушки",
            "Імпульсна диференційна передача",
            "Затримка: 25...45 нс",
            "CMTI: 100...150 кВ/мкс",
            "Висока магнітна стійкість",
            "Швидкість: до 50...150 Мбіт/с"
        ]),
        ("Ємнісна ізоляція\n(Capacitive SiO2 Barrier)", 680, "#27ae60", [
            "Високовольтний діелектрик SiO2",
            "ВЧ-модуляція сигналу (OOK)",
            "Затримка: 15...30 нс",
            "CMTI: > 150...200 кВ/мкс",
            "Найдовший ресурс роботи",
            "Швидкість: > 150 Мбіт/с"
        ])
    ]

    for title, cx, col, items in cols:
        p.append(rect(cx - 120, 50, 240, 370, fill="#ffffff", stroke=col, sw=2, rx=8))
        p.append(mtext(cx, 80, title, size=13, color=col, bold=True))
        p.append(line(cx - 100, 115, cx + 100, 115, color=col, sw=1.2, dash="3,3"))

        # Іконка/схематичне зображення бар'єра
        if "Оптична" in title:
            p.append(rect(cx - 80, 130, 45, 45, fill="#fbeee6", stroke=ALERT, sw=1.5, rx=4))
            p.append(text(cx - 57, 158, "LED", size=11, color=ALERT, bold=True))
            p.append(arrow(cx - 25, 152, cx + 25, 152, color=ALERT, sw=2))
            p.append(rect(cx + 35, 130, 45, 45, fill="#ebf5fb", stroke=LS_COL, sw=1.5, rx=4))
            p.append(text(cx + 57, 158, "PD", size=11, color=LS_COL, bold=True))
        elif "Мікротрансформаторна" in title:
            p.append(circle(cx - 40, 152, 22, fill="#fef5e7", stroke=col, sw=2))
            p.append(text(cx - 40, 157, "L1", size=11, color=col, bold=True))
            p.append(line(cx - 5, 130, cx - 5, 175, color=LINE, sw=1.5, dash="3,2"))
            p.append(line(cx + 5, 130, cx + 5, 175, color=LINE, sw=1.5, dash="3,2"))
            p.append(circle(cx + 40, 152, 22, fill="#fef5e7", stroke=col, sw=2))
            p.append(text(cx + 40, 157, "L2", size=11, color=col, bold=True))
        else:
            p.append(line(cx - 40, 130, cx - 40, 175, color=col, sw=3))
            p.append(line(cx - 25, 130, cx - 25, 175, color=MUTED, sw=1.5, dash="2,2"))
            p.append(text(cx, 157, "SiO2", size=11, color=col, bold=True))
            p.append(line(cx + 25, 130, cx + 25, 175, color=MUTED, sw=1.5, dash="2,2"))
            p.append(line(cx + 40, 130, cx + 40, 175, color=col, sw=3))

        p.append(line(cx - 100, 195, cx + 100, 195, color=col, sw=1.2, dash="3,3"))

        # Параметри
        y_it = 225
        for it in items:
            p.append(text(cx, y_it, it, size=11, color=INK))
            y_it += 30

    render(os.path.join(OUT, "isolation-channels.svg"), W, H, *p,
           title="Порівняння трьох технологій гальванічної ізоляції драйверів")


# ── 4. shoot-through-deadtime: Наскрізний струм і формування мертвого часу ────
def fig_shoot_through_deadtime():
    W, H = 840, 460
    p = []

    # Діаграма А: Аварійне перемикання БЕЗ dead-time
    p.append(rect(40, 50, 360, 380, fill="#ffffff", stroke=ALERT, sw=1.8, rx=8))
    p.append(text(220, 75, "Без Dead-time: Наскрізний струм", size=13, color=ALERT, bold=True))

    # Сигнал HS (закривається повільно)
    p.append(text(85, 115, "HS Gate", size=11, color=HS_COL, bold=True))
    p.append(line(130, 110, 210, 110, color=HS_COL, sw=2.5))
    p.append(line(210, 110, 260, 150, color=HS_COL, sw=2.5))  # повільний спад
    p.append(line(260, 150, 370, 150, color=HS_COL, sw=2.5))

    # Сигнал LS (вмикається одразу)
    p.append(text(85, 195, "LS Gate", size=11, color=LS_COL, bold=True))
    p.append(line(130, 230, 210, 230, color=LS_COL, sw=2.5))
    p.append(line(210, 230, 225, 190, color=LS_COL, sw=2.5))  # швидкий фронт
    p.append(line(225, 190, 370, 190, color=LS_COL, sw=2.5))

    # Зона перекриття (Cross-conduction)
    p.append(rect(210, 95, 50, 155, fill="#fdecea", stroke=ALERT, sw=1.5))
    p.append(text(235, 268, "Перекриття (Обидва ON!)", size=10, color=ALERT, bold=True))

    # Сплеск наскрізного струму
    p.append(text(85, 310, "Струм I_bus", size=11, color=ALERT, bold=True))
    p.append(line(130, 340, 210, 340, color=ALERT, sw=2))
    p.append(line(210, 340, 235, 290, color=ALERT, sw=3))
    p.append(line(235, 290, 260, 340, color=ALERT, sw=3))
    p.append(line(260, 340, 370, 340, color=ALERT, sw=2))
    p.append(text(235, 280, "I_peak > 200 А!", size=11, color=ALERT, bold=True))

    b1, _, _ = textbox(220, 395, "Миттєве коротке замикання шини +V_bus\nТеплове руйнування кристалів транзисторів", size=10, fill="#fdecea", stroke=ALERT, sw=1.2, pad=6)
    p.append(b1)


    # Діаграма Б: Безпечне перемикання З dead-time
    p.append(rect(440, 50, 360, 380, fill="#ffffff", stroke=SAFE, sw=1.8, rx=8))
    p.append(text(620, 75, "З Dead-time: Безпечна пауза", size=13, color=SAFE, bold=True))

    # Сигнал HS (закривається)
    p.append(text(485, 115, "HS Gate", size=11, color=HS_COL, bold=True))
    p.append(line(530, 110, 590, 110, color=HS_COL, sw=2.5))
    p.append(line(590, 110, 625, 150, color=HS_COL, sw=2.5))
    p.append(line(625, 150, 770, 150, color=HS_COL, sw=2.5))

    # Мертвий час (пауза)
    p.append(rect(590, 95, 75, 155, fill="#e8f8f5", stroke=SAFE, sw=1.5))
    p.append(text(627, 268, "t_dead (Обидва OFF)", size=10, color=SAFE, bold=True))

    # Сигнал LS (вмикається ПІСЛЯ завершення паузи)
    p.append(text(485, 195, "LS Gate", size=11, color=LS_COL, bold=True))
    p.append(line(530, 230, 665, 230, color=LS_COL, sw=2.5))
    p.append(line(665, 230, 680, 190, color=LS_COL, sw=2.5))
    p.append(line(680, 190, 770, 190, color=LS_COL, sw=2.5))

    # Струм шини чистий, без піків
    p.append(text(485, 310, "Струм I_bus", size=11, color=SAFE, bold=True))
    p.append(line(530, 340, 770, 340, color=SAFE, sw=2))
    p.append(text(630, 325, "Наскрізний струм = 0 А", size=11, color=SAFE, bold=True))

    b2, _, _ = textbox(620, 395, "Ключ повністю закривається ДО старту\nвідкриття другого ключа стійки", size=10, fill="#eafaf1", stroke=SAFE, sw=1.2, pad=6)
    p.append(b2)

    render(os.path.join(OUT, "shoot-through-deadtime.svg"), W, H, *p,
           title="Порівняння процесів комутації без паузи та з мертвим часом")


# ── 5. miller-clamp: Паразитне відмикання через dV/dt та Active Miller Clamp ──
def fig_miller_clamp():
    W, H = 840, 440
    p = []

    # Ліва частина: Загроза паразитного відмикання без Клемпа
    p.append(rect(40, 50, 365, 360, fill="#ffffff", stroke=ALERT, sw=1.8, rx=8))
    p.append(text(222, 75, "Без Miller Clamp: dV/dt пробій", size=13, color=ALERT, bold=True))

    # Вузол стоку підстрибує
    p.append(text(120, 110, "Стік: dV/dt = 50 В/нс", size=11, color=POS, bold=True))
    p.append(line(240, 115, 240, 150, color=POS, sw=2))

    # Ємність C_gd (Міллера)
    p.append(rect(220, 150, 40, 25, fill="#fef9e7", stroke=ALERT, sw=1.5, rx=4))
    p.append(text(240, 167, "C_gd", size=11, color=ALERT, bold=True))
    p.append(line(240, 175, 240, 210, color=ALERT, sw=2))

    p.append(circle(240, 210, 4, fill=ALERT, stroke=ALERT))
    p.append(text(285, 205, "Затвір Q_LS", size=11, color=INK, bold=True))

    # Струм тече через опір затвора Rg
    p.append(arrow(240, 210, 130, 210, color=ALERT, sw=2))
    p.append(text(185, 198, "I_miller", size=10, color=ALERT, bold=True))

    p.append(rect(90, 198, 40, 24, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    p.append(text(110, 214, "R_g", size=11, color=INK))

    p.append(line(90, 210, 60, 210, color=INK, sw=1.5))
    p.append(line(60, 210, 60, 260, color=INK, sw=1.5))
    p.append(line(45, 260, 75, 260, color=LINE, sw=2.5))
    p.append(text(60, 278, "GND", size=10, color=MUTED))

    # Падіння напруги на Rg піднімає V_gs
    b_vgs, _, _ = textbox(222, 280, "V_gs = I_miller · (R_g + R_driver)\n= 1.5 А · 6 Ом = 9.0 В > V_th (3 В)!", size=10, fill="#fdecea", stroke=ALERT, sw=1.2, pad=6)
    p.append(b_vgs)

    b_res1, _, _ = textbox(222, 365, "Ключ LS самочинно ПРИВІДКРИВАЄТЬСЯ\nпід час увімкнення верхнього ключа!", size=10, fill="#fdecea", stroke=ALERT, sw=1.2, pad=6)
    p.append(b_res1)


    # Права частина: Захист із Active Miller Clamp
    p.append(rect(435, 50, 365, 360, fill="#ffffff", stroke=SAFE, sw=1.8, rx=8))
    p.append(text(617, 75, "З Active Miller Clamp: Безпека", size=13, color=SAFE, bold=True))

    # Вузол стоку
    p.append(text(515, 110, "Стік: dV/dt = 50 В/нс", size=11, color=POS, bold=True))
    p.append(line(635, 115, 635, 150, color=POS, sw=2))

    # Ємність C_gd
    p.append(rect(615, 150, 40, 25, fill="#fef9e7", stroke=SAFE, sw=1.5, rx=4))
    p.append(text(635, 167, "C_gd", size=11, color=SAFE, bold=True))
    p.append(line(635, 175, 635, 210, color=SAFE, sw=2))

    p.append(circle(635, 210, 4, fill=SAFE, stroke=SAFE))
    p.append(text(680, 205, "Затвір Q_LS", size=11, color=INK, bold=True))

    # Miller Clamp транзистор увімкнений і шунтує затвор
    p.append(line(635, 210, 635, 250, color=SAFE, sw=2.5))
    p.append(rect(605, 250, 60, 35, fill="#e8f8f5", stroke=SAFE, sw=1.8, rx=4))
    p.append(text(635, 272, "Clamp FET", size=11, color=SAFE, bold=True))
    p.append(line(635, 285, 635, 315, color=SAFE, sw=2.5))
    p.append(line(615, 315, 655, 315, color=LINE, sw=2.5))
    p.append(text(635, 332, "GND (або −V_ee)", size=10, color=SAFE, bold=True))

    p.append(arrow(635, 185, 635, 245, color=SAFE, sw=2))
    p.append(text(710, 245, "I_miller скидається\nв обхід R_g (< 0.5 Ом)", size=10, color=SAFE))

    b_res2, _, _ = textbox(617, 375, "V_gs надійно утримується біля 0 В (< 0.8 В)\nПаразитне відмикання повністю блоковано", size=10, fill="#eafaf1", stroke=SAFE, sw=1.2, pad=6)
    p.append(b_res2)

    render(os.path.join(OUT, "miller-clamp.svg"), W, H, *p,
           title="Схема паразитного відмикання через dV/dt та робота Active Miller Clamp")


# ── 6. desat-protection: Схема та часова діаграма захисту від десатурації ──────
def fig_desat_protection():
    W, H = 840, 460
    p = []

    # Ліва частина: Схема виявлення десатурації (DESAT Circuit)
    p.append(rect(40, 50, 420, 380, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    p.append(text(250, 75, "Схемотехніка DESAT-детектора", size=14, color=INK, bold=True))

    # Джерело струму I_charge
    p.append(rect(70, 115, 80, 35, fill="#f3e5f5", stroke=LOGIC, sw=1.5, rx=4))
    p.append(text(110, 137, "I_desat = 0.5 мА", size=10, color=LOGIC, bold=True))
    p.append(line(150, 132, 210, 132, color=LOGIC, sw=2))

    # Вузол DESAT pin
    p.append(circle(210, 132, 4, fill=INK, stroke=INK))
    p.append(text(210, 118, "DESAT Pin", size=11, color=INK, bold=True))

    # Конденсатор маскування C_blank
    p.append(line(210, 132, 210, 180, color=LINE, sw=1.8))
    p.append(rect(190, 180, 40, 25, fill="#fef9e7", stroke=HS_COL, sw=1.5, rx=4))
    p.append(text(210, 197, "C_blank", size=10, color=HS_COL, bold=True))
    p.append(line(210, 205, 210, 235, color=LINE, sw=1.8))
    p.append(line(195, 235, 225, 235, color=LINE, sw=2.5))
    p.append(text(210, 250, "GND", size=10, color=MUTED))

    # Високовольтний діод D_desat
    p.append(arrow(210, 132, 280, 132, color=LINE, sw=2))
    p.append(rect(280, 117, 50, 30, fill="#ffffff", stroke=HS_COL, sw=1.5, rx=4))
    p.append(text(305, 136, "D_desat", size=10, color=HS_COL, bold=True))
    p.append(line(330, 132, 380, 132, color=LINE, sw=2))

    # Підключення до силового стоку / колектора
    p.append(circle(380, 132, 4, fill=POS, stroke=POS))
    p.append(text(410, 126, "Стік / Колектор\n(V_ds / V_ce)", size=10, color=POS, bold=True))

    # Компаратор порогу V_th
    p.append(line(210, 132, 210, 280, color=LINE, sw=1.5))
    p.append(arrow(210, 280, 270, 280, color=LINE, sw=1.8))

    # Трикутник компаратора
    p.append(rect(270, 260, 60, 45, fill="#ebf5fb", stroke=LS_COL, sw=1.8, rx=4))
    p.append(text(300, 287, "V_th = 7 В", size=10, color=LS_COL, bold=True))

    p.append(arrow(330, 282, 380, 282, color=ALERT, sw=2))
    p.append(text(415, 287, "Fault / Soft\nTurn-Off", size=11, color=ALERT, bold=True))

    b_desc, _, _ = textbox(250, 380, "Норма: V_ds < 2 В -> діод відкритий -> C_blank розряджений\nКЗ: V_ds підстрибує -> діод закритий -> C_blank заряджається до 7 В", size=9.5, fill="#fcfcfc", stroke=MUTED, sw=1.2, pad=6)
    p.append(b_desc)


    # Права частина: Хронограма спрацьовування та Soft Turn-Off
    p.append(rect(480, 50, 320, 380, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    p.append(text(640, 75, "М'яке аварійне вимкнення", size=14, color=ALERT, bold=True))

    # Графік напруги DESAT
    p.append(text(540, 115, "V_desat", size=11, color=HS_COL, bold=True))
    p.append(line(570, 150, 620, 150, color=HS_COL, sw=2))
    p.append(line(620, 150, 670, 105, color=HS_COL, sw=2.5))
    p.append(line(670, 105, 780, 105, color=HS_COL, sw=2))
    p.append(line(570, 105, 780, 105, color=ALERT, sw=1.2, dash="3,2"))
    p.append(text(750, 95, "V_th (7 В)", size=9, color=ALERT))

    # Струм КЗ (Short Circuit Current)
    p.append(text(540, 200, "I_fault", size=11, color=ALERT, bold=True))
    p.append(line(570, 230, 620, 230, color=LINE, sw=2))
    p.append(line(620, 230, 630, 180, color=ALERT, sw=3))
    p.append(line(630, 180, 680, 180, color=ALERT, sw=3))
    p.append(line(680, 180, 730, 230, color=ALERT, sw=2))
    p.append(line(730, 230, 780, 230, color=LINE, sw=2))
    p.append(text(655, 170, "I_sc > 500 А", size=10, color=ALERT, bold=True))

    # Напруга затвора: Soft Turn-Off замість різкого фронту
    p.append(text(540, 290, "V_gate", size=11, color=SAFE, bold=True))
    p.append(line(570, 280, 670, 280, color=SAFE, sw=2))
    p.append(line(670, 280, 730, 330, color=HS_COL, sw=2.5)) # плавний спуск
    p.append(line(730, 330, 780, 330, color=LINE, sw=2))
    p.append(text(715, 300, "Soft Turn-Off\n(t_soft ≈ 2 мкс)", size=9, color=HS_COL, bold=True))

    b_st, _, _ = textbox(640, 385, "М'який розряд затвора гасить\nіндуктивний викид V = L_stray · di/dt", size=10, fill="#fef5e7", stroke=HS_COL, sw=1.2, pad=6)
    p.append(b_st)

    render(os.path.join(OUT, "desat-protection.svg"), W, H, *p,
           title="Принцип роботи захисту від десатурації та м'яке вимкнення")


if __name__ == "__main__":
    fig_bridge_architecture()
    fig_bootstrap_mechanism()
    fig_isolation_channels()
    fig_shoot_through_deadtime()
    fig_miller_clamp()
    fig_desat_protection()
    print("All figures generated successfully.")
