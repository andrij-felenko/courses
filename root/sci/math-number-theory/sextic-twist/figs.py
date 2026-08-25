# -*- coding: utf-8 -*-
"""Фігури для теми «Шестикратний твіст (Sextic Twist)» (book/algorithms/complexity-computability/sextic-twist)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_twist_isomorphism():
    """fig1-twist-isomorphism.svg: Ізоморфізм шестикратного твісту між кривою над полем розширення та твістованою кривою."""
    W, H = 880, 420
    frags = []

    # Загальне тло
    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгебраїчний ізоморфізм шестикратного твісту (d = 6)", size=16, bold=True, color="#1e293b"))

    # Блок 1: Початкова крива над полем розширення E(F_{p^12})
    frags.append(rect(40, 70, 370, 160, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(225, 95, "Базова крива E / 𝔽ₚ: y² = x³ + b", size=13, bold=True, color=RED_S))
    frags.append(text(225, 118, "Група G₂ ⊂ E(𝔽ₚ₁₂)[r]", size=12, bold=True, color="#991b1b"))
    
    txt_orig = "Точка Q = (x, y) ∈ E(𝔽ₚ₁₂)\n• Розмір координат: 12 елементів 𝔽ₚ (384 байти)\n• Арифметика: множення над 𝔽ₚ₁₂\n• Висока обчислювальна складність"
    frags.append(fitbox(55, 135, 340, 80, txt_orig, size=11, fill="#ffffff", stroke="#fca5a5", color="#7f1d1d", rx=5))

    # Блок 2: Твістована крива E'(F_{p^2})
    frags.append(rect(470, 70, 370, 160, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(655, 95, "Твістована крива E' / 𝔽ₚ₂ (d = 6)", size=13, bold=True, color=GREEN_S))
    frags.append(text(655, 118, "Група G₂' ⊂ E'(𝔽ₚ₂)[r]", size=12, bold=True, color="#166534"))
    
    txt_twist = "Точка Q' = (x', y') ∈ E'(𝔽ₚ₂)\n• Розмір координат: 2 елементи 𝔽ₚ (64 байти)\n• D-type: y'² = x'³ + b/ξ | M-type: y'² = x'³ + b·ξ\n• Арифметика: швидкі операції в 𝔽ₚ₂"
    frags.append(fitbox(485, 135, 340, 80, txt_twist, size=11, fill="#ffffff", stroke="#86efac", color="#14532d", rx=5))

    # Відображення ізоморфізму (стрілки між блоками)
    frags.append(line(410, 130, 470, 130, color=BLUE_S, sw=2))
    frags.append(line(460, 124, 470, 130, color=BLUE_S, sw=2))
    frags.append(line(460, 136, 470, 130, color=BLUE_S, sw=2))
    frags.append(text(440, 115, "ψ⁻¹", size=13, bold=True, color=BLUE_S))

    frags.append(line(470, 170, 410, 170, color=PURPLE_S, sw=2))
    frags.append(line(420, 164, 410, 170, color=PURPLE_S, sw=2))
    frags.append(line(420, 176, 410, 170, color=PURPLE_S, sw=2))
    frags.append(text(440, 190, "ψ (розтвіст)", size=12, bold=True, color=PURPLE_S))

    # Нижній блок: Алгебраїчні вирази відображення
    frags.append(rect(40, 250, 800, 140, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(440, 275, "Формули розтвістування ψ: E'(𝔽ₚ₂) → E(𝔽ₚ₁₂) через елемент ω⁶ = ξ ∈ 𝔽ₚ₂", size=13, bold=True, color=PURPLE_S))

    txt_d = "D-type твіст (y'² = x'³ + b/ξ):\n(x, y) = ψ_D(x', y') = (x' · ω², y' · ω³)"
    frags.append(fitbox(60, 295, 360, 75, txt_d, size=11, fill="#ffffff", stroke=PURPLE_S, color="#581c87", rx=5))

    txt_m = "M-type твіст (y'² = x'³ + b·ξ):\n(x, y) = ψ_M(x', y') = (x' / ω², y' / ω³)"
    frags.append(fitbox(460, 295, 360, 75, txt_m, size=11, fill="#ffffff", stroke=PURPLE_S, color="#581c87", rx=5))

    render(os.path.join(IMG, "fig1-twist-isomorphism.svg"), W, H, *frags)


def fig_miller_tower_sparse():
    """fig2-miller-tower-sparse.svg: Вежа розширень полів та структура розрідженого елемента в алгоритмі Міллера."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Вежа розширень полів 𝔽ₚ → 𝔽ₚ₂ → 𝔽ₚ₆ → 𝔽ₚ₁₂ та розріджені множення", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Вежа полів
    frags.append(rect(40, 65, 360, 305, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(220, 90, "Вежа розширень полів (Tower Construction)", size=13, bold=True, color=BLUE_S))

    levels = [
        ("𝔽ₚ₁₂ = 𝔽ₚ₆[w] / (w² - v)", "Ступінь 12 | Цільова група Gₜ ⊂ 𝔽ₚ₁₂*", AMBER_F, AMBER_S),
        ("𝔽ₚ₆ = 𝔽ₚ₂[v] / (v³ - ξ)", "Ступінь 6 | Проміжне розширення", TEAL_F, TEAL_S),
        ("𝔽ₚ₂ = 𝔽ₚ[u] / (u² - β)", "Ступінь 2 | Поле точок твістованої кривої E'", GREEN_F, GREEN_S),
        ("𝔽ₚ (Базове поле)", "Ступінь 1 | Поле точок кривої E та G₁", GRAY_F, GRAY_S),
    ]

    y_pos = [115, 175, 235, 295]
    for (title, desc, fill_c, stroke_c), y in zip(levels, y_pos):
        txt = f"{title}\n{desc}"
        frags.append(fitbox(60, y, 320, 48, txt, size=11, fill=fill_c, stroke=stroke_c, color="#1e293b", rx=5))

    # Правий блок: Розріджений елемент прямої Міллера
    frags.append(rect(440, 65, 400, 305, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(640, 90, "Розріджена функція прямої l_{P, Q'}(T) ∈ 𝔽ₚ₁₂", size=13, bold=True, color=AMBER_S))

    txt_miller = "Обчислення прямої між P=(xₚ, yₚ) ∈ G₁ та Q'=(x', y') ∈ G₂':\n\nl_{P, Q'}(T) = c₀ + c₁ · w + c₃ · w³\n\n• c₀ ∈ 𝔽ₚ₂  (лінійний коефіцієнт)\n• c₁ ∈ 𝔽ₚ₂  (компонента y' · w³ розтвістована)\n• c₃ ∈ 𝔽ₚ₂  (компонента x' · w² розтвістована)\n• c₂ = c₄ = c₅ = 0 (9 із 12 коефіцієнтів дорівнюють 0!)"
    frags.append(fitbox(460, 110, 360, 155, txt_miller, size=11, fill="#ffffff", stroke="#fcd34d", color="#78350f", rx=5))

    txt_speedup = "Результат розрідженості (Sparse Multiplication):\n• Стандартне множення в 𝔽ₚ₁₂: 54 множення в 𝔽ₚ\n• Розріджене множення l_{P,Q'} · f: лише 13–18 множень в 𝔽ₚ\n• Прискорення крок за кроком в алгоритмі Міллера: > 3×"
    frags.append(fitbox(460, 275, 360, 80, txt_speedup, size=11, fill=GREEN_F, stroke=GREEN_S, color="#14532d", rx=5))

    render(os.path.join(IMG, "fig2-miller-tower-sparse.svg"), W, H, *frags)


def fig_g2_compression_speedup():
    """fig3-g2-compression-speedup.svg: Порівняння обсягу пам'яті та обчислювальної складності для різних ступенів твісту."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Вплив ступеня твісту d на розмір точок G₂ та обчислення", size=16, bold=True, color="#1e293b"))

    # Таблична порівняльна схема
    col_x = [40, 240, 440, 640]
    col_w = 180

    headers = [
        ("Без твісту (d = 1)", "Generic Curves", RED_F, RED_S),
        ("Квадратичний (d = 2)", "j = 1728 / generic", AMBER_F, AMBER_S),
        ("Кубічний (d = 3)", "j = 0 / 𝔽ₚ", TEAL_F, TEAL_S),
        ("Шестикратний (d = 6)", "j = 0 (BN, BLS12)", GREEN_F, GREEN_S),
    ]

    for (title, sub, f_c, s_c), x in zip(headers, col_x):
        frags.append(rect(x, 65, col_w, 60, fill=f_c, stroke=s_c, sw=1.5, rx=6))
        frags.append(text(x + col_w//2, 88, title, size=12, bold=True, color=s_c))
        frags.append(text(x + col_w//2, 108, sub, size=10, italic=True, color="#475569"))

    rows = [
        ("Поле точок G₂", ["𝔽ₚ₁₂", "𝔽ₚ₆", "𝔽ₚ₄", "𝔽ₚ₂"]),
        ("Розмір точки (BN254)", ["384 B", "192 B", "128 B", "64 B"]),
        ("Стиснена точка (BLS12-381)", ["576 B", "288 B", "192 B", "48 B"]),
        ("Множення в G₂", ["100% (база)", "~45% часу", "~30% часу", "~12% часу"]),
        ("Розріджене l_{P,Q}", ["Немає", "Часткове", "Часткове", "Максимальне"]),
    ]

    y_start = 140
    row_h = 42

    for r_idx, (r_name, vals) in enumerate(rows):
        y = y_start + r_idx * row_h
        bg = "#f1f5f9" if r_idx % 2 == 0 else "#ffffff"
        frags.append(rect(40, y, 780, row_h - 4, fill=bg, stroke="#e2e8f0", rx=4))
        
        for c_idx, val in enumerate(vals):
            x = col_x[c_idx]
            color = GREEN_S if c_idx == 3 else "#1e293b"
            bold = True if c_idx == 3 else False
            txt_cell = f"{r_name}:\n{val}"
            frags.append(fitbox(x + 5, y + 2, col_w - 10, row_h - 8, txt_cell, size=10, fill="none", stroke="none", color=color, bold=bold))

    txt_summary = "Ключовий висновок: Шестикратний твіст (d = 6) зменшує розмір координат у 6 разів і прискорює обчислення в G₂ майже на порядок, роблячи спарування BN254 та BLS12-381 придатними для реального часу та ZK-протоколів."
    frags.append(fitbox(40, y_start + len(rows)*row_h + 10, 780, 50, txt_summary, size=11, fill=BLUE_F, stroke=BLUE_S, color=BLUE_S, bold=True))

    render(os.path.join(IMG, "fig3-g2-compression-speedup.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_twist_isomorphism()
    fig_miller_tower_sparse()
    fig_g2_compression_speedup()
    print("Усі фігури успішно згенеровано.")
