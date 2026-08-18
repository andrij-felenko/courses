# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми osi-model (Семирівнева модель OSI)."""

import os
import sys

# Додаємо шлях до scripts для імпорту svgkit
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "scripts"
    ),
)
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_osi_7_layers():
    """Фігура 1: Семирівнева еталонна модель OSI (ISO/IEC 7498-1)."""
    w, h = 880, 520
    frags = []

    layers = [
        ("L7", "Прикладний (Application)", "APDU", "#e8f4fd", "#1b6ca8"),
        ("L6", "Представницький (Presentation)", "PPDU", "#edf7ed", "#2e7d32"),
        ("L5", "Сеансовий (Session)", "SPDU", "#fff4e5", "#ed6c02"),
        ("L4", "Транспортний (Transport)", "TPDU (Сегмент)", "#fce4ec", "#c2185b"),
        ("L3", "Мережевий (Network)", "Пакет (Packet)", "#f3e5f5", "#7b1fa2"),
        ("L2", "Канальний (Data Link)", "Кадр (Frame)", "#e0f2f1", "#00796b"),
        ("L1", "Фізичний (Physical)", "Біт (Bit stream)", "#eceff1", "#455a64"),
    ]

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Семирівнева еталонна модель OSI (ISO/IEC 7498-1)", size=17, bold=True))

    box_w = 260
    box_h = 44
    gap_y = 12
    start_y = 65

    frags.append(text(170, start_y - 12, "Кінцева система A (Host A)", size=14, bold=True))
    frags.append(text(710, start_y - 12, "Кінцева система B (Host B)", size=14, bold=True))

    # Малюємо 7 рівнів для Системи A та B
    for i, (lvl, name, pdu, fill_c, stroke_c) in enumerate(layers):
        y = start_y + i * (box_h + gap_y)

        # Host A
        frags.append(rect(40, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        frags.append(text(60, y + 27, lvl, size=13, bold=True, color=stroke_c))
        frags.append(text(175, y + 27, name, size=12, bold=False, color=INK))

        # Host B
        frags.append(rect(580, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        frags.append(text(600, y + 27, lvl, size=13, bold=True, color=stroke_c))
        frags.append(text(715, y + 27, name, size=12, bold=False, color=INK))

        # Віртуальні зв'язки між рівнями (dotted horizontal lines)
        if i < 3:
            # L7..L5 Наскрізні прикладні
            frags.append(line(305, y + box_h / 2, 575, y + box_h / 2, color=stroke_c, sw=1.2, dash="4,4"))
            frags.append(text(440, y + box_h / 2 - 4, f"Віртуальний протокол {lvl} ({pdu})", size=10, color=stroke_c))
        elif i == 3:
            # L4 Наскрізний транспорт
            frags.append(line(305, y + box_h / 2, 575, y + box_h / 2, color=stroke_c, sw=1.5, dash="5,3"))
            frags.append(text(440, y + box_h / 2 - 4, f"Наскрізний транспорт L4 ({pdu})", size=11, bold=True, color=stroke_c))

    # Центральний вузол: Маршрутизатор (Intermediate System, L1-L3)
    router_x = 350
    router_w = 180
    frags.append(rect(router_x, start_y + 3 * (box_h + gap_y) + 14, router_w, 3 * box_h + 2 * gap_y + 12, fill="none", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(router_x + router_w / 2, start_y + 3 * (box_h + gap_y) + 28, "Проміжний вузол (L3-Router)", size=10.5, bold=True, color=MUTED))

    for idx, i in enumerate([4, 5, 6]):
        lvl, name, pdu, fill_c, stroke_c = layers[i]
        ry = start_y + i * (box_h + gap_y)
        frags.append(rect(router_x + 10, ry, router_w - 20, box_h, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(router_x + router_w / 2, ry + 27, f"{lvl}: {name.split()[0]}", size=11, bold=True, color=stroke_c))

    # Стрілки передачі через проміжний вузол (Hop-by-hop)
    frags.append(line(170, start_y + 7 * (box_h + gap_y) - gap_y, 170, 485, color=LINE, sw=2))
    frags.append(line(170, 485, 440, 485, color=LINE, sw=2))
    frags.append(line(440, 485, 440, start_y + 7 * (box_h + gap_y) - gap_y, color=LINE, sw=2))
    frags.append(line(440, 485, 710, 485, color=LINE, sw=2))
    frags.append(line(710, 485, 710, start_y + 7 * (box_h + gap_y) - gap_y, color=LINE, sw=2))

    frags.append(rect(320, 470, 240, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(440, 489, "Фізичне середовище (кабель / ефір)", size=11, bold=True))

    # Вертикальні стрілки інкапсуляції / декапсуляції
    frags.append(arrow(20, start_y + 40, 20, start_y + 360, color=POS, sw=1.8))
    frags.append(text(20, start_y + 390, "Вниз", size=11, bold=True, color=POS))
    frags.append(text(20, start_y + 20, "Спуск", size=11, color=MUTED))

    frags.append(arrow(860, start_y + 360, 860, start_y + 40, color=NEG, sw=1.8))
    frags.append(text(860, start_y + 20, "Підйом", size=11, bold=True, color=NEG))
    frags.append(text(860, start_y + 390, "Вгору", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "osi-7-layers-architecture.svg"), w, h, *frags)


def fig_encapsulation_pdu_sap():
    """Фігура 2: Інкапсуляція даних, блоки PDU/SDU та точки SAP."""
    w, h = 900, 500
    frags = []

    frags.append(text(w / 2, 28, "Інкапсуляція даних та точки доступу до послуг (SAP)", size=17, bold=True))

    steps = [
        ("L7 Прикладний", "Дані програми", "L7-PDU (APDU)", 240, "#e8f4fd", "#1b6ca8"),
        ("L6 Представницький", "PH | Дані програми", "L6-PDU (PPDU)", 290, "#edf7ed", "#2e7d32"),
        ("L5 Сеансовий", "SH | PH | Дані програми", "L5-PDU (SPDU)", 340, "#fff4e5", "#ed6c02"),
        ("L4 Транспортний", "TH | SH | PH | Дані програми", "L4-PDU (Сегмент)", 400, "#fce4ec", "#c2185b"),
        ("L3 Мережевий", "NH | TH | SH | PH | Дані", "L3-PDU (Пакет)", 450, "#f3e5f5", "#7b1fa2"),
        ("L2 Канальний", "DH | NH | TH | SH | Дані | DT", "L2-PDU (Кадр)", 500, "#e0f2f1", "#00796b"),
    ]

    saps = [
        "PSAP (Presentation SAP)",
        "SSAP (Session SAP)",
        "TSAP (Transport SAP / Port)",
        "NSAP (Network SAP / IP)",
        "LSAP (Link SAP / MAC-тип)",
    ]

    start_y = 65
    row_h = 50
    gap = 20

    for i, (lvl_name, pdu_content, pdu_name, block_w, fill_c, stroke_c) in enumerate(steps):
        y = start_y + i * (row_h + gap)

        # Лівий напис рівня
        frags.append(rect(20, y, 160, row_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
        frags.append(text(100, y + 30, lvl_name, size=12, bold=True))

        # Центральний блок інкапсульованого PDU
        cx = 450
        bx = cx - block_w / 2
        frags.append(rect(bx, y, block_w, row_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        frags.append(text(cx, y + 22, pdu_content, size=11.5, bold=True, color=INK))
        frags.append(text(cx, y + 38, f"SDU + PCI = {pdu_name}", size=10, color=stroke_c))

        # Правий підпис PDU
        frags.append(rect(720, y, 160, row_h, fill=fill_c, stroke=stroke_c, sw=1.2, rx=5))
        frags.append(text(800, y + 30, pdu_name.split()[0], size=12, bold=True, color=stroke_c))

        # Стрілки та SAP між рівнями
        if i < len(steps) - 1:
            arrow_y1 = y + row_h
            arrow_y2 = arrow_y1 + gap
            frags.append(arrow(cx, arrow_y1, cx, arrow_y2, color=POS, sw=1.5))
            sap_name = saps[i]
            frags.append(text(cx + 120, arrow_y1 + 13, f"Точка доступу: {sap_name}", size=9, color=MUTED))

    # Нижній рівень L1 Фізичний
    y_l1 = start_y + len(steps) * (row_h + gap)
    frags.append(rect(20, y_l1, 160, 36, fill="#eceff1", stroke="#455a64", sw=1.2, rx=5))
    frags.append(text(100, y_l1 + 23, "L1 Фізичний", size=12, bold=True, color="#455a64"))

    frags.append(rect(200, y_l1, 500, 36, fill="#263238", stroke=LINE, sw=1.5, rx=5))
    frags.append(text(450, y_l1 + 23, "Потік бітів: 0 1 1 0 1 0 0 1 0 1 1 1 0 1 0 0 1 1 0 0 1 ...", size=12, bold=True, color="#81d4fa"))

    frags.append(rect(720, y_l1, 160, 36, fill="#eceff1", stroke="#455a64", sw=1.2, rx=5))
    frags.append(text(800, y_l1 + 23, "Біти", size=12, bold=True, color="#455a64"))

    render(os.path.join(IMG_DIR, "encapsulation-pdu-sap.svg"), w, h, *frags)


def fig_osi_vs_tcpip_stacks():
    """Фігура 3: Порівняння рівнів OSI, TCP/IP та гібридної 5-рівневої моделі."""
    w, h = 880, 480
    frags = []

    frags.append(text(w / 2, 28, "Порівняння архітектурних моделей: OSI, TCP/IP та гібридна модель", size=17, bold=True))

    col_w = 230
    start_y = 70
    h_layer = 46
    gap = 8

    # Колонка 1: OSI 7-Layer Model
    c1_x = 50
    frags.append(text(c1_x + col_w / 2, start_y - 12, "Модель OSI (7 рівнів)", size=14, bold=True, color="#1b6ca8"))

    osi_layers = [
        ("L7 Прикладний", "FTAM, X.400, X.500, CMIP", "#e8f4fd", "#1b6ca8"),
        ("L6 Представницький", "ASN.1, BER, XDR", "#edf7ed", "#2e7d32"),
        ("L5 Сеансовий", "ISO Session, RPC Dialogs", "#fff4e5", "#ed6c02"),
        ("L4 Транспортний", "TP0, TP1, TP2, TP3, TP4", "#fce4ec", "#c2185b"),
        ("L3 Мережевий", "CLNP, CONP, IS-IS, ES-IS", "#f3e5f5", "#7b1fa2"),
        ("L2 Канальний", "HDLC, LAPB, 802.2/802.3", "#e0f2f1", "#00796b"),
        ("L1 Фізичний", "V.24, V.35, RS-232, 10BASE5", "#eceff1", "#455a64"),
    ]

    for i, (name, protos, fill_c, stroke_c) in enumerate(osi_layers):
        y = start_y + i * (h_layer + gap)
        frags.append(rect(c1_x, y, col_w, h_layer, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        frags.append(text(c1_x + col_w / 2, y + 20, name, size=12, bold=True, color=stroke_c))
        frags.append(text(c1_x + col_w / 2, y + 36, protos, size=9.5, color=INK))

    # Колонка 2: TCP/IP Стек (4 рівні)
    c2_x = 325
    frags.append(text(c2_x + col_w / 2, start_y - 12, "Стек TCP/IP (4 рівні)", size=14, bold=True, color="#c2185b"))

    # L4 TCP/IP = L7+L6+L5 OSI
    y_app = start_y
    h_app = 3 * h_layer + 2 * gap
    frags.append(rect(c2_x, y_app, col_w, h_app, fill="#e8f4fd", stroke="#1b6ca8", sw=2, rx=6))
    frags.append(text(c2_x + col_w / 2, y_app + 45, "Прикладний рівень", size=14, bold=True, color="#1b6ca8"))
    frags.append(text(c2_x + col_w / 2, y_app + 70, "HTTP/3, HTTPS, DNS, SSH, gRPC", size=11, bold=True))
    frags.append(text(c2_x + col_w / 2, y_app + 95, "Форматування (JSON/Protobuf) та сесії", size=10, color=MUTED))
    frags.append(text(c2_x + col_w / 2, y_app + 115, "вбудовані в бібліотеки застосунку", size=10, color=MUTED))

    # Транспортний
    y_trans = start_y + 3 * (h_layer + gap)
    frags.append(rect(c2_x, y_trans, col_w, h_layer, fill="#fce4ec", stroke="#c2185b", sw=1.5, rx=5))
    frags.append(text(c2_x + col_w / 2, y_trans + 20, "Транспортний", size=12, bold=True, color="#c2185b"))
    frags.append(text(c2_x + col_w / 2, y_trans + 36, "TCP, UDP, QUIC, SCTP", size=10, bold=True))

    # Міжмережевий
    y_net = start_y + 4 * (h_layer + gap)
    frags.append(rect(c2_x, y_net, col_w, h_layer, fill="#f3e5f5", stroke="#7b1fa2", sw=1.5, rx=5))
    frags.append(text(c2_x + col_w / 2, y_net + 20, "Міжмережевий (Internet)", size=12, bold=True, color="#7b1fa2"))
    frags.append(text(c2_x + col_w / 2, y_net + 36, "IPv4, IPv6, ICMP, IPsec, BGP", size=10, bold=True))

    # Мережевого доступу = L2 + L1 OSI
    y_link = start_y + 5 * (h_layer + gap)
    h_link = 2 * h_layer + gap
    frags.append(rect(c2_x, y_link, col_w, h_link, fill="#e0f2f1", stroke="#00796b", sw=1.5, rx=5))
    frags.append(text(c2_x + col_w / 2, y_link + 35, "Рівень мережевого доступу", size=12, bold=True, color="#00796b"))
    frags.append(text(c2_x + col_w / 2, y_link + 58, "Ethernet (802.3), Wi-Fi (802.11), LTE/5G", size=10, bold=True))
    frags.append(text(c2_x + col_w / 2, y_link + 78, "Драйвери мережевих карт, MAC/PHY", size=10, color=MUTED))

    # Колонка 3: Сучасна гібридна навчальна модель (5 рівнів)
    c3_x = 600
    frags.append(text(c3_x + col_w / 2, start_y - 12, "Гібридна модель (5 рівнів)", size=14, bold=True, color="#2e7d32"))

    hybrid_layers = [
        ("5. Прикладний", "HTTP, DNS, SSH, TLS", h_app, "#e8f4fd", "#1b6ca8"),
        ("4. Транспортний", "TCP, UDP, QUIC", h_layer, "#fce4ec", "#c2185b"),
        ("3. Мережевий", "IP (IPv4/IPv6), Маршрутизація", h_layer, "#f3e5f5", "#7b1fa2"),
        ("2. Канальний", "Кадри Ethernet, MAC-адреси", h_layer, "#e0f2f1", "#00796b"),
        ("1. Фізичний", "Мідь, оптика, радіоефір", h_layer, "#eceff1", "#455a64"),
    ]

    cur_y = start_y
    for name, desc, lh, fill_c, stroke_c in hybrid_layers:
        frags.append(rect(c3_x, cur_y, col_w, lh, fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        if lh > 60:
            frags.append(text(c3_x + col_w / 2, cur_y + 45, name, size=13, bold=True, color=stroke_c))
            frags.append(text(c3_x + col_w / 2, cur_y + 70, desc, size=11, bold=True))
            frags.append(text(c3_x + col_w / 2, cur_y + 95, "Охоплює функції L5-L7 OSI", size=10, color=MUTED))
        else:
            frags.append(text(c3_x + col_w / 2, cur_y + 20, name, size=12, bold=True, color=stroke_c))
            frags.append(text(c3_x + col_w / 2, cur_y + 36, desc, size=10, color=INK))
        cur_y += lh + gap

    render(os.path.join(IMG_DIR, "osi-vs-tcpip-stacks.svg"), w, h, *frags)


def fig_curved_hourglass_effect():
    """Фігура 4: Пісочний годинник TCP/IP проти моделі висячого моста OSI."""
    w, h = 860, 460
    frags = []

    frags.append(text(w / 2, 28, "Архітектурний контраст: «Пісочний годинник» TCP/IP та «Роздутий стос» OSI", size=16, bold=True))

    # Ліва половина: Пісочний годинник TCP/IP
    left_cx = 220
    frags.append(text(left_cx, 65, "Стек TCP/IP («Вузька талія»)", size=14, bold=True, color="#2e7d32"))

    # Верхній широкий блок (Застосунки)
    frags.append(rect(left_cx - 160, 85, 320, 70, fill="#e8f4fd", stroke="#1b6ca8", sw=1.5, rx=6))
    frags.append(text(left_cx, 112, "Безліч прикладних застосунків", size=13, bold=True, color="#1b6ca8"))
    frags.append(text(left_cx, 134, "Web, Video streaming, Mail, DNS, P2P, Ігри, SSH", size=10.5))

    # Звуження: Транспорт
    frags.append(rect(left_cx - 100, 165, 200, 45, fill="#fce4ec", stroke="#c2185b", sw=1.5, rx=5))
    frags.append(text(left_cx, 185, "Транспортний шар", size=11, bold=True, color="#c2185b"))
    frags.append(text(left_cx, 200, "TCP, UDP, QUIC", size=10))

    # Найвужча талія: IP (The Thin Waist)
    frags.append(rect(left_cx - 60, 220, 120, 50, fill="#f3e5f5", stroke="#7b1fa2", sw=2.5, rx=5))
    frags.append(text(left_cx, 243, "IP (v4 / v6)", size=15, bold=True, color="#7b1fa2"))
    frags.append(text(left_cx, 260, "Єдиний шлюз", size=10, color=MUTED))

    # Розширення донизу: Фізичні середовища
    frags.append(rect(left_cx - 160, 280, 320, 70, fill="#e0f2f1", stroke="#00796b", sw=1.5, rx=6))
    frags.append(text(left_cx, 307, "Безліч фізичних середовищ", size=13, bold=True, color="#00796b"))
    frags.append(text(left_cx, 330, "Оптоволокно, Ethernet, Wi-Fi, 4G/5G, Супутник", size=10.5))

    frags.append(rect(left_cx - 170, 365, 340, 65, fill="#f8fafc", stroke="#2e7d32", sw=1.2, rx=6))
    frags.append(text(left_cx, 388, "Головна перевага:", size=11, bold=True, color="#2e7d32"))
    frags.append(text(left_cx, 406, "Будь-який застосунок працює поверх будь-якого заліза,", size=10))
    frags.append(text(left_cx, 421, "бо всі сходяться в єдиній точці — протоколі IP", size=10))

    # Розділювач
    frags.append(line(430, 60, 430, 440, color=LINE, sw=1, dash="4,4"))

    # Права половина: Стек OSI
    right_cx = 640
    frags.append(text(right_cx, 65, "Стек OSI («Важкий моноліт»)", size=14, bold=True, color="#c0392b"))

    osi_blocks = [
        ("L7 Прикладний", "FTAM, X.400, X.500, CMIP, VT, CCR (сотні опцій)", "#e8f4fd", "#1b6ca8"),
        ("L6 Представницький", "ASN.1, BER, PER, складне дерево типів", "#edf7ed", "#2e7d32"),
        ("L5 Сеансовий", "Токени діалогу, контрольні точки, відкоти", "#fff4e5", "#ed6c02"),
        ("L4 Транспортний", "5 класів транспорту: TP0, TP1, TP2, TP3, TP4", "#fce4ec", "#c2185b"),
        ("L3 Мережевий", "CLNP (дейтаграми) проти CONP/X.25 (з'єднання)", "#f3e5f5", "#7b1fa2"),
        ("L2 Канальний", "HDLC, LAPB, 802.2 LLC Type 1/2/3", "#e0f2f1", "#00796b"),
    ]

    for i, (lvl, desc, fill_c, stroke_c) in enumerate(osi_blocks):
        by = 85 + i * 44
        frags.append(rect(right_cx - 170, by, 340, 38, fill=fill_c, stroke=stroke_c, sw=1.2, rx=5))
        frags.append(text(right_cx, by + 16, lvl, size=11, bold=True, color=stroke_c))
        frags.append(text(right_cx, by + 30, desc, size=9.5, color=INK))

    frags.append(rect(right_cx - 170, 365, 340, 65, fill="#fdf2f2", stroke="#c0392b", sw=1.2, rx=6))
    frags.append(text(right_cx, 388, "Головний провал:", size=11, bold=True, color="#c0392b"))
    frags.append(text(right_cx, 406, "Немає вузької талії: суперечливі стандарти на кожному", size=10))
    frags.append(text(right_cx, 421, "рівні породили несумісність та надмірні обчислювальні витрати", size=10))

    render(os.path.join(IMG_DIR, "curved-hourglass-effect.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_osi_7_layers()
    fig_encapsulation_pdu_sap()
    fig_osi_vs_tcpip_stacks()
    fig_curved_hourglass_effect()
    print("Всі 4 фігури згенеровано успішно.")
