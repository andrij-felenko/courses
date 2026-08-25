# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Теплоємність'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_cv_vs_cp():
    """Фігура 1: Термодинамічна різниця між ізохорною (C_V) та ізобарною (C_p) теплоємностями."""
    w, h = 800, 410
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Термодинамічне порівняння ізохорної (C_V) та ізобарної (C_p) теплоємностей", size=16, bold=True))

    # Лівий блок: Ізохорний процес (V = const)
    b1_x, b1_y, b1_w, b1_h = 30, 55, 350, 290
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 25, "Ізохорний процес: C_V (V = const)", size=14, bold=True, color=NEG))
    frags.append(line(b1_x + 15, b1_y + 35, b1_x + b1_w - 15, b1_y + 35, color=MUTED, sw=1, dash="3,3"))

    # Схема циліндра з зафіксованим поршнем
    cx1 = b1_x + 80
    cy1 = b1_y + 60
    cw, ch = 190, 150
    # Циліндр
    frags.append(rect(cx1, cy1, cw, ch, fill="#f8fafc", stroke=LINE, sw=2, rx=4))
    # Поршень (зафіксований стопорами)
    frags.append(rect(cx1 + 4, cy1 + 30, cw - 8, 16, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s"/>' %
                 (cx1 - 6, cy1 + 25, cx1 + 4, cy1 + 38, cx1 - 6, cy1 + 50, POS, LINE))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s"/>' %
                 (cx1 + cw + 6, cy1 + 25, cx1 + cw - 4, cy1 + 38, cx1 + cw + 6, cy1 + 50, POS, LINE))
    frags.append(text(cx1 + cw / 2, cy1 + 22, "Зафіксований поршень (dV = 0)", size=11, color=MUTED))

    # Молекули газу внизу
    for (mx, my) in [(cx1 + 40, cy1 + 75), (cx1 + 90, cy1 + 110), (cx1 + 140, cy1 + 80), (cx1 + 70, cy1 + 130), (cx1 + 150, cy1 + 125)]:
        frags.append(circle(mx, my, 7, fill=NEG, stroke=LINE, sw=1))

    # Тепловий потік Q_V
    frags.append(arrow(cx1 + cw / 2, cy1 + ch + 35, cx1 + cw / 2, cy1 + ch + 5, color=POS, sw=3))
    frags.append(text(cx1 + cw / 2 + 35, cy1 + ch + 22, "Q_V = dU", size=13, color=POS, bold=True))

    # Формули ізохорного процесу
    frags.append(textbox(b1_x + b1_w / 2, b1_y + 245, "Робота розширення: dW = P · dV = 0\nУсе тепло йде на внутрішню енергію: dU = δQ_V\nC_V = (∂U / ∂T)_V", size=12, fill="#ffffff", stroke=NEG, sw=1.2)[0])

    # Правий блок: Ізобарний процес (P = const)
    b2_x, b2_y, b2_w, b2_h = 420, 55, 350, 290
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 25, "Ізобарний процес: C_p (P = const)", size=14, bold=True, color=POS))
    frags.append(line(b2_x + 15, b2_y + 35, b2_x + b2_w - 15, b2_y + 35, color=MUTED, sw=1, dash="3,3"))

    # Схема циліндра з рухомим поршнем
    cx2 = b2_x + 80
    cy2 = b2_y + 60
    # Циліндр
    frags.append(rect(cx2, cy2, cw, ch, fill="#f8fafc", stroke=LINE, sw=2, rx=4))
    # Рухомий поршень (зсунутий вгору, є стрілка руху)
    frags.append(rect(cx2 + 4, cy2 + 15, cw - 8, 16, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(arrow(cx2 + cw / 2, cy2 + 15, cx2 + cw / 2, cy2 - 10, color=FIELD, sw=2.5))
    frags.append(text(cx2 + cw / 2, cy2 - 16, "Розширення: dW = P · dV > 0", size=11, color=FIELD, bold=True))

    # Молекули газу внизу
    for (mx, my) in [(cx2 + 40, cy2 + 65), (cx2 + 90, cy2 + 105), (cx2 + 140, cy2 + 75), (cx2 + 65, cy2 + 125), (cx2 + 150, cy2 + 120)]:
        frags.append(circle(mx, my, 7, fill=POS, stroke=LINE, sw=1))

    # Тепловий потік Q_p
    frags.append(arrow(cx2 + cw / 2, cy2 + ch + 35, cx2 + cw / 2, cy2 + ch + 5, color=POS, sw=3))
    frags.append(text(cx2 + cw / 2 + 45, cy2 + ch + 22, "Q_p = dU + P dV", size=13, color=POS, bold=True))

    # Формули ізобарного процесу
    frags.append(textbox(b2_x + b2_w / 2, b2_y + 245, "Газ виконує роботу проти тиску: dW > 0\nПотрібно більше тепла для розігріву на 1 K\nC_p = (∂H / ∂T)_p = C_V + P(∂V/∂T)_p", size=12, fill="#ffffff", stroke=POS, sw=1.2)[0])

    # Загальний підсумок знизу: Співвідношення Маєра
    frags.append(textbox(w / 2, 375, "Співвідношення Маєра для 1 моля ідеального газу:  C_p,m - C_V,m = R ≈ 8.314 Дж/(моль·К)", size=13, bold=True, fill="#f1f5f9", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "cv-vs-cp.svg"), w, h, *frags)


def build_fig2_quantum_heat_capacity():
    """Фігура 2: Залежність молярної теплоємності C_V(T) двоатомного газу від температури (розморожування мод)."""
    w, h = 780, 420
    frags = []

    frags.append(text(w / 2, 26, "Температурна залежність теплоємності C_V(T) двоатомного газу (H₂)", size=15, bold=True))

    ox, oy = 80, 350
    graph_w, graph_h = 650, 270

    # Вісі координат
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Температура T (абсолютна шкала, логарифмічний масштаб)", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "C_V / R", size=14, bold=True, anchor="middle"))

    # Пунктирні лінії плато (1.5 R, 2.5 R, 3.5 R)
    levels = [(1.5, "3/2 R (поступальні)", NEG, oy - 70),
              (2.5, "5/2 R (+ обертальні)", FIELD, oy - 150),
              (3.5, "7/2 R (+ коливальні)", POS, oy - 230)]

    for val, label, col, y_pos in levels:
        frags.append(line(ox, y_pos, ox + graph_w, y_pos, color=MUTED, sw=1, dash="4,4"))
        frags.append(text(ox - 10, y_pos + 4, "%.1f" % val, size=11, anchor="end", bold=True, color=col))
        frags.append(text(ox + graph_w - 10, y_pos - 8, label, size=11, anchor="end", bold=True, color=col))

    # Температурні позначки на осі X (T_rot ~ 85 K, T_vib ~ 3000 K, T_dissoc ~ 5000 K)
    ticks = [(ox + 100, "50 К"), (ox + 230, "T_rot ≈ 85 К"), (ox + 460, "T_vib ≈ 3000 К"), (ox + 600, "T_дисоц")]
    for tx, tlabel in ticks:
        frags.append(line(tx, oy, tx, oy + 6, color=LINE, sw=1.5))
        frags.append(text(tx, oy + 22, tlabel, size=11, anchor="middle", bold=True))

    # Плавна крива C_V(T) для H2
    pts = [
        (ox, oy - 70), (ox + 120, oy - 70),
        (ox + 180, oy - 100), (ox + 250, oy - 150), (ox + 350, oy - 150),
        (ox + 420, oy - 180), (ox + 500, oy - 230), (ox + 560, oy - 230),
        (ox + 610, oy - 180)
    ]

    path_d = ["M %.1f,%.1f" % pts[0]]
    for i in range(1, len(pts)):
        p0 = pts[i-1]
        p1 = pts[i]
        cx1 = p0[0] + (p1[0] - p0[0]) / 2
        cy1 = p0[1]
        cx2 = p0[0] + (p1[0] - p0[0]) / 2
        cy2 = p1[1]
        path_d.append("C %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx1, cy1, cx2, cy2, p1[0], p1[1]))

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_d), POS))

    # Аннотаційні текстові блоки під ступенями
    frags.append(text(ox + 60, oy - 85, "Лише поступальний рух", size=10, italic=True, color=NEG))
    frags.append(text(ox + 300, oy - 165, "Поступальний + Обертальний", size=10, italic=True, color=FIELD))
    frags.append(text(ox + 510, oy - 245, "Поступальний + Обертальний + Коливальний", size=10, italic=True, color=POS))

    render(os.path.join(IMG_DIR, "quantum-heat-capacity.svg"), w, h, *frags)


def build_fig3_einstein_debye_curves():
    """Фігура 3: Порівняння моделей Дюлонга — Пті, Ейнштейна та Дебая для теплоємності твердих тіл."""
    w, h = 780, 430
    frags = []

    frags.append(text(w / 2, 26, "Теплоємність твердих тіл: класична та квантові моделі", size=15, bold=True))

    ox, oy = 80, 360
    graph_w, graph_h = 650, 280

    # Вісі
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Нормована температура T / Θ_D", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "C_V / 3R", size=14, bold=True, anchor="middle"))

    # Стеля Дюлонга - Пті (C_V = 3R => ratio = 1.0)
    y_3r = oy - 230
    frags.append(line(ox, y_3r, ox + graph_w, y_3r, color=POS, sw=2, dash="6,4"))
    frags.append(text(ox - 10, y_3r + 4, "1.0", size=12, anchor="end", bold=True, color=POS))
    frags.append(text(ox + graph_w - 20, y_3r - 8, "Класична межа Дюлонга — Пті (C_V = 3R)", size=12, anchor="end", bold=True, color=POS))

    # Позначки осі X (T/Theta_D)
    x_ticks = [(ox, "0"), (ox + 130, "0.2"), (ox + 260, "0.4"), (ox + 390, "0.6"), (ox + 520, "0.8"), (ox + 650, "1.0")]
    for tx, tlabel in x_ticks:
        frags.append(line(tx, oy, tx, oy + 6, color=LINE, sw=1.5))
        frags.append(text(tx, oy + 22, tlabel, size=11, anchor="middle"))

    # Побудова кривої Дебая C_V^D ~ T^3 при малій T, перехід до 1
    pts_debye = []
    for i in range(101):
        t_norm = i / 100.0
        if t_norm < 0.15:
            val = (12 * math.pi**4 / 5) * (t_norm**3) / 3.0
        else:
            val = t_norm**3 / (t_norm**3 + 0.12)
        val = min(val, 1.0)
        px = ox + t_norm * graph_w
        py = oy - val * 230
        pts_debye.append((px, py))

    path_debye = ["M %.1f,%.1f" % pts_debye[0]]
    for pt in pts_debye[1:]:
        path_debye.append("L %.1f,%.1f" % pt)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_debye), FIELD))

    # Побудова кривої Ейнштейна C_V^E ~ exp(-T_E/T) / T^2
    pts_einstein = []
    for i in range(101):
        t_norm = i / 100.0
        if t_norm < 0.03:
            val = 0.0
        else:
            x_e = 0.75 / t_norm
            if x_e > 40:
                val = 0.0
            else:
                val = (x_e**2 * math.exp(x_e)) / ((math.exp(x_e) - 1)**2)
        val = min(val, 1.0)
        px = ox + t_norm * graph_w
        py = oy - val * 230
        pts_einstein.append((px, py))

    path_einstein = ["M %.1f,%.1f" % pts_einstein[0]]
    for pt in pts_einstein[1:]:
        path_einstein.append("L %.1f,%.1f" % pt)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (" ".join(path_einstein), NEG))

    # Легенда
    leg_x, leg_y = ox + 320, oy - 80
    frags.append(rect(leg_x, leg_y, 300, 75, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(line(leg_x + 10, leg_y + 20, leg_x + 40, leg_y + 20, color=POS, sw=2, dash="4,2"))
    frags.append(text(leg_x + 50, leg_y + 24, "Дюлонг — Пті (класична, C_V = 3R)", size=11))

    frags.append(line(leg_x + 10, leg_y + 40, leg_x + 40, leg_y + 40, color=FIELD, sw=3))
    frags.append(text(leg_x + 50, leg_y + 44, "Модель Дебая (фонони, C_V ∝ T³)", size=11, bold=True))

    frags.append(line(leg_x + 10, leg_y + 60, leg_x + 40, leg_y + 60, color=NEG, sw=2.5, dash="5,3"))
    frags.append(text(leg_x + 50, leg_y + 64, "Модель Ейнштейна (експоненційний спад)", size=11))

    render(os.path.join(IMG_DIR, "einstein-debye-curves.svg"), w, h, *frags)


def build_fig4_phase_transition_lambda():
    """Фігура 4: Аномалія теплоємності при фазових переходах (лямбда-точка рідкого гелію-4)."""
    w, h = 760, 410
    frags = []

    frags.append(text(w / 2, 26, "Аномалія теплоємності при лямбда-переході в рідкому гелії-4", size=15, bold=True))

    ox, oy = 80, 350
    graph_w, graph_h = 630, 270

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Температура T (К)", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "C_p (Дж / (моль·К))", size=14, bold=True, anchor="middle"))

    # Позначка критичної температури T_lambda = 2.17 K
    x_lambda = ox + 320
    frags.append(line(x_lambda, oy, x_lambda, oy - graph_h + 20, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(x_lambda, oy, x_lambda, oy + 6, color=POS, sw=2))
    frags.append(text(x_lambda, oy + 22, "T_λ = 2.17 K", size=12, anchor="middle", bold=True, color=POS))

    # Спік лямбда-кривої C_p(T)
    pts_left = []
    for i in range(50):
        t = 1.0 + (i / 49.0) * 1.16
        dt = abs(2.17 - t)
        val = 10 + 15 * math.log(1.0 + 1.0 / (dt + 0.02))
        px = ox + ((t - 1.0) / 2.0) * graph_w
        py = oy - min(val, 240) * (graph_h / 260)
        pts_left.append((px, py))

    pts_right = []
    for i in range(50):
        t = 2.172 + (i / 49.0) * 0.828
        dt = abs(t - 2.17)
        val = 12 + 18 * math.log(1.0 + 1.0 / (dt + 0.03))
        px = ox + ((t - 1.0) / 2.0) * graph_w
        py = oy - min(val, 240) * (graph_h / 260)
        pts_right.append((px, py))

    path_l = ["M %.1f,%.1f" % pts_left[0]] + ["L %.1f,%.1f" % p for p in pts_left[1:]]
    path_r = ["M %.1f,%.1f" % pts_right[0]] + ["L %.1f,%.1f" % p for p in pts_right[1:]]

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_l), POS))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_r), POS))

    # Підписи фаз
    frags.append(textbox(ox + 140, oy - 180, "Надплинний гелій (He-II)\nКвантова рідина (BSE)", size=12, fill="#dbeafe", stroke=NEG, sw=1.2)[0])
    frags.append(textbox(ox + 480, oy - 140, "Нормальний рідкий гелій (He-I)\nКласична в'язка рідина", size=12, fill="#fee2e2", stroke=POS, sw=1.2)[0])

    render(os.path.join(IMG_DIR, "phase-transition-lambda.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_cv_vs_cp()
    build_fig2_quantum_heat_capacity()
    build_fig3_einstein_debye_curves()
    build_fig4_phase_transition_lambda()
    print("Усі фігури для heat-capacity успішно згенеровано.")
