# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.14 — «Налагодження глибоко: JTAG/SWD, GDB і посмертний аналіз».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r14-1-1-print-vs-halt.svg
  fig-r14-1-2-print-vs-debugger-table.svg
  fig-r14-2-1-debug-port-into-core.svg
  fig-r14-2-2-scan-chain.svg
  fig-r14-2-3-jtag-vs-swd.svg
  fig-r14-2-4-esp32-jtag-pins.svg
  fig-r14-3-1-hw-breakpoint-comparator.svg
  fig-r14-3-2-sw-breakpoint-swap.svg
  fig-r14-3-3-watchpoint-data.svg
  fig-r14-4-1-probe-openocd-gdb.svg
  fig-r14-4-3-gdb-command-map.svg
  fig-r14-5-1-stack-to-frames.svg
  fig-r14-5-2-step-next-finish.svg
  fig-r14-5-3-rtos-tasks-stacks.svg
  fig-r14-6-1-cortexm-fault-regs.svg
  fig-r14-6-2-exception-frame.svg
  fig-r14-6-3-addr2line-pipeline.svg
  fig-r14-7-1-postmortem-timeline.svg
  fig-r14-7-2-coredump-anatomy.svg
  fig-r14-7-3-debug-decision-tree.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.1.1 — Друк vs зупинка часу
# ══════════════════════════════════════════════════════════════════════════════
def fig_print_vs_halt():
    W, H = 820, 400
    frags = []

    # ── Ліва панель: «Друк» ────────────────────────────────────────────────
    frags.append(rect(20, 50, 370, 320, fill="#fff8f0", stroke="#e67e22", sw=2, rx=10))
    frags.append(text(205, 82, "ДРУК (Serial.print)", size=15, bold=True, color="#e67e22"))

    # Бігун (умовний: кружечок + стрілка руху)
    frags.append(circle(130, 185, 28, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(130, 191, "CPU", size=13, bold=True, color=POS))
    frags.append(arrow(158, 185, 230, 185, color="#e67e22", sw=2))
    frags.append(text(270, 189, "біжить →", size=12, color="#e67e22"))

    # Питання «де ти?»
    frags.append(line(205, 215, 205, 250, color=MUTED, sw=1.5, dash="4,3"))
    tb, _, _ = textbox(205, 272, "? де ти ?", size=13, fill="#fff3e0",
                       stroke="#e67e22", sw=1.5, color="#e67e22", bold=True)
    frags.append(tb)

    # Відповідь: лише те, що встиг
    frags.append(text(205, 310, "відповідь — лише те,", size=11, color=MUTED))
    frags.append(text(205, 325, "що встиг сказати", size=11, color=MUTED))

    # Попередження про сповільнення
    tb2, _, _ = textbox(205, 358, "друк змінює таймінг!", size=11,
                        fill="#fdecea", stroke=POS, sw=1.2, color=POS)
    frags.append(tb2)

    # ── Права панель: «Halt» ───────────────────────────────────────────────
    frags.append(rect(430, 50, 370, 320, fill="#f0f8ff", stroke=NEG, sw=2, rx=10))
    frags.append(text(615, 82, "ВІДЛАГОДЖУВАЧ (halt)", size=15, bold=True, color=NEG))

    # Завмерлий бігун
    frags.append(circle(530, 185, 28, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(530, 191, "CPU", size=13, bold=True, color=NEG))
    tb3, _, _ = textbox(530, 240, "⏸ завмер", size=13, fill="#eaf0fd",
                        stroke=NEG, sw=1.5, color=NEG, bold=True)
    frags.append(tb3)

    # Інженер ходить навколо
    frags.append(text(650, 175, "читаємо:", size=12, color=INK))
    items = ["• будь-який регістр", "• будь-яку пам'ять", "• весь стек викликів"]
    for i, it in enumerate(items):
        frags.append(text(650, 195 + i * 18, it, size=11, color=FIELD, anchor="middle"))

    # Висновок
    tb4, _, _ = textbox(615, 358, "зупинено час — читаємо все", size=11,
                        fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD, bold=True)
    frags.append(tb4)

    # ── Роздільник і підпис ────────────────────────────────────────────────
    frags.append(line(408, 60, 408, 360, color=MUTED, sw=1, dash="6,4"))
    frags.append(text(W // 2, 395, "Рис. 4.14.1.1. Друк опитує на ходу; відлагоджувач зупиняє час і оглядає нерухоме.", size=11, color=MUTED))

    render(os.path.join(OUT, "fig-r14-1-1-print-vs-halt.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.1.2 — Порівняльна таблиця: друк vs відлагоджувач
# ══════════════════════════════════════════════════════════════════════════════
def fig_print_vs_debugger_table():
    W, H = 820, 380
    frags = []

    headers = ["Критерій", "Serial.print", "Відлагоджувач"]
    rows = [
        ["Що бачить?", "лише надруковане\nнаперед", "всю пам'ять,\nрегістри, стек"],
        ["Вплив на таймінг", "мінімальний\n(якщо короткий)", "зупиняє ядро —\nрве реальний час"],
        ["Потребує зонда?", "ні — лише UART", "так — зонд\nабо USB-JTAG"],
        ["Краще для", "потокового\nмоніторингу", "локалізації збою\nта аналізу стану"],
        ["Heisenbug?", "може приховати\nбаг (змінює час)", "ніколи — ядро\nзавмерло"],
    ]

    col_x = [55, 290, 555]
    col_w = [190, 220, 220]
    row_h = 54
    y0 = 55

    # Заголовки
    for i, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
        fill = "#2d3e50"
        frags.append(rect(cx - cw / 2, y0, cw - 4, row_h - 4,
                          fill=fill, stroke=LINE, sw=1.2, rx=6))
        frags.append(text(cx, y0 + row_h / 2 + 1, hdr, size=13,
                          color="#ffffff", bold=True))

    # Рядки
    for ri, row in enumerate(rows):
        bg = FILL if ri % 2 == 0 else "#edf2f7"
        y = y0 + (ri + 1) * row_h
        for ci, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
            frags.append(fitbox(cx - cw / 2, y, cw - 4, row_h - 4,
                                cell, size=12, fill=bg, stroke=LINE,
                                pad=6, rx=4))

    # Підсумок
    tb, _, _ = textbox(W // 2, H - 28,
                       "Інструменти доповнюють одне одного — відлагоджувач не заміна друку, а інша сила.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r14-1-2-print-vs-debugger-table.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.2.1 — Як дріт ззовні дотягується до нутрощів ядра
# ══════════════════════════════════════════════════════════════════════════════
def fig_debug_port_into_core():
    W, H = 780, 420
    frags = []

    # Чип (зовнішній корпус)
    frags.append(rect(200, 60, 400, 300, fill="#e8edf5", stroke="#2457d6", sw=2.5, rx=12))
    frags.append(text(400, 88, "Чип (мікроконтролер)", size=14, bold=True, color="#2457d6"))

    # Ядро CPU всередині
    frags.append(rect(290, 110, 220, 120, fill="#d5e8d4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(400, 160, "Ядро CPU", size=14, bold=True, color=FIELD))
    frags.append(text(400, 180, "(виконує код)", size=11, color=MUTED))

    # Відлагоджувальний блок DAP/OCD
    frags.append(rect(290, 255, 220, 70, fill="#fdecea", stroke=POS, sw=2, rx=8))
    frags.append(text(400, 283, "DAP / OCD-блок", size=13, bold=True, color=POS))
    frags.append(text(400, 300, "(регістри halt, bkpt, watch)", size=10, color=MUTED))

    # Внутрішня шина між ядром і DAP
    frags.append(line(400, 230, 400, 255, color=MUTED, sw=2, dash="4,3"))
    frags.append(text(415, 245, "внутр. шина", size=10, color=MUTED, anchor="start"))

    # Порт (ніжки зліва від чипа)
    frags.append(rect(80, 260, 100, 65, fill="#fff8e1", stroke="#e67e22", sw=2, rx=6))
    frags.append(text(130, 288, "Debug Port", size=12, bold=True, color="#e67e22"))
    frags.append(text(130, 305, "JTAG/SWD", size=11, color="#e67e22"))

    # Стрілка від порту до DAP
    frags.append(arrow(180, 292, 290, 292, color="#e67e22", sw=2.2))
    frags.append(text(235, 282, "скан-ланцюг", size=10, color="#e67e22"))

    # Зонд зліва
    frags.append(rect(0, 268, 70, 50, fill="#f5f5f5", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(35, 288, "Зонд", size=12, bold=True))
    frags.append(text(35, 305, "(USB)", size=11, color=MUTED))
    frags.append(arrow(70, 292, 80, 292, color=LINE, sw=2))

    # Команда halt — стрілка з підписом
    frags.append(arrow(400, 325, 400, 245, color=POS, sw=1.8))
    frags.append(text(415, 340, "«halt» = запис біта в регістр", size=10, color=POS, anchor="start"))

    # Підпис
    frags.append(text(W // 2, H - 10, "Рис. 4.14.2.1. halt — не магія, а запис у реальний апаратний регістр через відлагоджувальний порт.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-2-1-debug-port-into-core.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.2.2 — Скан-ланцюг: реєстри нанизані на одну нитку
# ══════════════════════════════════════════════════════════════════════════════
def fig_scan_chain():
    W, H = 820, 380
    frags = []

    # TDI зліва
    frags.append(text(30, 190, "TDI", size=14, bold=True, color=NEG))
    frags.append(arrow(55, 185, 100, 185, color=NEG, sw=2.2))
    frags.append(text(78, 175, "вхід", size=10, color=MUTED))

    # 5 комірок-тригерів
    cells = [150, 270, 390, 510, 630]
    cell_w, cell_h = 90, 60
    for i, cx in enumerate(cells):
        frags.append(rect(cx - cell_w // 2, 155, cell_w, cell_h,
                          fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
        frags.append(text(cx, 181, f"REG{i+1}", size=13, bold=True, color=NEG))
        frags.append(text(cx, 198, "1 біт", size=10, color=MUTED))
        # з'єднання між комірками
        if i < len(cells) - 1:
            frags.append(arrow(cx + cell_w // 2, 185, cells[i+1] - cell_w // 2, 185,
                               color=LINE, sw=2))

    # TDO справа
    frags.append(arrow(675, 185, 740, 185, color=POS, sw=2.2))
    frags.append(text(760, 190, "TDO", size=14, bold=True, color=POS))
    frags.append(text(708, 175, "вихід", size=10, color=MUTED))

    # TCK такт — знизу
    for cx in cells:
        frags.append(line(cx, 215, cx, 260, color="#e67e22", sw=1.5, dash="4,3"))
    frags.append(line(100, 260, 710, 260, color="#e67e22", sw=2))
    frags.append(text(405, 278, "TCK (такт)", size=12, bold=True, color="#e67e22"))

    # Пояснення
    frags.append(text(405, 320, "Кожен такт TCK: бít вдвигається з TDI, зсувається по ланцюгу, стан чипа видвигається у TDO.", size=11, color=MUTED))
    frags.append(text(405, 338, "Один тонкий дріт-«нитка» дає серіалізований доступ до всіх регістрів.", size=11, color=INK, bold=False))

    # Підпис
    frags.append(text(W // 2, H - 10, "Рис. 4.14.2.2. Скан-ланцюг: один тонкий дріт дає доступ до всіх нутрощів коштом серіалізації.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-2-2-scan-chain.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.2.3 — JTAG проти SWD: ті самі можливості, різна кількість ліній
# ══════════════════════════════════════════════════════════════════════════════
def fig_jtag_vs_swd():
    W, H = 780, 380
    frags = []

    # JTAG — ліворуч
    frags.append(rect(30, 50, 280, 280, fill="#f0f4fc", stroke=NEG, sw=2, rx=10))
    frags.append(text(170, 80, "JTAG", size=17, bold=True, color=NEG))
    frags.append(text(170, 100, "IEEE 1149.1", size=11, color=MUTED))

    lines_j = ["TCK — такт", "TMS — вибір стану", "TDI — вхід даних",
                "TDO — вихід даних", "(+TRST — скидання)"]
    colors_j = [NEG, FIELD, "#e67e22", POS, MUTED]
    for i, (ln, cl) in enumerate(zip(lines_j, colors_j)):
        frags.append(text(170, 132 + i * 28, ln, size=13, color=cl))

    frags.append(text(170, 295, "4–5 ліній", size=15, bold=True, color=NEG))

    # SWD — посередині
    frags.append(rect(340, 50, 220, 280, fill="#f0faf4", stroke=FIELD, sw=2, rx=10))
    frags.append(text(450, 80, "SWD", size=17, bold=True, color=FIELD))
    frags.append(text(450, 100, "ARM Serial Wire", size=11, color=MUTED))

    lines_s = ["SWCLK — такт", "SWDIO — дані\n(двоспрямовані)"]
    for i, ln in enumerate(lines_s):
        frags.append(mtext(450, 140 + i * 45, ln, size=13, color=FIELD))

    frags.append(text(450, 295, "2 лінії", size=15, bold=True, color=FIELD))

    # Спільний блок — debug core
    frags.append(rect(590, 100, 160, 180, fill="#fff8e1", stroke="#e67e22", sw=2, rx=10))
    frags.append(mtext(670, 150, "Debug\nCore\n(ядро чипа)", size=13,
                       color="#e67e22", bold=True))

    # Стрілки до debug core
    frags.append(arrow(310, 190, 590, 190, color=NEG, sw=2))
    frags.append(arrow(560, 210, 590, 210, color=FIELD, sw=2))

    # Підпис висновку
    tb, _, _ = textbox(W // 2 - 50, H - 28,
                       "SWD — економний транспорт для дрібних корпусів, сила та сама.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r14-2-3-jtag-vs-swd.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.2.4 — JTAG на ESP32: піни й ланцюг зонд→чип
# ══════════════════════════════════════════════════════════════════════════════
def fig_esp32_jtag_pins():
    W, H = 820, 400
    frags = []

    # ── Верхній варіант: зовнішній зонд (класичний ESP32) ─────────────────
    frags.append(text(410, 30, "Варіант А: зовнішній зонд (ESP32, ESP32-S2)", size=13, bold=True, color=INK))

    # Хост
    frags.append(rect(20, 50, 90, 50, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(65, 80, "Хост (USB)", size=11))

    # Зонд
    frags.append(rect(145, 50, 110, 50, fill="#fff8e1", stroke="#e67e22", sw=2, rx=6))
    frags.append(text(200, 70, "Зонд", size=12, bold=True, color="#e67e22"))
    frags.append(text(200, 86, "ESP-Prog / JLink", size=10, color=MUTED))
    frags.append(arrow(110, 75, 145, 75, color="#e67e22", sw=2))

    # Лінії
    line_names = ["MTCK", "MTDI", "MTDO", "MTMS", "GND"]
    line_colors = [NEG, "#e67e22", POS, FIELD, MUTED]
    for i, (ln, cl) in enumerate(zip(line_names, line_colors)):
        y = 55 + i * 12
        frags.append(line(255, y, 380, y, color=cl, sw=1.8))
        frags.append(text(318, y - 4, ln, size=9, color=cl))

    # ESP32 чип
    frags.append(rect(380, 45, 130, 70, fill="#e8edf5", stroke="#2457d6", sw=2, rx=6))
    frags.append(text(445, 72, "ESP32", size=13, bold=True, color="#2457d6"))
    frags.append(text(445, 88, "JTAG-піни", size=10, color=MUTED))
    frags.append(text(445, 104, "(займають GPIO)", size=10, color=POS))

    # ── Нижній варіант: USB-Serial-JTAG ────────────────────────────────────
    frags.append(text(410, 160, "Варіант Б: USB-Serial-JTAG (ESP32-S3 / C3 / C6 — без зовнішнього зонда)", size=13, bold=True, color=FIELD))

    frags.append(rect(20, 185, 90, 50, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(65, 215, "Хост (USB)", size=11))

    frags.append(rect(380, 180, 160, 60, fill="#d5e8d4", stroke=FIELD, sw=2, rx=6))
    frags.append(text(460, 203, "ESP32-S3/C3/C6", size=12, bold=True, color=FIELD))
    frags.append(text(460, 220, "USB-Serial-JTAG", size=11, color=FIELD))
    frags.append(text(460, 235, "(вбудований JTAG)", size=10, color=MUTED))

    frags.append(arrow(110, 210, 380, 210, color=FIELD, sw=2.2))
    tb, _, _ = textbox(245, 228, "USB (без зонда!)", size=11,
                       fill="#d5e8d4", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    # Пунктирна позначка «зонд не потрібен»
    frags.append(rect(600, 183, 130, 54, fill="#f9f9f9", stroke=MUTED, sw=1, rx=6))
    frags.append(text(665, 205, "Зонд", size=11, color=MUTED))
    frags.append(text(665, 222, "не потрібен", size=11, color=MUTED, bold=True))
    frags.append(line(600, 183, 730, 237, color=POS, sw=1.5, dash="5,4"))

    # Конфлікт GPIO
    tb2, _, _ = textbox(445, 290,
                        "Лінії JTAG зайняті — ці GPIO\nне можна використовувати для\nіншої периферії одночасно.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS)
    frags.append(tb2)

    # Підпис
    frags.append(text(W // 2, H - 10, "Рис. 4.14.2.4. Відлагодження коштує конкретних ніжок; на нових чипах JTAG іде прямо по USB.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-2-4-esp32-jtag-pins.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.3.1 — Апаратний брейкпоінт: компаратор адрес у залізі
# ══════════════════════════════════════════════════════════════════════════════
def fig_hw_breakpoint_comparator():
    W, H = 780, 380
    frags = []

    # Потік PC
    frags.append(text(80, 50, "Потік вибірки команд", size=13, bold=True, color=INK))
    for i in range(5):
        x = 40 + i * 80
        addr = 0x2000 + i * 4
        frags.append(rect(x, 65, 70, 40, fill=FILL, stroke=LINE, sw=1.2, rx=4))
        frags.append(text(x + 35, 80, f"0x{addr:04X}", size=10, color=INK))
        frags.append(text(x + 35, 95, "інструкція", size=9, color=MUTED))
    frags.append(arrow(450, 85, 520, 85, color=LINE, sw=2))
    frags.append(text(536, 89, "PC →", size=12, bold=True, color=INK, anchor="start"))

    # Блок компараторів
    frags.append(rect(550, 55, 190, 175, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(645, 78, "Компаратори адрес", size=12, bold=True, color=NEG))
    cmp_names = ["CMP0: 0x2008  ←", "CMP1: (вільний)", "CMP2: (вільний)",
                 "...", "CMP5: (вільний)"]
    cmp_fills = ["#fdecea", FILL, FILL, "#f9f9f9", FILL]
    for i, (nm, cf) in enumerate(zip(cmp_names, cmp_fills)):
        frags.append(rect(558, 90 + i * 28, 174, 22, fill=cf, stroke=LINE, sw=0.8, rx=3))
        frags.append(text(645, 105 + i * 28, nm, size=10, color=POS if i == 0 else INK))

    frags.append(text(645, 240, "N компараторів — фіксовано!", size=11, bold=True, color=POS))

    # Збіг → halt
    frags.append(arrow(645, 255, 645, 300, color=POS, sw=2.2))
    tb, _, _ = textbox(645, 325, "ЗБІГ → HALT\n(зупинити ядро)", size=13,
                       fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True)
    frags.append(tb)

    # Flash-мітка
    tb2, _, _ = textbox(230, 300, "Працює у Flash!\n(байт не потрібно підмінювати)", size=11,
                        fill="#d5e8d4", stroke=FIELD, sw=1.5, color=FIELD)
    frags.append(tb2)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.3.1. Апаратний брейк працює навіть у Flash, але компараторів лічена кількість.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-3-1-hw-breakpoint-comparator.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.3.2 — Програмний брейкпоінт: підміна команди пасткою
# ══════════════════════════════════════════════════════════════════════════════
def fig_sw_breakpoint_swap():
    W, H = 780, 380
    frags = []

    # Рядок пам'яті — 5 комірок
    addrs = [0x2000, 0x2002, 0x2004, 0x2006, 0x2008]
    instrs = ["MOV r0,#1", "ADD r1,r0", "▶ BKPT", "STR r1,[r2]", "BL func"]
    fills = [FILL, FILL, "#fdecea", FILL, FILL]
    cell_w, cell_h = 110, 50
    x0 = 40
    for i, (addr, instr, fl) in enumerate(zip(addrs, instrs, fills)):
        cx = x0 + i * (cell_w + 10)
        sw = 2.5 if i == 2 else 1.2
        scl = POS if i == 2 else LINE
        frags.append(rect(cx, 80, cell_w, cell_h, fill=fl, stroke=scl, sw=sw, rx=5))
        frags.append(text(cx + cell_w // 2, 98, f"0x{addr:04X}", size=10, color=MUTED))
        frags.append(text(cx + cell_w // 2, 116, instr, size=11,
                          bold=(i == 2), color=POS if i == 2 else INK))

    # Оригінальна команда збоку
    tb, _, _ = textbox(680, 60, "оригінал:\nBL crypto", size=11,
                       fill="#fff8e1", stroke="#e67e22", sw=1.5, color="#e67e22")
    frags.append(tb)
    frags.append(line(400, 80, 650, 60, color="#e67e22", sw=1.2, dash="4,3"))

    # Процес підміни і відновлення
    frags.append(text(400, 165, "1. Відлагоджувач підмінює інструкцію на BKPT", size=12, color=INK))
    frags.append(text(400, 183, "2. Ядро доходить → пастка спрацьовує → halt", size=12, color=POS, bold=True))
    frags.append(text(400, 201, "3. Відлагоджувач відновлює оригінальну інструкцію", size=12, color=FIELD))
    frags.append(text(400, 219, "4. Продовжуємо виконання зі справжньою командою", size=12, color=INK))

    # Flash-обмеження
    tb2, _, _ = textbox(400, 285,
                        "У Flash підмінити байт «на льоту» не можна\n(треба стерти-тоді-писати — §4.3.2)\n→ потрібні апаратні брейкпоінти!",
                        size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS)
    frags.append(tb2)

    tb3, _, _ = textbox(400, 350, "У RAM — програмних брейків скільки завгодно.", size=11,
                        fill="#d5e8d4", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb3)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.3.2. Програмний брейк підміняє інструкцію на пастку; у Flash не працює.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-3-2-sw-breakpoint-swap.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.3.3 — Вотчпоінт: пастка на доступ до даних
# ══════════════════════════════════════════════════════════════════════════════
def fig_watchpoint_data():
    W, H = 780, 400
    frags = []

    # Шина пам'яті
    frags.append(rect(30, 155, 720, 40, fill="#f0f4fc", stroke=NEG, sw=2, rx=6))
    frags.append(text(390, 180, "Шина даних (Data Bus)", size=12, bold=True, color=NEG))

    # Стережена змінна в RAM
    frags.append(rect(300, 70, 180, 60, fill="#fdecea", stroke=POS, sw=2.5, rx=8))
    frags.append(text(390, 95, "cfg->rate", size=14, bold=True, color=POS))
    frags.append(text(390, 113, "адреса 0x3FFB_1234", size=10, color=MUTED))
    frags.append(line(390, 130, 390, 155, color=POS, sw=2))

    # Компаратор даних
    frags.append(rect(540, 60, 200, 75, fill="#fff8e1", stroke="#e67e22", sw=2, rx=8))
    frags.append(text(640, 83, "Компаратор даних", size=12, bold=True, color="#e67e22"))
    frags.append(text(640, 100, "addr = 0x3FFB_1234", size=10, color=INK))
    frags.append(text(640, 116, "умова: WRITE", size=10, color=POS))
    frags.append(text(640, 130, "(або READ/RW)", size=9, color=MUTED))

    # Стрілка від шини до компаратора
    frags.append(line(640, 155, 640, 135, color="#e67e22", sw=1.8))
    frags.append(text(655, 148, "кожен запис", size=9, color=MUTED, anchor="start"))

    # HALT
    frags.append(arrow(640, 200, 640, 265, color=POS, sw=2.2))
    tb, _, _ = textbox(640, 295, "ЗБІГ → HALT\nвинний рядок коду", size=13,
                       fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True)
    frags.append(tb)

    # Три різних агенти, що пишуть у змінну
    writers = [
        (100, "task_ctrl\nwrite()", NEG),
        (390, "ISR_timer\nwrite()", "#e67e22"),
        (680, "ble_cb\nwrite()", FIELD),
    ]
    for wx, wlbl, wcl in writers:
        frags.append(rect(wx - 60, 245, 120, 45, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        frags.append(mtext(wx, 263, wlbl, size=11, color=wcl))
        frags.append(arrow(wx, 245, wx, 195, color=wcl, sw=1.8))

    # Питання
    tb2, _, _ = textbox(390, 365,
                        "ХТО псує мою змінну?\nВотчпоінт ловить будь-якого кривдника — незалежно від місця у коді.",
                        size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb2)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.3.3. Вотчпоінт ловить псування пам'яті незалежно від того, хто винен.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-3-3-watchpoint-data.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.4.1 — Ланцюг зонд → OpenOCD → GDB: хто що знає
# ══════════════════════════════════════════════════════════════════════════════
def fig_probe_openocd_gdb():
    W, H = 860, 380
    frags = []

    boxes = [
        (80,  "Зонд\n(USB↔JTAG/SWD)",   "#e67e22", "#fff8e1", "біти JTAG/SWD\n(апаратний рівень)"),
        (290, "OpenOCD",                  NEG,       "#eaf0fd", "знає чип + конфіг;\nGDB-сервер :3333"),
        (500, "GDB",                      FIELD,     "#d5e8d4", "знає .elf:\nфункції, рядки, змінні"),
        (710, "Інженер",                  INK,       FILL,      "розуміє логіку\nпрограми"),
    ]

    box_w, box_h = 150, 80
    y0 = 80

    for cx, title, tcl, fill, subtitle in boxes:
        frags.append(rect(cx - box_w // 2, y0, box_w, box_h, fill=fill, stroke=tcl, sw=2, rx=8))
        frags.append(text(cx, y0 + 28, title, size=13, bold=True, color=tcl))
        frags.append(mtext(cx, y0 + 52, subtitle, size=10, color=MUTED))

    # Стрілки між блоками
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + box_w // 2
        x2 = boxes[i+1][0] - box_w // 2
        frags.append(arrow(x1, y0 + 40, x2, y0 + 40, color=LINE, sw=2))

    # Стрілка від .elf до GDB
    frags.append(rect(420, 210, 160, 60, fill="#fff8e1", stroke="#e67e22", sw=1.5, rx=6))
    frags.append(text(500, 233, "app.elf", size=13, bold=True, color="#e67e22"))
    frags.append(text(500, 252, "символи: адреса → ім'я", size=10, color=MUTED))
    frags.append(arrow(500, 210, 500, 160, color="#e67e22", sw=1.8))
    frags.append(text(518, 190, "«словник»", size=10, color="#e67e22", anchor="start"))

    # Протокол між OpenOCD і GDB
    frags.append(text(395, 75, "Remote Serial\nProtocol (TCP)", size=10, color=MUTED))

    # Висновок
    tb, _, _ = textbox(W // 2, H - 30,
                       "Кожна ланка перекладає на наступний рівень абстракції; усі три необхідні.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.4.1. Ланцюг зонд → OpenOCD → GDB.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-4-1-probe-openocd-gdb.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.4.3 — Карта команд GDB за призначенням
# ══════════════════════════════════════════════════════════════════════════════
def fig_gdb_command_map():
    W, H = 820, 420
    frags = []

    groups = [
        ("РУХ", NEG, "#eaf0fd", [
            ("continue / c", "продовжити виконання"),
            ("next / n",     "крок (не входить у функцію)"),
            ("step / s",     "крок (входить у функцію)"),
            ("finish",       "вийти з поточної функції"),
        ]),
        ("ОГЛЯД", FIELD, "#d5e8d4", [
            ("print / p VAR",  "значення змінної"),
            ("info locals",    "усі локальні змінні"),
            ("info registers", "регістри CPU"),
            ("x/…  ADDR",      "дамп пам'яті за адресою"),
            ("backtrace / bt", "стек викликів"),
        ]),
        ("ПАСТКИ", POS, "#fdecea", [
            ("break / b LOC",  "програмний брейкпоінт"),
            ("hbreak LOC",     "апаратний брейкпоінт"),
            ("watch VAR",      "вотчпоінт (запис)"),
        ]),
        ("MONITOR", "#e67e22", "#fff8e1", [
            ("monitor RESET",  "скинути ядро (OpenOCD)"),
            ("monitor halt",   "зупинити ядро (OpenOCD)"),
        ]),
    ]

    col_w = 180
    x_starts = [30, 220, 430, 620]
    y0 = 55

    for gi, (grp_name, tcl, fill, cmds) in enumerate(groups):
        cx = x_starts[gi]
        # Заголовок групи
        frags.append(rect(cx, y0, col_w, 32, fill=tcl, stroke=tcl, sw=1.5, rx=6))
        frags.append(text(cx + col_w // 2, y0 + 20, grp_name, size=14,
                          bold=True, color="#ffffff"))
        # Команди
        for ci, (cmd, desc) in enumerate(cmds):
            ry = y0 + 35 + ci * 62
            frags.append(rect(cx, ry, col_w, 58, fill=fill, stroke=tcl, sw=1, rx=4))
            frags.append(text(cx + col_w // 2, ry + 20, cmd, size=11,
                              bold=True, color=tcl))
            frags.append(text(cx + col_w // 2, ry + 38, desc, size=10, color=INK))

    # Підпис
    tb, _, _ = textbox(W // 2, H - 28,
                       "Невеликий словник команд покриває весь щоденний цикл налагодження.",
                       size=11, fill=FILL, stroke=LINE, sw=1.2, color=INK)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.4.3. Карта команд GDB за призначенням.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-4-3-gdb-command-map.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.5.1 — Від стека в пам'яті до списку фреймів backtrace
# ══════════════════════════════════════════════════════════════════════════════
def fig_stack_to_frames():
    W, H = 820, 440
    frags = []

    # ── Лівий бік: стек у RAM ──────────────────────────────────────────────
    frags.append(text(175, 35, "Стек у RAM (зростає донизу ↓)", size=13, bold=True, color=NEG))

    frames_data = [
        ("leaf()", ["local x=7", "збер. LR=0x2010", "збер. r4"]),
        ("mid(int n)", ["local buf[]", "збер. LR=0x200C", "збер. r4,r5"]),
        ("app_main()", ["local cfg", "збер. LR=0xFFFF", "..."]),
    ]
    colors = [POS, "#e67e22", FIELD]
    y_cur = 60
    frame_boxes = []  # (y_top, y_bottom, color) for arrows

    for i, (fname, items, cl) in enumerate(zip(
            [f[0] for f in frames_data],
            [f[1] for f in frames_data],
            colors)):
        fh = len(items) * 22 + 30
        frags.append(rect(30, y_cur, 290, fh, fill=FILL, stroke=cl, sw=2, rx=6))
        frags.append(text(175, y_cur + 18, fname, size=12, bold=True, color=cl))
        for j, it in enumerate(items):
            frags.append(text(175, y_cur + 36 + j * 22, it, size=10, color=MUTED))
        frame_boxes.append((y_cur + fh // 2, cl))
        y_cur += fh + 8

    frags.append(text(175, y_cur + 10, "SP →", size=12, bold=True, color=NEG))

    # ── Правий бік: вивід GDB bt ──────────────────────────────────────────
    frags.append(text(620, 35, "GDB: backtrace", size=13, bold=True, color=FIELD))
    frags.append(rect(450, 55, 330, 220, fill="#1e2030", stroke=FIELD, sw=2, rx=8))

    bt_lines = [
        ("#0  leaf () at main.c:45", POS),
        ("    x = 7", "#aaaaaa"),
        ("#1  mid (n=3) at main.c:30", "#e67e22"),
        ("    n = 3", "#aaaaaa"),
        ("#2  app_main () at main.c:12", FIELD),
        ("    ...", "#aaaaaa"),
    ]
    for i, (ln, cl) in enumerate(bt_lines):
        frags.append(text(465, 80 + i * 30, ln, size=10, color=cl, anchor="start"))

    # Стрілки між стеком і bt
    bt_ys = [80, 140, 200]
    for (frame_y, cl), bt_y in zip(frame_boxes, bt_ys):
        frags.append(arrow(320, frame_y, 450, bt_y + 10, color=cl, sw=1.5))

    # Підпис
    tb, _, _ = textbox(W // 2, H - 30,
                       "backtrace відновлює ланцюг «хто кого викликав» із завмерлого стека.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.5.1. Від стека в пам'яті до списку фреймів backtrace.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-5-1-stack-to-frames.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.5.2 — step проти next проти finish
# ══════════════════════════════════════════════════════════════════════════════
def fig_step_next_finish():
    W, H = 780, 420
    frags = []

    # Дерево викликів
    # main → рядки коду → виклик foo → foo → виклик bar → bar
    nodes = {
        "main":  (390, 60),
        "L1":    (200, 150),   # рядок перед викликом foo
        "foo":   (390, 150),
        "L2":    (590, 150),   # рядок після виклику foo (повернення)
        "bar":   (390, 250),
    }
    node_w, node_h = 110, 38

    def draw_node(cx, cy, lbl, fill, stroke):
        frags.append(rect(cx - node_w // 2, cy - node_h // 2, node_w, node_h,
                          fill=fill, stroke=stroke, sw=2, rx=6))
        frags.append(text(cx, cy + 5, lbl, size=12, bold=True, color=stroke))

    draw_node(*nodes["main"], "main()", FILL, INK)
    draw_node(*nodes["foo"],  "foo()", "#eaf0fd", NEG)
    draw_node(*nodes["bar"],  "bar()", "#fdecea", POS)

    # З'єднання main → foo → bar
    frags.append(line(390, 60 + node_h // 2, 390, 150 - node_h // 2,
                      color=LINE, sw=1.5))
    frags.append(line(390, 150 + node_h // 2, 390, 250 - node_h // 2,
                      color=LINE, sw=1.5))

    # Три траєкторії
    # step: main → foo → bar (синьо)
    frags.append(text(80, 160, "step", size=13, bold=True, color=NEG))
    frags.append(text(80, 178, "заходить у foo і bar", size=10, color=MUTED))
    frags.append(arrow(140, 165, 280, 155, color=NEG, sw=2))

    # next: main → (переступає foo як один крок) → L2
    frags.append(text(590, 100, "next", size=13, bold=True, color=FIELD))
    frags.append(text(590, 118, "переступає foo", size=10, color=MUTED))
    draw_node(*nodes["L2"], "→ next", "#d5e8d4", FIELD)
    frags.append(arrow(390 + node_w // 2, 60, nodes["L2"][0] - node_w // 2, nodes["L2"][1],
                       color=FIELD, sw=2))

    # finish: з bar → повернення у foo
    frags.append(text(200, 310, "finish", size=13, bold=True, color="#e67e22"))
    frags.append(text(200, 328, "виходить із bar у foo", size=10, color=MUTED))
    frags.append(arrow(335, 255, 200, 170, color="#e67e22", sw=2))
    frags.append(text(255, 225, "повернення", size=10, color="#e67e22"))

    # Легенда
    frags.append(text(W // 2, H - 30, "step заходить усередину  ·  next переступає виклик  ·  finish виходить із функції", size=11, color=INK))
    frags.append(text(W // 2, H - 10, "Рис. 4.14.5.2. step проти next проти finish на дереві викликів.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-5-2-step-next-finish.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.5.3 — RTOS: кожна задача — свій стек і свій застиглий PC
# ══════════════════════════════════════════════════════════════════════════════
def fig_rtos_tasks_stacks():
    W, H = 820, 400
    frags = []

    tasks = [
        ("app_task", "#eaf0fd", NEG,      "xQueueReceive()\n@ queue.c:112"),
        ("wifi_task", "#d5e8d4", FIELD,   "esp_wifi_scan()\n@ wifi_api.c:55"),
        ("sensor_task", "#fff8e1", "#e67e22", "i2c_read()\n@ i2c_drv.c:88"),
    ]

    box_w, box_h = 210, 130
    x_starts = [40, 300, 560]

    for i, ((tname, fill, cl, pc_info), x) in enumerate(zip(tasks, x_starts)):
        # Стек-блок
        frags.append(rect(x, 60, box_w, box_h, fill=fill, stroke=cl, sw=2, rx=8))
        frags.append(text(x + box_w // 2, 85, tname, size=13, bold=True, color=cl))

        # PC (де застиглий)
        frags.append(rect(x + 10, 95, box_w - 20, 48, fill="#ffffff", stroke=cl, sw=1, rx=4))
        frags.append(text(x + box_w // 2, 113, "PC застиг:", size=10, color=MUTED))
        frags.append(mtext(x + box_w // 2, 128, pc_info, size=10, color=cl, bold=True))

        # Стек окремо
        frags.append(text(x + box_w // 2, 165, "власний стек", size=10, color=MUTED))
        frags.append(rect(x + 30, 170, box_w - 60, 14, fill=cl, stroke=cl, sw=1, rx=2))

        # bt-підпис
        frags.append(text(x + box_w // 2, 205, f"bt #{i}: {tname}", size=10, color=cl))

    # Відлагоджувач показує всіх
    frags.append(rect(270, 240, 280, 55, fill=FILL, stroke=LINE, sw=2, rx=8))
    frags.append(text(410, 262, "Відлагоджувач", size=13, bold=True))
    frags.append(text(410, 280, "бачить ВСІ задачі і їхні стеки", size=11, color=INK))

    for x in x_starts:
        frags.append(line(x + box_w // 2, 215, 410, 240, color=MUTED, sw=1.2, dash="4,3"))

    # Висновок
    tb, _, _ = textbox(W // 2, H - 28,
                       "Відлагоджувач показує, де застрягла КОЖНА задача водночас — недосяжне для друку.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.5.3. RTOS: кожна задача — свій стек і свій застиглий PC.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-5-3-rtos-tasks-stacks.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.6.1 — Карта fault-регістрів Cortex-M
# ══════════════════════════════════════════════════════════════════════════════
def fig_cortexm_fault_regs():
    W, H = 840, 480
    frags = []

    frags.append(text(W // 2, 30, "Fault-регістри Cortex-M — довідкова карта", size=15, bold=True))

    # CFSR (головний)
    frags.append(rect(30, 50, W - 60, 55, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(W // 2, 70, "CFSR — Configurable Fault Status Register", size=13, bold=True, color=NEG))
    frags.append(text(W // 2, 90, "32-бітний: [31:16] UsageFault · [15:8] BusFault · [7:0] MemManage", size=11, color=INK))

    # Три підрегістри CFSR
    sub_regs = [
        ("UsageFault [31:16]", "#e67e22", "#fff8e1",
         ["DIVBYZERO — ділення на нуль", "UNALIGNED — невирівняний доступ",
          "UNDEFINSTR — невідома інструкція", "NOCP — немає співпроцесора"]),
        ("BusFault [15:8]", POS, "#fdecea",
         ["IMPRECISERR — неточна помилка (буфер)", "PRECISERR — точна помилка",
          "IBUSERR — помилка вибірки коду", "BFARVALID — BFAR валідний"]),
        ("MemManage [7:0]", FIELD, "#d5e8d4",
         ["IACCVIOL — немає доступу до коду", "DACCVIOL — немає доступу до даних",
          "MMARVALID — MMFAR валідний", "MUNSTKERR — відновлення стека"]),
    ]

    col_w = (W - 60) // 3
    for i, (sname, cl, sfill, bits) in enumerate(sub_regs):
        x = 30 + i * col_w
        frags.append(rect(x, 118, col_w - 4, 180, fill=sfill, stroke=cl, sw=1.8, rx=6))
        frags.append(text(x + col_w // 2, 138, sname, size=11, bold=True, color=cl))
        for j, bit in enumerate(bits):
            frags.append(text(x + 10, 158 + j * 34, bit, size=10, color=INK, anchor="start"))

    # HFSR
    frags.append(rect(30, 310, 250, 55, fill="#f9f2fc", stroke="#8e44ad", sw=1.8, rx=6))
    frags.append(text(155, 330, "HFSR", size=12, bold=True, color="#8e44ad"))
    frags.append(text(155, 350, "HardFault: FORCED, VECTTBL", size=10, color=INK))

    # MMFAR / BFAR
    frags.append(rect(300, 310, 230, 55, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    frags.append(text(415, 330, "MMFAR", size=12, bold=True, color=POS))
    frags.append(text(415, 350, "адреса помилки пам'яті (MemManage)", size=10, color=INK))

    frags.append(rect(550, 310, 230, 55, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    frags.append(text(665, 330, "BFAR", size=12, bold=True, color=POS))
    frags.append(text(665, 350, "адреса шинної помилки (BusFault)", size=10, color=INK))

    # Підказка imprecise
    tb, _, _ = textbox(415, 415,
                       "IMPRECISERR: через буфер запису — справжня адреса вже втрачена!\n(BFARVALID у цьому разі = 0)",
                       size=10, fill="#fff3cd", stroke="#e67e22", sw=1.5, color="#e67e22")
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.6.1. Карта fault-регістрів Cortex-M: біти і значення.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-6-1-cortexm-fault-regs.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.6.2 — Exception-фрейм: «передсмертна записка» на стеку
# ══════════════════════════════════════════════════════════════════════════════
def fig_exception_frame():
    W, H = 780, 440
    frags = []

    frags.append(text(W // 2, 30, "Exception-фрейм: ядро автоматично зберігає знімок збою", size=14, bold=True))

    # Стек зліва
    frame_items = [
        ("xPSR", "#e67e22", "стан процесора"),
        ("PC (Return Addr)", POS, "де саме впало! →"),
        ("LR", NEG, "звідки прийшли"),
        ("R12", MUTED, ""),
        ("R3", MUTED, ""),
        ("R2", MUTED, ""),
        ("R1", MUTED, ""),
        ("R0", MUTED, ""),
    ]

    cell_h = 36
    y0 = 60
    stack_x = 60

    for i, (name, cl, hint) in enumerate(frame_items):
        y = y0 + i * cell_h
        fill = "#fdecea" if cl == POS else ("#fff8e1" if cl == "#e67e22" else FILL)
        frags.append(rect(stack_x, y, 220, cell_h - 2, fill=fill, stroke=cl, sw=1.8, rx=4))
        frags.append(text(stack_x + 20, y + cell_h // 2 + 5, name, size=12,
                          bold=(cl == POS), color=cl, anchor="start"))
        if hint:
            frags.append(text(stack_x + 215, y + cell_h // 2 + 5, hint,
                              size=10, color=cl, anchor="end"))

    frags.append(text(stack_x + 110, y0 + len(frame_items) * cell_h + 14,
                      "↑ SP (перед входом в обробник)", size=10, color=MUTED))

    # Стрілка від PC до .elf
    pc_y = y0 + cell_h + cell_h // 2
    frags.append(arrow(280, pc_y, 380, pc_y, color=POS, sw=2.2))

    # .elf блок
    frags.append(rect(385, pc_y - 35, 175, 70, fill="#fff8e1", stroke="#e67e22", sw=1.8, rx=6))
    frags.append(text(472, pc_y - 15, "app.elf", size=13, bold=True, color="#e67e22"))
    frags.append(text(472, pc_y + 8,  "addr2line / GDB", size=10, color=MUTED))
    frags.append(text(472, pc_y + 25, "list *PC", size=10, color="#e67e22"))

    # Результат
    frags.append(arrow(560, pc_y, 640, pc_y, color=FIELD, sw=2.2))
    tb, _, _ = textbox(700, pc_y, "main.c:87\ncfg->rate = 100;", size=12,
                       fill="#d5e8d4", stroke=FIELD, sw=2, color=FIELD, bold=True)
    frags.append(tb)

    # Ядро зберігає автоматично
    tb2, _, _ = textbox(W // 2, H - 45,
                        "Ядро САМО зберігає знімок до виходу в обробник збою —\nлишається лише прочитати реєстри.",
                        size=11, fill="#eaf0fd", stroke=NEG, sw=1.5, color=NEG)
    frags.append(tb2)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.6.2. Ядро кладе «передсмертну записку» на стек — PC вказує, де саме впало.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-6-2-exception-frame.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.6.3 — Від адрес паніки до функцій і рядків (addr2line pipeline)
# ══════════════════════════════════════════════════════════════════════════════
def fig_addr2line_pipeline():
    W, H = 820, 380
    frags = []

    # Крок 1: панічний дамп
    frags.append(rect(20, 60, 200, 200, fill="#1e2030", stroke=POS, sw=2, rx=8))
    frags.append(text(120, 85, "Паніка ESP32", size=12, bold=True, color=POS))
    panic_lines = [
        "Backtrace:",
        "0x400D2ABC",
        "0x400D1F44",
        "0x400D0C12",
        "0x400C9BEE",
    ]
    for i, ln in enumerate(panic_lines):
        cl = "#aaaaaa" if i > 0 else "#ffffff"
        frags.append(text(30, 110 + i * 28, ln, size=10, color=cl, anchor="start"))

    # Стрілка + інструмент
    frags.append(arrow(220, 160, 310, 160, color="#e67e22", sw=2.2))

    frags.append(rect(315, 110, 190, 100, fill="#fff8e1", stroke="#e67e22", sw=2, rx=8))
    frags.append(text(410, 133, "idf.py monitor", size=12, bold=True, color="#e67e22"))
    frags.append(text(410, 152, "  або", size=11, color=MUTED))
    frags.append(text(410, 170, "xtensa-…-addr2line", size=11, color="#e67e22"))
    frags.append(text(410, 190, "+ app.elf (той самий!)", size=10, color=POS))

    # Стрілка до результату
    frags.append(arrow(505, 160, 580, 160, color=FIELD, sw=2.2))

    # Результат: функції + рядки
    frags.append(rect(585, 60, 210, 200, fill="#d5e8d4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(690, 85, "Результат", size=12, bold=True, color=FIELD))
    result_lines = [
        "crash_handler()",
        "  fault.c:87",
        "process_packet()",
        "  proto.c:234",
        "app_main()",
        "  main.c:42",
    ]
    for i, ln in enumerate(result_lines):
        cl = FIELD if i % 2 == 0 else MUTED
        frags.append(text(595, 110 + i * 24, ln, size=10, color=cl, anchor="start"))

    # Попередження про .elf
    tb, _, _ = textbox(W // 2 - 10, H - 45,
                       "Потрібен РІВНО той app.elf, що прошитий — інший .elf дасть хибні рядки!",
                       size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.6.3. Адреси без .elf — німі числа; з .elf — читана траса падіння.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-6-3-addr2line-pipeline.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.7.1 — Часова вісь посмертного аналізу
# ══════════════════════════════════════════════════════════════════════════════
def fig_postmortem_timeline():
    W, H = 860, 380
    frags = []

    # Часова вісь
    frags.append(arrow(40, 180, W - 30, 180, color=LINE, sw=2.5))
    frags.append(text(W - 20, 184, "t", size=14, bold=True))

    events = [
        (80,  "Нормальна\nробота", "#d5e8d4", FIELD),
        (230, "ЗБІЙ\n(panic)", "#fdecea", POS),
        (390, "Обробник зберігає\ncore dump → Flash", "#fff8e1", "#e67e22"),
        (560, "Reboot\n(робота)", "#d5e8d4", FIELD),
        (730, "Офлайн-аналіз\n(дні по тому)", "#eaf0fd", NEG),
    ]

    for x, lbl, fill, cl in events:
        # Вертикальна позначка
        frags.append(line(x, 165, x, 195, color=cl, sw=2.5))
        # Блок
        tb, bw, bh = textbox(x, 130, lbl, size=11, fill=fill, stroke=cl, sw=1.8, color=cl, bold=True)
        frags.append(tb)

    # Дужка «живий зонд має бути тут»
    frags.append(line(230, 230, 560, 230, color=POS, sw=2, dash="5,3"))
    frags.append(text(395, 248, "живий зонд: потрібен у момент збою", size=10, color=POS))

    # Дужка «core dump: аналіз потім»
    frags.append(line(390, 270, 730, 270, color=NEG, sw=2))
    frags.append(text(560, 288, "core dump: аналіз у будь-який час", size=10, color=NEG, bold=True))

    tb2, _, _ = textbox(W // 2, H - 30,
                        "Core dump відв'язує момент збою від моменту розслідування.",
                        size=11, fill="#eaf0fd", stroke=NEG, sw=1.2, color=NEG)
    frags.append(tb2)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.7.1. Часова вісь посмертного аналізу.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-7-1-postmortem-timeline.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.7.2 — З чого складається core dump
# ══════════════════════════════════════════════════════════════════════════════
def fig_coredump_anatomy():
    W, H = 820, 440
    frags = []

    # Дамп — ліворуч
    frags.append(rect(30, 50, 300, 310, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    frags.append(text(180, 75, "Core Dump (бінарний файл)", size=13, bold=True, color=NEG))

    sections = [
        ("Заголовок", "#d0d8f0", "версія, чипсет, причина"),
        ("Регістри CPU", "#fdecea", "всіх задач (PC, SP, LR, …)"),
        ("Стек app_task", "#d5e8d4", "повний зріз"),
        ("Стек wifi_task", "#d5e8d4", "повний зріз"),
        ("Ключові глобальні", "#fff8e1", "обрані ділянки RAM"),
    ]
    y = 95
    for sname, sfill, sdesc in sections:
        frags.append(rect(40, y, 280, 44, fill=sfill, stroke=LINE, sw=1, rx=4))
        frags.append(text(180, y + 16, sname, size=12, bold=True, color=INK))
        frags.append(text(180, y + 33, sdesc, size=9, color=MUTED))
        y += 48

    # Межа: не вся пам'ять
    frags.append(text(180, 370, "⚠ уся RAM не влазить —", size=10, color=POS))
    frags.append(text(180, 386, "зберігають стеки + ключове", size=10, color=POS))

    # .elf — посередині як «словник»
    frags.append(rect(360, 165, 160, 80, fill="#fff8e1", stroke="#e67e22", sw=2, rx=8))
    frags.append(text(440, 190, "app.elf", size=15, bold=True, color="#e67e22"))
    frags.append(text(440, 212, "«словник»", size=11, color="#e67e22"))
    frags.append(text(440, 230, "адреса → ім'я", size=10, color=MUTED))

    # Стрілки від дампа і .elf до GDB
    frags.append(arrow(330, 200, 360, 200, color=NEG, sw=2))
    frags.append(arrow(520, 200, 590, 200, color="#e67e22", sw=2))

    # GDB офлайн
    frags.append(rect(595, 140, 190, 130, fill="#d5e8d4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(690, 165, "GDB офлайн", size=13, bold=True, color=FIELD))
    frags.append(text(690, 185, "backtrace", size=11, color=FIELD))
    frags.append(text(690, 203, "info threads", size=11, color=FIELD))
    frags.append(text(690, 221, "print VAR", size=11, color=FIELD))
    frags.append(text(690, 240, "(без живого чипа!)", size=10, color=MUTED))

    # Підпис
    tb, _, _ = textbox(W // 2, H - 30,
                       "Дамп — компактний кадр моменту смерті, читаний лише разом зі своїм .elf.",
                       size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=FIELD)
    frags.append(tb)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.7.2. З чого складається core dump і що дає .elf.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-7-2-coredump-anatomy.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.7.3 — Дерево рішень: два шляхи розслідування
# ══════════════════════════════════════════════════════════════════════════════
def fig_debug_decision_tree():
    W, H = 820, 500
    frags = []

    # Корінь
    tb_root, rw, rh = textbox(W // 2, 50, "Пристрій спинився / впав", size=14,
                               fill="#2d3e50", stroke=LINE, sw=2, color="#ffffff",
                               bold=True, min_w=280)
    frags.append(tb_root)

    # Питання
    tb_q, _, _ = textbox(W // 2, 120, "Зонд підключений?\nМомент збою «живий»?", size=13,
                          fill=FILL, stroke="#e67e22", sw=2, color="#e67e22", bold=True)
    frags.append(tb_q)
    frags.append(arrow(W // 2, 68, W // 2, 100, color=LINE, sw=2))
    frags.append(arrow(W // 2, 140, W // 2, 155, color=LINE, sw=2))
    frags.append(line(W // 2, 155, 215, 155, color=LINE, sw=2))
    frags.append(line(W // 2, 155, 605, 155, color=LINE, sw=2))
    frags.append(arrow(215, 155, 215, 185, color=FIELD, sw=2))
    frags.append(arrow(605, 155, 605, 185, color=NEG, sw=2))
    frags.append(text(170, 168, "ТАК", size=12, bold=True, color=FIELD))
    frags.append(text(620, 168, "НІ", size=12, bold=True, color=POS))

    # Гілка А: живе налагодження
    frags.append(rect(50, 185, 325, 230, fill="#d5e8d4", stroke=FIELD, sw=2, rx=10))
    frags.append(text(213, 208, "Гілка А: Живе налагодження", size=13, bold=True, color=FIELD))
    a_steps = [
        "halt + зонд (4.14.2)",
        "брейк/вотч (4.14.3)",
        "OpenOCD + GDB (4.14.4)",
        "backtrace + фрейми (4.14.5)",
        "розбір HardFault (4.14.6)",
    ]
    for i, s in enumerate(a_steps):
        frags.append(text(70, 228 + i * 34, "▸ " + s, size=11, color=INK, anchor="start"))

    # Гілка Б: посмертний аналіз
    frags.append(rect(445, 185, 325, 230, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    frags.append(text(607, 208, "Гілка Б: Посмертний аналіз", size=13, bold=True, color=NEG))
    b_steps = [
        "причина reset (§4.1.8)",
        "core dump у Flash (4.14.7)",
        "idf.py coredump-info",
        "офлайн-backtrace + .elf",
        "fault-регістри з дампа",
    ]
    for i, s in enumerate(b_steps):
        frags.append(text(465, 228 + i * 34, "▸ " + s, size=11, color=INK, anchor="start"))

    # Висновок
    tb2, _, _ = textbox(W // 2, H - 38,
                        "Вибір шляху диктують доступність зонда і те, чи момент збою ще «живий».",
                        size=11, fill=FILL, stroke=LINE, sw=1.2, color=INK)
    frags.append(tb2)

    frags.append(text(W // 2, H - 10, "Рис. 4.14.7.3. Зведення розділу: два шляхи розслідування — живий зонд або посмертний дамп.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r14-7-3-debug-decision-tree.svg"), W, H, *frags)


# ══════════════════════════════════════════════════════════════════════════════
# Точка входу
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("Generuyu figury dlya Rozdilu 4.14...")
    fig_print_vs_halt()
    print("  OK fig-r14-1-1-print-vs-halt.svg")
    fig_print_vs_debugger_table()
    print("  OK fig-r14-1-2-print-vs-debugger-table.svg")
    fig_debug_port_into_core()
    print("  OK fig-r14-2-1-debug-port-into-core.svg")
    fig_scan_chain()
    print("  OK fig-r14-2-2-scan-chain.svg")
    fig_jtag_vs_swd()
    print("  OK fig-r14-2-3-jtag-vs-swd.svg")
    fig_esp32_jtag_pins()
    print("  OK fig-r14-2-4-esp32-jtag-pins.svg")
    fig_hw_breakpoint_comparator()
    print("  OK fig-r14-3-1-hw-breakpoint-comparator.svg")
    fig_sw_breakpoint_swap()
    print("  OK fig-r14-3-2-sw-breakpoint-swap.svg")
    fig_watchpoint_data()
    print("  OK fig-r14-3-3-watchpoint-data.svg")
    fig_probe_openocd_gdb()
    print("  OK fig-r14-4-1-probe-openocd-gdb.svg")
    fig_gdb_command_map()
    print("  OK fig-r14-4-3-gdb-command-map.svg")
    fig_stack_to_frames()
    print("  OK fig-r14-5-1-stack-to-frames.svg")
    fig_step_next_finish()
    print("  OK fig-r14-5-2-step-next-finish.svg")
    fig_rtos_tasks_stacks()
    print("  OK fig-r14-5-3-rtos-tasks-stacks.svg")
    fig_cortexm_fault_regs()
    print("  OK fig-r14-6-1-cortexm-fault-regs.svg")
    fig_exception_frame()
    print("  OK fig-r14-6-2-exception-frame.svg")
    fig_addr2line_pipeline()
    print("  OK fig-r14-6-3-addr2line-pipeline.svg")
    fig_postmortem_timeline()
    print("  OK fig-r14-7-1-postmortem-timeline.svg")
    fig_coredump_anatomy()
    print("  OK fig-r14-7-2-coredump-anatomy.svg")
    fig_debug_decision_tree()
    print("  OK fig-r14-7-3-debug-decision-tree.svg")
    print("Done! All SVGs in", OUT)
