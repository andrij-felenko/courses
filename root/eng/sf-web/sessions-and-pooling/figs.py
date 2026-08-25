# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_overhead_vs_keepalive():
    """Порівняння одноразових HTTP-з'єднань із персистентним з'єднанням (Keep-Alive)."""
    W, H = 940, 480
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Порівняння накладних витрат: Одноразові з'єднання проти HTTP Keep-Alive",
                      size=16, bold=True))

    # ── Ліва колонка: Одноразові з'єднання
    frags.append(rect(30, 50, 425, 385, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(242, 75, "Без Keep-Alive (окремий сокет на кожен запит)", size=13, bold=True, color=POS))

    # Запит 1
    frags.append(rect(45, 95, 395, 85, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=5))
    frags.append(text(60, 115, "Запит 1:", size=11, bold=True, anchor="start"))
    frags.append(text(60, 133, "• TCP Handshake (SYN -> SYN-ACK -> ACK): 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 150, "• TLS 1.3 Handshake (Keys + Cert): 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 167, "• HTTP GET /api/v1/user -> 200 OK: 1 RTT  |  Закриття: FIN/ACK", size=10, color=INK, anchor="start"))

    # Запит 2
    frags.append(rect(45, 190, 395, 85, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=5))
    frags.append(text(60, 210, "Запит 2:", size=11, bold=True, anchor="start"))
    frags.append(text(60, 228, "• Повторний TCP Handshake на новому порту: 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 245, "• Повторний TLS Handshake (нова асиметрична криптографія): 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 262, "• HTTP GET /api/v1/orders -> 200 OK: 1 RTT  |  Закриття: FIN/ACK", size=10, color=INK, anchor="start"))

    # Запит 3
    frags.append(rect(45, 285, 395, 85, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=5))
    frags.append(text(60, 305, "Запит 3:", size=11, bold=True, anchor="start"))
    frags.append(text(60, 323, "• Повторний TCP Handshake: 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 340, "• Повторний TLS Handshake: 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(60, 357, "• HTTP GET /api/v1/items -> 200 OK: 1 RTT  |  Закриття: FIN/ACK", size=10, color=INK, anchor="start"))

    # Підсумок ліворуч
    frags.append(rect(45, 380, 395, 45, fill="#fde8e8", stroke=POS, sw=1.2, rx=5))
    frags.append(text(242, 398, "Загальна затримка: 9 RTT (при 50 мс = 450 мс)", size=11, bold=True, color=POS))
    frags.append(text(242, 415, "3 сокети в стані TIME_WAIT (ризик виснаження портів)", size=10, color=MUTED))

    # ── Права колонка: Keep-Alive та повторне використання
    frags.append(rect(485, 50, 425, 385, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(697, 75, "З Keep-Alive та пулом (одне відкрите з'єднання)", size=13, bold=True, color=FIELD))

    # Запит 1 (ініціалізація)
    frags.append(rect(500, 95, 395, 85, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=5))
    frags.append(text(515, 115, "Запит 1 (встановлення зв'язку):", size=11, bold=True, anchor="start"))
    frags.append(text(515, 133, "• TCP Handshake (SYN -> SYN-ACK -> ACK): 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(515, 150, "• TLS 1.3 Handshake (Keys + Cert): 1 RTT", size=10, color=MUTED, anchor="start"))
    frags.append(text(515, 167, "• HTTP GET /api/v1/user -> 200 OK: 1 RTT  |  Сокет лишається відкритим", size=10, color=FIELD, anchor="start"))

    # Запит 2 (повторне використання)
    frags.append(rect(500, 190, 395, 85, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=5))
    frags.append(text(515, 210, "Запит 2 (повторне використання каналу):", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(515, 232, "• Сокет вилучається з пулу без хендшейків (0 RTT)", size=10, color=FIELD, anchor="start"))
    frags.append(text(515, 255, "• HTTP GET /api/v1/orders -> 200 OK: 1 RTT", size=10, color=INK, anchor="start"))

    # Запит 3 (повторне використання)
    frags.append(rect(500, 285, 395, 85, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=5))
    frags.append(text(515, 305, "Запит 3 (повторне використання каналу):", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(515, 327, "• Сокет вилучається з пулу без хендшейків (0 RTT)", size=10, color=FIELD, anchor="start"))
    frags.append(text(515, 350, "• HTTP GET /api/v1/items -> 200 OK: 1 RTT", size=10, color=INK, anchor="start"))

    # Підсумок праворуч
    frags.append(rect(500, 380, 395, 45, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(697, 398, "Загальна затримка: 3 RTT (при 50 мс = 150 мс, утричі швидше)", size=11, bold=True, color=FIELD))
    frags.append(text(697, 415, "0 сокетів у TIME_WAIT, мінімальне навантаження на процесор", size=10, color=MUTED))

    frags.append(text(W / 2, 460, "Keep-Alive усуває повторні TCP/TLS-рукостискання для всіх наступних HTTP-запитів",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "tcp-tls-overhead-vs-keepalive.svg"), W, H, *frags)


def fig_session_pool_architecture():
    """Архітектура клієнтської сесії, диспетчера пулів та черги з'єднань."""
    W, H = 960, 490
    frags = []

    frags.append(text(W / 2, 28, "Архітектура клієнтської сесії та пулу з'єднань (Connection Pool)",
                      size=16, bold=True))

    # ── Зовнішній контур: Клієнтська сесія
    frags.append(rect(30, 50, 900, 400, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 75, "Об'єкт Session (стан застосунку)", size=14, bold=True, color=INK))

    # 1. Cookie Jar
    frags.append(rect(50, 95, 265, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(182, 118, "Cookie Jar (Сховище куків)", size=12, bold=True, color=INK))
    frags.append(text(182, 138, "Автоматичний парсинг Set-Cookie", size=10, color=MUTED))
    frags.append(text(182, 155, "Фільтрація за Host/Path та ін'єкція Cookie", size=10, color=MUTED))

    # 2. Заголовки та автентифікація
    frags.append(rect(345, 95, 270, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(480, 118, "Default Headers & Auth", size=12, bold=True, color=INK))
    frags.append(text(480, 138, "Authorization: Bearer <token>", size=10, color=MUTED))
    frags.append(text(480, 155, "User-Agent, Accept, Accept-Encoding", size=10, color=MUTED))

    # 3. Контекст TLS / Безпеки
    frags.append(rect(645, 95, 265, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(777, 118, "TLS Context & Proxies", size=12, bold=True, color=INK))
    frags.append(text(777, 138, "Клієнтські сертифікати (mTLS)", size=10, color=MUTED))
    frags.append(text(777, 155, "CA bundles (verify), налаштування проксі", size=10, color=MUTED))

    # Стрілка вниз до менеджера пулів
    frags.append(arrow(480, 180, 480, 205, color=LINE, sw=1.5))

    # ── Внутрішній блок: Менеджер пулів з'єднань (PoolManager)
    frags.append(rect(50, 210, 860, 225, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    frags.append(text(190, 233, "PoolManager (Диспетчер підпулів)", size=13, bold=True, color=FIELD))
    frags.append(text(620, 233, "Маршрутизація запитів за ключем Origin: (scheme, host, port)", size=11, color=MUTED))

    # Підпул 1: api.example.com
    frags.append(rect(70, 255, 380, 165, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(260, 277, "Підпул: ('https', 'api.example.com', 443)", size=11, bold=True, color=FIELD))
    frags.append(text(260, 295, "pool_maxsize = 10, timeout = 30s", size=10, color=MUTED))

    # Черга сокетів у підпулі 1
    frags.append(rect(85, 310, 160, 95, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(165, 330, "LIFO Черга вільних", size=10, bold=True, color=FIELD))
    frags.append(text(165, 350, "Socket #1 [IDLE: 1.2s]", size=10, color=INK))
    frags.append(text(165, 370, "Socket #2 [IDLE: 0.4s]", size=10, color=INK))
    frags.append(text(165, 390, "(Найновіший зверху)", size=9, color=MUTED))

    frags.append(rect(265, 310, 170, 95, fill="#fdf2e9", stroke="#e67e22", sw=1.0, rx=4))
    frags.append(text(350, 330, "Орендовані потоками", size=10, bold=True, color="#d35400"))
    frags.append(text(350, 350, "Socket #3 -> Потік A", size=10, color=INK))
    frags.append(text(350, 370, "Socket #4 -> Потік B", size=10, color=INK))
    frags.append(text(350, 390, "Семафор: 2 зайняті / 8 вільних", size=9, color=MUTED))

    # Підпул 2: auth.example.com
    frags.append(rect(480, 255, 410, 165, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(685, 277, "Підпул: ('https', 'auth.example.com', 443)", size=11, bold=True, color=INK))
    frags.append(text(685, 295, "pool_maxsize = 5, timeout = 30s", size=10, color=MUTED))

    frags.append(rect(495, 310, 185, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(587, 330, "LIFO Черга вільних", size=10, bold=True, color=INK))
    frags.append(text(587, 355, "Socket #5 [IDLE: 4.1s]", size=10, color=INK))
    frags.append(text(587, 380, "(1 готовий сокет)", size=9, color=MUTED))

    frags.append(rect(695, 310, 180, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(785, 330, "Орендовані потоками", size=10, bold=True, color=INK))
    frags.append(text(785, 355, "Немає активних запитів", size=10, color=MUTED))
    frags.append(text(785, 380, "Семафор: 0 зайнято / 5 вільних", size=9, color=MUTED))

    frags.append(text(W / 2, 472, "Сесія керує станом застосунку (куки, заголовки), а диспетчер пулів ізолює з'єднання за доменами",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "session-pool-architecture.svg"), W, H, *frags)


def fig_lifecycle_and_race():
    """Життєвий цикл сокета в пулі та гонка закриття за таймаутом бездіяльності."""
    W, H = 940, 480
    frags = []

    frags.append(text(W / 2, 28, "Життєвий цикл з'єднання та гонка закриття (Idle Timeout Race)",
                      size=16, bold=True))

    # ── Лівий блок: Стан сокета в пулі
    frags.append(rect(30, 55, 415, 385, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(237, 80, "Стани сокета в пулі з'єднань", size=13, bold=True, color=INK))

    # Стан 1: Створення
    frags.append(rect(60, 105, 355, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=5))
    frags.append(text(237, 125, "1. NEW (Створення сокета)", size=11, bold=True, color=INK))
    frags.append(text(237, 143, "DNS -> TCP Connect -> TLS Handshake", size=10, color=MUTED))

    frags.append(arrow(237, 155, 237, 175, color=LINE, sw=1.3))

    # Стан 2: В оренді
    frags.append(rect(60, 175, 355, 50, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=5))
    frags.append(text(237, 195, "2. ACQUIRED / LEASED (Використання)", size=11, bold=True, color=FIELD))
    frags.append(text(237, 213, "Відправка HTTP Request -> Читання Response", size=10, color=INK))

    # Розгалуження
    frags.append(arrow(237, 225, 237, 245, color=LINE, sw=1.3))

    # Стан 3: В очікуванні (IDLE)
    frags.append(rect(60, 245, 355, 55, fill="#e8f4fd", stroke=NEG, sw=1.0, rx=5))
    frags.append(text(237, 265, "3. IDLE (Вільний у пулі LIFO)", size=11, bold=True, color=NEG))
    frags.append(text(237, 283, "Чекає наступного запиту; цокає таймер бездіяльності", size=10, color=MUTED))

    frags.append(arrow(237, 300, 237, 320, color=LINE, sw=1.3))

    # Стан 4: Закриття
    frags.append(rect(60, 320, 355, 50, fill="#fde8e8", stroke=POS, sw=1.0, rx=5))
    frags.append(text(237, 340, "4. CLOSED / DISCARDED (Знищення)", size=11, bold=True, color=POS))
    frags.append(text(237, 358, "Таймаут, помилка мережі або закриття сесії", size=10, color=MUTED))

    # Повторне використання
    frags.append(text(237, 410, "Повторне використання: ACQUIRED ⇄ IDLE без створення нового сокета",
                      size=10, color=FIELD, bold=True))

    # ── Правий блок: Гонка закриття (Race Condition)
    frags.append(rect(475, 55, 435, 385, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(692, 80, "Гонка тайм-ауту бездіяльності (Server Idle Timeout)", size=13, bold=True, color=POS))

    # Часова шкала
    frags.append(line(540, 110, 540, 385, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(840, 110, 840, 385, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(540, 105, "Клієнт", size=11, bold=True))
    frags.append(text(840, 105, "Сервер", size=11, bold=True))

    # Подія 1: Таймаут на сервері
    frags.append(text(840, 140, "Таймаут 5.0с вичерпано!", size=10, bold=True, color=POS, anchor="end"))
    frags.append(arrow(840, 155, 540, 225, color=POS, sw=1.5))
    frags.append(text(690, 175, "TCP FIN / RST (у польоті)", size=10, color=POS))

    # Подія 2: Клієнт бере сокет одночасно
    frags.append(text(540, 165, "Потік бере сокет з пулу", size=10, bold=True, color=INK, anchor="start"))
    frags.append(arrow(540, 185, 840, 255, color=INK, sw=1.5))
    frags.append(text(690, 230, "HTTP GET /data (у польоті)", size=10, color=INK))

    # Колізія
    frags.append(rect(495, 275, 395, 65, fill="#fde8e8", stroke=POS, sw=1.2, rx=5))
    frags.append(text(692, 295, "Зіткнення пакетів у каналі:", size=11, bold=True, color=POS))
    frags.append(text(692, 313, "Сервер отримує GET на закритому сокеті -> повертає TCP RST", size=10, color=INK))
    frags.append(text(692, 328, "Клієнт отримує ConnectionResetError (розрив з'єднання)", size=10, color=POS))

    # Захист
    frags.append(rect(495, 350, 395, 75, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(692, 368, "Як запобігти збою:", size=11, bold=True, color=FIELD))
    frags.append(text(692, 386, "1. Перевірка сокета перед запитом (Socket Health Check через poll/select)", size=9, color=INK))
    frags.append(text(692, 402, "2. Автоматичний повтор (Retry) для ідемпотентних методів (GET/HEAD)", size=9, color=INK))

    frags.append(text(W / 2, 462, "Асинхронне закриття сокета сервером потребує валідації каналу перед запитом та ідемпотентних повторів",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "connection-lifecycle-and-race.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_overhead_vs_keepalive()
    fig_session_pool_architecture()
    fig_lifecycle_and_race()
    print("Figures generated successfully in img/")
