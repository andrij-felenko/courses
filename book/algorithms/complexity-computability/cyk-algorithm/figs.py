# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Алгоритм Кока–Янгера–Касамі (CYK)'."""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_cyk_table_pyramid():
    """Піраміда динамічного програмування алгоритму CYK: розбиття підрядків."""
    w, h = 820, 520
    frags = []

    # Заголовок зверху
    frags.append(text(410, 30, "Таблиця розбору CYK: динамічне об'єднання підрядків", size=18, bold=True))

    # Схема піраміди для рядка w = "b a b a" (довжина n = 4)
    symbols = ['w[1] = "b"', 'w[2] = "a"', 'w[3] = "b"', 'w[4] = "a"']
    base_x = 110
    cell_w = 150
    cell_h = 60
    gap_x = 15

    # Символи вхідного рядка (l = 0)
    for i, sym in enumerate(symbols):
        cx = base_x + i * (cell_w + gap_x) + cell_w / 2
        cy = 475
        frags.append(rect(cx - cell_w/2, cy - 20, cell_w, 40, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(cx, cy + 5, sym, size=14, bold=True, color="#1e3a8a"))

    # Рівень 1 (l = 1, довжина 1): 4 клітинки
    y1 = 390
    cell_l1 = [
        ("P[1, 1]", "{ B }"),
        ("P[1, 2]", "{ A, C }"),
        ("P[1, 3]", "{ B }"),
        ("P[1, 4]", "{ A, C }")
    ]
    for i, (hdr, val) in enumerate(cell_l1):
        cx = base_x + i * (cell_w + gap_x) + cell_w / 2
        frags.append(arrow(cx, 455, cx, y1 + cell_h/2 + 2, color=MUTED, sw=1.2))
        frags.append(rect(cx - cell_w/2, y1 - cell_h/2, cell_w, cell_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=5))
        frags.append(text(cx, y1 - 10, hdr, size=12, bold=True, color=MUTED))
        frags.append(text(cx, y1 + 14, val, size=14, bold=True, color=INK))

    # Рівень 2 (l = 2, довжина 2): 3 клітинки
    y2 = 300
    shift_l2 = (cell_w + gap_x) / 2
    cell_l2 = [
        ("P[2, 1] (b a)", "{ S, A, C }"),
        ("P[2, 2] (a b)", "{ S, C }"),
        ("P[2, 3] (b a)", "{ S, A, C }")
    ]
    for i, (hdr, val) in enumerate(cell_l2):
        cx = base_x + shift_l2 + i * (cell_w + gap_x) + cell_w / 2
        frags.append(rect(cx - cell_w/2, y2 - cell_h/2, cell_w, cell_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=5))
        frags.append(text(cx, y2 - 10, hdr, size=12, bold=True, color=MUTED))
        frags.append(text(cx, y2 + 14, val, size=14, bold=True, color=INK))

    # Рівень 3 (l = 3, довжина 3): 2 клітинки
    y3 = 210
    shift_l3 = (cell_w + gap_x)
    cell_l3 = [
        ("P[3, 1] (b a b)", "{ B }"),
        ("P[3, 2] (a b a)", "{ S, A, C }")
    ]
    for i, (hdr, val) in enumerate(cell_l3):
        cx = base_x + shift_l3 + i * (cell_w + gap_x) + cell_w / 2
        f_fill = "#fdf4ff" if i == 0 else "#f8fafc"
        f_stroke = "#a855f7" if i == 0 else LINE
        frags.append(rect(cx - cell_w/2, y3 - cell_h/2, cell_w, cell_h, fill=f_fill, stroke=f_stroke, sw=1.8 if i==0 else 1.5, rx=5))
        frags.append(text(cx, y3 - 10, hdr, size=12, bold=True, color="#a855f7" if i == 0 else MUTED))
        frags.append(text(cx, y3 + 14, val, size=14, bold=True, color=INK))

    # Рівень 4 (l = 4, довжина 4, верхівка): 1 клітинка
    y4 = 120
    shift_l4 = (cell_w + gap_x) * 1.5
    cx_top = base_x + shift_l4 + cell_w / 2
    frags.append(rect(cx_top - cell_w/2, y4 - cell_h/2, cell_w, cell_h, fill="#ecfdf5", stroke=FIELD, sw=2.2, rx=6))
    frags.append(text(cx_top, y4 - 10, "P[4, 1] (b a b a)", size=12, bold=True, color=FIELD))
    frags.append(text(cx_top, y4 + 14, "{ S, A, C }  OK", size=15, bold=True, color="#065f46"))

    # Пояснювальні стрілки обчислення для P[3, 1]
    c_p31 = base_x + shift_l3 + cell_w / 2
    c_p11 = base_x + cell_w / 2
    c_p22 = base_x + shift_l2 + 1 * (cell_w + gap_x) + cell_w / 2
    c_p21 = base_x + shift_l2 + cell_w / 2
    c_p13 = base_x + 2 * (cell_w + gap_x) + cell_w / 2

    # Стрілка для k=1
    frags.append(arrow(c_p11 + 30, y1 - 25, c_p31 - 40, y3 + 25, color=POS, sw=1.5))
    frags.append(arrow(c_p22, y2 - 25, c_p31 - 10, y3 + 25, color=POS, sw=1.5))
    frags.append(text(285, 260, "k=1: P[1,1] x P[2,2]", size=11, color=POS, bold=True))

    # Стрілка для k=2
    frags.append(arrow(c_p21 + 20, y2 - 25, c_p31 + 10, y3 + 25, color=NEG, sw=1.5))
    frags.append(arrow(c_p13, y1 - 25, c_p31 + 40, y3 + 25, color=NEG, sw=1.5))
    frags.append(text(465, 260, "k=2: P[2,1] x P[1,3]", size=11, color=NEG, bold=True))

    frags.append(text(410, 68, "S in P[n, 1] => слово w належить мові L(G)", size=13, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "cyk-table-pyramid.svg"), w, h, *frags)


def fig_cnf_derivation_tree():
    """Синтаксичне дерево виведення в CNF порівняно з довільним КВ-деревом."""
    w, h = 800, 440
    frags = []

    frags.append(text(400, 25, "Структура дерева виведення в нормальній формі Хомського", size=18, bold=True))

    # Ліва частина: Бінарне дерево в CNF
    frags.append(rect(30, 50, 350, 360, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(205, 75, "Бінарне дерево виведення (CNF)", size=14, bold=True, color="#1e40af"))
    frags.append(text(205, 95, "Правила A -> BC та A -> a", size=12, color=MUTED))

    # Вузли лівого дерева (CNF)
    # Корінь S
    frags.append(circle(205, 135, 18, fill="#eff6ff", stroke="#1d4ed8", sw=1.8))
    frags.append(text(205, 140, "S", size=14, bold=True, color="#1d4ed8"))

    # Рівень 1: A та B
    frags.append(line(205, 153, 135, 195, color=LINE, sw=1.5))
    frags.append(line(205, 153, 275, 195, color=LINE, sw=1.5))

    frags.append(circle(135, 205, 18, fill="#eff6ff", stroke="#1d4ed8", sw=1.8))
    frags.append(text(135, 210, "A", size=14, bold=True, color="#1d4ed8"))

    frags.append(circle(275, 205, 18, fill="#eff6ff", stroke="#1d4ed8", sw=1.8))
    frags.append(text(275, 210, "B", size=14, bold=True, color="#1d4ed8"))

    # Рівень 2: B, A від лівого A; термінал b від правого B
    frags.append(line(135, 223, 90, 265, color=LINE, sw=1.5))
    frags.append(line(135, 223, 175, 265, color=LINE, sw=1.5))
    frags.append(line(275, 223, 275, 335, color=LINE, sw=1.5))

    frags.append(circle(90, 275, 18, fill="#eff6ff", stroke="#1d4ed8", sw=1.8))
    frags.append(text(90, 280, "B", size=14, bold=True, color="#1d4ed8"))

    frags.append(circle(175, 275, 18, fill="#eff6ff", stroke="#1d4ed8", sw=1.8))
    frags.append(text(175, 280, "A", size=14, bold=True, color="#1d4ed8"))

    # Рівень 3: термінали
    frags.append(line(90, 293, 90, 335, color=LINE, sw=1.5))
    frags.append(line(175, 293, 175, 335, color=LINE, sw=1.5))

    # Листя (термінали)
    leafs_cnf = [(90, 350, "'b'"), (175, 350, "'a'"), (275, 350, "'b'")]
    for lx, ly, lch in leafs_cnf:
        frags.append(rect(lx - 16, ly - 15, 32, 30, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
        frags.append(text(lx, ly + 5, lch, size=13, bold=True, color="#065f46"))

    frags.append(text(205, 395, "Строго бінарне розгалуження: 2n - 1 вузлів", size=11, bold=True, color="#1e40af"))

    # Права частина: Довільне КВ-дерево
    frags.append(rect(420, 50, 350, 360, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(595, 75, "Довільне дерево виведення (CFG)", size=14, bold=True, color="#9a3412"))
    frags.append(text(595, 95, "Правила A -> alpha (довільна довжина)", size=12, color=MUTED))

    # Вузли правого дерева
    frags.append(circle(595, 135, 18, fill="#fff7ed", stroke="#ea580c", sw=1.8))
    frags.append(text(595, 140, "E", size=14, bold=True, color="#ea580c"))

    # 3 гілки: E, '+', T
    frags.append(line(595, 153, 495, 205, color=LINE, sw=1.5))
    frags.append(line(595, 153, 595, 335, color=LINE, sw=1.5))
    frags.append(line(595, 153, 695, 205, color=LINE, sw=1.5))

    frags.append(circle(495, 215, 18, fill="#fff7ed", stroke="#ea580c", sw=1.8))
    frags.append(text(495, 220, "E", size=14, bold=True, color="#ea580c"))

    # '+' термінал посередині
    frags.append(rect(595 - 16, 350 - 15, 32, 30, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(595, 355, "'+'", size=13, bold=True, color=POS))

    frags.append(circle(695, 215, 18, fill="#fff7ed", stroke="#ea580c", sw=1.8))
    frags.append(text(695, 220, "T", size=14, bold=True, color="#ea580c"))

    # Гілки вниз від лівого E і правого T
    frags.append(line(495, 233, 495, 335, color=LINE, sw=1.5))
    frags.append(rect(495 - 16, 350 - 15, 32, 30, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(495, 355, "'id'", size=12, bold=True, color="#065f46"))

    frags.append(line(695, 233, 660, 275, color=LINE, sw=1.5))
    frags.append(line(695, 233, 730, 275, color=LINE, sw=1.5))

    frags.append(circle(660, 285, 16, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(660, 290, "T", size=12, bold=True, color="#ea580c"))
    frags.append(line(660, 301, 660, 335, color=LINE, sw=1.5))
    frags.append(rect(660 - 15, 350 - 15, 30, 30, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(660, 355, "'*'", size=12, bold=True, color="#065f46"))

    frags.append(circle(730, 285, 16, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(730, 290, "F", size=12, bold=True, color="#ea580c"))
    frags.append(line(730, 301, 730, 335, color=LINE, sw=1.5))
    frags.append(rect(730 - 15, 350 - 15, 30, 30, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(730, 355, "'id'", size=12, bold=True, color="#065f46"))

    frags.append(text(595, 395, "Довільна арність правил (ланцюжки, eps-переходи)", size=11, bold=True, color="#9a3412"))

    render(os.path.join(OUT_DIR, "cnf-derivation-tree.svg"), w, h, *frags)


def fig_cyk_algorithm_flow():
    """Конвеєр роботи алгоритму CYK: від граматики до синтаксичного дерева."""
    w, h = 820, 220
    frags = []

    frags.append(text(410, 25, "Конвеєр синтаксичного аналізу CYK", size=17, bold=True))

    steps = [
        ("1. Конвертація в CNF", "Усунення eps, UNIT,\nдовгих та змішаних правил", 100),
        ("2. Базовий шар (l = 1)", "Заповнення P[1, i] за\nтермінальними A -> w[i]", 260),
        ("3. Ітеративне ДП (l = 2..n)", "Об'єднання P[k,i] x P[l-k,i+k]\nдля правил A -> BC", 450),
        ("4. Перевірка та AST", "S in P[n, 1] ? Відновлення\nдерева за вказівниками", 670),
    ]

    for title, desc, cx in steps:
        tw = 170 if cx == 670 else 160
        frags.append(rect(cx - tw/2, 55, tw, 130, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
        frags.append(text(cx, 80, title, size=13, bold=True, color="#1e3a8a"))
        frags.append(line(cx - tw/2 + 10, 95, cx + tw/2 - 10, 95, color="#cbd5e1", sw=1.0))
        lines = desc.split("\n")
        for j, ln in enumerate(lines):
            frags.append(text(cx, 120 + j * 20, ln, size=12, color=INK))

    # Стрілки між блоками
    frags.append(arrow(180, 120, 180 + 35, 120, color=LINE, sw=1.8))
    frags.append(arrow(340, 120, 340 + 35, 120, color=LINE, sw=1.8))
    frags.append(arrow(530, 120, 530 + 55, 120, color=LINE, sw=1.8))

    render(os.path.join(OUT_DIR, "cyk-algorithm-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_cyk_table_pyramid()
    fig_cnf_derivation_tree()
    fig_cyk_algorithm_flow()
    print("Всі фігури успішно згенеровано.")
