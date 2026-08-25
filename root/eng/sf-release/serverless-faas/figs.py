# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми Serverless/FaaS."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_cold_vs_warm_start():
    """Фігура 1: Порівняння фаз виконання — Холодний старт проти Гарячого старту."""
    W, H = 960, 490
    p = []
    
    p.append(text(W / 2, 30, "Анатомія затримки: холодний запуск проти теплого повторного виклику", size=16, color=INK, bold=True))
    
    # ── Панель 1: Холодний старт (Cold Start) ──
    py1 = 60.0
    pw, ph = 912.0, 185.0
    px = 24.0
    p.append(rect(px, py1, pw, ph, fill="#fdfaf6", stroke="#e8c49e", sw=1.3, rx=8))
    p.append(text(px + 18, py1 + 24, "Холодний старт (Cold Start) — перше звертання або масштабування вгору (загалом ≈ 350–1500 мс)", size=13.5, color=POS, bold=True, anchor="start"))
    
    bx = px + 18
    by = py1 + 45
    
    # Фаза 1: Створення мікровіртуальної машини / пісочниці (30-80 мс)
    w1 = 195.0
    p.append(rect(bx, by, w1, 62, fill="#fbe9e7", stroke=POS, sw=1.2, rx=5))
    p.append(text(bx + w1 / 2, by + 24, "1. Виділення пісочниці", size=12, color=INK, bold=True))
    p.append(text(bx + w1 / 2, by + 44, "MicroVM / cgroup (30–80 мс)", size=10.5, color=MUTED))
    
    # Стрілка 1
    p.append(arrow(bx + w1, by + 31, bx + w1 + 20, by + 31, color=LINE, sw=1.5))
    
    # Фаза 2: Завантаження коду / шарів (50-250 мс)
    bx2 = bx + w1 + 24
    w2 = 205.0
    p.append(rect(bx2, by, w2, 62, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=5))
    p.append(text(bx2 + w2 / 2, by + 24, "2. Завантаження коду", size=12, color=INK, bold=True))
    p.append(text(bx2 + w2 / 2, by + 44, "Fetch zip / image (50–250 мс)", size=10.5, color=MUTED))
    
    # Стрілка 2
    p.append(arrow(bx2 + w2, by + 31, bx2 + w2 + 20, by + 31, color=LINE, sw=1.5))
    
    # Фаза 3: Статична ініціалізація (100-1000 мс)
    bx3 = bx2 + w2 + 24
    w3 = 220.0
    p.append(rect(bx3, by, w3, 62, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=5))
    p.append(text(bx3 + w3 / 2, by + 24, "3. Ініціалізація середовища", size=12, color=INK, bold=True))
    p.append(text(bx3 + w3 / 2, by + 44, "JVM/V8, імпорти, DB-клієнт", size=10.5, color=MUTED))
    
    # Стрілка 3
    p.append(arrow(bx3 + w3, by + 31, bx3 + w3 + 20, by + 31, color=LINE, sw=1.5))
    
    # Фаза 4: Виконання обробника (10-50 мс)
    bx4 = bx3 + w3 + 24
    w4 = 170.0
    p.append(rect(bx4, by, w4, 62, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(bx4 + w4 / 2, by + 24, "4. Обробник (Invoke)", size=12, color=INK, bold=True))
    p.append(text(bx4 + w4 / 2, by + 44, "handler(event, ctx)", size=10.5, color=FIELD, bold=True))
    
    p.append(text(px + 20, py1 + 132, "Платформа виконує повний ланцюг: виділення пісочниці, розгортання артефакту, запуск VM і статичні імпорти.", size=11, color=MUTED, anchor="start"))
    p.append(text(px + 20, py1 + 154, "Оптимізації: знімки пам'яті (SnapStart/Firecracker), мінімальний розмір артефакту, скомпільовані мови (Go/Rust/C++).", size=11, color=INK, anchor="start"))
    
    # ── Панель 2: Теплий запуск (Warm Start) ──
    py2 = 265.0
    p.append(rect(px, py2, pw, 190.0, fill="#f4faf6", stroke="#a3d9b8", sw=1.3, rx=8))
    p.append(text(px + 18, py2 + 24, "Теплий старт (Warm Start) — повторний виклик у живій прогрітій пісочниці (загалом ≈ 5–25 мс)", size=13.5, color=FIELD, bold=True, anchor="start"))
    
    by2 = py2 + 45
    
    # Пропущений блок (сірий)
    w_skip = 428.0
    p.append(rect(bx, by2, w_skip, 62, fill="#eef2f5", stroke="#cbd5e1", sw=1.1, rx=5))
    p.append(text(bx + w_skip / 2, by2 + 25, "Пропущено: пісочниця вже створена, образ змонтовано", size=11.5, color=MUTED))
    p.append(text(bx + w_skip / 2, by2 + 45, "Фази 1 і 2 не виконуються повторно", size=10.5, color=MUTED, italic=True))
    
    # Стрілка
    p.append(arrow(bx + w_skip, by2 + 31, bx + w_skip + 20, by2 + 31, color=LINE, sw=1.5))
    
    # Збережений стан
    bx_cached = bx + w_skip + 24
    w_cached = 220.0
    p.append(rect(bx_cached, by2, w_cached, 62, fill="#e8f4fd", stroke=NEG, sw=1.2, rx=5))
    p.append(text(bx_cached + w_cached / 2, by2 + 24, "Збережений глобальний стан", size=12, color=INK, bold=True))
    p.append(text(bx_cached + w_cached / 2, by2 + 44, "Пул з'єднань, кеші в пам'яті (0 мс)", size=10.5, color=NEG))
    
    # Стрілка
    p.append(arrow(bx_cached + w_cached, by2 + 31, bx_cached + w_cached + 20, by2 + 31, color=LINE, sw=1.5))
    
    # Обробник
    bx_inv2 = bx_cached + w_cached + 24
    w_inv2 = 170.0
    p.append(rect(bx_inv2, by2, w_inv2, 62, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(bx_inv2 + w_inv2 / 2, by2 + 24, "Обробник (Invoke)", size=12, color=INK, bold=True))
    p.append(text(bx_inv2 + w_inv2 / 2, by2 + 44, "handler(event, ctx) (5–20 мс)", size=10.5, color=FIELD, bold=True))
    
    p.append(text(px + 20, py2 + 132, "Пісочниця залишається «теплою» протягом 5–30 хв бездіяльності. Повторні запити йдуть безпосередньо в обробник.", size=11, color=MUTED, anchor="start"))
    p.append(text(px + 20, py2 + 154, "Увага: будь-який збережений стан (з'єднання, локальний кеш) зникає при масштабуванні в 0 або заміні пісочниці.", size=11, color=POS, anchor="start"))
    
    render(os.path.join(OUT, "cold-vs-warm-start.svg"), W, H, *p,
           title="Анатомія затримки: холодний запуск проти теплого повторного виклику")


def fig_faas_architecture_topology():
    """Фігура 2: Архітектурна топологія платформи безсерверних обчислень."""
    W, H = 960, 520
    p = []
    
    p.append(text(W / 2, 28, "Топологія FaaS-платформи: від джерела події до ізольованої пісочниці", size=16, color=INK, bold=True))
    
    # ── Колонка 1: Джерела подій (Event Sources) ──
    x1 = 24.0
    y1 = 60.0
    w1 = 170.0
    h1 = 430.0
    p.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 24, "Джерела подій", size=13, color=INK, bold=True))
    
    events = [
        ("HTTP API Gateway", "Синхронні REST/gRPC"),
        ("Об'єктне сховище", "S3: PutObject, Delete"),
        ("Черги та стрими", "SQS, Kafka, Kinesis"),
        ("Планувальник (Cron)", "EventBridge, таймери"),
        ("Зміна в базі даних", "CDC, DynamoDB Streams"),
    ]
    for idx, (title_ev, desc_ev) in enumerate(events):
        ey = y1 + 48 + idx * 72
        p.append(rect(x1 + 10, ey, w1 - 20, 60, fill="#ffffff", stroke="#94a3b8", sw=1.1, rx=5))
        p.append(text(x1 + w1 / 2, ey + 22, title_ev, size=11.5, color=INK, bold=True))
        p.append(text(x1 + w1 / 2, ey + 42, desc_ev, size=10, color=MUTED))
    
    # Стрілка від подій до Ingress/Control Plane
    ax1 = x1 + w1
    ax2 = ax1 + 26
    for idx in range(5):
        ey = y1 + 78 + idx * 72
        p.append(arrow(ax1, ey, ax2, ey, color=LINE, sw=1.3))
    
    # ── Колонка 2: Площина керування та планувальник (Control Plane & Placement) ──
    x2 = ax2 + 8
    w2 = 210.0
    p.append(rect(x2, y1, w2, h1, fill="#eff6ff", stroke="#93c5fd", sw=1.3, rx=8))
    p.append(text(x2 + w2 / 2, y1 + 24, "Площина керування", size=13, color=NEG, bold=True))
    
    ctrl_blocks = [
        ("Вхідний роутер / Ingress", "Автентифікація, ліміти, квоти"),
        ("Диспетчер викликів", "Placement & Scheduling Engine"),
        ("Реєстр пісочниць", "Відстеження теплих інстансів"),
        ("Сховище артефактів", "Кеш S3 / OCI Layers"),
        ("Автоскейлер площини", "Підйом нових воркерів"),
    ]
    for idx, (ctitle, cdesc) in enumerate(ctrl_blocks):
        cy = y1 + 48 + idx * 72
        p.append(rect(x2 + 10, cy, w2 - 20, 60, fill="#ffffff", stroke="#60a5fa", sw=1.1, rx=5))
        p.append(text(x2 + w2 / 2, cy + 22, ctitle, size=11.5, color=INK, bold=True))
        p.append(text(x2 + w2 / 2, cy + 42, cdesc, size=10, color=MUTED))
    
    # Стрілка від Control Plane до Worker Fleet
    bx1 = x2 + w2
    bx2 = bx1 + 26
    for idx in range(3):
        cy = y1 + 90 + idx * 130
        p.append(arrow(bx1, cy, bx2, cy, color=LINE, sw=1.3))
    
    # ── Колонка 3: Робочі вузли (Worker Fleet & Sandboxes) ──
    x3 = bx2 + 8
    w3 = 260.0
    p.append(rect(x3, y1, w3, h1, fill="#f0fdf4", stroke="#86efac", sw=1.3, rx=8))
    p.append(text(x3 + w3 / 2, y1 + 24, "Робочі вузли (Worker Fleet)", size=13, color=FIELD, bold=True))
    
    # Вузол 1 (Воркер)
    ny1 = y1 + 42
    p.append(rect(x3 + 10, ny1, w3 - 20, 175, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=6))
    p.append(text(x3 + 22, ny1 + 20, "Worker Node A (Host Linux KVM)", size=11, color=FIELD, bold=True, anchor="start"))
    
    # Пісочниця 1 у Воркері 1
    p.append(rect(x3 + 18, ny1 + 30, w3 - 36, 60, fill="#fef2f2", stroke=POS, sw=1.1, rx=4))
    p.append(text(x3 + w3 / 2, ny1 + 50, "MicroVM 1 (Тепла, екземпляр А)", size=10.5, color=INK, bold=True))
    p.append(text(x3 + w3 / 2, ny1 + 72, "Runtime API ← Bootstrap ← Handler", size=9.5, color=POS))
    
    # Пісочниця 2 у Воркері 1
    p.append(rect(x3 + 18, ny1 + 100, w3 - 36, 60, fill="#fef9c3", stroke="#eab308", sw=1.1, rx=4))
    p.append(text(x3 + w3 / 2, ny1 + 120, "MicroVM 2 (Холодний запуск...)", size=10.5, color=INK, bold=True))
    p.append(text(x3 + w3 / 2, ny1 + 142, "Init: розпакування zip і запуск JVM", size=9.5, color="#854d0e"))
    
    # Вузол 2 (Воркер)
    ny2 = ny1 + 190
    p.append(rect(x3 + 10, ny2, w3 - 20, 185, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=6))
    p.append(text(x3 + 22, ny2 + 20, "Worker Node B (Host Linux KVM)", size=11, color=FIELD, bold=True, anchor="start"))
    
    # Пісочниця 3 у Воркері 2
    p.append(rect(x3 + 18, ny2 + 32, w3 - 36, 62, fill="#fef2f2", stroke=POS, sw=1.1, rx=4))
    p.append(text(x3 + w3 / 2, ny2 + 52, "MicroVM 3 (Виконує запит)", size=10.5, color=INK, bold=True))
    p.append(text(x3 + w3 / 2, ny2 + 74, "Handler обробляє POST /orders", size=9.5, color=POS))
    
    # Пісочниця 4 (Idle/Freezer)
    p.append(rect(x3 + 18, ny2 + 104, w3 - 36, 62, fill="#f1f5f9", stroke="#94a3b8", sw=1.1, rx=4))
    p.append(text(x3 + w3 / 2, ny2 + 124, "MicroVM 4 (Заморожена cgroup)", size=10.5, color=MUTED, bold=True))
    p.append(text(x3 + w3 / 2, ny2 + 146, "CPU = 0, очікує виклику або видалення", size=9.5, color=MUTED))
    
    # Стрілка від Sandboxes до External State
    cx1 = x3 + w3
    cx2 = cx1 + 26
    for idx in range(3):
        sy = y1 + 100 + idx * 115
        p.append(arrow(cx1, sy, cx2, sy, color=LINE, sw=1.3))
    
    # ── Колонка 4: Зовнішній стан (External Backends) ──
    x4 = cx2 + 8
    w4 = 170.0
    p.append(rect(x4, y1, w4, h1, fill="#faf5ff", stroke="#d8b4fe", sw=1.3, rx=8))
    p.append(text(x4 + w4 / 2, y1 + 24, "Зовнішній стан", size=13, color="#7e22ce", bold=True))
    
    state_blocks = [
        ("RDS / DB Proxy", "Пул до SQL (Postgres/MySQL)"),
        ("NoSQL / Key-Value", "DynamoDB, Firestore"),
        ("Розподілений кеш", "Managed Redis / Memcached"),
        ("Черги відповідей", "SQS / SNS / EventBridge"),
        ("Об'єктне сховище", "S3 / GCS для артефактів"),
    ]
    for idx, (stitle, sdesc) in enumerate(state_blocks):
        sy = y1 + 48 + idx * 72
        p.append(rect(x4 + 10, sy, w4 - 20, 60, fill="#ffffff", stroke="#c084fc", sw=1.1, rx=5))
        p.append(text(x4 + w4 / 2, sy + 22, stitle, size=11.5, color=INK, bold=True))
        p.append(text(x4 + w4 / 2, sy + 42, sdesc, size=10, color=MUTED))
    
    render(os.path.join(OUT, "faas-architecture-topology.svg"), W, H, *p,
           title="Топологія FaaS-платформи: від джерела події до ізольованої пісочниці")


def fig_concurrency_scaling_model():
    """Фігура 3: Модель масштабування конкурентності — Моноліт/Сервер проти FaaS."""
    W, H = 960, 430
    p = []
    
    p.append(text(W / 2, 28, "Модель конкурентності: спільний процес проти ізольованих пісочниць FaaS", size=16, color=INK, bold=True))
    
    # ── Ліва панель: Традиційний сервер (Thread pool / Event Loop) ──
    px1 = 24.0
    py = 58.0
    pw = 436.0
    ph = 345.0
    p.append(rect(px1, py, pw, ph, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=8))
    p.append(text(px1 + pw / 2, py + 26, "Традиційний сервер (1 процес = N запитів)", size=13.5, color=INK, bold=True))
    
    proc_y = py + 48
    proc_h = 215.0
    p.append(rect(px1 + 20, proc_y, pw - 40, proc_h, fill="#eff6ff", stroke=NEG, sw=1.3, rx=6))
    p.append(text(px1 + pw / 2, proc_y + 24, "Процес застосунку (JVM / Node.js / Go / Python daemon)", size=11.5, color=NEG, bold=True))
    
    p.append(rect(px1 + 35, proc_y + 38, pw - 70, 42, fill="#ffffff", stroke="#93c5fd", sw=1.1, rx=4))
    p.append(text(px1 + pw / 2, proc_y + 55, "Спільна пам'ять (Heap, Local Cache, DB Connection Pool)", size=10.5, color=INK))
    p.append(text(px1 + pw / 2, proc_y + 70, "1 пул на 20 з'єднань обслуговує 1000 паралельних запитів", size=9.5, color=MUTED))
    
    th_y = proc_y + 90
    for i in range(4):
        tx = px1 + 35 + i * 94
        p.append(rect(tx, th_y, 82, 105, fill="#ffffff", stroke="#60a5fa", sw=1.1, rx=4))
        p.append(text(tx + 41, th_y + 22, f"Потік #{i+1}", size=11, color=NEG, bold=True))
        p.append(text(tx + 41, th_y + 44, "Req " + chr(65 + i), size=10, color=INK))
        p.append(text(tx + 41, th_y + 68, "Socket FD", size=9.5, color=MUTED))
        p.append(text(tx + 41, th_y + 90, "Active", size=9.5, color=FIELD, bold=True))
    
    p.append(text(px1 + pw / 2, py + 285, "• Стан у пам'яті спільний між запитами", size=11, color=INK))
    p.append(text(px1 + pw / 2, py + 305, "• CPU платиться за час роботи процесу (24/7), навіть при простої", size=11, color=MUTED))
    p.append(text(px1 + pw / 2, py + 325, "• База даних захищена стабільним пулом з'єднань", size=11, color=FIELD))
    
    # ── Права панель: FaaS (1 екземпляр = 1 паралельний запит) ──
    px2 = 500.0
    p.append(rect(px2, py, pw, ph, fill="#fdfaf6", stroke="#e8c49e", sw=1.3, rx=8))
    p.append(text(px2 + pw / 2, py + 26, "Безсерверна модель FaaS (1 пісочниця = 1 запит)", size=13.5, color=POS, bold=True))
    
    for i in range(4):
        col = i % 2
        row = i // 2
        sx = px2 + 25 + col * 195
        sy = py + 48 + row * 110
        p.append(rect(sx, sy, 180, 98, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
        p.append(text(sx + 90, sy + 20, f"Пісочниця #{i+1} (MicroVM)", size=11, color=POS, bold=True))
        p.append(text(sx + 90, sy + 40, f"Req {chr(65 + i)} (1 виклик)", size=10.5, color=INK))
        p.append(text(sx + 90, sy + 62, "Окремий DB-клієнт!", size=9.5, color=POS, bold=True))
        p.append(text(sx + 90, sy + 82, "Ізольована пам'ять", size=9.5, color=MUTED))
    
    p.append(text(px2 + pw / 2, py + 285, "• 1000 паралельних запитів = 1000 окремих пісочниць і процесів", size=11, color=POS))
    p.append(text(px2 + pw / 2, py + 305, "• Оплата строго за фактичний час виклику (0 запитів = $0)", size=11, color=FIELD))
    p.append(text(px2 + pw / 2, py + 325, "• Ризик перевантаження БД: потрібен RDS Proxy / PgBouncer", size=11, color=POS))
    
    render(os.path.join(OUT, "concurrency-scaling-model.svg"), W, H, *p,
           title="Модель конкурентності: спільний процес проти ізольованих пісочниць FaaS")


if __name__ == "__main__":
    fig_cold_vs_warm_start()
    fig_faas_architecture_topology()
    fig_concurrency_scaling_model()
    print("Всі фігури згенеровано успішно.")
