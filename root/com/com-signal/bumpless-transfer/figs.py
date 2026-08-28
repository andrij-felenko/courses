#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Безударне перемикання регулятора»."""

import os
import sys

# Додаємо шлях до scripts для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_shock_vs_bumpless():
    """Фігура 1: Порівняння ударного та безударного перемикання режимів."""
    w, h = 820, 430
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 24, "Перемикання з ручного режиму в автоматичний (t = 4.0 c)", size=15, bold=True))

    # Ліва колонка: Ударне перемикання (без узгодження)
    # Координатна сітка
    x0, y0, pw, ph = 60, 60, 320, 140
    frags.append(rect(x0, y0, pw, ph, fill="#fafbfc", stroke="#d1d5db", rx=4))
    frags.append(text(x0 + pw / 2, y0 - 10, "Ударне перемикання (голий ПІД)", size=13, bold=True, color=POS))

    # Осі
    frags.append(line(x0 + 20, y0 + 120, x0 + pw - 10, y0 + 120, color=MUTED, sw=1))
    frags.append(line(x0 + 20, y0 + 10, x0 + 20, y0 + 120, color=MUTED, sw=1))
    frags.append(text(x0 + pw - 10, y0 + 135, "Час t", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 + 15, y0 + 15, "u(t)", size=11, color=MUTED, anchor="end"))

    # Лінія t_sw
    t_sw_x = x0 + 130
    frags.append(line(t_sw_x, y0 + 10, t_sw_x, y0 + 120, color="#e74c3c", sw=1.2, dash="4,4"))
    frags.append(text(t_sw_x, y0 + 135, "t_sw", size=11, color=POS, anchor="middle", bold=True))

    # Сигнал керування u(t) з ударом
    # Ручний режим: u = 30% (y = y0 + 85)
    frags.append(line(x0 + 20, y0 + 85, t_sw_x, y0 + 85, color=NEG, sw=2))
    # Стрибок вгору: від 30% до 85% (y = y0 + 25)
    frags.append(line(t_sw_x, y0 + 85, t_sw_x, y0 + 25, color=POS, sw=2))
    # Перехідний процес автомата з перельотом
    path_u_shock = (
        f'<path d="M {t_sw_x} {y0 + 25} '
        f'Q {t_sw_x + 30} {y0 + 15}, {t_sw_x + 60} {y0 + 45} '
        f'T {t_sw_x + 120} {y0 + 55} '
        f'L {x0 + pw - 10} {y0 + 55}" '
        f'fill="none" stroke="{POS}" stroke-width="2"/>'
    )
    frags.append(path_u_shock)

    # Підпис стрибка Δu
    frags.append(arrow(t_sw_x + 15, y0 + 80, t_sw_x + 15, y0 + 30, color=POS, sw=1.5))
    frags.append(text(t_sw_x + 22, y0 + 55, "Стрибок Δu", size=11, color=POS, anchor="start", bold=True))

    # Графік виходу об'єкта y(t) для ударного випадку
    y0_proc = y0 + 175
    frags.append(rect(x0, y0_proc, pw, ph, fill="#fafbfc", stroke="#d1d5db", rx=4))
    frags.append(line(x0 + 20, y0_proc + 120, x0 + pw - 10, y0_proc + 120, color=MUTED, sw=1))
    frags.append(line(x0 + 20, y0_proc + 10, x0 + 20, y0_proc + 120, color=MUTED, sw=1))
    frags.append(text(x0 + pw - 10, y0_proc + 135, "Час t", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 + 15, y0_proc + 15, "y(t)", size=11, color=MUTED, anchor="end"))

    # Уставка r(t)
    frags.append(line(x0 + 20, y0_proc + 40, x0 + pw - 10, y0_proc + 40, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(x0 + pw - 15, y0_proc + 35, "Уставка r", size=10, color=MUTED, anchor="end"))

    frags.append(line(t_sw_x, y0_proc + 10, t_sw_x, y0_proc + 120, color="#e74c3c", sw=1.2, dash="4,4"))

    # Траєкторія y(t) - удар, великий переліт і коливання
    path_y_shock = (
        f'<path d="M {x0 + 20} {y0_proc + 95} '
        f'L {t_sw_x} {y0_proc + 95} '
        f'Q {t_sw_x + 25} {y0_proc + 70}, {t_sw_x + 50} {y0_proc + 20} '
        f'Q {t_sw_x + 75} {y0_proc + 60}, {t_sw_x + 100} {y0_proc + 35} '
        f'Q {t_sw_x + 125} {y0_proc + 45}, {x0 + pw - 10} {y0_proc + 40}" '
        f'fill="none" stroke="{POS}" stroke-width="2"/>'
    )
    frags.append(path_y_shock)
    frags.append(text(t_sw_x + 55, y0_proc + 15, "Переліт і коливання", size=10, color=POS, bold=True))

    # Права колонка: Безударне перемикання (Bumpless Transfer)
    x1 = 440
    frags.append(rect(x1, y0, pw, ph, fill="#fafbfc", stroke="#d1d5db", rx=4))
    frags.append(text(x1 + pw / 2, y0 - 10, "Безударне перемикання (Tracking Mode)", size=13, bold=True, color=FIELD))

    # Осі
    frags.append(line(x1 + 20, y0 + 120, x1 + pw - 10, y0 + 120, color=MUTED, sw=1))
    frags.append(line(x1 + 20, y0 + 10, x1 + 20, y0 + 120, color=MUTED, sw=1))
    frags.append(text(x1 + pw - 10, y0 + 135, "Час t", size=11, color=MUTED, anchor="end"))
    frags.append(text(x1 + 15, y0 + 15, "u(t)", size=11, color=MUTED, anchor="end"))

    frags.append(line(x1 + 130, y0 + 10, x1 + 130, y0 + 120, color=FIELD, sw=1.2, dash="4,4"))
    frags.append(text(x1 + 130, y0 + 135, "t_sw", size=11, color=FIELD, anchor="middle", bold=True))

    # Сигнал керування u(t) - гладкий без розриву
    path_u_bump = (
        f'<path d="M {x1 + 20} {y0 + 85} '
        f'L {x1 + 130} {y0 + 85} '
        f'Q {x1 + 170} {y0 + 80}, {x1 + 200} {y0 + 60} '
        f'T {x1 + pw - 10} {y0 + 55}" '
        f'fill="none" stroke="{FIELD}" stroke-width="2.2"/>'
    )
    frags.append(path_u_bump)
    frags.append(circle(x1 + 130, y0 + 85, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(x1 + 145, y0 + 95, "Гладкий стик: Δu = 0", size=11, color=FIELD, anchor="start", bold=True))

    # Графік виходу об'єкта y(t) для безударного випадку
    frags.append(rect(x1, y0_proc, pw, ph, fill="#fafbfc", stroke="#d1d5db", rx=4))
    frags.append(line(x1 + 20, y0_proc + 120, x1 + pw - 10, y0_proc + 120, color=MUTED, sw=1))
    frags.append(line(x1 + 20, y0_proc + 10, x1 + 20, y0_proc + 120, color=MUTED, sw=1))
    frags.append(text(x1 + pw - 10, y0_proc + 135, "Час t", size=11, color=MUTED, anchor="end"))
    frags.append(text(x1 + 15, y0_proc + 15, "y(t)", size=11, color=MUTED, anchor="end"))

    frags.append(line(x1 + 20, y0_proc + 40, x1 + pw - 10, y0_proc + 40, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(x1 + pw - 15, y0_proc + 35, "Уставка r", size=10, color=MUTED, anchor="end"))
    frags.append(line(x1 + 130, y0_proc + 10, x1 + 130, y0_proc + 120, color=FIELD, sw=1.2, dash="4,4"))

    # Траєкторія y(t) - монотонний плавний дохід до уставки
    path_y_bump = (
        f'<path d="M {x1 + 20} {y0_proc + 95} '
        f'L {x1 + 130} {y0_proc + 95} '
        f'Q {x1 + 180} {y0_proc + 90}, {x1 + 220} {y0_proc + 55} '
        f'T {x1 + pw - 10} {y0_proc + 40}" '
        f'fill="none" stroke="{FIELD}" stroke-width="2.2"/>'
    )
    frags.append(path_y_bump)
    frags.append(text(x1 + 210, y0_proc + 25, "Плавний аперіодичний вихід", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "shock-vs-bumpless.svg"), w, h, *frags)


def fig_integrator_tracking():
    """Фігура 2: Структурна схема алгоритму узгодження інтегратора (Tracking Mode)."""
    w, h = 820, 370
    frags = []

    frags.append(text(w / 2, 24, "Структура безударного ПІД з контуром зворотного стеження (Tracking Mode)", size=15, bold=True))

    # Вхід уставки r і виміру y
    frags.append(text(35, 90, "r[k]", size=13, bold=True))
    frags.append(arrow(55, 90, 85, 90, color=LINE, sw=1.8))

    # Суматор помилки
    frags.append(circle(95, 90, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(95, 87, "+", size=10, bold=True))
    frags.append(text(95, 107, "−", size=12, bold=True))

    # Лінія виміру y
    frags.append(line(95, 140, 95, 100, color=LINE, sw=1.8))
    frags.append(line(35, 140, 95, 140, color=LINE, sw=1.8))
    frags.append(text(35, 135, "y[k]", size=13, bold=True))

    # Помилка e[k]
    frags.append(arrow(105, 90, 150, 90, color=LINE, sw=1.8))
    frags.append(text(125, 80, "e[k]", size=12, italic=True))

    # Розгалуження на P, I, D
    frags.append(circle(150, 90, 3, fill=LINE, stroke=LINE))
    frags.append(line(150, 45, 150, 135, color=LINE, sw=1.8))

    # Блок P
    frags.append(arrow(150, 45, 185, 45, color=LINE, sw=1.8))
    b_p, _, _ = textbox(225, 45, "Пропорційна\nKp · e[k]", size=12, pad=6, fill="#f8fafc", stroke=LINE)
    frags.append(b_p)

    # Блок I (з інтегратором і входом узгодження)
    frags.append(arrow(150, 90, 185, 90, color=LINE, sw=1.8))

    # Суматор всередині I-ланцюга для tracking
    frags.append(circle(195, 90, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(195, 87, "+", size=10, bold=True))
    frags.append(text(195, 107, "+", size=10, bold=True))

    frags.append(arrow(205, 90, 240, 90, color=LINE, sw=1.8))
    b_i, _, _ = textbox(295, 90, "Інтегратор I\nI[k] = I[k-1] + ΔI", size=12, pad=6, fill="#eef2ff", stroke=NEG)
    frags.append(b_i)

    # Блок D (від виміру)
    frags.append(arrow(150, 135, 185, 135, color=LINE, sw=1.8))
    b_d, _, _ = textbox(225, 135, "Диференційна\n−Kd · Δy/Δt", size=12, pad=6, fill="#f8fafc", stroke=LINE)
    frags.append(b_d)

    # Суматор PID: u_calc
    frags.append(line(265, 45, 380, 45, color=LINE, sw=1.8))
    frags.append(line(350, 90, 380, 90, color=LINE, sw=1.8))
    frags.append(line(265, 135, 380, 135, color=LINE, sw=1.8))

    frags.append(line(380, 45, 380, 80, color=LINE, sw=1.8))
    frags.append(line(380, 135, 380, 100, color=LINE, sw=1.8))

    frags.append(circle(380, 90, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(380, 80, "+", size=9, bold=True))
    frags.append(text(372, 90, "+", size=9, bold=True))
    frags.append(text(380, 100, "+", size=9, bold=True))

    frags.append(arrow(390, 90, 440, 90, color=LINE, sw=1.8))
    frags.append(text(415, 80, "u_calc", size=11, bold=True))

    # Перемикач режимів (Manual / Auto)
    sw_box = rect(440, 50, 120, 90, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6)
    frags.append(sw_box)
    frags.append(text(500, 68, "Перемикач", size=12, bold=True))

    # Контакти перемикача
    frags.append(circle(460, 90, 3, fill=LINE, stroke=LINE))
    frags.append(circle(460, 120, 3, fill=LINE, stroke=LINE))
    frags.append(circle(535, 100, 3, fill=LINE, stroke=LINE))
    frags.append(line(460, 90, 532, 98, color=FIELD, sw=2.5))  # Положення Auto
    frags.append(text(480, 84, "Auto", size=10, color=FIELD, bold=True))
    frags.append(text(480, 132, "Manual", size=10, color=MUTED))

    # Вхід ручного керування u_man
    frags.append(arrow(410, 120, 460, 120, color=MUTED, sw=1.8))
    frags.append(text(380, 125, "u_man", size=11, color=MUTED))

    # Вихід на виконавчий орган u_act
    frags.append(arrow(535, 100, 600, 100, color=LINE, sw=2))
    b_sat, _, _ = textbox(660, 100, "Обмежувач (Sat)\n[u_min ... u_max]", size=12, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(b_sat)

    frags.append(arrow(725, 100, 785, 100, color=LINE, sw=2))
    frags.append(text(760, 90, "u_act[k]", size=12, bold=True))

    # Зворотний зв'язок узгодження (Tracking Loop)
    frags.append(circle(755, 100, 3, fill=LINE, stroke=LINE))
    frags.append(line(755, 100, 755, 230, color=FIELD, sw=1.8))
    frags.append(line(755, 230, 540, 230, color=FIELD, sw=1.8))

    # Також беремо u_calc
    frags.append(circle(415, 90, 3, fill=LINE, stroke=LINE))
    frags.append(line(415, 90, 415, 210, color=POS, sw=1.5))
    frags.append(line(415, 210, 540, 210, color=POS, sw=1.5))

    # Суматор неузгодженості виходів: e_trk = u_act - u_calc
    frags.append(circle(540, 220, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(540, 233, "+", size=10, bold=True, color=FIELD))
    frags.append(text(540, 213, "−", size=12, bold=True, color=POS))

    # Підпис неузгодженості
    frags.append(arrow(530, 220, 450, 220, color=FIELD, sw=1.8))
    frags.append(text(490, 208, "e_trk = u_act − u_calc", size=11, color=FIELD, bold=True))

    # Коефіцієнт стеження Kt = 1 / Tt
    b_kt, _, _ = textbox(360, 220, "Підсилювач узгодження\nKt = 1 / Tt", size=12, pad=6, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_kt)

    # Замикання контуру в інтегратор
    frags.append(line(275, 220, 195, 220, color=FIELD, sw=1.8))
    frags.append(arrow(195, 220, 195, 100, color=FIELD, sw=1.8))
    frags.append(text(125, 205, "Поправка ΔI_trk = Kt·e_trk·Δt", size=11, color=FIELD, bold=True))

    # Пояснювальний блок знизу
    b_desc, _, _ = textbox(w / 2, 315,
        "У ручному режимі (Manual) або при насиченні (Sat) контур узгодження автоматично коригує інтегратор,\n"
        "підтримуючи u_calc = u_act. У момент перемикання стрибок відсутній (Δu = 0).",
        size=11, pad=8, fill="#f8fafc", stroke="#94a3b8")
    frags.append(b_desc)

    render(os.path.join(IMG_DIR, "integrator-tracking.svg"), w, h, *frags)


def fig_gain_scheduling_bump():
    """Фігура 3: Механізм стрибка при зміні Gain Scheduling та його компенсація."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 24, "Стрибок сигналу при зміні коефіцієнтів (Gain Scheduling) та інтегральна компенсація", size=15, bold=True))

    # Лівий блок: Проблема в позиційній формі
    x0, y0, bw, bh = 50, 55, 335, 260
    frags.append(rect(x0, y0, bw, bh, fill="#fff5f5", stroke="#feb2b2", rx=6))
    frags.append(text(x0 + bw / 2, y0 + 22, "1. Позиційна форма без компенсації", size=13, bold=True, color=POS))

    # Формула
    frags.append(rect(x0 + 15, y0 + 40, bw - 30, 45, fill="#fff", stroke="#fca5a5", rx=4))
    frags.append(text(x0 + bw / 2, y0 + 67, "u[k] = Kp(t) · e[k] + I[k]", size=12, bold=True))

    # Схема стрибка
    # Графік Kp
    gx = x0 + 30
    frags.append(line(gx, y0 + 135, gx + 120, y0 + 135, color=MUTED, sw=1.5))
    frags.append(line(gx + 120, y0 + 135, gx + 120, y0 + 105, color=POS, sw=1.8))
    frags.append(line(gx + 120, y0 + 105, gx + 270, y0 + 105, color=MUTED, sw=1.5))
    frags.append(text(gx + 50, y0 + 150, "Kp_1 = 1.0", size=10, color=MUTED))
    frags.append(text(gx + 200, y0 + 95, "Kp_2 = 2.5", size=10, color=POS, bold=True))

    # Графік виходу u[k]
    frags.append(line(gx, y0 + 215, gx + 120, y0 + 215, color=NEG, sw=2))
    frags.append(line(gx + 120, y0 + 215, gx + 120, y0 + 175, color=POS, sw=2))
    frags.append(line(gx + 120, y0 + 175, gx + 270, y0 + 175, color=POS, sw=2))

    frags.append(arrow(gx + 130, y0 + 210, gx + 130, y0 + 180, color=POS, sw=1.5))
    frags.append(text(gx + 140, y0 + 198, "Δu = (Kp2 − Kp1) · e", size=11, color=POS, bold=True))

    frags.append(text(x0 + bw / 2, y0 + 245, "⚠ Стрибок пропорційної складової б'є по приводу", size=11, color=POS, bold=True))

    # Правий блок: Рішення з компенсацією інтегратора
    x1 = 435
    frags.append(rect(x1, y0, bw, bh, fill="#f0fdf4", stroke="#86efac", rx=6))
    frags.append(text(x1 + bw / 2, y0 + 22, "2. Компенсоване перемикання або інкрементна форма", size=13, bold=True, color=FIELD))

    # Формула компенсації
    frags.append(rect(x1 + 15, y0 + 40, bw - 30, 45, fill="#fff", stroke="#86efac", rx=4))
    frags.append(text(x1 + bw / 2, y0 + 67, "I_new = I_old − (Kp_new − Kp_old) · e[k]", size=12, bold=True, color=FIELD))

    # Графіки Kp, I та u
    gx1 = x1 + 30
    frags.append(line(gx1, y0 + 120, gx1 + 120, y0 + 120, color=MUTED, sw=1.5))
    frags.append(line(gx1 + 120, y0 + 120, gx1 + 120, y0 + 95, color=FIELD, sw=1.8))
    frags.append(line(gx1 + 120, y0 + 95, gx1 + 270, y0 + 95, color=MUTED, sw=1.5))
    frags.append(text(gx1 + 200, y0 + 88, "Kp зростає (+ΔKp)", size=10, color=FIELD))

    # Графік I
    frags.append(line(gx1, y0 + 155, gx1 + 120, y0 + 155, color="#6366f1", sw=1.5))
    frags.append(line(gx1 + 120, y0 + 155, gx1 + 120, y0 + 180, color="#6366f1", sw=1.8))
    frags.append(line(gx1 + 120, y0 + 180, gx1 + 270, y0 + 180, color="#6366f1", sw=1.5))
    frags.append(text(gx1 + 200, y0 + 172, "I компенсує (−ΔKp·e)", size=10, color="#6366f1"))

    # Графік суми u[k]
    frags.append(line(gx1, y0 + 215, gx1 + 270, y0 + 215, color=FIELD, sw=2.5))
    frags.append(circle(gx1 + 120, y0 + 215, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(gx1 + 130, y0 + 205, "Сума u[k] неперервна (Δu = 0)", size=11, color=FIELD, bold=True))

    frags.append(text(x1 + bw / 2, y0 + 245, "✓ Зміна коефіцієнтів змінює лише динаміку, без стрибка", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "gain-scheduling-bump.svg"), w, h, *frags)


def fig_two_dof_setpoint():
    """Фігура 4: Двоступеневий регулятор (2-DoF PID) та профілювання уставки (Setpoint Ramping)."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 24, "Структура 2-DoF регулятора з профілюванням уставки (Setpoint Ramping)", size=15, bold=True))

    # Вхід уставки r_raw
    frags.append(text(30, 85, "Уставка\nr_raw(t)", size=12, bold=True, anchor="middle"))
    frags.append(arrow(60, 85, 95, 85, color=LINE, sw=1.8))

    # Блок Setpoint Ramping / Slew rate
    b_ramp, _, _ = textbox(165, 85, "Профілювач уставки\n|dr/dt| ≤ v_max (S-curve)", size=12, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(b_ramp)

    frags.append(arrow(240, 85, 290, 85, color=LINE, sw=1.8))
    frags.append(text(265, 75, "r_f(t)", size=12, bold=True, color="#d97706"))

    # Розгалуження r_f на P-вагу (b), I-суматор
    frags.append(circle(290, 85, 3, fill=LINE, stroke=LINE))
    frags.append(line(290, 45, 290, 130, color=LINE, sw=1.8))

    # Ланцюг P: b · r_f − y
    frags.append(arrow(290, 45, 330, 45, color=LINE, sw=1.8))
    b_b, _, _ = textbox(365, 45, "Вага уставки\nb · r_f", size=11, pad=5, fill="#f1f5f9", stroke=LINE)
    frags.append(b_b)

    frags.append(arrow(405, 45, 435, 45, color=LINE, sw=1.8))
    frags.append(circle(445, 45, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(445, 42, "+", size=9, bold=True))
    frags.append(text(445, 57, "−", size=11, bold=True))

    frags.append(arrow(455, 45, 490, 45, color=LINE, sw=1.8))
    b_kp, _, _ = textbox(530, 45, "Kp · (b·r − y)", size=12, pad=6, fill="#f8fafc", stroke=LINE)
    frags.append(b_kp)

    # Ланцюг I: r_f − y
    frags.append(arrow(290, 130, 435, 130, color=LINE, sw=1.8))
    frags.append(circle(445, 130, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(445, 127, "+", size=9, bold=True))
    frags.append(text(445, 142, "−", size=11, bold=True))

    frags.append(arrow(455, 130, 490, 130, color=LINE, sw=1.8))
    b_ki, _, _ = textbox(540, 130, "Ki · ∫ (r − y) dt", size=12, pad=6, fill="#eef2ff", stroke=NEG)
    frags.append(b_ki)

    # Ланцюг D: лише від виміру y
    b_kd, _, _ = textbox(540, 205, "−Kd · (dy/dt) / (1 + τ·s)", size=12, pad=6, fill="#f8fafc", stroke=LINE)
    frags.append(b_kd)

    # Вхід вимірюваної величини y(t)
    frags.append(text(30, 260, "Вимір давача\ny(t)", size=12, bold=True, anchor="middle"))
    frags.append(line(70, 260, 445, 260, color=LINE, sw=1.8))
    frags.append(circle(445, 260, 3, fill=LINE, stroke=LINE))

    # Зв'язок y з суматором P
    frags.append(line(445, 260, 445, 55, color=LINE, sw=1.8))

    # Зв'язок y з суматором I
    frags.append(line(445, 260, 445, 140, color=LINE, sw=1.8))

    # Зв'язок y з блоком D
    frags.append(line(445, 205, 480, 205, color=LINE, sw=1.8))
    frags.append(arrow(480, 205, 490, 205, color=LINE, sw=1.8))

    # Головний суматор виходу u(t)
    frags.append(line(575, 45, 660, 45, color=LINE, sw=1.8))
    frags.append(line(595, 130, 660, 130, color=LINE, sw=1.8))
    frags.append(line(600, 205, 660, 205, color=LINE, sw=1.8))

    frags.append(line(660, 45, 660, 120, color=LINE, sw=1.8))
    frags.append(line(660, 205, 660, 140, color=LINE, sw=1.8))

    frags.append(circle(660, 130, 10, fill="#fff", stroke=LINE, sw=1.8))
    frags.append(text(660, 120, "+", size=9, bold=True))
    frags.append(text(652, 130, "+", size=9, bold=True))
    frags.append(text(660, 140, "+", size=9, bold=True))

    frags.append(arrow(670, 130, 740, 130, color=LINE, sw=2))
    frags.append(text(750, 120, "Керування\nu(t)", size=12, bold=True))

    # Пояснення знизу
    b_foot, _, _ = textbox(w / 2, 310,
        "Два ступені свободи (2-DoF): за уставки b = 0 пропорційна складова не смикає привід при стрибку r(t),\n"
        "диференційна складова D береться суто від швидкості зміни виходу (-dy/dt), а темп наростання задає Ramping-фільтр.",
        size=11, pad=8, fill="#f8fafc", stroke="#94a3b8")
    frags.append(b_foot)

    render(os.path.join(IMG_DIR, "two-dof-setpoint-ramping.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_shock_vs_bumpless()
    fig_integrator_tracking()
    fig_gain_scheduling_bump()
    fig_two_dof_setpoint()
    print("Всі 4 фігури успішно згенеровано!")
