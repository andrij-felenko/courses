# -*- coding: utf-8 -*-
"""Фігури до теми «Кеш-когерентність між сервісами».

Генерує 4 SVG діаграми:
1. stale-overwrite-race.svg        — Гонка застарілого запису (Stale-Overwrite Race)
2. lease-token-resolution.svg     — Розв'язання гонки через маркери оренди (Lease Tokens)
3. two-tier-coherence-arch.svg    — Архітектура дворівневого кешування (L1 In-Memory + L2 Redis + CDC)
4. redis-tracking-invalidation.svg — Протокол клієнтського трекінгу Redis 6 (Client-Side Tracking)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / застарілий стан / гонка
COOL = "#eaf0fd"   # нейтральне / клієнт / сховище / пам'ять
GOOD = "#e8f6ee"   # успіх / узгодженість / свіжі дані
WARN = "#fef9e7"   # брокер / повідомлення / проміжне


# ── 1. Гонка застарілого запису ─────────────────────────────────────────────
def fig_stale_overwrite_race():
    W, H = 1180, 580
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "ГОНКА ЗАСТАРІЛОГО ЗАПИСУ (STALE-OVERWRITE RACE): як кеш отруюється старими даними",
                    size=13, bold=True, fill=COOL))

    # Колонка 1: Читач (Сервіс A)
    c1_x, c1_y, c1_w, c1_h = 40.0, 75.0, 340.0, 480.0
    f.append(rect(c1_x, c1_y, c1_w, c1_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(c1_x + 15, c1_y + 15, c1_w - 30, 36,
                    "КЛІЄНТ ЧИТАННЯ (СЕРВІС A)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(c1_x + 15, c1_y + 65, c1_w - 30, 56,
                    "1. GET user:42 → Кеш-промах (Cache Miss)\n"
                    "Дані у кеші відсутні",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(c1_x + 15, c1_y + 135, c1_w - 30, 60,
                    "2. Запит у СКБД: SELECT ... WHERE id=42\n"
                    "Отримано: {id: 42, balance: 100} (Версія 1)",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(c1_x + 15, c1_y + 215, c1_w - 30, 75,
                    "⚡ ЗАТРИМКА (GC Pause / лаг мережі):\n"
                    "Процес Сервісу A засинає на 80 мс\n"
                    "і ще не встиг виконати SET у кеш!",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.6))

    f.append(fitbox(c1_x + 15, c1_y + 310, c1_w - 30, 65,
                    "5. Пробудження Сервісу A:\n"
                    "SET user:42 {balance: 100}\n"
                    "Запис застарілої Версії 1 у кеш!",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(c1_x + 15, c1_y + 395, c1_w - 30, 65,
                    "НАСЛІДОК: Кеш містить 100 замість 150.\n"
                    "Постійне отруєння до завершення TTL!",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Колонка 2: База Даних та Кеш (Центральні ресурси)
    c2_x, c2_y, c2_w, c2_h = 420.0, 75.0, 340.0, 480.0
    f.append(rect(c2_x, c2_y, c2_w, c2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(c2_x + 15, c2_y + 15, c2_w - 30, 36,
                    "РЕСУРСИ (СКБД ТА КЕШ REDIS)",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.2))

    f.append(fitbox(c2_x + 15, c2_y + 65, c2_w - 30, 56,
                    "КЕШ REDIS:\nКлюч user:42 відсутній (Null)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(c2_x + 15, c2_y + 135, c2_w - 30, 60,
                    "СКБД (Master PostgreSQL):\n"
                    "Початковий стан рядка: balance = 100",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(c2_x + 15, c2_y + 215, c2_w - 30, 75,
                    "СКБД: UPDATE accounts SET balance = 150;\n"
                    "COMMIT (Зафіксовано Версію 2)\n"
                    "CDC надсилає інвалідацію: DEL user:42",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(c2_x + 15, c2_y + 310, c2_w - 30, 65,
                    "КЕШ REDIS:\n"
                    "Приймає SET user:42 {balance: 100}\n"
                    "Перезаписує порожній ключ старійшиною!",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.5))

    f.append(fitbox(c2_x + 15, c2_y + 395, c2_w - 30, 65,
                    "СТАН РОЗХОДЖЕННЯ:\n"
                    "СКБД = 150 (Свіже) | Кеш = 100 (Брудне)",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Колонка 3: Письменник (Сервіс B)
    c3_x, c3_y, c3_w, c3_h = 800.0, 75.0, 340.0, 480.0
    f.append(rect(c3_x, c3_y, c3_w, c3_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(c3_x + 15, c3_y + 15, c3_w - 30, 36,
                    "КЛІЄНТ ЗАПИСУ (СЕРВІС B)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(c3_x + 15, c3_y + 65, c3_w - 30, 56,
                    "Очікування події бізнес-мутації\n(поповнення рахунку на 50 грн)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(c3_x + 15, c3_y + 135, c3_w - 30, 60,
                    "3. Виконання мутації в БД:\n"
                    "UPDATE accounts SET balance = 150\n"
                    "Транзакція COMMIT успішна",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(c3_x + 15, c3_y + 215, c3_w - 30, 75,
                    "4. Інвалідація кешу:\n"
                    "Виклик DEL user:42 у Redis\n"
                    "Кеш чистий, але Сервіс A вже несе старе!",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(c3_x + 15, c3_y + 310, c3_w - 30, 65,
                    "Сервіс B вважає інвалідацію завершеною,\n"
                    "але кеш щойно отруєно Сервісом A",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(c3_x + 15, c3_y + 395, c3_w - 30, 65,
                    "Подальші запити інших сервісів\n"
                    "читатимуть застарілі 100 грн з кешу",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.2))

    # Стрілки взаємодії
    f.append(arrow(c1_x + c1_w - 15, c1_y + 165, c2_x + 15, c2_y + 165, color=FIELD, sw=1.8))
    f.append(arrow(c3_x + 15, c3_y + 165, c2_x + c2_w - 15, c2_y + 235, color=FIELD, sw=1.8))
    f.append(arrow(c3_x + 15, c3_y + 250, c2_x + c2_w - 15, c2_y + 250, color=MUTED, sw=1.8))
    f.append(arrow(c1_x + c1_w - 15, c1_y + 340, c2_x + 15, c2_y + 340, color=POS, sw=2.0))

    render(os.path.join(OUT, "stale-overwrite-race.svg"), W, H, *f)


# ── 2. Розв'язання гонки через маркери оренди ──────────────────────────────
def fig_lease_token_resolution():
    W, H = 1180, 560
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "РОЗВ'ЯЗАННЯ ГОНКИ ЧЕРЕЗ МАРКЕРИ ОРЕНДИ (LEASE TOKENS / GENERATION CAS)",
                    size=13, bold=True, fill=GOOD))

    # Стовпчик 1: Клієнт читання (Сервіс A з орендою)
    ax, ay, aw, ah = 40.0, 75.0, 340.0, 460.0
    f.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(ax + 15, ay + 15, aw - 30, 36,
                    "СЕРВІС А (ЧИТАННЯ З ОРЕНДОЮ)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(ax + 15, ay + 65, aw - 30, 60,
                    "1. GET_LEASE user:42\n"
                    "Кеш повертає: MISS + Lease_ID: 0x9A4F\n"
                    "(Токен дійсний для поповнення кешу)",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(ax + 15, ay + 140, aw - 30, 60,
                    "2. Читання зі СКБД:\n"
                    "Отримано {balance: 100} (Версія 1)\n"
                    "Затримка потоку (GC / мережа 80 мс)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(ax + 15, ay + 215, aw - 30, 80,
                    "5. Спроба запису в кеш із токеном:\n"
                    "SET user:42 {balance: 100}\n"
                    "LEASE_TOKEN = 0x9A4F",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(ax + 15, ay + 310, aw - 30, 60,
                    "6. Відповідь кешу:\n"
                    "❌ REJECTED / LEASE_INVALIDATED\n"
                    "Запис відхилено кеш-сервером!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    f.append(fitbox(ax + 15, ay + 380, aw - 30, 65,
                    "РЕЗУЛЬТАТ: Застарілий запис ВІДХИЛЕНО.\n"
                    "Кеш захищено від отруєння старим станом!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Стовпчик 2: Кеш із підтримкою оренди
    bx, by, bw, bh = 420.0, 75.0, 340.0, 460.0
    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(bx + 15, by + 15, bw - 30, 36,
                    "КЕШ ІЗ СЕРВЕРОМ ОРЕНДИ (LEASE SERVER)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(bx + 15, by + 65, bw - 30, 60,
                    "Реєстрація активної оренди:\n"
                    "ActiveLeases[user:42] = 0x9A4F\n"
                    "Таймаут оренди = 10 секунд",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(bx + 15, by + 140, bw - 30, 60,
                    "Очікування поповнення або інвалідації\n"
                    "Ключ заблокований від stampede",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(bx + 15, by + 215, bw - 30, 80,
                    "4. Отримано INVAL user:42 від Сервісу B:\n"
                    "ActiveLeases[user:42] → СКАСОВАНО!\n"
                    "Усі видані токени 0x9A4F стають недійсними",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.6))

    f.append(fitbox(bx + 15, by + 310, bw - 30, 60,
                    "Перевірка токена Сервісу A:\n"
                    "Token 0x9A4F != ActiveLease (Скасовано)\n"
                    "→ Повернення помилки клієнту",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.4))

    f.append(fitbox(bx + 15, by + 380, bw - 30, 65,
                    "Кеш лишається порожнім або оновлюється\n"
                    "наступним читачем зі свіжою орендою",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Стовпчик 3: Сервіс запису B
    cx, cy, cw, ch = 800.0, 75.0, 340.0, 460.0
    f.append(rect(cx, cy, cw, ch, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(cx + 15, cy + 15, cw - 30, 36,
                    "СЕРВІС B (ЗАПИС ТА ІНВАЛІДАЦІЯ)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(cx + 15, cy + 65, cw - 30, 60,
                    "Сервіс B готує транзакцію запису\n"
                    "(зміна балансу на 150 грн)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(cx + 15, cy + 140, cw - 30, 60,
                    "3. Успішний COMMIT у СКБД:\n"
                    "Новий стан: balance = 150 (Версія 2)\n"
                    "Дані надійно збережено на диску",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(cx + 15, cy + 215, cw - 30, 80,
                    "4. Публікація інвалідації:\n"
                    "INVALIDATE user:42\n"
                    "Скидає стан оренди в кеш-сервері",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(cx + 15, cy + 310, cw - 30, 60,
                    "Інвалідація гарантовано випередила\n"
                    "запізнілий SET від Сервісу A",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(cx + 15, cy + 380, cw - 30, 65,
                    "СТАН УЗГОДЖЕНОСТІ:\n"
                    "БД = 150 | Кеш = Безпечно очищено",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Стрілки
    f.append(arrow(ax + aw - 15, ay + 95, bx + 15, by + 95, color=MUTED, sw=1.8))
    f.append(arrow(cx + 15, cy + 255, bx + bw - 15, by + 255, color=POS, sw=2.0))
    f.append(arrow(ax + aw - 15, ay + 255, bx + 15, by + 255, color=MUTED, sw=1.8))
    f.append(arrow(bx + 15, by + 340, ax + aw - 15, ay + 340, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "lease-token-resolution.svg"), W, H, *f)


# ── 3. Дворівнева архітектура кешування ─────────────────────────────────────
def fig_two_tier_coherence_arch():
    W, H = 1180, 600
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "АРХІТЕКТУРА ДВОРІВНЕВОГО КОГЕРЕНТНОГО КЕШУВАННЯ (L1 IN-MEMORY + L2 REDIS + CDC)",
                    size=13, bold=True, fill=COOL))

    # Ліва частина: Інстанси Сервісу з локальним L1 кешем
    f.append(rect(40, 75, 480, 480, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(55, 90, 450, 34,
                    "КЛАСТЕР МІКРОСЕРВІСІВ (СЕРВІС КАТАЛОГУ / ЗАМОВЛЕНЬ)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    # Інстанс 1
    f.append(rect(60, 135, 440, 185, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    f.append(fitbox(75, 145, 410, 28, "ІНСТАНС #1 (POD 1)", size=11, bold=True, fill="#ffffff"))
    f.append(fitbox(75, 180, 410, 55,
                    "L1 Local Cache (RAM / 100 нс):\n"
                    "Кеш у процесі (Caffeine / Ristretto / Sharded Map)\n"
                    "Зберігає гарячі об'єкти без мережевих RTT",
                    size=10.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(75, 245, 410, 65,
                    "Слухач інвалідації (Invalidation Listener):\n"
                    "• Приймає події по шині NATS / Kafka / Redis PubSub\n"
                    "• Очищає L1 слот або оновлює версію атомарно",
                    size=10.5, bold=True, fill=WARN, stroke=MUTED, sw=1.0))

    # Інстанс 2
    f.append(rect(60, 335, 440, 205, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    f.append(fitbox(75, 345, 410, 28, "ІНСТАНС #2 (POD 2)", size=11, bold=True, fill="#ffffff"))
    f.append(fitbox(75, 380, 410, 55,
                    "L1 Local Cache (RAM / 100 нс):\n"
                    "Ізольований адресний простір другого вузла\n"
                    "Потребує когерентного скидання при змінах",
                    size=10.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(75, 445, 410, 80,
                    "Клієнтський трекінг (Redis Tracking Client):\n"
                    "RESP3 підключення: тримає інвалідні повідомлення\n"
                    "та витісняє локальні змінні при мутаціях у L2",
                    size=10.5, bold=True, fill=WARN, stroke=MUTED, sw=1.0))

    # Права частина: Спільні ресурси (L2, Брокер, CDC, СКБД)
    rx, ry, rw, rh = 560.0, 75.0, 580.0, 480.0
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(rx + 15, ry + 15, rw - 30, 34,
                    "СПІЛЬНИЙ ШАР ЗБЕРЕЖЕННЯ ТА ШИНА ІНВАЛІДАЦІЇ",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.2))

    # L2 Спільний Кеш
    f.append(fitbox(rx + 25, ry + 60, rw - 50, 70,
                    "L2 Спільний Кеш (Redis Cluster / Memcached / 1-2 мс):\n"
                    "• Централізоване сховище ключ-значення для всіх інстансів\n"
                    "• Підтримка атомарних Lease Tokens, CAS та версій\n"
                    "• Запобігає навантаженню бази при промахах L1",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    # Шина Інвалідації
    f.append(fitbox(rx + 25, ry + 145, rw - 50, 70,
                    "Шина Інвалідації (Kafka / NATS / Redis PubSub):\n"
                    "• Топік: cache-invalidation-events\n"
                    "• Повідомлення: {key: 'prod:12', ver: 4, action: 'EVICT'}\n"
                    "• Трансляція (Fan-out) на всі поди сервісів",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    # CDC Engine
    f.append(fitbox(rx + 25, ry + 230, rw - 50, 65,
                    "CDC Engine (Debezium / PostgreSQL WAL Reader):\n"
                    "Зчитує зафіксовані транзакції з бінарного журналу бази\n"
                    "Гарантує відсутність фантомних або втрачених подій",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Master DB
    f.append(fitbox(rx + 25, ry + 310, rw - 50, 65,
                    "Первинна СКБД (Master PostgreSQL / MySQL):\n"
                    "Єдине джерело правди (Single Source of Truth)\n"
                    "ACID-транзакції, первинні таблиці та WAL",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    # Підсумок узгодженості
    f.append(fitbox(rx + 25, ry + 390, rw - 50, 70,
                    "ГАРАНТІЯ КОГЕРЕНТНОСТІ:\n"
                    "Мутація в БД → WAL → CDC → Шина → L2 Evict + L1 Evict на всіх вузлах.\n"
                    "Повна ліквідація вікна застарілості без блокуючого 2PC!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Зв'язки між блоками
    f.append(arrow(rx + 290, ry + 310, rx + 290, ry + 295, color=FIELD, sw=1.8))
    f.append(arrow(rx + 290, ry + 230, rx + 290, ry + 215, color=FIELD, sw=1.8))
    f.append(arrow(rx + 290, ry + 145, rx + 290, ry + 130, color=MUTED, sw=1.8))
    f.append(arrow(rx + 25, ry + 180, 500, 275, color=POS, sw=2.0))
    f.append(arrow(rx + 25, ry + 180, 500, 485, color=POS, sw=2.0))

    render(os.path.join(OUT, "two-tier-coherence-arch.svg"), W, H, *f)


# ── 4. Протокол клієнтського трекінгу Redis 6 ──────────────────────────────
def fig_redis_tracking_invalidation():
    W, H = 1180, 560
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "ПРОТОКОЛ КЛІЄНТСЬКОГО ТРЕКІНГУ REDIS 6+ (RESP3 CLIENT-SIDE TRACKING)",
                    size=13, bold=True, fill=COOL))

    # Сервіс А (Клієнт 1)
    x1, y1, w1, h1 = 40.0, 75.0, 320.0, 460.0
    f.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(x1 + 15, y1 + 15, w1 - 30, 36,
                    "СЕРВІС А (ЧИТАЧ З L1 КЕШЕМ)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(x1 + 15, y1 + 65, w1 - 30, 60,
                    "1. Включення трекінгу:\n"
                    "CLIENT TRACKING on REDIRECT ...\n"
                    "(Реєструє клієнта в сервері)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(x1 + 15, y1 + 140, w1 - 30, 65,
                    "2. Читання ключа:\n"
                    "GET item:99 → повертає 'Phone'\n"
                    "Зберігає 'Phone' у локальний L1 RAM",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(x1 + 15, y1 + 220, w1 - 30, 65,
                    "3. Швидкі повторні читання:\n"
                    "Читання прямо з локальної RAM (0 мс)\n"
                    "Жодних звернень до мережі!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(x1 + 15, y1 + 300, w1 - 30, 65,
                    "5. Асинхронне push-повідомлення:\n"
                    "<-push- ['invalidate', ['item:99']]\n"
                    "Миттєве вилучення item:99 з L1",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.6))

    f.append(fitbox(x1 + 15, y1 + 380, w1 - 30, 65,
                    "6. Наступний GET:\n"
                    "L1 Miss → новий похід у Redis/БД\n"
                    "Отримання оновленої ціни!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Сервер Redis (Tracking Table)
    x2, y2, w2, h2 = 400.0, 75.0, 380.0, 460.0
    f.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(x2 + 15, y2 + 15, w2 - 30, 36,
                    "СЕРВЕР REDIS (ТАБЛИЦЯ ТРЕКІНГУ / RADIX TREE)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(x2 + 15, y2 + 65, w2 - 30, 60,
                    "Таблиця недійсності (Invalidation Table):\n"
                    "item:99 → [Client_ID: 104 (Сервіс A)]",
                    size=11, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(x2 + 15, y2 + 140, w2 - 30, 65,
                    "Сервер запам'ятовує, що Клієнт 104\n"
                    "зчитав ключ item:99 і кешує його в себе",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(x2 + 15, y2 + 220, w2 - 30, 65,
                    "4. Отримано запис від Сервісу B:\n"
                    "MSET item:99 'NewPhone'\n"
                    "Мутація значення ключа в пам'яті",
                    size=11, bold=True, fill=WARN, stroke=MUTED, sw=1.2))

    f.append(fitbox(x2 + 15, y2 + 300, w2 - 30, 65,
                    "Пошук підписників на item:99:\n"
                    "Знайдено Client 104 → Push Invalidation!\n"
                    "Запис вилучається з Tracking Table",
                    size=11, bold=True, fill=WARM, stroke=POS, sw=1.5))

    f.append(fitbox(x2 + 15, y2 + 380, w2 - 30, 65,
                    "Оптимізація інвалідації:\n"
                    "Одне сповіщення на ключ до наступного GET.\n"
                    "Немає спаму повідомлень при серії записів!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Сервіс B (Клієнт 2 - Письменник)
    x3, y3, w3, h3 = 820.0, 75.0, 320.0, 460.0
    f.append(rect(x3, y3, w3, h3, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(x3 + 15, y3 + 15, w3 - 30, 36,
                    "СЕРВІС B (ПИСЬМЕННИК)",
                    size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.2))

    f.append(fitbox(x3 + 15, y3 + 65, w3 - 30, 60,
                    "Сервіс B оновлює каталог товарів\n"
                    "(зміна характеристик item:99)",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(x3 + 15, y3 + 140, w3 - 30, 65,
                    "Транзакційне оновлення в СКБД\n"
                    "та публікація в спільний Redis",
                    size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.0))

    f.append(fitbox(x3 + 15, y3 + 220, w3 - 30, 65,
                    "4. Виклик команди:\n"
                    "SET item:99 'NewPhone'\n"
                    "Зміна ціни або опису товару",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(x3 + 15, y3 + 300, w3 - 30, 65,
                    "Сервісу B не потрібно знати про L1 кеші\n"
                    "інших 50-ти інстансів сервісів!",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(x3 + 15, y3 + 380, w3 - 30, 65,
                    "ПЕРЕВАГА:\n"
                    "Автоматична когерентність L1 на рівні ядра Redis.",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Стрілки
    f.append(arrow(x1 + w1 - 15, y1 + 172, x2 + 15, y2 + 172, color=FIELD, sw=1.8))
    f.append(arrow(x3 + 15, y3 + 252, x2 + w2 - 15, y2 + 252, color=FIELD, sw=1.8))
    f.append(arrow(x2 + 15, y2 + 332, x1 + w1 - 15, y1 + 332, color=POS, sw=2.0))

    render(os.path.join(OUT, "redis-tracking-invalidation.svg"), W, H, *f)


def main():
    fig_stale_overwrite_race()
    fig_lease_token_resolution()
    fig_two_tier_coherence_arch()
    fig_redis_tracking_invalidation()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
