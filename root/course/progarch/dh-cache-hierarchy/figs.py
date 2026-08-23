# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"
PURPLE_T= "#f3e8ff"

def fig_cache_hierarchy_overview():
    """Три яруси кеш-ієрархії DH: Клієнт -> L3 Edge CDN -> L1 Memory в API -> L2 Redis -> Origin DB."""
    W, H = 1060, 440
    f = []

    # Заголовок / Шар Клієнтів
    f.append(fitbox(45, 50, 180, 50, "Клієнти DH\n(Моб. застосунок / Панель)", size=13, bold=True, fill=NEUT, stroke=INK))

    # L3 Edge CDN
    f.append(fitbox(275, 50, 200, 70, "L3: Edge CDN\n(Cloudflare / Fastly)\n20–30 ms · HTTP Cache", size=13, bold=True, fill=BLUE_T, stroke=NEG))

    # L1 In-Memory API
    f.append(fitbox(525, 50, 200, 70, "L1: Внутрішня пам'ять API\n(Process Memory LRU)\n< 1 ms · No I/O", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    # L2 Redis Cluster
    f.append(fitbox(775, 50, 230, 70, "L2: Спільний Redis Cluster\n(Розподілений кеш)\n1–3 ms · Shared State", size=13, bold=True, fill=AMBER_T, stroke=AMBER))

    # Origin DB
    f.append(fitbox(525, 310, 480, 65, "Origin DB (PostgreSQL / ScyllaDB Cluster)\n50+ ms · Джерело правди (I/O & Disk Bottleneck)", size=13, bold=True, fill=RED_T, stroke=POS))

    # Стрілки прямого читання (Read Path)
    f.append(arrow(225, 75, 275, 75, color=INK, sw=2))
    f.append(text(250, 65, "100k r/s", size=11, color=MUTED, anchor="middle"))

    f.append(arrow(475, 75, 525, 75, color=INK, sw=2))
    f.append(text(500, 65, "Miss (10k)", size=11, color=MUTED, anchor="middle"))

    f.append(arrow(725, 75, 775, 75, color=INK, sw=2))
    f.append(text(750, 65, "Miss (2k)", size=11, color=MUTED, anchor="middle"))

    f.append(arrow(890, 120, 890, 310, color=POS, sw=2))
    f.append(text(900, 210, "Origin Fetch (100 r/s)", size=11, color=POS, anchor="start"))

    # Пункт інвалідації (Write / Purge Path)
    f.append(fitbox(45, 210, 390, 165, "Канал інвалідації при зміні стану:\n1. Запис у DB & L2 Redis\n2. Redis Pub/Sub → evict L1 memory\n3. Edge Purge API → evict L3 key", size=13, fill=PURPLE_T, stroke="#8b5cf6"))

    f.append(line(435, 292, 525, 342, color="#8b5cf6", sw=1.8, dash="5 4"))
    f.append(text(460, 305, "Write DB", size=11, color="#8b5cf6"))

    f.append(line(375, 210, 625, 120, color="#8b5cf6", sw=1.8, dash="5 4"))
    f.append(text(480, 180, "Pub/Sub Evict L1", size=11, color="#8b5cf6"))

    f.append(line(270, 210, 375, 120, color="#8b5cf6", sw=1.8, dash="5 4"))
    f.append(text(300, 180, "Edge Purge L3", size=11, color="#8b5cf6"))

    render(os.path.join(OUT, 'cache-hierarchy-overview.svg'), W, H, *f,
           title="Багатоярусна кеш-ієрархія стану розумних будинків DH")

def fig_cache_invalidation_fanout():
    """Послідовність інвалідації при оновленні стану пристрою."""
    W, H = 980, 400
    f = []

    f.append(fitbox(45, 45, 200, 60, "Давач / Пристрій\nPUT /devices/dev-42", size=13, bold=True, fill=NEUT, stroke=INK))

    f.append(fitbox(340, 45, 220, 60, "Сервіс стану DH\n(API Worker)", size=13, bold=True, fill=BG, stroke=INK))
    f.append(arrow(245, 75, 340, 75, color=INK, sw=2))

    # Запис у БД та Redis L2
    f.append(fitbox(700, 45, 235, 60, "Origin DB & L2 Redis\n(Запис нового стану)", size=13, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(560, 75, 700, 75, color=AMBER, sw=2))
    f.append(text(630, 65, "1. Write State", size=11, color=AMBER, anchor="middle"))

    # Pub/Sub Broadcast до всіх L1
    f.append(fitbox(340, 195, 220, 70, "Redis Pub/Sub Channel\ninvalidation:home-101", size=13, bold=True, fill=PURPLE_T, stroke="#8b5cf6"))
    f.append(arrow(450, 105, 450, 195, color="#8b5cf6", sw=2))
    f.append(text(460, 145, "2. Publish Evict", size=11, color="#8b5cf6", anchor="start"))

    # L1 Вузли Evict
    f.append(fitbox(45, 310, 240, 60, "L1 Memory (Вузол A)\n[Evicted key home-101]", size=12, fill=RED_T, stroke=POS))
    f.append(fitbox(330, 310, 240, 60, "L1 Memory (Вузол B)\n[Evicted key home-101]", size=12, fill=RED_T, stroke=POS))
    f.append(line(390, 265, 165, 310, color="#8b5cf6", sw=1.5, dash="4 3"))
    f.append(line(450, 265, 450, 310, color="#8b5cf6", sw=1.5, dash="4 3"))

    # Edge CDN Purge
    f.append(fitbox(700, 195, 235, 70, "Edge CDN Purge API\nSurrogate-Key: home-101", size=13, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(arrow(560, 230, 700, 230, color=NEG, sw=2))
    f.append(text(630, 220, "3. CDN Purge Call", size=11, color=NEG, anchor="middle"))

    f.append(fitbox(700, 310, 235, 60, "Edge CDN Cache\n[Purged surrogate tag]", size=12, fill=RED_T, stroke=POS))
    f.append(line(817, 265, 817, 310, color=NEG, sw=1.5, dash="4 3"))

    render(os.path.join(OUT, 'cache-invalidation-fanout.svg'), W, H, *f,
           title="Послідовність інвалідації стану крізь яруси при оновленні пристрою")

def fig_stampede_mitigation():
    """Захист від кеш-шторму (Cache Stampede): звичайний провал проти Singleflight / Mutex Coalescing."""
    W, H = 980, 390
    f = []

    # Верхня частина — Без Singleflight
    f.append(fitbox(45, 40, 210, 45, "500 одночасних запитів\n(Key Expiration)", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(255, 62, 380, 62, color=POS, sw=2))
    f.append(text(317, 52, "500 L1/L2 Misses", size=11, color=POS, anchor="middle"))

    f.append(fitbox(380, 40, 240, 45, "Прямий шторм на Origin DB\n(500 SQL-запитів)", size=12, bold=True, fill=RED_T, stroke=POS))
    f.append(arrow(620, 62, 740, 62, color=POS, sw=2))

    f.append(fitbox(740, 40, 195, 45, "Перевантаження DB\n(CPU 100% / Collapse)", size=12, bold=True, fill=RED_T, stroke=POS))

    # Розділювач
    f.append(line(45, 185, 935, 185, color=MUTED, sw=1.5, dash="6 5"))
    f.append(text(490, 175, "МЕХАНІЗМ ЗАХИСТУ (SINGLEFLIGHT / MUTEX COALESCING)", size=12, bold=True, color=MUTED, anchor="middle"))

    # Нижня частина — З Singleflight
    f.append(fitbox(45, 230, 210, 45, "500 одночасних запитів\n(Key Expiration)", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(255, 252, 380, 252, color=INK, sw=2))

    f.append(fitbox(380, 215, 240, 80, "Singleflight Mutex\n\n1-й запит -> іде в DB\n499 запитів -> чекають mutex", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(arrow(620, 235, 740, 235, color=FIELD, sw=2))
    f.append(text(680, 225, "1 Origin Fetch", size=11, color=FIELD, anchor="middle"))

    f.append(fitbox(740, 215, 195, 80, "Origin DB\n(1 SQL-запит)\n\nРезультат роздається усім 500", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'stampede-mitigation.svg'), W, H, *f,
           title="Захист від кеш-шторму за допомогою схлопування запитів (Singleflight)")

def fig_traffic_funnel_rates():
    """Воронка зрізання трафіку крізь яруси кешування (Hit-rate cascade)."""
    W, H = 960, 400
    f = []

    f.append(fitbox(45, 50, 260, 60, "Вхідний потік клієнтів\n100 000 запитів/сек", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(305, 80, 370, 80, color=INK, sw=2))

    # Ярус L3 Edge
    f.append(fitbox(370, 50, 250, 60, "L3: Edge CDN\nHit Rate = 90%", size=13, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(arrow(620, 80, 685, 80, color=NEG, sw=2))
    f.append(text(652, 70, "10 000 r/s", size=11, color=MUTED, anchor="middle"))

    # Ярус L1 Memory
    f.append(fitbox(685, 50, 230, 60, "L1: In-Memory API\nHit Rate = 80%", size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(800, 110, 800, 190, color=FIELD, sw=2))
    f.append(text(810, 150, "2 000 r/s", size=11, color=MUTED, anchor="start"))

    # Ярус L2 Redis
    f.append(fitbox(685, 190, 230, 60, "L2: Redis Cluster\nHit Rate = 95%", size=13, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(685, 220, 540, 220, color=AMBER, sw=2))
    f.append(text(612, 210, "100 r/s Miss", size=11, color=AMBER, anchor="middle"))

    # Origin DB
    f.append(fitbox(280, 190, 260, 60, "Origin DB (База даних)\n100 запитів/сек", size=14, bold=True, fill=RED_T, stroke=POS))

    # Підсумкова картка
    f.append(fitbox(45, 290, 870, 70, "Результат каскадного кешування:\n• Трафік до Origin DB зменшено у 1000 разів (з 100 000 r/s до 100 r/s)\n• Сукупний Hit-Rate (Overall Hit-Rate) = 99.9%\n• 90% запитів відповідають за 20 ms, 8% — за <1 ms, 1.9% — за 2 ms", size=13, bold=True, fill=PURPLE_T, stroke="#8b5cf6"))

    render(os.path.join(OUT, 'traffic-funnel-rates.svg'), W, H, *f,
           title="Воронка зрізання трафіку та підсумковий Hit-Rate крізь яруси")

if __name__ == '__main__':
    fig_cache_hierarchy_overview()
    fig_cache_invalidation_fanout()
    fig_stampede_mitigation()
    fig_traffic_funnel_rates()
    print("Figures generated successfully.")
