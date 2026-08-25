# -*- coding: utf-8 -*-
"""Фігури до теми «Антиферомагнетизм і феримагнетизм».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Спінові структури підґраток ─────────────────────────────────────
def fig_spin_sublattices_afm_ferri():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 28, "Порівняння спінових структур магнітного впорядкування", size=16, bold=True, color=INK))

    panel_w = 175
    panel_h = 280
    y_top = 55

    panels = [
        ("Феромагнетизм", "Паралельні спіни\n(M > 0)", "#eff6ff", "#1d4ed8", "fm"),
        ("Антиферомагнетизм", "Скомпенсовані\nпідґратки (M = 0)", "#f0fdf4", "#15803d", "afm"),
        ("Феримагнетизм", "Нескомпенсовані\nпідґратки (M > 0)", "#fff7ed", "#c2410c", "ferri"),
        ("Слабкий FM", "Скіс спінів\nDzyaloshinskii (m > 0)", "#faf5ff", "#7e22ce", "canted")
    ]

    for idx, (title_str, sub_str, bg_color, main_color, stype) in enumerate(panels):
        x0 = 20 + idx * 190
        f.append(rect(x0, y_top, panel_w, panel_h, fill=bg_color, stroke=BORDER, rx=6))
        f.append(text(x0 + panel_w / 2, y_top + 22, title_str, size=13, bold=True, color=main_color))
        
        # Grid of atoms
        grid_y0 = y_top + 60
        rows, cols = 4, 3
        dx = 45
        dy = 45
        start_x = x0 + 43
        start_y = grid_y0 + 20

        for r in range(rows):
            for c in range(cols):
                cx = start_x + c * dx
                cy = start_y + r * dy
                is_sub_a = ((r + c) % 2 == 0)
                
                # Atom circle
                atom_color = main_color if is_sub_a else "#64748b"
                f.append(circle(cx, cy, 7, fill=atom_color, stroke="none"))

                # Spin arrow
                if stype == "fm":
                    # All up
                    f.append(arrow(cx, cy + 12, cx, cy - 16, color="#1d4ed8", sw=2.5))
                elif stype == "afm":
                    # Sub A up, Sub B down
                    if is_sub_a:
                        f.append(arrow(cx, cy + 12, cx, cy - 16, color="#15803d", sw=2.5))
                    else:
                        f.append(arrow(cx, cy - 12, cx, cy + 16, color="#047857", sw=2.5))
                elif stype == "ferri":
                    # Sub A up (big), Sub B down (small)
                    if is_sub_a:
                        f.append(arrow(cx, cy + 14, cx, cy - 18, color="#c2410c", sw=3.0))
                    else:
                        f.append(arrow(cx, cy - 8, cx, cy + 10, color="#ea580c", sw=2.0))
                elif stype == "canted":
                    # Sub A slightly left-up, Sub B slightly right-up
                    if is_sub_a:
                        f.append(arrow(cx + 8, cy + 12, cx - 6, cy - 14, color="#7e22ce", sw=2.2))
                    else:
                        f.append(arrow(cx - 8, cy + 12, cx + 6, cy - 14, color="#a855f7", sw=2.2))

        # Subtext explanation
        sub_lines = sub_str.split("\n")
        for l_idx, line in enumerate(sub_lines):
            f.append(text(x0 + panel_w / 2, y_top + panel_h - 35 + l_idx * 16, line, size=11, bold=True, color=INK))

    f.append(text(W / 2, H - 15, "Атомні спінові підґратки визначають результуючий макроскопічний магнітний момент кристала", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-sublattices-afm-ferri.svg'), W, H, "\n".join(f))

# ── Фігура 2: Температурна залежність сприйнятливості ─────────────────────────
def fig_susceptibility_temp_neel():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Залежність магнітної сприйнятливості (χ) від температури (T)", size=16, bold=True, color=INK))

    x_zero = 90
    x_tn = 380
    x_max = 700
    y_top = 60
    y_bot = 360

    f.append(rect(x_zero, y_top, x_tn - x_zero, y_bot - y_top, fill="#f0fdf4", stroke="none", rx=0))
    f.append(rect(x_tn, y_top, x_max - x_tn, y_bot - y_top, fill="#f8fafc", stroke="none", rx=0))

    f.append(path_svg(f"M {x_tn} {y_top} L {x_tn} {y_bot}", stroke="#16a34a", sw=2, dash="4,4"))
    f.append(text(x_tn, y_top + 16, "T = T_N", size=13, bold=True, color="#16a34a"))

    f.append(text((x_zero + x_tn) / 2, y_top + 18, "Антиферомагнітний порядок", size=12, bold=True, color="#15803d"))
    f.append(text((x_tn + x_max) / 2, y_top + 18, "Парамагнітна фаза", size=12, bold=True, color="#475569"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 25, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 35, y_bot + 4, "T", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 20, y_top - 10, "χ", size=14, bold=True, italic=True, color=INK))

    f.append(text(x_zero, y_bot + 18, "0 K", size=11, color=MUTED))
    f.append(text(x_tn, y_bot + 18, "T_N", size=12, bold=True, color="#16a34a"))

    # Extrapolated asymptote -theta_p
    x_theta = 230
    f.append(path_svg(f"M {x_theta} {y_bot} L {x_tn} 130", stroke="#dc2626", sw=1.5, dash="3,3"))
    f.append(circle(x_theta, y_bot, 4, fill="#dc2626", stroke="none"))
    f.append(text(x_theta, y_bot + 18, "-θ_p", size=12, bold=True, color="#dc2626"))

    # Paramagnetic chi curve above T_N
    pts_pm = []
    y_tn_peak = 130
    for i in range(101):
        t_ratio = i / 100.0
        x = x_tn + t_ratio * (x_max - x_tn)
        val = 1.0 / (1.0 + t_ratio * 1.5)
        y = y_bot - val * (y_bot - y_tn_peak)
        pts_pm.append((x, y))

    d_pm = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_pm)
    f.append(path_svg(d_pm, stroke="#2563eb", sw=3))
    f.append(text(x_tn + 130, y_top + 100, "χ = C / (T + θ_p)", size=12, bold=True, color="#2563eb"))

    # Below T_N: chi_perp (constant)
    f.append(path_svg(f"M {x_zero} {y_tn_peak} L {x_tn} {y_tn_peak}", stroke="#16a34a", sw=2.5))
    f.append(text(x_zero + 110, y_tn_peak - 12, "χ_perp = const = 1 / λ", size=11, bold=True, color="#16a34a"))

    # Below T_N: chi_parallel (goes to zero at 0 K)
    pts_par = []
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tn - x_zero)
        val = (t_ratio**2.0)
        y = y_bot - val * (y_bot - y_tn_peak)
        pts_par.append((x, y))

    d_par = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_par)
    f.append(path_svg(d_par, stroke="#059669", sw=2.5, dash="6,3"))
    f.append(text(x_zero + 140, y_bot - 45, "χ_parallel → 0", size=11, bold=True, color="#059669"))

    # Below T_N: chi_poly (2/3 at 0 K)
    y_23 = y_bot - (2.0 / 3.0) * (y_bot - y_tn_peak)
    pts_poly = []
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tn - x_zero)
        val_par = (t_ratio**2.0)
        val_poly = (2.0 / 3.0) + (1.0 / 3.0) * val_par
        y = y_bot - val_poly * (y_bot - y_tn_peak)
        pts_poly.append((x, y))

    d_poly = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_poly)
    f.append(path_svg(d_poly, stroke="#9333ea", sw=2))
    f.append(text(x_zero - 35, y_23, "(2/3)χ_perp", size=10, bold=True, color="#9333ea"))
    f.append(text(x_zero + 70, y_23 - 15, "χ_poly (полікристал)", size=11, bold=True, color="#9333ea"))

    f.append(text(W / 2, H - 12, "Максимум сприйнятливості при T_N та непряма лінія асимптоти визначають від'ємний обмінний інтеграл", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'susceptibility-temp-neel.svg'), W, H, "\n".join(f))

# ── Фігура 3: Спін-флоп та спін-фліп переходи ─────────────────────────────────
def fig_spin_flop_spin_flip():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 26, "Фазові переходи спін-флоп та спін-фліп у зовнішньому полі (H)", size=16, bold=True, color=INK))

    p_w = 230
    p_h = 270
    y0 = 55

    phases = [
        ("Спін-антипаралельна", "H < H_sf", "Спіни уздовж осі легкого\nнамагнічування (↑ ↓)", "#f8fafc", "#475569", "collinear"),
        ("Спін-флоп фаза", "H_sf < H < H_flip", "Спіни повертаються ⊥ H\nі згортаються кутом", "#eff6ff", "#1d4ed8", "spin_flop"),
        ("Спін-фліп фаза", "H > H_flip", "Всі спіни примусово\nпаралельні полю (↑ ↑)", "#f0fdf4", "#15803d", "spin_flip")
    ]

    for idx, (title, cond, desc, bg, main_c, ptype) in enumerate(phases):
        x = 20 + idx * 250
        f.append(rect(x, y0, p_w, p_h, fill=bg, stroke=BORDER, rx=6))
        f.append(text(x + p_w / 2, y0 + 22, title, size=14, bold=True, color=main_c))
        f.append(text(x + p_w / 2, y0 + 42, cond, size=12, bold=True, color=MUTED))

        # Field Arrow on top
        f.append(arrow(x + p_w / 2, y0 + 100, x + p_w / 2, y0 + 60, color="#dc2626", sw=3.0))
        f.append(text(x + p_w / 2 + 18, y0 + 80, "H", size=13, bold=True, italic=True, color="#dc2626"))

        # Center spin vectors
        cx = x + p_w / 2
        cy = y0 + 160

        f.append(circle(cx, cy, 8, fill=main_c, stroke="none"))

        if ptype == "collinear":
            f.append(arrow(cx - 20, cy + 30, cx - 20, cy - 35, color="#1e40af", sw=3.0))
            f.append(text(cx - 35, cy, "M_A", size=11, bold=True, color="#1e40af"))
            f.append(arrow(cx + 20, cy - 30, cx + 20, cy + 35, color="#047857", sw=3.0))
            f.append(text(cx + 35, cy, "M_B", size=11, bold=True, color="#047857"))
        elif ptype == "spin_flop":
            # Flop perpendicular to field, canted upwards
            f.append(arrow(cx, cy, cx - 45, cy - 25, color="#1e40af", sw=3.0))
            f.append(text(cx - 50, cy - 30, "M_A", size=11, bold=True, color="#1e40af"))
            f.append(arrow(cx, cy, cx + 45, cy - 25, color="#047857", sw=3.0))
            f.append(text(cx + 50, cy - 30, "M_B", size=11, bold=True, color="#047857"))
            # Angle arc
            f.append(path_svg(f"M {cx - 25} {cy - 14} Q {cx} {cy - 28} {cx + 25} {cy - 14}", stroke="#9333ea", sw=1.5, dash="2,2"))
        elif ptype == "spin_flip":
            f.append(arrow(cx - 15, cy + 25, cx - 15, cy - 35, color="#1e40af", sw=3.0))
            f.append(text(cx - 30, cy, "M_A", size=11, bold=True, color="#1e40af"))
            f.append(arrow(cx + 15, cy + 25, cx + 15, cy - 35, color="#047857", sw=3.0))
            f.append(text(cx + 30, cy, "M_B", size=11, bold=True, color="#047857"))

        # Desc text
        lines = desc.split("\n")
        for l_idx, line in enumerate(lines):
            f.append(text(x + p_w / 2, y0 + p_h - 35 + l_idx * 16, line, size=11, color=INK))

    f.append(text(W / 2, H - 15, "При досягненні поля H_sf спінові вектори скачкоподібно розвертаються перпендикулярно до осі поля", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-flop-spin-flip.svg'), W, H, "\n".join(f))

# ── Фігура 4: Температурна компенсація у феримагнетиках ───────────────────────
def fig_ferrimagnet_compensation_temp():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Температурна компенсація намагніченості у феримагнетиках", size=16, bold=True, color=INK))

    x_zero = 80
    x_comp = 350
    x_tn = 620
    x_max = 710
    y_top = 60
    y_bot = 360

    f.append(rect(x_zero, y_top, x_tn - x_zero, y_bot - y_top, fill="#fff7ed", stroke="none", rx=0))
    f.append(path_svg(f"M {x_comp} {y_top} L {x_comp} {y_bot}", stroke="#9333ea", sw=1.8, dash="4,4"))
    f.append(text(x_comp, y_top + 16, "T = T_comp", size=12, bold=True, color="#9333ea"))

    f.append(path_svg(f"M {x_tn} {y_top} L {x_tn} {y_bot}", stroke="#dc2626", sw=1.8, dash="4,4"))
    f.append(text(x_tn, y_top + 16, "T = T_N", size=12, bold=True, color="#dc2626"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 20, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 30, y_bot + 4, "T", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 10, "M(T)", size=13, bold=True, color=INK))

    f.append(text(x_zero, y_bot + 18, "0 K", size=11, color=MUTED))
    f.append(text(x_comp, y_bot + 18, "T_comp", size=12, bold=True, color="#9333ea"))
    f.append(text(x_tn, y_bot + 18, "T_N", size=12, bold=True, color="#dc2626"))

    # Curve M_A (starts higher, drops faster)
    pts_a = []
    y_a0 = 100
    for i in range(101):
        t = i / 100.0
        x = x_zero + t * (x_tn - x_zero)
        val = (1.0 - t**1.2)**0.6
        y = y_bot - val * (y_bot - y_a0)
        pts_a.append((x, y))

    d_a = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_a)
    f.append(path_svg(d_a, stroke="#1d4ed8", sw=2.5))
    f.append(text(x_zero + 40, y_a0 - 10, "|M_A(T)|", size=12, bold=True, color="#1d4ed8"))

    # Curve M_B (starts lower, drops slower)
    pts_b = []
    y_b0 = 160
    for i in range(101):
        t = i / 100.0
        x = x_zero + t * (x_tn - x_zero)
        val = (1.0 - t**3.0)**0.3
        y = y_bot - val * (y_bot - y_b0)
        pts_b.append((x, y))

    d_b = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_b)
    f.append(path_svg(d_b, stroke="#ea580c", sw=2.5))
    f.append(text(x_zero + 40, y_b0 + 20, "|M_B(T)|", size=12, bold=True, color="#ea580c"))

    # Net magnetization M_net = |M_A - M_B|
    pts_net = []
    for i in range(101):
        t = i / 100.0
        x = x_zero + t * (x_tn - x_zero)
        val_a = (1.0 - t**1.2)**0.6 * (y_bot - y_a0)
        val_b = (1.0 - t**3.0)**0.3 * (y_bot - y_b0)
        val_net = abs(val_a - val_b)
        y = y_bot - val_net
        pts_net.append((x, y))

    d_net = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_net)
    f.append(path_svg(d_net, stroke="#059669", sw=3.0, dash="5,3"))
    f.append(text(x_zero + 130, y_bot - 80, "M_net = |M_A - M_B|", size=12, bold=True, color="#059669"))

    f.append(circle(x_comp, y_bot, 5, fill="#9333ea", stroke="none"))
    f.append(text(x_comp + 15, y_bot - 15, "M_net = 0 у точці компенсації", size=11, bold=True, color="#9333ea"))

    f.append(text(W / 2, H - 12, "Різна швидкість спадання намагніченості підґраток призводить до обнулення M_net при T_comp", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'ferrimagnet-compensation-temp.svg'), W, H, "\n".join(f))

def main():
    fig_spin_sublattices_afm_ferri()
    fig_susceptibility_temp_neel()
    fig_spin_flop_spin_flip()
    fig_ferrimagnet_compensation_temp()
    print("All figures successfully generated in ./img/")

if __name__ == '__main__':
    main()
