# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Концепція стійкості сортування ───────────────────────────────────
def fig_stability_concept():
    W, H = 820, 360
    frags = []
    
    frags.append(text(W/2, 28, "Порівняння стійкого та нестійкого сортування", size=15, bold=True))
    frags.append(text(W/2, 48, "Початковий масив містить однакові ключі 5a та 5b", size=12, color=MUTED))

    # Початковий масив
    frags.append(text(W/2, 85, "Вхідний масив:", size=13, bold=True, anchor="middle"))
    
    # Коробки вхідного масиву
    x0 = W/2 - 200
    y0 = 105
    items_in = [("3", FILL, INK), ("5a", "#e8f8f5", FIELD), ("2", FILL, INK), ("5b", "#feefea", POS), ("1", FILL, INK)]
    for i, (val, bg_col, txt_col) in enumerate(items_in):
        bx = x0 + i * 80
        frags.append(rect(bx, y0, 70, 42, fill=bg_col, stroke=LINE, rx=6))
        frags.append(text(bx + 35, y0 + 26, val, size=14, bold=True, color=txt_col))

    # Стрілки розгалуження
    y_branch = 175
    frags.append(arrow(W/2 - 100, 155, W/4 + 40, y_branch, color=FIELD, sw=2))
    frags.append(arrow(W/2 + 100, 155, 3*W/4 - 40, y_branch, color=POS, sw=2))

    # Стійке сортування (ліворуч)
    x_st = W/4 - 150
    y_st = y_branch + 10
    frags.append(rect(x_st, y_st, 300, 130, fill="#f4faf7", stroke=FIELD, rx=8))
    frags.append(text(x_st + 150, y_st + 25, "Стійке сортування (Stable Sort)", size=13, bold=True, color=FIELD))
    frags.append(text(x_st + 150, y_st + 45, "Зберігає відносний порядок: 5a передує 5b", size=11, color=MUTED))
    
    items_st = [("1", FILL, INK), ("2", FILL, INK), ("3", FILL, INK), ("5a", "#e8f8f5", FIELD), ("5b", "#feefea", POS)]
    for i, (val, bg_col, txt_col) in enumerate(items_st):
        bx = x_st + 15 + i * 54
        frags.append(rect(bx, y_st + 65, 48, 38, fill=bg_col, stroke=FIELD, rx=5))
        frags.append(text(bx + 24, y_st + 89, val, size=13, bold=True, color=txt_col))

    # Нестійке сортування (праворуч)
    x_unst = 3*W/4 - 150
    y_unst = y_branch + 10
    frags.append(rect(x_unst, y_unst, 300, 130, fill="#fdf5f4", stroke=POS, rx=8))
    frags.append(text(x_unst + 150, y_unst + 25, "Нестійке сортування (Unstable Sort)", size=13, bold=True, color=POS))
    frags.append(text(x_unst + 150, y_unst + 45, "Порядок дублікатів порушено: 5b опинився перед 5a", size=11, color=MUTED))
    
    items_unst = [("1", FILL, INK), ("2", FILL, INK), ("3", FILL, INK), ("5b", "#feefea", POS), ("5a", "#e8f8f5", FIELD)]
    for i, (val, bg_col, txt_col) in enumerate(items_unst):
        bx = x_unst + 15 + i * 54
        frags.append(rect(bx, y_unst + 65, 48, 38, fill=bg_col, stroke=POS, rx=5))
        frags.append(text(bx + 24, y_unst + 89, val, size=13, bold=True, color=txt_col))

    render(os.path.join(OUT, "stability-concept.svg"), W, H, *frags)


# ── Фіг. 2: Багатопрохідне сортування за кількома ключами ────────────────────
def fig_multi_pass_sort():
    W, H = 840, 420
    frags = []
    
    frags.append(text(W/2, 26, "Багатопрохідне сортування списку за двома ключами (Клас ➔ Прізвище)", size=15, bold=True))
    frags.append(text(W/2, 46, "Крок 1: сортуємо за Прізвищем. Крок 2: сортуємо за Класом.", size=12, color=MUTED))

    # Крок 0: Вхідний список
    y_row0 = 80
    frags.append(text(70, y_row0 + 25, "Початкові\nдані:", size=11, bold=True, anchor="start"))
    data0 = [("10-А", "Коваль"), ("10-Б", "Бондар"), ("10-А", "Аврам"), ("10-Б", "Аврам")]
    for i, (cls, name) in enumerate(data0):
        bx = 160 + i * 160
        frags.append(rect(bx, y_row0, 140, 45, fill=FILL, stroke=LINE, rx=5))
        frags.append(text(bx + 70, y_row0 + 28, f"{cls}: {name}", size=12, bold=True))

    # Крок 1: Після сортування за Прізвищем
    y_row1 = 170
    frags.append(text(70, y_row1 + 25, "1. Сортування\nза Прізвищем:", size=11, bold=True, anchor="start"))
    frags.append(arrow(W/2, y_row0 + 48, W/2, y_row1 - 5, color=LINE))
    
    data1 = [("10-А", "Аврам"), ("10-Б", "Аврам"), ("10-Б", "Бондар"), ("10-А", "Коваль")]
    for i, (cls, name) in enumerate(data1):
        bx = 160 + i * 160
        frags.append(rect(bx, y_row1, 140, 45, fill="#e8f0fe", stroke=NEG, rx=5))
        frags.append(text(bx + 70, y_row1 + 28, f"{cls}: {name}", size=12, bold=True, color=NEG))

    # Крок 2: Стійке vs Нестійке сортування за Класом
    y_row2 = 280
    
    # Стійкий варіант
    frags.append(arrow(280, y_row1 + 48, 280, y_row2 - 5, color=FIELD))
    frags.append(text(160, y_row2 - 15, "Стійкий 2-й прохід (за Класом):", size=11, bold=True, color=FIELD, anchor="start"))
    data2_st = [("10-А", "Аврам"), ("10-А", "Коваль"), ("10-Б", "Аврам"), ("10-Б", "Бондар")]
    for i, (cls, name) in enumerate(data2_st[:2]):
        bx = 160 + i * 150
        frags.append(rect(bx, y_row2, 140, 45, fill="#e8f8f5", stroke=FIELD, rx=5))
        frags.append(text(bx + 70, y_row2 + 28, f"{cls}: {name}", size=12, bold=True, color=FIELD))

    # Нестійкий варіант
    frags.append(arrow(600, y_row1 + 48, 600, y_row2 - 5, color=POS))
    frags.append(text(480, y_row2 - 15, "Нестійкий 2-й прохід (зламано порядок):", size=11, bold=True, color=POS, anchor="start"))
    data2_unst = [("10-А", "Коваль"), ("10-А", "Аврам"), ("10-Б", "Бондар"), ("10-Б", "Аврам")]
    for i, (cls, name) in enumerate(data2_unst[:2]):
        bx = 480 + i * 150
        frags.append(rect(bx, y_row2, 140, 45, fill="#feefea", stroke=POS, rx=5))
        frags.append(text(bx + 70, y_row2 + 28, f"{cls}: {name}", size=12, bold=True, color=POS))

    # Підписи висновку
    frags.append(text(280, y_row2 + 75, "✓ Аврам передує Ковалю в 10-А", size=11, bold=True, color=FIELD))
    frags.append(text(600, y_row2 + 75, "✗ Коваль опинився перед Аврамом у 10-А!", size=11, bold=True, color=POS))

    render(os.path.join(OUT, "multi-pass-sort.svg"), W, H, *frags)


# ── Фіг. 3: Матриця алгоритмів та причин стійкості/нестійкості ──────────────────
def fig_algorithm_matrix():
    W, H = 840, 440
    frags = []
    
    frags.append(text(W/2, 28, "Класифікація алгоритмів сортування за стійкістю", size=15, bold=True))
    frags.append(text(W/2, 48, "Основний критерій: чи міняються місцями елементи через великі відстані", size=12, color=MUTED))

    # Колонка 1: Стійкі алгоритми
    x_st = 50
    w_col = 350
    frags.append(rect(x_st, 75, w_col, 330, fill="#f4faf7", stroke=FIELD, rx=8))
    frags.append(text(x_st + w_col/2, 102, "Стійкі алгоритми (Stable)", size=14, bold=True, color=FIELD))
    frags.append(line(x_st + 20, 115, x_st + w_col - 20, 115, color=FIELD))

    st_algos = [
        ("Сортування злиттям (Merge Sort)", "left[i] <= right[j] віддає перевагу лівому"),
        ("Сортування вставками (Insertion)", "зсув зупиняється на першому рівному"),
        ("Сортування бульбашкою (Bubble)", "обмін лише при строгому a[j] > a[j+1]"),
        ("Порозрядне / Рахунком (Radix/Counting)", "запис у кошики в порядку вихідного скану")
    ]
    for i, (name, desc) in enumerate(st_algos):
        y_item = 135 + i * 65
        frags.append(rect(x_st + 15, y_item, w_col - 30, 52, fill=BG, stroke=FIELD, rx=5))
        frags.append(text(x_st + 28, y_item + 22, f"• {name}", size=12, bold=True, anchor="start", color=INK))
        frags.append(text(x_st + 28, y_item + 40, desc, size=10, color=MUTED, anchor="start"))

    # Колонка 2: Нестійкі алгоритми
    x_unst = 440
    frags.append(rect(x_unst, 75, w_col, 330, fill="#fdf5f4", stroke=POS, rx=8))
    frags.append(text(x_unst + w_col/2, 102, "Нестійкі алгоритми (Unstable)", size=14, bold=True, color=POS))
    frags.append(line(x_unst + 20, 115, x_unst + w_col - 20, 115, color=POS))

    unst_algos = [
        ("Швидке сортування (Quicksort)", "перестрибування опорного елемента (pivot)"),
        ("Сортування купою (Heapsort)", "просіювання в дереві та обмін із кінцем"),
        ("Сортування вибором (Selection Sort)", "обмін мінімуму з a[i] через проміжні елементи"),
        ("Сортування Шелла (Shellsort)", "сорт зсувами з кроком h > 1 через великі відстані")
    ]
    for i, (name, desc) in enumerate(unst_algos):
        y_item = 135 + i * 65
        frags.append(rect(x_unst + 15, y_item, w_col - 30, 52, fill=BG, stroke=POS, rx=5))
        frags.append(text(x_unst + 28, y_item + 22, f"• {name}", size=12, bold=True, anchor="start", color=INK))
        frags.append(text(x_unst + 28, y_item + 40, desc, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "algorithm-stability-matrix.svg"), W, H, *frags)


# ── Фіг. 4: Декорування ключів початковим індексом ───────────────────────────
def fig_index_augmentation():
    W, H = 820, 340
    frags = []
    
    frags.append(text(W/2, 28, "Декорування ключів початковим індексом (Key Augmentation)", size=15, bold=True))
    frags.append(text(W/2, 48, "Перетворення ключа K на паралельний кортеж (K, index) робить будь-яке сортування стійким", size=12, color=MUTED))

    # Ліва панель: Вхідні елементи
    x_l = 60
    y_box = 85
    frags.append(rect(x_l, y_box, 320, 220, fill=FILL, stroke=LINE, rx=8))
    frags.append(text(x_l + 160, y_box + 25, "Оригінальні елементи з однаковим K", size=13, bold=True))
    
    frags.append(rect(x_l + 30, y_box + 50, 260, 45, fill=BG, stroke=LINE, rx=5))
    frags.append(text(x_l + 45, y_box + 77, "Елемент A: Key = 42 (Index 0)", size=12, anchor="start"))
    
    frags.append(rect(x_l + 30, y_box + 110, 260, 45, fill=BG, stroke=LINE, rx=5))
    frags.append(text(x_l + 45, y_box + 137, "Елемент B: Key = 42 (Index 1)", size=12, anchor="start"))

    frags.append(text(x_l + 160, y_box + 185, "Порівняння 42 == 42 викликає\nневизначеність у нестійкім сортуванні", size=10, color=POS))

    # Стрелка трансляції
    frags.append(arrow(x_l + 330, y_box + 110, x_l + 400, y_box + 110, color=NEG, sw=2))
    frags.append(text(x_l + 365, y_box + 90, "Декорування", size=11, bold=True, color=NEG))

    # Права панель: Декоровані кортежі
    x_r = 470
    frags.append(rect(x_r, y_box, 300, 220, fill="#e8f0fe", stroke=NEG, rx=8))
    frags.append(text(x_r + 150, y_box + 25, "Розширені ключі (Ключ, Індекс)", size=13, bold=True, color=NEG))

    frags.append(rect(x_r + 20, y_box + 50, 260, 45, fill=BG, stroke=NEG, rx=5))
    frags.append(text(x_r + 35, y_box + 77, "Tuple A: (42, 0)", size=12, bold=True, color=NEG, anchor="start"))

    frags.append(rect(x_r + 20, y_box + 110, 260, 45, fill=BG, stroke=NEG, rx=5))
    frags.append(text(x_r + 35, y_box + 137, "Tuple B: (42, 1)", size=12, bold=True, color=NEG, anchor="start"))

    frags.append(text(x_r + 150, y_box + 185, "Оскільки (42, 0) < (42, 1),\nпорядок суворо детермінований!", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "index-augmentation.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_stability_concept()
    fig_multi_pass_sort()
    fig_algorithm_matrix()
    fig_index_augmentation()
    print("Figures generated successfully in img/")
