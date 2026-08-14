# -*- coding: utf-8 -*-
"""Фігури до теми «Хроматична дисперсія у волокні».
Запуск: python figs.py  → створює SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Кольори
BLUE_WAVE  = "#2457d6"  # коротка хвиля (синя)
RED_WAVE   = "#c0392b"  # довга хвиля (червона)
GREEN_WAVE = "#27ae60"  # середня хвиля (зелена)
FIBER_BG   = "#f4f6f8"
FIBER_CORE = "#e2e8f0"
FIBER_LINE = "#64748b"

def fig_pulse_broadening():
    W, H = 820, 380
    f = [text(W / 2, 25, "Розпливання оптичного імпульсу через хроматичну дисперсію", size=15, bold=True)]

    # 1. Вхідний вузький імпульс
    f.append(rect(20, 50, 220, 290, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(130, 75, "Вхідний імпульс (z = 0)", size=13, bold=True, color=INK))
    
    # Вхідний спектр
    f.append(line(40, 180, 220, 180, color=LINE, sw=1.5))
    f.append(line(130, 180, 130, 100, color=INK, sw=2))
    # Спектральні складові
    f.append(arrow(130, 180, 90, 120, color=BLUE_WAVE, sw=2))
    f.append(arrow(130, 180, 130, 105, color=GREEN_WAVE, sw=2))
    f.append(arrow(130, 180, 170, 120, color=RED_WAVE, sw=2))
    f.append(text(85, 110, "λ₁ (синя)", size=10, bold=True, color=BLUE_WAVE))
    f.append(text(130, 95, "λ₀ (зелена)", size=10, bold=True, color=GREEN_WAVE))
    f.append(text(175, 110, "λ₂ (червона)", size=10, bold=True, color=RED_WAVE))
    f.append(text(130, 205, "Вузька часова ширина Δt₀", size=11, bold=True, color=INK))
    f.append(text(130, 225, "Усі кольори випромінені", size=10, color=MUTED))
    f.append(text(130, 240, "в один момент часу", size=10, color=MUTED))

    # Волоконна лінія в центрі
    f.append(rect(250, 160, 320, 70, fill=FIBER_CORE, stroke=FIBER_LINE, sw=1.5, rx=6))
    f.append(text(410, 180, "Одномодове волокно (довжина L)", size=12, bold=True, color=INK))
    f.append(text(410, 200, "Швидкість v_g(λ) залежить від довжини хвилі", size=11, italic=True, color=MUTED))
    f.append(arrow(225, 195, 245, 195, color=INK, sw=2))
    f.append(arrow(575, 195, 595, 195, color=INK, sw=2))

    # 2. Вихідний розширений імпульс
    f.append(rect(580, 50, 220, 290, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(690, 75, "Вихідний імпульс (z = L)", size=13, bold=True, color=POS))

    # Поділ складових у часі
    f.append(line(600, 180, 780, 180, color=LINE, sw=1.5))
    f.append(line(630, 180, 630, 130, color=BLUE_WAVE, sw=2))
    f.append(line(690, 180, 690, 115, color=GREEN_WAVE, sw=2))
    f.append(line(750, 180, 750, 130, color=RED_WAVE, sw=2))
    f.append(arrow(600, 165, 780, 165, color=POS, sw=1.5))
    f.append(text(630, 120, "λ₁ долітає першою", size=10, bold=True, color=BLUE_WAVE))
    f.append(text(750, 120, "λ₂ відстає", size=10, bold=True, color=RED_WAVE))

    f.append(text(690, 205, "Розширений імпульс Δt", size=11, bold=True, color=POS))
    f.append(text(690, 225, "Δt = |D| · Δλ · L", size=12, bold=True, color=POS))
    f.append(text(690, 255, "Сусідні імпульси перекриваються", size=10, bold=True, color=POS))
    f.append(text(690, 270, "→ Міжсимвольна інтерференція", size=10, color=POS))

    return render(os.path.join(IMG, "pulse-broadening.svg"), W, H, *f)

def fig_dispersion_curves():
    W, H = 820, 420
    f = [text(W / 2, 25, "Залежність коефіцієнта хроматичної дисперсії D від довжини хвилі", size=15, bold=True)]

    # Вісі графіку
    ox, oy = 90, 340
    gw, gh = 680, 270
    f.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke=MUTED, sw=1, rx=4))

    # Лінія нульової дисперсії D = 0
    y_zero = oy - gh / 2
    f.append(line(ox, y_zero, ox + gw, y_zero, color=MUTED, sw=1.5, dash="4,4"))
    f.append(text(ox - 15, y_zero + 4, "0", size=11, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - gh + 20, "+D (пс/нм·км)", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(ox - 15, oy - 15, "−D (пс/нм·км)", size=11, bold=True, color=NEG, anchor="end"))

    # Позначки довжин хвиль (1200, 1310, 1480, 1550, 1600 нм)
    def nm_to_x(nm):
        return ox + 40 + (nm - 1200) * (gw - 80) / 400

    # Вертикальні лінії вікон
    x_1310 = nm_to_x(1310)
    x_1550 = nm_to_x(1550)
    f.append(line(x_1310, oy - gh, x_1310, oy, color=FIELD, sw=1, dash="3,3"))
    f.append(line(x_1550, oy - gh, x_1550, oy, color=FIELD, sw=1, dash="3,3"))
    f.append(text(x_1310, oy + 20, "1310 нм (O-band)", size=11, bold=True, color=FIELD))
    f.append(text(x_1550, oy + 20, "1550 нм (C-band)", size=11, bold=True, color=FIELD))

    # Складові для SSMF (G.652): D_M та D_W
    pts_ssmf = []
    pts_dm = []
    pts_dw = []
    pts_nzdsf = []

    for nm in range(1200, 1601, 10):
        x = nm_to_x(nm)
        dm_val = 0.08 * (nm - 1270)
        dw_val = -5.0
        d_ssmf = dm_val + dw_val
        d_nzdsf = 0.05 * (nm - 1480)

        y_ssmf = y_zero - d_ssmf * 3.8
        y_dm = y_zero - dm_val * 3.8
        y_dw = y_zero - dw_val * 3.8
        y_nzdsf = y_zero - d_nzdsf * 3.8

        pts_ssmf.append((x, y_ssmf))
        pts_dm.append((x, y_dm))
        pts_dw.append((x, y_dw))
        pts_nzdsf.append((x, y_nzdsf))

    def poly_str(pts):
        return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)

    f.append(f'<polyline points="{poly_str(pts_dm)}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5,3"/>')
    f.append(f'<polyline points="{poly_str(pts_dw)}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="2,2"/>')
    f.append(f'<polyline points="{poly_str(pts_ssmf)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    f.append(f'<polyline points="{poly_str(pts_nzdsf)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Позначки точок та підписи
    y_1550_ssmf = y_zero - 17 * 3.8
    f.append(circle(x_1550, y_1550_ssmf, 4, fill=POS, stroke=POS))
    f.append(text(x_1550 + 10, y_1550_ssmf - 10, "D ≈ +17 пс/(нм·км)", size=11, bold=True, color=POS, anchor="start"))

    f.append(circle(x_1310, y_zero, 4, fill=POS, stroke=POS))
    f.append(text(x_1310 - 10, y_zero - 12, "D = 0 при 1310 нм", size=11, bold=True, color=POS, anchor="end"))

    # Легенда
    f.append(rect(ox + 20, oy - gh + 15, 340, 90, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(line(ox + 30, oy - gh + 35, ox + 60, oy - gh + 35, color=POS, sw=2.5))
    f.append(text(ox + 70, oy - gh + 39, "Стандартне волокно G.652 (SMF-28)", size=11, bold=True, color=INK, anchor="start"))

    f.append(line(ox + 30, oy - gh + 55, ox + 60, oy - gh + 55, color=FIELD, sw=2.5))
    f.append(text(ox + 70, oy - gh + 59, "Зміщена дисперсія G.655 (NZDSF)", size=11, bold=True, color=INK, anchor="start"))

    line_dm = line(ox + 30, oy - gh + 75, ox + 60, oy - gh + 75, color=MUTED, sw=1.5, dash="5,3")
    f.append(line_dm)
    f.append(text(ox + 70, oy - gh + 79, "Матеріальна складова D_M", size=10, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "dispersion-curves.svg"), W, H, *f)

def fig_dispersion_compensation():
    W, H = 820, 360
    f = [text(W / 2, 25, "Схеми компенсації хроматичної дисперсії у оптичних лініях", size=15, bold=True)]

    # 1. Оптична компенсація катушкою DCF
    f.append(rect(20, 50, 780, 130, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(400, 72, "Пасивна оптична компенсація волокном DCF (Dispersion Compensating Fiber)", size=13, bold=True, color=INK))

    # Блоки: Передавач Tx -> SSMF (+D) -> DCF (-D) -> Приймач Rx
    f.append(rect(40, 95, 90, 60, fill="#ebf8ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(85, 130, "Передавач\nTx", size=11, bold=True, color=NEG))

    f.append(arrow(130, 125, 175, 125, color=INK, sw=1.8))

    f.append(rect(175, 95, 200, 60, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(275, 120, "Магістраль G.652 (SMF)", size=11, bold=True, color=POS))
    f.append(text(275, 138, "L = 80 км, D = +17 пс/(нм·км)", size=10, color=POS))

    f.append(arrow(375, 125, 420, 125, color=INK, sw=1.8))

    f.append(rect(420, 95, 210, 60, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(525, 120, "Модуль компенсації DCF", size=11, bold=True, color=FIELD))
    f.append(text(525, 138, "L_dcf = 13.6 км, D = -100 пс/(нм·км)", size=10, color=FIELD))

    f.append(arrow(630, 125, 675, 125, color=INK, sw=1.8))

    f.append(rect(675, 95, 100, 60, fill="#ebf8ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(725, 130, "Приймач\nRx", size=11, bold=True, color=NEG))

    # 2. Цифрова компенсація DSP у когерентному приймачі
    f.append(rect(20, 200, 780, 130, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(400, 222, "Сучасна цифрова компенсація у DSP (Когерентні системи 100G+)", size=13, bold=True, color=FIELD))

    f.append(rect(40, 245, 90, 60, fill="#ebf8ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(85, 280, "Передавач\nTx 100G+", size=11, bold=True, color=NEG))

    f.append(arrow(130, 275, 210, 275, color=INK, sw=1.8))

    f.append(rect(210, 245, 240, 60, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(330, 270, "Магістральне волокно G.652", size=11, bold=True, color=POS))
    f.append(text(330, 288, "Прямий прогін > 1000 км без DCF!", size=10, bold=True, color=POS))

    f.append(arrow(450, 275, 520, 275, color=INK, sw=1.8))

    f.append(rect(520, 245, 255, 60, fill="#f0fff4", stroke=FIELD, sw=2, rx=6))
    f.append(text(647, 268, "Когерентний Rx + DSP", size=11, bold=True, color=FIELD))
    f.append(text(647, 288, "Цифровий FIR-фільтр інвертує D", size=10, bold=True, color=FIELD))

    return render(os.path.join(IMG, "dispersion-compensation.svg"), W, H, *f)

if __name__ == "__main__":
    fig_pulse_broadening()
    fig_dispersion_curves()
    fig_dispersion_compensation()
    print("Figures generated successfully.")
