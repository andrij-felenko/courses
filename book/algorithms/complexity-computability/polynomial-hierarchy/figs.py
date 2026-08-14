# -*- coding: utf-8 -*-
"""Фігури для теми «Поліноміальна ієрархія (PH)» (book/algorithms/complexity-computability)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"


def fig_ph_levels():
    """ph-levels.svg: Структура рівнів поліноміальної ієрархії від P до PSPACE."""
    W, H = 900, 520
    frags = []

    # Зовнішній контейнер — PSPACE
    frags.append(rect(30, 20, 840, 480, fill="#f8fafc", stroke="#94a3b8", sw=2, rx=12))
    frags.append(text(450, 48, "PSPACE — клас задач із поліномною пам'яттю", size=18, bold=True, color="#475569"))

    # Контейнер PH
    frags.append(rect(60, 70, 780, 410, fill="#f1f5f9", stroke="#64748b", sw=2, rx=10))
    frags.append(text(450, 98, "PH — Поліноміальна ієрархія (Polynomial Hierarchy)", size=16, bold=True, color="#334155"))

    # Рівень k (узагальнений)
    frags.append(rect(90, 120, 720, 75, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8, rx=8))
    frags.append(text(450, 142, "Рівень k:  Σₖᵖ  |  Πₖᵖ  |  Δₖᵖ = P^(Σₖ₋₁ᵖ)", size=14, bold=True, color=PURPLE_S))
    frags.append(text(450, 168, "Формули з k чергуваннями кванторів (∃ x₁ ∀ x₂ ... Qₖ xₖ R)", size=12, color=INK))

    # Стрілка вниз (ієрархічне включення)
    frags.append(arrow(450, 200, 450, 222, color=LINE, sw=2))

    # Рівень 2
    frags.append(rect(90, 225, 720, 80, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=8))
    frags.append(text(450, 248, "Рівень 2:  Σ₂ᵖ = NP^(NP)   |   Π₂ᵖ = coNP^(NP)   |   Δ₂ᵖ = P^(NP)", size=14, bold=True, color=AMBER_S))
    frags.append(text(450, 274, "Формули вигляду ∃x ∀y R(x,y)  (напр. мінімізація булевих схем)", size=12, color=INK))

    # Стрілка вниз
    frags.append(arrow(450, 310, 450, 332, color=LINE, sw=2))

    # Рівень 1
    frags.append(rect(90, 335, 720, 70, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    b_np, _, _ = textbox(250, 370, "Σ₁ᵖ = NP\n(існує свідок ∃)", size=13, bold=True, fill="#ffffff", stroke=NEG, sw=1.5)
    b_conp, _, _ = textbox(650, 370, "Π₁ᵖ = coNP\n(для всіх свідків ∀)", size=13, bold=True, fill="#ffffff", stroke=NEG, sw=1.5)
    frags += [b_np, b_conp]
    frags.append(text(450, 370, "Δ₁ᵖ = P", size=13, bold=True, color=INK))

    # Стрілка вниз
    frags.append(arrow(450, 410, 450, 428, color=LINE, sw=2))

    # Рівень 0
    b_p, _, _ = textbox(450, 450, "Рівень 0:  Δ₀ᵖ = Σ₀ᵖ = Π₀ᵖ = P  (детермінований поліномний час)",
                        size=14, bold=True, fill="#e9f7ef", stroke=FIELD, sw=2, pad=10)
    frags.append(b_p)

    render(os.path.join(IMG, "ph-levels.svg"), W, H, *frags)


def fig_quantifier_alternation():
    """quantifier-alternation.svg: Дерева обчислень для Σ₁ᵖ, Π₁ᵖ та Σ₂ᵖ."""
    W, H = 880, 380
    frags = []

    # Блок Σ₁ᵖ (NP: ∃x)
    frags.append(rect(20, 20, 260, 340, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(150, 48, "Σ₁ᵖ = NP (Квантор ∃)", size=15, bold=True, color=NEG))
    frags.append(text(150, 72, "Формула: ∃ x R(x)", size=13, italic=True))
    b_ex, _, _ = textbox(150, 120, "Корінь: ∃ x", size=13, bold=True, fill="#ffffff", stroke=NEG)
    b_l1, _, _ = textbox(85, 200, "x = 0\nR(0)", size=12, fill="#ffffff", stroke=LINE)
    b_l2, _, _ = textbox(215, 200, "x = 1\nR(1)", size=12, fill="#ffffff", stroke=LINE)
    frags += [b_ex, b_l1, b_l2]
    frags.append(arrow(130, 138, 95, 180, color=LINE))
    frags.append(arrow(170, 138, 205, 180, color=LINE))
    b_or, _, _ = textbox(150, 290, "Правило істинності:\nАБО (достатньо 1 гілки)", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S, pad=8)
    frags.append(b_or)

    # Блок Π₁ᵖ (coNP: ∀x)
    frags.append(rect(310, 20, 260, 340, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    frags.append(text(440, 48, "Π₁ᵖ = coNP (Квантор ∀)", size=15, bold=True, color=POS))
    frags.append(text(440, 72, "Формула: ∀ x R(x)", size=13, italic=True))
    b_all, _, _ = textbox(440, 120, "Корінь: ∀ x", size=13, bold=True, fill="#ffffff", stroke=POS)
    b_r1, _, _ = textbox(375, 200, "x = 0\nR(0)", size=12, fill="#ffffff", stroke=LINE)
    b_r2, _, _ = textbox(505, 200, "x = 1\nR(1)", size=12, fill="#ffffff", stroke=LINE)
    frags += [b_all, b_r1, b_r2]
    frags.append(arrow(420, 138, 385, 180, color=LINE))
    frags.append(arrow(460, 138, 495, 180, color=LINE))
    b_and, _, _ = textbox(440, 290, "Правило істинності:\nІ (вимагає ВСІХ гілок)", size=12, bold=True, fill="#fff3cd", stroke="#ffc107", pad=8)
    frags.append(b_and)

    # Блок Σ₂ᵖ (NP^NP: ∃x ∀y)
    frags.append(rect(600, 20, 260, 340, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8, rx=8))
    frags.append(text(730, 48, "Σ₂ᵖ = NP^(NP) (∃x ∀y)", size=15, bold=True, color=PURPLE_S))
    frags.append(text(730, 72, "Формула: ∃ x ∀ y R(x,y)", size=13, italic=True))
    b_s2, _, _ = textbox(730, 120, "Корінь: ∃ x", size=13, bold=True, fill="#ffffff", stroke=PURPLE_S)
    b_y1, _, _ = textbox(665, 195, "∀ y для x=0", size=12, bold=True, fill="#ffffff", stroke=POS)
    b_y2, _, _ = textbox(795, 195, "∀ y для x=1", size=12, bold=True, fill="#ffffff", stroke=POS)
    frags += [b_s2, b_y1, b_y2]
    frags.append(arrow(710, 138, 675, 178, color=LINE))
    frags.append(arrow(750, 138, 785, 178, color=LINE))
    b_alt, _, _ = textbox(730, 290, "Чергування:\nАБО над тавтологіями І", size=12, bold=True, fill="#e2e8f0", stroke="#475569", pad=8)
    frags.append(b_alt)

    render(os.path.join(IMG, "quantifier-alternation.svg"), W, H, *frags)


def fig_oracle_stack():
    """oracle-stack.svg: Концептуальна модель оракульної машини Тюринга."""
    W, H = 840, 340
    frags = []

    # Головна машина Тюринга (M)
    b_mach, _, _ = textbox(220, 170,
                           "Детермінована або недетермінована\nполіномна машина M\n(процесор / алгоритм)",
                           size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, pad=14)
    frags.append(b_mach)

    # Оракул (O)
    b_ora, _, _ = textbox(620, 170,
                          "Оракул O для класу C\n(наприклад, розв'язувач SAT)\nВердикт за O(1) кроків!",
                          size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2.2, pad=14)
    frags.append(b_ora)

    # Канал запиту
    frags.append(arrow(370, 130, 470, 130, color=POS, sw=2.5))
    frags.append(text(420, 115, "1. Запит записується на стрічку", size=12, bold=True, color=POS))
    frags.append(text(420, 145, "q ∈ SAT ?", size=13, bold=True, italic=True))

    # Канал відповіді
    frags.append(arrow(470, 210, 370, 210, color=FIELD, sw=2.5))
    frags.append(text(420, 195, "2. Миттєва відповідь", size=12, bold=True, color=FIELD))
    frags.append(text(420, 225, "1 (Так) / 0 (Ні)", size=13, bold=True, italic=True))

    # Підсумкова позначка
    b_class, _, _ = textbox(420, 300,
                            "Клас обчислюваності позначується як M^O (наприклад, P^(NP) або NP^(NP))",
                            size=14, bold=True, fill="#f1f5f9", stroke="#64748b", pad=10)
    frags.append(b_class)

    render(os.path.join(IMG, "oracle-stack.svg"), W, H, *frags)


def fig_ph_collapse():
    """ph-collapse.svg: Механізм обвалу ієрархії при Σₖᵖ = Πₖᵖ."""
    W, H = 860, 360
    frags = []

    # Ліва частина: Звичайна ієрархія
    frags.append(rect(20, 20, 390, 320, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    frags.append(text(215, 48, "Гіпотеза: PH нескінченна", size=15, bold=True, color=INK))
    frags.append(text(215, 72, "Кожен новий рівень строго ширший", size=12, italic=True))

    b_lh3, _, _ = textbox(215, 120, "Σ₃ᵖ ≠ Π₃ᵖ (Вищий рівень)", size=13, fill=PURPLE_F, stroke=PURPLE_S)
    b_lh2, _, _ = textbox(215, 180, "Σ₂ᵖ ≠ Π₂ᵖ (Другий рівень)", size=13, fill=AMBER_F, stroke=AMBER_S)
    b_lh1, _, _ = textbox(215, 240, "NP ≠ coNP (Перший рівень)", size=13, fill="#eaf0fd", stroke=NEG)
    b_lh0, _, _ = textbox(215, 295, "P (Базовий рівень 0)", size=13, fill="#e9f7ef", stroke=FIELD)
    frags += [b_lh3, b_lh2, b_lh1, b_lh0]
    frags.append(arrow(215, 162, 215, 140, color=LINE))
    frags.append(arrow(215, 222, 215, 200, color=LINE))
    frags.append(arrow(215, 280, 215, 258, color=LINE))

    # Права частина: Обвал
    frags.append(rect(450, 20, 390, 320, fill="#fdecea", stroke=POS, sw=2, rx=8))
    frags.append(text(645, 48, "Обвал: Якщо Σₖᵖ = Πₖᵖ", size=15, bold=True, color=POS))
    frags.append(text(645, 72, "Усі вищі рівні сплющуються до k", size=12, italic=True))

    b_col_top, _, _ = textbox(645, 135, "PH = Σₖᵖ = Σₖ₊₁ᵖ = Σₖ₊₂ᵖ ...\n(Усі вищі квантори згортаються)",
                              size=13, bold=True, fill="#ffffff", stroke=POS, pad=10)
    frags.append(b_col_top)

    b_col_p, _, _ = textbox(645, 230, "Особливий випадок: Якщо P = NP (k = 1)\n ⇒ PH обвалюється повністю до P!",
                            size=13, bold=True, fill="#e9f7ef", stroke=FIELD, pad=10)
    frags.append(b_col_p)

    frags.append(arrow(645, 175, 645, 200, color=POS, sw=2))

    render(os.path.join(IMG, "ph-collapse.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_ph_levels()
    fig_quantifier_alternation()
    fig_oracle_stack()
    fig_ph_collapse()
    print("Фігури успішно згенеровано у teці img/")
