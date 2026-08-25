# -*- coding: utf-8 -*-
"""Фігури для статті «Garbage collection у Flash-сховищах»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f5ee"
GRAY_FILL = "#eceff1"
HOT_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"

def cell(x, y, w, h, label, kind="free", size=11):
    styles = {
        "valid": (GREEN_FILL, FIELD, INK),
        "invalid": (GRAY_FILL, MUTED, MUTED),
        "free": (BG, LINE, MUTED),
        "data": (FILL, LINE, INK),
        "hot": (HOT_FILL, POS, INK),
        "cold": (BLUE_FILL, NEG, INK),
    }
    fill, stroke, color = styles.get(kind, (FILL, LINE, INK))
    return fitbox(x, y, w, h, label, size=size, pad=6, fill=fill, stroke=stroke, color=color)

# ───────────────────────────────────────────────────────────────────────────
# Фігура 1 — Цикл збирання сміття у Flash
# ───────────────────────────────────────────────────────────────────────────
def fig_gc_lifecycle():
    W, H = 920, 460
    f = []

    f.append(textbox(150, 40, "Крок 1: Блок-жертва", size=13, pad=16, bold=True)[0])
    f.append(textbox(460, 40, "Крок 2: Евакуація чинних сторінок", size=13, pad=18, bold=True)[0])
    f.append(textbox(770, 40, "Крок 3 та 4: Стирання й Пул", size=13, pad=16, bold=True)[0])

    # Блок 1 (Жертва)
    f.append(fitbox(70, 80, 160, 300, "", fill=FILL, stroke=LINE))
    f.append(text(150, 105, "Блок #12 (Жертва)", size=12, bold=True))
    pages1 = [
        ("P0: Чинна (LBA 5)", "valid"),
        ("P1: Застаріла ✗", "invalid"),
        ("P2: Застаріла ✗", "invalid"),
        ("P3: Чинна (LBA 8)", "valid"),
        ("P4: Застаріла ✗", "invalid"),
        ("P5: Застаріла ✗", "invalid"),
    ]
    for i, (lab, k) in enumerate(pages1):
        f.append(cell(80, 120 + i * 42, 140, 36, lab, k, size=10))

    # Стрілка міграції
    f.append(arrow(240, 140, 375, 140, color=POS, sw=2))
    f.append(text(307, 115, "Копіювання P0", size=10, color=POS, bold=True))

    f.append(arrow(240, 266, 375, 224, color=POS, sw=2))
    f.append(text(307, 200, "Копіювання P3", size=10, color=POS, bold=True))

    # Блок 2 (Новий активний блок)
    f.append(fitbox(380, 80, 160, 300, "", fill=FILL, stroke=LINE))
    f.append(text(460, 105, "Блок #45 (Активний)", size=12, bold=True))
    pages2 = [
        ("P0: Чинна (LBA 5)", "valid"),
        ("P1: Чинна (LBA 8)", "valid"),
        ("P2: Вільна сторінка", "free"),
        ("P3: Вільна сторінка", "free"),
        ("P4: Вільна сторінка", "free"),
        ("P5: Вільна сторінка", "free"),
    ]
    for i, (lab, k) in enumerate(pages2):
        f.append(cell(390, 120 + i * 42, 140, 36, lab, k, size=10))

    # Блок 3 (Стертий блок у пулі)
    f.append(fitbox(690, 80, 160, 300, "", fill=GREEN_FILL, stroke=FIELD))
    f.append(text(770, 105, "Блок #12 (Стертий)", size=12, bold=True, color=FIELD))
    pages3 = [
        ("Стерто (0xFF)", "free"),
        ("Стерто (0xFF)", "free"),
        ("Стерто (0xFF)", "free"),
        ("Стерто (0xFF)", "free"),
        ("Стерто (0xFF)", "free"),
        ("Стерто (0xFF)", "free"),
    ]
    for i, (lab, k) in enumerate(pages3):
        f.append(cell(700, 120 + i * 42, 140, 36, lab, k, size=10))

    # Стрілка стирання
    f.append(arrow(550, 230, 680, 230, color=FIELD, sw=2))
    f.append(text(615, 208, "BLOCK ERASE", size=10, color=FIELD, bold=True))

    f.append(fitbox(50, 400, 820, 45, 
                    "Висновок: із 6 сторінок жертви лише 2 скопійовано. Блок стерто й повернуто в пул вільних ресурсів.",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "fig1-gc-lifecycle.svg"), W, H, *f,
           title="Цикл збирання сміття у Flash")

# ───────────────────────────────────────────────────────────────────────────
# Фігура 2 — Стратегії вибору жертви
# ───────────────────────────────────────────────────────────────────────────
def fig_victim_selection():
    W, H = 940, 460
    f = []

    f.append(textbox(160, 40, "Жадібний (Greedy)", size=13, pad=16, bold=True)[0])
    f.append(textbox(470, 40, "Cost-Benefit (Оустерхаут)", size=13, pad=16, bold=True)[0])
    f.append(textbox(780, 40, "Wear-Leveling (Баланс)", size=13, pad=16, bold=True)[0])

    # Стовпчик 1: Greedy
    f.append(fitbox(50, 80, 220, 290, "", fill=FILL, stroke=LINE))
    f.append(text(160, 105, "Критерій: min(V)", size=12, bold=True))
    f.append(cell(65, 130, 190, 40, "Блок A: 10% чинних", "valid", size=11))
    f.append(cell(65, 180, 190, 40, "Блок B: 40% чинних", "data", size=11))
    f.append(cell(65, 230, 190, 40, "Блок C: 80% чинних", "data", size=11))
    f.append(text(160, 300, "Обирає Блок A", size=12, color=POS, bold=True))
    f.append(text(160, 325, "Сліпий до гарячих/холодних", size=10, color=MUTED))
    f.append(text(160, 345, "даних у пам'яті", size=10, color=MUTED))

    # Стовпчик 2: Cost-Benefit
    f.append(fitbox(360, 80, 220, 290, "", fill=FILL, stroke=LINE))
    f.append(text(470, 105, "Критерій: ((1-u)/2u)·age", size=12, bold=True))
    f.append(cell(375, 130, 190, 40, "Блок A (Гарячий, u=0.2)", "hot", size=11))
    f.append(cell(375, 180, 190, 40, "Блок B (Холодний, u=0.4)", "cold", size=11))
    f.append(cell(375, 230, 190, 40, "Блок C (Гарячий, u=0.8)", "hot", size=11))
    f.append(text(470, 300, "Обирає Блок B (Холодний)", size=12, color=NEG, bold=True))
    f.append(text(470, 325, "Чекає самоочищення A;", size=10, color=MUTED))
    f.append(text(470, 345, "консолідує холодний B", size=10, color=MUTED))

    # Стовпчик 3: Wear-Leveling
    f.append(fitbox(670, 80, 220, 290, "", fill=FILL, stroke=LINE))
    f.append(text(780, 105, "Критерій: P/E Cycles", size=12, bold=True))
    f.append(cell(685, 130, 190, 40, "Блок X: P/E = 2900", "hot", size=11))
    f.append(cell(685, 180, 190, 40, "Блок Y: P/E = 2850", "hot", size=11))
    f.append(cell(685, 230, 190, 40, "Блок Z: P/E = 120 (Холод)", "cold", size=11))
    f.append(text(780, 300, "Примусово обирає Z", size=12, color=FIELD, bold=True))
    f.append(text(780, 325, "Вивільняє блок Z для", size=10, color=MUTED))
    f.append(text(780, 345, "вирівнювання зносу комірок", size=10, color=MUTED))

    f.append(fitbox(50, 390, 840, 50,
                    "Порівняння: Жадібний мінімізує копіювання миттєво; Cost-Benefit враховує шар даних; Wear-Leveling рятує залізо.",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "fig2-victim-selection.svg"), W, H, *f,
           title="Стратегії вибору блоку-жертви")

# ───────────────────────────────────────────────────────────────────────────
# Фігура 3 — Фонове проти екстреного GC
# ───────────────────────────────────────────────────────────────────────────
def fig_bg_vs_fg():
    W, H = 900, 460
    f = []

    # Шкала вільних блоків
    f.append(fitbox(60, 60, 780, 140, "", fill=FILL, stroke=LINE))
    f.append(text(450, 85, "Пул вільних блоків (Free Block Pool)", size=14, bold=True))

    # Пороги
    f.append(line(200, 110, 200, 185, color=POS, sw=2, dash="4 4"))
    f.append(text(200, 100, "N_crit (Критичний)", size=11, color=POS, bold=True))

    f.append(line(480, 110, 480, 185, color=NEG, sw=2, dash="4 4"))
    f.append(text(480, 100, "N_low (Нижній)", size=11, color=NEG, bold=True))

    f.append(line(720, 110, 720, 185, color=FIELD, sw=2, dash="4 4"))
    f.append(text(720, 100, "N_high (Верхній)", size=11, color=FIELD, bold=True))

    # Зони
    f.append(rect(80, 120, 110, 55, fill=HOT_FILL, stroke=POS))
    f.append(text(135, 152, "Екстрений GC\n(Foreground)", size=11, color=POS, bold=True))

    f.append(rect(210, 120, 260, 55, fill=BLUE_FILL, stroke=NEG))
    f.append(text(340, 152, "Адаптивне дротування\n(Throttling)", size=11, color=NEG, bold=True))

    f.append(rect(490, 120, 220, 55, fill=GREEN_FILL, stroke=FIELD))
    f.append(text(600, 152, "Фоновий GC\n(Background)", size=11, color=FIELD, bold=True))

    f.append(rect(730, 120, 100, 55, fill=BG, stroke=LINE))
    f.append(text(780, 152, "Спокій\n(Idle)", size=11, color=MUTED))

    # Графік затримок нижче
    f.append(fitbox(60, 230, 780, 200, "", fill=BG, stroke=LINE))
    f.append(text(450, 255, "Вплив на затримку запису хоста (Latency)", size=13, bold=True))

    # Вісі графіку
    f.append(line(100, 400, 800, 400, color=LINE, sw=1.5))
    f.append(line(100, 280, 100, 400, color=LINE, sw=1.5))
    f.append(text(75, 290, "Затримка", size=10, color=MUTED))
    f.append(text(780, 415, "Час / Потік записів", size=10, color=MUTED))

    # Лінія затримок: низька в фоні, сплеск в екстреному
    path_points = [
        (100, 390), (250, 390), (450, 385), (480, 370), 
        (520, 310), (550, 290), (600, 295), (650, 385), (800, 390)
    ]
    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i+1]
        col = POS if y1 < 350 or y2 < 350 else FIELD
        f.append(line(x1, y1, x2, y2, color=col, sw=2.5))

    f.append(text(570, 280, "Сплеск затримки (Tail Latency Spike: 50 ms)", size=11, color=POS, bold=True))
    f.append(text(220, 375, "Нормальна затримка: 200 us", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "fig3-background-vs-foreground.svg"), W, H, *f,
           title="Фонове проти екстреного GC")

# ───────────────────────────────────────────────────────────────────────────
# Фігура 4 — Вплив TRIM / Discard
# ───────────────────────────────────────────────────────────────────────────
def fig_trim_impact():
    W, H = 900, 450
    f = []

    f.append(textbox(230, 40, "БЕЗ команди TRIM", size=14, pad=16, bold=True)[0])
    f.append(textbox(670, 40, "З командою TRIM / Discard", size=14, pad=16, bold=True)[0])

    # Сценарій БЕЗ TRIM
    f.append(fitbox(50, 80, 360, 300, "", fill=HOT_FILL, stroke=POS))
    f.append(text(230, 105, "1. Файл видалено в ОС", size=12, bold=True, color=POS))
    f.append(text(230, 125, "2. FTL НЕ знає про це", size=11, color=INK))

    p_no_trim = [
        ("P0: Дані файлу (Видалено в ОС)", "valid"),
        ("P1: Дані файлу (Видалено в ОС)", "valid"),
        ("P2: Дані файлу (Видалено в ОС)", "valid"),
        ("P3: Корисні дані B", "valid"),
    ]
    for i, (lab, k) in enumerate(p_no_trim):
        f.append(cell(70, 150 + i * 44, 320, 38, lab, k, size=11))

    f.append(text(230, 340, "Результат GC:", size=11, bold=True))
    f.append(text(230, 360, "FTL марно копіює всі 4 сторінки!", size=11, color=POS, bold=True))

    # Сценарій З TRIM
    f.append(fitbox(490, 80, 360, 300, "", fill=GREEN_FILL, stroke=FIELD))
    f.append(text(670, 105, "1. Файл видалено в ОС", size=12, bold=True, color=FIELD))
    f.append(text(670, 125, "2. ОС надсилає команду TRIM", size=11, color=INK))

    p_trim = [
        ("P0: Застаріла ✗ (TRIMmed)", "invalid"),
        ("P1: Застаріла ✗ (TRIMmed)", "invalid"),
        ("P2: Застаріла ✗ (TRIMmed)", "invalid"),
        ("P3: Корисні дані B", "valid"),
    ]
    for i, (lab, k) in enumerate(p_trim):
        f.append(cell(510, 150 + i * 44, 320, 38, lab, k, size=11))

    f.append(text(670, 340, "Результат GC:", size=11, bold=True))
    f.append(text(670, 360, "FTL копіює лише 1 сторінку (P3)!", size=11, color=FIELD, bold=True))

    f.append(fitbox(50, 395, 800, 45,
                    "Висновок: TRIM інформує FTL про вільний простір, ліквідуючи марні міграції та знижуючи WA.",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "fig4-trim-impact.svg"), W, H, *f,
           title="Вплив команди TRIM на збирання сміття")

def main():
    fig_gc_lifecycle()
    fig_victim_selection()
    fig_bg_vs_fg()
    fig_trim_impact()
    print("Усі фігури успішно згенеровано у теці img/")

if __name__ == "__main__":
    main()
