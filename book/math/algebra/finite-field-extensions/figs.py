# -*- coding: utf-8 -*-
"""Фігури для статті «Розширення скінченних полів».
Запуск із кореня репо:  python book/math/algebra/finite-field-extensions/figs.py
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


# ─────────────────────────────────────────────────────────────────────────────
# 1. Побудова поля F_{p^n} як фактор-кільця F_p[x] / (f(x))
# ─────────────────────────────────────────────────────────────────────────────
def fig_field_extension_construction():
    W, H = 840, 430
    p = []

    # Заголовок
    p.append(text(W/2, 28, "Алгебраїчна побудова скінченного поля F_p^n як фактор-кільця F_p[x] / (f(x))", size=15, bold=True))
    p.append(text(W/2, 48, "Многочлени довільного степеня редукуються за модулем незвідного f(x) степеня n", size=12, color=MUTED, italic=True))

    # Лівий блок: Кільце поліномів F_p[x] (нескінченне)
    bx1, by1, bw1, bh1 = 40, 75, 230, 320
    p.append(rect(bx1, by1, bw1, bh1, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(bx1, by1, bw1, 32, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=8))
    p.append(text(bx1 + bw1/2, by1 + 21, "Кільце поліномів F_p[x]", size=13, bold=True, color=C_BLUE_BD))
    p.append(text(bx1 + bw1/2, by1 + 60, "Нескінченна множина", size=11, color=MUTED))
    p.append(text(bx1 + bw1/2, by1 + 80, "A(x) = c_m x^m + ... + c_0", size=12, bold=True))
    
    examples = [
        "c_i ∈ F_p = {0, 1, ..., p-1}",
        "Степінь deg(A) ≥ 0",
        "Звичайне множення поліномів",
        "deg(A · B) = deg(A) + deg(B)",
        "Ділення з остачею"
    ]
    for i, ex in enumerate(examples):
        p.append(rect(bx1 + 15, by1 + 110 + i * 36, bw1 - 30, 26, fill=C_GRAY_BG, stroke=C_GRAY_BD, sw=1, rx=4))
        p.append(text(bx1 + bw1/2, by1 + 127 + i * 36, ex, size=11))

    # Центральна стрілка-факторизація
    p.append(arrow(280, 235, 345, 235, color=C_RED_BD, sw=2.5))
    p.append(rect(280, 160, 65, 55, fill=C_RED_BG, stroke=C_RED_BD, sw=1.2, rx=6))
    p.append(text(312, 180, "mod f(x)", size=12, bold=True, color=C_RED_BD))
    p.append(text(312, 198, "deg(f) = n", size=11, color=C_RED_BD))

    # Блок посередині: Ідеал (f(x)) та фактор-відображення
    bx2, by2, bw2, bh2 = 355, 75, 445, 320
    p.append(rect(bx2, by2, bw2, bh2, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(bx2, by2, bw2, 32, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=8))
    p.append(text(bx2 + bw2/2, by2 + 21, "Скінченне поле розширення F_p^n ≅ F_p[x] / (f(x))", size=13, bold=True, color=C_GREEN_BD))

    # Канонічні залишки
    p.append(text(bx2 + bw2/2, by2 + 58, "Рівно p^n канонічних елементів: поліноми степеня < n", size=12, bold=True))
    p.append(rect(bx2 + 20, by2 + 75, bw2 - 40, 48, fill=C_ORANGE_BG, stroke=C_ORANGE_BD, sw=1.2, rx=6))
    p.append(text(bx2 + bw2/2, by2 + 95, "r(x) = a_{n-1} x^{n-1} + a_{n-2} x^{n-2} + ... + a_1 x + a_0", size=12, bold=True, color=C_ORANGE_BD))
    p.append(text(bx2 + bw2/2, by2 + 113, "Кожен коефіцієнт a_i має p варіантів ⇒ разом p · p · ... · p = p^n елементів", size=11, color=INK))

    # Структура операцій
    p.append(rect(bx2 + 20, by2 + 135, 195, 160, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(bx2 + 117, by2 + 155, "Канонічний базис над F_p", size=12, bold=True, color=C_BLUE_BD))
    p.append(text(bx2 + 117, by2 + 175, "B = {1, α, α^2, ..., α^{n-1}}", size=11, bold=True))
    p.append(text(bx2 + 117, by2 + 195, "де α = x mod f(x), f(α) = 0", size=11, italic=True))
    p.append(text(bx2 + 117, by2 + 225, "Векторний вигляд:", size=11, bold=True))
    p.append(text(bx2 + 117, by2 + 245, "(a_0, a_1, ..., a_{n-1}) ∈ F_p^n", size=11))
    p.append(text(bx2 + 117, by2 + 275, "Додавання: покомпонентно", size=11, color=FIELD))

    p.append(rect(bx2 + 225, by2 + 135, 200, 160, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(bx2 + 325, by2 + 155, "Множення та обернення", size=12, bold=True, color=C_PURPLE_BD))
    p.append(text(bx2 + 325, by2 + 175, "a(x) · b(x) = (a·b) mod f(x)", size=11, bold=True))
    p.append(text(bx2 + 325, by2 + 198, "Незвідність f(x) гарантує:", size=11, italic=True))
    p.append(text(bx2 + 325, by2 + 218, "НСД(a(x), f(x)) = 1 для a ≠ 0", size=11))
    p.append(text(bx2 + 325, by2 + 245, "Розширений алгоритм Евкліда:", size=11, bold=True))
    p.append(text(bx2 + 325, by2 + 265, "u(x)a(x) + v(x)f(x) = 1", size=11))
    p.append(text(bx2 + 325, by2 + 283, "⇒ a^{-1}(x) = u(x) mod f(x)", size=11, color=C_PURPLE_BD, bold=True))

    render(os.path.join(IMG, "field-extension-construction.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Ґратка підполів GF(2^12) та критерій подільності d | n
# ─────────────────────────────────────────────────────────────────────────────
def fig_subfield_lattice():
    W, H = 840, 440
    p = []

    p.append(text(W/2, 26, "Ґратка підполів поля GF(2^12) та критерій вкладення d | n", size=15, bold=True))
    p.append(text(W/2, 45, "Підполе F_p^d міститься у F_p^n тоді й лише тоді, коли степінь d ділить n без остачі", size=12, color=MUTED, italic=True))

    nodes = {
        "GF12": (420, 85,  "GF(2^12)", "4096 елементів", C_RED_BG, C_RED_BD),
        "GF6":  (260, 175, "GF(2^6)",  "64 елементи",     C_PURPLE_BG, C_PURPLE_BD),
        "GF4":  (580, 175, "GF(2^4)",  "16 елементів",    C_ORANGE_BG, C_ORANGE_BD),
        "GF3":  (180, 265, "GF(2^3)",  "8 елементів",     C_BLUE_BG, C_BLUE_BD),
        "GF2_2":(460, 265, "GF(2^2)",  "4 елементи",      C_GREEN_BG, C_GREEN_BD),
        "GF1":  (420, 365, "GF(2)",    "2 елементи (базове поле)", C_GRAY_BG, C_GRAY_BD),
    }

    edges = [
        ("GF12", "GF6",   "степінь [12:6] = 2", -25, 0),
        ("GF12", "GF4",   "степінь [12:4] = 3", 25, 0),
        ("GF6",  "GF3",   "степінь [6:3] = 2",  -20, 0),
        ("GF6",  "GF2_2", "степінь [6:2] = 3",  15, -10),
        ("GF4",  "GF2_2", "степінь [4:2] = 2",  -15, -10),
        ("GF3",  "GF1",   "степінь [3:1] = 3",  -25, 10),
        ("GF2_2","GF1",   "степінь [2:1] = 2",  20, 10),
    ]

    # Малюємо лінії ребер
    for u, v, lbl, dx, dy in edges:
        x1, y1 = nodes[u][0], nodes[u][1]
        x2, y2 = nodes[v][0], nodes[v][1]
        p.append(line(x1, y1 + 18, x2, y2 - 18, color=LINE, sw=1.5))
        mx, my = (x1 + x2)/2 + dx, (y1 + y2)/2 + dy
        p.append(rect(mx - 48, my - 9, 96, 18, fill=BG, stroke=MUTED, sw=0.8, rx=3))
        p.append(text(mx, my + 4, lbl, size=9, color=INK))

    # Малюємо вузли
    for k, (x, y, title_txt, sub_txt, bg_c, bd_c) in nodes.items():
        nw, nh = (180, 42) if k == "GF1" else (130, 42)
        p.append(rect(x - nw/2, y - nh/2, nw, nh, fill=bg_c, stroke=bd_c, sw=1.5, rx=6))
        p.append(text(x, y - 3, title_txt, size=12, bold=True, color=bd_c))
        p.append(text(x, y + 13, sub_txt, size=10, color=MUTED))

    # Бічна виноска: чому GF(2^3) не є підполем GF(2^4)
    p.append(rect(670, 245, 150, 130, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(745, 268, "Критерій d | n", size=11, bold=True, color=C_RED_BD))
    p.append(text(745, 290, "3 ∤ 4 ⇒ GF(2^3) ⊈ GF(2^4)", size=10, bold=True))
    p.append(text(745, 310, "Перетин підполів:", size=10, color=MUTED))
    p.append(text(745, 330, "GF(2^3) ∩ GF(2^4) = GF(2)", size=10, bold=True))
    p.append(text(745, 355, "НСД(3, 4) = 1 ⇒ GF(2^1)", size=10, color=FIELD))

    render(os.path.join(IMG, "subfield-lattice.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Орбіти Фробеніуса, слід і норма в GF(2^4)
# ─────────────────────────────────────────────────────────────────────────────
def fig_frobenius_orbits_trace():
    W, H = 840, 430
    p = []

    p.append(text(W/2, 28, "Автоморфізм Фробеніуса σ: x ↦ x^2, орбіти спряження, слід і норма в GF(2^4)", size=15, bold=True))
    p.append(text(W/2, 48, "Многочлен f(x) = x^4 + x + 1. Автоморфізм σ розбиває поле на неперетинні класи спряженості", size=12, color=MUTED, italic=True))

    hx, hy, hw, hh = 40, 75, 760, 320
    p.append(rect(hx, hy, hw, hh, fill=BG, stroke=LINE, sw=1.2, rx=8))
    
    # Шапка
    p.append(rect(hx, hy, hw, 32, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=8))
    p.append(text(hx + 90, hy + 21, "Орбіта під дією σ(x) = x^2", size=12, bold=True, color=C_BLUE_BD))
    p.append(text(hx + 280, hy + 21, "Мінімальний многочлен над F_2", size=12, bold=True, color=C_BLUE_BD))
    p.append(text(hx + 470, hy + 21, "Розмір орбіти", size=12, bold=True, color=C_BLUE_BD))
    p.append(text(hx + 580, hy + 21, "Слід Tr(β)", size=12, bold=True, color=C_BLUE_BD))
    p.append(text(hx + 690, hy + 21, "Норма N(β)", size=12, bold=True, color=C_BLUE_BD))

    rows = [
        ("{ 0 }", "x", "1 (нерухома)", "0", "0", C_GRAY_BG, C_GRAY_BD),
        ("{ 1 }", "x + 1", "1 (нерухома)", "0 (1+1+1+1)", "1", C_GRAY_BG, C_GRAY_BD),
        ("{ α^5, α^10 }", "x^2 + x + 1  [підполе GF(2^2)]", "2 (дільник 4)", "0 (α^5 + α^10 = 0)", "1", C_GREEN_BG, C_GREEN_BD),
        ("{ α, α^2, α^4, α^8 }", "x^4 + x + 1  [корінь задає GF(2^4)]", "4 (повна орбіта)", "0 (α+α^2+α^4+α^8)", "1", C_ORANGE_BG, C_ORANGE_BD),
        ("{ α^3, α^6, α^12, α^9 }", "x^4 + x^3 + x^2 + x + 1", "4 (повна орбіта)", "0", "1", C_PURPLE_BG, C_PURPLE_BD),
        ("{ α^7, α^14, α^13, α^11 }", "x^4 + x^3 + 1", "4 (повна орбіта)", "1 (Tr = 1)", "1", C_RED_BG, C_RED_BD),
    ]

    for i, (orb, poly_m, sz, tr_val, norm_val, bg_c, bd_c) in enumerate(rows):
        ry = hy + 42 + i * 45
        p.append(rect(hx + 10, ry, hw - 20, 38, fill=bg_c, stroke=bd_c, sw=1, rx=5))
        p.append(text(hx + 90, ry + 24, orb, size=11, bold=True))
        p.append(text(hx + 280, ry + 24, poly_m, size=11))
        p.append(text(hx + 470, ry + 24, sz, size=11))
        p.append(text(hx + 580, ry + 24, tr_val, size=11, bold=True, color=C_RED_BD if "1" in tr_val else INK))
        p.append(text(hx + 690, ry + 24, norm_val, size=11, bold=True, color=C_GREEN_BD))

    render(os.path.join(IMG, "frobenius-orbits-trace.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Поліноміальний та нормальний базиси
# ─────────────────────────────────────────────────────────────────────────────
def fig_polynomial_vs_normal_basis():
    W, H = 840, 420
    p = []

    p.append(text(W/2, 28, "Порівняння базисів розширення: Поліноміальний проти Нормального", size=15, bold=True))
    p.append(text(W/2, 48, "Вибір базису визначає обчислювальну складність множення, додавання та піднесення до степеня", size=12, color=MUTED, italic=True))

    # Лівий блок: Поліноміальний базис
    bx1, by1, bw1, bh1 = 40, 75, 365, 320
    p.append(rect(bx1, by1, bw1, bh1, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(bx1, by1, bw1, 32, fill=C_BLUE_BG, stroke=C_BLUE_BD, sw=1.2, rx=8))
    p.append(text(bx1 + bw1/2, by1 + 21, "Поліноміальний (канонічний) базис", size=13, bold=True, color=C_BLUE_BD))

    p.append(text(bx1 + bw1/2, by1 + 60, "B_poly = { 1, α, α^2, ..., α^{n-1} }", size=12, bold=True))
    p.append(text(bx1 + bw1/2, by1 + 80, "Вектор: v = a_0 + a_1 α + ... + a_{n-1} α^{n-1}", size=11, color=MUTED))

    poly_ops = [
        ("Додавання", "Покомпонентне XOR (для p=2)", "O(n) бітових операцій", C_GREEN_BG, C_GREEN_BD),
        ("Множення", "Многочленне множення + редукція mod f(x)", "Шкільне O(n^2) або Карацуба O(n^{1.58})", C_ORANGE_BG, C_ORANGE_BD),
        ("Піднесення до квадрата", "Вставляння нулів між бітами + редукція", "O(n) з лінійною матрицею", C_PURPLE_BG, C_PURPLE_BD),
        ("Перевага", "Проста реалізація в софті (AES xtime, таблиці)", "Універсальний стандарт для криптографії", C_BLUE_BG, C_BLUE_BD)
    ]
    for i, (op_name, op_desc, op_cost, bg_c, bd_c) in enumerate(poly_ops):
        oy = by1 + 105 + i * 50
        p.append(rect(bx1 + 12, oy, bw1 - 24, 44, fill=bg_c, stroke=bd_c, sw=1, rx=5))
        p.append(text(bx1 + 22, oy + 17, op_name + ":", size=11, bold=True, anchor="start", color=bd_c))
        p.append(text(bx1 + 22, oy + 33, op_desc, size=10, anchor="start"))
        p.append(text(bx1 + bw1 - 20, oy + 17, op_cost, size=9, anchor="end", italic=True, color=MUTED))

    # Правий блок: Нормальний базис
    bx2, by2, bw2, bh2 = 435, 75, 365, 320
    p.append(rect(bx2, by2, bw2, bh2, fill=BG, stroke=LINE, sw=1.2, rx=8))
    p.append(rect(bx2, by2, bw2, 32, fill=C_GREEN_BG, stroke=C_GREEN_BD, sw=1.2, rx=8))
    p.append(text(bx2 + bw2/2, by2 + 21, "Нормальний базис (степені Фробеніуса)", size=13, bold=True, color=C_GREEN_BD))

    p.append(text(bx2 + bw2/2, by2 + 60, "B_norm = { β, β^p, β^{p^2}, ..., β^{p^{n-1}} }", size=12, bold=True))
    p.append(text(bx2 + bw2/2, by2 + 80, "Вектор: v = b_0 β + b_1 β^p + ... + b_{n-1} β^{p^{n-1}}", size=11, color=MUTED))

    norm_ops = [
        ("Додавання", "Покомпонентне XOR (для p=2)", "O(n) бітових операцій", C_GREEN_BG, C_GREEN_BD),
        ("Піднесення до p (квадрат)", "Циклічний бітовий зсув регістра!", "O(1) в апаратурі — без логіки!", C_RED_BG, C_RED_BD),
        ("Множення", "Множник Мессі–Омури через матрицю множення", "Апаратна матриця AND-XOR вентилів", C_ORANGE_BG, C_ORANGE_BD),
        ("Перевага", "Ідеально для FPGA/ASIC (алгоритм Іто–Цудзі)", "Швидке піднесення до степеня та інверсія", C_GREEN_BG, C_GREEN_BD)
    ]
    for i, (op_name, op_desc, op_cost, bg_c, bd_c) in enumerate(norm_ops):
        oy = by2 + 105 + i * 50
        p.append(rect(bx2 + 12, oy, bw2 - 24, 44, fill=bg_c, stroke=bd_c, sw=1, rx=5))
        p.append(text(bx2 + 22, oy + 17, op_name + ":", size=11, bold=True, anchor="start", color=bd_c))
        p.append(text(bx2 + 22, oy + 33, op_desc, size=10, anchor="start"))
        p.append(text(bx2 + bw2 - 20, oy + 17, op_cost, size=9, anchor="end", italic=True, color=MUTED))

    render(os.path.join(IMG, "polynomial-vs-normal-basis.svg"), W, H, *p)


if __name__ == "__main__":
    fig_field_extension_construction()
    fig_subfield_lattice()
    fig_frobenius_orbits_trace()
    fig_polynomial_vs_normal_basis()
    print("Фігури згенеровано успішно.")
