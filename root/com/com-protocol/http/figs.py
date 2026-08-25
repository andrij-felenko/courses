# -*- coding: utf-8 -*-
"""Фігури до теми «HTTP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"
BLUE  = "#2457d6"
GREEN = "#27ae60"
RED   = "#c0392b"
CARD  = "#f4f6f8"


# ── 1. Анатомія повідомлення HTTP/1.1 ─────────────────────────────────────────
def fig_message_anatomy():
    W, H = 940, 480
    f = [text(W / 2, 28, "Анатомія текстового повідомлення HTTP/1.1", size=16, bold=True)]

    # Ліва колонка — Запит, Права колонка — Відповідь
    col_w = 440
    gap = 20
    x_req = 20
    x_resp = x_req + col_w + gap

    # Панель Запиту
    f.append(rect(x_req, 50, col_w, 400, fill=PANEL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_req + col_w / 2, 76, "ЗАПИТ КЛІЄНТА (REQUEST)", size=13, color=BLUE, bold=True))

    # Стартовий рядок (Request-Line)
    f.append(fitbox(x_req + 15, 96, col_w - 30, 44, "GET /api/v2/orders/42 HTTP/1.1\n[Метод] [Шлях ресурсу / URI] [Версія]",
                    size=11, bold=True, fill="#eaf0fd", stroke=BLUE))

    # Заголовки запиту
    f.append(fitbox(x_req + 15, 150, col_w - 30, 110,
                    "Host: api.example.com\nUser-Agent: BackendService/1.0\nAccept: application/json\nContent-Type: application/json\n[Заголовки: ключ: значення (CRLF)]",
                    size=11, fill="#fdfbf0", stroke=AMBER))

    # Роздільник CRLF
    f.append(fitbox(x_req + 15, 270, col_w - 30, 36, "\\r\\n (порожній рядок — однозначна межа заголовків)",
                    size=11, bold=True, fill="#fdecea", stroke=RED))

    # Тіло запиту
    f.append(fitbox(x_req + 15, 316, col_w - 30, 114,
                    '{"customer_id": 8104, "status": "active"}\n\n[Тіло повідомлення / Payload]\n(визначається через Content-Length або Transfer-Encoding)',
                    size=11, fill="#eef6ef", stroke=GREEN))

    # Панель Відповіді
    f.append(rect(x_resp, 50, col_w, 400, fill=PANEL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_resp + col_w / 2, 76, "ВІДПОВІДЬ СЕРВЕРА (RESPONSE)", size=13, color=GREEN, bold=True))

    # Стартовий рядок (Status-Line)
    f.append(fitbox(x_resp + 15, 96, col_w - 30, 44, "HTTP/1.1 200 OK\n[Версія] [Код стану] [Пояснення]",
                    size=11, bold=True, fill="#eef6ef", stroke=GREEN))

    # Заголовки відповіді
    f.append(fitbox(x_resp + 15, 150, col_w - 30, 110,
                    "Date: Thu, 20 Aug 2026 08:30:00 GMT\nContent-Type: application/json; charset=utf-8\nContent-Length: 48\nConnection: keep-alive\n[Заголовки: ключ: значення (CRLF)]",
                    size=11, fill="#fdfbf0", stroke=AMBER))

    # Роздільник CRLF
    f.append(fitbox(x_resp + 15, 270, col_w - 30, 36, "\\r\\n (порожній рядок — однозначна межа заголовків)",
                    size=11, bold=True, fill="#fdecea", stroke=RED))

    # Тіло відповіді
    f.append(fitbox(x_resp + 15, 316, col_w - 30, 114,
                    '{"id": 42, "status": "ready", "total": 128.50}\n\n[Тіло повідомлення / Payload]\n(байти даних згідно з Content-Type та довжиною)',
                    size=11, fill="#eaf0fd", stroke=BLUE))

    render(os.path.join(IMG, 'http-message-anatomy.svg'), W, H, *f)


# ── 2. Еволюція транспорту й блокування черги ────────────────────────────────
def fig_transport_evolution():
    W, H = 940, 520
    f = [text(W / 2, 28, "Еволюція транспорту: подолання блокування черги (Head-of-Line Blocking)", size=16, bold=True)]

    panel_h = 136
    px = 20
    pw = 900

    # 1. HTTP/1.1 Pipelining
    y1 = 52
    f.append(rect(px, y1, pw, panel_h, fill=PANEL, stroke=RED, sw=1.5, rx=8))
    f.append(text(px + 20, y1 + 24, "HTTP/1.1 PIPELINING (1 TCP-з'єднання)", size=12, color=RED, anchor="start", bold=True))
    f.append(fitbox(px + 20, y1 + 44, 250, 72, "Запити надсилаються пачкою:\nReq 1 (важкий SQL)\nReq 2 (стиль CSS)\nReq 3 (логотип PNG)",
                    size=10.5, fill="#fdecea", stroke=RED))
    f.append(arrow(px + 280, y1 + 80, px + 330, y1 + 80, color=LINE, sw=1.5))
    f.append(fitbox(px + 340, y1 + 44, 530, 72,
                    "ВІДПОВІДІ СУВОРО ЗА ЧЕРГОЮ: Resp 1 (обробка 3 с) → Resp 2 (чекає!) → Resp 3 (чекає!)\n"
                    "Блокування початку черги на рівні HTTP: швидкі ресурси заблоковані важким запитом.",
                    size=11, fill="#fdecea", stroke=RED, color=RED, bold=True))

    # 2. HTTP/2 Multiplexing
    y2 = 204
    f.append(rect(px, y2, pw, panel_h, fill=PANEL, stroke=AMBER, sw=1.5, rx=8))
    f.append(text(px + 20, y2 + 24, "HTTP/2 MULTIPLEXING (1 TCP-з'єднання, незалежні логічні потоки)", size=12, color=AMBER, anchor="start", bold=True))
    f.append(fitbox(px + 20, y2 + 44, 250, 72, "Запити розбиваються на бінарні кадри:\nStream 1 (кадри даних)\nStream 2 (кадри даних)\nStream 3 (кадри даних)",
                    size=10.5, fill="#fdfbf0", stroke=AMBER))
    f.append(arrow(px + 280, y2 + 80, px + 330, y2 + 80, color=LINE, sw=1.5))
    f.append(fitbox(px + 340, y2 + 44, 530, 72,
                    "КАДРИ ЧЕРГУЮТЬСЯ В ОДНОМУ TCP-СОКЕТІ: [S2 Frame] [S3 Frame] [S1 Frame 1] [S2 Frame 2]...\n"
                    "HTTP HoL знято! Але втрата одного IP-пакета блокує весь TCP-буфер для ВСІХ потоків.",
                    size=11, fill="#fdfbf0", stroke=AMBER, color=INK))

    # 3. HTTP/3 QUIC over UDP
    y3 = 356
    f.append(rect(px, y3, pw, panel_h, fill=PANEL, stroke=GREEN, sw=1.5, rx=8))
    f.append(text(px + 20, y3 + 24, "HTTP/3 QUIC (UDP-дейтаграми, фізично незалежні потоки)", size=12, color=GREEN, anchor="start", bold=True))
    f.append(fitbox(px + 20, y3 + 44, 250, 72, "Потоки QUIC поверх UDP:\nПотік A (незалежні пакети)\nПотік B (незалежні пакети)\nПотік C (незалежні пакети)",
                    size=10.5, fill="#eef6ef", stroke=GREEN))
    f.append(arrow(px + 280, y3 + 80, px + 330, y3 + 80, color=LINE, sw=1.5))
    f.append(fitbox(px + 340, y3 + 44, 530, 72,
                    "ВТРАТА ПАКЕТА В ПОТОЦІ A НЕ ВПЛИВАЄ НА ПОТОКИ B І C:\n"
                    "Повна відсутність блокування черги як на рівні HTTP, так і на рівні транспорту + 0-RTT рукостискання.",
                    size=11, fill="#eef6ef", stroke=GREEN, color=GREEN, bold=True))

    render(os.path.join(IMG, 'http-multiplexing-vs-pipelining.svg'), W, H, *f)


# ── 3. Матриця властивостей HTTP-методів ─────────────────────────────────────
def fig_methods_matrix():
    W, H = 940, 430
    f = [text(W / 2, 26, "Семантичні властивості методів HTTP (RFC 9110)", size=16, bold=True)]

    # Заголовок таблиці
    headers = [
        ("Метод", 130),
        ("Безпечний (Safe)", 180),
        ("Ідемпотентний (Idempotent)", 220),
        ("Кешований (Cacheable)", 190),
        ("Тіло запиту", 160)
    ]

    x_start = 30
    y_start = 54
    row_h = 44

    # Малюємо заголовок
    cur_x = x_start
    for name, w in headers:
        f.append(fitbox(cur_x, y_start, w, 38, name, size=11.5, bold=True, fill="#eef2fb", stroke=BLUE))
        cur_x += w + 6

    # Рядки
    rows_data = [
        ("GET", "ТАК (тільки читання)", "ТАК", "ТАК (за замовчуванням)", "Не використовується", GREEN, GREEN, GREEN),
        ("HEAD", "ТАК (тільки метадані)", "ТАК", "ТАК", "Не використовується", GREEN, GREEN, GREEN),
        ("OPTIONS", "ТАК (запит можливостей)", "ТАК", "НІ", "Рідко (без семантики)", GREEN, GREEN, RED),
        ("PUT", "НІ (створює / замінює)", "ТАК (N разів = 1 раз)", "НІ (інвалідує кеш)", "Обов'язкове (повний стан)", RED, GREEN, RED),
        ("DELETE", "НІ (видаляє ресурс)", "ТАК (N разів = 1 раз)", "НІ (інвалідує кеш)", "Не рекомендовано", RED, GREEN, RED),
        ("POST", "НІ (обробка / мутація)", "НІ (N викликів = N дій)", "Умовно (з явним Cache-Control)", "Типове (вхідні дані)", RED, RED, AMBER),
        ("PATCH", "НІ (часткова зміна)", "НІ (у загальному випадку)", "НІ (інвалідує кеш)", "Обов'язкове (набір правок)", RED, RED, RED),
    ]

    for idx, (m, safe, idem, cache, body, c_s, c_i, c_c) in enumerate(rows_data):
        y = y_start + 44 + idx * row_h
        cx = x_start

        # Метод
        f.append(fitbox(cx, y, headers[0][1], row_h - 6, m, size=12, bold=True, fill="#ffffff", stroke=LINE))
        cx += headers[0][1] + 6

        # Safe
        f.append(fitbox(cx, y, headers[1][1], row_h - 6, safe, size=10.5, bold=True,
                        fill=("#eef6ef" if c_s == GREEN else "#fdecea"), stroke=c_s, color=c_s))
        cx += headers[1][1] + 6

        # Idempotent
        f.append(fitbox(cx, y, headers[2][1], row_h - 6, idem, size=10.5, bold=True,
                        fill=("#eef6ef" if c_i == GREEN else "#fdecea"), stroke=c_i, color=c_i))
        cx += headers[2][1] + 6

        # Cacheable
        f.append(fitbox(cx, y, headers[3][1], row_h - 6, cache, size=10.5,
                        fill=("#eef6ef" if c_c == GREEN else ("#fdfbf0" if c_c == AMBER else "#fdecea")),
                        stroke=c_c, color=c_c))
        cx += headers[3][1] + 6

        # Body
        f.append(fitbox(cx, y, headers[4][1], row_h - 6, body, size=10, fill="#ffffff", stroke=LINE))

    render(os.path.join(IMG, 'http-methods-matrix.svg'), W, H, *f)


# ── 4. Розсинхронізація меж повідомлень (Request Smuggling) ───────────────────
def fig_smuggling_desync():
    W, H = 960, 480
    f = [text(W / 2, 28, "Розсинхронізація запитів (HTTP Request Smuggling: CL.TE)", size=16, bold=True)]

    # Ліворуч: Атакувальний запит
    f.append(rect(20, 56, 260, 400, fill=PANEL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(150, 80, "АТАКУВАЛЬНИЙ ПАКЕТ", size=12, color=BLUE, bold=True))
    f.append(fitbox(30, 96, 240, 340,
                    "POST / HTTP/1.1\n"
                    "Host: example.com\n"
                    "Content-Length: 13\n"
                    "Transfer-Encoding: chunked\n"
                    "\n"
                    "0\n"
                    "\n"
                    "GET /admin HTTP/1.1\n"
                    "Host: example.com\n"
                    "X-Injected: 1",
                    size=10.5, fill="#fdfbf0", stroke=AMBER))

    # Посередині: Фронтенд-проксі
    f.append(rect(300, 56, 310, 185, fill=PANEL, stroke=RED, sw=1.5, rx=8))
    f.append(text(455, 80, "ФРОНТЕНД-ПРОКСІ (читає CL)", size=11.5, color=RED, bold=True))
    f.append(fitbox(310, 96, 290, 130,
                    "Керується Content-Length: 13.\n"
                    "Бачить рівно 13 байтів тіла:\n"
                    "\"0\\r\\n\\r\\nGET /admin...\"\n"
                    "Пересилає весь блок бекенду як\n"
                    "один повний HTTP-запит #1.",
                    size=10.5, fill="#fdecea", stroke=RED))

    # Посередині: Бекенд-сервер
    f.append(rect(300, 270, 310, 185, fill=PANEL, stroke=POS, sw=1.5, rx=8))
    f.append(text(455, 294, "БЕКЕНД-СЕРВЕР (читає TE)", size=11.5, color=POS, bold=True))
    f.append(fitbox(310, 310, 290, 130,
                    "Керується Transfer-Encoding.\n"
                    "Бачить шматок довжиною 0\n"
                    "і вважає запит #1 завершеним.\n"
                    "Хвіст \"GET /admin...\" лишається\n"
                    "в сокеті як початок запиту #2!",
                    size=10.5, fill="#fdecea", stroke=POS))

    # Стрілки
    f.append(arrow(280, 148, 300, 148, color=LINE, sw=1.6))
    f.append(arrow(455, 241, 455, 270, color=LINE, sw=1.6))

    # Праворуч: Жертва / Наслідок
    f.append(rect(630, 56, 310, 400, fill=PANEL, stroke=RED, sw=1.8, rx=8))
    f.append(text(785, 80, "НАСЛІДОК ДЛЯ ЖЕРТВИ", size=11.5, color=RED, bold=True))
    f.append(fitbox(640, 96, 290, 340,
                    "1. Наступний користувач надсилає:\n"
                    "   GET /index.html HTTP/1.1\n\n"
                    "2. Бекенд склеює отруєний хвіст із\n"
                    "   новим запитом у цьому ж сокеті:\n"
                    "   GET /admin HTTP/1.1\n"
                    "   X-Injected: 1GET /index.html...\n\n"
                    "3. Бекенд виконує /admin від імені\n"
                    "   або в сесії невинної жертви!\n\n"
                    "Захист: суворо відхиляти (HTTP 400)\n"
                    "запити, що одночасно мають\n"
                    "і Content-Length, і Transfer-Encoding.",
                    size=10.5, fill="#fdecea", stroke=RED, color=RED, bold=True))

    render(os.path.join(IMG, 'http-smuggling-desync.svg'), W, H, *f)


if __name__ == '__main__':
    fig_message_anatomy()
    fig_transport_evolution()
    fig_methods_matrix()
    fig_smuggling_desync()
    print("All figures generated successfully.")
