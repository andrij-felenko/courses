# -*- coding: utf-8 -*-
"""Фігури до теми «Найпростіший HTTP-сервер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER  = "#b08900"
GRAY   = "#9aa0a6"
PANEL  = "#fbfbfb"
PURPLE = "#7b1fa2"
CYAN   = "#00838f"


# ── 1. Життєвий цикл TCP-сокета та сирого HTTP/1.1 з'єднання ─────────────────
def fig_http_socket_lifecycle():
    W, H = 1000, 520
    f = [
        text(W / 2, 28, "Життєвий цикл сокетного HTTP-сервера: від TCP-байтів до відповіді", size=15, bold=True)
    ]

    col1_x = 130
    col2_x = 500
    col3_x = 870

    f.append(fitbox(col1_x - 90, 48, 180, 36, "HTTP-клієнт (curl)", size=12, bold=True, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(col2_x - 100, 48, 200, 36, "TCP-сокет ядра (Буфер)", size=12, bold=True, fill="#fdf3e7", stroke=AMBER))
    f.append(fitbox(col3_x - 90, 48, 180, 36, "Python HTTP Server", size=12, bold=True, fill="#e8f5e9", stroke=FIELD))

    # Вертикальні напрямні (сегментовані, щоб не перетинати рамки)
    f.append(line(col1_x, 86, col1_x, 455, color=GRAY, sw=1.2, dash="4 4"))
    
    f.append(line(col2_x, 86, col2_x, 203, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col2_x, 249, col2_x, 455, color=GRAY, sw=1.2, dash="4 4"))

    f.append(line(col3_x, 86, col3_x, 92, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col3_x, 128, col3_x, 225, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col3_x, 295, col3_x, 325, color=GRAY, sw=1.2, dash="4 4"))
    f.append(line(col3_x, 365, col3_x, 455, color=GRAY, sw=1.2, dash="4 4"))

    # Подія 1: TCP Handshake & bind/listen/accept
    f.append(textbox(col3_x, 110, "socket() -> bind() -> listen()\nserver_sock.accept() -> блокування", size=10.5, pad=6, fill=FILL, stroke=LINE)[0])

    # Клієнт підключається
    f.append(arrow(col1_x, 140, col2_x - 10, 140, color=NEG, sw=1.5))
    f.append(text((col1_x + col2_x) / 2, 132, "TCP SYN / Handshake", size=10, color=NEG))

    f.append(arrow(col2_x, 148, col3_x - 10, 148, color=FIELD, sw=1.5))
    f.append(text((col2_x + col3_x) / 2, 142, "accept() повертає (client_sock, addr)", size=10, color=FIELD))

    # Подія 2: Відправка HTTP Request
    f.append(arrow(col1_x, 190, col2_x - 10, 190, color=NEG, sw=1.5))
    f.append(text((col1_x + col2_x) / 2, 180, "POST /telemetry HTTP/1.1 + Headers + Body", size=10, color=NEG))

    # Буферизація
    f.append(fitbox(col2_x - 85, 205, 170, 42, "Буфер прийому ОС\nrecv(4096) частинами", size=10, fill="#fff9c4", stroke=AMBER))

    # Читання та пошук CRLF CRLF
    f.append(arrow(col2_x + 90, 220, col3_x - 10, 220, color=LINE, sw=1.4))
    f.append(textbox(col3_x, 260, "Накопичення буфера:\nПошук b'\\r\\n\\r\\n' (кінець заголовків)\nВилучення Content-Length: N\nДочитування тіла розміром N байтів", size=10, pad=6, fill=FILL, stroke=LINE)[0])

    # Обробка запиту
    f.append(textbox(col3_x, 345, "Маршрутизація та обробка:\nОбчислення JSON / метрик / стану", size=10.5, pad=6, fill="#e8f5e9", stroke=FIELD)[0])

    # Відправка HTTP Response
    f.append(arrow(col3_x - 10, 395, col2_x + 10, 395, color=FIELD, sw=1.5))
    f.append(text((col2_x + col3_x) / 2, 385, "client_sock.sendall(HTTP/1.1 200 OK...)", size=10, color=FIELD))

    f.append(arrow(col2_x - 10, 425, col1_x + 10, 425, color=NEG, sw=1.5))
    f.append(text((col1_x + col2_x) / 2, 415, "HTTP/1.1 200 OK + Content-Length + JSON", size=10, color=NEG))

    # Закриття або Keep-Alive
    f.append(textbox(W / 2, 475, "Connection: close -> client_sock.close() | Connection: keep-alive -> цикл наступного recv()", size=10.5, pad=6, fill=PANEL, stroke=LINE)[0])

    render(os.path.join(IMG, "http-socket-lifecycle.svg"), W, H, *f)


# ── 2. Ієрархія класів стандартної бібліотеки http.server ────────────────────
def fig_http_server_class_hierarchy():
    W, H = 960, 440
    f = [
        text(W / 2, 28, "Ієрархія класів socketserver та http.server у стандартній бібліотеці", size=15, bold=True)
    ]

    box_w = 260
    box_h = 44

    # Серверна гілка
    f.append(text(240, 60, "СЕРВЕРНІ КЛАСИ (Мережевий транспорт)", size=12.5, bold=True, color=FIELD))
    f.append(fitbox(110, 80, box_w, box_h, "socketserver.BaseServer\n(Абстрактний цикл обробки)", size=10.5, fill=FILL, stroke=LINE))
    
    f.append(arrow(240, 126, 240, 150, color=LINE, sw=1.4))
    f.append(fitbox(110, 152, box_w, box_h, "socketserver.TCPServer\n(Створення сокета, bind, listen)", size=10.5, fill=FILL, stroke=LINE))

    f.append(arrow(240, 198, 240, 222, color=LINE, sw=1.4))
    f.append(fitbox(110, 224, box_w, box_h, "http.server.HTTPServer\n(Серверний сокет + HTTP-контекст)", size=10.5, fill="#e8f5e9", stroke=FIELD, bold=True))

    # ThreadingMixIn
    f.append(fitbox(10, 296, 200, 44, "socketserver.ThreadingMixIn\n(Новий потік на кожен accept)", size=10, fill="#eaf0fd", stroke=NEG))
    f.append(arrow(110, 342, 190, 368, color=NEG, sw=1.4))
    f.append(arrow(240, 270, 240, 368, color=FIELD, sw=1.4))

    f.append(fitbox(110, 370, box_w, box_h, "http.server.ThreadingHTTPServer\n(Багатопотоковий HTTP-сервер)", size=10.5, fill="#e8f5e9", stroke=FIELD, bold=True))

    # Зв'язок Сервер -> Обробник
    f.append(arrow(372, 246, 560, 246, color=AMBER, sw=1.5))
    f.append(text(465, 236, "делегує з'єднання", size=10, color=AMBER))

    # Гілка обробників
    f.append(text(710, 60, "КЛАСИ ОБРОБНИКІВ (Парсинг протоколу)", size=12.5, bold=True, color=NEG))
    f.append(fitbox(580, 80, box_w, box_h, "socketserver.BaseRequestHandler\n(Методи setup, handle, finish)", size=10.5, fill=FILL, stroke=LINE))

    f.append(arrow(710, 126, 710, 150, color=LINE, sw=1.4))
    f.append(fitbox(580, 152, box_w, box_h, "socketserver.StreamRequestHandler\n(Файлові обгортки rfile, wfile)", size=10.5, fill=FILL, stroke=LINE))

    f.append(arrow(710, 198, 710, 222, color=LINE, sw=1.4))
    f.append(fitbox(580, 224, box_w, box_h, "http.server.BaseHTTPRequestHandler\n(Розбір заголовків, do_GET, do_POST)", size=10.5, fill="#eaf0fd", stroke=NEG, bold=True))

    f.append(arrow(710, 270, 710, 294, color=LINE, sw=1.4))
    f.append(fitbox(580, 296, box_w, box_h, "http.server.SimpleHTTPRequestHandler\n(Віддача статичних файлів із диска)", size=10.5, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "http-server-class-hierarchy.svg"), W, H, *f)


# ── 3. Архітектура та конвеєр WSGI (PEP 3333) ────────────────────────────────
def fig_wsgi_architecture_pipeline():
    W, H = 1000, 480
    f = [
        text(W / 2, 28, "Конвеєр WSGI (PEP 3333): поділ транспорту, проміжного шару та бізнес-додатка", size=15, bold=True)
    ]

    # Блок 1: Клієнтський запит
    f.append(fitbox(20, 160, 140, 100, "HTTP-клієнт\n\nGET /api/v1/user\nHost: example.com\nAuthorization: ...", size=10.5, fill="#eaf0fd", stroke=NEG))

    # Стрілка 1
    f.append(arrow(162, 210, 220, 210, color=NEG, sw=1.6))
    f.append(text(191, 198, "HTTP", size=10, color=NEG, bold=True))

    # Блок 2: WSGI Gateway / Server
    f.append(rect(222, 90, 220, 240, fill="#fdf3e7", stroke=AMBER, sw=1.5, rx=8))
    f.append(text(332, 115, "WSGI-сервер / Gateway", size=12, color=AMBER, bold=True))
    f.append(text(332, 135, "(wsgiref / Gunicorn / uWSGI)", size=10, color=MUTED))
    f.append(fitbox(237, 155, 190, 60, "1. Парсинг TCP/HTTP\n2. Створення environ: dict\n3. Визначення start_response", size=10, fill=BG, stroke=AMBER))
    f.append(fitbox(237, 230, 190, 85, "4. Виклик WSGI-додатка\n5. Читання ітерованого тіла\n6. Відправка HTTP-відповіді", size=10, fill=BG, stroke=AMBER))

    # Стрілка 2
    f.append(arrow(444, 210, 505, 210, color=AMBER, sw=1.6))
    f.append(text(475, 195, "environ,\nstart_resp", size=9.5, color=AMBER, bold=True))

    # Блок 3: Middleware
    f.append(rect(507, 90, 200, 240, fill="#f3e5f5", stroke=PURPLE, sw=1.5, rx=8))
    f.append(text(607, 115, "WSGI Middleware", size=12, color=PURPLE, bold=True))
    f.append(text(607, 135, "(Проміжний шар)", size=10, color=MUTED))
    f.append(fitbox(522, 155, 170, 45, "Автентифікація\nПеревірка токена", size=10, fill=BG, stroke=PURPLE))
    f.append(fitbox(522, 210, 170, 45, "Логування та таймінг\nВимір часу запиту", size=10, fill=BG, stroke=PURPLE))
    f.append(fitbox(522, 265, 170, 45, "Gzip-стиснення\nТрансформація тіла", size=10, fill=BG, stroke=PURPLE))

    # Стрілка 3
    f.append(arrow(709, 210, 770, 210, color=PURPLE, sw=1.6))
    f.append(text(740, 195, "модиф.\nenviron", size=9.5, color=PURPLE, bold=True))

    # Блок 4: WSGI Application
    f.append(rect(772, 90, 208, 240, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(876, 115, "WSGI Application", size=12, color=FIELD, bold=True))
    f.append(text(876, 135, "(Flask / Django / micro-app)", size=10, color=MUTED))
    f.append(fitbox(787, 155, 178, 65, "Маршрутизація URL\nPATH_INFO -> handler\nРозбір JSON / Query", size=10, fill=BG, stroke=FIELD))
    f.append(fitbox(787, 230, 178, 85, "start_response('200 OK',\n [('Content-Type', ...)])\n\nreturn [b'{\"status\": \"ok\"}']", size=9.5, fill=BG, stroke=FIELD))

    # Зворотний потік байтів
    f.append(arrow(772, 380, 222, 380, color=FIELD, sw=1.8))
    f.append(text(500, 368, "Ітерований потік байтів: iterable[bytes] повертається до сокета сервера", size=10.5, color=FIELD, bold=True))

    # Зворотна HTTP-відповідь клієнту
    f.append(arrow(220, 420, 20, 420, color=NEG, sw=1.8))
    f.append(text(120, 408, "HTTP/1.1 200 OK + байти", size=10, color=NEG, bold=True))

    render(os.path.join(IMG, "wsgi-architecture-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_http_socket_lifecycle()
    fig_http_server_class_hierarchy()
    fig_wsgi_architecture_pipeline()
    print("Всі фігури згенеровано успішно.")
