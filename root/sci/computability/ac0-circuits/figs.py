# -*- coding: utf-8 -*-
"""Фігури для теми «Клас схем AC0 та схемна складність» (book/algorithms/complexity-computability/ac0-circuits)."""
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

def fig_ac0_structure():
    """fig1-ac0-structure.svg: Архітектура булевої схеми AC0 з константною глибиною та необмеженою валентністю."""
    W, H = 880, 440
    frags = []

    # Загальна рамка
    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Будова схеми класу AC⁰ (необмежена валентність, константна глибина d)", size=16, bold=True, color="#1e293b"))

    # Вхідний шар (внизу)
    frags.append(text(440, 390, "Вхідний шар: змінні x₁, ¬x₁, x₂, ¬x₂, ..., x♁, ¬x♁ (fan-in = 0)", size=12, italic=True, color="#475569"))
    
    in_labels = ["x₁", "¬x₁", "x₂", "¬x₂", "x₃", "¬x₃", "...", "xₙ", "¬xₙ"]
    in_xs = [80, 150, 240, 310, 400, 470, 560, 680, 750]
    for x, lbl in zip(in_xs, in_labels):
        if lbl == "...":
            frags.append(text(x, 360, "...", size=16, bold=True, color="#64748b"))
        else:
            b, _, _ = textbox(x, 360, lbl, size=12, fill="#ffffff", stroke=BLUE_S)
            frags.append(b)

    # Шар 1 (AND / OR гейти з великою валентністю)
    frags.append(text(80, 270, "Шар 1 (AND / OR)\nFan-in = n", size=11, color=PURPLE_S, bold=True))
    g1_xs = [200, 440, 680]
    g1_types = ["∨ (OR)", "∧ (AND)", "∨ (OR)"]
    for x, t in zip(g1_xs, g1_types):
        b, _, _ = textbox(x, 260, t, size=13, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
        frags.append(b)

    # Лінії від входів до Шару 1
    for ix in [80, 150, 240, 310]:
        frags.append(line(ix, 345, 200, 278, color="#94a3b8", sw=1.2))
    for ix in [240, 310, 400, 470]:
        frags.append(line(ix, 345, 440, 278, color="#94a3b8", sw=1.2))
    for ix in [470, 680, 750]:
        frags.append(line(ix, 345, 680, 278, color="#94a3b8", sw=1.2))

    # Шар 2 (OR / AND гейти)
    frags.append(text(80, 160, "Шар 2 (AND / OR)\nFan-in = n", size=11, color=AMBER_S, bold=True))
    g2_xs = [320, 560]
    g2_types = ["∧ (AND)", "∨ (OR)"]
    for x, t in zip(g2_xs, g2_types):
        b, _, _ = textbox(x, 150, t, size=13, bold=True, fill=AMBER_F, stroke=AMBER_S)
        frags.append(b)

    # Зв'язки між Шаром 1 та Шаром 2
    frags.append(line(200, 242, 320, 168, color="#94a3b8", sw=1.5))
    frags.append(line(440, 242, 320, 168, color="#94a3b8", sw=1.5))
    frags.append(line(440, 242, 560, 168, color="#94a3b8", sw=1.5))
    frags.append(line(680, 242, 560, 168, color="#94a3b8", sw=1.5))

    # Вихідний гейт (Шар 3 / Вихід)
    b_out, _, _ = textbox(440, 70, "Вихідний гейт ∧ (AND)\nf(x₁, ..., xₙ) ∈ {0, 1}", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_out)

    frags.append(line(320, 132, 440, 88, color=GREEN_S, sw=1.8))
    frags.append(line(560, 132, 440, 88, color=GREEN_S, sw=1.8))

    # Бічна панель з параметрами AC0
    param_text = "Параметри класу AC⁰:\n• Глибина: d = O(1) [константна]\n• Розмір: S(n) ≤ nᵏ [поліноміальний]\n• Базис: AND, OR, NOT\n• Fan-in: необмежений"
    b_p, _, _ = textbox(770, 130, param_text, size=11, fill="#f1f5f9", stroke="#475569")
    frags.append(b_p)

    render(os.path.join(IMG, "fig1-ac0-structure.svg"), W, H, *frags)


def fig_parity_tree_vs_ac0():
    """fig2-parity-tree-vs-ac0.svg: Порівняння бінарного дерева NC1 та спроби побудови AC0 для PARITY."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Обчислення парності PARITY(x): NC¹ (логоглибина) проти AC⁰ (бар'єр)", size=16, bold=True, color="#1e293b"))

    # Лівий блок: NC1 (дерево парності)
    frags.append(rect(30, 60, 390, 310, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Клас NC¹ (XOR / fan-in = 2)", size=14, bold=True, color=BLUE_S))
    
    b_nc_out, _, _ = textbox(225, 125, "XOR (Вихід)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_nc_m1, _, _ = textbox(130, 190, "XOR", size=11, fill="#ffffff", stroke=BLUE_S)
    b_nc_m2, _, _ = textbox(320, 190, "XOR", size=11, fill="#ffffff", stroke=BLUE_S)
    
    b_in1, _, _ = textbox(80, 260, "x₁ ⊕ x₂", size=11, fill="#ffffff", stroke=LINE)
    b_in2, _, _ = textbox(180, 260, "x₃ ⊕ x₄", size=11, fill="#ffffff", stroke=LINE)
    b_in3, _, _ = textbox(270, 260, "x₅ ⊕ x₆", size=11, fill="#ffffff", stroke=LINE)
    b_in4, _, _ = textbox(370, 260, "x₇ ⊕ x₈", size=11, fill="#ffffff", stroke=LINE)

    frags += [b_nc_out, b_nc_m1, b_nc_m2, b_in1, b_in2, b_in3, b_in4]
    
    frags.append(arrow(130, 175, 225, 138, color=BLUE_S, sw=1.5))
    frags.append(arrow(320, 175, 225, 138, color=BLUE_S, sw=1.5))
    frags.append(arrow(80, 246, 130, 203, color=BLUE_S, sw=1.2))
    frags.append(arrow(180, 246, 130, 203, color=BLUE_S, sw=1.2))
    frags.append(arrow(270, 246, 320, 203, color=BLUE_S, sw=1.2))
    frags.append(arrow(370, 246, 320, 203, color=BLUE_S, sw=1.2))

    txt_nc = "• Глибина: d = log₂ n (О(log n))\n• Fan-in: 2\n• Розмір: O(n)\n• Висновок: PARITY ∈ NC¹"
    b_nc_t, _, _ = textbox(225, 325, txt_nc, size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_nc_t)

    # Правий блок: AC0 (бар'єр для PARITY)
    frags.append(rect(460, 60, 390, 310, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(655, 85, "Клас AC⁰ (константна глибина d)", size=14, bold=True, color=RED_S))

    b_ac_out, _, _ = textbox(655, 125, "AND / OR (Вихід)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    b_ac_mid, _, _ = textbox(655, 190, "Експоненціальна кількість гейтів!\nРозмір ≥ 2^{Ω(n^{1/(d-1)})}", size=11, bold=True, fill="#ffffff", stroke=RED_S)
    
    frags += [b_ac_out, b_ac_mid]
    frags.append(arrow(655, 175, 655, 138, color=RED_S, sw=1.5))

    txt_ac = "• Глибина: d = O(1) [фіксована]\n• Потрібний розмір: 2^{Ω(n^{1/(d-1)})}\n• Висновок: PARITY ∉ AC⁰\n• Теорема Гастада (1986)"
    b_ac_t, _, _ = textbox(655, 325, txt_ac, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_ac_t)

    render(os.path.join(IMG, "fig2-parity-tree-vs-ac0.svg"), W, H, *frags)


def fig_switching_lemma_collapse():
    """fig3-switching-lemma-collapse.svg: Спрощення DNF/CNF гейта під дією випадкового обмеження (Лема Гастада)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Спрощення логічного шару за лемою про перемикання Гастада (Switching Lemma)", size=16, bold=True, color="#1e293b"))

    # Верхній блок: Початкова k-DNF формула
    frags.append(rect(30, 60, 820, 100, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(440, 80, "До застосування випадкового обмеження ρ ∈ Rₚ:", size=13, bold=True, color=PURPLE_S))
    
    txt_dnf = "k-DNF формула f = T₁ ∨ T₂ ∨ ... ∨ Tₘ  (кожен терм Tᵢ має валентність ≤ k)\nСкладний шар гейтів OR над AND з багатьма високовалентними входами"
    b_dnf, _, _ = textbox(440, 120, txt_dnf, size=12, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_dnf)

    # Стрілка посередині з дією випадкового обмеження
    frags.append(arrow(440, 170, 440, 230, color=RED_S, sw=2.5))
    
    txt_rho = "Випадкове обмеження ρ ∈ Rₚ:\nКожна змінна xᵢ зафіксовується в 0 або 1 з імовірністю 1 - p,\nі залишається вільною з імовірністю p = n^{-1/(d-1)}"
    b_rho, _, _ = textbox(440, 200, txt_rho, size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_rho)

    # Нижній блок: Результат - Дерево рішень малої глибини r / k-CNF
    frags.append(rect(30, 240, 820, 150, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(440, 260, "Після застосування обмеження f|ₚ:", size=13, bold=True, color=GREEN_S))

    txt_res = "З імовірністю ≥ 1 - (5·p·k)ʳ функція f|ₚ еквівалентна Дереву Рішень глибини ≤ r (або r-CNF)\nЗменшення глибини схемного шару:  d ↦ d - 1  без зростання розміру!"
    b_res, _, _ = textbox(440, 315, txt_res, size=12, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_res)

    render(os.path.join(IMG, "fig3-switching-lemma-collapse.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_ac0_structure()
    fig_parity_tree_vs_ac0()
    fig_switching_lemma_collapse()
    print("Figures generated successfully.")
