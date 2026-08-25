# -*- coding: utf-8 -*-
"""Фігури для теми «Арифметика Пеано» (book/algorithms/complexity-computability/peano-arithmetic)."""
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

def fig_arithmetic_spectrum():
    """fig1-arithmetic-spectrum.svg: Спектр формальних арифметичних систем."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Спектр формальних арифметичних систем", size=16, bold=True, color="#1e293b"))

    cols = [
        ("Арифметика Пресбурга", TEAL_F, TEAL_S, ["Сигнатура: (0, S, +)", "Без множення", "Повна & Розв'язна", "Складність: 2^2^cn"]),
        ("Арифметика Робінсона Q", AMBER_F, AMBER_S, ["Сигнатура: (0, S, +, ·)", "Без схеми індукції", "Неповна & Нерозв'язна", "Скінченні аксіоми"]),
        ("Арифметика Пеано PA", BLUE_F, BLUE_S, ["Сигнатура: (0, S, +, ·)", "Схема індукції Σ₀..∞", "Неповна & Нерозв'язна", "Зліченні аксіоми"]),
        ("Арифметика 2-го порядку", PURPLE_F, PURPLE_S, ["Квантори за множинами", "Повна індукція", "Категорична модель", "Неефективна теорія"])
    ]

    x_start = 25
    col_w = 190
    gap = 20

    for i, (title, fill_c, stroke_c, lines) in enumerate(cols):
        cx = x_start + i * (col_w + gap)
        frags.append(rect(cx, 60, col_w, 310, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        
        # Використовуємо текстовий блок без додаткових вкладених тагів
        frags.append(rect(cx + 10, 75, col_w - 20, 34, fill="#ffffff", stroke=stroke_c, sw=1, rx=5))
        frags.append(text(cx + col_w // 2, 96, title, size=12, bold=True, color=stroke_c))

        y_text = 140
        for line in lines:
            frags.append(text(cx + col_w // 2, y_text, line, size=11, color="#334155"))
            y_text += 32

        if i < 3:
            ax = cx + col_w + 2
            frags.append(arrow(ax, 200, ax + gap - 4, 200, color="#64748b", sw=1.5))

    render(os.path.join(IMG, "fig1-arithmetic-spectrum.svg"), W, H, *frags)

def fig_induction_and_representability():
    """fig2-induction-and-representability.svg: Схема індукції та β-функція Ґеделя."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Схема індукції та кодування обчислень через β-функцію Ґеделя", size=16, bold=True, color="#1e293b"))

    # Лівий блок: Схема індукції
    frags.append(rect(30, 60, 395, 320, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(227, 88, "Синтаксис схеми індукції у PA", size=14, bold=True, color=BLUE_S))

    frags.append(rect(60, 115, 335, 36, fill="#ffffff", stroke=BLUE_S, sw=1, rx=5))
    frags.append(text(227, 137, "База індукції: φ(0)", size=12, color=BLUE_S))

    frags.append(rect(60, 175, 335, 36, fill="#ffffff", stroke=BLUE_S, sw=1, rx=5))
    frags.append(text(227, 197, "Крок індукції: ∀x (φ(x) → φ(S(x)))", size=12, color=BLUE_S))

    frags.append(rect(60, 245, 335, 40, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=5))
    frags.append(text(227, 269, "Висновок: ∀x φ(x)", size=13, bold=True, color=GREEN_S))

    frags.append(arrow(227, 151, 227, 175, color=BLUE_S, sw=2))
    frags.append(arrow(227, 211, 227, 245, color=BLUE_S, sw=2))

    # Правий блок: β-функція Ґеделя
    frags.append(rect(455, 60, 395, 320, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(652, 88, "β-функція Ґеделя (Кодування послідовностей)", size=14, bold=True, color=PURPLE_S))

    frags.append(text(652, 125, "β(a, b, i) = a mod (1 + (i + 1) · b)", size=12, bold=True, color="#0f172a"))
    
    frags.append(rect(485, 155, 335, 40, fill="#ffffff", stroke=PURPLE_S, sw=1, rx=5))
    frags.append(text(652, 179, "Послідовність чисел: a₀, a₁, a₂, ..., aₖ", size=11, color=PURPLE_S))

    frags.append(rect(485, 235, 335, 48, fill=TEAL_F, stroke=TEAL_S, sw=1, rx=5))
    frags.append(text(652, 255, "Кодується парою натуральних чисел (a, b)", size=11, color=TEAL_S))
    frags.append(text(652, 273, "через Китайську теорему про залишки", size=11, color=TEAL_S))

    frags.append(arrow(652, 195, 652, 235, color=PURPLE_S, sw=2))
    
    frags.append(text(652, 330, "Забезпечує Σ₁-виражуваність рекурсивних функцій у PA", size=11, color="#475569", bold=True))

    render(os.path.join(IMG, "fig2-induction-and-representability.svg"), W, H, *frags)

def fig_peano_incompleteness_map():
    """fig3-peano-incompleteness-map.svg: Неповнота PA та недоведені твердження."""
    W, H = 880, 430
    frags = []

    frags.append(rect(10, 10, 860, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Ландшафт довідності у PA та недоведені математичні істини", size=16, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 820, 340, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=10))
    frags.append(text(440, 85, "Множина всіх істинних арифметичних тверджень Th(ℕ) (Семантична істина)", size=13, bold=True, color="#334155"))

    # Внутрішній блок: Виведені у PA (PA ⊢ φ)
    frags.append(rect(50, 110, 400, 270, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(250, 135, "Довідні твердження у PA (PA ⊢ φ)", size=13, bold=True, color=GREEN_S))

    pa_provable = [
        "· Основна теорема арифметики",
        "· Нескінченність простих чисел",
        "· Алгоритм Евкліда",
        "· Комутативність додавання й множення",
        "· Скінченна арифметика й поліноми"
    ]
    y_p = 170
    for item in pa_provable:
        frags.append(text(250, y_p, item, size=11, color="#1e293b"))
        y_p += 38

    # Блок праворуч: Істинні, але недоведені у PA (Th(N) \\ PA)
    frags.append(rect(470, 110, 360, 270, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(650, 135, "Недоведені істини (Th(ℕ) \\ PA)", size=13, bold=True, color=RED_S))

    unprovable = [
        "· Речення Ґеделя G_PA (Самореферентність)",
        "· Несуперечливість PA (Consis(PA))",
        "· Теорема Ґудстейна (Goodstein Theorem)",
        "· Теорема Парижа — Гаррінгтона (Ramsey)",
        "· Теорема Кірбі — Паріса (Hydra Game)"
    ]
    y_u = 170
    for item in unprovable:
        frags.append(text(650, y_u, item, size=11, color="#7f1d1d"))
        y_u += 38

    render(os.path.join(IMG, "fig3-peano-incompleteness-map.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_arithmetic_spectrum()
    fig_induction_and_representability()
    fig_peano_incompleteness_map()
    print("Figures generated successfully!")
