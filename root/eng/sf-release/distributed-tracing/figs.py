# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Граф викликів DAG та часовий розріз (Waterfall) ───────────────
def fig_trace_dag_and_waterfall():
    W, H = 1000, 520
    frags = []

    # Ліва половина: Граф сервісів (DAG)
    frags.append(text(245, 35, "Граф розподілених викликів (DAG)", size=15, bold=True))
    frags.append(rect(20, 55, 450, 440, fill="#fcfdfe", stroke=MUTED, sw=1, rx=8))

    frags.append(box(245, 95, "API Gateway\n[Root Span: 120ms]", size=12, bold=True, fill="#e8f0ff", stroke=NEG, min_w=180))
    
    frags.append(box(125, 205, "Auth Service\n[Span A: 25ms]", size=11, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=140))
    frags.append(box(345, 205, "Order Service\n[Span B: 85ms]", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=140))

    frags.append(arrow(200, 125, 145, 180, color=MUTED, sw=1.8))
    frags.append(arrow(280, 125, 330, 180, color=FIELD, sw=1.8))

    frags.append(box(220, 315, "Payment API\n[Span C: 45ms]", size=11, bold=True, fill="#fdecea", stroke=POS, min_w=130))
    frags.append(box(365, 315, "Inventory DB\n[Span D: 20ms]", size=11, bold=True, fill="#fff3e0", stroke=LINE, min_w=110))

    frags.append(arrow(320, 235, 250, 290, color=POS, sw=1.8))
    frags.append(arrow(365, 235, 365, 290, color=LINE, sw=1.8))

    frags.append(box(345, 425, "Kafka (Event: OrderPlaced)\n[Span E: 10ms async]", size=11, fill="#fdf6e3", stroke=MUTED, min_w=190))
    frags.append(arrow(345, 235, 345, 400, color=MUTED, sw=1.5))

    # Права половина: Waterfall (Каскадний графік затримок)
    frags.append(text(720, 35, "Часова шкала трейсу (Waterfall)", size=15, bold=True))
    frags.append(rect(480, 55, 500, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))

    # Вісь часу
    frags.append(line(520, 90, 940, 90, color=MUTED, sw=1.2))
    for t_val, x_pos in [(0, 530), (30, 625), (60, 720), (90, 815), (120, 910)]:
        frags.append(line(x_pos, 85, x_pos, 95, color=MUTED, sw=1))
        frags.append(text(x_pos, 80, f"{t_val}ms", size=10, color=MUTED))
        frags.append(line(x_pos, 95, x_pos, 470, color="#f0f2f5", sw=1, dash="3 3"))

    # Спани у форматі горизонтальних барів
    # Root Span
    frags.append(rect(530, 115, 380, 26, fill="#e8f0ff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(540, 132, "API Gateway: POST /checkout (120ms)", size=11, bold=True, anchor="start", color=INK))

    # Span A (Auth)
    frags.append(rect(545, 165, 80, 24, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(555, 181, "Auth: verify (25ms)", size=10, anchor="start", color=INK))

    # Span B (Order)
    frags.append(rect(635, 215, 270, 24, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(645, 231, "Order: create_order (85ms)", size=10, bold=True, anchor="start", color=INK))

    # Span C (Payment)
    frags.append(rect(650, 265, 145, 24, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(660, 281, "Payment: charge (45ms)", size=10, anchor="start", color=INK))

    # Span D (Inventory DB)
    frags.append(rect(805, 315, 65, 24, fill="#fff3e0", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(812, 331, "DB: reserve (20ms)", size=10, anchor="start", color=INK))

    # Span E (Kafka)
    frags.append(rect(875, 365, 35, 24, fill="#fdf6e3", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(880, 405, "Kafka: publish (10ms)", size=10, anchor="start", color=MUTED))
    frags.append(arrow(890, 390, 890, 370, color=MUTED, sw=1.2))

    # Пояснення критичного шляху
    frags.append(line(530, 450, 910, 450, color=POS, sw=2))
    frags.append(text(720, 442, "Критичний шлях: Auth (25ms) + Order overhead + Payment (45ms) + DB (20ms) = 120ms", size=10, bold=True, color=POS))

    render(os.path.join(IMG, 'trace-dag-and-waterfall.svg'), W, H, *frags,
           title="Граф розподілених викликів (DAG) та каскадний часовий графік (Waterfall)")


# ── Фігура 2: Структура W3C traceparent заголовка ───────────────────────────
def fig_w3c_traceparent():
    W, H = 960, 420
    frags = []

    frags.append(text(W / 2, 35, "Анатомія W3C Trace Context заголовка (traceparent)", size=15, bold=True))

    # Загальний рядок заголовка
    frags.append(rect(60, 70, 840, 60, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(W / 2, 107, "traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
                      size=16, bold=True, color=INK))

    # Розбивка на 4 блоки зі стрілками
    # Блок 1: Version
    frags.append(line(195, 130, 140, 190, color=MUTED, sw=1.5))
    frags.append(box(140, 240, "Версія (2 hex)\n«00» — поточний W3C\n(ff заборонено)", size=11, fill="#e8f0ff", stroke=NEG, min_w=140))

    # Блок 2: Trace ID
    frags.append(line(375, 130, 360, 190, color=FIELD, sw=1.5))
    frags.append(box(360, 250, "Trace ID (32 hex / 16 байтів)\nГлобальний 128-бітний ID транзакції\nУнікальний для всього графа\n(всі нулі заборонено)", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=240))

    # Блок 3: Parent / Span ID
    frags.append(line(670, 130, 650, 190, color=POS, sw=1.5))
    frags.append(box(650, 250, "Parent ID / Span ID (16 hex / 8 байтів)\nЛокальний 64-бітний ID спана\nІдентифікує конкретний виклик\n(всі нулі заборонено)", size=11, bold=True, fill="#fdecea", stroke=POS, min_w=240))

    # Блок 4: Trace Flags
    frags.append(line(845, 130, 845, 190, color=LINE, sw=1.5))
    frags.append(box(845, 240, "Прапорці (2 hex)\n01 — Recorded (семпльовано)\n00 — Not recorded", size=11, fill="#fff3e0", stroke=LINE, min_w=150))

    # Нижня плашка з поясненням контексту
    frags.append(box(W / 2, 365, "Довжина фіксована: 55 символів UTF-8. Розділювач — дефіс «-». Передається в заголовках HTTP/gRPC.", size=12, fill="#ffffff", stroke=MUTED, pad=8, min_w=780))

    render(os.path.join(IMG, 'w3c-traceparent-format.svg'), W, H, *frags,
           title="Анатомія заголовка W3C Trace Context (traceparent)")


# ── Фігура 3: Head-based проти Tail-based семплінгу ─────────────────────────
def fig_head_vs_tail_sampling():
    W, H = 960, 480
    frags = []

    frags.append(text(W / 2, 30, "Порівняння стратегій вибірки: Head-based проти Tail-based", size=15, bold=True))

    # Ліва колонка: Head-based sampling
    frags.append(rect(30, 60, 430, 390, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(245, 90, "Head-based семплінг (на вході)", size=14, bold=True, color=NEG))

    frags.append(box(245, 140, "1. Вхідний запит на API Gateway\n[Рішення приймається миттєво]", size=11, fill="#e8f0ff", stroke=NEG, min_w=320))
    frags.append(arrow(245, 170, 245, 205, color=NEG, sw=1.8))

    frags.append(box(245, 235, "Імовірнісний фільтр (наприклад, 1%)\n99% — прапорець sampled=0\n1% — прапорець sampled=1", size=11, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=320))
    frags.append(arrow(245, 275, 245, 310, color=MUTED, sw=1.8))

    frags.append(box(245, 365, "Переваги: нульова затримка, мінімум пам'яті.\nНедолік: рідкісні помилки (HTTP 500) у 99%\nвідкинутих трейсів губляться назавжди!", size=10, fill="#fdecea", stroke=POS, pad=6, min_w=340))

    # Права колонка: Tail-based sampling
    frags.append(rect(500, 60, 430, 390, fill="#fcfdfe", stroke=FIELD, sw=1.2, rx=8))
    frags.append(text(715, 90, "Tail-based семплінг (на виході)", size=14, bold=True, color=FIELD))

    frags.append(box(715, 140, "1. Усі сервіси генерують спани\n[100% спанів надсилаються в OTel Collector]", size=11, fill="#eafaf0", stroke=FIELD, min_w=330))
    frags.append(arrow(715, 170, 715, 205, color=FIELD, sw=1.8))

    frags.append(box(715, 235, "Буферизація в пам'яті OTel Collector (30с)\nОцінка завершеного графа трейсу:\n• Помилка (error=true) → ЗБЕРЕГТИ 100%\n• Затримка > 500ms → ЗБЕРЕГТИ 100%\n• Успішні швидкі → ЗБЕРЕГТИ 0.1%", size=10, bold=True, fill="#fff3e0", stroke=LINE, min_w=340))
    frags.append(arrow(715, 290, 715, 320, color=FIELD, sw=1.8))

    frags.append(box(715, 375, "Переваги: 100% видимість усіх збоїв та хвостів p99.\nНедолік: вимагає буфера пам'яті на колекторі\nта маршрутизації за Trace ID (routing connector).", size=10, fill="#eafaf0", stroke=FIELD, pad=6, min_w=340))

    render(os.path.join(IMG, 'head-vs-tail-sampling.svg'), W, H, *frags,
           title="Порівняння стратегій вибірки трейсів: Head-based проти Tail-based")


# ── Фігура 4: Конвеєр OpenTelemetry (In-App -> Collector -> Storage) ────────
def fig_opentelemetry_pipeline():
    W, H = 1000, 440
    frags = []

    frags.append(text(W / 2, 30, "Архітектура збору телеметрії OpenTelemetry (OTel)", size=15, bold=True))

    # Стовпчик 1: Застосунки (Сервіси)
    frags.append(rect(20, 60, 240, 350, fill="#f8f9fa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(140, 85, "Сервіси застосунку", size=13, bold=True, color=INK))
    frags.append(box(140, 135, "Service A (Go)\nOTel SDK + Auto-instr", size=10, fill="#e8f0ff", stroke=NEG, min_w=190))
    frags.append(box(140, 215, "Service B (Java / C++)\nOTel SDK + Manual Spans", size=10, fill="#e8f0ff", stroke=NEG, min_w=190))
    frags.append(box(140, 295, "Service C (Python / Node)\nOTel SDK + HTTP middleware", size=10, fill="#e8f0ff", stroke=NEG, min_w=190))
    frags.append(box(140, 365, "Експорт: OTLP / gRPC\n(протокол Protobuf)", size=10, bold=True, fill="#fff", stroke=MUTED, min_w=190))

    frags.append(arrow(245, 235, 310, 235, color=NEG, sw=2))

    # Стовпчик 2: OpenTelemetry Collector
    frags.append(rect(315, 60, 370, 350, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(500, 85, "OpenTelemetry Collector (Агент / Шлюз)", size=13, bold=True, color=FIELD))

    frags.append(box(500, 135, "Receivers (Приймачі)\notlp: protocols: [grpc, http]", size=11, fill="#eafaf0", stroke=FIELD, min_w=310))
    frags.append(arrow(500, 160, 500, 185, color=FIELD, sw=1.5))

    frags.append(box(500, 230, "Processors (Обробники)\n1. memory_limiter (захист від OOM)\n2. tail_sampling (фільтрація помилок)\n3. batch (пакетування спанів)", size=10, bold=True, fill="#fff3e0", stroke=LINE, min_w=310))
    frags.append(arrow(500, 275, 500, 300, color=FIELD, sw=1.5))

    frags.append(box(500, 345, "Exporters (Експортери)\notlp / clickhouse / jaeger", size=11, fill="#eafaf0", stroke=FIELD, min_w=310))

    frags.append(arrow(670, 235, 735, 235, color=FIELD, sw=2))

    # Стовпчик 3: Сховища та візуалізація
    frags.append(rect(740, 60, 240, 350, fill="#f8f9fa", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(860, 85, "Сховища та UI", size=13, bold=True, color=INK))
    frags.append(box(860, 140, "ClickHouse\n[Колонкове збереження]", size=10, fill="#fdecea", stroke=POS, min_w=190))
    frags.append(box(860, 215, "Grafana Tempo\n[Об'єктне сховище S3]", size=10, fill="#fdecea", stroke=POS, min_w=190))
    frags.append(box(860, 290, "Jaeger Backend\n[Пошук і аналіз DAG]", size=10, fill="#fdecea", stroke=POS, min_w=190))
    frags.append(box(860, 365, "Grafana / UI\n[Візуалізація Waterfall]", size=10, bold=True, fill="#fff", stroke=MUTED, min_w=190))

    render(os.path.join(IMG, 'opentelemetry-pipeline.svg'), W, H, *frags,
           title="Архітектура збору телеметрії: від SDK через OTel Collector до сховищ")


# ── Фігура 5: Поширення контексту через межі рантаймів і черг ───────────────
def fig_async_context_propagation():
    W, H = 960, 460
    frags = []

    frags.append(text(W / 2, 30, "Поширення контексту (Context Propagation) крізь межі системи", size=15, bold=True))

    # Крок 1: Вхідний HTTP-запит
    frags.append(box(160, 90, "Клієнтський виклик\nPOST /api/order", size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=180))
    frags.append(arrow(260, 90, 350, 90, color=NEG, sw=1.8))

    # Крок 2: Сервіс А (HTTP Server)
    frags.append(rect(360, 50, 240, 370, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(480, 75, "Сервіс А (Web API)", size=12, bold=True, color=FIELD))

    frags.append(box(480, 120, "Extract Context:\nзчитування traceparent\nстворення Server Span", size=10, fill="#eafaf0", stroke=FIELD, min_w=200))
    frags.append(arrow(480, 150, 480, 180, color=FIELD, sw=1.5))

    frags.append(box(480, 210, "In-process Propagation:\nThreadLocal / AsyncContext\n(збереження TraceID у потоці)", size=10, fill="#fff", stroke=MUTED, min_w=200))
    frags.append(arrow(480, 245, 480, 275, color=FIELD, sw=1.5))

    frags.append(box(480, 320, "Inject Context:\nзапис traceparent у\nзаголовки Kafka повідомлення", size=10, fill="#fff3e0", stroke=LINE, min_w=200))
    frags.append(arrow(480, 360, 480, 385, color=LINE, sw=1.5))

    frags.append(box(480, 400, "Kafka Producer send()", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=180))

    # Крок 3: Брокер повідомлень
    frags.append(arrow(580, 400, 680, 400, color=LINE, sw=1.8))
    frags.append(box(760, 400, "Kafka Topic: orders\n[Повідомлення з headers: traceparent]", size=11, bold=True, fill="#fdf6e3", stroke=LINE, min_w=200))

    # Крок 4: Сервіс Б (Асинхронний воркер)
    frags.append(rect(670, 50, 260, 280, fill="#fcfdfe", stroke=POS, sw=1.5, rx=8))
    frags.append(text(800, 75, "Сервіс Б (Фоновий Consumer)", size=12, bold=True, color=POS))

    frags.append(box(800, 130, "Kafka Consumer poll()\nотримання повідомлення", size=10, fill="#fdecea", stroke=POS, min_w=220))
    frags.append(arrow(800, 160, 800, 185, color=POS, sw=1.5))

    frags.append(box(800, 235, "Extract + Link:\nвилучення батьківського TraceID\nстворення Consumer Span\nзбереження причинного зв'язку", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=220))

    # Стрілка від брокера до консьюмера
    frags.append(arrow(760, 370, 760, 160, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'async-context-propagation.svg'), W, H, *frags,
           title="Поширення розподіленого контексту крізь мережеві межі та черги повідомлень")


if __name__ == '__main__':
    fig_trace_dag_and_waterfall()
    fig_w3c_traceparent()
    fig_head_vs_tail_sampling()
    fig_opentelemetry_pipeline()
    fig_async_context_propagation()
    print("All figures generated successfully.")
