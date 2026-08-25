# -*- coding: utf-8 -*-
"""Фігури до статті «Алгоритм Поліга — Геллмана»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Декомпозиція та відновлення за Полігом — Геллманом
# ─────────────────────────────────────────────────────────────────────────────
def fig_reduction():
    W, H = 840, 420
    frby = []

    # 1. Головна задача (ліворуч)
    b1, _, _ = textbox(140, 180, "Глобальна задача ДЛ\nПорядок N = ∏ pᵢᵉⁱ\ngˣ = h  у групі G\nШукаємо: x mod N", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    frby.append(b1)

    # 2. Підгрупи (по центру)
    subgroups = [
        (420, 75, "Підгрупа H₁ (порядок p₁ᵉ¹)\ng₁ˣ¹ = h₁  ⟹  x ≡ x₁ (mod p₁ᵉ¹)", "#eef2f7", NEG),
        (420, 155, "Підгрупа H₂ (порядок p₂ᵉ²)\ng₂ˣ² = h₂  ⟹  x ≡ x₂ (mod p₂ᵉ²)", "#eef2f7", NEG),
        (420, 285, "Підгрупа Hₖ (порядок pₖᵉᵏ)\ngₖˣᵏ = hₖ  ⟹  x ≡ xₖ (mod pₖᵉᵏ)", "#eef2f7", NEG),
    ]

    for cx, cy, label, fl, st in subgroups:
        box, _, _ = textbox(cx, cy, label, size=11, bold=True, fill=fl, stroke=st)
        frby.append(box)

    frby.append(text(420, 218, "•   •   •", size=18, bold=True, color=MUTED))

    # Стрілки проекції
    frby.append(arrow(260, 160, 290, 75, color=LINE, sw=1.5))
    frby.append(text(250, 105, "степінь N/p₁ᵉ¹", size=10, italic=True, color=MUTED))

    frby.append(arrow(260, 175, 290, 155, color=LINE, sw=1.5))
    frby.append(text(265, 148, "степінь N/p₂ᵉ²", size=10, italic=True, color=MUTED))

    frby.append(arrow(260, 195, 290, 285, color=LINE, sw=1.5))
    frby.append(text(250, 255, "степінь N/pₖᵉᵏ", size=10, italic=True, color=MUTED))

    # 3. Збирання через CRT (праворуч)
    b3, _, _ = textbox(710, 180, "Китайська теорема\nпро залишки (CRT)\nx ≡ x₁ (mod p₁ᵉ¹)\n…\nx ≡ xₖ (mod pₖᵉᵏ)\n⟹  x mod N знайдено", size=12, bold=True, fill="#eafaf1", stroke=FIELD)
    frby.append(b3)

    # Стрілки до CRT
    frby.append(arrow(550, 75, 580, 160, color=FIELD, sw=1.5))
    frby.append(arrow(550, 155, 580, 175, color=FIELD, sw=1.5))
    frby.append(arrow(550, 285, 580, 195, color=FIELD, sw=1.5))

    frby.append(text(W / 2, 360, "Проекція підносить елементи до степеня N/pᵢᵉⁱ, обнуляючи всі сторонні множники.", size=12, color=MUTED))
    frby.append(text(W / 2, 385, "Розв'язки xᵢ у малих підгрупах об'єднуються в єдиний показник x за модулем N.", size=12, color=MUTED))

    render(os.path.join(OUT, "pohlig-hellman-reduction.svg"), W, H, *frby,
           title="Декомпозиція задачі дискретного логарифма за алгоритмом Поліга — Геллмана")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Порозрядне вилучення (lifting) у підгрупі степеня простого числа pᵉ
# ─────────────────────────────────────────────────────────────────────────────
def fig_lifting():
    W, H = 840, 400
    frby = []

    # Заголовок зверху
    frby.append(text(W / 2, 30, "Показник x = z₀ + z₁·p + z₂·p² + … + zₑ₋₁·pᵉ⁻¹  (цифри zⱼ ∈ [0, p-1])", size=13, bold=True, color=INK))

    steps = [
        (130, 140, "Крок 0: цифра z₀\nПіднесення до pᵉ⁻¹\n(gⁱ)ᵖᵉ⁻¹·ᶻ⁰ = (hⁱ)ᵖᵉ⁻¹\nПошук z₀ у групі ⟨γ⟩", "#fff6e5", POS),
        (370, 140, "Крок 1: цифра z₁\nДілення на gⁱᶻ⁰\nПіднесення до pᵉ⁻²\nПошук z₁ у групі ⟨γ⟩", "#eef2f7", NEG),
        (610, 140, "Крок e-1: цифра zₑ₋₁\nДілення на відомі zⱼ\nПіднесення до p⁰ = 1\nПошук zₑ₋₁ у групі ⟨γ⟩", "#eafaf1", FIELD),
    ]

    for cx, cy, label, fl, st in steps:
        box, _, _ = textbox(cx, cy, label, size=11, bold=True, fill=fl, stroke=st)
        frby.append(box)

    frby.append(arrow(220, 140, 275, 140, color=LINE, sw=1.5))
    frby.append(arrow(465, 140, 515, 140, color=LINE, sw=1.5))

    # Спільний генератор унизу
    box_gen, _, _ = textbox(W / 2, 270, "Незмінна база пошуку: γ = gⁱᵖᵉ⁻¹ (елемент порядку p)\nТаблиця Baby-Step Giant-Step для бази γ будується лише один раз!", size=12, bold=True, fill="#faf5ff", stroke="#8e44ad")
    frby.append(box_gen)

    frby.append(arrow(130, 205, 300, 240, color="#8e44ad", sw=1.3))
    frby.append(arrow(370, 205, 420, 240, color="#8e44ad", sw=1.3))
    frby.append(arrow(610, 205, 540, 240, color="#8e44ad", sw=1.3))

    frby.append(text(W / 2, 350, "Кожен крок зводить знаходження однієї p-адичної цифри до задачі розміру p.", size=12, color=MUTED))
    frby.append(text(W / 2, 375, "Загальна складність для pᵉ становить O(e · √p) замість непідйомного O(pᵉ/²).", size=12, color=MUTED))

    render(os.path.join(OUT, "prime-power-lifting.svg"), W, H, *frby,
           title="Покрокове відновлення цифр дискретного логарифма у підгрупі порядку pᵉ")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Порівняння гладкого порядку проти безпечного простого числа
# ─────────────────────────────────────────────────────────────────────────────
def fig_smooth_vs_safe():
    W, H = 840, 420
    frby = []

    # Ліва колонка: Гладкий порядок (вразливий)
    bx1, by1, bw, bh = 40, 40, 360, 310
    frby.append(rect(bx1, by1, bw, bh, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frby.append(text(bx1 + bw / 2, by1 + 28, "Гладкий порядок групи (B-smooth)", size=13, bold=True, color=POS))
    frby.append(line(bx1 + 15, by1 + 42, bx1 + bw - 15, by1 + 42, color=POS, sw=1))

    frby.append(text(bx1 + bw / 2, by1 + 70, "Порядок N = 2 · 3² · 5 · 7 · 11 · 13 · …", size=11, bold=True, color=INK))

    # Смужки дрібних підгруп
    sub_bars = [
        ("p₁ = 2", 30, NEG),
        ("p₂² = 9", 45, NEG),
        ("p₃ = 5", 35, NEG),
        ("p₄ = 7", 40, NEG),
        ("p₅ = 11", 50, NEG),
        ("p₆ = 13", 55, NEG),
    ]
    cur_x = bx1 + 35
    for name, w_bar, col in sub_bars:
        frby.append(rect(cur_x, by1 + 95, w_bar, 32, fill="#eaf0fd", stroke=col, sw=1.2, rx=4))
        frby.append(text(cur_x + w_bar / 2, by1 + 115, name, size=9, bold=True, color=col))
        cur_x += w_bar + 8

    frby.append(text(bx1 + bw / 2, by1 + 160, "Складність Поліга — Геллмана:", size=12, bold=True, color=INK))
    frby.append(text(bx1 + bw / 2, by1 + 185, "∑ O(√pᵢ)  ≈  мікросекунди", size=13, bold=True, color=POS))
    frby.append(text(bx1 + bw / 2, by1 + 225, "Кожна підгрупа розкриває свій фрагмент xᵢ.", size=11, color=MUTED))
    frby.append(text(bx1 + bw / 2, by1 + 248, "CRT збирає повний секрет x миттєво.", size=11, color=MUTED))
    frby.append(text(bx1 + bw / 2, by1 + 285, "⚠️ КРИПТОГРАФІЧНИЙ ЗЛАМ", size=12, bold=True, color=POS))

    # Права колонка: Безпечне просте число Safe Prime (стійке)
    bx2, by2 = 440, 40
    frby.append(rect(bx2, by2, bw, bh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frby.append(text(bx2 + bw / 2, by2 + 28, "Безпечне просте (p = 2q + 1, q просте)", size=13, bold=True, color=FIELD))
    frby.append(line(bx2 + 15, by2 + 42, bx2 + bw - 15, by2 + 42, color=FIELD, sw=1))

    frby.append(text(bx2 + bw / 2, by2 + 70, "Порядок N = p - 1 = 2 · q  (q ≈ 2²⁵⁵)", size=11, bold=True, color=INK))

    # Смужка 2 та гігантський блок q
    frby.append(rect(bx2 + 35, by2 + 95, 35, 32, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frby.append(text(bx2 + 52.5, by2 + 115, "2", size=10, bold=True, color=NEG))

    frby.append(rect(bx2 + 78, by2 + 95, 245, 32, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    frby.append(text(bx2 + 200, by2 + 115, "Гігантська підгрупа q (255 біт)", size=10, bold=True, color=FIELD))

    frby.append(text(bx2 + bw / 2, by2 + 160, "Складність Поліга — Геллмана:", size=12, bold=True, color=INK))
    frby.append(text(bx2 + bw / 2, by2 + 185, "O(√2) + O(√q)  ≈  2¹²⁸ операцій", size=13, bold=True, color=FIELD))
    frby.append(text(bx2 + bw / 2, by2 + 225, "Витікає лише 1 біт (x mod 2).", size=11, color=MUTED))
    frby.append(text(bx2 + bw / 2, by2 + 248, "Основний секрет x mod q лишається недосяжним.", size=11, color=MUTED))
    frby.append(text(bx2 + bw / 2, by2 + 285, "✓ НАДІЙНИЙ ЗАХИСТ", size=12, bold=True, color=FIELD))

    frby.append(text(W / 2, 385, "Безпека схеми визначається розміром НАЙБІЛЬШОГО простого дільника порядку групи.", size=12, color=MUTED))

    render(os.path.join(OUT, "smooth-vs-safe-primes.svg"), W, H, *frby,
           title="Порівняння структури порядку групи: B-гладкий порядок проти безпечного простого числа")


if __name__ == "__main__":
    fig_reduction()
    fig_lifting()
    fig_smooth_vs_safe()
    print("Всі фігури згенеровано успішно.")
