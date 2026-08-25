# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"
PURPLE_F = "#f3e8fa"
YELLOW_F = "#fffde6"

# ── 1. abundance-asymmetry: Асиметрія надлишковості та недостатності в дружній парі ──
def fig_abundance_asymmetry():
    W, H = 1000, 420
    elements = []

    # Заголовок / концепція
    elements.append(text(W / 2, 45, "Асиметрія дружньої пари (220, 284) відносно межі досконалості", size=17, color=INK, bold=True))

    # Панель 1: Менше число 220 (надлишкове)
    elements.append(fitbox(50, 85, 410, 230, "", fill=BLUE_F, stroke=NEG, sw=2, rx=8))
    elements.append(text(255, 115, "a = 220  (менше число)", size=16, color=NEG, bold=True))
    elements.append(text(255, 145, "Сума всіх дільників: σ(220) = 504", size=14, color=INK))
    elements.append(text(255, 175, "Відношення збагачення: σ(220) / 220 = 2.2909 > 2", size=14, color=INK, bold=True))
    elements.append(text(255, 205, "Сума власних дільників s(220) = 284", size=14, color=INK))
    elements.append(fitbox(80, 235, 350, 50, "НАДЛИШКОВЕ (abundant)\ns(220) = 284 > 220", size=15, fill=FILL, stroke=NEG, sw=2, bold=True, color=NEG))

    # Вертикальна вісь межі досконалості
    elements.append(line(500, 75, 500, 325, color=FIELD, sw=2.5, dash="6,6"))
    elements.append(fitbox(425, 335, 150, 40, "Межа: σ(n)/n = 2\n(досконале число)", size=13, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=FIELD))

    # Панель 2: Більше число 284 (недостатнє)
    elements.append(fitbox(540, 85, 410, 230, "", fill=RED_F, stroke=POS, sw=2, rx=8))
    elements.append(text(745, 115, "b = 284  (більше число)", size=16, color=POS, bold=True))
    elements.append(text(745, 145, "Сума всіх дільників: σ(284) = 504", size=14, color=INK))
    elements.append(text(745, 175, "Відношення збагачення: σ(284) / 284 = 1.7746 < 2", size=14, color=INK, bold=True))
    elements.append(text(745, 205, "Сума власних дільників s(284) = 220", size=14, color=INK))
    elements.append(fitbox(570, 235, 350, 50, "НЕДОСТАТНЄ (deficient)\ns(284) = 220 < 284", size=15, fill=FILL, stroke=POS, sw=2, bold=True, color=POS))

    # Нижня узагальнювальна рамка
    elements.append(fitbox(50, 382, 900, 32, "У будь-якій дружній парі a < b: менше число a завжди надлишкове, а більше b — завжди недостатнє", size=13.5, fill=YELLOW_F, stroke=MUTED, sw=1.5, bold=True, color=INK))

    return render(os.path.join(OUT, "abundance-asymmetry.svg"), W, H, *elements,
                  title="Асиметрія надлишковості та недостатності в дружній парі")

# ── 2. thabit-generator: Схема генератора Сабіта ibn Кюрри ──
def fig_thabit_generator():
    W, H = 1000, 480
    elements = []

    elements.append(text(W / 2, 40, "Генератор дружніх пар Сабіта ibn Кюрри для n = 2", size=17, color=INK, bold=True))

    # Вхідний параметр n
    elements.append(fitbox(410, 65, 180, 50, "Вхід: n = 2", size=16, fill=BLUE_F, stroke=NEG, sw=2.2, bold=True, color=INK))

    # Стрілки розгалуження
    elements.append(arrow(430, 115, 200, 160, color=MUTED, sw=2))
    elements.append(arrow(500, 115, 500, 160, color=MUTED, sw=2))
    elements.append(arrow(570, 115, 800, 160, color=MUTED, sw=2))

    # Три обчислення простих чисел
    elements.append(fitbox(60, 165, 280, 80, "p = 3·2²⁻¹ − 1 = 5\n(просте число ✓)", size=14, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=INK))
    elements.append(fitbox(360, 165, 280, 80, "q = 3·2² − 1 = 11\n(просте число ✓)", size=14, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=INK))
    elements.append(fitbox(660, 165, 280, 80, "r = 9·2²⁺²⁻¹ − 1 = 71\n(просте число ✓)", size=14, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=INK))

    # Збирання чисел a та b
    elements.append(arrow(200, 245, 270, 310, color=MUTED, sw=2))
    elements.append(arrow(500, 245, 270, 310, color=MUTED, sw=2))
    elements.append(arrow(800, 245, 730, 310, color=MUTED, sw=2))

    elements.append(fitbox(120, 315, 300, 75, "a = 2² · p · q\n= 4 · 5 · 11 = 220", size=15, fill=PURPLE_F, stroke="#7e22ce", sw=2.2, bold=True, color=INK))
    elements.append(fitbox(580, 315, 300, 75, "b = 2² · r\n= 4 · 71 = 284", size=15, fill=PURPLE_F, stroke="#7e22ce", sw=2.2, bold=True, color=INK))

    # Зв'язок дружньої пари
    elements.append(arrow(425, 345, 575, 345, color=NEG, sw=2.5))
    elements.append(arrow(575, 360, 425, 360, color=NEG, sw=2.5))
    elements.append(text(500, 332, "s(220) = 284", size=12.5, color=NEG, bold=True))
    elements.append(text(500, 375, "s(284) = 220", size=12.5, color=NEG, bold=True))

    # Нижня примітка
    elements.append(fitbox(60, 415, 880, 45, "Якщо p, q, r — прості, то числа a = 2ⁿ·p·q та b = 2ⁿ·r гарантовано утворюють дружню пару", size=13.5, fill=FILL, stroke=MUTED, sw=1.5))

    return render(os.path.join(OUT, "thabit-generator.svg"), W, H, *elements,
                  title="Генератор дружніх пар Сабіта ibn Кюрри")

# ── 3. aliquot-trajectories: Траєкторії аліквотних послідовностей ──
def fig_aliquot_trajectories():
    W, H = 1020, 470
    elements = []

    elements.append(text(W / 2, 40, "Долі чисел під дією оператора s(n) = σ(n) − n", size=17, color=INK, bold=True))

    # Початковий вузол
    elements.append(fitbox(410, 65, 200, 45, "Початкове число n", size=15, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))
    elements.append(arrow(510, 110, 510, 150, color=MUTED, sw=2))

    # 4 типи траєкторій (панелі)
    # 1. Завершення в 1
    elements.append(fitbox(40, 155, 210, 240, "", fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    elements.append(text(145, 180, "Згасання до 1", size=15, color=NEG, bold=True))
    elements.append(text(145, 210, "12 → 16 → 15", size=13.5, color=INK))
    elements.append(text(145, 235, "→ 9 → 4 → 3", size=13.5, color=INK))
    elements.append(text(145, 260, "→ 1 → 0", size=14, color=NEG, bold=True))
    elements.append(fitbox(55, 300, 180, 80, "Найпоширеніша доля:\nпослідовність обривається на 0", size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    # 2. 1-цикл (Досконале)
    elements.append(fitbox(280, 155, 210, 240, "", fill=GREEN_F, stroke=FIELD, sw=1.5, rx=6))
    elements.append(text(385, 180, "1-цикл (Досконале)", size=15, color=FIELD, bold=True))
    elements.append(text(385, 220, "6 ↺ 6", size=18, color=FIELD, bold=True))
    elements.append(text(385, 255, "s(6) = 6", size=14, color=INK))
    elements.append(fitbox(295, 300, 180, 80, "Нерухома точка:\nчисло дорівнює сумі своїх дільників", size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    # 3. 2-цикл (Дружні числа)
    elements.append(fitbox(520, 155, 220, 240, "", fill=PURPLE_F, stroke="#7e22ce", sw=2, rx=6))
    elements.append(text(630, 180, "2-цикл (Дружні числа)", size=15, color="#7e22ce", bold=True))
    elements.append(text(630, 220, "220 ⇄ 284", size=18, color="#7e22ce", bold=True))
    elements.append(text(630, 255, "s(220)=284, s(284)=220", size=13, color=INK))
    elements.append(fitbox(535, 300, 190, 80, "Пара взаємного виклику:\nдва числа живлять одне одне", size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    # 4. k-цикл (Компанійські числа)
    elements.append(fitbox(760, 155, 220, 240, "", fill=YELLOW_F, stroke=POS, sw=1.5, rx=6))
    elements.append(text(870, 180, "k-цикл (Компанійські)", size=15, color=POS, bold=True))
    elements.append(text(870, 210, "12496 → 14288", size=13, color=INK))
    elements.append(text(870, 235, "→ 15472 → 14536", size=13, color=INK))
    elements.append(text(870, 260, "→ 14264 ↺ 12496", size=13, color=POS, bold=True))
    elements.append(fitbox(775, 300, 190, 80, "Замкнене коло з k ≥ 3:\nдовші орбіти дільників", size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    # Загальний висновок
    elements.append(fitbox(40, 410, 940, 45, "Гіпотеза Каталана–Діксона: кожна аліквотна послідовність або завершується на 1, або заходить у 1-, 2- чи k-цикл", size=13.5, fill=FILL, stroke=MUTED, sw=1.5, bold=True))

    return render(os.path.join(OUT, "aliquot-trajectories.svg"), W, H, *elements,
                  title="Траєкторії аліквотних послідовностей")

if __name__ == "__main__":
    fig_abundance_asymmetry()
    fig_thabit_generator()
    fig_aliquot_trajectories()
    print("Generated 3 figures in img/")
