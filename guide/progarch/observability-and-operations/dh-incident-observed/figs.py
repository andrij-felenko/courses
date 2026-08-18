# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_triage_funnel():
    """Малює воронку розслідування інциденту через три стовпи спостережуваності."""
    w, h = 860, 420
    out = []
    
    # Фон та заголовок контейнера
    out.append(rect(10, 10, 840, 400, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    
    # Крок 1: Метрики
    out.append(rect(30, 40, 240, 340, fill="#fff5f5", stroke="#e74c3c", sw=1.5, rx=6))
    out.append(text(150, 70, "1. МЕТРИКИ (Prometheus)", size=14, color="#c0392b", bold=True))
    out.append(text(150, 95, "Сигнал про проблему (Що?)", size=11, color=MUTED, italic=True))
    
    out.append(rect(45, 120, 210, 90, fill="#ffffff", stroke="#e74c3c", sw=1.0, rx=4))
    out.append(text(150, 145, "p99 latency: 14.2 с", size=13, color="#c0392b", bold=True))
    out.append(text(150, 168, "http_requests_total (500)", size=11, color=INK))
    out.append(text(150, 190, "Alert: HighLatencyP99", size=11, color="#c0392b", bold=True))
    
    out.append(rect(45, 230, 210, 130, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=4))
    out.append(text(150, 255, "Prometheus Exemplar:", size=11, color=MUTED, bold=True))
    out.append(text(150, 280, "value = 14.21s", size=11, color=INK))
    out.append(text(150, 305, "trace_id = 4bf92f35...", size=11, color="#2457d6", bold=True))
    out.append(text(150, 335, "Місток до трейсів", size=11, color="#2457d6", bold=True))

    # Стрілка 1 -> 2
    out.append(arrow(270, 210, 305, 210, color="#2457d6", sw=2.0))

    # Крок 2: Трейси
    out.append(rect(310, 40, 240, 340, fill="#f0f7ff", stroke="#2457d6", sw=1.5, rx=6))
    out.append(text(430, 70, "2. ТРЕЙСИ (OpenTelemetry)", size=14, color="#2457d6", bold=True))
    out.append(text(430, 95, "Локалізація спану (Де?)", size=11, color=MUTED, italic=True))
    
    # Спан водоспад
    out.append(rect(325, 120, 210, 235, fill="#ffffff", stroke="#2457d6", sw=1.0, rx=4))
    
    # Envoy span
    out.append(rect(335, 135, 190, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=3))
    out.append(text(430, 157, "Envoy Proxy (14.25 s)", size=11, color="#2457d6", bold=True))
    
    # Gateway span
    out.append(rect(345, 180, 170, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=3))
    out.append(text(430, 202, "automation-mw (14.23 s)", size=11, color="#2457d6"))
    
    # Telemetry Service span
    out.append(rect(355, 225, 150, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=3))
    out.append(text(430, 247, "telemetry-svc (14.21 s)", size=11, color="#2457d6"))
    
    # Database span (BottleNeck!)
    out.append(rect(365, 270, 130, 45, fill="#fdecea", stroke="#c0392b", sw=1.5, rx=3))
    out.append(text(430, 288, "db:pg_exec (14.18 s)", size=11, color="#c0392b", bold=True))
    out.append(text(430, 304, "Вузьке місце!", size=10, color="#c0392b", italic=True))
    
    out.append(text(430, 340, "TraceID + SpanID", size=11, color="#27ae60", bold=True))

    # Стрілка 2 -> 3
    out.append(arrow(550, 210, 585, 210, color="#27ae60", sw=2.0))

    # Крок 3: Логи
    out.append(rect(590, 40, 240, 340, fill="#f2f9f4", stroke="#27ae60", sw=1.5, rx=6))
    out.append(text(710, 70, "3. ЛОГИ (Loki / JSON)", size=14, color="#27ae60", bold=True))
    out.append(text(710, 95, "Фізична причина (Чому?)", size=11, color=MUTED, italic=True))
    
    out.append(rect(605, 120, 210, 235, fill="#1a1a1a", stroke="#333333", sw=1.0, rx=4))
    out.append(text(710, 145, "Фільтр: trace_id = 4bf9...", size=10, color="#27ae60", bold=True))
    
    out.append(mtext(710, 175, [
        '{"level": "error",',
        ' "trace_id": "4bf9...",',
        ' "span_id": "00f0...",',
        ' "db.lock_wait": "14.1s",',
        ' "query": "SELECT * FROM',
        '  telemetry_events WHERE',
        '  payload->>\'status\'...",',
        ' "err": "Lock timeout",',
        ' "cause": "Unindexed JSON',
        '  scan + Row Lock"}',
    ], size=10, color="#00ff66", anchor="middle"))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'telemetry-triage-funnel.svg'), w, h, "".join(out))


def build_traceparent_propagation():
    """Малює структуру W3C traceparent та поширення контексту крізь сервіси."""
    w, h = 860, 440
    out = []
    
    out.append(rect(10, 10, 840, 420, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    
    # Блок заголовка специфікації
    out.append(rect(30, 25, 800, 90, fill="#f8f9fa", stroke="#2457d6", sw=1.2, rx=6))
    out.append(text(430, 48, "Формат заголовка W3C Trace Context (traceparent)", size=14, color="#2457d6", bold=True))
    
    # Сегменти traceparent
    # 00 - TraceID (32 hex) - ParentSpanID (16 hex) - TraceFlags (2 hex)
    out.append(rect(50, 65, 50, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=4))
    out.append(text(75, 87, "00", size=12, color="#2457d6", bold=True))
    out.append(text(75, 108, "Версія", size=9, color=MUTED))

    out.append(text(108, 87, "-", size=14, color=INK, bold=True))

    out.append(rect(115, 65, 360, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=4))
    out.append(text(295, 87, "4bf92f3577b34da6a3ce929d0e0e4736", size=12, color="#2457d6", bold=True))
    out.append(text(295, 108, "TraceID (128 біт / 32 hex) — єдиний на весь запит", size=9, color=MUTED))

    out.append(text(482, 87, "-", size=14, color=INK, bold=True))

    out.append(rect(490, 65, 230, 35, fill="#eaf0fd", stroke="#2457d6", sw=1.0, rx=4))
    out.append(text(605, 87, "00f067aa0ba902b7", size=12, color="#2457d6", bold=True))
    out.append(text(605, 108, "ParentSpanID (64 біти / 16 hex)", size=9, color=MUTED))

    out.append(text(727, 87, "-", size=14, color=INK, bold=True))

    out.append(rect(735, 65, 80, 35, fill="#fdecea", stroke="#c0392b", sw=1.0, rx=4))
    out.append(text(775, 87, "01", size=12, color="#c0392b", bold=True))
    out.append(text(775, 108, "Flags (Sampled)", size=9, color=MUTED))

    # Схема прокидання крізь сервіси
    out.append(text(430, 140, "Шлях прокидання контексту телеметрії Digital Homes", size=13, color=INK, bold=True))

    # 1. Edge Proxy
    out.append(rect(30, 160, 220, 110, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=6))
    out.append(text(140, 185, "Envoy Edge Gateway", size=12, color=INK, bold=True))
    out.append(text(140, 205, "Генерує TraceID", size=10, color=MUTED))
    out.append(text(140, 225, "Створює Span: edge-ingress", size=10, color="#2457d6"))
    out.append(text(140, 245, "Ін'єкція traceparent в HTTP", size=10, color="#27ae60", bold=True))

    out.append(arrow(250, 215, 300, 215, color="#2457d6", sw=2.0))
    out.append(text(275, 203, "HTTP/2", size=9, color=MUTED))

    # 2. Microservice Gateway
    out.append(rect(300, 160, 240, 110, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=6))
    out.append(text(420, 185, "Automation Service (Node/C++)", size=12, color=INK, bold=True))
    out.append(text(420, 205, "Витягає traceparent із заголовка", size=10, color=MUTED))
    out.append(text(420, 225, "Створює Child Span: command-exec", size=10, color="#2457d6"))
    out.append(text(420, 245, "Прокидає gRPC metadata далі", size=10, color="#27ae60", bold=True))

    out.arrow(540, 215, 590, 215, color="#2457d6", sw=2.0) if hasattr(out, 'arrow') else out.append(arrow(540, 215, 590, 215, color="#2457d6", sw=2.0))
    out.append(text(565, 203, "gRPC", size=9, color=MUTED))

    # 3. Telemetry Service & DB
    out.append(rect(590, 160, 240, 110, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=6))
    out.append(text(710, 185, "Device Telemetry Svc", size=12, color=INK, bold=True))
    out.append(text(710, 205, "Прив'язує TraceID до логера", size=10, color=MUTED))
    out.append(text(710, 225, "Створює DB Span: pg_query", size=10, color="#c0392b", bold=True))
    out.append(text(710, 245, "Експортує Exemplar у Prometheus", size=10, color="#2457d6", bold=True))

    # Відгалуження до трьох стовпів на виході
    out.append(arrow(140, 270, 140, 310, color="#e74c3c", sw=1.5))
    out.append(rect(40, 310, 200, 100, fill="#fff5f5", stroke="#e74c3c", sw=1.2, rx=6))
    out.append(text(140, 332, "Prometheus Metrics", size=12, color="#c0392b", bold=True))
    out.append(mtext(140, 357, [
        "http_requests_total",
        "duration_seconds_bucket",
        "+ Exemplar (trace_id)"
    ], size=10, color=INK))

    out.append(arrow(420, 270, 420, 310, color="#2457d6", sw=1.5))
    out.append(rect(320, 310, 200, 100, fill="#f0f7ff", stroke="#2457d6", sw=1.2, rx=6))
    out.append(text(420, 332, "OTel Trace Collector", size=12, color="#2457d6", bold=True))
    out.append(mtext(420, 357, [
        "Span Graph (Jaeger / Tempo)",
        "Parent-Child tree",
        "Duration & Status"
    ], size=10, color=INK))

    out.append(arrow(710, 270, 710, 310, color="#27ae60", sw=1.5))
    out.append(rect(610, 310, 200, 100, fill="#f2f9f4", stroke="#27ae60", sw=1.2, rx=6))
    out.append(text(710, 332, "Loki Log Aggregator", size=12, color="#27ae60", bold=True))
    out.append(mtext(710, 357, [
        "Structured JSON Logs",
        "Indexed trace_id field",
        "DB Slow Query & Exception"
    ], size=10, color=INK))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'w3c-traceparent-propagation.svg'), w, h, "".join(out))


if __name__ == '__main__':
    build_triage_funnel()
    build_traceparent_propagation()
    print("Figures generated successfully.")
