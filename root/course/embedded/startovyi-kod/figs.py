# -*- coding: utf-8 -*-
"""Фігури для статті startovyi-kod («Стартовий код: від Reset_Handler до main»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. startup-timeline: Послідовність запуску від скидання до main ─────────
def fig_startup_timeline():
    W, H = 880, 260
    p = []

    # Ланцюжок 6 кроків
    steps = [
        ("1. Reset & Вектори", "Читання SP з 0x00\nі PC з 0x04 (Thumb)", POS),
        ("2. Reset_Handler", "Вхід у C-код\nініціалізації", INK),
        ("3. Пам'ять C", "Копіювання .data\nЗанулення .bss", FIELD),
        ("4. Апаратне залізо", "SystemInit()\nУвімкнення FPU", NEG),
        ("5. C++ рантайм", "__libc_init_array\nКонструктори об'єктів", INK),
        ("6. main() & Trap", "Основна програма\nПастка при виході", POS),
    ]

    n = len(steps)
    box_w = 120
    gap = 24
    total_w = n * box_w + (n - 1) * gap
    start_x = (W - total_w) / 2.0 + box_w / 2.0
    cy = 100

    for i, (title, sub, color) in enumerate(steps):
        cx = start_x + i * (box_w + gap)
        
        # Рамка для кроку
        fill_col = "#fdf2f2" if color == POS else ("#eafaf0" if color == FIELD else ("#eff6ff" if color == NEG else FILL))
        stroke_col = color if color != INK else LINE
        
        b, bw, bh = textbox(cx, cy, f"{title}\n{sub}", size=11, pad=8, min_w=box_w,
                            fill=fill_col, stroke=stroke_col, sw=1.5, color=INK, bold=False)
        p.append(b)

        # Стрілка між кроками
        if i < n - 1:
            ax1 = cx + box_w / 2.0 + 2
            ax2 = cx + box_w / 2.0 + gap - 2
            p.append(arrow(ax1, cy, ax2, cy, color=LINE, sw=1.5))

    # Нижній пояснювальний коментар
    b_bot, _, _ = textbox(W / 2.0, 205,
                          "Апаратний секвенсер ядра ARM Cortex-M виконує крок 1 автоматично.\n"
                          "Кроки 2–5 виконує стартовий код (crt0 / startup.c) до передачі керування в main().",
                          size=11, pad=8, fill="#fcfcfc", stroke="#d1d5db", sw=1.0, color=MUTED)
    p.append(b_bot)

    render(os.path.join(OUT, "startup-timeline.svg"), W, H, *p)


# ── 2. cortex-vector-table: Анатомія векторної таблиці ARM Cortex-M ─────────
def fig_cortex_vector_table():
    W, H = 880, 430
    p = []

    # Таблиця зліва: Flash пам'ять векторів
    tx = 160
    ty = 40
    row_h = 32
    col1_w = 110
    col2_w = 170

    entries = [
        ("0x0000 0000", "Initial MSP (0x20020000)", "#fee2e2", POS),
        ("0x0000 0004", "Reset_Handler (0x0800018D)", "#e0e7ff", NEG),
        ("0x0000 0008", "NMI_Handler", FILL, INK),
        ("0x0000 000C", "HardFault_Handler", FILL, INK),
        ("0x0000 0010", "MemManage_Handler", FILL, INK),
        ("0x0000 0014", "BusFault_Handler", FILL, INK),
        ("0x0000 0018", "UsageFault_Handler", FILL, INK),
        ("0x0000 002C", "SVCall_Handler", FILL, INK),
        ("0x0000 0038", "PendSV_Handler", FILL, INK),
        ("0x0000 003C", "SysTick_Handler", FILL, INK),
        ("0x0000 0040+", "Периферійні IRQ 0..N", "#f0fdf4", FIELD),
    ]

    p.append(text(tx + (col1_w + col2_w) / 2.0 - 50, ty - 14, "Векторна таблиця (.isr_vector у Flash)",
                  size=12, bold=True, color=INK))

    for i, (addr, name, fcol, scol) in enumerate(entries):
        y = ty + i * row_h
        # Колонка адреси
        p.append(rect(tx - 50, y, col1_w, row_h - 2, fill="#ffffff", stroke="#9ca3af", sw=1.0, rx=2))
        p.append(text(tx - 50 + col1_w / 2.0, y + row_h / 2.0 + 2, addr, size=11, color=MUTED))
        # Колонка вектора
        p.append(rect(tx - 50 + col1_w + 4, y, col2_w, row_h - 2, fill=fcol, stroke=scol if scol != INK else "#9ca3af", sw=1.2, rx=2))
        p.append(text(tx - 50 + col1_w + 4 + col2_w / 2.0, y + row_h / 2.0 + 2, name, size=11, bold=(i < 2), color=scol if scol != INK else INK))

    # Праві пояснювальні блоки зі стрілками
    # 1. Пояснення Initial MSP
    b1, bw1, bh1 = textbox(590, 56,
                           "Апаратне завантаження в регістр SP (MSP):\n"
                           "Вказує на кінець виділеної RAM (_estack).\n"
                           "Стек готовий ще ДО першої інструкції коду.",
                           size=11, pad=8, fill="#fff1f2", stroke=POS, sw=1.4)
    p.append(b1)
    p.append(arrow(tx - 50 + col1_w + 4 + col2_w + 4, ty + row_h / 2.0, 590 - bw1 / 2.0 - 4, 56, color=POS, sw=1.5))

    # 2. Пояснення Reset_Handler і Thumb bit
    b2, bw2, bh2 = textbox(590, 160,
                           "Завантаження адреси точки входу в регістр PC:\n"
                           "Зверніть увагу на LSB: адреса 0x0800018D є непарною!\n"
                           "Біт 0 = 1 перемикає ядро в режим Thumb-2.\n"
                           "Якщо біт 0 = 0 → негайний UsageFault (INVSTATE).",
                           size=11, pad=8, fill="#eef2ff", stroke=NEG, sw=1.4)
    p.append(b2)
    p.append(arrow(tx - 50 + col1_w + 4 + col2_w + 4, ty + row_h + row_h / 2.0, 590 - bw2 / 2.0 - 4, 160, color=NEG, sw=1.5))

    # 3. Релокація через VTOR
    b3, bw3, bh3 = textbox(590, 310,
                           "Регістр SCB->VTOR (Vector Table Offset):\n"
                           "Дозволяє перенести таблицю векторів у RAM\n"
                           "або іншу область Flash (актуально для Bootloader).\n"
                           "Вимога: адреса має бути вирівняна по ступеню двійки.",
                           size=11, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.4)
    p.append(b3)
    p.append(arrow(tx - 50 + col1_w + 4 + col2_w + 4, ty + 10 * row_h + row_h / 2.0, 590 - bw3 / 2.0 - 4, 310, color=FIELD, sw=1.5))

    render(os.path.join(OUT, "cortex-vector-table.svg"), W, H, *p)


# ── 3. flash-to-ram-relocation: LMA vs VMA розгортання .data та .bss ────────
def fig_flash_to_ram_relocation():
    W, H = 880, 420
    p = []

    # Блок Flash (LMA) зліва
    fx = 140
    fw = 190
    p.append(text(fx, 30, "FLASH (LMA — у прошивці)", size=13, bold=True, color=INK))

    flash_sections = [
        (".isr_vector (Вектори)", 45, "#e5e7eb", INK),
        (".text (Машинний код)", 75, "#e0e7ff", NEG),
        (".rodata (Константи)", 45, "#f3e8ff", "#7e22ce"),
        (".init_array (Конструктори)", 45, "#fef3c7", "#b45309"),
        (".data (Початкові дані)", 65, "#fee2e2", POS),
    ]

    fy = 50
    for name, h, fcol, scol in flash_sections:
        p.append(rect(fx - fw / 2.0, fy, fw, h, fill=fcol, stroke=scol if scol != INK else "#6b7280", sw=1.5, rx=3))
        p.append(text(fx, fy + h / 2.0 + 4, name, size=11, bold=True, color=scol if scol != INK else INK))
        fy += h + 4

    p.append(text(fx + fw / 2.0 + 8, 50 + 45 + 75 + 45 + 45 + 32, "_sidata", size=11, color=POS, bold=True, anchor="start"))

    # Блок RAM (VMA) справа
    rx = 740
    rw = 190
    p.append(text(rx, 30, "RAM (VMA — адреса виконання)", size=13, bold=True, color=INK))

    ram_sections = [
        (".data (Змінні в RAM)", 65, "#fee2e2", POS, "_sdata", "_edata"),
        (".bss (Занулені змінні)", 65, "#dcfce7", FIELD, "_sbss", "_ebss"),
        ("Heap (Динамічна пам'ять ↑)", 60, FILL, MUTED, "_end", ""),
        ("Stack (Стек викликів ↓)", 65, "#fef2f2", POS, "", "_estack"),
    ]

    ry = 50
    for name, h, fcol, scol, s_sym, e_sym in ram_sections:
        p.append(rect(rx - rw / 2.0, ry, rw, h, fill=fcol, stroke=scol if scol != INK else "#6b7280", sw=1.5, rx=3))
        p.append(text(rx, ry + h / 2.0 + 4, name, size=11, bold=True, color=scol if scol != INK else INK))
        if s_sym:
            p.append(text(rx - rw / 2.0 - 8, ry + 12, s_sym, size=11, color=scol, bold=True, anchor="end"))
        if e_sym:
            p.append(text(rx - rw / 2.0 - 8, ry + h - 4, e_sym, size=11, color=scol, bold=True, anchor="end"))
        ry += h + 6

    # 1. Стрілка та блок для копіювання .data
    # Текстовий блок по центру зверху
    b_data, bw_d, bh_d = textbox(440, 80,
                                 "1. Копіювання секції .data:\n"
                                 "Блок значень копіюється з Flash LMA (_sidata)\n"
                                 "в RAM VMA (_sdata .. _edata) по 4 байти.",
                                 size=11, pad=8, fill="#fff1f2", stroke=POS, sw=1.3)
    p.append(b_data)

    # Лінія стрілки від Flash .data до RAM .data, огинаючи текстовий блок знизу
    data_flash_y = 50 + 45 + 75 + 45 + 45 + 32
    data_ram_y = 50 + 32
    p.append(arrow(fx + fw / 2.0 + 55, data_flash_y, 320, data_flash_y, color=POS, sw=1.6))
    p.append(line(320, data_flash_y, 320, 145, color=POS, sw=1.6))
    p.append(line(320, 145, 560, 145, color=POS, sw=1.6))
    p.append(line(560, 145, 560, data_ram_y, color=POS, sw=1.6))
    p.append(arrow(560, data_ram_y, rx - rw / 2.0 - 4, data_ram_y, color=POS, sw=1.6))

    # 2. Блок та стрілка для обнулення .bss
    b_bss, bw_b, bh_b = textbox(440, 240,
                                "2. Занулення секції .bss:\n"
                                "Ділянка RAM від _sbss до _ebss\n"
                                "заповнюється нулями (*p++ = 0).",
                                size=11, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.3)
    p.append(b_bss)

    bss_ram_y = 50 + 65 + 6 + 32
    p.append(arrow(440 + bw_b / 2.0 + 4, 240, rx - rw / 2.0 - 4, bss_ram_y, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "flash-to-ram-relocation.svg"), W, H, *p)


# ── 4. fpu-init-register: Регістр SCB->CPACR та увімкнення FPU ──────────────
def fig_fpu_init_register():
    W, H = 880, 260
    p = []

    # Заголовок
    p.append(text(W / 2.0, 30, "Регістр SCB->CPACR (Coprocessor Access Control Register, 0xE000ED88)",
                  size=13, bold=True, color=INK))

    # Смуга 32-бітного регістра
    rx = 80
    ry = 60
    rw = 720
    rh = 42

    # Зарезервовано 31..24
    w_res1 = rw * (8.0 / 32.0)
    p.append(rect(rx, ry, w_res1, rh, fill="#f3f4f6", stroke="#9ca3af", sw=1.2, rx=0))
    p.append(text(rx + w_res1 / 2.0, ry + rh / 2.0 + 4, "31 .. 24 (Зарезервовано)", size=11, color=MUTED))

    # CP11 (біти 23..22)
    w_cp11 = rw * (2.0 / 32.0)
    x_cp11 = rx + w_res1
    p.append(rect(x_cp11, ry, w_cp11, rh, fill="#fee2e2", stroke=POS, sw=1.5, rx=0))
    p.append(text(x_cp11 + w_cp11 / 2.0, ry + rh / 2.0 + 4, "CP11", size=11, bold=True, color=POS))

    # CP10 (біти 21..20)
    w_cp10 = rw * (2.0 / 32.0)
    x_cp10 = x_cp11 + w_cp11
    p.append(rect(x_cp10, ry, w_cp10, rh, fill="#fee2e2", stroke=POS, sw=1.5, rx=0))
    p.append(text(x_cp10 + w_cp10 / 2.0, ry + rh / 2.0 + 4, "CP10", size=11, bold=True, color=POS))

    # Решта бітів 19..0
    w_res2 = rw * (20.0 / 32.0)
    x_res2 = x_cp10 + w_cp10
    p.append(rect(x_res2, ry, w_res2, rh, fill="#f3f4f6", stroke="#9ca3af", sw=1.2, rx=0))
    p.append(text(x_res2 + w_res2 / 2.0, ry + rh / 2.0 + 4, "19 .. 0 (Зарезервовано / інші співпроцесори)", size=11, color=MUTED))

    # Підписи бітів зверху
    p.append(text(rx + 4, ry - 6, "31", size=10, color=MUTED, anchor="start"))
    p.append(text(x_cp11 + 2, ry - 6, "23", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(x_cp10 + w_cp10 - 2, ry - 6, "20", size=10, color=POS, bold=True, anchor="end"))
    p.append(text(rx + rw - 4, ry - 6, "0", size=10, color=MUTED, anchor="end"))

    # Пояснення значень бітів знизу
    b_expl, _, _ = textbox(W / 2.0, 180,
                           "Значення полів CP10 та CP11 (керування FPU):\n"
                           "• 0b00: Доступ заборонено (спроба FPU-команди викликає NOCP UsageFault / HardFault)\n"
                           "• 0b01: Тільки привілейований режим\n"
                           "• 0b11: Повний доступ (Full Access) — запис маски (0xF << 20) = 0x00F00000",
                           size=11, pad=8, fill="#eff6ff", stroke=NEG, sw=1.4)
    p.append(b_expl)

    # Стрілка від бітів CP10/CP11 до пояснення
    p.append(arrow(x_cp11 + w_cp11, ry + rh + 2, W / 2.0, 140, color=POS, sw=1.5))

    render(os.path.join(OUT, "fpu-init-register.svg"), W, H, *p)


if __name__ == "__main__":
    fig_startup_timeline()
    fig_cortex_vector_table()
    fig_flash_to_ram_relocation()
    fig_fpu_init_register()
    print("Всі фігури успішно згенеровано.")
