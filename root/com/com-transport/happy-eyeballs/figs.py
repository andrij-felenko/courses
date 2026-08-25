# -*- coding: utf-8 -*-
"""Генератор фігур для статті Happy Eyeballs (book/communications/networks/happy-eyeballs)."""

import sys
import os

# scripts/ у корені репо — 4 рівні вгору
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')


def make_fig1():
    """Фігура 1: Послідовний вибір адреси при непрацездатному IPv6 (проблема 20-30 с таймауту)."""
    w, h = 880, 520
    frags = []

    # Колони учасників
    c_client = 160
    c_middle = 440
    c_server = 720

    # Заголовки учасників
    b1, _, _ = textbox(c_client, 45, "Клієнт (Dual-Stack)\nPOSIX getaddrinfo()", size=13, bold=True, pad=8, fill="#eef2f7", min_w=180)
    b2, _, _ = textbox(c_middle, 45, "Мережа / Фаєрвол\n(IPv6 Black Hole)", size=13, bold=True, pad=8, fill="#fdecea", stroke=POS, min_w=180)
    b3, _, _ = textbox(c_server, 45, "Сервер (Dual-Stack)\n2001:db8::1 / 198.51.100.1", size=13, bold=True, pad=8, fill="#eef2f7", min_w=200)
    frags.extend([b1, b2, b3])

    # Вертикальні лінії часової шкали
    frags.append(line(c_client, 75, c_client, 485, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(c_middle, 75, c_middle, 485, color=POS, sw=1.5, dash="4,4"))
    frags.append(line(c_server, 75, c_server, 485, color=MUTED, sw=1.5, dash="4,4"))

    # Початковий DNS
    frags.append(arrow(c_client, 105, c_server, 105, color=LINE, sw=1.5))
    frags.append(text((c_client + c_server) / 2, 98, "1. DNS запит (A та AAAA) → отримано IPv6 і IPv4", size=12, bold=True))

    frags.append(arrow(c_server, 125, c_client, 125, color=LINE, sw=1.5))
    frags.append(text((c_client + c_server) / 2, 120, "2. Відповідь DNS: AAAA 2001:db8::1, A 198.51.100.1", size=11, color=MUTED))

    # Спроба 1: IPv6 SYN губиться
    frags.append(rect(c_client - 85, 140, 170, 24, fill="#fbeae8", stroke=POS, sw=1.2, rx=4))
    frags.append(text(c_client, 156, "Спроба 1: IPv6 (RFC 6724)", size=11, color=POS, bold=True))

    frags.append(arrow(c_client, 175, c_middle, 175, color=POS, sw=1.8))
    frags.append(text((c_client + c_middle) / 2, 168, "TCP SYN [IPv6: 2001:db8::1] (t = 0 с)", size=11, color=POS, bold=True))

    # Хрестик втрати пакета на фаєрволі
    frags.append(circle(c_middle, 175, 12, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(c_middle, 180, "✖", size=14, color=POS, bold=True))
    frags.append(text(c_middle + 95, 179, "Пакет мовчки відкинуто", size=11, color=POS, italic=True))

    # Експоненційний відступ ретрансмісій
    frags.append(rect(c_client - 145, 195, 290, 145, fill="#fffaf9", stroke=POS, sw=1, rx=6))
    frags.append(text(c_client, 212, "Експоненційний відступ SYN-ретрансмісій ядра:", size=11, color=POS, bold=True))
    frags.append(text(c_client, 232, "• t = 1 с: повторний TCP SYN #1 (втрачено)", size=11, color=INK))
    frags.append(text(c_client, 252, "• t = 3 с: повторний TCP SYN #2 (втрачено)", size=11, color=INK))
    frags.append(text(c_client, 272, "• t = 7 с: повторний TCP SYN #3 (втрачено)", size=11, color=INK))
    frags.append(text(c_client, 292, "• t = 15 с: повторний TCP SYN #4 (втрачено)", size=11, color=INK))
    frags.append(text(c_client, 317, "t = 21–31 с: ETIMEDOUT (збій сокета IPv6)", size=11, color=POS, bold=True))

    # Пояснювальний блок праворуч
    pb, _, _ = textbox(600, 260, "Користувач бачить затримку 21–31 с!\nБраузер показує порожню сторінку.\nКористувач закриває вкладку\nта вимикає IPv6 в системі.", size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.5, bold=True)
    frags.append(pb)

    # Спроба 2: IPv4 Fallback
    frags.append(rect(c_client - 85, 355, 170, 24, fill="#e8f6ed", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(c_client, 371, "Спроба 2: IPv4 Fallback", size=11, color=FIELD, bold=True))

    frags.append(arrow(c_client, 395, c_server, 395, color=FIELD, sw=1.8))
    frags.append(text(440, 388, "TCP SYN [IPv4: 198.51.100.1] (t = 25.0 с)", size=11, color=FIELD, bold=True))

    frags.append(arrow(c_server, 425, c_client, 425, color=FIELD, sw=1.8))
    frags.append(text(440, 418, "TCP SYN-ACK [IPv4] (t = 25.04 с, RTT = 40 мс)", size=11, color=FIELD, bold=True))

    frags.append(arrow(c_client, 455, c_server, 455, color=FIELD, sw=1.8))
    frags.append(text(440, 448, "TCP ACK [IPv4] → З'єднання встановлено успішно (t = 25.08 с)", size=11, color=FIELD, bold=True))

    frags.append(rect(c_client - 120, 468, 680, 26, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(text(440, 485, "Підсумок: послідовний перебір робить мережу повільною та непридатною при будь-яких збоях IPv6", size=12, bold=True))

    render(os.path.join(OUT_DIR, "fig1-broken-ipv6-timeout.svg"), w, h, *frags)


def make_fig2():
    """Фігура 2: Змагання з'єднань в алгоритмі Happy Eyeballs v2 (RFC 8305)."""
    w, h = 880, 480
    frags = []

    c_client = 150
    c_v6 = 470
    c_v4 = 750

    # Шапка учасників
    b1, _, _ = textbox(c_client, 45, "Клієнт Happy Eyeballs\n(RFC 8305 Connection Racer)", size=13, bold=True, pad=8, fill="#eef2f7", min_w=190)
    b2, _, _ = textbox(c_v6, 45, "IPv6 Маршрут (2001:db8::1)\n(проблема зв'язності / втрати)", size=13, bold=True, pad=8, fill="#fdecea", stroke=POS, min_w=200)
    b3, _, _ = textbox(c_v4, 45, "IPv4 Маршрут (198.51.100.1)\n(робоча зв'язність, RTT 40 мс)", size=13, bold=True, pad=8, fill="#e8f6ed", stroke=FIELD, min_w=200)
    frags.extend([b1, b2, b3])

    # Часові шкали
    frags.append(line(c_client, 75, c_client, 445, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(c_v6, 75, c_v6, 445, color=POS, sw=1.5, dash="4,4"))
    frags.append(line(c_v4, 75, c_v4, 445, color=FIELD, sw=1.5, dash="4,4"))

    # Етап 1: DNS запит
    frags.append(rect(40, 90, 800, 32, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(text(440, 111, "Паралельний DNS: запити A та AAAA відправлено одночасно (Resolution Delay = 50 мс)", size=11, bold=True))

    # Етап 2: Старт IPv6 (t = 0 мс)
    frags.append(arrow(c_client, 145, c_v6, 145, color=POS, sw=1.8))
    frags.append(text((c_client + c_v6) / 2, 137, "t = 0 мс: Старт спроби 1 → TCP SYN [IPv6]", size=11, color=POS, bold=True))
    frags.append(text((c_client + c_v6) / 2, 160, "Запуск таймера Connection Attempt Delay (250 мс)", size=10, color=MUTED))

    # Втрата пакета на IPv6
    frags.append(circle(c_v6, 145, 10, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(c_v6, 149, "✖", size=12, color=POS, bold=True))

    # Інтервал очікування 250 мс
    frags.append(line(c_client - 40, 145, c_client - 40, 235, color=MUTED, sw=1.5))
    frags.append(line(c_client - 45, 145, c_client - 35, 145, color=MUTED, sw=1.5))
    frags.append(line(c_client - 45, 235, c_client - 35, 235, color=MUTED, sw=1.5))
    frags.append(text(c_client - 85, 195, "250 мс", size=11, color=MUTED, bold=True))

    # Етап 3: Старт IPv4 після таймауту 250 мс (t = 250 мс)
    frags.append(arrow(c_client, 235, c_v4, 235, color=FIELD, sw=1.8))
    frags.append(text((c_client + c_v4) / 2, 227, "t = 250 мс: Сплив таймер 250 мс → Старт спроби 2: TCP SYN [IPv4]", size=11, color=FIELD, bold=True))
    frags.append(text((c_client + c_v4) / 2, 248, "Обидва з'єднання активні паралельно у гонці!", size=10, color=FIELD, italic=True))

    # Етап 4: Прибуття SYN-ACK IPv4 (t = 290 мс)
    frags.append(arrow(c_v4, 290, c_client, 290, color=FIELD, sw=1.8))
    frags.append(text((c_client + c_v4) / 2, 282, "t = 290 мс: TCP SYN-ACK [IPv4] успішно прибув (RTT = 40 мс)", size=11, color=FIELD, bold=True))

    # Етап 5: Завершення гонки (t = 290 мс)
    frags.append(rect(c_client - 95, 315, 360, 48, fill="#e8f6ed", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(c_client + 85, 333, "t = 290 мс: Перемога IPv4 в гонці!", size=12, color=FIELD, bold=True))
    frags.append(text(c_client + 85, 351, "Відправлено TCP ACK [IPv4], канал готовий для TLS/HTTP", size=10, color=INK))

    # Скасування IPv6
    frags.append(rect(c_client - 95, 375, 360, 42, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    frags.append(text(c_client + 85, 393, "Скасування IPv6: сокет закривається (close)", size=11, color=POS, bold=True))
    frags.append(text(c_client + 85, 409, "Якщо пізніше прийде SYN-ACK — ядро відповість TCP RST", size=10, color=MUTED))

    # Підсумковий плакат
    frags.append(rect(40, 430, 800, 32, fill="#eef8f2", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(440, 451, "Загальна затримка для користувача: 290 мс (замість 30 с при наївному послідовному очікуванні)", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "fig2-happy-eyeballs-racing.svg"), w, h, *frags)


def make_fig3():
    """Фігура 3: Кінцевий автомат та архітектура Happy Eyeballs v2."""
    w, h = 880, 520
    frags = []

    # Верхній блок: DNS
    b_dns, _, _ = textbox(220, 65, "1. DNS Resolution\nЗапити A та AAAA одночасно.\nТаймер Resolution Delay (50 мс)", size=12, bold=True, pad=10, fill="#eef2f7", min_w=260)

    # Чергування адрес
    b_sort, _, _ = textbox(660, 65, "2. Address Interleaving\nСортування RFC 6724 + чергування:\n[IPv6_0, IPv4_0, IPv6_1, IPv4_1...]", size=12, bold=True, pad=10, fill="#eef2f7", min_w=280)

    frags.extend([b_dns, b_sort])
    frags.append(arrow(360, 65, 510, 65, color=LINE, sw=1.8))
    frags.append(text(435, 55, "Списки IP", size=11, bold=True))

    # Планувальник з'єднань
    b_sched, _, _ = textbox(660, 190, "3. Connection Scheduler\nЗапуск спроб із Connection Attempt Delay (250 мс)\nНеблокуючі сокети connect()", size=12, bold=True, pad=10, fill="#fffaf0", stroke="#d97706", min_w=280)
    frags.append(b_sched)
    frags.append(arrow(660, 105, 660, 150, color=LINE, sw=1.8))

    # Пул активних сокетів (гонка)
    b_pool, _, _ = textbox(220, 190, "4. Socket Racing Pool\nАсинхронний цикл подій (epoll/kqueue)\nПаралельний моніторинг готовності сокетів", size=12, bold=True, pad=10, fill="#eef2f7", min_w=260)
    frags.append(b_pool)
    frags.append(arrow(510, 190, 360, 190, color=LINE, sw=1.8))
    frags.append(text(435, 180, "Додати сокет", size=11, bold=True))

    # Переможець гонки
    b_win, _, _ = textbox(220, 330, "5. Winner Handshake\nПерший сокет з успішним SYN-ACK\nпередається додатку для передачі даних", size=12, bold=True, pad=10, fill="#e8f6ed", stroke=FIELD, min_w=260)
    frags.append(b_win)
    frags.append(arrow(220, 235, 220, 285, color=FIELD, sw=2))
    frags.append(text(165, 260, "TCP Handshake OK", size=11, color=FIELD, bold=True))

    # Очищення невдах
    b_clean, _, _ = textbox(660, 330, "6. Cleanup & Reset (RST)\nНегайне закриття всіх інших сокетів пулу.\nЗвільнення ресурсів клієнта й сервера", size=12, bold=True, pad=10, fill="#fdecea", stroke=POS, min_w=280)
    frags.append(b_clean)
    frags.append(arrow(360, 330, 510, 330, color=POS, sw=1.8))
    frags.append(text(435, 320, "Скасувати невдах", size=11, color=POS, bold=True))

    # Кеш стану мережі
    b_cache, _, _ = textbox(440, 455, "7. Historical RDA State / Кеш працездатності\nЗбереження RTT та збоїв для префіксів / інтерфейсів.\nТимчасовий backoff для непрацездатних родин адрес", size=12, bold=True, pad=10, fill="#f4f6f8", stroke=LINE, min_w=460)
    frags.append(b_cache)

    frags.append(arrow(220, 375, 350, 420, color=FIELD, sw=1.5))
    frags.append(arrow(660, 375, 530, 420, color=POS, sw=1.5))
    frags.append(text(250, 410, "Успіх RTT", size=10, color=FIELD))
    frags.append(text(620, 410, "Збій IPv6", size=10, color=POS))

    render(os.path.join(OUT_DIR, "fig3-happy-eyeballs-state-machine.svg"), w, h, *frags)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    make_fig1()
    make_fig2()
    make_fig3()
    print("Згенеровано 3 фігури у", OUT_DIR)


if __name__ == "__main__":
    main()
