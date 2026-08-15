# -*- coding: utf-8 -*-
"""Фігури для теми «Ізоморфізм графів» (book/algorithms/complexity-computability/graph-isomorphism)."""
import sys, os
import math

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


def fig_isomorphism_concept():
    """fig1-isomorphism-concept.svg: Поняття ізоморфізму графів та перестановка матриці суміжності."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Поняття ізоморфізму графів G₁ ≅ G₂ та бієкція вершин π", size=16, bold=True, color="#1e293b"))

    # Лівий граф G1 (форма шестикутника з трьома діагоналями)
    frags.append(rect(30, 55, 270, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(165, 78, "Граф G₁ (вершини 1..6)", size=13, bold=True, color=BLUE_S))

    cx1, cy1, r1 = 165, 185, 80
    g1_nodes = []
    g1_lbls = ["1", "2", "3", "4", "5", "6"]
    for i in range(6):
        ang = -math.pi / 2 + i * math.pi / 3
        x = cx1 + r1 * math.cos(ang)
        y = cy1 + r1 * math.sin(ang)
        g1_nodes.append((x, y))

    g1_edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),
        (0, 3), (1, 4), (2, 5)
    ]
    for i, j in g1_edges:
        x1, y1 = g1_nodes[i]
        x2, y2 = g1_nodes[j]
        frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.5))

    for i, (x, y) in enumerate(g1_nodes):
        frags.append(circle(x, y, 16, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
        frags.append(text(x, y + 4, g1_lbls[i], size=12, bold=True, color=BLUE_S))

    # Стрілка ізоморфізму в центрі
    frags.append(line(315, 185, 365, 185, color=PURPLE_S, sw=2.5))
    frags.append('<polygon points="365,179 377,185 365,191" fill="%s" stroke="%s" stroke-width="1.0"/>' % (PURPLE_S, PURPLE_S))
    frags.append(text(342, 172, "π", size=16, bold=True, color=PURPLE_S))

    # Правий граф G2 (інше візуальне розташування тих самих 6 вершин)
    frags.append(rect(390, 55, 270, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(525, 78, "Граф G₂ (вершини a..f)", size=13, bold=True, color=GREEN_S))

    # П'ятикутник + центр
    cx2, cy2, r2 = 525, 190, 75
    g2_nodes = []
    g2_lbls = ["a", "b", "c", "d", "e", "f"]
    for i in range(5):
        ang = -math.pi / 2 + i * 2 * math.pi / 5
        x = cx2 + r2 * math.cos(ang)
        y = cy2 + r2 * math.sin(ang)
        g2_nodes.append((x, y))
    g2_nodes.append((cx2, cy2)) # f у центрі

    # Бієкція: 1->c(2), 2->a(0), 3->f(5), 4->b(1), 5->e(4), 6->d(3)
    g2_edges = [
        (2, 0), (0, 5), (5, 1), (1, 4), (4, 3), (3, 2),
        (2, 1), (0, 4), (5, 3)
    ]
    for i, j in g2_edges:
        x1, y1 = g2_nodes[i]
        x2, y2 = g2_nodes[j]
        frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.5))

    for i, (x, y) in enumerate(g2_nodes):
        frags.append(circle(x, y, 16, fill=GREEN_F, stroke=GREEN_S, sw=2.0))
        frags.append(text(x, y + 4, g2_lbls[i], size=12, bold=True, color=GREEN_S))

    # Панель праворуч (Матричне поняття та зберігання суміжності)
    info_txt = "Таблиця бієкції π:\n1 ↦ c | 2 ↦ a | 3 ↦ f\n4 ↦ b | 5 ↦ e | 6 ↦ d\n\nАлгебраїчний критерій:\nP · A(G₁) · Pᵀ = A(G₂)\nде P — матриця перестановки.\n(u, v) ∈ E(G₁) ⇔ (π(u), π(v)) ∈ E(G₂)"
    b_info, _, _ = textbox(775, 185, info_txt, size=11, fill=PURPLE_F, stroke=PURPLE_S, pad=10)
    frags.append(b_info)

    # Нижній пояснювальний підпис
    frags.append(text(440, 385, "Ізоморфізм зберігає зв'язність і структурні властивості, незважаючи на зміну міток чи геометрії.", size=11, italic=True, color="#334155"))

    render(os.path.join(IMG, "fig1-isomorphism-concept.svg"), W, H, *frags)


def fig_weisfeiler_leman():
    """fig2-weisfeiler-leman.svg: Ітеративне перефарбовування вершин в алгоритмі 1-WL."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Алгоритм 1-WL (Color Refinement): від степенів до стабільної розбивки", size=16, bold=True, color="#1e293b"))

    # Крок 0: Початкове розфарбування (за степенями)
    frags.append(rect(30, 60, 240, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(150, 82, "Крок 0: c⁽⁰⁾(v) = deg(v)", size=12, bold=True, color=BLUE_S))
    
    # 4 вершини
    s0_nodes = [(90, 130, "1", "deg 2", BLUE_F, BLUE_S),
                (210, 130, "2", "deg 3", GREEN_F, GREEN_S),
                (90, 240, "3", "deg 2", BLUE_F, BLUE_S),
                (210, 240, "4", "deg 3", GREEN_F, GREEN_S)]
    
    s0_edges = [(0, 1), (1, 2), (2, 3), (3, 1)] # 1-2, 2-3, 3-4, 4-2
    for i, j in s0_edges:
        frags.append(line(s0_nodes[i][0], s0_nodes[i][1], s0_nodes[j][0], s0_nodes[j][1], color="#cbd5e1", sw=1.5))
    for x, y, lbl, sub, ff, fs in s0_nodes:
        frags.append(circle(x, y, 18, fill=ff, stroke=fs, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=12, bold=True, color=fs))

    # Стрілка 1
    frags.append(line(275, 190, 305, 190, color="#64748b", sw=2.0))
    frags.append('<polygon points="305,185 315,190 305,195" fill="#64748b" stroke="#64748b" stroke-width="1.0"/>')

    # Крок 1: Збирання мультимножини сусідів
    frags.append(rect(320, 60, 250, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(445, 82, "Крок 1: H(c⁽⁰⁾(v), {{c⁽⁰⁾(u)}})", size=12, bold=True, color=PURPLE_S))
    
    s1_txt = "Мультимножини:\n• v₁: (2, {{3, 3}})\n• v₂: (3, {{2, 2, 3}})\n• v₃: (2, {{2, 3}})\n• v₄: (3, {{2, 3, 3}})"
    b_s1, _, _ = textbox(445, 190, s1_txt, size=11, fill=PURPLE_F, stroke=PURPLE_S, pad=10)
    frags.append(b_s1)

    # Стрілка 2
    frags.append(line(575, 190, 605, 190, color="#64748b", sw=2.0))
    frags.append('<polygon points="605,185 615,190 605,195" fill="#64748b" stroke="#64748b" stroke-width="1.0"/>')

    # Крок 2: Нове розфарбування та стабілізація
    frags.append(rect(620, 60, 230, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(735, 82, "Крок 2: Стабільні кольори", size=12, bold=True, color=GREEN_S))

    s2_nodes = [(670, 130, "v₁", "C₁", BLUE_F, BLUE_S),
                (790, 130, "v₂", "C₂", GREEN_F, GREEN_S),
                (670, 240, "v₃", "C₃", AMBER_F, AMBER_S),
                (790, 240, "v₄", "C₄", RED_F, RED_S)]
    for i, j in s0_edges:
        frags.append(line(s2_nodes[i][0], s2_nodes[i][1], s2_nodes[j][0], s2_nodes[j][1], color="#cbd5e1", sw=1.5))
    for x, y, lbl, sub, ff, fs in s2_nodes:
        frags.append(circle(x, y, 18, fill=ff, stroke=fs, sw=2.0))
        frags.append(text(x, y + 4, lbl, size=11, bold=True, color=fs))
        frags.append(text(x, y + 34, sub, size=10, bold=True, color=fs))

    # Нижній опис обмежень WL
    bot_txt = "Властивість 1-WL: розрізняє майже всі випадкові графи за O((V+E) log V). Проте існує неізоморфна пара графа Cai-Fürer-Immerman (CFI),\nде 1-WL (і загалом k-WL для фіксованого k) дає однаковий гістограмний підпис кольорів."
    b_bot, _, _ = textbox(440, 365, bot_txt, size=11, fill="#f1f5f9", stroke="#475569", pad=8)
    frags.append(b_bot)

    render(os.path.join(IMG, "fig2-weisfeiler-leman.svg"), W, H, *frags)


def fig_search_tree_nauty():
    """fig3-search-tree-nauty.svg: Дерево індивідуалізації та ущільнення в Nauty/Traces."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Дерево індивідуалізації-ущільнення (Nauty / Traces)", size=16, bold=True, color="#1e293b"))

    # Корінь
    frags.append(rect(340, 60, 200, 45, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(440, 82, "Початкова розбивка π₀\n[v₁ v₂ v₃ | v₄ v₅ v₆]", size=11, bold=True, color=BLUE_S))

    # Ліва та права гілки (Індивідуалізація вершини з цільового осередку)
    frags.append(line(410, 105, 230, 160, color="#64748b", sw=1.5))
    frags.append(text(300, 125, "Індивідуалізація v₁", size=10, bold=True, color="#475569"))

    frags.append(line(470, 105, 650, 160, color="#64748b", sw=1.5))
    frags.append(text(580, 125, "Індивідуалізація v₂", size=10, bold=True, color="#475569"))

    # Вузол L1
    frags.append(rect(130, 160, 200, 45, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=6))
    frags.append(text(230, 182, "Осередок {v₁} зафіксовано\nУщільнення WL → π₁", size=11, bold=True, color=PURPLE_S))

    # Вузол R1
    frags.append(rect(550, 160, 200, 45, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=6))
    frags.append(text(650, 182, "Осередок {v₂} зафіксовано\nУщільнення WL → π₁'", size=11, bold=True, color=PURPLE_S))

    # Пунктирна стрілка автоморфізму (Pruning)
    frags.append(line(330, 182, 550, 182, color=RED_S, sw=2.0, dash="5 3"))
    frags.append(text(440, 172, "Автоморфізм γ ∈ Aut(G) → Відсікання!", size=10, bold=True, color=RED_S))

    # Лісткові вузли
    frags.append(line(200, 205, 140, 270, color="#64748b", sw=1.5))
    frags.append(rect(50, 270, 180, 45, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(140, 292, "Канонічний листок L*\nМінімальний хеш графа", size=11, bold=True, color=GREEN_S))

    frags.append(line(260, 205, 320, 270, color="#64748b", sw=1.5))
    frags.append(rect(250, 270, 160, 45, fill=GRAY_F, stroke=GRAY_S, sw=1.0, rx=6))
    frags.append(text(330, 292, "Листок L₂\n(гірший канонічний код)", size=10, color=GRAY_S))

    # Панель з описом
    desc_txt = "Основні етапи Nauty:\n1. Вибір цільового осередку (Target Cell Selection).\n2. Індивідуалізація (фіксація вершини) та ущільнення WL.\n3. Обчислення канонічного підпису на листках дерева.\n4. Виявлення автоморфізмів для геометричного відсікання гілок дерева пошуку."
    b_desc, _, _ = textbox(650, 290, desc_txt, size=11, fill="#ffffff", stroke="#64748b", pad=10)
    frags.append(b_desc)

    frags.append(text(440, 385, "Завдяки генераторам групи автоморфізмів Aut(G) дерево пошуку скорочується з O(n!) до декількох кроків.", size=11, italic=True, color="#334155"))

    render(os.path.join(IMG, "fig3-search-tree-nauty.svg"), W, H, *frags)


def fig_complexity_landscape():
    """fig4-complexity-landscape.svg: Ієрархія класів складності та статус задачі GI."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Обчислювальний статус задачі Graph Isomorphism (GI)", size=16, bold=True, color="#1e293b"))

    # Зони класичної складності
    # Зовнішній прямокутник NP
    frags.append(rect(40, 60, 420, 310, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=10))
    frags.append(text(250, 82, "Клас NP (НЕДЕТЕРМІНОВАНИЙ ПОЛІНОМ)", size=13, bold=True, color="#334155"))

    # Підзона NP-Complete
    frags.append(rect(60, 100, 170, 250, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(145, 122, "NP-повні задачі\n(SAT, TSP, 3-Color)", size=11, bold=True, color=RED_S))

    # Підзона P
    frags.append(rect(260, 220, 180, 130, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(350, 242, "Клас P (Поліном)\nShortest Path, Matching", size=11, bold=True, color=GREEN_S))

    # Зона GI (Проміжна або P)
    frags.append(rect(260, 100, 180, 100, fill=AMBER_F, stroke=AMBER_S, sw=2.0, rx=8))
    frags.append(text(350, 125, "Спеціальний клас GI\n(Graph Isomorphism)", size=12, bold=True, color=AMBER_S))
    frags.append(text(350, 145, "Проміжна складність\n(NP ∩ co-AM)", size=10, color=AMBER_S))

    # Права панель з межами складності
    bounds_txt = "Верхні та нижні межі складності GI:\n\n• Квазіполіноміальний верхній час (Бабай, 2015):\n  T(n) = exp(O((log n)ᶜ)) = 2^(O((log n)ᶜ))\n\n• Інтерактивні докази:\n  GNI (Graph Non-Isomorphism) ∈ IP = PSPACE\n  GNI ∈ co-AM ⇒ GI не може бути NP-повною,\n  якщо поліноміальна ієрархія PH не колапсує до Σ₂ᵖ.\n\n• Спеціальні класи графа в P:\n  - Дерева: O(n)\n  - Планарні графи: O(n)\n  - Обмежений степінь: O(nᵖ) (Luks, 1982)"
    b_bounds, _, _ = textbox(670, 215, bounds_txt, size=11, fill=PURPLE_F, stroke=PURPLE_S, pad=12)
    frags.append(b_bounds)

    frags.append(text(440, 385, "Сьогодні GI вважається яскравим прикладом проблеми 'NP-проміжної' складності (теорема Ладнера).", size=11, italic=True, color="#334155"))

    render(os.path.join(IMG, "fig4-complexity-landscape.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_isomorphism_concept()
    fig_weisfeiler_leman()
    fig_search_tree_nauty()
    fig_complexity_landscape()
