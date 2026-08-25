# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Durable workflows на масштабі».
Використовує спільну бібліотеку svgkit з каталогу scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_history_explosion_and_continue_as_new():
    """Порівняння неконтрольованого зростання історії подій та Continue-As-New."""
    w, h = 920, 460
    frags = []

    # Ліва колонка: Проблема — вибух історії
    frags.append(fitbox(20, 15, 425, 430, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(232, 42, "Вибух історії подій (Unbounded History)", size=13, color=POS, bold=True))

    frags.append(textbox(232, 85, "Тривалий цикл / Сутність без відсікання\n(10 000+ подій у межах одного запуску)", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=300)[0])

    frags.append(arrow(232, 115, 232, 145, color=POS, sw=1.5))

    frags.append(textbox(232, 185, "Квадратична вартість Replay O(N²):\nНа кожну подію воркер вичитує всі минулі кроки,\nперепарсує мегабайти JSON та проганяє CPU-цикл", size=10.5, pad=8, fill="#fdecea", stroke=POS, min_w=300)[0])

    frags.append(arrow(232, 230, 232, 260, color=POS, sw=1.5))

    frags.append(fitbox(35, 270, 395, 160,
                         "Руйнівні наслідки для кластера:\n"
                         "• Гігабайти пам'яті воркерів під кеш історії -> OOM\n"
                         "• Затримка обробки сигналу зростає з 2 мс до секунд\n"
                         "• Трафік між сховищем та воркерами забиває мережу\n"
                         "• Ризик перевищення ліміту розміру одного запису БД",
                         size=10.5, pad=8, fill="#ffffff", stroke="#e0b4b0", sw=1.2, color=INK))

    # Права колонка: Рішення — Continue-As-New
    frags.append(fitbox(475, 15, 425, 430, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(687, 42, "Атомарне відсікання: Continue-As-New", size=13, color=FIELD, bold=True))

    frags.append(textbox(687, 85, "Запуск 1 (Ітерація 1..N)\nНакопичення компактного знімка стану", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=300)[0])

    frags.append(arrow(687, 115, 687, 145, color=FIELD, sw=1.5))

    frags.append(textbox(687, 185, "Атомарний перехід Continue-As-New:\nЗавершення поточного запуску + старт нового\nз чистим журналом подій та збереженим станом", size=10.5, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=300)[0])

    frags.append(arrow(687, 230, 687, 260, color=FIELD, sw=1.5))

    frags.append(fitbox(490, 270, 395, 160,
                         "Переваги на масштабі:\n"
                         "• Лінійна вартість обчислень O(N) та стабільна пам'ять\n"
                         "• Час відтворення лишається фіксованим (< 5 мс)\n"
                         "• Збереження єдиного WorkflowID для зовнішніх систем\n"
                         "• Архівування старого журналу в дешеве сховище",
                         size=10.5, pad=8, fill="#ffffff", stroke="#a3d9b8", sw=1.2, color=INK))

    render(os.path.join(OUT_DIR, "history-explosion-and-continue-as-new.svg"), w, h, *frags)


def fig_sharded_history_architecture():
    """Архітектура шардування історії за WorkflowID."""
    w, h = 940, 500
    frags = []

    # Рівень 1: Вхідний шлюз
    frags.append(fitbox(20, 15, 900, 65, "", fill="#f9fafb", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 35, "Frontend API Gateway / Ingress Service", size=13, color=INK, bold=True))
    frags.append(text(470, 60, "Прийом викликів: StartWorkflow, Signal, Query, Cancel (без збереження стану)", size=11, color=MUTED))

    # Стрілка вниз до блоку маршрутизації
    frags.append(arrow(470, 80, 470, 95, color=LINE, sw=1.5))
    frags.append(textbox(470, 115, "Стабільне хешування: ShardID = Hash(WorkflowID) % TotalShards", size=10.5, pad=6, fill="#ffffff", stroke=LINE, min_w=440)[0])
    frags.append(arrow(470, 135, 470, 150, color=LINE, sw=1.5))

    # Рівень 2: Шардований сервіс історії
    frags.append(fitbox(20, 150, 900, 205, "", fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 172, "Шардовані вузли історії (History Service: 4096 логічних шардів)", size=12.5, color=INK, bold=True))

    # Шард 1
    frags.append(fitbox(35, 185, 270, 155,
                         "Логічний Шард #42\n"
                         "• LRU-кеш детермінованого стану\n"
                         "• Локальний м'ютекс на WorkflowID\n"
                         "• Ієрархічне колесо таймерів\n"
                         "• Оптимістичний контроль версій",
                         size=10.5, pad=8, fill="#f4faf6", stroke="#a3d9b8", sw=1.2, color=INK))

    # Шард 2
    frags.append(fitbox(335, 185, 270, 155,
                         "Логічний Шард #108\n"
                         "• LRU-кеш детермінованого стану\n"
                         "• Локальний м'ютекс на WorkflowID\n"
                         "• Ієрархічне колесо таймерів\n"
                         "• Оптимістичний контроль версій",
                         size=10.5, pad=8, fill="#f4faf6", stroke="#a3d9b8", sw=1.2, color=INK))

    # Шард N
    frags.append(fitbox(635, 185, 270, 155,
                         "Логічний Шард #4095\n"
                         "• LRU-кеш детермінованого стану\n"
                         "• Локальний м'ютекс на WorkflowID\n"
                         "• Ієрархічне колесо таймерів\n"
                         "• Оптимістичний контроль версій",
                         size=10.5, pad=8, fill="#f4faf6", stroke="#a3d9b8", sw=1.2, color=INK))

    # Стрілки вниз до сховища
    frags.append(arrow(170, 355, 170, 385, color=LINE, sw=1.5))
    frags.append(arrow(470, 355, 470, 385, color=LINE, sw=1.5))
    frags.append(arrow(770, 355, 770, 385, color=LINE, sw=1.5))

    # Рівень 3: Сховище даних
    frags.append(fitbox(20, 385, 900, 95, "", fill="#f9fafb", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 408, "Розподілений шар зберігання та черг", size=12.5, color=INK, bold=True))
    frags.append(textbox(240, 445, "Транзакційне сховище журналу\n(Cassandra / CockroachDB / PostgreSQL)", size=10, pad=5, fill="#ffffff", stroke=LINE, min_w=340)[0])
    frags.append(textbox(700, 445, "Сервіс черг задач (Matching Service)\nДиспетчеризація завдань на пули воркерів", size=10, pad=5, fill="#ffffff", stroke=LINE, min_w=340)[0])

    render(os.path.join(OUT_DIR, "sharded-history-architecture.svg"), w, h, *frags)


def fig_hierarchical_timer_wheel():
    """Ієрархічне колесо таймерів (Timer Wheel) шарду."""
    w, h = 920, 450
    frags = []

    # Верхній заголовок порівняння
    frags.append(fitbox(20, 15, 425, 100, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(232, 40, "Наївний глобальний Poller (Антипатерн)", size=12, color=POS, bold=True))
    frags.append(fitbox(35, 55, 395, 50,
                         "SELECT * FROM timers WHERE fire_time <= NOW() LIMIT 1000\n"
                         "Блокування таблиць, сплески I/O та відставання черги",
                         size=10, pad=5, fill="#ffffff", stroke="#e0b4b0", sw=1, color=INK))

    frags.append(fitbox(475, 15, 425, 100, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(687, 40, "Ієрархічне квантування таймерів (Timer Wheel)", size=12, color=FIELD, bold=True))
    frags.append(fitbox(490, 55, 395, 50,
                         "Квантування часу за бакетами (секунди -> хвилини -> дні)\n"
                         "O(1) перевірка готових таймерів без сканування бази даних",
                         size=10, pad=5, fill="#ffffff", stroke="#a3d9b8", sw=1, color=INK))

    # Нижній блок: Структура Timer Wheel
    frags.append(fitbox(20, 130, 880, 305, "", fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(460, 155, "Структура ієрархічних часових бакетів усередині логічного шарду", size=12.5, color=INK, bold=True))

    # Рівень 1: Секундний бакет (Активний)
    frags.append(fitbox(35, 175, 260, 150,
                         "Рівень 1: Секундні слоти [0..59]\n"
                         "• Поточний активний секундний бакет\n"
                         "• Таймери спрацьовують негайно\n"
                         "• Завдання миттєво відправляються\n"
                         "  у Task Queue воркерам",
                         size=10.5, pad=8, fill="#e8f8f0", stroke=FIELD, sw=1.5, color=INK))

    # Рівень 2: Хвилинний бакет
    frags.append(fitbox(330, 175, 260, 150,
                         "Рівень 2: Хвилинні бакети [0..59]\n"
                         "• Таймери на найближчу годину\n"
                         "• На межі кожної хвилини таймери\n"
                         "  пересипаються (каскадуються)\n"
                         "  у секундне колесо",
                         size=10.5, pad=8, fill="#f9fafb", stroke=LINE, sw=1.2, color=INK))

    # Рівень 3: Денний / Довгостроковий бакет
    frags.append(fitbox(625, 175, 260, 150,
                         "Рівень 3: Довготривалі бакети (Дні)\n"
                         "• Таймери на дні, місяці та роки\n"
                         "• Зберігаються у партиціях БД,\n"
                         "  відсортованих за часом;\n"
                         "  підвантажуються порціями",
                         size=10.5, pad=8, fill="#f9fafb", stroke=LINE, sw=1.2, color=INK))

    # Стрілки каскадування
    frags.append(arrow(625, 250, 590, 250, color=LINE, sw=1.5))
    frags.append(arrow(330, 250, 295, 250, color=FIELD, sw=1.5))

    # Підсумковий блок унизу
    frags.append(fitbox(35, 340, 850, 80,
                         "Механізм переміщення (Cascade): Шард просуває внутрішній годинник без блокування таблиць.\n"
                         "Коли хвилина минає, елементи з хвилинного бакета розкладаються у відповідні секунди.\n"
                         "База даних зчитується лише блоками великих діапазонів, мінімізуючи навантаження на сховище.",
                         size=10.5, pad=6, fill="#f4f6f8", stroke=LINE, sw=1, color=INK))

    render(os.path.join(OUT_DIR, "hierarchical-timer-wheel.svg"), w, h, *frags)


def fig_hot_partition_signal_fanout():
    """Подолання гарячих точок (Hot Shards): буферизація та Tree Fan-Out."""
    w, h = 920, 460
    frags = []

    # Ліва колонка: Проблема — прямий штурм єдиного процесу
    frags.append(fitbox(20, 15, 425, 430, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(232, 42, "Конкурентний колапс (Single Entity Bottleneck)", size=12.5, color=POS, bold=True))

    frags.append(textbox(232, 85, "10 000 сигналів/сек на один WorkflowID\n(наприклад, глобальний лічильник або флеш-розпродаж)", size=10.5, pad=7, fill="#ffffff", stroke=LINE, min_w=310)[0])

    frags.append(arrow(232, 115, 232, 145, color=POS, sw=1.5))

    frags.append(textbox(232, 185, "Постійні конфлікти CAS (Optimistic Locking):\nКожен сигнал вимагає блокування шарду,\nповторного зчитування історії та оновлення версії", size=10, pad=7, fill="#fdecea", stroke=POS, min_w=310)[0])

    frags.append(arrow(232, 225, 232, 255, color=POS, sw=1.5))

    frags.append(fitbox(35, 265, 395, 165,
                         "Результат:\n"
                         "• 99% запитів зазнають відмови за таймаутом блокування\n"
                         "• Шард перевантажується ретраями та блокує сусідні процеси\n"
                         "• Падіння загальної пропускної здатності кластера",
                         size=10.5, pad=8, fill="#ffffff", stroke="#e0b4b0", sw=1.2, color=INK))

    # Права колонка: Рішення — Деревовидна агрегація (Tree Fan-Out)
    frags.append(fitbox(475, 15, 425, 430, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(687, 42, "Масштабоване рішення: Tree Fan-Out і батчинг", size=12.5, color=FIELD, bold=True))

    frags.append(textbox(687, 85, "Вхідний потік сигналів розподіляється\nза хешем ключа (User / Partition ID)", size=10.5, pad=7, fill="#ffffff", stroke=LINE, min_w=310)[0])

    frags.append(arrow(687, 115, 687, 145, color=FIELD, sw=1.5))

    frags.append(fitbox(490, 145, 395, 120,
                         "Каскад дочірніх процесів (Child Workflows):\n"
                         "• Листкові воркфлоу приймають сигнали локально\n"
                         "• Агрегують по 100–500 подій у пам'яті\n"
                         "• Передають зведені батчі батьківському процесу",
                         size=10.5, pad=8, fill="#ffffff", stroke="#a3d9b8", sw=1.2, color=INK))

    frags.append(arrow(687, 265, 687, 290, color=FIELD, sw=1.5))

    frags.append(fitbox(490, 290, 395, 140,
                         "Кореневий процес (Root Aggregator):\n"
                         "• Отримує періодичні батчі замість мільйонів сигналів\n"
                         "• Навантаження на один процес знижується в 100–1000 разів\n"
                         "• Ізоляція збоїв та нульові блокування сховища",
                         size=10.5, pad=8, fill="#ffffff", stroke="#a3d9b8", sw=1.2, color=INK))

    render(os.path.join(OUT_DIR, "hot-partition-signal-fanout.svg"), w, h, *frags)


def main():
    fig_history_explosion_and_continue_as_new()
    fig_sharded_history_architecture()
    fig_hierarchical_timer_wheel()
    fig_hot_partition_signal_fanout()
    print("Усі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
