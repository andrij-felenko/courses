# -*- coding: utf-8 -*-
"""Фігури для статті «Моноїд».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
GRAY_FILL  = "#f4f6f8"
YELLOW_FILL = "#fef9e7"
PURPLE_FILL = "#f4ecf7"

ORANGE      = "#e67e22"
ORANGE_FILL = "#fdf1e5"
PURPLE      = "#8e44ad"


# ─────────────────────────────────────────────────────────────────────────
# Фігура 1 — Ієрархія алгебраїчних структур
# ─────────────────────────────────────────────────────────────────────────
def fig_algebraic_hierarchy():
    W, H = 880, 520
    p = []
    p.append(text(W/2, 28, "Ієрархія алгебраїчних структур: від магми до абелевої групи", size=17, bold=True))

    bw, bh = 150, 160
    xs = [30, 200, 370, 540, 710]
    y_box = 70

    structs = [
        ("МАГМА", "Замкненість\n\n∀ a, b ∈ M\na · b ∈ M", "(ℤ, −)\n(ℝ, ÷)\nвіднімання", GRAY_FILL, LINE),
        ("ПІВГРУПА", "+ Асоціативність\n\n(a · b) · c =\na · (b · c)", "(ℤ>0, +)\nнепорожні\nрядки Σ⁺", BLUE_FILL, NEG),
        ("МОНОЇД", "+ Нейтральний e\n\ne · a = a · e = a\nєдиний нуль/одиниця", "(ℕ, +, 0)\n(Σ*, ·, ε)\n(Mₙ, ·, I)", GREEN_FILL, FIELD),
        ("ГРУПА", "+ Обернений a⁻¹\n\n∀ a ∃ a⁻¹:\na · a⁻¹ = e", "(ℤ, +, 0)\n(ℚ\\{0}, ·, 1)\nперестановки Sₙ", YELLOW_FILL, ORANGE),
        ("АБЕЛЕВА ГРУПА", "+ Комутативність\n\na · b = b · a\nдля всіх пар", "(ℤ, +, 0)\n(ℝ, +, 0)\nвектори (V, +)", PURPLE_FILL, PURPLE)
    ]

    for i, (name, laws, ex, bg_col, stroke_col) in enumerate(structs):
        x = xs[i]
        # Header box
        p.append(rect(x, y_box, bw, bh, fill=bg_col, stroke=stroke_col, sw=2, rx=6))
        p.append(text(x + bw/2, y_box + 22, name, size=13, bold=True, color=stroke_col))
        p.append(line(x, y_box + 34, x + bw, y_box + 34, color=stroke_col, sw=1.2))

        # Laws text
        law_lines = laws.split("\n")
        p.append(mtext(x + bw/2, y_box + 52, law_lines, size=11.5, color=INK, lh=1.25))

        # Arrow to next
        if i < 4:
            p.append(arrow(x + bw + 2, y_box + bh/2, xs[i+1] - 4, y_box + bh/2, color=LINE, sw=1.8))

        # Examples box below
        y_ex = y_box + bh + 25
        p.append(rect(x, y_ex, bw, 95, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        p.append(text(x + bw/2, y_ex + 18, "Приклади:", size=11, bold=True, color=MUTED))
        ex_lines = ex.split("\n")
        p.append(mtext(x + bw/2, y_ex + 36, ex_lines, size=11, color=INK, lh=1.25))

    # Bottom summary explanation bar
    y_sum = y_box + bh + 145
    p.append(rect(30, y_sum, 830, 85, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(W/2, y_sum + 24, "МОНОЇД — природний фундамент агрегації даних та обчислень", size=13.5, bold=True, color=FIELD))
    p.append(text(W/2, y_sum + 46, "Асоціативність дозволяє довільне розставляння дужок і паралельне обчислення частин.", size=12, color=INK))
    p.append(text(W/2, y_sum + 68, "Нейтральний елемент e задає початковий стан акумулятора й обробку порожніх наборів.", size=12, color=INK))

    render(os.path.join(IMG, "algebraic-hierarchy.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — Асоціативність і паралельне дерево редукції
# ─────────────────────────────────────────────────────────────────────────
def fig_monoid_reduction_tree():
    W, H = 880, 520
    p = []
    p.append(text(W/2, 26, "Асоціативність у дії: послідовне згортання проти паралельного дерева", size=16, bold=True))

    # Left panel: Sequential fold
    lx, ly, lw, lh = 30, 56, 380, 370
    p.append(rect(lx, ly, lw, lh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(lx + lw/2, ly + 24, "Послідовне згортання (Fold Left)", size=14, bold=True))
    p.append(text(lx + lw/2, ly + 44, "Час: O(N) кроків — послідовний ланцюг залежностей", size=11.5, color=MUTED))

    # Step-by-step fold
    cy_start = ly + 76
    p.append(textbox(lx + 60, cy_start, "e", size=12, fill=GREEN_FILL, stroke=FIELD)[0])
    p.append(arrow(lx + 80, cy_start, lx + 120, cy_start))
    p.append(textbox(lx + 145, cy_start, "a₁", size=12, fill=BLUE_FILL, stroke=NEG)[0])
    p.append(arrow(lx + 165, cy_start, lx + 205, cy_start + 25))

    # Acc 1
    p.append(textbox(lx + 260, cy_start + 30, "res₁ = e · a₁", size=11.5, fill=FILL, stroke=LINE)[0])
    p.append(textbox(lx + 60, cy_start + 75, "a₂", size=12, fill=BLUE_FILL, stroke=NEG)[0])
    p.append(arrow(lx + 80, cy_start + 75, lx + 195, cy_start + 95))
    p.append(arrow(lx + 260, cy_start + 50, lx + 260, cy_start + 85))

    # Acc 2
    p.append(textbox(lx + 260, cy_start + 105, "res₂ = res₁ · a₂", size=11.5, fill=FILL, stroke=LINE)[0])
    p.append(textbox(lx + 60, cy_start + 150, "a₃", size=12, fill=BLUE_FILL, stroke=NEG)[0])
    p.append(arrow(lx + 80, cy_start + 150, lx + 195, cy_start + 170))
    p.append(arrow(lx + 260, cy_start + 125, lx + 260, cy_start + 160))

    # Acc 3
    p.append(textbox(lx + 260, cy_start + 180, "res₃ = res₂ · a₃", size=11.5, fill=FILL, stroke=LINE)[0])
    p.append(textbox(lx + 60, cy_start + 225, "a₄", size=12, fill=BLUE_FILL, stroke=NEG)[0])
    p.append(arrow(lx + 80, cy_start + 225, lx + 195, cy_start + 245))
    p.append(arrow(lx + 260, cy_start + 200, lx + 260, cy_start + 235))

    # Final
    p.append(textbox(lx + 230, cy_start + 260, "Підсумок: (((a₁·a₂)·a₃)·a₄)", size=11.5, bold=True, fill=GREEN_FILL, stroke=FIELD)[0])

    # Right panel: Parallel tree reduction
    rx, ry, rw, rh = 440, 56, 410, 370
    p.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw/2, ry + 24, "Паралельна редукція (Tree Reduce)", size=14, bold=True))
    p.append(text(rx + rw/2, ry + 44, "Час: O(log₂ N) кроків — паралельні гілки обчислень", size=11.5, color=FIELD, bold=True))

    # Level 0: 4 elements
    xs_tree = [rx + 50, rx + 145, rx + 255, rx + 350]
    y_l0 = ry + 85
    for i, name in enumerate(["a₁", "a₂", "a₃", "a₄"]):
        p.append(textbox(xs_tree[i], y_l0, name, size=12, fill=BLUE_FILL, stroke=NEG)[0])

    # Level 1: pairwise combinations
    y_l1 = ry + 175
    x_p1 = (xs_tree[0] + xs_tree[1]) / 2
    x_p2 = (xs_tree[2] + xs_tree[3]) / 2

    p.append(arrow(xs_tree[0], y_l0 + 15, x_p1 - 15, y_l1 - 15))
    p.append(arrow(xs_tree[1], y_l0 + 15, x_p1 + 15, y_l1 - 15))
    p.append(textbox(x_p1, y_l1, "b₁ = a₁ · a₂", size=12, fill=YELLOW_FILL, stroke=ORANGE)[0])

    p.append(arrow(xs_tree[2], y_l0 + 15, x_p2 - 15, y_l1 - 15))
    p.append(arrow(xs_tree[3], y_l0 + 15, x_p2 + 15, y_l1 - 15))
    p.append(textbox(x_p2, y_l1, "b₂ = a₃ · a₄", size=12, fill=YELLOW_FILL, stroke=ORANGE)[0])

    # Level 2: root combination
    y_l2 = ry + 275
    x_root = (x_p1 + x_p2) / 2
    p.append(arrow(x_p1, y_l1 + 18, x_root - 30, y_l2 - 18))
    p.append(arrow(x_p2, y_l1 + 18, x_root + 30, y_l2 - 18))
    p.append(textbox(x_root, y_l2, "Підсумок: (a₁·a₂) · (a₃·a₄)", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD)[0])

    # Bottom identity note
    y_bot = ly + lh + 20
    p.append(rect(30, y_bot, 820, 50, fill=YELLOW_FILL, stroke=ORANGE, sw=1.5, rx=6))
    p.append(text(W/2, y_bot + 20, "Асоціативність гарантує: (((a₁·a₂)·a₃)·a₄) = (a₁·a₂)·(a₃·a₄) = a₁·(a₂·(a₃·a₄))", size=12.5, bold=True))
    p.append(text(W/2, y_bot + 38, "Будь-який порядок розбиття на паралельні задачі дає строго ідентичний результат.", size=11.5, color=MUTED))

    render(os.path.join(IMG, "monoid-reduction-tree.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — Універсальна властивість вільного моноїда
# ─────────────────────────────────────────────────────────────────────────
def fig_free_monoid_universal():
    W, H = 840, 430
    p = []
    p.append(text(W/2, 26, "Універсальна властивість вільного моноїда слів Σ*", size=16, bold=True))

    # Diagram coordinates
    ax, ay = 180, 100   # Set Sigma
    bx, by = 640, 100   # Free monoid Sigma*
    cx, cy = 410, 260   # Any monoid M

    # Nodes
    p.append(textbox(ax, ay, "Алфавіт Σ\n(довільна множина символів)", size=13, fill=BLUE_FILL, stroke=NEG, bold=True)[0])
    p.append(textbox(bx, by, "Вільний моноїд (Σ*, ·, ε)\n(слова над алфавітом Σ)", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True)[0])
    p.append(textbox(cx, cy, "Довільний моноїд (M, ⋆, e_M)\n(цільова алгебраїчна структура)", size=13, fill=YELLOW_FILL, stroke=ORANGE, bold=True)[0])

    # Arrows
    # i: Sigma -> Sigma*
    p.append(arrow(ax + 110, ay, bx - 120, ay, color=LINE, sw=2))
    p.append(text((ax + bx)/2, ay - 14, "i : a ↦ (a)   [канонічне вкладення]", size=12, bold=True))

    # f: Sigma -> M
    p.append(arrow(ax + 40, ay + 25, cx - 80, cy - 25, color=LINE, sw=1.8))
    p.append(text(ax + 70, (ay + cy)/2 - 5, "f : Σ → M", size=12.5, bold=True, color=INK))
    p.append(text(ax + 55, (ay + cy)/2 + 15, "(відображення символів)", size=11, color=MUTED))

    # f_bar: Sigma* -> M (dashed)
    p.append(arrow(bx - 40, by + 25, cx + 80, cy - 25, color=FIELD, sw=2.2))
    p.append(text(bx - 60, (by + cy)/2 - 8, "∃! f̄ : Σ* → M", size=13, bold=True, color=FIELD))
    p.append(text(bx - 45, (by + cy)/2 + 12, "(єдиний гомоморфізм моноїдів)", size=11, color=FIELD))

    # Commutative triangle formula
    p.append(text(cx, cy + 45, "f̄ ∘ i = f   (трикутник комутативний)", size=13, bold=True))
    p.append(text(cx, cy + 65, "f̄(a₁ a₂ … aₖ) = f(a₁) ⋆ f(a₂) ⋆ … ⋆ f(aₖ)    та    f̄(ε) = e_M", size=12, color=INK))

    # Example box
    y_ex = cy + 90
    p.append(rect(60, y_ex, 720, 50, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(W/2, y_ex + 18, "Приклад: Σ = {0, 1},  M = (ℤ, +, 0),  f(0)=0, f(1)=1", size=12, bold=True))
    p.append(text(W/2, y_ex + 36, "Гомоморфізм f̄ рахує кількість одиниць:  f̄(\"1011\") = 1 + 0 + 1 + 1 = 3,  f̄(ε) = 0", size=11.5, color=MUTED))

    render(os.path.join(IMG, "free-monoid-universal.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 4 — Моноїд у теорії категорій
# ─────────────────────────────────────────────────────────────────────────
def fig_monoid_category_single_object():
    W, H = 860, 440
    p = []
    p.append(text(W/2, 26, "Моноїди в теорії категорій: один об'єкт і моноїдальні об'єкти", size=16, bold=True))

    # Left panel: Monoid as single-object category
    lx, ly, lw, lh = 30, 56, 390, 350
    p.append(rect(lx, ly, lw, lh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(lx + lw/2, ly + 24, "Категорія з одним об'єктом", size=14, bold=True))
    p.append(text(lx + lw/2, ly + 44, "Елементи моноїда — це ендоморфізми", size=11.5, color=MUTED))

    # Center object dot
    cx, cy = lx + lw/2, ly + 180
    p.append(circle(cx, cy, 14, fill=FIELD, stroke=INK, sw=2))
    p.append(text(cx, cy + 5, "•", size=18, bold=True, color="#ffffff"))
    p.append(text(cx, cy - 24, "Єдиний об'єкт X", size=12, bold=True))

    # Loop morphisms
    # Top loop (f)
    p.append(textbox(cx - 90, cy - 60, "f ∈ M", size=11.5, fill=BLUE_FILL, stroke=NEG)[0])
    p.append(arrow(cx - 10, cy - 12, cx - 60, cy - 45, color=NEG, sw=1.5))
    p.append(arrow(cx - 60, cy - 45, cx - 12, cy - 5, color=NEG, sw=1.5))

    # Right loop (g)
    p.append(textbox(cx + 90, cy - 60, "g ∈ M", size=11.5, fill=YELLOW_FILL, stroke=ORANGE)[0])
    p.append(arrow(cx + 10, cy - 12, cx + 60, cy - 45, color=ORANGE, sw=1.5))
    p.append(arrow(cx + 60, cy - 45, cx + 12, cy - 5, color=ORANGE, sw=1.5))

    # Bottom loop (id = e)
    p.append(textbox(cx, cy + 70, "id_• = e (нейтральний)", size=11.5, fill=GREEN_FILL, stroke=FIELD)[0])
    p.append(arrow(cx - 10, cy + 12, cx - 35, cy + 50, color=FIELD, sw=1.5))
    p.append(arrow(cx + 35, cy + 50, cx + 10, cy + 12, color=FIELD, sw=1.5))

    # Properties list below
    p.append(text(lx + lw/2, ly + lh - 50, "Морфізми: Hom(•, •) = M", size=12, bold=True))
    p.append(text(lx + lw/2, ly + lh - 30, "Композиція: g ∘ f = g · f   (асоціативна)", size=12))
    p.append(text(lx + lw/2, ly + lh - 12, "Тотожний: id_• ∘ f = f ∘ id_• = f", size=12))

    # Right panel: Monoid object in Monoidal Category
    rx, ry, rw, rh = 440, 56, 390, 350
    p.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw/2, ry + 24, "Моноїдний об'єкт у категорії (𝒞, ⊗, I)", size=13.5, bold=True))
    p.append(text(rx + rw/2, ry + 44, "Узагальнення на тензорний добуток", size=11.5, color=MUTED))

    # Boxes for M x M -> M
    rcx = rx + rw/2
    p.append(textbox(rcx, ry + 85, "Множення:   μ : M ⊗ M → M", size=12, fill=BLUE_FILL, stroke=NEG, bold=True)[0])
    p.append(textbox(rcx, ry + 135, "Одиниця:   η : I → M", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True)[0])

    # Monad in Endofunctors note
    p.append(rect(rx + 20, ry + 180, rw - 40, 140, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5, rx=6))
    p.append(text(rcx, ry + 204, "Монада як моноїдний об'єкт", size=13, bold=True, color=PURPLE))
    p.append(text(rcx, ry + 228, "Категорія: ендофунктори [𝒞, 𝒞]", size=11.5, bold=True))
    p.append(text(rcx, ry + 248, "Тензорний добуток: композиція функторів ∘", size=11.5))
    p.append(text(rcx, ry + 268, "Одиниця: тотожний функтор Id", size=11.5))
    p.append(text(rcx, ry + 292, "Монада — моноїд (T, μ : T ∘ T → T, η : Id → T)", size=12, bold=True, color=PURPLE))

    render(os.path.join(IMG, "monoid-category-single-object.svg"), W, H, *p)


if __name__ == "__main__":
    fig_algebraic_hierarchy()
    fig_monoid_reduction_tree()
    fig_free_monoid_universal()
    fig_monoid_category_single_object()
    print("Всі фігури згенеровано успішно.")
