# -*- coding: utf-8 -*-
"""Фігури для теми «Нестандартні моделі» (book/algorithms/complexity-computability/non-standard-models)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def draw_polygon(points, fill):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}"/>'

def fig_order_structure():
    """fig1-order-structure.svg: Структура лінійного порядку нестандартної моделі N + Z x Q."""
    W, H = 840, 360
    frags = []

    frags.append(rect(10, 10, 820, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Лінійний порядок нестандартної моделі арифметики: ℕ + ℤ × ℚ", size=16, bold=True, color="#1e293b"))

    # Початковий сегмент N (Стандартний ряд)
    b_n, _, _ = textbox(140, 185, "Стандартний сегмент ℕ\n\n0, 1, 2, 3, 4, ..., n, n+1, ...\n\nСкінченні натуральні числа\n(Ізоморфно стандартній моделі)", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_n)

    # Розділювач / Межа
    frags.append(line(270, 75, 270, 295, color=RED_S, sw=2, dash="4,4"))
    frags.append(text(270, 318, "Зовнішня межа (невиражувана)", size=10, bold=True, color=RED_S, anchor="middle"))

    # Заголовок нестандартного сегменту
    frags.append(text(550, 75, "Нестандартний сегмент M \\ ℕ (Блоки ℤ × ℚ)", size=13, bold=True, color=BLUE_S))

    # Блок H
    b_z1, _, _ = textbox(370, 155, "Блок H:\n..., H-2, H-1, H, H+1, H+2, ...\n(Нескінченне число H)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_z1)

    # Блок 2H або H^2
    b_z2, _, _ = textbox(550, 155, "Блок 2H або H²:\n..., 2H-1, 2H, 2H+1, ...\n(Більший нестандартний блок)", size=10, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_z2)

    # Блок H/2 (Щільність Q)
    b_z3, _, _ = textbox(730, 155, "Блок H/2 або ⌊√H⌋:\n..., K-1, K, K+1, ...\n(Проміжний блок)", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_z3)

    # Впорядкування блоків як Q
    b_q, _, _ = textbox(550, 260, "Порядок між блоками є щільним, без найменшого та найбільшого елемента (ізоморфно ℚ)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_q)

    render(os.path.join(IMG, "fig1-order-structure.svg"), W, H, *frags)

def fig_overspill_principle():
    """fig2-overspill-principle.svg: Принцип Оверспілу (Переливу) та Андерспілу (Недоливу)."""
    W, H = 840, 360
    frags = []

    frags.append(rect(10, 10, 820, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Принцип Оверспілу (Overspill) та Андерспілу (Underspill)", size=16, bold=True, color="#1e293b"))

    # Вісь порядку
    frags.append(line(50, 180, 790, 180, color="#64748b", sw=3))
    frags.append(draw_polygon([(790, 174), (805, 180), (790, 186)], fill="#64748b"))

    # Позначення 0 та межі N
    frags.append(circle(80, 180, 5, fill=GREEN_S))
    frags.append(text(80, 205, "0", size=12, bold=True, color=GREEN_S, anchor="middle"))

    frags.append(line(280, 140, 280, 220, color=RED_S, sw=2, dash="4,4"))
    frags.append(text(180, 150, "Стандартні ℕ", size=12, bold=True, color=GREEN_S, anchor="middle"))
    frags.append(text(500, 150, "Нестандартні числа M \\ ℕ", size=12, bold=True, color=BLUE_S, anchor="middle"))

    # Оверспіл стрілка і блок
    frags.append(line(80, 110, 380, 110, color=AMBER_S, sw=2.5))
    frags.append(draw_polygon([(380, 104), (395, 110), (380, 116)], fill=AMBER_S))
    b_over, _, _ = textbox(240, 80, "Оверспіл: якщо φ(n) істинна ∀n ∈ ℕ, то вона виливається в M \\ ℕ (до елемента H)", size=10, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_over)

    # Андерспіл стрілка і блок
    frags.append(line(700, 250, 220, 250, color=PURPLE_S, sw=2.5))
    frags.append(draw_polygon([(220, 244), (205, 250), (220, 256)], fill=PURPLE_S))
    b_under, _, _ = textbox(460, 280, "Андерспіл: якщо ψ(c) істинна для нескінченно малих нестандартних c, вона затікає в ℕ", size=10, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_under)

    # Елемент H на осі
    frags.append(circle(380, 180, 5, fill=AMBER_S))
    frags.append(text(380, 205, "H (нестандартне)", size=11, bold=True, color=AMBER_S, anchor="middle"))

    # Елемент K на осі
    frags.append(circle(650, 180, 5, fill=PURPLE_S))
    frags.append(text(650, 205, "K (велике нестандартне)", size=11, bold=True, color=PURPLE_S, anchor="middle"))

    render(os.path.join(IMG, "fig2-overspill-principle.svg"), W, H, *frags)

def fig_tennenbaum_theorem():
    """fig3-tennenbaum-theorem.svg: Структурне доведення теореми Тенненбаума про нерекурсивність."""
    W, H = 840, 380
    frags = []

    frags.append(rect(10, 10, 820, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Теорема Тенненбаума: Необчислюваність нестандартної арифметики", size=16, bold=True, color="#1e293b"))

    # Нерозв'язні множини A та B
    b_ab, _, _ = textbox(210, 135, "Рекурсивно невідокремлювані множини\n\nA, B ⊂ ℕ — рекурсивно перелічувані, A ∩ B = ∅\nНе існує обчислювальної множини C,\nтакої що A ⊆ C та B ∩ C = ∅", size=10, fill=RED_F, stroke=RED_S)
    frags.append(b_ab)

    # Нестандартне число H і кодування через прості числа
    b_h, _, _ = textbox(630, 135, "Кодування в нестандартне число H\n\nКодувальний елемент H ∈ M \\ ℕ:\n∀i ∈ ℕ: (p_i | H ⟺ i ∈ A)\nКодує нескінченну інформацію множини A", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_h)

    # Стрілка зв'язку
    frags.append(line(380, 135, 460, 135, color="#64748b", sw=2))

    # Суперечність з обчислюваністю операцій
    b_dilemma, _, _ = textbox(420, 280, "Неможливість обчислюваності операцій +_M та ·_M\n\nЯкби операції +_M або ·_M були обчислюваними над стандартними кодами,\nто висловлювання (p_i | H) було б алгоритмічно розв'язним для кожного i ∈ ℕ.\nЦе дало б обчислювальний сепаратор C для A і B, що СУПЕРЕЧИТЬ їхній невідокремлюваності!", size=10, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_dilemma)

    render(os.path.join(IMG, "fig3-tennenbaum-theorem.svg"), W, H, *frags)

def fig_nonstandard_turing_execution():
    """fig4-nonstandard-turing-execution.svg: Траєкторія виконання нестандартної машини Тюринга."""
    W, H = 840, 360
    frags = []

    frags.append(rect(10, 10, 820, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Траєкторія обчислення нестандартної машини Тюринга", size=16, bold=True, color="#1e293b"))

    # Стандартний початковий відрізок обчислення (0, 1, ..., n)
    b_st, _, _ = textbox(160, 170, "Стандартні кроки k ∈ ℕ\n\nКроки: 0, 1, 2, ..., n\n\nСкінченні конфігурації\nстрічки та станів M", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_st)

    # Нескінченне стандартне спостереження
    frags.append(line(280, 170, 340, 170, color=GREEN_S, sw=2))
    frags.append(text(310, 155, "Зовнішній світ ℕ", size=10, bold=True, color=GREEN_S, anchor="middle"))

    # Нестандартний проміжок і гіпер-кроки H
    b_hyp, _, _ = textbox(570, 170, "Нестандартний гіпер-час H ∈ M \\ ℕ\n\nКроки: ..., H-2, H-1, H, H+1, ...\n\nМашина вважається такою, що зупинилася в M за H кроків,\nхоч для стандартного спостерігача це нескінченне обчислення", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_hyp)

    # Висновок про зупинку та Con(PA)
    b_con, _, _ = textbox(420, 305, "Нестандартний доказ суперечності 0=1 відповідає нестандартній машині Тюринга, що зупинилася за H кроків", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_con)

    render(os.path.join(IMG, "fig4-nonstandard-turing-execution.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_order_structure()
    fig_overspill_principle()
    fig_tennenbaum_theorem()
    fig_nonstandard_turing_execution()
    print("Figures generated successfully.")
