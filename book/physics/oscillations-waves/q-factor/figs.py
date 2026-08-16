# -*- coding: utf-8 -*-
"""
Генератор фігур для теми «Добротність» (q-factor).
Вивід: SVG-файли у теці ./img/
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def fig_ringdown_q():
    """Фігура 1: Згасання коливань для високої та низької добротності."""
    w, h = 760, 400
    frags = []

    frags.append(text(w / 2, 25, "Вільне загасання коливань та обвідна енергії для різної добротності Q", size=16, bold=True))

    # Схема 1: Висока добротність Q = 15 (ліва частина)
    frags.append(rect(20, 55, 350, 325, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(195, 80, "Висока добротність (Q = 15)", size=14, color=POS, bold=True))

    ox1, oy1 = 50, 220
    frags.append(arrow(ox1, oy1 + 110, ox1, oy1 - 120, color=LINE, sw=1.2))
    frags.append(arrow(ox1, oy1, ox1 + 305, oy1, color=LINE, sw=1.2))
    frags.append(text(ox1 - 10, oy1 - 110, "x(t)", size=11, color=INK, anchor="end"))
    frags.append(text(ox1 + 295, oy1 + 18, "Час t", size=11, color=INK))

    # Побудова синусоїди з експоненційним загасанням Q = 15
    pts_top1 = []
    pts_bot1 = []
    pts_wave1 = []
    Q1 = 15.0
    omega1 = 0.25
    A0 = 90.0

    for px in range(0, 280, 2):
        t = float(px)
        env = A0 * math.exp(-math.pi * (t / 40.0) / Q1)
        val = env * math.cos(omega1 * t)
        pts_wave1.append("%.1f,%.1f" % (ox1 + px, oy1 - val))
        pts_top1.append("%.1f,%.1f" % (ox1 + px, oy1 - env))
        pts_bot1.append("%.1f,%.1f" % (ox1 + px, oy1 + env))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % (" ".join(pts_top1), MUTED))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % (" ".join(pts_bot1), MUTED))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_wave1), POS))

    frags.append(text(270, 115, "e⁻⁽ⁿⁿ ᶠ⁰ ᵗ ∕ 𝑸⁾", size=12, color=MUTED, italic=True))
    frags.append(textbox(195, 345, "Багато періодів коливань\nповільна втрата енергії за цикл", size=11, pad=6, fill="#fdecea", stroke=POS)[0])

    # Схема 2: Низька добротність Q = 3 (права частина)
    frags.append(rect(390, 55, 350, 325, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(565, 80, "Низька добротність (Q = 3)", size=14, color=NEG, bold=True))

    ox2, oy2 = 420, 220
    frags.append(arrow(ox2, oy2 + 110, ox2, oy2 - 120, color=LINE, sw=1.2))
    frags.append(arrow(ox2, oy2, ox2 + 305, oy2, color=LINE, sw=1.2))
    frags.append(text(ox2 - 10, oy2 - 110, "x(t)", size=11, color=INK, anchor="end"))
    frags.append(text(ox2 + 295, oy2 + 18, "Час t", size=11, color=INK))

    pts_top2 = []
    pts_bot2 = []
    pts_wave2 = []
    Q2 = 3.0

    for px in range(0, 280, 2):
        t = float(px)
        env = A0 * math.exp(-math.pi * (t / 40.0) / Q2)
        val = env * math.cos(omega1 * t)
        pts_wave2.append("%.1f,%.1f" % (ox2 + px, oy2 - val))
        pts_top2.append("%.1f,%.1f" % (ox2 + px, oy2 - env))
        pts_bot2.append("%.1f,%.1f" % (ox2 + px, oy2 + env))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % (" ".join(pts_top2), MUTED))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' % (" ".join(pts_bot2), MUTED))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_wave2), NEG))

    frags.append(text(580, 155, "Швидкий згасаючий спад", size=12, color=MUTED, italic=True))
    frags.append(textbox(565, 345, "Лише 2-3 згасаючі гойдання\nшвидка дисипація енергії", size=11, pad=6, fill="#eaf0fd", stroke=NEG)[0])

    render(os.path.join(IMG_DIR, 'ringdown-q.svg'), w, h, *frags)

def fig_resonance_peak_q():
    """Фігура 2: Амплітудно-частотна характеристика та смуга 3 дБ для різних Q."""
    w, h = 760, 440
    frags = []

    frags.append(text(w / 2, 25, "Резонансна крива, гострота піка та смуга пропускання Δf = f₀ / Q", size=16, bold=True))

    ox, oy = 80, 370
    pw, ph = 630, 310

    frags.append(arrow(ox, oy, ox + pw + 20, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - ph - 20, color=LINE, sw=1.5))

    frags.append(text(ox + pw + 15, oy + 22, "Частота f", size=12, bold=True))
    frags.append(text(ox - 25, oy - ph - 10, "Амплітуда A(f)", size=12, bold=True))

    f0_x = ox + pw * 0.45
    frags.append(line(f0_x, oy, f0_x, oy - ph + 10, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(text(f0_x, oy + 22, "f₀ (Резонанс)", size=12, color=INK, bold=True))

    def calc_curve(Q_val, scale_h):
        pts = []
        for x in range(30, pw, 2):
            f_ratio = (x) / (pw * 0.45)
            denom = math.sqrt((1.0 - f_ratio**2)**2 + (f_ratio / Q_val)**2)
            amp = (1.0 / denom) * scale_h
            y_val = oy - min(amp, ph - 20)
            pts.append("%.1f,%.1f" % (ox + x, y_val))
        return " ".join(pts)

    curve_high = calc_curve(10.0, 28.0)
    curve_mid  = calc_curve(4.0, 28.0)
    curve_low  = calc_curve(1.5, 28.0)

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (curve_high, POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (curve_mid, FIELD))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (curve_low, NEG))

    # Смуга 3 дБ для Q = 10
    peak_y = oy - 280.0
    h3db_y = oy - 280.0 * 0.707

    f1_x = f0_x - 30.0
    f2_x = f0_x + 30.0

    frags.append(line(ox, h3db_y, ox + pw, h3db_y, color=MUTED, sw=1.0, dash="2 2"))
    frags.append(text(ox - 35, h3db_y + 4, "A_max / √2", size=10, color=MUTED))

    frags.append(line(f1_x, oy, f1_x, h3db_y, color=POS, sw=1.2, dash="3 3"))
    frags.append(line(f2_x, oy, f2_x, h3db_y, color=POS, sw=1.2, dash="3 3"))
    frags.append(arrow(f0_x, h3db_y, f1_x, h3db_y, color=POS, sw=1.5))
    frags.append(arrow(f0_x, h3db_y, f2_x, h3db_y, color=POS, sw=1.5))
    frags.append(text(f0_x, h3db_y - 10, "Смуга Δf = f₀ / Q", size=11, color=POS, bold=True))

    # Легенда
    frags.append(rect(480, 70, 220, 115, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(line(495, 90, 525, 90, color=POS, sw=2.5))
    frags.append(text(535, 94, "Q = 10 (Висока, вузька Δf)", size=11, anchor="start", bold=True))

    frags.append(line(495, 120, 525, 120, color=FIELD, sw=2.0))
    frags.append(text(535, 124, "Q = 4 (Середня)", size=11, anchor="start"))

    frags.append(line(495, 150, 525, 150, color=NEG, sw=2.0))
    frags.append(text(535, 154, "Q = 1.5 (Низька, широка Δf)", size=11, anchor="start"))

    render(os.path.join(IMG_DIR, 'resonance-peak-q.svg'), w, h, *frags)

def fig_q_zoo():
    """Фігура 3: Двовимірна логарифмічна шкала добротностей у фізиці та техніці."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 25, "Шкала добротностей Q у фізичних та інженерних системах", size=16, bold=True))

    ox, oy = 60, 340
    bar_w = 640

    frags.append(arrow(ox, oy, ox + bar_w + 30, oy, color=LINE, sw=2.0))
    frags.append(text(ox + bar_w + 25, oy + 25, "Добротність Q (логарифмічна шкала)", size=12, bold=True))

    ticks = [
        (0, "1", "10⁰"),
        (1, "10", "10¹"),
        (2, "100", "10²"),
        (3, "1k", "10³"),
        (4, "10k", "10⁴"),
        (5, "100k", "10⁵"),
        (6, "1M", "10⁶"),
        (7, "10M", "10⁷"),
        (8, "100M", "10⁸"),
        (9, "1G", "10⁹"),
        (10, "10G", "10¹⁰"),
        (11, "100G", "10¹¹"),
    ]

    for idx, label_num, label_exp in ticks:
        x_pos = ox + (idx / 11.0) * bar_w
        frags.append(line(x_pos, oy - 6, x_pos, oy + 6, color=LINE, sw=1.5))
        frags.append(text(x_pos, oy + 22, label_exp, size=11, color=INK))

    items = [
        ("Автомобільний\nамортизатор", 0.3, 85, NEG, "#eaf0fd"),
        ("LC-контур\nрадіоприймача", 2.2, 175, FIELD, "#e8f8f0"),
        ("Сталевий\nкамертон", 3.4, 265, POS, "#fdecea"),
        ("Кварцовий\nрезонансор", 5.2, 105, POS, "#fdecea"),
        ("MEMS-вакуумний\nрезонатор", 6.3, 195, FIELD, "#e8f8f0"),
        ("Нап.провідниковий\nмікрорезонатор", 8.8, 115, NEG, "#eaf0fd"),
        ("Оптичний резонатор\nФабри-Перо", 10.4, 215, POS, "#fdecea"),
    ]

    for name, exp_val, y_top, col, fill_col in items:
        x_pos = ox + (exp_val / 11.0) * bar_w
        frags.append(line(x_pos, oy, x_pos, y_top + 40, color=col, sw=1.5, dash="3 3"))
        frags.append(circle(x_pos, oy, 4, fill=col, stroke=col))
        box_el, bw, bh = textbox(x_pos, y_top, name, size=10, pad=5, fill=fill_col, stroke=col)
        frags.append(box_el)

    render(os.path.join(IMG_DIR, 'q-zoo.svg'), w, h, *frags)

def fig_phase_slope_q():
    """Фігура 4: Нахил фази поблизу резонансу dφ/dω = 2Q / ω₀."""
    w, h = 760, 380
    frags = []

    frags.append(text(w / 2, 25, "Фазово-частотна характеристика φ(f) та крутизна переходу", size=16, bold=True))

    ox, oy = 80, 200
    pw, ph = 620, 260

    frags.append(arrow(ox, oy + 120, ox, oy - 130, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox + pw + 20, oy, color=LINE, sw=1.5))

    frags.append(text(ox + pw + 15, oy + 22, "Частота f", size=12, bold=True))
    frags.append(text(ox - 25, oy - 120, "Фаза φ", size=12, bold=True))

    frags.append(text(ox - 20, oy - 90, "+90°", size=10, color=MUTED))
    frags.append(line(ox - 5, oy - 90, ox + pw, oy - 90, color=MUTED, sw=1.0, dash="2 2"))
    frags.append(text(ox - 20, oy + 90, "−90°", size=10, color=MUTED))
    frags.append(line(ox - 5, oy + 90, ox + pw, oy + 90, color=MUTED, sw=1.0, dash="2 2"))

    f0_x = ox + pw * 0.5
    frags.append(line(f0_x, oy - 120, f0_x, oy + 120, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(text(f0_x, oy + 22, "f₀ (φ = 0)", size=12, color=INK, bold=True))

    def calc_phase_curve(Q_val):
        pts = []
        for x in range(30, pw, 2):
            f_rat = (x) / (pw * 0.5)
            if abs(1.0 - f_rat**2) < 1e-6:
                phase_rad = -math.pi / 2.0
            else:
                phase_rad = -math.atan((f_rat / Q_val) / (1.0 - f_rat**2))
                if f_rat > 1.0:
                    phase_rad -= math.pi
            y_val = oy - (phase_rad + math.pi/2.0) * (180.0 / math.pi) * 1.0
            pts.append("%.1f,%.1f" % (ox + x, y_val))
        return " ".join(pts)

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (calc_phase_curve(15.0), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (calc_phase_curve(3.0), NEG))

    frags.append(line(f0_x - 40, oy - 90, f0_x + 40, oy + 90, color=POS, sw=1.5, dash="4 3"))
    frags.append(textbox(f0_x + 130, oy - 55, "Крутизна нахилу:\ndφ/dω = 2Q / ω₀\n(висока стійкість частоти)", size=11, pad=6, fill="#fdecea", stroke=POS)[0])

    frags.append(textbox(f0_x - 140, oy + 65, "Пологий перехід фази\n(низьке Q)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)[0])

    render(os.path.join(IMG_DIR, 'phase-slope-q.svg'), w, h, *frags)

if __name__ == '__main__':
    fig_ringdown_q()
    fig_resonance_peak_q()
    fig_q_zoo()
    fig_phase_slope_q()
    print("Всі фігури для q-factor успішно згенеровано.")
