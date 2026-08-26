# -*- coding: utf-8 -*-
"""Фігури до статті «Вибір ключа під навантаження на піні МК».
Запуск: python figs.py  -> генерує SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра
COLOR_GPIO = "#8e44ad"   # фіолетовий для МК / логіки
COLOR_BJT  = "#c0392b"   # червоний / теплий для BJT
COLOR_FET  = "#2457d6"   # синій / холодний для MOSFET
COLOR_SAFE = "#27ae60"   # зелений для безпеки / захисту
COLOR_WARN = "#d35400"   # помаранчевий для попереджень


def axes(f, ox, oy, w, h, xlabel, ylabel):
    """Малює осі координат з підписами."""
    f.append(line(ox, oy, ox + w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - h, color=INK, sw=1.8))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        ox + w, oy, ox + w - 8, oy - 4, ox + w - 8, oy + 4, INK))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        ox, oy - h, ox - 4, oy - h + 8, ox + 4, oy - h + 8, INK))
    f.append(text(ox + w, oy + 22, xlabel, size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - h - 8, ylabel, size=12, color=MUTED, anchor="middle"))


# ── 1. Внутрішній каскад GPIO vs Силове навантаження ──
def fig_gpio_vs_load():
    W, H = 820, 420
    f = [text(W / 2, 28, "Конфлікт рівнів: вихідний каскад GPIO проти силового навантаження", size=16, bold=True)]

    # Ліва частина: Внутрішній вихідний каскад GPIO МК
    f.append(rect(30, 60, 360, 330, fill="#fdfefe", stroke=COLOR_GPIO, sw=2, rx=8))
    f.append(text(210, 85, "Вихідний каскад GPIO МК (Push-Pull)", size=13, color=COLOR_GPIO, bold=True))

    # Шина живлення 3.3 В
    f.append(line(70, 120, 210, 120, color=POS, sw=2))
    f.append(text(140, 112, "VDD = 3.3 В", size=11, color=POS, bold=True))

    # Верхній P-FET (R_int ~ 30 Ом)
    f.append(rect(180, 140, 60, 45, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(210, 160, "P-MOS", size=11, bold=True))
    f.append(text(210, 175, "R ≈ 30 Ω", size=10, color=MUTED))
    f.append(line(210, 120, 210, 140, color=LINE, sw=1.5))
    f.append(line(210, 185, 210, 230, color=LINE, sw=1.5))

    # Нижній N-FET (R_int ~ 30 Ом)
    f.append(rect(180, 230, 60, 45, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(210, 250, "N-MOS", size=11, bold=True))
    f.append(text(210, 265, "R ≈ 30 Ω", size=10, color=MUTED))
    f.append(line(210, 275, 210, 310, color=LINE, sw=1.5))

    # Земля МК
    f.append(line(160, 310, 260, 310, color=INK, sw=2))
    f.append(text(210, 328, "GND (0 В)", size=11, color=MUTED))

    # Вивід піна
    f.append(circle(290, 210, 6, fill=COLOR_GPIO, stroke=INK, sw=1.5))
    f.append(line(210, 210, 290, 210, color=COLOR_GPIO, sw=2.5))
    f.append(text(290, 198, "Пін GPIO", size=11, color=COLOR_GPIO, bold=True))

    # Обмеження GPIO
    f.append(rect(50, 340, 320, 40, fill="#fbf0f0", stroke=POS, sw=1, rx=4))
    f.append(text(210, 356, "Макс. струм піна: 8–20 мА", size=11, color=POS, bold=True))
    f.append(text(210, 372, "Сумарно по кристалу: ≤ 100–150 мА", size=10, color=POS))

    # Права частина: Силове навантаження безпосередньо (Аварія)
    f.append(rect(430, 60, 360, 330, fill="#fdf6f0", stroke=COLOR_WARN, sw=2, rx=8))
    f.append(text(610, 85, "Спроба прямого підключення (АВАРІЯ)", size=13, color=POS, bold=True))

    # Силова шина 12 В / 24 В
    f.append(line(460, 120, 610, 120, color=POS, sw=2.5))
    f.append(text(535, 112, "V_LOAD = +12 В / +24 В", size=11, color=POS, bold=True))

    # Навантаження (мотор / реле / LED 2A)
    f.append(rect(570, 140, 80, 60, fill="#fff2e6", stroke=COLOR_WARN, sw=1.8))
    f.append(text(610, 165, "Мотор / Реле", size=11, bold=True))
    f.append(text(610, 185, "I = 0.5..3 А", size=11, color=POS, bold=True))
    f.append(line(610, 120, 610, 140, color=POS, sw=2))

    # Дріт до піна
    f.append(arrow(610, 200, 610, 250, color=POS, sw=2.5))
    f.append(line(610, 250, 300, 250, color=POS, sw=2.5, dash="4 3"))

    # Наслідки аварії
    f.append(rect(450, 260, 320, 115, fill="#fff", stroke=POS, sw=1.5, rx=6))
    f.append(text(610, 280, "Чому кристал миттєво згорає:", size=11, color=POS, bold=True))
    f.append(text(610, 300, "1. Струм 2 А через пін -> виділення тепла > 10 Вт", size=10, color=INK))
    f.append(text(610, 318, "2. Напруга 12 В пробиває захисні діоди GPIO", size=10, color=INK))
    f.append(text(610, 336, "3. Зворотна ЕРС котушки (100–500 В) спалює ядро", size=10, color=INK))
    f.append(text(610, 356, "4. Просідання VDD викликає Brown-out Reset", size=10, color=INK))

    render(os.path.join(IMG, "gpio-vs-load.svg"), W, H, *f)


# ── 2. ВАХ BJT: Лінійний режим проти Глибокого Насичення ──
def fig_bjt_saturation():
    W, H = 800, 440
    f = [text(W / 2, 28, "Вихідні характеристики BJT: небезпека лінійного режиму та вимушене насичення", size=15, bold=True)]

    ox, oy, w, h = 90, 350, 640, 270
    axes(f, ox, oy, w, h, "Напруга колектор-емітер V_CE (В)", "Струм колектора I_C (А)")

    # Зона глибокого насичення (вертикальна смуга зліва)
    f.append(rect(ox, oy - h + 20, 80, h - 20, fill="#e8f8f5", stroke="#a3e4d7", sw=1))
    f.append(text(ox + 40, oy - h + 40, "ГЛИБОКЕ", size=11, color=COLOR_SAFE, bold=True))
    f.append(text(ox + 40, oy - h + 55, "НАСИЧЕННЯ", size=11, color=COLOR_SAFE, bold=True))
    f.append(text(ox + 40, oy - h + 72, "h_FE_sat ≈ 10", size=10, color=COLOR_SAFE))
    f.append(text(ox + 40, oy - h + 88, "V_CE ≈ 0.15–0.25 В", size=9, color=COLOR_SAFE))

    # Зона лінійного підсилення (активний режим)
    f.append(text(ox + 360, oy - h + 40, "АКТИВНИЙ РЕЖИМ (ПІДСИЛЕННЯ): h_FE = 100–300", size=12, color=COLOR_WARN, bold=True))
    f.append(text(ox + 360, oy - h + 58, "Небезпечно для ключа: V_CE = 1..5 В -> кристал миттєво перегрівається!", size=10, color=COLOR_WARN))

    # Криві струму колектора при різних струмах бази
    ib_list = [
        (30, "I_B = 30 мА (глибоке насичення, I_C = 300 мА)", COLOR_SAFE, 2.4),
        (20, "I_B = 20 мА", "#16a085", 1.8),
        (10, "I_B = 10 мА (початок насичення)", "#2980b9", 1.8),
        (3,  "I_B = 1.5 мА (розрахунок за h_FE = 200 -> пастка!)", COLOR_WARN, 2.2),
        (0.5, "I_B = 0 (відсічка)", MUTED, 1.5)
    ]

    for ib, lbl, col, sw in ib_list:
        pts = []
        max_ic = min(ib * 12.0, 240.0)
        # ділянка насичення (крутий підйом від 0 до 0.25 В)
        for step in range(0, 11):
            v = (step / 10.0) * 0.25
            curr = max_ic * (step / 10.0)
            pts.append((ox + (v / 5.0) * w, oy - (curr / 260.0) * (h - 30)))
        # ділянка активного режиму (майже горизонтальна з невеликим нахилом Ерлі)
        for step in range(1, 41):
            v = 0.25 + (step / 40.0) * 4.75
            curr = max_ic + (step / 40.0) * (max_ic * 0.08)
            pts.append((ox + (v / 5.0) * w, oy - (curr / 260.0) * (h - 30)))

        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' %
                 (" ".join("%.1f,%.1f" % p for p in pts), col, sw))

    # Позначка на кривій лінійного режиму (пастка)
    trap_x = ox + (1.8 / 5.0) * w
    trap_y = oy - (45.0 / 260.0) * (h - 30)
    f.append(circle(trap_x, trap_y, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(line(trap_x, trap_y, trap_x + 50, trap_y - 40, color=POS, sw=1.5))
    f.append(rect(trap_x + 50, trap_y - 65, 230, 45, fill="#fff2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(trap_x + 165, trap_y - 48, "Пастка: V_CE = 1.8 В", size=10, color=POS, bold=True))
    f.append(text(trap_x + 165, trap_y - 32, "P = 1.8 В · 0.3 А = 0.54 Вт (перегрів!)", size=9, color=POS))

    # Позначка на точці насичення
    sat_x = ox + (0.2 / 5.0) * w
    sat_y = oy - (240.0 / 260.0) * (h - 30)
    f.append(circle(sat_x, sat_y, 6, fill=COLOR_SAFE, stroke=INK, sw=1.5))
    f.append(line(sat_x, sat_y, sat_x + 70, sat_y + 20, color=COLOR_SAFE, sw=1.5))
    f.append(rect(sat_x + 70, sat_y + 5, 230, 45, fill="#eafaf1", stroke=COLOR_SAFE, sw=1.2, rx=4))
    f.append(text(sat_x + 185, sat_y + 22, "Правильно: V_CE(sat) = 0.2 В", size=10, color=COLOR_SAFE, bold=True))
    f.append(text(sat_x + 185, sat_y + 38, "P = 0.2 В · 0.3 А = 0.06 Вт (холодний)", size=9, color=COLOR_SAFE))

    # Підписи напруг по осі X
    f.append(line(ox + (0.25 / 5.0) * w, oy, ox + (0.25 / 5.0) * w, oy + 6, color=INK, sw=1.5))
    f.append(text(ox + (0.25 / 5.0) * w, oy + 18, "0.25 В", size=10, color=MUTED, anchor="middle"))

    f.append(line(ox + (3.3 / 5.0) * w, oy, ox + (3.3 / 5.0) * w, oy + 6, color=INK, sw=1.5))
    f.append(text(ox + (3.3 / 5.0) * w, oy + 18, "3.3 В", size=10, color=MUTED, anchor="middle"))

    f.append(line(ox + (5.0 / 5.0) * w, oy, ox + (5.0 / 5.0) * w, oy + 6, color=INK, sw=1.5))
    f.append(text(ox + (5.0 / 5.0) * w, oy + 18, "5.0 В", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "bjt-saturation.svg"), W, H, *f)


# ── 3. Графік R_ds(on) vs V_gs: Порівняння Logic-Level та Standard FET ──
def fig_mosfet_vgs_curves():
    W, H = 820, 450
    f = [text(W / 2, 28, "Криві R_DS(on) від напруги затвора V_GS: чому стандартний MOSFET згорає від 3.3 В", size=15, bold=True)]

    ox, oy, w, h = 90, 360, 650, 280
    axes(f, ox, oy, w, h, "Напруга затвор-виток V_GS (В)", "Опір відкритого каналу R_DS(on) (Ом)")

    # Лінії логічних рівнів 3.3 В та 5.0 В
    x_3v3 = ox + (3.3 / 10.0) * w
    x_5v0 = ox + (5.0 / 10.0) * w
    x_10v = ox + (10.0 / 10.0) * w

    f.append(line(x_3v3, oy, x_3v3, oy - h + 20, color=COLOR_GPIO, sw=1.5, dash="4 4"))
    f.append(text(x_3v3, oy + 18, "3.3 В (МК)", size=11, color=COLOR_GPIO, bold=True, anchor="middle"))

    f.append(line(x_5v0, oy, x_5v0, oy - h + 20, color="#7f8c8d", sw=1.2, dash="4 4"))
    f.append(text(x_5v0, oy + 18, "5.0 В (TTL)", size=10, color=MUTED, anchor="middle"))

    f.append(line(x_10v, oy, x_10v, oy - h + 20, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(x_10v, oy + 18, "10.0 В (Gate Driver)", size=10, color=MUTED, anchor="middle"))

    # Крива 1: Стандартний MOSFET (IRFZ44N / IRF540N) - червона
    pts_std = []
    for i in range(15, 101):
        v = i / 10.0
        if v < 2.5:
            r = 50.0
        elif v < 4.0:
            r = 50.0 / ((v - 2.0) ** 3 + 0.1)
        else:
            r = 0.02 + 1.8 / ((v - 3.2) ** 2)
        r = min(r, 15.0)
        pts_std.append((ox + (v / 10.0) * w, oy - (r / 16.0) * (h - 20)))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_std), POS))

    # Крива 2: Logic-Level MOSFET (AO3400A / IRLZ44N) - синя
    pts_logic = []
    for i in range(8, 101):
        v = i / 10.0
        if v < 1.0:
            r = 30.0
        elif v < 2.0:
            r = 0.5 / ((v - 0.7) ** 2 + 0.05)
        else:
            r = 0.025 + 0.06 / (v - 1.2)
        r = min(r, 15.0)
        pts_logic.append((ox + (v / 10.0) * w, oy - (r / 16.0) * (h - 20)))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_logic), COLOR_FET))

    # Позначка для стандартного FET при 3.3 В
    f.append(circle(x_3v3, oy - (6.5 / 16.0) * (h - 20), 6, fill=POS, stroke=INK, sw=1.5))
    f.append(rect(x_3v3 + 15, oy - (6.5 / 16.0) * (h - 20) - 45, 270, 50, fill="#fdf2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(x_3v3 + 150, oy - (6.5 / 16.0) * (h - 20) - 30, "IRFZ44N при 3.3 В: R_DS ≈ 6–10 Ом", size=10, color=POS, bold=True))
    f.append(text(x_3v3 + 150, oy - (6.5 / 16.0) * (h - 20) - 12, "При струмі 2 А -> P = 24–40 Вт (вибух)", size=9, color=POS))

    # Позначка для Logic-Level FET при 3.3 В
    f.append(circle(x_3v3, oy - (0.05 / 16.0) * (h - 20), 6, fill=COLOR_SAFE, stroke=INK, sw=1.5))
    f.append(rect(x_3v3 + 15, oy - (0.05 / 16.0) * (h - 20) - 60, 270, 50, fill="#eafaf1", stroke=COLOR_SAFE, sw=1.2, rx=4))
    f.append(text(x_3v3 + 150, oy - (0.05 / 16.0) * (h - 20) - 45, "AO3400A при 3.3 В: R_DS ≈ 0.035 Ом", size=10, color=COLOR_SAFE, bold=True))
    f.append(text(x_3v3 + 150, oy - (0.05 / 16.0) * (h - 20) - 27, "При струмі 2 А -> P = 0.14 Вт (холодний)", size=9, color=COLOR_SAFE))

    # Легенда
    f.append(rect(ox + 350, oy - h + 30, 280, 55, fill="#fff", stroke=MUTED, sw=1, rx=6))
    f.append(line(ox + 365, oy - h + 48, ox + 395, oy - h + 48, color=POS, sw=3))
    f.append(text(ox + 405, oy - h + 52, "Стандартний FET (V_GS = 10 В)", size=10, color=INK, anchor="start"))
    f.append(line(ox + 365, oy - h + 70, ox + 395, oy - h + 70, color=COLOR_FET, sw=3))
    f.append(text(ox + 405, oy - h + 74, "Logic-Level FET (повне відкриття при 2.5–3.3 В)", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "mosfet-vgs-curves.svg"), W, H, *f)


# ── 4. Схемотехніка обв'язки затвора MOSFET (R_gate, R_pull, Драйвер) ──
def fig_gate_drive_circuit():
    W, H = 840, 460
    f = [text(W / 2, 28, "Схемотехніка керування затвором: пряме підключення та драйвер затвора", size=15, bold=True)]

    # Ліва схема: Пряме керування Low-Side N-MOSFET від 3.3 В GPIO
    f.append(rect(25, 60, 380, 370, fill="#fdfefe", stroke=COLOR_GPIO, sw=1.8, rx=8))
    f.append(text(215, 85, "1. Пряме керування Low-Side (ШІМ ≤ 10 кГц)", size=12, color=COLOR_GPIO, bold=True))

    # Пін МК
    f.append(rect(45, 180, 70, 45, fill="#ede7f6", stroke=COLOR_GPIO, sw=1.5, rx=4))
    f.append(text(80, 200, "GPIO", size=11, color=COLOR_GPIO, bold=True))
    f.append(text(80, 215, "3.3 В", size=10, color=COLOR_GPIO))

    # Послідовний резистор R_gate (100–330 Ом)
    f.append(line(115, 202, 160, 202, color=LINE, sw=1.8))
    f.append(rect(160, 192, 50, 20, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(185, 206, "R_gate", size=10, bold=True))
    f.append(text(185, 182, "100–330 Ω", size=9, color=MUTED))
    f.append(line(210, 202, 260, 202, color=LINE, sw=1.8))

    # Стягувальний резистор R_pull (10–100 кОм)
    f.append(circle(240, 202, 3, fill=INK, stroke=INK))
    f.append(line(240, 202, 240, 260, color=LINE, sw=1.5))
    f.append(rect(230, 260, 20, 45, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(240, 287, "R_p", size=9, bold=True))
    f.append(text(275, 287, "10–100 kΩ", size=9, color=MUTED))
    f.append(line(240, 305, 240, 335, color=LINE, sw=1.5))
    f.append(line(220, 335, 260, 335, color=INK, sw=2)) # Земля

    # Транзистор Logic N-FET
    f.append(rect(260, 175, 65, 55, fill="#ebf5fb", stroke=COLOR_FET, sw=1.8, rx=4))
    f.append(text(292, 195, "N-FET", size=11, color=COLOR_FET, bold=True))
    f.append(text(292, 212, "Logic", size=10, color=COLOR_FET))

    # Навантаження та живлення 12 В
    f.append(line(292, 175, 292, 145, color=LINE, sw=1.8))
    f.append(rect(267, 105, 50, 40, fill="#fff2e6", stroke=COLOR_WARN, sw=1.5))
    f.append(text(292, 128, "LOAD", size=10, bold=True))
    f.append(line(292, 105, 292, 85, color=POS, sw=2))
    f.append(text(292, 78, "+12 В", size=10, color=POS, bold=True))

    # Виток до землі
    f.append(line(292, 230, 292, 335, color=LINE, sw=1.8))
    f.append(line(275, 335, 310, 335, color=INK, sw=2))
    f.append(text(292, 350, "GND", size=10, color=MUTED))

    # Пояснення обв'язки
    f.append(rect(35, 365, 360, 55, fill="#f8f9fa", stroke=MUTED, sw=1, rx=4))
    f.append(text(215, 382, "• R_gate обмежує піковий струм заряду C_iss", size=10, color=INK))
    f.append(text(215, 402, "• R_pull тримає 0 В при Reset / High-Z піна МК", size=10, color=INK))

    # Права схема: Керування через Gate Driver (TC4427 / MCP1407) для потужного ШІМ
    f.append(rect(430, 60, 385, 370, fill="#fdfefe", stroke=COLOR_SAFE, sw=1.8, rx=8))
    f.append(text(622, 85, "2. Драйвер затвора (ШІМ 20–200 кГц, струм до 6 А)", size=12, color=COLOR_SAFE, bold=True))

    # Пін МК
    f.append(rect(445, 180, 60, 45, fill="#ede7f6", stroke=COLOR_GPIO, sw=1.5, rx=4))
    f.append(text(475, 200, "GPIO", size=10, color=COLOR_GPIO, bold=True))
    f.append(text(475, 215, "3.3 В", size=9, color=COLOR_GPIO))

    # Драйвер затвора TC4427
    f.append(rect(530, 160, 85, 85, fill="#e8f8f5", stroke=COLOR_SAFE, sw=2, rx=6))
    f.append(text(572, 185, "Gate Driver", size=11, color=COLOR_SAFE, bold=True))
    f.append(text(572, 202, "TC4427 / MCP1407", size=9, color=COLOR_SAFE))
    f.append(text(572, 225, "I_peak = 1.5–6 А", size=9, color=POS, bold=True))
    f.append(line(505, 202, 530, 202, color=LINE, sw=1.5))

    # Живлення драйвера 12 В
    f.append(line(572, 160, 572, 115, color=POS, sw=2))
    f.append(text(572, 108, "VDD = +12 В", size=10, color=POS, bold=True))
    f.append(line(572, 245, 572, 335, color=LINE, sw=1.5))
    f.append(line(555, 335, 590, 335, color=INK, sw=2)) # Земля

    # Вихід драйвера до MOSFET через малий R_g (4.7–10 Ом)
    f.append(line(615, 202, 650, 202, color=LINE, sw=1.8))
    f.append(rect(650, 194, 35, 16, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(667, 206, "10 Ω", size=9))
    f.append(line(685, 202, 720, 202, color=LINE, sw=1.8))

    # Силовий MOSFET
    f.append(rect(720, 175, 70, 55, fill="#ebf5fb", stroke=COLOR_FET, sw=1.8, rx=4))
    f.append(text(755, 195, "Power FET", size=10, color=COLOR_FET, bold=True))
    f.append(text(755, 212, "IRFB4110", size=9, color=COLOR_FET))

    # Навантаження силового FET
    f.append(line(755, 175, 755, 145, color=LINE, sw=1.8))
    f.append(rect(730, 105, 50, 40, fill="#fff2e6", stroke=COLOR_WARN, sw=1.5))
    f.append(text(755, 128, "HEAVY", size=9, bold=True))
    f.append(line(755, 105, 755, 85, color=POS, sw=2))
    f.append(text(755, 78, "+24 В", size=10, color=POS, bold=True))

    f.append(line(755, 230, 755, 335, color=LINE, sw=1.8))
    f.append(line(740, 335, 770, 335, color=INK, sw=2))

    # Пояснення переваг драйвера
    f.append(rect(440, 365, 365, 55, fill="#f8f9fa", stroke=MUTED, sw=1, rx=4))
    f.append(text(622, 382, "• Перезаряджає C_iss за 20–40 наносекунд", size=10, color=INK))
    f.append(text(622, 402, "• Знижує динамічні втрати перемикання P_sw у 50 разів", size=10, color=INK))

    render(os.path.join(IMG, "gate-drive-circuit.svg"), W, H, *f)


# ── 5. Захист від індуктивних викидів (Flyback діод, Snubber, TVS) ──
def fig_inductive_protection():
    W, H = 840, 440
    f = [text(W / 2, 28, "Захист силового ключа від індуктивного викиду зворотної ЕРС (e = −L · di/dt)", size=15, bold=True)]

    # 1. Flyback діод Шотткі
    f.append(rect(25, 60, 245, 360, fill="#fdfefe", stroke=COLOR_SAFE, sw=1.5, rx=6))
    f.append(text(147, 85, "1. Зворотний діод Шотткі", size=12, color=COLOR_SAFE, bold=True))

    # Силова шина
    f.append(line(50, 110, 240, 110, color=POS, sw=2))
    f.append(text(147, 102, "+V_LOAD (+12 В / +24 В)", size=9, color=POS, bold=True))

    # Індуктивність
    f.append(rect(60, 140, 60, 70, fill="#fff2e6", stroke=COLOR_WARN, sw=1.5))
    f.append(text(90, 170, "Котушка", size=10, bold=True))
    f.append(text(90, 188, "L, R_coil", size=9, color=MUTED))
    f.append(line(90, 110, 90, 140, color=LINE, sw=1.5))
    f.append(line(90, 210, 90, 260, color=LINE, sw=1.5))

    # Діод паралельно котушці (катод до +, анод до стоку)
    f.append(line(190, 110, 190, 150, color=LINE, sw=1.5))
    f.append(rect(170, 150, 40, 50, fill="#e8f8f5", stroke=COLOR_SAFE, sw=1.5))
    f.append(text(190, 172, "D_fly", size=10, color=COLOR_SAFE, bold=True))
    f.append(text(190, 190, "Шотткі", size=9, color=COLOR_SAFE))
    f.append(line(190, 200, 190, 235, color=LINE, sw=1.5))
    f.append(line(190, 235, 90, 235, color=LINE, sw=1.5))

    # Ключ
    f.append(rect(65, 260, 50, 40, fill="#ebf5fb", stroke=COLOR_FET, sw=1.5))
    f.append(text(90, 285, "MOSFET", size=9, bold=True))
    f.append(line(90, 300, 90, 330, color=LINE, sw=1.5))
    f.append(line(75, 330, 105, 330, color=INK, sw=2))

    f.append(rect(35, 350, 225, 60, fill="#f8f9fa", stroke=MUTED, sw=1, rx=4))
    f.append(text(147, 368, "• Затискає викид до V_DD + 0.4 В", size=9, color=INK))
    f.append(text(147, 385, "• Повільне відпускання реле", size=9, color=INK))
    f.append(text(147, 402, "• При ШІМ: діод Шотткі (SS34)", size=9, color=POS, bold=True))

    # 2. RC-демпфер (Snubber)
    f.append(rect(295, 60, 245, 360, fill="#fdfefe", stroke=COLOR_FET, sw=1.5, rx=6))
    f.append(text(417, 85, "2. RC-демпфер (Snubber)", size=12, color=COLOR_FET, bold=True))

    f.append(line(320, 110, 510, 110, color=POS, sw=2))
    f.append(text(417, 102, "+V_LOAD", size=9, color=POS, bold=True))

    f.append(rect(330, 140, 60, 70, fill="#fff2e6", stroke=COLOR_WARN, sw=1.5))
    f.append(text(360, 170, "Котушка /", size=10, bold=True))
    f.append(text(360, 188, "Мотор", size=10, bold=True))
    f.append(line(360, 110, 360, 140, color=LINE, sw=1.5))
    f.append(line(360, 210, 360, 260, color=LINE, sw=1.5))

    # RC-коло
    f.append(line(460, 110, 460, 145, color=LINE, sw=1.5))
    f.append(rect(445, 145, 30, 25, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(460, 162, "R_s", size=9, bold=True))
    f.append(line(460, 170, 460, 185, color=LINE, sw=1.5))
    f.append(rect(445, 185, 30, 25, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(460, 202, "C_s", size=9, bold=True))
    f.append(line(460, 210, 460, 235, color=LINE, sw=1.5))
    f.append(line(460, 235, 360, 235, color=LINE, sw=1.5))

    f.append(rect(335, 260, 50, 40, fill="#ebf5fb", stroke=COLOR_FET, sw=1.5))
    f.append(text(360, 285, "MOSFET", size=9, bold=True))
    f.append(line(360, 300, 360, 330, color=LINE, sw=1.5))
    f.append(line(345, 330, 375, 330, color=INK, sw=2))

    f.append(rect(305, 350, 225, 60, fill="#f8f9fa", stroke=MUTED, sw=1, rx=4))
    f.append(text(417, 368, "• Поглинає ВЧ-дзвін і завади EMI", size=9, color=INK))
    f.append(text(417, 385, "• Обмежує швидкість dv/dt", size=9, color=INK))
    f.append(text(417, 402, "• Типово: 10–47 Ω + 1–10 нФ", size=9, color=COLOR_FET, bold=True))

    # 3. TVS-супресор / Зенер-кламп
    f.append(rect(565, 60, 245, 360, fill="#fdfefe", stroke=COLOR_WARN, sw=1.5, rx=6))
    f.append(text(687, 85, "3. TVS-супресор (Кламп)", size=12, color=COLOR_WARN, bold=True))

    f.append(line(590, 110, 780, 110, color=POS, sw=2))
    f.append(text(687, 102, "+V_LOAD", size=9, color=POS, bold=True))

    f.append(rect(600, 140, 60, 70, fill="#fff2e6", stroke=COLOR_WARN, sw=1.5))
    f.append(text(630, 170, "Швидке", size=10, bold=True))
    f.append(text(630, 188, "Реле", size=10, bold=True))
    f.append(line(630, 110, 630, 140, color=LINE, sw=1.5))
    f.append(line(630, 210, 630, 260, color=LINE, sw=1.5))

    # TVS або Діод + Стабілітрон
    f.append(line(730, 110, 730, 150, color=LINE, sw=1.5))
    f.append(rect(710, 150, 40, 50, fill="#fff5eb", stroke=COLOR_WARN, sw=1.5))
    f.append(text(730, 172, "TVS", size=10, color=COLOR_WARN, bold=True))
    f.append(text(730, 190, "V_clamp", size=9, color=COLOR_WARN))
    f.append(line(730, 200, 730, 235, color=LINE, sw=1.5))
    f.append(line(730, 235, 630, 235, color=LINE, sw=1.5))

    f.append(rect(605, 260, 50, 40, fill="#ebf5fb", stroke=COLOR_FET, sw=1.5))
    f.append(text(630, 285, "MOSFET", size=9, bold=True))
    f.append(line(630, 300, 630, 330, color=LINE, sw=1.5))
    f.append(line(615, 330, 645, 330, color=INK, sw=2))

    f.append(rect(575, 350, 225, 60, fill="#f8f9fa", stroke=MUTED, sw=1, rx=4))
    f.append(text(687, 368, "• Миттєве розмикання контактів", size=9, color=INK))
    f.append(text(687, 385, "• Швидке згасання магнітного поля", size=9, color=INK))
    f.append(text(687, 402, "• V_clamp < V_DS_max транзистора", size=9, color=COLOR_WARN, bold=True))

    render(os.path.join(IMG, "inductive-protection.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gpio_vs_load()
    fig_bjt_saturation()
    fig_mosfet_vgs_curves()
    fig_gate_drive_circuit()
    fig_inductive_protection()
    print("All figures generated successfully.")
