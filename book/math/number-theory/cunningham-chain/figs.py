# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F   = "#e8eefc"
RED_F    = "#fdecea"
GREEN_F  = "#e6f7ee"
PURPLE_F = "#f3e8fa"
YELLOW_F = "#fffde6"
GRAY_F   = "#f1f5f9"

# ── 1. cunningham-tree: Структура ланцюжків 1-го та 2-го роду і двонапрямлених ланцюжків ──
def fig_cunningham_tree():
    W, H = 1000, 540
    elements = []

    # Заголовок
    elements.append(text(W / 2, 30, "Структура ланцюжків Каннінгема: рекурентний ріст та зупинка на складеному числі", size=16, color=INK, bold=True))

    # Секція 1: Ланцюжок 1-го роду (2p + 1)
    elements.append(fitbox(40, 60, 440, 36, "Ланцюжок 1-го роду: pᵢ₊₁ = 2pᵢ + 1", size=14, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))
    
    nodes_1st = [
        ("p₁ = 2", GREEN_F, POS, "Початкове просте"),
        ("p₂ = 5", GREEN_F, POS, "Безпечне просте"),
        ("p₃ = 11", GREEN_F, POS, "Безпечне просте"),
        ("p₄ = 23", GREEN_F, POS, "Безпечне просте"),
        ("p₅ = 47", GREEN_F, POS, "Безпечне просте"),
        ("p₆ = 95 = 5·19", RED_F, "#b91c1c", "Складене (Кінець, k=5)")
    ]

    y_start = 115
    for i, (val, bg, st, label) in enumerate(nodes_1st):
        y = y_start + i * 65
        elements.append(fitbox(50, y, 160, 44, val, size=13.5, fill=bg, stroke=st, sw=1.8, bold=True, color=INK))
        elements.append(fitbox(230, y + 4, 230, 36, label, size=12, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))
        if i < len(nodes_1st) - 1:
            elements.append(arrow(130, y + 44, 130, y + 65, color=NEG, sw=2))
            elements.append(text(145, y + 56, "2p+1", size=11, color=NEG, bold=True))

    # Секція 2: Ланцюжок 2-го роду (2p - 1)
    elements.append(fitbox(520, 60, 440, 36, "Ланцюжок 2-го роду: pᵢ₊₁ = 2pᵢ - 1", size=14, fill=PURPLE_F, stroke="#7e22ce", sw=2, bold=True, color=INK))

    nodes_2nd = [
        ("p₁ = 1531", GREEN_F, POS, "Початкове просте"),
        ("p₂ = 3061", GREEN_F, POS, "Просте 2-го роду"),
        ("p₃ = 6121", GREEN_F, POS, "Просте 2-го роду"),
        ("p₄ = 12241", GREEN_F, POS, "Просте 2-го роду"),
        ("p₅ = 24481", GREEN_F, POS, "Просте 2-го роду"),
        ("p₆ = 48961", GREEN_F, POS, "Просте 2-го роду"),
        ("p₇ = 97921", GREEN_F, POS, "Просте 2-го роду"),
        ("p₈ = 195841 = 79·2479", RED_F, "#b91c1c", "Складене (Кінець, k=7)")
    ]

    y_start_2 = 115
    for i, (val, bg, st, label) in enumerate(nodes_2nd):
        y = y_start_2 + i * 48
        elements.append(fitbox(530, y, 190, 36, val, size=12.5, fill=bg, stroke=st, sw=1.5, bold=True, color=INK))
        elements.append(fitbox(740, y + 2, 210, 32, label, size=11.5, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))
        if i < len(nodes_2nd) - 1:
            elements.append(arrow(625, y + 36, 625, y + 48, color="#7e22ce", sw=1.8))

    return render(os.path.join(OUT, "cunningham-tree.svg"), W, H, *elements,
                  title="Структура ланцюжків Каннінгема 1-го та 2-го роду")


# ── 2. modular-sieve-pattern: Схема модулярних перешкод ──
def fig_modular_sieve_pattern():
    W, H = 1000, 520
    elements = []

    elements.append(text(W / 2, 30, "Механізм модулярних перешкод: відсіювання за малими простими модулями q", size=16, color=INK, bold=True))

    # Таблична структура за модулями q = 3, 5, 7
    elements.append(fitbox(40, 60, 920, 45, "Залежність остач pᵢ mod q від початкового значення p₁ mod q для ланцюжка 1-го роду (2p + 1)", size=13.5, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))

    # Секція q = 3
    elements.append(fitbox(40, 120, 290, 32, "Модуль q = 3 (Період d = 1)", size=13, fill=YELLOW_F, stroke=MUTED, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(40, 160, 290, 110, "p₁ ≡ 1 (mod 3) ⇒ p₂ ≡ 0 (mod 3)\n(p₂ ділиться на 3 → складене!)\n\np₁ ≡ 2 (mod 3) ⇒ pᵢ ≡ 2 (mod 3)\n(Дозволений клас остачі!)", size=12, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))

    # Секція q = 5
    elements.append(fitbox(355, 120, 290, 32, "Модуль q = 5 (Період d = 4)", size=13, fill=YELLOW_F, stroke=MUTED, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(355, 160, 290, 110, "2⁴ ≡ 1 (mod 5)\nЯкщо p₁ ≢ 4 (mod 5), то кожний 4-й член буде ≡ 0 (mod 5).\n\nМаксимальна довжина без p₁ ≡ 4:\nk ≤ 4!", size=12, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))

    # Секція q = 7
    elements.append(fitbox(670, 120, 290, 32, "Модуль q = 7 (Період d = 3)", size=13, fill=YELLOW_F, stroke=MUTED, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(670, 160, 290, 110, "2³ ≡ 1 (mod 7)\nЯкщо p₁ ≢ 6 (mod 7), то кожний 3-й член буде ≡ 0 (mod 7).\n\nМаксимальна довжина без p₁ ≡ 6:\nk ≤ 3!", size=12, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))

    # Нижній блок синтезу
    elements.append(fitbox(40, 295, 920, 195, 
                           "ГОЛОВНИЙ ВИСНОВОК ЩОДО ДОВГИХ ЛАНЦЮЖКІВ:\n\n"
                           "• Для будь-якого простого модуля q, якщо p₁ + 1 ≢ 0 (mod q), ланцюжок 1-го роду обов'язково містить член, кратний q, не пізніше ніж через d кроків (де d — порядок двійки mod q).\n"
                           "• Щоб побудувати довгий ланцюжок (k ≥ 6), початковий член p₁ ПОВИНЕН задовольняти систему конгруенцій:\n"
                           "  p₁ ≡ -1 ≡ 2 (mod 3),  p₁ ≡ -1 ≡ 4 (mod 5),  p₁ ≡ -1 ≡ 6 (mod 7),  p₁ ≡ -1 ≡ 10 (mod 11)...\n"
                           "• За Китайською теоремою про остачі це означає: p₁ ≡ -1 (mod 3·5·7·11...) = -1 (mod 2310...).",
                           size=12.5, fill=GREEN_F, stroke=POS, sw=2, bold=True, color=INK))

    return render(os.path.join(OUT, "modular-sieve-pattern.svg"), W, H, *elements,
                  title="Механізм модулярних перешкод")


# ── 3. bateman-horn-density: Асимптотичний спад щільності ──
def fig_bateman_horn_density():
    W, H = 1000, 500
    elements = []

    elements.append(text(W / 2, 30, "Асимптотична щільність ланцюжків Каннінгема πₖ(x) ~ Cₖ · x / (ln x)ₖ", size=16, color=INK, bold=True))

    # Пояснювальний блок ліворуч
    elements.append(fitbox(40, 70, 420, 400,
                           "ГІПОТЕЗА БЕЙТМАНА — ГОРНА ТА КЛАСТЕРИЗАЦІЯ:\n\n"
                           "1. Експоненційне згасання:\n"
                           "   Кількість ланцюжків довжини k до межі x пропорційна x / (ln x)ᵏ.\n"
                           "   Кожний наступний крок k додає множник 1 / ln x ≈ 1 / 28 для x ≈ 10¹².\n\n"
                           "2. Стала Констант-Множник Cₖ:\n"
                           "   Враховує модулярне відсіювання малими простими числами.\n"
                           "   C₁ ≈ 1 (Теорема про розподіл простих чисел)\n"
                           "   C₂ ≈ 1.32032 (Константа Близнюків / Жермен)\n"
                           "   C₃ ≈ 2.8582, C₄ ≈ 4.1511...\n\n"
                           "3. Наслідок для рекордно довгих ланцюжків:\n"
                           "   Для k = 17 або k = 19 величина (ln x)ᵏ стає колосальною.\n"
                           "   Пошук вимагає чисел x > 10¹⁸ та розподілених обчислень.",
                           size=12, fill=PURPLE_F, stroke="#7e22ce", sw=1.5, color=INK))

    # Порівняльна таблиця праворуч
    elements.append(fitbox(480, 70, 480, 40, "Відносна рідкісність ланцюжків для x = 10¹² (ln x ≈ 27.6)", size=13, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))

    rows = [
        ("k = 1 (Прості числа)", "π₁(x) ≈ x / ln x", "37 607 912 018", GREEN_F),
        ("k = 2 (Пари Жермен)", "π₂(x) ≈ C₂ · x / (ln x)²", "1 740 000 000", GREEN_F),
        ("k = 3 (Ланцюжки k=3)", "π₃(x) ≈ C₃ · x / (ln x)³", "130 000 000", GREEN_F),
        ("k = 4 (Ланцюжки k=4)", "π₄(x) ≈ C₄ · x / (ln x)⁴", "9 200 000", YELLOW_F),
        ("k = 5 (Ланцюжки k=5)", "π₅(x) ≈ C₅ · x / (ln x)⁵", "710 000", YELLOW_F),
        ("k = 6 (Ланцюжки k=6)", "π₆(x) ≈ C₆ · x / (ln x)⁶", "55 000", RED_F),
        ("k = 7 (Ланцюжки k=7)", "π₇(x) ≈ C₇ · x / (ln x)⁷", "4 200", RED_F),
    ]

    y_start = 120
    for i, (k_name, formula, count_str, bg) in enumerate(rows):
        y = y_start + i * 50
        elements.append(fitbox(480, y, 160, 42, k_name, size=12, fill=bg, stroke=MUTED, sw=1.2, bold=True, color=INK))
        elements.append(fitbox(645, y, 165, 42, formula, size=11.5, fill=GRAY_F, stroke=MUTED, sw=1, color=INK))
        elements.append(fitbox(815, y, 145, 42, count_str, size=12, fill=bg, stroke=MUTED, sw=1.2, bold=True, color=INK))

    return render(os.path.join(OUT, "bateman-horn-density.svg"), W, H, *elements,
                  title="Асимптотична щільність ланцюжків Каннінгема")


if __name__ == "__main__":
    fig_cunningham_tree()
    fig_modular_sieve_pattern()
    fig_bateman_horn_density()
    print("Figures generated successfully!")
