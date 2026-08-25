# -*- coding: utf-8 -*-
"""Фігури для теми «Символ Кронекера».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os

# Чотири рівні вгору від book/math/algebra/kronecker-delta до scripts/ у корені репо
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
GRAY_FILL   = "#f8fafc"
MUTED_BORDER = "#cbd5e1"
HIGHLIGHT_BORDER = "#2563eb"

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — Фільтруюча властивість суми: ∑ a_j · δ_3j = a_3
# ─────────────────────────────────────────────────────────────────────────────
def fig_sifting_property():
    W, H = 820, 360
    p = []

    # Заголовок
    p.append(text(W/2, 26, "Фільтруюча властивість символу Кронекера в сумах", size=16, bold=True))
    p.append(text(W/2, 46, "Усі доданки з j ≠ i множаться на нуль і гаснуть; виживає єдиний доданок із j = i", size=12, color=MUTED, italic=True))

    # Стовпчики доданків j = 1..5
    elements = [
        ("j = 1", "a₁", "δ₃₁ = 0", "a₁ · 0 = 0", False),
        ("j = 2", "a₂", "δ₃₂ = 0", "a₂ · 0 = 0", False),
        ("j = 3", "a₃", "δ₃₃ = 1", "a₃ · 1 = a₃", True),
        ("j = 4", "a₄", "δ₃₄ = 0", "a₄ · 0 = 0", False),
        ("j = 5", "a₅", "δ₃₅ = 0", "a₅ · 0 = 0", False),
    ]

    col_w = 120
    gap = 18
    total_w = 5 * col_w + 4 * gap
    start_x = (W - total_w) / 2

    y_top = 75

    for idx, (j_label, a_label, delta_label, res_label, is_hit) in enumerate(elements):
        cx = start_x + idx * (col_w + gap) + col_w / 2
        bx = start_x + idx * (col_w + gap)

        fill_col = GREEN_FILL if is_hit else GRAY_FILL
        stroke_col = FIELD if is_hit else MUTED_BORDER
        sw = 2.0 if is_hit else 1.0

        # Рамка стовпчика
        p.append(rect(bx, y_top, col_w, 175, fill=fill_col, stroke=stroke_col, sw=sw, rx=8))

        # Заголовок індексу j
        p.append(text(cx, y_top + 22, j_label, size=13, bold=True, color=POS if is_hit else INK))
        p.append(line(bx + 10, y_top + 32, bx + col_w - 10, y_top + 32, color=stroke_col, sw=1.0))

        # Компонента вектора a_j
        p.append(text(cx, y_top + 58, a_label, size=16, bold=True, color=INK))

        # Значення символу Кронекера δ_3j
        p.append(text(cx, y_top + 88, "×", size=13, color=MUTED))
        p.append(text(cx, y_top + 112, delta_label, size=13, bold=True, color=FIELD if is_hit else MUTED))

        # Результат множення
        p.append(line(bx + 10, y_top + 128, bx + col_w - 10, y_top + 128, color=stroke_col, sw=1.0))
        p.append(text(cx, y_top + 152, res_label, size=13, bold=True, color=FIELD if is_hit else MUTED))

        # Стрілка вниз до підсумку
        arrow_col = FIELD if is_hit else "#94a3b8"
        p.append(line(cx, y_top + 175, cx, y_top + 205, color=arrow_col, sw=2.0 if is_hit else 1.0))

    # Спільний блок суми внизу
    sum_box_y = 285
    sum_box_w = 460
    sum_box_x = (W - sum_box_w) / 2
    p.append(rect(sum_box_x, sum_box_y, sum_box_w, 54, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(W/2, sum_box_y + 24, "Сума:  ∑ⱼ₌₁⁵ aⱼ · δ₃ⱼ = 0 + 0 + a₃ + 0 + 0 = a₃", size=14, bold=True, color=NEG))
    p.append(text(W/2, sum_box_y + 44, "Символ Кронекера діє як селекторний фільтр потрібного індексу", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "sifting-property.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — Ортонормований базис: e_i · e_j = δ_ij
# ─────────────────────────────────────────────────────────────────────────────
def fig_orthonormal_basis():
    W, H = 820, 370
    p = []

    p.append(text(W/2, 26, "Ортонормований базис у просторі ℝ³", size=16, bold=True))
    p.append(text(W/2, 46, "Взаємна перпендикулярність і одинична довжина векторів компактно задаються через eᵢ · eⱼ = δᵢⱼ", size=12, color=MUTED, italic=True))

    # Ліва частина — геометричний рисунок осей
    ox, oy = 210, 225

    # Осі базису
    # e_1 (вісь X, вправо-вниз під кутом)
    p.append(line(ox, oy, ox + 115, oy + 45, color=POS, sw=2.5))
    p.append(circle(ox + 115, oy + 45, 3.5, fill=POS))
    p.append(text(ox + 130, oy + 48, "e₁", size=15, bold=True, color=POS))
    p.append(text(ox + 75, oy + 48, "|e₁| = 1", size=11, color=MUTED))

    # e_2 (вісь Y, вправо)
    p.append(line(ox, oy, ox + 135, oy - 25, color=FIELD, sw=2.5))
    p.append(circle(ox + 135, oy - 25, 3.5, fill=FIELD))
    p.append(text(ox + 152, oy - 23, "e₂", size=15, bold=True, color=FIELD))
    p.append(text(ox + 90, oy - 28, "|e₂| = 1", size=11, color=MUTED))

    # e_3 (вісь Z, вгору)
    p.append(line(ox, oy, ox, oy - 135, color=NEG, sw=2.5))
    p.append(circle(ox, oy - 135, 3.5, fill=NEG))
    p.append(text(ox - 16, oy - 135, "e₃", size=15, bold=True, color=NEG))
    p.append(text(ox - 35, oy - 70, "|e₃| = 1", size=11, color=MUTED))

    # Позначки прямих кутів між осями
    # Між e_3 та e_2
    p.append(line(ox, oy - 25, ox + 22, oy - 29, color=LINE, sw=1.0))
    p.append(line(ox + 22, oy - 29, ox + 22, oy - 4, color=LINE, sw=1.0))
    p.append(circle(ox + 11, oy - 16, 1.5, fill=LINE))

    # Між e_3 та e_1
    p.append(line(ox, oy - 25, ox + 18, oy - 18, color=LINE, sw=1.0))
    p.append(line(ox + 18, oy - 18, ox + 18, oy + 7, color=LINE, sw=1.0))

    # Початок координат O
    p.append(circle(ox, oy, 4, fill=INK))
    p.append(text(ox - 14, oy + 16, "O", size=13, bold=True))

    # Права частина — таблиця скалярних добутків та матриця Грама
    rx = 425
    ry = 80
    rw = 360
    rh = 250
    p.append(rect(rx, ry, rw, rh, fill=GRAY_FILL, stroke=MUTED_BORDER, sw=1.2, rx=8))

    p.append(text(rx + rw/2, ry + 26, "Матриця скалярних добутків Gᵢⱼ = eᵢ · eⱼ", size=13, bold=True))

    # Формула з фігурною дужкою
    p.append(text(rx + rw/2, ry + 56, "eᵢ · eⱼ = δᵢⱼ = { 1,  якщо i = j (довжина)", size=12, bold=True, color=FIELD))
    p.append(text(rx + rw/2 + 37, ry + 76, "{ 0,  якщо i ≠ j (перпендикулярність)", size=12, bold=True, color=POS))

    # Таблиця-матриця
    tbl_x = rx + 35
    tbl_y = ry + 95
    p.append(rect(tbl_x, tbl_y, 290, 115, fill=BG, stroke=LINE, sw=1.2, rx=6))

    headers = ["·", "e₁", "e₂", "e₃"]
    for j, h in enumerate(headers):
        hx = tbl_x + 35 + j * 65
        p.append(text(hx, tbl_y + 22, h, size=12, bold=True, color=INK if j == 0 else (POS if j==1 else (FIELD if j==2 else NEG))))

    p.append(line(tbl_x + 10, tbl_y + 30, tbl_x + 280, tbl_y + 30, color=MUTED_BORDER, sw=1.0))
    p.append(line(tbl_x + 65, tbl_y + 8, tbl_x + 65, tbl_y + 105, color=MUTED_BORDER, sw=1.0))

    matrix_rows = [
        ("e₁", ["1", "0", "0"], POS),
        ("e₂", ["0", "1", "0"], FIELD),
        ("e₃", ["0", "0", "1"], NEG),
    ]

    for i, (rlabel, row_vals, rcol) in enumerate(matrix_rows):
        cy_row = tbl_y + 52 + i * 25
        p.append(text(tbl_x + 35, cy_row, rlabel, size=12, bold=True, color=rcol))
        for j, val in enumerate(row_vals):
            vx = tbl_x + 100 + j * 65
            is_diag = (i == j)
            p.append(text(vx, cy_row, val, size=13, bold=is_diag, color=FIELD if is_diag else MUTED))

    p.append(text(rx + rw/2, ry + 230, "Одинична матриця Грама гарантує збереження довжин і кутів", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "orthonormal-basis.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — Одинична матриця та змішаний тензор δ^i_j
# ─────────────────────────────────────────────────────────────────────────────
def fig_tensor_delta_matrix():
    W, H = 820, 360
    p = []

    p.append(text(W/2, 26, "Символ Кронекера як одинична матриця та змішаний тензор", size=16, bold=True))
    p.append(text(W/2, 46, "Змішаний тензор δⁱ_ⱼ типу (1,1) є абсолютно інваріантним оператором тотожного перетворення", size=12, color=MUTED, italic=True))

    # Лівий блок — Матриця I_3
    bx1 = 45
    by = 75
    bw1 = 330
    bh = 250
    p.append(rect(bx1, by, bw1, bh, fill=GRAY_FILL, stroke=MUTED_BORDER, sw=1.2, rx=8))

    p.append(text(bx1 + bw1/2, by + 26, "Одинична матриця (I)ᵢⱼ = δᵢⱼ", size=14, bold=True))
    p.append(text(bx1 + bw1/2, by + 46, "Рядки i, стовпчики j", size=12, color=MUTED, italic=True))

    # Матриця з круглими дужками
    mx = bx1 + 65
    my = by + 65
    mw = 200
    mh = 110

    # Прямі дужки матриці [ ]
    p.append(line(mx + 15, my, mx + 5, my, color=INK, sw=1.8))
    p.append(line(mx + 5, my, mx + 5, my + mh, color=INK, sw=1.8))
    p.append(line(mx + 5, my + mh, mx + 15, my + mh, color=INK, sw=1.8))

    p.append(line(mx + mw - 15, my, mx + mw - 5, my, color=INK, sw=1.8))
    p.append(line(mx + mw - 5, my, mx + mw - 5, my + mh, color=INK, sw=1.8))
    p.append(line(mx + mw - 5, my + mh, mx + mw - 15, my + mh, color=INK, sw=1.8))

    mat_entries = [
        ["1", "0", "0"],
        ["0", "1", "0"],
        ["0", "0", "1"]
    ]

    for r in range(3):
        for c in range(3):
            ex = mx + 45 + c * 55
            ey = my + 25 + r * 35
            val = mat_entries[r][c]
            is_diag = (r == c)
            if is_diag:
                p.append(rect(ex - 16, ey - 14, 32, 22, fill=GREEN_FILL, stroke=FIELD, sw=1.2, rx=4))
            p.append(text(ex, ey + 2, val, size=14, bold=is_diag, color=FIELD if is_diag else MUTED))

    p.append(text(bx1 + bw1/2, by + 205, "Слід матриці: tr(I) = ∑ᵢ δᵢᵢ = 1 + 1 + 1 = 3", size=12, bold=True, color=POS))
    p.append(text(bx1 + bw1/2, by + 228, "Слід дорівнює розмірності простору n", size=11, color=MUTED, italic=True))

    # Правий блок — Тензорне перетворення при заміні базису
    bx2 = 415
    bw2 = 360
    p.append(rect(bx2, by, bw2, bh, fill=BLUE_FILL, stroke=NEG, sw=1.2, rx=8))

    p.append(text(bx2 + bw2/2, by + 26, "Тензорний закон заміни базису", size=14, bold=True, color=NEG))
    p.append(text(bx2 + bw2/2, by + 46, "Пряма матриця переходу L та обернена L⁻¹", size=12, color=MUTED, italic=True))

    # Формули в рамці
    fx = bx2 + 20
    fy = by + 65
    fw = bw2 - 40
    fh = 120
    p.append(rect(fx, fy, fw, fh, fill=BG, stroke=MUTED_BORDER, sw=1.0, rx=6))

    p.append(text(bx2 + bw2/2, fy + 26, "δ'ⁱ_ⱼ = Lⁱ_p · (L⁻¹)ᵍ_ⱼ · δᵖ_ᵍ", size=13, bold=True))
    p.append(text(bx2 + bw2/2, fy + 52, "= Lⁱ_p · (L⁻¹)ᵖ_ⱼ        [згортка за g]", size=12, color=MUTED))
    p.append(text(bx2 + bw2/2, fy + 78, "= (L · L⁻¹)ⁱ_ⱼ           [добуток матриць]", size=12, color=MUTED))
    p.append(text(bx2 + bw2/2, fy + 104, "= δⁱ_ⱼ                   [інваріантність!]", size=13, bold=True, color=FIELD))

    p.append(text(bx2 + bw2/2, by + 215, "Змішаний символ δⁱ_ⱼ не змінює своїх значень", size=12, bold=True, color=INK))
    p.append(text(bx2 + bw2/2, by + 234, "у жодній довільній системі координат", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "tensor-delta-matrix.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 — Згортка Епсилон-Дельта: ε_ijk · ε_imn = δ_jm · δ_kn - δ_jn · δ_km
# ─────────────────────────────────────────────────────────────────────────────
def fig_epsilon_delta_contraction():
    W, H = 820, 360
    p = []

    p.append(text(W/2, 26, "Тотожність Епсилон-Дельта та векторні добутки", size=16, bold=True))
    p.append(text(W/2, 46, "Згортка за спільним індексом i виражає векторний добуток через різницю паралельних і перехресних проєкцій", size=12, color=MUTED, italic=True))

    # Центральна формула вгорі
    f_box_x = 110
    f_box_y = 68
    f_box_w = 600
    f_box_h = 48
    p.append(rect(f_box_x, f_box_y, f_box_w, f_box_h, fill=PURPLE_FILL, stroke="#7c3aed", sw=1.5, rx=6))
    p.append(text(W/2, f_box_y + 30, "∑ᵢ εᵢⱼₖ · εᵢₘₙ = δⱼₘ · δₖₙ − δⱼₙ · δₖₘ", size=15, bold=True, color="#5b21b6"))

    # Лівий блок — комбінаторна структура визначника 2x2
    bx1 = 60
    by = 135
    bw1 = 330
    bh = 195
    p.append(rect(bx1, by, bw1, bh, fill=GRAY_FILL, stroke=MUTED_BORDER, sw=1.2, rx=8))

    p.append(text(bx1 + bw1/2, by + 24, "Визначник 2×2 з дельт Кронекера", size=13, bold=True))

    # Визначник матриці
    dx = bx1 + 65
    dy = by + 45
    dw = 200
    dh = 75

    p.append(line(dx + 25, dy, dx + 25, dy + dh, color=INK, sw=1.8))
    p.append(line(dx + dw - 25, dy, dx + dw - 25, dy + dh, color=INK, sw=1.8))

    p.append(text(dx + 65, dy + 28, "δⱼₘ", size=13, bold=True, color=FIELD))
    p.append(text(dx + 135, dy + 28, "δⱼₙ", size=13, bold=True, color=POS))
    p.append(text(dx + 65, dy + 62, "δₖₘ", size=13, bold=True, color=POS))
    p.append(text(dx + 135, dy + 62, "δₖₙ", size=13, bold=True, color=FIELD))

    # Діагональні стрілки-підказки
    p.append(text(bx1 + bw1/2, by + 145, "Головна діагональ: + (δⱼₘ · δₖₙ)", size=12, bold=True, color=FIELD))
    p.append(text(bx1 + bw1/2, by + 170, "Побічна діагональ: − (δⱼₙ · δₖₘ)", size=12, bold=True, color=POS))

    # Правий блок — Геометричний наслідок (правило BAC-CAB)
    bx2 = 430
    bw2 = 330
    p.append(rect(bx2, by, bw2, bh, fill=ORANGE_FILL, stroke=POS, sw=1.2, rx=8))

    p.append(text(bx2 + bw2/2, by + 24, "Подвійний векторний добуток (BAC-CAB)", size=13, bold=True, color=POS))

    # Блок формули векторного добутку
    p.append(rect(bx2 + 20, by + 45, bw2 - 40, 52, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(bx2 + bw2/2, by + 76, "a × (b × c) = b · (a · c) − c · (a · b)", size=13, bold=True, color=INK))

    p.append(text(bx2 + bw2/2, by + 125, "Зв'язок доданків із символами Кронекера:", size=11, color=MUTED, italic=True))
    p.append(text(bx2 + bw2/2, by + 150, "δⱼₘ · δₖₙ  ⟶  bⱼ · (aₖ · cₖ) = b · (a · c)", size=12, bold=True, color=FIELD))
    p.append(text(bx2 + bw2/2, by + 175, "δⱼₙ · δₖₘ  ⟶  cⱼ · (aₖ · bₖ) = c · (a · b)", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "epsilon-delta-contraction.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sifting_property()
    fig_orthonormal_basis()
    fig_tensor_delta_matrix()
    fig_epsilon_delta_contraction()
    print("Всі 4 фігури згенеровано успішно.")
