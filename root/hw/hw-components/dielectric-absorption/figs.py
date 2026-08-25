# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Діелектрична абсорбція'."""
import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_da_phenomenon():
    """Діаграма феномену діелектричної абсорбції: заряд, КЗ та самочинне відновлення напруги."""
    w, h = 760, 360
    frags = []

    # Рамка графіка
    gx, gy, gw, gh = 70, 60, 640, 220
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=MUTED, sw=1))

    # Сітка та осі
    for y_val, lbl in [(gy, "V_charge (100%)"), (gy + gh * 0.5, "50%"), (gy + gh, "0 В")]:
        frags.append(line(gx, y_val, gx + gw, y_val, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(gx - 8, y_val + 4, lbl, size=11, color=MUTED, anchor="end"))

    # Вісь X
    frags.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.5))
    frags.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.5))

    # Зони часу:
    # 0 -> 220px: Заряджання (15 хв)
    # 220 -> 270px: Розряджання / КЗ (5 с)
    # 270 -> 640px: Розімкнення та самочинне відновлення напруги V_recovered
    t1 = gx + 220
    t2 = gx + 270
    t_end = gx + gw

    frags.append(rect(gx, gy, 220, gh, fill="#f0fdf4", stroke="none"))
    frags.append(rect(t1, gy, 50, gh, fill="#fef2f2", stroke="none"))
    frags.append(rect(t2, gy, gw - 270, gh, fill="#eff6ff", stroke="none"))

    frags.append(line(t1, gy, t1, gy + gh, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(t2, gy, t2, gy + gh, color=MUTED, sw=1, dash="2,2"))

    # Крива напруги
    # 1. Заряд: швидкий вихід на V_charge і утримання
    path_d = f"M {gx} {gy + gh} C {gx + 30} {gy + 10}, {gx + 80} {gy}, {t1} {gy}"
    # 2. Миттєвий спад до 0 при КЗ
    path_d += f" L {t1} {gy + gh} L {t2} {gy + gh}"
    # 3. Експоненційне самочинне зростання V_recovered до рівня ~15%
    rec_y = gy + gh - 45  # ~15% висоти
    path_d += f" C {t2 + 40} {gy + gh - 5}, {t2 + 120} {rec_y + 4}, {t_end} {rec_y}"

    frags.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначення зон часу знизу
    frags.append(text(gx + 110, gy + gh + 22, "1. Тривалий заряд (15 хв)", size=12, bold=True, color=FIELD))
    frags.append(text(t1 + 25, gy + gh + 38, "2. КЗ (5 с)", size=11, bold=True, color=POS))
    frags.append(text(t2 + 180, gy + gh + 22, "3. Розімкнення: повільне вивільнення заряду", size=12, bold=True, color=NEG))

    # Стрілка та напис відновленої напруги
    frags.append(line(t_end - 40, gy + gh, t_end - 40, rec_y, color=NEG, sw=1.5))
    frags.append(line(t_end - 45, rec_y, t_end - 35, rec_y, color=NEG, sw=1.5))
    frags.append(text(t_end - 50, rec_y + 16, "V_recovered", size=12, bold=True, color=NEG, anchor="end"))

    # Пояснювальні плашки зверху
    frags.append(textbox(gx + 110, gy + 35, "Діелектрик глибоко поляризується\nі накопичує зв'язані заряди", size=11, fill="#ffffff", stroke=FIELD)[0])
    frags.append(textbox(t2 + 180, gy + 50, "Диполі релаксують, а захоплені носії стікають:\nнапруга на обкладках зростає сама по собі!", size=11, fill="#ffffff", stroke=NEG)[0])

    render(os.path.join(OUT_DIR, "da-phenomenon.svg"), w, h, *frags,
           title="Феномен діелектричної абсорбції: самочинна поява залишкової напруги")


def fig_dielectric_physics():
    """Фізичний механізм абсорбції: швидка поляризація, пастки заряду та релаксація."""
    w, h = 760, 360
    frags = []

    panels = [
        ("а) Тривалий заряд під напругою", 130, "#f0fdf4", FIELD),
        ("б) Коротке замикання (5 с)", 380, "#fef2f2", POS),
        ("в) Після зняття КЗ (відновлення)", 630, "#eff6ff", NEG)
    ]

    for title, cx, bg_col, stroke_col in panels:
        px = cx - 110
        frags.append(rect(px, 50, 220, 280, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        frags.append(text(cx, 72, title, size=12, bold=True, color=stroke_col))

        # Обкладки конденсатора (вертикальні пластини)
        frags.append(rect(px + 20, 95, 12, 160, fill="#d1d5db", stroke=LINE, sw=1))
        frags.append(rect(px + 188, 95, 12, 160, fill="#d1d5db", stroke=LINE, sw=1))

        # Діелектрик між обкладками
        frags.append(rect(px + 32, 95, 156, 160, fill="#ffffff", stroke="#cbd5e1", sw=1))

    # Панель (а): Заряд
    # Заряди на обкладках
    for y in [115, 145, 175, 205, 235]:
        frags.append(plus(30, y, r=5))
        frags.append(minus(218, y, r=5))

    # Диполі та пастки в діелектрику (орієнтовані)
    for y in [120, 160, 200, 240]:
        frags.append(minus(65, y, r=6))
        frags.append(plus(92, y, r=6))
        frags.append(line(71, y, 86, y, color=LINE, sw=1))

        frags.append(minus(130, y, r=6))
        frags.append(plus(157, y, r=6))
        frags.append(line(136, y, 151, y, color=LINE, sw=1))

    frags.append(text(130, 285, "Повне вишиковування диполів\nі заповнення пасток заряду", size=11, color=INK))

    # Панель (б): Коротке замикання
    # Обкладки замкнені дротом
    frags.append(line(290, 85, 470, 85, color=POS, sw=2))
    frags.append(line(290, 85, 290, 95, color=POS, sw=2))
    frags.append(line(470, 85, 470, 95, color=POS, sw=2))
    frags.append(textbox(380, 85, "КЗ: швидкий розряд", size=10, fill="#ffffff", stroke=POS, pad=4)[0])

    # На обкладках зарядів нема (розрядилися)
    # Але в діелектрику диполі ще не встигли розвернутися назад!
    for y in [120, 160, 200, 240]:
        frags.append(minus(315, y, r=6))
        frags.append(plus(342, y, r=6))
        frags.append(line(321, y, 336, y, color=LINE, sw=1))

        frags.append(minus(380, y, r=6))
        frags.append(plus(407, y, r=6))
        frags.append(line(386, y, 401, y, color=LINE, sw=1))

    frags.append(text(380, 285, "Обкладки розряджені до 0 В,\nале поляризація 'заморожена'", size=11, color=INK))

    # Панель (в): Відновлення
    # Диполі повільно релаксують, виштовхуючи наведені заряди на вільні обкладки
    for y in [125, 175, 225]:
        # Частина диполів розвернулася хаотично
        frags.append(circle(565, y, r=4, fill="#9ca3af", stroke="none"))
        frags.append(circle(630, y, r=4, fill="#9ca3af", stroke="none"))

    # На обкладках знову з'являється заряд!
    frags.append(plus(540, 140, r=5))
    frags.append(plus(540, 210, r=5))
    frags.append(minus(728, 140, r=5))
    frags.append(minus(728, 210, r=5))

    # Вольтметр фіксує напругу
    frags.append(textbox(630, 85, "V_recovered > 0 В", size=11, fill="#ffffff", stroke=NEG, bold=True, pad=5)[0])
    frags.append(text(630, 285, "Залишкова поляризація\nстворює вторинну напругу", size=11, color=INK))

    render(os.path.join(OUT_DIR, "dielectric-physics.svg"), w, h, *frags,
           title="Мікроскопічний механізм: затримка релаксації диполів та вивільнення зв'язаних зарядів")


def fig_debye_model():
    """Еквівалентна багатоланкова схема Дебая для конденсатора з діелектричною абсорбцією."""
    w, h = 760, 320
    frags = []

    # Верхня і нижня шини
    frags.append(line(50, 80, 710, 80, color=LINE, sw=2))
    frags.append(line(50, 250, 710, 250, color=LINE, sw=2))

    # Вхідні клеми
    frags.append(circle(50, 80, r=4, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(circle(50, 250, r=4, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(35, 84, "A", size=13, bold=True))
    frags.append(text(35, 254, "B", size=13, bold=True))

    # Паразитні послідовні елементи: ESR + ESL на верхній шині
    frags.append(textbox(100, 80, "ESR", size=11, fill="#ffffff", stroke=MUTED)[0])
    frags.append(textbox(150, 80, "ESL", size=11, fill="#ffffff", stroke=MUTED)[0])

    # 1. Основна ємність C0
    c0_x = 220
    frags.append(line(c0_x, 80, c0_x, 145, color=LINE, sw=1.5))
    frags.append(line(c0_x - 18, 145, c0_x + 18, 145, color=LINE, sw=2.5))
    frags.append(line(c0_x - 18, 155, c0_x + 18, 155, color=LINE, sw=2.5))
    frags.append(line(c0_x, 155, c0_x, 250, color=LINE, sw=1.5))
    frags.append(text(c0_x + 28, 154, "C₀", size=13, bold=True, color=FIELD))
    frags.append(text(c0_x, 280, "Основна ємність\n(швидка)", size=11, color=FIELD))

    # 2. Опір витоку R_leak
    r_leak_x = 320
    frags.append(line(r_leak_x, 80, r_leak_x, 130, color=LINE, sw=1.5))
    frags.append(textbox(r_leak_x, 150, "R_leak", size=11, fill="#ffffff", stroke=MUTED)[0])
    frags.append(line(r_leak_x, 170, r_leak_x, 250, color=LINE, sw=1.5))
    frags.append(text(r_leak_x, 280, "Опір ізоляції\n(> 10¹⁰ Ом)", size=11, color=MUTED))

    # 3. Гілки Дебая: r1-c1, r2-c2, ..., rn-cn
    branches = [
        (430, "r₁", "c₁", "τ₁ ≈ 10 мс", "Швидкі диполі"),
        (540, "r₂", "c₂", "τ₂ ≈ 1 с", "Сегменти ланцюгів"),
        (650, "rₙ", "cₙ", "τₙ ≈ 1000 с", "Глибокі пастки")
    ]

    for bx, r_lbl, c_lbl, tau_lbl, desc in branches:
        # Вертикальний дріт від верхньої шини
        frags.append(line(bx, 80, bx, 115, color=LINE, sw=1.5))
        # Резистор r_i
        frags.append(textbox(bx, 125, r_lbl, size=11, fill="#ffffff", stroke=POS, pad=4)[0])
        frags.append(line(bx, 137, bx, 160, color=LINE, sw=1.5))
        # Конденсатор c_i
        frags.append(line(bx - 14, 160, bx + 14, 160, color=LINE, sw=2))
        frags.append(line(bx - 14, 168, bx + 14, 168, color=LINE, sw=2))
        frags.append(text(bx + 24, 167, c_lbl, size=11, bold=True, color=NEG))
        # Дріт до нижньої шини (розірваний під плашку tau_lbl)
        frags.append(line(bx, 168, bx, 196, color=LINE, sw=1.5))
        frags.append(line(bx, 224, bx, 250, color=LINE, sw=1.5))
        # Підпис константи часу
        frags.append(textbox(bx, 210, tau_lbl, size=10, fill="#fef2f2", stroke=POS, pad=3)[0])
        frags.append(text(bx, 280, desc, size=11, color=INK))

    # Пунктир між гілками Дебая (символ багатьох ланок)
    frags.append(text(595, 150, "...", size=16, bold=True, color=MUTED))

    # Об'єднувальна дужка або рамка моделі абсорбції
    frags.append('<rect x="380.0" y="50.0" width="320.0" height="220.0" rx="8" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % POS)
    frags.append(textbox(540, 50, "Абсорбційні гілки релаксації Дебая (Dielectric Soakage)", size=11, fill="#ffffff", stroke=POS, bold=True)[0])

    render(os.path.join(OUT_DIR, "debye-model.svg"), w, h, *frags,
           title="Багатоланкова схема Дебая: спектр часових констант релаксації діелектрика")


def fig_sample_and_hold_error():
    """Вплив діелектричної абсорбції на схему вибірки-зберігання (Sample-and-Hold)."""
    w, h = 760, 340
    frags = []

    # Ліва частина: Спрощена схема S/H
    sx, sy = 50, 60
    frags.append(rect(sx, sy, 290, 245, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(sx + 145, sy + 22, "Схема вибірки-зберігання (S/H)", size=12, bold=True, color=INK))

    # Вхідний буфер -> ключ -> Chold -> вихідний буфер
    frags.append(line(sx + 20, sy + 80, sx + 50, sy + 80, color=LINE, sw=1.5))
    frags.append(textbox(sx + 75, sy + 80, "Буфер\nвходу", size=10, fill="#ffffff", stroke=LINE)[0])

    # Ключ (відкритий/закритий)
    frags.append(line(sx + 105, sy + 80, sx + 130, sy + 80, color=LINE, sw=1.5))
    frags.append(line(sx + 130, sy + 80, sx + 155, sy + 65, color=POS, sw=2)) # піднятий контакт
    frags.append(circle(sx + 130, sy + 80, r=3, fill=LINE, stroke="none"))
    frags.append(circle(sx + 160, sy + 80, r=3, fill=LINE, stroke="none"))
    frags.append(text(sx + 145, sy + 52, "Ключ Hold", size=10, color=POS, bold=True))

    # Вузол збереження і конденсатор C_hold
    frags.append(line(sx + 160, sy + 80, sx + 220, sy + 80, color=LINE, sw=1.5))
    frags.append(line(sx + 190, sy + 80, sx + 190, sy + 130, color=LINE, sw=1.5))
    frags.append(line(sx + 175, sy + 130, sx + 205, sy + 130, color=LINE, sw=2.5))
    frags.append(line(sx + 175, sy + 138, sx + 205, sy + 138, color=LINE, sw=2.5))
    frags.append(line(sx + 190, sy + 138, sx + 190, sy + 170, color=LINE, sw=1.5))
    # Земля
    frags.append(line(sx + 180, sy + 170, sx + 200, sy + 170, color=LINE, sw=1.5))
    frags.append(line(sx + 184, sy + 174, sx + 196, sy + 174, color=LINE, sw=1.5))
    frags.append(text(sx + 230, sy + 136, "C_hold", size=11, bold=True, color=FIELD))

    # Вихідний буфер
    frags.append(textbox(sx + 245, sy + 80, "Буфер\nFET", size=10, fill="#ffffff", stroke=LINE)[0])
    frags.append(line(sx + 270, sy + 80, sx + 285, sy + 80, color=LINE, sw=1.5))
    frags.append(text(sx + 275, sy + 70, "V_out", size=10, bold=True))

    frags.append(textbox(sx + 145, sy + 215, "Якщо C_hold має високу DA:\nзаряд стікає вглиб діелектрика під час Hold!", size=10, fill="#fef2f2", stroke=POS)[0])

    # Права частина: Графік напруги під час Track і Hold
    gx, gy, gw, gh = 375, 60, 350, 245
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(gx + gw/2, gy + 22, "Спотворення вибірки через абсорбцію", size=12, bold=True, color=INK))

    # Осі
    frags.append(line(gx + 35, gy + gh - 40, gx + gw - 20, gy + gh - 40, color=INK, sw=1.5))
    frags.append(line(gx + 35, gy + 45, gx + 35, gy + gh - 40, color=INK, sw=1.5))
    frags.append(text(gx + gw - 20, gy + gh - 25, "Час", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx + 30, gy + 45, "V", size=11, color=MUTED, anchor="end"))

    # Фаза 1: Track (0 -> 100px), Фаза 2: Hold (100 -> 280px)
    fx1 = gx + 130
    frags.append(line(fx1, gy + 45, fx1, gy + gh - 40, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(gx + 80, gy + gh - 25, "Фаза Track", size=11, bold=True, color=FIELD))
    frags.append(text(gx + 220, gy + gh - 25, "Фаза Hold (зберігання)", size=11, bold=True, color=POS))

    # Стрибок вхідної напруги
    # Вхідний сигнал: з 0 до V_in
    vin_y = gy + 80
    frags.append(line(gx + 35, vin_y, fx1, vin_y, color=MUTED, sw=1.5, dash="4,4"))

    # Ідеальний конденсатор (C0G / Тефлон): миттєвий вихід і рівне плато
    frags.append(line(gx + 35, gy + gh - 40, gx + 60, vin_y, color=FIELD, sw=2))
    frags.append(line(gx + 60, vin_y, gx + gw - 30, vin_y, color=FIELD, sw=2))
    frags.append(text(gx + gw - 35, vin_y - 8, "Ідеальне плато (C0G/PP)", size=10, bold=True, color=FIELD, anchor="end"))

    # Реальний конденсатор з DA (Mylar / X7R): просідання напруги під час Hold
    # Під час Track внутрішні ємності Дебая не встигли зарядитися. Після розмикання ключа
    # заряд з обкладок перетікає вглиб діелектрика -> напруга падає!
    droop_d = f"M {gx + 35} {gy + gh - 40} L {gx + 60} {vin_y} L {fx1} {vin_y} C {fx1 + 40} {vin_y + 15}, {fx1 + 100} {vin_y + 35}, {gx + gw - 30} {vin_y + 42}"
    frags.append(f'<path d="{droop_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначення похибки просідання (Voltage Droop)
    err_x = gx + gw - 60
    frags.append(line(err_x, vin_y, err_x, vin_y + 42, color=POS, sw=1.5))
    frags.append(line(err_x - 4, vin_y, err_x + 4, vin_y, color=POS, sw=1.5))
    frags.append(line(err_x - 4, vin_y + 42, err_x + 4, vin_y + 42, color=POS, sw=1.5))
    frags.append(text(err_x - 8, vin_y + 24, "Похибка DA (Droop)", size=10, bold=True, color=POS, anchor="end"))

    frags.append(text(gx + 220, gy + 175, "Реальна напруга спадає,\nбо заряд стікає в абсорбційні шари!", size=10, color=POS))

    render(os.path.join(OUT_DIR, "sample-and-hold-error.svg"), w, h, *frags,
           title="Похибка вибірки-зберігання: діелектрична абсорбція руйнує точність АЦП")


def fig_safety_hazard():
    """Небезпека високовольтних конденсаторів для людини через ефект повернення напруги."""
    w, h = 760, 320
    frags = []

    steps = [
        ("1. Робота під 3000 В", 130, "#fef2f2", POS),
        ("2. Швидкий розряд (КЗ)", 380, "#f0fdf4", FIELD),
        ("3. Повернення напруги (150–300 В)", 630, "#fff7ed", "#ea580c")
    ]

    for title, cx, bg_col, stroke_col in steps:
        px = cx - 110
        frags.append(rect(px, 50, 220, 240, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        frags.append(text(cx, 72, title, size=11, bold=True, color=stroke_col))

    # Крок 1: Конденсатор 3000 В
    frags.append(rect(75, 100, 110, 80, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    frags.append(circle(105, 100, r=5, fill=POS, stroke=LINE, sw=1))
    frags.append(circle(155, 100, r=5, fill=NEG, stroke=LINE, sw=1))
    frags.append(text(130, 145, "HV CAP\n3000 В", size=12, bold=True, color=POS))
    frags.append(text(130, 215, "Конденсатор повністю\nзаряджений і поляризований", size=11, color=INK))

    # Крок 2: Розряд заземлювальною штангою
    frags.append(rect(325, 100, 110, 80, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    frags.append(circle(355, 100, r=5, fill=LINE, stroke=LINE, sw=1))
    frags.append(circle(405, 100, r=5, fill=LINE, stroke=LINE, sw=1))
    # Штанга
    frags.append(line(355, 95, 405, 95, color=FIELD, sw=3))
    frags.append(line(380, 95, 380, 65, color=FIELD, sw=3))
    frags.append(textbox(380, 65, "Розрядна штанга (2 с)", size=10, fill="#ffffff", stroke=FIELD, pad=3)[0])
    frags.append(text(380, 145, "V = 0 В\n(миттєво)", size=12, bold=True, color=FIELD))
    frags.append(text(380, 215, "Знято лише зовнішній заряд.\nШтангу прибрали!", size=11, color=INK))

    # Крок 3: Самовільне відновлення напруги і небезпека удару
    frags.append(rect(575, 100, 110, 80, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    frags.append(circle(605, 100, r=5, fill=POS, stroke=LINE, sw=1))
    frags.append(circle(655, 100, r=5, fill=NEG, stroke=LINE, sw=1))
    frags.append(text(630, 135, "V = 250 В!", size=14, bold=True, color=POS))
    frags.append(text(630, 155, "Смертельна напруга!", size=10, bold=True, color=POS))
    frags.append(textbox(630, 215, "Через 15 хв абсорбція\nповернула небезпечний потенціал.\nПотрібна коротильна планка!", size=10, fill="#ffffff", stroke=POS)[0])

    render(os.path.join(OUT_DIR, "safety-hazard.svg"), w, h, *frags,
           title="Небезпека для життя: залишкова напруга на високовольтних конденсаторах")


def main():
    fig_da_phenomenon()
    fig_dielectric_physics()
    fig_debye_model()
    fig_sample_and_hold_error()
    fig_safety_hazard()
    print("Усі 5 фігур успішно згенеровано.")


if __name__ == "__main__":
    main()
