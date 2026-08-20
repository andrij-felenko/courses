# -*- coding: utf-8 -*-
"""Фігури теми «Дрібні кеш-тактики, що рятують проди». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#eaf0fd"
WARN_F  = "#fef9e7"
WARN_S  = "#f39c12"


# ── 1. ttl-avalanche-jitter: лавиноподібне застарівання проти джиттеру ─────────
def fig_ttl_avalanche_jitter():
    W, H = 1000, 520
    f = []

    f.append(text(W / 2, 34, "Синхронізоване застарівання TTL проти розкиду (TTL Jitter)",
                  size=16, bold=True))

    # Секція 1: Без джиттеру (Фіксований TTL = 3600 с)
    f.append(fitbox(40, 60, 440, 195,
                    "1. Без джиттеру: фіксований TTL = 3600 с\n\n"
                    "• 100 000 ключів збережено о 00:00:00 (TTL = 1 год)\n"
                    "• Рівно о 01:00:00 всі 100 000 ключів зникають одночасно\n"
                    "• Частка влучань обвалюється з 99 % до 2 %\n"
                    "• Шторм промахів (Cache Avalanche) перевантажує БД",
                    size=12, fill=RED_F, stroke=POS, pad=10))

    f.append(fitbox(520, 60, 440, 195,
                    "Навантаження на первинну БД (Без джиттеру)\n\n"
                    "RPS до БД:\n"
                    "  00:00 – 00:59  |== (200 RPS — фонові промахи)\n"
                    "  01:00:00       |============================== (65 000 RPS СПАЛАХ!)\n"
                    "  01:00:05       | Пул з'єднань СУБД вичерпано -> Відмова сервісу",
                    size=12, fill=FILL, stroke=POS, pad=10, bold=False))

    # Секція 2: З джиттером (TTL = 3600 ± 600 с)
    f.append(fitbox(40, 280, 440, 195,
                    "2. З розкидом: TTL = 3600 ± 600 с (Jitter ±15 %)\n\n"
                    "• Кожен ключ отримує випадковий TTL від 3000 до 4200 с\n"
                    "• Вичерпання ключів розмазується у вікні 20 хвилин\n"
                    "• Частка влучань залишається стабільною (> 96 %)\n"
                    "• Навантаження на БД зростає плавно й без піків",
                    size=12, fill=GREEN_F, stroke=FIELD, pad=10))

    f.append(fitbox(520, 280, 440, 195,
                    "Навантаження на первинну БД (З джиттером)\n\n"
                    "RPS до БД:\n"
                    "  00:50 – 01:10  |====== (800–1200 RPS — плавне оновлення)\n"
                    "  01:00:00       |====== (1100 RPS — нормальна робота)\n"
                    "  Результат:     | Черги відсутні, база працює стабільно",
                    size=12, fill=FILL, stroke=FIELD, pad=10, bold=False))

    f.append(text(W / 2, 498,
                  "Формула: TTL_actual = TTL_base · (1 + Uniform(-J, +J)), де J = 0.10..0.20",
                  size=12, color=MUTED))

    render(out("ttl-avalanche-jitter.svg"), W, H, *f,
           title="Розкид TTL запобігає лавинному перевантаженню бази даних")


# ── 2. negative-caching: захист від проникнення кешу ─────────────────────────
def fig_negative_caching():
    W, H = 1020, 520
    f = []

    f.append(text(W / 2, 34, "Проникнення кешу (Cache Penetration) та кешування порожнечі",
                  size=16, bold=True))

    # Ліва колонка: Без Negative Caching
    f.append(fitbox(40, 60, 445, 420,
                    "БЕЗ кешування порожнечі (Вразливість)\n\n"
                    "1. Клієнт / бот запитує неіснуючий ключ:\n"
                    "   GET /users/999999999 (ID немає в системі)\n\n"
                    "2. Сервіс перевіряє Redis -> ПРОМАХ (ключа нема)\n\n"
                    "3. Сервіс робить SELECT у PostgreSQL -> 0 рядків\n\n"
                    "4. У кеш нічого не пишеться (бо значення null)\n\n"
                    "5. Наступні 10 000 таких самих запитів знову йдуть\n"
                    "   напряму в БД, створюючи прямий DDoS на дисковий ввід/вивід.\n\n"
                    "Наслідок: 100 % запитів до неіснуючих сутностей б'ють у базу.",
                    size=12, fill=RED_F, stroke=POS, pad=12))

    # Права колонка: З Negative Caching
    f.append(fitbox(535, 60, 445, 420,
                    "З кешуванням порожнечі (Negative Caching)\n\n"
                    "1. Клієнт запитує неіснуючий ключ:\n"
                    "   GET /users/999999999\n\n"
                    "2. Сервіс перевіряє Redis -> ПРОМАХ (перший раз)\n\n"
                    "3. Сервіс робить SELECT у PostgreSQL -> 0 рядків\n\n"
                    "4. Сервіс записує маркер порожнечі в Redis:\n"
                    "   SET users:999999999 \"__NULL__\" EX 60\n\n"
                    "5. Наступні 9 999 запитів отримують маркер із пам'яті\n"
                    "   і миттєво повертають 404 Not Found без виклику бази даних.\n\n"
                    "Результат: База захищена, короткий TTL (30–60 с) запобігає застряганню.",
                    size=12, fill=GREEN_F, stroke=FIELD, pad=12))

    f.append(text(W / 2, 500,
                  "Правило: Маркер відсутності записується з коротким TTL, а при створенні сутності ключ інвалідується.",
                  size=12, color=MUTED))

    render(out("negative-caching.svg"), W, H, *f,
           title="Кешування відсутності запису захищає базу даних від сканування неіснуючих ID")


# ── 3. stale-while-revalidate: часова шкала Soft TTL та SWR ─────────────────
def fig_stale_while_revalidate():
    W, H = 1020, 500
    f = []

    f.append(text(W / 2, 34, "Часова шкала Stale-While-Revalidate та дворівневого часу життя (Dual TTL)",
                  size=16, bold=True))

    # Три фази на часовій шкалі
    # Фаза 1: Свіжі дані (Fresh)
    f.append(fitbox(40, 75, 300, 160,
                    "Фаза 1: Свіжі дані (Fresh)\n"
                    "[ t = 0 ... Soft TTL = 300 c ]\n\n"
                    "• Читання з кешу: 0.5 мс\n"
                    "• Статус: FRESH_HIT\n"
                    "• Жодних фонових дій\n"
                    "• Клієнт отримує актуальні дані",
                    size=12, fill=GREEN_F, stroke=FIELD, pad=10))

    # Фаза 2: Застарілі, але придатні (Stale / Revalidate)
    f.append(fitbox(360, 75, 300, 160,
                    "Фаза 2: Оновлення (SWR)\n"
                    "[ Soft TTL 300 c ... Hard TTL 3600 c ]\n\n"
                    "• Читання з кешу: 0.5 мс (STALE_HIT)\n"
                    "• Клієнт НЕ чекає на базу даних!\n"
                    "• Фоновий потік оновлює кеш з БД\n"
                    "• Single-Flight захищає оновлення",
                    size=12, fill=BLUE_F, stroke=NEG, pad=10))

    # Фаза 3: Повне вичерпання (Expired / Hard Miss)
    f.append(fitbox(680, 75, 300, 160,
                    "Фаза 3: Видалення (Hard Expired)\n"
                    "[ t > Hard TTL = 3600 c ]\n\n"
                    "• Ключ виселяється з кешу\n"
                    "• Статус: HARD_MISS\n"
                    "• Синхронне звернення до БД\n"
                    "• Або Stale Fallback при збої",
                    size=12, fill=WARN_F, stroke=WARN_S, pad=10))

    # Нижня порівняльна панель: Поведінка під час деградації БД
    f.append(fitbox(40, 260, 940, 195,
                    "Поведінка під час деградації або відмови первинної бази даних (Stale-As-Fallback)\n\n"
                    "• Звичайна система без SWR: База падає -> Запити отримують таймаут 2.0 с -> Пул з'єднань забивається -> 500 Server Error для 100 % клієнтів.\n"
                    "• Система з Stale Fallback: База падає -> Фоновий ревалідатор фіксує таймаут або 5xx -> Кеш подовжує життя Stale-значення -> Користувачі миттєво отримують дані з кешу (0.5 мс) із заголовком Warning: 110 Response is Stale.\n"
                    "• Результат: Повна стійкість (Graceful Degradation) користувацького інтерфейсу під час ремонтних робіт чи аварій СУБД.",
                    size=12, fill=FILL, stroke=LINE, pad=12, bold=False))

    f.append(text(W / 2, 480,
                  "SWR поєднує миттєву швидкість RAM для клієнта із захистом бекенду від блокуючих очікувань.",
                  size=12, color=MUTED))

    render(out("stale-while-revalidate.svg"), W, H, *f,
           title="Stale-While-Revalidate усуває затримки оновлення та забезпечує деградацію")


# ── 4. two-tier-cache-topology: дворівневий кеш та версіонування ключів ──────
def fig_two_tier_cache_topology():
    W, H = 1020, 520
    f = []

    f.append(text(W / 2, 34, "Дворівневий кеш (L1 In-Memory + L2 Redis) та миттєва інвалідація просторів назв",
                  size=16, bold=True))

    # Вузол Pod 1
    f.append(fitbox(40, 65, 270, 190,
                    "App Pod 1 (Вузол 1)\n\n"
                    "• L1 Cache: In-Process RAM\n"
                    "  Затримка: < 1 мкс\n"
                    "  Мікро-TTL: 2–5 секунд\n"
                    "• Підписник на шину Pub/Sub:\n"
                    "  Слухає події скидання L1",
                    size=12, fill=BLUE_F, stroke=NEG, pad=10))

    # Вузол Pod 2
    f.append(fitbox(710, 65, 270, 190,
                    "App Pod 2 (Вузол 2)\n\n"
                    "• L1 Cache: In-Process RAM\n"
                    "  Затримка: < 1 мкс\n"
                    "  Мікро-TTL: 2–5 секунд\n"
                    "• Підписник на шину Pub/Sub:\n"
                    "  Слухає події скидання L1",
                    size=12, fill=BLUE_F, stroke=NEG, pad=10))

    # Центральний рівень L2 (Redis)
    f.append(fitbox(340, 65, 340, 190,
                    "L2 Спільний розподілений кеш\n(Redis Cluster / Memcached)\n\n"
                    "• Затримка мережі: 0.5–1.5 мс\n"
                    "• Зберігає повний стан сутностей\n"
                    "• Канал інвалідації: Redis Pub/Sub\n"
                    "• Лічильник версій просторів назв",
                    size=12, fill=GREEN_F, stroke=FIELD, pad=10))

    # Нижня панель: Версіонування просторів назв (Key Versioning)
    f.append(fitbox(40, 280, 940, 195,
                    "Миттєва безблокуюча інвалідація групи ключів через лічильник версій (Namespacing)\n\n"
                    "• Проблема: Команда KEYS tenant:42:* або масовий DEL у Redis блокує однопотоковий Event Loop і кладе продакшн.\n"
                    "• Рішення: Зберігаємо версію простору: GET v:tenant:42 -> повертає 7. Формуємо ключі: tenant:42:v7:orders:101.\n"
                    "• Миттєве скидання всіх даних тенанта: Атомарна команда INCR v:tenant:42 (нова версія 8).\n"
                    "• Усі попередні сотні тисяч ключів із суфіксом v7 стають миттєво невидимими і тихо зникають за власним TTL.",
                    size=12, fill=FILL, stroke=LINE, pad=12, bold=False))

    f.append(text(W / 2, 498,
                  "Дворівнева архітектура розвантажує мережу L2, а версіонування усуває блокуючі сканування пам'яті.",
                  size=12, color=MUTED))

    render(out("two-tier-cache-topology.svg"), W, H, *f,
           title="Дворівневий кеш та логічне версіонування ключів")


if __name__ == '__main__':
    fig_ttl_avalanche_jitter()
    fig_negative_caching()
    fig_stale_while_revalidate()
    fig_two_tier_cache_topology()
    print("All figures generated successfully.")
