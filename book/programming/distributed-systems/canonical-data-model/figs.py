# -*- coding: utf-8 -*-
"""Фігури до теми «Канонічна модель даних» (Canonical Data Model)."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / спагеті / legacy
COOL = "#eaf0fd"   # нейтральне / формати / адаптери
GOOD = "#e8f6ee"   # успіх / канонічна модель / чистота
WARN = "#fef9e7"   # застереження / метадані
PANEL = "#f8fafc"  # фон підпанелей


# ── 1. Анатомія канонічного повідомлення та адаптерів ───────────────────────
def cdm_architecture_layers():
    W, H = 1240, 560
    f = []

    # Загальний заголовок і контейнер
    f.append(rect(20, 20, 1200, 520, fill=FILL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(620, 50, "Анатомія Канонічної Моделі Даних (CDM)", size=16, bold=True, color=INK))
    f.append(text(620, 72, "Розділення метаданих конверта, типізованого доменного тіла та антикорупційних адаптерів", size=12, color=MUTED))

    # Ліва колонка: Різнорідні джерела (Inbound Sources)
    f.append(rect(35, 95, 230, 425, fill=PANEL, stroke=LINE, sw=1.1, rx=8))
    f.append(text(150, 120, "Системи-джерела", size=13, bold=True, color=INK))
    f.append(text(150, 138, "Власні локальні формати", size=10.5, color=MUTED))

    sources = [
        ("Web API (JSON / CamelCase)", 180, COOL),
        ("Legacy ERP (SOAP / XML)", 270, WARM),
        ("Партнер (EDIFACT / Flat)", 360, WARN),
        ("IoT Edge (CBOR / Binary)", 450, COOL),
    ]
    for sname, sy, sfill in sources:
        f.append(rect(50, sy - 20, 200, 42, fill=sfill, stroke=LINE, sw=1.2, rx=6))
        f.append(text(150, sy + 5, sname, size=10.5, bold=True, color=INK))

    # Колонка вхідних трансляторів (Inbound Translators / ACL)
    f.append(rect(280, 95, 175, 425, fill=PANEL, stroke=LINE, sw=1.1, rx=8))
    f.append(text(367, 120, "Вхідні адаптери (ACL)", size=13, bold=True, color=POS))
    f.append(text(367, 138, "Нормалізація до CDM", size=10.5, color=MUTED))

    for _, sy, _ in sources:
        f.append(arrow(250, sy + 1, 295, sy + 1, color=POS, sw=1.5))
        f.append(rect(295, sy - 20, 145, 42, fill=WARM, stroke=POS, sw=1.2, rx=6))
        f.append(text(367, sy - 3, "Inbound Translator", size=10.5, bold=True, color=POS))
        f.append(text(367, sy + 12, "Синтаксис → CDM", size=9.5, color=MUTED))
        f.append(arrow(440, sy + 1, 475, 310, color=FIELD, sw=1.5))

    # Центральний блок: Канонічне повідомлення (Canonical Message)
    f.append(rect(475, 95, 290, 425, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(text(620, 120, "КАНОНІЧНИЙ КОНВЕРТ (CDM)", size=13.5, bold=True, color=FIELD))
    f.append(text(620, 138, "Єдиний бізнес-контракт шини", size=10.5, color=MUTED))

    # Блок метаданих (Envelope Headers)
    f.append(rect(490, 155, 260, 130, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(620, 175, "Канонічні метадані (Headers)", size=11.5, bold=True, color=FIELD))
    f.append(text(500, 198, "• message_id: UUIDv7", size=10, color=INK, anchor="start"))
    f.append(text(500, 216, "• correlation_id: UUIDv4", size=10, color=INK, anchor="start"))
    f.append(text(500, 234, "• schema_version: \"2.4.0\"", size=10, color=INK, anchor="start"))
    f.append(text(500, 252, "• timestamp_utc: 1787220000000", size=10, color=INK, anchor="start"))
    f.append(text(500, 270, "• bounded_context: \"Billing\"", size=10, color=INK, anchor="start"))

    # Блок канонічного тіла (Canonical Payload)
    f.append(rect(490, 295, 260, 155, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(620, 315, "Канонічне тіло (Canonical Payload)", size=11.5, bold=True, color=FIELD))
    f.append(text(500, 338, "• order_id: \"ORD-88219\"", size=10, color=INK, anchor="start"))
    f.append(text(500, 356, "• customer_id: \"CUST-4091\"", size=10, color=INK, anchor="start"))
    f.append(text(500, 374, "• total_amount_cents: 19990", size=10, color=INK, anchor="start"))
    f.append(text(500, 392, "• currency: Currency::UAH", size=10, color=INK, anchor="start"))
    f.append(text(500, 410, "• status: OrderStatus::PAID", size=10, color=INK, anchor="start"))
    f.append(text(500, 428, "• line_items: [ { sku, qty, price } ]", size=10, color=INK, anchor="start"))

    f.append(fitbox(490, 460, 260, 50,
                    "Strict Typing • ISO Dates • Cents Money\nSemantics Locked to Ubiquitous Language",
                    size=9.5, fill=GOOD, stroke=FIELD, sw=1))

    # Колонка вихідних трансляторів (Outbound Translators)
    f.append(rect(785, 95, 175, 425, fill=PANEL, stroke=LINE, sw=1.1, rx=8))
    f.append(text(872, 120, "Вихідні адаптери (ACL)", size=13, bold=True, color=NEG))
    f.append(text(872, 138, "Проекція з CDM назовні", size=10.5, color=MUTED))

    targets = [
        ("Склад (Protobuf / gRPC)", 180, COOL),
        ("Логістика (JSON API)", 270, COOL),
        ("Аналітика (Apache Avro)", 360, GOOD),
        ("Податкова (XML / ДПС)", 450, WARN),
    ]

    for _, ty, _ in targets:
        f.append(arrow(765, 310, 800, ty + 1, color=FIELD, sw=1.5))
        f.append(rect(800, ty - 20, 145, 42, fill=COOL, stroke=NEG, sw=1.2, rx=6))
        f.append(text(872, ty - 3, "Outbound Translator", size=10.5, bold=True, color=NEG))
        f.append(text(872, ty + 12, "CDM → Цільовий", size=9.5, color=MUTED))
        f.append(arrow(945, ty + 1, 985, ty + 1, color=NEG, sw=1.5))

    # Права колонка: Системи-одержувачі (Outbound Consumers)
    f.append(rect(980, 95, 235, 425, fill=PANEL, stroke=LINE, sw=1.1, rx=8))
    f.append(text(1097, 120, "Системи-споживачі", size=13, bold=True, color=INK))
    f.append(text(1097, 138, "Очікують свій формат", size=10.5, color=MUTED))

    for tname, ty, tfill in targets:
        f.append(rect(995, ty - 20, 205, 42, fill=tfill, stroke=LINE, sw=1.2, rx=6))
        f.append(text(1097, ty + 5, tname, size=10.5, bold=True, color=INK))

    render(os.path.join(OUT, 'cdm-architecture-layers.svg'), W, H, *f)


# ── 2. Глобальна монолітна CDM vs Федеративна CDM (DDD) ─────────────────────
def global_vs_federated_cdm():
    W, H = 1200, 560
    f = []

    f.append(rect(20, 20, 1160, 520, fill=FILL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(600, 48, "Еволюція концепції: Глобальна EDM vs Федеративна CDM", size=16, bold=True, color=INK))
    f.append(text(600, 70, "Чому єдина мегасхема підприємства зазнала краху і як DDD Bounded Contexts врятували інтеграцію", size=11.5, color=MUTED))

    # Ліва частина: Глобальна модель 2000-х (ESB Anti-Pattern)
    f.append(rect(35, 95, 545, 430, fill=PANEL, stroke=POS, sw=1.3, rx=8))
    f.append(text(307, 122, "Глобальна корпоративна модель (ESB 2000-х)", size=13.5, bold=True, color=POS))
    f.append(text(307, 142, "Антипатерн: «Одна універсальна схема для всієї корпорації»", size=10.5, color=MUTED))

    # Центр лівої частини: Гігантська монолітна схема
    f.append(rect(195, 168, 225, 95, fill=WARM, stroke=POS, sw=1.8, rx=8))
    f.append(text(307, 192, "Enterprise Mega-Schema", size=12.5, bold=True, color=POS))
    f.append(text(307, 212, "(800+ полів, 50 рівнів XML)", size=10.5, color=INK))
    f.append(text(307, 230, "«Customer», «Order», «Invoice»", size=10, italic=True, color=MUTED))
    f.append(text(307, 248, "Комітет стандартизації (місяці)", size=10, bold=True, color=POS))

    # Сервіси навколо з конфліктами
    services_left = [
        ("Продажі (CRM)", 95, 305),
        ("Бухгалтерія (ERP)", 235, 305),
        ("Логістика (WMS)", 375, 305),
        ("Підтримка", 515, 305),
    ]
    for sname, sx, sy in services_left:
        f.append(rect(sx - 50, sy - 18, 100, 36, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
        f.append(text(sx, sy + 4, sname, size=9.5, bold=True, color=INK))
        f.append(arrow(sx, sy - 18, 307, 263, color=POS, sw=1.2))

    f.append(fitbox(50, 355, 515, 155,
                    "НАСЛІДКИ МОНОЛІТНОЇ CDM:\n"
                    "1. Організаційне блокування: будь-яка зміна узгоджується місяцями всіма відділами.\n"
                    "2. Семантичний розрив: сутність «Клієнт» означає діаметрально різні речі в CRM і WMS.\n"
                    "3. Найменший спільний знаменник або монстр: 90% полів схеми є порожніми (null).\n"
                    "4. Крихкість: зміна версії ламає десятки інтегрованих систем одночасно.",
                    size=10.5, fill=WARM, stroke=POS, sw=1.1))

    # Права частина: Федеративна CDM (DDD Bounded Contexts)
    f.append(rect(615, 95, 550, 430, fill=PANEL, stroke=FIELD, sw=1.3, rx=8))
    f.append(text(890, 122, "Федеративна CDM (DDD Bounded Contexts)", size=13.5, bold=True, color=FIELD))
    f.append(text(890, 142, "Сучасний підхід: Published Language на межах контекстів", size=10.5, color=MUTED))

    # Окремі обмежені контексти
    contexts = [
        ("Sales Context", 720, 190, "Canonical Lead / Quote", COOL),
        ("Billing Context", 1020, 190, "Canonical Invoice / Payer", GOOD),
        ("Shipping Context", 720, 280, "Canonical Waybill / Cargo", WARN),
        ("Analytics Context", 1020, 280, "Canonical Fact Event", COOL),
    ]
    for cname, cx, cy, cmodel, cfill in contexts:
        f.append(rect(cx - 85, cy - 25, 170, 52, fill=cfill, stroke=FIELD, sw=1.4, rx=6))
        f.append(text(cx, cy - 6, cname, size=11, bold=True, color=INK))
        f.append(text(cx, cy + 14, cmodel, size=9.5, italic=True, color=MUTED))

    # Зв'язки між контекстами через ACL / Published Language
    f.append(line(720, 216, 720, 255, color=FIELD, sw=1.5))
    f.append(line(1020, 216, 1020, 255, color=FIELD, sw=1.5))
    f.append(line(805, 190, 935, 190, color=FIELD, sw=1.5))
    f.append(line(805, 280, 935, 280, color=FIELD, sw=1.5))

    # Плашка антикорупційного шару
    f.append(rect(820, 222, 100, 28, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(870, 240, "ACL / OHS", size=10, bold=True, color=FIELD))

    f.append(fitbox(630, 355, 520, 155,
                    "ПЕРЕВАГИ ФЕДЕРАТИВНОЇ CDM:\n"
                    "1. Автономність команд: кожен Bounded Context володіє власною моделлю та схемою.\n"
                    "2. Точна семантика: чиста єдина мова (Ubiquitous Language) всередині контексту.\n"
                    "3. Антикорупційний шар (ACL): захищає ядро домену від брудних зовнішніх контрактів.\n"
                    "4. Published Language: публічний канонічний API/події для взаємодії між доменами.",
                    size=10.5, fill=GOOD, stroke=FIELD, sw=1.1))

    render(os.path.join(OUT, 'global-vs-federated-cdm.svg'), W, H, *f)


# ── 3. Конвеєр обробки канонічного повідомлення ──────────────────────────────
def cdm_transformation_pipeline():
    W, H = 1200, 520
    f = []

    f.append(rect(20, 20, 1160, 480, fill=FILL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(600, 48, "Конвеєр канонічної трансформації та валідації", size=16, bold=True, color=INK))
    f.append(text(600, 70, "Поетапний рух даних: від сирого вхідного пакету до строго валідованого канонічного контракту та проекцій", size=11.5, color=MUTED))

    steps = [
        ("1. Ingress & Decode", 145, 175,
         "• Читання з сокета/черги\n• Перевірка кодування (UTF-8)\n• Десеріалізація синтаксису\n(JSON / XML / Protobuf)",
         COOL, LINE),
        ("2. Inbound ACL Mapping", 370, 175,
         "• Сплощення ієрархії\n• Нормалізація типів (копійки)\n• Мапінг Enum та статусів\n• Генерація Envelope Headers",
         WARM, POS),
        ("3. Schema Validation", 600, 175,
         "• Звірка з Schema Registry\n• Перевірка версії контракту\n• Валідація інваріантів\n• Помилка → Dead Letter Queue",
         GOOD, FIELD),
        ("4. Canonical Event Log", 830, 175,
         "• Публікація в Event Log\n• Маршрутизація підписникам\n• Незмінний аудит-трейс\n• Ідемпотентна доставка",
         WARN, LINE),
        ("5. Outbound Projection", 1055, 175,
         "• Проекція на модель клієнта\n• Фільтрація зайвих полів\n• Серіалізація у формат таргету\n• Доставка в цільову чергу",
         COOL, NEG),
    ]

    for title, cx, cy, desc, fill_c, stroke_c in steps:
        f.append(rect(cx - 95, cy - 65, 190, 195, fill=fill_c, stroke=stroke_c, sw=1.6, rx=8))
        f.append(text(cx, cy - 40, title, size=11, bold=True, color=stroke_c if stroke_c != LINE else INK))
        f.append(line(cx - 85, cy - 25, cx + 85, cy - 25, color=stroke_c, sw=1))

        lines = desc.split("\n")
        ly = cy - 5
        for ln in lines:
            f.append(text(cx - 80, ly, ln, size=9.5, color=INK, anchor="start"))
            ly += 20

    # Стрілки між етапами конвеєра
    for i in range(len(steps) - 1):
        x1 = steps[i][1] + 95
        x2 = steps[i+1][1] - 95
        y = steps[i][2] + 25
        f.append(arrow(x1, y, x2, y, color=FIELD, sw=2))

    # Нижній блок контролю помилок та DLQ
    f.append(rect(45, 340, 1110, 135, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(600, 365, "Критичні механізми надійності конвеєра", size=13, bold=True, color=INK))

    subblocks = [
        ("Tolerant Reader", 185, 385, "Споживач читає лише відомі йому поля;\nнові поля ігноруються без помилок."),
        ("Dead Letter Queue", 460, 385, "Повідомлення з порушенням схеми або\nневідомими статусами ізолюються в DLQ."),
        ("Correlation & Tracing", 740, 385, "W3C traceparent та correlation_id\nзберігаються на всіх фазах мапінгу."),
        ("Schema Compatibility", 1015, 385, "Зворотна сумісність (BACKWARD):\nвидалення обов'язкових полів заборонено."),
    ]

    for stitle, scx, scy, sbody in subblocks:
        f.append(rect(scx - 120, scy, 240, 75, fill=PANEL, stroke=MUTED, sw=1, rx=5))
        f.append(text(scx, scy + 20, stitle, size=11, bold=True, color=INK))
        slines = sbody.split("\n")
        f.append(text(scx, scy + 40, slines[0], size=9.5, color=MUTED))
        f.append(text(scx, scy + 55, slines[1], size=9.5, color=MUTED))

    render(os.path.join(OUT, 'cdm-transformation-pipeline.svg'), W, H, *f)


if __name__ == '__main__':
    cdm_architecture_layers()
    global_vs_federated_cdm()
    cdm_transformation_pipeline()
    print("Фігури успішно згенеровано.")
