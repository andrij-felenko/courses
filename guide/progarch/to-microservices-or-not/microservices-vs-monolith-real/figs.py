# -*- coding: utf-8 -*-
"""Фігури до статті «Мікросервіси проти моноліта без ідеології»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_tradeoff_matrix():
    """Порівняльна матриця компромісів: Моноліт проти Мікросервісів."""
    W, H = 1120, 520
    frags = []

    # Заголовок матриці
    b, _, _ = textbox(560, 45, "Порівняльна матриця компромісів топ-рівня", size=15,
                      fill="#eef2fb", stroke=LINE, bold=True, min_w=460)
    frags.append(b)

    # Колонки: Вимір, Модульний моноліт, Мікросервісна архітектура
    y_top = 90
    frags.append(rect(60, y_top, 240, 40, fill="#333333", stroke=LINE, rx=4))
    frags.append(text(180, y_top + 25, "Вимір архітектури", size=13, color="#ffffff", bold=True))

    frags.append(rect(310, y_top, 380, 40, fill="#27ae60", stroke=LINE, rx=4))
    frags.append(text(500, y_top + 25, "Модульний моноліт", size=13, color="#ffffff", bold=True))

    frags.append(rect(700, y_top, 380, 40, fill="#2457d6", stroke=LINE, rx=4))
    frags.append(text(890, y_top + 25, "Мікросервіси", size=13, color="#ffffff", bold=True))

    rows = [
        ("Мережева затримка (IPC)", "Виклики в пам'яті (~10-50 нс)\nZero-copy, відсутність серіалізації", "Мережеві стрибки (~1-10 мс)\nmTLS, JSON/Protobuf, p99 хвости"),
        ("Консистентність даних", "ACID-транзакції у 1 БД\nАтомарний COMMIT / ROLLBACK", "Розподілені транзакції (Saga)\nEventual consistency, Outbox, CDC"),
        ("Операційні витрати", "Низькі (1 binary/container)\n1 CI/CD, простий моніторинг", "Високі (N сервісів, K8s, Mesh)\nN CI/CD, OpenTelemetry, Tracing"),
        ("Автономія деплою", "Спільний релізний цикл\nПотрібна координація команд", "Незалежний деплой сервісів\nРізні технологічні стеки"),
        ("Масштабування орги", "Вузьке місце при >30-50 інженерів\nКонфлікти в єдиному репозиторії", "Ідеально під Закон Конвея\nАвтономні 2-pizza teams"),
        ("Локальна розробка", "Запуск за 1 команду в IDE\nМиттєвий фідбек і відлагодження", "Потрібні Docker Compose/k3d/telepresence\nВисоке навантаження на RAM"),
    ]

    y_curr = 140
    for idx, (dim, mon, ms) in enumerate(rows):
        h_row = 56
        bg_color = "#fcfdfe" if idx % 2 == 0 else "#f4f6f8"

        # Вимір
        b, _, _ = textbox(180, y_curr + h_row/2, dim, size=12, fill="#eaeded", stroke=LINE, min_w=240, bold=True)
        frags.append(b)

        # Моноліт
        b, _, _ = textbox(500, y_curr + h_row/2, mon, size=11, fill=bg_color, stroke=MUTED, min_w=380)
        frags.append(b)

        # Мікросервіси
        b, _, _ = textbox(890, y_curr + h_row/2, ms, size=11, fill=bg_color, stroke=MUTED, min_w=380)
        frags.append(b)

        y_curr += h_row + 4

    render(os.path.join(IMG, "tradeoff-matrix.svg"), W, H, *frags,
           title="Порівняльна матриця компромісів моноліта та мікросервісів")


def fig_tail_latency_amplification():
    """Ефект накопичення хвостових затримок (Tail Latency Amplification)."""
    W, H = 1120, 500
    frags = []

    # Заголовок
    b, _, _ = textbox(560, 40, "Ампліфікація хвостових затримок (p99) при послідовних мережевих викликах",
                      size=14, fill="#eef2fb", stroke=LINE, bold=True, min_w=580)
    frags.append(b)

    # Формула
    b, _, _ = textbox(560, 95, "P(затримка системи) = 1 - (1 - p)^k   [де p = p99 поодинокого сервісу (1%), k = кількість послідовних викликів]",
                      size=12, fill="#fff9e6", stroke="#d35400", min_w=680)
    frags.append(b)

    # Порівняльні схеми для k=1, k=5, k=10, k=20
    scenarios = [
        ("k = 1 виклик", "Моноліт або 1 сервіс", "p99 = 1.0%", "P = 1.0%", "#27ae60"),
        ("k = 5 викликів", "Короткий ланцюжок", "p99 = 1.0% на крок", "P = 4.9%", "#f39c12"),
        ("k = 10 викликів", "Середній ланцюжок", "p99 = 1.0% на крок", "P = 9.6%", "#e67e22"),
        ("k = 20 викликів", "Глибокий мікросервісний граф", "p99 = 1.0% на крок", "P = 18.2%", "#c0392b"),
    ]

    x_start = 140
    for idx, (title_k, desc, step_p, total_p, col) in enumerate(scenarios):
        x = x_start + idx * 270
        y = 160

        # Карточка сценарію
        frags.append(rect(x - 110, y, 220, 300, fill="#fafbfc", stroke=col, rx=6, sw=2))

        # Заголовок картки
        frags.append(rect(x - 110, y, 220, 40, fill=col, stroke=col, rx=4))
        frags.append(text(x, y + 25, title_k, size=14, color="#ffffff", bold=True))

        # Опис
        frags.append(text(x, y + 70, desc, size=11, color=MUTED))
        frags.append(text(x, y + 100, step_p, size=11, color=INK))

        # Візуальні блоки викликів
        num_boxes = 1 if idx == 0 else (3 if idx == 1 else (5 if idx == 2 else 7))
        y_box = y + 125
        for b_idx in range(num_boxes):
            box_h = 14 if idx >= 2 else 20
            frags.append(rect(x - 70, y_box, 140, box_h, fill="#eef2fb", stroke="#2457d6", rx=2))
            if b_idx < num_boxes - 1:
                frags.append(arrow(x, y_box + box_h, x, y_box + box_h + 6, color="#2457d6", sw=1.2))
            y_box += box_h + 6

        # Результат p99 для всієї системи
        frags.append(rect(x - 90, y + 240, 180, 45, fill="#ffffff", stroke=col, rx=4, sw=1.8))
        frags.append(text(x, y + 260, "Загальний p99 системи:", size=10, color=MUTED))
        frags.append(text(x, y + 277, total_p, size=15, color=col, bold=True))

    render(os.path.join(IMG, "tail-latency-amplification.svg"), W, H, *frags,
           title="Ампліфікація хвостових затримок у мікросервісах")


def fig_saga_vs_acid_flow():
    """Порівняння потоку ACID-транзакції в моноліті проти Saga + Outbox у мікросервісах."""
    W, H = 1140, 520
    frags = []

    # Заголовок
    b, _, _ = textbox(570, 40, "Анатомія обробки відмови: Моноліт (ACID) проти Мікросервісів (Saga + Outbox)",
                      size=14, fill="#eef2fb", stroke=LINE, bold=True, min_w=620)
    frags.append(b)

    # Ліва панель: Моноліт
    frags.append(rect(40, 80, 510, 410, fill="#fcfdfe", stroke="#27ae60", rx=6, sw=1.8))
    frags.append(rect(40, 80, 510, 40, fill="#27ae60", stroke="#27ae60", rx=4))
    frags.append(text(295, 105, "Модульний моноліт: Атомарна ACID-транзакція", size=13, color="#ffffff", bold=True))

    monolith_steps = [
        "1. Запит: Оформлення замовлення",
        "2. BEGIN TRANSACTION (1 БД)",
        "3. UPDATE Accounts SET balance = balance - 100",
        "4. INSERT INTO Orders (status = 'created')",
        "5. UPDATE Inventory SET qty = qty - 1",
        "6. Якщо збій на кроці 5 -> ROLLBACK",
        "7. Атомарний COMMIT (стан консистентний за <5 мс)",
    ]

    y_m = 145
    for st in monolith_steps:
        is_err = "ROLLBACK" in st
        fill_c = "#fdecea" if is_err else "#eafaf0"
        strk_c = POS if is_err else FIELD
        b, _, _ = textbox(295, y_m + 16, st, size=11, fill=fill_c, stroke=strk_c, min_w=450)
        frags.append(b)
        y_m += 44

    # Права панель: Мікросервіси
    frags.append(rect(590, 80, 510, 410, fill="#fcfdfe", stroke="#2457d6", rx=6, sw=1.8))
    frags.append(rect(590, 80, 510, 40, fill="#2457d6", stroke="#2457d6", rx=4))
    frags.append(text(845, 105, "Мікросервіси: Saga + Transactional Outbox", size=13, color="#ffffff", bold=True))

    saga_steps = [
        "1. Service A: Charge Account -> Write DB + Write Outbox Table",
        "2. CDC / Relay (Debezium): Poll Outbox -> Publish to Kafka",
        "3. Service B consumes event -> Reserve Inventory",
        "4. Збій у Service B (немає товару)",
        "5. Service B publishes 'InventoryFailedEvent' to Kafka",
        "6. Service A consumes failure event -> Runs Compensating Tx",
        "7. Service A: Refund Account (Eventual consistency, ~500-2000 мс)",
    ]

    y_s = 145
    for st in saga_steps:
        is_err = "Збій" in st or "Compensating" in st or "Refund" in st
        fill_c = "#fdecea" if is_err else "#eef2fb"
        strk_c = POS if is_err else NEG
        b, _, _ = textbox(845, y_s + 16, st, size=11, fill=fill_c, stroke=strk_c, min_w=470)
        frags.append(b)
        y_s += 44

    render(os.path.join(IMG, "saga-vs-acid-flow.svg"), W, H, *frags,
           title="Порівняння ACID в моноліті проти Saga у мікросервісах")


if __name__ == "__main__":
    fig_tradeoff_matrix()
    fig_tail_latency_amplification()
    fig_saga_vs_acid_flow()
    print("Всі фігури згенеровано успішно.")
