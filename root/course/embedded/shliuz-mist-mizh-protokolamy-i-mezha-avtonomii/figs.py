# -*- coding: utf-8 -*-
"""Фігури до теми «Шлюз: міст між протоколами й межа автономії».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Палітра для шлюзу
COL_SOUTH = "#d97706"  # польові шини (Modbus, CAN, BLE) — бурштиновий
COL_GW    = "#2563eb"  # шлюз / обчислення ядра — синій
COL_NORTH = "#059669"  # глобальна мережа (WAN / MQTT / Cloud) — зелений
COL_SEC   = "#dc2626"  # межа безпеки / ізоляція — червоний
COL_BUF   = "#7c3aed"  # сховище / Store-and-Forward — фіолетовий


# ── 1. Архітектура шлюзу: міст між двома світами ────────────────────────────
def fig_gateway_architecture():
    W, H = 840, 480
    f = [text(W / 2, 28, "Анатомія промислового IoT-шлюзу: подвійна природа та локальний мозок", 16, INK, "middle", bold=True)]

    # Тло блоків: Southbound (ліворуч), Gateway (центр), Northbound (праворуч)
    # Лівий блок: Польовий периметр (Southbound)
    f.append(rect(24, 60, 220, 370, fill="#fffbeb", stroke=COL_SOUTH, sw=1.6, rx=6))
    f.append(text(134, 88, "ПОЛЬОВИЙ СЕГМЕНТ", 12, COL_SOUTH, "middle", bold=True))
    f.append(text(134, 106, "(Southbound / OT)", 10, MUTED, "middle"))

    south_nodes = [
        ("RS-485 / Modbus RTU", "PLC, частотники, лічильники", 130),
        ("CAN 2.0B / CANopen", "Сервоприводи, датчики кута", 205),
        ("BLE GATT / Beacon", "Бездротові термодавачі", 280),
        ("LoRa P2P / 802.15.4", "Віддалені польові зонди", 355),
    ]
    for title, desc, y_pos in south_nodes:
        f.append(rect(36, y_pos, 196, 58, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
        f.append(text(134, y_pos + 22, title, 10.5, INK, "middle", bold=True))
        f.append(text(134, y_pos + 42, desc, 9, MUTED, "middle"))

    # Правий блок: Хмарний / корпоративний периметр (Northbound)
    f.append(rect(596, 60, 220, 370, fill="#ecfdf5", stroke=COL_NORTH, sw=1.6, rx=6))
    f.append(text(706, 88, "ГЛОБАЛЬНА МЕРЕЖА", 12, COL_NORTH, "middle", bold=True))
    f.append(text(706, 106, "(Northbound / IT / WAN)", 10, MUTED, "middle"))

    north_nodes = [
        ("MQTT Broker (TLS)", "Публікація подій та телеметрії", 130),
        ("Cloud Time-Series DB", "InfluxDB, TimescaleDB, S3", 205),
        ("REST / CoAP Сервери", "Конфігурація, звіти, OTA", 280),
        ("SCADA / MES Системи", "Диспетчерський нагляд", 355),
    ]
    for title, desc, y_pos in north_nodes:
        f.append(rect(608, y_pos, 196, 58, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
        f.append(text(706, y_pos + 22, title, 10.5, INK, "middle", bold=True))
        f.append(text(706, y_pos + 42, desc, 9, MUTED, "middle"))

    # Центральний блок: Шлюз (Edge Gateway)
    f.append(rect(264, 60, 312, 370, fill="#eff6ff", stroke=COL_GW, sw=2.2, rx=8))
    f.append(text(420, 88, "ІНДУСТРІАЛЬНИЙ ШЛЮЗ (EDGE GATEWAY)", 12.5, COL_GW, "middle", bold=True))
    f.append(text(420, 106, "Трансляція, автономія та брандмауер", 10, MUTED, "middle"))

    # Внутрішні компоненти шлюзу
    gw_modules = [
        ("1. Драйвери польових шин та опитувачі", "Polling Master, RX/TX Ring Buffers", 130, COL_SOUTH),
        ("2. Нормалізація та транслятор форматів", "Бінарні регістри → JSON / CBOR / Топіки", 195, COL_GW),
        ("3. Локальний рушій правил (Edge Autonomy)", "Аварійні пороги, прямий зворотний зв'язок", 260, COL_SEC),
        ("4. Store-and-Forward буфер (NVRAM/Flash)", "Захист від блекаутів WAN, черга відправки", 325, COL_BUF),
    ]
    for title, desc, y_pos, col in gw_modules:
        f.append(rect(276, y_pos, 288, 52, fill="#ffffff", stroke=col, sw=1.5, rx=5))
        f.append(text(420, y_pos + 20, title, 10, INK, "middle", bold=True))
        f.append(text(420, y_pos + 38, desc, 9, MUTED, "middle"))

    # Зв'язки (стрілки)
    # Зліва направо: Southbound -> Gateway
    for y_pos in [159, 234, 309, 384]:
        f.append(line(232, y_pos, 276, y_pos, color=COL_SOUTH, sw=1.8))
        f.append(arrow(268, y_pos, 276, y_pos, color=COL_SOUTH, sw=1.8))

    # Зсередини направо: Gateway -> Northbound
    for y_pos in [159, 234, 309, 384]:
        f.append(line(564, y_pos, 608, y_pos, color=COL_NORTH, sw=1.8))
        f.append(arrow(600, y_pos, 608, y_pos, color=COL_NORTH, sw=1.8))

    # Підпис знизу
    f.append(text(W / 2, 460, "Шлюз ізолює не-IP пристрої від WAN, перетворює моделі зв'язку та керує аваріями при обриві зв'язку", 10.5, INK, "middle", italic=True))

    render(os.path.join(IMG, "gateway-architecture.svg"), W, H, *f)


# ── 2. Механіка трансляції протоколів: бінарні регістри в топіки ──────────────
def fig_protocol_translation_mapping():
    W, H = 840, 420
    f = [text(W / 2, 28, "Механіка трансляції: перетворення моделі опитування у модель подій", 16, INK, "middle", bold=True)]

    # Ліва частина: Вхідний бінарний кадр Modbus RTU / BLE
    f.append(rect(30, 65, 340, 300, fill="#fffbeb", stroke=COL_SOUTH, sw=1.8, rx=6))
    f.append(text(200, 92, "ПОЛЬОВИЙ КАДР (Modbus RTU / RS-485)", 12, COL_SOUTH, "middle", bold=True))
    f.append(text(200, 110, "Синхронний опит Master-Slave (Raw Binary)", 10, MUTED, "middle"))

    # Структура сирого кадру
    f.append(rect(46, 130, 308, 44, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=4))
    f.append(text(76, 157, "0x0A", 11, INK, "middle", bold=True))
    f.append(text(76, 142, "Slave ID", 9.2, MUTED, "middle"))

    f.append(line(106, 130, 106, 174, color="#e5e7eb", sw=1.2))
    f.append(text(136, 157, "0x03", 11, INK, "middle", bold=True))
    f.append(text(136, 142, "Func", 9.2, MUTED, "middle"))

    f.append(line(166, 130, 166, 174, color="#e5e7eb", sw=1.2))
    f.append(text(196, 157, "0x04", 11, INK, "middle", bold=True))
    f.append(text(196, 142, "Bytes", 9.2, MUTED, "middle"))

    f.append(line(226, 130, 226, 174, color="#e5e7eb", sw=1.2))
    f.append(text(276, 157, "0x42 0x88 0x00 0x00", 10.5, COL_SOUTH, "middle", bold=True))
    f.append(text(276, 142, "Data (Reg 40001..2)", 9.2, MUTED, "middle"))

    # Розбір значень
    f.append(rect(46, 190, 308, 160, fill="#ffffff", stroke="#e5e7eb", sw=1.2, rx=4))
    f.append(text(60, 212, "Семантичний розбір у шлюзі:", 10.5, INK, "start", bold=True))
    f.append(text(60, 236, "• Пристрій: Котел #10 (Slave ID = 10)", 9.8, INK, "start"))
    f.append(text(60, 258, "• Регістр 0x0001: Тиск теплоносія (Float32)", 9.8, INK, "start"))
    f.append(text(60, 280, "• Байтовий порядок: Big-Endian (IEEE 754)", 9.8, INK, "start"))
    f.append(text(60, 302, "• Перетворення: 0x42880000 → 68.0", 9.8, COL_SOUTH, "start", bold=True))
    f.append(text(60, 324, "• Одиниці: бари (bar) + мітка часу RTC", 9.8, MUTED, "start"))

    # Центральний стрілочний блок
    f.append(line(370, 215, 465, 215, color=COL_GW, sw=2.5))
    f.append(arrow(455, 215, 465, 215, color=COL_GW, sw=2.5))
    f.append(text(418, 195, "ТРАНСЛЯЦІЯ", 10, COL_GW, "middle", bold=True))
    f.append(text(418, 235, "Мапінг схеми", 9, MUTED, "middle"))

    # Права частина: Вихідне повідомлення MQTT JSON
    f.append(rect(470, 65, 340, 300, fill="#ecfdf5", stroke=COL_NORTH, sw=1.8, rx=6))
    f.append(text(640, 92, "ВИХІДНЕ ПОВІДОМЛЕННЯ (MQTT / WAN)", 12, COL_NORTH, "middle", bold=True))
    f.append(text(640, 110, "Асинхронний Pub/Sub через TLS-з'єднання", 10, MUTED, "middle"))

    # MQTT Topic
    f.append(rect(486, 130, 308, 44, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=4))
    f.append(text(500, 145, "MQTT Topic:", 9, MUTED, "start"))
    f.append(text(500, 163, "plant1/boiler10/telemetry/pressure", 10.5, COL_NORTH, "start", bold=True))

    # MQTT Payload
    f.append(rect(486, 190, 308, 160, fill="#ffffff", stroke="#e5e7eb", sw=1.2, rx=4))
    f.append(text(500, 212, "JSON Payload (UTF-8):", 10.5, INK, "start", bold=True))
    f.append(text(510, 236, "{", 10, INK, "start"))
    f.append(text(524, 258, '"device_id": "boiler_10",', 9.8, INK, "start"))
    f.append(text(524, 280, '"pressure_bar": 68.0,', 9.8, COL_NORTH, "start", bold=True))
    f.append(text(524, 302, '"timestamp": 1724698800,', 9.8, INK, "start"))
    f.append(text(524, 324, '"status": "nominal"', 9.8, INK, "start"))
    f.append(text(510, 344, "}", 10, INK, "start"))

    # Підпис
    f.append(text(W / 2, 398, "Шлюз зв'язує фізичну адресу регістра з глобальною семантичною назвою ресурсу", 10.5, INK, "middle", italic=True))

    render(os.path.join(IMG, "protocol-translation-mapping.svg"), W, H, *f)


# ── 3. Життєвий цикл Store-and-Forward під час блекаутів ───────────────────────
def fig_store_and_forward_lifecycle():
    W, H = 840, 440
    f = [text(W / 2, 28, "Патерн Store-and-Forward: запобігання втраті телеметрії під час блекаутів WAN", 16, INK, "middle", bold=True)]

    # Три фази: 1. Нормальний стан, 2. Обрив WAN, 3. Відновлення та зрідження
    phases = [
        (30, 230, "1. ОНЛАЙН-РЕЖИМ", "Прямий стрімінг у брокер", "#ecfdf5", COL_NORTH),
        (280, 230, "2. БЛЕКАУТ WAN", "Накопичення у Flash Ring Buffer", "#fef2f2", COL_SEC),
        (530, 280, "3. ВІДНОВЛЕННЯ ЗВ'ЯЗКУ", "Зріджене викачування (Rate Limit)", "#faf5ff", COL_BUF),
    ]

    for x_pos, width, title, sub, bg_col, stroke_col in phases:
        f.append(rect(x_pos, 60, width, 320, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        f.append(text(x_pos + width / 2, 88, title, 11.5, stroke_col, "middle", bold=True))
        f.append(text(x_pos + width / 2, 106, sub, 9.2, MUTED, "middle"))

    # Фаза 1 деталі
    f.append(rect(45, 125, 200, 80, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(145, 150, "Давач → Шлюз", 10, INK, "middle", bold=True))
    f.append(arrow(145, 162, 145, 178, color=COL_NORTH, sw=1.8))
    f.append(text(145, 195, "Пряма публікація в MQTT", 9.5, COL_NORTH, "middle"))

    f.append(rect(45, 220, 200, 140, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(145, 245, "Стан буфера:", 10, INK, "middle", bold=True))
    f.append(text(145, 270, "• Буфер Flash порожній", 9.5, MUTED, "middle"))
    f.append(text(145, 295, "• Нульова затримка (RTT < 50ms)", 9.5, MUTED, "middle"))
    f.append(text(145, 320, "• Знос Flash = 0 (усе в RAM)", 9.5, COL_NORTH, "middle", bold=True))

    # Фаза 2 деталі
    f.append(rect(295, 125, 200, 80, fill="#ffffff", stroke=COL_SEC, sw=1.2, rx=4))
    f.append(text(395, 150, "Обрив WAN-лінка ✗", 10.5, COL_SEC, "middle", bold=True))
    f.append(text(395, 170, "Таймаут TCP / 4G зник", 9, MUTED, "middle"))
    f.append(text(395, 190, "Перехід у режим очікування", 9, COL_SEC, "middle"))

    f.append(rect(295, 220, 200, 140, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(395, 245, "Дії шлюзу в блекауті:", 10, INK, "middle", bold=True))
    f.append(text(395, 268, "• Запис блоків у Flash/eMMC", 9.3, INK, "middle"))
    f.append(text(395, 290, "• Автономні правила активні", 9.3, COL_SEC, "middle", bold=True))
    f.append(text(395, 312, "• При переповненні: FIFO drop", 9.3, MUTED, "middle"))
    f.append(text(395, 334, "  або зрідження (Downsample)", 9.3, MUTED, "middle"))

    # Фаза 3 деталі
    f.append(rect(545, 125, 250, 80, fill="#ffffff", stroke=COL_BUF, sw=1.2, rx=4))
    f.append(text(670, 150, "Зв'язок відновлено ✓", 10.5, COL_NORTH, "middle", bold=True))
    f.append(text(670, 170, "mTLS рукостискання успішне", 9, MUTED, "middle"))
    f.append(text(670, 190, "Старт дренажу черги", 9, COL_BUF, "middle"))

    f.append(rect(545, 220, 250, 140, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(670, 245, "Дисципліна викачування:", 10, INK, "middle", bold=True))
    f.append(text(670, 268, "• Свіжі дані йдуть у ПЕРШУ чергу", 9.3, COL_NORTH, "middle", bold=True))
    f.append(text(670, 290, "• Історичний буфер — фоном", 9.3, INK, "middle"))
    f.append(text(670, 312, "• Обмеження смуги (Rate Limit)", 9.3, MUTED, "middle"))
    f.append(text(670, 334, "• ACK брокера звільняє блоки Flash", 9.3, COL_BUF, "middle"))

    # Стрілки переходу між фазами
    f.append(line(260, 220, 280, 220, color=COL_SEC, sw=2))
    f.append(arrow(272, 220, 280, 220, color=COL_SEC, sw=2))

    f.append(line(510, 220, 530, 220, color=COL_BUF, sw=2))
    f.append(arrow(522, 220, 530, 220, color=COL_BUF, sw=2))

    # Підпис знизу
    f.append(text(W / 2, 415, "Контрольований дренаж запобігає перевантаженню вузького каналу зв'язку та втраті оперативних даних", 10.5, INK, "middle", italic=True))

    render(os.path.join(IMG, "store-and-forward-lifecycle.svg"), W, H, *f)


# ── 4. Безпека: шлюз як брандмауер та межа довіри ─────────────────────────────
def fig_security_perimeter_ot_it():
    W, H = 840, 440
    f = [text(W / 2, 28, "Шлюз як межа безпеки: захист польового OT-периметра від атак з IT/WAN", 16, INK, "middle", bold=True)]

    # Недовірена зона (Зовнішній інтернет / WAN)
    f.append(rect(24, 60, 210, 330, fill="#fef2f2", stroke=COL_SEC, sw=1.8, rx=6))
    f.append(text(129, 88, "НЕДОВІРЕНА ЗОНА", 12, COL_SEC, "middle", bold=True))
    f.append(text(129, 106, "(Публічний інтернет / WAN)", 10, MUTED, "middle"))

    threats = [
        ("Сканування портів", "Шкідливий ботнет"),
        ("Replay / Spoofing", "Підміна пакетів"),
        ("DoS / Перевантаження", "Забиття шини трафіком"),
        ("Прямі ін'єкції", "Спроби збити прошивку"),
    ]
    for i, (thr, desc) in enumerate(threats):
        y_pos = 135 + i * 58
        f.append(rect(36, y_pos, 186, 48, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
        f.append(text(129, y_pos + 20, thr, 10, COL_SEC, "middle", bold=True))
        f.append(text(129, y_pos + 36, desc, 9.2, MUTED, "middle"))

    # Центральна захисна стіна (Брандмауер / Шлюз)
    f.append(rect(254, 60, 330, 330, fill="#eff6ff", stroke=COL_GW, sw=2.2, rx=8))
    f.append(text(419, 88, "ШЛЮЗ ЯК БРАНДМАУЕР (SECURE EDGE)", 12, COL_GW, "middle", bold=True))
    f.append(text(419, 106, "Нульова довіра (Zero-Trust Boundary)", 10, MUTED, "middle"))

    defenses = [
        ("1. Закриті вхідні порти (No Listen)", "Лише вихідні клієнтські mTLS-сесії"),
        ("2. Апаратний захист ключів (TPM/SE)", "Secure Boot, зашифроване сховище"),
        ("3. Повна санітизація низхідних команд", "Перевірка діапазонів, Rate-limit, ACL"),
        ("4. Фізична ізоляція шин (Air-Gap logic)", "Неможливість прямої маршрутизації IP → RS485"),
    ]
    for i, (title, desc) in enumerate(defenses):
        y_pos = 135 + i * 58
        f.append(rect(266, y_pos, 306, 48, fill="#ffffff", stroke=COL_GW, sw=1.4, rx=4))
        f.append(text(419, y_pos + 20, title, 9.8, INK, "middle", bold=True))
        f.append(text(419, y_pos + 36, desc, 9.2, MUTED, "middle"))

    # Довірена захищена зона (Польовий периметр / OT)
    f.append(rect(604, 60, 210, 330, fill="#ecfdf5", stroke=COL_NORTH, sw=1.8, rx=6))
    f.append(text(709, 88, "ДОВІРЕНА ЗОНА", 12, COL_NORTH, "middle", bold=True))
    f.append(text(709, 106, "(Польові контролери / OT)", 10, MUTED, "middle"))

    protected_nodes = [
        ("Modbus RTU вузли", "Без криптографії та паролів"),
        ("CANopen приводи", "Відкритий протокол без захисту"),
        ("BLE маяки", "Мінімальний стек пам'яті"),
        ("Датчики 4-20 мА", "Аналогові сигнальні ланцюги"),
    ]
    for i, (node, desc) in enumerate(protected_nodes):
        y_pos = 135 + i * 58
        f.append(rect(616, y_pos, 186, 48, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
        f.append(text(709, y_pos + 20, node, 10, COL_NORTH, "middle", bold=True))
        f.append(text(709, y_pos + 36, desc, 9.2, MUTED, "middle"))

    # Блокування атак ліворуч
    f.append(line(224, 225, 254, 225, color=COL_SEC, sw=2.5, dash="3 3"))
    f.append(text(239, 212, "✗ БЛОК", 9.5, COL_SEC, "middle", bold=True))

    # Санкціонований потік праворуч
    f.append(line(584, 225, 604, 225, color=COL_NORTH, sw=2))
    f.append(arrow(596, 225, 604, 225, color=COL_NORTH, sw=2))
    f.append(text(594, 212, "✓ ВАЛІДНО", 9.5, COL_NORTH, "middle", bold=True))

    # Підпис знизу
    f.append(text(W / 2, 415, "Шлюз повністю виключає прямий мережевий контакт між незахищеними польовими МК та зовнішньою мережею", 10.5, INK, "middle", italic=True))

    render(os.path.join(IMG, "security-perimeter-ot-it.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gateway_architecture()
    fig_protocol_translation_mapping()
    fig_store_and_forward_lifecycle()
    fig_security_perimeter_ot_it()
    print("OK: figures generated successfully.")
