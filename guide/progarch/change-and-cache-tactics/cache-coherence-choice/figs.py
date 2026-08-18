# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_staleness_window_dual_write():
    """Анатомія вікна несвіжості та розсинхронізація при подвійному записі."""
    W, H = 1040, 440
    f = []

    # Заголовок
    f.append(fitbox(320, 20, 400, 36, "Проблема подвійного запису та зомбі-кеш",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Ліва панель: Подвійний запис (збій)
    f.append(fitbox(30, 70, 470, 340, "", fill=BG, stroke=NEG, sw=1.5, dash="6 4"))
    f.append(fitbox(50, 85, 430, 32, "Сценарій збою при прямому подвійному записі",
                    size=14, bold=True, fill=RED_T, color=NEG, stroke=NEG))

    f.append(fitbox(50, 140, 110, 80, "Клієнт /\nСервіс А", size=13, fill=NEUT, stroke=INK))
    f.append(fitbox(240, 130, 110, 50, "Первинна БД\n(DB v2)", size=13, fill=GREEN_T, stroke=POS))
    f.append(fitbox(360, 185, 110, 50, "Розподілений\nКеш (v1)", size=13, fill=RED_T, stroke=NEG))

    f.append(arrow(160, 155, 240, 155, color=POS, sw=2))
    f.append(text(200, 145, "1. Commit OK", size=10, color=POS, anchor="middle"))

    # Маршрут виклику 2 понад БД чи навпрошки до кешу від 160,195 до 360,210
    f.append(arrow(160, 195, 360, 210, color=NEG, sw=2))
    f.append(text(250, 220, "2. Cache.delete() ❌ Збій мережі / crash", size=11, color=NEG, anchor="middle"))

    f.append(fitbox(60, 230, 410, 80,
                    "⚠️ РЕЗУЛЬТАТ: ЗОМБІ-КЕШ\nБаза даних має v2, а кеш назавжди застряг на v1!\nВікно несвіжості W нескінченне (до закінчення TTL).",
                    size=12, fill=RED_T, stroke=NEG))

    f.append(fitbox(60, 325, 410, 65,
                    "Причина: Запис у БД та видалення з кешу в прикладному коді\nНЕ є атомарною транзакцією (немає 2PC між DB та Redis).",
                    size=11, fill=BG, color=MUTED, stroke="#d0d7de"))

    # Правий панель: Зчитування застарілого кешу
    f.append(fitbox(540, 70, 470, 340, "", fill=BG, stroke=AMBER, sw=1.5))
    f.append(fitbox(560, 85, 430, 32, "Вплив на сервіси-споживачі (Staleness Window)",
                    size=14, bold=True, fill=AMBER_T, color=AMBER, stroke=AMBER))

    f.append(fitbox(560, 135, 110, 60, "Сервіс Б\n(Читач)", size=13, fill=NEUT, stroke=INK))
    f.append(fitbox(730, 135, 110, 60, "Розподілений\nКеш", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(880, 135, 110, 60, "Первинна БД\n(Джерела)", size=13, fill=GREEN_T, stroke=POS))

    f.append(arrow(670, 150, 730, 150, color=INK, sw=2))
    f.append(text(700, 140, "1. Get(key)", size=11, anchor="middle"))

    f.append(arrow(730, 175, 670, 175, color=AMBER, sw=2))
    f.append(text(700, 190, "2. Hit: stale v1!", size=11, color=AMBER, anchor="middle"))

    # Заблокований/обхідний зв'язок до БД (знизу)
    f.append(line(615, 195, 615, 215, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(615, 215, 935, 215, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(935, 215, 935, 195, color=MUTED, sw=1.5, dash="4 4"))
    f.append(text(775, 210, "3. Запит до БД оминуто (Cache Hit)", size=10, color=MUTED, anchor="middle"))

    f.append(fitbox(570, 230, 420, 80,
                    "⚡ ВІКНО НЕСВІЖОСТІ W = T_read - T_write\nСервіс Б виконує бізнес-логіку на застарілому стані v1,\nігноруючи актуальні дані v2 у первинній БД.",
                    size=12, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(570, 325, 420, 65,
                    "Критичний ризик: Акредитиви, ціни, права доступу та адреси\nобробляються з помилками через запізнення когерентності.",
                    size=11, fill=BG, color=MUTED, stroke="#d0d7de"))

    render(os.path.join(OUT, 'staleness-window-dual-write.svg'), W, H, *f,
           title="Проблема подвійного запису та вікно несвіжості кешу")


def fig_cache_aside_race():
    """Паралельна гонка читача й записувача у Cache-Aside та її вирішення."""
    W, H = 1040, 420
    f = []

    # Ліва панель: Гонка (Race Condition)
    f.append(fitbox(30, 35, 470, 360, "", fill=BG, stroke=NEG, sw=1.5, dash="6 4"))
    f.append(fitbox(50, 50, 430, 32, "Гонка у Cache-Aside (Оновлення кешу)",
                    size=14, bold=True, fill=RED_T, color=NEG, stroke=NEG))

    f.append(fitbox(60, 100, 110, 45, "1. Читач", size=12, fill=NEUT, stroke=INK))
    f.append(text(180, 120, "Cache Miss → Читає БД (v1)", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(60, 155, 110, 45, "2. Записувач", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(text(180, 175, "Оновлює БД (v2) & Set Cache(v2)", size=11, color=AMBER, anchor="start"))

    f.append(fitbox(60, 210, 110, 45, "3. Читач (пізно)", size=12, fill=RED_T, stroke=NEG))
    f.append(text(180, 230, "Записує старе Set Cache(v1) поверх v2!", size=11, color=NEG, anchor="start", bold=True))

    f.append(fitbox(60, 275, 410, 100,
                    "❌ ЗОМБІ-ЗАПИС У КЕШ\nЧитач запізнився із записом до кешу й перетер свіжі дані v2\nстарою версією v1, зчитаною до оновлення бази.",
                    size=12, fill=RED_T, stroke=NEG))

    # Правий панель: Вирішення через видалення ключів
    f.append(fitbox(540, 35, 470, 360, "", fill=BG, stroke=POS, sw=1.5))
    f.append(fitbox(560, 50, 430, 32, "Рішення: Інвалідація через видалення (Eviction)",
                    size=14, bold=True, fill=GREEN_T, color=POS, stroke=POS))

    f.append(fitbox(570, 100, 110, 45, "1. Читач", size=12, fill=NEUT, stroke=INK))
    f.append(text(690, 120, "Cache Miss → Читає БД (v1)", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(570, 155, 110, 45, "2. Записувач", size=12, fill=GREEN_T, stroke=POS))
    f.append(text(690, 175, "Оновлює БД (v2) & Delete Cache(key)", size=11, color=POS, anchor="start", bold=True))

    f.append(fitbox(570, 210, 110, 45, "3. Читач", size=12, fill=BLUE_T, stroke=INK))
    f.append(text(690, 230, "Запис v1 марний / перевірка версії", size=11, color=INK, anchor="start"))

    f.append(fitbox(570, 275, 420, 100,
                    "✅ ЗАХИСТ ВІД ГОНОК\nЗаписувач вилучає (Evict) ключ замість перевизначення.\nНаступний читач гарантовано вибиває Cache Miss та зчитує v2.",
                    size=12, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'cache-aside-race.svg'), W, H, *f,
           title="Гонка у Cache-Aside та інвалідація через видалення ключів")


def fig_cdc_outbox_coherence_pipeline():
    """Конвеєр інвалідації на основі Change Data Capture (CDC) та Outbox."""
    W, H = 1040, 400
    f = []

    # Заголовок
    f.append(fitbox(320, 20, 400, 36, "Подійно-орієнтована когерентність та CDC",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Джерело: Сервіс-власник та База
    f.append(fitbox(40, 80, 140, 70, "Сервіс-Власник\n(Write Path)", size=13, fill=NEUT, stroke=INK))
    f.append(fitbox(40, 200, 140, 70, "Первинна БД\n(PostgreSQL / MySQL)", size=13, fill=GREEN_T, stroke=POS))

    f.append(arrow(110, 150, 110, 200, color=POS, sw=2))
    f.append(text(115, 180, "1. ACID Commit", size=11, color=POS, anchor="start"))

    # CDC / Log Miner шар
    f.append(fitbox(250, 200, 150, 70, "Журнал WAL /\nBinlog", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(470, 200, 150, 70, "CDC Engine\n(Debezium)", size=13, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(180, 235, 250, 235, color=POS, sw=2))
    f.append(arrow(400, 235, 470, 235, color=AMBER, sw=2))
    f.append(text(435, 220, "2. Read WAL", size=11, color=AMBER, anchor="middle"))

    # Брокер подій
    f.append(fitbox(690, 140, 120, 130, "Шина Подій\n(Apache Kafka /\nRabbitMQ)", size=13, fill=BLUE_T, stroke=INK))

    f.append(arrow(620, 235, 690, 235, color=AMBER, sw=2))
    f.append(text(655, 220, "3. Publish Event", size=11, color=INK, anchor="middle"))

    # Споживачі та Кеші
    f.append(fitbox(870, 80, 130, 65, "Сервіс Б\n(Споживач)", size=13, fill=NEUT, stroke=INK))
    f.append(fitbox(870, 240, 130, 65, "Локальний / L2\nКеш Б", size=13, fill=GREEN_T, stroke=POS))

    f.append(arrow(810, 170, 870, 115, color=INK, sw=2))
    f.append(text(835, 135, "4. Event", size=11, anchor="middle"))

    f.append(arrow(935, 145, 935, 240, color=POS, sw=2))
    f.append(text(940, 195, "5. Evict / Invalidate", size=11, color=POS, anchor="start", bold=True))

    # Нижній опис
    f.append(fitbox(40, 310, 960, 70,
                    "✨ ПЕРЕВАГИ CDC (CHANGE DATA CAPTURE):\n• Атомарність гарантована БД: запис у WAL неможливо оминути чи зламати аварією сервісу.\n• Нульове часове зчеплення: сервіс-власник не знає про існування кешів споживачів.\n• Повна усуненість проблеми подвійного запису в прикладному коді.",
                    size=12, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'cdc-outbox-coherence-pipeline.svg'), W, H, *f,
           title="Конвеєр інвалідації кешу через Change Data Capture (CDC)")


def fig_coherence_decision_tree():
    """Дерево прийняття рішень вибору стратегії свіжості даних між сервісами."""
    W, H = 1040, 430
    f = []

    # Заголовок
    f.append(fitbox(320, 15, 400, 36, "Дерево прийняття рішень: Стратегія когерентності",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Питання 1
    f.append(fitbox(40, 70, 260, 55, "1. Чи припустима несвіжість\nданих > 0 мс (Staleness Tolerance)?",
                    size=12, bold=True, fill=BLUE_T, stroke=INK))

    # Гілка НІ -> Прямий виклик / Без кешу
    f.append(arrow(170, 125, 110, 180, color=NEG, sw=2))
    f.append(text(125, 150, "НІ (0 мс)", size=11, color=NEG, anchor="end", bold=True))
    f.append(fitbox(30, 180, 160, 75, "БЕЗ КЕШУВАНИХ КОПІЙ\n• Прямий gRPC/REST\n• Дджерело правди\n• Строга консистентність",
                    size=11, fill=RED_T, stroke=NEG))

    # Гілка ТАК -> Питання 2
    f.append(arrow(170, 125, 400, 180, color=POS, sw=2))
    f.append(text(290, 150, "ТАК (W > 0)", size=11, color=POS, anchor="start", bold=True))

    # Питання 2
    f.append(fitbox(280, 180, 240, 55, "2. Яка частота змін даних\nі вимоги до латентності?",
                    size=12, bold=True, fill=BLUE_T, stroke=INK))

    # Гілка 2a: Висока частота / Рідкісні зміни -> TTL / Refresh Ahead
    f.append(arrow(330, 235, 230, 290, color=INK, sw=2))
    f.append(text(260, 260, "Рідкісні зміни / High Read", size=11, anchor="end"))
    f.append(fitbox(150, 290, 170, 80, "TTL / Refresh-Ahead\n• Пасивна інвалідація\n• М'який TTL (Stale-While)\n• Захист від Stampede",
                    size=11, fill=AMBER_T, stroke=AMBER))

    # Гілка 2b: Критичні події змін -> Питання 3
    f.append(arrow(430, 235, 590, 290, color=INK, sw=2))
    f.append(text(520, 260, "Критична інвалідація", size=11, anchor="start"))

    # Питання 3
    f.append(fitbox(500, 290, 220, 55, "3. Чи є можливість інфраструктури\nдля CDC / Transactional Outbox?",
                    size=12, bold=True, fill=BLUE_T, stroke=INK))

    # Гілка 3a: НІ -> Cache-Aside + Eviction
    f.append(arrow(550, 345, 440, 375, color=AMBER, sw=2))
    f.append(text(480, 365, "НІ", size=11, color=AMBER, anchor="end", bold=True))
    f.append(fitbox(340, 370, 180, 50, "Cache-Aside + Evict\n• Видалення ключів\n• Твердий TTL захист",
                    size=11, fill=AMBER_T, stroke=AMBER))

    # Гілка 3b: ТАК -> CDC (Debezium) / Outbox
    f.append(arrow(670, 345, 780, 375, color=POS, sw=2))
    f.append(text(730, 365, "ТАК", size=11, color=POS, anchor="start", bold=True))
    f.append(fitbox(700, 370, 210, 50, "CDC (Debezium) / Outbox\n• Нуль подвійного запису\n• Подійна інвалідація",
                    size=11, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'coherence-decision-tree.svg'), W, H, *f,
           title="Дерево прийняття рішень для вибору стратегії свіжості даних")


if __name__ == '__main__':
    fig_staleness_window_dual_write()
    fig_cache_aside_race()
    fig_cdc_outbox_coherence_pipeline()
    fig_coherence_decision_tree()
    print("Figures generated successfully in img/")
