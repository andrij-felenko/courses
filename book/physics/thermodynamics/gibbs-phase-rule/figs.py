# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_water_phase_diagram(out_path):
    w, h = 760, 500
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 26, "Фазова діаграма стану води (однокомпонентна система, K = 1)", size=16, bold=True))
    
    # Осі координат
    ox, oy = 90, 420
    w_ax, h_ax = 600, 340
    frags.append(arrow(ox, oy, ox + w_ax + 20, oy)) # Ось T
    frags.append(arrow(ox, oy, ox, oy - h_ax - 20)) # Ось P
    
    frags.append(text(ox + w_ax + 25, oy + 5, "Температура T", size=13, anchor="start", bold=True))
    frags.append(text(ox - 10, oy - h_ax - 25, "Тиск P (лог. масштаб)", size=13, anchor="middle", bold=True))
    
    # Точки
    # Потрійна точка T_tr
    tx, ty = 290, 280
    # Критична точка T_cr
    cx, cy = 620, 110
    # Верхня точка лінії плавлення
    mx, my = 260, 90
    # Початок сублімації
    sx, sy = 120, 410
    
    # Крива сублімації (суцільна лінія)
    frags.append(f'<path d="M {sx} {sy} Q 210 360 {tx} {ty}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    # Крива випаровування (рідка-газ)
    frags.append(f'<path d="M {tx} {ty} Q 460 230 {cx} {cy}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    # Крива плавлення (лід-вода, негативний нахил)
    frags.append(f'<path d="M {tx} {ty} L {mx} {my}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    
    # Позначення фазових областей за допомогою textbox
    box_ice, _, _ = textbox(180, 130, "Тверда фаза (Лід)\nK = 1, P = 1\nF = 1 - 1 + 2 = 2\n(диваріантна)", size=11, fill="#eef6fc", stroke=NEG)
    box_water, _, _ = textbox(440, 130, "Рідка фаза (Вода)\nK = 1, P = 1\nF = 1 - 1 + 2 = 2\n(диваріантна)", size=11, fill="#eff9f0", stroke=FIELD)
    box_vapor, _, _ = textbox(520, 360, "Газоподібна фаза (Пара)\nK = 1, P = 1\nF = 1 - 1 + 2 = 2\n(диваріантна)", size=11, fill="#fdf3f2", stroke=POS)
    
    frags.extend([box_ice, box_water, box_vapor])
    
    # Потрійна точка
    frags.append(circle(tx, ty, 6, fill=POS, stroke=INK, sw=1.5))
    box_tr, _, _ = textbox(190, 275, "Потрійна точка (T_tr, P_tr)\nT = 0.01 °C, P = 611.65 Pa\nK = 1, P = 3 → F = 0\n(нонваріантна точка)", size=11, fill="#ffffff", stroke=POS, bold=True)
    frags.append(box_tr)
    frags.append(line(tx, ty, 260, 275, color=POS, dash="2,2"))
    
    # Критична точка
    frags.append(circle(cx, cy, 6, fill=FIELD, stroke=INK, sw=1.5))
    box_crit, _, _ = textbox(610, 50, "Критична точка K_cr\nT = 374 °C, P = 22.06 MPa\nМежа фазового переходу", size=11, fill="#ffffff", stroke=FIELD, bold=True)
    frags.append(box_crit)
    
    # Підписи ліній співіснування (моноваріантні лінії F = 1)
    frags.append(text(210, 350, "Сублімація (F = 1)", size=11, color=NEG, italic=True))
    frags.append(text(460, 250, "Випаровування (F = 1)", size=11, color=POS, italic=True))
    frags.append(text(230, 170, "Плавлення (F = 1)", size=11, color=FIELD, italic=True))

    render(out_path, w, h, *frags)

def draw_eutectic_phase_diagram(out_path):
    w, h = 760, 520
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 26, "Двокомпонентна евтектична діаграма стану (K = 2, P = const)", size=16, bold=True))
    
    ox, oy = 90, 440
    w_ax, h_ax = 580, 350
    
    frags.append(arrow(ox, oy, ox + w_ax + 20, oy)) # Ось складу x_B
    frags.append(arrow(ox, oy, ox, oy - h_ax - 20)) # Ось T ліва
    frags.append(line(ox + w_ax, oy, ox + w_ax, oy - h_ax - 20, color=LINE)) # Ось T права
    
    frags.append(text(ox + w_ax / 2, oy + 35, "Склад системи (масова або мольна частка компонента B, %)", size=13, bold=True))
    frags.append(text(ox - 15, oy - h_ax - 15, "Температура T", size=13, anchor="middle", bold=True))
    
    # Характерні точки
    # T_A (температура плавлення A)
    tax, tay = ox, oy - 280
    # T_B (температура плавлення B)
    tbx, tby = ox + w_ax, oy - 230
    # Евтектична точка E
    ex, ey = ox + 250, oy - 140
    
    # Ліквідус A-E
    frags.append(f'<path d="M {tax} {tay} Q {ox + 100} {oy - 200} {ex} {ey}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    # Ліквідус B-E
    frags.append(f'<path d="M {tbx} {tby} Q {ox + 420} {oy - 170} {ex} {ey}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    
    # Евтектична ізотерма (лінія солідус)
    frags.append(line(ox, ey, ox + w_ax, ey, color=NEG, sw=2.5))
    
    # Області
    box_liq, _, _ = textbox(ox + w_ax / 2, oy - 290, "Рідкий розчин (L)\nK = 2, P = 1 → F = 2 - 1 + 1 = 2 (диваріантна)", size=12, fill="#fdf3f2", stroke=POS)
    box_l_a, _, _ = textbox(ox + 90, oy - 190, "L + α (Рідина + Кристали A)\nK = 2, P = 2 → F = 1", size=11, fill="#ffffff", stroke=MUTED)
    box_l_b, _, _ = textbox(ox + 440, oy - 190, "L + β (Рідина + Кристали B)\nK = 2, P = 2 → F = 1", size=11, fill="#ffffff", stroke=MUTED)
    box_sol, _, _ = textbox(ox + w_ax / 2, oy - 35, "Твердий стан: суміш фаз α + β\nK = 2, P = 2 → F = 2 - 2 + 1 = 1", size=12, fill="#eff9f0", stroke=FIELD)
    
    frags.extend([box_liq, box_l_a, box_l_b, box_sol])
    
    # Позначення евтектичної точки
    frags.append(circle(ex, ey, 6, fill=NEG, stroke=INK, sw=1.5))
    box_e, _, _ = textbox(ex - 120, ey + 50, "Евтектична точка E (T_E, x_E)\nL ⇌ α + β\nK = 2, P = 3 → F = 0\n(нонваріантна точка)", size=11, fill="#ffffff", stroke=NEG, bold=True)
    frags.append(box_e)
    frags.append(line(ex, ey, ex - 60, ey + 30, color=NEG, dash="2,2"))
    
    # Правило важеля (нода / tie-line)
    t_y = oy - 210
    nl_x = ox + 30
    nr_x = ox + 175
    np_x = ox + 105
    frags.append(line(nl_x, t_y, nr_x, t_y, color=FIELD, sw=3))
    frags.append(circle(np_x, t_y, 4, fill=FIELD, stroke=INK))
    frags.append(text(np_x, t_y - 12, "Фігуративна точка", size=10, color=FIELD, bold=True))
    frags.append(text(nl_x, t_y + 14, "Фаза α", size=10, color=FIELD))
    frags.append(text(nr_x, t_y + 14, "Фаза L", size=10, color=FIELD))
    
    # Підписи точок плавлення
    frags.append(text(tax - 15, tay + 5, "T_A", size=12, bold=True))
    frags.append(text(tbx + 15, tby + 5, "T_B", size=12, bold=True))
    frags.append(text(ox - 15, ey + 5, "T_E", size=12, color=NEG, bold=True))

    render(out_path, w, h, *frags)

def draw_chemical_potential_equilibrium(out_path):
    w, h = 740, 460
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 26, "Термодинамічні умови фазової рівноваги у багатокомпонентній системі", size=15, bold=True))
    
    # Три блоки фаз
    b1_x, b1_y = 140, 150
    b2_x, b2_y = 370, 150
    b3_x, b3_y = 600, 150
    
    box1, _, _ = textbox(b1_x, b1_y, "Фаза α (Тверда)\nT^(α), P^(α)\nμ_1^(α), μ_2^(α), ..., μ_K^(α)", size=12, fill="#eef6fc", stroke=NEG, pad=12)
    box2, _, _ = textbox(b2_x, b2_y, "Фаза β (Рідка)\nT^(β), P^(β)\nμ_1^(β), μ_2^(β), ..., μ_K^(β)", size=12, fill="#eff9f0", stroke=FIELD, pad=12)
    box3, _, _ = textbox(b3_x, b3_y, "Фаза γ (Газова)\nT^(γ), P^(γ)\nμ_1^(γ), μ_2^(γ), ..., μ_K^(γ)", size=12, fill="#fdf3f2", stroke=POS, pad=12)
    
    frags.extend([box1, box2, box3])
    
    # Стрілки рівноваги між фазами
    frags.append(arrow(b1_x + 75, b1_y - 20, b2_x - 75, b2_y - 20, color=LINE, sw=2))
    frags.append(arrow(b2_x - 75, b2_y + 20, b1_x + 75, b1_y + 20, color=LINE, sw=2))
    frags.append(text((b1_x + b2_x) / 2, b1_y - 30, "T^(α) = T^(β),  P^(α) = P^(β)", size=11, bold=True))
    frags.append(text((b1_x + b2_x) / 2, b1_y + 35, "μ_i^(α) = μ_i^(β)", size=11, color=FIELD, bold=True))
    
    frags.append(arrow(b2_x + 75, b2_y - 20, b3_x - 75, b3_y - 20, color=LINE, sw=2))
    frags.append(arrow(b3_x - 75, b3_y + 20, b2_x + 75, b2_y + 20, color=LINE, sw=2))
    frags.append(text((b2_x + b3_x) / 2, b2_y - 30, "T^(β) = T^(γ),  P^(β) = P^(γ)", size=11, bold=True))
    frags.append(text((b2_x + b3_x) / 2, b2_y + 35, "μ_i^(β) = μ_i^(γ)", size=11, color=FIELD, bold=True))
    
    # Нижній підсумковий блок розрахунку вариативності F
    calc_text = (
        "Баланс термодинамічних змінних та рівнянь зв'язку:\n"
        "1. Інтенсивні змінні системи: T, P та P·(K - 1) мольних часток  →  Всього N_var = 2 + P·(K - 1)\n"
        "2. Рівняння рівноваги: K·(P - 1) рівностей хімічних потенціалів  →  Всього N_eq = K·(P - 1)\n"
        "3. Число ступенів вільності (варіантність): F = N_var - N_eq = [2 + P·(K - 1)] - K·(P - 1) = K - P + 2"
    )
    box_calc, _, _ = textbox(w / 2, 340, calc_text, size=11, fill="#ffffff", stroke=INK, pad=14, bold=False)
    frags.append(box_calc)

    render(out_path, w, h, *frags)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    draw_water_phase_diagram(os.path.join(img_dir, 'water-phase-diagram.svg'))
    draw_eutectic_phase_diagram(os.path.join(img_dir, 'eutectic-phase-diagram.svg'))
    draw_chemical_potential_equilibrium(os.path.join(img_dir, 'chemical-potential-equilibrium.svg'))
    print("Figures generated successfully in img/")

if __name__ == '__main__':
    main()
