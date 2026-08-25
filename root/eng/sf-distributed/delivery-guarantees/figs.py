# -*- coding: utf-8 -*-
"""Фігури до теми «Гарантії доставки: at-most-once, at-least-once та ілюзія exactly-once»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / втрата
COOL = "#eaf0fd"   # нейтральне пояснення / структура
GOOD = "#e8f6ee"   # успіх / надійність
WARN = "#fef9e7"   # застереження / дублікати


# ── 1. Три точки розриву: чому відправник бачить однаковий таймаут ───────────
def two_generals_delivery():
    W, H = 1140, 520
    f = []

    # Три колонки для трьох сценаріїв відмови
    cols = [
        (40.0, 360.0, "Сценарій А: втрата запиту в мережі"),
        (400.0, 720.0, "Сценарій Б: збій сервера після дії"),
        (760.0, 1080.0, "Сценарій В: втрата квитанції (ACK)"),
    ]

    for x0, x1, title in cols:
        mid = (x0 + x1) / 2
        f.append(rect(x0, 20, x1 - x0, 410, fill=FILL, stroke=LINE, sw=1.3, rx=8))
        f.append(text(mid, 48, title, size=13, bold=True, color=INK))

        # Вузли: Відправник (A) і Отримувач (B)
        xa, xb = x0 + 55, x1 - 55
        f.append(fitbox(xa - 42, 75, 84, 32, "Клієнт (A)", size=12, bold=True, fill=COOL))
        f.append(fitbox(xb - 45, 75, 90, 32, "Сервер (B)", size=12, bold=True, fill=COOL))

        # Вертикальні лінії життя
        f.append(line(xa, 112, xa, 350, color=MUTED, sw=1.2, dash="4,4"))
        f.append(line(xb, 112, xb, 350, color=MUTED, sw=1.2, dash="4,4"))

    # Сценарій А деталі
    x0, x1 = cols[0][0], cols[0][1]
    xa, xb = x0 + 55, x1 - 55
    f.append(line(xa, 140, xa + 130, 185, color=POS, sw=1.8))
    f.append(text(xa + 65, 150, "Запит", size=11, color=POS, bold=True))
    f.append(text(xa + 145, 192, "✖ загублено", size=11.5, color=POS, bold=True))
    f.append(text(xb, 220, "Дія НЕ виконана", size=11.5, color=MUTED, italic=True))
    f.append(line(xa - 10, 290, xa + 10, 290, color=POS, sw=2))
    f.append(text(xa + 60, 295, "Таймаут!", size=12, color=POS, bold=True))

    # Сценарій Б деталі
    x0, x1 = cols[1][0], cols[1][1]
    xa, xb = x0 + 55, x1 - 55
    f.append(arrow(xa, 140, xb, 185, color=LINE, sw=1.6))
    f.append(text((xa + xb) / 2, 150, "Запит", size=11, color=INK, bold=True))
    f.append(rect(xb - 42, 195, 84, 28, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(xb, 213, "Дію виконано", size=11, color=FIELD, bold=True))
    f.append(text(xb, 248, "⚡ Аварія / Kill", size=11.5, color=POS, bold=True))
    f.append(line(xa - 10, 290, xa + 10, 290, color=POS, sw=2))
    f.append(text(xa + 60, 295, "Таймаут!", size=12, color=POS, bold=True))

    # Сценарій В деталі
    x0, x1 = cols[2][0], cols[2][1]
    xa, xb = x0 + 55, x1 - 55
    f.append(arrow(xa, 140, xb, 185, color=LINE, sw=1.6))
    f.append(text((xa + xb) / 2, 150, "Запит", size=11, color=INK, bold=True))
    f.append(rect(xb - 42, 195, 84, 28, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(xb, 213, "Дію виконано", size=11, color=FIELD, bold=True))
    f.append(line(xb, 235, xb - 125, 275, color=POS, sw=1.8))
    f.append(text(xb - 60, 245, "ACK", size=11, color=POS, bold=True))
    f.append(text(xb - 140, 282, "✖ загублено", size=11.5, color=POS, bold=True))
    f.append(line(xa - 10, 290, xa + 10, 290, color=POS, sw=2))
    f.append(text(xa + 60, 295, "Таймаут!", size=12, color=POS, bold=True))

    # Підсумок унизу
    f.append(fitbox(40, 445, 1060, 60,
                    "Наслідок: клієнт бачить однаковий таймаут у всіх трьох випадках. "
                    "Якщо не повторити — у сценарії А дані втрачено; якщо повторити наївно — "
                    "у сценаріях Б і В дію буде виконано двічі.",
                    size=13, fill=WARN, stroke=LINE, sw=1.3))

    render(os.path.join(OUT, 'two-generals-delivery.svg'), W, H, *f)


# ── 2. Таксономія гарантій: At-most-once, At-least-once, Effectively-once ────
def guarantees_taxonomy():
    W, H = 1160, 460
    f = []

    cards = [
        (40.0, 380.0, "Щонайбільше один раз\n(At-most-once)",
         "Спроб: рівно 1 (без повторів)\nПідтвердження: до або без обробки\n\n"
         "• Втрати: МОЖЛИВІ (0 або 1)\n• Дублікати: ВИКЛЮЧЕНІ\n• Ціна: мінімальна затримка\n\n"
         "Застосування: метрики, телеметрія,\nпотокове аудіо/відео, де свіжість\nважливіша за повноту.",
         COOL, LINE),
        (410.0, 750.0, "Щонайменше один раз\n(At-least-once)",
         "Спроб: 1..N (повтори до ACK)\nПідтвердження: після запису/обробки\n\n"
         "• Втрати: ВИКЛЮЧЕНІ (при стійкості)\n• Дублікати: НЕМИНУЧІ\n• Ціна: навантаження від повторів\n\n"
         "Застосування: черги повідомлень\n(RabbitMQ, Kafka, SQS) за замовчуванням;\nбазовий фундамент систем.",
         WARN, LINE),
        (780.0, 1120.0, "Рівно один наслідок\n(Effectively-once)",
         "At-least-once + Ідемпотентність\n(дедуплікація на боці стану)\n\n"
         "• Втрати: ВИКЛЮЧЕНІ\n• Дублікати: ВІДСІКАЮТЬСЯ\n• Ціна: пам'ять під ключі + транзакції\n\n"
         "Застосування: фінансові операції,\nбілінг, зміна залишків на складі,\nкритичні мутації бази даних.",
         GOOD, FIELD),
    ]

    for x0, x1, title, body, bg, st in cards:
        w = x1 - x0
        f.append(rect(x0, 25, w, 410, fill=bg, stroke=st, sw=1.6, rx=8))
        f.append(fitbox(x0 + 15, 40, w - 30, 52, title, size=14, bold=True, fill="#ffffff", stroke=st, sw=1.2))
        f.append(fitbox(x0 + 15, 105, w - 30, 315, body, size=12.5, fill=bg, stroke="none"))

    render(os.path.join(OUT, 'guarantees-taxonomy.svg'), W, H, *f)


# ── 3. Три стадії наскрізного ланцюга доставки ───────────────────────────────
def producer_broker_consumer_stages():
    W, H = 1180, 490
    f = []

    # Три великі блоки стадій
    stages = [
        (40.0, 370.0, "Стадія 1: Продюсер → Брокер",
         "Гарантія публікації:\n"
         "• acks = 0 (надіслав і забув)\n"
         "• acks = 1 (запис у лідера)\n"
         "• acks = all (кворум реплік)\n"
         "• PID + SeqNum (дедуплікація на вході брокера)",
         COOL),
        (410.0, 770.0, "Стадія 2: Сховище брокера",
         "Стійкість у спокої:\n"
         "• Write-Ahead Log (WAL)\n"
         "• Синхронізація fsync\n"
         "• Реплікація в ISR (In-Sync Replicas)\n"
         "• Збереження порядку в партиції",
         COOL),
        (810.0, 1140.0, "Стадія 3: Брокер → Консюмер",
         "Гарантія споживання:\n"
         "• Автокоміт до обробки\n  → at-most-once (ризик втрати)\n"
         "• Коміт після збереження в БД\n  → at-least-once (ризик дубля)\n"
         "• Транзакційний Inbox\n  → effectively-once",
         GOOD),
    ]

    for x0, x1, title, body, bg in stages:
        w = x1 - x0
        f.append(rect(x0, 40, w, 320, fill=bg, stroke=LINE, sw=1.5, rx=8))
        f.append(fitbox(x0 + 12, 55, w - 24, 42, title, size=13.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.2))
        f.append(fitbox(x0 + 15, 110, w - 30, 235, body, size=12.5, fill=bg, stroke="none"))

    # Стрілки між стадіями
    f.append(arrow(372, 200, 408, 200, color=LINE, sw=2.5))
    f.append(arrow(772, 200, 808, 200, color=LINE, sw=2.5))

    # Нижній висновок
    f.append(fitbox(40, 385, 1100, 85,
                    "Закон наскрізного ланцюга: загальна гарантія системи дорівнює найслабшій ланці. "
                    "Навіть якщо брокер забезпечує ідемпотентну публікацію та потрійну реплікацію, "
                    "консюмер з автокомітом зміщення до завершення обробки зводить усю систему до at-most-once.",
                    size=13, fill=FILL, stroke=MUTED, sw=1.3))

    render(os.path.join(OUT, 'producer-broker-consumer-stages.svg'), W, H, *f)


# ── 4. Патерн Transactional Inbox та ковзне вікно дедуплікації ───────────────
def deduplication_window():
    W, H = 1180, 500
    f = []

    # Вхідне повідомлення
    f.append(fitbox(40, 60, 220, 110,
                    "Вхідне повідомлення\n\nID: msg_94821\nKey: pay_order_441\nСума: 500 грн",
                    size=12, bold=True, fill=COOL))

    # Стрілка до транзакції
    f.append(arrow(262, 115, 338, 115, color=LINE, sw=2))

    # Велика рамка: Локальна транзакція БД
    f.append(rect(340, 30, 520, 430, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(600, 58, "Єдина локальна транзакція бази даних (ACID)", size=14, bold=True, color=FIELD))

    # Крок 1: Перевірка в таблиці Inbox
    f.append(rect(365, 80, 470, 95, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
    f.append(text(600, 105, "1. INSERT INTO inbox (msg_id) VALUES ('msg_94821')", size=12, bold=True))
    f.append(text(600, 130, "Унікальний індекс за msg_id (або idempotency_key)", size=11.5, color=MUTED))
    f.append(text(600, 155, "Конфлікт унікальності? → ДУБЛІКАТ, скасувати або повернути кеш", size=11.5, color=POS, bold=True))

    # Крок 2: Бізнес-мутація
    f.append(rect(365, 195, 470, 95, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
    f.append(text(600, 220, "2. Бізнес-дія: UPDATE accounts SET balance = balance - 500", size=12, bold=True))
    f.append(text(600, 245, "Виконується ТІЛЬКИ якщо ключ унікальний", size=11.5, color=FIELD, bold=True))
    f.append(text(600, 270, "Зміна грошей і запис ключа нерозривні", size=11.5, color=MUTED))

    # Крок 3: Фіксація
    f.append(rect(365, 310, 470, 65, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
    f.append(text(600, 335, "3. COMMIT TRANSACTION", size=13, bold=True, color=FIELD))
    f.append(text(600, 360, "Або обидва записи на диску, або жоден", size=11.5, color=MUTED))

    # Вихід праворуч: ACK до черги
    f.append(arrow(862, 342, 938, 342, color=LINE, sw=2))
    f.append(fitbox(940, 305, 200, 80,
                    "Підтвердження черзі\n(ACK msg_94821)\n\nЧерга видаляє повідомлення",
                    size=12, bold=True, fill=COOL))

    # Розгалуження при збої ACK
    f.append(arrow(1040, 390, 1040, 440, color=POS, sw=1.5))
    f.append(line(1040, 440, 150, 440, color=POS, sw=1.5))
    f.append(arrow(150, 440, 150, 175, color=POS, sw=1.5))
    f.append(text(595, 465, "Якщо ACK загубився → повтор прийде знову, але крок 1 відсіче його через конфлікт ключа",
                  size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, 'deduplication-window.svg'), W, H, *f)


two_generals_delivery()
guarantees_taxonomy()
producer_broker_consumer_stages()
deduplication_window()
print("готово:", ", ".join(sorted(os.listdir(OUT))))
