# -*- coding: utf-8 -*-
"""Фігури до статті «Визначник Вандермонда»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Структура матриці Вандермонда та поліноміальна інтерполяція
# ─────────────────────────────────────────────────────────────────────────────
def fig_vandermonde_matrix_structure():
    W, H = 880, 480
    frby = []

    frby.append(text(W / 2, 28, "Матриця Вандермонда та система поліноміальної інтерполяції", size=15, bold=True, color=INK))

    # Ліва частина: Матриця V_n
    frby.append(rect(40, 60, 360, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(220, 88, "Матриця Вандермонда V_n", size=14, bold=True, color=INK))
    frby.append(line(50, 102, 390, 102, color=LINE, sw=1))

    # Стовпчики зі степенями
    frby.append(text(100, 125, "Ступінь 0", size=11, color=MUTED))
    frby.append(text(180, 125, "Ступінь 1", size=11, color=MUTED))
    frby.append(text(260, 125, "Ступінь 2", size=11, color=MUTED))
    frby.append(text(340, 125, "Ступінь n-1", size=11, color=MUTED))

    # Рядки матриці
    rows_data = [
        ("Рядок 0 (x₀)", "1", "x₀", "x₀²", "x₀ⁿ⁻¹", 165),
        ("Рядок 1 (x₁)", "1", "x₁", "x₁²", "x₁ⁿ⁻¹", 225),
        ("Рядок 2 (x₂)", "1", "x₂", "x₂²", "x₂ⁿ⁻¹", 285),
        ("Рядок n-1 (xₙ₋₁)", "1", "xₙ₋₁", "xₙ₋₁²", "xₙ₋₁ⁿ⁻¹", 375),
    ]

    for label, c0, c1, c2, cn, y_pos in rows_data:
        frby.append(rect(55, y_pos - 18, 330, 34, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
        frby.append(text(100, y_pos + 4, c0, size=13, bold=True, color=INK))
        frby.append(text(180, y_pos + 4, c1, size=13, bold=True, color=INK))
        frby.append(text(260, y_pos + 4, c2, size=13, bold=True, color=INK))
        frby.append(text(340, y_pos + 4, cn, size=13, bold=True, color=INK))

    frby.append(text(220, 335, "⋮", size=18, bold=True, color=MUTED))

    frby.append(text(220, 425, "Кожен рядок i — геометрична прогресія вузла x_i", size=11, color=MUTED))

    # Знак множення
    frby.append(text(420, 250, "×", size=22, bold=True, color=INK))

    # Вектор коефіцієнтів c
    frby.append(rect(445, 120, 80, 270, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    frby.append(text(485, 105, "Коефіцієнти c", size=12, bold=True, color="#ca8a04"))
    frby.append(text(485, 165, "c₀", size=13, bold=True, color=INK))
    frby.append(text(485, 225, "c₁", size=13, bold=True, color=INK))
    frby.append(text(485, 285, "c₂", size=13, bold=True, color=INK))
    frby.append(text(485, 335, "⋮", size=18, bold=True, color=MUTED))
    frby.append(text(485, 375, "cₙ₋₁", size=13, bold=True, color=INK))

    # Знак дорівнює
    frby.append(text(545, 250, "=", size=22, bold=True, color=INK))

    # Вектор значень y
    frby.append(rect(570, 120, 80, 270, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frby.append(text(610, 105, "Значення y", size=12, bold=True, color=FIELD))
    frby.append(text(610, 165, "y₀", size=13, bold=True, color=INK))
    frby.append(text(610, 225, "y₁", size=13, bold=True, color=INK))
    frby.append(text(610, 285, "y₂", size=13, bold=True, color=INK))
    frby.append(text(610, 335, "⋮", size=18, bold=True, color=MUTED))
    frby.append(text(610, 375, "yₙ₋₁", size=13, bold=True, color=INK))

    # Права панель із висновком
    b_info, _, _ = textbox(760, 255, "Рівняння інтерполяції:\nP(x_i) = ∑ c_j · x_iʲ = y_i\n\nЄдиність розв'язку:\ndet(V_n) ≠ 0\nякщо всі вузли x_i різні", size=12, pad=10, fill="#ffffff", stroke=LINE, sw=1.5)
    frby.append(b_info)

    render(os.path.join(OUT, "vandermonde-matrix-structure.svg"), W, H, *frby,
           title="Структура матриці Вандермонда та система інтерполяції")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Геометричне виродження об'єму при зближенні вузлів
# ─────────────────────────────────────────────────────────────────────────────
def fig_vandermonde_geometric_collapse():
    W, H = 880, 440
    frby = []

    frby.append(text(W / 2, 28, "Геометричний зміст визначника: виродження об'єму при збігу вузлів", size=15, bold=True, color=INK))

    # Ліва картка: Різні вузли -> Ненульовий об'єм
    frby.append(rect(40, 60, 380, 350, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frby.append(text(230, 88, "Випадок 1: Усі вузли різні (x₀ ≠ x₁ ≠ x₂)", size=13, bold=True, color=FIELD))
    frby.append(line(55, 102, 405, 102, color=FIELD, sw=1))

    # Числова вісь з точками
    frby.append(line(70, 160, 390, 160, color=INK, sw=1.5))
    frby.append(arrow(370, 160, 395, 160, color=INK, sw=1.5))
    frby.append(text(395, 145, "x", size=12, bold=True, color=INK))

    frby.append(circle(120, 160, 5, fill=POS, stroke=INK, sw=1.5))
    frby.append(text(120, 185, "x₀", size=12, bold=True, color=POS))

    frby.append(circle(230, 160, 5, fill=NEG, stroke=INK, sw=1.5))
    frby.append(text(230, 185, "x₁", size=12, bold=True, color=NEG))

    frby.append(circle(340, 160, 5, fill=FIELD, stroke=INK, sw=1.5))
    frby.append(text(340, 185, "x₂", size=12, bold=True, color=FIELD))

    # Відстані
    frby.append(line(125, 135, 225, 135, color=NEG, sw=1.2, dash="3 3"))
    frby.append(text(175, 125, "Δ₁₀ = x₁ - x₀ > 0", size=10, color=NEG))

    frby.append(line(235, 135, 335, 135, color=FIELD, sw=1.2, dash="3 3"))
    frby.append(text(285, 125, "Δ₂₁ = x₂ - x₁ > 0", size=10, color=FIELD))

    # Орієнтований паралелепіпед
    frby.append(rect(90, 220, 280, 90, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frby.append(text(230, 245, "Орієнтований гіпероб'єм:", size=12, bold=True, color=INK))
    frby.append(text(230, 270, "det(V₃) = (x₁ - x₀)(x₂ - x₀)(x₂ - x₁) ≠ 0", size=12, bold=True, color=FIELD))
    frby.append(text(230, 295, "Базисні вектори лінійно незалежні", size=11, color=MUTED))

    frby.append(text(230, 360, "✓ Система має єдиний розв'язок", size=12, bold=True, color=FIELD))
    frby.append(text(230, 385, "✓ Інтерполяційний поліном існує і єдиний", size=11, color=MUTED))

    # Права картка: Два вузли збігаються -> Сплющення в нуль
    frby.append(rect(460, 60, 380, 350, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frby.append(text(650, 88, "Випадок 2: Збіг вузлів (x₂ → x₁)", size=13, bold=True, color=POS))
    frby.append(line(475, 102, 825, 102, color=POS, sw=1))

    # Числова вісь зі злиттям точок
    frby.append(line(490, 160, 810, 160, color=INK, sw=1.5))
    frby.append(arrow(790, 160, 815, 160, color=INK, sw=1.5))
    frby.append(text(815, 145, "x", size=12, bold=True, color=INK))

    frby.append(circle(540, 160, 5, fill=POS, stroke=INK, sw=1.5))
    frby.append(text(540, 185, "x₀", size=12, bold=True, color=POS))

    frby.append(circle(710, 160, 6, fill=POS, stroke=INK, sw=1.5))
    frby.append(text(710, 185, "x₁ = x₂", size=12, bold=True, color=POS))

    frby.append(text(710, 130, "Δ₂₁ = x₂ - x₁ = 0", size=11, bold=True, color=POS))

    # Сплющений об'єм
    frby.append(rect(510, 220, 280, 90, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frby.append(text(650, 245, "Колапс гіпероб'єму:", size=12, bold=True, color=INK))
    frby.append(text(650, 270, "det(V₃) = (x₁ - x₀)(x₂ - x₀) · 0 = 0", size=12, bold=True, color=POS))
    frby.append(text(650, 295, "Два однакові рядки в матриці!", size=11, color=MUTED))

    frby.append(text(650, 360, "✗ Матриця неортогональна / вироджена", size=12, bold=True, color=POS))
    frby.append(text(650, 385, "✗ Неможливо відновити коефіцієнти", size=11, color=MUTED))

    render(os.path.join(OUT, "vandermonde-geometric-collapse.svg"), W, H, *frby,
           title="Геометричне виродження визначника Вандермонда")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Двоетапний конвеєр алгоритму Бйорка — Перейри
# ─────────────────────────────────────────────────────────────────────────────
def fig_bjorck_pereyra_pipeline():
    W, H = 880, 460
    frby = []

    frby.append(text(W / 2, 28, "Конвеєр швидкого розв'язання систем Вандермонда (Бйорк — Перейра)", size=15, bold=True, color=INK))

    # Блок 1: Вхідні дані
    b1, _, _ = textbox(140, 110, "Вхідні дані:\nВузли: x = (x₀, x₁, ..., xₙ₋₁)\nЗначення: y = (y₀, y₁, ..., yₙ₋₁)", size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b1)

    # Блок 2: Етап 1 (Розділені різниці)
    b2, _, _ = textbox(470, 110, "Етап 1: Прямий хід (Базис Ньютона)\nОбчислення розділених різниць\nчерез розклад біодіагоналей L_k(x)\nСкладність: n(n - 1) / 2 операцій", size=12, pad=10, fill="#eff6ff", stroke=NEG, sw=1.5)
    frby.append(b2)

    frby.append(arrow(265, 110, 325, 110, color=INK, sw=1.8))

    # Блок 3: Проміжний стан (Ньютонівські коефіцієнти)
    b3, _, _ = textbox(470, 240, "Проміжний результат:\nКоефіцієнти полінома Ньютона d = (d₀, d₁, ..., dₙ₋₁)\nN(x) = ∑ d_k · ∏_{j=0}^{k-1} (x - x_j)", size=12, pad=10, fill="#fefce8", stroke="#ca8a04", sw=1.5)
    frby.append(b3)

    frby.append(arrow(470, 160, 470, 195, color=INK, sw=1.8))

    # Блок 4: Етап 2 (Перехід до мономіального базису)
    b4, _, _ = textbox(470, 370, "Етап 2: Зворотний хід (Базис мономів)\nПеретворення у форму c₀ + c₁x + ... + cₙ₋₁xⁿ⁻¹\nчерез зворотні множники U_k(x)\nСкладність: n(n - 1) / 2 операцій", size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b4)

    frby.append(arrow(470, 285, 470, 320, color=INK, sw=1.8))

    # Блок 5: Вихідні коефіцієнти
    b5, _, _ = textbox(770, 370, "Вихід:\nКоефіцієнти c = (c₀, ..., cₙ₋₁)\nПоліном P(x) = ∑ c_j · xʲ", size=12, pad=10, fill="#ffffff", stroke=LINE, sw=1.5)
    frby.append(b5)

    frby.append(arrow(625, 370, 680, 370, color=FIELD, sw=1.8))

    # Порівняльна плашка внизу зліва
    b_cmp, _, _ = textbox(170, 290, "Порівняння складності:\n\nМетод Гаусса:\nЧас: O(n³), Пам'ять: O(n²)\n\nБйорк — Перейра:\nЧас: 2n² + O(n), Пам'ять: O(n)", size=11, pad=10, fill="#f8fafc", stroke=LINE, sw=1.2)
    frby.append(b_cmp)

    render(os.path.join(OUT, "bjorck-pereyra-pipeline.svg"), W, H, *frby,
           title="Конвеєр алгоритму Бйорка — Перейри")


if __name__ == "__main__":
    fig_vandermonde_matrix_structure()
    fig_vandermonde_geometric_collapse()
    fig_bjorck_pereyra_pipeline()
    print("Всі фігури згенеровано успішно.")
