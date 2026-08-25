# -*- coding: utf-8 -*-
"""Фігури до теми «Адаптивне позиціонування напруги (AVP / Droop Control)»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

# ── 1. Порівняння перехідних процесів: без AVP проти AVP ──────────────────────
def fig_transient_comparison():
    W, H = 820, 520
    frags = []
    frags.append(text(W / 2, 24, "Перехідний процес при стрибку струму: звичайний стабілізатор проти AVP", size=15, bold=True))

    # Спільні межі часу
    x_start, x_step1, x_step2, x_end = 80, 240, 520, 760
    
    # ── Верхній графік: Звичайний стабілізатор (R_out = 0)
    y_top_base = 70
    y_nom = y_top_base + 80
    y_vmax = y_top_base + 25
    y_vmin = y_top_base + 135

    # Заголовок секції
    frags.append(text(x_start, y_top_base - 10, "1. Ідеальний стабілізатор (R_out = 0, без AVP): потрібен подвійний запас ємності", size=13, color=POS, anchor="start", bold=True))

    # Зона допуску (Tolerance Window)
    frags.append(rect(x_start, y_vmax, x_end - x_start, y_vmin - y_vmax, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=0))
    frags.append(line(x_start, y_vmax, x_end, y_vmax, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(x_start, y_vmin, x_end, y_vmin, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(x_start, y_nom, x_end, y_nom, color="#94a3b8", sw=1, dash="2,2"))

    frags.append(text(x_start - 8, y_vmax + 4, "V_max", size=11, color=MUTED, anchor="end"))
    frags.append(text(x_start - 8, y_nom + 4, "V_nom", size=11, color=MUTED, anchor="end"))
    frags.append(text(x_start - 8, y_vmin + 4, "V_min", size=11, color=MUTED, anchor="end"))

    # Крива напруги без AVP
    pts1 = [
        (x_start, y_nom),
        (x_step1, y_nom),
        (x_step1 + 2, y_vmin - 5),      # глибоке просідання (undershoot)
        (x_step1 + 40, y_vmin + 5),
        (x_step1 + 100, y_nom),
        (x_step2, y_nom),
        (x_step2 + 2, y_vmax + 5),      # високий викид (overshoot)
        (x_step2 + 40, y_vmax - 5),
        (x_step2 + 100, y_nom),
        (x_end, y_nom)
    ]
    p_str1 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts1)
    frags.append(f'<path d="{p_str1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначки Undershoot та Overshoot
    frags.append(line(x_step1 + 20, y_nom, x_step1 + 20, y_vmin - 5, color=POS, sw=1.5))
    frags.append(text(x_step1 + 26, y_nom + 30, "Просідання ΔV1", size=11, color=POS, anchor="start"))

    frags.append(line(x_step2 + 20, y_nom, x_step2 + 20, y_vmax + 5, color=POS, sw=1.5))
    frags.append(text(x_step2 + 26, y_nom - 30, "Викид ΔV2", size=11, color=POS, anchor="start"))

    # ── Нижній графік: Стабілізатор з AVP (Active Droop Control)
    y_bot_base = 290
    y_avp_vmax = y_bot_base + 25
    y_avp_vmin = y_bot_base + 135

    frags.append(text(x_start, y_bot_base - 10, "2. Стабілізатор з AVP (R_out = R_LL): повне використання коридору напруги", size=13, color=FIELD, anchor="start", bold=True))

    # Зона допуску
    frags.append(rect(x_start, y_avp_vmax, x_end - x_start, y_avp_vmin - y_avp_vmax, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=0))
    frags.append(line(x_start, y_avp_vmax, x_end, y_avp_vmax, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(x_start, y_avp_vmin, x_end, y_avp_vmin, color="#94a3b8", sw=1, dash="4,4"))

    frags.append(text(x_start - 8, y_avp_vmax + 4, "V_max", size=11, color=MUTED, anchor="end"))
    frags.append(text(x_start - 8, y_avp_vmin + 4, "V_min", size=11, color=MUTED, anchor="end"))

    # Крива напруги з AVP
    pts2 = [
        (x_start, y_avp_vmax),
        (x_step1, y_avp_vmax),
        (x_step1 + 4, y_avp_vmin),       # чіткий монотонний спад до V_min
        (x_step2, y_avp_vmin),          # утримання на V_min під навантаженням
        (x_step2 + 4, y_avp_vmax),       # чіткий підйом до V_max
        (x_end, y_avp_vmax)
    ]
    p_str2 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts2)
    frags.append(f'<path d="{p_str2}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Пояснювальні підписи напруг AVP
    frags.append(text(x_step1 - 30, y_avp_vmax - 8, "I = 0 (холостий хід)", size=11, color=FIELD, anchor="middle"))
    frags.append(text((x_step1 + x_step2) / 2, y_avp_vmin + 18, "I = I_max (повне навантаження)", size=11, color=FIELD, anchor="middle"))

    # ── Графік струму навантаження внизу
    y_i_base = 460
    frags.append(line(x_start, y_i_base + 30, x_end, y_i_base + 30, color=LINE, sw=1.5))
    frags.append(arrow(x_end, y_i_base + 30, x_end + 25, y_i_base + 30, color=LINE, sw=1.5))
    frags.append(text(x_end + 30, y_i_base + 34, "t", size=12, color=INK, anchor="start", italic=True))

    pts_i = [
        (x_start, y_i_base + 30),
        (x_step1, y_i_base + 30),
        (x_step1 + 2, y_i_base),
        (x_step2, y_i_base),
        (x_step2 + 2, y_i_base + 30),
        (x_end, y_i_base + 30)
    ]
    p_str_i = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_i)
    frags.append(f'<path d="{p_str_i}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    frags.append(text(x_start - 8, y_i_base + 34, "0 А", size=11, color=MUTED, anchor="end"))
    frags.append(text(x_start - 8, y_i_base + 4, "I_max", size=11, color=MUTED, anchor="end"))
    frags.append(text((x_step1 + x_step2) / 2, y_i_base - 8, "Струм навантаження I_load (наприклад, 0 → 150 А)", size=11, color=NEG, anchor="middle", bold=True))

    # Пунктири зв'язку подій
    frags.append(line(x_step1, y_top_base, x_step1, y_i_base + 30, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(x_step2, y_top_base, x_step2, y_i_base + 30, color="#cbd5e1", sw=1, dash="3,3"))

    render(os.path.join(IMG, "transient-comparison.svg"), W, H, *frags)


# ── 2. Навантажувальна пряма (Load-Line) ──────────────────────────────────────
def fig_loadline_characteristic():
    W, H = 760, 440
    frags = []
    frags.append(text(W / 2, 24, "Навантажувальна пряма (Load-Line) та вікно толерантності VRM", size=15, bold=True))

    ox, oy = 110, 360
    gx_len, gy_len = 540, 290

    # Осі
    frags.append(line(ox, oy, ox + gx_len, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox + gx_len, oy, ox + gx_len + 25, oy, color=LINE, sw=1.8))
    frags.append(text(ox + gx_len + 30, oy + 4, "I_вих (А)", size=12, color=INK, anchor="start"))

    frags.append(line(ox, oy, ox, oy - gy_len, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy - gy_len, ox, oy - gy_len - 25, color=LINE, sw=1.8))
    frags.append(text(ox, oy - gy_len - 32, "V_вих (В)", size=12, color=INK, anchor="middle"))

    # Координати напруг і струмів
    y_vmax_spec = oy - 270
    y_vmax_avp  = oy - 240
    y_vnom      = oy - 160
    y_vmin_avp  = oy - 80
    y_vmin_spec = oy - 50

    x_imax = ox + 460

    # Коридор специфікації (специфікація процесора V_max_spec ... V_min_spec)
    frags.append(f'<rect x="{ox:.1f}" y="{y_vmax_spec:.1f}" width="460.0" height="{y_vmin_spec - y_vmax_spec:.1f}" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,4"/>')
    frags.append(text(ox + 470, (y_vmax_spec + y_vmin_spec) / 2, "Допустимий коридор напруг CPU", size=11, color=MUTED, anchor="start"))

    # Позначки на осі Y
    frags.append(text(ox - 10, y_vmax_spec + 4, "V_max (специфікація)", size=11, color=POS, anchor="end"))
    frags.append(text(ox - 10, y_vmax_avp + 4, "V_NL (холостий хід)", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(ox - 10, y_vnom + 4, "V_nom (без AVP)", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, y_vmin_avp + 4, "V_FL (повне навантаження)", size=11, color=FIELD, anchor="end", bold=True))
    frags.append(text(ox - 10, y_vmin_spec + 4, "V_min (специфікація)", size=11, color=POS, anchor="end"))

    # Позначки на осі X
    frags.append(line(x_imax, oy, x_imax, oy + 6, color=LINE, sw=1.5))
    frags.append(text(x_imax, oy + 22, "I_max", size=12, color=INK, anchor="middle", bold=True))
    frags.append(line(ox, oy, ox, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox, oy + 22, "0", size=12, color=INK, anchor="middle"))

    # Лінія без AVP (горизонтальна)
    frags.append(line(ox, y_vnom, x_imax, y_vnom, color=POS, sw=2, dash="5,5"))
    frags.append(text(ox + 230, y_vnom - 10, "Звичайне регулювання: R_out = 0 (V = const)", size=11, color=POS, anchor="middle"))

    # Лінія навантаження AVP (похила з кутом -R_LL)
    frags.append(line(ox, y_vmax_avp, x_imax, y_vmin_avp, color=FIELD, sw=3))
    frags.append(circle(ox, y_vmax_avp, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(circle(x_imax, y_vmin_avp, 4.5, fill=FIELD, stroke=FIELD))

    # Формула навантажувальної прямої
    tb = fitbox(ox + 130, y_vmax_avp + 45, 270, 54, "V_вих(I) = V_NL − R_LL · I_load\nНахил характеристики: R_LL = ΔV / I_max", size=12, fill="#ecfdf5", stroke=FIELD)
    frags.append(tb)

    # Запас на шум та DC точність (Guardbands)
    frags.append(line(ox + 420, y_vmax_spec, ox + 420, y_vmax_avp, color="#64748b", sw=1.5))
    frags.append(text(ox + 426, (y_vmax_spec + y_vmax_avp) / 2 + 3, "Запас на похибку DC", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "loadline-characteristic.svg"), W, H, *frags)


# ── 3. Структурна схема контуру Active Droop Control у багатофазному VRM ───────
def fig_vrm_droop_loop():
    W, H = 820, 480
    frags = []
    frags.append(text(W / 2, 24, "Контур зворотного зв'язку за струмом та напругою (Active Droop Control)", size=15, bold=True))

    # Процесор праворуч
    cpu_x, cpu_y, cpu_w, cpu_h = 660, 140, 120, 240
    frags.append(rect(cpu_x, cpu_y, cpu_w, cpu_h, fill="#f1f5f9", stroke="#334155", sw=2, rx=6))
    frags.append(text(cpu_x + cpu_w/2, cpu_y + 30, "CPU / GPU", size=14, bold=True, color="#0f172a"))
    frags.append(text(cpu_x + cpu_w/2, cpu_y + 55, "Ядро VCore", size=12, color=MUTED))
    frags.append(text(cpu_x + cpu_w/2, cpu_y + 110, "Стрибки струму", size=11, color=POS, bold=True))
    frags.append(text(cpu_x + cpu_w/2, cpu_y + 130, "50–300 А", size=12, color=POS, bold=True))
    frags.append(text(cpu_x + cpu_w/2, cpu_y + 150, "di/dt > 100 А/мкс", size=10, color=POS))

    # Вихідна шина живлення
    v_rail_y = 100
    gnd_rail_y = 420
    frags.append(line(460, v_rail_y, cpu_x, v_rail_y, color=POS, sw=3))
    frags.append(text(540, v_rail_y - 10, "Шина VCore (0.8–1.3 В)", size=12, color=POS, bold=True, anchor="middle"))

    # Конденсаторна батарея (C_out)
    cap_x = 590
    frags.append(line(cap_x, v_rail_y, cap_x, v_rail_y + 40, color=LINE, sw=2))
    frags.append(line(cap_x - 16, v_rail_y + 40, cap_x + 16, v_rail_y + 40, color=LINE, sw=2.5))
    frags.append(line(cap_x - 16, v_rail_y + 47, cap_x + 16, v_rail_y + 47, color=LINE, sw=2.5))
    frags.append(line(cap_x, v_rail_y + 47, cap_x, gnd_rail_y, color=LINE, sw=2))
    frags.append(text(cap_x + 22, v_rail_y + 48, "C_вих (MLCC + Polymer)", size=11, color=MUTED, anchor="start"))

    # Земляна шина
    frags.append(line(160, gnd_rail_y, cpu_x, gnd_rail_y, color=LINE, sw=2.5))
    frags.append(text(540, gnd_rail_y + 18, "Силова земля (GND)", size=11, color=MUTED, anchor="middle"))

    # 3 Фази перетворювача (зліва)
    p_ys = [140, 200, 260]
    for i, py in enumerate(p_ys):
        frags.append(rect(340, py - 18, 90, 36, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
        frags.append(text(385, py + 5, f"Фаза {i+1} (L, DCR)", size=11, color=NEG, bold=True))
        # З'єднання до шини VCore
        frags.append(line(430, py, 460, py, color=POS, sw=2))
        frags.append(line(460, py, 460, v_rail_y, color=POS, sw=2))
        # Сигнал струмового сенсингу до суматора
        frags.append(line(340, py, 260, py, color="#64748b", sw=1.2, dash="3,3"))

    # Блок сумування струмів
    frags.append(rect(160, 160, 100, 120, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(210, 195, "Суматор", size=12, bold=True, color="#334155"))
    frags.append(text(210, 215, "струмів фаз", size=11, color="#334155"))
    frags.append(text(210, 245, "I_sum = Σ I_k", size=11, bold=True, color=NEG))

    # Підсилювач помилки напруги та введення Droop
    ea_x, ea_y = 60, 70
    frags.append(rect(ea_x, ea_y, 160, 75, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(ea_x + 80, ea_y + 24, "Підсилювач помилки", size=12, bold=True, color=NEG))
    frags.append(text(ea_x + 80, ea_y + 44, "з контуром Droop", size=11, color=NEG))
    frags.append(text(ea_x + 80, ea_y + 64, "V_FB = V_сенс − R_LL · I_sum", size=10, bold=True, color=FIELD))

    # Зв'язок від суматора струму до підсилювача помилки (Droop Injection)
    frags.append(arrow(210, 160, 210, ea_y + 75, color=FIELD, sw=2))
    frags.append(text(218, 150, "Droop-сигнал", size=10, color=FIELD, anchor="start", bold=True))

    # Зворотний зв'язок від виходу CPU (Remote Sense) до підсилювача
    frags.append(line(cpu_x, v_rail_y + 15, 600, v_rail_y + 15, color=POS, sw=1.2, dash="4,4"))
    frags.append(line(600, v_rail_y + 15, 600, 50, color=POS, sw=1.2, dash="4,4"))
    frags.append(line(600, 50, ea_x + 80, 50, color=POS, sw=1.2, dash="4,4"))
    frags.append(arrow(ea_x + 80, 50, ea_x + 80, ea_y, color=POS, sw=1.5))
    frags.append(text(400, 42, "Дистанційний сенсинг напруги ядра (V_sense)", size=11, color=POS, bold=True, anchor="middle"))

    # ШІМ контролер і розподіл фаз
    pwm_x, pwm_y = 60, 290
    frags.append(rect(pwm_x, pwm_y, 160, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(pwm_x + 80, pwm_y + 28, "ШІМ-генератор", size=12, bold=True, color=INK))
    frags.append(text(pwm_x + 80, pwm_y + 48, "Розподіл фаз (N фаз)", size=11, color=MUTED))

    # Зв'язок EA -> ШІМ
    frags.append(arrow(ea_x + 80, ea_y + 75, pwm_x + 80, pwm_y, color=INK, sw=1.8))
    frags.append(text(ea_x + 70, 215, "V_COMP", size=11, color=INK, anchor="end"))

    # Зв'язок ШІМ -> Фази
    for py in p_ys:
        frags.append(arrow(pwm_x + 160, pwm_y + 35, 340, py, color=LINE, sw=1.2))

    render(os.path.join(IMG, "vrm-droop-loop.svg"), W, H, *frags)


# ── 4. DCR-моніторинг струму з NTC-компенсацією ──────────────────────────────
def fig_dcr_sensing_ntc():
    W, H = 780, 420
    frags = []
    frags.append(text(W / 2, 24, "Струмовий моніторинг котушки (DCR Sensing) з NTC-компенсацією", size=15, bold=True))

    # Вузол перемикання SW зліва
    sw_x, sw_y = 60, 100
    frags.append(circle(sw_x, sw_y, 4, fill=POS, stroke=POS))
    frags.append(text(sw_x, sw_y - 12, "Вузол SW", size=12, color=POS, bold=True, anchor="middle"))

    # Силова котушка L з активним опором DCR
    frags.append(line(sw_x, sw_y, sw_x + 50, sw_y, color=LINE, sw=2.5))
    
    # Символ індуктивності
    lx0 = sw_x + 50
    for k in range(3):
        cx = lx0 + 15 + k * 24
        frags.append(f'<path d="M{cx-12:.1f} {sw_y:.1f} A12 12 0 0 1 {cx+12:.1f} {sw_y:.1f}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    frags.append(text(lx0 + 36, sw_y - 18, "L (індуктивність)", size=12, color=INK, anchor="middle", bold=True))

    # Резистор DCR (внутрішній опір міді)
    dcr_x = lx0 + 72 + 20
    frags.append(line(lx0 + 72, sw_y, dcr_x, sw_y, color=LINE, sw=2.5))
    frags.append(rect(dcr_x, sw_y - 12, 50, 24, fill="#fef2f2", stroke=POS, sw=1.8, rx=2))
    frags.append(text(dcr_x + 25, sw_y + 5, "DCR", size=11, color=POS, bold=True))
    frags.append(text(dcr_x + 25, sw_y + 26, "(мідь, +0.39%/°C)", size=9, color=POS))

    # Вихідний вузол VCore
    vcore_x = dcr_x + 50 + 40
    frags.append(line(dcr_x + 50, sw_y, vcore_x + 80, sw_y, color=LINE, sw=2.5))
    frags.append(circle(vcore_x + 80, sw_y, 4, fill=POS, stroke=POS))
    frags.append(text(vcore_x + 80, sw_y - 12, "VCore", size=12, color=POS, bold=True, anchor="middle"))

    # Паралельний RC-ланцюг сенсингу струму (R_s, C_s)
    rc_y = 210
    frags.append(line(sw_x + 20, sw_y, sw_x + 20, rc_y, color=NEG, sw=1.8))
    frags.append(line(sw_x + 20, rc_y, sw_x + 70, rc_y, color=NEG, sw=1.8))

    # Резистор R_s
    frags.append(rect(sw_x + 70, rc_y - 12, 50, 24, fill="#ffffff", stroke=NEG, sw=1.8, rx=2))
    frags.append(text(sw_x + 95, rc_y + 5, "R_s", size=11, color=NEG, bold=True))

    frags.append(line(sw_x + 120, rc_y, sw_x + 170, rc_y, color=NEG, sw=1.8))

    # Конденсатор C_s
    cs_x = sw_x + 170
    frags.append(line(cs_x, rc_y - 14, cs_x, rc_y + 14, color=NEG, sw=2.5))
    frags.append(line(cs_x + 7, rc_y - 14, cs_x + 7, rc_y + 14, color=NEG, sw=2.5))
    frags.append(text(cs_x + 3, rc_y + 28, "C_s", size=11, color=NEG, bold=True, anchor="middle"))

    # Повернення до VCore (Kelvin підключення)
    frags.append(line(cs_x + 7, rc_y, vcore_x + 30, rc_y, color=NEG, sw=1.8))
    frags.append(line(vcore_x + 30, rc_y, vcore_x + 30, sw_y, color=NEG, sw=1.8))

    # Умова узгодження RC
    tb_match = fitbox(sw_x + 40, 260, 240, 48, "Умова балансу постійних часу:\nL / DCR = R_s · C_s  ⇒  V_Cs = DCR · i_L", size=11, fill="#eff6ff", stroke=NEG)
    frags.append(tb_match)

    # ── Термічна компенсація NTC праворуч
    ntc_box_x = 440
    frags.append(rect(ntc_box_x, 80, 310, 300, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(ntc_box_x + 155, 108, "Схема температурної компенсації", size=13, bold=True, color="#1e293b"))
    frags.append(text(ntc_box_x + 155, 128, "(NTC біля котушки нівелює нагрів DCR)", size=10, color=MUTED))

    # Дільник з терморезистором NTC
    ny0 = 160
    frags.append(line(ntc_box_x + 60, ny0, ntc_box_x + 120, ny0, color=LINE, sw=1.8))
    frags.append(rect(ntc_box_x + 120, ny0 - 12, 45, 24, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(ntc_box_x + 142, ny0 + 5, "R1", size=11, color=INK))

    frags.append(line(ntc_box_x + 165, ny0, ntc_box_x + 210, ny0, color=LINE, sw=1.8))

    # NTC терморезистор
    frags.append(rect(ntc_box_x + 210, ny0 - 12, 55, 24, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=2))
    frags.append(line(ntc_box_x + 205, ny0 + 16, ntc_box_x + 270, ny0 - 16, color=FIELD, sw=1.5))
    frags.append(text(ntc_box_x + 237, ny0 + 5, "NTC", size=11, color=FIELD, bold=True))
    frags.append(text(ntc_box_x + 237, ny0 - 20, "−T°", size=10, color=FIELD, bold=True))

    # Сигнал до VRM контролера
    frags.append(arrow(ntc_box_x + 210, ny0, ntc_box_x + 210, 270, color=POS, sw=2))
    
    frags.append(rect(ntc_box_x + 130, 270, 160, 50, fill="#eff6ff", stroke=POS, sw=1.8, rx=4))
    frags.append(text(ntc_box_x + 210, 292, "VRM контролер", size=12, bold=True, color=POS))
    frags.append(text(ntc_box_x + 210, 310, "Вхід ISEN / DROOP", size=10, color=POS))

    # Сигнал від C_s до схеми NTC
    frags.append(line(cs_x + 3, rc_y, ntc_box_x + 60, rc_y, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(ntc_box_x + 60, rc_y, ntc_box_x + 60, ny0, color=NEG, sw=1.5, dash="3,3"))
    frags.append(circle(ntc_box_x + 60, ny0, 3.5, fill=NEG, stroke=NEG))

    tb_ntc_res = fitbox(ntc_box_x + 20, 335, 270, 36, "Сумарний коефіцієнт R_droop = const\nнезалежно від температури 25 °C → 100 °C", size=10, fill="#ffffff", stroke=FIELD)
    frags.append(tb_ntc_res)

    render(os.path.join(IMG, "dcr-sensing-ntc.svg"), W, H, *frags)


# ── 5. Вихідний імпеданс у частотній області: |Z_out(f)| = R_LL = const ───────
def fig_impedance_frequency():
    W, H = 780, 440
    frags = []
    frags.append(text(W / 2, 24, "Вихідний імпеданс VRM у частотній області |Z_вих(f)|", size=15, bold=True))

    ox, oy = 90, 360
    gx_len, gy_len = 620, 290

    # Осі
    frags.append(line(ox, oy, ox + gx_len, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox + gx_len, oy, ox + gx_len + 25, oy, color=LINE, sw=1.8))
    frags.append(text(ox + gx_len + 30, oy + 4, "Частота f (Гц)", size=12, color=INK, anchor="start"))

    frags.append(line(ox, oy, ox, oy - gy_len, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy - gy_len, ox, oy - gy_len - 25, color=LINE, sw=1.8))
    frags.append(text(ox, oy - gy_len - 30, "|Z_вих| (мОм)", size=12, color=INK, anchor="middle"))

    # Позначки частот на осі X (логарифмічна шкала)
    freqs = [
        (ox + 50, "100 Гц"),
        (ox + 160, "10 кГц"),
        (ox + 280, "100 кГц (f_c)"),
        (ox + 400, "1 МГц"),
        (ox + 520, "10 МГц"),
        (ox + 600, "100 МГц")
    ]
    for fx, flabel in freqs:
        frags.append(line(fx, oy, fx, oy + 6, color=LINE, sw=1.2))
        frags.append(text(fx, oy + 22, flabel, size=10, color=MUTED, anchor="middle"))
        frags.append(line(fx, oy, fx, oy - gy_len + 20, color="#f1f5f9", sw=1, dash="2,2"))

    # Цільовий рівень Z_target = R_LL (наприклад, 1.0 мОм)
    y_rll = oy - 140
    frags.append(line(ox, y_rll, ox + gx_len, y_rll, color=FIELD, sw=3.5))
    frags.append(text(ox - 10, y_rll + 4, "R_LL (1.0 мОм)", size=11, color=FIELD, anchor="end", bold=True))
    
    # Плашка для навантажувального імпедансу зверху праворуч (зона x > 440, y < 85)
    tb_avp = fitbox(ox + 350, oy - gy_len + 10, 300, 32, "Ціль AVP: сталий імпеданс |Z_вих(f)| = R_LL", size=11, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(tb_avp)

    # Складові імпедансу
    # 1. Регулятор (активний контур низьких частот)
    pts_loop = [
        (ox + 10, y_rll),
        (ox + 160, y_rll),
        (ox + 230, y_rll + 15),
        (ox + 300, y_rll - 60),
        (ox + 360, y_rll - 150)
    ]
    p_loop = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_loop)
    frags.append(f'<path d="{p_loop}" fill="none" stroke="{NEG}" stroke-width="1.8" stroke-dasharray="4,4"/>')

    # 2. Об'ємні полімерні конденсатори Bulk (середні частоти)
    pts_bulk = [
        (ox + 180, y_rll - 120),
        (ox + 250, y_rll),
        (ox + 370, y_rll),
        (ox + 440, y_rll - 60)
    ]
    p_bulk = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_bulk)
    frags.append(f'<path d="{p_bulk}" fill="none" stroke="#d97706" stroke-width="1.8" stroke-dasharray="4,4"/>')

    # 3. Керамічні MLCC та он-пакетні конденсатори (високі частоти)
    pts_mlcc = [
        (ox + 360, y_rll - 110),
        (ox + 430, y_rll),
        (ox + 540, y_rll),
        (ox + 600, y_rll - 40)
    ]
    p_mlcc = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_mlcc)
    frags.append(f'<path d="{p_mlcc}" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-dasharray="4,4"/>')

    # Звичайний імпеданс без AVP (резонансний пік)
    pts_no_avp = [
        (ox + 10, oy - 20),
        (ox + 130, oy - 30),
        (ox + 230, y_rll - 100),  # різкий резонансний пік через невідповідність фази і ESR
        (ox + 330, y_rll),
        (ox + 500, y_rll)
    ]
    p_no_avp = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_no_avp)
    frags.append(f'<path d="{p_no_avp}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="3,3"/>')

    # Плашка для резонансного сплеску (розміщена ліворуч у вільному просторі)
    frags.append(fitbox(ox + 20, oy - gy_len + 10, 240, 32, "Без AVP: резонансний сплеск |Z_вих|", size=10, fill="#fef2f2", stroke=POS, bold=True))

    # Пояснювальні плашки внизу графіка (legend)
    b1 = fitbox(ox + 20, oy - 80, 170, 42, "1. Контур VRM\n(до зрізу f_c ≈ 100 кГц)", size=10, fill="#eff6ff", stroke=NEG)
    b2 = fitbox(ox + 210, oy - 80, 180, 42, "2. Полімерні Bulk C\n(ESR_bulk = R_LL)", size=10, fill="#fefce8", stroke="#d97706")
    b3 = fitbox(ox + 410, oy - 80, 180, 42, "3. Керамічні MLCC\n(компенсація ВЧ)", size=10, fill="#faf5ff", stroke="#7c3aed")
    frags.append(b1)
    frags.append(b2)
    frags.append(b3)

    render(os.path.join(IMG, "impedance-frequency.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_transient_comparison()
    fig_loadline_characteristic()
    fig_vrm_droop_loop()
    fig_dcr_sensing_ntc()
    fig_impedance_frequency()
    print("Усі фігури згенеровано успішно.")
