# -*- coding: utf-8 -*-
"""Фігури для теми «Гамільтонів граф та гамільтонів цикл» (book/algorithms/complexity-computability/hamiltonian-cycle)."""
import sys, os, math
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

def fig1_dodecahedron_icosian_game():
    """fig1-dodecahedron-icosian-game.svg: Проекція додекаедра (Ікосіанська гра) з виділеним гамільтоновим циклом."""
    W, H = 840, 520
    frags = []
    
    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 36, "Ікосіанська гра Уїльяма Гамільтона (1857): Гамільтонів цикл на додекаедрі", size=15, bold=True, color="#1e293b"))
    
    cx, cy = 340, 270
    r1, r2, r3, r4 = 190, 130, 80, 35
    
    verts = {}
    for i in range(5):
        angle = math.pi / 2 + i * 2 * math.pi / 5
        verts[i] = (cx + r1 * math.cos(angle), cy - r1 * math.sin(angle))
    for i in range(5):
        angle = math.pi / 2 + i * 2 * math.pi / 5
        verts[i + 5] = (cx + r2 * math.cos(angle), cy - r2 * math.sin(angle))
    for i in range(5):
        angle = math.pi / 2 + (i + 0.5) * 2 * math.pi / 5
        verts[i + 10] = (cx + r3 * math.cos(angle), cy - r3 * math.sin(angle))
    for i in range(5):
        angle = math.pi / 2 + (i + 0.5) * 2 * math.pi / 5
        verts[i + 15] = (cx + r4 * math.cos(angle), cy - r4 * math.sin(angle))

    all_edges = []
    for i in range(5): all_edges.append((i, (i + 1) % 5))
    for i in range(5): all_edges.append((i, i + 5))
    for i in range(5):
        all_edges.append((i + 5, i + 10))
        all_edges.append((i + 5, ((i - 1) % 5) + 10))
    for i in range(5): all_edges.append((i + 10, i + 15))
    for i in range(5): all_edges.append((i + 15, ((i + 1) % 5) + 15))

    hc_path = [0, 1, 2, 3, 4, 9, 14, 19, 18, 13, 8, 7, 12, 17, 16, 11, 6, 5, 10, 15]
    hc_edges = set()
    for i in range(len(hc_path)):
        u = hc_path[i]
        v = hc_path[(i + 1) % len(hc_path)]
        hc_edges.add((min(u, v), max(u, v)))

    for u, v in all_edges:
        edge_key = (min(u, v), max(u, v))
        if edge_key not in hc_edges:
            x1, y1 = verts[u]
            x2, y2 = verts[v]
            frags.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=2.0))

    for u, v in all_edges:
        edge_key = (min(u, v), max(u, v))
        if edge_key in hc_edges:
            x1, y1 = verts[u]
            x2, y2 = verts[v]
            frags.append(line(x1, y1, x2, y2, color=RED_S, sw=4.0))

    for i in range(20):
        vx, vy = verts[i]
        frags.append(circle(vx, vy, 13, fill=RED_F if i in hc_path else "#ffffff", stroke=RED_S if i in hc_path else GRAY_S, sw=2))
        frags.append(text(vx, vy + 4, str(i + 1), size=10, bold=True, color=RED_S if i in hc_path else INK))

    lx = 580
    frags.append(rect(lx, 70, 230, 420, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 115, 95, "Особливості графа", size=14, bold=True, color="#1e293b"))
    
    info_items = [
        ("Вершин (V):", "20 вершин додекаедра"),
        ("Ребер (E):", "30 ребер графа"),
        ("Степінь (deg):", "3 для кожної вершини"),
        ("Цикл (червоний):", "Замкнений прохід"),
        ("Довжина циклу:", "Рівно 20 ребер"),
        ("Правило:", "Кожна вершина 1 раз")
    ]
    
    y_curr = 135
    for label, val in info_items:
        frags.append(text(lx + 15, y_curr, label, size=11, bold=True, color="#334155", anchor="start"))
        frags.append(text(lx + 15, y_curr + 18, val, size=11, color="#64748b", anchor="start"))
        y_curr += 45

    frags.append(line(lx + 15, 410, lx + 60, 410, color=RED_S, sw=4.0))
    frags.append(text(lx + 70, 414, "Гамільтонів цикл", size=11, bold=True, color=RED_S, anchor="start"))
    
    frags.append(line(lx + 15, 440, lx + 60, 440, color="#cbd5e1", sw=2.0))
    frags.append(text(lx + 70, 444, "Невикористані ребра", size=11, color="#64748b", anchor="start"))

    render(os.path.join(IMG, "fig1-dodecahedron-icosian-game.svg"), W, H, *frags)


def fig2_eulerian_vs_hamiltonian():
    """fig2-eulerian-vs-hamiltonian.svg: Порівняння Ейлерового циклу (покриття ребер) та Гамільтонового циклу (покриття вершин)."""
    W, H = 840, 440
    frags = []
    
    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 36, "Фундаментальна відмінність: Ейлерів цикл vs Гамільтонів цикл", size=15, bold=True, color="#1e293b"))
    
    frags.append(rect(30, 60, 375, 350, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(217, 88, "Ейлерів цикл (Eulerian Circuit)", size=14, bold=True, color=BLUE_S))
    frags.append(text(217, 110, "Покриває кожне РЕБРО рівно один раз", size=12, italic=True, color="#3b82f6"))
    
    ev = {}
    for i in range(5):
        ang = math.pi/2 + i*2*math.pi/5
        ev[i+1] = (217 + 80*math.cos(ang), 210 - 80*math.sin(ang))
        
    e_edges = [(1,2),(2,3),(3,4),(4,5),(5,1), (1,3),(3,5),(5,2),(2,4),(4,1)]
    for u, v in e_edges:
        frags.append(line(ev[u][0], ev[u][1], ev[v][0], ev[v][1], color=BLUE_S, sw=2.5))
    for i in range(1, 6):
        frags.append(circle(ev[i][0], ev[i][1], 12, fill="#ffffff", stroke=BLUE_S, sw=2))
        frags.append(text(ev[i][0], ev[i][1]+4, str(i), size=11, bold=True, color=BLUE_S))

    frags.append(text(217, 330, "Критерій: усі deg(v) парні", size=12, bold=True, color=INK))
    frags.append(text(217, 355, "Складність: O(V + E) — ПОЛІНОМІАЛЬНА", size=12, bold=True, color=GREEN_S))
    frags.append(text(217, 380, "Локальна перевірка степенів вершин", size=11, color="#64748b"))

    frags.append(rect(435, 60, 375, 350, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(622, 88, "Гамільтонів цикл (Hamiltonian Cycle)", size=14, bold=True, color=RED_S))
    frags.append(text(622, 110, "Покриває кожну ВЕРШИНУ рівно один раз", size=12, italic=True, color="#dc2626"))

    hv = {}
    for i in range(5):
        ang = math.pi/2 + i*2*math.pi/5
        hv[i+1] = (622 + 80*math.cos(ang), 210 - 80*math.sin(ang))
        
    h_all_edges = [(1,2),(2,3),(3,4),(4,5),(5,1), (1,3),(2,4),(3,5)]
    h_cycle_edges = set([(1,2),(2,3),(3,4),(4,5),(5,1)])

    for u, v in h_all_edges:
        if (u,v) not in h_cycle_edges and (v,u) not in h_cycle_edges:
            frags.append(line(hv[u][0], hv[u][1], hv[v][0], hv[v][1], color="#cbd5e1", sw=1.5))
    for u, v in h_cycle_edges:
        frags.append(line(hv[u][0], hv[u][1], hv[v][0], hv[v][1], color=RED_S, sw=3.5))

    for i in range(1, 6):
        frags.append(circle(hv[i][0], hv[i][1], 12, fill=RED_F, stroke=RED_S, sw=2))
        frags.append(text(hv[i][0], hv[i][1]+4, str(i), size=11, bold=True, color=RED_S))

    frags.append(text(622, 330, "Критерій: глобальний зв'язок (немає локального)", size=12, bold=True, color=INK))
    frags.append(text(622, 355, "Складність: NP-ПОВНА (Експоненційна)", size=12, bold=True, color=RED_S))
    frags.append(text(622, 380, "Потрібен комбінаторний перебір / DP", size=11, color="#64748b"))

    render(os.path.join(IMG, "fig2-eulerian-vs-hamiltonian.svg"), W, H, *frags)


def fig3_dirac_ore_conditions():
    """fig3-dirac-ore-conditions.svg: Ілюстрація достатніх умов Дірака та Оре для гамільтоновості."""
    W, H = 840, 440
    frags = []
    
    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 36, "Достатні умови існування Гамільтонового циклу: Теореми Дірака та Оре", size=15, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 375, 350, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(217, 90, "Теорема Дірака (Gabriel Dirac, 1952)", size=13, bold=True, color=GREEN_S))
    
    b1, _, _ = textbox(217, 130, "deg(v) ≥ n / 2  для КОЖНОЇ вершины v", size=12, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b1)
    
    dv = {}
    for i in range(6):
        ang = i * math.pi / 3
        dv[i] = (217 + 75 * math.cos(ang), 230 + 75 * math.sin(ang))
    
    d_edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0), (0,3),(1,4),(2,5)]
    for u, v in d_edges:
        frags.append(line(dv[u][0], dv[u][1], dv[v][0], dv[v][1], color=GREEN_S, sw=2.0))
    for i in range(6):
        frags.append(circle(dv[i][0], dv[i][1], 11, fill="#ffffff", stroke=GREEN_S, sw=2))
        frags.append(text(dv[i][0], dv[i][1]+4, f"v{i+1}", size=10, bold=True, color=GREEN_S))

    frags.append(text(217, 335, "Граф n=6, deg(v) = 3 ≥ 6/2 = 3", size=11, bold=True, color=INK))
    frags.append(text(217, 360, "Висновок: Граф є ГАМІЛЬТОНОВИМ", size=12, bold=True, color=GREEN_S))
    frags.append(text(217, 385, "Вимога високого степеня для всіх вершин", size=11, color="#64748b"))

    frags.append(rect(435, 60, 375, 350, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(622, 90, "Теорема Оре (Øystein Ore, 1960)", size=13, bold=True, color=AMBER_S))

    b2, _, _ = textbox(622, 130, "deg(u) + deg(v) ≥ n  для НЕСУМІЖНИХ u, v", size=12, bold=True, fill="#ffffff", stroke=AMBER_S)
    frags.append(b2)

    ov = {}
    for i in range(6):
        ang = i * math.pi / 3
        ov[i] = (622 + 75 * math.cos(ang), 230 + 75 * math.sin(ang))

    o_edges = [(0,1),(0,5),(1,2),(2,3),(3,4),(4,5),(5,1),(2,4),(1,3),(3,5)]
    for u, v in o_edges:
        frags.append(line(ov[u][0], ov[u][1], ov[v][0], ov[v][1], color=AMBER_S, sw=2.0))
    for i in range(6):
        frags.append(circle(ov[i][0], ov[i][1], 11, fill="#ffffff", stroke=AMBER_S, sw=2))
        frags.append(text(ov[i][0], ov[i][1]+4, f"v{i+1}", size=10, bold=True, color=AMBER_S))

    frags.append(line(ov[0][0], ov[0][1], ov[3][0], ov[3][1], color=RED_S, sw=1.5, dash="4,4"))

    frags.append(text(622, 335, "Несуміжні v1 (deg 2) та v4 (deg 4): 2+4 = 6 ≥ 6", size=11, bold=True, color=INK))
    frags.append(text(622, 360, "Висновок: Граф є ГАМІЛЬТОНОВИМ", size=12, bold=True, color=AMBER_S))
    frags.append(text(622, 385, "Більш загальна умова, ніж теорема Дірака", size=11, color="#64748b"))

    render(os.path.join(IMG, "fig3-dirac-ore-conditions.svg"), W, H, *frags)


def fig4_3sat_to_hc_gadgets():
    """fig4-3sat-to-hc-gadgets.svg: Схема звідності 3SAT до Гамільтонового циклу (гаджети змінних та диз'юнктів)."""
    W, H = 840, 460
    frags = []
    
    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 36, "Конструкція звідності 3SAT ≤ₚ Гамільтонів цикл (Karp, 1972)", size=15, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 480, 370, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(270, 88, "Гаджет змінної xᵢ (Двонаправлений ланцюг)", size=13, bold=True, color=PURPLE_S))

    lx, rx_v = 70, 470
    cy = 230
    
    frags.append(circle(lx, cy, 14, fill="#ffffff", stroke=PURPLE_S, sw=2))
    frags.append(text(lx, cy+4, "Lᵢ", size=11, bold=True, color=PURPLE_S))
    
    frags.append(circle(rx_v, cy, 14, fill="#ffffff", stroke=PURPLE_S, sw=2))
    frags.append(text(rx_v, cy+4, "Rᵢ", size=11, bold=True, color=PURPLE_S))

    frags.append(text(270, 140, "Напрямок L → R: Змінна xᵢ = TRUE (істина)", size=11, bold=True, color=GREEN_S))
    frags.append(arrow(lx+14, cy-20, rx_v-14, cy-20, color=GREEN_S, sw=2.5))

    frags.append(text(270, 310, "Напрямок R → L: Змінна xᵢ = FALSE (хибність)", size=11, bold=True, color=RED_S))
    frags.append(arrow(rx_v-14, cy+20, lx+14, cy+20, color=RED_S, sw=2.5))

    for idx, x_pos in enumerate([150, 230, 310, 390]):
        frags.append(circle(x_pos, cy-20, 8, fill="#ffffff", stroke=GREEN_S, sw=1.5))
        frags.append(circle(x_pos, cy+20, 8, fill="#ffffff", stroke=RED_S, sw=1.5))

    frags.append(text(270, 360, "Вибір напрямку проходження фіксує значення булевої змінної", size=11, italic=True, color="#475569"))

    frags.append(rect(530, 60, 280, 370, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(670, 88, "Гаджет диз'юнкта Cⱼ", size=13, bold=True, color=AMBER_S))

    frags.append(circle(670, 210, 24, fill="#ffffff", stroke=AMBER_S, sw=2.5))
    frags.append(text(670, 215, "Cⱼ", size=14, bold=True, color=AMBER_S))

    frags.append(text(670, 130, "Вершина диз'юнкта Cⱼ", size=12, bold=True, color=INK))
    frags.append(text(670, 155, "підключається до 3-х треків", size=11, color="#64748b"))

    frags.append(line(480, 180, 646, 205, color=AMBER_S, sw=2.0, dash="3,3"))
    frags.append(line(646, 215, 480, 240, color=AMBER_S, sw=2.0, dash="3,3"))

    frags.append(text(670, 280, "Обхід вершини Cⱼ", size=12, bold=True, color=INK))
    frags.append(text(670, 305, "можливий лише якщо", size=11, color="#64748b"))
    frags.append(text(670, 325, "бодай один літерал = TRUE", size=11, bold=True, color=GREEN_S))
    frags.append(text(670, 365, "Гамільтонів цикл існує", size=11, bold=True, color=PURPLE_S))
    frags.append(text(670, 385, "якщо формула є виконуваною", size=11, bold=True, color=PURPLE_S))

    render(os.path.join(IMG, "fig4-3sat-to-hc-gadgets.svg"), W, H, *frags)


def fig5_held_karp_bitmask_dp():
    """fig5-held-karp-bitmask-dp.svg: Структура станів та переходів алгоритму Гелда-Карпа (Bitmask DP)."""
    W, H = 840, 450
    frags = []
    
    frags.append(rect(10, 10, 820, 430, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(420, 36, "Динамічне програмування з бітовими масками (Held-Karp): DP[S][v]", size=15, bold=True, color="#1e293b"))

    b1, _, _ = textbox(420, 75, "dp[mask][v] = ⋁ { dp[mask \\ {v}][u] ∧ HasEdge(u, v) }  для  u ∈ mask", size=12, bold=True, fill=CYAN_F, stroke=CYAN_S)
    frags.append(b1)

    levels = [
        ("Розмір |S| = 1", ["{v₀}"], 130),
        ("Розмір |S| = 2", ["{v₀, v₁}", "{v₀, v₂}", "{v₀, v₃}"], 210),
        ("Розмір |S| = 3", ["{v₀, v₁, v₂}", "{v₀, v₁, v₃}", "{v₀, v₂, v₃}"], 290),
        ("Розмір |S| = N", ["{v₀, v₁, ..., vₙ₋₁}"], 370)
    ]

    for label, states, y_pos in levels:
        frags.append(text(110, y_pos+5, label, size=11, bold=True, color="#475569", anchor="start"))
        
        n_st = len(states)
        step = 460 / (n_st + 1)
        for idx, st_name in enumerate(states):
            x_st = 270 + (idx + 1) * step
            b, _, _ = textbox(x_st, y_pos, st_name, size=11, bold=True, fill="#ffffff", stroke=BLUE_S)
            frags.append(b)

    frags.append(line(500, 145, 385, 195, color="#cbd5e1", sw=1.5))
    frags.append(line(500, 145, 500, 195, color="#cbd5e1", sw=1.5))
    frags.append(line(500, 145, 615, 195, color="#cbd5e1", sw=1.5))

    frags.append(line(385, 225, 385, 275, color=CYAN_S, sw=2.0))
    frags.append(line(500, 225, 385, 275, color=CYAN_S, sw=2.0))
    frags.append(line(615, 225, 615, 275, color=CYAN_S, sw=2.0))

    lx = 660
    frags.append(rect(lx, 115, 155, 290, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 77, 138, "Особливості", size=13, bold=True, color="#1e293b"))

    frags.append(text(lx + 12, 175, "Часова складність:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 195, "O(2ⁿ · n²)", size=12, bold=True, color=RED_S, anchor="start"))

    frags.append(text(lx + 12, 235, "Просторова пам'ять:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 255, "O(2ⁿ · n)", size=12, bold=True, color=AMBER_S, anchor="start"))

    frags.append(text(lx + 12, 295, "Максимальний n:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 315, "n ≤ 30..32", size=12, bold=True, color=GREEN_S, anchor="start"))

    frags.append(text(lx + 12, 355, "Прискорення від n!:", size=10, bold=True, color="#334155", anchor="start"))
    frags.append(text(lx + 12, 375, "в ~10¹² разів", size=11, bold=True, color=PURPLE_S, anchor="start"))

    render(os.path.join(IMG, "fig5-held-karp-bitmask-dp.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_dodecahedron_icosian_game()
    fig2_eulerian_vs_hamiltonian()
    fig3_dirac_ore_conditions()
    fig4_3sat_to_hc_gadgets()
    fig5_held_karp_bitmask_dp()
    print("Всі фігури успішно згенеровано у напрямку img/")
