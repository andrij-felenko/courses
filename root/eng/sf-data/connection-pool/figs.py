# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від кореня теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Топологія шва між клієнтом і базою ─────────────────────────────
def fig_seam_topology():
    W, H = 960, 500
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Ліва половина: Внутрішньопроцесний пул (In-Process Pool)
    left_w = 440.0
    p.append(rect(25, 25, left_w, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(25 + left_w / 2, 48, "1. Внутрішньопроцесний пул (HikariCP / r2dbc)", size=13, color=INK, bold=True))

    # Клієнтські ноди
    p.append(rect(45, 75, 400, 150, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    p.append(text(245, 95, "Застосунок (Node / JVM / Pod): 100 процесів", size=11.5, color="#1d4ed8", bold=True))
    
    # Воркери всередині
    for i in range(3):
        x = 55 + i * 130
        p.append(rect(x, 110, 120, 45, fill="#dbeafe", stroke="#60a5fa", sw=1.0, rx=4))
        p.append(text(x + 60, 128, f"Worker Thread #{i+1}", size=10, color="#1e40af", bold=True))
        p.append(text(x + 60, 143, "acquire() / release()", size=9, color="#1e3a8a"))

    # Внутрішній пул
    p.append(rect(55, 168, 380, 45, fill="#bfdbfe", stroke="#2563eb", sw=1.2, rx=4))
    p.append(text(245, 186, "In-Process Connection Pool (10 сокетів на процес)", size=10.5, color="#1e40af", bold=True))
    p.append(text(245, 201, "Сумарно від 100 подів: 100 × 10 = 1000 прямих TCP до СУБД", size=9.5, color="#1e3a8a"))

    p.append(arrow(245, 228, 245, 280, color="#2563eb", sw=1.6))
    p.append(text(255, 258, "1000 TCP-з'єднань", size=9.5, color="#1e40af", bold=True, anchor="start"))

    # База даних ліворуч
    p.append(rect(45, 285, 400, 175, fill="#fef2f2", stroke="#ef4444", sw=1.3, rx=6))
    p.append(text(245, 308, "Кластер СУБД (PostgreSQL / MySQL)", size=12, color="#b91c1c", bold=True))
    p.append(rect(60, 322, 370, 70, fill="#fee2e2", stroke="#f87171", sw=1.0, rx=4))
    p.append(text(245, 342, "1000 бекенд-процесів (fork / threads)", size=11, color="#991b1b", bold=True))
    p.append(text(245, 360, "Пам'ять сесій: 1000 × 10 МБ = 10 ГБ RSS", size=10, color="#7f1d1d"))
    p.append(text(245, 376, "Висока конкуренція за процесорні локи та перемикання контексту", size=9, color="#7f1d1d"))

    p.append(text(245, 412, "Проблема: зростання кількості подів перевантажує СУБД", size=10, color="#b91c1c", bold=True))
    p.append(text(245, 430, "Масштабування застосунку обмежене стелею з'єднань бази", size=9.5, color="#7f1d1d"))

    # Права половина: Багаторівневий пул із зовнішнім проксі
    right_x = 495.0
    p.append(rect(right_x, 25, left_w, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(right_x + left_w / 2, 48, "2. Зовнішній шов (PgBouncer / ProxySQL)", size=13, color=INK, bold=True))

    # Клієнтські ноди праворуч
    p.append(rect(right_x + 20, 75, 400, 100, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    p.append(text(right_x + 220, 95, "5000 клієнтських воркерів (PHP / Python / Node)", size=11.5, color="#1d4ed8", bold=True))
    p.append(text(right_x + 220, 115, "Короткоживучі процеси без великих локальних пулів", size=10, color="#1e3a8a"))
    p.append(text(right_x + 220, 135, "Відкривають легкі TCP-з'єднання до проксі-шару", size=9.5, color="#1e3a8a"))

    p.append(arrow(right_x + 220, 178, right_x + 220, 215, color="#0284c7", sw=1.6))
    p.append(text(right_x + 230, 198, "5000 легких клієнтських сокетів", size=9.5, color="#0369a1", bold=True, anchor="start"))

    # Шар проксі
    p.append(rect(right_x + 20, 218, 400, 105, fill="#f0fdf4", stroke="#16a34a", sw=1.4, rx=6))
    p.append(text(right_x + 220, 238, "Зовнішній проксі-пулер (PgBouncer / ProxySQL)", size=12, color="#15803d", bold=True))
    p.append(text(right_x + 220, 258, "Transaction Pooling: мультиплексування 5000 → 40", size=10.5, color="#166534", bold=True))
    p.append(text(right_x + 220, 276, "Утримання сокета тільки на час активної транзакції", size=9.5, color="#14532d"))
    p.append(text(right_x + 220, 292, "Автоматичне очищення стану (DISCARD / RESET)", size=9.5, color="#14532d"))

    p.append(arrow(right_x + 220, 325, right_x + 220, 360, color="#16a34a", sw=1.6))
    p.append(text(right_x + 230, 345, "Всього 40 стабільних сокетів", size=9.5, color="#15803d", bold=True, anchor="start"))

    # База даних праворуч
    p.append(rect(right_x + 20, 365, 400, 95, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=6))
    p.append(text(right_x + 220, 385, "Кластер СУБД (PostgreSQL / MySQL)", size=12, color="#047857", bold=True))
    p.append(text(right_x + 220, 405, "40 активних бекенд-процесів = 400 МБ пам'яті RSS", size=10.5, color="#065f46", bold=True))
    p.append(text(right_x + 220, 423, "100% CPU витрачається на SQL-обчислення та I/O", size=9.5, color="#064e3b"))
    p.append(text(right_x + 220, 441, "Нульовий оверхед на перемикання контексту ядра ОС", size=9.5, color="#064e3b"))

    render(os.path.join(OUT, "seam-topology-inprocess-vs-proxy.svg"), W, H, *p)

# ── Фігура 2: Гранулярність режимів пулінгу ──────────────────────────────────
def fig_pooling_modes():
    W, H = 960, 480
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 35, "Режими пулінгу: гранулярність захоплення серверного з'єднання в часі", size=14, color=INK, bold=True))

    # Вісь часу зверху
    p.append(line(80, 65, 900, 65, color="#94a3b8", sw=1.5))
    p.append(arrow(880, 65, 915, 65, color="#64748b", sw=1.5))
    p.append(text(920, 69, "Час t", size=11, color="#64748b", anchor="start", italic=True))

    # 1. Session Pooling
    y1 = 85.0
    p.append(rect(25, y1, W - 50, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(40, y1 + 22, "1. Session Pooling (Сесійний режим)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(40, y1 + 40, "З'єднання закріплене за клієнтом на весь життєвий цикл сесії (від connect до disconnect)", size=9.5, color=MUTED, anchor="start"))

    p.append(text(150, y1 + 75, "Клієнт A:", size=10.5, color=INK, bold=True, anchor="end"))
    p.append(rect(160, y1 + 58, 730, 32, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(525, y1 + 78, "Серверне з'єднання зайняте 100% часу (включно з простоями клієнта між запитами)", size=10, color="#334155", bold=True))

    # 2. Transaction Pooling
    y2 = 210.0
    p.append(rect(25, y2, W - 50, 130, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(40, y2 + 22, "2. Transaction Pooling (Транзакційний режим)", size=12, color="#15803d", bold=True, anchor="start"))
    p.append(text(40, y2 + 40, "Серверне з'єднання видається ТІЛЬКИ на час від BEGIN до COMMIT/ROLLBACK", size=9.5, color="#166534", anchor="start"))

    # Серверний сокет 1 обслуговує різних клієнтів по черзі
    p.append(text(150, y2 + 75, "Серверний сокет:", size=10.5, color="#15803d", bold=True, anchor="end"))
    
    # Блоки транзакцій
    p.append(rect(160, y2 + 58, 140, 32, fill="#bbf7d0", stroke="#16a34a", sw=1.3, rx=4))
    p.append(text(230, y2 + 78, "TX 1 (Клієнт A)", size=10, color="#14532d", bold=True))

    p.append(rect(305, y2 + 63, 60, 22, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=3))
    p.append(text(335, y2 + 78, "idle", size=9, color="#64748b", italic=True))

    p.append(rect(370, y2 + 58, 180, 32, fill="#fed7aa", stroke="#f97316", sw=1.3, rx=4))
    p.append(text(460, y2 + 78, "TX 2 (Клієнт B)", size=10, color="#9a3412", bold=True))

    p.append(rect(555, y2 + 63, 50, 22, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=3))
    p.append(text(580, y2 + 78, "idle", size=9, color="#64748b", italic=True))

    p.append(rect(610, y2 + 58, 150, 32, fill="#bfdbfe", stroke="#2563eb", sw=1.3, rx=4))
    p.append(text(685, y2 + 78, "TX 3 (Клієнт C)", size=10, color="#1e3a8a", bold=True))

    p.append(rect(765, y2 + 58, 125, 32, fill="#ddd6fe", stroke="#7c3aed", sw=1.3, rx=4))
    p.append(text(827, y2 + 78, "TX 4 (Клієнт A)", size=10, color="#4c1d95", bold=True))

    p.append(text(40, y2 + 112, "Результат: 1 серверне з'єднання обслуговує десятки активних клієнтів без втрати ізоляції", size=9.5, color="#14532d", bold=True, anchor="start"))

    # 3. Statement Pooling
    y3 = 355.0
    p.append(rect(25, y3, W - 50, 110, fill="#fff7ed", stroke="#fdba74", sw=1.2, rx=6))
    p.append(text(40, y3 + 22, "3. Statement Pooling (Операторний режим)", size=12, color="#c2410c", bold=True, anchor="start"))
    p.append(text(40, y3 + 40, "З'єднання виділяється на 1 SQL-запит (автокоміт). Багатооператорні BEGIN...COMMIT заборонені!", size=9.5, color="#9a3412", anchor="start"))

    p.append(text(150, y3 + 75, "Серверний сокет:", size=10.5, color="#c2410c", bold=True, anchor="end"))
    
    queries = [("Q1 (A)", 160, 60, "#fed7aa", "#ea580c"), ("Q2 (B)", 230, 80, "#bbf7d0", "#16a34a"),
               ("Q3 (C)", 320, 70, "#bfdbfe", "#2563eb"), ("Q4 (A)", 400, 90, "#ddd6fe", "#7c3aed"),
               ("Q5 (D)", 500, 65, "#fbcfe8", "#db2777"), ("Q6 (B)", 575, 110, "#fed7aa", "#ea580c"),
               ("Q7 (E)", 695, 80, "#bbf7d0", "#16a34a"), ("Q8 (C)", 785, 105, "#bfdbfe", "#2563eb")]
    
    for qtitle, qx, qw, qbg, qst in queries:
        p.append(rect(qx, y3 + 58, qw, 32, fill=qbg, stroke=qst, sw=1.1, rx=3))
        p.append(text(qx + qw / 2, y3 + 78, qtitle, size=9.5, color=qst, bold=True))

    render(os.path.join(OUT, "pooling-modes-granularity.svg"), W, H, *p)

# ── Фігура 3: Витік стану сесії та бар'єр очищення ───────────────────────────
def fig_state_leakage():
    W, H = 960, 480
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 35, "Витік сесійного стану при транзакційному мультиплексуванні та бар'єр очищення", size=14, color=INK, bold=True))

    # Ліва частина: Клієнт 1 модифікує стан сесії
    p.append(rect(30, 60, 270, 390, fill="#eff6ff", stroke="#3b82f6", sw=1.3, rx=6))
    p.append(text(165, 85, "Клієнт 1 (Транзакція 1)", size=12, color="#1d4ed8", bold=True))

    ops1 = [
        "BEGIN;",
        "SET timezone = 'America/New_York';",
        "SET work_mem = '128MB';",
        "CREATE TEMP TABLE tmp_cache (...);",
        "PREPARE stmt_find AS SELECT ...;",
        "LISTEN order_events;",
        "COMMIT;"
    ]
    for i, op in enumerate(ops1):
        p.append(rect(45, 110 + i * 42, 240, 32, fill="#dbeafe", stroke="#93c5fd", sw=1.0, rx=4))
        p.append(text(55, 130 + i * 42, op, size=9.5, color="#1e3a8a", anchor="start"))

    p.append(text(165, 425, "З'єднання повертається в пул", size=10, color="#1d4ed8", bold=True))

    # Центральна частина: Бар'єр очищення (PgBouncer / ProxySQL)
    p.append(rect(320, 60, 320, 390, fill="#fef2f2", stroke="#ef4444", sw=1.4, rx=6))
    p.append(text(480, 85, "Шов очищення стану (Sanitization)", size=12, color="#b91c1c", bold=True))

    p.append(rect(335, 110, 290, 85, fill="#fee2e2", stroke="#f87171", sw=1.1, rx=5))
    p.append(text(480, 130, "Без очищення (НЕБЕЗПЕЧНО!):", size=10.5, color="#991b1b", bold=True))
    p.append(text(480, 150, "• Чужий часовий пояс і змінні оточення", size=9.5, color="#7f1d1d"))
    p.append(text(480, 168, "• Завищений work_mem виснажує RAM", size=9.5, color="#7f1d1d"))
    p.append(text(480, 185, "• Тимчасові таблиці видимі іншому клієнту", size=9.5, color="#7f1d1d"))

    # Зелений блок бар'єру
    p.append(rect(335, 210, 290, 220, fill="#f0fdf4", stroke="#16a34a", sw=1.3, rx=5))
    p.append(text(480, 230, "Команди бар'єру скидання стану:", size=11, color="#15803d", bold=True))

    p.append(rect(345, 245, 270, 32, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=3))
    p.append(text(480, 265, "DISCARD ALL  (PostgreSQL)", size=10, color="#14532d", bold=True))

    p.append(rect(345, 285, 270, 32, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=3))
    p.append(text(480, 305, "DISCARD PLANS, TEMP, SEQUENCES", size=9.5, color="#14532d", bold=True))

    p.append(rect(345, 325, 270, 32, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=3))
    p.append(text(480, 345, "RESET ALL; UNLISTEN *;", size=9.5, color="#14532d", bold=True))

    p.append(text(480, 380, "server_reset_query виконується", size=10, color="#166534", bold=True))
    p.append(text(480, 398, "перед передачею сокета клієнту 2", size=9.5, color="#14532d"))
    p.append(text(480, 416, "Гарантує ізоляцію середовища", size=9, color="#166534", italic=True))

    # Права частина: Клієнт 2 отримує чисте з'єднання
    p.append(rect(660, 60, 270, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(795, 85, "Клієнт 2 (Транзакція 2)", size=12, color=INK, bold=True))

    ops2 = [
        "Отримує сокет із пулу",
        "Стан: повністю очищений",
        "Timezone: за замовчуванням",
        "work_mem: 4MB (дефолт)",
        "Temp tables: відсутні",
        "BEGIN;",
        "Виконує чистий запит;"
    ]
    for i, op in enumerate(ops2):
        p.append(rect(675, 110 + i * 42, 240, 32, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(685, 130 + i * 42, op, size=9.5, color=INK, anchor="start"))

    p.append(text(795, 425, "Ізольоване середовище", size=10, color="#15803d", bold=True))

    p.append(arrow(302, 250, 318, 250, color="#2563eb", sw=1.5))
    p.append(arrow(642, 250, 658, 250, color="#16a34a", sw=1.5))

    render(os.path.join(OUT, "state-leakage-and-cleanup.svg"), W, H, *p)

# ── Фігура 4: Крива насичення з'єднань та закон Літтла ────────────────────────
def fig_latency_cliff():
    W, H = 960, 460
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 35, "Крива пропускної здатності та кліф затримки при надлишку з'єднань СУБД", size=14, color=INK, bold=True))

    # Графік
    gx, gy, gw, gh = 80.0, 70.0, 800.0, 320.0
    p.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))

    # Сітка графіка
    for i in range(1, 5):
        y = gy + i * (gh / 5)
        p.append(line(gx, y, gx + gw, y, color="#e2e8f0", sw=1.0, dash="4,4"))

    # Осі
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color="#64748b", sw=1.5))
    p.append(line(gx, gy, gx, gy + gh, color="#64748b", sw=1.5))

    p.append(text(gx + gw - 10, gy + gh + 28, "Кількість одночасних з'єднань (Pool Size / Connections)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(gx - 15, gy + 15, "Throughput (QPS) / Latency (ms)", size=11, color=INK, bold=True, anchor="start"))

    # Оптимальна точка (N_cpu_cores * 2)
    opt_x = gx + 220.0
    p.append(line(opt_x, gy, opt_x, gy + gh, color="#16a34a", sw=1.5, dash="5,3"))
    p.append(rect(opt_x - 70, gy + 10, 140, 36, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(opt_x, gy + 26, "Оптимум пулу (~32)", size=10, color="#14532d", bold=True))
    p.append(text(opt_x, gy + 40, "(CPU cores × 2 + I/O)", size=9, color="#166534"))

    # Крива Throughput (Зелена)
    # Зростає до opt_x, далі падає через thrashing
    t_pts = f"M {gx},{gy+gh} Q {gx+120},{gy+60} {opt_x},{gy+50} Q {gx+450},{gy+70} {gx+gw},{gy+gh-60}"
    p.append(f'<path d="{t_pts}" fill="none" stroke="#16a34a" stroke-width="3"/>')
    p.append(text(gx + 340, gy + 65, "Пропускна здатність (QPS) — пік на оптимумі", size=10.5, color="#15803d", bold=True))

    # Крива Latency (Червона)
    # Низька до opt_x, далі стрімко злітає вгору (кліф)
    l_pts = f"M {gx},{gy+gh-20} Q {opt_x-30},{gy+gh-25} {opt_x},{gy+gh-40} Q {gx+400},{gy+gh-80} {gx+gw-50},{gy+30}"
    p.append(f'<path d="{l_pts}" fill="none" stroke="#dc2626" stroke-width="3"/>')
    p.append(text(gx + 620, gy + 110, "Затримка запиту (Latency Cliff) — вибухове зростання", size=10.5, color="#b91c1c", bold=True))

    # Пояснення зон
    p.append(rect(gx + 20, gy + gh - 90, 160, 55, fill="#f0fdf4", stroke="#86efac", sw=1.0, rx=4))
    p.append(text(gx + 100, gy + gh - 72, "Зона високої", size=10, color="#166534", bold=True))
    p.append(text(gx + 100, gy + gh - 56, "ефективності процесора", size=9.5, color="#14532d"))
    p.append(text(gx + 100, gy + gh - 40, "(Мінімальні черги)", size=9.5, color="#166534", italic=True))

    p.append(rect(gx + gw - 280, gy + gh - 90, 260, 65, fill="#fee2e2", stroke="#fca5a5", sw=1.0, rx=4))
    p.append(text(gx + gw - 150, gy + gh - 72, "Зона перевантаження (Thrashing)", size=10, color="#991b1b", bold=True))
    p.append(text(gx + gw - 150, gy + gh - 56, "Конкуренція за L1/L2 кеші, блокування пам'яті,", size=9, color="#7f1d1d"))
    p.append(text(gx + gw - 150, gy + gh - 40, "перемикання контексту ядра (context switching)", size=9, color="#7f1d1d"))

    # Закон Літтла внизу
    p.append(text(W / 2, H - 20, "Закон Літтла: L = λ × W (довжина черги дорівнює інтенсивності вхідного потоку, помноженій на час очікування)", size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "pool-queue-latency-cliff.svg"), W, H, *p)

if __name__ == "__main__":
    fig_seam_topology()
    fig_pooling_modes()
    fig_state_leakage()
    fig_latency_cliff()
    print("All figures generated successfully.")
