#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Зрізи кварцу: AT, BT, SC та інші'."""

import sys
import os
import math

# Підключаємо svgkit з кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_quartz_axes_and_cuts():
    """Фігура 1: Кристалографічні осі кварцу та орієнтація головних зрізів."""
    W, H = 820, 480
    s = []

    # Заголовок / панелі
    # Ліва панель: Кристал кварцу та його три головні осі
    s.append(rect(20, 20, 370, 440, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    s.append(text(205, 48, "Кристалографічні осі α-кварцу", size=15, bold=True))
    s.append(text(205, 68, "Тригональна сингонія (клас 32, без центра інверсії)", size=12, color=MUTED))

    # Схематичний монокристал кварцу (шестигранна призма з пірамідальними верхівками)
    # Координати проекції
    # Центр кристала (205, 230)
    cx, cy = 205, 230

    # Вертикальна оптична вісь Z (вісь 3-го порядку)
    s.append(arrow(cx, cy + 160, cx, cy - 160, color=LINE, sw=2))
    s.append(text(cx + 12, cy - 145, "Z (оптична вісь)", size=13, bold=True, anchor="start"))
    s.append(text(cx + 12, cy - 130, "п'єзоефект = 0", size=11, color=MUTED, anchor="start"))

    # Вісь X (електрична, 2-й порядок, полярна)
    s.append(arrow(cx - 140, cy + 45, cx + 140, cy - 45, color=POS, sw=2))
    s.append(text(cx + 145, cy - 45, "X (електрична)", size=13, color=POS, bold=True, anchor="start"))
    s.append(text(cx + 145, cy - 30, "поздовжній п'єзоефект", size=11, color=POS, anchor="start"))

    # Вісь Y (механічна)
    s.append(arrow(cx - 110, cy - 70, cx + 110, cy + 70, color=NEG, sw=2))
    s.append(text(cx + 115, cy + 70, "Y (механічна)", size=13, color=NEG, bold=True, anchor="start"))
    s.append(text(cx + 115, cy + 85, "поперечний п'єзоефект", size=11, color=NEG, anchor="start"))

    # Грані кристала (контур призми)
    pts_prism = [
        (cx - 55, cy - 80), (cx + 55, cy - 80), (cx + 80, cy - 40),
        (cx + 80, cy + 60), (cx + 55, cy + 100), (cx - 55, cy + 100),
        (cx - 80, cy + 60), (cx - 80, cy - 40)
    ]
    poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_prism)
    s.append(f'<polygon points="{poly_str}" fill="#edf4fc" stroke="#688bb5" stroke-width="1.5" stroke-dasharray="4,3" fill-opacity="0.6"/>')

    # Опис властивостей осей внизу лівої панелі
    s.append(rect(35, 380, 340, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    s.append(text(45, 398, "• Вісь Z: 3-кратна симетрія, оптично активна", size=11, anchor="start", color=INK))
    s.append(text(45, 416, "• Три осі X (120°): полярні, породжують заряд q = d₁₁·F", size=11, anchor="start", color=INK))
    s.append(text(45, 434, "• Три осі Y: перпендикулярні до X і Z (зсувні напруги)", size=11, anchor="start", color=INK))

    # Права панель: Орієнтація пластин при різних зрізах
    s.append(rect(410, 20, 390, 440, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    s.append(text(605, 48, "Орієнтація кутів зрізу кварцових пластин", size=15, bold=True))
    s.append(text(605, 68, "Кути повороту задають температурну компенсацію та моду", size=12, color=MUTED))

    # Схема кутів у площині Y-Z навколо осі X
    rcx, rcy = 605, 200

    # Осі системи координат (Z вертикально, Y горизонтально)
    s.append(line(rcx, rcy + 110, rcx, rcy - 110, color=LINE, sw=1.5, dash="3,3"))
    s.append(text(rcx, rcy - 116, "+Z", size=12, bold=True))
    s.append(line(rcx - 140, rcy, rcx + 140, rcy, color=LINE, sw=1.5, dash="3,3"))
    s.append(text(rcx + 150, rcy + 4, "+Y", size=12, bold=True, anchor="start"))
    s.append(text(rcx - 150, rcy + 4, "−Y", size=12, bold=True, anchor="end"))

    # Позначення осі обертання X (перпендикулярно до екрана)
    s.append(circle(rcx, rcy, 6, fill="#ffffff", stroke=POS, sw=2))
    s.append(circle(rcx, rcy, 2, fill=POS, stroke=POS, sw=1))
    s.append(text(rcx - 14, rcy - 12, "X ⊙", size=12, bold=True, color=POS))

    # AT-зріз (+35°15' від осі Z)
    # Кут 35.25 градусів від осі Z (або 54.75 від осі Y)
    ang_at = math.radians(35.25)
    # Вектор площини пластини AT
    dx_at = 115 * math.cos(ang_at)
    dy_at = -115 * math.sin(ang_at)
    s.append(line(rcx - dx_at, rcy - dy_at, rcx + dx_at, rcy + dy_at, color="#1b8a43", sw=2.5))
    s.append(text(rcx + dx_at + 8, rcy + dy_at + 4, "AT-зріз (+35°15′)", size=12, bold=True, color="#1b8a43", anchor="start"))

    # Дуга кута AT
    s.append(f'<path d="M {rcx} {rcy-50} A 50 50 0 0 1 {rcx+50*math.sin(ang_at):.1f} {rcy-50*math.cos(ang_at):.1f}" fill="none" stroke="#1b8a43" stroke-width="1.5"/>')
    s.append(text(rcx + 28, rcy - 56, "+35°15′", size=10, bold=True, color="#1b8a43"))

    # BT-зріз (-49°00' від осі Z)
    ang_bt = math.radians(-49.0)
    dx_bt = 115 * math.cos(ang_bt)
    dy_bt = -115 * math.sin(ang_bt)
    s.append(line(rcx - dx_bt, rcy - dy_bt, rcx + dx_bt, rcy + dy_bt, color="#b91c1c", sw=2.5))
    s.append(text(rcx - dx_bt - 8, rcy - dy_bt + 4, "BT-зріз (−49°00′)", size=12, bold=True, color="#b91c1c", anchor="end"))

    # Дуга кута BT
    s.append(f'<path d="M {rcx} {rcy-40} A 40 40 0 0 0 {rcx-40*math.sin(math.radians(49)):.1f} {rcy-40*math.cos(math.radians(49)):.1f}" fill="none" stroke="#b91c1c" stroke-width="1.5"/>')
    s.append(text(rcx - 28, rcy - 46, "−49°", size=10, bold=True, color="#b91c1c"))

    # Картки опису зрізів праворуч внизу
    # SC-зріз (двічі повернутий)
    s.append(rect(425, 325, 360, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    s.append(text(435, 345, "Класифікація поворотів IEEE:", size=12, bold=True, anchor="start"))
    s.append(text(435, 365, "• AT / BT (одиничний поворот YXl θ): обертання навколо осі X", size=11, anchor="start"))
    s.append(text(435, 385, "• SC (подвійний поворот YXwlt φ/θ): φ ≈ 21.93°, θ ≈ 34.11°", size=11, anchor="start", bold=True, color="#0369a1"))
    s.append(text(435, 405, "  → повна компенсація внутрішніх механічних напруг", size=11, anchor="start", color="#0369a1"))
    s.append(text(435, 425, "• XY / +5° X: камертони 32.768 кГц (згинна мода)", size=11, anchor="start"))

    return render(os.path.join(OUT, 'quartz-axes-and-cuts.svg'), W, H, *s)


def fig_vibration_modes():
    """Фігура 2: Чотири основні механічні моди коливань кварцових резонаторів."""
    W, H = 840, 460
    s = []

    s.append(rect(15, 15, 810, 430, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    s.append(text(420, 42, "Механічні моди коливань кварцових резонаторів", size=16, bold=True))
    s.append(text(420, 62, "Форма деформації визначає робочу частоту, спосіб кріплення та добротність", size=12, color=MUTED))

    # 4 квадранти
    # 1. Товщинний зсув (Thickness Shear - TS) -> AT, BT, SC (1 .. 50+ МГц)
    s.append(rect(30, 85, 375, 165, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    s.append(text(45, 108, "1. Товщинний зсув (Thickness Shear, TS)", size=13, bold=True, anchor="start", color="#1e3a8a"))
    s.append(text(45, 126, "Зрізи: AT, BT, SC, IT · Частоти: 1–50+ МГц (до 200 МГц на овертонах)", size=11, color=MUTED, anchor="start"))

    # Малюнок деформації товщинного зсуву
    # Нерухомий прямокутник (пунктир)
    s.append(rect(95, 145, 160, 40, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=2))
    # Зсунутий паралелограм (суцільний)
    s.append('<polygon points="110,145 270,145 250,185 90,185" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="1.8" fill-opacity="0.8"/>')
    # Стрілки зсуву
    s.append(arrow(155, 137, 215, 137, color=POS, sw=2))
    s.append(arrow(205, 193, 145, 193, color=NEG, sw=2))
    s.append(text(285, 155, "f = N / t", size=12, bold=True, anchor="start"))
    s.append(text(285, 172, "t — товщина", size=11, color=MUTED, anchor="start"))
    s.append(text(285, 188, "N — стала частоти", size=11, color=MUTED, anchor="start"))

    s.append(text(45, 232, "Верхня й нижня грані ковзають у протилежні боки; частота ∝ 1/товщини", size=11, anchor="start"))

    # 2. Згинні коливання камертона (Flexure) -> XY-cut, Tuning Fork (32.768 кГц)
    s.append(rect(435, 85, 375, 165, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    s.append(text(450, 108, "2. Згинний камертон (Flexure Tuning Fork)", size=13, bold=True, anchor="start", color="#065f46"))
    s.append(text(450, 126, "Зрізи: XY-cut, +5° X-cut · Частота: 32.768 кГц (годинниковий стандарт)", size=11, color=MUTED, anchor="start"))

    # Малюнок камертона
    # Основа камертона
    s.append(rect(510, 175, 40, 25, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    # Зубці камертона (вигнуті)
    s.append('<path d="M 515 175 C 515 150, 498 140, 500 135 L 508 135 C 506 142, 523 150, 523 175 Z" fill="#a7f3d0" stroke="#059669" stroke-width="1.5"/>')
    s.append('<path d="M 537 175 C 537 150, 554 140, 552 135 L 544 135 C 546 142, 529 150, 529 175 Z" fill="#a7f3d0" stroke="#059669" stroke-width="1.5"/>')
    # Стрілки згину
    s.append(arrow(490, 138, 510, 138, color=POS, sw=1.5))
    s.append(arrow(562, 138, 542, 138, color=POS, sw=1.5))
    s.append(text(585, 152, "f ∝ w / L²", size=12, bold=True, anchor="start"))
    s.append(text(585, 168, "L — довжина зубця", size=11, color=MUTED, anchor="start"))
    s.append(text(585, 184, "w — ширина зубця", size=11, color=MUTED, anchor="start"))

    s.append(text(450, 232, "Два зубці коливаються у протифазі; реакції в основі взаємно гасяться", size=11, anchor="start"))

    # 3. Контурний/площинний зсув (Face Shear / Contour Shear) -> CT, DT (100–500 кГц)
    s.append(rect(30, 265, 375, 165, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    s.append(text(45, 288, "3. Площинний зсув (Face Shear)", size=13, bold=True, anchor="start", color="#9a3412"))
    s.append(text(45, 306, "Зрізи: CT, DT · Частоти: 100–600 кГц (проміжний діапазон)", size=11, color=MUTED, anchor="start"))

    # Малюнок площинного зсуву (квадрат перекошується в ромб)
    s.append(rect(140, 325, 60, 60, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=2))
    # Стрілки деформації кутів
    s.append(arrow(132, 320, 142, 330, color=POS, sw=1.5))
    s.append(arrow(208, 390, 198, 380, color=POS, sw=1.5))
    s.append(text(235, 345, "f = N_fs / a", size=12, bold=True, anchor="start"))
    s.append(text(235, 362, "a — довжина ребра", size=11, color=MUTED, anchor="start"))
    s.append(text(235, 378, "частота від розмірів грані", size=11, color=MUTED, anchor="start"))

    s.append(text(45, 412, "Квадратна пластина перетворюється на ромб у власній площині", size=11, anchor="start"))

    # 4. Поздовжній стиск-розтяг (Extensional / Longitudinal) -> MT, NT, +5° X-cut (40–200 кГц)
    s.append(rect(435, 265, 375, 165, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    s.append(text(450, 288, "4. Поздовжній стиск/розтяг (Extensional)", size=13, bold=True, anchor="start", color="#6b21a8"))
    s.append(text(450, 306, "Зрізи: MT, NT, GT, +5° X-брусок · Частоти: 40–200 кГц", size=11, color=MUTED, anchor="start"))

    # Малюнок поздовжнього стиску-розтягу
    s.append(rect(480, 345, 100, 25, fill="#e9d5ff", stroke="#9333ea", sw=1.5, rx=2))
    s.append(arrow(470, 357, 455, 357, color=POS, sw=2))
    s.append(arrow(590, 357, 605, 357, color=POS, sw=2))
    s.append(text(625, 345, "f = v / (2·L)", size=12, bold=True, anchor="start"))
    s.append(text(625, 362, "L — довжина стрижня", size=11, color=MUTED, anchor="start"))
    s.append(text(625, 378, "v — швидкість звуку", size=11, color=MUTED, anchor="start"))

    s.append(text(450, 412, "Хвиля біжить уздовж бруска; частота задається виключно його довжиною", size=11, anchor="start"))

    return render(os.path.join(OUT, 'vibration-modes.svg'), W, H, *s)


def fig_temperature_curves():
    """Фігура 3: Температурно-частотні характеристики (f-T) різних зрізів."""
    W, H = 840, 500
    s = []

    s.append(rect(15, 15, 810, 470, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    s.append(text(420, 42, "Температурно-частотні криві (f-T) головних зрізів кварцу", size=16, bold=True))
    s.append(text(420, 62, "Кубічні (AT, SC) та параболічні (BT, Tuning Fork) залежності відхилення частоти Δf/f₀", size=12, color=MUTED))

    # Область графіка
    # X: Температура від -40 °C до +120 °C (ширина 500 px, cx = 350, від x=100 до x=600)
    # Y: Відхилення частоти від +40 ppm до -160 ppm (висота 320 px, cy = 250, нуль на y=200)
    gx0, gy0 = 90, 95
    gw, gh = 520, 320

    s.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))

    # Координатна сітка
    # Y-лінії: +40, +20, 0, -20, -40, -60, -80, -100, -120, -140, -160 ppm
    # Y-scale: 0 ppm -> y = 160; -160 ppm -> y = 380 (1 ppm = 1.375 px)
    def y_ppm(ppm):
        return gy0 + 65 - ppm * 1.35

    def x_temp(t):
        # t від -40 до +120 (діапазон 160 °C на gw=520 px -> 1 °C = 3.25 px)
        return gx0 + (t + 40) * 3.25

    # Сітка Y
    for ppm in [40, 20, 0, -20, -40, -60, -80, -100, -120, -140]:
        y = y_ppm(ppm)
        is_zero = (ppm == 0)
        s.append(line(gx0, y, gx0 + gw, y, color="#475569" if is_zero else "#f1f5f9", sw=1.5 if is_zero else 1))
        s.append(text(gx0 - 8, y + 4, f"{ppm:+d}" if ppm != 0 else "0", size=10, color=INK if is_zero else MUTED, anchor="end"))

    s.append(text(gx0 - 38, y_ppm(0) - 80, "Δf / f₀\n(ppm)", size=11, bold=True, anchor="middle"))

    # Сітка X (температура)
    for t in [-40, -20, 0, 25, 50, 75, 90, 105, 120]:
        x = x_temp(t)
        is_ref = (t == 25)
        s.append(line(x, gy0, x, gy0 + gh, color="#94a3b8" if is_ref else "#f1f5f9", sw=1.2 if is_ref else 1, dash="3,3" if is_ref else None))
        s.append(text(x, gy0 + gh + 16, f"{t}°C", size=10, color=POS if is_ref else MUTED, anchor="middle", bold=is_ref))

    s.append(text(gx0 + gw / 2, gy0 + gh + 34, "Температура навколишнього середовища T (°C)", size=11, bold=True, anchor="middle"))

    # Промисловий діапазон -40..+85 °C (виділення зони)
    s.append(rect(x_temp(-40), gy0, x_temp(85) - x_temp(-40), gh, fill="#f8fafc", stroke="none", sw=0))
    s.append(text(x_temp(22.5), gy0 + 15, "Промисловий робочий діапазон (−40 ... +85 °C)", size=10, color="#64748b", anchor="middle"))

    # 1. AT-зріз (кубічна S-крива, перегин біля 25 °C, стабільність ±15 ppm)
    # Δf/f = a*(T-25) + b*(T-25)^2 + c*(T-25)^3, a=0, b=0, c=0.95e-4
    pts_at = []
    for t_deg in range(-40, 121, 2):
        dt = t_deg - 26.0
        ppm = 0.0 * dt - 0.0005 * (dt**2) + 0.000095 * (dt**3)
        pts_at.append(f"{x_temp(t_deg):.1f},{y_ppm(ppm):.1f}")
    s.append(f'<polyline points="{" ".join(pts_at)}" fill="none" stroke="#16a34a" stroke-width="2.8"/>')
    s.append(text(x_temp(70), y_ppm(10) - 10, "AT-зріз (кубічна S-крива, ±15 ppm)", size=11, bold=True, color="#15803d", anchor="middle"))

    # 2. BT-зріз (парабола вершиною на 25 °C, круте спадання)
    # Δf/f = -0.040 * (T - 25)^2
    pts_bt = []
    for t_deg in range(-40, 105, 2):
        dt = t_deg - 25.0
        ppm = -0.040 * (dt**2)
        if ppm >= -160:
            pts_bt.append(f"{x_temp(t_deg):.1f},{y_ppm(ppm):.1f}")
    s.append(f'<polyline points="{" ".join(pts_bt)}" fill="none" stroke="#dc2626" stroke-width="2.2"/>')
    s.append(text(x_temp(-15), y_ppm(-70), "BT-зріз (парабола)", size=11, bold=True, color="#dc2626", anchor="middle"))

    # 3. Годинниковий камертон 32.768 кГц (парабола -0.035 * (T - 25)^2)
    pts_tf = []
    for t_deg in range(-40, 95, 2):
        dt = t_deg - 25.0
        ppm = -0.035 * (dt**2)
        if ppm >= -160:
            pts_tf.append(f"{x_temp(t_deg):.1f},{y_ppm(ppm):.1f}")
    s.append(f'<polyline points="{" ".join(pts_tf)}" fill="none" stroke="#ea580c" stroke-width="2.0" stroke-dasharray="5,3"/>')
    s.append(text(x_temp(-30), y_ppm(-110), "Камертон 32 кГц (−0.035·ΔT²)", size=10, bold=True, color="#c2410c", anchor="start"))

    # 4. SC-зріз (кубічна крива з точкою перегину на 92 °C для OCXO)
    pts_sc = []
    for t_deg in range(-40, 121, 2):
        dt = t_deg - 92.0
        ppm = 0.0 * dt - 0.0003 * (dt**2) + 0.000075 * (dt**3)
        pts_sc.append(f"{x_temp(t_deg):.1f},{y_ppm(ppm):.1f}")
    s.append(f'<polyline points="{" ".join(pts_sc)}" fill="none" stroke="#0284c7" stroke-width="2.5"/>')
    s.append(text(x_temp(95), y_ppm(0) - 14, "SC-зріз (перегин при +92 °C, OCXO)", size=11, bold=True, color="#0369a1", anchor="middle"))

    # Легенда та пояснення праворуч
    lx, ly = 625, 95
    s.append(rect(lx, ly, 185, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    s.append(text(lx + 92, ly + 22, "Порівняння зрізів", size=13, bold=True))

    s.append(line(lx + 12, ly + 48, lx + 35, ly + 48, color="#16a34a", sw=2.8))
    s.append(text(lx + 42, ly + 52, "AT-зріз: масовий", size=11, bold=True, color="#15803d", anchor="start"))
    s.append(text(lx + 12, ly + 68, "±10–30 ppm у −40..+85°C", size=10, color=MUTED, anchor="start"))
    s.append(text(lx + 12, ly + 82, "Точка перегину ~25 °C", size=10, color=MUTED, anchor="start"))

    s.append(line(lx + 12, ly + 108, lx + 35, ly + 108, color="#0284c7", sw=2.5))
    s.append(text(lx + 42, ly + 112, "SC-зріз: еталон OCXO", size=11, bold=True, color="#0369a1", anchor="start"))
    s.append(text(lx + 12, ly + 128, "Перегин на 85–95 °C", size=10, color=MUTED, anchor="start"))
    s.append(text(lx + 12, ly + 142, "Q > 10⁶, нульовий dF/dt", size=10, color=MUTED, anchor="start"))

    s.append(line(lx + 12, ly + 168, lx + 35, ly + 168, color="#dc2626", sw=2.2))
    s.append(text(lx + 42, ly + 172, "BT-зріз: ВЧ-пластина", size=11, bold=True, color="#b91c1c", anchor="start"))
    s.append(text(lx + 12, ly + 188, "Товстіша на 53% за AT", size=10, color=MUTED, anchor="start"))
    s.append(text(lx + 12, ly + 202, "Парабола, гірша на краях", size=10, color=MUTED, anchor="start"))

    s.append(line(lx + 12, ly + 228, lx + 35, ly + 228, color="#ea580c", sw=2.0, dash="4,2"))
    s.append(text(lx + 42, ly + 232, "Камертон 32.768 кГц", size=11, bold=True, color="#c2410c", anchor="start"))
    s.append(text(lx + 12, ly + 248, "Вершина при +25 °C", size=10, color=MUTED, anchor="start"))
    s.append(text(lx + 12, ly + 262, "При 0 °C: −22 ppm (~2 с/добу)", size=10, color=MUTED, anchor="start"))

    s.append(rect(lx + 8, ly + 278, 169, 32, fill="#ecfdf5", stroke="#a7f3d0", sw=1, rx=4))
    s.append(text(lx + 92, ly + 298, "Чутливість кута: 1′ ≈ 2 ppm/°C", size=10, bold=True, color="#047857", anchor="middle"))

    return render(os.path.join(OUT, 'temperature-curves-comparison.svg'), W, H, *s)


def fig_stress_compensation():
    """Фігура 4: Механізм компенсації напружень та стійкості до теплового удару в SC-зрізі."""
    W, H = 840, 440
    s = []

    s.append(rect(15, 15, 810, 410, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    s.append(text(420, 42, "Стійкість до напружень: одинарний AT проти подвійного SC-зрізу", size=16, bold=True))
    s.append(text(420, 62, "Чому подвійний кут повороту (SC) усуває динамічний дрейф при тепловому ударі та вібраціях", size=12, color=MUTED))

    # Ліва колонка: AT-зріз (одинарний поворот) під дією напруг
    s.append(rect(30, 85, 375, 320, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    s.append(text(217, 110, "AT-зріз: чутливий до напруг (Stress-Sensitive)", size=13, bold=True, color="#991b1b"))

    # Малюнок пластини AT з тримачами
    s.append(rect(100, 140, 180, 50, fill="#ffffff", stroke="#b91c1c", sw=1.5, rx=3))
    s.append(text(190, 168, "Кварцова пластина AT", size=11, bold=True, color="#7f1d1d"))

    # Механічні опори/кліпси
    s.append(rect(75, 150, 25, 30, fill="#64748b", stroke="#334155", sw=1.2, rx=2))
    s.append(rect(280, 150, 25, 30, fill="#64748b", stroke="#334155", sw=1.2, rx=2))
    s.append(arrow(60, 165, 75, 165, color="#b91c1c", sw=2))
    s.append(arrow(320, 165, 305, 165, color="#b91c1c", sw=2))
    s.append(text(190, 205, "Стиск від кріплення / теплового градієнта", size=10, color="#b91c1c"))

    # Графік динамічного відгуку на тепловий стрибок (стрибок частоти)
    s.append(rect(50, 220, 335, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    s.append(text(60, 238, "Відгук частоти на увімкнення нагрівача (тепловий удар):", size=10, bold=True, anchor="start"))

    # Вісь часу та частоти
    s.append(line(70, 295, 360, 295, color="#94a3b8", sw=1))
    s.append(line(70, 295, 70, 245, color="#94a3b8", sw=1))
    s.append(text(360, 305, "t (час)", size=9, anchor="end", color=MUTED))
    s.append(text(65, 250, "Δf", size=9, anchor="end", color=MUTED))

    # Стрибок частоти при тепловому ударі
    s.append('<path d="M 70 295 L 110 295 Q 120 250, 140 252 Q 180 260, 240 293 L 360 295" fill="none" stroke="#dc2626" stroke-width="2"/>')
    s.append(text(150, 250, "Сплеск до +5..10 ppm!", size=10, bold=True, color="#b91c1c"))
    s.append(text(250, 280, "повільна релаксація", size=9, color=MUTED))

    s.append(text(50, 335, "• Коефіцієнт напруги K_stress ≠ 0", size=11, color="#7f1d1d", anchor="start", bold=True))
    s.append(text(50, 355, "• Чутливість до прискорення: ~1–2 ppb/g", size=11, color="#7f1d1d", anchor="start"))
    s.append(text(50, 375, "• Нестабільність при вібрації та теплових перехідних процесах", size=11, color="#7f1d1d", anchor="start"))

    # Права колонка: SC-зріз (подвійний поворот)
    s.append(rect(435, 85, 375, 320, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    s.append(text(622, 110, "SC-зріз: компенсація напружень (Stress-Compensated)", size=13, bold=True, color="#166534"))

    # Малюнок пластини SC
    s.append(rect(505, 140, 180, 50, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=3))
    s.append(text(595, 168, "Кварцова пластина SC (φ=21.9°, θ=34.1°)", size=11, bold=True, color="#14532d"))

    s.append(rect(480, 150, 25, 30, fill="#64748b", stroke="#334155", sw=1.2, rx=2))
    s.append(rect(685, 150, 25, 30, fill="#64748b", stroke="#334155", sw=1.2, rx=2))
    s.append(arrow(465, 165, 480, 165, color="#16a34a", sw=2))
    s.append(arrow(725, 165, 710, 165, color="#16a34a", sw=2))
    s.append(text(595, 205, "Тензорні компоненти напруг взаємно гасяться", size=10, color="#15803d"))

    # Графік динамічного відгуку для SC
    s.append(rect(455, 220, 335, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    s.append(text(465, 238, "Відгук частоти на увімкнення нагрівача (тепловий удар):", size=10, bold=True, anchor="start"))

    s.append(line(475, 295, 765, 295, color="#94a3b8", sw=1))
    s.append(line(475, 295, 475, 245, color="#94a3b8", sw=1))
    s.append(text(765, 305, "t (час)", size=9, anchor="end", color=MUTED))
    s.append(text(470, 250, "Δf", size=9, anchor="end", color=MUTED))

    # Практично плоска пряма без сплеску
    s.append(line(475, 295, 765, 295, color="#16a34a", sw=2.5))
    s.append(text(620, 275, "Сплеск частоти відсутній (нульовий dF/dt)", size=10, bold=True, color="#15803d", anchor="middle"))

    s.append(text(455, 335, "• Коефіцієнт напруги K_stress ≈ 0 (компенсовано)", size=11, color="#14532d", anchor="start", bold=True))
    s.append(text(455, 355, "• Чутливість до прискорення: ~0.1–0.2 ppb/g (у 10 разів краща)", size=11, color="#14532d", anchor="start"))
    s.append(text(455, 375, "• Миттєвий вихід на робочу частоту в OCXO без теплового дрейфу", size=11, color="#14532d", anchor="start"))

    return render(os.path.join(OUT, 'stress-compensation-and-thermal-transient.svg'), W, H, *s)


def main():
    fig_quartz_axes_and_cuts()
    fig_vibration_modes()
    fig_temperature_curves()
    fig_stress_compensation()
    print("Всі 4 фігури успішно згенеровано.")


if __name__ == '__main__':
    main()
