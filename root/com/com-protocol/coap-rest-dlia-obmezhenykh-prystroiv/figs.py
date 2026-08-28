# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми CoAP (Constrained Application Protocol)."""

import os
import sys

# Підключення svgkit із scripts/ (4 рівні вгору від root/com/com-protocol/<slug>)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_coap_header():
    """Фігура 1: Будова бінарного повідомлення CoAP (4 байти заголовка + токен + опції + навантаження)."""
    w, h = 820, 440
    frags = []

    # Сітка 32 бітів
    x0, y0 = 50, 60
    total_w = 720
    bit_w = total_w / 32.0
    row_h = 48

    # Шкала бітів
    for b in range(32):
        bx = x0 + b * bit_w
        if b in (0, 1, 2, 3, 4, 7, 8, 15, 16, 31):
            frags.append(text(bx + bit_w / 2, y0 - 8, str(b), size=10, color=MUTED))

    # Рядок 1: Базовий заголовок 4 байти (32 біти)
    # Ver (2 біти)
    frags.append(fitbox(x0, y0, bit_w * 2, row_h, "Ver\n(2б)", size=11, fill="#e8f4f8", stroke=NEG, bold=True))
    # T (2 біти)
    frags.append(fitbox(x0 + bit_w * 2, y0, bit_w * 2, row_h, "T\n(2б)", size=11, fill="#e8f8f5", stroke=FIELD, bold=True))
    # TKL (4 біти)
    frags.append(fitbox(x0 + bit_w * 4, y0, bit_w * 4, row_h, "TKL (4 біти)\nToken Len", size=11, fill="#fef9e7", stroke="#d4ac0d", bold=True))
    # Code (8 бітів)
    frags.append(fitbox(x0 + bit_w * 8, y0, bit_w * 8, row_h, "Код (Code, 8 бітів)\nКлас (3б) . Деталь (5б)", size=11, fill="#fbeee6", stroke=POS, bold=True))
    # Message ID (16 бітів)
    frags.append(fitbox(x0 + bit_w * 16, y0, bit_w * 16, row_h, "Ідентифікатор повідомлення (Message ID, 16 бітів)", size=12, fill="#f4f6f8", stroke=LINE, bold=True))

    # Пояснення фіксованого заголовка
    frags.append(textbox(x0 + total_w / 2, y0 + row_h + 20, "Фіксований базовий заголовок CoAP — рівно 4 байти (32 біти)", size=12, fill="#ffffff", stroke=MUTED, bold=True)[0])

    # Рядок 2: Token (0..8 байтів)
    y1 = y0 + row_h + 46
    frags.append(fitbox(x0, y1, total_w, row_h, "Токен (Token, 0–8 байтів, довжина задається полем TKL)\nНаскрізний ідентифікатор запиту-відповіді для клієнта", size=12, fill="#fefde8", stroke="#b7950b"))

    # Рядок 3: Опції з дельта-кодуванням
    y2 = y1 + row_h + 14
    opt_w1 = total_w * 0.22
    opt_w2 = total_w * 0.22
    opt_w3 = total_w * 0.56
    frags.append(fitbox(x0, y2, opt_w1, row_h, "Option Delta\n(4 або 12/20 біт)", size=11, fill="#edf2f7", stroke="#4a5568", bold=True))
    frags.append(fitbox(x0 + opt_w1, y2, opt_w2, row_h, "Option Length\n(4 або 12/20 біт)", size=11, fill="#edf2f7", stroke="#4a5568", bold=True))
    frags.append(fitbox(x0 + opt_w1 + opt_w2, y2, opt_w3, row_h, "Значення опції (Option Value, довжина L байтів)\nUri-Path, Content-Format, Max-Age, Observe, Block2...", size=11, fill="#edf2f7", stroke="#4a5568"))

    # Рядок 4: Маркер корисного навантаження + Payload
    y3 = y2 + row_h + 14
    m_w = total_w * 0.18
    p_w = total_w * 0.82
    frags.append(fitbox(x0, y3, m_w, row_h, "Маркер 0xFF\n(1 байт)", size=12, fill="#fadbd8", stroke=POS, bold=True))
    frags.append(fitbox(x0 + m_w, y3, p_w, row_h, "Корисне навантаження (Payload, до кінця UDP-датаграми)\nСенсорні дані, JSON, CBOR, бінарний масив або текст", size=12, fill="#e8f8f5", stroke=FIELD, bold=True))

    # Нижня анотація
    frags.append(textbox(x0 + total_w / 2, y3 + row_h + 24, "Компактна структура: мінімальний пакет без опцій та тіла становить лише 4 байти", size=12, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "coap-header-format.svg"), w, h, *frags)


def fig_coap_messages():
    """Фігура 2: Чотири типи повідомлень (CON+ACK попутна відповідь, окрема відповідь, NON, RST)."""
    w, h = 840, 520
    frags = []

    # Ділимо полотно на 4 колонки/секції
    col_w = 380
    row_h_sec = 210

    # Секція 1 (зліва зверху): CON з попутною відповіддю (Piggybacked)
    x1, y1 = 40, 40
    frags.append(rect(x1, y1, col_w, row_h_sec, fill="#fbfcfd", stroke="#d5dbdb", sw=1.2))
    frags.append(text(x1 + col_w / 2, y1 + 22, "1. CON + попутна відповідь у ACK", size=13, color=INK, bold=True))
    # Вузли
    frags.append(textbox(x1 + 60, y1 + 55, "Клієнт", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    frags.append(textbox(x1 + col_w - 60, y1 + 55, "Сервер", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    # Стрілки
    frags.append(arrow(x1 + 80, y1 + 95, x1 + col_w - 80, y1 + 95, color=NEG, sw=1.8))
    frags.append(text(x1 + col_w / 2, y1 + 86, "CON [MID=0x1A01, GET /temp, Tkn=0x42]", size=10, color=NEG, bold=True))
    frags.append(arrow(x1 + col_w - 80, y1 + 145, x1 + 80, y1 + 145, color=FIELD, sw=1.8))
    frags.append(text(x1 + col_w / 2, y1 + 136, "ACK [MID=0x1A01, 2.05 Content, Tkn=0x42]", size=10, color=FIELD, bold=True))
    frags.append(text(x1 + col_w / 2, y1 + 185, "Відповідь повертається одразу в тілі квитанції ACK", size=10, color=MUTED, italic=True))

    # Секція 2 (справа зверху): Окрема відповідь (Separate response)
    x2 = x1 + col_w + 35
    frags.append(rect(x2, y1, col_w, row_h_sec, fill="#fbfcfd", stroke="#d5dbdb", sw=1.2))
    frags.append(text(x2 + col_w / 2, y1 + 22, "2. Окрема відповідь (Separate)", size=13, color=INK, bold=True))
    frags.append(textbox(x2 + 60, y1 + 45, "Клієнт", size=12, fill="#ffffff", stroke=LINE, pad=5)[0])
    frags.append(textbox(x2 + col_w - 60, y1 + 45, "Сервер", size=12, fill="#ffffff", stroke=LINE, pad=5)[0])
    # Стрілка 1: CON запит
    frags.append(arrow(x2 + 80, y1 + 75, x2 + col_w - 80, y1 + 75, color=NEG, sw=1.6))
    frags.append(text(x2 + col_w / 2, y1 + 67, "CON [MID=0x1A02, GET /slow, Tkn=0x77]", size=9, color=NEG, bold=True))
    # Стрілка 2: Порожній ACK
    frags.append(arrow(x2 + col_w - 80, y1 + 105, x2 + 80, y1 + 105, color=MUTED, sw=1.6))
    frags.append(text(x2 + col_w / 2, y1 + 97, "ACK [MID=0x1A02, Порожній 0.00]", size=9, color=MUTED))
    # Стрілка 3: Новий CON з даними
    frags.append(arrow(x2 + col_w - 80, y1 + 140, x2 + 80, y1 + 140, color=FIELD, sw=1.6))
    frags.append(text(x2 + col_w / 2, y1 + 132, "CON [MID=0x8B30, 2.05 Content, Tkn=0x77]", size=9, color=FIELD, bold=True))
    # Стрілка 4: ACK клієнта
    frags.append(arrow(x2 + 80, y1 + 170, x2 + col_w - 80, y1 + 170, color=MUTED, sw=1.6))
    frags.append(text(x2 + col_w / 2, y1 + 162, "ACK [MID=0x8B30, Порожній 0.00]", size=9, color=MUTED))
    frags.append(text(x2 + col_w / 2, y1 + 195, "Сервер бере паузу на обробку, Token зшиває запит", size=10, color=MUTED, italic=True))

    # Секція 3 (зліва знизу): NON-повідомлення (Непідтверджуване)
    y3 = y1 + row_h_sec + 25
    frags.append(rect(x1, y3, col_w, row_h_sec, fill="#fbfcfd", stroke="#d5dbdb", sw=1.2))
    frags.append(text(x1 + col_w / 2, y3 + 22, "3. Непідтверджуваний обмін (NON)", size=13, color=INK, bold=True))
    frags.append(textbox(x1 + 60, y3 + 55, "Клієнт", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    frags.append(textbox(x1 + col_w - 60, y3 + 55, "Сервер", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    frags.append(arrow(x1 + 80, y3 + 95, x1 + col_w - 80, y3 + 95, color=NEG, sw=1.8))
    frags.append(text(x1 + col_w / 2, y3 + 86, "NON [MID=0x3F10, GET /telemetry, Tkn=0x99]", size=10, color=NEG, bold=True))
    frags.append(arrow(x1 + col_w - 80, y3 + 145, x1 + 80, y3 + 145, color=FIELD, sw=1.8))
    frags.append(text(x1 + col_w / 2, y3 + 136, "NON [MID=0x3F11, 2.05 Content, Tkn=0x99]", size=10, color=FIELD, bold=True))
    frags.append(text(x1 + col_w / 2, y3 + 185, "Без квитування ACK: мінімум трафіку для періодичних даних", size=10, color=MUTED, italic=True))

    # Секція 4 (справа знизу): Скидання (Reset - RST)
    frags.append(rect(x2, y3, col_w, row_h_sec, fill="#fbfcfd", stroke="#d5dbdb", sw=1.2))
    frags.append(text(x2 + col_w / 2, y3 + 22, "4. Скидання зв'язку (RST)", size=13, color=INK, bold=True))
    frags.append(textbox(x2 + 60, y3 + 55, "Клієнт", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    frags.append(textbox(x2 + col_w - 60, y3 + 55, "Сервер", size=12, fill="#ffffff", stroke=LINE, pad=6)[0])
    frags.append(arrow(x2 + 80, y3 + 95, x2 + col_w - 80, y3 + 95, color=NEG, sw=1.8))
    frags.append(text(x2 + col_w / 2, y3 + 86, "NON / CON [MID=0x5C22, Невідомий контекст]", size=10, color=NEG, bold=True))
    frags.append(arrow(x2 + col_w - 80, y3 + 145, x2 + 80, y3 + 145, color=POS, sw=1.8))
    frags.append(text(x2 + col_w / 2, y3 + 136, "RST [MID=0x5C22, Помилка / відхилення]", size=10, color=POS, bold=True))
    frags.append(text(x2 + col_w / 2, y3 + 185, "Ознака перезавантаження або відсутності контексту обробки", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "coap-message-types.svg"), w, h, *frags)


def fig_coap_observe():
    """Фігура 3: Механізм підписки та спостереження Observe (RFC 7641)."""
    w, h = 800, 480
    frags = []

    # Лінії життя (життя вузлів)
    c_x, s_x = 180, 620
    y_top, y_bot = 60, 430

    frags.append(line(c_x, y_top + 30, c_x, y_bot, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(s_x, y_top + 30, s_x, y_bot, color=MUTED, sw=1.5, dash="4,4"))

    # Шапки вузлів
    frags.append(textbox(c_x, y_top, "Клієнт (Спостерігач)", size=13, fill="#e8f4f8", stroke=NEG, bold=True, pad=8)[0])
    frags.append(textbox(s_x, y_top, "Сервер (Джерело даних)", size=13, fill="#e8f8f5", stroke=FIELD, bold=True, pad=8)[0])

    # Крок 1: Реєстрація підписки
    y1 = 120
    frags.append(arrow(c_x, y1, s_x, y1, color=NEG, sw=1.8))
    frags.append(textbox(400, y1 - 16, "GET /sensors/light [CON, MID=100, Token=0xAA, Observe=0]", size=11, fill="#ffffff", stroke=NEG, pad=4)[0])

    # Крок 2: Початкова відповідь
    y2 = 170
    frags.append(arrow(s_x, y2, c_x, y2, color=FIELD, sw=1.8))
    frags.append(textbox(400, y2 - 16, "ACK 2.05 Content [MID=100, Token=0xAA, Observe=120, '450 lx']", size=11, fill="#ffffff", stroke=FIELD, pad=4)[0])

    # Стан: реєстрація в таблиці
    frags.append(textbox(s_x, 215, "Сервер реєструє підписку:\nIP, Port, Token=0xAA", size=10, fill="#fef9e7", stroke="#d4ac0d", pad=4)[0])

    # Крок 3: Асинхронне сповіщення 1 (зміна освітленості)
    y3 = 265
    frags.append(arrow(s_x, y3, c_x, y3, color=FIELD, sw=1.8))
    frags.append(textbox(400, y3 - 16, "NON 2.05 Content [MID=301, Token=0xAA, Observe=121, '720 lx']", size=11, fill="#ffffff", stroke=FIELD, pad=4)[0])

    # Крок 4: Періодична перевірка доступності спостерігача (CON)
    y4 = 325
    frags.append(arrow(s_x, y4, c_x, y4, color=POS, sw=1.8))
    frags.append(textbox(400, y4 - 16, "CON 2.05 Content [MID=302, Token=0xAA, Observe=122, '715 lx']", size=11, fill="#ffffff", stroke=POS, pad=4)[0])

    # Крок 5: Квитування або скасування
    y5 = 375
    frags.append(arrow(c_x, y5, s_x, y5, color=MUTED, sw=1.8))
    frags.append(textbox(400, y5 - 16, "ACK [MID=302] (підтвердження) АБО RST [MID=302] (скасування підписки)", size=10, fill="#ffffff", stroke=MUTED, pad=4)[0])

    frags.append(textbox(400, 440, "Observe перетворює REST на ефективну модель push-сповіщень без накладних витрат опитування", size=11, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "coap-observe-pattern.svg"), w, h, *frags)


def fig_coap_blockwise():
    """Фігура 4: Блокова передача Block-Wise Transfer (RFC 7959) для Block1 та Block2."""
    w, h = 820, 460
    frags = []

    # Верхній блок: анатомія опції Block1 / Block2
    y_opt = 35
    frags.append(textbox(410, y_opt, "Бінарна структура опції Block1 (27) та Block2 (23): 1–3 байти", size=13, fill="#f4f6f8", stroke=LINE, bold=True, pad=6)[0])

    bx0 = 120
    bw_num = 360
    bw_m = 90
    bw_szx = 130
    h_box = 40
    y_box = 65

    frags.append(fitbox(bx0, y_box, bw_num, h_box, "NUM: Номер блока (4, 12 або 20 бітів)\nПорядковий індекс фрагмента 0, 1, 2...", size=11, fill="#e8f4f8", stroke=NEG, bold=True))
    frags.append(fitbox(bx0 + bw_num, y_box, bw_m, h_box, "M: More (1 біт)\n0=Кінець, 1=Є ще", size=10, fill="#fadbd8", stroke=POS, bold=True))
    frags.append(fitbox(bx0 + bw_num + bw_m, y_box, bw_szx, h_box, "SZX (3 біти): Розмір\n2^(SZX+4): 16..1024 б", size=10, fill="#e8f8f5", stroke=FIELD, bold=True))

    # Нижній блок: діаграма обміну Block2 (завантаження великої відповіді блоками)
    y_seq = 140
    c_x, s_x = 160, 660

    frags.append(line(c_x, y_seq + 25, c_x, 410, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(s_x, y_seq + 25, s_x, 410, color=MUTED, sw=1.5, dash="4,4"))

    frags.append(textbox(c_x, y_seq, "Клієнт", size=12, fill="#e8f4f8", stroke=NEG, bold=True, pad=5)[0])
    frags.append(textbox(s_x, y_seq, "Сервер", size=12, fill="#e8f8f5", stroke=FIELD, bold=True, pad=5)[0])

    # Крок 1: Запит першого блока
    y1 = 190
    frags.append(arrow(c_x, y1, s_x, y1, color=NEG, sw=1.6))
    frags.append(textbox(410, y1 - 14, "GET /firmware/log [Block2: NUM=0, SZX=6 (1024 б)]", size=10, fill="#ffffff", stroke=NEG, pad=3)[0])

    # Крок 2: Відповідь блоком 0
    y2 = 240
    frags.append(arrow(s_x, y2, c_x, y2, color=FIELD, sw=1.6))
    frags.append(textbox(410, y2 - 14, "2.05 Content [Block2: NUM=0, M=1, SZX=6] + 1024 байти даних", size=10, fill="#ffffff", stroke=FIELD, pad=3)[0])

    # Крок 3: Запит другого блока
    y3 = 290
    frags.append(arrow(c_x, y3, s_x, y3, color=NEG, sw=1.6))
    frags.append(textbox(410, y3 - 14, "GET /firmware/log [Block2: NUM=1, SZX=6 (1024 б)]", size=10, fill="#ffffff", stroke=NEG, pad=3)[0])

    # Крок 4: Відповідь блоком 1
    y4 = 340
    frags.append(arrow(s_x, y4, c_x, y4, color=FIELD, sw=1.6))
    frags.append(textbox(410, y4 - 14, "2.05 Content [Block2: NUM=1, M=1, SZX=6] + 1024 байти даних", size=10, fill="#ffffff", stroke=FIELD, pad=3)[0])

    # Крок 5: Запит фінального блока
    y5 = 390
    frags.append(arrow(c_x, y5, s_x, y5, color=NEG, sw=1.6))
    frags.append(textbox(410, y5 - 14, "GET /firmware/log [Block2: NUM=2, SZX=6] -> Сервер шле [NUM=2, M=0] (фінал)", size=10, fill="#ffffff", stroke=NEG, pad=3)[0])

    frags.append(textbox(410, 435, "Передача великих даних усуває IP-фрагментацію на слабких каналах 6LoWPAN / NB-IoT", size=11, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "coap-blockwise.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_coap_header()
    fig_coap_messages()
    fig_coap_observe()
    fig_coap_blockwise()
    print("All figures rendered successfully.")
