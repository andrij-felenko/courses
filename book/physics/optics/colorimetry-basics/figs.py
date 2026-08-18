# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Спектральні функції чутливості CIE 1931 x̄(λ), ȳ(λ), z̄(λ)
# ═══════════════════════════════════════════════════════════════════════════
def fig_cie1931_cmf():
    W, H = 720, 440
    f = []
    f.append(text(W / 2, 28, 'Спектральні функції чутливості спостерігача CIE 1931 (2°)',
                  16, INK, 'middle', bold=True))

    gx0, gy0 = 80, 370
    gw, gh = 580, 300

    # Grid & Axes
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.8))
    f.append(text(gx0 + gw / 2, gy0 + 42, 'Довжина хвилі λ (нм)', 13, INK, 'middle', bold=True))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">%s</text>' %
             (gx0 - 55, gy0 - gh / 2, FONT, INK, gx0 - 55, gy0 - gh / 2, esc('Амплітуда (відн. од.)')))

    # X-axis ticks (380 nm to 780 nm)
    for wl in range(380, 781, 50):
        xx = gx0 + ((wl - 380) / 400.0) * gw
        f.append(line(xx, gy0, xx, gy0 + 6, color=MUTED, sw=1))
        f.append(text(xx, gy0 + 20, str(wl), 11, MUTED, 'middle'))
        if wl > 380 and wl < 780:
            f.append(line(xx, gy0, xx, gy0 - gh, color=LINE, sw=0.5, dash='2,4'))

    # Y-axis ticks (0.0 to 2.0)
    for val in [0.0, 0.5, 1.0, 1.5, 2.0]:
        yy = gy0 - (val / 2.0) * gh
        f.append(line(gx0 - 6, yy, gx0, yy, color=MUTED, sw=1))
        f.append(text(gx0 - 12, yy + 4, '%.1f' % val, 11, MUTED, 'end'))
        if val > 0:
            f.append(line(gx0, yy, gx0 + gw, yy, color=LINE, sw=0.5, dash='2,4'))

    def cmf_values(wl):
        z = 1.74 * math.exp(-((wl - 446) / 35.0)**2)
        y = 1.00 * math.exp(-((wl - 555) / 47.0)**2)
        x = 1.06 * math.exp(-((wl - 598) / 48.0)**2) + 0.36 * math.exp(-((wl - 442) / 26.0)**2)
        return x, y, z

    pts_x, pts_y, pts_z = [], [], []
    for wl in range(380, 781, 4):
        xx = gx0 + ((wl - 380) / 400.0) * gw
        xv, yv, zv = cmf_values(wl)
        pts_x.append((xx, gy0 - (xv / 2.0) * gh))
        pts_y.append((xx, gy0 - (yv / 2.0) * gh))
        pts_z.append((xx, gy0 - (zv / 2.0) * gh))

    def make_path(pts):
        d = ["M %.1f %.1f" % pts[0]]
        for px_i, py_i in pts[1:]:
            d.append("L %.1f %.1f" % (px_i, py_i))
        return " ".join(d)

    # Plot Z_bar (Blue)
    f.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.8"/>' % make_path(pts_z))
    # Plot Y_bar (Green - V(λ))
    f.append('<path d="%s" fill="none" stroke="#16a34a" stroke-width="2.8"/>' % make_path(pts_y))
    # Plot X_bar (Red)
    f.append('<path d="%s" fill="none" stroke="#dc2626" stroke-width="2.8"/>' % make_path(pts_x))

    # Peak Annotations
    f.append(text(gx0 + ((445 - 380)/400.0)*gw, gy0 - (1.75/2.0)*gh - 10, 'z̄(λ)', 13, '#2563eb', 'middle', bold=True))
    f.append(text(gx0 + ((555 - 380)/400.0)*gw + 5, gy0 - (1.02/2.0)*gh - 10, 'ȳ(λ) ≡ V(λ)', 13, '#16a34a', 'middle', bold=True))
    f.append(text(gx0 + ((600 - 380)/400.0)*gw + 15, gy0 - (1.08/2.0)*gh - 10, 'x̄(λ)', 13, '#dc2626', 'middle', bold=True))

    # Legend box
    lx, ly = gx0 + gw - 210, gy0 - gh + 20
    f.append(rect(lx, ly, 195, 80, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    f.append(line(lx + 15, ly + 20, lx + 45, ly + 20, color='#dc2626', sw=2.5))
    f.append(text(lx + 55, ly + 24, 'x̄(λ) — червона складова', 11, INK, 'start'))
    f.append(line(lx + 15, ly + 40, lx + 45, ly + 40, color='#16a34a', sw=2.5))
    f.append(text(lx + 55, ly + 44, 'ȳ(λ) — яскравість V(λ)', 11, INK, 'start'))
    f.append(line(lx + 15, ly + 60, lx + 45, ly + 60, color='#2563eb', sw=2.5))
    f.append(text(lx + 55, ly + 64, 'z̄(λ) — синя складова', 11, INK, 'start'))

    render(os.path.join(IMG, 'cie1931-cmf.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Лінія чорного тіла (Planckian Locus) та діаграма CIE 1931
# ═══════════════════════════════════════════════════════════════════════════
def fig_planckian_locus():
    W, H = 720, 480
    f = []
    f.append(text(W / 2, 28, 'Лінія чорного тіла (Planckian Locus) та колірна температура',
                  16, INK, 'middle', bold=True))

    gx0, gy0 = 75, 430
    gw, gh = 580, 370

    # Axes
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.8))
    f.append(text(gx0 + gw + 12, gy0 + 4, 'x', 14, INK, 'start', bold=True))
    f.append(text(gx0 - 10, gy0 - gh - 5, 'y', 14, INK, 'end', bold=True))

    # Ticks
    for i in range(1, 9):
        vx = i * 0.1
        xx = gx0 + (vx / 0.8) * (gw - 30)
        f.append(line(xx, gy0, xx, gy0 + 4, color=MUTED, sw=1))
        f.append(text(xx, gy0 + 18, '%.1f' % vx, 10, MUTED, 'middle'))

    for i in range(1, 10):
        vy = i * 0.1
        yy = gy0 - (vy / 0.9) * (gh - 30)
        f.append(line(gx0 - 4, yy, gx0, yy, color=MUTED, sw=1))
        f.append(text(gx0 - 10, yy + 3, '%.1f' % vy, 10, MUTED, 'end'))

    def map_xy(x_val, y_val):
        return (gx0 + (x_val / 0.8) * (gw - 30), gy0 - (y_val / 0.9) * (gh - 30))

    # Spectral locus outline
    raw_locus = [
        (0.174, 0.005), (0.144, 0.030), (0.091, 0.133), (0.008, 0.538),
        (0.074, 0.834), (0.229, 0.754), (0.357, 0.636), (0.444, 0.555),
        (0.528, 0.470), (0.627, 0.372), (0.735, 0.265)
    ]
    pts = [map_xy(xv, yv) for xv, yv in raw_locus]
    path_d = ["M %.1f %.1f" % pts[0]]
    for px_i, py_i in pts[1:]:
        path_d.append("L %.1f %.1f" % (px_i, py_i))
    path_d.append("Z")

    f.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="1.8"/>' % (" ".join(path_d), MUTED))

    # Planckian locus coordinates: (T, x, y)
    planck_pts = [
        (1500, 0.586, 0.392),
        (2000, 0.527, 0.413),
        (2700, 0.458, 0.410),
        (3500, 0.405, 0.391),
        (5000, 0.345, 0.355),
        (6500, 0.313, 0.329),
        (10000, 0.281, 0.288),
        (20000, 0.262, 0.266)
    ]
    mapped_planck = [map_xy(xv, yv) for _, xv, yv in planck_pts]

    # Draw Planckian curve
    d_planck = ["M %.1f %.1f" % mapped_planck[0]]
    for px_i, py_i in mapped_planck[1:]:
        d_planck.append("L %.1f %.1f" % (px_i, py_i))
    f.append('<path d="%s" fill="none" stroke="#d97706" stroke-width="3"/>' % " ".join(d_planck))

    # Temperature points & isotemperature lines
    for T, xv, yv in planck_pts:
        px_i, py_i = map_xy(xv, yv)
        f.append(circle(px_i, py_i, 3.5, fill='#d97706', stroke='#ffffff', sw=1))
        if T in [2000, 2700, 4000, 6500, 10000]:
            f.append(line(px_i - 12, py_i - 18, px_i + 12, py_i + 18, color='#94a3b8', sw=1.2, dash='2,2'))

    # Annotate specific temperatures
    t_labels = [
        (1500, '1500 K', 'start', 10, -5),
        (2700, '2700 K (Тепле світло)', 'start', 15, -10),
        (5000, '5000 K', 'start', 15, -5),
        (6500, '6500 K', 'start', 15, 5),
        (10000, '10000 K', 'end', -15, -10)
    ]
    for T, label, align, dx, dy in t_labels:
        for t_val, xv, yv in planck_pts:
            if t_val == T:
                px_i, py_i = map_xy(xv, yv)
                f.append(text(px_i + dx, py_i + dy, label, 11, INK, align, bold=True))

    # Illuminants: Standard Illuminant A (2856K), D65 (6504K), E (equal energy)
    p_A = map_xy(0.4476, 0.4074)
    p_D65 = map_xy(0.3127, 0.3290)
    p_E = map_xy(0.3333, 0.3333)

    f.append(circle(p_A[0], p_A[1], 4, fill='#ef4444', stroke='#ffffff', sw=1))
    f.append(text(p_A[0] + 12, p_A[1] + 15, 'A (2856 K)', 11, '#ef4444', 'start'))

    f.append(circle(p_D65[0], p_D65[1], 4, fill='#0284c7', stroke='#ffffff', sw=1))
    f.append(text(p_D65[0] - 15, p_D65[1] - 15, 'D65 (6504 K)', 11, '#0284c7', 'end'))

    f.append(circle(p_E[0], p_E[1], 4, fill='#6b7280', stroke='#ffffff', sw=1))
    f.append(text(p_E[0] + 10, p_E[1] - 5, 'E (1/3, 1/3)', 10, '#6b7280', 'start', italic=True))

    # Legend / Title box inside diagram
    lx, ly = gx0 + 320, gy0 - gh + 30
    f.append(rect(lx, ly, 230, 85, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    f.append(line(lx + 15, ly + 22, lx + 45, ly + 22, color='#d97706', sw=3))
    f.append(text(lx + 55, ly + 26, 'Лінія чорного тіла (Planck)', 11, INK, 'start', bold=True))
    f.append(line(lx + 15, ly + 47, lx + 45, ly + 47, color='#94a3b8', sw=1.5, dash='2,2'))
    f.append(text(lx + 55, ly + 51, 'Ізотемпературні лінії CCT', 11, INK, 'start'))
    f.append(circle(lx + 30, ly + 68, 4, fill='#0284c7', stroke='#ffffff', sw=1))
    f.append(text(lx + 55, ly + 72, 'Стандартні ілюмінанти', 11, INK, 'start'))

    render(os.path.join(IMG, 'planckian-locus.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Алгоритм обчислення індексу кольоропередачі CRI (Ra)
# ═══════════════════════════════════════════════════════════════════════════
def fig_cri_calculation():
    W, H = 720, 440
    f = []
    f.append(text(W / 2, 26, 'Механізм вимірювання та обчислення індексу кольоропередачі CRI (R_a)',
                  16, INK, 'middle', bold=True))

    b1 = fitbox(40, 60, 200, 75, 'Випробовуване джерело\nS(λ) [напр. LED]', fill='#e0f2fe', stroke='#0284c7', text_size=12, text_color='#0369a1', bold=True)
    b2 = fitbox(480, 60, 200, 75, 'Еталонне джерело S_r(λ)\n[Планк або D65, CCT]', fill='#fef3c7', stroke='#d97706', text_size=12, text_color='#b45309', bold=True)

    for el in b1 + b2:
        f.append(el)

    b_tcs = fitbox(250, 155, 220, 65, '8 еталонних зразків\nвідбиття ρ_i(λ) (TCS01..08)', fill='#f1f5f9', stroke='#64748b', text_size=12, text_color='#334155', bold=True)
    for el in b_tcs:
        f.append(el)

    f.append(arrow(140, 135, 300, 155, color='#0284c7', sw=1.8))
    f.append(arrow(580, 135, 420, 155, color='#d97706', sw=1.8))

    b_uc1 = fitbox(40, 240, 280, 70, 'Відбитий спектр S_i(λ) = S(λ)·ρ_i(λ)\nОбчислення U*_i, V*_i, W*_i', fill='#e0f2fe', stroke='#0284c7', text_size=11, text_color='#0369a1')
    b_uc2 = fitbox(400, 240, 280, 70, 'Еталонний відбитий спектр\nОбчислення U*_ri, V*_ri, W*_ri', fill='#fef3c7', stroke='#d97706', text_size=11, text_color='#b45309')

    for el in b_uc1 + b_uc2:
        f.append(el)

    f.append(arrow(310, 220, 180, 240, color='#64748b', sw=1.5))
    f.append(arrow(410, 220, 540, 240, color='#64748b', sw=1.5))

    b_diff = fitbox(160, 335, 400, 80, 'Колірне зсунення ΔE_i = √[(ΔU*)^2 + (ΔV*)^2 + (ΔW*)^2]\nОкремі індекси: R_i = 100 - 4.6 · ΔE_i\nЗагальний індекс: R_a = (1/8) ∑ R_i  [i=1..8]', fill='#f0fdf4', stroke='#16a34a', text_size=11, text_color='#15803d', bold=True)

    for el in b_diff:
        f.append(el)

    f.append(arrow(180, 310, 280, 335, color='#0284c7', sw=1.8))
    f.append(arrow(540, 310, 440, 335, color='#d97706', sw=1.8))

    render(os.path.join(IMG, 'cri-calculation.svg'), W, H, *f)

if __name__ == '__main__':
    fig_cie1931_cmf()
    fig_planckian_locus()
    fig_cri_calculation()
    print("Figures generated successfully.")
