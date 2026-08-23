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

def fig_stale_spectrum():
    """Спектр стратегій обробки лагу: від сліпого обману до чесної деградації."""
    W, H = 1020, 380
    f = []

    f.append(fitbox(510, 35, 420, 36, "Спектр архітектурних рішень при лагу даних", size=15, bold=True, fill=NEUT, stroke=INK))

    # Три колони — кожен блок як окрема автономна картка з верхнім заголовком і нижнім тілом
    cols = [
        (185, "1. Сліпий обман", "Fake Realtime", [
            "• Приховує лаг реплікації",
            "• Видає старе за свіже",
            "• Ризик: хибні дії клієнта",
            "• Подвійні списання / плутанина"
        ], "Поганий UX: фальшива довіра", RED_T, POS),
        (510, "2. Жорсткий блок", "Synchronous Wait", [
            "• Блокує UI спинером",
            "• Нищить доступність системи",
            "• Зависання при збоях мережі",
            "• Висока латентність читання"
        ], "Важкий UX: вимагає 100% мережу", AMBER_T, AMBER),
        (835, "3. Чесна деградація", "Honest Stale UX", [
            "• Миттєвий вивід кешу (SWR)",
            "• Бейдж: «Оновлено 3 хв тому»",
            "• Авто-корекція + фоновий fetch",
            "• Перехід у Read-Only режим"
        ], "Передбачуваний UX: прозорість", GREEN_T, FIELD)
    ]

    for cx, t1, t2, bullet_list, btm, bg_col, border_col in cols:
        # Головна картка
        f.append(rect(cx - 145, 80, 290, 260, fill=bg_col, stroke=border_col, sw=1.8))
        # Заголовок всередині
        f.append(text(cx, 110, t1, size=14, bold=True, color=border_col))
        f.append(text(cx, 130, t2, size=11, italic=True, color=MUTED))
        f.append(line(cx - 125, 142, cx + 125, 142, color=border_col, sw=1.0))
        # Текст кулею
        f.append(mtext(cx, 165, bullet_list, size=12, color=INK, anchor="middle", lh=1.4))
        # Нижня плашка
        f.append(line(cx - 125, 295, cx + 125, 295, color=border_col, sw=1.0))
        f.append(text(cx, 318, btm, size=11, bold=True, color=border_col))

    render(os.path.join(OUT, 'fig1-stale-spectrum.svg'), W, H, *f,
           title="Спектр стратегій обробки лагу даних")

def fig_freshness_pipeline():
    """Наскрізний пайплайн передачі метаданих свіжості від БД до UI."""
    W, H = 1040, 360
    f = []

    # 1. Primary DB / Write Model
    f.append(fitbox(100, 140, 150, 80, "Write DB\n\nPrimary Master\n[t = t0]", size=12, bold=True, fill=NEUT, stroke=INK))
    
    # Arrow to Event Bus
    f.append(arrow(175, 140, 265, 140))
    f.append(text(220, 128, "CDC / Event", size=10, color=MUTED))

    # 2. Read Projection & Replication Lag
    f.append(fitbox(355, 140, 180, 80, "Read Projection\n\nCQRS View Store\n[t = t0 + Δt_lag]", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Arrow to API Service
    f.append(arrow(445, 140, 520, 140))
    f.append(text(482, 128, "SQL / Query", size=10, color=MUTED))

    # 3. API Gateway / Service
    f.append(fitbox(625, 140, 210, 100, "API Gateway / Service\n\nОбгортка метаданими:\nfetchedAt, lagMs, isStale", size=12, bold=True, fill=BG, stroke=INK))

    # Arrow to Client SWR Store
    f.append(arrow(730, 140, 805, 140))
    f.append(text(767, 128, "HTTP Envelope", size=10, color=MUTED))

    # 4. Client SWR Cache & UI
    f.append(fitbox(910, 140, 190, 120, "Client App & UI\n\nSWR Cache Engine\n↓\nBadge: «Оновлено 45с»\n[Muted UI + Revalidate]", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Lower annotation box for SLAs
    f.append(fitbox(520, 280, 720, 45, "Скрізь передається часова мітка правди (timestamp) -> Обчислення лагу на кожному кроці", size=12, bold=True, fill=BLUE_T, stroke=NEG))

    render(os.path.join(OUT, 'fig2-freshness-pipeline.svg'), W, H, *f,
           title="Наскрізний пайплайн метаданих свіжості")

def fig_optimistic_correction_flow():
    """Потік оптимістичного запису з візуалізацією наміру та підтвердження."""
    W, H = 1000, 380
    f = []

    # Timeline axis
    f.append(line(80, 70, 920, 70, color=INK, sw=2))
    f.append(text(920, 55, "Час (t)", size=12, bold=True, color=INK, anchor="end"))

    # Event 1: User action
    f.append(circle(120, 70, 6, fill=INK, stroke=INK))
    f.append(fitbox(120, 120, 160, 60, "t1: Клік «Увімкнути»\n\nЮзер тисне кнопку", size=11, fill=BG, stroke=INK))

    # Arrow to Optimistic Render
    f.append(arrow(120, 155, 300, 155))

    # Event 2: Pending State
    f.append(circle(300, 70, 6, fill=AMBER, stroke=AMBER))
    f.append(fitbox(300, 120, 180, 70, "t2: Optimistic Render\n\nUI: «Вмикається...»\nDesired: ON, Reported: OFF", size=11, bold=True, fill=AMBER_T, stroke=AMBER))

    # Arrow split: Scenario A (Success) vs Scenario B (Failure)
    f.append(arrow(390, 155, 520, 240))
    f.append(arrow(390, 155, 520, 310))

    # Scenario A: Backend ACK -> Confirmed State
    f.append(fitbox(640, 240, 240, 55, "Сценарій А: Сервер ACK (200 OK)\nUI: Стан підтверджено [ON]", size=11, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(760, 240, 850, 240))
    f.append(fitbox(905, 240, 110, 40, "Стабільність", size=11, fill=BG, stroke=FIELD))

    # Scenario B: Backend Reject/Timeout -> Rollback & Alert
    f.append(fitbox(640, 310, 240, 55, "Сценарій Б: Збій / Помилка (500)\nUI: Відкат [OFF] + Alert баннер", size=11, bold=True, fill=RED_T, stroke=POS))
    f.append(arrow(760, 310, 850, 310))
    f.append(fitbox(905, 310, 110, 40, "Корекція UX", size=11, fill=BG, stroke=POS))

    render(os.path.join(OUT, 'fig3-optimistic-correction-flow.svg'), W, H, *f,
           title="Потік оптимістичного запису та узгодження стану")

if __name__ == '__main__':
    fig_stale_spectrum()
    fig_freshness_pipeline()
    fig_optimistic_correction_flow()
    print("Figures generated successfully.")
