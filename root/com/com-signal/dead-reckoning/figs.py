# -*- coding: utf-8 -*-
"""Фігури до теми «Інерціальне числення позиції».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── 1. Блок-схема механізації БІНС (Strapdown INS Mechanization) ──
def fig_strapdown_mechanization():
    W, H = 840, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Конвеєр безплатформного інерціального числення (Strapdown INS)", size=16, bold=True))

    # Вхідні блоки ліворуч (IMU)
    b_gyro = fitbox(40, 90, 150, 70, "Гіроскоп (IMU)\nкутова швидкість ω_b\n[рад/с]", size=12, fill="#eaf2f8", stroke="#2980b9", bold=True)
    b_accel = fitbox(40, 270, 150, 70, "Акселерометр (IMU)\nпитома сила f_b\n[м/с²]", size=12, fill="#fef9e7", stroke="#d4ac0d", bold=True)
    f.extend([b_gyro, b_accel])

    # Блок орієнтації
    b_att = fitbox(250, 90, 170, 70, "Інтегрування кутів\nКватерніон q / Матриця R_b^n\n(дискретний крок Δt)", size=12, fill="#ebf5fb", stroke="#2471a3")
    f.append(b_att)
    f.append(arrow(190, 125, 250, 125, color=LINE, sw=1.8))
    f.append(text(220, 115, "ω_b", size=11, color=MUTED, bold=True))

    # Блок перетворення координат
    b_rot = fitbox(250, 270, 170, 70, "Поворот у навігаційну СК\nf_n = R_b^n · f_b", size=12, fill="#fcf3cf", stroke="#b7950b")
    f.append(b_rot)
    f.append(arrow(190, 305, 250, 305, color=LINE, sw=1.8))
    f.append(text(220, 295, "f_b", size=11, color=MUTED, bold=True))

    # Стрілка орієнтації R_b^n до блоку повороту
    f.append(arrow(335, 160, 335, 270, color="#2980b9", sw=1.8))
    f.append(text(345, 215, "R_b^n (орієнтація)", size=10.5, color="#2471a3", anchor="start"))

    # Блок компенсації гравітації
    b_grav = fitbox(480, 270, 140, 70, "Компенсація g\na_n = f_n − g_n\n[0, 0, 9.81]", size=12, fill="#fadbd8", stroke=POS)
    f.append(b_grav)
    f.append(arrow(420, 305, 480, 305, color=LINE, sw=1.8))
    f.append(text(450, 295, "f_n", size=11, color=MUTED, bold=True))

    # Вектор гравітації зверху
    f.append(arrow(550, 210, 550, 270, color=POS, sw=1.6))
    f.append(text(550, 200, "Вектор g_n (вертикаль)", size=10.5, color=POS, bold=True))

    # Блок інтегрування швидкості
    b_vel = fitbox(480, 390, 140, 65, "Інтеграл швидкості\nv_n = ∫ a_n dt\nv[k+1] = v[k] + a·Δt", size=11.5, fill="#e8f8f5", stroke=FIELD)
    f.append(b_vel)
    f.append(arrow(550, 340, 550, 390, color=LINE, sw=1.8))
    f.append(text(560, 365, "a_n", size=11, color=MUTED, bold=True, anchor="start"))

    # Блок інтегрування позиції
    b_pos = fitbox(680, 390, 130, 65, "Інтеграл позиції\np_n = ∫ v_n dt\np[k+1] = p[k] + v·Δt", size=11.5, fill="#e8f8f5", stroke=FIELD, bold=True)
    f.append(b_pos)
    f.append(arrow(620, 422, 680, 422, color=LINE, sw=1.8))
    f.append(text(650, 412, "v_n", size=11, color=MUTED, bold=True))

    # Стрілка виходу
    f.append(arrow(810, 422, 835, 422, color=FIELD, sw=2.2))

    # Виноска про замкнену корекцію / комплексування
    b_corr = fitbox(160, 470, 480, 36, "Зовнішні корекції (GNSS, одометрія коліс, оптичний потік, ZUPT) стабілізують дрейф", size=11, fill="#fdfefe", stroke=MUTED, rx=4)
    f.append(b_corr)

    render(os.path.join(IMG, "strapdown-mechanization.svg"), W, H, *f)


# ── 2. Геометричний витік гравітації (Gravity Leakage under Tilt Error) ──
def fig_gravity_leakage():
    W, H = 760, 460
    f = []

    f.append(text(W / 2, 28, "Витік сили тяжіння через кутову похибку орієнтації", size=16, bold=True))

    # Справжня вертикаль та оцінена вертикаль
    ox, oy = 380, 90

    # Справжня СК (навігаційна): вісь Z вниз
    f.append(line(ox, oy, ox, oy + 260, color=MUTED, sw=1.5, dash="5,4"))
    f.append(text(ox - 10, oy + 250, "Справжня вертикаль (земна)", size=11, color=MUTED, anchor="end"))

    # Справжній вектор g (синій/зелений)
    f.append(arrow(ox, oy, ox, oy + 220, color=NEG, sw=3.0))
    f.append(text(ox - 12, oy + 120, "Справжня сила тяжіння g", size=12, color=NEG, bold=True, anchor="end"))

    # Нахилена система координат через похибку δθ
    angle_rad = 0.28  # ~16 градусів для наочності креслення
    lx = ox + 220 * math.sin(angle_rad)
    ly = oy + 220 * math.cos(angle_rad)

    f.append(line(ox, oy, lx + 20, ly + 20, color=POS, sw=1.5, dash="5,4"))
    f.append(text(lx + 25, ly + 15, "Оцінена алгоритмом вісь (помилкова)", size=11, color=POS, anchor="start"))

    # Дуга кута δθ
    arc_r = 70
    arc_pts = []
    for step in range(0, 16):
        a = step * (angle_rad / 15.0)
        arc_pts.append((ox + arc_r * math.sin(a), oy + arc_r * math.cos(a)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in arc_pts), POS))
    f.append(text(ox + 26, oy + 76, "δθ", size=13, color=POS, bold=True))

    # Віднімання скомпенсованого g': вектор g' направлений вздовж оціненої вертикалі
    # Вектор залишку (помилкове горизонтальне прискорення)
    f.append(arrow(ox, oy + 220, lx, ly, color=POS, sw=2.8))
    f.append(text((ox + lx) / 2 + 10, oy + 245, "Хибне прискорення δa ≈ g · δθ", size=12.5, color=POS, bold=True, anchor="start"))

    # Пояснювальні рамки внизу
    b_calc = fitbox(60, 350, 640, 85,
                    "Похибка кута нахилу всього 0.1° (0.00175 рад) викликає горизонтальне хибне прискорення:\n"
                    "δa = g · sin(δθ) ≈ 9.81 · 0.00175 ≈ 0.017 м/с²\n"
                    "За 1 хвилину це дає похибку швидкості 1.0 м/с та похибку позиції 31 метр на рівному місці!",
                    size=12, fill="#fdf2e9", stroke=POS)
    f.append(b_calc)

    render(os.path.join(IMG, "gravity-leakage.svg"), W, H, *f)


# ── 3. Криві накопичення похибок (Error Growth Curves: t, t^2, t^3) ──
def fig_error_growth_curves():
    W, H = 780, 480
    f = []

    f.append(text(W / 2, 28, "Порівняння законів росту похибки позиції з часом", size=16, bold=True))

    ox, oy = 90, 370
    span_x = 460
    span_y = 290

    # Осі
    f.append(line(ox, oy, ox + span_x + 30, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - span_y - 10, color=LINE, sw=1.5))
    f.append(text(ox + span_x + 35, oy + 5, "Час t (с)", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 10, oy - span_y - 15, "Похибка позиції δp (м)", size=11, color=MUTED, anchor="start"))

    # Позначки на осях
    for i in range(1, 6):
        tx = ox + i * (span_x / 5.0)
        f.append(line(tx, oy - 4, tx, oy + 4, color=MUTED, sw=1.0))
        f.append(text(tx, oy + 18, "%d0 с" % (i * 2), size=10, color=MUTED))

    # 1. Початкова похибка швидкості: лінійний ріст δp = δv0 * t
    lin_pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = ox + t * span_x
        yy = oy - (t * 0.35) * span_y
        lin_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in lin_pts), "#2980b9"))

    # 2. Зміщення нуля акселерометра (bias b_a): квадратичний ріст δp = 0.5 * b_a * t^2
    quad_pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = ox + t * span_x
        yy = oy - (t ** 2 * 0.65) * span_y
        quad_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in quad_pts), "#d4ac0d"))

    # 3. Дрейф нуля гіроскопа (bias b_g): кубічний ріст δp = 1/6 * g * b_g * t^3
    cube_pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = ox + t * span_x
        yy = oy - (t ** 3 * 0.98) * span_y
        cube_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>'
             % (" ".join("%.1f,%.1f" % p for p in cube_pts), POS))

    # Легенда праворуч
    lx, ly = 580, 110

    # Блок легенди
    f.append(rect(565, 85, 205, 270, fill="#fcfcfc", stroke=MUTED, sw=1.0, rx=5))
    f.append(text(575, 108, "Джерела дрейфу:", size=12, bold=True, anchor="start"))

    # Пункт 1: Кубічний
    f.append(line(575, 140, 605, 140, color=POS, sw=3.0))
    f.append(text(612, 137, "Дрейф гіроскопа b_g", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(612, 153, "δp(t) ~ 1/6 · g · b_g · t³", size=10.5, color=INK, anchor="start"))

    # Пункт 2: Квадратичний
    f.append(line(575, 200, 605, 200, color="#d4ac0d", sw=2.6))
    f.append(text(612, 197, "Зміщення акселерометра b_a", size=11, color="#b7950b", bold=True, anchor="start"))
    f.append(text(612, 213, "δp(t) ~ 1/2 · b_a · t²", size=10.5, color=INK, anchor="start"))

    # Пункт 3: Лінійний
    f.append(line(575, 260, 605, 260, color="#2980b9", sw=2.2, dash="6,4"))
    f.append(text(612, 257, "Похибка швидкості δv₀", size=11, color="#2471a3", bold=True, anchor="start"))
    f.append(text(612, 273, "δp(t) ~ δv₀ · t", size=10.5, color=INK, anchor="start"))

    # Висновок
    f.append(text(575, 320, "Кубічний дрейф гіроскопа", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(text(575, 336, "домінує на довгих інтервалах!", size=10, color=MUTED, anchor="start"))

    # Рамка підсумок знизу
    b_sum = fitbox(60, 405, 480, 50,
                   "Через подвійне інтегрування помилки нахилу похибка гіроскопа вибухає як t³.\n"
                   "Тому якість оцінки орієнтації є найважливішим фактором стабільності БІНС.",
                   size=11, fill="#f4f6f7", stroke=LINE)
    f.append(b_sum)

    render(os.path.join(IMG, "error-growth-curves.svg"), W, H, *f)


# ── 4. Комплексування БІНС із зовнішніми давачами (Sensor Fusion / Aiding) ──
def fig_wheel_ins_fusion():
    W, H = 820, 480
    f = []

    f.append(text(W / 2, 28, "Архітектура комплексування БІНС із давачами швидкості (ESKF / Fusion)", size=16, bold=True))

    # Високочастотний контур БІНС зверху
    f.append(rect(40, 70, 740, 150, fill="#f4f9f9", stroke="#16a085", sw=1.5, rx=6))
    f.append(text(60, 95, "Високочастотний контур прямого числення БІНС (200 – 1000 Гц, плавний, без затримок)", size=12, color="#117864", bold=True, anchor="start"))

    b_imu = fitbox(60, 120, 130, 70, "IMU давачі\n(акселерометр,\nгіроскоп)", size=11.5, fill="#ffffff", stroke="#16a085")
    b_mech = fitbox(250, 120, 240, 70, "Кінематичний інтегратор\nОрієнтація R_b^n -> Компенсація g\nШвидкість v_ins -> Позиція p_ins", size=11, fill="#ffffff", stroke="#16a085")
    b_out = fitbox(570, 120, 180, 70, "Оцінка навігаційного стану\n(p, v, q)\nВисока частота для керування", size=11, fill="#e8f8f5", stroke=FIELD, bold=True)

    f.extend([b_imu, b_mech, b_out])
    f.append(arrow(190, 155, 250, 155, color=LINE, sw=1.8))
    f.append(arrow(490, 155, 570, 155, color=LINE, sw=1.8))

    # Низькочастотний контур корекції знизу
    f.append(rect(40, 260, 740, 195, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    f.append(text(60, 285, "Контур корекції похибок та спостереження (20 – 50 Гц або аперіодично)", size=12, color="#b7950b", bold=True, anchor="start"))

    b_sensors = fitbox(60, 310, 170, 115, "Давачі обмеження дрейфу:\n• Одометрія коліс (v_wheel)\n• Детектор зупинки (ZUPT)\n• Оптичний потік (Flow)\n• Неголономні зв'язки (NHC)", size=10.5, fill="#ffffff", stroke="#d4ac0d")
    b_residual = fitbox(280, 335, 180, 70, "Обчислення нев'язки\nΔv = v_ins − R_b^n · v_wheel\n(різниця швидкостей)", size=11, fill="#ffffff", stroke="#d4ac0d")
    b_eskf = fitbox(520, 325, 230, 90, "Фільтр помилок стану (ESKF)\nОцінює вектор помилок:\nδp, δv, δθ, зміщення bias b_a, b_g", size=11, fill="#fef5e7", stroke=POS, bold=True)

    f.extend([b_sensors, b_residual, b_eskf])

    # Зв'язки між блоками корекції
    f.append(arrow(230, 370, 280, 370, color=LINE, sw=1.6))
    f.append(arrow(460, 370, 520, 370, color=LINE, sw=1.6))

    # Зв'язок від БІНС до обчислення нев'язки
    f.append(arrow(370, 190, 370, 335, color=MUTED, sw=1.4))
    f.append(text(380, 245, "v_ins", size=10.5, color=MUTED, anchor="start"))

    # Зворотний зв'язок від ESKF до БІНС (скидання похибок)
    f.append(arrow(635, 325, 635, 190, color=POS, sw=2.0))
    f.append(text(645, 245, "Корекція стану: -δp, -δv, -δθ\nта оновлення зміщень bias", size=10.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "wheel-ins-fusion.svg"), W, H, *f)


if __name__ == "__main__":
    fig_strapdown_mechanization()
    fig_gravity_leakage()
    fig_error_growth_curves()
    fig_wheel_ins_fusion()
    print("OK: 4 figures generated in ->", IMG)
