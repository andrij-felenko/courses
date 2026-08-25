# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. fig-mobius-lattice-cancel: Взаємне скасування коефіцієнтів для n=30
def fig_mobius_lattice_cancel():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 35, "Механізм взаємного скасування коефіцієнтів Мьобіуса для n = 30", size=16, bold=True))
    p.append(text(W / 2, 58, "Розгортання f(30) = ∑_{d|30} μ(30/d) · g(d) через значення f(k)", size=13, color=MUTED))

    # Таблиця доданків g(d) та їхнього внеску
    divs_data = [
        (30, "g(30)", "μ(1) = +1", "+1 · [f(1)+f(2)+f(3)+f(5)+f(6)+f(10)+f(15)+f(30)]", "#eafaf0", FIELD),
        (15, "g(15)", "μ(2) = -1", "-1 · [f(1)+f(3)+f(5)+f(15)]", "#fff5f5", "#e53e3e"),
        (10, "g(10)", "μ(3) = -1", "-1 · [f(1)+f(2)+f(5)+f(10)]", "#fff5f5", "#e53e3e"),
        (6,  "g(6)",  "μ(5) = -1", "-1 · [f(1)+f(2)+f(3)+f(6)]",  "#fff5f5", "#e53e3e"),
        (5,  "g(5)",  "μ(6) = +1", "+1 · [f(1)+f(5)]",            "#eafaf0", FIELD),
        (3,  "g(3)",  "μ(10)= +1", "+1 · [f(1)+f(3)]",            "#eafaf0", FIELD),
        (2,  "g(2)",  "μ(15)= +1", "+1 · [f(1)+f(2)]",            "#eafaf0", FIELD),
        (1,  "g(1)",  "μ(30)= -1", "-1 · [f(1)]",                 "#fff5f5", "#e53e3e")
    ]

    Y_START = 85
    ROW_H = 34

    for i, (d, g_str, mu_str, exp_str, bg_color, border_color) in enumerate(divs_data):
        y = Y_START + i * ROW_H

        # Плашка рядка
        p.append(rect(60, y, 840, 28, fill=bg_color, stroke=border_color, sw=1.0, rx=4))

        # Дільник та g(d)
        p.append(text(100, y + 18, "d = %2d  ➔  %s" % (d, g_str), size=12.5, bold=True, color=INK, anchor="start"))

        # Множник Мьобіуса μ(30/d)
        p.append(text(340, y + 18, mu_str, size=12.5, bold=True, color=border_color, anchor="start"))

        # Розгорнутий вираз
        p.append(text(480, y + 18, exp_str, size=11.5, color=INK, anchor="start"))

    # Підсумкова рамка об'єднання
    p.append(rect(60, Y_START + 8 * ROW_H + 10, 840, 50, fill="#ffffff", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(W / 2, Y_START + 8 * ROW_H + 32,
                  "Сума по кожному f(k) при k < 30:  f(1)·(1-1-1-1+1+1+1-1) = 0,  f(2)·(1-1-1+1) = 0  ➔  залишається тільки 1 · f(30)",
                  size=12.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "fig-mobius-lattice-cancel.svg"), W, H, *p, title="Скасування коефіцієнтів Мьобіуса")


# ── 2. fig_poset_duality_lattice: Дуальність решітки підмножин та дільників
def fig_poset_duality_lattice():
    W, H = 960, 460
    p = []

    p.append(text(W / 2, 40, "Дуальність Мьобіуса: від включень-виключень до решітки подільності", size=16, bold=True))
    p.append(text(W / 2, 65, "Ізоморфізм між булевою решіткою підмножин 2^S та решіткою дільників числа n = p₁p₂p₃", size=13, color=MUTED))

    # Ліва частина: Решітка підмножин (Принцип включень-виключень)
    p.append(rect(50, 95, 410, 335, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=10))
    p.append(text(255, 125, "Решітка підмножин 2^{A, B, C}", size=14, bold=True, color=INK))
    p.append(text(255, 145, "μ(A, B) = (-1)^{|B| - |A|}", size=12.5, color=MUTED))

    # Рівні підмножин
    p.append(rect(205, 170, 100, 32, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(255, 191, "{A, B, C}", size=12, bold=True, color=FIELD))

    # Рівень 2
    subset_l2 = [(110, "{A,B}"), (255, "{A,C}"), (400, "{B,C}")]
    for x, txt in subset_l2:
        p.append(rect(x - 40, 240, 80, 28, fill="#fff5f5", stroke="#e53e3e", sw=1.2, rx=5))
        p.append(text(x, 259, txt, size=11.5, bold=True, color="#e53e3e"))
        p.append(line(255, 202, x, 240, color=LINE, sw=1.0))

    # Рівень 1
    subset_l1 = [(110, "{A}"), (255, "{B}"), (400, "{C}")]
    for x, txt in subset_l1:
        p.append(rect(x - 35, 310, 70, 28, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=5))
        p.append(text(x, 329, txt, size=11.5, bold=True, color=FIELD))

    for x1, _ in subset_l2:
        for x2, _ in subset_l1:
            if abs(x1 - x2) <= 150:
                p.append(line(x1, 268, x2, 310, color=LINE, sw=0.8, dash="3,3"))

    # Рівень 0
    p.append(rect(220, 375, 70, 28, fill="#fff5f5", stroke="#e53e3e", sw=1.2, rx=5))
    p.append(text(255, 394, "∅", size=13, bold=True, color="#e53e3e"))
    for x, _ in subset_l1:
        p.append(line(x, 338, 255, 375, color=LINE, sw=1.0))

    # Права частина: Решітка дільників n = p1*p2*p3 (наприклад 30)
    p.append(rect(500, 95, 410, 335, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(705, 125, "Решітка дільників d | (p₁p₂p₃)", size=14, bold=True, color=FIELD))
    p.append(text(705, 145, "μ(d) = (-1)^{ω(d)} для бесквадратних d", size=12.5, color=MUTED))

    # Рівень 3: n = 30
    p.append(rect(660, 170, 90, 32, fill="#fff5f5", stroke="#e53e3e", sw=1.5, rx=6))
    p.append(text(705, 191, "30 (μ=-1)", size=12, bold=True, color="#e53e3e"))

    # Рівень 2: 6, 10, 15
    div_l2 = [(560, "6 (μ=+1)"), (705, "10 (μ=+1)"), (850, "15 (μ=+1)")]
    for x, txt in div_l2:
        p.append(rect(x - 45, 240, 90, 28, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=5))
        p.append(text(x, 259, txt, size=11, bold=True, color=FIELD))
        p.append(line(705, 202, x, 240, color=LINE, sw=1.0))

    # Рівень 1: 2, 3, 5
    div_l1 = [(560, "2 (μ=-1)"), (705, "3 (μ=-1)"), (850, "5 (μ=-1)")]
    for x, txt in div_l1:
        p.append(rect(x - 40, 310, 80, 28, fill="#fff5f5", stroke="#e53e3e", sw=1.2, rx=5))
        p.append(text(x, 329, txt, size=11, bold=True, color="#e53e3e"))

    for x1, _ in div_l2:
        for x2, _ in div_l1:
            if abs(x1 - x2) <= 150:
                p.append(line(x1, 268, x2, 310, color=LINE, sw=0.8, dash="3,3"))

    # Рівень 0: 1
    p.append(rect(670, 375, 70, 28, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(705, 394, "1 (μ=+1)", size=11.5, bold=True, color=FIELD))
    for x, _ in div_l1:
        p.append(line(x, 338, 705, 375, color=LINE, sw=1.0))

    render(os.path.join(OUT, "fig-poset-duality-lattice.svg"), W, H, *p, title="Дуальність решіток та Мьобіус")


# ── 3. fig_block_division_complexity: Блокове ділення ⌊N/d⌋ та підсумовування
def fig_block_division_complexity():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 35, "Оптимізація обчислення сум згортки Мьобіуса: метод блокового ділення", size=16, bold=True))
    p.append(text(W / 2, 58, "Групування однакових значень ⌊N/d⌋ у діапазони [L, R] зменшує кількість кроків від N до 2√N", size=13, color=MUTED))

    p.append(text(W / 2, 100, "Розбиття інтервалу d ∈ [1, N] на плато константних значень ⌊N/d⌋", size=13, bold=True, color=INK))

    # Діапазони блоків для N = 100
    blocks = [
        (1, 1, "d=1", "⌊100/1⌋=100", "#eafaf0", FIELD),
        (2, 2, "d=2", "⌊100/2⌋=50",  "#eafaf0", FIELD),
        (3, 3, "d=3", "⌊100/3⌋=33",  "#eafaf0", FIELD),
        (4, 4, "d=4", "⌊100/4⌋=25",  "#eafaf0", FIELD),
        (5, 5, "d=5", "⌊100/5⌋=20",  "#eafaf0", FIELD),
        (6, 10, "d∈[6..10]", "⌊100/d⌋∈[10..16]", "#f8f9fa", INK),
        (11, 20, "d∈[11..20]", "⌊100/d⌋∈[5..9]", "#f8f9fa", INK),
        (21, 50, "d∈[21..50]", "⌊100/d⌋∈[2..4]", "#f8f9fa", INK),
        (51, 100, "d∈[51..100]", "⌊100/d⌋=1", "#fff5f5", "#e53e3e")
    ]

    XS = [80, 150, 220, 290, 360, 450, 570, 710, 840]
    WIDS = [55, 55, 55, 55, 55, 100, 120, 130, 110]

    for i, (l_val, r_val, label, val_str, bg, brd) in enumerate(blocks):
        x = XS[i]
        w = WIDS[i]
        p.append(rect(x - w/2, 125, w, 70, fill=bg, stroke=brd, sw=1.2, rx=6))
        p.append(text(x, 150, label, size=11.5, bold=True, color=INK))
        p.append(text(x, 175, val_str, size=10, color=MUTED))

    # Нижній блок: формула прискорення через префіксні суми
    p.append(rect(60, 245, 840, 125, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(W / 2, 275, "Сума на блоці [L, R]:   S(L, R) = k · [ M(R) - M(L - 1) ]", size=14, bold=True, color=FIELD))
    p.append(text(W / 2, 305, "де k = ⌊N/L⌋ є сталим для всіх d ∈ [L, R], а M(x) = ∑_{i=1}^x μ(i) — префіксна сума Мьобіуса", size=12.5, color=INK))
    p.append(text(W / 2, 335, "Підсумкова складність обчислення всієї суми: O(√N) замість O(N)", size=12, bold=True, color="#e53e3e"))

    render(os.path.join(OUT, "fig-block-division-complexity.svg"), W, H, *p, title="Метод блокового ділення")


if __name__ == "__main__":
    fig_mobius_lattice_cancel()
    fig_poset_duality_lattice()
    fig_block_division_complexity()
    print("All figures generated successfully!")
