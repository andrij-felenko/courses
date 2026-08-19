# -*- coding: utf-8 -*-
"""Фігури для теми «Системи переписування термів» (book/algorithms/complexity-computability/term-rewriting-systems)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_confluence_diamond():
    """confluence-diamond.svg: Конфлюентність, локальна конфлюентність та лема Ньюмана."""
    W, H = 880, 430
    frags = []

    frags.append(rect(10, 10, 860, 410, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Властивості збіжності: Конфлюентність, локальна конфлюентність і ромб Чорча-Россера", size=15, bold=True, color="#1e293b"))

    # Ліва панель: Конфлюентність (Confluence / Church-Rosser)
    frags.append(rect(25, 60, 395, 340, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(rect(35, 72, 375, 32, fill="#ffffff", stroke=BLUE_S, sw=1, rx=5))
    frags.append(text(222, 93, "Глобальна конфлюентність (CR)", size=13, bold=True, color=BLUE_S))

    # Вершина s
    frags.append(circle(222, 140, 22, fill="#ffffff", stroke=BLUE_S, sw=2))
    frags.append(text(222, 145, "s", size=14, bold=True, color="#1e293b"))

    # Гілки t1 і t2
    frags.append(circle(115, 230, 22, fill="#ffffff", stroke=BLUE_S, sw=2))
    frags.append(text(115, 235, "t₁", size=14, bold=True, color="#1e293b"))

    frags.append(circle(330, 230, 22, fill="#ffffff", stroke=BLUE_S, sw=2))
    frags.append(text(330, 235, "t₂", size=14, bold=True, color="#1e293b"))

    # Спільний терм u
    frags.append(circle(222, 320, 22, fill=GREEN_F, stroke=GREEN_S, sw=2))
    frags.append(text(222, 325, "u", size=14, bold=True, color=GREEN_S))

    # Стрілки глобальних редукцій (* кроків)
    frags.append(arrow(206, 155, 131, 215, color=BLUE_S, sw=1.8))
    frags.append(text(152, 175, "→*", size=13, bold=True, color=BLUE_S))

    frags.append(arrow(238, 155, 314, 215, color=BLUE_S, sw=1.8))
    frags.append(text(292, 175, "→*", size=13, bold=True, color=BLUE_S))

    frags.append(line(131, 245, 206, 305, color=GREEN_S, sw=1.8, dash="4,3"))
    frags.append(arrow(131, 245, 206, 305, color=GREEN_S, sw=1.8))
    frags.append(text(152, 288, "→*", size=13, bold=True, color=GREEN_S))

    frags.append(line(314, 245, 238, 305, color=GREEN_S, sw=1.8, dash="4,3"))
    frags.append(arrow(314, 245, 238, 305, color=GREEN_S, sw=1.8))
    frags.append(text(292, 288, "→*", size=13, bold=True, color=GREEN_S))

    frags.append(text(222, 375, "Будь-які два шляхи зводяться до спільного u", size=12, color="#334155"))

    # Права панель: Локальна конфлюентність (WCR) та Лема Ньюмана
    frags.append(rect(460, 60, 395, 340, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(rect(470, 72, 375, 32, fill="#ffffff", stroke=PURPLE_S, sw=1, rx=5))
    frags.append(text(657, 93, "Локальна конфлюентність (WCR) та SN", size=13, bold=True, color=PURPLE_S))

    # Вершина s
    frags.append(circle(657, 140, 22, fill="#ffffff", stroke=PURPLE_S, sw=2))
    frags.append(text(657, 145, "s", size=14, bold=True, color="#1e293b"))

    # Гілки t1 і t2 (1 крок!)
    frags.append(circle(550, 230, 22, fill="#ffffff", stroke=PURPLE_S, sw=2))
    frags.append(text(550, 235, "t₁", size=14, bold=True, color="#1e293b"))

    frags.append(circle(765, 230, 22, fill="#ffffff", stroke=PURPLE_S, sw=2))
    frags.append(text(765, 235, "t₂", size=14, bold=True, color="#1e293b"))

    # Спільний терм v
    frags.append(circle(657, 320, 22, fill=GREEN_F, stroke=GREEN_S, sw=2))
    frags.append(text(657, 325, "v", size=14, bold=True, color=GREEN_S))

    # Стрілки 1 кроку
    frags.append(arrow(641, 155, 566, 215, color=PURPLE_S, sw=1.8))
    frags.append(text(588, 175, "→₁", size=13, bold=True, color=PURPLE_S))

    frags.append(arrow(673, 155, 749, 215, color=PURPLE_S, sw=1.8))
    frags.append(text(725, 175, "→₁", size=13, bold=True, color=PURPLE_S))

    frags.append(line(566, 245, 641, 305, color=GREEN_S, sw=1.8, dash="4,3"))
    frags.append(arrow(566, 245, 641, 305, color=GREEN_S, sw=1.8))
    frags.append(text(588, 288, "→*", size=13, bold=True, color=GREEN_S))

    frags.append(line(749, 245, 673, 305, color=GREEN_S, sw=1.8, dash="4,3"))
    frags.append(arrow(749, 245, 673, 305, color=GREEN_S, sw=1.8))
    frags.append(text(725, 288, "→*", size=13, bold=True, color=GREEN_S))

    frags.append(text(657, 375, "Лема Ньюмана: WCR + Термінація (SN) ⇒ CR", size=12, bold=True, color=PURPLE_S))

    render(os.path.join(IMG, "confluence-diamond.svg"), W, H, *frags)

def fig_critical_pair_overlap():
    """critical-pair-overlap.svg: Накладання правил та утворення критичної пари."""
    W, H = 880, 390
    frags = []

    frags.append(rect(10, 10, 860, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Геометрія критичної пари: Накладання правил l₁ → r₁ та l₂ → r₂ у підтермі", size=15, bold=True, color="#1e293b"))

    # Центральне дерево накладання: mu(l1)
    frags.append(rect(300, 65, 280, 115, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(440, 90, "Уніфікований терм:  t = l₁μ", size=13, bold=True, color=AMBER_S))
    frags.append(rect(360, 108, 160, 56, fill="#ffffff", stroke=AMBER_S, sw=1.2, rx=5))
    frags.append(text(440, 130, "Підтерм t|ₚ = l₁|ₚμ", size=11, bold=True, color="#1e293b"))
    frags.append(text(440, 150, "= l₂μ  (найзагальніший уніфікатор μ)", size=10, color="#64748b"))

    # Ліва гілка: редукція за правилом 1 у корені
    frags.append(arrow(340, 185, 170, 245, color=BLUE_S, sw=2))
    frags.append(text(210, 205, "Редукція кореня: l₁ → r₁", size=11, bold=True, color=BLUE_S))

    frags.append(rect(40, 250, 260, 75, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(170, 275, "Лівий результат:  r₁μ", size=13, bold=True, color=BLUE_S))
    frags.append(text(170, 303, "Пряма заміна всього виразу", size=11, color="#334155"))

    # Права гілка: редукція за правилом 2 у позиції p
    frags.append(arrow(540, 185, 710, 245, color=PURPLE_S, sw=2))
    frags.append(text(670, 205, "Редукція у підтермі: l₂ → r₂", size=11, bold=True, color=PURPLE_S))

    frags.append(rect(580, 250, 260, 75, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(710, 275, "Правий результат:  (l₁μ)[r₂μ]ₚ", size=13, bold=True, color=PURPLE_S))
    frags.append(text(710, 303, "Локальна заміна в піддереві p", size=11, color="#334155"))

    # Нижня стрілка зв'язку: Критична пара
    frags.append(rect(300, 335, 280, 32, fill="#ffffff", stroke=RED_S, sw=1.5, rx=6))
    frags.append(text(440, 356, "Критична пара: ⟨ r₁μ,  (l₁μ)[r₂μ]ₚ ⟩", size=12, bold=True, color=RED_S))

    frags.append(line(300, 287, 440, 335, color=RED_S, sw=1.5, dash="3,3"))
    frags.append(line(580, 287, 440, 335, color=RED_S, sw=1.5, dash="3,3"))

    render(os.path.join(IMG, "critical-pair-overlap.svg"), W, H, *frags)

def fig_knuth_bendix_completion():
    """knuth-bendix-completion.svg: Алгоритм поповнення Кнута-Бендікса."""
    W, H = 880, 450
    frags = []

    frags.append(rect(10, 10, 860, 430, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Конвеєр поповнення Кнута-Бендікса: Від рівнянь до канонічної системи", size=15, bold=True, color="#1e293b"))

    # Блок 1: Вхідні рівняння E та порядок >
    frags.append(rect(35, 65, 220, 80, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=8))
    frags.append(text(145, 93, "Вхід: Рівняння E", size=13, bold=True, color="#1e293b"))
    frags.append(text(145, 117, "Порядок редукції >", size=12, color=GRAY_S))
    frags.append(text(145, 134, "(LPO / KBO / MPO)", size=11, color=GRAY_S))

    frags.append(arrow(255, 105, 310, 105, color="#1e293b", sw=1.8))

    # Блок 2: Вибір та нормалізація рівняння
    frags.append(rect(310, 65, 260, 80, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(440, 93, "1. Нормалізація пари (s, t)", size=13, bold=True, color=BLUE_S))
    frags.append(text(440, 117, "s₀ = s↓_R ,  t₀ = t↓_R", size=12, bold=True, color="#1e293b"))
    frags.append(text(440, 134, "Спрощення поточними правилами R", size=11, color="#334155"))

    frags.append(arrow(440, 145, 440, 185, color="#1e293b", sw=1.8))

    # Блок 3: Перевірка тривіальності s0 == t0
    frags.append(rect(330, 185, 220, 60, fill=TEAL_F, stroke=TEAL_S, sw=1.5, rx=8))
    frags.append(text(440, 210, "Чи s₀ ≡ t₀ ?", size=13, bold=True, color=TEAL_S))
    frags.append(text(440, 232, "Так → Відкинути тотожність", size=11, color="#334155"))

    frags.append(arrow(440, 245, 440, 285, color="#1e293b", sw=1.8))
    frags.append(text(458, 265, "Ні", size=11, bold=True, color=RED_S))

    # Блок 4: Орієнтація за порядком >
    frags.append(rect(300, 285, 280, 85, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(440, 310, "2. Орієнтація за порядком >", size=13, bold=True, color=PURPLE_S))
    frags.append(text(440, 332, "Якщо s₀ > t₀  ⇒  R ← R ∪ {s₀ → t₀}", size=11, bold=True, color="#1e293b"))
    frags.append(text(440, 352, "Якщо неорієнтовне  ⇒  ПОМИЛКА / ПРОВАЛ", size=10, bold=True, color=RED_S))

    frags.append(arrow(580, 327, 635, 327, color="#1e293b", sw=1.8))

    # Блок 5: Обчислення критичних пар та спрощення R
    frags.append(rect(635, 275, 210, 105, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(740, 300, "3. Критичні пари", size=13, bold=True, color=AMBER_S))
    frags.append(text(740, 324, "CP(R ∪ {нове}) → E", size=12, bold=True, color="#1e293b"))
    frags.append(text(740, 345, "Взаємна редукція R", size=11, color="#334155"))
    frags.append(text(740, 365, "(inter-reduction)", size=10, color="#64748b"))

    # Зворотна петля на блок 2
    frags.append(line(740, 275, 740, 105, color=AMBER_S, sw=1.8, dash="4,3"))
    frags.append(arrow(740, 105, 570, 105, color=AMBER_S, sw=1.8))
    frags.append(text(665, 93, "Поповнення E", size=11, bold=True, color=AMBER_S))

    # Успішний вихід: Канонічна система
    frags.append(rect(35, 305, 220, 65, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(145, 332, "Вихід: Канонічна R", size=13, bold=True, color=GREEN_S))
    frags.append(text(145, 354, "Термінантна + Конфлюентна", size=11, color="#334155"))

    frags.append(line(310, 105, 145, 105, color=GREEN_S, sw=1.5))
    frags.append(arrow(145, 105, 145, 305, color=GREEN_S, sw=1.8))
    frags.append(text(75, 205, "E порожня", size=11, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "knuth-bendix-completion.svg"), W, H, *frags)

def fig_reduction_orderings_hierarchy():
    """reduction-orderings-hierarchy.svg: Ієрархія методів доведення термінації TRS."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Спектр ієрархії порядків редукції для доведення термінації (SN)", size=15, bold=True, color="#1e293b"))

    cols = [
        ("Синтаксичні спрощувальні", BLUE_F, BLUE_S, [
            "Лексикографічний (LPO)",
            "Мультимножинний (MPO)",
            "Деревний порядок (RPO)",
            "Теорема Крускала",
            "Повністю автоматизовні"
        ]),
        ("Зважені синтаксичні", PURPLE_F, PURPLE_S, [
            "Порядок Кнута-Бендікса (KBO)",
            "Вагова функція w(f) ≥ 0",
            "Умова кількості змінних",
            "Квазіпрості порядки",
            "Швидке обчислення"
        ]),
        ("Семантичні інтерпретації", TEAL_F, TEAL_S, [
            "Поліноміальні інтерпретації",
            "Матричні інтерпретації",
            "Монотонні алгебри в N, R",
            "Інтерпретація інтервалів",
            "Потужна виразна сила"
        ]),
        ("Сучасні структурні методи", AMBER_F, AMBER_S, [
            "Пари залежностей (DP)",
            "Графи залежностей",
            "DP-фреймворк (AProVE, TTT2)",
            "Модульні розбиття систем",
            "Неспрощувальні системи"
        ])
    ]

    x_start = 25
    col_w = 195
    gap = 17

    for i, (title, fill_c, stroke_c, lines) in enumerate(cols):
        cx = x_start + i * (col_w + gap)
        frags.append(rect(cx, 60, col_w, 310, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        
        frags.append(rect(cx + 8, 75, col_w - 16, 34, fill="#ffffff", stroke=stroke_c, sw=1, rx=5))
        frags.append(text(cx + col_w // 2, 96, title, size=11, bold=True, color=stroke_c))

        y_text = 140
        for line in lines:
            frags.append(text(cx + col_w // 2, y_text, line, size=11, color="#334155"))
            y_text += 34

        if i < 3:
            ax = cx + col_w + 1
            frags.append(arrow(ax, 200, ax + gap - 2, 200, color="#64748b", sw=1.5))

    render(os.path.join(IMG, "reduction-orderings-hierarchy.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_confluence_diamond()
    fig_critical_pair_overlap()
    fig_knuth_bendix_completion()
    fig_reduction_orderings_hierarchy()
    print("All figures generated successfully.")
