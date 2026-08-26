# -*- coding: utf-8 -*-
"""Фігури до теми «Свій кадр між двома платами» (root/course/embedded/svii-kadr-mizh-dvoma-platamy).
Запуск: python figs.py  -> створює SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_framing_problem():
    W, H = 860, 360
    f = []
    f.append(text(W / 2, 28, "Проблема меж кадру в безперервному байтовому потоці UART", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "UART не знає про пакети: збій одного байта ламає межі всіх наступних повідомлень", 11.5, MUTED, "middle", italic=True))

    # Секція 1: Потік із пошкодженою довжиною (Length-Prefix Failure)
    y1 = 80
    f.append(text(30, y1 + 15, "1. Довжина в заголовку (Length-prefixed): збій поля LEN поглинає наступні кадри", 12.5, INK, "start", bold=True))

    bytes_data = [
        ("0x02", FILL, INK), ("0xAA", FILL, INK), ("0xBB", FILL, INK),
        ("0xFA", "#fdecea", POS),  # пошкоджений LEN: замість 0x02 прийшло 0xFA (250 байтів)
        ("0x11", FILL, INK), ("0x22", FILL, INK),
        ("0x03", FILL, INK), ("0x33", FILL, INK), ("0x44", FILL, INK), ("0x55", FILL, INK)
    ]
    labels = [
        "LEN=2", "кадр 1", "кадр 1",
        "LEN=250!", "кадр 2", "кадр 2",
        "LEN=3", "кадр 3", "кадр 3", "кадр 3"
    ]

    bx = 30
    bw = 72
    bh = 36
    for i, ((bval, bfill, bcol), blbl) in enumerate(zip(bytes_data, labels)):
        x = bx + i * (bw + 8)
        f.append(rect(x, y1 + 30, bw, bh, fill=bfill, stroke=bcol, sw=1.5, rx=4))
        f.append(text(x + bw / 2, y1 + 53, bval, 13, bcol, "middle", bold=True))
        f.append(text(x + bw / 2, y1 + 80, blbl, 10, MUTED, "middle"))

    f.append(line(bx + 3 * (bw + 8), y1 + 95, bx + 10 * (bw + 8) - 8, y1 + 95, color=POS, sw=1.8, dash="4,3"))
    f.append(text(bx + 6.5 * (bw + 8), y1 + 112, "Приймач чекає 250 байтів: кадри 2 і 3 ковтаються як «дані» битого кадру", 11, POS, "middle", bold=True))

    # Секція 2: Таймаути між байтами (Silent Gap Failure)
    y2 = 220
    f.append(text(30, y2 + 15, "2. Міжкадровий таймаут (Modbus-подібний): джиттер RTOS розриває цілий кадр", 12.5, INK, "start", bold=True))

    f.append(rect(30, y2 + 30, 220, bh, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(140, y2 + 53, "Кадр A (байти 1..8)", 12, FIELD, "middle", bold=True))

    f.append(line(255, y2 + 48, 335, y2 + 48, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(295, y2 + 40, "пауза", 10.5, MUTED, "middle"))

    f.append(rect(340, y2 + 30, 140, bh, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(410, y2 + 53, "Кадр B (частина 1)", 11.5, POS, "middle", bold=True))

    f.append(rect(490, y2 + 30, 130, bh, fill="#fff3cd", stroke="#e67e22", sw=1.5, rx=4))
    f.append(text(555, y2 + 46, "Затримка RTOS > T_gap", 10, "#d35400", "middle", bold=True))
    f.append(text(555, y2 + 59, "фальшивий таймаут!", 9.5, "#d35400", "middle", italic=True))

    f.append(rect(630, y2 + 30, 140, bh, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(700, y2 + 53, "Кадр B (частина 2)", 11.5, POS, "middle", bold=True))

    f.append(text(30, y2 + 95, "Наслідок: один цілий кадр розколюється на два фрагменти, обидва відкидаються за помилкою CRC.", 11, INK, "start", italic=True))

    render(os.path.join(IMG, "framing-problem.svg"), W, H, *f)


def fig_cobs_mechanism():
    W, H = 860, 380
    f = []
    f.append(text(W / 2, 28, "Алгоритм COBS: заміна нулів зміщеннями та гарантований розділювач 0x00", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Нулі замінюються на відстані до наступного нуля, а сам 0x00 стає єдиним маркером кінця кадру", 11.5, MUTED, "middle", italic=True))

    # 1. Початковий масив байтів
    y1 = 85
    f.append(text(30, y1, "1. Сирі дані (містять байти 0x00 у корисних полях чи CRC):", 12.5, INK, "start", bold=True))

    raw_bytes = [
        ("0x22", FILL, INK),
        ("0x00", "#fdecea", POS),
        ("0x33", FILL, INK),
        ("0x44", FILL, INK),
        ("0x00", "#fdecea", POS),
        ("0x55", FILL, INK),
        ("0x66", FILL, INK)
    ]
    raw_sub = ["data[0]", "нуль 1", "data[2]", "data[3]", "нуль 2", "data[5]", "data[6]"]

    bx = 60
    bw = 70
    bh = 36
    for i, ((val, fill_c, strk_c), sub) in enumerate(zip(raw_bytes, raw_sub)):
        x = bx + i * (bw + 24)
        f.append(rect(x, y1 + 15, bw, bh, fill=fill_c, stroke=strk_c, sw=1.5, rx=4))
        f.append(text(x + bw / 2, y1 + 38, val, 13, strk_c, "middle", bold=True))
        f.append(text(x + bw / 2, y1 + 65, sub, 10, MUTED, "middle"))

    f.append(line(bx + bw / 2, y1 + 75, bx + 1 * (bw + 24) + bw / 2, y1 + 75, color=NEG, sw=1.8))
    f.append(text(bx + 0.5 * (bw + 24) + bw / 2, y1 + 90, "офсет = 2", 10.5, NEG, "middle", bold=True))

    f.append(line(bx + 1 * (bw + 24) + bw / 2, y1 + 75, bx + 4 * (bw + 24) + bw / 2, y1 + 75, color=NEG, sw=1.8))
    f.append(text(bx + 2.5 * (bw + 24) + bw / 2, y1 + 90, "офсет = 3", 10.5, NEG, "middle", bold=True))

    f.append(line(bx + 4 * (bw + 24) + bw / 2, y1 + 75, bx + 6 * (bw + 24) + bw / 2, y1 + 75, color=NEG, sw=1.8))
    f.append(text(bx + 5.5 * (bw + 24) + bw / 2, y1 + 90, "офсет = 3 (до кінця)", 10.5, NEG, "middle", bold=True))

    # 2. Закодований потік COBS
    y2 = 230
    f.append(text(30, y2, "2. Закодований кадр у лінії (жодного 0x00 всередині + розділювач 0x00 у кінці):", 12.5, INK, "start", bold=True))

    enc_bytes = [
        ("0x02", "#eaf0fd", NEG, "офсет 1"),
        ("0x22", FILL, INK, "data[0]"),
        ("0x03", "#eaf0fd", NEG, "офсет 2"),
        ("0x33", FILL, INK, "data[2]"),
        ("0x44", FILL, INK, "data[3]"),
        ("0x03", "#eaf0fd", NEG, "офсет 3"),
        ("0x55", FILL, INK, "data[5]"),
        ("0x66", FILL, INK, "data[6]"),
        ("0x00", "#eafaf1", FIELD, "МАРКЕР")
    ]

    bx2 = 35
    bw2 = 64
    for i, (val, fill_c, strk_c, sub) in enumerate(enc_bytes):
        x = bx2 + i * (bw2 + 18)
        f.append(rect(x, y2 + 15, bw2, bh, fill=fill_c, stroke=strk_c, sw=1.6, rx=4))
        f.append(text(x + bw2 / 2, y2 + 38, val, 13, strk_c, "middle", bold=True))
        f.append(text(x + bw2 / 2, y2 + 65, sub, 9.5, MUTED, "middle"))

    f.append(text(30, y2 + 105, "Результат: довжина збільшилася лише на 1 байт (overhead = +1 байт), а байт 0x00 гарантовано зустрічається тільки як кінець кадру.", 11, INK, "start", italic=True))

    render(os.path.join(IMG, "cobs-mechanism.svg"), W, H, *f)


def fig_frame_structure():
    W, H = 860, 360
    f = []
    f.append(text(W / 2, 28, "Анатомія кадру: логічна структура пакета та фізичний вигляд у лінії", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Корисні поля захищаються CRC-16, після чого весь пакет пакується в COBS-оболонку", 11.5, MUTED, "middle", italic=True))

    # Рівень 1: Логічний пакет (до кодування)
    y1 = 80
    f.append(text(30, y1 + 10, "1. Логічний пакет (структура в пам'яті мікроконтролера):", 12.5, INK, "start", bold=True))

    fields1 = [
        ("MSG ID\n(1 байт)", 80, "#eaf0fd", NEG),
        ("SEQ NUM\n(1 байт)", 80, "#eaf0fd", NEG),
        ("PAYLOAD LEN\n(2 байти)", 110, "#eaf0fd", NEG),
        ("PAYLOAD (КОРИСНІ ДАНІ)\n(0 .. 250 байтів)", 260, FILL, INK),
        ("CRC-16 CCITT\n(2 байти)", 120, "#fdecea", POS)
    ]

    x = 30
    bh = 44
    for title, w, fill_c, strk_c in fields1:
        f.append(rect(x, y1 + 25, w, bh, fill=fill_c, stroke=strk_c, sw=1.5, rx=4))
        lines = title.split("\n")
        f.append(text(x + w / 2, y1 + 44, lines[0], 11, strk_c, "middle", bold=True))
        f.append(text(x + w / 2, y1 + 59, lines[1], 9.5, MUTED, "middle"))
        x += w + 8

    f.append(line(30, y1 + 75, 30 + 80 + 80 + 110 + 260 + 24, y1 + 75, color=POS, sw=1.5, dash="3,3"))
    f.append(text(30 + (530) / 2, y1 + 90, "Область розрахунку CRC-16 (покриває заголовок і корисні дані)", 10.5, POS, "middle"))

    y_mid = y1 + 115
    f.append(line(W / 2, y_mid, W / 2, y_mid + 25, color=LINE, sw=1.6))
    f.append(arrow(W / 2, y_mid + 25, W / 2, y_mid + 40, color=LINE, sw=1.6))
    f.append(text(W / 2 + 15, y_mid + 24, "COBS-кодування (усунення всіх 0x00)", 11, MUTED, "start", italic=True))

    # Рівень 2: Фізичний кадр на лінії UART/RS-485
    y2 = y_mid + 50
    f.append(text(30, y2 + 10, "2. Фізичний кадр на лінії (те, що передається по UART / RS-485):", 12.5, INK, "start", bold=True))

    fields2 = [
        ("COBS Overhead\n(1 байт)", 110, "#eaf0fd", NEG),
        ("COBS Encoded Payload & Header & CRC\n(байти 0x01 .. 0xFF, жодного 0x00)", 480, FILL, INK),
        ("DELIMITER\n0x00 (1 байт)", 110, "#eafaf1", FIELD)
    ]

    x2 = 30
    for title, w, fill_c, strk_c in fields2:
        f.append(rect(x2, y2 + 25, w, bh, fill=fill_c, stroke=strk_c, sw=1.6, rx=4))
        lines = title.split("\n")
        f.append(text(x2 + w / 2, y2 + 44, lines[0], 11, strk_c, "middle", bold=True))
        f.append(text(x2 + w / 2, y2 + 59, lines[1], 9.5, MUTED, "middle"))
        x2 += w + 8

    render(os.path.join(IMG, "frame-structure.svg"), W, H, *f)


def fig_fsm_states():
    W, H = 860, 360
    f = []
    f.append(text(W / 2, 28, "Скінченний автомат приймача (Framing FSM)", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "Побайтовий розбір вхідного потоку, стійкий до сміття, обривів та переповнення", 11.5, MUTED, "middle", italic=True))

    x1, y1, w1, h1 = 60, 110, 170, 70
    f.append(rect(x1, y1, w1, h1, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 28, "STATE_IDLE", 13, NEG, "middle", bold=True))
    f.append(text(x1 + w1 / 2, y1 + 46, "Очікування кадру", 11, INK, "middle"))
    f.append(text(x1 + w1 / 2, y1 + 59, "rx_len = 0", 10, MUTED, "middle"))

    x2, y2, w2, h2 = 340, 110, 190, 70
    f.append(rect(x2, y2, w2, h2, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 28, "STATE_RECEIVE", 13, FIELD, "middle", bold=True))
    f.append(text(x2 + w2 / 2, y2 + 46, "Накопичення байтів", 11, INK, "middle"))
    f.append(text(x2 + w2 / 2, y2 + 59, "buf[rx_len++] = byte", 10, MUTED, "middle"))

    x3, y3, w3, h3 = 340, 245, 190, 65
    f.append(rect(x3, y3, w3, h3, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(x3 + w3 / 2, y3 + 26, "STATE_OVERFLOW", 13, POS, "middle", bold=True))
    f.append(text(x3 + w3 / 2, y3 + 44, "Буфер вичерпано", 11, INK, "middle"))
    f.append(text(x3 + w3 / 2, y3 + 57, "Скидання до 0x00", 10, MUTED, "middle"))

    x4, y4, w4, h4 = 630, 110, 180, 70
    f.append(rect(x4, y4, w4, h4, fill="#fff8e7", stroke="#d35400", sw=1.8, rx=8))
    f.append(text(x4 + w4 / 2, y4 + 24, "COBS DECODE", 12.5, "#d35400", "middle", bold=True))
    f.append(text(x4 + w4 / 2, y4 + 40, "Перевірка CRC-16", 11, INK, "middle"))
    f.append(text(x4 + w4 / 2, y4 + 56, "on_frame_valid()", 10.5, FIELD, "middle", bold=True))

    f.append(arrow(x1 + w1, y1 + 35, x2, y2 + 35, color=LINE, sw=1.5))
    f.append(text((x1 + w1 + x2) / 2, y1 + 25, "байт != 0x00", 10.5, INK, "middle", bold=True))

    f.append(line(x1 + 30, y1 + h1, x1 + 30, y1 + h1 + 20, color=MUTED, sw=1.4))
    f.append(line(x1 + 30, y1 + h1 + 20, x1 + 80, y1 + h1 + 20, color=MUTED, sw=1.4))
    f.append(arrow(x1 + 80, y1 + h1 + 20, x1 + 80, y1 + h1, color=MUTED, sw=1.4))
    f.append(text(x1 + 55, y1 + h1 + 32, "байт == 0x00 (тиша)", 9.5, MUTED, "middle"))

    f.append(line(x2 + 40, y2, x2 + 40, y2 - 22, color=MUTED, sw=1.4))
    f.append(line(x2 + 40, y2 - 22, x2 + 130, y2 - 22, color=MUTED, sw=1.4))
    f.append(arrow(x2 + 130, y2 - 22, x2 + 130, y2, color=MUTED, sw=1.4))
    f.append(text(x2 + 85, y2 - 27, "байт != 0x00 (накопичення)", 9.5, MUTED, "middle"))

    f.append(arrow(x2 + w2, y2 + 35, x4, y4 + 35, color=FIELD, sw=1.8))
    f.append(text((x2 + w2 + x4) / 2, y2 + 25, "байт == 0x00", 10.5, FIELD, "middle", bold=True))

    f.append(line(x4 + w4 / 2, y4 + h4, x4 + w4 / 2, y4 + h4 + 30, color=MUTED, sw=1.4))
    f.append(line(x4 + w4 / 2, y4 + h4 + 30, x1 + w1 / 2, y4 + h4 + 30, color=MUTED, sw=1.4))
    f.append(arrow(x1 + w1 / 2, y4 + h4 + 30, x1 + w1 / 2, y1 + h1, color=MUTED, sw=1.4))
    f.append(text((x4 + x1) / 2, y4 + h4 + 44, "Кадр оброблено -> повернення в IDLE", 10, MUTED, "middle"))

    f.append(arrow(x2 + 60, y2 + h2, x3 + 60, y3, color=POS, sw=1.5))
    f.append(text(x2 + 45, (y2 + h2 + y3) / 2, "len >= MAX", 9.5, POS, "end", bold=True))

    f.append(line(x3, y3 + 32, x1 + 40, y3 + 32, color=MUTED, sw=1.4))
    f.append(arrow(x1 + 40, y3 + 32, x1 + 40, y1 + h1, color=MUTED, sw=1.4))
    f.append(text((x3 + x1 + 40) / 2, y3 + 22, "байт == 0x00 (скидання сміття)", 9.5, MUTED, "middle"))

    render(os.path.join(IMG, "fsm-states.svg"), W, H, *f)


if __name__ == "__main__":
    fig_framing_problem()
    fig_cobs_mechanism()
    fig_frame_structure()
    fig_fsm_states()
    print("Figures generated successfully.")
