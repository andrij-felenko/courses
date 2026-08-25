# -*- coding: utf-8 -*-
"""Фігури до теми «Узгодження вмісту (content negotiation)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"


# ── 1. Чотири виміри узгодження ───────────────────────────────────────────────
def fig_negotiation_dimensions():
    W, H = 940, 490
    f = [text(W / 2, 28, "Чотири виміри узгодження представлення ресурсу", size=16, bold=True)]

    # Ліва частина — Клієнт з 4 заголовками Accept-*
    f.append(rect(30, 60, 360, 390, fill=PANEL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(210, 90, "КЛІЄНТ: ЗАГОЛОВКИ ПЕРЕВАГ", size=13, color=NEG, bold=True))

    headers = [
        ("Accept", "Формат / MIME-тип", "application/json;q=1, text/html;q=0.8"),
        ("Accept-Language", "Мова й регіон", "uk-UA, en-US;q=0.7, *;q=0.1"),
        ("Accept-Encoding", "Алгоритм стиснення", "zstd, br, gzip, identity"),
        ("Accept-Charset", "Набір символів", "utf-8 (де-факто стандарт)"),
    ]

    y_pos = 112
    for name, desc, ex in headers:
        f.append(fitbox(50, y_pos, 320, 72, f"{name}\n{desc}\n{ex}", size=11, fill="#ffffff", stroke="#d0d7de"))
        y_pos += 80

    # Центр — Стрілки переходу
    for y_arrow in [148, 228, 308, 388]:
        f.append(arrow(380, y_arrow, 440, 255, color=LINE, sw=1.5))

    # Центральний вузол — Сервер і селектор
    f.append(fitbox(450, 185, 150, 140, "СЕРВЕР\n\nАбстрактний\nресурс /report\n\nМатриця\nваріантів", size=12, fill="#eef2fb", stroke=NEG, bold=True))

    # Стрілка від сервера до обраного представлення
    f.append(arrow(610, 255, 660, 255, color=FIELD, sw=2.0))

    # Права частина — Обране представлення (байти + метадані)
    f.append(rect(670, 60, 240, 390, fill="#f4fcf6", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(790, 90, "ОБРАНЕ ПРЕДСТАВЛЕННЯ", size=13, color=FIELD, bold=True))

    resp_boxes = [
        ("Content-Type", "application/json"),
        ("Content-Language", "uk-UA"),
        ("Content-Encoding", "zstd"),
        ("Vary", "Accept, Accept-Language, Accept-Encoding"),
    ]

    y_resp = 115
    for hname, hval in resp_boxes:
        f.append(fitbox(685, y_resp, 210, 58, f"{hname}\n{hval}", size=11, fill="#ffffff", stroke="#b7eb8f"))
        y_resp += 66

    f.append(fitbox(685, 385, 210, 50, "Тіло відповіді\n[байти JSON у zstd]", size=11, fill="#ffffff", stroke=FIELD, bold=True))

    render(os.path.join(IMG, "negotiation-dimensions.svg"), W, H, *f)


# ── 2. Проактивне проти реактивного узгодження ──────────────────────────────
def fig_proactive_vs_reactive():
    W, H = 940, 500
    f = [text(W / 2, 28, "Проактивне (серверне) проти реактивного (клієнтського) узгодження", size=16, bold=True)]

    # Верхня панель — Проактивне (1 RTT)
    f.append(rect(30, 50, 880, 195, fill=PANEL, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(50, 78, "ПРОАКТИВНЕ УЗГОДЖЕННЯ (SERVER-DRIVEN) — 1 ОБМІН (1 RTT)", size=12.5, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(60, 100, 110, 48, "Клієнт", size=12, fill="#ffffff", stroke=LINE))
    f.append(fitbox(770, 100, 120, 48, "Сервер", size=12, fill="#ffffff", stroke=LINE))

    # Стрілка туди
    f.append(arrow(180, 115, 760, 115, color=NEG, sw=1.6))
    f.append(text(470, 108, "GET /document  [Accept: application/json; Accept-Language: uk]", size=11, color=NEG))

    # Обробка на сервері
    f.append(fitbox(750, 155, 150, 36, "Вибір варіанта\n(алгоритм на сервері)", size=10, fill="#eaf0fd", stroke=NEG))

    # Стрілка назад
    f.append(arrow(760, 205, 180, 205, color=FIELD, sw=1.6))
    f.append(text(470, 198, "200 OK  [Content-Type: application/json; Content-Language: uk; Vary: Accept, ...]", size=11, color=FIELD))
    f.append(fitbox(60, 185, 110, 42, "Готові дані\n(0 затримок)", size=11, fill="#f4fcf6", stroke=FIELD))

    # Нижня панель — Реактивне (2 RTT)
    f.append(rect(30, 265, 880, 215, fill=PANEL, stroke=AMBER, sw=1.5, rx=8))
    f.append(text(50, 292, "РЕАКТИВНЕ УЗГОДЖЕННЯ (CLIENT-DRIVEN) — 2 ОБМІНИ (2 RTT)", size=12.5, color=AMBER, anchor="start", bold=True))

    f.append(fitbox(60, 310, 110, 44, "Клієнт", size=12, fill="#ffffff", stroke=LINE))
    f.append(fitbox(770, 310, 120, 44, "Сервер", size=12, fill="#ffffff", stroke=LINE))

    # Запит 1
    f.append(arrow(180, 322, 760, 322, color=LINE, sw=1.4))
    f.append(text(470, 315, "1. GET /video  (без специфікації)", size=11, color=INK))

    # Відповідь 1 (300 Multiple Choices)
    f.append(arrow(760, 355, 180, 355, color=AMBER, sw=1.4))
    f.append(text(470, 348, "2. 300 Multiple Choices  [Перелік: 1080p (/v-hd), 720p (/v-md), 480p (/v-sd)]", size=11, color=AMBER))

    # Вибір клієнта
    f.append(fitbox(60, 375, 110, 36, "Клієнт обирає\n1080p за шириною", size=10, fill="#fef9e7", stroke=AMBER))

    # Запит 2
    f.append(arrow(180, 422, 760, 422, color=NEG, sw=1.4))
    f.append(text(470, 415, "3. GET /video/v-hd  (конкретний вибраний URI)", size=11, color=NEG))

    # Відповідь 2
    f.append(arrow(760, 455, 180, 455, color=FIELD, sw=1.4))
    f.append(text(470, 448, "4. 200 OK  [Тіло потоку 1080p]", size=11, color=FIELD))

    render(os.path.join(IMG, "proactive-vs-reactive.svg"), W, H, *f)


# ── 3. Вплив заголовка Vary на кеш ───────────────────────────────────────────
def fig_vary_cache_matrix():
    W, H = 940, 520
    f = [text(W / 2, 28, "Вплив заголовка Vary на формування ключів кеша", size=16, bold=True)]

    # Верхня частина — БЕЗ Vary (катастрофа / отруєння)
    f.append(rect(30, 50, 880, 205, fill="#fff5f5", stroke=POS, sw=1.6, rx=8))
    f.append(text(50, 76, "БЕЗ VARY: КЕШУВАННЯ ЗА ЄДИНИМ КЛЮЧЕМ URI (ОТРУЄННЯ КЕША)", size=12.5, color=POS, anchor="start", bold=True))

    # Клієнт 1
    f.append(fitbox(50, 95, 170, 50, "Клієнт A (UA, Brotli)\nAccept-Lang: uk\nAccept-Enc: br", size=10.5, fill="#ffffff", stroke=LINE))
    f.append(arrow(225, 120, 360, 120, color=LINE, sw=1.4))

    # Кеш (проміжний проксі)
    f.append(fitbox(370, 95, 180, 50, "Проміжний кеш CDN\nКлюч: [GET /article]", size=11, fill="#ffffff", stroke=POS, bold=True))
    f.append(arrow(555, 120, 690, 120, color=LINE, sw=1.4))
    f.append(fitbox(700, 95, 180, 50, "Сервер джерела\nВіддає: UK / Brotli\n(забув Vary!)", size=11, fill="#ffffff", stroke=LINE))

    # Другий запит — Клієнт 2 (помилка)
    f.append(fitbox(50, 160, 170, 50, "Клієнт B (EN, без br)\nAccept-Lang: en\nAccept-Enc: identity", size=10.5, fill="#ffffff", stroke=LINE))
    f.append(arrow(225, 185, 360, 185, color=LINE, sw=1.4))
    f.append(arrow(360, 195, 225, 195, color=POS, sw=1.8))
    f.append(fitbox(450, 160, 430, 50, "ХИБНЕ ПОТРАПЛЯННЯ В КЕШ (CACHE POISONING):\nКлієнту B віддано закешовані байти UK + Brotli!\nБраузер показує сміття замість англійського тексту.", size=10.5, fill="#ffffff", stroke=POS, color=POS, bold=True))

    # Нижня частина — З Vary (правильна ізоляція)
    f.append(rect(30, 275, 880, 225, fill="#f6ffed", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(50, 302, "З VARY: СКЛАДЕНИЙ КЛЮЧ КЕША (ПОВНА ІЗОЛЯЦІЯ ВАРІАНТІВ)", size=12.5, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(50, 325, 180, 65, "Клієнт A (UA, br)\nAccept-Lang: uk\nAccept-Enc: br", size=10.5, fill="#ffffff", stroke=LINE))
    f.append(fitbox(50, 410, 180, 65, "Клієнт B (EN, gzip)\nAccept-Lang: en\nAccept-Enc: gzip", size=10.5, fill="#ffffff", stroke=LINE))

    # Стрілки
    f.append(arrow(235, 355, 335, 355, color=LINE, sw=1.4))
    f.append(arrow(235, 440, 335, 440, color=LINE, sw=1.4))

    # Кеш зі складеними ключами
    f.append(rect(345, 320, 260, 165, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(475, 342, "Складені ключі кеша CDN:", size=11, bold=True, color=FIELD))
    f.append(fitbox(355, 355, 240, 55, "Ключ 1: [/article | uk | br]\n→ Закешовано відповідь A", size=10.5, fill="#f4fcf6", stroke="#b7eb8f"))
    f.append(fitbox(355, 420, 240, 55, "Ключ 2: [/article | en | gzip]\n→ Закешовано відповідь B", size=10.5, fill="#f4fcf6", stroke="#b7eb8f"))

    # Сервер
    f.append(fitbox(660, 355, 230, 120, "Сервер додає заголовок:\nVary: Accept-Language,\n      Accept-Encoding\n\nКожен клієнт дістає свій\nнезалежний кеш-слот.", size=11, fill="#ffffff", stroke=FIELD))
    f.append(arrow(608, 385, 652, 385, color=LINE, sw=1.4))

    render(os.path.join(IMG, "vary-cache-matrix.svg"), W, H, *f)


# ── 4. Ієрархія специфічності та q-фактори ──────────────────────────────────
def fig_specificity_weights():
    W, H = 940, 460
    f = [text(W / 2, 28, "Ієрархія специфічності та якісні коефіцієнти (q-value)", size=16, bold=True)]

    # Сходинки специфічності (зверху вниз від найбільш специфічного)
    steps = [
        ("Рівень 4: Повний MIME-тип з параметрами", "application/json; version=2; charset=utf-8", "Специфічність: 3", "q = 1.0 (найвищий)", FIELD, "#f4fcf6"),
        ("Рівень 3: Конкретний точний підтип", "application/json  або  text/html", "Специфічність: 2", "q = 0.9 (або дефолт 1.0)", NEG, "#eaf0fd"),
        ("Рівень 2: Діапазон типу з підстановочним знаком", "text/*  або  image/*", "Специфічність: 1", "q = 0.5 (будь-який text/)", AMBER, "#fef9e7"),
        ("Рівень 1: Універсальний підстановочний знак", "*/*", "Специфічність: 0", "q = 0.1 (запасний для всього)", GRAY, "#f5f5f5"),
    ]

    y_step = 60
    for title, example, spec, qval, col, bgcol in steps:
        # Ліва плашка з назвою та прикладом
        f.append(rect(40, y_step, 540, 80, fill=bgcol, stroke=col, sw=1.5, rx=6))
        f.append(text(60, y_step + 28, title, size=12, color=col, anchor="start", bold=True))
        f.append(text(60, y_step + 56, f"Приклад: {example}", size=11, color=INK, anchor="start"))

        # Плашка специфічності
        f.append(fitbox(590, y_step, 140, 80, spec, size=11, fill="#ffffff", stroke=col, color=col, bold=True))

        # Плашка q-значення
        f.append(fitbox(740, y_step, 160, 80, qval, size=11, fill="#ffffff", stroke=col, color=col, bold=True))

        y_step += 88

    # Пояснення внизу
    f.append(rect(40, 415, 860, 36, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(470, 437, "Правило RFC 9110: Спершу порівнюється q-коефіцієнт; при однакових q перемагає вища специфічність.", size=11, bold=True))

    render(os.path.join(IMG, "specificity-weights.svg"), W, H, *f)


if __name__ == '__main__':
    fig_negotiation_dimensions()
    fig_proactive_vs_reactive()
    fig_vary_cache_matrix()
    fig_specificity_weights()
    print("All figures generated successfully.")
