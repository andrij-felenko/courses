# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Ієрархічні метрики проти багатовимірних міток ─────────────────
def fig_metric_models():
    W, H = 940, 480
    frags = []

    # Заголовок зліва: Ієрархічна модель (Graphite / StatsD)
    col1_x = 230
    frags.append(text(col1_x, 38, "Ієрархічні шляхи (Graphite, StatsD)", size=15, bold=True, color=INK))
    frags.append(text(col1_x, 58, "Жорстко зашита послідовність сегментів у назві", size=12, color=MUTED))

    # Схема ієрархії
    b1, _, _ = textbox(col1_x, 105, "prod.eu-west.web-01.http.GET.200.count", size=12, bold=True,
                       fill="#fff5f5", stroke=POS, sw=1.6, pad=8)
    b2, _, _ = textbox(col1_x, 155, "prod.us-east.web-02.http.POST.500.count", size=12, bold=True,
                       fill="#fff5f5", stroke=POS, sw=1.6, pad=8)
    frags.extend([b1, b2])

    # Проблема ієрархії
    prob_lines = [
        "• Порядок сегментів не можна змінити",
        "• Запит «помилки 500 по всіх регіонах»",
        "  вимагає складних масок: prod.*.*.http.*.500.*",
        "• Додавання мітки версії (v2) ламає всі існуючі запити"
    ]
    prob_box, _, _ = textbox(col1_x, 275, "\n".join(prob_lines), size=12,
                             fill=FILL, stroke=LINE, sw=1.2, pad=12)
    frags.append(prob_box)

    # Розділювач
    frags.append(line(470, 30, 470, 450, color=MUTED, sw=1.2, dash="4 4"))

    # Заголовок справа: Багатовимірна модель (Prometheus / OpenMetrics)
    col2_x = 705
    frags.append(text(col2_x, 38, "Багатовимірні мітки (Prometheus, OTel)", size=15, bold=True, color=FIELD))
    frags.append(text(col2_x, 58, "Метрика + довільний набір пар ключ-значення", size=12, color=MUTED))

    # Схема міток
    b3, _, _ = textbox(col2_x, 115, 'http_requests_total{\n  env="prod", dc="eu-west",\n  host="web-01", method="GET", status="200"\n}',
                       size=11, bold=True, fill="#f4faf5", stroke=FIELD, sw=1.6, pad=8)
    frags.append(b3)

    # Переваги моделі
    adv_lines = [
        "• Зрізи за довільними вимірами (slice-and-dice)",
        "• Агрегація за будь-яким полем:",
        "  sum by (status) (rate(http_requests_total[5m]))",
        "• Нові мітки додаються без ламання старих дашбордів"
    ]
    adv_box, _, _ = textbox(col2_x, 275, "\n".join(adv_lines), size=12,
                            fill=FILL, stroke=FIELD, sw=1.4, pad=12)
    frags.append(adv_box)

    # Підсумкова плашка знизу
    bot_box, _, _ = textbox(470, 415, "Багатовимірність замінює позиційний синтаксис гнучкою алгеброю реляційних фільтрів",
                            size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.5, pad=10)
    frags.append(bot_box)

    render(os.path.join(IMG, 'metric-models-comparison.svg'), W, H, *frags,
           title="Порівняння ієрархічної та багатовимірної моделей метрик")


# ── Фігура 2: Методології RED та USE ────────────────────────────────────────
def fig_red_vs_use():
    W, H = 940, 460
    frags = []

    # Верхня панель: Рівень застосунку (RED)
    frags.append(rect(30, 25, 880, 185, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(80, 52, "МЕТОД RED (Tom Wilkie) — Сервіси та запити", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(80, 72, "Орієнтований на користувача: як система виконує запити", size=11, color=MUTED, anchor="start"))

    red_items = [
        ("Rate (Частота)", "Кількість запитів на секунду\n(наприклад, req/s, rps)", NEG, 190),
        ("Errors (Помилки)", "Кількість невдалих запитів\n(частка 5xx або помилок)", POS, 470),
        ("Duration (Тривалість)", "Розподіл часу обробки\n(перцентилі p95, p99 затримки)", FIELD, 750)
    ]
    for title, desc, col, cx in red_items:
        box, _, _ = textbox(cx, 130, f"{title}\n{desc}", size=12, bold=True,
                            fill="#ffffff", stroke=col, sw=1.5, pad=10)
        frags.append(box)

    # Нижня панель: Рівень ресурсів (USE)
    frags.append(rect(30, 245, 880, 185, fill="#f6faf7", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(80, 272, "МЕТОД USE (Brendan Gregg) — Ресурси та апаратне забезпечення", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(80, 292, "Орієнтований на залізо: CPU, пам'ять, диски, мережеві інтерфейси", size=11, color=MUTED, anchor="start"))

    use_items = [
        ("Utilization (Утилізація)", "Частка часу активності\n(наприклад, CPU % зайнятості)", FIELD, 190),
        ("Saturation (Насиченість)", "Черга очікування роботи\n(load avg, disk queue depth)", POS, 470),
        ("Errors (Помилки)", "Апаратні та драйверні збої\n(ECC-пам'ять, dropped packets)", NEG, 750)
    ]
    for title, desc, col, cx in use_items:
        box, _, _ = textbox(cx, 350, f"{title}\n{desc}", size=12, bold=True,
                            fill="#ffffff", stroke=col, sw=1.5, pad=10)
        frags.append(box)

    render(os.path.join(IMG, 'red-vs-use-frameworks.svg'), W, H, *frags,
           title="Методології спостережуваності: RED для сервісів проти USE для ресурсів")


# ── Фігура 3: Гістограми та інтерполяція перцентилів ─────────────────────────
def fig_histogram_percentiles():
    W, H = 940, 480
    frags = []

    frags.append(text(W / 2, 35, "Кумулятивна гістограма та інтерполяція квантилів (p95)", size=15, bold=True))
    frags.append(text(W / 2, 55, "Кожен кошик рахує кількість спостережень <= le (less or equal)", size=12, color=MUTED))

    # Стовпчики кошиків
    buckets = [
        ("le=0.05", "50ms", 120, 70, 140),
        ("le=0.1", "100ms", 250, 140, 210),
        ("le=0.25", "250ms", 520, 240, 310),
        ("le=0.5", "500ms", 840, 330, 480),
        ("le=1.0", "1s", 960, 380, 650),
        ("le=+Inf", "+Inf", 1000, 400, 820)
    ]

    base_y = 380
    # Вісь X
    frags.append(line(60, base_y, 900, base_y, color=LINE, sw=2))
    # Вісь Y
    frags.append(line(60, base_y, 60, 90, color=LINE, sw=2))
    frags.append(text(50, 100, "Кількість запитів (Count)", size=11, color=MUTED, anchor="end"))

    # Позначки Y
    for count_val, y_pos in [(250, base_y - 100), (500, base_y - 200), (750, base_y - 300), (1000, base_y - 400)]:
        frags.append(line(55, y_pos, 60, y_pos, color=LINE, sw=1.5))
        frags.append(text(50, y_pos + 4, str(count_val), size=10, color=MUTED, anchor="end"))
        frags.append(line(60, y_pos, 900, y_pos, color="#e5e7eb", sw=1, dash="2 4"))

    for le_label, time_label, count, h_px, bx in buckets:
        # Прямокутник стовпчика
        bar_col = "#e0edff" if count < 950 else "#ffeedb"
        border_col = NEG if count < 950 else POS
        frags.append(rect(bx - 35, base_y - h_px, 70, h_px, fill=bar_col, stroke=border_col, sw=1.5, rx=3))
        frags.append(text(bx, base_y - h_px - 8, str(count), size=11, bold=True, color=border_col))
        frags.append(text(bx, base_y + 18, le_label, size=11, bold=True))
        frags.append(text(bx, base_y + 34, f"({time_label})", size=10, color=MUTED))

    # Лінія p95 (950-й запит з 1000)
    p95_y = base_y - 380  # 95% висоти
    frags.append(line(60, p95_y, 750, p95_y, color=POS, sw=2, dash="4 4"))
    frags.append(text(760, p95_y + 4, "Ціль 95% = 950-й запит", size=12, bold=True, color=POS, anchor="start"))

    # Стрілка інтерполяції між le=0.5 (840) та le=1.0 (960)
    frags.append(arrow(700, p95_y - 35, 650, p95_y + 2, color=POS, sw=2))
    p_info, _, _ = textbox(720, p95_y - 65, "Інтерполяція всередині кошика [0.5s .. 1.0s]:\nЗначення p95 ≈ 0.5s + (950-840)/(960-840) × 0.5s ≈ 0.958s",
                           size=11, bold=True, fill="#fffaf0", stroke=POS, sw=1.4, pad=8)
    frags.append(p_info)

    render(os.path.join(IMG, 'histogram-buckets-percentiles.svg'), W, H, *frags,
           title="Інтерполяція квантилів за кумулятивними кошиками гістограми")


# ── Фігура 4: Pull проти Push у зборі телеметрії ─────────────────────────────
def fig_pull_vs_push():
    W, H = 940, 450
    frags = []

    # Ліва колонка: PULL (Prometheus)
    p1_cx = 240
    frags.append(rect(20, 20, 430, 410, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(p1_cx, 48, "PULL-модель (Prometheus)", size=15, bold=True, color=NEG))
    frags.append(text(p1_cx, 68, "Сервер сам опитує вузли за розкладом", size=11, color=MUTED))

    # Сервер
    srv_pull, _, _ = textbox(p1_cx, 130, "Сервер TSDB (Prometheus)\n[Service Discovery + Scrape Loop]",
                             size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6, pad=10)
    frags.append(srv_pull)

    # Стрілки опитування
    frags.append(arrow(p1_cx - 80, 165, 120, 235, color=NEG, sw=1.8))
    frags.append(arrow(p1_cx + 80, 165, 340, 235, color=NEG, sw=1.8))
    frags.append(text(120, 195, "GET /metrics", size=10, bold=True, color=NEG))
    frags.append(text(340, 195, "GET /metrics", size=10, bold=True, color=NEG))

    # Таргети
    t1, _, _ = textbox(120, 265, "Web-01\n(:8080/metrics)", size=11, bold=True, fill="#ffffff", stroke=LINE, sw=1.3, pad=8)
    t2, _, _ = textbox(340, 265, "Web-02\n(:8080/metrics)", size=11, bold=True, fill="#ffffff", stroke=LINE, sw=1.3, pad=8)
    frags.extend([t1, t2])

    # Властивості Pull
    pull_props = [
        "✓ Природний backpressure (контроль темпу)",
        "✓ Вбудований контроль доступності (Health check)",
        "✗ Складність збирання крізь NAT та у FaaS"
    ]
    p_box, _, _ = textbox(p1_cx, 365, "\n".join(pull_props), size=11,
                          fill="#ffffff", stroke=NEG, sw=1.2, pad=10)
    frags.append(p_box)

    # Права колонка: PUSH (StatsD, OTel, Influx)
    p2_cx = 700
    frags.append(rect(490, 20, 430, 410, fill="#f6faf7", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(p2_cx, 48, "PUSH-модель (StatsD, OTLP)", size=15, bold=True, color=FIELD))
    frags.append(text(p2_cx, 68, "Додатки самі шлють метрики до приймача", size=11, color=MUTED))

    # Клієнти зверху
    c1, _, _ = textbox(580, 130, "Lambda / App-01\n[OTel SDK]", size=11, bold=True, fill="#ffffff", stroke=LINE, sw=1.3, pad=8)
    c2, _, _ = textbox(800, 130, "Batch Job-02\n[StatsD Client]", size=11, bold=True, fill="#ffffff", stroke=LINE, sw=1.3, pad=8)
    frags.extend([c1, c2])

    # Стрілки відправки
    frags.append(arrow(580, 165, p2_cx - 60, 235, color=FIELD, sw=1.8))
    frags.append(arrow(800, 165, p2_cx + 60, 235, color=FIELD, sw=1.8))
    frags.append(text(600, 195, "POST /otlp", size=10, bold=True, color=FIELD))
    frags.append(text(800, 195, "UDP 8125", size=10, bold=True, color=FIELD))

    # Приймач
    srv_push, _, _ = textbox(p2_cx, 265, "Колектор / TSDB Gateway\n[Ingestion Pipeline / Buffer]",
                             size=12, bold=True, fill="#f4faf5", stroke=FIELD, sw=1.6, pad=10)
    frags.append(srv_push)

    # Властивості Push
    push_props = [
        "✓ Легко проходить крізь NAT і фаєрволи",
        "✓ Природно підходить для короткоживучих завдань",
        "✗ Ризик перевантаження сервера штормом даних"
    ]
    push_box, _, _ = textbox(p2_cx, 365, "\n".join(push_props), size=11,
                             fill="#ffffff", stroke=FIELD, sw=1.2, pad=10)
    frags.append(push_box)

    render(os.path.join(IMG, 'pull-vs-push-topology.svg'), W, H, *frags,
           title="Порівняння архітектур збору метрик: Pull проти Push")


if __name__ == '__main__':
    fig_metric_models()
    fig_red_vs_use()
    fig_histogram_percentiles()
    fig_pull_vs_push()
