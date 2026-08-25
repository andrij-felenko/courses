# -*- coding: utf-8 -*-
"""Фігури до статті «Кільця многочленів»."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Ієрархія алгебраїчних структур та кілець многочленів
# ─────────────────────────────────────────────────────────────────────────────
def fig_hierarchy_rings():
    W, H = 840, 480
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Ієрархія комутативних кілець та місце кілець многочленів", size=15, bold=True, color=INK))

    levels = [
        ("Комутативні кільця з 1", "Загальні кільця: R[x]", "#f8fafc", LINE, 70),
        ("Області цілісності (Domain)", "Без дільників нуля: D[x], якщо D — область", "#f1f5f9", LINE, 135),
        ("Факторіальні кільця (UFD)", "Однозначний розклад на множники: ℤ[x], K[x₁, ..., xₙ]", "#e0f2fe", NEG, 200),
        ("Кільця головних ідеалів (PID)", "Кожен ідеал породжений одним елементом: K[x]", "#fef08a", "#ca8a04", 265),
        ("Евклідові кільця (ED)", "Існує ділення з остачею (степінь deg): K[x], ℤ", "#dcfce7", FIELD, 330),
        ("Поля (Fields)", "Кожен ненульовий елемент оборотний: K, K(x)", "#fee2e2", POS, 395)
    ]

    for i, (title, desc, fill, stroke, y) in enumerate(levels):
        w_box = 740 - i * 40
        x_box = (W - w_box) / 2
        frags.append(rect(x_box, y, w_box, 52, fill=fill, stroke=stroke, sw=1.5, rx=6))
        frags.append(text(W / 2, y + 20, title, size=13, bold=True, color=INK))
        frags.append(text(W / 2, y + 38, desc, size=11, color=MUTED))

    # Вертикальні стрілки включення
    for y in [122, 187, 252, 317, 382]:
        frags.append(arrow(W / 2, y, W / 2, y + 12, color=INK, sw=1.5))

    render(os.path.join(OUT, "hierarchy-rings.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Схема евклідового ділення многочленів з остачею
# ─────────────────────────────────────────────────────────────────────────────
def fig_polynomial_long_division():
    W, H = 820, 430
    frags = []

    frags.append(text(W / 2, 28, "Схема евклідового ділення в K[x]: f(x) = q(x)·g(x) + r(x)", size=15, bold=True, color=INK))

    # Лівий блок: Ділене f(x)
    b1, w1, h1 = textbox(160, 105, "Ділене: f(x)\nстепінь deg(f) = n\nстарший член aₙ·xⁿ", size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frags.append(b1)

    # Правий блок: Дільник g(x)
    b2, w2, h2 = textbox(660, 105, "Дільник: g(x)\nстепінь deg(g) = m\nстарший член bₘ·xᵐ ≠ 0", size=12, pad=10, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(b2)

    # Центральний блок ітераційного вилучення
    b_mid, wm, hm = textbox(410, 215, "Ітерація редукції старшого монома:\nmonom = (aₙ / bₘ) · xⁿ⁻ᵐ\nf₁(x) = f(x) − monom · g(x)\nЗменшення степеня: deg(f₁) < deg(f)", size=12, pad=12, fill="#fefce8", stroke="#ca8a04", sw=1.5)
    frags.append(b_mid)

    frags.append(arrow(260, 105, 310, 180, color=LINE, sw=1.5))
    frags.append(arrow(560, 105, 510, 180, color=NEG, sw=1.5))

    # Стрілка вниз до зупинки
    frags.append(arrow(410, 275, 410, 320, color=LINE, sw=1.5))
    frags.append(text(495, 298, "поки deg(fₖ) ≥ deg(g)", size=11, color=MUTED))

    # Нижні блоки: Частка та Остача
    b_q, wq, hq = textbox(240, 365, "Частка: q(x)\nсума всіх мономиків (aₖ / bₘ)·xᵏ⁻ᵐ\ndeg(q) = deg(f) − deg(g)", size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frags.append(b_q)

    b_r, wr, hr = textbox(580, 365, "Остача: r(x)\nкінцевий залишок\ndeg(r) < deg(g) або r(x) = 0", size=12, pad=10, fill="#fef2f2", stroke=POS, sw=1.5)
    frags.append(b_r)

    frags.append(arrow(360, 320, 290, 335, color=FIELD, sw=1.5))
    frags.append(arrow(460, 320, 530, 335, color=POS, sw=1.5))

    render(os.path.join(OUT, "polynomial-long-division.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Побудова фактор-кільця K[x]/(f(x)) та розширення полів
# ─────────────────────────────────────────────────────────────────────────────
def fig_quotient_ring_isomorphism():
    W, H = 840, 440
    frags = []

    frags.append(text(W / 2, 28, "Фактор-кільце K[x]/(f(x)): від поліномів до розширення полів", size=15, bold=True, color=INK))

    # Ліва панель: Кільце многочленів K[x]
    frags.append(rect(40, 65, 230, 345, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(155, 95, "Кільце K[x]", size=14, bold=True, color=INK))
    frags.append(text(155, 120, "Нескінченновимірний простір", size=10, color=MUTED))

    frags.append(rect(60, 145, 190, 40, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(155, 170, "g(x) = a₀ + a₁x + a₂x² + ...", size=11, color=INK))

    frags.append(rect(60, 205, 190, 60, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(155, 228, "Головний ідеал I = (f(x))", size=11, bold=True, color=POS))
    frags.append(text(155, 250, "{ h(x) · f(x) | h(x) ∈ K[x] }", size=10, color=POS))

    frags.append(rect(60, 285, 190, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(155, 305, "Суміжні класи (косети):", size=10, color=MUTED))
    frags.append(text(155, 322, "g(x) + (f(x))", size=11, bold=True, color=INK))

    # Центральна стрілка канонічної проекції
    frags.append(arrow(280, 235, 340, 235, color=INK, sw=2))
    frags.append(text(310, 218, "π : mod f(x)", size=11, bold=True, color=INK))

    # Середня панель: Канонічні залишки
    frags.append(rect(350, 65, 220, 345, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(460, 95, "Фактор-кільце K[x]/(f(x))", size=13, bold=True, color=FIELD))
    frags.append(text(460, 120, "Канонічні представники: r(x)", size=10, color=MUTED))

    frags.append(rect(370, 145, 180, 80, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(460, 172, "r(x) = c₀ + c₁x + ... + cₙ₋₁xⁿ⁻¹", size=10, bold=True, color=INK))
    frags.append(text(460, 195, "deg(r) < deg(f) = n", size=11, color=FIELD))
    frags.append(text(460, 215, "dim_K = n", size=11, bold=True, color=FIELD))

    frags.append(rect(370, 245, 180, 75, fill="#fefce8", stroke="#ca8a04", sw=1, rx=4))
    frags.append(text(460, 268, "Множення в факторі:", size=10, bold=True, color=INK))
    frags.append(text(460, 288, "(r₁ · r₂) mod f(x)", size=11, color="#854d0e"))
    frags.append(text(460, 308, "f(x) ≡ 0", size=11, bold=True, color=POS))

    # Права панель: Розгалуження властивостей
    frags.append(arrow(580, 190, 630, 145, color=POS, sw=1.8))
    frags.append(arrow(580, 280, 630, 325, color=NEG, sw=1.8))

    # Верхній випадок: f(x) незвідний -> Поле
    b_field, wf, hf = textbox(725, 145, "f(x) — незвідний:\n(f(x)) — максимальний ідеал\nK[x]/(f(x)) ≅ K(α) — ПОЛЕ!\n(Приклад: ℝ[x]/(x²+1) ≅ ℂ)", size=11, pad=8, fill="#fee2e2", stroke=POS, sw=1.5)
    frags.append(b_field)

    # Нижній випадок: f(x) розкладний -> Кільце з дільниками нуля
    b_ring, wr, hr = textbox(725, 325, "f(x) = g(x)·h(x) — розкладний:\n(f(x)) не максимальний\nЄ дільники нуля: g·h ≡ 0\n(Приклад: ℝ[x]/(x²−1) ≅ ℝ × ℝ)", size=11, pad=8, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(b_ring)

    render(os.path.join(OUT, "quotient-ring-isomorphism.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Мономіальна ґратка та східчастий контур базису Грьобнера
# ─────────────────────────────────────────────────────────────────────────────
def fig_groebner_monomial_ideal():
    W, H = 820, 460
    frags = []

    frags.append(text(W / 2, 26, "2D-ґратка мономиків xᵃyᵇ: ідеал старших членів ⟨LT(I)⟩ та базис Грьобнера", size=14, bold=True, color=INK))

    # Координатні осі для степенів x та y
    ox, oy = 100, 390
    step = 45
    max_deg = 6

    # Вісь X (степінь x)
    frags.append(arrow(ox - 10, oy, ox + max_deg * step + 40, oy, color=LINE, sw=1.8))
    frags.append(text(ox + max_deg * step + 35, oy + 25, "Степінь x (a)", size=12, bold=True, color=INK))

    # Вісь Y (степінь y)
    frags.append(arrow(ox, oy + 10, ox, oy - max_deg * step - 40, color=LINE, sw=1.8))
    frags.append(text(ox - 45, oy - max_deg * step - 25, "Степінь y (b)", size=12, bold=True, color=INK))

    # Заливка області ідеалу ⟨LT(I)⟩ для прикладу з генераторами x²y та xy³
    # Полігон ідеалу
    pts = [
        (ox + 1 * step, oy - 3 * step),
        (ox + 1 * step, oy - 6 * step),
        (ox + 6 * step, oy - 6 * step),
        (ox + 6 * step, oy - 1 * step),
        (ox + 2 * step, oy - 1 * step),
        (ox + 2 * step, oy - 3 * step),
    ]
    pts_str = " ".join(["%.1f,%.1f" % p for p in pts])
    frags.append('<polygon points="%s" fill="#dbeafe" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (pts_str, NEG))

    # Східчаста лінія (границя ідеалу)
    staircase = [
        (ox + 1 * step, oy - 6 * step),
        (ox + 1 * step, oy - 3 * step),
        (ox + 2 * step, oy - 3 * step),
        (ox + 2 * step, oy - 1 * step),
        (ox + 6 * step, oy - 1 * step)
    ]
    for i in range(len(staircase) - 1):
        x1, y1 = staircase[i]
        x2, y2 = staircase[i+1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2.5))

    # Сітка та точки мономиків
    for a in range(max_deg + 1):
        for b in range(max_deg + 1):
            px = ox + a * step
            py = oy - b * step
            in_ideal = (a >= 1 and b >= 3) or (a >= 2 and b >= 1)
            is_gen = (a == 1 and b == 3) or (a == 2 and b == 1)
            
            if is_gen:
                frags.append(circle(px, py, 6, fill=POS, stroke=LINE, sw=1.5))
            elif in_ideal:
                frags.append(circle(px, py, 4, fill=NEG, stroke=LINE, sw=1))
            else:
                frags.append(circle(px, py, 4, fill=FIELD, stroke=LINE, sw=1))

    # Позначення на осях
    for a in range(max_deg + 1):
        frags.append(line(ox + a * step, oy - 4, ox + a * step, oy + 4, color=LINE, sw=1))
        frags.append(text(ox + a * step, oy + 16, str(a), size=10, color=MUTED))
    for b in range(1, max_deg + 1):
        frags.append(line(ox - 4, oy - b * step, ox + 4, oy - b * step, color=LINE, sw=1))
        frags.append(text(ox - 14, oy - b * step + 4, str(b), size=10, color=MUTED))

    # Підписи генераторів
    frags.append(text(ox + 1 * step - 25, oy - 3 * step - 10, "LT(g₁) = xy³", size=11, bold=True, color=POS))
    frags.append(text(ox + 2 * step + 30, oy - 1 * step + 15, "LT(g₂) = x²y", size=11, bold=True, color=POS))

    # Легенда та пояснення праворуч
    lx, ly = 480, 85
    frags.append(rect(lx, ly, 310, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(lx + 155, ly + 25, "Анатомія простору K[x, y]", size=13, bold=True, color=INK))

    frags.append(circle(lx + 25, ly + 60, 5, fill=POS, stroke=LINE, sw=1))
    frags.append(text(lx + 40, ly + 64, "Провідні мономи базису Грьобнера G", size=11, bold=True, color=POS, anchor="start"))

    frags.append(circle(lx + 25, ly + 95, 5, fill=NEG, stroke=LINE, sw=1))
    frags.append(text(lx + 40, ly + 99, "Мономи в ідеалі старших членів ⟨LT(I)⟩", size=11, color=NEG, anchor="start"))

    frags.append(circle(lx + 25, ly + 130, 5, fill=FIELD, stroke=LINE, sw=1))
    frags.append(text(lx + 40, ly + 134, "Стандартні мономи (базис K[x,y]/I)", size=11, bold=True, color=FIELD, anchor="start"))

    frags.append(line(lx + 15, ly + 160, lx + 295, ly + 160, color=LINE, sw=0.8, dash="2,2"))

    b_exp = (
        "Східчастий контур ділить простір:\n"
        "1. Усе всередині контуру ділиться\n"
        "   на старші мономи базису G.\n"
        "2. Зелені точки під східцями —\n"
        "   нескоротні мономи (канонічні остачі).\n"
        "3. Кількість зелених точок = dim(K[x,y]/I)\n"
        "   (кількість розв'язків системи рівнянь)."
    )
    b_desc, _, _ = textbox(lx + 155, ly + 235, b_exp, size=11, pad=6, fill="#ffffff", stroke=LINE, sw=1)
    frags.append(b_desc)

    render(os.path.join(OUT, "groebner-monomial-ideal.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hierarchy_rings()
    fig_polynomial_long_division()
    fig_quotient_ring_isomorphism()
    fig_groebner_monomial_ideal()
    print("Усі фігури згенеровано успішно.")
