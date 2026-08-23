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

def fig_metastable_loop_hysteresis():
    """Петля метастабільної відмови та гістерезис продуктивності."""
    W, H = 1020, 440
    f = []

    # Первинне перевантаження та підсилення
    f.append(fitbox(50, 40, 230, 70, "Зовнішній тригер / сплеск\n(Cold Cache / DB Outage)\nLoad L > Capacity C", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(50, 160, 230, 70, "Зростання затримок\n(Latency Spike & Queues)\nT_response > T_timeout", size=12, bold=True, fill=RED_T, stroke=POS))

    f.append(fitbox(50, 280, 230, 70, "Шторм повторів (Retries)\nW(L) = 1 + r · P_retry(L)\nПідсилення роботи W > 1", size=12, bold=True, fill=PURPLE_T, stroke="#8b5cf6"))

    # Стрілки петлі підсилення (Feedback Loop)
    f.append(arrow(165, 110, 165, 160, color=AMBER, sw=2))
    f.append(arrow(165, 230, 165, 280, color=POS, sw=2))

    # Зворотна стрілка від Retries до Load (Позитивний зворотний зв'язок)
    f.append(line(50, 315, 15, 315, color="#8b5cf6", sw=2))
    f.append(line(15, 315, 15, 75, color="#8b5cf6", sw=2))
    f.append(arrow(15, 75, 50, 75, color="#8b5cf6", sw=2))

    # Графік гістерезису
    f.append(fitbox(320, 40, 660, 360, "", size=10, fill=BG, stroke=INK))

    # Вісі графіка
    f.append(arrow(380, 350, 940, 350, color=INK, sw=2)) # X: Зовнішнє навантаження L
    f.append(text(930, 375, "Зовнішнє навантаження (L)", size=12, color=INK, anchor="end"))

    f.append(arrow(380, 350, 380, 70, color=INK, sw=2)) # Y: Внутрішнє навантаження / Latency
    f.append(text(390, 65, "Внутрішнє навантаження W(L) / Latency", size=12, color=INK, anchor="start"))

    # Стабільна гілка (Нижня лінія)
    f.append(line(380, 340, 700, 280, color=POS, sw=3))
    f.append(text(530, 325, "Стабільна гілка (W ≈ 1)", size=12, color=POS))

    # Зрив у метастабільний стан (Пунктир вгору при L_crit)
    f.append(line(700, 280, 700, 120, color=AMBER, sw=2, dash="4 4"))
    f.append(text(710, 200, "Точка зриву (L_crit)", size=11, color=AMBER))

    # Метастабільна гілка (Верхня лінія перевантаження)
    f.append(line(700, 120, 480, 140, color=POS, sw=3))
    f.append(text(530, 105, "Метастабільна відмова (W >> 1)", size=12, color=POS))

    # Відновлення (Пунктир вниз при L_rec)
    f.append(line(480, 140, 480, 324, color="#8b5cf6", sw=2, dash="4 4"))
    f.append(text(490, 220, "Поріг скидання (L_rec << L_crit)", size=11, color="#8b5cf6"))

    render(os.path.join(OUT, 'metastable-loop-hysteresis.svg'), W, H, *f,
           title="Петля метастабільної відмови та гістерезис продуктивності")

def fig_retry_storm_amplification():
    """Каскадна спіраль повторних запитів (Retry Death Spiral)."""
    W, H = 980, 420
    f = []

    f.append(fitbox(40, 50, 180, 70, "Клієнти / App\nT_timeout = 2.0s\nRetry count = 3", size=12, bold=True, fill=NEUT, stroke=INK))

    f.append(fitbox(300, 50, 200, 70, "API Gateway / LB\nRouting & Retries\nActive Connection Pool", size=12, bold=True, fill=BLUE_T, stroke=NEG))

    f.append(fitbox(580, 50, 360, 70, "Backend Сервіс (Обробник)\nОбробка запиту = 2.5s (Деградація)\nQueue Capacity = EXHAUSTED", size=12, bold=True, fill=RED_T, stroke=POS))

    f.append(arrow(220, 85, 300, 85, color=INK, sw=2))
    f.append(text(260, 75, "Запит #1 (t=0s)", size=11, color=INK, anchor="middle"))

    f.append(arrow(500, 85, 580, 85, color=POS, sw=2))
    f.append(text(540, 75, "Обробка", size=11, color=POS, anchor="middle"))

    f.append(fitbox(40, 200, 900, 180, "Хронологія марної роботи (Wasted Work):\n1. t=0.0s — Клієнт надсилає Запит #1. Сервіс починає важке обчислення.\n2. t=2.0s — У клієнта спрацьовує таймаут T_timeout. Клієнт анулює чекання і генерує Повтор #2.\n3. t=2.5s — Сервіс завершує Запит #1 і надсилає відповідь, але клієнт її вже відкинув! (Марний CPU/RAM).\n4. t=4.0s — Повтор #2 падає за таймаутом. Клієнт генерує Повтор #3. Навантаження на сервіс зростає втричі.", size=12, fill=PURPLE_T, stroke="#8b5cf6"))

    render(os.path.join(OUT, 'retry-storm-amplification.svg'), W, H, *f,
           title="Каскадна спіраль повторних запитів та марна робота")

def fig_connection_pool_starvation():
    """Каскадне виснаження пулів з'єднань і голодування потоків."""
    W, H = 1000, 420
    f = []

    f.append(fitbox(40, 60, 180, 80, "Вхідні HTTP Клієнти\n(10 000 r/s)\n503 Service Unavailable", size=12, bold=True, fill=RED_T, stroke=POS))

    f.append(fitbox(300, 60, 220, 80, "API Gateway Workers\nThread Pool (200 threads)\nСТАН: Blocked / Waiting", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(600, 60, 180, 80, "DB Connection Pool\n(Max 50 connections)\n100% EXHAUSTED", size=12, bold=True, fill=PURPLE_T, stroke="#8b5cf6"))

    f.append(fitbox(840, 60, 120, 80, "Slow DB / Lock\nRTT: 5s", size=12, bold=True, fill=RED_T, stroke=POS))

    f.append(arrow(220, 100, 300, 100, color=POS, sw=2))
    f.append(text(260, 90, "Запити", size=11, color=POS, anchor="middle"))

    f.append(arrow(520, 100, 600, 100, color=AMBER, sw=2))
    f.append(text(560, 90, "Acquire", size=11, color=AMBER, anchor="middle"))

    f.append(arrow(780, 100, 840, 100, color="#8b5cf6", sw=2))
    f.append(text(810, 90, "Query", size=11, color="#8b5cf6", anchor="middle"))

    f.append(fitbox(40, 220, 920, 160, "Механізм каскадного блокування за Законом Літтла (N = λ · W):\n1. Затримка бази даних зростає з 10 ms до 500 ms (у 50 разів).\n2. Усі 50 з'єднань у пулі виявляються зайнятими тривалими запитами.\n3. Воркери API чекають на вільне з'єднання з пулу і блокують свої потоки.\n4. Пул потоків API (200 threads) повністю виснажується за декілька секунд.\n5. API Gateway припиняє приймати нові HTTP-з'єднання й відкидає трафік.", size=12, fill=BG, stroke=INK))

    render(os.path.join(OUT, 'connection-pool-starvation.svg'), W, H, *f,
           title="Каскадне виснаження пулів з'єднань і голодування потоків")

def fig_load_shedding_circuit_breaker():
    """Архітектурний бар'єр захисту від метастабільних пасток."""
    W, H = 1040, 420
    f = []

    f.append(fitbox(40, 70, 160, 70, "Вхідний потік\n(Всі запити)", size=12, bold=True, fill=NEUT, stroke=INK))

    f.append(fitbox(240, 50, 220, 110, "1. Adaptive Load Shedder\n(CoDel Queue / Tokens)\nСкидання надлишку L > C\nHTTP 429 / 503 + Retry-After", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(fitbox(500, 50, 230, 110, "2. Circuit Breaker\n(Closed / Open / Half-Open)\nЗрізання повторних запитів\nRetry Budget (Token Bucket ≤ 10%)", size=12, bold=True, fill=BLUE_T, stroke=NEG))

    f.append(fitbox(770, 50, 230, 110, "3. Connection Pool Guard\n(Sema Bulkhead & Coalesce)\nЗахист від Thundering Herd\nSingleflight & Fast-Fail Timeout", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    f.append(arrow(200, 105, 240, 105, color=INK, sw=2))
    f.append(arrow(460, 105, 500, 105, color=FIELD, sw=2))
    f.append(arrow(730, 105, 770, 105, color=NEG, sw=2))

    f.append(fitbox(500, 280, 500, 80, "Захищене джерело правди / Backend Сервіси\n(Обробляє лише підсилений, але стабільний потік L ≤ Capacity C)", size=13, bold=True, fill=PURPLE_T, stroke="#8b5cf6"))

    f.append(arrow(885, 160, 885, 280, color=AMBER, sw=2))
    f.append(text(895, 220, "Безпечний потік", size=11, color=AMBER, anchor="start"))

    render(os.path.join(OUT, 'load-shedding-circuit-breaker.svg'), W, H, *f,
           title="Трирівневий бар'єр захисту від метастабільних відмов")

if __name__ == '__main__':
    fig_metastable_loop_hysteresis()
    fig_retry_storm_amplification()
    fig_connection_pool_starvation()
    fig_load_shedding_circuit_breaker()
    print("Figures generated successfully!")
