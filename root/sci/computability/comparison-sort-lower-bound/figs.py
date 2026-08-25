# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Дерево прийняття рішень для сортування N=3 ───────────────────────
def fig_decision_tree():
    W, H = 840, 460
    frags = []
    
    # Заголовок
    frags.append(text(W/2, 28, "Дерево прийняття рішень для сортування масиву з 3 елементів (N = 3)", size=15, bold=True))
    frags.append(text(W/2, 50, "3! = 6 можливих перестановок ⟹ мінімальна висота дерева h = ⌈log₂ 6⌉ = 3 порівняння", size=12, color=MUTED))

    # Корінь: Порівняння a : b
    node_root, w_r, h_r = textbox(W/2, 95, "a < b ?", size=13, pad=10, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(node_root)

    # Рівень 1
    x_l1_a, y_l1 = W/2 - 200, 185
    x_l1_b = W/2 + 200
    node_l1_a, _, _ = textbox(x_l1_a, y_l1, "b < c ?", size=12, pad=8, fill=FILL, stroke=LINE)
    node_l1_b, _, _ = textbox(x_l1_b, y_l1, "a < c ?", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(node_l1_a)
    frags.append(node_l1_b)

    # Стрілки з кореня
    frags.append(arrow(W/2 - 35, 112, x_l1_a + 35, y_l1 - 18, color=NEG))
    frags.append(text(W/2 - 110, 135, "Так (a < b)", size=11, color=NEG, bold=True))
    
    frags.append(arrow(W/2 + 35, 112, x_l1_b - 35, y_l1 - 18, color=POS))
    frags.append(text(W/2 + 110, 135, "Ні (a ≥ b)", size=11, color=POS, bold=True))

    # Рівень 2 та Листки
    y_l2 = 275
    y_l3 = 365

    # Ліва частина (a < b):
    # Вузол l1_a (b < c ?)
    # Гілка 1: Так (b < c) -> Листок [a, b, c] при x=110, y=365
    x_leaf1 = 110
    box_leaf1, _, _ = textbox(x_leaf1, y_l3, "[a, b, c]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    frags.append(box_leaf1)
    frags.append(arrow(x_l1_a - 25, y_l1 + 16, x_leaf1 + 10, y_l3 - 18, color=FIELD))
    frags.append(text(x_l1_a - 90, 260, "Так (b < c)", size=10, color=FIELD, bold=True))

    # Гілка 2: Ні (b ≥ c) -> Вузол l2_2 (a < c ?) при x=290, y=275
    x_l2_2 = 290
    node_l2_2, _, _ = textbox(x_l2_2, y_l2, "a < c ?", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(node_l2_2)
    frags.append(arrow(x_l1_a + 20, y_l1 + 16, x_l2_2 - 20, y_l2 - 16, color=LINE))
    frags.append(text(x_l1_a + 60, 222, "Ні (b ≥ c)", size=10, color=INK))

    # Листки з вузла l2_2 (a < c ?)
    x_leaf2, x_leaf3 = 230, 350
    box_leaf2, _, _ = textbox(x_leaf2, y_l3, "[a, c, b]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    box_leaf3, _, _ = textbox(x_leaf3, y_l3, "[c, a, b]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    frags.append(box_leaf2)
    frags.append(box_leaf3)
    frags.append(arrow(x_l2_2 - 20, y_l2 + 16, x_leaf2 + 10, y_l3 - 16, color=FIELD))
    frags.append(arrow(x_l2_2 + 20, y_l2 + 16, x_leaf3 - 10, y_l3 - 16, color=FIELD))

    # Права частина (a ≥ b):
    # Вузол l1_b (a < c ?)
    # Гілка 1: Так (a < c) -> Вузол l2_3 (b < c ?) при x=550, y=275
    x_l2_3 = 550
    node_l2_3, _, _ = textbox(x_l2_3, y_l2, "b < c ?", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(node_l2_3)
    frags.append(arrow(x_l1_b - 20, y_l1 + 16, x_l2_3 + 20, y_l2 - 16, color=LINE))
    frags.append(text(x_l1_b - 60, 222, "Так (a < c)", size=10, color=INK))

    # Листки з вузла l2_3 (b < c ?)
    x_leaf4, x_leaf5 = 470, 590
    box_leaf4, _, _ = textbox(x_leaf4, y_l3, "[b, a, c]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    box_leaf5, _, _ = textbox(x_leaf5, y_l3, "[b, c, a]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    frags.append(box_leaf4)
    frags.append(box_leaf5)
    frags.append(arrow(x_l2_3 - 20, y_l2 + 16, x_leaf4 + 10, y_l3 - 16, color=FIELD))
    frags.append(arrow(x_l2_3 + 20, y_l2 + 16, x_leaf5 - 10, y_l3 - 16, color=FIELD))

    # Гілка 2: Ні (a ≥ c) -> Листок [c, b, a] при x=710, y=365
    x_leaf6 = 710
    box_leaf6, _, _ = textbox(x_leaf6, y_l3, "[c, b, a]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    frags.append(box_leaf6)
    frags.append(arrow(x_l1_b + 25, y_l1 + 16, x_leaf6 - 10, y_l3 - 18, color=FIELD))
    frags.append(text(x_l1_b + 90, 260, "Ні (a ≥ c)", size=10, color=FIELD, bold=True))

    # Позначки рівнів (ліворуч, без перетинів з коробками)
    frags.append(text(15, 95, "Рівень 0", size=10, color=MUTED, anchor="start"))
    frags.append(text(15, 185, "Рівень 1", size=10, color=MUTED, anchor="start"))
    frags.append(text(15, 275, "Рівень 2", size=10, color=MUTED, anchor="start"))
    frags.append(text(15, 365, "Рівень 3", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "decision-tree-sort.svg"), W, H, *frags)


# ── Фіг. 2: Зменшення невизначеності (інформаційний приріст) ───────────────
def fig_information_gain():
    W, H = 800, 380
    frags = []

    frags.append(text(W/2, 28, "Звуження простору перестановок при кожному порівнянні", size=15, bold=True))
    frags.append(text(W/2, 48, "Кожне порівняння дає ≤ 1 біт інформації й ділить простір кандидатів щонайбільше навпіл", size=11.5, color=MUTED))

    # 4 етапи: Початок (N!), Крок 1 (N!/2), Крок k, Фінал (1)
    stages = [
        ("Початковий стан", "N! кандидатів", "Невизначеність:\nI = log₂ (N!) біт", "#f4f6f8", LINE, 110),
        ("Після 1-го порівняння", "≤ N! / 2 кандидатів", "Отримано 1 біт:\nI₁ = log₂ (N!) - 1", "#eaf0fd", NEG, 300),
        ("Після k-го порівняння", "≤ N! / 2ᵏ кандидатів", "Отримано k біт:\nIₖ = log₂ (N!) - k", "#fef9e7", "#e08a1e", 490),
        ("Фінальний результат", "1 точна перестановка", "Невизначеність = 0:\nПовністю відсортовано", "#e8f8f5", FIELD, 680)
    ]

    for title_txt, cand_txt, info_txt, fill_c, stroke_c, cx in stages:
        frags.append(rect(cx - 75, 85, 150, 230, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(cx, 115, title_txt, size=12, bold=True, color=INK))
        frags.append(line(cx - 60, 130, cx + 60, 130, color=stroke_c, sw=1.0))
        
        # Візуалізація кількості перестановок
        frags.append(text(cx, 160, cand_txt, size=13, bold=True, color=stroke_c))
        
        # Блок опису інформації
        lines_info = info_txt.split("\n")
        ty = 220
        for li in lines_info:
            frags.append(text(cx, ty, li, size=11, color=INK))
            ty += 18

    # Стрілки між етапами
    frags.append(arrow(190, 200, 220, 200, color=NEG, sw=2.0))
    frags.append(text(205, 185, "-1 біт", size=10, color=NEG, bold=True))

    frags.append(arrow(380, 200, 410, 200, color="#e08a1e", sw=2.0))
    frags.append(text(395, 185, "...", size=12, color="#e08a1e", bold=True))

    frags.append(arrow(570, 200, 600, 200, color=FIELD, sw=2.0))
    frags.append(text(585, 185, "k = ⌈log₂N!⌉", size=10, color=FIELD, bold=True))

    # Підпис знизу
    frags.append(rect(60, 330, 680, 34, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=4))
    frags.append(text(W/2, 351, "Формула інформаційної стелі: мінімальна кількість запитань k ≥ ⌈log₂ (N!)⌉ = Ω(N log N)", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "information-gain-tree.svg"), W, H, *frags)


# ── Фіг. 3: Криві зростання складностей сортування ─────────────────────────
def fig_sorting_complexity_curves():
    W, H = 820, 460
    frags = []

    frags.append(text(W/2, 28, "Порівняння класів складності алгоритмів сортування", size=15, bold=True))
    frags.append(text(W/2, 48, "Як зростає кількість операцій при збільшенні розміру масиву N", size=12, color=MUTED))

    ox, oy = 90.0, 390.0
    pw, ph = 560.0, 300.0
    N_max = 50
    y_max = 2500.0

    def X(n):
        return ox + pw * (n - 1) / (N_max - 1)

    def Y(v):
        return oy - ph * min(v, y_max) / y_max

    # Осі
    frags.append(line(ox, oy, ox + pw + 15, oy, color=INK, sw=1.5))
    frags.append(line(ox, oy, ox, oy - ph - 10, color=INK, sw=1.5))
    frags.append(text(ox + pw / 2, oy + 38, "Розмір масиву (N)  →", size=12, color=INK, bold=True))
    
    frags.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
                 'font-size="12" fill="%s" text-anchor="middle" font-weight="700">%s</text>'
                 % (ox - 55, oy - ph / 2, FONT, INK, esc("Кількість операцій T(N)  →")))

    # Сітка
    for n_val in [10, 20, 30, 40, 50]:
        frags.append(line(X(n_val), oy, X(n_val), oy - ph, color="#e5e7eb", sw=1.0, dash="3 3"))
        frags.append(text(X(n_val), oy + 18, str(n_val), size=11, color=MUTED))

    # Криві:
    # 1. Quadratic O(N²) - red
    pts_sq = []
    for n in range(1, N_max + 1):
        v = n * n
        if v <= y_max:
            pts_sq.append((X(n), Y(v)))
    path_sq = "M " + " L ".join("%.1f,%.1f" % pt for pt in pts_sq)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_sq, POS))
    frags.append(text(X(48) - 10, Y(48*48) - 12, "O(N²) Bubble / Insertion", size=11.5, color=POS, bold=True, anchor="end"))

    # 2. Comparison lower bound O(N log₂ N) - purple
    pts_nlogn = []
    for n in range(1, N_max + 1):
        v = n * math.log2(max(n, 1)) * 4.5
        if v <= y_max:
            pts_nlogn.append((X(n), Y(v)))
    path_nlogn = "M " + " L ".join("%.1f,%.1f" % pt for pt in pts_nlogn)
    frags.append('<path d="%s" fill="none" stroke="#8e44ad" stroke-width="2.5"/>' % (path_nlogn))
    frags.append(text(X(50) + 5, Y(50 * math.log2(50) * 4.5), "Ω(N log N) Межа порівнянь", size=11.5, color="#8e44ad", bold=True, anchor="start"))

    # 3. Non-comparison linear O(N) - green
    pts_lin = []
    for n in range(1, N_max + 1):
        v = n * 12.0
        if v <= y_max:
            pts_lin.append((X(n), Y(v)))
    path_lin = "M " + " L ".join("%.1f,%.1f" % pt for pt in pts_lin)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_lin, FIELD))
    frags.append(text(X(50) + 5, Y(50 * 12.0) + 4, "O(N) Counting / Radix Sort", size=11.5, color=FIELD, bold=True, anchor="start"))

    # Легенда
    frags.append(rect(ox + 20, 75, 270, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(line(ox + 30, 95, ox + 60, 95, color=POS, sw=2.5))
    frags.append(text(ox + 70, 99, "O(N²) — квадратичне сортування", size=11, anchor="start"))
    
    frags.append(line(ox + 30, 117, ox + 60, 117, color="#8e44ad", sw=2.5))
    frags.append(text(ox + 70, 121, "Ω(N log N) — межа порівнянь", size=11, anchor="start"))

    frags.append(line(ox + 30, 139, ox + 60, 139, color=FIELD, sw=2.5))
    frags.append(text(ox + 70, 143, "O(N) — порозрядний обхід межі", size=11, anchor="start"))

    render(os.path.join(OUT, "sorting-complexity-curves.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_decision_tree()
    fig_information_gain()
    fig_sorting_complexity_curves()
    print("SVG generation complete.")
