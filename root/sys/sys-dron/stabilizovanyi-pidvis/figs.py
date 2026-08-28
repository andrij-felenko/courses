#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми stabilizovanyi-pidvis.
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


def fig_gimbal_axes_kinematics():
    """Фігура 1: Кінематична схема 3-осьового підвісу (Yaw -> Roll -> Pitch) та розташування сенсорів."""
    w, h = 860, 420
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок зверху
    elements.append(text(430, 28, "Кінематична структура триосьового підвісу та топологія сенсорів", size=14, color=INK, bold=True))
    
    # Рама дрона зверху
    b_frame, _, _ = textbox(430, 65, "Рама апарата (Базовий рівень) + IMU рами (Base IMU)", size=12, pad=8, fill="#e2e8f0", stroke=LINE, min_w=380)
    elements.append(b_frame)
    
    # З'єднання від рами до мотора Yaw
    elements.append(line(430, 85, 430, 115, color=LINE, sw=2.0))
    
    # Мотор 1: Yaw (Курс)
    b_yaw, _, _ = textbox(430, 135, "Мотор прямого приводу YAW (Курс)\nБезколекторний двигун (28P) + Магнітний енкодер (AS5048A)", size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=390)
    elements.append(b_yaw)
    
    # Балка від Yaw до мотора Roll (Г-подібний кронштейн)
    elements.append(line(235, 135, 140, 135, color=LINE, sw=2.0))
    elements.append(line(140, 135, 140, 225, color=LINE, sw=2.0))
    elements.append(line(140, 225, 190, 225, color=LINE, sw=2.0))
    
    # Мотор 2: Roll (Крен)
    b_roll, _, _ = textbox(360, 225, "Мотор прямого приводу ROLL (Крен)\nСтабілізація лінії горизонту (22P) + Енкодер кута", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=340)
    elements.append(b_roll)
    
    # Балка від Roll до Pitch (П-подібна вилка)
    elements.append(line(530, 225, 720, 225, color=LINE, sw=2.0))
    elements.append(line(720, 225, 720, 315, color=LINE, sw=2.0))
    elements.append(line(720, 315, 650, 315, color=LINE, sw=2.0))
    
    # Мотор 3: Pitch (Тангаж)
    b_pitch, _, _ = textbox(480, 315, "Мотор прямого приводу PITCH (Тангаж)\nНахил камери (14P/22P) + Енкодер кута", size=11, pad=8, fill="#dbeafe", stroke=NEG, min_w=340)
    elements.append(b_pitch)
    
    # Зв'язок від Pitch до платформи камери
    elements.append(line(310, 315, 230, 315, color=LINE, sw=2.0))
    elements.append(arrow(230, 315, 230, 355, color=LINE, sw=2.0))
    
    # Корисне навантаження: Камера з IMU
    b_cam = rect(110, 355, 240, 52, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=6)
    elements.append(b_cam)
    elements.append(text(230, 375, "Камера (Корисне навантаження)", size=11, color=INK, bold=True))
    elements.append(text(230, 395, "Головний сенсор IMU (Gyro + Accel)", size=10, color=FIELD, bold=True))
    
    # Пояснювальні плашки збоку
    p1 = rect(590, 355, 240, 52, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=6)
    elements.append(p1)
    elements.append(text(710, 373, "Порядок осей: Z (Yaw) → X (Roll) → Y (Pitch)", size=10, color=INK))
    elements.append(text(710, 392, "Прямий привід без люфтів і зазорів", size=10, color=MUTED))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'gimbal-axes-kinematics.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_foc_clarke_park_dq():
    """Фігура 2: Перетворення координат у векторному керуванні (Clarke abc->αβ, Park αβ->dq)."""
    w, h = 860, 340
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(430, 26, "Векторні простори FOC: Трифазний (a-b-c) → Нерухомий (α-β) → Обертовий роторний (d-q)", size=13, color=INK, bold=True))
    
    # 1. Трифазна система a-b-c
    b1_body = rect(30, 55, 230, 245, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    elements.append(b1_body)
    elements.append(text(145, 80, "Трифазна система (a, b, c)", size=12, color=INK, bold=True))
    elements.append(text(145, 102, "3 осі зі зсувом 120°", size=10, color=MUTED))
    
    # Осі a, b, c
    cx1, cy1 = 145, 190
    elements.append(arrow(cx1, cy1, cx1 + 75, cy1, color=POS, sw=2.0))
    elements.append(text(cx1 + 82, cy1 - 4, "a", size=12, color=POS, bold=True))
    
    elements.append(arrow(cx1, cy1, cx1 - 37.5, cy1 - 65, color=FIELD, sw=2.0))
    elements.append(text(cx1 - 45, cy1 - 70, "b", size=12, color=FIELD, bold=True))
    
    elements.append(arrow(cx1, cy1, cx1 - 37.5, cy1 + 65, color=NEG, sw=2.0))
    elements.append(text(cx1 - 45, cy1 + 75, "c", size=12, color=NEG, bold=True))
    
    elements.append(text(145, 285, "i_a + i_b + i_c = 0", size=11, color=INK, bold=True))
    
    # Стрілка перетворення Кларк
    elements.append(arrow(265, 175, 315, 175, color="#d97706", sw=2.2))
    elements.append(text(290, 160, "Кларк", size=11, color="#d97706", bold=True))
    
    # 2. Нерухома ортогональна система α-β
    b2_body = rect(320, 55, 230, 245, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    elements.append(b2_body)
    elements.append(text(435, 80, "Стаціонарна система (α, β)", size=12, color=INK, bold=True))
    elements.append(text(435, 102, "2 ортогональні осі (90°)", size=10, color=MUTED))
    
    # Осі α, β
    cx2, cy2 = 435, 190
    elements.append(arrow(cx2, cy2, cx2 + 75, cy2, color=POS, sw=2.0))
    elements.append(text(cx2 + 82, cy2 - 4, "α", size=12, color=POS, bold=True))
    
    elements.append(arrow(cx2, cy2, cx2, cy2 - 75, color=NEG, sw=2.0))
    elements.append(text(cx2 + 8, cy2 - 75, "β", size=12, color=NEG, bold=True))
    
    # Сумарний вектор напруги/струму Vs
    elements.append(arrow(cx2, cy2, cx2 + 50, cy2 - 50, color="#7c3aed", sw=2.2))
    elements.append(text(cx2 + 58, cy2 - 52, "V_s", size=11, color="#7c3aed", bold=True))
    
    elements.append(text(435, 285, "V_α = v_a,  V_β = (v_a+2v_b)/√3", size=10, color=INK))
    
    # Стрілка перетворення Парка
    elements.append(arrow(555, 175, 605, 175, color="#d97706", sw=2.2))
    elements.append(text(580, 160, "Парк", size=11, color="#d97706", bold=True))
    elements.append(text(580, 195, "кут θ_e", size=10, color=MUTED))
    
    # 3. Обертова система d-q ротора
    b3_body = rect(610, 55, 220, 245, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    elements.append(b3_body)
    elements.append(text(720, 80, "Роторна система (d, q)", size=12, color=INK, bold=True))
    elements.append(text(720, 102, "Обертається разом із ротором", size=10, color=MUTED))
    
    # Осі d, q під кутом θ_e
    cx3, cy3 = 720, 190
    angle_deg = 35
    rad = math.radians(angle_deg)
    
    # Вісь d (потік магніту)
    dx, dy = 70 * math.cos(rad), -70 * math.sin(rad)
    elements.append(arrow(cx3, cy3, cx3 + dx, cy3 + dy, color=FIELD, sw=2.0))
    elements.append(text(cx3 + dx + 10, cy3 + dy, "d (потік)", size=11, color=FIELD, bold=True))
    
    # Вісь q (перпендикулярна, крутний момент)
    qx, qy = -70 * math.sin(rad), -70 * math.cos(rad)
    elements.append(arrow(cx3, cy3, cx3 + qx, cy3 + qy, color=POS, sw=2.0))
    elements.append(text(cx3 + qx - 8, cy3 + qy - 6, "q (момент)", size=11, color=POS, bold=True))
    
    elements.append(text(720, 275, "I_d = 0 (без нагріву)", size=10, color=FIELD, bold=True))
    elements.append(text(720, 292, "I_q = τ / K_t (чистий момент)", size=10, color=POS, bold=True))
    
    # Пояснення знизу
    elements.append(text(430, 325, "Положення ротора θ_e задає поворот осей; струм у осі q створює 100% корисного моменту без пульсацій", size=11, color=MUTED, italic=True))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'foc-clarke-park-dq.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_svpwm_hexagonal_sectors():
    """Фігура 3: Гексагональна діаграма просторових векторів SVPWM (Сектори 1..6, базові та нульові вектори)."""
    w, h = 860, 420
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(430, 25, "Широтно-імпульсна модуляція просторового вектора (SVPWM) у шести секторах", size=13, color=INK, bold=True))
    
    cx, cy = 290, 220
    R = 145
    
    # 6 базових векторів V1..V6
    vectors = [
        ("V1 (100)", 0),
        ("V2 (110)", 60),
        ("V3 (010)", 120),
        ("V4 (011)", 180),
        ("V5 (001)", 240),
        ("V6 (101)", 300)
    ]
    
    coords = []
    for name, deg in vectors:
        rad = math.radians(deg)
        vx = cx + R * math.cos(rad)
        vy = cy - R * math.sin(rad)
        coords.append((vx, vy, name, deg))
    
    # Малюємо шестикутник
    hex_pts = " ".join([f"{vx:.1f},{vy:.1f}" for vx, vy, _, _ in coords])
    elements.append(f'<polygon points="{hex_pts}" fill="#f1f5f9" stroke="{LINE}" stroke-width="1.8" stroke-dasharray="4,4"/>')
    
    # Вписане коло (максимальна синусоїдальна напруга без спотворень: V_max = V_dc / √3 ≈ 0.577 V_dc)
    r_inscribed = R * math.cos(math.radians(30))
    elements.append(circle(cx, cy, r_inscribed, fill="none", stroke="#2563eb", sw=1.5))
    
    # Малюємо базові стрілки від центру
    for vx, vy, name, deg in coords:
        elements.append(arrow(cx, cy, vx, vy, color=LINE, sw=1.8))
        # Зміщення для тексту
        rad = math.radians(deg)
        tx = cx + (R + 26) * math.cos(rad)
        ty = cy - (R + 14) * math.sin(rad) + 4
        elements.append(text(tx, ty, name, size=11, color=INK, bold=True))
    
    # Позначення секторів S1..S6 (радіус 75, зміщення від стрілок)
    for i in range(6):
        deg_mid = i * 60 + 30
        rad_mid = math.radians(deg_mid)
        sx = cx + 75 * math.cos(rad_mid)
        sy = cy - 75 * math.sin(rad_mid) + 4
        elements.append(text(sx, sy, f"S{i+1}", size=11, color=MUTED, bold=True))
    
    # Нульові вектори в центрі
    elements.append(circle(cx, cy, 4, fill="#ef4444", stroke=LINE, sw=1.0))
    elements.append(text(cx - 24, cy - 8, "V0, V7", size=10, color=POS, bold=True))
    
    # Синтезований вектор V_out у секторі 1 (радіус 80, далеко від кола 125)
    target_deg = 18
    target_rad = math.radians(target_deg)
    target_len = 80
    tvx = cx + target_len * math.cos(target_rad)
    tvy = cy - target_len * math.sin(target_rad)
    elements.append(arrow(cx, cy, tvx, tvy, color="#7c3aed", sw=2.5))
    elements.append(text(tvx + 18, tvy + 4, "V_out", size=11, color="#7c3aed", bold=True))
    
    # Права інформаційна панель
    panel = rect(560, 55, 275, 335, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    elements.append(panel)
    elements.append(text(697, 80, "Синтез напруги в SVPWM", size=12, color=INK, bold=True))
    
    elements.append(text(697, 112, "Час увімкнення базових векторів:", size=11, color=INK, bold=True))
    elements.append(text(697, 134, "T1 = T_s · m · sin(60° − θ)", size=11, color="#7c3aed"))
    elements.append(text(697, 154, "T2 = T_s · m · sin(θ)", size=11, color="#7c3aed"))
    elements.append(text(697, 174, "T0 = T_s − T1 − T2 (нульовий стан)", size=11, color=POS))
    
    elements.append(line(580, 195, 815, 195, color=MUTED, sw=1.0, dash="2,2"))
    
    elements.append(text(697, 220, "Ключові переваги над SPWM:", size=11, color=FIELD, bold=True))
    elements.append(text(697, 245, "• +15.5% використання шини DC", size=10, color=INK))
    elements.append(text(697, 265, "• Коефіцієнт: 1 / √3 ≈ 0.577 V_dc", size=10, color=INK))
    elements.append(text(697, 285, "• Мінімальні гармоніки струму", size=10, color=INK))
    elements.append(text(697, 305, "• Плавний крутний момент без ривків", size=10, color=INK))
    elements.append(text(697, 330, "• Симетричне вирівнювання імпульсів", size=10, color=MUTED))
    elements.append(text(697, 360, "T_PWM: 20–30 кГц (безшумна робота)", size=10, color="#b45309", bold=True))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'svpwm-hexagonal-sectors.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_cascade_control_loops():
    """Фігура 4: Трьохконтурна каскадна структура стабілізації підвісу (Положення -> Швидкість -> FOC/Струм)."""
    w, h = 880, 310
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(440, 24, "Ієрархія трьох каскадних контурів керування віссю підвісу", size=13, color=INK, bold=True))
    
    # 1. Зовнішній контур: Кут / Положення (Angle Loop)
    b1_body = rect(30, 50, 230, 175, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8)
    elements.append(b1_body)
    elements.append(text(145, 75, "1. Контур абсолютного кута", size=11, color=NEG, bold=True))
    elements.append(text(145, 95, "Частота: 500 – 1000 Гц", size=10, color=MUTED))
    elements.append(text(145, 125, "Вхід: Цільовий кут (RC / MAVLink)", size=10, color=INK))
    elements.append(text(145, 145, "Зворотний зв'язок: IMU кут + Енкодер", size=10, color=INK))
    elements.append(text(145, 175, "Вихід: Цільова кутова швидкість ω_des", size=10, color=NEG, bold=True))
    elements.append(text(145, 205, "P- або PI-регулятор положення", size=10, color=MUTED))
    
    # Стрілка 1 -> 2
    elements.append(arrow(260, 137, 310, 137, color=NEG, sw=2.0))
    elements.append(text(285, 122, "ω_des", size=11, color=NEG, bold=True))
    
    # 2. Середній контур: Кутова швидкість (Rate Loop)
    b2_body = rect(315, 50, 250, 175, fill="#fef2f2", stroke=POS, sw=1.5, rx=8)
    elements.append(b2_body)
    elements.append(text(440, 75, "2. Контур кутової швидкості", size=11, color=POS, bold=True))
    elements.append(text(440, 95, "Частота: 1000 – 2000 Гц", size=10, color=MUTED))
    elements.append(text(440, 125, "Зворотний зв'язок: Гіроскоп камери ω_meas", size=10, color=INK))
    elements.append(text(440, 145, "PID з Anti-Windup + D-фільтр низьких частот", size=10, color=INK))
    elements.append(text(440, 175, "Вихід: Цільовий крутний момент / I_q_des", size=10, color=POS, bold=True))
    elements.append(text(440, 205, "Компенсація збурень рами в реальному часі", size=10, color=MUTED))
    
    # Стрілка 2 -> 3
    elements.append(arrow(565, 137, 615, 137, color=POS, sw=2.0))
    elements.append(text(590, 122, "I_q_des", size=11, color=POS, bold=True))
    
    # 3. Внутрішній контур: Векторне керування FOC (Current / Voltage Loop)
    b3_body = rect(620, 50, 230, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8)
    elements.append(b3_body)
    elements.append(text(735, 75, "3. Внутрішній FOC / SVPWM", size=11, color=FIELD, bold=True))
    elements.append(text(735, 95, "Частота: 10 000 – 30 000 Гц", size=10, color=MUTED))
    elements.append(text(735, 125, "Зворотний зв'язок: Енкодер θ_e + Струми", size=10, color=INK))
    elements.append(text(735, 145, "Парк, Кларк, генерація 3-фазного SVPWM", size=10, color=INK))
    elements.append(text(735, 175, "Вихід: Комутація ключів H-мостів", size=10, color=FIELD, bold=True))
    elements.append(text(735, 205, "Прямий вплив на магнітне поле статора", size=10, color=MUTED))
    
    # Нижній блок зв'язку з фізикою
    p_bot = rect(30, 245, 820, 48, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6)
    elements.append(p_bot)
    elements.append(text(440, 265, "Ієрархія швидкостей: швидкий контур FOC ізолює зовнішні контури від нелінійностей індуктивності мотора,", size=11, color=INK))
    elements.append(text(440, 282, "а контур швидкості пригнічує вібрації до того, як вони спричинять помітне відхилення кута камери", size=11, color=MUTED, italic=True))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'cascade-control-loops.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_gimbal_axes_kinematics()
    fig_foc_clarke_park_dq()
    fig_svpwm_hexagonal_sectors()
    fig_cascade_control_loops()
