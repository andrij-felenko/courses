# -*- coding: utf-8 -*-
"""Фігури для статті «Теорема Вієта».
Запуск із кореня теми:  python figs.py  → SVG у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра
GREEN_FILL  = "#eafaf1"
BLUE_FILL   = "#eaf0fd"
ORANGE_FILL = "#fdf1e5"
PURPLE_FILL = "#f3e8ff"
GRAY_FILL   = "#f4f6f8"

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — Комбінаторна структура вибору доданків при розкритті дужок
# ─────────────────────────────────────────────────────────────────────────────
def fig_expansion_tree():
    W, H = 880, 420
    p = []

    # Заголовок і підзаголовок
    p.append(text(W/2, 28, "Комбінаторна структура формул Вієта для кубічного многочлена", size=16, bold=True))
    p.append(text(W/2, 48, "Розкриття (x − r₁)(x − r₂)(x − r₃): вибір x або −rᵢ на кожному кроці", size=12, color=MUTED, italic=True))

    col1_x = 110
    col2_x = 340
    col3_x = 610
    col4_x = 780

    p.append(fitbox(col1_x - 85, 75, 170, 32, "Лінійні множники", size=12, bold=True, fill=GRAY_FILL))
    p.append(fitbox(col2_x - 110, 75, 220, 32, "8 елементарних добутків", size=12, bold=True, fill=GRAY_FILL))
    p.append(fitbox(col3_x - 110, 75, 220, 32, "Групування за степенем x", size=12, bold=True, fill=GRAY_FILL))
    p.append(fitbox(col4_x - 70, 75, 140, 32, "Формули Вієта", size=12, bold=True, fill=GRAY_FILL))

    p.append(fitbox(col1_x - 75, 140, 150, 45, "1. (x − r₁)\nвибір: x або −r₁", size=11, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(col1_x - 75, 215, 150, 45, "2. (x − r₂)\nвибір: x або −r₂", size=11, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(col1_x - 75, 290, 150, 45, "3. (x − r₃)\nвибір: x або −r₃", size=11, fill=BLUE_FILL, stroke=NEG))

    y_pos = [125, 165, 195, 225, 265, 295, 325, 370]
    terms = [
        "+ x · x · x = + x³",
        "− r₁ · x · x = − r₁ x²",
        "− r₂ · x · x = − r₂ x²",
        "− r₃ · x · x = − r₃ x²",
        "+ r₁ r₂ · x",
        "+ r₁ r₃ · x",
        "+ r₂ r₃ · x",
        "− r₁ r₂ r₃"
    ]

    for y, t in zip(y_pos, terms):
        p.append(fitbox(col2_x - 95, y - 14, 190, 28, t, size=11, fill=FILL, stroke=LINE, sw=1.0))

    p.append(fitbox(col3_x - 100, 115, 200, 32, "x³  (C(3,0) = 1 доданок)", size=11, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(col3_x - 100, 175, 200, 65, "− (r₁ + r₂ + r₃) x²\n(C(3,1) = 3 доданки)", size=11, bold=True, fill=ORANGE_FILL, stroke=POS))
    p.append(fitbox(col3_x - 100, 275, 200, 65, "+ (r₁r₂ + r₁r₃ + r₂r₃) x\n(C(3,2) = 3 доданки)", size=11, bold=True, fill=PURPLE_FILL, stroke=NEG))
    p.append(fitbox(col3_x - 100, 360, 200, 32, "− (r₁ r₂ r₃)  (C(3,3) = 1)", size=11, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(col4_x - 65, 115, 130, 32, "e₀ = 1", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(col4_x - 65, 185, 130, 45, "a₂/a₃ = −e₁\ne₁ = ∑ rᵢ", size=11, bold=True, fill=ORANGE_FILL, stroke=POS))
    p.append(fitbox(col4_x - 65, 285, 130, 45, "a₁/a₃ = +e₂\ne₂ = ∑ rᵢ rⱼ", size=11, bold=True, fill=PURPLE_FILL, stroke=NEG))
    p.append(fitbox(col4_x - 65, 360, 130, 32, "a₀/a₃ = −e₃", size=12, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(col1_x + 80, 240, col2_x - 105, 240, color=MUTED))
    p.append(arrow(col2_x + 100, 130, col3_x - 105, 130, color=FIELD))
    p.append(arrow(col2_x + 100, 200, col3_x - 105, 200, color=POS))
    p.append(arrow(col2_x + 100, 300, col3_x - 105, 300, color=NEG))
    p.append(arrow(col2_x + 100, 375, col3_x - 105, 375, color=NEG))

    p.append(arrow(col3_x + 105, 130, col4_x - 70, 130, color=FIELD))
    p.append(arrow(col3_x + 105, 205, col4_x - 70, 205, color=POS))
    p.append(arrow(col3_x + 105, 305, col4_x - 70, 305, color=NEG))
    p.append(arrow(col3_x + 105, 375, col4_x - 70, 375, color=NEG))

    render(os.path.join(IMG, "vieta-expansion-tree.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — Зв'язок формул Вієта зі спектром матриці (слід і визначник)
# ─────────────────────────────────────────────────────────────────────────────
def fig_matrix_trace_det():
    W, H = 880, 380
    p = []

    p.append(text(W/2, 28, "Спектральні інваріанти матриці як окремі випадки формул Вієта", size=16, bold=True))
    p.append(text(W/2, 48, "Характеристичний многочлен p(λ) = det(λI − A) пов'язує власні значення λᵢ з коефіцієнтами матриці", size=12, color=MUTED, italic=True))

    p.append(fitbox(40, 80, 250, 130,
                    "Квадратна матриця A (n × n)\n"
                    "a₁₁  a₁₂  ...  a₁ₙ\n"
                    "a₂₁  a₂₂  ...  a₂ₙ\n"
                    "...  ...  ...  ...\n"
                    "aₙ₁  aₙ₂  ...  aₙₙ",
                    size=12, fill=GRAY_FILL, stroke=LINE))

    p.append(fitbox(40, 230, 250, 120,
                    "Характеристичний поліном:\n"
                    "p(λ) = det(λI − A)\n"
                    "= (λ − λ₁)(λ − λ₂)...(λ − λₙ)\n"
                    "= λⁿ − c₁ λⁿ⁻¹ + c₂ λⁿ⁻² − ...",
                    size=12, fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(330, 80, 240, 130,
                    "Перший коефіцієнт (e₁):\n\n"
                    "c₁ = λ₁ + λ₂ + ... + λₙ\n"
                    "= tr(A) = ∑ aᵢᵢ\n"
                    "(Слід: сума діагоналі)",
                    size=12, fill=ORANGE_FILL, stroke=POS, bold=True))

    p.append(fitbox(330, 230, 240, 120,
                    "Вільний член (eₙ):\n\n"
                    "cₙ = λ₁ · λ₂ · ... · λₙ\n"
                    "= det(A)\n"
                    "(Визначник: добуток коренів)",
                    size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(610, 80, 230, 130,
                    "Геометричний зміст сліду:\n\n"
                    "• Швидкість росту об'єму\n"
                    "• Дивергенція потоку: div(v)\n"
                    "• Сума розтягів по осях",
                    size=11, fill=ORANGE_FILL, stroke=POS))

    p.append(fitbox(610, 230, 230, 120,
                    "Геометричний зміст визначника:\n\n"
                    "• Масштаб орієнтованого об'єму\n"
                    "• Коефіцієнт зміни n-об'єму\n"
                    "• det(A) = V_new / V_initial",
                    size=11, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(295, 145, 325, 145, color=POS, sw=2.0))
    p.append(arrow(295, 290, 325, 290, color=FIELD, sw=2.0))
    p.append(arrow(575, 145, 605, 145, color=POS, sw=2.0))
    p.append(arrow(575, 290, 605, 290, color=FIELD, sw=2.0))

    render(os.path.join(IMG, "matrix-trace-det.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — Пряма та обернена задачі: Вієт проти нестійкості Вілкінсона
# ─────────────────────────────────────────────────────────────────────────────
def fig_wilkinson_sensitivity():
    W, H = 880, 360
    p = []

    p.append(text(W/2, 28, "Чисельна поведінка: прямий синтез Вієта проти оберненого пошуку коренів", size=16, bold=True))
    p.append(text(W/2, 48, "Обчислення коефіцієнтів за коренями стійке; пошук коренів за коефіцієнтами може бути надчутливим", size=12, color=MUTED, italic=True))

    p.append(fitbox(50, 80, 220, 100,
                    "Задані корені / полюси:\n"
                    "r₁, r₂, ..., rₙ\n"
                    "(бажана динаміка системи)",
                    size=12, fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(330, 80, 220, 100,
                    "Формули Вієта\n(симетрична згортка):\n"
                    "aₖ = (−1)ⁿ⁻ᵏ eₙ₋ₖ(r₁,...,rₙ)\n"
                    "Складність: O(n²)",
                    size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(610, 80, 220, 100,
                    "Фізичні коефіцієнти:\n"
                    "aₙ, aₙ₋₁, ..., a₀\n"
                    "Чисельно СТІЙКИЙ процес\n(без втрати точності)",
                    size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(arrow(275, 130, 325, 130, color=FIELD, sw=2.2))
    p.append(arrow(555, 130, 605, 130, color=FIELD, sw=2.2))

    p.append(fitbox(50, 220, 220, 105,
                    "Збурені коефіцієнти:\n"
                    "aₖ + δaₖ\n"
                    "(похибка округлення: 2⁻²³)",
                    size=12, fill=ORANGE_FILL, stroke=POS, bold=True))

    p.append(fitbox(330, 220, 220, 105,
                    "Чисельний пошук коренів:\n"
                    "Многочлен Вілкінсона W(x)\n"
                    "W(x) = ∏ (x − k) для k=1..20\n"
                    "Погано обумовлена задача",
                    size=11, fill=ORANGE_FILL, stroke=POS, bold=True))

    p.append(fitbox(610, 220, 220, 105,
                    "Катастрофічне зміщення:\n"
                    "Корені зміщуються на ±3.0\n"
                    "або стають комплексними!\n"
                    "Погана обумовленість",
                    size=11, fill=ORANGE_FILL, stroke=POS, bold=True))

    p.append(arrow(275, 272, 325, 272, color=POS, sw=2.2))
    p.append(arrow(555, 272, 605, 272, color=POS, sw=2.2))

    render(os.path.join(IMG, "wilkinson-sensitivity.svg"), W, H, *p)

if __name__ == "__main__":
    fig_expansion_tree()
    fig_matrix_trace_det()
    fig_wilkinson_sensitivity()
    print("Всі 3 фігури успішно згенеровано у", IMG)
