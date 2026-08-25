# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Співвідношення взаємності Онсагера у нерівноважній термодинаміці'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_coupled_matrix():
    """Фігура 1: Матриця кінетичних коефіцієнтів L_ij та симетрія взаємності Онсагера."""
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Матриця феноменологічних коефіцієнтів L_ij та перехресні ефекти", size=16, bold=True))

    # Matrix structure layout
    ox, oy = 50, 65
    box_w, box_h = 240, 105
    gap_x, gap_y = 18, 16

    headers_col = [
        "Сила X_q = ∇(1/T)\n(Градієнт температури)",
        "Сила X_e = −∇(φ/T)\n(Градієнт потенціалу)",
        "Сила X_m = −∇(μ/T)\n(Градієнт концентрації)"
    ]

    headers_row = [
        "Потік тепла J_q",
        "Потік заряду J_e",
        "Потік маси J_m"
    ]

    # Draw Column Headers
    for j in range(3):
        cx = ox + 170 + j * (box_w + gap_x) + box_w / 2
        lines = headers_col[j].split("\n")
        frags.append(rect(ox + 170 + j * (box_w + gap_x), oy, box_w, 45, fill="#e2e8f0", stroke="#475569", sw=1.5))
        frags.append(text(cx, oy + 18, lines[0], size=12, bold=True, color="#1e293b"))
        frags.append(text(cx, oy + 34, lines[1], size=10.5, color="#475569"))

    # Matrix content
    cells = [
        [
            ("L_qq: Теплопровідність", "Прямий ефект Фур'є\nJ_q = L_qq · X_q", "#f1f5f9", "#475569"),
            ("L_qe: Ефект Пельтьє", "Струм створює потік тепла\nJ_q = L_qe · X_e", "#fef3c7", "#d97706"),
            ("L_qm: Ефект Дюфура", "Дифузія створює потік тепла\nJ_q = L_qm · X_m", "#e0e7ff", "#4338ca")
        ],
        [
            ("L_eq: Ефект Зеебека", "Градієнт T генерує ЕРС\nJ_e = L_eq · X_q", "#fef3c7", "#d97706"),
            ("L_ee: Електропровідність", "Прямий закон Ома\nJ_e = L_ee · X_e", "#f1f5f9", "#475569"),
            ("L_em: Електроосмос", "Поле переносить рідину\nJ_e = L_em · X_m", "#dcfce7", "#15803d")
        ],
        [
            ("L_mq: Ефект Соре", "Градієнт T викликає поділ\nJ_m = L_mq · X_q", "#e0e7ff", "#4338ca"),
            ("L_me: Потенціал протікання", "Тиск генерує потенціал\nJ_m = L_me · X_e", "#dcfce7", "#15803d"),
            ("L_mm: Молекулярна дифузія", "Прямий закон Фіка\nJ_m = L_mm · X_m", "#f1f5f9", "#475569")
        ]
    ]

    for i in range(3):
        ry = oy + 55 + i * (box_h + gap_y)
        # Row Header
        frags.append(rect(ox, ry, 155, box_h, fill="#cbd5e1", stroke="#475569", sw=1.5))
        frags.append(text(ox + 77.5, ry + box_h / 2 + 4, headers_row[i], size=13, bold=True, color="#0f172a"))

        for j in range(3):
            rx = ox + 170 + j * (box_w + gap_x)
            title, desc, bg, border = cells[i][j]

            frags.append(rect(rx, ry, box_w, box_h, fill=bg, stroke=border, sw=1.8 if i != j else 1.2, rx=6))
            frags.append(text(rx + box_w / 2, ry + 24, title, size=12.5, bold=True, color=border))
            frags.append(line(rx + 10, ry + 36, rx + box_w - 10, ry + 36, color=border, sw=1, dash="2,2"))

            d_lines = desc.split("\n")
            frags.append(text(rx + box_w / 2, ry + 56, d_lines[0], size=11, color="#334155"))
            frags.append(text(rx + box_w / 2, ry + 74, d_lines[1], size=11, bold=True, color="#0f172a"))

    # Symmetry note box at bottom
    frags.append(rect(ox, oy + 55 + 3 * (box_h + gap_y) - 5, w - 2 * ox, 32, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=4))
    frags.append(text(w / 2, oy + 55 + 3 * (box_h + gap_y) + 16,
                      "Теорема Онсагера стверджує симетрію перехресних коефіцієнтів: L_qe = L_eq ,  L_qm = L_mq ,  L_em = L_me",
                      size=12.5, bold=True, color="#1e40af"))

    render(os.path.join(IMG_DIR, "coupled-phenomena-matrix.svg"), w, h, *frags)


def build_fig2_fluctuation_relaxation():
    """Фігура 2: Флуктуації в рівновазі та гіпотеза регресії Онсагера."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 25, "Мікроскопічна мікрореверсивність та макроскопічний релаксаційний згасальний потік", size=15, bold=True))

    # Left Box: Microscopic Fluctuation Symmetry
    frags.append(rect(30, 50, 365, 335, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(212.5, 75, "Мікроскопічні флуктуації в рівновазі", size=13, bold=True, color="#1e293b"))
    frags.append(text(212.5, 93, "Часова симетрія: <α_i(0) α_j(t)> = <α_i(t) α_j(0)>", size=11, color="#475569"))

    # Graph 1 Axes
    ox1, oy1 = 70, 330
    gw1, gh1 = 300, 200
    frags.append(line(ox1, oy1, ox1 + gw1, oy1, color=LINE, sw=1.5))
    frags.append(line(ox1, oy1 - gh1 / 2, ox1, oy1 - gh1, color=LINE, sw=1.5))
    frags.append(line(ox1, oy1 - gh1 / 2, ox1 + gw1, oy1 - gh1 / 2, color="#94a3b8", sw=1, dash="3,3"))

    frags.append(text(ox1 + gw1 - 10, oy1 + 22, "Час t", size=11))
    frags.append(text(ox1 - 25, oy1 - gh1 + 10, "α_i(t)", size=11, anchor="end"))

    # Plot fluctuating curve
    pts1 = []
    for step in range(60):
        t_val = step / 59.0
        x_p = ox1 + t_val * gw1
        # Random-looking symmetric fluctuation waveform
        y_val = math.sin(t_val * 4 * math.pi) * math.cos(t_val * 7 * math.pi) * 60
        pts1.append((x_p, oy1 - gh1 / 2 - y_val))

    for k in range(len(pts1) - 1):
        frags.append(line(pts1[k][0], pts1[k][1], pts1[k + 1][0], pts1[k + 1][1], color="#2563eb", sw=1.8))

    frags.append(text(212.5, 365, "Симетрія за інверсії часу (t ↔ −t)", size=11.5, bold=True, color="#1e40af"))

    # Right Box: Macroscopic Relaxation
    frags.append(rect(425, 50, 365, 335, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(607.5, 75, "Гіпотеза регресії Онсагера", size=13, bold=True, color="#1e293b"))
    frags.append(text(607.5, 93, "Згасання флуктуації підпорядковане закону: dα_i/dt = ∑ L_ik X_k", size=10.5, color="#475569"))

    # Graph 2 Axes
    ox2, oy2 = 465, 330
    gw2, gh2 = 300, 200
    frags.append(line(ox2, oy2, ox2 + gw2, oy2, color=LINE, sw=1.5))
    frags.append(line(ox2, oy2, ox2, oy2 - gh2, color=LINE, sw=1.5))

    frags.append(text(ox2 + gw2 - 10, oy2 + 22, "Час t", size=11))
    frags.append(text(ox2 - 25, oy2 - gh2 + 10, "<α_i(t)>", size=11, anchor="end"))

    # Plot macroscopic exponential decay curve
    pts2 = []
    for step in range(60):
        t_val = step / 59.0
        x_p = ox2 + t_val * gw2
        y_val = (gh2 - 20) * math.exp(-t_val * 4.0)
        pts2.append((x_p, oy2 - y_val))

    for k in range(len(pts2) - 1):
        frags.append(line(pts2[k][0], pts2[k][1], pts2[k + 1][0], pts2[k + 1][1], color="#dc2626", sw=2.2))

    # Dashed line showing initial slope (flux J = L * X)
    frags.append(line(ox2, oy2 - (gh2 - 20), ox2 + 80, oy2 - (gh2 - 20) + 80 * 4.0 * (gh2 - 20) / gw2, color="#991b1b", sw=1.2, dash="4,4"))
    frags.append(text(ox2 + 100, oy2 - 120, "Початкова швидкість = L_ij · X_j", size=11, color="#991b1b", bold=True))

    frags.append(text(607.5, 365, "Макроскопічне згасання збігається з феноменологією", size=11.5, bold=True, color="#991b1b"))

    render(os.path.join(IMG_DIR, "onsager-fluctuation-relaxation.svg"), w, h, *frags)


def build_fig3_thermoelectric_scheme():
    """Фігура 3: Схема термоелектричних ефектів Зеебека та Пельтьє."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 25, "Зв'язок ефектів Зеебека та Пельтьє через співвідношення Онсагера", size=15, bold=True))

    # Main Conductive Leg Box
    leg_x, leg_y = 160, 100
    leg_w, leg_h = 500, 140

    frags.append(rect(leg_x, leg_y, leg_w, leg_h, fill="#f8fafc", stroke="#334155", sw=2, rx=6))

    # Temperature reservoirs on sides
    frags.append(rect(50, leg_y - 15, 110, leg_h + 30, fill="#fee2e2", stroke="#ef4444", sw=2, rx=8))
    frags.append(text(105, leg_y + leg_h / 2 - 10, "Гарячий контакт", size=12, bold=True, color="#991b1b"))
    frags.append(text(105, leg_y + leg_h / 2 + 10, "T_hot = T + ΔT", size=12.5, bold=True, color="#b91c1c"))

    frags.append(rect(leg_x + leg_w, leg_y - 15, 110, leg_h + 30, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=8))
    frags.append(text(leg_x + leg_w + 55, leg_y + leg_h / 2 - 10, "Холодний контакт", size=12, bold=True, color="#1e3a8a"))
    frags.append(text(leg_x + leg_w + 55, leg_y + leg_h / 2 + 10, "T_cold = T", size=12.5, bold=True, color="#1d4ed8"))

    # Vector arrows inside leg
    # Heat flux vector J_q
    frags.append(arrow(leg_x + 40, leg_y + 40, leg_x + leg_w - 40, leg_y + 40, color="#dc2626", sw=2.5))
    frags.append(text(leg_x + leg_w / 2, leg_y + 25, "Потік тепла J_q = L_qq · ∇(1/T) + L_qe · (−∇φ/T)", size=11.5, bold=True, color="#991b1b"))

    # Electric current vector J_e
    frags.append(arrow(leg_x + 40, leg_y + 100, leg_x + leg_w - 40, leg_y + 100, color="#2563eb", sw=2.5))
    frags.append(text(leg_x + leg_w / 2, leg_y + 118, "Потік заряду J_e = L_eq · ∇(1/T) + L_ee · (−∇φ/T)", size=11.5, bold=True, color="#1e40af"))

    # Two effect boxes below
    box_w = 340
    box_h = 130

    # Box Left: Seebeck Effect
    frags.append(rect(50, 280, box_w, box_h, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(50 + box_w / 2, 305, "Ефект Зеебека (термо-ЕРС)", size=13, bold=True, color="#b45309"))
    frags.append(text(50 + box_w / 2, 328, "Градієнт ∇T породжує різницю потенціалів ΔV", size=11, color="#78350f"))
    frags.append(text(50 + box_w / 2, 350, "Коефіцієнт Зеебека: S = ΔV / ΔT = L_eq / (T · L_ee)", size=11.5, bold=True, color="#92400e"))

    # Box Right: Peltier Effect
    frags.append(rect(430, 280, box_w, box_h, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=6))
    frags.append(text(430 + box_w / 2, 305, "Ефект Пельтьє (теплоперенос струмом)", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(430 + box_w / 2, 328, "Струм I виділяє/поглинає тепло Q_Peltier на контакті", size=11, color="#1e3a8a"))
    frags.append(text(430 + box_w / 2, 350, "Коефіцієнт Пельтьє: Π = Q_Peltier / I = L_qe / L_ee", size=11.5, bold=True, color="#1e40af"))

    # Connecting formula bar at the very bottom
    frags.append(rect(50, 415, w - 100, 22, fill="#f1f5f9", stroke="#475569", sw=1, rx=3))
    frags.append(text(w / 2, 430, "Взаємність Онсагера L_qe = L_eq  ⇒  Співвідношення Кельвіна: Π = T · S", size=11.5, bold=True, color="#0f172a"))

    render(os.path.join(IMG_DIR, "thermoelectric-coupling-scheme.svg"), w, h, *frags)


if __name__ == '__main__':
    build_fig1_coupled_matrix()
    build_fig2_fluctuation_relaxation()
    build_fig3_thermoelectric_scheme()
    print("Всі фігури для onsager-reciprocal-relations успішно згенеровано.")
