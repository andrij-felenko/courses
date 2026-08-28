# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Flask і FastAPI'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_wsgi_vs_asgi():
    """Порівняння архітектури WSGI (Gunicorn sync workers) та ASGI (Uvicorn event loop)."""
    w, h = 980, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Архітектурні моделі: WSGI (Синхронна) проти ASGI (Асинхронна)", size=16, bold=True))

    # Ліва колонка: WSGI
    col1_x = 30
    col_w = 445
    frags.append(rect(col1_x, 50, col_w, 450, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(col1_x, 50, col_w, 36, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(col1_x + col_w / 2, 73, "WSGI: Gunicorn + Flask (1 потік / процес на клієнта)", size=13, bold=True, color=POS))

    # Клієнти WSGI
    frags.append(rect(col1_x + 20, 105, 110, 45, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(col1_x + 75, 125, "Сенсор A", size=11, bold=True))
    frags.append(text(col1_x + 75, 140, "HTTP POST", size=9, color=MUTED))

    frags.append(rect(col1_x + 20, 165, 110, 45, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(col1_x + 75, 185, "Сенсор B", size=11, bold=True))
    frags.append(text(col1_x + 75, 200, "HTTP POST", size=9, color=MUTED))

    frags.append(rect(col1_x + 20, 230, 110, 45, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    frags.append(text(col1_x + 75, 250, "Сенсор C (Черга)", size=10, bold=True, color=POS))
    frags.append(text(col1_x + 75, 265, "Очікує воркер", size=9, color=POS))

    # Воркери WSGI
    frags.append(rect(col1_x + 190, 105, 230, 45, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    frags.append(text(col1_x + 305, 124, "Воркер 1 (Блокування)", size=11, bold=True, color=POS))
    frags.append(text(col1_x + 305, 140, "I/O очікування БД (10 мс)", size=9, color=MUTED))
    frags.append(arrow(col1_x + 130, 127, col1_x + 188, 127, color=LINE, sw=1.4))

    frags.append(rect(col1_x + 190, 165, 230, 45, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    frags.append(text(col1_x + 305, 184, "Воркер 2 (Блокування)", size=11, bold=True, color=POS))
    frags.append(text(col1_x + 305, 200, "I/O очікування сокета (15 мс)", size=9, color=MUTED))
    frags.append(arrow(col1_x + 130, 187, col1_x + 188, 187, color=LINE, sw=1.4))

    # Пояснення пулу WSGI
    frags.append(rect(col1_x + 20, 290, 405, 195, fill="#fff9f8", stroke=POS, sw=1.0, rx=6))
    frags.append(text(col1_x + 222, 312, "Обмеження моделі WSGI:", size=11, bold=True, color=POS))
    frags.append(text(col1_x + 35, 335, "• Пул обмежений (наприклад, 4-16 процесів Gunicorn)", size=10, anchor="start"))
    frags.append(text(col1_x + 35, 360, "• Пам'ять: ~30-50 МБ на окремий процес CPython", size=10, anchor="start"))
    frags.append(text(col1_x + 35, 385, "• Потоки ОС: стек 2-8 МБ, дорогий Context Switching", size=10, anchor="start"))
    frags.append(text(col1_x + 35, 410, "• При I/O блокуванні нові сенсори отримують 504 Gateway", size=10, anchor="start"))
    frags.append(text(col1_x + 35, 435, "• Не підтримує довгі відкриті з'єднання (WebSockets)", size=10, anchor="start"))
    frags.append(text(col1_x + 35, 460, "• Межа пропускної здатності: сотні req/sec", size=10, anchor="start", bold=True))

    # Права колонка: ASGI
    col2_x = 505
    frags.append(rect(col2_x, 50, col_w, 450, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(col2_x, 50, col_w, 36, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col2_x + col_w / 2, 73, "ASGI: Uvicorn + FastAPI (Event Loop + Корутини)", size=13, bold=True, color=FIELD))

    # Клієнти ASGI
    frags.append(rect(col2_x + 20, 105, 105, 170, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(col2_x + 72, 130, "10 000+", size=12, bold=True, color=FIELD))
    frags.append(text(col2_x + 72, 150, "Одночасних", size=10))
    frags.append(text(col2_x + 72, 170, "сенсорів", size=10))
    frags.append(text(col2_x + 72, 200, "HTTP / WS", size=9, color=MUTED))
    frags.append(text(col2_x + 72, 220, "Keep-Alive", size=9, color=MUTED))
    frags.append(text(col2_x + 72, 245, "Non-blocking", size=9, color=FIELD))

    # Event Loop Uvicorn
    frags.append(rect(col2_x + 180, 105, 245, 170, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=6))
    frags.append(text(col2_x + 302, 126, "Цикл подій (uvloop / epoll)", size=11, bold=True, color=FIELD))
    frags.append(line(col2_x + 190, 136, col2_x + 415, 136, color=FIELD, sw=1.0))

    frags.append(rect(col2_x + 195, 145, 215, 26, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    frags.append(text(col2_x + 302, 162, "Task 1: Sensor A (await db.save)", size=9))

    frags.append(rect(col2_x + 195, 177, 215, 26, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    frags.append(text(col2_x + 302, 194, "Task 2: Sensor B (parsing Pydantic)", size=9))

    frags.append(rect(col2_x + 195, 209, 215, 26, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    frags.append(text(col2_x + 302, 226, "Task N: Sensor N (ready in epoll)", size=9))

    frags.append(rect(col2_x + 195, 241, 215, 26, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    frags.append(text(col2_x + 302, 258, "1 потік ОС обробляє всі задачі", size=9, bold=True, color=FIELD))

    frags.append(arrow(col2_x + 125, 190, col2_x + 178, 190, color=FIELD, sw=1.8))

    # Переваги моделі ASGI
    frags.append(rect(col2_x + 20, 290, 405, 195, fill="#f4fbf7", stroke=FIELD, sw=1.0, rx=6))
    frags.append(text(col2_x + 222, 312, "Переваги моделі ASGI:", size=11, bold=True, color=FIELD))
    frags.append(text(col2_x + 35, 335, "• Кооперативна багатозадачність (async/await)", size=10, anchor="start"))
    frags.append(text(col2_x + 35, 360, "• Пам'ять: ~2-4 КБ на корутину замість мегабайтів потоку", size=10, anchor="start"))
    frags.append(text(col2_x + 35, 385, "• Безперервна обробка I/O через ядра epoll / kqueue", size=10, anchor="start"))
    frags.append(text(col2_x + 35, 410, "• Нативна підтримка WebSockets та Streaming HTTP", size=10, anchor="start"))
    frags.append(text(col2_x + 35, 435, "• Нульові витрати на перемикання контексту ОС ядра", size=10, anchor="start"))
    frags.append(text(col2_x + 35, 460, "• Пропускна здатність: 20 000+ req/sec на процес", size=10, anchor="start", bold=True))

    render(os.path.join(OUT_DIR, "wsgi-vs-asgi-architecture.svg"), w, h, *frags)


def fig_telemetry_pipeline():
    """Покроковий конвеєр прийому та валідації телеметрії у FastAPI."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр прийому телеметрії IoT у FastAPI з Pydantic v2 та DI", size=16, bold=True))

    steps = [
        ("1. Вхідний запит", [
            "HTTP POST /api/v1/telemetry",
            "TCP сокет -> Uvicorn ASGI",
            "Словник scope: 'http'",
            "Неблокувальний receive()"
        ], "#eaf0fd", NEG),

        ("2. Pydantic v2 (Rust Core)", [
            "Парсинг JSON у C/Rust шарі",
            "Перевірка діапазонів (ge, le)",
            "ISO 8601 -> datetime об'єкт",
            "Авто-відповідь 422 Unprocessable"
        ], "#fdecea", POS),

        ("3. Впровадження залежностей", [
            "Depends(verify_device_token)",
            "Depends(get_db_session)",
            "Обчислення графа залежностей",
            "Контроль життєвого циклу ресурсів"
        ], "#fef9e7", "#b78103"),

        ("4. Асинхронний бекенд", [
            "Ендпоінт async def ingest_data()",
            "await db.telemetry.insert(...)",
            "Неблокувальний драйвер asyncpg",
            "Публікація в Redis/MQTT чергу"
        ], "#e8f8f0", FIELD),
    ]

    card_w = 215
    card_h = 240
    gap = 26
    start_x = 25
    y_pos = 65

    for i, (title, bullets, fill_c, stroke_c) in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        frags.append(rect(cx, y_pos, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        frags.append(text(cx + card_w / 2, y_pos + 26, title, size=11, bold=True, color=stroke_c))
        frags.append(line(cx + 8, y_pos + 36, cx + card_w - 8, y_pos + 36, color=stroke_c, sw=1.0))

        for b_idx, bullet in enumerate(bullets):
            frags.append(text(cx + 10, y_pos + 62 + b_idx * 34, "• " + bullet, size=9, anchor="start", color=INK))

        if i < len(steps) - 1:
            ax1 = cx + card_w + 3
            ay1 = y_pos + card_h / 2
            ax2 = cx + card_w + gap - 3
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.6))

    # Нижній пояснювальний блок
    bottom_y = 330
    frags.append(rect(start_x, bottom_y, w - 2 * start_x, 125, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, bottom_y + 24, "Ключова оптимізація FastAPI: асинхронний нерозривний конвеєр", size=12, bold=True))
    frags.append(text(start_x + 20, bottom_y + 52, "• Валідація виконується в pydantic-core (написаному на Rust), що в 5-15 разів швидше за Marshmallow/чистий Python.", size=10, anchor="start"))
    frags.append(text(start_x + 20, bottom_y + 76, "• Ендпоінт не виділяє окремий потік операційної системи під час очікування відповіді від бази даних (I/O Wait).", size=10, anchor="start"))
    frags.append(text(start_x + 20, bottom_y + 100, "• Помилки валідації повертають стандартизований RFC 7807 JSON з точним шляхом до некоректного датчика чи поля.", size=10, anchor="start"))

    render(os.path.join(OUT_DIR, "telemetry-processing-pipeline.svg"), w, h, *frags)


def fig_concurrency_latency():
    """Порівняння масштабованості: затримка P99 та споживання пам'яті при зростанні навантаження."""
    w, h = 980, 500
    frags = []

    frags.append(text(w / 2, 26, "Масштабованість IoT-сервера: P99 Latency та Пам'ять (100 - 10 000 з'єднань)", size=16, bold=True))

    # Графік 1: Затримка P99 (Latency)
    g1_x, g1_y, g_w, g_h = 45, 60, 420, 260
    frags.append(rect(g1_x, g1_y, g_w, g_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(g1_x + g_w / 2, g1_y + 24, "Затримка відповіді (P99 Latency)", size=12, bold=True))

    # Осі
    frags.append(line(g1_x + 50, g1_y + 220, g1_x + 390, g1_y + 220, color=LINE, sw=1.4))
    frags.append(line(g1_x + 50, g1_y + 50, g1_x + 50, g1_y + 220, color=LINE, sw=1.4))

    # Підписи осей
    frags.append(text(g1_x + 395, g1_y + 224, "RPS / Сенсори", size=9, anchor="start", color=MUTED))
    frags.append(text(g1_x + 48, g1_y + 42, "мс", size=9, anchor="end", color=MUTED))

    # Позначки осі X
    for idx, label in enumerate(["100", "500", "2000", "5000", "10000"]):
        lx = g1_x + 60 + idx * 75
        frags.append(line(lx, g1_y + 220, lx, g1_y + 224, color=LINE, sw=1.0))
        frags.append(text(lx, g1_y + 238, label, size=9, color=MUTED))

    # Крива WSGI (експоненційне зростання)
    frags.append(line(g1_x + 60, g1_y + 205, g1_x + 135, g1_y + 190, color=POS, sw=2.2))
    frags.append(line(g1_x + 135, g1_y + 190, g1_x + 210, g1_y + 130, color=POS, sw=2.2))
    frags.append(line(g1_x + 210, g1_y + 130, g1_x + 285, g1_y + 65, color=POS, sw=2.2))
    frags.append(line(g1_x + 285, g1_y + 65, g1_x + 360, g1_y + 55, color=POS, sw=2.2, dash="3,3"))
    frags.append(text(g1_x + 260, g1_y + 80, "WSGI (черга переповнена)", size=9, color=POS, bold=True))

    # Крива ASGI (майже плоска)
    frags.append(line(g1_x + 60, g1_y + 212, g1_x + 135, g1_y + 210, color=FIELD, sw=2.2))
    frags.append(line(g1_x + 135, g1_y + 210, g1_x + 210, g1_y + 205, color=FIELD, sw=2.2))
    frags.append(line(g1_x + 210, g1_y + 205, g1_x + 285, g1_y + 195, color=FIELD, sw=2.2))
    frags.append(line(g1_x + 285, g1_y + 195, g1_x + 360, g1_y + 185, color=FIELD, sw=2.2))
    frags.append(text(g1_x + 290, g1_y + 175, "ASGI (uvloop)", size=9, color=FIELD, bold=True))

    # Графік 2: Споживання пам'яті (RAM)
    g2_x = 515
    frags.append(rect(g2_x, g1_y, g_w, g_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(g2_x + g_w / 2, g1_y + 24, "Споживання пам'яті (RAM)", size=12, bold=True))

    # Осі
    frags.append(line(g2_x + 50, g1_y + 220, g2_x + 390, g1_y + 220, color=LINE, sw=1.4))
    frags.append(line(g2_x + 50, g1_y + 50, g2_x + 50, g1_y + 220, color=LINE, sw=1.4))

    # Підписи осей
    frags.append(text(g2_x + 395, g1_y + 224, "З'єднання", size=9, anchor="start", color=MUTED))
    frags.append(text(g2_x + 48, g1_y + 42, "МБ", size=9, anchor="end", color=MUTED))

    # Позначки осі X
    for idx, label in enumerate(["100", "500", "2000", "5000", "10000"]):
        lx = g2_x + 60 + idx * 75
        frags.append(line(lx, g1_y + 220, lx, g1_y + 224, color=LINE, sw=1.0))
        frags.append(text(lx, g1_y + 238, label, size=9, color=MUTED))

    # Крива WSGI (лінійне зростання від кількості процесів/потоків)
    frags.append(line(g2_x + 60, g1_y + 195, g2_x + 135, g1_y + 165, color=POS, sw=2.2))
    frags.append(line(g2_x + 135, g1_y + 165, g2_x + 210, g2_x - 395, color=POS, sw=2.2))
    frags.append(line(g2_x + 210, g1_y + 115, g2_x + 285, g1_y + 70, color=POS, sw=2.2))
    frags.append(text(g2_x + 265, g1_y + 60, "WSGI (потоки ОС)", size=9, color=POS, bold=True))

    # Крива ASGI (низьке повільне зростання)
    frags.append(line(g2_x + 60, g1_y + 210, g2_x + 135, g1_y + 205, color=FIELD, sw=2.2))
    frags.append(line(g2_x + 135, g1_y + 205, g2_x + 210, g1_y + 198, color=FIELD, sw=2.2))
    frags.append(line(g2_x + 210, g1_y + 198, g2_x + 285, g1_y + 190, color=FIELD, sw=2.2))
    frags.append(line(g2_x + 285, g1_y + 190, g2_x + 360, g1_y + 180, color=FIELD, sw=2.2))
    frags.append(text(g2_x + 295, g1_y + 172, "ASGI (корутини)", size=9, color=FIELD, bold=True))

    # Нижній висновок
    bot_y = 345
    frags.append(rect(45, bot_y, w - 90, 130, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, bot_y + 24, "Висновки для високонавантаженої телеметрії:", size=12, bold=True))
    frags.append(text(65, bot_y + 54, "1. WSGI-сервери (Gunicorn sync) вичерпують пул потоків при досягненні ліміту паралельних з'єднань.", size=10, anchor="start"))
    frags.append(text(65, bot_y + 78, "2. Будь-яка затримка у зовнішньому сервісі чи БД спричиняє каскадне зростання черги й виснаження пам'яті у WSGI.", size=10, anchor="start"))
    frags.append(text(65, bot_y + 102, "3. ASGI-сервер (Uvicorn/FastAPI) утримує стабільну затримку завдяки неблокувальному мультиплексуванню сокетів.", size=10, anchor="start"))

    render(os.path.join(OUT_DIR, "concurrency-memory-latency.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_wsgi_vs_asgi()
    fig_telemetry_pipeline()
    fig_concurrency_latency()
    print("All figures generated successfully.")
