# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми SCTP (RFC 4960)."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_four_way_handshake():
    """Чотириетапне рукостискання SCTP із захистом State Cookie від SYN Flood."""
    w, h = 860, 580
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Чотириетапне рукостискання SCTP (RFC 4960)", size=16, bold=True))

    # Стовпчики хостів
    x_cli, x_srv = 130, 730
    frags.append(textbox(x_cli, 70, "Клієнт (Endpoint A)\nIP: A1, A2", size=12, fill="#e8f0fe", stroke=NEG, bold=True)[0])
    frags.append(textbox(x_srv, 70, "Сервер (Endpoint B)\nIP: B1, B2", size=12, fill="#fef3e8", stroke=POS, bold=True)[0])

    # Вертикальні лінії життя
    frags.append(line(x_cli, 105, x_cli, 515, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(x_srv, 105, x_srv, 515, color=MUTED, sw=1.5, dash="4,4"))

    # Початкові стани
    frags.append(text(x_cli - 65, 125, "CLOSED", size=10, color=MUTED, bold=True))
    frags.append(text(x_srv + 65, 125, "LISTEN", size=10, color=MUTED, bold=True))

    # 1. INIT
    y1 = 145
    frags.append(arrow(x_cli + 10, y1, x_srv - 10, y1 + 35, color=NEG, sw=2))
    msg1 = "1. INIT [Initiate Tag=0x9A4F, a_rwnd=65535, OutStr=10, InStr=10, InitTSN=1000, IPs={A1,A2}]"
    frags.append(text(w / 2, y1 + 10, msg1, size=10, color=INK, bold=True))
    frags.append(text(x_cli - 65, y1 + 25, "COOKIE-WAIT", size=10, color=NEG, bold=True))

    # Сервер обробляє INIT без стану
    y_cookie_gen = 205
    box_srv_stateless, _, _ = textbox(520, y_cookie_gen, "Сервер обчислює:\nCookie = HMAC(Key, Params+Time)\nБЕЗ виділення пам'яті TCB!", size=10, fill="#fff2e8", stroke=POS, sw=1.2)
    frags.append(box_srv_stateless)

    # 2. INIT ACK
    y2 = 250
    frags.append(arrow(x_srv - 10, y2, x_cli + 10, y2 + 35, color=POS, sw=2))
    msg2 = "2. INIT ACK [Initiate Tag=0x3C81, a_rwnd=65535, InitTSN=5000, STATE COOKIE, IPs={B1,B2}]"
    frags.append(text(w / 2, y2 + 10, msg2, size=10, color=INK, bold=True))

    # Клієнт створює TCB
    y_cli_tcb = 310
    frags.append(text(x_cli - 65, y_cli_tcb, "COOKIE-ECHOED", size=9, color=NEG, bold=True))
    box_cli_tcb, _, _ = textbox(340, y_cli_tcb, "Клієнт створює TCB,\nзберігає узгоджені параметри", size=10, fill="#e8f4fc", stroke=NEG, sw=1.2)
    frags.append(box_cli_tcb)

    # 3. COOKIE ECHO
    y3 = 355
    frags.append(arrow(x_cli + 10, y3, x_srv - 10, y3 + 35, color=NEG, sw=2))
    msg3 = "3. COOKIE ECHO [State Cookie + необов'язкові перші DATA Chunks]"
    frags.append(text(w / 2, y3 + 10, msg3, size=10, color=INK, bold=True))

    # Сервер перевіряє Cookie та створює TCB
    y_srv_verify = 410
    box_srv_verify, _, _ = textbox(520, y_srv_verify, "Перевірка HMAC Cookie.\nЯкщо валідна -> створює TCB!", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2)
    frags.append(box_srv_verify)
    frags.append(text(x_srv + 65, y_srv_verify + 20, "ESTABLISHED", size=10, color=FIELD, bold=True))

    # 4. COOKIE ACK
    y4 = 450
    frags.append(arrow(x_srv - 10, y4, x_cli + 10, y4 + 35, color=FIELD, sw=2))
    msg4 = "4. COOKIE ACK [Підтвердження готовності асоціації]"
    frags.append(text(w / 2, y4 + 10, msg4, size=10, color=INK, bold=True))

    # Фінальний стан клієнта
    frags.append(text(x_cli - 65, y4 + 40, "ESTABLISHED", size=10, color=FIELD, bold=True))

    # Нижній висновок
    box_summary, _, _ = textbox(w / 2, 545, "Захист від SYN Flood: сервер не виділяє ресурси ядра (TCB) до отримання валідного COOKIE ECHO у кроці 3", size=11, fill="#f4f6f8", stroke=LINE, bold=True)
    frags.append(box_summary)

    render(os.path.join(OUT_DIR, "four-way-handshake.svg"), w, h, *frags)


def fig_sctp_packet_structure():
    """Загальна структура пакета SCTP та модульні чанки DATA і SACK."""
    w, h = 820, 520
    frags = []

    frags.append(text(w / 2, 26, "Структура пакета SCTP (Заголовок та Chunks)", size=16, bold=True))

    # 1. Загальний заголовок (12 байтів)
    y_hdr = 70
    frags.append(textbox(w / 2, y_hdr - 16, "Загальний заголовок SCTP (12 байтів / Common Header)", size=13, fill="#f0f4f8", stroke=LINE, bold=True)[0])

    # Сітка 32 біти для заголовка
    bw = 700
    bx0 = (w - bw) / 2
    # Поля заголовка
    # Рядок 1: Порт відправника (16 біт) + Порт отримувача (16 біт)
    frags.append(rect(bx0, y_hdr, bw / 2, 34, fill="#e8f0fe", stroke=NEG, sw=1.5))
    frags.append(text(bx0 + bw / 4, y_hdr + 21, "Source Port (16 біт)", size=12, bold=True))
    frags.append(rect(bx0 + bw / 2, y_hdr, bw / 2, 34, fill="#e8f0fe", stroke=NEG, sw=1.5))
    frags.append(text(bx0 + 3 * bw / 4, y_hdr + 21, "Destination Port (16 біт)", size=12, bold=True))

    # Рядок 2: Verification Tag (32 біти)
    frags.append(rect(bx0, y_hdr + 34, bw, 34, fill="#fef3e8", stroke=POS, sw=1.5))
    frags.append(text(bx0 + bw / 2, y_hdr + 55, "Verification Tag (32 біти) — валідація належності асоціації", size=12, bold=True))

    # Рядок 3: Checksum (32 біти)
    frags.append(rect(bx0, y_hdr + 68, bw, 34, fill="#eafaf1", stroke=FIELD, sw=1.5))
    frags.append(text(bx0 + bw / 2, y_hdr + 89, "Checksum (32 біти) — CRC32c (RFC 3309) або Adler-32", size=12, bold=True))

    # Розділювач / Chunks Container
    y_chunks = 205
    frags.append(textbox(w / 2, y_chunks, "Послідовність Chunks (кожен вирівняний по 32-бітному слову з Padding)", size=13, fill="#f9fafb", stroke=MUTED, bold=True)[0])

    # Приклад 1: DATA Chunk
    y_data = 245
    frags.append(text(bx0 + 80, y_data - 8, "DATA Chunk (Type = 0x00):", size=12, color=NEG, bold=True))
    frags.append(rect(bx0, y_data, bw * 0.25, 30, fill="#e8f0fe", stroke=NEG, sw=1.2))
    frags.append(text(bx0 + bw * 0.125, y_data + 19, "Type = 0 (8b)", size=11))
    frags.append(rect(bx0 + bw * 0.25, y_data, bw * 0.25, 30, fill="#e8f0fe", stroke=NEG, sw=1.2))
    frags.append(text(bx0 + bw * 0.375, y_data + 19, "Flags: U, B, E (8b)", size=11))
    frags.append(rect(bx0 + bw * 0.50, y_data, bw * 0.50, 30, fill="#e8f0fe", stroke=NEG, sw=1.2))
    frags.append(text(bx0 + bw * 0.75, y_data + 19, "Chunk Length (16 біт)", size=11))

    # DATA рядки 2 і 3
    frags.append(rect(bx0, y_data + 30, bw, 28, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(bx0 + bw / 2, y_data + 48, "Transmission Sequence Number — TSN (32 біти, надійність асоціації)", size=11, bold=True))

    frags.append(rect(bx0, y_data + 58, bw / 2, 28, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(bx0 + bw / 4, y_data + 76, "Stream Identifier — SID (16b)", size=11))
    frags.append(rect(bx0 + bw / 2, y_data + 58, bw / 2, 28, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(bx0 + 3 * bw / 4, y_data + 76, "Stream Sequence Number — SSN (16b)", size=11))

    frags.append(rect(bx0, y_data + 86, bw, 28, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(bx0 + bw / 2, y_data + 104, "Payload Protocol Identifier — PPID (32 біти, M3UA, WebRTC, S1AP)", size=11))

    frags.append(rect(bx0, y_data + 114, bw, 30, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(text(bx0 + bw / 2, y_data + 133, "User Data Payload (корисні дані прикладного повідомлення) + Падінг (0-3 байти)", size=11, italic=True))

    # Приклад 2: SACK Chunk (Коротко)
    y_sack = 415
    frags.append(text(bx0 + 80, y_sack - 8, "SACK Chunk (Type = 0x03, Selective ACK):", size=12, color=FIELD, bold=True))
    frags.append(rect(bx0, y_sack, bw / 2, 28, fill="#eafaf1", stroke=FIELD, sw=1.2))
    frags.append(text(bx0 + bw / 4, y_sack + 18, "Cumulative TSN Ack (32 біти)", size=11, bold=True))
    frags.append(rect(bx0 + bw / 2, y_sack, bw / 2, 28, fill="#eafaf1", stroke=FIELD, sw=1.2))
    frags.append(text(bx0 + 3 * bw / 4, y_sack + 18, "a_rwnd (Advertised Window, 32 біти)", size=11))

    frags.append(rect(bx0, y_sack + 28, bw, 28, fill="#ffffff", stroke=FIELD, sw=1.2))
    frags.append(text(bx0 + bw / 2, y_sack + 46, "Gap Ack Blocks (діапазони доставлених блоків) + Duplicate TSNs (дублікати)", size=11))

    # Висновок
    frags.append(textbox(w / 2, 495, "Один IP-пакет може об'єднувати кілька керуючих та інформаційних чанків у межах MTU", size=11, fill="#f4f6f8", stroke=LINE)[0])

    render(os.path.join(OUT_DIR, "sctp-packet-structure.svg"), w, h, *frags)


def fig_multistreaming_holb():
    """Мультистрімінг та усунення блокування початку черги (Head-of-Line Blocking)."""
    w, h = 820, 520
    frags = []

    frags.append(text(w / 2, 26, "Мультистрімінг SCTP проти блокування черги (HoLB)", size=16, bold=True))

    # Ліва колонка: Традиційний TCP (Блокування початку черги)
    x_tcp = 205
    frags.append(textbox(x_tcp, 65, "TCP: один байтовий потік на з'єднання", size=13, fill="#fdf2e9", stroke=POS, bold=True)[0])

    # Пакети TCP
    y_t = 110
    frags.append(rect(x_tcp - 150, y_t, 300, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(x_tcp - 100, y_t + 24, "Pkt 1 [OK]", size=11, color=FIELD, bold=True))
    frags.append(rect(x_tcp - 40, y_t + 5, 80, 30, fill="#fde8e8", stroke=POS, sw=1.5))
    frags.append(text(x_tcp, y_t + 24, "Pkt 2 [ВТРАТА]", size=10, color=POS, bold=True))
    frags.append(text(x_tcp + 90, y_t + 24, "Pkt 3 [OK]", size=11, color=MUTED))

    # Буфер доставки TCP
    frags.append(arrow(x_tcp, y_t + 45, x_tcp, y_t + 85, color=POS, sw=2))
    frags.append(textbox(x_tcp, y_t + 120, "Буфер приймача TCP:\nPkt 3 заблоковано в очікуванні\nповторної передачі Pkt 2!", size=11, fill="#fde8e8", stroke=POS, bold=True)[0])

    frags.append(arrow(x_tcp, y_t + 160, x_tcp, y_t + 200, color=MUTED, sw=1.5))
    frags.append(textbox(x_tcp, y_t + 225, "Прикладний застосунок:\nПОВНЕ ЗАВИСАННЯ ВСІХ СЕСІЙ\n(Head-of-Line Blocking)", size=11, fill="#f9d5d5", stroke=POS, bold=True)[0])

    # Права колонка: Мультистрімінг SCTP
    x_sctp = 615
    frags.append(textbox(x_sctp, 65, "SCTP: множина незалежних потоків", size=13, fill="#eafaf1", stroke=FIELD, bold=True)[0])

    # Потоки SCTP
    y_s = 105
    # Stream 0
    frags.append(rect(x_sctp - 150, y_s, 300, 32, fill="#e8f0fe", stroke=NEG, sw=1.2))
    frags.append(text(x_sctp - 90, y_s + 20, "Потік 0 (SSN=0,1):", size=11, bold=True, color=NEG))
    frags.append(text(x_sctp + 50, y_s + 20, "Всі чанки доставлено [OK]", size=11, color=FIELD, bold=True))

    # Stream 1 (з втратою)
    frags.append(rect(x_sctp - 150, y_s + 38, 300, 32, fill="#fef3e8", stroke=POS, sw=1.2))
    frags.append(text(x_sctp - 90, y_s + 58, "Потік 1 (SSN=0,1):", size=11, bold=True, color=POS))
    frags.append(text(x_sctp + 50, y_s + 58, "Втрачено SSN=0 -> Чекає", size=11, color=POS, bold=True))

    # Stream 2
    frags.append(rect(x_sctp - 150, y_s + 76, 300, 32, fill="#e8f0fe", stroke=NEG, sw=1.2))
    frags.append(text(x_sctp - 90, y_s + 96, "Потік 2 (SSN=0,1):", size=11, bold=True, color=NEG))
    frags.append(text(x_sctp + 50, y_s + 96, "Всі чанки доставлено [OK]", size=11, color=FIELD, bold=True))

    # Стрілки доставки SCTP
    frags.append(arrow(x_sctp, y_s + 115, x_sctp, y_s + 155, color=FIELD, sw=2))
    frags.append(textbox(x_sctp, y_s + 195, "Приймач SCTP (демультиплексор):\nПотік 0 та Потік 2 передаються\nзастосунку НЕГАЙНО!", size=11, fill="#eafaf1", stroke=FIELD, bold=True)[0])

    frags.append(arrow(x_sctp, y_s + 240, x_sctp, y_s + 275, color=FIELD, sw=1.5))
    frags.append(textbox(x_sctp, y_s + 305, "Прикладний застосунок:\nБлокується ЛИШЕ транзакція Потоку 1.\nРешта транзакцій працюють без затримок!", size=11, fill="#d5f5e3", stroke=FIELD, bold=True)[0])

    # Нижній висновок
    y_bot = 460
    frags.append(textbox(w / 2, y_bot, "TSN гарантує надійність на рівні всієї асоціації, а окремі SSN забезпечують впорядкування всередині потоку", size=12, fill="#f4f6f8", stroke=LINE, bold=True)[0])

    render(os.path.join(OUT_DIR, "multistreaming-holb.svg"), w, h, *frags)


def fig_multihoming_failover():
    """Мультихоумінг та автоматичне перемикання шляхів (Failover) при відмові каналу."""
    w, h = 860, 530
    frags = []

    frags.append(text(w / 2, 26, "Мультихоумінг SCTP та автоматичний Failover", size=16, bold=True))

    # Хост А (зліва)
    x_a = 120
    frags.append(rect(x_a - 100, 75, 200, 380, fill="#f0f4f8", stroke=LINE, sw=1.5))
    frags.append(text(x_a, 100, "Вузол A (Host A)", size=13, bold=True))
    frags.append(textbox(x_a, 150, "Інтерфейс eth0\nIP: 198.51.100.1", size=10, fill="#e8f0fe", stroke=NEG, bold=True)[0])
    frags.append(textbox(x_a, 370, "Інтерфейс eth1\nIP: 203.0.113.1", size=10, fill="#fef3e8", stroke=POS, bold=True)[0])

    # Хост B (справа)
    x_b = 740
    frags.append(rect(x_b - 100, 75, 200, 380, fill="#f0f4f8", stroke=LINE, sw=1.5))
    frags.append(text(x_b, 100, "Вузол B (Host B)", size=13, bold=True))
    frags.append(textbox(x_b, 150, "Інтерфейс eth0\nIP: 198.51.100.2", size=10, fill="#e8f0fe", stroke=NEG, bold=True)[0])
    frags.append(textbox(x_b, 370, "Інтерфейс eth1\nIP: 203.0.113.2", size=10, fill="#fef3e8", stroke=POS, bold=True)[0])

    # Шлях 1: Основний (Primary Path) — Збій
    y_p1 = 150
    frags.append(line(x_a + 100, y_p1, x_b - 100, y_p1, color=POS, sw=2.5, dash="6,6"))
    frags.append(textbox(w / 2, y_p1 - 35, "Основний шлях (Primary Path) — активний трафік DATA\n[Обрив зв'язку / Збій маршрутизатора ✗]", size=10, fill="#fde8e8", stroke=POS, bold=True)[0])

    # Позначка аварії по центру лінії
    frags.append(circle(w / 2, y_p1, 14, fill="#c0392b", stroke="#ffffff", sw=2))
    frags.append(text(w / 2, y_p1 + 5, "✗", size=14, color="#ffffff", bold=True))

    # Центральний блок логіки Failover
    y_mid = 255
    logic_text = "Логіка перемикання (RFC 4960):\n1. Таймаут DATA/Heartbeat на Primary -> Path.Error.Count++\n2. Якщо помилок > Path.Max.Retrans -> Шлях стає INACTIVE\n3. SCTP прозоро перенаправляє DATA на Alternate Path БЕЗ розриву сесії!"
    frags.append(textbox(w / 2, y_mid, logic_text, size=10, fill="#ffffff", stroke=LINE, sw=1.5)[0])

    # Шлях 2: Резервний (Alternate Path) — Зондування та Failover
    y_p2 = 370
    frags.append(textbox(w / 2, y_p2 - 35, "Резервний шлях (Alternate Path) — HEARTBEAT зондування RTO ->\nАвтоматичне перемикання потоку DATA!", size=10, fill="#eafaf1", stroke=FIELD, bold=True)[0])
    frags.append(arrow(x_a + 100, y_p2 - 6, x_b - 100, y_p2 - 6, color=FIELD, sw=1.8))
    frags.append(arrow(x_b - 100, y_p2 + 8, x_a + 100, y_p2 + 8, color=FIELD, sw=1.8))

    # Нижній висновок
    frags.append(textbox(w / 2, 490, "Мультихоумінг забезпечує надійність операторського класу (99.999%): фізична відмова інтерфейсу не розриває з'єднання", size=11, fill="#f4f6f8", stroke=LINE)[0])

    render(os.path.join(OUT_DIR, "multihoming-failover.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_four_way_handshake()
    fig_sctp_packet_structure()
    fig_multistreaming_holb()
    fig_multihoming_failover()
    print("Всі SVG-фігури для SCTP успішно згенеровано.")
