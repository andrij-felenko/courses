# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. remote-diagnostics-spectrum: Рівні спостережливості польового вузла ────
def fig_remote_diagnostics_spectrum():
    W, H = 780, 330
    parts = [text(W / 2, 28, "Спектр віддаленої діагностики польового пристрою", size=16, bold=True)]

    levels = [
        ("1. Базовий моніторинг", "Пасивна телеметрія",
         ["• Heartbeat-пакети", "• Напруга живлення Vbat", "• Завантаження CPU / RAM", "• Температура кристала"],
         "#eafaf0", FIELD),
        ("2. Мережевий тракт", "Метрики сокетів і пам'яті",
         ["• TCP Retransmits / RST", "• Latency DNS / сервера", "• High-water mark пулів", "• Найбільший блок купи"],
         "#eaf0fd", NEG),
        ("3. Посмертний зріз", "Crash Dump (.noinit)",
         ["• Регістри R0-R15, xPSR", "• Регістри CFSR / BFAR", "• Зріз вершини стека", "• Стек викликів DWARF"],
         "#fff7e6", POS),
        ("4. Активний зонд", "Безпечний Remote Shell",
         ["• Сканування шини I2C", "• Мережевий Ping вузла", "• Апаратний POST-тест", "• Контроль таймаутів"],
         "#fbf0fa", "#8e44ad"),
    ]

    bw, gap = 172, 16
    x0 = (W - (4 * bw + 3 * gap)) / 2
    y0 = 56

    for i, (title, sub, items, bg_col, stroke_col) in enumerate(levels):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, y0, bw, 210, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        parts.append(text(x + bw / 2, y0 + 24, title, size=12, color=INK, bold=True))
        parts.append(text(x + bw / 2, y0 + 44, sub, size=10, color=stroke_col, italic=True))
        parts.append(line(x + 10, y0 + 56, x + bw - 10, y0 + 56, color=stroke_col, sw=1.0, dash="3 2"))

        for j, item in enumerate(items):
            parts.append(text(x + 10, y0 + 82 + j * 30, item, size=10, color=INK, anchor="start"))

        if i < 3:
            parts.append(arrow(x + bw + 2, y0 + 100, x + bw + gap - 2, y0 + 100, color=LINE, sw=1.5))

    parts.append(text(W / 2, 290, "Від періодичного пульсу до глибокого розслідування причин аварій без виїзду на об'єкт",
                      size=12, color=INK))
    parts.append(text(W / 2, 312, "Кожен наступний шар додає деталізації, не порушуючи автономності пристрою",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "remote-diagnostics-spectrum.svg"), W, H, *parts)


# ── 2. cortex-m-fault-unwind: Анатомія аварійного кадру ARM Cortex-M ──────────
def fig_cortex_m_fault_unwind():
    W, H = 820, 400
    parts = [text(W / 2, 26, "Анатомія винятку HardFault та розпакування стану процесора", size=16, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    # Ліва колонка: EXC_RETURN та вибір стека
    lx, ly, lw, lh = 20, 56, 210, 285
    parts.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke=LINE, sw=1.5))
    parts.append(text(lx + lw / 2, ly + 22, "1. Регістр LR (EXC_RETURN)", size=12, color=INK, bold=True))
    parts.append(rect(lx + 10, ly + 36, lw - 20, 36, fill="#ffffff", stroke=NEG, sw=1.2))
    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle" font-weight="700">0xFFFFFFFD / 0xFFFFFFF9</text>' % (
        lx + lw / 2, ly + 58, mono, NEG))

    parts.append(text(lx + 12, ly + 94, "Біт 2 (SPSEL) визначає стек:", size=11, color=INK, anchor="start", bold=True))
    parts.append(text(lx + 12, ly + 118, "• Біт 2 = 1 → Стек задачі PSP", size=10, color=FIELD, anchor="start"))
    parts.append(text(lx + 12, ly + 140, "• Біт 2 = 0 → Головний стек MSP", size=10, color=POS, anchor="start"))

    parts.append(rect(lx + 10, ly + 165, lw - 20, 105, fill="#eaf0fd", stroke=NEG, sw=1.2))
    note_lines = [
        "В RTOS аварія зазвичай",
        "стається в потоці задачі,",
        "тому дані кадру лежать",
        "у PSP, а не в MSP.",
    ]
    for k, n_ln in enumerate(note_lines):
        parts.append(text(lx + lw / 2, ly + 190 + k * 20, n_ln, size=10, color=INK))

    # Центральна колонка: Апаратний стековий кадр
    cx, cy, cw, ch = 244, 56, 240, 285
    parts.append(rect(cx, cy, cw, ch, fill="#fff7e6", stroke=POS, sw=1.8))
    parts.append(text(cx + cw / 2, cy + 22, "2. Апаратний кадр (вказівник SP)", size=12, color=POS, bold=True))

    stack_regs = [
        ("xPSR", "Статус процесора, Thumb"),
        ("PC (R15)", "Адреса інструкції збою"),
        ("LR (R14)", "Адреса повернення виклику"),
        ("R12", "Внутрішній регістр IP"),
        ("R3..R0", "Аргументи та проміжні дані"),
    ]
    for i, (reg, desc) in enumerate(stack_regs):
        ry = cy + 40 + i * 46
        is_key = (i <= 1)
        r_bg = "#fdecea" if is_key else "#ffffff"
        r_strk = POS if is_key else LINE
        parts.append(rect(cx + 10, ry, cw - 20, 38, fill=r_bg, stroke=r_strk, sw=1.2))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="start" font-weight="700">%s</text>' % (
            cx + 16, ry + 23, mono, POS if is_key else INK, reg))
        parts.append(text(cx + cw - 14, ry + 23, desc, size=9.5, color=MUTED, anchor="end"))

    # Права колонка: Системні діагностичні регістри SCB
    rx, ry, rw, rh = 498, 56, 302, 285
    parts.append(rect(rx, ry, rw, rh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    parts.append(text(rx + rw / 2, ry + 22, "3. Регістри несправностей SCB", size=12, color=FIELD, bold=True))

    scb_regs = [
        ("HFSR", "0xE000ED2C", "HardFault: FORCED, VECTTBL"),
        ("CFSR", "0xE000ED28", "UFSR (DIVBYZERO) + BFSR + MMFSR"),
        ("MMFAR", "0xE000ED34", "Точна адреса порушення захисту MPU"),
        ("BFAR", "0xE000ED38", "Точна адреса апаратної помилки шини"),
    ]
    for i, (r_name, r_addr, r_desc) in enumerate(scb_regs):
        s_y = ry + 40 + i * 58
        parts.append(rect(rx + 10, s_y, rw - 20, 50, fill="#ffffff", stroke=FIELD, sw=1.2))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" font-weight="700">%s</text>' % (
            rx + 18, s_y + 20, mono, FIELD, r_name))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" text-anchor="end">%s</text>' % (
            rx + rw - 18, s_y + 20, mono, MUTED, r_addr))
        parts.append(text(rx + 18, s_y + 38, r_desc, size=9.5, color=INK, anchor="start"))

    # Нижній висновок
    parts.append(text(W / 2, 360, "Комбінація PC + CFSR + BFAR/MMFAR точно вказує рядок коду та невалідну адресу звернення",
                      size=12, color=INK, bold=True))
    parts.append(text(W / 2, 382, "Дані видобуваються за лічені мікросекунди без використання динамічної пам'яті чи блокуючих драйверів",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cortex-m-fault-unwind.svg"), W, H, *parts)


# ── 3. crashdump-storage-flow: Життєвий цикл дампу ────────────────────────────
def fig_crashdump_storage_flow():
    W, H = 780, 330
    parts = [text(W / 2, 26, "Життєвий цикл аварійного дампу: від фаталу до хмари", size=16, bold=True)]

    steps = [
        ("1. HardFault ISR", "Захоплення стану",
         ["• Зчитування PSP/MSP", "• Запис у .noinit RAM", "• Фіксація Magic Word", "• Час: < 40 мкс"],
         POS, "#fdecea"),
        ("2. Soft / WDT Reset", "Безпечне скидання",
         ["• NVIC_SystemReset()", "• Живлення не зникає", "• RAM зберігає байти", "• Рестарт CPU"],
         LINE, "#f3f4f6"),
        ("3. Bootloader / App", "Валідація пам'яті",
         ["• Перевірка Magic Word", "• Розрахунок CRC32", "• Перенесення у Flash", "• Очищення прапорця"],
         NEG, "#eaf0fd"),
        ("4. Cloud Telemetry", "Віддалене вивантаження",
         ["• Підключення до мережі", "• Відправка по MQTT/CoAP", "• Декодування з .elf", "• Локалізація багу"],
         FIELD, "#eafaf0"),
    ]

    bw, gap = 168, 22
    x0 = (W - (4 * bw + 3 * gap)) / 2
    y0 = 56

    for i, (title, sub, lines, col, fill_col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, y0, bw, 210, fill=fill_col, stroke=col, sw=1.8, rx=6))
        parts.append(text(x + bw / 2, y0 + 24, title, size=12, color=INK, bold=True))
        parts.append(text(x + bw / 2, y0 + 44, sub, size=10, color=col, italic=True))
        parts.append(line(x + 10, y0 + 56, x + bw - 10, y0 + 56, color=col, sw=1.0, dash="3 2"))

        for j, ln in enumerate(lines):
            parts.append(text(x + 10, y0 + 82 + j * 28, ln, size=10, color=INK, anchor="start"))

        if i < 3:
            parts.append(arrow(x + bw + 2, y0 + 100, x + bw + gap - 2, y0 + 100, color=LINE, sw=2.0))

    parts.append(text(W / 2, 290, "Пам'ять .noinit витримує програмний рестарт і дозволяє не писати у повільну Flash у момент збою",
                      size=12, color=INK))
    parts.append(text(W / 2, 312, "Валідація заголовка та CRC32 запобігає розбору випадкового сміття після холодного ввімкнення",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "crashdump-storage-flow.svg"), W, H, *parts)


# ── 4. remote-command-engine: Архітектура віддаленого діагностичного рушія ────
def fig_remote_command_engine():
    W, H = 820, 360
    parts = [text(W / 2, 26, "Архітектура безпечного віддаленого діагностичного рушія", size=16, bold=True)]

    # Вхідний канал
    bx1, by1, bw1, bh1 = 18, 56, 170, 240
    parts.append(rect(bx1, by1, bw1, bh1, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(text(bx1 + bw1 / 2, by1 + 22, "Командний канал", size=12, color=NEG, bold=True))
    parts.append(text(bx1 + bw1 / 2, by1 + 42, "MQTT / CoAP / Shell", size=10, color=MUTED, italic=True))

    in_items = [
        "• MQTT RPC запит",
        "• LwM2M Execute",
        "• Підпис команди HMAC",
        "• Перевірка Nonce",
    ]
    for i, item in enumerate(in_items):
        parts.append(text(bx1 + 12, by1 + 76 + i * 38, item, size=10.5, color=INK, anchor="start"))

    parts.append(arrow(bx1 + bw1 + 2, by1 + 100, 206, by1 + 100, color=NEG, sw=1.8))

    # Диспетчер та рубежі безпеки
    bx2, by2, bw2, bh2 = 208, 56, 334, 240
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f8fafc", stroke=LINE, sw=1.8))
    parts.append(text(bx2 + bw2 / 2, by2 + 22, "Діагностичний диспетчер", size=12, color=INK, bold=True))
    parts.append(text(bx2 + bw2 / 2, by2 + 42, "Асинхронний фоновий потік", size=10, color=FIELD, italic=True))

    guards = [
        ("Рубіж 1: Тайм-аут (Execution Deadline)", "Примусове переривання завислого драйвера через 1500 мс", POS, "#fdecea"),
        ("Рубіж 2: Сторож (Watchdog Safe)", "Скидання апаратного WDT без блокування основного циклу", FIELD, "#eafaf0"),
        ("Рубіж 3: Неінвазивність (Read-Only)", "Заборона впливу на виконавчі реле, помпи та мотори", NEG, "#eaf0fd"),
    ]
    for i, (g_title, g_desc, g_col, g_bg) in enumerate(guards):
        gy = by2 + 58 + i * 56
        parts.append(rect(bx2 + 10, gy, bw2 - 20, 50, fill=g_bg, stroke=g_col, sw=1.2))
        parts.append(text(bx2 + 18, gy + 18, g_title, size=10, color=g_col, anchor="start", bold=True))
        parts.append(text(bx2 + 18, gy + 36, g_desc, size=9.5, color=INK, anchor="start"))

    parts.append(arrow(bx2 + bw2 + 2, by2 + 100, 558, by2 + 100, color=FIELD, sw=1.8))

    # Виконавчі тестові зонди
    bx3, by3, bw3, bh3 = 560, 56, 242, 240
    parts.append(rect(bx3, by3, bw3, bh3, fill="#eafaf0", stroke=FIELD, sw=1.8))
    parts.append(text(bx3 + bw3 / 2, by3 + 22, "Діагностичні зонди", size=12, color=FIELD, bold=True))
    parts.append(text(bx3 + bw3 / 2, by3 + 42, "Безпечні процедури", size=10, color=MUTED, italic=True))

    probes = [
        ("diag_ping(host)", "Перевірка IP-зв'язку"),
        ("diag_i2c_scan(bus)", "Пошук відмов шин / ліній"),
        ("diag_self_test()", "POST / CRC Flash / Живлення"),
        ("diag_mem_stats()", "Купа / Буфери LwIP"),
    ]
    mono = "'Consolas','DejaVu Sans Mono',monospace"
    for i, (p_fn, p_desc) in enumerate(probes):
        py_box = by3 + 58 + i * 42
        parts.append(rect(bx3 + 10, py_box, bw3 - 20, 36, fill="#ffffff", stroke=FIELD, sw=1.1))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10.5" fill="%s" font-weight="700">%s</text>' % (
            bx3 + 16, py_box + 16, mono, FIELD, p_fn))
        parts.append(text(bx3 + 16, py_box + 29, p_desc, size=9.5, color=MUTED, anchor="start"))

    parts.append(text(W / 2, 318, "Діагностичні запити ізолюються у фоновому конвеєрі, захищеному жорсткими часовими лімітами",
                      size=12, color=INK))
    parts.append(text(W / 2, 338, "Збій у тестовій процедурі (наприклад, зависання I2C) не призводить до краху всього пристрою",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "remote-command-engine.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_remote_diagnostics_spectrum()
    fig_cortex_m_fault_unwind()
    fig_crashdump_storage_flow()
    fig_remote_command_engine()
    print("All figures generated successfully.")
