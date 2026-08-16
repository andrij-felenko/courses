# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Теорема рівнорозподілу енергії'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_dof_partition():
    """Фігура 1: Розподіл енергії ½ kT за ступенями вільності двоатомної молекули."""
    w, h = 820, 390
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Розподіл енергії ½ kT за ступенями вільності двоатомної молекули", size=16, bold=True))

    # Лівий блок: Поступальний рух (3 ступені)
    b1_x, b1_y, b1_w, b1_h = 30, 55, 235, 275
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 25, "Поступальні (3)", size=14, bold=True, color=POS))
    frags.append(line(b1_x + 15, b1_y + 35, b1_x + b1_w - 15, b1_y + 35, color=MUTED, sw=1, dash="3,3"))

    # Схематичний рисунок поступального руху
    frags.append(circle(b1_x + 70, b1_y + 90, 14, fill="#e2e8f0", stroke=POS, sw=2))
    frags.append(circle(b1_x + 110, b1_y + 90, 14, fill="#e2e8f0", stroke=POS, sw=2))
    frags.append(line(b1_x + 84, b1_y + 90, b1_x + 96, b1_y + 90, color=LINE, sw=3))
    # Стрілки напрямків X, Y, Z
    frags.append(arrow(b1_x + 90, b1_y + 90, b1_x + 160, b1_y + 90, color=POS, sw=2))
    frags.append(text(b1_x + 165, b1_y + 93, "v_x", size=12, color=POS, bold=True))
    frags.append(arrow(b1_x + 90, b1_y + 90, b1_x + 90, b1_y + 50, color=POS, sw=2))
    frags.append(text(b1_x + 90, b1_y + 42, "v_y", size=12, color=POS, bold=True))
    frags.append(arrow(b1_x + 90, b1_y + 90, b1_x + 50, b1_y + 120, color=POS, sw=2))
    frags.append(text(b1_x + 42, b1_y + 130, "v_z", size=12, color=POS, bold=True))

    frags.append(textbox(b1_x + b1_w / 2, b1_y + 175, "½ m v_x² → ½ k_B T\n½ m v_y² → ½ k_B T\n½ m v_z² → ½ k_B T", size=12, fill="#ffffff", stroke=POS, sw=1.2)[0])
    frags.append(textbox(b1_x + b1_w / 2, b1_y + 245, "Разом: 3 × ½ k_B T = 1.5 k_B T", size=12, bold=True, fill="#fee2e2", stroke=POS, sw=1.5)[0])

    # Середній блок: Обертальний рух (2 ступені)
    b2_x, b2_y, b2_w, b2_h = 290, 55, 240, 275
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 25, "Обертальні (2)", size=14, bold=True, color=NEG))
    frags.append(line(b2_x + 15, b2_y + 35, b2_x + b2_w - 15, b2_y + 35, color=MUTED, sw=1, dash="3,3"))

    # Схематичний рисунок обертання
    frags.append(circle(b2_x + 80, b2_y + 90, 14, fill="#e2e8f0", stroke=NEG, sw=2))
    frags.append(circle(b2_x + 160, b2_y + 90, 14, fill="#e2e8f0", stroke=NEG, sw=2))
    frags.append(line(b2_x + 94, b2_y + 90, b2_x + 146, b2_y + 90, color=LINE, sw=3))
    frags.append(line(b2_x + 120, b2_y + 50, b2_x + 120, b2_y + 130, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(b2_x + 120, b2_y + 43, "вісь 1", size=11, color=MUTED))
    frags.append(text(b2_x + 190, b2_y + 93, "ω_x, ω_y", size=12, color=NEG, bold=True))

    frags.append(textbox(b2_x + b2_w / 2, b2_y + 175, "½ I_x ω_x² → ½ k_B T\n½ I_y ω_y² → ½ k_B T\n(вздовж осі z: I_z ≈ 0)", size=12, fill="#ffffff", stroke=NEG, sw=1.2)[0])
    frags.append(textbox(b2_x + b2_w / 2, b2_y + 245, "Разом: 2 × ½ k_B T = 1.0 k_B T", size=12, bold=True, fill="#dbeafe", stroke=NEG, sw=1.5)[0])

    # Правий блок: Коливальний рух (2 квадратичні терми)
    b3_x, b3_y, b3_w, b3_h = 555, 55, 235, 275
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b3_x + b3_w / 2, b3_y + 25, "Коливальні (2)", size=14, bold=True, color=FIELD))
    frags.append(line(b3_x + 15, b3_y + 35, b3_x + b3_w - 15, b3_y + 35, color=MUTED, sw=1, dash="3,3"))

    # Схематичний рисунок пружинки
    frags.append(circle(b3_x + 65, b3_y + 90, 14, fill="#e2e8f0", stroke=FIELD, sw=2))
    frags.append(circle(b3_x + 170, b3_y + 90, 14, fill="#e2e8f0", stroke=FIELD, sw=2))
    px = b3_x + 79
    py = b3_y + 90
    pts = [(px, py), (px + 10, py - 8), (px + 20, py + 8), (px + 30, py - 8), (px + 40, py + 8), (px + 50, py - 8), (px + 60, py + 8), (px + 70, py + 0), (px + 77, py)]
    for i in range(len(pts) - 1):
        frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=FIELD, sw=2))

    frags.append(textbox(b3_x + b3_w / 2, b3_y + 175, "½ μ v_колеб² → ½ k_B T  (кін)\n½ k r²       → ½ k_B T  (пот)", size=12, fill="#ffffff", stroke=FIELD, sw=1.2)[0])
    frags.append(textbox(b3_x + b3_w / 2, b3_y + 245, "Разом: 2 × ½ k_B T = 1.0 k_B T", size=12, bold=True, fill="#dcfce7", stroke=FIELD, sw=1.5)[0])

    # Загальний підсумок знизу
    frags.append(textbox(w / 2, 360, "Повна класична середня енергія молекули: (3 + 2 + 2) × ½ k_B T = 3.5 k_B T", size=13, bold=True, fill="#f1f5f9", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "dof-partition.svg"), w, h, *frags)


def build_fig2_heat_capacity_quantum():
    """Фігура 2: Залежність молярної теплоємності C_V(T) двоатомного газу H₂ від температури (квантове виморожування)."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 26, "Залежність молярної теплоємності C_V двоатомного газу (H₂) від температури", size=15, bold=True))

    ox, oy = 80, 350
    graph_w, graph_h = 630, 270

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 42, "Температура T (логарифмічна шкала, К)", size=13, bold=True))
    frags.append(text(ox - 50, oy - graph_h / 2, "C_V / R", size=14, bold=True, anchor="middle"))

    y_3_2 = oy - graph_h * (1.5 / 4.0)
    y_5_2 = oy - graph_h * (2.5 / 4.0)
    y_7_2 = oy - graph_h * (3.5 / 4.0)

    frags.append(line(ox - 5, y_3_2, ox + graph_w, y_3_2, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(ox - 5, y_5_2, ox + graph_w, y_5_2, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(ox - 5, y_7_2, ox + graph_w, y_7_2, color=MUTED, sw=1, dash="3,3"))

    frags.append(text(ox - 15, y_3_2 + 4, "3/2 R", size=12, color=POS, bold=True, anchor="end"))
    frags.append(text(ox - 15, y_5_2 + 4, "5/2 R", size=12, color=NEG, bold=True, anchor="end"))
    frags.append(text(ox - 15, y_7_2 + 4, "7/2 R", size=12, color=FIELD, bold=True, anchor="end"))

    def x_from_T(T):
        log_T = math.log10(max(T, 5.0))
        frac = (log_T - 1.0) / 3.0
        return ox + frac * graph_w

    x_10 = x_from_T(10)
    x_85 = x_from_T(85)
    x_300 = x_from_T(300)
    x_3000 = x_from_T(3000)

    frags.append(line(x_10, oy, x_10, oy + 6, color=LINE, sw=1.5))
    frags.append(text(x_10, oy + 20, "10 K", size=11))

    frags.append(line(x_85, oy, x_85, oy + 6, color=LINE, sw=1.5))
    frags.append(line(x_85, oy, x_85, oy - graph_h, color=NEG, sw=1, dash="4,4"))
    frags.append(text(x_85, oy + 20, "85 K", size=11, color=NEG, bold=True))
    frags.append(text(x_85, oy - graph_h + 15, "T_rot", size=11, color=NEG, bold=True))

    frags.append(line(x_300, oy, x_300, oy + 6, color=LINE, sw=1.5))
    frags.append(text(x_300, oy + 20, "300 K (кімнатна)", size=11))

    frags.append(line(x_3000, oy, x_3000, oy + 6, color=LINE, sw=1.5))
    frags.append(line(x_3000, oy, x_3000, oy - graph_h, color=FIELD, sw=1, dash="4,4"))
    frags.append(text(x_3000, oy + 20, "3000 K", size=11, color=FIELD, bold=True))

    curve_pts = []
    T_list = [10, 20, 40, 60, 85, 120, 200, 300, 500, 800, 1200, 2000, 3000, 5000, 8000]
    for T in T_list:
        cx = x_from_T(T)
        val = 1.5 + 1.0 / (1.0 + math.exp(-(math.log(T) - math.log(85)) * 2.2)) + 1.0 / (1.0 + math.exp(-(math.log(T) - math.log(3000)) * 2.0))
        cy = oy - graph_h * (val / 4.0)
        curve_pts.append((cx, cy))

    for i in range(len(curve_pts) - 1):
        frags.append(line(curve_pts[i][0], curve_pts[i][1], curve_pts[i+1][0], curve_pts[i+1][1], color=POS, sw=3))

    frags.append(textbox(x_from_T(25), y_3_2 - 30, "Лише поступальний рух\n(обертання й коливання заморожені)", size=10.5, fill="#fee2e2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(x_from_T(500), y_5_2 - 30, "Поступальний + Обертальний\n(класична кімнатна зона)", size=10.5, fill="#dbeafe", stroke=NEG, sw=1.2)[0])
    frags.append(textbox(x_from_T(4500), y_7_2 - 25, "Поступальний + Обертальний + Коливальний\n(повний класичний рівнорозподіл)", size=10, fill="#dcfce7", stroke=FIELD, sw=1.2)[0])

    render(os.path.join(IMG_DIR, "heat-capacity-quantum.svg"), w, h, *frags)


def build_fig3_rayleigh_jeans_catastrophe():
    """Фігура 3: Ультрафіолетова катастрофа — розходження класичного рівнорозподілу з квантовим законом Планка."""
    w, h = 780, 420
    frags = []

    frags.append(text(w / 2, 26, "Ультрафіолетова катастрофа: класичний рівнорозподіл проти закону Планка", size=15, bold=True))

    ox, oy = 80, 360
    graph_w, graph_h = 650, 290

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=2))

    frags.append(text(ox + graph_w / 2, oy + 38, "Частота випромінювання ν (або 1/λ)", size=13, bold=True))
    frags.append(text(ox - 45, oy - graph_h / 2, "Спектральна густина енергії u(ν)", size=13, bold=True, anchor="middle"))

    x_uv = ox + graph_w * 0.58
    # Тло UV зони без рамок, щоб не конфліктувати з розрахунком solid boxes
    frags.append(line(x_uv, oy, x_uv, oy - graph_h, color="#c084fc", sw=1.5, dash="4,4"))
    frags.append(text(x_uv + 70, oy - graph_h + 20, "Ультрафіолетова область (високі частоти)", size=11, color="#7e22ce", bold=True))

    # Класична парабола Релея-Джинса
    rj_pts = []
    N = 40
    for i in range(N):
        nu = (i / float(N - 1)) * 1.25
        cx = ox + (nu / 1.25) * (graph_w * 0.52)
        cy = oy - graph_h * (0.85 * nu * nu)
        if cy >= oy - graph_h:
            rj_pts.append((cx, cy))

    for i in range(len(rj_pts) - 1):
        frags.append(line(rj_pts[i][0], rj_pts[i][1], rj_pts[i+1][0], rj_pts[i+1][1], color=POS, sw=3, dash="6,4"))

    # Квантова крива Планка
    planck_pts = []
    for i in range(N):
        nu = (i / float(N - 1)) * 2.8
        cx = ox + (i / float(N - 1)) * graph_w
        if nu == 0:
            val = 0
        else:
            val = (nu**3) / (math.exp(nu) - 1.0)
        cy = oy - graph_h * (val / 1.42)
        planck_pts.append((cx, cy))

    for i in range(len(planck_pts) - 1):
        frags.append(line(planck_pts[i][0], planck_pts[i][1], planck_pts[i+1][0], planck_pts[i+1][1], color=NEG, sw=3))

    frags.append(textbox(ox + 180, oy - 240, "Класичний рівнорозподіл (Релей-Джинс):\nu(ν) ∝ ν² k_B T  →  ∞ (Катастрофа!)", size=11.5, fill="#fee2e2", stroke=POS, sw=1.5)[0])
    frags.append(textbox(ox + 460, oy - 110, "Квантовий закон Планка:\nh ν >> k_B T  →  виморожування мод", size=11.5, fill="#dbeafe", stroke=NEG, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "rayleigh-jeans-catastrophe.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_dof_partition()
    build_fig2_heat_capacity_quantum()
    build_fig3_rayleigh_jeans_catastrophe()
    print("Фігури успішно згенеровано у", IMG_DIR)
