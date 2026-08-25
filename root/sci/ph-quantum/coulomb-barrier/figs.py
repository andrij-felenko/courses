# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def fig_coulomb_potential():
    w, h = 820, 500
    frags = []

    # Background card
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))

    # Title
    frags.append(text(w / 2, 40, "Потенціальний бар'єр ядра та тунелювання частинки", size=18, bold=True, color=INK))

    # Axes layout
    x0, y0 = 100, 380  # Origin (r=0, V=0)
    x_max = 750
    y_top = 80
    y_well = 450       # V0 level

    # Draw axes
    frags.append(arrow(x0, y0, x_max, y0, color=LINE, sw=1.5))  # r axis
    frags.append(text(x_max - 15, y0 + 25, "Відстань r (фм)", size=13, bold=True, color=INK))

    frags.append(arrow(x0, y_well + 20, x0, y_top - 20, color=LINE, sw=1.5))  # V axis
    frags.append(text(x0 - 45, y_top - 10, "Потенціальна енергія V(r) (МеВ)", size=12, bold=True, color=INK, anchor="end"))

    # Zero level reference line
    frags.append(line(x0 - 10, y0, x_max, y0, color="#9ca3af", sw=1, dash="4 4"))
    frags.append(text(x0 - 15, y0 + 4, "0", size=12, color=MUTED, anchor="end"))

    # Key parameters
    r_R = 240          # Nuclear radius R pixel position
    V_peak = 110       # Peak of Coulomb barrier (V_B)
    r_rc = 520         # Classical turning point r_c
    y_E = 240          # Particle energy E level

    # 1. Shaded classically forbidden area (tunneling zone)
    # Polygon for region under Coulomb curve between R and r_c down to y_E
    shade_pts = []
    steps = 40
    for i in range(steps + 1):
        rx = r_R + (r_rc - r_R) * i / steps
        vy = V_peak + (y_E - V_peak) * (i / steps) ** 0.85
        shade_pts.append((rx, vy))
    shade_pts.append((r_rc, y_E))
    shade_pts.append((r_R, y_E))

    shade_svg_pts = " ".join([f"{px:.1f},{py:.1f}" for px, py in shade_pts])
    frags.append(f'<polygon points="{shade_svg_pts}" fill="#fee2e2" opacity="0.6"/>')

    # 2. Draw Nuclear Potential Well (r < R)
    frags.append(line(x0, y_well, r_R, y_well, color="#1e40af", sw=2.5))
    frags.append(line(r_R, y_well, r_R, V_peak, color="#1e40af", sw=2.5))

    # Well depth label
    frags.append(text(x0 - 15, y_well + 4, "-V₀ (-40 МеВ)", size=11, color="#1e40af", anchor="end"))
    frags.append(line(x0 - 8, y_well, x0, y_well, color="#1e40af", sw=1))

    # 3. Draw Coulomb Potential Tail (r >= R)
    coulomb_pts = []
    coulomb_pts.append((r_R, V_peak))
    for i in range(1, 60):
        rx = r_R + (x_max - 50 - r_R) * i / 50
        r_ratio = (r_R - x0) / (rx - x0)
        vy = y0 - (y0 - V_peak) * r_ratio
        coulomb_pts.append((rx, vy))

    coul_svg_pts = " ".join([f"{px:.1f},{py:.1f}" for px, py in coulomb_pts])
    frags.append(f'<polyline points="{coul_svg_pts}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Peak V_B label
    frags.append(circle(r_R, V_peak, 4, fill=POS, stroke=POS))
    frags.append(text(x0 - 15, V_peak + 4, "V_B (Бар'єр)", size=12, bold=True, color=POS, anchor="end"))
    frags.append(line(x0 - 8, V_peak, r_R, V_peak, color=POS, sw=1, dash="2 2"))

    # 4. Particle Energy Level E
    frags.append(line(x0, y_E, x_max - 50, y_E, color="#059669", sw=2.0, dash="6 4"))
    frags.append(text(x0 - 15, y_E + 4, "Енергія E", size=12, bold=True, color="#059669", anchor="end"))

    # Turning points vertical dashed lines
    frags.append(line(r_R, V_peak, r_R, y0 + 35, color="#1e40af", sw=1.2, dash="3 3"))
    frags.append(text(r_R, y0 + 50, "r = R", size=12, bold=True, color="#1e40af"))
    frags.append(text(r_R, y0 + 66, "(Радіус ядра)", size=10, color=MUTED))

    frags.append(line(r_rc, y_E, r_rc, y0 + 35, color=POS, sw=1.2, dash="3 3"))
    frags.append(text(r_rc, y0 + 50, "r = r_c", size=12, bold=True, color=POS))
    frags.append(text(r_rc, y0 + 66, "(Точка повороту)", size=10, color=MUTED))

    # Barrier width double arrow
    frags.append(arrow(r_R, y_E - 30, r_rc, y_E - 30, color=POS, sw=1.5))
    frags.append(arrow(r_rc, y_E - 30, r_R, y_E - 30, color=POS, sw=1.5))
    frags.append(textbox((r_R + r_rc) / 2, y_E - 55, "Ширина b = r_c - R", size=11, bold=True, fill="#fff1f2", stroke=POS, pad=6)[0])

    # 5. Quantum Wavefunction Psi(r)
    psi_pts = []
    for rx in range(x0, r_R):
        vy = y_E - 22 * math.sin((rx - x0) * 0.15)
        psi_pts.append((rx, vy))

    for rx in range(r_R, r_rc):
        t = (rx - r_R) / (r_rc - r_R)
        decay = math.exp(-3.0 * t)
        vy = y_E - 22 * decay * math.cos(t * math.pi * 0.5)
        psi_pts.append((rx, vy))

    trans_amp = 22 * math.exp(-3.0)
    for rx in range(r_rc, x_max - 50):
        vy = y_E - trans_amp * math.cos((rx - r_rc) * 0.12)
        psi_pts.append((rx, vy))

    psi_svg_pts = " ".join([f"{px:.1f},{py:.1f}" for px, py in psi_pts])
    frags.append(f'<polyline points="{psi_svg_pts}" fill="none" stroke="#7c3aed" stroke-width="2.2"/>')

    # Wavefunction label
    frags.append(fitbox(x0 + 60, y_E - 35, 110, 24, "Хвильова функція ψ(r)", size=10, fill="#f3e8ff", stroke="#7c3aed"))
    frags.append(fitbox(r_rc + 70, y_E - 35, 110, 24, "Протунельована хвиля", size=10, fill="#f3e8ff", stroke="#7c3aed"))

    # Annotation box for tunneling probability P(E)
    frags.append(textbox(570, 130, "Прозорість бар'єра (ВКБ):\nP(E) ≈ exp(-2G)\n\nФактор Ґамова G ∝ Z₁Z₂ / √E", size=11, bold=False, fill="#ffffff", stroke="#94a3b8", pad=8)[0])

    return render(os.path.join(make_img_dir(), "coulomb-potential-barrier.svg"), w, h, *frags)


def fig_gamow_peak():
    w, h = 820, 480
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w / 2, 40, "Гамовський пік термоядерного синтезу в зорях", size=18, bold=True, color=INK))

    x0, y0 = 90, 390
    x_max = 760
    y_top = 90

    # Axes
    frags.append(arrow(x0, y0, x_max, y0, color=LINE, sw=1.5))
    frags.append(text(x_max - 20, y0 + 25, "Кінетична енергія E", size=13, bold=True, color=INK))

    frags.append(arrow(x0, y0, x0, y_top, color=LINE, sw=1.5))
    frags.append(text(x0 - 15, y_top - 15, "Імовірність / Функція розподілу", size=12, bold=True, color=INK, anchor="end"))

    # Curves calculation
    num_pts = 100
    mb_pts = []
    p_pts = []
    gp_pts = []

    for i in range(1, num_pts):
        e_val = i * 10.0 / num_pts
        x_px = x0 + (x_max - 50 - x0) * (e_val / 10.0)

        mb_val = 3.5 * e_val * math.exp(-0.75 * e_val)
        y_mb = y0 - mb_val * 65.0
        mb_pts.append((x_px, max(y_top + 10, y_mb)))

        p_val = 0.005 * math.exp(0.72 * e_val)
        y_p = y0 - min(p_val, 4.2) * 65.0
        p_pts.append((x_px, max(y_top + 10, y_p)))

        gp_val = mb_val * p_val * 0.95
        y_gp = y0 - gp_val * 140.0
        gp_pts.append((x_px, max(y_top + 10, y_gp)))

    # Draw curves
    mb_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in mb_pts])
    frags.append(f'<polyline points="{mb_svg}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    p_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in p_pts])
    frags.append(f'<polyline points="{p_svg}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Shade Gamow peak area
    E0_x = x0 + (x_max - 50 - x0) * (4.4 / 10.0)
    E0_y_peak = y0 - (3.5 * 4.4 * math.exp(-0.75 * 4.4)) * (0.005 * math.exp(0.72 * 4.4)) * 0.95 * 140.0

    gp_shade = [(x0 + (x_max - 50 - x0) * (e * 10.0 / num_pts / 10.0), py) for e, (px, py) in enumerate(gp_pts)]
    gp_shade.append((gp_pts[-1][0], y0))
    gp_shade.insert(0, (gp_pts[0][0], y0))
    gp_shade_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in gp_shade])
    frags.append(f'<polygon points="{gp_shade_svg}" fill="#dcfce7" opacity="0.8"/>')

    gp_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in gp_pts])
    frags.append(f'<polyline points="{gp_svg}" fill="none" stroke="{FIELD}" stroke-width="3.0"/>')

    # Gamow Peak Center E0
    frags.append(line(E0_x, y0, E0_x, E0_y_peak, color=FIELD, sw=1.8, dash="4 4"))
    frags.append(circle(E0_x, E0_y_peak, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(text(E0_x, y0 + 22, "E₀ (Пік Ґамова)", size=12, bold=True, color=FIELD))

    # Thermal energy kT reference
    kT_x = x0 + (x_max - 50 - x0) * (1.33 / 10.0)
    frags.append(line(kT_x, y0, kT_x, y0 - 150, color=NEG, sw=1.2, dash="3 3"))
    frags.append(text(kT_x, y0 + 22, "k_B T (~1 кЕв)", size=11, bold=True, color=NEG))

    # Effective width delta E
    w_left = E0_x - 45
    w_right = E0_x + 45
    y_w = E0_y_peak + 50
    frags.append(arrow(w_left, y_w, w_right, y_w, color=FIELD, sw=1.5))
    frags.append(arrow(w_right, y_w, w_left, y_w, color=FIELD, sw=1.5))
    frags.append(fitbox(E0_x - 50, y_w + 8, 100, 22, "Вікно ΔE", size=10, fill="#f0fdf4", stroke=FIELD))

    # Legend textboxes
    frags.append(textbox(240, 140, "Розподіл Максвелла-Больцмана\nf(E) ∝ E · exp(-E / k_B T)", size=11, bold=False, fill="#eff6ff", stroke=NEG)[0])
    frags.append(textbox(640, 140, "Прозорість бар'єра\nP(E) ∝ exp(-b / √E)", size=11, bold=False, fill="#fff1f2", stroke=POS)[0])
    frags.append(textbox(E0_x, E0_y_peak - 35, "Гамовський пік I(E) = f(E) · P(E)\nВузьке вікно термоядерних реакцій", size=11, bold=True, fill="#f0fdf4", stroke=FIELD)[0])

    return render(os.path.join(make_img_dir(), "gamow-peak.svg"), w, h, *frags)


def fig_geiger_nuttall():
    w, h = 820, 480
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w / 2, 40, "Закон Ґейґера — Неттолла для альфа-розпаду", size=18, bold=True, color=INK))

    x0, y0 = 90, 400
    x_max = 760
    y_top = 80

    # Axes
    frags.append(arrow(x0, y0, x_max, y0, color=LINE, sw=1.5))
    frags.append(text(x_max - 20, y0 + 25, "1 / √E_α  (МеВ⁻¹/²)", size=13, bold=True, color=INK))

    frags.append(arrow(x0, y0, x0, y_top, color=LINE, sw=1.5))
    frags.append(text(x0 - 15, y_top - 15, "lg(T₁/₂ , с)", size=13, bold=True, color=INK, anchor="end"))

    # Y-axis ticks (log T1/2 from -8 to +18)
    y_ticks = [(-8, 380), (0, 310), (8, 230), (16, 150)]
    for val, py in y_ticks:
        frags.append(line(x0 - 5, py, x0, py, color=LINE, sw=1))
        frags.append(text(x0 - 12, py + 4, str(val), size=11, color=MUTED, anchor="end"))
        frags.append(line(x0, py, x_max - 40, py, color="#f1f5f9", sw=1))

    # X-axis ticks (1/sqrt(E) from 0.34 to 0.49)
    x_ticks = [(0.34, 140), (0.38, 290), (0.42, 440), (0.46, 590), (0.49, 700)]
    for val, px in x_ticks:
        frags.append(line(px, y0, px, y0 + 5, color=LINE, sw=1))
        frags.append(text(px, y0 + 20, f"{val:.2f}", size=11, color=MUTED))
        frags.append(line(px, y0, px, y_top + 10, color="#f1f5f9", sw=1))

    # Uranium series data
    u_chain = [
        ("²¹⁴Po (8.78 МеВ)", 0.337, -6.5),
        ("²¹⁸Po (6.00 МеВ)", 0.408, 2.2),
        ("²²²Rn (5.49 МеВ)", 0.426, 5.5),
        ("²²⁶Ra (4.78 МеВ)", 0.457, 10.7),
        ("²³⁸U (4.20 МеВ)", 0.488, 17.15)
    ]

    # Thorium series data
    th_chain = [
        ("²¹²Po (8.78 МеВ)", 0.337, -6.7),
        ("²²⁰Rn (6.29 МеВ)", 0.398, 1.7),
        ("²²⁴Ra (5.68 МеВ)", 0.419, 5.5),
        ("²²⁸Th (5.42 МеВ)", 0.429, 7.8),
        ("²³²Th (4.01 МеВ)", 0.499, 17.6)
    ]

    def map_xy(inv_sqrt_e, lg_t):
        px = x0 + (inv_sqrt_e - 0.32) * (x_max - 50 - x0) / (0.50 - 0.32)
        py = y0 - (lg_t - (-8)) * (y0 - y_top - 20) / (20 - (-8))
        return px, py

    u_pts = [map_xy(inv_e, lg_t) for _, inv_e, lg_t in u_chain]
    u_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in u_pts])
    frags.append(f'<polyline points="{u_svg}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    for label, inv_e, lg_t in u_chain:
        px, py = map_xy(inv_e, lg_t)
        frags.append(circle(px, py, 4.5, fill=POS, stroke=POS))
        frags.append(text(px + 10, py - 6, label, size=10, bold=True, color=POS, anchor="start"))

    th_pts = [map_xy(inv_e, lg_t) for _, inv_e, lg_t in th_chain]
    th_svg = " ".join([f"{px:.1f},{py:.1f}" for px, py in th_pts])
    frags.append(f'<polyline points="{th_svg}" fill="none" stroke="{NEG}" stroke-width="2.2" stroke-dasharray="6 4"/>')

    for label, inv_e, lg_t in th_chain:
        px, py = map_xy(inv_e, lg_t)
        frags.append(circle(px, py, 4, fill=NEG, stroke=NEG))

    frags.append(textbox(260, 120, "Емпіричний закон Ґейґера — Неттолла (1911):\nlg(T₁/₂) = A + B / √E_α\n\nҐамовська теорія (1928):\nКоефіцієнт B = π √2μ Z₁ Z₂ e² / ℏ\nПояснює зміну T₁/₂ на 24 порядки!", size=11, bold=False, fill="#ffffff", stroke="#94a3b8", pad=8)[0])
    frags.append(textbox(640, 340, "Ряди розпаду:\n— Ряд Урану-238 (Z=92)\n- - Ряд Торію-232 (Z=90)", size=10, fill="#f8fafc", stroke="#cbd5e1")[0])

    return render(os.path.join(make_img_dir(), "geiger-nuttall-law.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_coulomb_potential()
    fig_gamow_peak()
    fig_geiger_nuttall()
    print("Figures generated successfully!")
