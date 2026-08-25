# -*- coding: utf-8 -*-
"""Фігури для теми «Диз'юнктивні та кон'юнктивні нормальні форми (ДНФ і КНФ)»
(book/algorithms/complexity-computability/dnf-cnf)."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

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


def fig_dnf_cnf_structures():
    """Фігура 1: Дворівнева деревоподібна структура ДНФ та КНФ."""
    W, H = 840, 360
    frags = []

    # Заголовок
    frags.append(text(W/2, 25, "Дворівнева ієрархічна структура ДНФ та КНФ", size=16, bold=True, color=INK))

    col_w = 380
    gap = 30
    start_x = 25

    # Ліва панель: ДНФ
    x1 = start_x
    frags.append(rect(x1, 45, col_w, 295, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 70, "Диз'юнктивна нормальна форма (ДНФ)", size=14, bold=True, color="#0369a1"))
    frags.append(text(x1 + col_w/2, 90, "Або кон'юнктів (OR of ANDs): F = C₁ ∨ C₂ ∨ C₃", size=11, italic=True, color=COLOR_MUTED))

    # Верхній вузол ДНФ: OR (∨)
    b_or, _, _ = textbox(x1 + col_w/2, 130, "Верхній рівень: Диз'юнкція (∨)",
                         size=12, bold=True, pad=8, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1.2)
    frags.append(b_or)

    # Три кон'юнкти ДНФ
    cx1 = x1 + 65
    cx2 = x1 + col_w/2
    cx3 = x1 + col_w - 65

    b_c1, _, _ = textbox(cx1, 215, "C₁ = A ∧ B\n(Кон'юнкт 1)", size=10, pad=5, fill="#ffffff", stroke="#7dd3fc", sw=1)
    b_c2, _, _ = textbox(cx2, 215, "C₂ = ¬A ∧ C\n(Кон'юнкт 2)", size=10, pad=5, fill="#ffffff", stroke="#7dd3fc", sw=1)
    b_c3, _, _ = textbox(cx3, 215, "C₃ = B ∧ ¬C\n(Кон'юнкт 3)", size=10, pad=5, fill="#ffffff", stroke="#7dd3fc", sw=1)
    frags.extend([b_c1, b_c2, b_c3])

    # Зв'язки ДНФ
    frags.append(arrow(x1 + col_w/2 - 40, 145, cx1, 195, color=COLOR_ACCENT, sw=1.5))
    frags.append(arrow(x1 + col_w/2, 145, cx2, 195, color=COLOR_ACCENT, sw=1.5))
    frags.append(arrow(x1 + col_w/2 + 40, 145, cx3, 195, color=COLOR_ACCENT, sw=1.5))

    # Нижня примітка ДНФ
    frags.append(text(x1 + col_w/2, 285, "Перевірка виконуваності (SAT): O(N)", size=11, bold=True, color=COLOR_SUCCESS))
    frags.append(text(x1 + col_w/2, 305, "Достатньо хоча б одного несуперечливого кон'юнкта", size=10, color=COLOR_MUTED))

    # Права панель: КНФ
    x2 = start_x + col_w + gap
    frags.append(rect(x2, 45, col_w, 295, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 70, "Кон'юнктивна нормальна форма (КНФ)", size=14, bold=True, color="#86198f"))
    frags.append(text(x2 + col_w/2, 90, "І диз'юнктів (AND of ORs): F = D₁ ∧ D₂ ∧ D₃", size=11, italic=True, color=COLOR_MUTED))

    # Верхній вузол КНФ: AND (∧)
    b_and, _, _ = textbox(x2 + col_w/2, 130, "Верхній рівень: Кон'юнкція (∧)",
                          size=12, bold=True, pad=8, fill="#fae8ff", stroke="#c026d3", sw=1.2)
    frags.append(b_and)

    # Три диз'юнкти КНФ
    dx1 = x2 + 65
    dx2 = x2 + col_w/2
    dx3 = x2 + col_w - 65

    b_d1, _, _ = textbox(dx1, 215, "D₁ = A ∨ B\n(Диз'юнкт 1)", size=10, pad=5, fill="#ffffff", stroke="#f0abfc", sw=1)
    b_d2, _, _ = textbox(dx2, 215, "D₂ = ¬A ∨ C\n(Диз'юнкт 2)", size=10, pad=5, fill="#ffffff", stroke="#f0abfc", sw=1)
    b_d3, _, _ = textbox(dx3, 215, "D₃ = B ∨ ¬C\n(Диз'юнкт 3)", size=10, pad=5, fill="#ffffff", stroke="#f0abfc", sw=1)
    frags.extend([b_d1, b_d2, b_d3])

    # Зв'язки КНФ
    frags.append(arrow(x2 + col_w/2 - 40, 145, dx1, 195, color="#c026d3", sw=1.5))
    frags.append(arrow(x2 + col_w/2, 145, dx2, 195, color="#c026d3", sw=1.5))
    frags.append(arrow(x2 + col_w/2 + 40, 145, dx3, 195, color="#c026d3", sw=1.5))

    # Нижня примітка КНФ
    frags.append(text(x2 + col_w/2, 285, "Перевірка загальнозначущості (Tautology): O(N)", size=11, bold=True, color=COLOR_ACCENT))
    frags.append(text(x2 + col_w/2, 305, "Кожен диз'юнкт має містити пару літералів (x ∨ ¬x)", size=10, color=COLOR_MUTED))

    return render(os.path.join(IMG, "fig1-dnf-cnf-structures.svg"), W, H, *frags)


def fig_hypercube_geometry():
    """Фігура 2: Геометрична інтерпретація ДНФ як об'єднання підкубів та КНФ як перетину обмежень."""
    W, H = 840, 360
    frags = []

    frags.append(text(W/2, 25, "Геометрична дуальність у булевому гіперкубі {0,1}³", size=16, bold=True, color=INK))

    col_w = 380
    gap = 30
    start_x = 25

    # 1. ДНФ у гіперкубі: Покриття істинних вершин (1-наборів)
    x1 = start_x
    frags.append(rect(x1, 45, col_w, 295, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 70, "ДНФ: Покриття істинних наборів (1-точок)", size=13, bold=True, color="#15803d"))

    b_dnf_geom, _, _ = textbox(x1 + col_w/2, 125,
                               "• Кожен кон'юнкт фіксує k змінних\n"
                               "• Утворює грань/підкуб розмірності (n - k)\n"
                               "• ДНФ = об'єднання підкубів (Union of Cubes)",
                               size=11, pad=8, fill="#ffffff", stroke="#86efac", sw=1)
    frags.append(b_dnf_geom)

    # Приклад покриття
    b_ex_dnf, _, _ = textbox(x1 + col_w/2, 210,
                             "Приклад: F = (x₁ ∧ x₂) ∨ (¬x₁ ∧ x₃)\n"
                             "• Term (x₁ ∧ x₂): ребро (1,1,0)-(1,1,1)\n"
                             "• Term (¬x₁ ∧ x₃): ребро (0,0,1)-(0,1,1)",
                             size=11, bold=True, pad=8, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.2)
    frags.append(b_ex_dnf)

    frags.append(text(x1 + col_w/2, 285, "Оптимізація: Мінімізація склеюванням (карт Карно)", size=11, bold=True, color="#15803d"))
    frags.append(text(x1 + col_w/2, 305, "Поєднання суміжних граней зменшує кількість літералів", size=10, color=COLOR_MUTED))

    # 2. КНФ у гіперкубі: Заборона хибних вершин (0-наборів)
    x2 = start_x + col_w + gap
    frags.append(rect(x2, 45, col_w, 295, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 70, "КНФ: Відсікання хибних наборів (0-точок)", size=13, bold=True, color="#b91c1c"))

    b_cnf_geom, _, _ = textbox(x2 + col_w/2, 125,
                               "• Кожен диз'юнкт блокує підкуб хибності\n"
                               "• Утворює гіперплощину-обмеження (Constraint)\n"
                               "• КНФ = перетин допустимих півпросторів",
                               size=11, pad=8, fill="#ffffff", stroke="#fca5a5", sw=1)
    frags.append(b_cnf_geom)

    # Приклад обмежень
    b_ex_cnf, _, _ = textbox(x2 + col_w/2, 210,
                             "Приклад: F = (x₁ ∨ x₂) ∧ (¬x₂ ∨ ¬x₃)\n"
                             "• Clause (x₁ ∨ x₂): забороняє вершину (0,0,*)\n"
                             "• Clause (¬x₂ ∨ ¬x₃): забороняє вершину (*,1,1)",
                             size=11, bold=True, pad=8, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=1.2)
    frags.append(b_ex_cnf)

    frags.append(text(x2 + col_w/2, 285, "Оптимізація: Простір пошуку SAT-розв'язувача", size=11, bold=True, color="#b91c1c"))
    frags.append(text(x2 + col_w/2, 305, "Послідовне звуження допустимого підпростору вершин", size=10, color=COLOR_MUTED))

    return render(os.path.join(IMG, "fig2-hypercube-geometry.svg"), W, H, *frags)


def fig_conversion_pipeline():
    """Фігура 3: Порівняння рівносильного алгебраїчного розгортання та рівновиконуваного Цейтін-перетворення."""
    W, H = 840, 360
    frags = []

    frags.append(text(W/2, 25, "Шляхи зведення булевих виразів до КНФ / ДНФ", size=16, bold=True, color=INK))

    col_w = 380
    gap = 30
    start_x = 25

    # 1. Класичне алгебраїчне зведення
    x1 = start_x
    frags.append(rect(x1, 45, col_w, 295, fill="#fffbeab0", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 70, "Класичне алгебраїчне перетворення", size=13, bold=True, color="#b45309"))

    b_alg_steps, _, _ = textbox(x1 + col_w/2, 135,
                                "1. Усунення імплікації (→) та еквівалентності (≡)\n"
                                "2. Закони Де Моргана (перенесення ¬ до змінних)\n"
                                "3. Закони дистрибутивності (розкриття дужок)",
                                size=11, pad=8, fill="#ffffff", stroke="#fcd34d", sw=1)
    frags.append(b_alg_steps)

    b_alg_res, _, _ = textbox(x1 + col_w/2, 220,
                              "Властивість: Еквівалентність за семантикою (F ≡ F')\n"
                              "Ціна: Експоненційний роздув розміру O(2ⁿ)",
                              size=11, bold=True, pad=8, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=1.2)
    frags.append(b_alg_res)

    frags.append(text(x1 + col_w/2, 290, "Застосування: Невелика кількість змінних (n ≤ 15)", size=11, color=COLOR_MUTED))
    frags.append(text(x1 + col_w/2, 308, "та аналітичні математичні виведення", size=10, color=COLOR_MUTED))

    # 2. Трансформація Цейтіна
    x2 = start_x + col_w + gap
    frags.append(rect(x2, 45, col_w, 295, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 70, "Перетворення Цейтіна (Tseytin Encoding)", size=13, bold=True, color="#0369a1"))

    b_ts_steps, _, _ = textbox(x2 + col_w/2, 135,
                               "1. Побудова синтаксичного дерева AST\n"
                               "2. Введення допоміжних змінних xᵢ для вузлів\n"
                               "3. Локальне кодування кожної операції у КНФ",
                               size=11, pad=8, fill="#ffffff", stroke="#7dd3fc", sw=1)
    frags.append(b_ts_steps)

    b_ts_res, _, _ = textbox(x2 + col_w/2, 220,
                             "Властивість: Рівновиконуваність (Equisatisfiability)\n"
                             "Перевага: Строго лінійний розмір O(N)",
                             size=11, bold=True, pad=8, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=1.2)
    frags.append(b_ts_res)

    frags.append(text(x2 + col_w/2, 290, "Застосування: Промислові SAT-розв'язувачі (MiniSAT, Z3)", size=11, color=COLOR_ACCENT))
    frags.append(text(x2 + col_w/2, 308, "та системи верифікації з мільйонами змінних", size=10, color=COLOR_MUTED))

    return render(os.path.join(IMG, "fig3-conversion-pipeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_dnf_cnf_structures()
    fig_hypercube_geometry()
    fig_conversion_pipeline()
    print("DNF/CNF figures generated successfully!")
