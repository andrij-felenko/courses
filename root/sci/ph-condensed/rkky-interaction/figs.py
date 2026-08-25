# -*- coding: utf-8 -*-
"""Фігури до теми «Взаємодія Рудермана — Кіттеля — Касуї — Йосіди (РККЙ)».
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

# ── Фігура 1: Фізичний механізм РККЙ (спінова поляризація електронів провідності) ──
def fig_rkky_mechanism(path):
    W, H = 760, 360
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e2e8f0", rx=0))
    f.append(text(W / 2, 28, "Механізм опосередкованої обмінної взаємодії РККЙ", size=16, bold=True, color=INK))

    # Background metal conduction electron sea
    f.append(rect(30, 50, 700, 280, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(380, 75, "Море вільних електронів провідності (фермі-газ металу)", size=12, color=MUTED, italic=True))

    # Localized spin 1
    x1, y1 = 180, 180
    f.append(circle(x1, y1, 24, fill="#fee2e2", stroke=POS, sw=2))
    f.append(arrow(x1, y1 + 14, x1, y1 - 14, color=POS, sw=3))
    f.append(text(x1, y1 + 42, "Локалізований спін S₁", size=13, bold=True, color=POS))
    f.append(text(x1, y1 + 58, "(атом 4f/3d)", size=11, color=MUTED))

    # Localized spin 2
    x2, y2 = 580, 180
    f.append(circle(x2, y2, 24, fill="#dbeafe", stroke=NEG, sw=2))
    f.append(arrow(x2, y2 - 14, x2, y2 + 14, color=NEG, sw=3))
    f.append(text(x2, y2 + 42, "Локалізований спін S₂", size=13, bold=True, color=NEG))
    f.append(text(x2, y2 + 58, "(на відстані r)", size=11, color=MUTED))

    # Distance line r
    f.append(line(x1, y1 - 45, x2, y1 - 45, color=LINE, sw=1.5, dash="4,4"))
    f.append(arrow(x1 + 60, y1 - 45, x1, y1 - 45, color=LINE, sw=1.2))
    f.append(arrow(x2 - 60, y1 - 45, x2, y1 - 45, color=LINE, sw=1.2))
    f.append(text(380, y1 - 52, "Відстань між спінами r", size=12, bold=True, color=INK))

    # Friedel spin polarization wave around spin 1
    # Plot spin density polarization wave delta_rho_spin(x)
    path_pts = []
    num_pts = 200
    x_start = x1 + 25
    x_end = x2 - 25
    
    for i in range(num_pts + 1):
        t = i / float(num_pts)
        curr_x = x_start + t * (x_end - x_start)
        r_val = (curr_x - x1) * 0.05 + 0.5
        # Friedel oscillations proportional to cos(2*kF*r) / r^2 for visualization
        wave = math.cos(3.5 * math.pi * t * 4) * math.exp(-0.8 * t) * 45
        curr_y = y1 - wave
        path_pts.append((curr_x, curr_y))

    path_str = f"M {path_pts[0][0]:.1f},{path_pts[0][1]:.1f}"
    for px, py in path_pts[1:]:
        path_str += f" L {px:.1f},{py:.1f}"

    # Zero polarization reference line
    f.append(line(x_start, y1, x_end, y1, color="#94a3b8", sw=1, dash="2,2"))
    f.append(path_svg(path_str, fill="none", stroke="#0284c7", sw=2.2))
    f.append(text(380, 235, "Осцилююча спінова поляризація σ_spin(r)", size=12, bold=True, color="#0284c7"))

    # Labels for electron spin alignment
    f.append(arrow(260, 140, 260, 115, color=POS, sw=1.8))
    f.append(text(260, 107, "Спін ↑", size=11, color=POS))

    f.append(arrow(340, 205, 340, 230, color=NEG, sw=1.8))
    f.append(text(340, 245, "Спін ↓", size=11, color=NEG))

    f.append(arrow(430, 145, 430, 125, color=POS, sw=1.8))
    f.append(text(430, 117, "Спін ↑", size=11, color=POS))

    # Explanation box below
    f.append(rect(120, 285, 520, 38, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(380, 308, "Спін S₁ поляризує електрони провідності → хвиля спінової густини досягає S₂", size=12, color=INK))

    return render(path, W, H, *f)


# ── Фігура 2: Залежність обмінного інтеграла J_RKKY від відстані ──────────────
def fig_rkky_oscillations(path):
    W, H = 760, 380
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e2e8f0", rx=0))
    f.append(text(W / 2, 26, "Залежність обмінного інтеграла РККЙ J_RKKY(r) від відстані", size=16, bold=True, color=INK))

    x0, y0 = 80, 200
    plot_w, plot_h = 630, 260

    # Axes
    f.append(arrow(x0, y0, x0 + plot_w, y0, color=INK, sw=1.8))  # X axis
    f.append(arrow(x0, y0 + 110, x0, y0 - 120, color=INK, sw=1.8)) # Y axis

    f.append(text(x0 + plot_w - 20, y0 + 25, "x = 2 · k_F · r", size=13, bold=True, color=INK))
    f.append(text(x0 - 15, y0 - 110, "J_RKKY(r)", size=13, bold=True, color=INK))

    # Zero line
    f.append(line(x0, y0, x0 + plot_w - 30, y0, color="#94a3b8", sw=1))

    # Shaded FM and AFM regions
    # FM region 1 (x from 0 to pi)
    f.append(rect(x0, y0 - 90, 85, 90, fill="#fee2e2", stroke="none"))
    f.append(text(x0 + 42, y0 - 70, "Феромагнітна (FM)", size=11, bold=True, color=POS))
    f.append(text(x0 + 42, y0 - 55, "J > 0", size=11, color=POS))

    # AFM region 1 (x from pi to 2pi)
    f.append(rect(x0 + 85, y0, 85, 90, fill="#dbeafe", stroke="none"))
    f.append(text(x0 + 127, y0 + 65, "Антиферомагнітна (AFM)", size=11, bold=True, color=NEG))
    f.append(text(x0 + 127, y0 + 80, "J < 0", size=11, color=NEG))

    # Plot RKKY function: F(x) = (x*cos(x) - sin(x)) / x^4
    # Scaled for visualization
    num_pts = 300
    pts = []
    envelope_pos = []
    envelope_neg = []

    for i in range(num_pts):
        # x_val from 0.8 to 14.0
        x_val = 0.8 + (i / float(num_pts)) * 13.2
        # Function value
        fx = (x_val * math.cos(x_val) - math.sin(x_val)) / (x_val ** 3.2)
        # Scale for plot
        px = x0 + (x_val - 0.8) / 13.2 * (plot_w - 60)
        py = y0 - fx * 180.0

        pts.append((px, py))

        # Envelopes 1 / x^2.2
        env = 160.0 / (x_val ** 2.2)
        envelope_pos.append((px, y0 - env))
        envelope_neg.append((px, y0 + env))

    path_str = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
    for px, py in pts[1:]:
        path_str += f" L {px:.1f},{py:.1f}"

    env_p_str = f"M {envelope_pos[0][0]:.1f},{envelope_pos[0][1]:.1f}"
    for px, py in envelope_pos[1:]:
        env_p_str += f" L {px:.1f},{py:.1f}"

    env_n_str = f"M {envelope_neg[0][0]:.1f},{envelope_neg[0][1]:.1f}"
    for px, py in envelope_neg[1:]:
        env_n_str += f" L {px:.1f},{py:.1f}"

    # Envelope dashed lines
    f.append(path_svg(env_p_str, fill="none", stroke="#dc2626", sw=1.2, dash="3,3"))
    f.append(path_svg(env_n_str, fill="none", stroke="#dc2626", sw=1.2, dash="3,3"))
    f.append(text(x0 + plot_w - 120, y0 - 45, "Огинаюча ~ 1/r³", size=11, italic=True, color="#dc2626"))

    # RKKY curve
    f.append(path_svg(path_str, fill="none", stroke="#1e293b", sw=2.5))

    # Ticks and labels on x axis
    ticks = [
        (math.pi, "π"),
        (2 * math.pi, "2π"),
        (3 * math.pi, "3π"),
        (4 * math.pi, "4π")
    ]
    for x_rad, label_str in ticks:
        px = x0 + (x_rad - 0.8) / 13.2 * (plot_w - 60)
        f.append(line(px, y0 - 5, px, y0 + 5, color=INK, sw=1.5))
        f.append(text(px, y0 + 20, label_str, size=12, bold=True, color=INK))

    # Wavelength lambda_F / 2 label
    px1 = x0 + (math.pi - 0.8) / 13.2 * (plot_w - 60)
    px2 = x0 + (3 * math.pi - 0.8) / 13.2 * (plot_w - 60)
    f.append(line(px1, y0 + 35, px2, y0 + 35, color=FIELD, sw=1.5, dash="2,2"))
    f.append(arrow(px1 + 40, y0 + 35, px1, y0 + 35, color=FIELD, sw=1.2))
    f.append(arrow(px2 - 40, y0 + 35, px2, y0 + 35, color=FIELD, sw=1.2))
    f.append(text((px1 + px2) / 2, y0 + 48, "Період осциляцій λ = π / k_F", size=12, bold=True, color=FIELD))

    # Explanatory text box
    f.append(rect(100, 325, 560, 40, fill="#f8fafc", stroke=BORDER, rx=4))
    f.append(text(380, 348, "Знак взаємодії змінюється з ферро (J > 0) на антиферро (J < 0) залежно від відстані", size=12, color=INK))

    return render(path, W, H, *f)


# ── Фігура 3: Мультишари (GMR/SAF) та Спінове скло (Фрустрація) ───────────────
def fig_multilayer_gmr_spinglass(path):
    W, H = 760, 360
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e2e8f0", rx=0))
    f.append(text(W / 2, 26, "Застосування РККЙ: Міжшаровий зв'язок та спінові стекла", size=16, bold=True, color=INK))

    # Left panel: Magnetic multilayers (IEC in GMR/SAF)
    x_left = 30
    w_panel = 335
    f.append(rect(x_left, 50, w_panel, 290, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x_left + w_panel / 2, 73, "А: Міжшаровий зв'язок (IEC)", size=14, bold=True, color="#0f766e"))
    f.append(text(x_left + w_panel / 2, 90, "Мультишари FM / NM / FM", size=11, color=MUTED))

    # Multilayer diagram (FM1, NM spacer, FM2)
    y_m = 115
    # FM Layer 1
    f.append(rect(x_left + 40, y_m, 255, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    f.append(text(x_left + 70, y_m + 20, "Феромагнетик FM₁ (Co)", size=11, bold=True, color=POS))
    f.append(arrow(x_left + 220, y_m + 15, x_left + 260, y_m + 15, color=POS, sw=2.5))

    # Non-magnetic Spacer (Cu, Ru)
    f.append(rect(x_left + 40, y_m + 35, 255, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=3))
    f.append(text(x_left + 167, y_m + 55, "Немагнітний прошарок (Cu, Ru)", size=11, bold=True, color="#0369a1"))
    f.append(text(x_left + 167, y_m + 70, "Товщина d_NM (осциляції J_IEC)", size=10, italic=True, color="#0369a1"))

    # FM Layer 2
    f.append(rect(x_left + 40, y_m + 85, 255, 30, fill="#dbeafe", stroke=NEG, sw=1.5, rx=3))
    f.append(text(x_left + 70, y_m + 105, "Феромагнетик FM₂ (Co)", size=11, bold=True, color=NEG))
    f.append(arrow(x_left + 260, y_m + 100, x_left + 220, y_m + 100, color=NEG, sw=2.5))

    # State text below layers
    f.append(rect(x_left + 30, 245, 275, 75, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(x_left + 167, 265, "Антиферомагнітний стан (d = 0.9 нм)", size=11, bold=True, color=NEG))
    f.append(text(x_left + 167, 282, "Високий опір (стан GMR / SAF)", size=11, color=INK))
    f.append(text(x_left + 167, 305, "Феромагнітний стан (d = 1.8 нм) → низький опір", size=10, color=MUTED))


    # Right panel: Spin Glass & Magnetic Frustration
    x_right = 395
    f.append(rect(x_right, 50, w_panel, 290, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x_right + w_panel / 2, 73, "Б: Спінова фрустрація", size=14, bold=True, color="#b45309"))
    f.append(text(x_right + w_panel / 2, 90, "Розбавлені сплави (CuMn, AuFe)", size=11, color=MUTED))

    # Triangular spin triad showing frustration
    cx, cy = x_right + 167, 165
    r_tri = 55
    # Triangle vertices
    v1 = (cx, cy - r_tri)
    v2 = (cx - r_tri * 0.866, cy + r_tri * 0.5)
    v3 = (cx + r_tri * 0.866, cy + r_tri * 0.5)

    # Bonds between vertices
    # Bond 1-2: FM (J > 0)
    f.append(line(v1[0], v1[1], v2[0], v2[1], color=POS, sw=2.5))
    f.append(text((v1[0] + v2[0]) / 2 - 22, (v1[1] + v2[1]) / 2, "J > 0 (FM)", size=10, bold=True, color=POS))

    # Bond 1-3: AFM (J < 0)
    f.append(line(v1[0], v1[1], v3[0], v3[1], color=NEG, sw=2.5))
    f.append(text((v1[0] + v3[0]) / 2 + 22, (v1[1] + v3[1]) / 2, "J < 0 (AFM)", size=10, bold=True, color=NEG))

    # Bond 2-3: AFM (J < 0) -> Frustrated link!
    f.append(line(v2[0], v2[1], v3[0], v3[1], color="#7c3aed", sw=2.5, dash="4,3"))
    f.append(text(cx, v2[1] + 18, "Фрустрований зв'язок!", size=11, bold=True, color="#7c3aed"))

    # Spin nodes
    # Node 1: Spin UP
    f.append(circle(v1[0], v1[1], 16, fill="#fee2e2", stroke=POS, sw=2))
    f.append(arrow(v1[0], v1[1] + 10, v1[0], v1[1] - 10, color=POS, sw=2.2))

    # Node 2: Spin UP (satisfies FM bond with 1)
    f.append(circle(v2[0], v2[1], 16, fill="#fee2e2", stroke=POS, sw=2))
    f.append(arrow(v2[0], v2[1] + 10, v2[0], v2[1] - 10, color=POS, sw=2.2))

    # Node 3: Spin DOWN (satisfies AFM with 1, but violates AFM with 2!)
    f.append(circle(v3[0], v3[1], 16, fill="#dbeafe", stroke=NEG, sw=2))
    f.append(arrow(v3[0], v3[1] - 10, v3[0], v3[1] + 10, color=NEG, sw=2.2))

    # Spin glass state summary below
    f.append(rect(x_right + 30, 255, 275, 65, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(x_right + 167, 275, "Хаотично розташовані домішки", size=11, color=INK))
    f.append(text(x_right + 167, 295, "→ Неможливо задовольнити всі зв'язки", size=11, bold=True, color="#b45309"))

    return render(path, W, H, *f)


def main():
    figs = [
        ("rkky-mechanism.svg", fig_rkky_mechanism),
        ("rkky-oscillations.svg", fig_rkky_oscillations),
        ("multilayer-gmr-spinglass.svg", fig_multilayer_gmr_spinglass),
    ]
    for filename, func in figs:
        path = os.path.join(IMG_DIR, filename)
        func(path)
        print(f" Згенеровано: {path}")

if __name__ == "__main__":
    main()
