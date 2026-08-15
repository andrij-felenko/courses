# -*- coding: utf-8 -*-
"""Фігури для теми «Реляційна модель даних та теорема Кодда» (book/algorithms/complexity-computability/codd-relational-model)."""
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

def fig1_relational_structure():
    """fig1-relational-structure.svg: Структура відношення (Схема, Атрибути, Домени, Кортежі)."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Реляційна структура: Відношення R ⊆ D₁ × D₂ × ... × Dₖ", size=16, bold=True, color="#1e293b"))

    # Домени (Верхній блок)
    b_dom1, _, _ = textbox(160, 80, "Домен D₁ (Integer)\n{101, 102, 103}", size=11, pad=6, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=180)
    b_dom2, _, _ = textbox(420, 80, "Домен D₂ (String)\n{'Аліса', 'Боб', 'Єва'}", size=11, pad=6, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=180)
    b_dom3, _, _ = textbox(680, 80, "Домен D₃ (Decimal)\n{1500.0, 2400.0, 3100.0}", size=11, pad=6, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=180)
    frags.extend([b_dom1, b_dom2, b_dom3])

    # Стрілки відображення доменів у заголовки
    frags.append(arrow(160, 105, 160, 145, color=TEAL_S, sw=1.5))
    frags.append(arrow(420, 105, 420, 145, color=BLUE_S, sw=1.5))
    frags.append(arrow(680, 105, 680, 145, color=PURPLE_S, sw=1.5))

    # Схема відношення (Заголовок таблиці)
    frags.append(rect(70, 150, 700, 36, fill="#334155", stroke="#1e293b", sw=1.5, rx=4))
    frags.append(text(160, 172, "ID (Первинний ключ)", size=12, bold=True, color="#ffffff"))
    frags.append(text(420, 172, "Name (Ім'я)", size=12, bold=True, color="#ffffff"))
    frags.append(text(680, 172, "Salary (Зарплата)", size=12, bold=True, color="#ffffff"))

    # Рядки відношення (Кортежі)
    tuples_data = [
        ("101", "Аліса", "2400.0", GREEN_F, GREEN_S, 205),
        ("102", "Боб", "1500.0", GRAY_F, GRAY_S, 250),
        ("103", "Єва", "3100.0", AMBER_F, AMBER_S, 295),
    ]

    for id_val, name_val, sal_val, f_clr, s_clr, y in tuples_data:
        frags.append(rect(70, y - 16, 700, 34, fill=f_clr, stroke=s_clr, sw=1.2, rx=4))
        frags.append(text(160, y + 2, id_val, size=12, bold=True, color="#1e293b"))
        frags.append(text(420, y + 2, name_val, size=12, color="#1e293b"))
        frags.append(text(680, y + 2, sal_val, size=12, color="#1e293b"))

    # Пояснювальні виноси
    b_key, _, _ = textbox(150, 375, "Первинний ключ (Key):\nУнікально ідентифікує кортеж", size=10, pad=5, fill=GREEN_F, stroke=GREEN_S, min_w=200)
    b_tup, _, _ = textbox(420, 375, "Кортеж (Tuple):\nУпорядкована послідовність n-значень", size=10, pad=5, fill=AMBER_F, stroke=AMBER_S, min_w=220)
    b_1nf, _, _ = textbox(690, 375, "1NF (Атомарність):\nЗначення не є списками чи множинами", size=10, pad=5, fill=PURPLE_F, stroke=PURPLE_S, min_w=220)
    frags.extend([b_key, b_tup, b_1nf])

    render(os.path.join(IMG, "fig1-relational-structure.svg"), W, H, *frags)

def fig2_relational_algebra_operators():
    """fig2-relational-algebra-operators.svg: Фундаментальні оператори реляційної алгебри."""
    W, H = 840, 500
    frags = []

    frags.append(rect(10, 10, 820, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Фундаментальні оператори Реляційної Алгебри Кодда", size=16, bold=True, color="#1e293b"))

    ops = [
        ("Селекція σ_φ(R)", "Фільтрація рядків за умовою φ\n(вибирає підмножину кортежів)", BLUE_F, BLUE_S, 80, 80),
        ("Проекція π_A(R)", "Вибір колонки A та вилучення дублікатів\n(зміна схеми відношення)", TEAL_F, TEAL_S, 480, 80),
        ("Декартів добуток R × S", "Комбінування кожного кортежу R з кожним S\n(розмір |R| · |S|)", PURPLE_F, PURPLE_S, 80, 210),
        ("Природне з'єднання R ⋈ S", "Об'єднання за спільними атрибутами\n(π_{R.A, S.B}(σ_{R.X = S.X}(R × S)))", GREEN_F, GREEN_S, 480, 210),
        ("Об'єднання R ∪ S", "Множинне об'єднання кортежів\n(вимагає однакові схеми R та S)", AMBER_F, AMBER_S, 80, 340),
        ("Різниця R \\ S", "Кортежі, що є в R, але відсутні в S\n(вимагає сумісність за схемою)", RED_F, RED_S, 480, 340),
    ]

    for title, desc, f_clr, s_clr, x, y in ops:
        b_box, _, _ = textbox(x + 130, y + 50, title + "\n\n" + desc, size=11, pad=8, fill=f_clr, stroke=s_clr, bold=True, min_w=260)
        frags.append(b_box)

    frags.append(text(420, 465, "Оператори замкнені: результат застосування оператора до відношень є новим відношенням.", size=11, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig2-relational-algebra-operators.svg"), W, H, *frags)

def fig3_codd_theorem_equivalence():
    """fig3-codd-theorem-equivalence.svg: Трикутник еквівалентності Теореми Кодда."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Теорема Кодда: Еквівалентність мов реляційних запитів", size=16, bold=True, color="#1e293b"))

    # Вузол 1: Реляційна Алгебра (Процедурна)
    b_ra, _, _ = textbox(420, 110, "Реляційна Алгебра (RA)\n[Процедурна мова]\nσ, π, ×, ∪, \\, ⋈", size=12, pad=10, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=280)
    frags.append(b_ra)

    # Вузол 2: Безпечне реляційне числення кортежів (Safe TRC)
    b_trc, _, _ = textbox(210, 310, "Безпечне реляційне числення (Safe TRC)\n[Декларативна мова]\n{ t | φ(t) }, незалежне від домену", size=11, pad=10, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=260)
    frags.append(b_trc)

    # Вузол 3: Логіка першого порядку (FO) над скінченними структурами
    b_fo, _, _ = textbox(630, 310, "Логіка першого порядку (FO)\n[Дескриптивна складність]\nКласи складності: FO ≡ AC⁰", size=11, pad=10, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=260)
    frags.append(b_fo)

    # Двосторонні стрілки еквівалентності
    frags.append(arrow(340, 150, 240, 260, color=BLUE_S, sw=2.5))
    frags.append(arrow(240, 260, 340, 150, color=GREEN_S, sw=2.5))
    frags.append(text(250, 195, "Алгоритм Кодда (RA ⟺ TRC)", size=10, bold=True, color="#1e293b"))

    frags.append(arrow(500, 150, 600, 260, color=BLUE_S, sw=2.5))
    frags.append(arrow(600, 260, 500, 150, color=PURPLE_S, sw=2.5))
    frags.append(text(590, 195, "Ізоморфізм структури", size=10, bold=True, color="#1e293b"))

    frags.append(arrow(340, 310, 500, 310, color=GREEN_S, sw=2.5))
    frags.append(arrow(500, 310, 340, 310, color=PURPLE_S, sw=2.5))
    frags.append(text(420, 295, "Синтаксичний еквівалент", size=10, bold=True, color="#1e293b"))

    frags.append(text(420, 395, "Реляційна повнота: будь-яка мова, еквівалентна RA, називається реляційно повною.", size=11, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig3-codd-theorem-equivalence.svg"), W, H, *frags)

def fig4_query_optimization_tree():
    """fig4-query-optimization-tree.svg: Дерево запиту та алгебраїчні оптимізації."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Оптимізація запитів: Проштовхування селекцій у реляційному дереві", size=16, bold=True, color="#1e293b"))

    # Ліве дерево: Неоптимізований запит σ_{age > 30}(Users ⋈ Orders)
    frags.append(text(210, 70, "Неоптимізований вираз", size=13, bold=True, color=RED_S))

    b_root1, _, _ = textbox(210, 110, "π_{Name, OrderID}", size=11, pad=6, fill=GRAY_F, stroke=GRAY_S, bold=True, min_w=140)
    b_sel1, _, _ = textbox(210, 180, "σ_{Age > 30}", size=11, pad=6, fill=RED_F, stroke=RED_S, bold=True, min_w=140)
    b_join1, _, _ = textbox(210, 250, "⋈_{Users.ID = Orders.UID}", size=11, pad=6, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=180)
    b_u1, _, _ = textbox(130, 330, "Users\n(1,000,000 рядків)", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, min_w=130)
    b_o1, _, _ = textbox(290, 330, "Orders\n(5,000,000 рядків)", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, min_w=130)

    frags.extend([b_root1, b_sel1, b_join1, b_u1, b_o1])
    frags.append(arrow(210, 132, 210, 160, color=GRAY_S, sw=1.5))
    frags.append(arrow(210, 202, 210, 230, color=RED_S, sw=1.5))
    frags.append(arrow(180, 272, 140, 310, color=PURPLE_S, sw=1.5))
    frags.append(arrow(240, 272, 280, 310, color=PURPLE_S, sw=1.5))

    # Центральна стрілка перетворення
    frags.append(arrow(390, 220, 450, 220, color=AMBER_S, sw=3.0))
    frags.append(text(420, 200, "Алгебраїчний\nперепис", size=10, bold=True, color=AMBER_S))

    # Праве дерево: Оптимізований запит (π(σ(Users) ⋈ Orders))
    frags.append(text(630, 70, "Оптимізований вираз (Pushdown)", size=13, bold=True, color=GREEN_S))

    b_root2, _, _ = textbox(630, 110, "π_{Name, OrderID}", size=11, pad=6, fill=GRAY_F, stroke=GRAY_S, bold=True, min_w=140)
    b_join2, _, _ = textbox(630, 180, "⋈_{Users.ID = Orders.UID}", size=11, pad=6, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=180)
    b_sel2, _, _ = textbox(550, 250, "σ_{Age > 30}", size=11, pad=6, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=130)
    b_u2, _, _ = textbox(550, 330, "Users\n(1,000,000 рядків)", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, min_w=130)
    b_o2, _, _ = textbox(710, 330, "Orders\n(5,000,000 рядків)", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, min_w=130)

    frags.extend([b_root2, b_join2, b_sel2, b_u2, b_o2])
    frags.append(arrow(630, 132, 630, 160, color=GRAY_S, sw=1.5))
    frags.append(arrow(590, 202, 560, 230, color=PURPLE_S, sw=1.5))
    frags.append(arrow(670, 202, 700, 310, color=PURPLE_S, sw=1.5))
    frags.append(arrow(550, 272, 550, 310, color=GREEN_S, sw=1.5))

    frags.append(text(420, 400, "Проштовхування селекції зменшує кількість кортежів перед дорогою операцією з'єднання (Join).", size=11, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig4-query-optimization-tree.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_relational_structure()
    fig2_relational_algebra_operators()
    fig3_codd_theorem_equivalence()
    fig4_query_optimization_tree()
    print("All figures generated successfully.")
