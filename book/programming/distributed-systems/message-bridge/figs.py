# -*- coding: utf-8 -*-
"""Фігури теми «Міст повідомлень». Вивід — ./img/*.svg"""
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
PURPLE_F = "#f3e8fd"

# ── 1. isolated-brokers-vs-bridge: ізольовані середовища проти моста повідомлень
def fig_isolated_brokers_vs_bridge():
    W, H = 1000, 440
    f = []

    # Ліва половина: Пряма спроба з'єднання між несумісними середовищами
    f.append(rect(15, 15, 470, 405, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 42, "Без моста: несумісні протоколи та ізоляція мереж", size=13, bold=True, color=POS))

    # Джерело: Edge IoT (MQTT)
    b_src, _, _ = textbox(110, 115, "IoT Edge (MQTT)\n50 000 сенсорів\nПриватна LAN / NAT", size=10.5, bold=True, min_w=140, pad=6, fill=FILL, stroke=LINE)
    f.append(b_src)

    # Ціль 1: Хмарний Kafka кластер
    b_kfk, _, _ = textbox(380, 115, "Cloud Analytics (Kafka)\nПартиціонований лог\nПублічна хмара (TLS)", size=10.5, bold=True, min_w=150, pad=6, fill=RED_F, stroke=POS)
    f.append(b_kfk)

    # Ціль 2: Локальний ERP (RabbitMQ)
    b_rmq, _, _ = textbox(380, 275, "Локальний ERP (AMQP)\nRabbitMQ Exchange\nКорпоративний контур", size=10.5, bold=True, min_w=150, pad=6, fill=RED_F, stroke=POS)
    f.append(b_rmq)

    # Лінії помилок і конфліктів
    f.append(line(185, 115, 300, 115, color="#e74c3c", sw=1.5, dash="4,4"))
    f.append(text(242, 100, "✗ Несумісність MQTT ↔ Kafka API", size=9.5, color="#c0392b", bold=True))
    f.append(text(242, 133, "✗ Блокування вхідних портів NAT", size=9.5, color="#c0392b"))

    f.append(line(185, 135, 300, 260, color="#e74c3c", sw=1.5, dash="4,4"))
    f.append(text(215, 205, "✗ Обриви WAN та втрата пакетів", size=9.5, color="#c0392b", bold=True))

    f.append(text(250, 395, "✗ Відправники змушені знати чужі протоколи, адреси та авторизацію", size=10, color=POS, italic=True))

    # Права половина: Міст повідомлень як розв'язка
    f.append(rect(515, 15, 470, 405, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 42, "З мостом: прозоре перенесення та адаптація", size=13, bold=True, color=FIELD))

    b_src2, _, _ = textbox(590, 200, "Edge Джерело\n(MQTT Broker)\nЛокальний буфер", size=10.5, bold=True, min_w=120, pad=6, fill=FILL, stroke=LINE)
    f.append(b_src2)

    # Міст по центру
    b_bridge, _, _ = textbox(750, 200, "МІСТ ПОВІДОМЛЕНЬ\n(Message Bridge)\n\n• Споживач на джерелі\n• Трансляція заголовків\n• Продюсер на цілі\n• Подвійне підтвердження",
                             size=10.5, bold=True, min_w=140, pad=8, fill=BLUE_F, stroke=NEG, sw=1.8)
    f.append(b_bridge)

    b_dst1, _, _ = textbox(910, 120, "Cloud Kafka\nTopic: edge.sensors\nОфсети збережено", size=10.5, bold=True, min_w=125, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(b_dst1)

    b_dst2, _, _ = textbox(910, 280, "RabbitMQ ERP\nQueue: orders.sync\nAMQP Confirm", size=10.5, bold=True, min_w=125, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(b_dst2)

    # Стрілки
    f.append(arrow(655, 200, 675, 200, color=NEG, sw=1.5))
    f.append(arrow(825, 185, 845, 135, color=FIELD, sw=1.4))
    f.append(arrow(825, 215, 845, 265, color=FIELD, sw=1.4))

    f.append(text(750, 395, "✓ Брокери залишаються ізольованими; міст гарантує доставку крізь WAN", size=10, color=FIELD, italic=True))

    render(out("isolated-brokers-vs-bridge.svg"), W, H, *f,
           title="Ізольовані брокери проти моста повідомлень")


# ── 2. dual-ack-and-failure: протокол подвійного підтвердження та крайові випадки
def fig_dual_ack_and_failure():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, 980, 460, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Протокол подвійного підтвердження (Dual Acknowledgment) та вікно дублювання", size=14, bold=True))

    # Три вертикальні доріжки компонентів
    # 1. Source Broker (170)
    # 2. Message Bridge (500)
    # 3. Target Broker (830)

    f.append(line(170, 70, 170, 420, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(500, 70, 500, 420, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(830, 70, 830, 420, color=MUTED, sw=1.5, dash="4,4"))

    b_s, _, _ = textbox(170, 70, "Брокер-джерело\n(Source Broker)", size=11, bold=True, min_w=140, pad=5, fill=GRAY_F, stroke=LINE)
    f.append(b_s)

    b_b, _, _ = textbox(500, 70, "Міст повідомлень\n(Message Bridge)", size=11, bold=True, min_w=140, pad=5, fill=BLUE_F, stroke=NEG)
    f.append(b_b)

    b_t, _, _ = textbox(830, 70, "Цільовий брокер\n(Target Broker)", size=11, bold=True, min_w=140, pad=5, fill=GREEN_F, stroke=FIELD)
    f.append(b_t)

    # Кроки протоколу
    # Крок 1: Отримання повідомлення
    y1 = 130
    f.append(arrow(170, y1, 495, y1, color=LINE, sw=1.4))
    f.append(text(335, y1 - 10, "1. Fetch / Poll (msg_id: 101, payload)", size=10, bold=True))
    f.append(text(335, y1 + 14, "Повідомлення переходить у стан in-flight (unacked)", size=9, color=MUTED, italic=True))

    # Крок 2: Трансляція та відправка на ціль
    y2 = 200
    f.append(arrow(505, y2, 825, y2, color=FIELD, sw=1.4))
    f.append(text(665, y2 - 10, "2. Forward / Produce (msg_id: 101, trace_headers)", size=10, bold=True, color=FIELD))
    f.append(text(665, y2 + 14, "Адаптація конверта, додавання X-Bridge-Origin-ID", size=9, color=MUTED, italic=True))

    # Крок 3: Підтвердження від цільового брокера
    y3 = 270
    f.append(arrow(825, y3, 505, y3, color=FIELD, sw=1.4))
    f.append(text(665, y3 - 10, "3. Target Ack / Commit Confirm (OK)", size=10, bold=True, color=FIELD))
    f.append(text(665, y3 + 14, "Ціль записала повідомлення на диск / у лог", size=9, color=MUTED, italic=True))

    # Вікно вразливості: крах моста
    f.append(rect(420, 310, 160, 44, fill=RED_F, stroke=POS, sw=1.2, rx=4))
    f.append(text(500, 325, "КРАХ МОСТА (Crash)", size=10, bold=True, color=POS))
    f.append(text(500, 343, "Офсет на джерелі не зафіксовано!", size=9.5, color=POS))

    # Крок 4: Фіксація на джерелі (якщо немає краху)
    y4 = 390
    f.append(arrow(495, y4, 175, y4, color=NEG, sw=1.4))
    f.append(text(335, y4 - 10, "4. Source Ack / Commit Offset", size=10, bold=True, color=NEG))
    f.append(text(335, y4 + 14, "Після краху: джерело віддасть msg 101 повторно (At-Least-Once)", size=9.5, color=POS, italic=True))

    render(out("dual-ack-and-failure.svg"), W, H, *f,
           title="Протокол подвійного підтвердження та семантика доставки")


# ── 3. bridge-topologies-and-loops: топології та запобігання нескінченним петлям
def fig_bridge_topologies_and_loops():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, 980, 460, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Топології мостів повідомлень та виявлення циклічних петель", size=14, bold=True))

    # Блок А: Зірка / Edge-to-Hub (зліва зверху)
    f.append(rect(25, 60, 455, 185, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(252, 80, "А. Зіркова топологія (Edge-to-Hub Aggregation)", size=11, bold=True))

    b_e1, _, _ = textbox(85, 125, "Edge Factory A\n(MQTT)", size=9.5, min_w=95, pad=4, fill=FILL, stroke=LINE)
    b_e2, _, _ = textbox(85, 185, "Edge Factory B\n(MQTT)", size=9.5, min_w=95, pad=4, fill=FILL, stroke=LINE)
    f.append(b_e1); f.append(b_e2)

    b_hub, _, _ = textbox(252, 155, "Хмарний Hub\n(Kafka Cluster)\norders.aggregated", size=10, bold=True, min_w=115, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(b_hub)

    b_c1, _, _ = textbox(410, 155, "Data Warehouse\n/ Analytics", size=9.5, min_w=95, pad=4, fill=GREEN_F, stroke=FIELD)
    f.append(b_c1)

    f.append(arrow(135, 125, 190, 145, color=NEG, sw=1.2))
    f.append(arrow(135, 185, 190, 165, color=NEG, sw=1.2))
    f.append(arrow(315, 155, 360, 155, color=FIELD, sw=1.2))
    f.append(text(252, 230, "Односпрямоване зведення: без ризику циклів", size=9.5, color=FIELD, italic=True))

    # Блок Б: Ланцюгова ретрансляція (Store-and-Forward Chain) (зліва знизу)
    f.append(rect(25, 260, 455, 195, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(252, 280, "Б. Ланцюг збереження та пересилки (Store-and-Forward)", size=11, bold=True))

    b_ch1, _, _ = textbox(85, 345, "Edge Node\n(Local DB)", size=9.5, min_w=90, pad=4, fill=FILL, stroke=LINE)
    b_ch2, _, _ = textbox(240, 345, "Regional Bridge\n(Disk Spool)", size=9.5, min_w=105, pad=5, fill=WARN_F, stroke=LINE)
    b_ch3, _, _ = textbox(405, 345, "Central DC\n(Active Log)", size=9.5, min_w=95, pad=4, fill=GREEN_F, stroke=FIELD)
    f.append(b_ch1); f.append(b_ch2); f.append(b_ch3)

    f.append(arrow(135, 345, 182, 345, color=NEG, sw=1.2))
    f.append(arrow(298, 345, 352, 345, color=FIELD, sw=1.2))
    f.append(text(252, 415, "Ізоляція обривів WAN через проміжні буфери", size=9.5, color=FIELD, italic=True))
    f.append(text(252, 435, "Регіональний вузол накопичує стан при відсутності зв'язку", size=9.5, color=MUTED))

    # Блок В: Двоспрямований міст та запобігання петлям (справа)
    f.append(rect(500, 60, 475, 395, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(737, 80, "В. Двоспрямований міст (Active-Active) і детекція петель", size=11.5, bold=True, color=POS))

    b_clA, _, _ = textbox(590, 175, "Кластер A (EU)\nTopic: orders\nCluster-ID: 0x01", size=10, bold=True, min_w=120, pad=6, fill=BLUE_F, stroke=NEG)
    b_clB, _, _ = textbox(885, 175, "Кластер B (US)\nTopic: orders\nCluster-ID: 0x02", size=10, bold=True, min_w=120, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(b_clA); f.append(b_clB)

    # Верхній міст A -> B
    f.append(arrow(655, 155, 820, 155, color=FIELD, sw=1.4))
    f.append(text(737, 140, "Міст 1 (A → B): додає X-Bridge-Path: [0x01]", size=9.5, color=FIELD, bold=True))

    # Нижній міст B -> A
    f.append(arrow(820, 195, 655, 195, color=POS, sw=1.4))
    f.append(text(737, 215, "Міст 2 (B → A): перевіряє X-Bridge-Path", size=9.5, color=POS, bold=True))

    # Панель правила розриву циклу
    f.append(rect(525, 255, 425, 180, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    f.append(text(737, 275, "Алгоритм фільтрації луни (Loop Detection):", size=10.5, bold=True))
    f.append(text(737, 305, "1. Міст зчитує заголовок X-Bridge-Path з вхідного пакета.", size=9.5))
    f.append(text(737, 330, "2. Якщо власний Cluster-ID вже є у списку hops → ВІДКИДАННЯ.", size=9.5, color="#c0392b", bold=True))
    f.append(text(737, 355, "3. Якщо немає → додати поточний ID і переслати далі.", size=9.5, color=FIELD))
    f.append(text(737, 380, "4. Альтернатива: префіксовані топіки (eu.orders ↔ us.orders).", size=9.5, color=MUTED))
    f.append(text(737, 415, "✓ Запобігає нескінченному лавиноподібному шторму повідомлень", size=9.5, color=FIELD, italic=True))

    render(out("bridge-topologies-and-loops.svg"), W, H, *f,
           title="Топології мостів повідомлень та запобігання петлям")


if __name__ == '__main__':
    fig_isolated_brokers_vs_bridge()
    fig_dual_ack_and_failure()
    fig_bridge_topologies_and_loops()
    print("Фігури успішно згенеровано у ./img/")
