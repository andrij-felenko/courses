# -*- coding: utf-8 -*-
"""Фігури до статті «Count-Min Sketch». Запуск: python figs.py
Виводить SVG у ./img/. Усі підписи рознесено із запасом."""
import sys, os

# 4 рівні вгору до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 46, 36
FILLED = "#eaf0fd"
ACCENT = "#fdecea"
GREEN_BG = "#eafaf1"

def draw_cell(x, y, label, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.5, tcolor=INK, tsize=13, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out

# ── Фігура 1: Матриця лічильників Count-Min Sketch ────────────────────────────
def fig_grid_update():
    W, H = 940, 440
    parts = []

    # Заголовок блоку вхідного елемента
    elem_box = rect(30, 55, 170, 44, fill=FILLED, stroke=NEG, sw=1.8, rx=6)
    elem_box += text(115, 82, "Елемент x (запит/вставка)", size=12, bold=True, color=NEG)
    parts.append(elem_box)

    # Хеш-функції
    hash_y = [150, 215, 280, 345]
    d_labels = ["h₁(x) = 3", "h₂(x) = 6", "h₃(x) = 1", "h₄(x) = 5"]
    col_targets = [3, 6, 1, 5]
    row_colors = [POS, FIELD, NEG, "#8e44ad"]

    # Сітка лічильників
    grid_x = 290
    cols = 7
    rows = 4
    
    # Значення лічильників у сітці
    table_data = [
        [12, 45, 3,  19, 8, 27, 4],
        [5,  18, 92, 14, 2, 33, 19],
        [8,  22, 15, 41, 9, 3,  50],
        [31, 4,  16, 7,  2, 19, 88]
    ]

    # Підписи колонок
    for c in range(cols):
        cx = grid_x + c * (CW + 6)
        parts.append(text(cx + CW / 2, 115, str(c), size=12, color=MUTED, bold=True))
    parts.append(text(grid_x + (cols * (CW + 6)) / 2, 95, "Стовпці w (ширина = ⌈e / ε⌉)", size=13, color=MUTED))

    # Малювання лічильників
    for r in range(rows):
        ry = hash_y[r] - CH / 2
        # Підпис рядка
        parts.append(text(grid_x - 15, ry + CH / 2 + 4, f"Рядок {r+1}", size=12, color=INK, anchor="end", bold=True))
        
        # Хеш-блок
        h_box = rect(30, ry, 170, CH, fill=FILL, stroke=LINE, sw=1.5, rx=5)
        h_box += text(115, ry + CH / 2 + 4, d_labels[r], size=13, color=INK, bold=True)
        parts.append(h_box)

        # Стрілка від вхідного елемента до хеш-блоку
        parts.append(arrow(115, 100, 115, ry - 2, color=MUTED, sw=1.2))

        for c in range(cols):
            cx = grid_x + c * (CW + 6)
            is_hit = (c == col_targets[r])
            f_col = ACCENT if is_hit else BG
            s_col = row_colors[r] if is_hit else LINE
            sw_val = 2.0 if is_hit else 1.0
            t_col = POS if is_hit else INK
            val_str = str(table_data[r][c])
            parts.append(draw_cell(cx, ry, val_str, w=CW, h=CH, fill=f_col, stroke=s_col, sw=sw_val, tcolor=t_col, bold=is_hit))

            if is_hit:
                # Стрілка від хешу до комірки
                parts.append(arrow(202, ry + CH / 2, cx - 2, ry + CH / 2, color=row_colors[r], sw=1.6))

    # Блок результату мінімуму справа
    min_box_x = 710
    min_box_y = 210
    m_box = rect(min_box_x, min_box_y - 45, 195, 135, fill=GREEN_BG, stroke=FIELD, sw=2, rx=8)
    m_box += text(min_box_x + 97, min_box_y - 20, "Запит частоти", size=13, bold=True, color=FIELD)
    m_box += text(min_box_x + 97, min_box_y + 8, "min(19, 19, 22, 19)", size=12, bold=True, color=INK)
    m_box += text(min_box_x + 97, min_box_y + 38, "= 19", size=19, bold=True, color=POS)
    m_box += text(min_box_x + 97, min_box_y + 68, "Оцінка частоти â[x]", size=12, italic=True, color=MUTED)
    parts.append(m_box)

    # Стрілка від сітки до блоку min
    parts.append(arrow(grid_x + cols * (CW + 6) + 10, 245, min_box_x - 4, 245, color=FIELD, sw=2))

    render(os.path.join(IMG, "sketch-grid-update.svg"), W, H, *parts, title="Оновлення та запит частоти в матриці Count-Min Sketch")


# ── Фігура 2: Консервативне оновлення (Conservative Update) ───────────────────
def fig_conservative_update():
    W, H = 880, 360
    parts = []

    # Ліва колонка: Звичайне оновлення
    left_x = 40
    parts.append(text(left_x + 175, 55, "Стандартне оновлення Count-Min", size=14, bold=True, color=POS))
    parts.append(text(left_x + 175, 75, "Кожен лічильник інкрементується: C[j, h_j(x)] += 1", size=11, color=MUTED))

    # Стан лічильників ДО
    parts.append(text(left_x + 20, 118, "Рядок 1 (h₁=2):", size=12, anchor="start"))
    parts.append(draw_cell(left_x + 160, 102, "10", w=52, h=30, fill=FILL, tcolor=INK))
    parts.append(text(left_x + 230, 118, "→", size=14, bold=True))
    parts.append(draw_cell(left_x + 255, 102, "11", w=52, h=30, fill=ACCENT, stroke=POS, sw=2, tcolor=POS, bold=True))

    parts.append(text(left_x + 20, 163, "Рядок 2 (h₂=5):", size=12, anchor="start"))
    parts.append(draw_cell(left_x + 160, 147, "15 (шум)", w=52, h=30, fill=FILL, tcolor=MUTED, tsize=10))
    parts.append(text(left_x + 230, 163, "→", size=14, bold=True))
    parts.append(draw_cell(left_x + 255, 147, "16", w=52, h=30, fill=ACCENT, stroke=POS, sw=2, tcolor=POS, bold=True))

    parts.append(text(left_x + 20, 208, "Рядок 3 (h₃=1):", size=12, anchor="start"))
    parts.append(draw_cell(left_x + 160, 192, "10", w=52, h=30, fill=FILL, tcolor=INK))
    parts.append(text(left_x + 230, 208, "→", size=14, bold=True))
    parts.append(draw_cell(left_x + 255, 192, "11", w=52, h=30, fill=ACCENT, stroke=POS, sw=2, tcolor=POS, bold=True))

    parts.append(text(left_x + 175, 258, "Результат: min(11, 16, 11) = 11", size=13, bold=True, color=INK))
    parts.append(text(left_x + 175, 283, "Шум у рядку 2 зріс з 15 до 16 даремно", size=12, color=POS))

    # Розділювач
    parts.append(line(440, 45, 440, 325, color=MUTED, sw=1.2, dash="4,4"))

    # Права колонка: Консервативне оновлення
    right_x = 470
    parts.append(text(right_x + 175, 55, "Консервативне оновлення (CU)", size=14, bold=True, color=FIELD))
    parts.append(text(right_x + 175, 75, "Інкремент лише тих, де C[j, h_j(x)] == поточний min", size=11, color=MUTED))

    parts.append(text(right_x + 20, 118, "Рядок 1 (h₁=2):", size=12, anchor="start"))
    parts.append(draw_cell(right_x + 160, 102, "10", w=52, h=30, fill=FILL, tcolor=INK))
    parts.append(text(right_x + 230, 118, "→", size=14, bold=True))
    parts.append(draw_cell(right_x + 255, 102, "11", w=52, h=30, fill=GREEN_BG, stroke=FIELD, sw=2, tcolor=FIELD, bold=True))

    parts.append(text(right_x + 20, 163, "Рядок 2 (h₂=5):", size=12, anchor="start"))
    parts.append(draw_cell(right_x + 160, 147, "15 (шум)", w=52, h=30, fill=FILL, tcolor=MUTED, tsize=10))
    parts.append(text(right_x + 230, 163, "→", size=14, bold=True))
    parts.append(draw_cell(right_x + 255, 147, "15", w=52, h=30, fill=FILL, stroke=MUTED, sw=1.5, tcolor=MUTED, bold=True))

    parts.append(text(right_x + 20, 208, "Рядок 3 (h₃=1):", size=12, anchor="start"))
    parts.append(draw_cell(right_x + 160, 192, "10", w=52, h=30, fill=FILL, tcolor=INK))
    parts.append(text(right_x + 230, 208, "→", size=14, bold=True))
    parts.append(draw_cell(right_x + 255, 192, "11", w=52, h=30, fill=GREEN_BG, stroke=FIELD, sw=2, tcolor=FIELD, bold=True))

    parts.append(text(right_x + 175, 258, "Результат: min(11, 15, 11) = 11", size=13, bold=True, color=INK))
    parts.append(text(right_x + 175, 283, "Шум у рядку 2 НЕ зріс (збережено 15)", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "conservative-update.svg"), W, H, *parts, title="Порівняння звичайного та консервативного оновлення")


# ── Фігура 3: Потоковий конвеєр Heavy Hitters ──────────────────────────────────
def fig_heavy_hitters():
    W, H = 880, 360
    parts = []

    # 1. Потік подій
    parts.append(rect(30, 115, 150, 85, fill=FILLED, stroke=NEG, sw=1.8, rx=6))
    parts.append(text(105, 140, "Потік подій", size=14, bold=True, color=NEG))
    parts.append(text(105, 163, "пакети / запити", size=12, color=MUTED))
    parts.append(text(105, 183, "(x, +c)", size=13, bold=True, color=INK))

    # Стрілка 1 -> 2
    parts.append(arrow(182, 157, 248, 157, color=LINE, sw=1.8))

    # 2. Count-Min Sketch
    parts.append(rect(250, 75, 225, 165, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    parts.append(text(362, 102, "Count-Min Sketch", size=15, bold=True, color=INK))
    parts.append(text(362, 125, "Матриця d × w", size=12, color=MUTED))
    parts.append(text(362, 155, "1. Оновлення лічильників", size=12, anchor="middle"))
    parts.append(text(362, 180, "2. Оцінка â[x] = min(...)", size=12, anchor="middle", bold=True))
    parts.append(text(362, 212, "Фіксована пам'ять O(d·w)", size=11, color=FIELD, bold=True))

    # Стрілка 2 -> 3
    parts.append(arrow(477, 157, 538, 157, color=LINE, sw=1.8))
    parts.append(text(508, 145, "â[x]", size=12, bold=True, color=POS))

    # 3. Фільтр та Min-Heap
    parts.append(rect(540, 75, 305, 165, fill=GREEN_BG, stroke=FIELD, sw=2, rx=8))
    parts.append(text(692, 102, "Трекер важких елементів (Top-K)", size=14, bold=True, color=FIELD))
    parts.append(text(692, 127, "Мін-купа розміру K (наприклад K = 100)", size=12, color=MUTED))
    parts.append(text(692, 155, "Якщо â[x] > min(Heap):", size=12, bold=True))
    parts.append(text(692, 180, "вставити або оновити частоту x", size=12))
    parts.append(text(692, 212, "Точний список найчастіших ключів", size=11, color=POS, bold=True))

    # Вихід внизу
    parts.append(arrow(692, 242, 692, 298, color=FIELD, sw=2))
    parts.append(rect(570, 300, 245, 42, fill=ACCENT, stroke=POS, sw=1.8, rx=6))
    parts.append(text(692, 326, "Звіт Heavy Hitters (DDoS, тренди)", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "heavy-hitters-stream.svg"), W, H, *parts, title="Архітектура виявлення важких елементів (Heavy Hitters) у потоці")


if __name__ == "__main__":
    fig_grid_update()
    fig_conservative_update()
    fig_heavy_hitters()
    print("All figures generated successfully.")
