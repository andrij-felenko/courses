# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми CDN та Edge Computing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_anycast_routing():
    """Фігура 1: Anycast-маршрутизація до найближчого Edge PoP проти централізованого Unicast."""
    W, H = 960, 480
    p = []
    
    # ── Ліва панель: Централізований Unicast (довге плече RTT) ──
    px1, py1, pw1, ph1 = 20.0, 50.0, 445.0, 405.0
    p.append(rect(px1, py1, pw1, ph1, fill="#fdfaf6", stroke="#e8c49e", sw=1.3, rx=8))
    p.append(text(px1 + pw1 / 2, py1 + 24, "Традиційний Unicast (єдиний центральний сервер)", size=13, color=POS, bold=True))
    
    # Центральний сервер у Франкфурті
    ox = px1 + pw1 / 2
    oy = py1 + 80
    p.append(rect(ox - 110, oy, 220, 55, fill="#feebe8", stroke=POS, sw=1.5, rx=6))
    p.append(text(ox, oy + 22, "Центральний сервер (Origin)", size=12, color=INK, bold=True))
    p.append(text(ox, oy + 42, "IP: 198.51.100.10 (Франкфурт)", size=10.5, color=MUTED))
    
    # Клієнти Unicast
    c_y1 = py1 + 195
    c_y2 = py1 + 280
    c_y3 = py1 + 355
    
    # Клієнт 1: Сідней
    p.append(rect(px1 + 20, c_y1, 145, 45, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px1 + 92, c_y1 + 18, "Клієнт (Сідней)", size=11, color=INK, bold=True))
    p.append(text(px1 + 92, c_y1 + 34, "RTT: 280–320 мс", size=9.5, color=POS))
    p.append(arrow(px1 + 165, c_y1 + 22, ox - 110, oy + 38, color=POS, sw=1.4))
    
    # Клієнт 2: Сан-Паулу
    p.append(rect(px1 + 20, c_y2, 145, 45, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px1 + 92, c_y2 + 18, "Клієнт (Сан-Паулу)", size=11, color=INK, bold=True))
    p.append(text(px1 + 92, c_y2 + 34, "RTT: 210–250 мс", size=9.5, color=POS))
    p.append(arrow(px1 + 165, c_y2 + 22, ox - 60, oy + 55, color=POS, sw=1.4))
    
    # Клієнт 3: Токіо
    p.append(rect(px1 + 20, c_y3, 145, 45, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px1 + 92, c_y3 + 18, "Клієнт (Токіо)", size=11, color=INK, bold=True))
    p.append(text(px1 + 92, c_y3 + 34, "RTT: 240–270 мс", size=9.5, color=POS))
    p.append(arrow(px1 + 165, c_y3 + 22, ox, oy + 55, color=POS, sw=1.4))
    
    p.append(text(px1 + pw1 / 2, py1 + 245, "TCP + TLS рукостискання", size=10, color=POS, italic=True))
    p.append(text(px1 + pw1 / 2, py1 + 262, "через увесь світ (3–4 RTT)", size=10, color=POS, italic=True))

    # ── Права панель: Anycast BGP + Edge PoP (коротке плече) ──
    px2, py2, pw2, ph2 = 490.0, 50.0, 450.0, 405.0
    p.append(rect(px2, py2, pw2, ph2, fill="#f4faf6", stroke="#a3d9b8", sw=1.3, rx=8))
    p.append(text(px2 + pw2 / 2, py2 + 24, "Anycast BGP + Розподілені Edge PoP", size=13, color=FIELD, bold=True))
    
    # Спільний Anycast IP
    p.append(rect(px2 + pw2 / 2 - 130, py2 + 45, 260, 32, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(px2 + pw2 / 2, py2 + 65, "Єдина адреса Anycast IP: 192.0.2.1", size=11, color=FIELD, bold=True))
    
    # 3 PoP вузли
    pop_y1 = py2 + 105
    pop_y2 = py2 + 205
    pop_y3 = py2 + 305
    
    # PoP 1: Сідней
    p.append(rect(px2 + 20, pop_y1, 120, 50, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px2 + 80, pop_y1 + 20, "Клієнт (Сідней)", size=10.5, color=INK, bold=True))
    p.append(text(px2 + 80, pop_y1 + 38, "Локальний BGP", size=9.5, color=MUTED))
    
    p.append(arrow(px2 + 140, pop_y1 + 25, px2 + 230, pop_y1 + 25, color=FIELD, sw=1.5))
    p.append(rect(px2 + 230, pop_y1 - 5, 195, 60, fill="#e8f4fd", stroke=NEG, sw=1.2, rx=5))
    p.append(text(px2 + 327, pop_y1 + 18, "Edge PoP (Сідней)", size=11, color=INK, bold=True))
    p.append(text(px2 + 327, pop_y1 + 35, "RTT до краю: 4–12 мс", size=10, color=FIELD, bold=True))
    p.append(text(px2 + 327, pop_y1 + 48, "TLS термінація на місці", size=9, color=MUTED))
    
    # PoP 2: Сан-Паулу
    p.append(rect(px2 + 20, pop_y2, 120, 50, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px2 + 80, pop_y2 + 20, "Клієнт (Сан-Паулу)", size=10.5, color=INK, bold=True))
    p.append(text(px2 + 80, pop_y2 + 38, "Локальний BGP", size=9.5, color=MUTED))
    
    p.append(arrow(px2 + 140, pop_y2 + 25, px2 + 230, pop_y2 + 25, color=FIELD, sw=1.5))
    p.append(rect(px2 + 230, pop_y2 - 5, 195, 60, fill="#e8f4fd", stroke=NEG, sw=1.2, rx=5))
    p.append(text(px2 + 327, pop_y2 + 18, "Edge PoP (Сан-Паулу)", size=11, color=INK, bold=True))
    p.append(text(px2 + 327, pop_y2 + 35, "RTT до краю: 5–15 мс", size=10, color=FIELD, bold=True))
    p.append(text(px2 + 327, pop_y2 + 48, "Кеш хіт / Edge Worker", size=9, color=MUTED))
    
    # PoP 3: Токіо
    p.append(rect(px2 + 20, pop_y3, 120, 50, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    p.append(text(px2 + 80, pop_y3 + 20, "Клієнт (Токіо)", size=10.5, color=INK, bold=True))
    p.append(text(px2 + 80, pop_y3 + 38, "Локальний BGP", size=9.5, color=MUTED))
    
    p.append(arrow(px2 + 140, pop_y3 + 25, px2 + 230, pop_y3 + 25, color=FIELD, sw=1.5))
    p.append(rect(px2 + 230, pop_y3 - 5, 195, 60, fill="#e8f4fd", stroke=NEG, sw=1.2, rx=5))
    p.append(text(px2 + 327, pop_y3 + 18, "Edge PoP (Токіо)", size=11, color=INK, bold=True))
    p.append(text(px2 + 327, pop_y3 + 35, "RTT до краю: 2–8 мс", size=10, color=FIELD, bold=True))
    p.append(text(px2 + 327, pop_y3 + 48, "Оптимізований бекбон", size=9, color=MUTED))

    p.append(text(px2 + pw2 / 2, py2 + 388, "Магістральний оптимізований зв'язок між PoP та Origin (Tier 1 Backbone)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "anycast-routing-edge.svg"), W, H, *p, title="Anycast-маршрутизація до найближчого вузла присутності (PoP)")


def fig_edge_cache_hierarchy():
    """Фігура 2: Багаторівнева ієрархія кешування: Edge PoP (L1), Origin Shield (L2) та Origin Server."""
    W, H = 960, 440
    p = []
    
    # ── Рівень 1: Клієнти та L1 Edge PoP ──
    p.append(rect(20, 50, 260, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(150, 75, "Рівень 1: Крайові вузли (L1)", size=12.5, color=INK, bold=True))
    p.append(text(150, 95, "Сотні PoP по всьому світу", size=10.5, color=MUTED))
    
    # Вузол L1-A
    p.append(rect(35, 120, 230, 80, fill="#ffffff", stroke=NEG, sw=1.3, rx=6))
    p.append(text(150, 142, "Edge PoP 1 (Франкфурт)", size=11.5, color=INK, bold=True))
    p.append(text(150, 162, "Швидкий RAM / NVMe кеш", size=10, color=MUTED))
    p.append(text(150, 182, "Cache Hit: 85–92% (2–5 мс)", size=10, color=FIELD, bold=True))
    
    # Вузол L1-B
    p.append(rect(35, 220, 230, 80, fill="#ffffff", stroke=NEG, sw=1.3, rx=6))
    p.append(text(150, 242, "Edge PoP 2 (Варшава)", size=11.5, color=INK, bold=True))
    p.append(text(150, 262, "Швидкий RAM / NVMe кеш", size=10, color=MUTED))
    p.append(text(150, 282, "Cache Hit: 85–92% (2–5 мс)", size=10, color=FIELD, bold=True))

    # Вузол L1-C
    p.append(rect(35, 320, 230, 75, fill="#ffffff", stroke=NEG, sw=1.3, rx=6))
    p.append(text(150, 342, "Edge PoP N (Стокгольм)", size=11.5, color=INK, bold=True))
    p.append(text(150, 362, "Cache Hit: 85–92% (2–5 мс)", size=10, color=FIELD, bold=True))
    p.append(text(150, 380, "Локальні промахи → L2 Shield", size=9.5, color=MUTED))

    # Стрілки L1 -> L2
    p.append(arrow(265, 160, 360, 210, color=POS, sw=1.5))
    p.append(arrow(265, 260, 360, 225, color=POS, sw=1.5))
    p.append(arrow(265, 350, 360, 240, color=POS, sw=1.5))
    
    # ── Рівень 2: Регіональний кеш / Origin Shield (L2) ──
    p.append(rect(360, 50, 260, 360, fill="#f4faf6", stroke="#a3d9b8", sw=1.2, rx=8))
    p.append(text(490, 75, "Рівень 2: Origin Shield (L2)", size=12.5, color=FIELD, bold=True))
    p.append(text(490, 95, "Регіональний консолідатор", size=10.5, color=MUTED))
    
    p.append(rect(375, 130, 230, 180, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(490, 155, "Регіональний Shield-вузол", size=12, color=INK, bold=True))
    p.append(text(490, 180, "Поглинає промахи з усіх L1", size=10.5, color=MUTED))
    p.append(text(490, 205, "Згортання дублікатів (Collapse)", size=10.5, color=POS, bold=True))
    p.append(text(490, 230, "L2 Hit Ratio: 60–80%", size=11, color=FIELD, bold=True))
    p.append(text(490, 255, "Сумарний Offload: 97–99%", size=11, color=FIELD, bold=True))
    p.append(text(490, 285, "Знижує навантаження на Origin в 50×", size=9.5, color=MUTED, italic=True))

    # Стрілка L2 -> Origin
    p.append(arrow(605, 220, 700, 220, color=POS, sw=1.8))
    p.append(text(652, 205, "Тільки 1–3%", size=10.5, color=POS, bold=True))
    p.append(text(652, 238, "промахів", size=10, color=MUTED))

    # ── Рівень 3: Джерело (Origin Server) ──
    p.append(rect(700, 50, 240, 360, fill="#fdfaf6", stroke="#e8c49e", sw=1.2, rx=8))
    p.append(text(820, 75, "Джерело даних (Origin)", size=12.5, color=POS, bold=True))
    p.append(text(820, 95, "Бекенд / Хмарний кластер", size=10.5, color=MUTED))
    
    p.append(rect(715, 130, 210, 180, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(820, 160, "Origin Backend", size=12, color=INK, bold=True))
    p.append(text(820, 190, "Генерація динаміки", size=10.5, color=MUTED))
    p.append(text(820, 215, "База даних / Мікросервіси", size=10.5, color=MUTED))
    p.append(text(820, 245, "Захищений від сплесків", size=10.5, color=FIELD, bold=True))
    p.append(text(820, 275, "Таймаути та ліміти пулу", size=9.5, color=MUTED))

    render(os.path.join(OUT, "edge-cache-hierarchy.svg"), W, H, *p, title="Ієрархія розподіленого кешування: Edge PoP, Origin Shield та джерело даних")


def fig_stale_while_revalidate():
    """Фігура 3: Асинхронне оновлення кешу за моделлю stale-while-revalidate."""
    W, H = 960, 430
    p = []
    
    # Шкала часу вгорі
    p.append(rect(30, 45, 900, 35, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(80, 67, "T0: Кеш свіжий", size=11, color=FIELD, bold=True))
    p.append(text(350, 67, "T1: TTL вичерпано (Stale вікно)", size=11, color=POS, bold=True))
    p.append(text(720, 67, "T2: Кеш оновлено у фоні", size=11, color=FIELD, bold=True))

    # Сценарій: Запит 1 приходить у вікні stale
    py = 100.0
    p.append(rect(30, py, 900, 145, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(50, py + 25, "1. Запит клієнта потрапляє на застарілий об'єкт у вікні stale-while-revalidate", size=12, color=INK, bold=True, anchor="start"))
    
    # Клієнт 1 -> Edge PoP
    p.append(rect(50, py + 45, 130, 50, fill="#f8fafc", stroke=LINE, sw=1.1, rx=4))
    p.append(text(115, py + 67, "Клієнт 1", size=11, color=INK, bold=True))
    p.append(text(115, py + 83, "GET /catalog/item", size=9.5, color=MUTED))
    
    p.append(arrow(180, py + 70, 270, py + 70, color=NEG, sw=1.5))
    
    # Edge PoP повертає Stale
    p.append(rect(270, py + 40, 240, 60, fill="#fef3c7", stroke="#d97706", sw=1.3, rx=4))
    p.append(text(390, py + 62, "Edge PoP (Кеш застарів)", size=11.5, color=INK, bold=True))
    p.append(text(390, py + 82, "Повертає Stale копію клієнту (2 мс)", size=10, color=POS, bold=True))
    
    p.append(arrow(270, py + 85, 180, py + 85, color=FIELD, sw=1.5))
    p.append(text(225, py + 102, "HTTP 200 (Stale)", size=9, color=FIELD, bold=True))

    # Паралельний фоновий запит до Origin
    p.append(arrow(510, py + 70, 670, py + 70, color=POS, sw=1.5))
    p.append(text(590, py + 60, "Фоновий запит (Async)", size=10, color=POS, bold=True))
    p.append(text(590, py + 88, "не блокує клієнта!", size=9.5, color=MUTED, italic=True))
    
    p.append(rect(670, py + 40, 230, 60, fill="#fdfaf6", stroke=POS, sw=1.3, rx=4))
    p.append(text(785, py + 62, "Origin Server", size=11.5, color=INK, bold=True))
    p.append(text(785, py + 82, "Генерація нової версії (250 мс)", size=10, color=MUTED))

    # Сценарій: Запит 2 приходить після фонового оновлення
    py2 = 265.0
    p.append(rect(30, py2, 900, 140, fill="#f4faf6", stroke="#a3d9b8", sw=1.2, rx=6))
    p.append(text(50, py2 + 25, "2. Наступний клієнт отримує вже свіжий оновлений об'єкт миттєво", size=12, color=FIELD, bold=True, anchor="start"))
    
    # Клієнт 2 -> Edge PoP
    p.append(rect(50, py2 + 45, 130, 50, fill="#ffffff", stroke=LINE, sw=1.1, rx=4))
    p.append(text(115, py2 + 67, "Клієнт 2", size=11, color=INK, bold=True))
    p.append(text(115, py2 + 83, "GET /catalog/item", size=9.5, color=MUTED))
    
    p.append(arrow(180, py2 + 70, 270, py2 + 70, color=NEG, sw=1.5))
    
    # Edge PoP повертає Fresh
    p.append(rect(270, py2 + 40, 320, 60, fill="#e8f8f5", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(430, py2 + 62, "Edge PoP (Кеш оновлено у фоні)", size=11.5, color=INK, bold=True))
    p.append(text(430, py2 + 82, "Миттєва відповідь Fresh Cache (2 мс)", size=10, color=FIELD, bold=True))
    
    p.append(arrow(270, py2 + 85, 180, py2 + 85, color=FIELD, sw=1.5))
    p.append(text(225, py2 + 102, "HTTP 200 (Fresh)", size=9, color=FIELD, bold=True))

    p.append(rect(670, py2 + 45, 230, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(785, py2 + 68, "Origin Server (Відпочиває)", size=11, color=MUTED, bold=True))
    p.append(text(785, py2 + 84, "0 навантаження від клієнта 2", size=9.5, color=FIELD))

    render(os.path.join(OUT, "stale-while-revalidate-flow.svg"), W, H, *p, title="Асинхронне оновлення кешу за моделлю stale-while-revalidate")


def fig_edge_worker_pipeline():
    """Фігура 4: Конвеєр виконання крайового коду (Edge Worker Pipeline)."""
    W, H = 960, 450
    p = []
    
    # Клієнт
    cx, cy = 60.0, 210.0
    p.append(rect(cx - 45, cy - 40, 90, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(cx, cy - 10, "Клієнт", size=12, color=INK, bold=True))
    p.append(text(cx, cy + 10, "Браузер / Додаток", size=9.5, color=MUTED))
    p.append(text(cx, cy + 26, "HTTPS запит", size=9, color=POS))
    
    # Стрілка Клієнт -> Вхід на край
    p.append(arrow(cx + 45, cy, 150, cy, color=POS, sw=1.5))
    
    # ── Велика панель Edge Node (Point of Presence) ──
    ew_x, ew_y, ew_w, ew_h = 150.0, 50.0, 580.0, 360.0
    p.append(rect(ew_x, ew_y, ew_w, ew_h, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(ew_x + ew_w / 2, ew_y + 24, "Edge Point of Presence (V8 Isolate / Wasm Runtime)", size=13, color=INK, bold=True))
    
    # Фаза 1: TLS Termination & WAF
    bx1 = ew_x + 20
    by1 = ew_y + 45
    p.append(rect(bx1, by1, 160, 65, fill="#feebe8", stroke=POS, sw=1.2, rx=5))
    p.append(text(bx1 + 80, by1 + 22, "1. TLS & WAF", size=11, color=INK, bold=True))
    p.append(text(bx1 + 80, by1 + 40, "Термінація TLS 1.3", size=9.5, color=MUTED))
    p.append(text(bx1 + 80, by1 + 54, "DDoS фільтрація", size=9, color=POS))

    p.append(arrow(bx1 + 160, by1 + 32, bx1 + 195, by1 + 32, color=LINE, sw=1.3))

    # Фаза 2: Edge Worker (Viewer Request)
    bx2 = bx1 + 195
    p.append(rect(bx2, by1, 165, 65, fill="#e8f8f5", stroke=FIELD, sw=1.3, rx=5))
    p.append(text(bx2 + 82, by1 + 22, "2. Edge Worker (Request)", size=11, color=FIELD, bold=True))
    p.append(text(bx2 + 82, by1 + 40, "Перевірка JWT / Auth", size=9.5, color=INK))
    p.append(text(bx2 + 82, by1 + 54, "A/B спліт / Geo-routing", size=9, color=MUTED))

    p.append(arrow(bx2 + 165, by1 + 32, bx2 + 200, by1 + 32, color=LINE, sw=1.3))

    # Фаза 3: Edge Cache Lookup
    bx3 = bx2 + 200
    p.append(rect(bx3, by1, 145, 65, fill="#e8f4fd", stroke=NEG, sw=1.3, rx=5))
    p.append(text(bx3 + 72, by1 + 22, "3. Cache Lookup", size=11, color=NEG, bold=True))
    p.append(text(bx3 + 72, by1 + 40, "Ключ: URL+Vary", size=9.5, color=MUTED))
    p.append(text(bx3 + 72, by1 + 54, "RAM / NVMe перевірка", size=9, color=MUTED))

    # Розгалуження Cache Hit / Cache Miss
    # Cache Hit (Повернення назад)
    p.append(arrow(bx3 + 72, by1 + 65, bx3 + 72, by1 + 175, color=FIELD, sw=1.5))
    p.append(text(bx3 + 120, by1 + 120, "Cache HIT (85%)", size=10, color=FIELD, bold=True))

    # Cache Miss (Вихід до Origin)
    p.append(arrow(bx3 + 145, by1 + 32, 770, by1 + 32, color=POS, sw=1.5))
    p.append(text(750, by1 + 18, "Cache MISS", size=10, color=POS, bold=True))

    # Джерело (Origin Server)
    ox, oy = 770.0, 50.0
    p.append(rect(ox, oy, 160, 160, fill="#fdfaf6", stroke=POS, sw=1.3, rx=6))
    p.append(text(ox + 80, oy + 30, "Origin Backend", size=12, color=INK, bold=True))
    p.append(text(ox + 80, oy + 55, "Пул Keep-Alive", size=10, color=MUTED))
    p.append(text(ox + 80, oy + 75, "з'єднань", size=10, color=MUTED))
    p.append(text(ox + 80, oy + 105, "Генерація відповіді", size=10, color=POS))
    p.append(text(ox + 80, oy + 130, "Заголовки кешування", size=9.5, color=MUTED))

    # Повернення від Origin до Edge
    p.append(arrow(ox, oy + 120, bx3 + 145, by1 + 200, color=POS, sw=1.5))

    # Фаза 4: Edge Worker (Response Mutation & Cache Store)
    by2 = by1 + 175
    p.append(rect(bx2, by2, 345, 75, fill="#fef9e7", stroke="#d4ac0d", sw=1.3, rx=5))
    p.append(text(bx2 + 172, by2 + 22, "4. Edge Worker (Origin Response & Cache Store)", size=11, color=INK, bold=True))
    p.append(text(bx2 + 172, by2 + 42, "Стримінг тіла, оптимізація HTML/JSON, ін'єкція security-заголовків", size=9.5, color=MUTED))
    p.append(text(bx2 + 172, by2 + 60, "Запис у розподілений кеш згідно з Cache-Control", size=9.5, color=FIELD, bold=True))

    # Стрілка повернення клієнту
    p.append(arrow(bx2, by2 + 37, bx1 + 160, by2 + 37, color=LINE, sw=1.3))

    # Фаза 5: Viewer Response
    p.append(rect(bx1, by2, 160, 75, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(bx1 + 80, by2 + 22, "5. Viewer Response", size=11, color=FIELD, bold=True))
    p.append(text(bx1 + 80, by2 + 42, "Стиснення (Brotli/Zstd)", size=9.5, color=MUTED))
    p.append(text(bx1 + 80, by2 + 60, "Віддача через HTTP/3", size=9.5, color=INK))

    p.append(arrow(bx1, by2 + 37, cx + 45, by2 + 37, color=FIELD, sw=1.5))
    p.append(text(cx + 95, by2 + 55, "HTTP 200 OK", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "edge-worker-pipeline.svg"), W, H, *p, title="Життєвий цикл виконання крайового обробника (Edge Worker)")


if __name__ == "__main__":
    fig_anycast_routing()
    fig_edge_cache_hierarchy()
    fig_stale_while_revalidate()
    fig_edge_worker_pipeline()
    print("Всі 4 фігури успішно згенеровано.")
