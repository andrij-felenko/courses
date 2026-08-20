# -*- coding: utf-8 -*-
"""Фігури до теми «Структуровані логи».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"


# ── 1. Неструктурований текст проти структурованої події ───────────────────────
def fig_text_vs_structured():
    W, H = 960, 500
    f = [text(W / 2, 30, "Текстовий рядок проти структурованого документа", size=16, bold=True)]

    # Ліва колонка: сирий рядок
    f.append(rect(24, 56, 436, 414, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(44, 86, "СИРИЙ ФОРМАТОВАНИЙ ТЕКСТ", size=13, color=POS, anchor="start", bold=True))
    
    raw_str = (
        '2026-08-20 03:14:12 [ERROR] User 84920\n'
        'payment failed for order 19482:\n'
        'timeout connecting to gateway after 3004ms'
    )
    f.append(fitbox(44, 102, 396, 76, raw_str, size=11.5, stroke=POS, fill="#ffffff", color=INK))

    raw_problems = [
        ("Втрата типів", "числа 84920 і 19482 — просто символи без семантики"),
        ("Крихкість парсерів", "зміна слова «User» на «Customer» ламає всі регулярні вирази"),
        ("Ціна розбору", "Grok/Regex з'їдає до 70% CPU на агенті збору логів"),
        ("Неможливість вибірок", "запит «duration_ms > 3000» вимагає повного скану тексту"),
    ]
    ry = 194
    for title_p, desc_p in raw_problems:
        f.append(fitbox(44, ry, 396, 56, title_p + "\n" + desc_p, size=11, stroke=GRAY, fill="#ffffff"))
        ry += 66

    # Права колонка: структурований JSON
    f.append(rect(500, 56, 436, 414, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(520, 86, "СТРУКТУРОВАНА ПОДІЯ (JSON / ndjson)", size=13, color=FIELD, anchor="start", bold=True))

    json_str = (
        '{\n'
        '  "timestamp": "2026-08-20T03:14:12.802Z",\n'
        '  "level": "ERROR", "msg": "payment_failed",\n'
        '  "user_id": 84920, "order_id": 19482,\n'
        '  "duration_ms": 3004, "trace_id": "a1f8c4...",\n'
        '  "error": {"type": "GatewayTimeout", "code": 504}\n'
        '}'
    )
    f.append(fitbox(520, 102, 396, 126, json_str, size=11, stroke=FIELD, fill="#ffffff", color=INK))

    struct_benefits = [
        ("Типізовані поля", "числові діапазони, булеві прапорці, вкладені об'єкти"),
        ("Колонковий індекс", "миттєві агрегації й фільтри в ClickHouse / Elasticsearch"),
        ("Незмінність схеми", "додавання нових полів не ламає наявні дашборди й алерти"),
        ("Наскрізний контекст", "trace_id зв'язує подію з розподіленим трейсом"),
    ]
    sy = 244
    for title_b, desc_b in struct_benefits:
        f.append(fitbox(520, sy, 396, 50, title_b + "\n" + desc_b, size=11, stroke=FIELD, fill="#ffffff"))
        sy += 58

    render(os.path.join(IMG, "text-vs-structured.svg"), W, H, *f)


# ── 2. Наскрізний конвеєр збору та обробки телеметрії ──────────────────────────
def fig_ingestion_pipeline():
    W, H = 960, 480
    f = [text(W / 2, 30, "Шлях логу: від коду застосунку до сховища запитів", size=16, bold=True)]

    steps = [
        (30, 150, "1 · Застосунок", "нуль-алокаційний\nенкодер + буфер", NEG, "#eef2fb"),
        (220, 150, "2 · Фоновий потік", "неблокувальний\nпакетний скид у stdout", AMBER, "#fdf6e3"),
        (410, 150, "3 · Агент вузла", "Vector / Fluent Bit\n(збір з контейнера)", LINE, FILL),
        (600, 150, "4 · Буфер черги", "Kafka / Redpanda\n(захист від сплесків)", AMBER, "#fdf6e3"),
        (790, 140, "5 · Сховище", "ClickHouse / Loki /\nElasticsearch", FIELD, "#eafaf1"),
    ]

    yt = 70
    bh = 76
    for x, w, title_s, desc_s, col, bg_col in steps:
        f.append(fitbox(x, yt, w, bh, title_s + "\n" + desc_s, size=11.5, stroke=col, fill=bg_col, bold=True))

    for i in range(len(steps) - 1):
        x1 = steps[i][0] + steps[i][1] + 2
        x2 = steps[i+1][0] - 2
        f.append(arrow(x1, yt + bh / 2, x2, yt + bh / 2, color=GRAY, sw=1.6))

    # Нижня частина: характеристики й вимоги на кожному етапі
    py = 176
    f.append(rect(24, py, W - 48, 276, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(44, py + 28, "Інженерні гарантії та ціна на кожному щаблі конвеєра", size=12.5,
                  color=MUTED, anchor="start", bold=True))

    rows = [
        ("Гарячий шлях коду", "Логер НЕ має виділяти пам'ять на купі (zero allocation) і не блокує робочі потоки під замками.", NEG),
        ("Міжпроцесна межа", "Застосунок пише JSON-лінії в stdout/pipe; ОС керує буфером каналу (~64 КБ); переповнення веде до дропу або блокування.", AMBER),
        ("Збір та парсинг", "Агент вузла збагачує логи метаданими пода (node_name, container_id, namespace) без втручання в код.", LINE),
        ("Транспортний буфер", "Шина повідомлень згладжує навантаження під час інцидентів, коли обсяг логів зростає в 10–100 разів.", AMBER),
        ("Індексація й пошук", "Колонкове збереження стискає однакові ключі на 85–90% і дозволяє читати лише потрібні стовпчики полів.", FIELD),
    ]

    ry = py + 48
    for name_r, desc_r, col_r in rows:
        f.append(fitbox(44, ry, 180, 36, name_r, size=11.5, stroke=col_r, fill="#ffffff", color=col_r, bold=True))
        f.append(text(236, ry + 22, desc_r, size=11.5, color=INK, anchor="start"))
        ry += 44

    render(os.path.join(IMG, "ingestion-pipeline.svg"), W, H, *f)


# ── 3. Трикутник спостережності: метрики, трейси, логи ────────────────────────
def fig_observability_triangle():
    W, H = 940, 480
    f = [text(W / 2, 30, "Трикутник спостережності: роль структурованих логів", size=16, bold=True)]

    # Три колони
    cols = [
        dict(x=24, w=280, title="МЕТРИКИ", sub="Числові агрегати (числа)",
             q="«Що зламалося і коли?»",
             pts=["Агреговані лічильники й таймери", "Низька вартість збереження", "Не мають контексту окремого виклику"],
             col=NEG, fill="#eef2fb"),
        dict(x=330, w=280, title="РОЗПОДІЛЕНІ ТРЕЙСИ", sub="Причинно-наслідкові ланцюги",
             q="«Де саме виникла затримка?»",
             pts=["Дерево спанів між сервісами", "Шлях запиту крізь мікросервіси", "Фіксують тривалість етапів"],
             col=AMBER, fill="#fdf6e3"),
        dict(x=636, w=280, title="СТРУКТУРОВАНІ ЛОГИ", sub="Детальні фактичні події",
             q="«Чому саме це сталося?»",
             pts=["Довільний набір типізованих полів", "Вичерпний контекст помилки", "Повна деталізація вхідних даних"],
             col=FIELD, fill="#eafaf1"),
    ]

    ytop = 66
    for c in cols:
        f.append(rect(c["x"], ytop, c["w"], 240, fill=c["fill"], stroke=c["col"], sw=1.8, rx=10))
        f.append(text(c["x"] + c["w"] / 2, ytop + 28, c["title"], size=13.5, color=c["col"], bold=True))
        f.append(text(c["x"] + c["w"] / 2, ytop + 50, c["sub"], size=11, color=MUTED, italic=True))
        f.append(fitbox(c["x"] + 14, ytop + 64, c["w"] - 28, 36, c["q"], size=11.5, stroke=c["col"], fill="#ffffff", bold=True))

        py = ytop + 112
        for pt in c["pts"]:
            f.append(text(c["x"] + 20, py, "• " + pt, size=11, color=INK, anchor="start"))
            py += 36

    # Зв'язувальний міст знизу
    by = 324
    f.append(rect(24, by, W - 48, 134, fill=PANEL, stroke=LINE, sw=1.5, rx=10))
    f.append(text(44, by + 28, "Міст кореляції: trace_id та span_id всередині структурованого логу", size=13,
                  color=INK, anchor="start", bold=True))
    f.append(fitbox(44, by + 46, 852, 68,
                    'У структурованому лозі trace_id автоматично зв\'язує спан трейсингу з усіма логами операції:\n'
                    'Алерт метрики (5xx > 1%) ──> Відкриття спану в трейсі (затримка 3004 мс) ──> Перехід за trace_id до точного логу з помилкою',
                    size=12, stroke=FIELD, fill="#ffffff", color=INK))

    render(os.path.join(IMG, "observability-triangle.svg"), W, H, *f)


# ── 4. Поширення контексту (Context Propagation & MDC) ────────────────────────
def fig_context_propagation():
    W, H = 960, 490
    f = [text(W / 2, 30, "Поширення контексту крізь шари виконання", size=16, bold=True)]

    # Верхній блок: Вхідний HTTP-запит
    f.append(fitbox(40, 60, 880, 54,
                    'Вхідний HTTP-запит  ──>  Мідлвар видобуває / генерує контекст:\n'
                    '{ "trace_id": "4bf92f3577b34da6", "request_id": "req-9821", "tenant_id": "org_77", "user_id": 401 }',
                    size=11.5, stroke=NEG, fill="#eef2fb", bold=True))

    # Стрілка вниз у Context Storage
    f.append(arrow(480, 118, 480, 148, color=GRAY, sw=1.6))

    # Середній шар: збереження контексту
    f.append(rect(40, 152, 880, 140, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(60, 178, "Шар збереження контексту (Implicit Context / MDC / Execution Context)", size=12.5,
                  color=MUTED, anchor="start", bold=True))

    ctx_boxes = [
        (60, 194, 260, 82, "ThreadLocal / MDC\n(Java, C++ per-thread)\nПрацює в 1 потоці;\nгубиться в пулах задач", AMBER, "#ffffff"),
        (350, 194, 260, 82, "AsyncLocalStorage\n(Node.js / V8)\nАвтоматично слідує за\nасинхронними промісами", FIELD, "#ffffff"),
        (640, 194, 260, 82, "Явний context.Context\n(Go / Rust explicit)\nПередається першим\nаргументом у виклики", NEG, "#ffffff"),
    ]
    for x, y, w, h, txt, col, bg_col in ctx_boxes:
        f.append(fitbox(x, y, w, h, txt, size=11, stroke=col, fill=bg_col))

    # Стрілка вниз до глибокого виклику
    f.append(arrow(480, 296, 480, 326, color=GRAY, sw=1.6))

    # Нижній шар: Глибокий виклик у сховищі даних
    f.append(rect(40, 330, 880, 134, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(60, 356, "Глибокий виклик: db.Exec(query) зазнав помилки", size=13, color=FIELD,
                  anchor="start", bold=True))

    log_call = 'logger.Error("db_query_timeout", Field("table", "orders"), Field("elapsed_ms", 1250));'
    f.append(fitbox(60, 370, 840, 32, log_call, size=11.5, stroke=LINE, fill="#ffffff"))

    f.append(text(60, 426,
                  "→ Результат: логер автоматично об'єднує локальні поля виклику з контекстом запиту (trace_id, user_id, tenant_id)",
                  size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(60, 448,
                  "без потреби вручну протягувати 10 параметрів крізь 5 проміжних функцій сервісного шару.",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "context-propagation.svg"), W, H, *f)


# ── 5. Архітектура нуль-алокаційного логера ────────────────────────────────────
def fig_zero_alloc_encoder():
    W, H = 960, 520
    f = [text(W / 2, 30, "Архітектура швидкого логера: наївний підхід проти нуль-алокаційного", size=16, bold=True)]

    # Верхня половина: Наївний логер
    f.append(rect(24, 56, 912, 196, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    f.append(text(44, 82, "НАЇВНИЙ ЛОГЕР (String interpolation + Mutex + Синхронний I/O)", size=12.5,
                  color=POS, anchor="start", bold=True))

    n_steps = [
        (44, 100, 260, 68, "1 · Форматування рядка\n`sprintf` / `fmt.Sprintf`\nВиділення на купі (heap malloc)", POS),
        (330, 100, 260, 68, "2 · Захоплення замка\n`std::mutex.lock()`\nКонтеншн між усіма ядрами", POS),
        (616, 100, 290, 68, "3 · Синхронний сискол\n`write(fd, buf, len)`\nПотік чекає на заповнений pipe", POS),
    ]
    for x, y, w, h, txt, col in n_steps:
        f.append(fitbox(x, y, w, h, txt, size=11, stroke=col, fill="#ffffff", color=INK))

    f.append(arrow(306, 134, 328, 134, color=GRAY, sw=1.6))
    f.append(arrow(592, 134, 614, 134, color=GRAY, sw=1.6))

    f.append(fitbox(44, 182, 862, 54,
                    "Наслідок: 200–800 нс на запис, сплески затримки GC через мільйони дрібних рядків,\n"
                    "деградація пропускної здатності сервісу у 2–4 рази під навантаженням.",
                    size=11, stroke=POS, fill="#ffffff", color=POS))

    # Нижня половина: Нуль-алокаційний логер
    f.append(rect(24, 270, 912, 230, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(44, 296, "НУЛЬ-АЛОКАЦІЙНИЙ ЛОГЕР (Попередньо виділений буфер + SPSC кільце + фоновий батчинг)",
                  size=12.5, color=FIELD, anchor="start", bold=True))

    z_steps = [
        (44, 314, 260, 78, "1 · Кодування в стек/пул\nПрямий запис байтів у буфер\n0 виділень пам'яті (0 allocs)", FIELD),
        (330, 314, 260, 78, "2 · Беззамкова черга\nLock-free Ring Buffer\nАтомарний рух покажчика", FIELD),
        (616, 314, 290, 78, "3 · Фоновий записувач\n`writev()` пакетів по 64 КБ\nРобочі потоки вільні негайно", FIELD),
    ]
    for x, y, w, h, txt, col in z_steps:
        f.append(fitbox(x, y, w, h, txt, size=11, stroke=col, fill="#ffffff", color=INK))

    f.append(arrow(306, 353, 328, 353, color=GRAY, sw=1.6))
    f.append(arrow(592, 353, 614, 353, color=GRAY, sw=1.6))

    f.append(fitbox(44, 406, 862, 76,
                    "Результат: 10–35 нс на запис (у 20 разів швидше), нульове навантаження на Garbage Collector,\n"
                    "стабільний p99.9 час реакції мікросервісу навіть за інтенсивного логування.",
                    size=11.5, stroke=FIELD, fill="#ffffff", color=FIELD, bold=True))

    render(os.path.join(IMG, "zero-alloc-architecture.svg"), W, H, *f)


# ── 6. Ієрархія та фільтрація рівнів логування ─────────────────────────────────
def fig_log_levels():
    W, H = 940, 450
    f = [text(W / 2, 30, "Ієрархія рівнів логування та рання фільтрація", size=16, bold=True)]

    levels = [
        (40,  130, "TRACE", "1", "Детальний потік коду,\nкроки циклів, дампи", GRAY, "#f4f6f8"),
        (185, 130, "DEBUG", "2", "Діагностика для розробки,\nпараметри функцій", GRAY, "#f4f6f8"),
        (330, 130, "INFO",  "3", "Ключові бізнес-події,\nстарт, зупинка, операції", FIELD, "#eafaf1"),
        (475, 130, "WARN",  "4", "Нештатні ситуації,\nповтори, деградація", AMBER, "#fdf6e3"),
        (620, 130, "ERROR", "5", "Збій операції,\nпомилка запиту клієнта", POS, "#fdecea"),
        (765, 130, "FATAL", "6", "Аварія застосунку,\nнеможливість роботи", POS, "#fdecea"),
    ]

    for x, w, name_l, num_l, desc_l, col, bg_col in levels:
        f.append(rect(x, 66, w, 140, fill=bg_col, stroke=col, sw=1.8, rx=8))
        f.append(text(x + w / 2, 94, name_l, size=14, color=col, bold=True))
        f.append(text(x + w / 2, 114, "рівень " + num_l, size=10.5, color=MUTED))
        f.append(fitbox(x + 6, 126, w - 12, 70, desc_l, size=10.5, stroke=col, fill="#ffffff"))

    # Поріг відсікання
    f.append(line(325, 56, 325, 218, color=POS, sw=3, dash="6 4"))
    f.append(text(325, 236, "▲ Поточний поріг (INFO) — усе лівіше відкидається миттєво", size=11.5,
                  color=POS, bold=True))

    # Нижня панель: правило ранньої перевірки
    py = 256
    f.append(rect(24, py, W - 48, 170, fill=PANEL, stroke=NEG, sw=1.6, rx=10))
    f.append(text(44, py + 28, "Головний закон швидкодії: перевірка рівня ДО обчислення параметрів", size=13,
                  color=NEG, anchor="start", bold=True))

    f.append(fitbox(44, py + 44, 852, 46,
                    'if (logger.IsEnabled(Level::Debug)) { logger.Debug("payload", ExpensiveSerialize(large_object)); }\n'
                    'Або через ліниві лямбди / вирази: logger.Debug("payload", [&]{ return ExpensiveSerialize(obj); });',
                    size=11, stroke=LINE, fill="#ffffff"))

    f.append(text(44, py + 116,
                  "Без цієї перевірки виклик `logger.Debug(\"data: \" + serialize(obj))` виконає дорогу серіалізацію на кожній ітерації,",
                  size=11.5, color=INK, anchor="start"))
    f.append(text(44, py + 138,
                  "навіть якщо рівень DEBUG вимкнено в конфігурації. Логер має відсікати неактивні рівні за 1 такт CPU.",
                  size=11.5, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, "log-level-hierarchy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_text_vs_structured()
    fig_ingestion_pipeline()
    fig_observability_triangle()
    fig_context_propagation()
    fig_zero_alloc_encoder()
    fig_log_levels()
    print("готово:", IMG)
