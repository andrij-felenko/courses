# -*- coding: utf-8 -*-
"""Фігури для теми «Розподілений кеш (memcached/Redis-клас)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#eaf0fd"
GRAY_F  = "#f4f6f8"
WARN_F  = "#fff3cd"

# ── 1. distributed-cache-topologies: Клієнтський шардинг проти Проксі та Кластера ──
def fig_topologies():
    W, H = 1040, 520
    f = []

    # Три вертикальні зони
    f.append(line(346, 40, 346, 500, color=MUTED, sw=1, dash="4,4"))
    f.append(line(693, 40, 693, 500, color=MUTED, sw=1, dash="4,4"))

    # 1. Клієнтська маршрутизація (Memcached / Ketama)
    f.append(text(173, 55, "1. Клієнтська маршрутизація", size=15, bold=True))
    f.append(text(173, 75, "Ketama / Consistent Hashing", size=11, color=MUTED))

    f.append(fitbox(63, 100, 220, 54, "Застосунок\n(Smart Client: Кільце хешів)", size=12, bold=True, fill=BLUE_F, stroke=NEG))

    f.append(arrow(113, 154, 80, 230, color=FIELD, sw=1.6))
    f.append(text(50, 185, "hash(k₁) → N₁", size=10, color=INK, anchor="end"))

    f.append(arrow(173, 154, 173, 230, color=FIELD, sw=1.6))
    f.append(text(180, 185, "hash(k₂) → N₂", size=10, color=INK, anchor="start"))

    f.append(arrow(233, 154, 266, 230, color=FIELD, sw=1.6))
    f.append(text(285, 185, "hash(k₃) → N₃", size=10, color=INK, anchor="start"))

    f.append(fitbox(20, 230, 95, 48, "Вузол 1\n(Memcached)", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(125, 230, 95, 48, "Вузол 2\n(Memcached)", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(230, 230, 95, 48, "Вузол 3\n(Memcached)", size=11, fill=GREEN_F, stroke=FIELD))

    f.append(fitbox(30, 310, 286, 170,
                    "Властивості:\n"
                    "• Вузли ізольовані (Shared-Nothing)\n"
                    "• Сервери не знають один про одного\n"
                    "• Нульовий додатковий мережевий хоп\n"
                    "• Топологія прошита в кожному клієнті\n"
                    "• Складність оновлення списку серверів",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    # 2. Проксі-маршрутизація (Twemproxy / Envoy / Mcrouter)
    f.append(text(520, 55, "2. Маршрутизація через Проксі", size=15, bold=True))
    f.append(text(520, 75, "Twemproxy / Envoy / Mcrouter", size=11, color=MUTED))

    f.append(fitbox(420, 100, 200, 44, "Застосунок (Простий клієнт)", size=12, bold=True, fill=BLUE_F, stroke=NEG))

    f.append(arrow(520, 144, 520, 180, color=NEG, sw=1.6))
    f.append(text(535, 162, "TCP", size=10, color=MUTED))

    f.append(fitbox(400, 180, 240, 50, "Проксі (Twemproxy / Envoy)\nПул з'єднань + Шардинг", size=11, bold=True, fill=WARN_F, stroke=POS))

    f.append(arrow(460, 230, 400, 280, color=FIELD, sw=1.6))
    f.append(arrow(520, 230, 520, 280, color=FIELD, sw=1.6))
    f.append(arrow(580, 230, 640, 280, color=FIELD, sw=1.6))

    f.append(fitbox(360, 280, 95, 48, "Шард 1\n(Redis/MC)", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(472, 280, 95, 48, "Шард 2\n(Redis/MC)", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(585, 280, 95, 48, "Шард 3\n(Redis/MC)", size=11, fill=GREEN_F, stroke=FIELD))

    f.append(fitbox(375, 360, 290, 120,
                    "Властивості:\n"
                    "• Клієнт бачить один ендпоінт\n"
                    "• Проксі тримає постійні пули з'єднань\n"
                    "• Додатковий мережевий хоп (+0.5..1 мс)\n"
                    "• Проксі є вузьким місцем CPU/пам'яті",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    # 3. Серверний кластер (Redis Cluster: 16384 слоти)
    f.append(text(866, 55, "3. Координований кластер", size=15, bold=True))
    f.append(text(866, 75, "Redis Cluster (Gossip + Слоти)", size=11, color=MUTED))

    f.append(fitbox(756, 100, 220, 44, "Застосунок (Cluster Client)", size=12, bold=True, fill=BLUE_F, stroke=NEG))

    f.append(arrow(820, 144, 770, 220, color=FIELD, sw=1.6))
    f.append(text(750, 180, "1. get(k)", size=10, color=FIELD))

    f.append(arrow(780, 220, 840, 144, color=POS, sw=1.4))
    f.append(text(860, 180, "2. -MOVED", size=10, color=POS, anchor="start"))

    f.append(arrow(910, 144, 950, 220, color=FIELD, sw=1.6))
    f.append(text(970, 180, "3. get(k)", size=10, color=FIELD))

    f.append(fitbox(710, 220, 100, 52, "Майстер A\n[0..5460]", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(820, 220, 100, 52, "Майстер B\n[5461..10922]", size=11, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(930, 220, 100, 52, "Майстер C\n[10923..16383]", size=11, fill=GREEN_F, stroke=FIELD))

    # Gossip зв'язки між майстрами
    f.append(line(810, 246, 820, 246, color=POS, sw=1.5))
    f.append(line(920, 246, 930, 246, color=POS, sw=1.5))

    f.append(fitbox(720, 310, 290, 170,
                    "Властивості:\n"
                    "• 16384 фіксовані хеш-слоти\n"
                    "• Gossip-протокол між вузлами (порт +10000)\n"
                    "• Клієнт кешує карту слотів у пам'яті\n"
                    "• При ребалансуванні: MOVED / ASK\n"
                    "• Вбудована реплікація та автофейловер",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "distributed-cache-topologies.svg"), W, H, *f)


# ── 2. slab-allocator-vs-heap: Архітектура Slab Allocator проти купи ───────────
def fig_slab_allocator():
    W, H = 1000, 480
    f = []

    # Ліворуч: Проблема загальної купи (malloc / free)
    f.append(text(240, 45, "Фрагментація загальної купи (malloc)", size=15, bold=True))
    f.append(text(240, 65, "Довільні розміри спричиняють дірки в пам'яті", size=11, color=MUTED))

    # Смуга пам'яті купи
    f.append(rect(40, 95, 400, 50, fill=GRAY_F, stroke=LINE))
    f.append(rect(45, 100, 60, 40, fill=GREEN_F, stroke=FIELD))
    f.append(text(75, 125, "120 B", size=10, bold=True))

    f.append(rect(110, 100, 40, 40, fill=RED_F, stroke=POS))
    f.append(text(130, 125, "FREE", size=9, color=POS))

    f.append(rect(155, 100, 90, 40, fill=GREEN_F, stroke=FIELD))
    f.append(text(200, 125, "1.5 KB", size=10, bold=True))

    f.append(rect(250, 100, 30, 40, fill=RED_F, stroke=POS))
    f.append(text(265, 125, "FREE", size=9, color=POS))

    f.append(rect(285, 100, 110, 40, fill=GREEN_F, stroke=FIELD))
    f.append(text(340, 125, "8 KB", size=10, bold=True))

    f.append(rect(400, 100, 35, 40, fill=RED_F, stroke=POS))
    f.append(text(417, 125, "FREE", size=9, color=POS))

    f.append(fitbox(40, 170, 400, 120,
                    "Наслідки фрагментації:\n"
                    "• Сумарно вільної пам'яті багато (40%), але\n"
                    "  немає суцільного блоку на 4 KB.\n"
                    "• Аллокатор відмовляє (OOM) або смикає mmap.\n"
                    "• Непередбачувані затримки при виділенні пам'яті.\n"
                    "• RSS процесу зростає, хоча даних мало.",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    # Розділювач
    f.append(line(480, 30, 480, 460, color=MUTED, sw=1, dash="4,4"))

    # Праворуч: Slab Allocator (Memcached)
    f.append(text(740, 45, "Slab Allocator (Memcached)", size=15, bold=True))
    f.append(text(740, 65, "Пам'ять розбита на класи зі сталим розміром чанків", size=11, color=MUTED))

    # Slab Class 1
    f.append(fitbox(510, 95, 450, 60,
                    "Slab Class 1 (Chunk size = 96 B, 1 MB Page = 10922 чанки)\n"
                    "[96B: KeyA][96B: KeyB][96B: Free][96B: KeyC][... 10918 чанків ...]",
                    size=10, fill=BLUE_F, stroke=NEG))

    # Slab Class 2
    f.append(fitbox(510, 165, 450, 60,
                    "Slab Class 2 (Chunk size = 120 B, множник росту factor=1.25)\n"
                    "[120B: Session1][120B: Session2][120B: Free][... 8738 чанків ...]",
                    size=10, fill=GREEN_F, stroke=FIELD))

    # Slab Class 3
    f.append(fitbox(510, 235, 450, 60,
                    "Slab Class N (Chunk size = 1 MB, 1 MB Page = 1 чанк)\n"
                    "[1 MB: Великий JSON / Граф користувача / HTML кеш]",
                    size=10, fill=WARN_F, stroke=POS))

    f.append(fitbox(510, 315, 450, 145,
                    "Переваги та компроміси Slab Allocation:\n"
                    "✓ Нульова зовнішня фрагментація (виділення за O(1))\n"
                    "✓ Незалежний LRU-список для кожного Slab-класу окремо\n"
                    "⚠ Внутрішня фрагментація: значення 97 B займає чанк 120 B (23 B відходу)\n"
                    "⚠ Закальцинування (Slab Calcification): якщо сторінки роздані\n"
                    "  класу 1, а трафік пішов у клас 2, клас 2 витісняє дані (evictions)!",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "slab-allocator-vs-heap.svg"), W, H, *f)


# ── 3. redis-event-loop-io: Модель подій та I/O потоки ────────────────────────
def fig_redis_event_loop():
    W, H = 1000, 480
    f = []

    f.append(text(500, 40, "Архітектура обробки запитів: Однопотокове ядро + Багатопотоковий I/O", size=16, bold=True))
    f.append(text(500, 62, "Чому кеш у пам'яті не потребує блокувань на структурах даних", size=12, color=MUTED))

    # Ліва частина: Мережа та I/O Threads
    f.append(fitbox(40, 100, 140, 50, "Клієнт 1\n(TCP Сокет)", size=11, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(40, 170, 140, 50, "Клієнт 2\n(TCP Сокет)", size=11, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(40, 240, 140, 50, "Клієнт N\n(TCP Сокет)", size=11, fill=BLUE_F, stroke=NEG))

    # Стрілки до I/O Threads
    f.append(arrow(180, 125, 250, 170, color=FIELD, sw=1.6))
    f.append(arrow(180, 195, 250, 195, color=FIELD, sw=1.6))
    f.append(arrow(180, 265, 250, 220, color=FIELD, sw=1.6))

    f.append(fitbox(250, 130, 200, 150,
                    "I/O Threads (Redis 6+)\n(epoll / kqueue)\n\n"
                    "• Зчитування байтів із сокета\n"
                    "• Парсинг протоколу RESP\n"
                    "• Формування черги команд\n"
                    "• Серіалізація відповідей",
                    size=11, pad=10, fill=WARN_F, stroke=POS))

    # Перехід до головного циклу
    f.append(arrow(450, 205, 530, 205, color=POS, sw=2.2))
    f.append(text(490, 190, "Команди", size=11, bold=True, color=POS))

    # Центр: Single-Threaded Event Loop Core
    f.append(fitbox(530, 100, 230, 210,
                    "Головний потік (Main Thread)\n"
                    "Event Loop (AeEvent)\n\n"
                    "1. Атомарне виконання:\n"
                    "   GET / SET / HINCRBY / ZADD\n"
                    "2. Порядок викликів гарантовано\n"
                    "3. Жодних Mutex / RWLock!\n"
                    "4. Модифікація RAM таблиць\n"
                    "5. Витіснення (LRU/LFU)",
                    size=11, pad=10, fill=GREEN_F, stroke=FIELD))

    # Праворуч: Структури в RAM
    f.append(arrow(760, 205, 830, 205, color=FIELD, sw=2.0))
    f.append(text(795, 190, "RAM", size=11, bold=True, color=FIELD))

    f.append(fitbox(830, 100, 140, 210,
                    "Структури даних\n\n"
                    "• Dict (Хеш-таблиці)\n"
                    "• Skiplist (ZSet)\n"
                    "• Quicklist (Lists)\n"
                    "• Intset / Radix Tree\n"
                    "• SDS (Рядки)",
                    size=11, pad=10, fill=GRAY_F, stroke=LINE))

    # Нижній блок пояснення
    f.append(fitbox(40, 340, 930, 120,
                    "Чому однопотокове ядро швидше за багатопотокове з блокуваннями:\n"
                    "1. Час операції над структурою в L1/L2 кеші процесора — 50–200 наносекунд.\n"
                    "2. Захоплення mutex/pthread_mutex з перемиканням контексту — 1000–5000 наносекунд (в 10-50 разів довше!).\n"
                    "3. Вузьке місце кешу — не обчислення, а системні виклики I/O ядра (read/write/epoll) та пропускна здатність мережі.\n"
                    "4. I/O-потоки паралелять мережу, а ядро лишається безблокувальним і детермінованим.",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "redis-event-loop-io.svg"), W, H, *f)


# ── 4. cache-cluster-failure-modes: Динаміка відмов та фейловеру ──────────────
def fig_failure_modes():
    W, H = 1000, 480
    f = []

    f.append(text(500, 40, "Динаміка відмов у розподіленому кластері", size=16, bold=True))
    f.append(text(500, 62, "Аварія майстра, деградація хітрейту та лавинний ефект бази даних", size=12, color=MUTED))

    # Блок 1: Нормальний стан
    f.append(fitbox(40, 95, 270, 230,
                    "Стан 1: Нормальна робота\n\n"
                    "• Майстер A: 100k req/s (Hit 99%)\n"
                    "• Асинхронна реплікація на Replica A\n"
                    "• База даних отримує лише 1% запитів\n"
                    "• Латентність читання p99 < 1 мс",
                    size=11, pad=10, fill=GREEN_F, stroke=FIELD))

    # Стрілка переходу
    f.append(arrow(310, 210, 360, 210, color=POS, sw=2.0))
    f.append(text(335, 195, "Аварія", size=10, color=POS, bold=True))

    # Блок 2: Аварія майстра і фейловер
    f.append(fitbox(360, 95, 280, 230,
                    "Стан 2: Фейловер (1-5 секунд)\n\n"
                    "• Майстер A падає (OOM / Kernel panic)\n"
                    "• Sentinel / Gossip фіксує таймаут\n"
                    "• Недорепліковані байти втрачаються\n"
                    "• Replica A промоутиться в Майстра\n"
                    "• Клієнти отримують Connection Refused",
                    size=11, pad=10, fill=WARN_F, stroke=POS))

    # Стрілка переходу
    f.append(arrow(640, 210, 690, 210, color=POS, sw=2.0))
    f.append(text(665, 195, "Наслідки", size=10, color=POS, bold=True))

    # Блок 3: Лавина на базу даних
    f.append(fitbox(690, 95, 270, 230,
                    "Стан 3: Лавина на первинне сховище\n\n"
                    "• Промахи кешу (Cache Misses) летять в SQL\n"
                    "• База даних отримує сплеск x50 запитів\n"
                    "• Пул з'єднань БД вичерпано (Pool Exhaustion)\n"
                    "• Латентність SQL зростає з 5 мс до 10 с\n"
                    "• Каскадне падіння застосунків!",
                    size=11, pad=10, fill=RED_F, stroke=POS))

    # Нижня панель захисту
    f.append(fitbox(40, 345, 920, 115,
                    "Архітектурні заходи запобігання каскадним збоям:\n"
                    "1. Захист від лавини (Request Coalescing / Singleflight): злиття сотень паралельних промахів в один SQL-запит.\n"
                    "2. Імовірнісна рання регенерація (XFetch): оновлення запису у фоні до закінчення його TTL.\n"
                    "3. Circuit Breaker: відсікання частини некритичних запитів у разі деградації кешу (Graceful Degradation).\n"
                    "4. Теплий старт (Cache Warming): прогрівання критичних ключів перед пуском бойового трафіку на новий шард.",
                    size=11, pad=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "cache-cluster-failure-modes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topologies()
    fig_slab_allocator()
    fig_redis_event_loop()
    fig_failure_modes()
    print("Всі 4 фігури згенеровано успішно.")
