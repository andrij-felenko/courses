# -*- coding: utf-8 -*-
"""Фігури до теми «Тест ємності: електронне навантаження й справжня крива розряду».
Запуск: python figs.py  → записує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_LION  = "#c0392b"   # Li-ion — червоний
C_LFP   = "#caa24a"   # LiFePO4 — золотаво-бронзовий
C_SOCL2 = "#2457d6"   # Li-SOCl2 — темно-синій
C_MNO2  = "#8e44ad"   # Li-MnO2 — фіолетовий
C_ALK   = "#d35400"   # Alkaline — помаранчевий
C_PULSE = "#27ae60"   # Імпульс — зелений


# ── 1. Профілі навантаження (CC, CR, CP, Pulsed) ────────────────────────────
def fig_load_modes():
    W, H = 880, 430
    f = [text(W / 2, 28, "Режими навантаження батареї: поведінка струму при падінні напруги", size=15, bold=True)]
    
    pw, ph = 195, 350
    top_y = 55
    xs = [25, 235, 445, 655]
    
    modes = [
        ("CC (Постійний струм)", "I = const", "Лабораторні тести",
         "Струм фіксований. Потужність падає разом із напругою.",
         "Стандарт для даташитів"),
        
        ("CR (Постійний опір)", "R = const", "Пасивні схеми, резистори",
         "Струм спадає лінійно з напругою. Менше навантаження в кінці.",
         "Ліхтарики, нагрівачі"),
        
        ("CP (Постійна потужність)", "P = const", "DC-DC перетворювачі",
         "При падінні напруги струм зростає. Прискорює розряд.",
         "SMPS пристрої, модеми"),
         
        ("Pulsed (Імпульсний)", "I_tx >> I_sleep", "IoT радіопередавачі",
         "Короткі сплески на тлі сну. Критичний динамічний опір.",
         "LoRa, BLE, NB-IoT")
    ]
    
    for i, (m_title, m_formula, m_type, m_desc, m_app) in enumerate(modes):
        px = xs[i]
        f.append(rect(px, top_y, pw, ph, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
        f.append(fitbox(px + 4, top_y + 4, pw - 8, 26, m_title, size=10, bold=True, fill="#f6f8fa", stroke="#c0c8d0", sw=1))
        f.append(text(px + pw / 2, top_y + 48, m_formula, size=11, bold=True, color=POS if "CP" in m_title else FIELD))
        f.append(text(px + pw / 2, top_y + 64, m_type, size=9, color=MUTED, italic=True))
        
        gx, gy, gw, gh = px + 12, top_y + 78, pw - 24, 100
        f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1, rx=3))
        f.append(line(gx + 12, gy + gh - 12, gx + gw - 6, gy + gh - 12, color="#959da5", sw=1))
        f.append(line(gx + 12, gy + gh - 12, gx + 12, gy + 8, color="#959da5", sw=1))
        f.append(text(gx + gw - 8, gy + gh - 4, "t", size=9, color=MUTED))
        f.append(text(gx + 6, gy + 14, "V,I", size=9, color=MUTED))
        
        if "Pulsed" in m_title:
            f.append(line(gx + 12, gy + gh - 18, gx + 45, gy + gh - 18, color=C_PULSE, sw=2))
            f.append(line(gx + 45, gy + gh - 18, gx + 45, gy + 28, color=POS, sw=2))
            f.append(line(gx + 45, gy + 28, gx + 85, gy + 28, color=POS, sw=2.5))
            f.append(line(gx + 85, gy + 28, gx + 85, gy + gh - 18, color=POS, sw=2))
            f.append(line(gx + 85, gy + gh - 18, gx + gw - 8, gy + gh - 18, color=C_PULSE, sw=2))
            f.append(text(gx + 65, gy + 18, "TX Burst", size=9, bold=True, color=POS))
            f.append(text(gx + 28, gy + gh - 24, "Sleep", size=9, color=C_PULSE))
        elif "CP" in m_title:
            f.append(line(gx + 16, gy + 22, gx + gw - 16, gy + gh - 18, color=C_LION, sw=1.8, dash="3,2"))
            f.append(line(gx + 16, gy + gh - 22, gx + gw - 16, gy + 22, color=POS, sw=2.2))
            f.append(text(gx + 34, gy + 32, "V(t) ↓", size=9, color=C_LION))
            f.append(text(gx + gw - 34, gy + 20, "I(t) ↑", size=9, bold=True, color=POS))
        elif "CR" in m_title:
            f.append(line(gx + 16, gy + 22, gx + gw - 16, gy + gh - 18, color=C_LION, sw=1.8, dash="3,2"))
            f.append(line(gx + 16, gy + 32, gx + gw - 16, gy + gh - 14, color=C_PULSE, sw=2))
            f.append(text(gx + 34, gy + 32, "V(t) ↓", size=9, color=C_LION))
            f.append(text(gx + gw - 34, gy + gh - 20, "I(t) ↓", size=9, color=C_PULSE))
        else:
            f.append(line(gx + 16, gy + 22, gx + gw - 16, gy + gh - 18, color=C_LION, sw=1.8, dash="3,2"))
            f.append(line(gx + 16, gy + 45, gx + gw - 16, gy + 45, color=C_PULSE, sw=2))
            f.append(text(gx + 34, gy + 32, "V(t) ↓", size=9, color=C_LION))
            f.append(text(gx + gw - 34, gy + 38, "I = const", size=9, color=C_PULSE))

        f.append(fitbox(px + 8, top_y + 190, pw - 16, 75, m_desc, size=9, fill="#ffffff", stroke="none"))
        f.append(fitbox(px + 8, top_y + 285, pw - 16, 38, "Типово: " + m_app, size=9, bold=True, fill="#f0f4f8", stroke="#d0d7de", sw=1))

    render(os.path.join(IMG, "load-modes-comparison.svg"), W, H, *f)


# ── 2. Анатомія розрядних кривих різних хімій ──────────────────────────────
def fig_discharge_profiles():
    W, H = 860, 460
    f = [text(W / 2, 26, "Розрядні криві хімій батарей і вплив напруги відсічки (Cutoff)", size=15, bold=True)]
    
    ox, oy = 90, 370
    pw, ph = 520, 310
    top_y = oy - ph
    
    f.append(rect(ox, top_y, pw, ph, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=4))
    
    v_max = 4.5
    sc_y = ph / v_max
    for v in [1.0, 2.0, 3.0, 3.6, 4.0]:
        yy = oy - v * sc_y
        f.append(line(ox, yy, ox + pw, yy, color="#f0f2f5", sw=1))
        f.append(text(ox - 10, yy + 4, "%.1f В" % v, size=10, color=MUTED, anchor="end"))
    
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, top_y, color=INK, sw=1.5))
    f.append(text(ox - 10, top_y + 10, "Напруга (В)", size=11, bold=True, anchor="end"))
    
    for pct in [0, 20, 40, 60, 80, 100]:
        xx = ox + (pct / 100.0) * pw
        f.append(line(xx, oy, xx, top_y, color="#f0f2f5", sw=1))
        f.append(line(xx, oy, xx, oy + 5, color=INK, sw=1))
        f.append(text(xx, oy + 18, "%d%%" % pct, size=10, color=MUTED))
    f.append(text(ox + pw / 2, oy + 36, "Віддана ємність від номіналу (%)", size=11, bold=True))
    
    # Li-SOCl2 (3.6 В)
    pts_socl2 = [(0, 3.65), (5, 3.60), (30, 3.60), (70, 3.58), (92, 3.55), (96, 3.40), (98, 2.80), (100, 1.80)]
    poly_socl2 = " ".join(["%.1f,%.1f" % (ox + p[0]*pw/100, oy - p[1]*sc_y) for p in pts_socl2])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_socl2, C_SOCL2))
    
    # Li-SOCl2 TMV пасивація
    pts_tmv = [(0, 3.65), (2, 2.40), (8, 3.40), (15, 3.58)]
    poly_tmv = " ".join(["%.1f,%.1f" % (ox + p[0]*pw/100, oy - p[1]*sc_y) for p in pts_tmv])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (poly_tmv, C_SOCL2))
    f.append(fitbox(ox + 20, oy - int(2.55 * sc_y), 90, 24, "TMV пасивація", size=9, bold=True, fill="#f0f4fd", stroke=C_SOCL2, color=C_SOCL2))

    # Li-Ion NMC (3.7 В)
    pts_lion = [(0, 4.20), (10, 3.95), (25, 3.80), (50, 3.68), (75, 3.55), (90, 3.35), (97, 3.00), (100, 2.70)]
    poly_lion = " ".join(["%.1f,%.1f" % (ox + p[0]*pw/100, oy - p[1]*sc_y) for p in pts_lion])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_lion, C_LION))

    # LiFePO4 (3.2 В)
    pts_lfp = [(0, 3.45), (8, 3.25), (30, 3.22), (60, 3.20), (85, 3.15), (94, 2.95), (98, 2.50), (100, 2.00)]
    poly_lfp = " ".join(["%.1f,%.1f" % (ox + p[0]*pw/100, oy - p[1]*sc_y) for p in pts_lfp])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_lfp, C_LFP))

    # Li-MnO2 (3.0 В, CR2032/CR123A)
    pts_mno2 = [(0, 3.15), (10, 2.95), (35, 2.85), (65, 2.70), (85, 2.45), (95, 2.10), (100, 1.80)]
    poly_mno2 = " ".join(["%.1f,%.1f" % (ox + p[0]*pw/100, oy - p[1]*sc_y) for p in pts_mno2])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_mno2, C_MNO2))

    # Cutoff thresholds
    y_cut_ldo = oy - 3.0 * sc_y
    f.append(line(ox, y_cut_ldo, ox + pw, y_cut_ldo, color=POS, sw=1.5, dash="6,3"))
    f.append(text(ox + pw - 6, y_cut_ldo - 6, "Відсічка LDO / MCU (3.0 В)", size=9, bold=True, color=POS, anchor="end"))
    
    y_cut_low = oy - 2.0 * sc_y
    f.append(line(ox, y_cut_low, ox + pw, y_cut_low, color="#27ae60", sw=1.5, dash="6,3"))
    f.append(text(ox + pw - 6, y_cut_low - 6, "Глибока відсічка (2.0 В)", size=9, bold=True, color="#27ae60", anchor="end"))

    # Легенда
    lx, ly = ox + pw + 20, top_y + 5
    lw, lh = 215, 305
    f.append(rect(lx, ly, lw, lh, fill="#f8f9fa", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(lx + lw/2, ly + 20, "Електрохімічні системи", size=11, bold=True))
    
    leg_items = [
        (C_LION, "Li-ion (NMC/LCO)", "3.7 В номінал (4.2→3.0 В)", "Спадний профіль, видно SoC"),
        (C_LFP,  "LiFePO4",          "3.2 В номінал (3.6→2.5 В)", "Пласке плато, надійний"),
        (C_SOCL2,"Li-SOCl2",         "3.6 В первинний",           "Ультраплаский, пасивація TMV"),
        (C_MNO2, "Li-MnO2",          "3.0 В первинний (CR2032)",  "Пологий спад до 2.0 В")
    ]
    
    for i, (col, name, nom, note) in enumerate(leg_items):
        item_y = ly + 40 + i * 65
        f.append(line(lx + 10, item_y + 6, lx + 32, item_y + 6, color=col, sw=3.5))
        f.append(text(lx + 38, item_y + 8, name, size=10, bold=True, color=col, anchor="start"))
        f.append(text(lx + 10, item_y + 24, nom, size=9, color=INK, anchor="start"))
        f.append(text(lx + 10, item_y + 40, note, size=9, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(IMG, "discharge-profiles.svg"), W, H, *f)


# ── 3. Відгук батареї на імпульс струму (DC IR Step) ────────────────────────
def fig_dc_ir_step():
    W, H = 880, 450
    f = [text(W / 2, 26, "Анатомія падіння напруги при ступінчастому навантаженні (DC IR)", size=15, bold=True)]
    
    ox, oy = 80, 360
    pw, ph = 740, 290
    top_y = oy - ph
    
    f.append(rect(ox, top_y, pw, ph, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=4))
    
    f.append(line(ox + 20, oy - 20, ox + pw - 20, oy - 20, color=INK, sw=1.5))
    f.append(arrow(ox + pw - 30, oy - 20, ox + pw - 15, oy - 20, color=INK, sw=1.5))
    f.append(text(ox + pw - 10, oy - 16, "Час (t)", size=11, bold=True, anchor="start"))
    
    f.append(line(ox + 30, oy - 20, ox + 30, top_y + 20, color=INK, sw=1.5))
    f.append(arrow(ox + 30, top_y + 30, ox + 30, top_y + 15, color=INK, sw=1.5))
    f.append(text(ox + 25, top_y + 16, "Напруга V(t)", size=11, bold=True, anchor="end"))
    
    t0 = ox + 90
    t1 = ox + 430
    
    f.append(line(t0, top_y + 20, t0, oy - 20, color="#d0d7de", sw=1, dash="4,4"))
    f.append(line(t1, top_y + 20, t1, oy - 20, color="#d0d7de", sw=1, dash="4,4"))
    f.append(text(t0, oy - 6, "t_on (Старт I_load)", size=10, bold=True))
    f.append(text(t1, oy - 6, "t_off (Зняття навантаження)", size=10, bold=True))
    
    v_ocv = top_y + 40
    v_ohm = top_y + 95
    v_ct  = top_y + 160
    v_diff= top_y + 215
    
    f.append(line(ox + 30, v_ocv, t0, v_ocv, color=C_SOCL2, sw=2.5))
    f.append(text(ox + 60, v_ocv - 8, "V_OCV", size=10, bold=True, color=C_SOCL2))
    
    f.append(line(t0, v_ocv, t0, v_ohm, color=POS, sw=2.5))
    
    pts_pulse = [(t0, v_ohm), (t0 + 20, v_ohm + 25), (t0 + 60, v_ohm + 45),
                 (t0 + 140, v_ct), (t0 + 240, v_ct + 25), (t1, v_diff)]
    poly_pulse = " ".join(["%.1f,%.1f" % p for p in pts_pulse])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_pulse, POS))
    
    f.append(line(t1, v_diff, t1, v_diff - (v_ohm - v_ocv), color=FIELD, sw=2.5))
    pts_rec = [(t1, v_diff - (v_ohm - v_ocv)), (t1 + 50, v_ocv + 45), (t1 + 140, v_ocv + 15), (ox + pw - 30, v_ocv)]
    poly_rec = " ".join(["%.1f,%.1f" % p for p in pts_rec])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_rec, FIELD))

    # Складова 1: Омічне падіння (R_ohm)
    f.append(line(t0 + 5, v_ocv, t0 + 40, v_ocv, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 5, v_ohm, t0 + 40, v_ohm, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 35, v_ocv, t0 + 35, v_ohm, color=POS, sw=1.5))
    f.append(fitbox(t0 + 45, v_ocv, 245, 46,
                    "ΔV_ohm = I · R_ohm (< 10 мкс)\nОпір електроліту й фольги. Вимірює AC IR 1 kHz.",
                    size=9, fill="#fdf2f2", stroke=POS, sw=1))

    # Складова 2: Поляризація подвійного шару та реакції (R_ct || C_dl)
    f.append(line(t0 + 130, v_ohm, t0 + 160, v_ohm, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 130, v_ct, t0 + 160, v_ct, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 155, v_ohm, t0 + 155, v_ct, color=C_LFP, sw=1.5))
    f.append(fitbox(t0 + 165, v_ohm + 20, 245, 46,
                    "ΔV_ct: Кінетика перенесення заряду (10 мс – 1 с)\nЄмність подвійного шару електродів.",
                    size=9, fill="#fef9e7", stroke=C_LFP, sw=1))

    # Складова 3: Дифузійна поляризація (Warburg)
    f.append(line(t0 + 220, v_ct, t0 + 250, v_ct, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 220, v_diff, t0 + 250, v_diff, color="#7f8c8d", sw=1, dash="2,2"))
    f.append(line(t0 + 245, v_ct, t0 + 245, v_diff, color="#8e44ad", sw=1.5))
    f.append(fitbox(t0 + 255, v_ct + 15, 245, 46,
                    "ΔV_diff: Дифузія іонів (секунди – хвилини)\nГрадієнт концентрації в об'ємі.",
                    size=9, fill="#fbf0fd", stroke="#8e44ad", sw=1))

    f.append(fitbox(ox + 35, oy + 8, pw - 70, 30,
                    "DC IR = ΔV_total / ΔI (через 100 мс або 1 с) на 30–100% перевищує паспортний AC IR 1 kHz!",
                    size=10, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, "dc-ir-step.svg"), W, H, *f)


# ── 4. Апаратна схема розрядного стенду на мікроконтролері ─────────────────
def fig_electronic_load_circuit():
    W, H = 900, 460
    f = [text(W / 2, 26, "Апаратна схема розрядного стенду (Electronic Load) з 4-провідним підключенням Кельвіна", size=15, bold=True)]
    
    # 1. Батарея
    bx, by, bw, bh = 30, 70, 160, 330
    f.append(rect(bx, by, bw, bh, fill="#fbfcfd", stroke="#d0d7de", sw=1.5, rx=6))
    f.append(fitbox(bx + 6, by + 6, bw - 12, 26, "Батарея (DUT)", size=11, bold=True, fill="#f0f4f8", stroke="#c0c8d0"))
    
    f.append(circle(bx + bw - 15, by + 70, 6, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(bx + bw - 30, by + 74, "Force +", size=10, bold=True, color=POS, anchor="end"))
    
    f.append(circle(bx + bw - 15, by + 120, 6, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(bx + bw - 30, by + 124, "Sense +", size=10, bold=True, color=POS, anchor="end"))
    
    f.append(circle(bx + bw - 15, by + 230, 6, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(bx + bw - 30, by + 234, "Sense −", size=10, bold=True, color=NEG, anchor="end"))
    
    f.append(circle(bx + bw - 15, by + 280, 6, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(bx + bw - 30, by + 284, "Force −", size=10, bold=True, color=NEG, anchor="end"))
    
    f.append(fitbox(bx + 10, by + 150, bw - 20, 65,
                    "4-провідне підключення:\nСтрум розряду не спотворює вимір напруги комірки!",
                    size=9, fill="#ffffff", stroke="none"))

    # 2. Силова частина лінійного навантаження
    lx, ly, lw, lh = 230, 70, 330, 330
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    f.append(fitbox(lx + 6, ly + 6, lw - 12, 26, "Лінійний стабілізатор струму (CC Sink)", size=11, bold=True, fill="#f0f4f8", stroke="#c0c8d0"))

    op_x, op_y = lx + 80, ly + 140
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#f8f9fa" stroke="%s" stroke-width="1.8"/>' %
             (op_x, op_y - 30, op_x, op_y + 30, op_x + 50, op_y, INK))
    f.append(text(op_x + 10, op_y - 12, "+", size=12, bold=True, color=POS))
    f.append(text(op_x + 10, op_y + 16, "−", size=12, bold=True, color=NEG))
    f.append(text(op_x + 24, op_y + 3, "OpAmp", size=9, bold=True))

    mos_x, mos_y = lx + 195, ly + 140
    f.append(rect(mos_x - 15, mos_y - 25, 30, 50, fill="#edf2f7", stroke=INK, sw=1.5, rx=3))
    f.append(text(mos_x, mos_y - 5, "N-FET", size=9, bold=True))
    f.append(text(mos_x, mos_y + 10, "IRLZ44N", size=9, color=MUTED))
    
    f.append(line(mos_x + 18, mos_y - 30, mos_x + 28, mos_y - 30, color="#7f8c8d", sw=2))
    f.append(line(mos_x + 18, mos_y - 15, mos_x + 28, mos_y - 15, color="#7f8c8d", sw=2))
    f.append(line(mos_x + 18, mos_y, mos_x + 28, mos_y, color="#7f8c8d", sw=2))
    f.append(line(mos_x + 18, mos_y + 15, mos_x + 28, mos_y + 15, color="#7f8c8d", sw=2))
    f.append(line(mos_x + 18, mos_y + 30, mos_x + 28, mos_y + 30, color="#7f8c8d", sw=2))
    f.append(text(mos_x + 50, mos_y + 4, "Радіатор", size=9, color=MUTED))

    f.append(line(op_x + 50, op_y, mos_x - 15, mos_y, color=INK, sw=1.5))
    f.append(circle(op_x + 75, op_y, 4, fill=POS, stroke=POS))
    f.append(text(op_x + 75, op_y - 8, "R_g 100Ω", size=9, color=MUTED))

    sh_x, sh_y = mos_x, ly + 250
    f.append(rect(sh_x - 14, sh_y - 15, 28, 30, fill="#fef9e7", stroke="#caa24a", sw=1.5, rx=2))
    f.append(text(sh_x, sh_y + 4, "R_sh", size=9, bold=True))
    f.append(text(sh_x + 45, sh_y + 4, "0.05 Ω (1%)", size=9, color=MUTED))

    f.append(line(bx + bw - 9, by + 70, mos_x, by + 70, color=POS, sw=2.5))
    f.append(line(mos_x, by + 70, mos_x, mos_y - 25, color=POS, sw=2.5))
    f.append(line(mos_x, mos_y + 25, mos_x, sh_y - 15, color=INK, sw=2))
    f.append(line(mos_x, sh_y + 15, mos_x, by + 280, color=NEG, sw=2.5))
    f.append(line(mos_x, by + 280, bx + bw - 9, by + 280, color=NEG, sw=2.5))

    f.append(circle(mos_x, sh_y - 10, 4, fill=NEG, stroke=NEG))
    f.append(line(mos_x, sh_y - 10, lx + 45, sh_y - 10, color=NEG, sw=1.4))
    f.append(line(lx + 45, sh_y - 10, lx + 45, op_y + 16, color=NEG, sw=1.4))
    f.append(line(lx + 45, op_y + 16, op_x, op_y + 16, color=NEG, sw=1.4))
    f.append(text(lx + 50, sh_y - 18, "Зворотний зв'язок V_shunt", size=9, color=NEG, bold=True))

    f.append(line(op_x + 50, op_y, op_x + 50, op_y - 45, color="#7f8c8d", sw=1.2))
    f.append(line(op_x + 50, op_y - 45, lx + 45, op_y - 45, color="#7f8c8d", sw=1.2))
    f.append(line(lx + 45, op_y - 45, lx + 45, op_y + 16, color="#7f8c8d", sw=1.2))
    f.append(rect(op_x + 15, op_y - 52, 28, 14, fill="#ffffff", stroke="#7f8c8d", sw=1))
    f.append(text(op_x + 29, op_y - 58, "C_comp 10nF", size=9, color=MUTED))

    # 3. Блок мікроконтролера
    mx, my, mw, mh = 600, 70, 260, 330
    f.append(rect(mx, my, mw, mh, fill="#fbfcfd", stroke="#d0d7de", sw=1.5, rx=6))
    f.append(fitbox(mx + 6, my + 6, mw - 12, 26, "Мікроконтролер (MCU / Стенд)", size=11, bold=True, fill="#f0f4f8", stroke="#c0c8d0"))

    dac_y = ly + 128
    f.append(circle(mx + 20, dac_y, 5, fill=FIELD, stroke=FIELD))
    f.append(text(mx + 32, dac_y + 4, "DAC (V_ref / I_set)", size=9, bold=True, color=FIELD, anchor="start"))
    f.append(line(mx + 20, dac_y, op_x, op_y - 12, color=FIELD, sw=1.6))
    
    adc1_y = ly + 175
    f.append(circle(mx + 20, adc1_y, 5, fill=POS, stroke=POS))
    f.append(text(mx + 32, adc1_y + 4, "ADC1 (V_batt sense diff)", size=9, bold=True, color=POS, anchor="start"))
    f.append(line(bx + bw - 9, by + 120, lx + 20, by + 120, color=POS, sw=1.2, dash="3,2"))
    f.append(line(lx + 20, by + 120, lx + 20, ly + 40, color=POS, sw=1.2, dash="3,2"))
    f.append(line(lx + 20, ly + 40, mx + 20, ly + 40, color=POS, sw=1.2, dash="3,2"))
    f.append(line(mx + 20, ly + 40, mx + 20, adc1_y, color=POS, sw=1.2, dash="3,2"))

    adc2_y = ly + 220
    f.append(circle(mx + 20, adc2_y, 5, fill=NEG, stroke=NEG))
    f.append(text(mx + 32, adc2_y + 4, "ADC2 (I_load actual)", size=9, bold=True, color=NEG, anchor="start"))
    f.append(line(mos_x, sh_y - 10, mx + 20, adc2_y, color=NEG, sw=1.2, dash="3,2"))

    adc3_y = ly + 265
    f.append(circle(mx + 20, adc3_y, 5, fill="#d35400", stroke="#d35400"))
    f.append(text(mx + 32, adc3_y + 4, "ADC3 (NTC радіатора)", size=9, bold=True, color="#d35400", anchor="start"))
    f.append(line(mos_x + 35, mos_y + 30, mx + 20, adc3_y, color="#d35400", sw=1.2, dash="3,2"))

    f.append(fitbox(mx + 15, my + mh - 50, mw - 30, 36,
                    "USB / UART (CSV телеметрія)\nt, V_cell, I_load, mAh, mWh, R_int",
                    size=9, bold=True, fill="#eafaf0", stroke=FIELD, sw=1))

    render(os.path.join(IMG, "electronic-load-circuit.svg"), W, H, *f)


if __name__ == "__main__":
    fig_load_modes()
    fig_discharge_profiles()
    fig_dc_ir_step()
    fig_electronic_load_circuit()
    print("All figures generated successfully.")
