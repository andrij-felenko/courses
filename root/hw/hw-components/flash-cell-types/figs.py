# -*- coding: utf-8 -*-
"""Фігури до теми «SLC, MLC, TLC, QLC: типи Flash-комірок» (hw-components).
Фігури теми:
  cell-types-distribution.svg — розподіли порогової напруги V_th для SLC, MLC, TLC, QLC в єдиному вікні напруг;
  ispp-programming-steps.svg  — алгоритм покрокового імпульсного програмування ISPP (імпульси V_pgm та верифікація V_pv);
  soft-decision-sensing-llr.svg — багатопорогове м'яке зчитування LDPC: квантування напруги на біни LLR.
Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def cell_types_distribution():
    """Розподіли V_th для SLC (2), MLC (4), TLC (8), QLC (16) в єдиному вікні напруг (0..6 В).
    Показує звуження міжрівневих проміжків та появу перекриття хвостів у щільних типах."""
    W, H = 840, 570
    p = []

    p.append(text(W / 2, 28, "Розподіл порогової напруги V_th для різних типів NAND-комірок", size=15, bold=True))

    configs = [
        ("SLC (1 біт/комірка: 2 стани)", 2, ["E (1)", "P1 (0)"], 75, False),
        ("MLC (2 біти/комірка: 4 стани)", 4, ["E", "P1", "P2", "P3"], 190, False),
        ("TLC (3 біти/комірка: 8 станів)", 8, ["E", "P1", "P2", "P3", "P4", "P5", "P6", "P7"], 305, False),
        ("QLC (4 біти/комірка: 16 станів)", 16, ["E", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15"], 420, True),
    ]

    x_left = 75
    x_right = 785
    win_w = x_right - x_left

    for title, n_states, state_labels, y_base, is_qlc in configs:
        p.append(text(x_left, y_base - 50, title, size=12, bold=True, anchor="start", color=POS if n_states >= 8 else INK))
        
        # Вісь V_th
        p.append(line(x_left, y_base, x_right, y_base, color="#8a94a6", sw=1.2))
        p.append(text(x_right + 6, y_base + 4, "V_th", size=10, color=MUTED, anchor="start"))
        
        step = win_w / n_states
        peak_h = 34 if n_states <= 4 else 32
        sigma = step * 0.16 if n_states <= 4 else step * 0.20

        for i in range(n_states):
            mu = x_left + (i + 0.5) * step
            pts = []
            steps_num = 18
            span_pts = step * 0.48 if not is_qlc else step * 0.56
            for s in range(-steps_num, steps_num + 1):
                dx = s * (span_pts / steps_num)
                xx = mu + dx
                arg = (dx / sigma) ** 2
                yy = y_base - peak_h * math.exp(-0.5 * arg)
                pts.append("%.1f,%.1f" % (xx, yy))
            
            c_stroke = NEG if i == 0 else ("#1b5e20" if i % 2 == 1 else "#b71c1c")
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), c_stroke))
            
            # Підпис стану
            if n_states <= 8:
                p.append(text(mu, y_base - peak_h - 6, state_labels[i], size=10, bold=True, color=INK))
            elif i in (0, 3, 7, 11, 15):
                p.append(text(mu, y_base - peak_h - 6, state_labels[i], size=9, bold=True, color=INK))

        # Позначення захисного вікна (margin) між сусідами
        if n_states <= 4:
            m_start = x_left + 0.5 * step + sigma * 1.6
            m_end = x_left + 1.5 * step - sigma * 1.6
            p.append(line(m_start, y_base - 14, m_end, y_base - 14, color=FIELD, sw=1.5))
            p.append(text((m_start + m_end) / 2, y_base - 18, "захисний проміжок", size=9, bold=True, color=FIELD))

    box, bwd, bhd = textbox(W / 2, 535, "Вікно напруги незмінне (~5–6 В): зі зростанням бітів захисний бар'єр тане, а хвости розмиваються", size=11, color=INK, fill="#fff8e6", stroke="#e0b400")
    p.append(box)

    render(os.path.join(OUT, "cell-types-distribution.svg"), W, H, *p)


def ispp_programming_steps():
    """Алгоритм покрокового імпульсного програмування (ISPP).
    Показує сходинки напруги V_pgm з інкрементом ΔV_ispp та імпульси верифікації V_pv."""
    W, H = 820, 480
    p = []

    p.append(text(W / 2, 28, "Алгоритм покрокового імпульсного програмування (ISPP)", size=15, bold=True))

    x0 = 80
    y0 = 360
    x_end = 760

    # Осі
    p.append(arrow(x0, y0, x_end, y0, color=INK, sw=1.5))
    p.append(arrow(x0, y0, x0, 70, color=INK, sw=1.5))
    p.append(text(x_end, y0 + 20, "Час (t) →", size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 10, 80, "Напруга на затворі V_g (В) →", size=11, color=MUTED, anchor="end"))

    v_start = 14.0
    dv = 0.6
    n_pulses = 6
    t_step = 95
    p_w = 40
    v_scale = 14.0
    base_v = 10.0

    for k in range(n_pulses):
        v_pgm = v_start + k * dv
        tx = x0 + 25 + k * t_step
        ty_pgm = y0 - (v_pgm - base_v) * v_scale

        # Імпульс запису (V_pgm)
        p.append(rect(tx, ty_pgm, p_w, y0 - ty_pgm, fill="#fdecea", stroke=POS, sw=1.4))
        p.append(text(tx + p_w / 2, ty_pgm - 8, "%.1f В" % v_pgm, size=9, bold=True, color=POS))

        # Імпульс перевірки (Verify V_pv)
        v_pv = 12.0
        ty_pv = y0 - (v_pv - base_v) * v_scale
        pv_x = tx + p_w + 10
        pv_w = 26
        p.append(rect(pv_x, ty_pv, pv_w, y0 - ty_pv, fill="#eaf0fd", stroke=NEG, sw=1.3))
        p.append(text(pv_x + pv_w / 2, ty_pv - 6, "V_pv", size=9, bold=True, color=NEG))

        # Позначка кроку ΔV_ispp між імпульсами
        if k < n_pulses - 1:
            next_ty = y0 - (v_start + (k + 1) * dv - base_v) * v_scale
            p.append(line(tx + p_w, ty_pgm, tx + t_step, ty_pgm, color="#9ca3af", sw=1.0, dash="2 2"))
            p.append(line(tx + t_step, ty_pgm, tx + t_step, next_ty, color=FIELD, sw=1.5))
            if k == 1:
                p.append(text(tx + t_step + 24, (ty_pgm + next_ty) / 2 + 3, "ΔV_ispp", size=9, bold=True, color=FIELD))

    # Пояснювальні плашки праворуч
    tb1, _, _ = textbox(240, 420, "Імпульс запису V_pgm: інжекція електронів крізь оксид", size=10, fill="#fdecea", stroke=POS)
    tb2, _, _ = textbox(600, 420, "Імпульс верифікації V_pv: перевірка чи досягнуто цільову V_th", size=10, fill="#eaf0fd", stroke=NEG)
    p.append(tb1)
    p.append(tb2)

    render(os.path.join(OUT, "ispp-programming-steps.svg"), W, H, *p)


def soft_decision_sensing_llr():
    """Багатопорогове м'яке зчитування (Soft-decision LDPC decoding).
    Показує 1 жорстке зчитування (V_ref) та додаткові м'які строби (V_ref ± Δ), що формують метрики LLR."""
    W, H = 860, 520
    p = []

    p.append(text(W / 2, 28, "Багатопорогове м'яке зчитування (Soft-Decision LDPC) та оцінка LLR", size=15, bold=True))

    x0 = 70
    y_base = 220
    x_end = 790

    p.append(line(x0, y_base, x_end, y_base, color="#8a94a6", sw=1.4))
    p.append(text(x_end + 6, y_base + 4, "V_th", size=11, color=MUTED, anchor="start"))

    # Два сусідні розподіли: Стан S_A (біт 1) та Стан S_B (біт 0)
    mu_a = 270
    mu_b = 590
    sigma = 75
    peak_h = 115

    pts_a = []
    pts_b = []
    for s in range(-90, 91):
        # Розподіл A
        xa = mu_a + s * 2.4
        ya = y_base - peak_h * math.exp(-0.5 * ((xa - mu_a) / sigma) ** 2)
        pts_a.append("%.1f,%.1f" % (xa, ya))
        # Розподіл B
        xb = mu_b + s * 2.4
        yb = y_base - peak_h * math.exp(-0.5 * ((xb - mu_b) / sigma) ** 2)
        pts_b.append("%.1f,%.1f" % (xb, yb))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_a), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_b), POS))

    p.append(text(mu_a, y_base - peak_h - 12, "Стан S_A (біт '1')", size=12, bold=True, color=NEG))
    p.append(text(mu_b, y_base - peak_h - 12, "Стан S_B (біт '0')", size=12, bold=True, color=POS))

    # Пороги зчитування
    v_hard = (mu_a + mu_b) / 2  # 430
    delta_s = 60

    v_soft_l2 = v_hard - 2 * delta_s  # 310
    v_soft_l1 = v_hard - delta_s      # 370
    v_soft_r1 = v_hard + delta_s      # 490
    v_soft_r2 = v_hard + 2 * delta_s  # 550

    # Жорсткий поріг (лінія закінчується на y_base + 35)
    p.append(line(v_hard, 70, v_hard, y_base + 35, color="#111827", sw=2.0, dash="4 3"))
    p.append(text(v_hard, 58, "V_ref (Hard Read)", size=11, bold=True, color=INK))

    # М'які пороги (лінії закінчуються на y_base + 35)
    soft_strobes = [
        (v_soft_l2, "V_ref - 2Δ"),
        (v_soft_l1, "V_ref - Δ"),
        (v_soft_r1, "V_ref + Δ"),
        (v_soft_r2, "V_ref + 2Δ"),
    ]

    for sx, slabel in soft_strobes:
        p.append(line(sx, 90, sx, y_base + 35, color=FIELD, sw=1.2, dash="3 3"))
        p.append(text(sx, 78, slabel, size=9, bold=True, color=FIELD))

    # Нижня шкала квантування LLR
    y_llr = 330
    p.append(text(x0, y_llr - 16, "Зони впевненості та квантовані значення LLR (Log-Likelihood Ratio):", size=11, bold=True, anchor="start", color=INK))
    
    bins = [
        (x0 + 15, v_soft_l2, "LLR = +7\nпевна 1", "#dbeafe", NEG),
        (v_soft_l2, v_soft_l1, "LLR = +4\nймовірна 1", "#eff6ff", NEG),
        (v_soft_l1, v_hard, "LLR = +1\nслабка 1", "#f3f4f6", "#4b5563"),
        (v_hard, v_soft_r1, "LLR = -1\nслабкий 0", "#f3f4f6", "#4b5563"),
        (v_soft_r1, v_soft_r2, "LLR = -4\nймовірний 0", "#fef2f2", POS),
        (v_soft_r2, x_end - 15, "LLR = -7\nтвердий 0", "#fee2e2", POS),
    ]

    for bx1, bx2, blabel, bfill, bcol in bins:
        p.append(fitbox(bx1 + 1, y_llr, bx2 - bx1 - 2, 48, blabel, size=10, fill=bfill, stroke=bcol, color=bcol, bold=True))

    box, bwd, bhd = textbox(W / 2, 475, "М'які строби передають декодеру LDPC не просто біт, а ступінь впевненості: LLR = ln( P(0)/P(1) )", size=11, color=INK, fill="#eef7ef", stroke=FIELD)
    p.append(box)

    render(os.path.join(OUT, "soft-decision-sensing-llr.svg"), W, H, *p)


if __name__ == "__main__":
    cell_types_distribution()
    ispp_programming_steps()
    soft_decision_sensing_llr()
    print("OK: figs written to", OUT)
