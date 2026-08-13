# -*- coding: utf-8 -*-
"""Фігури до теми «Аналітичний сигнал і перетворення Гільберта».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. analytic-signal-concept.svg ─────────────────────────────────────────────
def fig_analytic_signal_concept():
    path = os.path.join(IMG, 'analytic-signal-concept.svg')
    f = []

    # 2D projection/representation of Complex Plane (Re, Im) & Instantaneous Envelope A(t) / Phase phi(t)
    w_box, h_box = 780, 340
    
    # Left diagram: Complex plane with vector z(t) = x(t) + j x_hat(t)
    cx, cy = 190, 180
    r = 110

    # Grid / Circle
    f.append(circle(cx, cy, r, fill="#f8fafc", stroke=MUTED, sw=1.0))
    f.append(line(cx - 140, cy, cx + 140, cy, color=LINE, sw=1.2)) # Re axis
    f.append(line(cx, cy - 140, cx, cy + 140, color=LINE, sw=1.2)) # Im axis

    f.append(text(cx + 145, cy + 15, "Re = x(t)", size=11, color=INK, anchor="start", bold=True))
    f.append(text(cx + 15, cy - 142, "Im = x̂(t)", size=11, color=NEG, anchor="start", bold=True))

    # Vector z(t) at angle phi = 50 degrees
    phi = math.radians(50)
    vx = cx + r * math.cos(phi)
    vy = cy - r * math.sin(phi) # inverted y axis

    # Vector arrow
    f.append(line(cx, cy, vx, vy, color=POS, sw=2.5))
    f.append(circle(vx, vy, 4, fill=POS, stroke=POS, sw=1))

    # Projections
    f.append(line(vx, vy, vx, cy, color=POS, sw=1.2, dash="3,3")) # Re projection
    f.append(line(vx, vy, cx, vy, color=NEG, sw=1.2, dash="3,3")) # Im projection

    f.append(text(vx, cy + 18, "x(t)", size=11, color=POS, bold=True))
    f.append(text(cx - 25, vy + 4, "x̂(t)", size=11, color=NEG, bold=True))

    # Angle arc for phi(t)
    arc_pts = []
    for deg in range(0, 51, 5):
        rad = math.radians(deg)
        arc_pts.append((cx + 35 * math.cos(rad), cy - 35 * math.sin(rad)))
    poly_arc = " ".join("%.1f,%.1f" % p for p in arc_pts)
    f.append(f'<polyline points="{poly_arc}" fill="none" stroke="{FIELD}" stroke-width="1.8"/>')
    f.append(text(cx + 45, cy - 15, "φ(t)", size=12, color=FIELD, bold=True))

    # Label for z(t) vector
    f.append(text(vx + 15, vy - 10, "z(t) = x(t) + j·x̂(t)", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(cx + 45, cy - 70, "A(t) = |z(t)|", size=11, color=POS, italic=True, anchor="start"))

    # Right diagram: Signal in time domain showing x(t), x̂(t), and envelope A(t)
    tx0, ty0 = 410, 180
    tw, th = 330, 240

    f.append(line(tx0, ty0, tx0 + tw, ty0, color=LINE, sw=1.2)) # time axis
    f.append(line(tx0, ty0 - 110, tx0, ty0 + 110, color=LINE, sw=1.2)) # amplitude axis
    f.append(text(tx0 + tw - 5, ty0 + 20, "Час t", size=11, color=MUTED, anchor="end"))
    f.append(text(tx0 + 10, ty0 - 115, "Амплітуда", size=11, color=MUTED, anchor="start"))

    # Generate carrier modulated by envelope
    pts_x = []
    pts_xhat = []
    pts_env_p = []
    pts_env_m = []

    N_pts = 150
    for i in range(N_pts + 1):
        t_rel = i / N_pts # 0 to 1
        px = tx0 + t_rel * (tw - 20)
        
        # Envelope A(t) = 85 * (0.35 + 0.65 * sin(pi * t))
        env = 85.0 * (0.35 + 0.65 * math.sin(math.pi * t_rel))
        # Instantaneous phase phi(t) = 2 * pi * 5 * t
        ph = 2.0 * math.pi * 5.0 * t_rel
        
        val_x = env * math.cos(ph)
        val_xhat = env * math.sin(ph)

        pts_x.append((px, ty0 - val_x))
        pts_xhat.append((px, ty0 - val_xhat))
        pts_env_p.append((px, ty0 - env))
        pts_env_m.append((px, ty0 + env))

    str_x = " ".join("%.1f,%.1f" % p for p in pts_x)
    str_xhat = " ".join("%.1f,%.1f" % p for p in pts_xhat)
    str_env_p = " ".join("%.1f,%.1f" % p for p in pts_env_p)
    str_env_m = " ".join("%.1f,%.1f" % p for p in pts_env_m)

    # Draw Hilbert transform xhat(t) first (background)
    f.append(f'<polyline points="{str_xhat}" fill="none" stroke="{NEG}" stroke-width="1.2" stroke-dasharray="3,3"/>')
    # Draw real signal x(t)
    f.append(f'<polyline points="{str_x}" fill="none" stroke="{POS}" stroke-width="1.8"/>')
    # Draw envelope A(t)
    f.append(f'<polyline points="{str_env_p}" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')
    f.append(f'<polyline points="{str_env_m}" fill="none" stroke="{FIELD}" stroke-width="2.0" stroke-dasharray="4,4"/>')

    # Legend / Labels for time plot
    f.append(text(tx0 + 60, ty0 - 95, "Огинаюча A(t)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(tx0 + 190, ty0 - 55, "Дійсний x(t)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(tx0 + 190, ty0 + 60, "Уявний x̂(t)", size=11, color=NEG, bold=True, anchor="start"))

    render(path, w_box, h_box, *f)


# ── 2. hilbert-spectrum.svg ───────────────────────────────────────────────────
def fig_hilbert_spectrum():
    path = os.path.join(IMG, 'hilbert-spectrum.svg')
    f = []
    w_box, h_box = 780, 360

    # Top graph: Spectrum of Real Signal X(f)
    # Bottom graph: Spectrum of Analytic Signal Z(f)
    x0 = 80
    w_axis = 640

    # Top: Real spectrum X(f) (Symmetric positive and negative frequencies)
    y_top = 130
    f.append(line(x0, y_top, x0 + w_axis, y_top, color=LINE, sw=1.4)) # f axis
    f.append(line(x0 + w_axis/2, y_top - 90, x0 + w_axis/2, y_top + 20, color=LINE, sw=1.2)) # f=0 axis

    f.append(text(x0 + w_axis - 10, y_top + 18, "Частота f", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 + w_axis/2, y_top + 18, "0", size=11, color=INK, anchor="middle"))
    f.append(text(x0 + 10, y_top - 75, "|X(f)| (Дійсний сигнал)", size=12, color=INK, bold=True, anchor="start"))

    # Left lobe (-f_c) and Right lobe (+f_c)
    cx_neg = x0 + w_axis/2 - 160
    cx_pos = x0 + w_axis/2 + 160

    # Draw lobes
    def draw_lobe(cx_l, cy_l, amp, color, fill_color):
        pts = [(cx_l - 70, cy_l)]
        for i in range(41):
            dx = -70 + i * (140 / 40)
            val = amp * math.exp(- (dx / 30)**2)
            pts.append((cx_l + dx, cy_l - val))
        pts.append((cx_l + 70, cy_l))
        poly_str = " ".join("%.1f,%.1f" % p for p in pts)
        f.append(f'<polygon points="{poly_str}" fill="{fill_color}" fill-opacity="0.5" stroke="{color}" stroke-width="1.8"/>')

    draw_lobe(cx_neg, y_top, 55, NEG, "#dbeafe")
    draw_lobe(cx_pos, y_top, 55, NEG, "#dbeafe")

    f.append(text(cx_neg, y_top - 63, "X(-f)", size=11, color=NEG, bold=True))
    f.append(text(cx_pos, y_top - 63, "X(+f)", size=11, color=NEG, bold=True))

    # Bottom: Analytic signal spectrum Z(f) (Negative zeroed, Positive doubled 2*X(f))
    y_bot = 300
    f.append(line(x0, y_bot, x0 + w_axis, y_bot, color=LINE, sw=1.4))
    f.append(line(x0 + w_axis/2, y_bot - 110, x0 + w_axis/2, y_bot + 20, color=LINE, sw=1.2))

    f.append(text(x0 + w_axis - 10, y_bot + 18, "Частота f", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 + w_axis/2, y_bot + 18, "0", size=11, color=INK, anchor="middle"))
    f.append(text(x0 + 10, y_bot - 95, "|Z(f)| (Аналітичний сигнал)", size=12, color=POS, bold=True, anchor="start"))

    # Zero spectrum on negative side
    f.append(line(x0 + 40, y_bot, x0 + w_axis/2 - 10, y_bot, color=MUTED, sw=2.5))
    f.append(text(cx_neg, y_bot - 15, "0 (пригнічено)", size=11, color=MUTED, italic=True))

    # Doubled lobe on positive side
    draw_lobe(cx_pos, y_bot, 90, POS, "#fee2e2")
    f.append(text(cx_pos, y_bot - 98, "2·X(+f)", size=12, color=POS, bold=True))

    # Arrow transition from top to bottom
    f.append(arrow(x0 + w_axis - 70, y_top + 25, x0 + w_axis - 70, y_bot - 45, color=FIELD, sw=2.0))
    f.append(text(x0 + w_axis - 60, (y_top + y_bot)/2, "Z(f) = 2·U(f)·X(f)", size=11, color=FIELD, bold=True, anchor="start"))

    render(path, w_box, h_box, *f)


# ── 3. envelope-phase-demod.svg ─────────────────────────────────────────────
def fig_envelope_phase_demod():
    path = os.path.join(IMG, 'envelope-phase-demod.svg')
    f = []
    w_box, h_box = 790, 320

    x_in = 50
    y_in = 160

    # Input node
    f.append(circle(x_in, y_in, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(x_in - 10, y_in - 15, "x(t)", size=13, color=INK, bold=True, anchor="end"))

    # Split lines
    y_top_path = 80
    y_bot_path = 240

    f.append(line(x_in, y_in, x_in + 40, y_in, color=LINE, sw=1.8))
    f.append(line(x_in + 40, y_in, x_in + 40, y_top_path, color=LINE, sw=1.8))
    f.append(line(x_in + 40, y_in, x_in + 40, y_bot_path, color=LINE, sw=1.8))

    # Top Path: Delay matching (or direct)
    tb_top, w_top, h_top = textbox(x_in + 150, y_top_path, "Затримка τ\n(узгодження фази)", size=11, pad=8, fill="#f1f5f9", stroke=LINE)
    f.append(tb_top[0])
    f.append(arrow(x_in + 40, y_top_path, x_in + 150 - w_top/2, y_top_path, color=LINE, sw=1.8))

    # Bottom Path: Hilbert Transformer
    tb_hilb, w_hilb, h_hilb = textbox(x_in + 150, y_bot_path, "Фільтр Гільберта\nH(f) = -j sgn(f)", size=11, pad=8, fill="#dbeafe", stroke=NEG, color=NEG, bold=True)
    f.append(tb_hilb[0])
    f.append(arrow(x_in + 40, y_bot_path, x_in + 150 - w_hilb/2, y_bot_path, color=NEG, sw=1.8))

    # Output of top and bottom paths
    x_mid = 310
    f.append(arrow(x_in + 150 + w_top/2, y_top_path, x_mid, y_top_path, color=POS, sw=1.8))
    f.append(text(x_mid - 30, y_top_path - 12, "I(t) = x(t)", size=12, color=POS, bold=True))

    f.append(arrow(x_in + 150 + w_hilb/2, y_bot_path, x_mid, y_bot_path, color=NEG, sw=1.8))
    f.append(text(x_mid - 30, y_bot_path + 22, "Q(t) = x̂(t)", size=12, color=NEG, bold=True))

    # Computation blocks
    # Block 1: Envelope Detector sqrt(I^2 + Q^2)
    tb_env, w_env, h_env = textbox(470, y_top_path, "Обчислення огинаючої\nA(t) = √(I² + Q²)", size=12, pad=10, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True)
    f.append(tb_env[0])
    f.append(line(x_mid, y_top_path, 470 - w_env/2, y_top_path, color=POS, sw=1.8))
    f.append(line(x_mid, y_bot_path, x_mid, y_top_path + 30, color=NEG, sw=1.8))
    f.append(arrow(x_mid, y_top_path + 30, 470 - w_env/2, y_top_path + 15, color=NEG, sw=1.8))

    # Block 2: Phase/Frequency Detector arctan2(Q, I)
    tb_ph, w_ph, h_ph = textbox(470, y_bot_path, "Обчислення фази\nφ(t) = atan2(Q, I)", size=12, pad=10, fill="#fef3c7", stroke="#d97706", color="#b45309", bold=True)
    f.append(tb_ph[0])
    f.append(arrow(x_mid, y_bot_path, 470 - w_ph/2, y_bot_path, color=NEG, sw=1.8))
    f.append(line(x_mid + 40, y_top_path, x_mid + 40, y_bot_path - 30, color=POS, sw=1.8))
    f.append(arrow(x_mid + 40, y_bot_path - 30, 470 - w_ph/2, y_bot_path - 15, color=POS, sw=1.8))

    # Final outputs
    f.append(arrow(470 + w_env/2, y_top_path, 720, y_top_path, color=FIELD, sw=2.0))
    f.append(text(725, y_top_path + 4, "A(t) (Амплітудна демодуляція)", size=11, color=FIELD, bold=True, anchor="start"))

    f.append(arrow(470 + w_ph/2, y_bot_path, 600, y_bot_path, color="#b45309", sw=2.0))
    f.append(text(605, y_bot_path - 12, "φ(t) (Фазова демодуляція)", size=11, color="#b45309", bold=True, anchor="start"))

    # Differentiator block for frequency
    tb_diff, w_diff, h_diff = textbox(650, y_bot_path + 35, "dφ/dt / 2π", size=11, pad=5, fill="#fff7ed", stroke="#d97706")
    f.append(tb_diff[0])
    f.append(line(580, y_bot_path, 580, y_bot_path + 35, color="#b45309", sw=1.5))
    f.append(arrow(580, y_bot_path + 35, 650 - w_diff/2, y_bot_path + 35, color="#b45309", sw=1.5))
    f.append(arrow(650 + w_diff/2, y_bot_path + 35, 740, y_bot_path + 35, color="#b45309", sw=1.5))
    f.append(text(745, y_bot_path + 39, "f_inst(t) (Частотна демодуляція)", size=11, color="#b45309", bold=True, anchor="start"))

    render(path, w_box, h_box, *f)


# ── 4. fir-hilbert-transformer.svg ───────────────────────────────────────────
def fig_fir_hilbert_transformer():
    path = os.path.join(IMG, 'fir-hilbert-transformer.svg')
    f = []
    w_box, h_box = 780, 320

    # Plot of Discrete FIR Hilbert Transformer Impulse Response h[n]
    x0 = 80
    y0 = 170
    w_axis = 640

    f.append(line(x0, y0, x0 + w_axis, y0, color=LINE, sw=1.4)) # n axis
    f.append(line(x0 + w_axis/2, y0 - 120, x0 + w_axis/2, y0 + 110, color=LINE, sw=1.4)) # n=0 axis

    f.append(text(x0 + w_axis - 10, y0 + 20, "Відлік n", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 + w_axis/2 - 15, y0 - 105, "h[n]", size=12, color=INK, bold=True, anchor="end"))
    f.append(text(x0 + w_axis/2 + 10, y0 + 20, "0", size=11, color=INK))

    # Compute discrete stems for n from -12 to +12
    N_max = 12
    dx = (w_axis / 2 - 40) / N_max

    for n in range(-N_max, N_max + 1):
        px = x0 + w_axis/2 + n * dx
        
        if n == 0:
            val = 0.0
        elif n % 2 == 0:
            val = 0.0 # Even samples are exactly zero!
        else:
            # Windowed Hilbert impulse response
            # Ideal: 2 / (pi * n)
            window = 0.54 + 0.46 * math.cos(math.pi * n / N_max) # Hamming window
            val = (2.0 / (math.pi * n)) * window

        py = y0 - val * 120.0

        # Stem line
        stem_color = POS if val > 0 else (NEG if val < 0 else MUTED)
        f.append(line(px, y0, px, py, color=stem_color, sw=1.8))
        # Stem marker
        f.append(circle(px, py, 3.5, fill=stem_color, stroke=stem_color, sw=1))

        # n label for key points
        if n in [-5, -3, -1, 1, 3, 5]:
            lbl_y = y0 + 18 if val >= 0 else y0 - 10
            f.append(text(px, lbl_y, str(n), size=10, color=INK))

    # Annotations
    f.append(text(x0 + w_axis/2 + 3 * dx, y0 - 90, "Непарні n: h[n] = 2 / (π·n)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(x0 + w_axis/2 + 4 * dx, y0 + 55, "Парні n: h[n] = 0 (економія 50% множень!)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(x0 + 40, y0 - 90, "Антисиметрія: h[-n] = -h[n]", size=11, color=NEG, bold=True, anchor="start"))

    render(path, w_box, h_box, *f)


if __name__ == '__main__':
    fig_analytic_signal_concept()
    fig_hilbert_spectrum()
    fig_envelope_phase_demod()
    fig_fir_hilbert_transformer()
    print("Всі фігури успішно згенеровано у ./img/")
