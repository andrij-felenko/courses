# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'hall-sensor' (Магнітне поле й Холл)."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_hall_plate():
    """Фізика пластини Холла: струм I, поле B, сила Лоренца F_L, напруга V_H."""
    w, h = 760, 420
    frags = []

    # Заголовок блоків
    frags.append(text(w / 2, 28, "Фізика ефекту Холла: розділення зарядів силою Лоренца", size=16, bold=True))

    # Пластина Холла (напівпровідник n-типу)
    px, py, pw, ph = 180, 120, 380, 180
    frags.append(rect(px, py, pw, ph, fill="#edf2f7", stroke="#4a5568", sw=2, rx=8))

    # Струм (вхід зліва -> вихід справа)
    # Зліва: контакт входу струму (плюс джерела)
    frags.append(rect(px - 14, py + 40, 14, ph - 80, fill="#cbd5e0", stroke=LINE, sw=1.5, rx=3))
    # Справа: контакт виходу струму
    frags.append(rect(px + pw, py + 40, 14, ph - 80, fill="#cbd5e0", stroke=LINE, sw=1.5, rx=3))

    # Стрілка струму I (зліва направо)
    frags.append(arrow(px - 75, py + ph / 2, px - 18, py + ph / 2, color=POS, sw=2.5))
    frags.append(text(px - 45, py + ph / 2 - 12, "Струм I", size=12, color=POS, bold=True))

    frags.append(arrow(px + pw + 18, py + ph / 2, px + pw + 75, py + ph / 2, color=POS, sw=2.5))
    frags.append(text(px + pw + 45, py + ph / 2 - 12, "Струм I", size=12, color=POS, bold=True))

    # Рух електронів v_d (справа наліво, у правій частині)
    frags.append(arrow(px + 320, py + 75, px + 240, py + 75, color=NEG, sw=2))
    frags.append(text(px + 280, py + 60, "Дрейф електронів v_d", size=11, color=NEG, bold=True))

    # Магнітне поле B (перпендикулярно до площини)
    frags.append(circle(px + 65, py + 80, 13, fill="#e8f8f0", stroke=FIELD, sw=2))
    frags.append(circle(px + 65, py + 80, 3, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(px + 65, py + 106, "Поле B (на нас)", size=10.5, color=FIELD, bold=True))

    # Сила Лоренца F_L (штовхає електрони вниз)
    frags.append(arrow(px + 280, py + 90, px + 280, py + 138, color=POS, sw=2))
    frags.append(text(px + 292, py + 118, "Сила Лоренца F_L", size=11, color=POS, bold=True, anchor="start"))

    # Накопичення зарядів: вгорі нескомпенсовані донори (+), внизу надлишок електронів (-)
    for i in range(5):
        frags.append(plus(px + 50 + i * 70, py + 22, r=7.5))
        frags.append(minus(px + 50 + i * 70, py + ph - 22, r=7.5))

    # Електричне поле Холла E_H (від плюса до мінуса, зверху вниз, у лівій частині)
    frags.append(arrow(px + 140, py + 42, px + 140, py + ph - 42, color=FIELD, sw=2))
    frags.append(text(px + 150, py + 118, "Поле E_H", size=11, color=FIELD, bold=True, anchor="start"))

    # Сенсорні контакти напруги Холла (зверху і знизу)
    frags.append(rect(px + pw / 2 - 25, py - 12, 50, 12, fill="#cbd5e0", stroke=LINE, sw=1.5, rx=3))
    frags.append(rect(px + pw / 2 - 25, py + ph, 50, 12, fill="#cbd5e0", stroke=LINE, sw=1.5, rx=3))

    # Провідники до вимірювання напруги V_H
    frags.append(line(px + pw / 2, py - 12, px + pw / 2, py - 45, color=LINE, sw=1.5))
    frags.append(line(px + pw / 2, py + ph + 12, px + pw / 2, py + ph + 45, color=LINE, sw=1.5))

    # Вольтметр напруги Холла
    frags.append(circle(w - 110, py + ph / 2, 28, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(w - 110, py + ph / 2 + 5, "V_H", size=14, bold=True))

    frags.append(line(px + pw / 2, py - 45, w - 110, py - 45, color=LINE, sw=1.5))
    frags.append(line(w - 110, py - 45, w - 110, py + ph / 2 - 28, color=LINE, sw=1.5))

    frags.append(line(px + pw / 2, py + ph + 45, w - 110, py + ph + 45, color=LINE, sw=1.5))
    frags.append(line(w - 110, py + ph + 45, w - 110, py + ph / 2 + 28, color=LINE, sw=1.5))

    # Підпис рівноваги
    b_eq, _, _ = textbox(w / 2, 385, "Стан рівноваги: q · E_H = q · v_d · B  ⇒  V_H = (R_H · I · B) / t",
                         size=13, pad=8, fill="#f8fafc", stroke="#94a3b8", bold=True)
    frags.append(b_eq)

    render(os.path.join(IMG_DIR, "hall-physics-plate.svg"), w, h, *frags)


def fig_spinning_current():
    """Чотирифідний метод динамічного обертання струму (Spinning Current)."""
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 26, "Динамічне обертання струму (4-фазний Spinning Current)", size=16, bold=True))

    phases = [
        ("Фаза 1 (0°)", "I: 1 → 3, Вихід: 2 − 4", "V_1 = +V_H + V_off", POS),
        ("Фаза 2 (90°)", "I: 2 → 4, Вихід: 3 − 1", "V_2 = −V_H + V_off", NEG),
        ("Фаза 3 (180°)", "I: 3 → 1, Вихід: 4 − 2", "V_3 = +V_H + V_off", POS),
        ("Фаза 4 (270°)", "I: 4 → 2, Вихід: 1 − 3", "V_4 = −V_H + V_off", NEG),
    ]

    card_w = 180
    card_gap = 18
    start_x = (w - (4 * card_w + 3 * card_gap)) / 2

    for idx, (title_p, conn, formula, col) in enumerate(phases):
        cx = start_x + idx * (card_w + card_gap)
        cy = 55
        # Рамка фази
        frags.append(rect(cx, cy, card_w, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
        frags.append(text(cx + card_w / 2, cy + 22, title_p, size=13, bold=True, color=col))
        frags.append(text(cx + card_w / 2, cy + 42, conn, size=10.5, color=MUTED))

        # Мініатюра пластини Холла (квадрат із 4 контактами)
        sq_cx = cx + card_w / 2
        sq_cy = cy + 120
        sq_s = 64
        frags.append(rect(sq_cx - sq_s / 2, sq_cy - sq_s / 2, sq_s, sq_s, fill="#edf2f7", stroke="#475569", sw=1.5, rx=4))

        # 4 виводи (1-верх, 2-право, 3-низ, 4-ліво)
        p1 = (sq_cx, sq_cy - sq_s / 2)
        p2 = (sq_cx + sq_s / 2, sq_cy)
        p3 = (sq_cx, sq_cy + sq_s / 2)
        p4 = (sq_cx - sq_s / 2, sq_cy)

        frags.append(circle(p1[0], p1[1], 4, fill="#1e293b", stroke="#1e293b"))
        frags.append(text(p1[0], p1[1] - 8, "1", size=10, bold=True))

        frags.append(circle(p2[0], p2[1], 4, fill="#1e293b", stroke="#1e293b"))
        frags.append(text(p2[0] + 8, p2[1] + 4, "2", size=10, bold=True))

        frags.append(circle(p3[0], p3[1], 4, fill="#1e293b", stroke="#1e293b"))
        frags.append(text(p3[0], p3[1] + 13, "3", size=10, bold=True))

        frags.append(circle(p4[0], p4[1], 4, fill="#1e293b", stroke="#1e293b"))
        frags.append(text(p4[0] - 8, p4[1] + 4, "4", size=10, bold=True))

        # Стрілка струму всередині
        if idx == 0:  # 1 -> 3
            frags.append(arrow(sq_cx, sq_cy - 18, sq_cx, sq_cy + 18, color=POS, sw=2))
            frags.append(line(p2[0], p2[1], p2[0] + 18, p2[1], color=NEG, sw=1.5))
            frags.append(line(p4[0], p4[1], p4[0] - 18, p4[1], color=NEG, sw=1.5))
        elif idx == 1:  # 2 -> 4
            frags.append(arrow(sq_cx + 18, sq_cy, sq_cx - 18, sq_cy, color=POS, sw=2))
            frags.append(line(p1[0], p1[1], p1[0], p1[1] - 18, color=NEG, sw=1.5))
            frags.append(line(p3[0], p3[1], p3[0], p3[1] + 18, color=NEG, sw=1.5))
        elif idx == 2:  # 3 -> 1
            frags.append(arrow(sq_cx, sq_cy + 18, sq_cx, sq_cy - 18, color=POS, sw=2))
            frags.append(line(p2[0], p2[1], p2[0] + 18, p2[1], color=NEG, sw=1.5))
            frags.append(line(p4[0], p4[1], p4[0] - 18, p4[1], color=NEG, sw=1.5))
        elif idx == 3:  # 4 -> 2
            frags.append(arrow(sq_cx - 18, sq_cy, sq_cx + 18, sq_cy, color=POS, sw=2))
            frags.append(line(p1[0], p1[1], p1[0], p1[1] - 18, color=NEG, sw=1.5))
            frags.append(line(p3[0], p3[1], p3[0], p3[1] + 18, color=NEG, sw=1.5))

        # Формула виходу
        frags.append(rect(cx + 10, cy + 195, card_w - 20, 32, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        frags.append(text(cx + card_w / 2, cy + 215, formula, size=11.5, bold=True))

    # Підсумковий блок демодуляції
    b_res, _, _ = textbox(w / 2, 345, "Демодуляція: V_H = (V_1 − V_2 + V_3 − V_4) / 4  (зміщення V_off і 1/f-шум повністю знищуються)",
                          size=13, pad=10, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_res)

    render(os.path.join(IMG_DIR, "spinning-current-phases.svg"), w, h, *frags)


def fig_hall_switch_types():
    """Характеристики цифрових перемикачів Холла: уніполярний, біполярний (засувка), омніполярний."""
    w, h = 820, 370
    frags = []

    frags.append(text(w / 2, 26, "Характеристики цифрових давачів Холла: типи магнітного перемикання", size=16, bold=True))

    cards = [
        ("Уніполярний перемикач", "Реагує лише на один полюс (S)", "B_OP > 0, B_RP > 0", 0),
        ("Біполярна засувка (Latch)", "Вмикає S-полюс, вимикає N-полюс", "B_OP > 0, B_RP < 0", 1),
        ("Омніполярний перемикач", "Спрацьовує на будь-який полюс (|B|)", "|B| > |B_OP|", 2),
    ]

    card_w = 246
    card_gap = 20
    start_x = (w - (3 * card_w + 2 * card_gap)) / 2

    for idx, (title_s, desc_s, formula_s, mode) in enumerate(cards):
        cx = start_x + idx * (card_w + card_gap)
        cy = 55
        frags.append(rect(cx, cy, card_w, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
        frags.append(text(cx + card_w / 2, cy + 24, title_s, size=13.5, bold=True))
        frags.append(text(cx + card_w / 2, cy + 42, desc_s, size=11, color=MUTED))

        # Графік перемикання
        gx = cx + 32
        gy = cy + 70
        gw = card_w - 64
        gh = 130

        # Осі: горизонтальна B (поле), вертикальна OUT (HIGH/LOW)
        frags.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color="#94a3b8", sw=1.2))  # вісь B = 0
        frags.append(line(gx + gw / 2, gy, gx + gw / 2, gy + gh, color="#94a3b8", sw=1.2))  # нуль B

        frags.append(text(gx + gw - 8, gy + gh / 2 - 6, "B", size=11, bold=True, color=MUTED))
        frags.append(text(gx + gw / 2 + 6, gy + 12, "OUT", size=10, bold=True, color=MUTED))
        frags.append(text(gx + 12, gy + gh / 2 - 6, "−B (N)", size=9.5, color=MUTED))
        frags.append(text(gx + gw - 22, gy + gh / 2 + 14, "+B (S)", size=9.5, color=MUTED))

        # Крива петлі
        y_high = gy + 25
        y_low = gy + gh - 25

        if mode == 0:  # Unipolar
            b_rp = gx + gw / 2 + 25
            b_op = gx + gw / 2 + 60
            # Лінія HIGH до B_OP, стрибок вниз до LOW
            frags.append(line(gx, y_high, b_op, y_high, color=POS, sw=2))
            frags.append(arrow(b_op, y_high, b_op, y_low, color=POS, sw=2))
            frags.append(line(b_op, y_low, gx + gw - 10, y_low, color=POS, sw=2))
            # Зворотний рух: LOW до B_RP, стрибок вгору до HIGH
            frags.append(line(gx + gw - 10, y_low, b_rp, y_low, color=NEG, sw=2, dash="3,3"))
            frags.append(arrow(b_rp, y_low, b_rp, y_high, color=NEG, sw=2))
            frags.append(line(b_rp, y_high, gx, y_high, color=NEG, sw=2, dash="3,3"))

            frags.append(text(b_op, gy + gh - 6, "B_OP", size=9.5, bold=True, color=POS))
            frags.append(text(b_rp - 10, gy + gh - 6, "B_RP", size=9.5, bold=True, color=NEG))

        elif mode == 1:  # Bipolar Latch
            b_rp = gx + gw / 2 - 45  # North
            b_op = gx + gw / 2 + 45  # South
            frags.append(line(gx, y_high, b_op, y_high, color=POS, sw=2))
            frags.append(arrow(b_op, y_high, b_op, y_low, color=POS, sw=2))
            frags.append(line(b_op, y_low, gx + gw - 10, y_low, color=POS, sw=2))

            frags.append(line(gx + gw - 10, y_low, b_rp, y_low, color=NEG, sw=2, dash="3,3"))
            frags.append(arrow(b_rp, y_low, b_rp, y_high, color=NEG, sw=2))
            frags.append(line(b_rp, y_high, gx, y_high, color=NEG, sw=2, dash="3,3"))

            frags.append(text(b_op, gy + gh - 6, "+B_OP", size=9.5, bold=True, color=POS))
            frags.append(text(b_rp, gy + gh - 6, "−B_RP", size=9.5, bold=True, color=NEG))

        elif mode == 2:  # Omnipolar
            b_op_s = gx + gw / 2 + 50
            b_rp_s = gx + gw / 2 + 25
            b_op_n = gx + gw / 2 - 50
            b_rp_n = gx + gw / 2 - 25

            # В центрі (|B| < B_RP) -> HIGH
            frags.append(line(b_rp_n, y_high, b_rp_s, y_high, color=LINE, sw=2))
            # При русі вправо -> LOW
            frags.append(arrow(b_op_s, y_high, b_op_s, y_low, color=POS, sw=1.8))
            frags.append(line(b_op_s, y_low, gx + gw - 10, y_low, color=POS, sw=1.8))
            # При русі вліво -> LOW
            frags.append(arrow(b_op_n, y_high, b_op_n, y_low, color=NEG, sw=1.8))
            frags.append(line(b_op_n, y_low, gx + 10, y_low, color=NEG, sw=1.8))

            frags.append(text(gx + gw / 2, gy + gh - 6, "Гістерезис з обох боків", size=9.5, color=MUTED))

        # Пояснення гістерезису
        frags.append(rect(cx + 12, cy + 225, card_w - 24, 48, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        frags.append(text(cx + card_w / 2, cy + 245, formula_s, size=11, bold=True))
        frags.append(text(cx + card_w / 2, cy + 262, "B_HYS = B_OP − B_RP (захист від брязкоту)", size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "hall-switch-hysteresis.svg"), w, h, *frags)


def fig_integrated_hall_arch():
    """Архітектура інтегрального сенсора Холла з чоппером і температурною компенсацією."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Внутрішня структура прецизійного інтегрального сенсора Холла", size=16, bold=True))

    # Блоки тракту (зліва направо)
    blocks = [
        ("Елемент Холла\n(Spinning Plate)", 50, 75, 120, 85, "#e0f2fe", "#0284c7"),
        ("Комутатор\n(Chopper Switches)", 200, 75, 125, 85, "#f1f5f9", "#475569"),
        ("Низькошумний\nПП (LNA)", 355, 75, 115, 85, "#fef3c7", "#d97706"),
        ("Демодулятор\nй ФНЧ (SC Filter)", 500, 75, 125, 85, "#f1f5f9", "#475569"),
        ("Вихідний каскад\n(АЦП / ДСП / Драйвер)", 655, 75, 125, 85, "#dcfce7", "#16a34a"),
    ]

    for label, bx, by, bw, bh, fill_c, stroke_c in blocks:
        frags.append(fitbox(bx, by, bw, bh, label, size=12, pad=6, fill=fill_c, stroke=stroke_c, sw=1.8, bold=True))

    # Стрілки між блоками
    frags.append(arrow(170, 117, 200, 117, color=LINE, sw=2))
    frags.append(arrow(325, 117, 355, 117, color=LINE, sw=2))
    frags.append(arrow(470, 117, 500, 117, color=LINE, sw=2))
    frags.append(arrow(625, 117, 655, 117, color=LINE, sw=2))

    # Вихід назовні
    frags.append(arrow(780, 117, 810, 117, color=LINE, sw=2))
    frags.append(text(780, 105, "V_OUT / I2C", size=11, bold=True, anchor="end"))

    # Допоміжні блоки знизу (Тактовий генератор чоппера, Температурний сенсор, EEPROM)
    aux_blocks = [
        ("Тактовий генератор\nобертання (f_chop ~ 100-500 кГц)", 200, 205, 190, 65, "#f8fafc", "#64748b"),
        ("Температурна компенсація\nй EEPROM калібрування", 460, 205, 200, 65, "#fdf4ff", "#a855f7"),
    ]

    for label, bx, by, bw, bh, fill_c, stroke_c in aux_blocks:
        frags.append(fitbox(bx, by, bw, bh, label, size=11.5, pad=6, fill=fill_c, stroke=stroke_c, sw=1.5, bold=True))

    # Зв'язки допоміжних блоків
    frags.append(arrow(295, 205, 262, 160, color="#64748b", sw=1.5))
    frags.append(arrow(295, 205, 562, 160, color="#64748b", sw=1.5))

    frags.append(arrow(560, 205, 717, 160, color="#a855f7", sw=1.5))

    # Пояснювальний підпис
    b_foot, _, _ = textbox(w / 2, 315, "Чоппер переносить сигнал на частоту f_chop, відокремлюючи його від 1/f шуму та зсуву кристала",
                           size=12.5, pad=8, fill="#ffffff", stroke="#cbd5e1", bold=False)
    frags.append(b_foot)

    render(os.path.join(IMG_DIR, "integrated-hall-arch.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_hall_plate()
    fig_spinning_current()
    fig_hall_switch_types()
    fig_integrated_hall_arch()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
