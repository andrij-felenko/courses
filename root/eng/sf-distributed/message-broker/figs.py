# -*- coding: utf-8 -*-
"""Фігури теми «Брокер повідомлень». Вивід — ./img/*.svg"""
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

# ── 1. broker-architecture-overview: Внутрішня архітектура брокера ───────────
def fig_broker_architecture_overview():
    W, H = 1040, 480
    f = []

    # Загальний контур сервера-брокера
    f.append(rect(190, 20, 660, 440, fill="#ffffff", stroke=LINE, sw=2, rx=10))
    f.append(text(520, 48, "СЕРВЕР-БРОКЕР ПОВІДОМЛЕНЬ (Message Broker Core Engine)", size=14, bold=True, color=INK))

    # Продюсери зліва
    f.append(rect(20, 80, 130, 320, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(85, 105, "Продюсери", size=13, bold=True, color=POS))
    f.append(text(85, 125, "(Видавці подій)", size=10, color=MUTED))

    producers = [
        ("Web API\n(HTTP/REST)", 150),
        ("Мікросервіс\n(AMQP 0-9-1)", 230),
        ("IoT-шлюз\n(MQTT 5.0)", 310),
        ("Біллінг\n(gRPC/STOMP)", 375)
    ]
    for lbl, y in producers:
        b, _, _ = textbox(85, y, lbl, size=10.5, bold=True, min_w=110, pad=6, fill=RED_F, stroke=POS)
        f.append(b)

    # 1. Шар прийому з'єднань і мультиплексування
    f.append(rect(210, 75, 125, 365, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(272, 98, "Мережевий шар", size=11.5, bold=True, color=NEG))
    f.append(text(272, 115, "(IO Multiplexing)", size=9.5, color=MUTED))
    net_items = [
        ("epoll / kqueue\nTCP Acceptor", 145),
        ("TLS термінація\nй перевірка", 215),
        ("Канали AMQP\n(Channel Mux)", 285),
        ("Протокольні\nтранслятори", 355)
    ]
    for lbl, y in net_items:
        b, _, _ = textbox(272, y, lbl, size=9.5, min_w=105, pad=5, fill="#ffffff", stroke=NEG)
        f.append(b)

    # Стрілки від продюсерів до мережевого шару
    for _, y in producers:
        f.append(arrow(140, y, 210, y, color=POS, sw=1.3))

    # 2. Двигун маршрутизації та обмінники
    f.append(rect(360, 75, 140, 365, fill=WARN_F, stroke="#d39e00", sw=1.5, rx=6))
    f.append(text(430, 98, "Маршрутизатор", size=11.5, bold=True, color="#856404"))
    f.append(text(430, 115, "(Exchange Engine)", size=9.5, color=MUTED))
    ex_items = [
        ("Direct Exchange\n(хеш-таблиця O(1))", 145),
        ("Topic Exchange\n(дерево префіксів)", 215),
        ("Fanout Exchange\n(широкомовлення)", 285),
        ("Dead Letter DLX\n(помилки й таймаути)", 355)
    ]
    for lbl, y in ex_items:
        b, _, _ = textbox(430, y, lbl, size=9.5, min_w=120, pad=5, fill="#ffffff", stroke="#d39e00")
        f.append(b)

    # Стрілка від мережевого шару до маршрутизатора
    f.append(arrow(335, 255, 360, 255, color=INK, sw=1.8))

    # 3. Буфери черг і пам'ять
    f.append(rect(525, 75, 145, 230, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(597, 98, "Буфери черг (RAM)", size=11.5, bold=True, color=FIELD))
    f.append(text(597, 115, "(FIFO / Пріоритети)", size=9.5, color=MUTED))
    q_items = [
        ("Черга «orders»\n(Кільцевий буфер)", 145),
        ("Черга «payments»\n(Пріоритетна черга)", 205),
        ("Черга «telemetry»\n(Швидка RAM черга)", 265)
    ]
    for lbl, y in q_items:
        b, _, _ = textbox(597, y, lbl, size=9.5, min_w=125, pad=5, fill="#ffffff", stroke=FIELD)
        f.append(b)

    # 4. Дискова підсистема персистентності
    f.append(rect(525, 320, 145, 120, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=6))
    f.append(text(597, 342, "Сховище на диску", size=11, bold=True, color="#343a40"))
    f.append(text(597, 368, "WAL журнал + Сегменти\nСкидання сторінок (fsync)\nКворумний лог (Raft)", size=9.5, color=INK))

    # Зв'язки між маршрутизатором, чергами та диском
    f.append(arrow(500, 145, 525, 145, color=FIELD, sw=1.4))
    f.append(arrow(500, 205, 525, 205, color=FIELD, sw=1.4))
    f.append(arrow(500, 265, 525, 265, color=FIELD, sw=1.4))
    f.append(line(597, 305, 597, 320, color="#495057", sw=1.4, dash="3,3"))

    # 5. Диспетчер і відстеження підтверджень (In-flight tracker)
    f.append(rect(695, 75, 135, 365, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(762, 98, "Диспетчер видачі", size=11.5, bold=True, color=NEG))
    f.append(text(762, 115, "(Delivery Engine)", size=9.5, color=MUTED))
    disp_items = [
        ("Prefetch контроль\n(Кредити споживачів)", 145),
        ("In-flight реєстр\n(Очікування ACK)", 215),
        ("Таймаути оренди\nта перевідправка", 285),
        ("Лічильник спроб\n(Poison Pill захист)", 355)
    ]
    for lbl, y in disp_items:
        b, _, _ = textbox(762, y, lbl, size=9.5, min_w=115, pad=5, fill="#ffffff", stroke=NEG)
        f.append(b)

    # Стрілки від черг до диспетчера
    f.append(arrow(670, 200, 695, 200, color=NEG, sw=1.6))

    # Споживачі справа
    f.append(rect(890, 80, 130, 320, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(955, 105, "Споживачі", size=13, bold=True, color=FIELD))
    f.append(text(955, 125, "(Воркери / Служби)", size=10, color=MUTED))

    consumers = [
        ("Воркер замовлень\n(ACK після БД)", 150),
        ("Платіжний шлюз\n(Prefetch = 10)", 230),
        ("Сервіс аналітики\n(Пакетний ACK)", 310),
        ("Dead Letter\nІнспектор", 375)
    ]
    for lbl, y in consumers:
        b, _, _ = textbox(955, y, lbl, size=10.5, bold=True, min_w=110, pad=6, fill=GREEN_F, stroke=FIELD)
        f.append(b)

    # Стрілки від диспетчера до споживачів
    for _, y in consumers:
        f.append(arrow(830, y, 890, y, color=FIELD, sw=1.4))

    render(out("broker-architecture-overview.svg"), W, H, *f,
           title="Внутрішня архітектура та конвеєр обробки брокера повідомлень")


# ── 2. exchange-routing-models: Моделі та типи обмінників (Exchanges) ────────
def fig_exchange_routing_models():
    W, H = 1040, 440
    f = []

    # Блок 1: Direct Exchange (Зліва вгорі)
    f.append(rect(15, 15, 495, 195, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(260, 38, "1. Direct Exchange (Точний ключ маршрутизації)", size=12.5, bold=True, color=INK))
    
    b_pub1, _, _ = textbox(75, 110, "Продюсер\nKey: \"error\"", size=10, min_w=85, pad=5, fill=RED_F, stroke=POS)
    b_ex1, _, _ = textbox(215, 110, "Direct\nExchange\n(Хеш O(1))", size=10.5, bold=True, min_w=90, pad=6, fill=WARN_F, stroke="#d39e00")
    b_q1a, _, _ = textbox(370, 75, "Черга «errors»\n[Bind: \"error\"]", size=9.5, min_w=105, pad=5, fill=GREEN_F, stroke=FIELD)
    b_q1b, _, _ = textbox(370, 145, "Черга «all_logs»\n[Bind: \"info\"]", size=9.5, min_w=105, pad=5, fill=GRAY_F, stroke=MUTED)
    f.extend([b_pub1, b_ex1, b_q1a, b_q1b])
    f.append(arrow(118, 110, 170, 110, color=POS, sw=1.3))
    f.append(arrow(260, 100, 318, 75, color=FIELD, sw=1.5))
    f.append(line(260, 120, 318, 145, color=MUTED, sw=1, dash="3,3"))
    f.append(text(465, 145, "Відхилено", size=9, color=MUTED))

    # Блок 2: Fanout Exchange (Справа вгорі)
    f.append(rect(530, 15, 495, 195, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(775, 38, "2. Fanout Exchange (Широкомовна розсилка усім)", size=12.5, bold=True, color=INK))
    
    b_pub2, _, _ = textbox(590, 110, "Продюсер\n(Ключ ігнорується)", size=10, min_w=85, pad=5, fill=RED_F, stroke=POS)
    b_ex2, _, _ = textbox(730, 110, "Fanout\nExchange\n(Копіювання ref)", size=10.5, bold=True, min_w=90, pad=6, fill=WARN_F, stroke="#d39e00")
    b_q2a, _, _ = textbox(885, 75, "Черга «email_svc»", size=9.5, min_w=105, pad=5, fill=GREEN_F, stroke=FIELD)
    b_q2b, _, _ = textbox(885, 145, "Черга «sms_svc»", size=9.5, min_w=105, pad=5, fill=GREEN_F, stroke=FIELD)
    f.extend([b_pub2, b_ex2, b_q2a, b_q2b])
    f.append(arrow(633, 110, 685, 110, color=POS, sw=1.3))
    f.append(arrow(775, 95, 833, 75, color=FIELD, sw=1.5))
    f.append(arrow(775, 125, 833, 145, color=FIELD, sw=1.5))

    # Блок 3: Topic Exchange (Зліва внизу)
    f.append(rect(15, 225, 495, 200, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(260, 248, "3. Topic Exchange (Ієрархічні шаблони * та #)", size=12.5, bold=True, color=INK))
    
    b_pub3, _, _ = textbox(75, 325, "Продюсер\n\"eu.orders.vip\"", size=10, min_w=85, pad=5, fill=RED_F, stroke=POS)
    b_ex3, _, _ = textbox(215, 325, "Topic\nExchange\n(Prefix Trie)", size=10.5, bold=True, min_w=90, pad=6, fill=WARN_F, stroke="#d39e00")
    b_q3a, _, _ = textbox(370, 285, "Черга «all_eu»\n[Bind: \"eu.#\"]", size=9.5, min_w=105, pad=5, fill=GREEN_F, stroke=FIELD)
    b_q3b, _, _ = textbox(370, 365, "Черга «vip_only»\n[Bind: \"*.orders.vip\"]", size=9.5, min_w=105, pad=5, fill=GREEN_F, stroke=FIELD)
    f.extend([b_pub3, b_ex3, b_q3a, b_q3b])
    f.append(arrow(118, 325, 170, 325, color=POS, sw=1.3))
    f.append(arrow(260, 310, 318, 285, color=FIELD, sw=1.5))
    f.append(arrow(260, 340, 318, 365, color=FIELD, sw=1.5))

    # Блок 4: Headers & Dead Letter Exchange (Справа внизу)
    f.append(rect(530, 225, 495, 200, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(775, 248, "4. Headers та Dead-Letter Exchange (DLX)", size=12.5, bold=True, color=INK))
    
    b_pub4, _, _ = textbox(590, 325, "Повідомлення\n[TTL=0 або NACK]", size=10, min_w=90, pad=5, fill=RED_F, stroke=POS)
    b_ex4, _, _ = textbox(730, 325, "Dead Letter\nExchange\n(DLX / Fallback)", size=10.5, bold=True, min_w=90, pad=6, fill="#f8d7da", stroke=POS)
    b_q4a, _, _ = textbox(885, 285, "Черга «poison_dlq»\n(Аналіз збоїв)", size=9.5, min_w=110, pad=5, fill="#f8d7da", stroke=POS)
    b_q4b, _, _ = textbox(885, 365, "Черга «retry_delay»\n(Повтор через TTL)", size=9.5, min_w=110, pad=5, fill=WARN_F, stroke="#d39e00")
    f.extend([b_pub4, b_ex4, b_q4a, b_q4b])
    f.append(arrow(635, 325, 685, 325, color=POS, sw=1.3))
    f.append(arrow(775, 310, 830, 285, color=POS, sw=1.5))
    f.append(arrow(775, 340, 830, 365, color="#d39e00", sw=1.5))

    render(out("exchange-routing-models.svg"), W, H, *f,
           title="Моделі маршрутизації обмінників: Direct, Fanout, Topic та Dead Letter")


# ── 3. broker-flow-control-backpressure: Керування потоком і зворотний тиск ──
def fig_broker_flow_control_backpressure():
    W, H = 1000, 380
    f = []

    f.append(rect(15, 15, 970, 350, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Механізми зворотного тиску (Backpressure) та скидання на диск", size=14, bold=True, color=INK))

    # Фаза 1: Швидкий продюсер наповнює оперативну пам'ять
    f.append(rect(40, 75, 280, 265, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(180, 100, "1. Сплеск вхідного трафіку", size=12, bold=True, color=POS))
    f.append(mtext(180, 125, ["Продюсер: 50 000 msg/s", "Споживач: 5 000 msg/s", "Буфер RAM стрімко росте"], size=10, color=INK))
    
    # Стовпчик пам'яті
    f.append(rect(80, 175, 200, 140, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(rect(80, 215, 200, 100, fill=RED_F, stroke=POS, sw=1.5, rx=4))
    f.append(text(180, 245, "RAM: 85% (Переповнення)", size=10, bold=True, color=POS))
    f.append(line(75, 215, 285, 215, color=POS, sw=1.5, dash="4,2"))
    f.append(text(180, 205, "Watermark Ліміт (40%)", size=9, bold=True, color=POS))

    # Фаза 2: Спрацьовування сигналізації та пейджинг
    f.append(rect(360, 75, 280, 265, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(500, 100, "2. Скидання на диск (Paging)", size=12, bold=True, color="#856404"))
    f.append(mtext(500, 125, ["Брокер активує дисковий скид", "RAM звільняється для заголовків", "Тіла повідомлень ідуть у файл"], size=10, color=INK))

    b_ram_evict, _, _ = textbox(500, 195, "Очищення RAM\nВитіснення пейджів", size=10, min_w=160, pad=6, fill=WARN_F, stroke="#d39e00")
    b_disk_write, _, _ = textbox(500, 275, "Дисковий сегментний пул\n(Асинхронний запис)", size=10, min_w=170, pad=6, fill="#f1f3f5", stroke="#495057")
    f.extend([b_ram_evict, b_disk_write])
    f.append(arrow(500, 222, 500, 250, color="#495057", sw=1.5))

    # Фаза 3: Зупинка TCP сокетів продюсерів та Prefetch
    f.append(rect(680, 75, 280, 265, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(820, 100, "3. Блокування TCP і Prefetch", size=12, bold=True, color=FIELD))
    f.append(mtext(820, 125, ["TCP Zero-Window продюсерам", "Prefetch лімітує воркери", "Баланс відновлюється"], size=10, color=INK))

    b_tcp_pause, _, _ = textbox(820, 195, "TCP Socket Read: PAUSED\n(Продюсер блокується)", size=10, min_w=180, pad=6, fill=RED_F, stroke=POS)
    b_qos_credit, _, _ = textbox(820, 275, "Consumer basic.qos = 20\n(Видача лише під ACK)", size=10, min_w=180, pad=6, fill=GREEN_F, stroke=FIELD)
    f.extend([b_tcp_pause, b_qos_credit])
    f.append(arrow(820, 222, 820, 250, color=FIELD, sw=1.5))

    # Стрілки між фазами
    f.append(arrow(320, 205, 360, 205, color=INK, sw=1.6))
    f.append(arrow(640, 205, 680, 205, color=INK, sw=1.6))

    render(out("broker-flow-control-backpressure.svg"), W, H, *f,
           title="Керування зворотним тиском: водні позначки пам'яті, дисковий пейджинг та блокування сокетів")


# ── 4. broker-clustering-quorum: Кластеризація та кворумні черги ─────────────
def fig_broker_clustering_quorum():
    W, H = 1020, 420
    f = []

    f.append(rect(15, 15, 990, 390, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(510, 40, "Кластеризація брокерів: Класичні дзеркала проти Кворумних черг (Raft)", size=14, bold=True, color=INK))

    # Ліва половина: Classic Mirrored Queues (Active-Passive Sync)
    f.append(rect(30, 65, 460, 320, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(260, 90, "Класичні дзеркальні черги (Active-Passive)", size=12.5, bold=True, color=POS))
    f.append(text(260, 110, "Вразливі до Split-Brain при розриві мережі", size=10, color=MUTED, italic=True))

    b_m_leader, _, _ = textbox(130, 175, "Лідер (Master)\nВузол 1\n[Обробка I/O]", size=10.5, bold=True, min_w=120, pad=7, fill=RED_F, stroke=POS)
    b_m_fol1, _, _ = textbox(380, 140, "Дзеркало (Slave)\nВузол 2\n[Синхронне]", size=10, min_w=110, pad=6, fill=GRAY_F, stroke=MUTED)
    b_m_fol2, _, _ = textbox(380, 220, "Дзеркало (Slave)\nВузол 3\n[Несинхронне]", size=10, min_w=110, pad=6, fill=GRAY_F, stroke=MUTED)
    f.extend([b_m_leader, b_m_fol1, b_m_fol2])

    f.append(arrow(190, 165, 325, 145, color=POS, sw=1.3))
    f.append(line(190, 185, 325, 215, color=MUTED, sw=1.3, dash="3,3"))
    f.append(text(260, 275, "Розрив мережі призводить до роздвоєння лідерів", size=10.5, bold=True, color=POS))
    f.append(text(260, 295, "Втрата несинхронізованих повідомлень при збої", size=9.5, color=INK))

    # Права половина: Quorum Queues (Raft Consensus)
    f.append(rect(530, 65, 460, 320, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(760, 90, "Кворумні черги (Raft Consensus 2F+1)", size=12.5, bold=True, color=FIELD))
    f.append(text(760, 110, "Мажоритарна згода більшості: N/2 + 1 голосів", size=10, color=MUTED, italic=True))

    b_q_leader, _, _ = textbox(630, 175, "Raft Лідер\nВузол 1\n[Прийом запису]", size=10.5, bold=True, min_w=120, pad=7, fill=GREEN_F, stroke=FIELD)
    b_q_fol1, _, _ = textbox(880, 140, "Raft Послідовник\nВузол 2\n[Підтвердив: ACK]", size=10, min_w=115, pad=6, fill=GREEN_F, stroke=FIELD)
    b_q_fol2, _, _ = textbox(880, 220, "Raft Послідовник\nВузол 3\n[Офлайн / Збій]", size=10, min_w=115, pad=6, fill=GRAY_F, stroke=MUTED)
    f.extend([b_q_leader, b_q_fol1, b_q_fol2])

    f.append(arrow(690, 165, 822, 145, color=FIELD, sw=1.5))
    f.append(line(690, 185, 822, 215, color=MUTED, sw=1.3, dash="3,3"))
    f.append(text(760, 275, "Кворум досягнуто: 2 з 3 вузлів відповіли", size=10.5, bold=True, color=FIELD))
    f.append(text(760, 295, "Гарантована безпека: без дублювання лідерів", size=9.5, color=INK))

    render(out("broker-clustering-quorum.svg"), W, H, *f,
           title="Порівняння кластерних архітектур: дзеркальні черги та розподілений консенсус Raft")


if __name__ == "__main__":
    fig_broker_architecture_overview()
    fig_exchange_routing_models()
    fig_broker_flow_control_backpressure()
    fig_broker_clustering_quorum()
    print("Всі фігури згенеровано успішно.")
