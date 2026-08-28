# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_gateway_architecture():
    W, H = 840, 520
    p = []

    # Заголовок / фонові зони
    # Ліва зона: Southbound (Польовий периметр)
    p.append(rect(20, 20, 230, 480, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(135, 45, "Низхідний контур (Southbound)", size=13, color=INK, bold=True))
    p.append(text(135, 62, "Польові шини та сенсори", size=11, color=MUTED))

    # Центральна зона: Шлюзовий рушій (Gateway Engine & Storage)
    p.append(rect(270, 20, 310, 480, fill="#ffffff", stroke=FIELD, sw=2, rx=8))
    p.append(text(425, 45, "Ядро шлюзу й автономії", size=14, color=FIELD, bold=True))
    p.append(text(425, 62, "Фільтрація, правила, черга SQLite", size=11, color=MUTED))

    # Права зона: Northbound (Висхідний контур)
    p.append(rect(600, 20, 220, 480, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(710, 45, "Висхідний контур (Northbound)", size=13, color=NEG, bold=True))
    p.append(text(710, 62, "WAN / Хмара / MQTT Брокер", size=11, color=MUTED))

    # Блоки Southbound
    p.append(fitbox(35, 85, 200, 65, "RS-485 / Modbus RTU\nВитратоміри, ПЛК, приводи", size=12, fill="#eef2f6", stroke=LINE))
    p.append(fitbox(35, 165, 200, 65, "LoRaWAN Concentrator\nSX1302 · Бездротові давачі", size=12, fill="#eef2f6", stroke=LINE))
    p.append(fitbox(35, 245, 200, 65, "BLE / Zigbee Coordinator\nКліматичні мікросенсори", size=12, fill="#eef2f6", stroke=LINE))
    p.append(fitbox(35, 335, 200, 65, "Локальні АЦП / GPIO\nСухі контакти, струмові петлі", size=12, fill="#eef2f6", stroke=LINE))
    p.append(fitbox(35, 420, 200, 65, "Аварійні реле / Приводи\nКлапани відсікання, сирени", size=12, fill="#fdecea", stroke=POS, bold=True))

    # Стрілки від Southbound в Ingestion Pipeline
    p.append(arrow(235, 117, 285, 117, color=LINE, sw=1.5))
    p.append(arrow(235, 197, 285, 140, color=LINE, sw=1.5))
    p.append(arrow(235, 277, 285, 160, color=LINE, sw=1.5))
    p.append(arrow(235, 367, 285, 180, color=LINE, sw=1.5))

    # Центральні блоки
    # 1. Ingestion Pipeline
    p.append(fitbox(285, 85, 280, 110, "Конвеєр первинної обробки\n· Десеріалізація та мічення часу RTC\n· Апертурна фільтрація (Deadband)\n· Фільтрація викидів (Sanity Check)\n· Віконна агрегація (Avg, Min, Max)", size=11, fill="#f4f6f8", stroke=LINE))

    # 2. Local Rule Engine (Fast-Path)
    p.append(fitbox(285, 215, 280, 105, "Локальний рушій правил (Rule Engine)\n· Таблиця стану об'єкта в пам'яті\n· Перевірка порогових аварій (<1 мс)\n· Гістерезис і таймери захисту", size=11, fill="#eafaf0", stroke=FIELD, bold=True))

    # Стрілка від Ingestion до Rule Engine
    p.append(arrow(425, 195, 425, 215, color=FIELD, sw=2))

    # Зворотна лінія швидкого реагування від Rule Engine до Аварійних приводів
    p.append(line(285, 280, 252, 280, color=POS, sw=2))
    p.append(line(252, 280, 252, 452, color=POS, sw=2))
    p.append(arrow(252, 452, 235, 452, color=POS, sw=2))
    p.append(text(252, 350, "Аварія (<1 мс)", size=10, color=POS, bold=True, anchor="middle"))

    # 3. Store-and-Forward Queue (SQLite WAL / Flash)
    p.append(fitbox(285, 340, 280, 135, "Сховище Store-and-Forward\n· SQLite у режимі WAL (Flash Safe)\n· Черга повідомлень із пріоритетами\n· Політика витіснення телеметрії\n· Автономний буфер на дні блекауту", size=11, fill="#fff7e6", stroke="#b8860b", bold=True))

    # Стрілка від Rule Engine до Store-and-Forward
    p.append(arrow(425, 320, 425, 340, color=LINE, sw=1.5))

    # Блоки Northbound
    p.append(fitbox(615, 85, 190, 85, "Агент синхронізації WAN\n· Автомат стану з'єднання\n· Порційний злив черги (Drain)\n· Обмеження швидкості (Rate limit)", size=11, fill="#eaf0fd", stroke=NEG, bold=True))
    p.append(fitbox(615, 195, 190, 85, "Транспортний рівень\n· TLS 1.3 / mTLS шифрування\n· MQTT v3.1.1 / v5.0 Client\n· Стільниковий 4G/LTE / Ethernet", size=11, fill="#eef2f6", stroke=LINE))
    p.append(fitbox(615, 310, 190, 95, "Хмарна платформа / SCADA\n· Брокер повідомлень MQTT\n· База часових рядів (TSDB)\n· Моніторинг та аналітика", size=11, fill="#f4f6f8", stroke=MUTED))
    p.append(fitbox(615, 420, 190, 65, "Зворотні команди\n· Уставки та дистанційні накази\n(Підпорядковані локальному захисту)", size=10, fill="#fdecea", stroke=POS))

    # Стрілки між Core та Northbound
    p.append(arrow(565, 400, 615, 140, color=NEG, sw=2))
    p.append(arrow(710, 170, 710, 195, color=NEG, sw=1.5))
    p.append(arrow(710, 280, 710, 310, color=NEG, sw=1.5))
    p.append(arrow(615, 452, 565, 275, color=POS, sw=1.5))

    render(os.path.join(IMG, 'gateway-architecture.svg'), W, H, *p,
           title="Архітектура автономного IoT-шлюзу")


def fig_store_forward_lifecycle():
    W, H = 820, 430
    p = []

    # 4 стани автомата синхронізації
    y_states = 95
    p.append(fitbox(30, y_states, 170, 70, "1. ONLINE STREAMING\nПряма трансляція в MQTT\nЧерга порожня, нульова затримка", size=11, fill="#eafaf0", stroke=FIELD, bold=True))
    p.append(fitbox(230, y_states, 170, 70, "2. OFFLINE BUFFERING\nВисхідний канал обірвано\nЗапис у SQLite WAL на Flash", size=11, fill="#fdecea", stroke=POS, bold=True))
    p.append(fitbox(430, y_states, 170, 70, "3. WAN RECOVERING\nЗв'язок відновився\nРукостискання TLS + MQTT", size=11, fill="#fff7e6", stroke="#b8860b", bold=True))
    p.append(fitbox(630, y_states, 170, 70, "4. DRAINING SYNC\nПорційний злив черги\nКонтроль темпу й підтверджень", size=11, fill="#eaf0fd", stroke=NEG, bold=True))

    # Переходи між станами
    # 1 -> 2 (обрив зв'язку)
    p.append(arrow(200, 115, 230, 115, color=POS, sw=2))
    p.append(text(215, 105, "Обрив WAN", size=9, color=POS, bold=True))

    # 2 -> 3 (відновлення мережі)
    p.append(arrow(400, 115, 430, 115, color="#b8860b", sw=2))
    p.append(text(415, 105, "Link Up", size=9, color="#b8860b", bold=True))

    # 3 -> 4 (успішне підключення до брокера)
    p.append(arrow(600, 115, 630, 115, color=NEG, sw=2))
    p.append(text(615, 105, "MQTT Conn", size=9, color=NEG, bold=True))

    # 4 -> 1 (черга повністю вичерпана)
    p.append(line(715, 165, 715, 200, color=FIELD, sw=2))
    p.append(line(715, 200, 115, 200, color=FIELD, sw=2))
    p.append(arrow(115, 200, 115, 165, color=FIELD, sw=2))
    p.append(text(415, 192, "Черга вичерпана (Queue Empty) → повернення до прямої трансляції", size=11, color=FIELD, bold=True))

    # Повторний обрив під час зливу (4 -> 2)
    p.append(line(700, 95, 700, 60, color=POS, sw=1.5, dash="4 3"))
    p.append(line(700, 60, 315, 60, color=POS, sw=1.5, dash="4 3"))
    p.append(arrow(315, 60, 315, 95, color=POS, sw=1.5))
    p.append(text(510, 52, "Повторний обрив WAN під час зливу", size=10, color=POS))

    # Нижній пояс: структура транзакційного зливу (Batch Drain Pipeline)
    y_drain = 235
    p.append(rect(30, y_drain, 760, 175, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(410, y_drain + 25, "Механізм порційного зливу (Batch Drain) без перевантаження мережі", size=13, color=INK, bold=True))

    p.append(fitbox(50, y_drain + 45, 210, 105, "1. Вибірка пачки (Batch SELECT)\n`SELECT * FROM queue`\n`ORDER BY priority DESC, id ASC`\n`LIMIT 50;`", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(260, y_drain + 97, 290, 97, color=LINE, sw=1.5))

    p.append(fitbox(290, y_drain + 45, 220, 105, "2. Публікація в MQTT (QoS 1)\nВідправка з оригінальною\nміткою часу вимірювання\n`sampled_at: 1724700000`", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(510, y_drain + 97, 540, 97, color=LINE, sw=1.5))

    p.append(fitbox(540, y_drain + 45, 230, 105, "3. Атомарне видалення (DELETE)\nОтримано `PUBACK` від брокера:\n`DELETE FROM queue`\n`WHERE id IN (пачка_id);`", size=11, fill="#eafaf0", stroke=FIELD, bold=True))

    render(os.path.join(IMG, 'store-forward-lifecycle.svg'), W, H, *p,
           title="Життєвий цикл механізму Store-and-Forward")


def fig_emergency_rule_pipeline():
    W, H = 820, 440
    p = []

    # Верхній контур: Швидкий локальний аварійний шлях (Local Fast-Path)
    y_fast = 50
    p.append(rect(20, y_fast, 780, 170, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(text(410, y_fast + 25, "Локальний аварійний контур (Fast-Path) — детермінована реакція < 1 мс", size=13, color=POS, bold=True))

    p.append(fitbox(40, y_fast + 45, 155, 95, "Сирий вхідний кадр\nDMA переривання UART\nабо SPI LoRa пакета", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(195, y_fast + 92, 230, 92, color=POS, sw=2))

    p.append(fitbox(230, y_fast + 45, 175, 95, "Оновлення стану\nЗапис у таблицю\nзначень у RAM", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(405, y_fast + 92, 440, 92, color=POS, sw=2))

    p.append(fitbox(440, y_fast + 45, 175, 95, "Rule Engine\n`T > 95°C || P > 6 bar`\nМиттєвий розрахунок", size=11, fill="#ffffff", stroke=POS, bold=True))
    p.append(arrow(615, y_fast + 92, 645, 92, color=POS, sw=2))

    p.append(fitbox(645, y_fast + 45, 140, 95, "Захисна дія\nGPIO клапана,\nвимикання котла", size=11, fill="#c0392b", stroke="#962d22", color="#ffffff", bold=True))

    # Нижній контур: Повільний висхідний хмарний шлях (Cloud Async Loop)
    y_slow = 250
    p.append(rect(20, y_slow, 780, 170, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(410, y_slow + 25, "Хмарний контур моніторингу — непередбачувана затримка (200 мс — обрив каналу)", size=13, color=MUTED, bold=True))

    # Стрілка вниз від Ingestion до буферизації
    p.append(arrow(317, y_fast + 140, 317, y_slow + 45, color=MUTED, sw=1.5))
    p.append(text(325, 235, "Асинхронно", size=10, color=MUTED, anchor="start"))

    p.append(fitbox(230, y_slow + 45, 175, 95, "Буфер SQLite WAL\nЗбереження для\nхмарної аналітики", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(405, y_slow + 92, 440, 92, color=MUTED, sw=1.5))

    p.append(fitbox(440, y_slow + 45, 175, 95, "WAN / 4G / Wi-Fi\nПередача через TCP/IP\n(ризик втрати зв'язку)", size=11, fill="#ffffff", stroke=LINE))
    p.append(arrow(615, y_slow + 92, 645, 92, color=MUTED, sw=1.5))

    p.append(fitbox(645, y_slow + 45, 140, 95, "Хмарний сервер\nАналітика, графіки,\nдовгострокові тренди", size=11, fill="#ffffff", stroke=MUTED))

    # Підсумок у центрі
    p.append(text(120, y_slow + 92, "Безпека не чекає\nхмару", size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'emergency-rule-pipeline.svg'), W, H, *p,
           title="Розділення локального аварійного контуру та висхідного моніторингу")


def fig_protocol_translation_flow():
    W, H = 820, 450
    p = []

    # Верхня половина: Modbus RTU -> MQTT JSON
    y_mb = 35
    p.append(rect(20, y_mb, 780, 190, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, y_mb + 22, "1. Трансляція Modbus RTU (RS-485) → MQTT JSON", size=13, color=INK, bold=True))

    # Сирі байти Modbus
    p.append(fitbox(35, y_mb + 40, 210, 125, "Сирий кадр Modbus RTU\n`0x01 0x03 0x04`\n`0x42 0x88 0x00 0x00`\n`0x6E 0x92`\n(Slave 1, Func 3, 4 байти, CRC)", size=10, fill="#eef2f6", stroke=LINE))
    p.append(arrow(245, y_mb + 102, 280, 102, color=LINE, sw=1.5))

    # Етап обробки в шлюзі
    p.append(fitbox(280, y_mb + 40, 240, 125, "Шлюзовий дескриптор пристрою\n· Перевірка CRC16 (OK)\n· Мапінг: Reg 40001-40002\n· Word Swap (IEEE 754 Float32)\n→ `value = 68.0 bar`\n· Мітка RTC: `1724698800`", size=10, fill="#ffffff", stroke=FIELD, bold=True))
    p.append(arrow(520, y_mb + 102, 555, 102, color=LINE, sw=1.5))

    # Вихідний MQTT JSON
    p.append(fitbox(555, y_mb + 40, 230, 125, "MQTT Топік & JSON Payload\n`plant/boiler_1/pressure`\n{\n  \"val\": 68.0,\n  \"unit\": \"bar\",\n  \"ts\": 1724698800\n}", size=10, fill="#eafaf0", stroke=FIELD))

    # Нижня половина: LoRaWAN Payload -> MQTT JSON
    y_lora = 240
    p.append(rect(20, y_lora, 780, 190, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, y_lora + 22, "2. Трансляція LoRaWAN Бінарного пакета → MQTT JSON", size=13, color=INK, bold=True))

    # Сирі байти LoRaWAN
    p.append(fitbox(35, y_lora + 40, 210, 125, "Сирий радіопакет LoRaWAN\nDevAddr: `0x26012A34`\nFPort: `2`\nPayload: `0x01 0x67 0x01 0x1A`\n`0x02 0x68 0x78`\n(Cayenne LPP формат)", size=10, fill="#eef2f6", stroke=LINE))
    p.append(arrow(245, y_lora + 102, 280, 102, color=LINE, sw=1.5))

    # Етап обробки в шлюзі
    p.append(fitbox(280, y_lora + 40, 240, 125, "Декодер корисного навантаження\n· Перевірка MIC та лічильника FCnt\n· Канал 1: Temp (0x011A / 10 = 28.2°C)\n· Канал 2: Hum (0x78 / 2 = 60.0%)\n· Метрики радіо: RSSI -85, SNR +9\n· Апаратна мітка часу RTC", size=10, fill="#ffffff", stroke=NEG, bold=True))
    p.append(arrow(520, y_lora + 102, 555, 102, color=LINE, sw=1.5))

    # Вихідний MQTT JSON
    p.append(fitbox(555, y_lora + 40, 230, 125, "MQTT Топік & JSON Payload\n`farm/greenhouse/node_34/env`\n{\n  \"temp\": 28.2,\n  \"hum\": 60.0,\n  \"rssi\": -85,\n  \"ts\": 1724698800\n}", size=10, fill="#eaf0fd", stroke=NEG))

    render(os.path.join(IMG, 'protocol-translation-flow.svg'), W, H, *p,
           title="Трансляція різнорідних протоколів у структуровані MQTT повідомлення")


def main():
    fig_gateway_architecture()
    fig_store_forward_lifecycle()
    fig_emergency_rule_pipeline()
    fig_protocol_translation_flow()
    print("All figures generated successfully.")


if __name__ == '__main__':
    main()
