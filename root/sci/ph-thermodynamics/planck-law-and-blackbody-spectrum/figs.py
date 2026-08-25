# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Випромінювання чорного тіла'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_cavity_radiation():
    """Фігура 1: Схема моделі абсолютно чорного тіла (порожнина Hohlraum з малим отвором)."""
    w, h = 760, 380
    frags = []

    # Title
    frags.append(text(w / 2, 25, "Фізична модель абсолютно чорного тіла (порожнина Гольраума)", size=15, bold=True))

    cx, cy, r_inner = 250, 200, 115

    # Cavity wall - single dark circle with stroke representing wall
    frags.append(circle(cx, cy, r_inner, fill="#0f172a", stroke=LINE, sw=4))

    # Aperture gap
    aperture_y1 = cy - 15
    aperture_y2 = cy + 15
    aperture_x = cx + r_inner

    # Mask aperture opening
    frags.append(rect(aperture_x - 3, aperture_y1, 10, aperture_y2 - aperture_y1, fill="#0f172a", stroke="none"))

    # Aperture labels & lines
    frags.append(line(aperture_x + 35, cy - 35, aperture_x + 3, cy - 10, color=NEG, sw=1.5))
    frags.append(text(aperture_x + 40, cy - 40, "Малий отвір (площа A)", size=12, color=NEG, bold=True))

    # Incoming light ray entering the aperture
    frags.append(arrow(aperture_x + 130, cy - 5, aperture_x + 5, cy, color="#f59e0b", sw=2.5))
    frags.append(text(aperture_x + 135, cy - 10, "Падаючий промінь", size=12, color="#d97706", bold=True))

    # Internal multiple reflection path
    ray_pts = [
        (aperture_x, cy),
        (cx - 90, cy - 65),
        (cx + 40, cy + 95),
        (cx - 100, cy + 40),
        (cx + 80, cy - 70),
        (cx - 40, cy - 100),
        (cx + 10, cy + 100),
    ]

    for i in range(len(ray_pts) - 1):
        x1, y1 = ray_pts[i]
        x2, y2 = ray_pts[i + 1]
        alpha = max(0.25, 1.0 - i * 0.12)
        r_col = f"rgba(245, 158, 11, {alpha:.2f})"
        frags.append(line(x1, y1, x2, y2, color=r_col, sw=1.8, dash="3,2"))
        frags.append(circle(x2, y2, 3, fill="#f59e0b", stroke="none"))

    # Explanatory text boxes on the right
    frags.append(textbox(570, 90, "Стінки порожнини:\n• Виготовлені з поглинаючого матеріалу\n• Підтримуються при сталій T\n• Безперервно випромінюють і поглинають", size=11.5, fill="#f8fafc", stroke=LINE, sw=1.2)[0])
    frags.append(textbox(570, 210, "Термодинамічна рівновага:\n• Випромінювання всередині повністю ізотропне\n• Спектральна густина u(ν, T) залежить ЛИШЕ від T\n• Отвір випускає малу частку випромінювання", size=11.5, fill="#eff6ff", stroke=POS, sw=1.2)[0])
    frags.append(textbox(570, 320, "Коефіцієнт поглинання отвору: α(ν) = 1.0", size=12, bold=True, fill="#fef2f2", stroke=NEG, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "cavity-radiation.svg"), w, h, *frags)


def build_fig2_planck_spectrum_curves():
    """Фігура 2: Спектральна щільність випромінювання Планка для різних температур (закон зміщення Віна та Стефана-Больцмана)."""
    w, h = 800, 440
    frags = []

    frags.append(text(w / 2, 25, "Спектральна яскравість випромінювання Планка B_λ(λ, T)", size=15, bold=True))

    ox, oy = 85, 370
    graph_w, graph_h = 660, 300

    # Axes
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Довжина хвилі λ (мкм)", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "Спектральна яскравість B_λ", size=13, bold=True, anchor="middle"))

    # Wavelength axis ticks (0.5 to 3.5 μm)
    for i in range(7):
        lam = 0.5 + i * 0.5
        x = ox + (lam - 0.5) / 3.0 * graph_w
        frags.append(line(x, oy, x, oy + 6, color=LINE, sw=1.5))
        frags.append(text(x, oy + 22, f"{lam:.1f}", size=11))

    temps = [
        (6000, "#dc2626", "T = 6000 K (Сонце)"),
        (5000, "#d97706", "T = 5000 K"),
        (4000, "#2563eb", "T = 4000 K"),
        (3000, "#059669", "T = 3000 K"),
    ]

    c2 = 14387.7  # μm·K

    def planck_val(lam, T):
        x = c2 / (lam * T)
        if x > 100:
            return 0.0
        return (1.0 / (lam ** 5)) / (math.exp(x) - 1.0)

    max_val_6000 = planck_val(0.483, 6000)

    wien_peaks = []

    for T, color, label in temps:
        pts = []
        N = 80
        lam_max_curr = 2897.77 / T
        val_max_curr = planck_val(lam_max_curr, T)

        x_peak = ox + (lam_max_curr - 0.5) / 3.0 * graph_w
        y_peak = oy - (val_max_curr / max_val_6000) * (graph_h - 40)
        wien_peaks.append((x_peak, y_peak, T))

        for i in range(N):
            lam = 0.5 + (i / float(N - 1)) * 3.0
            val = planck_val(lam, T)
            cx = ox + (lam - 0.5) / 3.0 * graph_w
            cy = oy - (val / max_val_6000) * (graph_h - 40)
            pts.append((cx, cy))

        for i in range(len(pts) - 1):
            frags.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=color, sw=2.5))

    for i in range(len(wien_peaks) - 1):
        frags.append(line(wien_peaks[i][0], wien_peaks[i][1], wien_peaks[i + 1][0], wien_peaks[i + 1][1], color="#7c3aed", sw=2, dash="4,4"))

    for xp, yp, T in wien_peaks:
        frags.append(circle(xp, yp, 4, fill="#7c3aed", stroke="#ffffff", sw=1.5))

    frags.append(textbox(ox + 480, oy - 240, "T = 6000 K (λ_max = 0.48 мкм)\nT = 5000 K (λ_max = 0.58 мкм)\nT = 4000 K (λ_max = 0.72 мкм)\nT = 3000 K (λ_max = 0.97 мкм)", size=11, fill="#ffffff", stroke=LINE, sw=1.2)[0])

    frags.append(textbox(ox + 210, oy - 275, "Закон зміщення Віна:\nλ_max · T = b ≈ 2.898 × 10⁻³ м·К", size=11.5, fill="#f3e8ff", stroke="#7c3aed", sw=1.5)[0])

    frags.append(textbox(ox + 480, oy - 120, "Закон Стефана-Больцмана:\nПлоща під кривою ∝ T⁴", size=11.5, fill="#fef2f2", stroke="#dc2626", sw=1.5)[0])

    render(os.path.join(IMG_DIR, "planck-spectrum-curves.svg"), w, h, *frags)


def build_fig3_ultraviolet_catastrophe_comparison():
    """Фігура 3: Порівняння класичного закону Релея-Джинса, наближення Віна та квантового закону Планка."""
    w, h = 780, 420
    frags = []

    frags.append(text(w / 2, 25, "Порівняння законів Релея-Джинса, Віна та закону Планка", size=15, bold=True))

    ox, oy = 80, 360
    graph_w, graph_h = 650, 290

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 38, "Частота ν (або 1/λ)", size=13, bold=True))
    frags.append(text(ox - 45, oy - graph_h / 2, "Спектральна густина енергії u(ν, T)", size=13, bold=True, anchor="middle"))

    N = 60

    # Rayleigh-Jeans curve
    rj_pts = []
    for i in range(N):
        x_norm = (i / float(N - 1)) * 1.3
        cx = ox + (x_norm / 1.3) * (graph_w * 0.55)
        cy = oy - graph_h * (0.8 * x_norm * x_norm)
        if cy >= oy - graph_h:
            rj_pts.append((cx, cy))

    for i in range(len(rj_pts) - 1):
        frags.append(line(rj_pts[i][0], rj_pts[i][1], rj_pts[i + 1][0], rj_pts[i + 1][1], color="#dc2626", sw=3, dash="6,3"))

    # Wien's curve
    wien_pts = []
    for i in range(N):
        x_norm = (i / float(N - 1)) * 3.0
        cx = ox + (i / float(N - 1)) * graph_w
        val = (x_norm ** 3) * math.exp(-1.1 * x_norm) if x_norm > 0 else 0
        cy = oy - graph_h * (val / 0.42)
        wien_pts.append((cx, cy))

    for i in range(len(wien_pts) - 1):
        frags.append(line(wien_pts[i][0], wien_pts[i][1], wien_pts[i + 1][0], wien_pts[i + 1][1], color="#2563eb", sw=2.5, dash="4,4"))

    # Planck curve
    planck_pts = []
    for i in range(N):
        x_norm = (i / float(N - 1)) * 3.0
        cx = ox + (i / float(N - 1)) * graph_w
        if x_norm == 0:
            val = 0
        else:
            val = (x_norm ** 3) / (math.exp(x_norm) - 1.0)
        cy = oy - graph_h * (val / 1.42)
        planck_pts.append((cx, cy))

    for i in range(len(planck_pts) - 1):
        frags.append(line(planck_pts[i][0], planck_pts[i][1], planck_pts[i + 1][0], planck_pts[i + 1][1], color="#059669", sw=3.5))

    # Explanatory text boxes
    frags.append(textbox(ox + 160, oy - 230, "Релей-Джинс (класичний):\nu(ν) ∝ ν² k_B T\n(Прямує до ∞ при ν → ∞)", size=11, fill="#fee2e2", stroke="#dc2626", sw=1.5)[0])

    frags.append(textbox(ox + 460, oy - 230, "Формула Віна (1896):\nu(ν) ∝ ν³ exp(-hν/kT)\n(Працює лише при високих ν)", size=11, fill="#dbeafe", stroke="#2563eb", sw=1.5)[0])

    frags.append(textbox(ox + 460, oy - 100, "Закон Планка (1900):\nu(ν) = (8πhν³/c³) / (exp(hν/kT) - 1)\n(Точний для всього спектра!)", size=11, fill="#d1fae5", stroke="#059669", sw=1.8)[0])

    render(os.path.join(IMG_DIR, "ultraviolet-catastrophe-comparison.svg"), w, h, *frags)


def build_fig4_energy_quantization_oscillators():
    """Фігура 4: Дискретна драбина енергетичних рівнів E_n = n · h · ν та пригнічення високих частот."""
    w, h = 760, 400
    frags = []

    frags.append(text(w / 2, 25, "Дискретизація енергії осциляторів стінок та квантове виморожування", size=15, bold=True))

    # Left box: Low frequency oscillator
    b1_x, b1_y, b1_w, b1_h = 40, 55, 320, 325
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 25, "Низька частота (h·ν << k_B·T)", size=13, bold=True, color=POS))
    frags.append(line(b1_x + 15, b1_y + 35, b1_x + b1_w - 15, b1_y + 35, color=MUTED, sw=1, dash="3,3"))

    n_levels_1 = 6
    for n in range(n_levels_1):
        ly = b1_y + 220 - n * 30
        frags.append(line(b1_x + 40, ly, b1_x + 220, ly, color=POS, sw=2))
        frags.append(text(b1_x + 230, ly + 4, f"E_{n} = {n} hν", size=11, color=POS))

    frags.append(textbox(b1_x + b1_w / 2, b1_y + 275, "Квант ΔE = h·ν малий у порівнянні з k_B·T.\nТепловий рух легко збуджує багато рівнів.\n⟨E⟩ ≈ k_B·T (класична межа)", size=11, fill="#ecfdf5", stroke=POS, sw=1.2)[0])

    # Right box: High frequency oscillator
    b2_x, b2_y, b2_w, b2_h = 400, 55, 320, 325
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 25, "Висока частота (h·ν >> k_B·T)", size=13, bold=True, color=NEG))
    frags.append(line(b2_x + 15, b2_y + 35, b2_x + b2_w - 15, b2_y + 35, color=MUTED, sw=1, dash="3,3"))

    n_levels_2 = 3
    for n in range(n_levels_2):
        ly = b2_y + 220 - n * 75
        frags.append(line(b2_x + 40, ly, b2_x + 220, ly, color=NEG, sw=2))
        frags.append(text(b2_x + 230, ly + 4, f"E_{n} = {n} hν", size=11, color=NEG))

    frags.append(textbox(b2_x + b2_w / 2, b2_y + 275, "Квант ΔE = h·ν значно більший за k_B·T.\nІмовірність P(E₁) ∝ exp(-hν/kT) → 0.\nМода виявилась вимороженою!", size=11, fill="#fef2f2", stroke=NEG, sw=1.2)[0])

    render(os.path.join(IMG_DIR, "energy-quantization-oscillators.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_cavity_radiation()
    build_fig2_planck_spectrum_curves()
    build_fig3_ultraviolet_catastrophe_comparison()
    build_fig4_energy_quantization_oscillators()
    print("Фігури для випромінювання чорного тіла успішно згенеровано.")
