# -*- coding: utf-8 -*-
"""Фігури до статті «Теорема Фальтінгса». Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Розкладку тримаємо з запасом — текст не накладається."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Три геометрії — три числові світи (Рід g=0, 1, ≥2) ─────────────
def fig_genus_dichotomy():
    W, H = 820, 390
    f = []

    # 3 панелі
    f.append(rect(20, 45, 245, 315, fill="#f2faf4", stroke=FIELD, sw=2))
    f.append(rect(285, 45, 250, 315, fill="#f4f6f8", stroke=LINE, sw=2))
    f.append(rect(555, 45, 245, 315, fill="#fdf4f3", stroke=POS, sw=2))

    # ── Панель 1: g = 0 (Коніки, коло) ──
    f.append(text(142, 75, "Рід g = 0", size=18, bold=True, color=FIELD))
    f.append(text(142, 98, "Коло, коніки: x² + y² = 1", size=13, color=MUTED, bold=True))
    f.append(circle(142, 185, 55, fill="#ffffff", stroke=FIELD, sw=2))
    # Січна лінія (метод хорди)
    f.append(line(80, 225, 204, 145, color=POS, sw=1.8))
    f.append(circle(87, 220, 4, fill=POS, stroke=POS))
    f.append(text(78, 240, "P₀(-1,0)", size=11, color=POS, bold=True))
    f.append(circle(185, 157, 4, fill=POS, stroke=POS))
    f.append(text(198, 155, "P(t)", size=11, color=POS, bold=True))

    b1, bw1, bh1 = textbox(142, 290, "Якщо є хоча б 1 точка,\nрозв'язків нескінченно багато:\n|C(ℚ)| = ∞", size=12.5, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5)
    f.append(b1)

    # ── Панель 2: g = 1 (Еліптичні криві) ──
    f.append(text(410, 75, "Рід g = 1", size=18, bold=True, color=INK))
    f.append(text(410, 98, "Еліптичні криві: y² = x³ + ax + b", size=13, color=MUTED, bold=True))

    # Рисуємо тороподібне кільце або овал + гілку
    f.append(ellipse(410, 185, 55, 35, fill="#ffffff", stroke=LINE, sw=2))
    f.append(ellipse(410, 185, 20, 10, fill="#f4f6f8", stroke=MUTED, sw=1.5))

    b2, bw2, bh2 = textbox(410, 290, "Теорема Морделла–Вейля:\nC(ℚ) — скінченно породжена група\nМоже бути 0 або ∞ точок", size=12.5, pad=8, fill="#ffffff", stroke=LINE, sw=1.5)
    f.append(b2)

    # ── Панель 3: g ≥ 2 (Теорема Фальтінгса) ──
    f.append(text(677, 75, "Рід g ≥ 2", size=18, bold=True, color=POS))
    f.append(text(677, 98, "Криві вищих родів: xⁿ + yⁿ = 1 (n≥4)", size=12.5, color=POS, bold=True))

    # Подвійний крендель / розвузлений крендель
    f.append(ellipse(635, 185, 38, 28, fill="#ffffff", stroke=POS, sw=2))
    f.append(ellipse(635, 185, 12, 6, fill="#fdf4f3", stroke=POS, sw=1.2))
    f.append(ellipse(719, 185, 38, 28, fill="#ffffff", stroke=POS, sw=2))
    f.append(ellipse(719, 185, 12, 6, fill="#fdf4f3", stroke=POS, sw=1.2))

    # Скінченні точки
    f.append(circle(645, 165, 4.5, fill=POS, stroke=POS))
    f.append(circle(710, 200, 4.5, fill=POS, stroke=POS))
    f.append(text(677, 230, "лише скінченна купка точок", size=11.5, color=POS, italic=True))

    b3, bw3, bh3 = textbox(677, 290, "Теорема Фальтінгса (1983):\nРаціональних точок ЗАВЖДИ\nлише скінченна кількість:\n|C(K)| < ∞", size=12.5, pad=8, fill="#ffffff", stroke=POS, sw=1.8, bold=True)
    f.append(b3)

    render(os.path.join(IMG, "genus-dichotomy.svg"), W, H, *f)


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, stroke, sw))


# ── Фігура 2: Логічна машина доведення Фальтінгса ─────────────────────────────
def fig_faltings_machinery():
    W, H = 800, 520
    f = []

    # Блок 1: Раціональні точки на кривій C(K)
    b1, w1, h1 = textbox(400, 55, "Раціональні точки P ∈ C(K) на кривій роду g ≥ 2\n(Припускаємо, що точки розглядаються над числовим полем K)", size=14, pad=10, fill="#ffffff", stroke=LINE, sw=1.8, bold=True)
    f.append(b1)

    f.append(arrow(400, 95, 400, 140, color=POS, sw=2))
    f.append(text(415, 120, "Конструкція Кодайри–Паршина (нерозгалужені накриття Cₚ → C)", size=12, color=POS, anchor="left", italic=True))

    # Блок 2: Абелеві многовиди A_P
    b2, w2, h2 = textbox(400, 180, "Абелеві многовиди A_P = Jac(Cₚ) фіксованого розміру g'\nта обмеженого провідника N (розгалуження лише в заданих простих)", size=14, pad=10, fill="#ffffff", stroke=LINE, sw=1.8)
    f.append(b2)

    f.append(arrow(400, 220, 400, 265, color=POS, sw=2))
    f.append(text(415, 245, "Доведення Фальтінгса: гіпотеза Тейта, висота Фальтінгса & теорема про ізогенії", size=12, color=POS, anchor="left", italic=True))

    # Блок 3: Гіпотеза Шафаревича
    b3, w3, h3 = textbox(400, 305, "Гіпотеза Шафаревича (доведена Фальтінгсом):\nКласів ізоморфізму таких абелевих многовидів A_P лише СКІНЧЕННА кількість!", size=14, pad=10, fill="#eaf0fd", stroke=NEG, sw=2, bold=True)
    f.append(b3)

    f.append(arrow(400, 345, 400, 390, color=FIELD, sw=2))
    f.append(text(415, 370, "Теорема Тореллі (Cₚ відновлюється за Jac) + скінченність покриттів", size=12, color=FIELD, anchor="left", italic=True))

    # Блок 4: Висновок - Теорема Фальтінгса
    b4, w4, h4 = textbox(400, 440, "ВИСНОВОК: Множина раціональних точок C(K) є СКІНЧЕННОЮ\n|C(K)| < ∞  (Теорема Фальтінгса / Гіпотеза Морделла)", size=15, pad=12, fill="#f2faf4", stroke=FIELD, sw=2.2, color=FIELD, bold=True)
    f.append(b4)

    render(os.path.join(IMG, "faltings-machinery.svg"), W, H, *f)


# ── Фігура 3: Метод Чабауті–Коулмана (p-адичне інтегрування при r < g) ────────
def fig_chabauty_coleman_method():
    W, H = 800, 410
    f = []

    # Заголовок / концептуальні області
    f.append(rect(30, 40, 350, 330, fill="#f4f6f8", stroke=LINE, sw=1.8))
    f.append(text(205, 68, "Геометрія в p-адичному Якобіані J(ℚₚ)", size=15, bold=True))

    # Якобіан J(ℚ_p) - g-вимірний
    f.append(rect(55, 95, 300, 245, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(205, 118, "Якобіан J(ℚₚ) (вимір g)", size=13, color=MUTED, bold=True))

    # Підгрупа J(ℚ) closure - r-вимірна
    f.append(rect(75, 140, 260, 90, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(205, 163, "Замикання раціональних точок J(ℚ)", size=12.5, color=NEG, bold=True))
    f.append(text(205, 185, "вимір r = rank(J(ℚ)) < g", size=13, color=NEG, bold=True))

    # Вкладена крива C(ℚ_p) - 1-вимірна
    f.append(ellipse(205, 280, 110, 30, fill="#fdf4f3", stroke=POS, sw=1.5))
    f.append(text(205, 275, "Вкладена крива C(ℚₚ)", size=12.5, color=POS, bold=True))
    f.append(text(205, 295, "(вимір 1)", size=11.5, color=POS))

    # Дискретні точки перетину
    f.append(circle(145, 270, 5, fill=POS, stroke=POS))
    f.append(circle(265, 270, 5, fill=POS, stroke=POS))
    f.append(text(145, 253, "P₁", size=11, color=POS, bold=True))
    f.append(text(265, 253, "P₂", size=11, color=POS, bold=True))

    # Права панель: p-адичні інтеграли та оцінка
    f.append(rect(410, 40, 360, 330, fill="#f2faf4", stroke=FIELD, sw=1.8))
    f.append(text(590, 68, "Механізм аналітичного вирахування", size=15, bold=True, color=FIELD))

    b1, w1, h1 = textbox(590, 135, "1. p-адичний інтеграл Коулмана:\n∫_P₀^P ω_i = 0  для  i = 1, …, g − r\nде ω_i — анулюючі диференціали", size=13, pad=10, fill="#ffffff", stroke=FIELD, sw=1.5)
    f.append(b1)

    b2, w2, h2 = textbox(590, 230, "2. Локальні нулі p-адичних степенних рядів:\nУ кожній редукційній точці не більше\nза 2g − 2 нулів аналітичних функцій", size=13, pad=10, fill="#ffffff", stroke=FIELD, sw=1.5)
    f.append(b2)

    b3, w3, h3 = textbox(590, 320, "ОЦІНКА КОУЛМАНА:\n|C(ℚ)| ≤ |C(𝔽ₚ)| + 2g − 2\n(При p > 2g та r < g дає явну межу!)", size=13.5, pad=10, fill="#ffffff", stroke=POS, sw=2, color=POS, bold=True)
    f.append(b3)

    render(os.path.join(IMG, "chabauty-coleman-method.svg"), W, H, *f)


if __name__ == "__main__":
    fig_genus_dichotomy()
    fig_faltings_machinery()
    fig_chabauty_coleman_method()
    print("SVG figures successfully generated in ./img/")
