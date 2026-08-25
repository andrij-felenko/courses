# -*- coding: utf-8 -*-
"""Генератор векторних фігур SVG для теми «Протокол SD/SDIO».
Використовує спільний модуль svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра сигналів та елементів
CLK_COL  = NEG          # Тактовий сигнал CLK (синій #2457d6)
CMD_COL  = POS          # Командна лінія CMD (червоний #c0392b)
DAT_COL  = "#7a5fb0"    # Лінії даних DAT0..DAT3 (фіолетовий)
STAT_COL = FIELD        # Статуси та підтвердження (зелений #27ae60)
HI_Z_COL = MUTED        # Високоімпедансний стан Hi-Z (сірий)
BOX_BG   = FILL         # Фонова заливка блоків (#f4f6f8)
HL_BG    = "#eef2ff"    # Підсвітка активних фаз (блакитний)
WARN_BG  = "#fef2f2"    # Затримки / Busy (червонуватий)
CARD_BG  = "#fdf8e2"    # Фонова заливка карти пам'яті (жовтуватий)


# ── 1. Топологія шини SD/SDIO та режими ──────────────────────────────────────
def fig_sd_bus_topology():
    W, H = 840, 520
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Секція 1: Режим SPI (4 дроти)
    p.append(rect(30, 40, 360, 205, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(210, 65, "Режим SPI (1 біт, повний дуплекс)", size=13, color=INK, bold=True))
    
    p.append(rect(45, 85, 90, 140, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(90, 155, "MCU SPI", size=12, color=INK, bold=True))
    p.append(rect(285, 85, 90, 140, fill=CARD_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(330, 155, "SD Card", size=12, color=INK, bold=True))

    lines_spi = [
        (105, "CS# (Вибір карти / Pin 1)", CMD_COL, "→"),
        (135, "SCK (Тактовий сигнал / Pin 5)", CLK_COL, "→"),
        (165, "MOSI (Дані до карти / Pin 2)", DAT_COL, "→"),
        (195, "MISO (Дані від карти / Pin 7)", STAT_COL, "←"),
    ]
    for y, label, col, direction in lines_spi:
        if direction == "→":
            p.append(arrow(135, y, 285, y, color=col, sw=1.6))
        else:
            p.append(arrow(285, y, 135, y, color=col, sw=1.6))
        p.append(text(210, y - 5, label, size=9.5, color=col, bold=True))

    # Секція 2: Рідний SD-режим (4-бітний паралельний)
    p.append(rect(410, 40, 400, 205, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(610, 65, "Рідний 4-бітний SD/SDIO режим", size=13, color=INK, bold=True))
    
    p.append(rect(425, 85, 90, 140, fill=BOX_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(470, 155, "SD Host", size=12, color=INK, bold=True))
    p.append(rect(705, 85, 90, 140, fill=CARD_BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(750, 155, "SD/SDIO", size=12, color=INK, bold=True))

    lines_sd = [
        (100, "CLK (Тактування 25–50 МГц)", CLK_COL, "→"),
        (125, "CMD (Команди/Відповіді)", CMD_COL, "⇄"),
        (150, "DAT0 (Дані / Busy)", DAT_COL, "⇄"),
        (170, "DAT1 (Дані / SDIO IRQ)", DAT_COL, "⇄"),
        (190, "DAT2 (Дані)", DAT_COL, "⇄"),
        (210, "DAT3 (Дані / Card Detect)", DAT_COL, "⇄"),
    ]
    for y, label, col, direction in lines_sd:
        if direction == "→":
            p.append(arrow(515, y, 705, y, color=col, sw=1.5))
        else:
            p.append(line(515, y, 705, y, color=col, sw=1.5))
            p.append(circle(515, y, 2.5, fill=col, stroke=col))
            p.append(circle(705, y, 2.5, fill=col, stroke=col))
        p.append(text(610, y - 4, label, size=9, color=col, bold=True))

    # Секція 3: Порівняльна таблиця характеристик режимів
    p.append(rect(30, 265, 780, 235, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 290, "Порівняння фізичного та канального рівнів інтерфейсу Secure Digital", size=13, color=INK, bold=True))

    headers = ["Параметр", "SPI-режим", "1-бітний SD-режим", "4-бітний SD-режим", "SDIO (Ввід-Вивід)"]
    col_x = [45, 165, 310, 470, 635, 795]
    
    p.append(rect(45, 305, 750, 28, fill=BOX_BG, stroke=LINE, sw=1.0, rx=2))
    for i in range(len(headers)):
        cx = (col_x[i] + col_x[i+1]) / 2
        p.append(text(cx, 323, headers[i], size=10, color=INK, bold=True))

    rows_data = [
        ("Сигнальні лінії", "4 (CS, SCK, MOSI, MISO)", "3 (CLK, CMD, DAT0)", "6 (CLK, CMD, DAT0..3)", "6 (CLK, CMD, DAT0..3)"),
        ("Ширина шини даних", "1 біт", "1 біт", "4 біти (нібл / такт)", "1 або 4 біти"),
        ("Частота тактування", "до 25 МГц", "до 25 МГц (Default Speed)", "25 / 50 / 208 МГц", "25 / 50 МГц"),
        ("Пропускна здатність", "3.1 МБ/с", "3.1 МБ/с", "12.5 / 25 / 104 МБ/с", "12.5 / 25 МБ/с"),
        ("Контроль помилок CRC", "Опціональний (крім CMD0/8)", "Обов'язковий (CRC7+CRC16)", "Обов'язковий (CRC7+4xCRC16)", "Обов'язковий (CRC7+CRC16)"),
    ]

    for row_idx, row in enumerate(rows_data):
        y_pos = 353 + row_idx * 28
        bg_color = HL_BG if row_idx % 2 == 1 else "#ffffff"
        p.append(rect(45, y_pos - 16, 750, 26, fill=bg_color, stroke=LINE, sw=0.5, rx=2))
        for col_idx in range(len(row)):
            cx = (col_x[col_idx] + col_x[col_idx+1]) / 2
            is_bold = col_idx == 0
            p.append(text(cx, y_pos + 1, row[col_idx], size=9.5, color=INK, bold=is_bold))

    render(os.path.join(OUT, "sd-bus-topology.svg"), W, H, *p)


# ── 2. Анатомія команд, відповідей та пакетів даних ──────────────────────────
def fig_command_response_frames():
    W, H = 840, 560
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Заголовок
    p.append(text(W / 2, 35, "Структура 48-бітного командного фрейму CMD, відповідей та блоку даних", size=14, color=INK, bold=True))

    # 1. Формат 48-бітної команди CMD
    p.append(rect(30, 55, 780, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 76, "48-бітний командний пакет хоста (Host Command Token)", size=11, color=INK, bold=True, anchor="start"))

    fields_cmd = [
        ("S", "0", 30, WARN_BG),
        ("T", "1", 30, HL_BG),
        ("Command Index", "6 бітів (CMD0..63)", 140, "#e0f2fe"),
        ("Argument", "32 біти (Адреса, напруга, конфігурація)", 360, "#fef3c7"),
        ("CRC7", "7 бітів (x⁷+x³+1)", 135, "#dcfce7"),
        ("E", "1", 30, WARN_BG),
    ]
    cur_x = 45
    for name, desc, w_box, bg_c in fields_cmd:
        p.append(rect(cur_x, 90, w_box, 55, fill=bg_c, stroke=LINE, sw=1.0, rx=3))
        p.append(text(cur_x + w_box / 2, 112, name, size=10.5, color=INK, bold=True))
        p.append(text(cur_x + w_box / 2, 131, desc, size=9.5, color=MUTED))
        cur_x += w_box + 7

    # 2. Формати відповідей карти R1 та R2
    p.append(rect(30, 180, 780, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 202, "Формати відповідей карти: Базовий 48-бітний R1/R7 та 136-бітний R2 (CID/CSD)", size=11, color=INK, bold=True, anchor="start"))

    # R1
    p.append(text(45, 224, "Відповідь R1 / R7 (48 бітів):", size=10, color=INK, bold=True, anchor="start"))
    fields_r1 = [
        ("S", "0", 30, WARN_BG),
        ("T", "0", 30, HL_BG),
        ("Cmd Index / VHS", "6 бітів", 140, "#e0f2fe"),
        ("Card Status / Echo Pattern", "32 біти (Статуси та прапори)", 360, "#fef3c7"),
        ("CRC7", "7 бітів", 135, "#dcfce7"),
        ("E", "1", 30, WARN_BG),
    ]
    cur_x = 45
    for name, desc, w_box, bg_c in fields_r1:
        p.append(rect(cur_x, 232, w_box, 42, fill=bg_c, stroke=LINE, sw=1.0, rx=3))
        p.append(text(cur_x + w_box / 2, 249, name, size=10, color=INK, bold=True))
        p.append(text(cur_x + w_box / 2, 264, desc, size=9, color=MUTED))
        cur_x += w_box + 7

    # R2 (136 бітів)
    p.append(text(45, 294, "Довга відповідь R2 (136 бітів — Регістри CID / CSD):", size=10, color=INK, bold=True, anchor="start"))
    fields_r2 = [
        ("S", "0", 30, WARN_BG),
        ("T", "0", 30, HL_BG),
        ("Reserved", "6 бітів", 100, "#e0f2fe"),
        ("CID або CSD Регістр", "128 бітів (Ідентифікатор / геометрія)", 415, "#fef3c7"),
        ("CRC7", "7 бітів", 120, "#dcfce7"),
        ("E", "1", 30, WARN_BG),
    ]
    cur_x = 45
    for name, desc, w_box, bg_c in fields_r2:
        p.append(rect(cur_x, 302, w_box, 42, fill=bg_c, stroke=LINE, sw=1.0, rx=3))
        p.append(text(cur_x + w_box / 2, 319, name, size=10, color=INK, bold=True))
        p.append(text(cur_x + w_box / 2, 334, desc, size=9, color=MUTED))
        cur_x += w_box + 7

    # 3. Структура 512-байтного блоку даних у 4-бітовому режимі
    p.append(rect(30, 375, 780, 165, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 396, "Пакет передачі даних 512 байт (4-бітний паралельний режим DAT0..DAT3)", size=11, color=INK, bold=True, anchor="start"))

    lanes = [
        ("DAT0", "S=0", "Нібли [0, 2, 4 ... 1022] (1024 біти)", "CRC16 [0] (16 бітів)", "E=1"),
        ("DAT1", "S=0", "Нібли [0, 2, 4 ... 1022] (1024 біти)", "CRC16 [1] (16 бітів)", "E=1"),
        ("DAT2", "S=0", "Нібли [1, 3, 5 ... 1023] (1024 біти)", "CRC16 [2] (16 бітів)", "E=1"),
        ("DAT3", "S=0", "Нібли [1, 3, 5 ... 1023] (1024 біти)", "CRC16 [3] (16 бітів)", "E=1"),
    ]

    for idx, (lane_name, s_bit, payload, crc_val, e_bit) in enumerate(lanes):
        y_pos = 412 + idx * 30
        p.append(text(45, y_pos + 16, lane_name, size=10.5, color=DAT_COL, bold=True, anchor="start"))
        # S
        p.append(rect(95, y_pos, 42, 24, fill=WARN_BG, stroke=LINE, sw=0.8, rx=2))
        p.append(text(116, y_pos + 16, s_bit, size=9.5, color=INK, bold=True))
        # Payload
        p.append(rect(145, y_pos, 420, 24, fill="#fef3c7", stroke=LINE, sw=0.8, rx=2))
        p.append(text(355, y_pos + 16, payload, size=9.5, color=INK))
        # CRC16
        p.append(rect(575, y_pos, 170, 24, fill="#dcfce7", stroke=LINE, sw=0.8, rx=2))
        p.append(text(660, y_pos + 16, crc_val, size=9.5, color=FIELD, bold=True))
        # E
        p.append(rect(753, y_pos, 42, 24, fill=WARN_BG, stroke=LINE, sw=0.8, rx=2))
        p.append(text(774, y_pos + 16, e_bit, size=9.5, color=INK, bold=True))

    render(os.path.join(OUT, "command-response-frames.svg"), W, H, *p)


# ── 3. Автомат станів ініціалізації та ідентифікації ─────────────────────────
def fig_init_state_machine():
    W, H = 840, 620
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Заголовок
    p.append(text(W / 2, 32, "Послідовність ініціалізації та автомат станів карти SD (SD Physical Layer)", size=13.5, color=INK, bold=True))

    # Стовпчик кроків (Flowchart)
    steps = [
        (55, "1. Подача живлення VDD", "VDD > 2.7В, пауза >= 1мс, генерація >= 74 тактів CLK з CMD/DAT=1", CARD_BG, "Стан: Inactive / Power-on"),
        (122, "2. CMD0 (GO_IDLE_STATE)", "Апаратне скидання внутрішньої логіки карти у вихідний стан", HL_BG, "Стан: Idle State"),
        (189, "3. CMD8 (SEND_IF_COND)", "VHS=2.7–3.6В, Check Pattern = 0xAA. Відповідь R7 підтверджує SD v2.0+", "#e0f2fe", "Перевірка інтерфейсу"),
        (256, "4. Цикл CMD55 + ACMD41", "HCS=1 (Host Capacity Support). Опитування Busy (біт 31 OCR) та CCS (біт 30 OCR)", "#fef3c7", "Стан: Ready (SDHC/SDXC)"),
        (323, "5. CMD2 (ALL_SEND_CID)", "Зчитування 128-бітного ідентифікатора карти (виробник, OEM, серійний номер)", "#dcfce7", "Стан: Identification State"),
        (390, "6. CMD3 (SEND_RELATIVE_ADDR)", "Карта публікує відносну адресу RCA (16 бітів) та повертає статус R6", "#e0e7ff", "Стан: Standby State"),
        (457, "7. CMD7 (SELECT_CARD з RCA)", "Вибір активної карти на спільній шині, перехід до передачі даних", "#fae8ff", "Стан: Transfer (Data Mode)"),
        (524, "8. CMD55 + ACMD6 (SET_BUS_WIDTH)", "Аргумент 0x02: перемикання з 1-бітового на 4-бітовий паралельний режим шини", HL_BG, "Готовність до читання/запису"),
    ]

    for y_pos, title_txt, desc_txt, bg_c, state_txt in steps:
        p.append(rect(40, y_pos, 510, 54, fill=bg_c, stroke=LINE, sw=1.1, rx=5))
        p.append(text(55, y_pos + 20, title_txt, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(55, y_pos + 40, desc_txt, size=9.5, color=MUTED, anchor="start"))

        # Блок стану
        p.append(rect(565, y_pos, 235, 54, fill="#ffffff", stroke=LINE, sw=1.0, rx=5))
        p.append(text(682, y_pos + 32, state_txt, size=10, color=CMD_COL if "Transfer" in state_txt else INK, bold=True))

        # Стрілка вниз
        if y_pos < 524:
            p.append(arrow(295, y_pos + 54, 295, y_pos + 67, color=LINE, sw=1.5))
            p.append(arrow(682, y_pos + 54, 682, y_pos + 67, color=LINE, sw=1.2))

    render(os.path.join(OUT, "init-state-machine.svg"), W, H, *p)


# ── 4. Часові діаграми читання та запису блоків ─────────────────────────────
def fig_data_read_write_timing():
    W, H = 840, 510
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Заголовок
    p.append(text(W / 2, 32, "Часові діаграми одиночного читання (CMD17) та запису (CMD24) блоку 512 байт", size=13.5, color=INK, bold=True))

    # Секція 1: Одиночне читання CMD17
    p.append(rect(30, 50, 780, 205, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 70, "А. Одиночне читання блоку: CMD17 (Single Block Read)", size=11, color=INK, bold=True, anchor="start"))

    # Лінія CMD
    p.append(text(45, 105, "CMD", size=11, color=CMD_COL, bold=True, anchor="start"))
    p.append(line(85, 100, 790, 100, color=MUTED, sw=1.0, dash="3,3"))
    
    # CMD17
    p.append(rect(100, 85, 130, 30, fill=HL_BG, stroke=CMD_COL, sw=1.2, rx=3))
    p.append(text(165, 104, "CMD17 [48 бітів]", size=9.5, color=CMD_COL, bold=True))

    # R1 Response
    p.append(rect(270, 85, 120, 30, fill=CARD_BG, stroke=CMD_COL, sw=1.2, rx=3))
    p.append(text(330, 104, "R1 Resp [48 бітів]", size=9.5, color=INK, bold=True))

    # Лінія DAT0..DAT3
    p.append(text(45, 160, "DAT0..3", size=11, color=DAT_COL, bold=True, anchor="start"))
    p.append(line(85, 155, 790, 155, color=MUTED, sw=1.0, dash="3,3"))

    # Затримка доступу
    p.append(rect(395, 140, 60, 30, fill=WARN_BG, stroke=MUTED, sw=0.8, rx=2))
    p.append(text(425, 158, "t_NAC", size=9.5, color=POS, bold=True))

    # Data Block
    p.append(rect(465, 140, 35, 30, fill=WARN_BG, stroke=DAT_COL, sw=1.0, rx=2))
    p.append(text(482, 158, "S=0", size=9.5, color=INK, bold=True))

    p.append(rect(508, 140, 185, 30, fill="#fef3c7", stroke=DAT_COL, sw=1.2, rx=3))
    p.append(text(600, 158, "512 байтів (1024 нібли)", size=10, color=INK, bold=True))

    p.append(rect(700, 140, 60, 30, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=2))
    p.append(text(730, 158, "CRC16", size=9.5, color=FIELD, bold=True))

    p.append(rect(766, 140, 30, 30, fill=WARN_BG, stroke=DAT_COL, sw=1.0, rx=2))
    p.append(text(781, 158, "E=1", size=9.5, color=INK, bold=True))

    # Секція 2: Одиночний запис CMD24
    p.append(rect(30, 270, 780, 220, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 290, "Б. Одиночний запис блоку: CMD24 (Single Block Write) та сигналізація Busy", size=11, color=INK, bold=True, anchor="start"))

    # Лінія CMD
    p.append(text(45, 325, "CMD", size=11, color=CMD_COL, bold=True, anchor="start"))
    p.append(line(85, 320, 790, 320, color=MUTED, sw=1.0, dash="3,3"))
    
    # CMD24
    p.append(rect(100, 305, 130, 30, fill=HL_BG, stroke=CMD_COL, sw=1.2, rx=3))
    p.append(text(165, 324, "CMD24 [48 бітів]", size=9.5, color=CMD_COL, bold=True))

    # R1 Response
    p.append(rect(260, 305, 120, 30, fill=CARD_BG, stroke=CMD_COL, sw=1.2, rx=3))
    p.append(text(320, 324, "R1 Resp [48 бітів]", size=9.5, color=INK, bold=True))

    # Лінія DAT0..DAT3
    p.append(text(45, 380, "DAT0..3", size=11, color=DAT_COL, bold=True, anchor="start"))
    p.append(line(85, 375, 790, 375, color=MUTED, sw=1.0, dash="3,3"))

    # Data Block from Host
    p.append(rect(385, 360, 35, 30, fill=WARN_BG, stroke=DAT_COL, sw=1.0, rx=2))
    p.append(text(402, 378, "S=0", size=9, color=INK, bold=True))

    p.append(rect(426, 360, 140, 30, fill="#fef3c7", stroke=DAT_COL, sw=1.2, rx=3))
    p.append(text(496, 378, "512B Дані (Хост)", size=9.5, color=INK, bold=True))

    p.append(rect(572, 360, 52, 30, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=2))
    p.append(text(598, 378, "CRC16", size=9, color=FIELD, bold=True))

    p.append(rect(630, 360, 30, 30, fill=WARN_BG, stroke=DAT_COL, sw=1.0, rx=2))
    p.append(text(645, 378, "E=1", size=9, color=INK, bold=True))

    # Data Response Token & Busy on DAT0
    p.append(text(45, 435, "DAT0", size=11, color=POS, bold=True, anchor="start"))
    p.append(line(85, 430, 790, 430, color=MUTED, sw=1.0, dash="3,3"))

    p.append(rect(665, 415, 52, 30, fill=HL_BG, stroke=STAT_COL, sw=1.2, rx=2))
    p.append(text(691, 433, "010b OK", size=9, color=STAT_COL, bold=True))

    # Busy low
    p.append(rect(725, 423, 75, 22, fill=WARN_BG, stroke=POS, sw=1.2, rx=2))
    p.append(text(762, 438, "Busy (0V)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "data-read-write-timing.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sd_bus_topology()
    fig_command_response_frames()
    fig_init_state_machine()
    fig_data_read_write_timing()
    print("All figures generated successfully.")
