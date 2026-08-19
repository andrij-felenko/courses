# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. bjt-output-curves: Сімейство вихідних характеристик BJT ───────────────
def fig_bjt_output_curves():
    W, H = 880, 560
    p = []
    
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W/2, 50, "Сімейство кривих I_C(V_CE) при фіксованих струмах бази I_B у схемі зі спільним емітером", size=10, color=MUTED, italic=True))
    
    ox, oy = 180, 450
    gw, gh = 630, 360
    
    # Області кольоровими прямокутниками
    p.append(rect(ox, oy - gh, 55, gh, fill="#fff2e8", stroke="#ffbb96", sw=1, rx=0))
    p.append(text(ox + 27, oy - gh + 22, "Насичення", size=10, color="#d4380d", bold=True))
    p.append(text(ox + 27, oy - gh + 38, "V_CE < V_CE(sat)", size=9, color="#d4380d"))
    
    p.append(rect(ox + 55, oy - gh, 455, gh, fill="#f6ffed", stroke="#b7eb8f", sw=1, rx=0))
    p.append(text(ox + 280, oy - gh + 22, "Лінійна активна область (Forward-Active)", size=11, color="#389e0d", bold=True))
    p.append(text(ox + 280, oy - gh + 38, "I_C = β · I_B · (1 + V_CE / V_A)  —  кероване джерело струму", size=9.5, color="#389e0d"))
    
    p.append(rect(ox + 510, oy - gh, 120, gh, fill="#fff1f0", stroke="#ffa39e", sw=1, rx=0))
    p.append(text(ox + 570, oy - gh + 22, "Лавинний пробій", size=10, color=POS, bold=True))
    p.append(text(ox + 570, oy - gh + 38, "V_CE > BV_CEO", size=9, color=POS))
    
    # Сітка
    for vx in range(1, 13):
        x = ox + vx * 50
        p.append(line(x, oy, x, oy - gh, color="#e8e8e8", sw=0.8, dash="3 3"))
    for vy in range(1, 8):
        y = oy - vy * 50
        p.append(line(ox, y, ox + gw, y, color="#e8e8e8", sw=0.8, dash="3 3"))
        
    p.append(line(40, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    p.append(arrow(ox + gw + 10, oy, ox + gw + 25, oy, color=INK, sw=1.8))
    p.append(text(ox + gw + 30, oy + 4, "V_CE (В)", size=11, color=INK, anchor="start", bold=True))
    
    p.append(line(ox, oy + 15, ox, oy - gh - 20, color=INK, sw=1.8))
    p.append(arrow(ox, oy - gh - 10, ox, oy - gh - 25, color=INK, sw=1.8))
    p.append(text(ox - 10, oy - gh - 22, "I_C (мА)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 8, oy + 16, "0", size=10, color=INK, anchor="end"))
    
    va_x = 75
    p.append(circle(va_x, oy, 3.5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(va_x, oy + 18, "−V_A", size=11, color=POS, bold=True))
    p.append(text(va_x, oy + 34, "Напруга Ерлі", size=9, color=MUTED))
    
    ib_list = [
        (10, 50, "I_B1 = 10 мкА"),
        (20, 100, "I_B2 = 20 мкА"),
        (30, 150, "I_B3 = 30 мкА"),
        (40, 200, "I_B4 = 40 мкА"),
        (50, 250, "I_B5 = 50 мкА"),
    ]
    
    for ib_val, ic_base, label_text in ib_list:
        p.append(line(va_x, oy, ox + 55, oy - ic_base - (55 / (ox + gw - va_x)) * (ic_base * 0.4), color="#8c8c8c", sw=1, dash="4 4"))
        pts = []
        for step in range(12):
            v = step * 0.05
            x = ox + v * 100
            ratio = 1.0 - math.exp(-v * 10)
            y = oy - (ic_base * ratio)
            pts.append((x, y))
            
        for step in range(1, 20):
            v = 0.55 + step * 0.5
            x = ox + v * 50
            if x > ox + 500:
                break
            ic_active = ic_base * (1.0 + (x - ox) / (ox - va_x + 500))
            y = oy - ic_active
            pts.append((x, y))
            
        v_break = 10.0
        for step in range(1, 8):
            v = v_break + step * 0.3
            x = ox + v * 50
            if x > ox + gw:
                break
            ic_active = ic_base * (1.0 + (x - ox) / (ox - va_x + 500))
            delta_break = ic_base * 0.08 * math.exp(step * 0.9)
            y = oy - (ic_active + delta_break)
            if y < oy - gh + 10:
                break
            pts.append((x, y))
            
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=2.2))
            
        # Підпис струму бази в активній зоні
        p.append(text(ox + 420, oy - ic_base * 1.3 - 6, label_text, size=9, color=NEG, anchor="start", bold=True))
        
    p.append(line(ox, oy - 3, ox + 500, oy - 4, color="#595959", sw=2, dash="5 3"))
    p.append(line(ox + 500, oy - 4, ox + 550, oy - 70, color="#595959", sw=2))
    p.append(text(ox + 230, oy + 16, "Відсічка: I_B = 0,  I_C ≈ I_CEO ≈ (β + 1) · I_CBO", size=9, color="#595959", bold=True))
    
    # Гіпербола P_D(max)
    hyp_pts = []
    p_max_const = 22000
    for vx in range(80, 620, 10):
        x = ox + vx
        ic_p = p_max_const / vx
        y = oy - ic_p
        if 0 <= y - (oy - gh) <= gh:
            hyp_pts.append((x, y))
    for i in range(len(hyp_pts) - 1):
        p.append(line(hyp_pts[i][0], hyp_pts[i][1], hyp_pts[i+1][0], hyp_pts[i+1][1], color=POS, sw=1.8, dash="6 3"))
    if hyp_pts:
        p.append(text(hyp_pts[len(hyp_pts)//2][0] + 15, hyp_pts[len(hyp_pts)//2][1] - 14, "P_D(max) = V_CE · I_C", size=9.5, color=POS, bold=True))
        
    p.append(rect(ox + 100, oy - 320, 200, 52, fill="#ffffff", stroke="#91d5ff", sw=1.2, rx=4))
    p.append(text(ox + 200, oy - 302, "Диференційний опір r_o:", size=9.5, color=INK, bold=True))
    p.append(text(ox + 200, oy - 284, "r_o = ΔV_CE / ΔI_C ≈ V_A / I_C", size=9.5, color=NEG, bold=True))
    
    p.append(line(ox + 27, oy, ox + 27, oy + 18, color="#d4380d", sw=1.2))
    p.append(text(ox + 27, oy + 30, "V_CE(sat) ~ 0.2 В", size=9, color="#d4380d", bold=True))
    
    p.append(line(ox + 510, oy, ox + 510, oy + 18, color=POS, sw=1.2))
    p.append(text(ox + 510, oy + 30, "BV_CEO", size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "bjt-output-curves.svg"), W, H, *p,
           title="Вихідні характеристики біполярного транзистора (BJT)")


# ── 2. mosfet-output-curves: Сімейство вихідних характеристик MOSFET ──────────
def fig_mosfet_output_curves():
    W, H = 880, 560
    p = []
    
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W/2, 50, "Сімейство кривих I_D(V_DS) при фіксованих напругах затвор-витік V_GS", size=10, color=MUTED, italic=True))
    
    ox, oy = 80, 450
    gw, gh = 740, 360
    
    for vx in range(1, 13):
        x = ox + vx * 60
        p.append(line(x, oy, x, oy - gh, color="#e8e8e8", sw=0.8, dash="3 3"))
    for vy in range(1, 8):
        y = oy - vy * 50
        p.append(line(ox, y, ox + gw, y, color="#e8e8e8", sw=0.8, dash="3 3"))
        
    p.append(rect(ox, oy - gh, 190, gh, fill="#e6f7ff", stroke="#91d5ff", sw=0.8, rx=0))
    p.append(text(ox + 95, oy - gh + 22, "Тріодна область (Triode)", size=11, color="#096dd9", bold=True))
    p.append(text(ox + 95, oy - gh + 38, "V_DS < V_GS − V_th", size=9.5, color="#096dd9"))
    p.append(text(ox + 95, oy - gh + 54, "Керований резистор R_DS(on)", size=9, color="#096dd9"))
    
    p.append(rect(ox + 190, oy - gh, gw - 190, gh, fill="#f6ffed", stroke="#b7eb8f", sw=0.8, rx=0))
    p.append(text(ox + 460, oy - gh + 22, "Область насичення / перекриття каналу (Saturation)", size=11, color="#389e0d", bold=True))
    p.append(text(ox + 460, oy - gh + 38, "V_DS ≥ V_GS − V_th  (pinch-off біля стоку)", size=9.5, color="#389e0d"))
    p.append(text(ox + 460, oy - gh + 54, "I_D = ½ · μ_n C_ox (W/L) (V_GS − V_th)² · (1 + λ · V_DS)", size=9.5, color="#389e0d"))
    
    p.append(line(ox, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    p.append(arrow(ox + gw + 10, oy, ox + gw + 25, oy, color=INK, sw=1.8))
    p.append(text(ox + gw + 30, oy + 4, "V_DS (В)", size=11, color=INK, anchor="start", bold=True))
    
    p.append(line(ox, oy + 15, ox, oy - gh - 20, color=INK, sw=1.8))
    p.append(arrow(ox, oy - gh - 10, ox, oy - gh - 25, color=INK, sw=1.8))
    p.append(text(ox - 10, oy - gh - 22, "I_D (мА)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 8, oy + 16, "0", size=10, color=INK, anchor="end"))
    
    pinch_pts = []
    for step in range(0, 55):
        v = step * 0.08
        x = ox + v * 60
        id_val = 18 * (v ** 2)
        y = oy - id_val
        if y < oy - gh + 60:
            break
        pinch_pts.append((x, y))
    for i in range(len(pinch_pts) - 1):
        p.append(line(pinch_pts[i][0], pinch_pts[i][1], pinch_pts[i+1][0], pinch_pts[i+1][1], color="#d46b08", sw=2, dash="5 4"))
    p.append(text(pinch_pts[-1][0] + 14, pinch_pts[-1][1] + 16, "Межа насичення: V_DS = V_GS − V_th", size=9.5, color="#d46b08", bold=True, anchor="start"))
    
    vgs_list = [
        (2.5, 1.0, "V_GS1 = 2.5 В (V_ov = 1.0 В)"),
        (3.0, 1.5, "V_GS2 = 3.0 В (V_ov = 1.5 В)"),
        (3.5, 2.0, "V_GS3 = 3.5 В (V_ov = 2.0 В)"),
        (4.0, 2.5, "V_GS4 = 4.0 В (V_ov = 2.5 В)"),
        (4.5, 3.0, "V_GS5 = 4.5 В (V_ov = 3.0 В)"),
    ]
    
    lambda_param = 0.03
    for vgs, vov, label in vgs_list:
        pts = []
        v_ds_sat = vov
        id_sat = 18 * (vov ** 2)
        
        steps_triode = 20
        for s in range(steps_triode + 1):
            vds = (s / steps_triode) * v_ds_sat
            x = ox + vds * 60
            id_curr = 36 * (vov * vds - 0.5 * (vds ** 2))
            y = oy - id_curr
            pts.append((x, y))
            
        steps_sat = 40
        for s in range(1, steps_sat + 1):
            vds = v_ds_sat + s * 0.2
            x = ox + vds * 60
            if x > ox + gw - 30:
                break
            id_curr = id_sat * (1.0 + lambda_param * (vds - v_ds_sat))
            y = oy - id_curr
            if y < oy - gh + 40:
                break
            pts.append((x, y))
            
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=2.2))
            
        if pts:
            p.append(text(pts[-1][0] + 8, pts[-1][1] + 3, label, size=9, color=NEG, anchor="start", bold=True))
            
    p.append(line(ox, oy - 2, ox + gw - 40, oy - 2, color="#595959", sw=2, dash="5 3"))
    p.append(text(ox + 380, oy + 16, "Відсічка: V_GS < V_th (струм I_D ≈ 0)", size=9.5, color="#595959", bold=True))
    
    p.append(line(ox, oy, ox + 60, oy - 140, color="#cf1322", sw=1.5, dash="3 3"))
    p.append(text(ox + 70, oy - 120, "Нахил = 1 / R_DS(on)", size=9.5, color="#cf1322", bold=True))
    
    p.append(rect(ox + 480, oy - 100, 240, 56, fill="#ffffff", stroke="#d9d9d9", sw=1.2, rx=4))
    p.append(text(ox + 600, oy - 82, "Модуляція довжини каналу (CLM):", size=9, color=INK, bold=True))
    p.append(text(ox + 600, oy - 66, "Нахил кривої в насиченні: λ = 1/V_A", size=9, color=MUTED))
    p.append(text(ox + 600, oy - 50, "r_o = 1 / (λ · I_D) — вихідний опір", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "mosfet-output-curves.svg"), W, H, *p,
           title="Вихідні характеристики польового транзистора (MOSFET)")


# ── 3. load-line-dc-ac: Статична й динамічна навантажувальні прямі ────────────
def fig_load_line_dc_ac():
    W, H = 880, 580
    p = []
    
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W/2, 50, "Побудова точки спокою Q та визначення максимального неспотвореного розмаху сигналу", size=10, color=MUTED, italic=True))
    
    ox, oy = 90, 460
    gw, gh = 710, 380
    
    for vx in range(1, 13):
        x = ox + vx * 55
        p.append(line(x, oy, x, oy - gh, color="#f0f0f0", sw=0.8))
    for vy in range(1, 9):
        y = oy - vy * 45
        p.append(line(ox, y, ox + gw, y, color="#f0f0f0", sw=0.8))
        
    p.append(line(ox, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    p.append(arrow(ox + gw + 10, oy, ox + gw + 25, oy, color=INK, sw=1.8))
    p.append(text(ox + gw + 30, oy + 4, "V_CE (В)", size=11, color=INK, anchor="start", bold=True))
    
    p.append(line(ox, oy + 15, ox, oy - gh - 20, color=INK, sw=1.8))
    p.append(arrow(ox, oy - gh - 10, ox, oy - gh - 25, color=INK, sw=1.8))
    p.append(text(ox - 10, oy - gh - 22, "I_C (мА)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 8, oy + 16, "0", size=10, color=INK, anchor="end"))
    
    curves_y = [40, 90, 150, 210, 270, 330]
    for idx, cy in enumerate(curves_y):
        pts = [(ox, oy)]
        for step in range(1, 8):
            pts.append((ox + step * 5, oy - cy * (1 - math.exp(-step * 0.6))))
        for step in range(8, 125):
            x = ox + step * 5.5
            if x > ox + gw - 40:
                break
            y = oy - (cy * (1 - math.exp(-4.8)) + (x - ox) * 0.05)
            pts.append((x, y))
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color="#bfbfbf", sw=1.2))
        p.append(text(pts[-1][0] + 6, pts[-1][1] + 3, "I_B%d" % (idx + 1), size=9, color="#8c8c8c", anchor="start"))
        
    x_vcc = ox + 520
    y_ic_dc = oy - 310
    
    p.append(line(ox, y_ic_dc, x_vcc, oy, color=POS, sw=2.4))
    p.append(circle(x_vcc, oy, 4, fill=POS, stroke=POS, sw=1.5))
    p.append(circle(ox, y_ic_dc, 4, fill=POS, stroke=POS, sw=1.5))
    
    p.append(text(x_vcc, oy + 18, "V_CC", size=10, color=POS, bold=True))
    p.append(text(ox - 10, y_ic_dc + 4, "V_CC / R_C", size=9.5, color=POS, anchor="end", bold=True))
    p.append(text(x_vcc - 80, oy - 65, "DC навантажувальна пряма", size=10, color=POS, bold=True))
    p.append(text(x_vcc - 80, oy - 48, "Нахил = −1 / R_DC", size=9, color=POS))
    
    xq, yq = ox + 260, oy - 155
    p.append(circle(xq, yq, 6, fill=FIELD, stroke=INK, sw=2))
    p.append(text(xq + 14, yq - 12, "Q (V_CEQ, I_CQ)", size=11, color=FIELD, bold=True, anchor="start"))
    
    p.append(line(xq, yq, xq, oy, color=FIELD, sw=1.2, dash="4 4"))
    p.append(line(xq, yq, ox, yq, color=FIELD, sw=1.2, dash="4 4"))
    p.append(text(xq, oy + 18, "V_CEQ", size=10, color=FIELD, bold=True))
    p.append(text(ox - 10, yq + 4, "I_CQ", size=10, color=FIELD, anchor="end", bold=True))
    
    x_ac_max = ox + 420
    y_ac_max = oy - 360
    x_ac_min = ox + 100
    
    p.append(line(x_ac_min, y_ac_max, x_ac_max, oy, color=NEG, sw=2.4, dash="7 3"))
    p.append(circle(x_ac_max, oy, 4, fill=NEG, stroke=NEG, sw=1.5))
    p.append(text(x_ac_max, oy + 18, "V_CE(max,ac)", size=9.5, color=NEG, bold=True))
    p.append(text(ox + 120, y_ac_max + 18, "AC навантажувальна пряма", size=10, color=NEG, bold=True))
    p.append(text(ox + 120, y_ac_max + 34, "Нахил = −1 / (R_C || R_L)", size=9, color=NEG))
    
    delta_v = 120
    p.append(line(xq - delta_v, oy + 38, xq + delta_v, oy + 38, color=FIELD, sw=1.8))
    p.append(line(xq - delta_v, oy + 32, xq - delta_v, oy + 44, color=FIELD, sw=1.8))
    p.append(line(xq + delta_v, oy + 32, xq + delta_v, oy + 44, color=FIELD, sw=1.8))
    p.append(text(xq, oy + 54, "Максимальний неспотворений розмах напруги V_pp", size=9.5, color=FIELD, bold=True))
    
    p.append(rect(ox, oy - gh, 40, gh, fill="#fff2e8", stroke="#ffbb96", sw=1, rx=0))
    p.append(text(ox + 20, oy - gh + 18, "Кліпування", size=9, color="#d4380d", bold=True))
    p.append(text(ox + 20, oy - gh + 34, "насиченням", size=9, color="#d4380d"))
    
    p.append(rect(x_vcc, oy - gh, gw - 520, gh, fill="#fff1f0", stroke="#ffa39e", sw=1, rx=0))
    p.append(text(x_vcc + 50, oy - gh + 18, "Кліпування", size=9, color=POS, bold=True))
    p.append(text(x_vcc + 50, oy - gh + 34, "відсічкою", size=9, color=POS))

    render(os.path.join(OUT, "load-line-dc-ac.svg"), W, H, *p,
           title="Статична та динамічна навантажувальні прямі (DC/AC Load Lines)")


# ── 4. bjt-early-physics: Фізичні механізми (Ерлі в BJT та перекриття MOSFET) ──
def fig_bjt_early_physics():
    W, H = 880, 440
    p = []
    
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W/2, 50, "Зміна ефективної геометрії активної зони під дією високої вихідної напруги", size=10, color=MUTED, italic=True))
    
    p.append(rect(25, 75, 395, 335, fill="#fbfbfb", stroke="#d9d9d9", sw=1.2, rx=8))
    p.append(text(222, 100, "BJT: Модуляція ширини бази (ефект Ерлі)", size=11.5, color=INK, bold=True))
    
    p.append(rect(45, 130, 85, 110, fill="#e6f7ff", stroke="#69c0ff", sw=1.5, rx=0))
    p.append(text(87, 175, "n+ (Емітер)", size=10, color="#0050b3", bold=True))
    p.append(text(87, 195, "сильно легований", size=9, color="#0050b3"))
    
    p.append(rect(130, 130, 55, 110, fill="#fff1f0", stroke="#ff7875", sw=1.5, rx=0))
    p.append(text(157, 175, "p (База)", size=9.5, color="#a8071a", bold=True))
    p.append(text(157, 195, "слабо", size=9, color="#a8071a"))
    
    p.append(rect(185, 130, 75, 110, fill="#fffbe6", stroke="#ffe58f", sw=1.5, rx=0))
    p.append(text(222, 172, "Збіднений шар", size=9, color="#ad6800", bold=True))
    p.append(text(222, 190, "колектора W_dep", size=9, color="#ad6800"))
    
    p.append(rect(260, 130, 145, 110, fill="#e6f7ff", stroke="#69c0ff", sw=1.5, rx=0))
    p.append(text(332, 180, "n (Колектор)", size=10, color="#0050b3", bold=True))
    
    p.append(arrow(225, 260, 170, 260, color=POS, sw=1.8))
    p.append(text(222, 280, "Ріст V_CE розширює збіднений шар углиб бази", size=9, color=POS, bold=True))
    
    p.append(line(130, 310, 185, 310, color=FIELD, sw=2))
    p.append(line(130, 305, 130, 315, color=FIELD, sw=1.5))
    p.append(line(185, 305, 185, 315, color=FIELD, sw=1.5))
    p.append(text(157, 328, "W_B(eff) менша", size=9, color=FIELD, bold=True))
    
    p.append(text(222, 362, "Результат: градієнт концентрації dn/dx росте →", size=9, color=INK))
    p.append(text(222, 382, "Струм колектора I_C збільшується з ростом V_CE", size=9, color=NEG, bold=True))
    
    
    p.append(rect(455, 75, 400, 335, fill="#fbfbfb", stroke="#d9d9d9", sw=1.2, rx=8))
    p.append(text(655, 100, "MOSFET: Модуляція довжини каналу (CLM)", size=11.5, color=INK, bold=True))
    
    p.append(rect(475, 155, 360, 85, fill="none", stroke="#adc6ff", sw=1.2, rx=0))
    p.append(rect(475, 200, 360, 40, fill="#f0f5ff", stroke="#adc6ff", sw=1.2, rx=0))
    p.append(text(655, 224, "p-тип кремнієва підкладка (Bulk)", size=9, color="#1d39c4"))
    
    p.append(rect(475, 155, 65, 45, fill="#e6f7ff", stroke="#69c0ff", sw=1.5, rx=0))
    p.append(text(507, 182, "n+ Витік", size=9.5, color="#0050b3", bold=True))
    
    p.append(rect(770, 155, 65, 45, fill="#e6f7ff", stroke="#69c0ff", sw=1.5, rx=0))
    p.append(text(802, 182, "n+ Стік", size=9.5, color="#0050b3", bold=True))
    
    p.append(rect(540, 145, 230, 10, fill="#fffbe6", stroke="#d4b106", sw=1, rx=0))
    p.append(rect(540, 120, 230, 25, fill="#d9d9d9", stroke="#8c8c8c", sw=1.5, rx=0))
    p.append(text(655, 137, "Затвор (Gate, V_GS > V_th)", size=9.5, color=INK, bold=True))
    
    p.append(rect(540, 155, 150, 45, fill="#b7eb8f", stroke="#52c41a", sw=1, rx=0))
    p.append(text(615, 182, "Канал", size=9, color="#237804", bold=True))
    
    p.append(rect(690, 155, 80, 45, fill="#fff2e8", stroke="#ffbb96", sw=1, rx=0))
    p.append(text(730, 182, "Pinch-off", size=9, color="#d4380d", bold=True))

    
    p.append(line(540, 255, 690, 255, color=FIELD, sw=2))
    p.append(line(540, 250, 540, 260, color=FIELD, sw=1.5))
    p.append(line(690, 250, 690, 260, color=FIELD, sw=1.5))
    p.append(text(615, 275, "Ефективна довжина L_eff = L − ΔL", size=9, color=FIELD, bold=True))
    
    p.append(line(690, 255, 770, 255, color=POS, sw=2))
    p.append(line(770, 250, 770, 260, color=POS, sw=1.5))
    p.append(text(730, 275, "ΔL", size=9, color=POS, bold=True))
    
    p.append(text(655, 360, "Зростання V_DS розширює зону перекриття ΔL →", size=9, color=INK))
    p.append(text(655, 380, "L_eff зменшується, струм I_D ∝ 1/L_eff зростає", size=9, color=NEG, bold=True))

    render(os.path.join(OUT, "bjt-early-physics.svg"), W, H, *p,
           title="Фізика неідеальностей: ефект Ерлі та модуляція довжини каналу")


if __name__ == "__main__":
    fig_bjt_output_curves()
    fig_mosfet_output_curves()
    fig_load_line_dc_ac()
    fig_bjt_early_physics()
    print("All figures generated successfully.")