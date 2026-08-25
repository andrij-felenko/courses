# -*- coding: utf-8 -*-
"""Фігури до теми «Патерн вихідної скриньки (Transactional Outbox)».

Генерує 4 SVG діаграми:
1. dual-write-failure-modes.svg       — Пастка подвійного запису та сценарії неузгодженості
2. transactional-outbox-architecture.svg — Архітектура локальної транзакції та способи ретрансляції
3. outbox-cdc-pipeline.svg            — Конвеєр CDC на основі читання WAL-журналу
4. outbox-to-inbox-end-to-end.svg     — Наскрізний ланцюг: Outbox на видачі та Inbox на прийомі
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / втрата / фантом
COOL = "#eaf0fd"   # нейтральне / дані / сховище
GOOD = "#e8f6ee"   # успіх / атомарність / узгодженість
WARN = "#fef9e7"   # проміжне / черга / брокер


# ── 1. Пастка подвійного запису ─────────────────────────────────────────────
def fig_dual_write_failure_modes():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "ПАСТКА ПОДВІЙНОГО ЗАПИСУ: чому неможливо безпечно писати у два мережеві ресурси без 2PC",
                    size=14, bold=True, fill=COOL))

    # Сценарій А: Спершу БД, потім Брокер
    ax = 40.0
    ay = 80.0
    aw = 535.0
    ah = 460.0
    f.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(ax + 15, ay + 15, aw - 30, 36,
                    "СЦЕНАРІЙ А: Спершу фіксація в БД, потім надсилання в брокер",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.2))

    # Кроки сценарію А
    f.append(fitbox(ax + 25, ay + 65, aw - 50, 48,
                    "1. BEGIN TRANSACTION\n2. UPDATE accounts SET balance = balance - 1000;\n3. COMMIT;",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(ax + 25, ay + 130, aw - 50, 40,
                    "БАЗА ДАНИХ: Зміни успішно зафіксовано на диску",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    # Точка падіння
    f.append(fitbox(ax + 25, ay + 185, aw - 50, 52,
                    "⚡ АВАРІЙНА ВІДМОВА: знеструмлення / OOM-кілер / збій мережі\n(до того, як виконано broker.send())",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(ax + 25, ay + 255, aw - 50, 48,
                    "4. broker.send(\"MoneyWithdrawn\", payload) — НЕ ВИКОНАНО",
                    size=11, bold=True, fill="#ffffff", stroke=POS, sw=1.2))

    # Наслідок А
    f.append(fitbox(ax + 20, ay + 325, aw - 40, 115,
                    "НАСЛІДОК: ВТРАТА ПОДІЇ (Event Loss)\n\n"
                    "• Гроші з балансу списано назавжди\n"
                    "• Повідомлення в брокер ніколи не надійде\n"
                    "• Сервіс сповіщень та бухгалтерія не знають про факт списання\n"
                    "• Система переходить у фатально неузгоджений стан",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Сценарій Б: Спершу Брокер, потім БД
    bx = 605.0
    by = 80.0
    bw = 535.0
    bh = 460.0
    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(bx + 15, by + 15, bw - 30, 36,
                    "СЦЕНАРІЙ Б: Спершу надсилання в брокер, потім фіксація в БД",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.2))

    # Кроки сценарію Б
    f.append(fitbox(bx + 25, by + 65, bw - 50, 48,
                    "1. broker.send(\"MoneyWithdrawn\", payload) → ACK отримано\n"
                    "Повідомлення збережено у брокері та пішло до консюмерів",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(bx + 25, by + 130, bw - 50, 40,
                    "БРОКЕР: Подію вже прочитали інші мікросервіси",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    # Точка падіння
    f.append(fitbox(bx + 25, by + 185, bw - 50, 52,
                    "⚡ АВАРІЙНА ВІДМОВА: конфлікт унікальності / відкат транзакції\nабо збій БД під час виконання COMMIT",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(bx + 25, by + 255, bw - 50, 48,
                    "2. BEGIN ... UPDATE ... COMMIT — ВІДКОЧЕНО (ROLLBACK)",
                    size=11, bold=True, fill="#ffffff", stroke=POS, sw=1.2))

    # Наслідок Б
    f.append(fitbox(bx + 20, by + 325, bw - 40, 115,
                    "НАСЛІДОК: ФАНТОМНА ПОДІЯ (Phantom Event)\n\n"
                    "• У базі даних стан лишився незмінним (списання не було)\n"
                    "• Сервіс складського обліку вже відвантажує товар за подією\n"
                    "• Відкликати повідомлення з брокера неможливо\n"
                    "• Виникає матеріальний збиток через хибну реакцію споживачів",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Нижній висновок
    f.append(fitbox(40, 555, 1100, 48,
                    "ВИСНОВОК: Дві незалежні мережеві операції не можуть бути атомарними. "
                    "Будь-який порядок їх виклику містить вікно розриву.",
                    size=12.5, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'dual-write-failure-modes.svg'), W, H, *f)


# ── 2. Архітектура Transactional Outbox ──────────────────────────────────────
def fig_transactional_outbox_architecture():
    W, H = 1180, 640
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "АРХІТЕКТУРА TRANSACTIONAL OUTBOX: об'єднання мутації та події в одну локальну транзакцію",
                    size=14, bold=True, fill=COOL))

    # 1. Клієнтський запит
    f.append(fitbox(40, 90, 190, 60,
                    "КЛІЄНТ\nHTTP / gRPC запит\n(створити замовлення)",
                    size=11.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.5))

    f.append(arrow(230, 120, 290, 120, color=LINE, sw=2))

    # 2. Сервіс застосунку
    f.append(fitbox(290, 80, 250, 80,
                    "СЕРВІС ЗАСТОСУНКУ\n(Order Service)\n\nВідкриває локальну транзакцію",
                    size=12, bold=True, fill=COOL, stroke=LINE, sw=1.6))

    # Стрілка вниз до транзакції
    f.append(arrow(415, 160, 415, 200, color=FIELD, sw=2))

    # 3. Межа локальної транзакції бази даних
    tx_x, tx_y, tx_w, tx_h = 240.0, 200.0, 350.0, 230.0
    f.append(rect(tx_x, tx_y, tx_w, tx_h, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(fitbox(tx_x + 15, tx_y + 10, tx_w - 30, 28,
                    "ЄДИНА ЛОКАЛЬНА ACID-ТРАНЗАКЦІЯ",
                    size=12, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5))

    # Дві таблиці всередині транзакції
    f.append(fitbox(tx_x + 20, tx_y + 48, tx_w - 40, 60,
                    "Таблиця бізнес-сутностей (orders)\nINSERT INTO orders (id, user_id, status)\nVALUES (42, 814, 'PAID')",
                    size=10.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(tx_x + 20, tx_y + 118, tx_w - 40, 60,
                    "Таблиця вихідних подій (outbox)\nINSERT INTO outbox (id, aggregate_id, payload)\nVALUES (uuid, 42, '{...json...}')",
                    size=10.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(tx_x + 20, tx_y + 188, tx_w - 40, 30,
                    "COMMIT — або обидва записи на диску, або жодного",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # 4. Шляхи ретрансляції (два варіанти)
    # Варіант А: Опитування (Polling Publisher)
    f.append(arrow(590, 270, 680, 220, color=LINE, sw=2))
    f.append(fitbox(680, 170, 240, 95,
                    "СТРАТЕГІЯ 1: Polling Publisher\n\n"
                    "• Фоновий воркер читає таблицю\n"
                    "• SELECT ... FOR UPDATE SKIP LOCKED\n"
                    "• Надсилає батч і видаляє оброблене",
                    size=11, bold=True, fill=COOL, stroke=LINE, sw=1.4))

    # Варіант Б: Журнал транзакцій (CDC)
    f.append(arrow(590, 350, 680, 370, color=FIELD, sw=2))
    f.append(fitbox(680, 320, 240, 95,
                    "СТРАТЕГІЯ 2: Transaction Log Tailing\n\n"
                    "• Debezium / CDC читає WAL бази\n"
                    "• Нульове навантаження опитуванням\n"
                    "• Стрімінг змін у реальному часі",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    # 5. Брокер повідомлень
    f.append(arrow(920, 220, 970, 280, color=LINE, sw=2))
    f.append(arrow(920, 370, 970, 310, color=FIELD, sw=2))

    f.append(fitbox(970, 210, 170, 190,
                    "БРОКЕР\nПОВІДОМЛЕНЬ\n\n"
                    "Apache Kafka /\nRabbitMQ\n\n"
                    "Topic: orders\nKey: order_id\n"
                    "At-Least-Once",
                    size=12, bold=True, fill=WARN, stroke=LINE, sw=1.6))

    # Споживачі
    f.append(arrow(1055, 400, 1055, 450, color=LINE, sw=2))
    f.append(fitbox(950, 450, 210, 75,
                    "СПОЖИВАЧІ (Consumers)\n\n"
                    "• Доставка (Delivery)\n"
                    "• Склад (Inventory)\n"
                    "• Білінг (Billing)",
                    size=11.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.4))

    # Підсумок внизу
    f.append(fitbox(40, 550, 1100, 65,
                    "КЛЮЧОВА ПЕРЕВАГА: База даних виступає єдиним джерелом правди. "
                    "Вузол може впасти у будь-яку секунду — після перезапуску воркер або CDC-рушій "
                    "продовжить ретрансляцію непосланих рядків з outbox без жодної втрати даних.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'transactional-outbox-architecture.svg'), W, H, *f)


# ── 3. Конвеєр Change Data Capture (CDC) ────────────────────────────────────
def fig_outbox_cdc_pipeline():
    W, H = 1200, 580
    f = []

    f.append(fitbox(30, 20, 1140, 44,
                    "КОНВЕЄР CHANGE DATA CAPTURE (CDC): вилучення подій із журналу транзакцій (WAL)",
                    size=14, bold=True, fill=COOL))

    w_block = 225.0
    gap = 75.0
    y_box = 85.0
    h_box = 375.0

    # Крок 1: База даних та WAL
    x1 = 30.0
    f.append(fitbox(x1, y_box, w_block, h_box,
                    "1. БАЗА ДАНИХ\n(PostgreSQL)\n\n"
                    "Сховище таблиць:\n"
                    "• orders (бізнес-дані)\n"
                    "• outbox (події)\n\n"
                    "Журнал транзакцій:\n"
                    "• Write-Ahead Log (WAL)\n"
                    "• Реплікаційний слот\n"
                    "• Плагін pgoutput\n\n"
                    "COMMIT фіксує зміни\n"
                    "у WAL-файлах на диску.",
                    size=11.5, bold=True, fill=COOL, stroke=LINE, sw=1.5))

    # Стрілка 1
    arrow1_x1 = x1 + w_block
    arrow1_x2 = arrow1_x1 + gap
    f.append(arrow(arrow1_x1, 270, arrow1_x2, 270, color=FIELD, sw=2.2))
    f.append(fitbox(arrow1_x1 + 4, 235, gap - 8, 26, "WAL потік", size=10, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Крок 2: CDC-рушій Debezium
    x2 = arrow1_x2
    f.append(fitbox(x2, y_box, w_block, h_box,
                    "2. DEBEZIUM\nCONNECTOR\n\n"
                    "Logical Decoding:\n"
                    "• Підключений до слота\n"
                    "• Читає бінарний WAL\n"
                    "• Фільтрує лише outbox\n"
                    "• Фіксує позицію LSN\n"
                    "• Нуль SQL-опитувань\n\n"
                    "Перетворює мутацію\n"
                    "рядка на подію CDC.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Стрілка 2
    arrow2_x1 = x2 + w_block
    arrow2_x2 = arrow2_x1 + gap
    f.append(arrow(arrow2_x1, 270, arrow2_x2, 270, color=FIELD, sw=2.2))
    f.append(fitbox(arrow2_x1 + 4, 235, gap - 8, 26, "CDC подія", size=10, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Крок 3: SMT Трансформація
    x3 = arrow2_x2
    f.append(fitbox(x3, y_box, w_block, h_box,
                    "3. OUTBOX ROUTER\n(SMT Transform)\n\n"
                    "Single Message Transform:\n"
                    "• payload → тіло запису\n"
                    "• aggregate_id → ключ\n"
                    "• aggregate_type → топік\n"
                    "• headers → трасування\n\n"
                    "Очищає подію від колонок БД\n"
                    "і формує чистий Kafka-запис.",
                    size=11.5, bold=True, fill=WARN, stroke=MUTED, sw=1.5))

    # Стрілка 3
    arrow3_x1 = x3 + w_block
    arrow3_x2 = arrow3_x1 + gap
    f.append(arrow(arrow3_x1, 270, arrow3_x2, 270, color=FIELD, sw=2.2))
    f.append(fitbox(arrow3_x1 + 2, 235, gap - 4, 26, "Kafka запис", size=10, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Крок 4: Брокер Kafka
    x4 = arrow3_x2
    f.append(fitbox(x4, y_box, w_block, h_box,
                    "4. APACHE KAFKA\nCLUSTER\n\n"
                    "Топіки подій:\n"
                    "• topic: orders.events\n"
                    "• key: order_id = 42\n"
                    "• partition = hash(key) % N\n\n"
                    "Порядок строго збережено\n"
                    "в межах одного aggregate_id.\n\n"
                    "Гарантія: At-Least-Once.",
                    size=11.5, bold=True, fill=COOL, stroke=LINE, sw=1.5))

    # Нижній висновок
    f.append(fitbox(30, 480, 1140, 75,
                    "ПЕРЕВАГИ CDC ПЕРЕД ОПИТУВАННЯМ:\n"
                    "1. Затримка менше 10 мс (замість періодичного сну опитувача).\n"
                    "2. Нульовий вплив на продуктивність SQL-рушія (немає блокувань таблиці та роздування індексів).\n"
                    "3. Гарантія фіксації навіть тих рядків, які були негайно видалені з таблиці.",
                    size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, 'outbox-cdc-pipeline.svg'), W, H, *f)


# ── 4. Наскрізний конвеєр Outbox + Inbox ────────────────────────────────────
def fig_outbox_to_inbox_end_to_end():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "НАСКРІЗНА НАДІЙНІСТЬ: Transactional Outbox на відправнику + Transactional Inbox на отримувачі",
                    size=14, bold=True, fill=COOL))

    # Ліва колонка: Producer
    px = 40.0
    pw = 340.0
    f.append(rect(px, 80, pw, 445, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(px + 10, 95, pw - 20, 36,
                    "ВИРОБНИК (PRODUCER SERVICE)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(px + 15, 145, pw - 30, 80,
                    "Локальна транзакція:\n"
                    "1. Зміна бізнес-стану (таблиця A)\n"
                    "2. Запис події (таблиця outbox)\n"
                    "3. COMMIT",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(arrow(px + pw / 2, 230, px + pw / 2, 260, color=LINE, sw=1.8))

    f.append(fitbox(px + 15, 265, pw - 30, 80,
                    "Ретранслятор (Relay / CDC):\n"
                    "• Читає подію з outbox / WAL\n"
                    "• broker.send(event)\n"
                    "• Очікує підтвердження ACK",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(px + 15, 360, pw - 30, 65,
                    "При втраті ACK або таймауті:\n"
                    "Воркер надсилає повтор (RETRY)\n"
                    "→ Гарантія: AT-LEAST-ONCE",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(px + 15, 440, pw - 30, 70,
                    "Захист від втрат:\nПодія ніколи не зникне,\nдоки брокер не прийме її.",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.0))

    # Середня колонка: Брокер
    mx = 415.0
    mw = 350.0
    f.append(rect(mx, 80, mw, 445, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(mx + 10, 95, mw - 20, 36,
                    "ТРАНСПОРТ (MESSAGE BROKER)",
                    size=12, bold=True, fill=WARN, stroke=LINE, sw=1.2))

    # Стрілка від продюсера до брокера
    f.append(arrow(px + pw, 290, mx, 200, color=LINE, sw=2))
    f.append(arrow(px + pw, 380, mx, 330, color=POS, sw=2))
    f.append(text((px + pw + mx) / 2, 345, "повтор (дубль)", size=10.5, color=POS, bold=True))

    f.append(fitbox(mx + 15, 150, mw - 30, 90,
                    "Kafka Partition / RabbitMQ Queue\n\n"
                    "• Зберігає потік повідомлень на диск\n"
                    "• Може містити дублікати через\n"
                    "  повтори мережевих запитів",
                    size=11.5, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(mx + 15, 260, mw - 30, 110,
                    "Ненадійний зв'язок:\n"
                    "Збій мережі на відрізку повернення ACK\n"
                    "змушує відправника штурмувати брокер,\n"
                    "створюючи два однакових записи\n"
                    "з ідентичним event_id.",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.2))

    f.append(fitbox(mx + 15, 385, mw - 30, 125,
                    "ФУНДАМЕНТАЛЬНИЙ ФАКТ:\n\n"
                    "Брокер не може магічно усунути дублікати "
                    "без координації стану зі споживачем.",
                    size=11, bold=True, fill=FILL, stroke=LINE, sw=1.2))

    # Права колонка: Consumer
    cx = 800.0
    cw = 340.0
    f.append(rect(cx, 80, cw, 445, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(cx + 10, 95, cw - 20, 36,
                    "СПОЖИВАЧ (CONSUMER SERVICE)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Стрілка від брокера до консюмера
    f.append(arrow(mx + mw, 195, cx, 170, color=LINE, sw=2))
    f.append(arrow(mx + mw, 330, cx, 270, color=POS, sw=2))

    f.append(fitbox(cx + 15, 145, cw - 30, 110,
                    "Локальна транзакція дедуплікації:\n"
                    "1. INSERT INTO inbox (message_id)\n"
                    "   ON CONFLICT (message_id) DO NOTHING\n"
                    "2. Якщо вставка успішна:\n"
                    "   • Виконати мутацію стану\n"
                    "   • COMMIT",
                    size=10.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(cx + 15, 270, cw - 30, 95,
                    "Обробка повторного повідомлення:\n"
                    "• message_id вже є в таблиці inbox\n"
                    "• Вставка дає 0 рядків або конфлікт\n"
                    "• Транзакція ігнорує бізнес-дію\n"
                    "• Брокеру підтверджується ACK",
                    size=10.5, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(cx + 15, 380, cw - 30, 130,
                    "ПІДСУМКОВА СЕМАНТИКА:\n\n"
                    "Outbox (At-Least-Once на відправці)\n"
                    "           +\n"
                    "Inbox (Ідемпотентність на прийомі)\n"
                    "           =\n"
                    "EFFECTIVELY-ONCE ОБРОБКА",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Нижній висновок
    f.append(fitbox(40, 545, 1100, 55,
                    "СИМЕТРІЯ ПАТЕРНІВ: Outbox гарантує, що подія обов'язково вийде у світ без втрат. "
                    "Inbox гарантує, що неминучі дублікати цієї події не спотворять бізнес-стан отримувача.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'outbox-to-inbox-end-to-end.svg'), W, H, *f)


if __name__ == '__main__':
    fig_dual_write_failure_modes()
    fig_transactional_outbox_architecture()
    fig_outbox_cdc_pipeline()
    fig_outbox_to_inbox_end_to_end()
    print("All figures successfully generated in", OUT)
