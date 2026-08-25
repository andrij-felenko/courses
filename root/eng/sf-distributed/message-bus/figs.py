# -*- coding: utf-8 -*-
"""Фігури до теми «Шина повідомлень»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / попарний хаос / відмова
COOL = "#eaf0fd"   # нейтральне / повідомлення / сервіси
GOOD = "#e8f6ee"   # успіх / шина / канонічна модель
WARN = "#fef9e7"   # посередник / перехоплювач / буфер
ACCENT = "#2457d6" # синій акцент
BUS_COLOR = "#8e44ad" # фіолетовий для магістралі шини


# ── 1. Порівняння попарної інтеграції «спагеті» та топології шини ────────────
def p2p_vs_bus_topology():
    W, H = 1080, 520
    f = []

    # Загальний фон
    f.append(rect(15, 15, 1050, 490, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))

    # ── Ліва панель: Попарна інтеграція (Spaghetti Architecture) ──
    f.append(rect(30, 35, 490, 455, fill=WARM, stroke=POS, sw=1.5, rx=8))
    f.append(text(275, 65, "Попарна інтеграція («спагеті»)", size=15, bold=True, color=POS))
    f.append(text(275, 88, "N = 5 сервісів  →  N(N−1)/2 = 10 попарних з'єднань", size=11.5, color=INK))
    f.append(text(275, 106, "20 адаптерів трансляції форматів і протоколів", size=11, color=MUTED, italic=True))

    # Координати 5 вузлів по колу (ліворуч)
    nodes_left = [
        ("Замовлення", 275, 150),
        ("Оплата", 400, 235),
        ("Склад", 355, 385),
        ("Доставка", 195, 385),
        ("Аналітика", 150, 235),
    ]

    # Сплутані попарні лінії зв'язку (усі пари)
    for i in range(len(nodes_left)):
        for j in range(i + 1, len(nodes_left)):
            x1, y1 = nodes_left[i][1], nodes_left[i][2]
            x2, y2 = nodes_left[j][1], nodes_left[j][2]
            f.append(line(x1, y1, x2, y2, color="#e74c3c", sw=1.4, dash="3,3"))

    # Малюємо блоки сервісів ліворуч
    for name, nx, ny in nodes_left:
        f.append(fitbox(nx - 52, ny - 22, 104, 44, name, size=11.5, bold=True, fill="#ffffff", stroke=POS, sw=1.5))

    # Нижній висновок для лівої панелі
    f.append(fitbox(45, 425, 460, 52, "Жорстка комбінаторна зв'язаність:\nЗміна формату в одному сервісі ламає 4 сусідні адаптери", size=11, bold=True, fill="#ffffff", color=POS, stroke=POS, sw=1.2))

    # ── Права панель: Топологія шини повідомлень (Message Bus) ──
    f.append(rect(545, 35, 505, 455, fill=GOOD, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(797, 65, "Шина повідомлень (Message Bus)", size=15, bold=True, color=FIELD))
    f.append(text(797, 88, "N = 5 сервісів  →  рівно N = 5 підключень до магістралі", size=11.5, color=INK))
    f.append(text(797, 106, "Єдина канонічна модель даних (CDM) + стандартизований конверт", size=11, color=MUTED, italic=True))

    # Центральна шина (горизонтальна широка смуга)
    f.append(rect(585, 255, 425, 50, fill="#f5eef8", stroke=BUS_COLOR, sw=2.2, rx=6))
    f.append(text(797, 280, "Спільна магістраль шини (Канонічні події та команди)", size=12.5, bold=True, color=BUS_COLOR))
    f.append(text(797, 296, "Маршрутизація · Фільтрація · Трасування · Гарантії черг", size=10, color=MUTED, italic=True))

    # Вузли сервісів (верхній і нижній яруси)
    top_nodes = [
        ("Замовлення", 645, 160),
        ("Оплата", 797, 160),
        ("Склад", 950, 160),
    ]
    bot_nodes = [
        ("Доставка", 715, 390),
        ("Аналітика", 880, 390),
    ]

    # Стрілки та адаптери від верхніх сервісів до шини
    for name, nx, ny in top_nodes:
        f.append(fitbox(nx - 52, ny - 22, 104, 44, name, size=11.5, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5))
        # Адаптер (маленький прямокутник)
        f.append(rect(nx - 28, 218, 56, 22, fill=WARN, stroke=LINE, sw=1.0, rx=3))
        f.append(text(nx, 233, "Адаптер", size=9, bold=True, color=INK))
        # Двосторонній зв'язок
        f.append(line(nx, ny + 22, nx, 218, color=LINE, sw=1.5))
        f.append(arrow(nx, 240, nx, 255, color=FIELD, sw=1.6))

    # Стрілки та адаптери від нижніх сервісів до шини
    for name, nx, ny in bot_nodes:
        f.append(fitbox(nx - 52, ny - 22, 104, 44, name, size=11.5, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5))
        # Адаптер
        f.append(rect(nx - 28, 320, 56, 22, fill=WARN, stroke=LINE, sw=1.0, rx=3))
        f.append(text(nx, 335, "Адаптер", size=9, bold=True, color=INK))
        # Двосторонній зв'язок
        f.append(line(nx, ny - 22, nx, 342, color=LINE, sw=1.5))
        f.append(arrow(nx, 320, nx, 305, color=FIELD, sw=1.6))

    # Нижній висновок для правої панелі
    f.append(fitbox(560, 425, 475, 52, "Повне архітектурне розчеплення:\nДодавання нового сервісу вимагає лише 1 адаптера до канонічної шини", size=11, bold=True, fill="#ffffff", color=FIELD, stroke=FIELD, sw=1.2))

    render(os.path.join(OUT, 'p2p-vs-bus-topology.svg'), W, H, *f)


# ── 2. Внутрішня архітектура та підсистеми шини повідомлень ──────────────────
def message_bus_internal_architecture():
    W, H = 1080, 560
    f = []

    # Загальний фон
    f.append(rect(15, 15, 1050, 530, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))

    # Ліва колонка: Продюсери та вхідні адаптери
    f.append(rect(30, 40, 200, 485, fill=COOL, stroke=ACCENT, sw=1.4, rx=8))
    f.append(text(130, 68, "Джерела повідомлень", size=13.5, bold=True, color=ACCENT))
    f.append(text(130, 88, "Продюсери / Клієнти", size=11, color=MUTED, italic=True))

    f.append(fitbox(45, 110, 170, 60, "Сервіс замовлень\n(Видавець подій)", size=11.5, bold=True, fill="#ffffff"))
    f.append(fitbox(45, 185, 170, 45, "Вхідний адаптер (Outbox)\nТрансляція в канонічну схему", size=10, fill=WARN))

    f.append(fitbox(45, 260, 170, 60, "Платіжний шлюз\n(Команди обробки)", size=11.5, bold=True, fill="#ffffff"))
    f.append(fitbox(45, 335, 170, 45, "Вхідний адаптер (Outbox)\nФормування конверта", size=10, fill=WARN))

    f.append(fitbox(45, 410, 170, 95, "Зовнішній Webhook / API\n(HTTP / JSON)\n\nШлюз адаптації\n(Edge Gateway)", size=10.5, fill="#ffffff"))

    # Стрілки вводу в шину
    f.append(arrow(215, 207, 260, 207, color=LINE, sw=1.6))
    f.append(arrow(215, 357, 260, 357, color=LINE, sw=1.6))
    f.append(arrow(215, 457, 260, 457, color=LINE, sw=1.6))

    # Центральна секція: Ядро шини повідомлень (Message Bus Core)
    f.append(rect(260, 40, 560, 485, fill="#f8fafc", stroke=BUS_COLOR, sw=1.8, rx=8))
    f.append(text(540, 68, "Ядро шини повідомлень (Message Bus Core)", size=15, bold=True, color=BUS_COLOR))

    # Блок 1: Конвеєр перехоплювачів (Interceptor Pipeline)
    f.append(rect(280, 95, 520, 110, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(540, 118, "Конвеєр перехоплювачів (Middleware / Interceptors)", size=12.5, bold=True, color=INK))

    inter_w = 95
    inter_h = 55
    ix0 = 295
    f.append(fitbox(ix0, 135, inter_w, inter_h, "1. Автентифікація\nта перевірка прав", size=9.5, fill=COOL))
    f.append(arrow(ix0 + inter_w, 162, ix0 + inter_w + 10, 162, color=LINE, sw=1.2))

    f.append(fitbox(ix0 + 105, 135, inter_w, inter_h, "2. Валідація схеми\n(Schema Registry)", size=9.5, fill=COOL))
    f.append(arrow(ix0 + 105 + inter_w, 162, ix0 + 105 + inter_w + 10, 162, color=LINE, sw=1.2))

    f.append(fitbox(ix0 + 210, 135, inter_w, inter_h, "3. Трасування\n(W3C TraceContext)", size=9.5, fill=COOL))
    f.append(arrow(ix0 + 210 + inter_w, 162, ix0 + 210 + inter_w + 10, 162, color=LINE, sw=1.2))

    f.append(fitbox(ix0 + 315, 135, inter_w, inter_h, "4. Дедуплікація\nта ідемпотентність", size=9.5, fill=COOL))
    f.append(arrow(ix0 + 315 + inter_w, 162, ix0 + 315 + inter_w + 10, 162, color=LINE, sw=1.2))

    f.append(fitbox(ix0 + 420, 135, 80, inter_h, "5. Метрики\nта аудит", size=9.5, fill=COOL))

    # Стрілка від конвеєра до маршрутизатора
    f.append(arrow(540, 205, 540, 230, color=LINE, sw=1.8))

    # Блок 2: Диспетчер та маршрутизатор каналів
    f.append(rect(280, 230, 520, 175, fill="#fdfbf7", stroke=LINE, sw=1.2, rx=6))
    f.append(text(540, 252, "Маршрутизатор і канали повідомлень (Routing & Channel Engine)", size=12.5, bold=True, color=INK))

    # Три канали
    f.append(fitbox(295, 270, 155, 115, "Канали Pub/Sub (Теми)\n\n• events.orders.created\n• events.orders.paid\n• events.inventory.held\n(Роздача 1:N)", size=10, fill=GOOD))
    f.append(fitbox(462, 270, 155, 115, "Черги команд (P2P)\n\n• cmd.billing.charge\n• cmd.email.send\n• cmd.delivery.schedule\n(Конкурентні воркери 1:1)", size=10, fill=GOOD))
    f.append(fitbox(630, 270, 155, 115, "Запит-Відповідь (RPC)\n\n• Dynamic Reply Queue\n• Correlation ID Match\n• Таймаути й повернення\n(Асинхронний відгук)", size=10, fill=GOOD))

    # Блок 3: Стійкість та ізоляція збоїв (Нижня смуга в ядрі)
    f.append(rect(280, 420, 520, 90, fill="#fdf3f2", stroke=POS, sw=1.2, rx=6))
    f.append(text(540, 442, "Стійкість до відмов: Буфер на диску (WAL) та Мертва черга (DLQ)", size=11.5, bold=True, color=POS))
    f.append(fitbox(295, 455, 245, 45, "💾 Журнал випереджального запису\nПовідомлення не губляться при перезапуску", size=9.5, fill="#ffffff"))
    f.append(fitbox(550, 455, 235, 45, "☠ Мертва черга (DLQ) + Карантин\nІзоляція отруйних повідомлень (Poison)", size=9.5, fill="#ffffff"))

    # Стрілки виводу з шини до споживачів
    f.append(arrow(820, 290, 850, 170, color=LINE, sw=1.6))
    f.append(arrow(820, 320, 850, 310, color=LINE, sw=1.6))
    f.append(arrow(820, 350, 850, 450, color=LINE, sw=1.6))

    # Права колонка: Споживачі та вихідні адаптери
    f.append(rect(850, 40, 200, 485, fill=GOOD, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(950, 68, "Отримувачі повідомлень", size=13.5, bold=True, color=FIELD))
    f.append(text(950, 88, "Споживачі / Воркери", size=11, color=MUTED, italic=True))

    f.append(fitbox(865, 110, 170, 45, "Вихідний адаптер (Inbox)\nДесеріалізація та валідація", size=10, fill=WARN))
    f.append(fitbox(865, 160, 170, 60, "Сервіс складу\n(Оновлення залишків)", size=11.5, bold=True, fill="#ffffff"))

    f.append(fitbox(865, 250, 170, 45, "Вихідний адаптер (Inbox)\nКонтроль ідемпотентності", size=10, fill=WARN))
    f.append(fitbox(865, 300, 170, 60, "Сервіс сповіщень\n(Push / Email клієнту)", size=11.5, bold=True, fill="#ffffff"))

    f.append(fitbox(865, 390, 170, 45, "Вихідний адаптер (Inbox)\nПакетний буфер подій", size=10, fill=WARN))
    f.append(fitbox(865, 440, 170, 60, "Аналітичне сховище\n(ClickHouse / Data Lake)", size=11.5, bold=True, fill="#ffffff"))

    render(os.path.join(OUT, 'message-bus-internal-architecture.svg'), W, H, *f)


# ── 3. Трансляція через канонічну модель даних (Canonical Data Model) ────────
def canonical_data_model_translation():
    W, H = 1080, 500
    f = []

    # Загальний фон
    f.append(rect(15, 15, 1050, 470, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))

    # Заголовок зверху
    f.append(text(540, 45, "Трансляція даних через канонічну модель (Canonical Data Model)", size=16, bold=True, color=INK))
    f.append(text(540, 68, "Локальні діалекти сервісів транслюються у стандартизований конверт на кордоні шини", size=11.5, color=MUTED, italic=True))

    # ── Лівий блок: Джерело (Сервіс оплат, власний JSON) ──
    f.append(rect(35, 95, 260, 370, fill=COOL, stroke=ACCENT, sw=1.4, rx=6))
    f.append(text(165, 122, "1. Локальна модель джерела", size=12.5, bold=True, color=ACCENT))
    f.append(text(165, 140, "Сервіс білінгу (JSON REST)", size=10.5, color=MUTED, italic=True))

    json_src = (
        "{\n"
        '  "inv_id": 9841,\n'
        '  "amt_cents": 150000,\n'
        '  "cur": "UAH",\n'
        '  "cust": "user_77",\n'
        '  "st": "SUCCESS",\n'
        '  "t": 1724148000\n'
        "}"
    )
    f.append(fitbox(50, 155, 230, 160, json_src, size=11, color=INK, fill="#ffffff", stroke=MUTED, sw=1.0))

    f.append(fitbox(50, 335, 230, 110, "Вхідний адаптер (Translator):\n• Читає внутрішні поля білінгу\n• Додає UUID, trace_id, тип\n• Формує бінарний Protobuf\n• Публікує в шину", size=10.5, fill=WARN))

    # Стрілка від джерела до канонічного конверта
    f.append(arrow(295, 280, 345, 280, color=LINE, sw=2.0))
    f.append(text(320, 268, "Адаптація", size=10, color=MUTED, italic=True))

    # ── Центральний блок: Канонічний конверт на шині (Canonical Envelope) ──
    f.append(rect(345, 95, 390, 370, fill="#fdfbf7", stroke=BUS_COLOR, sw=2.0, rx=8))
    f.append(text(540, 122, "2. Канонічний конверт шини (Canonical Envelope)", size=13, bold=True, color=BUS_COLOR))
    f.append(text(540, 140, "Спільний корпоративний стандарт (Protobuf / Avro / CloudEvents)", size=10.5, color=MUTED, italic=True))

    # Заголовки конверта
    env_headers = (
        "=== ЗАГОЛОВКИ (Metadata Headers) ===\n"
        "message_id:     \"550e8400-e29b-41d4-a716-446655440000\"\n"
        "message_type:   \"events.billing.payment_received\"\n"
        "schema_version: \"2.1.0\"\n"
        "timestamp_utc:  \"2026-08-20T08:40:00.124Z\"\n"
        "correlation_id: \"corr_ord_10482\"\n"
        "traceparent:    \"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01\"\n"
        "idempotency_key:\"pay_9841_attempt_1\""
    )
    f.append(fitbox(360, 155, 360, 145, env_headers, size=9.5, bold=True, color=INK, fill="#ffffff", stroke=BUS_COLOR, sw=1.2))

    # Корисне навантаження конверта (Payload)
    env_payload = (
        "=== КОРИСНЕ НАВАНТАЖЕННЯ (Canonical Payload) ===\n"
        "order_id:       \"ord_10482\"\n"
        "customer_id:    \"cust_user_77\"\n"
        "amount_minor:   150000        // копійки\n"
        "currency_code:  \"UAH\"         // ISO 4217\n"
        "payment_status: PAYMENT_COMPLETED"
    )
    f.append(fitbox(360, 310, 360, 135, env_payload, size=9.5, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Стрілки від шини до двох отримувачів
    f.append(arrow(735, 210, 785, 175, color=LINE, sw=2.0))
    f.append(arrow(735, 350, 785, 385, color=LINE, sw=2.0))

    # ── Правий верхній блок: Отримувач 1 (Склад ERP - SOAP / XML) ──
    f.append(rect(785, 95, 260, 175, fill=GOOD, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(915, 118, "3A. Складська система (ERP)", size=11.5, bold=True, color=FIELD))
    f.append(text(915, 134, "Трансляція в корпоративний XML", size=9.5, color=MUTED, italic=True))

    xml_dst = (
        "<HoldStockRequest>\n"
        '  <OrderId>ord_10482</OrderId>\n'
        "  <Status>PAID</Status>\n"
        "</HoldStockRequest>"
    )
    f.append(fitbox(800, 145, 230, 110, xml_dst, size=10, fill="#ffffff", stroke=MUTED, sw=1.0))

    # ── Правий нижній блок: Отримувач 2 (Аналітика - SQL / Parquet) ──
    f.append(rect(785, 290, 260, 175, fill=GOOD, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(915, 313, "3B. Аналітика (ClickHouse)", size=11.5, bold=True, color=FIELD))
    f.append(text(915, 329, "Трансляція в колоночну схему", size=9.5, color=MUTED, italic=True))

    sql_dst = (
        "INSERT INTO payments_fact\n"
        "(order_id, user_id, uah_amt,\n"
        " paid_at_ts, trace_id)\n"
        "VALUES ('ord_10482', 'user_77',\n"
        " 1500.00, 1724148000, ...)"
    )
    f.append(fitbox(800, 340, 230, 110, sql_dst, size=10, fill="#ffffff", stroke=MUTED, sw=1.0))

    render(os.path.join(OUT, 'canonical-data-model-translation.svg'), W, H, *f)


if __name__ == "__main__":
    p2p_vs_bus_topology()
    message_bus_internal_architecture()
    canonical_data_model_translation()
    print("All figures generated successfully.")
