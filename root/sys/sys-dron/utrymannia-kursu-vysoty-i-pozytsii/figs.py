#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми utrymannia-kursu-vysoty-i-pozytsii.
Вивід у ./img/
"""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cascaded_hierarchy():
    """Фігура 1: Ієрархія 4 каскадних контурів керування польотом БПЛА."""
    w, h = 880, 340
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Ієрархія каскадних контурів польотного контролера", size=14, color=INK, bold=True))
    frags.append(text(w / 2, 48, "Внутрішній контур швидший за зовнішній у 3–5 разів (розділення смуг пропускання)", size=11, color=MUTED, italic=True))

    # 4 каскадні блоки
    # Блок 1: Контур позиції (20-50 Гц)
    b1_body = rect(30, 75, 170, 140, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6)
    frags.append(b1_body)
    frags.append(text(115, 98, "Контур позиції", size=12, color=INK, bold=True))
    frags.append(text(115, 116, "Частота: 20–50 Гц", size=10, color=NEG, bold=True))
    frags.append(line(45, 126, 185, 126, color="#cbd5e1", sw=1))
    frags.append(text(115, 145, "Вхід: r_target (NEU)", size=10, color=INK))
    frags.append(text(115, 165, "Закон: P-регулятор", size=10, color=INK))
    frags.append(text(115, 190, "Вихід: v_des (швидкість)", size=10, color=FIELD, bold=True))

    # Стрілка 1 -> 2
    frags.append(arrow(200, 145, 240, 145, color=LINE, sw=1.8))
    frags.append(text(220, 133, "v_des", size=10, color=INK, bold=True))

    # Блок 2: Контур швидкостей (50 Гц)
    b2_body = rect(240, 75, 175, 140, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6)
    frags.append(b2_body)
    frags.append(text(327, 98, "Контур швидкості", size=12, color=INK, bold=True))
    frags.append(text(327, 116, "Частота: ~50 Гц", size=10, color=FIELD, bold=True))
    frags.append(line(255, 126, 400, 126, color="#bbf7d0", sw=1))
    frags.append(text(327, 145, "Вхід: v_des, v_meas", size=10, color=INK))
    frags.append(text(327, 165, "Закон: PID + вітровий I", size=10, color=INK))
    frags.append(text(327, 190, "Вихід: q_des (крен/тангаж)", size=10, color=POS, bold=True))

    # Стрілка 2 -> 3
    frags.append(arrow(415, 145, 455, 145, color=LINE, sw=1.8))
    frags.append(text(435, 133, "q_des", size=10, color=INK, bold=True))

    # Блок 3: Контур орієнтації (100-250 Гц)
    b3_body = rect(455, 75, 180, 140, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6)
    frags.append(b3_body)
    frags.append(text(545, 98, "Контур орієнтації", size=12, color=INK, bold=True))
    frags.append(text(545, 116, "Частота: 100–250 Гц", size=10, color="#ca8a04", bold=True))
    frags.append(line(470, 126, 620, 126, color="#fef08a", sw=1))
    frags.append(text(545, 145, "Вхід: q_des, q_meas", size=10, color=INK))
    frags.append(text(545, 165, "Закон: P-кут / кватерніон", size=10, color=INK))
    frags.append(text(545, 190, "Вихід: ω_des (кутова шв.)", size=10, color=POS, bold=True))

    # Стрілка 3 -> 4
    frags.append(arrow(635, 145, 675, 145, color=LINE, sw=1.8))
    frags.append(text(655, 133, "ω_des", size=10, color=INK, bold=True))

    # Блок 4: Контур кутових швидкостей (250-1000 Гц)
    b4_body = rect(675, 75, 175, 140, fill="#fee2e2", stroke=POS, sw=1.8, rx=6)
    frags.append(b4_body)
    frags.append(text(762, 98, "Контур кутових шв.", size=12, color=POS, bold=True))
    frags.append(text(762, 116, "Частота: 250–1000 Гц", size=10, color=POS, bold=True))
    frags.append(line(690, 126, 835, 126, color="#fecaca", sw=1))
    frags.append(text(762, 145, "Вхід: ω_des, ω_gyro", size=10, color=INK))
    frags.append(text(762, 165, "Закон: PID + анти-віндап", size=10, color=INK))
    frags.append(text(762, 190, "Вихід: τ (моменти моторів)", size=10, color=INK, bold=True))

    # Нижня частина: Давачі та зворотний зв'язок
    frags.append(rect(30, 245, 820, 65, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(440, 265, "Джерела зворотного зв'язку (State Estimation / EKF)", size=11, color=INK, bold=True))

    # Позначки давачів знизу
    frags.append(text(115, 290, "GNSS / RTK / Одометрія", size=10, color=NEG))
    frags.append(text(327, 290, "EKF / Оптичний потік", size=10, color=FIELD))
    frags.append(text(545, 290, "Компас + AHRS (акселерометр)", size=10, color="#ca8a04"))
    frags.append(text(762, 290, "Гіроскоп (IMU 1–8 кГц)", size=10, color=POS))

    # Зворотні стрілки вгору від давачів
    frags.append(arrow(115, 245, 115, 220, color=NEG, sw=1.4))
    frags.append(arrow(327, 245, 327, 220, color=FIELD, sw=1.4))
    frags.append(arrow(545, 245, 545, 220, color="#ca8a04", sw=1.4))
    frags.append(arrow(762, 245, 762, 220, color=POS, sw=1.4))

    render(os.path.join(IMG_DIR, 'cascaded-loops-hierarchy.svg'), w, h, *frags)
    print("Generated cascaded-loops-hierarchy.svg")


def fig_altitude_control():
    """Фігура 2: Архітектура контуру утримання висоти з компенсацією нахилу та напруги."""
    w, h = 860, 320
    frags = []

    frags.append(text(w / 2, 26, "Контур утримання висоти (Altitude Hold Loop)", size=14, color=INK, bold=True))

    # Вхід уставки висоти
    frags.append(text(45, 95, "z_target", size=11, color=INK, bold=True))
    frags.append(arrow(75, 95, 110, 95, color=LINE, sw=1.8))

    # Суматор 1 (похибка z)
    frags.append(circle(125, 95, 14, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(125, 99, "Σ", size=13, color=INK, bold=True))
    frags.append(plus(108, 83, 6))
    frags.append(minus(125, 120, 6))

    # P-регулятор висоти
    frags.append(arrow(140, 95, 175, 95, color=LINE, sw=1.8))
    frags.append(text(157, 85, "e_z", size=10, color=INK))
    
    b_p = rect(175, 65, 100, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6)
    frags.append(b_p)
    frags.append(text(225, 90, "P-регулятор", size=11, color=INK, bold=True))
    frags.append(text(225, 108, "V_z = Kp · e_z", size=10, color=MUTED))

    # Суматор 2 (похибка швидкості)
    frags.append(arrow(275, 95, 315, 95, color=LINE, sw=1.8))
    frags.append(text(295, 85, "V_z,des", size=10, color=FIELD, bold=True))
    
    frags.append(circle(330, 95, 14, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(330, 99, "Σ", size=13, color=INK, bold=True))
    frags.append(plus(313, 83, 6))
    frags.append(minus(330, 120, 6))

    # PID регулятор швидкості
    frags.append(arrow(345, 95, 380, 95, color=LINE, sw=1.8))
    frags.append(text(362, 85, "e_vz", size=10, color=INK))

    b_pid = rect(380, 65, 115, 60, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6)
    frags.append(b_pid)
    frags.append(text(437, 90, "PID швидкості", size=11, color=FIELD, bold=True))
    frags.append(text(437, 108, "a_z = PID(e_vz)", size=10, color=MUTED))

    # Блок додавання базової тяги зависання
    frags.append(arrow(495, 95, 530, 95, color=LINE, sw=1.8))
    frags.append(circle(545, 95, 14, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(545, 99, "+", size=14, color=POS, bold=True))
    frags.append(text(545, 50, "T_hover (база)", size=10, color=POS, bold=True))
    frags.append(arrow(545, 57, 545, 80, color=POS, sw=1.5))

    # Блок компенсації нахилу
    frags.append(arrow(560, 95, 595, 95, color=LINE, sw=1.8))
    b_tilt = rect(595, 65, 120, 60, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6)
    frags.append(b_tilt)
    frags.append(text(655, 88, "Компенсація нахилу", size=10, color=INK, bold=True))
    frags.append(text(655, 106, "/ (cos φ · cos θ)", size=10, color="#ca8a04", bold=True))

    # Блок компенсації напруги батареї
    frags.append(arrow(715, 95, 745, 95, color=LINE, sw=1.8))
    b_bat = rect(745, 65, 100, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=6)
    frags.append(b_bat)
    frags.append(text(795, 88, "Шкала напруги", size=10, color=INK, bold=True))
    frags.append(text(795, 106, "· (V_nom / V_bat)", size=10, color=POS, bold=True))

    # Стрілка на мотори
    frags.append(arrow(795, 125, 795, 160, color=LINE, sw=1.8))
    frags.append(text(805, 145, "Throttle", size=10, color=INK, bold=True, anchor="start"))

    # Блок оцінки висоти EKF знизу
    b_ekf = rect(125, 185, 560, 105, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    frags.append(b_ekf)
    frags.append(text(405, 208, "Комплексування давачів у EKF (Extended Kalman Filter)", size=12, color=INK, bold=True))

    # Входи в EKF
    frags.append(text(205, 235, "Барометр (тиск)", size=10, color=MUTED))
    frags.append(text(205, 255, "Далекомір LiDAR / УЗ", size=10, color=MUTED))
    frags.append(text(205, 275, "Акселерометр Z (IMU)", size=10, color=MUTED))

    frags.append(arrow(280, 235, 330, 235, color=LINE, sw=1.2))
    frags.append(arrow(280, 255, 330, 255, color=LINE, sw=1.2))
    frags.append(arrow(280, 275, 330, 275, color=LINE, sw=1.2))

    frags.append(rect(340, 222, 170, 60, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(425, 245, "Оцінка стану:", size=11, color=INK, bold=True))
    frags.append(text(425, 265, "z_meas та V_z,meas", size=11, color=NEG, bold=True))

    # Зворотний зв'язок від EKF до суматорів
    frags.append(line(510, 252, 535, 252, color=NEG, sw=1.5))
    frags.append(line(535, 252, 535, 150, color=NEG, sw=1.5))
    frags.append(line(535, 150, 330, 150, color=NEG, sw=1.5))
    frags.append(arrow(330, 150, 330, 115, color=NEG, sw=1.5))
    frags.append(text(342, 140, "V_z,meas", size=9, color=NEG, anchor="start"))

    frags.append(line(535, 150, 125, 150, color=NEG, sw=1.5))
    frags.append(arrow(125, 150, 125, 115, color=NEG, sw=1.5))
    frags.append(text(137, 140, "z_meas", size=9, color=NEG, anchor="start"))

    render(os.path.join(IMG_DIR, 'altitude-control-loop.svg'), w, h, *frags)
    print("Generated altitude-control-loop.svg")


def fig_heading_shortest_arc():
    """Фігура 3: Обчислення похибки курсу на колі S¹ та захист від розкручування."""
    w, h = 860, 300
    frags = []

    frags.append(text(w / 2, 25, "Утримання курсу: обчислення найкоротшої дуги на колі S¹", size=14, color=INK, bold=True))

    # Ліва частина: Коло кутів
    cx, cy, r = 210, 160, 95
    frags.append(circle(cx, cy, r, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(line(cx - r - 15, cy, cx + r + 15, cy, color="#cbd5e1", sw=1, dash="4,4"))
    frags.append(line(cx, cy - r - 15, cx, cy + r + 15, color="#cbd5e1", sw=1, dash="4,4"))

    # Позначки градусів на колі
    frags.append(text(cx, cy - r - 6, "0° / Північ", size=10, color=MUTED, bold=True))
    frags.append(text(cx + r + 24, cy + 4, "+90° (Схід)", size=9, color=MUTED))
    frags.append(text(cx, cy + r + 16, "±180° (Розрив)", size=10, color=POS, bold=True))
    frags.append(text(cx - r - 24, cy + 4, "-90° (Захід)", size=9, color=MUTED))

    # Вектор виміряного курсу ψ_meas = +170°
    a_meas = math.radians(170 - 90)
    x_m = cx + r * math.cos(a_meas)
    y_m = cy + r * math.sin(a_meas)
    frags.append(arrow(cx, cy, x_m, y_m, color=NEG, sw=2.2))
    frags.append(text(x_m + 15, y_m + 8, "ψ_meas (+170°)", size=10, color=NEG, bold=True, anchor="start"))

    # Вектор цільового курсу ψ_target = -170° (= +190°)
    a_tgt = math.radians(-170 - 90)
    x_t = cx + r * math.cos(a_tgt)
    y_t = cy + r * math.sin(a_tgt)
    frags.append(arrow(cx, cy, x_t, y_t, color=FIELD, sw=2.2))
    frags.append(text(x_t - 15, y_t + 8, "ψ_target (-170°)", size=10, color=FIELD, bold=True, anchor="end"))

    # Коротка дуга (правильна)
    frags.append(circle(cx, cy + r, 12, fill="#fef3c7", stroke=POS, sw=1.5))
    frags.append(text(cx, cy + r + 4, "20°", size=9, color=POS, bold=True))

    # Права частина: Порівняння формул
    b_comp = rect(440, 55, 395, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    frags.append(b_comp)

    frags.append(text(637, 80, "Пастка наївного віднімання кутів", size=12, color=INK, bold=True))

    # Наївний варіант
    frags.append(rect(460, 98, 355, 62, fill="#fee2e2", stroke=POS, sw=1.2, rx=5))
    frags.append(text(475, 118, "Наївне віднімання: e = ψ_target - ψ_meas", size=10, color=POS, bold=True, anchor="start"))
    frags.append(text(475, 136, "e = -170° - (+170°) = -340°", size=10, color=INK, bold=True, anchor="start"))
    frags.append(text(475, 152, "✖ Дрон робить майже повний розворот (unwinding)", size=9, color=POS, italic=True, anchor="start"))

    # Правильний варіант
    frags.append(rect(460, 172, 355, 88, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(475, 192, "Нормалізація на S¹ (найкоротша дуга):", size=10, color=FIELD, bold=True, anchor="start"))
    frags.append(text(475, 212, "e_yaw = atan2(sin(Δψ), cos(Δψ))", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(475, 232, "e_yaw = wrap_pi(-340°) = +20°", size=10, color=FIELD, bold=True, anchor="start"))
    frags.append(text(475, 248, "✔ Короткий доворот на 20° через нульовий розрив", size=9, color=FIELD, italic=True, anchor="start"))

    render(os.path.join(IMG_DIR, 'heading-error-shortest-arc.svg'), w, h, *frags)
    print("Generated heading-error-shortest-arc.svg")


def fig_position_projection():
    """Фігура 4: Перетворення похибки позиції з площини NEU в бажані кути нахилу."""
    w, h = 880, 310
    frags = []

    frags.append(text(w / 2, 26, "Трансляція похибки позиції NEU у нахили корпусу (Roll & Pitch)", size=14, color=INK, bold=True))

    # Крок 1: Похибка координат у площині Землі
    b1 = rect(25, 65, 200, 215, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6)
    frags.append(b1)
    frags.append(text(125, 90, "1. Позиція (Earth NEU)", size=11, color=INK, bold=True))
    frags.append(line(40, 100, 210, 100, color="#cbd5e1", sw=1))
    frags.append(text(125, 125, "e_North = r_N,tgt - r_N", size=10, color=INK))
    frags.append(text(125, 145, "e_East  = r_E,tgt - r_E", size=10, color=INK))
    frags.append(text(125, 175, "P-контур позиції:", size=10, color=MUTED))
    frags.append(text(125, 195, "v_N,des = Kp_pos · e_North", size=10, color=FIELD, bold=True))
    frags.append(text(125, 215, "v_E,des = Kp_pos · e_East", size=10, color=FIELD, bold=True))
    frags.append(text(125, 255, "Затиск: ||v_des|| ≤ V_max", size=9, color=POS, italic=True))

    frags.append(arrow(230, 170, 265, 170, color=LINE, sw=1.8))

    # Крок 2: PID швидкостей -> бажані прискорення a_N, a_E
    b2 = rect(270, 65, 195, 215, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6)
    frags.append(b2)
    frags.append(text(367, 90, "2. Швидкість (PID)", size=11, color=FIELD, bold=True))
    frags.append(line(285, 100, 450, 100, color="#bbf7d0", sw=1))
    frags.append(text(367, 125, "e_vN = v_N,des - v_N,meas", size=10, color=INK))
    frags.append(text(367, 145, "e_vE = v_E,des - v_E,meas", size=10, color=INK))
    frags.append(text(367, 175, "PID + інтеграл вітру:", size=10, color=MUTED))
    frags.append(text(367, 195, "a_N = PID(e_vN)", size=10, color=INK, bold=True))
    frags.append(text(367, 215, "a_E = PID(e_vE)", size=10, color=INK, bold=True))
    frags.append(text(367, 255, "Вектор тяги в площині", size=9, color=MUTED, italic=True))

    frags.append(arrow(470, 170, 505, 170, color=LINE, sw=1.8))

    # Крок 3: Проекція на курс апарата (Body Frame Rotation)
    b3 = rect(510, 65, 185, 215, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6)
    frags.append(b3)
    frags.append(text(602, 90, "3. Проекція на курс ψ", size=11, color="#ca8a04", bold=True))
    frags.append(line(525, 100, 680, 100, color="#fef08a", sw=1))
    frags.append(text(602, 125, "Поворот на курс ψ:", size=10, color=MUTED))
    frags.append(text(602, 155, "a_fwd  = a_N·cos ψ + a_E·sin ψ", size=9, color=INK, bold=True))
    frags.append(text(602, 185, "a_rgt  = -a_N·sin ψ + a_E·cos ψ", size=9, color=INK, bold=True))
    frags.append(text(602, 225, "Поздовжня та бічна", size=10, color=MUTED))
    frags.append(text(602, 245, "сили корпусу", size=10, color=MUTED))

    frags.append(arrow(700, 170, 735, 170, color=LINE, sw=1.8))

    # Крок 4: Бажані кути крену й тангажу
    b4 = rect(740, 65, 125, 215, fill="#fee2e2", stroke=POS, sw=1.8, rx=6)
    frags.append(b4)
    frags.append(text(802, 90, "4. Кути", size=11, color=POS, bold=True))
    frags.append(line(750, 100, 855, 100, color="#fecaca", sw=1))
    frags.append(text(802, 125, "Гравітація g", size=10, color=MUTED))
    frags.append(text(802, 155, "Pitch (тангаж):", size=10, color=INK, bold=True))
    frags.append(text(802, 175, "θ = atan2(a_fwd, g)", size=9, color=POS, bold=True))
    frags.append(text(802, 210, "Roll (крен):", size=10, color=INK, bold=True))
    frags.append(text(802, 230, "φ = atan2(a_rgt, g)", size=9, color=POS, bold=True))
    frags.append(text(802, 260, "Затиск: ≤ 35°", size=9, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, 'position-to-attitude-projection.svg'), w, h, *frags)
    print("Generated position-to-attitude-projection.svg")


if __name__ == '__main__':
    fig_cascaded_hierarchy()
    fig_altitude_control()
    fig_heading_shortest_arc()
    fig_position_projection()
