# -*- coding: utf-8 -*-
"""Фігури для теми «Арифметична ієрархія» (book/algorithms/complexity-computability/arithmetic-hierarchy)."""
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

def fig_hierarchy_cone():
    """fig1-hierarchy-cone.svg: Візуалізація конуса вкладення класів арифметичної ієрархії."""
    W, H = 840, 520
    frags = []

    # Загальний фон
    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Структура та конус вкладення класів Арифметичної Ієрархії", size=16, bold=True, color="#1e293b"))

    # Рівень Δ₀⁰ / Σ₀⁰ / Π₀⁰
    b0, _, _ = textbox(420, 460, "Δ₀⁰ = Σ₀⁰ = Π₀⁰ (Обчислювані / Розв'язні предикати з обмеженими кванторами)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b0)

    # Рівень 1: Σ₁⁰ та Π₁⁰
    frags.append(line(420, 438, 260, 382, color=GREEN_S, sw=1.5))
    frags.append(line(420, 438, 580, 382, color=GREEN_S, sw=1.5))

    b_s1, _, _ = textbox(260, 370, "Σ₁⁰ (Rec. Enumerable / RE)\nПриклад: K (Проблема зупинки)\n∃y R(x,y)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_p1, _, _ = textbox(580, 370, "Π₁⁰ (Co-RE / Доповнення RE)\nПриклад: EMPTY (Порожнеча)\n∀y R(x,y)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_s1)
    frags.append(b_p1)

    # Перетин Δ₁⁰
    b_d1, _, _ = textbox(420, 370, "Δ₁⁰ = Σ₁⁰ ∩ Π₁⁰\n(Обчислювані множини)", size=10, fill="#ffffff", stroke="#64748b")
    frags.append(b_d1)

    # Рівень 2: Σ₂⁰ та Π₂⁰
    frags.append(line(260, 335, 260, 270, color=BLUE_S, sw=1.5))
    frags.append(line(580, 335, 580, 270, color=PURPLE_S, sw=1.5))
    frags.append(line(420, 345, 420, 270, color="#64748b", sw=1.5))

    b_s2, _, _ = textbox(260, 250, "Σ₂⁰ (Оракул 0')\nПриклад: FIN (Скінченність Wₑ)\n∃y ∀z R(x,y,z)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_p2, _, _ = textbox(580, 250, "Π₂⁰ (Оракул 0')\nПриклад: TOTAL, INF\n∀y ∃z R(x,y,z)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_s2)
    frags.append(b_p2)

    # Перетин Δ₂⁰
    b_d2, _, _ = textbox(420, 250, "Δ₂⁰ = Σ₂⁰ ∩ Π₂⁰\n(Обчислювані з оракулом K)", size=10, fill="#ffffff", stroke="#64748b")
    frags.append(b_d2)

    # Рівень 3: Σ₃⁰ та Π₃⁰
    frags.append(line(260, 215, 260, 150, color=BLUE_S, sw=1.5))
    frags.append(line(580, 215, 580, 150, color=PURPLE_S, sw=1.5))

    b_s3, _, _ = textbox(260, 130, "Σ₃⁰ (Оракул 0'')\nПриклад: COFIN, REC\n∃y ∀z ∃w R(x,y,z,w)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_p3, _, _ = textbox(580, 130, "Π₃⁰ (Оракул 0'')\nПриклад: COREC\n∀y ∃z ∀w R(x,y,z,w)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_s3)
    frags.append(b_p3)

    # Перетин Δ₃⁰
    b_d3, _, _ = textbox(420, 130, "Δ₃⁰ = Σ₃⁰ ∩ Π₃⁰\n(Обчислювані з оракулом 0'')", size=10, fill="#ffffff", stroke="#64748b")
    frags.append(b_d3)

    # Верхній стрілочний вихід до AH та Неарифметичних множин
    frags.append(line(420, 105, 420, 75, color=AMBER_S, sw=2, dash="4,4"))
    b_ah, _, _ = textbox(420, 65, "Арифметична ієрархія AH = ⋃ₙ Σ♁⁰  ⊂  True Arithmetic / Аналітична ієрархія (Σ₁¹)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_ah)

    render(os.path.join(IMG, "fig1-hierarchy-cone.svg"), W, H, *frags)


def fig_quantifier_alternation():
    """fig2-quantifier-alternation.svg: Процес згортання однакових кванторів та чергування кванторів."""
    W, H = 840, 360
    frags = []

    frags.append(rect(10, 10, 820, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Перетворення префіксів: згортання однорідних кванторів через пару Кантора", size=16, bold=True, color="#1e293b"))

    # Крок 1: Початкова формула з кількома однорідними кванторами
    frags.append(text(80, 85, "1. Початкова формула з повторюваними однаковими кванторами:", size=12, bold=True, color="#334155"))
    b_step1, _, _ = textbox(420, 115, "P(x)  ≡  ∃y₁  ∃y₂  ∀z₁  ∀z₂  ∀z₃  ∃w  R(x, y₁, y₂, z₁, z₂, z₃, w)", size=12, fill=RED_F, stroke=RED_S)
    frags.append(b_step1)

    # Стрілка вниз
    frags.append(line(420, 138, 420, 162, color="#64748b", sw=2))

    # Крок 2: Кодування пар функцією Кантора <a,b> = (a+b)(a+b+1)/2 + b
    frags.append(text(80, 178, "2. Згортання сусідніх кванторів через функцію парування Кантора ⟨a, b⟩:", size=12, bold=True, color="#334155"))
    b_step2, _, _ = textbox(420, 208, "∃y₁, y₂ ↦ ∃Y (Y = ⟨y₁, y₂⟩)    та    ∀z₁, z₂, z₃ ↦ ∀Z (Z = ⟨⟨z₁, z₂⟩, z₃⟩)", size=12, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_step2)

    # Стрілка вниз
    frags.append(line(420, 230, 420, 255, color="#64748b", sw=2))

    # Крок 3: Префіксна форма із суворим чергуванням (Σ₃⁰)
    frags.append(text(80, 270, "3. Канонічна префіксна форма з n = 3 чергуваннями (Σ₃⁰):", size=12, bold=True, color="#334155"))
    b_step3, _, _ = textbox(420, 300, "P(x)  ≡  ∃Y  ∀Z  ∃w  R'(x, Y, Z, w)   ⇒   Формула класу Σ₃⁰", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_step3)

    render(os.path.join(IMG, "fig2-quantifier-alternation.svg"), W, H, *frags)


def fig_posts_theorem():
    """fig3-posts-theorem.svg: Міст Поста між рівнем кванторів та ітераціями стрибка Тюринга."""
    W, H = 840, 400
    frags = []

    frags.append(rect(10, 10, 820, 380, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Теорема Поста: еквівалентність логічних префіксів та оракулів Тюринга", size=16, bold=True, color="#1e293b"))

    # Ліва колона: Логічний вимір (Квантори)
    frags.append(rect(40, 65, 340, 290, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(210, 90, "Логічний префікс (Синтаксис)", size=14, bold=True, color=BLUE_S))

    b_l1, _, _ = textbox(210, 135, "Σ₁⁰: ∃y R(x,y)\nΠ₁⁰: ∀y R(x,y)", size=12, fill="#ffffff", stroke=BLUE_S)
    b_l2, _, _ = textbox(210, 210, "Σ₂⁰: ∃y ∀z R(x,y,z)\nΠ₂⁰: ∀y ∃z R(x,y,z)", size=12, fill="#ffffff", stroke=BLUE_S)
    b_l3, _, _ = textbox(210, 285, "Σ₃⁰: ∃y ∀z ∃w R(x,y,z,w)\nΠ₃⁰: ∀y ∃z ∀w R(x,y,z,w)", size=12, fill="#ffffff", stroke=BLUE_S)

    frags.append(b_l1)
    frags.append(b_l2)
    frags.append(b_l3)

    # Права колона: Обчислювальний вимір (Оракули та Стрибки)
    frags.append(rect(460, 65, 340, 290, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(630, 90, "Оракули та Стрибки Тюринга", size=14, bold=True, color=PURPLE_S))

    b_r1, _, _ = textbox(630, 135, "r.e. відносно ∅\nСтрибок 0' = K (Проблема зупинки)", size=12, fill="#ffffff", stroke=PURPLE_S)
    b_r2, _, _ = textbox(630, 210, "r.e. відносно 0'\nДругий стрибок 0'' = K⁰'", size=12, fill="#ffffff", stroke=PURPLE_S)
    b_r3, _, _ = textbox(630, 285, "r.e. відносно 0''\nТретій стрибок 0''' = K⁰''", size=12, fill="#ffffff", stroke=PURPLE_S)

    frags.append(b_r1)
    frags.append(b_r2)
    frags.append(b_r3)

    # Горизонтальні мости еквівалентності (Теорема Поста)
    frags.append(line(355, 135, 485, 135, color=GREEN_S, sw=2))
    frags.append(line(355, 210, 485, 210, color=GREEN_S, sw=2))
    frags.append(line(355, 285, 485, 285, color=GREEN_S, sw=2))

    b_eq1, _, _ = textbox(420, 135, "⇔", size=14, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_eq2, _, _ = textbox(420, 210, "⇔", size=14, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_eq3, _, _ = textbox(420, 285, "⇔", size=14, bold=True, fill=GREEN_F, stroke=GREEN_S)

    frags.append(b_eq1)
    frags.append(b_eq2)
    frags.append(b_eq3)

    # Нижня примітка про Δₙ₊₁⁰
    b_note, _, _ = textbox(420, 360, "Δₙ₊₁⁰ = Σₙ₊₁⁰ ∩ Πₙ₊₁⁰ ⟺ Тюринг-обчислюваність з оракулом 0⁽ⁿ⁾ (A ≤ₜ 0⁽ⁿ⁾)", size=11, bold=True, fill="#ffffff", stroke="#475569")
    frags.append(b_note)

    render(os.path.join(IMG, "fig3-posts-theorem.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hierarchy_cone()
    fig_quantifier_alternation()
    fig_posts_theorem()
    print("Figures generated successfully.")
