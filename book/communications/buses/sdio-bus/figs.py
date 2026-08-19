# -*- coding: utf-8 -*-
"""Фігури теми «Шина SDIO» (book/communications/buses/sdio-bus).
Чистий Python без зовнішніх залежностей; svgkit імпортується зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння архітектури SD Memory та SDIO Multi-Function ────────────────
def fig_sdio_vs_sd_architecture():
    W, H = 940, 520
    p = []

    # Заголовок
    p.append(text(W/2, 28, "Порівняння архітектури: карта пам'яті SD проти мультифункціонального пристрою SDIO", size=17, bold=True))
    p.append(text(W/2, 48, "Один фізичний інтерфейс — принципово різні моделі адресації, паралелізму та обробки подій", size=12, color=MUTED, italic=True))

    # Ліва колонка: SD Memory Card
    x_left = 40
    w_col = 410
    y_top = 70
    h_col = 425
    p.append(rect(x_left, y_top, w_col, h_col, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    p.append(rect(x_left, y_top, w_col, 36, fill="#eaeded", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(x_left + w_col/2, y_top + 23, "Карта пам'яті SD (SD Memory Card)", size=14, bold=True, color=INK))

    # Складові SD Memory
    p.append(rect(x_left + 20, y_top + 55, w_col - 40, 48, fill="#ebf5fb", stroke=NEG, sw=1.2, rx=6))
    p.append(text(x_left + w_col/2, y_top + 75, "Фізичний інтерфейс: CLK, CMD, DAT[0..3]", size=12, bold=True, color=NEG))
    p.append(text(x_left + w_col/2, y_top + 92, "Спільний фізичний рівень SD-роз'єму", size=10.5, color=MUTED))

    p.append(rect(x_left + 20, y_top + 118, w_col - 40, 58, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    p.append(text(x_left + w_col/2, y_top + 138, "Модель адресації: LBA (блокова пам'ять)", size=12, bold=True, color="#7d6608"))
    p.append(text(x_left + w_col/2, y_top + 154, "Фіксовані сектори 512 байтів · CMD17/18 (Read), CMD24/25 (Write)", size=10, color=MUTED))
    p.append(text(x_left + w_col/2, y_top + 167, "Немає прямого доступу до окремих регістрів керування", size=9.5, color=POS))

    p.append(rect(x_left + 20, y_top + 190, w_col - 40, 68, fill="#fdf2e9", stroke="#e59866", sw=1.2, rx=6))
    p.append(text(x_left + w_col/2, y_top + 210, "Контролер FTL (Flash Translation Layer)", size=12, bold=True, color="#935116"))
    p.append(text(x_left + w_col/2, y_top + 228, "Wear-leveling, збирання сміття, трансляція LBA → NAND", size=10, color=MUTED))
    p.append(text(x_left + w_col/2, y_top + 244, "Недетерміновані затримки зайнятості (BUSY на DAT0)", size=10, color=POS))

    p.append(rect(x_left + 20, y_top + 272, w_col - 40, 62, fill="#fdedec", stroke=POS, sw=1.2, rx=6))
    p.append(text(x_left + w_col/2, y_top + 292, "Модель керування подіями: Пасивна", size=12, bold=True, color=POS))
    p.append(text(x_left + w_col/2, y_top + 310, "Карта ніколи не ініціює обмін самостійно", size=10, color=MUTED))
    p.append(text(x_left + w_col/2, y_top + 324, "Відсутній апаратний механізм переривань хоста", size=10, color=POS))

    p.append(rect(x_left + 20, y_top + 348, w_col - 40, 60, fill="#f8f9f9", stroke=MUTED, sw=1, rx=4))
    p.append(text(x_left + w_col/2, y_top + 368, "Призначення: масивне енергонезалежне сховище", size=11, bold=True, color=INK))
    p.append(text(x_left + w_col/2, y_top + 386, "Один логічний простір даних без внутрішньої мультиплексії", size=10, color=MUTED))
    p.append(text(x_left + w_col/2, y_top + 399, "Ініціалізація: CMD0 → CMD8 → ACMD41", size=9.5, color=MUTED))

    # Права колонка: SDIO Multi-Function Device
    x_right = 490
    p.append(rect(x_right, y_top, w_col, h_col, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    p.append(rect(x_right, y_top, w_col, 36, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x_right + w_col/2, y_top + 23, "Пристрій SDIO (SDIO Multi-Function Device)", size=14, bold=True, color="#117864"))

    # Складові SDIO
    p.append(rect(x_right + 20, y_top + 55, w_col - 40, 48, fill="#ebf5fb", stroke=NEG, sw=1.2, rx=6))
    p.append(text(x_right + w_col/2, y_top + 75, "Фізичний інтерфейс: CLK, CMD, DAT[0..3]", size=12, bold=True, color=NEG))
    p.append(text(x_right + w_col/2, y_top + 92, "Сумісний 1-бітний / 4-бітний роз'єм або впаяна мікросхема", size=10.5, color=MUTED))

    # Function 0 (CIA)
    p.append(rect(x_right + 20, y_top + 114, w_col - 40, 68, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=6))
    p.append(text(x_right + w_col/2, y_top + 133, "Функція 0: CIA (Common Information Area)", size=11.5, bold=True, color=NEG))
    p.append(text(x_right + w_col/2, y_top + 149, "Регістри CCCR (керування шиною, частотою, шиною переривань)", size=10, color=INK))
    p.append(text(x_right + w_col/2, y_top + 163, "Регістри FBR (властивості функцій 1..7) + CIS кортежі ідентифікації", size=9.5, color=MUTED))
    p.append(text(x_right + w_col/2, y_top + 175, "Доступ: 1-байтові команди CMD52 / burst CMD53", size=9.5, color="#1a5276"))

    # Functions 1..7 (Wi-Fi, BT, etc.)
    p.append(rect(x_right + 20, y_top + 190, (w_col - 48)/2, 70, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(x_right + 20 + (w_col - 48)/4, y_top + 209, "Функція 1: Wi-Fi MAC", size=10.5, bold=True, color=FIELD))
    p.append(text(x_right + 20 + (w_col - 48)/4, y_top + 225, "TX/RX FIFO черги", size=9.5, color=INK))
    p.append(text(x_right + 20 + (w_col - 48)/4, y_top + 239, "Розмір блока: 512 Б", size=9.5, color=MUTED))
    p.append(text(x_right + 20 + (w_col - 48)/4, y_top + 252, "Окремий IRQ статус", size=9.5, color="#196f3d"))

    p.append(rect(x_right + 20 + (w_col - 48)/2 + 8, y_top + 190, (w_col - 48)/2, 70, fill="#f4ecf7", stroke="#8e44ad", sw=1.2, rx=6))
    p.append(text(x_right + 20 + 3*(w_col - 48)/4 + 8, y_top + 209, "Функція 2: Bluetooth HCI", size=10.5, bold=True, color="#8e44ad"))
    p.append(text(x_right + 20 + 3*(w_col - 48)/4 + 8, y_top + 225, "HCI пакети команд/UART", size=9.5, color=INK))
    p.append(text(x_right + 20 + 3*(w_col - 48)/4 + 8, y_top + 239, "Розмір блока: 64 Б", size=9.5, color=MUTED))
    p.append(text(x_right + 20 + 3*(w_col - 48)/4 + 8, y_top + 252, "Окремий IRQ статус", size=9.5, color="#6c3483"))

    # In-band Interrupt
    p.append(rect(x_right + 20, y_top + 270, w_col - 40, 64, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(x_right + w_col/2, y_top + 289, "Апаратні переривання (In-band IRQ на DAT1)", size=11.5, bold=True, color=FIELD))
    p.append(text(x_right + w_col/2, y_top + 306, "Пристрій опускає лінію DAT1 у нуль між передачею блоків", size=10, color=INK))
    p.append(text(x_right + w_col/2, y_top + 321, "Хост миттєво реагує та опитує регістр INT_PENDING через CMD52", size=9.5, color=MUTED))

    # Summary box
    p.append(rect(x_right + 20, y_top + 344, w_col - 40, 64, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    p.append(text(x_right + w_col/2, y_top + 363, "Призначення: швидкісний периферійний інтерфейс", size=11, bold=True, color="#196f3d"))
    p.append(text(x_right + w_col/2, y_top + 379, "До 7 незалежних апаратних функцій + прямий доступ до регістрів", size=9.5, color=MUTED))
    p.append(text(x_right + w_col/2, y_top + 394, "Ініціалізація: CMD0 → CMD5 (IO_SEND_OP_COND) → CMD3", size=9.5, color="#196f3d"))

    render(os.path.join(OUT, "sdio-vs-sd-architecture.svg"), W, H, *p)


# ── 2. Формати команд CMD52 та CMD53 ──────────────────────────────────────────
def fig_cmd52_cmd53_frames():
    W, H = 940, 500
    p = []

    p.append(text(W/2, 28, "Формати кадрів керування SDIO: команди прямого (CMD52) та розширеного (CMD53) доступу", size=16.5, bold=True))
    p.append(text(W/2, 48, "48-бітні командні послідовності на лінії CMD та структура полів аргументу", size=12, color=MUTED, italic=True))

    # Секція CMD52
    y1 = 70
    p.append(rect(30, y1, 880, 195, fill="#fdfefe", stroke=NEG, sw=1.5, rx=8))
    p.append(rect(30, y1, 880, 32, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=8))
    p.append(text(45, y1 + 21, "CMD52: Прямий доступ до регістру (IO_RW_DIRECT) — 1 байт за транзакцію", size=13, bold=True, color=NEG, anchor="start"))
    p.append(text(890, y1 + 21, "Не займає лінії даних DAT[0..3]", size=11, color=MUTED, anchor="end", italic=True))

    # Бітові поля CMD52 (48 біт)
    # Start(1), Tx(1), CmdIdx(6), R/W(1), Func(3), RAW(1), Stuff(1), RegAddr(17), WriteData(8), CRC7(7), End(1)
    fields52 = [
        ("S", "0", 24, "#d5dbdb", INK),
        ("T", "1", 24, "#d5dbdb", INK),
        ("Index", "110100 (52)", 85, "#ebf5fb", NEG),
        ("R/W", "1/0", 42, "#fdebd0", "#b9770e"),
        ("Func", "0..7 (3б)", 62, "#e8f8f5", FIELD),
        ("RAW", "1/0", 44, "#fef9e7", "#7d6608"),
        ("Stuff", "0", 38, "#eaeded", MUTED),
        ("Register Address", "17 бітів (0x00000 .. 0x1FFFF)", 255, "#eaf2f8", NEG),
        ("Write Data", "8 бітів (байт запису)", 150, "#fdedec", POS),
        ("CRC7", "7 бітів", 70, "#f4ecf7", "#8e44ad"),
        ("E", "1", 24, "#d5dbdb", INK)
    ]

    bx = 45
    by = y1 + 45
    for name, desc, fw, bg_c, txt_c in fields52:
        p.append(rect(bx, by, fw, 50, fill=bg_c, stroke=LINE, sw=1, rx=4))
        p.append(text(bx + fw/2, by + 20, name, size=10.5, bold=True, color=txt_c))
        p.append(text(bx + fw/2, by + 38, desc, size=9.5, color=MUTED))
        bx += fw + 3

    # Опис специфічних прапорців CMD52
    p.append(rect(45, y1 + 104, 415, 75, fill="#fbfcfc", stroke=MUTED, sw=1, rx=4))
    p.append(text(55, y1 + 122, "Прапорець RAW (Read After Write, біт 27):", size=10.5, bold=True, color=INK, anchor="start"))
    p.append(text(55, y1 + 138, "• 0 = у відповіді повертається стан регістру ДО запису;", size=9.5, color=MUTED, anchor="start"))
    p.append(text(55, y1 + 152, "• 1 = повертається оновлене значення ПІСЛЯ виконання запису.", size=9.5, color=MUTED, anchor="start"))
    p.append(text(55, y1 + 166, "Дозволяє атомарно записати керівний біт і перевірити результат.", size=9.5, color=FIELD, anchor="start"))

    p.append(rect(475, y1 + 104, 420, 75, fill="#fbfcfc", stroke=MUTED, sw=1, rx=4))
    p.append(text(485, y1 + 122, "Відповідь R5 (48 біт у зворотному напрямку):", size=10.5, bold=True, color=INK, anchor="start"))
    p.append(text(485, y1 + 138, "• 8 бітів прочитаних даних (Read Data) з адресованого регістру;", size=9.5, color=MUTED, anchor="start"))
    p.append(text(485, y1 + 152, "• 8 бітів прапорців стану SDIO (COM_CRC_ERR, ILLEGAL_CMD, ERROR);", size=9.5, color=MUTED, anchor="start"))
    p.append(text(485, y1 + 166, "• Прапорці стану функції (IO_CURRENT_STATE) та апаратні біти помилок.", size=9.5, color=NEG, anchor="start"))

    # Секція CMD53
    y2 = 280
    p.append(rect(30, y2, 880, 205, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    p.append(rect(30, y2, 880, 32, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(45, y2 + 21, "CMD53: Розширений доступ (IO_RW_EXTENDED) — пакетний / блоковий обмін через DAT[0..3]", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(890, y2 + 21, "Потоки FIFO та блоки до 512 байтів", size=11, color=MUTED, anchor="end", italic=True))

    # Бітові поля CMD53
    # Start(1), Tx(1), CmdIdx(6), R/W(1), Func(3), BlockMode(1), OpCode(1), RegAddr(17), Count(9), CRC7(7), End(1)
    fields53 = [
        ("S", "0", 24, "#d5dbdb", INK),
        ("T", "1", 24, "#d5dbdb", INK),
        ("Index", "110101 (53)", 85, "#e8f8f5", FIELD),
        ("R/W", "1/0", 42, "#fdebd0", "#b9770e"),
        ("Func", "0..7 (3б)", 60, "#ebf5fb", NEG),
        ("Block", "0=Byte/1=Blk", 74, "#fef9e7", "#7d6608"),
        ("OpCode", "0=Fix/1=Inc", 70, "#fdedec", POS),
        ("Register Address", "17 бітів базової адреси", 200, "#eaf2f8", NEG),
        ("Byte/Block Count", "9 бітів (1..512 Б / 1..511 Блок)", 165, "#d5f5e3", "#196f3d"),
        ("CRC7", "7 бітів", 64, "#f4ecf7", "#8e44ad"),
        ("E", "1", 24, "#d5dbdb", INK)
    ]

    bx = 45
    by = y2 + 45
    for name, desc, fw, bg_c, txt_c in fields53:
        p.append(rect(bx, by, fw, 50, fill=bg_c, stroke=LINE, sw=1, rx=4))
        p.append(text(bx + fw/2, by + 20, name, size=10.5, bold=True, color=txt_c))
        p.append(text(bx + fw/2, by + 38, desc, size=9.5, color=MUTED))
        bx += fw + 3

    # Опис режимів CMD53
    p.append(rect(45, y2 + 104, 415, 88, fill="#fbfcfc", stroke=MUTED, sw=1, rx=4))
    p.append(text(55, y2 + 120, "Режим адреси (Op Code, біт 26):", size=10.5, bold=True, color=POS, anchor="start"))
    p.append(text(55, y2 + 135, "• OpCode = 0 (Fixed Address): передача у фіксований FIFO-регістр.", size=9.5, color=INK, anchor="start"))
    p.append(text(55, y2 + 148, "  Весь масив байтів ллється в один порт черги без зміни вказівника;", size=9, color=MUTED, anchor="start"))
    p.append(text(55, y2 + 162, "• OpCode = 1 (Incrementing Address): автоінкремент адреси.", size=9.5, color=INK, anchor="start"))
    p.append(text(55, y2 + 176, "  Зчитування або запис масиву послідовних конфігураційних регістрів.", size=9, color=MUTED, anchor="start"))

    p.append(rect(475, y2 + 104, 420, 88, fill="#fbfcfc", stroke=MUTED, sw=1, rx=4))
    p.append(text(485, y2 + 120, "Одиниці виміру лічильника (Block Mode, біт 27):", size=10.5, bold=True, color="#7d6608", anchor="start"))
    p.append(text(485, y2 + 135, "• Block Mode = 0 (Byte Mode): Count = 1..512 байтів (0 = 512 Б);", size=9.5, color=INK, anchor="start"))
    p.append(text(485, y2 + 149, "• Block Mode = 1 (Block Mode): Count = 1..511 блоків;", size=9.5, color=INK, anchor="start"))
    p.append(text(485, y2 + 163, "  Розмір блока (FBR Block Size) задається заздалегідь у CIA (наприклад, 512 Б);", size=9, color=MUTED, anchor="start"))
    p.append(text(485, y2 + 177, "  Передача кількох кілобайтів пакетів Wi-Fi за одну транзакцію шини.", size=9, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "sdio-cmd52-cmd53-frames.svg"), W, H, *p)


# ── 3. Часова діаграма переривання In-band Interrupt на лінії DAT1 ────────────
def fig_inband_interrupt():
    W, H = 940, 480
    p = []

    p.append(text(W/2, 28, "Апаратний механізм внутрішньосмугового переривання (SDIO In-band Interrupt) на лінії DAT1", size=16.5, bold=True))
    p.append(text(W/2, 48, "Мультиплексування лінії даних DAT1 між передачею корисних бітів та сигналізацією запиту IRQ", size=12, color=MUTED, italic=True))

    # Секція сигналів
    # Лінії: CLK, CMD, DAT0, DAT1 (IRQ), DAT2, DAT3
    labels = [
        ("CLK", NEG),
        ("CMD", NEG),
        ("DAT0", INK),
        ("DAT1 / IRQ", POS),
        ("DAT2", INK),
        ("DAT3", INK)
    ]

    y_sig_start = 75
    row_h = 42

    for i, (name, col) in enumerate(labels):
        sy = y_sig_start + i * row_h
        p.append(rect(35, sy, 110, 32, fill="#f8f9f9", stroke=col, sw=1.2, rx=4))
        p.append(text(90, sy + 21, name, size=11, bold=True, color=col))
        p.append(line(155, sy + 16, 905, sy + 16, color="#eaeded", sw=1, dash="4,4"))

    # Фази часу (вертикальні зони)
    # Фаза 1: Передача блоку даних (Data Block Transfer) [155 .. 380]
    p.append(rect(155, 68, 225, 260, fill="#ebf5fb", stroke="none"))
    p.append(text(267, 345, "Фаза 1: Передача даних", size=11, bold=True, color=NEG))
    p.append(text(267, 360, "DAT[0..3] несуть корисний блок", size=9.5, color=MUTED))

    # Фаза 2: Кінець блоку та перехід у стан спокою (End Bit + Idle) [380 .. 540]
    p.append(rect(380, 68, 160, 260, fill="#fef9e7", stroke="none"))
    p.append(text(460, 345, "Фаза 2: Інтервал спокою", size=11, bold=True, color="#7d6608"))
    p.append(text(460, 360, "Лінії у високому Z через pull-up", size=9.5, color=MUTED))

    # Фаза 3: Сигналізація переривання периферією (DAT1 Low) [540 .. 710]
    p.append(rect(540, 68, 170, 260, fill="#fdedec", stroke="none"))
    p.append(text(625, 345, "Фаза 3: Запит IRQ", size=11, bold=True, color=POS))
    p.append(text(625, 360, "Пристрій стягує DAT1 до GND", size=9.5, color=POS))

    # Фаза 4: Опитування та квітування хостом через CMD52 [710 .. 905]
    p.append(rect(710, 68, 195, 260, fill="#e8f8f5", stroke="none"))
    p.append(text(807, 345, "Фаза 4: Опитування хостом", size=11, bold=True, color=FIELD))
    p.append(text(807, 360, "CMD52 читає CCCR 0x04", size=9.5, color=FIELD))

    # Малювання сигналів
    # 1. CLK (тактові імпульси)
    clk_y = y_sig_start + 16
    clk_pts = []
    for x in range(160, 900, 20):
        clk_pts.append(f"{x},{clk_y-10} {x+10},{clk_y-10} {x+10},{clk_y+10} {x+20},{clk_y+10}")
    p.append(f'<polyline points="{" ".join(clk_pts)}" fill="none" stroke="{NEG}" stroke-width="1.5"/>')

    # 2. CMD (командна лінія)
    cmd_y = y_sig_start + row_h + 16
    p.append(line(155, cmd_y, 715, cmd_y, color=MUTED, sw=1.5))
    # CMD52 транзакція на фазі 4
    p.append(rect(720, cmd_y - 12, 175, 24, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(807, cmd_y + 4, "CMD52: Читання INT_PENDING", size=9.5, bold=True, color="#196f3d"))

    # 3. DAT0, DAT2, DAT3 (передача даних на фазі 1, потім High-Z)
    for row_idx, d_name in [(2, "DAT0"), (4, "DAT2"), (5, "DAT3")]:
        dy = y_sig_start + row_idx * row_h + 16
        # Data block burst
        p.append(rect(160, dy - 10, 210, 20, fill="#d4e6f1", stroke=NEG, sw=1.2, rx=2))
        p.append(text(265, dy + 4, f"Data Bits {d_name}", size=9, color=NEG))
        # High-Z (Pull-up)
        p.append(line(370, dy, 905, dy, color=MUTED, sw=1.2))

    # 4. DAT1 / IRQ (найважливіша лінія)
    irq_y = y_sig_start + 3 * row_h + 16
    # Фаза 1: Data bits
    p.append(rect(160, irq_y - 10, 210, 20, fill="#d4e6f1", stroke=NEG, sw=1.2, rx=2))
    p.append(text(265, irq_y + 4, "Data Bits DAT1", size=9, color=NEG))
    # Фаза 2: High level (Idle)
    p.append(line(370, irq_y - 10, 540, irq_y - 10, color=MUTED, sw=1.5))
    # Фаза 3: Спад у LOW (Периферія тягне до GND)
    p.append(line(540, irq_y - 10, 550, irq_y + 10, color=POS, sw=2))
    p.append(line(550, irq_y + 10, 780, irq_y + 10, color=POS, sw=2.5))
    p.append(text(645, irq_y + 24, "DAT1 = LOW (Запит переривання від Wi-Fi/BT)", size=10, bold=True, color=POS))
    # Фаза 4: Звільнення лінії після квітування
    p.append(line(780, irq_y + 10, 790, irq_y - 10, color=FIELD, sw=2))
    p.append(line(790, irq_y - 10, 905, irq_y - 10, color=MUTED, sw=1.5))

    # Пояснювальний підвал
    p.append(rect(35, 385, 870, 75, fill="#fdfefe", stroke=MUTED, sw=1, rx=6))
    p.append(text(45, 405, "Ключові аспекти внутрішньосмугової сигналізації переривань:", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(45, 422, "1. Не потребує окремого фізичного виводу IRQ на друкованій платі — заощаджує виводи хоста та площу модуля;", size=9.5, color=MUTED, anchor="start"))
    p.append(text(45, 437, "2. Переривання активне лише між передачею блоків (Interrupt Period). Під час пакетного обміну воно тимчасово блокується;", size=9.5, color=MUTED, anchor="start"))
    p.append(text(45, 452, "3. Асинхронний режим дозволяє пристрою розбудити хост при зупиненій тактовій частоті шини CLK (енергозбереження).", size=9.5, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "sdio-inband-interrupt-timing.svg"), W, H, *p)


# ── 4. Стек драйверів Linux та обробка переривання ────────────────────────────
def fig_linux_sdio_stack():
    W, H = 940, 520
    p = []

    p.append(text(W/2, 28, "Архітектура стека драйверів SDIO у ядрі Linux та диспетчеризація подій", size=17, bold=True))
    p.append(text(W/2, 48, "Ієрархія підсистем: від апаратного хост-контролера через ядро MMC до функціональних драйверів", size=12, color=MUTED, italic=True))

    # Рівень 1: Функціональні драйвери (User/Function Drivers)
    y_l1 = 70
    p.append(rect(40, y_l1, 860, 95, fill="#f4ecf7", stroke="#8e44ad", sw=1.5, rx=8))
    p.append(text(55, y_l1 + 22, "Рівень функціональних драйверів периферії (SDIO Function Drivers)", size=13, bold=True, color="#8e44ad", anchor="start"))

    # Блоки драйверів
    # Wi-Fi driver
    p.append(rect(55, y_l1 + 35, 260, 50, fill="#ffffff", stroke="#8e44ad", sw=1.2, rx=6))
    p.append(text(185, y_l1 + 54, "brcmfmac / mwifiex_sdio", size=11.5, bold=True, color="#8e44ad"))
    p.append(text(185, y_l1 + 71, "Драйвер Wi-Fi (Функція 1, net_device)", size=9.5, color=MUTED))

    # BT driver
    p.append(rect(340, y_l1 + 35, 260, 50, fill="#ffffff", stroke="#8e44ad", sw=1.2, rx=6))
    p.append(text(470, y_l1 + 54, "btmtksdio / btbcm", size=11.5, bold=True, color="#8e44ad"))
    p.append(text(470, y_l1 + 71, "Драйвер Bluetooth (Функція 2, hci_dev)", size=9.5, color=MUTED))

    # Generic driver
    p.append(rect(625, y_l1 + 35, 260, 50, fill="#ffffff", stroke="#8e44ad", sw=1.2, rx=6))
    p.append(text(755, y_l1 + 54, "sdio_uart / sdio_raw", size=11.5, bold=True, color="#8e44ad"))
    p.append(text(755, y_l1 + 71, "Послідовні порти та користувацькі модулі", size=9.5, color=MUTED))

    # Стрілка вниз/вгору між L1 та L2
    p.append(line(260, y_l1 + 95, 260, y_l1 + 125, color=LINE, sw=1.5))
    p.append(line(620, y_l1 + 95, 620, y_l1 + 125, color=LINE, sw=1.5))
    p.append(text(440, y_l1 + 115, "API ядра: sdio_claim_host(), sdio_claim_irq(), sdio_memcpy_fromio()", size=10, bold=True, color=INK))

    # Рівень 2: Ядро підсистеми MMC/SDIO (MMC/SDIO Core Subsystem)
    y_l2 = 195
    p.append(rect(40, y_l2, 860, 155, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=8))
    p.append(text(55, y_l2 + 22, "Ядро підсистеми MMC/SDIO (drivers/mmc/core/)", size=13, bold=True, color=NEG, anchor="start"))

    # Підкомпоненти Core
    p.append(rect(55, y_l2 + 35, 195, 100, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(152, y_l2 + 55, "sdio.c & sdio_bus.c", size=11, bold=True, color=NEG))
    p.append(text(152, y_l2 + 72, "Ініціалізація шини", size=9.5, color=INK))
    p.append(text(152, y_l2 + 88, "Зчитування CCCR/FBR", size=9, color=MUTED))
    p.append(text(152, y_l2 + 103, "Парсинг кортежів CIS", size=9, color=MUTED))
    p.append(text(152, y_l2 + 118, "Реєстрація struct sdio_func", size=9, color="#1a5276"))

    p.append(rect(270, y_l2 + 35, 185, 100, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(362, y_l2 + 55, "sdio_io.c & sdio_ops.c", size=11, bold=True, color=NEG))
    p.append(text(362, y_l2 + 72, "Формування команд", size=9.5, color=INK))
    p.append(text(362, y_l2 + 88, "Виконання CMD52/CMD53", size=9, color=MUTED))
    p.append(text(362, y_l2 + 103, "Контроль байт/блок режимів", size=9, color=MUTED))
    p.append(text(362, y_l2 + 118, "Синхронізація блокувань", size=9, color="#1a5276"))

    p.append(rect(475, y_l2 + 35, 205, 100, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(577, y_l2 + 55, "sdio_irq.c (IRQ Thread)", size=11, bold=True, color=POS))
    p.append(text(577, y_l2 + 72, "Потік обробки переривань", size=9.5, color=INK))
    p.append(text(577, y_l2 + 88, "Опитування INT_PENDING", size=9, color=MUTED))
    p.append(text(577, y_l2 + 103, "Маршрутизація до функцій 1..7", size=9, color=MUTED))
    p.append(text(577, y_l2 + 118, "sdio_irq_thread() квітування", size=9, color=POS))

    p.append(rect(700, y_l2 + 35, 185, 100, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(792, y_l2 + 55, "queue.c & block.c", size=11, bold=True, color=NEG))
    p.append(text(792, y_l2 + 72, "Черги запитів ядра", size=9.5, color=INK))
    p.append(text(792, y_l2 + 88, "DMA-дескриптори", size=9, color=MUTED))
    p.append(text(792, y_l2 + 103, "Scatter-Gather списки", size=9, color=MUTED))
    p.append(text(792, y_l2 + 118, "Управління чергою MMC", size=9, color="#1a5276"))

    # Стрілка вниз між L2 та L3
    p.append(line(470, y_l2 + 155, 470, y_l2 + 185, color=LINE, sw=1.5))
    p.append(text(470, y_l2 + 172, "struct mmc_host_ops: request(), set_ios(), enable_sdio_irq()", size=10, bold=True, color=INK))

    # Рівень 3: Драйвер хост-контролера та апаратний рівень (Host Controller & Hardware)
    y_l3 = 380
    p.append(rect(40, y_l3, 860, 115, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(55, y_l3 + 22, "Драйвер контролера хоста та фізичне залізо (Host Controller & Hardware)", size=13, bold=True, color=FIELD, anchor="start"))

    p.append(rect(55, y_l3 + 35, 260, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(185, y_l3 + 54, "sdhci / sdhci-pci / dw_mmc", size=11, bold=True, color=FIELD))
    p.append(text(185, y_l3 + 70, "Стандартизовані контролери SDHCI", size=9.5, color=MUTED))
    p.append(text(185, y_l3 + 85, "Апаратний ADMA2 / Auto-CMD", size=9, color="#196f3d"))

    p.append(rect(340, y_l3 + 35, 260, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(470, y_l3 + 54, "Апаратний блок SD Host", size=11, bold=True, color=FIELD))
    p.append(text(470, y_l3 + 70, "Тактовий генератор CLK (до 208 МГц)", size=9.5, color=MUTED))
    p.append(text(470, y_l3 + 85, "Апаратний детектер спаду DAT1", size=9, color="#196f3d"))

    p.append(rect(625, y_l3 + 35, 260, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(755, y_l3 + 54, "SDIO Пристрій (Wi-Fi/BT SoC)", size=11, bold=True, color=FIELD))
    p.append(text(755, y_l3 + 70, "Фізичні лінії: CLK, CMD, DAT[0..3]", size=9.5, color=MUTED))
    p.append(text(755, y_l3 + 85, "BCM43438 / 88W8801 / ESP32", size=9, color="#196f3d"))

    render(os.path.join(OUT, "sdio-linux-stack-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sdio_vs_sd_architecture()
    fig_cmd52_cmd53_frames()
    fig_inband_interrupt()
    fig_linux_sdio_stack()
    print("Всі 4 фігури згенеровано успішно у img/")
