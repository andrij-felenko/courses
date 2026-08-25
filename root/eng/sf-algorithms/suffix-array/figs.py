# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Суфіксний масив»."""

import sys
import os

# 4 рівні вгору: root/eng/sf-algorithms/suffix-array -> root -> repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_suffix_array_concept():
    """Фігура 1: Концепція суфіксного масиву на прикладі banana$."""
    w, h = 880, 420
    frags = []

    # Заголовок блоків
    frags.append(text(220, 35, "Вихідний рядок: S = \"banana$\"", size=16, bold=True))
    frags.append(text(660, 35, "Відсортований суфіксний масив (SA)", size=16, bold=True))

    # Вихідний рядок у вигляді масиву символів
    chars = ["b", "a", "n", "a", "n", "a", "$"]
    cell_w = 40
    start_x = 80
    y_row = 60
    frags.append(text(start_x - 30, y_row + 24, "i :", size=13, color=MUTED, bold=True, anchor="end"))
    for idx, ch in enumerate(chars):
        x = start_x + idx * cell_w
        bg_col = "#eaf0fd" if ch == "$" else FILL
        frags.append(rect(x, y_row, cell_w, 36, fill=bg_col, stroke=LINE, sw=1.2, rx=4))
        frags.append(text(x + cell_w / 2, y_row + 22, ch, size=15, bold=True))
        frags.append(text(x + cell_w / 2, y_row - 8, str(idx), size=12, color=MUTED))

    # Несортовані суфікси
    suffixes_orig = [
        (0, "banana$"),
        (1, "anana$"),
        (2, "nana$"),
        (3, "ana$"),
        (4, "na$"),
        (5, "a$"),
        (6, "$")
    ]

    y_start = 135
    row_h = 34
    frags.append(text(start_x + 10, y_start - 12, "Позиція", size=12, color=MUTED, bold=True))
    frags.append(text(start_x + 110, y_start - 12, "Суфікс S[i..N-1]", size=12, color=MUTED, bold=True))

    for idx, (pos, suf) in enumerate(suffixes_orig):
        cy = y_start + idx * row_h
        # Позиція
        frags.append(rect(start_x, cy, 45, 28, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
        frags.append(text(start_x + 22.5, cy + 18, str(pos), size=13, bold=True))
        # Текст суфікса
        frags.append(rect(start_x + 60, cy, 140, 28, fill=FILL, stroke=LINE, sw=1.0, rx=3))
        frags.append(text(start_x + 70, cy + 18, suf, size=13, anchor="start"))

    # Стрілка сортування
    frags.append(arrow(320, 240, 460, 240, color=POS, sw=2.5))
    frags.append(text(390, 225, "Лексикографічне", size=13, color=POS, bold=True))
    frags.append(text(390, 260, "сортування", size=13, color=POS, bold=True))

    # Відсортовані суфікси
    sorted_suffixes = [
        (0, 6, "$"),
        (1, 5, "a$"),
        (2, 3, "ana$"),
        (3, 1, "anana$"),
        (4, 0, "banana$"),
        (5, 4, "na$"),
        (6, 2, "nana$")
    ]

    r_start = 500
    frags.append(text(r_start + 20, y_start - 12, "Ранг k", size=12, color=MUTED, bold=True))
    frags.append(text(r_start + 90, y_start - 12, "SA[k]", size=12, color=FIELD, bold=True))
    frags.append(text(r_start + 200, y_start - 12, "Відсортований суфікс", size=12, color=MUTED, bold=True))

    for k, sa_val, suf in sorted_suffixes:
        cy = y_start + k * row_h
        # Ранг k
        frags.append(rect(r_start, cy, 45, 28, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
        frags.append(text(r_start + 22.5, cy + 18, str(k), size=13, color=MUTED))
        # Значення SA
        frags.append(rect(r_start + 60, cy, 60, 28, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=3))
        frags.append(text(r_start + 90, cy + 18, str(sa_val), size=14, color=FIELD, bold=True))
        # Текст суфікса
        frags.append(rect(r_start + 135, cy, 185, 28, fill=FILL, stroke=LINE, sw=1.0, rx=3))
        frags.append(text(r_start + 145, cy + 18, suf, size=13, anchor="start"))

    # Підсумковий масив
    y_bot = 385
    frags.append(text(r_start - 100, y_bot + 18, "Масив SA = [", size=14, bold=True, anchor="end"))
    for idx, (_, sa_val, _) in enumerate(sorted_suffixes):
        x = r_start - 80 + idx * 42
        frags.append(rect(x, y_bot, 36, 26, fill="#e8f8f0", stroke=FIELD, sw=1.2, rx=3))
        frags.append(text(x + 18, y_bot + 17, str(sa_val), size=13, color=FIELD, bold=True))
        if idx < len(sorted_suffixes) - 1:
            frags.append(text(x + 39, y_bot + 17, ",", size=13, bold=True))
    frags.append(text(r_start - 80 + len(sorted_suffixes) * 42, y_bot + 18, "]", size=14, bold=True))

    render(os.path.join(OUT_DIR, "suffix-array-concept.svg"), w, h, *frags)


def fig_lcp_array_rmq():
    """Фігура 2: Масив LCP та запити мінімуму на відрізку (RMQ)."""
    w, h = 880, 400
    frags = []

    frags.append(text(w / 2, 30, "Масив найдовших спільних префіксів (LCP Array)", size=16, bold=True))

    rows = [
        (0, 6, 0, "$", "-"),
        (1, 5, 0, "a$", "lcp($, a$) = 0"),
        (2, 3, 1, "ana$", "lcp(a$, ana$) = 1 (\"a\")"),
        (3, 1, 3, "anana$", "lcp(ana$, anana$) = 3 (\"ana\")"),
        (4, 0, 0, "banana$", "lcp(anana$, banana$) = 0"),
        (5, 4, 0, "na$", "lcp(banana$, na$) = 0"),
        (6, 2, 2, "nana$", "lcp(na$, nana$) = 2 (\"na\")")
    ]

    sx = 60
    sy = 70
    rh = 36

    # Заголовки стовпців
    frags.append(text(sx + 25, sy - 12, "k", size=13, color=MUTED, bold=True))
    frags.append(text(sx + 85, sy - 12, "SA[k]", size=13, color=FIELD, bold=True))
    frags.append(text(sx + 155, sy - 12, "LCP[k]", size=13, color=POS, bold=True))
    frags.append(text(sx + 270, sy - 12, "Суфікс S[SA[k]..N-1]", size=13, color=INK, bold=True))
    frags.append(text(sx + 450, sy - 12, "Спільний префікс із попереднім", size=13, color=MUTED, bold=True))

    for k, sa_val, lcp_val, suf, desc in rows:
        cy = sy + k * rh
        # Виділення діапазону для демонстрації RMQ (рядки 1, 2, 3)
        bg = "#fff8e8" if 1 <= k <= 3 else "#ffffff"

        frags.append(rect(sx, cy, 50, 30, fill=bg, stroke=MUTED, sw=1.0, rx=3))
        frags.append(text(sx + 25, cy + 19, str(k), size=13, color=MUTED))

        frags.append(rect(sx + 60, cy, 50, 30, fill="#e8f8f0" if bg == "#ffffff" else "#d0f0e0", stroke=FIELD, sw=1.2, rx=3))
        frags.append(text(sx + 85, cy + 19, str(sa_val), size=13, color=FIELD, bold=True))

        frags.append(rect(sx + 120, cy, 65, 30, fill="#fdecea" if bg == "#ffffff" else "#fcd0cc", stroke=POS, sw=1.2, rx=3))
        frags.append(text(sx + 152.5, cy + 19, str(lcp_val), size=14, color=POS, bold=True))

        frags.append(rect(sx + 195, cy, 150, 30, fill=FILL, stroke=LINE, sw=1.0, rx=3))
        frags.append(text(sx + 205, cy + 19, suf, size=13, anchor="start"))

        frags.append(text(sx + 360, cy + 19, desc, size=12, color=MUTED, anchor="start"))

    # Блок пояснення RMQ властивості праворуч
    bx, by, bw, bh = 580, 85, 270, 240
    frags.append(rect(bx, by, bw, bh, fill="#f9fafb", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(bx + bw / 2, by + 30, "Властивість RMQ для LCP", size=14, bold=True))

    l1 = "LCP довільних суфіксів i та j:"
    l2 = "LCP(SA[i], SA[j]) = min( LCP[k] )"
    l3 = "де k змінюється від i+1 до j"
    frags.append(text(bx + bw / 2, by + 65, l1, size=12, color=INK))
    frags.append(text(bx + bw / 2, by + 92, l2, size=13, color=POS, bold=True))
    frags.append(text(bx + bw / 2, by + 115, l3, size=12, color=MUTED))

    # Приклад обчислення
    frags.append(line(bx + 20, by + 135, bx + bw - 20, by + 135, color="#e5e7eb", sw=1.0))
    frags.append(text(bx + bw / 2, by + 160, "Приклад: LCP(SA[1], SA[3])", size=13, bold=True))
    frags.append(text(bx + bw / 2, by + 182, "Суфікси \"a$\" та \"anana$\"", size=12, color=MUTED))
    frags.append(text(bx + bw / 2, by + 208, "= min( LCP[2], LCP[3] )", size=12, color=INK))
    frags.append(text(bx + bw / 2, by + 228, "= min( 1, 3 ) = 1 (\"a\")", size=13, color=FIELD, bold=True))

    # Дужка праворуч від таблиці для рядків 2 і 3
    frags.append(line(550, sy + rh + 15, 565, sy + rh + 15, color=POS, sw=2.0))
    frags.append(line(565, sy + rh + 15, 565, sy + 3 * rh + 15, color=POS, sw=2.0))
    frags.append(line(565, sy + 2 * rh + 15, 575, sy + 2 * rh + 15, color=POS, sw=2.0))
    frags.append(line(550, sy + 3 * rh + 15, 565, sy + 3 * rh + 15, color=POS, sw=2.0))

    # Нижній висновок
    frags.append(text(w / 2, 365, "Sparse Table дозволяє відповідати на запит LCP будь-яких двох суфіксів за O(1) час.", size=13, color=INK, bold=True))

    render(os.path.join(OUT_DIR, "lcp-array-rmq.svg"), w, h, *frags)


def fig_prefix_doubling_steps():
    """Фігура 3: Алгоритм подвоєння префіксів Манбера — Маєрса."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Алгоритм подвоєння префіксів Манбера — Маєрса (Prefix Doubling)", size=16, bold=True))

    col_w = 260
    col1_x = 40
    col2_x = 320
    col3_x = 600

    # Стовпець 1: k = 0 (довжина 1)
    frags.append(rect(col1_x, 55, col_w - 20, 310, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(col1_x + (col_w - 20) / 2, 80, "Крок 1: довжина 2⁰ = 1", size=14, bold=True))
    frags.append(text(col1_x + (col_w - 20) / 2, 100, "Сортування окремих символів", size=11, color=MUTED))

    data_k0 = [
        (0, "b", 1),
        (1, "a", 0),
        (2, "n", 2),
        (3, "a", 0),
        (4, "n", 2),
        (5, "a", 0),
        (6, "$", -1)
    ]
    sy = 120
    for idx, ch, rk in data_k0:
        cy = sy + idx * 28
        frags.append(text(col1_x + 25, cy + 14, f"i={idx}", size=12, color=MUTED))
        frags.append(text(col1_x + 90, cy + 14, f"'{ch}'", size=12, bold=True))
        frags.append(text(col1_x + 180, cy + 14, f"Rank={rk}", size=12, color=POS, bold=True))

    # Стовпець 2: k = 1 (довжина 2)
    frags.append(rect(col2_x, 55, col_w - 20, 310, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(col2_x + (col_w - 20) / 2, 80, "Крок 2: довжина 2¹ = 2", size=14, bold=True))
    frags.append(text(col2_x + (col_w - 20) / 2, 100, "Пари рангів (R[i], R[i+1])", size=11, color=MUTED))

    data_k1 = [
        (0, "ba", "(1, 0)", 3),
        (1, "an", "(0, 2)", 1),
        (2, "na", "(2, 0)", 4),
        (3, "an", "(0, 2)", 1),
        (4, "na", "(2, 0)", 4),
        (5, "a$", "(0, -1)", 0),
        (6, "$", "(-1, -1)", -1)
    ]
    for idx, s2, pair, rk in data_k1:
        cy = sy + idx * 28
        frags.append(text(col2_x + 25, cy + 14, f"i={idx}", size=12, color=MUTED))
        frags.append(text(col2_x + 85, cy + 14, pair, size=11, bold=True))
        frags.append(text(col2_x + 185, cy + 14, f"Rank={rk}", size=12, color=POS, bold=True))

    # Стовпець 3: k = 2 (довжина 4)
    frags.append(rect(col3_x, 55, col_w - 20, 310, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(col3_x + (col_w - 20) / 2, 80, "Крок 3: довжина 2² = 4", size=14, bold=True))
    frags.append(text(col3_x + (col_w - 20) / 2, 100, "Пари рангів (R[i], R[i+2])", size=11, color=MUTED))

    data_k2 = [
        (0, "(3, 4)", 4),
        (1, "(1, 1)", 3),
        (2, "(4, 4)", 6),
        (3, "(1, 0)", 2),
        (4, "(4, -1)", 5),
        (5, "(0, -1)", 1),
        (6, "(-1, -1)", 0)
    ]
    for idx, pair, rk in data_k2:
        cy = sy + idx * 28
        frags.append(text(col3_x + 25, cy + 14, f"i={idx}", size=12, color=MUTED))
        frags.append(text(col3_x + 95, cy + 14, pair, size=11, bold=True))
        frags.append(text(col3_x + 185, cy + 14, f"SA_pos={rk}", size=12, color=FIELD, bold=True))

    # Стрілки між стовпцями
    frags.append(arrow(col1_x + col_w - 20, 200, col2_x, 200, color=LINE, sw=1.8))
    frags.append(arrow(col2_x + col_w - 20, 200, col3_x, 200, color=LINE, sw=1.8))

    # Нижній висновок
    frags.append(text(w / 2, 395, "Кількість кроків подвоєння: ⌈log₂ N⌉. Кожен крок сортується Radix Sort за O(N), сумарно O(N log N).", size=13, color=INK, bold=True))

    render(os.path.join(OUT_DIR, "prefix-doubling-steps.svg"), w, h, *frags)


def fig_suffix_tree_vs_array():
    """Фігура 4: Порівняння суфіксного дерева та суфіксного масиву."""
    w, h = 880, 400
    frags = []

    frags.append(text(w / 2, 28, "Порівняння структур: Суфіксне дерево проти Суфіксного масиву", size=16, bold=True))

    # Ліва половина: Суфіксне дерево
    lx, ly, lw, lh = 40, 55, 380, 315
    frags.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(text(lx + lw / 2, ly + 25, "Суфіксне дерево (Suffix Tree)", size=15, color="#c0392b", bold=True))

    # Схематичне дерево
    rx, ry = lx + lw / 2, ly + 65
    frags.append(circle(rx, ry, 12, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(rx, ry + 4, "R", size=11, bold=True))

    # Гілки дерева
    n1_x, n1_y = rx - 100, ry + 60
    n2_x, n2_y = rx, ry + 60
    n3_x, n3_y = rx + 100, ry + 60

    frags.append(line(rx, ry + 12, n1_x, n1_y - 12, color=LINE, sw=1.2))
    frags.append(line(rx, ry + 12, n2_x, n2_y - 12, color=LINE, sw=1.2))
    frags.append(line(rx, ry + 12, n3_x, n3_y - 12, color=LINE, sw=1.2))

    frags.append(text(rx - 65, ry + 30, "\"a\"", size=11, color=MUTED))
    frags.append(text(rx + 15, ry + 30, "\"b\"", size=11, color=MUTED))
    frags.append(text(rx + 65, ry + 30, "\"n\"", size=11, color=MUTED))

    frags.append(circle(n1_x, n1_y, 10, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(circle(n2_x, n2_y, 10, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(circle(n3_x, n3_y, 10, fill=FILL, stroke=LINE, sw=1.2))

    # Листя
    l1_x, l1_y = n1_x - 35, n1_y + 45
    l2_x, l2_y = n1_x + 35, n1_y + 45
    frags.append(line(n1_x, n1_y + 10, l1_x, l1_y - 10, color=LINE, sw=1.0))
    frags.append(line(n1_x, n1_y + 10, l2_x, l2_y - 10, color=LINE, sw=1.0))
    frags.append(rect(l1_x - 12, l1_y - 10, 24, 20, fill="#eaf0fd", stroke=NEG, sw=1.0, rx=2))
    frags.append(text(l1_x, l1_y + 4, "5", size=11, color=NEG, bold=True))
    frags.append(rect(l2_x - 12, l2_y - 10, 24, 20, fill="#eaf0fd", stroke=NEG, sw=1.0, rx=2))
    frags.append(text(l2_x, l2_y + 4, "3", size=11, color=NEG, bold=True))

    tree_props = [
        "• Розмір: 20–45 байтів на символ тексту",
        "• Велика кількість дрібних об'єктів у купі",
        "• Промахи кешу (Pointer Chasing)",
        "• Складні алгоритми побудови (Укконен)"
    ]
    for idx, prop in enumerate(tree_props):
        frags.append(text(lx + 20, ly + 200 + idx * 24, prop, size=12, color=INK, anchor="start"))

    # Права половина: Суфіксний масив
    rax, ray, raw, rah = 460, 55, 380, 315
    frags.append(rect(rax, ray, raw, rah, fill="#ffffff", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(text(rax + raw / 2, ray + 25, "Суфіксний масив (Suffix Array + LCP)", size=15, color="#27ae60", bold=True))

    # Схематичний масив
    arr_y = ray + 65
    arr_h = 32
    cell_w = 42
    start_arr = rax + 40

    frags.append(text(start_arr - 15, arr_y + 20, "SA:", size=12, color=FIELD, bold=True, anchor="end"))
    sa_vals = [6, 5, 3, 1, 0, 4, 2]
    for idx, val in enumerate(sa_vals):
        cx = start_arr + idx * cell_w
        frags.append(rect(cx, arr_y, cell_w, arr_h, fill="#e8f8f0", stroke=FIELD, sw=1.2, rx=3))
        frags.append(text(cx + cell_w / 2, arr_y + 21, str(val), size=13, color=FIELD, bold=True))

    lcp_y = arr_y + 42
    frags.append(text(start_arr - 15, lcp_y + 20, "LCP:", size=12, color=POS, bold=True, anchor="end"))
    lcp_vals = [0, 0, 1, 3, 0, 0, 2]
    for idx, val in enumerate(lcp_vals):
        cx = start_arr + idx * cell_w
        frags.append(rect(cx, lcp_y, cell_w, arr_h, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        frags.append(text(cx + cell_w / 2, lcp_y + 21, str(val), size=13, color=POS, bold=True))

    array_props = [
        "• Розмір: 4 байти на символ (uint32_t)",
        "• Єдиний неперервний буфер у пам'яті",
        "• Ідеальна просторова кеш-локальність",
        "• Простий двійковий пошук O(M + log N)"
    ]
    for idx, prop in enumerate(array_props):
        frags.append(text(rax + 20, ray + 200 + idx * 24, prop, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "suffix-tree-vs-array.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_suffix_array_concept()
    fig_lcp_array_rmq()
    fig_prefix_doubling_steps()
    fig_suffix_tree_vs_array()
    print("Фігури успішно згенеровано.")
