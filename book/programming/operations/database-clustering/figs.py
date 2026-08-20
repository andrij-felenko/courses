#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Кластеризація баз даних»."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_topologies():
    """Порівняння трьох ключових архітектурних топологій кластеризації баз даних."""
    w, h = 960, 480
    c = []

    # Заголовок фігури
    c.append(text(w / 2, 28, "Архітектурні моделі кластеризації баз даних", size=18, bold=True))
    c.append(text(w / 2, 50, "Організація стану, вузлів та потоків реплікації", size=13, color=MUTED))

    # Три панелі для трьох топологій
    panel_w = 290
    panel_h = 390
    y_top = 70

    # 1. Primary-Standby (Physical Streaming)
    x1 = 20
    c.append(rect(x1, y_top, panel_w, panel_h, fill="#fafbfc", stroke=LINE, rx=8))
    c.append(rect(x1, y_top, panel_w, 36, fill="#e8f0fe", stroke=LINE, rx=8))
    c.append(text(x1 + panel_w / 2, y_top + 23, "1. Primary-Standby (Active-Passive)", size=13, bold=True, color="#1a56db"))

    # Primary Node
    b1, _, _ = textbox(x1 + panel_w / 2, y_top + 80, "Лідер (Primary Node)\nЧитання + Запис (RW)\nЛокальний NVMe + WAL", size=12, fill="#e1f5fe", stroke="#0288d1", min_w=250)
    c.append(b1)

    # WAL replication arrow
    c.append(arrow(x1 + panel_w / 2, y_top + 120, x1 + panel_w / 2, y_top + 165, color=FIELD, sw=2.2))
    c.append(text(x1 + panel_w / 2 + 10, y_top + 145, "Потік WAL / Binlog", size=11, color=FIELD, anchor="start", bold=True))

    # Standby Node
    b2, _, _ = textbox(x1 + panel_w / 2, y_top + 205, "Репліка (Standby Node)\nТільки читання (RO)\nВідтворення WAL (Replay)", size=12, fill="#f3e5f5", stroke="#7b1fa2", min_w=250)
    c.append(b2)

    # Властивості
    c.append(line(x1 + 15, y_top + 260, x1 + panel_w - 15, y_top + 260, color="#d1d5db", dash="3,3"))
    c.append(text(x1 + 20, y_top + 285, "• Єдине джерело запису (SPOW)", size=11, anchor="start"))
    c.append(text(x1 + 20, y_top + 310, "• Синхронна або асинхронна реплікація", size=11, anchor="start"))
    c.append(text(x1 + 20, y_top + 335, "• Промоція репліки при відмові лідера", size=11, anchor="start"))
    c.append(text(x1 + 20, y_top + 360, "• Приклади: PostgreSQL (Patroni), MySQL", size=11, anchor="start", color=MUTED))

    # 2. Multi-Primary (Certification Replication)
    x2 = 335
    c.append(rect(x2, y_top, panel_w, panel_h, fill="#fafbfc", stroke=LINE, rx=8))
    c.append(rect(x2, y_top, panel_w, 36, fill="#fef3c7", stroke=LINE, rx=8))
    c.append(text(x2 + panel_w / 2, y_top + 23, "2. Multi-Primary (All-Active)", size=13, bold=True, color="#b45309"))

    # Multi nodes in ring / mesh
    b3, _, _ = textbox(x2 + 75, y_top + 80, "Вузол A (RW)\nБД + Буфер", size=11, fill="#fef9c3", stroke="#ca8a04", min_w=120)
    b4, _, _ = textbox(x2 + panel_w - 75, y_top + 80, "Вузол B (RW)\nБД + Буфер", size=11, fill="#fef9c3", stroke="#ca8a04", min_w=120)
    b5, _, _ = textbox(x2 + panel_w / 2, y_top + 185, "Вузол C (RW)\nБД + Сертифікація", size=11, fill="#fef9c3", stroke="#ca8a04", min_w=180)
    c.extend([b3, b4, b5])

    # Interconnect lines
    c.append(line(x2 + 130, y_top + 80, x2 + panel_w - 130, y_top + 80, color=LINE, sw=1.5, dash="4,4"))
    c.append(line(x2 + 80, y_top + 115, x2 + panel_w / 2 - 40, y_top + 160, color=LINE, sw=1.5, dash="4,4"))
    c.append(line(x2 + panel_w - 80, y_top + 115, x2 + panel_w / 2 + 40, y_top + 160, color=LINE, sw=1.5, dash="4,4"))
    c.append(text(x2 + panel_w / 2, y_top + 130, "Тотальний порядок подій", size=10, color=POS, bold=True))

    # Властивості
    c.append(line(x2 + 15, y_top + 260, x2 + panel_w - 15, y_top + 260, color="#d1d5db", dash="3,3"))
    c.append(text(x2 + 20, y_top + 285, "• Запис приймає будь-який вузол", size=11, anchor="start"))
    c.append(text(x2 + 20, y_top + 310, "• Оптимістичне блокування (Commit Rollback)", size=11, anchor="start"))
    c.append(text(x2 + 20, y_top + 335, "• Кворумна сертифікація конфліктів", size=11, anchor="start"))
    c.append(text(x2 + 20, y_top + 360, "• Приклади: Galera Cluster, Group Repl.", size=11, anchor="start", color=MUTED))

    # 3. Distributed Consensus / NewSQL
    x3 = 650
    c.append(rect(x3, y_top, panel_w, panel_h, fill="#fafbfc", stroke=LINE, rx=8))
    c.append(rect(x3, y_top, panel_w, 36, fill="#dcfce7", stroke=LINE, rx=8))
    c.append(text(x3 + panel_w / 2, y_top + 23, "3. Розподілений консенсус (NewSQL)", size=13, bold=True, color="#15803d"))

    # Ranges & Raft groups
    b6, _, _ = textbox(x3 + panel_w / 2, y_top + 80, "Діапазон R1 [A..M]: Лідер Raft\nВузол 1 (Лідер) ↔ Вузли 2,3 (Фоловер)", size=11, fill="#d1fae5", stroke="#059669", min_w=260)
    b7, _, _ = textbox(x3 + panel_w / 2, y_top + 160, "Діапазон R2 [N..Z]: Лідер Raft\nВузол 2 (Лідер) ↔ Вузли 1,3 (Фоловер)", size=11, fill="#ede9fe", stroke="#7c3aed", min_w=260)
    c.extend([b6, b7])

    c.append(arrow(x3 + panel_w / 2, y_top + 115, x3 + panel_w / 2, y_top + 135, color=LINE, sw=1.5))

    # Властивості
    c.append(line(x3 + 15, y_top + 260, x3 + panel_w - 15, y_top + 260, color="#d1d5db", dash="3,3"))
    c.append(text(x3 + 20, y_top + 285, "• Автоматичне шардування на діапазони", size=11, anchor="start"))
    c.append(text(x3 + 20, y_top + 310, "• Незалежний Raft-консенсус на діапазон", size=11, anchor="start"))
    c.append(text(x3 + 20, y_top + 335, "• Прозоре горизонтальне масштабування", size=11, anchor="start"))
    c.append(text(x3 + 20, y_top + 360, "• Приклади: CockroachDB, TiDB, Spanner", size=11, anchor="start", color=MUTED))

    render(os.path.join(OUT_DIR, "database-clustering-topologies.svg"), w, h, "".join(c))


def fig_patroni_etcd_architecture():
    """Архітектура високонадійного кластера Patroni + etcd + HAProxy."""
    w, h = 960, 520
    c = []

    c.append(text(w / 2, 28, "Архітектура відмовостійкого кластера: Patroni + etcd + HAProxy", size=18, bold=True))
    c.append(text(w / 2, 50, "Розподілена координація консенсусу, сервісний супервізор та маршрутизація запитів", size=13, color=MUTED))

    # 1. Application Layer (Клієнти)
    b_app, _, _ = textbox(w / 2, 90, "Застосунки бекенду (Web / API / Microservices)", size=13, fill="#f3f4f6", stroke="#4b5563", min_w=400)
    c.append(b_app)

    # Arrows to Proxy
    c.append(arrow(w / 2 - 120, 115, w / 2 - 120, 150, color=POS, sw=2))
    c.append(text(w / 2 - 130, 135, "Port 5000 (RW)", size=11, color=POS, anchor="end", bold=True))

    c.append(arrow(w / 2 + 120, 115, w / 2 + 120, 150, color=NEG, sw=2))
    c.append(text(w / 2 + 130, 135, "Port 5001 (RO)", size=11, color=NEG, anchor="start", bold=True))

    # 2. HAProxy Layer
    b_haproxy, _, _ = textbox(w / 2, 175, "Маршрутизатор з'єднань HAProxy / PgBouncer\nПостійна перевірка HTTP-ендпоінтів Patroni (/primary, /replica)", size=12, fill="#fffbeb", stroke="#f59e0b", min_w=650)
    c.append(b_haproxy)

    # 3. Database Cluster Nodes (PostgreSQL + Patroni)
    node_w = 260
    node_h = 130
    y_nodes = 245

    # Node 1 (Primary)
    x_n1 = 50
    c.append(rect(x_n1, y_nodes, node_w, node_h, fill="#eff6ff", stroke="#2563eb", sw=2, rx=8))
    c.append(text(x_n1 + node_w / 2, y_nodes + 22, "Вузол 1 (Поточний Лідер)", size=13, bold=True, color="#1d4ed8"))
    c.append(text(x_n1 + node_w / 2, y_nodes + 45, "PostgreSQL (Primary, RW)", size=12, bold=True))
    c.append(rect(x_n1 + 15, y_nodes + 60, node_w - 30, 26, fill="#dbeafe", stroke="#93c5fd", rx=4))
    c.append(text(x_n1 + node_w / 2, y_nodes + 78, "Patroni Daemon (Тримає лізу)", size=11, bold=True, color="#1e40af"))
    c.append(text(x_n1 + node_w / 2, y_nodes + 110, "HTTP REST API (:8008/primary -> 200 OK)", size=10, color=FIELD))

    # Node 2 (Standby 1)
    x_n2 = 350
    c.append(rect(x_n2, y_nodes, node_w, node_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    c.append(text(x_n2 + node_w / 2, y_nodes + 22, "Вузол 2 (Синхронна репліка)", size=13, bold=True, color=INK))
    c.append(text(x_n2 + node_w / 2, y_nodes + 45, "PostgreSQL (Standby, RO)", size=12))
    c.append(rect(x_n2 + 15, y_nodes + 60, node_w - 30, 26, fill="#f1f5f9", stroke="#cbd5e1", rx=4))
    c.append(text(x_n2 + node_w / 2, y_nodes + 78, "Patroni Daemon (Стежить за лізою)", size=11, color=MUTED))
    c.append(text(x_n2 + node_w / 2, y_nodes + 110, "HTTP REST API (:8008/replica -> 200 OK)", size=10, color=NEG))

    # Node 3 (Standby 2)
    x_n3 = 650
    c.append(rect(x_n3, y_nodes, node_w, node_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    c.append(text(x_n3 + node_w / 2, y_nodes + 22, "Вузол 3 (Асинхронна репліка)", size=13, bold=True, color=INK))
    c.append(text(x_n3 + node_w / 2, y_nodes + 45, "PostgreSQL (Standby, RO)", size=12))
    c.append(rect(x_n3 + 15, y_nodes + 60, node_w - 30, 26, fill="#f1f5f9", stroke="#cbd5e1", rx=4))
    c.append(text(x_n3 + node_w / 2, y_nodes + 78, "Patroni Daemon (Стежить за лізою)", size=11, color=MUTED))
    c.append(text(x_n3 + node_w / 2, y_nodes + 110, "HTTP REST API (:8008/replica -> 200 OK)", size=10, color=NEG))

    # Traffic lines from HAProxy to Nodes
    c.append(arrow(w / 2 - 100, 205, x_n1 + node_w / 2, y_nodes, color=POS, sw=1.8))
    c.append(arrow(w / 2 + 50, 205, x_n2 + node_w / 2, y_nodes, color=NEG, sw=1.5))
    c.append(arrow(w / 2 + 150, 205, x_n3 + node_w / 2, y_nodes, color=NEG, sw=1.5))

    # WAL Replication lines between PG nodes
    c.append(arrow(x_n1 + node_w, y_nodes + 45, x_n2, y_nodes + 45, color=FIELD, sw=2))
    c.append(text((x_n1 + node_w + x_n2) / 2, y_nodes + 38, "WAL", size=10, color=FIELD, bold=True))
    c.append(arrow(x_n2 + node_w, y_nodes + 45, x_n3, y_nodes + 45, color=FIELD, sw=2))
    c.append(text((x_n2 + node_w + x_n3) / 2, y_nodes + 38, "WAL", size=10, color=FIELD, bold=True))

    # 4. Distributed Consensus Store (etcd Cluster)
    y_etcd = 430
    c.append(rect(40, y_etcd, 880, 75, fill="#f5f3ff", stroke="#8b5cf6", sw=1.5, rx=8))
    c.append(text(120, y_etcd + 24, "DCS Кворум (etcd 3-node):", size=12, bold=True, color="#6d28d9", anchor="start"))
    c.append(text(120, y_etcd + 48, "Ключ лідера: /service/db/leader = 'node1' (TTL = 10s)", size=11, color="#4c1d95", anchor="start"))

    # etcd nodes mini boxes
    b_e1, _, _ = textbox(560, y_etcd + 37, "etcd #1\n(Leader)", size=10, fill="#ede9fe", stroke="#7c3aed", min_w=80)
    b_e2, _, _ = textbox(680, y_etcd + 37, "etcd #2\n(Follower)", size=10, fill="#ede9fe", stroke="#7c3aed", min_w=80)
    b_e3, _, _ = textbox(800, y_etcd + 37, "etcd #3\n(Follower)", size=10, fill="#ede9fe", stroke="#7c3aed", min_w=80)
    c.extend([b_e1, b_e2, b_e3])

    # Heartbeat arrows between Patroni and DCS
    c.append(arrow(x_n1 + node_w / 2, y_nodes + node_h, x_n1 + node_w / 2, y_etcd, color="#6d28d9", sw=1.5))
    c.append(text(x_n1 + node_w / 2 + 8, y_etcd - 20, "Heartbeat (2s)", size=10, color="#6d28d9", anchor="start"))

    c.append(arrow(x_n2 + node_w / 2, y_nodes + node_h, x_n2 + node_w / 2, y_etcd, color="#6d28d9", sw=1.5))
    c.append(arrow(x_n3 + node_w / 2, y_nodes + node_h, x_n3 + node_w / 2, y_etcd, color="#6d28d9", sw=1.5))

    render(os.path.join(OUT_DIR, "patroni-etcd-ha-architecture.svg"), w, h, "".join(c))


def fig_failover_timeline():
    """Порівняння життєвого циклу планового Switchover та аварійного Failover."""
    w, h = 960, 490
    c = []

    c.append(text(w / 2, 28, "Життєвий цикл зміни лідера: Switchover проти Failover", size=18, bold=True))
    c.append(text(w / 2, 50, "Контрольоване планове перемикання проти аварійного відновлення після краху", size=13, color=MUTED))

    # Секція 1: Плановий Switchover (Zero Data Loss)
    y1 = 80
    c.append(rect(20, y1, 920, 175, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    c.append(text(40, y1 + 25, "Плановий Switchover (RPO = 0, планове обслуговування)", size=14, bold=True, color="#15803d", anchor="start"))

    # Етапи switchover
    steps_s = [
        ("1. Сигнал Demote", "Зупинка прийому\nнових транзакцій"),
        ("2. Синхронізація", "Очікування LSN:\nStandby доганяє WAL"),
        ("3. Оновлення DCS", "Зміна ключа лідера\nв etcd на вузол 2"),
        ("4. Промоція", "Standby стає Primary\n(pg_ctl promote)"),
        ("5. Маршрутизація", "HAProxy спрямовує\nRW-трафік на вузол 2")
    ]

    for i, (title, desc) in enumerate(steps_s):
        x_st = 50 + i * 175
        b_st, _, _ = textbox(x_st + 75, y1 + 95, f"{title}\n{desc}", size=11, fill="#dcfce7", stroke="#22c55e", min_w=150)
        c.append(b_st)
        if i < len(steps_s) - 1:
            c.append(arrow(x_st + 155, y1 + 95, x_st + 170, y1 + 95, color="#16a34a", sw=2))

    c.append(text(40, y1 + 160, "Результат: Нульова втрата даних (RPO=0), пауза запису 300–800 мс, колишній лідер безпечно стає реплікою", size=11, color="#166534", anchor="start", bold=True))

    # Секція 2: Аварійний Failover (Emergency Recovery)
    y2 = 280
    c.append(rect(20, y2, 920, 185, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    c.append(text(40, y2 + 25, "Аварійний Failover (RPO >= 0, раптовий крах лідера)", size=14, bold=True, color="#b91c1c", anchor="start"))

    # Етапи failover
    steps_f = [
        ("1. Крах Лідера", "Вузол 1 гине або\nізолюється мережею"),
        ("2. Спливання лізи", "DCS Lease TTL (10s)\nвичерпується"),
        ("3. Вибори & LSN", "Репліки порівнюють\nнайновіший WAL LSN"),
        ("4. Огородження", "STONITH / Watchdog\nблокує старий вузол 1"),
        ("5. Промоція Репліки", "Вузол 2 стає Primary,\nHAProxy перемикає")
    ]

    for i, (title, desc) in enumerate(steps_f):
        x_st = 50 + i * 175
        b_st, _, _ = textbox(x_st + 75, y2 + 95, f"{title}\n{desc}", size=11, fill="#fee2e2", stroke="#ef4444", min_w=150)
        c.append(b_st)
        if i < len(steps_f) - 1:
            c.append(arrow(x_st + 155, y2 + 95, x_st + 170, y2 + 95, color="#dc2626", sw=2))

    c.append(text(40, y2 + 165, "Результат: Автоматичне відновлення доступності (RTO ~10–15 с), при асинхронній реплікації можливий RPO > 0 (потрібен pg_rewind)", size=11, color="#991b1b", anchor="start", bold=True))

    render(os.path.join(OUT_DIR, "failover-vs-switchover-timeline.svg"), w, h, "".join(c))


def fig_fencing_stonith():
    """Механізм огородження (Fencing) та STONITH для запобігання Split-Brain."""
    w, h = 960, 480
    c = []

    c.append(text(w / 2, 28, "Захист від Split-Brain: Кворум, Fencing та STONITH", size=18, bold=True))
    c.append(text(w / 2, 50, "Як кластер нейтралізує ізольований вузол і запобігає паралельному запису розбіжних даних", size=13, color=MUTED))

    # Мережевий розрив (Network Partition Barrier)
    x_part = 420
    c.append(line(x_part, 75, x_part, 440, color=POS, sw=2.5, dash="6,6"))
    c.append(text(x_part, 85, "МЕРЕЖЕВИЙ РОЗРИВ (Partition)", size=12, color=POS, bold=True))

    # Лівий бік: Ізольований старий лідер (Minority Partition, 1 вузол)
    c.append(rect(30, 105, 360, 340, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=8))
    c.append(text(210, 130, "Ізольований сегмент (Меншість 1/3)", size=13, bold=True, color="#be123c"))

    b_old, _, _ = textbox(210, 190, "Старий Лідер (Вузол 1)\nВважає себе лідером, але\nвтратив зв'язок із DCS", size=12, fill="#ffe4e6", stroke="#e11d48", min_w=300)
    c.append(b_old)

    # Watchdog timer box
    b_wd, _, _ = textbox(210, 285, "Апаратний Watchdog (/dev/watchdog)\nЛіза спливла -> Скидання таймера не виконано\n-> Примусовий Kernel Panic / Hard Reset", size=11, fill="#fecdd3", stroke="#be123c", min_w=320)
    c.append(b_wd)

    c.append(arrow(210, 225, 210, 255, color=POS, sw=2))
    c.append(text(210, 360, "STONITH (Shoot The Other Node)", size=12, bold=True, color=POS))
    c.append(text(210, 385, "Вузол 1 фізично вимикається або перезавантажується,\nблокуючи будь-яку можливість прийняти запис", size=10, color=MUTED))

    # Правий бік: Кворумний сегмент (Majority Partition, 2 вузли + DCS)
    c.append(rect(450, 105, 480, 340, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    c.append(text(690, 130, "Кворумний сегмент (Більшість 2/3 + DCS)", size=13, bold=True, color="#15803d"))

    # DCS quorum
    b_dcs, _, _ = textbox(690, 185, "DCS Кворум (etcd 3-Node Quorum)\n2 з 3 вузлів доступні -> Кворум є\nФіксує спливання лізи Вузла 1", size=11, fill="#ede9fe", stroke="#8b5cf6", min_w=400)
    c.append(b_dcs)

    # New leader election
    b_n2, _, _ = textbox(570, 290, "Вузол 2 (Новий Лідер)\nВиграє лізу в etcd\nСтає Primary (RW)", size=11, fill="#dcfce7", stroke="#16a34a", min_w=200)
    b_n3, _, _ = textbox(810, 290, "Вузол 3 (Репліка)\nПерепідключається\nдо Вузла 2", size=11, fill="#dbeafe", stroke="#2563eb", min_w=200)
    c.extend([b_n2, b_n3])

    c.append(arrow(690, 220, 590, 255, color="#16a34a", sw=2))
    c.append(arrow(570 + 105, 290, 810 - 105, 290, color=FIELD, sw=2))
    c.append(text(690, 280, "WAL потік", size=10, color=FIELD, bold=True))

    c.append(text(690, 360, "Консистентність збережена", size=12, bold=True, color="#15803d"))
    c.append(text(690, 385, "Кластер продовжує приймати транзакції без колізій;\nдва лідери не можуть існувати одночасно", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "fencing-stonith-mechanism.svg"), w, h, "".join(c))


def main():
    print("Генерація SVG-фігур для database-clustering...")
    fig_topologies()
    fig_patroni_etcd_architecture()
    fig_failover_timeline()
    fig_fencing_stonith()
    print("Усі фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
