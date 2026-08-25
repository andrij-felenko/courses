# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми Reservoir Sampling."""

import sys
import os

# 4 рівні вгору до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def draw_reservoir_mechanism():
    """Фігура 1: Потокова обробка та ймовірнісний механізм заміни слота в Алгоритмі R."""
    w, h = 820, 360
    frags = []

    # Фон секцій
    frags.append(rect(15, 45, 230, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(265, 45, 260, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(545, 45, 260, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовки блоків
    frags.append(text(130, 70, "Вхідний потік даних", size=15, bold=True, color=INK))
    frags.append(text(395, 70, "Рішення на кроці n+1", size=15, bold=True, color=INK))
    frags.append(text(675, 70, "Резервуар (розмір k=3)", size=15, bold=True, color=INK))

    # Вхідні елементи
    stream_items = [
        ("x[1] ... x[n]", 130, 115, "#e2e8f0", INK),
        ("Новий елемент x[n+1]", 130, 175, "#dbeafe", NEG),
        ("Наступні x[n+2] ...", 130, 235, "#f1f5f9", MUTED)
    ]
    for label, cx, cy, fill_c, text_c in stream_items:
        b, _, _ = textbox(cx, cy, label, size=13, pad=8, fill=fill_c, stroke=LINE, color=text_c, bold=True, min_w=190)
        frags.append(b)

    frags.append(text(130, 305, "Повна довжина N невідома", size=11, italic=True, color=MUTED))

    # Стрілка від нового елемента до центру прийняття рішень
    frags.append(arrow(225, 175, 280, 175, color=LINE, sw=2))

    # Генератор випадкового індексу
    b_rng, _, _ = textbox(395, 120, "Генерація індексу:\nj = RandInt(1, n+1)", size=12, pad=6, fill="#ffffff", stroke=LINE, color=INK, min_w=200)
    frags.append(b_rng)

    # Стрілка вниз до розгалуження
    frags.append(line(395, 148, 395, 175, color=LINE, sw=1.5))
    frags.append(line(330, 175, 460, 175, color=LINE, sw=1.5))

    # Гілка 1: j <= k (Заміна)
    frags.append(arrow(460, 175, 460, 205, color=FIELD, sw=1.5))
    b_accept, _, _ = textbox(460, 240, "j ≤ k\nШанс: k/(n+1)\nЗапис у R[j-1]", size=11, pad=6, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True, min_w=105)
    frags.append(b_accept)

    # Гілка 2: j > k (Відкидання)
    frags.append(arrow(330, 175, 330, 205, color=POS, sw=1.5))
    b_reject, _, _ = textbox(330, 240, "j > k\nШанс: 1 - k/(n+1)\nПропуск", size=11, pad=6, fill="#fee2e2", stroke=POS, color=POS, bold=True, min_w=105)
    frags.append(b_reject)

    frags.append(text(395, 310, "Збереження: P = n/(n+1)", size=11, color=INK))

    # Стрілка від заміни до резервуара
    frags.append(arrow(515, 240, 560, 210, color=FIELD, sw=2))

    # Слоти резервуара
    slots = [
        ("Слот R[0]: x[17]", 675, 125, "#ffffff"),
        ("Слот R[1]: x[n+1] (замінено)", 675, 185, "#dcfce7"),
        ("Слот R[2]: x[42]", 675, 245, "#ffffff")
    ]
    for label, cx, cy, fill_c in slots:
        b, _, _ = textbox(cx, cy, label, size=12, pad=8, fill=fill_c, stroke=LINE, color=INK, bold=True, min_w=220)
        frags.append(b)

    frags.append(text(675, 310, "Для кожного: P(в резервуарі) = k/(n+1)", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-reservoir-mechanism.svg"), w, h, *frags, title="Механізм заміни слота в алгоритмі вибірки з резервуара (Algorithm R)")


def draw_skip_algorithms():
    """Фігура 2: Порівняння алгоритму R (поелементна перевірка) та алгоритму L (стрибки через геометричний розподіл)."""
    w, h = 820, 370
    frags = []

    # Верхня панель: Algorithm R
    frags.append(rect(15, 45, 790, 140, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(35, 70, "Algorithm R: O(N) викликів генератора випадкових чисел", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(35, 90, "Для кожного з N елементів викликається RandInt(1, i). Понад 99.9% перевірок закінчуються відкиданням.", size=11, color=MUTED, anchor="start"))

    # Вісь елементів для R
    frags.append(line(45, 140, 775, 140, color=LINE, sw=2))
    r_points = [
        (80, "x[101]\nRNG", POS),
        (160, "x[102]\nRNG", POS),
        (240, "x[103]\nRNG", POS),
        (320, "x[104]\nRNG", POS),
        (400, "x[105]\nRNG", POS),
        (480, "x[106]\nRNG", POS),
        (560, "x[107]\nRNG", POS),
        (640, "x[108]\nRNG", POS),
        (720, "x[109]\nRNG", POS),
    ]
    for px, lbl, col in r_points:
        frags.append(circle(px, 140, 4, fill=col, stroke=col))
        lines = lbl.split("\n")
        frags.append(text(px, 120, lines[0], size=10, color=INK))
        frags.append(text(px, 160, lines[1], size=10, bold=True, color=col))

    # Нижня панель: Algorithm L
    frags.append(rect(15, 205, 790, 150, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(35, 230, "Algorithm L (Vitter): O(k · log(N/k)) викликів генератора через довжину стрибка S", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(35, 250, "Обчислюється випадкова кількість елементів S для пропуску: S = ⌊ln(U) / ln(1 - W)⌋. Елементи всередині інтервалу ігноруються.", size=11, color=MUTED, anchor="start"))

    # Вісь елементів для L
    frags.append(line(45, 305, 775, 305, color=LINE, sw=2))

    # Початкова точка
    frags.append(circle(80, 305, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(80, 285, "x[100]", size=11, bold=True, color=INK))
    frags.append(text(80, 325, "Вставка", size=10, bold=True, color=FIELD))

    # Дуга стрибка 1 (S1 = 145)
    frags.append(text(250, 275, "Пропуск S1 = 145 елементів (без звернення до RNG)", size=11, bold=True, color=NEG))
    frags.append(line(85, 300, 415, 300, color=NEG, sw=2, dash="4,3"))
    frags.append(arrow(85, 300, 420, 300, color=NEG, sw=2))

    frags.append(circle(420, 305, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(420, 285, "x[246]", size=11, bold=True, color=INK))
    frags.append(text(420, 325, "Вставка R", size=10, bold=True, color=FIELD))

    # Дуга стрибка 2 (S2 = 320)
    frags.append(text(580, 275, "Пропуск S2 = 320 елементів", size=11, bold=True, color=NEG))
    frags.append(line(425, 300, 725, 300, color=NEG, sw=2, dash="4,3"))
    frags.append(arrow(425, 300, 730, 300, color=NEG, sw=2))

    frags.append(circle(730, 305, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(730, 285, "x[567]", size=11, bold=True, color=INK))
    frags.append(text(730, 325, "Вставка R", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-skip-algorithms.svg"), w, h, *frags, title="Оптимізація часу: послідовна обробка в Algorithm R проти геометричних стрибків в Algorithm L")


def draw_weighted_sampling():
    """Фігура 3: Зважена вибірка A-Res з пріоритетною чергою (мін-купою)."""
    w, h = 820, 360
    frags = []

    # Ліва секція: Генерація ключів
    frags.append(rect(15, 45, 360, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(195, 70, "1. Потік із вагами (A-Res / A-ExpJ)", size=15, bold=True, color=INK))

    items = [
        ("Елемент e[1]: вага w[1]=10", "Ключ r[1] = -ln(u[1]) / 10 = 0.042", "#ffffff"),
        ("Елемент e[2]: вага w[2]=2",  "Ключ r[2] = -ln(u[2]) / 2  = 0.693", "#ffffff"),
        ("Новий e[i]: вага w[i]=50",  "Ключ r[i] = -ln(u[i]) / 50 = 0.015", "#dbeafe"),
    ]
    for idx, (t1, t2, col) in enumerate(items):
        cy = 115 + idx * 65
        box, _, _ = textbox(195, cy, f"{t1}\n{t2}", size=11, pad=6, fill=col, stroke=LINE, min_w=325)
        frags.append(box)

    frags.append(text(195, 315, "u ~ Uniform(0, 1), більша вага → менший r[i]", size=11, italic=True, color=MUTED))

    # Стрілка між секціями
    frags.append(arrow(380, 190, 435, 190, color=LINE, sw=2))
    frags.append(text(407, 175, "r[i]", size=12, bold=True, color=NEG))

    # Права секція: Мін-купа (резервуар)
    frags.append(rect(445, 45, 360, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(625, 70, "2. Резервуар як мін-купа (розмір k=3)", size=15, bold=True, color=INK))

    # Вузли купи
    b_root, _, _ = textbox(625, 120, "Корінь (мінімум): r = 0.693 (e[2])\nНайгірший кандидат у вибірці", size=11, pad=6, fill="#fee2e2", stroke=POS, color=POS, bold=True, min_w=280)
    frags.append(b_root)

    frags.append(line(580, 145, 535, 185, color=LINE, sw=1.5))
    frags.append(line(670, 145, 715, 185, color=LINE, sw=1.5))

    b_l, _, _ = textbox(520, 215, "r = 0.150\n(елемент e[7])", size=11, pad=6, fill="#ffffff", stroke=LINE, min_w=125)
    b_r, _, _ = textbox(730, 215, "r = 0.042\n(елемент e[1])", size=11, pad=6, fill="#ffffff", stroke=LINE, min_w=125)
    frags.append(b_l)
    frags.append(b_r)

    # Правило заміни
    b_rule, _, _ = textbox(625, 295, "Якщо r[новий] < r[корінь]:\nВидалити корінь, вставити новий за O(log k)", size=11, pad=6, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True, min_w=310)
    frags.append(b_rule)

    render(os.path.join(IMG_DIR, "fig-weighted-sampling.svg"), w, h, *frags, title="Зважена вибірка з резервуара: метод випадкових ключів та мін-купа")


if __name__ == '__main__':
    draw_reservoir_mechanism()
    draw_skip_algorithms()
    draw_weighted_sampling()
    print("All figures successfully generated in img/")
