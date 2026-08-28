#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Ймовірність — це ще не рішення»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox, textbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_calibration_and_overconfidence():
    """Фігура 1: Діаграма надійності та температурне масштабування."""
    w, h = 840, 470
    frags = []

    # Заголовки блоків
    frags.append(text(235, 32, "Діаграма калібрування (Reliability Diagram)", size=15, bold=True))
    frags.append(text(645, 32, "Температурне масштабування", size=15, bold=True))

    # Лівий графік (Reliability diagram)
    gx0, gy0, gw, gh = 75, 370, 310, 270
    gx1, gy1 = gx0 + gw, gy0 - gh

    # Рамка графіка
    frags.append(rect(gx0, gy1, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.0))
    for i in range(1, 5):
        xx = gx0 + i * (gw / 5)
        yy = gy0 - i * (gh / 5)
        frags.append(line(xx, gy0, xx, gy1, color="#e5e7eb", sw=1.0, dash="3,3"))
        frags.append(line(gx0, yy, gx1, yy, color="#e5e7eb", sw=1.0, dash="3,3"))
        val_str = "0.%d" % (i * 2)
        frags.append(text(xx, gy0 + 18, val_str, size=11, color=MUTED))
        frags.append(text(gx0 - 14, yy + 4, val_str, size=11, color=MUTED, anchor="end"))

    frags.append(text(gx0, gy0 + 18, "0.0", size=11, color=MUTED))
    frags.append(text(gx1, gy0 + 18, "1.0", size=11, color=MUTED))
    frags.append(text(gx0 - 14, gy0 + 4, "0.0", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx0 - 14, gy1 + 4, "1.0", size=11, color=MUTED, anchor="end"))

    # Підписи осей
    frags.append(text(gx0 + gw / 2, gy0 + 40, "Впевненість моделі (Confidence / Softmax)", size=12, bold=True))
    frags.append(text(gx0 + 10, gy1 - 12, "Фактична точність (Accuracy)", size=12, bold=True, anchor="start"))

    # 1. Ідеальна калібрована лінія y = x
    frags.append(line(gx0, gy0, gx1, gy1, color="#9ca3af", sw=2.0, dash="5,5"))
    frags.append(text(gx1 - 40, gy1 + 35, "Ідеал (y = x)", size=11, color=MUTED, italic=True))

    # 2. Некалібрована крива (overconfident)
    pts_uncal = [
        (gx0, gy0),
        (gx0 + 0.3 * gw, gy0 - 0.12 * gh),
        (gx0 + 0.6 * gw, gy0 - 0.30 * gh),
        (gx0 + 0.85 * gw, gy0 - 0.52 * gh),
        (gx0 + 1.0 * gw, gy0 - 0.78 * gh)
    ]
    path_d = ["M %.1f,%.1f" % pts_uncal[0]]
    for px, py in pts_uncal[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), POS))
    for px, py in pts_uncal:
        frags.append(circle(px, py, 3.5, fill=POS, stroke="#ffffff", sw=1.5))

    # Позначка перенасиченої зони (Overconfidence)
    frags.append(text(gx0 + 0.72 * gw, gy0 - 0.22 * gh, "Надмірна впевненість", size=11, color=POS, bold=True))
    frags.append(text(gx0 + 0.72 * gw, gy0 - 0.14 * gh, "(Softmax 0.95 → Точність 65%)", size=10, color=POS))

    # 3. Відкалібрована крива після Temperature Scaling
    pts_cal = [
        (gx0, gy0),
        (gx0 + 0.25 * gw, gy0 - 0.23 * gh),
        (gx0 + 0.50 * gw, gy0 - 0.48 * gh),
        (gx0 + 0.75 * gw, gy0 - 0.73 * gh),
        (gx0 + 1.0 * gw, gy0 - 0.98 * gh)
    ]
    path_cal_d = ["M %.1f,%.1f" % pts_cal[0]]
    for px, py in pts_cal[1:]:
        path_cal_d.append("L %.1f,%.1f" % (px, py))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_cal_d), FIELD))
    for px, py in pts_cal:
        frags.append(circle(px, py, 3.5, fill=FIELD, stroke="#ffffff", sw=1.5))

    frags.append(text(gx0 + 0.32 * gw, gy0 - 0.58 * gh, "Калібрована крива", size=11, color=FIELD, bold=True))

    # Правий блок: Пояснення Temperature Scaling
    rx0, ry0, rw, rh = 460, 65, 340, 360
    frags.append(rect(rx0, ry0, rw, rh, fill=FILL, stroke="#cbd5e1", sw=1.5, rx=8))

    frags.append(text(rx0 + rw / 2, ry0 + 26, "Масштабування логітів (T > 1)", size=13, bold=True))

    # Формула softmax з температурою
    box_formula = rect(rx0 + 15, ry0 + 48, rw - 30, 48, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=5)
    frags.append(box_formula)
    frags.append(text(rx0 + rw / 2, ry0 + 77, "q[i] = exp( z[i] / T ) / Σ exp( z[j] / T )", size=12, color=INK, bold=True))

    # Пояснювальні пункти
    items = [
        ("• z[i] — сирі логіти", "вихід останнього лінійного шару моделі"),
        ("• T = 1.0 (стандарт)", "екстремальні ймовірності 0.01 або 0.99"),
        ("• T > 1.0 (пом'якшення)", "розподіл згладжується, ентропія зростає"),
        ("• Властивість інваріантності", "argmax(z) не змінюється (top-1 клас той самий)"),
        ("• Результат", "значення q[i] відповідають реальній точності")
    ]

    ty = ry0 + 120
    for title_txt, desc_txt in items:
        frags.append(text(rx0 + 20, ty, title_txt, size=11, bold=True, anchor="start", color=INK))
        frags.append(text(rx0 + 30, ty + 16, desc_txt, size=10, color=MUTED, anchor="start"))
        ty += 42

    return render(os.path.join(IMG_DIR, "calibration-and-overconfidence.svg"), w, h, *frags)


def fig_decision_cost_matrix():
    """Фігура 2: Матриця втрат і вибір оптимального порогу."""
    w, h = 840, 430
    frags = []

    frags.append(text(w / 2, 28, "Матриця втрат і зсув порогу прийняття рішення", size=15, bold=True))

    # Ліва частина: Матриця втрат 2x2
    mx0, my0 = 50, 65
    mw, mh = 350, 310
    frags.append(rect(mx0, my0, mw, mh, fill=FILL, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(mx0 + mw / 2, my0 + 26, "Матриця ціни помилок (Cost Matrix)", size=13, bold=True))

    # Заголовки стовпців і рядків
    frags.append(text(mx0 + 200, my0 + 56, "Дія: Стоп (a₁)", size=11, bold=True))
    frags.append(text(mx0 + 290, my0 + 56, "Дія: Рух (a₀)", size=11, bold=True))

    frags.append(text(mx0 + 20, my0 + 115, "Факт: Перешкода", size=11, bold=True, anchor="start"))
    frags.append(text(mx0 + 20, my0 + 195, "Факт: Чисто", size=11, bold=True, anchor="start"))

    # 4 клітинки
    # True Positive: перешкода + стоп -> Втрати = 0
    frags.append(rect(mx0 + 160, my0 + 80, 80, 70, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(mx0 + 200, my0 + 110, "C_TP = 0", size=12, bold=True, color=FIELD))
    frags.append(text(mx0 + 200, my0 + 130, "Вчасний стоп", size=9, color=MUTED))

    # False Negative: перешкода + рух -> Зіткнення (катастрофа)
    frags.append(rect(mx0 + 250, my0 + 80, 80, 70, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(mx0 + 290, my0 + 110, "C_FN = 1000", size=12, bold=True, color=POS))
    frags.append(text(mx0 + 290, my0 + 130, "Аварія / Травма", size=9, color=POS))

    # False Positive: чисто + стоп -> Хибна тривога
    frags.append(rect(mx0 + 160, my0 + 160, 80, 70, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(mx0 + 200, my0 + 190, "C_FP = 1", size=12, bold=True, color="#b45309"))
    frags.append(text(mx0 + 200, my0 + 210, "Затримка 2 с", size=9, color=MUTED))

    # True Negative: чисто + рух -> Втрати = 0
    frags.append(rect(mx0 + 250, my0 + 160, 80, 70, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(mx0 + 290, my0 + 190, "C_TN = 0", size=12, bold=True, color=FIELD))
    frags.append(text(mx0 + 290, my0 + 210, "Штатний рух", size=9, color=MUTED))

    # Підсумок під матрицею
    frags.append(text(mx0 + mw / 2, my0 + 270, "Асиметрія: C_FN >> C_FP (у 1000 разів)", size=11, bold=True, color=POS))

    # Права частина: Порівняння порогів та формули
    px0, py0 = 430, 65
    pw, ph = 370, 310
    frags.append(rect(px0, py0, pw, ph, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(px0 + pw / 2, py0 + 26, "Бейєсівський оптимум порогу T*", size=13, bold=True))

    # Формула розрахунку T*
    box_f = rect(px0 + 15, py0 + 48, pw - 30, 48, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=5)
    frags.append(box_f)
    frags.append(text(px0 + pw / 2, py0 + 77, "T* = C_FP / ( C_FP + C_FN )", size=13, bold=True, color=INK))

    # Графічна шкала порогів від 0.0 до 1.0
    sy = py0 + 155
    frags.append(line(px0 + 30, sy, px0 + pw - 30, sy, color=LINE, sw=3.0))
    frags.append(line(px0 + 30, sy - 8, px0 + 30, sy + 8, color=LINE, sw=2.0))
    frags.append(line(px0 + pw - 30, sy - 8, px0 + pw - 30, sy + 8, color=LINE, sw=2.0))
    frags.append(text(px0 + 30, sy + 22, "0.0", size=11, color=MUTED))
    frags.append(text(px0 + pw - 30, sy + 22, "1.0", size=11, color=MUTED))

    # Наївний симетричний поріг T = 0.5
    mid_x = px0 + pw / 2
    frags.append(line(mid_x, sy - 15, mid_x, sy + 15, color="#9ca3af", sw=2.0, dash="3,3"))
    frags.append(circle(mid_x, sy, 5, fill="#9ca3af", stroke="#ffffff", sw=1.5))
    frags.append(text(mid_x, sy - 22, "Наївний T = 0.5", size=11, color=MUTED, bold=True))
    frags.append(text(mid_x, sy + 38, "(ігнорує ціну смерті)", size=9, color=MUTED))

    # Реальний поріг T* = 0.001 (біля 0)
    opt_x = px0 + 30 + 15
    frags.append(line(opt_x, sy - 20, opt_x, sy + 20, color=POS, sw=2.5))
    frags.append(circle(opt_x, sy, 6, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(opt_x + 35, sy - 26, "Оптимум T* ≈ 0.001", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(opt_x + 35, sy - 10, "Гальмуємо навіть при P = 0.01", size=10, color=POS, anchor="start"))

    # Пояснення висновку
    frags.append(text(px0 + 20, py0 + 235, "Висновок інженера:", size=11, bold=True, anchor="start"))
    frags.append(text(px0 + 20, py0 + 258, "Краще 10 разів помилково зупинитися,", size=10, color=INK, anchor="start"))
    frags.append(text(px0 + 20, py0 + 276, "ніж 1 раз на повній швидкості збити перешкоду.", size=10, color=INK, anchor="start"))

    return render(os.path.join(IMG_DIR, "decision-cost-matrix.svg"), w, h, *frags)


def fig_temporal_filter_and_hysteresis():
    """Фігура 3: Часова фільтрація (Leaky Integrator) та гістерезис."""
    w, h = 880, 500
    frags = []

    frags.append(text(w / 2, 28, "Ланцюг обробки: від сирого шуму до стабільного стану", size=15, bold=True))

    x0, gw = 90, 740
    t_end = x0 + gw

    # Графік 1: Сирий Softmax (P_raw) та Фільтрований сигнал (S_filtered)
    g1_y0 = 230
    g1_h = 145
    g1_y1 = g1_y0 - g1_h

    # Сітка графіка 1
    frags.append(rect(x0, g1_y1, gw, g1_h, fill="#fafbfc", stroke="#d0d7de", sw=1.0))
    frags.append(line(x0, g1_y0, t_end, g1_y0, color=LINE, sw=1.5))
    frags.append(line(x0, g1_y1, x0, g1_y0, color=LINE, sw=1.5))

    # Горизонтальні рівні 0.0, 0.4 (H_off), 0.75 (H_on), 1.0
    y_hon = g1_y0 - 0.75 * g1_h
    y_hoff = g1_y0 - 0.40 * g1_h

    frags.append(line(x0, y_hon, t_end, y_hon, color=POS, sw=1.2, dash="4,4"))
    frags.append(line(x0, y_hoff, t_end, y_hoff, color=FIELD, sw=1.2, dash="4,4"))

    frags.append(text(x0 - 10, g1_y0 + 4, "0.0", size=10, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, y_hoff + 4, "H_off (0.4)", size=10, color=FIELD, bold=True, anchor="end"))
    frags.append(text(x0 - 10, y_hon + 4, "H_on (0.75)", size=10, color=POS, bold=True, anchor="end"))
    frags.append(text(x0 - 10, g1_y1 + 4, "1.0", size=10, color=MUTED, anchor="end"))

    # Сирі точки P_raw
    raw_bars = [
        (105, 0.1), (120, 0.85), (135, 0.15),
        (170, 0.1), (190, 0.2), (210, 0.8), (230, 0.9), (250, 0.88), (270, 0.95),
        (290, 0.35),
        (310, 0.92), (330, 0.89), (350, 0.85), (370, 0.78),
        (400, 0.25), (420, 0.15), (440, 0.05),
        (480, 0.1), (500, 0.65), (520, 0.12), (550, 0.05), (580, 0.1), (610, 0.05), (640, 0.1), (670, 0.05), (710, 0.05)
    ]
    for rx, rval in raw_bars:
        frags.append(circle(rx, g1_y0 - rval * g1_h, 3.0, fill="#cbd5e1", stroke="#64748b", sw=1.0))
        frags.append(line(rx, g1_y0, rx, g1_y0 - rval * g1_h, color="#e2e8f0", sw=1.0))

    # Фільтрована крива Leaky Integrator S[k]
    filtered_pts = [
        (90, 0.0), (115, 0.05), (120, 0.25), (135, 0.15), (155, 0.08),
        (190, 0.10), (210, 0.30), (230, 0.55), (250, 0.72), (260, 0.78), # перетин H_on біля x=260
        (270, 0.85), (290, 0.70), (310, 0.82), (330, 0.87), (350, 0.86), (370, 0.81),
        (400, 0.62), (420, 0.45), (435, 0.38), # перетин H_off біля x=435
        (450, 0.25), (480, 0.12), (500, 0.28), (520, 0.18), (550, 0.08), (610, 0.05), (760, 0.02)
    ]
    filt_d = ["M %.1f,%.1f" % (filtered_pts[0][0], g1_y0 - filtered_pts[0][1] * g1_h)]
    for px, py in filtered_pts[1:]:
        filt_d.append("L %.1f,%.1f" % (px, g1_y0 - py * g1_h))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(filt_d), NEG))

    # Підписи до кривих
    frags.append(text(145, 68, "Хибний спалах (1 кадр)", size=10, color=MUTED))
    frags.append(arrow(145, 74, 120, 95, color=MUTED, sw=1.2))

    frags.append(text(290, 218, "Провал на 1 кадр", size=10, color=MUTED))
    frags.append(arrow(290, 208, 290, 185, color=MUTED, sw=1.2))

    frags.append(text(680, g1_y0 - 0.85 * g1_h, "— — Сирий Softmax P[k]", size=11, color="#64748b"))
    frags.append(text(680, g1_y0 - 0.65 * g1_h, "—— Фільтр впевненості S[k]", size=11, color=NEG, bold=True))

    # Точки перемикання порогів
    frags.append(circle(260, y_hon, 5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(260, y_hon - 14, "Активація (S > H_on)", size=10, color=POS, bold=True))

    frags.append(circle(435, y_hoff, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    frags.append(text(435, y_hoff - 14, "Скидання (S < H_off)", size=10, color=FIELD, bold=True))

    # Графік 2: Стан автомата рішень
    g2_y0 = 390
    g2_h = 75
    g2_y1 = g2_y0 - g2_h

    frags.append(rect(x0, g2_y1, gw, g2_h, fill="#fafbfc", stroke="#d0d7de", sw=1.0))
    frags.append(line(x0, g2_y0, t_end, g2_y0, color=LINE, sw=1.5))
    frags.append(line(x0, g2_y1, x0, g2_y0, color=LINE, sw=1.5))

    frags.append(text(x0 - 10, g2_y0 - 10, "0 (Норма)", size=10, color=FIELD, bold=True, anchor="end"))
    frags.append(text(x0 - 10, g2_y1 + 20, "1 (Тривога)", size=10, color=POS, bold=True, anchor="end"))

    # Стан: 0 до 260, потім 1 від 260 до 435, потім 0 після 435
    state_path = [
        "M %.1f,%.1f" % (x0, g2_y0 - 10),
        "L 260,%.1f" % (g2_y0 - 10),
        "L 260,%.1f" % (g2_y1 + 18),
        "L 435,%.1f" % (g2_y1 + 18),
        "L 435,%.1f" % (g2_y0 - 10),
        "L %.1f,%.1f" % (t_end, g2_y0 - 10)
    ]
    frags.append(rect(260, g2_y1 + 18, 175, g2_h - 28, fill="#fee2e2", stroke="none"))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (" ".join(state_path), POS))

    # Вертикальні лінії зв'язку між графіками
    frags.append(line(260, y_hon + 8, 260, g2_y1 + 15, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(435, y_hoff + 8, 435, g2_y1 + 15, color=FIELD, sw=1.5, dash="3,3"))

    # Позначення зони утримання стану
    frags.append(text(347, g2_y1 + 42, "Стабільне рішення: ГАЛЬМУВАННЯ", size=11, color=POS, bold=True))
    frags.append(text(347, g2_y1 + 58, "(жодного брязкоту на шумі)", size=10, color=MUTED))

    # Загальна вісь часу знизу
    frags.append(text(t_end - 20, g2_y0 + 25, "Час t (кадри) →", size=12, bold=True, anchor="end"))
    frags.append(text(120, g2_y0 + 25, "Спалах знехтувано", size=10, color=FIELD))

    return render(os.path.join(IMG_DIR, "temporal-filter-and-hysteresis.svg"), w, h, *frags)


def main():
    fig_calibration_and_overconfidence()
    fig_decision_cost_matrix()
    fig_temporal_filter_and_hysteresis()
    print("Figures generated successfully in %s" % IMG_DIR)


if __name__ == "__main__":
    main()
