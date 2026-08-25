# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Оптимістичне блокування» (optimistic-locking)."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle,
    INK, MUTED, LINE, FILL, POS, NEG, FIELD, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_occ_timeline():
    """Фігура 1: Часова шкала конкурентних спроб запису та виявлення колізії."""
    w, h = 820, 480
    frags = []

    # Клієнт 1 (успішний)
    b1, _, _ = textbox(150, 45, "Клієнт 1 (Транзакція A)", size=13, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b1)
    frags.append(line(150, 65, 150, 430, color=NEG, sw=1.5, dash="4,4"))

    # База даних (Джерело правди)
    b_db, _, _ = textbox(410, 45, "Реляційна СУБД (Рядок id=42)", size=13, bold=True, fill="#e8f8f0", stroke=FIELD)
    frags.append(b_db)
    frags.append(line(410, 65, 410, 430, color=FIELD, sw=1.8))

    # Клієнт 2 (колізія)
    b2, _, _ = textbox(670, 45, "Клієнт 2 (Транзакція B)", size=13, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b2)
    frags.append(line(670, 65, 670, 430, color=POS, sw=1.5, dash="4,4"))

    # Початковий стан у базі
    db_s1, _, _ = textbox(410, 95, "Стан: {balance: 1000, version: 1}", size=11, fill="#ffffff", stroke=FIELD, pad=6)
    frags.append(db_s1)

    # 1. Читання Клієнтом 1
    frags.append(arrow(150, 125, 400, 125, color=NEG))
    frags.append(text(275, 118, "1. SELECT balance, version WHERE id=42", size=10, color=NEG))

    # Відповідь Клієнту 1
    frags.append(arrow(410, 145, 160, 145, color=MUTED))
    frags.append(text(275, 140, "Дані: balance=1000, version=1", size=10, color=MUTED))

    # 2. Читання Клієнтом 2 (паралельно)
    frags.append(arrow(670, 165, 420, 165, color=POS))
    frags.append(text(545, 158, "2. SELECT balance, version WHERE id=42", size=10, color=POS))

    # Відповідь Клієнту 2
    frags.append(arrow(410, 185, 660, 185, color=MUTED))
    frags.append(text(545, 180, "Дані: balance=1000, version=1", size=10, color=MUTED))

    # Обчислення в пам'яті клієнтів
    c1_work, _, _ = textbox(150, 220, "Обчислення в RAM:\nbalance = 1000 - 200 = 800", size=10, fill=FILL, pad=5)
    frags.append(c1_work)

    c2_work, _, _ = textbox(670, 220, "Обчислення в RAM:\nbalance = 1000 - 300 = 700", size=10, fill=FILL, pad=5)
    frags.append(c2_work)

    # 3. Клієнт 1 надсилає CAS UPDATE першим
    frags.append(arrow(150, 265, 400, 265, color=NEG, sw=2))
    frags.append(text(275, 258, "3. UPDATE ... SET balance=800, version=2 WHERE v=1", size=10, color=NEG, bold=True))

    # Стан у базі змінюється
    db_s2, _, _ = textbox(410, 295, "Успіх CAS: affected_rows = 1\nНовий стан: {balance: 800, version: 2}", size=11, fill="#e8f8f0", stroke=FIELD, pad=6, bold=True)
    frags.append(db_s2)

    # Відповідь Клієнту 1: успіх
    frags.append(arrow(410, 325, 160, 325, color=NEG))
    frags.append(text(275, 320, "Фіксація успішна (Rows Affected: 1)", size=10, color=FIELD, bold=True))

    # 4. Клієнт 2 надсилає запізнілий CAS UPDATE зі старою версією
    frags.append(arrow(670, 355, 420, 355, color=POS, sw=2))
    frags.append(text(545, 348, "4. UPDATE ... SET balance=700, version=2 WHERE v=1", size=10, color=POS, bold=True))

    # СУБД перевіряє: поточна версія в базі вже 2, а запит вимагає version=1 -> 0 рядків змінено!
    db_s3, _, _ = textbox(410, 385, "Провал CAS: version != 1\nРядки не змінено: affected_rows = 0", size=11, fill="#fdecea", stroke=POS, pad=6, bold=True)
    frags.append(db_s3)

    # Відповідь Клієнту 2: колізія
    frags.append(arrow(410, 415, 660, 415, color=POS))
    frags.append(text(545, 410, "Помилка: OptimisticLockException (Rows: 0)", size=10, color=POS, bold=True))

    path = os.path.join(IMG_DIR, "occ-timeline.svg")
    render(path, w, h, *frags)
    print("Generated:", path)


def fig_occ_throughput():
    """Фігура 2: Графік пропускної здатності OCC проти песимістичного блокування 2PL."""
    w, h = 820, 440
    frags = []

    # Y axis
    frags.append(arrow(100, 370, 100, 45, color=LINE, sw=2))
    frags.append(text(105, 35, "Пропускна здатність (успішних транзакцій / с)", size=11, color=INK, anchor="start", bold=True))

    # X axis
    frags.append(arrow(100, 370, 770, 370, color=LINE, sw=2))
    frags.append(text(760, 395, "Рівень конкуренції за записи (Contention Rate, %)", size=11, color=INK, anchor="end", bold=True))

    # Сітка та мітки X
    for x_val, label in [(200, "10%"), (330, "25% (Перетин)"), (480, "50%"), (630, "75%"), (740, "100%")]:
        frags.append(line(x_val, 370, x_val, 70, color="#e5e7eb", sw=1, dash="3,3"))
        frags.append(text(x_val, 388, label, size=10, color=MUTED))

    # Крива 1: Оптимістичне блокування (OCC)
    occ_points = "M 110,80 C 200,85 280,120 330,190 C 400,280 500,340 740,362"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (occ_points, FIELD))

    # Позначка для OCC
    b_occ, _, _ = textbox(215, 52, "Оптимістичне блокування (OCC)\nНульові витрати на блокування", size=10, fill="#e8f8f0", stroke=FIELD, pad=5, bold=True)
    frags.append(b_occ)

    # Крива 2: Песимістичне блокування (2PL / SELECT FOR UPDATE)
    pess_points = "M 110,180 C 220,182 280,185 330,190 C 420,200 550,220 740,250"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5" stroke-dasharray="6,4"/>' % (pess_points, NEG))

    # Позначка для Pessimistic
    b_pess, _, _ = textbox(600, 180, "Песимістичне блокування (2PL)\nУпорядкування через черги замків", size=10, fill="#eaf0fd", stroke=NEG, pad=5, bold=True)
    frags.append(b_pess)

    # Точка перетину (Crossover point)
    frags.append(circle(330, 190, 6, fill=POS, stroke="#ffffff", sw=2))
    # Розміщуємо блок пояснення перетину праворуч угорі від точки
    cross_b, _, _ = textbox(440, 110, "Поріг ефективності (~20-25% колізій):\nOCC зазнає колапсу через лавину\nповторних спроб (Retry Storm)", size=10, fill="#fdecea", stroke=POS, pad=6)
    frags.append(cross_b)
    frags.append(line(340, 180, 400, 135, color=POS, sw=1.5))

    # Зони ефективності знизу
    z1 = rect(110, 405, 210, 24, fill="#e8f8f0", stroke=FIELD, rx=4)
    frags.append(z1)
    frags.append(text(215, 421, "Зона переваги OCC (Read-Heavy)", size=10, color=FIELD, bold=True))

    z2 = rect(340, 405, 410, 24, fill="#eaf0fd", stroke=NEG, rx=4)
    frags.append(z2)
    frags.append(text(545, 421, "Зона переваги 2PL (High Contention Hotspots)", size=10, color=NEG, bold=True))

    path = os.path.join(IMG_DIR, "occ-vs-pessimistic-throughput.svg")
    render(path, w, h, *frags)
    print("Generated:", path)


def fig_aggregate_versioning():
    """Фігура 3: Патерн оновлення версії кореня агрегату при модифікації дочірніх сутностей."""
    w, h = 820, 380
    frags = []

    # Рамка агрегату Замовлення (Order Aggregate)
    agg_bg = rect(50, 40, 720, 310, fill="none", stroke="#9ca3af", sw=1.5, rx=10)
    frags.append(agg_bg)
    frags.append(text(80, 68, "Межа транзакційного агрегату (Order Aggregate Boundary)", size=13, color=MUTED, anchor="start", bold=True))

    # Коренева сутність (Order Root)
    order_box, _, _ = textbox(220, 140, "Кореневий об'єкт: Order\n--------------------------------\nid: 101 (PK)\ncustomer_id: 55\ntotal_amount: $450\nlock_version: 5 (Маркер)", size=11, fill="#eaf0fd", stroke=NEG, pad=8, bold=True)
    frags.append(order_box)

    # Дочірні сутності (Order Items)
    item1_box, _, _ = textbox(580, 105, "OrderItem 1: {id: 1, sku: 'SSD-1TB', qty: 1, price: $100}", size=11, fill="#ffffff", stroke=LINE, pad=6)
    frags.append(item1_box)

    item2_box, _, _ = textbox(580, 160, "OrderItem 2: {id: 2, sku: 'RAM-32G', qty: 2, price: $350}", size=11, fill="#ffffff", stroke=LINE, pad=6)
    frags.append(item2_box)

    item3_new, _, _ = textbox(580, 225, "OrderItem 3 (НОВИЙ): {id: 3, sku: 'MOUSE', qty: 1, price: $50}", size=11, fill="#e8f8f0", stroke=FIELD, pad=6, bold=True)
    frags.append(item3_new)

    # Зв'язки між коренем і елементами
    frags.append(arrow(320, 125, 420, 105, color=MUTED))
    frags.append(arrow(320, 140, 420, 160, color=MUTED))
    frags.append(arrow(320, 155, 420, 225, color=FIELD, sw=2))

    # Блок пояснення інкременту версії кореня
    rule_box, _, _ = textbox(410, 305, "Правило цілісності інваріантів:\nДодавання/видалення OrderItem не має власної версії в таблиці позицій.\nТранзакція виконує примусовий інкремент: UPDATE orders SET lock_version = 6 WHERE id = 101 AND lock_version = 5\nЦе захищає агрегат від паралельного перевищення кредитного ліміту або знижок.", size=10, fill="#fef3c7", stroke="#d97706", pad=8)
    frags.append(rule_box)

    path = os.path.join(IMG_DIR, "occ-aggregate-versioning.svg")
    render(path, w, h, *frags)
    print("Generated:", path)


if __name__ == "__main__":
    fig_occ_timeline()
    fig_occ_throughput()
    fig_aggregate_versioning()
