# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = "#eafaf0"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eef4fd"
GREY_FILL  = "#f4f6f8"
HL_FILL    = "#fdf6e3"


# ── Фіг. 1: Двоетапна архітектура методу Квайна–Мак-Класкі ─────────────────────
def fig_qm_pipeline():
    W, H = 840, 420
    p = []

    # Тло блоку Фази 1
    p.append(rect(30, 40, 365, 340, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=10))
    p.append(text(212, 70, "Фаза 1: Генерація простих імплікантів", size=15, color=NEG, bold=True))

    # Кроки Фази 1
    p.append(rect(50, 95, 325, 48, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(212, 116, "Мінтерми функції F та don't-care (d)", size=13, color=INK, bold=True))
    p.append(text(212, 133, "Подання двійковими векторами {0, 1}ⁿ", size=11, color=MUTED))

    p.append(arrow(212, 143, 212, 163, color=LINE, sw=1.5))

    p.append(rect(50, 165, 325, 52, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(212, 185, "Розбиття за вагою Геммінга", size=13, color=INK, bold=True))
    p.append(text(212, 203, "Групи G₀, G₁, …, Gₙ за кількістю одиниць (popcount)", size=11, color=MUTED))

    p.append(arrow(212, 217, 212, 237, color=LINE, sw=1.5))

    p.append(rect(50, 239, 325, 58, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(212, 258, "Каскадне склеювання (Gₖ × Gₖ₊₁)", size=13, color=INK, bold=True))
    p.append(text(212, 275, "Сусідні за 1 біт → прочерк «-» (d_H = 1)", size=11, color=MUTED))
    p.append(text(212, 289, "Ітерація: 1-куби → 2-куби → 4-куби …", size=11, color=MUTED))

    p.append(arrow(212, 297, 212, 317, color=LINE, sw=1.5))

    p.append(rect(50, 319, 325, 45, fill=HL_FILL, stroke=POS, sw=1.5, rx=6))
    p.append(text(212, 338, "Усі несклеєні терми (Prime Implicants)", size=12, color=POS, bold=True))
    p.append(text(212, 354, "Повний набір максимальних склейок функції", size=11, color=MUTED))

    # Стрілка переходу між фазами
    p.append(arrow(395, 210, 443, 210, color=POS, sw=2.5))
    p.append(text(420, 198, "Імпліканти", size=11, color=POS, bold=True))

    # Тло блоку Фази 2
    p.append(rect(445, 40, 365, 340, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=10))
    p.append(text(627, 70, "Фаза 2: Оптимальне покриття мінтермів", size=15, color=FIELD, bold=True))

    # Кроки Фази 2
    p.append(rect(465, 95, 325, 48, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(627, 116, "Таблиця покриття (PI Chart)", size=13, color=INK, bold=True))
    p.append(text(627, 133, "Рядки — прості імпліканти, стовпці — мінтерми F", size=11, color=MUTED))

    p.append(arrow(627, 143, 627, 163, color=LINE, sw=1.5))

    p.append(rect(465, 165, 325, 52, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(627, 185, "Виділення істотних імплікантів (EPI)", size=13, color=INK, bold=True))
    p.append(text(627, 203, "Стовпці з єдиним «X» → неминучі доданки", size=11, color=MUTED))

    p.append(arrow(627, 217, 627, 237, color=LINE, sw=1.5))

    p.append(rect(465, 239, 325, 58, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(627, 258, "Редукція та розв'язання ядра", size=13, color=INK, bold=True))
    p.append(text(627, 275, "Домінування рядків і стовпців", size=11, color=MUTED))
    p.append(text(627, 289, "Циклічне ядро → метод Патріка або розгалуження", size=11, color=MUTED))

    p.append(arrow(627, 297, 627, 317, color=LINE, sw=1.5))

    p.append(rect(465, 319, 325, 45, fill=HL_FILL, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(627, 338, "Мінімальна ДНФ (Exact Minimal SOP)", size=12, color=FIELD, bold=True))
    p.append(text(627, 354, "Найменше число доданків і літер", size=11, color=MUTED))

    render(os.path.join(OUT, "qm-pipeline.svg"), W, H, *p,
           title="Двоетапна структура методу Квайна–Мак-Класкі")


# ── Фіг. 2: Склеювання за вагою Геммінга (Phase 1) ────────────────────────────
def fig_group_merging():
    W, H = 820, 390
    p = []

    # Заголовок
    p.append(text(410, 30, "Групування за кількістю одиничних бітів та склеювання сусідніх груп",
                  size=14, color=INK, bold=True))

    # Стовпчик 1: Початкові мінтерми у групах
    col1_x = 40
    p.append(rect(col1_x, 50, 200, 310, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(col1_x + 100, 75, "Раунд 0: Мінтерми", size=13, color=INK, bold=True))

    # Група 0
    p.append(rect(col1_x + 10, 90, 180, 42, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(col1_x + 20, 110, "G₀ (w=0):", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col1_x + 85, 110, "m0  (0000) ✓", size=11, color=INK, anchor="start"))

    # Група 1
    p.append(rect(col1_x + 10, 140, 180, 68, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(col1_x + 20, 160, "G₁ (w=1):", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col1_x + 85, 160, "m1  (0001) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 178, "m2  (0010) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 196, "m8  (1000) ✓", size=11, color=INK, anchor="start"))

    # Група 2
    p.append(rect(col1_x + 10, 216, 180, 68, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(col1_x + 20, 236, "G₂ (w=2):", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col1_x + 85, 236, "m5  (0101) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 254, "m6  (0110) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 272, "m9  (1001) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 290, "m10 (1010) ✓", size=11, color=INK, anchor="start"))

    # Група 3
    p.append(rect(col1_x + 10, 308, 180, 42, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(col1_x + 20, 328, "G₃ (w=3):", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col1_x + 85, 328, "m7  (0111) ✓", size=11, color=INK, anchor="start"))
    p.append(text(col1_x + 85, 344, "m14 (1110) ✓", size=11, color=INK, anchor="start"))

    # Стрілка між стовпчиками 1 і 2
    p.append(arrow(245, 200, 283, 200, color=LINE, sw=1.8))

    # Стовпчик 2: Склейки 1-го порядку (2-куби з одним '-')
    col2_x = 290
    p.append(rect(col2_x, 50, 240, 310, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(col2_x + 120, 75, "Раунд 1: Склейки (1 прочерк)", size=13, color=INK, bold=True))

    p.append(rect(col2_x + 10, 90, 220, 60, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(col2_x + 15, 110, "G₀ × G₁:", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 110, "(0,1)  000- ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 126, "(0,2)  00-0 ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 142, "(0,8)  -000 ✓", size=11, color=INK, anchor="start"))

    p.append(rect(col2_x + 10, 158, 220, 96, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(col2_x + 15, 178, "G₁ × G₂:", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 178, "(1,5)  0-01 ★ PI", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 194, "(1,9)  -001 ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 210, "(2,6)  0-10 ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 226, "(2,10) -010 ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 242, "(8,9)  100- ✓", size=11, color=INK, anchor="start"))

    p.append(rect(col2_x + 10, 262, 220, 88, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(col2_x + 15, 282, "G₂ × G₃:", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 282, "(5,7)   01-1 ★ PI", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 298, "(6,7)   011- ★ PI", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(col2_x + 80, 314, "(6,14)  -110 ✓", size=11, color=INK, anchor="start"))
    p.append(text(col2_x + 80, 330, "(10,14) 1-10 ✓", size=11, color=INK, anchor="start"))

    # Стрілка між стовпчиками 2 і 3
    p.append(arrow(535, 200, 573, 200, color=LINE, sw=1.8))

    # Стовпчик 3: Склейки 2-го порядку (4-куби з двома '-')
    col3_x = 580
    p.append(rect(col3_x, 50, 200, 310, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(col3_x + 100, 75, "Раунд 2: Прості імпліканти", size=13, color=FIELD, bold=True))

    p.append(rect(col3_x + 10, 95, 180, 75, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(col3_x + 15, 115, "(0,1,8,9)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(col3_x + 15, 135, "Двійковий: -00-", size=11, color=MUTED, anchor="start"))
    p.append(text(col3_x + 15, 155, "Вираз: B̄·C̄ ★ PI", size=12, color=POS, bold=True, anchor="start"))

    p.append(rect(col3_x + 10, 180, 180, 75, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(col3_x + 15, 200, "(0,2,8,10)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(col3_x + 15, 220, "Двійковий: -0-0", size=11, color=MUTED, anchor="start"))
    p.append(text(col3_x + 15, 240, "Вираз: B̄·D̄ ★ PI", size=12, color=POS, bold=True, anchor="start"))

    p.append(rect(col3_x + 10, 265, 180, 75, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(col3_x + 15, 285, "(2,6,10,14)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(col3_x + 15, 305, "Двійковий: --10", size=11, color=MUTED, anchor="start"))
    p.append(text(col3_x + 15, 325, "Вираз: C·D̄ ★ PI", size=12, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "group-merging.svg"), W, H, *p,
           title="Покрокове склеювання за групами ваги Геммінга")


# ── Фіг. 3: Таблиця покриття простих імплікантів (Phase 2) ────────────────────
def fig_pi_chart_reduction():
    W, H = 840, 380
    p = []

    # Таблиця
    ox = 180
    oy = 60
    cw = 58
    rh = 38
    minterms = [0, 1, 2, 5, 6, 7, 8, 9, 10, 14]
    pi_labels = [
        ("P1: B̄·C̄ (0,1,8,9)", [0, 1, 8, 9], True, FIELD),
        ("P2: B̄·D̄ (0,2,8,10)", [0, 2, 8, 10], False, MUTED),
        ("P3: C·D̄ (2,6,10,14)", [2, 6, 10, 14], True, FIELD),
        ("P4: Ā·C̄·D (1,5)", [1, 5], False, MUTED),
        ("P5: Ā·B·D (5,7)", [5, 7], True, POS),
        ("P6: Ā·B·C (6,7)", [6, 7], False, MUTED),
    ]

    # Заголовок
    p.append(text(W / 2, 30, "Таблиця покриття: виявлення істотних імплікантів та редукція",
                  size=14, color=INK, bold=True))

    # Стовпці (мінтерми)
    for j, m in enumerate(minterms):
        x = ox + j * cw
        # Підсвітка стовпців з єдиним X (9 та 14)
        col_fill = HL_FILL if m in (9, 14) else BG
        p.append(rect(x, oy, cw, rh, fill=col_fill, stroke=LINE, sw=1.2, rx=0))
        p.append(text(x + cw / 2, oy + 24, "m" + str(m), size=12, color=NEG if m in (9, 14) else INK, bold=True))
        if m in (9, 14):
            p.append(text(x + cw / 2, oy - 8, "★ 1-X", size=10, color=POS, bold=True))

    # Рядки
    for i, (name, covered, is_chosen, col) in enumerate(pi_labels):
        y = oy + (i + 1) * rh
        # Заголовок рядка
        row_fill = GREEN_FILL if is_chosen and col == FIELD else (RED_FILL if is_chosen else BG)
        p.append(rect(30, y, ox - 30, rh, fill=row_fill, stroke=LINE, sw=1.2, rx=0))
        p.append(text(40, y + 23, name, size=11, color=col if is_chosen else INK, bold=is_chosen, anchor="start"))

        # Клітини покриття
        for j, m in enumerate(minterms):
            x = ox + j * cw
            c_fill = row_fill if is_chosen else (HL_FILL if m in (9, 14) else BG)
            p.append(rect(x, y, cw, rh, fill=c_fill, stroke=LINE, sw=1, rx=0))
            if m in covered:
                # Позначка X
                x_col = col if is_chosen else INK
                p.append(text(x + cw / 2, y + 25, "✕", size=16, color=x_col, bold=True))

    # Підсумкова легенда
    ly = oy + 7 * rh + 20
    p.append(rect(30, ly, W - 60, 48, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(45, ly + 20, "1. Стовпці m9 (тільки P1) та m14 (тільки P3) виявляють Істотні Прості Імпліканти: P1 та P3 (виділено зеленим).",
                  size=11, color=INK, anchor="start"))
    p.append(text(45, ly + 36, "2. P1 і P3 накривають {0,1,2,6,8,9,10,14}. Для решти {5,7} рядок P5 накриває обидва, домінуючи над P4 та P6 → F = P1 + P3 + P5.",
                  size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "pi-chart-reduction.svg"), W, H, *p,
           title="Таблиця покриття: пошук істотних імплікантів та домінування")


# ── Фіг. 4: Циклічне ядро та розв'язання за методом Патріка ──────────────────
def fig_cyclic_core_petrick():
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 28, "Циклічна таблиця покриття (немає стовпців з одним «X») та метод Патріка",
                  size=14, color=INK, bold=True))

    # Ліва панель: Циклічна таблиця 4×4 або 6×6
    lx, ly = 30, 55
    cw, rh = 54, 34
    p.append(rect(lx, ly, 380, 310, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(lx + 190, ly + 24, "Циклічна матриця покриття (Core)", size=13, color=NEG, bold=True))

    c_minterms = ["m0", "m1", "m2", "m3", "m4", "m5"]
    c_pis = [
        ("P₁", [0, 1]),
        ("P₂", [1, 2]),
        ("P₃", [2, 3]),
        ("P₄", [3, 4]),
        ("P₅", [4, 5]),
        ("P₆", [5, 0])
    ]

    tox = lx + 50
    toy = ly + 40
    for j, m in enumerate(c_minterms):
        p.append(rect(tox + j * cw, toy, cw, rh, fill=BG, stroke=LINE, sw=1, rx=0))
        p.append(text(tox + j * cw + cw / 2, toy + 22, m, size=11, color=INK, bold=True))

    for i, (name, cov) in enumerate(c_pis):
        y = toy + (i + 1) * rh
        p.append(rect(tox - 40, y, 40, rh, fill=BG, stroke=LINE, sw=1, rx=0))
        p.append(text(tox - 20, y + 22, name, size=12, color=NEG, bold=True))
        for j in range(len(c_minterms)):
            x = tox + j * cw
            p.append(rect(x, y, cw, rh, fill=BG, stroke=LINE, sw=1, rx=0))
            if j in cov:
                p.append(text(x + cw / 2, y + 23, "✕", size=15, color=NEG, bold=True))

    p.append(text(lx + 190, ly + 295, "Кожен стовпець має рівно 2 позначки «X» — немає EPI!",
                  size=11, color=POS, bold=True))

    # Права панель: Алгебраїчний вивід за методом Патріка
    rx, ry = 430, 55
    p.append(rect(rx, ry, 380, 310, fill=GREEN_FILL, stroke=FIELD, sw=1.2, rx=8))
    p.append(text(rx + 190, ry + 24, "Алгебраїчне розкриття за Патріком", size=13, color=FIELD, bold=True))

    # Текстовий блок кроків
    p.append(rect(rx + 15, ry + 40, 350, 60, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(rx + 25, ry + 60, "1. Умова покриття кожного стовпця (КНФ):", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 78, "P = (P₁+P₆)(P₁+P₂)(P₂+P₃)(P₃+P₄)(P₄+P₅)(P₅+P₆)", size=10, color=NEG, anchor="start"))

    p.append(rect(rx + 15, ry + 110, 350, 75, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(rx + 25, ry + 130, "2. Розкриття дужок і поглинання (X + XY = X):", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 148, "(P₁+P₆)(P₁+P₂) = P₁ + P₂·P₆", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 25, ry + 165, "(P₂+P₃)(P₃+P₄) = P₃ + P₂·P₄", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 25, ry + 180, "(P₄+P₅)(P₅+P₆) = P₅ + P₄·P₆", size=10, color=MUTED, anchor="start"))

    p.append(rect(rx + 15, ry + 195, 350, 95, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(rx + 25, ry + 215, "3. ДНФ усіх можливих мінімальних покриттів:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 235, "P = P₁·P₃·P₅ + P₂·P₄·P₆ + (доданки з 4+ імплікантів)", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 258, "Два рівноцінні мінімуми по 3 доданки:", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 25, ry + 276, "• Варіант A: P₁ + P₃ + P₅   • Варіант B: P₂ + P₄ + P₆", size=11, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "cyclic-core-petrick.svg"), W, H, *p,
           title="Циклічне ядро та розв'язання за методом Патріка")


if __name__ == "__main__":
    fig_qm_pipeline()
    fig_group_merging()
    fig_pi_chart_reduction()
    fig_cyclic_core_petrick()
    print("All figures generated successfully.")
