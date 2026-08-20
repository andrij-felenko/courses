# -*- coding: utf-8 -*-
"""Фігури до теми «Ідемпотентність у розподілених системах»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / подвійна мутація
COOL = "#eaf0fd"   # нейтральне / пояснення / стан
GOOD = "#e8f6ee"   # успіх / ідемпотентний результат


# ── 1. Невизначеність повтору через втрату відповіді ────────────────────────
def two_generals_retry_ambiguity():
    W, H = 1180, 620
    f = []

    # Заголовок зверху
    f.append(fitbox(40, 24, 1100, 48,
                    "НЕВИЗНАЧЕНІСТЬ ПОВТОРУ: втрата відповіді виглядає так само, як втрата запиту",
                    size=14, bold=True, fill=COOL))

    # Ліва колонка: Клієнт
    cx = 120.0
    f.append(fitbox(cx - 70, 90, 140, 44, "КЛІЄНТ", size=13, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))
    f.append(line(cx, 134, cx, 520, color=MUTED, sw=1.5, dash="6,6"))

    # Права колонка: Сервер
    sx = 560.0
    f.append(fitbox(sx - 70, 90, 140, 44, "СЕРВЕР", size=13, bold=True, fill="#ffffff", stroke=LINE, sw=1.6))
    f.append(line(sx, 134, sx, 520, color=MUTED, sw=1.5, dash="6,6"))

    # 1-й запит
    f.append(arrow(cx, 170, sx, 200, color=FIELD, sw=2))
    f.append(text((cx + sx) / 2, 175, "POST /charge {order: 42, sum: 1000}", size=12, color=FIELD, bold=True))

    # Виконання на сервері
    f.append(rect(sx - 12, 195, 24, 60, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text(sx + 22, 230, "списано 1000 грн", size=12, color=FIELD, anchor="start", bold=True))

    # Загублена відповідь
    f.append(line(sx, 255, (cx + sx) / 2 + 30, 280, color=POS, sw=2, dash="4,4"))
    f.append(line((cx + sx) / 2 + 10, 270, (cx + sx) / 2 + 35, 295, color=POS, sw=2.6))
    f.append(line((cx + sx) / 2 + 35, 270, (cx + sx) / 2 + 10, 295, color=POS, sw=2.6))
    f.append(text((cx + sx) / 2 + 45, 285, "обрив зв'язку / таймаут", size=12, color=POS, anchor="start", bold=True))

    # Клієнт бачить таймаут
    f.append(fitbox(cx - 85, 305, 170, 48, "ТАЙМАУТ\nчи списано гроші?", size=12, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Повторний запит
    f.append(arrow(cx, 370, sx, 400, color=NEG, sw=2))
    f.append(text((cx + sx) / 2, 375, "RETRY: POST /charge {order: 42, sum: 1000}", size=12, color=NEG, bold=True))

    # Права частина: два наслідки повтору
    rx = 740.0
    # Без ідемпотентності
    f.append(fitbox(rx, 160, 390, 150,
                    "БЕЗ ІДЕМПОТЕНТНОСТІ\n\n"
                    "• Сервер повторно виконує операцію\n"
                    "• З балансу знято 2000 грн замість 1000\n"
                    "• Стан бази даних спаплюжено дублем",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=2))

    # З ідемпотентністю
    f.append(fitbox(rx, 340, 390, 150,
                    "З ІДЕМПОТЕНТНІСТЮ\n\n"
                    "• Сервер розпізнає повтор за токеном\n"
                    "• Мутація стану НЕ повторюється\n"
                    "• Повертається збережений успіх (1000 грн)",
                    size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    # Стрілки від сервера до двох наслідків
    f.append(arrow(sx + 30, 240, rx - 10, 235, color=POS, sw=1.8))
    f.append(arrow(sx + 30, 410, rx - 10, 415, color=FIELD, sw=1.8))

    f.append(fitbox(40, 545, 1100, 52,
                    "часткова відмова робить повтори неминучими;\n"
                    "ідемпотентність — єдиний механізм, що робить неминучі повтори безпечними",
                    size=13, bold=True, fill=FILL))

    render(os.path.join(OUT, 'two-generals-retry-ambiguity.svg'), W, H, *f)


# ── 2. Природна проти синтезованої ідемпотентності ──────────────────────────
def natural_vs_synthesized():
    W, H = 1200, 640
    f = []

    f.append(fitbox(40, 24, 1120, 46,
                    "СПЕКТР ОПЕРАЦІЙ: від природної ідемпотентності до синтезованого стану",
                    size=14, bold=True, fill=COOL))

    cw = 345.0
    h = 440.0
    y = 90.0

    # Колонка 1: Природно ідемпотентні
    x1 = 40.0
    f.append(fitbox(x1, y, cw, 60, "ПРИРОДНО ІДЕМПОТЕНТНІ\nструктура дії зберігає стан", size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))
    items1 = [
        ("Абсолютне присвоєння", "x := 42\nповтор залишає x = 42"),
        ("Булеві прапорці й tombstones", "status := 'DELETED'\nповтор не міняє ознаки"),
        ("Операції над множинами", "S := S ∪ {user_id}\nповтор не подвоює елемент"),
        ("Монотонний максимум", "max_seen := max(max_seen, t)\nповтор не збільшує число"),
    ]
    iy = y + 70
    for title, desc in items1:
        f.append(fitbox(x1, iy, cw, 78, f"{title}\n{desc}", size=12, fill="#ffffff", stroke=FIELD, sw=1.3))
        iy += 86

    # Колонка 2: Неідемпотентні за природою
    x2 = x1 + cw + 35
    f.append(fitbox(x2, y, cw, 60, "НЕІДЕМПОТЕНТНІ ЗА СУТТЮ\nкожен виклик міняє стан", size=13, bold=True, fill=WARM, stroke=POS, sw=2))
    items2 = [
        ("Відносні дельти та лічильники", "balance := balance - 100\nповтор краде ще 100 грн"),
        ("Додавання до списку / черги", "list.append(order_item)\nповтор подвоює товар"),
        ("Генерація сутностей", "INSERT INTO orders ... (auto_id)\nповтор створює дубль"),
        ("Побічні ефекти назовні", "send_push_notification()\nповтор дратує людину"),
    ]
    iy = y + 70
    for title, desc in items2:
        f.append(fitbox(x2, iy, cw, 78, f"{title}\n{desc}", size=12, fill="#ffffff", stroke=POS, sw=1.3))
        iy += 86

    # Колонка 3: Синтезована ідемпотентність
    x3 = x2 + cw + 35
    f.append(fitbox(x3, y, cw, 60, "СИНТЕЗОВАНА ІДЕМПОТЕНТНІСТЬ\nміст через токен і реєстр", size=13, bold=True, fill=COOL, stroke=NEG, sw=2))
    items3 = [
        ("Детерміновані ключі", "id := hash(buyer, order_ref)\nINSERT IGNORE замість auto_id"),
        ("Автомат станів із лізою", "IN_PROGRESS → COMMITTED\nпаралельні дублі блокуються"),
        ("Збереження відбитка запиту", "хеш тіла звіряється на вході\nзахист від підміни параметрів"),
        ("Кешування результату", "повтору віддається старий 200\nбез повторної мутації"),
    ]
    iy = y + 70
    for title, desc in items3:
        f.append(fitbox(x3, iy, cw, 78, f"{title}\n{desc}", size=12, fill="#ffffff", stroke=NEG, sw=1.3))
        iy += 86

    # Стрілка синтезу між неідемпотентним і синтезованим
    f.append(fitbox(40, 555, 1120, 55,
                    "якщо операція не є ідемпотентною природно — її синтезують:\n"
                    "прив'язують до унікального токена запиту й проводять через транзакційний реєстр",
                    size=13, bold=True, fill=FILL))

    render(os.path.join(OUT, 'natural-vs-synthesized.svg'), W, H, *f)


# ── 3. Автомат стану ключа ідемпотентності ──────────────────────────────────
def idempotency_state_machine():
    W, H = 1200, 680
    f = []

    f.append(fitbox(40, 20, 1120, 44,
                    "ЖИТТЄВИЙ ЦИКЛ ТОКЕНА: атомарні переходи, блокування та повтори",
                    size=14, bold=True, fill=COOL))

    # Стан 1: ВІДСУТНІЙ (порожній)
    f.append(fitbox(60, 120, 200, 90, "НЕМАЄ ЗАПИСУ\nновий запит", size=13.5, bold=True, fill="#ffffff", stroke=MUTED, sw=1.6))

    # Стан 2: В ОБРОБЦІ (IN_PROGRESS)
    f.append(fitbox(460, 120, 280, 90, "В ОБРОБЦІ (IN_PROGRESS)\nвзято блокування / лізу TTL\nзбережено хеш запиту", size=13, bold=True, fill=COOL, stroke=NEG, sw=2))

    # Стан 3: ЗАФІКСОВАНО (COMMITTED)
    f.append(fitbox(900, 120, 240, 90, "ЗАФІКСОВАНО (COMMITTED)\nзбережено тіло відповіді\nоперацію завершено", size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2.2))

    # Стан 4: ПОМИЛКА (FAILED / RETRYABLE)
    f.append(fitbox(460, 390, 280, 90, "ЗБІЙ (FAILED)\nтимчасова помилка\n(можна повторити)", size=13, bold=True, fill=WARM, stroke=POS, sw=2))

    # Перехід 1: НЕМАЄ -> IN_PROGRESS
    f.append(arrow(260, 165, 455, 165, color=FIELD, sw=2.2))
    f.append(text(355, 145, "INSERT токена (CAS)", size=12, color=FIELD, bold=True))

    # Перехід 2: IN_PROGRESS -> COMMITTED
    f.append(arrow(740, 165, 895, 165, color=FIELD, sw=2.2))
    f.append(text(817, 145, "Успіх + UPDATE", size=12, color=FIELD, bold=True))

    # Перехід 3: IN_PROGRESS -> FAILED
    f.append(arrow(600, 210, 600, 385, color=POS, sw=2))
    f.append(text(615, 295, "Збій обробки", size=12, color=POS, bold=True, anchor="start"))

    # Перехід 4: FAILED -> IN_PROGRESS (повтор спроби)
    f.append(line(460, 435, 380, 435, color=NEG, sw=1.8))
    f.append(line(380, 435, 380, 185, color=NEG, sw=1.8))
    f.append(arrow(380, 185, 455, 185, color=NEG, sw=1.8))
    f.append(text(320, 310, "Повторний запит\nзняття збою", size=11.5, color=NEG, bold=True))

    # Поведінка при дублікатах (петлі)
    # Дублікат коли IN_PROGRESS
    f.append(line(600, 120, 600, 80, color=NEG, sw=1.8))
    f.append(line(600, 80, 700, 80, color=NEG, sw=1.8))
    f.append(line(700, 80, 700, 115, color=NEG, sw=1.8))
    f.append(arrow(700, 115, 700, 118, color=NEG, sw=1.8))
    f.append(text(650, 70, "Конкурентний дубль → 409 Conflict / очікування лізи", size=11.5, color=NEG, bold=True))

    # Дублікат коли COMMITTED (повернення кешу)
    f.append(line(1020, 120, 1020, 75, color=FIELD, sw=1.8))
    f.append(line(1020, 75, 1120, 75, color=FIELD, sw=1.8))
    f.append(line(1120, 75, 1120, 115, color=FIELD, sw=1.8))
    f.append(arrow(1120, 115, 1120, 118, color=FIELD, sw=1.8))
    f.append(text(1070, 65, "Повтор → повернення збереженого результату", size=11.5, color=FIELD, bold=True))

    # Очищення по TTL
    f.append(line(1020, 210, 1020, 520, color=MUTED, sw=1.6, dash="5,4"))
    f.append(line(1020, 520, 160, 520, color=MUTED, sw=1.6, dash="5,4"))
    f.append(arrow(160, 520, 160, 215, color=MUTED, sw=1.6))
    f.append(text(590, 538, "Витіснення застарілого запису після завершення вікна збереження (TTL)", size=12, color=MUTED, bold=True))

    f.append(fitbox(40, 580, 1120, 75,
                    "три правила надійного автомата:\n"
                    "1. Резервування ключа — строго атомарне через унікальне обмеження;\n"
                    "2. Паралельний дубль не виконує логіку двічі, а чекає чи повертає блокування;\n"
                    "3. Повтор після успіху повертає збережений результат без повторного виклику бізнес-шару",
                    size=12.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'idempotency-state-machine.svg'), W, H, *f)


# ── 4. Пастка подвійного запису ─────────────────────────────────────────────
def dual_write_atomicity_hazard():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "ПАСТКА ПОДВІЙНОГО ЗАПИСУ: чому дія та збереження ключа мають бути атомарними",
                    size=14, bold=True, fill=COOL))

    hw = 510.0
    hh = 450.0
    y0 = 85.0

    # Ліва половина: Роздільні системи (Помилка)
    xL = 50.0
    f.append(fitbox(xL, y0, hw, 56, "РОЗДІЛЬНІ СИСТЕМИ (ПОМИЛКА)\nключ у Redis, гроші в PostgreSQL", size=13, bold=True, fill=WARM, stroke=POS, sw=2))

    # Крок 1 і збій
    f.append(fitbox(xL + 25, y0 + 75, 460, 65, "1. Списати 1000 грн в БД (успіх)\nUPDATE accounts SET balance = balance - 1000", size=12, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(arrow(xL + 255, y0 + 140, xL + 255, y0 + 175, color=POS, sw=2.2))

    # Мить краху
    f.append(fitbox(xL + 25, y0 + 175, 460, 60, "КРАХ ВУЗЛА / ОБРИВ МЕРЕЖІ ДО REDIS\nключ ідемпотентності НЕ збережено!", size=12.5, bold=True, fill=WARM, stroke=POS, sw=2.2))
    f.append(arrow(xL + 255, y0 + 235, xL + 255, y0 + 270, color=POS, sw=2.2))

    f.append(fitbox(xL + 25, y0 + 270, 460, 65, "2. Клієнт бачить таймаут і шле повтор\nРеєстр порожній → подвійне списання!", size=12, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(xL + 25, y0 + 355, 460, 65, "Наслідок: неможливо гарантувати узгодженість\nміж двома незалежними сховищами без 2PC", size=12, fill=FILL, stroke=POS, sw=1.2))

    # Права половина: Єдина транзакція (Правильно)
    xR = xL + hw + 60
    f.append(fitbox(xR, y0, hw, 56, "ЄДИНА ТРАНЗАКЦІЯ (ПРАВИЛЬНО)\nбізнес-мутація + ключ в одній БД", size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(xR + 25, y0 + 75, 460, 155,
                    "BEGIN TRANSACTION;\n\n"
                    "  INSERT INTO idempotency_keys (key, hash, status)\n"
                    "  VALUES ('key-42', 'h_abc', 'COMMITTED');\n\n"
                    "  UPDATE accounts SET balance = balance - 1000;\n\n"
                    "COMMIT;", size=12, fill="#ffffff", stroke=FIELD, sw=1.8))

    f.append(arrow(xR + 255, y0 + 230, xR + 255, y0 + 270, color=FIELD, sw=2.2))

    f.append(fitbox(xR + 25, y0 + 270, 460, 65, "При збої: відкочується І списання, І ключ\nПри успіху: зафіксовано І списання, І ключ", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))

    f.append(fitbox(xR + 25, y0 + 355, 460, 65, "Результат: або операції немає взагалі,\nабо вона виконана рівно один раз і захищена", size=12, fill=FILL, stroke=FIELD, sw=1.2))

    f.append(fitbox(40, 550, 1100, 52,
                    "золоте правило ідемпотентності: збереження токена й зміна стану мусять бути неподільними;\n"
                    "якщо сховища різні — використовують патерн Transactional Outbox або двофазний консенсус",
                    size=13, bold=True, fill=FILL))

    render(os.path.join(OUT, 'dual-write-atomicity-hazard.svg'), W, H, *f)


# ── 5. Вікно збереження ключів проти горизонту повторів ──────────────────────
def ttl_retention_window():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "ГОРИЗОНТ ЗБЕРЕЖЕННЯ КЛЮЧІВ: співвідношення TTL та клієнтських повторів",
                    size=14, bold=True, fill=COOL))

    x0, x1 = 120.0, 1060.0
    span = x1 - x0

    # Часова вісь
    yAxis = 150.0
    f.append(line(x0, yAxis, x1, yAxis, color=INK, sw=2))
    f.append(arrow(x1 - 10, yAxis, x1, yAxis, color=INK, sw=2))
    f.append(text(x1, yAxis - 18, "Час →", size=13, color=MUTED, anchor="end"))

    # Початковий запит T0
    t0 = x0 + 40
    f.append(line(t0, yAxis - 10, t0, yAxis + 10, color=FIELD, sw=2.4))
    f.append(text(t0, yAxis - 20, "T₀ (Перший запит)", size=12.5, color=FIELD, bold=True))

    # Максимальний горизонт повторів клієнта T_retry_max
    t_retry = t0 + span * 0.42
    f.append(line(t_retry, yAxis - 10, t_retry, yAxis + 10, color=NEG, sw=2.4))
    f.append(text(t_retry, yAxis - 20, "T_retry (Крайній повтор клієнта)", size=12, color=NEG, bold=True))

    # TTL ідемпотентності T_ttl
    t_ttl = t0 + span * 0.72
    f.append(line(t_ttl, yAxis - 10, t_ttl, yAxis + 10, color=POS, sw=2.4))
    f.append(text(t_ttl, yAxis - 20, "T_ttl (Спливання TTL ключа)", size=12, color=POS, bold=True))

    # Смуга безпечного вікна (до T_ttl)
    f.append(rect(t0, yAxis + 25, t_ttl - t0, 36, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text((t0 + t_ttl) / 2, yAxis + 48, "БЕЗПЕЧНА ЗОНА: ключ у пам'яті → повтори безпечні й ідемпотентні", size=12, color=FIELD, bold=True))

    # Смуга небезпечної зони (після T_ttl)
    f.append(rect(t_ttl, yAxis + 25, x1 - t_ttl - 30, 36, fill=WARM, stroke=POS, sw=1.8))
    f.append(text((t_ttl + x1 - 30) / 2, yAxis + 48, "НЕБЕЗПЕЧНА ЗОНА (ключ видалено)", size=12, color=POS, bold=True))

    # Сценарій А: легітимний повтор
    f.append(fitbox(x0 + 40, 245, 420, 110,
                    "СЦЕНАРІЙ А: повтор у межах вікна\n\n"
                    "• Запит приходить до T_ttl\n"
                    "• Ключ знайдено в реєстрі\n"
                    "• Віддається збережена відповідь (Успіх)",
                    size=12, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(arrow(t0 + span * 0.25, yAxis + 61, t0 + span * 0.25, 240, color=FIELD, sw=1.8))

    # Сценарій Б: зомбі-повтор після TTL
    f.append(fitbox(t_ttl - 30, 245, 440, 110,
                    "СЦЕНАРІЙ Б: запізнілий «зомбі-повтор»\n\n"
                    "• Повтор затримався в черзі й прийшов після T_ttl\n"
                    "• Сервер не знає про попереднє виконання\n"
                    "• Дія виконується вдруге (Помилка!)",
                    size=12, fill=WARM, stroke=POS, sw=1.8))
    f.append(arrow(t_ttl + span * 0.12, yAxis + 61, t_ttl + span * 0.12, 240, color=POS, sw=1.8))

    # Формула надійності
    f.append(fitbox(120, 385, 940, 100,
                    "МАТЕМАТИЧНЕ ПРАВИЛО РОЗРАХУНКУ TTL:\n\n"
                    "TTL_idempotency  >  Max_Client_Backoff  +  Max_Network_Delay  +  Clock_Skew\n\n"
                    "Якщо клієнт робить експоненційні повтори до 24 годин — TTL має бути не менше 48–72 годин",
                    size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))

    f.append(fitbox(40, 545, 1100, 52,
                    "пам'ять скінченна, але занадто малий TTL перетворює легітимні повтори на аварії;\n"
                    "горизонт збереження ключів завжди проєктують із запасом відносно максимального бюджету повторів",
                    size=13, bold=True, fill=FILL))

    render(os.path.join(OUT, 'ttl-retention-window.svg'), W, H, *f)


two_generals_retry_ambiguity()
natural_vs_synthesized()
idempotency_state_machine()
dual_write_atomicity_hazard()
ttl_retention_window()

print("Фігури успішно згенеровано у:", OUT)
