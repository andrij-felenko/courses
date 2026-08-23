# -*- coding: utf-8 -*-
"""Фігури до кроку «Перший сервіс-аудит DH» (root/course/progarch/monolith-vs-microservices/dh-services-audit)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eafaf0"
RED_TINT = "#fdecea"
BLUE_TINT = "#eef2fb"
YELLOW_TINT = "#fffde7"
NEUT = "#f7f8fa"

COLOR_WARN = "#d35400"
COLOR_INFO = "#2980b9"

def fig_coupling_three_axes():
    """Три виміри зв'язаності в сервіс-аудиті: дані, час виконання, модель."""
    W, H = 960, 480
    frags = []

    frags.append(text(W / 2, 30, "Три виміри зв'язаності під час сервіс-аудиту", size=15, bold=True))

    axes = [
        ("1. Зчеплення за даними\n(Data Coupling)", 
         "• Спільні таблиці SQL та FK\n• Прямі JOIN між доменами\n• Спільний Redis / Shared DB\n• Прямий доступ до чужого storage",
         RED_TINT, POS),
        ("2. Зчеплення за часом\n(Temporal / Execution)", 
         "• Синхронні HTTP/gRPC виклики\n• Накопичення затримок (Latency)\n• Каскадні відмови сервісів\n• Транзакційні замки та 2PC",
         YELLOW_TINT, COLOR_WARN),
        ("3. Зчеплення за моделлю\n(Domain / Model)", 
         "• Спільні DTO й бібліотеки\n• Протікання вендорських протоколів\n• Позичення сутностей домену\n• Монолітні класи-боги",
         BLUE_TINT, COLOR_INFO)
    ]

    for i, (title, desc, bg, stroke_color) in enumerate(axes):
        cx = 160 + i * 320
        cy = 230
        frags.append(rect(cx - 145, cy - 150, 290, 310, fill=bg, stroke=stroke_color, sw=1.8, rx=10))
        
        # Заголовок блоку
        title_lines = title.split('\n')
        for k, t_line in enumerate(title_lines):
            frags.append(text(cx, cy - 115 + k * 22, t_line, size=14, bold=True, color=INK))
            
        frags.append(line(cx - 120, cy - 60, cx + 120, cy - 60, color=stroke_color, sw=1.2))

        # Пункти
        desc_lines = desc.split('\n')
        for j, d_line in enumerate(desc_lines):
            frags.append(text(cx - 125, cy - 30 + j * 26, d_line, size=11, color=MUTED, anchor="start"))

    # Нижнє підсумкове правило
    frags.append(rect(40, 410, 880, 50, fill=NEUT, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(W / 2, 440, "Мета аудиту: знайти модулі з МІНІМАЛЬНИМ зчепленням за даними й максимальним виграшем від винесення.", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "coupling-three-axes.svg"), W, H, *frags,
           title="Три виміри зв'язаності в сервіс-аудиті")


def fig_dh_monolith_tangle():
    """Схема заплутаності моноліта Digital Homes до аудиту (Shared Database & Sync RPC)."""
    W, H = 960, 500
    frags = []

    frags.append(text(W / 2, 28, "Моноліт Digital Homes до аудиту: заплутаність даних і викликів", size=15, bold=True))

    # Рамка моноліта
    frags.append(rect(40, 55, 880, 425, fill=NEUT, stroke=LINE, sw=2, rx=12))
    frags.append(text(150, 80, "Єдиний монолітний процес Digital Homes", size=13, bold=True, color=MUTED))

    # Спільна БД внизу
    frags.append(rect(240, 370, 480, 85, fill=RED_TINT, stroke=POS, sw=2, rx=8))
    frags.append(text(480, 395, "Спільна база даних PostgreSQL (Single DB Anti-pattern)", size=13, bold=True, color=POS))
    frags.append(text(480, 425, "Таблиці: devices | device_states | telemetry_logs | video_feeds | users | billing_cards", size=10, color=MUTED))

    # Модулі всередині
    modules = [
        ("Device Management", 130, 140),
        ("Digital Twin", 360, 140),
        ("Automations Engine", 600, 140),
        ("Telemetry Ingestion", 830, 140),
        ("Video Streaming", 200, 260),
        ("Notifications", 480, 260),
        ("Identity & Auth", 740, 260)
    ]

    for title, cx, cy in modules:
        b, _, _ = textbox(cx, cy, title, size=11, fill="#ffffff", stroke=FIELD, bold=True)
        frags.append(b)

        # Стрілки зчеплення до спільної БД
        frags.append(arrow(cx, cy + 25, 480, 370, color=POS, sw=1.2))

    # Синхронні виклики між модулями (червоні суцільні)
    frags.append(arrow(130, 165, 360, 140, color=POS, sw=1.8)) # Device -> Twin
    frags.append(arrow(360, 165, 600, 140, color=POS, sw=1.8)) # Twin -> Automations
    frags.append(arrow(830, 165, 480, 370, color=POS, sw=2.5)) # Telemetry -> DB (WAL lock!)
    frags.append(arrow(740, 285, 200, 260, color=POS, sw=1.5)) # Auth -> Video

    # Підписи проблем
    frags.append(rect(50, 300, 220, 50, fill="#ffffff", stroke=COLOR_WARN, sw=1, rx=5))
    frags.append(text(160, 325, "⚠️ OOM падіння Video\nвалить весь моноліт", size=10, color=COLOR_WARN))

    frags.append(rect(690, 300, 220, 50, fill="#ffffff", stroke=POS, sw=1, rx=5))
    frags.append(text(800, 325, "⚠️ 15k/s Телеметрії\nзабиває connection pool", size=10, color=POS))

    render(os.path.join(IMG, "dh-monolith-data-tangle.svg"), W, H, *frags,
           title="Моноліт Digital Homes до аудиту")


def fig_dh_audit_matrix_quadrant():
    """Квадрант виділення сервісів: Виграш від винесення vs Зчеплення за даними."""
    W, H = 960, 520
    frags = []

    frags.append(text(W / 2, 28, "Матриця кандидатів на виділення у Digital Homes", size=15, bold=True))

    # Вісі координатної системи
    ox, oy = 120, 440
    w_axis, h_axis = 780, 370

    frags.append(arrow(ox, oy, ox + w_axis, oy, color=INK, sw=2)) # X: Data Coupling
    frags.append(arrow(ox, oy, ox, oy - h_axis, color=INK, sw=2)) # Y: Extraction Score

    frags.append(text(ox + w_axis - 60, oy + 25, "Зчеплення за даними (Data Coupling) ►", size=11, bold=True, anchor="end"))
    frags.append(text(ox - 10, oy - h_axis + 20, "▲ Виграш від винесення (Extraction Score)", size=11, bold=True, anchor="start"))

    # Чотири квадранти
    # Top-Left: High Score, Low Coupling -> PRIME CANDIDATES
    frags.append(rect(ox + 20, oy - h_axis + 40, 350, 150, fill=GREEN_TINT, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(ox + 195, oy - h_axis + 65, "🟢 Перші кандидати на виніс", size=13, bold=True, color=FIELD))
    frags.append(text(ox + 195, oy - h_axis + 95, "• Telemetry Ingestion (High IO/scale)\n• Video Streaming (Fault isolation/GPU)\n• Notifications (Async fan-out)\n• Billing (PCI-DSS wall)", size=10, color=MUTED))

    # Bottom-Left: Low Score, Low Coupling -> KEEP IN MONOLITH FOR NOW
    frags.append(rect(ox + 20, oy - 160, 350, 140, fill=NEUT, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(ox + 195, oy - 135, "⚪ Залишити в моноліті (Низький пріоритет)", size=12, bold=True, color=MUTED))
    frags.append(text(ox + 195, oy - 105, "• Audit Logs\n• User Profiles UI\nНемає виміряного болю", size=10, color=MUTED))

    # Bottom-Right: Low Score, High Coupling -> KEEP IN MONOLITH CORE
    frags.append(rect(ox + 410, oy - 160, 350, 140, fill=NEUT, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(ox + 585, oy - 135, "🔴 Ядро моноліта (НЕ різати!)", size=12, bold=True, color=POS))
    frags.append(text(ox + 585, oy - 105, "• Device Registry & Digital Twin\n• Automations Engine\nВисоке зчеплення SQL JOIN, спільний стан", size=10, color=MUTED))

    # Top-Right: High Score, High Coupling -> REQUIRES REFACTORING FIRST
    frags.append(rect(ox + 410, oy - h_axis + 40, 350, 150, fill=YELLOW_TINT, stroke=COLOR_WARN, sw=1.5, rx=8))
    frags.append(text(ox + 585, oy - h_axis + 65, "🟡 Спочатку розв'язати дані", size=12, bold=True, color=COLOR_WARN))
    frags.append(text(ox + 585, oy - h_axis + 95, "• Identity & User Auth\nПотрібно перевести на JWKS local verify\nта прибрати прямі SQL виклики", size=10, color=MUTED))

    render(os.path.join(IMG, "dh-audit-matrix-quadrant.svg"), W, H, *frags,
           title="Матриця кандидатів на виділення у Digital Homes")


def fig_dh_decoupled_target():
    """Цільова архітектура Digital Homes після першого сервіс-аудиту та розколу."""
    W, H = 960, 520
    frags = []

    frags.append(text(W / 2, 28, "Цільова архітектура Digital Homes після сервіс-аудиту", size=15, bold=True))

    # API Gateway зверху
    frags.append(rect(180, 55, 600, 50, fill=BLUE_TINT, stroke=COLOR_INFO, sw=1.8, rx=8))
    frags.append(text(480, 80, "Edge API Gateway (JWKS verify / Rate Limiting / SSL)", size=13, bold=True, color=COLOR_INFO))

    # Ядро Монументального Моноліта ліворуч
    frags.append(rect(60, 145, 420, 260, fill=NEUT, stroke=LINE, sw=2, rx=10))
    frags.append(text(270, 175, "Модульний Ядро-Моноліт DH (Core)", size=14, bold=True, color=INK))
    
    frags.append(rect(80, 200, 380, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(270, 225, "Devices & Digital Twin & Automations", size=12, bold=True))
    frags.append(text(270, 255, "Прямі виклики в пам'яті, ACID транзакції", size=10, color=MUTED))

    frags.append(rect(140, 330, 260, 55, fill=BLUE_TINT, stroke=COLOR_INFO, sw=1.5, rx=6))
    frags.append(text(270, 355, "PostgreSQL Core DB (Isolated schema)", size=11, bold=True))

    # Винесені автономні сервіси праворуч
    services = [
        ("Telemetry Service", "TimescaleDB / ScyllaDB", 520, 145, GREEN_TINT, FIELD),
        ("Video Stream Service", "RTSP / HLS Proxy (GPU)", 740, 145, GREEN_TINT, FIELD),
        ("Notifications Service", "Push (FCM/APNS) Worker", 520, 275, GREEN_TINT, FIELD),
        ("Billing & Cards Zone", "PCI-DSS Vault DB", 740, 275, RED_TINT, POS)
    ]

    for title, db_info, cx, cy, bg, stroke_col in services:
        frags.append(rect(cx, cy, 180, 110, fill=bg, stroke=stroke_col, sw=1.5, rx=8))
        frags.append(text(cx + 90, cy + 35, title, size=11, bold=True, color=INK))
        frags.append(text(cx + 90, cy + 70, db_info, size=10, color=MUTED))

    # NATS/Kafka Event Bus внизу
    frags.append(rect(60, 430, 840, 50, fill=YELLOW_TINT, stroke=COLOR_WARN, sw=1.8, rx=8))
    frags.append(text(480, 455, "Асинхронний Event Bus (NATS JetStream / Apache Kafka)", size=12, bold=True, color=INK))

    # Зв'язки стрілками від Gateway
    frags.append(arrow(380, 105, 270, 145, color=COLOR_INFO, sw=1.5))
    frags.append(arrow(600, 105, 610, 145, color=COLOR_INFO, sw=1.5))
    frags.append(arrow(680, 105, 830, 145, color=COLOR_INFO, sw=1.5))

    # Зв'язки з Event Bus
    frags.append(arrow(270, 405, 270, 430, color=COLOR_WARN, sw=1.5))
    frags.append(arrow(610, 255, 610, 430, color=COLOR_WARN, sw=1.5))
    frags.append(arrow(610, 385, 610, 430, color=COLOR_WARN, sw=1.5))

    render(os.path.join(IMG, "dh-decoupled-target-arch.svg"), W, H, *frags,
           title="Цільова архітектура Digital Homes після сервіс-аудиту")


if __name__ == "__main__":
    fig_coupling_three_axes()
    fig_dh_monolith_tangle()
    fig_dh_audit_matrix_quadrant()
    fig_dh_decoupled_target()
