# -*- coding: utf-8 -*-
"""Фігури для теми «Квантування енергії» (book/physics/quantum-mechanics/energy-quantization)."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def path_svg(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def fig1_blackbody_planck():
    """fig1-blackbody-planck.svg: Спектр випромінювання абсолютно чорного тіла (Релей-Джинс vs Планк)."""
    W, H = 820, 480
    frags = []

    # Фон та заголовок
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 35, "Спектральна щільність випромінювання абсолютно чорного тіла (T = 5500 K)", size=16, bold=True, color="#1e293b"))

    # Осі координат
    x0, y0 = 100, 400
    w_axis, h_axis = 660, 330
    frags.append(line(x0, y0, x0 + w_axis, y0, color="#1e293b", sw=2.0))
    frags.append(line(x0, y0, x0, y0 - h_axis, color="#1e293b", sw=2.0))

    # Стрілки осей
    frags.append(path_svg(f"M {x0 + w_axis} {y0 - 5} L {x0 + w_axis + 10} {y0} L {x0 + w_axis} {y0 + 5} Z", fill="#1e293b", stroke="#1e293b"))
    frags.append(path_svg(f"M {x0 - 5} {y0 - h_axis} L {x0} {y0 - h_axis - 10} L {x0 + 5} {y0 - h_axis} Z", fill="#1e293b", stroke="#1e293b"))

    # Підписи осей
    frags.append(text(x0 + w_axis + 15, y0 + 18, "Частота ν", size=13, bold=True, color="#1e293b"))
    frags.append(text(x0 - 15, y0 - h_axis - 15, "Густина енергії u(ν)", size=13, bold=True, color="#1e293b"))

    # Мітки по частоті
    for i in range(1, 6):
        x_val = x0 + i * 110
        frags.append(line(x_val, y0, x_val, y0 + 5, color="#1e293b", sw=1.5))

    # Крива Релея-Джинса (класична фізика): u(ν) ~ ν² -> розбіжність в УФ
    pts_rj = []
    for px in range(0, 310, 5):
        nu = px / 100.0
        u_rj = 35.0 * (nu ** 2)
        py = y0 - u_rj
        if py < y0 - h_axis:
            break
        pts_rj.append(f"{x0 + px:.1f},{py:.1f}")

    d_rj = "M " + " L ".join(pts_rj)
    frags.append(path_svg(d_rj, stroke=RED_S, sw=3.0, dash="6,6"))

    # Крива Планка (квантова фізика): u(ν) ~ ν³ / (exp(hν/kT) - 1)
    pts_planck = []
    for px in range(0, 640, 5):
        nu = px / 100.0
        if nu == 0:
            u_pl = 0
        else:
            u_pl = (180.0 * (nu ** 3)) / (math.exp(1.4 * nu) - 1.0)
        py = y0 - u_pl
        pts_planck.append(f"{x0 + px:.1f},{py:.1f}")

    d_planck = "M " + " L ".join(pts_planck)
    d_planck_area = d_planck + f" L {x0 + 635} {y0} L {x0} {y0} Z"
    frags.append(path_svg(d_planck_area, fill=TEAL_F, stroke="none"))
    frags.append(path_svg(d_planck, stroke=TEAL_S, sw=3.5))

    # Позначення ультрафіолетової катастрофи
    frags.append(rect(200, 75, 230, 55, fill=RED_F, stroke=RED_S, sw=1.5, rx=6))
    frags.append(text(315, 95, "Ультрафіолетова катастрофа", size=12, bold=True, color=RED_S))
    frags.append(text(315, 115, "Класична фізика: u(ν) → ∞", size=11, color="#991b1b"))
    frags.append(line(210, 130, 190, 180, color=RED_S, sw=1.5, dash="2,2"))

    # Легенда
    frags.append(rect(480, 70, 300, 95, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(line(495, 95, 545, 95, color=RED_S, sw=3.0, dash="6,6"))
    frags.append(text(555, 99, "Релей — Джинс (Класична)", size=12, color="#1e293b"))

    frags.append(line(495, 135, 545, 135, color=TEAL_S, sw=3.5))
    frags.append(text(555, 139, "Планк (Квантова: E = h·ν)", size=12, bold=True, color=TEAL_S))

    # Текстова вставка з формулою - розміщено у чистій зоні (cx=600, cy=240)
    box_svg, _, _ = textbox(610, 240, ["Закон випромінювання Планка", "u(ν) = (8πhν³/c³) · 1/(e^(hν/kT) - 1)"], size=12, fill="#ffffff", stroke=TEAL_S)
    frags.append(box_svg)

    content = "\n".join(frags)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>'
    with open(os.path.join(IMG, "fig1-blackbody-planck.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig2_bohr_atom_levels():
    """fig2-bohr-atom-levels.svg: Енергетичний спектр атома водню за Бором та квантові переходи."""
    W, H = 480, 480
    frags = []

    # Фон та заголовок
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 35, "Дискретні енергетичні рівні та оптичні переходи", size=15, bold=True, color="#1e293b"))

    # Ліва частина: Енергетична діаграма рівнів E_n = -13.6 / n² eV
    x_left = 70
    w_level = 320
    levels = [
        (1, -13.60, 410, "n = 1 (Основний стан, E₁ = -13.60 еВ)"),
        (2, -3.40, 310, "n = 2 (E₂ = -3.40 еВ)"),
        (3, -1.51, 230, "n = 3 (E₃ = -1.51 еВ)"),
        (4, -0.85, 170, "n = 4 (E₄ = -0.85 еВ)"),
        (5, -0.54, 130, "n = 5 (E₅ = -0.54 еВ)"),
    ]

    # Границя іонізації (E = 0)
    y_ion = 80
    frags.append(line(x_left, y_ion, x_left + w_level, y_ion, color=RED_S, sw=2.0, dash="5,5"))
    frags.append(text(x_left + w_level / 2, y_ion - 8, "E = 0 (Границя іонізації)", size=11, bold=True, color=RED_S))

    # Енергетичні рівні
    for n, ev, y_pos, label in levels:
        sw_l = 3.0 if n == 1 else 2.0
        c_l = BLUE_S if n == 1 else "#334155"
        frags.append(line(x_left, y_pos, x_left + w_level, y_pos, color=c_l, sw=sw_l))
        frags.append(text(x_left - 10, y_pos + 4, f"{ev:.2f} еВ", size=11, color="#475569", anchor="end"))
        frags.append(text(x_left + w_level + 8, y_pos + 4, f"n={n}", size=11, color="#1e293b", anchor="start"))

    # Переходи (серія Лаймана: n->1, серія Бальмера: n->2)
    # Перехід 2->1 (Лаймана alpha)
    frags.append(line(x_left + 60, 310, x_left + 60, 410, color=PURPLE_S, sw=2.5))
    frags.append(path_svg(f"M {x_left + 55} 400 L {x_left + 60} 410 L {x_left + 65} 400 Z", fill=PURPLE_S, stroke=PURPLE_S))
    frags.append(text(x_left + 82, 360, "Ly-α", size=10, bold=True, color=PURPLE_S))

    # Перехід 3->1 (Лаймана beta)
    frags.append(line(x_left + 110, 230, x_left + 110, 410, color=PURPLE_S, sw=2.5))
    frags.append(path_svg(f"M {x_left + 105} 400 L {x_left + 110} 410 L {x_left + 115} 400 Z", fill=PURPLE_S, stroke=PURPLE_S))
    frags.append(text(x_left + 132, 320, "Ly-β", size=10, bold=True, color=PURPLE_S))

    # Перехід 3->2 (Бальмера alpha - червоне світло)
    frags.append(line(x_left + 190, 230, x_left + 190, 310, color=RED_S, sw=2.5))
    frags.append(path_svg(f"M {x_left + 185} 300 L {x_left + 190} 310 L {x_left + 195} 300 Z", fill=RED_S, stroke=RED_S))
    frags.append(text(x_left + 212, 270, "H-α", size=10, bold=True, color=RED_S))

    # Перехід 4->2 (Бальмера beta - блакитне світло)
    frags.append(line(x_left + 240, 170, x_left + 240, 310, color=TEAL_S, sw=2.5))
    frags.append(path_svg(f"M {x_left + 235} 300 L {x_left + 240} 310 L {x_left + 245} 300 Z", fill=TEAL_S, stroke=TEAL_S))
    frags.append(text(x_left + 262, 240, "H-β", size=10, bold=True, color=TEAL_S))

    # Формульне пояснення внизу
    box_svg, _, _ = textbox(W / 2, 445, ["E_n = -13.6 / n² еВ", "h·ν = E_n2 - E_n1"], size=12, fill="#ffffff", stroke=BLUE_S)
    frags.append(box_svg)

    content = "\n".join(frags)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>'
    with open(os.path.join(IMG, "fig2-bohr-atom-levels.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig3_potential_well_quantization():
    """fig3-potential-well-quantization.svg: Нескінченно глибока потенціальна яма та стаціонарні хвильові функції."""
    W, H = 820, 500
    frags = []

    # Фон та заголовок
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 35, "Нескінченна 1D потенціальна яма: хвильові функції ψₙ(x) та рівня Eₙ ~ n²", size=16, bold=True, color="#1e293b"))

    # Межі ями
    x_left, x_right = 220, 580
    w_well = x_right - x_left
    y_bot, y_top = 430, 80

    # Стінки U = infinity
    frags.append(rect(60, y_top, x_left - 60, y_bot - y_top + 20, fill="#e2e8f0", stroke="#64748b", sw=2.0))
    frags.append(rect(x_right, y_top, W - 60 - x_right, y_bot - y_top + 20, fill="#e2e8f0", stroke="#64748b", sw=2.0))
    frags.append(text(140, (y_bot + y_top) / 2, "U(x) = ∞", size=15, bold=True, color="#475569"))
    frags.append(text(650, (y_bot + y_top) / 2, "U(x) = ∞", size=15, bold=True, color="#475569"))

    # Дно ями
    frags.append(line(x_left, y_bot, x_right, y_bot, color="#1e293b", sw=2.5))
    frags.append(text(x_left, y_bot + 20, "x = 0", size=12, bold=True, color="#1e293b"))
    frags.append(text(x_right, y_bot + 20, "x = L", size=12, bold=True, color="#1e293b"))

    # Внутрішня зона U = 0
    frags.append(text((x_left + x_right) / 2, y_bot + 20, "Ширина ями L (U = 0)", size=12, color="#475569"))

    # Рівні E1, E2, E3
    levels_data = [
        (1, 370, "E₁ = π²ℏ² / (2mL²)", BLUE_S, BLUE_F),
        (2, 290, "E₂ = 4·E₁", TEAL_S, TEAL_F),
        (3, 160, "E₃ = 9·E₁", PURPLE_S, PURPLE_F),
    ]

    for n, y_lev, label, color_s, color_f in levels_data:
        frags.append(line(x_left, y_lev, x_right, y_lev, color=color_s, sw=2.0, dash="6,6"))
        frags.append(text(x_right + 15, y_lev + 4, label, size=12, bold=True, color=color_s, anchor="start"))

        amp = 40.0
        pts_psi = []
        num_pts = 100
        for i in range(num_pts + 1):
            px = x_left + (w_well * i / num_pts)
            val = math.sin(n * math.pi * i / num_pts)
            py = y_lev - amp * val
            pts_psi.append(f"{px:.1f},{py:.1f}")

        d_psi = "M " + " L ".join(pts_psi)
        frags.append(path_svg(d_psi, stroke=color_s, sw=2.5))
        frags.append(text(x_left - 15, y_lev + 4, f"n = {n}", size=12, bold=True, color=color_s, anchor="end"))

    box_svg, _, _ = textbox(400, 75, ["Умова квантування (стояча хвиля)", "ψ(0) = 0,   ψ(L) = 0   ⇒   k·L = n·π"], size=12, fill="#ffffff", stroke=BLUE_S)
    frags.append(box_svg)

    content = "\n".join(frags)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>'
    with open(os.path.join(IMG, "fig3-potential-well-quantization.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig4_harmonic_oscillator_spectrum():
    """fig4-harmonic-oscillator-spectrum.svg: Квантовий гармонічний осцилятор та енергія нульових коливань."""
    W, H = 820, 520
    frags = []

    # Фон та заголовок
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 35, "Квантовий гармонічний осцилятор: U(x) = ½ m ω² x² та Eₙ = ℏω(n + ½)", size=16, bold=True, color="#1e293b"))

    # Центр параболи
    xc, y0 = 360, 440
    scale_x = 180.0
    scale_y = 320.0

    pts_parabola = []
    for px in range(-180, 181, 5):
        x_val = px / scale_x
        u_val = x_val ** 2
        py = y0 - scale_y * u_val
        pts_parabola.append(f"{xc + px:.1f},{py:.1f}")

    d_parabola = "M " + " L ".join(pts_parabola)
    frags.append(path_svg(d_parabola, fill=AMBER_F, stroke=AMBER_S, sw=3.0))

    frags.append(line(xc, y0 + 10, xc, 70, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(xc, y0 + 25, "x = 0 (Рівновага)", size=12, color="#475569"))

    osc_levels = [
        (0, 390, "n = 0: E₀ = ½ ℏω (Нульова енергія)", RED_S),
        (1, 310, "n = 1: E₁ = 3/2 ℏω", TEAL_S),
        (2, 230, "n = 2: E₂ = 5/2 ℏω", BLUE_S),
        (3, 150, "n = 3: E₃ = 7/2 ℏω", PURPLE_S),
    ]

    for n, y_pos, label, color_s in osc_levels:
        u_val = (y0 - y_pos) / scale_y
        x_val = math.sqrt(max(0, u_val))
        px_span = x_val * scale_x

        frags.append(line(xc - px_span, y_pos, xc + px_span, y_pos, color=color_s, sw=2.5))
        frags.append(text(xc + px_span + 15, y_pos + 4, label, size=12, bold=True, color=color_s, anchor="start"))

    y_gap1, y_gap2 = 310, 230
    x_gap = xc - 120
    frags.append(line(x_gap, y_gap1, x_gap, y_gap2, color="#1e293b", sw=2.0))
    frags.append(path_svg(f"M {x_gap-4} {y_gap1-6} L {x_gap} {y_gap1} L {x_gap+4} {y_gap1-6} Z", fill="#1e293b", stroke="#1e293b"))
    frags.append(path_svg(f"M {x_gap-4} {y_gap2+6} L {x_gap} {y_gap2} L {x_gap+4} {y_gap2+6} Z", fill="#1e293b", stroke="#1e293b"))
    frags.append(text(x_gap - 12, (y_gap1 + y_gap2) / 2 + 4, "ΔE = ℏω", size=12, bold=True, color="#1e293b", anchor="end"))

    frags.append(line(xc, y0, xc, 390, color=RED_S, sw=2.0, dash="3,3"))
    box_svg, _, _ = textbox(160, 380, ["Енергія нульових коливань", "E_0 = ½ ℏ·ω > 0", "(Принцип Гейзенберга)"], size=12, fill="#ffffff", stroke=RED_S)
    frags.append(box_svg)

    content = "\n".join(frags)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>'
    with open(os.path.join(IMG, "fig4-harmonic-oscillator-spectrum.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    fig1_blackbody_planck()
    fig2_bohr_atom_levels()
    fig3_potential_well_quantization()
    fig4_harmonic_oscillator_spectrum()
    print("Фігури створено успішно у ./img/")


if __name__ == "__main__":
    main()
