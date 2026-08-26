# -*- coding: utf-8 -*-
"""Фігури до теми «Способи залити прошивку: SWD, DFU, UART-завантажувач, накопичувач».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Таксономія способів прошивки: чотири шляхи до кремнію ─────────────────
def fig_flashing_taxonomy():
    W, H = 840, 470
    f = [text(W / 2, 28, "Чотири шляхи доставки коду у Flash мікроконтролера", size=15, bold=True)]

    # 4 колонки: SWD/JTAG, UART ROM, USB DFU, USB UF2
    cols = [
        ("SWD / JTAG", "Апаратний зонд", POS, "#fdecea", [
            "Фізичний рівень: SWDIO, SWCLK",
            "Вузол МК: CoreSight DAP (SW-DP)",
            "Доступ: прямий до шини (AHB-AP)",
            "Код у МК: не потрібен (в залізі)",
            "Відлагодження: покрокове, зупинки"
        ]),
        ("UART Bootloader", "Заводський ROM", "#d35400", "#fef5e7", [
            "Фізичний рівень: RX / TX (UART)",
            "Вузол МК: системне Mask ROM",
            "Активація: вивід BOOT0 = 1",
            "Протокол: кадри команд + XOR",
            "Призначення: завод, порятунок"
        ]),
        ("USB DFU", "Стандартний USB-клас", NEG, "#eaf0fd", [
            "Фізичний рівень: USB D+ / D−",
            "Вузол МК: нативний USB + DFU",
            "Клас USB: 0xFE (App Specific)",
            "Канал: Control Endpoint 0 (EP0)",
            "Призначення: польове оновлення"
        ]),
        ("Накопичувач UF2", "Віртуальний FAT12", FIELD, "#eafaf1", [
            "Фізичний рівень: USB D+ / D− (MSC)",
            "Вузол МК: USB Mass Storage ROM",
            "Емуляція: віртуальний диск RAM",
            "Формат: 512-байтні блоки .uf2",
            "Призначення: DIY, освіта, Drag"
        ]),
    ]

    col_w = 180
    gap = 16
    start_x = (W - (4 * col_w + 3 * gap)) / 2
    top_y = 65
    card_h = 325

    for i, (title, subtitle, col, fill, lines) in enumerate(cols):
        cx = start_x + i * (col_w + gap)
        f.append(rect(cx, top_y, col_w, card_h, fill=fill, stroke=col, sw=1.8, rx=6))
        f.append(text(cx + col_w / 2, top_y + 24, title, size=13, bold=True, color=col))
        f.append(text(cx + col_w / 2, top_y + 42, subtitle, size=10.5, italic=True, color=MUTED))
        f.append(line(cx + 10, top_y + 54, cx + col_w - 10, top_y + 54, color=col, sw=1.0))

        ly = top_y + 76
        for line_txt in lines:
            parts = line_txt.split(":", 1)
            f.append(text(cx + 10, ly, parts[0] + ":", size=10, bold=True, color=INK, anchor="start"))
            if len(parts) > 1:
                val = parts[1].strip()
                f.append(text(cx + 14, ly + 15, val, size=10, color=MUTED, anchor="start"))
            ly += 46

    b, _, _ = textbox(W / 2, 430,
                      "Кожен спосіб відповідає різним вимогам: прямий апаратний контроль, незнищенний заводський порятунок,\n"
                      "оновлення без програматора за стандартом USB або користувацьке перетягування файлу без софту.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "flashing-taxonomy.svg"), W, H, *f)


# ── 2. Архітектура CoreSight DAP та прямий доступ до пам'яті через SWD ────────
def fig_swd_dap_access():
    W, H = 840, 440
    f = [text(W / 2, 28, "Апаратний доступ до шин і Flash мікроконтролера через CoreSight DAP", size=15, bold=True)]

    # Ліва частина: ПК та налагоджувальний зонд
    f.append(rect(30, 75, 140, 190, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(100, 100, "ПК / Тулчейн", size=12.5, bold=True))
    f.append(text(100, 122, "OpenOCD / probe-rs", size=10.5, color=MUTED))
    f.append(text(100, 140, "pyOCD / st-flash", size=10.5, color=MUTED))
    f.append(line(45, 155, 155, 155, color=MUTED, sw=1))
    f.append(rect(45, 175, 110, 65, fill="#fff", stroke=POS, sw=1.5, rx=4))
    f.append(text(100, 200, "Зонд (Probe)", size=11, bold=True, color=POS))
    f.append(text(100, 220, "ST-Link / J-Link", size=10, color=MUTED))

    # Лінії SWD між зондом і МК
    f.append(arrow(155, 195, 230, 195, color=POS, sw=2))
    f.append(arrow(230, 220, 155, 220, color=POS, sw=2))
    f.append(text(192, 185, "SWDIO", size=10.5, bold=True, color=POS))
    f.append(text(192, 238, "SWCLK", size=10.5, bold=True, color=POS))

    # Права частина: Внутрішня структура кремнію МК
    f.append(rect(235, 65, 575, 295, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    f.append(text(522, 90, "Кремній мікроконтролера (MCU SoC)", size=13, bold=True, color="#2c3e50"))

    # Блок CoreSight DAP
    f.append(rect(255, 115, 180, 225, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    f.append(text(345, 138, "CoreSight DAP", size=12, bold=True, color=POS))
    f.append(text(345, 155, "Debug Access Port", size=10, italic=True, color=MUTED))

    # SW-DP і AHB-AP всередині DAP
    f.append(rect(270, 170, 150, 55, fill="#fff", stroke=POS, sw=1.3, rx=4))
    f.append(text(345, 192, "SW-DP", size=11, bold=True, color=POS))
    f.append(text(345, 210, "Послідовний порт дебагу", size=9.5, color=MUTED))

    f.append(arrow(345, 225, 345, 250, color=POS, sw=1.5))

    f.append(rect(270, 250, 150, 75, fill="#fff", stroke=POS, sw=1.3, rx=4))
    f.append(text(345, 270, "MEM-AP / AHB-AP", size=11, bold=True, color=POS))
    f.append(text(345, 288, "Транслятор SWD → шина", size=9.5, color=MUTED))
    f.append(text(345, 306, "Прямий доступ у пам'ять", size=9.5, bold=True, color=POS))

    # Матриця шин (Bus Matrix)
    f.append(arrow(420, 287, 475, 287, color=INK, sw=2))
    f.append(rect(475, 115, 75, 225, fill="#eef1f4", stroke=LINE, sw=1.5, rx=4))
    f.append(text(512, 170, "Ш", size=12, bold=True))
    f.append(text(512, 195, "И", size=12, bold=True))
    f.append(text(512, 220, "Н", size=12, bold=True))
    f.append(text(512, 245, "А", size=12, bold=True))
    f.append(text(512, 280, "AHB/AXI", size=9.5, color=MUTED))

    # Права підсистема: Ядро CPU, SRAM, Flash Controller
    # Ядро CPU
    f.append(rect(585, 115, 205, 65, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(687, 138, "Ядро процесора (CPU)", size=11, bold=True, color=NEG))
    f.append(text(687, 156, "FPB (точки зупину), DWT", size=9.5, color=MUTED))
    f.append(arrow(550, 147, 585, 147, color=NEG, sw=1.5))

    # SRAM
    f.append(rect(585, 195, 205, 65, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(687, 218, "Оперативна пам'ять (SRAM)", size=11, bold=True, color=FIELD))
    f.append(text(687, 236, "Завантаження RAM-стаба", size=9.5, color=MUTED))
    f.append(arrow(550, 227, 585, 227, color=FIELD, sw=1.5))

    # Контролер Flash пам'яті
    f.append(rect(585, 275, 205, 65, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=4))
    f.append(text(687, 298, "Контролер Flash пам'яті", size=11, bold=True, color="#d35400"))
    f.append(text(687, 316, "Регістри CR/SR + NOR Flash", size=9.5, color=MUTED))
    f.append(arrow(550, 307, 585, 307, color="#d35400", sw=1.5))

    b, _, _ = textbox(W / 2, 400,
                      "DAP працює незалежно від процесорного ядра: зонд через AHB-AP може читати й писати SRAM,\n"
                      "керувати контролером Flash і завантажувати швидкісний RAM-стаб, навіть коли ядро спить чи зависло.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "swd-dap-access.svg"), W, H, *f)


# ── 3. Послідовність прошивки через системний UART ROM-завантажувач ────────────
def fig_uart_bootloader_flow():
    W, H = 840, 520
    f = [text(W / 2, 28, "Протокол роботи заводського ROM-завантажувача через UART", size=15, bold=True)]

    # Дві вертикальні лінії: Хост (ПК) та Завантажувач МК (ROM)
    hx = 160
    mx = 680

    f.append(rect(hx - 70, 55, 140, 36, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(hx, 78, "Хост (stm32flash)", size=12, bold=True, color=NEG))

    f.append(rect(mx - 70, 55, 140, 36, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=4))
    f.append(text(mx, 78, "МК (ROM Bootloader)", size=12, bold=True, color="#d35400"))

    f.append(line(hx, 91, hx, 435, color=NEG, sw=1.5, dash="4,4"))
    f.append(line(mx, 91, mx, 435, color="#d35400", sw=1.5, dash="4,4"))

    # Покроковий обмін
    steps = [
        # (y, dir, label, subtext, color)
        (120, "h->m", "BOOT0 = 1 + Імпульс NRST", "Активація системної пам'яті (ROM) при скиданні", MUTED),
        (165, "h->m", "Байт 0x7F (Синхронізація)", "Автокалібрування швидкості UART за тривалістю біта", NEG),
        (195, "m->h", "0x79 (ACK)", "Завантажувач зафіксував Baud Rate і готовий", "#d35400"),
        (240, "h->m", "Команда 0x44 + 0xBB (Extended Erase)", "Запит на стирання Flash пам'яті перед записом", NEG),
        (270, "m->h", "0x79 (ACK) → Масове або посторінкове стирання", "Контролер Flash очищує сектори у стан 0xFF", "#d35400"),
        (315, "h->m", "Команда 0x31 + 0xCE (Write Memory) + Адреса + XOR", "Передача цільової адреси Flash (напр. 0x08000000)", NEG),
        (345, "m->h", "0x79 (ACK) — адреса коректна", "Завантажувач очікує блок даних", "#d35400"),
        (385, "h->m", "Кількість N (256 байт) + Данні образу + Контрольна сума", "Посторінкова передача двійкового образу прошивки", NEG),
        (415, "m->h", "0x79 (ACK) — сектор успішно прошито", "Запис завершено; перехід до наступного блоку або Go 0x21", FIELD),
    ]

    for y, direction, main_txt, sub_txt, col in steps:
        if direction == "h->m":
            f.append(arrow(hx + 10, y, mx - 10, y, color=col, sw=1.8))
            f.append(text((hx + mx) / 2, y - 8, main_txt, size=10.5, bold=True, color=col))
            f.append(text((hx + mx) / 2, y + 14, sub_txt, size=9.5, color=MUTED))
        else:
            f.append(arrow(mx - 10, y, hx + 10, y, color=col, sw=1.8))
            f.append(text((hx + mx) / 2, y - 8, main_txt, size=10.5, bold=True, color=col))
            f.append(text((hx + mx) / 2, y + 14, sub_txt, size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 480,
                      "Протокол UART ROM гарантує надійність: кожен байт команди дублюється інверсним (C XOR ~C = 0xFF),\n"
                      "а швидкість визначається за першим стартовим бітом без потреби у високоточному кварці.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "uart-bootloader-flow.svg"), W, H, *f)


# ── 4. Емуляція віртуального накопичувача FAT12 та структура блоку UF2 ─────────
def fig_uf2_fat12_mapping():
    W, H = 840, 480
    f = [text(W / 2, 28, "Як працює UF2: емуляція FAT12 у RAM та перетворення на запис у Flash", size=15, bold=True)]

    # Верхній шар: Віртуальний диск на ПК
    f.append(rect(35, 65, 345, 160, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(207, 88, "Віртуальний USB-накопичувач (ПК)", size=12, bold=True, color=NEG))
    f.append(text(207, 106, "Розпізнається як звичайна флешка (RPI-RP2)", size=10, color=MUTED))

    # Файли на віртуальному диску
    f.append(rect(50, 120, 145, 45, fill="#fff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(122, 140, "INFO_UF2.TXT", size=10, bold=True))
    f.append(text(122, 155, "Версія завантажувача", size=9.5, color=MUTED))

    f.append(rect(215, 120, 145, 45, fill="#fff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(287, 140, "INDEX.HTM", size=10, bold=True))
    f.append(text(287, 155, "Посилання на мануал", size=9.5, color=MUTED))

    f.append(rect(50, 175, 310, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(205, 193, "Користувач перетягує firmware.uf2", size=10.5, bold=True, color=POS))
    f.append(text(205, 207, "ОС надсилає SCSI WRITE (10) секторами по 512 байт", size=9.5, color=MUTED))

    # Стрілка вниз до обробника завантажувача
    f.append(arrow(205, 225, 205, 255, color=POS, sw=2))

    # Середній блок: Структура блоку UF2 (512 байт)
    f.append(rect(405, 65, 395, 190, fill="#fef5e7", stroke="#d35400", sw=1.8, rx=6))
    f.append(text(602, 88, "Анатомія блоку UF2 (рівно 512 байт)", size=12, bold=True, color="#d35400"))

    # Поля структури UF2
    uf2_fields = [
        ("MagicStart0 & 1", "0x0A324655, 0x9E5D5157", POS),
        ("TargetAddr", "Абсолютна адреса Flash (напр. 0x10000000)", INK),
        ("PayloadSize", "Кількість корисних даних (зазвичай 256 B)", INK),
        ("BlockNo / NumBlocks", "Порядковий номер блоку / загальна к-ть", INK),
        ("FamilyID", "Ідентифікатор чіпа (RP2040: 0xe48ff56e)", NEG),
        ("Data Payload (476B)", "256 корисних байт прошивки + паддінг", FIELD),
        ("MagicEnd", "0x0AB16414", POS),
    ]

    fy = 108
    for name, val, col in uf2_fields:
        f.append(rect(420, fy, 365, 18, fill="#fff", stroke=LINE, sw=0.8, rx=2))
        f.append(text(430, fy + 13, name, size=9.5, bold=True, color=col, anchor="start"))
        f.append(text(775, fy + 13, val, size=9.5, color=MUTED, anchor="end"))
        fy += 20

    # Нижній шар: Фізичний запис у Flash
    f.append(rect(35, 275, 765, 120, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(W / 2, 298, "Дії UF2-завантажувача на мікроконтролері на льоту", size=12.5, bold=True, color=FIELD))

    f.append(rect(55, 315, 220, 65, fill="#fff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(165, 335, "1. Перехоплення сектора", size=10.5, bold=True))
    f.append(text(165, 352, "Звірка Magic чисел та", size=9.5, color=MUTED))
    f.append(text(165, 368, "відповідності FamilyID", size=9.5, color=MUTED))

    f.append(arrow(275, 347, 305, 347, color=FIELD, sw=1.5))

    f.append(rect(305, 315, 230, 65, fill="#fff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(420, 335, "2. Витягування 256 байт", size=10.5, bold=True))
    f.append(text(420, 352, "Ігнорування FAT-таблиць;", size=9.5, color=MUTED))
    f.append(text(420, 368, "прямий запис за TargetAddr", size=9.5, color=MUTED))

    f.append(arrow(535, 347, 565, 347, color=FIELD, sw=1.5))

    f.append(rect(565, 315, 220, 65, fill="#fff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(675, 335, "3. Фінал і перезапуск", size=10.5, bold=True))
    f.append(text(675, 352, "Отримано BlockNo = NumBlocks;", size=9.5, color=MUTED))
    f.append(text(675, 368, "виклик NVIC_SystemReset()", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 440,
                      "Завантажувачу не потрібно парсити складну файлову систему: кожен 512-байтний сектор UF2\n"
                      "самодостатній і несе в собі точну адресу Flash, перетворюючи drag-and-drop на посторінковий запис.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "uf2-fat12-mapping.svg"), W, H, *f)


# ── 5. Інженерна матриця вибору способу прошивки ──────────────────────────────
def fig_flashing_selection_matrix():
    W, H = 840, 460
    f = [text(W / 2, 28, "Дерево рішень: який інтерфейс прошивки обрати під ваше завдання", size=15, bold=True)]

    # Головне питання зліва
    f.append(rect(35, 180, 165, 75, fill="#f4f6f8", stroke=LINE, sw=2, rx=6))
    f.append(text(117, 205, "Який етап життєвого", size=11, bold=True))
    f.append(text(117, 222, "циклу пристрою?", size=11, bold=True))
    f.append(text(117, 240, "(головна вимога)", size=10, italic=True, color=MUTED))

    # 4 гілки вибору
    branches = [
        # (y, title, cond1, cond2, choice, col, fill, tools)
        (75, "Активна розробка та дебаг", "Потрібні breakpoints, покрокове виконання,", "перевірка змінних та пам'яті ядра",
         "SWD / JTAG", POS, "#fdecea", "OpenOCD, probe-rs, ST-Link, J-Link"),
        (165, "Серійне заводське виробництво", "Чистий кремній з фабрики, мінімум", "виведених ліній на платі, швидкість",
         "SWD голками / UART ROM", "#d35400", "#fef5e7", "Пого-піни тестового джига, stm32flash"),
        (255, "Польове / сервісне оновлення", "Герметичний корпус, є виведений роз'єм USB,", "без окремого апаратного програматора",
         "USB DFU", NEG, "#eaf0fd", "Утиліта dfu-util, фірмовий скрипт OTA/USB"),
        (345, "Освіта, DIY та кінцеві клієнти", "Нуль встановленого софту в системі,", "drag-and-drop у звичайному провіднику",
         "USB UF2", FIELD, "#eafaf1", "RP2040 BOOTSEL, MakeCode, CircuitPython"),
    ]

    for y, stage_title, cond1, cond2, choice_txt, col, fill, tools_txt in branches:
        f.append(line(200, 217, 235, y + 35, color=col, sw=1.6))
        f.append(arrow(235, y + 35, 260, y + 35, color=col, sw=1.6))

        f.append(rect(260, y, 280, 70, fill="#fff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(270, y + 22, stage_title, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(270, y + 42, cond1, size=9.5, color=MUTED, anchor="start"))
        f.append(text(270, y + 56, cond2, size=9.5, color=MUTED, anchor="start"))

        f.append(arrow(540, y + 35, 565, y + 35, color=col, sw=1.6))

        f.append(rect(565, y, 240, 70, fill=fill, stroke=col, sw=1.8, rx=5))
        f.append(text(685, y + 26, choice_txt, size=12.5, bold=True, color=col))
        f.append(text(685, y + 48, tools_txt, size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 430,
                      "Універсального способу не існує: SWD незамінний на столі розробника й тестовому джизі,\n"
                      "ROM UART рятує при повній аварії, DFU оновлює серійний виріб, а UF2 усуває бар'єр входу для користувача.",
                      size=10.5, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "flashing-selection-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_flashing_taxonomy()
    fig_swd_dap_access()
    fig_uart_bootloader_flow()
    fig_uf2_fat12_mapping()
    fig_flashing_selection_matrix()
    print("All figures generated successfully.")
