# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Квантова статистика Бозе — Ейнштейна та бозе-конденсація'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_phase_space_microstates():
    """Фігура 1: Підрахунок мікростанів двох частинок у двох комірках для трьох статистик."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 25, "Мікростани 2 частинок у 2 квантових станках (комірках)", size=15, bold=True))

    col_w = 240
    gap = 20
    top_y = 55
    card_h = 360

    stats = [
        ("Класична статистика\nМаксвелла — Больцмана", "#f8fafc", "#475569", [
            ("Частинки розрізнювані (A, B)", "#334155"),
            ("Стан 1: [A, B] | [  ]", "50% обидві разом"),
            ("Стан 2: [  ] | [A, B]", ""),
            ("Стан 3: [ A ] | [ B ]", "50% окремо"),
            ("Стан 4: [ B ] | [ A ]", ""),
            ("Усього мікростанів: 4", "P(разом) = 2/4 = 50%"),
        ]),
        ("Квантова статистика\nБозе — Ейнштейна", "#f0fdf4", "#16a34a", [
            ("Частинки нерозрізнювані бозони (•, •)", "#15803d"),
            ("Стан 1: [ • • ] | [   ]", "66.7% обидві разом"),
            ("Стан 2: [   ] | [ • • ]", ""),
            ("Стан 3: [  •  ] | [  •  ]", "33.3% окремо"),
            (" ", ""),
            ("Усього мікростанів: 3", "P(разом) = 2/3 = 66.7%"),
        ]),
        ("Квантова статистика\nФермі — Дірака", "#fef2f2", "#dc2626", [
            ("Частинки ферміони (Паулі заборона)", "#b91c1c"),
            ("Заборонено: [ • • ] | [   ]", "0% разом!"),
            ("Заборонено: [   ] | [ • • ]", ""),
            ("Стан 1: [  •  ] | [  •  ]", "100% окремо"),
            (" ", ""),
            ("Усього мікростанів: 1", "P(разом) = 0%"),
        ]),
    ]

    for idx, (title, bg, border, content) in enumerate(stats):
        cx = 30 + idx * (col_w + gap)
        frags.append(rect(cx, top_y, col_w, card_h, fill=bg, stroke=border, sw=1.5, rx=8))

        lines_title = title.split("\n")
        frags.append(text(cx + col_w / 2, top_y + 22, lines_title[0], size=13, bold=True, color=border))
        frags.append(text(cx + col_w / 2, top_y + 40, lines_title[1], size=12, bold=True, color=border))
        frags.append(line(cx + 12, top_y + 50, cx + col_w - 12, top_y + 50, color=border, sw=1, dash="3,3"))

        frags.append(text(cx + col_w / 2, top_y + 70, content[0][0], size=11, bold=True, color=content[0][1]))

        # Render states
        for s_idx in range(1, 5):
            st_text, st_note = content[s_idx]
            sy = top_y + 105 + (s_idx - 1) * 45
            if st_text.strip():
                frags.append(rect(cx + 20, sy - 15, col_w - 40, 32, fill="#ffffff", stroke=LINE, sw=1, rx=4))
                frags.append(text(cx + col_w / 2, sy + 4, st_text, size=11.5, bold=True))
                if st_note:
                    frags.append(text(cx + col_w - 25, sy - 20, st_note, size=10.5, color=border, bold=True, anchor="end"))

        # Footer summary box
        summary_text, summary_prob = content[5]
        frags.append(rect(cx + 15, top_y + 285, col_w - 30, 60, fill="#ffffff", stroke=border, sw=1.5, rx=6))
        frags.append(text(cx + col_w / 2, top_y + 308, summary_text, size=12, bold=True, color=border))
        frags.append(text(cx + col_w / 2, top_y + 330, summary_prob, size=11, bold=True, color=border))

    render(os.path.join(IMG_DIR, "phase-space-microstates.svg"), w, h, *frags)


def build_fig2_bose_occupancy_comparison():
    """Фігура 2: Порівняння середніх чисел заповнення n(E) для трьох статистик."""
    w, h = 800, 440
    frags = []

    frags.append(text(w / 2, 25, "Середнє число заповнення n(ε) для трьох квантово-статистичних розподілів", size=15, bold=True))

    ox, oy = 85, 360
    graph_w, graph_h = 660, 290

    # Axes
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Енергетичний параметр (ε - μ) / (k_B · T)", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "Середнє число заповнення n(ε)", size=13, bold=True, anchor="middle"))

    # Horizontal asymptote n=1
    y_n1 = oy - (1.0 / 3.0) * graph_h
    frags.append(line(ox, y_n1, ox + graph_w, y_n1, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(ox - 10, y_n1 + 4, "1.0", size=11, anchor="end", color=MUTED))

    # Ticks on X axis (from 0.05 to 3.0)
    for i in range(7):
        val = i * 0.5
        x = ox + (val / 3.0) * graph_w
        frags.append(line(x, oy, x, oy + 6, color=LINE, sw=1.5))
        frags.append(text(x, oy + 22, f"{val:.1f}", size=11))

    N = 100
    be_pts = []
    mb_pts = []
    fd_pts = []

    for i in range(N):
        x_val = 0.04 + (i / float(N - 1)) * 2.96
        cx = ox + (x_val / 3.0) * graph_w

        # Bose-Einstein: 1 / (exp(x) - 1)
        be_val = 1.0 / (math.exp(x_val) - 1.0)
        cy_be = oy - (be_val / 3.0) * graph_h
        if cy_be >= oy - graph_h - 20:
            be_pts.append((cx, max(oy - graph_h - 10, cy_be)))

        # Maxwell-Boltzmann: exp(-x)
        mb_val = math.exp(-x_val)
        cy_mb = oy - (mb_val / 3.0) * graph_h
        mb_pts.append((cx, cy_mb))

        # Fermi-Dirac: 1 / (exp(x) + 1)
        fd_val = 1.0 / (math.exp(x_val) + 1.0)
        cy_fd = oy - (fd_val / 3.0) * graph_h
        fd_pts.append((cx, cy_fd))

    # Draw curves
    for i in range(len(be_pts) - 1):
        frags.append(line(be_pts[i][0], be_pts[i][1], be_pts[i + 1][0], be_pts[i + 1][1], color="#16a34a", sw=3))

    for i in range(len(mb_pts) - 1):
        frags.append(line(mb_pts[i][0], mb_pts[i][1], mb_pts[i + 1][0], mb_pts[i + 1][1], color="#475569", sw=2.5, dash="6,3"))

    for i in range(len(fd_pts) - 1):
        frags.append(line(fd_pts[i][0], fd_pts[i][1], fd_pts[i + 1][0], fd_pts[i + 1][1], color="#dc2626", sw=2.5, dash="3,2"))

    # Explanatory text boxes
    frags.append(textbox(ox + 200, oy - 265, "Бозе — Ейнштейн:\nn(ε) = 1 / [exp((ε-μ)/kT) - 1]\n(Розбіжність n → ∞ при ε → μ)", size=11, fill="#f0fdf4", stroke="#16a34a", sw=1.5)[0])

    frags.append(textbox(ox + 450, oy - 180, "Класичний Максвелл — Больцман:\nn(ε) = exp(-(ε-μ)/kT)\n(Межа низької густини)", size=11, fill="#f8fafc", stroke="#475569", sw=1.5)[0])

    frags.append(textbox(ox + 450, oy - 70, "Фермі — Дірак:\nn(ε) = 1 / [exp((ε-μ)/kT) + 1]\n(Обмеження Паулі n ≤ 1)", size=11, fill="#fef2f2", stroke="#dc2626", sw=1.5)[0])

    render(os.path.join(IMG_DIR, "bose-occupancy-comparison.svg"), w, h, *frags)


def build_fig3_bec_transition_condensation():
    """Фігура 3: Температурна залежність частки конденсату N0/N та теплової фази Nth/N."""
    w, h = 800, 440
    frags = []

    frags.append(text(w / 2, 25, "Фазовий перехід бозе-конденсації: частки N₀/N та N_th/N в ідеальному газі", size=15, bold=True))

    ox, oy = 85, 360
    graph_w, graph_h = 660, 290

    # Axes
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Відносна температура T / T_c", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "Відносна кількість частинок N_i / N", size=13, bold=True, anchor="middle"))

    # T_c vertical line
    x_tc = ox + (1.0 / 2.0) * graph_w
    frags.append(line(x_tc, oy, x_tc, oy - graph_h, color=NEG, sw=1.5, dash="4,4"))
    frags.append(text(x_tc, oy + 22, "1.0 (T_c)", size=11, bold=True, color=NEG))

    # Ticks on X axis
    for i in range(5):
        val = i * 0.5
        x = ox + (val / 2.0) * graph_w
        if abs(val - 1.0) > 0.01:
            frags.append(line(x, oy, x, oy + 6, color=LINE, sw=1.5))
            frags.append(text(x, oy + 22, f"{val:.1f}", size=11))

    # Y axis ticks (0 to 1)
    for i in range(5):
        val = i * 0.25
        y = oy - val * graph_h
        frags.append(line(ox - 6, y, ox, y, color=LINE, sw=1.5))
        frags.append(text(ox - 10, y + 4, f"{val:.2f}", size=11, anchor="end"))

    N = 100
    n0_pts = []
    nth_pts = []

    for i in range(N):
        t_rel = (i / float(N - 1)) * 2.0
        cx = ox + (t_rel / 2.0) * graph_w

        if t_rel <= 1.0:
            n0_val = 1.0 - (t_rel ** 1.5)
            nth_val = t_rel ** 1.5
        else:
            n0_val = 0.0
            nth_val = 1.0

        cy_n0 = oy - n0_val * graph_h
        cy_nth = oy - nth_val * graph_h

        n0_pts.append((cx, cy_n0))
        nth_pts.append((cx, cy_nth))

    # Draw curves
    for i in range(len(n0_pts) - 1):
        frags.append(line(n0_pts[i][0], n0_pts[i][1], n0_pts[i + 1][0], n0_pts[i + 1][1], color="#2563eb", sw=3))

    for i in range(len(nth_pts) - 1):
        frags.append(line(nth_pts[i][0], nth_pts[i][1], nth_pts[i + 1][0], nth_pts[i + 1][1], color="#d97706", sw=2.5, dash="6,3"))

    # Highlight point at T = 0 and T = T_c
    frags.append(circle(ox, oy - graph_h, 5, fill="#2563eb", stroke="#ffffff", sw=1.5))
    frags.append(circle(x_tc, oy, 5, fill="#2563eb", stroke="#ffffff", sw=1.5))

    # Annotations & text boxes positioned cleanly away from curves and vertical lines
    frags.append(textbox(ox + 40, oy - 275, "Бозе-конденсат (основний стан E₀ = 0):\nN₀ / N = 1 - (T / T_c)³ᐟ²   (при T ≤ T_c)\nN₀ / N = 0                (при T > T_c)", size=10.5, fill="#eff6ff", stroke="#2563eb", sw=1.5)[0])

    frags.append(textbox(ox + 440, oy - 250, "Теплова фаза (збуджені стани E > 0):\nN_th / N = (T / T_c)³ᐟ²   (при T ≤ T_c)\nN_th / N = 1.0            (при T > T_c)", size=10.5, fill="#fffbeb", stroke="#d97706", sw=1.5)[0])

    frags.append(textbox(ox + 440, oy - 140, "Критична температура T_c:\nЗламання похідної dN₀/dT\nМакроскопічна населеність E₀", size=10.5, fill="#fef2f2", stroke=NEG, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "bec-transition-condensation.svg"), w, h, *frags)


def build_fig4_chemical_potential_temperature():
    """Фігура 4: Температурна залежність хімічного потенціалу μ(T) для бозе-газу."""
    w, h = 800, 420
    frags = []

    frags.append(text(w / 2, 25, "Температурна залежність хімічного потенціалу μ(T) ідеального бозе-газу", size=15, bold=True))

    ox, oy = 85, 230
    graph_w, graph_h = 660, 160

    # Axes
    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))  # Zero line mu = 0
    frags.append(line(ox, oy - graph_h, ox, oy + 120, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 145, "Температура T / T_c", size=13, bold=True))
    frags.append(text(ox - 55, oy - 30, "Хімічний потенціал μ / (k_B · T_c)", size=13, bold=True, anchor="middle"))

    # T_c line
    x_tc = ox + (1.0 / 2.5) * graph_w
    frags.append(line(x_tc, oy - graph_h + 20, x_tc, oy + 110, color=NEG, sw=1.5, dash="4,4"))
    frags.append(text(x_tc, oy + 130, "1.0 (T_c)", size=11, bold=True, color=NEG))

    # Ticks on X axis
    for i in range(6):
        val = i * 0.5
        x = ox + (val / 2.5) * graph_w
        if abs(val - 1.0) > 0.01:
            frags.append(line(x, oy - 4, x, oy + 4, color=LINE, sw=1.5))
            frags.append(text(x, oy + 20, f"{val:.1f}", size=11))

    # Horizontal mu = 0 label
    frags.append(text(ox - 10, oy + 4, "0.0", size=11, anchor="end", bold=True))

    N = 100
    mu_pts = []

    for i in range(N):
        t_rel = (i / float(N - 1)) * 2.5
        cx = ox + (t_rel / 2.5) * graph_w

        if t_rel <= 1.0:
            mu_val = 0.0
        else:
            # Approximation for mu(T) above T_c: -1.1 * (t_rel - 1)^1.25
            mu_val = -1.1 * math.pow(t_rel - 1.0, 1.25)

        cy_mu = oy - mu_val * 70  # Since mu <= 0, cy_mu >= oy
        mu_pts.append((cx, cy_mu))

    # Draw curve
    for i in range(len(mu_pts) - 1):
        frags.append(line(mu_pts[i][0], mu_pts[i][1], mu_pts[i + 1][0], mu_pts[i + 1][1], color="#7c3aed", sw=3))

    # Highlight mu = 0 region for T <= T_c
    frags.append(line(ox, oy, x_tc, oy, color="#7c3aed", sw=4))
    frags.append(circle(x_tc, oy, 5, fill="#7c3aed", stroke="#ffffff", sw=1.5))

    # Annotations
    frags.append(textbox(ox + 50, oy - 90, "Нижче T_c (область конденсату):\nμ ≡ 0 (фіксація на рівні E₀ = 0)\nЧастинки вільно входять у condensate", size=10.5, fill="#f3e8ff", stroke="#7c3aed", sw=1.5)[0])

    frags.append(textbox(ox + 420, oy + 30, "Вище T_c (класична й вироджена фаза):\nμ < 0 (від'ємний хімічний потенціал)\nПри T >> T_c: μ/kT → -∞ (Максвелл — Больцман)", size=10.5, fill="#f8fafc", stroke=LINE, sw=1.2)[0])

    render(os.path.join(IMG_DIR, "chemical-potential-temperature.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_phase_space_microstates()
    build_fig2_bose_occupancy_comparison()
    build_fig3_bec_transition_condensation()
    build_fig4_chemical_potential_temperature()
    print("Фігури для статистики Бозе — Ейнштейна успішно згенеровано.")
