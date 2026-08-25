# -*- coding: utf-8 -*-
"""Фігури до теми «Транслятор повідомлень і канонічна модель»."""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / спагеті
COOL = "#eaf0fd"   # нейтральне / вузли / формати
GOOD = "#e8f6ee"   # успіх / канонічна шина / чистота
WARN = "#fef9e7"   # застереження / адаптери


# ── 1. Порівняння: Point-to-Point (O(N^2)) vs Канонічна модель (O(N)) ────────
def point_to_point_vs_canonical():
    W, H = 1140, 520
    f = []

    # Ліва половина: Point-to-Point спагеті
    f.append(rect(30, 20, 525, 420, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(292, 50, "Пряма інтеграція: Point-to-Point (O(N²))", size=14, bold=True, color=POS))
    f.append(text(292, 72, "5 систем = 20 адаптерів; додавання 6-ї вимагає 10 нових конвертерів", size=11.5, color=MUTED))

    p2p_nodes = [
        ("Checkout (JSON)", 0),
        ("ERP (XML)", 72),
        ("Logistics (EDI)", 144),
        ("Billing (Proto)", 216),
        ("Analytics (Avro)", 288),
    ]
    p2p_coords = []
    cx_l, cy_l, r_l = 292, 245, 130
    for name, deg in p2p_nodes:
        rad = math.radians(deg - 90)
        nx = cx_l + r_l * math.cos(rad)
        ny = cy_l + r_l * math.sin(rad)
        p2p_coords.append((nx, ny, name))

    # Малюємо лінії зв'язку між усіма парами
    for i in range(len(p2p_coords)):
        for j in range(i + 1, len(p2p_coords)):
            x1, y1, _ = p2p_coords[i]
            x2, y2, _ = p2p_coords[j]
            f.append(line(x1, y1, x2, y2, color=POS, sw=1.2, dash="3,3"))

    # Малюємо блоки вузлів
    for nx, ny, name in p2p_coords:
        f.append(rect(nx - 55, ny - 16, 110, 32, fill=WARM, stroke=POS, sw=1.4, rx=6))
        f.append(text(nx, ny + 4, name, size=11, bold=True, color=INK))

    f.append(fitbox(45, 385, 495, 45,
                    "Жорстке зачеплення: зміна формату в одній системі ламає всі 4 зв'язані адаптери.",
                    size=11.5, fill=WARM, stroke=POS, sw=1.1))

    # Права половина: Канонічна модель (CDM)
    f.append(rect(585, 20, 525, 420, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(847, 50, "Канонічна модель: Message Translator (O(N))", size=14, bold=True, color=FIELD))
    f.append(text(847, 72, "5 систем = 10 трансляторів (2N); додавання 6-ї вимагає лише 2", size=11.5, color=MUTED))

    cx_r, cy_r, r_r = 847, 245, 135
    cdm_coords = []
    for name, deg in p2p_nodes:
        rad = math.radians(deg - 90)
        nx = cx_r + r_r * math.cos(rad)
        ny = cy_r + r_r * math.sin(rad)
        cdm_coords.append((nx, ny, name))

    # Центральний вузол: Канонічна шина
    f.append(rect(cx_r - 70, cy_r - 35, 140, 70, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(text(cx_r, cy_r - 10, "Канонічна модель", size=12, bold=True, color=FIELD))
    f.append(text(cx_r, cy_r + 8, "(CDM / Шина)", size=11, bold=True, color=INK))
    f.append(text(cx_r, cy_r + 24, "Єдиний формат", size=10, italic=True, color=MUTED))

    # Двосторонні стрілки від систем до центру через адаптери
    for nx, ny, name in cdm_coords:
        f.append(line(nx, ny, cx_r, cy_r, color=FIELD, sw=1.8))
        f.append(rect(nx - 55, ny - 16, 110, 32, fill=COOL, stroke=LINE, sw=1.3, rx=6))
        f.append(text(nx, ny + 4, name, size=11, bold=True, color=INK))

    f.append(fitbox(600, 385, 495, 45,
                    "Повне розчеплення: кожна система знає лише власний формат і канонічний контракт.",
                    size=11.5, fill=GOOD, stroke=FIELD, sw=1.1))

    # Підсумкова плашка
    f.append(fitbox(30, 455, 1080, 50,
                    "Математичний ефект: перехід від прямого спагеті пар N·(N−1) до централізованої канонічної моделі 2N "
                    "зменшує кількість трансляторів у рази та ізолює схеми систем одна від одної.",
                    size=12.5, fill=WARN, stroke=LINE, sw=1.3))

    render(os.path.join(OUT, 'point-to-point-vs-canonical.svg'), W, H, *f)


# ── 2. Анатомія конвеєра трансляції повідомлення ─────────────────────────────
def translator_pipeline_anatomy():
    W, H = 1140, 530
    f = []

    f.append(rect(20, 15, 1100, 495, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 45, "Внутрішній конвеєр транслятора повідомлень (Pipeline Stages)", size=15, bold=True, color=INK))
    f.append(text(570, 68, "Послідовна обробка вхідного пакету від сирих байтів до канонічного контракту та DLQ", size=11.5, color=MUTED))

    # 5 основних блоків конвеєра по горизонталі
    stages = [
        (45, "1. Ingress & Unwrap", "Розпакування\nконверта", "Заголовки, трасування,\nвитяг тіла payload", COOL),
        (255, "2. Syntax Parse", "Парсинг синтаксису\nй типів", "JSON/XML десеріалізація,\nперевірка формату", COOL),
        (465, "3. Semantic Map", "Семантичний мапінг\nі збагачення", "Конверсія одиниць, мапінг enum,\nнормалізація ID", GOOD),
        (675, "4. Canonical DTO", "Канонічна валідація\nй DTO", "Контроль інваріантів,\nпобудова чистого об'єкта", GOOD),
        (885, "5. Egress Serialize", "Серіалізація у цільовий\nформат", "Упаковка в Protobuf/Avro,\nвідправка в чергу/топік", GOOD),
    ]

    for x, num, title, desc, col in stages:
        f.append(rect(x, 100, 190, 190, fill=col, stroke=LINE, sw=1.4, rx=6))
        f.append(text(x + 95, 125, num, size=12, bold=True, color=INK))
        lines = title.split("\n")
        if len(lines) == 1:
            f.append(text(x + 95, 150, lines[0], size=11.5, bold=True, color=INK))
        else:
            f.append(text(x + 95, 145, lines[0], size=11.5, bold=True, color=INK))
            f.append(text(x + 95, 162, lines[1], size=11.5, bold=True, color=INK))

        f.append(line(x + 15, 180, x + 175, 180, color=MUTED, sw=1, dash="2,2"))

        dlines = desc.split("\n")
        if len(dlines) == 1:
            f.append(text(x + 95, 215, dlines[0], size=10, color=MUTED))
        else:
            f.append(text(x + 95, 205, dlines[0], size=10, color=MUTED))
            f.append(text(x + 95, 222, dlines[1], size=10, color=MUTED))

    # Стрілки між послідовними стадіями
    for i in range(len(stages) - 1):
        x_from = stages[i][0] + 190
        x_to = stages[i + 1][0]
        f.append(arrow(x_from, 195, x_to, 195, color=FIELD, sw=2))

    # Вхідний та вихідний потоки
    f.append(text(45 + 95, 90, "Вхідний пакет (JSON/XML)", size=10.5, color=MUTED, italic=True))
    f.append(text(885 + 95, 90, "Цільова черга (Protobuf)", size=10.5, color=FIELD, bold=True))

    # Відгалуження помилок у Dead Letter Queue (DLQ)
    f.append(rect(255, 330, 610, 95, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(560, 355, "Карантин помилок: Мертва черга (Dead Letter Queue, DLQ)", size=13, bold=True, color=POS))
    f.append(text(560, 375, "Фіксація причини збою: пошкоджений синтаксис, невідомий enum, відсутні обов'язкові поля", size=10.5, color=INK))
    f.append(text(560, 395, "Оригінальні байти збережено + контекст помилки + трасування (Traceparent)", size=10.5, italic=True, color=MUTED))

    # Стрілки вниз до DLQ
    f.append(arrow(350, 290, 350, 330, color=POS, sw=1.6))
    f.append(text(395, 310, "Помилка парсингу", size=9.5, color=POS, bold=True))

    f.append(arrow(560, 290, 560, 330, color=POS, sw=1.6))
    f.append(text(620, 310, "Семантичний збій", size=9.5, color=POS, bold=True))

    f.append(arrow(770, 290, 770, 330, color=POS, sw=1.6))
    f.append(text(825, 310, "Порушення інваріанту", size=9.5, color=POS, bold=True))

    # Підсумок
    f.append(fitbox(45, 445, 1050, 50,
                    "Ключове правило надійності: транслятор ніколи не ковтає помилки мовчки та не запускає нескінченні повтори "
                    "для невалідних даних — пошкоджений пакет ізолюється в DLQ із діагностичним контекстом.",
                    size=12, fill=WARN, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'translator-pipeline-anatomy.svg'), W, H, *f)


# ── 3. Захисний шар (Anti-Corruption Layer, ACL) у Domain-Driven Design ──────
def anti_corruption_layer_ddd():
    W, H = 1140, 480
    f = []

    f.append(rect(25, 15, 1090, 445, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 45, "Anti-Corruption Layer (ACL): ізоляція доменної моделі від чужої спадщини", size=15, bold=True, color=INK))
    f.append(text(570, 68, "Транслятор повідомлень як бар'єр між архаїчною спадщиною (Legacy) та чистою бізнес-моделлю (DDD)", size=11.5, color=MUTED))

    # Лівий бік: Зовнішня/Застаріла система (Upstream Legacy)
    f.append(rect(50, 105, 290, 245, fill=WARM, stroke=POS, sw=1.4, rx=6))
    f.append(text(195, 135, "Зовнішній світ / Legacy ERP", size=13, bold=True, color=POS))
    f.append(text(195, 155, "(Upstream Context)", size=11, italic=True, color=MUTED))
    f.append(line(70, 170, 320, 170, color=POS, sw=1, dash="2,2"))

    legacy_items = [
        "• Хаотичні назви полів (CUST_ADDR_LN1)",
        "• Числові магічні статуси (104, 999, -1)",
        "• Змішання транспорту й бізнес-даних",
        "• Відсутність типізації дат (строки YYYYMMDD)",
        "• Нестабільні неоголошені схеми",
    ]
    for idx, it in enumerate(legacy_items):
        f.append(text(75, 195 + idx * 22, it, size=10.5, color=INK, anchor="start"))

    # Центральний блок: Anti-Corruption Layer (ACL)
    f.append(rect(390, 95, 340, 265, fill=WARN, stroke=LINE, sw=1.8, rx=8))
    f.append(text(560, 125, "Anti-Corruption Layer (ACL)", size=14, bold=True, color=INK))
    f.append(text(560, 145, "Фасад + Адаптер + Транслятор", size=11, color=FIELD, bold=True))
    f.append(line(410, 160, 710, 160, color=LINE, sw=1, dash="2,2"))

    acl_stages = [
        ("1. Channel Adapter", "Прийом протоколу (HTTP/AMQP)"),
        ("2. Translator Service", "Мапінг форматів і валідація схем"),
        ("3. Domain Factory", "Побудова чистих Value Objects / Entities"),
        ("4. Context Boundary", "Фільтрація чужих артефактів"),
    ]
    for idx, (t1, t2) in enumerate(acl_stages):
        f.append(rect(410, 175 + idx * 42, 300, 34, fill=BG, stroke=LINE, sw=1.1, rx=4))
        f.append(text(420, 196 + idx * 42, t1, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(700, 196 + idx * 42, t2, size=9.5, color=MUTED, anchor="end"))

    # Правий бік: Чистий обмежений контекст (Downstream Domain)
    f.append(rect(780, 105, 310, 245, fill=GOOD, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(935, 135, "Чистий доменний контекст", size=13, bold=True, color=FIELD))
    f.append(text(935, 155, "(Downstream Bounded Context)", size=11, italic=True, color=MUTED))
    f.append(line(800, 170, 1070, 170, color=FIELD, sw=1, dash="2,2"))

    domain_items = [
        "• Чиста загальноприйнята мова (Ubiquitous Lang)",
        "• Строгі незмінні Value Objects (Money, Email)",
        "• Доменні події: OrderPlaced, PaymentReceived",
        "• Повна ізоляція від формату зберігання Legacy",
        "• Незалежна еволюція внутрішнього коду",
    ]
    for idx, it in enumerate(domain_items):
        f.append(text(800, 195 + idx * 22, it, size=10.5, color=INK, anchor="start"))

    # Стрілки передачі даних
    f.append(arrow(340, 227, 390, 227, color=POS, sw=2))
    f.append(arrow(730, 227, 780, 227, color=FIELD, sw=2))

    # Підсумковий блок
    f.append(fitbox(50, 385, 1040, 55,
                    "Призначення ACL: не дозволити чужим концепціям і технічним компромісам зовнішніх систем "
                    "проникнути в серцевину вашої доменної моделі. Транслятор бере на себе всю брудну роботу з очищення та конверсії.",
                    size=12, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'anti-corruption-layer-ddd.svg'), W, H, *f)


# ── 4. Пастка монолітної моделі vs Локальні канонічні схеми ──────────────────
def canonical_model_trap_vs_bounded_context():
    W, H = 1140, 500
    f = []

    f.append(rect(25, 15, 1090, 465, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 45, "Пастка глобальної канонічної моделі проти локальних схем контекстів", size=15, bold=True, color=INK))
    f.append(text(570, 68, "Чому «єдина модель усього підприємства» зазнала фіаско і як діють сучасні розподілені системи", size=11.5, color=MUTED))

    # Верхній блок: Антипатерн — Глобальна монолітна супер-модель
    f.append(rect(50, 95, 1040, 155, fill=WARM, stroke=POS, sw=1.4, rx=6))
    f.append(text(570, 120, "Антипатерн: Єдина всеохопна корпоративна супер-схема (The Global CDM Trap)", size=13, bold=True, color=POS))

    trap_cols = [
        (75, 360, "Роздуті DTO (God Objects)", [
            "Сотні опціональних полів, де",
            "кожній команді потрібні лише 5%.",
            "Найменший спільний знаменник."
        ]),
        (400, 710, "Бюрократичний тупик змін", [
            "Будь-яка зміна поля вимагає",
            "погодження 12 відділів компанії.",
            "Релізи заморожуються на місяці."
        ]),
        (750, 1060, "Семантичний конфлікт", [
            "Поняття «Клієнт» у білінгу, CRM,",
            "логістиці та підтримці має зовсім",
            "різний зміст та життєвий цикл."
        ]),
    ]
    for x0, x1, h_title, lines in trap_cols:
        w_col = x1 - x0
        f.append(rect(x0, 135, w_col, 100, fill=BG, stroke=POS, sw=1.1, rx=4))
        f.append(text(x0 + w_col / 2, 156, h_title, size=11.5, bold=True, color=POS))
        for l_idx, l_txt in enumerate(lines):
            f.append(text(x0 + w_col / 2, 178 + l_idx * 17, l_txt, size=10, color=INK))

    # Нижній блок: Прагматичний підхід — Локальні канонічні моделі Bounded Contexts
    f.append(rect(50, 270, 1040, 190, fill=GOOD, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(570, 295, "Сучасне рішення: Федеративні контракти за межами обмежених контекстів (DDD + Schema Registry)", size=13, bold=True, color=FIELD))

    ctx_cards = [
        (75, 360, "Контекст Замовлень (Orders)", [
            "Канонічна модель замовлення:",
            "• OrderID, CustomerRef",
            "• LineItems, Pricing",
            "• OrderState, Timestamp"
        ]),
        (400, 710, "Контекст Доставки (Shipping)", [
            "Канонічна модель відправлення:",
            "• ParcelID, DestinationAddress",
            "• WeightKg, CarrierCode",
            "• DeliveryStatus"
        ]),
        (750, 1060, "Контекст Рахунків (Invoicing)", [
            "Канонічна модель оплати:",
            "• InvoiceID, TaxID",
            "• AmountCents, Currency",
            "• PaymentStatus"
        ]),
    ]
    for x0, x1, c_title, lines in ctx_cards:
        w_col = x1 - x0
        f.append(rect(x0, 310, w_col, 135, fill=BG, stroke=FIELD, sw=1.2, rx=4))
        f.append(text(x0 + w_col / 2, 332, c_title, size=11.5, bold=True, color=FIELD))
        f.append(line(x0 + 15, 342, x1 - 15, 342, color=MUTED, sw=1, dash="2,2"))
        f.append(text(x0 + 15, 362, lines[0], size=10, bold=True, color=INK, anchor="start"))
        for l_idx, l_txt in enumerate(lines[1:]):
            f.append(text(x0 + 20, 382 + l_idx * 18, l_txt, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'canonical-model-trap-vs-bounded-context.svg'), W, H, *f)


if __name__ == '__main__':
    point_to_point_vs_canonical()
    translator_pipeline_anatomy()
    anti_corruption_layer_ddd()
    canonical_model_trap_vs_bounded_context()
    print("Всі фігури згенеровано успішно.")
