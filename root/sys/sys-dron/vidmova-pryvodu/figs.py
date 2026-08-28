#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми vidmova-pryvodu (sys-dron).
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


def fig_fault_detection_pipeline():
    """Фігура 1: Конвеєр детектування, ізоляції відмов приводів (FDI) та реконфігурації матриці."""
    w, h = 880, 430
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок зверху
    elements.append(text(440, 28, "Архітектура відмовостійкого керування приводами (FDI + Dynamic Allocation)",
                         size=14, color=INK, bold=True))

    # 1. Блок: Бажані моменти та сили (τ_des)
    b_cmd, _, _ = textbox(110, 105, "Контури керування\n(PID положення/швидкості)\nτ_des = [F_z, M_x, M_y, M_z]ᵀ",
                          size=11, pad=8, fill=FILL, stroke=LINE, min_w=160)
    elements.append(b_cmd)

    # Стрілка 1 -> Алокатор
    elements.append(arrow(195, 105, 255, 105, color=LINE, sw=1.6))
    elements.append(text(225, 92, "τ_des", size=11, color=INK, bold=True))

    # 2. Блок: Динамічний алокатор мікшування
    b_alloc = rect(260, 55, 230, 100, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6)
    elements.append(b_alloc)
    elements.append(text(375, 80, "Динамічний алокатор", size=12, color=INK, bold=True))
    elements.append(text(375, 102, "u = B_deg⁺ · τ_des", size=11, color=INK, bold=True))
    elements.append(text(375, 124, "Реконфігурація матриці B", size=10, color=MUTED))
    elements.append(text(375, 142, "та пріоритетна десатурація", size=10, color=MUTED))

    # Стрілка Алокатор -> Фізичні приводи
    elements.append(arrow(495, 105, 565, 105, color=LINE, sw=1.6))
    elements.append(text(530, 92, "u ∈ [0, 1]", size=11, color=INK, bold=True))

    # 3. Блок: Фізичні приводи та планер
    b_act = rect(570, 55, 280, 100, fill=FILL, stroke=LINE, sw=1.6, rx=6)
    elements.append(b_act)
    elements.append(text(710, 78, "Фізичні приводи та планер", size=12, color=INK, bold=True))
    elements.append(text(710, 100, "ESC / Мотори 1..m + Сервоприводи", size=11, color=INK))
    elements.append(text(710, 122, "Можлива відмова: обрив фази, клин серво,", size=10, color="#b91c1c"))
    elements.append(text(710, 140, "зріз редуктора, втрата лопаті", size=10, color="#b91c1c"))

    # Стрілка від приводів вниз до сенсорів
    elements.append(arrow(680, 158, 680, 218, color=LINE, sw=1.6))
    elements.append(text(695, 190, "Тяга, моменти", size=10, color=MUTED, anchor="start"))

    # 4. Блок сенсорів зворотного зв'язку
    b_sens = rect(570, 222, 280, 96, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6)
    elements.append(b_sens)
    elements.append(text(710, 242, "Сенсори та телеметрія", size=12, color=INK, bold=True))
    elements.append(text(710, 265, "• DShot Telemetry (eRPM, I_esc, T_esc)", size=10, color=INK))
    elements.append(text(710, 285, "• IMU Гіроскопи (кутова швидкість ω)", size=10, color=INK))
    elements.append(text(710, 303, "• Інтегральні помилки PID (I-term)", size=10, color=INK))

    # Стрілка від Сенсорів вліво до FDI блоку
    elements.append(arrow(565, 270, 495, 270, color=LINE, sw=1.6))
    elements.append(text(530, 258, "ω, RPM, e(t)", size=10, color=INK, bold=True))

    # 5. Блок FDI (Fault Detection & Isolation)
    b_fdi = rect(140, 210, 350, 120, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6)
    elements.append(b_fdi)
    elements.append(text(315, 232, "Детектування та ізоляція відмов (FDI)", size=12, color="#92400e", bold=True))
    elements.append(text(315, 254, "1. Спостерігач: r(t) = ω̇_meas - J⁻¹(τ_cmd - ω × Jω)", size=10, color=INK))
    elements.append(text(315, 274, "2. DShot eRPM / PWM неузгодженість (ΔRPM > th)", size=10, color=INK))
    elements.append(text(315, 294, "3. Насичення інтегратора I-term при нульовому відгуку", size=10, color=INK))
    elements.append(text(315, 314, "4. Ізоляція відмови: індекс несправного привода k", size=10, color="#b45309", bold=True))

    # Стрілка від FDI вгору до Алокатора (сигнал реконфігурації)
    elements.append(arrow(315, 205, 315, 160, color="#dc2626", sw=2.0))
    elements.append(text(330, 185, "Fault Mask (k)", size=10, color="#dc2626", bold=True, anchor="start"))

    # Пояснювальний підпис унизу
    elements.append(text(440, 375, "Контур замкнено: залишковий сигнал незв'язки r(t) та телеметрія ESC виявляють відмову k-го привода,",
                         size=11, color=MUTED))
    elements.append(text(440, 395, "після чого алокатор миттєво обнуляє стовпець b_k у матриці B та перераховує псевдообернену матрицю B_deg⁺.",
                         size=11, color=MUTED))

    # Збірка SVG
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'fault-detection-isolation-pipeline.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_hexacopter_motor_loss():
    """Фігура 2: Геометрія гексакоптера при втраті одного мотора та компенсація моментів."""
    w, h = 880, 440
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок
    elements.append(text(440, 28, "Геометрія сил та моментів гексакоптера при відмові мотора №1",
                         size=14, color=INK, bold=True))

    # Центр гексакоптера
    cx, cy = 240, 225
    r_arm = 125
    r_hub = 30
    r_motor = 28

    # Корпус / промені гексакоптера
    elements.append(circle(cx, cy, r_hub, fill="#e2e8f0", stroke=LINE, sw=1.8))
    elements.append(text(cx, cy + 4, "Центр мас", size=10, color=INK, bold=True))

    # 6 моторів (кути: 0, 60, 120, 180, 240, 300 град)
    angles_deg = [0, 60, 120, 180, 240, 300]
    cw_dirs = [-1, 1, -1, 1, -1, 1]  # CW / CCW

    for i, deg in enumerate(angles_deg):
        rad = math.radians(deg)
        mx = cx + r_arm * math.cos(rad)
        my = cy + r_arm * math.sin(rad)

        # Промінь малюємо ВІД краю центрального хаба ДО краю моторної платформи
        p1_x = cx + r_hub * math.cos(rad)
        p1_y = cy + r_hub * math.sin(rad)
        p2_x = cx + (r_arm - r_motor) * math.cos(rad)
        p2_y = cy + (r_arm - r_motor) * math.sin(rad)

        elements.append(line(p1_x, p1_y, p2_x, p2_y, color=LINE, sw=2.0))

        if i == 0:  # Відмовий мотор №1
            elements.append(circle(mx, my, r_motor, fill="#fee2e2", stroke="#dc2626", sw=2.2))
            elements.append(text(mx, my - 6, "M1 (ВІДМОВА)", size=9, color="#dc2626", bold=True))
            elements.append(text(mx, my + 8, "F₁ = 0 Н", size=10, color="#dc2626"))
        else:
            # Справні мотори
            elements.append(circle(mx, my, r_motor, fill="#ecfdf5", stroke="#059669", sw=1.8))
            rot_txt = "CW" if cw_dirs[i] == 1 else "CCW"
            elements.append(text(mx, my - 6, f"M{i+1} ({rot_txt})", size=9, color=INK, bold=True))
            elements.append(text(mx, my + 8, f"F_{i+1} ↑", size=10, color="#059669"))

    # Права частина: аналітична панель балансу моментів
    panel_x, panel_y, panel_w, panel_h = 490, 60, 360, 310
    elements.append(rect(panel_x, panel_y, panel_w, panel_h, fill="#f8fafc", stroke=LINE, sw=1.6, rx=8))
    elements.append(text(panel_x + 180, panel_y + 25, "Аналіз керованості на 5 моторах", size=12, color=INK, bold=True))

    # Рядки аналізу
    elements.append(text(panel_x + 20, panel_y + 60, "1. Крен (Roll, M_x):", size=11, color=INK, bold=True, anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 80, "Парирується асиметрією тяги моторів 2, 3 та 5, 6.", size=10, color=MUTED, anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 98, "Баланс M_x = 0 досягається повністю.", size=10, color="#059669", anchor="start"))

    elements.append(text(panel_x + 20, panel_y + 130, "2. Тангаж (Pitch, M_y):", size=11, color=INK, bold=True, anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 150, "Протилежний мотор M4 (180°) зменшує тягу,", size=10, color=MUTED, anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 168, "щоб компенсувати плече тяги M1. Баланс M_y = 0.", size=10, color="#059669", anchor="start"))

    elements.append(text(panel_x + 20, panel_y + 200, "3. Рискання (Yaw, M_z) — головний дефіцит:", size=11, color=INK, bold=True, anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 220, "Сумарний реактивний момент гвинтів ≠ 0.", size=10, color="#b91c1c", anchor="start"))
    elements.append(text(panel_x + 35, panel_y + 238, "Неможливо утримати курс без втрати висоти.", size=10, color="#b91c1c", anchor="start"))

    # Підсумок стратегії
    b_strat = rect(panel_x + 15, panel_y + 252, panel_w - 30, 46, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4)
    elements.append(b_strat)
    elements.append(text(panel_x + 180, panel_y + 270, "Стратегія: авторотація / релаксація Yaw", size=10, color="#92400e", bold=True))
    elements.append(text(panel_x + 180, panel_y + 288, "Дрон швидко крутиться навколо Z, але керовано сідає", size=9.5, color="#92400e"))

    # Пояснення знизу
    elements.append(text(440, 400, "Втрата тяги мотора M1 вимагає зменшення тяги мотора M4 та перерозподілу сил бічних моторів.",
                         size=11, color=MUTED))
    elements.append(text(440, 418, "Незбалансований реактивний момент перетворюється на контрольоване обертання по рисканню (Yaw relaxation).",
                         size=11, color=MUTED))

    # Збірка SVG
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'hexacopter-motor-loss-geometry.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_fault_detection_pipeline()
    fig_hexacopter_motor_loss()
