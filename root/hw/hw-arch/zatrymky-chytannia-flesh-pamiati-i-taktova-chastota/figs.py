# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d, color=LINE, sw=1.5, fill="none"):
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"/>'


# ── 1. flash-access-timing: Часові діаграми 16 МГц (0WS) та 168 МГц (5WS) ──
def fig_flash_access_timing():
    W, H = 840, 390
    p = []

    # Заголовок
    p.append(text(420, 24, "Часові діаграми доступу до Flash: 16 МГц (0WS) проти 168 МГц (5WS)", size=14, bold=True))

    # ── Секція 16 МГц ──
    p.append(rect(40, 42, 760, 140, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(60, 64, "Режим 16 МГц (HSI / старт): T_clk = 62.5 нс ≥ 30 нс (0 Wait States, 1 такт)", size=12, color=NEG, bold=True, anchor="start"))

    # Тактовий сигнал 16 МГц
    p.append(text(120, 95, "CLK (16 МГц)", size=11, color=MUTED, anchor="end"))
    clk1_path = "M 140,105 L 140,80 L 320,80 L 320,105 L 500,105 L 500,80 L 680,80 L 680,105"
    p.append(svg_path(clk1_path, color=NEG, sw=2.0))
    p.append(text(230, 75, "Такт 1 (62.5 нс)", size=10, color=NEG))

    # Смуга Flash Access Time (30 нс)
    p.append(text(120, 135, "Flash матриця", size=11, color=MUTED, anchor="end"))
    p.append(rect(140, 120, 175, 26, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    p.append(text(227, 137, "Час доступу матриці (30 нс)", size=10, color="#9a3412", bold=True))

    # Смуга валідних даних
    p.append(rect(315, 120, 185, 26, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(407, 137, "Дані валідні (0WS — за 1 такт)", size=10, color="#14532d", bold=True))
    p.append(line(500, 75, 500, 155, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(text(508, 148, "Захоплення ядром", size=9, color=FIELD, anchor="start", italic=True))

    # ── Секція 168 МГц ──
    p.append(rect(40, 195, 760, 175, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(60, 218, "Режим 168 МГц (PLL): T_clk = 5.95 нс < 30 нс (Потрібно 5WS Latency, разом 6 тактів = 35.7 нс)", size=12, color=POS, bold=True, anchor="start"))

    p.append(text(120, 250, "CLK (168 МГц)", size=11, color=MUTED, anchor="end"))

    # 6 тактів по 55 px
    step = 55
    x0 = 140
    clk_pts = [f"M {x0},260"]
    for i in range(6):
        cur_x = x0 + i * step
        clk_pts.append(f"L {cur_x},235 L {cur_x + step/2},235 L {cur_x + step/2},260 L {cur_x + step},260")
        label = "T1" if i == 0 else (f"WS{i}" if i < 5 else "T6 (Data)")
        col = NEG if i == 0 else (POS if i < 5 else FIELD)
        p.append(text(cur_x + step/2, 230, label, size=9, color=col, bold=True))
        p.append(line(cur_x + step, 230, cur_x + step, 345, color="#cbd5e1", sw=1.0, dash="2,2"))

    p.append(svg_path(" ".join(clk_pts), color=LINE, sw=1.8))

    # Flash Matrix Access Time (30 нс) розтягнуто на 5.04 тактів (≈ 278 px)
    p.append(text(120, 295, "Flash матриця", size=11, color=MUTED, anchor="end"))
    p.append(rect(x0, 280, 280, 26, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    p.append(text(x0 + 140, 297, "Фізичний час доступу Flash-матриці (~30 нс)", size=10, color="#9a3412", bold=True))

    # Смуга готовності на 6-му такті
    p.append(rect(x0 + 280, 280, step * 6 - 280, 26, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(x0 + 305, 297, "Дані валідні", size=10, color="#14532d", bold=True))

    p.append(text(x0 + 165, 335, "← 5 тактів очікування шини (Wait States / LATENCY = 5 у FLASH_ACR) →", size=11, color=POS, bold=True))
    p.append(line(x0 + step * 6, 230, x0 + step * 6, 345, color=FIELD, sw=1.8))
    p.append(text(x0 + step * 6 + 8, 335, "Захоплення на 6-му такті", size=10, color=FIELD, anchor="start", italic=True))

    render(os.path.join(OUT, "flash-access-timing.svg"), W, H, *p,
           title="Часові діаграми доступу до Flash: 16 МГц та 168 МГц")


# ── 2. art-accelerator-block: Блок-схема прискорювача Flash та кешу ──
def fig_art_accelerator_block():
    W, H = 840, 440
    p = []

    p.append(text(420, 22, "Архітектура прискорювача Flash: буфер Prefetch, I-Cache та D-Cache (ART)", size=14, bold=True))

    # Блок Flash матриці ліворуч
    b_flash, w_f, h_f = textbox(130, 210, "Масив Flash\n(Embedded NOR)\n128-бітне слово\n+ 8 біт ECC\n(Час доступу ~30 нс)",
                                size=11, bold=True, fill="#fff7ed", stroke="#ea580c", sw=2.0, pad=12)
    p.append(b_flash)

    # Контролер доступу до Flash
    p.append(rect(240, 48, 340, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, 70, "Контролер Flash (FLASH_ACR / Прискорювач ART)", size=12, color=NEG, bold=True))

    # Буфер Prefetch
    b_pref, wp, hp = textbox(410, 115, "Буфер попередньої вибірки (Prefetch Buffer)\n128 біт (4 інструкції Thumb-2 / 8 x 16-біт)",
                             size=10, bold=True, fill="#e0f2fe", stroke="#0284c7", sw=1.5, pad=8)
    p.append(b_pref)

    # I-Cache (Кеш інструкцій)
    b_icache, wi, hi = textbox(410, 205, "Кеш інструкцій (Instruction Cache)\n64 рядки x 128 біт (1 Кбайт)\nПовний асоціативний пошук за тегом (0WS Hit)",
                               size=10, bold=True, fill="#dcfce7", stroke=FIELD, sw=1.5, pad=8)
    p.append(b_icache)

    # D-Cache (Кеш літералів / констант)
    b_dcache, wd, hd = textbox(410, 295, "Кеш даних / літералів (Data Cache)\n8 рядків x 128 біт (128 байтів)\nТаблиці переходів, константи пулу (0WS Hit)",
                               size=10, bold=True, fill="#fef3c7", stroke="#d97706", sw=1.5, pad=8)
    p.append(b_dcache)

    # Регістр керування FLASH_ACR
    b_acr, wa, ha = textbox(410, 375, "Регістр керування FLASH_ACR (LATENCY, PRFTEN, ICEN, DCEN)",
                            size=9, bold=True, fill="#ede9fe", stroke="#7c3aed", sw=1.2, pad=6)
    p.append(b_acr)

    # Лінії від Flash до блоків контролера
    p.append(line(195, 170, 275, 115, color="#ea580c", sw=2.0))
    p.append(line(195, 210, 275, 205, color="#ea580c", sw=2.0))
    p.append(line(195, 250, 275, 295, color="#ea580c", sw=2.0))
    p.append(text(235, 155, "128 біт", size=9, color="#ea580c", bold=True))

    # Блок ядра та шинної матриці праворуч
    p.append(rect(650, 48, 150, 360, fill="#f1f5f9", stroke=NEG, sw=1.8, rx=8))
    p.append(text(725, 75, "Шинна матриця\nта Ядро Cortex-M", size=12, color=NEG, bold=True))

    b_icode, _, _ = textbox(725, 160, "I-Code Bus\n(32 біти)\nВибірка коду", size=10, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    p.append(b_icode)

    b_dcode, _, _ = textbox(725, 290, "D-Code Bus\n(32 біти)\nКонстанти/літерали", size=10, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    p.append(b_dcode)

    # З'єднання між контролером та шинами
    p.append(line(545, 115, 665, 150, color=NEG, sw=1.8))
    p.append(line(545, 205, 665, 165, color=FIELD, sw=2.0))
    p.append(text(605, 175, "32 біти (0WS)", size=9, color=FIELD, bold=True))

    p.append(line(545, 295, 665, 290, color="#d97706", sw=1.8))
    p.append(text(605, 305, "32 біти (0WS)", size=9, color="#d97706", bold=True))

    render(os.path.join(OUT, "art-accelerator-block.svg"), W, H, *p,
           title="Архітектура апаратного прискорювача Flash та кешу")


# ── 3. flash-vs-ram-execution: Порівняння конвеєра Flash та RAM ──
def fig_flash_vs_ram_execution():
    W, H = 840, 380
    p = []

    p.append(text(420, 22, "Виконання інструкцій: Flash без кешу, Flash з ART та виконання з RAM", size=14, bold=True))

    # Секція 1: Flash 5WS без кешу (Stall bubbles)
    p.append(rect(40, 42, 760, 95, fill="#fff1f2", stroke=POS, sw=1.2, rx=6))
    p.append(text(60, 62, "1. Flash 5WS без кешу / Prefetch (IPC ≈ 0.17 — величезні затримки конвеєра)", size=11, color=POS, bold=True, anchor="start"))

    boxes_s1 = [
        (160, "Fetch #1\n(6 тактів: 5WS)", POS, "#fecdd3"),
        (260, "Dec\n(1 такт)", INK, "#ffffff"),
        (330, "Exec\n(1 такт)", INK, "#ffffff"),
        (430, "Fetch #2\n(6 тактів: 5WS)", POS, "#fecdd3"),
        (530, "Dec\n(1 такт)", INK, "#ffffff"),
        (600, "Exec\n(1 такт)", INK, "#ffffff"),
        (700, "Fetch #3\n(6 тактів)", POS, "#fecdd3")
    ]
    for cx, lbl, col, fl in boxes_s1:
        b, bw, bh = textbox(cx, 98, lbl, size=9, bold=True, fill=fl, stroke=col, sw=1.2, pad=4)
        p.append(b)

    # Секція 2: Flash 5WS з Prefetch та кешем ART
    p.append(rect(40, 148, 760, 105, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(60, 168, "2. Flash 5WS з Prefetch + ART Cache (0WS Equivalent при попаданні в кеш; штраф лише при переході)", size=11, color="#15803d", bold=True, anchor="start"))

    boxes_s2 = [
        (120, "F1 (0WS)", FIELD, "#dcfce7"),
        (180, "F2 (0WS)", FIELD, "#dcfce7"),
        (240, "F3 (0WS)", FIELD, "#dcfce7"),
        (300, "F4 (0WS)", FIELD, "#dcfce7"),
        (385, "Branch (Промах)\n5WS штраф", POS, "#fee2e2"),
        (480, "F_tgt\n(6 тактів)", POS, "#fee2e2"),
        (560, "F_loop (0WS)", FIELD, "#dcfce7"),
        (640, "F_loop (0WS)", FIELD, "#dcfce7"),
        (720, "F_loop (0WS)", FIELD, "#dcfce7")
    ]
    for cx, lbl, col, fl in boxes_s2:
        b, bw, bh = textbox(cx, 212, lbl, size=9, bold=True, fill=fl, stroke=col, sw=1.2, pad=4)
        p.append(b)

    # Секція 3: Виконання з RAM (SRAM / CCMRAM)
    p.append(rect(40, 265, 760, 95, fill="#f8fafc", stroke=NEG, sw=1.2, rx=6))
    p.append(text(60, 285, "3. Виконання з RAM (.ramfunc / CCMRAM / SRAM) — абсолютний детермінізм, 0WS завжди", size=11, color=NEG, bold=True, anchor="start"))

    boxes_s3 = [
        (110, "F1 (1 такт)", NEG, "#e0f2fe"),
        (175, "F2 (1 такт)", NEG, "#e0f2fe"),
        (240, "F3 (1 такт)", NEG, "#e0f2fe"),
        (305, "Branch", INK, "#ffffff"),
        (375, "F_tgt (1 такт)", NEG, "#e0f2fe"),
        (445, "F_isr1", NEG, "#e0f2fe"),
        (515, "F_isr2", NEG, "#e0f2fe"),
        (585, "F_isr3", NEG, "#e0f2fe"),
        (665, "Zero Jitter\n0WS детермінізм", FIELD, "#dcfce7")
    ]
    for cx, lbl, col, fl in boxes_s3:
        b, bw, bh = textbox(cx, 322, lbl, size=9, bold=True, fill=fl, stroke=col, sw=1.2, pad=4)
        p.append(b)

    render(os.path.join(OUT, "flash-vs-ram-execution.svg"), W, H, *p,
           title="Порівняння конвеєра: Flash без кешу, Flash з ART та RAM")


# ── 4. frequency-scaling-order: Порядок зміни частоти та затримок ──
def fig_frequency_scaling_order():
    W, H = 840, 480
    p = []

    p.append(text(420, 22, "Безпечний порядок зміни тактової частоти та затримок Flash Latency", size=14, bold=True))

    # Ліва колонка: Розгін частоти (Clock Increase)
    p.append(rect(40, 48, 360, 360, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(220, 72, "Підвищення частоти (Розгін)", size=13, color=NEG, bold=True))
    p.append(text(220, 90, "16 МГц → 168 МГц (Збільшення затримки СПЕРШУ)", size=10, color=MUTED, italic=True))

    inc_steps = [
        (220, 130, "1. Збільшити затримку Flash\nFLASH_ACR.LATENCY = 5WS", "#1d4ed8", "#dbeafe"),
        (220, 195, "2. Перевірити запис у FLASH_ACR\n(Цикл очікування фіксації бітів)", "#1d4ed8", "#dbeafe"),
        (220, 260, "3. Налаштувати й запустити PLL\n(Очікування прапорця PLLRDY == 1)", "#1d4ed8", "#dbeafe"),
        (220, 335, "4. Перемкнути системний такт на PLL\nRCC_CFGR.SW = PLL (Очікування SWS)", "#166534", "#dcfce7")
    ]
    for cx, cy, lbl, st, fl in inc_steps:
        b, bw, bh = textbox(cx, cy, lbl, size=10, bold=True, fill=fl, stroke=st, sw=1.4, pad=7)
        p.append(b)
        if cy < 300:
            p.append(line(cx, cy + bh/2, cx, cy + 35, color=NEG, sw=1.5))

    # Права колонка: Зниження частоти (Clock Decrease)
    p.append(rect(440, 48, 360, 360, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=8))
    p.append(text(620, 72, "Зниження частоти (Гальмування)", size=13, color="#9333ea", bold=True))
    p.append(text(620, 90, "168 МГц → 16 МГц (Зменшення затримки НАПРИКІНЦІ)", size=10, color=MUTED, italic=True))

    dec_steps = [
        (620, 130, "1. Перемкнути такт на HSI / HSE\nRCC_CFGR.SW = HSI (Очікування SWS)", "#7e22ce", "#f3e8ff"),
        (620, 195, "2. Вимкнути або переналаштувати PLL\nRCC_CR.PLLON = 0", "#7e22ce", "#f3e8ff"),
        (620, 260, "3. Зменшити затримку Flash\nFLASH_ACR.LATENCY = 0WS", "#7e22ce", "#f3e8ff"),
        (620, 335, "4. Перевірити запис у FLASH_ACR\n(Фіксація 0WS для низької частоти)", "#166534", "#dcfce7")
    ]
    for cx, cy, lbl, st, fl in dec_steps:
        b, bw, bh = textbox(cx, cy, lbl, size=10, bold=True, fill=fl, stroke=st, sw=1.4, pad=7)
        p.append(b)
        if cy < 300:
            p.append(line(cx, cy + bh/2, cx, cy + 35, color="#9333ea", sw=1.5))

    # Попереджувальний банер унизу
    p.append(rect(40, 420, 760, 48, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(420, 442, "Критичне правило: Перемикання частоти без завчасного налаштування Flash Latency", size=11, color=POS, bold=True))
    p.append(text(420, 458, "спричиняє зчитування спотворених кодів інструкцій та миттєвий апаратний збій (HardFault / BusFault)!", size=10, color="#991b1b"))

    render(os.path.join(OUT, "frequency-scaling-order.svg"), W, H, *p,
           title="Безпечний порядок зміни тактової частоти та затримок Flash")


if __name__ == "__main__":
    fig_flash_access_timing()
    fig_art_accelerator_block()
    fig_flash_vs_ram_execution()
    fig_frequency_scaling_order()
    print("All figures generated successfully.")
