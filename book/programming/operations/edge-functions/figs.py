# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми Edge Functions."""
import sys, os

# Додаємо шлях до svgkit у кореневій папці scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_edge_topology_latency():
    """Фігура 1: Порівняння топологій — централізована хмара проти крайових обчислень на CDN."""
    W, H = 960, 480
    p = []
    
    p.append(text(W / 2, 28, "Топологія мережевих затримок: централізований FaaS проти крайових функцій (Edge)", size=15.5, color=INK, bold=True))
    
    # ── Панель 1: Традиційний централізований FaaS ──
    py1 = 55.0
    pw, ph = 445.0, 395.0
    px1 = 22.0
    p.append(rect(px1, py1, pw, ph, fill="#fdfaf6", stroke="#e8c49e", sw=1.3, rx=8))
    p.append(text(px1 + pw / 2, py1 + 24, "Централізований FaaS (напр. AWS Lambda в us-east-1)", size=13, color=POS, bold=True))
    
    # Клієнт у Токіо
    cx1 = px1 + 25
    cy1 = py1 + 60
    p.append(rect(cx1, cy1, 125, 65, fill="#fbe9e7", stroke=POS, sw=1.2, rx=6))
    p.append(text(cx1 + 62, cy1 + 25, "Користувач", size=12, color=INK, bold=True))
    p.append(text(cx1 + 62, cy1 + 45, "Токіо (Японія)", size=10.5, color=MUTED))
    
    # Трансокеанський оптоволоконний лінк
    p.append(arrow(cx1 + 125, cy1 + 32, px1 + pw - 155, cy1 + 32, color=POS, sw=2))
    p.append(text(px1 + 215, cy1 + 18, "11 000 км (RTT ≈ 240 мс)", size=10.5, color=POS, bold=True))
    p.append(text(px1 + 215, cy1 + 48, "Транзит через 15 хопів", size=10, color=MUTED))
    
    # Центральний ЦОД
    dc_x1 = px1 + pw - 150
    dc_y1 = cy1
    p.append(rect(dc_x1, dc_y1, 130, 65, fill="#fbe9e7", stroke=POS, sw=1.2, rx=6))
    p.append(text(dc_x1 + 65, dc_y1 + 25, "Хмарний регіон", size=12, color=INK, bold=True))
    p.append(text(dc_x1 + 65, dc_y1 + 45, "us-east-1 (США)", size=10.5, color=MUTED))
    
    # Послідовні кроки в централізованій моделі
    sy1 = py1 + 145
    steps1 = [
        ("1. Запит користувача", "HTTP GET /api/v1/profile з JWT-токеном у заголовку"),
        ("2. Мережевий транзит", "Затримка світла у волокні + маршрутизація: ~240 мс RTT"),
        ("3. Виконання функції", "Холодний/теплий запуск MicroVM у центральному ЦОД: 25 мс"),
        ("4. Зворотна відповідь", "Транзит через Тихий океан назад у Токіо: ~120 мс"),
    ]
    for i, (stitle, sdesc) in enumerate(steps1):
        box_y = sy1 + i * 52
        p.append(rect(px1 + 20, box_y, pw - 40, 44, fill="#ffffff", stroke="#f0d5be", sw=1, rx=5))
        p.append(text(px1 + 32, box_y + 18, stitle, size=11, color=POS, bold=True, anchor="start"))
        p.append(text(px1 + 32, box_y + 34, sdesc, size=10, color=INK, anchor="start"))
    
    p.append(text(px1 + pw / 2, py1 + ph - 16, "Сумарна затримка для користувача: 260–380 мс", size=12, color=POS, bold=True))
    
    # ── Панель 2: Крайові функції (Edge Functions) ──
    px2 = px1 + pw + 25
    p.append(rect(px2, py1, pw, ph, fill="#f4faf6", stroke="#a3d9b8", sw=1.3, rx=8))
    p.append(text(px2 + pw / 2, py1 + 24, "Крайові функції на PoP CDN (Edge Functions)", size=13, color=FIELD, bold=True))
    
    # Клієнт у Токіо
    cx2 = px2 + 25
    cy2 = py1 + 60
    p.append(rect(cx2, cy2, 125, 65, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(cx2 + 62, cy2 + 25, "Користувач", size=12, color=INK, bold=True))
    p.append(text(cx2 + 62, cy2 + 45, "Токіо (Японія)", size=10.5, color=MUTED))
    
    # Локальний лінк до PoP
    p.append(arrow(cx2 + 125, cy2 + 32, px2 + pw - 155, cy2 + 32, color=FIELD, sw=2))
    p.append(text(px2 + 215, cy2 + 18, "Остання миля (RTT ≈ 8 мс)", size=10.5, color=FIELD, bold=True))
    p.append(text(px2 + 215, cy2 + 48, "Anycast-маршрутизація", size=10, color=MUTED))
    
    # PoP у Токіо
    pop_x2 = px2 + pw - 150
    pop_y2 = cy2
    p.append(rect(pop_x2, pop_y2, 130, 65, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(pop_x2 + 65, pop_y2 + 25, "Edge PoP (Токіо)", size=12, color=INK, bold=True))
    p.append(text(pop_x2 + 65, pop_y2 + 45, "V8 Isolate / Wasm", size=10.5, color=FIELD, bold=True))
    
    # Послідовні кроки в Edge моделі
    sy2 = py1 + 145
    steps2 = [
        ("1. Запит користувача", "Маршрутизація Anycast BGP на найближчий сервер PoP"),
        ("2. Локальна обробка", "Запуск V8 Isolate (< 5 мс), валідація JWT та A/B спліт"),
        ("3. Edge Cache / KV", "Миттєва віддача з локального сховища PoP (1–2 мс)"),
        ("4. Асинхронний бекенд", "Лише за потреби: стримінг у фоні через магістраль"),
    ]
    for i, (stitle, sdesc) in enumerate(steps2):
        box_y = sy2 + i * 52
        p.append(rect(px2 + 20, box_y, pw - 40, 44, fill="#ffffff", stroke="#c2edd3", sw=1, rx=5))
        p.append(text(px2 + 32, box_y + 18, stitle, size=11, color=FIELD, bold=True, anchor="start"))
        p.append(text(px2 + 32, box_y + 34, sdesc, size=10, color=INK, anchor="start"))
    
    p.append(text(px2 + pw / 2, py1 + ph - 16, "Сумарна затримка для користувача: 12–25 мс", size=12, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "edge-topology-latency.svg"), W, H, *p)


def fig_v8_isolates_vs_containers():
    """Фігура 2: Моделі ізоляції — контейнери/MicroVM проти V8 Isolates і Wasm."""
    W, H = 960, 470
    p = []
    
    p.append(text(W / 2, 28, "Порівняння архітектури ізоляції: MicroVM проти V8 Isolates та WebAssembly", size=15.5, color=INK, bold=True))
    
    # ── Ліва панель: MicroVM / Контейнери ──
    px1, py1, pw, ph = 24.0, 55.0, 440.0, 390.0
    p.append(rect(px1, py1, pw, ph, fill="#fdfaf6", stroke="#e8c49e", sw=1.3, rx=8))
    p.append(text(px1 + pw / 2, py1 + 24, "Традиційний FaaS: Ізоляція на рівні ОС / MicroVM", size=12.5, color=POS, bold=True))
    
    # Залізо + Хостове ядро
    p.append(rect(px1 + 20, py1 + 315, pw - 40, 50, fill="#f5f5f5", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(px1 + pw / 2, py1 + 335, "Хостова ОС Linux (KVM / cgroups / namespaces)", size=11, color=INK, bold=True))
    p.append(text(px1 + pw / 2, py1 + 352, "Фізичний сервер (Bare Metal Host)", size=10, color=MUTED))
    
    # MicroVM 1
    mv1_x = px1 + 20
    mv1_y = py1 + 50
    mv_w = 190.0
    p.append(rect(mv1_x, mv1_y, mv_w, 250, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=6))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 22, "MicroVM / Pod #1", size=12, color=POS, bold=True))
    
    p.append(rect(mv1_x + 12, mv1_y + 36, mv_w - 24, 48, fill="#fbe9e7", stroke=POS, sw=1, rx=4))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 55, "Код функції + Node.js", size=10.5, color=INK, bold=True))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 72, "Пам'ять: 30–60 МБ", size=9.5, color=POS))
    
    p.append(rect(mv1_x + 12, mv1_y + 92, mv_w - 24, 46, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 112, "Гостьова ОС (Linux Kernel)", size=10, color=MUTED))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 128, "Ініціалізація: 80–200 мс", size=9.5, color=MUTED))
    
    p.append(rect(mv1_x + 12, mv1_y + 146, mv_w - 24, 44, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 166, "Віртуальні пристрої (virtio)", size=10, color=MUTED))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 180, "Емуляція блоків та мережі", size=9.5, color=MUTED))
    
    p.append(rect(mv1_x + 12, mv1_y + 198, mv_w - 24, 42, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv1_x + mv_w / 2, mv1_y + 220, "Firecracker / vCPU", size=10, color=MUTED))
    
    # MicroVM 2
    mv2_x = px1 + 230
    p.append(rect(mv2_x, mv1_y, mv_w, 250, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=6))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 22, "MicroVM / Pod #2", size=12, color=POS, bold=True))
    
    p.append(rect(mv2_x + 12, mv1_y + 36, mv_w - 24, 48, fill="#fbe9e7", stroke=POS, sw=1, rx=4))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 55, "Код функції #2 (Python)", size=10.5, color=INK, bold=True))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 72, "Пам'ять: 40–80 МБ", size=9.5, color=POS))
    
    p.append(rect(mv2_x + 12, mv1_y + 92, mv_w - 24, 46, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 112, "Гостьова ОС (Linux Kernel)", size=10, color=MUTED))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 128, "Ініціалізація: 80–200 мс", size=9.5, color=MUTED))
    
    p.append(rect(mv2_x + 12, mv1_y + 146, mv_w - 24, 44, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 166, "Віртуальні пристрої (virtio)", size=10, color=MUTED))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 180, "Емуляція блоків та мережі", size=9.5, color=MUTED))
    
    p.append(rect(mv2_x + 12, mv1_y + 198, mv_w - 24, 42, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(mv2_x + mv_w / 2, mv1_y + 220, "Firecracker / vCPU", size=10, color=MUTED))
    
    p.append(text(px1 + pw / 2, py1 + ph - 14, "Накладні витрати: ~35 МБ RAM на функцію; старт: ~150 мс", size=10.5, color=POS, bold=True))
    
    # ── Права панель: V8 Isolates / Wasm ──
    px2 = px1 + pw + 32
    p.append(rect(px2, py1, pw, ph, fill="#f4faf6", stroke="#a3d9b8", sw=1.3, rx=8))
    p.append(text(px2 + pw / 2, py1 + 24, "Edge Runtime: Програмна ізоляція (V8 Isolates / Wasm)", size=12.5, color=FIELD, bold=True))
    
    # Залізо + Хостове ядро
    p.append(rect(px2 + 20, py1 + 315, pw - 40, 50, fill="#f5f5f5", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(px2 + pw / 2, py1 + 335, "Хостова ОС Linux (єдиний системний процес воркера)", size=11, color=INK, bold=True))
    p.append(text(px2 + pw / 2, py1 + 352, "Фізичний сервер Edge PoP", size=10, color=MUTED))
    
    # Єдиний V8 Process
    v8_box_y = py1 + 50
    p.append(rect(px2 + 20, v8_box_y, pw - 40, 250, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(px2 + pw / 2, v8_box_y + 22, "Єдиний процес рантайму V8 Engine / Wasmtime", size=12, color=FIELD, bold=True))
    
    # Спільний JIT / GC
    p.append(rect(px2 + 30, v8_box_y + 36, pw - 60, 36, fill="#ffffff", stroke="#a3d9b8", sw=1, rx=4))
    p.append(text(px2 + pw / 2, v8_box_y + 56, "Спільний компілятор TurboFan / JIT / Базовий рантайм", size=10.5, color=INK))
    
    # 3 паралельні Isolates
    iso_w = 115.0
    iso_y = v8_box_y + 82
    
    iso_data = [
        ("Isolate #1 (Орендар A)", "1.5 МБ RAM", "< 2 мс старт"),
        ("Isolate #2 (Орендар B)", "2.0 МБ RAM", "< 1 мс старт"),
        ("Isolate #3 (Wasm модуль)", "0.8 МБ RAM", "< 0.1 мс старт"),
    ]
    for i, (ititle, iram, istart) in enumerate(iso_data):
        ix = px2 + 30 + i * (iso_w + 16)
        p.append(rect(ix, iso_y, iso_w, 155, fill="#f0fdf4", stroke=FIELD, sw=1.1, rx=5))
        p.append(text(ix + iso_w / 2, iso_y + 22, ititle, size=9.5, color=FIELD, bold=True))
        
        p.append(rect(ix + 8, iso_y + 38, iso_w - 16, 46, fill="#ffffff", stroke="#c2edd3", sw=1, rx=3))
        p.append(text(ix + iso_w / 2, iso_y + 56, "Окрема купа", size=9.5, color=INK))
        p.append(text(ix + iso_w / 2, iso_y + 72, "(Heap Sandbox)", size=9.5, color=MUTED))
        
        p.append(rect(ix + 8, iso_y + 92, iso_w - 16, 48, fill="#ffffff", stroke="#c2edd3", sw=1, rx=3))
        p.append(text(ix + iso_w / 2, iso_y + 110, iram, size=10, color=POS, bold=True))
        p.append(text(ix + iso_w / 2, iso_y + 128, istart, size=9.5, color=FIELD, bold=True))
        
    p.append(text(px2 + pw / 2, py1 + ph - 14, "Накладні витрати: ~1.5 МБ RAM на функцію; старт: 0–5 мс", size=10.5, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "v8-isolates-vs-containers.svg"), W, H, *p)


def fig_edge_request_pipeline():
    """Фігура 3: Життєвий цикл запиту та точки перехоплення на Edge (Pipeline)."""
    W, H = 960, 440
    p = []
    
    p.append(text(W / 2, 26, "Конвеєр обробки та перехоплення запиту на крайовому вузлі (Edge Request Pipeline)", size=15.5, color=INK, bold=True))
    
    # ── Лівий блок: Клієнт ──
    cx, cy = 25.0, 140.0
    cw, ch = 125.0, 140.0
    p.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(cx + cw / 2, cy + 30, "Клієнт", size=13, color=INK, bold=True))
    p.append(text(cx + cw / 2, cy + 50, "(Браузер / Додаток)", size=10, color=MUTED))
    p.append(text(cx + cw / 2, cy + 85, "HTTP GET /", size=11, color=FIELD, bold=True))
    p.append(text(cx + cw / 2, cy + 105, "User-Agent, Cookie", size=10, color=MUTED))
    
    # ── Середній блок: Edge Worker Node ──
    ex, ey = 180.0, 55.0
    ew, eh = 560.0, 355.0
    p.append(rect(ex, ey, ew, eh, fill="#f4faf6", stroke="#a3d9b8", sw=1.4, rx=8))
    p.append(text(ex + 18, ey + 24, "Крайовий вузол PoP (Edge Worker Runtime)", size=13, color=FIELD, bold=True, anchor="start"))
    
    # Стрілка Клієнт -> Viewer Request
    p.append(arrow(cx + cw, cy + 30, ex + 25, ey + 75, color=FIELD, sw=1.8))
    p.append(text(cx + cw + 15, cy + 10, "1. Запит", size=10, color=FIELD, bold=True))
    
    # Блок 1: Viewer Request Handler
    b1_x, b1_y = ex + 25, ey + 50
    b1_w, b1_h = 230.0, 70.0
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(b1_x + b1_w / 2, b1_y + 22, "1. Viewer Request Hook", size=11, color=FIELD, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 40, "Перевірка JWT, GeoIP, переписування URL,", size=9.5, color=INK))
    p.append(text(b1_x + b1_w / 2, b1_y + 55, "A/B спліт та маршрутизація", size=9.5, color=INK))
    
    # Блок 2: Edge Cache / KV
    b2_x, b2_y = ex + 300, ey + 50
    b2_w, b2_h = 230.0, 70.0
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#ffffff", stroke="#0ea5e9", sw=1.2, rx=5))
    p.append(text(b2_x + b2_w / 2, b2_y + 22, "2. Перевірка Edge Cache", size=11, color="#0284c7", bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 40, "Cache API / Edge KV Store", size=10, color=INK))
    p.append(text(b2_x + b2_w / 2, b2_y + 55, "Пошук за ключем запиту", size=9.5, color=MUTED))
    
    # Стрілка Viewer Request -> Cache
    p.append(arrow(b1_x + b1_w, b1_y + 35, b2_x, b2_y + 35, color="#0ea5e9", sw=1.5))
    p.append(text(b1_x + b1_w + 22, b1_y + 22, "match()", size=10, color="#0ea5e9", bold=True))
    
    # Шлях Cache HIT (стрілка вниз праворуч)
    p.append(arrow(b2_x + 190, b2_y + b2_h, b2_x + 190, ey + 240, color=FIELD, sw=1.5))
    p.append(text(b2_x + 150, ey + 180, "HIT: 2 мс", size=10, color=FIELD, bold=True))
    
    # Блок 3: Origin Request / Fetch Subrequest
    b3_x, b3_y = ex + 300, ey + 150
    b3_w, b3_h = 230.0, 70.0
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=5))
    p.append(text(b3_x + b3_w / 2, b3_y + 22, "3. Origin Request (MISS)", size=11, color=POS, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 40, "fetch(originRequest)", size=10, color=INK, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 55, "Додавання ключів та підписів", size=9.5, color=MUTED))
    
    # Стрілка Cache -> Origin Request (MISS)
    p.append(arrow(b2_x + 45, b2_y + b2_h, b2_x + 45, b3_y, color=POS, sw=1.5))
    p.append(text(b2_x + 15, b2_y + b2_h + 18, "MISS", size=9.5, color=POS, bold=True))
    
    # Блок 4: Streaming Transform & Response Hook
    b4_x, b4_y = ex + 25, ey + 240
    b4_w, b4_h = 505.0, 85.0
    p.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#ffffff", stroke=FIELD, sw=1.3, rx=5))
    p.append(text(b4_x + b4_w / 2, b4_y + 22, "4. Потокова трансформація (TransformStream) та Viewer Response Hook", size=11.5, color=FIELD, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 44, "Модифікація HTML/JSON на льоту, стиснення (Brotli), додавання заголовків безпеки,", size=10, color=INK))
    p.append(text(b4_x + b4_w / 2, b4_y + 64, "асинхронне оновлення кешу через ctx.waitUntil(caches.default.put(...))", size=9.5, color=MUTED))
    
    # Стрілка з Origin Request до Transform
    p.append(arrow(b3_x + 45, b3_y + b3_h, b3_x + 45, b4_y, color=POS, sw=1.5))
    
    # Стрілка Transform -> Клієнт
    p.append(arrow(b4_x, b4_y + 45, cx + cw, cy + 95, color=FIELD, sw=1.8))
    p.append(text(cx + cw + 15, cy + 120, "5. Стримінг", size=10, color=FIELD, bold=True))
    
    # ── Правий блок: Origin Backend ──
    ox, oy = 770.0, 140.0
    ow, oh = 165.0, 140.0
    p.append(rect(ox, oy, ow, oh, fill="#fbe9e7", stroke=POS, sw=1.3, rx=6))
    p.append(text(ox + ow / 2, oy + 28, "Origin Server", size=12.5, color=POS, bold=True))
    p.append(text(ox + ow / 2, oy + 48, "(Центральний бекенд)", size=10, color=MUTED))
    p.append(text(ox + ow / 2, oy + 82, "PostgreSQL / База даних", size=10, color=INK))
    p.append(text(ox + ow / 2, oy + 105, "Monolith / Microservices", size=10, color=INK))
    
    # Стрілки між Edge та Origin
    p.append(arrow(b3_x + b3_w, b3_y + 25, ox, oy + 35, color=POS, sw=1.5))
    p.append(arrow(ox, oy + 75, b3_x + b3_w, b3_y + 55, color=LINE, sw=1.5))
    p.append(text(ox - 20, oy + 25, "HTTPS", size=9.5, color=POS))
    p.append(text(ox - 20, oy + 95, "Body", size=9.5, color=LINE))
    
    render(os.path.join(OUT, "edge-request-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_edge_topology_latency()
    fig_v8_isolates_vs_containers()
    fig_edge_request_pipeline()
    print("Всі SVG-фігури для edge-functions згенеровано успішно.")
