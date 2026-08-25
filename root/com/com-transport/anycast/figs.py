# -*- coding: utf-8 -*-
"""Фігури до теми «Anycast і глобальне балансування трафіку».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# 1. Порівняння моделей передавання: Unicast, Broadcast, Multicast, Anycast
def fig_anycast_vs_unicast_multicast():
    W, H = 860, 480
    f = [text(W / 2, 28, "Чотири парадигми адресації та маршрутизації в IP-мережах", size=15, bold=True)]

    panels = [
        ("Unicast (один до одного)", 20, 60, 195, 395, [
            "Адреса належить",
            "рівно одному інтерфейсу.",
            "Маршрут веде до єдиного",
            "фізичного вузла в мережі."
        ], "#edf4ff", NEG),
        ("Broadcast (один до всіх)", 230, 60, 195, 395, [
            "Пакет копіюється всім",
            "вузлам у межах одного",
            "L2-домену мовлення.",
            "Не виходить за маршрутизатор."
        ], "#fff7e6", MUTED),
        ("Multicast (один до групи)", 440, 60, 195, 395, [
            "Пакет доставляється групі",
            "підписників через дерево",
            "розподілу (IGMP / PIM).",
            "Ефективно для потокового відео."
        ], "#eafaf0", FIELD),
        ("Anycast (один до найближчого)", 650, 60, 195, 395, [
            "Одна адреса анонсується",
            "багатьма вузлами одночасно.",
            "Мережа спрямовує пакет до",
            "найближчого за метрикою BGP."
        ], "#fdf2f2", POS),
    ]

    for title_text, px, py, pw, ph, desc_lines, bg_col, stroke_col in panels:
        f.append(rect(px, py, pw, ph, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        f.append(text(px + pw / 2, py + 24, title_text, size=11, bold=True, color=stroke_col))

        # Джерело
        f.append(rect(px + 15, py + 55, 60, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(px + 45, py + 74, "Клієнт", size=10, bold=True))

        # Призначення
        if title_text.startswith("Unicast"):
            f.append(rect(px + 105, py + 120, 75, 30, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
            f.append(text(px + 142, py + 140, "Сервер A", size=10, bold=True, color=NEG))
            f.append(arrow(px + 75, py + 70, px + 105, py + 125, color=NEG, sw=1.8))

            f.append(rect(px + 105, py + 180, 75, 30, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
            f.append(text(px + 142, py + 200, "Сервер B", size=10, color=MUTED))

        elif title_text.startswith("Broadcast"):
            f.append(rect(px + 105, py + 100, 75, 26, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
            f.append(text(px + 142, py + 117, "Вузол 1", size=10, bold=True))
            f.append(rect(px + 105, py + 140, 75, 26, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
            f.append(text(px + 142, py + 157, "Вузол 2", size=10, bold=True))
            f.append(rect(px + 105, py + 180, 75, 26, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
            f.append(text(px + 142, py + 197, "Вузол 3", size=10, bold=True))

            f.append(arrow(px + 75, py + 70, px + 105, py + 110, color=MUTED, sw=1.4))
            f.append(arrow(px + 75, py + 70, px + 105, py + 150, color=MUTED, sw=1.4))
            f.append(arrow(px + 75, py + 70, px + 105, py + 190, color=MUTED, sw=1.4))

        elif title_text.startswith("Multicast"):
            f.append(rect(px + 105, py + 100, 75, 26, fill="#ffffff", stroke=FIELD, sw=1.4, rx=4))
            f.append(text(px + 142, py + 117, "Член гр. 1", size=10, bold=True, color=FIELD))
            f.append(rect(px + 105, py + 140, 75, 26, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
            f.append(text(px + 142, py + 157, "Не підпис.", size=9, color=MUTED))
            f.append(rect(px + 105, py + 180, 75, 26, fill="#ffffff", stroke=FIELD, sw=1.4, rx=4))
            f.append(text(px + 142, py + 197, "Член гр. 2", size=10, bold=True, color=FIELD))

            f.append(arrow(px + 75, py + 70, px + 105, py + 110, color=FIELD, sw=1.5))
            f.append(arrow(px + 75, py + 70, px + 105, py + 190, color=FIELD, sw=1.5))

        else: # Anycast
            f.append(rect(px + 105, py + 100, 75, 28, fill="#ffffff", stroke=POS, sw=1.8, rx=4))
            f.append(text(px + 142, py + 118, "PoP Токіо", size=10, bold=True, color=POS))
            f.append(rect(px + 105, py + 145, 75, 28, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
            f.append(text(px + 142, py + 163, "PoP Франкф.", size=9, color=MUTED))
            f.append(rect(px + 105, py + 185, 75, 28, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
            f.append(text(px + 142, py + 203, "PoP Ашберн", size=9, color=MUTED))

            f.append(arrow(px + 75, py + 70, px + 105, py + 112, color=POS, sw=2.0))
            f.append(text(px + 78, py + 102, "RTT 5ms", size=9, bold=True, color=POS))

        # Опис унизу
        f.append(fitbox(px + 8, py + 235, pw - 16, 145, "\n".join(desc_lines), size=10,
                        fill="#ffffff", stroke=LINE, sw=0.8, color=INK))

    render(os.path.join(IMG, "anycast-vs-unicast-multicast.svg"), W, H, *f)


# 2. Глобальні зони притягання (Anycast catchments) та вибір BGP-маршруту
def fig_bgp_anycast_catchment():
    W, H = 860, 480
    f = [text(W / 2, 28, "BGP Anycast: топологічні басейни притягання (Catchments) для префікса 198.51.100.0/24", size=14, bold=True)]

    # PoP Nodes (Edge Data Centers)
    pops = [
        ("PoP Франкфурт (EU)", 60, 65, 220, 115, "#eef3ff", NEG, "198.51.100.0/24\nASN: 13335\nAS_PATH: [13335]"),
        ("PoP Ашберн (US-East)", 320, 65, 220, 115, "#eafaf0", FIELD, "198.51.100.0/24\nASN: 13335\nAS_PATH: [13335]"),
        ("PoP Токіо (APAC)", 580, 65, 220, 115, "#fff7e6", POS, "198.51.100.0/24\nASN: 13335\nAS_PATH: [13335]"),
    ]

    for title_txt, x, y, w, h, bg, stroke_col, body_txt in pops:
        f.append(rect(x, y, w, h, fill=bg, stroke=stroke_col, sw=1.6, rx=8))
        f.append(text(x + w / 2, y + 22, title_txt, size=11, bold=True, color=stroke_col))
        f.append(fitbox(x + 10, y + 36, w - 20, 68, body_txt, size=10, fill="#ffffff", stroke=LINE, sw=0.8, color=INK))

    # Internet Transit / Autonomous Systems Layer
    f.append(rect(50, 230, 760, 75, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    f.append(text(W / 2, 252, "Глобальна транзитна мережа Інтернет (Tier-1 / Tier-2 ISP)", size=12, bold=True))
    f.append(text(W / 2, 278, "Кожен провайдер обирає найкращий шлях за правилами BGP Best Path (найкоротший AS_PATH / найменший IGP Cost)", size=10, color=MUTED))

    # Clients Layer
    clients = [
        ("Користувач у Берліні", 60, 360, 220, 85, "Запит до 198.51.100.1\nМаршрут: AS3320 -> AS13335 (EU)\nRTT = 8 мс", NEG),
        ("Користувач у Чикаго", 320, 360, 220, 85, "Запит до 198.51.100.1\nМаршрут: AS701 -> AS13335 (US)\nRTT = 14 мс", FIELD),
        ("Користувач у Сеулі", 580, 360, 220, 85, "Запит до 198.51.100.1\nМаршрут: AS4766 -> AS13335 (JP)\nRTT = 18 мс", POS),
    ]

    for title_txt, x, y, w, h, body_txt, col in clients:
        f.append(rect(x, y, w, h, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        f.append(text(x + w / 2, y + 20, title_txt, size=11, bold=True, color=col))
        f.append(fitbox(x + 8, y + 30, w - 16, 48, body_txt, size=10, fill="#fdfefe", stroke=MUTED, sw=0.6, color=INK))

    # Arrows from clients to transit
    f.append(arrow(170, 360, 170, 305, color=NEG, sw=1.8))
    f.append(arrow(430, 360, 430, 305, color=FIELD, sw=1.8))
    f.append(arrow(690, 360, 690, 305, color=POS, sw=1.8))

    # Arrows from transit to PoPs
    f.append(arrow(170, 230, 170, 180, color=NEG, sw=1.8))
    f.append(arrow(430, 230, 430, 180, color=FIELD, sw=1.8))
    f.append(arrow(690, 230, 690, 180, color=POS, sw=1.8))

    render(os.path.join(IMG, "bgp-anycast-catchment.svg"), W, H, *f)


# 3. Захист від DDoS-атак через Anycast Sinkholing
def fig_ddos_traffic_sinkholing():
    W, H = 880, 490
    f = [text(W / 2, 26, "Розсіювання об'ємної DDoS-атаки (Anycast Sinkholing) проти Unicast", size=14, bold=True)]

    # Left Side: Unicast Under Attack
    f.append(rect(20, 50, 410, 420, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(225, 75, "Традиційний Unicast (Один дата-центр)", size=12, bold=True, color=POS))

    f.append(rect(40, 100, 150, 55, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(115, 120, "Ботнет США", size=10, bold=True, color=POS))
    f.append(text(115, 138, "350 Гбіт/с атаки", size=9, color=MUTED))

    f.append(rect(260, 100, 150, 55, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(335, 120, "Ботнет Європа", size=10, bold=True, color=POS))
    f.append(text(335, 138, "450 Гбіт/с атаки", size=9, color=MUTED))

    f.append(rect(150, 175, 150, 55, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(225, 195, "Ботнет Азія", size=10, bold=True, color=POS))
    f.append(text(225, 213, "300 Гбіт/с атаки", size=9, color=MUTED))

    # Converging arrows
    f.append(arrow(115, 155, 180, 260, color=POS, sw=2.0))
    f.append(arrow(335, 155, 270, 260, color=POS, sw=2.0))
    f.append(arrow(225, 230, 225, 260, color=POS, sw=2.0))

    f.append(rect(80, 260, 290, 75, fill="#ffffff", stroke=POS, sw=2.0, rx=6))
    f.append(text(225, 282, "Єдиний Origin Сервер (Unicast)", size=11, bold=True, color=POS))
    f.append(text(225, 302, "Канал 100 Гбіт/с перевантажено!", size=10, bold=True, color=POS))
    f.append(text(225, 320, "Сумарно 1.1 Тбіт/с -> 100% ВІДМОВА", size=9, color=POS))

    f.append(fitbox(35, 350, 380, 105,
                    "Результат: локальний аплінк повністю\n"
                    "забитий сміттєвими пакетами атаки;\n"
                    "легітимні клієнти у всьому світі\n"
                    "не можуть встановити з'єднання.",
                    size=10, fill="#ffffff", stroke=LINE, sw=0.8))

    # Right Side: Anycast Sinkholing
    f.append(rect(450, 50, 410, 420, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(655, 75, "Розподілений Anycast (Глобальна мережа PoP)", size=12, bold=True, color=FIELD))

    # 3 PoP nodes
    f.append(rect(470, 100, 115, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(527, 120, "PoP Ашберн", size=10, bold=True, color=FIELD))
    f.append(text(527, 140, "Ботнет US: 350G", size=9, color=POS))
    f.append(text(527, 158, "Фільтр: L3/L4 BPF", size=9, color=MUTED))

    f.append(rect(598, 100, 115, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(655, 120, "PoP Франкфурт", size=10, bold=True, color=FIELD))
    f.append(text(655, 140, "Ботнет EU: 450G", size=9, color=POS))
    f.append(text(655, 158, "Фільтр: L3/L4 BPF", size=9, color=MUTED))

    f.append(rect(725, 100, 115, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(782, 120, "PoP Сінгапур", size=10, bold=True, color=FIELD))
    f.append(text(782, 140, "Ботнет Asia: 300G", size=9, color=POS))
    f.append(text(782, 158, "Фільтр: L3/L4 BPF", size=9, color=MUTED))

    f.append(arrow(527, 175, 610, 260, color=FIELD, sw=1.4))
    f.append(arrow(655, 175, 655, 260, color=FIELD, sw=1.4))
    f.append(arrow(782, 175, 700, 260, color=FIELD, sw=1.4))

    f.append(rect(510, 260, 290, 75, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(655, 282, "Origin Дата-Центр (Захищений)", size=11, bold=True, color=FIELD))
    f.append(text(655, 302, "Очищений трафік: лише 50 Мбіт/с", size=10, bold=True, color=FIELD))
    f.append(text(655, 320, "DDoS локалізовано й поглинуто на Edge", size=9, color=MUTED))

    f.append(fitbox(465, 350, 380, 105,
                    "Результат: трафік атаки розсіюється по\n"
                    "регіональних вузлах і фільтрується на краю;\n"
                    "легітимні клієнти продовжують працювати\n"
                    "з найближчим справним PoP.",
                    size=10, fill="#ffffff", stroke=LINE, sw=0.8))

    render(os.path.join(IMG, "ddos-traffic-sinkholing.svg"), W, H, *f)


# 4. Проблема BGP Route Flapping у TCP та балансування Maglev Consistent Hashing
def fig_tcp_flapping_and_maglev_ecmp():
    W, H = 860, 520
    f = [text(W / 2, 26, "Проблема зміни маршруту (BGP Flap) у TCP та її вирішення через Maglev і QUIC", size=14, bold=True)]

    # Top Half: Flapping problem
    f.append(rect(20, 50, 820, 215, fill="#fdf2f2", stroke=POS, sw=1.4, rx=8))
    f.append(text(210, 72, "Проблема: BGP Route Flap під час активної сесії TCP", size=12, bold=True, color=POS))

    f.append(rect(40, 95, 140, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(110, 118, "Клієнт", size=11, bold=True))
    f.append(text(110, 138, "TCP 198.51.100.1", size=10, color=MUTED))

    f.append(rect(340, 90, 210, 70, fill="#ffffff", stroke=NEG, sw=1.4, rx=6))
    f.append(text(445, 112, "PoP 1 (Франкфурт)", size=11, bold=True, color=NEG))
    f.append(text(445, 132, "TCP State: ESTABLISHED", size=10, color=MUTED))
    f.append(text(445, 148, "Seq: 10420, Ack: 501", size=9, color=MUTED))

    f.append(rect(610, 90, 210, 70, fill="#ffffff", stroke=POS, sw=1.4, rx=6))
    f.append(text(715, 112, "PoP 2 (Лондон)", size=11, bold=True, color=POS))
    f.append(text(715, 132, "НЕМАЄ TCP стану!", size=10, bold=True, color=POS))
    f.append(text(715, 148, "Відповідь: TCP RST (скидання)", size=9, color=POS))

    # Two arrows with plenty of spacing
    f.append(arrow(180, 110, 340, 110, color=NEG, sw=1.8))
    f.append(text(260, 102, "1. SYN, SYN-ACK", size=9, bold=True, color=NEG))

    f.append(arrow(180, 140, 610, 140, color=POS, sw=1.8))
    f.append(text(260, 155, "2. BGP flap -> DATA", size=9, bold=True, color=POS))

    f.append(fitbox(40, 175, 780, 75,
                    "Коли проміжний лінк падає або перераховується BGP AS-Path, наступний пакет сесії\n"
                    "потрапляє на інший PoP. Без синхронізації або узгодженого хешування новий сервер\n"
                    "не знає стану сесії й надсилає клієнту TCP RST, перериваючи передачу.",
                    size=10, fill="#ffffff", stroke=POS, sw=0.8))

    # Bottom Half: Maglev consistent hashing & QUIC CID
    f.append(rect(20, 280, 820, 225, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(275, 304, "Архітектурні рішення: Maglev Consistent Hashing та QUIC Connection ID", size=12, bold=True, color=FIELD))

    # Three solution columns (using rect and multi-line texts without nested colliding fitbox rects)
    f.append(rect(40, 325, 235, 95, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(157, 348, "1. Балансувальник Maglev", size=11, bold=True, color=FIELD))
    f.append(text(157, 370, "Таблиця розміром M (просте).", size=9, color=INK))
    f.append(text(157, 386, "5-tuple стабільно хешується", size=9, color=INK))
    f.append(text(157, 402, "на той самий бекенд-вузол.", size=9, color=INK))

    f.append(rect(310, 325, 235, 95, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(427, 348, "2. Тунелювання DSR / GRE", size=11, bold=True, color=FIELD))
    f.append(text(427, 370, "L4-проксі інкапсулює пакет", size=9, color=INK))
    f.append(text(427, 386, "у GRE/Geneve до вузла;", size=9, color=INK))
    f.append(text(427, 402, "відповідь іде клієнту напряму.", size=9, color=INK))

    f.append(rect(580, 325, 240, 95, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(700, 348, "3. Протокол QUIC (RFC 9000)", size=11, bold=True, color=FIELD))
    f.append(text(700, 370, "Connection ID (CID) замість IP:Port.", size=9, color=INK))
    f.append(text(700, 386, "Зміна маршруту чи IP-адреси", size=9, color=INK))
    f.append(text(700, 402, "не розриває транспортний потік.", size=9, color=INK))

    f.append(fitbox(40, 430, 780, 62,
                    "Завдяки узгодженому розподілу таблиць Maglev усі PoP однаково відображають клієнтські 5-tuple\n"
                    "на бекенди, а QUIC усуває прив'язку до IP-адрес на транспортному рівні.",
                    size=10, fill="#ffffff", stroke=FIELD, sw=0.8))

    render(os.path.join(IMG, "tcp-flapping-and-maglev-ecmp.svg"), W, H, *f)


# 5. Внутрішньоцентровий Anycast (ECMP Anycast у дата-центрах)
def fig_datacenter_ecmp_anycast():
    W, H = 860, 480
    f = [text(W / 2, 28, "Внутрішній Anycast у дата-центрі (BGP to the Host + ECMP у топології Clos)", size=14, bold=True)]

    # Spine Switches Layer
    f.append(rect(220, 55, 420, 55, fill="#edf4ff", stroke=NEG, sw=1.4, rx=6))
    f.append(text(430, 77, "Рівень Spine-комутаторів (Магістраль DC)", size=12, bold=True, color=NEG))
    f.append(text(430, 96, "BGP / ECMP розподіл між фабрикою комутації", size=10, color=MUTED))

    # Leaf (Top-of-Rack) Switches
    f.append(rect(100, 145, 280, 70, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(240, 167, "Leaf Switch 1 (ToR)", size=11, bold=True, color=FIELD))
    f.append(text(240, 187, "ECMP маршрут до VIP 10.0.0.100/32", size=10, color=MUTED))
    f.append(text(240, 202, "Хешування за 5-tuple у залізі (ASIC)", size=9, color=MUTED))

    f.append(rect(480, 145, 280, 70, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(620, 167, "Leaf Switch 2 (ToR)", size=11, bold=True, color=FIELD))
    f.append(text(620, 187, "ECMP маршрут до VIP 10.0.0.100/32", size=10, color=MUTED))
    f.append(text(620, 202, "Хешування за 5-tuple у залізі (ASIC)", size=9, color=MUTED))

    # Links Spine <-> Leaf
    f.append(line(320, 110, 240, 145, color=LINE, sw=1.5))
    f.append(line(540, 110, 240, 145, color=LINE, sw=1.5))
    f.append(line(320, 110, 620, 145, color=LINE, sw=1.5))
    f.append(line(540, 110, 620, 145, color=LINE, sw=1.5))

    # Server Load Balancers (BGP to the Host)
    servers = [
        ("L4 Балансувальник 1", 50, 255, 170, 100, "BIRD / ExaBGP\nVIP: 10.0.0.100/32\nСтатус: HEALTHY\nАнонс: BGP OK", FIELD),
        ("L4 Балансувальник 2", 245, 255, 170, 100, "BIRD / ExaBGP\nVIP: 10.0.0.100/32\nСтатус: HEALTHY\nАнонс: BGP OK", FIELD),
        ("L4 Балансувальник 3", 445, 255, 170, 100, "BIRD / ExaBGP\nVIP: 10.0.0.100/32\nСтатус: UNHEALTHY\nАнонс: WITHDRAWN!", POS),
        ("L4 Балансувальник 4", 640, 255, 170, 100, "BIRD / ExaBGP\nVIP: 10.0.0.100/32\nСтатус: HEALTHY\nАнонс: BGP OK", FIELD),
    ]

    for title_txt, x, y, w, h, body_txt, col in servers:
        f.append(rect(x, y, w, h, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        f.append(text(x + w / 2, y + 20, title_txt, size=10, bold=True, color=col))
        f.append(fitbox(x + 6, y + 28, w - 12, 64, body_txt, size=9, fill="#fdfefe", stroke=MUTED, sw=0.6, color=INK))

    # Links Leaf -> Servers
    f.append(line(240, 215, 135, 255, color=FIELD, sw=1.5))
    f.append(line(240, 215, 330, 255, color=FIELD, sw=1.5))
    f.append(line(620, 215, 530, 255, color=POS, sw=1.5, dash="4,4"))
    f.append(line(620, 215, 725, 255, color=FIELD, sw=1.5))

    # Bottom summary
    f.append(fitbox(50, 375, 760, 80,
                    "Механізм відмовостійкості: Якщо сервіс на Балансувальнику 3 дає збій, локальний healthcheck демон\n"
                    "знімає BGP-анонс (BGP Withdraw). Комутатор Leaf миттєво вилучає вузол з апаратної групи ECMP\n"
                    "без затримок DNS TTL.",
                    size=10, fill="#f8fafc", stroke=LINE, sw=1.0, color=INK))

    render(os.path.join(IMG, "datacenter-ecmp-anycast.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anycast_vs_unicast_multicast()
    fig_bgp_anycast_catchment()
    fig_ddos_traffic_sinkholing()
    fig_tcp_flapping_and_maglev_ecmp()
    fig_datacenter_ecmp_anycast()
    print("All figures generated successfully.")
