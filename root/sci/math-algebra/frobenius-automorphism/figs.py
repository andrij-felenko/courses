# -*- coding: utf-8 -*-
"""Фігури для статті «Автоморфізм Фробеніуса».
Запуск із кореня репо:  python book/math/algebra/frobenius-automorphism/figs.py
або з теки теми:       python figs.py
"""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра теми
C_BLUE_BG   = "#eef4fd"
C_BLUE_BD   = "#2457d6"
C_GREEN_BG  = "#ebfaf0"
C_GREEN_BD  = "#1e824c"
C_PURPLE_BG = "#f5eeff"
C_PURPLE_BD = "#7d3c98"
C_ORANGE_BG = "#fef5e7"
C_ORANGE_BD = "#d35400"
C_RED_BG    = "#fdeeed"
C_RED_BD    = "#c0392b"
C_GRAY_BG   = "#f8f9fa"
C_GRAY_BD   = "#7f8c8d"

def poly(pts, fill=LINE, stroke="none", sw=1):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)

def path_tag(d, fill="none", stroke=LINE, sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Freshman's Dream: Трикутник Паскаля за модулем p = 5
# ─────────────────────────────────────────────────────────────────────────────
def fig_freshman_dream():
    W, H = 840, 420
    p = []

    # Заголовок
    p.append(text(W/2, 28, "«Мрія першокурсника» та зникнення проміжних біноміальних коефіцієнтів", size=16, bold=True))
    p.append(text(W/2, 48, "У характеристиці p = 5 усі коефіцієнти C(5, k) для 1 ≤ k ≤ 4 діляться на 5 і перетворюються на 0", size=12, color=MUTED, italic=True))

    # Лівий блок: класичний біноміальний розклад (a + b)⁵
    bx, by, bw, bh = 40, 75, 360, 315
    p.append(rect(bx, by, bw, bh, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(bx, by, bw, 32, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=8))
    p.append(text(bx + bw/2, by + 21, "Розклад у звичайній алгебрі (над ℤ або ℝ)", size=13, bold=True, color=C_BLUE_BD))

    p.append(text(bx + 20, by + 65, "(a + b)⁵ = C(5,0)·a⁵ + C(5,1)·a⁴b + C(5,2)·a³b²", size=12, anchor="start", bold=True))
    p.append(text(bx + 85, by + 85, "+ C(5,3)·a²b³ + C(5,4)·ab⁴ + C(5,5)·b⁵", size=12, anchor="start", bold=True))

    terms = [
        ("C(5, 0) = 1", "крайовий член: a⁵"),
        ("C(5, 1) = 5", "містить множник 5 (5 · a⁴b)"),
        ("C(5, 2) = 10", "містить множник 5 (2 · 5 · a³b²)"),
        ("C(5, 3) = 10", "містить множник 5 (2 · 5 · a²b³)"),
        ("C(5, 4) = 5", "містить множник 5 (5 · ab⁴)"),
        ("C(5, 5) = 1", "крайовий член: b⁵"),
    ]
    for i, (coeff, desc) in enumerate(terms):
        ty = by + 120 + i * 28
        is_inner = 1 <= i <= 4
        c_bg = C_RED_BG if is_inner else C_GREEN_BG
        c_bd = C_RED_BD if is_inner else C_GREEN_BD
        p.append(rect(bx + 15, ty - 14, 95, 22, fill=c_bg, stroke=c_bd, sw=1, rx=4))
        p.append(text(bx + 62, ty + 2, coeff, size=11, bold=True, color=c_bd))
        p.append(text(bx + 120, ty + 2, desc, size=11, color=INK, anchor="start"))

    p.append(text(bx + bw/2, by + bh - 15, "Кожен внутрішній коефіцієнт: 5 | C(5, k)", size=11, bold=True, color=POS))

    # Стрілка переходу від ℤ до поля характеристики 5
    p.append(line(415, 230, 445, 230, color=LINE, sw=2))
    p.append(poly([(445, 224), (457, 230), (445, 236)], fill=LINE))
    p.append(text(435, 215, "mod 5", size=11, bold=True, color=C_PURPLE_BD))

    # Правий блок: дія за модулем p = 5
    rx_b, ry_b, rw_b, rh_b = 470, 75, 330, 315
    p.append(rect(rx_b, ry_b, rw_b, rh_b, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(rx_b, ry_b, rw_b, 32, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=8))
    p.append(text(rx_b + rw_b/2, ry_b + 21, "Дія у полі характеристики p = 5 (GF(5ⁿ))", size=13, bold=True, color=C_GREEN_BD))

    p.append(text(rx_b + 20, ry_b + 65, "(a + b)⁵ ≡ 1·a⁵ + 0·a⁴b + 0·a³b²", size=12, anchor="start", bold=True))
    p.append(text(rx_b + 95, ry_b + 85, "+ 0·a²b³ + 0·ab⁴ + 1·b⁵ (mod 5)", size=12, anchor="start", bold=True))

    res_box_y = ry_b + 120
    p.append(rect(rx_b + 20, res_box_y, rw_b - 40, 70, fill=C_PURPLE_BG, stroke=C_PURPLE_BD, sw=1.5, rx=6))
    p.append(text(rx_b + rw_b/2, res_box_y + 28, "(a + b)⁵ = a⁵ + b⁵", size=17, bold=True, color=C_PURPLE_BD))
    p.append(text(rx_b + rw_b/2, res_box_y + 52, "Піднесення до степеня p є адитивним!", size=11, bold=True, color=INK))

    p.append(text(rx_b + 20, ry_b + 225, "Властивості автоморфізму Фробеніуса σ(x) = x⁵:", size=11, bold=True, anchor="start"))
    p.append(text(rx_b + 25, ry_b + 248, "• Зберігає додавання: σ(a + b) = σ(a) + σ(b)", size=11, anchor="start"))
    p.append(text(rx_b + 25, ry_b + 270, "• Зберігає множення: σ(a · b) = σ(a) · σ(b)", size=11, anchor="start"))
    p.append(text(rx_b + 25, ry_b + 292, "• Фіксує базове поле: ∀ c ∈ GF(5): σ(c) = c", size=11, anchor="start", color=C_GREEN_BD, bold=True))

    render(os.path.join(IMG, "freshman-dream-mod-p.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Орбіти автоморфізму Фробеніуса у полі GF(2⁴)
# ─────────────────────────────────────────────────────────────────────────────
def fig_frobenius_orbits():
    W, H = 840, 430
    p = []

    # Заголовок
    p.append(text(W/2, 26, "Орбіти автоморфізму Фробеніуса σ(x) = x² у полі GF(2⁴)", size=16, bold=True))
    p.append(text(W/2, 46, "Поле породжене многочленом f(x) = x⁴ + x + 1, корінь α. Степінь розширення [GF(2⁴) : GF(2)] = 4", size=12, color=MUTED, italic=True))

    # Секція підполя GF(2) (орбіти довжини 1)
    b1_x, b1_y, b1_w, b1_h = 40, 75, 230, 150
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(b1_x, b1_y, b1_w, 28, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=6))
    p.append(text(b1_x + b1_w/2, b1_y + 18, "Орбіти довжини 1: GF(2)", size=12, bold=True, color=C_GREEN_BD))

    # Орбіта {0}
    p.append(circle(b1_x + 60, b1_y + 75, 18, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.5))
    p.append(text(b1_x + 60, b1_y + 80, "0", size=12, bold=True))
    p.append(path_tag("M %d %d A 14 14 0 1 1 %d %d" % (b1_x + 50, b1_y + 60, b1_x + 70, b1_y + 60), stroke=C_GREEN_BD, sw=1.5))
    p.append(poly([(b1_x + 73, b1_y + 60), (b1_x + 70, b1_y + 53), (b1_x + 65, b1_y + 63)], fill=C_GREEN_BD))
    p.append(text(b1_x + 60, b1_y + 115, "0² = 0", size=11, color=MUTED))

    # Орбіта {1}
    p.append(circle(b1_x + 165, b1_y + 75, 18, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.5))
    p.append(text(b1_x + 165, b1_y + 80, "1", size=12, bold=True))
    p.append(path_tag("M %d %d A 14 14 0 1 1 %d %d" % (b1_x + 155, b1_y + 60, b1_x + 175, b1_y + 60), stroke=C_GREEN_BD, sw=1.5))
    p.append(poly([(b1_x + 178, b1_y + 60), (b1_x + 175, b1_y + 53), (b1_x + 170, b1_y + 63)], fill=C_GREEN_BD))
    p.append(text(b1_x + 165, b1_y + 115, "1² = 1", size=11, color=MUTED))
    p.append(text(b1_x + b1_w/2, b1_y + 138, "Фіксоване поле Fix(σ)", size=10, bold=True, color=C_GREEN_BD))

    # Секція підполя GF(2²) (орбіта довжини 2)
    b2_x, b2_y, b2_w, b2_h = 40, 240, 230, 165
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(b2_x, b2_y, b2_w, 28, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=6))
    p.append(text(b2_x + b2_w/2, b2_y + 18, "Орбіта довжини 2: GF(2²)", size=12, bold=True, color=C_BLUE_BD))

    # Вузли α⁵ та α¹⁰
    p.append(circle(b2_x + 65, b2_y + 85, 20, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.5))
    p.append(text(b2_x + 65, b2_y + 90, "α⁵", size=12, bold=True))
    p.append(circle(b2_x + 165, b2_y + 85, 20, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.5))
    p.append(text(b2_x + 165, b2_y + 90, "α¹⁰", size=12, bold=True))

    # Стрілки туди й назад
    p.append(path_tag("M %d %d Q %d %d %d %d" % (b2_x + 85, b2_y + 75, b2_x + 115, b2_y + 60, b2_x + 145, b2_y + 75), stroke=C_BLUE_BD, sw=1.5))
    p.append(poly([(b2_x + 147, b2_y + 76), (b2_x + 138, b2_y + 70), (b2_x + 140, b2_y + 80)], fill=C_BLUE_BD))

    p.append(path_tag("M %d %d Q %d %d %d %d" % (b2_x + 145, b2_y + 95, b2_x + 115, b2_y + 110, b2_x + 85, b2_y + 95), stroke=C_BLUE_BD, sw=1.5))
    p.append(poly([(b2_x + 83, b2_y + 94), (b2_x + 92, b2_y + 100), (b2_x + 90, b2_y + 90)], fill=C_BLUE_BD))

    p.append(text(b2_x + b2_w/2, b2_y + 135, "(α⁵)² = α¹⁰,  (α¹⁰)² = α²⁰ = α⁵", size=10, color=MUTED))
    p.append(text(b2_x + b2_w/2, b2_y + 153, "Мінімал. многочлен: x² + x + 1", size=10, bold=True, color=C_BLUE_BD))

    # Права секція: Орбіти довжини 4 (примітивні елементи поля GF(2⁴))
    b3_x, b3_y, b3_w, b3_h = 290, 75, 510, 330
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(b3_x, b3_y, b3_w, 28, fill=C_PURPLE_BG, stroke=C_PURPLE_BD, sw=1.2, rx=6))
    p.append(text(b3_x + b3_w/2, b3_y + 18, "Три орбіти довжини 4 (породжують незвідні многочлени степеня 4 над GF(2))", size=12, bold=True, color=C_PURPLE_BD))

    # 3 циклічні діаграми для трьох орбіт довжини 4
    orbit_data = [
        ("Орбіта 1: {α, α², α⁴, α⁸}", ["α", "α²", "α⁴", "α⁸"], "m₁(x) = x⁴ + x + 1", 400, 160, C_PURPLE_BG, C_PURPLE_BD),
        ("Орбіта 2: {α³, α⁶, α¹², α⁹}", ["α³", "α⁶", "α¹²", "α⁹"], "m₂(x) = x⁴ + x³ + x² + x + 1", 670, 160, C_ORANGE_BG, C_ORANGE_BD),
        ("Орбіта 3: {α⁷, α¹⁴, α¹³, α¹¹}", ["α⁷", "α¹⁴", "α¹³", "α¹¹"], "m₃(x) = x⁴ + x³ + 1", 535, 295, C_RED_BG, C_RED_BD),
    ]

    for title_orb, nodes, poly_lbl, cx, cy, c_bg, c_bd in orbit_data:
        rad = 30
        coords = [
            (cx, cy - rad),
            (cx + rad + 10, cy),
            (cx, cy + rad),
            (cx - rad - 10, cy),
        ]
        for idx in range(4):
            x1, y1 = coords[idx]
            x2, y2 = coords[(idx + 1) % 4]
            p.append(line(x1, y1, x2, y2, color=c_bd, sw=1.5))
        
        for idx, (nx, ny) in enumerate(coords):
            p.append(circle(nx, ny, 13, fill=c_bg, stroke=c_bd, sw=1.2))
            p.append(text(nx, ny + 4, nodes[idx], size=10, bold=True))

        p.append(text(cx, cy - rad - 14, title_orb, size=10, bold=True, color=c_bd))
        p.append(text(cx, cy + rad + 16, poly_lbl, size=9, bold=True, color=INK))

    render(os.path.join(IMG, "frobenius-galois-orbits.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Прискорення Кобліца: τ-адичний розклад проти Double-and-Add
# ─────────────────────────────────────────────────────────────────────────────
def fig_koblitz_pipeline():
    W, H = 840, 420
    p = []

    # Заголовок
    p.append(text(W/2, 26, "Обчислення скаляра k·P на кривих Кобліца: Класичний метод vs Автоморфізм Фробеніуса", size=16, bold=True))
    p.append(text(W/2, 46, "Заміна дорогих подвоєнь точок 2·P на миттєве піднесення координат до квадрата τ(P) = (x², y²)", size=12, color=MUTED, italic=True))

    # Верхній конвеєр: Стандартний Double-and-Add
    y1 = 80
    p.append(rect(40, y1, 760, 140, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(40, y1, 760, 28, fill=C_RED_BG, stroke=C_RED_BD, sw=1.2, rx=8))
    p.append(text(420, y1 + 18, "Класичний алгоритм Double-and-Add (двійковий розклад скаляра k)", size=13, bold=True, color=C_RED_BD))

    # Блоки конвеєра 1
    c1_steps = [
        ("Скаляр k", "k = (kₘ...k₀)₂", 110, C_GRAY_BG, C_GRAY_BD),
        ("Подвоєння 2·Q", "Множення, ділення в GF(2ᵐ)\nЦіна: 1I + 2M + 1S (~150 тактів)", 310, C_RED_BG, C_RED_BD),
        ("Умовне додавання", "Q = Q + P (якщо kᵢ = 1)\nЦіна: 1I + 2M (~130 тактів)", 530, C_ORANGE_BG, C_ORANGE_BD),
        ("Результат k·P", "m подвоєнь + m/2 додавань", 720, C_GREEN_BG, C_GREEN_BD),
    ]

    for name, desc, cx, c_bg, c_bd in c1_steps:
        bw, bh = 140, 75
        p.append(rect(cx - bw/2, y1 + 45, bw, bh, fill=c_bg, stroke=c_bd, sw=1.2, rx=6))
        p.append(text(cx, y1 + 65, name, size=11, bold=True, color=c_bd))
        p.append(mtext(cx, y1 + 83, desc, size=9, color=INK, lh=1.2))

    p.append(line(180, y1 + 82, 235, y1 + 82, color=LINE, sw=1.5))
    p.append(poly([(235, y1 + 78), (243, y1 + 82), (235, y1 + 86)], fill=LINE))

    p.append(line(380, y1 + 82, 455, y1 + 82, color=LINE, sw=1.5))
    p.append(poly([(455, y1 + 78), (463, y1 + 82), (455, y1 + 86)], fill=LINE))

    p.append(line(600, y1 + 82, 645, y1 + 82, color=LINE, sw=1.5))
    p.append(poly([(645, y1 + 78), (653, y1 + 82), (645, y1 + 86)], fill=LINE))

    # Нижній конвеєр: Кобліц τ-NAF
    y2 = 245
    p.append(rect(40, y2, 760, 150, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(40, y2, 760, 28, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=8))
    p.append(text(420, y2 + 18, "Прискорення Кобліца через τ-NAF (тау-адичний розклад автоморфізму Фробеніуса)", size=13, bold=True, color=C_GREEN_BD))

    # Блоки конвеєра 2
    c2_steps = [
        ("τ-NAF розклад", "k = ∑ uᵢ·τⁱ, uᵢ ∈ {0, ±1}\nЩільність ненульових: 1/3", 110, C_BLUE_BG, C_BLUE_BD),
        ("Фробеніус τ(Q)", "τ(x, y) = (x², y²)\nУ норм. базисі: 0–1 такт CPU!", 310, C_GREEN_BG, C_GREEN_BD),
        ("Додавання / віднімання", "Q = Q ± P (якщо uᵢ = ±1)\nУсього m/3 операцій", 530, C_ORANGE_BG, C_ORANGE_BD),
        ("Результат k·P", "0 подвоєнь точок!\nПрискорення у 3–5 разів", 720, C_PURPLE_BG, C_PURPLE_BD),
    ]

    for name, desc, cx, c_bg, c_bd in c2_steps:
        bw, bh = 140, 85
        p.append(rect(cx - bw/2, y2 + 45, bw, bh, fill=c_bg, stroke=c_bd, sw=1.2, rx=6))
        p.append(text(cx, y2 + 65, name, size=11, bold=True, color=c_bd))
        p.append(mtext(cx, y2 + 83, desc, size=9, color=INK, lh=1.2))

    p.append(line(180, y2 + 87, 235, y2 + 87, color=LINE, sw=1.5))
    p.append(poly([(235, y2 + 83), (243, y2 + 87), (235, y2 + 91)], fill=LINE))

    p.append(line(380, y2 + 87, 455, y2 + 87, color=LINE, sw=1.5))
    p.append(poly([(455, y2 + 83), (463, y2 + 87), (455, y2 + 91)], fill=LINE))

    p.append(line(600, y2 + 87, 645, y2 + 87, color=LINE, sw=1.5))
    p.append(poly([(645, y2 + 83), (653, y2 + 87), (645, y2 + 91)], fill=LINE))

    render(os.path.join(IMG, "koblitz-frobenius-action.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Алгоритм Шуфа: Слід Фробеніуса та підрахунок точок кривої
# ─────────────────────────────────────────────────────────────────────────────
def fig_schoof_trace():
    W, H = 840, 420
    p = []

    # Заголовок
    p.append(text(W/2, 26, "Алгоритм Шуфа: Визначення сліду Фробеніуса та кількості точок кривої #E(GF(q))", size=16, bold=True))
    p.append(text(W/2, 46, "Характеристичне рівняння: π²(P) - t·π(P) + q·P = 𝒪 для точок кручення P ∈ E[l]", size=12, color=MUTED, italic=True))

    # Центральне рівняння
    eq_y = 75
    p.append(rect(180, eq_y, 480, 50, fill=C_PURPLE_BG, stroke=C_PURPLE_BD, sw=1.5, rx=6))
    p.append(text(420, eq_y + 24, "π² - t · π + q = 0  на кільці ендоморфізмів End(E)", size=13, bold=True, color=C_PURPLE_BD))
    p.append(text(420, eq_y + 42, "Слід Фробеніуса t пов'язаний із кількістю точок: #E(GF(q)) = q + 1 - t", size=11, bold=True, color=INK))

    # Ліва колонка: Прості числа l і многочлени поділу
    y_blocks = 145
    p.append(rect(40, y_blocks, 220, 245, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(40, y_blocks, 220, 28, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=6))
    p.append(text(150, y_blocks + 18, "1. Малі прості l ∈ {2, 3, 5, 7, ...}", size=11, bold=True, color=C_BLUE_BD))

    p.append(text(50, y_blocks + 48, "Обираємо набір простих чисел:", size=10, anchor="start"))
    p.append(text(50, y_blocks + 66, "L = {l₁, l₂, ..., lₖ} таких, що:", size=10, anchor="start", bold=True))
    p.append(text(50, y_blocks + 88, "∏ lᵢ > 4·√q  (межа Хассе)", size=11, anchor="start", color=POS, bold=True))

    p.append(text(50, y_blocks + 120, "Многочлени поділу ψₗ(x):", size=10, anchor="start", bold=True))
    p.append(text(50, y_blocks + 138, "Корені ψₗ(x) — це точно", size=10, anchor="start"))
    p.append(text(50, y_blocks + 154, "x-координати точок l-кручення", size=10, anchor="start"))
    p.append(text(50, y_blocks + 172, "E[l] = {P ∈ E : l·P = 𝒪}", size=10, anchor="start", bold=True))
    p.append(text(50, y_blocks + 200, "Степінь ψₗ: deg ≈ (l² - 1)/2", size=10, anchor="start", color=MUTED))

    # Центральна колонка: Обчислення за модулем (ψ_l(x), x^q - x)
    p.append(rect(280, y_blocks, 280, 245, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(280, y_blocks, 280, 28, fill=C_ORANGE_BG, stroke=C_ORANGE_BD, sw=1.2, rx=6))
    p.append(text(420, y_blocks + 18, "2. Символьна перевірка tₗ mod l", size=11, bold=True, color=C_ORANGE_BD))

    p.append(text(290, y_blocks + 48, "Для кожного можливого τ ∈ [0, l - 1]:", size=10, anchor="start"))
    p.append(text(290, y_blocks + 75, "Обчислюємо дію на точці (x, y):", size=10, anchor="start"))
    
    p.append(rect(290, y_blocks + 90, 260, 60, fill=C_ORANGE_BG, stroke=C_ORANGE_BD, sw=1, rx=4))
    p.append(text(420, y_blocks + 112, "(x^(q²), y^(q²)) + (q mod l)·(x, y)", size=10, bold=True))
    p.append(text(420, y_blocks + 132, "= τ · (x^q, y^q)  mod (ψₗ(x), y² - f(x))", size=10, bold=True, color=C_ORANGE_BD))

    p.append(text(290, y_blocks + 175, "Піднесення до степеня q — це", size=10, anchor="start"))
    p.append(text(290, y_blocks + 192, "автоморфізм Фробеніуса x ↦ x^q.", size=10, anchor="start", bold=True))
    p.append(text(290, y_blocks + 215, "Знайдено точний залишок: t ≡ tₗ (mod l)", size=10, anchor="start", color=POS, bold=True))

    # Права колонка: Китайська теорема про остачі (CRT)
    p.append(rect(580, y_blocks, 220, 245, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(580, y_blocks, 220, 28, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=6))
    p.append(text(690, y_blocks + 18, "3. Відновлення через CRT", size=11, bold=True, color=C_GREEN_BD))

    p.append(text(590, y_blocks + 48, "Система конгруенцій:", size=10, anchor="start"))
    p.append(text(600, y_blocks + 70, "t ≡ t₁ (mod l₁)", size=10, anchor="start", bold=True))
    p.append(text(600, y_blocks + 90, "t ≡ t₂ (mod l₂)", size=10, anchor="start", bold=True))
    p.append(text(600, y_blocks + 110, "...", size=10, anchor="start", bold=True))
    p.append(text(600, y_blocks + 130, "t ≡ tₖ (mod lₖ)", size=10, anchor="start", bold=True))

    p.append(text(590, y_blocks + 160, "За теоремою Хассе |t| ≤ 2·√q,", size=10, anchor="start"))
    p.append(text(590, y_blocks + 178, "тому розв'язок t єдиний у ℤ!", size=10, anchor="start", bold=True))

    res_y = y_blocks + 195
    p.append(rect(590, res_y, 200, 38, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.5, rx=4))
    p.append(text(690, res_y + 23, "#E(GF(q)) = q + 1 - t", size=12, bold=True, color=C_GREEN_BD))

    # Стрілки між колонками
    p.append(line(260, y_blocks + 120, 280, y_blocks + 120, color=LINE, sw=1.5))
    p.append(poly([(276, y_blocks + 116), (284, y_blocks + 120), (276, y_blocks + 124)], fill=LINE))

    p.append(line(560, y_blocks + 120, 580, y_blocks + 120, color=LINE, sw=1.5))
    p.append(poly([(576, y_blocks + 116), (584, y_blocks + 120), (576, y_blocks + 124)], fill=LINE))

    render(os.path.join(IMG, "schoof-frobenius-trace.svg"), W, H, *p)


if __name__ == "__main__":
    fig_freshman_dream()
    fig_frobenius_orbits()
    fig_koblitz_pipeline()
    fig_schoof_trace()
    print("Всі фігури згенеровано успішно.")
