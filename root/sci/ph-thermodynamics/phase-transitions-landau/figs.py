# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Теорія фазових переходів другого роду Ландау'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def polyline(pts, color=LINE, sw=1.5, fill="none", dash=None):
    pt_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (pt_str, fill, color, sw, d)


def build_fig1_landau_potential_wells():
    """Фігура 1: Термодинамічний потенціал Ландау Ф(T, η) при різних температурах."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 25, "Термодинамічний потенціал Ландау Ф(T, η) при різній температурі", size=15, bold=True))

    ox, oy = 410, 360

    # Draw grid lines
    for y_val in range(100, 361, 50):
        frags.append(line(70, y_val, 750, y_val, color="#e2e8f0", sw=1, dash="2,2"))

    # Axes
    frags.append(line(70, oy, 750, oy, color=LINE, sw=2))  # Horizontal axis (eta)
    frags.append(line(ox, oy + 20, ox, 60, color=LINE, sw=2))  # Vertical axis (Phi)

    frags.append(text(750, oy + 25, "Параметр порядку η", size=12, bold=True, anchor="end"))
    frags.append(text(ox + 15, 65, "Термодинамічний потенціал Ф(T, η)", size=12, bold=True))

    def eta_to_x(eta):
        return ox + eta * 140

    def phi_to_y(phi):
        return oy - phi * 120

    # 1. T > Tc: a = +0.6, b = 0.5
    pts_above = []
    for i in range(-110, 111):
        e = i / 50.0
        p = 0.6 * (e ** 2) + 0.25 * (e ** 4)
        pts_above.append((eta_to_x(e), phi_to_y(p)))
    frags.append(polyline(pts_above, color="#16a34a", sw=2.5))

    # 2. T = Tc: a = 0, b = 0.5
    pts_tc = []
    for i in range(-115, 116):
        e = i / 50.0
        p = 0.25 * (e ** 4)
        pts_tc.append((eta_to_x(e), phi_to_y(p)))
    frags.append(polyline(pts_tc, color="#d97706", sw=2.5, dash="6,3"))

    # 3. T < Tc: a = -0.7, b = 0.5
    pts_below = []
    for i in range(-125, 126):
        e = i / 50.0
        p = -0.7 * (e ** 2) + 0.25 * (e ** 4)
        pts_below.append((eta_to_x(e), phi_to_y(p)))
    frags.append(polyline(pts_below, color="#2563eb", sw=3))

    # Mark minima for T < Tc
    e0 = math.sqrt(1.4)
    x_m1, y_m1 = eta_to_x(-e0), phi_to_y(-0.49)
    x_m2, y_m2 = eta_to_x(e0), phi_to_y(-0.49)

    frags.append(circle(x_m1, y_m1, 5, fill="#2563eb", stroke="#ffffff", sw=1.5))
    frags.append(circle(x_m2, y_m2, 5, fill="#2563eb", stroke="#ffffff", sw=1.5))
    frags.append(circle(ox, oy, 5, fill="#dc2626", stroke="#ffffff", sw=1.5))

    # Dashed lines to minima
    frags.append(line(x_m1, oy, x_m1, y_m1, color="#2563eb", sw=1, dash="3,3"))
    frags.append(line(x_m2, oy, x_m2, y_m2, color="#2563eb", sw=1, dash="3,3"))

    frags.append(text(x_m1, oy + 20, "-η₀", size=12, bold=True, color="#2563eb"))
    frags.append(text(x_m2, oy + 20, "+η₀", size=12, bold=True, color="#2563eb"))

    # Labels and Legend box
    leg_x, leg_y = 520, 75
    frags.append(rect(leg_x, leg_y, 220, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))

    frags.append(line(leg_x + 15, leg_y + 25, leg_x + 45, leg_y + 25, color="#16a34a", sw=2.5))
    frags.append(text(leg_x + 55, leg_y + 29, "T > T꜀  (a > 0, η = 0 стійкий)", size=11, bold=True, color="#16a34a", anchor="start"))

    frags.append(line(leg_x + 15, leg_y + 55, leg_x + 45, leg_y + 55, color="#d97706", sw=2.5, dash="6,3"))
    frags.append(text(leg_x + 55, leg_y + 59, "T = T꜀  (a = 0, пласке дно)", size=11, bold=True, color="#d97706", anchor="start"))

    frags.append(line(leg_x + 15, leg_y + 85, leg_x + 45, leg_y + 85, color="#2563eb", sw=3))
    frags.append(text(leg_x + 55, leg_y + 89, "T < T꜀  (a < 0, дві ями ±η₀)", size=11, bold=True, color="#2563eb", anchor="start"))

    # Extra annotations
    frags.append(text(ox + 10, oy - 15, "0", size=11, bold=True))
    frags.append(text(ox - 130, 240, "Нестійкий максимум при η=0", size=10.5, color="#dc2626", bold=True, anchor="middle"))
    frags.append(line(ox - 60, 245, ox - 10, oy - 5, color="#dc2626", sw=1, dash="2,2"))

    render(os.path.join(IMG_DIR, "landau-potential-wells.svg"), w, h, *frags)


def build_fig2_order_parameter_heat_capacity():
    """Фігура 2: Залежність параметра порядку η(T) та теплоємності C_p(T) від температури."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 25, "Температурна залежність параметра порядку η(T) та стрибок теплоємності ΔC_p", size=15, bold=True))

    # Left plot: eta(T)
    ox1, oy1 = 75, 350
    pw, ph = 320, 260

    frags.append(rect(ox1 - 10, oy1 - ph - 10, pw + 30, ph + 50, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(ox1 + pw / 2, oy1 - ph + 15, "Параметр порядку η(T)", size=13, bold=True, color="#1e293b"))

    frags.append(line(ox1, oy1, ox1 + pw, oy1, color=LINE, sw=2))
    frags.append(line(ox1, oy1, ox1, oy1 - ph + 25, color=LINE, sw=2))

    tc_x1 = ox1 + pw * 0.65

    # Grid line at Tc
    frags.append(line(tc_x1, oy1, tc_x1, oy1 - ph + 25, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(text(tc_x1, oy1 + 22, "T꜀", size=12, bold=True, color="#dc2626"))
    frags.append(text(ox1 + pw - 10, oy1 + 22, "Температура T", size=11, bold=True, anchor="end"))
    frags.append(text(ox1 - 15, oy1 - ph + 35, "η", size=12, bold=True))

    pts_eta = []
    steps = 80
    for i in range(steps + 1):
        tx = ox1 + (pw * i / steps)
        if tx > tc_x1:
            eta_val = 0
        else:
            rel_t = (tc_x1 - tx) / (tc_x1 - ox1)
            eta_val = math.sqrt(rel_t)
        ty = oy1 - eta_val * (ph - 60)
        pts_eta.append((tx, ty))

    frags.append(polyline(pts_eta, color="#2563eb", sw=3))
    frags.append(text(ox1 + 100, oy1 - 140, "η ~ (T꜀ - T)¹ᐟ²", size=12, bold=True, color="#2563eb", anchor="middle"))

    # Right plot: Cp(T)
    ox2, oy2 = 475, 350

    frags.append(rect(ox2 - 10, oy2 - ph - 10, pw + 30, ph + 50, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(ox2 + pw / 2, oy2 - ph + 15, "Теплоємність Cₚ(T)", size=13, bold=True, color="#1e293b"))

    frags.append(line(ox2, oy2, ox2 + pw, oy2, color=LINE, sw=2))
    frags.append(line(ox2, oy2, ox2, oy2 - ph + 25, color=LINE, sw=2))

    tc_x2 = ox2 + pw * 0.65

    frags.append(line(tc_x2, oy2, tc_x2, oy2 - ph + 25, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(text(tc_x2, oy2 + 22, "T꜀", size=12, bold=True, color="#dc2626"))
    frags.append(text(ox2 + pw - 10, oy2 + 22, "Температура T", size=11, bold=True, anchor="end"))
    frags.append(text(ox2 - 15, oy2 - ph + 35, "Cₚ", size=12, bold=True))

    pts_cp_below = []
    pts_cp_above = []

    for i in range(steps + 1):
        tx = ox2 + (pw * i / steps)
        base_y = oy2 - 40 - (tx - ox2) * 0.15
        if tx < tc_x2:
            jump_y = base_y - 90 - (tc_x2 - tx) * 0.1
            pts_cp_below.append((tx, jump_y))
        else:
            pts_cp_above.append((tx, base_y))

    frags.append(polyline(pts_cp_below, color="#16a34a", sw=3))
    frags.append(polyline(pts_cp_above, color="#16a34a", sw=3))

    y_jump_top = oy2 - 40 - (tc_x2 - ox2) * 0.15 - 90
    y_jump_bot = oy2 - 40 - (tc_x2 - ox2) * 0.15
    frags.append(line(tc_x2, y_jump_top, tc_x2, y_jump_bot, color="#16a34a", sw=2, dash="3,3"))

    frags.append(circle(tc_x2, y_jump_top, 4, fill="#16a34a", stroke="#ffffff", sw=1.5))
    frags.append(circle(tc_x2, y_jump_bot, 4, fill="#ffffff", stroke="#16a34a", sw=1.5))

    # Delta Cp label placed safely to the right of vertical line without touching
    frags.append(text(tc_x2 + 12, (y_jump_top + y_jump_bot) / 2 + 4, "ΔCₚ = a₀² T꜀ / b", size=11, bold=True, color="#dc2626", anchor="start"))

    render(os.path.join(IMG_DIR, "order-parameter-heat-capacity.svg"), w, h, *frags)


def build_fig3_phase_diagram_first_second_order():
    """Фігура 3: Порівняння фазових переходів першого та другого роду."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 25, "Порівняльна характеристика фазових переходів 1-го та 2-го роду", size=15, bold=True))

    box_w = 370
    box_h = 340
    top_y = 55

    # 1-st order box
    bx1 = 30
    frags.append(rect(bx1, top_y, box_w, box_h, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=8))
    frags.append(text(bx1 + box_w / 2, top_y + 25, "Фазовий перехід 1-го роду", size=14, bold=True, color="#c2410c", anchor="middle"))
    frags.append(text(bx1 + box_w / 2, top_y + 45, "(Плавлення, кипіння, скачок параметра)", size=11, color="#ea580c", anchor="middle"))
    frags.append(line(bx1 + 15, top_y + 55, bx1 + box_w - 15, top_y + 55, color="#fdba74", sw=1))

    f1_items = [
        ("• Стрибок параметра порядку:", "Δη ≠ 0 (переривчастий)"),
        ("• Прихована теплота плавлення/пару:", "L = T꜀ · ΔS ≠ 0"),
        ("• Співіснування фаз:", "Існує гетерогенна суміш"),
        ("• Похідні вільної енергії:", "Стрибок 1-х похідних (S, V)"),
        ("• Гістерезис та переохолодження:", "Присутні метастабільні стани"),
    ]

    for idx, (label, val) in enumerate(f1_items):
        iy = top_y + 85 + idx * 50
        frags.append(rect(bx1 + 15, iy - 12, box_w - 30, 42, fill="#ffffff", stroke="#fed7aa", sw=1, rx=5))
        frags.append(text(bx1 + 25, iy + 4, label, size=10.5, bold=True, color="#9a3412", anchor="start"))
        frags.append(text(bx1 + 25, iy + 22, val, size=10.5, color="#c2410c", anchor="start"))

    # 2-nd order box
    bx2 = 420
    frags.append(rect(bx2, top_y, box_w, box_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(bx2 + box_w / 2, top_y + 25, "Фазовий перехід 2-го роду (Ландау)", size=14, bold=True, color="#15803d", anchor="middle"))
    frags.append(text(bx2 + box_w / 2, top_y + 45, "(Точка Кюрі, надпровідність, He-II)", size=11, color="#16a34a", anchor="middle"))
    frags.append(line(bx2 + 15, top_y + 55, bx2 + box_w - 15, top_y + 55, color="#86efac", sw=1))

    f2_items = [
        ("• Неперервний параметр порядку:", "η(T꜀) = 0 (без стрибка)"),
        ("• Прихована теплота:", "L = 0 (теплота не виділяється)"),
        ("• Співіснування фаз:", "Відсутнє (межа критична точка)"),
        ("• Похідні вільної енергії:", "Стрибок 2-х похідних (Cₚ, χ)"),
        ("• Фундаментальна причина:", "Спонтанне порушення симетрії"),
    ]

    for idx, (label, val) in enumerate(f2_items):
        iy = top_y + 85 + idx * 50
        frags.append(rect(bx2 + 15, iy - 12, box_w - 30, 42, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=5))
        frags.append(text(bx2 + 25, iy + 4, label, size=10.5, bold=True, color="#166534", anchor="start"))
        frags.append(text(bx2 + 25, iy + 22, val, size=10.5, color="#15803d", anchor="start"))

    render(os.path.join(IMG_DIR, "phase-diagram-first-second-order.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_landau_potential_wells()
    build_fig2_order_parameter_heat_capacity()
    build_fig3_phase_diagram_first_second_order()
    print("Всі 3 фігури успішно згенеровано у", IMG_DIR)
