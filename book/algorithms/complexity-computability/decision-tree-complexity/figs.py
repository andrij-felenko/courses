# -*- coding: utf-8 -*-
"""Фігури для теми «Складність дерев рішень» (book/algorithms/complexity-computability/decision-tree-complexity)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_decision_tree_model():
    """fig1-decision-tree-model.svg: Модель дерева рішень для булевої функції MAJ(x1, x2, x3)."""
    W, H = 880, 480
    frags = []

    frags.append(rect(10, 10, 860, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Модель дерева рішень для функції більшості MAJ(x₁, x₂, x₃)", size=16, bold=True, color="#1e293b"))

    # Корінь: x1
    b_root, _, _ = textbox(440, 85, "Запит змінної x₁", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S, pad=10)
    frags.append(b_root)

    # Шар 2: x2 (ліва гілка x1=0, права гілка x1=1)
    b_l2, _, _ = textbox(215, 175, "Запит x₂ (при x₁=0)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    b_r2, _, _ = textbox(665, 175, "Запит x₂ (при x₁=1)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    frags.append(b_l2)
    frags.append(b_r2)

    # Ребра від кореня до Шару 2
    frags.append(line(360, 100, 245, 155, color="#64748b", sw=2))
    frags.append(text(285, 120, "x₁ = 0", size=11, bold=True, color="#dc2626"))

    frags.append(line(520, 100, 635, 155, color="#64748b", sw=2))
    frags.append(text(595, 120, "x₁ = 1", size=11, bold=True, color="#16a34a"))

    # Гілки від x2 (ліворуч):
    leaf_01, _, _ = textbox(105, 270, "Листок = 0\n(x₁=0, x₂=0)", size=11, bold=True, fill=RED_F, stroke=RED_S, pad=7)
    b_l3, _, _ = textbox(285, 270, "Запит x₃ (при x₁=0, x₂=1)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=7)
    frags.append(leaf_01)
    frags.append(b_l3)

    frags.append(line(175, 195, 120, 245, color="#64748b", sw=1.8))
    frags.append(text(135, 215, "x₂ = 0", size=10, bold=True, color="#dc2626"))

    frags.append(line(255, 195, 275, 245, color="#64748b", sw=1.8))
    frags.append(text(280, 215, "x₂ = 1", size=10, bold=True, color="#16a34a"))

    # Гілки від x2 (праворуч):
    b_r3, _, _ = textbox(595, 270, "Запит x₃ (при x₁=1, x₂=0)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=7)
    leaf_11, _, _ = textbox(775, 270, "Листок = 1\n(x₁=1, x₂=1)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=7)
    frags.append(b_r3)
    frags.append(leaf_11)

    frags.append(line(625, 195, 605, 245, color="#64748b", sw=1.8))
    frags.append(text(600, 215, "x₂ = 0", size=10, bold=True, color="#dc2626"))

    frags.append(line(705, 195, 760, 245, color="#64748b", sw=1.8))
    frags.append(text(745, 215, "x₂ = 1", size=10, bold=True, color="#16a34a"))

    # Гілки від x3 під b_l3 (x3=0 та x3=1):
    leaf_l3_0, _, _ = textbox(215, 375, "Листок = 0\n(x₁=0, x₂=1, x₃=0)", size=10, bold=True, fill=RED_F, stroke=RED_S, pad=5)
    leaf_l3_1, _, _ = textbox(365, 375, "Листок = 1\n(x₁=0, x₂=1, x₃=1)", size=10, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=5)
    frags.append(leaf_l3_0)
    frags.append(leaf_l3_1)

    frags.append(line(260, 290, 230, 355, color="#64748b", sw=1.5))
    frags.append(text(230, 320, "x₃=0", size=10, color="#dc2626"))

    frags.append(line(310, 290, 350, 355, color="#64748b", sw=1.5))
    frags.append(text(345, 320, "x₃=1", size=10, color="#16a34a"))

    # Гілки від x3 під b_r3 (x3=0 та x3=1):
    leaf_r3_0, _, _ = textbox(515, 375, "Листок = 0\n(x₁=1, x₂=0, x₃=0)", size=10, bold=True, fill=RED_F, stroke=RED_S, pad=5)
    leaf_r3_1, _, _ = textbox(665, 375, "Листок = 1\n(x₁=1, x₂=0, x₃=1)", size=10, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=5)
    frags.append(leaf_r3_0)
    frags.append(leaf_r3_1)

    frags.append(line(570, 290, 530, 355, color="#64748b", sw=1.5))
    frags.append(text(535, 320, "x₃=0", size=10, color="#dc2626"))

    frags.append(line(620, 290, 650, 355, color="#64748b", sw=1.5))
    frags.append(text(650, 320, "x₃=1", size=10, color="#16a34a"))

    frags.append(rect(40, 425, 800, 35, fill=TEAL_F, stroke=TEAL_S, rx=6))
    frags.append(text(440, 447, "Найгірший шлях = 3 запити (D(MAJ) = 3). Деякі шляхи (сертифікати) завершуються за 2 запити (C(MAJ) = 2).", size=11, bold=True, color="#0f766e"))

    render(os.path.join(IMG, "fig1-decision-tree-model.svg"), W, H, *frags)

def fig_complexity_measures_map():
    """fig2-complexity-measures-map.svg: Карта зв'язків між заходами складності булевих функцій."""
    W, H = 840, 520
    frags = []

    frags.append(rect(10, 10, 820, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Поліноміальні зв'язки між заходами складності булевих функцій", size=16, bold=True, color="#1e293b"))

    b_df, _, _ = textbox(420, 100, "D(f)\nДетермінована складність", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S, pad=10)
    frags.append(b_df)

    b_rf, _, _ = textbox(180, 200, "R(f)\nЙмовірнісна складність", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    frags.append(b_rf)

    b_qf, _, _ = textbox(660, 200, "Q(f)\nКвантова складність", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S, pad=8)
    frags.append(b_qf)

    b_cf, _, _ = textbox(420, 240, "C(f)\nСкладність сертифікатів", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=8)
    frags.append(b_cf)

    b_bs, _, _ = textbox(280, 360, "bs(f)\nБлокова чутливість", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=8)
    frags.append(b_bs)

    b_deg, _, _ = textbox(560, 360, "deg(f)\nСтепінь многочлена", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=8)
    frags.append(b_deg)

    b_sf, _, _ = textbox(420, 450, "s(f)\nЧутливість (Sensitivity)", size=13, bold=True, fill=RED_F, stroke=RED_S, pad=10)
    frags.append(b_sf)

    frags.append(line(330, 115, 230, 180, color="#64748b", sw=1.8))
    frags.append(text(260, 140, "R(f) ≤ D(f) ≤ R(f)³", size=10, color="#7e22ce", bold=True))

    frags.append(line(510, 115, 610, 180, color="#64748b", sw=1.8))
    frags.append(text(580, 140, "Q(f) ≤ D(f) ≤ Q(f)⁶", size=10, color="#0d9488", bold=True))

    frags.append(line(420, 125, 420, 215, color="#64748b", sw=1.8))
    frags.append(text(430, 175, "D(f) ≤ C(f)·bs(f)", size=10, color="#b45309", bold=True))

    frags.append(line(370, 260, 310, 335, color="#64748b", sw=1.8))
    frags.append(text(310, 295, "C(f) ≤ bs(f)²", size=10, color="#b45309", bold=True))

    frags.append(line(470, 260, 530, 335, color="#64748b", sw=1.8))
    frags.append(text(520, 295, "deg(f) ≤ C(f)", size=10, color="#16a34a", bold=True))

    frags.append(line(370, 430, 310, 385, color="#dc2626", sw=2.2))
    frags.append(text(310, 420, "bs(f) ≤ s(f)⁴ (Хуан, 2019)", size=10, color="#dc2626", bold=True))

    frags.append(line(470, 430, 530, 385, color="#dc2626", sw=2.2))
    frags.append(text(530, 420, "deg(f) ≤ s(f)²", size=10, color="#dc2626", bold=True))

    render(os.path.join(IMG, "fig2-complexity-measures-map.svg"), W, H, *frags)

def fig_hypercube_subgraph():
    """fig3-hypercube-subgraph.svg: Гіперкуб Q3 та підграф із 5 вершин для доведення Хуана."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Геометрія доведення Хуана: індукований підграф H у гіперкубі Q₃", size=16, bold=True, color="#1e293b"))

    coords = {
        "000": (240, 300),
        "100": (440, 300),
        "110": (440, 160),
        "010": (240, 160),
        "001": (340, 240),
        "101": (540, 240),
        "111": (540, 100),
        "011": (340, 100)
    }

    edges = [
        ("000","100"), ("100","110"), ("110","010"), ("010","000"),
        ("001","101"), ("101","111"), ("111","011"), ("011","001"),
        ("000","001"), ("100","101"), ("110","111"), ("010","011")
    ]

    H_nodes = {"000", "110", "011", "101", "111"}

    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        if u in H_nodes and v in H_nodes:
            frags.append(line(x1, y1, x2, y2, color="#dc2626", sw=2.5))
        else:
            frags.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=1.5))

    for node, (x, y) in coords.items():
        if node in H_nodes:
            b, _, _ = textbox(x, y, f"{node} ∈ H", size=11, bold=True, fill=RED_F, stroke=RED_S, pad=6)
        else:
            b, _, _ = textbox(x, y, node, size=10, fill="#ffffff", stroke=GRAY_S, pad=5)
        frags.append(b)

    frags.append(rect(610, 80, 200, 310, fill=AMBER_F, stroke=AMBER_S, rx=8))
    frags.append(text(710, 105, "Ключова лема", size=13, bold=True, color="#b45309"))
    frags.append(text(710, 140, "Будь-який підграф H ⊂ Qₙ\nна |H| > 2ⁿ⁻¹ вершин\nмає хоча б одну\nвершину зі ступенем:\n\nΔ(H) ≥ √n", size=11, color="#78350f"))
    frags.append(text(710, 260, "Для n=3:\n2³⁻¹ + 1 = 5 вершин.\nМаксимальний ступінь\nΔ(H) ≥ √3 ≈ 1.73 (тобто 2).", size=10, italic=True, color="#92400e"))
    frags.append(text(710, 350, "Максимальний ступінь Δ(H)\nпрямо визначає\nчутливість s(f)!", size=10, bold=True, color="#dc2626"))

    render(os.path.join(IMG, "fig3-hypercube-subgraph.svg"), W, H, *frags)

def fig_and_or_tree():
    """fig4-and-or-tree.svg: Ймовірнісне прискорення для дерев AND-OR (Снір / Соловей-Сака)."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Дерева AND-OR: Детермінована vs Ймовірнісна складність", size=16, bold=True, color="#1e293b"))

    b_root, _, _ = textbox(420, 90, "OR (Корінь)", size=13, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=10)
    frags.append(b_root)

    b_and1, _, _ = textbox(220, 190, "AND (Вузол 1)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    b_and2, _, _ = textbox(620, 190, "AND (Вузол 2)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    frags.append(b_and1)
    frags.append(b_and2)

    frags.append(line(370, 105, 250, 175, color="#64748b", sw=1.8))
    frags.append(line(470, 105, 590, 175, color="#64748b", sw=1.8))

    leaf_xs1 = [130, 210, 290]
    leaf_xs2 = [530, 610, 690]

    for x in leaf_xs1:
        b, _, _ = textbox(x, 280, "x", size=10, fill="#ffffff", stroke=BLUE_S, pad=6)
        frags.append(b)
        frags.append(line(220, 205, x, 268, color="#94a3b8", sw=1.2))

    for x in leaf_xs2:
        b, _, _ = textbox(x, 280, "x", size=10, fill="#ffffff", stroke=BLUE_S, pad=6)
        frags.append(b)
        frags.append(line(620, 205, x, 268, color="#94a3b8", sw=1.2))

    frags.append(rect(40, 330, 360, 75, fill=RED_F, stroke=RED_S, rx=6))
    frags.append(text(220, 350, "Детермінована складність D(f)", size=12, bold=True, color="#dc2626"))
    frags.append(text(220, 372, "Супротивник може змусити прочитати\nабсолютно всі n листків: D(f) = n", size=11, color="#991b1b"))

    frags.append(rect(440, 330, 360, 75, fill=GREEN_F, stroke=GREEN_S, rx=6))
    frags.append(text(620, 350, "Ймовірнісна складність R₀(f)", size=12, bold=True, color="#16a34a"))
    frags.append(text(620, 372, "Випадковий вибір гілки дає в середньому\nО(n⁰ˑ⁷⁵³) запитів (Теорема Сніра)", size=11, color="#166534"))

    render(os.path.join(IMG, "fig4-and-or-tree.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_decision_tree_model()
    fig_complexity_measures_map()
    fig_hypercube_subgraph()
    fig_and_or_tree()
    print("Figures generated successfully.")
