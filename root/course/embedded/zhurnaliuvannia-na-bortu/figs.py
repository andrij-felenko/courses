# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_flash_sector_ring():
    # Архітектура секторного кільцевого буфера на NOR Flash:
    # 6 секторів по 4 КБ зі станами (ERASED, ACTIVE, FULL, DIRTY/READY),
    # рух покажчиків голови (head) і хвоста (tail), атомарні бітові переходи 0xFF->0xFE->0xFC->0x00
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 28, "Кільцевий секторний буфер у пам'яті SPI NOR Flash", size=16, bold=True))
    p.append(text(W / 2, 48, "Розбивка області на сектори по 4 КБ та бітові переходи станів без попереднього стирання", size=12, color=MUTED))

    # Сектори (6 блоків у ряд)
    sec_w = 118
    sec_h = 160
    start_x = 45
    y_sec = 85

    sectors = [
        ("Сектор 0", "0x0000", "0x00 (DIRTY)", "Звільнено", "Чекає на стирання", "#f9f0f0", POS),
        ("Сектор 1", "0x1000", "0xFF (ERASED)", "Стерто", "Чистий резерв", "#f4f6f8", MUTED),
        ("Сектор 2", "0x2000", "0xFE (ACTIVE)", "Запис", "Поточний Head", "#eafaf0", FIELD),
        ("Сектор 3", "0x3000", "0xFC (FULL)", "Заповнено", "Готово до відправки", "#eaf0fd", NEG),
        ("Сектор 4", "0x4000", "0xFC (FULL)", "Заповнено", "Поточний Tail (ACK)", "#eaf0fd", NEG),
        ("Сектор 5", "0x5000", "0x00 (DIRTY)", "Відправлено", "Підтверджено ACK", "#f9f0f0", POS),
    ]

    for i, (name, addr, st_hex, st_title, st_desc, bg_col, stroke_col) in enumerate(sectors):
        x = start_x + i * (sec_w + 12)
        p.append(rect(x, y_sec, sec_w, sec_h, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        p.append(text(x + sec_w / 2, y_sec + 22, name, size=13, bold=True, color=stroke_col))
        p.append(text(x + sec_w / 2, y_sec + 40, addr, size=11, color=MUTED))
        p.append(line(x + 8, y_sec + 48, x + sec_w - 8, y_sec + 48, color=stroke_col, sw=1, dash="2 2"))
        
        p.append(text(x + sec_w / 2, y_sec + 68, "Стан заголовка:", size=10, color=MUTED))
        p.append(text(x + sec_w / 2, y_sec + 86, st_hex, size=11, bold=True, color=INK))
        p.append(text(x + sec_w / 2, y_sec + 110, st_title, size=11, bold=True, color=stroke_col))
        p.append(text(x + sec_w / 2, y_sec + 132, st_desc, size=9, color=MUTED))

    # Покажчики Head і Tail
    head_x = start_x + 2 * (sec_w + 12) + sec_w / 2
    tail_x = start_x + 4 * (sec_w + 12) + sec_w / 2

    # Стрілка Head зверху
    p.append(arrow(head_x, y_sec - 24, head_x, y_sec - 2, color=FIELD, sw=2.2))
    b_h, _, _ = textbox(head_x, y_sec - 34, "HEAD (Запис нових логів)", size=11, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD, pad=6)
    p.append(b_h)

    # Стрілка Tail знизу
    p.append(arrow(tail_x, y_sec + sec_h + 24, tail_x, y_sec + sec_h + 2, color=NEG, sw=2.2))
    b_t, _, _ = textbox(tail_x, y_sec + sec_h + 34, "TAIL (Вивантаження в мережу)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG, pad=6)
    p.append(b_t)

    # Нижній пояс: Машина станів бітів NOR Flash
    y_trans = 310
    p.append(rect(35, y_trans, W - 70, 150, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(W / 2, y_trans + 24, "Атомарна зміна стану сектора через властивість NOR Flash (перехід 1 -> 0 без стирання)", size=13, bold=True))

    steps = [
        ("0xFF (11111111b)", "Стирання 4 КБ", "Сектор очищено", MUTED),
        ("0xFE (11111110b)", "Відкриття сектора", "Старт запису записів", FIELD),
        ("0xFC (11111100b)", "Сектор вичерпано", "Перехід до наступного", NEG),
        ("0x00 (00000000b)", "ACK від сервера", "Готово під стирання", POS),
    ]

    x_step_start = 55
    step_w = 160
    for j, (hex_val, action, desc, col) in enumerate(steps):
        x_st = x_step_start + j * (step_w + 30)
        p.append(rect(x_st, y_trans + 42, step_w, 88, fill="#f8fafc", stroke=col, sw=1.5, rx=6))
        p.append(text(x_st + step_w / 2, y_trans + 62, hex_val, size=12, bold=True, color=col))
        p.append(text(x_st + step_w / 2, y_trans + 84, action, size=11, bold=True, color=INK))
        p.append(text(x_st + step_w / 2, y_trans + 106, desc, size=10, color=MUTED))

        if j < len(steps) - 1:
            p.append(arrow(x_st + step_w + 4, y_trans + 86, x_st + step_w + 26, y_trans + 86, color=LINE, sw=1.5))

    return render(os.path.join(IMG, 'flash-sector-ring.svg'), W, H, *p)


def fig_binary_tokenized_flow():
    # Словникове токенізоване логування: компіляція -> бортовий мікроконтролер -> хост/сервер
    W, H = 820, 430
    p = []

    p.append(text(W / 2, 28, "Конвеєр словникового токенізованого логування (Tokenized Logging)", size=16, bold=True))
    p.append(text(W / 2, 48, "Винесення рядків форматування на етап компіляції для 85% економії Flash і каналу", size=12, color=MUTED))

    col_w = 230
    col_h = 320
    y_top = 75

    # 1. Етап компіляції (Ліворуч)
    x1 = 35
    p.append(rect(x1, y_top, col_w, col_h, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(x1 + col_w / 2, y_top + 26, "1. Етап компіляції", size=13, bold=True, color=NEG))
    p.append(text(x1 + col_w / 2, y_top + 44, "Препроцесор / Скрипт збірки", size=10, color=MUTED))
    p.append(line(x1 + 10, y_top + 54, x1 + col_w - 10, y_top + 54, color=NEG, sw=1, dash="2 2"))

    b_src, _, _ = textbox(x1 + col_w / 2, y_top + 95, "LOG_WARN(\"Sens %d err %u\",\n         id, err_code);", size=11, bold=True, fill="#ffffff", stroke=LINE, pad=8)
    p.append(b_src)

    p.append(arrow(x1 + col_w / 2, y_top + 140, x1 + col_w / 2, y_top + 168, color=NEG, sw=1.5))
    p.append(text(x1 + col_w / 2, y_top + 158, "Хешування рядка", size=10, color=NEG))

    b_tok, _, _ = textbox(x1 + col_w / 2, y_top + 205, "Token ID: 0x8F3A2B1C\nХеш у бінарник\nРядок у словник хоста", size=10, fill="#eaf0fd", stroke=NEG, color=INK, pad=6)
    p.append(b_tok)

    b_dict, _, _ = textbox(x1 + col_w / 2, y_top + 280, "Словник логів (schema.json)\nЗберігається на сервері", size=10, bold=True, fill="#ffffff", stroke=POS, color=POS, pad=6)
    p.append(b_dict)

    # Стрілка між 1 і 2
    p.append(arrow(x1 + col_w + 4, y_top + 100, x1 + col_w + 24, y_top + 100, color=FIELD, sw=1.8))

    # 2. На борту МК (Посередині)
    x2 = x1 + col_w + 28
    p.append(rect(x2, y_top, col_w, col_h, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x2 + col_w / 2, y_top + 26, "2. На борту МК (Runtime)", size=13, bold=True, color=FIELD))
    p.append(text(x2 + col_w / 2, y_top + 44, "Нуль форматування, чисті байти", size=10, color=MUTED))
    p.append(line(x2 + 10, y_top + 54, x2 + col_w - 10, y_top + 54, color=FIELD, sw=1, dash="2 2"))

    b_frame, _, _ = textbox(x2 + col_w / 2, y_top + 120, "Компактний бінарний кадр:\n• Timestamp: 4B (мс)\n• Token ID:  4B\n• Arg1 (id): 2B\n• Arg2 (err): 2B\nВсього: 12 байтів у Flash!", size=10, bold=True, fill="#ffffff", stroke=FIELD, color=INK, pad=8)
    p.append(b_frame)

    b_adv, _, _ = textbox(x2 + col_w / 2, y_top + 235, "Переваги на борту:\n• Час запису: < 4 мкс\n• Нуль snprintf / heap\n• Економія RAM і Flash", size=10, fill="#eafaf0", stroke=FIELD, color=FIELD, pad=6)
    p.append(b_adv)

    # Стрілка між 2 і 3
    p.append(arrow(x2 + col_w + 4, y_top + 120, x2 + col_w + 24, y_top + 120, color=FIELD, sw=1.8))

    # 3. Сервер / Хост (Праворуч)
    x3 = x2 + col_w + 28
    p.append(rect(x3, y_top, col_w, col_h, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    p.append(text(x3 + col_w / 2, y_top + 26, "3. Серверний декодер", size=13, bold=True, color=POS))
    p.append(text(x3 + col_w / 2, y_top + 44, "Відновлення повного тексту", size=10, color=MUTED))
    p.append(line(x3 + 10, y_top + 54, x3 + col_w - 10, y_top + 54, color=POS, sw=1, dash="2 2"))

    b_dec, _, _ = textbox(x3 + col_w / 2, y_top + 110, "12 байтів кадру +\nСловник (schema.json)", size=11, bold=True, fill="#ffffff", stroke=LINE, pad=8)
    p.append(b_dec)

    p.append(arrow(x3 + col_w / 2, y_top + 155, x3 + col_w / 2, y_top + 185, color=POS, sw=1.5))
    p.append(text(x3 + col_w / 2, y_top + 172, "Збірка повідомлення", size=10, color=POS))

    b_res, _, _ = textbox(x3 + col_w / 2, y_top + 245, "Відновлений лог у системі:\n[WARN] 14:02:11.450\nSens 3 err 104\n(Повний текст для інженера)", size=10, bold=True, fill="#fdf2f2", stroke=POS, color=POS, pad=8)
    p.append(b_res)

    return render(os.path.join(IMG, 'binary-tokenized-flow.svg'), W, H, *p)


def fig_log_record_layout():
    # Анатомія двійкового кадру логу на Flash
    W, H = 820, 360
    p = []

    p.append(text(W / 2, 28, "Байтове компонування бінарного запису логу (Binary Log Frame)", size=16, bold=True))
    p.append(text(W / 2, 48, "Фіксований заголовок, токен, упаковані аргументи змінної довжини та контрольна сума", size=12, color=MUTED))

    # Стрічка байтів
    start_x = 40
    y_band = 85
    h_band = 90

    fields = [
        ("Синхробайти", "0x55AA", "2B", 85, "#eaf0fd", NEG),
        ("Довжина", "Length", "1B", 70, "#eaf0fd", NEG),
        ("Рівень", "Level", "1B", 65, "#fdf2f2", POS),
        ("Модуль", "ModID", "1B", 65, "#fdf2f2", POS),
        ("Послідовність", "SeqNum", "4B", 95, "#eafaf0", FIELD),
        ("Мітка часу", "Timestamp", "4B", 100, "#eafaf0", FIELD),
        ("Токен ID", "TokenID", "4B", 95, "#fef9e7", "#d4ac0d"),
        ("Аргументи (Varargs)", "Payload bytes", "NB", 145, "#ffffff", LINE),
        ("CRC16", "CRC-16", "2B", 80, "#fdf2f2", POS),
    ]

    curr_x = start_x
    for name, code_str, sz_str, w_box, bg_c, strk_c in fields:
        p.append(rect(curr_x, y_band, w_box, h_band, fill=bg_c, stroke=strk_c, sw=1.5, rx=5))
        p.append(text(curr_x + w_box / 2, y_band + 24, name, size=11, bold=True, color=INK))
        p.append(text(curr_x + w_box / 2, y_band + 48, code_str, size=12, bold=True, color=strk_c))
        p.append(text(curr_x + w_box / 2, y_band + 72, sz_str, size=10, color=MUTED))
        curr_x += w_box + 2

    # Описи секцій
    y_desc = 210
    p.append(rect(start_x, y_desc, W - 2 * start_x, 125, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))

    desc_items = [
        ("Синхронізація (0x55AA):", "Дозволяє знайти початок наступного запису після раптового збою живлення чи пошкодження."),
        ("Рівень + Модуль:", "1 байт рівня (TRACE..FATAL) + 1 байт підсистеми (0: Power, 1: Radio, 2: Sensors, 3: Flash)."),
        ("SeqNum + Час:", "SeqNum ловить пропущені пакети; Timestamp (мс монотонного таймера) дає точну хронологію."),
        ("TokenID + Payload:", "32-бітний хеш рядка замість ASCII-тексту + сирі змінні (int, float, status codes)."),
        ("Контрольна сума CRC-16:", "Захист від читання недописаного кадру під час знеструмлення або деградації комірок Flash."),
    ]

    for k, (title_str, val_str) in enumerate(desc_items):
        y_item = y_desc + 22 + k * 21
        p.append(text(start_x + 15, y_item, title_str, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(start_x + 195, y_item, val_str, size=11, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'log-record-layout.svg'), W, H, *p)


def fig_upload_triage_fsm():
    # Диспетчер вивантаження, пріоритезація та обробка аварій
    W, H = 840, 460
    p = []

    p.append(text(W / 2, 28, "Диспетчер вивантаження логів, пріоритезація та захист каналу", size=16, bold=True))
    p.append(text(W / 2, 48, "Розподіл потоків між звичайним кільцевим буфером і аварійним розділом (Crash Dump)", size=12, color=MUTED))

    # Джерела ліворуч
    x_src = 40
    p.append(rect(x_src, 80, 200, 160, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(x_src + 100, 105, "CRASH / PANIC PARTITION", size=11, bold=True, color=POS))
    p.append(text(x_src + 100, 125, "Виділений Flash-сектор", size=10, color=MUTED))
    p.append(text(x_src + 100, 155, "• Дамп регістрів (R0-R15)", size=10, color=INK))
    p.append(text(x_src + 100, 175, "• Причина паніки / HardFault", size=10, color=INK))
    p.append(text(x_src + 100, 195, "• Міні-трейс стека ядра", size=10, color=INK))
    p.append(text(x_src + 100, 222, "Пріоритет #1: Негайно", size=10, bold=True, color=POS))

    p.append(rect(x_src, 260, 200, 170, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    p.append(text(x_src + 100, 285, "RING LOG BUFFER", size=11, bold=True, color=NEG))
    p.append(text(x_src + 100, 305, "Кільце секторів (64 КБ)", size=10, color=MUTED))
    p.append(text(x_src + 100, 335, "• Поточні INFO / WARN / ERR", size=10, color=INK))
    p.append(text(x_src + 100, 355, "• Накопичення при офлайні", size=10, color=INK))
    p.append(text(x_src + 100, 375, "• Витіснення старих INFO", size=10, color=INK))
    p.append(text(x_src + 100, 405, "Пріоритет #2: Фонова пачка", size=10, bold=True, color=NEG))

    # Диспетчер вивантаження посередині
    x_mid = 290
    w_mid = 240
    p.append(rect(x_mid, 80, w_mid, 350, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x_mid + w_mid / 2, 108, "Диспетчер передачі (Uploader)", size=13, bold=True, color=FIELD))
    p.append(line(x_mid + 10, 120, x_mid + w_mid - 10, 120, color=FIELD, sw=1, dash="2 2"))

    b_step1, _, _ = textbox(x_mid + w_mid / 2, 155, "1. Перевірка наявності Crash Dump\nЯкщо є -> терміновий пакет", size=10, bold=True, fill="#ffffff", stroke=POS, color=POS, pad=6)
    p.append(b_step1)

    b_step2, _, _ = textbox(x_mid + w_mid / 2, 220, "2. Пакування логів у пачку\nФормування блоку до 512B MTU", size=10, bold=True, fill="#ffffff", stroke=NEG, color=NEG, pad=6)
    p.append(b_step2)

    b_step3, _, _ = textbox(x_mid + w_mid / 2, 285, "3. Кадрування COBS + CRC\nЗахист транспортного рівня", size=10, fill="#ffffff", stroke=LINE, color=INK, pad=6)
    p.append(b_step3)

    b_step4, _, _ = textbox(x_mid + w_mid / 2, 355, "4. Очікування Server ACK\nУспіх -> зсув Tail pointer\nПомилка -> Exponential Backoff", size=10, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD, pad=6)
    p.append(b_step4)

    # Стрілки зліва направо в диспетчер
    p.append(arrow(x_src + 204, 160, x_mid - 4, 155, color=POS, sw=2.0))
    p.append(arrow(x_src + 204, 345, x_mid - 4, 220, color=NEG, sw=2.0))

    # Сервер і радіоканал праворуч
    x_srv = 580
    w_srv = 220
    p.append(rect(x_srv, 80, w_srv, 170, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(x_srv + w_srv / 2, 108, "Сервер моніторингу", size=13, bold=True, color=INK))
    p.append(text(x_srv + w_srv / 2, 132, "Хмара / Ingestion Service", size=10, color=MUTED))
    p.append(text(x_srv + w_srv / 2, 160, "• Прийом пачки логів", size=10, color=INK))
    p.append(text(x_srv + w_srv / 2, 180, "• Перевірка CRC та Tokenize", size=10, color=INK))
    p.append(text(x_srv + w_srv / 2, 202, "• Відповідь: ACK(LastSeq)", size=11, bold=True, color=FIELD))

    p.append(rect(x_srv, 270, w_srv, 160, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(x_srv + w_srv / 2, 298, "Обмежений канал (IoT)", size=12, bold=True, color=MUTED))
    p.append(text(x_srv + w_srv / 2, 325, "NB-IoT / LTE-M / LoRa / BLE", size=10, color=INK))
    p.append(text(x_srv + w_srv / 2, 352, "• Дорогі байт-квоти й батарея", size=10, color=POS))
    p.append(text(x_srv + w_srv / 2, 375, "• Пакетування знижує трафік", size=10, color=FIELD))
    p.append(text(x_srv + w_srv / 2, 398, "• Тротлінг при слабкому сигналі", size=10, color=NEG))

    # Стрілки між диспетчером і сервером
    p.append(arrow(x_mid + w_mid + 4, 180, x_srv - 4, 160, color=FIELD, sw=2.0))
    p.append(text((x_mid + w_mid + x_srv) / 2, 162, "Batch Data", size=10, bold=True, color=FIELD))

    p.append(arrow(x_srv - 4, 210, x_mid + w_mid + 4, 350, color=FIELD, sw=2.0))
    p.append(text((x_mid + w_mid + x_srv) / 2, 290, "Server ACK", size=10, bold=True, color=FIELD))

    return render(os.path.join(IMG, 'upload-triage-fsm.svg'), W, H, *p)


if __name__ == '__main__':
    fig_flash_sector_ring()
    fig_binary_tokenized_flow()
    fig_log_record_layout()
    fig_upload_triage_fsm()
    print("All figures generated successfully.")
