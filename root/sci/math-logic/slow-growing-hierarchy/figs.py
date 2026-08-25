# -*- coding: utf-8 -*-
"""Фігури для теми «Повільнозростаюча ієрархія» (book/algorithms/complexity-computability/slow-growing-hierarchy)."""
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


def fig1_sgh_growth_curves():
    """fig1-sgh-growth-curves.svg: Порівняння темпів росту SGH G_α(n) та FGH F_α(n)."""
    W, H = 880, 520
    frags = []

    frags.append(rect(10, 10, 860, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Спектр функцій повільнозростаючої ієрархії G_α(n) та порівняння з F_α(n)", size=15, bold=True, color="#1e293b"))

    levels = [
        ("G_k(n) = k", "Константний (k)", "Інкремент на скінченних ординалах", BLUE_F, BLUE_S),
        ("G_ω(n) = n", "Лінійний ріст", "Тотожна функція (базовий трансфінітний крок)", BLUE_F, BLUE_S),
        ("G_{ω·k}(n) = k·n", "Лінійно-скалярний", "Масштабування аргументу коефіцієнтом k", TEAL_F, TEAL_S),
        ("G_{ω²}(n) = n²", "Квадратичний ріст", "Діагоналізація добутку омеги", TEAL_F, TEAL_S),
        ("G_{ω^k}(n) = n^k", "Поліноміальний", "Повний спектр довільних поліномів степеня k", GREEN_F, GREEN_S),
        ("G_{ω^ω}(n) = nⁿ", "Суперекспоненціальний", "Степінь з основою та показником n", AMBER_F, AMBER_S),
        ("G_{ε₀}(n) = n ↑↑ n", "Тетрація (рівень F₃)", "Вежа степенів висоти n (швидкість Аккермана)", PURPLE_F, PURPLE_S),
        ("G_{ψ(Ω^ω)}(n) ≈ F_{ε₀}(n)", "Межа PA (колапс)", "Повне наздоганяння FGH через колапсні ординали", RED_F, RED_S),
    ]

    y_start = 65
    dy = 50

    for idx, (formula, growth, desc, fill_c, stroke_c) in enumerate(levels):
        y = y_start + idx * dy

        if idx < len(levels) - 1:
            frags.append(arrow(50, y + 18, 50, y + dy - 2, color="#94a3b8", sw=2))

        b_form, _, _ = textbox(170, y, formula, size=12, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_form)

        b_gr, _, _ = textbox(380, y, growth, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_gr)

        b_desc, _, _ = textbox(660, y, desc, size=11, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_desc)

    y_pa = y_start + 7 * dy - 25
    frags.append(line(25, y_pa, 855, y_pa, color=RED_S, sw=1.5, dash="6 4"))
    frags.append(text(730, y_pa - 6, "Збіг зі швидкозростаючою F_{ε₀}", size=10, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig1-sgh-growth-curves.svg"), W, H, *frags)


def fig2_ordinal_homomorphism():
    """fig2-ordinal-homomorphism.svg: Алгебраїчний гомоморфізм Кантора: заміна ω на n при обчисленні G_α(n)."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгебраїчний гомоморфізм обчислення G_α(n): підстановка ω ↦ n", size=15, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 390, 350, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Ординал у формі Кантора: α = ω³·2 + ω²·5 + 7", size=12, bold=True, color=BLUE_S))

    b_root, _, _ = textbox(225, 125, "Сума (+)", size=12, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_root)

    b_term1, _, _ = textbox(110, 195, "Доданок ω³ · 2", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    b_term2, _, _ = textbox(225, 195, "Доданок ω² · 5", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    b_term3, _, _ = textbox(340, 195, "Константа 7", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_term1)
    frags.append(b_term2)
    frags.append(b_term3)

    frags.append(line(200, 140, 120, 180, color=BLUE_S, sw=1.5))
    frags.append(line(225, 140, 225, 180, color=BLUE_S, sw=1.5))
    frags.append(line(250, 140, 330, 180, color=BLUE_S, sw=1.5))

    b_p1, _, _ = textbox(110, 265, "Показник 3, коеф 2", size=10, fill=AMBER_F, stroke=AMBER_S)
    b_p2, _, _ = textbox(225, 265, "Показник 2, коеф 5", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_p1)
    frags.append(b_p2)
    frags.append(line(110, 212, 110, 250, color=PURPLE_S, sw=1.5))
    frags.append(line(225, 212, 225, 250, color=TEAL_S, sw=1.5))

    b_rule, _, _ = textbox(225, 340, "Правило гомоморфізму: G_α(n) = Eval(α, ω ↦ n)", size=10, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_rule)

    frags.append(rect(450, 60, 400, 350, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(650, 85, "Числова оцінка полінома для аргументу n = 4", size=12, bold=True, color=GREEN_S))

    eval_steps = [
        "1. Заміна бази ω на аргумент n: ω ↦ 4",
        "2. Обчислення першого доданка: 4³ · 2 = 64 · 2 = 128",
        "3. Обчислення другого доданка: 4² · 5 = 16 · 5 = 80",
        "4. Скінченний вільний член: 7",
        "5. Підсумовування: 128 + 80 + 7 = 215",
        "6. Результат: G_{ω³·2 + ω²·5 + 7}(4) = 215",
    ]
    for i, st in enumerate(eval_steps):
        frags.append(text(470, 130 + i * 36, st, size=11, color="#1e293b", anchor="start"))

    b_poly, _, _ = textbox(650, 360, "Алгебраїчний поліном: P(n) = 2n³ + 5n² + 7", size=11, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_poly)

    render(os.path.join(IMG, "fig2-ordinal-homomorphism.svg"), W, H, *frags)


def fig3_girard_catchup():
    """fig3-girard-catchup.svg: Механізм наздоганяння Жірара через колапс ординалів."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Теорема збігу Жірара: колапс незліченних ординалів та стрибок росту G_α", size=15, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 380, 150, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(220, 85, "Швидка ієрархія F_α на малих ординалах", size=12, bold=True, color=BLUE_S))
    frags.append(text(220, 115, "• F₀(n) = n + 1 (інкремент)", size=11, color="#1e293b"))
    frags.append(text(220, 140, "• F₁(n) = 2n, F₂(n) = n·2ⁿ", size=11, color="#1e293b"))
    frags.append(text(220, 165, "• F_ω(n) — рівень Аккермана; F_{ε₀}(n) — межа PA", size=11, bold=True, color=PURPLE_S))
    frags.append(text(220, 190, "Агресивна ітерація F_{α+1}(n) = F_αⁿ(n)", size=10, color=MUTED))

    frags.append(rect(470, 60, 380, 150, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(660, 85, "Повільна ієрархія G_α на малих ординалах", size=12, bold=True, color=AMBER_S))
    frags.append(text(660, 115, "• G_k(n) = k (константа)", size=11, color="#1e293b"))
    frags.append(text(660, 140, "• G_{ω^k}(n) = n^k (поліноми)", size=11, color="#1e293b"))
    frags.append(text(660, 165, "• G_{ε₀}(n) = n ↑↑ n (лише рівень F₃!)", size=11, bold=True, color=RED_S))
    frags.append(text(660, 190, "Мінімальний крок G_{α+1}(n) = G_α(n) + 1", size=10, color=MUTED))

    frags.append(rect(150, 240, 580, 170, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(440, 265, "Міст колапсу Жірара (Bachmann-Howard / Buchholz ψ)", size=13, bold=True, color=PURPLE_S))
    frags.append(text(440, 295, "Колапсна функція перетворює незліченний кардинал Ω у зліченний ординал ψ(Ω)", size=11, color="#1e293b"))
    frags.append(text(440, 320, "Фундаментальна послідовність: ψ(Ω)[n] = ψ(n) породжує рекурсивну діагоналізацію", size=11, color="#1e293b"))

    frags.append(arrow(220, 215, 300, 238, color=BLUE_S, sw=2))
    frags.append(arrow(660, 215, 580, 238, color=AMBER_S, sw=2))

    b_eq, _, _ = textbox(440, 365, "Точка збігу: G_{ψ(Ω^ω)}(n) ≈ F_{ε₀}(n)", size=12, bold=True, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_eq)

    render(os.path.join(IMG, "fig3-girard-catchup.svg"), W, H, *frags)


def fig4_hydra_sgh_reduction():
    """fig4-hydra-sgh-reduction.svg: Редукція дерев Бухгольца та оцінка довжини гри в Гідру через G_α."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Редукція дерев Гідри Бухгольца та відповідність кроків ієрархії SGH", size=15, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 390, 340, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Деревоподібна Гідра з маркованими мітками", size=12, bold=True, color=GREEN_S))

    b_root_h, _, _ = textbox(225, 125, "Корінь: D_0", size=11, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_root_h)

    b_node1, _, _ = textbox(130, 195, "Вузол D_1 (колапс)", size=10, fill=PURPLE_F, stroke=PURPLE_S)
    b_node2, _, _ = textbox(320, 195, "Гілка D_0 (натуральна)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_node1)
    frags.append(b_node2)

    frags.append(line(200, 140, 140, 180, color=GREEN_S, sw=1.5))
    frags.append(line(250, 140, 310, 180, color=GREEN_S, sw=1.5))

    b_leaf1, _, _ = textbox(80, 270, "Голова (D_0)", size=10, fill=RED_F, stroke=RED_S)
    b_leaf2, _, _ = textbox(180, 270, "Голова (D_0)", size=10, fill=RED_F, stroke=RED_S)
    b_leaf3, _, _ = textbox(320, 270, "Листок", size=10, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b_leaf1)
    frags.append(b_leaf2)
    frags.append(b_leaf3)

    frags.append(line(120, 212, 90, 255, color=PURPLE_S, sw=1.5))
    frags.append(line(140, 212, 170, 255, color=PURPLE_S, sw=1.5))
    frags.append(line(320, 212, 320, 255, color=BLUE_S, sw=1.5))

    b_action, _, _ = textbox(225, 345, "Відрубування голови ⟹ ординал спадає з α до α[n]", size=10, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_action)

    frags.append(rect(450, 60, 400, 340, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(650, 85, "Оцінка кількості кроків гри через G_α(n)", size=12, bold=True, color=BLUE_S))

    steps = [
        "• Кожен крок битви зменшує ординал дерева: α ↦ α[n]",
        "• Приріст копій обмежений фактором реплікації n",
        "• G_α(n) точно вимірює максимальну довжину гри:",
        "    Steps(T_α, n) ≤ G_α(n + c)",
        "• Для звичайних гідр Кірбі-Паріса: довжина ~ F_{ε₀}(n)",
        "• Для гідр Бухгольца з колапсом: довжина ~ G_{ψ(Ω^ω)}(n)",
    ]
    for i, st in enumerate(steps):
        frags.append(text(470, 130 + i * 34, st, size=11, color="#1e293b", anchor="start"))

    b_bound, _, _ = textbox(650, 345, "Точний комбінаторний калібр: Steps ≤ G_α(n)", size=11, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_bound)

    render(os.path.join(IMG, "fig4-hydra-sgh-reduction.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_sgh_growth_curves()
    fig2_ordinal_homomorphism()
    fig3_girard_catchup()
    fig4_hydra_sgh_reduction()
    print("All figures successfully generated in img/")
