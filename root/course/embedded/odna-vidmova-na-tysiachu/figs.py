# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT = "#2563eb"
ACCENT_BG = "#eff6ff"
BORDER = "#cbd5e1"
TEXT_DARK = "#0f172a"
SUCCESS = "#16a34a"
SUCCESS_BG = "#f0fdf4"
DANGER = "#dc2626"
DANGER_BG = "#fef2f2"
WARN = "#d97706"
WARN_BG = "#fffbeb"
PURPLE = "#7c3aed"
PURPLE_BG = "#f5f3ff"

# ── 1. genealogy-tree.svg ──────────────────────────────────────────────────
# Наскрізна генеалогія друкованого вузла від кремнієвих пластин до рекламації
def fig_genealogy_tree():
    W, H = 880, 480
    p = []
    p.append(text(W/2, 28, "Генеалогічне дерево друкованого вузла (PCBA Traceability)", size=16, bold=True))

    # Рівень 1: Вхідні матеріали
    y1 = 65
    p.append(text(W/2, y1, "1. Вхідна комплектація та напівфабрикати", size=13, bold=True, color=ACCENT))
    
    box_w1 = 200
    box_h1 = 68
    xs1 = [35, 245, 455, 665]
    
    mats = [
        ("Кремнієві чіпи (IC)", ["• Номер пластини (Wafer Lot)", "• Код дати (Date Code: 2134)", "• Степпінг кристала (Rev B)"], PURPLE, PURPLE_BG),
        ("Пасивні SMD (MLCC/R)", ["• Котушка (Reel ID #8921)", "• Виробник / завод (AVL)", "• Партія діелектрика / кераміки"], ACCENT, ACCENT_BG),
        ("Друкована плата (PCB)", ["• Номер панелі (Panel #14)", "• Партія склотекстоліту FR4", "• Склад маски й фінішне ENIG"], FIELD, "#f0fdf4"),
        ("Хімія монтажу", ["• Партія паяльної пасти SAC305", "• Термін життя на трафареті", "• Вологість тари (MSL Level)"], WARN, WARN_BG)
    ]
    
    for x, (title, lines, col, bg) in zip(xs1, mats):
        p.append(rect(x, y1 + 14, box_w1, box_h1, fill=bg, stroke=col, sw=1.4, rx=6))
        p.append(text(x + box_w1/2, y1 + 30, title, size=11, bold=True, color=col))
        ly = y1 + 46
        for ln in lines:
            p.append(text(x + 8, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 16

    # Стрілки від матеріалів до лінії монтажу
    y_arr1 = y1 + 14 + box_h1 + 6
    y_arr1_end = y_arr1 + 22
    for x in xs1:
        cx = x + box_w1/2
        p.append(arrow(cx, y_arr1, cx, y_arr1_end, color=BORDER, sw=1.5))

    # Рівень 2: Процес монтажу на SMT-лінії
    y2 = 190
    p.append(text(W/2, y2, "2. Виробничий процес SMT та телеметрія лінії", size=13, bold=True, color=ACCENT))
    
    box_w2 = 265
    box_h2 = 72
    xs2 = [35, 315, 595]
    
    proc = [
        ("Нанесення пасти (SPI)", ["• Товщина та об'єм пасти (SPI %)", "• Вологість цеху (RH 62%, T 24°C)", "• Номер трафарету та цикл змивки"], WARN, WARN_BG),
        ("Монтаж Pick & Place", ["• ID живильника (Feeder Slot #12)", "• Вакуумні помилки захвату", "• Зіставлення Reel ID ↔ Designator"], ACCENT, ACCENT_BG),
        ("Оплавлення (Reflow Oven)", ["• Пікова температура (T_peak 245°C)", "• Час вище ліквідусу (TAL 55s)", "• Атмосфера (N2 ppm кисню)"], POS, "#fdf2f2")
    ]
    
    for x, (title, lines, col, bg) in zip(xs2, proc):
        p.append(rect(x, y2 + 14, box_w2, box_h2, fill=bg, stroke=col, sw=1.4, rx=6))
        p.append(text(x + box_w2/2, y2 + 30, title, size=11, bold=True, color=col))
        ly = y2 + 47
        for ln in lines:
            p.append(text(x + 10, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 16

    # Стрілки від монтажу до тестування
    y_arr2 = y2 + 14 + box_h2 + 6
    y_arr2_end = y_arr2 + 22
    for x in xs2:
        cx = x + box_w2/2
        p.append(arrow(cx, y_arr2, cx, y_arr2_end, color=BORDER, sw=1.5))

    # Рівень 3: Контроль якості та серійний номер
    y3 = 318
    p.append(text(W/2, y3, "3. Вихідний контроль та присвоєння DataMatrix", size=13, bold=True, color=ACCENT))
    
    box_w3 = 405
    box_h3 = 58
    xs3 = [35, 450]
    
    tests = [
        ("Оптичний та електричний тест (AOI / ICT / FCT)", ["• Логи напруг живлення, опорних джерел VREF, споживання струму", "• ID тестового стенда (Fixture ID), час і результат перевірки"], FIELD, "#f0fdf4"),
        ("Фізичний паспорт вузла (Serial Number)", ["• Унікальний DataMatrix на текстоліті: зв'язок усіх вищевказаних", "  параметрів в єдиний цифровий профіль виробу (Digital Passport)"], PURPLE, PURPLE_BG)
    ]
    
    for x, (title, lines, col, bg) in zip(xs3, tests):
        p.append(rect(x, y3 + 14, box_w3, box_h3, fill=bg, stroke=col, sw=1.4, rx=6))
        p.append(text(x + box_w3/2, y3 + 30, title, size=11, bold=True, color=col))
        ly = y3 + 47
        for ln in lines:
            p.append(text(x + 10, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 16

    # Стрілка вниз до польової рекламації
    p.append(arrow(W/2, y3 + 14 + box_h3 + 6, W/2, y3 + 14 + box_h3 + 26, color=DANGER, sw=2.0))

    # Рівень 4: Польова рекламація (RMA)
    y4 = 422
    p.append(rect(140, y4, 600, 48, fill=DANGER_BG, stroke=DANGER, sw=1.6, rx=6))
    p.append(text(W/2, y4 + 20, "Польовий відсів (RMA Return): симптом збою + серійний номер", size=12, bold=True, color=DANGER))
    p.append(text(W/2, y4 + 38, "За серійним номером розгортається повний стек історії виготовлення для кореляційного аналізу", size=10, color=TEXT_DARK))

    render(os.path.join(OUT, "genealogy-tree.svg"), W, H, *p)


# ── 2. contingency-correlation.svg ──────────────────────────────────────────
# Матриця спряженості 2x2 та порівняння шансів відмови (Odds Ratio)
def fig_contingency_correlation():
    W, H = 880, 430
    p = []
    p.append(text(W/2, 28, "Матриця спряженості 2x2 та ізоляція дефектної партії", size=16, bold=True))

    # Ліва панель: 2x2 матриця спряженості
    x_m = 40
    y_m = 65
    w_m = 400
    h_m = 335
    p.append(rect(x_m, y_m, w_m, h_m, fill=FILL, stroke=BORDER, sw=1.5, rx=8))
    p.append(text(x_m + w_m/2, y_m + 25, "Матриця 2×2 (Contingency Table)", size=13, bold=True, color=ACCENT))
    
    # Таблиця
    tx0 = x_m + 110
    ty0 = y_m + 65
    cell_w = 125
    cell_h = 60
    
    # Заголовки стовпців
    p.append(text(tx0 + cell_w/2, ty0 - 12, "Відмова (RMA)", size=11, bold=True, color=DANGER))
    p.append(text(tx0 + cell_w*1.5, ty0 - 12, "Справні (OK)", size=11, bold=True, color=SUCCESS))
    
    # Заголовки рядків
    p.append(text(tx0 - 55, ty0 + cell_h/2 + 4, "Підозріла партія\n(Vendor B / DC2134)", size=10, bold=True, color=TEXT_DARK))
    p.append(text(tx0 - 55, ty0 + cell_h*1.5 + 4, "Інші партії\n(Vendor A / інші DC)", size=10, bold=True, color=TEXT_DARK))
    
    # Клітинки
    # A: Пошкоджені з підозрілої партії
    p.append(rect(tx0, ty0, cell_w, cell_h, fill=DANGER_BG, stroke=DANGER, sw=1.6, rx=4))
    p.append(text(tx0 + cell_w/2, ty0 + 26, "a = 18", size=16, bold=True, color=DANGER))
    p.append(text(tx0 + cell_w/2, ty0 + 46, "Збій + Дефектний лот", size=9, color=MUTED))
    
    # B: Справні з підозрілої партії
    p.append(rect(tx0 + cell_w + 6, ty0, cell_w, cell_h, fill=SUCCESS_BG, stroke=SUCCESS, sw=1.2, rx=4))
    p.append(text(tx0 + cell_w*1.5 + 6, ty0 + 26, "b = 982", size=15, bold=True, color=TEXT_DARK))
    p.append(text(tx0 + cell_w*1.5 + 6, ty0 + 46, "Справні в лоті (Σ = 1000)", size=9, color=MUTED))
    
    # C: Пошкоджені з інших партій
    p.append(rect(tx0, ty0 + cell_h + 6, cell_w, cell_h, fill="#fff5f5", stroke=BORDER, sw=1.2, rx=4))
    p.append(text(tx0 + cell_w/2, ty0 + cell_h + 32, "c = 2", size=15, bold=True, color=TEXT_DARK))
    p.append(text(tx0 + cell_w/2, ty0 + cell_h + 52, "Фоновий збій", size=9, color=MUTED))
    
    # D: Справні з інших партій
    p.append(rect(tx0 + cell_w + 6, ty0 + cell_h + 6, cell_w, cell_h, fill=SUCCESS_BG, stroke=BORDER, sw=1.2, rx=4))
    p.append(text(tx0 + cell_w*1.5 + 6, ty0 + cell_h + 32, "d = 18 998", size=15, bold=True, color=TEXT_DARK))
    p.append(text(tx0 + cell_w*1.5 + 6, ty0 + cell_h + 52, "Справні (Σ = 19 000)", size=9, color=MUTED))

    # Підсумкові розрахунки знизу таблиці
    p.append(text(x_m + w_m/2, y_m + 225, "Частота збоїв у підозрілій партії: 18 / 1000 = 1.80%", size=10.5, bold=True, color=DANGER))
    p.append(text(x_m + w_m/2, y_m + 248, "Частота збоїв у решті партій: 2 / 19 000 = 0.01%", size=10.5, bold=True, color=SUCCESS))
    p.append(text(x_m + w_m/2, y_m + 272, "Відносний ризик (Relative Risk) = 1.80% / 0.01% = 171.0×", size=11, bold=True, color=PURPLE))
    p.append(text(x_m + w_m/2, y_m + 296, "Точний тест Фішера: p = 1.4 × 10⁻¹⁹ (випадковість виключена)", size=10, bold=True, color=TEXT_DARK))

    # Права панель: Інтерпретація та локалізація відклику
    x_r = 460
    y_r = 65
    w_r = 380
    h_r = 335
    p.append(rect(x_r, y_r, w_r, h_r, fill=FILL, stroke=BORDER, sw=1.5, rx=8))
    p.append(text(x_r + w_r/2, y_r + 25, "Інженерне рішення та ізоляція", size=13, bold=True, color=ACCENT))

    cards = [
        ("Без кореляції за генеалогією (Повна паніка)", DANGER, DANGER_BG, [
            "• «Усі 20 000 плат під загрозою»",
            "• Загальний відклик партії ($350 000 збитків)",
            "• Інженери безпорадно шукають «баг у софті»",
            "• Репутаційний крах бренду"
        ]),
        ("З точним кореляційним аналізом (Хірургічний карантин)", SUCCESS, SUCCESS_BG, [
            "• Винна одна котушка MLCC (Reel #8921, DC2134)",
            "• Вражено лише 1 000 серійних номерів (SN 14000..14999)",
            "• Карантин на складах для невідвантажених 600 шт.",
            "• Адресна сервісна заміна лише 400 пристроїв у клієнтів",
            "• Загальні витрати скорочено в 20 разів!"
        ])
    ]

    yc = y_r + 48
    for head, col, bg, lines in cards:
        ch = 120 if col == SUCCESS else 105
        p.append(rect(x_r + 15, yc, w_r - 30, ch, fill=bg, stroke=col, sw=1.4, rx=6))
        p.append(text(x_r + 25, yc + 18, head, size=10.5, bold=True, color=col, anchor="start"))
        ly = yc + 36
        for ln in lines:
            p.append(text(x_r + 25, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 17
        yc += ch + 12

    render(os.path.join(OUT, "contingency-correlation.svg"), W, H, *p)


# ── 3. subtle-failure-mechanisms.svg ────────────────────────────────────────
# Три фізичні механізми прихованих дефектів рівня 0.1%
def fig_subtle_failure_mechanisms():
    W, H = 880, 440
    p = []
    p.append(text(W/2, 26, "Фізична природа дефектів «однієї відмови на тисячу»", size=16, bold=True))

    col_w = 265
    col_h = 360
    xs = [30, 310, 585]
    y0 = 55

    cols_data = [
        ("А. DC-Bias та п'єзоефект MLCC", ACCENT, ACCENT_BG, [
            "Зміна постачальника пасивів (AVL)",
            "------------------------------------",
            "• Номінал: 10 мкФ 0805 X7R",
            "• Постачальник A: 6.5 мкФ при 3.3 В",
            "• Постачальник B: 1.8 мкФ при 3.3 В",
            "  (просідання ємності на 82%!)",
            "------------------------------------",
            "Наслідок у полі:",
            "Провал напруги живлення DC-DC",
            "під час стрибка струму радіомодуля,",
            "непередбачуваний Brown-out Reset (BOR)."
        ]),
        ("Б. MSL та мікротріщини (Popcorning)", WARN, WARN_BG, [
            "Вологість корпусу перед Reflow",
            "------------------------------------",
            "• Корпус QFN/BGA увібрав вологу",
            "  (перевищено Floor Life > 168 год)",
            "• При 245°C волога вибухає парою,",
            "  виникає внутрішнє розшарування",
            "------------------------------------",
            "Наслідок у полі:",
            "Плата проходить заводський ICT,",
            "але через 100 термоциклів зима/літо",
            "відривається розварений контакт кристала."
        ]),
        ("В. Дендрити та залишки флюсу (ECM)", POS, "#fdf2f2", [
            "Недогрітий No-Clean флюс + волога",
            "------------------------------------",
            "• Неповна активація флюсу в печі",
            "• Залишки кислотних іонних сполук",
            "• Постійна напруга (DC-bias) на шині",
            "• Електрохімічна міграція іонів міді",
            "------------------------------------",
            "Наслідок у полі:",
            "Ростуть струмопровідні мікронитки,",
            "опір ізоляції падає зі 100 МОм до",
            "50 кОм: фантомні натискання й витік струму."
        ])
    ]

    for x, (title, col, bg, lines) in zip(xs, cols_data):
        p.append(rect(x, y0, col_w, col_h, fill=bg, stroke=col, sw=1.5, rx=6))
        p.append(text(x + col_w/2, y0 + 24, title, size=11.5, bold=True, color=col))
        p.append(line(x + 10, y0 + 36, x + col_w - 10, y0 + 36, color=col, sw=1.0))
        ly = y0 + 58
        for ln in lines:
            if ln.startswith("---"):
                p.append(line(x + 15, ly - 4, x + col_w - 15, ly - 4, color=BORDER, sw=0.8, dash="3,3"))
                ly += 12
            elif ln.startswith("Наслідок"):
                p.append(text(x + 12, ly, ln, size=10, bold=True, color=TEXT_DARK, anchor="start"))
                ly += 18
            else:
                p.append(text(x + 12, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
                ly += 18

    render(os.path.join(OUT, "subtle-failure-mechanisms.svg"), W, H, *p)


if __name__ == "__main__":
    fig_genealogy_tree()
    fig_contingency_correlation()
    fig_subtle_failure_mechanisms()
    print("Figures generated successfully in ./img/")
