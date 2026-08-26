# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

# ── 1. Динамічний профіль струму автономного вузла ────────────────────────────
def fig_current_profile():
    W, H = 840, 480
    frags = []

    frags.append(text(W / 2, 24, 'Динамічний профіль струму автономного бездротового вузла', size=15, bold=True))

    x0, x_max = 95, 780
    y_i0 = 215
    y_v0 = 430

    # ── Графік струму
    frags.append(rect(x0, 45, x_max - x0, 180, fill='#fafbfc', stroke='#cbd5e1', sw=1, rx=4))
    frags.append(line(x0, y_i0, x_max, y_i0, color=LINE, sw=1.5))
    frags.append(arrow(x_max, y_i0, x_max + 20, y_i0, color=LINE, sw=1.5))
    frags.append(text(x_max + 25, y_i0 + 4, 't', size=12, italic=True, anchor='start'))

    frags.append(line(x0, y_i0, x0, 52, color=LINE, sw=1.5))
    frags.append(arrow(x0, 58, x0, 42, color=LINE, sw=1.5))
    frags.append(text(x0 - 10, 48, 'I_нав', size=12, bold=True, anchor='end'))

    frags.append(text(x0 - 8, y_i0 - 4, '0', size=10, color=MUTED, anchor='end'))
    frags.append(text(x0 - 8, y_i0 - 18, '2 мкА (Сон)', size=10, color=MUTED, anchor='end'))
    frags.append(text(x0 - 8, y_i0 - 65, '15 мА (MCU)', size=10, color=MUTED, anchor='end'))
    frags.append(text(x0 - 8, y_i0 - 130, '350 мА (Радіо TX)', size=10, color=POS, anchor='end', bold=True))

    t_sleep1 = 200
    t_wake   = 290
    t_meas   = 380
    t_tx_on  = 450
    t_tx_off = 620
    t_rx     = 690
    t_sleep2 = 770

    tx_poly = [
        (t_tx_on, y_i0),
        (t_tx_on, y_i0 - 130),
        (t_tx_off, y_i0 - 130),
        (t_tx_off, y_i0)
    ]
    p_tx = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in tx_poly) + ' Z'
    frags.append(f'<path d="{p_tx}" fill="#fdecea" stroke="none"/>')

    pts_i = [
        (x0, y_i0 - 3),
        (t_sleep1, y_i0 - 3),
        (t_sleep1 + 2, y_i0 - 40),
        (t_wake, y_i0 - 40),
        (t_wake + 2, y_i0 - 65),
        (t_meas, y_i0 - 65),
        (t_meas + 2, y_i0 - 30),
        (t_tx_on, y_i0 - 30),
        (t_tx_on + 3, y_i0 - 130),
        (t_tx_off, y_i0 - 130),
        (t_tx_off + 2, y_i0 - 55),
        (t_rx, y_i0 - 55),
        (t_rx + 2, y_i0 - 3),
        (t_sleep2, y_i0 - 3)
    ]
    p_i = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_i)
    frags.append(f'<path d="{p_i}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    frags.append(text((x0 + t_sleep1) / 2, 65, 'Глибокий сон', size=10.5, color=MUTED))
    frags.append(text((t_wake + t_meas) / 2, 80, 'Сенсор', size=10.5, color=LINE))
    frags.append(text((t_tx_on + t_tx_off) / 2, 65, 'Імпульс передачі RF (350 мА)', size=11, color=POS, bold=True))
    frags.append(text((t_tx_off + t_rx) / 2, 80, 'Прийом ACK', size=10.5, color=MUTED))

    tb1, _, _ = textbox(535, 170, 'Динамічний діапазон струмів:\nI_peak / I_sleep > 150 000 разів!', size=10.5, pad=6, fill='#ffffff', stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(tb1)

    # ── Графік напруги
    frags.append(rect(x0, 255, x_max - x0, 190, fill='#fafbfc', stroke='#cbd5e1', sw=1, rx=4))
    frags.append(line(x0, y_v0, x_max, y_v0, color=LINE, sw=1.5))
    frags.append(arrow(x_max, y_v0, x_max + 20, y_v0, color=LINE, sw=1.5))
    frags.append(text(x_max + 25, y_v0 + 4, 't', size=12, italic=True, anchor='start'))

    frags.append(line(x0, y_v0, x0, 262, color=LINE, sw=1.5))
    frags.append(arrow(x0, 268, x0, 252, color=LINE, sw=1.5))
    frags.append(text(x0 - 10, 258, 'V_шина', size=12, bold=True, anchor='end'))

    y_v_nom = 285
    y_v_bor = 370

    frags.append(line(x0, y_v_nom, x_max, y_v_nom, color='#94a3b8', sw=1, dash='4,4'))
    frags.append(text(x0 - 8, y_v_nom + 4, '3.3 В (V_ном)', size=10, color=MUTED, anchor='end'))

    frags.append(line(x0, y_v_bor, x_max, y_v_bor, color=POS, sw=1.5, dash='5,3'))
    frags.append(text(x0 - 8, y_v_bor + 4, '2.2 В (Поріг BOR)', size=10, color=POS, anchor='end', bold=True))

    pts_v_bad = [
        (x0, y_v_nom),
        (t_tx_on, y_v_nom),
        (t_tx_on + 5, y_v_bor + 20),
        (t_tx_on + 25, y_v_bor + 28),
        (t_tx_on + 30, y_v_nom + 25),
        (t_tx_off, y_v_nom)
    ]
    p_v_bad = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_v_bad)
    frags.append(f'<path d="{p_v_bad}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="3,3"/>')

    pts_v_good = [
        (x0, y_v_nom),
        (t_tx_on, y_v_nom),
        (t_tx_on + 2, y_v_nom + 25),
        (t_tx_off, y_v_nom + 50),
        (t_tx_off + 20, y_v_nom + 10),
        (t_sleep2, y_v_nom)
    ]
    p_v_good = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_v_good)
    frags.append(f'<path d="{p_v_good}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Підписи розташовані осторонь кривих
    frags.append(text(t_tx_on + 5, y_v_bor + 45, 'Аварійне скидання (BOR Reset)!', size=10.5, color=POS, bold=True, anchor='start'))
    frags.append(text(t_tx_off - 10, y_v_nom + 25, 'Із буфером: напруга в нормі', size=10.5, color=FIELD, bold=True, anchor='end'))

    render(os.path.join(IMG, 'current-profile-contrast.svg'), W, H, *frags)


# ── 2. Анатомія просідання напруги та еквівалентна схема PDN ──────────────────
def fig_pdn_droop():
    W, H = 840, 480
    frags = []

    frags.append(text(W / 2, 24, 'Еквівалентна схема розподілу живлення (PDN) та складові просідання', size=15, bold=True))

    x_sch = 40
    y_sch = 60
    w_sch = 350
    h_sch = 395

    # Замість суцільного фонового прямокутника робимо тонку рамку секції
    frags.append(line(x_sch, y_sch, x_sch + w_sch, y_sch, color='#cbd5e1', sw=1))
    frags.append(line(x_sch, y_sch + h_sch, x_sch + w_sch, y_sch + h_sch, color='#cbd5e1', sw=1))
    frags.append(line(x_sch, y_sch, x_sch, y_sch + h_sch, color='#cbd5e1', sw=1))
    frags.append(line(x_sch + w_sch, y_sch, x_sch + w_sch, y_sch + h_sch, color='#cbd5e1', sw=1))
    frags.append(text(x_sch + w_sch / 2, y_sch + 22, 'Еквівалентна схема PDN', size=13, bold=True))

    tb_bat, _, _ = textbox(x_sch + 75, y_sch + 75, 'Джерело живлення\n(OCV, R_джерела)', size=11, pad=6, fill='#eaf0fd', stroke=NEG, color=NEG, bold=True)
    frags.append(tb_bat)

    tb_trace, _, _ = textbox(x_sch + 245, y_sch + 75, 'Провідники / Доріжки\n(L_петлі, R_доріжки)', size=11, pad=6, fill='#ffffff', stroke=LINE, color=INK)
    frags.append(tb_trace)

    frags.append(line(x_sch + 140, y_sch + 75, x_sch + 175, y_sch + 75, color=LINE, sw=2))

    tb_cap, _, _ = textbox(x_sch + 140, y_sch + 195, 'Буферний вузол (C_буф)\nESR + ESL + C_ефект', size=11, pad=6, fill='#eafaf1', stroke=FIELD, color=FIELD, bold=True)
    frags.append(tb_cap)

    tb_load, _, _ = textbox(x_sch + 275, y_sch + 195, 'Навантаження\nMCU + RF PA\n(Пік I_нав)', size=11, pad=6, fill='#fdecea', stroke=POS, color=POS, bold=True)
    frags.append(tb_load)

    frags.append(line(x_sch + 245, y_sch + 110, x_sch + 245, y_sch + 150, color=LINE, sw=2))
    frags.append(line(x_sch + 140, y_sch + 150, x_sch + 275, y_sch + 150, color=LINE, sw=2))
    frags.append(line(x_sch + 140, y_sch + 150, x_sch + 140, y_sch + 170, color=LINE, sw=2))
    frags.append(line(x_sch + 275, y_sch + 150, x_sch + 275, y_sch + 170, color=LINE, sw=2))

    frags.append(line(x_sch + 75, y_sch + 320, x_sch + 275, y_sch + 320, color=LINE, sw=2))
    frags.append(line(x_sch + 75, y_sch + 110, x_sch + 75, y_sch + 320, color=LINE, sw=1.5))
    frags.append(line(x_sch + 140, y_sch + 220, x_sch + 140, y_sch + 320, color=LINE, sw=1.5))
    frags.append(line(x_sch + 275, y_sch + 230, x_sch + 275, y_sch + 320, color=LINE, sw=1.5))
    frags.append(text(x_sch + 175, y_sch + 345, 'Спільна шина повернення (GND)', size=10.5, color=MUTED))

    # Графік справа
    x_gr = 420
    y_gr = 60
    w_gr = 390
    h_gr = 395

    frags.append(rect(x_gr, y_gr, w_gr, h_gr, fill='#fafbfc', stroke='#cbd5e1', sw=1.2, rx=6))
    frags.append(text(x_gr + w_gr / 2, y_gr + 24, 'Три фази просідання напруги V_bus', size=13, bold=True))

    y_axis = y_gr + 320
    x_axis_end = x_gr + w_gr - 25

    frags.append(line(x_gr + 35, y_axis, x_axis_end, y_axis, color=LINE, sw=1.5))
    frags.append(arrow(x_axis_end, y_axis, x_axis_end + 18, y_axis, color=LINE, sw=1.5))
    frags.append(text(x_axis_end + 22, y_axis + 4, 't', size=12, italic=True))

    frags.append(line(x_gr + 35, y_axis, x_gr + 35, y_gr + 45, color=LINE, sw=1.5))
    frags.append(arrow(x_gr + 35, y_gr + 50, x_gr + 35, y_gr + 35, color=LINE, sw=1.5))
    frags.append(text(x_gr + 25, y_gr + 40, 'V', size=12, bold=True, anchor='end'))

    y_vstart = y_gr + 70
    frags.append(line(x_gr + 35, y_vstart, x_axis_end, y_vstart, color='#94a3b8', sw=1, dash='3,3'))
    frags.append(text(x_gr + 30, y_vstart + 4, 'V_0', size=10, color=MUTED, anchor='end'))

    t0 = x_gr + 60
    t1 = x_gr + 95
    t2 = x_gr + 240
    t3 = x_gr + 330

    pts_trans = [
        (x_gr + 35, y_vstart),
        (t0, y_vstart),
        (t0 + 4, y_vstart + 35),
        (t0 + 10, y_vstart + 24),
        (t1, y_vstart + 30),
        (t2, y_vstart + 115),
        (t2 + 4, y_vstart + 80),
        (t3, y_vstart + 5),
        (x_axis_end, y_vstart)
    ]
    p_trans = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_trans)
    frags.append(f'<path d="{p_trans}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    frags.append(text(t0 + 15, y_vstart + 15, '1: ΔV_L = L · (di/dt)', size=9.5, color=POS, anchor='start', bold=True))
    frags.append(text(t1 + 20, y_vstart + 42, '2: ΔV_ESR = I_пік · ESR', size=9.5, color=NEG, anchor='start', bold=True))
    frags.append(text(t2 + 15, y_vstart + 80, '3: ΔV_C = I · Δt / C', size=9.5, color=FIELD, anchor='start', bold=True))

    y_bor_line = y_vstart + 145
    frags.append(line(x_gr + 35, y_bor_line, x_axis_end, y_bor_line, color='#dc2626', sw=1.5, dash='4,4'))
    frags.append(text(x_axis_end - 10, y_bor_line - 6, 'Поріг аварійного скидання BOR', size=10, color='#dc2626', anchor='end', bold=True))

    render(os.path.join(IMG, 'pdn-droop-mechanism.svg'), W, H, *frags)


# ── 3. Порівняння технологій накопичувальних конденсаторів ───────────────────
def fig_capacitor_tech():
    W, H = 840, 460
    frags = []

    frags.append(text(W / 2, 24, 'Порівняння класів буферних конденсаторів для компенсації пікових струмів', size=15, bold=True))

    col_w = 235
    h_box = 370
    y_box = 60

    # 1. Кераміка MLCC
    x1 = 40
    frags.append(rect(x1, y_box, col_w, h_box, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=6))
    frags.append(rect(x1 + 10, y_box + 10, col_w - 20, 42, fill='#eaf0fd', stroke=NEG, sw=1.2, rx=4))
    frags.append(text(x1 + col_w / 2, y_box + 28, 'Кераміка MLCC', size=12.5, color=NEG, bold=True))
    frags.append(text(x1 + col_w / 2, y_box + 44, '(X5R, X7R)', size=10.5, color=NEG))

    mlcc_facts = [
        'Ємність: 1 – 100 мкФ',
        'ESR: 2 – 20 мОм (наймалий)',
        'Швидкодія: одиниці нс',
        'Струм витоку: < 0.1 мкА',
        'Пастка: падіння ємності',
        'під напругою (DC Bias) до −70%!',
        'Застосування: розв язка РФ,',
        'локальні швидкі фронти'
    ]
    frags.append(mtext(x1 + col_w / 2, y_box + 85, mlcc_facts, size=11, color=INK, lh=1.45))

    # 2. Тантал / Полімер
    x2 = x1 + col_w + 25
    frags.append(rect(x2, y_box, col_w, h_box, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=6))
    frags.append(rect(x2 + 10, y_box + 10, col_w - 20, 42, fill='#fef9c3', stroke='#ca8a04', sw=1.2, rx=4))
    frags.append(text(x2 + col_w / 2, y_box + 28, 'Тантал / Полімер', size=12.5, color='#854d0e', bold=True))
    frags.append(text(x2 + col_w / 2, y_box + 44, '(POSCAP, KO-CAP)', size=10.5, color='#854d0e'))

    tant_facts = [
        'Ємність: 47 – 1000 мкФ',
        'ESR: 15 – 80 мОм (помірний)',
        'Швидкодія: десятки нс',
        'Струм витоку: 1 – 10 мкА',
        'Перевага: стабільна ємність,',
        'немає DC-bias ефекту',
        'Пастка: чутливість до полярності',
        'та імпульсного пускового струму'
    ]
    frags.append(mtext(x2 + col_w / 2, y_box + 85, tant_facts, size=11, color=INK, lh=1.45))

    # 3. Суперемності EDLC
    x3 = x2 + col_w + 25
    frags.append(rect(x3, y_box, col_w, h_box, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=6))
    frags.append(rect(x3 + 10, y_box + 10, col_w - 20, 42, fill='#eafaf1', stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(x3 + col_w / 2, y_box + 28, 'Суперемності EDLC / HLC', size=12, color=FIELD, bold=True))
    frags.append(text(x3 + col_w / 2, y_box + 44, '(Іоністори)', size=10.5, color=FIELD))

    edlc_facts = [
        'Ємність: 0.1 – 10 Фарад (гігантська)',
        'ESR: 0.1 – 5 Ом (значний)',
        'Швидкодія: частки мілісекунди',
        'Струм витоку: 2 – 15 мкА (високий)',
        'Перевага: тримає імпульси',
        'тривалістю сотні мілісекунд',
        'Пастка: вимагає схеми м якого',
        'заряду та захисту від КЗ'
    ]
    frags.append(mtext(x3 + col_w / 2, y_box + 85, edlc_facts, size=11, color=INK, lh=1.45))

    render(os.path.join(IMG, 'capacitor-tech-comparison.svg'), W, H, *frags)


# ── 4. Падіння ефективної ємності MLCC під постійною напругою (DC Bias) ──────
def fig_dc_bias():
    W, H = 840, 440
    frags = []

    frags.append(text(W / 2, 26, 'Ефект постійної напруги зміщення (DC Bias Derating) у керамічних конденсаторах MLCC', size=14.5, bold=True))

    x0, y0 = 100, 360
    w_g, h_g = 680, 280

    frags.append(rect(x0, y0 - h_g, w_g, h_g, fill='#fafbfc', stroke='#cbd5e1', sw=1, rx=4))

    for pct, label in [(0, '0%'), (25, '−25%'), (50, '−50%'), (75, '−75%'), (100, '−100%')]:
        y_l = y0 - (100 - pct) * (h_g - 40) / 100 - 20
        frags.append(line(x0, y_l, x0 + w_g, y_l, color='#e2e8f0', sw=1, dash='3,3'))
        frags.append(text(x0 - 10, y_l + 4, label, size=10.5, color=MUTED, anchor='end'))

    voltages = [
        (0.0, '0 В'),
        (1.8, '1.8 В'),
        (3.3, '3.3 В (Шина)'),
        (5.0, '5.0 В'),
        (6.3, '6.3 В (Номінал 1)'),
        (10.0, '10 В (Номінал 2)')
    ]

    for v, lbl in voltages:
        xv = x0 + (v / 10.0) * (w_g - 60) + 30
        frags.append(line(xv, y0 - h_g, xv, y0, color='#f1f5f9', sw=1))
        frags.append(line(xv, y0, xv, y0 + 5, color=LINE, sw=1.2))
        frags.append(text(xv, y0 + 18, lbl, size=10, color=INK, anchor='middle'))

    frags.append(line(x0, y0, x0 + w_g, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0, x0, y0 - h_g, color=LINE, sw=1.5))
    frags.append(arrow(x0 + w_g - 10, y0, x0 + w_g + 10, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0 - h_g + 10, x0, y0 - h_g - 10, color=LINE, sw=1.5))
    frags.append(text(x0 + w_g + 15, y0 + 4, 'V_DC', size=11.5, italic=True))
    frags.append(text(x0 - 12, y0 - h_g - 5, 'ΔC/C₀', size=11.5, bold=True, anchor='end'))

    pts_c1 = [
        (0.0, 0), (1.0, -18), (1.8, -38), (2.5, -52), (3.3, -68), (4.2, -78), (5.0, -84), (6.3, -90), (10.0, -95)
    ]
    pts_px1 = [(x0 + (v / 10.0) * (w_g - 60) + 30, y0 - (100 + pct) * (h_g - 40) / 100 - 20) for v, pct in pts_c1]
    p_str1 = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_px1)
    frags.append(f'<path d="{p_str1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    pts_c2 = [
        (0.0, 0), (1.0, -5), (1.8, -12), (2.5, -20), (3.3, -30), (4.2, -42), (5.0, -52), (6.3, -64), (10.0, -82)
    ]
    pts_px2 = [(x0 + (v / 10.0) * (w_g - 60) + 30, y0 - (100 + pct) * (h_g - 40) / 100 - 20) for v, pct in pts_c2]
    p_str2 = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_px2)
    frags.append(f'<path d="{p_str2}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    pts_c3 = [(0.0, 0), (10.0, 0)]
    pts_px3 = [(x0 + (v / 10.0) * (w_g - 60) + 30, y0 - (100 + pct) * (h_g - 40) / 100 - 20) for v, pct in pts_c3]
    p_str3 = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_px3)
    frags.append(f'<path d="{p_str3}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="4,4"/>')

    frags.append(text(460, 115, '1. Тантал POSCAP / Кераміка C0G: ємність стабільна (0% втрат)', size=10.5, color=NEG, bold=True, anchor='start'))
    frags.append(text(460, 195, '2. 10 мкФ 0805 10 В X7R: втрата −30% при 3.3 В', size=10.5, color=FIELD, bold=True, anchor='start'))
    frags.append(text(460, 275, '3. 10 мкФ 0402 6.3 В X5R: втрата −68% при 3.3 В! (лишилося 3.2 мкФ)', size=10.5, color=POS, bold=True, anchor='start'))

    x_3v3 = x0 + (3.3 / 10.0) * (w_g - 60) + 30
    frags.append(line(x_3v3, y0 - h_g + 10, x_3v3, y0, color='#dc2626', sw=1.2, dash='3,3'))

    render(os.path.join(IMG, 'dc-bias-derating.svg'), W, H, *frags)


# ── 5. Каскадне ввімкнення та обмеження швидкості наростання струму ────────────
def fig_staggered():
    W, H = 840, 480
    frags = []

    frags.append(text(W / 2, 24, 'Зниження пікового навантаження: одночасний пуск проти каскадного (Staggered Wake-up)', size=14.5, bold=True))

    x0 = 80
    w_chart = 710
    y1_base = 210

    frags.append(rect(x0, 50, w_chart, 180, fill='#fafbfc', stroke='#cbd5e1', sw=1, rx=4))
    frags.append(text(x0 + 15, 72, '1. Несинхронізований одночасний пуск (Одночасно: Flash + Сенсор + Радіо)', size=11.5, color=POS, bold=True, anchor='start'))

    frags.append(line(x0 + 30, y1_base, x0 + w_chart - 20, y1_base, color=LINE, sw=1.2))
    frags.append(line(x0 + 30, y1_base, x0 + 30, 85, color=LINE, sw=1.2))
    frags.append(text(x0 + 20, 90, 'I_нав', size=10.5, bold=True, anchor='end'))

    t_start = x0 + 100
    pts_bad_i = [
        (x0 + 30, y1_base - 2),
        (t_start, y1_base - 2),
        (t_start + 4, y1_base - 110),
        (t_start + 50, y1_base - 110),
        (t_start + 55, y1_base - 2),
        (x0 + w_chart - 20, y1_base - 2)
    ]
    p_bi = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_bad_i)
    frags.append(f'<path d="{p_bi}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    frags.append(text(t_start + 65, y1_base - 95, 'Сумарний пік: 480 мА! Глибока просадка шини -> BOR Reset', size=10.5, color=POS, bold=True, anchor='start'))

    y2_base = 430
    frags.append(rect(x0, 260, w_chart, 190, fill='#fafbfc', stroke='#cbd5e1', sw=1, rx=4))
    frags.append(text(x0 + 15, 282, '2. Каскадне рознесене ввімкнення з контрольованим фронтом (Soft-Start)', size=11.5, color=FIELD, bold=True, anchor='start'))

    frags.append(line(x0 + 30, y2_base, x0 + w_chart - 20, y2_base, color=LINE, sw=1.2))
    frags.append(line(x0 + 30, y2_base, x0 + 30, 295, color=LINE, sw=1.2))
    frags.append(text(x0 + 20, 300, 'I_нав', size=10.5, bold=True, anchor='end'))

    t_s1 = x0 + 80
    t_s2 = x0 + 230
    t_s3 = x0 + 390
    t_s4 = x0 + 550

    pts_good_i = [
        (x0 + 30, y2_base - 2),
        (t_s1, y2_base - 2),
        (t_s1 + 15, y2_base - 25),
        (t_s2, y2_base - 25),
        (t_s2 + 10, y2_base - 45),
        (t_s3, y2_base - 45),
        (t_s3 + 25, y2_base - 95),
        (t_s4, y2_base - 95),
        (t_s4 + 10, y2_base - 2),
        (x0 + w_chart - 20, y2_base - 2)
    ]
    p_gi = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts_good_i)
    frags.append(f'<path d="{p_gi}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')

    frags.append(text((t_s1 + t_s2) / 2, y2_base - 35, '1. Сенсор (20 мА)', size=10, color=INK))
    frags.append(text((t_s2 + t_s3) / 2, y2_base - 55, '2. Flash SPI (35 мА)', size=10, color=INK))
    frags.append(rect((t_s3 + t_s4) / 2 - 120, y2_base - 125, 240, 38, fill='#ffffff', stroke=FIELD, sw=1.2, rx=4))
    frags.append(text((t_s3 + t_s4) / 2, y2_base - 108, '3. Радіопередавач із Soft-Start', size=10.5, color=FIELD, bold=True))
    frags.append(text((t_s3 + t_s4) / 2, y2_base - 94, '(Максимум 180 мА замість 480 мА)', size=9.5, color=FIELD))

    render(os.path.join(IMG, 'staggered-power-up.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_current_profile()
    fig_pdn_droop()
    fig_capacitor_tech()
    fig_dc_bias()
    fig_staggered()
    print('Всі фігури згенеровано успішно.')
