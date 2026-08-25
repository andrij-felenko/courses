# -*- coding: utf-8 -*-
"""Фігури до статті «Індекс Жаккара».
Генерує SVG-діаграми у теці img/:
1. jaccard-venn.svg — Схема перетину та об'єднання множин для індексу Жаккара.
2. size-filtering.svg — Розмірне вікно та префіксний фільтр для кандидатури.
3. minhash-concept.svg — Принцип роботи сигнатур MinHash для оцінки Жаккара.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. jaccard-venn.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_venn():
    path = os.path.join(OUT, "jaccard-venn.svg")
    W, H = 840, 420
    p = []

    p.append(text(W / 2, 32, "Геометричний зміст індексу Жаккара J(A, B)", size=18, bold=True, color=INK))

    # Left box: Venn diagram
    p.append(rect(30, 60, 375, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(217, 90, "Діаграма Венна множин A та B", size=15, bold=True, color=INK))

    # Circles for Set A and Set B
    p.append('<circle cx="175.0" cy="220.0" r="90.0" fill="#2457d6" fill-opacity="0.25" stroke="#2457d6" stroke-width="2.5"/>')
    p.append('<circle cx="260.0" cy="220.0" r="90.0" fill="#27ae60" fill-opacity="0.25" stroke="#27ae60" stroke-width="2.5"/>')

    # Labels inside circles
    p.append(text(130, 220, "A \\ B", size=16, bold=True, color="#1e40af"))
    p.append(text(217, 220, "A ∩ B", size=16, bold=True, color="#15803d"))
    p.append(text(305, 220, "B \\ A", size=16, bold=True, color="#166534"))

    p.append(text(130, 115, "Множина A", size=14, bold=True, color="#2457d6"))
    p.append(text(305, 115, "Множина B", size=14, bold=True, color="#27ae60"))

    # Right box: Mathematical definitions
    p.append(rect(435, 60, 375, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(622, 90, "Формули метрики", size=15, bold=True, color=INK))

    # Intersection box
    p.append(rect(460, 120, 325, 70, fill="#eafaf0", stroke="#27ae60", sw=1.8, rx=6))
    p.append(text(622, 148, "Перетин |A ∩ B|", size=14, bold=True, color="#15803d"))
    p.append(text(622, 172, "Спільні елементи обох множин", size=12, color=MUTED))

    # Union box
    p.append(rect(460, 205, 325, 70, fill="#eef6ff", stroke="#2457d6", sw=1.8, rx=6))
    p.append(text(622, 233, "Об'єднання |A ∪ B| = |A| + |B| - |A ∩ B|", size=14, bold=True, color="#1e40af"))
    p.append(text(622, 257, "Усі унікальні елементи разом", size=12, color=MUTED))

    # Ratio box
    p.append(rect(460, 290, 325, 80, fill="#fdf2f2", stroke=POS, sw=2.0, rx=6))
    p.append(text(622, 318, "J(A, B) = |A ∩ B| / |A ∪ B|", size=16, bold=True, color=POS))
    p.append(text(622, 350, "Відстань Жаккара: d_J(A, B) = 1 - J(A, B)", size=13, bold=True, color=INK))

    render(path, W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 2. size-filtering.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_size_filtering():
    path = os.path.join(OUT, "size-filtering.svg")
    W, H = 840, 400
    p = []

    p.append(text(W / 2, 30, "Розмірний фільтр схожості Жаккара з порогом τ", size=18, bold=True, color=INK))

    # Main axis line
    p.append(rect(30, 60, 780, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Axis text
    p.append(text(420, 95, "Ось розмірів кандидатів |B| для опитувальної множини |A|", size=14, bold=True, color=INK))

    # Horizontal spectrum bar
    p.append(rect(60, 160, 720, 40, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=4))

    # Active window highlight
    p.append(rect(60, 160, 180, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=0))
    p.append(text(150, 185, "Відсіювання (|B| < τ·|A|)", size=11, bold=True, color=POS))

    p.append(rect(240, 160, 360, 40, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=0))
    p.append(text(420, 185, "Допустиме вікно [ τ·|A| ,  |A| / τ ]", size=13, bold=True, color="#15803d"))

    p.append(rect(600, 160, 180, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=0))
    p.append(text(690, 185, "Відсіювання (|B| > |A|/τ)", size=11, bold=True, color=POS))

    # Vertical markers above/below bar to avoid crossing text inside the bar
    p.append(line(240, 138, 240, 158, color=FIELD, sw=2.5))
    p.append(line(240, 202, 240, 222, color=FIELD, sw=2.5))
    p.append(text(240, 128, "Ніжня межа: τ·|A|", size=12, bold=True, color=FIELD))

    p.append(line(420, 138, 420, 158, color=INK, sw=2.5, dash="3,3"))
    p.append(line(420, 202, 420, 222, color=INK, sw=2.5, dash="3,3"))
    p.append(text(420, 128, "Опитувальна |A|", size=12, bold=True, color=INK))

    p.append(line(600, 138, 600, 158, color=FIELD, sw=2.5))
    p.append(line(600, 202, 600, 222, color=FIELD, sw=2.5))
    p.append(text(600, 128, "Верхня межа: |A| / τ", size=12, bold=True, color=FIELD))

    # Explanatory cards below
    p.append(rect(60, 245, 340, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(230, 268, "Математична необхідність", size=14, bold=True, color=INK))
    p.append(mtext(230, 293, "Якщо |B| поза межами, то навіть при\nповній перекритності J(A, B) < τ.\nПеревірка за O(1) відсіює > 90% пар.", size=12, color=MUTED))

    p.append(rect(440, 245, 340, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(610, 268, "Префіксний фільтр", size=14, bold=True, color=INK))
    p.append(mtext(610, 293, "Для відсортованої множини A достатньо\nперевірити перші (|A| - ⌈τ·|A|⌉ + 1)\nелементів в інвертованому індексі.", size=12, color=MUTED))

    render(path, W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 3. minhash-concept.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_minhash_concept():
    path = os.path.join(OUT, "minhash-concept.svg")
    W, H = 840, 420
    p = []

    p.append(text(W / 2, 30, "Принцип оцінювання схожості Жаккара через MinHash", size=18, bold=True, color=INK))

    p.append(rect(30, 60, 780, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Input sets box
    p.append(rect(60, 90, 220, 130, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(170, 115, "Вихідні множини", size=14, bold=True, color=INK))
    p.append(mtext(170, 145, "Множина A = {s₁, s₃, s₅, s₇}\nМножина B = {s₁, s₃, s₆, s₈}\n\nТочний J(A, B) = 2 / 6 = 0.333", size=12, color=MUTED))

    # MinHash signatures box
    p.append(rect(310, 90, 220, 130, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(420, 115, "MinHash Сигнатури (K=4)", size=14, bold=True, color=INK))
    p.append(mtext(420, 145, "Sig(A) = [h₁(A), h₂(A), h₃(A), h₄(A)]\nSig(B) = [h₁(B), h₂(B), h₃(B), h₄(B)]\n\nКомпактний вектор k хешів", size=12, color=MUTED))

    # Arrow 1
    p.append(arrow(280, 155, 310, 155, color=INK, sw=2.0))

    # Estimation box
    p.append(rect(560, 90, 220, 130, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(670, 115, "Оцінка схожості", size=14, bold=True, color="#15803d"))
    p.append(mtext(670, 145, "P(h_k(A) == h_k(B)) = J(A, B)\n\nJ_approx = (Збіги в Sig) / K\nОцінка за O(K) операцій", size=12, color=INK))

    # Arrow 2
    p.append(arrow(530, 155, 560, 155, color=INK, sw=2.0))

    # Bottom workflow detail
    p.append(rect(60, 240, 720, 120, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(420, 265, "Механізм перестановки та мінімального значення", size=14, bold=True, color=INK))

    # 3 step sub-boxes
    p.append(rect(80, 280, 210, 65, fill="#eef6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(185, 302, "1. Хешування елементів", size=13, bold=True, color=NEG))
    p.append(text(185, 325, "h_k(x) = (a·x + b) mod p", size=11, color=MUTED))

    p.append(rect(315, 280, 210, 65, fill="#eef6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(420, 302, "2. Пошук мінімуму", size=13, bold=True, color=NEG))
    p.append(text(420, 325, "h_k(A) = min_{x ∈ A} h_k(x)", size=11, color=MUTED))

    p.append(rect(550, 280, 210, 65, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(655, 302, "3. Порівняння сигнатур", size=13, bold=True, color="#15803d"))
    p.append(text(655, 325, "Поелементний збіг цілих чисел", size=11, color=MUTED))

    render(path, W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_venn()
    fig_size_filtering()
    fig_minhash_concept()
    print("Всі 3 фігури успішно згенеровано у", OUT)
