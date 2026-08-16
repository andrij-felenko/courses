# -*- coding: utf-8 -*-
"""
Generator script for exponential horn figures.
Uses svgkit from scripts directory.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: exponential-horn-geometry.svg
# -----------------------------------------------------------------------------
def gen_exponential_horn_geometry():
    path = os.path.join(IMG_DIR, 'exponential-horn-geometry.svg')
    w, h = 740, 320
    frags = []

    # Horn parameters for drawing
    x_start = 140
    x_end = 580
    y_center = 160
    r_throat = 22
    r_mouth = 100
    m_rate = math.log(r_mouth / r_throat) / (x_end - x_start)

    # Driver / Transducer box at throat (using single fitbox to avoid overlapping rects)
    dr_w, dr_h = 75, 70
    frags.append(fitbox(x_start - dr_w, y_center - dr_h / 2, dr_w, dr_h, "Акустичний\nвипромінювач\n(динамік)", size=10, fill="#cbd5e1", stroke=LINE, sw=1.8))

    # Wavefronts inside horn
    for i in range(1, 8):
        frac = i / 8.0
        x_wf = x_start + frac * (x_end - x_start)
        r_wf = r_throat * math.exp(m_rate * (x_wf - x_start))
        # Draw curved wavefront
        pts_wf = []
        steps = 20
        for j in range(steps + 1):
            t = -1.0 + 2.0 * j / steps
            yw = y_center + t * r_wf
            xw = x_wf + (1.0 - t * t) * 12 * (frac + 0.2)
            pts_wf.append("%.1f,%.1f" % (xw, yw))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(pts_wf), NEG))

    # Upper and lower exponential profile contours
    pts_upper = []
    pts_lower = []
    num_pts = 60
    for i in range(num_pts + 1):
        x = x_start + (x_end - x_start) * i / num_pts
        r = r_throat * math.exp(m_rate * (x - x_start))
        pts_upper.append((x, y_center - r))
        pts_lower.append((x, y_center + r))

    # Draw shaded horn body
    path_d = ["M %.1f,%.1f" % (pts_upper[0][0], pts_upper[0][1])]
    for px, py in pts_upper[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    path_d.append("L %.1f,%.1f" % (pts_lower[-1][0], pts_lower[-1][1]))
    for px, py in reversed(pts_lower[:-1]):
        path_d.append("L %.1f,%.1f" % (px, py))
    path_d.append("Z")

    frags.append('<path d="%s" fill="#f1f5f9" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), LINE))

    # Center axis line
    frags.append(line(x_start - 80, y_center, x_end + 80, y_center, color=MUTED, sw=1.2, dash="5,5"))

    # Dimension lines & labels
    # Throat S0
    frags.append(line(x_start, y_center - r_throat, x_start, y_center + r_throat, color=POS, sw=2))
    frags.append(fitbox(x_start - 5, y_center - r_throat - 32, 70, 26, "Горло S₀", size=11, fill="#fee2e2", stroke=POS))

    # Mouth SL
    frags.append(line(x_end, y_center - r_mouth, x_end, y_center + r_mouth, color=FIELD, sw=2))
    frags.append(fitbox(x_end - 35, y_center - r_mouth - 32, 70, 26, "Гирло S_L", size=11, fill="#dcfce7", stroke=FIELD))

    # Length L dimension
    y_dim = y_center + r_mouth + 20
    frags.append(line(x_start, y_dim, x_end, y_dim, color=LINE, sw=1.2))
    frags.append(line(x_start, y_center + r_throat, x_start, y_dim + 8, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(x_end, y_center + r_mouth, x_end, y_dim + 8, color=MUTED, sw=1, dash="2,2"))
    frags.append(textbox((x_start + x_end) / 2, y_dim + 2, "Довжина рупора L", size=11, pad=4, fill=BG, stroke=LINE)[0])

    # Formula callout for S(x)
    frags.append(textbox(340, y_center - 55, "Закон розширення:\nS(x) = S₀ · e^(m·x)", size=12, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)[0])

    # Axis arrow for x
    frags.append(arrow(x_end + 20, y_center + 45, x_end + 80, y_center + 45, color=LINE, sw=1.5))
    frags.append(text(x_end + 50, y_center + 63, "вісь x", size=11, anchor="middle"))

    render(path, w, h, *frags, title="Геометрія експоненційного рупора")

# -----------------------------------------------------------------------------
# Figure 2: impedance-vs-frequency.svg
# -----------------------------------------------------------------------------
def gen_impedance_vs_frequency():
    path = os.path.join(IMG_DIR, 'impedance-vs-frequency.svg')
    w, h = 740, 340
    frags = []

    # Plot axes setup
    x0, y0 = 80, 260
    pw, ph = 600, 200

    # Grid & Axes
    frags.append(rect(x0, y0 - ph, pw, ph, fill="#fafafa", stroke="#e2e8f0", sw=1, rx=2))

    # Grid lines
    for i in range(1, 7):
        gx = x0 + i * (pw / 6.0)
        frags.append(line(gx, y0, gx, y0 - ph, color="#e2e8f0", sw=1, dash="2,2"))
        ratio_val = i * 0.5
        frags.append(text(gx, y0 + 18, "%.1f" % ratio_val, size=11, color=MUTED))

    for j in range(1, 5):
        gy = y0 - j * (ph / 4.0)
        frags.append(line(x0, gy, x0 + pw, gy, color="#e2e8f0", sw=1, dash="2,2"))
        frags.append(text(x0 - 10, gy + 4, "%.2f" % (j * 0.25), size=11, anchor="end", color=MUTED))

    frags.append(text(x0 - 10, y0 + 4, "0.00", size=11, anchor="end", color=MUTED))
    frags.append(text(x0, y0 + 18, "0.0", size=11, color=MUTED))

    # Cutoff frequency fc line at f/fc = 1.0 (index 2 in grid: 2 * 0.5 = 1.0)
    x_fc = x0 + 2 * (pw / 6.0)
    frags.append(line(x_fc, y0, x_fc, y0 - ph, color=POS, sw=1.8, dash="4,4"))
    frags.append(fitbox(x_fc + 5, y0 - ph + 20, 110, 24, "Частота зрізу f_c", size=10, fill="#fee2e2", stroke=POS))

    # Axis Labels
    frags.append(arrow(x0, y0, x0 + pw + 25, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0, x0, y0 - ph - 15, color=LINE, sw=1.5))
    frags.append(text(x0 + pw / 2, y0 + 38, "Відносна частота (f / f_c)", size=12, bold=True))
    frags.append(text(x0 - 45, y0 - ph / 2, "Нормований імпеданс Z / (ρc/S₀)", size=11, bold=True, anchor="middle"))

    # Curves for Infinite Exponential Horn:
    pts_R = []
    pts_X = []
    num_steps = 150

    for step in range(num_steps + 1):
        f_ratio = 3.0 * step / num_steps
        px = x0 + (f_ratio / 3.0) * pw

        if f_ratio < 1.0:
            r_val = 0.0
            x_val = f_ratio if f_ratio > 0.01 else 0.0  # imaginary part below cutoff
        else:
            r_val = math.sqrt(1.0 - 1.0 / (f_ratio * f_ratio))
            x_val = 1.0 / f_ratio

        py_R = y0 - r_val * ph
        py_X = y0 - x_val * ph

        pts_R.append("%.1f,%.1f" % (px, py_R))
        if f_ratio >= 1.0:
            pts_X.append("%.1f,%.1f" % (px, py_X))

    # Draw R_in (Active Radiation Resistance) - Green curve
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_R), FIELD))

    # Draw X_in (Reactive Mass Load) - Blue curve (f >= fc)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,3"/>' % (" ".join(pts_X), NEG))

    # Regions background highlighting
    frags.append(rect(x0 + 2, y0 - ph + 2, x_fc - x0 - 2, ph - 4, fill="#fee2e2", stroke="none", rx=0))
    frags.append(text((x0 + x_fc) / 2, y0 - ph + 50, "Область згасання\n(f < f_c, R = 0)", size=11, color=POS, bold=True))

    frags.append(text(x0 + 420, y0 - ph + 50, "Область поширення (f > f_c)\nR → 1 (активне випромінювання)", size=11, color=FIELD, bold=True))

    # Legend box
    frags.append(rect(x0 + 350, y0 - 80, 230, 55, fill=BG, stroke=LINE, sw=1, rx=4))
    frags.append(line(x0 + 360, y0 - 62, x0 + 390, y0 - 62, color=FIELD, sw=2.5))
    frags.append(text(x0 + 400, y0 - 58, "Активний опір R_in (випромінювання)", size=10, anchor="start"))
    frags.append(line(x0 + 360, y0 - 38, x0 + 390, y0 - 38, color=NEG, sw=2.2, dash="5,3"))
    frags.append(text(x0 + 400, y0 - 34, "Реактивний опір X_in (інерційність)", size=10, anchor="start"))

    render(path, w, h, *frags, title="Акустичний імпеданс у горлі нескінченного експоненційного рупора")

# -----------------------------------------------------------------------------
# Figure 3: webster-wave-propagation.svg
# -----------------------------------------------------------------------------
def gen_webster_wave_propagation():
    path = os.path.join(IMG_DIR, 'webster-wave-propagation.svg')
    w, h = 740, 320
    frags = []

    # Diagram showing phase velocity cp/c vs f/fc and wave behaviors
    x0, y0 = 80, 240
    pw, ph = 600, 170

    frags.append(rect(x0, y0 - ph, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))

    # Grid & Axes
    x_fc = x0 + (1.0 / 3.0) * pw
    frags.append(line(x_fc, y0, x_fc, y0 - ph, color=POS, sw=1.8, dash="4,4"))

    # Phase velocity curve: c_p / c = 1 / sqrt(1 - (fc/f)^2)
    pts_cp = []
    num_pts = 100
    for i in range(1, num_pts + 1):
        f_ratio = 1.01 + 2.0 * i / num_pts
        px = x0 + (f_ratio / 3.0) * pw
        val = 1.0 / math.sqrt(1.0 - 1.0 / (f_ratio * f_ratio))
        # Cap for plotting
        val_clamped = min(val, 3.5)
        py = y0 - (val_clamped / 3.5) * ph
        pts_cp.append("%.1f,%.1f" % (px, py))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_cp), NEG))

    # Baseline c_p = c (val = 1.0)
    y_c = y0 - (1.0 / 3.5) * ph
    frags.append(line(x0, y_c, x0 + pw, y_c, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(x0 + pw - 10, y_c - 6, "c_p = c (недиспесійне середовище)", size=10, anchor="end", color=MUTED))

    # Evanescent region (f < fc) - spatial attenuation alpha
    pts_alpha = []
    for i in range(num_pts + 1):
        f_ratio = 1.0 * i / num_pts
        px = x0 + (f_ratio / 3.0) * pw
        alpha_val = math.sqrt(1.0 - f_ratio * f_ratio)  # normalized alpha
        py = y0 - (alpha_val / 3.5) * ph
        pts_alpha.append("%.1f,%.1f" % (px, py))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>' % (" ".join(pts_alpha), POS))

    # Axis Labels
    frags.append(arrow(x0, y0, x0 + pw + 20, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0, x0, y0 - ph - 15, color=LINE, sw=1.5))
    frags.append(text(x0 + pw / 2, y0 + 35, "Відносна частота (f / f_c)", size=12, bold=True))
    frags.append(text(x0 - 45, y0 - ph / 2, "Відносна фазова швидкість c_p / c", size=11, bold=True, anchor="middle"))

    # Labels for curves
    frags.append(textbox(x_fc - 70, y0 - ph + 45, "Еванесцентний режим\n(експоненційне згасання α)", size=10, pad=5, fill="#fee2e2", stroke=POS)[0])
    frags.append(textbox(x0 + 360, y0 - ph + 45, "Дисперсійне поширення\nc_p = c / √(1 - (f_c/f)²)", size=10, pad=5, fill="#dbeafe", stroke=NEG)[0])

    render(path, w, h, *frags, title="Дисперсія фазової швидкості та згасання в експоненційному рупорі")

# -----------------------------------------------------------------------------
# Figure 4: finite-horn-reflections.svg
# -----------------------------------------------------------------------------
def gen_finite_horn_reflections():
    path = os.path.join(IMG_DIR, 'finite-horn-reflections.svg')
    w, h = 740, 330
    frags = []

    x0, y0 = 80, 250
    pw, ph = 600, 180

    frags.append(rect(x0, y0 - ph, pw, ph, fill="#fafafa", stroke="#e2e8f0", sw=1, rx=2))

    # Cutoff line
    x_fc = x0 + (1.0 / 3.5) * pw
    frags.append(line(x_fc, y0, x_fc, y0 - ph, color=MUTED, sw=1.5, dash="4,4"))

    # Infinite horn reference curve (smooth)
    pts_inf = []
    num_pts = 160
    for i in range(num_pts + 1):
        f_ratio = 3.5 * i / num_pts
        px = x0 + (f_ratio / 3.5) * pw
        if f_ratio < 1.0:
            r_val = 0.0
        else:
            r_val = math.sqrt(1.0 - 1.0 / (f_ratio * f_ratio))
        py = y0 - r_val * (ph * 0.75)
        pts_inf.append("%.1f,%.1f" % (px, py))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' % (" ".join(pts_inf), MUTED))

    # Finite horn curve (with ripples due to reflections from mouth)
    pts_fin = []
    for i in range(num_pts + 1):
        f_ratio = 3.5 * i / num_pts
        px = x0 + (f_ratio / 3.5) * pw
        if f_ratio < 1.0:
            # Small acoustic resonance peaks even below cutoff in finite tube
            r_val = 0.08 * math.exp(2 * f_ratio) * abs(math.sin(3.5 * math.pi * f_ratio))
        else:
            base_r = math.sqrt(1.0 - 1.0 / (f_ratio * f_ratio))
            # Ripple amplitude decays as 1 / (f_ratio * mouth_size)
            ripple = (0.35 / (f_ratio + 0.2)) * math.sin(6.0 * math.pi * (f_ratio - 1.0)) * math.exp(-0.4 * (f_ratio - 1.0))
            r_val = max(0.0, base_r + ripple)
        py = y0 - r_val * (ph * 0.75)
        pts_fin.append("%.1f,%.1f" % (px, py))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_fin), FIELD))

    # Axes
    frags.append(arrow(x0, y0, x0 + pw + 20, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0, x0, y0 - ph - 15, color=LINE, sw=1.5))
    frags.append(text(x0 + pw / 2, y0 + 35, "Відносна частота (f / f_c)", size=12, bold=True))
    frags.append(text(x0 - 45, y0 - ph / 2, "Вхідний опір R_in / (ρc/S₀)", size=11, bold=True, anchor="middle"))

    # Legend and callout
    frags.append(rect(x0 + 260, y0 - ph + 15, 320, 60, fill=BG, stroke=LINE, sw=1, rx=4))
    frags.append(line(x0 + 270, y0 - ph + 32, x0 + 300, y0 - ph + 32, color=MUTED, sw=2, dash="4,4"))
    frags.append(text(x0 + 310, y0 - ph + 36, "Ідеальний нескінченний рупор (без відбитів)", size=10, anchor="start"))
    frags.append(line(x0 + 270, y0 - ph + 52, x0 + 300, y0 - ph + 52, color=FIELD, sw=2.5))
    frags.append(text(x0 + 310, y0 - ph + 56, "Скінченний рупор (пульсації через відбиття від гирла)", size=10, anchor="start"))

    render(path, w, h, *frags, title="Вхідний опір скінченного експоненційного рупора з відбиттям від гирла")

if __name__ == '__main__':
    gen_exponential_horn_geometry()
    gen_impedance_vs_frequency()
    gen_webster_wave_propagation()
    gen_finite_horn_reflections()
    print("All figures for exponential-horn generated successfully.")
