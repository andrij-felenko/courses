# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT = "#2563eb"      # синій
ACCENT_BG = "#eff6ff"
BORDER = "#cbd5e1"
TEXT_DARK = "#0f172a"
SUCCESS = "#16a34a"     # зелений
SUCCESS_BG = "#f0fdf4"
DANGER = "#dc2626"      # червоний
DANGER_BG = "#fef2f2"
WARN = "#d97706"        # помаранчевий
WARN_BG = "#fffbeb"
PURPLE = "#7c3aed"      # фіолетовий
PURPLE_BG = "#f5f3ff"


# ── 1. certification-decision-tree.svg ───────────────────────────────────────
def fig_certification_decision_tree():
    W, H = 960, 520
    p = []
    p.append(text(W/2, 28, "Архітектурне дерево вибору сертифікаційних програм для пристрою", size=15, bold=True))

    # 4 блоки критеріїв зліва
    col_w = 210
    col_h = 90
    x0 = 24
    y_gap = 104
    y_start = 64

    criteria = [
        ("1. Ринок збуту", ["• ЄС: CE (самодекларація)", "• США: FCC + OSHA / UL", "• Світ: ISED, MIC, SRRC"], ACCENT, ACCENT_BG),
        ("2. Радіотракт", ["• Без радіо: лише ненавмисне", "• Модуль: FCC ID + Spurious", "• Chip-down: повне RED / FCC"], PURPLE, PURPLE_BG),
        ("3. Джерело живлення", ["• Мережа 230 В: LVD + Hi-Pot", "• SELV < 60 В: GPSR (без LVD)", "• Li-ion: обов'язковий UN 38.3"], WARN, WARN_BG),
        ("4. Галузь застосування", ["• Побутова: Class B (жорсткіше)", "• Пром: Class A + 10 В/м імунітет", "• IoT / Мережа: CRA + EN 303 645"], SUCCESS, SUCCESS_BG)
    ]

    for i, (title, lines, col, bg) in enumerate(criteria):
        cy = y_start + i * y_gap
        p.append(rect(x0, cy, col_w, col_h, fill=bg, stroke=col, sw=1.5, rx=6))
        p.append(text(x0 + col_w/2, cy + 20, title, size=12, bold=True, color=col))
        p.append(line(x0 + 8, cy + 28, x0 + col_w - 8, cy + 28, color=col, sw=0.8))
        ly = cy + 46
        for ln in lines:
            p.append(text(x0 + 10, ly, ln, size=10, color=TEXT_DARK, anchor="start"))
            ly += 18

    # Центральний блок: Матриця оцінки архітектури
    cx = 275
    cw = 260
    ch = 402
    cy0 = 64
    p.append(rect(cx, cy0, cw, ch, fill="#f8fafc", stroke=BORDER, sw=1.4, rx=6))
    p.append(text(cx + cw/2, cy0 + 24, "Архітектурний фільтр ризиків", size=12.5, bold=True, color=TEXT_DARK))
    p.append(line(cx + 12, cy0 + 34, cx + cw - 12, cy0 + 34, color=BORDER, sw=1.0))

    filters = [
        ("Висока напруга (Mains AC)", "Вимагає LVD, ізоляцію 3 кВ, пластик V-0", DANGER),
        ("Дискретне радіо (Chip-down)", "Повна камера RED/FCC, SAR ($15k+)", DANGER),
        ("Готовий радіомодуль", "Лише Spurious + Part 15B ($3k)", SUCCESS),
        ("Живлення SELV (адаптер)", "Знімає дію директиви LVD з плати", SUCCESS),
        ("Li-ion акумулятор", "Тести UN 38.3 (T.1-T.8) для перевезення", WARN),
        ("Підключення до Інтернету", "Вимоги CRA / RED 3.3 / EN 303 645", PURPLE)
    ]

    fy = cy0 + 48
    for head, desc, tag_col in filters:
        p.append(rect(cx + 10, fy, cw - 20, 50, fill="#ffffff", stroke=BORDER, sw=1.0, rx=4))
        p.append(circle(cx + 22, fy + 16, 4, fill=tag_col, stroke=tag_col))
        p.append(text(cx + 32, fy + 20, head, size=10, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(cx + 16, fy + 38, desc, size=9.5, color=MUTED, anchor="start"))
        fy += 58

    # Стрілки від критеріїв до фільтра
    for i in range(4):
        src_y = y_start + i * y_gap + col_h / 2
        p.append(arrow(x0 + col_w + 2, src_y, cx - 4, src_y, color=LINE, sw=1.4))

    # Стрілка від фільтра до виходу
    p.append(arrow(cx + cw + 2, cy0 + ch/2, cx + cw + 28, cy0 + ch/2, color=LINE, sw=1.6))

    # Блоки результату справа (Обов'язкові директиви та випробування)
    rx = 572
    rw = 364
    ry0 = 64
    p.append(rect(rx, ry0, rw, ch, fill="#ffffff", stroke=ACCENT, sw=1.5, rx=6))
    p.append(text(rx + rw/2, ry0 + 24, "Підсумковий пакет сертифікації", size=12.5, bold=True, color=ACCENT))
    p.append(line(rx + 12, ry0 + 34, rx + rw - 12, ry0 + 34, color=ACCENT, sw=1.0))

    results = [
        ("EMC (2014/30/EU / FCC Part 15B)", "EN 55032 (емісія Class A/B), EN 55035 (ESD, Surge)", ACCENT_BG, ACCENT),
        ("Радіоспектр (RED 2014/53/EU / FCC 15C)", "EN 300 328 (спектральна маска, потужність EIRP)", PURPLE_BG, PURPLE),
        ("Безпека / LVD (2014/35/EU / IEC 62368)", "Зазори/витоки, електрична міцність, займистість", WARN_BG, WARN),
        ("Екологія: RoHS 3, REACH, WEEE", "Декларації компонентів (BOM), знак утилізації", SUCCESS_BG, SUCCESS),
        ("Транспорт та кібербезпека", "UN 38.3 (батареї), ETSI EN 303 645 (CRA паролі)", DANGER_BG, DANGER)
    ]

    ry = ry0 + 46
    for title_r, desc_r, bg_r, col_r in results:
        p.append(rect(rx + 10, ry, rw - 20, 60, fill=bg_r, stroke=col_r, sw=1.2, rx=4))
        p.append(text(rx + 18, ry + 22, title_r, size=10.5, bold=True, color=col_r, anchor="start"))
        p.append(text(rx + 18, ry + 44, desc_r, size=9.5, color=TEXT_DARK, anchor="start"))
        ry += 69

    render(os.path.join(OUT, "certification-decision-tree.svg"), W, H, *p)


# ── 2. emc-spectrum-and-limits.svg ──────────────────────────────────────────
def fig_emc_spectrum_and_limits():
    W, H = 960, 470
    p = []
    p.append(text(W/2, 28, "Спектральний розподіл ЕМС: завади провідності, випромінювання та ліміти", size=15, bold=True))

    # Головна вісь частот
    ax_x1, ax_x2 = 60, 900
    ax_y = 110
    p.append(line(ax_x1, ax_y, ax_x2, ax_y, color=INK, sw=2.0))
    p.append(arrow(ax_x2 - 10, ax_y, ax_x2 + 20, ax_y, color=INK, sw=2.0))
    p.append(text(ax_x2 + 25, ax_y - 8, "Частота f", size=11, bold=True, color=INK, anchor="end"))

    # Поділки частотної шкали
    freqs = [
        (ax_x1, "9 кГц"),
        (210, "150 кГц"),
        (400, "30 МГц"),
        (650, "1 ГГц"),
        (ax_x2 - 20, "6 ГГц")
    ]
    for fx, flabel in freqs:
        p.append(line(fx, ax_y - 6, fx, ax_y + 6, color=INK, sw=1.5))
        p.append(text(fx, ax_y + 22, flabel, size=10.5, bold=True, color=TEXT_DARK))

    # Зона 1: Завади провідності (Conducted Emissions)
    z1_x, z1_w = 210, 190
    p.append(rect(z1_x, 48, z1_w, 44, fill=ACCENT_BG, stroke=ACCENT, sw=1.4, rx=4))
    p.append(text(z1_x + z1_w/2, 66, "Завади провідності", size=11, bold=True, color=ACCENT))
    p.append(text(z1_x + z1_w/2, 82, "150 кГц – 30 МГц (LISN)", size=9.5, color=MUTED))

    # Зона 2: Випромінювані завади (Radiated Emissions)
    z2_x, z2_w = 400, 480
    p.append(rect(z2_x, 48, z2_w, 44, fill=PURPLE_BG, stroke=PURPLE, sw=1.4, rx=4))
    p.append(text(z2_x + z2_w/2, 66, "Випромінювані завади в просторі", size=11, bold=True, color=PURPLE))
    p.append(text(z2_x + z2_w/2, 82, "30 МГц – 6 ГГц (Безвідлунна камера)", size=9.5, color=MUTED))

    # Блоки опису джерел завад та методів вимірювання
    y_blocks = 160
    bh = 135
    
    # Блок 1: Провідність
    p.append(rect(50, y_blocks, 415, bh, fill="#ffffff", stroke=BORDER, sw=1.2, rx=6))
    p.append(text(65, y_blocks + 22, "Завади провідності (Conducted Emissions)", size=11.5, bold=True, color=ACCENT, anchor="start"))
    p.append(line(65, y_blocks + 28, 445, y_blocks + 28, color=BORDER, sw=0.8))
    
    c_lines = [
        "• Метод: вимірювання струмів через мережу LISN (50 Ом / 50 мкГн)",
        "• Джерела: ШІМ ключів DC-DC (100–500 кГц) та випрямлячів",
        "• Ліміти EN 55032: Class B (46–66 дБмкВ), Class A (+10 дБ послаблення)",
        "• Лікування: синфазні дроселі, X/Y конденсатори, П-фільтри"
    ]
    cy = y_blocks + 48
    for ln in c_lines:
        p.append(text(65, cy, ln, size=10, color=TEXT_DARK, anchor="start"))
        cy += 21

    # Блок 2: Випромінювання
    p.append(rect(495, y_blocks, 415, bh, fill="#ffffff", stroke=BORDER, sw=1.2, rx=6))
    p.append(text(510, y_blocks + 22, "Випромінювані завади (Radiated Emissions)", size=11.5, bold=True, color=PURPLE, anchor="start"))
    p.append(line(510, y_blocks + 28, 890, y_blocks + 28, color=BORDER, sw=0.8))

    r_lines = [
        "• Метод: вимірювальна антена на відстані 3 м або 10 м у SAC",
        "• Джерела: тактові генератори (24/48 МГц), шлейфи, швидкісні шини",
        "• Ліміти EN 55032: Class B (30–37 дБмкВ/м), Class A (40–47 дБмкВ/м)",
        "• Лікування: суцільний шар GND, феритові намистини, екранування"
    ]
    ry = y_blocks + 48
    for ln in r_lines:
        p.append(text(510, ry, ln, size=10, color=TEXT_DARK, anchor="start"))
        ry += 21

    # Нижня панель: Критерії стійкості виробу (Performance Criteria)
    y_crit = 315
    ch_h = 135
    p.append(rect(50, y_crit, 860, ch_h, fill="#f8fafc", stroke=BORDER, sw=1.2, rx=6))
    p.append(text(65, y_crit + 24, "Критерії стійкості до завад (Immunity Performance Criteria за EN 55035 / EN 61000-6-2):", size=11.5, bold=True, color=TEXT_DARK, anchor="start"))
    
    crit_cards = [
        ("Критерій A: Нормальна робота", "Прилад працює без збоїв і втрати даних під час дії завади (ESD 4 кВ, RF 3..10 В/м)", SUCCESS, SUCCESS_BG),
        ("Критерій B: Самовідновлення", "Тимчасове погіршення параметрів під час завади з автоматичним відновленням без людини", WARN, WARN_BG),
        ("Критерій C: Втручання оператора", "Зависання або скидання, яке вимагає ручного перезапуску живлення користувачем", DANGER, DANGER_BG)
    ]
    
    cx_card = 65
    cw_card = 266
    for c_title, c_body, c_col, c_bg in crit_cards:
        p.append(rect(cx_card, y_crit + 38, cw_card, 82, fill=c_bg, stroke=c_col, sw=1.0, rx=4))
        p.append(text(cx_card + 10, y_crit + 58, c_title, size=10.5, bold=True, color=c_col, anchor="start"))
        p.append(text(cx_card + 10, y_crit + 78, c_body[:44], size=9.5, color=TEXT_DARK, anchor="start"))
        p.append(text(cx_card + 10, y_crit + 96, c_body[44:], size=9.5, color=TEXT_DARK, anchor="start"))
        cx_card += cw_card + 16

    render(os.path.join(OUT, "emc-spectrum-and-limits.svg"), W, H, *p)


# ── 3. lab-testing-pipeline.svg ─────────────────────────────────────────────
def fig_lab_testing_pipeline():
    W, H = 960, 480
    p = []
    p.append(text(W/2, 28, "Конвеєр сертифікації: від передтестування на столі до знаків CE та FCC", size=15, bold=True))

    # 4 етапи конвеєра
    stages = [
        ("1. Передтестування (Pre-compliance)", [
            "• H-field магнітні пробники",
            "• Настільний спектроаналізатор",
            "• Виявлення піків на платі",
            "• Локалізація струмових петель"
        ], SUCCESS, SUCCESS_BG),
        ("2. Акредитована лабораторія", [
            "• Безвідлунна камера (SAC 3m/10m)",
            "• Тести на радіо, EMC, ESD, Surge",
            "• Випробування безпеки LVD",
            "• Офіційні протоколи Test Reports"
        ], ACCENT, ACCENT_BG),
        ("3. Технічний файл (TCF)", [
            "• Повні електричні схеми й BOM",
            "• Сертифікати RoHS / REACH / UN 38.3",
            "• Оцінка кіберризиків (CRA)",
            "• Інструкція користувача й маркування"
        ], WARN, WARN_BG),
        ("4. Декларація (DoC) і маркування", [
            "• Підписана директором EU DoC",
            "• Отримання FCC ID (TCB Grant)",
            "• Нанесення знаків CE, FCC, WEEE",
            "• Легальний випуск на ринок"
        ], PURPLE, PURPLE_BG)
    ]

    card_w = 210
    card_h = 170
    x_start = 24
    x_gap = 240
    y_card = 64

    for i, (stitle, slines, scol, sbg) in enumerate(stages):
        cx = x_start + i * x_gap
        p.append(rect(cx, y_card, card_w, card_h, fill=sbg, stroke=scol, sw=1.5, rx=6))
        p.append(text(cx + card_w/2, y_card + 20, stitle, size=10.5, bold=True, color=scol))
        p.append(line(cx + 8, y_card + 28, cx + card_w - 8, y_card + 28, color=scol, sw=0.8))
        ly = y_card + 48
        for ln in slines:
            p.append(text(cx + 10, ly, ln, size=10, color=TEXT_DARK, anchor="start"))
            ly += 23

        if i < 3:
            p.append(arrow(cx + card_w + 4, y_card + card_h/2, cx + card_w + 26, y_card + card_h/2, color=LINE, sw=1.6))

    # Нижній блок: Крива вартості усунення дефектів (Rule of 10x)
    y_rule = 260
    p.append(rect(x_start, y_rule, 912, 195, fill="#ffffff", stroke=BORDER, sw=1.4, rx=6))
    p.append(text(W/2, y_rule + 24, "Економіка сертифікації: експоненційне зростання вартості виправлення помилок", size=12.5, bold=True, color=TEXT_DARK))
    p.append(line(x_start + 14, y_rule + 36, x_start + 898, y_rule + 36, color=BORDER, sw=0.8))

    costs = [
        ("САПР / Схема", "$10..$50", ["Зміна номіналу RC-фільтра,", "додавання TVS на схемі", "(10 хвилин роботи)"], SUCCESS, SUCCESS_BG),
        ("Ревізія PCB", "$300..$1 500", ["Перерозведення 4-шарової", "плати, замовлення нової", "вибірки на фабриці"], WARN, WARN_BG),
        ("Лабораторія", "$3 000..$8 000", ["Провал у камері: повторна", "оренда $2k/день + затримка", "релізу на 4 тижні"], DANGER, DANGER_BG),
        ("Митниця / Ринок", "$50 000..$200k+", ["Арешт партії, заборона", "продажу, штрафи, повне", "відкликання серії"], "#991b1b", "#fee2e2")
    ]

    cw_box = 210
    cx_box = x_start + 12
    for c_stage, c_val, c_lines, c_col, c_bg in costs:
        p.append(rect(cx_box, y_rule + 48, cw_box, 130, fill=c_bg, stroke=c_col, sw=1.2, rx=5))
        p.append(text(cx_box + cw_box/2, y_rule + 70, c_stage, size=11.5, bold=True, color=TEXT_DARK))
        p.append(text(cx_box + cw_box/2, y_rule + 94, c_val, size=13.5, bold=True, color=c_col))
        p.append(line(cx_box + 12, y_rule + 104, cx_box + cw_box - 12, y_rule + 104, color=c_col, sw=0.6))
        
        ly_exp = y_rule + 122
        for eln in c_lines:
            p.append(text(cx_box + cw_box/2, ly_exp, eln, size=9.5, color=TEXT_DARK))
            ly_exp += 16
            
        cx_box += cw_box + 20

    render(os.path.join(OUT, "lab-testing-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_certification_decision_tree()
    fig_emc_spectrum_and_limits()
    fig_lab_testing_pipeline()
    print("All figures generated successfully.")
