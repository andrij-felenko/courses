# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── fig-dirichlet-convolution-matrix: обчислення (f * g)(12)
def fig_dirichlet_convolution_matrix():
    W, H = 960, 440
    p = []

    p.append(text(W / 2, 45, "Операція згортки Диріхле: обчислення (f * g)(12)", size=16, bold=True))
    p.append(text(W / 2, 70, "Сума добутків f(d) · g(12/d) по всіх дільниках d числа 12", size=13, color=MUTED))

    divs = [1, 2, 3, 4, 6, 12]
    XS = [100, 240, 380, 520, 660, 800]
    CW, CH = 110, 85

    # Верхня смуга: дільники d та пари (d, 12/d)
    for i, d in enumerate(divs):
        x = XS[i]
        compl = 12 // d
        p.append(rect(x - CW/2, 110, CW, CH, fill="#f8f9fa", stroke=LINE, sw=1.3, rx=6))
        p.append(text(x, 135, "d = %d" % d, size=14, bold=True, color=INK))
        p.append(text(x, 160, "12/d = %d" % compl, size=13, color=MUTED))

        # Стрілка вниз до елементу добутку
        p.append(arrow(x, 110 + CH, x, 240, color=LINE, sw=1.4))

    # Середня смуга: добутки f(d) · g(12/d)
    for i, d in enumerate(divs):
        x = XS[i]
        compl = 12 // d
        p.append(rect(x - CW/2, 240, CW, 55, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
        p.append(text(x, 272, "f(%d) · g(%d)" % (d, compl), size=12.5, bold=True, color=FIELD))

        # Стрілка від добутку до центрального суматора
        p.append(arrow(x, 295, W / 2, 350, color=FIELD, sw=1.2))

    # Центральний вузол суми
    b, _, _ = textbox(W / 2, 375, "(f * g)(12) = f(1)g(12) + f(2)g(6) + f(3)g(4) + f(4)g(3) + f(6)g(2) + f(12)g(1)",
                      size=13.5, pad=12, fill="#ffffff", stroke=FIELD, sw=2.0, bold=True)
    p.append(b)

    render(os.path.join(OUT, "fig-dirichlet-convolution-matrix.svg"), W, H, *p, title="Згортка Диріхле для n=12")


# ── fig-dirichlet-algebra-tree: мережа тотожностей згортки Диріхле
def fig_dirichlet_algebra_tree():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 45, "Алгебраїчна мережа тотожностей згортки Диріхле", size=16, bold=True))
    p.append(text(W / 2, 70, "Зв'язки між базовими арифметичними функціями через операцію *", size=13, color=MUTED))

    # Вузли
    nodes = {
        "eps": (480, 120, "ε(n)", "Одиниця згортки\n[n=1]"),
        "one": (280, 220, "1(n)", "Постійна 1\n1(n) = 1"),
        "mob": (680, 220, "μ(n)", "Функція Мебіуса\n(-1)^k, 0"),
        "id":  (280, 360, "id(n)", "Тотожна функція\nid(n) = n"),
        "phi": (680, 360, "φ(n)", "Функція Ейлера\nтотієнт"),
        "d":   (120, 360, "d(n)", "Кількість дільників\n1 * 1"),
        "sig": (480, 440, "σ(n)", "Сума дільників\nid * 1"),
        "mang":(480, 290, "Λ(n)", "Мангольдт\nln * μ")
    }

    # Горизонтальне обернення між 1 і μ
    p.append(arrow(340, 220, 620, 220, color=LINE, sw=1.5))
    p.append(text(380, 205, "1 * μ = ε", size=12, color=MUTED, anchor="start"))

    # Вертикальні та похилі зв'язки
    p.append(arrow(280, 260, 280, 320, color=LINE, sw=1.5))
    p.append(text(240, 290, "1 * φ = id", size=12, color=MUTED, anchor="end"))

    p.append(arrow(680, 320, 680, 260, color=LINE, sw=1.5))
    p.append(text(720, 290, "id * μ = φ", size=12, color=MUTED, anchor="start"))

    p.append(arrow(230, 240, 160, 320, color=LINE, sw=1.5))
    p.append(text(175, 270, "1 * 1 = d", size=12, color=MUTED, anchor="end"))

    p.append(arrow(320, 390, 430, 425, color=LINE, sw=1.5))
    p.append(text(360, 420, "id * 1 = σ", size=12, color=MUTED))

    # Вертикальна стрілка від mang до eps
    p.append(arrow(480, 260, 480, 160, color=LINE, sw=1.5))
    p.append(text(510, 195, "1 * Λ = ln", size=12, color=MUTED, anchor="start"))

    # Малюємо вузли
    for key, (x, y, label, desc) in nodes.items():
        is_core = key in ("eps", "one", "mob", "phi")
        w, h = 100, 55
        p.append(rect(x - w/2, y - h/2, w, h,
                      fill="#eafaf0" if is_core else "#f8f9fa",
                      stroke=FIELD if is_core else LINE, sw=1.8 if is_core else 1.2, rx=8))
        p.append(text(x, y - 5, label, size=14, bold=True, color=FIELD if is_core else INK))
        lines = desc.split("\n")
        p.append(text(x, y + 15, lines[0], size=10.5, color=MUTED))

    render(os.path.join(OUT, "fig-dirichlet-algebra-tree.svg"), W, H, *p, title="Алгебраїчна мережа тотожностей згортки")


# ── fig-mobius-inversion: прямо підсумовування та обернення Мебіуса
def fig_mobius_inversion():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 45, "Формула обернення Мебіуса: прямо та навпаки", size=16, bold=True))
    p.append(text(W / 2, 70, "Перехід від накопичення g(n) = ∑ f(d) до відновлення f(n) = ∑ μ(d) g(n/d)", size=13, color=MUTED))

    # Ліва панель: Пряме підсумовування g = f * 1
    p.append(rect(40, 100, 420, 280, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=10))
    p.append(text(250, 130, "Пряме накопичення: g = f * 1", size=14, bold=True, color=INK))
    p.append(text(250, 155, "g(n) = ∑_{d|n} f(d) · 1", size=12.5, color=MUTED))

    p.append(rect(80, 185, 340, 45, fill="#f8f9fa", stroke=LINE, sw=1.0, rx=6))
    p.append(text(250, 212, "Усі вагові коефіцієнти дорівнюють +1", size=12.5, color=INK))

    p.append(arrow(250, 240, 250, 280, color=LINE, sw=1.5))

    p.append(rect(80, 290, 340, 60, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(250, 315, "g(12) = f(1)+f(2)+f(3)+f(4)+f(6)+f(12)", size=12, bold=True, color=FIELD))
    p.append(text(250, 335, "сумування по всіх дільниках", size=11, color=MUTED))

    # Права панель: Обернення Мебіуса f = g * μ
    p.append(rect(500, 100, 420, 280, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(710, 130, "Обернення Мебіуса: f = g * μ", size=14, bold=True, color=FIELD))
    p.append(text(710, 155, "f(n) = ∑_{d|n} μ(d) g(n/d)", size=12.5, color=MUTED))

    p.append(rect(540, 185, 340, 45, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=6))
    p.append(text(710, 212, "Ваги μ(d): +1 (парні p), -1 (непарні p), 0 (p²|d)", size=11.5, bold=True, color=FIELD))

    p.append(arrow(710, 240, 710, 280, color=FIELD, sw=1.5))

    p.append(rect(540, 290, 340, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(710, 315, "f(12) = g(12) - g(6) - g(4) + g(2)", size=12, bold=True, color=INK))
    p.append(text(710, 335, "скасування знаків за принципом включень-виключень", size=11, color=MUTED))

    render(os.path.join(OUT, "fig-mobius-inversion.svg"), W, H, *p, title="Обернення Мебіуса")


if __name__ == "__main__":
    fig_dirichlet_convolution_matrix()
    fig_dirichlet_algebra_tree()
    fig_mobius_inversion()
    print("All figures generated successfully!")
