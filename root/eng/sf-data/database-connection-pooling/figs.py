# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Порівняння витрат на створення з'єднання та повторне використання ──
def fig_connection_lifecycle_cost():
    W, H = 960, 520
    p = []
    
    # Загальний фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── Верхня частина: Без пулу (нове підключення на кожен запит) ─────────────
    top_y = 30.0
    p.append(rect(24, top_y, W - 48, 215, fill="#fff8f8", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(40, top_y + 24, "Без пулу: накладні витрати на новий запит (20–60 мс)", size=13, color="#b91c1c", bold=True, anchor="start"))
    
    steps_no_pool = [
        ("1. TCP Handshake", "SYN → SYN-ACK → ACK\n1 RTT у мережі\n1.0–5.0 мс", "#fee2e2", "#ef4444"),
        ("2. TLS 1.3 Handshake", "Ключі ECDH + Сертифікат\n1–2 RTT + криптографія\n5.0–15.0 мс", "#fecaca", "#dc2626"),
        ("3. Аутентифікація БД", "SCRAM-SHA-256 / Пароль\nПеревірка прав доступу\n3.0–10.0 мс", "#fca5a5", "#b91c1c"),
        ("4. Ініціалізація бекенду", "fork() процесу / потік\nВиділення пам'яті сесії\n5.0–20.0 мс", "#f87171", "#991b1b"),
        ("5. Виконання запиту", "SELECT / UPDATE даних\nКорисна робота ядра БД\n0.5–2.0 мс", "#dcfce7", "#15803d"),
        ("6. Закриття TCP", "FIN → ACK → TIME_WAIT\nЗвільнення дескриптора\n1.0–3.0 мс", "#fee2e2", "#ef4444")
    ]
    
    bw = 142.0
    bh = 115.0
    gap = 8.0
    sx = 34.0
    sy = top_y + 42.0
    
    for i, (stitle, sdesc, sbg, sstroke) in enumerate(steps_no_pool):
        x = sx + i * (bw + gap)
        p.append(rect(x, sy, bw, bh, fill=sbg, stroke=sstroke, sw=1.5, rx=5))
        p.append(text(x + bw / 2, sy + 22, stitle, size=11, color=sstroke, bold=True))
        lines = sdesc.split("\n")
        p.append(mtext(x + bw / 2, sy + 48, lines, size=10, color=INK, lh=1.35))
        
        if i < len(steps_no_pool) - 1:
            p.append(arrow(x + bw + 1, sy + bh / 2, x + bw + gap - 1, sy + bh / 2, color="#991b1b", sw=1.3))
            
    p.append(text(40, top_y + 195, "Підсумок без пулу: 95% часу і ресурсів процесора спалюється на встановлення зв'язку, а не на запит.", size=11.5, color="#7f1d1d", italic=True, anchor="start"))

    # ── Нижня частина: З пулом (миттєве взяття готового з'єднання) ───────────
    bot_y = 265.0
    p.append(rect(24, bot_y, W - 48, 225, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(40, bot_y + 24, "З пулом з'єднань: повторне використання прогрітих сокетів (0.5–2.1 мс)", size=13, color="#15803d", bold=True, anchor="start"))
    
    steps_pool = [
        ("1. Оренда з пулу", "Взяття з черги пам'яті\nАтомарна операція CAS\n~0.01–0.05 мс", "#dcfce7", "#16a34a"),
        ("2. Швидка валідація", "Перевірка таймштампу\nабо ping по сокету\n~0.01–0.05 мс", "#dcfce7", "#16a34a"),
        ("3. Виконання запиту", "SELECT / UPDATE даних\nКорисна робота ядра БД\n0.5–2.0 мс", "#bbf7d0", "#15803d"),
        ("4. Очищення стану", "Скидання транзакції\nROLLBACK / DISCARD\n~0.02–0.05 мс", "#dcfce7", "#16a34a"),
        ("5. Повернення в пул", "Звільнення дескриптора\nСповіщення очікувача\n~0.01–0.02 мс", "#dcfce7", "#16a34a")
    ]
    
    pbw = 170.0
    pbh = 115.0
    pgap = 12.0
    psx = 34.0
    psy = bot_y + 42.0
    
    for i, (stitle, sdesc, sbg, sstroke) in enumerate(steps_pool):
        x = psx + i * (pbw + pgap)
        p.append(rect(x, psy, pbw, pbh, fill=sbg, stroke=sstroke, sw=1.5, rx=5))
        p.append(text(x + pbw / 2, psy + 22, stitle, size=11.5, color=sstroke, bold=True))
        lines = sdesc.split("\n")
        p.append(mtext(x + pbw / 2, psy + 50, lines, size=10.5, color=INK, lh=1.35))
        
        if i < len(steps_pool) - 1:
            p.append(arrow(x + pbw + 2, psy + pbh / 2, x + pbw + pgap - 2, psy + pbh / 2, color="#15803d", sw=1.4))
            
    p.append(text(40, bot_y + 200, "Підсумок із пулом: нульові системні витрати ядра, захист СУБД від перевантаження та прискорення до 500 разів.", size=11.5, color="#14532d", italic=True, anchor="start"))

    render(os.path.join(OUT, "connection-lifecycle-cost.svg"), W, H, *p)

# ── Фіг. 2: Архітектура та автомат станів пулу з'єднань ─────────────────────────
def fig_pool_architecture_and_state_machine():
    W, H = 960, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Ліва колонка: Архітектура компонентів пулу
    left_w = 440.0
    p.append(rect(24, 25, left_w, 470, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(24 + left_w / 2, 48, "Внутрішня архітектура пулу", size=13.5, color=INK, bold=True))
    
    # Клієнтські потоки
    p.append(rect(44, 70, 400, 52, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=5))
    p.append(text(244, 92, "Клієнтські потоки застосунку (Workers)", size=12, color="#0369a1", bold=True))
    p.append(text(244, 110, "acquire(timeout) / release(connection)", size=10, color=INK))
    
    p.append(arrow(244, 122, 244, 142, color="#0284c7", sw=1.4))
    
    # Черга очікування
    p.append(rect(44, 145, 400, 52, fill="#fffbeb", stroke="#d97706", sw=1.3, rx=5))
    p.append(text(244, 167, "Черга очікування (Waiter Queue / Semaphore)", size=12, color="#b45309", bold=True))
    p.append(text(244, 185, "Блокування очікувачів за дедлайном connectionTimeout", size=10, color=INK))
    
    p.append(arrow(139, 197, 139, 218, color="#10b981", sw=1.4))
    
    # Сховище вільних з'єднань
    p.append(rect(44, 220, 190, 115, fill="#ecfdf5", stroke="#10b981", sw=1.3, rx=5))
    p.append(text(139, 242, "Вільні з'єднання", size=11.5, color="#047857", bold=True))
    p.append(mtext(139, 268, ["Список Idle Connections", "LIFO стек або FIFO черга", "Готові до негайної видачі"], size=9.5, color=INK, lh=1.35))
    
    # Реєстр активних оренд
    p.append(rect(254, 220, 190, 115, fill="#eff6ff", stroke="#3b82f6", sw=1.3, rx=5))
    p.append(text(349, 242, "Активні оренди", size=11.5, color="#1d4ed8", bold=True))
    p.append(mtext(349, 268, ["In-Use / Leased Map", "Фіксація часу оренди", "Детекція витоків (Leak)"], size=9.5, color=INK, lh=1.35))
    
    # Горизонтальні стрілки між Idle та In-Use
    p.append(arrow(234, 260, 252, 260, color="#1d4ed8", sw=1.4))
    p.append(text(244, 250, "оренда", size=9.5, color="#1d4ed8", bold=True))
    
    p.append(arrow(254, 290, 236, 290, color="#047857", sw=1.4))
    p.append(text(244, 304, "повернення", size=9.5, color="#047857", bold=True))
    
    # Фонові потоки обслуговування
    p.append(rect(44, 350, 400, 125, fill="#faf5ff", stroke="#a855f7", sw=1.3, rx=5))
    p.append(text(244, 374, "Фонові демони обслуговування (Housekeeper)", size=12, color="#7e22ce", bold=True))
    p.append(mtext(244, 400, [
        "• Health Check: періодичний ping неактивних сокетів",
        "• Max Lifetime Reaper: закриття застарілих з'єднань",
        "• Connection Scaler: підтримання minIdle та масштабування"
    ], size=10, color=INK, lh=1.4))

    # Права колонка: Автомат станів з'єднання
    right_x = 485.0
    right_w = 450.0
    p.append(rect(right_x, 25, right_w, 470, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(right_x + right_w / 2, 48, "Життєвий цикл стану з'єднання", size=13.5, color=INK, bold=True))
    
    states = [
        ("CREATING", "Створення сокета,\nTLS та аутентифікація", 560, 100, "#fef3c7", "#d97706"),
        ("IDLE", "Очікує в пулі вільних;\nдоступне для оренди", 780, 100, "#dcfce7", "#16a34a"),
        ("BORROWED", "Орендоване потоком;\nвиконує запити клієнта", 780, 250, "#dbeafe", "#2563eb"),
        ("RETURNING", "Скидання стану сесії,\nROLLBACK транзакції", 560, 250, "#e0e7ff", "#4f46e5"),
        ("EVICTED / DEAD", "Таймаут, обрив зв'язку\nабо вичерпання ліміту", 670, 390, "#fee2e2", "#dc2626")
    ]
    
    for sname, sdesc, cx, cy, sbg, sstroke in states:
        box_w = 150.0
        box_h = 60.0
        p.append(rect(cx - box_w / 2, cy - box_h / 2, box_w, box_h, fill=sbg, stroke=sstroke, sw=1.5, rx=6))
        p.append(text(cx, cy - 8, sname, size=11, color=sstroke, bold=True))
        lines = sdesc.split("\n")
        p.append(mtext(cx, cy + 12, lines, size=9.5, color=INK, lh=1.25))
        
    # Переходи між станами
    p.append(arrow(635, 100, 705, 100, color="#16a34a", sw=1.4))
    p.append(text(670, 88, "успіх", size=10, color="#16a34a", bold=True))
    
    p.append(arrow(780, 130, 780, 220, color="#2563eb", sw=1.4))
    p.append(text(830, 175, "borrow()", size=10, color="#2563eb", bold=True))
    
    p.append(arrow(705, 250, 635, 250, color="#4f46e5", sw=1.4))
    p.append(text(670, 238, "release()", size=10, color="#4f46e5", bold=True))
    
    # Стрілка скидання стану RETURNING -> IDLE
    p.append(arrow(560, 220, 710, 125, color="#16a34a", sw=1.4))
    p.append(text(605, 155, "очищено", size=10, color="#16a34a", bold=True))
    
    p.append(arrow(560, 280, 620, 365, color="#dc2626", sw=1.3))
    p.append(arrow(780, 280, 720, 365, color="#dc2626", sw=1.3))
    p.append(arrow(750, 130, 690, 360, color="#dc2626", sw=1.3))
    p.append(text(670, 455, "Закриття дескриптора сокета і знищення об'єкта", size=10, color="#991b1b", italic=True))

    render(os.path.join(OUT, "pool-architecture-and-state-machine.svg"), W, H, *p)

# ── Фіг. 3: Крива закону Літтла та крах продуктивності при перенасиченні ────────
def fig_little_law_saturation_curve():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Координатна сітка графіка
    gx, gy, gw, gh = 80.0, 70.0, 800.0, 330.0
    
    # Зони навантаження
    # Зона 1: Оптимальне масштабування
    p.append(rect(gx, gy, 260, gh, fill="#f0fdf4", stroke="none"))
    p.append(text(gx + 130, gy + 25, "Зона 1: Лінійний ріст", size=11.5, color="#16a34a", bold=True))
    p.append(text(gx + 130, gy + 45, "Pool Size < CPU Cores", size=10, color="#15803d"))
    
    # Зона 2: Точка насичення (Knee)
    p.append(rect(gx + 260, gy, 180, gh, fill="#fefce8", stroke="none"))
    p.append(text(gx + 350, gy + 25, "Зона 2: Оптимум", size=11.5, color="#ca8a04", bold=True))
    p.append(text(gx + 350, gy + 45, "Cores * 2 + Spindles", size=10, color="#a16207"))
    
    # Зона 3: Крах через конкуренцію (Thrashing)
    p.append(rect(gx + 440, gy, 360, gh, fill="#fef2f2", stroke="none"))
    p.append(text(gx + 620, gy + 25, "Зона 3: Деградація (Thrashing / Bottleneck)", size=11.5, color="#dc2626", bold=True))
    p.append(text(gx + 620, gy + 45, "Контекстні перемикання, блокування пам'яті та диска", size=10, color="#991b1b"))

    # Осі координат
    p.append(line(gx, gy + gh, gx + gw + 20, gy + gh, color=LINE, sw=1.8))
    p.append(line(gx, gy + gh, gx, gy - 20, color=LINE, sw=1.8))
    p.append(arrow(gx + gw, gy + gh, gx + gw + 30, gy + gh, color=LINE, sw=2.0))
    p.append(arrow(gx, gy, gx, gy - 30, color=LINE, sw=2.0))
    
    p.append(text(gx + gw + 25, gy + gh + 22, "Розмір пулу з'єднань (Pool Size / Конкурентність)", size=11.5, color=INK, bold=True, anchor="end"))
    p.append(text(gx - 10, gy - 25, "Пропускна здатність (RPS) / Затримка (Latency)", size=11.5, color=INK, bold=True, anchor="start"))
    
    # Пунктирні вертикальні роздільники
    p.append(line(gx + 260, gy, gx + 260, gy + gh, color="#cbd5e1", sw=1.2, dash="4 3"))
    p.append(line(gx + 440, gy, gx + 440, gy + gh, color="#cbd5e1", sw=1.2, dash="4 3"))
    
    # Крива Throughput (Зелена)
    # Зростає від gy+gh-30 до gy+60, плато, потім спадає
    t_points = [
        (gx, gy + gh - 20),
        (gx + 120, gy + gh - 140),
        (gx + 260, gy + 70),
        (gx + 350, gy + 65),
        (gx + 440, gy + 85),
        (gx + 560, gy + 170),
        (gx + 700, gy + 250),
        (gx + 800, gy + 280)
    ]
    t_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in t_points)
    p.append(f'<path d="{t_path}" fill="none" stroke="#16a34a" stroke-width="3.0"/>')
    p.append(circle(gx + 350, gy + 65, 5, fill="#16a34a", stroke="#ffffff", sw=1.5))
    p.append(text(gx + 350, gy + 90, "Пікова пропускна здатність (Max RPS)", size=11, color="#15803d", bold=True))
    
    # Крива Latency (Червона)
    # Низька стабільна, потім після точки насичення стрімко зростає вгору
    l_points = [
        (gx, gy + gh - 40),
        (gx + 120, gy + gh - 45),
        (gx + 260, gy + gh - 55),
        (gx + 350, gy + gh - 75),
        (gx + 440, gy + gh - 130),
        (gx + 560, gy + gh - 220),
        (gx + 700, gy + 50),
        (gx + 800, gy + 30)
    ]
    l_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in l_points)
    p.append(f'<path d="{l_path}" fill="none" stroke="#dc2626" stroke-width="3.0"/>')
    p.append(text(gx + 740, gy + 45, "Експоненційне зростання затримки (L = λW)", size=11, color="#b91c1c", bold=True, anchor="end"))

    # Пояснювальна легенда знизу
    leg_y = gy + gh + 35
    p.append(rect(gx + 100, leg_y, 600, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(line(gx + 120, leg_y + 16, gx + 160, leg_y + 16, color="#16a34a", sw=3.0))
    p.append(text(gx + 170, leg_y + 20, "Пропускна здатність (Throughput)", size=11, color=INK, anchor="start"))
    
    p.append(line(gx + 420, leg_y + 16, gx + 460, leg_y + 16, color="#dc2626", sw=3.0))
    p.append(text(gx + 470, leg_y + 20, "Середня затримка відповіді (Latency)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "little-law-saturation-curve.svg"), W, H, *p)

# ── Фіг. 4: Клієнтський пул проти серверного проксі-пулера ─────────────────────
def fig_client_vs_server_side_pooling():
    W, H = 960, 500
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── Лівий блок: Лише клієнтський пул (Проблема масштабування) ─────────────
    lw = 430.0
    lx = 24.0
    p.append(rect(lx, 25, lw, 450, fill="#fff8f8", stroke="#fca5a5", sw=1.3, rx=6))
    p.append(text(lx + lw / 2, 48, "1. Лише клієнтський пул (In-Process)", size=13, color="#b91c1c", bold=True))
    
    # Застосунки
    p.append(rect(lx + 20, 75, 390, 85, fill="#ffffff", stroke="#f87171", sw=1.2, rx=5))
    p.append(text(lx + lw / 2, 98, "100 подів застосунку (Kubernetes / Сервіси)", size=11.5, color=INK, bold=True))
    p.append(mtext(lx + lw / 2, 120, [
        "Кожен інстанс має власний локальний пул (наприклад, pool_size = 20)",
        "Сумарна кількість підключень: 100 подів * 20 = 2000 TCP-сокетів!"
    ], size=10, color=INK, lh=1.3))
    
    # Стрілка вниз
    p.append(arrow(lx + lw / 2, 165, lx + lw / 2, 270, color="#dc2626", sw=2.0))
    p.append(text(lx + lw / 2 + 10, 215, "2000 постійних\nз'єднань", size=10.5, color="#dc2626", bold=True, anchor="start"))
    
    # База даних з перевантаженням
    p.append(rect(lx + 20, 275, 390, 180, fill="#fee2e2", stroke="#ef4444", sw=1.3, rx=5))
    p.append(text(lx + lw / 2, 300, "Сервер бази даних (PostgreSQL / MySQL)", size=12, color="#991b1b", bold=True))
    p.append(mtext(lx + lw / 2, 330, [
        "• 2000 процесів postgres backend / потоків",
        "• Гігабайти оперативної пам'яті на буфери сесій",
        "• max_connections вичерпано → збої нових клієнтів",
        "• 90% CPU на перемикання контексту ядра",
        "• Висока затримка запитів і ризик падіння СУБД"
    ], size=10, color=INK, lh=1.35))

    # ── Правий блок: Дворівнева архітектура з проксі (PgBouncer / ProxySQL) ────
    rx = 506.0
    rw = 430.0
    p.append(rect(rx, 25, rw, 450, fill="#f0fdf4", stroke="#86efac", sw=1.3, rx=6))
    p.append(text(rx + rw / 2, 48, "2. Дворівневий пулінг із проксі (Server-Side)", size=13, color="#15803d", bold=True))
    
    # Застосунки
    p.append(rect(rx + 20, 75, 390, 85, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=5))
    p.append(text(rx + rw / 2, 98, "100 подів застосунку (Kubernetes / Сервіси)", size=11.5, color=INK, bold=True))
    p.append(mtext(rx + rw / 2, 120, [
        "Легковагі клієнтські з'єднання до проксі",
        "Транзакційний режим пулінгу (Transaction Pooling)"
    ], size=10, color=INK, lh=1.3))
    
    # Стрілка до проксі
    p.append(arrow(rx + rw / 2, 165, rx + rw / 2, 195, color="#16a34a", sw=1.5))
    p.append(text(rx + rw / 2 + 10, 180, "2000 легких клієнтів", size=9.5, color="#15803d", anchor="start"))
    
    # Проміжний проксі-пулер
    p.append(rect(rx + 20, 200, 390, 95, fill="#dcfce7", stroke="#22c55e", sw=1.4, rx=5))
    p.append(text(rx + rw / 2, 224, "Проміжний проксі (PgBouncer / Odyssey / ProxySQL)", size=12, color="#166534", bold=True))
    p.append(mtext(rx + rw / 2, 250, [
        "Мультиплексування: тисячі клієнтів використовують пул",
        "з'єднання закріплюється лише на час транзакції (BEGIN..COMMIT)"
    ], size=10, color=INK, lh=1.3))
    
    # Стрілка від проксі до БД
    p.append(arrow(rx + rw / 2, 300, rx + rw / 2, 335, color="#16a34a", sw=2.0))
    p.append(text(rx + rw / 2 + 10, 318, "50 фізичних сокетів до СУБД", size=9.5, color="#15803d", bold=True, anchor="start"))
    
    # База даних в оптимальному стані
    p.append(rect(rx + 20, 340, 390, 115, fill="#ffffff", stroke="#86efac", sw=1.3, rx=5))
    p.append(text(rx + rw / 2, 364, "Сервер бази даних (Оптимальний режим)", size=12, color="#15803d", bold=True))
    p.append(mtext(rx + rw / 2, 390, [
        "• Рівно 50 активних бекендів під кількість ядер CPU",
        "• Максимальний кеш-хіт L1/L2/L3 процесора",
        "• Нульові накладні витрати на перемикання контексту",
        "• Стабільний p99 час виконання запитів"
    ], size=10, color=INK, lh=1.35))

    render(os.path.join(OUT, "client-vs-server-side-pooling.svg"), W, H, *p)

if __name__ == "__main__":
    fig_connection_lifecycle_cost()
    fig_pool_architecture_and_state_machine()
    fig_little_law_saturation_curve()
    fig_client_vs_server_side_pooling()
    print("All figures successfully generated in", OUT)
