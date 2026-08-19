# -*- coding: utf-8 -*-
"""Фігури для теми «Обмежена арифметика Bounded Arithmetic»
Шлях: book/algorithms/complexity-computability/bounded-arithmetic
"""
import sys
import os

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
CYAN_F, CYAN_S = "#ecfeff", "#0891b2"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_buss_hierarchy():
    """fig1-buss-hierarchy.svg: Ієрархія теорій Басса S₂ⁱ та T₂ⁱ та їхній зв'язок із класами складності."""
    W, H = 880, 560
    frags = []

    b0, _, _ = textbox(440, 490, "IΔ₀ (Арифметика Паріха з обмеженими кванторами)\nФункції: лінійна пам'ять LINSPACE / неповні схеми", size=11, bold=True, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b0)

    frags.append(line(440, 460, 240, 405, color=BLUE_S, sw=1.5))
    frags.append(line(440, 460, 640, 405, color=PURPLE_S, sw=1.5))

    b_s1, _, _ = textbox(240, 375, "Теорія S₂¹ (Σ₁ᵇ-PIND)\nДовідні функції: FP (Поліноміальний час P)\nПропозиційні доведення: Extended Frege (eF)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_t1, _, _ = textbox(640, 375, "Теорія T₂¹ (Σ₁ᵇ-IND)\nДовідні функції: PLS (Поліноміальний локальний пошук)\nПропозиційні доведення: Frege", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_s1)
    frags.append(b_t1)

    frags.append(line(370, 375, 490, 375, color="#64748b", sw=1.5, dash="4,4"))
    frags.append(text(430, 370, "⊆", size=14, bold=True, color="#64748b"))

    frags.append(line(240, 335, 240, 280, color=BLUE_S, sw=1.5))
    frags.append(line(640, 335, 640, 280, color=PURPLE_S, sw=1.5))

    b_s2, _, _ = textbox(240, 250, "Теорія S₂² (Σ₂ᵇ-PIND)\nДовідні функції: FP^NP (Оракул NP)\nКлас складності: P^NP[O(log n)]", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_t2, _, _ = textbox(640, 250, "Теорія T₂² (Σ₂ᵇ-IND)\nДовідні функції: PLS з оракулом NP\nВищий локальний пошук", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_s2)
    frags.append(b_t2)

    frags.append(line(370, 250, 490, 250, color="#64748b", sw=1.5, dash="4,4"))
    frags.append(text(430, 245, "⊆", size=14, bold=True, color="#64748b"))

    frags.append(line(240, 210, 240, 165, color=BLUE_S, sw=1.5, dash="3,3"))
    frags.append(line(640, 210, 640, 165, color=PURPLE_S, sw=1.5, dash="3,3"))

    b_si, _, _ = textbox(240, 135, "Теорія S₂ⁱ (Σᵢᵇ-PIND)\nДовідні функції: FP^(Σᵢ₋₁ᴾ)\nІєрархія складності: Рівень i Поліноміальної ієрархії", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_ti, _, _ = textbox(640, 135, "Теорія T₂ⁱ (Σᵢᵇ-IND)\nДовідні функції: PLS з оракулом Σᵢ₋₁ᴾ\nЛокальний пошук вищих рівнів", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_si)
    frags.append(b_ti)

    frags.append(line(240, 100, 360, 65, color=GREEN_S, sw=1.5))
    frags.append(line(640, 100, 520, 65, color=GREEN_S, sw=1.5))

    b_top, _, _ = textbox(440, 65, "S₂ = ⋃ᵢ S₂ⁱ (Поліноміальна ієрархія PH)  ⊂  PA (Арифметика Пеано / Рекурсивні функції)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_top)

    render(os.path.join(IMG, "fig1-buss-hierarchy.svg"), W, H, *frags, title="Ієрархія теорій обмеженої арифметики Басса та класи складності")


def fig_pind_vs_ind():
    """fig2-pind-vs-ind.svg: Порівняння класичної індукції IND, індукції за довжиною LIND та префіксної індукції PIND."""
    W, H = 880, 480
    frags = []

    # Блок 1: Класична індукція IND
    frags.append(rect(30, 65, 255, 385, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(157, 90, "Класична індукція (IND)", size=13, bold=True, color=RED_S))
    b_ind_f, _, _ = textbox(157, 140, "φ(0) ∧ ∀x(φ(x) → φ(x+1))\n⟹ ∀x φ(x)", size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_ind_f)
    frags.append(text(157, 195, "Кількість кроків розгортання:", size=11, color="#334155"))
    frags.append(text(157, 220, "x кроків = 2^{|x|}", size=14, bold=True, color=RED_S))
    frags.append(text(157, 255, "Експоненційний пошук:", size=11, bold=True, color="#1e293b"))
    frags.append(text(157, 280, "0 ➔ 1 ➔ 2 ➔ 3 ➔ ... ➔ x", size=11, color="#475569"))
    frags.append(text(157, 320, "Дозволяє доводити тотальність", size=10, color="#475569"))
    frags.append(text(157, 340, "надшвидких функцій (суперекспонента,", size=10, color="#475569"))
    frags.append(text(157, 360, "функція Аккермана).", size=10, color="#475569"))
    frags.append(text(157, 400, "Складність: Необмежена / EXP", size=11, bold=True, color=RED_S))

    # Блок 2: Індукція за довжиною LIND
    frags.append(rect(312, 65, 255, 385, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(439, 90, "Індукція за довжиною (LIND)", size=13, bold=True, color=AMBER_S))
    b_lind_f, _, _ = textbox(439, 140, "φ(0) ∧ ∀x(φ(x) → φ(x+1))\n⟹ ∀x φ(|x|)", size=11, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_lind_f)
    frags.append(text(439, 195, "Кількість кроків розгортання:", size=11, color="#334155"))
    frags.append(text(439, 220, "|x| кроків = ⌈log₂(x+1)⌉", size=14, bold=True, color=AMBER_S))
    frags.append(text(439, 255, "Логарифмічний прохід:", size=11, bold=True, color="#1e293b"))
    frags.append(text(439, 280, "0 ➔ 1 ➔ 2 ➔ ... ➔ |x|", size=11, color="#475569"))
    frags.append(text(439, 320, "Обмежує індуктивне доведення", size=10, color="#475569"))
    frags.append(text(439, 340, "довжиною бітового представлення.", size=10, color="#475569"))
    frags.append(text(439, 360, "Поліноміальна кількість кроків.", size=10, color="#475569"))
    frags.append(text(439, 400, "Складність: Поліноміальний час P", size=11, bold=True, color=AMBER_S))

    # Блок 3: Префіксна / Поліноміальна індукція PIND
    frags.append(rect(595, 65, 255, 385, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(722, 90, "Префіксна індукція (PIND)", size=13, bold=True, color=GREEN_S))
    b_pind_f, _, _ = textbox(722, 140, "φ(0) ∧ ∀x(φ(⌊x/2⌋) → φ(x))\n⟹ ∀x φ(x)", size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_pind_f)
    frags.append(text(722, 195, "Кількість кроків розгортання:", size=11, color="#334155"))
    frags.append(text(722, 220, "|x| бітових переходів", size=14, bold=True, color=GREEN_S))
    frags.append(text(722, 255, "Двійкове нарощування:", size=11, bold=True, color="#1e293b"))
    frags.append(text(722, 280, "0 ➔ ⌊⌊x/2⌋/2⌋ ➔ ⌊x/2⌋ ➔ x", size=11, color="#475569"))
    frags.append(text(722, 320, "Будує значення числового аргументу", size=10, color="#475569"))
    frags.append(text(722, 340, "побітово від старшого до молодшого.", size=10, color="#475569"))
    frags.append(text(722, 360, "Еквівалентна LIND у присутності #.", size=10, color="#475569"))
    frags.append(text(722, 400, "Складність: Клас FP (Поліном P)", size=11, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig2-pind-vs-ind.svg"), W, H, *frags, title="Порівняння схем індукції: IND, LIND та PIND")


def fig_witnessing_extraction():
    """fig3-witnessing-extraction.svg: Механізм екстракції поліноміального алгоритму з доведення у теорії S₂¹."""
    W, H = 880, 500
    frags = []

    # Крок 1: Вхідна теорема в S₂¹
    b1, _, _ = textbox(160, 110, "Формальне доведення в S₂¹:\nS₂¹ ⊢ ∀x ∃y A(x, y)\n(де A ∈ Σ₁ᵇ — обмежена формула)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b1)

    # Стрілка 1 -> 2
    frags.append(arrow(285, 110, 360, 110, color=BLUE_S, sw=2))

    # Крок 2: Секвенційне числення LKB та усунення перетинів
    b2, _, _ = textbox(520, 110, "Секвенційне числення LKB:\nУсунення вільних перетинів (Cut-Elimination)\nДерево виводу містить лише формули підструктури", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b2)

    # Стрілка 2 -> 3 (вниз)
    frags.append(arrow(520, 155, 520, 205, color=PURPLE_S, sw=2))

    # Крок 3: Індуктивна трансляція предикатів Wit_A
    b3, _, _ = textbox(520, 255, "Предикат свідка Wit_A(w, x):\nДля кожного правила виводу будується поліноміальний комбінатор:\n• Аксіоми BASIC ➔ пряме обчислення за O(1)\n• Логічні зв'язки ➔ проекції пари Кантора π₁, π₂\n• Правило PIND ➔ поліноміальний цикл довжини |x|", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b3)

    # Стрілка 3 -> 4 (вліво)
    frags.append(arrow(355, 255, 280, 255, color=AMBER_S, sw=2))

    # Крок 4: Поліноміальна програма / Булева схема
    b4, _, _ = textbox(160, 255, "Екстрагований алгоритм:\nФункція f(x) ∈ FP\nЧас роботи: T(n) = O(|x|^c)\nГарантія: ℕ ⊨ A(x, f(x))", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b4)

    # Нижній пояснювальний блок: Практичне значення
    frags.append(rect(40, 360, 800, 105, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=8))
    frags.append(text(440, 385, "Практичний наслідок для комп'ютерних наук та верифікації", size=12, bold=True, color="#1e293b"))
    frags.append(text(440, 410, "1. Доведення існування розв'язку в слабкій арифметиці S₂¹ автоматично генерує коректний алгоритм поліноміального часу.", size=10.5, color="#334155"))
    frags.append(text(440, 430, "2. Якщо теорему про нижню оцінку схем (наприклад, P ≠ NP) вдасться довести в S₂¹, то це породить алгоритми атак.", size=10.5, color="#334155"))
    frags.append(text(440, 450, "3. Обмежена арифметика задає формальні межі того, які теореми складності можна довести методами поліноміального аналізу.", size=10.5, color="#334155"))

    render(os.path.join(IMG, "fig3-witnessing-extraction.svg"), W, H, *frags, title="Теорема Басса про свідків: Синтез поліноміальної програми")


def main():
    fig_buss_hierarchy()
    fig_pind_vs_ind()
    fig_witnessing_extraction()
    print("Згенеровано 3 фігури у", IMG)


if __name__ == "__main__":
    main()
