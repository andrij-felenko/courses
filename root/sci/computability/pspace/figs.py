# -*- coding: utf-8 -*-
"""Фігури для теми «Клас PSPACE: поліноміальна пам'ять» (book/algorithms/complexity-computability/pspace)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eef2ff", "#3b82f6"
GREEN_F, GREEN_S = "#f0fdf4", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"


def fig_complexity_hierarchy():
    """complexity-hierarchy.svg: Вкладеність класів складності від P до EXPTIME з виділенням PSPACE."""
    W, H = 860, 480
    frags = []

    # Фон
    frags.append(rect(10, 10, 840, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # EXPTIME
    frags.append(rect(30, 30, 800, 420, fill="#f8fafc", stroke="#64748b", sw=2, rx=12))
    frags.append(text(430, 58, "EXPTIME — час O(2ⁿᵏ)", size=16, bold=True, color="#334155"))

    # PSPACE / NPSPACE
    frags.append(rect(60, 80, 740, 355, fill=PURPLE_F, stroke=PURPLE_S, sw=2.5, rx=10))
    frags.append(text(430, 108, "PSPACE = NPSPACE — пам'ять O(nᵏ) [Теорема Савича]", size=16, bold=True, color=PURPLE_S))
    frags.append(text(710, 108, "TQBF, Ігри", size=13, bold=True, color=PURPLE_S))

    # PH (Polynomial Hierarchy)
    frags.append(rect(90, 130, 680, 290, fill=BLUE_F, stroke=BLUE_S, sw=2, rx=8))
    frags.append(text(430, 156, "PH — Поліноміальна ієрархія (Σₖᵖ, Πₖᵖ)", size=15, bold=True, color=BLUE_S))

    # NP & coNP (Розміщуємо у верхньому ярусі PH)
    frags.append(rect(110, 175, 310, 115, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=8))
    frags.append(text(265, 200, "NP (перевірка ∃)", size=14, bold=True, color=AMBER_S))
    frags.append(text(265, 226, "SAT, 3-SAT, Кліка", size=12, color=INK))

    frags.append(rect(440, 175, 310, 115, fill=RED_F, stroke=RED_S, sw=1.8, rx=8))
    frags.append(text(595, 200, "coNP (перевірка ∀)", size=14, bold=True, color=RED_S))
    frags.append(text(595, 226, "TAUTOLOGY, UNSAT", size=12, color=INK))

    # P (Розміщуємо у нижньому ярусі PH, під NP і coNP)
    frags.append(rect(110, 305, 640, 100, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=8))
    frags.append(text(430, 330, "P — детермінований поліномний час O(nᵏ)", size=14, bold=True, color=GREEN_S))

    # L / NL всередині P
    frags.append(rect(230, 348, 400, 45, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(430, 375, "L ⊆ NL (логарифмічна пам'ять O(log n))", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "complexity-hierarchy.svg"), W, H, *frags)


def fig_savitch_divide_conquer():
    """savitch-divide-conquer.svg: Рекурсивний поділ навпіл у графі конфігурацій за теоремою Савича."""
    W, H = 860, 420
    frags = []

    # Заголовок / рамка
    frags.append(rect(10, 10, 840, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 38, "Теорема Савича: Перевірка досяжності Reach(C₁, C₂, k)", size=16, bold=True, color=INK))

    # Вузол Старт
    b_start, _, _ = textbox(100, 140, "Стартова\nконфігурація C_in", size=13, pad=10, fill=GREEN_F, stroke=GREEN_S, sw=2, min_w=140)
    frags.append(b_start)

    # Проміжний вузол C_mid
    b_mid, _, _ = textbox(430, 140, "Проміжна\nконфігурація C_mid", size=13, pad=10, fill=AMBER_F, stroke=AMBER_S, sw=2, min_w=150)
    frags.append(b_mid)

    # Вузол Фініш
    b_acc, _, _ = textbox(760, 140, "Приймаюча\nконфігурація C_acc", size=13, pad=10, fill=BLUE_F, stroke=BLUE_S, sw=2, min_w=140)
    frags.append(b_acc)

    # Стрілки рекурсивних викликів
    frags.append(arrow(180, 140, 345, 140, color=LINE, sw=2))
    frags.append(text(262, 125, "Крок 1: Reach(C_in, C_mid, k-1)", size=12, bold=True, color=LINE))
    frags.append(text(262, 160, "Довжина шляху ≤ 2ᵏ⁻¹", size=11, color=MUTED))

    frags.append(arrow(515, 140, 680, 140, color=LINE, sw=2))
    frags.append(text(597, 125, "Крок 2: Reach(C_mid, C_acc, k-1)", size=12, bold=True, color=LINE))
    frags.append(text(597, 160, "Довжина шляху ≤ 2ᵏ⁻¹", size=11, color=MUTED))

    # Стековий фрейм (пояснення використання пам'яті)
    frags.append(rect(60, 220, 740, 160, fill="#f8fafc", stroke=PURPLE_S, sw=1.8, rx=8))
    frags.append(text(430, 245, "Стек рекурсії для перебору всіх кандидатів C_mid:", size=14, bold=True, color=PURPLE_S))

    frags.append(text(430, 275, "1. Глибина рекурсії: m = O(S(n)) рівнів (оскільки 2ᵐ ≥ кількість конфігурацій)", size=12, color=INK))
    frags.append(text(430, 305, "2. Розмір одного фрейму: O(S(n)) бітів (збереження конфігурації C_mid та лічильника)", size=12, color=INK))
    frags.append(text(430, 335, "3. Загальна пам'ять: S_детерм(n) = Depth × FrameSize = O(S(n)) × O(S(n)) = O(S(n)²)", size=13, bold=True, color=POS))

    render(os.path.join(IMG, "savitch-divide-conquer.svg"), W, H, *frags)


def fig_tqbf_game_tree():
    """tqbf-game-tree.svg: Дерево гри для TQBF з чергуванням кванторів ∃ та ∀."""
    W, H = 860, 440
    frags = []

    # Заголовок / рамка
    frags.append(rect(10, 10, 840, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 35, "Дерево гри TQBF: ∃x₁ ∀x₂ ∃x₃ ... (Оцінка в поліномній пам'яті)", size=16, bold=True, color=INK))

    # Корінь (∃x₁)
    b_root, _, _ = textbox(430, 80, "Гравець ∃ (x₁)\nОбирає гілку з TRUE (OR)", size=12, pad=8, fill=AMBER_F, stroke=AMBER_S, sw=2, min_w=180)
    frags.append(b_root)

    # Рівень 1 (∀x₂)
    b_l1, _, _ = textbox(240, 170, "Гравець ∀ (x₂=0)\nМусить дати TRUE (AND)", size=11, pad=6, fill=RED_F, stroke=RED_S, sw=1.8, min_w=170)
    b_r1, _, _ = textbox(620, 170, "Гравець ∀ (x₂=1)\nМусить дати TRUE (AND)", size=11, pad=6, fill=RED_F, stroke=RED_S, sw=1.8, min_w=170)
    frags += [b_l1, b_r1]

    # Зв'язки корінь -> рівень 1
    frags.append(arrow(370, 105, 270, 145, color=LINE, sw=1.5))
    frags.append(text(300, 120, "x₁ = 0", size=11, bold=True, color=INK))

    frags.append(arrow(490, 105, 590, 145, color=LINE, sw=1.5))
    frags.append(text(560, 120, "x₁ = 1", size=11, bold=True, color=INK))

    # Рівень 2 (Листки / Обчислення)
    b_ll2, _, _ = textbox(150, 260, "x₃=0: TRUE", size=11, pad=6, fill=GREEN_F, stroke=GREEN_S, sw=1.5, min_w=110)
    b_lr2, _, _ = textbox(330, 260, "x₃=1: FALSE", size=11, pad=6, fill=RED_F, stroke=RED_S, sw=1.5, min_w=110)

    b_rl2, _, _ = textbox(530, 260, "x₃=0: FALSE", size=11, pad=6, fill=RED_F, stroke=RED_S, sw=1.5, min_w=110)
    b_rr2, _, _ = textbox(710, 260, "x₃=1: TRUE", size=11, pad=6, fill=GREEN_F, stroke=GREEN_S, sw=1.5, min_w=110)
    frags += [b_ll2, b_lr2, b_rl2, b_rr2]

    # Зв'язки рівень 1 -> рівень 2
    frags.append(arrow(210, 195, 170, 235, color=LINE, sw=1.5))
    frags.append(arrow(270, 195, 310, 235, color=LINE, sw=1.5))
    frags.append(arrow(590, 195, 550, 235, color=LINE, sw=1.5))
    frags.append(arrow(650, 195, 690, 235, color=LINE, sw=1.5))

    # Нижня рамка з висновком
    frags.append(rect(40, 320, 780, 90, fill=BLUE_F, stroke=BLUE_S, sw=1.8, rx=8))
    frags.append(text(430, 345, "Чому це потребує лише поліномної пам'яті O(n):", size=13, bold=True, color=BLUE_S))
    frags.append(text(430, 370, "Пошук у глибину (DFS) зберігає в пам'яті лише один поточний шлях від кореня до листка.", size=12, color=INK))
    frags.append(text(430, 395, "Глибина дерева = n змінних → Пам'ять O(n), хоча кількість листків = 2ⁿ (час O(2ⁿ)).", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "tqbf-game-tree.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_complexity_hierarchy()
    fig_savitch_divide_conquer()
    fig_tqbf_game_tree()
    print("Всі фігури для PSPACE успішно згенеровано.")
