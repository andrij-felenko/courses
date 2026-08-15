# -*- coding: utf-8 -*-
"""Фігури для теми «Графи-розширювачі (Expander Graphs)» (book/algorithms/complexity-computability/expander-graphs)."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import rect, circle, line, text, textbox, render

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
RED_F, RED_S = "#fef2f2", "#dc2626"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_vertex_edge_expansion():
    """fig1-vertex-edge-expansion.svg: Порівняння графа з вузьким місцем та графа-розширювача."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Порівняння розширення: Граф із вузьким місцем vs Граф-розширювач", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Низьке розширення (мостове з'єднання)
    frags.append(rect(30, 60, 390, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(225, 85, "Низьке розширення h(G) ≈ 0 (Мост)", size=14, bold=True, color=RED_S))

    left_cluster1 = [(80, 150), (140, 130), (120, 200), (70, 210), (140, 260)]
    left_cluster2 = [(310, 150), (370, 130), (350, 200), (300, 210), (370, 260)]

    for x, y in left_cluster1:
        frags.append(circle(x, y, 16, fill=BLUE_F, stroke=BLUE_S, sw=1.8))
    for x, y in left_cluster2:
        frags.append(circle(x, y, 16, fill=RED_F, stroke=RED_S, sw=1.8))

    # Внутрішні ребра лівого кластера
    for i in range(len(left_cluster1)):
        for j in range(i + 1, len(left_cluster1)):
            x1, y1 = left_cluster1[i]
            x2, y2 = left_cluster1[j]
            frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.2))

    # Внутрішні ребра правого кластера
    for i in range(len(left_cluster2)):
        for j in range(i + 1, len(left_cluster2)):
            x1, y1 = left_cluster2[i]
            x2, y2 = left_cluster2[j]
            frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.2))

    # Єдине вузьке ребро (мост)
    frags.append(line(140, 200, 350, 200, color=RED_S, sw=3.0, dash="5 3"))

    b_low, _, _ = textbox(225, 335, "Вузьке місце: розріз S |S|=5, e(S,S̄)=1\nh(G) = 1/5 = 0.2\nЛегко розділити на ізольовані частини", size=11, fill=RED_F, stroke=RED_S, pad=8)
    frags.append(b_low)

    # Права панель: Високе розширення (Граф-розширювач)
    frags.append(rect(460, 60, 390, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(655, 85, "Високе розширення h(G) ≥ α > 0", size=14, bold=True, color=GREEN_S))

    right_nodes_S = [(530, 130), (510, 200), (540, 270), (500, 320)]
    right_nodes_Sbar = [(740, 120), (780, 180), (760, 250), (790, 310), (710, 330)]

    for x, y in right_nodes_S:
        frags.append(circle(x, y, 16, fill=BLUE_F, stroke=BLUE_S, sw=1.8))
    for x, y in right_nodes_Sbar:
        frags.append(circle(x, y, 16, fill=GREEN_F, stroke=GREEN_S, sw=1.8))

    # Багато перехресних ребер між S і Sbar
    cross_edges = [
        ((530, 130), (740, 120)), ((530, 130), (780, 180)),
        ((510, 200), (740, 120)), ((510, 200), (760, 250)), ((510, 200), (710, 330)),
        ((540, 270), (760, 250)), ((540, 270), (790, 310)),
        ((500, 320), (710, 330)), ((500, 320), (790, 310))
    ]
    for (x1, y1), (x2, y2) in cross_edges:
        frags.append(line(x1, y1, x2, y2, color=GREEN_S, sw=1.8))

    b_high, _, _ = textbox(655, 335, "Розширювач: для будь-якого S (|S| ≤ n/2)\nкількість вихідних ребер e(S,S̄) ≥ d·|S|/2\nВідсутні вузькі місця, висока зв'язність", size=11, fill=GREEN_F, stroke=GREEN_S, pad=8)
    frags.append(b_high)

    render(os.path.join(IMG, "fig1-vertex-edge-expansion.svg"), W, H, *frags)


def fig_spectral_gap_distribution():
    """fig2-spectral-gap-distribution.svg: Спектр власних значень d-регулярного графа та спектральна щілина."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Спектр власних значень матриці суміжності d-регулярного графа", size=16, bold=True, color="#1e293b"))

    # Осі спектра від -d до +d
    frags.append(line(80, 200, 800, 200, color="#475569", sw=2.0)) # Головна вісь
    frags.append(line(80, 180, 80, 220, color="#475569", sw=2.0))   # Позначка -d
    frags.append(line(800, 180, 800, 220, color="#475569", sw=2.0)) # Позначка +d (λ1)
    frags.append(line(440, 190, 440, 210, color="#94a3b8", sw=1.5)) # Нуль

    frags.append(text(80, 240, "λₙ = -d", size=13, bold=True, color=RED_S))
    frags.append(text(440, 240, "0", size=13, color="#64748b"))
    frags.append(text(800, 240, "λ₁ = d", size=14, bold=True, color=BLUE_S))

    # Спектральна щілина gamma = d - λ2
    lambda2_x = 620
    frags.append(line(lambda2_x, 170, lambda2_x, 230, color=PURPLE_S, sw=2.5))
    frags.append(text(lambda2_x, 240, "λ₂", size=14, bold=True, color=PURPLE_S))

    # Інші власні значення
    other_lambdas = [150, 210, 280, 350, 400, 470, 520, 570]
    for lx in other_lambdas:
        frags.append(line(lx, 190, lx, 210, color="#64748b", sw=1.5))

    # Інтервал спектральної щілини (між λ2 та λ1)
    frags.append(rect(lambda2_x, 140, 800 - lambda2_x, 30, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=4))
    frags.append(text((lambda2_x + 800) / 2, 160, "Спектральна щілина γ = d - λ₂", size=12, bold=True, color=PURPLE_S))

    # Межа Алона — Боппани 2√(d-1)
    alon_x = 580
    frags.append(line(alon_x, 80, alon_x, 200, color=GREEN_S, sw=2.0, dash="4 3"))
    
    b_alon, _, _ = textbox(420, 100, "Межа Алона — Боппани:\nдля нескінченних сімейств d-регулярних графів\nlim inf λ₂ ≥ 2√(d - 1).\nГрафи Рамануджана: λ₂ ≤ 2√(d - 1)", size=11, fill=GREEN_F, stroke=GREEN_S, pad=8)
    frags.append(b_alon)

    b_summary, _, _ = textbox(440, 310, "Чим більша спектральна щілина γ = d - λ₂, тим швидше випадкове блукання збігається до стаціонарного розподілу U = (1/n, ..., 1/n)", size=11, fill=AMBER_F, stroke=AMBER_S, pad=8)
    frags.append(b_summary)

    render(os.path.join(IMG, "fig2-spectral-gap-distribution.svg"), W, H, *frags)


def fig_expander_mixing_lemma():
    """fig3-expander-mixing-lemma.svg: Розподіл ребер між множинами S та T відповідно до Expander Mixing Lemma."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Лема про змішування розширювачів (Expander Mixing Lemma)", size=16, bold=True, color="#1e293b"))

    # Множина V (Весь граф)
    frags.append(rect(40, 60, 480, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(280, 85, "Множина вершин графа V (|V| = n)", size=14, bold=True, color="#334155"))

    # Множина S
    frags.append(rect(80, 110, 160, 220, fill=BLUE_F, stroke=BLUE_S, sw=2.0, rx=6))
    frags.append(text(160, 135, "Множина S", size=13, bold=True, color=BLUE_S))

    # Множина T
    frags.append(rect(320, 110, 160, 220, fill=GREEN_F, stroke=GREEN_S, sw=2.0, rx=6))
    frags.append(text(400, 135, "Множина T", size=13, bold=True, color=GREEN_S))

    # Ребра між S та T
    edges_st = [
        ((240, 160), (320, 160)),
        ((240, 190), (320, 210)),
        ((240, 220), (320, 170)),
        ((240, 250), (320, 260)),
        ((240, 280), (320, 290))
    ]
    for p1, p2 in edges_st:
        frags.append(line(p1[0], p1[1], p2[0], p2[1], color=PURPLE_S, sw=2.2))

    frags.append(text(280, 215, "e(S, T)", size=13, bold=True, color=PURPLE_S))

    # Формула Лемми про змішування
    b_formula, _, _ = textbox(690, 160, "Expander Mixing Lemma:\n\n| e(S,T) - (d/n)·|S|·|T| | ≤ λ₂ · √(|S|·|T|)\n\n• (d/n)·|S|·|T| — очікувана кількість\n  ребер у випадковому графі G(n, p=d/n)\n\n• λ₂ — друге за величиною власне значення\n  матриці суміжності\n\nВисновок: чим менше λ₂, тим більше\nструктура ребер схожа на випадковий граф!", size=11, fill=PURPLE_F, stroke=PURPLE_S, pad=12)
    frags.append(b_formula)

    render(os.path.join(IMG, "fig3-expander-mixing-lemma.svg"), W, H, *frags)


def fig_zigzag_product():
    """fig4-zigzag-product.svg: Схема Зіг-Заг добутку графів G ∘ H."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Конструкція Зіг-Заг добутку G ∘ H (Reingold-Vadhan-Wigderson)", size=16, bold=True, color="#1e293b"))

    # Блок графа G
    frags.append(rect(40, 70, 240, 280, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(160, 95, "Великий граф G", size=14, bold=True, color=BLUE_S))
    frags.append(text(160, 120, "N вершин, степінь D", size=12, color="#334155"))

    # Блок графа H
    frags.append(rect(320, 70, 240, 280, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(440, 95, "Малий розширювач H", size=14, bold=True, color=GREEN_S))
    frags.append(text(440, 120, "D вершин, степінь d", size=12, color="#334155"))

    # Символ Зіг-Заг добутку ∘
    frags.append(circle(290, 210, 18, fill="#ffffff", stroke="#475569", sw=2.0))
    frags.append(text(290, 214, "∘", size=18, bold=True, color="#1e293b"))

    # Результат G ∘ H
    frags.append(rect(600, 70, 240, 280, fill=PURPLE_F, stroke=PURPLE_S, sw=2.0, rx=8))
    frags.append(text(720, 95, "Добуток G ∘ H", size=14, bold=True, color=PURPLE_S))
    
    info_result = "Властивості результату:\n• Кількість вершин: N · D\n• Степінь: d² (постійний!)\n• Спектральна щілина:\n  успадковує розширення H\n  та графа G\n\nКрок Zig-Zag блукання:\n1. Крок у копії H (степінь d)\n2. Крок по ребу G (степінь D)\n3. Крок у копії H (степінь d)"
    b_res, _, _ = textbox(720, 235, info_result, size=11, fill="#ffffff", stroke=PURPLE_S, pad=8)
    frags.append(b_res)

    render(os.path.join(IMG, "fig4-zigzag-product.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_vertex_edge_expansion()
    fig_spectral_gap_distribution()
    fig_expander_mixing_lemma()
    fig_zigzag_product()
    print("Figures generated successfully!")
