# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Стан апарата як числа' (vehicle-state-as-numbers)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"/>' %
            (cx, cy, rx, ry, fill, stroke, sw))


def fig_coordinate_frames():
    """Фігура 1: Земна система NED та зв'язана система координат апарата Body Frame."""
    w, h = 880, 460
    p = []

    # Заголовок фігури
    p.append(text(w / 2, 28, "Земна система координат (NED) та зв'язана система апарата (Body Frame)", size=16, color=INK, bold=True))

    # Ліва частина: Земна система NED
    p.append(rect(30, 55, 390, 380, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(225, 84, "Земна система (NED — North-East-Down)", size=14, color=INK, bold=True))

    cx_e, cy_e = 220, 240
    # X - North (вгору-вліво)
    p.append(arrow(cx_e, cy_e, cx_e - 75, cy_e - 65, color=POS, sw=2.5))
    p.append(fitbox(50, cy_e - 100, 135, 30, "X_N (Північ / North)", size=11, bold=True, fill=BG, stroke=POS, sw=1.2))

    # Y - East (вправо)
    p.append(arrow(cx_e, cy_e, cx_e + 85, cy_e - 10, color=FIELD, sw=2.5))
    p.append(fitbox(cx_e + 95, cy_e - 25, 100, 30, "Y_E (Схід)", size=11, bold=True, fill=BG, stroke=FIELD, sw=1.2))

    # Z - Down (вниз)
    p.append(arrow(cx_e, cy_e, cx_e, cy_e + 85, color=NEG, sw=2.5))
    p.append(fitbox(cx_e - 70, cy_e + 95, 140, 30, "Z_D (Вниз / Центр)", size=11, bold=True, fill=BG, stroke=NEG, sw=1.2))

    p.append(circle(cx_e, cy_e, 4, fill=INK, stroke="none"))
    p.append(text(cx_e + 14, cy_e + 16, "Початок (O_E)", size=11, color=MUTED))
    p.append(fitbox(50, 385, 350, 34, "Висота h = -Z_D (плюс угору, Z_D униз)", size=11, fill=BG, stroke=MUTED, sw=1))

    # Права частина: Зв'язана система апарата (Body Frame)
    p.append(rect(460, 55, 390, 380, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(655, 84, "Зв'язана система (Body Frame B)", size=14, color=INK, bold=True))

    cx_b, cy_b = 645, 240
    # Промені дрона
    p.append(line(cx_b - 45, cy_b - 35, cx_b + 45, cy_b + 35, color=MUTED, sw=2))
    p.append(line(cx_b - 45, cy_b + 35, cx_b + 45, cy_b - 35, color=MUTED, sw=2))
    for mx, my in [(cx_b - 45, cy_b - 35), (cx_b + 45, cy_b + 35), (cx_b - 45, cy_b + 35), (cx_b + 45, cy_b - 35)]:
        p.append(circle(mx, my, 7, fill=BG, stroke=LINE, sw=1.2))
    p.append(circle(cx_b, cy_b, 12, fill="#dbeafe", stroke=LINE, sw=1.5))
    p.append(text(cx_b, cy_b + 4, "CG", size=10, color=LINE, bold=True))

    # X_B - вперед
    p.append(arrow(cx_b, cy_b, cx_b, cy_b - 80, color=POS, sw=2.5))
    p.append(fitbox(cx_b - 65, cy_b - 115, 130, 30, "X_B (Ніс / Forward)", size=11, bold=True, fill=BG, stroke=POS, sw=1.2))
    p.append(text(cx_b + 25, cy_b - 50, "p (крен / roll)", size=11, color=POS))

    # Y_B - вправо
    p.append(arrow(cx_b, cy_b, cx_b + 85, cy_b, color=FIELD, sw=2.5))
    p.append(fitbox(cx_b + 95, cy_b - 15, 100, 30, "Y_B (Крило)", size=11, bold=True, fill=BG, stroke=FIELD, sw=1.2))
    p.append(text(cx_b + 35, cy_b + 18, "q (тангаж)", size=11, color=FIELD))

    # Z_B - вниз
    p.append(arrow(cx_b, cy_b, cx_b - 55, cy_b + 55, color=NEG, sw=2.5))
    p.append(fitbox(cx_b - 155, cy_b + 65, 115, 30, "Z_B (Черево)", size=11, bold=True, fill=BG, stroke=NEG, sw=1.2))
    p.append(text(cx_b + 5, cy_b + 45, "r (курс / yaw)", size=11, color=NEG))

    p.append(fitbox(480, 385, 350, 34, "Кутова швидкість: ω = [p, q, r]^T (гіроскоп)", size=11, fill=BG, stroke=MUTED, sw=1))

    render(os.path.join(OUT, "coordinate-frames-ned-body.svg"), w, h, *p)


def fig_gimbal_lock():
    """Фігура 2: Механізм шарнірного замка (Gimbal Lock) та виродження кутів Ейлера."""
    w, h = 880, 420
    p = []

    p.append(text(w / 2, 28, "Геометрична природа шарнірного замка (Gimbal Lock) при тангажі θ = ±90°", size=16, color=INK, bold=True))

    # Ліва панель: Нормальний стан (θ = 0°)
    p.append(rect(30, 55, 390, 345, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(225, 82, "Нормальний політ (тангаж θ = 0°)", size=14, color=FIELD, bold=True))

    c1_x, c1_y = 225, 205
    p.append(circle(c1_x, c1_y, 70, fill="none", stroke=POS, sw=2.5))
    p.append(text(c1_x, c1_y - 78, "Кільце курсу (Yaw / ψ) — вісь Z", size=11, color=POS, bold=True))

    p.append(ellipse(c1_x, c1_y, 50, 30, fill="none", stroke=FIELD, sw=2.5))
    p.append(text(c1_x, c1_y - 38, "Кільце тангажу (Pitch / θ) — вісь Y", size=11, color=FIELD, bold=True))

    p.append(line(c1_x - 40, c1_y, c1_x + 40, c1_y, color=NEG, sw=3))
    p.append(text(c1_x, c1_y + 20, "Вісь крену (Roll / φ) — вісь X", size=11, color=NEG, bold=True))

    p.append(fitbox(50, 345, 350, 36, "3 незалежні осі обертання (3 ступені вільності)", size=11, bold=True, fill=BG, stroke=FIELD, sw=1.2))

    # Права панель: Шарнірний замок (θ = +90°)
    p.append(rect(460, 55, 390, 345, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(655, 82, "Шарнірний замок (тангаж θ = +90°)", size=14, color=POS, bold=True))

    c2_x, c2_y = 655, 205
    p.append(circle(c2_x, c2_y, 70, fill="none", stroke=POS, sw=2.5))
    p.append(text(c2_x, c2_y - 78, "Вісь курсу (Yaw / ψ) — вісь Z", size=11, color=POS, bold=True))

    p.append(ellipse(c2_x, c2_y, 18, 60, fill="none", stroke=FIELD, sw=2))
    p.append(text(c2_x + 72, c2_y, "Pitch θ = +90°", size=11, color=FIELD, bold=True))

    p.append(line(c2_x, c2_y - 65, c2_x, c2_y + 65, color=NEG, sw=3))
    p.append(text(c2_x - 75, c2_y + 30, "Вісь крену (Roll / φ)", size=11, color=NEG, bold=True))

    p.append(arrow(c2_x - 12, c2_y - 45, c2_x - 12, c2_y + 45, color=POS, sw=1.5))
    p.append(fitbox(480, 305, 350, 32, "Осі Roll та Yaw стали КОЛІНЕАРНИМИ!", size=11, bold=True, fill="#fee2e2", stroke=POS, sw=1.2, color=POS))
    p.append(fitbox(480, 345, 350, 36, "1 / cos(θ) → ∞  |  Втрата 1 ступеня вільності", size=11, fill=BG, stroke=POS, sw=1))

    render(os.path.join(OUT, "gimbal-lock-mechanism.svg"), w, h, *p)


def fig_state_pipeline():
    """Фігура 3: Пайплайн обробки навігаційного стану апарата у прошивці."""
    w, h = 880, 380
    p = []

    p.append(text(w / 2, 28, "Архітектура обчислення вектора стану апарата в реальному часі", size=16, color=INK, bold=True))

    # 1. Сенсорний рівень
    b1_x, b1_y, b1_w, b1_h = 30, 65, 220, 290
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(b1_x + b1_w / 2, b1_y + 24, "Первинні виміри", size=13, color=INK, bold=True))

    p.append(fitbox(b1_x + 12, b1_y + 42, b1_w - 24, 62, "IMU Гіроскоп (p, q, r)\n1000 Гц, кутова швидкість", size=11, fill=BG, stroke=MUTED, sw=1))
    p.append(fitbox(b1_x + 12, b1_y + 118, b1_w - 24, 62, "IMU Акселерометр (a_B)\n1000 Гц, питома сила", size=11, fill=BG, stroke=MUTED, sw=1))
    p.append(fitbox(b1_x + 12, b1_y + 194, b1_w - 24, 62, "GNSS / Барометр\n10-50 Гц, координати й висота", size=11, fill=BG, stroke=MUTED, sw=1))

    # Стрілки
    p.append(arrow(b1_x + b1_w, b1_y + 73, 295, b1_y + 73, color=LINE, sw=2))
    p.append(arrow(b1_x + b1_w, b1_y + 149, 295, b1_y + 149, color=LINE, sw=2))
    p.append(arrow(b1_x + b1_w, b1_y + 225, 295, b1_y + 225, color=LINE, sw=2))

    # 2. Обчислювальне ядро стану
    b2_x, b2_y, b2_w, b2_h = 295, 65, 290, 290
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(b2_x + b2_w / 2, b2_y + 24, "Оцінювач стану (EKF / Кватерніон)", size=13, color=NEG, bold=True))

    p.append(fitbox(b2_x + 12, b2_y + 42, b2_w - 24, 68, "Кінематика орієнтації (500 Гц):\nq(t + Δt) = q + 0.5·q ⊗ ω·Δt\nНормалізація: |q| = 1", size=11, fill=BG, stroke=NEG, sw=1))
    p.append(fitbox(b2_x + 12, b2_y + 118, b2_w - 24, 68, "Обертання прискорення:\na_N = q ⊗ a_B ⊗ q* - g_N", size=11, fill=BG, stroke=NEG, sw=1))
    p.append(fitbox(b2_x + 12, b2_y + 194, b2_w - 24, 68, "Інтегрування швидкості й позиції:\nv_N += a_N·Δt,  p_N += v_N·Δt", size=11, fill=BG, stroke=NEG, sw=1))

    # Стрілка
    p.append(arrow(b2_x + b2_w, b2_y + 152, 630, b2_y + 152, color=LINE, sw=2))

    # 3. Вектор стану
    b3_x, b3_y, b3_w, b3_h = 630, 65, 220, 290
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(b3_x + b3_w / 2, b3_y + 24, "Вектор стану X(t)", size=13, color=INK, bold=True))

    p.append(fitbox(b3_x + 12, b3_y + 42, b3_w - 24, 95, "Позиція: p = [N, E, D]^T\nШвидкість: v = [vN, vE, vD]^T\nКватерніон: q = [qw, qx, qy, qz]\nКутова швидкість: ω = [p, q, r]", size=11, bold=True, fill=BG, stroke=FIELD, sw=1.2))
    p.append(fitbox(b3_x + 12, b3_y + 150, b3_w - 24, 110, "Споживачі стану:\n• ПІД-регулятори кутів і кутових швидкостей\n• Навігація за точками\n• Телеметрія MAVLink", size=11, fill=BG, stroke=MUTED, sw=1))

    render(os.path.join(OUT, "state-vector-pipeline.svg"), w, h, *p)


if __name__ == "__main__":
    fig_coordinate_frames()
    fig_gimbal_lock()
    fig_state_pipeline()
    print("All figures generated successfully.")
