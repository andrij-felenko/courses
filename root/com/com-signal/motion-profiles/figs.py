# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Профілі руху» (motion-profiles)."""

import sys
import os
import math

# Підключення svgkit із кореня репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Додаткові кольори палітри
ACC_POS = "#c0392b"   # Прискорення (червоний)
ACC_NEG = "#2457d6"   # Сповільнення (синій)
VEL_COL = "#27ae60"   # Швидкість (зелений)
POS_COL = "#8e44ad"   # Положення (фіолетовий)
JERK_COL = "#d35400"  # Ривок (помаранчевий)
GRID_COL = "#e2e8f0"  # Сітка


def polyline(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>'
            % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), color, sw, d))


def axis_arrow(x1, y1, x2, y2, color=INK, sw=1.4):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


# ── 1. Порівняння трапеції та S-кривої (trapezoid-vs-scurve.svg) ──────────────
def fig_trapezoid_vs_scurve():
    W, H = 840, 520
    p = []

    # Заголовок колонок
    t1, _, _ = textbox(225, 26, "Трапецеподібний профіль (a = const)", size=13, bold=True, fill="#fee2e2", stroke=POS)
    t2, _, _ = textbox(635, 26, "S-крива (обмежений ривок j = const)", size=13, bold=True, fill="#dcfce7", stroke=FIELD)
    p.append(t1)
    p.append(t2)

    # 4 графіки для кожної колонки: Положення s(t), Швидкість v(t), Прискорення a(t), Ривок j(t)
    row_ys = [120, 225, 335, 445]
    labels = [
        ("s(t)", "Положення", POS_COL),
        ("v(t)", "Швидкість", VEL_COL),
        ("a(t)", "Прискорення", ACC_POS),
        ("j(t)", "Ривок", JERK_COL)
    ]

    col_w = 330
    col1_x = 75
    col2_x = 485

    # Сітка та осі
    for i, (sym, name, col) in enumerate(labels):
        cy = row_ys[i]
        
        # Підписи величин зліва
        p.append(text(35, cy - 18, sym, size=13, color=col, bold=True, anchor="middle"))
        p.append(text(35, cy + 2, name, size=9, color=MUTED, anchor="middle"))

        for cx in (col1_x, col2_x):
            # Нульова вісь
            p.append(line(cx, cy, cx + col_w, cy, color=GRID_COL, sw=1.0))
            # Вісь Y та X
            p.append(axis_arrow(cx, cy + 32, cx, cy - 42, color=INK, sw=1.2))
            p.append(axis_arrow(cx, cy, cx + col_w + 12, cy, color=INK, sw=1.2))
            p.append(text(cx + col_w + 10, cy + 14, "t", size=11, color=MUTED, italic=True))

    # --- Колонка 1: Трапеція ---
    w_t = col_w - 20
    t1_px = col1_x + w_t * 0.3
    t2_px = col1_x + w_t * 0.7
    t3_px = col1_x + w_t

    # 1. Положення s(t)
    s_pts = []
    for step in range(101):
        tau = step / 100.0
        x = col1_x + tau * w_t
        if tau <= 0.3:
            s_val = 0.5 * (tau / 0.3) ** 2 * 0.3
        elif tau <= 0.7:
            s_val = 0.15 + (tau - 0.3) * 1.0
        else:
            t_d = (tau - 0.7) / 0.3
            s_val = 0.55 + 0.45 * (1.0 - (1.0 - t_d) ** 2)
        y = row_ys[0] - s_val * 32.0 / 1.0
        s_pts.append((x, y))
    p.append(polyline(s_pts, POS_COL, sw=2.2))

    # 2. Швидкість v(t): трапеція
    v_pts = [
        (col1_x, row_ys[1]),
        (t1_px, row_ys[1] - 32),
        (t2_px, row_ys[1] - 32),
        (t3_px, row_ys[1])
    ]
    p.append(polyline(v_pts, VEL_COL, sw=2.4))

    # 3. Прискорення a(t): сходинки
    a_pts = [
        (col1_x, row_ys[2] - 30),
        (t1_px, row_ys[2] - 30),
        (t1_px, row_ys[2]),
        (t2_px, row_ys[2]),
        (t2_px, row_ys[2] + 30),
        (t3_px, row_ys[2] + 30),
        (t3_px, row_ys[2])
    ]
    p.append(polyline(a_pts, ACC_POS, sw=2.2))
    p.append(line(t1_px, row_ys[2] - 30, t1_px, row_ys[2], color=ACC_POS, sw=1.5, dash="2,2"))
    p.append(line(t2_px, row_ys[2], t2_px, row_ys[2] + 30, color=ACC_POS, sw=1.5, dash="2,2"))

    # 4. Ривок j(t): дельта-імпульси (нескінченний ривок)
    p.append(arrow(col1_x + 2, row_ys[3], col1_x + 2, row_ys[3] - 36, color=JERK_COL, sw=2.2))
    p.append(arrow(t1_px, row_ys[3], t1_px, row_ys[3] + 36, color=JERK_COL, sw=2.2))
    p.append(arrow(t2_px, row_ys[3], t2_px, row_ys[3] + 36, color=JERK_COL, sw=2.2))
    p.append(arrow(t3_px, row_ys[3], t3_px, row_ys[3] - 36, color=JERK_COL, sw=2.2))
    p.append(text(col1_x + 18, row_ys[3] - 22, "+inf", size=11, color=JERK_COL, bold=True))
    p.append(text(t1_px + 14, row_ys[3] + 24, "-inf", size=11, color=JERK_COL, bold=True))
    p.append(text(t2_px + 14, row_ys[3] + 24, "-inf", size=11, color=JERK_COL, bold=True))
    p.append(text(t3_px - 18, row_ys[3] - 22, "+inf", size=11, color=JERK_COL, bold=True))

    p.append(text(col1_x + w_t * 0.5, row_ys[3] + 32, "Удари та вібрація механіки", size=11, color=POS, bold=True, anchor="middle"))

    # --- Колонка 2: S-крива ---
    s_pts2 = []
    v_pts2 = []
    a_pts2 = []
    j_pts2 = []

    for step in range(121):
        tau = step / 120.0
        x = col2_x + tau * w_t
        if tau < 0.1:
            j = 1.0
            a = tau / 0.1
        elif tau < 0.2:
            j = 0.0
            a = 1.0
        elif tau < 0.3:
            j = -1.0
            a = 1.0 - (tau - 0.2) / 0.1
        elif tau < 0.7:
            j = 0.0
            a = 0.0
        elif tau < 0.8:
            j = -1.0
            a = -(tau - 0.7) / 0.1
        elif tau < 0.9:
            j = 0.0
            a = -1.0
        else:
            j = 1.0
            a = -1.0 + (tau - 0.9) / 0.1
        
        if tau < 0.1:
            v = 0.5 * (tau / 0.1) ** 2 * 0.25
        elif tau < 0.2:
            v = 0.125 + ((tau - 0.1) / 0.1) * 0.25
        elif tau < 0.3:
            dt = (tau - 0.2) / 0.1
            v = 0.375 + (dt - 0.5 * dt ** 2) * 0.25
        elif tau < 0.7:
            v = 0.5
        elif tau < 0.8:
            dt = (tau - 0.7) / 0.1
            v = 0.5 - 0.5 * dt ** 2 * 0.25
        elif tau < 0.9:
            dt = (tau - 0.8) / 0.1
            v = 0.5 - 0.125 - dt * 0.25
        else:
            dt = (tau - 0.9) / 0.1
            v = 0.125 - (dt - 0.5 * dt ** 2) * 0.25
        v_norm = v / 0.5

        s_y = row_ys[0] - (tau ** 2 * (3.0 - 2.0 * tau)) * 32.0
        s_pts2.append((x, s_y))
        v_pts2.append((x, row_ys[1] - v_norm * 32.0))
        a_pts2.append((x, row_ys[2] - a * 30.0))
        j_pts2.append((x, row_ys[3] - j * 28.0))

    p.append(polyline(s_pts2, POS_COL, sw=2.2))
    p.append(polyline(v_pts2, VEL_COL, sw=2.4))
    p.append(polyline(a_pts2, ACC_POS, sw=2.2))
    p.append(polyline(j_pts2, JERK_COL, sw=2.2))

    p.append(text(col2_x + w_t * 0.5, row_ys[3] + 32, "Плавний рух, нульова вібрація", size=11, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "trapezoid-vs-scurve.svg"), W, H, "".join(p))


# ── 2. Сім сегментів S-кривої (scurve-seven-segments.svg) ─────────────────────
def fig_scurve_seven_segments():
    W, H = 840, 480
    p = []

    tb_title, _, _ = textbox(W / 2, 24, "7-сегментна S-крива (повний цикл руху з обмеженням ривка)", size=14, bold=True, fill="#f1f5f9", stroke=LINE)
    p.append(tb_title)

    ox = 80
    graph_w = 700
    oy_j = 115
    oy_a = 230
    oy_v = 360

    seg_fracs = [0.10, 0.12, 0.10, 0.36, 0.10, 0.12, 0.10]
    seg_short = ["I", "II", "III", "IV", "V", "VI", "VII"]

    cum_x = [ox]
    cur = 0.0
    for f in seg_fracs:
        cur += f
        cum_x.append(ox + cur * graph_w)

    for i in range(8):
        x = cum_x[i]
        p.append(line(x, 60, x, 420, color="#e2e8f0", sw=1.2, dash="3,3"))
        if i < 7:
            cx = (cum_x[i] + cum_x[i+1]) / 2
            p.append(rect(cx - 16, 56, 32, 20, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
            p.append(text(cx, 70, seg_short[i], size=11, bold=True, color=INK, anchor="middle"))

    for oy, sym, title, col in [(oy_j, "j(t)", "Ривок (Jerk)", JERK_COL),
                                (oy_a, "a(t)", "Прискорення", ACC_POS),
                                (oy_v, "v(t)", "Швидкість", VEL_COL)]:
        p.append(line(ox, oy, ox + graph_w, oy, color="#cbd5e1", sw=1.0))
        p.append(axis_arrow(ox, oy + 42, ox, oy - 48, color=INK, sw=1.4))
        p.append(axis_arrow(ox, oy, ox + graph_w + 25, oy, color=INK, sw=1.4))
        p.append(text(ox - 38, oy - 12, sym, size=13, bold=True, color=col, anchor="middle"))
        p.append(text(ox - 38, oy + 6, title, size=9, color=MUTED, anchor="middle"))
        p.append(text(ox + graph_w + 20, oy + 15, "t", size=11, color=MUTED, italic=True))

    j_pts = [
        (cum_x[0], oy_j - 30), (cum_x[1], oy_j - 30),
        (cum_x[1], oy_j), (cum_x[2], oy_j),
        (cum_x[2], oy_j + 30), (cum_x[3], oy_j + 30),
        (cum_x[3], oy_j), (cum_x[4], oy_j),
        (cum_x[4], oy_j + 30), (cum_x[5], oy_j + 30),
        (cum_x[5], oy_j), (cum_x[6], oy_j),
        (cum_x[6], oy_j - 30), (cum_x[7], oy_j - 30),
        (cum_x[7], oy_j)
    ]
    p.append(polyline(j_pts, JERK_COL, sw=2.2))
    p.append(text(ox + 12, oy_j - 34, "+j_max", size=10, bold=True, color=JERK_COL))
    p.append(text(ox + 12, oy_j + 40, "-j_max", size=10, bold=True, color=JERK_COL))

    a_pts = [
        (cum_x[0], oy_a),
        (cum_x[1], oy_a - 35),
        (cum_x[2], oy_a - 35),
        (cum_x[3], oy_a),
        (cum_x[4], oy_a),
        (cum_x[5], oy_a + 35),
        (cum_x[6], oy_a + 35),
        (cum_x[7], oy_a)
    ]
    p.append(polyline(a_pts, ACC_POS, sw=2.4))
    p.append(text(ox + 12, oy_a - 38, "+a_max", size=10, bold=True, color=ACC_POS))
    p.append(text(ox + 12, oy_a + 44, "-a_max", size=10, bold=True, color=ACC_POS))

    v_curve = []
    n_pts = 140
    for idx in range(n_pts + 1):
        x = ox + (idx / n_pts) * graph_w
        if x < cum_x[1]:
            tau = (x - cum_x[0]) / (cum_x[1] - cum_x[0])
            v = 0.5 * tau ** 2 * 0.25
        elif x < cum_x[2]:
            tau = (x - cum_x[1]) / (cum_x[2] - cum_x[1])
            v = 0.125 + tau * 0.25
        elif x < cum_x[3]:
            tau = (x - cum_x[2]) / (cum_x[3] - cum_x[2])
            v = 0.375 + (tau - 0.5 * tau ** 2) * 0.25
        elif x < cum_x[4]:
            v = 0.5
        elif x < cum_x[5]:
            tau = (x - cum_x[4]) / (cum_x[5] - cum_x[4])
            v = 0.5 - 0.5 * tau ** 2 * 0.25
        elif x < cum_x[6]:
            tau = (x - cum_x[5]) / (cum_x[6] - cum_x[5])
            v = 0.375 - tau * 0.25
        else:
            tau = (x - cum_x[6]) / (cum_x[7] - cum_x[6])
            v = 0.125 - (tau - 0.5 * tau ** 2) * 0.25
        
        y = oy_v - (v / 0.5) * 55.0
        v_curve.append((x, y))
    
    p.append(polyline(v_curve, VEL_COL, sw=2.6))
    p.append(text(ox + 12, oy_v - 60, "v_max", size=10, bold=True, color=VEL_COL))

    p.append(text(cum_x[0], 438, "0", size=10, color=MUTED, anchor="middle"))
    p.append(text(cum_x[1], 438, "T_j1", size=10, color=MUTED, anchor="middle"))
    p.append(text(cum_x[2], 438, "T_a", size=10, color=MUTED, anchor="middle"))
    p.append(text(cum_x[3], 438, "T_j2", size=10, color=MUTED, anchor="middle"))
    p.append(text(cum_x[4], 438, "T_v", size=10, color=MUTED, anchor="middle"))
    p.append(text(cum_x[7], 438, "T_total", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "scurve-seven-segments.svg"), W, H, "".join(p))


# ── 3. Спектральне придушення вібрацій (frequency-spectrum-jerk.svg) ──────────
def fig_frequency_spectrum():
    W, H = 760, 420
    p = []

    tb, _, _ = textbox(W / 2, 25, "Спектр амплітуди збудження механіки |A(f)|: Трапеція проти S-кривої", size=13, bold=True, fill="#f1f5f9", stroke=LINE)
    p.append(tb)

    ox, oy = 90, 340
    gw, gh = 600, 260

    for db, y_off in [("0 dB", 30), ("-20 dB", 95), ("-40 dB", 160), ("-60 dB", 225)]:
        y = oy - (260 - y_off)
        p.append(line(ox, y, ox + gw, y, color="#f1f5f9", sw=1.0))
        p.append(text(ox - 10, y + 4, db, size=10, color=MUTED, anchor="end"))

    p.append(axis_arrow(ox, oy, ox, oy - gh - 20, color=INK, sw=1.4))
    p.append(axis_arrow(ox, oy, ox + gw + 25, oy, color=INK, sw=1.4))
    p.append(text(ox - 35, oy - gh - 5, "|A(f)|", size=12, bold=True, color=INK, anchor="middle"))
    p.append(text(ox + gw + 20, oy + 16, "Частота f (log)", size=11, color=MUTED, italic=True))

    trap_pts = []
    scurve_pts = []

    for i in range(1, 241):
        f = i / 30.0
        x = ox + math.log10(f + 0.1) * 320.0 + 200.0
        if x < ox or x > ox + gw:
            continue
        
        mag_trap = 1.0 / math.sqrt(1.0 + (f * 1.2) ** 2)
        mag_scurve = 1.0 / (math.sqrt(1.0 + (f * 1.2) ** 2) * math.sqrt(1.0 + (f * 3.5) ** 2))

        null_trap = abs(math.sin(math.pi * f * 0.8)) + 0.05
        null_scurve = abs(math.sin(math.pi * f * 0.8) * math.sin(math.pi * f * 0.3)) + 0.02

        db_trap = 20.0 * math.log10(max(mag_trap * null_trap, 1e-4))
        db_scurve = 20.0 * math.log10(max(mag_scurve * null_scurve, 1e-4))

        y_t = (oy - 230) - db_trap * 3.25
        y_s = (oy - 230) - db_scurve * 3.25

        y_t = min(max(y_t, oy - gh), oy)
        y_s = min(max(y_s, oy - gh), oy)

        trap_pts.append((x, y_t))
        scurve_pts.append((x, y_s))

    p.append(polyline(trap_pts, ACC_POS, sw=2.0))
    p.append(polyline(scurve_pts, FIELD, sw=2.4))

    res_x = ox + 430
    p.append(rect(res_x - 35, oy - gh + 15, 70, gh - 15, fill="#fee2e2", stroke="#f87171", sw=1.0, rx=4))
    p.append(text(res_x, oy - gh + 35, "Резонанс", size=10, bold=True, color=POS, anchor="middle"))
    p.append(text(res_x, oy - gh + 48, "механіки f_res", size=9, color=POS, anchor="middle"))

    t_leg1, _, _ = textbox(ox + 120, 85, "Трапеція: спад -20 dB/декаду (1/f)", size=11, bold=True, fill="#fff1f2", stroke=ACC_POS)
    t_leg2, _, _ = textbox(ox + 120, 125, "S-крива: спад -40 dB/декаду (1/f^2)", size=11, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(t_leg1)
    p.append(t_leg2)

    p.append(line(res_x, oy - 190, res_x, oy - 60, color=JERK_COL, sw=2.0))
    p.append(text(res_x + 8, oy - 120, "Придушення >30 dB", size=10, bold=True, color=JERK_COL))

    render(os.path.join(OUT, "frequency-spectrum-jerk.svg"), W, H, "".join(p))


# ── 4. Архітектура каскадного керування з профілем (motion-control-cascade-arch.svg) ──
def fig_cascade_architecture():
    W, H = 820, 360
    p = []

    tb, _, _ = textbox(W / 2, 24, "Подача траєкторії в трирівневий каскад електропривода", size=13, bold=True, fill="#f1f5f9", stroke=LINE)
    p.append(tb)

    b_plan, _, _ = textbox(110, 160, "Планувальник\nтраєкторії\n(S-Curve Generator)", size=12, bold=True, fill="#e0f2fe", stroke="#0284c7")
    p.append(b_plan)

    p.append(circle(255, 160, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(255, 164, "+", size=14, bold=True, anchor="middle"))

    b_pos, _, _ = textbox(335, 160, "Контур\nположення\n(PID)", size=11, bold=True, fill="#f3e8ff", stroke=POS_COL)
    p.append(b_pos)

    p.append(circle(425, 160, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(425, 164, "+", size=14, bold=True, anchor="middle"))

    b_vel, _, _ = textbox(505, 160, "Контур\nшвидкості\n(PI)", size=11, bold=True, fill="#dcfce7", stroke=FIELD)
    p.append(b_vel)

    p.append(circle(595, 160, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(595, 164, "+", size=14, bold=True, anchor="middle"))

    b_cur, _, _ = textbox(675, 160, "Контур струму\nта інвертор\n(FOC / PWM)", size=11, bold=True, fill="#fee2e2", stroke=POS)
    p.append(b_cur)

    b_mot, _, _ = textbox(770, 160, "Двигун\n+ Енкодер", size=10, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(b_mot)

    p.append(arrow(180, 160, 241, 160, color=INK, sw=1.5))
    p.append(text(210, 150, "s_ref", size=11, bold=True, color=POS_COL, anchor="middle"))

    p.append(arrow(269, 160, 290, 160, color=INK, sw=1.4))
    p.append(arrow(380, 160, 411, 160, color=INK, sw=1.4))
    p.append(arrow(439, 160, 460, 160, color=INK, sw=1.4))
    p.append(arrow(550, 160, 581, 160, color=INK, sw=1.4))
    p.append(arrow(609, 160, 625, 160, color=INK, sw=1.4))
    p.append(arrow(725, 160, 740, 160, color=INK, sw=1.4))

    p.append(line(180, 140, 210, 85, color=VEL_COL, sw=1.8))
    p.append(line(210, 85, 425, 85, color=VEL_COL, sw=1.8))
    p.append(arrow(425, 85, 425, 146, color=VEL_COL, sw=1.8))
    p.append(text(315, 75, "Прямий зв'язок за швидкістю v_ff", size=10, bold=True, color=VEL_COL, anchor="middle"))

    p.append(line(180, 175, 220, 245, color=ACC_POS, sw=1.8))
    p.append(line(220, 245, 595, 245, color=ACC_POS, sw=1.8))
    p.append(arrow(595, 245, 595, 174, color=ACC_POS, sw=1.8))
    p.append(text(410, 258, "Прямий зв'язок за моментом T_ff = J·a_ff", size=10, bold=True, color=ACC_POS, anchor="middle"))

    p.append(line(770, 195, 770, 310, color=MUTED, sw=1.5))
    p.append(line(770, 310, 255, 310, color=MUTED, sw=1.5))
    p.append(arrow(255, 310, 255, 174, color=MUTED, sw=1.5))
    p.append(text(510, 325, "Зворотний зв'язок по поточному положенню s_act та швидкості v_act", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "motion-control-cascade-arch.svg"), W, H, "".join(p))


if __name__ == "__main__":
    fig_trapezoid_vs_scurve()
    fig_scurve_seven_segments()
    fig_frequency_spectrum()
    fig_cascade_architecture()
    print("All figures generated successfully.")
