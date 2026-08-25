# -*- coding: utf-8 -*-
"""Фігури теми «Міст шин повідомлень». Вивід — ./img/*.svg"""
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

# ── 1. direct-vs-bridge: пряме зчеплення систем проти мосту шин ─────────────
def fig_direct_vs_bridge():
    W, H = 1000, 440
    f = []

    # Ліва панель: Пряме спагеті-підключення
    f.append(rect(15, 15, 470, 405, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 42, "Пряме з'єднання гетерогенних шин", size=13, bold=True, color=POS))

    left_sources = [
        (100, 110, "MQTT Брокер\n(Edge IoT Завод)"),
        (100, 210, "RabbitMQ\n(AMQP Склад)"),
        (100, 310, "ActiveMQ\n(JMS Legacy)")
    ]
    for x, y, lbl in left_sources:
        b, _, _ = textbox(x, y, lbl, size=11, bold=True, min_w=125, pad=6, fill=FILL, stroke=LINE)
        f.append(b)

    left_dests = [
        (385, 110, "Kafka Cluster\n(Хмарна аналітика)"),
        (385, 210, "AWS SQS / SNS\n(Білінг & Чекаут)"),
        (385, 310, "Redis Streams\n(Realtime UI)")
    ]
    for x, y, lbl in left_dests:
        b, _, _ = textbox(x, y, lbl, size=11, min_w=135, pad=6, fill=RED_F, stroke=POS)
        f.append(b)

    # Перехресні лінії спагеті
    for _, sy, _ in left_sources:
        for _, dy, _ in left_dests:
            f.append(line(165, sy, 310, dy, color="#e74c3c", sw=1, dash="3,3"))

    f.append(text(250, 400, "✗ N × M адаптерів, несумісні протоколи, втрата повідомлень при збоях WAN", size=10, color=POS, italic=True))

    # Права панель: Міст шин повідомлень
    f.append(rect(515, 15, 470, 405, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 42, "Міст шин повідомлень (Message Bus Bridge)", size=13, bold=True, color=FIELD))

    right_sources = [
        (595, 110, "MQTT Брокер\n(Edge IoT Завод)"),
        (595, 210, "RabbitMQ\n(AMQP Склад)"),
        (595, 310, "ActiveMQ\n(JMS Legacy)")
    ]
    for x, y, lbl in right_sources:
        b, _, _ = textbox(x, y, lbl, size=11, bold=True, min_w=120, pad=6, fill=FILL, stroke=LINE)
        f.append(b)

    # Центральний блок Bridge
    bridge_box, _, _ = textbox(750, 210, "МІСТ ШИН (BRIDGE)\n\n• Адаптація протоколів\n• Трансляція заголовків\n• Store-and-Forward WAL\n• Протитиск і Dual-Ack",
                               size=10.5, bold=True, min_w=135, pad=8, fill=BLUE_F, stroke=NEG, sw=1.8)
    f.append(bridge_box)

    right_dests = [
        (905, 110, "Kafka Cluster\n(Хмарна аналітика)"),
        (905, 210, "AWS SQS / SNS\n(Білінг & Чекаут)"),
        (905, 310, "Redis Streams\n(Realtime UI)")
    ]
    for x, y, lbl in right_dests:
        b, _, _ = textbox(905, y, lbl, size=11, min_w=130, pad=6, fill=GREEN_F, stroke=FIELD)
        f.append(b)

    # Стрілки до мосту і від мосту
    for _, sy, _ in right_sources:
        f.append(arrow(660, sy, 680, 210, color=NEG, sw=1.4))

    for _, dy, _ in right_dests:
        f.append(arrow(820, 210, 835, dy, color=FIELD, sw=1.3))

    f.append(text(750, 400, "✓ Повне розчеплення протоколів, єдиний буфер стійкості та контроль потоку", size=10, color=FIELD, italic=True))

    render(out("direct-vs-bridge.svg"), W, H, *f,
           title="Пряме з'єднання гетерогенних шин проти мосту повідомлень")


# ── 2. bridge-architecture-pipeline: внутрішній конвеєр мосту ───────────────
def fig_bridge_architecture_pipeline():
    W, H = 1000, 500
    f = []

    f.append(rect(10, 10, 980, 480, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Архітектурний конвеєр мосту шин повідомлень (Store-and-Forward Pipeline)", size=14, bold=True))

    # Стадії конвеєра зліва направо
    stages = [
        (110, 125, "1. Ingress Consumer\n(Вхідний адаптер)", "Зчитування з шини А\n(MQTT / AMQP / Kafka)\nКерування сесією"),
        (300, 125, "2. Protocol Decoder\n& Schema Check", "Десеріалізація payload\nВалідація схеми\nВиділення метаданих"),
        (500, 125, "3. Transform & Routing\n& Loop Guard", "Мапування заголовків\nПеревірка трасування\n(X-Bridge-Hops)"),
        (700, 125, "4. Resilient Buffer\n(Spill / Ring / WAL)", "Локальний буфер\nЗахист від сплесків\nПротитиск (Flow Control)"),
        (890, 125, "5. Egress Producer\n(Вихідний адаптер)", "Формування пакетів\nПублікація в шину Б\nОчікування Egress-ACK")
    ]

    for x, y, title_lbl, desc_lbl in stages:
        b1, _, _ = textbox(x, y, title_lbl, size=11, bold=True, min_w=145, pad=6, fill=BLUE_F, stroke=NEG, sw=1.4)
        f.append(b1)
        b2, _, _ = textbox(x, y + 80, desc_lbl, size=9.5, min_w=145, pad=5, fill=FILL, stroke=LINE)
        f.append(b2)
        f.append(line(x, y + 25, x, y + 55, color=MUTED, sw=1))

    # Стрілки між стадіями
    stage_xs = [110, 300, 500, 700, 890]
    for i in range(len(stage_xs) - 1):
        f.append(arrow(stage_xs[i] + 75, 125, stage_xs[i+1] - 75, 125, color=NEG, sw=1.6))

    # Нижня панель: Координація подвійного підтвердження (Dual-Ack Coordinator)
    f.append(rect(60, 310, 880, 150, fill=PURPLE_F, stroke="#8e44ad", sw=1.4, rx=6))
    f.append(text(500, 335, "Координатор подвійного підтвердження (Dual-Ack & Commit Coordinator)", size=12, bold=True, color="#6c3483"))

    f.append(text(200, 375, "1. Ingress Read (Auto-Ack = False)", size=10.5, bold=True))
    f.append(text(200, 400, "Отримано повідомлення, ACK відкладено", size=9.5, color=MUTED))
    f.append(text(200, 420, "Пакет зафіксовано в черзі мосту", size=9, color=MUTED))

    f.append(arrow(340, 385, 410, 385, color="#8e44ad", sw=1.4))

    f.append(text(500, 375, "2. Egress Publish & Wait ACK", size=10.5, bold=True))
    f.append(text(500, 400, "Підтвердження запису від шини Б", size=9.5, color=MUTED))
    f.append(text(500, 420, "Очікування мережевого квитка", size=9, color=MUTED))

    f.append(arrow(590, 385, 660, 385, color="#8e44ad", sw=1.4))

    f.append(text(790, 375, "3. Ingress Commit ACK / Offset", size=10.5, bold=True, color=FIELD))
    f.append(text(790, 400, "Безпечне закриття циклу доставки", size=9.5, color=FIELD))
    f.append(text(790, 420, "Зсув офсету або AMQP basic.ack", size=9, color=FIELD))

    # Стрілки координації без перетинів тексту
    f.append(arrow(110, 245, 110, 305, color="#8e44ad", sw=1.3))
    f.append(arrow(890, 245, 890, 305, color="#8e44ad", sw=1.3))

    render(out("bridge-architecture-pipeline.svg"), W, H, *f,
           title="Архітектурний конвеєр мосту шин повідомлень")


# ── 3. loop-prevention-topologies: запобігання зацикленню ───────────────────
def fig_loop_prevention_topologies():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, 980, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Запобігання зацикленню повідомлень у двонаправлених мостах", size=14, bold=True))

    # Верхній блок: Проблема шторму зациклення (Loop Storm Hazard)
    f.append(rect(30, 65, 940, 150, fill=RED_F, stroke=POS, sw=1.2, rx=6))
    f.append(text(500, 90, "Небезпека луни: нескінченний пінг-понг між шинами без контролю походження", size=12, bold=True, color=POS))

    b_a, _, _ = textbox(160, 145, "Шина А\n(Франкфурт)", size=11, bold=True, min_w=120, pad=5, fill=FILL, stroke=LINE)
    f.append(b_a)

    b_b1, _, _ = textbox(500, 115, "Міст А → Б\n(Forward A)", size=10, bold=True, min_w=110, pad=4, fill=BLUE_F, stroke=NEG)
    f.append(b_b1)

    b_b2, _, _ = textbox(500, 175, "Міст Б → А\n(Forward B)", size=10, bold=True, min_w=110, pad=4, fill=BLUE_F, stroke=NEG)
    f.append(b_b2)

    b_b, _, _ = textbox(840, 145, "Шина Б\n(Вірджинія)", size=11, bold=True, min_w=120, pad=5, fill=FILL, stroke=LINE)
    f.append(b_b)

    f.append(arrow(225, 130, 440, 115, color=POS, sw=1.5))
    f.append(arrow(560, 115, 775, 130, color=POS, sw=1.5))
    f.append(arrow(775, 160, 560, 175, color=POS, sw=1.5))
    f.append(arrow(440, 175, 225, 160, color=POS, sw=1.5))

    f.append(text(500, 202, "Повідомлення M реплікується в Б → Б повертає M в А → лавиноподібний шторм повідомлень", size=9.5, color=POS, bold=True))

    # Нижні 3 блоки: Три стратегії захисту
    strategies = [
        (180, 245, "1. Заголовки трасування\n(Trace & Hop Limit)",
         "Додавання X-Forwarded-By: [A, B].\nЯкщо ідентифікатор поточної шини\nвже є в списку — скидання (Drop).\nЛіміт стрибків max_hops ≤ 3.",
         BLUE_F, NEG),
        (500, 245, "2. Розділення просторів\n(Split Namespaces)",
         "Шина А публікує в local.orders.\nМіст пересилає в remote.a.orders.\nМіст Б слухає виключно local.*,\nігноруючи репліковані теми remote.*.",
         GREEN_F, FIELD),
        (820, 245, "3. Вікно дедуплікації\n(Deduplication Cache)",
         "Збереження message_id у ковзному\nфільтрі Блума або LRU-кеші.\nПовторне надходження дубліката\nвідсікається до публікації в шину.",
         PURPLE_F, "#8e44ad")
    ]

    for x, y, title_lbl, desc_lbl, bg_c, str_c in strategies:
        f.append(rect(x - 145, y, 290, 180, fill=bg_c, stroke=str_c, sw=1.2, rx=6))
        f.append(text(x, y + 25, title_lbl.split("\n")[0], size=11, bold=True, color=str_c))
        f.append(text(x, y + 42, title_lbl.split("\n")[1], size=10, bold=True, color=str_c))
        lines = desc_lbl.split("\n")
        for idx, line_text in enumerate(lines):
            f.append(text(x, y + 75 + idx * 20, line_text, size=9.5, color=INK))

    render(out("loop-prevention-topologies.svg"), W, H, *f,
           title="Запобігання зацикленню повідомлень у двонаправлених мостах")


# ── 4. dual-ack-and-failure-modes: збої Dual-Ack та дедуплікація ────────────
def fig_dual_ack_and_failure_modes():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, 980, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Матриця збоїв Dual-Ack: походження дублікатів та їх ізоляція", size=14, bold=True))

    # 3 вертикальні колони життєвого циклу
    cols = [
        (180, "Крок 1: Зчитування", 80),
        (500, "Крок 2: Egress-публікація", 80),
        (820, "Крок 3: Ingress-коміт", 80)
    ]

    for x, title_lbl, y in cols:
        f.append(text(x, y, title_lbl, size=12, bold=True, color=INK))
        f.append(line(x, y + 15, x, 400, color=MUTED, sw=1, dash="4,4"))

    # Сценарій нормальної доставки
    f.append(rect(40, 120, 920, 75, fill=GREEN_F, stroke=FIELD, sw=1, rx=6))
    f.append(text(90, 145, "Норма (Success)", size=11, bold=True, color=FIELD))
    f.append(text(180, 165, "Fetch msg #42", size=9.5))
    f.append(arrow(230, 165, 450, 165, color=FIELD, sw=1.3))
    f.append(text(500, 165, "Publish #42 → Dest ACK ok", size=9.5))
    f.append(arrow(580, 165, 770, 165, color=FIELD, sw=1.3))
    f.append(text(820, 165, "Commit Source #42 ✓", size=9.5, bold=True, color=FIELD))

    # Сценарій збою до Egress
    f.append(rect(40, 210, 920, 85, fill=BLUE_F, stroke=NEG, sw=1, rx=6))
    f.append(text(90, 235, "Краш до Egress", size=11, bold=True, color=NEG))
    f.append(text(180, 255, "Fetch msg #43", size=9.5))
    f.append(text(340, 255, "💥 КРАШ МОСТУ", size=10, bold=True, color=POS))
    f.append(text(500, 255, "(У шину Б нічого не пішло)", size=9.5, color=MUTED))
    f.append(text(820, 255, "Source перевіддає #43 іншому воркеру (Zero Loss) ✓", size=9.5, color=FIELD))

    # Сценарій краху між Egress ACK та Ingress Commit (Джерело дублікатів)
    f.append(rect(40, 310, 920, 115, fill=WARN_F, stroke="#d35400", sw=1.2, rx=6))
    f.append(text(90, 335, "Крах після Egress", size=11, bold=True, color="#d35400"))
    f.append(text(180, 355, "Fetch msg #44", size=9.5))
    f.append(arrow(230, 355, 430, 355, color="#d35400", sw=1.3))
    f.append(text(500, 355, "Publish #44 → Dest ACK ok", size=9.5))
    f.append(text(650, 355, "💥 КРАШ ДО КОМІТУ", size=10, bold=True, color=POS))
    f.append(text(820, 355, "❌ Ingress ACK не відправлено", size=9.5, color=POS, bold=True))
    f.append(text(500, 395, "Результат: після рестарту міст знову прочитає #44 і надішле в Б. At-Least-Once вимагає ідемпотентності на боці Б!", size=10, color="#b9770e", bold=True))

    render(out("dual-ack-and-failure-modes.svg"), W, H, *f,
           title="Матриця збоїв Dual-Ack: походження дублікатів та їх ізоляція")


if __name__ == "__main__":
    fig_direct_vs_bridge()
    fig_bridge_architecture_pipeline()
    fig_loop_prevention_topologies()
    fig_dual_ack_and_failure_modes()
    print("Всі фігури згенеровано успішно.")
