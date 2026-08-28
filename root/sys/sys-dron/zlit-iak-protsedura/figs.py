#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми zlit-iak-protsedura.
Вивід у ./img/
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_takeoff_state_machine():
    """Фігура 1: Скінченний автомат процедури зльоту."""
    w, h = 880, 480
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок
    frags.append(text(w / 2, 28, "Скінченний автомат автоматичного зльоту (Takeoff FSM)", size=16, bold=True))
    
    # 5 основних послідовних станів (зліва направо вгорі та вниз)
    # Стан 1: DISARMED
    s1, _, _ = textbox(110, 110, "1. DISARMED\n• Мотори вимкнено\n• Pre-Arm перевірки\n• Очікування команди",
                       size=11, pad=8, fill=FILL, stroke=LINE, min_w=150)
    frags.append(s1)
    
    # Стрілка 1 -> 2
    frags.append(arrow(185, 110, 245, 110, color=LINE, sw=1.8))
    frags.append(text(215, 95, "ARM", size=10, bold=True, color=FIELD))
    
    # Стан 2: SPOOLUP
    s2, _, _ = textbox(325, 110, "2. ARMING_SPOOLUP\n• Холостий хід (Idle)\n• Рампа розкрутки (1.0 с)\n• Баланс струмів та RPM",
                       size=11, pad=8, fill="#eff6ff", stroke=NEG, min_w=150)
    frags.append(s2)
    
    # Стрілка 2 -> 3
    frags.append(arrow(400, 110, 465, 110, color=LINE, sw=1.8))
    frags.append(text(432, 95, "Оберти OK", size=10, bold=True, color=FIELD))
    
    # Стан 3: GROUND_EFFECT_RAMP
    s3, _, _ = textbox(550, 110, "3. GROUND_RAMP\n• Тяга 60–70%\n• Заморожування I-термів\n• Фіксація Home Point",
                       size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=160)
    frags.append(s3)
    
    # Стрілка 3 -> 4
    frags.append(arrow(630, 110, 695, 110, color=LINE, sw=1.8))
    frags.append(text(662, 95, "Відрив", size=10, bold=True, color=FIELD))
    
    # Стан 4: RAPID_CLIMB
    s4, _, _ = textbox(775, 110, "4. RAPID_CLIMB\n• Пробиття екрана\n• Vz = 2.0 м/с\n• Розмороження PID",
                       size=11, pad=8, fill="#dcfce7", stroke=FIELD, min_w=140)
    frags.append(s4)
    
    # Стрілка 4 -> 5 (вниз)
    frags.append(arrow(775, 160, 775, 235, color=LINE, sw=1.8))
    frags.append(text(780, 200, "z ≥ h_target", size=10, bold=True, color=FIELD, anchor="start"))
    
    # Стан 5: TAKEOFF_COMPLETE
    s5, _, _ = textbox(775, 290, "5. COMPLETE\n• Гасіння швидкості\n• Утримання висоти\n• Перехід до місії",
                       size=11, pad=8, fill="#f3e8ff", stroke="#7e22ce", min_w=150)
    frags.append(s5)
    
    # Стан АВАРІЙНИЙ: TAKEOFF_ABORT
    sab, _, _ = textbox(440, 360, "TAKEOFF_ABORT (Аварійне переривання зльоту)\n• Миттєве скидання газу на 0 (Disarm)\n• Захист: нахил > 15°, перекіс струмів, застрягання, таймаут розкрутки\n• MAVLink STATUSTEXT (CRITICAL)",
                        size=11, pad=10, fill="#fee2e2", stroke=POS, min_w=460)
    frags.append(sab)
    
    # Аварійні стрілки до ABORT
    # Від Spoolup
    frags.append(arrow(325, 160, 350, 300, color=POS, sw=1.5))
    frags.append(text(300, 230, "Асиметрія струму / Клин", size=10, color=POS, bold=True))
    
    # Від Ground Ramp
    frags.append(arrow(550, 160, 520, 300, color=POS, sw=1.5))
    frags.append(text(575, 230, "Нахил > 15° / Застрягання", size=10, color=POS, bold=True))
    
    # Від Rapid Climb
    frags.append(arrow(720, 160, 580, 320, color=POS, sw=1.5))
    frags.append(text(660, 260, "EKF збій / Відмова мотора", size=10, color=POS, bold=True))
    
    # Від Abort назад до Disarmed
    frags.append(arrow(210, 360, 110, 160, color=MUTED, sw=1.5))
    frags.append(text(120, 290, "Скидання у Disarm", size=10, color=MUTED, italic=True))
    
    # Нижній підпис
    frags.append(text(w / 2, 445, "Кожен крок зльоту захищено часовими та просторовими порогами; відхилення веде до негайного Disarm",
                      size=12, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, 'takeoff-state-machine.svg'), w, h, *frags)
    print("Generated takeoff-state-machine.svg")


def fig_ground_effect_aerodynamics():
    """Фігура 2: Аеродинаміка ротора у вільному повітрі та біля поверхні землі."""
    w, h = 880, 420
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    frags.append(text(w / 2, 26, "Аеродинаміка ротора: вільне повітря проти екранного ефекту землі", size=15, bold=True))
    
    # Ліва панель: Вільне повітря (h > 1.5 D)
    frags.append(rect(25, 55, 400, 315, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(225, 80, "Вільне повітря (Out of Ground Effect, OGE)", size=13, bold=True))
    frags.append(text(225, 100, "Висота h > 1.5 · D (вільний схід струменя)", size=11, color=MUTED))
    
    # Ротор OGE
    frags.append(line(125, 160, 325, 160, color=LINE, sw=4))
    frags.append(circle(225, 160, 8, fill=LINE, stroke=LINE))
    frags.append(text(225, 150, "Площина ротора (D)", size=11, bold=True))
    
    # Вектор тяги OGE
    frags.append(arrow(225, 140, 225, 95, color=POS, sw=2.5))
    frags.append(text(235, 115, "Тяга T_OGE", size=11, bold=True, color=POS, anchor="start"))
    
    # Струмені вниз
    for offset in [-70, -35, 0, 35, 70]:
        frags.append(arrow(225 + offset, 170, 225 + offset * 0.8, 280, color=NEG, sw=1.5))
    frags.append(text(225, 305, "Індуктивна швидкість v_i,∞ (максимальна)", size=11, color=NEG, bold=True))
    frags.append(text(225, 325, "Звуження струменя (вена контракта)", size=10, color=MUTED))
    frags.append(text(225, 345, "Витрата потужності на індуктивний опір: висока", size=10, color=LINE))
    
    # Права панель: В екранному ефекті (h < 0.5 D)
    frags.append(rect(455, 55, 400, 315, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(655, 80, "В екранному ефекті (In Ground Effect, IGE)", size=13, bold=True, color="#b45309"))
    frags.append(text(655, 100, "Висота h < 0.5 · D (гальмування об поверхню)", size=11, color=MUTED))
    
    # Земля
    frags.append(line(465, 290, 845, 290, color="#78350f", sw=3))
    for gx in range(475, 840, 25):
        frags.append(line(gx, 290, gx - 10, 305, color="#78350f", sw=1.2))
    frags.append(text(655, 320, "Поверхня землі (непроникна межа)", size=10, bold=True, color="#78350f"))
    
    # Ротор IGE
    frags.append(line(555, 175, 755, 175, color=LINE, sw=4))
    frags.append(circle(655, 175, 8, fill=LINE, stroke=LINE))
    frags.append(text(655, 165, "Площина ротора (D)", size=11, bold=True))
    
    # Вектор тяги IGE (більший)
    frags.append(arrow(655, 155, 655, 95, color=POS, sw=3.0))
    frags.append(text(665, 115, "Тяга T_IGE = 1.20 · T_OGE (+20%)", size=11, bold=True, color=POS, anchor="start"))
    
    # Розтікання повітряної подушки та вихори
    frags.append(rect(585, 215, 140, 55, fill="#fde68a", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(655, 238, "Подушка підвищеного", size=10, bold=True, color="#92400e"))
    frags.append(text(655, 254, "статичного тиску (+ΔP)", size=10, bold=True, color="#92400e"))
    
    # Радіальні стрілки розтікання
    frags.append(arrow(580, 265, 490, 275, color=NEG, sw=2))
    frags.append(arrow(730, 265, 820, 275, color=NEG, sw=2))
    
    # Рециркуляційні вихори
    frags.append(text(510, 230, "Кінцевий вихор", size=10, color=POS, italic=True))
    frags.append(text(800, 230, "Кінцевий вихор", size=10, color=POS, italic=True))
    frags.append(text(655, 345, "Знижена індуктивна швидкість v_i < v_i,∞; ризик перекидання", size=10, color="#b45309"))
    
    # Нижній підпис
    frags.append(text(w / 2, 395, "Екран створює додаткову підйомну силу, але породжує нестабільні вихори та спотворює показники барометра",
                      size=12, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, 'ground-effect-aerodynamics.svg'), w, h, *frags)
    print("Generated ground-effect-aerodynamics.svg")


def fig_spoolup_and_climb_profile():
    """Фігура 3: Часові профілі тяги, швидкості, висоти та струмів під час зльоту."""
    w, h = 880, 520
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    frags.append(text(w / 2, 25, "Динамічні профілі фаз зльоту в часі: тяга, швидкість, висота і струми", size=15, bold=True))
    
    # Фазові зони (вертикальні смуги)
    def tx(t):
        return 100 + t * 102.8
    
    # Фонове підсвічування фаз
    frags.append(rect(tx(0), 50, tx(1.0) - tx(0), 400, fill="#f1f5f9", stroke="none", rx=0))
    frags.append(rect(tx(1.0), 50, tx(2.2) - tx(1.0), 400, fill="#fef3c7", stroke="none", rx=0))
    frags.append(rect(tx(2.2), 50, tx(4.2) - tx(2.2), 400, fill="#dcfce7", stroke="none", rx=0))
    frags.append(rect(tx(4.2), 50, tx(7.0) - tx(4.2), 400, fill="#f3e8ff", stroke="none", rx=0))
    
    # Заголовки фаз
    frags.append(text((tx(0) + tx(1.0)) / 2, 65, "1. Spool-Up", size=11, bold=True))
    frags.append(text((tx(1.0) + tx(2.2)) / 2, 65, "2. Ground Ramp", size=11, bold=True))
    frags.append(text((tx(2.2) + tx(4.2)) / 2, 65, "3. Rapid Climb (Екран)", size=11, bold=True))
    frags.append(text((tx(4.2) + tx(7.0)) / 2, 65, "4. Level-off / Mission", size=11, bold=True))
    
    # Розділові вертикальні пунктири
    for t_val in [1.0, 2.2, 4.2]:
        frags.append(line(tx(t_val), 50, tx(t_val), 450, color=MUTED, sw=1.2, dash="4,4"))
    
    # Графік 1: Тяга u(t) (Y від 90 до 160)
    frags.append(line(tx(0), 160, tx(7.0), 160, color=LINE, sw=1.2))
    frags.append(text(50, 125, "Тяга u\n[%]", size=11, bold=True, color=POS))
    p_u = [
        (tx(0), 155),
        (tx(0.8), 145),
        (tx(1.0), 145),
        (tx(2.2), 95),   # 65% throttle
        (tx(3.8), 98),
        (tx(4.5), 115),  # hover 50%
        (tx(7.0), 115)
    ]
    for i in range(len(p_u) - 1):
        frags.append(line(p_u[i][0], p_u[i][1], p_u[i+1][0], p_u[i+1][1], color=POS, sw=2.2))
    frags.append(text(tx(2.2), 85, "65% (Відрив)", size=10, color=POS, bold=True))
    frags.append(text(tx(5.5), 105, "50% (Висіння)", size=10, color=POS))
    
    # Графік 2: Вертикальна швидкість Vz(t) (Y від 190 до 260)
    frags.append(line(tx(0), 260, tx(7.0), 260, color=LINE, sw=1.2))
    frags.append(text(50, 225, "Швидкість Vz\n[м/с]", size=11, bold=True, color=FIELD))
    p_v = [
        (tx(0), 260),
        (tx(2.0), 260),
        (tx(2.2), 255),
        (tx(2.8), 200),  # Vz = 2.0 m/s
        (tx(3.8), 200),
        (tx(4.8), 260),  # brake to 0
        (tx(7.0), 260)
    ]
    for i in range(len(p_v) - 1):
        frags.append(line(p_v[i][0], p_v[i][1], p_v[i+1][0], p_v[i+1][1], color=FIELD, sw=2.2))
    frags.append(text(tx(3.3), 190, "+2.0 м/с (Пробиття)", size=10, color=FIELD, bold=True))
    
    # Графік 3: Висота z(t) (Y від 290 до 360)
    frags.append(line(tx(0), 360, tx(7.0), 360, color=LINE, sw=1.2))
    frags.append(text(50, 325, "Висота z\n[м]", size=11, bold=True, color=NEG))
    p_z = [
        (tx(0), 360),
        (tx(2.0), 360),
        (tx(2.2), 358),
        (tx(3.2), 330),
        (tx(4.5), 295),  # target 5.0m
        (tx(7.0), 295)
    ]
    for i in range(len(p_z) - 1):
        frags.append(line(p_z[i][0], p_z[i][1], p_z[i+1][0], p_z[i+1][1], color=NEG, sw=2.2))
    frags.append(line(tx(0), 340, tx(7.0), 340, color="#d97706", sw=1.0, dash="3,3"))
    frags.append(text(tx(1.5), 335, "Межа екрана (1.2 м)", size=9, color="#d97706"))
    frags.append(text(tx(5.5), 285, "h_target = 5.0 м", size=10, color=NEG, bold=True))
    
    # Графік 4: Струми моторів I_1..I_4 (Y від 390 до 450)
    frags.append(line(tx(0), 450, tx(7.0), 450, color=LINE, sw=1.2))
    frags.append(text(50, 420, "Струми I_i\n[А]", size=11, bold=True, color="#7e22ce"))
    p_i = [
        (tx(0), 450),
        (tx(0.8), 442),
        (tx(1.0), 442),  # 2.5A idle
        (tx(2.2), 400),  # 15A punch
        (tx(3.8), 405),
        (tx(4.5), 422),  # 9A hover
        (tx(7.0), 422)
    ]
    for k in range(len(p_i) - 1):
        frags.append(line(p_i[k][0], p_i[k][1], p_i[k+1][0], p_i[k+1][1], color="#7e22ce", sw=2.0))
    frags.append(line(tx(0), 385, tx(7.0), 385, color=POS, sw=1.2, dash="4,4"))
    frags.append(text(tx(6.2), 380, "Поріг аварійного перекосу (Abort)", size=9, color=POS, bold=True))
    
    # Вісь часу знизу
    frags.append(arrow(tx(0), 465, tx(7.0) + 15, 465, color=LINE, sw=1.5))
    frags.append(text(tx(7.0) + 25, 465, "t [c]", size=11, bold=True, anchor="start"))
    for t_sec in range(8):
        frags.append(line(tx(t_sec), 462, tx(t_sec), 468, color=LINE, sw=1.2))
        frags.append(text(tx(t_sec), 480, str(t_sec), size=10))
    
    # Підпис внизу
    frags.append(text(w / 2, 505, "Послідовне проходження фаз зльоту: від холостого ходу до стабільного зависання на цільовій висоті",
                      size=12, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, 'spoolup-and-climb-profile.svg'), w, h, *frags)
    print("Generated spoolup-and-climb-profile.svg")


def fig_home_point_latch():
    """Фігура 4: Геометрія та система координат фіксації Home Point."""
    w, h = 880, 400
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    frags.append(text(w / 2, 26, "Ініціалізація та фіксація точки старту (Home Point Initialization)", size=15, bold=True))
    
    # Лівий блок: Супутники GNSS та прийом сигналів
    frags.append(rect(30, 60, 240, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(150, 85, "1. Глобальний простір (GNSS)", size=12, bold=True))
    
    # Супутник
    frags.append(circle(150, 130, 16, fill="#e0f2fe", stroke=NEG, sw=1.8))
    frags.append(text(150, 134, "GNSS", size=10, bold=True, color=NEG))
    frags.append(line(125, 130, 175, 130, color=NEG, sw=2))
    
    # Промені до антени
    frags.append(arrow(105, 150, 105, 220, color=NEG, sw=1.5))
    frags.append(text(115, 185, "3D Fix (≥ 8 супутників)", size=10, color=NEG, italic=True, anchor="start"))
    
    # Координати WGS-84
    frags.append(rect(45, 230, 210, 100, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(150, 250, "Опорні координати WGS-84:", size=10, bold=True))
    frags.append(text(150, 270, "• Широта φ₀ [deg]", size=10, color=INK))
    frags.append(text(150, 290, "• Довгота λ₀ [deg]", size=10, color=INK))
    frags.append(text(150, 310, "• Висота h_AMSL,0 [м]", size=10, color=INK))
    
    # Центральна стрілка фіксації
    frags.append(arrow(275, 205, 345, 205, color=FIELD, sw=2.5))
    frags.append(text(310, 190, "LATCH", size=11, bold=True, color=FIELD))
    frags.append(text(310, 225, "в момент\nARM / Відриву", size=10, color=FIELD))
    
    # Правий блок: Локальна система відліку NED і Home Point
    frags.append(rect(355, 60, 495, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(600, 85, "2. Локальна навігаційна площина NED (North-East-Down)", size=12, bold=True))
    
    # Поверхня землі
    frags.append(line(375, 270, 830, 270, color="#78350f", sw=2.5))
    frags.append(text(430, 288, "Поверхня землі", size=10, color="#78350f", bold=True))
    
    # Точка Home (0,0,0)
    frags.append(circle(480, 270, 9, fill=POS, stroke=LINE, sw=2))
    frags.append(text(480, 310, "HOME POINT\nNED: [0, 0, 0]ᵀ\nБарометр: P₀ (h_rel = 0)", size=10, bold=True, color=POS))
    
    # Дрон у повітрі на висоті h_target
    frags.append(line(670, 150, 770, 150, color=LINE, sw=3))
    frags.append(circle(720, 150, 10, fill="#fef08a", stroke=LINE, sw=2))
    frags.append(circle(680, 145, 12, fill="none", stroke=NEG, sw=1.2))
    frags.append(circle(760, 145, 12, fill="none", stroke=NEG, sw=1.2))
    frags.append(text(720, 130, "Позиція після зльоту", size=10, bold=True))
    
    # Вектор підйому
    frags.append(arrow(480, 270, 720, 160, color=FIELD, sw=2.2))
    frags.append(text(585, 200, "Вектор цілі: [0, 0, -h_target]ᵀ", size=11, bold=True, color=FIELD))
    
    # Висота
    frags.append(line(720, 150, 720, 270, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(text(735, 215, "h_target", size=11, bold=True, color=NEG, anchor="start"))
    
    # Прив'язка до RTL та Geofence
    frags.append(rect(530, 310, 305, 30, fill="#e0e7ff", stroke="#4338ca", sw=1.2, rx=4))
    frags.append(text(682, 330, "База для аварійного повернення (RTL) та Geofence", size=10, bold=True, color="#3730a3"))
    
    # Підпис внизу
    frags.append(text(w / 2, 380, "Home Point жорстко прив'язує нуль локальної системи координат NED та нуль відносної висоти",
                      size=12, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, 'home-point-latch-geometry.svg'), w, h, *frags)
    print("Generated home-point-latch-geometry.svg")


def main():
    fig_takeoff_state_machine()
    fig_ground_effect_aerodynamics()
    fig_spoolup_and_climb_profile()
    fig_home_point_latch()


if __name__ == '__main__':
    main()
