# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up from root/hw/hw-arch/latentnist-pereryvannia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. timing-breakdown.svg ──────────────────────────────────────────────────
# Анатомія 12 тактів латентності Cortex-M3/M4 при 0 Wait States:
# Від фронту сигналу на GPIO до виконання першої інструкції в ISR.
def fig_timing_breakdown():
    W, H = 840, 360
    p = []

    # Заголовок / фонова панель
    p.append(rect(20, 20, 800, 320, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Смуга часової шкали
    axis_y = 270
    p.append(line(50, axis_y, 790, axis_y, color=LINE, sw=1.8))
    # Стрілка на кінці
    p.append(arrow(770, axis_y, 795, axis_y, color=LINE, sw=1.8))
    p.append(text(790, axis_y + 25, "Час (такти)", size=11, color=MUTED, anchor="end", italic=True))

    # Етапи латентності (колонки)
    # 1. Синхронізація (0..2 такт) - 2 такти
    # 2. Арбітраж NVIC (2..4 такт) - 2 такти
    # 3. Auto-stacking & Vector Fetch (4..10 такт) - 6 тактів
    # 4. Fetch & Decode ISR (10..12 такт) - 2 такти
    # Разом = 12 тактів
    stages = [
        (60, 160, 2, "Синхронізація GPIO\nі фільтрація входу", "#eaf0fd", NEG, "Такт 1–2 (2T)"),
        (230, 160, 2, "Пріоритезація та\nрішення NVIC", "#fff9e6", "#b08800", "Такт 3–4 (2T)"),
        (400, 240, 6, "Паралельний автостекінг (D-Bus)\nта вибірка вектора VTOR (I-Bus)", "#e6f4ea", FIELD, "Такт 5–10 (6T)"),
        (650, 130, 2, "Вибірка й декодування\nпершої інструкції ISR", "#fdecea", POS, "Такт 11–12 (2T)")
    ]

    for x, w_box, cycles, title, bg_col, stroke_col, t_label in stages:
        # Прямокутник етапу
        b, bw, bh = textbox(x + w_box / 2, 110, title, size=11, bold=True, pad=8,
                            fill=bg_col, stroke=stroke_col, sw=1.6, min_w=w_box - 10)
        p.append(b)

        # Вертикальні лінії прив'язки до осі
        p.append(line(x, 155, x, axis_y, color="#9ca3af", sw=1.2, dash="3,3"))
        p.append(line(x + w_box, 155, x + w_box, axis_y, color="#9ca3af", sw=1.2, dash="3,3"))

        # Позначка тактів під віссю
        tb, tbw, tbh = textbox(x + w_box / 2, 195, t_label, size=10, bold=True, pad=4,
                               fill="#ffffff", stroke=stroke_col, sw=1.2)
        p.append(tb)

        # Стрілка тривалості на осі
        p.append(line(x + 4, axis_y, x + w_box - 4, axis_y, color=stroke_col, sw=3.0))

    # Крайні мітки осі
    p.append(text(60, axis_y + 18, "0 (Фронт)", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(220, axis_y + 18, "2T", size=10, color=INK, anchor="middle"))
    p.append(text(390, axis_y + 18, "4T", size=10, color=INK, anchor="middle"))
    p.append(text(640, axis_y + 18, "10T", size=10, color=INK, anchor="middle"))
    p.append(text(780, axis_y + 18, "12T (ISR)", size=10, color=POS, anchor="middle", bold=True))

    # Загальний маркер
    p.append(rect(60, 40, 720, 30, fill="#f3f4f6", stroke="#4b5563", sw=1.4, rx=4))
    p.append(text(420, 60, "Базова апаратна латентність Cortex-M3/M4: рівно 12 тактів ядра при 0WS",
                  size=12, color=INK, anchor="middle", bold=True))

    render(os.path.join(OUT, "timing-breakdown.svg"), W, H, *p,
           title="Анатомія 12 тактів латентності переривання в ARM Cortex-M")


# ── 2. auto-stacking-frame.svg ───────────────────────────────────────────────
# Структура апаратного фрейму стека та паралельна робота шин коду й даних.
def fig_auto_stacking_frame():
    W, H = 820, 420
    p = []

    # Фонова панель
    p.append(rect(15, 15, 790, 390, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Ліва частина: Апаратний фрейм стека (8 слів / 32 байти)
    p.append(text(180, 45, "Апаратний стек-фрейм (Auto-stacking)", size=13, color=INK, bold=True))
    p.append(text(180, 65, "Зберігається апаратно до виклику C-обробника", size=11, color=MUTED))

    regs = [
        ("xPSR", "Прапорці стану процесора та вирівнювання", "#fdecea", POS),
        ("PC (R15)", "Адреса повернення (наступна інструкція)", "#fdecea", POS),
        ("LR (R14)", "Попереднє значення регістра зв'язку", "#fff9e6", "#b08800"),
        ("R12", "Внутрішньопроцедурний скретч-регістр IP", "#eaf0fd", NEG),
        ("R3", "Четвертий аргумент / результат функції", "#eaf0fd", NEG),
        ("R2", "Третій аргумент функції", "#eaf0fd", NEG),
        ("R1", "Другий аргумент функції", "#eaf0fd", NEG),
        ("R0", "Перший аргумент / повернене значення", "#eaf0fd", NEG),
    ]

    start_y = 85
    row_h = 32
    for i, (reg, desc, bg, stroke_c) in enumerate(regs):
        y = start_y + i * row_h
        # Позначка адреси стека
        offset = "+%d" % ((7 - i) * 4) if (7 - i) > 0 else "SP (новий)"
        p.append(text(45, y + 20, offset, size=10, color=MUTED, anchor="start"))
        # Комірка регістра
        p.append(rect(115, y, 70, row_h - 4, fill=bg, stroke=stroke_c, sw=1.5, rx=4))
        p.append(text(150, y + 19, reg, size=11, color=INK, bold=True))
        # Опис призначення
        p.append(text(195, y + 19, desc, size=10, color="#374151", anchor="start"))

    # Позначка розміру фрейму
    p.append(line(100, start_y, 100, start_y + 8 * row_h - 4, color=LINE, sw=1.5))
    p.append(line(95, start_y, 105, start_y, color=LINE, sw=1.5))
    p.append(line(95, start_y + 8 * row_h - 4, 105, start_y + 8 * row_h - 4, color=LINE, sw=1.5))
    p.append(text(90, start_y + 4 * row_h, "32 байти\n(8 слів)", size=10, color=LINE, anchor="end", bold=True))

    # Права частина: Паралелізм шин I-Bus та D-Bus
    p.append(text(600, 45, "Паралельний доступ до шин", size=13, color=INK, bold=True))
    p.append(text(600, 65, "Гарвардська структура усуває шинний затор", size=11, color=MUTED))

    # Блок ядра NVIC/CPU
    core_box, _, _ = textbox(600, 120, "Ядро Cortex-M\nКонтролер винятків NVIC", size=11, bold=True,
                             fill="#f3f4f6", stroke="#4b5563", sw=1.8, pad=10)
    p.append(core_box)

    # Дві шини: D-Bus і I-Bus
    # D-Bus (вниз до RAM)
    p.append(line(520, 155, 520, 240, color=NEG, sw=2.0))
    p.append(arrow(520, 240, 520, 260, color=NEG, sw=2.0))
    p.append(text(460, 205, "Шина D-Bus\n(запис 8 регістрів)", size=10, color=NEG, anchor="middle", bold=True))

    ram_box, _, _ = textbox(520, 290, "SRAM (Пам'ять даних)\nЗбереження стек-фрейму", size=10, bold=True,
                            fill="#eaf0fd", stroke=NEG, sw=1.5, pad=8)
    p.append(ram_box)

    # I-Bus (вправо/вниз до Flash/VTOR)
    p.append(line(680, 155, 680, 240, color=FIELD, sw=2.0))
    p.append(arrow(680, 240, 680, 260, color=FIELD, sw=2.0))
    p.append(text(740, 205, "Шина I-Bus / Code\n(вибірка вектора)", size=10, color=FIELD, anchor="middle", bold=True))

    flash_box, _, _ = textbox(680, 290, "Flash / VTOR Table\nЗчитування адреси ISR", size=10, bold=True,
                              fill="#e6f4ea", stroke=FIELD, sw=1.5, pad=8)
    p.append(flash_box)

    # Висновок внизу
    p.append(rect(450, 350, 330, 42, fill="#fff9e6", stroke="#e0a800", sw=1.4, rx=6))
    p.append(text(615, 375, "Auto-stacking у RAM і Vector Fetch із Flash\nвиконуються ОДНОЧАСНО за 12 тактів",
                  size=10, color=INK, anchor="middle", bold=True))

    render(os.path.join(OUT, "auto-stacking-frame.svg"), W, H, *p,
           title="Апаратний стек-фрейм та одночасний доступ до шин даних і коду")


# ── 3. tail-chaining-late-arrival.svg ─────────────────────────────────────────
# Порівняння: Звичайний послідовний вхід/вихід vs Tail-Chaining vs Late Arrival.
def fig_tail_chaining_late_arrival():
    W, H = 840, 420
    p = []

    p.append(rect(15, 15, 810, 390, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Заголовок
    p.append(text(420, 40, "Апаратні оптимізації NVIC: Tail-Chaining та Late Arrival", size=13, color=INK, bold=True))

    # Сценарій 1: Без оптимізації (Повний вихід і повторний вхід = 24 такти)
    y1 = 80
    p.append(text(30, y1 + 18, "1. Без оптимізації:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(160, y1, 150, 32, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(235, y1 + 20, "Виконання ISR 1", size=10, color=NEG, bold=True))

    p.append(rect(315, y1, 140, 32, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(385, y1 + 20, "Unstacking (12T)", size=10, color=POS, bold=True))

    p.append(rect(460, y1, 140, 32, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(530, y1 + 20, "Stacking (12T)", size=10, color=POS, bold=True))

    p.append(rect(605, y1, 150, 32, fill="#e6f4ea", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(680, y1 + 20, "Виконання ISR 2", size=10, color=FIELD, bold=True))

    p.append(text(765, y1 + 20, "Втрата: 24T", size=10, color=POS, anchor="start", bold=True))

    # Сценарій 2: Tail-Chaining (Зчеплення хвостів = лише 6 тактів!)
    y2 = 160
    p.append(text(30, y2 + 18, "2. Tail-Chaining:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(160, y2, 150, 32, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(235, y2 + 20, "Виконання ISR 1", size=10, color=NEG, bold=True))

    # Блок зчеплення 6 тактів
    p.append(rect(315, y2, 110, 32, fill="#fff9e6", stroke="#e0a800", sw=2.0, rx=4))
    p.append(text(370, y2 + 20, "Tail-Chain (6T)", size=10, color="#b08800", bold=True))

    p.append(rect(430, y2, 150, 32, fill="#e6f4ea", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(505, y2 + 20, "Виконання ISR 2", size=10, color=FIELD, bold=True))

    p.append(text(590, y2 + 20, "Заощаджено 18 тактів! (Без unstack/restack)", size=10, color=FIELD, anchor="start", bold=True))

    # Сценарій 3: Late Arrival (Пізнє прибуття вищого пріоритету)
    y3 = 260
    p.append(text(30, y3 + 18, "3. Late Arrival:", size=11, color=INK, anchor="start", bold=True))

    # Початок стекінгу для ISR_Low
    p.append(rect(160, y3, 110, 32, fill="#f3f4f6", stroke="#6b7280", sw=1.4, rx=4))
    p.append(text(215, y3 + 20, "Stacking (0..4T)", size=10, color=INK))

    # Момент приходу High Priority
    p.append(line(270, y3 - 20, 270, y3 + 45, color=POS, sw=2.0, dash="3,3"))
    p.append(text(270, y3 - 25, "Прибув High-IRQ!", size=10, color=POS, bold=True))

    # Продовження стекінгу + підміна вектора
    p.append(rect(275, y3, 140, 32, fill="#fff9e6", stroke=POS, sw=1.8, rx=4))
    p.append(text(345, y3 + 20, "Підміна вектора VTOR", size=10, color=POS, bold=True))

    # Виконання термінового ISR High
    p.append(rect(420, y3, 150, 32, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(495, y3 + 20, "Виконання ISR High", size=10, color=POS, bold=True))

    # Tail chain до відкладеного ISR Low
    p.append(rect(575, y3, 90, 32, fill="#fff9e6", stroke="#e0a800", sw=1.6, rx=4))
    p.append(text(620, y3 + 20, "Tail-Chain (6T)", size=9, color="#b08800", bold=True))

    p.append(rect(670, y3, 120, 32, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(730, y3 + 20, "ISR Low", size=10, color=NEG, bold=True))

    # Пояснення внизу
    p.append(rect(30, 345, 760, 45, fill="#f9fafb", stroke="#9ca3af", sw=1.2, rx=6))
    p.append(text(410, 365, "NVIC динамічно оптимізує чергу переривань: жодного зайвого такту на перепаковування стек-фрейму",
                  size=11, color=INK, anchor="middle", bold=True))
    p.append(text(410, 380, "Late Arrival гарантує найвищому пріоритету стабільні 12 тактів реакції навіть при раптовому виникненні",
                  size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "tail-chaining-late-arrival.svg"), W, H, *p,
           title="Механізми Tail-Chaining та Late Arrival у контролері NVIC")


# ── 4. latency-jitter-sources.svg ────────────────────────────────────────────
# Джерела збільшення латентності та виникнення джитера у реальному мікроконтролері.
def fig_latency_jitter_sources():
    W, H = 820, 380
    p = []

    p.append(rect(15, 15, 790, 350, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    p.append(text(410, 42, "Джерела збільшення латентності та джитера (Jitter)", size=13, color=INK, bold=True))
    p.append(text(410, 62, "Чому реальна затримка може перевищувати теоретичні 12 тактів", size=11, color=MUTED))

    # 4 основні фактори
    factors = [
        (40, 95, 340, 95, "Flash Wait States & I-Cache Miss",
         "При роботі на високих частотах (наприклад, 168 МГц)\nFlash вимагає до 5 циклів очікування (WS).\nПромах кешу інструкцій додає 3–6 тактів на вибірку вектора.",
         "#eaf0fd", NEG),

        (420, 95, 360, 95, "Багатотактові неподільні інструкції",
         "Інструкції LDRD/STRD або UDIV/SDIV (до 12 тактів)\nне можуть бути перервані миттєво на деяких ядрах,\nщо змушує NVIC чекати завершення виконання команди.",
         "#fff9e6", "#b08800"),

        (40, 215, 340, 95, "Критичні секції (CPSID / BASEPRI)",
         "Програмне блокування переривань макросом __disable_irq()\nабо підняттям порогу BASEPRI у драйверах RTOS\nвідкладає реакцію на весь час виконання захищеного коду.",
         "#fdecea", POS),

        (420, 215, 360, 95, "FPU Lazy Stacking & Шинні колізії",
         "Збереження 16 регістрів FPU (s0–s15) додає затримку,\nякщо в ISR використовується float-арифметика.\nDMA та ядро можуть змагатися за доступ до шинної матриці.",
         "#e6f4ea", FIELD)
    ]

    for x, y, w_box, h_box, title, desc, bg, stroke_c in factors:
        p.append(rect(x, y, w_box, h_box, fill=bg, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(x + 12, y + 22, title, size=11, color=stroke_c, anchor="start", bold=True))
        p.append(mtext(x + 12, y + 42, desc, size=10, color=INK, anchor="start", lh=1.35))

    p.append(rect(40, 325, 740, 30, fill="#f3f4f6", stroke="#4b5563", sw=1.2, rx=4))
    p.append(text(410, 344, "Підсумок: Найгірший час реакції (WCET) = 12T + Flash_WS + Long_Inst + Critical_Section",
                  size=11, color=INK, anchor="middle", bold=True))

    render(os.path.join(OUT, "latency-jitter-sources.svg"), W, H, *p,
           title="Чинники збільшення латентності переривань та джитера в мікроконтролерах")


if __name__ == "__main__":
    fig_timing_breakdown()
    fig_auto_stacking_frame()
    fig_tail_chaining_late_arrival()
    fig_latency_jitter_sources()
    print("All figures generated successfully.")
