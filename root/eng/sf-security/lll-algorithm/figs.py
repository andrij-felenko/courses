# -*- coding: utf-8 -*-
"""Фігури до статті «LLL-алгоритм редукції ґраток»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Порівняння «поганого» та «редукованого» базисів ґратки
# ─────────────────────────────────────────────────────────────────────────────
def fig_lattice_basis():
    W, H = 840, 420
    frby = []

    # Заголовок
    frby.append(text(W / 2, 28, "Геометрія ґратки: вироджений витягнутий базис проти LLL-редукованого", size=15, bold=True, color=INK))

    # Ліва панель: «Поганий» базис
    frby.append(rect(20, 55, 385, 345, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(212, 80, "Невигідний (витягнутий) базис", size=14, bold=True, color=POS))
    frby.append(text(212, 100, "Вектори довгі, кут між ними гострий (0.1 рад)", size=12, color=MUTED))

    # Сітка точок зліва (центр 212, 260)
    ox1, oy1 = 212, 270

    # Вузли ґратки
    for i in range(-2, 3):
        for j in range(-2, 3):
            px = ox1 + i * 55 + j * 20
            py = oy1 + i * (-10) + j * (-45)
            if 35 <= px <= 390 and 115 <= py <= 385:
                frby.append(circle(px, py, 2.5, fill="#94a3b8", stroke="#64748b", sw=1))

    # Початкова точка
    frby.append(circle(ox1, oy1, 4.5, fill=INK, stroke=INK, sw=1.5))
    frby.append(text(ox1 - 12, oy1 + 16, "0", size=12, bold=True, color=INK))

    # Вектори поганого базису
    bx1, by1 = ox1 + 110, oy1 - 20
    bx2, by2 = ox1 + 130, oy1 - 65
    frby.append(line(ox1, oy1, bx1, by1, color=POS, sw=2.5))
    frby.append(line(ox1, oy1, bx2, by2, color="#e67e22", sw=2.5))
    frby.append(circle(bx1, by1, 4, fill=POS, stroke=POS, sw=1))
    frby.append(circle(bx2, by2, 4, fill="#e67e22", stroke="#e67e22", sw=1))

    frby.append(text(bx1 + 16, by1 + 12, "b₁ (довгий)", size=12, bold=True, color=POS))
    frby.append(text(bx2 + 20, by2 - 4, "b₂ (майже паралельний)", size=12, bold=True, color="#e67e22"))

    # Підпис знизу панелі 1
    frby.append(rect(35, 335, 355, 50, fill="#fff1f2", stroke="#fecdd3", sw=1, rx=6))
    frby.append(text(212, 355, "Пошук найкоротшого вектора складний:", size=12, bold=True, color=POS))
    frby.append(text(212, 372, "комбінації z₁b₁ + z₂b₂ мають великі за модулем коефіцієнти", size=11, color=INK))

    # Права панель: LLL-редукований базис
    frby.append(rect(435, 55, 385, 345, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(627, 80, "LLL-редукований (короткий) базис", size=14, bold=True, color=FIELD))
    frby.append(text(627, 100, "Вектори короткі, майже ортогональні (кут ≈ 90°)", size=12, color=MUTED))

    # Сітка точок справа (та сама ґратка!)
    ox2, oy2 = 627, 270
    for i in range(-2, 3):
        for j in range(-2, 3):
            px = ox2 + i * 55 + j * 20
            py = oy2 + i * (-10) + j * (-45)
            if 450 <= px <= 805 and 115 <= py <= 385:
                frby.append(circle(px, py, 2.5, fill="#94a3b8", stroke="#64748b", sw=1))

    # Початкова точка
    frby.append(circle(ox2, oy2, 4.5, fill=INK, stroke=INK, sw=1.5))
    frby.append(text(ox2 - 12, oy2 + 16, "0", size=12, bold=True, color=INK))

    # Вектори LLL-базису: короткі кроки вздовж ґратки
    rx1, ry1 = ox2 + 55, oy2 - 10
    rx2, ry2 = ox2 + 20, oy2 - 45
    frby.append(line(ox2, oy2, rx1, ry1, color=FIELD, sw=2.5))
    frby.append(line(ox2, oy2, rx2, ry2, color=NEG, sw=2.5))
    frby.append(circle(rx1, ry1, 4, fill=FIELD, stroke=FIELD, sw=1))
    frby.append(circle(rx2, ry2, 4, fill=NEG, stroke=NEG, sw=1))

    frby.append(text(rx1 + 18, ry1 + 12, "v₁ (короткий)", size=12, bold=True, color=FIELD))
    frby.append(text(rx2 - 22, ry2 - 10, "v₂ (майже ортогональний)", size=12, bold=True, color=NEG))

    # Підпис знизу панелі 2
    frby.append(rect(450, 335, 355, 50, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=6))
    frby.append(text(627, 355, "Оптимальна геометрія для обчислень:", size=12, bold=True, color=FIELD))
    frby.append(text(627, 372, "‖v₁‖ наближає найкоротший ненульовий вектор ґратки λ₁(Λ)", size=11, color=INK))

    render(os.path.join(OUT, "lll-lattice-basis.svg"), W, H, *frby)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Геометрія умови Ловаса та розмірного редукування
# ─────────────────────────────────────────────────────────────────────────────
def fig_gram_schmidt_step():
    W, H = 840, 440
    frby = []

    frby.append(text(W / 2, 28, "Геометричний зміст розмірного редукування та умови Ловаса", size=15, bold=True, color=INK))

    # Ліва частина: Розмірне редукування (проекція μ)
    frby.append(rect(20, 55, 385, 365, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(212, 80, "1. Розмірне редукування (Size Reduction)", size=13, bold=True, color=NEG))
    frby.append(text(212, 100, "|μ_{k,j}| ≤ 1/2 шляхом віднімання q · b_j", size=12, color=MUTED))

    # Графічна ілюстрація розмірної редукції
    ax0, ay0 = 60, 240
    ax1, ay1 = 360, 240
    frby.append(line(ax0, ay0, ax1, ay1, color="#94a3b8", sw=1.5, dash="4,4"))
    frby.append(text(340, 258, "напрямок b*ₖ₋₁", size=11, color=MUTED))

    # Початок
    frby.append(circle(100, ay0, 4, fill=INK, stroke=INK))
    frby.append(text(90, ay0 + 18, "0", size=12, bold=True, color=INK))

    # Вектор b_{k-1}* на осі
    frby.append(line(100, ay0, 240, ay0, color=NEG, sw=2.5))
    frby.append(circle(240, ay0, 3.5, fill=NEG, stroke=NEG))
    frby.append(text(170, ay0 + 18, "b*ₖ₋₁", size=12, bold=True, color=NEG))

    # Початковий вектор b_k (довгий нахилений)
    frby.append(line(100, ay0, 310, 140, color=POS, sw=2))
    frby.append(circle(310, 140, 3.5, fill=POS, stroke=POS))
    frby.append(text(315, 130, "bₖ (до редукції)", size=11, bold=True, color=POS))

    # Проекція μ b_{k-1}* = 1.5 b_{k-1}*
    frby.append(line(310, 140, 310, ay0, color=POS, sw=1.2, dash="3,3"))
    frby.append(text(310, ay0 + 18, "μ = 1.5", size=11, color=POS))

    # Віднімання 1 · b_{k-1}
    frby.append(arrow(310, 140, 170, 140, color=FIELD, sw=2))
    frby.append(text(240, 130, "− ⌊1.5⌉ · bₖ₋₁", size=11, bold=True, color=FIELD))

    # Новий вектор b_k'
    frby.append(line(100, ay0, 170, 140, color=FIELD, sw=2.5))
    frby.append(circle(170, 140, 3.5, fill=FIELD, stroke=FIELD))
    frby.append(text(160, 122, "bₖ (редукований)", size=11, bold=True, color=FIELD))
    frby.append(line(170, 140, 170, ay0, color=FIELD, sw=1.2, dash="3,3"))
    frby.append(text(170, ay0 + 36, "новий |μ| = 0.5 ≤ 1/2", size=11, bold=True, color=FIELD))

    # Пояснення знизу зліва
    frby.append(rect(35, 335, 355, 70, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frby.append(text(212, 355, "Зсув вздовж дискретної прямої:", size=12, bold=True, color=INK))
    frby.append(text(212, 372, "bₖ ← bₖ − ⌊μ_{k,j}⌉ · bⱼ", size=12, bold=True, color=NEG))
    frby.append(text(212, 390, "Коефіцієнт проекції гарантовано потрапляє в [−1/2, 1/2]", size=11, color=MUTED))

    # Права частина: Умова Ловаса (Lovasz Condition)
    frby.append(rect(435, 55, 385, 365, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(627, 80, "2. Умова Ловаса (Lovász Condition)", size=13, bold=True, color="#d97706"))
    frby.append(text(627, 100, "δ ‖b*ₖ₋₁‖² ≤ ‖b*ₖ + μ b*ₖ₋₁‖²  (для δ = 3/4)", size=12, color=MUTED))

    # Схема ортогональних компонент
    bx0, by0 = 490, 260
    frby.append(line(bx0, by0, bx0 + 280, by0, color="#94a3b8", sw=1.5, dash="4,4"))
    frby.append(line(bx0, by0, bx0, by0 - 150, color="#94a3b8", sw=1.5, dash="4,4"))

    frby.append(circle(bx0, by0, 4, fill=INK, stroke=INK))

    # b_{k-1}* вздовж осі X
    frby.append(line(bx0, by0, bx0 + 160, by0, color=NEG, sw=2.5))
    frby.append(text(bx0 + 80, by0 + 18, "‖b*ₖ₋₁‖", size=12, bold=True, color=NEG))

    # μ b_{k-1}*
    frby.append(line(bx0, by0, bx0 + 60, by0, color=FIELD, sw=2))
    frby.append(text(bx0 + 35, by0 - 8, "μ b*ₖ₋₁", size=10, color=FIELD))

    # b_k* по осі Y
    frby.append(line(bx0 + 60, by0, bx0 + 60, by0 - 100, color=POS, sw=2.5))
    frby.append(text(bx0 + 100, by0 - 55, "‖b*ₖ‖", size=12, bold=True, color=POS))

    # Гіпотенуза
    frby.append(line(bx0, by0, bx0 + 60, by0 - 100, color="#d97706", sw=2.5))
    frby.append(text(bx0 + 15, by0 - 110, "‖b*ₖ + μ b*ₖ₋₁‖", size=11, bold=True, color="#d97706"))

    # Пояснення знизу справа
    frby.append(rect(450, 335, 355, 70, fill="#fefce8", stroke="#fef08a", sw=1, rx=6))
    frby.append(text(627, 353, "Критерій обміну (Swap):", size=12, bold=True, color="#d97706"))
    frby.append(text(627, 370, "Якщо b*ₖ надто малий: ‖b*ₖ‖² < (δ − μ²) ‖b*ₖ₋₁‖²", size=11, bold=True, color=POS))
    frby.append(text(627, 388, "→ Обмін bₖ ↔ bₖ₋₁ та крок назад k ← max(k−1, 2)", size=11, color=INK))

    render(os.path.join(OUT, "lll-gram-schmidt-step.svg"), W, H, *frby)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Повний блок-схема конвеєра LLL-алгоритму
# ─────────────────────────────────────────────────────────────────────────────
def fig_flowchart():
    W, H = 840, 520
    frby = []

    frby.append(text(W / 2, 28, "Блок-схема алгоритму Ленстри — Ленстри — Ловаса (LLL)", size=15, bold=True, color=INK))

    # Блок 1: Вхід
    b1, w1, h1 = textbox(420, 70, "Вхід: базис b₁, b₂, ..., bₙ ∈ ℤᵐ, параметр δ ∈ (1/4, 1]\nОбчислення Грама — Шмідта b*₁, ..., b*ₙ та μ_{i,j}\nІніціалізація індексу: k = 2", size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b1)

    # Стрілка 1 -> 2
    frby.append(arrow(420, 105, 420, 135, color=INK, sw=1.8))

    # Блок 2: Розмірне редукування для k, k-1
    b2, w2, h2 = textbox(420, 165, "1. Розмірне редукування пари (k, k−1)\nq = ⌊μ_{k, k−1}⌉;   bₖ ← bₖ − q · bₖ₋₁\nОновлення коефіцієнтів μ_{k, j} для j < k", size=12, pad=10, fill="#eff6ff", stroke=NEG, sw=1.5)
    frby.append(b2)

    # Стрілка 2 -> 3
    frby.append(arrow(420, 200, 420, 235, color=INK, sw=1.8))

    # Блок 3: Перевірка умови Ловаса
    b3, w3, h3 = textbox(420, 265, "2. Перевірка умови Ловаса:\n‖b*ₖ‖² ≥ (δ − μ_{k, k−1}²) · ‖b*ₖ₋₁‖² ?", size=12, pad=10, fill="#fefce8", stroke="#ca8a04", sw=1.5, bold=True)
    frby.append(b3)

    # Ліва гілка: НІ (вихід з лівого краю b3)
    left_edge = 420 - w3 / 2
    frby.append(arrow(left_edge, 265, 140, 265, color=POS, sw=2))
    frby.append(text((left_edge + 140) / 2, 252, "НІ", size=12, bold=True, color=POS))

    b_swap, ws, hs = textbox(140, 350, "Обмін bₖ ↔ bₖ₋₁\nПерерахунок b*ₖ₋₁, b*ₖ та μ\nk ← max(k − 1, 2)", size=12, pad=10, fill="#fef2f2", stroke=POS, sw=1.5)
    frby.append(b_swap)

    frby.append(arrow(140, 265, 140, 310, color=POS, sw=1.8))
    # Повернення з обміну назад на крок 1 по лівому контуру
    frby.append(line(140, 395, 140, 435, color=POS, sw=1.5))
    frby.append(line(140, 435, 25, 435, color=POS, sw=1.5))
    frby.append(line(25, 435, 25, 165, color=POS, sw=1.5))
    frby.append(arrow(25, 165, 420 - w2 / 2, 165, color=POS, sw=1.8))

    # Права гілка: ТАК (вихід з правого краю b3)
    right_edge = 420 + w3 / 2
    frby.append(arrow(right_edge, 265, 680, 265, color=FIELD, sw=2))
    frby.append(text((right_edge + 680) / 2, 252, "ТАК", size=12, bold=True, color=FIELD))

    b_ok, wok, hok = textbox(680, 350, "Повне розмірне редукування:\nдля j = k−2 спадаючи до 1:\n  bₖ ← bₖ − ⌊μ_{k,j}⌉ · bⱼ\nКрок уперед: k ← k + 1", size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b_ok)

    frby.append(arrow(680, 265, 680, 310, color=FIELD, sw=1.8))

    # Умова завершення k > n
    frby.append(arrow(680, 395, 680, 430, color=INK, sw=1.8))

    b_end, we, he = textbox(680, 465, "k > n ?\nТАК → Кінець (базис LLL-редукований)\nНІ → Повернутися на крок 1", size=12, pad=8, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b_end)

    # Зворотний зв'язок якщо k <= n по правому контуру
    frby.append(line(680 + we / 2, 465, 815, 465, color=FIELD, sw=1.5))
    frby.append(line(815, 465, 815, 165, color=FIELD, sw=1.5))
    frby.append(arrow(815, 165, 420 + w2 / 2, 165, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "lll-flowchart.svg"), W, H, *frby)

    render(os.path.join(OUT, "lll-flowchart.svg"), W, H, *frby)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Зведення задачі рюкзака (Subset Sum) до пошуку вектора в ґратці
# ─────────────────────────────────────────────────────────────────────────────
def fig_knapsack_lattice():
    W, H = 840, 430
    frby = []

    frby.append(text(W / 2, 28, "Криптоаналіз рюкзака: зведення задачі Subset Sum до редукції ґратки", size=15, bold=True, color=INK))

    # Лівий блок: Формулювання задачі
    frby.append(rect(20, 55, 360, 355, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(200, 80, "Задача рюкзака (Subset Sum)", size=13, bold=True, color=POS))
    frby.append(text(200, 100, "Знайти біти xᵢ ∈ {0, 1} такі, що ∑ xᵢ aᵢ = S", size=12, color=MUTED))

    # Формула
    b_eq, weq, heq = textbox(200, 160, "Відкритий ключ (ваги):\na = (a₁, a₂, ..., aₙ)\nШифротекст (сума):\nS = x₁ a₁ + x₂ a₂ + ... + xₙ aₙ", size=12, pad=10, fill="#fff1f2", stroke=POS, sw=1.2)
    frby.append(b_eq)

    frby.append(rect(35, 235, 330, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frby.append(text(200, 255, "Чому прямий перебір не працює:", size=12, bold=True, color=INK))
    frby.append(text(200, 275, "Кількість комбінацій: 2ⁿ варіантів.", size=11, color=MUTED))
    frby.append(text(200, 295, "Для n = 100 це 2¹⁰⁰ ≈ 1.26 · 10³⁰ дій.", size=11, color=POS))
    frby.append(text(200, 325, "Ідея Клоса — Одляжка — Шнорра:", size=12, bold=True, color=FIELD))
    frby.append(text(200, 345, "Вектор розв'язку x = (x₁, ..., xₙ, 0) є", size=11, color=INK))
    frby.append(text(200, 365, "аномально коротким вектором у ґратці!", size=11, bold=True, color=FIELD))

    # Стрілка між блоками
    frby.append(arrow(385, 230, 425, 230, color=INK, sw=2))
    frby.append(text(405, 218, "зведення", size=11, bold=True, color=FIELD))

    # Правий блок: Матриця ґратки (n+1) x (n+1)
    frby.append(rect(435, 55, 385, 355, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(627, 80, "Базисна матриця ґратки B (n+1) × (n+1)", size=13, bold=True, color=NEG))
    frby.append(text(627, 100, "Кожен рядок — це вектор базису bᵢ", size=12, color=MUTED))

    # Відображення структури матриці
    frby.append(rect(455, 125, 345, 175, fill="#f0f9ff", stroke="#bae6fd", sw=1.5, rx=6))

    # Одинична діагональ
    frby.append(text(505, 155, "1   0  ...  0", size=12, bold=True, color=NEG))
    frby.append(text(505, 185, "0   1  ...  0", size=12, bold=True, color=NEG))
    frby.append(text(505, 215, "... ... ... ...", size=12, color=MUTED))
    frby.append(text(505, 245, "0   0  ...  1", size=12, bold=True, color=NEG))
    frby.append(text(505, 275, "1/2 1/2 ... 1/2", size=12, bold=True, color="#d97706"))

    # Останній стовпчик (ваги та цільова сума S)
    frby.append(line(575, 135, 575, 290, color="#0284c7", sw=1.5))
    frby.append(text(675, 155, "N · a₁", size=12, bold=True, color=POS))
    frby.append(text(675, 185, "N · a₂", size=12, bold=True, color=POS))
    frby.append(text(675, 215, "...", size=12, color=MUTED))
    frby.append(text(675, 245, "N · aₙ", size=12, bold=True, color=POS))
    frby.append(text(675, 275, "N · S", size=12, bold=True, color=POS))

    # Результат після LLL
    frby.append(rect(455, 315, 345, 80, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=6))
    frby.append(text(627, 335, "Результат роботи LLL-алгоритму:", size=12, bold=True, color=FIELD))
    frby.append(text(627, 355, "Короткий вектор: v = (±1/2, ±1/2, ..., ±1/2, 0)", size=11, bold=True, color=INK))
    frby.append(text(627, 375, "Координати v безпосередньо розкривають біти xᵢ!", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "lll-crypto-knapsack.svg"), W, H, *frby)


if __name__ == "__main__":
    fig_lattice_basis()
    fig_gram_schmidt_step()
    fig_flowchart()
    fig_knapsack_lattice()
    print("Всі фігури згенеровано успішно.")
