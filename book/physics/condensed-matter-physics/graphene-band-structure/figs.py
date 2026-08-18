# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

# 1. Гексагональна кристалічна ґратка графену з двома підґратками A та B
def gen_real_lattice():
    w, h = 720, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Кристалічна ґратка графену: підґратки A і B та вектори зв'язку", size=16, bold=True))

    a_cc = 40.0
    cx, cy = 310.0, 240.0

    # Вектори найближчих сусідів від вузла A до B
    delta1 = (0.0, -a_cc)
    delta2 = (a_cc * math.sqrt(3)/2, a_cc * 0.5)
    delta3 = (-a_cc * math.sqrt(3)/2, a_cc * 0.5)

    # Одиничні вектори примітивної трансляції
    a1 = (a_cc * math.sqrt(3), 0.0)
    a2 = (a_cc * math.sqrt(3)/2, a_cc * 1.5)

    nodes_a = []
    nodes_b = []

    for i in range(-3, 4):
        for j in range(-3, 3):
            ax = cx + i * a1[0] + j * a2[0]
            ay = cy + i * a1[1] + j * a2[1]

            if 40 < ax < w - 230 and 40 < ay < h - 40:
                nodes_a.append((ax, ay))
                bx = ax + delta1[0]
                by = ay + delta1[1]
                nodes_b.append((bx, by))

    # Зв'язки (лінії між A та B)
    for ax, ay in nodes_a:
        for dx, dy in [delta1, delta2, delta3]:
            bx, by = ax + dx, ay + dy
            if 30 < bx < w - 210 and 30 < by < h - 20:
                frags.append(line(ax, ay, bx, by, color="#b0b7c0", sw=2.0))

    # Вектори трансляції a1 та a2 від центрального вузла A
    orig_a = (cx, cy)
    v_a1 = (cx + a1[0], cy + a1[1])
    v_a2 = (cx + a2[0], cy + a2[1])

    frags.append(arrow(orig_a[0], orig_a[1], v_a1[0], v_a1[1], color=FIELD, sw=2.5))
    frags.append(text(v_a1[0] + 15, v_a1[1] + 5, "a₁", size=15, color=FIELD, bold=True))

    frags.append(arrow(orig_a[0], orig_a[1], v_a2[0], v_a2[1], color=FIELD, sw=2.5))
    frags.append(text(v_a2[0] - 22, v_a2[1] + 10, "a₂", size=15, color=FIELD, bold=True))

    # Вектори найближчих сусідів δ1, δ2, δ3 від центрального A
    d1_pos = (cx + delta1[0], cy + delta1[1])
    d2_pos = (cx + delta2[0], cy + delta2[1])
    d3_pos = (cx + delta3[0], cy + delta3[1])

    frags.append(arrow(cx, cy, d1_pos[0], d1_pos[1], color=POS, sw=2.0))
    frags.append(text(d1_pos[0] + 12, d1_pos[1] + 5, "δ₁", size=14, color=POS, bold=True))

    frags.append(arrow(cx, cy, d2_pos[0], d2_pos[1], color=POS, sw=2.0))
    frags.append(text(d2_pos[0] + 14, d2_pos[1] - 5, "δ₂", size=14, color=POS, bold=True))

    frags.append(arrow(cx, cy, d3_pos[0], d3_pos[1], color=POS, sw=2.0))
    frags.append(text(d3_pos[0] - 24, d3_pos[1] - 5, "δ₃", size=14, color=POS, bold=True))

    # Малювання вузлів A та B
    for ax, ay in nodes_a:
        frags.append(circle(ax, ay, 7.0, fill=POS, stroke="#900c3f", sw=1.5))
    for bx, by in nodes_b:
        frags.append(circle(bx, by, 7.0, fill=NEG, stroke="#1b3b82", sw=1.5))

    # Відстань a_cc
    frags.append(line(cx + 8, cy - 20, cx + 8, cy - a_cc + 10, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(cx + 18, cy - a_cc/2 - 2, "a_cc = 1.42 Å", size=12, color=MUTED, italic=True))

    # Легенда праворуч
    leg_x = 520.0
    frags.append(rect(leg_x, 80, 180, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(leg_x + 90, 105, "Позначення", size=15, bold=True))

    frags.append(circle(leg_x + 25, 140, 7.0, fill=POS, stroke="#900c3f", sw=1.5))
    frags.append(text(leg_x + 42, 144, "Підґратка A", size=13, anchor="start"))

    frags.append(circle(leg_x + 25, 175, 7.0, fill=NEG, stroke="#1b3b82", sw=1.5))
    frags.append(text(leg_x + 42, 179, "Підґратка B", size=13, anchor="start"))

    frags.append(line(leg_x + 15, 210, leg_x + 35, 210, color=FIELD, sw=2.5))
    frags.append(text(leg_x + 42, 214, "Базис a₁, a₂", size=13, anchor="start"))

    frags.append(line(leg_x + 15, 245, leg_x + 35, 245, color=POS, sw=2.0))
    frags.append(text(leg_x + 42, 249, "Зв'язки δᵢ", size=13, anchor="start"))

    frags.append(text(leg_x + 90, 290, "Параметри:", size=13, bold=True))
    frags.append(text(leg_x + 15, 315, "a = √3 a_cc ≈ 2.46 Å", size=12, anchor="start", color=MUTED))
    frags.append(text(leg_x + 15, 340, "Кут між σ-зв'язками: 120°", size=12, anchor="start", color=MUTED))
    frags.append(text(leg_x + 15, 365, "Перекриття 2p_z: π-зони", size=12, anchor="start", color=MUTED))
    frags.append(text(leg_x + 15, 390, "2 атоми на осередку", size=12, anchor="start", color=MUTED))

    render(os.path.join(OUT_DIR, "real-lattice-sublattices.svg"), w, h, *frags)

# 2. Перша зона Бріллюена графену та особливі точки Г, M, K, K'
def gen_brillouin_zone():
    w, h = 680, 480
    frags = []

    frags.append(text(w / 2, 28, "Перша зона Бріллюена графену в квазіімпульсному просторі", size=16, bold=True))

    cx, cy = 250.0, 240.0
    R = 105.0  # Радіус вершин шестикутника (точки K та K')

    # Вершини першої зони Бріллюена
    k_points = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3
        kx = cx + R * math.cos(angle)
        ky = cy + R * math.sin(angle)
        k_points.append((kx, ky))

    # Полігон першої зони Бріллюена
    poly_pts = " ".join(["%.1f,%.1f" % (px, py) for px, py in k_points])
    frags.append('<polygon points="%s" fill="#eef2ff" stroke="%s" stroke-width="2.5"/>' % (poly_pts, NEG))

    # Осі k_x та k_y
    frags.append(arrow(cx - 170, cy, cx + 180, cy, color=MUTED, sw=1.5))
    frags.append(text(cx + 195, cy + 4, "k_x", size=14, color=MUTED, bold=True))

    frags.append(arrow(cx, cy + 160, cx, cy - 170, color=MUTED, sw=1.5))
    frags.append(text(cx, cy - 180, "k_y", size=14, color=MUTED, bold=True))

    # Точка Gamma (центр)
    frags.append(circle(cx, cy, 5.0, fill=INK, stroke=INK, sw=1.0))
    frags.append(text(cx - 16, cy + 18, "Γ", size=15, bold=True))

    # Точки K та K' на вершинах
    labels_k = ["K", "K'", "K", "K'", "K", "K'"]
    colors_k = [POS, NEG, POS, NEG, POS, NEG]

    for i, (px, py) in enumerate(k_points):
        lbl = labels_k[i]
        col = colors_k[i]
        frags.append(circle(px, py, 6.0, fill=col, stroke=INK, sw=1.2))

        dx = 16 * math.cos(math.pi / 6 + i * math.pi / 3)
        dy = 16 * math.sin(math.pi / 6 + i * math.pi / 3)
        frags.append(text(px + dx, py + dy + 4, lbl, size=13, color=col, bold=True))

    # Точка M (середина грані)
    mx = (k_points[0][0] + k_points[1][0]) / 2.0
    my = (k_points[0][1] + k_points[1][1]) / 2.0
    frags.append(circle(mx, my, 5.0, fill=FIELD, stroke=INK, sw=1.2))
    frags.append(text(mx + 16, my + 4, "M", size=13, color=FIELD, bold=True))

    # Вектори оберненої ґратки b1 та b2
    b1_angle = 0.0
    b2_angle = math.pi / 3
    b_len = R * math.sqrt(3)

    b1_x = cx + b_len * math.cos(b1_angle)
    b1_y = cy - b_len * math.sin(b1_angle)
    b2_x = cx + b_len * math.cos(b2_angle)
    b2_y = cy - b_len * math.sin(b2_angle)

    frags.append(arrow(cx, cy, b1_x, b1_y, color=FIELD, sw=2.0))
    frags.append(text(b1_x + 14, b1_y + 4, "b₁", size=14, color=FIELD, bold=True))

    frags.append(arrow(cx, cy, b2_x, b2_y, color=FIELD, sw=2.0))
    frags.append(text(b2_x + 10, b2_y - 8, "b₂", size=14, color=FIELD, bold=True))

    # Інформаційна картка праворуч
    card_x = 460.0
    frags.append(rect(card_x, 70, 205, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(card_x + 102, 95, "Особливі точки ЗБ", size=15, bold=True))

    frags.append(circle(card_x + 20, 130, 5.0, fill=INK, stroke=INK, sw=1.0))
    frags.append(text(card_x + 35, 134, "Γ: k = (0, 0)", size=12, anchor="start"))

    frags.append(circle(card_x + 20, 165, 6.0, fill=POS, stroke=INK, sw=1.0))
    frags.append(text(card_x + 35, 169, "K: (4π/(3√3 a_cc), 0)", size=11, anchor="start", color=POS, bold=True))

    frags.append(circle(card_x + 20, 200, 6.0, fill=NEG, stroke=INK, sw=1.0))
    frags.append(text(card_x + 35, 204, "K': (-4π/(3√3 a_cc), 0)", size=11, anchor="start", color=NEG, bold=True))

    frags.append(circle(card_x + 20, 235, 5.0, fill=FIELD, stroke=INK, sw=1.0))
    frags.append(text(card_x + 35, 239, "M: середина грані ЗБ", size=12, anchor="start", color=FIELD))

    frags.append(text(card_x + 102, 275, "Властивості:", size=13, bold=True))
    frags.append(text(card_x + 12, 300, "• 6 вершин поділені на", size=11, anchor="start", color=MUTED))
    frags.append(text(card_x + 12, 318, "  дві долині K та K'", size=11, anchor="start", color=MUTED))
    frags.append(text(card_x + 12, 340, "• У K та K' конуси", size=11, anchor="start", color=MUTED))
    frags.append(text(card_x + 12, 358, "  торкаються при E=0", size=11, anchor="start", color=MUTED))
    frags.append(text(card_x + 12, 380, "• Долинний фактор g_v = 2", size=11, anchor="start", color=MUTED))
    frags.append(text(card_x + 12, 400, "• Спіновий фактор g_s = 2", size=11, anchor="start", color=MUTED))

    render(os.path.join(OUT_DIR, "brillouin-zone-dirac-points.svg"), w, h, *frags)

# 3. Діраківський конус та лінійна зонна дисперсія
def gen_dirac_cone():
    w, h = 700, 480
    frags = []

    frags.append(text(w / 2, 28, "Діраківський конус: зонний спектр графену поблизу точки K", size=16, bold=True))

    cx, cy = 260.0, 240.0

    # Вісь енергії E
    frags.append(arrow(cx, cy + 180, cx, cy - 190, color=INK, sw=2.0))
    frags.append(text(cx + 25, cy - 192, "Енергія E", size=14, bold=True))

    # Вісь квазіімпульсу q_x
    frags.append(arrow(cx - 180, cy, cx + 190, cy, color=MUTED, sw=1.5))
    frags.append(text(cx + 205, cy + 4, "q_x", size=14, color=MUTED, bold=True))

    # Верхній конус (π*)
    top_cone_pts = "%d,%d %d,%d %d,%d" % (cx - 130, cy - 140, cx, cy, cx + 130, cy - 140)
    frags.append('<polygon points="%s" fill="#fee2e2" stroke="%s" stroke-width="2.0"/>' % (top_cone_pts, POS))

    # Еліпс для верхньої основи
    frags.append('<ellipse cx="%d" cy="%d" rx="130" ry="26" fill="#fca5a5" stroke="%s" stroke-width="1.5" opacity="0.7"/>' % (cx, cy - 140, POS))

    # Нижній конус (π)
    bot_cone_pts = "%d,%d %d,%d %d,%d" % (cx - 130, cy + 140, cx, cy, cx + 130, cy + 140)
    frags.append('<polygon points="%s" fill="#dbeafe" stroke="%s" stroke-width="2.0"/>' % (bot_cone_pts, NEG))

    # Еліпс для нижньої основи
    frags.append('<ellipse cx="%d" cy="%d" rx="130" ry="26" fill="#93c5fd" stroke="%s" stroke-width="1.5" opacity="0.7"/>' % (cx, cy + 140, NEG))

    # Точка Дірака
    frags.append(circle(cx, cy, 6.0, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(cx + 40, cy + 5, "Точка Дірака", size=13, color=POS, bold=True))

    # Позначення зон
    frags.append(text(cx - 75, cy - 75, "Зона провідності π*", size=13, color=POS, bold=True))
    frags.append(text(cx - 75, cy + 80, "Валентна зона π", size=13, color=NEG, bold=True))

    # Рівень Фермі
    frags.append(line(cx - 170, cy, cx - 10, cy, color=FIELD, sw=1.8, dash="5,3"))
    frags.append(text(cx - 110, cy - 10, "Рівень Фермі E_F", size=12, color=FIELD, bold=True))

    # Фізична картка праворуч
    card_x = 470.0
    frags.append(rect(card_x, 70, 210, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(card_x + 105, 95, "Фізичні параметри", size=15, bold=True))

    frags.append(text(card_x + 15, 130, "• Фермі-швидкість v_F:", size=13, anchor="start", bold=True))
    frags.append(text(card_x + 25, 150, "v_F ≈ 10⁶ м/с (c / 300)", size=12, anchor="start", color=POS))

    frags.append(text(card_x + 15, 185, "• Безмасові ферміони:", size=13, anchor="start", bold=True))
    frags.append(text(card_x + 25, 205, "m* = 0 при E = E_F", size=12, anchor="start", color=NEG))

    frags.append(text(card_x + 15, 240, "• Густина станів g(E):", size=13, anchor="start", bold=True))
    frags.append(text(card_x + 25, 260, "g(E) ∝ |E| (лінійна)", size=12, anchor="start", color=FIELD))

    frags.append(text(card_x + 15, 295, "• Гамільтоніан Дірака:", size=13, anchor="start", bold=True))
    frags.append(text(card_x + 25, 315, "H_eff = ħ v_F (σ · q)", size=12, anchor="start", color=INK))

    frags.append(text(card_x + 15, 350, "• Спіральність/Хіральність:", size=13, anchor="start", bold=True))
    frags.append(text(card_x + 25, 370, "h = ±1 (псевдоспін)", size=12, anchor="start", color=MUTED))

    render(os.path.join(OUT_DIR, "dirac-cone-dispersion.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_real_lattice()
    gen_brillouin_zone()
    gen_dirac_cone()
    print("Успішно згенеровано 3 SVG-фігури в img/")
