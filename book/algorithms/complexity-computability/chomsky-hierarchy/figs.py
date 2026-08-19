# -*- coding: utf-8 -*-
"""Фігури для теми «Ієрархія Хомського» (book/algorithms/complexity-computability/chomsky-hierarchy)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_chomsky_levels():
    """chomsky-levels.svg: Чотири поверхи ієрархії Хомського та їхні обчислювальні межі."""
    W, H = 880, 560
    frags = []

    # Загальний фон
    frags.append(rect(10, 10, 860, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 38, "Ієрархія Хомського: класи граматик, автомати та межі обчислюваності", size=16, bold=True, color="#1e293b"))

    # Вісь пам'яті ліворуч
    frags.append(rect(25, 65, 40, 460, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(45, 95, "▲", size=14, bold=True, color="#475569"))
    frags.append(text(45, 295, "ПАМ'ЯТЬ   ТА   ВИРАЗНА   СИЛА", size=11, bold=True, color="#475569", anchor="middle"))

    # Рівень 0: Рекурсивно-зліченні (Type 0)
    frags.append(rect(80, 65, 780, 105, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(95, 90, "Тип 0: Рекурсивно-зліченні мови (Unrestricted / RE)", size=13, bold=True, color=RED_S, anchor="start"))
    b0_rules, _, _ = textbox(215, 128, "Правила: α → β\n(α непорожнє, без обмежень)", size=11, fill="#ffffff", stroke=RED_S, min_w=225)
    b0_auto, _, _ = textbox(470, 128, "Автомат: Машина Тюринга (TM)\nПам'ять: Необмежена стрічка", size=11, fill="#ffffff", stroke=RED_S, min_w=235)
    b0_comp, _, _ = textbox(725, 128, "Належність: Нерозв'язна (RE)\nСвідок: Проблема зупинки K", size=11, fill="#ffffff", stroke=RED_S, min_w=225)
    frags.extend([b0_rules, b0_auto, b0_comp])

    # Рівень 1: Контекстно-залежні (Type 1)
    frags.append(rect(80, 180, 780, 105, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(95, 205, "Тип 1: Контекстно-залежні мови (Context-Sensitive / CSL)", size=13, bold=True, color=AMBER_S, anchor="start"))
    b1_rules, _, _ = textbox(215, 243, "Правила: αAβ → αγβ (|α| ≤ |β|)\n(нескорочувальні заміни)", size=11, fill="#ffffff", stroke=AMBER_S, min_w=225)
    b1_auto, _, _ = textbox(470, 243, "Автомат: Лінійно-обмежений (LBA)\nПам'ять: Стрічка довжини c·n", size=11, fill="#ffffff", stroke=AMBER_S, min_w=235)
    b1_comp, _, _ = textbox(725, 243, "Належність: PSPACE-повна\nСвідок: aⁿbⁿcⁿ, ww", size=11, fill="#ffffff", stroke=AMBER_S, min_w=225)
    frags.extend([b1_rules, b1_auto, b1_comp])

    # Рівень 2: Контекстно-вільні (Type 2)
    frags.append(rect(80, 295, 780, 105, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(95, 320, "Тип 2: Контекстно-вільні мови (Context-Free / CFL)", size=13, bold=True, color=BLUE_S, anchor="start"))
    b2_rules, _, _ = textbox(215, 358, "Правила: A → γ\n(один нетермінал ліворуч)", size=11, fill="#ffffff", stroke=BLUE_S, min_w=225)
    b2_auto, _, _ = textbox(470, 358, "Автомат: Магазинний автомат (PDA)\nПам'ять: Стек (LIFO)", size=11, fill="#ffffff", stroke=BLUE_S, min_w=235)
    b2_comp, _, _ = textbox(725, 358, "Належність: O(n³) CYK / O(n) LR\nСвідок: aⁿbⁿ, мова Діка", size=11, fill="#ffffff", stroke=BLUE_S, min_w=225)
    frags.extend([b2_rules, b2_auto, b2_comp])

    # Рівень 3: Регулярні (Type 3)
    frags.append(rect(80, 410, 780, 105, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(95, 435, "Тип 3: Регулярні мови (Regular / REG)", size=13, bold=True, color=GREEN_S, anchor="start"))
    b3_rules, _, _ = textbox(215, 473, "Правила: A → aB | a | ε\n(праволінійні або ліволінійні)", size=11, fill="#ffffff", stroke=GREEN_S, min_w=225)
    b3_auto, _, _ = textbox(470, 473, "Автомат: Скінченний автомат (DFA/NFA)\nПам'ять: O(1) скінченні стани", size=11, fill="#ffffff", stroke=GREEN_S, min_w=235)
    b3_comp, _, _ = textbox(725, 473, "Належність: O(n) час, O(1) пам'ять\nСвідок: a*b*, лексеми мов", size=11, fill="#ffffff", stroke=GREEN_S, min_w=225)
    frags.extend([b3_rules, b3_auto, b3_comp])

    render(os.path.join(IMG, "chomsky-levels.svg"), W, H, *frags)


def fig_decidability_matrix():
    """decidability-matrix.svg: Матриця розв'язності фундаментальних алгоритмічних задач."""
    W, H = 900, 470
    frags = []

    frags.append(rect(10, 10, 880, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(450, 38, "Алгоритмічна розв'язність і складність задач за рівнями ієрархії", size=16, bold=True, color="#1e293b"))

    # Заголовки колонок
    col_x = [110, 275, 440, 605, 770]
    headers = ["Тип граматики", "Належність (w ∈ L)", "Порожнеча (L = ∅)", "Еквівалентність (L₁ = L₂)", "Однозначність"]
    for i, h in enumerate(headers):
        b, _, _ = textbox(col_x[i], 80, h, size=11, bold=True, fill="#f1f5f9", stroke="#64748b", min_w=140)
        frags.append(b)

    # Рядки матриці
    rows_data = [
        ("Тип 3: Регулярні", GREEN_F, GREEN_S,
         "O(n) час, O(1) простір\nРозв'язна (DFA)",
         "Розв'язна\nO(|V| + |E|) пошук",
         "Розв'язна\nМінімізація DFA",
         "Розв'язна\nПошук циклів NFA"),
        ("Тип 2: Контекстно-вільні", BLUE_F, BLUE_S,
         "O(n³) CYK / O(n) LR\nРозв'язна (P-клас)",
         "Розв'язна\nГенерація нетерміналів",
         "НЕРОЗВ'ЯЗНА\n(Зведення з PCP)",
         "НЕРОЗВ'ЯЗНА\n(Зведення з PCP)"),
        ("Тип 1: Контекстно-залежні", AMBER_F, AMBER_S,
         "PSPACE-повна\nРозв'язна (NSPACE(n))",
         "НЕРОЗВ'ЯЗНА\n(Зведення з TM halting)",
         "НЕРОЗВ'ЯЗНА\n(Зведення з TM halting)",
         "НЕРОЗВ'ЯЗНА\n(Зведення з TM halting)"),
        ("Тип 0: Без обмежень", RED_F, RED_S,
         "НЕРОЗВ'ЯЗНА\nНапіврозв'язна (RE-повна)",
         "НЕРОЗВ'ЯЗНА\nТеорема Райса",
         "НЕРОЗВ'ЯЗНА\nТеорема Райса",
         "НЕРОЗВ'ЯЗНА\nТеорема Райса")
    ]

    y_pos = [145, 225, 305, 385]
    for row_idx, (name, bg, st, c1, c2, c3, c4) in enumerate(rows_data):
        y = y_pos[row_idx]
        b_name, _, _ = textbox(col_x[0], y, name, size=11, bold=True, fill=bg, stroke=st, min_w=140)
        b_c1, _, _ = textbox(col_x[1], y, c1, size=10, fill="#ffffff", stroke=st, min_w=140)
        b_c2, _, _ = textbox(col_x[2], y, c2, size=10, fill="#ffffff", stroke=st, min_w=140)
        b_c3, _, _ = textbox(col_x[3], y, c3, size=10, fill="#ffffff", stroke=st, min_w=140)
        b_c4, _, _ = textbox(col_x[4], y, c4, size=10, fill="#ffffff", stroke=st, min_w=140)
        frags.extend([b_name, b_c1, b_c2, b_c3, b_c4])

    render(os.path.join(IMG, "decidability-matrix.svg"), W, H, *frags)


def fig_cyk_grid():
    """cyk-grid.svg: Піраміда динамічного програмування алгоритму CYK."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 38, "Алгоритм CYK: динамічне обчислення таблиці підрядків P[довжина, початок]", size=16, bold=True, color="#1e293b"))

    # Рядок символів вхідного слова w = a b c d
    symbols = ["w[1] = 'a'", "w[2] = 'b'", "w[3] = 'c'", "w[4] = 'd'"]
    xs = [180, 340, 500, 660]
    for i in range(4):
        b, _, _ = textbox(xs[i], 420, symbols[i], size=12, bold=True, fill="#e2e8f0", stroke="#475569", min_w=110)
        frags.append(b)

    # Рівень 1 (l = 1): довжина 1
    b_lvl1, _, _ = textbox(70, 350, "Рівень 1\n(l = 1)", size=11, bold=True, fill="#f1f5f9", stroke="#64748b", min_w=80)
    frags.append(b_lvl1)
    b1_1, _, _ = textbox(180, 350, "P[1, 1]\n{A | A → 'a'}", size=11, fill=BLUE_F, stroke=BLUE_S, min_w=100)
    b1_2, _, _ = textbox(340, 350, "P[1, 2]\n{B | B → 'b'}", size=11, fill=BLUE_F, stroke=BLUE_S, min_w=100)
    b1_3, _, _ = textbox(500, 350, "P[1, 3]\n{C | C → 'c'}", size=11, fill=BLUE_F, stroke=BLUE_S, min_w=100)
    b1_4, _, _ = textbox(660, 350, "P[1, 4]\n{D | D → 'd'}", size=11, fill=BLUE_F, stroke=BLUE_S, min_w=100)
    frags.extend([b1_1, b1_2, b1_3, b1_4])

    # Рівень 2 (l = 2): довжина 2
    b_lvl2, _, _ = textbox(70, 270, "Рівень 2\n(l = 2)", size=11, bold=True, fill="#f1f5f9", stroke="#64748b", min_w=80)
    frags.append(b_lvl2)
    b2_1, _, _ = textbox(260, 270, "P[2, 1] (ab)\nP[1,1] ⋈ P[1,2]", size=11, fill=AMBER_F, stroke=AMBER_S, min_w=120)
    b2_2, _, _ = textbox(420, 270, "P[2, 2] (bc)\nP[1,2] ⋈ P[1,3]", size=11, fill=AMBER_F, stroke=AMBER_S, min_w=120)
    b2_3, _, _ = textbox(580, 270, "P[2, 3] (cd)\nP[1,3] ⋈ P[1,4]", size=11, fill=AMBER_F, stroke=AMBER_S, min_w=120)
    frags.extend([b2_1, b2_2, b2_3])

    # Рівень 3 (l = 3): довжина 3
    b_lvl3, _, _ = textbox(70, 190, "Рівень 3\n(l = 3)", size=11, bold=True, fill="#f1f5f9", stroke="#64748b", min_w=80)
    frags.append(b_lvl3)
    b3_1, _, _ = textbox(340, 190, "P[3, 1] (abc)\nP[1,1]⋈P[2,2] ∪ P[2,1]⋈P[1,3]", size=10, fill=PURPLE_F, stroke=PURPLE_S, min_w=150)
    b3_2, _, _ = textbox(500, 190, "P[3, 2] (bcd)\nP[1,2]⋈P[2,3] ∪ P[2,2]⋈P[1,4]", size=10, fill=PURPLE_F, stroke=PURPLE_S, min_w=150)
    frags.extend([b3_1, b3_2])

    # Рівень 4 (l = 4): вершина піраміди — все слово
    b_lvl4, _, _ = textbox(70, 105, "Рівень 4\n(l = n = 4)", size=11, bold=True, fill="#f1f5f9", stroke="#64748b", min_w=80)
    frags.append(b_lvl4)
    b4_1, _, _ = textbox(420, 105, "P[4, 1] (abcd): Вершина розбору\nЧи належить стартовий нетермінал S ∈ P[4, 1]?", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S, min_w=280)
    frags.append(b4_1)

    # Стрілки залежностей розбиття для вершини P[4, 1]
    frags.append(line(420, 132, 340, 168, color=GREEN_S, sw=1.5, dash="3,3"))
    frags.append(line(420, 132, 500, 168, color=GREEN_S, sw=1.5, dash="3,3"))

    render(os.path.join(IMG, "cyk-grid.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_chomsky_levels()
    fig_decidability_matrix()
    fig_cyk_grid()
    print("Figures for chomsky-hierarchy generated successfully.")
