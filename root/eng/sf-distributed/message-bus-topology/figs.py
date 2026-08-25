# -*- coding: utf-8 -*-
"""Фігури теми «Топологія шини повідомлень». Вивід — ./img/*.svg"""
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
GRAY_F  = "#f8f9fa"
PURPLE_F= "#ede7f6"

# ── 1. bus-topologies-overview: 4 класичні топології шини ──────────────────
def fig_bus_topologies_overview():
    W, H = 1000, 580
    f = []

    f.append(rect(10, 10, 980, 560, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Архітектурні топології шини повідомлень", size=14, bold=True))

    # 4 квадранти: (2x2)
    # Квадрант 1: Централізований брокер (Hub-and-Spoke)
    f.append(rect(20, 55, 465, 245, fill=GRAY_F, stroke=LINE, sw=1, rx=6))
    f.append(text(252, 75, "1. Централізований брокер (Hub-and-Spoke)", size=12, bold=True, color=POS))
    
    broker_b, _, _ = textbox(252, 160, "ЦЕНТРАЛЬНИЙ\nБРОКЕР\n(RabbitMQ / Kafka)", size=11, bold=True, min_w=125, pad=6, fill=RED_F, stroke=POS)
    f.append(broker_b)

    nodes_1 = [(80, 110, "Сервіс А"), (80, 210, "Сервіс Б"), (425, 110, "Сервіс В"), (425, 210, "Сервіс Г")]
    for nx, ny, nlbl in nodes_1:
        nb, _, _ = textbox(nx, ny, nlbl, size=10, min_w=75, pad=4, fill=FILL, stroke=LINE)
        f.append(nb)
    
    f.append(arrow(120, 115, 185, 145, color=LINE, sw=1.2))
    f.append(arrow(120, 205, 185, 175, color=LINE, sw=1.2))
    f.append(arrow(318, 145, 385, 115, color=LINE, sw=1.2))
    f.append(arrow(318, 175, 385, 205, color=LINE, sw=1.2))
    f.append(text(252, 280, "2 мережеві стрибки • Єдина точка збою • Глобальний аудит", size=10, color=MUTED, italic=True))

    # Квадрант 2: Федеративна / Кластерна шина (Federated)
    f.append(rect(515, 55, 465, 245, fill=GRAY_F, stroke=LINE, sw=1, rx=6))
    f.append(text(747, 75, "2. Федеративна / Регіональна шина", size=12, bold=True, color=NEG))

    b_eu, _, _ = textbox(630, 160, "Брокер ЄС\n(Франкфурт)", size=10.5, bold=True, min_w=95, pad=5, fill=BLUE_F, stroke=NEG)
    b_us, _, _ = textbox(865, 160, "Брокер США\n(Орегон)", size=10.5, bold=True, min_w=95, pad=5, fill=BLUE_F, stroke=NEG)
    f.append(b_eu)
    f.append(b_us)

    f.append(arrow(685, 155, 810, 155, color=NEG, sw=1.5))
    f.append(arrow(810, 165, 685, 165, color=NEG, sw=1.5))
    f.append(text(747, 145, "WAN Міст / Shovel", size=9.5, color=NEG, italic=True))

    neu, _, _ = textbox(565, 110, "Вузол ЄС 1", size=10, min_w=70, pad=4, fill=FILL, stroke=LINE)
    neu2, _, _ = textbox(565, 210, "Вузол ЄС 2", size=10, min_w=70, pad=4, fill=FILL, stroke=LINE)
    nus, _, _ = textbox(930, 110, "Вузол США 1", size=10, min_w=70, pad=4, fill=FILL, stroke=LINE)
    nus2, _, _ = textbox(930, 210, "Вузол США 2", size=10, min_w=70, pad=4, fill=FILL, stroke=LINE)
    f.append(neu); f.append(neu2); f.append(nus); f.append(nus2)

    f.append(arrow(605, 115, 630, 135, color=LINE, sw=1.1))
    f.append(arrow(605, 205, 630, 185, color=LINE, sw=1.1))
    f.append(arrow(865, 135, 890, 115, color=LINE, sw=1.1))
    f.append(arrow(865, 185, 890, 205, color=LINE, sw=1.1))
    f.append(text(747, 280, "Локальна затримка низька • WAN трафік фільтрується • Складніший роутинг", size=10, color=MUTED, italic=True))

    # Квадрант 3: Безброкерна однорангова шина (Peer-to-Peer / ZeroMQ / DDS)
    f.append(rect(20, 315, 465, 245, fill=GRAY_F, stroke=LINE, sw=1, rx=6))
    f.append(text(252, 335, "3. Безброкерна однорангова шина (P2P / DDS)", size=12, bold=True, color=FIELD))

    p2p_nodes = [(100, 395, "Вузол 1\n(Publisher)"), (100, 495, "Вузол 2\n(Pub / Sub)"), 
                 (405, 395, "Вузол 3\n(Subscriber)"), (405, 495, "Вузол 4\n(Subscriber)")]
    for nx, ny, nlbl in p2p_nodes:
        nb, _, _ = textbox(nx, ny, nlbl, size=10, bold=True, min_w=85, pad=4, fill=GREEN_F, stroke=FIELD)
        f.append(nb)

    # Прямі стрілки між вузлами
    f.append(arrow(145, 395, 360, 395, color=FIELD, sw=1.3))
    f.append(arrow(145, 400, 360, 490, color=FIELD, sw=1.3))
    f.append(arrow(145, 490, 360, 400, color=FIELD, sw=1.3))
    f.append(arrow(145, 495, 360, 495, color=FIELD, sw=1.3))
    f.append(text(252, 445, "Прямі сокети / Кільцеві буфери", size=9.5, color=FIELD, italic=True))
    f.append(text(252, 542, "1 мережевий стрибок • Мікросекундна затримка • Складний NAT/виявлення", size=10, color=MUTED, italic=True))

    # Квадрант 4: Апаратна мультикаст-шина (Multicast / PGM)
    f.append(rect(515, 315, 465, 245, fill=GRAY_F, stroke=LINE, sw=1, rx=6))
    f.append(text(747, 335, "4. Мережева мультикаст-шина (L2/L3 Multicast)", size=12, bold=True, color="#8e44ad"))

    sw_b, _, _ = textbox(747, 445, "МЕРЕЖЕВИЙ КОМУТАТОР\n(L2/L3 Switch / IGMP Snooping)\nАпаратне клонування кадрів", size=10, bold=True, min_w=185, pad=5, fill=PURPLE_F, stroke="#8e44ad")
    f.append(sw_b)

    pub_m, _, _ = textbox(575, 445, "Паблішер\n(HFT Trading)", size=10, bold=True, min_w=85, pad=4, fill=FILL, stroke=LINE)
    sub1_m, _, _ = textbox(920, 385, "Підписник 1", size=10, min_w=75, pad=4, fill=FILL, stroke=LINE)
    sub2_m, _, _ = textbox(920, 445, "Підписник 2", size=10, min_w=75, pad=4, fill=FILL, stroke=LINE)
    sub3_m, _, _ = textbox(920, 505, "Підписник 3", size=10, min_w=75, pad=4, fill=FILL, stroke=LINE)
    f.append(pub_m); f.append(sub1_m); f.append(sub2_m); f.append(sub3_m)

    f.append(arrow(625, 445, 650, 445, color="#8e44ad", sw=1.5))
    f.append(arrow(842, 435, 878, 390, color="#8e44ad", sw=1.2))
    f.append(arrow(842, 445, 878, 445, color="#8e44ad", sw=1.2))
    f.append(arrow(842, 455, 878, 500, color="#8e44ad", sw=1.2))
    f.append(text(747, 542, "0 навантаження на CPU при fan-out • Вимагає On-Premises/Bare-Metal", size=10, color=MUTED, italic=True))

    render(out("bus-topologies-overview.svg"), W, H, *f,
           title="Архітектурні топології шини повідомлень")


# ── 2. logical-vs-physical-bus: Логічна абстракція проти фізичної реальності ──
def fig_logical_vs_physical_bus():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, 980, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Логічна шина проти фізичної топології мережі", size=14, bold=True))

    # Верхня панель: Логічна шина
    f.append(rect(25, 55, 950, 160, fill=BLUE_F, stroke=NEG, sw=1.2, rx=6))
    f.append(text(500, 78, "Логічний погляд програми: Єдина плоска шина повідомлень (Shared Medium Abstraction)", size=12, bold=True, color=NEG))

    # Суцільна лінія шини
    f.append(rect(80, 130, 840, 18, fill=NEG, stroke=LINE, sw=1, rx=4))
    f.append(text(500, 143, "ЛОГІЧНА ШИНА: Шлях за темами (Subject: orders.eu.*, telemetry.gps)", size=10.5, color="#ffffff", bold=True))

    log_nodes = [(140, "Сервіс замовлень"), (380, "Платіжний шлюз"), (620, "Фрод-контроль"), (860, "Складська база")]
    for nx, nlbl in log_nodes:
        nb, _, _ = textbox(nx, 100, nlbl, size=10, min_w=105, pad=4, fill=FILL, stroke=LINE)
        f.append(nb)
        f.append(line(nx, 116, nx, 130, color=NEG, sw=2))

    f.append(text(500, 198, "Кожен вузол вважає, що підключений до спільного мідного кабелю й отримує потрібні теми без посередників", size=10.5, color=MUTED, italic=True))

    # Нижня панель: Фізична мережева реальність
    f.append(rect(25, 230, 950, 205, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(500, 252, "Фізична реальність: Оверлей над точковими IP-з'єднаннями", size=12, bold=True, color=POS))

    # 3 фізичні варіанти
    # Варіант А: Зірка
    f.append(rect(45, 275, 275, 145, fill=FILL, stroke=MUTED, sw=1, rx=4))
    f.append(text(182, 295, "А. Зірка через брокер", size=10.5, bold=True, color=POS))
    f.append(circle(182, 345, 16, fill=RED_F, stroke=POS, sw=1.5))
    f.append(text(182, 350, "Hub", size=9.5, bold=True, color=POS))
    for cx, cy in [(115, 325), (115, 370), (250, 325), (250, 370)]:
        f.append(circle(cx, cy, 11, fill=BLUE_F, stroke=NEG, sw=1))
        f.append(line(cx, cy, 182, 345, color=LINE, sw=1, dash="2,2"))
    f.append(text(182, 405, "2 хопи, централізований буфер", size=9.5, color=MUTED))

    # Варіант Б: Повна однорангова сітка
    f.append(rect(362, 275, 275, 145, fill=FILL, stroke=MUTED, sw=1, rx=4))
    f.append(text(500, 295, "Б. Повнозв'язна P2P-сітка", size=10.5, bold=True, color=FIELD))
    p_pts = [(430, 335), (430, 375), (570, 335), (570, 375)]
    for i, p1 in enumerate(p_pts):
        for j, p2 in enumerate(p_pts):
            if i < j:
                f.append(line(p1[0], p1[1], p2[0], p2[1], color=FIELD, sw=1, dash="2,2"))
    for cx, cy in p_pts:
        f.append(circle(cx, cy, 11, fill=GREEN_F, stroke=FIELD, sw=1.2))
    f.append(text(500, 405, "1 хоп, N*(N-1)/2 сокетів", size=9.5, color=MUTED))

    # Варіант В: Мультикаст комутатор
    f.append(rect(680, 275, 275, 145, fill=FILL, stroke=MUTED, sw=1, rx=4))
    f.append(text(817, 295, "В. Дерево комутаторів L2/L3", size=10.5, bold=True, color="#8e44ad"))
    f.append(rect(782, 335, 70, 24, fill=PURPLE_F, stroke="#8e44ad", sw=1.2, rx=3))
    f.append(text(817, 350, "Switch", size=9.5, bold=True, color="#8e44ad"))
    for cx, cy in [(725, 335), (725, 375), (910, 335), (910, 375)]:
        f.append(circle(cx, cy, 11, fill=FILL, stroke=LINE, sw=1))
        f.append(line(cx, cy, 817, 347, color="#8e44ad", sw=1.2))
    f.append(text(817, 405, "1 хоп, клонування в кремнії", size=9.5, color=MUTED))

    render(out("logical-vs-physical-bus.svg"), W, H, *f,
           title="Логічна шина проти фізичної топології мережі")


# ── 3. brokerless-vs-brokered-latency-hops: Шлях пакета та затримка ─────────
def fig_brokerless_vs_brokered():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, 980, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Порівняння затримки та черг: Брокер проти Безброкерної шини", size=14, bold=True))

    # Ліва половина: Брокерна модель (2 хопи)
    f.append(rect(25, 55, 460, 380, fill=GRAY_F, stroke=POS, sw=1.2, rx=6))
    f.append(text(255, 78, "Централізований брокер: 2 хопи, черга в центрі", size=12, bold=True, color=POS))

    # Складові ланцюжка
    f.append(rect(45, 105, 115, 140, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(102, 125, "Відправник", size=10.5, bold=True))
    f.append(rect(55, 145, 95, 24, fill=BLUE_F, stroke=NEG, sw=1, rx=3))
    f.append(text(102, 160, "App Code", size=9.5))
    f.append(rect(55, 185, 95, 48, fill=FILL, stroke=MUTED, sw=1, rx=3))
    f.append(text(102, 202, "Socket TCP", size=9.5))
    f.append(text(102, 220, "Egress Buffer", size=9))

    # Брокер посередині
    f.append(rect(190, 105, 130, 205, fill=RED_F, stroke=POS, sw=1.5, rx=4))
    f.append(text(255, 125, "Брокер (Hub)", size=10.5, bold=True, color=POS))
    f.append(rect(200, 140, 110, 38, fill="#ffffff", stroke=POS, sw=1, rx=3))
    f.append(text(255, 154, "Ingress Buffer", size=9.5))
    f.append(text(255, 169, "(TCP In)", size=9, color=MUTED))
    
    f.append(rect(200, 185, 110, 48, fill="#ffffff", stroke=POS, sw=1.2, rx=3))
    f.append(text(255, 202, "Черга на диску/RAM", size=9.5, bold=True))
    f.append(text(255, 220, "(PageCache/DB)", size=9, color=MUTED))

    f.append(rect(200, 240, 110, 38, fill="#ffffff", stroke=POS, sw=1, rx=3))
    f.append(text(255, 255, "Маршрутизатор", size=9.5))
    f.append(text(255, 270, "(Egress Queues)", size=9, color=MUTED))

    # Отримувач
    f.append(rect(350, 105, 115, 140, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(407, 125, "Отримувач", size=10.5, bold=True))
    f.append(rect(360, 145, 95, 48, fill=FILL, stroke=MUTED, sw=1, rx=3))
    f.append(text(407, 162, "Socket TCP", size=9.5))
    f.append(text(407, 180, "Ingress Buffer", size=9))
    f.append(rect(360, 205, 95, 24, fill=GREEN_F, stroke=FIELD, sw=1, rx=3))
    f.append(text(407, 220, "App Handler", size=9.5))

    # Стрілки передачі
    f.append(arrow(160, 200, 190, 155, color=POS, sw=1.5))
    f.append(text(175, 170, "Хоп 1", size=9.5, bold=True, color=POS))
    f.append(arrow(320, 255, 350, 165, color=POS, sw=1.5))
    f.append(text(335, 200, "Хоп 2", size=9.5, bold=True, color=POS))

    f.append(rect(40, 325, 430, 95, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(255, 345, "Метрики брокерної топології:", size=10, bold=True))
    f.append(text(255, 363, "• Затримка: 1.5 – 15.0 мс (подвійний контекст-свіч ОС + диск)", size=9.5, color=POS))
    f.append(text(255, 381, "• Пропускна здатність обмежена NIC і CPU брокера", size=9.5, color=POS))
    f.append(text(255, 399, "• Протитиск ізольовано брокером (витримує сплески навантаження)", size=9.5, color=FIELD))

    # Права половина: Безброкерна P2P шина (1 хоп)
    f.append(rect(515, 55, 460, 380, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(745, 78, "Безброкерна шина (ZeroMQ/DDS): 1 прямий хоп", size=12, bold=True, color=FIELD))

    # Відправник P2P
    f.append(rect(540, 115, 175, 185, fill=FILL, stroke=FIELD, sw=1.3, rx=4))
    f.append(text(627, 135, "Відправник (Publisher)", size=10.5, bold=True, color=FIELD))
    f.append(rect(550, 150, 155, 25, fill=BLUE_F, stroke=NEG, sw=1, rx=3))
    f.append(text(627, 166, "Бізнес-код (Zero-Copy)", size=9.5))
    f.append(rect(550, 185, 155, 48, fill=GREEN_F, stroke=FIELD, sw=1, rx=3))
    f.append(text(627, 202, "Локальний Ring Buffer", size=9.5, bold=True))
    f.append(text(627, 220, "(High Water Mark: 10k msg)", size=9, color=MUTED))
    f.append(rect(550, 240, 155, 38, fill=FILL, stroke=LINE, sw=1, rx=3))
    f.append(text(627, 260, "TCP/IPC Egress Engine", size=9.5))

    # Отримувач P2P
    f.append(rect(775, 115, 175, 185, fill=FILL, stroke=FIELD, sw=1.3, rx=4))
    f.append(text(862, 135, "Отримувач (Subscriber)", size=10.5, bold=True, color=FIELD))
    f.append(rect(785, 150, 155, 38, fill=FILL, stroke=LINE, sw=1, rx=3))
    f.append(text(862, 170, "TCP Ingress / Фільтр тем", size=9.5))
    f.append(rect(785, 195, 155, 48, fill=GREEN_F, stroke=FIELD, sw=1, rx=3))
    f.append(text(862, 212, "Клієнтський буфер пам'яті", size=9.5, bold=True))
    f.append(text(862, 230, "(Lock-Free / SPSC Queue)", size=9, color=MUTED))
    f.append(rect(785, 250, 155, 25, fill=GREEN_F, stroke=FIELD, sw=1, rx=3))
    f.append(text(862, 266, "App Handler Execution", size=9.5))

    # Пряма стрілка
    f.append(arrow(715, 260, 775, 170, color=FIELD, sw=2))
    f.append(text(745, 205, "1 Прямий хоп", size=10, bold=True, color=FIELD))

    f.append(rect(530, 325, 430, 95, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(745, 345, "Метрики безброкерної топології:", size=10, bold=True))
    f.append(text(745, 363, "• Затримка: 15 – 120 мікросекунд (sub-microsecond на IPC)", size=9.5, color=FIELD))
    f.append(text(745, 381, "• Пропускна здатність обмежена лише проводом мережі", size=9.5, color=FIELD))
    f.append(text(745, 399, "• Буфери у пам'яті клієнта; ризик OOM або втрати за переповнення", size=9.5, color=POS))

    render(out("brokerless-vs-brokered-latency-hops.svg"), W, H, *f,
           title="Порівняння затримки та черг: Брокер проти Безброкерної шини")


# ── 4. hierarchical-edge-bus: Гібридна ієрархічна шина Edge-to-Cloud ─────────
def fig_hierarchical_edge_bus():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, 980, 460, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 32, "Ієрархічна гібридна топологія: від периферії до хмарного бекбону", size=14, bold=True))

    # Рівень 1: Локальні вузли (Рівень Edge / IoT / Robot / Car)
    f.append(rect(25, 55, 280, 400, fill=GREEN_F, stroke=FIELD, sw=1.3, rx=6))
    f.append(text(165, 78, "Рівень 1: Периферія (Edge / Real-time)", size=11.5, bold=True, color=FIELD))
    f.append(text(165, 96, "Безброкерна шина DDS / ZeroMQ / CAN", size=9.5, color=MUTED, italic=True))

    e_nodes = [
        ("Датчик LiDAR / Радар\n(100 МБ/с, P2P)", 135),
        ("Контролер приводу / Мотор\n(Критична затримка < 1 мс)", 210),
        ("Блок комп'ютерного зору\n(ML Inference Node)", 285),
        ("Edge Gateway Daemon\n(Агрегатор телеметрії)", 365)
    ]
    for lbl, ny in e_nodes:
        is_gw = "Gateway" in lbl
        fill_col = BLUE_F if is_gw else FILL
        strk_col = NEG if is_gw else LINE
        b, _, _ = textbox(165, ny, lbl, size=9.5, bold=is_gw, min_w=240, pad=5, fill=fill_col, stroke=strk_col)
        f.append(b)

    f.append(arrow(165, 160, 165, 190, color=FIELD, sw=1.2))
    f.append(arrow(165, 235, 165, 265, color=FIELD, sw=1.2))
    f.append(arrow(165, 310, 165, 345, color=NEG, sw=1.4))
    f.append(text(165, 435, "Локальний контур: RTOS, IPC, мікросекунди", size=9.5, color=FIELD, italic=True))

    # Рівень 2: Регіональний / Фабричний рівень (Edge Broker)
    f.append(rect(345, 55, 280, 400, fill=BLUE_F, stroke=NEG, sw=1.3, rx=6))
    f.append(text(485, 78, "Рівень 2: Регіональний шлюз / Фабрика", size=11.5, bold=True, color=NEG))
    f.append(text(485, 96, "Кластерні брокери MQTT / EMQX / RabbitMQ", size=9.5, color=MUTED, italic=True))

    f.append(rect(365, 125, 240, 80, fill=FILL, stroke=NEG, sw=1, rx=4))
    f.append(text(485, 145, "Локальний MQTT Брокер", size=10, bold=True, color=NEG))
    f.append(text(485, 165, "• Буферизація офлайн-станів", size=9.5))
    f.append(text(485, 183, "• Фільтрація локальних подій", size=9.5))

    f.append(rect(365, 220, 240, 90, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(485, 240, "Локальні оператори й SCADA", size=10, bold=True))
    f.append(text(485, 258, "• Моніторинг цеху в реальному часі", size=9.5))
    f.append(text(485, 275, "• Аварійне відключення конвеєра", size=9.5))
    f.append(text(485, 292, "• Робота без доступу до хмари", size=9.5, color=FIELD))

    f.append(rect(365, 330, 240, 75, fill=WARN_F, stroke=POS, sw=1, rx=4))
    f.append(text(485, 350, "Shovel / CDC Bridge Daemon", size=10, bold=True, color=POS))
    f.append(text(485, 368, "Стиснення й батчинг телеметрії", size=9))
    f.append(text(485, 384, "Відправка через WAN / Starlink / 5G", size=9))

    f.append(arrow(285, 365, 365, 160, color=NEG, sw=1.5))
    f.append(arrow(485, 205, 485, 220, color=LINE, sw=1.2))
    f.append(arrow(485, 205, 485, 330, color=POS, sw=1.2))
    f.append(text(485, 435, "Автономність майданчика за втрати зв'язку", size=9.5, color=NEG, italic=True))

    # Рівень 3: Глобальна хмарна шина подій (Cloud Backbone)
    f.append(rect(665, 55, 310, 400, fill=PURPLE_F, stroke="#8e44ad", sw=1.3, rx=6))
    f.append(text(820, 78, "Рівень 3: Глобальний хмарний бекбон", size=11.5, bold=True, color="#8e44ad"))
    f.append(text(820, 96, "Kafka / Apache Pulsar / EventBridge", size=9.5, color=MUTED, italic=True))

    f.append(rect(685, 125, 270, 90, fill=FILL, stroke="#8e44ad", sw=1.2, rx=4))
    f.append(text(820, 145, "Глобальний журнал подій (Kafka)", size=10, bold=True, color="#8e44ad"))
    f.append(text(820, 164, "• Довговічне збереження (Retention 30d)", size=9.5))
    f.append(text(820, 181, "• Точний порядок у партиціях", size=9.5))
    f.append(text(820, 198, "• Масштабування споживачів", size=9.5))

    c_subs = [
        ("ML Навчання моделей (Datalake / S3)", 255),
        ("Фінансовий білінг і звіти", 320),
        ("Глобальний дашборд флоту / Fleet Ops", 385)
    ]
    for lbl, ny in c_subs:
        b, _, _ = textbox(820, ny, lbl, size=9.5, min_w=250, pad=4, fill=FILL, stroke=LINE)
        f.append(b)

    f.append(arrow(605, 365, 685, 165, color=POS, sw=1.5))
    f.append(arrow(820, 215, 820, 235, color="#8e44ad", sw=1.2))
    f.append(arrow(820, 275, 820, 300, color="#8e44ad", sw=1.2))
    f.append(arrow(820, 340, 820, 365, color="#8e44ad", sw=1.2))
    f.append(text(820, 435, "Глобальний контекст і аналітика флоту", size=9.5, color="#8e44ad", italic=True))

    render(out("hierarchical-edge-bus.svg"), W, H, *f,
           title="Ієрархічна гібридна топологія: від периферії до хмарного бекбону")


def main():
    fig_bus_topologies_overview()
    fig_logical_vs_physical_bus()
    fig_brokerless_vs_brokered()
    fig_hierarchical_edge_bus()

if __name__ == '__main__':
    main()
