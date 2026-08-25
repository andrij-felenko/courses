# -*- coding: utf-8 -*-
"""Фігури для теми «Двочастковий граф» (book/algorithms/complexity-computability/bipartite-graph)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
RED_F, RED_S = "#fef2f2", "#dc2626"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_bipartite_concept():
    """fig1-bipartite-concept.svg: Базова структура двочасткового графа з частками U та V."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Структура двочасткового графа G = (U ∪ V, E)", size=16, bold=True, color="#1e293b"))

    frags.append(rect(40, 60, 240, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(160, 85, "Частка U (Ліві вершини)", size=14, bold=True, color=BLUE_S))

    frags.append(rect(360, 60, 240, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(480, 85, "Частка V (Праві вершини)", size=14, bold=True, color=GREEN_S))

    u_nodes = [
        (160, 130, "u₁"),
        (160, 195, "u₂"),
        (160, 260, "u₃"),
        (160, 325, "u₄"),
    ]
    for x, y, lbl in u_nodes:
        frags.append(circle(x, y, 22, fill="#ffffff", stroke=BLUE_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=BLUE_S))

    v_nodes = [
        (480, 130, "v₁"),
        (480, 195, "v₂"),
        (480, 260, "v₃"),
        (480, 325, "v₄"),
    ]
    for x, y, lbl in v_nodes:
        frags.append(circle(x, y, 22, fill="#ffffff", stroke=GREEN_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=GREEN_S))

    edges = [
        ((160, 130), (480, 130)), # u1 - v1
        ((160, 130), (480, 195)), # u1 - v2
        ((160, 195), (480, 195)), # u2 - v2
        ((160, 195), (480, 260)), # u2 - v3
        ((160, 260), (480, 130)), # u3 - v1
        ((160, 260), (480, 325)), # u3 - v4
        ((160, 325), (480, 260)), # u4 - v3
    ]
    for (x1, y1), (x2, y2) in edges:
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        ux, uy = dx/dist, dy/dist
        sx, sy = x1 + ux*22, y1 + uy*22
        ex, ey = x2 - ux*22, y2 - uy*22
        frags.append(line(sx, sy, ex, ey, color="#475569", sw=1.8))

    panel_txt = "Формальні умови:\n• V = U ∪ V, U ∩ V = ∅\n• E ⊆ U × V (усі ребра між частками)\n• Немає внутрішніх ребер (uᵢ, uⱼ)\n• Хроматичне число χ(G) ≤ 2\n• Жодного непарного циклу C₂ₖ₊₁"
    b_p, _, _ = textbox(740, 225, panel_txt, size=11, fill="#f1f5f9", stroke="#475569", pad=12)
    frags.append(b_p)

    render(os.path.join(IMG, "fig1-bipartite-concept.svg"), W, H, *frags)


def fig_odd_cycle_conflict():
    """fig2-odd-cycle-conflict.svg: Конфлікт двоколірного розфарбовування на непарному циклі C5."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Неможливість 2-розфарбування на непарному циклі (C₅)", size=16, bold=True, color="#1e293b"))

    import math
    cx, cy, r = 280, 210, 110
    coords = []
    colors_fill = [BLUE_F, RED_F, BLUE_F, RED_F, BLUE_F]
    colors_stroke = [BLUE_S, RED_S, BLUE_S, RED_S, BLUE_S]
    labels = ["v₁", "v₂", "v₃", "v₄", "v₅"]

    for i in range(5):
        angle = -math.pi/2 + i * 2 * math.pi / 5
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        coords.append((x, y))

    for i in range(5):
        j = (i + 1) % 5
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        ux, uy = dx/dist, dy/dist
        sx, sy = x1 + ux*22, y1 + uy*22
        ex, ey = x2 - ux*22, y2 - uy*22
        
        if (i == 4 and j == 0) or (i == 0 and j == 4):
            frags.append(line(sx, sy, ex, ey, color=RED_S, sw=3.5, dash="6 3"))
        else:
            frags.append(line(sx, sy, ex, ey, color="#475569", sw=1.8))

    for i, (x, y) in enumerate(coords):
        frags.append(circle(x, y, 22, fill=colors_fill[i], stroke=colors_stroke[i], sw=2.2))
        frags.append(text(x, y + 4, labels[i], size=13, bold=True, color=colors_stroke[i]))

    b_conf, _, _ = textbox(580, 160, "КОНФЛІКТ 2-РОЗФАРБОВУВАННЯ!\nРебро (v₅, v₁) з'єднує дві вершини\nоднакового Кольору 0 (Синій).\n\nНаслідок: непарний цикл C₅ унеможливлює\nрозбиття графа на дві незалежні частки.", size=12, fill=RED_F, stroke=RED_S, pad=12, bold=False)
    frags.append(b_conf)

    b_rule, _, _ = textbox(580, 300, "Теорема Кеніга (1916):\nГраф є двочастковим ⇔ він НЕ містить\nжодного непарного циклу будь-якої довжини.", size=12, fill=AMBER_F, stroke=AMBER_S, pad=10)
    frags.append(b_rule)

    render(os.path.join(IMG, "fig2-odd-cycle-conflict.svg"), W, H, *frags)


def fig_bfs_coloring():
    """fig3-bfs-coloring.svg: Процес BFS-розфарбовування за рівнями відстані від старту."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгоритм BFS-розфарбовування вершин за рівнями відстані", size=16, bold=True, color="#1e293b"))

    # Рівень 0
    frags.append(rect(40, 65, 780, 80, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(120, 110, "Рівень d = 0\n(Колір 0)", size=12, bold=True, color=BLUE_S))
    frags.append(circle(260, 105, 20, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(260, 109, "r", size=13, bold=True, color=BLUE_S))

    # Рівень 1
    frags.append(rect(40, 160, 780, 90, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(120, 210, "Рівень d = 1\n(Колір 1)", size=12, bold=True, color=GREEN_S))
    l1_nodes = [(260, 205, "a"), (440, 205, "b"), (660, 205, "c")]
    for x, y, lbl in l1_nodes:
        frags.append(circle(x, y, 20, fill=GREEN_F, stroke=GREEN_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=GREEN_S))

    # Рівень 2
    frags.append(rect(40, 265, 780, 90, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(120, 315, "Рівень d = 2\n(Колір 0)", size=12, bold=True, color=BLUE_S))
    l2_nodes = [(260, 310, "d"), (440, 310, "e"), (660, 310, "f")]
    for x, y, lbl in l2_nodes:
        frags.append(circle(x, y, 20, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=BLUE_S))

    # Деревні ребра
    tree_edges = [
        ((260, 105), (260, 205)), # r - a
        ((260, 105), (440, 205)), # r - b
        ((260, 105), (660, 205)), # r - c
        ((260, 205), (260, 310)), # a - d
        ((440, 205), (440, 310)), # b - e
        ((660, 205), (660, 310)), # c - f
    ]
    for (x1, y1), (x2, y2) in tree_edges:
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        ux, uy = dx/dist, dy/dist
        frags.append(line(x1 + ux*20, y1 + uy*20, x2 - ux*20, y2 - uy*20, color="#475569", sw=1.8))

    # Перекресне ребро в межах одного рівня
    frags.append(line(460, 205, 640, 205, color=RED_S, sw=2.2, dash="4 3"))
    
    # Використовуємо textbox для попередження, щоб воно не перетиналося з лініями
    b_edge_warn, _, _ = textbox(550, 175, "Ребро (b, c) однакового Кольору 1!", size=10, fill=RED_F, stroke=RED_S, pad=4)
    frags.append(b_edge_warn)

    frags.append(text(440, 380, "Правило: ребра між d і d+1 завжди з'єднують протилежні кольори. Ребро в межах одного рівня d руйнує двочастковість.", size=11, italic=True, color="#334155"))

    render(os.path.join(IMG, "fig3-bfs-coloring.svg"), W, H, *frags)


def fig_konig_matching_cover():
    """fig4-konig-matching-cover.svg: Двоїстість максимального паросполучення та мінімального вершинного покриття (Теорема Кеніга)."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Теорема Кеніга (1931): Двоїстість ν(G) = τ(G) у двочасткових графах", size=16, bold=True, color="#1e293b"))

    u_nodes = [(180, 110, "u₁"), (180, 200, "u₂"), (180, 290, "u₃")]
    v_nodes = [(460, 110, "v₁"), (460, 200, "v₂"), (460, 290, "v₃")]

    cover_highlights = [(180, 110), (180, 200), (460, 290)]
    for x, y in cover_highlights:
        frags.append(circle(x, y, 28, fill=PURPLE_F, stroke=PURPLE_S, sw=2.0))

    normal_edges = [
        ((180, 110), (460, 200)), # u1 - v2
        ((180, 200), (460, 200)), # u2 - v2
        ((180, 290), (460, 290)), # u3 - v3
    ]
    for (x1, y1), (x2, y2) in normal_edges:
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        ux, uy = dx/dist, dy/dist
        frags.append(line(x1 + ux*22, y1 + uy*22, x2 - ux*22, y2 - uy*22, color="#94a3b8", sw=1.5))

    matching_edges = [
        ((180, 110), (460, 110)), # u1 - v1
        ((180, 200), (460, 200)), # u2 - v2
        ((180, 290), (460, 290)), # u3 - v3
    ]
    for (x1, y1), (x2, y2) in matching_edges:
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        ux, uy = dx/dist, dy/dist
        frags.append(line(x1 + ux*22, y1 + uy*22, x2 - ux*22, y2 - uy*22, color=GREEN_S, sw=3.5))

    for x, y, lbl in u_nodes:
        frags.append(circle(x, y, 20, fill="#ffffff", stroke=BLUE_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=BLUE_S))

    for x, y, lbl in v_nodes:
        frags.append(circle(x, y, 20, fill="#ffffff", stroke=GREEN_S, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=13, bold=True, color=GREEN_S))

    panel_txt = "Оптимальні величини:\n• Максимальне паросполучення |M|:\n  M = {(u₁, v₁), (u₂, v₂), (u₃, v₃)}\n  ν(G) = 3 (жирні зелені ребра)\n\n• Мінімальне вершинне покриття C:\n  C = {u₁, u₂, v₃} (фіолетовий ореол)\n  τ(G) = 3 (покриває всі ребра)\n\n• Рівність Кеніга: ν(G) = τ(G) = 3"
    b_panel, _, _ = textbox(710, 200, panel_txt, size=11, fill="#ffffff", stroke=PURPLE_S, pad=12)
    frags.append(b_panel)

    render(os.path.join(IMG, "fig4-konig-matching-cover.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_bipartite_concept()
    fig_odd_cycle_conflict()
    fig_bfs_coloring()
    fig_konig_matching_cover()
