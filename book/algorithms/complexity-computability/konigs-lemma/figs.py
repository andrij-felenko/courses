# -*- coding: utf-8 -*-
"""Фігури для теми «Лема Кеніґа» (book/algorithms/complexity-computability/konigs-lemma)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів (відповідно до єдиного стилю)
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"  # Виділений нескінченний шлях
BLUE_F, BLUE_S   = "#eaf0fd", "#2563eb"  # BFS / Вузли
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce" # Залишок піддерев / Кліні
RED_F, RED_S     = "#fef2f2", "#dc2626"  # Пастка DFS / глухий кут
GRAY_F, GRAY_S   = "#f8fafc", "#64748b"  # Скінченне піддерево
AMBER_F, AMBER_S = "#fff6e5", "#d97706"  # Попередження / межа

def fig_konig_tree_branch():
    """fig1-konig-tree-branch.svg: Побудова нескінченного шляху в локально скінченному дереві за лемою Кеніґа."""
    W, H = 840, 500
    frags = []

    # Фон та заголовок
    frags.append(rect(10, 10, 820, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Принцип Кеніґа: вибір нащадка з нескінченним піддеревом (|Tᵥ| = ∞)", size=15, bold=True, color="#1e293b"))

    # Рівень 0: Корень r = v₀
    frags.append(circle(420, 80, 22, fill=GREEN_F, stroke=GREEN_S, sw=2.5))
    frags.append(text(420, 85, "v₀", size=13, bold=True, color=GREEN_S))

    # Пояснення принципу для v₀
    b_r, _, _ = textbox(190, 80, "Корінь v₀ (|T| = ∞)\nНащадків: 3 (скінченно)\nЗа принципом Діріхле:\n∃ cᵢ з |T(cᵢ)| = ∞", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_r)

    # Рівень 1: Нащадки v₀ -> L1_1 (скінченний), L1_2 (нескінченний v₁), L1_3 (скінченний)
    # Лінії рівня 0 -> 1
    frags.append(line(405, 98, 260, 160, color=GRAY_S, sw=1.5, dash="3,3"))
    frags.append(line(420, 102, 420, 160, color=GREEN_S, sw=3)) # Шлях
    frags.append(line(435, 98, 580, 160, color=GRAY_S, sw=1.5, dash="3,3"))

    # Вузли рівня 1
    frags.append(circle(260, 175, 18, fill=GRAY_F, stroke=GRAY_S, sw=1.5))
    frags.append(text(260, 179, "u₁", size=11, color=GRAY_S))
    frags.append(text(260, 205, "|T| = 14 (скінченне)", size=9, color=GRAY_S))

    frags.append(circle(420, 175, 20, fill=GREEN_F, stroke=GREEN_S, sw=2.5))
    frags.append(text(420, 179, "v₁", size=12, bold=True, color=GREEN_S))
    frags.append(text(420, 205, "|T(v₁)| = ∞", size=10, bold=True, color=GREEN_S))

    frags.append(circle(580, 175, 18, fill=GRAY_F, stroke=GRAY_S, sw=1.5))
    frags.append(text(580, 179, "u₂", size=11, color=GRAY_S))
    frags.append(text(580, 205, "|T| = 8 (скінченне)", size=9, color=GRAY_S))

    # Рівень 2: Нащадки v₁ -> v₂ (нескінченний), w₁ (скінченний)
    frags.append(line(410, 193, 340, 255, color=GRAY_S, sw=1.5, dash="3,3"))
    frags.append(line(428, 193, 490, 255, color=GREEN_S, sw=3))

    frags.append(circle(340, 270, 18, fill=GRAY_F, stroke=GRAY_S, sw=1.5))
    frags.append(text(340, 274, "w₁", size=11, color=GRAY_S))
    frags.append(text(340, 298, "|T| = 42", size=9, color=GRAY_S))

    frags.append(circle(490, 270, 20, fill=GREEN_F, stroke=GREEN_S, sw=2.5))
    frags.append(text(490, 274, "v₂", size=12, bold=True, color=GREEN_S))
    frags.append(text(490, 298, "|T(v₂)| = ∞", size=10, bold=True, color=GREEN_S))

    # Рівень 3: Нащадки v₂ -> v₃ (нескінченний)
    frags.append(line(480, 288, 440, 345, color=GREEN_S, sw=3))
    frags.append(line(500, 288, 550, 345, color=GRAY_S, sw=1.5, dash="3,3"))

    frags.append(circle(440, 360, 20, fill=GREEN_F, stroke=GREEN_S, sw=2.5))
    frags.append(text(440, 364, "v₃", size=12, bold=True, color=GREEN_S))
    frags.append(text(440, 388, "|T(v₃)| = ∞", size=10, bold=True, color=GREEN_S))

    frags.append(circle(550, 360, 18, fill=GRAY_F, stroke=GRAY_S, sw=1.5))
    frags.append(text(550, 364, "w₂", size=11, color=GRAY_S))

    # Нескінченна пупкова лінія далі
    frags.append(line(440, 380, 440, 430, color=GREEN_S, sw=3, dash="5,3"))
    frags.append(text(440, 450, "Нескінченна гілка P = (v₀, v₁, v₂, v₃, ...)", size=12, bold=True, color=GREEN_S))

    # Підсумковий блок збоку
    b_summary, _, _ = textbox(690, 430, "Властивість:\n1. Кожен крок локальний\n2. Гарантується DC\n3. Побудова індуктивна", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_summary)

    render(os.path.join(IMG, "fig1-konig-tree-branch.svg"), W, H, *frags)

def fig_bfs_vs_dfs_infinite():
    """fig2-bfs-vs-dfs-infinite.svg: Порівняння поведінки BFS та DFS у нескінченному пошуковому дереві."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Динаміка обходу: BFS знаходить ціль, DFS застрягає в нескінченній гілці", size=15, bold=True, color="#1e293b"))

    # Ліва панель: DFS (Застрягання)
    frags.append(rect(30, 60, 375, 360, fill="#fdf2f2", stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(217, 85, "Пошук у глибину (DFS)", size=14, bold=True, color=RED_S))

    # Дерево для DFS
    frags.append(circle(217, 120, 14, fill="#ffffff", stroke=RED_S, sw=2))
    frags.append(text(217, 124, "r", size=10, bold=True, color=RED_S))

    # Ліва гілка DFS - нескінченна пастка
    frags.append(line(210, 132, 140, 175, color=RED_S, sw=2.5))
    frags.append(circle(140, 185, 12, fill=RED_F, stroke=RED_S, sw=2))
    frags.append(line(135, 195, 110, 240, color=RED_S, sw=2.5))
    frags.append(circle(110, 250, 12, fill=RED_F, stroke=RED_S, sw=2))
    frags.append(line(110, 260, 110, 310, color=RED_S, sw=2.5, dash="4,3"))

    b_dfs_trap, _, _ = textbox(110, 345, "Пастка DFS:\nЗанурення в нескінченну\nгілку без повернення!", size=10, fill="#ffffff", stroke=RED_S)
    frags.append(b_dfs_trap)

    # Права гілка DFS - де сховано розв'язок
    frags.append(line(224, 132, 290, 175, color=GRAY_S, sw=1.5, dash="3,3"))
    frags.append(circle(290, 185, 14, fill=GREEN_F, stroke=GREEN_S, sw=2))
    frags.append(text(290, 189, "Ціль", size=9, bold=True, color=GREEN_S))
    frags.append(text(290, 215, "(Не буде досягнута DFS)", size=9, color=RED_S))

    # Права панель: BFS (Успіх)
    frags.append(rect(435, 60, 375, 360, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(622, 85, "Пошук у ширину (BFS)", size=14, bold=True, color=BLUE_S))

    # Дерево для BFS
    frags.append(circle(622, 120, 14, fill="#ffffff", stroke=BLUE_S, sw=2))
    frags.append(text(622, 124, "r", size=10, bold=True, color=BLUE_S))

    # Рівень 1 фронту BFS
    frags.append(line(615, 132, 545, 175, color=BLUE_S, sw=2))
    frags.append(line(629, 132, 695, 175, color=BLUE_S, sw=2))

    frags.append(circle(545, 185, 12, fill=BLUE_F, stroke=BLUE_S, sw=2))
    frags.append(text(545, 189, "1", size=10, color=BLUE_S))

    frags.append(circle(695, 185, 14, fill=GREEN_F, stroke=GREEN_S, sw=2.5))
    frags.append(text(695, 189, "Ціль", size=9, bold=True, color=GREEN_S))

    # Пунктир рівнів BFS
    frags.append(line(450, 148, 795, 148, color=AMBER_S, sw=1.5, dash="4,4"))
    frags.append(text(480, 142, "Рівень d=1", size=9, color=AMBER_S))

    frags.append(line(450, 215, 795, 215, color=AMBER_S, sw=1.5, dash="4,4"))
    frags.append(text(480, 209, "Рівень d=2", size=9, color=AMBER_S))

    b_bfs_ok, _, _ = textbox(622, 345, "Гарантія BFS:\nЗа лемою Кеніґа кожен рівень d\nскінченний → ціль на глибині d\nгарантовано буде знайдена!", size=10, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_bfs_ok)

    render(os.path.join(IMG, "fig2-bfs-vs-dfs-infinite.svg"), W, H, *frags)

def fig_kleene_tree_computability():
    """fig3-kleene-tree-computability.svg: Структура дерева Кліні (необчислюваність нескінченних гілок)."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Дерево Кліні: Обчислюване нескінченне бінарне дерево без обчислюваних гілок", size=15, bold=True, color="#1e293b"))

    # Блок обчислюваності дерева
    b_prop, _, _ = textbox(420, 80, "Властивість дерева Tₖ ⊂ 2^{<ω}:\n1. Належність вершини σ ∈ Tₖ є обчислювальною (рекурсивна множина слів)\n2. Множина вершин нескінченна (|Tₖ| = ∞) ⇒ За Лемою Кеніґа ∃ нескінченна гілка f ∈ 2^ω\n3. ЖОДНА нескінченна гілка f НЕ є обчислювальною функцією! (f ∉ Δ₁⁰, f ∈ Δ₂⁰)", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_prop)

    # Візуалізація відтинання обчислюваних кандидатів
    frags.append(rect(50, 160, 740, 280, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=8))
    frags.append(text(420, 185, "Блокування обчислювальних кандидатів алгоритмом Кліні", size=13, bold=True, color="#334155"))

    # Обчислюваний кандидат 1 (Машина Тюрінга M_e1)
    b_m1, _, _ = textbox(200, 240, "Алгоритм φₑ₁\n(Обчислювальний кандидат 1)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_m1)
    frags.append(line(200, 268, 200, 310, color=RED_S, sw=2, dash="3,3"))
    b_dead1, _, _ = textbox(200, 335, "Відтинання на кроці s:\nTₖ примусово блокує σ\nз збігом φₑ₁(n)", size=10, fill=RED_F, stroke=RED_S)
    frags.append(b_dead1)

    # Обчислюваний кандидат 2 (Машина Тюрінга M_e2)
    b_m2, _, _ = textbox(420, 240, "Алгоритм φₑ₂\n(Обчислювальний кандидат 2)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_m2)
    frags.append(line(420, 268, 420, 310, color=RED_S, sw=2, dash="3,3"))
    b_dead2, _, _ = textbox(420, 335, "Відтинання на кроці s':\nКодування двох r.e. A, B\n(A ∩ B = ∅, невідокремлювані)", size=10, fill=RED_F, stroke=RED_S)
    frags.append(b_dead2)

    # Необчислювальна гілка (Виділена)
    b_noncomp, _, _ = textbox(640, 240, "Необчислювальна гілка f\n(Оракул 0' / Стрибок K)", size=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_noncomp)
    frags.append(line(640, 268, 640, 310, color=GREEN_S, sw=2.5))
    b_path_ok, _, _ = textbox(640, 335, "Існує за Лемою Кеніґа!\nf ∤ φₑ для всіх e\nНалежить класу Δ₂⁰", size=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_path_ok)

    # Нижній підпис
    frags.append(text(420, 415, "Слабка Лема Кеніґа (WKL) доводить існування нескінченної гілки, але не гарантує її алгоритмічну побудову.", size=10, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig3-kleene-tree-computability.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_konig_tree_branch()
    fig_bfs_vs_dfs_infinite()
    fig_kleene_tree_computability()
    print("Konig lemma figures generated successfully.")
