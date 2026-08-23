# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"

def fig_pipeline_overview():
    """Анатомія канареєчного конвеєра DH: коміт -> ворота -> канарка 1% -> аналіз -> реліз або автовідкат."""
    W, H = 1000, 380
    f = []

    # Title / Header areas
    f.append(fitbox(20, 20, 210, 50, "1. Коміт і збірка\nTrunk-based + Git SHA", size=13, bold=True, fill=BLUE_T))
    f.append(fitbox(260, 20, 220, 50, "2. Ворота якості\nUnit, integration, contract", size=13, bold=True, fill=NEUT))
    f.append(fitbox(510, 20, 220, 50, "3. Канаркова розкатка\n1% -> 10% -> 50% -> 100%", size=13, bold=True, fill=AMBER_T))
    f.append(fitbox(760, 20, 220, 50, "4. Прийняття рішення\nАналіз метрик та автовідкат", size=13, bold=True, fill=GREEN_T))

    # Flow arrows top row
    f.append(arrow(230, 45, 260, 45))
    f.append(arrow(480, 45, 510, 45))
    f.append(arrow(730, 45, 760, 45))

    # Details middle section
    # Stage 1 details
    f.append(fitbox(20, 95, 210, 110, "Артефакт контейнера:\ndh-backend:sha-a8f3b9\n(незмінний бінарник,\nконфіг ззовні)", size=12, fill=BG, stroke=LINE))

    # Stage 2 details
    f.append(fitbox(260, 95, 220, 110, "Автоматичні тести:\n- Лінтер і статаналіз\n- Юніт-тести ядра\n- Контракти сервісів", size=12, fill=BG, stroke=LINE))

    # Stage 3 details (Traffic split)
    f.append(fitbox(510, 95, 220, 110, "Маршрутизація Envoy:\n- 99% -> Базовий в1.4\n- 1% -> Канарка в1.5\n(однакове середовище)", size=12, fill=BG, stroke=LINE))

    # Stage 4 details (Decision engine)
    f.append(fitbox(760, 95, 220, 110, "Аналізатор метрик:\n- Порівняння RED\n- p95/p99 затримка\n- Специфічні IoT SLI", size=12, fill=BG, stroke=LINE))

    # Bottom decision outcomes
    f.append(fitbox(510, 250, 220, 85, "УСПІХ (Score >= 95)\nПідвищення частки\n1% -> 10% -> 100%", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(760, 250, 220, 85, "АВАРІЯ (Score < 75)\nАвтоматичний відкат:\n1% -> 0% за секунди", size=12, bold=True, fill=RED_T, stroke=POS))

    # Arrows from stage 4 to outcomes
    f.append(arrow(870, 205, 620, 250, color=FIELD, sw=2))
    f.append(arrow(870, 205, 870, 250, color=POS, sw=2))

    render(os.path.join(OUT, 'canary-pipeline-overview.svg'), W, H, *f)

def fig_metrics_comparison():
    """Порівняльний аналіз метрик: Базова версія (v1.4) vs Канарка (v1.5)."""
    W, H = 960, 360
    f = []

    # Title area
    f.append(fitbox(20, 20, 440, 45, "Базова версія v1.4 (95% трафіку)", size=14, bold=True, fill=BLUE_T))
    f.append(fitbox(500, 20, 440, 45, "Канарка v1.5 (5% трафіку)", size=14, bold=True, fill=AMBER_T))

    # Metric Rows
    # Row 1: Error rate
    f.append(fitbox(20, 80, 440, 65, "Частота помилок (5xx / exceptions):\n0.02% (норма під навантаженням)", size=13, fill=BG))
    f.append(fitbox(500, 80, 440, 65, "Частота помилок (5xx / exceptions):\n1.85% (АНОМАЛІЯ: +925% від бази)", size=13, bold=True, fill=RED_T, stroke=POS))

    # Row 2: Latency p95
    f.append(fitbox(20, 160, 440, 65, "Затримка p95 / p99:\np95 = 42 мс, p99 = 110 мс", size=13, fill=BG))
    f.append(fitbox(500, 160, 440, 65, "Затримка p95 / p99:\np95 = 145 мс, p99 = 890 мс (ХВІСТ)", size=13, bold=True, fill=RED_T, stroke=POS))

    # Row 3: IoT Specific Metric
    f.append(fitbox(20, 240, 440, 65, "Перепідключення хабів (reconnects):\n0.15 подій / сек", size=13, fill=BG))
    f.append(fitbox(500, 240, 440, 65, "Перепідключення хабів (reconnects):\n4.80 подій / сек (ШТОРМ ПІДКЛЮЧЕНЬ)", size=13, bold=True, fill=RED_T, stroke=POS))

    # Bottom score calculation banner
    f.append(fitbox(20, 315, 920, 35, "Рішення Kayenta / PromQL: Score = 32 / 100 (ПОРІГ 75) -> ІНІЦІАЦІЯ АВТОВІДКАТУ", size=13, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'canary-metrics-comparison.svg'), W, H, *f)

def fig_traffic_routing_and_flags():
    """Взаємодія шлюзу маршрутизації та прапорців функцій."""
    W, H = 980, 370
    f = []

    # Left: Incoming Traffic
    f.append(fitbox(20, 130, 180, 90, "Вхідний трафік\n(IoT хаби + мобільний\nзастосунок DH)", size=13, bold=True, fill=NEUT))

    # Center: Edge Ingress Router
    f.append(fitbox(240, 100, 220, 150, "Вхідний шлюз (Envoy)\n- Weighted Cluster\n- Header matching\n\n95% -> Baseline\n5% -> Canary", size=13, bold=True, fill=BLUE_T))

    f.append(arrow(200, 175, 240, 175))

    # Right Top: Baseline Nodes
    f.append(fitbox(520, 40, 220, 110, "Базовий кластер (v1.4)\n95% нод\nКод v1.4 бінарник", size=13, fill=BG))

    # Right Bottom: Canary Nodes
    f.append(fitbox(520, 210, 220, 110, "Канарковий кластер (v1.5)\n5% нод\nКод v1.5 бінарник", size=13, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(460, 140, 520, 95, sw=2))
    f.append(arrow(460, 210, 520, 265, sw=2))

    # Far Right: Feature Flag Service
    f.append(fitbox(780, 110, 180, 130, "Сервіс прапорців\n(Feature Flags)\n\nАварійний рубильник:\nkill-switch = true/false", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    # Lines connecting Feature Flag service to nodes
    f.append(line(780, 150, 740, 95, color=FIELD, sw=1.5, dash="4 4"))
    f.append(line(780, 200, 740, 265, color=FIELD, sw=1.5, dash="4 4"))

    render(os.path.join(OUT, 'traffic-routing-and-flags.svg'), W, H, *f)

if __name__ == '__main__':
    fig_pipeline_overview()
    fig_metrics_comparison()
    fig_traffic_routing_and_flags()
    print("Figures generated successfully.")
