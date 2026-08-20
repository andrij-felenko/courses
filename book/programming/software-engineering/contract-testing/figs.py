# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#fdecea"
COLD = "#eef4ff"
GRN  = "#eafaf1"
WARN = "#fff8e1"


# ── Фігура 1: дилема інтеграції ──────────────────────────────────────────────
def fig_integration_dilemma():
    W, H = 1080, 500
    frags = []

    frags.append(text(W / 2, 40, "Три підходи до перевірки міжсервісних стиків", size=17, bold=True))

    panels = [
        (40,  "Наскрізні тести (E2E)",
         ["3+ сервіси разом у тестовому", "середовищі; висока вартість,", "миготіння, пошук серед тисяч рядків"],
         HOT, POS, "Зона підозри: вся мережа"),
        (380, "Ізольовані моки",
         ["Кожен сервіс окремо; замість", "сусідів — вигадані стаби. Швидко,", "але моки тихо дрейфують від реальності"],
         WARN, "#b8860b", "Ризик: хибнозелені тести"),
        (720, "Контрактні тести",
         ["Два швидкі ізольовані тести,", "пов'язані єдиним виконуваним", "артефактом-контрактом у CI"],
         GRN, FIELD, "Ізоляція + доведена сумісність"),
    ]

    PW, PH = 320, 360
    PY = 75

    for px, title, desc, bg_col, stroke_col, verdict in panels:
        frags.append(rect(px, PY, PW, PH, fill=BG, stroke=stroke_col, sw=2, rx=8))
        frags.append(text(px + PW / 2, PY + 32, title, size=15, bold=True, color=stroke_col))
        frags.append(line(px + 20, PY + 48, px + PW - 20, PY + 48, color=MUTED, sw=1))

        # Схематичний малюнок усередині панелі
        if title.startswith("Наскрізні"):
            box1, _, _ = textbox(px + 65, PY + 100, "Сервіс А", size=11, fill=COLD, stroke=NEG, pad=8)
            box2, _, _ = textbox(px + 160, PY + 100, "Сервіс Б", size=11, fill=COLD, stroke=NEG, pad=8)
            box3, _, _ = textbox(px + 255, PY + 100, "Сервіс В", size=11, fill=COLD, stroke=NEG, pad=8)
            frags.extend([box1, box2, box3])
            frags.append(arrow(px + 100, PY + 100, px + 125, PY + 100, color=NEG, sw=1.5))
            frags.append(arrow(px + 195, PY + 100, px + 220, PY + 100, color=NEG, sw=1.5))
            frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 4"/>' % (px + 20, PY + 68, PW - 40, 68, POS))
            frags.append(text(px + PW / 2, PY + 152, "спільне важке середовище", size=11, italic=True, color=POS))
        elif title.startswith("Ізольовані"):
            box1, _, _ = textbox(px + 80, PY + 100, "Сервіс А", size=11, fill=COLD, stroke=NEG, pad=8)
            box2, _, _ = textbox(px + 230, PY + 100, "Ручний мок Б", size=11, fill=WARN, stroke="#b8860b", pad=8)
            frags.extend([box1, box2])
            frags.append(arrow(px + 125, PY + 100, px + 175, PY + 100, color="#b8860b", sw=1.5))
            frags.append(text(px + PW / 2, PY + 152, "віра в поведінку без перевірки", size=11, italic=True, color="#b8860b"))
        else:
            box1, _, _ = textbox(px + 75, PY + 88, "Тест А", size=10, fill=COLD, stroke=NEG, pad=6)
            box_c, _, _ = textbox(px + PW / 2, PY + 115, "Контракт", size=11, bold=True, fill=GRN, stroke=FIELD, pad=6)
            box2, _, _ = textbox(px + 245, PY + 88, "Тест Б", size=10, fill=COLD, stroke=NEG, pad=6)
            frags.extend([box1, box_c, box2])
            frags.append(arrow(px + 105, PY + 92, px + 118, PY + 110, color=FIELD, sw=1.5))
            frags.append(arrow(px + 202, PY + 110, px + 215, PY + 92, color=FIELD, sw=1.5))
            frags.append(text(px + PW / 2, PY + 152, "обидва звіряються з одним файлом", size=11, italic=True, color=FIELD))

        frags.append(mtext(px + PW / 2, PY + 200, desc, size=12, lh=1.4, color=INK))

        vbox, _, _ = textbox(px + PW / 2, PY + 310, verdict, size=12, bold=True, fill=bg_col, stroke=stroke_col, pad=10)
        frags.append(vbox)

    frags.append(text(W / 2, 475,
                      "Контрактний тест розділяє інтеграцію на дві локальні перевірки без розгортання спільного стенда.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'integration-dilemma.svg'), W, H, *frags,
           title="Дилема інтеграції: наскрізні тести, моки та контрактні тести")


# ── Фігура 2: життєвий цикл Consumer-Driven Contracts ────────────────────────
def fig_consumer_driven_flow():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 38, "Життєвий цикл контракту, керованого споживачем (CDC)", size=17, bold=True))

    # Ліва колонка: Споживач
    frags.append(rect(40, 70, 310, 390, fill=BG, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(195, 100, "1. Споживач (Consumer)", size=15, bold=True, color=NEG))

    c_box1, _, _ = textbox(195, 160, ["Модульний тест споживача", "викликає локальний Mock-сервер"], size=12, fill=COLD, stroke=NEG, pad=10)
    c_box2, _, _ = textbox(195, 270, ["Генерація артефакту", "Файл контракту (pact.json)", "фіксує мінімальні очікування"], size=12, fill=GRN, stroke=FIELD, pad=10)
    c_box3, _, _ = textbox(195, 390, ["Публікація в Брокер", "Версія клієнта + контракт"], size=12, fill=FILL, stroke=MUTED, pad=10)

    frags.extend([c_box1, c_box2, c_box3])
    frags.append(arrow(195, 205, 195, 225, color=NEG, sw=1.8))
    frags.append(arrow(195, 320, 195, 350, color=FIELD, sw=1.8))

    # Центральна колонка: Брокер контрактів
    frags.append(rect(385, 130, 310, 270, fill="#fafbfc", stroke="#6c5ce7", sw=2, rx=8))
    frags.append(text(540, 165, "2. Брокер контрактів", size=15, bold=True, color="#6c5ce7"))
    frags.append(text(540, 190, "(Pact Broker / Registry)", size=12, italic=True, color=MUTED))

    b_box1, _, _ = textbox(540, 250, ["Збереження контрактів", "Матриця сумісності версій", "Статуси верифікації"], size=12, fill="#f3f0ff", stroke="#6c5ce7", pad=10)
    b_box2, _, _ = textbox(540, 345, ["Шлюз релізу (can-i-deploy)", "Перевірка матриці перед деплоєм"], size=12, bold=True, fill=GRN, stroke=FIELD, pad=8)
    frags.extend([b_box1, b_box2])

    # Стрілка від споживача до брокера
    frags.append(arrow(350, 390, 430, 390, color=FIELD, sw=2))

    # Права колонка: Постачальник
    frags.append(rect(730, 70, 310, 390, fill=BG, stroke=POS, sw=1.8, rx=8))
    frags.append(text(885, 100, "3. Постачальник (Provider)", size=15, bold=True, color=POS))

    p_box1, _, _ = textbox(885, 160, ["Стягування контрактів", "Отримання очікувань усіх клієнтів"], size=12, fill=FILL, stroke=MUTED, pad=10)
    p_box2, _, _ = textbox(885, 270, ["Верифікаційний раннер", "Налаштування стану (Provider State)", "Відтворення запитів проти реального API"], size=12, fill=COLD, stroke=NEG, pad=10)
    p_box3, _, _ = textbox(885, 390, ["Публікація результату", "Успіх / невдача верифікації"], size=12, fill=GRN, stroke=FIELD, pad=10)

    frags.extend([p_box1, p_box2, p_box3])
    frags.append(arrow(885, 205, 885, 220, color=NEG, sw=1.8))
    frags.append(arrow(885, 325, 885, 355, color=FIELD, sw=1.8))

    # Стрілки між брокером і постачальником
    frags.append(arrow(695, 230, 730, 180, color="#6c5ce7", sw=1.8))
    frags.append(arrow(730, 390, 695, 360, color=FIELD, sw=1.8))

    frags.append(text(W / 2, 495,
                      "Споживач формує контракт на основі своїх потреб; постачальник доводить сумісність у своєму CI.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'consumer-driven-flow.svg'), W, H, *frags,
           title="Життєвий цикл Consumer-Driven Contracts: від тесту клієнта до шлюзу can-i-deploy")


# ── Фігура 3: асиметрія зіставлення (Закон Постела) ─────────────────────────
def fig_matching_rules_asymmetry():
    W, H = 1080, 490
    frags = []

    frags.append(text(W / 2, 38, "Асиметрія контракту: споживач фіксує лише те, що читає", size=17, bold=True))

    # Ліва частина: Повна відповідь постачальника
    frags.append(rect(40, 75, 420, 355, fill=BG, stroke=MUTED, sw=1.8, rx=8))
    frags.append(text(250, 105, "Повна відповідь постачальника (8 полів)", size=14, bold=True, color=INK))

    fields = [
        ("id: 42", True, "Споживач А і Б"),
        ("status: \"active\"", True, "Споживач А"),
        ("balance: 1500.50", True, "Споживач Б"),
        ("currency: \"UAH\"", False, "ніхто не читає"),
        ("created_at: 1714567890", False, "ніхто не читає"),
        ("tier: \"gold\"", False, "ніхто не читає"),
        ("internal_flags: 0x0F", False, "деталь реалізації"),
        ("debug_trace: null", False, "деталь реалізації"),
    ]

    for i, (fname, used, note) in enumerate(fields):
        fy = 135 + i * 35
        fbg = COLD if used else "#f5f6f8"
        fstroke = NEG if used else "#d5d8dd"
        frags.append(rect(60, fy, 380, 28, fill=fbg, stroke=fstroke, sw=1.2, rx=4))
        frags.append(text(75, fy + 18, fname, size=12, bold=used, color=INK, anchor="start"))
        frags.append(text(420, fy + 18, note, size=11, italic=True, color=MUTED if not used else FIELD, anchor="end"))

    # Центральні стрілки вибірковості
    frags.append(arrow(470, 190, 550, 150, color=NEG, sw=2))
    frags.append(arrow(470, 270, 550, 310, color=FIELD, sw=2))

    # Права частина зверху: Контракт Споживача А
    frags.append(rect(560, 75, 480, 160, fill=BG, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(800, 102, "Контракт Споживача А (мобільний застосунок)", size=13, bold=True, color=NEG))
    a_box, _, _ = textbox(800, 165,
                          ["Очікує лише: id (int), status (string)",
                           "Правило: TypeMatcher (значення може змінюватися)",
                           "Байдуже до balance, tier, created_at, flags"],
                          size=11, fill=COLD, stroke=NEG, pad=10)
    frags.append(a_box)

    # Права частина знизу: Контракт Споживача Б
    frags.append(rect(560, 255, 480, 175, fill=BG, stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(800, 282, "Контракт Споживача Б (білінговий сервіс)", size=13, bold=True, color=FIELD))
    b_box, _, _ = textbox(800, 350,
                          ["Очікує лише: id (int), balance (number >= 0)",
                           "Правило: id == integer, balance == decimal",
                           "Байдуже до status, tier, created_at, flags"],
                          size=11, fill=GRN, stroke=FIELD, pad=10)
    frags.append(b_box)

    frags.append(text(W / 2, 465,
                      "Постачальник може вільно видаляти чи модифікувати поля, яких немає в жодному контракті.",
                      size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, 'matching-rules-asymmetry.svg'), W, H, *frags,
           title="Асиметрія зіставлення: споживач вимагає лише власну підмножину схеми")


# ── Фігура 4: механізм стану постачальника (Provider State) ──────────────────
def fig_provider_state():
    W, H = 1080, 480
    frags = []

    frags.append(text(W / 2, 38, "Механізм налаштування стану постачальника (Provider State)", size=17, bold=True))

    # Блок контракту
    c_box, cw, ch = textbox(180, 240,
                            ["Контракт (Pact-файл)",
                             "─" * 24,
                             "Given: \"user 42 has balance 150\"",
                             "When: GET /users/42/balance",
                             "Then: 200 OK",
                             "Body: { balance: 150.0 }"],
                            size=12, fill=GRN, stroke=FIELD, sw=2, pad=14)
    frags.append(c_box)

    # Центральні етапи верифікації
    frags.append(rect(390, 80, 310, 340, fill=BG, stroke=MUTED, sw=1.8, rx=8))
    frags.append(text(545, 110, "Верифікаційний раннер", size=14, bold=True))

    s1, _, _ = textbox(545, 165, ["1. Виклик обробника стану", "State: \"user 42 has balance 150\""], size=11, fill=WARN, stroke="#b8860b", pad=8)
    s2, _, _ = textbox(545, 255, ["2. Виконання HTTP-запиту", "GET /users/42/balance"], size=11, fill=COLD, stroke=NEG, pad=8)
    s3, _, _ = textbox(545, 345, ["3. Звірка відповіді", "Status == 200, Body ~= contract"], size=11, fill=GRN, stroke=FIELD, pad=8)
    frags.extend([s1, s2, s3])
    frags.append(arrow(545, 200, 545, 222, color=MUTED, sw=1.5))
    frags.append(arrow(545, 290, 545, 312, color=MUTED, sw=1.5))

    # Стрілки від контракту до раннера
    frags.append(arrow(180 + cw / 2 + 5, 215, 390, 165, color="#b8860b", sw=1.8))
    frags.append(arrow(180 + cw / 2 + 5, 240, 390, 255, color=NEG, sw=1.8))
    frags.append(arrow(180 + cw / 2 + 5, 265, 390, 345, color=FIELD, sw=1.8))

    # Права частина: Сервіс постачальника
    frags.append(rect(760, 80, 280, 340, fill=BG, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(900, 110, "Сервіс постачальника", size=14, bold=True, color=NEG))

    db_box, _, _ = textbox(900, 165, ["Тестова БД / Fixtures", "Вставка запису: user 42,", "active, balance = 150"], size=11, fill="#f3f0ff", stroke="#6c5ce7", pad=8)
    api_box, _, _ = textbox(900, 255, ["Контролер API", "Реальна бізнес-логіка", "Читання з БД → JSON"], size=11, fill=COLD, stroke=NEG, pad=8)
    resp_box, _, _ = textbox(900, 345, ["HTTP Відповідь", "200 { \"balance\": 150.0 }"], size=11, fill=GRN, stroke=FIELD, pad=8)
    frags.extend([db_box, api_box, resp_box])

    # Зв'язки між раннером і сервісом
    frags.append(arrow(700, 165, 785, 165, color="#b8860b", sw=1.8))
    frags.append(arrow(700, 255, 785, 255, color=NEG, sw=1.8))
    frags.append(arrow(785, 345, 700, 345, color=FIELD, sw=1.8))

    frags.append(text(W / 2, 455,
                      "Provider State готує детерміноване середовище перед кожним запитом без глобального скидання БД.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'provider-state-mechanism.svg'), W, H, *frags,
           title="Механізм стану постачальника (Provider State)")


# ── Фігура 5: перевірений фейк (Verified Fake) ──────────────────────────────
def fig_verified_fake():
    W, H = 1080, 480
    frags = []

    frags.append(text(W / 2, 38, "Перевірений дублер (Verified Fake): один набір тестів на дві реалізації", size=17, bold=True))

    suite_box, sw, sh = textbox(210, 240,
                                ["Параметризований набір", "контрактних тестів",
                                 "─" * 24,
                                 "• save() зберігає сутність",
                                 "• find_by_id() знаходить збережене",
                                 "• дубльований ID кидає конфлікт",
                                 "• неіснуючий ID повертає null"],
                                size=12, fill=FILL, stroke=INK, sw=2, pad=14)
    frags.append(suite_box)

    # Гілка 1: Fake Repository (в пам'яті)
    frags.append(rect(480, 80, 560, 150, fill=BG, stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(500, 110, "Реалізація А: InMemoryFakeRepository", size=14, bold=True, color=FIELD, anchor="start"))
    f_box, _, _ = textbox(720, 165,
                          ["Хеш-таблиця на стеку/купі", "Час прогону: 2 мс", "Використовується в unit-тестах споживача щосекунди"],
                          size=11, fill=GRN, stroke=FIELD, pad=10)
    frags.append(f_box)
    v1_box, _, _ = textbox(980, 165, ["Контракт", "виконано", "✓ 2 мс"], size=11, bold=True, fill=GRN, stroke=FIELD, pad=8)
    frags.append(v1_box)

    # Гілка 2: Real Database Repository
    frags.append(rect(480, 260, 560, 150, fill=BG, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(500, 290, "Реалізація Б: PostgresSqlRepository", size=14, bold=True, color=NEG, anchor="start"))
    r_box, _, _ = textbox(720, 345,
                          ["Справжня СУБД / транзакції / драйвер", "Час прогону: 250 мс", "Ганяється в CI перед злиттям гілки"],
                          size=11, fill=COLD, stroke=NEG, pad=10)
    frags.append(r_box)
    v2_box, _, _ = textbox(980, 345, ["Контракт", "виконано", "✓ 250 мс"], size=11, bold=True, fill=COLD, stroke=NEG, pad=8)
    frags.append(v2_box)

    # Стрілки від набору до реалізацій
    frags.append(arrow(210 + sw / 2 + 5, 210, 480, 155, color=FIELD, sw=2))
    frags.append(arrow(210 + sw / 2 + 5, 270, 480, 335, color=NEG, sw=2))

    frags.append(text(W / 2, 455,
                      "Один тестовий набір гарантує, що легкий дублер і важкий бойовий драйвер поводяться однаково.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'verified-fake-dual-run.svg'), W, H, *frags,
           title="Перевірений фейк: ідентичний набір перевірок для бойового адаптера і дублера")


# ── Фігура 6 (вставка hist): еволюція від моків до Pact ──────────────────────
def fig_cdc_timeline():
    W, H = 1080, 640
    frags = []

    frags.append(text(W / 2, 42, "Еволюція контрактного тестування: від моків до розподіленого брокера", size=17, bold=True))

    rows = [
        ("2000", "Mackinnon, Freeman, Craig: «Endo-Testing: Unit Testing with Mock Objects»\n"
                 "Виникає потреба перевіряти очікування від співпрацівників у межах одного процесу"),
        ("2006", "Ian Robinson (ThoughtWorks): стаття «Consumer-Driven Contracts: A Service Design Pattern»\n"
                 "Формулювання ідеї: споживач публікує власні очікування, щоб постачальник не ламав клієнтів"),
        ("2011", "Martin Fowler: формалізація «Contract Test»\n"
                 "Окремий клас тестів на межі зовнішніх сервісів та для верифікації тестових дублерів"),
        ("2013", "Beth Skurrie, Ron Holshausen (realestate.com.au / DiUS): створення Pact\n"
                 "Перший виконуваний JSON-формат контракту та mock-сервер для автоматичного запису очікувань"),
        ("2017+", "Pact Broker, матриця сумісності can-i-deploy та специфікації Pact v3/v4\n"
                  "Підтримка бінарних повідомлень, черг подій (Kafka/RabbitMQ), gRPC та Protobuf"),
    ]

    AX = 260
    y0, step = 115, 95
    frags.append(line(AX, y0 - 30, AX, y0 + step * (len(rows) - 1) + 30, color=MUTED, sw=2.2))

    for i, (when, what) in enumerate(rows):
        cy = y0 + step * i
        frags.append(text(220, cy + 5, when, size=15, bold=True, anchor="end"))
        frags.append(circle(AX, cy, 9, fill=BG, stroke=NEG if i == 3 else INK, sw=2.4))
        frags.append(fitbox(300, cy - 35, 730, 70, what, size=13,
                            fill=GRN if i == 3 else (COLD if i >= 1 else FILL),
                            stroke=FIELD if i == 3 else MUTED, sw=1.6))

    frags.append(text(W / 2, H - 25,
                      "Контрактні тести перетворили неформальні домовленості команд на машинно перевірювані артефакти в CI.",
                      size=13, color=INK))

    render(os.path.join(IMG, 'cdc-evolution-timeline.svg'), W, H, *frags,
           title="Хронологія розвитку контрактного тестування")


# ── Фігура 7 (вставка proj): архітектура тестового стенда ────────────────────
def fig_harness_replay():
    W, H = 1080, 470
    frags = []

    frags.append(text(W / 2, 40, "Архітектура відтворення контрактів у тестовому стенді", size=17, bold=True))

    c_box, cw, ch = textbox(160, 220,
                            ["Файл контракту", "pact.json", "─" * 16, "Запити, очікувані", "відповіді та матчери"],
                            size=12, fill=GRN, stroke=FIELD, sw=2, pad=12)
    frags.append(c_box)

    h_box, hw, hh = textbox(460, 220,
                            ["Раннер стенда (Harness)", "─" * 24, "1. Парсинг JSON-контракту",
                             "2. Виклик State Callback", "3. Виконання HTTP-запиту", "4. Зіставлення JSON-схем"],
                            size=12, fill=COLD, stroke=NEG, sw=2, pad=12)
    frags.append(h_box)

    s_box, sw_b, sh_b = textbox(820, 150,
                                ["Сервіс під тестом", "(Provider Process)", "─" * 20, "Обробляє запит через", "реальний мережевий стек"],
                                size=12, fill=FILL, stroke=INK, sw=2, pad=12)
    frags.append(s_box)

    v_box, vw, vh = textbox(820, 310,
                            ["Звіт верифікації", "─" * 20, "✓ Статус-код збігся", "✓ Обов'язкові поля присутні", "✓ Типи даних коректні"],
                            size=12, fill=GRN, stroke=FIELD, sw=2, pad=12)
    frags.append(v_box)

    frags.append(arrow(160 + cw / 2 + 5, 220, 460 - hw / 2 - 5, 220, color=FIELD, sw=2))
    frags.append(arrow(460 + hw / 2 + 5, 180, 820 - sw_b / 2 - 5, 150, color=NEG, sw=2))
    frags.append(arrow(820 - sw_b / 2 - 5, 170, 460 + hw / 2 + 5, 200, color=MUTED, sw=1.5))
    frags.append(arrow(460 + hw / 2 + 5, 260, 820 - vw / 2 - 5, 310, color=FIELD, sw=2))

    frags.append(text(W / 2, 435,
                      "Раннер ізолює процес тестування: взаємодія відбувається через стандартні мережеві протоколи.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'harness-contract-replay.svg'), W, H, *frags,
           title="Архітектура відтворення контрактів у тестовому стенді")


if __name__ == '__main__':
    fig_integration_dilemma()
    fig_consumer_driven_flow()
    fig_matching_rules_asymmetry()
    fig_provider_state()
    fig_verified_fake()
    fig_cdc_timeline()
    fig_harness_replay()
    print("ok")
