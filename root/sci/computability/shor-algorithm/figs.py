# -*- coding: utf-8 -*-
"""Фігури для теми «Алгоритм Шора»
(book/algorithms/complexity-computability/shor-algorithm)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#ebf5fb", "#2980b9"
GREEN_F, GREEN_S = "#e9f7ef", "#27ae60"
RED_F, RED_S = "#fdecea", "#c0392b"
AMBER_F, AMBER_S = "#fef9e7", "#d35400"
PURPLE_F, PURPLE_S = "#f4ecf7", "#8e44ad"
GRAY_F, GRAY_S = "#f8f9fa", "#7f8c8d"


def fig_shor_circuit_architecture():
    """Повна квантова схема алгоритму Шора з класичним контуром пост-обробки."""
    W, H = 1000, 520
    frags = []

    # Загальна рамка
    frags.append(rect(10, 10, 980, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Секція квантового регістра 1 (Оцінка фази / Період)
    frags.append(rect(30, 40, 940, 200, fill="#f8fafc", stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(200, 65, "Регістр 1: 2n кубітів (стан адреси/входу)", size=13, bold=True, color=BLUE_S))

    # Лінії 1-го регістра
    frags.append(line(60, 110, 860, 110, color=LINE, sw=1.5))
    frags.append(line(60, 150, 860, 150, color=LINE, sw=1.5))
    frags.append(line(60, 190, 860, 190, color=LINE, sw=1.5))

    # Вхідний стан регістра 1
    frags.append(textbox(80, 110, "|0⟩", size=12, bold=True, fill="#ffffff", stroke=GRAY_S, sw=1, pad=3)[0])
    frags.append(textbox(80, 150, "|0⟩", size=12, bold=True, fill="#ffffff", stroke=GRAY_S, sw=1, pad=3)[0])
    frags.append(textbox(80, 190, "|0⟩", size=12, bold=True, fill="#ffffff", stroke=GRAY_S, sw=1, pad=3)[0])

    # Блок перетворень Адамара H
    frags.append(rect(130, 95, 45, 110, rx=4, fill=AMBER_F, stroke=AMBER_S, sw=1.5))
    frags.append(mtext(152, 150, ["H", "⊗2n"], size=12, bold=True, color=AMBER_S))

    # Керуючі зв'язки для модульного піднесення
    frags.append(circle(250, 110, 4.5, fill=LINE, stroke=LINE, sw=1))
    frags.append(line(250, 110, 250, 310, color=LINE, sw=1.5))

    frags.append(circle(360, 150, 4.5, fill=LINE, stroke=LINE, sw=1))
    frags.append(line(360, 150, 360, 310, color=LINE, sw=1.5))

    frags.append(circle(490, 190, 4.5, fill=LINE, stroke=LINE, sw=1))
    frags.append(line(490, 190, 490, 310, color=LINE, sw=1.5))

    # Блок оберненого квантового перетворення Фур'є QFT†
    frags.append(rect(570, 95, 80, 110, rx=6, fill=PURPLE_F, stroke=PURPLE_S, sw=2))
    frags.append(mtext(610, 145, ["QFT †", "Обернене", "Фур'є"], size=11, bold=True, color=PURPLE_S))

    # Блоки вимірювання регістра 1
    for y_pos in [110, 150, 190]:
        frags.append(rect(690, y_pos - 14, 40, 28, rx=4, fill="#fdedec", stroke=RED_S, sw=1.5))
        frags.append(mtext(710, y_pos + 4, ["M"], size=11, bold=True, color=RED_S))

    frags.append(arrow(735, 150, 780, 150, color=RED_S, sw=2))
    frags.append(textbox(855, 150, "Вихід: ціле y\n(фаза y/2²ⁿ ≈ s/r)", size=11, bold=True,
                         fill=RED_F, stroke=RED_S, sw=1.5, pad=5)[0])

    # Секція квантового регістра 2 (Модульне піднесення)
    frags.append(rect(30, 260, 940, 110, fill="#f8fafc", stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(200, 285, "Регістр 2: n кубітів (обчислення aˣ mod N)", size=12, bold=True, color=GREEN_S))

    frags.append(line(60, 330, 860, 330, color=LINE, sw=1.5))
    frags.append(textbox(80, 330, "|1⟩", size=12, bold=True, fill="#ffffff", stroke=GRAY_S, sw=1, pad=3)[0])

    # Вентилі модульного множення
    frags.append(rect(215, 305, 70, 48, rx=4, fill=GREEN_F, stroke=GREEN_S, sw=1.5))
    frags.append(mtext(250, 333, ["× a²⁰\nmod N"], size=10, bold=True, color=GREEN_S))

    frags.append(rect(325, 305, 70, 48, rx=4, fill=GREEN_F, stroke=GREEN_S, sw=1.5))
    frags.append(mtext(360, 333, ["× a²¹\nmod N"], size=10, bold=True, color=GREEN_S))

    frags.append(mtext(430, 330, ["· · ·"], size=16, bold=True, color=LINE))

    frags.append(rect(455, 305, 70, 48, rx=4, fill=GREEN_F, stroke=GREEN_S, sw=1.5))
    frags.append(mtext(490, 333, ["× a²²ⁿ⁻¹\nmod N"], size=10, bold=True, color=GREEN_S))

    # Стан заплутаності між регістрами
    frags.append(textbox(730, 330, "Заплутаний стан: ∑ |x⟩|aˣ mod N⟩\n(колапс у гребінку кроку r)",
                         size=11, fill="#ffffff", stroke=GREEN_S, sw=1.2, pad=5)[0])

    # Класична пост-обробка (нижня смуга)
    frags.append(rect(30, 390, 940, 95, fill="#f8fafc", stroke=GRAY_S, sw=1.5, rx=6))
    frags.append(text(120, 415, "Класичний процесор (Post-processing)", size=12, bold=True, color="#334155"))

    frags.append(textbox(230, 450, "Ланцюгові дроби (CFE)\nРозклад y/2²ⁿ → s/r", size=11, bold=True,
                         fill=BLUE_F, stroke=BLUE_S, sw=1.5, pad=5)[0])

    frags.append(arrow(345, 450, 385, 450, color=LINE, sw=1.5))

    frags.append(textbox(510, 450, "Тест періоду r:\naʳ ≡ 1 (mod N)", size=11, bold=True,
                         fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, pad=5)[0])

    frags.append(arrow(600, 450, 640, 450, color=LINE, sw=1.5))

    frags.append(textbox(745, 450, "Алгоритм Евкліда:\nНСД(a^(r/2) ± 1, N)", size=11, bold=True,
                         fill=AMBER_F, stroke=AMBER_S, sw=1.5, pad=5)[0])

    frags.append(arrow(850, 450, 885, 450, color=LINE, sw=1.5))

    frags.append(textbox(925, 450, "Множники\np, q", size=11, bold=True,
                         fill=GREEN_F, stroke=GREEN_S, sw=2, pad=5)[0])

    render(os.path.join(IMG, "shor-circuit-architecture.svg"), W, H, *frags,
           title="Квантова схема алгоритму Шора")


def fig_fourier_interference_comb():
    """Перетворення періодичного стану в часовій області на гострі піки Фур'є."""
    W, H = 960, 480
    frags = []

    frags.append(rect(10, 10, 940, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Верхній графік: До QFT (Гребінка значень)
    frags.append(text(260, 40, "Стан регістра 1 ДО QFT (просторовий базис |x⟩):", size=13, bold=True, color=BLUE_S))

    ox1, oy1 = 70, 180
    frags.append(arrow(ox1, oy1, 880, oy1, color=LINE, sw=1.8))
    frags.append(arrow(ox1, oy1, ox1, 65, color=LINE, sw=1.8))
    frags.append(mtext(895, oy1 + 4, ["x"], size=13, bold=True))
    frags.append(mtext(ox1 + 10, 55, ["Амплітуда |ψ(x)|"], size=11, bold=True))

    # Гребінка імпульсів з кроком r
    x_coords = [130, 230, 330, 430, 530, 630, 730, 830]
    for i, xc in enumerate(x_coords):
        frags.append(line(xc, oy1, xc, 95, color=BLUE_S, sw=2.5))
        frags.append(circle(xc, 95, 4, fill=BLUE_S, stroke=BLUE_S, sw=1))
        label = f"x₀" if i == 0 else f"x₀+{i}r"
        frags.append(mtext(xc, oy1 + 18, [label], size=10, bold=True, color=BLUE_S))

    # Стрілка періоду r
    frags.append(line(130, 85, 230, 85, color=AMBER_S, sw=1.8))
    frags.append(line(130, 80, 130, 90, color=AMBER_S, sw=1.8))
    frags.append(line(230, 80, 230, 90, color=AMBER_S, sw=1.8))
    frags.append(mtext(180, 75, ["період r"], size=11, bold=True, color=AMBER_S))

    # Перехід QFT†
    frags.append(textbox(480, 225, "Квантове перетворення Фур'є QFT† (Конструктивна інтерференція)",
                         size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, pad=5)[0])
    frags.append(arrow(480, 240, 480, 265, color=PURPLE_S, sw=2.2))

    # Нижній графік: Після QFT (Частотний базис |y⟩)
    ox2, oy2 = 70, 410
    frags.append(arrow(ox2, oy2, 880, oy2, color=LINE, sw=1.8))
    frags.append(arrow(ox2, oy2, ox2, 295, color=LINE, sw=1.8))
    frags.append(mtext(895, oy2 + 4, ["y"], size=13, bold=True))
    frags.append(mtext(ox2 + 15, 285, ["Імовірність |⟨y|ψ⟩|²"], size=11, bold=True))

    # Піки Фур'є в точках s * Q / r
    y_coords = [70, 220, 370, 520, 670, 820]
    s_labels = ["0", "Q/r", "2Q/r", "3Q/r", "4Q/r", "(r-1)Q/r"]
    for i, yc in enumerate(y_coords):
        frags.append(line(yc, oy2, yc, 320, color=GREEN_S, sw=3))
        frags.append(circle(yc, 320, 4, fill=GREEN_S, stroke=GREEN_S, sw=1))
        frags.append(mtext(yc, oy2 + 18, [s_labels[i]], size=10, bold=True, color=GREEN_S))

    # Пояснення деструктивної інтерференції
    frags.append(textbox(770, 335, "Між піками фази гасять\nодна одну до нуля", size=10, bold=True,
                         fill=RED_F, stroke=RED_S, sw=1, pad=4)[0])

    render(os.path.join(IMG, "fourier-interference-comb.svg"), W, H, *frags,
           title="Конструктивна інтерференція QFT")


def fig_factoring_to_period_reduction():
    """Блок-схема редукції факторизації цілих чисел до пошуку порядку елемента."""
    W, H = 960, 540
    frags = []

    frags.append(rect(10, 10, 940, 520, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Вхідне число N
    frags.append(textbox(480, 50, "Вхід: непарне складене число N (наприклад, модуль RSA N = p · q)",
                         size=12, bold=True, fill=GRAY_F, stroke=GRAY_S, sw=1.5, pad=6)[0])
    frags.append(arrow(480, 72, 480, 100, color=LINE, sw=1.8))

    # Крок 1: Вибір a
    frags.append(textbox(480, 120, "1. Обрати випадкове число a ∈ {2, 3, ..., N - 1}",
                         size=12, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=1.5, pad=5)[0])
    frags.append(arrow(480, 140, 480, 170, color=LINE, sw=1.8))

    # Перевірка НСД(a, N)
    frags.append(textbox(480, 190, "Перевірити d = НСД(a, N) класичним алгоритмом Евкліда",
                         size=11, fill="#ffffff", stroke=LINE, sw=1.2, pad=5)[0])

    # Гілка d > 1
    frags.append(line(670, 190, 830, 190, color=GREEN_S, sw=1.8))
    frags.append(arrow(830, 190, 830, 310, color=GREEN_S, sw=1.8))
    frags.append(textbox(830, 350, "Якщо d > 1:\nВипадковий успіх!\nДільник знайдено",
                         size=11, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=1.5, pad=5)[0])
    frags.append(arrow(830, 390, 830, 450, color=GREEN_S, sw=1.8))

    # Гілка d == 1 -> Квантовий пошук періоду
    frags.append(arrow(480, 212, 480, 245, color=LINE, sw=1.8))
    frags.append(textbox(480, 275, "2. Квантовий процесор (QPU):\nЗнайти найменший період r функції f(x) = aˣ mod N",
                         size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=2, pad=6)[0])

    frags.append(arrow(480, 305, 480, 335, color=LINE, sw=1.8))

    # Перевірка умов періоду
    frags.append(textbox(480, 365, "3. Перевірка придатності r:\nЧи r парне (r mod 2 == 0) ТА a^(r/2) ≢ -1 (mod N)?",
                         size=11, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=1.5, pad=5)[0])

    # Невдача умов -> повторний вибір a
    frags.append(line(240, 365, 80, 365, color=RED_S, sw=1.8))
    frags.append(line(80, 365, 80, 120, color=RED_S, sw=1.8))
    frags.append(arrow(80, 120, 280, 120, color=RED_S, sw=1.8))
    frags.append(textbox(130, 240, "НІ (імовірність < 1/2):\nОбрати інше a",
                         size=10, bold=True, fill=RED_F, stroke=RED_S, sw=1.5, pad=4)[0])

    # Успіх -> Обчислення дільників
    frags.append(arrow(480, 395, 480, 440, color=GREEN_S, sw=2))
    frags.append(textbox(480, 475, "ТАК! Обчислити нетривіальні дільники:\np = НСД(a^(r/2) - 1, N)   та   q = НСД(a^(r/2) + 1, N)",
                         size=12, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=2, pad=7)[0])

    # З'єднання d > 1 з кінцевим виходом
    frags.append(line(830, 450, 700, 475, color=GREEN_S, sw=1.5))

    render(os.path.join(IMG, "factoring-to-period-reduction.svg"), W, H, *frags,
           title="Редукція факторизації до пошуку періоду")


def fig_continued_fractions_phase():
    """Відновлення періоду з фазової оцінки методом неперервних дробів."""
    W, H = 960, 440
    frags = []

    frags.append(rect(20, 20, 920, 400, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Виміряне число y
    frags.append(textbox(170, 70, "Виміряне квантове значення y\n(розрядність 2n біт, Q = 2²ⁿ)",
                         size=12, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=1.5, pad=6)[0])

    frags.append(arrow(295, 70, 355, 70, color=LINE, sw=1.8))

    frags.append(textbox(500, 70, "Фазовий дріб θ = y / Q ∈ [0, 1)\nθ ≈ s / r з похибкою |θ - s/r| < 1 / (2Q)",
                         size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, pad=6)[0])

    frags.append(arrow(500, 100, 500, 135, color=LINE, sw=1.8))

    # Розклад у неперервний дріб
    frags.append(textbox(500, 165, "Розклад у неперервний дріб (Continued Fraction Expansion):\nθ = [a₀; a₁, a₂, a₃, ..., aₘ] = a₀ + 1/(a₁ + 1/(a₂ + ...))",
                         size=12, fill=GRAY_F, stroke=GRAY_S, sw=1.5, pad=8)[0])

    frags.append(arrow(500, 200, 500, 235, color=LINE, sw=1.8))

    # Ланцюжок підхідних дробів
    frags.append(textbox(180, 275, "Підхідні дроби pₖ / qₖ:\np₀/q₀, p₁/q₁, p₂/q₂, ...",
                         size=12, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=1.5, pad=6)[0])

    frags.append(arrow(310, 275, 370, 275, color=LINE, sw=1.8))

    frags.append(textbox(560, 275, "Теорема Лежандра гарантує:\nЯкщо |θ - s/r| < 1/(2r²), то s/r є одним із підхідних дробів pₖ/qₖ",
                         size=12, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=1.5, pad=6)[0])

    frags.append(arrow(560, 310, 560, 345, color=LINE, sw=1.8))

    # Перевірка кандидатів знаменників
    frags.append(textbox(560, 375, "Кандидат у період: r' = qₖ. Перевірка: чи a^(qₖ) ≡ 1 (mod N)?\nЯкщо так — період r знайдено!",
                         size=12, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=2, pad=8)[0])

    render(os.path.join(IMG, "continued-fractions-phase.svg"), W, H, *frags,
           title="Відновлення періоду неперервними дробами")


if __name__ == "__main__":
    fig_shor_circuit_architecture()
    fig_fourier_interference_comb()
    fig_factoring_to_period_reduction()
    fig_continued_fractions_phase()
    print("Всі 4 фігури успішно згенеровано!")
