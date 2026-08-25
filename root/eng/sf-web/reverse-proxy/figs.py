# -*- coding: utf-8 -*-
"""Фігури теми «Зворотний проксі». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. forward-vs-reverse-proxy: прямий проксі проти зворотного ─────────────
def fig_forward_vs_reverse_proxy():
    W, H = 1000, 390
    f = []

    # Ліва половина: Прямий проксі (Forward Proxy)
    f.append(rect(20, 20, 460, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 48, "Прямий проксі (Forward Proxy)", size=14, bold=True, color=NEG))
    f.append(text(250, 68, "Діє від імені клієнтів (захищає / приховує клієнта)", size=11, color=MUTED, italic=True))

    # Клієнти всередині локальної мережі
    f.append(rect(35, 90, 115, 230, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    f.append(text(92, 110, "Приватна LAN", size=10, bold=True, color=MUTED))
    c1, _, _ = textbox(92, 150, "Робоча станція\n192.168.1.10", size=10, pad=6, fill=FILL, stroke=LINE)
    c2, _, _ = textbox(92, 215, "Ноутбук\n192.168.1.11", size=10, pad=6, fill=FILL, stroke=LINE)
    c3, _, _ = textbox(92, 280, "Смартфон\n192.168.1.12", size=10, pad=6, fill=FILL, stroke=LINE)
    f.extend([c1, c2, c3])

    # Прямий проксі по центру лівої панелі
    fp_box, _, _ = textbox(245, 205, "ПРЯМИЙ ПРОКСІ\n(Forward Proxy)\n\n• Вихідний шлюз\n• Фільтрація сайтів\n• Кеш контенту\n• Приховує IP клієнта",
                           size=10, bold=True, min_w=125, pad=8, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(fp_box)

    # Сервери в інтернеті
    s1, _, _ = textbox(410, 150, "Сервер A\n(google.com)", size=10, pad=6, fill=FILL, stroke=LINE)
    s2, _, _ = textbox(410, 215, "Сервер B\n(github.com)", size=10, pad=6, fill=FILL, stroke=LINE)
    s3, _, _ = textbox(410, 280, "Сервер C\n(api.org)", size=10, pad=6, fill=FILL, stroke=LINE)
    f.extend([s1, s2, s3])

    # Стрілки зліва направо
    for cy in [150, 215, 280]:
        f.append(arrow(150, cy, 180, 205, color=LINE, sw=1.2))
    for sy in [150, 215, 280]:
        f.append(arrow(310, 205, 350, sy, color=NEG, sw=1.2))

    f.append(text(250, 350, "Сервер бачить запит від IP-адреси проксі, а не клієнта", size=10, color=INK))

    # Права половина: Зворотний проксі (Reverse Proxy)
    f.append(rect(520, 20, 460, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 48, "Зворотний проксі (Reverse Proxy)", size=14, bold=True, color=FIELD))
    f.append(text(750, 68, "Діє від імені серверів (приховує топологію кластера)", size=11, color=MUTED, italic=True))

    # Клієнти в інтернеті
    ic1, _, _ = textbox(580, 150, "Клієнт WAN\n203.0.113.5", size=10, pad=6, fill=FILL, stroke=LINE)
    ic2, _, _ = textbox(580, 215, "Мобільний клієнт\n198.51.100.8", size=10, pad=6, fill=FILL, stroke=LINE)
    ic3, _, _ = textbox(580, 280, "API-партнер\n192.0.2.77", size=10, pad=6, fill=FILL, stroke=LINE)
    f.extend([ic1, ic2, ic3])

    # Зворотний проксі по центру правої панелі
    rp_box, _, _ = textbox(735, 205, "ЗВОРОТНИЙ ПРОКСІ\n(Reverse Proxy)\n\n• Єдина точка входу\n• Термінація TLS\n• Буферизація\n• Розв'язка топології",
                           size=10, bold=True, min_w=125, pad=8, fill=GREEN_F, stroke=FIELD, sw=1.5)
    f.append(rp_box)

    # Приватна мережа серверів
    f.append(rect(825, 90, 140, 230, fill="#ffffff", stroke=FIELD, sw=1, rx=6))
    f.append(text(895, 110, "Приватна LAN кластера", size=10, bold=True, color=FIELD))
    bs1, _, _ = textbox(895, 150, "Воркер додатку\n10.0.0.11:8080", size=10, pad=6, fill=FILL, stroke=LINE)
    bs2, _, _ = textbox(895, 215, "Воркер додатку\n10.0.0.12:8080", size=10, pad=6, fill=FILL, stroke=LINE)
    bs3, _, _ = textbox(895, 280, "Статичний файл\n10.0.0.13:80", size=10, pad=6, fill=FILL, stroke=LINE)
    f.extend([bs1, bs2, bs3])

    # Стрілки справа
    for cy in [150, 215, 280]:
        f.append(arrow(635, cy, 670, 205, color=LINE, sw=1.2))
    for sy in [150, 215, 280]:
        f.append(arrow(800, 205, 835, sy, color=FIELD, sw=1.2))

    f.append(text(750, 350, "Клієнт знає лише публічний IP/домен проксі, бекенд ізольовано", size=10, color=INK))

    render(out("forward-vs-reverse-proxy.svg"), W, H, *f)

# ── 2. reverse-proxy-connection-split: розрив двох TCP сокетів та буфер ──────
def fig_reverse_proxy_connection_split():
    W, H = 940, 360
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 28, "Розрив TCP-сесій та буферизація між WAN і LAN", size=14, bold=True, color=INK))

    # Лівий блок: Клієнтське з'єднання (Повільний WAN)
    f.append(rect(20, 55, 260, 275, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(150, 80, "Зовнішній клієнт (WAN)", size=12, bold=True, color=POS))
    f.append(text(150, 100, "Повільний канал, втрати, затримки", size=10, color=MUTED, italic=True))

    c_box, _, _ = textbox(150, 155, "Мобільний клієнт\nRTT: 80–150 мс\nШвидкість: 50 КБ/с\nTLS 1.3 / HTTP/2",
                          size=10, pad=8, fill=FILL, stroke=LINE)
    f.append(c_box)

    f.append(rect(35, 215, 230, 95, fill=RED_F, stroke=POS, sw=1, rx=6))
    f.append(text(150, 235, "TCP Сокет 1 (Client-Facing)", size=10, bold=True, color=POS))
    f.append(text(150, 255, "• Довгоживучий TCP сеанс", size=9, color=INK))
    f.append(text(150, 275, "• Повільне читання тіла запиту", size=9, color=INK))
    f.append(text(150, 295, "• Захист від атак Slowloris", size=9, color=INK))

    # Центральний блок: Зворотний проксі з буферами
    f.append(rect(310, 55, 320, 275, fill=BLUE_F, stroke=NEG, sw=1.5, rx=8))
    f.append(text(470, 80, "Зворотний проксі (Event Loop / epoll)", size=12, bold=True, color=NEG))
    f.append(text(470, 100, "Неблокуючий ввід-вивід та ізоляція швидкостей", size=10, color=MUTED, italic=True))

    # Буфери всередині проксі
    f.append(rect(330, 120, 280, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    f.append(text(470, 140, "Буфер запиту (Request Buffer)", size=10, bold=True, color=NEG))
    f.append(text(470, 160, "Асинхронне накопичення байтів із WAN", size=9, color=INK))
    f.append(text(470, 180, "Запит передається в LAN лише після повного збору", size=9, color=FIELD, bold=True))

    f.append(rect(330, 220, 280, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    f.append(text(470, 240, "Буфер відповіді (Response Buffer)", size=10, bold=True, color=NEG))
    f.append(text(470, 260, "Миттєвий прийом повної відповіді від бекенда", size=9, color=INK))
    f.append(text(470, 280, "Повільна роздача клієнту без блокування бекенда", size=9, color=FIELD, bold=True))

    # Правий блок: Внутрішній бекенд (Швидкий LAN)
    f.append(rect(660, 55, 260, 275, fill="#fdfefe", stroke=FIELD, sw=1.2, rx=8))
    f.append(text(790, 80, "Внутрішній бекенд (LAN)", size=12, bold=True, color=FIELD))
    f.append(text(790, 100, "RTT < 0.5 мс, швидкість 10 Гбіт/с", size=10, color=MUTED, italic=True))

    s_box, _, _ = textbox(790, 155, "Воркер застосунку\n(Gunicorn / Puma / Tomcat)\nПул потоків обмежений",
                          size=10, pad=8, fill=FILL, stroke=LINE)
    f.append(s_box)

    f.append(rect(675, 215, 230, 95, fill=GREEN_F, stroke=FIELD, sw=1, rx=6))
    f.append(text(790, 235, "TCP Сокет 2 (Upstream-Facing)", size=10, bold=True, color=FIELD))
    f.append(text(790, 255, "• Пул з'єднань Keep-Alive", size=9, color=INK))
    f.append(text(790, 275, "• Воркер зайнятий лише 5–10 мс", size=9, color=FIELD, bold=True))
    f.append(text(790, 295, "• Швидка передача через LAN / UDS", size=9, color=INK))

    # Стрілки передачі між блоками
    f.append(arrow(280, 160, 330, 160, color=POS, sw=1.8))
    f.append(arrow(610, 160, 660, 160, color=FIELD, sw=1.8))
    f.append(arrow(660, 260, 610, 260, color=FIELD, sw=1.8))
    f.append(arrow(330, 260, 280, 260, color=POS, sw=1.8))

    f.append(text(W / 2, 345, "Проксі поглинає затримки WAN, звільняючи воркери бекенда від простою в очікуванні сокетів", size=10, color=INK, italic=True))

    render(out("reverse-proxy-connection-split.svg"), W, H, *f)

# ── 3. protocol-translation-tls-offloading: режими TLS та трансляція ────────
def fig_protocol_translation():
    W, H = 960, 380
    f = []

    f.append(text(W / 2, 28, "Режими обробки TLS та протокольна трансляція на зворотному проксі", size=14, bold=True, color=INK))

    modes_data = [
        {
            "y": 60, "title": "1. Зняття TLS (SSL Offloading / Termination)",
            "client_t": "Клієнт (WAN)\nHTTPS (TLS 1.3)", "proxy_t": "Зворотний проксі\nРозшифрування TLS\nAES-NI / криптографія",
            "backend_t": "Внутрішній сервер (LAN)\nЧистий HTTP/1.1 / UDS",
            "c_color": POS, "m_color": BLUE_F, "b_color": GREEN_F,
            "conn1": "HTTPS / TLS 1.3", "conn2": "HTTP / UDS (без шифрування)",
            "desc": "Найвища продуктивність; нульові накладні витрати на CPU у внутрішніх мікросервісах."
        },
        {
            "y": 165, "title": "2. Повторне шифрування (SSL Bridging / Re-encryption)",
            "client_t": "Клієнт (WAN)\nHTTPS (Публічний сертифікат)", "proxy_t": "Зворотний проксі\nТермінація + mTLS\nІнспекція L7 / WAF",
            "backend_t": "Внутрішній сервер (LAN)\nВнутрішній mTLS (Zero-Trust)",
            "c_color": POS, "m_color": BLUE_F, "b_color": BLUE_F,
            "conn1": "Публічний TLS", "conn2": "Внутрішній mTLS",
            "desc": "Повна ізоляція: проксі інспектує трафік, а внутрішній тракт захищено згідно з Zero-Trust."
        },
        {
            "y": 270, "title": "3. Наскрізний пропуск L4 (SSL Passthrough / SNI Routing)",
            "client_t": "Клієнт (WAN)\nЗашифрований потік TLS", "proxy_t": "L4 Проксі (SNI Switch)\nМаршрутизація за Server Name\nБез розшифрування",
            "backend_t": "Цільовий сервер (LAN)\nТермінація кінцевого TLS",
            "c_color": POS, "m_color": FILL, "b_color": POS,
            "conn1": "Шифрований потік TCP", "conn2": "Шифрований потік TCP",
            "desc": "Проксі не має доступу до ключів і не бачить HTTP-заголовків (наскрізна криптографія)."
        }
    ]

    for m in modes_data:
        my = m["y"]
        f.append(rect(20, my, 920, 95, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
        f.append(text(40, my + 20, m["title"], size=11, bold=True, color=INK, anchor="start"))

        # Блоки зліва направо
        cb, _, _ = textbox(130, my + 55, m["client_t"], size=9, pad=5, fill=FILL, stroke=m["c_color"])
        pb, _, _ = textbox(470, my + 55, m["proxy_t"], size=9, bold=True, min_w=170, pad=5, fill=m["m_color"], stroke=NEG)
        bb, _, _ = textbox(810, my + 55, m["backend_t"], size=9, pad=5, fill=FILL, stroke=LINE)
        f.extend([cb, pb, bb])

        # З'єднання між блоками
        f.append(arrow(210, my + 55, 370, my + 55, color=LINE, sw=1.3))
        f.append(text(290, my + 42, m["conn1"], size=10, color=MUTED))

        f.append(arrow(570, my + 55, 715, my + 55, color=LINE, sw=1.3))
        f.append(text(642, my + 42, m["conn2"], size=10, color=MUTED))

    render(out("protocol-translation-tls-offloading.svg"), W, H, *f)

# ── 4. http-request-smuggling-vulnerability: розсинхронізація меж запитів ───
def fig_request_smuggling():
    W, H = 940, 370
    f = []

    f.append(text(W / 2, 28, "Вразливість розсинхронізації запитів (HTTP Request Smuggling)", size=14, bold=True, color=POS))
    f.append(text(W / 2, 48, "Розбіжність у пріоритеті Content-Length (CL) та Transfer-Encoding (TE) між проксі та бекендом", size=10, color=MUTED, italic=True))

    # Схема атаки CL.TE
    f.append(rect(20, 70, 900, 275, fill="#fdfefe", stroke=MUTED, sw=1, rx=8))

    # 1. Шкідливий комбінований запит
    f.append(rect(40, 90, 240, 235, fill=RED_F, stroke=POS, sw=1.2, rx=6))
    f.append(text(160, 112, "Шкідливий запит нападника", size=11, bold=True, color=POS))

    req_text = (
        "POST /search HTTP/1.1\n"
        "Host: example.com\n"
        "Content-Length: 44\n"
        "Transfer-Encoding: chunked\n\n"
        "0\n\n"
        "GET /admin/delete?id=1 HTTP/1.1\n"
        "Host: example.com\n"
        "Foo: x"
    )
    f.append(rect(50, 128, 220, 185, fill="#ffffff", stroke=POS, sw=0.8, rx=4))
    f.append(mtext(60, 145, req_text, size=9, color=INK, anchor="start", lh=1.25))

    # 2. Проміжний Зворотний проксі (читає за Content-Length)
    f.append(rect(330, 90, 250, 110, fill=BLUE_F, stroke=NEG, sw=1.2, rx=6))
    f.append(text(455, 112, "Зворотний проксі (режим CL)", size=10, bold=True, color=NEG))
    f.append(text(455, 132, "Бачить Content-Length: 44", size=9, color=INK))
    f.append(text(455, 150, "Вважає весь блок ОДНИМ запитом", size=9, color=INK))
    f.append(text(455, 170, "Пересилає всі 44 байти бекенду", size=9, color=FIELD, bold=True))

    # 3. Внутрішній бекенд (читає за Transfer-Encoding)
    f.append(rect(630, 90, 270, 110, fill=WARN_F, stroke="#e67e22", sw=1.2, rx=6))
    f.append(text(765, 112, "Бекенд (режим TE: chunked)", size=10, bold=True, color="#d35400"))
    f.append(text(765, 132, "Бачить перший чанк: '0' (кінець)", size=9, color=INK))
    f.append(text(765, 150, "Повертає відповідь на POST /search", size=9, color=INK))
    f.append(text(765, 172, "Залишок залишається в TCP-буфері!", size=9, color=POS, bold=True))

    # Стрілки руху
    f.append(arrow(280, 145, 330, 145, color=POS, sw=1.5))
    f.append(arrow(580, 145, 630, 145, color=NEG, sw=1.5))

    # 4. Наслідок для наступного невинного користувача
    f.append(rect(330, 215, 570, 110, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    f.append(text(615, 235, "Жертва: Наступний звичайний запит у тому ж TCP-з'єднанні", size=10, bold=True, color=POS))

    victim_info = (
        "1. Звичайний користувач надсилає 'GET /index.html HTTP/1.1'.\n"
        "2. Бекенд бере з TCP-сокета залишок 'GET /admin/delete?id=1...' і приклеює до нього запит жертви.\n"
        "3. Бекенд виконує адміністративну дію від імені користувача жертви або краде його сесійні cookie!"
    )
    f.append(mtext(345, 258, victim_info, size=9, color=INK, anchor="start", lh=1.35))

    f.append(text(W / 2, 358, "Захист: суворе відхилення неоднозначних запитів із двома заголовками та перехід на HTTP/2 між усіма шарами", size=10, color=FIELD, bold=True))

    render(out("http-request-smuggling-vulnerability.svg"), W, H, *f)

def main():
    fig_forward_vs_reverse_proxy()
    fig_reverse_proxy_connection_split()
    fig_protocol_translation()
    fig_request_smuggling()
    print("OK: generated 4 figures for reverse-proxy")

if __name__ == "__main__":
    main()
