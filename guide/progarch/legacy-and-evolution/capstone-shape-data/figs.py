# -*- coding: utf-8 -*-
"""Фігури до кроку «Капстон, крок 2: форма застосунку та топологія даних»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_c4_containers_bounded_contexts():
    """C4 Container View та межі Bounded Contexts платформи OmniTrade Global."""
    W, H = 1020, 640
    frags = []

    frags.append(text(W / 2, 42,
                      "C4 Контейнери та межі контекстів (Bounded Contexts) OmniTrade Global",
                      size=14, bold=True, color=FIELD))
    frags.append(text(W / 2, 68,
                      "Запити через API Gateway розподіляються між ізольованими контекстами зі власними БД",
                      size=12, color=MUTED))

    # Клієнти (згори)
    b_cli, w_cli, h_cli = textbox(510, 120, "Клієнтські застосунки\n(Mobile App / Web SPA / B2B API Clients)",
                                  size=13, fill="#eaf0fd", stroke=LINE, sw=1.6)

    # API Gateway
    b_gw, w_gw, h_gw = textbox(510, 210, "API Gateway (Envoy / Kong)\nАвтентифікація · Rate Limiting · Маршрутизація",
                                size=13, fill="#eef2f6", stroke=LINE, sw=1.8)

    # Контексти (сервіси + бази даних)
    cy = 360
    # 1. Order Context
    b_ord, w_ord, h_ord = textbox(210, cy, "Order Context\n(Order Service)\nPostgreSQL (Orders)",
                                  size=12, fill="#eafaf0", stroke=FIELD, sw=1.8)
    # 2. Ledger & Wallet Context
    b_led, w_led, h_led = textbox(510, cy, "Ledger & Wallet Context\n(Ledger Service)\nCockroachDB (Acid Ledger)",
                                  size=12, fill="#eafaf0", stroke=FIELD, sw=2.2)
    # 3. Inventory Context
    b_inv, w_inv, h_inv = textbox(810, cy, "Inventory Context\n(Inventory Service)\nPostgreSQL + Redis Lock",
                                  size=12, fill="#eafaf0", stroke=FIELD, sw=1.8)

    # 4. Search & Catalog (знизу ліворуч)
    b_cat, w_cat, h_cat = textbox(310, 520, "Search & Catalog Context\n(Search Service)\nOpenSearch + Redis Read-Model",
                                  size=12, fill="#fef8ec", stroke=LINE, sw=1.6)

    # 5. Async Messaging Backbone (знизу праворуч)
    b_msg, w_msg, h_msg = textbox(710, 520, "Messaging Backbone\nApache Kafka Cluster\n(Event Stream & Outbox Topics)",
                                  size=12, fill="#f2f2f2", stroke=MUTED, sw=1.8)

    # Стрілки запитів від клієнтів до Gateway
    frags.append(arrow(510, 120 + h_cli / 2, 510, 210 - h_gw / 2 - 4, color=NEG, sw=2.0))

    # Стрілки від Gateway до 3 основних контекстів
    frags.append(arrow(430, 210 + h_gw / 2, 210, cy - h_ord / 2 - 4, color=FIELD, sw=2.0))
    frags.append(arrow(510, 210 + h_gw / 2, 510, cy - h_led / 2 - 4, color=FIELD, sw=2.0))
    frags.append(arrow(590, 210 + h_gw / 2, 810, cy - h_inv / 2 - 4, color=FIELD, sw=2.0))

    # Події між контекстами й Kafka
    frags.append(arrow(210, cy + h_ord / 2, 630, 520 - h_msg / 2 + 10, color=POS, sw=1.8))
    frags.append(arrow(510, cy + h_led / 2, 710, 520 - h_msg / 2 - 4, color=POS, sw=1.8))
    frags.append(arrow(810, cy + h_inv / 2, 780, 520 - h_msg / 2 + 10, color=POS, sw=1.8))

    # Події від Kafka до Search Context
    frags.append(arrow(610, 520, 430, 520, color=POS, sw=1.8))

    frags.append(text(W / 2, 615,
                      "Кожен контекст повністю володіє своїм сховищем даних; прямі SQL-запити між контекстами заборонені",
                      size=12, color=MUTED))

    frags += [b_cli, b_gw, b_ord, b_led, b_inv, b_cat, b_msg]
    render(os.path.join(IMG, "c4-containers-bounded-contexts.svg"), W, H, *frags,
           title="C4 Контейнери та межі Bounded Contexts OmniTrade Global")


def fig_data_topology_consistency_boundaries():
    """Топологія даних та межі консистентності (Strong ACID vs Eventual Consistency)."""
    W, H = 1000, 560
    frags = []

    frags.append(text(W / 2, 38,
                      "Топологія даних: Межі суворої (ACID) та асинхронної (Eventual) консистентності",
                      size=14, bold=True, color=FIELD))

    # Зона 1: Строга консистентність (Strong Consistency / CP / PC)
    frags.append(rect(60, 85, 410, 390, fill="#eafaf0", stroke=FIELD, sw=2.0))
    frags.append(text(265, 115, "ЗОНА СТРОГОЇ КОНСИСТЕНТНОСТІ (ACID)", size=13, bold=True, color=FIELD))
    frags.append(text(265, 138, "Гарантія відсутності подвійних списань та втрат коштів", size=11, color=MUTED))

    b_led_db, w_l, h_l = textbox(265, 210, "Ledger & Double-Entry DB\nMulti-Region CockroachDB / Spanner\nACID / Serializable Isolation",
                                 size=12, fill="#ffffff", stroke=FIELD, sw=1.6)
    b_wal_db, w_w, h_w = textbox(265, 330, "Wallet Balance & Reserves\nStrict Row Locking / Pessimistic\nZero Overdraft Invariant",
                                 size=12, fill="#ffffff", stroke=FIELD, sw=1.6)
    b_tx_out, w_to, h_to = textbox(265, 430, "Transactional Outbox Table\nАтомарний запис події у тій же БД",
                                   size=12, fill="#eef2f6", stroke=LINE, sw=1.4)

    # Зона 2: Послідовна / Eventual консистентність (Eventual Consistency / AP / EL)
    frags.append(rect(530, 85, 410, 390, fill="#fef8ec", stroke=LINE, sw=2.0))
    frags.append(text(735, 115, "ЗОНА EVENTUAL КОНСИСТЕНТНОСТІ (SAGA)", size=13, bold=True, color=NEG))
    frags.append(text(735, 138, "Оптимізація під високу пропускну здатність та доступність", size=11, color=MUTED))

    b_ev_bus, w_eb, h_eb = textbox(735, 210, "Event Bus (Kafka Cluster)\nPartitioned Topic / At-Least-Once",
                                   size=12, fill="#ffffff", stroke=LINE, sw=1.6)
    b_search, w_se, h_se = textbox(735, 330, "Catalog & Search Read-Models\nOpenSearch Index / Redis Cache\nEventual Lag < 500ms",
                                   size=12, fill="#ffffff", stroke=LINE, sw=1.6)
    b_analytics, w_an, h_an = textbox(735, 430, "Analytical Data Lake\nClickHouse / ScyllaDB\nAppend-Only Stream",
                                      size=12, fill="#ffffff", stroke=LINE, sw=1.6)

    # Межа / Outbox Publisher
    frags.append(arrow(380, 430, 630, 210, color=POS, sw=2.4))
    frags.append(text(500, 305, "Outbox Relayer\n(Асинхронний мост)", size=11, color=POS, bold=True))

    frags.append(text(W / 2, 520,
                      "Фінансове ядро вимагає строгої ACID-консистентності; вітрина й аналітика працюють через асинхронні події",
                      size=12, color=MUTED))

    frags += [b_led_db, b_wal_db, b_tx_out, b_ev_bus, b_search, b_analytics]
    render(os.path.join(IMG, "data-topology-consistency-boundaries.svg"), W, H, *frags,
           title="Топологія даних та межі консистентності")


def fig_outbox_saga_topology():
    """Транзакційний Outbox та топологія саги під час оформлення замовлення."""
    W, H = 980, 540
    frags = []

    frags.append(text(W / 2, 38,
                      "Взаємодія Transactional Outbox та Saga Orchestrator під час чекауту",
                      size=14, bold=True, color=FIELD))

    # Крок 1: Клієнт створює замовлення
    b1, w1, h1 = textbox(160, 120, "1. Клієнт\nPOST /orders/checkout", size=12, fill="#eaf0fd")

    # Крок 2: Order Service локальна транзакція
    b2, w2, h2 = textbox(490, 120, "2. Order Service\nBEGIN TX:\n - Save Order (PENDING)\n - Insert Outbox Event\nCOMMIT TX",
                         size=12, fill="#eafaf0", stroke=FIELD, sw=2.0)

    # Крок 3: Outbox Relayer
    b3, w3, h3 = textbox(820, 120, "3. Outbox Relayer\nPoll / CDC -> Kafka\n'OrderCreated'", size=12, fill="#eef2f6")

    # Крок 4: Saga Orchestration / Handlers
    y4 = 340
    b4_a, w4a, h4a = textbox(240, y4, "4a. Wallet Service\nLock Funds / Reserve\nPublish 'FundsReserved'", size=12, fill="#ffffff", stroke=LINE, sw=1.6)
    b4_b, w4b, h4b = textbox(740, y4, "4b. Inventory Service\nReserve Stock items\nPublish 'StockReserved'", size=12, fill="#ffffff", stroke=LINE, sw=1.6)

    # Крок 5: Завершення замовлення
    b5, w5, h5 = textbox(490, 460, "5. Order Service (Saga Complete)\nUpdate Order -> CONFIRMED\n(або Компенсація при помилці)", size=12, fill="#eafaf0", stroke=FIELD, sw=2.0)

    # Стрілки
    frags.append(arrow(160 + w1 / 2, 120, 490 - w2 / 2 - 4, 120, color=FIELD, sw=2.0))
    frags.append(arrow(490 + w2 / 2, 120, 820 - w3 / 2 - 4, 120, color=FIELD, sw=2.0))

    frags.append(arrow(820, 120 + h3 / 2, 240, y4 - h4a / 2 - 4, color=POS, sw=1.8))
    frags.append(arrow(820, 120 + h3 / 2, 740, y4 - h4b / 2 - 4, color=POS, sw=1.8))

    frags.append(arrow(240, y4 + h4a / 2, 490 - 40, 460 - h5 / 2 - 4, color=FIELD, sw=1.8))
    frags.append(arrow(740, y4 + h4b / 2, 490 + 40, 460 - h5 / 2 - 4, color=FIELD, sw=1.8))

    frags.append(text(W / 2, 518,
                      "Атомарна локальна транзакція гарантує, що подія Outbox вийде лише після успішного збереження замовлення",
                      size=12, color=MUTED))

    frags += [b1, b2, b3, b4_a, b4_b, b5]
    render(os.path.join(IMG, "outbox-saga-topology.svg"), W, H, *frags,
           title="Транзакційний Outbox та топологія саги")


if __name__ == "__main__":
    fig_c4_containers_bounded_contexts()
    fig_data_topology_consistency_boundaries()
    fig_outbox_saga_topology()
    print("OK: c4-containers-bounded-contexts.svg, data-topology-consistency-boundaries.svg, outbox-saga-topology.svg")
