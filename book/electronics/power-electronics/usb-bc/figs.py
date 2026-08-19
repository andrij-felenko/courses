# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. usb-power-evolution: обмеження USB 2.0 проти BC 1.2 ────────────────────
def fig_power_evolution():
    W, H = 760, 360
    p = []

    # Дві порівняльні панелі: USB 2.0 (класичний) та USB BC 1.2
    p.append(rect(30, 45, 335, 255, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=10))
    p.append(rect(395, 45, 335, 255, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=10))

    p.append(text(197, 72, "Класичний USB 2.0 (2000 р.)", size=13, color=INK, bold=True))
    p.append(text(562, 72, "USB Battery Charging 1.2 (2010 р.)", size=13, color=FIELD, bold=True))

    # Ліва колонка (USB 2.0)
    p.append(fitbox(55, 95, 285, 42, "Лише 100 мА до опитування (енумерації)\nМаксимум 500 мА після дозволу хоста", size=10, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(55, 147, 285, 42, "Потрібен активний хост-контролер\nБез процесора струм заблоковано", size=10, fill=BG, stroke=POS, sw=1.2, color=POS))
    p.append(fitbox(55, 199, 285, 42, "Стеля потужності: 5 В × 0.5 А = 2.5 Вт\nБатарея 3000 мА·год заряджається > 6 год", size=10, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(55, 251, 285, 36, "У режимі сну (Suspend): лише 2.5 мА", size=10, fill=BG, stroke=MUTED, sw=1.0, color=MUTED))

    # Права колонка (USB BC 1.2)
    p.append(fitbox(420, 95, 285, 42, "До 1.5 А (7.5 Вт) на звичайному роз'ємі\nЗаряджання втричі швидше (≈ 2 год)", size=10, fill=BG, stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    p.append(fitbox(420, 147, 285, 42, "Апаратний автодетект через лінії D+/D−\nХост-контролер і стек USB НЕ потрібні", size=10, fill=BG, stroke=FIELD, sw=1.2))
    p.append(fitbox(420, 199, 285, 42, "Три стандартизовані порти: SDP, CDP, DCP\nБезпечне визначення навантажувальної здатності", size=10, fill=BG, stroke=FIELD, sw=1.2))
    p.append(fitbox(420, 251, 285, 36, "Струм до 1.5 А навіть без передачі даних", size=10, fill=BG, stroke=NEG, sw=1.0, color=NEG))

    # Підсумкова плашка внизу
    b, _, _ = textbox(W / 2, 325, "BC 1.2 розширив 5-вольтове живлення USB від 2.5 Вт до 7.5 Вт без зміни кабелів і роз'ємів",
                      size=11, fill="#eef2ff", stroke=NEG, sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "usb-power-evolution.svg"), W, H, *p,
           title="Порівняння лімітів живлення USB 2.0 та USB BC 1.2")


# ── 2. port-architectures: архітектура трьох портів SDP / CDP / DCP ───────────
def fig_port_architectures():
    W, H = 760, 320
    p = []

    ports = [
        (145, "SDP", "Standard Downstream", "Стандартний порт ПК", NEG, "#f8fafc",
         "Лінії D+/D− підтягнуті\nдо GND через R_PD = 15 кОм\nДані: USB 2.0 (480 Мбіт/с)\nСтрум: 100 мА / 500 мА (900 мА USB 3.0)"),
        (380, "CDP", "Charging Downstream", "ПК з посиленим живленням", FIELD, "#eff6ff",
         "Активна схема рукостискання:\nповертає 0.6 В на пробу D+\nДані: USB 2.0 під час зарядки\nСтрум: до 1.5 А при 5 В"),
        (615, "DCP", "Dedicated Charging", "Блок живлення / адаптер", POS, "#f0fdf4",
         "Пасивна перемичка:\nD+ замкнено на D− (R ≤ 200 Ом)\nДані відсутні (без хоста)\nСтрум: до 1.5 А (до 7.5 Вт)"),
    ]

    for cx, name, sub, desc, col, fill, body in ports:
        p.append(rect(cx - 105, 45, 210, 250, fill=fill, stroke=col, sw=1.6, rx=10))
        p.append(text(cx, 75, name, size=18, color=col, bold=True))
        p.append(text(cx, 95, sub, size=10, color=MUTED))
        p.append(text(cx, 115, desc, size=11, color=INK, bold=True))
        p.append(line(cx - 85, 128, cx + 85, 128, color=col, sw=1.0))
        p.append(fitbox(cx - 95, 140, 190, 140, body, size=10, fill=BG, stroke=MUTED, sw=1.0))

    render(os.path.join(OUT, "port-architectures.svg"), W, H, *p,
           title="Архітектура та характеристики портів SDP, CDP та DCP за стандартом BC 1.2")


# ── 3. detection-state-machine: алгоритм трьохетапної детекції ─────────────────
def fig_detection_flow():
    W, H = 760, 440
    p = []

    # 1. Етап: VBUS Detect & DCD
    p.append(fitbox(30, 45, 210, 75, "1. Поява VBUS (> 4.4 В)\nДетект контакту даних (DCD)\nСтрум I_DP_SRC = 10 мкА на D+\n(або таймаут до 900 мс)", size=10, fill="#f8fafc", stroke=MUTED, sw=1.4))
    p.append(arrow(240, 82, 275, 82, color=INK, sw=1.6))

    # 2. Етап: Primary Detection
    p.append(fitbox(275, 45, 215, 75, "2. Primary Detection\nПодача V_DP_SRC (0.6 В) на D+\nВимірювання V_DM на D−\nПорівняння з V_DAT_REF (0.4 В)", size=10, fill="#eff6ff", stroke=NEG, sw=1.4, bold=True, color=NEG))

    # Гілка вниз від Primary: V_DM < 0.4 В -> SDP
    p.append(arrow(382, 120, 382, 175, color=POS, sw=1.6))
    p.append(text(390, 150, "V_DM < 0.4 В", size=10, color=POS, anchor="start", bold=True))
    p.append(fitbox(275, 175, 215, 70, "Порт: SDP (Standard)\nЗвичайний хост USB\nЛіміт: 100 мА / 500 мА\nПотрібна енумерація USB", size=10, fill="#fef2f2", stroke=POS, sw=1.4, color=POS))

    # Гілка праворуч від Primary: V_DM > 0.4 В -> Зарядний порт
    p.append(arrow(490, 82, 525, 82, color=FIELD, sw=1.6))
    p.append(text(508, 70, "V_DM > 0.4 В", size=9.5, color=FIELD, bold=True))

    # 3. Етап: Secondary Detection
    p.append(fitbox(525, 45, 210, 75, "3. Secondary Detection\nПодача V_DM_SRC (0.6 В) на D−\nВимірювання V_DP на D+\nПорівняння з V_DAT_REF (0.4 В)", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.4, bold=True, color=FIELD))

    # Гілка вниз-ліворуч від Secondary: V_DP < 0.4 В -> CDP
    p.append(arrow(580, 120, 580, 275, color=NEG, sw=1.6))
    p.append(text(500, 200, "V_DP < 0.4 В\n(активна відповідь знята)", size=9, color=NEG, anchor="start"))
    p.append(fitbox(490, 275, 115, 90, "Порт: CDP\nCharging Port\nСтрум: 1.5 А\n+ дані USB 2.0", size=9.5, fill="#eff6ff", stroke=NEG, sw=1.4, color=NEG, bold=True))

    # Гілка вниз-праворуч від Secondary: V_DP > 0.4 В -> DCP
    p.append(arrow(680, 120, 680, 275, color=FIELD, sw=1.6))
    p.append(text(690, 200, "V_DP > 0.4 В\n(перемичка R ≤ 200 Ом)", size=9, color=FIELD, anchor="start"))
    p.append(fitbox(625, 275, 115, 90, "Порт: DCP\nDedicated Charger\nСтрум: 1.5 А\nЛише зарядка", size=9.5, fill="#f0fdf4", stroke=FIELD, sw=1.4, color=FIELD, bold=True))

    # Знизу пояснення
    b, _, _ = textbox(W / 2, 405, "Автомат BC 1.2 за 2 етапи тестування напругою 0.6 В однозначно класифікує SDP, CDP або DCP",
                      size=10, fill="#f8fafc", stroke=MUTED, sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "detection-state-machine.svg"), W, H, *p,
           title="Послідовність станів Primary та Secondary Detection у протоколі BC 1.2")


# ── 4. proprietary-dividers: фірмові схеми резистивних дільників ───────────────
def fig_proprietary_dividers():
    W, H = 760, 330
    p = []

    configs = [
        (105, "Apple 1.0 A", "D+ = 2.0 В, D− = 2.7 В", "R1=75k, R2=49.9k\nR3=43.2k, R4=49.9k", "5 Вт зарядний блок", "#e0e7ff", NEG),
        (255, "Apple 2.1 A", "D+ = 2.7 В, D− = 2.0 В", "R1=43.2k, R2=49.9k\nR3=75k, R4=49.9k", "10 Вт iPad блок", "#e0e7ff", NEG),
        (405, "Apple 2.4 A", "D+ = 2.7 В, D− = 2.7 В", "R1=43.2k, R2=49.9k\nR3=43.2k, R4=49.9k", "12 Вт iPad блок", "#e0e7ff", NEG),
        (555, "Samsung 2.0 A", "D+ = 1.2 В, D− = 1.2 В", "R1=33k, R2=10k\n(обидві лінії 1.2 В)", "Galaxy Tab / Note", "#fef3c7", "#b45309"),
        (675, "BC 1.2 DCP", "D+ замкнено на D−", "R_DCP_DAT ≤ 200 Ом\n(без напруг зміщення)", "Стандартний DCP", "#dcfce7", FIELD),
    ]

    for cx, title, vols, res, note, fill, col in configs:
        w_box = 130 if cx != 675 else 90
        p.append(rect(cx - w_box/2, 45, w_box, 235, fill=fill, stroke=col, sw=1.4, rx=8))
        p.append(text(cx, 70, title, size=12, color=col, bold=True))
        p.append(text(cx, 95, vols, size=9, color=INK, bold=True))
        p.append(line(cx - w_box/2 + 10, 110, cx + w_box/2 - 10, 110, color=col, sw=1.0))
        p.append(fitbox(cx - w_box/2 + 5, 120, w_box - 10, 85, res, size=9, fill=BG, stroke=MUTED, sw=1.0))
        p.append(fitbox(cx - w_box/2 + 5, 215, w_box - 10, 50, note, size=9, fill=fill, stroke=col, sw=1.0, color=col))

    b, _, _ = textbox(W / 2, 305, "Різні виробники задавали струм дільниками напруги від VBUS (5 В), що створювало несумісність до BC 1.2",
                      size=10, fill="#f8fafc", stroke=MUTED, sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "proprietary-dividers.svg"), W, H, *p,
           title="Фірмові схеми кодування струму резистивними дільниками на D+/D-")


# ── 5. auto-detect-controller: контролер автоматичного детекту (TPS2511) ───────
def fig_auto_detect():
    W, H = 760, 340
    p = []

    # Зовнішній контур контролера (наприклад TPS2511)
    p.append(rect(60, 45, 640, 245, fill="#fafaf9", stroke=NEG, sw=1.6, rx=10))
    p.append(text(380, 70, "Контролер порту з авто-детектом (наприклад TPS2511 / CHY100)", size=13, color=NEG, bold=True))

    # Блоки всередині
    # 1. Силовий ключ VBUS
    p.append(fitbox(90, 95, 170, 75, "Силовий ключ VBUS\nОбмеження струму (2.1 А)\nЗахист від КЗ та перегріву\n(Power Switch)", size=9, fill="#eff6ff", stroke=NEG, sw=1.2))

    # 2. Блок моніторингу ліній D+/D-
    p.append(fitbox(290, 95, 180, 75, "Сенсор сигнатур D+/D−\nАналогові компаратори\nДетект імпедансу та напруг\nклієнтського пристрою", size=9, fill="#fef3c7", stroke="#b45309", sw=1.2))

    # 3. Матриця конфігурації
    p.append(fitbox(500, 95, 170, 75, "Матриця комутації:\n• Режим BC 1.2 DCP (коротке)\n• Дільники Apple 2.4A / 1A\n• Дільник Samsung 2.0A", size=9, fill="#f0fdf4", stroke=FIELD, sw=1.2))

    # Зв'язки між блоками
    p.append(arrow(260, 132, 290, 132, color=INK, sw=1.5))
    p.append(arrow(470, 132, 500, 132, color=INK, sw=1.5))

    # Роз'єм праворуч
    p.append(fitbox(180, 195, 400, 75, "Динамічна поведінка:\n1. За замовчуванням виставляє перемичку BC 1.2 DCP\n2. Якщо підключено iPhone/iPad — миттєво підключає дільники 2.7 В / 2.7 В\n3. Якщо підключено Samsung — перемикає на 1.2 В / 1.2 В", size=10, fill=BG, stroke=MUTED, sw=1.2))

    b, _, _ = textbox(W / 2, 315, "Мікросхеми автодетекту емулюють потрібний профіль зарядки для будь-якого підключеного смартфона",
                      size=10, fill="#eef2ff", stroke=NEG, sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "auto-detect-controller.svg"), W, H, *p,
           title="Принцип функціонування контролера порту з авто-детектом")


if __name__ == "__main__":
    fig_power_evolution()
    fig_port_architectures()
    fig_detection_flow()
    fig_proprietary_dividers()
    fig_auto_detect()
    print("Всі фігури згенеровано успішно.")
