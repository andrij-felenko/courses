# -*- coding: utf-8 -*-
"""Фігури до кроку «Фінал тактик змін і кешування DH» (модуль 26)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

TINT_G = "#eef7f0"   # світло-зелений фон (успіх / цільовий стан)
TINT_R = "#fdecea"   # світло-червоний фон (старий стан / небезпека)
TINT_B = "#eef2fd"   # світло-синій фон (транзитний стан / підготовка)
TINT_Y = "#fffceb"   # світло-жовтий фон (буфер / перевірка)


def fig_twin_migration_phases():
    """Анатомія zero-downtime міграції цифрового твіна DH: 4 фази переходу."""
    W, H = 1080, 680
    cx = 540
    frags = []

    # Заголовок блоку
    frags.append(text(cx, 40, "4-фазна zero-downtime міграція цифрового твіна Digital Homes (Б → В)",
                      size=16, bold=True, color=INK))

    phases = [
        ("Фаза 0: Baseline (Стабільний стан Б)",
         TINT_R, POS,
         "100% запитів іде на Твін Б (PostgreSQL + Redis). Твін В не існує або в розробці.\n"
         "• Відкат: Не потрібен • Ризик: 0 • Метрика mismatch: N/A"),

        ("Фаза 1: Expand & Dual-Write (Подвійний запис і порівняння)",
         TINT_Y, LINE,
         "Запис синхронно в Б + через Outbox в Kafka → Твін В. Читання з Б. Verification Harness порівнює 1% відповідей.\n"
         "• Відкат: Вимкнути dual_write_flag • Метрика mismatch: twin_mismatch_total → 0"),

        ("Фаза 2: Switch Read Primary & Backfill (Перемикання читання і тротльований backfill)",
         TINT_B, NEG,
         "Онлайн-backfill історичних твінів Б → В (тротлінг 500 req/s). Читання з В, Fallback на Б при помилках.\n"
         "• ТОЧКА НЕПОВЕРНЕННЯ: В стає джерелом нової телеметрії • Відкат: Потребує реверсного backfill"),

        ("Фаза 3: Contract & Deprecate B (Завершення та відключення Б)",
         TINT_G, FIELD,
         "100% читань і записів тільки через Твін В. Твін Б відключено, таблиці архівуються після 72г без fallback.\n"
         "• Цільовий стан: Event-Driven CQRS твін без боргу • SLO доступності: 99.99%"),
    ]

    x0, w = 60, 960
    ry = 70
    step = 138

    for i, (p_title, tint, border_col, p_desc) in enumerate(phases):
        y = ry + i * step
        frags.append(rect(x0, y, w, 116, fill=tint, stroke=border_col, sw=1.6, rx=8))
        # Ліва кольорова смужка-акцент
        frags.append(rect(x0, y, 10, 116, fill=border_col, stroke=border_col, sw=1, rx=0))
        frags.append(text(x0 + 26, y + 32, p_title, size=15, color=INK, bold=True, anchor="start"))

        lines = p_desc.split("\n")
        frags.append(text(x0 + 26, y + 60, lines[0], size=12.5, color=INK, anchor="start"))
        frags.append(text(x0 + 26, y + 86, lines[1], size=11.5, color=MUTED, bold=True, anchor="start"))

        if i < len(phases) - 1:
            frags.append(arrow(cx, y + 116, cx, y + step, color=INK, sw=2.0))

    render(os.path.join(IMG, "twin-migration-phases.svg"), W, H, *frags,
           title="4-фазна zero-downtime міграція цифрового твіна DH від Варіанта Б до В")


def fig_cache_coherence_lag():
    """Схема інвалідації кешу подіями, лагу телеметрії та захисту від Cache Stampede."""
    W, H = 1080, 600
    frags = []

    # Ліва частина: Подійний інвалідатор кешу
    frags.append(rect(40, 50, 480, 500, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(280, 82, "Подійна інвалідація та Read-Your-Writes", size=15, bold=True, color=INK))

    # Складові лівої частини
    box1, _, _ = textbox(280, 140, "Зміна стану: Твін В (Outbox)", size=13, fill=TINT_B, stroke=NEG, bold=True)
    box2, _, _ = textbox(280, 230, "Kafka Topic: twin.state_changed\n(payload: home_id, ETag, version_seq)", size=12, fill=FILL, stroke=LINE)
    box3, _, _ = textbox(280, 330, "Gateway / BFF Cache Invalidator\n(Перевіряє: event.version > cache.version)", size=12, fill=TINT_Y, stroke=LINE)
    box4, _, _ = textbox(280, 440, "Redis Edge Cache (Версійний запис)\n+ Read-Your-Writes Header (X-Min-Version)", size=12, fill=TINT_G, stroke=FIELD, bold=True)

    frags.extend([box1, box2, box3, box4])
    frags.append(arrow(280, 166, 280, 204, color=LINE, sw=1.6))
    frags.append(arrow(280, 260, 280, 302, color=LINE, sw=1.6))
    frags.append(arrow(280, 360, 280, 412, color=LINE, sw=1.6))

    # Права частина: Телеметрія, Read Model Lag та Cache Stampede
    frags.append(rect(560, 50, 480, 500, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(800, 82, "Чесний лаг телеметрії та Singleflight", size=15, bold=True, color=INK))

    box5, _, _ = textbox(800, 140, "Датчик / MQTT → Ingestion Pipeline\n(Мережевий & batching лаг Δt ≈ 350-2500ms)", size=12, fill=FILL, stroke=LINE)
    box6, _, _ = textbox(800, 240, "Read Model DTO (Двохчасовий штамп):\nupdatedAt (твін) vs observedAt (датчик)", size=12, fill=TINT_B, stroke=NEG, bold=True)
    box7, _, _ = textbox(800, 340, "Request Coalescing (Singleflight):\n100 запитів / 50ms → 1 виклик до DB", size=12, fill=TINT_Y, stroke=LINE)
    box8, _, _ = textbox(800, 440, "Клієнтський UX (Мобільний застосунок):\nІндикатор свіжості ('Оновлено 2с тому')", size=12, fill=TINT_G, stroke=FIELD, bold=True)

    frags.extend([box5, box6, box7, box8])
    frags.append(arrow(800, 172, 800, 212, color=LINE, sw=1.6))
    frags.append(arrow(800, 272, 800, 312, color=LINE, sw=1.6))
    frags.append(arrow(800, 372, 800, 412, color=LINE, sw=1.6))

    render(os.path.join(IMG, "cache-coherence-lag.svg"), W, H, *frags,
           title="Інвалідація кешу подіями, управління лагом телеметрії та захист від шторму")


if __name__ == "__main__":
    fig_twin_migration_phases()
    fig_cache_coherence_lag()
    print("OK: twin-migration-phases.svg, cache-coherence-lag.svg")
