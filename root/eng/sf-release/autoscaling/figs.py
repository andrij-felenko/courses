# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Контур зворотного зв'язку автоскейлу ──────────────────────────────
def fig_autoscaling_control_loop():
    W, H = 980, 520
    p = []
    
    # Загальний фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок зверху
    p.append(text(W / 2, 36, "Контур зворотного зв'язку автоматичного масштабування (Autoscaling Control Loop)", size=15, color=INK, bold=True))
    
    box_w, box_h = 210, 110
    
    # Крок 1: Джерела метрик
    x1, y1 = 40, 70
    p.append(rect(x1, y1, box_w, box_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(x1 + box_w / 2, y1 + 24, "1. Збір показників", size=13, color="#2563eb", bold=True))
    p.append(mtext(x1 + box_w / 2, y1 + 50, [
        "CPU / Memory (cgroups)",
        "RPS / In-flight (Ingress)",
        "Довжина черги (Kafka/SQS)"
    ], size=11, color=INK, lh=1.35))
    
    # Крок 2: Згладжування та обчислення цілі (праворуч вгорі)
    x2, y2 = 380, 70
    p.append(rect(x2, y2, box_w, box_h, fill="#fdf4ff", stroke="#c026d3", sw=1.6, rx=6))
    p.append(text(x2 + box_w / 2, y2 + 24, "2. Оцінка формули", size=13, color="#c026d3", bold=True))
    p.append(mtext(x2 + box_w / 2, y2 + 50, [
        "Експоненційне згладжування",
        "Ціль: ceil[N · (M_curr / M_target)]",
        "Зона нечутливості (±10%)"
    ], size=11, color=INK, lh=1.35))
    
    # Крок 3: Фільтри та обмеження (праворуч внизу)
    x3, y3 = 720, 70
    p.append(rect(x3, y3, box_w, box_h, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(x3 + box_w / 2, y3 + 24, "3. Захисні бар'єри", size=13, color="#d97706", bold=True))
    p.append(mtext(x3 + box_w / 2, y3 + 50, [
        "Межі: [MinReplicas, MaxReplicas]",
        "Вікно стабілізації (Cooldown)",
        "Ліміт швидкості зміни (Rate limit)"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілки верхнього ряду
    p.append(arrow(x1 + box_w + 5, y1 + box_h / 2, x2 - 5, y1 + box_h / 2, color=LINE, sw=1.8))
    p.append(text((x1 + box_w + x2) / 2, y1 + box_h / 2 - 10, "Телеметрія", size=10.5, color=MUTED))
    
    p.append(arrow(x2 + box_w + 5, y2 + box_h / 2, x3 - 5, y2 + box_h / 2, color=LINE, sw=1.8))
    p.append(text((x2 + box_w + x3) / 2, y2 + box_h / 2 - 10, "Бажаний N", size=10.5, color=MUTED))
    
    # Крок 4: Виконання в оркестраторі (нижній правий)
    x4, y4 = 720, 270
    p.append(rect(x4, y4, box_w, box_h, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(x4 + box_w / 2, y4 + 24, "4. Оркестрація змін", size=13, color="#059669", bold=True))
    p.append(mtext(x4 + box_w / 2, y4 + 50, [
        "API Server (Scale deployment)",
        "Provisioning / Deprovisioning",
        "Graceful drain старих подів"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка вниз 3 -> 4
    p.append(arrow(x3 + box_w / 2, y3 + box_h + 5, x4 + box_w / 2, y4 - 5, color=LINE, sw=1.8))
    p.append(text(x3 + box_w / 2 + 65, (y3 + box_h + y4) / 2, "Затверджений N", size=10.5, color=MUTED))
    
    # Крок 5: Інфраструктура та навантаження (нижній центр)
    x5, y5 = 380, 270
    p.append(rect(x5, y5, box_w, box_h, fill="#f8fafc", stroke="#475569", sw=1.6, rx=6))
    p.append(text(x5 + box_w / 2, y5 + 24, "5. Пул обчислень", size=13, color="#475569", bold=True))
    p.append(mtext(x5 + box_w / 2, y5 + 50, [
        "Нові екземпляри прогріваються",
        "Балансувальник додає IP в пул",
        "Навантаження на вузол падає"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка вліво 4 -> 5
    p.append(arrow(x4 - 5, y4 + box_h / 2, x5 + box_w + 5, y4 + box_h / 2, color=LINE, sw=1.8))
    p.append(text((x4 + x5 + box_w) / 2, y4 + box_h / 2 - 10, "Запуск / Стоп", size=10.5, color=MUTED))
    
    # Крок 6: Зовнішнє навантаження (нижній лівий)
    x6, y6 = 40, 270
    p.append(rect(x6, y6, box_w, box_h, fill="#fef2f2", stroke="#dc2626", sw=1.6, rx=6))
    p.append(text(x6 + box_w / 2, y6 + 24, "6. Вхідний трафік", size=13, color="#dc2626", bold=True))
    p.append(mtext(x6 + box_w / 2, y6 + 50, [
        "Динамічний потік клієнтів",
        "Розподіл по здорових репліках",
        "Зміна навантаження на ядро"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка вліво 5 -> 6
    p.append(arrow(x5 - 5, y5 + box_h / 2, x6 + box_w + 5, y6 + box_h / 2, color=LINE, sw=1.8))
    p.append(text((x5 + x6 + box_w) / 2, y5 + box_h / 2 - 10, "Розподіл запитів", size=10.5, color=MUTED))
    
    # Стрілка вгору 6 -> 1 (замикання циклу)
    p.append(arrow(x6 + box_w / 2, y6 - 5, x1 + box_w / 2, y1 + box_h + 5, color="#2563eb", sw=2.0))
    p.append(text(x6 + box_w / 2 - 75, (y1 + box_h + y6) / 2, "Новий стан", size=11, color="#2563eb", bold=True))
    
    # Нижня інформаційна плашка
    p.append(rect(30, 415, W - 60, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(48, 440, "Ключові інваріанти надійного контуру:", size=12.5, color=INK, bold=True, anchor="start"))
    p.append(text(48, 462, "• Період зняття метрик (15-30 с) задає мінімальну затримку виявлення сплеску", size=11.5, color=MUTED, anchor="start"))
    p.append(text(48, 482, "• Згладжування та гістерезис захищають від флапінгу при коротких імпульсах навантаження", size=11.5, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "autoscaling-control-loop.svg"), W, H, *p)

# ── Фіг. 2: Флапінг проти гістерезису та вікон стабілізації ───────────────────
def fig_flapping_and_hysteresis():
    W, H = 980, 530
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── ВЕРХНЯ ПОЛОВИНА: Наївний пороговий регулятор (Флапінг) ─────────────────
    top_y = 30
    p.append(rect(25, top_y, W - 50, 220, fill="#fff5f5", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(45, top_y + 24, "1. Наївний поріг без гістерезису: постійний «флапінг» (thrashing)", size=13, color="#b91c1c", bold=True, anchor="start"))
    
    # Графік навантаження та кількості реплік
    gx, gy, gw, gh = 50, top_y + 42, 520, 155
    p.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    
    # Поріг 70% CPU
    thresh_y = gy + gh * 0.42
    p.append(line(gx, thresh_y, gx + gw, thresh_y, color="#dc2626", sw=1.5, dash="5 4"))
    p.append(text(gx + gw - 12, thresh_y - 8, "Жорсткий поріг (70% CPU)", size=10.5, color="#dc2626", bold=True, anchor="end"))
    
    # Коливальна крива метрики
    pts = [
        (gx + 10, gy + 115), (gx + 60, gy + 85), (gx + 100, gy + 40),
        (gx + 140, gy + 125),
        (gx + 180, gy + 130),
        (gx + 220, gy + 35),
        (gx + 260, gy + 125),
        (gx + 300, gy + 30),
        (gx + 340, gy + 120),
        (gx + 390, gy + 35),
        (gx + 440, gy + 125),
        (gx + 500, gy + 50)
    ]
    path_d = ["M %.1f %.1f" % pts[0]]
    for x, y in pts[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.2"/>' % " ".join(path_d))
    p.append(text(gx + 70, gy + 20, "Метрика CPU", size=11, color="#2563eb", bold=True))
    
    # Права панель наслідків
    px = 600
    p.append(rect(px, top_y + 42, 335, gh, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    p.append(text(px + 15, top_y + 68, "Наслідки для продакшну:", size=12, color="#b91c1c", bold=True, anchor="start"))
    p.append(text(px + 15, top_y + 92, "• Репліки створюються і вбиваються щохвилини", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, top_y + 114, "• Процесор витрачається на старт контейнерів і JVM", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, top_y + 136, "• Розриви з'єднань і сплески 502/504 помилок", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, top_y + 158, "• Перевантаження реєстру образів та API-сервера", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, top_y + 180, "• Цілковита нестабільність розподілу трафіку", size=11, color="#b91c1c", bold=True, anchor="start"))
    
    # ── НИЖНЯ ПОЛОВИНА: Гістерезис та вікно стабілізації ────────────────────────
    bot_y = 270
    p.append(rect(25, bot_y, W - 50, 235, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(45, bot_y + 24, "2. Стійкий регулятор: зона нечутливості (Deadband) + асиметричний Cooldown", size=13, color="#15803d", bold=True, anchor="start"))
    
    b_gx, b_gy, b_gw, b_gh = 50, bot_y + 42, 520, 168
    p.append(rect(b_gx, b_gy, b_gw, b_gh, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    
    # Зона нечутливості (Deadband 60% - 80%)
    band_top = b_gy + b_gh * 0.28
    band_bot = b_gy + b_gh * 0.65
    p.append(rect(b_gx, band_top, b_gw, band_bot - band_top, fill="#ecfdf5", stroke="#86efac", sw=0.8))
    
    p.append(line(b_gx, band_top, b_gx + b_gw, band_top, color="#d97706", sw=1.2, dash="4 3"))
    p.append(line(b_gx, band_bot, b_gx + b_gw, band_bot, color="#059669", sw=1.2, dash="4 3"))
    p.append(text(b_gx + b_gw - 12, band_top - 6, "Верхня межа: Scale-up (> 80%)", size=9.5, color="#d97706", bold=True, anchor="end"))
    p.append(text(b_gx + b_gw - 12, band_bot + 14, "Нижня межа: Scale-down (< 60%)", size=9.5, color="#059669", bold=True, anchor="end"))
    
    # Плавна крива метрики та збереження стабільності (зміщуємо y щоб не перетинати написи)
    b_pts = [
        (b_gx + 10, b_gy + 115), (b_gx + 60, b_gy + 75), (b_gx + 110, b_gy + 35),
        (b_gx + 160, b_gy + 88),
        (b_gx + 220, b_gy + 98),
        (b_gx + 280, b_gy + 82),
        (b_gx + 340, b_gy + 92),
        (b_gx + 400, b_gy + 140),
        (b_gx + 460, b_gy + 145),
        (b_gx + 510, b_gy + 95)
    ]
    b_path_d = ["M %.1f %.1f" % b_pts[0]]
    for x, y in b_pts[1:]:
        b_path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.2"/>' % " ".join(b_path_d))
    p.append(text(b_gx + 12, b_gy + 20, "Метрика CPU", size=11, color="#2563eb", bold=True, anchor="start"))
    p.append(text(b_gx + 150, b_gy + 20, "Зона спокою: коливання 60–80% не чіпають пул", size=10.5, color="#15803d", bold=True, anchor="start"))
    
    # Права панель механізму
    p.append(rect(px, bot_y + 42, 335, b_gh, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(px + 15, bot_y + 68, "Механізм захисту регулятора:", size=12, color="#15803d", bold=True, anchor="start"))
    p.append(text(px + 15, bot_y + 92, "• Deadband: коливання всередині зони не чіпають пул", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, bot_y + 114, "• Scale-up: миттєвий крок (cooldown = 0-15 с)", size=11, color="#b91c1c", bold=True, anchor="start"))
    p.append(text(px + 15, bot_y + 136, "• Scale-down window: чекає 300 с стабільно низької метрики", size=11, color="#15803d", bold=True, anchor="start"))
    p.append(text(px + 15, bot_y + 158, "• Обмеження кроку: не більше ніж -10% реплік за хвилину", size=11, color=INK, anchor="start"))
    p.append(text(px + 15, bot_y + 180, "• Плавний дренаж: активні запити добігають штатно", size=11, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "flapping-and-hysteresis.svg"), W, H, *p)

# ── Фіг. 3: Анатомія часової затримки реакції (Scale-up Lag) ──────────────────
def fig_scale_up_lag_timeline():
    W, H = 980, 510
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    p.append(text(W / 2, 34, "Анатомія затримки масштабування: чому новий сервер з'являється лише через 2-5 хвилин", size=14, color=INK, bold=True))
    
    # 5 послідовних етапів у часі
    stages = [
        ("1. Збір метрик", "Scrape interval метрик\nЗатримка TSDB-буфера", "0–30 с", "#eff6ff", "#2563eb"),
        ("2. Рішення HPA", "Період sync-period\nОбчислення цілі за формулою", "30–45 с", "#fdf4ff", "#c026d3"),
        ("3. Планування й ВМ", "Пошук / замовлення ВМ\nCluster Autoscaler / Karpenter", "45–135 с", "#fffbeb", "#d97706"),
        ("4. Старт і прогрів", "Image pull, запуск контейнера\nПрогрів JIT і пулів з'єднань", "135–210 с", "#f0fdf4", "#16a34a"),
        ("5. Реєстрація в LB", "Readiness probe = OK\nПідключення до Ingress", "210–240 с", "#ecfdf5", "#059669")
    ]
    
    box_w = 172.0
    box_h = 135.0
    gap = 16.0
    start_x = 24.0
    y_pos = 70.0
    
    # Вісь часу
    axis_y = 265.0
    p.append(line(30, axis_y, W - 40, axis_y, color=LINE, sw=1.8))
    p.append(arrow(W - 70, axis_y, W - 30, axis_y, color=LINE, sw=2.0))
    p.append(text(W - 35, axis_y + 18, "Час після стрибка →", size=11, color=INK, bold=True, anchor="end"))
    
    for i, (title_txt, desc_txt, time_txt, bg_col, stroke_col) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        
        p.append(rect(x, y_pos, box_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        p.append(text(x + box_w / 2, y_pos + 22, title_txt, size=12.5, color=stroke_col, bold=True))
        
        # Плашка часу
        p.append(rect(x + box_w / 2 - 38, y_pos + 36, 76, 20, fill="#ffffff", stroke=stroke_col, sw=1.0, rx=4))
        p.append(text(x + box_w / 2, y_pos + 50, time_txt, size=11, color=stroke_col, bold=True))
        
        lines = desc_txt.split("\n")
        p.append(mtext(x + box_w / 2, y_pos + 78, lines, size=10.5, color=INK, lh=1.35))
        
        # Зв'язок з віссю часу
        cx = x + box_w / 2
        p.append(line(cx, y_pos + box_h, cx, axis_y, color=stroke_col, sw=1.2, dash="4 3"))
        p.append(circle(cx, axis_y, 4.5, fill=stroke_col, stroke="#ffffff", sw=1.5))
        
        if i < len(stages) - 1:
            next_x = start_x + (i + 1) * (box_w + gap)
            p.append(arrow(x + box_w + 2, y_pos + box_h / 2, next_x - 2, y_pos + box_h / 2, color=LINE, sw=1.4))
            
    # Нижня частина: Небезпечна зона (Headroom gap) та захист
    pan_y = 300.0
    pan_h = 185.0
    p.append(rect(24, pan_y, W - 48, pan_h, fill="#fff5f5", stroke="#fca5a5", sw=1.4, rx=6))
    
    p.append(text(42, pan_y + 26, "Критична «сліпа зона» затримки (0–240 секунд) і способи виживання:", size=13, color="#b91c1c", bold=True, anchor="start"))
    
    p.append(circle(48, pan_y + 56, 4, fill="#b91c1c", stroke="#b91c1c", sw=1))
    p.append(text(64, pan_y + 60, "Проблема: Стрибок трафіку навантажує існуючі екземпляри на 100% ДО того, як новий сервер прийме запит.", size=11.5, color=INK, anchor="start"))
    
    p.append(circle(48, pan_y + 90, 4, fill="#15803d", stroke="#15803d", sw=1))
    p.append(text(64, pan_y + 94, "Захист 1 (Headroom): Тримати постійний резерв (ціль CPU 60-70%, а не 90%), щоб поглинути сплеск перших 2 хвилин.", size=11.5, color=INK, anchor="start"))
    
    p.append(circle(48, pan_y + 124, 4, fill="#15803d", stroke="#15803d", sw=1))
    p.append(text(64, pan_y + 128, "Захист 2 (Rate Limiting): Швидке відсікання надлишку (HTTP 429), що рятує живі репліки від деградації та відмов.", size=11.5, color=INK, anchor="start"))
    
    p.append(circle(48, pan_y + 158, 4, fill="#15803d", stroke="#15803d", sw=1))
    p.append(text(64, pan_y + 162, "Захист 3 (Предиктивність): Розкладний автоскейл перед відомими подіями та попередній прогрів контейнерів.", size=11.5, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "scale-up-lag-timeline.svg"), W, H, *p)

# ── Фіг. 4: Масштабування обробників черги (Queue-driven autoscaling) ──────────
def fig_queue_worker_autoscaling():
    W, H = 980, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 34, "Масштабування асинхронних обробників за глибиною черги (Event/Queue-driven)", size=14, color=INK, bold=True))
    
    # Ліва частина: Продюсери та черга повідомлень
    p.append(rect(30, 65, 260, 200, fill="#eff6ff", stroke="#3b82f6", sw=1.4, rx=6))
    p.append(text(160, 90, "1. Джерело подій / Черга", size=13, color="#2563eb", bold=True))
    
    p.append(rect(50, 110, 220, 65, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(160, 130, "Kafka Lag / SQS Backlog", size=12, color=INK, bold=True))
    p.append(text(160, 152, "L = 45 000 повідомлень", size=12.5, color="#dc2626", bold=True))
    
    p.append(text(160, 195, "Швидкість приходу: λ = 500 msg/s", size=11, color=MUTED))
    p.append(text(160, 215, "Дедлайн обробки: T_target = 60 s", size=11, color=MUTED))
    p.append(text(160, 245, "Час обробки 1 задачі: t_task = 0.2 s", size=11, color=MUTED))
    
    # Центральна частина: Контролер автоскейлу KEDA / Custom
    p.append(rect(340, 65, 300, 200, fill="#fdf4ff", stroke="#c026d3", sw=1.4, rx=6))
    p.append(text(490, 90, "2. Контролер черги (KEDA / HPA)", size=13, color="#c026d3", bold=True))
    
    p.append(rect(360, 110, 260, 80, fill="#ffffff", stroke="#f0abfc", sw=1.2, rx=4))
    p.append(text(490, 130, "Формула розрахунку воркерів:", size=11.5, color=MUTED))
    p.append(text(490, 152, "N = ceil( L · t_task / T_target )", size=13, color="#c026d3", bold=True))
    p.append(text(490, 175, "N = ceil( 45000 · 0.2 / 60 ) = 150", size=12, color="#059669", bold=True))
    
    p.append(text(490, 215, "Scale-to-Zero: якщо L = 0 → N = 0", size=11.5, color="#2563eb", bold=True))
    p.append(text(490, 240, "Захист БД: N ≤ MaxWorkers (200)", size=11.5, color="#d97706", bold=True))
    
    # Права частина: Пул воркерів
    p.append(rect(690, 65, 260, 200, fill="#ecfdf5", stroke="#10b981", sw=1.4, rx=6))
    p.append(text(820, 90, "3. Пул воркерів (Workers)", size=13, color="#059669", bold=True))
    
    # Іконки воркерів
    wx, wy = 715, 115
    for row in range(3):
        for col in range(4):
            cur_x = wx + col * 55
            cur_y = wy + row * 40
            p.append(rect(cur_x, cur_y, 45, 30, fill="#ffffff", stroke="#34d399", sw=1.2, rx=4))
            p.append(text(cur_x + 22.5, cur_y + 19, "W%d" % (row * 4 + col + 1), size=10.5, color="#059669", bold=True))
            
    p.append(text(820, 245, "Пропускна здатність: 750 msg/s", size=11.5, color="#059669", bold=True))
    
    # Стрілки між блоками
    p.append(arrow(293, 165, 337, 165, color=LINE, sw=1.8))
    p.append(arrow(643, 165, 687, 165, color=LINE, sw=1.8))
    
    # Нижня частина: Порівняння підходів
    pan_y = 290.0
    pan_h = 165.0
    p.append(rect(30, pan_y, W - 60, pan_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(48, pan_y + 24, "Чому метрика CPU не працює для черг, а довжина черги (Lag) — працює:", size=12.5, color=INK, bold=True, anchor="start"))
    
    rows = [
        ("Проблема CPU для воркерів:", "Якщо є 2 воркери і 1 000 000 задач, обидва завантажені на 100% CPU. Завантаження не каже, чи треба 3 воркери, чи 500.", "#dc2626"),
        ("Перевага довжини черги (Lag):", "Кількість задач у черзі точно вказує обсяг накопиченої роботи. Формула дає точну кількість воркерів під SLA.", "#059669"),
        ("Масштабування до нуля (Scale-to-Zero):", "Коли черга порожня, можна зупинити всі воркери (N=0) і заощадити 100% вартості compute.", "#2563eb"),
        ("Захист від перевантаження сховища:", "Якщо воркери пишуть в один PostgreSQL, ліміт maxReplicas рятує базу від загибелі під час сплеску.", "#d97706"),
    ]
    
    ry = pan_y + 50
    for label_txt, desc_txt, col in rows:
        p.append(circle(52, ry, 3.5, fill=col, stroke=col, sw=1.0))
        p.append(text(66, ry + 4, label_txt, size=11.5, color=col, bold=True, anchor="start"))
        p.append(text(340, ry + 4, desc_txt, size=11.5, color=INK, anchor="start"))
        ry += 26
        
    render(os.path.join(OUT, "queue-worker-autoscaling.svg"), W, H, *p)

if __name__ == "__main__":
    fig_autoscaling_control_loop()
    fig_flapping_and_hysteresis()
    fig_scale_up_lag_timeline()
    fig_queue_worker_autoscaling()
    print("Всі фігури згенеровано успішно.")
