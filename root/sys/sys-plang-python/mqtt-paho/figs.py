# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми 'Приймач MQTT на сервері' (paho-mqtt v2)."""

import os
import sys

# Додаємо scripts/ до шляхів імпорту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_paho_network_loops():
    """Архітектура мережевих циклів paho-mqtt: loop_forever, loop_start, loop_read/write."""
    w, h = 960, 520
    frags = []

    frags.append(text(w / 2, 28, "Моделі мережевих циклів у paho-mqtt", size=15, bold=True))

    cards = [
        {
            "title": "1. loop_forever()",
            "sub": "Блокувальний однопотоковий цикл",
            "color": NEG,
            "fill": "#eff6ff",
            "blocks": [
                ("Виклик у головному потоці", "Повністю блокує виконання", "#ffffff", INK),
                ("Внутрішній select / poll", "Обробляє ввід, вивід та таймери", "#ffffff", INK),
                ("Диспетчеризація колбеків", "on_message викликається в цьому ж потоці", "#ffffff", NEG),
                ("Вбудований reconnect", "Автоматично відновлює з'єднання", "#d1fae5", FIELD),
            ],
            "note": "Ідеально: виділений воркер-процес"
        },
        {
            "title": "2. loop_start() / loop_stop()",
            "sub": "Фоновий потік демона",
            "color": FIELD,
            "fill": "#f0fdf4",
            "blocks": [
                ("Створення threading.Thread", "Запускає фоновий потік-демон", "#ffffff", INK),
                ("Неблокувальний для Main", "Головний потік вільний для логіки", "#ffffff", FIELD),
                ("Міжпотокова взаємодія", "Колбеки виконуються у фоновому потоці", "#ffffff", POS),
                ("Потрібна черга queue.Queue", "Для безпечної передачі даних", "#fef3c7", "#b45309"),
            ],
            "note": "Ідеально: сервіси з власним життєвим циклом"
        },
        {
            "title": "3. loop_read() / loop_write()",
            "sub": "Ручна інтеграція у селектор",
            "color": "#b45309",
            "fill": "#fef9e7",
            "blocks": [
                ("Прямий доступ до сокета", "client.socket() у poll / epoll", "#ffffff", INK),
                ("loop_read() / loop_write()", "Викликаються за подіями дескриптора", "#ffffff", "#b45309"),
                ("Обов'язковий loop_misc()", "Керує пінгами PINGREQ та таймаутами", "#fee2e2", POS),
                ("Повний контроль над I/O", "Нуль зайвих системних потоків", "#ffffff", INK),
            ],
            "note": "Ідеально: власні низькорівневі реактори"
        }
    ]

    card_w = 280
    card_h = 420
    gap = 35
    start_x = 35
    card_y = 60

    for i, c in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        cy = card_y

        frags.append(rect(cx, cy, card_w, card_h, fill=c["fill"], stroke=c["color"], sw=1.6, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, c["title"], size=12, bold=True, color=c["color"]))
        frags.append(line(cx + 10, cy + 34, cx + card_w - 10, cy + 34, color=c["color"], sw=1.0))
        frags.append(text(cx + card_w / 2, cy + 50, c["sub"], size=9, bold=True, color=MUTED))

        for b_idx, (b_title, b_desc, b_fill, b_col) in enumerate(c["blocks"]):
            by = cy + 70 + b_idx * 72
            frags.append(rect(cx + 10, by, card_w - 20, 62, fill=b_fill, stroke=LINE, sw=1.0, rx=5))
            frags.append(text(cx + card_w / 2, by + 20, b_title, size=10, bold=True, color=b_col))
            frags.append(text(cx + card_w / 2, by + 42, b_desc, size=9, color=INK))

        frags.append(rect(cx + 10, cy + card_h - 44, card_w - 20, 32, fill="#ffffff", stroke=c["color"], sw=1.2, rx=4))
        frags.append(text(cx + card_w / 2, cy + card_h - 24, c["note"], size=9, bold=True, color=c["color"]))

    frags.append(text(w / 2, 498, "Вибір мережевого циклу визначає розподіл потоків та механіку передачі отриманих повідомлень у бекенд", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "paho-network-loops.svg")
    render(path, w, h, *frags)


def fig_mqtt_v2_callbacks_flow():
    """Потік подій та зворотних викликів у CallbackAPIVersion.VERSION2."""
    w, h = 960, 500
    frags = []

    frags.append(text(w / 2, 28, "Архітектура подій і зворотних викликів у Paho v2 (VERSION2)", size=15, bold=True))

    # Ліва частина: Мережевий брокер і вхідний сокет
    col1_x, col1_y, col1_w, col1_h = 30, 60, 220, 400
    frags.append(rect(col1_x, col1_y, col1_w, col1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(col1_x + col1_w / 2, col1_y + 24, "Мережа та брокер MQTT", size=12, bold=True, color=NEG))
    frags.append(line(col1_x + 10, col1_y + 36, col1_x + col1_w - 10, col1_y + 36, color=NEG, sw=1.0))

    net_steps = [
        ("TCP / TLS Socket", "Канал зв'язку з брокером", "#ffffff", INK),
        ("Вхідні байти MQTT", "CONNACK, PUBLISH, SUBACK, DISCONNECT", "#ffffff", INK),
        ("Черга виходу", "Вихідний буфер PUBACK, PINGREQ", "#ffffff", INK),
        ("Обробка розривів", "Keep-Alive таймаути та скидання TCP", "#fee2e2", POS),
    ]
    for idx, (n_t, n_d, n_f, n_c) in enumerate(net_steps):
        ny = col1_y + 55 + idx * 82
        frags.append(rect(col1_x + 10, ny, col1_w - 20, 68, fill=n_f, stroke=LINE, sw=1.0, rx=6))
        frags.append(text(col1_x + col1_w / 2, ny + 22, n_t, size=10, bold=True, color=n_c))
        frags.append(text(col1_x + col1_w / 2, ny + 46, n_d, size=9, color=MUTED))

    # Центральна частина: Клієнт Paho та парсер
    col2_x, col2_y, col2_w, col2_h = 290, 60, 280, 400
    frags.append(rect(col2_x, col2_y, col2_w, col2_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(col2_x + col2_w / 2, col2_y + 24, "Paho Client v2 Рушій", size=12, bold=True, color=NEG))
    frags.append(line(col2_x + 10, col2_y + 36, col2_x + col2_w - 10, col2_y + 36, color=NEG, sw=1.0))

    core_items = [
        ("Парсинг фреймів MQTT 3.1.1 / 5.0", "Розбір заголовків, довжини та властивостей", "#ffffff", INK),
        ("ReasonCode & Properties", "Типізовані об'єкти статусів v2 API", "#d1fae5", FIELD),
        ("userdata Контекст", "Безпечна передача стану без глобальних змінних", "#ffffff", INK),
        ("Диспетчер подій", "Формування аргументів та виклик колбеків", "#fef3c7", "#b45309"),
    ]
    for idx, (c_t, c_d, c_f, c_c) in enumerate(core_items):
        cy = col2_y + 55 + idx * 82
        frags.append(rect(col2_x + 10, cy, col2_w - 20, 68, fill=c_f, stroke=LINE, sw=1.0, rx=6))
        frags.append(text(col2_x + col2_w / 2, cy + 22, c_t, size=10, bold=True, color=c_c))
        frags.append(text(col2_x + col2_w / 2, cy + 46, c_d, size=9, color=MUTED))

    # Права частина: Колбеки користувача
    col3_x, col3_y, col3_w, col3_h = 610, 60, 320, 400
    frags.append(rect(col3_x, col3_y, col3_w, col3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col3_x + col3_w / 2, col3_y + 24, "Колбеки CallbackAPIVersion.VERSION2", size=11, bold=True, color=FIELD))
    frags.append(line(col3_x + 10, col3_y + 36, col3_x + col3_w - 10, col3_y + 36, color=FIELD, sw=1.0))

    callbacks = [
        ("on_connect", "(client, userdata, flags, reason_code, properties)", "#ffffff", NEG),
        ("on_message", "(client, userdata, message: MQTTMessage)", "#ffffff", FIELD),
        ("on_disconnect", "(client, userdata, flags, reason_code, properties)", "#ffffff", POS),
        ("on_publish / on_subscribe", "(client, userdata, mid, reason_codes, properties)", "#ffffff", INK),
    ]
    for idx, (cb_n, cb_s, cb_f, cb_c) in enumerate(callbacks):
        cby = col3_y + 55 + idx * 82
        frags.append(rect(col3_x + 10, cby, col3_w - 20, 68, fill=cb_f, stroke=LINE, sw=1.0, rx=6))
        frags.append(text(col3_x + col3_w / 2, cby + 22, cb_n, size=11, bold=True, color=cb_c))
        frags.append(text(col3_x + col3_w / 2, cby + 46, cb_s, size=9, color=INK))

    # Стрілки
    frags.append(arrow(col1_x + col1_w, col1_y + 160, col2_x, col2_y + 160, color=NEG, sw=1.8))
    frags.append(arrow(col2_x + col2_w, col2_y + 160, col3_x, col3_y + 160, color=FIELD, sw=1.8))

    frags.append(text(w / 2, 480, "У VERSION2 усі колбеки отримують типізований reason_code та властивості MQTT 5.0 замість сирого числа rc", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "mqtt-v2-callbacks-flow.svg")
    render(path, w, h, *frags)


def fig_asyncio_mqtt_bridge():
    """Інтеграція Paho MQTT та циклу asyncio через асинхронні черги."""
    w, h = 960, 480
    frags = []

    frags.append(text(w / 2, 28, "Архітектура асинхронного приймача: aiomqtt та asyncio.Queue", size=15, bold=True))

    # Блок 1: Мережевий потік / сокет
    b1_x, b1_y, b1_w, b1_h = 35, 60, 240, 380
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 24, "1. Мережевий транспорт", size=12, bold=True, color=NEG))
    frags.append(line(b1_x + 10, b1_y + 36, b1_x + b1_w - 10, b1_y + 36, color=NEG, sw=1.0))

    t_items = [
        "Брокер MQTT (EMQX / Mosquitto)",
        "TLS порт 8883 / TCP 1883",
        "Paho / aiomqtt клієнт",
        "loop.add_reader(sock.fileno())",
        "Неблокувальне читання фреймів",
        "Автоматичне відновлення зв'язку"
    ]
    for idx, t_line in enumerate(t_items):
        is_h = (idx == 0 or idx == 2)
        frags.append(text(b1_x + 14, b1_y + 65 + idx * 48, t_line, size=9, bold=is_h, color=NEG if is_h else INK, anchor="start"))

    # Блок 2: Асинхронний міст
    b2_x, b2_y, b2_w, b2_h = 320, 60, 290, 380
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fef9e7", stroke="#b45309", sw=1.8, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 24, "2. Асинхронний буфер і міст", size=12, bold=True, color="#b45309"))
    frags.append(line(b2_x + 10, b2_y + 36, b2_x + b2_w - 10, b2_y + 36, color="#b45309", sw=1.0))

    bridge_boxes = [
        ("async with Client()", "Контекстний менеджер з'єднання", "#ffffff", INK),
        ("async for msg in messages", "Асинхронний генератор подій", "#ffffff", "#b45309"),
        ("asyncio.Queue(maxsize=10000)", "Буфер захисту від протитиску (backpressure)", "#fee2e2", POS),
        ("Розпаралелювання задач", "TaskGroup / воркери пулу", "#ffffff", INK),
    ]
    for idx, (br_t, br_d, br_f, br_c) in enumerate(bridge_boxes):
        by = b2_y + 50 + idx * 76
        frags.append(rect(b2_x + 10, by, b2_w - 20, 64, fill=br_f, stroke=LINE, sw=1.0, rx=6))
        frags.append(text(b2_x + b2_w / 2, by + 22, br_t, size=10, bold=True, color=br_c))
        frags.append(text(b2_x + b2_w / 2, by + 44, br_d, size=9, color=MUTED))

    # Блок 3: Споживачі бекенду
    b3_x, b3_y, b3_w, b3_h = 650, 60, 275, 380
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(b3_x + b3_w / 2, b3_y + 24, "3. Обробка та нормалізація", size=12, bold=True, color=FIELD))
    frags.append(line(b3_x + 10, b3_y + 36, b3_x + b3_w - 10, b3_y + 36, color=FIELD, sw=1.0))

    worker_items = [
        ("Парсинг та валідація", "Pydantic схеми / JSON / CBOR", "#ffffff", INK),
        ("Нормалізація міток часу", "ISO 8601 UTC конвертація", "#ffffff", INK),
        ("Фільтрація аномалій", "Перевірка діапазонів значень", "#ffffff", INK),
        ("Запис у сховище", "asyncpg / ClickHouse / Redis Streams", "#d1fae5", FIELD),
    ]
    for idx, (w_t, w_d, w_f, w_c) in enumerate(worker_items):
        wy = b3_y + 50 + idx * 76
        frags.append(rect(b3_x + 10, wy, b3_w - 20, 64, fill=w_f, stroke=LINE, sw=1.0, rx=6))
        frags.append(text(b3_x + b3_w / 2, wy + 22, w_t, size=10, bold=True, color=w_c))
        frags.append(text(b3_x + b3_w / 2, wy + 44, w_d, size=9, color=MUTED))

    # Стрілки
    frags.append(arrow(b1_x + b1_w, b1_y + 180, b2_x, b2_y + 180, color=NEG, sw=1.8))
    frags.append(arrow(b2_x + b2_w, b2_y + 180, b3_x, b3_y + 180, color=FIELD, sw=1.8))

    frags.append(text(w / 2, 460, "Асинхронний конвеєр відокремлює мережеве отримання MQTT-пакетів від важкої обробки та запису в базу даних", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "asyncio-mqtt-bridge.svg")
    render(path, w, h, *frags)


if __name__ == "__main__":
    fig_paho_network_loops()
    fig_mqtt_v2_callbacks_flow()
    fig_asyncio_mqtt_bridge()
    print("All figures generated successfully.")
