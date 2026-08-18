# -*- coding: utf-8 -*-
"""Фігури до кроку «Життя одного запиту і однієї команди: капстон-синтез Digital Homes»."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_e2e_request_journey():
    """Наскрізна схема проходження запиту «Відчинити двері» крізь усі шари системи."""
    W, H = 1060, 680
    frags = []

    frags.append(text(W / 2, 40, "Наскрізний потік команди «Відчинити замок» у платформі Digital Homes", size=15, bold=True, color=FIELD))
    frags.append(text(W / 2, 64, "від дотику на екрані смартфона до повороту ригеля та push-сповіщення родині", size=12, color=MUTED))

    # Стовпчики-шари (8 блоків за ланцюжком)
    boxes_data = [
        ("1. Мобільний клієнт", "Мобільний застосунок\nHTTPS / TLS 1.3\nJWT token + Trace ID", "#eaf0fd", 140, 140),
        ("2. Периметр та LB", "GeoDNS · Anycast IP\nEnvoy TLS Termination\neBPF L4/L7 Balancing", "#eef2f6", 380, 140),
        ("3. Шлюз та Auth", "API Gateway\nWAF · Token Bucket\nOAuth2 JWT · OPA Authz", "#eef2f6", 620, 140),
        ("4. Доменне ядро", "SmartLockService\nAggregate DeviceTwin\ndesired.lock = UNLOCKED", "#eafaf0", 860, 140),
        ("5. Outbox & DB", "PostgreSQL ACID TX\nDevice Twin update\nOutbox Event insert", "#eafaf0", 860, 360),
        ("6. Шина та CDC", "CDC / Debezium WAL\nKafka Event Bus\n`home.commands.lock`", "#fff8e7", 620, 360),
        ("7. MQTT брокер", "IoT MQTT Hub\nmTLS Persistent Socket\nQoS 1 Command Publish", "#fff8e7", 380, 360),
        ("8. Пристрій & Край", "Smart Lock MCU / Hub\nPayload HMAC verification\nMotor turn + Physical Ack", "#ffeef0", 140, 360),
    ]

    box_objs = {}
    for name, desc, bg, cx, cy in boxes_data:
        b, w, h = textbox(cx, cy, f"{name}\n{desc}", size=12, fill=bg, stroke=LINE, sw=1.6)
        box_objs[name] = (cx, cy, w, h, b)
        frags.append(b)

    # Додатковий шар сповіщень та спостережуваності у нижній частині
    b_push, wp, hp = textbox(500, 560, "9. Зворотний потік & Telemetry\nIngestion -> Redis Twin Sync -> OpenTelemetry Collector -> FCM / APNs Push", size=12, fill="#eafaf0", stroke=FIELD, sw=2.0)
    frags.append(b_push)

    # Стрілки прямого потоку (1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8)
    frags.append(arrow(210, 140, 310, 140, color=NEG, sw=2.2))
    frags.append(arrow(450, 140, 550, 140, color=NEG, sw=2.2))
    frags.append(arrow(690, 140, 790, 140, color=NEG, sw=2.2))
    frags.append(arrow(860, 190, 860, 310, color=FIELD, sw=2.2))
    frags.append(arrow(790, 360, 690, 360, color=POS, sw=2.2))
    frags.append(arrow(550, 360, 450, 360, color=POS, sw=2.2))
    frags.append(arrow(310, 360, 210, 360, color=POS, sw=2.2))

    # Зворотний потік підтвердження від пристрою до сповіщень
    frags.append(arrow(140, 410, 390, 520, color=FIELD, sw=2.0))
    frags.append(arrow(620, 520, 860, 410, color=FIELD, sw=2.0))

    frags.append(text(W / 2, 645, "потік прямує зверху вправо вглиб системи, а потім повертається на край з підтвердженням і телеметрією", size=11, color=MUTED))

    render(os.path.join(IMG, "e2e-request-journey.svg"), W, H, *frags,
           title="Наскрізний потік запиту Відчинити двері")


def fig_outbox_to_mqtt_flow():
    """Схема транзакційного Outbox та асинхронної доставки через MQTT."""
    W, H = 1000, 500
    frags = []

    frags.append(text(W / 2, 36, "Конвеєр атомарної доставки: від ACID-транзакції ядра до краю", size=15, bold=True, color=FIELD))

    # Блоки процесу
    b1, w1, h1 = textbox(160, 140, "1. Доменне ядро\nPostgreSQL ACID TX\nTwin update + Outbox", size=12, fill="#eafaf0", stroke=FIELD, sw=2.0)
    b2, w2, h2 = textbox(410, 140, "2. CDC / Outbox Relay\nReads WAL / Outbox table\nPublishes to Kafka", size=12, fill="#fff8e7", stroke=LINE, sw=1.6)
    b3, w3, h3 = textbox(660, 140, "3. Kafka Broker\nTopic `home.commands.lock`\nLog append & Partitioning", size=12, fill="#fff8e7", stroke=LINE, sw=1.6)
    b4, w4, h4 = textbox(880, 140, "4. MQTT Worker\nConsumes Kafka\nResolves IoT Gateway", size=12, fill="#eef2f6", stroke=LINE, sw=1.6)

    b5, w5, h5 = textbox(880, 350, "5. MQTT Broker\nPublish QoS 1 to topic\n`dh/v1/h1/l1/cmd`", size=12, fill="#eef2f6", stroke=LINE, sw=1.6)
    b6, w6, h6 = textbox(520, 350, "6. Smart Lock MCU\nmTLS Session -> Motor Actuation\nGenerates PUBACK + State Ack", size=12, fill="#ffeef0", stroke=FIELD, sw=2.0)
    b7, w7, h7 = textbox(160, 350, "7. Twin Reconciler\nReceives reported state\nClears delta & updates cache", size=12, fill="#eafaf0", stroke=FIELD, sw=2.0)

    # Стрілки
    frags.append(arrow(240, 140, 330, 140, color=FIELD, sw=2.0))
    frags.append(arrow(490, 140, 580, 140, color=POS, sw=2.0))
    frags.append(arrow(740, 140, 810, 140, color=POS, sw=2.0))
    frags.append(arrow(880, 190, 880, 300, color=POS, sw=2.0))
    frags.append(arrow(800, 350, 640, 350, color=NEG, sw=2.2))
    frags.append(arrow(400, 350, 240, 350, color=FIELD, sw=2.0))

    frags += [b1, b2, b3, b4, b5, b6, b7]
    frags.append(text(W / 2, 465, "жодних втрат: подія на край гарантується Outbox-шаблоном та QoS 1 підтвердженням", size=11, color=MUTED))

    render(os.path.join(IMG, "outbox-to-mqtt-flow.svg"), W, H, *frags,
           title="Конвеєр атомарної доставки через Outbox та MQTT")


def fig_telemetry_trace_span():
    """Профіль затримок (OpenTelemetry trace) наскрізного виконання команди."""
    W, H = 1000, 520
    frags = []

    frags.append(text(W / 2, 36, "Профіль затримок (OpenTelemetry Trace Waterfall) команди відчинення", size=15, bold=True, color=FIELD))
    frags.append(text(W / 2, 60, "Загальний час p99 ~ 445 мс (з урахуванням фізичної механіки замка 340 мс)", size=12, color=MUTED))

    # Спани
    spans = [
        ("POST /api/v1/homes/h1/locks/l1/unlock", 0, 445, "#d9e2ec", "Root Span (445 ms)"),
        ("  net.tls_and_lb_handshake", 0, 22, "#bccadc", "22 ms"),
        ("  gateway.auth_and_policy_eval", 22, 10, "#9fb3c8", "10 ms"),
        ("  domain.unlock_command_handler", 32, 18, "#829ab1", "18 ms"),
        ("    db.postgres_tx_commit_outbox", 36, 12, "#627d98", "12 ms"),
        ("  eventbus.kafka_publish", 50, 6, "#486581", "6 ms"),
        ("  mqtt.broker_dispatch", 56, 12, "#334e68", "12 ms"),
        ("  hardware.mcu_actuation_and_ack", 68, 340, "#ffeef0", "340 ms (механіка)"),
        ("  notification.fcm_push_fanout", 410, 35, "#eafaf0", "35 ms"),
    ]

    y_start = 100
    row_h = 38
    scale = 1.8  # ms -> pixels

    for i, (name, start, dur, col, val_lbl) in enumerate(spans):
        y = y_start + i * row_h
        # Назва спану зліва
        frags.append(text(240, y + 18, name, size=11, anchor="end", color=NEG))
        # Смуга спану
        x_bar = 260 + start * scale
        w_bar = max(dur * scale, 6)
        frags.append(rect(x_bar, y, w_bar, 24, fill=col, stroke=LINE, sw=1.0))
        # Підпис тривалості праворуч від смуги
        frags.append(text(x_bar + w_bar + 10, y + 16, val_lbl, size=10, anchor="start", color=MUTED))

    # Сітка часу
    for ms in [0, 100, 200, 300, 400]:
        x_grid = 260 + ms * scale
        frags.append(line(x_grid, y_start - 10, x_grid, y_start + len(spans) * row_h, color=LINE, sw=0.8, dash="3,3"))
        frags.append(text(x_grid, y_start + len(spans) * row_h + 18, f"{ms} ms", size=10, color=MUTED))

    render(os.path.join(IMG, "telemetry-trace-span.svg"), W, H, *frags,
           title="Профіль затримок OpenTelemetry Trace")


if __name__ == "__main__":
    fig_e2e_request_journey()
    fig_outbox_to_mqtt_flow()
    fig_telemetry_trace_span()
    print("OK: e2e-request-journey.svg, outbox-to-mqtt-flow.svg, telemetry-trace-span.svg generated")
