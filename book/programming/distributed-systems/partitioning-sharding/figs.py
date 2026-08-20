# -*- coding: utf-8 -*-
"""Фігури теми «Шардинг та партиціонування в розподілених системах». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Палітра кольорів
C_BLUE_BG   = "#eaf2fd"
C_BLUE_BRD  = "#2457d6"
C_GREEN_BG  = "#e8f8f0"
C_GREEN_BRD = "#27ae60"
C_AMBER_BG  = "#fef9e7"
C_AMBER_BRD = "#d35400"
C_PURPLE_BG = "#f3e8fd"
C_PURPLE_BRD= "#8e44ad"
C_GRAY_BG   = "#f4f6f8"
C_GRAY_BRD  = "#6b7280"
C_RED_BG    = "#fdecea"
C_RED_BRD   = "#c0392b"


# ── 1. partitioning-vs-replication: ортогональність шардингу та реплікації ──
def fig_partitioning_vs_replication():
    W, H = 960, 480
    f = []

    # Заголовок
    f.append(text(W / 2, 35, "Ортогональність шардингу та реплікації в розподіленому кластері", size=16, bold=True))

    # Ліва панель: Вхідний масив даних, розрізаний на 3 партиції
    f.append(rect(40, 70, 220, 360, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1.5, rx=8))
    f.append(text(150, 98, "Загальний масив даних", size=14, bold=True, color=INK))
    f.append(text(150, 118, "(100% обсягу, 100% записів)", size=11, color=MUTED))

    # Слайси даних
    f.append(rect(55, 140, 190, 75, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=6))
    f.append(text(150, 168, "Партиція 0 (P0)", size=13, bold=True, color=C_BLUE_BRD))
    f.append(text(150, 192, "Ключі [0000..5555]", size=11, color=INK))

    f.append(rect(55, 230, 190, 75, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=6))
    f.append(text(150, 258, "Партиція 1 (P1)", size=13, bold=True, color=C_GREEN_BRD))
    f.append(text(150, 282, "Ключі [5556..AAAA]", size=11, color=INK))

    f.append(rect(55, 320, 190, 75, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1.5, rx=6))
    f.append(text(150, 348, "Партиція 2 (P2)", size=13, bold=True, color=C_AMBER_BRD))
    f.append(text(150, 372, "Ключі [AAAB..FFFF]", size=11, color=INK))

    # Стрілка шардингу
    f.append(arrow(270, 250, 325, 250, color=LINE, sw=2))
    f.append(text(298, 235, "Шардинг", size=12, bold=True, color=LINE))
    f.append(text(298, 270, "(Масштабування)", size=10, color=MUTED))

    # Права частина: 3 фізичні сервери кластера
    node_x = [340, 545, 750]
    node_w = 175
    node_titles = ["Вузол А (Node 1)", "Вузол Б (Node 2)", "Вузол В (Node 3)"]

    for i in range(3):
        nx = node_x[i]
        f.append(rect(nx, 70, node_w, 360, fill=BG, stroke=LINE, sw=1.5, rx=8))
        f.append(rect(nx, 70, node_w, 40, fill=C_GRAY_BG, stroke=LINE, sw=1.5, rx=8))
        f.append(text(nx + node_w / 2, 95, node_titles[i], size=13, bold=True, color=INK))

    # Розподіл партицій та реплік по вузлах (Leader / Follower)
    # Вузол 1: P0 (Лідер), P1 (Фоловер), P2 (Фоловер)
    f.append(rect(352, 130, 151, 80, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=2, rx=6))
    f.append(text(427, 158, "P0 — Лідер", size=13, bold=True, color=C_BLUE_BRD))
    f.append(text(427, 184, "Приймає записи P0", size=11, color=INK))

    f.append(rect(352, 225, 151, 80, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=6))
    f.append(text(427, 253, "P1 — Фоловер", size=12, color=C_GREEN_BRD))
    f.append(text(427, 279, "Репліка для читання", size=10, color=MUTED))

    f.append(rect(352, 320, 151, 80, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1, rx=6))
    f.append(text(427, 348, "P2 — Фоловер", size=12, color=C_AMBER_BRD))
    f.append(text(427, 374, "Репліка для читання", size=10, color=MUTED))

    # Вузол 2: P0 (Фоловер), P1 (Лідер), P2 (Фоловер)
    f.append(rect(557, 130, 151, 80, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=6))
    f.append(text(632, 158, "P0 — Фоловер", size=12, color=C_BLUE_BRD))
    f.append(text(632, 184, "Репліка для читання", size=10, color=MUTED))

    f.append(rect(557, 225, 151, 80, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=2, rx=6))
    f.append(text(632, 253, "P1 — Лідер", size=13, bold=True, color=C_GREEN_BRD))
    f.append(text(632, 279, "Приймає записи P1", size=11, color=INK))

    f.append(rect(557, 320, 151, 80, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1, rx=6))
    f.append(text(632, 348, "P2 — Фоловер", size=12, color=C_AMBER_BRD))
    f.append(text(632, 374, "Репліка для читання", size=10, color=MUTED))

    # Вузол 3: P0 (Фоловер), P1 (Фоловер), P2 (Лідер)
    f.append(rect(762, 130, 151, 80, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=6))
    f.append(text(837, 158, "P0 — Фоловер", size=12, color=C_BLUE_BRD))
    f.append(text(837, 184, "Репліка для читання", size=10, color=MUTED))

    f.append(rect(762, 225, 151, 80, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=6))
    f.append(text(837, 253, "P1 — Фоловер", size=12, color=C_GREEN_BRD))
    f.append(text(837, 279, "Репліка для читання", size=10, color=MUTED))

    f.append(rect(762, 320, 151, 80, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=2, rx=6))
    f.append(text(837, 348, "P2 — Лідер", size=13, bold=True, color=C_AMBER_BRD))
    f.append(text(837, 374, "Приймає записи P2", size=11, color=INK))

    # Підвал / висновок
    f.append(rect(40, 440, 885, 30, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=4))
    f.append(text(482, 460, "Шардинг ділить простір даних для паралельного запису; реплікація дублює кожен шард для відмовостійкості", size=11, bold=True, color=INK))

    render(out("partitioning-vs-replication.svg"), W, H, *f)


# ── 2. partitioning-strategies: стратегії партиціонування ────────────────────
def fig_partitioning_strategies():
    W, H = 960, 470
    f = []

    # Заголовок
    f.append(text(W / 2, 30, "Порівняння трьох фундаментальних стратегій партиціонування", size=16, bold=True))

    col_w = 280
    cols_x = [40, 340, 640]
    titles = [
        ("1. За діапазонами ключів (Range)", C_BLUE_BG, C_BLUE_BRD),
        ("2. За хешем ключа (Hash)", C_GREEN_BG, C_GREEN_BRD),
        ("3. Складений ключ (Compound)", C_PURPLE_BG, C_PURPLE_BRD)
    ]

    for i, (title, bg, brd) in enumerate(titles):
        cx = cols_x[i]
        f.append(rect(cx, 55, col_w, 395, fill=BG, stroke=brd, sw=1.5, rx=8))
        f.append(rect(cx, 55, col_w, 40, fill=bg, stroke=brd, sw=1.5, rx=8))
        f.append(text(cx + col_w / 2, 80, title, size=13, bold=True, color=brd))

    # Стовпець 1: Range Partitioning
    f.append(rect(55, 108, 250, 70, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=5))
    f.append(text(180, 130, "Впорядковані діапазони:", size=11, bold=True, color=INK))
    f.append(text(180, 148, "Шард 1: [A .. K]", size=11, color=INK))
    f.append(text(180, 166, "Шард 2: [L .. Z]", size=11, color=INK))

    f.append(rect(55, 190, 250, 95, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=5))
    f.append(text(180, 212, "✓ Переваги:", size=12, bold=True, color=C_GREEN_BRD))
    f.append(text(180, 234, "• Ідеально для діапазонних вибірок", size=11, color=INK))
    f.append(text(180, 254, "• SCAN(key >= 'A' AND key <= 'C')", size=10, color=LINE))
    f.append(text(180, 274, "• Локальність у межах одного вузла", size=11, color=INK))

    f.append(rect(55, 298, 250, 95, fill=C_RED_BG, stroke=C_RED_BRD, sw=1, rx=5))
    f.append(text(180, 320, "✗ Ризики та вади:", size=12, bold=True, color=C_RED_BRD))
    f.append(text(180, 342, "• Гарячі точки (Hotspots)", size=11, color=INK))
    f.append(text(180, 362, "• Послідовні ключі (auto-inc, час)", size=11, color=INK))
    f.append(text(180, 382, "перевантажують останній шард", size=10, color=MUTED))

    f.append(text(180, 420, "Приклади: HBase, CockroachDB, Spanner", size=10, italic=True, color=MUTED))

    # Стовпець 2: Hash Partitioning
    f.append(rect(355, 108, 250, 70, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=5))
    f.append(text(480, 130, "Розсіювання через хеш:", size=11, bold=True, color=INK))
    f.append(text(480, 148, "shard = Murmur3(key) % N", size=11, color=INK))
    f.append(text(480, 166, "або токени на кільці хешів", size=11, color=MUTED))

    f.append(rect(355, 190, 250, 95, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=5))
    f.append(text(480, 212, "✓ Переваги:", size=12, bold=True, color=C_GREEN_BRD))
    f.append(text(480, 234, "• Рівномірний розподіл записів", size=11, color=INK))
    f.append(text(480, 254, "• Руйнує монотонні черги запису", size=11, color=INK))
    f.append(text(480, 274, "• Немає перекосів за часом", size=11, color=INK))

    f.append(rect(355, 298, 250, 95, fill=C_RED_BG, stroke=C_RED_BRD, sw=1, rx=5))
    f.append(text(480, 320, "✗ Ризики та вади:", size=12, bold=True, color=C_RED_BRD))
    f.append(text(480, 342, "• Діапазонні запити неможливі", size=11, color=INK))
    f.append(text(480, 362, "• SCAN вимагає Scatter-Gather", size=11, color=INK))
    f.append(text(480, 382, "опитування всіх вузлів кластера", size=10, color=MUTED))

    f.append(text(480, 420, "Приклади: DynamoDB, Redis Cluster, Riak", size=10, italic=True, color=MUTED))

    # Стовпець 3: Compound Key
    f.append(rect(655, 108, 250, 70, fill=C_PURPLE_BG, stroke=C_PURPLE_BRD, sw=1, rx=5))
    f.append(text(780, 130, "Дворівневий ключ:", size=11, bold=True, color=INK))
    f.append(text(780, 148, "((Partition_Key), Cluster_Key)", size=11, color=INK))
    f.append(text(780, 166, "Хеш для вузла + сортування всередині", size=10, color=MUTED))

    f.append(rect(655, 190, 250, 95, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=5))
    f.append(text(780, 212, "✓ Переваги:", size=12, bold=True, color=C_GREEN_BRD))
    f.append(text(780, 234, "• Хеш партиції розсіює сутності", size=11, color=INK))
    f.append(text(780, 254, "• Кластерний ключ дає швидкий SCAN", size=11, color=INK))
    f.append(text(780, 274, "для конкретного user_id", size=11, color=INK))

    f.append(rect(655, 298, 250, 95, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1, rx=5))
    f.append(text(780, 320, "⚠ Обмеження:", size=12, bold=True, color=C_AMBER_BRD))
    f.append(text(780, 342, "• Діапазон лише в межах партиції", size=11, color=INK))
    f.append(text(780, 362, "• Запит між різними user_id", size=11, color=INK))
    f.append(text(780, 382, "все одно є віяловим (Scatter-Gather)", size=10, color=MUTED))

    f.append(text(780, 420, "Приклади: Apache Cassandra, ScyllaDB", size=10, italic=True, color=MUTED))

    render(out("partitioning-strategies.svg"), W, H, *f)


# ── 3. secondary-indexes-partitioned: локальні та глобальні індекси ───────────
def fig_secondary_indexes():
    W, H = 960, 460
    f = []

    # Заголовок
    f.append(text(W / 2, 30, "Вторинні індекси в шардованих системах: локальні проти глобальних", size=16, bold=True))

    # Ліва половина: Локальний вторинний індекс (Document-partitioned)
    f.append(rect(40, 60, 425, 380, fill=BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(rect(40, 60, 425, 40, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(text(252, 85, "А. Локальний індекс (Document-Partitioned)", size=13, bold=True, color=C_BLUE_BRD))

    # Шард 1 і Шард 2
    f.append(rect(60, 115, 385, 85, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(140, 138, "Шард 1 (Ключі 1..500)", size=12, bold=True, color=INK))
    f.append(rect(75, 148, 170, 42, fill=BG, stroke=LINE, sw=1, rx=4))
    f.append(text(160, 172, "Дані: [ID:1, Color:Red]", size=11, color=INK))
    f.append(rect(260, 148, 170, 42, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=4))
    f.append(text(345, 172, "Індекс: Red -> [ID:1]", size=11, bold=True, color=C_BLUE_BRD))

    f.append(rect(60, 210, 385, 85, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(140, 233, "Шард 2 (Ключі 501..1000)", size=12, bold=True, color=INK))
    f.append(rect(75, 243, 170, 42, fill=BG, stroke=LINE, sw=1, rx=4))
    f.append(text(160, 267, "Дані: [ID:700, Color:Red]", size=11, color=INK))
    f.append(rect(260, 243, 170, 42, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=4))
    f.append(text(345, 267, "Індекс: Red -> [ID:700]", size=11, bold=True, color=C_BLUE_BRD))

    # Характеристики локального індексу
    f.append(rect(60, 305, 385, 120, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(252, 328, "Властивості локального індексу:", size=12, bold=True, color=INK))
    f.append(text(252, 350, "• Запис: швидкий і локальний (1 шард)", size=11, color=C_GREEN_BRD))
    f.append(text(252, 372, "• Читання: Scatter-Gather (опитування ВСІХ шардів)", size=11, color=C_RED_BRD))
    f.append(text(252, 394, "• P99 затримка експоненційно деградує з ростом N", size=11, color=INK))
    f.append(text(252, 412, "Приклад: Elasticsearch, MongoDB (за замовчуванням)", size=10, italic=True, color=MUTED))

    # Права половина: Глобальний вторинний індекс (Term-partitioned)
    f.append(rect(495, 60, 425, 380, fill=BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(rect(495, 60, 425, 40, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(text(707, 85, "Б. Глобальний індекс (Term-Partitioned)", size=13, bold=True, color=C_GREEN_BRD))

    # Шард даних та Шард індексу
    f.append(rect(515, 115, 385, 85, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(600, 138, "Вузол 1 (Шард даних)", size=12, bold=True, color=INK))
    f.append(rect(530, 148, 355, 42, fill=BG, stroke=LINE, sw=1, rx=4))
    f.append(text(707, 172, "Зберігає рядки: [ID:1, Red], [ID:2, Blue]", size=11, color=INK))

    f.append(rect(515, 210, 385, 85, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1, rx=6))
    f.append(text(630, 233, "Вузол 2 (Шард глобального індексу)", size=12, bold=True, color=C_GREEN_BRD))
    f.append(rect(530, 243, 355, 42, fill=BG, stroke=C_GREEN_BRD, sw=1, rx=4))
    f.append(text(707, 267, "Індекс термів [A..M]: Color:Blue -> [ID:2]", size=11, bold=True, color=C_GREEN_BRD))

    # Характеристики глобального індексу
    f.append(rect(515, 305, 385, 120, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(707, 328, "Властивості глобального індексу:", size=12, bold=True, color=INK))
    f.append(text(707, 350, "• Читання: точкове й швидке (1 цільовий шард індексу)", size=11, color=C_GREEN_BRD))
    f.append(text(707, 372, "• Запис: розподілена транзакція (2PC) або асинхронний лаг", size=11, color=C_RED_BRD))
    f.append(text(707, 394, "• Складність підтримки цілісності при збоях", size=11, color=INK))
    f.append(text(707, 412, "Приклад: DynamoDB Global Secondary Index (GSI)", size=10, italic=True, color=MUTED))

    render(out("secondary-indexes-partitioned.svg"), W, H, *f)


# ── 4. request-routing-architectures: моделі маршрутизації ───────────────────
def fig_request_routing():
    W, H = 960, 440
    f = []

    # Заголовок
    f.append(text(W / 2, 30, "Три архітектурні моделі маршрутизації запитів до партицій", size=16, bold=True))

    col_w = 280
    cols_x = [40, 340, 640]
    models = [
        ("1. Розумний клієнт (Smart Client)", C_BLUE_BG, C_BLUE_BRD),
        ("2. Маршрутний проксі (Proxy Tier)", C_AMBER_BG, C_AMBER_BRD),
        ("3. Рівноправна P2P координація", C_GREEN_BG, C_GREEN_BRD)
    ]

    for i, (title, bg, brd) in enumerate(models):
        cx = cols_x[i]
        f.append(rect(cx, 55, col_w, 365, fill=BG, stroke=brd, sw=1.5, rx=8))
        f.append(rect(cx, 55, col_w, 40, fill=bg, stroke=brd, sw=1.5, rx=8))
        f.append(text(cx + col_w / 2, 80, title, size=12, bold=True, color=brd))

    # Стовпець 1: Smart Client
    f.append(rect(60, 110, 240, 50, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=6))
    f.append(text(180, 130, "Клієнтський застосунок", size=11, bold=True, color=C_BLUE_BRD))
    f.append(text(180, 148, "Кеш топології партицій у RAM", size=10, color=INK))

    f.append(arrow(180, 160, 180, 205, color=C_BLUE_BRD, sw=1.5))
    f.append(text(225, 185, "Прямий TCP", size=10, color=MUTED))

    f.append(rect(60, 210, 240, 70, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(180, 235, "Цільовий вузол (Шард 3)", size=12, bold=True, color=INK))
    f.append(text(180, 258, "Обробляє запит без посередників", size=10, color=MUTED))

    f.append(rect(60, 295, 240, 110, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=5))
    f.append(text(180, 315, "Особливості моделі:", size=11, bold=True, color=INK))
    f.append(text(180, 335, "✓ Мінімальна латентність (0 hop)", size=10, color=C_GREEN_BRD))
    f.append(text(180, 355, "✗ Товстий клієнт (fat SDK)", size=10, color=C_RED_BRD))
    f.append(text(180, 375, "✗ Шторм з'єднань при N клієнтах", size=10, color=C_RED_BRD))
    f.append(text(180, 395, "Приклади: Kafka Producer, MongoDB Driver", size=9, italic=True, color=MUTED))

    # Стовпець 2: Proxy Router
    f.append(rect(360, 110, 240, 45, fill=BG, stroke=LINE, sw=1, rx=6))
    f.append(text(480, 135, "Тонкий клієнт (REST / SQL)", size=11, bold=True, color=INK))

    f.append(arrow(480, 155, 480, 185, color=LINE, sw=1.5))

    f.append(rect(360, 185, 240, 50, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1.5, rx=6))
    f.append(text(480, 205, "Шар маршрутизації (Proxy)", size=11, bold=True, color=C_AMBER_BRD))
    f.append(text(480, 223, "Пул з'єднань, парсинг SQL, Scatter", size=10, color=INK))

    f.append(arrow(480, 235, 480, 265, color=C_AMBER_BRD, sw=1.5))

    f.append(rect(360, 265, 240, 45, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(480, 290, "Кластер сховищ (Шарди 1..N)", size=11, bold=True, color=INK))

    f.append(rect(360, 320, 240, 85, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=5))
    f.append(text(480, 338, "Особливості моделі:", size=11, bold=True, color=INK))
    f.append(text(480, 356, "✓ Простий клієнт, пулінг з'єднань", size=10, color=C_GREEN_BRD))
    f.append(text(480, 374, "✗ Додатковий мережевий стрибок (+1 hop)", size=10, color=C_RED_BRD))
    f.append(text(480, 394, "Приклади: Vitess VTGate, Twemproxy", size=9, italic=True, color=MUTED))

    # Стовпець 3: Peer-to-Peer Routing
    f.append(rect(660, 110, 240, 45, fill=BG, stroke=LINE, sw=1, rx=6))
    f.append(text(780, 135, "Клієнт звертається до БУДЬ-ЯКОГО вузла", size=10, bold=True, color=INK))

    f.append(arrow(780, 155, 780, 185, color=LINE, sw=1.5))

    f.append(rect(660, 185, 240, 50, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=6))
    f.append(text(780, 205, "Вузол-координатор (Node 1)", size=11, bold=True, color=C_GREEN_BRD))
    f.append(text(780, 223, "Пересилає запит через Gossip-мапу", size=10, color=INK))

    f.append(arrow(780, 235, 780, 265, color=C_GREEN_BRD, sw=1.5))

    f.append(rect(660, 265, 240, 45, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(780, 290, "Вузол-власник партиції (Node 4)", size=11, bold=True, color=INK))

    f.append(rect(660, 320, 240, 85, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=5))
    f.append(text(780, 338, "Особливості моделі:", size=11, bold=True, color=INK))
    f.append(text(780, 356, "✓ Симетрична архітектура без SPOF", size=10, color=C_GREEN_BRD))
    f.append(text(780, 374, "✗ Внутрішній проксі-трафік між вузлами", size=10, color=C_AMBER_BRD))
    f.append(text(780, 394, "Приклади: Apache Cassandra, Amazon Dynamo", size=9, italic=True, color=MUTED))

    render(out("request-routing-architectures.svg"), W, H, *f)


# ── 5. dynamic-split-and-rebalance: стратегії ребалансування ──────────────────
def fig_dynamic_split_and_rebalance():
    W, H = 960, 450
    f = []

    # Заголовок
    f.append(text(W / 2, 30, "Механізми ребалансування: фіксовані слоти проти динамічного спліту", size=16, bold=True))

    # Ліва половина: Фіксована кількість партицій (Static Partition Slots)
    f.append(rect(40, 55, 425, 375, fill=BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(rect(40, 55, 425, 40, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(text(252, 80, "А. Фіксовані слоти (Static Partitions)", size=13, bold=True, color=C_BLUE_BRD))

    # Стан 1: 2 вузли ділять 1024 слоти
    f.append(text(252, 118, "Стан 1: 2 вузли ділять 1024 фіксовані партиції", size=11, bold=True, color=INK))
    f.append(rect(60, 130, 185, 60, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=5))
    f.append(text(152, 155, "Вузол 1", size=12, bold=True, color=C_BLUE_BRD))
    f.append(text(152, 175, "Слоти 0 .. 511 (512 шт)", size=11, color=INK))

    f.append(rect(260, 130, 185, 60, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=5))
    f.append(text(352, 155, "Вузол 2", size=12, bold=True, color=C_BLUE_BRD))
    f.append(text(352, 175, "Слоти 512 .. 1023 (512 шт)", size=11, color=INK))

    # Стрілка додавання вузла 3
    f.append(arrow(252, 198, 252, 228, color=LINE, sw=1.5))
    f.append(text(335, 218, "+ Додано Вузол 3", size=10, bold=True, color=C_GREEN_BRD))

    # Стан 2: 3 вузли після передачі слотів
    f.append(text(252, 245, "Стан 2: Цілі слоти переїжджають без рехешування ключів", size=11, bold=True, color=INK))
    f.append(rect(55, 260, 120, 60, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=4))
    f.append(text(115, 285, "Вузол 1", size=11, bold=True, color=C_BLUE_BRD))
    f.append(text(115, 305, "341 слот", size=10, color=INK))

    f.append(rect(190, 260, 120, 60, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=4))
    f.append(text(250, 285, "Вузол 2", size=11, bold=True, color=C_BLUE_BRD))
    f.append(text(250, 305, "341 слот", size=10, color=INK))

    f.append(rect(325, 260, 120, 60, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=4))
    f.append(text(385, 285, "Вузол 3 (Новий)", size=11, bold=True, color=C_GREEN_BRD))
    f.append(text(385, 305, "342 слоти", size=10, color=C_GREEN_BRD))

    f.append(rect(55, 335, 395, 80, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=5))
    f.append(text(252, 355, "Переваги фіксованих слотів:", size=11, bold=True, color=INK))
    f.append(text(252, 375, "• Кількість слотів незмінна (наприклад, 16 384 у Redis)", size=10, color=INK))
    f.append(text(252, 395, "• Переміщуються готові директорії даних", size=10, color=INK))

    # Права половина: Динамічний поділ діапазонів (Dynamic Range Split)
    f.append(rect(495, 55, 425, 375, fill=BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(rect(495, 55, 425, 40, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(text(707, 80, "Б. Динамічний поділ (Dynamic Range Split)", size=13, bold=True, color=C_GREEN_BRD))

    # Стан 1: Шард переповнюється
    f.append(text(707, 118, "Стан 1: Діапазон [A .. M] переростає ліміт 64 MB", size=11, bold=True, color=INK))
    f.append(rect(535, 130, 345, 60, fill=C_RED_BG, stroke=C_RED_BRD, sw=1.5, rx=5))
    f.append(text(707, 155, "Партиція 1: [A .. M] — 98 MB (Переповнення!)", size=12, bold=True, color=C_RED_BRD))
    f.append(text(707, 175, "Вузол 1 автоматично знаходить медіанний ключ 'G'", size=10, color=INK))

    # Стрілка спліту
    f.append(arrow(707, 198, 707, 228, color=LINE, sw=1.5))
    f.append(text(795, 218, "Автоматичний Split", size=10, bold=True, color=C_AMBER_BRD))

    # Стан 2: Дві нові дочірні партиції
    f.append(text(707, 245, "Стан 2: Розщеплення на дві рівні партиції по 49 MB", size=11, bold=True, color=INK))
    f.append(rect(515, 260, 180, 60, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1, rx=4))
    f.append(text(605, 285, "Партиція 1a: [A .. G)", size=11, bold=True, color=C_BLUE_BRD))
    f.append(text(605, 305, "Лишається на Вузлі 1", size=10, color=MUTED))

    f.append(rect(720, 260, 180, 60, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=4))
    f.append(text(810, 285, "Партиція 1b: [G .. M]", size=11, bold=True, color=C_GREEN_BRD))
    f.append(text(810, 305, "Мігрує на Вузол 2", size=10, color=C_GREEN_BRD))

    f.append(rect(515, 335, 385, 80, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1, rx=5))
    f.append(text(707, 355, "Переваги динамічного спліту:", size=11, bold=True, color=INK))
    f.append(text(707, 375, "• Розмір кожної партиції завжди під контролем", size=10, color=INK))
    f.append(text(707, 395, "• При зменшенні даних сусідні партиції зливаються (Merge)", size=10, color=INK))

    render(out("dynamic-split-and-rebalance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_partitioning_vs_replication()
    fig_partitioning_strategies()
    fig_secondary_indexes()
    fig_request_routing()
    fig_dynamic_split_and_rebalance()
    print("Усі фігури успішно згенеровано.")
