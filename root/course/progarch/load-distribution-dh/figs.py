# -*- coding: utf-8 -*-
"""Фігури до теми «Розподіл навантаження DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_l4_vs_l7_grpc():
    """Порівняння L4 та L7 балансування для мультиплексованого gRPC (HTTP/2)."""
    W, H = 1000, 480
    frags = []

    # Фон і заголовки двох частин
    frags.append(rect(15, 15, 970, 215, fill="#fcfcfd", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 42, "L4 Балансування (TCP рівень): Перевантаження одного вузла", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(35, 62, "Одне TCP з'єднання містить всі gRPC стрими. L4 бачить лише сокет і відправляє все на Вузол 1.", size=12, color=MUTED, anchor="start"))

    # L4 Блок: Клієнтський Хаб
    box1, w1, _ = textbox(130, 140, "Хаб DH\n(1 TCP сокет\n3 gRPC стрими)", size=12, fill="#eef2ff", stroke=NEG, sw=1.5)
    frags.append(box1)

    # L4 Балансувальник
    box2, w2, _ = textbox(420, 140, "L4 Балансувальник\n(IPVS / Maglev / TCP)\nБачить лише IP/Port", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(box2)

    # Стрілка від хаба до L4 LB
    frags.append(arrow(210, 140, 310, 140, color=LINE, sw=2.0))
    frags.append(text(260, 130, "TCP connection", size=11, color=INK))

    # Backend Pods L4
    box3, _, _ = textbox(780, 100, "Ingest Pod 1\n100% навантаження\n(100k RPC/s)", size=12, fill="#fdecea", stroke=POS, sw=1.8, bold=True)
    box4, _, _ = textbox(780, 180, "Ingest Pod 2\n0% навантаження\n(Простій)", size=12, fill="#f4f6f8", stroke=MUTED, sw=1.2)
    frags.append(box3)
    frags.append(box4)

    # Стрілки від L4 LB до Pods
    frags.append(arrow(530, 130, 680, 100, color=POS, sw=2.5))
    frags.append(text(600, 105, "Усі стрими", size=11, color=POS, bold=True))
    frags.append(line(530, 150, 680, 180, color=MUTED, sw=1.2, dash="4,4"))

    # ────────────────────────────────────────────────────────────
    # L7 Блок (нижня частина)
    frags.append(rect(15, 245, 970, 220, fill="#fcfcfd", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 272, "L7 Балансування (gRPC / HTTP/2 рівень): Рівномірний розподіл", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(35, 292, "Envoy L7 демультиплексує HTTP/2 фрейми й розподіляє окремі RPC виклики між усіма подами.", size=12, color=MUTED, anchor="start"))

    # L7 Блок: Клієнтський Хаб
    box5, _, _ = textbox(130, 370, "Хаб DH\n(gRPC / HTTP/2)", size=12, fill="#eef2ff", stroke=NEG, sw=1.5)
    frags.append(box5)

    # L7 Envoy Proxy
    box6, _, _ = textbox(420, 370, "L7 Проксі (Envoy)\nРозпакування HTTP/2\nStream Router", size=12, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    frags.append(box6)

    # Стрілка від хаба до L7 Envoy
    frags.append(arrow(210, 370, 310, 370, color=LINE, sw=2.0))
    frags.append(text(260, 360, "HTTP/2 Stream", size=11, color=INK))

    # Backend Pods L7
    box7, _, _ = textbox(780, 325, "Ingest Pod 1\n33% RPC (Stream 1)", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    box8, _, _ = textbox(780, 370, "Ingest Pod 2\n33% RPC (Stream 2)", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    box9, _, _ = textbox(780, 415, "Ingest Pod 3\n33% RPC (Stream 3)", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    frags.append(box7)
    frags.append(box8)
    frags.append(box9)

    # Стрілки від Envoy до 3 подів
    frags.append(arrow(530, 355, 680, 325, color=FIELD, sw=1.8))
    frags.append(arrow(530, 370, 680, 370, color=FIELD, sw=1.8))
    frags.append(arrow(530, 385, 680, 415, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "l4-vs-l7-grpc.svg"), W, H, *frags)


def fig_dh_lb_stack_architecture():
    """Багаторівнева архітектура входу Digital Homes: Anycast, Maglev, Envoy, Gateway та Router."""
    W, H = 1020, 520
    frags = []

    # Шари архітектури (зліва направо)
    # 1. Джерела трафіку
    frags.append(rect(15, 15, 175, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(102, 42, "1. Клієнти й Хаби", size=13, bold=True, color=INK))
    
    b_hubs, _, _ = textbox(102, 130, "5M Хабів DH\ngRPC persistent\nlong-lived streams", size=12, fill="#eef2ff", stroke=NEG, sw=1.5)
    b_apps, _, _ = textbox(102, 380, "Мобільні Додатки\n150k RPS REST/gRPC\nshort-lived requests", size=12, fill="#fef3c7", stroke="#d97706", sw=1.5)
    frags.append(b_hubs)
    frags.append(b_apps)

    # 2. Anycast & L4 Layer
    frags.append(rect(205, 15, 195, 490, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(302, 42, "2. Anycast & L4 LB", size=13, bold=True, color=INK))

    b_anycast, _, _ = textbox(302, 130, "BGP Anycast IP\nМаршрутизація до\nнайближчого PoP", size=12, fill="#ffffff", stroke=LINE, sw=1.2)
    b_maglev, _, _ = textbox(302, 380, "L4 LB (Maglev/IPVS)\nStateless 5-tuple hash\nSYN-flood захист", size=12, fill="#ffffff", stroke=LINE, sw=1.2)
    frags.append(b_anycast)
    frags.append(b_maglev)

    # 3. L7 Envoy & TLS Termination
    frags.append(rect(415, 15, 205, 490, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=6))
    frags.append(text(517, 42, "3. Envoy Edge Proxy", size=13, bold=True, color=FIELD))

    b_tls, _, _ = textbox(517, 130, "TLS 1.3 Termination\nmTLS валідація хабів\nOffload криптографії", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    b_envoy_r, _, _ = textbox(517, 380, "L7 Router & Rate Limit\nEWMA / Least-Req\nHeader inspection", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    frags.append(b_tls)
    frags.append(b_envoy_r)

    # 4. Internal Backend Services
    frags.append(rect(635, 15, 370, 490, fill="#fafafb", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(820, 42, "4. Внутрішня Платформа", size=13, bold=True, color=INK))

    b_ingest, _, _ = textbox(740, 140, "Ingest Gateways\n(gRPC Hub Connections)\nТримає стан сокету", size=12, fill="#eef2ff", stroke=NEG, sw=1.5)
    b_router, _, _ = textbox(915, 140, "Home Router\nRegistry (Redis/NATS)\nhome_id -> Pod_ID", size=11, fill="#ffffff", stroke=LINE, sw=1.2)
    b_stateless, _, _ = textbox(820, 380, "Stateless Mobile Services\n(Auth, Devices, Telemetry, Rules)\nГоризонтальний HPA автоскейл", size=12, fill="#eafaf0", stroke=FIELD, sw=1.5)
    frags.append(b_ingest)
    frags.append(b_router)
    frags.append(b_stateless)

    # Зв'язки між шарами
    # Хаби -> Anycast -> TLS -> Ingest
    frags.append(arrow(180, 130, 240, 130, color=NEG, sw=1.8))
    frags.append(arrow(365, 130, 445, 130, color=LINE, sw=1.8))
    frags.append(arrow(590, 130, 670, 130, color=FIELD, sw=1.8))
    frags.append(arrow(810, 140, 855, 140, color=LINE, sw=1.5))

    # Мобільні -> Maglev -> Envoy -> Stateless
    frags.append(arrow(180, 380, 240, 380, color="#d97706", sw=1.8))
    frags.append(arrow(365, 380, 445, 380, color=LINE, sw=1.8))
    frags.append(arrow(590, 380, 710, 380, color=FIELD, sw=1.8))

    # Мобільні API звертається до Home Router для виклику хабу
    frags.append(arrow(820, 335, 915, 195, color=LINE, sw=1.5))
    frags.append(text(880, 270, "Пошук home_id", size=10, color=MUTED))

    render(os.path.join(IMG, "dh-lb-stack-architecture.svg"), W, H, *frags)


def fig_grpc_connection_drain():
    """Часова шкала Graceful Connection Draining за допомогою HTTP/2 GOAWAY."""
    W, H = 1000, 440
    frags = []

    # Лінія часу
    frags.append(line(80, 370, 950, 370, color=LINE, sw=2.0))
    frags.append(arrow(940, 370, 960, 370, color=LINE, sw=2.0))
    frags.append(text(950, 395, "Час (t)", size=12, bold=True, color=INK))

    # Етапи на лінії часу
    t_points = [
        (140, "t = 0", "Звичайний режим", "Хаб підключений до Gateway 1.\nТривають gRPC стрими."),
        (370, "t = 1h", "Max Connection Age", "Envoy надсилає GOAWAY\nз max_stream_id."),
        (630, "t = 1h + 10s", "Завершення стримів", "Активні RPC доробляються.\nНові стрими не створюються."),
        (880, "t = 1h + 15s", "М'яке перепідключення", "Хаб закриває сокет 1 і з jitter\nпідключається до Gateway 2.")
    ]

    for x, label_t, title, desc in t_points:
        frags.append(line(x, 360, x, 380, color=LINE, sw=2.0))
        frags.append(text(x, 400, label_t, size=12, bold=True, color=NEG if "1h" in label_t else INK))
        
        # Картки подій
        y_box = 180 if "1h" not in label_t else 120
        stroke_c = FIELD if label_t == "t = 0" else (POS if label_t == "t = 1h" else NEG)
        fill_c = "#eafaf0" if label_t == "t = 0" else ("#fdecea" if label_t == "t = 1h" else "#eef2ff")
        
        box, _, _ = textbox(x, y_box, f"{title}\n\n{desc}", size=11, fill=fill_c, stroke=stroke_c, sw=1.5)
        frags.append(box)
        frags.append(arrow(x, y_box + 45, x, 355, color=stroke_c, sw=1.5))

    # Додатковий підпис угорі
    frags.append(rect(15, 15, 970, 50, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(500, 35, "Плавне перепідключення (Graceful Drain) запобігає втраті даних та сплескам Thundering Herd", size=13, bold=True, color=INK))

    render(os.path.join(IMG, "grpc-connection-drain.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_l4_vs_l7_grpc()
    fig_dh_lb_stack_architecture()
    fig_grpc_connection_drain()
    print("Всі фігури згенеровано успішно.")
