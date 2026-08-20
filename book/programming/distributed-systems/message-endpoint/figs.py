# -*- coding: utf-8 -*-
"""Фігури до теми «Message Endpoint (Кінцева точка обміну повідомленнями)»."""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / неконтрольований потік
COOL = "#eaf0fd"   # домен / сервіси / ядро
GOOD = "#e8f6ee"   # кінцева точка / успіх / буфер
WARN = "#fef9e7"   # черга / брокер / сховище


# ── 1. Анатомія Message Endpoint: розчеплення домену й брокера ─────────────────
def endpoint_anatomy():
    W, H = 1140, 520
    f = []

    # Заголовок та фон
    f.append(rect(20, 15, 1100, 490, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 45, "Анатомія Message Endpoint: подвійний міст між доменом і чергою", size=15, bold=True, color=INK))

    # Ліва колонка: Доменне ядро (Application / Domain Layer)
    f.append(rect(45, 80, 240, 395, fill=COOL, stroke=NEG, sw=1.5, rx=6))
    f.append(text(165, 110, "Доменний шар застосунку", size=13, bold=True, color=NEG))
    f.append(fitbox(60, 130, 210, 50, "OrderService\n• processOrder(order)\n• cancelOrder(id)", size=11, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(60, 210, 210, 55, "Доменні сутності (Entity/DTO)\n• Order, PaymentResult\n• Чисті структури пам'яті", size=11, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(60, 295, 210, 50, "Транзакційні межі (ACID)\n• Репозиторій банку/БД\n• Синхронні виклики", size=11, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(60, 375, 210, 75, "Вимоги домену:\n• Жодних сокетів і фреймів\n• Немає брокерських ACK\n• Детерміновані винятки", size=10.5, fill=GOOD, stroke=FIELD, sw=1.1))

    # Центральний блок: MESSAGE ENDPOINT
    f.append(rect(340, 80, 460, 395, fill=GOOD, stroke=FIELD, sw=1.8, rx=6))
    f.append(text(570, 110, "MESSAGE ENDPOINT (Шлюз, Мапер, Адаптер)", size=13.5, bold=True, color=FIELD))

    # Вихідний потік (Outbound)
    f.append(rect(360, 130, 420, 100, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(570, 150, "Вихідний шлюз (Messaging Gateway & Outbox)", size=11.5, bold=True, color=INK))
    f.append(text(570, 172, "1. Отримує Order від домену → 2. Мапер серіалізує в JSON/Proto", size=10.5, color=MUTED))
    f.append(text(570, 192, "3. Додає заголовки (Trace-ID, Message-ID) → 4. Публікує в Outbox/Канал", size=10.5, color=MUTED))
    f.append(text(570, 212, "Результат: Домен викликає звичайний метод інтерфейсу без AMQP-коду", size=10, bold=True, color=FIELD))

    # Вхідний потік (Inbound)
    f.append(rect(360, 245, 420, 135, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(570, 265, "Вхідний активатор (Service Activator & Listener)", size=11.5, bold=True, color=INK))
    f.append(text(570, 287, "1. Читає фрейм із черги → 2. Перевіряє ідемпотентність (Inbox-кеш)", size=10.5, color=MUTED))
    f.append(text(570, 307, "3. Десеріалізує Payload → 4. Кличе OrderService.processOrder()", size=10.5, color=MUTED))
    f.append(text(570, 327, "5. Фіксує успіх/помилку → 6. Шле ACK/NACK або редирект у DLQ", size=10.5, color=MUTED))
    f.append(text(570, 355, "Контроль потоку: префетч (Prefetch Buffer) та пул воркерів", size=10.5, bold=True, color=POS))

    # Нижній статус ендпоінта
    f.append(fitbox(360, 395, 420, 65, "Ендпоінт інкапсулює: мережеві сокети, серіалізацію, повтори (Retries),\nрозподілені транзакції, дедуплікацію та керування потоками ОС.", size=10.5, fill=WARN, stroke=LINE, sw=1.1))

    # Права колонка: Інфраструктура черг (Messaging Infrastructure)
    f.append(rect(850, 80, 245, 395, fill=WARN, stroke=LINE, sw=1.5, rx=6))
    f.append(text(972, 110, "Брокер / Мережевий канал", size=13, bold=True, color=INK))
    f.append(fitbox(865, 130, 215, 55, "Черги й Теми (Channels)\n• AMQP Queue / Exchange\n• Kafka Topic / Partition", size=11, fill=BG, stroke=LINE, sw=1.1))
    f.append(fitbox(865, 205, 215, 60, "Мережеві фрейми (Wire Msg)\n• Бінарний payload (байти)\n• Заголовки (Headers)\n• Delivery Tag, Offset", size=10.5, fill=BG, stroke=LINE, sw=1.1))
    f.append(fitbox(865, 285, 215, 55, "Протокольні операції\n• basic.ack / basic.nack\n• Commit offset / Heartbeat", size=10.5, fill=BG, stroke=LINE, sw=1.1))
    f.append(fitbox(865, 360, 215, 95, "Dead-Letter Queue (DLQ)\n• Сховище отруйних листів\n• Невалідовані повідомлення\n• Вичерпані ліміти повторів", size=10.5, fill=WARM, stroke=POS, sw=1.1))

    # Стрілки взаємодії
    f.append(arrow(285, 180, 355, 180, color=FIELD, sw=2))
    f.append(arrow(780, 180, 845, 180, color=FIELD, sw=2))
    f.append(arrow(845, 310, 785, 310, color=POS, sw=2))
    f.append(arrow(355, 310, 290, 310, color=POS, sw=2))

    render(os.path.join(OUT, 'endpoint-anatomy.svg'), W, H, *f)


# ── 2. Моделі вичитування: Polling Consumer vs Event-Driven Consumer ──────────
def polling_vs_event_driven():
    W, H = 1140, 500
    f = []

    f.append(rect(20, 15, 1100, 470, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 42, "Моделі доставки: Polling Consumer (Pull) проти Event-Driven Consumer (Push)", size=15, bold=True, color=INK))

    # Ліва половина: Polling Consumer (Pull)
    f.append(rect(40, 75, 515, 390, fill=BG, stroke=NEG, sw=1.5, rx=6))
    f.append(text(297, 105, "1. Polling Consumer (Синхронний Pull)", size=13.5, bold=True, color=NEG))

    f.append(rect(60, 130, 180, 85, fill=COOL, stroke=NEG, sw=1.2, rx=5))
    f.append(text(150, 155, "Консюмер (Потік)", size=12, bold=True, color=NEG))
    f.append(text(150, 178, "while (running) {", size=10.5, color=INK))
    f.append(text(150, 198, "  msg = poll(timeout);", size=10.5, color=INK))

    f.append(rect(355, 130, 180, 85, fill=WARN, stroke=LINE, sw=1.2, rx=5))
    f.append(text(445, 155, "Брокер / Черга", size=12, bold=True, color=INK))
    f.append(text(445, 178, "[ Msg 3 ][ Msg 2 ][ Msg 1 ]", size=10.5, color=MUTED))
    f.append(text(445, 198, "Буфер на диску/пам'яті", size=10, color=MUTED))

    # Стрілки Pull
    f.append(arrow(240, 155, 350, 155, color=NEG, sw=1.8))
    f.append(text(295, 147, "1. poll() запит", size=10, color=NEG))
    f.append(arrow(350, 190, 245, 190, color=FIELD, sw=1.8))
    f.append(text(295, 182, "2. Відповідь (батч)", size=10, color=FIELD))

    f.append(fitbox(60, 235, 475, 110,
                    "Властивості Pull-моделі:\n"
                    "• Природний протитиск (Backpressure): консюмер бере рівно стільки, скільки встигає.\n"
                    "• Контроль паузи: легка реалізація батчингу та зупинки на час перевантаження БД.\n"
                    "• Недолік: латентність простою між інтервалами опитування або спалювання CPU на пустих циклах.",
                    size=10.5, fill=GOOD, stroke=FIELD, sw=1.1))

    f.append(fitbox(60, 360, 475, 85,
                    "Типове застосування: Apache Kafka (KafkaConsumer.poll()), AWS SQS (ReceiveMessage),\n"
                    "пакетна аналітична обробка великих масивів даних.",
                    size=10.5, fill=COOL, stroke=NEG, sw=1.1))

    # Права половина: Event-Driven Consumer (Push)
    f.append(rect(585, 75, 515, 390, fill=BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(842, 105, "2. Event-Driven Consumer (Асинхронний Push)", size=13.5, bold=True, color=POS))

    f.append(rect(605, 130, 180, 85, fill=WARN, stroke=LINE, sw=1.2, rx=5))
    f.append(text(695, 155, "Брокер / Сокет", size=12, bold=True, color=INK))
    f.append(text(695, 178, "Миттєва відправка", size=10.5, color=MUTED))
    f.append(text(695, 198, "push(msg) у сокет", size=10.5, color=MUTED))

    f.append(rect(900, 130, 180, 85, fill=WARM, stroke=POS, sw=1.2, rx=5))
    f.append(text(990, 155, "Message Listener", size=12, bold=True, color=POS))
    f.append(text(990, 178, "onMessage(msg) {", size=10.5, color=INK))
    f.append(text(990, 198, "  handleAsync(msg);", size=10.5, color=INK))

    # Стрілки Push
    f.append(arrow(785, 160, 895, 160, color=POS, sw=2))
    f.append(text(840, 150, "1. Подія (Push)", size=10, color=POS))
    f.append(arrow(895, 195, 790, 195, color=FIELD, sw=1.8))
    f.append(text(840, 187, "2. basic.ack", size=10, color=FIELD))

    f.append(fitbox(605, 235, 475, 110,
                    "Властивості Push-моделі:\n"
                    "• Мінімальна латентність: повідомлення надходить негайно після публікації в чергу.\n"
                    "• Небезпека затоплення (OOM): якщо швидкість надходження > швидкості обробки,\n"
                    "  пам'ять процесу вичерпується без ліміту префетчу (Prefetch QoS limit).\n"
                    "• Обов'язкова наявність пулу воркерів та явного кредитного контролю (Credit Flow).",
                    size=10.5, fill=WARM, stroke=POS, sw=1.1))

    f.append(fitbox(605, 360, 475, 85,
                    "Типове застосування: RabbitMQ (basic.consume / Spring @RabbitListener),\n"
                    "JMS MessageListener, gRPC Streaming, реалтайм-сервіси з низькою латентністю.",
                    size=10.5, fill=GOOD, stroke=FIELD, sw=1.1))

    render(os.path.join(OUT, 'polling-vs-event-driven.svg'), W, H, *f)


# ── 3. Багатонитковість, префетч і збереження порядку за ключем ───────────────
def endpoint_threading_ordering():
    W, H = 1140, 520
    f = []

    f.append(rect(20, 15, 1100, 490, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 42, "Багатониткова обробка в Endpoint: збереження послідовності за Partition Key", size=15, bold=True, color=INK))

    # Лівий блок: Наївний спільний пул (Race Condition / Гонка стану)
    f.append(rect(40, 75, 515, 405, fill=BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(297, 105, "Наївний спільний пул (Гонка стану)", size=13, bold=True, color=POS))

    f.append(rect(60, 125, 150, 110, fill=WARN, stroke=LINE, sw=1.1, rx=4))
    f.append(text(135, 148, "Черга подій", size=11, bold=True, color=INK))
    f.append(text(135, 172, "1. [User#42: Created]", size=9.5, color=INK))
    f.append(text(135, 195, "2. [User#42: Paid]", size=9.5, color=INK))
    f.append(text(135, 218, "3. [User#42: Canceled]", size=9.5, color=INK))

    f.append(rect(360, 125, 175, 110, fill=WARM, stroke=POS, sw=1.1, rx=4))
    f.append(text(447, 148, "Спільний пул ниток", size=11, bold=True, color=POS))
    f.append(text(447, 172, "Нитка A → Подія 1 (зависла)", size=9.5, color=INK))
    f.append(text(447, 195, "Нитка B → Подія 2 (виконалася)", size=9.5, color=INK))
    f.append(text(447, 218, "Нитка C → Подія 3 (виконалася)", size=9.5, color=INK))

    # Стрілки
    f.append(arrow(210, 172, 355, 172, color=POS, sw=1.5))
    f.append(arrow(210, 195, 355, 195, color=POS, sw=1.5))
    f.append(arrow(210, 218, 355, 218, color=POS, sw=1.5))

    f.append(fitbox(60, 255, 475, 100,
                    "Катастрофа неупорядкованості:\n"
                    "• Подія «Оплачено» або «Скасовано» обганяє повільну подію «Створено».\n"
                    "• Доменна сутність User#42 потрапляє в некоректний стан (скасування неіснуючого замовлення).\n"
                    "• Блокування всієї черги однією ниткою вбиває паралелізм.",
                    size=10.5, fill=WARM, stroke=POS, sw=1.1))

    f.append(fitbox(60, 370, 475, 90,
                    "Результат: Застосування єдиного логічного каналу без прив'язки до ключа агрегата\n"
                    "руйнує причинно-наслідковий зв'язок бізнес-операцій.",
                    size=10.5, fill=FILL, stroke=LINE, sw=1.1))

    # Правий блок: Диспетчеризація з Partition Affinity (Ключова прив'язка)
    f.append(rect(585, 75, 515, 405, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(842, 105, "Key Affinity / Шардований диспетчер", size=13, bold=True, color=FIELD))

    # Хеш-розподільник
    f.append(rect(605, 130, 135, 105, fill=WARN, stroke=LINE, sw=1.1, rx=4))
    f.append(text(672, 155, "Вхідний потік", size=11, bold=True, color=INK))
    f.append(text(672, 178, "User#42 (Hash=0)", size=9.5, color=INK))
    f.append(text(672, 200, "User#99 (Hash=1)", size=9.5, color=INK))
    f.append(text(672, 222, "User#17 (Hash=2)", size=9.5, color=INK))

    f.append(rect(770, 145, 95, 75, fill=COOL, stroke=NEG, sw=1.2, rx=4))
    f.append(text(817, 172, "Хешування", size=10.5, bold=True, color=NEG))
    f.append(text(817, 192, "hash(key) % N", size=10, color=INK))

    f.append(rect(900, 125, 180, 115, fill=GOOD, stroke=FIELD, sw=1.1, rx=4))
    f.append(text(990, 145, "Виділені черги воркерів", size=10.5, bold=True, color=FIELD))
    f.append(text(990, 168, "Worker Queue 0 (User#42)", size=9.5, color=INK))
    f.append(text(990, 190, "Worker Queue 1 (User#99)", size=9.5, color=INK))
    f.append(text(990, 212, "Worker Queue 2 (User#17)", size=9.5, color=INK))

    f.append(arrow(740, 182, 765, 182, color=LINE, sw=1.5))
    f.append(arrow(865, 182, 895, 182, color=FIELD, sw=1.5))

    f.append(fitbox(605, 255, 475, 100,
                    "Гарантії порядку та паралелізму:\n"
                    "• Усі повідомлення одного Aggregate ID (наприклад, User#42) завжди потрапляють в одну нитку.\n"
                    "• Сувора послідовність (FIFO) всередині конкретного сутності без глобальних локів.\n"
                    "• Різні користувачі (User#42 та User#99) обробляються абсолютно паралельно на різних ядрах CPU.",
                    size=10.5, fill=GOOD, stroke=FIELD, sw=1.1))

    f.append(fitbox(605, 370, 475, 90,
                    "Формула префетчу: Розмір черги воркера B = Bandwidth × Latency. При перевищенні High Watermark\n"
                    "ендпоінт тимчасово призупиняє вичитування з мережевого сокета (TCP/AMQP Backpressure).",
                    size=10.5, fill=COOL, stroke=NEG, sw=1.1))

    render(os.path.join(OUT, 'endpoint-threading-ordering.svg'), W, H, *f)


# ── 4. Межі транзакцій: Transactional Outbox та Idempotent Inbox ─────────────
def transactional_outbox_inbox():
    W, H = 1140, 520
    f = []

    f.append(rect(20, 15, 1100, 490, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(570, 42, "Транзакційні межі Message Endpoint: Outbox і Inbox патерни", size=15, bold=True, color=INK))

    # Ліва система: Сервіс-відправник (Transactional Outbox)
    f.append(rect(40, 75, 430, 405, fill=BG, stroke=NEG, sw=1.5, rx=6))
    f.append(text(255, 105, "1. Відправник: Transactional Outbox Endpoint", size=12.5, bold=True, color=NEG))

    f.append(rect(60, 130, 390, 120, fill=COOL, stroke=NEG, sw=1.2, rx=5))
    f.append(text(255, 150, "Єдина локальна транзакція БД (ACID Commit)", size=11, bold=True, color=NEG))
    f.append(rect(75, 168, 165, 65, fill=BG, stroke=LINE, sw=1, rx=4))
    f.append(text(157, 190, "Бізнес-таблиця", size=10.5, bold=True, color=INK))
    f.append(text(157, 212, "INSERT INTO orders ...", size=9.5, color=MUTED))

    f.append(rect(270, 168, 165, 65, fill=BG, stroke=FIELD, sw=1, rx=4))
    f.append(text(352, 190, "Таблиця Outbox", size=10.5, bold=True, color=FIELD))
    f.append(text(352, 212, "INSERT INTO outbox_msg ...", size=9.5, color=MUTED))

    f.append(rect(60, 270, 390, 80, fill=GOOD, stroke=FIELD, sw=1.2, rx=5))
    f.append(text(255, 292, "Фоновий релей (CDC / Outbox Poller)", size=11, bold=True, color=FIELD))
    f.append(text(255, 315, "1. Вичитує нові повідомлення з таблиці outbox_msg", size=10, color=INK))
    f.append(text(255, 335, "2. Публікує в брокер → 3. Видаляє/позначає як відправлені", size=10, color=INK))

    f.append(arrow(255, 250, 255, 270, color=FIELD, sw=1.8))

    f.append(fitbox(60, 365, 390, 100,
                    "Подолання проблеми Dual-Write:\n"
                    "Неможливо атомарно зберегти запис у БД і зробити `channel.publish()` у мережу.\n"
                    "Outbox Endpoint гарантує: якщо замовлення збережено в БД, повідомлення\n"
                    "ГАРАНТОВАНО потрапить у чергу (At-least-once delivery).",
                    size=10, fill=COOL, stroke=NEG, sw=1.1))

    # Центральний брокер
    f.append(rect(490, 190, 160, 140, fill=WARN, stroke=LINE, sw=1.5, rx=6))
    f.append(text(570, 220, "Брокер черг", size=12, bold=True, color=INK))
    f.append(text(570, 245, "Kafka / RabbitMQ", size=10.5, color=MUTED))
    f.append(text(570, 270, "At-least-once", size=10.5, bold=True, color=POS))
    f.append(text(570, 295, "(Можливі дублікати)", size=10, color=POS))

    # Стрілки через брокер
    f.append(arrow(450, 305, 485, 280, color=FIELD, sw=2))
    f.append(arrow(650, 280, 685, 305, color=POS, sw=2))

    # Права система: Сервіс-отримувач (Idempotent Inbox)
    f.append(rect(670, 75, 430, 405, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(885, 105, "2. Отримувач: Idempotent Inbox Endpoint", size=12.5, bold=True, color=FIELD))

    f.append(rect(690, 130, 390, 120, fill=GOOD, stroke=FIELD, sw=1.2, rx=5))
    f.append(text(885, 150, "Вхідний фільтр дедуплікації (Inbox Table)", size=11, bold=True, color=FIELD))
    f.append(text(885, 175, "1. Перевірка: SELECT 1 FROM inbox WHERE msg_id = ?", size=10, color=INK))
    f.append(text(885, 198, "2. Якщо існує → миттєвий ACK без виклику бізнес-домену (Дубль!)", size=10, bold=True, color=POS))
    f.append(text(885, 225, "3. Якщо нове → відкриття транзакції та виклик OrderService", size=10, color=FIELD))

    f.append(rect(690, 270, 390, 80, fill=COOL, stroke=NEG, sw=1.2, rx=5))
    f.append(text(885, 292, "Атомарне виконання та фіксація", size=11, bold=True, color=NEG))
    f.append(text(885, 315, "INSERT INTO inbox (msg_id, processed_at) VALUES (?, NOW())", size=9.5, color=INK))
    f.append(text(885, 335, "UPDATE accounts SET balance = balance - amount ...", size=9.5, color=INK))

    f.append(arrow(885, 250, 885, 270, color=NEG, sw=1.8))

    f.append(fitbox(690, 365, 390, 100,
                    "Ефективна семантика Exactly-Once на рівні бізнесу:\n"
                    "Комбінація Outbox на стороні відправника та Idempotent Inbox на стороні отримувача\n"
                    "нівелює недоліки ненадійних мереж та повторних доставок.\n"
                    "Доменне ядро отримує кожну бізнес-подію рівно один раз.",
                    size=10, fill=GOOD, stroke=FIELD, sw=1.1))

    render(os.path.join(OUT, 'transactional-outbox-inbox.svg'), W, H, *f)


def main():
    endpoint_anatomy()
    polling_vs_event_driven()
    endpoint_threading_ordering()
    transactional_outbox_inbox()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
