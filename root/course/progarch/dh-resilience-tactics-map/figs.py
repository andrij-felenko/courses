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
PURPLE_T= "#f3e8ff"
PURPLE  = "#7e22ce"

def fig_resilience_map_pipeline():
    """Повний синтезований пайплайн тактик стійкості від Edge Gateway до асинхронних черг."""
    W, H = 1060, 520
    f = []

    # Крок 1: Вхідний потік
    f.append(fitbox(30, 200, 160, 80, "Вхідний потік запитів\n(18:00 Peak Burst)\n500k пристроїв", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(190, 240, 240, 240))

    # Шар 1: Edge API Gateway (Rate Limit + Priority Shedding)
    f.append(rect(240, 50, 200, 350, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(340, 78, "Шар 1 · Edge Gateway", size=14, bold=True, anchor="middle"))
    f.append(line(255, 88, 425, 88, color="#c8ced6", sw=1.2))
    f.append(fitbox(255, 98, 170, 48, "Token Bucket Rate Limit\n(Per-Tenant / Per-IP)", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(255, 154, 170, 56, "Priority Load Shedding\n(P0..P4 Cutoff)\nBrownout L0..L4", size=11, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(255, 218, 170, 48, "Early Reject 429 / 503\nDrop P4 / P3 at Edge", size=11, fill=RED_T, stroke=POS))
    f.append(fitbox(255, 274, 170, 70, "Pass P0/P1 + Throttled P2\n(Zero-Memory Allocation)", size=11, bold=True, fill=GREEN_T, stroke=FIELD))

    # Стрілка скидання на Шар 1 (від дна блоку Edge Gateway вниз)
    f.append(arrow(340, 400, 340, 435, color=POS))
    f.append(fitbox(260, 435, 160, 42, "HTTP 429 / 503\nRetry-After Header", size=10, fill=RED_T, stroke=POS))

    f.append(arrow(440, 225, 490, 225, color=FIELD))

    # Шар 2: Внутрішній сервіс (Adaptive Concurrency + Circuit Breaker)
    f.append(rect(490, 50, 210, 350, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(595, 78, "Шар 2 · Service Worker", size=14, bold=True, anchor="middle"))
    f.append(line(505, 88, 685, 88, color="#c8ced6", sw=1.2))
    f.append(fitbox(505, 98, 180, 52, "Adaptive Concurrency\n(CoDel / AIMD Limiter)\nIn-Flight Max: N", size=11, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(505, 158, 180, 56, "Circuit Breaker\n(Closed / Open / Half-Open)\nDependency Guard", size=11, bold=True, fill=PURPLE_T, stroke=PURPLE))
    f.append(fitbox(505, 222, 180, 48, "Primary Handler Execution\nDB / Cache Call", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(505, 278, 180, 85, "Sync Response (200 OK)\nабо Fallback Trigger\nабо Async Event Push", size=11, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(arrow(700, 225, 750, 225, color=FIELD))

    # Шар 3 & 4: Fallback & DLQ Router
    f.append(rect(750, 50, 270, 350, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(885, 78, "Шар 3 & 4 · Fallback / DLQ", size=14, bold=True, anchor="middle"))
    f.append(line(765, 88, 1005, 88, color="#c8ced6", sw=1.2))
    f.append(fitbox(765, 98, 240, 52, "Fallback Manager\n(Stale Cache / Default Safe / Local BLE)", size=11, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(765, 158, 240, 56, "Message Broker / Event Queue\n(End-to-End Backpressure)", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(765, 222, 240, 56, "Poison Pill Isolation\nExponential Backoff + Jitter", size=11, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(765, 286, 240, 80, "Dead-Letter Queue (DLQ)\nParked for Manual Inspection\nAlerting & Replay Pipeline", size=11, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'dh-resilience-map-pipeline.svg'), W, H, *f,
           title="Повний пайплайн тактик стійкості Digital Homes")

def fig_resilience_state_matrix():
    """Сходи деградації Brownout та стани Circuit Breaker."""
    W, H = 1000, 440
    f = []

    # Заголовок ліворуч — Brownout Levels
    f.append(rect(30, 40, 440, 370, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(250, 70, "Рівні деградації Brownout (Система)", size=14, bold=True, anchor="middle"))
    f.append(line(50, 82, 450, 82, color="#c8ced6", sw=1.2))

    b_levels = [
        (95,  "L0 · Normal State: 100% трафіку проходить", FIELD, GREEN_T),
        (155, "L1 · Mild Pressure: Drop P4 (Video Upload)", AMBER, AMBER_T),
        (215, "L2 · High Pressure: Drop P3 (Telemetry Analytics)", AMBER, AMBER_T),
        (275, "L3 · Severe Strain: Drop P2 + Throttling P1", POS, RED_T),
        (335, "L4 · Blackout Defense: Pass P0 ONLY (Locks/Alarms)", POS, RED_T),
    ]
    for y, label, col, tint in b_levels:
        f.append(fitbox(50, y, 400, 48, label, size=11, bold=True, stroke=col, fill=tint))

    # Стрілка зв'язку
    f.append(arrow(470, 225, 520, 225, color=PURPLE))

    # Заголовок праворуч — Circuit Breaker FSM
    f.append(rect(520, 40, 450, 370, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(745, 70, "Автомат станів Circuit Breaker (Сервіс)", size=14, bold=True, anchor="middle"))
    f.append(line(540, 82, 950, 82, color="#c8ced6", sw=1.2))

    # Три стани CB
    f.append(fitbox(645, 100, 200, 60, "CLOSED (Норма)\nЗапити проходять до БД\nПомилки < Threshold", size=11, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(745, 160, 745, 210, color=POS))
    f.append(text(755, 185, "Error Rate > 50%", size=10, color=POS, bold=True))

    f.append(fitbox(645, 210, 200, 60, "OPEN (Роззомкнено)\nШвидка відмова (Fast Fail)\nВиклик Fallback", size=11, bold=True, fill=RED_T, stroke=POS))
    f.append(arrow(645, 240, 580, 240, color=AMBER))
    f.append(text(612, 225, "Sleep Window\n(e.g., 10s)", size=9, color=AMBER, anchor="middle"))

    f.append(fitbox(645, 320, 200, 60, "HALF-OPEN (Проба)\nТестовий пропуск N запитів\nПеревірка здоров'я", size=11, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(745, 270, 745, 320, color=AMBER))

    f.append(arrow(845, 350, 910, 350, color=FIELD))
    f.append(arrow(910, 350, 910, 130, color=FIELD))
    f.append(arrow(910, 130, 845, 130, color=FIELD))
    f.append(text(920, 240, "Успіх -> Reset", size=10, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, 'dh-resilience-state-matrix.svg'), W, H, *f,
           title="Матриця станів Brownout та Circuit Breaker")

def fig_1800_peak_sequence():
    """Послідовність обробки запитів різного пріоритету під час пікового навантаження 18:00."""
    W, H = 1020, 450
    f = []

    # Колонки суб'єктів
    cols = [
        (60,  "Пристрої / Клієнти"),
        (280, "Edge Gateway (Shedder)"),
        (520, "Worker Pool (Adaptive)"),
        (760, "Downstream (DB / Broker)"),
    ]
    for x, label in cols:
        f.append(fitbox(x, 30, 200, 45, label, size=12, bold=True, fill=NEUT, stroke=INK))
        f.append(line(x + 100, 75, x + 100, 420, color="#d0d7de", sw=1.5, dash="4,4"))

    # Запити та їхні шляхи
    # P4: Video Upload -> Drop at Gateway
    f.append(text(40, 105, "P4 Video Upload", size=10, bold=True, color=PURPLE))
    f.append(arrow(160, 120, 380, 120, color=PURPLE))
    f.append(fitbox(380, 105, 18, 30, "X", size=12, bold=True, fill=RED_T, stroke=POS))
    f.append(line(380, 120, 160, 120, color=POS, dash="2,2"))
    f.append(text(270, 135, "503 Shedded", size=9, color=POS, anchor="middle"))

    # P2: Heartbeat -> Throttled
    f.append(text(40, 175, "P2 Heartbeat", size=10, bold=True, color=AMBER))
    f.append(arrow(160, 190, 380, 190, color=AMBER))
    f.append(fitbox(380, 175, 18, 30, "~", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(line(380, 190, 160, 190, color=AMBER, dash="2,2"))
    f.append(text(270, 205, "429 Throttled", size=9, color=AMBER, anchor="middle"))

    # P0: Door Unlock -> Pass to Worker -> DB -> 200 OK
    f.append(text(40, 245, "P0 Door Unlock", size=10, bold=True, color=FIELD))
    f.append(arrow(160, 260, 380, 260, color=FIELD))
    f.append(arrow(380, 260, 620, 260, color=FIELD))
    f.append(arrow(620, 260, 860, 260, color=FIELD))
    f.append(line(860, 280, 620, 280, color=FIELD, dash="2,2"))
    f.append(line(620, 280, 380, 280, color=FIELD, dash="2,2"))
    f.append(line(380, 280, 160, 280, color=FIELD, dash="2,2"))
    f.append(text(500, 295, "200 OK (p99 < 50ms)", size=9, color=FIELD, anchor="middle"))

    # Async Event Poison Message -> Worker -> Retry -> DLQ
    f.append(text(40, 335, "Async Event (Poison)", size=10, bold=True, color=POS))
    f.append(arrow(160, 350, 620, 350, color=POS))
    f.append(fitbox(620, 340, 18, 30, "!", size=12, bold=True, fill=RED_T, stroke=POS))
    f.append(arrow(620, 370, 860, 370, color=POS))
    f.append(text(740, 385, "Routed to DLQ", size=9, color=POS, anchor="middle"))

    render(os.path.join(OUT, 'dh-resilience-map-pipeline.svg'), W, H, *f,
           title="Повний пайплайн тактик стійкості Digital Homes")

if __name__ == "__main__":
    fig_resilience_map_pipeline()
    fig_resilience_state_matrix()
    fig_1800_peak_sequence()
    print("Figures generated successfully!")
