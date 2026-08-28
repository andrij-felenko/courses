# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT = "#2563eb"    # синій акцент
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

# ── 1. bom-row-anatomy.svg ──────────────────────────────────────────────────
# Анатомія рядка BOM: Designator, Qty, MPN (зі структурою), Footprint, Value, Rating, Description, Status/DNP, AVL
def fig_bom_row_anatomy():
    W, H = 860, 370
    p = []
    p.append(text(W/2, 28, "Анатомія інженерного рядка специфікації BOM", size=15, bold=True))

    # Стовпчики таблиці BOM
    cols = [
        ("Designator", "R1, R2, R5", 100, ACCENT, ACCENT_BG),
        ("Qty", "3", 45, INK, FILL),
        ("Manufacturer Part Number (MPN)", "RC0603FR-0710KL", 215, POS, "#fdf2f2"),
        ("Manufacturer", "Yageo", 85, INK, FILL),
        ("Package / Footprint", "0603 (1608 Metric)", 135, FIELD, "#f0fdf4"),
        ("Value / Rating", "10k 1% 100mW 50V", 135, INK, FILL),
        ("Status / DNP", "Populate", 75, SUCCESS, SUCCESS_BG),
    ]

    y_header = 70
    h_header = 32
    y_row = y_header + h_header + 4
    h_row = 38

    x = 25
    for title, val, w, stroke_c, fill_c in cols:
        # Заголовок стовпця
        p.append(rect(x, y_header, w, h_header, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
        p.append(text(x + w/2, y_header + 20, title, size=10, bold=True, color=TEXT_DARK))
        
        # Значення в рядку
        p.append(rect(x, y_row, w, h_row, fill=fill_c, stroke=stroke_c, sw=1.4, rx=4))
        p.append(text(x + w/2, y_row + 24, val, size=10.5, bold=True, color=TEXT_DARK))
        x += w + 6

    # Нижній блок пояснень: хто який стовпець читає і навіщо
    y_cards = 180
    card_w = 250
    card_h = 145
    card_gap = 26
    xs = [25, 25 + card_w + card_gap, 25 + 2 * (card_w + card_gap)]

    cards_data = [
        ("Автомат Pick & Place (CPL)", ACCENT, ACCENT_BG, [
            "• Звіряє Designator (R1, R2...)",
            "• Бере деталь за Package (0603)",
            "• Ігнорує позиції зі статусом DNP",
            "• Шукає координати в Pick & Place"
        ]),
        ("Відділ закупівель (ERP)", POS, "#fdf2f2", [
            "• Замовляє ТОЧНИЙ повний MPN",
            "• Перевіряє суфікс котушки (Tape&Reel)",
            "• Звіряє замовлену Qty + Attrition (+10%)",
            "• Використовує схвалений список замін (AVL)"
        ]),
        ("Інженерний контроль (DRC/ERC)", FIELD, "#f0fdf4", [
            "• Value/Rating: робоча напруга, точність",
            "• Footprint: відповідність IPC-7351",
            "• DNP: тестові шунти та конфігурація",
            "• Ревізія: зв'язок зі схемою та платою"
        ])
    ]

    for cx, (head, col, bg, lines) in zip(xs, cards_data):
        p.append(rect(cx, y_cards, card_w, card_h, fill=bg, stroke=col, sw=1.5, rx=6))
        p.append(text(cx + card_w/2, y_cards + 22, head, size=11, bold=True, color=col))
        p.append(line(cx + 10, y_cards + 32, cx + card_w - 10, y_cards + 32, color=col, sw=1.0))
        ly = y_cards + 54
        for ln in lines:
            p.append(text(cx + 12, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 22

    render(os.path.join(OUT, "bom-row-anatomy.svg"), W, H, *p)


# ── 2. mpn-suffix-trap.svg ──────────────────────────────────────────────────
# Розбір структури MPN: базовий номер проти суфіксів пакування, температури, ревізії
def fig_mpn_suffix_trap():
    W, H = 860, 390
    p = []
    p.append(text(W/2, 28, "Анатомія суфіксів MPN: пастки закупівлі та виробництва", size=15, bold=True))

    # Приклад 1: STM32F405RGT6TR
    p.append(text(30, 68, "Приклад 1: Мікроконтролер STMicroelectronics", size=11.5, bold=True, color=INK, anchor="start"))
    
    parts_mcu = [
        ("STM32", "ARM Cortex", 70, "#3b82f6", "#eff6ff"),
        ("F405", "168 МГц USB", 75, "#3b82f6", "#eff6ff"),
        ("R", "64 піни", 45, "#10b981", "#ecfdf5"),
        ("G", "1 МБ Flash", 55, "#10b981", "#ecfdf5"),
        ("T", "LQFP", 42, "#8b5cf6", "#f5f3ff"),
        ("6", "Ind -40..+85°C", 78, "#f59e0b", "#fffbeb"),
        ("TR", "Tape & Reel (Стрічка)", 125, "#ef4444", "#fef2f2")
    ]

    x0 = 30
    y0 = 85
    h_box = 32
    x = x0
    for code, desc, w, col, bg in parts_mcu:
        p.append(rect(x, y0, w, h_box, fill=bg, stroke=col, sw=1.4, rx=4))
        p.append(text(x + w/2, y0 + 21, code, size=11, bold=True, color=col))
        x += w + 4

    # Підписи під кожним сегментом
    x = x0
    labels_y = y0 + h_box + 16
    for code, desc, w, col, bg in parts_mcu:
        p.append(line(x + w/2, y0 + h_box, x + w/2, labels_y - 4, color=col, sw=1.0))
        p.append(text(x + w/2, labels_y + 8, desc, size=9.5, color=TEXT_DARK))
        x += w + 4

    # Пастка 1: без суфікса TR
    p.append(rect(540, 78, 290, 85, fill="#fef2f2", stroke="#ef4444", sw=1.4, rx=6))
    p.append(text(685, 98, "Пастка суфікса пакування:", size=10.5, bold=True, color="#b91c1c"))
    p.append(text(685, 116, "STM32F405RGT6 = Tray (пластиковий піддон)", size=9.5, color=TEXT_DARK))
    p.append(text(685, 134, "STM32F405RGT6TR = Tape & Reel (стрічка)", size=9.5, bold=True, color="#15803d"))
    p.append(text(685, 150, "Монтажний автомат вимагає стрічку!", size=9.5, color="#b91c1c", italic=True))

    # Розділювач
    p.append(line(30, 195, 830, 195, color="#e2e8f0", sw=1.2))

    # Приклад 2: TPS62130RGTR (Texas Instruments)
    p.append(text(30, 225, "Приклад 2: DC-DC перетворювач Texas Instruments", size=11.5, bold=True, color=INK, anchor="start"))

    parts_dcdc = [
        ("TPS62130", "Step-Down 3A перетворювач", 185, "#3b82f6", "#eff6ff"),
        ("RGT", "Корпус VQFN-16 (3×3 мм)", 135, "#8b5cf6", "#f5f3ff"),
        ("R", "Reel 3000 шт (велика котушка)", 165, "#ef4444", "#fef2f2")
    ]

    x = x0
    y0 = 245
    for code, desc, w, col, bg in parts_dcdc:
        p.append(rect(x, y0, w, h_box, fill=bg, stroke=col, sw=1.4, rx=4))
        p.append(text(x + w/2, y0 + 21, code, size=11, bold=True, color=col))
        x += w + 4

    x = x0
    labels_y = y0 + h_box + 16
    for code, desc, w, col, bg in parts_dcdc:
        p.append(line(x + w/2, y0 + h_box, x + w/2, labels_y - 4, color=col, sw=1.0))
        p.append(text(x + w/2, labels_y + 8, desc, size=9.5, color=TEXT_DARK))
        x += w + 4

    # Пастка 2: RGTR vs RGTT
    p.append(rect(540, 238, 290, 85, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(685, 258, "Пастка обсягу котушки (MOQ):", size=10.5, bold=True, color="#b45309"))
    p.append(text(685, 276, "TPS62130RGTR = Reel 3000 шт (велика)", size=9.5, color=TEXT_DARK))
    p.append(text(685, 294, "TPS62130RGTT = Mini-Reel 250 шт (мала)", size=9.5, bold=True, color="#15803d"))
    p.append(text(685, 310, "Для прототипу 10 плат RGTR заморозить $5000", size=9.5, color="#b45309", italic=True))

    render(os.path.join(OUT, "mpn-suffix-trap.svg"), W, H, *p)


# ── 3. second-sourcing-matrix.svg ───────────────────────────────────────────
# Матриця Second Sourcing та AVL: пасивні деталі проти активних ІС
def fig_second_sourcing_matrix():
    W, H = 860, 370
    p = []
    p.append(text(W/2, 28, "Матриця заміни компонентів (Second Sourcing & AVL)", size=15, bold=True))

    col_w = 385
    h_box = 290
    y0 = 60

    # Ліва колонка: Пасивні компоненти (Generic)
    p.append(rect(30, y0, col_w, h_box, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=8))
    p.append(rect(30, y0, col_w, 36, fill="#3b82f6", stroke="#3b82f6", sw=1.0, rx=8))
    p.append(text(30 + col_w/2, y0 + 24, "Пасивні компоненти (Резистори / Конденсатори)", size=11.5, bold=True, color="#ffffff"))

    p_items = [
        ("Резистори 1% 0603:", [
            "• Будь-який постачальник з AVL (Yageo, Vishay, Panasonic)",
            "• Критерії: Footprint = 0603, P ≥ 100mW, Tol ≤ 1%, TCR ≤ 100ppm"
        ]),
        ("Керамічні конденсатори MLCC:", [
            "• ТІЛЬКИ з однаковим діелектриком (X7R ≥ X5R > Y5V заборонено)",
            "• Робоча напруга: V_rated ≥ V_original (запас на DC-bias)",
            "• Не змінювати 0603 на 0402 без перевірки падіння ємності!"
        ]),
        ("Індуктивності / Дроселі:", [
            "• Обов'язкова звірка струму насичення I_sat та опору DCR"
        ])
    ]

    ly = y0 + 56
    for title, lines in p_items:
        p.append(text(45, ly, title, size=10.5, bold=True, color="#1e40af", anchor="start"))
        ly += 17
        for ln in lines:
            p.append(text(50, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 16
        ly += 6

    # Права колонка: Активні ІС (Active ICs)
    p.append(rect(445, y0, col_w, h_box, fill="#f8fafc", stroke="#dc2626", sw=1.5, rx=8))
    p.append(rect(445, y0, col_w, 36, fill="#dc2626", stroke="#dc2626", sw=1.0, rx=8))
    p.append(text(445 + col_w/2, y0 + 24, "Активні мікросхеми (ІС / МК / Драйвери)", size=11.5, bold=True, color="#ffffff"))

    a_items = [
        ("Рівень 1: Drop-in Pin-to-Pin:", [
            "• Повний електричний і програмний клон",
            "• Приклад: лінійні стабілізатори 1117-3.3, пам'ять W25Q128"
        ]),
        ("Рівень 2: Pin-compatible (інша обв'язка):", [
            "• Однаковий корпус і цоколівка, але інша V_ref чи f_sw",
            "• Вимагає зміни номіналів резисторів зворотного зв'язку"
        ]),
        ("Рівень 3: Сумісний функціонал, інший футпрінт:", [
            "• Вимагає комбінованого посадкового місця на PCB (Dual Footprint)",
            "• Приклад: SOIC-8 поверх WSON-8 для Flash-пам'яті"
        ]),
        ("Рівень 4: Архітектурна заміна (інший чіп):", [
            "• Вимагає перерозведення плати (Rev B) та модифікації прошивки"
        ])
    ]

    ly = y0 + 56
    for title, lines in a_items:
        p.append(text(460, ly, title, size=10.5, bold=True, color="#991b1b", anchor="start"))
        ly += 17
        for ln in lines:
            p.append(text(465, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 16
        ly += 5

    render(os.path.join(OUT, "second-sourcing-matrix.svg"), W, H, *p)


# ── 4. revision-sync.svg ────────────────────────────────────────────────────
# Синхронізація ревізій плати, схеми, BOM, CPL та прошивки за процедурою ECO
def fig_revision_sync():
    W, H = 860, 370
    p = []
    p.append(text(W/2, 28, "Синхронізація ревізій: єдине джерело правди через ECO", size=15, bold=True))

    # Центральний блок ECO (Engineering Change Order)
    eco_cx, eco_cy = W/2, 175
    eco_w, eco_h = 175, 72
    p.append(rect(eco_cx - eco_w/2, eco_cy - eco_h/2, eco_w, eco_h, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(eco_cx, eco_cy - 9, "Повідомлення про зміни", size=11, bold=True, color="#92400e"))
    p.append(text(eco_cx, eco_cy + 9, "ECO #2026-084", size=12, bold=True, color="#b45309"))
    p.append(text(eco_cx, eco_cy + 24, "Rev A → Rev B", size=10, bold=True, color="#15803d"))

    # Чотири кутові сутності
    nodes = [
        ("Схема (Schematic)", "SCH-1002 Rev B\n(новий LDO + pull-up)", 150, 95, ACCENT, ACCENT_BG),
        ("Друкована плата (PCB)", "PCB-1002 Rev B\n(шовкографія Rev B)", 710, 95, FIELD, "#f0fdf4"),
        ("Специфікація (BOM)", "BOM-1002 Rev B\n(DNP на R12, MPN U2)", 150, 265, POS, "#fdf2f2"),
        ("Прошивка (Firmware)", "FW v2.1.0\n(читає Board ID Rev B)", 710, 265, PURPLE, PURPLE_BG),
    ]

    box_w, box_h = 200, 66
    for title, sub, nx, ny, stroke_c, fill_c in nodes:
        p.append(rect(nx - box_w/2, ny - box_h/2, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(nx, ny - 10, title, size=11, bold=True, color=stroke_c))
        lines = sub.split("\n")
        p.append(text(nx, ny + 8, lines[0], size=9.5, color=TEXT_DARK))
        p.append(text(nx, ny + 22, lines[1], size=9.5, color=MUTED, italic=True))

        # Стрілка від ECO до вузла
        p.append(arrow(eco_cx, eco_cy, nx, ny, color="#d97706", sw=1.6))

    # Пояснення знизу
    p.append(line(50, 325, 810, 325, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 348, "Правило цілісності: не можна змінити один файл без оновлення всієї зв'язки ревізій", size=10.5, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "revision-sync.svg"), W, H, *p)


# ── 5. packaging-feeders.svg ────────────────────────────────────────────────
# Порівняння фабричного пакування: Tape & Reel проти Cut Tape, Tube, Tray
def fig_packaging_feeders():
    W, H = 860, 360
    p = []
    p.append(text(W/2, 28, "Фабричне пакування компонентів для монтажу Pick & Place", size=15, bold=True))

    types = [
        ("Tape & Reel (Стрічка в котушці)", "#16a34a", "#f0fdf4", [
            "• Стандарт промислового монтажу (SMT)",
            "• Має лідер (30-50 см порожньої стрічки)",
            "• Автоматична безперервна подача у фідер",
            "• Відсутній ризик перевертання деталей"
        ], "ІДЕАЛЬНО ДЛЯ СЕРІЇ", "#15803d"),

        ("Cut Tape (Обрізок стрічки)", "#dc2626", "#fef2f2", [
            "• Немає лідера для заправки у фідер",
            "• Перші 5-15 деталей втрачаються (scrap)",
            "• Потребує наклеювання лідера вручну",
            "• Ризик заклинювання живильника"
        ], "ПРОБЛЕМА ДЛЯ АВТОМАТА", "#b91c1c"),

        ("Tray / Tube (Піддон / Пенал)", "#d97706", "#fffbeb", [
            "• Використовується для QFP, BGA, роз'ємів",
            "• Потребує спеціального фідер-трею",
            "• Менша швидкість захоплення соплом",
            "• Чутливі до вібрації під час подачі"
        ], "ДЛЯ ВЕЛИКИХ ІС ТА THT", "#b45309")
    ]

    card_w = 250
    card_h = 250
    gap = 26
    y0 = 65
    xs = [30, 30 + card_w + gap, 30 + 2 * (card_w + gap)]

    for cx, (head, stroke_c, fill_c, lines, badge, badge_c) in zip(xs, types):
        p.append(rect(cx, y0, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(cx + card_w/2, y0 + 24, head, size=11, bold=True, color=stroke_c))
        p.append(line(cx + 10, y0 + 36, cx + card_w - 10, y0 + 36, color=stroke_c, sw=1.0))

        ly = y0 + 62
        for ln in lines:
            p.append(text(cx + 12, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 23

        # Бейдж унизу
        p.append(rect(cx + 20, y0 + card_h - 44, card_w - 40, 28, fill="#ffffff", stroke=badge_c, sw=1.2, rx=4))
        p.append(text(cx + card_w/2, y0 + card_h - 26, badge, size=9.5, bold=True, color=badge_c))

    render(os.path.join(OUT, "packaging-feeders.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bom_row_anatomy()
    fig_mpn_suffix_trap()
    fig_second_sourcing_matrix()
    fig_revision_sync()
    fig_packaging_feeders()
    print("All 5 figures generated successfully in", OUT)
