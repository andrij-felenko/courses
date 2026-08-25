# -*- coding: utf-8 -*-
"""Генератор схем для статті про database-sharding (шардинг баз даних)."""

import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_shard_architecture_topology():
    """Архітектурна топологія шардованої бази даних: клієнти, маршрутизатори, каталог та незалежні шарди."""
    w, h = 960, 520
    body = []

    # Заголовок
    body.append(text(w / 2, 28, "Архітектурна топологія шардованої СКБД (Shared-Nothing)", size=16, bold=True))

    # Рівень 1: Клієнти / Застосунки
    app1, _, _ = textbox(180, 80, "Застосунок A\n(Булкові замовлення)", size=12, pad=8, fill="#e8f4fd", stroke="#2457d6")
    app2, _, _ = textbox(450, 80, "Застосунок B\n(Користувацький API)", size=12, pad=8, fill="#e8f4fd", stroke="#2457d6")
    app3, _, _ = textbox(720, 80, "Застосунок C\n(Платіжний процесинг)", size=12, pad=8, fill="#e8f4fd", stroke="#2457d6")
    body.extend([app1, app2, app3])

    # Стрілки вниз до маршрутизаторів
    body.append(arrow(180, 110, 220, 160, color=LINE))
    body.append(arrow(450, 110, 390, 160, color=LINE))
    body.append(arrow(720, 110, 560, 160, color=LINE))

    # Рівень 2: Рівень маршрутизації (Router / Proxy Tier)
    proxy_box = rect(80, 165, 590, 95, fill="#fdfefe", stroke="#7f8c8d", sw=1.5, rx=8)
    proxy_lbl = text(375, 185, "Рівень маршрутизації (Stateless Routing Tier: Vitess / ProxySQL)", size=12, bold=True, color="#2c3e50")
    pr1, _, _ = textbox(180, 222, "Router 1\n(кеш мапи)", size=11, pad=6, fill="#f4f6f8")
    pr2, _, _ = textbox(375, 222, "Router 2\n(кеш мапи)", size=11, pad=6, fill="#f4f6f8")
    pr3, _, _ = textbox(570, 222, "Router 3\n(кеш мапи)", size=11, pad=6, fill="#f4f6f8")
    body.extend([proxy_box, proxy_lbl, pr1, pr2, pr3])

    # Каталог метаданих збоку
    cat_box, _, _ = textbox(815, 212, "Каталог метаданих\n(Shard Directory / etcd)\nВерсія топології: v14", size=11, pad=8, fill="#fef9e7", stroke="#f39c12")
    body.append(cat_box)
    body.append(arrow(720, 212, 672, 212, color="#f39c12"))

    # Стрілки до шардів
    body.append(arrow(180, 260, 130, 325, color=LINE))
    body.append(arrow(310, 260, 360, 325, color=LINE))
    body.append(arrow(440, 260, 590, 325, color=LINE))
    body.append(arrow(570, 260, 820, 325, color=LINE))

    # Рівень 3: Фізичні шарди (Shared-Nothing Clusters)
    shards_data = [
        ("Шард 0 (Shard-0)", "Діапазон: 0000..3FFF\nCPU: 64 core | RAM: 512GB\nDisk: 8TB NVMe (WAL-0)", 130, 385, "#eafaf1", "#27ae60"),
        ("Шард 1 (Shard-1)", "Діапазон: 4000..7FFF\nCPU: 64 core | RAM: 512GB\nDisk: 8TB NVMe (WAL-1)", 360, 385, "#eafaf1", "#27ae60"),
        ("Шард 2 (Shard-2)", "Діапазон: 8000..BFFF\nCPU: 64 core | RAM: 512GB\nDisk: 8TB NVMe (WAL-2)", 590, 385, "#eafaf1", "#27ae60"),
        ("Шард 3 (Shard-3)", "Діапазон: C000..FFFF\nCPU: 64 core | RAM: 512GB\nDisk: 8TB NVMe (WAL-3)", 820, 385, "#eafaf1", "#27ae60"),
    ]

    for title, desc, cx, cy, fill, stroke in shards_data:
        box = rect(cx - 100, cy - 55, 200, 140, fill=fill, stroke=stroke, sw=1.5, rx=8)
        head = text(cx, cy - 35, title, size=12, bold=True, color=stroke)
        desc_lines = desc.split("\n")
        info = mtext(cx, cy - 12, desc_lines, size=10, color=INK, lh=1.25)
        # Репліки всередині шарду
        rep_box = rect(cx - 90, cy + 32, 180, 42, fill="#ffffff", stroke="#95a5a6", sw=1, rx=4)
        rep_txt = text(cx, cy + 56, "Primary ⇄ Replica A, B (HA)", size=10, color="#7f8c8d")
        body.extend([box, head, info, rep_box, rep_txt])

    # Підпис внизу
    body.append(text(w / 2, 498, "Кожен шард є повністю автономною СКБД із власним пулом пам'яті, диском та чергою блокувань", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'shard-architecture-topology.svg'), w, h, *body)


def fig_sharding_strategies_comparison():
    """Порівняння чотирьох фундаментальних стратегій шардингу."""
    w, h = 920, 480
    body = []

    body.append(text(w / 2, 28, "Порівняльний аналіз стратегій розподілу даних між шардами", size=16, bold=True))

    strategies = [
        ("1. Діапазонний (Range-Based)",
         "Ключ: ID [1..100k], [100k..200k]\n"
         "• Ідеально для range-сканувань\n"
         "• Немає scatter-gather для відрізків\n"
         "✖ Перекіс: монотонні ключі\n"
         "  б'ють в останній шард (Hotspot)\n"
         "✖ Складний автоспліт меж",
         130, 240, "#fefde8", "#d4ac0d"),

        ("2. Хеш / Модуло (Hash / Modulo)",
         "Ключ: hash(ID) mod N\n"
         "• Рівномірне розсіювання даних\n"
         "• Відсутність точок перегріву\n"
         "✖ Зміна N (N → N+1) переміщує\n"
         "  (N-1)/N ключів (шторм міграції)\n"
         "✖ Range-запити йдуть на всі шарди",
         360, 240, "#fdeeed", "#c0392b"),

        ("3. Консистентне кільце (Ring)",
         "Ключ: Ring [0..2³²-1] + Vnodes\n"
         "• При додаванні шарду мігрує\n"
         "  лише 1/N ключів від сусідів\n"
         "• Vnodes згладжують дисперсію\n"
         "✖ Потребує алгоритму lookup\n"
         "✖ Range-запити фрагментовані",
         590, 240, "#eafaf1", "#27ae60"),

        ("4. Каталог / Lookup-таблиця",
         "Ключ → Shard_ID (Directory)\n"
         "• Абсолютна гнучкість мапінгу\n"
         "• Миттєве ізолювання VIP-клієнта\n"
         "• Легке динамічне дроблення\n"
         "✖ Каталог — критична точка\n"
         "✖ Накладні витрати на кешування",
         815, 240, "#ebf5fb", "#2980b9"),
    ]

    for title, content, cx, cy, fill, stroke in strategies:
        box = rect(cx - 105, cy - 165, 210, 335, fill=fill, stroke=stroke, sw=1.5, rx=8)
        head = text(cx, cy - 138, title, size=12, bold=True, color=stroke)
        lines = content.split("\n")
        txt = mtext(cx - 95, cy - 108, lines, size=11, color=INK, anchor="start", lh=1.4)
        body.extend([box, head, txt])

    body.append(text(w / 2, 445, "Вибір стратегії є компромісом між рівномірністю розсіювання записів та ціною range-запитів і ребалансування", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'sharding-strategies-comparison.svg'), w, h, *body)


def fig_live_resharding_lifecycle():
    """Конвеєр безпростойної міграції та розщеплення шарду (Live Resharding Lifecycle)."""
    w, h = 920, 420
    body = []

    body.append(text(w / 2, 28, "Фази безпростойного розщеплення шарду (Online Shard Splitting Pipeline)", size=16, bold=True))

    phases = [
        ("Фаза 1: Снапшот + CDC",
         "1. Фіксація точки у WAL/Binlog\n"
         "2. Фоновий бекфіл (Bulk Copy)\n"
         "3. Усі нові записи продовжують\n"
         "   іти на старий шард S_old\n"
         "4. CDC-потік починає буферизацію",
         130, 200, "#f4f6f8", "#7f8c8d"),

        ("Фаза 2: CDC Доганяння",
         "1. Стрімінг змін із WAL/Binlog\n"
         "2. Паралельне накочення на нові\n"
         "   шарди S_new1 та S_new2\n"
         "3. Лаг реплікації скорочується\n"
         "   з хвилин до < 50 мілісекунд",
         365, 200, "#e8f4fd", "#2457d6"),

        ("Фаза 3: Тіньова верифікація",
         "1. Порівняння хеш-сум рядків\n"
         "2. Тіньове дублювання читань\n"
         "3. Перевірка цілісності даних\n"
         "4. Підтвердження готовності\n"
         "   нових індексів та буферів",
         600, 200, "#fef9e7", "#f39c12"),

        ("Фаза 4: Атомний Cutover",
         "1. Захоплення лізи мапи (<5ms)\n"
         "2. Оновлення версії топології\n"
         "3. Роутери перемикають трафік\n"
         "4. S_old переходить у Read-Only\n"
         "5. Повне виведення S_old з дії",
         815, 200, "#eafaf1", "#27ae60"),
    ]

    for title, content, cx, cy, fill, stroke in phases:
        box = rect(cx - 100, cy - 130, 200, 260, fill=fill, stroke=stroke, sw=1.5, rx=8)
        head = text(cx, cy - 105, title, size=11, bold=True, color=stroke)
        lines = content.split("\n")
        txt = mtext(cx - 90, cy - 75, lines, size=11, color=INK, anchor="start", lh=1.35)
        body.extend([box, head, txt])

    # Стрілки між фазами
    body.append(arrow(232, 200, 262, 200, color=LINE, sw=2))
    body.append(arrow(467, 200, 497, 200, color=LINE, sw=2))
    body.append(arrow(702, 200, 712, 200, color=LINE, sw=2))

    body.append(text(w / 2, 385, "Атомне перемикання версії топології в каталозі гарантує нульовий час простою (Zero-Downtime) під час розщеплення", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'live-resharding-lifecycle.svg'), w, h, *body)


def fig_scatter_gather_latency_fanout():
    """Анатомія запиту Scatter-Gather: роздування затримки на повільному хвості (Tail Latency Amplification)."""
    w, h = 900, 460
    body = []

    body.append(text(w / 2, 28, "Анатомія Scatter-Gather запиту: бар'єр синхронізації та хвостова затримка", size=16, bold=True))

    # Клієнт
    client, _, _ = textbox(110, 215, "Клієнтський запит\n(Немає Shard Key)\nWHERE status='ACTIVE'", size=11, pad=8, fill="#e8f4fd", stroke="#2457d6")
    body.append(client)

    # Маршрутизатор (Coordinator)
    router, _, _ = textbox(310, 215, "Координатор / Proxy\nПаралельний Fan-Out (N=4)\nОчікування бар'єра", size=11, pad=8, fill="#fef9e7", stroke="#f39c12")
    body.append(router)

    body.append(arrow(185, 215, 220, 215, color=LINE))

    # Стрілки Fan-Out
    body.append(arrow(390, 190, 480, 100, color=LINE))
    body.append(arrow(400, 205, 480, 175, color=LINE))
    body.append(arrow(400, 225, 480, 255, color=LINE))
    body.append(arrow(390, 240, 480, 330, color=LINE))

    # Шарди та їхні затримки
    shards = [
        ("Шард 1", "Затримка: 4 ms", 580, 100, "#eafaf1", "#27ae60", 90),
        ("Шард 2", "Затримка: 7 ms", 580, 175, "#eafaf1", "#27ae60", 120),
        ("Шард 3 (Вузьке місце)", "Затримка: 185 ms (GC / Disk Queue Spike)", 650, 255, "#fdeeed", "#c0392b", 260),
        ("Шард 4", "Затримка: 6 ms", 580, 330, "#eafaf1", "#27ae60", 100),
    ]

    for title, desc, cx, cy, fill, stroke, box_w in shards:
        box = rect(cx - box_w / 2, cy - 25, box_w, 50, fill=fill, stroke=stroke, sw=1.5, rx=6)
        head = text(cx, cy - 7, title, size=11, bold=True, color=stroke)
        info = text(cx, cy + 12, desc, size=10, color=INK)
        body.extend([box, head, info])

    # Збір результатів назад
    body.append(line(630, 100, 770, 100, color=LINE, dash="4,4"))
    body.append(line(645, 175, 770, 175, color=LINE, dash="4,4"))
    body.append(line(785, 255, 770, 255, color=LINE, dash="4,4"))
    body.append(line(635, 330, 770, 330, color=LINE, dash="4,4"))

    body.append(line(770, 100, 770, 330, color=LINE, sw=2))

    # Бар'єрний блок
    barrier, _, _ = textbox(820, 215, "Бар'єр: T_total = max(T_i)\nЗагальний час = 185 ms\n+ Merge Sort / Limit", size=10, pad=6, fill="#fbeee6", stroke="#e67e22")
    body.append(barrier)

    body.append(text(w / 2, 420, "Загальний час виконання Scatter-Gather визначається найповільнішим шардом (p99 роздувається як 1 - (1-p)ⁿ)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'scatter-gather-latency-fanout.svg'), w, h, *body)


if __name__ == '__main__':
    fig_shard_architecture_topology()
    fig_sharding_strategies_comparison()
    fig_live_resharding_lifecycle()
    fig_scatter_gather_latency_fanout()
    print("All figures successfully generated.")
