# -*- coding: utf-8 -*-
"""Фігури для теми «Швидкозростаюча ієрархія» (book/algorithms/complexity-computability/fast-growing-hierarchy)."""
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

def fig1_fgh_levels():
    """fig1-fgh-levels.svg: Рівні швидкозростаючої ієрархії та їхні обчислювальні межі."""
    W, H = 880, 500
    frags = []

    frags.append(rect(10, 10, 860, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Структура рівнів швидкозростаючої ієрархії F_α(n)", size=16, bold=True, color="#1e293b"))

    levels = [
        ("F₀(n) = n + 1", "Лінійний ріст", "Інкремент (базовий крок)", BLUE_F, BLUE_S),
        ("F₁(n) = 2n", "Лінійно-скалярний", "Ітерація додавання (множення)", BLUE_F, BLUE_S),
        ("F₂(n) = n · 2ⁿ", "Експоненціальний", "Ітерація множення (піднесення до степеня)", TEAL_F, TEAL_S),
        ("F₃(n) > 2 ↑↑ n", "Гіперекспоненціальний", "Вежа степеней (тетрація)", AMBER_F, AMBER_S),
        ("F_ω(n) = Fₙ(n)", "Діагоналізація (ω)", "Рівень функції Аккермана A(n,n)", PURPLE_F, PURPLE_S),
        ("F_{ω+1}(n) = F_ωⁿ(n)", "Ітерація Аккермана", "Перевищує всі примітивно-рекурсивні функції", PURPLE_F, PURPLE_S),
        ("F_{ω^ω}(n)", "Трансфінітний крок", "Рівень ітерацій з ординалами ω^k", RED_F, RED_S),
        ("F_{ε₀}(n)", "Межа арифметики Пеано", "Нездійсненність доведення тотальності в PA", RED_F, RED_S),
    ]

    y_start = 65
    dy = 50

    for idx, (formula, growth, desc, fill_c, stroke_c) in enumerate(levels):
        y = y_start + idx * dy
        
        if idx < len(levels) - 1:
            frags.append(arrow(50, y + 18, 50, y + dy - 2, color="#94a3b8", sw=2))

        b_form, _, _ = textbox(160, y, formula, size=12, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_form)

        b_gr, _, _ = textbox(370, y, growth, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_gr)

        b_desc, _, _ = textbox(650, y, desc, size=11, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_desc)

    y_pa = y_start + 7 * dy - 25
    frags.append(line(25, y_pa, 855, y_pa, color=RED_S, sw=1.5, dash="6 4"))
    frags.append(text(720, y_pa - 6, "Бар'єр доводжуваності PA (ε₀)", size=10, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig1-fgh-levels.svg"), W, H, *frags)


def fig2_ordinal_tree():
    """fig2-ordinal-tree.svg: Представлення ординалів у формі Кантора та редукція фундаментальної послідовності."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Редукція граматичного дерева ординала λ[n] для обчислення F_λ(n)", size=16, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 390, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Канонічне дерево Кантора: α = ω^(ω + 1) + 2", size=13, bold=True, color=BLUE_S))

    b_root, _, _ = textbox(225, 125, "Сума (+)", size=12, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_root)

    b_left, _, _ = textbox(130, 195, "Доданок ω^(ω + 1)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    b_right, _, _ = textbox(320, 195, "Скінченна константа: 2", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_left)
    frags.append(b_right)

    frags.append(line(200, 140, 150, 180, color=BLUE_S, sw=1.5))
    frags.append(line(250, 140, 300, 180, color=BLUE_S, sw=1.5))

    b_exp, _, _ = textbox(130, 265, "Показник: ω + 1", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_exp)
    frags.append(line(130, 212, 130, 250, color=PURPLE_S, sw=1.5))

    b_exp_w, _, _ = textbox(80, 335, "Граничний ω", size=10, fill=TEAL_F, stroke=TEAL_S)
    b_exp_c, _, _ = textbox(180, 335, "Константа 1", size=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_exp_w)
    frags.append(b_exp_c)
    frags.append(line(115, 280, 90, 320, color=AMBER_S, sw=1.5))
    frags.append(line(145, 280, 170, 320, color=AMBER_S, sw=1.5))

    frags.append(rect(450, 60, 400, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(650, 85, "Кроки підстановки фундаментальної послідовності", size=13, bold=True, color=GREEN_S))

    steps = [
        "1. Вхід: F_{ω^(ω + 1)}(n) при n = 3",
        "2. Правило: (ω^(α+1))[n] = ω^α · n",
        "3. Показник: (ω + 1)[3] = ω, тому:",
        "4. (ω^(ω + 1))[3] = ω^ω · 3 = ω^ω + ω^ω + ω^ω",
        "5. Далі підстановка: (ω^ω)[3] = ω³",
        "6. Результат: F_{ω³ + ω³ + ω³}(3)",
    ]

    for idx, st in enumerate(steps):
        y_st = 125 + idx * 40
        b_st, _, _ = textbox(650, y_st, st, size=11, fill="#ffffff", stroke="#475569")
        frags.append(b_st)

    render(os.path.join(IMG, "fig2-ordinal-tree.svg"), W, H, *frags)


def fig3_peano_provability():
    """fig3-peano-provability.svg: Спектр доказової сили формальних систем та граничні ординали."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Спектр доказової сили формальних систем та відповідні ординали FGH", size=16, bold=True, color="#1e293b"))

    col_w = 180
    xs = [50, 250, 450, 650]
    headers = [
        ("PRA", "Примітивна арифметика", "Доказовий ординал: ω^ω", BLUE_F, BLUE_S),
        ("PA", "Арифметика Пеано", "Доказовий ординал: ε₀", PURPLE_F, PURPLE_S),
        ("ATR₀", "Арифметика трансфінітна", "Доказовий ординал: Γ₀", AMBER_F, AMBER_S),
        ("Π¹₁-CA₀", "Предикація другого порядку", "Ординал Бахмана — Говарда", RED_F, RED_S),
    ]

    for x, (title, subtitle, ord_txt, fill_c, stroke_c) in zip(xs, headers):
        frags.append(rect(x, 60, col_w, 340, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        frags.append(text(x + col_w/2, 85, title, size=16, bold=True, color=stroke_c))
        frags.append(text(x + col_w/2, 105, subtitle, size=10, italic=True, color="#475569"))

        b_ord, _, _ = textbox(x + col_w/2, 140, ord_txt, size=10, bold=True, fill="#ffffff", stroke=stroke_c)
        frags.append(b_ord)

    tasks = [
        (50 + 90, 200, "Функції з O(n!)\nта вежі експонент F₃"),
        (50 + 90, 280, "Функція Аккермана F_ω\n(доводиться в PRA)"),

        (250 + 90, 200, "Послідовності Ґудстейна\n(ріст F_{ε₀})"),
        (250 + 90, 280, "Гра з Гідрою Кірбі — Паріса\n(недоказово в PA)"),

        (450 + 90, 200, "Теорема Краскала\nпро дерева (F_{Γ₀})"),
        (450 + 90, 280, "Неперервний перебір\nординалів Фейфермана"),

        (650 + 90, 200, "Теорема Робертсона — Сеймура\nпро мінори графів"),
        (650 + 90, 280, "Великі ординали\nта ієрархія Тарського"),
    ]

    for tx, ty, ttxt in tasks:
        b_t, _, _ = textbox(tx, ty, ttxt, size=10, fill="#ffffff", stroke="#64748b")
        frags.append(b_t)

    render(os.path.join(IMG, "fig3-peano-provability.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_fgh_levels()
    fig2_ordinal_tree()
    fig3_peano_provability()
    print("All figures generated successfully.")
