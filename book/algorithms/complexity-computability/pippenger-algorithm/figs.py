# -*- coding: utf-8 -*-
"""
Генератор фігур для теми: Алгоритм Піппенджера (MSM)
Шлях: book/algorithms/complexity-computability/pippenger-algorithm
"""

import sys
import os

# Імпортуємо спільний svgkit з scripts/ (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_fig1_buckets():
    """Фігура 1: Віконне розбиття скалярів, кошики та накопичувальні суми (Running Sums)"""
    w, h = 860, 480
    frags = []

    # Заголовок блоків вікна скаляра
    frags.append(text(w / 2, 50, "1. Розбиття 256-бітного скаляра kᵢ на b вікон шириною c бітів", size=14, bold=True))

    # Стрічка бітів скаляра
    sw_x, sw_y = 70, 75
    box_w = 90
    box_h = 36
    labels = ["Вікно b−1\n[255..240]", "...", "Вікно j\n[kᵢ,ⱼ ∈ 0..2ᶜ−1]", "...", "Вікно 1\n[31..16]", "Вікно 0\n[15..0]"]
    colors = [FILL, FILL, "#e8f4fc", FILL, FILL, FILL]
    strokes = [LINE, MUTED, NEG, MUTED, LINE, LINE]

    for idx, (lbl, col, stk) in enumerate(zip(labels, colors, strokes)):
        bx = sw_x + idx * (box_w + 35)
        fb = fitbox(bx, sw_y, box_w, box_h, lbl, size=11, fill=col, stroke=stk, bold=(idx == 2))
        frags.append(fb)
        if idx < len(labels) - 1:
            frags.append(line(bx + box_w, sw_y + box_h / 2, bx + box_w + 35, sw_y + box_h / 2, color=MUTED, sw=1.5, dash="3,3"))

    # Стрілка вниз до кошиків вікна j
    frags.append(arrow(sw_x + 2 * (box_w + 35) + box_w / 2, sw_y + box_h + 5, sw_x + 2 * (box_w + 35) + box_w / 2, 160, color=NEG, sw=2))
    frags.append(text(w / 2, 150, "2. Розподіл n точок Pᵢ за значенням коефіцієнта u = kᵢ,ⱼ у 2ᶜ − 1 кошиків", size=13, bold=True))

    # Кошики
    b_y = 175
    b_w = 110
    b_h = 55
    buckets = [
        ("Кошик B₁", "∑ Pᵢ (kᵢ,ⱼ = 1)"),
        ("Кошик B₂", "∑ Pᵢ (kᵢ,ⱼ = 2)"),
        ("...", "..."),
        ("Кошик Bᵤ", "∑ Pᵢ (kᵢ,ⱼ = u)"),
        ("...", "..."),
        ("Кошик B₂ᶜ₋₁", "∑ Pᵢ (kᵢ,ⱼ = 2ᶜ−1)")
    ]

    for idx, (b_name, b_sum) in enumerate(buckets):
        bx = 50 + idx * (b_w + 22)
        fill_c = "#fef9e7" if "Bᵤ" in b_name else FILL
        strk_c = "#d97706" if "Bᵤ" in b_name else LINE
        fb = fitbox(bx, b_y, b_w, b_h, f"{b_name}\n{b_sum}", size=11, fill=fill_c, stroke=strk_c, bold=True)
        frags.append(fb)

    # Пояснення зворотних накопичувальних сум
    frags.append(text(w / 2, 265, "3. Зворотне сумування (Running Sums): Tᵥ = Tᵥ₊₁ + Bᵥ без скалярних множень", size=13, bold=True))

    # Блоки накопичувачів T_v
    t_y = 290
    t_w = 150
    t_h = 48
    t_blocks = [
        ("T₂ᶜ₋₁ = B₂ᶜ₋₁", 670, "#f3f4f6"),
        ("Tᵤ = Tᵤ₊₁ + Bᵤ", 440, "#eaf0fd"),
        ("T₁ = T₂ + B₁", 130, "#eaf0fd")
    ]

    for lbl, cx, f_col in t_blocks:
        tb, _, _ = textbox(cx, t_y + t_h / 2, lbl, size=12, pad=8, fill=f_col, stroke=NEG, bold=True)
        frags.append(tb)

    # Стрілки зворотного накопичення (справа наліво)
    frags.append(arrow(670 - t_w / 2, t_y + t_h / 2, 440 + t_w / 2 + 10, t_y + t_h / 2, color=POS, sw=2))
    frags.append(text(555, t_y + 15, "+ Bᵤ₊₁...B₂ᶜ₋₂", size=10, color=POS, bold=True))

    frags.append(arrow(440 - t_w / 2, t_y + t_h / 2, 130 + t_w / 2 + 10, t_y + t_h / 2, color=POS, sw=2))
    frags.append(text(285, t_y + 15, "+ B₁...Bᵤ₋₁", size=10, color=POS, bold=True))

    # Підсумковий блок результату вікна S_j
    res_y = 390
    tb_res, _, _ = textbox(w / 2, res_y + 25, "Результат вікна j:\nSⱼ = ∑ᵤ u·Bᵤ = ∑ᵥ Tᵥ  (потрібно лише 2ᶜ⁺¹ додавань)", size=13, pad=10, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(tb_res)

    # Стрілки зведення до підсумку
    frags.append(arrow(130, t_y + t_h + 5, w / 2 - 120, res_y + 10, color=FIELD, sw=1.8))
    frags.append(arrow(440, t_y + t_h + 5, w / 2, res_y + 5, color=FIELD, sw=1.8))
    frags.append(arrow(670, t_y + t_h + 5, w / 2 + 120, res_y + 10, color=FIELD, sw=1.8))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'pippenger-buckets.svg')
    render(out_path, w, h, *frags, title="Віконний розподіл по кошиках та обчислення суми вікна Sⱼ")
    print(f"Згенеровано: {out_path}")


def build_fig2_horner():
    """Фігура 2: Міжвіконна агрегація результатів за схемою Горнера"""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 48, "Міжвіконна схема Горнера: Q = 2ᶜ · ( ... (2ᶜ · S_{b−1} + S_{b−2}) ... ) + S₀", size=14, bold=True))

    # Ланцюжок віконних результатів
    nodes = [
        ("S_{b−1}\n(старше вікно)", 90, "#e8f4fc", NEG),
        ("S_{b−2}\n(вікно b−2)", 280, "#e8f4fc", NEG),
        ("S₁\n(вікно 1)", 510, "#e8f4fc", NEG),
        ("S₀\n(молодше вікно)", 710, "#e8f4fc", NEG)
    ]

    for lbl, cx, bg_col, stk_col in nodes:
        tb, _, _ = textbox(cx, 110, lbl, size=12, pad=8, fill=bg_col, stroke=stk_col, bold=True)
        frags.append(tb)

    # Проміжний акумулятор Q
    q_y = 240
    q_nodes = [
        ("Q₁ = S_{b−1}", 90),
        ("Q₂ = [2ᶜ]Q₁ + S_{b−2}", 280),
        ("Q_{b−1} = [2ᶜ]Q_{b−2} + S₁", 510),
        ("Q = [2ᶜ]Q_{b−1} + S₀", 710)
    ]

    for lbl, cx in q_nodes:
        tb, _, _ = textbox(cx, q_y, lbl, size=12, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
        frags.append(tb)

    # Стрілки зсуву та накопичення
    # 1 -> 2
    frags.append(arrow(90, 140, 90, q_y - 25, color=LINE, sw=1.8))
    frags.append(arrow(90 + 75, q_y, 280 - 100, q_y, color=POS, sw=2))
    frags.append(text(185, q_y - 12, "× 2ᶜ (c подвоєнь)", size=10, color=POS, bold=True))
    frags.append(arrow(280, 140, 280, q_y - 25, color=NEG, sw=1.8))
    frags.append(text(295, 185, "+", size=14, color=NEG, bold=True))

    # 2 -> ... -> 3
    frags.append(line(280 + 100, q_y, 360, q_y, color=POS, sw=2, dash="3,3"))
    frags.append(line(420, q_y, 510 - 110, q_y, color=POS, sw=2, dash="3,3"))
    frags.append(text(390, q_y - 5, "...", size=14, color=MUTED, bold=True))

    # 3 -> 4
    frags.append(arrow(510, 140, 510, q_y - 25, color=NEG, sw=1.8))
    frags.append(text(525, 185, "+", size=14, color=NEG, bold=True))
    frags.append(arrow(510 + 110, q_y, 710 - 95, q_y, color=POS, sw=2))
    frags.append(text(610, q_y - 12, "× 2ᶜ (c подвоєнь)", size=10, color=POS, bold=True))
    frags.append(arrow(710, 140, 710, q_y - 25, color=NEG, sw=1.8))
    frags.append(text(725, 185, "+", size=14, color=NEG, bold=True))

    # Підсумкова стрілка
    tb_final, _, _ = textbox(w / 2, 315, "Загальна кількість операцій подвоєння для всіх b вікон: (b − 1) · c ≈ λ подвоєнь", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(tb_final)

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'pippenger-horner.svg')
    render(out_path, w, h, *frags, title="Агрегація вікон за Горнером: масштабування на 2ᶜ та накопичення")
    print(f"Згенеровано: {out_path}")


def build_fig3_complexity():
    """Фігура 3: Порівняння кількості групових операцій та оптимум ширини вікна c"""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 48, "Асимптотична складність MSM: Наївний метод vs Штраус vs Піппенджер (λ = 256)", size=14, bold=True))

    # Ліва панель: графік порівняння зростання операцій
    p1_x, p1_y, p1_w, p1_h = 50, 75, 420, 310
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke=MUTED, sw=1, rx=4))
    frags.append(text(p1_x + p1_w / 2, p1_y + 22, "Кількість групових операцій vs Розмір n", size=12, bold=True))

    # Вісі графіка
    gx, gy = p1_x + 55, p1_y + p1_h - 45
    frags.append(line(gx, gy, gx + 340, gy, color=LINE, sw=1.5))
    frags.append(line(gx, gy, gx, gy - 210, color=LINE, sw=1.5))
    frags.append(text(gx + 340, gy + 20, "n (точок)", size=10, bold=True, anchor="end"))
    frags.append(text(gx - 10, gy - 210, "Операції", size=10, bold=True, anchor="end"))

    # Позначки по X: 2¹⁰, 2¹⁴, 2¹⁸, 2²²
    x_steps = [("2¹⁰", 60), ("2¹⁴", 140), ("2¹⁸", 220), ("2²²", 300)]
    for lbl, dx in x_steps:
        frags.append(line(gx + dx, gy, gx + dx, gy + 4, color=LINE, sw=1))
        frags.append(text(gx + dx, gy + 16, lbl, size=9))

    # Крива 1: Наївний O(n·λ) - крута пряма вгору
    frags.append(line(gx + 20, gy - 25, gx + 300, gy - 200, color=POS, sw=2.5))
    frags.append(text(gx + 220, gy - 165, "Наївний O(n·λ)", size=11, color=POS, bold=True))

    # Крива 2: Штраус (фіксоване вікно)
    frags.append(line(gx + 20, gy - 18, gx + 300, gy - 120, color="#d97706", sw=2, dash="4,2"))
    frags.append(text(gx + 240, gy - 105, "Штраус O(λ·n/c)", size=10, color="#d97706", bold=True))

    # Крива 3: Піппенджер O(n·λ / log n) з адаптивним c
    # Згинається повільніше
    frags.append(line(gx + 20, gy - 12, gx + 140, gy - 38, color=FIELD, sw=2.5))
    frags.append(line(gx + 140, gy - 38, gx + 300, gy - 75, color=FIELD, sw=2.5))
    frags.append(text(gx + 250, gy - 55, "Піппенджер O(n·λ/ln n)", size=11, color=FIELD, bold=True))

    # Права панель: Таблиця оптимальних значень c(n) для λ = 256
    p2_x, p2_y, p2_w, p2_h = 490, 75, 300, 310
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "Оптимальне вікно c для λ = 256", size=12, bold=True))

    rows = [
        ("n = 2¹⁰ (1024)", "c = 8 бітів", "b = 32 вікна"),
        ("n = 2¹⁴ (16 тис.)", "c = 11 бітів", "b = 24 вікна"),
        ("n = 2¹⁶ (65 тис.)", "c = 13 бітів", "b = 20 вікон"),
        ("n = 2¹⁸ (262 тис.)", "c = 14 бітів", "b = 19 вікон"),
        ("n = 2²⁰ (1 млн)", "c = 16 бітів", "b = 16 вікон"),
        ("n = 2²² (4 млн)", "c = 17 бітів", "b = 16 вікон"),
        ("n = 2²⁴ (16 млн)", "c = 19 бітів", "b = 14 вікон")
    ]

    for idx, (col1, col2, col3) in enumerate(rows):
        ry = p2_y + 55 + idx * 34
        bg_r = "#f4f6f8" if idx % 2 == 0 else "#ffffff"
        frags.append(rect(p2_x + 8, ry - 14, p2_w - 16, 28, fill=bg_r, stroke="none", rx=2))
        frags.append(text(p2_x + 20, ry + 4, col1, size=11, anchor="start", bold=True))
        frags.append(text(p2_x + 160, ry + 4, col2, size=11, anchor="middle", color=NEG))
        frags.append(text(p2_x + p2_w - 20, ry + 4, col3, size=11, anchor="end", color=MUTED))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'msm-complexity-tradeoff.svg')
    render(out_path, w, h, *frags, title="Складність та оптимальний вибір ширини вікна c")
    print(f"Згенеровано: {out_path}")


if __name__ == '__main__':
    build_fig1_buckets()
    build_fig2_horner()
    build_fig3_complexity()
