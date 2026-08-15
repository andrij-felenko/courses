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

# ── 1. mersenne-binary-shift: Двійкова анатомія та циклічний зсув ──
def fig_binary_shift():
    W, H = 960, 420
    elements = []

    elements.append(text(W / 2, 35, "Двійкова структура числа M₅ = 2⁵ − 1 = 31 та циклічний зсув", size=17, color=INK, bold=True))

    # Блок 1: Степінь 2^5
    elements.append(fitbox(50, 75, 410, 140, "Степінь двійки: 2⁵ = 32₁₀ = 100000₂\nОдна одиниця у 5-му розряді", size=14, fill=BLUE_F, stroke=NEG, sw=2, color=INK))

    # Блок 2: Число Мерсенна M_5
    elements.append(fitbox(500, 75, 410, 140, "Число Мерсенна: M₅ = 2⁵ − 1 = 31₁₀ = 11111₂\nЗаповнена стрічка з 5 одиниць", size=14, fill=GREEN_F, stroke=FIELD, sw=2, color=INK))

    elements.append(arrow(465, 145, 495, 145, color=LINE, sw=2))

    # Блок 3: Схема циклічного зсуву modulo M_n
    elements.append(fitbox(50, 245, 860, 145, "Особливість арифметики за модулем Mₙ = 2ⁿ − 1:\nМноження на 2ᵏ еквівалентне циклічному зсуву бітів у n-бітовому регістрі\n2ⁿ ≡ 1 (mod Mₙ) ⇒ Переповнення вищого розряду повертається у молодший біт", size=14, fill=YELLOW_F, stroke=LINE, sw=1.8, color=INK))

    return render(os.path.join(OUT, "mersenne-binary-shift.svg"), W, H, *elements,
                  title="Двійкова анатомія та циклічний зсув чисел Мерсенна")


# ── 2. divisibility-pattern: Структура розкладу M_6 = 63 ──
def fig_divisibility_pattern():
    W, H = 960, 440
    elements = []

    elements.append(text(W / 2, 35, "Розклад числа Мерсенна M₆ = 2⁶ − 1 = 63 через дільники показника", size=17, color=INK, bold=True))

    # M_6 у двійковій
    elements.append(fitbox(280, 70, 400, 55, "M₆ = 111111₂ = 63₁₀", size=16, fill=PURPLE_F, stroke=INK, sw=2, bold=True, color=INK))

    # Гілка 1: Показник a = 2 -> M_2 = 3
    elements.append(arrow(380, 130, 240, 185, color=NEG, sw=2))
    elements.append(fitbox(50, 190, 380, 180, "Показник a = 2 (дві одиниці):\nM₂ = 11₂ = 3₁₀\n\n111111₂ = 11₂ · (100010₂ + 1₂)\n63 = 3 · 21\nБлоки: [11][11][11]", size=13.5, fill=BLUE_F, stroke=NEG, sw=2, color=INK))

    # Гілка 2: Показник b = 3 -> M_3 = 7
    elements.append(arrow(580, 130, 720, 185, color=POS, sw=2))
    elements.append(fitbox(530, 190, 380, 180, "Показник b = 3 (три одиниці):\nM₃ = 111₂ = 7₁₀\n\n111111₂ = 111₂ · (1001₂)\n63 = 7 · 9\nБлоки: [111][111]", size=13.5, fill=RED_F, stroke=POS, sw=2, color=INK))

    elements.append(fitbox(150, 390, 660, 35, "Загальний принцип: Якщо a | b, то Ma | Mb", size=14, fill=YELLOW_F, stroke=LINE, sw=1.5, bold=True, color=INK))

    return render(os.path.join(OUT, "divisibility-pattern.svg"), W, H, *elements,
                  title="Структура розкладу M6 через дільники показника")


# ── 3. gcd-lattice: Ізоморфізм ґраток НСД ──
def fig_gcd_lattice():
    W, H = 960, 420
    elements = []

    elements.append(text(W / 2, 35, "Збереження НСД: НСД(2ᵃ − 1, 2ᵇ − 1) = 2^(НСД(a, b)) − 1", size=17, color=INK, bold=True))

    # Ліва ґратка (показники)
    elements.append(fitbox(60, 85, 380, 240, "Показники степеня:\n\na = 12,  b = 18\n\nНСД(12, 18) = 6\n\nАлгоритм Евкліда:\n18 = 1 · 12 + 6\n12 = 2 · 6 + 0", size=14, fill=BLUE_F, stroke=NEG, sw=2, color=INK))

    # Стрілка відповідності
    elements.append(arrow(450, 205, 510, 205, color=FIELD, sw=3))
    elements.append(fitbox(455, 160, 50, 30, "Mₙ", size=14, fill=GREEN_F, stroke=FIELD, sw=1.5, bold=True, color=INK))

    # Права ґратка (числа Мерсенна)
    elements.append(fitbox(520, 85, 380, 240, "Числа Мерсенна:\n\nM₁₂ = 4095,  M₁₈ = 262143\n\nНСД(M₁₂, M₁₈) = M₆ = 63\n\nАлгоритм Евкліда на Mₙ:\nM₁₈ = 2⁶ · M₁₂ + M₆", size=14, fill=GREEN_F, stroke=FIELD, sw=2, color=INK))

    elements.append(fitbox(80, 350, 800, 45, "Операція n ↦ 2ⁿ − 1 є ізоморфізмом адитивної ґратки НСД натуральних чисел у мультиплікативну ґратку чисел Мерсенна", size=13.5, fill=YELLOW_F, stroke=LINE, sw=1.5, bold=True, color=INK))

    return render(os.path.join(OUT, "gcd-lattice.svg"), W, H, *elements,
                  title="Ізоморфізм ґраток НСД показників та чисел Мерсенна")


# ── 4. prime-factor-structure: Структура простих дільників q = 2kp + 1 ──
def fig_prime_factor_structure():
    W, H = 960, 440
    elements = []

    elements.append(text(W / 2, 35, "Структура простих дільників q для Mₚ = 2ᵖ − 1 (p — просте)", size=17, color=INK, bold=True))

    # Вхідне Mp
    elements.append(fitbox(330, 65, 300, 50, "Число Мерсенна Mₚ (p — просте)", size=15, fill=PURPLE_F, stroke=INK, sw=2, bold=True, color=INK))

    elements.append(arrow(480, 115, 480, 155, color=LINE, sw=2))

    # Будова проста q
    elements.append(fitbox(100, 160, 760, 110, "Будь-який простий дільник q числа Mₚ задовольняє дві суворі умови:\n1) q ≡ 1 (mod 2p)  ⇒  q = 2kp + 1  (для деякого цілого k ≥ 1)\n2) q ≡ ±1 (mod 8)  ⇒  2 є квадратичним лишком за модулем q", size=14, fill=BLUE_F, stroke=NEG, sw=2, color=INK))

    elements.append(arrow(480, 270, 480, 305, color=LINE, sw=2))

    # Приклад M_11 = 2047
    elements.append(fitbox(60, 310, 840, 105, "Приклад: M₁₁ = 2047 = 23 · 89 (p = 11)\n- Для q = 23:  23 = 2·1·11 + 1  (k=1)  та  23 ≡ 7 ≡ −1 (mod 8)\n- Для q = 89:  89 = 2·4·11 + 1  (k=4)  та  89 ≡ 1 (mod 8)", size=13.5, fill=GREEN_F, stroke=FIELD, sw=2, color=INK))

    return render(os.path.join(OUT, "prime-factor-structure.svg"), W, H, *elements,
                  title="Структура простих дільників чисел Мерсенна")

if __name__ == "__main__":
    fig_binary_shift()
    fig_divisibility_pattern()
    fig_gcd_lattice()
    fig_prime_factor_structure()
    print("All figures successfully generated in img/")
