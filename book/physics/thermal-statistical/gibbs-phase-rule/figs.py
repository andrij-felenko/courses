# -*- coding: utf-8 -*-
"""
Генерація SVG-фігур для теми "Правило фаз Гіббса" (gibbs-phase-rule).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def generate_water_phase_diagram(out_path):
    w, h = 640, 480
    frags = []
    
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=8))
    
    ox, oy = 70, 410
    axis_w, axis_h = 520, 340
    frags.append(line(ox, oy, ox + axis_w, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - axis_h, color=INK, sw=2))
    
    frags.append(arrow(ox + axis_w - 10, oy, ox + axis_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy - axis_h + 10, ox, oy - axis_h, color=INK, sw=2))
    
    frags.append(text(ox + axis_w - 20, oy + 30, "Температура T (K)", size=14, bold=True))
    frags.append(text(ox - 50, oy - axis_h + 20, "Тиск P (Па)", size=14, bold=True))
    
    tx, ty = 260, 290
    
    frags.append(line(tx, ty, 230, 80, color=NEG, sw=2.5))
    frags.append(line(80, 400, tx, ty, color=POS, sw=2.5))
    
    cx, cy = 480, 120
    frags.append(line(tx, ty, cx, cy, color=FIELD, sw=2.5))
    
    frags.append(line(cx, cy, cx, oy, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(cx, cy, ox, cy, color=MUTED, sw=1, dash="4,4"))
    
    frags.append(line(tx, ty, tx, oy, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(tx, ty, ox, ty, color=MUTED, sw=1, dash="4,4"))
    
    frags.append(circle(tx, ty, 6, fill="#f1c40f", stroke=INK, sw=2))
    frags.append(circle(cx, cy, 6, fill="#e74c3c", stroke=INK, sw=2))
    
    b_solid, _, _ = textbox(150, 180, "ТВЕРДА ФАЗА\n(Лід)\nF = 1 - 1 + 2 = 2", size=13, fill="#ebf5fb", stroke=NEG, pad=6)
    b_liquid, _, _ = textbox(360, 180, "РІДКА ФАЗА\n(Вода)\nF = 1 - 1 + 2 = 2", size=13, fill="#eafaf1", stroke=FIELD, pad=6)
    b_gas, _, _ = textbox(360, 360, "ГАЗОПОДІБНА ФАЗА\n(Пара)\nF = 1 - 1 + 2 = 2", size=13, fill="#fdedec", stroke=POS, pad=6)
    frags.extend([b_solid, b_liquid, b_gas])
    
    t_melt, _, _ = textbox(165, 95, "Плавлення (P=2, F=1)", size=11, fill="#ffffff", stroke=NEG, pad=4)
    t_subl, _, _ = textbox(150, 345, "Сублімація (P=2, F=1)", size=11, fill="#ffffff", stroke=POS, pad=4)
    t_vap, _, _ = textbox(410, 240, "Випаровування (P=2, F=1)", size=11, fill="#ffffff", stroke=FIELD, pad=4)
    frags.extend([t_melt, t_subl, t_vap])
    
    t_tp_box, _, _ = textbox(tx + 65, ty + 15, "Потрійна точка\nP = 3, F = 0\n(Нонваріантний стан)", size=11, fill="#fef9e7", stroke="#f39c12", pad=5)
    t_cp_box, _, _ = textbox(cx + 45, cy - 25, "Критична точка\n(Фазова межа зникає)", size=11, fill="#fadbd8", stroke="#e74c3c", pad=5)
    frags.extend([t_tp_box, t_cp_box])
    
    render(out_path, w, h, *frags, title="Фазова P-T діаграма однокомпонентної системи (C = 1)")

def generate_binary_eutectic_diagram(out_path):
    w, h = 640, 480
    frags = []
    
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=8))
    
    ox, oy = 70, 410
    axis_w, axis_h = 500, 340
    
    frags.append(line(ox, oy, ox + axis_w, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - axis_h, color=INK, sw=2))
    frags.append(line(ox + axis_w, oy, ox + axis_w, oy - axis_h, color=INK, sw=2))
    
    frags.append(arrow(ox, oy - axis_h + 10, ox, oy - axis_h, color=INK, sw=2))
    frags.append(arrow(ox + axis_w, oy - axis_h + 10, ox + axis_w, oy - axis_h, color=INK, sw=2))
    
    frags.append(text(ox + axis_w / 2, oy + 30, "Мольна частка компонента B (x_B)", size=14, bold=True))
    frags.append(text(ox - 45, oy - axis_h + 20, "T (°C)", size=13, bold=True))
    frags.append(text(ox + axis_w + 25, oy - axis_h + 20, "T (°C)", size=13, bold=True))
    
    frags.append(text(ox, oy + 18, "0 (100% A)", size=11, bold=True))
    frags.append(text(ox + axis_w, oy + 18, "1 (100% B)", size=11, bold=True))
    
    t_A_y = oy - 270
    t_B_y = oy - 230
    
    ex = ox + 220
    ey = oy - 120
    
    frags.append(line(ox, t_A_y, ex, ey, color=POS, sw=2.5))
    frags.append(line(ox + axis_w, t_B_y, ex, ey, color=POS, sw=2.5))
    
    frags.append(line(ox, ey, ox + axis_w, ey, color=NEG, sw=2.5))
    
    frags.append(circle(ex, ey, 6, fill="#f1c40f", stroke=INK, sw=2))
    
    b_liq, _, _ = textbox(ox + axis_w / 2, oy - 295, "РІДКИЙ РОЗЧИН (L)\nC = 2, P = 1 => F' = 2 - 1 + 1 = 2\n(Можна змінювати T та x_B)", size=11.5, fill="#eafaf1", stroke=FIELD, pad=5)
    
    # Eutectic point label above E
    e_box, _, _ = textbox(ex + 20, ey - 70, "Евтоктична точка E\nP = 3 (L + A_s + B_s)\nF' = 2 - 3 + 1 = 0", size=10.5, fill="#fef9e7", stroke="#f39c12", pad=4)
    
    b_la, _, _ = textbox(ox + 90, oy - 150, "Рідина L + Кристали A\nC = 2, P = 2 => F' = 1", size=10, fill="#ffffff", stroke=LINE, pad=4)
    b_lb, _, _ = textbox(ox + 380, oy - 150, "Рідина L + Кристали B\nC = 2, P = 2 => F' = 1", size=10, fill="#ffffff", stroke=LINE, pad=4)
    
    b_ab, _, _ = textbox(ox + axis_w / 2, oy - 40, "ТВЕРДА СУМІШ (Кристали A + Кристали B)\nC = 2, P = 2 => F' = 1 (при P=const)", size=11, fill="#fef9e7", stroke=LINE, pad=5)
    
    frags.extend([b_liq, e_box, b_la, b_lb, b_ab])
    
    render(out_path, w, h, *frags, title="Ізобарна фазова T-x діаграма подвійної системи (P = const)")

def generate_phase_rule_variables(out_path):
    w, h = 640, 420
    frags = []
    
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=8))
    
    box_v, _, _ = textbox(160, 100, "ІНТЕНСИВНІ ЗМІННІ\n• T (Температура)\n• P (Тиск)\n• x_i^α (Концентрації)\nУсього змінних: 2 + P·C", size=13, fill="#ebf5fb", stroke=NEG, pad=10)
    box_e, _, _ = textbox(470, 100, "РІВНЯННЯ РІВНОВАГИ\n• ∑ x_i^α = 1 (в кожній фазі P)\n• μ_i¹ = μ_i² = ... = μ_i^P\n  (по P-1 для кожного C)\nУсього рівнянь: P + C·(P - 1)", size=13, fill="#eafaf1", stroke=FIELD, pad=10)
    
    frags.extend([box_v, box_e])
    
    frags.append(arrow(160, 175, 270, 240, color=INK, sw=2))
    frags.append(arrow(470, 175, 370, 240, color=INK, sw=2))
    
    box_diff, _, _ = textbox(320, 270, "Ступені вільності F = (Змінні) - (Рівняння)\nF = (2 + P·C) - [P + C·(P - 1)]", size=14, fill="#ffffff", stroke=INK, bold=True, pad=10)
    frags.append(box_diff)
    
    frags.append(arrow(320, 315, 320, 350, color=POS, sw=2.5))
    
    box_res, _, _ = textbox(320, 375, "ГОЛОВНЕ ПРАВИЛО ФАЗ ГІББСА:  F = C - P + 2", size=15, fill="#fef9e7", stroke="#f39c12", bold=True, pad=10)
    frags.append(box_res)
    
    render(out_path, w, h, *frags, title="Баланс інтенсивних змінних та рівнянь термодинамічної рівноваги")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = build_img_dir(base_dir)
    
    generate_water_phase_diagram(os.path.join(img_dir, "water-phase-diagram.svg"))
    generate_binary_eutectic_diagram(os.path.join(img_dir, "binary-eutectic-diagram.svg"))
    generate_phase_rule_variables(os.path.join(img_dir, "phase-rule-variables.svg"))
    print("SVG figures generated successfully.")

if __name__ == "__main__":
    main()
