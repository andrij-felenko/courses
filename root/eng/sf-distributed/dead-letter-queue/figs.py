# -*- coding: utf-8 -*-
"""Фігури до теми «Мертва черга (Dead Letter Queue, DLQ)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / втрата / аварія / DLQ
COOL = "#eaf0fd"   # нейтральне пояснення / структура / буфер
GOOD = "#e8f6ee"   # успіх / надійність / нормальна обробка
WARN = "#fef9e7"   # застереження / повтор / очікування


# ── 1. Життєвий цикл та архітектура мертвої черги ────────────────────────────
def dlq_lifecycle_and_architecture():
    W, H = 1180, 540
    f = []

    # Тло брокера
    f.append(rect(20, 20, 740, 500, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(390, 48, "Контур брокера повідомлень (Message Broker Runtime)", size=14, bold=True, color="#334155"))

    # Продюсер ліворуч
    f.append(fitbox(40, 90, 150, 60, "Продюсер\n(API / Сервіс)", size=12, bold=True, fill=COOL))
    f.append(arrow(190, 120, 250, 120, color=LINE, sw=1.6))
    f.append(text(220, 110, "Publish", size=10, color=MUTED, bold=True))

    # Основна черга
    f.append(rect(250, 80, 230, 90, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(365, 105, "Основна черга (Primary Queue)", size=12, bold=True, color=INK))
    msgs = [("M3", 270), ("M2", 325), ("M1", 380)]
    for label, mx in msgs:
        f.append(rect(mx, 120, 45, 34, fill=WARN, stroke=LINE, sw=1.2, rx=4))
        f.append(text(mx + 22.5, 142, label, size=11, bold=True, color=INK))
    f.append(arrow(435, 137, 470, 137, color=FIELD, sw=1.6))

    # Споживачі (воркери)
    f.append(rect(530, 70, 210, 180, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    f.append(text(635, 95, "Пул споживачів (Workers)", size=12, bold=True, color=INK))
    f.append(fitbox(545, 110, 180, 50, "Воркер A\n[Виконання M1]", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(545, 175, 180, 50, "Воркер B\n[Виконання M2]", size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Видача повідомлення з основної черги воркеру
    f.append(arrow(480, 120, 545, 135, color=FIELD, sw=1.6))
    f.append(text(510, 115, "Lease", size=10, color=FIELD, bold=True))

    # Успішна гілка (ACK)
    f.append(arrow(635, 70, 635, 45, color=FIELD, sw=1.5))
    f.append(line(635, 45, 490, 45, color=FIELD, sw=1.5))
    f.append(arrow(490, 45, 470, 80, color=FIELD, sw=1.5))
    f.append(text(560, 40, "Успіх: ACK → Видалення", size=10, color=FIELD, bold=True))

    # Невдала гілка: лічильник спроб та затримка
    f.append(arrow(635, 250, 635, 290, color=POS, sw=1.5))
    f.append(text(640, 275, "Збій обробки", size=10, color=POS, bold=True, anchor="start"))

    f.append(rect(500, 290, 240, 95, fill=WARN, stroke=LINE, sw=1.4, rx=8))
    f.append(text(620, 312, "Маршрутизатор повторів (Retry Router)", size=11, bold=True, color=INK))
    f.append(text(620, 332, "attempts < MAX_RETRIES (напр. 3)", size=10, color=MUTED, italic=True))
    f.append(text(620, 352, "Експоненційне уповільнення + Jitter", size=10, color=INK))
    f.append(text(620, 370, "delivery_count = delivery_count + 1", size=10, bold=True, color=POS))

    # Повернення в чергу на повторну спробу
    f.append(arrow(500, 340, 365, 340, color=LINE, sw=1.4))
    f.append(arrow(365, 340, 365, 170, color=LINE, sw=1.4))
    f.append(text(430, 330, "Delayed Requeue", size=10, color=MUTED, bold=True))

    # Гілка вичерпання спроб -> Мертва черга (DLQ)
    f.append(arrow(620, 385, 620, 420, color=POS, sw=1.8))
    f.append(arrow(620, 420, 490, 440, color=POS, sw=1.8))
    f.append(text(625, 410, "attempts ≥ MAX_RETRIES", size=10, color=POS, bold=True, anchor="start"))

    # Мертва черга (DLQ) всередині брокера
    f.append(rect(50, 400, 440, 105, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    f.append(text(270, 425, "Мертва черга (Dead Letter Queue — DLQ)", size=12, bold=True, color=POS))
    f.append(fitbox(70, 440, 400, 52,
                    "Збагачений конверт: [Оригінальний Payload] +\nx-original-queue, x-exception, x-stacktrace, x-retry-count, x-first-failed-at",
                    size=10, fill="#ffe3e3", stroke=POS))

    # Права частина: Екосистема обслуговування DLQ
    f.append(rect(790, 20, 370, 500, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(975, 48, "Експлуатація та відновлення (Ops)", size=14, bold=True, color="#334155"))

    # Спостережність та алерти
    f.append(fitbox(810, 80, 330, 75,
                    "1. Моніторинг та алертинг (Metrics & Alerts)\n• DLQ Depth > 0 (тривога на кожне повідомлення)\n• Age of Oldest Message (загроза вичерпання TTL)",
                    size=11, fill="#fff5f5", stroke=POS))

    # Аналіз та діагностика
    f.append(fitbox(810, 175, 330, 85,
                    "2. Тріаж та аналіз причин (Triage & Root Cause)\n• Отруйне повідомлення (дефект схеми/валідації)\n• Системна аварія стороннього сервісу\n• Дефект бізнес-логіки обробника",
                    size=11, fill=COOL, stroke=LINE))

    # Виправлення та повторне відтворення (Redrive)
    f.append(fitbox(810, 280, 330, 95,
                    "3. Повторне введення (Redrive / Replay Pipeline)\n• Виправлення коду / патч схеми даних\n• Контроль швидкості (Rate Limiter / Backpressure)\n• Захист від зациклення (Loop Breaker)",
                    size=11, fill=GOOD, stroke=FIELD))

    # Архівування
    f.append(fitbox(810, 395, 330, 70,
                    "4. Архів безнадійних повідомлень (Parking Lot)\n• Довготривале сховище S3 / холодний лог\n• Захист сховища брокера від переповнення",
                    size=11, fill=FILL, stroke=MUTED))

    # Зв'язки між DLQ та Ops
    f.append(arrow(490, 460, 810, 115, color=POS, sw=1.5))
    f.append(arrow(810, 320, 480, 150, color=FIELD, sw=1.5))
    f.append(text(670, 205, "Безпечний Redrive в основну чергу", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, 'dlq-lifecycle-and-architecture.svg'), W, H, *f)


# ── 2. Блокування початку черги (Head-of-Line Blocking) ──────────────────────
def poison_pill_hol_blocking():
    W, H = 1180, 490
    f = []

    # Верхня панель: БЕЗ DLQ (катастрофа)
    f.append(rect(20, 20, 1140, 215, fill="#fff5f5", stroke=POS, sw=1.6, rx=8))
    f.append(text(590, 45, "1. БЕЗ мертвої черги: блокування початку черги (Head-of-Line Blocking) та виснаження воркерів", size=13, bold=True, color=POS))

    # Черга зверху
    f.append(rect(50, 70, 420, 75, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
    f.append(text(260, 90, "Черга повідомлень (Queue)", size=11, bold=True))
    f.append(rect(70, 100, 70, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(105, 122, "M4: OK", size=10, bold=True, color=FIELD))
    f.append(rect(150, 100, 70, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(185, 122, "M3: OK", size=10, bold=True, color=FIELD))
    f.append(rect(230, 100, 70, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(265, 122, "M2: OK", size=10, bold=True, color=FIELD))
    f.append(rect(310, 100, 145, 35, fill="#ffe3e3", stroke=POS, sw=1.5, rx=4))
    f.append(text(382.5, 122, "M1: Отруйний (Panic)", size=10, bold=True, color=POS))

    # Воркери у верхній панелі
    f.append(fitbox(530, 65, 230, 45, "Воркер 1: Crash → Перезапуск", size=10, bold=True, fill="#ffe3e3", stroke=POS))
    f.append(fitbox(530, 115, 230, 45, "Воркер 2: Отримав M1 → Crash", size=10, bold=True, fill="#ffe3e3", stroke=POS))
    f.append(fitbox(530, 165, 230, 45, "Воркер 3: Отримав M1 → 100% CPU", size=10, bold=True, fill="#ffe3e3", stroke=POS))

    f.append(arrow(455, 115, 530, 85, color=POS, sw=1.5))
    f.append(arrow(455, 120, 530, 135, color=POS, sw=1.5))
    f.append(arrow(455, 125, 530, 185, color=POS, sw=1.5))

    # Наслідок зверху
    f.append(fitbox(790, 70, 350, 140,
                    "Наслідки нескінченних повторів (Requeue Loop):\n• 100% процесорного часу витрачається на одне бите повідомлення M1\n• Корисні задачі M2, M3, M4 заблоковані й голодують\n• Затримка обробки (End-to-End Latency) зростає до нескінченності\n• Каскадне падіння всього пулу воркерів через OOM / CrashLoop",
                    size=10, fill="#ffffff", stroke=POS))

    # Нижня панель: З DLQ (ізоляція та стабільність)
    f.append(rect(20, 255, 1140, 215, fill="#f4faf6", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(590, 280, "2. З мертвою чергою (DLQ): ліміт спроб, миттєва ізоляція та плавна обробка черги", size=13, bold=True, color=FIELD))

    # Черга знизу
    f.append(rect(50, 305, 340, 75, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
    f.append(text(220, 325, "Основна черга (Primary Queue)", size=11, bold=True))
    f.append(rect(70, 335, 75, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(107.5, 357, "M4: OK", size=10, bold=True, color=FIELD))
    f.append(rect(155, 335, 75, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(192.5, 357, "M3: OK", size=10, bold=True, color=FIELD))
    f.append(rect(240, 335, 75, 35, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(277.5, 357, "M2: OK", size=10, bold=True, color=FIELD))
    f.append(arrow(315, 352, 420, 352, color=FIELD, sw=1.6))

    # Воркери знизу
    f.append(fitbox(420, 305, 250, 50, "Воркер 1: Виконує M2 → ACK ✓", size=10, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(420, 365, 250, 50, "Воркер 2: Виконує M3 → ACK ✓", size=10, bold=True, fill=GOOD, stroke=FIELD))

    # DLQ знизу
    f.append(rect(50, 395, 340, 65, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(220, 415, "Мертва черга (Dead Letter Queue)", size=11, bold=True, color=POS))
    f.append(rect(110, 425, 220, 26, fill="#ffe3e3", stroke=POS, sw=1.2, rx=4))
    f.append(text(220, 442, "M1 (3 невдалі спроби) + Метадані", size=9, bold=True, color=POS))

    # Стрілка відкату в DLQ
    f.append(arrow(390, 320, 220, 395, color=POS, sw=1.5))
    f.append(text(340, 380, "NACK (max retries) → DLQ", size=9, color=POS, bold=True))

    # Результат знизу
    f.append(fitbox(710, 305, 430, 150,
                    "Переваги архітектури з DLQ:\n• Отруйне повідомлення M1 ізольоване після N спроб без зупинки системи\n• Задачі M2, M3, M4 виконуються паралельно без затримок і черги\n• Повні діагностичні дані про збій M1 збережено для аудиту та виправлення\n• Пропускна здатність системи (Throughput) залишається стабільною",
                    size=10, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, 'poison-pill-hol-blocking.svg'), W, H, *f)


# ── 3. Point-to-Point черги проти логів із партиціями (Kafka DLQ) ─────────────
def kafka_offset_vs_dlq():
    W, H = 1180, 510
    f = []

    # Ліва колонка: Point-to-Point (RabbitMQ / SQS)
    f.append(rect(20, 20, 560, 470, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(300, 48, "1. Point-to-Point черги (RabbitMQ / AWS SQS)", size=13, bold=True, color=INK))

    # Черга ліворуч
    f.append(rect(40, 75, 520, 110, fill=COOL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(300, 98, "Основна черга з індивідуальними квитанціями", size=11, bold=True))
    p_msgs = [("M1 (OK)", 60, GOOD, FIELD), ("M2 (FAIL)", 185, "#ffe3e3", POS), ("M3 (OK)", 310, GOOD, FIELD), ("M4 (OK)", 435, GOOD, FIELD)]
    for lbl, mx, bg_c, strk in p_msgs:
        f.append(rect(mx, 115, 110, 40, fill=bg_c, stroke=strk, sw=1.2, rx=4))
        f.append(text(mx + 55, 140, lbl, size=10, bold=True, color=INK))

    f.append(fitbox(40, 200, 520, 110,
                    "Механізм ізоляції в класичних чергах:\n• Брокер відстежує стан кожного повідомлення окремо\n• Невдале повідомлення M2 вибірково вилучається з черги після N спроб\n• Сусідні повідомлення M1, M3, M4 успішно підтверджуються (ACK)\n• Повідомлення M2 атомарно маршрутизується в DLQ без порушення черги",
                    size=10, fill=FILL, stroke=LINE))

    # DLQ ліворуч
    f.append(rect(40, 325, 520, 145, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(300, 350, "Окрема черга DLQ (Dead Letter Queue)", size=11, bold=True, color=POS))
    f.append(fitbox(60, 365, 480, 85,
                    "Ізольоване повідомлення [M2] зберігає свій початковий стан.\nВиправлення та повторна відправка (Redrive) відбуваються незалежно,\nале можуть спричинити порушення первинного порядку виконання (Out-of-Order).",
                    size=10, fill="#ffffff", stroke=POS))

    # Права колонка: Partitioned Logs (Kafka / Pulsar)
    f.append(rect(600, 20, 560, 470, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(880, 48, "2. Журнали з партиціями (Apache Kafka / Event Log)", size=13, bold=True, color=INK))

    # Лог праворуч
    f.append(rect(620, 75, 520, 110, fill=WARN, stroke=LINE, sw=1.3, rx=6))
    f.append(text(880, 98, "Незмінний лог партиції (Append-only Log Partition)", size=11, bold=True))
    k_offsets = [("Off: 40 ✓", 640, GOOD), ("Off: 41 ⚡", 765, "#ffe3e3"), ("Off: 42 ⏳", 890, FILL), ("Off: 43 ⏳", 1015, FILL)]
    for lbl, mx, bg_c in k_offsets:
        f.append(rect(mx, 115, 110, 40, fill=bg_c, stroke=LINE, sw=1.2, rx=4))
        f.append(text(mx + 55, 140, lbl, size=10, bold=True, color=INK))

    f.append(fitbox(620, 200, 520, 110,
                    "Фундаментальна дилема логів із партиціями:\n• Лог незмінний: неможливо «видалити» або «перемістити» офсет 41\n• Консюмер може просунути committed offset вперед лише послідовно\n• Якщо офсет 41 не обробляється, консюмер зависає (зупинка партиції)\n• Вирішення: клієнт публікує подію в topic-orders-dlq і комітить офсет 42",
                    size=10, fill=FILL, stroke=LINE))

    # DLQ Топік праворуч
    f.append(rect(620, 325, 520, 145, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(880, 350, "Окремий топік: topic-orders-dlq", size=11, bold=True, color=POS))
    f.append(fitbox(640, 365, 480, 85,
                    "Компроміс узгодженості (Ordering vs Availability):\n• Офсет 41 перенесено в топік DLQ, консюмер пішов далі до 42, 43\n• Якщо 41 — це CreateUser, а 42 — UpdateUser, виникає розрив стану!\n• Повторне відтворення з DLQ вимагає ідемпотентності та версіонування.",
                    size=10, fill="#ffffff", stroke=POS))

    render(os.path.join(OUT, 'kafka-offset-vs-dlq.svg'), W, H, *f)


# ── 4. Безпечний Redrive та захисні бар'єри ───────────────────────────────────
def dlq_redrive_and_safety_guards():
    W, H = 1180, 480
    f = []

    # Тло
    f.append(rect(20, 20, 1140, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(590, 48, "Архітектура безпечного відновлення повідомлень з DLQ (Safe Redrive Pipeline)", size=14, bold=True, color="#334155"))

    # Зліва: Сховище DLQ
    f.append(rect(40, 80, 210, 350, fill="#fff5f5", stroke=POS, sw=1.6, rx=8))
    f.append(text(145, 110, "Сховище DLQ", size=13, bold=True, color=POS))
    f.append(text(145, 130, "Накопичені помилки", size=10, color=MUTED, italic=True))

    dlq_items = [("Err #1042: Schema Mismatch", 155), ("Err #1043: Timeout Downstream", 215), ("Err #1044: Divide by Zero", 275), ("Err #1045: DB Deadlock", 335)]
    for label, my in dlq_items:
        f.append(rect(50, my, 190, 45, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
        f.append(text(145, my + 27, label, size=9, bold=True, color=INK))

    # Стрілка в конвеєр відновлення
    f.append(arrow(250, 255, 300, 255, color=POS, sw=1.6))
    f.append(text(275, 245, "Read", size=10, color=POS, bold=True))

    # Центр: 4 захисні бар'єри Redrive Контролера
    f.append(rect(300, 80, 550, 350, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(575, 108, "Контролер відновлення (Redrive Engine & Safety Guards)", size=12, bold=True, color=INK))

    # Бар'єр 1: Патч та валідація схеми
    f.append(fitbox(320, 125, 510, 55,
                    "1. Патчинг та валідація схеми даних\nВиправлення дефектних полів або міграція версії схеми",
                    size=10, fill=COOL, stroke=LINE))

    # Бар'єр 2: Обмежувач швидкості
    f.append(fitbox(320, 190, 510, 55,
                    "2. Обмежувач швидкості (Rate Limiter / Token Bucket)\nДозована подача повідомлень для захисту первинної системи",
                    size=10, fill=WARN, stroke=LINE))

    # Бар'єр 3: Захист від зациклення
    f.append(fitbox(320, 255, 510, 55,
                    "3. Захист від зациклення (Redrive Loop Breaker)\nКонтроль x-redrive-count та скидання безнадійних у Parking Lot",
                    size=10, fill="#ffe3e3", stroke=POS))

    # Бар'єр 4: Ідемпотентність
    f.append(fitbox(320, 320, 510, 55,
                    "4. Перевірка ідемпотентності (Idempotency Guard)\nЗапобігання повторному списанню для частково виконаних операцій",
                    size=10, fill=GOOD, stroke=FIELD))

    f.append(text(575, 405, "Оператор / Автоматична політика відновлення", size=10, color=MUTED, italic=True))

    # Справа: Основна черга та Parking Lot
    f.append(rect(890, 80, 250, 160, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(1015, 108, "Основна черга (Primary Queue)", size=12, bold=True, color=FIELD))
    f.append(fitbox(905, 125, 220, 100,
                    "Успішно відновлені задачі\nнадходять до воркерів\nбез лавинного ефекту\nта блокування черги.",
                    size=10, fill="#ffffff", stroke=FIELD))

    f.append(rect(890, 270, 250, 160, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(1015, 298, "Холодний архів (Parking Lot)", size=12, bold=True, color=MUTED))
    f.append(fitbox(905, 315, 220, 100,
                    "Безнадійно пошкоджені\nзаписи зберігаються в S3\nдля аудиту без переповнення\nсховища брокера.",
                    size=10, fill="#ffffff", stroke=MUTED))

    # Стрілки направо
    f.append(arrow(850, 160, 890, 160, color=FIELD, sw=1.6))
    f.append(text(870, 148, "Re-inject", size=9, color=FIELD, bold=True))

    f.append(arrow(850, 350, 890, 350, color=MUTED, sw=1.6))
    f.append(text(870, 338, "Discard", size=9, color=MUTED, bold=True))

    render(os.path.join(OUT, 'dlq-redrive-and-safety-guards.svg'), W, H, *f)


if __name__ == '__main__':
    dlq_lifecycle_and_architecture()
    poison_pill_hol_blocking()
    kafka_offset_vs_dlq()
    dlq_redrive_and_safety_guards()
    print("OK: all 4 figures rendered.")
