# -*- coding: utf-8 -*-
"""Фігури для теми «Елементарні функції за Кальмаром» (book/algorithms/complexity-computability/kalmar-elementary-functions)."""
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

def fig1_elementary_spectrum():
    """fig1-elementary-spectrum.svg: Спектр зростання функцій від поліномів до функції Аккермана."""
    W, H = 880, 520
    frags = []

    frags.append(rect(10, 10, 860, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Шкала зростання функцій: щаблі Гжегорчика та клас Кальмара", size=16, bold=True, color="#1e293b"))

    levels = [
        ("E⁰: Базові атоми", "f(x) = x + 1, Z(x), P(x)", "Підлінійне та лінійне зростання", BLUE_F, BLUE_S),
        ("E¹: Додавання", "f(x, y) = x + y", "Лінійне масштабування O(n)", BLUE_F, BLUE_S),
        ("E²: Множення", "f(x, y) = x · y, P(x) = xᶜ", "Поліноміальний клас (містить P, NP)", TEAL_F, TEAL_S),
        ("E³: Клас Кальмара", "f(x) = 2ˣ, 2 ↑↑ k (фіксоване k)", "Вежі експонент фіксованої висоти (ELEMENTARY)", GREEN_F, GREEN_S),
        ("E⁴: Тетрація", "f(n) = 2 ↑↑ n (висота n)", "Надекспоненціальна вежа змінної висоти", AMBER_F, AMBER_S),
        ("Eʷ: Примітивна рекурсія", "Усі рівні Eⁿ разом", "Замикання за довільною схемою рекурсії", PURPLE_F, PURPLE_S),
        ("За межами PR", "A(n, n) — функція Аккермана", "Діагоналізація над примітивною рекурсією", RED_F, RED_S),
    ]

    y_start = 72
    dy = 54

    for idx, (title, formula, desc, fill_c, stroke_c) in enumerate(levels):
        y = y_start + idx * dy
        
        if idx < len(levels) - 1:
            frags.append(arrow(45, y + 16, 45, y + dy - 2, color="#94a3b8", sw=2))

        b_title, _, _ = textbox(150, y, title, size=12, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_title)

        b_form, _, _ = textbox(370, y, formula, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_form)

        b_desc, _, _ = textbox(660, y, desc, size=11, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_desc)

    y_kalmar = y_start + 3 * dy + 28
    frags.append(line(25, y_kalmar, 855, y_kalmar, color=GREEN_S, sw=2, dash="6 4"))
    frags.append(text(730, y_kalmar - 6, "Межа елементарності за Кальмаром (E³)", size=10, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig1-elementary-spectrum.svg"), W, H, *frags)

def fig2_bounded_operators():
    """fig2-bounded-operators.svg: Механізм обмежених операторів у класі Кальмара."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Механізм обмежених операторів замикання класу Кальмара", size=16, bold=True, color="#1e293b"))

    col_w = 260
    xs = [30, 310, 590]

    blocks = [
        ("Обмежене підсумовування", "f(y, x) = ∑_{z ≤ y} g(z, x)", [
            "• Кількість ітерацій: y + 1",
            "• Оцінка росту: f ≤ (y+1) · max(g)",
            "• Зростання не перевищує",
            "  добуток полінома на базу",
            "• Зберігає експоненційну вежу",
        ], BLUE_F, BLUE_S),
        ("Обмежений добуток", "f(y, x) = ∏_{z ≤ y} g(z, x)", [
            "• Кількість множників: y + 1",
            "• Оцінка росту: f ≤ max(g)^(y+1)",
            "• Додає рівно один поверх",
            "  піднесення до степеня",
            "• Гарантує стабільну вежу",
        ], GREEN_F, GREEN_S),
        ("Обмежений μ-пошук", "f(y, x) = μ z ≤ y [P(z, x) == 1]", [
            "• Перебір значень z ∈ [0, y]",
            "• Гарантована зупинка за ≤ y",
            "• Результат строго f ≤ y",
            "• Усуває нескінченний",
            "  цикл пошуку моделі",
        ], AMBER_F, AMBER_S),
    ]

    for x, (title, form, items, fill_c, stroke_c) in zip(xs, blocks):
        frags.append(rect(x, 60, col_w, 330, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        frags.append(text(x + col_w/2, 88, title, size=13, bold=True, color=stroke_c))
        
        b_form, _, _ = textbox(x + col_w/2, 125, form, size=11, bold=True, fill="#ffffff", stroke=stroke_c)
        frags.append(b_form)

        for i, itm in enumerate(items):
            frags.append(text(x + 16, 175 + i * 32, itm, size=11, color="#1e293b", anchor="start"))

    render(os.path.join(IMG, "fig2-bounded-operators.svg"), W, H, *frags)

def fig3_complexity_hierarchy():
    """fig3-complexity-hierarchy.svg: Вкладення класів складності в ELEMENTARY та неделементарні задачі."""
    W, H = 880, 450
    frags = []

    frags.append(rect(10, 10, 860, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Вкладення класів складності в ELEMENTARY та неделементарні задачі", size=16, bold=True, color="#1e293b"))

    # Elementary zone
    frags.append(rect(30, 60, 480, 360, fill="#f0fdf4", stroke=GREEN_S, sw=2, rx=8))
    frags.append(text(270, 85, "Клас ELEMENTARY (∪ DTIME(2 ↑↑ k))", size=14, bold=True, color=GREEN_S))

    classes = [
        ("P", "Сортування, пошук шляху, лінійне програмування", 120, BLUE_F, BLUE_S),
        ("NP / co-NP", "SAT, розфарбування графів, кліка", 180, TEAL_F, TEAL_S),
        ("PSPACE", "TQBF, перевірка формул LTL, ігри на скінченних полях", 240, AMBER_F, AMBER_S),
        ("EXPTIME / k-EXPTIME", "Ігри на дошці n×n, верифікація автоматів", 300, PURPLE_F, PURPLE_S),
        ("Вежі експонент фіксованої висоти", "Теореми логіки першого порядку з обмеженими кванторами", 360, "#ffffff", "#475569"),
    ]

    for name, desc, y_pos, f_col, s_col in classes:
        frags.append(rect(45, y_pos - 15, 450, 45, fill=f_col, stroke=s_col, sw=1.2, rx=6))
        frags.append(text(60, y_pos + 12, name, size=11, bold=True, color=s_col, anchor="start"))
        frags.append(text(210, y_pos + 12, desc, size=10, color="#475569", anchor="start"))

    # Non-elementary zone
    frags.append(rect(530, 60, 320, 360, fill="#fef2f2", stroke=RED_S, sw=2, rx=8))
    frags.append(text(690, 85, "Неделементарні задачі (∉ ELEMENTARY)", size=13, bold=True, color=RED_S))

    nonelem = [
        ("Арифметика Пресбургера (MSO)", "Нижня межа: 2 ↑↑ (c · n)\nВимагає вежу експонент висоти O(n)", 135),
        ("Еквівалентність регексів", "Регулярні вирази з доповненням:\nТеорема Стокмеєра — Меєра", 215),
        ("Мережі Петрі / Досяжність", "Досяжність у векторних системах:\nПовна за Аккерманом", 295),
        ("Переписування термів (TRS)", "Завершуваність Кнута — Бендікса:\nВиходить за межі будь-якої вежі", 370),
    ]

    for title, desc, y_pos in nonelem:
        frags.append(rect(545, y_pos - 20, 290, 60, fill="#ffffff", stroke=RED_S, sw=1, rx=6))
        frags.append(text(555, y_pos, title, size=11, bold=True, color=RED_S, anchor="start"))
        lines = desc.split("\n")
        frags.append(text(555, y_pos + 18, lines[0], size=9, color="#475569", anchor="start"))
        if len(lines) > 1:
            frags.append(text(555, y_pos + 31, lines[1], size=9, color="#475569", anchor="start"))

    render(os.path.join(IMG, "fig3-complexity-hierarchy.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_elementary_spectrum()
    fig2_bounded_operators()
    fig3_complexity_hierarchy()
    print("All figures generated successfully.")
