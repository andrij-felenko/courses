# -*- coding: utf-8 -*-
"""Фігури до теми «Стрімінг результату: long-poll, SSE, WebSocket».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"
PURPLE = "#7b1fa2"


# ── 1. Порівняння чотирьох транспортів ────────────────────────────────────────
def fig_transports_comparison():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Порівняння веб-транспортів: від опитування до постійного сокета", size=16, bold=True)]

    panels = [
        dict(y=54, name="КОРОТКЕ ОПИТУВАННЯ (Short Polling)", col=POS,
             desc="Періодичні запити кожні N мс. Більшість відповідей порожні; затримка = інтервалу; високий оверхед заголовків.",
             kind="polling"),
        dict(y=180, name="ДОВГЕ ОПИТУВАННЯ (Long Polling)", col=AMBER,
             desc="Сервер тримає з'єднання до появи події або таймауту. Затримка низька, але на кожну подію — нове TCP/HTTP з'єднання.",
             kind="longpoll"),
        dict(y=306, name="SERVER-SENT EVENTS (SSE)", col=NEG,
             desc="Одне відкрите HTTP-з'єднання від сервера до клієнта. Текстовий потік, автоматичне перепідключення, Last-Event-ID.",
             kind="sse"),
        dict(y=432, name="WEBSOCKET (RFC 6455)", col=FIELD,
             desc="Повнодуплексний двосторонній бінарний протокол поверх одного TCP-сокета. Оверхед кадру від 2 байтів.",
             kind="ws"),
    ]

    PW, PH = 960, 114
    px = 20
    for p in panels:
        y = p["y"]
        f.append(rect(px, y, PW, PH, fill=PANEL, stroke=p["col"], sw=1.8, rx=8))
        f.append(text(px + 16, y + 22, p["name"], size=12.5, color=p["col"], anchor="start", bold=True))
        f.append(text(px + 16, y + 42, p["desc"], size=11, color=MUTED, anchor="start"))

        row = y + 78
        # Клієнт
        f.append(fitbox(px + 20, row - 22, 100, 44, "клієнт", size=11.5))
        # Сервер
        f.append(fitbox(px + 830, row - 22, 100, 44, "сервер", size=11.5, stroke=LINE, fill=FILL))

        # Діаграма ліній між клієнтом і сервером
        lx1 = px + 130
        lx2 = px + 820

        if p["kind"] == "polling":
            # 3 швидких стрілки запит-відповідь
            step = (lx2 - lx1) / 3
            for i in range(3):
                cx1 = lx1 + i * step + 10
                cx2 = cx1 + step - 25
                f.append(arrow(cx1, row - 8, cx2, row - 8, color=POS, sw=1.3))
                f.append(arrow(cx2, row + 8, cx1, row + 8, color=GRAY, sw=1.3))
                lbl = "GET (пусто)" if i < 2 else "GET (є дані!)"
                col = MUTED if i < 2 else POS
                f.append(text((cx1 + cx2)/2, row - 12, lbl, size=10, color=col))

        elif p["kind"] == "longpoll":
            # 1 довгий запит, висить, потім відповідь
            mid_x = (lx1 + lx2) / 2
            f.append(arrow(lx1 + 20, row - 8, mid_x - 30, row - 8, color=AMBER, sw=1.4))
            f.append(line(mid_x - 30, row - 8, lx2 - 80, row - 8, color=AMBER, sw=1.4, dash="3 3"))
            f.append(text(mid_x, row - 12, "GET (сервер тримає відкритим до появи події)", size=10, color=AMBER))
            f.append(arrow(lx2 - 80, row + 8, lx1 + 20, row + 8, color=FIELD, sw=1.4))
            f.append(text(mid_x, row + 20, "200 OK + дані -> з'єднання закривається -> новий GET", size=10, color=FIELD))

        elif p["kind"] == "sse":
            # 1 GET, далі відкритий потік подій вниз
            f.append(arrow(lx1 + 20, row - 8, lx2 - 20, row - 8, color=LINE, sw=1.2))
            f.append(text(lx1 + 100, row - 12, "GET /events (text/event-stream)", size=10, color=INK))
            # Потік подій праворуч наліво (від сервера до клієнта)
            ev_x = [lx2 - 120, lx2 - 320, lx2 - 520]
            for i, ex in enumerate(ev_x):
                f.append(arrow(ex, row + 10, ex - 120, row + 10, color=NEG, sw=1.5))
                f.append(text(ex - 60, row + 22, f"event #{i+1}", size=10, color=NEG, bold=True))

        elif p["kind"] == "ws":
            # Handshake Upgrade, далі двостороння стрілка
            mid_x = (lx1 + lx2) / 2
            f.append(text(mid_x, row - 14, "101 Switching Protocols (Upgrade: websocket)", size=10, color=FIELD, bold=True))
            # Двостороння товста лінія з кадрами в обидва боки
            f.append(arrow(lx1 + 30, row + 4, lx2 - 30, row + 4, color=FIELD, sw=2))
            f.append(arrow(lx2 - 30, row + 16, lx1 + 30, row + 16, color=PURPLE, sw=2))
            f.append(text(mid_x, row + 26, "◄── Двосторонній обмін бінарними та текстовими кадрами ──►", size=10, color=INK))

    render(os.path.join(IMG, "transports-comparison.svg"), W, H, *f)


# ── 2. Анатомія кадру WebSocket (RFC 6455) ───────────────────────────────────
def fig_websocket_frame():
    W, H = 960, 420
    f = [text(W / 2, 28, "Структура заголовка кадру WebSocket (RFC 6455)", size=16, bold=True)]

    # Бітова лінійка на 32 біти (4 байти)
    bx = 50
    by = 60
    bw = 860
    bit_w = bw / 32

    # Заголовок бітів 0..31
    f.append(rect(bx, by, bw, 24, fill="#e8edf3", stroke=LINE, sw=1.2))
    for i in range(32):
        f.append(line(bx + i * bit_w, by, bx + i * bit_w, by + 24, color=GRAY, sw=0.8))
        if i % 4 == 0 or i == 31:
            f.append(text(bx + i * bit_w + bit_w / 2, by + 16, str(i), size=9.5, color=MUTED))

    # Рядок 1: Байти 0 і 1 (Біти 0..15) + Байти 2 і 3
    r1_y = by + 34
    r1_h = 60

    # FIN (1 біт)
    f.append(rect(bx, r1_y, bit_w, r1_h, fill="#ffebee", stroke=POS, sw=1.2))
    f.append(text(bx + bit_w/2, r1_y + 24, "FIN", size=10, bold=True, color=POS))
    f.append(text(bx + bit_w/2, r1_y + 44, "1b", size=9, color=MUTED))

    # RSV 1..3 (3 біти)
    f.append(rect(bx + bit_w, r1_y, bit_w * 3, r1_h, fill="#f3e5f5", stroke=PURPLE, sw=1.2))
    f.append(text(bx + bit_w * 2.5, r1_y + 24, "RSV 1-3", size=10, bold=True, color=PURPLE))
    f.append(text(bx + bit_w * 2.5, r1_y + 44, "3b (розширення)", size=9, color=MUTED))

    # Opcode (4 біти)
    f.append(rect(bx + bit_w * 4, r1_y, bit_w * 4, r1_h, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    f.append(text(bx + bit_w * 6, r1_y + 24, "Opcode (код операції)", size=10.5, bold=True, color=FIELD))
    f.append(text(bx + bit_w * 6, r1_y + 44, "4b (0x1 Text, 0x2 Bin, 0x8 Close)", size=9.5, color=MUTED))

    # MASK (1 біт)
    f.append(rect(bx + bit_w * 8, r1_y, bit_w, r1_h, fill="#fff3e0", stroke=AMBER, sw=1.2))
    f.append(text(bx + bit_w * 8.5, r1_y + 24, "M", size=10, bold=True, color=AMBER))
    f.append(text(bx + bit_w * 8.5, r1_y + 44, "1b", size=9, color=MUTED))

    # Payload Len (7 бітів)
    f.append(rect(bx + bit_w * 9, r1_y, bit_w * 7, r1_h, fill="#e3f2fd", stroke=NEG, sw=1.2))
    f.append(text(bx + bit_w * 12.5, r1_y + 24, "Payload Length (довжина)", size=10.5, bold=True, color=NEG))
    f.append(text(bx + bit_w * 12.5, r1_y + 44, "7b: 0-125 або коди 126 / 127", size=9, color=MUTED))

    # Extended Payload Length (16 / 64 бітів)
    f.append(rect(bx + bit_w * 16, r1_y, bit_w * 16, r1_h, fill="#f5f5f5", stroke=LINE, sw=1.2))
    f.append(text(bx + bit_w * 24, r1_y + 24, "Extended Payload Length (якщо Len=126 або 127)", size=11, bold=True, color=INK))
    f.append(text(bx + bit_w * 24, r1_y + 44, "16 бітів (до 64 КБ) або 64 біти (до 16 ЕБ)", size=9.5, color=MUTED))

    # Рядок 2: Маскувальний ключ (32 біти)
    r2_y = r1_y + r1_h + 12
    r2_h = 50
    f.append(rect(bx, r2_y, bw, r2_h, fill="#fff8e1", stroke=AMBER, sw=1.4))
    f.append(text(bx + bw / 2, r2_y + 22, "Masking-Key (4 байти / 32 біти) — обов'язковий від клієнта до сервера", size=12, bold=True, color=AMBER))
    f.append(text(bx + bw / 2, r2_y + 38, "Випадковий ключ для XOR-маскування; запобігає отруєнню кешів проксі-серверів", size=10, color=MUTED))

    # Рядок 3: Корисне навантаження (Payload)
    r3_y = r2_y + r2_h + 12
    r3_h = 56
    f.append(rect(bx, r3_y, bw, r3_h, fill="#e8f5e9", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(bx + bw / 2, r3_y + 24, "Корисне навантаження (Payload Data: масковане або чисте)", size=12, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, r3_y + 42, "Текстові дані UTF-8 (Opcode 0x1) або сирі байти застосунку (Opcode 0x2)", size=10.5, color=MUTED))

    # Нижня пояснювальна картка
    bot_y = r3_y + r3_h + 16
    f.append(rect(bx, bot_y, bw, 70, fill=PANEL, stroke=GRAY, sw=1, rx=6))
    f.append(text(bx + 16, bot_y + 22, "Ключові властивості кадру:", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(bx + 16, bot_y + 40, "• Мінімальний розмір заголовка — лише 2 байти (сервер -> клієнт, довжина < 126 байтів).", size=10.5, color=MUTED, anchor="start"))
    f.append(text(bx + 16, bot_y + 58, "• Клієнт зобов'язаний маскувати кадри (MASK=1); сервер зобов'язаний відхиляти немасковані кадри клієнта з кодом 1002.", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "websocket-frame-layout.svg"), W, H, *f)


# ── 3. Життєвий цикл SSE та перепідключення ──────────────────────────────────
def fig_sse_reconnection():
    W, H = 940, 480
    f = [text(W / 2, 28, "Автоматичне відновлення потоку SSE через Last-Event-ID", size=16, bold=True)]

    PW, PH = 900, 420
    px, py = 20, 48
    f.append(rect(px, py, PW, PH, fill=PANEL, stroke=LINE, sw=1.2, rx=8))

    # Колонки Клієнт і Сервер
    col_c = px + 120
    col_s = px + 780
    f.append(fitbox(col_c - 60, py + 16, 120, 40, "Клієнт (Браузер)", size=12, bold=True))
    f.append(fitbox(col_s - 60, py + 16, 120, 40, "SSE-Сервер", size=12, bold=True, stroke=LINE, fill=FILL))

    # Вертикальні лінії життя
    f.append(line(col_c, py + 60, col_c, py + 400, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col_s, py + 60, col_s, py + 400, color=GRAY, sw=1.2, dash="4 4"))

    # Фаза 1: Перше підключення
    y1 = py + 80
    f.append(arrow(col_c, y1, col_s, y1 + 16, color=INK, sw=1.4))
    f.append(text((col_c + col_s) / 2, y1 + 4, "GET /events HTTP/1.1 (Accept: text/event-stream)", size=10.5, color=INK))

    y2 = y1 + 36
    f.append(arrow(col_s, y2, col_c, y2 + 16, color=FIELD, sw=1.4))
    f.append(text((col_c + col_s) / 2, y2 + 4, "HTTP/1.1 200 OK (Content-Type: text/event-stream, Cache-Control: no-cache)", size=10, color=FIELD))

    # Фаза 2: Події з ідентифікаторами
    y3 = y2 + 36
    f.append(arrow(col_s, y3, col_c, y3 + 14, color=NEG, sw=1.4))
    f.append(text((col_c + col_s) / 2, y3 + 4, "id: 101 \\n event: trade \\n data: {\"price\": 42.5} \\n\\n", size=10, color=NEG))

    y4 = y3 + 30
    f.append(arrow(col_s, y4, col_c, y4 + 14, color=NEG, sw=1.4))
    f.append(text((col_c + col_s) / 2, y4 + 4, "id: 102 \\n event: trade \\n data: {\"price\": 42.8} \\n\\n", size=10, color=NEG))

    # Фаза 3: Обрив з'єднання
    y_cut = y4 + 36
    f.append(rect(px + 180, y_cut - 12, 540, 24, fill="#ffebee", stroke=POS, sw=1.2, rx=4))
    f.append(text(W / 2, y_cut + 4, "⚡ ОБРИВ МЕРЕЖІ (таймаут проксі / зміна Wi-Fi на LTE) ⚡", size=10.5, color=POS, bold=True))

    # Фаза 4: Очікування retry
    y_retry = y_cut + 34
    f.append(text(col_c - 10, y_retry + 8, "пауза retry: 3000 мс", size=10, color=MUTED, anchor="end", italic=True))
    f.append(rect(col_c - 4, y_retry - 4, 8, 24, fill=AMBER, stroke=AMBER))

    # Фаза 5: Автоматичне перепідключення з Last-Event-ID
    y5 = y_retry + 36
    f.append(arrow(col_c, y5, col_s, y5 + 16, color=AMBER, sw=1.6))
    f.append(text((col_c + col_s) / 2, y5 + 4, "GET /events (Last-Event-ID: 102) ──► клієнт сам пам'ятає останній id!", size=10.5, color=AMBER, bold=True))

    # Фаза 6: Сервер відновлює потік без втрат
    y6 = y5 + 38
    f.append(arrow(col_s, y6, col_c, y6 + 14, color=FIELD, sw=1.5))
    f.append(text((col_c + col_s) / 2, y6 + 4, "id: 103 \\n event: trade \\n data: {\"price\": 43.1} \\n\\n (досилка з буфера)", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "sse-reconnection-flow.svg"), W, H, *f)


# ── 4. Горизонтальне масштабування пуш-серверів ──────────────────────────────
def fig_horizontal_push_broker():
    W, H = 980, 520
    f = [text(W / 2, 28, "Горизонтальне масштабування: пуш-вузли та шина подій (Pub/Sub)", size=16, bold=True)]

    # Верхній ярус: Клієнти (3 групи)
    top_y = 60
    f.append(fitbox(60, top_y, 160, 48, "Клієнти A (1..10k)", size=11, bold=True))
    f.append(fitbox(410, top_y, 160, 48, "Клієнт #42 (цільовий)", size=11, bold=True, stroke=POS, fill="#ffebee"))
    f.append(fitbox(760, top_y, 160, 48, "Клієнти C (20k..30k)", size=11, bold=True))

    # Середній ярус: Балансувальник і Вузли
    lb_y = top_y + 74
    f.append(rect(40, lb_y, 900, 36, fill="#f0f4f8", stroke=GRAY, sw=1.2, rx=6))
    f.append(text(W / 2, lb_y + 23, "Балансувальник навантаження (L4 TCP Proxy / L7 Reverse Proxy з підтримкою Upgrade)", size=11.5, color=INK))

    # Стрілки від клієнтів крізь LB
    f.append(arrow(140, top_y + 48, 140, lb_y, color=GRAY, sw=1.2))
    f.append(arrow(490, top_y + 48, 490, lb_y, color=POS, sw=1.4))
    f.append(arrow(840, top_y + 48, 840, lb_y, color=GRAY, sw=1.2))

    # Вузли застосунку (Node 1, Node 2, Node 3)
    node_y = lb_y + 54
    f.append(fitbox(60, node_y, 220, 68, "Пуш-сервер #1\n(тримає 10k сокетів)", size=11.5, stroke=LINE, fill=FILL))
    f.append(fitbox(380, node_y, 220, 68, "Пуш-сервер #2\n(тримає сокет Клієнта #42)", size=11.5, stroke=POS, fill="#fff5f5"))
    f.append(fitbox(700, node_y, 220, 68, "Пуш-сервер #3\n(тримає 10k сокетів)", size=11.5, stroke=LINE, fill=FILL))

    # Стрілки від LB до конкретних вузлів
    f.append(arrow(140, lb_y + 36, 170, node_y, color=GRAY, sw=1.2))
    f.append(arrow(490, lb_y + 36, 490, node_y, color=POS, sw=1.4))
    f.append(arrow(840, lb_y + 36, 810, node_y, color=GRAY, sw=1.2))

    # Нижній ярус: Шина повідомлень (Pub/Sub)
    bus_y = node_y + 110
    f.append(rect(40, bus_y, 900, 60, fill="#e8f5e9", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(W / 2, bus_y + 24, "Шина повідомлень / Брокер (Redis Pub/Sub, NATS, Kafka)", size=13, bold=True, color=FIELD))
    f.append(text(W / 2, bus_y + 44, "Канал fanout: вузли підписані на спільні топіки або персональні черги клієнтів", size=10.5, color=MUTED))

    # Зв'язки між вузлами та шиною
    f.append(arrow(170, bus_y, 170, node_y + 68, color=GRAY, sw=1.2))
    f.append(arrow(490, bus_y, 490, node_y + 68, color=POS, sw=1.8))
    f.append(arrow(810, bus_y, 810, node_y + 68, color=GRAY, sw=1.2))

    # Джерело події (Фоновий сервіс)
    src_y = bus_y + 80
    f.append(fitbox(330, src_y, 320, 52, "Фоновий воркер / API-обробник\n(згенерував подію для Клієнта #42)", size=11.5, stroke=AMBER, fill="#fffde7"))
    f.append(arrow(490, src_y, 490, bus_y + 60, color=AMBER, sw=1.6))
    f.append(text(540, src_y - 8, "PUBLISH user:42", size=10, bold=True, color=AMBER))

    render(os.path.join(IMG, "horizontal-push-broker.svg"), W, H, *f)


# ── 5. Довге опитування та вікно перепідключення ─────────────────────────────
def fig_long_poll_cycle():
    W, H = 940, 440
    f = [text(W / 2, 28, "Цикл довгого опитування: затримка та вікно між запитами", size=16, bold=True)]

    PW, PH = 900, 380
    px, py = 20, 48
    f.append(rect(px, py, PW, PH, fill=PANEL, stroke=LINE, sw=1.2, rx=8))

    col_c = px + 120
    col_s = px + 780
    f.append(fitbox(col_c - 60, py + 16, 120, 38, "Клієнт", size=12, bold=True))
    f.append(fitbox(col_s - 60, py + 16, 120, 38, "Сервер", size=12, bold=True, stroke=LINE, fill=FILL))

    f.append(line(col_c, py + 56, col_c, py + 360, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col_s, py + 56, col_s, py + 360, color=GRAY, sw=1.2, dash="4 4"))

    # Запит 1
    y1 = py + 76
    f.append(arrow(col_c, y1, col_s, y1 + 14, color=AMBER, sw=1.4))
    f.append(text((col_c + col_s) / 2, y1 + 4, "1. GET /poll (клієнт надсилає запит)", size=10.5, color=AMBER))

    # Сервер чекає (блокується або в epoll)
    y_wait = y1 + 20
    f.append(rect(col_s - 6, y_wait, 12, 60, fill="#fff8e1", stroke=AMBER))
    f.append(text(col_s + 18, y_wait + 34, "Сервер тримає запит відкритим\n(події ще немає)", size=10, color=MUTED, anchor="start"))

    # Подія сталася
    y_ev = y_wait + 60
    f.append(text(col_s + 18, y_ev + 4, "⚡ Подія з'явилася!", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(arrow(col_s, y_ev, col_c, y_ev + 14, color=FIELD, sw=1.4))
    f.append(text((col_c + col_s) / 2, y_ev + 4, "2. 200 OK [дані події] (з'єднання завершується)", size=10.5, color=FIELD, bold=True))

    # Небезпечне вікно міжзапитового розриву (Reconnection Gap)
    y_gap = y_ev + 24
    f.append(rect(px + 140, y_gap, 620, 44, fill="#ffebee", stroke=POS, sw=1.2, rx=4))
    f.append(text(W / 2, y_gap + 18, "⚠️ ВІКНО МІЖ ЗАПИТАМИ (Reconnection Gap, 20–100 мс)", size=11, bold=True, color=POS))
    f.append(text(W / 2, y_gap + 34, "Клієнт парсить JSON і відкриває новий fetch. Якщо подія виникне зараз — потрібен буфер на сервері!", size=9.5, color=MUTED))

    # Запит 2
    y2 = y_gap + 56
    f.append(arrow(col_c, y2, col_s, y2 + 14, color=AMBER, sw=1.4))
    f.append(text((col_c + col_s) / 2, y2 + 4, "3. GET /poll?since_id=42 (новий запит із курсором)", size=10.5, color=AMBER))

    # Таймаут сервера
    y_to = y2 + 20
    f.append(rect(col_s - 6, y_to, 12, 50, fill="#e8edf3", stroke=GRAY))
    f.append(text(col_s + 18, y_to + 28, "Таймаут (наприклад, 30 с) без подій", size=10, color=MUTED, anchor="start"))

    y_end = y_to + 50
    f.append(arrow(col_s, y_end, col_c, y_end + 12, color=GRAY, sw=1.2))
    f.append(text((col_c + col_s) / 2, y_end + 4, "4. 204 No Content (сервер скидає таймаут -> клієнт знову перезапитує)", size=10, color=MUTED))

    render(os.path.join(IMG, "long-poll-cycle.svg"), W, H, *f)


def main():
    fig_transports_comparison()
    fig_websocket_frame()
    fig_sse_reconnection()
    fig_horizontal_push_broker()
    fig_long_poll_cycle()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
