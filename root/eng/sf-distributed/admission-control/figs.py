# -*- coding: utf-8 -*-
"""Фігури до теми «Контроль допуску: збереження корисної пропускної здатності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # перевантаження / відмова / небезпека
COOL = "#eaf0fd"   # нейтральне / схема
GOOD = "#e8f6ee"   # корисна робота / успіх
ACCENT = "#fbf4db" # попередження / проміжний стан


# ── 1. Сира пропускна здатність проти корисної (Throughput vs Goodput) ──────
def throughput_vs_goodput():
    W, H = 1180, 680
    f = []

    xa, xb = 140.0, 1100.0
    ya, yb = 100.0, 530.0

    # Осі координат
    f.append(line(xa, yb, xb, yb, color=INK, sw=2.0))
    f.append(line(xa, ya, xa, yb, color=INK, sw=2.0))
    f.append(text(xb, yb + 38, "Вхідний потік запитів λ (RPS) →", size=13.5, color=INK, anchor="end", bold=True))
    f.append(text(xa - 14, ya - 20, "Пропускна здатність (RPS)", size=13.5, color=INK, anchor="start", bold=True))

    # Сітка та критична точка μ
    x_sat = 520.0
    y_sat = 260.0

    f.append(line(xa, y_sat, xb, y_sat, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(xa - 12, y_sat + 5, "Границя стійкості μ (100% CPU)", size=12.5, color=MUTED, anchor="end", bold=True))

    f.append(line(x_sat, ya, x_sat, yb, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(x_sat, yb + 24, "Точка насичення (λ = μ)", size=12.5, color=MUTED, bold=True))

    # Зони: нормальна робота vs перевантаження
    f.append(rect(xa + 1, ya, x_sat - xa, yb - ya, fill="#f8fafc", stroke="none"))
    f.append(rect(x_sat, ya, xb - x_sat, yb - ya, fill="#fef8f8", stroke="none"))
    f.append(text((xa + x_sat) / 2, ya + 30, "Штатний режим (λ < μ)", size=13, color=FIELD, bold=True))
    f.append(text((x_sat + xb) / 2, ya + 30, "Зона перевантаження (λ > μ)", size=13, color=POS, bold=True))

    # Лінія запропонованого навантаження (Offered Load: y = x)
    f.append(line(xa, yb, 680.0, ya + 40, color="#94a3b8", sw=1.8, dash="4,4"))
    f.append(text(460.0, ya + 140, "Вхідний потік (Offered load)", size=12, color="#64748b", italic=True))

    # Крива 1: З контролем допуску (Goodput зрізається на рівні μ)
    f.append(line(xa, yb, x_sat, y_sat, color=FIELD, sw=3.5))
    f.append(line(x_sat, y_sat, xb - 40, y_sat, color=FIELD, sw=3.5))
    f.append(circle(x_sat, y_sat, 6, fill=GOOD, stroke=FIELD, sw=2.5))
    f.append(fitbox(x_sat + 20, y_sat - 80, 280, 48,
                    "З контролем допуску:\nGoodput стабільний на максимумі μ",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))

    # Крива 2: Без контролю допуску (Колапс корисної роботи)
    pts_collapse = [
        (xa, yb),
        (x_sat, y_sat),
        (x_sat + 90, y_sat + 20),
        (x_sat + 180, y_sat + 90),
        (x_sat + 280, y_sat + 190),
        (x_sat + 400, yb - 20),
        (xb - 40, yb - 10)
    ]
    for i in range(len(pts_collapse) - 1):
        f.append(line(pts_collapse[i][0], pts_collapse[i][1],
                      pts_collapse[i+1][0], pts_collapse[i+1][1],
                      color=POS, sw=3.5, dash="7,4"))

    f.append(fitbox(x_sat + 160, y_sat + 120, 360, 68,
                    "Без контролю допуску:\nчерги вибухають, таймаути спливають,\nGoodput падає майже до 0 (марна праця)",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Стрілка різниці — відкинуті запити
    x_shed = 980.0
    f.append(line(x_shed, y_sat + 10, x_shed, ya + 60, color=NEG, sw=2.0))
    f.append(arrow(x_shed, ya + 100, x_shed, ya + 50, color=NEG))
    f.append(arrow(x_shed, ya + 100, x_shed, y_sat + 5, color=NEG))
    f.append(fitbox(880, ya + 30, 180, 52,
                    "Раннє скидання:\nшвидкі 429/503\nбез затрат CPU",
                    size=11.5, bold=True, fill=COOL, stroke=NEG, sw=1.5))

    # Підсумковий блок
    f.append(fitbox(xa, 580, xb - xa, 70,
                    "Головне правило стійкості: краще успішно обслужити 1000 запитів/с і 4000 відхилити на вході,\n"
                    "ніж прийняти всі 5000, забити пули потоків і завершити 0 через спливання клієнтських дедлайнів.",
                    size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'throughput-vs-goodput.svg'), W, H, *f)


# ── 2. Конвеєр ухвалення рішення про допуск (Admission Pipeline) ────────────
def admission_pipeline():
    W, H = 1220, 690
    f = []

    # Початок: вхідний запит
    x_in = 60.0
    f.append(fitbox(x_in, 260, 160, 110,
                    "ВХІДНИЙ ЗАПИТ\n\n- Пріоритет\n- Дедлайн (TTL)\n- Ідентифікатор",
                    size=12.5, bold=True, fill=COOL, stroke=LINE, sw=1.6))

    # Стрілка до фільтра 1
    f.append(arrow(x_in + 160, 315, x_in + 215, 315, color=LINE, sw=2.0))

    # Етап 1: Перевірка квот і пріоритетів
    x_s1 = 220.0
    f.append(fitbox(x_s1, 230, 200, 170,
                    "1. КЛАСИФІКАЦІЯ\nІ ПРІОРИТЕТ\n\nКритичний / Звичайний / Фоновий трафік;\nКвоти споживачів",
                    size=12.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))

    # Відсікання на етапі 1 (фоновий скидається при дефіциті)
    f.append(arrow(x_s1 + 80, 400, x_s1 + 80, 510, color=POS, sw=2.0))
    f.append(mtext(x_s1 + 95, 450, ["Низький пріоритет", "при стресі"], size=11, color=POS, bold=True, anchor="start"))

    # Стрілка від 1 до 2
    f.append(arrow(x_s1 + 200, 315, x_s1 + 260, 315, color=FIELD, sw=2.0))

    # Етап 2: Перевірка віку в черзі (Sojourn Time Gate)
    x_s2 = 485.0
    f.append(fitbox(x_s2, 230, 210, 170,
                    "2. ЧАС ОЧІКУВАННЯ\n(Sojourn Time)\n\nЧи встигне запис\nдо дедлайну клієнта?\nT_wait + T_exec < T_ttl",
                    size=12.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))

    # Відсікання на етапі 2 (просрочений у черзі)
    f.append(arrow(x_s2 + 80, 400, x_s2 + 80, 510, color=POS, sw=2.0))
    f.append(mtext(x_s2 + 95, 450, ["Очікування > TTL", "(запізно)"], size=11, color=POS, bold=True, anchor="start"))

    # Стрілка від 2 до 3
    f.append(arrow(x_s2 + 210, 315, x_s2 + 270, 315, color=FIELD, sw=2.0))

    # Етап 3: Лімітер паралелізму (Adaptive Concurrency Limiter)
    x_s3 = 760.0
    f.append(fitbox(x_s3, 230, 210, 170,
                    "3. ЛІМІТ ПОТОКІВ\n(In-flight Limiter)\n\nАктивних запитів < L_limit\n(Vegas / Gradient / AIMD)",
                    size=12.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))

    # Відсікання на етапі 3 (пул зайнятий)
    f.append(arrow(x_s3 + 80, 400, x_s3 + 80, 510, color=POS, sw=2.0))
    f.append(mtext(x_s3 + 95, 450, ["Пул переповнено", "(In-flight ≥ L)"], size=11, color=POS, bold=True, anchor="start"))

    # Стрілка до успішного виконання
    f.append(arrow(x_s3 + 210, 315, x_s3 + 275, 315, color=FIELD, sw=2.5))

    # Результат А: Допущено до виконання
    x_ok = 1040.0
    f.append(fitbox(x_ok, 245, 150, 140,
                    "ДОПУСК (Admit)\n\nВиділення потоку,\nробота з базою,\nуспішна відповідь 200 OK",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=2.0))

    # Результат Б: Швидка відмова (Fast Rejection)
    y_rej = 515.0
    f.append(fitbox(220, y_rej, 750, 80,
                    "РАННЯ ВІДМОВА (Fast Drop):\n"
                    "HTTP 429 Too Many Requests / 503 Unavailable / gRPC RESOURCE_EXHAUSTED\n"
                    "Заголовок Retry-After + випадковий джитер. Витрати ресурсів процесора ≈ 0.",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Зворотний зв'язок: Метрики затримки оновлюють ліміт L
    f.append(line(x_ok + 75, 245, x_ok + 75, 110, color=MUTED, sw=1.8))
    f.append(line(x_ok + 75, 110, x_s3 + 105, 110, color=MUTED, sw=1.8))
    f.append(arrow(x_s3 + 105, 110, x_s3 + 105, 225, color=MUTED, sw=1.8))
    f.append(fitbox(x_s3 - 60, 70, 330, 60,
                    "Зворотний зв'язок (Feedback loop):\nзатримка RTT і черги динамічно змінюють ліміт L",
                    size=11.5, bold=True, fill=COOL, stroke=MUTED, sw=1.3))

    # Загальний підпис знизу
    f.append(fitbox(60, 615, 1130, 55,
                    "Контролер допуску працює як багатошаровий фільтр перед ресурсоємним ядром сервісу,\n"
                    "відсікаючи приречені та надлишкові запити до виділення пам'яті та потоків виконання.",
                    size=13, fill=FILL, stroke=MUTED, sw=1.3))

    render(os.path.join(OUT, 'admission-pipeline.svg'), W, H, *f)


# ── 3. Провал у черзі: чому чекання руйнує бюджет дедлайну ─────────────────
def queue_sojourn_cliff():
    W, H = 1180, 660
    f = []

    x0, x1 = 300.0, 1120.0
    span = x1 - x0

    # Шкала дедлайну клієнта: 500 мс
    t_deadline = x0 + span * 0.65

    # ── Випадок 1: Нормальне навантаження
    y1 = 120.0
    f.append(fitbox(40, y1 - 32, 235, 64,
                    "1. Штатне навантаження\nчерга коротка",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=1.6))

    t_q1 = x0 + span * 0.10
    t_exec1 = t_q1 + span * 0.30

    f.append(rect(x0, y1 - 16, t_q1 - x0, 32, fill=COOL, stroke=LINE, sw=1.4))
    f.append(text((x0 + t_q1) / 2, y1 + 5, "Черга 20мс", size=12))

    f.append(rect(t_q1, y1 - 16, t_exec1 - t_q1, 32, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text((t_q1 + t_exec1) / 2, y1 + 5, "Обробка 80мс (Успіх 200 OK)", size=12, color=FIELD, bold=True))

    # ── Випадок 2: Перевантаження БЕЗ контролю допуску (Livelock / Wasted Work)
    y2 = 280.0
    f.append(fitbox(40, y2 - 32, 235, 64,
                    "2. Без контролю допуску\nзапис довго сидить у черзі",
                    size=13, bold=True, fill=WARM, stroke=POS, sw=1.8))

    t_q2 = x0 + span * 0.75  # черга вже перевищила дедлайн!
    t_exec2 = t_q2 + span * 0.20

    f.append(rect(x0, y2 - 16, t_q2 - x0, 32, fill=WARM, stroke=POS, sw=1.6))
    f.append(text((x0 + t_q2) / 2, y2 + 5, "Очікування в черзі 600мс (клієнт уже відвалився!)", size=12, color=POS, bold=True))

    f.append(rect(t_q2, y2 - 16, t_exec2 - t_q2, 32, fill="#fca5a5", stroke=POS, sw=1.8))
    f.append(text((t_q2 + t_exec2) / 2, y2 + 5, "100% МАРНА ПРАЦЯ CPU", size=11.5, color=POS, bold=True))

    # ── Випадок 3: З контролем допуску за часом у черзі (Sojourn Time Gate)
    y3 = 440.0
    f.append(fitbox(40, y3 - 32, 235, 64,
                    "3. З контролем допуску\nраннє скидання в черзі",
                    size=13, bold=True, fill=COOL, stroke=NEG, sw=1.8))

    f.append(rect(x0, y3 - 16, span * 0.04, 32, fill=WARM, stroke=POS, sw=1.8))
    f.append(text(x0 + span * 0.02, y3 + 5, "Drop", size=11, color=POS, bold=True))
    f.append(rect(x0 + span * 0.04, y3 - 16, span * 0.96, 32, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(x0 + span * 0.5, y3 + 5, "Потік CPU збережено для живих запитів! Відповідь: 503 Overloaded за 0.1мс", size=12, color=FIELD, bold=True))

    # Лінія клієнтського дедлайну
    f.append(line(t_deadline, 70, t_deadline, 520, color=POS, sw=2.2, dash="6,4"))
    f.append(fitbox(t_deadline - 110, 30, 220, 36,
                    "Клієнтський дедлайн (500 мс)",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.6))

    # Підсумковий блок
    f.append(fitbox(40, 560, 1080, 75,
                    "Якщо запит провів у черзі більше часу, ніж лишилося до його дедлайну, обробляти його безглуздо:\n"
                    "клієнт уже отримав timeout і розірвав з'єднання. Перевірка віку запиту на виході з черги\n"
                    "запобігає спалюванню обчислювальних ресурсів на обслуговування «мертвих» завдань.",
                    size=13, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'queue-sojourn-cliff.svg'), W, H, *f)


# ── 4. Крива затримки М/М/1 («хокейна ключка») ──────────────────────────────
def math_hockey_stick_latency():
    import math
    W, H = 1180, 640
    f = []

    xa, xb = 140.0, 1080.0
    ya, yb = 100.0, 500.0

    f.append(line(xa, yb, xb, yb, color=INK, sw=2.0))
    f.append(line(xa, ya, xa, yb, color=INK, sw=2.0))
    f.append(text(xb, yb + 38, "Завантаження системи ρ = λ / μ →", size=13.5, color=INK, anchor="end", bold=True))
    f.append(text(xa - 12, ya - 18, "Середній час відповіді W = 1 / (μ − λ)", size=13.5, color=INK, anchor="start", bold=True))

    # Сітка по осі X (утилізація)
    for rho, label in [(0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (0.9, "0.9"), (1.0, "1.0")]:
        x = xa + rho * (xb - xa)
        f.append(line(x, yb, x, yb + 6, color=MUTED, sw=1.2))
        f.append(text(x, yb + 24, label, size=12.5, color=MUTED, bold=(rho >= 0.8)))

    # Асимптота при rho = 1.0
    f.append(line(xb, ya, xb, yb, color=POS, sw=1.8, dash="5,5"))
    f.append(text(xb - 10, ya + 20, "Асимптота (W → ∞)", size=12, color=POS, anchor="end", bold=True))

    # Побудова гіперболи W/W0 = 1 / (1 - rho)
    w0_px = 24.0 # висота 1/mu в пікселях
    pts = []
    n = 120
    for i in range(n):
        rho = 0.96 * (i / float(n - 1))
        w_norm = 1.0 / (1.0 - rho)
        x = xa + rho * (xb - xa)
        y = yb - min(w_norm * w0_px, yb - ya)
        pts.append((x, y))

    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=POS, sw=3.2))

    # Точки перегину
    # rho = 0.5 -> W = 2
    x_50 = xa + 0.5 * (xb - xa)
    y_50 = yb - 2.0 * w0_px
    f.append(circle(x_50, y_50, 5, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(x_50 - 15, y_50 - 15, "ρ=0.5: W = 2·W₀", size=12, color=FIELD, bold=True, anchor="end"))

    # rho = 0.8 -> W = 5 (Коліно кривої)
    x_80 = xa + 0.8 * (xb - xa)
    y_80 = yb - 5.0 * w0_px
    f.append(circle(x_80, y_80, 6, fill=ACCENT, stroke=POS, sw=2))
    f.append(line(x_80, y_80, x_80 - 60, y_80 - 40, color=POS, sw=1.4))
    f.append(fitbox(x_80 - 240, y_80 - 90, 210, 50,
                    "Коліно затримки (ρ = 0.8):\nпочаток стрімкого росту черги",
                    size=11.5, bold=True, fill=ACCENT, stroke=POS, sw=1.4))

    # rho = 0.95 -> W = 20
    x_95 = xa + 0.95 * (xb - xa)
    y_95 = yb - 20.0 * w0_px
    f.append(circle(x_95, y_95, 6, fill=WARM, stroke=POS, sw=2))
    f.append(text(x_95 - 20, y_95 + 10, "ρ=0.95: W = 20·W₀", size=12, color=POS, bold=True, anchor="end"))

    # Зона дії контролера допуску
    f.append(rect(xa + 0.7 * (xb - xa), ya + 40, 0.25 * (xb - xa), 140,
                  fill=GOOD, stroke=FIELD, sw=1.5, rx=6))
    f.append(fitbox(xa + 0.7 * (xb - xa) + 10, ya + 50, 0.25 * (xb - xa) - 20, 120,
                    "Цільова зона контролю допуску:\nутримувати утилізацію на рівні 70–85%,\n"
                    "де затримка передбачувана,\nа ресурси не простоюють.",
                    size=12, bold=True, fill=GOOD))

    # Підсумковий блок
    f.append(fitbox(xa, 540, xb - xa, 75,
                    "Згідно з теорією масового обслуговування (модель M/M/1), затримка зростає нелінійно.\n"
                    "Наближення до 100% завантаження неминуче перетворює будь-який сплеск трафіку на нескінченну чергу.\n"
                    "Контроль допуску штучно обмежує потік λ, щоб утримати робочу точку лівіше коліна затримки.",
                    size=13, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'math-hockey-stick-latency.svg'), W, H, *f)


# ── 5. Хронологія еволюції контролю допуску (Hist Timeline) ─────────────────
def hist_evolution_timeline():
    W, H = 1240, 840
    f = []

    f.append(fitbox(60, 20, 1120, 50,
                    "Еволюція контролю допуску: від телефонії Ерланга до хмарних мікросервісів",
                    size=15, bold=True, fill=COOL, stroke=LINE, sw=1.6))

    # Часова вісь
    y_axis = 100.0
    x_start, x_end = 100.0, 1140.0
    f.append(line(x_start, y_axis, x_end, y_axis, color=INK, sw=2.5))
    f.append(arrow(x_end - 20, y_axis, x_end, y_axis, color=INK, sw=2.5))
    f.append(text(x_end, y_axis - 15, "Час →", size=13, color=MUTED, anchor="end"))

    events = [
        (1909, 130.0, 160.0, "1909: Агнер Ерланг\nФормула блокування Erlang B для телефонних ліній.\nПерша математична модель відмови при дефіциті каналів.", GOOD),
        (1985, 330.0, 360.0, "1980-ті: Мережі ATM і CAC\nCall Admission Control (CAC) і Leaky Bucket.\nГарантія якості (QoS) для віртуальних каналів зв'язку.", COOL),
        (1997, 530.0, 160.0, "1997: RSVP та IntServ (RFC 2205)\nРезервування смуги пропускання на маршрутизаторах.\nСкладна сигналізація поступилася DiffServ і дропанню пакетів.", ACCENT),
        (2012, 730.0, 360.0, "2012: CoDel і Bufferbloat\nKathie Nichols, Van Jacobson (ACM Queue).\nКонтроль затримки в черзі (Sojourn time) замість розміру черги.", GOOD),
        (2016, 930.0, 160.0, "2016: Google SRE Adaptive Throttling\nКлієнтський і серверний адаптивний тротлінг.\nІмовірнісне скидання запитів без перевантаження бекенду.", GOOD),
        (2018, 1080.0, 360.0, "2018+: Netflix Concurrency Limits\nАлгоритми TCP Vegas і Gradient у сервісних сітках.\nАвтоматичне визначення лімітів конкурентності без статичних конфігів.", COOL)
    ]

    for year, x_pos, y_box, text_block, bg_col in events:
        # Риска на осі
        f.append(line(x_pos, y_axis - 8, x_pos, y_axis + 8, color=INK, sw=2.0))
        f.append(text(x_pos, y_axis - 14, str(year), size=13, color=NEG, bold=True))

        # Сполучна лінія
        f.append(line(x_pos, y_axis + 8, x_pos, y_box, color=MUTED, sw=1.5, dash="4,4"))

        # Картка події
        bw = 250.0
        bh = 135.0
        f.append(fitbox(x_pos - bw / 2, y_box, bw, bh, text_block, size=11.5, fill=bg_col, stroke=LINE, sw=1.4))

    # Спільний концептуальний висновок
    f.append(fitbox(60, 560, 1120, 110,
                    "Головний історичний урок: жорсткі статичні ліміти та попереднє резервування (ATM / RSVP)\n"
                    "виявилися надто крихкими для масштабованих мереж. Сучасний підхід поєднує динамічний моніторинг черг\n"
                    "(CoDel / Sojourn time), адаптивні алгоритми пошуку пропускної здатності (TCP Vegas / Gradient)\n"
                    "та узгоджений захист на стороні клієнта і сервера (SRE Throttling).",
                    size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'hist-evolution-timeline.svg'), W, H, *f)


throughput_vs_goodput()
admission_pipeline()
queue_sojourn_cliff()
math_hockey_stick_latency()
hist_evolution_timeline()
print("Готово! Згенеровано фігури в:", OUT)
