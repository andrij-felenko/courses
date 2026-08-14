# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CLR_TCP  = "#2457d6"
CLR_UDP  = "#27ae60"
CLR_QUIC = "#c0392b"
CLR_WARN = "#b08900"

def fig_stack_comparison():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 28, "Порівняння архітектури мережевих стеків", size=16, bold=True))

    col_w = 240
    gap = 40
    x_start = 60

    stacks = [
        ("HTTP/1.1 (TCP)", [
            ("HTTP/1.1 (текстовий)", "#fdf3e0", INK),
            ("TLS 1.2 (окремий шар)", "#eaf0fd", INK),
            ("TCP (потоковий транспорт)", "#eaf0fd", INK),
            ("IP (мережевий шар)", "#f4f6f8", INK),
        ]),
        ("HTTP/2 (TCP)", [
            ("HTTP/2 (мультиплексування)", "#fdf3e0", INK),
            ("TLS 1.2 / 1.3", "#eaf0fd", INK),
            ("TCP (єдиний кадриковий потік)", "#eaf0fd", INK),
            ("IP (мережевий шар)", "#f4f6f8", INK),
        ]),
        ("HTTP/3 (QUIC/UDP)", [
            ("HTTP/3 (кадри + QPACK)", "#fdecea", INK),
            ("QUIC (потоки + TLS 1.3)", "#fdecea", INK),
            ("UDP (датаграми)", "#eaf6ee", INK),
            ("IP (мережевий шар)", "#f4f6f8", INK),
        ])
    ]

    for idx, (title_str, layers) in enumerate(stacks):
        x = x_start + idx * (col_w + gap)
        y = 65
        p.append(text(x + col_w / 2, y, title_str, size=13, bold=True, color=INK))
        y += 18
        for label, fill, text_color in layers:
            p.append(fitbox(x, y, col_w, 52, label, size=12, fill=fill, color=text_color, bold=True))
            y += 58

    lines = [
        "HTTP/1.1 та HTTP/2 спираються на TCP, де TLS є окремим шаром над байтовим потоком.",
        "HTTP/3 переносить мультиплексування і безпеку безпосередньо в QUIC поверх UDP.",
        "Втрата одного UDP-пакета у QUIC не затримує передачу інших незалежних HTTP-потоків.",
    ]
    ty = 335
    for ln in lines:
        p.append(text(x_start, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    render(os.path.join(OUT, "quic-stack-comparison.svg"), W, H, *p)


def fig_hol_blocking():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 28, "Head-of-Line Blocking у TCP проти QUIC", size=16, bold=True))

    box_w = 380
    box_h = 240
    y0 = 65

    # TCP Box
    x_tcp = 50
    p.append(fitbox(x_tcp, y0, box_w, box_h, "", fill="#f4f6f8", stroke=LINE))
    p.append(text(x_tcp + box_w / 2, y0 + 24, "TCP (HTTP/2): Єдиний потік кадривання", size=13, bold=True, color=CLR_TCP))
    
    # TCP Packets
    p.append(fitbox(x_tcp + 20, y0 + 55, 75, 45, "Stream A\nPkt 1", size=11, fill="#eaf0fd"))
    p.append(fitbox(x_tcp + 105, y0 + 55, 75, 45, "Stream B\nPkt 2 (втрачено)", size=10, fill="#fdecea", color=POS, bold=True))
    p.append(fitbox(x_tcp + 190, y0 + 55, 75, 45, "Stream A\nPkt 3", size=11, fill="#eaf0fd"))
    p.append(fitbox(x_tcp + 275, y0 + 55, 75, 45, "Stream C\nPkt 4", size=11, fill="#eaf0fd"))

    p.append(arrow(x_tcp + 180, y0 + 115, x_tcp + 180, y0 + 150, color=POS, sw=2))
    p.append(fitbox(x_tcp + 20, y0 + 155, 340, 60, "ЗАБЛОКОВАНО ВСІ ПОТОКИ (A, B, C)!\nБуфер ядра TCP чекає на повтор Pkt 2", size=11, fill="#fdecea", color=POS, bold=True))

    # QUIC Box
    x_quic = 450
    p.append(fitbox(x_quic, y0, box_w, box_h, "", fill="#f4f6f8", stroke=LINE))
    p.append(text(x_quic + box_w / 2, y0 + 24, "QUIC (HTTP/3): Незалежні потоки", size=13, bold=True, color=CLR_QUIC))

    # QUIC Streams
    p.append(fitbox(x_quic + 20, y0 + 55, 105, 45, "Stream A: Pkt 1, 3\nОтримано", size=11, fill="#eaf6ee", color=FIELD, bold=True))
    p.append(fitbox(x_quic + 135, y0 + 55, 110, 45, "Stream B: Pkt 2\n(втрачено)", size=11, fill="#fdecea", color=POS, bold=True))
    p.append(fitbox(x_quic + 255, y0 + 55, 105, 45, "Stream C: Pkt 4\nОтримано", size=11, fill="#eaf6ee", color=FIELD, bold=True))

    p.append(arrow(x_quic + 72, y0 + 115, x_quic + 72, y0 + 150, color=FIELD, sw=2))
    p.append(arrow(x_quic + 307, y0 + 115, x_quic + 307, y0 + 150, color=FIELD, sw=2))

    p.append(fitbox(x_quic + 20, y0 + 155, 160, 60, "Stream A і C обробляються\nНЕГАЙНО без затримок", size=11, fill="#eaf6ee", color=FIELD, bold=True))
    p.append(fitbox(x_quic + 200, y0 + 155, 160, 60, "Лише Stream B чекає\nна повтор датаграми", size=11, fill="#fdecea", color=POS, bold=True))

    lines = [
        "При втраті пакета TCP змушений зупинити весь буфер до отримання повторно надісланого байта.",
        "QUIC ізолює втрати: додаток відразу читає дані з надійних потоків, не чекаючи на пошкоджений.",
    ]
    ty = 330
    for ln in lines:
        p.append(text(50, ty, ln, size=12, color=INK, anchor="start"))
        ty += 22

    render(os.path.join(OUT, "hol-blocking-comparison.svg"), W, H, *p)


def fig_handshake_timeline():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 28, "Хронологія встановитися з'єднання: TCP+TLS vs QUIC", size=16, bold=True))

    # TCP + TLS 1.3 (2 RTT)
    x1_c, x1_s = 80, 360
    y0 = 65
    p.append(text((x1_c + x1_s) / 2, y0, "TCP + TLS 1.3 (2 RTT до першого HTTP-запиту)", size=13, bold=True, color=CLR_TCP))
    p.append(line(x1_c, y0 + 20, x1_c, y0 + 250, color=MUTED, sw=2))
    p.append(line(x1_s, y0 + 20, x1_s, y0 + 250, color=MUTED, sw=2))
    p.append(text(x1_c, y0 + 15, "Клієнт", size=11, bold=True))
    p.append(text(x1_s, y0 + 15, "Сервер", size=11, bold=True))

    # TCP Handshake
    p.append(arrow(x1_c, y0 + 40, x1_s, y0 + 70, color=CLR_TCP, sw=1.8))
    p.append(text((x1_c + x1_s) / 2, y0 + 45, "TCP SYN", size=11, color=CLR_TCP))
    p.append(arrow(x1_s, y0 + 70, x1_c, y0 + 100, color=CLR_TCP, sw=1.8))
    p.append(text((x1_c + x1_s) / 2, y0 + 75, "TCP SYN-ACK", size=11, color=CLR_TCP))

    # TLS Handshake
    p.append(arrow(x1_c, y0 + 110, x1_s, y0 + 140, color=NEG, sw=1.8))
    p.append(text((x1_c + x1_s) / 2, y0 + 115, "TLS ClientHello + ACK", size=11, color=NEG))
    p.append(arrow(x1_s, y0 + 140, x1_c, y0 + 170, color=NEG, sw=1.8))
    p.append(text((x1_c + x1_s) / 2, y0 + 145, "TLS ServerHello + Finished", size=11, color=NEG))

    # HTTP Data
    p.append(arrow(x1_c, y0 + 180, x1_s, y0 + 210, color=FIELD, sw=2.2))
    p.append(text((x1_c + x1_s) / 2, y0 + 185, "HTTP GET (Дані прикладного рівня)", size=11, color=FIELD, bold=True))

    # QUIC (1 RTT / 0 RTT)
    x2_c, x2_s = 520, 800
    p.append(text((x2_c + x2_s) / 2, y0, "QUIC (1 RTT / 0 RTT злитий хендшейк)", size=13, bold=True, color=CLR_QUIC))
    p.append(line(x2_c, y0 + 20, x2_c, y0 + 250, color=MUTED, sw=2))
    p.append(line(x2_s, y0 + 20, x2_s, y0 + 250, color=MUTED, sw=2))
    p.append(text(x2_c, y0 + 15, "Клієнт", size=11, bold=True))
    p.append(text(x2_s, y0 + 15, "Сервер", size=11, bold=True))

    # Combined Handshake
    p.append(arrow(x2_c, y0 + 40, x2_s, y0 + 80, color=CLR_QUIC, sw=2))
    p.append(text((x2_c + x2_s) / 2, y0 + 48, "QUIC Initial (ClientHello + Transport Params)", size=10, color=CLR_QUIC, bold=True))
    p.append(arrow(x2_s, y0 + 80, x2_c, y0 + 120, color=CLR_QUIC, sw=2))
    p.append(text((x2_c + x2_s) / 2, y0 + 88, "QUIC Handshake (ServerHello + EE + Finished)", size=10, color=CLR_QUIC, bold=True))

    # HTTP Data in 1 RTT
    p.append(arrow(x2_c, y0 + 130, x2_s, y0 + 170, color=FIELD, sw=2.2))
    p.append(text((x2_c + x2_s) / 2, y0 + 138, "HTTP/3 GET (1 RTT / або 0-RTT з ранніми даними)", size=10, color=FIELD, bold=True))

    lines = [
        "У TCP+TLS транспортне з'єднання та криптографічний сеанс узгоджуються послідовно (2-3 RTT).",
        "QUIC передає параметри транспорту та криптографії у першому ж пакеті Initial (1 RTT).",
        "При повторному підключенні QUIC підтримує 0-RTT, передаючи HTTP-дані у першому польоті.",
    ]
    ty = 330
    for ln in lines:
        p.append(text(60, ty, ln, size=12, color=INK, anchor="start"))
        ty += 22

    render(os.path.join(OUT, "quic-handshake-timeline.svg"), W, H, *p)


def fig_connection_migration():
    W, H = 880, 410
    p = []
    p.append(text(W / 2, 28, "Переключення мережевого інтерфейсу (Connection Migration)", size=16, bold=True))

    y0 = 65
    c_w, c_h = 220, 160

    # Client
    p.append(fitbox(50, y0, c_w, c_h, "", fill="#f4f6f8", stroke=LINE))
    p.append(text(50 + c_w / 2, y0 + 24, "Мобільний клієнт", size=13, bold=True, color=INK))
    p.append(fitbox(65, y0 + 45, 190, 40, "Інтерфейс Wi-Fi\nIP: 192.168.1.5:54321", size=11, fill="#eaf0fd"))
    p.append(fitbox(65, y0 + 98, 190, 40, "Інтерфейс LTE (4G/5G)\nIP: 100.64.2.88:61000", size=11, fill="#fdecea"))

    # Server
    p.append(fitbox(610, y0, c_w, c_h, "", fill="#f4f6f8", stroke=LINE))
    p.append(text(610 + c_w / 2, y0 + 24, "Сервер HTTP/3", size=13, bold=True, color=INK))
    p.append(fitbox(625, y0 + 55, 190, 70, "QUIC Session Table\nCID: 0x8f4a2b10\nСтан сесії: ACTIVE", size=11, fill="#eaf6ee", color=FIELD, bold=True))

    # Migration Arrows
    p.append(arrow(260, y0 + 65, 600, y0 + 75, color=CLR_TCP, sw=1.8))
    p.append(text(430, y0 + 58, "1. Початковий шлях (Wi-Fi) + CID: 0x8f4a2b10", size=11, color=CLR_TCP))

    p.append(arrow(260, y0 + 118, 600, y0 + 105, color=POS, sw=2.2))
    p.append(text(430, y0 + 132, "2. Зміна мережі на LTE (новий IP:Port) + CID: 0x8f4a2b10", size=11, color=POS, bold=True))

    lines = [
        "У TCP з'єднання прив'язане до сокета (IP_src, Port_src, IP_dst, Port_dst) і рветься при зміні Wi-Fi → LTE.",
        "У QUIC з'єднання ідентифікується прозорим Connection ID (CID), що не залежить від IP-адреси.",
        "Сервер валідує новий шлях через PATH_CHALLENGE і продовжує передачу без перезапуску TLS.",
    ]
    ty = 310
    for ln in lines:
        p.append(text(50, ty, ln, size=12, color=INK, anchor="start"))
        ty += 22

    render(os.path.join(OUT, "connection-migration.svg"), W, H, *p)


def fig_packet_structure():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 28, "Будова датаграми QUIC та зв'язок зсуву і кадрів", size=16, bold=True))

    y0 = 65
    bw = 780
    x0 = 50

    # UDP Outer
    p.append(fitbox(x0, y0, bw, 50, "Заголовок UDP (8 байтів: Порт джерела, Порт призначення, Довжина, Контрольна сума)", size=12, fill="#f4f6f8", stroke=LINE))

    # QUIC Short Header Packet
    y1 = y0 + 60
    p.append(fitbox(x0, y1, 210, 50, "QUIC Short Header\n1-RTT (Flags + CID)", size=11, fill="#eaf0fd", bold=True))
    p.append(fitbox(x0 + 215, y1, 140, 50, "Packet Number\n(Монотонний №)", size=11, fill="#fdf3e0", bold=True))
    p.append(fitbox(x0 + 360, y1, 420, 50, "Зашифрований корисний вантаж (Payload + AEAD Auth Tag)", size=12, fill="#fdecea", color=POS, bold=True))

    # Inside Payload: Frames
    y2 = y1 + 60
    p.append(text(x0 + 100, y2 + 25, "Розпаковані фрейми у Payload:", size=12, bold=True, color=INK))
    p.append(fitbox(x0 + 215, y2, 260, 50, "STREAM Frame\nStream ID: 4 | Offset: 1024 | Data: 512B", size=11, fill="#eaf6ee", color=FIELD, bold=True))
    p.append(fitbox(x0 + 480, y2, 170, 50, "ACK Frame\nLargest Acked: 105", size=11, fill="#eaf0fd"))
    p.append(fitbox(x0 + 655, y2, 125, 50, "PADDING Frame", size=11, fill="#f4f6f8"))

    lines = [
        "Packet Number монотонно зростає для КОЖНОЇ датаграми (навіть при повторі) і служить для вимірювання RTT.",
        "Stream Offset відповідає за порядок даних у конкретному потіку додатка (втрачений кадри мають той самий offset).",
        "Одна UDP-датаграма QUIC може містити декілька фреймів (STREAM, ACK, MAX_DATA) одночасно.",
    ]
    ty = 310
    for ln in lines:
        p.append(text(x0, ty, ln, size=12, color=INK, anchor="start"))
        ty += 22

    render(os.path.join(OUT, "quic-packet-structure.svg"), W, H, *p)


fig_stack_comparison()
fig_hol_blocking()
fig_handshake_timeline()
fig_connection_migration()
fig_packet_structure()
print("all figures generated successfully")
