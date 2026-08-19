# -*- coding: utf-8 -*-
"""
Генератор фігур для теми: Аномальні криві Кобліца (book/algorithms/complexity-computability/koblitz-curves)
"""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_fig1():
    """Фігура 1: Дія ендоморфізму Фробеніуса на двійковій еліптичній кривій"""
    w, h = 820, 360
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % INK,
        '  </marker>',
        '  <marker id="arr-pos" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % POS,
        '  </marker>',
        '  <marker id="arr-field" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % FIELD,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 28, "Порівняння: Класичне подвоєння точки [2]P проти автоморфізму Фробеніуса τ(P)", size=15, bold=True))

    # Ліва колонка: Класичне подвоєння [2]P
    b1, _, _ = textbox(210, 85, "Вхідна точка P = (x, y)\nна кривій E(F₂ᵐ)", size=13, fill=FILL, stroke=LINE, min_w=280)
    out.append(b1)

    out.append(arrow(210, 120, 210, 160, color=POS, sw=2.0))
    out.append(text(215, 145, "Класичне подвоєння [2]P", size=11, color=POS, anchor="start", bold=True))

    box_doubling = (
        "Геометричне подвоєння:\n"
        "λ = x + y / x\n"
        "x₃ = λ² + λ + a\n"
        "y₃ = x² + (λ + 1)x₃\n"
        "Ціна: 1 інверсія + 2 множення + 2 піднесення"
    )
    b2, _, _ = textbox(210, 240, box_doubling, size=11, fill="#fdf2f2", stroke=POS, min_w=340)
    out.append(b2)

    # Права колонка: Ендоморфізм Фробеніуса τ(P)
    b3, _, _ = textbox(610, 85, "Вхідна точка P = (x, y)\nна кривій Кобліца Eₐ(F₂ᵐ)", size=13, fill=FILL, stroke=LINE, min_w=280)
    out.append(b3)

    out.append(arrow(610, 120, 610, 160, color=FIELD, sw=2.0))
    out.append(text(615, 145, "Ендоморфізм Фробеніуса τ(P)", size=11, color=FIELD, anchor="start", bold=True))

    box_frob = (
        "Покоординатний підйом:\n"
        "τ(x, y) = (x², y²)\n"
        "У нормальному базисі: циклічний зсув бітів на 1\n"
        "У поліноміальному базисі: лінійне множення O(m)\n"
        "Ціна: 0 множень та 0 інверсій кривої (~1 такт)"
    )
    b4, _, _ = textbox(610, 240, box_frob, size=11, fill="#edfbf2", stroke=FIELD, min_w=340)
    out.append(b4)

    # Нижній висновок
    b_bot, _, _ = textbox(w / 2, 332, "Рівняння Кобліца: τ² - μτ + 2 = 0  ⇒  [2]P = μτ(P) - τ²(P) (подвоєння виключається з обчислень)", size=12, bold=True, fill="#eef3fc", stroke=NEG, min_w=760)
    out.append(b_bot)

    out.append("</svg>")
    return "\n".join(out)

def build_fig2():
    """Фігура 2: Конвеєр скалярного множення TNAF"""
    w, h = 840, 370
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % INK,
        '  </marker>',
        '</defs>',
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 26, "Конвеєр скалярного множення Q = [k]P на основі τ-NAF", size=15, bold=True))

    # Етап 1: Вхідний скаляр
    b1, _, _ = textbox(130, 95, "Скаляр k ∈ [1, r-1]\nта точка P ∈ Eₐ(F₂ᵐ)\n(довжина k: m бітів)", size=12, fill=FILL, stroke=LINE, min_w=180)
    out.append(b1)

    out.append(arrow(225, 95, 275, 95, color=INK, sw=1.8))

    # Етап 2: Редукція Солінаса
    b2, _, _ = textbox(400, 95, "Модулярна редукція Солінаса:\nρ = k mod δ  в кільці Z[τ]\nρ = r₀ + r₁τ, де N(ρ) < 2ᵐ / h", size=12, fill="#fdf8e6", stroke="#d4ac0d", min_w=240)
    out.append(b2)

    out.append(arrow(525, 95, 575, 95, color=INK, sw=1.8))

    # Етап 3: Генерація TNAF
    b3, _, _ = textbox(700, 95, "Генерація розкладу τ-NAF:\nρ = ∑ uᵢ τⁱ\nuᵢ ∈ {0, ±1}, uᵢ·uᵢ₊₁ = 0\n(довжина l ≤ m + a)", size=12, fill="#fdf8e6", stroke="#d4ac0d", min_w=230)
    out.append(b3)

    out.append(arrow(700, 155, 700, 195, color=INK, sw=1.8))

    # Етап 4: Цикл Горнера без подвоєнь
    box_horner = (
        "Акумуляція за схемою Горнера (Frobenius-and-Add):\n"
        "Q = O;\n"
        "for i = l - 1 downto 0:\n"
        "    Q = τ(Q);                // Фробеніус: (x², y²) замість [2]Q\n"
        "    if uᵢ == +1: Q = Q + P;  // Звичайне додавання точки\n"
        "    if uᵢ == -1: Q = Q - P;  // Додавання з від'ємним знаком: (x, x + y)\n"
        "return Q;"
    )
    b4, _, _ = textbox(420, 260, box_horner, size=11, fill="#edfbf2", stroke=FIELD, min_w=680)
    out.append(b4)

    # Підсумкова стрілка до результату
    out.append(arrow(420, 318, 420, 342, color=FIELD, sw=2.0))
    out.append(text(435, 335, "Результат: Q = [k]P з нульовою кількістю подвоєнь точок!", size=12, color=FIELD, anchor="start", bold=True))

    out.append("</svg>")
    return "\n".join(out)

def build_fig3():
    """Фігура 3: Порівняння обчислювальної складності алгоритмів скалярного множення"""
    w, h = 820, 360
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        rect(0, 0, w, h, fill=BG, stroke="none")
    ]

    out.append(text(w / 2, 28, "Порівняння обчислювальних витрат скалярного множення (m = 233 біти)", size=15, bold=True))

    # Стовпчик 1: Double-and-Add (F_p)
    b1_h, _, _ = textbox(160, 80, "Double-and-Add (Fₚ)\nКласичний бінарний", size=12, bold=True, fill=FILL, stroke=LINE, min_w=200)
    out.append(b1_h)

    # Гістограма 1
    # Подвоєння: 233
    out.append(rect(65, 120, 190, 80, fill="#fadbd8", stroke=POS, rx=4))
    out.append(text(160, 155, "233 подвоєння [2]P", size=12, bold=True, color=POS))
    out.append(text(160, 175, "(~1864 множень Fₚ)", size=10, color=MUTED))

    # Додавання: 116
    out.append(rect(65, 205, 190, 45, fill="#d4efdf", stroke=FIELD, rx=4))
    out.append(text(160, 232, "116 додавань P", size=12, bold=True, color=FIELD))

    # Підсумок 1
    out.append(text(160, 280, "Загалом: ~3250 M(Fₚ)", size=12, bold=True, color=INK))
    out.append(text(160, 305, "Базовий рівень (1.0×)", size=11, color=MUTED))

    # Стовпчик 2: wNAF (w = 4, F_p)
    b2_h, _, _ = textbox(410, 80, "Віконний wNAF (w = 4, Fₚ)\nОптимізований класичний", size=12, bold=True, fill=FILL, stroke=LINE, min_w=200)
    out.append(b2_h)

    # Гістограма 2
    # Подвоєння: 233
    out.append(rect(315, 120, 190, 80, fill="#fadbd8", stroke=POS, rx=4))
    out.append(text(410, 155, "233 подвоєння [2]P", size=12, bold=True, color=POS))
    out.append(text(410, 175, "(~1864 множень Fₚ)", size=10, color=MUTED))

    # Додавання: 46
    out.append(rect(315, 205, 190, 25, fill="#d4efdf", stroke=FIELD, rx=4))
    out.append(text(410, 222, "46 додавань P", size=11, bold=True, color=FIELD))

    # Підсумок 2
    out.append(text(410, 280, "Загалом: ~2400 M(Fₚ)", size=12, bold=True, color=INK))
    out.append(text(410, 305, "Прискорення: 1.35×", size=11, color=MUTED))

    # Стовпчик 3: w-TNAF (w = 4, Koblitz F_2^233)
    b3_h, _, _ = textbox(660, 80, "Крива Кобліца w-TNAF (w = 4)\nNIST K-233 (sect233k1)", size=12, bold=True, fill="#edfbf2", stroke=FIELD, min_w=200)
    out.append(b3_h)

    # Гістограма 3
    # Подвоєння: 0 (замінено на 233 зсуви)
    out.append(rect(565, 120, 190, 20, fill="#ebf5fb", stroke=NEG, rx=4))
    out.append(text(660, 134, "0 подвоєнь (233 τ-зсуви)", size=11, bold=True, color=NEG))

    # Додавання: 46
    out.append(rect(565, 145, 190, 25, fill="#d4efdf", stroke=FIELD, rx=4))
    out.append(text(660, 162, "46 додавань P", size=11, bold=True, color=FIELD))

    # Підсумок 3
    out.append(text(660, 280, "Загалом: ~600 M(F₂ᵐ)", size=12, bold=True, color=FIELD))
    out.append(text(660, 305, "Прискорення: 4.0×–5.4×", size=12, bold=True, color=FIELD))

    # Рамка висновку внизу
    b_bot, _, _ = textbox(w / 2, 338, "Криві Кобліца перетворюють обчислювально найважчу операцію (подвоєння точок) на безкоштовні бітові автоморфізми", size=11, fill="#f4f6f8", stroke=MUTED, min_w=780)
    out.append(b_bot)

    out.append("</svg>")
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    figs = [
        ('frobenius-action.svg', build_fig1),
        ('tnaf-scalar-pipeline.svg', build_fig2),
        ('complexity-comparison.svg', build_fig3),
    ]

    for fname, builder in figs:
        fpath = os.path.join(img_dir, fname)
        svg_code = builder()
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(svg_code)
        print("Generated: %s" % fpath)

if __name__ == '__main__':
    main()
