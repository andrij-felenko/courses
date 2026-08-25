# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Кругові поля» (cyclotomic-fields)."""

import os
import sys
import math

# Підключаємо спільну бібліотеку svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_cyclotomic_roots():
    """Фігура 1: Корені з одиниці 8-го степеня на комплексному колі.
    Показує примітивні корені (породжують усю групу) та непримітивні (породжують підгрупи)."""
    w, h = 760, 480
    frags = []

    # Заголовок
    frags.append(text(380, 28, "Корені з одиниці 8-го степеня: x⁸ − 1 = 0 на комплексній площині", size=16, bold=True))

    cx, cy, r = 240, 250, 150

    # Координатні осі
    frags.append(line(cx - 180, cy, cx + 180, cy, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(cx, cy - 180, cx, cy + 180, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(cx + 195, cy + 5, "Re", size=13, color=MUTED, bold=True))
    frags.append(text(cx, cy - 190, "Im", size=13, color=MUTED, bold=True))

    # Одиничне коло
    frags.append(circle(cx, cy, r, fill="none", stroke=LINE, sw=1.8))

    # 8 коренів
    # k = 0..7, кут = k * pi / 4
    angles = [k * math.pi / 4 for k in range(8)]
    is_primitive = [False, True, False, True, False, True, False, True]
    labels = [
        "1",
        "ζ₈",
        "i = ζ₈²",
        "ζ₈³",
        "−1 = ζ₈⁴",
        "ζ₈⁵",
        "−i = ζ₈⁶",
        "ζ₈⁷"
    ]

    # З'єднувальний 8-кутник
    poly_pts = []
    for k in range(8):
        px = cx + r * math.cos(angles[k])
        py = cy - r * math.sin(angles[k])
        poly_pts.append((px, py))
    for k in range(8):
        p1 = poly_pts[k]
        p2 = poly_pts[(k + 1) % 8]
        frags.append(line(p1[0], p1[1], p2[0], p2[1], color="#cbd5e1", sw=1.5, dash="3,3"))

    # Радіуси до примітивних коренів (зелені) та непримітивних (сірі)
    for k in range(8):
        px, py = poly_pts[k]
        c = FIELD if is_primitive[k] else MUTED
        sw = 1.6 if is_primitive[k] else 1.0
        frags.append(line(cx, cy, px, py, color=c, sw=sw))

    # Точки та підписи
    label_offsets = [
        (26, 5),    # 1 (0 rad)
        (24, -14),  # zeta_8 (pi/4)
        (0, -22),   # i (pi/2)
        (-28, -14), # zeta_8^3 (3pi/4)
        (-48, 5),   # -1 (pi)
        (-28, 22),  # zeta_8^5 (5pi/4)
        (0, 24),    # -i (3pi/2)
        (24, 22),   # zeta_8^7 (7pi/4)
    ]

    for k in range(8):
        px, py = poly_pts[k]
        if is_primitive[k]:
            frags.append(circle(px, py, 7, fill="#e8f5e9", stroke=FIELD, sw=2.2))
            col = "#1b5e20"
        else:
            frags.append(circle(px, py, 5, fill="#f1f5f9", stroke=MUTED, sw=1.8))
            col = MUTED
        ox, oy = label_offsets[k]
        frags.append(text(px + ox, py + oy, labels[k], size=13, color=col, bold=is_primitive[k]))

    # Легенда та пояснення праворуч
    lx, ly = 480, 80
    b1 = fitbox(lx, ly, 260, 160,
                "Примітивні корені ζ₈ (НСД(k, 8) = 1):\n"
                "• ζ₈, ζ₈³, ζ₈⁵, ζ₈⁷ (рівно φ(8) = 4)\n"
                "• Кожен породжує ВСІ 8 коренів\n"
                "• Їхній спільний мінімальний\n"
                "  многочлен: Φ₈(x) = x⁴ + 1\n"
                "• Розширення: [ℚ(ζ₈) : ℚ] = 4",
                size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frags.append(b1)

    b2 = fitbox(lx, ly + 180, 260, 175,
                "Непримітивні корені:\n"
                "• 1 (порядок 1, корінь Φ₁(x) = x − 1)\n"
                "• −1 (порядок 2, корінь Φ₂(x) = x + 1)\n"
                "• ±i (порядок 4, корені Φ₄(x) = x² + 1)\n\n"
                "Повний розклад:\n"
                "x⁸ − 1 = Φ₁(x) · Φ₂(x) · Φ₄(x) · Φ₈(x)",
                size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.2)
    frags.append(b2)

    render(os.path.join(OUT_DIR, "fig-cyclotomic-roots.svg"), w, h, *frags)


def fig_heptadecagon_periods():
    """Фігура 2: Періоди Гаусса для 17-кутника.
    Показує вежу з 4 квадратних рівнянь (2^4 = 16) розкладання коренів ζ₁₇."""
    w, h = 820, 460
    frags = []

    frags.append(text(410, 26, "Вежа періодів Гаусса для 17-кутника (1796 рік)", size=16, bold=True))

    # Рівень 0: 16 коренів (сума = -1)
    b0, w0, h0 = textbox(410, 65, "16 примітивних коренів ζ₁₇: сума η = −1\n[ℚ(ζ₁₇) : ℚ] = 16", size=13, fill="#f8fafc", stroke=LINE, bold=True)
    frags.append(b0)

    # Стрілки до рівня 1
    frags.append(arrow(340, 92, 250, 138, color=LINE, sw=1.5))
    frags.append(arrow(480, 92, 570, 138, color=LINE, sw=1.5))
    frags.append(text(410, 118, "квадратне рівняння 1: y² + y − 4 = 0", size=11, color=MUTED, italic=True))

    # Рівень 1: 2 періоди по 8 доданків
    b1_1 = fitbox(110, 140, 260, 60, "Період η₁ (8 коренів):\nζ + ζ² + ζ⁴ + ζ⁸ + ζ⁹ + ζ¹³ + ζ¹⁵ + ζ¹⁶", size=11, fill="#eff6ff", stroke=NEG, sw=1.5)
    b1_2 = fitbox(450, 140, 260, 60, "Період η₂ (8 коренів):\nζ³ + ζ⁵ + ζ⁶ + ζ⁷ + ζ¹⁰ + ζ¹¹ + ζ¹² + ζ¹⁴", size=11, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(b1_1)
    frags.append(b1_2)

    # Стрілки до рівня 2
    frags.append(arrow(240, 202, 170, 248, color=LINE, sw=1.5))
    frags.append(arrow(240, 202, 310, 248, color=LINE, sw=1.5))
    frags.append(arrow(580, 202, 510, 248, color=LINE, sw=1.5))
    frags.append(arrow(580, 202, 650, 248, color=LINE, sw=1.5))
    frags.append(text(410, 226, "квадратні рівняння 2 (поділ на 4 періоди по 4 доданки)", size=11, color=MUTED, italic=True))

    # Рівень 2: 4 періоди по 4 доданки
    b2_1 = fitbox(50, 250, 160, 50, "η₁₁ (4 доданки)\nζ + ζ⁴ + ζ¹³ + ζ¹⁶", size=10, fill="#fefce8", stroke="#ca8a04", sw=1.3)
    b2_2 = fitbox(220, 250, 160, 50, "η₁₂ (4 доданки)\nζ² + ζ⁸ + ζ⁹ + ζ¹⁵", size=10, fill="#fefce8", stroke="#ca8a04", sw=1.3)
    b2_3 = fitbox(440, 250, 160, 50, "η₂₁ (4 доданки)\nζ³ + ζ⁵ + ζ¹² + ζ¹⁴", size=10, fill="#fefce8", stroke="#ca8a04", sw=1.3)
    b2_4 = fitbox(610, 250, 160, 50, "η₂₂ (4 доданки)\nζ⁶ + ζ⁷ + ζ¹⁰ + ζ¹¹", size=10, fill="#fefce8", stroke="#ca8a04", sw=1.3)
    frags.append(b2_1); frags.append(b2_2); frags.append(b2_3); frags.append(b2_4)

    # Стрілки до рівня 3
    frags.append(arrow(130, 302, 190, 348, color=LINE, sw=1.5))
    frags.append(arrow(290, 302, 230, 348, color=LINE, sw=1.5))
    frags.append(text(210, 328, "квадратне рівняння 3", size=10, color=MUTED, italic=True))

    # Рівень 3: Період з 2 доданків
    b3 = fitbox(110, 350, 220, 50, "η₁₁₁ = ζ¹ + ζ¹⁶ = 2·cos(2π/17)\n(сума двох спряжених)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.8, bold=True)
    frags.append(b3)

    # Стрілка до фінального кореня
    frags.append(arrow(332, 375, 410, 375, color=LINE, sw=1.5))

    # Фінал
    b4 = fitbox(412, 342, 370, 72,
                "Квадратне рівняння 4: x² − (η₁₁₁)·x + 1 = 0\n"
                "→ Отримуємо сам корінь ζ₁₇ = cos(2π/17) + i·sin(2π/17)\n"
                "Висновок: cos(2π/17) виражається через 4 вкладені √\n"
                "⟹ 17-кутник будується циркулем і лінійкою!",
                size=11, fill="#fef2f2", stroke=POS, sw=1.8, bold=True)
    frags.append(b4)

    # Нижній висновок
    frags.append(text(410, 442, "Ступінь [ℚ(ζ₁₇):ℚ] = 16 = 2⁴ є степенем двійки — це критерій Гаусса — Ванцеля для побудови", size=12, color=INK, italic=True))

    render(os.path.join(OUT_DIR, "fig-heptadecagon-periods.svg"), w, h, *frags)


def fig_galois_correspondence():
    """Фігура 3: Відповідність Галуа для кругового поля Q(zeta_12).
    Показує зв'язок між підгрупами групи Галуа (Z/12Z)* = {1, 5, 7, 11} та проміжними полями."""
    w, h = 780, 460
    frags = []

    frags.append(text(390, 26, "Відповідність Галуа для кругового поля ℚ(ζ₁₂)", size=16, bold=True))

    # Ліва колонка: Решітка проміжних полів (знизу вгору: Q -> квадратичні -> Q(zeta_12))
    # Права колонка: Решітка підгруп Gal(Q(zeta_12)/Q) = (Z/12Z)* (згори вниз: G -> підгрупи порядку 2 -> {1})

    frags.append(text(190, 60, "Решітка підполів (вкладення ⊂)", size=14, color=FIELD, bold=True))
    frags.append(text(590, 60, "Решітка підгруп Галуа (включення ⊃)", size=14, color=NEG, bold=True))

    # Вершина полів: Q(zeta_12)
    b_top_field = fitbox(100, 85, 180, 45, "ℚ(ζ₁₂) = ℚ(i, √3)\nступінь 4 над ℚ", size=12, fill="#f0fdf4", stroke=FIELD, sw=1.8, bold=True)
    frags.append(b_top_field)

    # Вершина груп: {1} (тривіальна)
    b_top_group = fitbox(500, 85, 180, 45, "H = {1}\nфіксує все ℚ(ζ₁₂)", size=12, fill="#eff6ff", stroke=NEG, sw=1.8, bold=True)
    frags.append(b_top_group)

    # Середній рівень полів (3 квадратичні розширення)
    b_f1 = fitbox(20, 200, 100, 45, "ℚ(i)\n[ℚ(i):ℚ] = 2", size=11, fill="#f8fafc", stroke=LINE, sw=1.3)
    b_f2 = fitbox(140, 200, 100, 45, "ℚ(√3)\n[ℚ(√3):ℚ] = 2", size=11, fill="#f8fafc", stroke=LINE, sw=1.3)
    b_f3 = fitbox(260, 200, 100, 45, "ℚ(√−3)\n[ℚ(√−3):ℚ] = 2", size=11, fill="#f8fafc", stroke=LINE, sw=1.3)
    frags.append(b_f1); frags.append(b_f2); frags.append(b_f3)

    # Середній рівень груп (3 підгрупи порядку 2 в (Z/12Z)* = {1, 5, 7, 11})
    b_g1 = fitbox(420, 200, 100, 45, "H₁ = {1, 5}\n(σ₅: i ↦ i, √3 ↦ −√3)", size=10, fill="#f8fafc", stroke=LINE, sw=1.3)
    b_g2 = fitbox(540, 200, 100, 45, "H₂ = {1, 11}\n(σ₁₁: спряження)", size=10, fill="#f8fafc", stroke=LINE, sw=1.3)
    b_g3 = fitbox(660, 200, 100, 45, "H₃ = {1, 7}\n(σ₇: i ↦ −i, √3 ↦ √3)", size=10, fill="#f8fafc", stroke=LINE, sw=1.3)
    frags.append(b_g1); frags.append(b_g2); frags.append(b_g3)

    # Дно полів: Q
    b_bot_field = fitbox(100, 315, 180, 45, "ℚ (базове поле)\nступінь 1", size=12, fill="#f8fafc", stroke=LINE, sw=1.5, bold=True)
    frags.append(b_bot_field)

    # Дно груп: G = (Z/12Z)* = Z_2 x Z_2
    b_bot_group = fitbox(490, 315, 200, 45, "G = (ℤ/12ℤ)* = {1, 5, 7, 11}\nізоморфна ℤ/2ℤ × ℤ/2ℤ", size=11, fill="#eff6ff", stroke=NEG, sw=1.5, bold=True)
    frags.append(b_bot_group)

    # Лінії ліворуч (поля)
    frags.append(line(190, 131, 70, 199, color=FIELD, sw=1.4))
    frags.append(line(190, 131, 190, 199, color=FIELD, sw=1.4))
    frags.append(line(190, 131, 310, 199, color=FIELD, sw=1.4))

    frags.append(line(70, 246, 190, 314, color=FIELD, sw=1.4))
    frags.append(line(190, 246, 190, 314, color=FIELD, sw=1.4))
    frags.append(line(310, 246, 190, 314, color=FIELD, sw=1.4))

    # Лінії праворуч (групи)
    frags.append(line(590, 131, 470, 199, color=NEG, sw=1.4))
    frags.append(line(590, 131, 590, 199, color=NEG, sw=1.4))
    frags.append(line(590, 131, 710, 199, color=NEG, sw=1.4))

    frags.append(line(470, 246, 590, 314, color=NEG, sw=1.4))
    frags.append(line(590, 246, 590, 314, color=NEG, sw=1.4))
    frags.append(line(710, 246, 590, 314, color=NEG, sw=1.4))

    # Подвійні стрілки анти-ізоморфізму посередині
    frags.append(line(300, 107, 480, 107, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(370, 222, 410, 222, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(300, 337, 480, 337, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(390, 102, "відповідність 1:1", size=10, color=MUTED))
    frags.append(text(390, 332, "відповідність 1:1", size=10, color=MUTED))

    # Нижній висновок
    b_bot = fitbox(80, 390, 620, 52,
                   "Антиізоморфізм Ґалуа перевертає решітку: більшому підполю відповідає менша підгрупа.\n"
                   "Оскільки група (ℤ/12ℤ)* комутативна (абелева), усі підполя є розширеннями Ґалуа над ℚ.",
                   size=11, fill="#fefce8", stroke="#ca8a04", sw=1.3)
    frags.append(b_bot)

    render(os.path.join(OUT_DIR, "fig-galois-correspondence.svg"), w, h, *frags)


def fig_ring_lwe_lattice():
    """Фігура 4: Кругові кільця в постквантовій решітковій криптографії (Kyber / Dilithium).
    Показує, як фактор-кільце R_q = Z_q[x]/(x^N + 1) замінює N x N матриці поліноміальним множенням."""
    w, h = 800, 460
    frags = []

    frags.append(text(400, 26, "Кругові кільця ℤ_q[x]/(xᴺ + 1) у решітковій криптографії (Kyber / Ring-LWE)", size=15, bold=True))

    # Ліва панель: Стандартний LWE (матриці)
    b_left = fitbox(40, 60, 330, 230,
                    "Стандартний LWE (на загальних решітках):\n\n"
                    "• Секрет s ∈ ℤ_qᴺ, матриця A ∈ ℤ_q^(M × N)\n"
                    "• Відкритий ключ: b = A·s + e (mod q)\n"
                    "• Розмір ключа: M × N елементів ℤ_q\n"
                    "  (сотні кілобайт пам'яті!)\n"
                    "• Множення матриці на вектор: O(N²)\n"
                    "• Надійний, але повільний для інтернету",
                    size=11, pad=10, fill="#f8fafc", stroke=LINE, sw=1.4)
    frags.append(b_left)

    # Права панель: Ring-LWE (круговий многочлен Phi_{2N}(x) = x^N + 1)
    b_right = fitbox(430, 60, 330, 230,
                     "Ring-LWE / Kyber (на кругових кільцях):\n\n"
                     "• Кільце R_q = ℤ_q[x]/(xᴺ + 1)  [N = 256 = 2⁸]\n"
                     "• Замість матриці — ОДИН поліном a(x) ∈ R_q\n"
                     "• Відкритий ключ: b(x) = a(x)·s(x) + e(x)\n"
                     "• Розмір ключа скорочується у N разів (≈ 1 КБ!)\n"
                     "• Множення через ШПФ / NTT: O(N log N)\n"
                     "• Захищений стандарт NIST (ML-KEM / Kyber)",
                     size=11, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.8, bold=True)
    frags.append(b_right)

    # Стрілка переходу між ними
    frags.append(arrow(375, 175, 425, 175, color=FIELD, sw=2.2))
    frags.append(text(400, 160, "xᴺ ≡ −1", size=11, color=FIELD, bold=True))

    # Нижня панель: Геометрія циклотомічного множення (негациклічна матриця)
    b_matrix = fitbox(40, 310, 720, 130,
                      "Чому це працює: алгебраїчна редукція xᴺ ≡ −1 у круговому кільці\n"
                      "Множення на поліном a(x) = a₀ + a₁x + ... + a_{N-1}x^{N-1} рівносильне дії негациркулянтної матриці:\n"
                      "  [  a₀   −a_{N-1}  ...  −a₁  ]\n"
                      "  [  a₁     a₀      ...  −a₂  ]   ← Кожен стовпчик є циклічним зсувом зі зміною знака на межі!\n"
                      "  [ ...    ...      ...  ...  ]\n"
                      "  [ a_{N-1} a_{N-2} ...   a₀  ]   ⟹ Корені Φ_{2N}(x) дають дискретне перетворення Фур'є над ℤ_q.",
                      size=11, pad=8, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(b_matrix)

    render(os.path.join(OUT_DIR, "fig-ring-lwe-lattice.svg"), w, h, *frags)


def main():
    fig_cyclotomic_roots()
    fig_heptadecagon_periods()
    fig_galois_correspondence()
    fig_ring_lwe_lattice()
    print("Усі фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
