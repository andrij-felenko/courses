# -*- coding: utf-8 -*-
"""Фігури для теми «Клас P/poly: схема складності» (book/algorithms/complexity-computability/p-poly)."""
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

def fig_circuit_family():
    """fig1-circuit-family.svg: Сімейство поліноміальних схем {C_n} для вхідних довжин n."""
    W, H = 880, 420
    frags = []

    # Заголовок / рамка
    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Сімейство неоднорідних булевих схем {Cₙ | n ∈ ℕ}", size=16, bold=True, color="#1e293b"))

    # Схема C_1
    frags.append(rect(30, 60, 240, 320, fill=BLUE_F, stroke=BLUE_S, sw=1.8, rx=8))
    frags.append(text(150, 88, "Схема C₁ (для n = 1)", size=14, bold=True, color=BLUE_S))
    b_in1, _, _ = textbox(150, 130, "Вхід: x₁ ∈ {0, 1}", size=12, fill="#ffffff", stroke=LINE)
    b_g1, _, _ = textbox(150, 210, "Гейти AND/OR/NOT\nРозмір ≤ p(1)", size=12, fill=TEAL_F, stroke=TEAL_S)
    b_out1, _, _ = textbox(150, 320, "Вихід C₁(x₁) ∈ {0, 1}", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags += [b_in1, b_g1, b_out1]
    frags.append(arrow(150, 148, 150, 185, color=LINE, sw=1.5))
    frags.append(arrow(150, 252, 150, 298, color=LINE, sw=1.5))

    # Схема C_2
    frags.append(rect(320, 60, 240, 320, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8, rx=8))
    frags.append(text(440, 88, "Схема C₂ (для n = 2)", size=14, bold=True, color=PURPLE_S))
    b_in2, _, _ = textbox(440, 130, "Вхід: (x₁, x₂) ∈ {0, 1}²", size=12, fill="#ffffff", stroke=LINE)
    b_g2, _, _ = textbox(440, 210, "Гейти AND/OR/NOT\nРозмір ≤ p(2)", size=12, fill=AMBER_F, stroke=AMBER_S)
    b_out2, _, _ = textbox(440, 320, "Вихід C₂(x₁, x₂) ∈ {0, 1}", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags += [b_in2, b_g2, b_out2]
    frags.append(arrow(440, 148, 440, 185, color=LINE, sw=1.5))
    frags.append(arrow(440, 252, 440, 298, color=LINE, sw=1.5))

    # Схема C_n
    frags.append(rect(610, 60, 240, 320, fill="#f1f5f9", stroke="#475569", sw=1.8, rx=8))
    frags.append(text(730, 88, "Схема Cₙ (для n)", size=14, bold=True, color="#334155"))
    b_inn, _, _ = textbox(730, 130, "Вхід: x ∈ {0, 1}ⁿ", size=12, fill="#ffffff", stroke=LINE)
    b_gn, _, _ = textbox(730, 210, "Окремим алгоритмом\nне будується! Size ≤ p(n)", size=12, fill="#fee2e2", stroke="#dc2626")
    b_outn, _, _ = textbox(730, 320, "Вихід Cₙ(x) ∈ {0, 1}", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags += [b_inn, b_gn, b_outn]
    frags.append(arrow(730, 148, 730, 180, color=LINE, sw=1.5))
    frags.append(arrow(730, 252, 730, 298, color=LINE, sw=1.5))

    render(os.path.join(IMG, "fig1-circuit-family.svg"), W, H, *frags)


def fig_advice_tm():
    """fig2-advice-tm.svg: Еквівалентність схеми та машини Тюринга з поліноміальною підказкою."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Модель P/poly: Машина Тюринга з поліноміальною підказкою", size=16, bold=True, color="#1e293b"))

    # Блок входу x
    b_in, _, _ = textbox(180, 110, "Вхідний рядок x\nДовжина |x| = n", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S, pad=10)
    
    # Блок підказки a_n
    b_adv, _, _ = textbox(180, 230, "Поліноміальна підказка aₙ\n|aₙ| ≤ p(n), залежить лише від n", size=13, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=10)

    # Декларація машини M
    b_tm, _, _ = textbox(530, 170, "Детермінована машина Тюринга M\nПоліноміальний час виконання T(n) ≤ q(n)\nСимулює схему Cₙ за підказкою aₙ", size=13, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=14)

    # Вихід M(x, a_n)
    b_res, _, _ = textbox(790, 170, "Рішення:\n1 (YES)\n0 (NO)", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=10)

    frags += [b_in, b_adv, b_tm, b_res]

    # Стрілки
    frags.append(arrow(305, 110, 395, 145, color=BLUE_S, sw=2))
    frags.append(arrow(320, 230, 395, 195, color=AMBER_S, sw=2))
    frags.append(arrow(670, 170, 735, 170, color=GREEN_S, sw=2))

    # Нижній пояснювальний підпис
    frags.append(text(440, 335, "Важливо: підказка aₙ може бути необчислюваною функцією від n!", size=12, italic=True, color="#dc2626"))

    render(os.path.join(IMG, "fig2-advice-tm.svg"), W, H, *frags)


def fig_karp_lipton_collapse():
    """fig3-karp-lipton-collapse.svg: Схлопування поліноміальної ієрархії за теоремою Карпа — Ліптона."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Наслідки припущення NP ⊆ P/poly (Теорема Карпа — Ліптона)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Стандартна ієрархія
    frags.append(rect(40, 60, 380, 340, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(230, 88, "Стандартна поліноміальна ієрархія PH", size=14, bold=True, color="#334155"))

    b_ph3, _, _ = textbox(230, 140, "Рівень 3: Σ₃ᵖ / Π₃ᵖ", size=12, fill="#f3e8ff", stroke="#7e22ce")
    b_ph2, _, _ = textbox(230, 220, "Рівень 2: Σ₂ᵖ / Π₂ᵖ", size=12, fill=AMBER_F, stroke=AMBER_S)
    b_ph1, _, _ = textbox(230, 300, "Рівень 1: NP (Σ₁ᵖ) / coNP (Π₁ᵖ)", size=12, fill=BLUE_F, stroke=BLUE_S)
    b_ph0, _, _ = textbox(230, 365, "Рівень 0: P", size=12, fill=GREEN_F, stroke=GREEN_S)
    frags += [b_ph3, b_ph2, b_ph1, b_ph0]

    frags.append(arrow(230, 160, 230, 200, color=LINE))
    frags.append(arrow(230, 240, 230, 280, color=LINE))
    frags.append(arrow(230, 320, 230, 350, color=LINE))

    # Центральний транзишн (Умова)
    frags.append(arrow(430, 220, 480, 220, color="#dc2626", sw=3))
    b_cond, _, _ = textbox(455, 175, "Якщо\nNP ⊆ P/poly", size=13, bold=True, fill="#fee2e2", stroke="#dc2626", pad=8)
    frags.append(b_cond)

    # Права частина: Схлопована ієрархія
    frags.append(rect(490, 60, 350, 340, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=8))
    frags.append(text(665, 88, "Схлопована ієрархія PH = Σ₂ᵖ", size=14, bold=True, color=AMBER_S))

    b_top_col, _, _ = textbox(665, 150, "Усі вищі рівні Σₖᵖ (k ≥ 3)\nпадають на Σ₂ᵖ !", size=13, bold=True, fill="#fee2e2", stroke="#dc2626", pad=10)
    b_sig2, _, _ = textbox(665, 250, "Вершина: Σ₂ᵖ = Π₂ᵖ = PH", size=14, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=12)
    b_base, _, _ = textbox(665, 345, "P ⊆ NP ⊆ P/poly", size=12, fill=BLUE_F, stroke=BLUE_S)

    frags += [b_top_col, b_sig2, b_base]
    frags.append(arrow(665, 195, 665, 220, color="#dc2626", sw=2))

    render(os.path.join(IMG, "fig3-karp-lipton-collapse.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_circuit_family()
    fig_advice_tm()
    fig_karp_lipton_collapse()
    print("Figures generated successfully.")
