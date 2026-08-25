# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Хроматичне число графа»."""

import os
import sys
import math

# Додаємо шлях до svgkit у кореневій папці scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

# Локальні палітри кольорів розфарбування графів
COLOR_R = "#e74c3c"  # Червоний колір 1
COLOR_B = "#3498db"  # Синій колір 2
COLOR_G = "#2ecc71"  # Зелений колір 3
COLOR_Y = "#f39c12"  # Жовтий колір 4 (для Mycielski M4)
COLOR_UN = "#ecf0f1" # Нерозфарбована вершина
STROKE_V = "#2c3e50"


def draw_conflict_graph_coloring():
    """Фігура 1: Граф конфліктів та його мінімальне правильне 3-розфарбування."""
    w, h = 760, 360
    frags = []

    # Заголовок секції 1: Задачі та конфлікти
    frags.append(text(200, 30, "Граф несумісності завдань (конфлікти часу/ресурсів)", size=14, bold=True))
    frags.append(text(580, 30, "Розподіл за часовими слотами (кольори)", size=14, bold=True))

    coords = {
        "A": (100, 110),
        "B": (260, 100),
        "C": (300, 220),
        "D": (180, 280),
        "E": (90, 210),
        "F": (190, 170)
    }

    active_edges = [
        ("A", "B"), ("A", "E"), ("A", "F"),
        ("B", "C"), ("B", "F"),
        ("C", "D"),
        ("D", "E"), ("D", "F")
    ]

    v_colors = {
        "A": COLOR_B,
        "B": COLOR_G,
        "C": COLOR_R,
        "D": COLOR_B,
        "E": COLOR_G,
        "F": COLOR_R
    }

    # Малюємо ребра
    for u, v in active_edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        frags.append(line(x1, y1, x2, y2, color="#7f8c8d", sw=2.0))

    # Малюємо вершини
    r_node = 20
    for name, (cx, cy) in coords.items():
        c_fill = v_colors[name]
        frags.append(circle(cx, cy, r_node, fill=c_fill, stroke=STROKE_V, sw=2.0))
        frags.append(text(cx, cy + 5, name, size=14, color="#ffffff", bold=True))

    # Розділювальна лінія
    frags.append(line(400, 45, 400, 330, color="#bdc3c7", sw=1.5, dash="4,4"))

    # Права панель: Таблиця кольорових класів (незалежних множин)
    box1, _, _ = textbox(580, 85, "Колір 1 (Червоний): { F, C }\nСуміжні ребра відсутні: незалежна множина I₁",
                         size=12, fill="#fdecea", stroke=COLOR_R, sw=1.5, min_w=310)
    box2, _, _ = textbox(580, 165, "Колір 2 (Синій): { A, D }\nСуміжні ребра відсутні: незалежна множина I₂",
                         size=12, fill="#ebf5fb", stroke=COLOR_B, sw=1.5, min_w=310)
    box3, _, _ = textbox(580, 245, "Колір 3 (Зелений): { B, E }\nСуміжні ребра відсутні: незалежна множина I₃",
                         size=12, fill="#eafaf1", stroke=COLOR_G, sw=1.5, min_w=310)

    frags.extend([box1, box2, box3])

    # Підсумок знизу
    sum_box, _, _ = textbox(580, 315, "Хроматичне число χ(G) = 3: кліка K₃ {A,B,F} вимагає ≥ 3 кольорів",
                            size=12, fill=FILL, stroke=LINE, sw=1.2, bold=True, min_w=310)
    frags.append(sum_box)

    return render(os.path.join(os.path.dirname(__file__), "img", "conflict-graph-coloring.svg"),
                  w, h, *frags)


def draw_mycielski_construction():
    """Фігура 2: Конструкція Мицельського (від C5 до графа Грьотча M4 без трикутників з χ=4)."""
    w, h = 760, 420
    frags = []

    frags.append(text(380, 26, "Конструкція Мицельського M(G): зростання χ без появи трикутників", size=15, bold=True))

    center_x, center_y = 380, 220
    r_u = 80   # радіус кола u
    r_v = 150  # радіус кола v

    u_coords = {}
    v_coords = {}

    for i in range(5):
        angle = -math.pi / 2 + i * 2 * math.pi / 5
        u_coords[i] = (center_x + r_u * math.cos(angle), center_y + r_u * math.sin(angle))
        v_coords[i] = (center_x + r_v * math.cos(angle), center_y + r_v * math.sin(angle))

    w_coord = (center_x, center_y)

    # 1. Ребра від верхівки w до всіх v_i
    for i in range(5):
        frags.append(line(w_coord[0], w_coord[1], v_coords[i][0], v_coords[i][1], color="#e67e22", sw=1.8, dash="3,3"))

    # 2. Ребра тіньових вершин v_i до сусідів u_j (у C5 сусіди u_i — це (i-1)%5 та (i+1)%5)
    for i in range(5):
        left_u = (i - 1) % 5
        right_u = (i + 1) % 5
        frags.append(line(v_coords[i][0], v_coords[i][1], u_coords[left_u][0], u_coords[left_u][1], color="#95a5a6", sw=1.2))
        frags.append(line(v_coords[i][0], v_coords[i][1], u_coords[right_u][0], u_coords[right_u][1], color="#95a5a6", sw=1.2))

    # 3. Ребра базового C5 між u_i та u_{i+1}
    for i in range(5):
        next_u = (i + 1) % 5
        frags.append(line(u_coords[i][0], u_coords[i][1], u_coords[next_u][0], u_coords[next_u][1], color=INK, sw=2.2))

    # Малюємо вершини
    u_col_list = [COLOR_R, COLOR_B, COLOR_R, COLOR_B, COLOR_G] # C5 needs 3 colors
    for i in range(5):
        cx, cy = u_coords[i]
        frags.append(circle(cx, cy, 14, fill=u_col_list[i], stroke=STROKE_V, sw=1.5))
        frags.append(text(cx, cy + 4, f"u{i+1}", size=11, color="#ffffff", bold=True))

    # v_i (тіньові вершини) - дублюють кольори u_i
    for i in range(5):
        cx, cy = v_coords[i]
        frags.append(circle(cx, cy, 14, fill=u_col_list[i], stroke="#7f8c8d", sw=1.5))
        frags.append(text(cx, cy + 4, f"v{i+1}", size=11, color="#ffffff", bold=True))

    # w (купол) - вимагає нового 4-го кольору!
    frags.append(circle(w_coord[0], w_coord[1], 18, fill=COLOR_Y, stroke=STROKE_V, sw=2.0))
    frags.append(text(w_coord[0], w_coord[1] + 5, "w", size=13, color="#ffffff", bold=True))

    # Пояснювальні плашки з боків
    left_info, _, _ = textbox(125, 110, "Базовий C₅: u₁..u₅\nКліка ω = 2 (без K₃)\nХроматичне число χ = 3",
                              size=11, fill="#f4f6f8", stroke=LINE, min_w=210)
    shadow_info, _, _ = textbox(125, 230, "Тіні v₁..v₅ з'єднані\nз сусідами u в C₅.\nМіж v немає ребер!",
                                size=11, fill="#f4f6f8", stroke="#7f8c8d", min_w=210)
    apex_info, _, _ = textbox(635, 110, "Купол w з'єднаний з усіма v.\nОскільки {v} містить\nусі 3 кольори, для w\nпотрібен 4-й колір!",
                              size=11, fill="#fef9e7", stroke=COLOR_Y, min_w=210)
    prop_info, _, _ = textbox(635, 250, "Граф Грьотча M₄:\nВершин: 11, ребер: 20\nКліка: ω(M₄) = 2 (без K₃)\nХроматичне: χ(M₄) = 4",
                              size=11, fill="#fdecea", stroke=COLOR_R, bold=True, min_w=210)

    frags.extend([left_info, shadow_info, apex_info, prop_info])

    return render(os.path.join(os.path.dirname(__file__), "img", "mycielski-construction.svg"),
                  w, h, *frags)


def draw_gadget_reduction():
    """Фігура 3: Зведення 3-SAT до 3-Coloring (гаджети змінних та диз'юнкта)."""
    w, h = 760, 420
    frags = []

    frags.append(text(380, 24, "Зведення 3-SAT ≤ₚ 3-Coloring: палітра істинності та гаджет диз'юнкта", size=14, bold=True))

    # Ліва частина: Базовий трикутник істинності та гаджет змінної
    frags.append(text(170, 55, "1. Палітра і змінна xᵢ", size=13, bold=True))

    tb_b = (170, 95)
    tb_t = (100, 165)
    tb_f = (240, 165)

    frags.append(line(tb_b[0], tb_b[1], tb_t[0], tb_t[1], color=LINE, sw=1.8))
    frags.append(line(tb_t[0], tb_t[1], tb_f[0], tb_f[1], color=LINE, sw=1.8))
    frags.append(line(tb_f[0], tb_f[1], tb_b[0], tb_b[1], color=LINE, sw=1.8))

    frags.append(circle(tb_b[0], tb_b[1], 15, fill="#7f8c8d", stroke=STROKE_V, sw=1.5))
    frags.append(text(tb_b[0], tb_b[1] + 4, "B", size=12, color="#ffffff", bold=True))

    frags.append(circle(tb_t[0], tb_t[1], 15, fill=COLOR_G, stroke=STROKE_V, sw=1.5))
    frags.append(text(tb_t[0], tb_t[1] + 4, "T", size=12, color="#ffffff", bold=True))

    frags.append(circle(tb_f[0], tb_f[1], 15, fill=COLOR_R, stroke=STROKE_V, sw=1.5))
    frags.append(text(tb_f[0], tb_f[1] + 4, "F", size=12, color="#ffffff", bold=True))

    lit_x = (100, 270)
    lit_notx = (240, 270)

    frags.append(line(lit_x[0], lit_x[1], lit_notx[0], lit_notx[1], color=LINE, sw=1.8))
    frags.append(line(tb_b[0], tb_b[1], lit_x[0], lit_x[1], color="#95a5a6", sw=1.2, dash="3,3"))
    frags.append(line(tb_b[0], tb_b[1], lit_notx[0], lit_notx[1], color="#95a5a6", sw=1.2, dash="3,3"))

    frags.append(circle(lit_x[0], lit_x[1], 16, fill=COLOR_G, stroke=STROKE_V, sw=1.5))
    frags.append(text(lit_x[0], lit_x[1] + 4, "xᵢ", size=12, color="#ffffff", bold=True))

    frags.append(circle(lit_notx[0], lit_notx[1], 16, fill=COLOR_R, stroke=STROKE_V, sw=1.5))
    frags.append(text(lit_notx[0], lit_notx[1] + 4, "¬xᵢ", size=12, color="#ffffff", bold=True))

    p_var, _, _ = textbox(170, 360, "Оскільки xᵢ та ¬xᵢ з'єднані з B,\nвони отримують лише кольори {T, F}.\nРебро між ними змушує один бути T,\nа інший — F (булевий інваріант).",
                          size=11, fill=FILL, stroke=LINE, min_w=280)
    frags.append(p_var)

    # Розділювач
    frags.append(line(340, 50, 340, 400, color="#bdc3c7", sw=1.5, dash="4,4"))

    # Права частина: Гаджет диз'юнкта C = (l1 ∨ l2 ∨ l3)
    frags.append(text(550, 55, "2. Гаджет диз'юнкта (l₁ ∨ l₂ ∨ l₃)", size=13, bold=True))

    g_l1 = (410, 120)
    g_l2 = (410, 200)
    g_l3 = (410, 290)

    g_a1 = (490, 130)
    g_a2 = (490, 190)
    g_a3 = (560, 160)

    g_b1 = (630, 210)
    g_b2 = (630, 280)
    g_out = (700, 245)

    # Перший каскад OR(l1, l2)
    frags.append(line(g_l1[0], g_l1[1], g_a1[0], g_a1[1], color=LINE, sw=1.5))
    frags.append(line(g_l2[0], g_l2[1], g_a2[0], g_a2[1], color=LINE, sw=1.5))
    frags.append(line(g_a1[0], g_a1[1], g_a2[0], g_a2[1], color=LINE, sw=1.5))
    frags.append(line(g_a1[0], g_a1[1], g_a3[0], g_a3[1], color=LINE, sw=1.5))
    frags.append(line(g_a2[0], g_a2[1], g_a3[0], g_a3[1], color=LINE, sw=1.5))

    # Другий каскад OR(a3, l3)
    frags.append(line(g_a3[0], g_a3[1], g_b1[0], g_b1[1], color=LINE, sw=1.5))
    frags.append(line(g_l3[0], g_l3[1], g_b2[0], g_b2[1], color=LINE, sw=1.5))
    frags.append(line(g_b1[0], g_b1[1], g_b2[0], g_b2[1], color=LINE, sw=1.5))
    frags.append(line(g_b1[0], g_b1[1], g_out[0], g_out[1], color=LINE, sw=1.5))
    frags.append(line(g_b2[0], g_b2[1], g_out[0], g_out[1], color=LINE, sw=1.5))

    # Входи
    frags.append(circle(g_l1[0], g_l1[1], 13, fill=COLOR_G, stroke=STROKE_V, sw=1.5))
    frags.append(text(g_l1[0], g_l1[1] + 4, "l₁", size=11, color="#ffffff", bold=True))

    frags.append(circle(g_l2[0], g_l2[1], 13, fill=COLOR_R, stroke=STROKE_V, sw=1.5))
    frags.append(text(g_l2[0], g_l2[1] + 4, "l₂", size=11, color="#ffffff", bold=True))

    frags.append(circle(g_l3[0], g_l3[1], 13, fill=COLOR_R, stroke=STROKE_V, sw=1.5))
    frags.append(text(g_l3[0], g_l3[1] + 4, "l₃", size=11, color="#ffffff", bold=True))

    # Проміжні
    for pt in [g_a1, g_a2, g_a3, g_b1, g_b2]:
        frags.append(circle(pt[0], pt[1], 10, fill=FILL, stroke=STROKE_V, sw=1.2))

    # Вихід
    frags.append(circle(g_out[0], g_out[1], 15, fill=COLOR_G, stroke=STROKE_V, sw=2.0))
    frags.append(text(g_out[0], g_out[1] + 4, "out", size=10, color="#ffffff", bold=True))

    p_clause, _, _ = textbox(550, 360, "Вихідний вузол out з'єднаний з базовими {B, F}.\nВін може отримати колір T тоді й лише тоді,\nколи хоча б один із входів (l₁, l₂, l₃) має колір T.\nЯкщо всі хибні (F), гаджет не розфарбовується в 3 кольори.",
                             size=11, fill="#fdecea", stroke=COLOR_R, min_w=370)
    frags.append(p_clause)

    return render(os.path.join(os.path.dirname(__file__), "img", "gadget-reduction.svg"),
                  w, h, *frags)


def draw_dsatur_step():
    """Фігура 4: Динаміка насиченості в евристиці DSATUR."""
    w, h = 760, 360
    frags = []

    frags.append(text(380, 24, "Вибір наступної вершини за ступенем насиченості (DSATUR)", size=14, bold=True))

    v_pos = {
        "1": (120, 110),
        "2": (120, 250),
        "3": (360, 180),
        "A": (230, 100),
        "B": (230, 260),
        "C": (480, 180)
    }

    edges = [
        ("1", "A"), ("3", "A"),
        ("1", "B"), ("2", "B"), ("3", "B"),
        ("3", "C")
    ]

    for u, v in edges:
        x1, y1 = v_pos[u]
        x2, y2 = v_pos[v]
        frags.append(line(x1, y1, x2, y2, color="#7f8c8d", sw=1.8))

    # Розфарбовані
    frags.append(circle(v_pos["1"][0], v_pos["1"][1], 18, fill=COLOR_R, stroke=STROKE_V, sw=2.0))
    frags.append(text(v_pos["1"][0], v_pos["1"][1] + 5, "1", size=13, color="#ffffff", bold=True))

    frags.append(circle(v_pos["2"][0], v_pos["2"][1], 18, fill=COLOR_B, stroke=STROKE_V, sw=2.0))
    frags.append(text(v_pos["2"][0], v_pos["2"][1] + 5, "2", size=13, color="#ffffff", bold=True))

    frags.append(circle(v_pos["3"][0], v_pos["3"][1], 18, fill=COLOR_G, stroke=STROKE_V, sw=2.0))
    frags.append(text(v_pos["3"][0], v_pos["3"][1] + 5, "3", size=13, color="#ffffff", bold=True))

    # Нерозфарбовані
    # A (deg_sat = 2)
    frags.append(circle(v_pos["A"][0], v_pos["A"][1], 18, fill=COLOR_UN, stroke="#7f8c8d", sw=2.0))
    frags.append(text(v_pos["A"][0], v_pos["A"][1] + 5, "A", size=13, color=INK, bold=True))
    frags.append(text(v_pos["A"][0], v_pos["A"][1] - 26, "deg_sat = 2 {R, G}", size=11, color=MUTED, bold=True))

    # B (deg_sat = 3) -> HIGHLIGHTED
    frags.append(circle(v_pos["B"][0], v_pos["B"][1], 22, fill="#fef9e7", stroke=COLOR_R, sw=3.0))
    frags.append(text(v_pos["B"][0], v_pos["B"][1] + 5, "B", size=14, color=COLOR_R, bold=True))
    frags.append(text(v_pos["B"][0], v_pos["B"][1] + 38, "deg_sat = 3 {R, G, B} (MAX)", size=11, color=COLOR_R, bold=True))

    # C (deg_sat = 1)
    frags.append(circle(v_pos["C"][0], v_pos["C"][1], 18, fill=COLOR_UN, stroke="#7f8c8d", sw=2.0))
    frags.append(text(v_pos["C"][0], v_pos["C"][1] + 5, "C", size=13, color=INK, bold=True))
    frags.append(text(v_pos["C"][0], v_pos["C"][1] - 26, "deg_sat = 1 {G}", size=11, color=MUTED, bold=True))

    # Пояснювальна таблиця праворуч
    t1, _, _ = textbox(620, 100, "1. Обчислення насиченості:\ndeg_sat(v) = |{ кольори сусідів v }|\n• Вершина A: сусіди {1(R), 3(G)} → 2\n• Вершина B: сусіди {1(R), 2(B), 3(G)} → 3\n• Вершина C: сусіди {3(G)} → 1",
                       size=11, fill=FILL, stroke=LINE, min_w=240)

    t2, _, _ = textbox(620, 240, "2. Евристичне правило:\nОбираємо вершину з MAX deg_sat (вузол B).\nВона має найменше доступних кольорів\nі найбільше обмежує вибір.\nЯкщо deg_sat = k, це змушує або\nстворити новий (k+1)-й колір, або\nвідсікти тупикову гілку пошуку.",
                       size=11, fill="#fdecea", stroke=COLOR_R, min_w=240)

    frags.extend([t1, t2])

    return render(os.path.join(os.path.dirname(__file__), "img", "dsatur-step.svg"),
                  w, h, *frags)


if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    draw_conflict_graph_coloring()
    draw_mycielski_construction()
    draw_gadget_reduction()
    draw_dsatur_step()
    print("Всі 4 фігури успішно згенеровано у папку img/")
