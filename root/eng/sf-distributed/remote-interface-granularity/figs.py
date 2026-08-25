# -*- coding: utf-8 -*-
"""Фігури до теми «Дробність віддаленого інтерфейсу». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT, exist_ok=True)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"


# ── 1. chatty-vs-chunky-timeline: балакучий проти пакетованого ─────────────────
def fig_chatty_vs_chunky():
    W, H = 1120, 560
    f = []

    f.append(fitbox(40, 20, 1040, 44,
                    "БАЛАКУЧИЙ (CHATTY) ПРОТИ ПАКЕТОВАНОГО (CHUNKY) ІНТЕРФЕЙСУ НА ШКАЛІ ЧАСУ",
                    size=14, bold=True, fill=BLUE_F))

    # Ліва колонка: Балакучий інтерфейс
    f.append(rect(40, 75, 505, 410, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    f.append(text(292, 102, "Балакучий інтерфейс (5 послідовних RPC)", size=13, bold=True, color=POS))
    f.append(text(292, 122, "Сумарна затримка: 5 × (RTT + системні витрати) ≈ 510 мс", size=11, color=MUTED))

    calls = [
        ("getUserProfile(id)", "RTT: 50 мс", "Пакет 1"),
        ("getUserAddress(id)", "RTT: 50 мс", "Пакет 2"),
        ("getUserOrders(id)", "RTT: 50 мс", "Пакет 3"),
        ("getOrderItems(orderId)", "RTT: 50 мс", "Пакет 4"),
        ("getDiscountLevel(id)", "RTT: 50 мс", "Пакет 5"),
    ]

    for i, (name, rtt, pkt) in enumerate(calls):
        y = 145 + i * 58
        f.append(rect(55, y, 160, 42, fill=BLUE_F, stroke=NEG, sw=1.2))
        f.append(text(135, y + 25, "Клієнт (Потік)", size=11, bold=True))

        f.append(arrow(220, y + 14, 350, y + 14, color=POS, sw=1.3))
        f.append(text(285, y + 10, pkt, size=10, color=POS))

        f.append(arrow(350, y + 30, 220, y + 30, color=FIELD, sw=1.3))
        f.append(text(285, y + 42, rtt, size=9.5, color=MUTED))

        f.append(rect(355, y, 175, 42, fill=RED_F, stroke=POS, sw=1.2))
        f.append(text(442, y + 18, name, size=10.5, bold=True))
        f.append(text(442, y + 33, "обробка: ~1 мс", size=9.5, color=MUTED))

    f.append(fitbox(55, 442, 475, 34, "5 переходів через ядро OS, 5 черг TCP, ризик обриву на кожному кроці", size=10.5, fill=RED_F, stroke=POS, color=POS))

    # Права колонка: Пакетований фасад
    f.append(rect(575, 75, 505, 410, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(827, 102, "Пакетований віддалений фасад (1 Chunky RPC)", size=13, bold=True, color=FIELD))
    f.append(text(827, 122, "Сумарна затримка: 1 × RTT + паралельна обробка ≈ 103 мс", size=11, color=MUTED))

    # Один великий рейс
    f.append(rect(590, 150, 140, 260, fill=BLUE_F, stroke=NEG, sw=1.2))
    f.append(text(660, 260, "Клієнт", size=13, bold=True))
    f.append(text(660, 285, "1 блокування\nна сокеті", size=10.5, color=MUTED))

    f.append(arrow(735, 200, 810, 200, color=FIELD, sw=1.8))
    f.append(text(772, 190, "getDashboard()", size=10, bold=True, color=FIELD))

    f.append(arrow(810, 360, 735, 360, color=FIELD, sw=1.8))
    f.append(text(772, 380, "DashboardDTO (100 мс RTT)", size=10, color=FIELD))

    # Внутрішня серверна область
    f.append(rect(815, 145, 250, 270, fill=GRAY_F, stroke=FIELD, sw=1.4))
    f.append(text(940, 168, "Сервер: Remote Facade", size=12, bold=True, color=FIELD))

    in_mem_items = [
        "In-Memory Profile Fetch (10 мкс)",
        "In-Memory Address Lookup (8 мкс)",
        "In-Memory Orders Query (500 мкс)",
        "In-Memory Items Extraction (20 мкс)",
        "In-Memory Discount Calc (5 мкс)"
    ]
    for i, itm in enumerate(in_mem_items):
        iy = 185 + i * 40
        f.append(rect(825, iy, 230, 32, fill=GREEN_F, stroke=FIELD, sw=1.0))
        f.append(text(940, iy + 20, itm, size=9.8, color=INK))

    f.append(fitbox(590, 442, 475, 34, "1 перехід через мережу; вся композиція виконується в локальній пам'яті", size=10.5, fill=GREEN_F, stroke=FIELD, color=FIELD))

    # Висновок знизу
    f.append(fitbox(40, 498, 1040, 48,
                    "Висновок: об'єднання дрібних запитів у консолідований фасад скорочує накладні витрати на 80%,\n"
                    "ліквідує черги в сокетах і зводить імовірність мережевого збою до одного кругового рейсу.",
                    size=11.5, fill=FILL))

    render(os.path.join(OUT, 'chatty-vs-chunky-timeline.svg'), W, H, *f)


# ── 2. network-overhead-breakdown: анатомія накладних витрат ──────────────────
def fig_network_overhead():
    W, H = 1120, 520
    f = []

    f.append(fitbox(40, 20, 1040, 44,
                    "АНАТОМІЯ НАКЛАДНИХ ВИТРАТ МЕРЕЖЕВОГО ВИКЛИКУ: МІКРОСЕКУНДИ ПРОТИ МІЛІСЕКУНД",
                    size=14, bold=True, fill=WARN_F))

    stages = [
        ("1. Маршалінг у пам'яті", "Серіалізація структури в байти (JSON/Protobuf/FlatBuffers),\nвиділення буферів у heap, перевірка схеми.", "0.01 – 0.5 мс", BLUE_F, NEG),
        ("2. Системний виклик ядра", "Виклик sendmsg(), перемикання User -> Kernel Space,\nкопіювання пам'яті в sk_buff сокета.", "0.005 – 0.02 мс", GRAY_F, LINE),
        ("3. Стек TCP/IP та NIC", "TCP фреймінг, обчислення чексум, черга кільцевого буфера Tx,\nпередача даних контролеру через DMA.", "0.01 – 0.05 мс", GRAY_F, LINE),
        ("4. Фізичний транзит (Канал)", "Швидкість світла у волокні (~200 км/мс), затримки комутаторів,\nбуферизація в чергах маршрутизаторів (RTT).", "1.0 – 150.0 мс\n(98% часу!)", RED_F, POS),
        ("5. Прийом NIC і ядром", "DMA в Rx буфер, переривання ядра, TCP ACK generation,\nпробудження потоку з epoll_wait() / recvmsg().", "0.01 – 0.05 мс", GRAY_F, LINE),
        ("6. Дезеріалізація та логіка", "Парсинг байтів у структуру об'єкта, валідація полів,\nпередача параметрів у функцію бізнес-логіки.", "0.01 – 0.5 мс", GREEN_F, FIELD)
    ]

    for i, (title, desc, cost, fill_c, stroke_c) in enumerate(stages):
        col = i % 3
        row = i // 3
        x = 40 + col * 360
        y = 80 + row * 195

        f.append(rect(x, y, 340, 175, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        f.append(text(x + 170, y + 26, title, size=12, bold=True, color=stroke_c))
        f.append(fitbox(x + 15, y + 42, 310, 68, desc, size=10.2, fill="#ffffff", stroke=MUTED, sw=1.0))
        f.append(rect(x + 15, y + 120, 310, 42, fill=fill_c, stroke=stroke_c, sw=1.2))
        f.append(text(x + 170, y + 145, f"Затримка: {cost}", size=11, bold=True, color=stroke_c))

    # Стрілки між блоками
    f.append(arrow(385, 165, 395, 165, color=LINE, sw=1.5))
    f.append(arrow(745, 165, 755, 165, color=LINE, sw=1.5))
    f.append(arrow(930, 260, 930, 270, color=LINE, sw=1.5))
    f.append(arrow(755, 360, 745, 360, color=LINE, sw=1.5))
    f.append(arrow(395, 360, 385, 360, color=LINE, sw=1.5))

    f.append(fitbox(40, 475, 1040, 35,
                    "Головний висновок: 98% затримки генерує фізичний транзит (етап 4). Дрібні виклики повторюють цей транзит N разів.",
                    size=11, fill=FILL))

    render(os.path.join(OUT, 'network-overhead-breakdown.svg'), W, H, *f)


# ── 3. remote-facade-architecture: архітектура віддаленого фасаду ────────────
def fig_remote_facade_arch():
    W, H = 1120, 480
    f = []

    f.append(fitbox(40, 20, 1040, 44,
                    "АРХІТЕКТУРА ВІДДАЛЕНОГО ФАСАДУ (REMOTE FACADE) ТА DTO",
                    size=14, bold=True, fill=GREEN_F))

    # Зона 1: Клієнтський рівень
    f.append(rect(40, 80, 260, 330, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(170, 110, "Клієнтський процес", size=13, bold=True, color=NEG))
    f.append(fitbox(55, 135, 230, 80, "Клієнтський контролер / UI\n\nФормує 1 запит на потрібний екран:\nDashboardRequestDTO", size=11, fill="#ffffff", stroke=NEG))
    f.append(fitbox(55, 235, 230, 80, "Клієнтський Batching\nAggregator\n\nОб'єднує незалежні виклики потоків у єдиний пакет", size=10.5, fill="#ffffff", stroke=NEG))
    f.append(fitbox(55, 335, 230, 60, "1 мережевий виклик\n(1 сокет, 1 очікування)", size=10.5, fill=GREEN_F, stroke=FIELD, color=FIELD))

    # Зона 2: Мережевий бар'єр
    f.append(rect(330, 80, 210, 330, fill=WARN_F, stroke=POS, sw=1.5, rx=6))
    f.append(text(435, 110, "Мережевий бар'єр", size=13, bold=True, color=POS))
    f.append(text(435, 130, "(LAN / WAN / Internet)", size=10.5, color=MUTED))

    f.append(arrow(275, 190, 355, 190, color=POS, sw=1.6))
    f.append(fitbox(345, 170, 180, 45, "Composite Request DTO\n(gRPC / Protobuf / JSON)", size=9.8, bold=True, fill="#ffffff", stroke=POS))

    f.append(arrow(355, 300, 275, 300, color=FIELD, sw=1.6))
    f.append(fitbox(345, 280, 180, 45, "Consolidated Response DTO\n(Всі дані в 1 пакеті)", size=9.8, bold=True, fill="#ffffff", stroke=FIELD))

    f.append(fitbox(345, 345, 180, 50, "Мінімум пакетів,\nстиснення даних,\nнуль N+1 рейсів", size=10, fill=GRAY_F, stroke=MUTED))

    # Зона 3: Серверний рівень
    f.append(rect(570, 80, 510, 330, fill=GRAY_F, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(825, 108, "Серверний процес (Внутрішній адресний простір)", size=13, bold=True, color=FIELD))

    # Шар фасаду
    f.append(rect(585, 130, 480, 85, fill="#ffffff", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(825, 152, "Шар Remote Facade & DTO Assembler", size=12, bold=True, color=FIELD))
    f.append(fitbox(595, 165, 460, 42, "Приймає Composite Request -> викликає паралельно внутрішні доменні модулі -> збирає Response DTO", size=10.2, fill=GREEN_F, stroke=FIELD))

    # Внутрішні сутності (In-Memory)
    f.append(rect(585, 230, 480, 165, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(825, 252, "Дрібнозернисті доменні сутності (Локальна пам'ять / RAM)", size=11, bold=True, color=INK))

    domain_boxes = [
        ("User Entity", "getProfile()\ngetEmail()", 600, 270),
        ("Order Service", "getRecent()\ngetStatus()", 720, 270),
        ("Inventory", "checkStock()\ngetLocations()", 840, 270),
        ("Pricing / Tax", "calcDiscount()\napplyTax()", 960, 270),
    ]
    for title, methods, bx, by in domain_boxes:
        f.append(rect(bx, by, 100, 110, fill=BLUE_F, stroke=NEG, sw=1.1, rx=4))
        f.append(text(bx + 50, by + 20, title, size=10, bold=True, color=NEG))
        f.append(mtext(bx + 50, by + 50, methods, size=9.5, color=INK, lh=1.3))
        f.append(text(bx + 50, by + 98, "< 10 нс", size=9, bold=True, color=FIELD))

    # Підсумок знизу
    f.append(fitbox(40, 425, 1040, 42,
                    "Фасад ізолює дрібнозернисту доменну модель від мережі. Всі дрібні виклики відбуваються у локальній пам'яті (наносекунди),\n"
                    "а через повільну мережу курсує лише один оптимізований зліпок даних (DTO).",
                    size=11, fill=FILL))

    render(os.path.join(OUT, 'remote-facade-architecture.svg'), W, H, *f)


# ── 4. batch-partial-failure-model: модель часткових збоїв ───────────────────
def fig_batch_partial_failure():
    W, H = 1120, 500
    f = []

    f.append(fitbox(40, 20, 1040, 44,
                    "МОДЕЛЬ ОБРОБКИ ЧАСТКОВИХ ЗБОЇВ У ПАКЕТНИХ ОПЕРАЦІЯХ (MULTI-STATUS DTO)",
                    size=14, bold=True, fill=WARN_F))

    # Запит
    f.append(rect(40, 80, 230, 340, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(155, 108, "Пакетний запит (BatchRequest)", size=11.5, bold=True, color=NEG))
    f.append(fitbox(55, 125, 200, 280,
                    "{\n  \"batchId\": \"b-9912\",\n  \"items\": [\n    {\"id\": 1, \"cmd\": \"Update\"},\n    {\"id\": 2, \"cmd\": \"Update\"},\n    {\"id\": 3, \"cmd\": \"Update\"},\n    {\"id\": 4, \"cmd\": \"Update\"}\n  ]\n}",
                    size=10.5, fill="#ffffff", stroke=NEG))

    f.append(arrow(275, 240, 335, 240, color=LINE, sw=1.8))

    # Обробка на сервері
    f.append(rect(340, 80, 390, 340, fill=GRAY_F, stroke=LINE, sw=1.5, rx=6))
    f.append(text(535, 108, "Виконання на сервері (Ізольовані елементи)", size=12, bold=True))

    items_status = [
        ("Елемент #1: Update User 101", "Успішно збережено в базі", "HTTP 200 OK", GREEN_F, FIELD),
        ("Елемент #2: Update User 102", "Помилка валідації (Bad Email)", "HTTP 422 Unprocessable", WARN_F, POS),
        ("Елемент #3: Update User 103", "Успішно збережено в базі", "HTTP 200 OK", GREEN_F, FIELD),
        ("Елемент #4: Update User 104", "Таймаут виклику білінгу", "HTTP 504 Gateway Timeout", RED_F, POS),
    ]

    for i, (title, desc, status, bg, strk) in enumerate(items_status):
        iy = 125 + i * 70
        f.append(rect(355, iy, 360, 60, fill=bg, stroke=strk, sw=1.2, rx=4))
        f.append(text(460, iy + 22, title, size=10.5, bold=True, anchor="start"))
        f.append(text(460, iy + 44, desc, size=9.8, color=MUTED, anchor="start"))
        f.append(rect(610, iy + 10, 95, 40, fill="#ffffff", stroke=strk, sw=1.0))
        f.append(text(657, iy + 34, status.split()[1], size=10, bold=True, color=strk))

    f.append(arrow(735, 240, 795, 240, color=LINE, sw=1.8))

    # Консолідована відповідь
    f.append(rect(800, 80, 280, 340, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(940, 108, "Multi-Status Response DTO", size=11.5, bold=True, color=FIELD))
    f.append(fitbox(815, 125, 250, 280,
                    "{\n  \"batchId\": \"b-9912\",\n  \"total\": 4,\n  \"succeeded\": 2,\n  \"failed\": 2,\n  \"results\": [\n    {\"id\": 1, \"code\": 200},\n    {\"id\": 2, \"code\": 422},\n    {\"id\": 3, \"code\": 200},\n    {\"id\": 4, \"code\": 504}\n  ]\n}",
                    size=10.5, fill="#ffffff", stroke=FIELD))

    # Висновок
    f.append(fitbox(40, 435, 1040, 48,
                    "Пакетований інтерфейс не повинен падати цілком через помилку одного елемента.\n"
                    "Контракт повертає структурований масив статусів (Multi-Status / HTTP 207), дозволяючи клієнту розпарсити успішні результати та повторити лише збійні.",
                    size=11, fill=FILL))

    render(os.path.join(OUT, 'batch-partial-failure-model.svg'), W, H, *f)


if __name__ == "__main__":
    fig_chatty_vs_chunky()
    fig_network_overhead()
    fig_remote_facade_arch()
    fig_batch_partial_failure()
    print("All figures generated successfully.")
