# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Розріджена таблиця» (Sparse Table)."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/math/number-theory/sparse-table)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")


def fig1_powers_decomposition():
    """Ілюстрація перекривного покриття відрізка двома блоками довжини 2^k."""
    w, h = 880, 340
    p = []

    # Заголовок / підзаголовок
    p.append(text(w / 2, 28, "Покриття довільного запиту [L, R] двома перекривними блоками довжини 2^k", size=16, bold=True))
    p.append(text(w / 2, 50, "Довжина L = R - L + 1 = 7  →  k = ⌊log₂(7)⌋ = 2  →  довжина блоку 2² = 4", size=13, color=MUTED))

    # Візуалізація масиву
    arr = [14, 9, 3, 7, 2, 5, 8, 12, 19, 6]
    n = len(arr)
    cell_w = 64
    cell_h = 44
    start_x = (w - n * cell_w) / 2
    arr_y = 110

    # Малюємо комірки масиву
    for i in range(n):
        cx = start_x + i * cell_w
        is_in_query = 2 <= i <= 8
        is_overlap = (i == 5)
        
        # Вибір кольору комірки
        if is_overlap:
            fill_col = "#e8f8f0"
            stroke_col = FIELD
            sw = 2.0
        elif is_in_query:
            fill_col = "#f0f4fc"
            stroke_col = NEG
            sw = 1.5
        else:
            fill_col = FILL
            stroke_col = "#cbd5e1"
            sw = 1.0

        p.append(rect(cx, arr_y, cell_w, cell_h, fill=fill_col, stroke=stroke_col, sw=sw, rx=4))
        p.append(text(cx + cell_w / 2, arr_y - 10, "i = %d" % i, size=11, color=MUTED))
        p.append(text(cx + cell_w / 2, arr_y + cell_h / 2 + 5, str(arr[i]), size=15, bold=True, color=INK))

    # Виділення відрізка запиту [2, 8]
    ql_x = start_x + 2 * cell_w
    qr_x = start_x + 9 * cell_w
    p.append(line(ql_x, arr_y + cell_h + 12, qr_x, arr_y + cell_h + 12, color=INK, sw=2))
    p.append(line(ql_x, arr_y + cell_h + 7, ql_x, arr_y + cell_h + 17, color=INK, sw=2))
    p.append(line(qr_x, arr_y + cell_h + 7, qr_x, arr_y + cell_h + 17, color=INK, sw=2))
    p.append(text((ql_x + qr_x) / 2, arr_y + cell_h + 30, "Запит RMQ(L = 2, R = 8) — довжина 7 елементів", size=13, bold=True))

    # Блок 1: Лівий блок [L, L + 2^k - 1] = [2, 5]
    b1_x = start_x + 2 * cell_w
    b1_w = 4 * cell_w
    b1_y = arr_y + cell_h + 50
    p.append(rect(b1_x + 2, b1_y, b1_w - 4, 38, fill="#ebf3fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 24, "Лівий блок ST[2][2]: покриває [2, 5] (довжина 4) → min = 2", size=12, bold=True, color=NEG))

    # Блок 2: Правий блок [R - 2^k + 1, R] = [5, 8]
    b2_x = start_x + 5 * cell_w
    b2_w = 4 * cell_w
    b2_y = arr_y + cell_h + 96
    p.append(rect(b2_x + 2, b2_y, b2_w - 4, 38, fill="#ebf3fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(b2_x + b2_w / 2, b2_y + 24, "Правий блок ST[2][5]: покриває [5, 8] (довжина 4) → min = 2", size=12, bold=True, color=NEG))

    # Пояснення перекриття
    overlap_center_x = w / 2
    p.append(text(overlap_center_x, b2_y + 64, "Перекриття в точці i = 5: завдяки ідемпотентності min(a, a) = a дублювання не впливає на результат", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "sparse-table-powers-decomposition.svg"), w, h, *p)


def fig2_grid_structure():
    """Ілюстрація 2D структури таблиці ST[k][i] та рекурентного об'єднання блоків."""
    w, h = 880, 410
    p = []

    p.append(text(w / 2, 28, "Рекурентна побудова рівнів розрідженої таблиці ST[k][i]", size=16, bold=True))
    p.append(text(w / 2, 50, "Кожен блок рівня k утворюється об'єднанням двох сусідніх блоків рівня k - 1 довжини 2^(k-1)", size=13, color=MUTED))

    # Рівні k = 0, 1, 2, 3
    # Масив розміром 8
    n = 8
    cell_w = 80
    cell_h = 36
    grid_left = 160
    grid_top = 80

    levels = [
        ("k = 0 (довжина 1)", [7, 2, 3, 0, 5, 10, 3, 12]),
        ("k = 1 (довжина 2)", [2, 2, 0, 0, 5, 3, 3, "—"]),
        ("k = 2 (довжина 4)", [0, 0, 0, 0, 3, "—", "—", "—"]),
        ("k = 3 (довжина 8)", [0, "—", "—", "—", "—", "—", "—", "—"]),
    ]

    # Малюємо заголовки стовпців (індекси i)
    for i in range(n):
        cx = grid_left + i * cell_w
        p.append(text(cx + cell_w / 2, grid_top - 8, "i = %d" % i, size=12, bold=True, color=INK))

    # Малюємо таблицю
    for k_idx, (lbl, row_vals) in enumerate(levels):
        y = grid_top + k_idx * (cell_h + 24)
        # Підпис рядка (рівень k)
        p.append(text(grid_left - 15, y + cell_h / 2 + 4, lbl, size=12, bold=True, anchor="end", color=NEG if k_idx > 0 else INK))

        for i in range(n):
            x = grid_left + i * cell_w
            val = row_vals[i]
            is_dash = (val == "—")
            
            # Виділяємо об'єднання для ST[2][1]
            highlight_parent = (k_idx == 2 and i == 1)
            highlight_child1 = (k_idx == 1 and i == 1)
            highlight_child2 = (k_idx == 1 and i == 3)

            if highlight_parent:
                fill_c = "#e8f8f0"
                stroke_c = FIELD
                sw = 2.0
            elif highlight_child1 or highlight_child2:
                fill_c = "#ebf3fd"
                stroke_c = NEG
                sw = 1.8
            elif is_dash:
                fill_c = "#f8fafc"
                stroke_c = "#e2e8f0"
                sw = 1.0
            else:
                fill_c = FILL
                stroke_c = "#cbd5e1"
                sw = 1.2

            p.append(rect(x + 2, y, cell_w - 4, cell_h, fill=fill_c, stroke=stroke_c, sw=sw, rx=4))
            txt_c = MUTED if is_dash else (FIELD if highlight_parent else (NEG if (highlight_child1 or highlight_child2) else INK))
            p.append(text(x + cell_w / 2, y + cell_h / 2 + 5, str(val), size=14, bold=(not is_dash), color=txt_c))

    # Стрілки рекурентності: від ST[1][1] та ST[1][3] до ST[2][1]
    p1_x = grid_left + 1 * cell_w + cell_w / 2
    p1_y = grid_top + 1 * (cell_h + 24) + cell_h
    p2_x = grid_left + 3 * cell_w + cell_w / 2
    p2_y = grid_top + 1 * (cell_h + 24) + cell_h
    t_x = grid_left + 1 * cell_w + cell_w / 2
    t_y = grid_top + 2 * (cell_h + 24)

    p.append(arrow(p1_x, p1_y + 2, t_x, t_y - 2, color=FIELD, sw=2.0))
    p.append(arrow(p2_x, p2_y + 2, t_x + 15, t_y - 2, color=FIELD, sw=2.0))

    # Пояснення формули
    exp_y = grid_top + 4 * (cell_h + 24) + 12
    box_frag, _, _ = textbox(w / 2, exp_y, 
                             "ST[k][i] = min( ST[k - 1][i], ST[k - 1][i + 2^(k - 1)] )\n"
                             "Приклад: ST[2][1] = min( ST[1][1], ST[1][1 + 2¹] ) = min( ST[1][1], ST[1][3] ) = min(2, 0) = 0",
                             size=12, pad=8, fill="#fdfefe", stroke=FIELD, sw=1.5, color=INK, bold=False)
    p.append(box_frag)

    render(os.path.join(OUT, "sparse-table-grid-structure.svg"), w, h, *p)


def fig3_structures_comparison():
    """Порівняння розрідженої таблиці, дерева відрізків, дерева Фенвіка та префіксних сум."""
    w, h = 880, 370
    p = []

    p.append(text(w / 2, 28, "Порівняльний аналіз інтервальних структур даних", size=16, bold=True))
    p.append(text(w / 2, 50, "Часова складність операцій, споживання пам'яті та алгебраїчні обмеження", size=13, color=MUTED))

    # Стовпці таблиці
    cols = ["Структура", "Побудова", "RMQ (min/max/gcd)", "Сума (група)", "Оновлення", "Пам'ять", "Алгебра"]
    col_w = [160, 95, 140, 105, 95, 85, 140]
    start_x = (w - sum(col_w)) / 2
    start_y = 80
    row_h = 44

    # Шапка таблиці
    cur_x = start_x
    for j, (col_name, cw) in enumerate(zip(cols, col_w)):
        p.append(rect(cur_x, start_y, cw, row_h, fill="#1e293b", stroke="#0f172a", sw=1.0, rx=2))
        p.append(text(cur_x + cw / 2, start_y + row_h / 2 + 5, col_name, size=12, bold=True, color="#ffffff"))
        cur_x += cw

    rows_data = [
        ("Префіксні суми", "O(N)", "— (не підтримує)", "O(1)", "O(N)", "O(N)", "Абелева група (+, -)"),
        ("Розріджена таблиця", "O(N log N)", "O(1) [ідемпотентні]", "O(log N) [диз'юнктні]", "O(N log N) [статична]", "O(N log N)", "Напівґратка (min, gcd)"),
        ("Дерево відрізків", "O(N)", "O(log N)", "O(log N)", "O(log N)", "O(N) [4N слів]", "Моноїд (асоціативність)"),
        ("Дерево Фенвіка", "O(N)", "— (лише префікси)", "O(log N)", "O(log N)", "O(N) [N слів]", "Оборотна група (+, -)"),
    ]

    cur_y = start_y + row_h
    for row_idx, row in enumerate(rows_data):
        cur_x = start_x
        # Виділяємо розріджену таблицю
        is_st = (row_idx == 1)
        row_bg = "#ebf3fd" if is_st else (FILL if row_idx % 2 == 0 else "#ffffff")
        row_stroke = NEG if is_st else "#cbd5e1"
        row_sw = 1.8 if is_st else 1.0

        for col_idx, (cell_text, cw) in enumerate(zip(row, col_w)):
            p.append(rect(cur_x, cur_y, cw, row_h, fill=row_bg, stroke=row_stroke, sw=row_sw, rx=2))
            is_bold = (col_idx == 0 or (is_st and col_idx in (1, 2, 5)))
            cell_color = NEG if (is_st and col_idx in (0, 2)) else INK
            p.append(text(cur_x + cw / 2, cur_y + row_h / 2 + 5, cell_text, size=11 if col_idx >= 2 else 12, bold=is_bold, color=cell_color))
            cur_x += cw
        cur_y += row_h

    # Підсумковий акцент
    sum_y = cur_y + 30
    p.append(text(w / 2, sum_y, "Розріджена таблиця забезпечує абсолютний рекорд швидкості O(1) для запитів на незмінних масивах", size=13, bold=True, color=NEG))
    p.append(text(w / 2, sum_y + 20, "Дерево відрізків обирають лише тоді, коли елементи масиву динамічно змінюються в реальному часі", size=12, color=MUTED))

    render(os.path.join(OUT, "sparse-table-vs-trees.svg"), w, h, *p)


def main():
    if not os.path.exists(OUT):
        os.makedirs(OUT)
    fig1_powers_decomposition()
    fig2_grid_structure()
    fig3_structures_comparison()
    print("Всі фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
