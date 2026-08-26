# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. api-iot-dual-plane: Північна (Northbound) та Південна (Southbound) площини ──
def fig_api_iot_dual_plane():
    W, H = 940, 500
    p = []

    # Верхній рівень: Клієнти (Північ / Northbound)
    p.append(rect(40, 20, 860, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(470, 42, "Північна площина (Northbound Plane): Клієнти та користувачі", size=13, color=INK, bold=True))
    
    # 3 блоки клієнтів
    p.append(rect(60, 55, 250, 48, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(185, 76, "Веб-панелі (SPA / React)", size=11, color=NEG, bold=True))
    p.append(text(185, 93, "Операторські пульти керування", size=9.5, color=MUTED))

    p.append(rect(345, 55, 250, 48, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(470, 76, "Мобільні застосунки (iOS / Android)", size=11, color=NEG, bold=True))
    p.append(text(470, 93, "Користувацькі інтерфейси", size=9.5, color=MUTED))

    p.append(rect(630, 55, 250, 48, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(755, 76, "Корпоративні системи (ERP / SCADA)", size=11, color=NEG, bold=True))
    p.append(text(755, 93, "Аналітичні конвеєри та білінг", size=9.5, color=MUTED))

    # Стрілки між клієнтами та ядром
    p.append(arrow(185, 115, 185, 155, color=NEG, sw=1.8))
    p.append(arrow(185, 155, 185, 115, color=NEG, sw=1.8))
    p.append(text(250, 138, "HTTP/REST, gRPC, OAuth2 (Синхронний Request-Response)", size=10, color=NEG, bold=True))

    p.append(arrow(755, 115, 755, 155, color=NEG, sw=1.8))
    p.append(arrow(755, 155, 755, 115, color=NEG, sw=1.8))

    # Центральний рівень: Ядро IoT-служби (Сервісний рівень)
    p.append(rect(40, 160, 860, 180, fill="#ffffff", stroke="#cbd5e1", sw=1.8, rx=8))
    p.append(rect(40, 160, 860, 36, fill="#e9eefb", stroke=NEG, sw=1.8, rx=8))
    p.append(text(470, 183, "Ядро IoT-служби: Шлюз API, маршрутизація, стан та черги", size=13, color=NEG, bold=True))

    # Компоненти ядра
    box_w = 185
    box_h = 105
    cy_box = 210

    # 1. API Gateway & Auth
    p.append(rect(60, cy_box, box_w, box_h, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    p.append(text(152, 230, "L7 API Gateway", size=11, color=INK, bold=True))
    p.append(text(152, 248, "Контролер версій (v1/v2)", size=9.5, color=NEG))
    p.append(text(152, 265, "Автентифікація токенів", size=9.5, color=MUTED))
    p.append(text(152, 282, "Заголовки Deprecation", size=9.5, color=POS))
    p.append(text(152, 299, "Rate Limiting & Metrics", size=9.5, color=MUTED))

    # 2. REST Resource Router
    p.append(rect(270, cy_box, box_w, box_h, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    p.append(text(362, 230, "Ресурсний роутер", size=11, color=INK, bold=True))
    p.append(text(362, 248, "/v1/devices/{id}", size=9.5, color=FIELD))
    p.append(text(362, 265, "/telemetry (часові ряди)", size=9.5, color=MUTED))
    p.append(text(362, 282, "/commands (202 Accepted)", size=9.5, color=MUTED))
    p.append(text(362, 299, "/config (бажаний стан)", size=9.5, color=MUTED))

    # 3. Device Shadow & State
    p.append(rect(480, cy_box, box_w, box_h, fill="#fdf0e6", stroke="#c07a2e", sw=1.4, rx=6))
    p.append(text(572, 230, "Тіньовий стан (Shadow)", size=11, color="#c07a2e", bold=True))
    p.append(text(572, 248, "Цифровий двійник вузла", size=9.5, color=INK))
    p.append(text(572, 265, "Бажаний стан (Desired)", size=9.5, color=MUTED))
    p.append(text(572, 282, "Звітований стан (Reported)", size=9.5, color=MUTED))
    p.append(text(572, 299, "Delta-події для вузла", size=9.5, color="#c07a2e"))

    # 4. Command Broker & Ingestion
    p.append(rect(690, cy_box, box_w, box_h, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(782, 230, "Шлюз протоколів", size=11, color=FIELD, bold=True))
    p.append(text(782, 248, "MQTT-брокер / CoAP серв.", size=9.5, color=INK))
    p.append(text(782, 265, "Асинхронна черга команд", size=9.5, color=MUTED))
    p.append(text(782, 282, "Адаптери схем повідомлень", size=9.5, color=MUTED))
    p.append(text(782, 299, "Пайплайн збереження TSDB", size=9.5, color=FIELD))

    # Стрілки між ядром та пристроями
    p.append(arrow(362, 340, 362, 385, color=FIELD, sw=1.8))
    p.append(arrow(362, 385, 362, 340, color=FIELD, sw=1.8))
    p.append(text(530, 365, "MQTT / CoAP / LoRaWAN (Асинхронний Pub/Sub, сон, пуш телеметрії)", size=10, color=FIELD, bold=True))

    p.append(arrow(782, 340, 782, 385, color=FIELD, sw=1.8))
    p.append(arrow(782, 385, 782, 340, color=FIELD, sw=1.8))

    # Нижній рівень: Апаратні вузли (Південь / Southbound)
    p.append(rect(40, 390, 860, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(470, 412, "Південна площина (Southbound Plane): Парк польових пристроїв", size=13, color=INK, bold=True))

    # 3 типи пристроїв
    p.append(rect(60, 425, 250, 48, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(185, 446, "Автономні датчики (NB-IoT / GSM)", size=11, color=FIELD, bold=True))
    p.append(text(185, 463, "Глибокий сон 99% часу, батарея", size=9.5, color=MUTED))

    p.append(rect(345, 425, 250, 48, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(470, 446, "Виконавчі реле та контролери (Wi-Fi/Eth)", size=11, color=FIELD, bold=True))
    p.append(text(470, 463, "Постійне TCP-з'єднання, черга дій", size=9.5, color=MUTED))

    p.append(rect(630, 425, 250, 48, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(755, 446, "Промислові шлюзи (BLE / Modbus / Mesh)", size=11, color=FIELD, bold=True))
    p.append(text(755, 463, "Агрегація десятків локальних датчиків", size=9.5, color=MUTED))

    render(os.path.join(OUT, "api-iot-dual-plane.svg"), W, H, *p,
           title="Подвійна площина взаємодії IoT-служби: Північ (REST/gRPC) проти Півдня (MQTT/CoAP)")


# ── 2. rest-device-resource-model: Ресурсна модель та асинхронні команди ───────
def fig_rest_device_resource_model():
    W, H = 940, 520
    p = []

    # Колони учасників: Клієнт (UI/App), API-служба (REST), Черга/Брокер, Вузол у полі
    cx_cli = 120
    cx_api = 370
    cx_q   = 620
    cx_dev = 840

    # Шапки
    p.append(rect(cx_cli - 75, 18, 150, 36, fill="#e9eefb", stroke=NEG, sw=1.8, rx=6))
    p.append(text(cx_cli, 41, "Клієнт (UI / App)", size=12, color=NEG, bold=True))

    p.append(rect(cx_api - 85, 18, 170, 36, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    p.append(text(cx_api, 41, "REST API Служба", size=12, color=INK, bold=True))

    p.append(rect(cx_q - 80, 18, 160, 36, fill="#fdf0e6", stroke="#c07a2e", sw=1.8, rx=6))
    p.append(text(cx_q, 41, "Черга / MQTT Broker", size=12, color="#c07a2e", bold=True))

    p.append(rect(cx_dev - 75, 18, 150, 36, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(cx_dev, 41, "Вузол у полі (Device)", size=12, color=FIELD, bold=True))

    # Вертикальні лінії
    p.append(line(cx_cli, 54, cx_cli, 490, color="#d0d5dd", sw=1.5, dash="4,4"))
    p.append(line(cx_api, 54, cx_api, 490, color="#d0d5dd", sw=1.5, dash="4,4"))
    p.append(line(cx_q,   54, cx_q,   490, color="#d0d5dd", sw=1.5, dash="4,4"))
    p.append(line(cx_dev, 54, cx_dev, 490, color="#d0d5dd", sw=1.5, dash="4,4"))

    # 1. Запит на створення команди
    y1 = 90
    p.append(arrow(cx_cli, y1, cx_api, y1, color=NEG, sw=1.8))
    p.append(text(245, y1 - 8, "POST /v1/devices/dev-42/commands", size=10.5, color=NEG, bold=True))
    p.append(text(245, y1 + 14, "Payload: {action: 'RELAY_ON'}, Idempotency-Key: 'k89f'", size=9, color=MUTED))

    # 2. Створення запису в БД та черзі
    y2 = 140
    p.append(arrow(cx_api, y2, cx_q, y2, color="#c07a2e", sw=1.6))
    p.append(text(495, y2 - 8, "Зберегти команду cmd_901 (PENDING) & Enqueue", size=9.5, color="#c07a2e"))

    # 3. Миттєва відповідь 202 Accepted
    y3 = 185
    p.append(arrow(cx_api, y3, cx_cli, y3, color=FIELD, sw=1.8))
    p.append(text(245, y3 - 8, "HTTP 202 Accepted", size=11, color=FIELD, bold=True))
    p.append(text(245, y3 + 14, "Location: /v1/devices/dev-42/commands/cmd_901", size=9, color=INK))

    # Пристрій у сні
    y_sleep = 230
    p.append(rect(cx_dev - 65, y_sleep - 14, 130, 28, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(cx_dev, y_sleep + 4, "Спить 10 хвилин...", size=10, color=MUTED, italic=True))

    # 4. Пробудження та доставка
    y4 = 285
    p.append(rect(cx_dev - 70, y4 - 14, 140, 26, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(cx_dev, y4 + 4, "Пробудження / Connect", size=10, color=FIELD, bold=True))

    y5 = 325
    p.append(arrow(cx_q, y5, cx_dev, y5, color=FIELD, sw=1.6))
    p.append(text(730, y5 - 8, "MQTT: devices/dev-42/cmd (cmd_901)", size=9.5, color=FIELD))

    # 5. Виконання та підтвердження
    y6 = 375
    p.append(arrow(cx_dev, y6, cx_q, y6, color=FIELD, sw=1.6))
    p.append(text(730, y6 - 8, "ACK: cmd_901 status=EXECUTED", size=9.5, color=FIELD))

    y7 = 405
    p.append(arrow(cx_q, y7, cx_api, y7, color="#c07a2e", sw=1.6))
    p.append(text(495, y7 - 8, "Оновити статус: cmd_901 -> EXECUTED", size=9.5, color="#c07a2e"))

    # 6. Опитування статусу клієнтом
    y8 = 455
    p.append(arrow(cx_cli, y8, cx_api, y8, color=NEG, sw=1.6))
    p.append(text(245, y8 - 8, "GET /v1/devices/dev-42/commands/cmd_901", size=10, color=NEG))

    p.append(arrow(cx_api, y8 + 20, cx_cli, y8 + 20, color=FIELD, sw=1.6))
    p.append(text(245, y8 + 14, "HTTP 200 OK {status: 'EXECUTED', duration_ms: 120}", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "rest-device-resource-model.svg"), W, H, *p,
           title="Ресурсна модель пристрою в REST API та асинхронний життєвий цикл виконання команд")


# ── 3. api-versioning-strategies: Порівняння трьох стратегій версіонування ─────
def fig_api_versioning_strategies():
    W, H = 940, 480
    p = []

    cols = [
        ("1. Версія в URL (URI Path)", "/v1/devices/42/telemetry", 40, 270, "#e9eefb", NEG),
        ("2. Версія в заголовках (Headers)", "X-API-Version: 2026-03-01", 335, 270, "#fdf0e6", "#c07a2e"),
        ("3. Версія в схемі (Payload Schema)", '{"schema_v": 2, "readings": ...}', 630, 270, "#eef6ef", FIELD),
    ]

    for title, example, x, w, bg_col, stroke_col in cols:
        p.append(rect(x, 20, w, 440, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
        p.append(rect(x, 20, w, 68, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        p.append(text(x + w/2, 44, title, size=11.5, color=stroke_col, bold=True))
        p.append(text(x + w/2, 68, example, size=9.5, color=INK, italic=True))

    # Колонка 1: URL Path
    c1_x = 40 + 135
    p.append(rect(55, 105, 240, 95, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(c1_x, 125, "Механізм:", size=11, color=INK, bold=True))
    p.append(text(c1_x, 145, "Версія зашита прямо в шлях URL.", size=9.5, color=INK))
    p.append(text(c1_x, 163, "L7-проксі (Nginx/Envoy) легко", size=9.5, color=MUTED))
    p.append(text(c1_x, 181, "роутить запит на v1 або v2 пул.", size=9.5, color=MUTED))

    p.append(rect(55, 215, 240, 115, fill="#eef6ef", stroke=FIELD, sw=1, rx=6))
    p.append(text(c1_x, 235, "Переваги:", size=11, color=FIELD, bold=True))
    p.append(text(c1_x, 255, "• Максимальна прозорість у логах", size=9.5, color=INK))
    p.append(text(c1_x, 273, "• Просте кешування (унікальний URL)", size=9.5, color=INK))
    p.append(text(c1_x, 291, "• Без парсингу тіла чи заголовків", size=9.5, color=INK))
    p.append(text(c1_x, 309, "• Ідеально для Breaking Changes", size=9.5, color=FIELD))

    p.append(rect(55, 345, 240, 100, fill="#fbebee", stroke=POS, sw=1, rx=6))
    p.append(text(c1_x, 365, "Недоліки:", size=11, color=POS, bold=True))
    p.append(text(c1_x, 385, "• Зміна версії ламає весь префікс", size=9.5, color=INK))
    p.append(text(c1_x, 403, "• Дублювання спільних ендпоінтів", size=9.5, color=INK))
    p.append(text(c1_x, 421, "• Не підходить для точкових полів", size=9.5, color=MUTED))

    # Колонка 2: Headers
    c2_x = 335 + 135
    p.append(rect(350, 105, 240, 95, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(c2_x, 125, "Механізм:", size=11, color=INK, bold=True))
    p.append(text(c2_x, 145, "Версія передається в заголовку", size=9.5, color=INK))
    p.append(text(c2_x, 163, "X-API-Version або Accept Header", size=9.5, color="#c07a2e"))
    p.append(text(c2_x, 181, "(Content Negotiation vnd.iot.v2+json).", size=9.5, color=MUTED))

    p.append(rect(350, 215, 240, 115, fill="#eef6ef", stroke=FIELD, sw=1, rx=6))
    p.append(text(c2_x, 235, "Переваги:", size=11, color=FIELD, bold=True))
    p.append(text(c2_x, 255, "• Чистий, постійний ресурсний URL", size=9.5, color=INK))
    p.append(text(c2_x, 273, "• Гранулярні версії за датами", size=9.5, color=INK))
    p.append(text(c2_x, 291, "• Зручно для еволюції моделей", size=9.5, color=INK))
    p.append(text(c2_x, 309, "• Стандарт REST (Content-Type)", size=9.5, color=FIELD))

    p.append(rect(350, 345, 240, 100, fill="#fbebee", stroke=POS, sw=1, rx=6))
    p.append(text(c2_x, 365, "Недоліки:", size=11, color=POS, bold=True))
    p.append(text(c2_x, 385, "• Складніше кешування (Vary Header)", size=9.5, color=INK))
    p.append(text(c2_x, 403, "• Вимагає L7 розбору заголовків", size=9.5, color=INK))
    p.append(text(c2_x, 421, "• МК-клієнти часто мають сирі HTTP", size=9.5, color=POS))

    # Колонка 3: Payload Schema
    c3_x = 630 + 135
    p.append(rect(645, 105, 240, 95, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(c3_x, 125, "Механізм:", size=11, color=INK, bold=True))
    p.append(text(c3_x, 145, "Версія вкладена в тіло пакета", size=9.5, color=INK))
    p.append(text(c3_x, 163, "чи тег бінарного формату (Protobuf,", size=9.5, color=FIELD))
    p.append(text(c3_x, 181, "CBOR, JSON). Парсер обирає схему.", size=9.5, color=MUTED))

    p.append(rect(645, 215, 240, 115, fill="#eef6ef", stroke=FIELD, sw=1, rx=6))
    p.append(text(c3_x, 235, "Переваги:", size=11, color=FIELD, bold=True))
    p.append(text(c3_x, 255, "• Працює в MQTT, CoAP, LoRaWAN", size=9.5, color=FIELD))
    p.append(text(c3_x, 273, "• Не залежить від протоколу зв'язку", size=9.5, color=INK))
    p.append(text(c3_x, 291, "• Брокеру не потрібен розбір тем", size=9.5, color=INK))
    p.append(text(c3_x, 309, "• Сумісність зі Schema Registry", size=9.5, color=INK))

    p.append(rect(645, 345, 240, 100, fill="#fbebee", stroke=POS, sw=1, rx=6))
    p.append(text(c3_x, 365, "Недоліки:", size=11, color=POS, bold=True))
    p.append(text(c3_x, 385, "• Оверхед на десеріалізацію в роутері", size=9.5, color=INK))
    p.append(text(c3_x, 403, "• L7 проксі не бачить версію на льоту", size=9.5, color=INK))
    p.append(text(c3_x, 421, "• Неможливий швидкий дроп побитого", size=9.5, color=MUTED))

    render(os.path.join(OUT, "api-versioning-strategies.svg"), W, H, *p,
           title="Порівняння стратегій версіонування IoT API: URL Path, Headers та Payload Schema")


# ── 4. deprecation-sunset-lifecycle: Життєвий цикл депрекації та виведення ────
def fig_deprecation_sunset_lifecycle():
    W, H = 940, 480
    p = []

    # 4 послідовні фази на часовій осі
    phases = [
        ("1. Чинна версія (Active)", "v1 у продакшні", 40, 205, "#eef6ef", FIELD),
        ("2. Оголошення депрекації", "Deprecation & Sunset", 260, 205, "#fdf0e6", "#c07a2e"),
        ("3. Вікна блекауту (Brownout)", "Тестові відключення", 480, 205, "#fbebee", POS),
        ("4. Виведення (Sunset / 410)", "Остаточний вихід", 700, 200, "#f4f6f8", LINE),
    ]

    # Стрілка загальної осі часу
    p.append(arrow(30, 460, 910, 460, color=LINE, sw=2))
    p.append(text(470, 475, "Часова шкала життєвого циклу API (місяці / роки)", size=11, color=INK, bold=True))

    for title, sub, x, w, bg_col, stroke_col in phases:
        p.append(rect(x, 20, w, 400, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
        p.append(rect(x, 20, w, 54, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        p.append(text(x + w/2, 42, title, size=11, color=stroke_col, bold=True))
        p.append(text(x + w/2, 60, sub, size=9.5, color=INK))

    # Фаза 1: Активна версія
    cx1 = 40 + 102
    p.append(text(cx1, 95, "HTTP 200 OK", size=12, color=FIELD, bold=True))
    p.append(rect(50, 115, 185, 90, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(cx1, 135, "• Повний розвиток фіч", size=9.5, color=INK))
    p.append(text(cx1, 153, "• 100% пристроїв на v1", size=9.5, color=INK))
    p.append(text(cx1, 171, "• Без попереджень у логах", size=9.5, color=MUTED))
    p.append(text(cx1, 189, "• SLA підтримується 24/7", size=9.5, color=MUTED))

    p.append(rect(50, 220, 185, 80, fill="#eef6ef", stroke=FIELD, sw=1, rx=6))
    p.append(text(cx1, 240, "Стан пристроїв:", size=10, color=FIELD, bold=True))
    p.append(text(cx1, 260, "Парк працює штатно,", size=9.5, color=INK))
    p.append(text(cx1, 278, "нових версій ще немає.", size=9.5, color=MUTED))

    # Фаза 2: Оголошення депрекації
    cx2 = 260 + 102
    p.append(text(cx2, 95, "Заголовки RFC 8594", size=11, color="#c07a2e", bold=True))
    p.append(rect(270, 115, 185, 125, fill="#fdf0e6", stroke="#c07a2e", sw=1, rx=6))
    p.append(text(cx2, 133, "Deprecation: @1773446400", size=9, color=POS, bold=True))
    p.append(text(cx2, 150, "Sunset: 15 Nov 2026 GMT", size=9, color=POS, bold=True))
    p.append(text(cx2, 168, "Link: <.../v2>; rel='migr'", size=9, color=MUTED))
    p.append(text(cx2, 186, "• Метрики звернень за ID", size=9.5, color=INK))
    p.append(text(cx2, 204, "• Когорти старих прошивок", size=9.5, color=INK))
    p.append(text(cx2, 222, "• Повідомлення розробникам", size=9.5, color=MUTED))

    p.append(rect(270, 255, 185, 80, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(cx2, 275, "Моніторинг:", size=10, color=INK, bold=True))
    p.append(text(cx2, 295, "Графік спадання v1 трафіку,", size=9.5, color=MUTED))
    p.append(text(cx2, 313, "виявлення сплячих вузлів.", size=9.5, color=MUTED))

    # Фаза 3: Brownout Testing
    cx3 = 480 + 102
    p.append(text(cx3, 95, "Контрольований блекаут", size=11, color=POS, bold=True))
    p.append(rect(490, 115, 185, 125, fill="#fbebee", stroke=POS, sw=1, rx=6))
    p.append(text(cx3, 133, "5 хв штучного вимкнення", size=9.5, color=POS, bold=True))
    p.append(text(cx3, 151, "Повернення 410 Gone / 429", size=9.5, color=POS))
    p.append(text(cx3, 169, "• Перевірка сигналізацій", size=9.5, color=INK))
    p.append(text(cx3, 187, "• Тест реакції підтримки", size=9.5, color=INK))
    p.append(text(cx3, 205, "• 1 година за тиждень до...", size=9.5, color=MUTED))
    p.append(text(cx3, 223, "• Викриття забутих систем", size=9.5, color=MUTED))

    p.append(rect(490, 255, 185, 80, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(cx3, 275, "Результат фази:", size=10, color=INK, bold=True))
    p.append(text(cx3, 295, "Всі, хто ігнорував Sunset,", size=9.5, color=POS))
    p.append(text(cx3, 313, "терміново оновлюють код.", size=9.5, color=MUTED))

    # Фаза 4: Sunset / Retired
    cx4 = 700 + 100
    p.append(text(cx4, 95, "HTTP 410 Gone / Адаптер", size=11, color=INK, bold=True))
    p.append(rect(710, 115, 180, 125, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(cx4, 133, "Варіант А: Фізичний 410", size=9.5, color=POS, bold=True))
    p.append(text(cx4, 151, "Ендпоінт видалено з коду.", size=9.5, color=MUTED))
    p.append(text(cx4, 175, "Варіант Б: L7-адаптер", size=9.5, color=FIELD, bold=True))
    p.append(text(cx4, 193, "Проксі трансформує v1->v2", size=9.5, color=INK))
    p.append(text(cx4, 211, "для 'вічних' старих плат.", size=9.5, color=MUTED))

    p.append(rect(710, 255, 180, 80, fill="#eef6ef", stroke=FIELD, sw=1, rx=6))
    p.append(text(cx4, 275, "Фінал еволюції:", size=10, color=FIELD, bold=True))
    p.append(text(cx4, 295, "Сервер очищено від спадщини,", size=9.5, color=INK))
    p.append(text(cx4, 313, "старі прилади не зламано.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "deprecation-sunset-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл депрекації та виведення ендпоінтів: від попередження до Sunset")


if __name__ == "__main__":
    fig_api_iot_dual_plane()
    fig_rest_device_resource_model()
    fig_api_versioning_strategies()
    fig_deprecation_sunset_lifecycle()
    print("All figures for api-sluzhby generated successfully.")
