# -*- coding: utf-8 -*-
"""Фігури теми «Фільтр повідомлень (Message Filter)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. filter-problem-scenario: наївна трансляція проти фільтрації ────────────
def fig_filter_problem_scenario():
    W, H = 1000, 440
    f = []

    # Ліва колонка: Наївна доставка без фільтра
    f.append(rect(15, 15, 475, 410, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(252, 45, "Без фільтра: параліч споживача непотрібним трафіком", size=12, bold=True, color=POS))

    # Джерело потоку зліва
    src1_box, _, _ = textbox(105, 155, "Шина подій\n(120 000 под/с)\n\n• Платежі США (40%)\n• Кліки UI (45%)\n• Логи датчиків (12.5%)\n• Податки ЄС (2.5%)",
                             size=9.5, bold=True, min_w=125, pad=6, fill=FILL, stroke=LINE)
    f.append(src1_box)

    # Канал
    f.append(rect(195, 130, 110, 50, fill=WARN_F, stroke="#d39e00", sw=1.5, rx=4))
    f.append(text(250, 150, "Мережа: 150 МБ/с", size=9.5, bold=True, color="#856404"))
    f.append(text(250, 168, "120k повідомлень/с", size=9, color="#856404"))
    f.append(arrow(170, 155, 192, 155, color="#d39e00", sw=1.5))
    f.append(arrow(308, 155, 330, 155, color=POS, sw=1.5))

    # Споживач зліва
    c1_box, _, _ = textbox(400, 155, "Податковий сервіс ЄС\n\n1. Socket I/O (150 МБ/с)\n2. JSON Deserialization\n3. if (region != 'EU') drop\n\n⚠ 97.5% CPU на сміття!",
                           size=9.5, bold=True, min_w=125, pad=6, fill=RED_F, stroke=POS)
    f.append(c1_box)

    f.append(text(252, 335, "✗ 97.5% мережевої смуги та пам'яті витрачається марно", size=10, color=POS, italic=True))
    f.append(text(252, 358, "✗ Зупинки GC, таймаути сокетів і лавинне випадання консюмерів", size=10, color=POS, italic=True))
    f.append(text(252, 381, "✗ Порушення ізоляції: споживач бачить чужі конфіденційні події", size=10, color=POS, italic=True))

    # Права колонка: Фільтр повідомлень у потоці
    f.append(rect(510, 15, 475, 410, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(747, 45, "З фільтром: точна доставка лише цільових подій", size=12, bold=True, color=FIELD))

    # Джерело потоку справа
    src2_box, _, _ = textbox(580, 155, "Шина подій\n(120 000 под/с)\n\n• Платежі США\n• Кліки UI\n• Датчики\n• Податки ЄС",
                             size=9.5, bold=True, min_w=110, pad=6, fill=FILL, stroke=LINE)
    f.append(src2_box)

    # Фільтр
    f.append(arrow(638, 155, 660, 155, color=LINE, sw=1.5))
    flt_box, _, _ = textbox(728, 155, "ФІЛЬТР ПОВІДОМЛЕНЬ\n(Message Filter)\n\nP(m) = (region == 'EU'\n        && type == 'TAX')\n\nВідсів: 97.5% (117k под/с)",
                            size=9, bold=True, min_w=125, pad=6, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(flt_box)

    # Канал відфільтрований
    f.append(arrow(795, 155, 820, 155, color=FIELD, sw=1.5))

    # Споживач чистий
    c2_box, _, _ = textbox(895, 155, "Податковий сервіс ЄС\n\n• Трафік: 3.7 МБ/с\n• 3 000 под/с (лише ЄС)\n• 100% CPU на корисну\n  бізнес-логіку",
                           size=9.5, bold=True, min_w=125, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(c2_box)

    # Стрілка скидання вниз від фільтра
    f.append(arrow(728, 215, 728, 245, color=MUTED, sw=1.3))
    drop_box, _, _ = textbox(728, 272, "Скидання (Drop / Ignore)\n117 000 непотрібних под/с\n(Без передачі в мережу споживача)",
                             size=9, min_w=190, pad=5, fill=FILL, stroke=MUTED)
    f.append(drop_box)

    f.append(text(747, 335, "✓ 97.5% економія мережевого трафіку та пам'яті клієнта", size=10, color=FIELD, italic=True))
    f.append(text(747, 358, "✓ Споживач стабільний і не перевантажується чужими піками", size=10, color=FIELD, italic=True))
    f.append(text(747, 381, "✓ Безпека: конфіденційні дані не залишають захищеного контуру", size=10, color=FIELD, italic=True))

    render(out("filter-problem-scenario.svg"), W, H, *f,
           title="Проблема широкомовного навантаження проти фільтрації повідомлень")


# ── 2. filter-placement-topology: топології розміщення фільтра ───────────────
def fig_filter_placement_topology():
    W, H = 1000, 420
    f = []

    f.append(rect(15, 15, 970, 390, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Три архітектурні рівні розміщення фільтра повідомлень", size=14, bold=True))

    # Секція 1: Продюсер (Producer-side)
    f.append(rect(35, 70, 295, 315, fill="#fdfefe", stroke=LINE, sw=1.2, rx=6))
    f.append(text(182, 95, "1. Фільтрація на джерелі (Producer)", size=11.5, bold=True, color=INK))

    p1_box, _, _ = textbox(182, 160, "Продюсер\n[Локальний предикат P(m)]\n(Публікація лише потрібного)",
                           size=9.5, bold=True, min_w=170, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(p1_box)

    f.append(arrow(182, 205, 182, 235, color=LINE, sw=1.3))

    b1_box, _, _ = textbox(182, 260, "Брокер / Мережа\n(Мінімальний трафік)",
                           size=9.5, min_w=150, pad=5, fill=FILL, stroke=MUTED)
    f.append(b1_box)

    f.append(text(182, 310, "• Нульове навантаження на мережу", size=9.5, color=FIELD))
    f.append(text(182, 330, "• Тісне зв'язування (tight coupling)", size=9.5, color=POS))
    f.append(text(182, 350, "• Непридатне для динамічних підписок", size=9.5, color=POS))

    # Секція 2: Брокер (Broker-side / Server-side)
    f.append(rect(352, 70, 295, 315, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(500, 95, "2. Серверний фільтр (Broker / Bus)", size=11.5, bold=True, color=FIELD))

    b2_box, _, _ = textbox(500, 160, "Брокер повідомлень / Шлюз\n[JMS Selectors / SNS Filter / CEL]\nМаршрутизація до черги споживача",
                           size=9.5, bold=True, min_w=200, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(b2_box)

    f.append(arrow(500, 205, 500, 235, color=FIELD, sw=1.3))

    c2_box, _, _ = textbox(500, 260, "Споживач (Consumer)\nОтримує лише збіги",
                           size=9.5, min_w=150, pad=5, fill=FILL, stroke=LINE)
    f.append(c2_box)

    f.append(text(500, 310, "• Повна розв'язаність продюсера і клієнта", size=9.5, color=FIELD))
    f.append(text(500, 330, "• Економія мережі та пам'яті клієнта", size=9.5, color=FIELD))
    f.append(text(500, 350, "• Витрата CPU брокера на парсинг", size=9.5, color="#856404"))

    # Секція 3: Клієнт (Consumer-side)
    f.append(rect(670, 70, 295, 315, fill="#fdfefe", stroke=LINE, sw=1.2, rx=6))
    f.append(text(817, 95, "3. Клієнтський фільтр (Consumer)", size=11.5, bold=True, color=INK))

    c3_box, _, _ = textbox(817, 160, "Споживач (In-process Interceptor)\n[Предикат у коді клієнта]\n(Доступ до БД, кешу, бізнес-об'єктів)",
                           size=9.5, bold=True, min_w=210, pad=6, fill=WARN_F, stroke="#d39e00")
    f.append(c3_box)

    f.append(arrow(817, 205, 817, 235, color=LINE, sw=1.3))

    h3_box, _, _ = textbox(817, 260, "Бізнес-обробник (Handler)\nОбробка відібраного",
                           size=9.5, min_w=150, pad=5, fill=FILL, stroke=LINE)
    f.append(h3_box)

    f.append(text(817, 310, "• Довільна складність бізнес-правил", size=9.5, color=FIELD))
    f.append(text(817, 330, "• Не навантажує центральний брокер", size=9.5, color=FIELD))
    f.append(text(817, 350, "• Максимальні втрати мережі та CPU", size=9.5, color=POS))

    render(out("filter-placement-topology.svg"), W, H, *f,
           title="Порівняння архітектурних рівнів розміщення фільтра")


# ── 3. filter-evaluation-internals: внутрішній рушій фільтрації ──────────────
def fig_filter_evaluation_internals():
    W, H = 1000, 420
    f = []

    f.append(rect(15, 15, 970, 390, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Внутрішній механізм рушія: швидкий шлях заголовків проти парсингу тіла", size=14, bold=True))

    # Вхідне повідомлення
    msg_box, _, _ = textbox(105, 175, "Вхідне повідомлення\n\n[Заголовки / Headers]\n• type: 'ORDER_PAID'\n• tenant_id: 1042\n• priority: 5\n\n[Тіло / Payload]\nJSON / Protobuf / Avro\n(2.5 КБ двійкових даних)",
                            size=9.5, bold=True, min_w=150, pad=6, fill=FILL, stroke=LINE)
    f.append(msg_box)

    # Розгалуження на швидкий і повільний шлях
    f.append(rect(235, 75, 450, 120, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(460, 98, "ШВИДКИЙ ШЛЯХ: Фільтрація за метаданими (Header Filtering)", size=11, bold=True, color=FIELD))
    f.append(text(460, 122, "• O(1) перевірка хеш-таблиці або бітової маски прапорців", size=9.5, color=INK))
    f.append(text(460, 142, "• Zero-Copy: тіло повідомлення НЕ десеріалізується і лишається в Page Cache", size=9.5, color=INK))
    f.append(text(460, 162, "• Пропускна здатність: > 1 000 000 перевірок/с на ядро CPU", size=9.5, bold=True, color=FIELD))

    f.append(rect(235, 215, 450, 130, fill=WARN_F, stroke="#d39e00", sw=1.5, rx=6))
    f.append(text(460, 238, "ПОВІЛЬНИЙ ШЛЯХ: Фільтрація за вмістом (Content-Based Filtering)", size=11, bold=True, color="#856404"))
    f.append(text(460, 262, "• Повне розпакування JSON/XML/Protobuf у дерево об'єктів пам'яті", size=9.5, color=INK))
    f.append(text(460, 282, "• Обчислення виразів XPath / JSONPath / AST / CEL над полями", size=9.5, color=INK))
    f.append(text(460, 302, "• Виділення пам'яті (allocations), тиск на GC, втрата Zero-Copy", size=9.5, color=POS))
    f.append(text(460, 322, "• Пропускна здатність: ~ 15 000 – 50 000 перевірок/с на ядро", size=9.5, bold=True, color=POS))

    f.append(arrow(185, 160, 230, 135, color=FIELD, sw=1.5))
    f.append(arrow(185, 190, 230, 270, color="#d39e00", sw=1.5))

    # Результат обчислення предикату
    f.append(arrow(690, 135, 735, 160, color=LINE, sw=1.5))
    f.append(arrow(690, 270, 735, 210, color=LINE, sw=1.5))

    dec_box, _, _ = textbox(785, 185, "Оцінка P(m)\n\nTRUE / FALSE\nчи Помилка",
                            size=10, bold=True, min_w=90, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(dec_box)

    # Виходи
    f.append(arrow(835, 165, 875, 115, color=FIELD, sw=1.5))
    out_pass, _, _ = textbox(925, 110, "TRUE: Пропуск\n→ Вихідний канал\n(Споживач)",
                             size=9, bold=True, min_w=85, pad=5, fill=GREEN_F, stroke=FIELD)
    f.append(out_pass)

    f.append(arrow(835, 185, 875, 185, color=MUTED, sw=1.5))
    out_drop, _, _ = textbox(925, 185, "FALSE: Скидання\n→ Метрики лічильника\n(Drop/Ignore)",
                             size=9, min_w=85, pad=5, fill=FILL, stroke=MUTED)
    f.append(out_drop)

    f.append(arrow(835, 205, 875, 255, color=POS, sw=1.5))
    out_err, _, _ = textbox(925, 260, "ПОМИЛКА: Карантин\n→ Мертва черга (DLQ)\n(Fail-safe політика)",
                            size=9, bold=True, min_w=85, pad=5, fill=RED_F, stroke=POS)
    f.append(out_err)

    render(out("filter-evaluation-internals.svg"), W, H, *f,
           title="Швидкий та повільний шляхи виконання фільтра повідомлень")


# ── 4. filter-pipeline-composition: композиція конвеєра фільтрів ─────────────
def fig_filter_pipeline_composition():
    W, H = 1000, 390
    f = []

    f.append(rect(15, 15, 970, 360, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Конвеєр фільтрів (Filter Chain): послідовне звуження потоку", size=14, bold=True))

    # Стадії конвеєра зліва направо
    # Вхід
    in_box, _, _ = textbox(65, 175, "Вхідний потік\n\n100 000 под/с\n(100%)",
                           size=9.5, bold=True, min_w=85, pad=5, fill=FILL, stroke=LINE)
    f.append(in_box)
    f.append(arrow(115, 175, 145, 175, color=LINE, sw=1.5))

    # Стадія 1: Schema Version
    s1_box, _, _ = textbox(215, 175, "1. Схема / Формат\n\nПеревірка версії\nSchema ID in (2, 3)\n(Дешевий заголовок)",
                           size=9.5, bold=True, min_w=115, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(s1_box)
    f.append(arrow(215, 230, 215, 270, color=POS, sw=1.2))
    f.append(text(215, 290, "Drop legacy (5%)", size=9.5, color=POS))

    f.append(arrow(280, 175, 310, 175, color=LINE, sw=1.5))
    f.append(text(295, 160, "95 000", size=9, color=MUTED))

    # Стадія 2: Tenant Security
    s2_box, _, _ = textbox(380, 175, "2. Безпека орендаря\n\nПеревірка прав\ntenant_id == ctx.id\n(Ізоляція даних)",
                           size=9.5, bold=True, min_w=115, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(s2_box)
    f.append(arrow(380, 230, 380, 270, color=POS, sw=1.2))
    f.append(text(380, 290, "Drop чужі (60%)", size=9.5, color=POS))

    f.append(arrow(445, 175, 475, 175, color=LINE, sw=1.5))
    f.append(text(460, 160, "38 000", size=9, color=MUTED))

    # Стадія 3: Deduplication (Stateful)
    s3_box, _, _ = textbox(550, 175, "3. Дедуплікація\n\nФільтр Блума + LRU\nКовзне вікно 60 с\n(Відсів повторів)",
                           size=9.5, bold=True, min_w=115, pad=6, fill=WARN_F, stroke="#d39e00")
    f.append(s3_box)
    f.append(arrow(550, 230, 550, 270, color=POS, sw=1.2))
    f.append(text(550, 290, "Drop дублікати (8%)", size=9.5, color=POS))

    f.append(arrow(615, 175, 645, 175, color=LINE, sw=1.5))
    f.append(text(630, 160, "34 960", size=9, color=MUTED))

    # Стадія 4: Business Predicate
    s4_box, _, _ = textbox(720, 175, "4. Бізнес-предикат\n\nЦіна > 5000 грн\nstatus == 'PAID'\n(Доменна логіка)",
                           size=9.5, bold=True, min_w=115, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(s4_box)
    f.append(arrow(720, 230, 720, 270, color=POS, sw=1.2))
    f.append(text(720, 290, "Drop нецільові (85%)", size=9.5, color=POS))

    f.append(arrow(785, 175, 820, 175, color=FIELD, sw=1.5))
    f.append(text(802, 160, "5 244", size=9, color=FIELD, bold=True))

    # Вихід
    out_box, _, _ = textbox(895, 175, "Цільовий сервіс\n\n5 244 под/с\n(5.2% від входу)\nЧисті валідні дані",
                            size=9.5, bold=True, min_w=105, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(out_box)

    f.append(text(500, 345, "Принцип Fail-Fast: найдешевші фільтри заголовків стоять першими, дорогі предикати й стан — останніми",
                  size=10.5, color=FIELD, bold=True))

    render(out("filter-pipeline-composition.svg"), W, H, *f,
           title="Композиція конвеєра фільтрації з раннім скиданням")


if __name__ == "__main__":
    fig_filter_problem_scenario()
    fig_filter_placement_topology()
    fig_filter_evaluation_internals()
    fig_filter_pipeline_composition()
    print("All figures generated successfully.")
