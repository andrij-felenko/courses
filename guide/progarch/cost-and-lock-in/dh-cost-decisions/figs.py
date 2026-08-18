# -*- coding: utf-8 -*-
"""Фігури для теми «Економічні рішення DH» (guide/progarch/cost-and-lock-in/dh-cost-decisions)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_LIGHT = "#f8fafc"
BORDER_GRAY = "#cbd5e1"
TEXT_DARK = "#1e293b"
TEXT_MUTED = "#475569"

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S = "#f1f5f9", "#64748b"

def draw_polyline(pts, color="#333333", sw=1.5):
    d = "M " + " L ".join("%g %g" % (x, y) for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}"/>'

def fig_telemetry_cost_breakdown():
    """fig1-telemetry-cost-breakdown.svg: Наївна хмарна архітектура проти edge-агрегованої економічної моделі DH."""
    W, H = 880, 480
    frags = []

    # Загальний контейнер
    frags.append(rect(10, 10, 860, 460, fill=BG_LIGHT, stroke=BORDER_GRAY, sw=1.5, rx=10))
    frags.append(text(440, 34, "Архітектурний зсув: наївний хмарний потік проти Edge-агрегації DH", size=16, bold=True, color=TEXT_DARK))

    # Секція 1: Наївний підхід (Ліворуч)
    frags.append(rect(30, 60, 400, 390, fill="#ffffff", stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(230, 85, "Наївний підхід: Cloud-First Stream-All", size=14, bold=True, color=RED_S))

    # Вузли ліворуч
    b1, _, _ = textbox(230, 130, "100M Давачів у 5M Домах\n(Опитування що 5 сек)", size=11, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b1)
    
    b2, _, _ = textbox(230, 210, "51.8 Мільярдів MQTT-повідомлень / день\n(TLS Keep-Alive + 100B payload)", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b2)

    b3, _, _ = textbox(230, 290, "AWS IoT Core + DynamoDB Direct Ingest\n($1.00/1M msg ingest + $1.25/1M WCU)", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b3)

    b4, _, _ = textbox(230, 390, "Фінансовий результат:\n$3.49M / місяць ($0.70 / дім / міс)\nЗбиток: -$1.00M / місяць!", size=12, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b4)

    # Стрілки ліворуч
    frags.append(arrow(230, 155, 230, 185, color=RED_S, sw=1.5))
    frags.append(arrow(230, 235, 230, 265, color=RED_S, sw=1.5))
    frags.append(arrow(230, 315, 230, 355, color=RED_S, sw=1.5))

    # Секція 2: Edge-оптимізована модель DH (Праворуч)
    frags.append(rect(450, 60, 400, 390, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(650, 85, "Модель DH: Edge Aggregation & Delta", size=14, bold=True, color=GREEN_S))

    # Вузли праворуч
    b5, _, _ = textbox(650, 130, "100M Давачів + Локальна SQLite\n(Правила виконуються офлайн)", size=11, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b5)

    b6, _, _ = textbox(650, 210, "Delta-Filtering & 15-хвилинні Батчі\n(500 Мил. повідомлень / день, -99%)", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b6)

    b7, _, _ = textbox(650, 290, "Self-Hosted EMQX + ClickHouse Archive\n(Tiering: Hot SQLite -> Parquet Object)", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b7)

    b8, _, _ = textbox(650, 390, "Фінансовий результат:\n$45,000 / місяць ($0.009 / дім / міс)\nПрибуток: +$2.45M / місяць!", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b8)

    # Стрілки праворуч
    frags.append(arrow(650, 155, 650, 185, color=GREEN_S, sw=1.5))
    frags.append(arrow(650, 235, 650, 265, color=GREEN_S, sw=1.5))
    frags.append(arrow(650, 315, 650, 355, color=GREEN_S, sw=1.5))

    render(os.path.join(IMG, "fig1-telemetry-cost-breakdown.svg"), W, H, *frags)

def fig_video_egress_architecture():
    """fig2-video-egress-architecture.svg: Гібридна відеоархітектура WebRTC Direct Streaming проти Cloud Relay Egress."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill=BG_LIGHT, stroke=BORDER_GRAY, sw=1.5, rx=10))
    frags.append(text(440, 34, "Гібридна відеоархітектура DH: Оптимізація Cloud Egress", size=16, bold=True, color=TEXT_DARK))

    # Камера в будинку
    b_cam, _, _ = textbox(130, 180, "IP-Камера в Домі\n(1080p, H.265 / 2 Mbps)\nЛокальний Ring Buffer (SD/SSD)", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_cam)

    # WebRTC Direct P2P Stream (Основний потік)
    b_p2p, _, _ = textbox(440, 120, "WebRTC Direct Stream (STUN/TURN)\n(95% переглядів: Хаб -> Телефон напряму)\nEgress Cost = $0.00 / GB!", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_p2p)

    # Cloud Object Storage for Triggered Clips (Подієвий потік)
    b_cloud, _, _ = textbox(440, 280, "Хмарне сховище подієвих кліпів\n(Тільки 10-сек тривожні фрагменти)\nS3 Cold Tier (Parquet/HLS)", size=11, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_cloud)

    # Мобільний застосунок користувача
    b_app, _, _ = textbox(750, 180, "Застосунок Мобільний\n(Перегляд Live & Архіву)\nSmart Fallback Engine", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_app)

    # Лінії та зв'язки
    frags.append(arrow(240, 160, 310, 130, color=GREEN_S, sw=2))
    frags.append(arrow(570, 130, 640, 160, color=GREEN_S, sw=2))

    frags.append(arrow(240, 200, 310, 270, color=BLUE_S, sw=1.5))
    frags.append(arrow(570, 270, 640, 200, color=BLUE_S, sw=1.5))

    # Пояснювальний блок знизу
    frags.append(rect(130, 340, 620, 70, fill="#ffffff", stroke=BORDER_GRAY, rx=6))
    frags.append(text(440, 362, "Економічний ефект гібридного відео:", size=12, bold=True, color=TEXT_DARK))
    frags.append(text(440, 388, "Прямий P2P транзит знімає 27 Петабайт/місяць хмарного Egress. Витрати: з $1.35M/міс до $60K/міс (-95.5%)", size=11, color=TEXT_MUTED))

    render(os.path.join(IMG, "fig2-video-egress-architecture.svg"), W, H, *frags)

def fig_broker_tco_breakeven():
    """fig3-broker-tco-breakeven.svg: Точка перетину TCO (AWS IoT Core vs Self-Hosted EMQX Fleet)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill=BG_LIGHT, stroke=BORDER_GRAY, sw=1.5, rx=10))
    frags.append(text(440, 34, "TCO брокера повідомлень: Managed AWS IoT Core vs Self-Hosted EMQX", size=16, bold=True, color=TEXT_DARK))

    # Осі графіку
    frags.append(line(100, 340, 780, 340, color="#64748b", sw=2)) # Ось X
    frags.append(line(100, 80, 100, 340, color="#64748b", sw=2))  # Ось Y

    # Підписи осей
    frags.append(text(780, 365, "Флот хабів (Кількість активних будинків)", size=11, bold=True, color=TEXT_MUTED, anchor="end"))
    frags.append(text(85, 75, "TCO ($ / місяць)", size=11, bold=True, color=TEXT_MUTED, anchor="start"))

    # Відмітки X (100k, 500k, 1M, 5M)
    x_marks = [(180, "100K"), (320, "500K"), (480, "1M"), (720, "5M")]
    for x, lbl in x_marks:
        frags.append(line(x, 335, x, 345, color="#64748b", sw=1.5))
        frags.append(text(x, 360, lbl, size=11, color=TEXT_MUTED))

    # Відмітки Y ($10K, $50K, $200K, $500K)
    y_marks = [(300, "$10K"), (230, "$50K"), (160, "$200K"), (95, "$500K")]
    for y, lbl in y_marks:
        frags.append(line(95, y, 105, y, color="#64748b", sw=1.5))
        frags.append(text(85, y + 4, lbl, size=10, color=TEXT_MUTED, anchor="end"))

    # Лінія AWS IoT Core (Managed) - лінійна залежність від трафіку
    frags.append(draw_polyline([(180, 308), (320, 252), (480, 195), (720, 110)], color=RED_S, sw=2.5))
    frags.append(text(730, 105, "AWS IoT Core (Pay-as-you-go)", size=11, bold=True, color=RED_S, anchor="start"))

    # Лінія Self-Hosted EMQX (High fixed ops cost, low marginal scaling)
    frags.append(draw_polyline([(180, 290), (320, 285), (480, 278), (720, 240)], color=GREEN_S, sw=2.5))
    frags.append(text(730, 240, "Self-Hosted EMQX Cluster", size=11, bold=True, color=GREEN_S, anchor="start"))

    # Точка перетину (Breakeven point ~ 250K хабів)
    frags.append(circle(260, 295, 6, fill=AMBER_S, stroke="#ffffff", sw=2))
    frags.append(line(260, 295, 260, 340, color=AMBER_S, sw=1, dash="3,3"))
    frags.append(text(265, 285, "Breakeven Point (~250K хабів)", size=11, bold=True, color=AMBER_S))

    render(os.path.join(IMG, "fig3-broker-tco-breakeven.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_telemetry_cost_breakdown()
    fig_video_egress_architecture()
    fig_broker_tco_breakeven()
    print("SVGs generated successfully.")
