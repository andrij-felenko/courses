# -*- coding: utf-8 -*-
"""Фігури до статті «Онлайн-алгоритм Велфорда».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Усі тексти та розмітки сумісні з svgkit та svgcheck.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── Фігура 1: Катастрофічне скасування в наївній формулі проти стійкого кроку ────
def fig_catastrophic_cancellation():
    W, H = 880, 420
    parts = []

    # Верхній блок: Наївне сумування та катастрофічне скасування
    parts.append(rect(40, 50, 800, 155, fill="#fff5f5", stroke=POS, sw=1.8, rx=6))
    parts.append(text(440, 78, "Наївне однопрохідне обчислення: віднімання гігантських сум", size=15, bold=True, color=POS))
    
    parts.append(rect(70, 100, 320, 50, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    parts.append(text(230, 122, "Сума квадратів: S2 = ∑ x_i²", size=13, bold=True, color=INK))
    parts.append(text(230, 140, "≈ 10 000 000 000 000 000.12", size=11, color=MUTED))

    parts.append(text(410, 128, "−", size=22, bold=True, color=POS))

    parts.append(rect(430, 100, 320, 50, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    parts.append(text(590, 122, "Квадрат суми: S1² / n", size=13, bold=True, color=INK))
    parts.append(text(590, 140, "≈ 10 000 000 000 000 000.00", size=11, color=MUTED))

    parts.append(text(440, 185, "Різниця двох чисел порядку 10¹⁶ знищує молодші біти мантиси → дисперсія стає від'ємною або нульовою", size=12, color=POS, bold=True))

    # Нижній блок: Підхід Велфорда
    parts.append(rect(40, 230, 800, 160, fill="#f4faf6", stroke=FIELD, sw=1.8, rx=6))
    parts.append(text(440, 258, "Стійкий підхід Велфорда: накопичення локальних відхилень δ", size=15, bold=True, color=FIELD))

    parts.append(rect(70, 280, 210, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(175, 302, "Відхилення δ", size=13, bold=True, color=INK))
    parts.append(text(175, 322, "δ = x_k − μ_{k−1}", size=12, color=MUTED))

    parts.append(arrow(285, 306, 335, 306, color=FIELD, sw=1.5))

    parts.append(rect(340, 280, 210, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(445, 302, "Зсув середнього μ_k", size=13, bold=True, color=INK))
    parts.append(text(445, 322, "μ_k = μ_{k−1} + δ / k", size=12, color=MUTED))

    parts.append(arrow(555, 306, 605, 306, color=FIELD, sw=1.5))

    parts.append(rect(610, 280, 200, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(710, 302, "Накопичення M2", size=13, bold=True, color=INK))
    parts.append(text(710, 322, "M2_k = M2_{k−1} + δ·(x_k − μ_k)", size=12, color=MUTED))

    parts.append(text(440, 368, "Числа залишаються масштабу розсіювання (δ ≈ σ) — мантиса зберігає всі 53 біти точності", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "catastrophic-cancellation.svg"), W, H, *parts, title="Втрата точності в наївній формулі та числовий захист Велфорда")


# ── Фігура 2: Крок оновлення Велфорда ──────────────────────────────────────────
def fig_welford_step():
    W, H = 880, 360
    parts = []

    # Осі та числова шкала
    parts.append(line(80, 160, 800, 160, color=LINE, sw=2))
    parts.append(arrow(780, 160, 815, 160, color=LINE, sw=2))
    parts.append(text(810, 185, "Шкала значень x", size=12, color=MUTED, anchor="end"))

    # Попереднє середнє
    parts.append(circle(300, 160, 6, fill=NEG, stroke=LINE, sw=1.5))
    parts.append(line(300, 130, 300, 190, color=NEG, sw=1.5, dash="4,3"))
    parts.append(rect(220, 85, 160, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    parts.append(text(300, 110, "Попереднє середнє μ_{k−1}", size=12, bold=True, color=NEG))

    # Нова точка
    parts.append(circle(700, 160, 7, fill=POS, stroke=LINE, sw=1.5))
    parts.append(line(700, 130, 700, 190, color=POS, sw=1.5, dash="4,3"))
    parts.append(rect(630, 85, 140, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    parts.append(text(700, 110, "Нова точка x_k", size=12, bold=True, color=POS))

    # Інноваційне відхилення δ = x_k - μ_{k-1}
    parts.append(line(300, 210, 700, 210, color=MUTED, sw=1.5))
    parts.append(line(300, 205, 300, 215, color=MUTED, sw=1.5))
    parts.append(line(700, 205, 700, 215, color=MUTED, sw=1.5))
    parts.append(text(500, 232, "Попереднє відхилення: δ = x_k − μ_{k−1}", size=12, bold=True, color=MUTED))

    # Нове середнє
    parts.append(circle(380, 160, 6, fill=FIELD, stroke=LINE, sw=1.5))
    parts.append(line(380, 130, 380, 190, color=FIELD, sw=1.5, dash="4,3"))
    parts.append(rect(320, 265, 200, 45, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(420, 287, "Нове середнє μ_k", size=12, bold=True, color=FIELD))
    parts.append(text(420, 303, "μ_k = μ_{k−1} + δ / k", size=11, color=FIELD))

    # Зсув середнього
    parts.append(arrow(300, 140, 375, 140, color=FIELD, sw=1.8))
    parts.append(text(340, 132, "+ δ / k", size=11, bold=True, color=FIELD))

    # Нове відхилення δ_new = x_k - μ_k
    parts.append(line(380, 65, 700, 65, color=LINE, sw=1.2))
    parts.append(line(380, 60, 380, 70, color=LINE, sw=1.2))
    parts.append(line(700, 60, 700, 70, color=LINE, sw=1.2))
    parts.append(text(540, 55, "Нове відхилення: δ_new = x_k − μ_k", size=12, color=INK))

    render(os.path.join(IMG, "welford-step.svg"), W, H, *parts, title="Геометрія оновлення середнього та відхилень в алгоритмі Велфорда")


# ── Фігура 3: Паралельне об'єднання частин за Ченем ───────────────────────────
def fig_chan_parallel_merge():
    W, H = 880, 400
    parts = []

    # Рівень 0: Потоки A, B, C, D
    workers = [
        (80, 60, "Блок A", "n_A, μ_A, M2_A"),
        (280, 60, "Блок B", "n_B, μ_B, M2_B"),
        (480, 60, "Блок C", "n_C, μ_C, M2_C"),
        (680, 60, "Блок D", "n_D, μ_D, M2_D"),
    ]
    for x, y, title_w, stats_w in workers:
        parts.append(rect(x, y, 120, 55, fill="#f0f4f8", stroke=LINE, sw=1.4, rx=5))
        parts.append(text(x + 60, y + 22, title_w, size=13, bold=True, color=INK))
        parts.append(text(x + 60, y + 42, stats_w, size=11, color=MUTED))

    # Рівень 1: Проміжне злиття AB і CD
    merges_l1 = [
        (180, 180, "Злиття AB", "n_AB = n_A + n_B", "M2_AB = M2_A + M2_B + Δ²·(n_A·n_B / n_AB)"),
        (580, 180, "Злиття CD", "n_CD = n_C + n_D", "M2_CD = M2_C + M2_D + Δ²·(n_C·n_D / n_CD)"),
    ]
    # Стрілки L0 -> L1
    parts.append(arrow(140, 115, 210, 175, color=LINE, sw=1.5))
    parts.append(arrow(340, 115, 270, 175, color=LINE, sw=1.5))
    parts.append(arrow(540, 115, 610, 175, color=LINE, sw=1.5))
    parts.append(arrow(740, 115, 670, 175, color=LINE, sw=1.5))

    for x, y, title_m, n_formula, m2_formula in merges_l1:
        parts.append(rect(x, y, 200, 68, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
        parts.append(text(x + 100, y + 20, title_m, size=13, bold=True, color=NEG))
        parts.append(text(x + 100, y + 38, n_formula, size=11, color=INK))
        parts.append(text(x + 100, y + 56, m2_formula, size=9.5, color=MUTED))

    # Рівень 2: Фінальне злиття ABCD
    parts.append(arrow(280, 248, 400, 305, color=FIELD, sw=1.8))
    parts.append(arrow(680, 248, 480, 305, color=FIELD, sw=1.8))

    parts.append(rect(330, 305, 220, 75, fill="#f4faf6", stroke=FIELD, sw=2.0, rx=6))
    parts.append(text(440, 328, "Підсумкова статистика ABCD", size=13, bold=True, color=FIELD))
    parts.append(text(440, 348, "Дисперсія: s² = M2_total / (N − 1)", size=11.5, bold=True, color=INK))
    parts.append(text(440, 366, "Складність об'єднання: O(log P) паралельних кроків", size=10.5, color=MUTED))

    render(os.path.join(IMG, "chan-parallel-merge.svg"), W, H, *parts, title="Деревоподібна паралельна редукція статистик за формулами Чена")


# ── Фігура 4: Ієрархія оновлення статистичних моментів ────────────────────────
def fig_statistical_moments():
    W, H = 880, 340
    parts = []

    moments = [
        (40, 90, "n (Лічильник)", "Розмір вибірки", "n_k = n_{k−1} + 1", "#f0f4f8", LINE),
        (240, 90, "M1 (Середнє)", "Центр розподілу", "μ_k = μ_{k−1} + δ / k", "#eaf0fd", NEG),
        (450, 90, "M2 (Дисперсія)", "Розкид навколо μ", "M2 += δ · (x_k − μ_k)", "#f4faf6", FIELD),
        (660, 90, "M3, M4 (Форма)", "Асиметрія та ексцес", "Оновлення через δ² та δ³", "#fdf6ea", POS),
    ]

    for x, y, name, desc, formula, bg_col, stroke_col in moments:
        parts.append(rect(x, y, 180, 150, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        parts.append(text(x + 90, y + 28, name, size=13, bold=True, color=stroke_col))
        parts.append(text(x + 90, y + 50, desc, size=11, color=MUTED))
        parts.append(line(x + 15, y + 65, x + 165, y + 65, color=stroke_col, sw=1, dash="2,2"))
        parts.append(text(x + 90, y + 92, "Формула оновлення:", size=10.5, color=INK, bold=True))
        parts.append(text(x + 90, y + 115, formula, size=10, color=INK))

    # Стрілки залежностей між моментами
    parts.append(arrow(220, 165, 240, 165, color=LINE, sw=1.6))
    parts.append(arrow(420, 165, 450, 165, color=LINE, sw=1.6))
    parts.append(arrow(630, 165, 660, 165, color=LINE, sw=1.6))

    parts.append(text(440, 280, "Кожен вищий момент M_{m} залежить виключно від поточного значення x_k та нижчих моментів M_{<m}", size=12, color=INK, bold=True))
    parts.append(text(440, 305, "Потоковий розрахунок усіх 4 моментів за один прохід із пам'яттю O(1) і часом O(1) на точку", size=11, color=MUTED))

    render(os.path.join(IMG, "statistical-moments-pipeline.svg"), W, H, *parts, title="Каскад потокового оновлення центральних моментів вибірки")


if __name__ == "__main__":
    fig_catastrophic_cancellation()
    fig_welford_step()
    fig_chan_parallel_merge()
    fig_statistical_moments()
    print("All figures generated successfully.")
