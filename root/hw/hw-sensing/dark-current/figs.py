# -*- coding: utf-8 -*-
"""Фігури до статті «Фотострум у напругу: темновий струм, TIA та шумові межі».
Генерує векторні ілюстрації в ./img/:
  1. photodiode-equivalent-dark-current.svg — повна еквівалентна схема фотодіода та температурний дрейф темнового струму
  2. passive-vs-transimpedance.svg          — порівняння пасивного перетворювача (R) та активного TIA (віртуальна земля)
  3. tia-bode-stability.svg                 — діаграма Боде петльового підсилення: нуль 1/beta, нестійкість та компенсація через Cf
  4. dark-current-compensation-methods.svg  — методи компенсації темнового струму: апаратний спарений діод та подвійна корельована вибірка (CDS)
  5. guard-ring-pcb-layout.svg              — топологія захисного кільця Guard Ring для перехоплення струмів витоку плати

Запуск: python figs.py
"""
import sys, os, math

# Додаємо шлях до спільного svgkit у корені scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Допоміжні схемні елементи ────────────────────────────────────────────────
def opamp_sym(cx, cy, w=70, h=60, inv_top=True):
    """Символ операційного підсилювача."""
    x0 = cx - w / 2
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x0, cy - h / 2, x0, cy + h / 2, cx + w / 2, cy)
    body = '<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % (pts, INK)
    in_top = (x0, cy - h / 4)
    in_bot = (x0, cy + h / 4)
    out_pt = (cx + w / 2, cy)
    s_top = "−" if inv_top else "+"
    s_bot = "+" if inv_top else "−"
    c_top = NEG if s_top == "−" else POS
    c_bot = NEG if s_bot == "−" else POS
    body += text(x0 + 12, in_top[1] + 5, s_top, size=18, color=c_top, bold=True)
    body += text(x0 + 12, in_bot[1] + 5, s_bot, size=18, color=c_bot, bold=True)
    return body, in_top, in_bot, out_pt


def isource_sym(x, y1, y2, label="I", arrow_down=True, color=FIELD):
    """Джерело струму у вигляді кола зі стрілкою."""
    mid_y = (y1 + y2) / 2
    out = line(x, y1, x, mid_y - 14, color=INK, sw=1.6)
    out += line(x, mid_y + 14, x, y2, color=INK, sw=1.6)
    out += circle(x, mid_y, 14, fill="#ffffff", stroke=color, sw=1.8)
    if arrow_down:
        out += arrow(x, mid_y - 8, x, mid_y + 8, color=color, sw=1.8)
    else:
        out += arrow(x, mid_y + 8, x, mid_y - 8, color=color, sw=1.8)
    if label:
        out += text(x - 20, mid_y + 4, label, size=12, color=color, bold=True, anchor="end")
    return out


def res_v(x, y1, y2, label=None, color=INK):
    """Вертикальний резистор-зигзаг."""
    mid_y = (y1 + y2) / 2
    out = line(x, y1, x, mid_y - 16, color=color, sw=1.6)
    out += line(x, mid_y + 16, x, y2, color=color, sw=1.6)
    n = 4
    step = 32.0 / n
    pts = ["%.1f,%.1f" % (x, mid_y - 16)]
    for i in range(1, n):
        xx = x + (6 if i % 2 == 1 else -6)
        yy = mid_y - 16 + i * step
        pts.append("%.1f,%.1f" % (xx, yy))
    pts.append("%.1f,%.1f" % (x, mid_y + 16))
    out += '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), color)
    if label:
        out += text(x + 12, mid_y + 4, label, size=12, color=color, bold=True, anchor="start")
    return out


def res_h(x1, x2, y, label=None, color=INK):
    """Горизонтальний резистор."""
    mid_x = (x1 + x2) / 2
    out = line(x1, y, mid_x - 18, y, color=color, sw=1.6)
    out += line(mid_x + 18, y, x2, y, color=color, sw=1.6)
    n = 6
    step = 36.0 / n
    pts = ["%.1f,%.1f" % (mid_x - 18, y)]
    for i in range(1, n):
        xx = mid_x - 18 + i * step
        yy = y + (6 if i % 2 == 1 else -6)
        pts.append("%.1f,%.1f" % (xx, yy))
    pts.append("%.1f,%.1f" % (mid_x + 18, y))
    out += '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), color)
    if label:
        out += text(mid_x, y - 12, label, size=12, color=color, bold=True, anchor="middle")
    return out


def cap_v(x, y1, y2, label=None, color=NEG):
    """Вертикальний конденсатор."""
    mid_y = (y1 + y2) / 2
    out = line(x, y1, x, mid_y - 4, color=color, sw=1.6)
    out += line(x, mid_y + 4, x, y2, color=color, sw=1.6)
    out += line(x - 9, mid_y - 4, x + 9, mid_y - 4, color=color, sw=2.0)
    out += line(x - 9, mid_y + 4, x + 9, mid_y + 4, color=color, sw=2.0)
    if label:
        out += text(x + 14, mid_y + 4, label, size=12, color=color, bold=True, anchor="start")
    return out


def gnd_sym(x, y):
    """Символ заземлення."""
    out = line(x, y, x, y + 8, color=INK, sw=1.6)
    yy = y + 8
    for i, w in enumerate((14, 9, 4)):
        out += line(x - w / 2, yy + i * 3.5, x + w / 2, yy + i * 3.5, color=INK, sw=1.6)
    return out


def junc(x, y):
    """Точка з'єднання (вузол)."""
    return circle(x, y, 3.2, fill=INK, stroke=INK, sw=1.0)


# ── 1. Еквівалентна схема фотодіода та темновий струм ────────────────────────
def fig1_photodiode_equivalent():
    w, h = 820, 360
    frags = []

    # Ліва частина: Еквівалентна схема
    frags.append(rect(20, 15, 460, 330, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(250, 42, "Еквівалентна модель реального фотодіода", size=14, color=INK, bold=True))
    
    # Горизонтальні шини анода і катода
    y_top = 100
    y_bot = 265
    
    # Виводи фотодіода
    frags.append(line(40, y_top, 390, y_top, color=INK, sw=1.6))
    frags.append(line(40, y_bot, 430, y_bot, color=INK, sw=1.6))
    
    # Послідовний опір Rs
    frags.append(res_h(390, 430, y_top, label="Rs", color=MUTED))
    
    # Клеми Катод (K) і Анод (A)
    frags.append(circle(435, y_top, 3.5, fill="#ffffff", stroke=INK, sw=1.8))
    frags.append(circle(435, y_bot, 3.5, fill="#ffffff", stroke=INK, sw=1.8))
    frags.append(text(446, y_top + 4, "Катод (K)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(446, y_bot + 4, "Анод (A)", size=11, color=INK, anchor="start", bold=True))
    
    # 4 паралельні гілки
    # 1) Джерело фотоструму I_ph (світловий потік)
    x1 = 90
    frags.append(junc(x1, y_top))
    frags.append(junc(x1, y_bot))
    frags.append(isource_sym(x1, y_top, y_bot, label="I_ph", arrow_down=True, color=FIELD))
    # Промені світла
    frags.append(arrow(x1 - 34, y_top + 30, x1 - 18, y_top + 50, color="#e67e22", sw=1.8))
    frags.append(arrow(x1 - 34, y_top + 50, x1 - 18, y_top + 70, color="#e67e22", sw=1.8))
    frags.append(text(x1 - 42, y_top + 45, "hν", size=13, color="#d35400", bold=True))
    
    # 2) Джерело темнового струму I_d (теплова генерація)
    x2 = 180
    frags.append(junc(x2, y_top))
    frags.append(junc(x2, y_bot))
    frags.append(isource_sym(x2, y_top, y_bot, label="I_d(T)", arrow_down=True, color=POS))
    
    # 3) Ідеальний діод D_pn
    x3 = 270
    frags.append(junc(x3, y_top))
    frags.append(junc(x3, y_bot))
    frags.append(line(x3, y_bot, x3, 195, color=INK, sw=1.6))
    frags.append(line(x3, 160, x3, y_top, color=INK, sw=1.6))
    pts_d = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x3 - 8, 195, x3 + 8, 195, x3, 160)
    frags.append(f'<polygon points="{pts_d}" fill="#ffffff" stroke="{INK}" stroke-width="1.6"/>')
    frags.append(line(x3 - 8, 160, x3 + 8, 160, color=INK, sw=2.0))
    frags.append(text(x3 + 14, 180, "D_pn", size=11, color=INK, anchor="start"))
    
    # 4) Шунтуючий опір R_sh та бар'єрна ємність C_d
    x4 = 330
    frags.append(junc(x4, y_top))
    frags.append(junc(x4, y_bot))
    frags.append(res_v(x4, y_top, y_bot, label="R_sh", color=MUTED))
    
    x5 = 380
    frags.append(junc(x5, y_top))
    frags.append(junc(x5, y_bot))
    frags.append(cap_v(x5, y_top, y_bot, label="C_d", color=NEG))
    
    # Пояснювальний підпис знизу
    tb1, _, _ = textbox(250, 310, "I_total = I_ph + I_d(T) + I_diode + V_d / R_sh", size=12, fill="#ffffff", stroke=MUTED, bold=True)
    frags.append(tb1)
    
    # Права частина: Температурна залежність темнового струму
    frags.append(rect(500, 15, 300, 330, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(650, 42, "Експоненційне зростання I_d(T)", size=14, color=INK, bold=True))
    
    # Графік
    gx0, gy0 = 545, 275
    gw, gh = 230, 190
    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.5))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.5))
    frags.append(arrow(gx0 + gw - 5, gy0, gx0 + gw + 5, gy0, color=INK, sw=1.5))
    frags.append(arrow(gx0, gy0 - gh + 5, gx0, gy0 - gh - 5, color=INK, sw=1.5))
    
    frags.append(text(gx0 + gw - 5, gy0 + 20, "Температура T (°C)", size=11, color=INK, anchor="end"))
    frags.append(text(gx0 - 8, gy0 - gh + 15, "I_dark", size=12, color=POS, anchor="end", bold=True))
    
    # Крива при VR = 5V та VR = 0V
    pts_curve1 = []
    pts_curve2 = []
    for i in range(gw - 20):
        t_norm = i / (gw - 20)
        y_val1 = gy0 - 15 * math.exp(t_norm * 2.5)
        y_val2 = gy0 - 4 * math.exp(t_norm * 2.5)
        pts_curve1.append(f"{gx0 + i:.1f},{max(gy0 - gh + 15, y_val1):.1f}")
        pts_curve2.append(f"{gx0 + i:.1f},{max(gy0 - gh + 15, y_val2):.1f}")
        
    frags.append(f'<polyline points="{" ".join(pts_curve1)}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    frags.append(f'<polyline points="{" ".join(pts_curve2)}" fill="none" stroke="{NEG}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    
    frags.append(text(gx0 + 105, gy0 - 120, "Зміщення V_R = 5 В", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(gx0 + 125, gy0 - 40, "V_R = 0 В (Pv-режим)", size=11, color=NEG, bold=True, anchor="start"))
    
    tb_exp, _, _ = textbox(650, 75, "Подвоєння I_d кожні +8...+10 °C\n(генерація в збідненій зоні)", size=11, fill="#fff5f5", stroke=POS)
    frags.append(tb_exp)

    render(os.path.join(IMG, "photodiode-equivalent-dark-current.svg"), w, h, *frags)
    print("Generated photodiode-equivalent-dark-current.svg")


# ── 2. Пасивний резистор проти TIA ──────────────────────────────────────────
def fig2_passive_vs_transimpedance():
    w, h = 820, 340
    frags = []

    # Ліва половина: Пасивне перетворення (R_load)
    frags.append(rect(20, 15, 370, 310, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(205, 42, "Пасивний резистор: плаваючий потенціал", size=13, color=INK, bold=True))
    
    pdx = 100
    frags.append(line(pdx, 65, pdx, 90, color=INK, sw=1.6))
    frags.append(gnd_sym(pdx, 55))
    frags.append(circle(pdx, 115, 16, fill="#ffffff", stroke=INK, sw=1.6))
    pts_pd = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (pdx - 8, 122, pdx + 8, 122, pdx, 107)
    frags.append(f'<polygon points="{pts_pd}" fill="{INK}"/>')
    frags.append(line(pdx - 8, 107, pdx + 8, 107, color=INK, sw=2.0))
    frags.append(arrow(pdx - 26, 95, pdx - 14, 110, color="#e67e22", sw=1.8))
    frags.append(arrow(pdx - 26, 110, pdx - 14, 125, color="#e67e22", sw=1.8))
    
    frags.append(line(pdx, 131, pdx, 175, color=INK, sw=1.6))
    frags.append(junc(pdx, 175))
    frags.append(line(pdx, 175, 220, 175, color=INK, sw=1.6))
    frags.append(circle(225, 175, 3.5, fill="#ffffff", stroke=INK, sw=1.8))
    frags.append(text(235, 179, "V_out", size=12, color=POS, bold=True, anchor="start"))
    
    frags.append(res_v(pdx, 175, 255, label="R_L", color=INK))
    frags.append(gnd_sym(pdx, 255))
    
    frags.append(line(160, 175, 160, 195, color=MUTED, sw=1.4))
    frags.append(junc(160, 175))
    frags.append(cap_v(160, 195, 245, label="C_d + C_in", color=NEG))
    frags.append(line(160, 245, 160, 255, color=MUTED, sw=1.4))
    frags.append(gnd_sym(160, 255))
    
    tb_bad, _, _ = textbox(205, 285, "• V_out = I_ph · R_L гойдає напругу катода\n• Низька смуга: f_p = 1 / (2π · R_L · C_in)", size=10, fill="#fff5f5", stroke=POS)
    frags.append(tb_bad)

    # Права половина: Активний TIA (віртуальна земля)
    frags.append(rect(410, 15, 390, 310, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(605, 42, "Трансімпедансний підсилювач (TIA)", size=13, color=INK, bold=True))
    
    op_body, in_t, in_b, out_p = opamp_sym(640, 175, w=75, h=65, inv_top=True)
    frags.append(op_body)
    
    frags.append(line(in_b[0], in_b[1], in_b[0] - 25, in_b[1], color=INK, sw=1.6))
    frags.append(gnd_sym(in_b[0] - 25, in_b[1]))
    frags.append(text(in_b[0] - 30, in_b[1] + 16, "0 В", size=11, color=MUTED, anchor="end"))
    
    frags.append(line(in_t[0], in_t[1], in_t[0] - 95, in_t[1], color=INK, sw=1.6))
    v_node_x = in_t[0] - 70
    frags.append(junc(v_node_x, in_t[1]))
    
    tb_vg, _, _ = textbox(v_node_x - 30, in_t[1] - 40, "Віртуальна земля\nV_in(-) ≈ 0 В", size=10, fill="#eff6ff", stroke=NEG)
    frags.append(tb_vg)
    
    frags.append(line(v_node_x, in_t[1], v_node_x, 220, color=INK, sw=1.6))
    frags.append(circle(v_node_x, 235, 14, fill="#ffffff", stroke=INK, sw=1.6))
    pts_pd2 = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (v_node_x - 6, 241, v_node_x + 6, 241, v_node_x, 229)
    frags.append(f'<polygon points="{pts_pd2}" fill="{INK}"/>')
    frags.append(line(v_node_x - 6, 229, v_node_x + 6, 229, color=INK, sw=2.0))
    frags.append(line(v_node_x, 249, v_node_x, 260, color=INK, sw=1.6))
    frags.append(gnd_sym(v_node_x, 260))
    
    frags.append(arrow(v_node_x - 24, 220, v_node_x - 12, 232, color="#e67e22", sw=1.6))
    frags.append(arrow(v_node_x - 24, 232, v_node_x - 12, 244, color="#e67e22", sw=1.6))
    
    fb_y = 95
    frags.append(line(v_node_x, in_t[1], v_node_x, fb_y, color=INK, sw=1.6))
    frags.append(res_h(v_node_x, 690, fb_y, label="R_f", color=INK))
    frags.append(line(690, fb_y, 690, out_p[1], color=INK, sw=1.6))
    frags.append(junc(690, out_p[1]))
    
    frags.append(line(out_p[0], out_p[1], 745, out_p[1], color=INK, sw=1.8))
    frags.append(circle(750, out_p[1], 3.5, fill="#ffffff", stroke=INK, sw=1.8))
    frags.append(text(760, out_p[1] + 4, "V_out", size=12, color=POS, bold=True, anchor="start"))
    
    tb_good, _, _ = textbox(605, 285, "• Весь фотострум у R_f: V_out = -I_ph · R_f\n• Напруга діода зафіксована: dV/dt = 0", size=10, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb_good)

    render(os.path.join(IMG, "passive-vs-transimpedance.svg"), w, h, *frags)
    print("Generated passive-vs-transimpedance.svg")


# ── 3. Діаграма Боде та стабільність TIA ─────────────────────────────────────
def fig3_tia_bode_stability():
    w, h = 820, 360
    frags = []

    frags.append(rect(20, 15, 780, 330, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(410, 42, "Діаграма Боде петльового підсилення: компенсація ємністю C_f", size=14, color=INK, bold=True))

    ox, oy = 80, 280
    pw, ph = 680, 220
    
    frags.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    frags.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    frags.append(arrow(ox + pw - 5, oy, ox + pw + 5, oy, color=INK, sw=1.6))
    frags.append(arrow(ox, oy - ph + 5, ox, oy - ph - 5, color=INK, sw=1.6))
    
    frags.append(text(ox + pw - 10, oy + 24, "Частота f (логарифмічний масштаб)", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 10, oy - ph + 15, "Підсилення (дБ)", size=12, color=INK, anchor="end", bold=True))
    
    # 1) Розімкнене підсилення ОП |A(f)|
    f_gbw_x = ox + 560
    a0_y = oy - 190
    frags.append(line(ox, a0_y, ox + 60, a0_y, color=LINE, sw=2.2))
    frags.append(line(ox + 60, a0_y, f_gbw_x, oy, color=LINE, sw=2.2))
    frags.append(text(ox + 70, a0_y - 8, "|A(f)| ОП (-20 дБ/дек)", size=12, color=LINE, bold=True, anchor="start"))
    frags.append(circle(f_gbw_x, oy, 3.5, fill=LINE, stroke=LINE, sw=1.0))
    frags.append(text(f_gbw_x, oy + 18, "GBW", size=12, color=LINE, bold=True, anchor="middle"))
    
    # 2) Шумове підсилення 1/beta БЕЗ компенсації
    fz_x = ox + 160
    frags.append(line(ox, oy, fz_x, oy, color=POS, sw=2.0, dash="4,3"))
    
    fx_x = ox + 420
    fx_y = oy - 80
    frags.append(line(fz_x, oy, fx_x + 40, fx_y - 30, color=POS, sw=2.2, dash="4,3"))
    frags.append(circle(fx_x, fx_y, 4.5, fill=POS, stroke=POS, sw=1.2))
    
    frags.append(text(fz_x, oy + 18, "f_z = 1/(2π·R_f·C_in)", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(fx_x + 50, fx_y - 35, "1/β без C_f (+20 дБ/дек)", size=11, color=POS, bold=True, anchor="start"))
    
    tb_inst, _, _ = textbox(fx_x + 55, fx_y - 65, "ROC = 40 дБ/дек!\nΦ_m ≈ 0° (Генерація / дзвін)", size=10, fill="#fff1f2", stroke=POS)
    frags.append(tb_inst)

    # 3) Шумове підсилення 1/beta З компенсацією Cf
    fp_x = ox + 320
    fp_y = oy - 55
    
    frags.append(line(fz_x, oy, fp_x, fp_y, color=FIELD, sw=2.4))
    
    fc_x = ox + 475
    fc_y = oy - 55
    frags.append(line(fp_x, fp_y, fc_x + 50, fp_y, color=FIELD, sw=2.4))
    frags.append(circle(fc_x, fc_y, 4.5, fill=FIELD, stroke=FIELD, sw=1.2))
    
    frags.append(text(fp_x, oy + 18, "f_p = 1/(2π·R_f·C_f)", size=11, color=FIELD, anchor="middle", bold=True))
    frags.append(text(fc_x + 55, fc_y - 8, "1/β з C_f (полиця 1 + C_in/C_f)", size=11, color=FIELD, bold=True, anchor="start"))
    
    tb_st, _, _ = textbox(fc_x + 30, fc_y + 35, "ROC = 20 дБ/дек\nΦ_m ≈ 45°...65° (Баттерворт)", size=10, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb_st)
    
    tb_form, _, _ = textbox(ox + 140, oy - 150, "Оптимальна компенсація:\nC_f = √( C_in / (2π · R_f · GBW) )", size=11, fill="#ffffff", stroke=MUTED)
    frags.append(tb_form)

    render(os.path.join(IMG, "tia-bode-stability.svg"), w, h, *frags)
    print("Generated tia-bode-stability.svg")


# ── 4. Методи компенсації темнового струму ──────────────────────────────────
def fig4_dark_current_compensation():
    w, h = 820, 340
    frags = []

    # Ліва половина: Апаратна компенсація
    frags.append(rect(20, 15, 380, 310, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(210, 42, "Апаратна компенсація спареним діодом", size=13, color=INK, bold=True))
    
    op_body, in_t, in_b, out_p = opamp_sym(230, 160, w=70, h=60, inv_top=True)
    frags.append(op_body)
    
    pd1_x = 90
    frags.append(line(in_t[0], in_t[1], pd1_x, in_t[1], color=INK, sw=1.6))
    frags.append(line(pd1_x, in_t[1], pd1_x, 80, color=INK, sw=1.6))
    frags.append(circle(pd1_x, 65, 14, fill="#ffffff", stroke=INK, sw=1.6))
    pts_pd1 = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (pd1_x - 6, 70, pd1_x + 6, 70, pd1_x, 59)
    frags.append(f'<polygon points="{pts_pd1}" fill="{INK}"/>')
    frags.append(line(pd1_x - 6, 59, pd1_x + 6, 59, color=INK, sw=1.8))
    frags.append(line(pd1_x, 51, pd1_x, 40, color=INK, sw=1.6))
    frags.append(gnd_sym(pd1_x, 40))
    frags.append(arrow(pd1_x - 22, 55, pd1_x - 12, 65, color="#e67e22", sw=1.6))
    frags.append(text(pd1_x - 30, 75, "PD1\n(Світло)", size=10, color=INK, anchor="end"))
    
    pd2_x = 90
    frags.append(line(in_b[0], in_b[1], pd2_x, in_b[1], color=INK, sw=1.6))
    frags.append(res_h(pd2_x, in_b[0], in_b[1], label="R_f2", color=MUTED))
    frags.append(line(pd2_x, in_b[1], pd2_x, 240, color=INK, sw=1.6))
    frags.append(circle(pd2_x, 255, 14, fill="#333333", stroke=INK, sw=1.6))
    pts_pd2 = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (pd2_x - 6, 260, pd2_x + 6, 260, pd2_x, 249)
    frags.append(f'<polygon points="{pts_pd2}" fill="#ffffff"/>')
    frags.append(line(pd2_x - 6, 249, pd2_x + 6, 249, color="#ffffff", sw=1.8))
    frags.append(line(pd2_x, 269, pd2_x, 280, color=INK, sw=1.6))
    frags.append(gnd_sym(pd2_x, 280))
    frags.append(text(pd2_x - 22, 260, "PD2 (Темний)\nЕкранований", size=10, color=MUTED, anchor="end"))
    
    frags.append(line(130, in_t[1], 130, 105, color=INK, sw=1.6))
    frags.append(junc(130, in_t[1]))
    frags.append(res_h(130, 280, 105, label="R_f1", color=INK))
    frags.append(line(280, 105, 280, out_p[1], color=INK, sw=1.6))
    frags.append(junc(280, out_p[1]))
    
    frags.append(line(out_p[0], out_p[1], 345, out_p[1], color=INK, sw=1.8))
    frags.append(circle(350, out_p[1], 3.5, fill="#ffffff", stroke=INK, sw=1.8))
    frags.append(text(360, out_p[1] + 4, "V_out", size=12, color=POS, bold=True, anchor="start"))
    
    frags.append(text(210, 305, "I_d1(T) ≈ I_d2(T) віднімаються синфазно", size=11, color=FIELD, anchor="middle", bold=True))

    # Права половина: CDS
    frags.append(rect(420, 15, 380, 310, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(610, 42, "Подвійна корельована вибірка (CDS)", size=13, color=INK, bold=True))
    
    tx0, ty0 = 460, 130
    tw = 310
    
    frags.append(line(tx0, ty0, tx0 + tw, ty0, color=INK, sw=1.4))
    frags.append(text(tx0 + tw - 5, ty0 + 18, "Час (t)", size=11, color=INK, anchor="end"))
    
    frags.append(line(tx0, ty0 - 45, tx0 + 70, ty0 - 45, color=MUTED, sw=1.8))
    frags.append(line(tx0 + 70, ty0 - 45, tx0 + 70, ty0 - 75, color=MUTED, sw=1.8))
    frags.append(line(tx0 + 70, ty0 - 75, tx0 + 200, ty0 - 75, color="#e67e22", sw=2.2))
    frags.append(line(tx0 + 200, ty0 - 75, tx0 + 200, ty0 - 45, color=MUTED, sw=1.8))
    frags.append(line(tx0 + 200, ty0 - 45, tx0 + tw, ty0 - 45, color=MUTED, sw=1.8))
    
    frags.append(text(tx0 + 35, ty0 - 55, "LED ВИМК", size=10, color=MUTED, anchor="middle"))
    frags.append(text(tx0 + 135, ty0 - 85, "LED УВІМК (Імпульс світла)", size=11, color="#d35400", bold=True, anchor="middle"))
    
    frags.append(line(tx0, ty0 - 15, tx0 + 70, ty0 - 15, color=POS, sw=2.0))
    frags.append(line(tx0 + 70, ty0 - 15, tx0 + 85, ty0 - 55, color=POS, sw=2.0))
    frags.append(line(tx0 + 85, ty0 - 55, tx0 + 200, ty0 - 55, color=POS, sw=2.0))
    frags.append(line(tx0 + 200, ty0 - 55, tx0 + 215, ty0 - 15, color=POS, sw=2.0))
    frags.append(line(tx0 + 215, ty0 - 15, tx0 + tw, ty0 - 15, color=POS, sw=2.0))
    
    s1_x = tx0 + 45
    s2_x = tx0 + 150
    frags.append(circle(s1_x, ty0 - 15, 4.0, fill=NEG, stroke=NEG, sw=1.0))
    frags.append(circle(s2_x, ty0 - 55, 4.0, fill=FIELD, stroke=FIELD, sw=1.0))
    
    frags.append(line(s1_x, ty0 - 15, s1_x, ty0 + 15, color=NEG, sw=1.2, dash="3,2"))
    frags.append(line(s2_x, ty0 - 55, s2_x, ty0 + 15, color=FIELD, sw=1.2, dash="3,2"))
    
    frags.append(text(s1_x, ty0 + 28, "S₁: V_dark", size=11, color=NEG, bold=True, anchor="middle"))
    frags.append(text(s2_x, ty0 + 28, "S₂: V_sig+V_dark", size=11, color=FIELD, bold=True, anchor="middle"))
    
    tb_cds, _, _ = textbox(610, 245, "Результат CDS:\nV_clean = S₂ − S₁ = V_sig\nПовне усунення I_d(T) та шуму 1/f", size=10, fill="#eff6ff", stroke=NEG)
    frags.append(tb_cds)

    render(os.path.join(IMG, "dark-current-compensation-methods.svg"), w, h, *frags)
    print("Generated dark-current-compensation-methods.svg")


# ── 5. Топологія друкованої плати та Guard Ring ─────────────────────────────
def fig5_guard_ring_layout():
    w, h = 820, 320
    frags = []

    frags.append(rect(20, 15, 780, 290, fill="#fafafa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(410, 42, "Топологія друкованої плати: захисне кільце (Guard Ring) інвертуючого входу", size=14, color=INK, bold=True))

    pcb_x, pcb_y, pcb_w, pcb_h = 60, 60, 420, 220
    frags.append(f'<rect x="{pcb_x}" y="{pcb_y}" width="{pcb_w}" height="{pcb_h}" rx="8" fill="#1b4d3e" stroke="{INK}" stroke-width="1.8"/>')
    
    ic_cx, ic_cy = pcb_x + 230, pcb_y + 110
    frags.append(f'<rect x="{ic_cx - 40}" y="{ic_cy - 45}" width="80" height="90" rx="3" fill="#2d3748" stroke="#1a202c" stroke-width="1.5"/>')
    frags.append(circle(ic_cx - 25, ic_cy - 30, 4, fill="#1a202c", stroke="#4a5568", sw=1))
    frags.append(text(ic_cx, ic_cy + 5, "OPA / TIA", size=11, color="#e2e8f0", bold=True, anchor="middle"))
    
    pads_l = []
    pads_r = []
    for i in range(4):
        py = ic_cy - 33 + i * 22
        frags.append(f'<rect x="{ic_cx - 65}" y="{py - 5}" width="20" height="10" fill="#ecc94b" stroke="#b7791f" stroke-width="1"/>')
        pads_l.append((ic_cx - 55, py))
        frags.append(f'<rect x="{ic_cx + 45}" y="{py - 5}" width="20" height="10" fill="#ecc94b" stroke="#b7791f" stroke-width="1"/>')
        pads_r.append((ic_cx + 55, py))
        
    frags.append(text(pads_l[1][0] - 14, pads_l[1][1] + 4, "2: −IN", size=11, color="#ffffff", bold=True, anchor="end"))
    frags.append(text(pads_l[2][0] - 14, pads_l[2][1] + 4, "3: +IN (0V)", size=10, color="#68d391", anchor="end"))
    frags.append(text(pads_l[3][0] - 14, pads_l[3][1] + 4, "4: V− (−15V)", size=10, color="#fc8181", anchor="end"))
    frags.append(text(pads_r[1][0] + 14, pads_r[1][1] + 4, "7: V+ (+15V)", size=10, color="#fc8181", anchor="start"))
    frags.append(text(pads_r[2][0] + 14, pads_r[2][1] + 4, "6: OUT", size=10, color="#63b3ed", anchor="start"))
    
    node_in_x = pcb_x + 60
    node_in_y = pads_l[1][1]
    frags.append(line(node_in_x, node_in_y, pads_l[1][0], node_in_y, color="#ecc94b", sw=3.5))
    frags.append(circle(node_in_x, node_in_y, 7, fill="#ecc94b", stroke="#b7791f", sw=1.5))
    frags.append(text(node_in_x, node_in_y - 12, "Анод діода", size=10, color="#ffffff", bold=True, anchor="middle"))
    
    guard_pts = [
        f"{pads_l[2][0]},{pads_l[2][1]}",
        f"{pads_l[2][0] - 30},{pads_l[2][1]}",
        f"{pads_l[2][0] - 30},{pads_l[0][1] - 15}",
        f"{node_in_x - 20},{pads_l[0][1] - 15}",
        f"{node_in_x - 20},{node_in_y + 25}",
        f"{pads_l[2][0] - 15},{node_in_y + 25}",
        f"{pads_l[2][0] - 15},{pads_l[2][1]}"
    ]
    frags.append(f'<polyline points="{" ".join(guard_pts)}" fill="none" stroke="#48bb78" stroke-width="4.0"/>')
    
    frags.append(arrow(pcb_x + 120, pcb_y + 195, pcb_x + 120, pcb_y + 165, color="#fc8181", sw=1.5))
    frags.append(text(pcb_x + 120, pcb_y + 208, "Витік від V− (-15V)", size=9, color="#fc8181", anchor="middle"))
    
    tb_gr1, _, _ = textbox(640, 110, "Принцип Guard Ring:\n• Кільце з'єднане з +IN (0 В вірт. землі)\n• ΔV між Guard і −IN = V_os ≈ 0 мВ\n• Струм витоку I_leak = 0 / R_pcb = 0 пА!\n• Струми від шин V± стікають у Guard", size=10, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb_gr1)
    
    tb_gr2, _, _ = textbox(640, 225, "Правила монтажу:\n• Зняти паяльну маску над кільцем\n• Відмивання залишків флюсу (IPA)\n• Тефлонові стійки (PTFE) при I < 100 фА\n• Резистор Rf безпосередньо над кільцем", size=10, fill="#ffffff", stroke=MUTED)
    frags.append(tb_gr2)

    render(os.path.join(IMG, "guard-ring-pcb-layout.svg"), w, h, *frags)
    print("Generated guard-ring-pcb-layout.svg")


def main():
    fig1_photodiode_equivalent()
    fig2_passive_vs_transimpedance()
    fig3_tia_bode_stability()
    fig4_dark_current_compensation()
    fig5_guard_ring_layout()
    print("All figures successfully generated.")


if __name__ == "__main__":
    main()
