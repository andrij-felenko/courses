# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_requests_layers():
    """Багаторівнева архітектура HTTP-клієнта: від інтерфейсу requests до сокетів ОС."""
    W, H = 960, 520
    frags = []

    frags.append(text(W / 2, 28, "Багаторівнева архітектура виконання запиту в requests", size=16, bold=True))

    # Рівень 1: Високорівневий інтерфейс (Користувацький код)
    frags.append(rect(40, 55, 880, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(80, 80, "Клієнтський рівень (requests API)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(80, 104, "requests.get() / requests.post()   →   requests.Session (кукі, заголовки за замовчуванням, префікси адаптерів)", size=11, anchor="start", color=MUTED))

    # Рівень 2: Підготовка запиту (PreparedRequest)
    frags.append(rect(40, 145, 880, 85, fill="#edf2f7", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(80, 170, "Рівень конвеєра підготовки (Request → PreparedRequest)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(80, 194, "Нормалізація URL (IDNA/Punycode + percent-encoding)  •  CaseInsensitiveDict для заголовків  •  Серіалізація тіла (JSON/form/multipart)", size=11, anchor="start", color=MUTED))
    frags.append(text(80, 214, "Автоматичне обчислення Content-Length або виставлення Transfer-Encoding: chunked  •  Витягнення cookie з CookieJar", size=11, anchor="start", color=FIELD))

    # Рівень 3: Транспортний диспетчер (Transport Adapters)
    frags.append(rect(40, 250, 880, 75, fill="#ebf8fa", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(80, 275, "Транспортний адаптер (requests.adapters.HTTPAdapter)", size=13, bold=True, anchor="start", color="#0369a1"))
    frags.append(text(80, 298, "Маршрутизація за префіксом URL (https://, http://, unix://)  •  Трансляція таймаутів (connect/read)  •  Конфігурація проксі", size=11, anchor="start", color=MUTED))
    frags.append(text(80, 314, "Обгортка над пулом з'єднань urllib3.PoolManager  •  Управління політикою повторів urllib3.util.Retry", size=10, anchor="start", color=MUTED))

    # Рівень 4: Рушій з'єднань і пул (urllib3)
    frags.append(rect(40, 345, 880, 75, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=8))
    frags.append(text(80, 370, "Низькорівневий рушій (urllib3: PoolManager → HTTPConnectionPool)", size=13, bold=True, anchor="start", color="#a16207"))
    frags.append(text(80, 394, "Потокобезпечні черги вільних з'єднань (LifoQueue)  •  Повторне використання TCP (keep-alive)  •  TLS Context & SNI", size=11, anchor="start", color=MUTED))
    frags.append(text(80, 410, "Перевірка ланцюжків сертифікатів через OpenSSL/certifi  •  Формування HTTP-фреймів у http.client", size=10, anchor="start", color=MUTED))

    # Рівень 5: Системні сокети ОС
    frags.append(rect(40, 440, 880, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(80, 465, "Операційна система й мережевий стек (OS TCP/IP Sockets)", size=13, bold=True, anchor="start", color=POS))
    frags.append(text(80, 488, "Системні виклики socket(), connect(), send(), recv()  •  TCP 3-Way Handshake  •  TLS ClientHello / ServerHello", size=11, anchor="start", color=MUTED))

    # Стрілки між рівнями
    frags.append(arrow(480, 125, 480, 145, color=LINE, sw=2.0))
    frags.append(arrow(480, 230, 480, 250, color=LINE, sw=2.0))
    frags.append(arrow(480, 325, 480, 345, color=LINE, sw=2.0))
    frags.append(arrow(480, 420, 480, 440, color=LINE, sw=2.0))

    render(os.path.join(IMG, "requests-layers.svg"), W, H, *frags)


def fig_request_lifecycle():
    """Повний життєвий цикл запиту: конвеєр перетворень від Request до Response."""
    W, H = 960, 480
    frags = []

    frags.append(text(W / 2, 28, "Життєвий цикл запиту: конвеєр обробки та перетворень", size=16, bold=True))

    # Крок 1: Вхідний Request
    frags.append(rect(30, 60, 200, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(130, 85, "1. Створення Request", size=12, bold=True))
    frags.append(text(130, 110, "method: 'POST'", size=11, color=INK))
    frags.append(text(130, 130, "url: 'https://api...'", size=11, color=INK))
    frags.append(text(130, 150, "json: {'key': 'val'}", size=11, color=MUTED))
    frags.append(text(130, 170, "headers, auth, params", size=10, color=MUTED))
    frags.append(text(130, 200, "Декларативний опис", size=10, bold=True, color="#0284c7"))
    frags.append(text(130, 220, "запиту користувача", size=10, color=MUTED))

    # Крок 2: PreparedRequest
    frags.append(rect(270, 60, 200, 180, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(370, 85, "2. PreparedRequest", size=12, bold=True, color=FIELD))
    frags.append(text(370, 110, "URL кодовано (UTF-8)", size=10, color=INK))
    frags.append(text(370, 130, "CaseInsensitiveDict", size=10, color=INK))
    frags.append(text(370, 150, "Тіло серіалізовано", size=10, color=INK))
    frags.append(text(370, 170, "Content-Length: 15", size=10, color=FIELD))
    frags.append(text(370, 190, "Cookie: sid=abc; ...", size=10, color=MUTED))
    frags.append(text(370, 220, "Готовий до відправки", size=10, bold=True, color=FIELD))

    # Крок 3: Адаптер та Пул
    frags.append(rect(510, 60, 200, 180, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(text(610, 85, "3. HTTPAdapter.send()", size=12, bold=True, color="#a16207"))
    frags.append(text(610, 110, "Пошук пулу для хоста", size=10, color=INK))
    frags.append(text(610, 130, "Взяття TCP-з'єднання", size=10, color=INK))
    frags.append(text(610, 150, "Таймаути (з'єднання/читання)", size=10, color=MUTED))
    frags.append(text(610, 170, "Відправка HTTP-байтів", size=10, color=INK))
    frags.append(text(610, 200, "urllib3.urlopen()", size=10, bold=True, color="#ca8a04"))
    frags.append(text(610, 220, "Мережевий I/O обмін", size=10, color=MUTED))

    # Крок 4: urllib3 Response
    frags.append(rect(750, 60, 180, 180, fill="#fdf2f8", stroke="#db2777", sw=1.5, rx=6))
    frags.append(text(840, 85, "4. urllib3 Response", size=12, bold=True, color="#be185d"))
    frags.append(text(840, 110, "status: 200 OK", size=11, bold=True, color=FIELD))
    frags.append(text(840, 130, "raw: сокетний потік", size=10, color=INK))
    frags.append(text(840, 150, "декомпресія (gzip)", size=10, color=MUTED))
    frags.append(text(840, 170, "заголовки сервера", size=10, color=MUTED))
    frags.append(text(840, 200, "Низькорівневий потік", size=10, bold=True, color="#db2777"))
    frags.append(text(840, 220, "даних відповіді", size=10, color=MUTED))

    # Стрілки верхнього ряду
    frags.append(arrow(230, 150, 270, 150, color=LINE, sw=1.8))
    frags.append(arrow(470, 150, 510, 150, color=LINE, sw=1.8))
    frags.append(arrow(710, 150, 750, 150, color=LINE, sw=1.8))

    # Стрілка вниз до обробки редиректів та фінального об'єкта
    frags.append(arrow(840, 240, 840, 290, color=LINE, sw=1.8))

    # Блок перевірки перенаправлень (Redirect Loop)
    frags.append(rect(510, 290, 420, 160, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(text(720, 315, "5. Обробка статусів і перенаправлень (Session.resolve_redirects)", size=12, bold=True, color="#1d4ed8"))
    frags.append(text(720, 340, "Статус 3xx та allow_redirects=True?", size=11, color=INK))
    frags.append(text(720, 360, "→ ТАК: зміна методу (303 → GET), очищення Authorization при зміні хоста", size=10, color=MUTED))
    frags.append(text(720, 380, "→ збереження проміжної відповіді в response.history, повторний запит", size=10, color=MUTED))
    frags.append(text(720, 405, "→ НІ: завершення конвеєра, повернення об'єкта requests.Response", size=11, bold=True, color=FIELD))
    frags.append(text(720, 430, "Оновлення CookieJar з заголовків Set-Cookie", size=10, color=MUTED))

    # Фінальний блок Response для користувача
    frags.append(rect(30, 290, 440, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(250, 315, "6. Фінальний об'єкт requests.Response у користувача", size=12, bold=True, color=INK))
    frags.append(text(250, 340, "response.status_code  •  response.headers (CaseInsensitiveDict)", size=11, color=INK))
    frags.append(text(250, 365, "response.content: байти (жадібне читання, сокет повертається в пул)", size=10, color=FIELD))
    frags.append(text(250, 390, "response.text: декодування за response.encoding (chardet / Content-Type)", size=10, color=MUTED))
    frags.append(text(250, 415, "response.json(): парсинг JSON  •  response.raise_for_status()", size=10, color=MUTED))
    frags.append(text(250, 435, "response.history: список проміжних 3xx-відповідей", size=10, color=MUTED))

    # Стрілка від редиректів до фінального Response
    frags.append(arrow(510, 370, 470, 370, color=FIELD, sw=2.0))

    render(os.path.join(IMG, "request-lifecycle.svg"), W, H, *frags)


def fig_transport_pool_routing():
    """Маршрутизація адаптерів та пулів з'єднань за схемою та хостом."""
    W, H = 960, 460
    frags = []

    frags.append(text(W / 2, 28, "Маршрутизація адаптерів Session та пулу з'єднань urllib3", size=16, bold=True))

    # Session з реєстром адаптерів
    frags.append(rect(40, 60, 260, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(170, 90, "requests.Session", size=14, bold=True))
    frags.append(text(170, 115, "Реєстр адаптерів (adapters)", size=11, color=MUTED))

    frags.append(rect(55, 140, 230, 75, fill="#edf2f7", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(170, 162, "Префікс 'https://'", size=11, bold=True, color=INK))
    frags.append(text(170, 185, "HTTPAdapter(pool_connections=10,", size=10, color=MUTED))
    frags.append(text(170, 202, "            pool_maxsize=10)", size=10, color=MUTED))

    frags.append(rect(55, 230, 230, 75, fill="#edf2f7", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(170, 252, "Префікс 'http://'", size=11, bold=True, color=INK))
    frags.append(text(170, 275, "HTTPAdapter(pool_connections=10,", size=10, color=MUTED))
    frags.append(text(170, 292, "            pool_maxsize=10)", size=10, color=MUTED))

    frags.append(rect(55, 320, 230, 80, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=6))
    frags.append(text(170, 342, "Префікс 'unix://' або кастомний", size=11, bold=True, color="#0369a1"))
    frags.append(text(170, 365, "CustomAdapter / MockAdapter", size=10, color=MUTED))
    frags.append(text(170, 385, "session.mount('prefix://', ...)", size=10, color=FIELD))

    # Диспетчер адаптера HTTPAdapter
    frags.append(rect(360, 60, 250, 360, fill="#ebf8fa", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(485, 90, "HTTPAdapter", size=14, bold=True, color="#0369a1"))
    frags.append(text(485, 115, "urllib3.PoolManager", size=12, bold=True, color=INK))

    frags.append(rect(375, 140, 220, 110, fill=BG, stroke="#0284c7", sw=1.2, rx=6))
    frags.append(text(485, 165, "Кеш пулів за (схема, хост, порт)", size=10, bold=True, color=INK))
    frags.append(text(485, 190, "key: ('https', 'api.io', 443)", size=10, color=MUTED))
    frags.append(text(485, 210, "key: ('https', 'cdn.io', 443)", size=10, color=MUTED))
    frags.append(text(485, 230, "Максимум num_pools (10)", size=10, color=FIELD))

    frags.append(rect(375, 270, 220, 130, fill=BG, stroke="#0284c7", sw=1.2, rx=6))
    frags.append(text(485, 295, "Параметри таймауту й повторів", size=10, bold=True, color=INK))
    frags.append(text(485, 320, "Timeout(connect=3.0, read=10.0)", size=10, color=MUTED))
    frags.append(text(485, 345, "Retry(total=3, backoff_factor=0.5)", size=10, color=MUTED))
    frags.append(text(485, 375, "Трансляція в виклик urlopen()", size=10, color=FIELD))

    # Стрілки від Session до HTTPAdapter
    frags.append(arrow(285, 175, 360, 175, color=LINE, sw=1.8))
    frags.append(arrow(285, 265, 360, 265, color=LINE, sw=1.8))

    # Праворуч: Пули з'єднань urllib3.HTTPConnectionPool
    frags.append(rect(670, 60, 250, 360, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=8))
    frags.append(text(795, 90, "HTTPConnectionPool", size=13, bold=True, color="#a16207"))
    frags.append(text(795, 115, "Хост: https://api.io:443", size=11, color=MUTED))

    # Черга відкритих сокетів LifoQueue
    frags.append(rect(685, 140, 220, 130, fill=BG, stroke="#ca8a04", sw=1.2, rx=6))
    frags.append(text(795, 165, "LifoQueue відкритих сокетів", size=10, bold=True, color=INK))
    frags.append(text(795, 190, "[ Socket 1: TCP/TLS активний ]", size=10, color=FIELD))
    frags.append(text(795, 212, "[ Socket 2: TCP/TLS активний ]", size=10, color=FIELD))
    frags.append(text(795, 235, "[ Вільний слот пулу ... ]", size=10, color=MUTED))
    frags.append(text(795, 255, "maxsize = 10 з'єднань", size=10, color=MUTED))

    frags.append(rect(685, 290, 220, 110, fill=BG, stroke="#ca8a04", sw=1.2, rx=6))
    frags.append(text(795, 315, "Повторне використання", size=10, bold=True, color=INK))
    frags.append(text(795, 340, "Запит бере сокет з черги,", size=10, color=MUTED))
    frags.append(text(795, 360, "відправляє HTTP, читає дані,", size=10, color=MUTED))
    frags.append(text(795, 380, "повертає сокет назад у пул", size=10, color=FIELD))

    # Стрілка від PoolManager до ConnectionPool
    frags.append(arrow(595, 190, 670, 190, color=LINE, sw=1.8))

    render(os.path.join(IMG, "transport-pool-routing.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_requests_layers()
    fig_request_lifecycle()
    fig_transport_pool_routing()
    print("Фігури успішно згенеровано.")
