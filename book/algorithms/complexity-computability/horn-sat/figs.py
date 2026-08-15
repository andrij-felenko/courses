# -*- coding: utf-8 -*-
"""Фігури для теми «Задовільненість хорнівських диз'юнктів (Horn-SAT)»
(book/algorithms/complexity-computability/horn-sat)."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра
COLOR_BG_BOX = "#f8fafc"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_GRID_BORDER = "#cbd5e1"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_BG = "#dbeafe"
COLOR_SUCCESS = "#059669"
COLOR_SUCCESS_BG = "#d1fae5"
COLOR_WARNING = "#d97706"
COLOR_WARNING_BG = "#fef3c7"
COLOR_DANGER = "#dc2626"
COLOR_DANGER_BG = "#fee2e2"
COLOR_MUTED = "#64748b"


def fig_horn_clause_structure():
    """Фігура 1: Класифікація та структура хорнівських диз'юнктів."""
    W, H = 840, 360
    frags = []

    # Три колонки для трьох типів хорнівських диз'юнктів
    col_w = 250
    gap = 20
    start_x = 25

    # 1. Стверджувальне правило (Definite Clause)
    x1 = start_x
    frags.append(rect(x1, 20, col_w, 310, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 48, "Стверджувальне правило", size=15, bold=True, color="#0369a1"))
    frags.append(text(x1 + col_w/2, 70, "(Definite Clause)", size=12, italic=True, color=COLOR_MUTED))

    box1, _, _ = textbox(x1 + col_w/2, 120, "¬p₁ ∨ ¬p₂ ∨ ... ∨ ¬pₖ ∨ q\n(Один позитивний літерал)",
                         size=11, pad=6, fill="#ffffff", stroke="#7dd3fc", sw=1)
    frags.append(box1)

    box1_imp, _, _ = textbox(x1 + col_w/2, 190, "(p₁ ∧ ... ∧ pₖ) → q\n«Якщо всі pᵢ=1, то q=1»",
                             size=11, bold=True, pad=6, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1.2)
    frags.append(box1_imp)

    frags.append(text(x1 + col_w/2, 260, "Застосування:", size=12, bold=True, color=INK))
    frags.append(text(x1 + col_w/2, 282, "Правила виведення у Prolog / Datalog", size=11, color=COLOR_MUTED))
    frags.append(text(x1 + col_w/2, 302, "та каскадна дедукція", size=11, color=COLOR_MUTED))

    # 2. Атом / Факт (Fact / Unit Clause)
    x2 = start_x + col_w + gap
    frags.append(rect(x2, 20, col_w, 310, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 48, "Факт / Атом", size=15, bold=True, color="#15803d"))
    frags.append(text(x2 + col_w/2, 70, "(Fact / Unit Positive)", size=12, italic=True, color=COLOR_MUTED))

    box2, _, _ = textbox(x2 + col_w/2, 120, "q\n(Одиничний позитивний)",
                         size=11, pad=6, fill="#ffffff", stroke="#86efac", sw=1)
    frags.append(box2)

    box2_imp, _, _ = textbox(x2 + col_w/2, 190, "⊤ → q\n«Атом q є безумовно істинним»",
                             size=11, bold=True, pad=6, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.2)
    frags.append(box2_imp)

    frags.append(text(x2 + col_w/2, 260, "Застосування:", size=12, bold=True, color=INK))
    frags.append(text(x2 + col_w/2, 282, "Базові факти системи, початкові", size=11, color=COLOR_MUTED))
    frags.append(text(x2 + col_w/2, 302, "тригери каскаду поширення", size=11, color=COLOR_MUTED))

    # 3. Диз'юнкт-мета / Обмеження (Goal / Negative Clause)
    x3 = start_x + (col_w + gap) * 2
    frags.append(rect(x3, 20, col_w, 310, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(text(x3 + col_w/2, 48, "Диз'юнкт-мета / Обмеження", size=15, bold=True, color="#b91c1c"))
    frags.append(text(x3 + col_w/2, 70, "(Goal / Negative Clause)", size=12, italic=True, color=COLOR_MUTED))

    box3, _, _ = textbox(x3 + col_w/2, 120, "¬p₁ ∨ ¬p₂ ∨ ... ∨ ¬pₘ\n(Жодного позитивного)",
                         size=11, pad=6, fill="#ffffff", stroke="#fca5a5", sw=1)
    frags.append(box3)

    box3_imp, _, _ = textbox(x3 + col_w/2, 190, "(p₁ ∧ ... ∧ pₘ) → ⊥\n«Умови неістинні одночасно»",
                             size=11, bold=True, pad=6, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=1.2)
    frags.append(box3_imp)

    frags.append(text(x3 + col_w/2, 260, "Застосування:", size=12, bold=True, color=INK))
    frags.append(text(x3 + col_w/2, 282, "Перевірка суперечностей (UNSAT)", size=11, color=COLOR_MUTED))
    frags.append(text(x3 + col_w/2, 302, "та запити цілісності (integrity constraint)", size=11, color=COLOR_MUTED))

    return render(os.path.join(IMG, "fig1-horn-clause-structure.svg"), W, H, *frags)


def fig_unit_propagation_cascade():
    """Фігура 2: Каскадне поширення одиниць (Unit Propagation) у хорнівській формулі."""
    W, H = 820, 380
    frags = []

    # Заголовок зверху
    frags.append(text(W/2, 25, "Каскад хвилі дедукції (Unit Propagation) за час O(N)", size=16, bold=True, color=INK))

    # Схема кроків каскаду
    # Крок 0: Факти (Вхід)
    b0, _, _ = textbox(110, 110, "Крок 0: Факти\nA = 1, D = 1\n(У чергу активізації)",
                       size=13, bold=True, pad=10, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.5)
    frags.append(b0)

    # Правило 1: A -> B
    b1, _, _ = textbox(320, 90, "Правило 1: A → B\nОскільки A = 1,\nзнаходимо B = 1",
                       size=12, pad=8, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1.2)
    frags.append(b1)

    # Правило 2: (B ∧ D) -> C
    b2, _, _ = textbox(550, 110, "Правило 2: (B ∧ D) → C\nОскільки B = 1 та D = 1,\nзнаходимо C = 1",
                       size=12, pad=8, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1.2)
    frags.append(b2)

    # Обмеження / Мета: (C ∧ A) -> ⊥ (або перевірка на суперечність)
    b3, _, _ = textbox(720, 250, "Обмеження:\n(C ∧ A) → ⊥\nC=1, A=1 ⇒ ⊥!\nСуперечність (UNSAT)",
                       size=12, bold=True, pad=8, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=1.5)
    frags.append(b3)

    # Позитивна гілка (якщо суперечності немає)
    b4, _, _ = textbox(400, 270, "Якщо суперечностей немає:\nУсі неактивовані змінні := 0\n(Отримуємо єдину МІНІМАЛЬНУ модель)",
                       size=12, bold=True, pad=10, fill="#f0fdf4", stroke=COLOR_SUCCESS, sw=1.5)
    frags.append(b4)

    # Стрілки зв'язку
    frags.append(arrow(190, 110, 250, 90, color=COLOR_ACCENT, sw=2))
    frags.append(arrow(390, 90, 460, 105, color=COLOR_ACCENT, sw=2))
    frags.append(arrow(190, 130, 460, 125, color=COLOR_ACCENT, sw=2))
    frags.append(arrow(640, 110, 680, 200, color=COLOR_DANGER, sw=2))
    frags.append(arrow(640, 120, 520, 230, color=COLOR_SUCCESS, sw=2))

    # Нижній індикатор лінійної складності
    frags.append(rect(50, 325, 720, 40, fill=COLOR_HEADER_BG, stroke=COLOR_GRID_BORDER, sw=1, rx=6))
    frags.append(text(410, 348, "Кожен літерал переглядається максимум 1-2 рази ⇒ Часова складність O(N)",
                      size=13, bold=True, color=COLOR_ACCENT))

    return render(os.path.join(IMG, "fig2-unit-propagation-cascade.svg"), W, H, *frags)


def fig_complexity_landscape():
    """Фігура 3: Ландшафт складності SAT-задач (2-SAT vs Horn-SAT vs 3-SAT)."""
    W, H = 840, 350
    frags = []

    frags.append(text(W/2, 25, "Ієрархія складності задач здійснюваності (SAT)", size=16, bold=True, color=INK))

    col_w = 250
    gap = 20
    start_x = 25

    # 1. 2-SAT
    x1 = start_x
    frags.append(rect(x1, 50, col_w, 275, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 78, "2-SAT", size=16, bold=True, color="#15803d"))
    frags.append(text(x1 + col_w/2, 98, "Диз'юнкти довжини 2", size=12, italic=True, color=COLOR_MUTED))

    b1, _, _ = textbox(x1 + col_w/2, 145, "Складність: Лінійна O(N)\nКлас: NL-повна\n(Паралелізується в NC²)",
                       size=12, pad=6, fill="#ffffff", stroke="#86efac", sw=1)
    frags.append(b1)

    b1_struct, _, _ = textbox(x1 + col_w/2, 220, "Структура:\nГраф імплікацій (2-SCC)\n(a ∨ b) ≡ (¬a → b) ∧ (¬b → a)\nСиметричне дуальне виведення",
                              size=11, pad=6, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1)
    frags.append(b1_struct)

    frags.append(text(x1 + col_w/2, 295, "Симметричні альтернативи", size=11, color=COLOR_MUTED))

    # 2. Horn-SAT
    x2 = start_x + col_w + gap
    frags.append(rect(x2, 50, col_w, 275, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 78, "Horn-SAT", size=16, bold=True, color="#0369a1"))
    frags.append(text(x2 + col_w/2, 98, "≤1 позитивного літерала", size=12, italic=True, color=COLOR_MUTED))

    b2, _, _ = textbox(x2 + col_w/2, 145, "Складність: Лінійна O(N)\nКлас: P-повна\n(Послідовна за своєю суттю)",
                       size=12, pad=6, fill="#ffffff", stroke="#7dd3fc", sw=1)
    frags.append(b2)

    b2_struct, _, _ = textbox(x2 + col_w/2, 220, "Структура:\nГіперграф дедукції\n(p₁ ∧ ... ∧ pₖ) → q\nЗамкненість щодо перетину\nМонтонний каскад одиниць",
                              size=11, pad=6, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1)
    frags.append(b2_struct)

    frags.append(text(x2 + col_w/2, 295, "Межа детермінованого P", size=11, bold=True, color=COLOR_ACCENT))

    # 3. 3-SAT
    x3 = start_x + (col_w + gap) * 2
    frags.append(rect(x3, 50, col_w, 275, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(text(x3 + col_w/2, 78, "3-SAT / Загальний SAT", size=16, bold=True, color="#b91c1c"))
    frags.append(text(x3 + col_w/2, 98, "≥3 літералів у диз'юнкті", size=12, italic=True, color=COLOR_MUTED))

    b3, _, _ = textbox(x3 + col_w/2, 145, "Складність: Експоненційна O(2ⁿ)\nКлас: NP-повна\n(Теорема Кука — Левіна)",
                       size=12, pad=6, fill="#ffffff", stroke="#fca5a5", sw=1)
    frags.append(b3)

    b3_struct, _, _ = textbox(x3 + col_w/2, 220, "Структура:\nДовільні комбінації ∨, ∧, ¬\nВтрата замкненості перетину\nПотреба повернень (backtracking)\nта деревоподібного пошуку",
                              size=11, pad=6, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=1)
    frags.append(b3_struct)

    frags.append(text(x3 + col_w/2, 295, "По той бік межі P vs NP", size=11, bold=True, color=COLOR_DANGER))

    return render(os.path.join(IMG, "fig3-complexity-landscape.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_horn_clause_structure()
    fig_unit_propagation_cascade()
    fig_complexity_landscape()
    print("Horn-SAT figures generated successfully!")
