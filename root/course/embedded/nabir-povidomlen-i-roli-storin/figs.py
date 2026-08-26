# -*- coding: utf-8 -*-
"""Фігури до теми «Набір повідомлень і ролі сторін: клієнт, сервер, координатор»
(root/course/embedded/nabir-povidomlen-i-roli-storin).
Запуск: python figs.py -> створює SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_roles_and_topologies():
    W, H = 960, 480
    f = []
    f.append(text(W / 2, 28, "Комунікаційні ролі та топології в розподілених вбудованих мережах", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Розподіл ініціативи, детермінізм доступу до середовища та складність маршрутизації", 12, MUTED, "middle", italic=True))

    cards = [
        ("1. Master-Slave (Опитування)", "#eaf0fd", NEG, [
            "• Ініціатива: виключно Master.",
            "• Slaves відповідають лише на запит.",
            "• Плюси: 100% захист від колізій на RS-485.",
            "• Мінуси: затримка опитування (latency),",
            "  холостий трафік при відсутності змін."
        ]),
        ("2. Client-Server (Запит-відповідь)", "#eafaf1", FIELD, [
            "• Ініціатива: Клієнт за потребою події.",
            "• Сервер виконує дію та повертає статус.",
            "• Плюси: асинхронність, економія каналу,",
            "  паралельні транзакції за Sequence ID.",
            "• Мінуси: потрібен арбітраж або дуплекс."
        ]),
        ("3. Peer-to-Peer (Рівноправний)", "#fff3cd", "#d35400", [
            "• Ініціатива: будь-який вузол (Event / Pub).",
            "• Прямий обмін даними між сусідами.",
            "• Плюси: мінімальний час реакції на аварії,",
            "  немає єдиної точки відмови (SPOF).",
            "• Мінуси: ризик колізій та шторму подій."
        ]),
        ("4. Mesh Coordinator (Координатор)", "#f3e8fd", "#7d3c98", [
            "• Ініціатива: ведення мережевого дерева.",
            "• Роздача адрес, синхронізація часу,",
            "  маршрутизація транзитних пакетів.",
            "• Плюси: покриття великих просторів.",
            "• Мінуси: висока пам'ять на таблиці роутингу."
        ])
    ]

    card_w = 216
    card_h = 240
    start_x = 24
    start_y = 80
    gap = 18

    for i, (title_str, fill_c, strk_c, lines_list) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        cy = start_y
        f.append(rect(cx, cy, card_w, card_h, fill=fill_c, stroke=strk_c, sw=1.8, rx=8))
        f.append(rect(cx, cy, card_w, 36, fill=strk_c, stroke=strk_c, sw=1.8, rx=8))
        f.append(rect(cx, cy + 24, card_w, 12, fill=strk_c, stroke=strk_c, sw=0, rx=0))
        f.append(text(cx + card_w / 2, cy + 23, title_str, 12, BG, "middle", bold=True))

        for j, line_txt in enumerate(lines_list):
            f.append(text(cx + 10, cy + 58 + j * 20, line_txt, 11, INK, "start"))

    sum_y = 350
    f.append(rect(start_x, sum_y, W - 2 * start_x, 105, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(start_x + 16, sum_y + 24, "Ключовий критерій вибору архітектурної моделі:", 13, INK, "start", bold=True))
    f.append(text(start_x + 16, sum_y + 48, "• Фізичний напівдуплекс без апаратного арбітражу (RS-485 / голий UART)  ->  Master-Slave або Client-Server із токеном.", 11.5, INK, "start"))
    f.append(text(start_x + 16, sum_y + 70, "• Шинні інтерфейси з арбітражем пріоритетів (CAN-bus / I2C Multi-Master)  ->  Peer-to-Peer із подієвою моделлю.", 11.5, INK, "start"))
    f.append(text(start_x + 16, sum_y + 92, "• Бездротові транзитні топології з ретрансляцією (LoRa Mesh / Zigbee)   ->  Mesh Coordinator + Рухомі вузли.", 11.5, INK, "start"))

    render(os.path.join(IMG, "roles-and-topologies.svg"), W, H, *f)


def fig_message_envelope_layout():
    W, H = 960, 430
    f = []
    f.append(text(W / 2, 28, "Структура уніфікованого бінарного конверта транзакції (Transaction Envelope)", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Фіксований заголовок (Header 8 байтів), змінний Payload та кінцева контрольна сума CRC-16", 12, MUTED, "middle", italic=True))

    fields = [
        ("MSG_TYPE\n(1 байт)", 100, "#eaf0fd", NEG, "Тип повідомлення\n0x01..0xFF"),
        ("FLAGS\n(1 байт)", 95, "#fff3cd", "#d35400", "Прапорці транзакції\nACK, RESP, ERR"),
        ("TRANS_ID\n(1 байт)", 95, "#eaf0fd", NEG, "ID послідовності\n(Sequence ID)"),
        ("SRC_ADDR\n(1 байт)", 95, "#f3e8fd", "#7d3c98", "Адреса джерела\n0x01..0xFE"),
        ("DST_ADDR\n(1 байт)", 95, "#f3e8fd", "#7d3c98", "Адреса призначення\n(0x00=Broadcast)"),
        ("PAYLOAD_LEN\n(2 байти, LE)", 125, "#eaf0fd", NEG, "Довжина даних\n0 .. 512 байтів"),
        ("RESERVED\n(1 байт)", 95, "#f4f6f8", MUTED, "Вирівнювання 8B\n(версія 0x00)"),
        ("PAYLOAD (КОРИСНІ ДАНІ)\n(0 .. 512 байтів)", 150, "#eafaf1", FIELD, "Аргументи, телеметрія\nабо код помилки"),
        ("CRC-16 CCITT\n(2 байти, LE)", 110, "#fdecea", POS, "Контрольна сума\nHeader + Payload")
    ]

    start_x = 20
    y_pos = 95
    box_h = 58

    curr_x = start_x
    for title_str, bw, fill_c, strk_c, desc_str in fields:
        f.append(rect(curr_x, y_pos, bw, box_h, fill=fill_c, stroke=strk_c, sw=1.6, rx=6))
        lines = title_str.split("\n")
        f.append(text(curr_x + bw / 2, y_pos + 22, lines[0], 11, strk_c, "middle", bold=True))
        f.append(text(curr_x + bw / 2, y_pos + 38, lines[1], 9.5, MUTED, "middle"))

        desc_lines = desc_str.split("\n")
        f.append(text(curr_x + bw / 2, y_pos + 76, desc_lines[0], 10, INK, "middle", bold=True))
        if len(desc_lines) > 1:
            f.append(text(curr_x + bw / 2, y_pos + 90, desc_lines[1], 9.5, MUTED, "middle"))

        curr_x += bw + 6

    hdr_w = 100 + 95 + 95 + 95 + 95 + 125 + 95 + 6 * 6
    f.append(line(start_x, y_pos - 10, start_x + hdr_w, y_pos - 10, color=NEG, sw=1.8))
    f.append(line(start_x, y_pos - 10, start_x, y_pos - 4, color=NEG, sw=1.8))
    f.append(line(start_x + hdr_w, y_pos - 10, start_x + hdr_w, y_pos - 4, color=NEG, sw=1.8))
    f.append(text(start_x + hdr_w / 2, y_pos - 16, "Фіксований заголовок пакета (8 байтів) — 64-бітне вирівнювання", 11.5, NEG, "middle", bold=True))

    y_flags = 240
    f.append(rect(start_x, y_flags, 920, 170, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(start_x + 18, y_flags + 24, "Розпакування бітового поля FLAGS (1 байт):", 12.5, INK, "start", bold=True))

    flag_bits = [
        ("Bit 0: ACK_REQ", [
            "1 = потрібне підтвердження",
            "    (Response / ACK)",
            "0 = без квитування"
        ]),
        ("Bit 1: IS_RESP", [
            "1 = відповідь на запит",
            "    (Transaction Reply)",
            "0 = новий запит / івент"
        ]),
        ("Bit 2: IS_ERR", [
            "1 = помилка у Payload",
            "    (Error Response)",
            "0 = успіх або дані"
        ]),
        ("Bit 3: EXT_ADDR", [
            "1 = розширені адреси 16b",
            "    (у тілі Payload)",
            "0 = стандартні 8-бітні"
        ]),
        ("Bits 4..7: PROTO_VER", [
            "Версія протоколу 0..15",
            "для контролю сумісності",
            "різних прошивок"
        ])
    ]

    fb_x = start_x + 18
    fb_w = 172
    fb_gap = 8
    for i, (b_title, b_lines) in enumerate(flag_bits):
        bx = fb_x + i * (fb_w + fb_gap)
        by = y_flags + 38
        f.append(rect(bx, by, fb_w, 115, fill="#ffffff", stroke="#c0c4cc", sw=1.2, rx=6))
        f.append(rect(bx, by, fb_w, 24, fill="#fff3cd", stroke="#e67e22", sw=1.2, rx=6))
        f.append(text(bx + fb_w / 2, by + 16, b_title, 10.5, "#d35400", "middle", bold=True))

        for j, bline in enumerate(b_lines):
            f.append(text(bx + 8, by + 44 + j * 18, bline, 9.5, INK if j == 0 else MUTED, "start"))

    render(os.path.join(IMG, "message-envelope-layout.svg"), W, H, *f)


def fig_transaction_lifecycle():
    W, H = 960, 480
    f = []
    f.append(text(W / 2, 28, "Життєвий цикл транзакції: узгодження запиту, відповіді та обробка збоїв", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Зв'язування за Transaction ID, обробка помилок виконання та захист від дублікатів", 12, MUTED, "middle", italic=True))

    col1_x = 180
    col2_x = 780
    y_top = 80
    y_bottom = 450

    f.append(rect(col1_x - 80, y_top, 160, 36, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(col1_x, y_top + 23, "Клієнт (Ініціатор)", 13, NEG, "middle", bold=True))
    f.append(line(col1_x, y_top + 36, col1_x, y_bottom, color=NEG, sw=1.5, dash="4,4"))

    f.append(rect(col2_x - 80, y_top, 160, 36, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(col2_x, y_top + 23, "Сервер (Виконавець)", 13, FIELD, "middle", bold=True))
    f.append(line(col2_x, y_top + 36, col2_x, y_bottom, color=FIELD, sw=1.5, dash="4,4"))

    y1 = 145
    f.append(text(col1_x - 90, y1, "Сценарій 1: Успіх", 11, FIELD, "start", bold=True))
    f.append(arrow(col1_x, y1 + 10, col2_x, y1 + 25, color=LINE, sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y1 + 5, "CMD_MOTOR_SET_SPEED (SeqID=12, ACK_REQ, Speed=1500)", 11, INK, "middle", bold=True))

    f.append(rect(col2_x - 6, y1 + 25, 12, 35, fill="#d4efdf", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(col2_x + 15, y1 + 45, "Виконання (PWM update)", 10, MUTED, "start", italic=True))

    f.append(arrow(col2_x, y1 + 60, col1_x, y1 + 75, color=FIELD, sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y1 + 55, "RSP (SeqID=12, IS_RESP, Status=OK, CurrentRPM=1498)", 11, FIELD, "middle", bold=True))

    y2 = 245
    f.append(text(col1_x - 90, y2, "Сценарій 2: Відмова", 11, POS, "start", bold=True))
    f.append(arrow(col1_x, y2 + 10, col2_x, y2 + 25, color=LINE, sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y2 + 5, "CMD_WRITE_CALIBRATION (SeqID=13, ACK_REQ, Offset=5000)", 11, INK, "middle", bold=True))

    f.append(rect(col2_x - 6, y2 + 25, 12, 30, fill="#fadbd8", stroke=POS, sw=1.2, rx=2))
    f.append(text(col2_x + 15, y2 + 42, "Перевірка діапазону: FAIL", 10, POS, "start", italic=True))

    f.append(arrow(col2_x, y2 + 55, col1_x, y2 + 70, color=POS, sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y2 + 50, "RSP_ERR (SeqID=13, IS_RESP | IS_ERR, ErrorCode=ERR_INVALID_PARAM)", 11, POS, "middle", bold=True))

    y3 = 345
    f.append(text(col1_x - 90, y3, "Сценарій 3: Ретрай", 11, "#d35400", "start", bold=True))
    f.append(arrow(col1_x, y3 + 10, col1_x + 280, y3 + 22, color=LINE, sw=1.6))
    f.append(text(col1_x + 140, y3 + 4, "CMD_PING (SeqID=14)", 10.5, INK, "middle"))
    f.append(text(col1_x + 300, y3 + 26, "✕ ВТРАТА КАДРУ", 11, POS, "start", bold=True))

    f.append(rect(col1_x - 6, y3 + 10, 12, 45, fill="#fff3cd", stroke="#e67e22", sw=1.2, rx=2))
    f.append(text(col1_x - 12, y3 + 35, "Таймаут RTT вичерпано", 10, "#d35400", "end", italic=True))

    f.append(arrow(col1_x, y3 + 55, col2_x, y3 + 70, color="#d35400", sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y3 + 50, "CMD_PING (SeqID=14, RETRY) — той самий SeqID запобігає дублюванню дій", 10.5, "#d35400", "middle", bold=True))

    f.append(arrow(col2_x, y3 + 80, col1_x, y3 + 95, color=FIELD, sw=1.6))
    f.append(text((col1_x + col2_x) / 2, y3 + 75, "RSP (SeqID=14, IS_RESP, Status=OK)", 11, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "transaction-lifecycle.svg"), W, H, *f)


def fig_dispatcher_dispatch_flow():
    W, H = 960, 440
    f = []
    f.append(text(W / 2, 28, "Конвеєр обробки повідомлень у диспетчері (Table-Driven Dispatcher)", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Послідовні стадії валідації, маршрутизації транзакції та безпечного виконання без malloc", 12, MUTED, "middle", italic=True))

    stages = [
        ("1. Прийом кадру", "COBS декодування\nта валідація CRC-16", "#eaf0fd", NEG),
        ("2. Фільтр адреси", "Перевірка DST_ADDR:\nNode ID чи Broadcast", "#eaf0fd", NEG),
        ("3. Селектор типу", "Перевірка IS_RESP:\nвідповідь чи запит?", "#fff3cd", "#d35400"),
        ("4. Пошук у таблиці", "O(1) або бінарний\nпошук за MSG_TYPE", "#f3e8fd", "#7d3c98"),
        ("5. Валідація payload", "Перевірка розміру\nlen >= min_expected_len", "#fdecea", POS),
        ("6. Виклик обробника", "handler(payload, resp)\nта генерація статусу", "#eafaf1", FIELD)
    ]

    start_x = 24
    box_w = 138
    box_h = 75
    gap = 20
    y_pos = 90

    for i, (title_str, desc_str, fill_c, strk_c) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        f.append(rect(x, y_pos, box_w, box_h, fill=fill_c, stroke=strk_c, sw=1.6, rx=6))
        f.append(text(x + box_w / 2, y_pos + 22, title_str, 11, strk_c, "middle", bold=True))

        desc_lines = desc_str.split("\n")
        f.append(text(x + box_w / 2, y_pos + 42, desc_lines[0], 9.5, INK, "middle"))
        f.append(text(x + box_w / 2, y_pos + 57, desc_lines[1], 9.5, MUTED, "middle"))

        if i < len(stages) - 1:
            f.append(arrow(x + box_w, y_pos + box_h / 2, x + box_w + gap, y_pos + box_h / 2, color=LINE, sw=1.5))

    y_branch = 220
    f.append(rect(start_x, y_branch, 912, 190, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(start_x + 18, y_branch + 25, "Маршрутизація відмов та автоматична генерація негативної відповіді (Error Response):", 12.5, INK, "start", bold=True))

    error_branches = [
        ("1. Помилка CRC / Довжини", [
            "Кадр мовчки відкидається.",
            "Запобігання реакції на",
            "спотворені адреси й шум."
        ], POS),
        ("2. Чужа адреса вузла", [
            "Пакет ігнорується, якщо",
            "він не адресований вузлу",
            "і не є Broadcast (0x00)."
        ], MUTED),
        ("3. Невідомий MSG_TYPE", [
            "Генерується відповідь",
            "IS_RESP | IS_ERR із кодом",
            "ERR_NOT_SUPPORTED."
        ], "#d35400"),
        ("4. Недостатній Payload", [
            "Відхилення запиту з кодом",
            "ERR_INVALID_PARAM при",
            "меншій довжині за очікувану."
        ], POS),
        ("5. Помилка периферії", [
            "Обробник повертає",
            "ERR_BUSY або ERR_STATE,",
            "диспетчер шле відповідь."
        ], FIELD)
    ]

    eb_y = y_branch + 42
    eb_w = 172
    eb_gap = 8
    for i, (eb_title, eb_lines, eb_col) in enumerate(error_branches):
        bx = start_x + 18 + i * (eb_w + eb_gap)
        f.append(rect(bx, eb_y, eb_w, 125, fill="#ffffff", stroke=eb_col, sw=1.4, rx=6))
        f.append(rect(bx, eb_y, eb_w, 28, fill=eb_col, stroke=eb_col, sw=0, rx=4))
        f.append(text(bx + eb_w / 2, eb_y + 18, eb_title, 9.5, BG, "middle", bold=True))

        for j, eline in enumerate(eb_lines):
            f.append(text(bx + 8, eb_y + 48 + j * 18, eline, 9.2, INK if j == 0 else MUTED, "start"))

    render(os.path.join(IMG, "dispatcher-dispatch-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_roles_and_topologies()
    fig_message_envelope_layout()
    fig_transaction_lifecycle()
    fig_dispatcher_dispatch_flow()
    print("Figures generated successfully.")
