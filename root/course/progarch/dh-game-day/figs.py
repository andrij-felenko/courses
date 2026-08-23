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

def fig_game_day_pipeline():
    """Конвеєр проведення Game Day у Digital Homes:
    Гіпотеза -> Runbook -> Впорскування збоїв -> Спостереження & Kill Switch -> Blameless Postmortem"""
    W, H = 1000, 360
    f = []

    steps = [
        (40, 60, 160, 240, "1. Гіпотеза\n\n- Steady State\n- Чіткі SLO\n- Очікувана реакція", BLUE_T, NEG),
        (230, 60, 160, 240, "2. Runbook\n\n- Сценарій хаосу\n- Аварійні межі\n- Kill Switch trigger", NEUT, INK),
        (420, 60, 160, 240, "3. Впорскування\n\n- Chaos interceptor\n- Затримки / збої\n- Канарковий обсяг", AMBER_T, AMBER),
        (610, 60, 160, 240, "4. Спостереження\n\n- Liveness / Readiness\n- Prometheus / Trace\n- Задіяння Kill Switch", RED_T, "#d9381e"),
        (800, 60, 160, 240, "5. Postmortem\n\n- Без звинувачень\n- Аналіз таймлайну\n- Квитки на рефактор", GREEN_T, FIELD),
    ]

    for x, y, w, h, label, bg_color, border_color in steps:
        f.append(fitbox(x, y, w, h, label, size=13, bold=True, fill=bg_color, stroke=border_color))
        if x < 800:
            f.append(arrow(x + w, y + h // 2, x + w + 30, y + h // 2, color="#9aa4b0", sw=2))

    render(os.path.join(OUT, 'game-day-pipeline.svg'), W, H, *f,
           title="Конвеєр проведення інженерних навчань Game Day")

def fig_twin_cache_thundering_herd():
    """Схема падіння кешу твінів: Redis OOM -> Cache Stampede -> Circuit Breaker & Singleflight"""
    W, H = 1020, 420
    f = []

    # Клієнти & MQTT
    f.append(fitbox(40, 140, 160, 120, "100 000+ пристроїв\n\nMQTT/HTTP запити", size=13, fill=BLUE_T, stroke=NEG))
    f.append(arrow(200, 200, 260, 200, color=INK, sw=2))

    # Сервіс твіна DH
    f.append(fitbox(260, 80, 240, 240, "Сервіс твіна (C4)\n\n[ Singleflight ]\n[ Circuit Breaker ]\n\nReadiness: 0 при збої", size=13, bold=True, fill=NEUT, stroke=INK))

    # Кеш (упав)
    f.append(arrow(500, 140, 580, 100, color="#d9381e", sw=2))
    f.append(fitbox(580, 60, 180, 80, "Redis Cache\n\n[ ЗБОЙ / OOM ]\nКеш відсутній!", size=13, bold=True, fill=RED_T, stroke="#d9381e"))

    # База даних (Postgres) під загрозою шторму
    f.append(arrow(500, 260, 580, 290, color=AMBER, sw=2))
    f.append(fitbox(580, 250, 180, 100, "Primary Postgres\n\n[ Singleflight захист ]\nлише 1 запит замість 50 000!", size=13, fill=AMBER_T, stroke=AMBER))

    # Захисний шар Circuit Breaker
    f.append(fitbox(800, 140, 180, 120, "Degraded Mode\n\nПовернення stale-даних або 503 з Retry-After", size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(760, 300, 890, 260, color=FIELD, sw=2))

    render(os.path.join(OUT, 'twin-cache-thundering-herd.svg'), W, H, *f,
           title="Анатомія падіння кешу твінів та захисні тактики")

def fig_readiness_liveness_cascade():
    """Динаміка Liveness та Readiness проб під час шторму реконектів"""
    W, H = 980, 380
    f = []

    # Ліва частина: шторм реконектів
    f.append(fitbox(40, 100, 220, 180, "Шторм реконектів\n\n- 100 000 хабів одночасно\n- High CPU & Latency\n- Черга з'єднань росте", size=13, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(260, 190, 340, 190, color=INK, sw=2))

    # Центр: Под у K8s
    f.append(fitbox(340, 60, 280, 260, "Под connection-edge (C3)\n\nОбробляє реконекти з Backoff\nCPU: 95%, Latency: 4s", size=14, bold=True, fill=NEUT, stroke=INK))

    # Верхня гілка: Readiness Probe
    f.append(arrow(620, 120, 720, 100, color="#d9381e", sw=2))
    f.append(fitbox(720, 60, 220, 90, "Readiness Probe: FAIL (0)\n\nЗнімає потік трафіку з K8s Service. Под НЕ рестартує!", size=13, bold=True, fill=RED_T, stroke="#d9381e"))

    # Нижня гілка: Liveness Probe
    f.append(arrow(620, 260, 720, 280, color=FIELD, sw=2))
    f.append(fitbox(720, 240, 220, 90, "Liveness Probe: PASS (1)\n\nПроцес живий, event-loop працює. Немає каскадних рестартів!", size=13, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'readiness-liveness-cascade.svg'), W, H, *f,
           title="Розрізнення Liveness та Readiness проб під час навантаження")

if __name__ == '__main__':
    fig_game_day_pipeline()
    fig_twin_cache_thundering_herd()
    fig_readiness_liveness_cascade()
