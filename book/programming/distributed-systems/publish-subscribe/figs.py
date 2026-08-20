# -*- coding: utf-8 -*-
"""Фігури до теми «Шаблон Publish-Subscribe (Публікація-Підписка)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / повільний / блокування
COOL = "#eaf0fd"   # структура / зв'язок / нейтральне
GOOD = "#e8f6ee"   # швидкий / успіх / розв'язання
WARN = "#fef9e7"   # застереження / буфер / компроміс
PURPLE = "#f3e8fd" # брокер / маршрутизація


# ── 1. Три виміри розв'язання (Decoupling Dimensions) ─────────────────────────
def decoupling_dimensions():
    W, H = 1140, 480
    f = []

    cols = [
        (40.0, 370.0, "1. Прямий виклик (RPC / REST)",
         [
             ("Простір", "Тісний зв'язок: клієнт знає IP, порт і URL кожного отримувача", WARM, POS),
             ("Час", "Тісний зв'язок: обидва сервіси мусять бути в мережі одночасно", WARM, POS),
             ("Синхронізація", "Блокування: клієнт чекає завершення обробки кожним вузлом", WARM, POS),
             ("Масштабування 1:N", "Важке: додавання нового споживача вимагає правки коду відправника", WARM, POS)
         ]),
        (390.0, 750.0, "2. Черга повідомлень (Point-to-Point)",
         [
             ("Простір", "Частковий: знають ім'я черги, але не мережеву адресу одне одного", COOL, INK),
             ("Час", "Розв'язано: черга зберігає повідомлення, якщо споживач офлайн", GOOD, FIELD),
             ("Синхронізація", "Розв'язано: відправник публікує асинхронно й не чекає обробки", GOOD, FIELD),
             ("Масштабування 1:N", "Обмежене: 1 повідомлення = 1 споживач (конкурентна обробка)", WARN, INK)
         ]),
        (770.0, 1100.0, "3. Публікація-Підписка (Pub/Sub)",
         [
             ("Простір", "Повне розв'язання: видавець не знає кількості й адрес підписників", GOOD, FIELD),
             ("Час", "Розв'язано: довговічні підписки буферизують події для офлайн-вузлів", GOOD, FIELD),
             ("Синхронізація", "Розв'язано: подійне сповіщення (push/pull) без блокування видавця", GOOD, FIELD),
             ("Масштабування 1:N", "Ідеальне (Fan-out): 1 публікація транслюється M незалежним службам", GOOD, FIELD)
         ]),
    ]

    for x0, x1, title, items in cols:
        mid = (x0 + x1) / 2
        f.append(rect(x0, 20, x1 - x0, 370, fill=FILL, stroke=LINE, sw=1.3, rx=8))
        f.append(text(mid, 50, title, size=13, bold=True, color=INK))

        y = 75
        for label, desc, bg_col, stroke_col in items:
            f.append(rect(x0 + 12, y, x1 - x0 - 24, 62, fill=bg_col, stroke=stroke_col, sw=1.2, rx=6))
            f.append(text(x0 + 22, y + 20, label + ":", size=11, bold=True, color=stroke_col, anchor="start"))
            f.append(fitbox(x0 + 20, y + 26, x1 - x0 - 40, 32, desc, size=10.5, pad=2, stroke="none", fill="none"))
            y += 70

    f.append(fitbox(40, 405, 1060, 55,
                    "Підсумок: Pub/Sub розриває всі три залежності водночас. Видавець транслює факт події, "
                    "а брокер бере на себе просторову маршрутизацію, буферизацію в часі та доставку багатьом споживачам.",
                    size=12, fill=WARN, stroke=LINE, sw=1.3))

    render(os.path.join(OUT, 'decoupling-dimensions.svg'), W, H, *f)


# ── 2. Дерево префіксів для маршрутизації тем (Topic Trie Routing) ───────────
def topic_trie_routing():
    W, H = 1140, 500
    f = []

    # Верхній блок: Подія, що надходить
    f.append(rect(40, 20, 1060, 50, fill=COOL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(60, 48, "Опублікована подія:", size=12, bold=True, color=INK, anchor="start"))
    f.append(textbox(280, 45, "Тема: orders/eu/ua/created", size=12, bold=True, fill=GOOD, stroke=FIELD)[0])
    f.append(text(460, 48, "Payload: { order_id: 84102, total: 30000, user_id: 991 }", size=11.5, color=MUTED, anchor="start"))

    # Дерево вузлів префіксного пошуку (Trie)
    # Рівень 0: Root
    f.append(textbox(200, 120, "Root [/]", size=12, bold=True, fill=FILL, stroke=LINE)[0])

    # Рівень 1: orders, sensors
    f.append(arrow(200, 140, 150, 190, color=LINE, sw=1.4))
    f.append(arrow(200, 140, 360, 190, color=MUTED, sw=1.2))
    f.append(textbox(150, 205, "orders", size=12, bold=True, fill=PURPLE, stroke=LINE)[0])
    f.append(textbox(360, 205, "sensors", size=11.5, color=MUTED, fill=FILL, stroke=MUTED)[0])

    # Рівень 2: eu, us під orders
    f.append(arrow(150, 225, 120, 275, color=LINE, sw=1.4))
    f.append(arrow(150, 225, 230, 275, color=MUTED, sw=1.2))
    f.append(textbox(120, 290, "eu", size=12, bold=True, fill=PURPLE, stroke=LINE)[0])
    f.append(textbox(230, 290, "us", size=11.5, color=MUTED, fill=FILL, stroke=MUTED)[0])

    # Рівень 3: ua, de під eu
    f.append(arrow(120, 310, 90, 360, color=LINE, sw=1.4))
    f.append(arrow(120, 310, 190, 360, color=MUTED, sw=1.2))
    f.append(textbox(90, 375, "ua", size=12, bold=True, fill=PURPLE, stroke=LINE)[0])
    f.append(textbox(190, 375, "de", size=11.5, color=MUTED, fill=FILL, stroke=MUTED)[0])

    # Рівень 4: created під ua
    f.append(arrow(90, 395, 90, 440, color=LINE, sw=1.4))
    f.append(textbox(90, 455, "created", size=12, bold=True, fill=GOOD, stroke=FIELD)[0])

    # Права частина: Зіставлення підписок (Matching Subscriptions)
    f.append(rect(480, 90, 620, 390, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(500, 118, "Зіставлення з підписками (Matching Engine):", size=13, bold=True, color=INK, anchor="start"))

    subs = [
        ("Підписка 1 (Точний збіг):", "orders/eu/ua/created", "Співпало ✓",
         "Служба доставки (UA Courier) — створює накладну в базі", GOOD, FIELD),
        ("Підписка 2 (Однорівневий шаблон '+'):", "orders/eu/+/created", "Співпало ✓",
         "Аналітика продажів ЄС — фіксує конверсію в регіоні", GOOD, FIELD),
        ("Підписка 3 (Багаторівневий шаблон '#'):", "orders/#", "Співпало ✓",
         "Сховище аудиту (Audit Log / Data Lake) — зберігає копію в S3", GOOD, FIELD),
        ("Підписка 4 (Інша гілка):", "orders/us/#", "Ні ✗",
         "Логістика США — повідомлення ігнорується", WARM, MUTED),
    ]

    sy = 135
    for title, pat, status, action, card_bg, badge_col in subs:
        f.append(rect(495, sy, 590, 72, fill=card_bg, stroke=badge_col, sw=1.2, rx=6))
        f.append(text(510, sy + 20, title, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(760, sy + 20, pat, size=11.5, bold=True, color=badge_col, anchor="start"))
        f.append(text(1050, sy + 20, status, size=11.5, bold=True, color=badge_col, anchor="end"))
        f.append(text(510, sy + 48, action, size=10.5, color=INK, anchor="start"))
        sy += 82

    # Зв'язок між створеним токеном і співпадінням
    f.append(arrow(145, 455, 480, 200, color=FIELD, sw=1.5))

    render(os.path.join(OUT, 'topic-trie-routing.svg'), W, H, *f)


# ── 3. Проблема повільного споживача й зворотний тиск ─────────────────────────
def slow_consumer_backpressure():
    W, H = 1140, 500
    f = []

    # Видавець (Fast Producer)
    f.append(rect(40, 160, 160, 140, fill=COOL, stroke=LINE, sw=1.4, rx=8))
    f.append(text(120, 200, "Видавець", size=13, bold=True, color=INK))
    f.append(text(120, 225, "(Платіжний шлюз)", size=11, color=MUTED))
    f.append(textbox(120, 265, "λ = 10 000 msg/s", size=11.5, bold=True, fill=GOOD, stroke=FIELD)[0])

    # Стрілка від видавця до брокера
    f.append(arrow(200, 230, 280, 230, color=LINE, sw=2))
    f.append(text(240, 218, "Публікація", size=10.5, bold=True, color=INK))

    # Центральний Брокер
    f.append(rect(280, 40, 360, 420, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(460, 70, "Pub/Sub Брокер (Fan-out Engine)", size=13, bold=True, color=INK))

    # Буфер Споживача A (Швидкий)
    f.append(rect(300, 100, 320, 110, fill=GOOD, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(315, 125, "Буфер підписки А (Швидкий)", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(rect(315, 140, 290, 22, fill=BG, stroke=MUTED, sw=1, rx=3))
    # Заповнено 10%
    f.append(rect(315, 140, 35, 22, fill=FIELD, stroke="none", rx=3))
    f.append(text(360, 156, "Заповнення: 10% (100 / 1000 msg) — стан стабільний", size=10, color=INK, anchor="start"))
    f.append(text(315, 190, "Вихідний потік: 10 000 msg/s (черга порожня)", size=10.5, color=FIELD, anchor="start"))

    # Буфер Споживача B (Повільний)
    f.append(rect(300, 260, 320, 180, fill=WARM, stroke=POS, sw=1.4, rx=6))
    f.append(text(315, 285, "Буфер підписки B (Повільний споживач!)", size=11, bold=True, color=POS, anchor="start"))
    f.append(rect(315, 300, 290, 24, fill=BG, stroke=MUTED, sw=1, rx=3))
    # Заповнено 100%
    f.append(rect(315, 300, 290, 24, fill=POS, stroke="none", rx=3))
    f.append(text(460, 317, "ПЕРЕПОВНЕНО 1000 / 1000 (OOM Risk!)", size=10.5, bold=True, color=BG))

    f.append(text(315, 345, "Стратегії розв'язання кризи буфера:", size=10.5, bold=True, color=INK, anchor="start"))
    f.append(text(315, 365, "1. Drop-oldest / Drop-newest (втрата даних)", size=10, color=POS, anchor="start"))
    f.append(text(315, 385, "2. Backpressure (зупиняє видавця і всіх інших!)", size=10, color=POS, anchor="start"))
    f.append(text(315, 405, "3. DLQ / Скидання на диск (ізоляція збою)", size=10, color=FIELD, anchor="start"))

    # Стрілки від брокера до споживачів
    f.append(arrow(640, 155, 730, 155, color=FIELD, sw=2))
    f.append(text(685, 142, "push/pull", size=10.5, color=FIELD))

    f.append(arrow(640, 340, 730, 340, color=POS, sw=2))
    f.append(text(685, 328, "деградація", size=10.5, color=POS))

    # Споживач A
    f.append(rect(730, 100, 370, 110, fill=GOOD, stroke=FIELD, sw=1.3, rx=8))
    f.append(text(750, 130, "Споживач A: Сервіс балансів", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(750, 155, "Пропускна здатність: μ_A = 12 000 msg/s", size=11, color=INK, anchor="start"))
    f.append(text(750, 180, "Затримка: < 2 мс (встигає за видавцем)", size=11, color=MUTED, anchor="start"))

    # Споживач B
    f.append(rect(730, 280, 370, 150, fill=WARM, stroke=POS, sw=1.3, rx=8))
    f.append(text(750, 310, "Споживач B: Експорт у PDF / CRM", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(750, 335, "Пропускна здатність: μ_B = 200 msg/s (блокування БД)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(750, 360, "Відставання: зростає зі швидкістю 9 800 msg/s!", size=11, color=POS, anchor="start"))
    f.append(text(750, 395, "Наслідок: вичерпання RAM брокера або drop", size=11, bold=True, color=INK, anchor="start"))

    render(os.path.join(OUT, 'slow-consumer-backpressure.svg'), W, H, *f)


# ── 4. Топології: Брокерний проти Безброкерного Pub/Sub ───────────────────────
def broker_vs_brokerless():
    W, H = 1140, 480
    f = []

    # Ліва половина: Централізований брокер
    f.append(rect(30, 20, 525, 430, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(292, 50, "Централізований брокер (RabbitMQ, EMQX, Kafka)", size=13, bold=True, color=INK))

    # Видавці
    f.append(rect(50, 85, 110, 40, fill=COOL, stroke=LINE, sw=1.2, rx=4))
    f.append(text(105, 110, "Видавець 1", size=11, bold=True, color=INK))
    f.append(rect(50, 145, 110, 40, fill=COOL, stroke=LINE, sw=1.2, rx=4))
    f.append(text(105, 170, "Видавець 2", size=11, bold=True, color=INK))

    # Брокер у центрі лівої колонки
    f.append(rect(215, 95, 150, 80, fill=PURPLE, stroke=LINE, sw=1.5, rx=6))
    f.append(text(290, 130, "Pub/Sub Брокер", size=12, bold=True, color=INK))
    f.append(text(290, 152, "(Fan-out & State)", size=10.5, color=MUTED))

    f.append(arrow(160, 105, 215, 125, color=LINE, sw=1.4))
    f.append(arrow(160, 165, 215, 145, color=LINE, sw=1.4))

    # Підписники
    f.append(rect(415, 75, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(475, 98, "Підписник 1", size=11, bold=True, color=FIELD))
    f.append(rect(415, 120, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(475, 143, "Підписник 2", size=11, bold=True, color=FIELD))
    f.append(rect(415, 165, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(475, 188, "Підписник 3", size=11, bold=True, color=FIELD))

    f.append(arrow(365, 125, 415, 93, color=FIELD, sw=1.4))
    f.append(arrow(365, 135, 415, 138, color=FIELD, sw=1.4))
    f.append(arrow(365, 145, 415, 183, color=FIELD, sw=1.4))

    f.append(fitbox(50, 220, 485, 210,
                    "Властивості брокерної топології:\n\n"
                    "• Мережевий трафік видавця мінімальний: рівно 1 копія в мережу.\n"
                    "• Розмноження (fan-out) і фільтрацію бере на себе брокер.\n"
                    "• Довговічність (durable subscriptions): брокер тримає черги для офлайн-вузлів.\n"
                    "• Ціна: додатковий хоп мережі (латентність +1..5 мс), брокер є вузьким місцем CPU/RAM.",
                    size=11, pad=10, fill=BG, stroke=MUTED, sw=1))

    # Права половина: Безброкерний / Multicast
    f.append(rect(585, 20, 525, 430, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(847, 50, "Безброкерний / Multicast (ZeroMQ, DDS, ROS 2)", size=13, bold=True, color=INK))

    # Видавець праворуч (Fan-out на боці відправника або IP Multicast)
    f.append(rect(605, 100, 135, 75, fill=COOL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(672, 130, "Видавець", size=12, bold=True, color=INK))
    f.append(text(672, 152, "(Peer-to-Peer / PGM)", size=10.5, color=MUTED))

    # Підписники безпосередньо з'єднані
    f.append(rect(970, 75, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(1030, 98, "Підписник 1", size=11, bold=True, color=FIELD))
    f.append(rect(970, 120, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(1030, 143, "Підписник 2", size=11, bold=True, color=FIELD))
    f.append(rect(970, 165, 120, 36, fill=GOOD, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(1030, 188, "Підписник 3", size=11, bold=True, color=FIELD))

    f.append(arrow(740, 125, 970, 93, color=FIELD, sw=1.4))
    f.append(arrow(740, 137, 970, 138, color=FIELD, sw=1.4))
    f.append(arrow(740, 150, 970, 183, color=FIELD, sw=1.4))

    f.append(fitbox(605, 220, 485, 210,
                    "Властивості безброкерної топології:\n\n"
                    "• Ультранизька затримка: пряма доставка сокет-у-сокет (мікросекунди).\n"
                    "• Немає центральної точки відмови або посередника.\n"
                    "• Трафік видавця зростає лінійно з кількістю клієнтів (якщо unicast).\n"
                    "• Складність: динамічне виявлення пірів (discovery), втрата повідомлень при офлайні.",
                    size=11, pad=10, fill=BG, stroke=MUTED, sw=1))

    render(os.path.join(OUT, 'broker-vs-brokerless.svg'), W, H, *f)


if __name__ == '__main__':
    decoupling_dimensions()
    topic_trie_routing()
    slow_consumer_backpressure()
    broker_vs_brokerless()
    print("Всі фігури згенеровано успішно.")
