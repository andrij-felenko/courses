# -*- coding: utf-8 -*-
"""Фігури до теми «Фонові запити зі сторінки: часткове оновлення без перезавантаження» (client-architecture)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def panel(x, y, w, h, head, sub=None):
    """Панель із заголовком угорі; повертає (svg, внутрішній верх)."""
    s = rect(x, y, w, h, fill="#ffffff", stroke="#b8c2cc", sw=1.6, rx=10)
    s += text(x + w / 2, y + 26, head, size=15, bold=True)
    if sub:
        s += text(x + w / 2, y + 44, sub, size=12, color=MUTED)
        return s, y + 56
    return s, y + 42


# ── 1. Повне перезавантаження проти фонового часткового оновлення ─────────────
def fig_full_reload_vs_partial_update():
    W, H = 1060, 520
    P, PW, PH, PY = [40, 550], 470, 430, 55
    s = ""

    # Ліва панель: Повне перезавантаження
    px = P[0]
    p, top = panel(px, PY, PW, PH, "Повне перезавантаження сторінки", "скидання стану й повторний парсинг")
    s += p
    cx = px + PW / 2

    b1, _, _ = textbox(cx, top + 35, "1. Клік користувача (перехід/форма)", size=12, min_w=370, fill="#f4f6f8")
    s += b1
    s += arrow(cx, top + 55, cx, top + 85, color=LINE)

    b2, _, _ = textbox(cx, top + 115, "2. Знищення DOM, зупинка JS-таймерів,\nбілий спалах (White Flash), втрата фокусу", size=11, min_w=370, fill="#fdecea", stroke=POS)
    s += b2
    s += arrow(cx, top + 145, cx, top + 175, color=LINE)

    b3, _, _ = textbox(cx, top + 205, "3. Отримання повного HTML-документа,\nповторне завантаження CSS, шрифтів і JS", size=11, min_w=370, fill="#fdfbf7", stroke="#d97706")
    s += b3
    s += arrow(cx, top + 235, cx, top + 265, color=LINE)

    b4, _, _ = textbox(cx, top + 295, "4. Повний конвеєр: Parse -> Layout -> Paint\nСкидання позиції прокрутки (Scroll loss)", size=11, min_w=370, fill="#fdecea", stroke=POS)
    s += b4

    # Права панель: Фонові запити й часткова підміна
    px = P[1]
    p, top = panel(px, PY, PW, PH, "Фоновий запит і часткове оновлення", "точкова мутація зі збереженням контексту")
    s += p
    cx = px + PW / 2

    b1, _, _ = textbox(cx, top + 35, "1. Подія введення або клік у віджеті", size=12, min_w=370, fill="#f4f6f8")
    s += b1
    s += arrow(cx, top + 55, cx, top + 85, color=FIELD)

    b2, _, _ = textbox(cx, top + 115, "2. Неблоківний фоновий транспорт (Fetch/SSE)\nUI активний: фокус у полі, скрол на місці", size=11, min_w=370, fill="#eafaf1", stroke=FIELD)
    s += b2
    s += arrow(cx, top + 145, cx, top + 175, color=FIELD)

    b3, _, _ = textbox(cx, top + 205, "3. Передавання лише дельти (JSON / HTML-фрагмент)\nМінімальний мережевий трафік (RTT)", size=11, min_w=370, fill="#eaf0fd", stroke=NEG)
    s += b3
    s += arrow(cx, top + 235, cx, top + 265, color=FIELD)

    b4, _, _ = textbox(cx, top + 295, "4. Локальна заміна вузла DOM (Morphing / Patch)\nАнімації тривають, стан сесії не втрачається", size=11, min_w=370, fill="#eafaf1", stroke=FIELD, sw=1.8)
    s += b4

    render(os.path.join(OUT, "full-reload-vs-partial-update.svg"), W, H, s,
           title="Повне перезавантаження проти фонового часткового оновлення DOM")


# ── 2. Еволюція мережевих транспортів у браузері ──────────────────────────────
def fig_transport_evolution():
    W, H = 1060, 520
    s = ""

    # Етап 1: Hidden iframe / Image ping
    b1 = rect(50, 50, 960, 75, fill="#f4f6f8", stroke="#8c9ba5", sw=1.5, rx=8)
    b1 += text(80, 78, "1995–1999: Приховані фрейми (Hidden <iframe> / Image Beacon)", size=13, bold=True, anchor="start")
    b1 += text(80, 102, "Хак: форма відправлялася у прихований фрейм, скрипт парсив parent.window. Повільно й ламко.", size=11, color=MUTED, anchor="start")
    s += b1

    s += arrow(530, 125, 530, 140, color=LINE)

    # Етап 2: XMLHttpRequest
    b2 = rect(50, 140, 960, 75, fill="#eef3f8", stroke=NEG, sw=1.6, rx=8)
    b2 += text(80, 168, "1999–2005: XMLHttpRequest (XHR) та народження AJAX", size=13, bold=True, color=NEG, anchor="start")
    b2 += text(80, 192, "Перший нативний асинхронний HTTP-транспорт. Callback-модель (onreadystatechange), важка буферизація.", size=11, color=MUTED, anchor="start")
    s += b2

    s += arrow(530, 215, 530, 230, color=LINE)

    # Етап 3: Server-Sent Events (SSE)
    b3 = rect(50, 230, 960, 75, fill="#fdfbf7", stroke="#d97706", sw=1.6, rx=8)
    b3 += text(80, 258, "2009+: Server-Sent Events (EventSource / text/event-stream)", size=13, bold=True, color="#b45309", anchor="start")
    b3 += text(80, 282, "Односпрямований потік повідомлень від сервера до клієнта поверх звичайного HTTP. Авто-перепідключення.", size=11, color=MUTED, anchor="start")
    s += b3

    s += arrow(530, 305, 530, 320, color=LINE)

    # Етап 4: WebSocket
    b4 = rect(50, 320, 960, 75, fill="#fbf4fd", stroke="#8e44ad", sw=1.6, rx=8)
    b4 += text(80, 348, "2011+: WebSocket (RFC 6455)", size=13, bold=True, color="#8e44ad", anchor="start")
    b4 += text(80, 372, "Повнодуплексний TCP-канал поверх єдиного з'єднання. Мінімальний оверхед кадрів для частих подій.", size=11, color=MUTED, anchor="start")
    s += b4

    s += arrow(530, 395, 530, 410, color=FIELD)

    # Етап 5: Fetch API + Streams + AbortController
    b5 = rect(50, 410, 960, 75, fill="#eafaf1", stroke=FIELD, sw=2, rx=8)
    b5 += text(80, 438, "2015+: Fetch API, ReadableStream та AbortController", size=13, bold=True, color=FIELD, anchor="start")
    b5 += text(80, 462, "Promise-базований API, потокове читання байтів (bytestream), скасування запитів та стандартизований пайплайн.", size=11, color=MUTED, anchor="start")
    s += b5

    render(os.path.join(OUT, "transport-evolution-timeline.svg"), W, H, s,
           title="Еволюція мережевих фонових транспортів у вебклієнті")


# ── 3. Порівняння підходів: JSON API проти HTML-over-the-wire та RSC ─────────
def fig_payload_models():
    W, H = 1060, 510
    s = ""

    W_COL, H_COL, Y_COL = 310, 420, 55
    COLS = [40, 375, 710]

    # Колонка 1: JSON REST/GraphQL (SPA)
    px = COLS[0]
    p, top = panel(px, Y_COL, W_COL, H_COL, "JSON API (Клієнтський SPA)", "дані окремо від розмітки")
    s += p
    cx = px + W_COL / 2

    c1, _, _ = textbox(cx, top + 35, "Сервер віддає сирий JSON:\n`{ id: 42, title: 'Item' }`", size=11, min_w=270, fill="#f4f8fb", stroke=NEG)
    s += c1
    s += arrow(cx, top + 70, cx, top + 110, color=LINE)

    c2, _, _ = textbox(cx, top + 140, "Клієнт завантажує JS-шаблонізатор,\nкомпоненти й Virtual DOM (~50–300 КБ)", size=11, min_w=270, fill="#fdecea", stroke=POS)
    s += c2
    s += arrow(cx, top + 175, cx, top + 215, color=LINE)

    c3, _, _ = textbox(cx, top + 255, "Парсинг JSON -> Diff VDOM ->\nгенерація DOM-вузлів у браузері\n(навантаження на процесор клієнта)", size=11, min_w=270, fill="#f4f8fb")
    s += c3

    # Колонка 2: HTML-over-the-wire (HTMX / Turbo)
    px = COLS[1]
    p, top = panel(px, Y_COL, W_COL, H_COL, "HTML-over-the-wire", "HTMX, Hotwire Turbo")
    s += p
    cx = px + W_COL / 2

    c1, _, _ = textbox(cx, top + 35, "Сервер генерує готовий фрагмент:\n`<div id='todo-42'>...</div>`", size=11, min_w=270, fill="#fdfbf7", stroke="#d97706")
    s += c1
    s += arrow(cx, top + 70, cx, top + 110, color=FIELD)

    c2, _, _ = textbox(cx, top + 140, "Мінімальний клієнтський рантайм\n(10–15 КБ без важких SPA-фреймворків)", size=11, min_w=270, fill="#eafaf1", stroke=FIELD)
    s += c2
    s += arrow(cx, top + 175, cx, top + 215, color=FIELD)

    c3, _, _ = textbox(cx, top + 255, "Пряма підміна (DOM Morphing):\nелемент замінюється на льоту,\nстан іншого дерева не чіпається", size=11, min_w=270, fill="#eafaf1", stroke=FIELD, sw=1.8)
    s += c3

    # Колонка 3: React Server Components (RSC)
    px = COLS[2]
    p, top = panel(px, Y_COL, W_COL, H_COL, "React Server Components", "потоковий граф віртуальних вузлів")
    s += p
    cx = px + W_COL / 2

    c1, _, _ = textbox(cx, top + 35, "Сервер рендерить компоненти й\nстрімить RSC wire format (рядки JSON)", size=11, min_w=270, fill="#fbf4fd", stroke="#8e44ad")
    s += c1
    s += arrow(cx, top + 70, cx, top + 110, color=LINE)

    c2, _, _ = textbox(cx, top + 140, "Код серверних компонентів НЕ летить\nу бандл браузера (економія пам'яті)", size=11, min_w=270, fill="#eafaf1", stroke=FIELD)
    s += c2
    s += arrow(cx, top + 175, cx, top + 215, color=FIELD)

    c3, _, _ = textbox(cx, top + 255, "Потокова реконсиляція графа:\nвбудовування частин у клієнтський VDOM\nзі збереженням стану клієнтських кнопок", size=11, min_w=270, fill="#f4f8fb")
    s += c3

    render(os.path.join(OUT, "html-over-wire-vs-json-rsc.svg"), W, H, s,
           title="Архітектури часткового оновлення: JSON API, HTML-over-the-wire та RSC")


# ── 4. Гонка асинхронних запитів та AbortController ──────────────────────────
def fig_out_of_order_race_abort():
    W, H = 1060, 520
    s = ""

    # Ліва панель: Аномалія некерованих запитів
    p1, top1 = panel(40, 55, 475, 430, "Аномалія неупорядкованих відповідей", "повільний старий запит затирає новий")
    s += p1
    c1 = 40 + 475 / 2

    # Хронологія
    s += line(c1 - 180, top1 + 30, c1 + 180, top1 + 30, color=LINE, sw=1.2)
    s += text(c1 - 170, top1 + 22, "t = 0 мс", size=11, color=MUTED)
    s += text(c1, top1 + 22, "t = 150 мс", size=11, color=MUTED)
    s += text(c1 + 170, top1 + 22, "t = 600 мс", size=11, color=MUTED)

    b1, _, _ = textbox(c1, top1 + 75, "Введення «ca» (t=0): Запит #1 вирушає\n(затримка мережі RTT = 600 мс)", size=11, min_w=430, fill="#f4f8fb")
    b2, _, _ = textbox(c1, top1 + 155, "Введення «cat» (t=150): Запит #2 вирушає\n(швидка відповідь RTT = 120 мс)", size=11, min_w=430, fill="#eef3f8")
    b3, _, _ = textbox(c1, top1 + 235, "t = 270 мс: Прийшла відповідь на Запит #2 («cat»)\nСписок результатів оновлено під «cat» (коректно)", size=11, min_w=430, fill="#eafaf1", stroke=FIELD)
    b4, _, _ = textbox(c1, top1 + 325, "t = 600 мс: Із запізненням прийшла відповідь #1 («ca»)\nUI безконтрольно перезаписано застарілим списком «ca»!", size=11, min_w=430, fill="#fdecea", stroke=POS, sw=2)
    s += b1 + b2 + b3 + b4

    # Права панель: Синхронізація через AbortController та Sequence ID
    p2, top2 = panel(545, 55, 475, 430, "Захист: AbortController і нумерація версій", "скасування сокета та відсікання застарілих даних")
    s += p2
    c2 = 545 + 475 / 2

    s += line(c2 - 180, top2 + 30, c2 + 180, top2 + 30, color=LINE, sw=1.2)
    s += text(c2 - 170, top2 + 22, "t = 0 мс", size=11, color=MUTED)
    s += text(c2, top2 + 22, "t = 150 мс", size=11, color=MUTED)
    s += text(c2 + 170, top2 + 22, "t = 600 мс", size=11, color=MUTED)

    b5, _, _ = textbox(c2, top2 + 75, "Введення «ca» (t=0): Запит req_id=1\nСтворено AbortController #1", size=11, min_w=430, fill="#f4f8fb")
    b6, _, _ = textbox(c2, top2 + 155, "Введення «cat» (t=150): Запит req_id=2\ncontroller1.abort() -> обриває Запит #1 у мережі", size=11, min_w=430, fill="#eef3f8")
    b7, _, _ = textbox(c2, top2 + 235, "t = 270 мс: Відповідь req_id=2 застосовано\nUI показує вичерпні результати для «cat»", size=11, min_w=430, fill="#eafaf1", stroke=FIELD)
    b8, _, _ = textbox(c2, top2 + 325, "t = 600 мс: Відповідь #1 викидає AbortError\nабо відхиляється перевіркою (req_id=1 < latest=2)", size=11, min_w=430, fill="#eafaf1", stroke=FIELD, sw=2)
    s += b5 + b6 + b7 + b8

    render(os.path.join(OUT, "out-of-order-race-abort.svg"), W, H, s,
           title="Гонка відповідей фонових запитів: аномалія перезаписування та захист AbortController")


# ── 5. Скінченний автомат фонового часткового запиту ──────────────────────────
def fig_request_state_machine():
    W, H = 1060, 520
    s = ""

    # Стан 1: IDLE
    b_idle, _, _ = textbox(130, 250, "IDLE\n(стан спокою / очікування)", size=12, min_w=160, fill="#ffffff", stroke="#8c9ba5")
    s += b_idle

    s += arrow(215, 250, 305, 250, color=LINE)
    s += text(260, 235, "trigger()", size=11, bold=True)

    # Стан 2: LOADING
    b_load, _, _ = textbox(420, 250, "LOADING\n1. Ініціалізація AbortController\n2. Показ Skeleton / Spinner\n3. Блокування дублікатів", size=11, min_w=220, fill="#fdfbf7", stroke="#d97706", sw=1.8)
    s += b_load

    s += arrow(535, 250, 615, 250, color=LINE)
    s += text(575, 235, "Fetch()", size=11, bold=True)

    # Стан 3: STREAMING (якщо потік)
    b_stream, _, _ = textbox(720, 250, "STREAMING\nПотокове читання байтів\n(ReadableStream / SSE chunks)", size=11, min_w=200, fill="#fbf4fd", stroke="#8e44ad")
    s += b_stream

    # Гілка вгору: Успіх (SETTLED_SUCCESS)
    s += arrow(825, 220, 895, 130, color=FIELD)
    s += text(875, 165, "2xx OK", size=11, bold=True, color=FIELD)

    b_succ, _, _ = textbox(940, 105, "SETTLED_SUCCESS\n1. Атомарний DOM Morph\n2. Збереження фокусу/скролу\n3. Очищення індикаторів", size=11, min_w=200, fill="#eafaf1", stroke=FIELD, sw=2)
    s += b_succ

    # Гілка прямо: Тимчасовий збій мережі (RETRYING_BACKOFF)
    s += arrow(825, 250, 880, 250, color="#b45309")
    s += text(850, 235, "503/Offline", size=10, bold=True, color="#b45309")

    b_retry, _, _ = textbox(940, 250, "RETRYING_BACKOFF\n1. Exponential Backoff + Jitter\n2. Індикатор «З'єднання...»\n3. Повторне надсилання", size=11, min_w=200, fill="#fdfbf7", stroke="#d97706", sw=1.8)
    s += b_retry

    # Гілка вниз: Фатальна помилка (ERROR_STATE)
    s += arrow(825, 280, 895, 380, color=POS)
    s += text(875, 345, "4xx/Abort", size=11, bold=True, color=POS)

    b_err, _, _ = textbox(940, 410, "ERROR_STATE\n1. Відображення банера помилки\n2. Відкат оптимістичних змін\n3. Кнопка «Повторити дію»", size=11, min_w=200, fill="#fdecea", stroke=POS, sw=2)
    s += b_err

    # Повернення в IDLE
    s += arrow(940, 50, 130, 50, color=FIELD)
    s += line(940, 70, 940, 50, color=FIELD)
    s += line(130, 50, 130, 215, color=FIELD)
    s += text(530, 40, "Завершення мутації та перехід у стан готовності", size=11, color=MUTED)

    render(os.path.join(OUT, "request-lifecycle-state-machine.svg"), W, H, s,
           title="Скінченний автомат життєвого циклу фонового часткового оновлення")


if __name__ == "__main__":
    fig_full_reload_vs_partial_update()
    fig_transport_evolution()
    fig_payload_models()
    fig_out_of_order_race_abort()
    fig_request_state_machine()
    print("Всі фігури для ajax-partial-updates згенеровано успішно.")
