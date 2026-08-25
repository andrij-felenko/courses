# -*- coding: utf-8 -*-
"""Фігури для теми «Задача комівояжера» (book/algorithms/complexity-computability/traveling-salesperson-problem)."""
import sys, os, math

# Шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CYAN_F, CYAN_S = "#e6fffa", "#0d9488"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
BLUE_F, BLUE_S = "#eff6ff", "#2563eb"
GREEN_F, GREEN_S = "#f0fdf4", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig1_tsp_problem_statement():
    """fig1-tsp-problem-statement.svg: Постановка задачі комівояжера: граф вершин, матриця відстаней та оптимальний цикл."""
    W, H = 840, 480
    frags = []
    
    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 35, "Постановка задачі комівояжера (TSP): зважений граф та оптимальний обхід", size=15, bold=True, color="#1e293b"))

    # Вершини міста A, B, C, D, E
    cities = {
        'A': (140, 130),
        'B': (320, 110),
        'C': (380, 280),
        'D': (230, 390),
        'E': (100, 300)
    }

    edges = [
        ('A', 'B', 12, True),
        ('B', 'C', 8, True),
        ('C', 'D', 15, True),
        ('D', 'E', 9, True),
        ('E', 'A', 10, True),
        ('A', 'C', 22, False),
        ('A', 'D', 25, False),
        ('B', 'D', 18, False),
        ('B', 'E', 20, False),
        ('C', 'E', 14, False),
    ]

    # Малювання ребер (неоптимальні пунктиром, оптимальний цикл червоним)
    for u, v, w, is_opt in edges:
        x1, y1 = cities[u]
        x2, y2 = cities[v]
        if is_opt:
            frags.append(line(x1, y1, x2, y2, color=RED_S, sw=3.5))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            b, _, _ = textbox(mx, my, str(w), size=11, bold=True, fill=RED_F, stroke=RED_S)
            frags.append(b)
        else:
            frags.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=1.5, dash="4 4"))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            b, _, _ = textbox(mx, my, str(w), size=10, fill="#ffffff", stroke="#cbd5e1")
            frags.append(b)

    # Вершини
    for label, (cx, cy) in cities.items():
        frags.append(circle(cx, cy, 20, fill=RED_F, stroke=RED_S, sw=2.5))
        frags.append(text(cx, cy + 5, label, size=13, bold=True, color=RED_S))

    # Права панель: Матриця відстаней
    lx = 470
    frags.append(rect(lx, 70, 340, 380, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 170, 95, "Матриця відстаней W[i][j]", size=14, bold=True, color="#1e293b"))

    cols = ['A', 'B', 'C', 'D', 'E']
    matrix_data = [
        [0,  12, 22, 25, 10],
        [12, 0,  8,  18, 20],
        [22, 8,  0,  15, 14],
        [25, 18, 15, 0,  9],
        [10, 20, 14, 9,  0]
    ]

    # Заголовки колонок
    for j, col in enumerate(cols):
        frags.append(text(lx + 80 + j * 50, 130, col, size=12, bold=True, color=BLUE_S))

    # Рядки матриці
    for i, row_label in enumerate(cols):
        y_pos = 165 + i * 38
        frags.append(text(lx + 35, y_pos, row_label, size=12, bold=True, color=BLUE_S))
        for j, val in enumerate(matrix_data[i]):
            x_pos = lx + 80 + j * 50
            is_in_tour = (i, j) in [(0,1),(1,0),(1,2),(2,1),(2,3),(3,2),(3,4),(4,3),(4,0),(0,4)]
            val_str = "∞" if val == 0 and i != j else str(val)
            color_txt = RED_S if is_in_tour and val > 0 else ("#94a3b8" if val == 0 else "#334155")
            bold_txt = is_in_tour and val > 0
            frags.append(text(x_pos, y_pos, val_str, size=12, bold=bold_txt, color=color_txt))

    # Підсумок розв'язку
    frags.append(line(lx + 20, 365, lx + 320, 365, color="#cbd5e1", sw=1.0))
    frags.append(text(lx + 20, 390, "Оптимальний маршрут:", size=11, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 20, 410, "A → B → C → D → E → A", size=12, bold=True, color=RED_S, anchor="start"))
    frags.append(text(lx + 20, 432, "Загальна довжина = 12 + 8 + 15 + 9 + 10 = 54", size=11, bold=True, color=GREEN_S, anchor="start"))

    render(os.path.join(IMG, "fig1-tsp-problem-statement.svg"), W, H, *frags)

def fig2_hc_to_tsp_reduction():
    """fig2-hc-to-tsp-reduction.svg: Поліноміальна звідність задачі гамільтонового циклу до TSP."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 35, "Звідність: Гамільтонів цикл (HC) ≤p Задача комівояжера (TSP)", size=15, bold=True, color="#1e293b"))

    # Ліва частина: Вхідний граф G
    frags.append(rect(30, 65, 360, 345, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(210, 92, "Вхідний граф G = (V, E)", size=13, bold=True, color=BLUE_S))

    hc_verts = {'1': (120, 180), '2': (300, 180), '3': (300, 310), '4': (120, 310)}
    hc_edges = [('1','2'), ('2','3'), ('3','4'), ('4','1'), ('1','3')]

    for u, v in hc_edges:
        x1, y1 = hc_verts[u]
        x2, y2 = hc_verts[v]
        frags.append(line(x1, y1, x2, y2, color=BLUE_S, sw=2.5))

    for label, (cx, cy) in hc_verts.items():
        frags.append(circle(cx, cy, 18, fill="#ffffff", stroke=BLUE_S, sw=2))
        frags.append(text(cx, cy + 4, label, size=12, bold=True, color=BLUE_S))

    frags.append(text(210, 375, "Питання: чи існує гамільтонів цикл?", size=11, italic=True, color="#334155"))

    # Стрілка звідності
    frags.append(arrow(400, 230, 455, 230, color=AMBER_S, sw=3.0))
    frags.append(text(428, 212, "f(G)", size=12, bold=True, color=AMBER_S))

    # Права частина: Повний зважений граф K_n
    frags.append(rect(470, 65, 340, 345, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(640, 92, "Повний граф K_n з вагою w(e)", size=13, bold=True, color=PURPLE_S))

    tsp_verts = {'1': (550, 180), '2': (730, 180), '3': (730, 310), '4': (550, 310)}
    
    # Наявні ребра -> вага 1
    for u, v in [('1','2'), ('2','3'), ('3','4'), ('4','1'), ('1','3')]:
        x1, y1 = tsp_verts[u]
        x2, y2 = tsp_verts[v]
        frags.append(line(x1, y1, x2, y2, color=GREEN_S, sw=3.0))

    # Відсутнє ребро (2,4) -> вага 2 (або M)
    x1, y1 = tsp_verts['2']
    x2, y2 = tsp_verts['4']
    frags.append(line(x1, y1, x2, y2, color=RED_S, sw=2.0, dash="5 5"))

    for label, (cx, cy) in tsp_verts.items():
        frags.append(circle(cx, cy, 18, fill="#ffffff", stroke=PURPLE_S, sw=2))
        frags.append(text(cx, cy + 4, label, size=12, bold=True, color=PURPLE_S))

    # Правило зважування
    frags.append(rect(490, 340, 300, 55, fill="#ffffff", stroke=PURPLE_S, sw=1.0, rx=4))
    frags.append(text(640, 358, "w(u, v) = 1, якщо (u, v) ∈ E", size=11, bold=True, color=GREEN_S))
    frags.append(text(640, 380, "w(u, v) = 2 (або ∞), якщо (u, v) ∉ E", size=11, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig2-hc-to-tsp-reduction.svg"), W, H, *frags)

def fig3_held_karp_dp():
    """fig3-held-karp-dp.svg: Гратчаста структура підзадач алгоритму Хелда-Карпа (динамічне програмування з бітовими масками)."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 35, "Динамічне програмування Хелда-Карпа: O(n² · 2ⁿ)", size=15, bold=True, color="#1e293b"))

    # Рекурентне співвідношення нагорі
    frags.append(rect(40, 60, 760, 45, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(420, 87, "dp(S, v) = min { dp(S \\ {v}, u) + w(u, v) | u ∈ S \\ {v} }", size=13, bold=True, color=BLUE_S))

    # Рівні розміру підмножини |S| (зсунуті вліво, щоб не перетинатися з правою панеллю на x=660)
    levels = [
        ("|S| = 1 (База)", ["dp({0}, 0) = 0"], 145),
        ("|S| = 2", ["dp({0,1}, 1)", "dp({0,2}, 2)", "dp({0,3}, 3)"], 215),
        ("|S| = 3", ["dp({0,1,2}, 1)", "dp({0,1,2}, 2)", "dp({0,1,3}, 3)", "dp({0,2,3}, 3)"], 295),
        ("|S| = 4 (Фінал)", ["min { dp({0,1,2,3}, v) + w(v, 0) }"], 380)
    ]

    for label, states, y_pos in levels:
        frags.append(text(30, y_pos + 5, label, size=11, bold=True, color="#475569", anchor="start"))
        n_st = len(states)
        step = 440 / (n_st + 1)
        for idx, st_name in enumerate(states):
            x_st = 180 + (idx + 1) * step
            b, _, _ = textbox(x_st, y_pos, st_name, size=11, bold=True, fill="#ffffff", stroke=PURPLE_S if "|S| = 4" in label else BLUE_S)
            frags.append(b)

    # Лінії залежностей між рівнем 2 і 3
    frags.append(line(290, 230, 268, 280, color="#cbd5e1", sw=1.5))
    frags.append(line(290, 230, 356, 280, color="#cbd5e1", sw=1.5))
    frags.append(line(400, 230, 268, 280, color="#cbd5e1", sw=1.5))
    frags.append(line(400, 230, 444, 280, color="#cbd5e1", sw=1.5))

    # Права бічна панель складність
    lx = 660
    frags.append(rect(lx, 115, 155, 310, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 77, 138, "Оцінки ресурсу", size=13, bold=True, color="#1e293b"))

    frags.append(text(lx + 12, 168, "Часова складність:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 188, "O(n² · 2ⁿ)", size=12, bold=True, color=RED_S, anchor="start"))

    frags.append(text(lx + 12, 225, "Просторова пам'ять:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 245, "O(n · 2ⁿ)", size=12, bold=True, color=AMBER_S, anchor="start"))

    frags.append(text(lx + 12, 285, "Межа застосування:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 305, "n ≤ 23..25", size=12, bold=True, color=GREEN_S, anchor="start"))

    frags.append(text(lx + 12, 345, "Бітова маска S:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 365, "1 << v (uint32_t)", size=10, bold=True, color=PURPLE_S, anchor="start"))

    render(os.path.join(IMG, "fig3-held-karp-dp.svg"), W, H, *frags)

def fig4_christofides_algorithm():
    """fig4-christofides-algorithm.svg: 4 кроки алгоритму Крістофідеса-Сердюкова (1.5-апроксимація)."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 35, "Алгоритм Крістофідеса-Сердюкова: 1.5-апроксимація метричної TSP", size=15, bold=True, color="#1e293b"))

    panels = [
        ("1. Мінімальне кістякове дерево (T)", 30, 65, BLUE_F, BLUE_S, "weight(T) ≤ OPT"),
        ("2. Паросполучення непарних (M)", 430, 65, PURPLE_F, PURPLE_S, "weight(M) ≤ 0.5 OPT"),
        ("3. Ейлерів мультиграф (T + M)", 30, 265, AMBER_F, AMBER_S, "Кожна deg(v) парна"),
        ("4. Скорочення (Shortcutting)", 430, 265, GREEN_F, GREEN_S, "Цикл ≤ 1.5 OPT")
    ]

    for title, px, py, fill_c, stroke_c, note in panels:
        frags.append(rect(px, py, 380, 180, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        frags.append(text(px + 190, py + 24, title, size=12, bold=True, color=stroke_c))

        # 4 вершини в кожній панелі
        v_coords = {
            'A': (px + 60, py + 70),
            'B': (px + 180, py + 60),
            'C': (px + 320, py + 90),
            'D': (px + 260, py + 145),
            'E': (px + 100, py + 145)
        }

        if "1." in title:
            # MST edges
            mst_e = [('A','B'), ('B','D'), ('D','E'), ('B','C')]
            for u, v in mst_e:
                x1, y1 = v_coords[u]
                x2, y2 = v_coords[v]
                frags.append(line(x1, y1, x2, y2, color=BLUE_S, sw=2.5))
        elif "2." in title:
            # Odd vertices A, C, D, E matching
            for u, v in [('A','B'), ('B','D'), ('D','E'), ('B','C')]:
                x1, y1 = v_coords[u]
                x2, y2 = v_coords[v]
                frags.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=1.5, dash="3 3"))
            # Matching edges (A,E) and (C,D)
            frags.append(line(v_coords['A'][0], v_coords['A'][1], v_coords['E'][0], v_coords['E'][1], color=PURPLE_S, sw=3.0))
            frags.append(line(v_coords['C'][0], v_coords['C'][1], v_coords['D'][0], v_coords['D'][1], color=PURPLE_S, sw=3.0))
        elif "3." in title:
            # T + M multigraph
            for u, v in [('A','B'), ('B','D'), ('D','E'), ('B','C')]:
                x1, y1 = v_coords[u]
                x2, y2 = v_coords[v]
                frags.append(line(x1, y1, x2, y2, color=BLUE_S, sw=2.0))
            frags.append(line(v_coords['A'][0], v_coords['A'][1], v_coords['E'][0], v_coords['E'][1], color=PURPLE_S, sw=2.0))
            frags.append(line(v_coords['C'][0], v_coords['C'][1], v_coords['D'][0], v_coords['D'][1], color=PURPLE_S, sw=2.0))
        elif "4." in title:
            # Shortcutted Hamiltonian cycle
            hc_e = [('A','B'), ('B','C'), ('C','D'), ('D','E'), ('E','A')]
            for u, v in hc_e:
                x1, y1 = v_coords[u]
                x2, y2 = v_coords[v]
                frags.append(line(x1, y1, x2, y2, color=GREEN_S, sw=3.0))

        for label, (cx, cy) in v_coords.items():
            is_odd = label in ['A', 'C', 'D', 'E']
            fill_v = RED_F if is_odd and "2." in title else "#ffffff"
            stroke_v = RED_S if is_odd and "2." in title else stroke_c
            frags.append(circle(cx, cy, 12, fill=fill_v, stroke=stroke_v, sw=1.5))
            frags.append(text(cx, cy + 4, label, size=10, bold=True, color=INK))

        frags.append(text(px + 190, py + 170, note, size=10, bold=True, color=stroke_c))

    render(os.path.join(IMG, "fig4-christofides-algorithm.svg"), W, H, *frags)

def fig5_2opt_swap():
    """fig5-2opt-swap.svg: Геометрична інтуїція локального пошуку 2-Opt (розплітання перетинів)."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 35, "Локальна оптимізація 2-Opt: ліквідація самоперетинів ребер", size=15, bold=True, color="#1e293b"))

    # Ліва панель: До заміни (з перетином)
    frags.append(rect(40, 65, 350, 320, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(215, 95, "До 2-Opt: Перетин ребер (неоптимально)", size=12, bold=True, color=RED_S))

    pts_left = {
        'U': (100, 150),
        'V': (330, 310),
        'X': (100, 310),
        'Y': (330, 150)
    }

    # Перехресні ребра U-V та X-Y
    frags.append(line(pts_left['U'][0], pts_left['U'][1], pts_left['V'][0], pts_left['V'][1], color=RED_S, sw=3.0))
    frags.append(line(pts_left['X'][0], pts_left['X'][1], pts_left['Y'][0], pts_left['Y'][1], color=RED_S, sw=3.0))

    # Точка перетину
    frags.append(circle(215, 230, 6, fill=RED_S, stroke="#ffffff", sw=1.5))
    frags.append(text(215, 215, "Перетин!", size=10, bold=True, color=RED_S))

    for label, (cx, cy) in pts_left.items():
        frags.append(circle(cx, cy, 16, fill="#ffffff", stroke=RED_S, sw=2))
        frags.append(text(cx, cy + 4, label, size=11, bold=True, color=RED_S))

    frags.append(text(215, 360, "Довжина: d(U,V) + d(X,Y) = 18.4 + 18.4 = 36.8", size=10, bold=True, color=RED_S))

    # Стрілка заміни
    frags.append(arrow(400, 225, 455, 225, color=AMBER_S, sw=3.0))
    frags.append(text(428, 205, "2-Opt Swap", size=11, bold=True, color=AMBER_S))

    # Права панель: Після заміни (розплетено)
    frags.append(rect(470, 65, 340, 320, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(640, 95, "Після 2-Opt: Паралельні ребра (розплетено)", size=12, bold=True, color=GREEN_S))

    pts_right = {
        'U': (530, 150),
        'V': (760, 310),
        'X': (530, 310),
        'Y': (760, 150)
    }

    # Нові ребра U-Y та X-V
    frags.append(line(pts_right['U'][0], pts_right['U'][1], pts_right['Y'][0], pts_right['Y'][1], color=GREEN_S, sw=3.0))
    frags.append(line(pts_right['X'][0], pts_right['X'][1], pts_right['V'][0], pts_right['V'][1], color=GREEN_S, sw=3.0))

    for label, (cx, cy) in pts_right.items():
        frags.append(circle(cx, cy, 16, fill="#ffffff", stroke=GREEN_S, sw=2))
        frags.append(text(cx, cy + 4, label, size=11, bold=True, color=GREEN_S))

    frags.append(text(640, 360, "Довжина: d(U,Y) + d(X,V) = 11.5 + 11.5 = 23.0", size=10, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig5-2opt-swap.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_tsp_problem_statement()
    fig2_hc_to_tsp_reduction()
    fig3_held_karp_dp()
    fig4_christofides_algorithm()
    fig5_2opt_swap()
    print("Всі фігури успішно згенеровано в напрямку img/")
