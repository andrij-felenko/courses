# -*- coding: utf-8 -*-
"""Фігури для теми «Квантовий гармонічний осцилятор» (book/physics/quantum-mechanics/quantum-harmonic-oscillator)."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра
COLOR_POTENTIAL = "#1e293b"
COLOR_E0 = "#dc2626"
COLOR_E1 = "#d97706"
COLOR_E2 = "#2563eb"
COLOR_E3 = "#7e22ce"

def path_svg(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

def fig_potential_levels():
    """potential-levels.svg: Параболічний потенціал та дискретні рівні енергії."""
    W, H = 840, 520
    frags = []

    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(420, 36, "Потенціальна яма та дискретні рівні енергії квантового осцилятора", size=16, bold=True, color="#0f172a"))

    # Осі координат
    cx = 420
    base_y = 440
    frags.append(line(80, base_y, 760, base_y, color="#64748b", sw=1.5)) # x-axis
    frags.append(arrow(cx, base_y + 20, cx, 60, color="#64748b", sw=1.5)) # V(x), E axis
    frags.append(text(775, base_y + 5, "x", size=14, bold=True, color="#475569"))
    frags.append(text(cx + 15, 70, "E, V(x)", size=14, bold=True, color="#475569"))

    # Парабола V(x) = (1/2) m w^2 x^2
    pts = []
    for ix in range(-300, 301, 5):
        x_val = cx + ix
        y_val = base_y - 0.0038 * (ix ** 2)
        pts.append(f"{x_val:.1f},{y_val:.1f}")
    d_parabola = "M " + " L ".join(pts)
    frags.append(path_svg(d_parabola, fill="none", stroke=COLOR_POTENTIAL, sw=2.5))
    frags.append(text(cx + 150, base_y - 320, "V(x) = (1/2) m ω² x²", size=13, bold=True, color=COLOR_POTENTIAL))

    # Рівні енергії: E_n = hbar * w * (n + 1/2)
    levels = [
        (0, "E₀ = (1/2) ℏω", COLOR_E0, 390),
        (1, "E₁ = (3/2) ℏω", COLOR_E1, 330),
        (2, "E₂ = (5/2) ℏω", COLOR_E2, 270),
        (3, "E₃ = (7/2) ℏω", COLOR_E3, 210),
    ]

    for n, label, col, y_lvl in levels:
        dy = base_y - y_lvl
        dx = math.sqrt(dy / 0.0038)
        x_left = cx - dx
        x_right = cx + dx

        frags.append(line(x_left - 30, y_lvl, x_right + 30, y_lvl, color=col, sw=2.0))
        frags.append(text(x_right + 45, y_lvl + 4, label, size=13, bold=True, color=col))

        frags.append(circle(x_left, y_lvl, 4, fill=col, stroke="#ffffff", sw=1.0))
        frags.append(circle(x_right, y_lvl, 4, fill=col, stroke="#ffffff", sw=1.0))
        frags.append(line(x_left, y_lvl, x_left, base_y, color=col, sw=1.0, dash="3,3"))
        frags.append(line(x_right, y_lvl, x_right, base_y, color=col, sw=1.0, dash="3,3"))

    dx0 = math.sqrt((base_y - 390) / 0.0038)
    frags.append(text(cx - dx0, base_y + 18, "-x₀", size=11, color=COLOR_E0))
    frags.append(text(cx + dx0, base_y + 18, "+x₀", size=11, color=COLOR_E0))

    # Стрілка різниці рівнів ΔE = ℏω
    frags.append(line(cx - 180, 390, cx - 180, 330, color="#059669", sw=1.8))
    frags.append(arrow(cx - 180, 365, cx - 180, 330, color="#059669", sw=1.8))
    frags.append(arrow(cx - 180, 355, cx - 180, 390, color="#059669", sw=1.8))
    frags.append(text(cx - 215, 364, "ΔE = ℏω", size=12, bold=True, color="#059669"))

    b1, _, _ = textbox(160, 130, "Рівновіддалені рівні:\nΔE = ℏω = const\n(квант енергії)", size=11, fill="#f0fdf4", stroke="#16a34a", sw=1.2)
    frags.append(b1)

    b2, _, _ = textbox(660, 130, "Нульова енергія:\nE₀ = (1/2) ℏω > 0\n(квантові флуктуації)", size=11, fill="#fef2f2", stroke="#dc2626", sw=1.2)
    frags.append(b2)

    render(os.path.join(IMG, "potential-levels.svg"), W, H, *frags)

def fig_wavefunctions_probability():
    """wavefunctions-probability.svg: Просторові хвильові функції ψ_n(x) та густина ймовірності |ψ_n(x)|²."""
    W, H = 840, 560
    frags = []

    frags.append(rect(10, 10, 820, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(420, 34, "Хвильові функції ψₙ(x) та густина ймовірності |ψₙ(x)|²", size=16, bold=True, color="#0f172a"))

    panels = [
        (0, "n = 0 (Основний стан, парний)", 80, 390, COLOR_E0),
        (1, "n = 1 (Перший збуджений, непарний)", 80, 270, COLOR_E1),
        (2, "n = 2 (Другий збуджений, парний)", 80, 150, COLOR_E2),
    ]

    cx = 420
    scale_x = 45.0

    def H0(xi): return 1.0
    def H1(xi): return 2.0 * xi
    def H2(xi): return 4.0 * (xi**2) - 2.0

    H_funcs = [H0, H1, H2]
    norms = [1.0 / (math.pi**0.25), 1.0 / (math.sqrt(2) * math.pi**0.25), 1.0 / (math.sqrt(8) * math.pi**0.25)]

    for n, title_text, panel_x, cy, col in panels:
        frags.append(line(120, cy, 720, cy, color="#cbd5e1", sw=1.2))
        frags.append(text(160, cy - 25, title_text, size=12, bold=True, color=col))

        xi_turn = math.sqrt(2 * n + 1)
        x_turn_left = cx - xi_turn * scale_x
        x_turn_right = cx + xi_turn * scale_x

        frags.append(line(x_turn_left, cy - 35, x_turn_left, cy + 35, color="#94a3b8", sw=1.0, dash="2,2"))
        frags.append(line(x_turn_right, cy - 35, x_turn_right, cy + 35, color="#94a3b8", sw=1.0, dash="2,2"))
        frags.append(text(x_turn_right + 15, cy + 20, f"x_{n}", size=10, color="#64748b"))

        pts_psi = []
        pts_prob = []
        H_fn = H_funcs[n]
        norm = norms[n]
        scale_y = 28.0 if n == 0 else (22.0 if n == 1 else 14.0)

        for ix in range(-180, 181, 3):
            xi = ix / scale_x
            psi = norm * H_fn(xi) * math.exp(-0.5 * xi**2)
            prob = psi**2

            x_curr = cx + ix
            y_psi = cy - psi * scale_y
            y_prob = cy - prob * scale_y * 1.5

            pts_psi.append(f"{x_curr:.1f},{y_psi:.1f}")
            pts_prob.append(f"{x_curr:.1f},{y_prob:.1f}")

        d_psi = "M " + " L ".join(pts_psi)
        frags.append(path_svg(d_psi, fill="none", stroke=col, sw=2.0))

        d_prob = "M " + f"{cx - 180:.1f},{cy:.1f} L " + " L ".join(pts_prob) + f" L {cx + 180:.1f},{cy:.1f} Z"
        frags.append(path_svg(d_prob, fill=col, stroke="none", sw=0))

    frags.append(line(200, 480, 240, 480, color=COLOR_E2, sw=2.0))
    frags.append(text(310, 484, "Хвильова функція ψₙ(x)", size=11, color="#1e293b"))

    frags.append(rect(450, 474, 30, 12, fill=COLOR_E2, stroke="none"))
    frags.append(text(570, 484, "Густина ймовірності |ψₙ(x)|²", size=11, color="#1e293b"))

    b_tun, _, _ = textbox(420, 520, "Тунельний ефект: |ψₙ(x)|² > 0 поза класичними точками повороту |x| > xₙ", size=11, fill="#fff7ed", stroke="#ea580c", sw=1.2)
    frags.append(b_tun)

    render(os.path.join(IMG, "wavefunctions-probability.svg"), W, H, *frags)

def fig_ladder_operators():
    """ladder-operators-scheme.svg: Схема операторів народження a† та знищення a."""
    W, H = 840, 500
    frags = []

    frags.append(rect(10, 10, 820, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(420, 36, "Алгебра операторів Дірака: знищення (a) та народження (a⁺)", size=16, bold=True, color="#0f172a"))

    states = [
        (0, "|0⟩ (Вакуумний / Основний)", 390, COLOR_E0),
        (1, "|1⟩ (Перший збуджений)", 310, COLOR_E1),
        (2, "|2⟩ (Другий збуджений)", 230, COLOR_E2),
        (3, "|3⟩ (Третій збуджений)", 150, COLOR_E3),
    ]

    for n, name, y_pos, col in states:
        frags.append(rect(300, y_pos - 18, 240, 36, fill="#f8fafc", stroke=col, sw=2.0, rx=6))
        frags.append(text(420, y_pos + 5, name, size=13, bold=True, color=col))

    for n in range(3):
        y_from = states[n][2] - 18
        y_to = states[n+1][2] + 18
        frags.append(line(240, y_from, 240, y_to, color="#16a34a", sw=2.2))
        frags.append(arrow(240, y_from, 240, y_to, color="#16a34a", sw=2.2))
        frags.append(text(180, (y_from + y_to)/2 + 4, f"a⁺|{n}⟩ = √{n+1}|{n+1}⟩", size=11, bold=True, color="#16a34a"))

    for n in range(1, 4):
        y_from = states[n][2] + 18
        y_to = states[n-1][2] - 18
        frags.append(line(600, y_from, 600, y_to, color="#dc2626", sw=2.2))
        frags.append(arrow(600, y_from, 600, y_to, color="#dc2626", sw=2.2))
        frags.append(text(660, (y_from + y_to)/2 + 4, f"a|{n}⟩ = √{n}|{n-1}⟩", size=11, bold=True, color="#dc2626"))

    frags.append(line(600, 390 + 18, 600, 440, color="#dc2626", sw=1.8, dash="3,3"))
    frags.append(circle(600, 440, 6, fill="#fef2f2", stroke="#dc2626", sw=1.5))
    frags.append(text(640, 444, "a|0⟩ = 0 (Нижня межа!)", size=11, bold=True, color="#dc2626"))

    b_ham, _, _ = textbox(420, 100, "H = ℏω (a⁺a + 1/2)    |    [a, a⁺] = 1", size=13, fill="#f1f5f9", stroke="#475569", sw=1.5, bold=True)
    frags.append(b_ham)

    render(os.path.join(IMG, "ladder-operators-scheme.svg"), W, H, *frags)

def fig_coherent_state():
    """coherent-state-evolution.svg: Еволюція когерентного стану |α⟩ у часі."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(420, 36, "Когерентний стан Глаубера |α⟩: осциляція хвильового пакета", size=16, bold=True, color="#0f172a"))

    cx = 420
    base_y = 380
    pts = []
    for ix in range(-280, 281, 5):
        y_val = base_y - 0.003 * (ix ** 2)
        pts.append(f"{cx + ix:.1f},{y_val:.1f}")
    frags.append(path_svg("M " + " L ".join(pts), fill="none", stroke="#94a3b8", sw=1.8, dash="4,4"))

    times = [
        ("t = 0 (Відхилення +A)", cx + 160, base_y - 0.003*(160**2), "#2563eb"),
        ("t = T/4 (Центр x=0)", cx, base_y, "#059669"),
        ("t = T/2 (Відхилення -A)", cx - 160, base_y - 0.003*(160**2), "#d97706"),
    ]

    for label, px, py, col in times:
        pts_g = []
        for ix in range(-60, 61, 3):
            gx = px + ix
            gy = py - 45.0 * math.exp(- (ix / 22.0)**2)
            pts_g.append(f"{gx:.1f},{gy:.1f}")

        d_g = f"M {px - 60:.1f},{py:.1f} L " + " L ".join(pts_g) + f" L {px + 60:.1f},{py:.1f} Z"
        frags.append(path_svg(d_g, fill=col, stroke=col, sw=1.5))
        frags.append(circle(px, py - 45.0, 4, fill="#ffffff", stroke=col, sw=1.5))
        frags.append(text(px, py - 60, label, size=11, bold=True, color=col))

    frags.append(line(cx - 160, base_y + 25, cx + 160, base_y + 25, color="#475569", sw=1.5))
    frags.append(circle(cx + 160, base_y + 25, 4, fill="#2563eb", stroke="#2563eb"))
    frags.append(circle(cx - 160, base_y + 25, 4, fill="#d97706", stroke="#d97706"))
    frags.append(arrow(cx - 140, base_y + 25, cx + 140, base_y + 25, color="#475569", sw=1.5))
    frags.append(text(cx, base_y + 45, "Класична траєкторія ⟨x(t)⟩ = A cos(ωt)", size=12, bold=True, color="#334155"))

    b_coh, _, _ = textbox(420, 110, "Мінімальний пакет: Δx · Δp = ℏ / 2\nПакет зберігає форму і НЕ розпливається у часі!", size=12, fill="#f0f9ff", stroke="#0284c7", sw=1.3)
    frags.append(b_coh)

    render(os.path.join(IMG, "coherent-state-evolution.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_potential_levels()
    fig_wavefunctions_probability()
    fig_ladder_operators()
    fig_coherent_state()
    print("Всі 4 фігури квантового гармонічного осцилятора успішно згенеровано.")
