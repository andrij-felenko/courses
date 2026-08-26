# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Версії: пристрій, старший за сервер»."""

import os
import sys

# Додаємо scripts/ до шляху для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, text, mtext, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_lifecycle_divergence():
    """Фігура 1: Прірва життєвого циклу між замороженим пристроєм та еволюцією хмари."""
    w, h = 820, 390
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Прірва життєвого циклу: 15 років еволюції сервера проти замороженого пристрою", size=15, bold=True))

    # Вісь часу посередині
    y_axis = 185
    frags.append(line(50, y_axis, 760, y_axis, color=LINE, sw=2))
    # Стрілка на осі
    frags.append(arrow(740, y_axis, 770, y_axis, color=LINE, sw=2))
    frags.append(text(775, y_axis + 4, "Час", size=12, bold=True, anchor="start"))

    years = [
        (100, "2012 р.", "Розгортання"),
        (280, "2017 р.", "+5 років"),
        (480, "2022 р.", "+10 років"),
        (680, "2027 р.", "+15 років")
    ]

    for x_pos, yr_label, delta_label in years:
        frags.append(circle(x_pos, y_axis, 4, fill=LINE, stroke=LINE))
        frags.append(text(x_pos, y_axis - 10, yr_label, size=12, bold=True))
        frags.append(text(x_pos, y_axis + 16, delta_label, size=11, color=MUTED))

    # Верхня зона: Хмарний бекенд (Швидка еволюція кожні 1-2 роки)
    frags.append(rect(40, 48, 740, 100, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(55, 68, "Еволюція серверної частини (Хмара / Бекенд v1.0 → v5.0)", size=13, color=NEG, bold=True, anchor="start"))

    # Етапи сервера
    s1, _, _ = textbox(120, 110, "TLS 1.0 / 1.1\nRSA 1024 / SHA-1\nМоноліт / REST v1", size=10, fill="#ffffff", stroke=MUTED, pad=5)
    s2, _, _ = textbox(300, 110, "TLS 1.2 обов'язковий\nAPI v2.0 / JSON Schema\nМікросервіси", size=10, fill="#ffffff", stroke=MUTED, pad=5)
    s3, _, _ = textbox(500, 110, "Закінчення Root CA\nTLS 1.3 / ECC P-256\nKafka / Event Bus", size=10, fill="#fff1f0", stroke=POS, pad=5)
    s4, _, _ = textbox(690, 110, "Zero-Trust mTLS\nProtobuf / API v5.0\nTLS 1.0/1.1 заборонено", size=10, fill="#ffffff", stroke=MUTED, pad=5)
    frags.extend([s1, s2, s3, s4])

    # Нижня зона: Польовий пристрій (Заморожений стан на 15 років)
    frags.append(rect(40, 230, 740, 135, fill="#fffbf0", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(55, 252, "Польовий пристрій v1.0 (Газовий/водяний лічильник, автономний трекер)", size=13, color="#b45309", bold=True, anchor="start"))

    d1, _, _ = textbox(130, 310, "Заводська прошивка v1.0\nБатарея Li-SOCl2 на 15 р.\nЗашито Root CA 2012 р.", size=10, fill="#ffffff", stroke="#d97706", pad=5)
    d2, _, _ = textbox(360, 310, "Метрологічна пломба MID\nFlash 32 KB / RAM 4 KB\nOTA неможливе / заборонене", size=10, fill="#ffffff", stroke="#d97706", pad=5)
    d3, _, _ = textbox(630, 310, "Криза 2027 року:\n• Сертифікат CA прострочено\n• Шифри TLS відкинуто шлюзом\n• Формат пакетів v1 не знає API v5", size=10, fill="#fee2e2", stroke=POS, pad=5)
    frags.extend([d1, d2, d3])

    # Зв'язки-стрілки між етапами
    frags.append(line(630, 275, 690, 150, color=POS, sw=1.8, dash="4,3"))
    frags.append(text(670, 205, "Несумісність!", size=11, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "lifecycle-divergence.svg"), w, h, *frags)


def fig_security_termination_barrier():
    """Фігура 2: Шлюз сумісності та ізоляція застарілих протоколів (Legacy Ingestion Proxy)."""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 26, "Архітектура адаптера сумісності: ізоляція легасі-периметра від сучасного ядра", size=15, bold=True))

    # Зона 1: Поле (Старий парк)
    frags.append(rect(30, 55, 185, 340, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(122, 80, "Старий парк v1.0", size=13, bold=True))
    frags.append(text(122, 98, "Лічильники 2012–2015 рр.", size=10, color=MUTED))

    p1, _, _ = textbox(122, 145, "Промисловий лічильник\n• Raw TCP / Бінарний кадр\n• Статичний ключ PSK", size=9.5, fill="#ffffff", stroke=MUTED, pad=5)
    p2, _, _ = textbox(122, 230, "Газовий датчик RTU\n• TLS 1.0 / Старий CA\n• Застарілі шифри RSA", size=9.5, fill="#ffffff", stroke=MUTED, pad=5)
    p3, _, _ = textbox(122, 315, "Автономний трекер\n• HTTP 1.0 GET телеметрія\n• 1 вихід на зв'язок/добу", size=9.5, fill="#ffffff", stroke=MUTED, pad=5)
    frags.extend([p1, p2, p3])

    # Зона 2: Демілітаризована зона / Ingestion Proxy (Центр)
    frags.append(rect(245, 55, 350, 340, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(420, 80, "Адаптер сумісності (Legacy Proxy)", size=13, color=NEG, bold=True))
    frags.append(text(420, 98, "Ізольований периметр прийому трафіку", size=10, color=MUTED))

    t1, _, _ = textbox(420, 135, "1. Термінація безпеки\nТермінація застарілого TLS 1.0/1.1 / перевірка PSK HMAC", size=9.5, fill="#ffffff", stroke=NEG, pad=5)
    t2, _, _ = textbox(420, 195, "2. Розбір і валідація кадрів\nПеревірка CRC16/32, вилучення полів бінарного протоколу", size=9.5, fill="#ffffff", stroke=NEG, pad=5)
    t3, _, _ = textbox(420, 255, "3. Збагачення та нормалізація\nПерерахунок імпульсів у СІ, вирівнювання часу, каталог приладів", size=9.5, fill="#ffffff", stroke=NEG, pad=5)
    t4, _, _ = textbox(420, 315, "4. Генератор зворотних команд\nТрансляція наказів v5 → бінарний формат v1", size=9.5, fill="#ffffff", stroke=NEG, pad=5)
    frags.extend([t1, t2, t3, t4])

    # Зона 3: Сучасне ядро (Бекенд v5.0)
    frags.append(rect(625, 55, 185, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(717, 80, "Сучасне ядро v5.0", size=13, color=FIELD, bold=True))
    frags.append(text(717, 98, "Хмарні мікросервіси", size=10, color=MUTED))

    k1, _, _ = textbox(717, 145, "Шина подій\n• Kafka / NATS / RabbitMQ\n• Канонічні CloudEvents", size=9.5, fill="#ffffff", stroke=FIELD, pad=5)
    k2, _, _ = textbox(717, 230, "Сховище Time-Series\n• Нормалізовані дані в СІ\n• UTC мікросекунди", size=9.5, fill="#ffffff", stroke=FIELD, pad=5)
    k3, _, _ = textbox(717, 315, "Бізнес-логіка v5.0\n• Білінг, аномалії\n• Не знає про біти v1.0", size=9.5, fill="#ffffff", stroke=FIELD, pad=5)
    frags.extend([k1, k2, k3])

    # Стрілки передачі
    frags.append(arrow(215, 145, 243, 145, color=MUTED, sw=2))
    frags.append(arrow(215, 230, 243, 230, color=MUTED, sw=2))
    frags.append(arrow(215, 315, 243, 315, color=MUTED, sw=2))

    frags.append(arrow(595, 145, 623, 145, color=FIELD, sw=2))
    frags.append(arrow(595, 230, 623, 230, color=FIELD, sw=2))
    frags.append(arrow(623, 315, 595, 315, color=NEG, sw=1.8))

    render(os.path.join(IMG_DIR, "security-termination-barrier.svg"), w, h, *frags)


def fig_schema_evolution_pipeline():
    """Фігура 3: Пайплайн нормалізації бінарного кадру v1.0 у канонічний JSON/Event v5.0."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Нормалізація даних: перетворення сирого бінарного кадру v1.0 на канонічну подію v5.0", size=15, bold=True))

    # Крок 1: Сирий бінарний пакет v1.0
    frags.append(rect(30, 60, 220, 265, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(140, 85, "1. Сирий бінарний кадр v1.0", size=12, bold=True))
    frags.append(text(140, 102, "16 байтів у мережевому порядку", size=10, color=MUTED))

    raw_frame_text = (
        "0xAA [Преамбула: 1B]\n"
        "0x01 [Версія: 1B]\n"
        "0x00 0x1A 0x8C 0x04 [ID: 4B]\n"
        "0x00 0x42 [Seq: 2B]\n"
        "0x00 0x03 0x2A 0x10 [Імпульси: 4B]\n"
        "0xD8 [Батарея 0..255: 1B]\n"
        "0x01 [Статус / Тривога: 1B]\n"
        "0x8E 0x2A [CRC16-CCITT: 2B]"
    )
    b1, _, _ = textbox(140, 210, raw_frame_text, size=9.5, fill="#ffffff", stroke=MUTED, pad=5)
    frags.append(b1)

    # Стрілка між кроками 1 і 2
    frags.append(arrow(252, 190, 280, 190, color=LINE, sw=2))

    # Крок 2: Шлюзова трансформація та збагачення
    frags.append(rect(282, 60, 245, 265, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(404, 85, "2. Збагачення та перерахунок", size=12, color=NEG, bold=True))
    frags.append(text(404, 102, "Логіка адаптера сумісності", size=10, color=MUTED))

    trans_text = (
        "• Перевірка CRC16 == OK\n"
        "• Пошук у Device Registry:\n"
        "   - Коефіцієнт: 0.01 м³/імп.\n"
        "   - Базова дата: 2012-01-01\n"
        "   - Локація: Сектор 4\n"
        "• Перерахунок величин:\n"
        "   207376 імп. × 0.01 = 2073.76 м³\n"
        "• Напруга живлення:\n"
        "   0xD8 (216) → 3.60 В (94%)\n"
        "• Відновлення UTC часу:\n"
        "   Seq + серверний прийом"
    )
    b2, _, _ = textbox(404, 210, trans_text, size=9.5, fill="#ffffff", stroke=NEG, pad=5)
    frags.append(b2)

    # Стрілка між кроками 2 і 3
    frags.append(arrow(529, 190, 557, 190, color=FIELD, sw=2))

    # Крок 3: Канонічна подія v5.0
    frags.append(rect(559, 60, 230, 265, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(674, 85, "3. Канонічний JSON v5.0", size=12, color=FIELD, bold=True))
    frags.append(text(674, 102, "Єдина модель для всіх систем", size=10, color=MUTED))

    json_text = (
        "{\n"
        '  "device_id": "MTR-1739780",\n'
        '  "schema_version": 5,\n'
        '  "timestamp": "2027-08-26T16:30Z",\n'
        '  "reading": {\n'
        '    "volume_m3": 2073.76,\n'
        '    "unit": "CUBIC_METER"\n'
        "  },\n"
        '  "diagnostics": {\n'
        '    "battery_v": 3.60,\n'
        '    "tamper": true\n'
        "  },\n"
        '  "adapter": "legacy_bin_v1"\n'
        "}"
    )
    b3, _, _ = textbox(674, 210, json_text, size=9.5, fill="#ffffff", stroke=FIELD, pad=5)
    frags.append(b3)

    render(os.path.join(IMG_DIR, "schema-evolution-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_lifecycle_divergence()
    fig_security_termination_barrier()
    fig_schema_evolution_pipeline()
    print("All figures generated successfully.")
