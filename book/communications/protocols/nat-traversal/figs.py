#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для статті про NAT-траверсаль (STUN, TURN, ICE)."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

DIR = os.path.dirname(__file__)
IMG = os.path.join(DIR, "img")
os.makedirs(IMG, exist_ok=True)


def fig_nat_traversal_matrix():
    """Матриця прохідності різних комбінацій NAT."""
    w, h = 860, 470
    frags = []

    # Заголовок матриці та підписи осей
    frags.append(text(w / 2, 28, "Матриця сумісності та методів проходження NAT (P2P vs Relay)", size=15, bold=True))
    frags.append(text(w / 2, 50, "Поведінка відображення сокетів та фільтрації трафіку між двома вузлами (RFC 4787 / 8445)", size=12, color=MUTED))

    # Стовпці та рядки
    cols = ["Full Cone (EIM/EIF)", "Restricted (EIM/ADF)", "Port-Restricted (EIM/APDF)", "Symmetric (APDM/APDF)"]
    rows = ["Full Cone (EIM/EIF)", "Restricted (EIM/ADF)", "Port-Restricted (EIM/APDF)", "Symmetric (APDM/APDF)"]

    ox = 180
    oy = 90
    cell_w = 160
    cell_h = 75

    # Підписи стовпців (Вузол B)
    frags.append(text(ox + 2 * cell_w, oy - 20, "Вузол B (Тип NAT на стороні приймача)", size=13, bold=True, color=INK))
    for j, col_title in enumerate(cols):
        cx = ox + j * cell_w + cell_w / 2
        lines = col_title.split(" ")
        frags.append(mtext(cx, oy - 8, lines, size=11, bold=True, color=LINE))

    # Підписи рядків (Вузол A)
    frags.append(text(75, oy + 2 * cell_h, "Вузол A\n(Відправник)", size=13, bold=True, color=INK))
    for i, row_title in enumerate(rows):
        cy = oy + i * cell_h + cell_h / 2
        lines = row_title.split(" ")
        frags.append(mtext(95, cy - 4, lines, size=11, bold=True, anchor="middle", color=LINE))

    # Заповнення комірок
    # 0: Full Cone, 1: Restricted, 2: Port-Restricted, 3: Symmetric
    matrix_data = [
        # Full Cone
        [("Прямий P2P\n(STUN Direct)", "#e8f8f5", FIELD),
         ("Прямий P2P\n(STUN Direct)", "#e8f8f5", FIELD),
         ("Прямий P2P\n(STUN Direct)", "#e8f8f5", FIELD),
         ("Hole Punching\n(STUN)", "#eaf2f8", NEG)],
        # Restricted
        [("Прямий P2P\n(STUN Direct)", "#e8f8f5", FIELD),
         ("Hole Punching\n(UDP STUN)", "#eaf2f8", NEG),
         ("Hole Punching\n(UDP STUN)", "#eaf2f8", NEG),
         ("Гарантований\nTURN Relay", "#fdedec", POS)],
        # Port-Restricted
        [("Прямий P2P\n(STUN Direct)", "#e8f8f5", FIELD),
         ("Hole Punching\n(UDP STUN)", "#eaf2f8", NEG),
         ("Hole Punching\n(UDP STUN)", "#eaf2f8", NEG),
         ("Гарантований\nTURN Relay", "#fdedec", POS)],
        # Symmetric
        [("Hole Punching\n(STUN)", "#eaf2f8", NEG),
         ("Гарантований\nTURN Relay", "#fdedec", POS),
         ("Гарантований\nTURN Relay", "#fdedec", POS),
         ("Необхідний\nTURN Relay", "#fdedec", POS)]
    ]

    for i in range(4):
        for j in range(4):
            label, bg_col, stroke_col = matrix_data[i][j]
            x = ox + j * cell_w
            y = oy + i * cell_h
            frags.append(fitbox(x + 4, y + 4, cell_w - 8, cell_h - 8, label, size=12, bold=True,
                                fill=bg_col, stroke=stroke_col, sw=1.5))

    # Легенда внизу
    leg_y = oy + 4 * cell_h + 30
    frags.append(rect(140, leg_y - 12, 18, 18, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(168, leg_y + 2, "Пряме з'єднання (STUN)", size=12, anchor="start", color=INK))

    frags.append(rect(370, leg_y - 12, 18, 18, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(398, leg_y + 2, "UDP Hole Punching (STUN)", size=12, anchor="start", color=INK))

    frags.append(rect(610, leg_y - 12, 18, 18, fill="#fdedec", stroke=POS, sw=1.5, rx=3))
    frags.append(text(638, leg_y + 2, "Ретрансляція (TURN Relay)", size=12, anchor="start", color=INK))

    render(os.path.join(IMG, "nat-traversal-matrix.svg"), w, h, *frags)


def fig_udp_hole_punching_sequence():
    """Діаграма послідовності UDP Hole Punching."""
    w, h = 880, 520
    frags = []

    frags.append(text(w / 2, 26, "Механізм пробивання отворів (UDP Hole Punching) через STUN та Сигналізацію", size=15, bold=True))

    # Лінії життя (Lifelines)
    actors = [
        (80, "Клієнт A\n192.168.1.50"),
        (240, "NAT A (Шлюз)\n198.51.100.10"),
        (440, "Сервер STUN / Сигналізація\n203.0.113.1"),
        (640, "NAT B (Шлюз)\n198.51.100.20"),
        (800, "Клієнт B\n10.0.0.22")
    ]

    for x, title in actors:
        box, bw, bh = textbox(x, 68, title, size=11, bold=True, pad=6)
        frags.append(box)
        frags.append(line(x, 92, x, 490, color=MUTED, sw=1.2, dash="4,4"))

    # Покрокові повідомлення
    # 1. STUN Binding Request A
    y1 = 120
    frags.append(arrow(80, y1, 240, y1, color=NEG, sw=1.5))
    frags.append(text(160, y1 - 6, "1. UDP:порт 5000", size=10, color=NEG, bold=True))
    frags.append(arrow(240, y1, 440, y1, color=NEG, sw=1.5))
    frags.append(text(340, y1 - 6, "STUN Binding Request (зовн. порт 40001)", size=10, color=NEG))

    # 1b. STUN Binding Response A
    y2 = 155
    frags.append(arrow(440, y2, 240, y2, color=FIELD, sw=1.5))
    frags.append(text(340, y2 - 6, "STUN Binding Resp (XOR: 198.51.100.10:40001)", size=10, color=FIELD))
    frags.append(arrow(240, y2, 80, y2, color=FIELD, sw=1.5))

    # 2. STUN Binding Request B
    y3 = 190
    frags.append(arrow(800, y3, 640, y3, color=NEG, sw=1.5))
    frags.append(text(720, y3 - 6, "2. UDP:порт 6000", size=10, color=NEG, bold=True))
    frags.append(arrow(640, y3, 440, y3, color=NEG, sw=1.5))
    frags.append(text(540, y3 - 6, "STUN Binding Request (зовн. порт 50002)", size=10, color=NEG))

    # 2b. STUN Binding Response B
    y4 = 225
    frags.append(arrow(440, y4, 640, y4, color=FIELD, sw=1.5))
    frags.append(text(540, y4 - 6, "STUN Binding Resp (XOR: 198.51.100.20:50002)", size=10, color=FIELD))
    frags.append(arrow(640, y4, 800, y4, color=FIELD, sw=1.5))

    # 3. Сигналізація (Обмін адресами)
    y5 = 265
    frags.append(rect(180, y5 - 12, 520, 24, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(440, y5 + 4, "3. Обмін рефлексивними сокетами через Сигналізацію (SDP / WebSocket)", size=11, bold=True, color=INK))

    # 4. Зустрічні пробні пакети (Пробивання дірки)
    y6 = 310
    frags.append(arrow(80, y6, 635, y6 + 25, color=POS, sw=1.5))
    frags.append(text(280, y6 - 4, "4. Пакет A ➔ B (створює стан у NAT A; NAT B відкидає)", size=10, color=POS))
    frags.append(circle(640, y6 + 25, 5, fill=POS, stroke=LINE, sw=1))

    y7 = 355
    frags.append(arrow(800, y7, 245, y7 + 25, color=POS, sw=1.5))
    frags.append(text(600, y7 - 4, "5. Пакет B ➔ A (проходить відкритий NAT A! Відкриває NAT B)", size=10, color=POS))
    frags.append(circle(240, y7 + 25, 5, fill=FIELD, stroke=LINE, sw=1))

    # 6. Прямий двонаправлений P2P канал
    y8 = 425
    frags.append(rect(70, y8 - 20, 740, 48, fill="#e8f8f5", stroke=FIELD, sw=2, rx=6))
    frags.append(arrow(90, y8 + 4, 790, y8 + 4, color=FIELD, sw=2))
    frags.append(arrow(790, y8 + 4, 90, y8 + 4, color=FIELD, sw=2))
    frags.append(text(440, y8 - 4, "6. Прямий двонаправлений P2P медіапотік (RTP / UDP канал відкрито)", size=12, bold=True, color=FIELD))
    frags.append(text(440, y8 + 16, "Створено сесії conntrack: 198.51.100.10:40001 ⇄ 198.51.100.20:50002", size=10, color=MUTED))

    render(os.path.join(IMG, "udp-hole-punching-sequence.svg"), w, h, *frags)


def fig_stun_packet_structure():
    """Бінарна структура заголовка STUN (RFC 8489) та XOR-MAPPED-ADDRESS."""
    w, h = 860, 430
    frags = []

    frags.append(text(w / 2, 24, "Структура заголовка пакета STUN (RFC 8489) та атрибута XOR-MAPPED-ADDRESS", size=14, bold=True))

    ox = 50
    oy = 55
    bw = 760

    # Розмітка бітів 0..31
    frags.append(rect(ox, oy, bw, 22, fill="#e5e8e8", stroke=LINE, sw=1.2, rx=2))
    bit_steps = [0, 2, 16, 31]
    for bit in range(32):
        bx = ox + (bit * bw) / 32
        if bit in (0, 2, 16, 31):
            frags.append(text(bx + (bw / 64 if bit != 31 else -bw / 64), oy + 15, str(bit), size=10, color=LINE, bold=True))

    # Рядок 1: 0x00 (2 біти) | STUN Message Type (14 бітів) | Message Length (16 бітів)
    y1 = oy + 26
    h1 = 44
    frags.append(rect(ox, y1, bw * 2 / 32, h1, fill="#fdedec", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + (bw * 1 / 32), y1 + 26, "00", size=11, bold=True, color=POS))

    frags.append(rect(ox + bw * 2 / 32, y1, bw * 14 / 32, h1, fill="#ebf5fb", stroke=LINE, sw=1.2, rx=2))
    frags.append(mtext(ox + bw * 9 / 32, y1 + 20, ["STUN Message Type (14 бітів)", "Class (2) + Method (12)"], size=10, bold=True, color=NEG))

    frags.append(rect(ox + bw * 16 / 32, y1, bw * 16 / 32, h1, fill="#fef9e7", stroke=LINE, sw=1.2, rx=2))
    frags.append(mtext(ox + bw * 24 / 32, y1 + 20, ["Message Length (16 бітів)", "(без урахування 20 байтів заголовка)"], size=10, bold=True, color=INK))

    # Рядок 2: Magic Cookie (0x2112A442)
    y2 = y1 + h1 + 4
    frags.append(rect(ox, y2, bw, h1, fill="#e8f8f5", stroke=LINE, sw=1.2, rx=2))
    frags.append(mtext(ox + bw / 2, y2 + 20, ["Magic Cookie: 0x2112A442 (32 біти)", "Фіксована константа для детектування STUN та захисту від некоректних NAT ALG"], size=11, bold=True, color=FIELD))

    # Рядки 3-5: Transaction ID (96 бітів = 12 байтів)
    y3 = y2 + h1 + 4
    h_tid = 50
    frags.append(rect(ox, y3, bw, h_tid, fill="#f4f6f7", stroke=LINE, sw=1.2, rx=2))
    frags.append(mtext(ox + bw / 2, y3 + 22, ["Transaction ID (96 бітів / 12 байтів)", "Криптографічно випадковий ідентифікатор транзакції для запобігання підміні та зіставлення пар запит-відповідь"], size=11, bold=True, color=LINE))

    # TLV Атрибут: XOR-MAPPED-ADDRESS
    y4 = y3 + h_tid + 16
    frags.append(text(ox + 8, y4 - 4, "Корисне навантаження: Атрибут XOR-MAPPED-ADDRESS (Тип 0x0020)", size=12, bold=True, anchor="start", color=INK))

    # Рядок атрибута: Type (16 бітів) | Length (16 бітів)
    h_tlv = 36
    frags.append(rect(ox, y4 + 4, bw / 2, h_tlv, fill="#f5eef8", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + bw / 4, y4 + 26, "Type = 0x0020 (XOR-MAPPED-ADDRESS)", size=10, bold=True, color=INK))

    frags.append(rect(ox + bw / 2, y4 + 4, bw / 2, h_tlv, fill="#f5eef8", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + 3 * bw / 4, y4 + 26, "Length = 0x0008 (8 байтів для IPv4)", size=10, bold=True, color=INK))

    # Рядок значення: Reserved (8) | Family (8) | X-Port (16)
    y5 = y4 + h_tlv + 6
    frags.append(rect(ox, y5, bw * 8 / 32, h_tlv, fill="#fef5e7", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + bw * 4 / 32, y5 + 22, "Reserved (0x00)", size=10, color=MUTED))

    frags.append(rect(ox + bw * 8 / 32, y5, bw * 8 / 32, h_tlv, fill="#fef5e7", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + bw * 12 / 32, y5 + 22, "Family: IPv4 (0x01)", size=10, bold=True, color=INK))

    frags.append(rect(ox + bw * 16 / 32, y5, bw * 16 / 32, h_tlv, fill="#e8f6f3", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + bw * 24 / 32, y5 + 22, "X-Port = Реальний Порт ⊕ 0x2112", size=10, bold=True, color=FIELD))

    # Рядок адреси: X-Address (32 біти)
    y6 = y5 + h_tlv + 4
    frags.append(rect(ox, y6, bw, h_tlv, fill="#e8f6f3", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(ox + bw / 2, y6 + 22, "X-Address = Реальна IPv4-адреса ⊕ Magic Cookie (0x2112A442)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "stun-packet-structure.svg"), w, h, *frags)


def fig_turn_relay_lifecycle():
    """Життєвий цикл ретрансляції сесії TURN (RFC 8656)."""
    w, h = 880, 480
    frags = []

    frags.append(text(w / 2, 24, "Архітектура та життєвий цикл ретрансляції TURN (RFC 8656)", size=15, bold=True))

    # Вузли
    actors = [
        (90, "Клієнт A\n(Симетричний NAT)"),
        (260, "NAT A\n(Шлюз)"),
        (480, "Сервер TURN (Релей)\n203.0.113.50 (WAN)"),
        (780, "Співрозмовник B\n(Peer B)")
    ]

    for x, title in actors:
        box, bw, bh = textbox(x, 65, title, size=11, bold=True, pad=6)
        frags.append(box)
        frags.append(line(x, 88, x, 450, color=MUTED, sw=1.2, dash="4,4"))

    # Фаза 1: Allocate
    y1 = 115
    frags.append(arrow(90, y1, 480, y1, color=NEG, sw=1.5))
    frags.append(text(285, y1 - 6, "1. Allocate Request (Автентифікація + Запит релею)", size=10, color=NEG, bold=True))

    y2 = 145
    frags.append(arrow(480, y2, 90, y2, color=FIELD, sw=1.5))
    frags.append(mtext(285, y2 - 4, ["Allocate Success Resp (XOR-RELAYED-ADDRESS: 203.0.113.50:60000)", "Lifetime = 600 с"], size=9, color=FIELD))

    # Фаза 2: CreatePermission
    y3 = 190
    frags.append(arrow(90, y3, 480, y3, color=LINE, sw=1.5))
    frags.append(text(285, y3 - 6, "2. CreatePermission Request (Дозвіл для IP вузла B: 198.51.100.20)", size=10, color=LINE, bold=True))

    y4 = 218
    frags.append(arrow(480, y4, 90, y4, color=FIELD, sw=1.5))
    frags.append(text(285, y4 - 6, "CreatePermission Success Response (IP авторизовано)", size=9, color=FIELD))

    # Фаза 3: ChannelBind
    y5 = 260
    frags.append(arrow(90, y5, 480, y5, color=POS, sw=1.5))
    frags.append(text(285, y5 - 6, "3. ChannelBind Request (Прив'язка ChannelNumber = 0x4001 до Peer B)", size=10, color=POS, bold=True))

    y6 = 288
    frags.append(arrow(480, y6, 90, y6, color=FIELD, sw=1.5))
    frags.append(text(285, y6 - 6, "ChannelBind Success Response (Канал 0x4001 активовано)", size=9, color=FIELD))

    # Фаза 4: Ретрансляція медіа
    y7 = 345
    frags.append(rect(80, y7 - 18, 710, 85, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(435, y7 - 4, "4. Передача медіа через оптимізовані канали ChannelData (4 байти оверхеду)", size=11, bold=True, color=INK))

    frags.append(arrow(90, y7 + 22, 480, y7 + 22, color=LINE, sw=1.5))
    frags.append(text(285, y7 + 14, "ChannelData: [0x4001][Len][RTP Payload]", size=9, bold=True, color=INK))

    frags.append(arrow(480, y7 + 22, 780, y7 + 22, color=FIELD, sw=1.8))
    frags.append(text(630, y7 + 14, "Сирий UDP / RTP (від 203.0.113.50:60000)", size=9, color=FIELD, bold=True))

    frags.append(arrow(780, y7 + 50, 480, y7 + 50, color=FIELD, sw=1.8))
    frags.append(text(630, y7 + 42, "Сирий UDP / RTP відповідь", size=9, color=FIELD, bold=True))

    frags.append(arrow(480, y7 + 50, 90, y7 + 50, color=LINE, sw=1.5))
    frags.append(text(285, y7 + 42, "ChannelData: [0x4001][Len][RTP Payload]", size=9, bold=True, color=INK))

    render(os.path.join(IMG, "turn-relay-lifecycle.svg"), w, h, *frags)


def fig_ice_candidate_checklist_flow():
    """Конвеєр ICE: збір кандидатів, формування пар, перевірки та номінація."""
    w, h = 860, 460
    frags = []

    frags.append(text(w / 2, 24, "Конвеєр обробки з'єднань фреймворку ICE (RFC 8445)", size=15, bold=True))

    # 5 блоків конвеєра
    stages = [
        ("1. Збір кандидатів", ["Host: локальні IP", "Srflx: STUN рефлексивні", "Prflx: виявлені піром", "Relay: виділені TURN"], NEG, "#ebf5fb"),
        ("2. Обмін через SDP", ["Оферта / Відповідь", "a=candidate атрибути", "ufrag та pwd паролі", "Обмін списками"], LINE, "#f4f6f7"),
        ("3. Формування пар", ["Декартовий добуток", "Пріоритет пари:", "2³²·min(G,D) + 2·max", "Формування чекліста"], INK, "#fef9e7"),
        ("4. Перевірка зв'язку", ["STUN Binding Checks", "Frozen ➔ Waiting", "➔ In-Progress", "➔ Succeeded / Failed"], POS, "#fdedec"),
        ("5. Номінація шляху", ["USE-CANDIDATE прапор", "Controlling агент", "Формування Valid List", "Активація медіапотоку"], FIELD, "#e8f8f5")
    ]

    bx = 35
    by = 70
    bw = 145
    bh = 175
    gap = 20

    for i, (title, items_list, border_col, bg_col) in enumerate(stages):
        x = bx + i * (bw + gap)
        frags.append(rect(x, by, bw, bh, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        frags.append(text(x + bw / 2, by + 22, title, size=11, bold=True, color=border_col))
        frags.append(line(x + 8, by + 32, x + bw - 8, by + 32, color=border_col, sw=1))

        for k, itm in enumerate(items_list):
            frags.append(text(x + 10, by + 56 + k * 28, itm, size=9.5, anchor="start", color=INK))

        # Стрілка між блоками
        if i < 4:
            ax = x + bw + 2
            frags.append(arrow(ax, by + bh / 2, ax + gap - 4, by + bh / 2, color=MUTED, sw=2))

    # Нижня частина: деталізація станів пари кандидатів
    by2 = 280
    frags.append(rect(35, by2, 790, 150, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(w / 2, by2 + 22, "Граф переходу станів пари кандидатів у контрольному списку (Checklist State Machine)", size=12, bold=True, color=INK))

    states = [
        (100, by2 + 75, "Frozen\n(Заблоковано)", "#eaeded", LINE),
        (260, by2 + 75, "Waiting\n(У черзі)", "#ebf5fb", NEG),
        (420, by2 + 75, "In-Progress\n(STUN Check)", "#fef9e7", "#d4ac0d"),
        (600, by2 + 55, "Succeeded\n(Відповідь є)", "#e8f8f5", FIELD),
        (600, by2 + 105, "Failed\n(Таймаут/RST)", "#fdedec", POS),
        (740, by2 + 55, "Nominated\n(Обрано шлях)", "#d4efdf", FIELD)
    ]

    for sx, sy, stext, sfill, sstroke in states:
        box, _, _ = textbox(sx, sy, stext, size=10, bold=True, fill=sfill, stroke=sstroke, pad=6)
        frags.append(box)

    # Стрілки станів
    frags.append(arrow(140, by2 + 75, 215, by2 + 75, color=LINE, sw=1.5))
    frags.append(arrow(300, by2 + 75, 375, by2 + 75, color=LINE, sw=1.5))
    frags.append(arrow(470, by2 + 70, 545, by2 + 55, color=FIELD, sw=1.5))
    frags.append(arrow(470, by2 + 80, 545, by2 + 105, color=POS, sw=1.5))
    frags.append(arrow(650, by2 + 55, 690, by2 + 55, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "ice-candidate-checklist-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_nat_traversal_matrix()
    fig_udp_hole_punching_sequence()
    fig_stun_packet_structure()
    fig_turn_relay_lifecycle()
    fig_ice_candidate_checklist_flow()
    print("Всі фігури успішно згенеровано.")
