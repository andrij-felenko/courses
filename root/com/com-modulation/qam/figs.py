# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_qam_constellations():
    w, h = 800, 440
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 24, "Сигнальні сузір'я QAM: геометрія сітки та кодування Грея", size=15, bold=True))
    
    # ── Panel 1: 16-QAM (Left) ──
    cx1, cy1 = 200, 230
    grid_size1 = 180
    step1 = grid_size1 / 3.0
    
    out.append(rect(cx1 - grid_size1/2 - 50, 48, grid_size1 + 100, 370, fill="#f8fafc", stroke="#e2e8f0", rx=8))
    out.append(text(cx1, 70, "16-QAM (4 біти / символ)", size=14, bold=True, color=INK))
    
    # Grid background & decision boundaries
    for i in range(4):
        val = -1.5 + i
        pos_x = cx1 + val * step1
        pos_y = cy1 - val * step1
        out.append(line(pos_x, cy1 - grid_size1/2 - 20, pos_x, cy1 + grid_size1/2 + 20, color="#cbd5e1", sw=1, dash="3,3"))
        out.append(line(cx1 - grid_size1/2 - 20, pos_y, cx1 + grid_size1/2 + 20, pos_y, color="#cbd5e1", sw=1, dash="3,3"))

    # Axes
    out.append(arrow(cx1 - grid_size1/2 - 35, cy1, cx1 + grid_size1/2 + 35, cy1, color=INK, sw=1.5))
    out.append(arrow(cx1, cy1 + grid_size1/2 + 35, cx1, cy1 - grid_size1/2 - 35, color=INK, sw=1.5))
    out.append(text(cx1 + grid_size1/2 + 42, cy1 + 4, "I", size=12, bold=True, color=INK, anchor="start"))
    out.append(text(cx1 - 10, cy1 - grid_size1/2 - 40, "Q", size=12, bold=True, color=INK, anchor="end"))

    # Points & Gray labels
    # Gray 2D for 4-PAM: 00 -> -3, 01 -> -1, 11 -> +1, 10 -> +3
    gray1d = ["00", "01", "11", "10"]
    vals = [-1.5, -0.5, 0.5, 1.5]
    
    for row in range(4):
        for col in range(4):
            px = cx1 + vals[col] * step1
            py = cy1 - vals[row] * step1
            bits = gray1d[col] + gray1d[row]
            out.append(circle(px, py, 6, fill=NEG, stroke="#ffffff", sw=1.5))
            out.append(text(px, py - 10, bits, size=10, color=INK, bold=True))

    # d_min indicator
    x_a = cx1 + vals[1] * step1
    x_b = cx1 + vals[2] * step1
    y_ab = cy1 + vals[0] * step1 + 25
    out.append(line(x_a, y_ab, x_b, y_ab, color=POS, sw=2))
    out.append(line(x_a, y_ab - 4, x_a, y_ab + 4, color=POS, sw=2))
    out.append(line(x_b, y_ab - 4, x_b, y_ab + 4, color=POS, sw=2))
    out.append(text((x_a + x_b)/2, y_ab + 16, "d_min", size=11, color=POS, bold=True))

    # ── Panel 2: 64-QAM (Right) ──
    cx2, cy2 = 600, 230
    grid_size2 = 220
    step2 = grid_size2 / 7.0

    out.append(rect(cx2 - grid_size2/2 - 40, 48, grid_size2 + 80, 370, fill="#f8fafc", stroke="#e2e8f0", rx=8))
    out.append(text(cx2, 70, "64-QAM (6 бітів / символ)", size=14, bold=True, color=INK))

    # Grid lines
    for i in range(8):
        val = -3.5 + i
        pos_x = cx2 + val * step2
        pos_y = cy2 - val * step2
        out.append(line(pos_x, cy2 - grid_size2/2 - 15, pos_x, cy2 + grid_size2/2 + 15, color="#e2e8f0", sw=1, dash="2,2"))
        out.append(line(cx2 - grid_size2/2 - 15, pos_y, cx2 + grid_size2/2 + 15, pos_y, color="#e2e8f0", sw=1, dash="2,2"))

    # Axes
    out.append(arrow(cx2 - grid_size2/2 - 25, cy2, cx2 + grid_size2/2 + 25, cy2, color=INK, sw=1.5))
    out.append(arrow(cx2, cy2 + grid_size2/2 + 25, cx2, cy2 - grid_size2/2 - 25, color=INK, sw=1.5))
    out.append(text(cx2 + grid_size2/2 + 30, cy2 + 4, "I", size=12, bold=True, color=INK, anchor="start"))
    out.append(text(cx2 - 10, cy2 - grid_size2/2 - 30, "Q", size=12, bold=True, color=INK, anchor="end"))

    # Points 8x8
    for row in range(8):
        for col in range(8):
            px = cx2 + (-3.5 + col) * step2
            py = cy2 - (-3.5 + row) * step2
            out.append(circle(px, py, 4, fill=FIELD, stroke="#ffffff", sw=1))

    # Legend / Note at bottom
    out.append(text(w/2, 408, "У коді Грея сусідні точки сузір'я відрізняються лише на один біт — помилка вибору сусіднього стану дає 1 бітову помилку", size=11, color=MUTED, italic=True))

    render(os.path.join(os.path.dirname(__file__), "img", "qam-constellations.svg"), w, h, *out)

def fig_qam_mod_chain():
    w, h = 800, 360
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 22, "Схема квадратурного модулятора та демодулятора QAM", size=15, bold=True))

    # ── Section 1: Modulator (Top) ──
    out.append(rect(20, 42, 760, 140, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    out.append(text(35, 60, "ПЕРЕДАВАЧ (Квадратурний модулятор)", size=12, bold=True, color=INK, anchor="start"))

    # Input bits -> S/P
    out.append(text(35, 110, "Біти даних", size=11, bold=True, color=INK, anchor="start"))
    out.append(arrow(95, 110, 130, 110, color=INK, sw=1.5))
    out.append(fitbox(130, 90, 80, 40, "S / P\nMapper", size=11, fill="#e0f2fe", stroke="#0284c7"))

    # I branch (top)
    out.append(arrow(210, 95, 250, 95, color=NEG, sw=1.5))
    out.append(text(230, 88, "I(t)", size=10, bold=True, color=NEG))
    out.append(fitbox(250, 78, 65, 34, "ФНЧ / RRC", size=10, fill=FILL, stroke="#64748b"))
    out.append(arrow(315, 95, 360, 95, color=INK, sw=1.5))
    out.append(circle(375, 95, 14, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    out.append(text(375, 99, "×", size=16, bold=True, color=INK))

    # Q branch (bottom)
    out.append(arrow(210, 125, 250, 125, color=POS, sw=1.5))
    out.append(text(230, 140, "Q(t)", size=10, bold=True, color=POS))
    out.append(fitbox(250, 108, 65, 34, "ФНЧ / RRC", size=10, fill=FILL, stroke="#64748b"))
    out.append(arrow(315, 125, 360, 125, color=INK, sw=1.5))
    out.append(circle(375, 125, 14, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    out.append(text(375, 129, "×", size=16, bold=True, color=INK))

    # Carrier oscillator & 90 deg shift
    out.append(fitbox(430, 80, 80, 30, "LO cos(ω_c t)", size=10, fill="#f3e8ff", stroke="#9333ea"))
    out.append(arrow(430, 95, 389, 95, color=INK, sw=1.5))
    out.append(fitbox(430, 125, 80, 30, "-sin(ω_c t)", size=10, fill="#f3e8ff", stroke="#9333ea"))
    out.append(arrow(430, 140, 389, 125, color=INK, sw=1.5))

    # Summer
    out.append(arrow(389, 95, 540, 110, color=INK, sw=1.5))
    out.append(arrow(389, 125, 540, 110, color=INK, sw=1.5))
    out.append(circle(552, 110, 14, fill="#dcfce7", stroke=FIELD, sw=1.5))
    out.append(text(552, 114, "+", size=18, bold=True, color=INK))

    # RF Out
    out.append(arrow(566, 110, 630, 110, color=INK, sw=2))
    out.append(text(600, 98, "s(t) QAM", size=11, bold=True, color=INK))
    out.append(fitbox(630, 93, 130, 34, "Радіотракт / Канал", size=10, fill="#ffedd5", stroke="#ea580c"))

    # ── Section 2: Demodulator (Bottom) ──
    out.append(rect(20, 200, 760, 145, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    out.append(text(35, 218, "ПРИЙМАЧ (Квадратурний демодулятор)", size=12, bold=True, color=INK, anchor="start"))

    # RF In -> Splitter
    out.append(text(35, 270, "Вхід r(t)", size=11, bold=True, color=INK, anchor="start"))
    out.append(arrow(90, 270, 140, 270, color=INK, sw=1.5))
    out.append(circle(148, 270, 8, fill="#cbd5e1", stroke="#475569"))

    # I Demod branch
    out.append(arrow(154, 266, 200, 240, color=INK, sw=1.5))
    out.append(circle(210, 235, 12, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    out.append(text(210, 239, "×", size=14, bold=True, color=INK))
    out.append(arrow(222, 235, 260, 235, color=INK, sw=1.5))
    out.append(fitbox(260, 220, 65, 30, "Матч-фільтр", size=10, fill=FILL, stroke="#64748b"))
    out.append(arrow(325, 235, 370, 235, color=NEG, sw=1.5))
    out.append(text(348, 227, "I_hat", size=10, bold=True, color=NEG))

    # Q Demod branch
    out.append(arrow(154, 274, 200, 300, color=INK, sw=1.5))
    out.append(circle(210, 305, 12, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    out.append(text(210, 309, "×", size=14, bold=True, color=INK))
    out.append(arrow(222, 305, 260, 305, color=INK, sw=1.5))
    out.append(fitbox(260, 290, 65, 30, "Матч-фільтр", size=10, fill=FILL, stroke="#64748b"))
    out.append(arrow(325, 305, 370, 305, color=POS, sw=1.5))
    out.append(text(348, 297, "Q_hat", size=10, bold=True, color=POS))

    # Carrier recovery input
    out.append(fitbox(170, 218, 75, 24, "cos(ω_c t)", size=9, fill="#f3e8ff", stroke="#9333ea"))
    out.append(arrow(210, 242, 210, 247, color=INK, sw=1))
    out.append(fitbox(170, 318, 75, 24, "-sin(ω_c t)", size=9, fill="#f3e8ff", stroke="#9333ea"))
    out.append(arrow(210, 318, 210, 317, color=INK, sw=1))

    # Slicer / Demapper / AGC
    out.append(fitbox(370, 220, 110, 100, "AGC / Еквалайзер\n───\nДемодулятор / Slicer\n(Max-Log LLR)", size=10, fill="#e0f2fe", stroke="#0284c7"))
    out.append(arrow(480, 270, 540, 270, color=INK, sw=1.5))
    out.append(fitbox(540, 250, 100, 40, "P / S\nДекодер Грея", size=11, fill="#dcfce7", stroke=FIELD))
    out.append(arrow(640, 270, 720, 270, color=INK, sw=2))
    out.append(text(745, 270, "Біти", size=11, bold=True, color=INK, anchor="start"))

    render(os.path.join(os.path.dirname(__file__), "img", "qam-mod-chain.svg"), w, h, *out)

def fig_qam_noise_margin():
    w, h = 760, 380
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 24, "Запас стійкості від шуму: стискання відстані d_min зі зростанням M", size=15, bold=True))

    import random
    random.seed(42)

    configs = [
        ("QPSK (4-QAM)", 140, 2, 80, 0.18, "2 біти/символ (велике d_min)"),
        ("16-QAM", 380, 4, 80, 0.10, "4 біти/символ (середнє d_min)"),
        ("64-QAM", 620, 8, 80, 0.05, "6 бітів/символ (тісне d_min)")
    ]

    for title, cx, side, grid_w, sigma, desc in configs:
        out.append(rect(cx - grid_w - 15, 52, 2*grid_w + 30, 280, fill="#f8fafc", stroke="#e2e8f0", rx=8))
        out.append(text(cx, 72, title, size=13, bold=True, color=INK))
        
        cy = 190
        step = (2 * grid_w) / max(side, 2)
        
        # Axes
        out.append(line(cx - grid_w, cy, cx + grid_w, cy, color="#cbd5e1", sw=1.5))
        out.append(line(cx, cy - grid_w, cx, cy + grid_w, color="#cbd5e1", sw=1.5))

        # Grid points & noise clouds
        vals = [-grid_w + (i + 0.5) * step for i in range(side)]
        for rx in vals:
            for ry in vals:
                # Decision region border
                out.append(rect(cx + rx - step/2, cy + ry - step/2, step, step, fill="none", stroke="#e2e8f0", sw=1, rx=0))
                # Scatter points
                for _ in range(12):
                    nx = cx + rx + random.gauss(0, sigma * grid_w)
                    ny = cy + ry + random.gauss(0, sigma * grid_w)
                    out.append(circle(nx, ny, 1.5, fill="#93c5fd", stroke="none"))
                # Center point
                out.append(circle(cx + rx, cy + ry, 3, fill=POS))

        out.append(text(cx, 316, desc, size=10, color=MUTED, bold=True))

    out.append(text(w/2, 355, "За однакової середньої потужності сигналу вищі порядки QAM вимагають значно вищого SNR для розрізнення точок", size=11, color=MUTED, italic=True))

    render(os.path.join(os.path.dirname(__file__), "img", "qam-noise-margin.svg"), w, h, *out)

def fig_qam_evm_impairments():
    w, h = 800, 360
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 24, "Типові спотворення сузір'я QAM у реальному радіотракті", size=15, bold=True))

    import math

    panels = [
        ("EVM (Error Vector Magnitude)", 110, 190, "EVM"),
        ("Фазовий шум (Phase Noise)", 300, 190, "PHASE"),
        ("I/Q Дисбаланс посилення", 490, 190, "IQ_GAIN"),
        ("Витік несучої (DC Offset)", 680, 190, "DC_OFFSET")
    ]

    for title, cx, cy, mode in panels:
        out.append(rect(cx - 80, 52, 160, 260, fill="#f8fafc", stroke="#cbd5e1", rx=8))
        out.append(mtext(cx, 72, title, size=11, bold=True, color=INK))

        gw = 55
        out.append(line(cx - gw, cy, cx + gw, cy, color="#cbd5e1", sw=1.5))
        out.append(line(cx, cy - gw, cx, cy + gw, color="#cbd5e1", sw=1.5))

        vals = [-35, -12, 12, 35]
        
        if mode == "EVM":
            for ix in vals:
                for qy in vals:
                    out.append(circle(cx + ix, cy + qy, 2.5, fill=MUTED))
            ix0, qy0 = cx + 35, cy - 35
            ix_m, qy_m = cx + 48, cy - 48
            out.append(circle(ix0, qy0, 4, fill=FIELD))
            out.append(circle(ix_m, qy_m, 4, fill=POS))
            out.append(arrow(ix0, qy0, ix_m, qy_m, color=POS, sw=2))
            out.append(text(cx, cy + 85, "Вектор помилки e(t)", size=10, color=POS, bold=True))

        elif mode == "PHASE":
            for ix in vals:
                for qy in vals:
                    r = math.hypot(ix, qy)
                    phi = math.atan2(qy, ix)
                    for d_phi in [-0.2, -0.1, 0.0, 0.1, 0.2]:
                        px = cx + r * math.cos(phi + d_phi)
                        py = cy + r * math.sin(phi + d_phi)
                        out.append(circle(px, py, 2, fill="#93c5fd", stroke="none"))
            out.append(text(cx, cy + 85, "Дугоподібне розмиття", size=10, color=NEG, bold=True))

        elif mode == "IQ_GAIN":
            for ix in vals:
                for qy in vals:
                    px = cx + ix * 1.3
                    py = cy + qy * 0.7
                    out.append(circle(px, py, 2.5, fill=POS))
            out.append(text(cx, cy + 85, "Прямокутне перекошування", size=10, color=POS, bold=True))

        elif mode == "DC_OFFSET":
            dx, dy = 18, -14
            for ix in vals:
                for qy in vals:
                    out.append(circle(cx + ix, cy + qy, 2, fill="#cbd5e1"))
                    out.append(circle(cx + ix + dx, cy + qy + dy, 2.5, fill=FIELD))
            out.append(arrow(cx, cy, cx + dx, cy + dy, color=FIELD, sw=2))
            out.append(text(cx, cy + 85, "Зсув усього сузір'я", size=10, color=FIELD, bold=True))

    out.append(text(w/2, 335, "Калібрування I/Q, цифровий еквалайзер та адаптивне AGC усувають ці спотворення в сучасних SDR-приймачах", size=11, color=MUTED, italic=True))

    render(os.path.join(os.path.dirname(__file__), "img", "qam-evm-impairments.svg"), w, h, *out)

if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
    fig_qam_constellations()
    fig_qam_mod_chain()
    fig_qam_noise_margin()
    fig_qam_evm_impairments()
    print("QAM Figures generated successfully!")
