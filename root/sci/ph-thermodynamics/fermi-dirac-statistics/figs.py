# -*- coding: utf-8 -*-
"""Фігури до теми «Квантова статистика Фермі — Дірака та квантовий вироджений газ».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Розподіл Фермі — Дірака f(E) за різних температур ─────────────
def fig_fermi_dirac_distribution():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Розподіл Фермі — Дірака f(E) при різних температурах", size=16, bold=True, color=INK))

    x_zero = 90
    x_ef = 380
    x_max = 680
    y_top = 70
    y_bot = 350
    y_half = (y_top + y_bot) / 2

    # Background grids / reference lines
    f.append(path_svg(f"M {x_zero} {y_half} L {x_max} {y_half}", stroke="#e2e8f0", sw=1, dash="4,4"))
    f.append(path_svg(f"M {x_ef} {y_top} L {x_ef} {y_bot}", stroke="#94a3b8", sw=1.5, dash="4,4"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "E", size=14, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 20, color=INK, sw=1.5))
    f.append(text(x_zero - 30, y_top - 15, "f(E)", size=14, bold=True, italic=True, color=INK))

    # Axis ticks and labels
    f.append(text(x_zero - 15, y_top + 4, "1", size=12, bold=True, color=INK))
    f.append(text(x_zero - 20, y_half + 4, "0.5", size=11, color=MUTED))
    f.append(text(x_zero - 15, y_bot + 4, "0", size=12, bold=True, color=INK))

    f.append(text(x_ef, y_bot + 22, "E_F", size=13, bold=True, color="#dc2626"))
    f.append(text(x_ef, y_half - 10, "(E_F, 0.5)", size=11, bold=True, color="#dc2626"))

    # 1. T = 0 K (step function)
    f.append(path_svg(f"M {x_zero} {y_top} L {x_ef} {y_top} L {x_ef} {y_bot} L {x_max} {y_bot}", stroke="#2563eb", sw=3))

    # 2. T << T_F (Low T, e.g. T = 300 K)
    pts_low = []
    for i in range(151):
        x = x_zero + (i / 150.0) * (x_max - x_zero)
        e_rel = (x - x_ef) / 35.0  # scaled (E - E_F) / (k_B T)
        if e_rel > 15:
            fe = 0.0
        elif e_rel < -15:
            fe = 1.0
        else:
            fe = 1.0 / (math.exp(e_rel) + 1.0)
        y = y_bot - fe * (y_bot - y_top)
        pts_low.append((x, y))

    d_low = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_low)
    f.append(path_svg(d_low, stroke="#059669", sw=2.5))

    # 3. T ~ T_F (High T)
    pts_high = []
    for i in range(151):
        x = x_zero + (i / 150.0) * (x_max - x_zero)
        e_rel = (x - x_ef) / 110.0
        fe = 1.0 / (math.exp(e_rel) + 1.0)
        y = y_bot - fe * (y_bot - y_top)
        pts_high.append((x, y))

    d_high = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_high)
    f.append(path_svg(d_high, stroke="#d97706", sw=2, dash="6,3"))

    # Thermal smearing annotation for low T
    x_smear_left = x_ef - 35
    x_smear_right = x_ef + 35
    f.append(path_svg(f"M {x_smear_left} {y_bot + 35} L {x_smear_right} {y_bot + 35}", stroke="#059669", sw=1.5))
    f.append(path_svg(f"M {x_smear_left} {y_bot + 30} L {x_smear_left} {y_bot + 40}", stroke="#059669", sw=1.5))
    f.append(path_svg(f"M {x_smear_right} {y_bot + 30} L {x_smear_right} {y_bot + 40}", stroke="#059669", sw=1.5))
    f.append(text(x_ef, y_bot + 52, "Теплове розмиття ~ k_B · T", size=11, bold=True, color="#059669"))

    # Legend
    f.append(rect(480, 80, 210, 95, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(path_svg("M 495 100 L 530 100", stroke="#2563eb", sw=3))
    f.append(text(540, 104, "T = 0 K (Сходинка)", size=11, bold=True, color="#2563eb"))

    f.append(path_svg("M 495 125 L 530 125", stroke="#059669", sw=2.5))
    f.append(text(540, 129, "T << T_F (Низька T, 300 K)", size=11, bold=True, color="#059669"))

    f.append(path_svg("M 495 150 L 530 150", stroke="#d97706", sw=2, dash="6,3"))
    f.append(text(540, 154, "T ~ T_F (Висока T)", size=11, bold=True, color="#d97706"))

    f.append(text(W / 2, H - 10, "При T = 0 K розподіл строго сходинковий; при T > 0 K розмивається лише вузька область шириною ~ k_B·T довкола E_F", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fermi-dirac-distribution.svg'), W, H, "\n".join(f))

# ── Фігура 2: Густина зайнятих станів n(E) = g(E) · f(E) ──────────────────────
def fig_density_of_occupied_states():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Густина зайнятих станів n(E) = g(E) · f(E) при T = 0 K та T > 0 K", size=16, bold=True, color=INK))

    x_zero = 90
    x_ef = 450
    x_max = 680
    y_top = 70
    y_bot = 350

    # Density of states g(E) = C * sqrt(E)
    pts_g = []
    for i in range(151):
        x = x_zero + (i / 150.0) * (x_max - x_zero)
        e_val = (x - x_zero) / (x_max - x_zero)
        g_val = math.sqrt(max(0, e_val)) * 1.35
        y = y_bot - g_val * (y_bot - y_top) * 0.7
        pts_g.append((x, y))

    # Shaded area under T = 0 K
    pts_fill0 = [(x_zero, y_bot)]
    for x, y in pts_g:
        if x <= x_ef:
            pts_fill0.append((x, y))
        else:
            break
    pts_fill0.append((x_ef, y_bot))
    d_fill0 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_fill0) + " Z"
    f.append(path_svg(d_fill0, fill="#dbeafe", stroke="none"))

    # Draw density of states g(E) curve (dashed black)
    d_g = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_g)
    f.append(path_svg(d_g, stroke="#64748b", sw=2, dash="5,4"))
    f.append(text(x_max - 60, y_top + 40, "g(E) ~ √E", size=13, bold=True, color="#64748b"))

    # Draw occupied states curve n(E) at T > 0 K
    pts_n = []
    for x, y_g in pts_g:
        e_rel = (x - x_ef) / 30.0
        if e_rel > 15:
            fe = 0.0
        elif e_rel < -15:
            fe = 1.0
        else:
            fe = 1.0 / (math.exp(e_rel) + 1.0)
        y_occ = y_bot - (y_bot - y_g) * fe
        pts_n.append((x, y_occ))

    d_n = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_n)
    f.append(path_svg(d_n, stroke="#2563eb", sw=2.5))

    # Fermi level vertical reference
    f.append(path_svg(f"M {x_ef} {y_top - 10} L {x_ef} {y_bot}", stroke="#dc2626", sw=1.5, dash="4,4"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "E", size=14, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 20, color=INK, sw=1.5))
    f.append(text(x_zero - 45, y_top - 15, "n(E)", size=14, bold=True, italic=True, color=INK))

    f.append(text(x_ef, y_bot + 22, "E_F", size=13, bold=True, color="#dc2626"))

    # Labels inside the diagram
    f.append(text(250, 240, "Заповнене «Море Фермі» (T = 0 K)", size=12, bold=True, color="#1e40af"))

    # Excitation arrows / regions
    f.append(arrow(x_ef - 20, 160, x_ef + 25, 270, color="#d97706", sw=1.5))
    f.append(text(x_ef + 70, 230, "Теплові збудження при T > 0 K", size=11, bold=True, color="#d97706"))

    f.append(text(W / 2, H - 10, "При T > 0 K електрони з області під E_F переходять у вільні стани над E_F в межах вузького енергетичного проміжку ~ k_B·T", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'density-of-occupied-states.svg'), W, H, "\n".join(f))

# ── Фігура 3: Критерій виродження газу (Класичний vs Квантовий) ────────────────
def fig_degeneracy_regimes():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28, "Порівняння станів: класичний газ проти квантового виродженого газу", size=16, bold=True, color=INK))

    # Left Panel: Classical Gas
    f.append(rect(40, 60, 320, 280, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    f.append(text(200, 88, "Класичний газ (Максвелл — Больцман)", size=13, bold=True, color="#1e293b"))
    f.append(text(200, 110, "n · λ_dB³ << 1  (d >> λ_dB)", size=12, bold=True, color="#475569"))

    # Particles in classical gas (small non-overlapping dots)
    coords_class = [
        (80, 160), (140, 220), (220, 170), (290, 240), (120, 280),
        (260, 150), (180, 250), (310, 180), (100, 190), (240, 280)
    ]
    for cx, cy in coords_class:
        f.append(circle(cx, cy, 6, fill="#2563eb", stroke="none"))
        f.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="#93c5fd" stroke-width="1" stroke-dasharray="2,2"/>')

    f.append(text(200, 310, "Хвильові пакети частинок не перекриваються", size=11, color="#334155"))
    f.append(text(200, 328, "Принцип Паулі не впливає на розподіл", size=11, color="#334155"))

    # Right Panel: Quantum Degenerate Gas
    f.append(rect(400, 60, 320, 280, fill="#eff6ff", stroke="#93c5fd", rx=8))
    f.append(text(560, 88, "Квантовий вироджений газ (Фермі — Дірака)", size=13, bold=True, color="#1e40af"))
    f.append(text(560, 110, "n · λ_dB³ >> 1  (d <= λ_dB)", size=12, bold=True, color="#2563eb"))

    # Particles in quantum gas (large overlapping wave packets)
    coords_quant = [
        (460, 170), (510, 220), (570, 160), (620, 230), (480, 270),
        (550, 260), (630, 170), (520, 180), (590, 210), (450, 220)
    ]
    for cx, cy in coords_quant:
        f.append(circle(cx, cy, 28, fill="#bfdbfe", stroke="#3b82f6", sw=1.5))
        f.append(circle(cx, cy, 5, fill="#1e40af", stroke="none"))

    f.append(text(560, 310, "Хвильові функції перекриваються у просторі", size=11, bold=True, color="#1e40af"))
    f.append(text(560, 328, "Формується Море Фермі з тиском P_0 > 0", size=11, bold=True, color="#1e40af"))

    f.append(text(W / 2, H - 12, "Виродження настає, коли теплова довжина хвилі де Бройля λ_dB стає порівнянною із середньою відстанню між частинками d", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'degeneracy-regimes.svg'), W, H, "\n".join(f))


if __name__ == '__main__':
    fig_fermi_dirac_distribution()
    fig_density_of_occupied_states()
    fig_degeneracy_regimes()
    print("All figures successfully generated in ./img/")
