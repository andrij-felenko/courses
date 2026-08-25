# -*- coding: utf-8 -*-
"""Фігури до теми «Патерн Вхідна скринька (Transactional Inbox)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / втрата / дублювання
COOL = "#eaf0fd"   # стан / брокер / інформаційне поле
GOOD = "#e8f6ee"   # успіх / атомарна фіксація / захист


# ── 1. Пастка роздільної дедуплікації ──────────────────────────────────────
def fig_inbox_dual_write_failure():
    W, H = 1180, 640
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "ПАСТКА РОЗДІЛЬНОЇ ДЕДУПЛІКАЦІЇ: чому зовнішній реєстр не рятує від збоїв",
                    size=14, bold=True, fill=COOL))

    hw = 510.0
    y0 = 85.0

    # Ліва половина: Роздільні системи (Redis + Postgres)
    xL = 50.0
    f.append(fitbox(xL, y0, hw, 56, "РОЗДІЛЬНІ СХОВИЩА (ПОМИЛКА)\nключ у Redis, бізнес-стан у PostgreSQL", size=13, bold=True, fill=WARM, stroke=POS, sw=2))

    # Сценарій 1
    f.append(fitbox(xL + 20, y0 + 75, 470, 70,
                    "Сценарій А: Спочатку база даних, потім кеш\n"
                    "1. UPDATE balances SET amount = amount - 500 (Успіх)\n"
                    "2. КРАХ споживача до запису ключа в Redis!",
                    size=11.5, fill="#ffffff", stroke=POS, sw=1.4))

    f.append(fitbox(xL + 20, y0 + 155, 470, 60,
                    "Брокер пересилає повідомлення через таймаут ACK\n"
                    "Ключа в Redis немає → БАЗА ОНОВЛЮЄТЬСЯ ВДРУГЕ (Збитки!)",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Сценарій 2
    f.append(fitbox(xL + 20, y0 + 230, 470, 70,
                    "Сценарій Б: Спочатку кеш, потім база даних\n"
                    "1. SETNX idempotency:msg-101 (Успіх у Redis)\n"
                    "2. КРАХ споживача до виконання SQL у PostgreSQL!",
                    size=11.5, fill="#ffffff", stroke=POS, sw=1.4))

    f.append(fitbox(xL + 20, y0 + 310, 470, 60,
                    "Брокер пересилає повідомлення повторно\n"
                    "Ключ у Redis знайдено → ОБРОБКУ ПРОПУЩЕНО (Подія втрачена!)",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(xL + 20, y0 + 385, 470, 50,
                    "Причина: неможливо гарантувати атомарність\nміж двома незалежними мережевими вузлами",
                    size=11.5, fill=FILL, stroke=POS, sw=1.2))

    # Права половина: Transactional Inbox
    xR = xL + hw + 60
    f.append(fitbox(xR, y0, hw, 56, "TRANSACTIONAL INBOX (ПРАВИЛЬНО)\nдедуплікація і стан в одній локальній транзакції", size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(xR + 20, y0 + 75, 470, 190,
                    "BEGIN TRANSACTION;\n\n"
                    "  -- 1. Спроба вставити ідентифікатор події\n"
                    "  INSERT INTO inbox (message_id, handler, status)\n"
                    "  VALUES ('msg-101', 'OrderPaid', 'PROCESSED');\n\n"
                    "  -- 2. Мутація бізнес-таблиць\n"
                    "  UPDATE balances SET amount = amount - 500 WHERE user_id = 42;\n"
                    "  INSERT INTO orders (id, status) VALUES ('ord-101', 'PAID');\n\n"
                    "COMMIT;",
                    size=11.5, fill="#ffffff", stroke=FIELD, sw=1.8))

    f.append(fitbox(xR + 20, y0 + 280, 470, 75,
                    "При збої до COMMIT: відкочується І запис у inbox, І бізнес-зміни.\n"
                    "При повторі брокера: транзакція почнеться заново й виконається чисто.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    f.append(fitbox(xR + 20, y0 + 370, 470, 65,
                    "При збої після COMMIT (втрата ACK):\n"
                    "Повторний INSERT спричинить UniqueViolation → споживач відкидає дубль\n"
                    "і безпечно підтверджує повідомлення в брокері (ACK).",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    f.append(fitbox(40, 555, 1100, 52,
                    "золоте правило споживача: стан дедуплікації мусить фіксуватися в тій самій транзакції, що й бізнес-стан;\n"
                    "лише єдина транзакція бази даних перетворює ненадійний транспорт на надійну обробку",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'inbox-dual-write-failure.svg'), W, H, *f)


# ── 2. Життєвий цикл повідомлення у Transactional Inbox ────────────────────
def fig_transactional_inbox_lifecycle():
    W, H = 1200, 660
    f = []

    f.append(fitbox(40, 20, 1120, 44,
                    "ЖИТТЄВИЙ ЦИКЛ ПОВІДОМЛЕННЯ: атомарна дедуплікація та захист від дублів",
                    size=14, bold=True, fill=COOL))

    # Блок 1: Брокер повідомлень
    f.append(fitbox(50, 100, 200, 80, "БРОКЕР ПОВІДОМЛЕНЬ\n(Kafka / RabbitMQ / SQS)\nдоставка at-least-once", size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))

    # Стрілка від брокера до Споживача
    f.append(arrow(250, 140, 340, 140, color=NEG, sw=2))
    f.append(text(295, 125, "повідомлення\n(msg_id, payload)", size=11, color=NEG, bold=True))

    # Блок 2: Початок транзакції
    f.append(fitbox(345, 95, 230, 90, "ТРАНЗАКЦІЯ БД (BEGIN)\nINSERT INTO inbox\nON CONFLICT DO NOTHING", size=12.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.8))

    # Розгалуження: Нове чи Дубль?
    f.append(arrow(575, 140, 680, 140, color=FIELD, sw=2.2))
    f.append(text(628, 125, "Новий msg_id", size=11.5, color=FIELD, bold=True))

    # Блок 3: Виконання бізнес-логіки
    f.append(fitbox(685, 95, 240, 90, "БІЗНЕС-ОБРОБКА\nмутація доменних таблиць\nstatus = 'PROCESSED'", size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    # Блок 4: Фіксація COMMIT
    f.append(arrow(925, 140, 985, 140, color=FIELD, sw=2.2))
    f.append(fitbox(990, 95, 160, 90, "COMMIT\nтранзакції\nуспішно", size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2.2))

    # Стрілка підтвердження ACK
    f.append(line(1070, 185, 1070, 270, color=FIELD, sw=2))
    f.append(line(1070, 270, 150, 270, color=FIELD, sw=2))
    f.append(arrow(150, 270, 150, 185, color=FIELD, sw=2))
    f.append(text(600, 255, "ПІДТВЕРДЖЕННЯ БРОКЕРУ (ACK / Commit Offset) — повідомлення вилучається з черги", size=11.5, color=FIELD, bold=True))

    # Гілка дубліката
    f.append(arrow(460, 185, 460, 360, color=POS, sw=2))
    f.append(text(475, 225, "Колізія UNIQUE (дубль)", size=11.5, color=POS, bold=True, anchor="start"))

    f.append(fitbox(345, 365, 230, 90, "ДУБЛЬ ВЖЕ В БАЗІ\nROLLBACK транзакції\nігнорування бізнес-коду", size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Стрілка від дубля до негайного ACK
    f.append(arrow(575, 410, 800, 410, color=MUTED, sw=2))
    f.append(text(685, 395, "Безпечний повторний ACK", size=11.5, color=MUTED, bold=True))

    f.append(fitbox(805, 365, 200, 90, "НЕГАЙНИЙ ACK\nброкер зупиняє\nпересилання дублів", size=12.5, bold=True, fill=COOL, stroke=MUTED, sw=1.8))
    f.append(line(1005, 410, 1070, 410, color=MUTED, sw=2))
    f.append(line(1070, 410, 1070, 270, color=MUTED, sw=2))

    # Гілка аварійного збою (отруйне повідомлення / тайм-аут)
    f.append(line(805, 185, 805, 480, color=POS, sw=1.8, dash="5,4"))
    f.append(arrow(805, 480, 805, 490, color=POS, sw=1.8))
    f.append(text(815, 220, "Помилка в бізнес-коді", size=11, color=POS, bold=True, anchor="start"))
    f.append(fitbox(685, 490, 240, 80, "ЗБІЙ ОБРОБКИ\nROLLBACK + retry_count++\nпри перевищенні → DLQ", size=12, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(40, 585, 1120, 60,
                    "автомат гарантує неподільність: кожне повідомлення або виконує бізнес-ефект і фіксується в inbox,\n"
                    "або відкочується цілком і чекає повтору брокера; уже зафіксовані дублікати миттєво глушаться",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'transactional-inbox-lifecycle.svg'), W, H, *f)


# ── 3. Конкурентна обробка та розподілені лізи в Inbox ─────────────────────
def fig_inbox_concurrency_and_leases():
    W, H = 1200, 640
    f = []

    f.append(fitbox(40, 20, 1120, 44,
                    "КОНКУРЕНТНІ СПОЖИВАЧІ ТА ЛІЗИ: безпечний паралелізм через блокування рядків",
                    size=14, bold=True, fill=COOL))

    # Спільна таблиця Inbox (центр)
    f.append(fitbox(420, 90, 360, 210,
                    "ТАБЛИЦЯ INBOX (PostgreSQL)\n\n"
                    "id | status     | locked_until | locked_by\n"
                    "---+------------+--------------+----------\n"
                    " 1 | PROCESSING | 12:00:30     | worker-A \n"
                    " 2 | PROCESSING | 12:00:32     | worker-B \n"
                    " 3 | RECEIVED   | NULL         | NULL     \n"
                    " 4 | RECEIVED   | NULL         | NULL     \n"
                    " 5 | PROCESSED  | NULL         | worker-A ",
                    size=12, bold=False, fill="#ffffff", stroke=LINE, sw=1.8))

    # Воркер 1 (ліворуч)
    f.append(fitbox(50, 90, 300, 140,
                    "ВОРКЕР А (Под 1)\n\n"
                    "SELECT id FROM inbox\n"
                    "WHERE status = 'RECEIVED'\n"
                    "FOR UPDATE SKIP LOCKED LIMIT 1;\n\n"
                    "→ Захоплює рядок 1 (Блокує)",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))

    # Воркер 2 (праворуч)
    f.append(fitbox(850, 90, 300, 140,
                    "ВОРКЕР Б (Под 2)\n\n"
                    "SELECT id FROM inbox\n"
                    "WHERE status = 'RECEIVED'\n"
                    "FOR UPDATE SKIP LOCKED LIMIT 1;\n\n"
                    "→ Пропускає 1, бере рядок 2",
                    size=11.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))

    f.append(arrow(350, 160, 415, 160, color=FIELD, sw=2))
    f.append(arrow(850, 160, 785, 160, color=NEG, sw=2))

    # Нижня частина: Механізм спливання лізи (Lease Expiry / Heartbeat)
    f.append(fitbox(50, 340, 1100, 190,
                    "МЕХАНІЗМ ВІДНОВЛЕННЯ ПІСЛЯ КРАХУ ВОРКЕРА (LEASE TIMEOUT):\n\n"
                    "1. Воркер А захопив повідомлення 1 і виставив locked_until = NOW() + INTERVAL '30s';\n"
                    "2. Воркер А аварійно завершив роботу (OOM / крах хоста) посеред бізнес-обробки;\n"
                    "3. Фоновий прибиральник або інший воркер через 30 секунд бачить: status='PROCESSING' AND locked_until < NOW();\n"
                    "4. Ліза вважається простроченою → статус скидається в 'RECEIVED' або перехоплюється Воркером В;\n"
                    "5. Повідомлення не зависає назавжди й успішно завершується іншим екземпляром.",
                    size=12, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))

    f.append(fitbox(40, 560, 1120, 55,
                    "FOR UPDATE SKIP LOCKED усуває блокування черги між здоровими воркерами;\n"
                    "розподілені лізи з обмеженим часом гарантують, що аварія воркера не перетворить повідомлення на вічний висяк",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'inbox-concurrency-and-leases.svg'), W, H, *f)


# ── 4. Наскрізний тандем Transactional Outbox та Transactional Inbox ───────
def fig_inbox_outbox_tandem():
    W, H = 1200, 640
    f = []

    f.append(fitbox(40, 20, 1120, 44,
                    "НАСКРІЗНИЙ ТАНДЕМ: Transactional Outbox + Брокер + Transactional Inbox",
                    size=14, bold=True, fill=COOL))

    cw = 340.0
    y0 = 85.0

    # Колонка 1: Сервіс-відправник (Outbox)
    x1 = 50.0
    f.append(fitbox(x1, y0, cw, 60, "СЕРВІС-ВІДПРАВНИК\n(Сервіс замовлень)", size=13, bold=True, fill=COOL, stroke=LINE, sw=2))

    f.append(fitbox(x1, y0 + 75, cw, 170,
                    "ЛОКАЛЬНА ТРАНЗАКЦІЯ БД:\n\n"
                    "1. INSERT INTO orders ...;\n"
                    "2. INSERT INTO outbox (\n"
                    "     id, event_type, payload\n"
                    "   ) VALUES (\n"
                    "     'evt-99', 'OrderCreated', ...\n"
                    "   );\n"
                    "3. COMMIT;",
                    size=11.5, fill="#ffffff", stroke=FIELD, sw=1.6))

    f.append(fitbox(x1, y0 + 260, cw, 75,
                    "Outbox Relay / Debezium CDC:\n"
                    "Вичитує події з outbox\n"
                    "і публікує їх у брокер",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    # Колонка 2: Брокер (Транспорт)
    x2 = x1 + cw + 45
    f.append(fitbox(x2, y0, cw, 60, "БРОКЕР ПОВІДОМЛЕНЬ\n(Kafka / RabbitMQ / AWS SQS)", size=13, bold=True, fill=COOL, stroke=NEG, sw=2))

    f.append(fitbox(x2, y0 + 75, cw, 260,
                    "НЕНАДІЙНИЙ ТРАНСПОРТ:\n\n"
                    "• Гарантія at-least-once\n"
                    "• Можливі збої мережі\n"
                    "• Таймаути споживачів\n"
                    "• Повторні пересилання\n\n"
                    "→ Повідомлення 'evt-99'\n"
                    "може бути доставлено\n"
                    "1, 2 або більше разів!",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.6))

    # Колонка 3: Сервіс-отримувач (Inbox)
    x3 = x2 + cw + 45
    f.append(fitbox(x3, y0, cw, 60, "СЕРВІС-ОТРИМУВАЧ\n(Сервіс платежів)", size=13, bold=True, fill=COOL, stroke=LINE, sw=2))

    f.append(fitbox(x3, y0 + 75, cw, 170,
                    "ЛОКАЛЬНА ТРАНЗАКЦІЯ БД:\n\n"
                    "1. INSERT INTO inbox (msg_id)\n"
                    "   VALUES ('evt-99');\n"
                    "2. UPDATE accounts\n"
                    "   SET balance = balance - 100;\n"
                    "3. COMMIT;\n"
                    "4. ACK брокеру.",
                    size=11.5, fill="#ffffff", stroke=FIELD, sw=1.6))

    f.append(fitbox(x3, y0 + 260, cw, 75,
                    "Результат: дублікати брокера\n"
                    "відсікаються на кроці 1,\n"
                    "рахунок списується рівно один раз",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    # Стрілки взаємодії між блоками
    f.append(arrow(x1 + cw / 2, y0 + 245, x1 + cw / 2, y0 + 258, color=FIELD, sw=2))
    f.append(arrow(x1 + cw, y0 + 297, x2 - 5, y0 + 205, color=NEG, sw=2.2))
    f.append(arrow(x2 + cw, y0 + 205, x3 - 5, y0 + 160, color=NEG, sw=2.2))

    f.append(fitbox(40, 455, 1120, 80,
                    "СИНЕРГІЯ ПАТЕРНІВ:\n"
                    "Transactional Outbox гарантує, що повідомлення ніколи не загубиться на боці відправника;\n"
                    "Transactional Inbox гарантує, що неминучі дублікати транспорту ніколи не пошкодять стан отримувача",
                    size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))

    f.append(fitbox(40, 560, 1120, 55,
                    "разом Outbox та Inbox реалізують семантику effectively-once у розподіленій системі\n"
                    "без використання важких розподілених транзакцій (2PC / XA)",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'inbox-outbox-tandem.svg'), W, H, *f)


# ── 5. Горизонт збереження записів та пастка зомбі-повторів ────────────────
def fig_inbox_pruning_retention_window():
    W, H = 1180, 640
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "ГОРИЗОНТ ЗБЕРЕЖЕННЯ ЗАПИСІВ (TTL): захист від вичерпання диску та зомбі-повторів",
                    size=14, bold=True, fill=COOL))

    x0, x1 = 120.0, 1060.0
    span = x1 - x0
    yAxis = 150.0

    # Часова вісь
    f.append(line(x0, yAxis, x1, yAxis, color=INK, sw=2))
    f.append(arrow(x1 - 10, yAxis, x1, yAxis, color=INK, sw=2))
    f.append(text(x1, yAxis - 18, "Час →", size=13, color=MUTED, anchor="end"))

    # Початковий момент T0
    t0 = x0 + 40
    f.append(line(t0, yAxis - 10, t0, yAxis + 10, color=FIELD, sw=2.4))
    f.append(text(t0, yAxis - 20, "T₀ (Перша обробка)", size=12.5, color=FIELD, bold=True))

    # Максимальний час повторів T_retry_max
    t_retry = t0 + span * 0.40
    f.append(line(t_retry, yAxis - 10, t_retry, yAxis + 10, color=NEG, sw=2.4))
    f.append(text(t_retry, yAxis - 20, "T_retry (Крайній повтор брокера)", size=12, color=NEG, bold=True))

    # Межа очищення TTL (T_prune)
    t_prune = t0 + span * 0.70
    f.append(line(t_prune, yAxis - 10, t_prune, yAxis + 10, color=POS, sw=2.4))
    f.append(text(t_prune, yAxis - 20, "T_prune (Очищення запису з Inbox)", size=12, color=POS, bold=True))

    # Зелена зона безпечної дедуплікації
    f.append(rect(t0, yAxis + 25, t_prune - t0, 36, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text((t0 + t_prune) / 2, yAxis + 48, "БЕЗПЕЧНЕ ВІКНО: msg_id є в таблиці inbox → повтори безпечно відсікаються", size=11.5, color=FIELD, bold=True))

    # Червона небезпечна зона (після TTL)
    f.append(rect(t_prune, yAxis + 25, x1 - t_prune - 30, 36, fill=WARM, stroke=POS, sw=1.8))
    f.append(text((t_prune + x1 - 30) / 2, yAxis + 48, "ЗОНА РИЗИКУ: запис видалено", size=11.5, color=POS, bold=True))

    # Сценарій 1: Легітимний повтор
    f.append(fitbox(x0 + 40, 245, 420, 120,
                    "ЛЕГІТИМНИЙ ПОВТОР У МЕЖАХ ВІКНА:\n\n"
                    "• Повтор надходить до моменту T_prune\n"
                    "• Рядок знайдено в таблиці inbox\n"
                    "• Дубль ігнорується, баланс захищено\n"
                    "• Брокеру повертається ACK",
                    size=11.5, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(arrow(t0 + span * 0.22, yAxis + 61, t0 + span * 0.22, 240, color=FIELD, sw=1.8))

    # Сценарій 2: Зомбі-повтор
    f.append(fitbox(t_prune - 30, 245, 440, 120,
                    "ПАСТКА «ЗОМБІ-ПОВТОРУ» (ПІСЛЯ TTL):\n\n"
                    "• Зависле повідомлення переграно вручну після T_prune\n"
                    "• Запис про попередню обробку вже видалено з inbox!\n"
                    "• Споживач вважає повідомлення новим\n"
                    "• ПОВТОРНЕ СПИСАННЯ КОШТІВ (Аварія!)",
                    size=11.5, fill=WARM, stroke=POS, sw=1.8))
    f.append(arrow(t_prune + span * 0.14, yAxis + 61, t_prune + span * 0.14, 240, color=POS, sw=1.8))

    # Математичне правило розрахунку
    f.append(fitbox(120, 395, 940, 110,
                    "МАТЕМАТИЧНИЙ РОЗРАХУНОК ВІКНА ЗБЕРЕЖЕННЯ (RETENTION TTL):\n\n"
                    "TTL_inbox  >  Max_Broker_Redelivery_Period  +  DeadLetter_Replay_Buffer  +  Clock_Skew\n\n"
                    "Якщо брокер робить повтори протягом 48 годин, а регламент ручного перегравання DLQ складає 5 днів,\n"
                    "мінімальний строк життя записів у таблиці inbox повинен становити не менше 7–14 днів.",
                    size=12, bold=True, fill=COOL, stroke=NEG, sw=1.8))

    f.append(fitbox(40, 555, 1100, 52,
                    "таблицю inbox не можна нарощувати нескінченно, але передчасне очищення знищує дедуплікацію;\n"
                    "вікно очищення проектується з урахуванням найгіршого часу реакції на інциденти та ручних повторів",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'inbox-pruning-retention-window.svg'), W, H, *f)


fig_inbox_dual_write_failure()
fig_transactional_inbox_lifecycle()
fig_inbox_concurrency_and_leases()
fig_inbox_outbox_tandem()
fig_inbox_pruning_retention_window()

print("Фігури для inbox-pattern успішно згенеровано у:", OUT)
