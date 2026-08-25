# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми CDN (Мережі доставки вмісту)."""

import os
import sys

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від book/programming/distributed-systems/cdn)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cdn_edge_architecture():
    """Ієрархія CDN: Клієнти, Edge PoP (L1), Origin Shield (L2) та Origin Server."""
    w, h = 920, 480
    frags = []

    # Заголовок / фонові зони
    frags.append(rect(15, 45, 230, 415, fill="#f9fafb", stroke="#e5e7eb", sw=1, rx=8))
    frags.append(text(130, 70, "Клієнтський рівень", size=14, color=MUTED, bold=True))

    frags.append(rect(260, 45, 270, 415, fill="#f0f7ff", stroke="#bfdbfe", sw=1, rx=8))
    frags.append(text(395, 70, "Периферійні вузли (Edge L1)", size=14, color=NEG, bold=True))

    frags.append(rect(545, 45, 175, 415, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=8))
    frags.append(text(632, 70, "Origin Shield (L2)", size=14, color=FIELD, bold=True))

    frags.append(rect(735, 45, 170, 415, fill="#fef2f2", stroke="#fecaca", sw=1, rx=8))
    frags.append(text(820, 70, "Центральний Origin", size=14, color=POS, bold=True))

    # Клієнти
    b_c1, _, _ = textbox(130, 130, "Клієнт A (Київ)\nRTT до Edge: 4 мс", size=12, pad=8, fill="#ffffff", stroke="#9ca3af")
    b_c2, _, _ = textbox(130, 250, "Клієнт B (Варшава)\nRTT до Edge: 6 мс", size=12, pad=8, fill="#ffffff", stroke="#9ca3af")
    b_c3, _, _ = textbox(130, 370, "Клієнт C (Токіо)\nRTT до Edge: 5 мс", size=12, pad=8, fill="#ffffff", stroke="#9ca3af")
    frags.extend([b_c1, b_c2, b_c3])

    # Edge L1 PoPs
    b_e1, _, _ = textbox(395, 130, "Edge PoP (Київ)\nTLS Termination + RAM Cache", size=12, pad=8, fill="#ffffff", stroke=NEG)
    b_e2, _, _ = textbox(395, 250, "Edge PoP (Франкфурт)\nTLS Termination + RAM Cache", size=12, pad=8, fill="#ffffff", stroke=NEG)
    b_e3, _, _ = textbox(395, 370, "Edge PoP (Токіо)\nTLS Termination + RAM Cache", size=12, pad=8, fill="#ffffff", stroke=NEG)
    frags.extend([b_e1, b_e2, b_e3])

    # Shield L2
    b_shield, _, _ = textbox(632, 250, "Регіональний Shield\nФранкфурт (L2)\nNVMe кеш + Coalescing", size=12, pad=8, fill="#ffffff", stroke=FIELD)
    frags.append(b_shield)

    # Origin
    b_origin, _, _ = textbox(820, 250, "Центральний сервер\n(US-East, Вірджинія)\nБаза даних + Storage", size=12, pad=8, fill="#ffffff", stroke=POS)
    frags.append(b_origin)

    # З'єднання Клієнт -> Edge (короткі RTT)
    frags.append(arrow(195, 130, 305, 130, color=NEG, sw=1.5))
    frags.append(arrow(195, 250, 305, 250, color=NEG, sw=1.5))
    frags.append(arrow(195, 370, 305, 370, color=NEG, sw=1.5))

    # З'єднання Edge -> Shield (Приватний бекбон, прогріті TCP пули)
    frags.append(arrow(485, 130, 560, 220, color=FIELD, sw=1.5))
    frags.append(arrow(485, 250, 555, 250, color=FIELD, sw=1.5))
    frags.append(arrow(485, 370, 560, 280, color=FIELD, sw=1.5))

    # З'єднання Shield -> Origin (Одиночний магістральний канал)
    frags.append(arrow(710, 250, 745, 250, color=POS, sw=2.0))

    # Підписи латентності
    frags.append(text(250, 115, "RTT ~4мс", size=11, color=NEG, anchor="middle", italic=True))
    frags.append(text(250, 235, "RTT ~6мс", size=11, color=NEG, anchor="middle", italic=True))
    frags.append(text(250, 355, "RTT ~5мс", size=11, color=NEG, anchor="middle", italic=True))

    frags.append(text(515, 175, "Cache Miss", size=10, color=FIELD, anchor="middle"))
    frags.append(text(515, 335, "Cache Miss", size=10, color=FIELD, anchor="middle"))
    frags.append(text(728, 235, "1 запит", size=10, color=POS, anchor="middle", bold=True))

    return render(os.path.join(IMG_DIR, "cdn-edge-architecture.svg"), w, h, *frags)


def fig_anycast_vs_geodns():
    """Порівняння маршрутизації Anycast BGP проти GeoDNS."""
    w, h = 920, 460
    frags = []

    # Ліва колонка: BGP Anycast
    frags.append(rect(15, 30, 435, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(232, 58, "BGP Anycast Routing", size=15, color=NEG, bold=True))
    frags.append(text(232, 78, "Одна спільна IP (198.51.100.1) на всі дата-центри", size=11, color=MUTED))

    b_a_cl1, _, _ = textbox(110, 140, "Користувач у Києві", size=11, pad=6, fill="#ffffff", stroke="#9ca3af")
    b_a_cl2, _, _ = textbox(110, 340, "Користувач у Лондоні", size=11, pad=6, fill="#ffffff", stroke="#9ca3af")
    frags.extend([b_a_cl1, b_a_cl2])

    b_a_bgp, _, _ = textbox(232, 240, "Глобальна BGP-маршрутизація\n(Найкоротший AS-Path)", size=11, pad=6, fill="#eff6ff", stroke=NEG)
    frags.append(b_a_bgp)

    b_a_pop1, _, _ = textbox(365, 140, "Edge PoP Київ\nIP: 198.51.100.1\n(AS Path: 1 hop)", size=11, pad=6, fill="#ffffff", stroke=NEG)
    b_a_pop2, _, _ = textbox(365, 340, "Edge PoP Лондон\nIP: 198.51.100.1\n(AS Path: 1 hop)", size=11, pad=6, fill="#ffffff", stroke=NEG)
    frags.extend([b_a_pop1, b_a_pop2])

    frags.append(arrow(170, 140, 200, 215, color=LINE, sw=1.3))
    frags.append(arrow(170, 340, 200, 265, color=LINE, sw=1.3))
    frags.append(arrow(265, 215, 305, 140, color=NEG, sw=1.5))
    frags.append(arrow(265, 265, 305, 340, color=NEG, sw=1.5))

    # Права колонка: GeoDNS
    frags.append(rect(470, 30, 435, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(687, 58, "GeoDNS (DNS-базована маршрутизація)", size=15, color=FIELD, bold=True))
    frags.append(text(687, 78, "Різні IP-адреси залежно від клієнтської підмережі EDNS0", size=11, color=MUTED))

    b_g_cl, _, _ = textbox(550, 140, "Клієнт запитує\ncdn.example.com", size=11, pad=6, fill="#ffffff", stroke="#9ca3af")
    b_g_dns, _, _ = textbox(687, 240, "Authoritative DNS\n(Аналіз IP / EDNS0 Client Subnet)", size=11, pad=6, fill="#f0fdf4", stroke=FIELD)
    frags.extend([b_g_cl, b_g_dns])

    b_g_pop1, _, _ = textbox(820, 140, "PoP Європа\nIP: 203.0.113.10", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    b_g_pop2, _, _ = textbox(820, 340, "PoP США\nIP: 198.51.100.55", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.extend([b_g_pop1, b_g_pop2])

    frags.append(arrow(550, 175, 630, 220, color=LINE, sw=1.3))
    frags.append(arrow(687, 210, 755, 140, color=FIELD, sw=1.5))
    frags.append(arrow(687, 270, 755, 340, color=FIELD, sw=1.5))

    frags.append(text(585, 215, "1. DNS Query", size=10, color=MUTED, anchor="middle"))
    frags.append(text(745, 185, "2. A = 203.0.113.10", size=10, color=FIELD, anchor="middle", bold=True))
    frags.append(text(745, 305, "2. A = 198.51.100.55", size=10, color=FIELD, anchor="middle", bold=True))

    return render(os.path.join(IMG_DIR, "anycast-vs-geodns.svg"), w, h, *frags)


def fig_request_coalescing_stampede():
    """Схлопування паралельних запитів (Request Coalescing / Collapsing) на Edge."""
    w, h = 900, 420
    frags = []

    # Ліва зона: 100 паралельних клієнтів
    frags.append(rect(20, 35, 230, 360, fill="#fef2f2", stroke="#fecaca", sw=1, rx=8))
    frags.append(text(135, 60, "Сплеск запитів (10 000 req/s)", size=13, color=POS, bold=True))

    b_req1, _, _ = textbox(135, 110, "Клієнт 1: GET /video/chunk.m4s", size=10, pad=6, fill="#ffffff", stroke="#ef4444")
    b_req2, _, _ = textbox(135, 165, "Клієнт 2: GET /video/chunk.m4s", size=10, pad=6, fill="#ffffff", stroke="#ef4444")
    b_req3, _, _ = textbox(135, 220, "Клієнт 3: GET /video/chunk.m4s", size=10, pad=6, fill="#ffffff", stroke="#ef4444")
    frags.extend([b_req1, b_req2, b_req3])

    frags.append(text(135, 280, "⋮   (тисячі паралельних запитів)   ⋮", size=11, color=MUTED, anchor="middle", bold=True))
    b_reqN, _, _ = textbox(135, 345, "Клієнт N: GET /video/chunk.m4s", size=10, pad=6, fill="#ffffff", stroke="#ef4444")
    frags.append(b_reqN)

    # Центральна зона: Edge Proxy з Single-Flight
    frags.append(rect(290, 35, 320, 360, fill="#eff6ff", stroke="#bfdbfe", sw=1.2, rx=8))
    frags.append(text(450, 60, "Периферійний проксі (Edge Single-Flight)", size=13, color=NEG, bold=True))

    b_lock, _, _ = textbox(450, 130, "Хеш ключа: sha256('/video/chunk.m4s')\nСтатус: Cache Miss -> Блокування ключа", size=11, pad=8, fill="#ffffff", stroke=NEG)
    b_wait, _, _ = textbox(450, 240, "Черга очікування (Wait Queue):\nКлієнти 2..N блокуються на умовній змінній\nі чекають завершення першого запиту", size=11, pad=8, fill="#ffffff", stroke=MUTED)
    b_fanout, _, _ = textbox(450, 345, "Трансляція відповіді (Fan-Out):\nОтриманий потік байтів одночасно пишеться\nв локальний кеш і всім очікуючим клієнтам", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)
    frags.extend([b_lock, b_wait, b_fanout])

    # Права зона: Origin
    frags.append(rect(650, 35, 230, 360, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=8))
    frags.append(text(765, 60, "Origin Server", size=13, color=FIELD, bold=True))

    b_origin, _, _ = textbox(765, 200, "Центральний сервер\nОбробляє рівно 1 запит!\nНавантаження CPU: < 1%\nСмуга: 1× потік", size=11, pad=8, fill="#ffffff", stroke=FIELD)
    frags.append(b_origin)

    # Стрілки
    frags.append(arrow(215, 110, 320, 130, color=NEG, sw=1.5))
    frags.append(arrow(215, 165, 320, 220, color=MUTED, sw=1.2))
    frags.append(arrow(215, 220, 320, 240, color=MUTED, sw=1.2))
    frags.append(arrow(215, 345, 320, 260, color=MUTED, sw=1.2))

    # Edge -> Origin (єдиний запит)
    frags.append(arrow(580, 130, 680, 180, color=POS, sw=2.2))
    frags.append(text(630, 140, "1 Upstream Request", size=10, color=POS, anchor="middle", bold=True))

    # Origin -> Edge (відповідь)
    frags.append(arrow(680, 220, 580, 335, color=FIELD, sw=2.0))
    frags.append(text(630, 290, "200 OK (Stream)", size=10, color=FIELD, anchor="middle", bold=True))

    return render(os.path.join(IMG_DIR, "request-coalescing-stampede.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_cdn_edge_architecture()
    fig_anycast_vs_geodns()
    fig_request_coalescing_stampede()
    print("Усі фігури CDN згенеровано успішно.")
