#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Перемикачі й розкладка пульта».
Вивід у ./img/. Запуск: python figs.py
"""

import sys
import os
import math

# Підключення svgkit із кореня репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

def gen_stick_modes():
    """Фігура 1: stick-modes-comparison.svg — Порівняння чотирьох розкладок стіків (Mode 1, 2, 3, 4)."""
    w, h = 900, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Розподіл осей керування між стіками: Mode 1, 2, 3 та 4", size=16, bold=True))

    modes = [
        ("Mode 1 (Класичний літак / Європа)", 30, 60, 400, 185, [
            ("Лівий стік", "Тангаж (Pitch)", "Рискання (Yaw)", False),
            ("Правий стік", "Газ (Throttle)", "Крен (Roll)", True)
        ], "#fafbfc", LINE),
        ("Mode 2 (Світовий стандарт / Дрони)", 470, 60, 400, 185, [
            ("Лівий стік", "Газ (Throttle)", "Рискання (Yaw)", True),
            ("Правий стік", "Тангаж (Pitch)", "Крен (Roll)", False)
        ], "#f0fdf4", FIELD),
        ("Mode 3 (Дзеркальний Mode 2 / Лівша)", 30, 265, 400, 185, [
            ("Лівий стік", "Тангаж (Pitch)", "Крен (Roll)", False),
            ("Правий стік", "Газ (Throttle)", "Рискання (Yaw)", True)
        ], "#fafbfc", LINE),
        ("Mode 4 (Дзеркальний Mode 1)", 470, 265, 400, 185, [
            ("Лівий стік", "Газ (Throttle)", "Крен (Roll)", True),
            ("Правий стік", "Тангаж (Pitch)", "Рискання (Yaw)", False)
        ], "#fafbfc", LINE),
    ]

    for title_m, px, py, pw, ph, gimbals, bg_col, stroke_col in modes:
        # Рамка режиму
        sw_val = 2.0 if stroke_col == FIELD else 1.2
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=stroke_col, sw=sw_val, rx=8))
        frags.append(text(px + pw / 2, py + 22, title_m, size=13, bold=True, color=stroke_col if stroke_col == FIELD else INK))

        # Два стіки
        for idx, (g_name, v_axis, h_axis, is_throttle) in enumerate(gimbals):
            gx = px + 105 if idx == 0 else px + 295
            gy = py + 105

            # Корпус стіка (коло)
            frags.append(circle(gx, gy, 42, fill="#ffffff", stroke="#cbd5e1", sw=1.5))
            # Вісь X та Y (хрестовина)
            frags.append(line(gx - 40, gy, gx + 40, gy, color="#94a3b8", sw=1, dash="2,2"))
            frags.append(line(gx, gy - 40, gx, gy + 40, color="#94a3b8", sw=1, dash="2,2"))
            # Центральна ручка
            frags.append(circle(gx, gy, 8, fill=POS if is_throttle else NEG, stroke="#1e293b", sw=1.5))

            # Стрілки осей
            frags.append(arrow(gx, gy - 16, gx, gy - 36, color=POS if is_throttle else NEG, sw=1.5))
            frags.append(arrow(gx + 16, gy, gx + 36, gy, color=INK, sw=1.5))

            # Підписи стіка
            frags.append(text(gx, gy - 50, g_name, size=11, bold=True, color=MUTED))
            frags.append(text(gx, gy + 56, v_axis, size=11, bold=True, color=POS if is_throttle else NEG))
            frags.append(text(gx, gy + 70, h_axis, size=10, color=INK))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "stick-modes-comparison.svg")
    render(out_path, w, h, *frags)
    print(f"Generated: {out_path}")

def gen_resistor_ladder():
    """Фігура 2: resistor-ladder-switch.svg — Схема 6-позиційного перемикача та декодування в польотному контролері."""
    w, h = 880, 450
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Апаратний резистивний подільник та програмні вікна 6-позиційного перемикача", size=16, bold=True))

    # Ліва частина: Електрична схема дільника напруги
    frags.append(rect(20, 50, 360, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(200, 74, "Схема 6-позиційного селектора (VCC = 3.3V)", size=13, bold=True, color=INK))

    # Шина VCC зверху
    frags.append(line(80, 100, 140, 100, color=POS, sw=2))
    frags.append(text(70, 104, "3.3V", size=11, bold=True, color=POS, anchor="end"))

    # Послідовні резистори R1..R6
    r_y_start = 100
    res_height = 42
    res_names = ["R1 = 2.4k", "R2 = 1.0k", "R3 = 1.0k", "R4 = 1.0k", "R5 = 1.0k", "R6 = 3.3k"]
    taps = []

    for i in range(6):
        ry = r_y_start + i * res_height
        # Провідник між резисторами
        frags.append(line(110, ry, 110, ry + 10, color=LINE, sw=1.5))
        # Резистор прямокутник
        frags.append(rect(98, ry + 10, 24, 22, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
        frags.append(text(130, ry + 25, res_names[i], size=10, color=MUTED, anchor="start"))
        taps.append(ry + 10)

    # Шина GND знизу
    gnd_y = r_y_start + 6 * res_height
    frags.append(line(110, gnd_y - 10, 110, gnd_y, color=LINE, sw=1.5))
    frags.append(line(90, gnd_y, 130, gnd_y, color=LINE, sw=2))
    frags.append(line(96, gnd_y + 4, 124, gnd_y + 4, color=LINE, sw=1.5))
    frags.append(line(103, gnd_y + 8, 117, gnd_y + 8, color=LINE, sw=1))
    frags.append(text(140, gnd_y + 6, "GND", size=11, bold=True, color=MUTED, anchor="start"))

    # Відводи до поворотного перемикача
    sw_center_x, sw_center_y = 270, 225
    frags.append(circle(sw_center_x, sw_center_y, 45, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(text(sw_center_x, sw_center_y - 55, "Поворотний контакт (AUX)", size=11, bold=True, color=INK))

    angles = [-50, -30, -10, 10, 30, 50]
    for i in range(6):
        ry = taps[i]
        # Лінія від резистора вбік
        frags.append(line(122, ry + 11, 190, ry + 11, color="#64748b", sw=1.2))
        # Точка на перемикачі
        rad = math.radians(180 + angles[i])
        kx = sw_center_x + 35 * math.cos(rad)
        ky = sw_center_y + 35 * math.sin(rad)
        frags.append(circle(kx, ky, 3.5, fill=NEG, stroke=LINE, sw=1))
        frags.append(line(190, ry + 11, kx, ky, color="#64748b", sw=1.2))

    # Важіль селектора на позицію 3
    sel_rad = math.radians(180 - 10)
    frags.append(line(sw_center_x, sw_center_y, sw_center_x + 35 * math.cos(sel_rad), sw_center_y + 35 * math.sin(sel_rad), color=POS, sw=2.5))
    frags.append(circle(sw_center_x, sw_center_y, 6, fill=POS, stroke=LINE, sw=1.5))

    # Вихід на АЦП
    frags.append(arrow(sw_center_x, sw_center_y, 340, sw_center_y, color=POS, sw=2))
    frags.append(text(330, sw_center_y - 12, "U_out -> ADC", size=10, bold=True, color=POS))

    # Права частина: Шкала ШІМ / CRSF імпульсів та вікна декодування в ПК
    frags.append(rect(400, 50, 460, 380, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(630, 74, "Вікна декодування режимів польоту (ArduPilot / PX4)", size=13, bold=True, color=INK))

    # 6 смуг режимів
    mode_boxes = [
        (1, "Поз. 1 (1165 мкс)", "STABILIZE / MANUAL", 988, 1230, "#e0f2fe", "#0284c7"),
        (2, "Поз. 2 (1295 мкс)", "ALT_HOLD (Утримання висоти)", 1231, 1360, "#dcfce7", "#16a34a"),
        (3, "Поз. 3 (1425 мкс)", "LOITER / POSHOLD (Точка GNSS)", 1361, 1490, "#fef9c3", "#ca8a04"),
        (4, "Поз. 4 (1555 мкс)", "AUTO (Політ за місією)", 1491, 1620, "#ffedd5", "#ea580c"),
        (5, "Поз. 5 (1685 мкс)", "RTL (Повернення додому)", 1621, 1749, "#fee2e2", "#dc2626"),
        (6, "Поз. 6 (1815 мкс)", "LAND (Автопосадка)", 1750, 2012, "#f3e8ff", "#9333ea"),
    ]

    for idx, (p_num, p_val, m_name, w_min, w_max, b_bg, b_strk) in enumerate(mode_boxes):
        by = 96 + idx * 46
        frags.append(rect(415, by, 430, 38, fill=b_bg, stroke=b_strk, sw=1.2, rx=4))
        # Лівий ярлик
        frags.append(text(425, by + 23, p_val, size=11, bold=True, color=b_strk, anchor="start"))
        # Назва режиму
        frags.append(text(585, by + 23, m_name, size=11, bold=True, color=INK, anchor="start"))
        # Межі вікна
        frags.append(text(835, by + 23, f"[{w_min}..{w_max}]", size=10, color=MUTED, anchor="end"))

    # Пояснення про ширину вікна (простий текст без вкладеної рамки)
    frags.append(text(630, 395, "Ширина вікна ~130 мкс забезпечує запас ±65 мкс від дрейфу", size=11, color=MUTED, bold=True))
    frags.append(text(630, 412, "міжпорожні мертві зони запобігають тремтінню на межах", size=10, color=MUTED))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "resistor-ladder-switch.svg")
    render(out_path, w, h, *frags)
    print(f"Generated: {out_path}")

def gen_transmitter_layout():
    """Фігура 3: transmitter-safety-ergonomics.svg — Ергономіка розміщення перемикачів на пульті."""
    w, h = 900, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Безпечна архітектура перемикачів польового пульта керування", size=16, bold=True))

    # Зона верхніх перемикачів (окремо зверху, не накладається на корпус)
    # Перемикачі зверху зліва: ARM та PRE-ARM
    # 1. ARM SWITCH (SA) - 2-pos toggle
    sa_x, sa_y = 160, 48
    frags.append(rect(sa_x - 45, sa_y, 90, 46, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(sa_x, sa_y + 18, "SA (2-поз)", size=10, bold=True, color=POS))
    frags.append(text(sa_x, sa_y + 34, "ARM / DISARM", size=9, bold=True, color=POS))

    # 2. PRE-ARM (SB) - Кнопка без фіксації / плече
    sb_x, sb_y = 280, 48
    frags.append(rect(sb_x - 45, sb_y, 90, 46, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(sb_x, sb_y + 18, "SB (Кнопка)", size=10, bold=True, color="#d97706"))
    frags.append(text(sb_x, sb_y + 34, "PRE-ARM", size=9, bold=True, color="#d97706"))

    # Перемикачі зверху справа: FLIGHT MODE та EMERGENCY RTH
    # 3. FLIGHT MODE (SC) - 3-pos toggle
    sc_x, sc_y = 620, 48
    frags.append(rect(sc_x - 45, sc_y, 90, 46, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(sc_x, sc_y + 18, "SC (3-поз)", size=10, bold=True, color=FIELD))
    frags.append(text(sc_x, sc_y + 34, "Angle / Acro", size=9, bold=True, color=FIELD))

    # 4. EMERGENCY RTH / FAILSAFE (SD) - 2-pos довгий тумблер із ковпачком
    sd_x, sd_y = 740, 48
    frags.append(rect(sd_x - 45, sd_y, 90, 46, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    frags.append(text(sd_x, sd_y + 18, "SD (Довгий)", size=10, bold=True, color=POS))
    frags.append(text(sd_x, sd_y + 34, "RTH / FAILSAFE", size=9, bold=True, color=POS))

    # Лінії зв'язку від верхніх блоків до корпусу
    frags.append(line(sa_x, sa_y + 46, sa_x, 108, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(sb_x, sb_y + 46, sb_x, 108, color="#d97706", sw=1.5, dash="2,2"))
    frags.append(line(sc_x, sc_y + 46, sc_x, 108, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(line(sd_x, sd_y + 46, sd_x, 108, color=POS, sw=1.5, dash="2,2"))

    # Корпус пульта (починається з y=110)
    tx_x, tx_y, tx_w, tx_h = 90, 110, 720, 350
    frags.append(rect(tx_x, tx_y, tx_w, tx_h, fill="#f8fafc", stroke="#334155", sw=2, rx=24))

    # Екран пульта посередині
    frags.append(rect(tx_x + tx_w / 2 - 120, tx_y + 30, 240, 95, fill="#1e293b", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(tx_x + tx_w / 2, tx_y + 70, "ТЕЛЕМЕТРІЯ / OSD", size=12, bold=True, color="#38bdf8"))
    frags.append(text(tx_x + tx_w / 2, tx_y + 92, "DISARMED | 0.0V | SAT: 16", size=10, color="#94a3b8"))

    # Стіки пульта
    # Лівий стік
    frags.append(circle(tx_x + 130, tx_y + 195, 52, fill="#ffffff", stroke="#94a3b8", sw=2))
    frags.append(circle(tx_x + 130, tx_y + 195, 9, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(tx_x + 130, tx_y + 265, "Лівий стік (Throttle / Yaw)", size=11, bold=True, color=INK))

    # Правий стік
    frags.append(circle(tx_x + tx_w - 130, tx_y + 195, 52, fill="#ffffff", stroke="#94a3b8", sw=2))
    frags.append(circle(tx_x + tx_w - 130, tx_y + 195, 9, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(text(tx_x + tx_w - 130, tx_y + 265, "Правий стік (Pitch / Roll)", size=11, bold=True, color=INK))

    # Допоміжні перемикачі знизу
    aux_y = tx_y + 295
    frags.append(rect(tx_x + tx_w / 2 - 160, aux_y, 320, 30, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    frags.append(text(tx_x + tx_w / 2, aux_y + 19, "Вторинні канали: SE (Buzzer) | SF (Turtle Mode) | SG (VTX)", size=10, color=MUTED))

    # Золоте правило безпеки
    frags.append(text(w / 2, 495, "Золоте правило передпольотної перевірки: ВСІ ПЕРЕМИКАЧІ ВІД СЕБЕ / ВГОРУ = SAFE", size=12, color=FIELD, bold=True))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "transmitter-safety-ergonomics.svg")
    render(out_path, w, h, *frags)
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    gen_stick_modes()
    gen_resistor_ladder()
    gen_transmitter_layout()
