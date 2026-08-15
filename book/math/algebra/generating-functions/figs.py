# -*- coding: utf-8 -*-
"""Фігури для статті «Твірні функції: як упаковувати послідовності в алгебру».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os

# Шлях до scripts/ у корені репо (чотири рівні вгору від book/math/algebra/generating-functions)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
GREEN_FILL  = "#eafaf1"
BLUE_FILL   = "#eaf0fd"
ORANGE_FILL = "#fdf1e5"
PURPLE_FILL = "#f3e8ff"
GRAY_FILL   = "#f4f6f8"

# ─────────────────────────────────────────────────────────────────────────
# Фігура 1 — Упаковка послідовності в твірну функцію (гачки x^n)
# ─────────────────────────────────────────────────────────────────────────
def fig_sequence_package():
    W, H = 820, 360
    p = []
    
    p.append(text(W/2, 28, "Упаковка послідовності в твірну функцію A(x)", size=17, bold=True))
    p.append(text(W/2, 50, "Формальна змінна xⁿ слугує покажчиком позиції n для коефіцієнта aₙ", size=13, color=MUTED, italic=True))
    
    # Вектор послідовності зверху
    p.append(text(80, 95, "Послідовність:", size=14, bold=True, anchor="start"))
    
    terms = [("a₀", "n = 0"), ("a₁", "n = 1"), ("a₂", "n = 2"), ("a₃", "n = 3"), ("a₄", "n = 4"), ("…", "n → ∞")]
    box_w = 80
    gap = 20
    start_x = 230
    y_seq = 80
    
    for i, (val, label) in enumerate(terms):
        bx = start_x + i * (box_w + gap)
        fill_clr = ORANGE_FILL if i < 5 else GRAY_FILL
        stroke_clr = POS if i < 5 else MUTED
        
        p.append(rect(bx, y_seq, box_w, 42, fill=fill_clr, stroke=stroke_clr, sw=1.5, rx=6))
        p.append(text(bx + box_w/2, y_seq + 26, val, size=16, bold=True))
        p.append(text(bx + box_w/2, y_seq - 8, label, size=11, color=MUTED))
        
        if i < 5:
            # Стрілка вниз до гачка x^n
            p.append(line(bx + box_w/2, y_seq + 42, bx + box_w/2, y_seq + 95, color=LINE, sw=1.5, dash="3 3"))
            
            # Гачок x^i
            p.append(rect(bx, y_seq + 95, box_w, 36, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
            p.append(text(bx + box_w/2, y_seq + 118, f"× x^{i}" if i > 0 else "× 1 (x⁰)", size=13, bold=True, color=NEG))
            
            # Знак додавання між членами
            if i < 4:
                p.append(text(bx + box_w + gap/2, y_seq + 118, "+", size=18, bold=True, color=POS))
        else:
            p.append(text(bx + box_w/2, y_seq + 118, "+  …", size=15, bold=True))

    # Нижній результуючий блок ряду
    y_res = 235
    p.append(rect(start_x, y_res, 580, 65, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(start_x + 290, y_res + 26, "Формальний степеневий ряд A(x):", size=13, color=MUTED))
    p.append(text(start_x + 290, y_res + 48, "A(x) = a₀ + a₁·x + a₂·x² + a₃·x³ + a₄·x⁴ + …", size=16, bold=True, color=FIELD))

    render(os.path.join(IMG, "ogf-sequence-package.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — Дискретна згортка: множення двох твірних функцій
# ─────────────────────────────────────────────────────────────────────────
def fig_convolution():
    W, H = 820, 420
    p = []

    p.append(text(W/2, 28, "Множення рядів C(x) = A(x)·B(x) як згортка коефіцієнтів", size=17, bold=True))
    p.append(text(W/2, 50, "Коефіцієнт cₙ утворюється сумою всіх добутків aₖ·bₙ₋ₖ, де індекси в сумі дають n", size=13, color=MUTED, italic=True))

    # Таблиця сітки добутків
    x0, y0 = 180, 100
    cell_w, cell_h = 100, 44
    
    a_terms = ["a₀", "a₁", "a₂", "a₃"]
    b_terms = ["b₀", "b₁", "b₂", "b₃"]
    
    # Заголовки B по горизонталі
    p.append(text(x0 - 45, y0 - 15, "A \\ B", size=13, bold=True, color=MUTED))
    for j, b_val in enumerate(b_terms):
        px = x0 + j * cell_w
        p.append(rect(px, y0 - 32, cell_w - 6, 30, fill=BLUE_FILL, stroke=NEG, sw=1.2, rx=4))
        p.append(text(px + (cell_w - 6)/2, y0 - 12, f"{b_val}·x^{j}", size=13, bold=True, color=NEG))

    # Заголовки A по вертикалі
    for i, a_val in enumerate(a_terms):
        py = y0 + i * cell_h
        p.append(rect(x0 - 120, py, 110, cell_h - 6, fill=ORANGE_FILL, stroke=POS, sw=1.2, rx=4))
        p.append(text(x0 - 65, py + 24, f"{a_val}·x^{i}", size=13, bold=True, color=POS))

    # Клітинки сітки
    # Діагональ n = 2: (0,2), (1,1), (2,0)
    for i in range(4):
        for j in range(4):
            px = x0 + j * cell_w
            py = y0 + i * cell_h
            n_deg = i + j
            
            # Підсвічуємо діагональ n = 2
            if n_deg == 2:
                fill_c = GREEN_FILL
                stroke_c = FIELD
                sw_c = 2.0
            else:
                fill_c = BG
                stroke_c = "#d1d5db"
                sw_c = 1.0
                
            p.append(rect(px, py, cell_w - 6, cell_h - 6, fill=fill_c, stroke=stroke_c, sw=sw_c, rx=4))
            p.append(text(px + (cell_w - 6)/2, py + 24, f"{a_terms[i]}·{b_terms[j]}", size=13, bold=(n_deg == 2)))

    # Пояснення підсвіченої діагоналі n = 2
    y_info = y0 + 4 * cell_h + 20
    p.append(rect(x0 - 120, y_info, 690, 58, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(x0 + 225, y_info + 23, "Коефіцієнт c₂ при x² (діагональ i + j = 2):", size=13, bold=True, color=FIELD))
    p.append(text(x0 + 225, y_info + 44, "c₂ = a₀·b₂ + a₁·b₁ + a₂·b₀  =  ∑ₖ₌₀² aₖ·b₂₋ₖ", size=15, bold=True))

    render(os.path.join(IMG, "convolution-product.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — Оператор зсуву й зведення рекурентності Фібоначчі
# ─────────────────────────────────────────────────────────────────────────
def fig_fibonacci_shift():
    W, H = 840, 380
    p = []

    p.append(text(W/2, 28, "Алгебраїчне зведення рекурентності Фібоначчі", size=17, bold=True))
    p.append(text(W/2, 50, "Множення на x та x² зсуває члени ряду; віднімання гасить усі члени для n ≥ 2", size=13, color=MUTED, italic=True))

    x0 = 60
    y0 = 85
    row_h = 42

    rows = [
        ("F(x)",       "=", ["F₀", "F₁·x", "F₂·x²", "F₃·x³", "F₄·x⁴", "…"], BG, LINE),
        ("− x·F(x)",   "=", ["",   "−F₀·x", "−F₁·x²", "−F₂·x³", "−F₃·x⁴", "…"], ORANGE_FILL, POS),
        ("− x²·F(x)",  "=", ["",   "",      "−F₀·x²", "−F₁·x³", "−F₂·x⁴", "…"], ORANGE_FILL, POS),
    ]

    col_w = 95
    
    for r_idx, (label, eq, vals, f_clr, s_clr) in enumerate(rows):
        py = y0 + r_idx * row_h
        p.append(text(x0 + 60, py + 24, label, size=14, bold=True, anchor="end", color=s_clr if s_clr != LINE else INK))
        p.append(text(x0 + 80, py + 24, eq, size=14, bold=True))
        
        for c_idx, val in enumerate(vals):
            px = x0 + 100 + c_idx * col_w
            if val:
                p.append(rect(px, py, col_w - 8, row_h - 8, fill=f_clr, stroke=s_clr, sw=1.2, rx=4))
                p.append(text(px + (col_w - 8)/2, py + 22, val, size=13))

    # Горизонтальна лінія сумування
    y_sum_line = y0 + 3 * row_h + 5
    p.append(line(x0 + 10, y_sum_line, x0 + 740, y_sum_line, color=INK, sw=2))

    # Результат після додавання всіх трьох рядків
    y_res = y_sum_line + 15
    res_vals = ["0", "1·x", "0", "0", "0", "0"]
    
    p.append(text(x0 + 60, y_res + 28, "(1−x−x²)·F(x)", size=14, bold=True, anchor="end", color=FIELD))
    p.append(text(x0 + 80, y_res + 28, "=", size=14, bold=True))

    for c_idx, val in enumerate(res_vals):
        px = x0 + 100 + c_idx * col_w
        fill_c = GREEN_FILL if c_idx == 1 else GRAY_FILL
        stroke_c = FIELD if c_idx == 1 else MUTED
        p.append(rect(px, y_res + 4, col_w - 8, 38, fill=fill_c, stroke=stroke_c, sw=1.5, rx=4))
        p.append(text(px + (col_w - 8)/2, y_res + 26, val, size=14, bold=(c_idx == 1), color=FIELD if c_idx == 1 else MUTED))

    # Заключний висновок праворуч або знизу
    y_conc = y_res + 60
    p.append(rect(x0 + 100, y_conc, 560, 48, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=6))
    p.append(text(x0 + 380, y_conc + 28, "(1 − x − x²) · F(x) = x   ⇒   F(x) = x / (1 − x − x²)", size=16, bold=True, color=FIELD))

    render(os.path.join(IMG, "fibonacci-recurrence-shift.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sequence_package()
    fig_convolution()
    fig_fibonacci_shift()
    print("Успішно згенеровано 3 фігури у ./img/")
