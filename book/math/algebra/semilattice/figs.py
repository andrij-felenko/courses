# -*- coding: utf-8 -*-
"""Фігури для статті «Напіврешітка».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL  = "#eafaf1"
RED_FILL    = "#fdecea"
BLUE_FILL   = "#eaf0fd"
GRAY_FILL   = "#f4f6f8"
YELLOW_FILL = "#fef9e7"
PURPLE_FILL = "#f4ecf7"

ORANGE      = "#e67e22"
ORANGE_FILL = "#fdf1e5"
PURPLE      = "#8e44ad"
BLUE        = "#2457d6"
GREEN       = "#27ae60"
RED         = "#c0392b"
INK_DARK    = "#1a1a1a"


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — Алгебраїчний та порядковий погляди на напіврешітку
# ─────────────────────────────────────────────────────────────────────────────
def fig_algebra_order_duality():
    W, H = 860, 430
    p = []

    # Title
    p.append(fitbox(20, 16, 820, 38, "Два погляди на напіврешітку: алгебраїчний та порядковий ізоморфізм", size=15, bold=True, fill="#f8fafc", stroke=BLUE))

    # Left Column: Algebraic Semilattice
    col_w = 370
    p.append(rect(30, 75, col_w, 325, fill=BLUE_FILL, stroke=BLUE, sw=1.8, rx=8))
    p.append(fitbox(45, 90, 340, 36, "Алгебраїчна напіврешітка (S, ⋆)", size=14, bold=True, fill="#ffffff", stroke=BLUE))

    alg_axioms = [
        "1. Асоціативність:",
        "   (a ⋆ b) ⋆ c = a ⋆ (b ⋆ c)",
        "2. Комутативність:",
        "   a ⋆ b = b ⋆ a",
        "3. Ідемпотентність:",
        "   a ⋆ a = a"
    ]
    p.append(fitbox(45, 138, 340, 140, "\n".join(alg_axioms), size=12.5, bold=False, fill="#ffffff", stroke="#cbd5e1"))

    alg_meaning = [
        "Операція ⋆ є бінарним згортком.",
        "Порядок обчислень та повтори",
        "аргументів не змінюють результат."
    ]
    p.append(fitbox(45, 290, 340, 95, "\n".join(alg_meaning), size=12, fill="#ffffff", stroke=BLUE, color=INK_DARK))

    # Right Column: Order-theoretic Semilattice (Poset)
    rx = 460
    p.append(rect(rx, 75, col_w, 325, fill=GREEN_FILL, stroke=GREEN, sw=1.8, rx=8))
    p.append(fitbox(rx + 15, 90, 340, 36, "Порядкова напіврешітка (S, ≤)", size=14, bold=True, fill="#ffffff", stroke=GREEN))

    poset_props = [
        "1. Частковий порядок ≤:",
        "   рефлексивний, антисиметричний, транзитивний",
        "2. Точні грані для будь-якої пари {a, b}:",
        "   • Нижня (Meet, ⊓): інфімум inf{a, b}",
        "   • Верхня (Join, ⊔): супремум sup{a, b}"
    ]
    p.append(fitbox(rx + 15, 138, 340, 140, "\n".join(poset_props), size=12.5, bold=False, fill="#ffffff", stroke="#cbd5e1"))

    poset_meaning = [
        "Елементи утворюють ієрархію.",
        "Будь-які два елементи мають єдину",
        "найближчу спільну грань у посеті."
    ]
    p.append(fitbox(rx + 15, 290, 340, 95, "\n".join(poset_meaning), size=12, fill="#ffffff", stroke=GREEN, color=INK_DARK))

    # Central Bi-directional conversion arrows and bridge
    p.append(rect(375, 185, 110, 100, fill=YELLOW_FILL, stroke=ORANGE, sw=1.5, rx=6))
    p.append(arrow(365, 210, 465, 210, color=ORANGE, sw=2.2))
    p.append(arrow(465, 255, 365, 255, color=ORANGE, sw=2.2))
    p.append(text(430, 202, "a ≤ b ⇔ a ⋆ b = a", size=10.5, bold=True, color=ORANGE))
    p.append(text(430, 247, "a ⋆ b = inf{a, b}", size=10.5, bold=True, color=ORANGE))
    p.append(text(430, 276, "ІЗОМОРФІЗМ", size=10, bold=True, color=LINE))

    render(os.path.join(IMG, "semilattice-algebra-order-duality.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — Діаграми Хассе: порівняння порядкових структур
# ─────────────────────────────────────────────────────────────────────────────
def fig_hasse_diagrams_comparison():
    W, H = 900, 440
    p = []

    p.append(fitbox(20, 14, 860, 36, "Діаграми Хассе: напіврешітки, повні решітки та непорівнянні посети", size=15, bold=True, fill="#f8fafc", stroke=LINE))

    card_w = 195
    card_h = 360
    y_card = 60
    xs = [25, 245, 465, 685]

    # Sub-figure 1: Join-Semilattice (No bottom or disjoint branches with unique join)
    p.append(rect(xs[0], y_card, card_w, card_h, fill=GRAY_FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(fitbox(xs[0] + 10, y_card + 10, card_w - 20, 32, "Join-напіврешітка (⊔)", size=12, bold=True, fill="#ffffff", stroke=BLUE))
    # Nodes: Top=x⊔y⊔z, Mid=x⊔y, y⊔z, Bot=x, y, z
    # Lines
    p.append(line(xs[0] + 50, y_card + 280, xs[0] + 65, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[0] + 100, y_card + 280, xs[0] + 65, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[0] + 100, y_card + 280, xs[0] + 135, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[0] + 145, y_card + 280, xs[0] + 135, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[0] + 65, y_card + 180, xs[0] + 100, y_card + 90, color=LINE, sw=1.5))
    p.append(line(xs[0] + 135, y_card + 180, xs[0] + 100, y_card + 90, color=LINE, sw=1.5))
    # Node circles
    p.append(circle(xs[0] + 100, y_card + 90, 16, fill=GREEN_FILL, stroke=GREEN, sw=2))
    p.append(text(xs[0] + 100, y_card + 95, "⊤", size=13, bold=True, color=GREEN))
    p.append(circle(xs[0] + 65, y_card + 180, 14, fill="#ffffff", stroke=BLUE, sw=1.5))
    p.append(text(xs[0] + 65, y_card + 184, "a⊔b", size=10, bold=True, color=BLUE))
    p.append(circle(xs[0] + 135, y_card + 180, 14, fill="#ffffff", stroke=BLUE, sw=1.5))
    p.append(text(xs[0] + 135, y_card + 184, "b⊔c", size=10, bold=True, color=BLUE))
    p.append(circle(xs[0] + 50, y_card + 280, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[0] + 50, y_card + 284, "a", size=11, bold=True))
    p.append(circle(xs[0] + 100, y_card + 280, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[0] + 100, y_card + 284, "b", size=11, bold=True))
    p.append(circle(xs[0] + 145, y_card + 280, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[0] + 145, y_card + 284, "c", size=11, bold=True))
    p.append(fitbox(xs[0] + 10, y_card + 305, card_w - 20, 45, "Кожна пара має sup.\nНемає спільного inf для {a, c}.", size=10.5, fill="#ffffff", stroke=LINE))

    # Sub-figure 2: Meet-Semilattice (Tree structure with bottom root)
    p.append(rect(xs[1], y_card, card_w, card_h, fill=GRAY_FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(fitbox(xs[1] + 10, y_card + 10, card_w - 20, 32, "Meet-напіврешітка (⊓)", size=12, bold=True, fill="#ffffff", stroke=BLUE))
    # Inverted Tree: Root ⊥ at bottom, branching upwards
    p.append(line(xs[1] + 100, y_card + 280, xs[1] + 65, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[1] + 100, y_card + 280, xs[1] + 135, y_card + 180, color=LINE, sw=1.5))
    p.append(line(xs[1] + 65, y_card + 180, xs[1] + 45, y_card + 90, color=LINE, sw=1.5))
    p.append(line(xs[1] + 65, y_card + 180, xs[1] + 85, y_card + 90, color=LINE, sw=1.5))
    p.append(line(xs[1] + 135, y_card + 180, xs[1] + 120, y_card + 90, color=LINE, sw=1.5))
    p.append(line(xs[1] + 135, y_card + 180, xs[1] + 155, y_card + 90, color=LINE, sw=1.5))
    # Nodes
    p.append(circle(xs[1] + 100, y_card + 280, 16, fill=RED_FILL, stroke=RED, sw=2))
    p.append(text(xs[1] + 100, y_card + 285, "⊥", size=13, bold=True, color=RED))
    p.append(circle(xs[1] + 65, y_card + 180, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 65, y_card + 184, "u", size=11, bold=True))
    p.append(circle(xs[1] + 135, y_card + 180, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 135, y_card + 184, "v", size=11, bold=True))
    p.append(circle(xs[1] + 45, y_card + 90, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 45, y_card + 94, "x₁", size=10, bold=True))
    p.append(circle(xs[1] + 85, y_card + 90, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 85, y_card + 94, "x₂", size=10, bold=True))
    p.append(circle(xs[1] + 120, y_card + 90, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 120, y_card + 94, "y₁", size=10, bold=True))
    p.append(circle(xs[1] + 155, y_card + 90, 12, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[1] + 155, y_card + 94, "y₂", size=10, bold=True))
    p.append(fitbox(xs[1] + 10, y_card + 305, card_w - 20, 45, "Кожна пара має inf (LCA).\nГілки не мають спільного sup.", size=10.5, fill="#ffffff", stroke=LINE))

    # Sub-figure 3: Full Lattice (Boolean Algebra / Divisors D12)
    p.append(rect(xs[2], y_card, card_w, card_h, fill=GREEN_FILL, stroke=GREEN, sw=1.2, rx=6))
    p.append(fitbox(xs[2] + 10, y_card + 10, card_w - 20, 32, "Повна решітка (Lattice)", size=12, bold=True, fill="#ffffff", stroke=GREEN))
    # Diamond: ⊤ at top, a and b in middle, ⊥ at bottom
    p.append(line(xs[2] + 100, y_card + 280, xs[2] + 55, y_card + 185, color=LINE, sw=1.5))
    p.append(line(xs[2] + 100, y_card + 280, xs[2] + 145, y_card + 185, color=LINE, sw=1.5))
    p.append(line(xs[2] + 55, y_card + 185, xs[2] + 100, y_card + 90, color=LINE, sw=1.5))
    p.append(line(xs[2] + 145, y_card + 185, xs[2] + 100, y_card + 90, color=LINE, sw=1.5))
    p.append(circle(xs[2] + 100, y_card + 90, 16, fill="#ffffff", stroke=GREEN, sw=2))
    p.append(text(xs[2] + 100, y_card + 95, "⊤", size=13, bold=True, color=GREEN))
    p.append(circle(xs[2] + 55, y_card + 185, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[2] + 55, y_card + 189, "a", size=11, bold=True))
    p.append(circle(xs[2] + 145, y_card + 185, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[2] + 145, y_card + 189, "b", size=11, bold=True))
    p.append(circle(xs[2] + 100, y_card + 280, 16, fill="#ffffff", stroke=RED, sw=2))
    p.append(text(xs[2] + 100, y_card + 285, "⊥", size=13, bold=True, color=RED))
    p.append(fitbox(xs[2] + 10, y_card + 305, card_w - 20, 45, "Одночасно є і Join-, і Meet-напіврешіткою: є і ⊔, і ⊓.", size=10.5, fill="#ffffff", stroke=GREEN))

    # Sub-figure 4: Non-semilattice Poset (Crown / Dual Minimal Upper Bounds)
    p.append(rect(xs[3], y_card, card_w, card_h, fill=RED_FILL, stroke=RED, sw=1.2, rx=6))
    p.append(fitbox(xs[3] + 10, y_card + 10, card_w - 20, 32, "Посет БЕЗ напіврешітки", size=12, bold=True, fill="#ffffff", stroke=RED))
    # Two bottoms, two tops (Crown structure)
    p.append(line(xs[3] + 55, y_card + 260, xs[3] + 55, y_card + 110, color=RED, sw=1.5))
    p.append(line(xs[3] + 55, y_card + 260, xs[3] + 145, y_card + 110, color=RED, sw=1.5))
    p.append(line(xs[3] + 145, y_card + 260, xs[3] + 55, y_card + 110, color=RED, sw=1.5))
    p.append(line(xs[3] + 145, y_card + 260, xs[3] + 145, y_card + 110, color=RED, sw=1.5))
    p.append(circle(xs[3] + 55, y_card + 110, 14, fill="#ffffff", stroke=RED, sw=1.8))
    p.append(text(xs[3] + 55, y_card + 114, "m₁", size=11, bold=True, color=RED))
    p.append(circle(xs[3] + 145, y_card + 110, 14, fill="#ffffff", stroke=RED, sw=1.8))
    p.append(text(xs[3] + 145, y_card + 114, "m₂", size=11, bold=True, color=RED))
    p.append(circle(xs[3] + 55, y_card + 260, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[3] + 55, y_card + 264, "x", size=11, bold=True))
    p.append(circle(xs[3] + 145, y_card + 260, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(xs[3] + 145, y_card + 264, "y", size=11, bold=True))
    p.append(fitbox(xs[3] + 10, y_card + 305, card_w - 20, 45, "Дві мінімальні верхні межі m₁, m₂: немає ЄДИНОГО sup{x, y}!", size=10.2, fill="#ffffff", stroke=RED, color=RED))

    render(os.path.join(IMG, "hasse-diagrams-semilattices.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — Монотонне злиття станів CRDT над Join-напіврешіткою
# ─────────────────────────────────────────────────────────────────────────────
def fig_crdt_join_semilattice_merge():
    W, H = 880, 460
    p = []

    p.append(fitbox(20, 14, 840, 36, "Join-напіврешітка як основа сильної кінцевої узгодженості (CRDT / SEC)", size=15, bold=True, fill="#f8fafc", stroke=BLUE))

    # Left Panel: Lattice diagram of replica states
    p.append(rect(25, 60, 430, 385, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    p.append(fitbox(35, 70, 410, 28, "Простір станів G-Counter: s = ⟨A, B⟩", size=12.5, bold=True, fill=GRAY_FILL, stroke=LINE))

    # Bottom element
    p.append(fitbox(155, 365, 170, 52, "Початковий стан ⊥\ns₀ = ⟨A: 0, B: 0⟩", size=11.5, fill="#ffffff", stroke=LINE))

    # Replica A branch and Replica B branch
    p.append(fitbox(45, 230, 160, 55, "Репліка A (стан s₁)\ns₁ = ⟨A: 3, B: 1⟩", size=11.5, bold=True, fill=GREEN_FILL, stroke=GREEN))
    p.append(fitbox(255, 230, 160, 55, "Репліка B (стан s₂)\ns₂ = ⟨A: 1, B: 4⟩", size=11.5, bold=True, fill=BLUE_FILL, stroke=BLUE))

    # Top element (Join)
    p.append(fitbox(100, 115, 280, 68, "Точна верхня межа (LUB, Join ⊔)\ns₁ ⊔ s₂ = ⟨max(3,1), max(1,4)⟩\n= ⟨A: 3, B: 4⟩", size=12, bold=True, fill=YELLOW_FILL, stroke=ORANGE))

    # Arrows between states
    p.append(arrow(210, 365, 145, 290, color=GREEN, sw=2))
    p.append(arrow(270, 365, 315, 290, color=BLUE, sw=2))
    p.append(arrow(145, 230, 195, 185, color=LINE, sw=2))
    p.append(arrow(315, 230, 275, 185, color=LINE, sw=2))

    p.append(text(150, 335, "s₀ ≤ s₁", size=11, bold=True, color=GREEN))
    p.append(text(320, 335, "s₀ ≤ s₂", size=11, bold=True, color=BLUE))
    p.append(text(140, 205, "s₁ ≤ s₁⊔s₂", size=11, bold=True, color=LINE))
    p.append(text(325, 205, "s₂ ≤ s₁⊔s₂", size=11, bold=True, color=LINE))

    # Right Panel: Why the 3 Algebraic Laws Guarantee SEC
    p.append(rect(470, 60, 385, 385, fill="#f8fafc", stroke=BLUE, sw=1.5, rx=8))
    p.append(fitbox(485, 72, 355, 30, "Алгебраїчні гарантії напіврешітки", size=13.5, bold=True, fill=BLUE_FILL, stroke=BLUE))

    laws = [
        ("1. Комутативність: a ⊔ b = b ⊔ a", "Пакетна стійкість до перестановки.", "Не має значення, яка репліка прийшла першою."),
        ("2. Асоціативність: (a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)", "Стійкість до довільного групування.", "Батчі та проміжні ретрансляції безпечні."),
        ("3. Ідемпотентність: a ⊔ a = a", "Стійкість до дублювання повідомлень.", "Повторні мережеві retry не спотворюють стан."),
        ("4. Монотонність: s ≤ s ⊔ Δs", "Теорема CALM (Монтана / Геллерштейн).", "Стан реплік рухається лише вгору порядком ≤.")
    ]

    y_pos = 112
    for title, desc1, desc2 in laws:
        p.append(rect(485, y_pos, 355, 68, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(500, y_pos + 18, title, size=11.5, bold=True, color=BLUE, anchor="start"))
        p.append(text(500, y_pos + 36, desc1, size=11, color=INK_DARK, anchor="start"))
        p.append(text(500, y_pos + 54, desc2, size=10.5, color=MUTED, anchor="start", italic=True))
        y_pos += 76

    render(os.path.join(IMG, "crdt-join-semilattice-merge.svg"), W, H, *p)


if __name__ == "__main__":
    fig_algebra_order_duality()
    fig_hasse_diagrams_comparison()
    fig_crdt_join_semilattice_merge()
    print("All figures generated successfully.")
