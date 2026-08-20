# -*- coding: utf-8 -*-
"""Фігури теми «Патерн агрегації та ресеквенсингу повідомлень (Message Aggregator)». Вивід — ./img/*.svg"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"


# ── 1. aggregator-architecture-overview: Загальна архітектура агрегатора ────
def fig_aggregator_architecture():
    W, H = 940, 480
    f = []

    f.append(text(470, 28, "Архітектура агрегатора повідомлень: кореляція, буферизація та редукція", size=14, bold=True, color=INK))

    # Ліва колонка: Джерела повідомлень (асинхронні воркери)
    f.append(rect(15, 55, 210, 405, fill=GRAY_F, stroke=LINE, sw=1.2, rx=8))
    f.append(text(120, 80, "Асинхронні джерела подій", size=11.5, bold=True, color=INK))

    b_s1, _, _ = textbox(120, 135, "Сервіс авіаквитків\nMsg(id: A1, corr: 'ORD-901',\n    seq: 1/3, lat: 280 ms)", size=9.5, min_w=185, fill=BLUE_F, stroke=NEG)
    b_s2, _, _ = textbox(120, 220, "Сервіс готелів\nMsg(id: H1, corr: 'ORD-901',\n    seq: 2/3, lat: 45 ms)", size=9.5, min_w=185, fill=BLUE_F, stroke=NEG)
    b_s3, _, _ = textbox(120, 305, "Сервіс прокату авто\nMsg(id: C1, corr: 'ORD-901',\n    seq: 3/3, lat: 1200 ms)", size=9.5, min_w=185, fill=BLUE_F, stroke=NEG)
    b_s4, _, _ = textbox(120, 390, "Паралельні сесії\nMsg(id: X1, corr: 'ORD-902',\n    seq: 1/2, lat: 80 ms)", size=9.5, min_w=185, fill=FILL, stroke=MUTED)
    f.extend([b_s1, b_s2, b_s3, b_s4])

    # Стрілки у вхідний потік
    f.append(arrow(215, 135, 270, 200, color=NEG, sw=1.5))
    f.append(arrow(215, 220, 270, 220, color=NEG, sw=1.5))
    f.append(arrow(215, 305, 270, 240, color=NEG, sw=1.5))
    f.append(arrow(215, 390, 270, 260, color=MUTED, sw=1.5))

    # Центральна панель: Message Aggregator
    f.append(rect(275, 55, 410, 405, fill=GRAY_F, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(480, 80, "Message Aggregator (Диспетчер стану)", size=12.5, bold=True, color=FIELD))

    # Кореляційні комірки (Buckets)
    b_b1, _, _ = textbox(480, 150, "Кореляційний кошик: 'ORD-901'\n• Отримано: [Seq 2/3, Seq 1/3, Seq 3/3]\n• Дедуплікація: Bitset / Bloom Filter\n• Таймер дедлайну: 3000 ms (залишилось 1800 ms)\n• Стан: ПОВНИЙ НАБІР (3 з 3)", size=9.5, bold=True, min_w=370, fill=GREEN_F, stroke=FIELD, sw=1.5)
    
    b_b2, _, _ = textbox(480, 260, "Кореляційний кошик: 'ORD-902'\n• Отримано: [Seq 1/2]\n• Очікування: Seq 2/2\n• Таймер бездіяльності: 500 ms (пройшло 80 ms)\n• Стан: ОЧІКУВАННЯ (1 з 2)", size=9.5, min_w=370, fill=WARN_F, stroke="#d35400")
    
    b_eval, _, _ = textbox(480, 365, "Механізм оцінки завершення (Evaluator):\n1. Числа: Count == ExpectedTotal (3 == 3) -> ТАК!\n2. Предикат: FIN-прапорець / Кворум статусів\n3. Редуктор: Злиття ваучерів у єдиний OrderAggregate", size=9.5, bold=True, min_w=370, fill=FILL, stroke=LINE)
    f.extend([b_b1, b_b2, b_b3 if 'b_b3' in locals() else b_eval])

    # Стрілка на вихід
    f.append(arrow(685, 150, 725, 230, color=FIELD, sw=2.2))

    # Права колонка: Вихідний зведений результат
    f.append(rect(730, 55, 195, 405, fill=GRAY_F, stroke=LINE, sw=1.2, rx=8))
    f.append(text(827, 80, "Вихідний канал", size=11.5, bold=True, color=INK))

    b_out1, _, _ = textbox(827, 175, "Зведене замовлення\nCompositeOrder\n• order_id: 'ORD-901'\n• items: [Flight, Hotel, Car]\n• total_amount: 14 500 грн\n• status: 'READY_TO_CAPTURE'", size=9.5, bold=True, min_w=175, fill=GREEN_F, stroke=FIELD)
    
    b_out2, _, _ = textbox(827, 335, "Споживач результату:\n• Білінг / Кліринг\n• Генератор PDF квитка\n• Сповіщення клієнта\n\n(Нуль часткових відмов)", size=9.5, min_w=175, fill=BLUE_F, stroke=NEG)
    f.extend([b_out1, b_out2])

    render(out("aggregator-architecture-overview.svg"), W, H, *f)


# ── 2. state-machine-lifecycle: Життєвий цикл кореляційного кошика ─────────
def fig_state_machine_lifecycle():
    W, H = 940, 480
    f = []

    f.append(text(470, 28, "Скінченний автомат агрегаційного кошика: переходи, тайм-аути та надгробки", size=14, bold=True, color=INK))

    # Стан 1: INIT / COLLECTING
    b1, _, _ = textbox(160, 130, "1. COLLECTING (Збирання)\n• Створення кошика за першим CorrID\n• Старт таймерів дедлайну та бездіяльності\n• Буферизація повідомлень у сховищі\n• Фільтрація дублікатів (Idempotency)", size=10, bold=True, min_w=240, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(b1)

    # Перехід 1 -> 2: Отримано повний комплект
    f.append(arrow(280, 130, 410, 130, color=FIELD, sw=2.0))
    f.append(text(345, 115, "Count == Total / FIN", size=9.5, bold=True, color=FIELD))

    # Стан 2: COMPLETED
    b2, _, _ = textbox(540, 130, "2. COMPLETED (Завершено)\n• Зупинка фонових таймерів\n• Агрегація/редукція корисного навантаження\n• Атомарна публікація CompositeMessage\n• Створення запису надгробка (Tombstone)", size=10, bold=True, min_w=240, fill=GREEN_F, stroke=FIELD, sw=1.8)
    f.append(b2)

    # Перехід 1 -> 3: Сплив тайм-ауту
    f.append(arrow(160, 200, 160, 285, color=POS, sw=2.0))
    f.append(text(215, 245, "Сплив дедлайну\nабо Inactivity TTL", size=9.5, bold=True, color=POS))

    # Стан 3: TIMED_OUT / PARTIAL
    b3, _, _ = textbox(160, 360, "3. TIMED_OUT (Частковий збір)\n• Оцінка політики: Drop vs Partial vs DLQ\n• Відправка наявних елементів у DLQ\n• Запуск компенсувальної саги (Rollback)\n• Створення надгробка з прапорцем FAIL", size=10, bold=True, min_w=240, fill=RED_F, stroke=POS, sw=1.5)
    f.append(b3)

    # Перехід 2 -> 4 та 3 -> 4
    f.append(arrow(540, 200, 540, 285, color=LINE, sw=1.8))
    f.append(text(595, 245, "Встановлення TTL\nнадгробка", size=9.5, color=MUTED))

    f.append(arrow(280, 360, 410, 360, color=LINE, sw=1.8))
    f.append(text(345, 345, "Ескалація збою", size=9.5, color=MUTED))

    # Стан 4: TOMBSTONE
    b4, _, _ = textbox(540, 360, "4. TOMBSTONE (Надгробок)\n• Зберігає факт закриття CorrID\n• Перехоплює запізнілі повідомлення (Stragglers)\n• Спрямовує «хвости» у DLQ без створення нового кошика\n• TTL надгробка: 2x–5x від максимального SLA", size=10, bold=True, min_w=240, fill=WARN_F, stroke="#d35400", sw=1.5)
    f.append(b4)

    # Перехід 4 -> 5: Остаточне очищення
    f.append(arrow(660, 360, 735, 360, color=LINE, sw=1.8))
    f.append(text(700, 345, "TTL сплив", size=9.5, color=MUTED))

    # Стан 5: PURGED
    b5, _, _ = textbox(835, 360, "5. PURGED\n(Видалено)\n• Звільнення RAM\n• Очищення диска\n• Запобігання витокам", size=9.5, min_w=150, fill=GRAY_F, stroke=LINE)
    f.append(b5)

    render(out("state-machine-lifecycle.svg"), W, H, *f)


# ── 3. resequencer-sliding-window: Механіка ресеквенсера та ковзного вікна ─
def fig_resequencer_window():
    W, H = 940, 460
    f = []

    f.append(text(470, 28, "Ресеквенсер повідомлень: буферизація, усунення прогалин та відновлення порядку", size=14, bold=True, color=INK))

    # Верхня панель: Вхідний неупорядкований потік
    f.append(rect(15, 55, 910, 90, fill=GRAY_F, stroke=LINE, sw=1.2, rx=8))
    f.append(text(470, 75, "Вхідний потік через ненадійну мережу (Out-of-Order Delivery)", size=11.5, bold=True, color=INK))

    f.append(rect(40, 90, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(80, 115, "Seq #1", size=10, bold=True, color=FIELD))

    f.append(rect(140, 90, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(180, 115, "Seq #2", size=10, bold=True, color=FIELD))

    f.append(rect(240, 90, 80, 40, fill=WARN_F, stroke="#d35400", sw=1.5, rx=4))
    f.append(text(280, 115, "Seq #4", size=10, bold=True, color="#d35400"))

    f.append(rect(340, 90, 80, 40, fill=WARN_F, stroke="#d35400", sw=1.5, rx=4))
    f.append(text(380, 115, "Seq #5", size=10, bold=True, color="#d35400"))

    f.append(rect(440, 90, 90, 40, fill=BLUE_F, stroke=NEG, sw=1.8, rx=4))
    f.append(text(485, 115, "Seq #3 (Затримка)", size=9, bold=True, color=NEG))

    f.append(rect(550, 90, 80, 40, fill=WARN_F, stroke="#d35400", sw=1.5, rx=4))
    f.append(text(590, 115, "Seq #7", size=10, bold=True, color="#d35400"))

    f.append(rect(650, 90, 80, 40, fill=WARN_F, stroke="#d35400", sw=1.5, rx=4))
    f.append(text(690, 115, "Seq #6", size=10, bold=True, color="#d35400"))

    f.append(text(810, 115, "Порядок прибуття:\n1 -> 2 -> 4 -> 5 -> 3...", size=9.5, color=MUTED))

    # Стрілка вниз
    f.append(arrow(470, 150, 470, 185, color=LINE, sw=2.0))

    # Середня панель: Resequencer Engine
    f.append(rect(15, 190, 910, 140, fill=GRAY_F, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(470, 210, "Стан внутрішнього буфера ресеквенсера (Next Expected Sequence = 3)", size=12, bold=True, color=FIELD))

    b_buf1, _, _ = textbox(190, 265, "Випущено в потік:\nSeq #1, Seq #2 (OK)\n\nПоточний покажчик:\nnext_seq = 3", size=9.5, min_w=200, fill=GREEN_F, stroke=FIELD)
    
    b_buf2, _, _ = textbox(470, 265, "Буфер очікування (PriorityQueue / Map):\n• Затримано: {4, 5}\n• Прогалина (Gap): очікується #3!\n• Gap Timeout: 250 ms до примусового пропуску\nПрибуття #3 запускає каскадну емісію: [3, 4, 5]", size=9.5, bold=True, min_w=300, fill=WARN_F, stroke="#d35400", sw=1.5)
    
    b_buf3, _, _ = textbox(770, 265, "Політика прогалин (Gaps):\n1. Strict: чекати до упору\n2. Timeout: пропустити #3, залогувати втрату\n3. NACK: запит на повтор відправнику", size=9.5, min_w=220, fill=FILL, stroke=LINE)
    f.extend([b_buf1, b_buf2, b_buf3])

    # Стрілка вниз
    f.append(arrow(470, 335, 470, 370, color=FIELD, sw=2.0))

    # Нижня панель: Вихідний строго впорядкований потік
    f.append(rect(15, 375, 910, 70, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(140, 415, "Вихідний монотонний потік:", size=11, bold=True, color=FIELD))

    f.append(rect(260, 390, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(300, 415, "Seq #1", size=10, bold=True, color=FIELD))

    f.append(rect(360, 390, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(400, 415, "Seq #2", size=10, bold=True, color=FIELD))

    f.append(rect(460, 390, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(500, 415, "Seq #3", size=10, bold=True, color=FIELD))

    f.append(rect(560, 390, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(600, 415, "Seq #4", size=10, bold=True, color=FIELD))

    f.append(rect(660, 390, 80, 40, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(700, 415, "Seq #5", size=10, bold=True, color=FIELD))

    f.append(text(820, 415, "Ідеальна послідовність\n(Strict Monotonic Order)", size=9.5, bold=True, color=FIELD))

    render(out("resequencer-sliding-window.svg"), W, H, *f)


# ── 4. storage-concurrency-topology: Збереження стану та шардування ────────
def fig_storage_topology():
    W, H = 940, 480
    f = []

    f.append(text(470, 28, "Топологія стану агрегатора: розподілене шардування без блокувань проти спільного сховища", size=13.5, bold=True, color=INK))

    # Ліва половина: Спільне централізоване сховище (Висока конкуренція)
    f.append(rect(15, 55, 445, 405, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(237, 80, "Централізований стан (Shared Store + Locks)", size=12, bold=True, color=POS))

    b1, _, _ = textbox(237, 140, "N незалежних воркерів-агрегаторів\nВипадкове читання з черги без прив'язки", size=10, min_w=380, fill=FILL, stroke=LINE)
    f.append(b1)

    f.append(arrow(237, 175, 237, 215, color=POS, sw=1.8))
    f.append(text(237, 195, "Блокування / CAS-конфлікти", size=9.5, color=POS))

    b2, _, _ = textbox(237, 275, "Спільна база даних / Redis Cluster:\n• SELECT ... FOR UPDATE (Рядкові блокування)\n• Мережевий RTT: 1.5–4.0 мс на кожен запис\n• Висока ймовірність Deadlocks при паралелізмі\n• Стеля масштабування: пропускна здатність БД", size=9.5, bold=True, min_w=380, fill=RED_F, stroke=POS, sw=1.5)
    f.append(b2)

    b3, _, _ = textbox(237, 395, "Наслідки: Висока затримка (Tail Latency p99),\nвузьке горло на спільних блокуваннях пам'яті", size=9.5, min_w=380, fill=WARN_F, stroke="#d35400")
    f.append(b3)

    # Права половина: Шардування за Correlation ID (Zero-Locking)
    f.append(rect(480, 55, 445, 405, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(702, 80, "Шардування за ключем (Partitioned by CorrID)", size=12, bold=True, color=FIELD))

    b4, _, _ = textbox(702, 140, "Брокер з партиціонуванням (Kafka / Rabbit Consistent Hash):\nКлюч маршрутизації = hash(CorrelationID)", size=10, min_w=380, fill=FILL, stroke=LINE)
    f.append(b4)

    f.append(arrow(702, 175, 702, 215, color=FIELD, sw=1.8))
    f.append(text(702, 195, "Строга ізоляція: 1 Partition -> 1 Thread", size=9.5, color=FIELD))

    b5, _, _ = textbox(702, 275, "Локальний стан воркера (In-Memory + RocksDB WAL):\n• Повна відсутність блокувань (Lock-Free Threading)\n• Затримка обробки: < 0.05 мс (O(1) Hash Map)\n• Локальний WAL забезпечує надійність при краху\n• Лінійне горизонтальне масштабування кластера", size=9.5, bold=True, min_w=380, fill=GREEN_F, stroke=FIELD, sw=1.5)
    f.append(b5)

    b6, _, _ = textbox(702, 395, "Переваги: Максимальний TPS (100k+ msg/sec),\nнульові блокування, передбачувана p99 затримка", size=9.5, min_w=380, fill=BLUE_F, stroke=NEG)
    f.append(b6)

    render(out("storage-concurrency-topology.svg"), W, H, *f)


if __name__ == "__main__":
    fig_aggregator_architecture()
    fig_state_machine_lifecycle()
    fig_resequencer_window()
    fig_storage_topology()
    print("Усі 4 фігури успішно згенеровано.")
