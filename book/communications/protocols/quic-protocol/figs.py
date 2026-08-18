# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. quic-vs-tcp-stack: Порівняння мережевих стеків ──────────────────────────
def fig_quic_vs_tcp_stack():
    W, H = 820, 440
    p = []

    # Заголовки стеків
    p.append(fitbox(60, 20, 320, 36, "Традиційний стек (HTTP/2)", size=14, bold=True, fill="#eef2f7", stroke=LINE))
    p.append(fitbox(440, 20, 320, 36, "Сучасний стек QUIC (HTTP/3)", size=14, bold=True, fill="#eef2f7", stroke=LINE))

    # Стек HTTP/2 (зліва)
    p.append(fitbox(60, 70, 320, 48, "HTTP/2 (Кадрування, потоки, HPACK)\nПростір користувача", size=11.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(60, 126, 320, 48, "TLS 1.3 / 1.2 (Криптографія, безпека)\nОкремий рівень шифрування", size=11.5, fill="#fdecea", stroke=POS))
    p.append(fitbox(60, 182, 320, 70, "TCP (Надійна доставка, потік байтів,\nконтроль перевантаження, ковзне вікно)\nЯдро операційної системи (Kernel)", size=11.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(60, 260, 320, 44, "IP (IPv4 / IPv6 Маршрутизація)\nМережевий рівень", size=11.5, fill=FILL, stroke=LINE))
    p.append(fitbox(60, 312, 320, 44, "Канальний / Фізичний рівень (Ethernet, Wi-Fi, 5G)", size=11, fill=FILL, stroke=LINE))

    p.append(line(40, 178, 390, 178, color="#e74c3c", sw=1.5, dash="4 3"))
    p.append(text(220, 375, "Межа ядра: TCP зашитий у системний стек OS", size=10.5, color=MUTED, italic=True))

    # Стек QUIC (справа)
    p.append(fitbox(440, 70, 320, 48, "HTTP/3 (QPACK, мапінг запитів на потоки)\nПростір користувача", size=11.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(440, 126, 320, 104, "QUIC (RFC 9000 / RFC 9001 / RFC 9002)\n• Незалежні потоки без блокування (Streams)\n• Вбудований захист TLS 1.3 (0-RTT, крипто)\n• Контроль перевантаження у просторі процесу\n• Ідентифікатори з'єднань (Connection ID)", size=11, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(440, 238, 320, 44, "UDP (Проста датаграмна інкапсуляція)\nЯдро OS / Без стану черг", size=11.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(440, 290, 320, 44, "IP (IPv4 / IPv6 Маршрутизація)\nМережевий рівень", size=11.5, fill=FILL, stroke=LINE))
    p.append(fitbox(440, 342, 320, 44, "Канальний / Фізичний рівень (Ethernet, Wi-Fi, 5G)", size=11, fill=FILL, stroke=LINE))

    p.append(line(420, 234, 770, 234, color=FIELD, sw=1.5, dash="4 3"))
    p.append(text(600, 405, "QUIC реалізовано у просторі користувача поверх UDP", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "quic-vs-tcp-stack.svg"), W, H, *p,
           title="Порівняння мережевих стеків: монолітний TCP+TLS проти модульного QUIC+UDP")


# ── 2. hol-blocking-streams: Блокування початку черги ───────────────────────────
def fig_hol_blocking_streams():
    W, H = 820, 450
    p = []

    p.append(fitbox(40, 20, 740, 32, "TCP: Мультиплексування кількох потоків у єдиний монолітний потік байтів", size=12.5, bold=True, fill="#fdecea", stroke=POS))

    p.append(fitbox(50, 65, 130, 42, "Пакет 1 (Потік A)\nОтримано OK", size=10.5, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(190, 65, 130, 42, "Пакет 2 (Потік B)\nВТРАЧЕНО В КАНАЛІ", size=10.5, fill="#fdecea", stroke=POS, bold=True))
    p.append(fitbox(330, 65, 130, 42, "Пакет 3 (Потік C)\nОтримано в буфер", size=10.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(470, 65, 130, 42, "Пакет 4 (Потік A)\nОтримано в буфер", size=10.5, fill="#fff8e6", stroke="#d48800"))

    p.append(fitbox(50, 120, 720, 52, "Буфер ядра TCP (sk_buff): Потік A і C заблоковані у черзі очікування!\nЯдро Linux не віддає застосунку байти 3 і 4, доки не надійде повтор пакета 2 (Head-of-Line Blocking).", size=11, fill="#fdecea", stroke=POS))

    p.append(line(40, 195, 780, 195, color=MUTED, sw=1, dash="2 3"))

    p.append(fitbox(40, 215, 740, 32, "QUIC: Потоки є логічно незалежними структурами всередині UDP-датаграм", size=12.5, bold=True, fill="#eef6ef", stroke=FIELD))

    p.append(fitbox(50, 260, 160, 46, "Датаграма 10 (Потік A)\nЗсув 0..1200\nОбробляється негайно", size=10, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(220, 260, 160, 46, "Датаграма 11 (Потік B)\nЗсув 0..1200\nВТРАЧЕНО", size=10, fill="#fdecea", stroke=POS, bold=True))
    p.append(fitbox(390, 260, 160, 46, "Датаграма 12 (Потік C)\nЗсув 0..1200\nОбробляється негайно", size=10, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(560, 260, 160, 46, "Датаграма 13 (Потік A)\nЗсув 1200..2400\nОбробляється негайно", size=10, fill="#eef6ef", stroke=FIELD))

    p.append(fitbox(50, 320, 220, 60, "Потік A:\nОтримано байти 0..2400\nЗастосунок читає без затримки!", size=10.5, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(280, 320, 220, 60, "Потік B:\nОчікує повтору пакета\nЛише потік B на паузі", size=10.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(510, 320, 260, 60, "Потік C:\nОтримано байти 0..1200\nЗастосунок читає без затримки!", size=10.5, fill="#eef6ef", stroke=FIELD))

    p.append(fitbox(40, 395, 740, 36, "Результат: Втрата пакета в одному потоці QUIC не сповільнює паралельні потоки.", size=11, bold=True, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, "hol-blocking-streams.svg"), W, H, *p,
           title="Порівняння блокування Head-of-Line у TCP та незалежних потоків QUIC")


# ── 3. quic-handshake-timeline: Встановлення з'єднання 1-RTT та 0-RTT ───────────
def fig_quic_handshake_timeline():
    W, H = 840, 470
    p = []

    # Заголовки колонок
    p.append(text(210, 25, "Звичайне підключення (1-RTT Handshake)", size=13, bold=True, color=INK))
    p.append(text(630, 25, "Повторне підключення (0-RTT Resumption)", size=13, bold=True, color=INK))

    # Вісь часу 1-RTT
    p.append(text(60, 55, "Клієнт", size=11.5, bold=True, color=INK))
    p.append(text(360, 55, "Сервер", size=11.5, bold=True, color=INK))
    p.append(line(60, 65, 60, 350, color=LINE, sw=1.5))
    p.append(line(360, 65, 360, 350, color=LINE, sw=1.5))

    # 1-RTT Повідомлення 1 (Клієнт -> Сервер)
    p.append(arrow(60, 90, 360, 130, color=NEG, sw=1.8))
    p.append(text(210, 80, "QUIC Initial [ClientHello + Transport Params]", size=9.5, color=NEG, bold=True))

    # 1-RTT Повідомлення 2 (Сервер -> Клієнт)
    p.append(arrow(360, 150, 60, 190, color=FIELD, sw=1.8))
    p.append(text(210, 142, "Handshake [ServerHello, EE, Cert, Finished]", size=9.5, color=FIELD, bold=True))

    # 1-RTT Повідомлення 3 (Клієнт -> Сервер)
    p.append(arrow(60, 210, 360, 250, color=FIELD, sw=1.8))
    p.append(text(210, 202, "Handshake Finished + 1-RTT HTTP/3 Data", size=9.5, color=FIELD, bold=True))

    # 1-RTT Повідомлення 4 (Сервер -> Клієнт)
    p.append(arrow(360, 270, 60, 310, color=FIELD, sw=1.8))
    p.append(text(210, 262, "1-RTT HTTP/3 Відповідь сервера", size=9.5, color=FIELD, bold=True))

    # Підсумок 1-RTT
    p.append(fitbox(50, 370, 320, 65, "Час до першої відповіді: 1 RTT\n(У TCP+TLS 1.2 було 3 RTT,\nу TCP+TLS 1.3 було 2 RTT)", size=10.5, fill="#fff8e6", stroke="#d48800"))

    # Розділювач
    p.append(line(420, 20, 420, 445, color=MUTED, sw=1.2, dash="3 3"))

    # Вісь часу 0-RTT
    p.append(text(480, 55, "Клієнт", size=11.5, bold=True, color=INK))
    p.append(text(780, 55, "Сервер", size=11.5, bold=True, color=INK))
    p.append(line(480, 65, 480, 350, color=LINE, sw=1.5))
    p.append(line(780, 65, 780, 350, color=LINE, sw=1.5))

    # 0-RTT Повідомлення 1 (Клієнт -> Сервер: Initial + 0-RTT Data)
    p.append(arrow(480, 90, 780, 130, color=POS, sw=1.8))
    p.append(text(630, 80, "Initial [ClientHello, PSK] + 0-RTT Early Data (GET /)", size=9.5, color=POS, bold=True))

    # 0-RTT Повідомлення 2 (Сервер -> Клієнт: Handshake + 1-RTT Data)
    p.append(arrow(780, 150, 480, 190, color=FIELD, sw=1.8))
    p.append(text(630, 142, "Handshake [ServerHello, Finished] + HTTP/3 200 OK", size=9.5, color=FIELD, bold=True))

    # 0-RTT Повідомлення 3 (Клієнт -> Сервер: Finished)
    p.append(arrow(480, 210, 780, 250, color=FIELD, sw=1.8))
    p.append(text(630, 202, "Handshake Finished + наступні 1-RTT запити", size=9.5, color=FIELD, bold=True))

    # Підсумок 0-RTT
    p.append(fitbox(470, 370, 320, 65, "Час початку надсилання даних: 0 RTT!\nКлієнт надсилає прикладний HTTP-запит\nу найпершому UDP-пакеті разом із PSK.", size=10.5, fill="#eef6ef", stroke=FIELD, bold=True))

    render(os.path.join(OUT, "quic-handshake-timeline.svg"), W, H, *p,
           title="Часова діаграма рукостискання QUIC: порівняння 1-RTT та 0-RTT Resumption")


# ── 4. connection-migration: Міграція з'єднання ─────────────────────────────────
def fig_connection_migration():
    W, H = 820, 430
    p = []

    # Заголовок
    p.append(fitbox(40, 20, 740, 36, "Міграція з'єднання (Connection Migration) без розриву сесії", size=13, bold=True, fill="#eef2f7", stroke=LINE))

    # Вузол Клієнта (Смартфон)
    p.append(fitbox(50, 75, 200, 60, "Клієнт (Смартфон)\nCID = 0x83f1a9b2...\nПеремикання Wi-Fi -> LTE", size=11, fill="#fff8e6", stroke="#d48800"))

    # Вузол Сервера (Web / CDN)
    p.append(fitbox(570, 75, 200, 60, "Сервер (Edge Node)\nCID = 0x83f1a9b2...\nПрив'язка до CID, а не IP", size=11, fill="#eef6ef", stroke=FIELD))

    # Шлях 1: Початковий стан (Wi-Fi)
    p.append(fitbox(60, 155, 300, 48, "Початковий шлях (Wi-Fi):\nIP: 192.168.1.45:54321 -> Сервер :443", size=10.5, fill="#eaf0fd", stroke=NEG))
    p.append(arrow(370, 179, 560, 179, color=NEG, sw=1.8))
    p.append(text(465, 170, "1-RTT Data", size=9.5, color=NEG, bold=True))

    # Перемикання мережі
    p.append(fitbox(60, 220, 700, 36, "Подія: Користувач вийшов із зони Wi-Fi. Інтерфейс перемкнувся на стільникову мережу LTE (нова IP)", size=10.5, fill="#fdecea", stroke=POS, italic=True))

    # Шлях 2: Валідація шляху (LTE)
    p.append(fitbox(60, 275, 300, 52, "Новий шлях (LTE):\nIP: 100.64.22.8:61200 (Новий 4-tuple!)\nКлієнт шле PATH_CHALLENGE (8B)", size=10, fill="#fff8e6", stroke="#d48800"))

    p.append(arrow(370, 285, 560, 285, color=FIELD, sw=1.8))
    p.append(text(465, 277, "PATH_CHALLENGE", size=9, color=FIELD, bold=True))

    p.append(arrow(560, 315, 370, 315, color=FIELD, sw=1.8))
    p.append(text(465, 307, "PATH_RESPONSE", size=9, color=FIELD, bold=True))

    p.append(fitbox(570, 275, 200, 52, "Сервер відповідає:\nPATH_RESPONSE (8B)\nШлях підтверджено!", size=10, fill="#eef6ef", stroke=FIELD))

    # Підсумок у TCP проти QUIC
    p.append(fitbox(50, 355, 340, 50, "TCP при зміні IP: Повна загибель сесії!\nСокет скидається помилкою ECONNRESET,\nпотрібен новий TCP SYN + TLS Handshake.", size=10, fill="#fdecea", stroke=POS))

    p.append(fitbox(430, 355, 340, 50, "QUIC при зміні IP: Нульова затримка!\nПотоки даних продовжують передаватись\nзавдяки сталому ідентифікатору CID.", size=10, fill="#eef6ef", stroke=FIELD, bold=True))

    render(os.path.join(OUT, "connection-migration.svg"), W, H, *p,
           title="Процес міграції з'єднання QUIC між Wi-Fi та LTE за допомогою Connection ID")


# ── 5. packet-number-vs-offset: Розв'язання Replay Ambiguity ───────────────────
def fig_packet_number_vs_offset():
    W, H = 820, 430
    p = []

    # Заголовок
    p.append(fitbox(40, 20, 740, 34, "Розділення номера пакета (Packet Number) та зсуву потоку (Stream Offset)", size=12.5, bold=True, fill="#eef2f7", stroke=LINE))

    # Секція TCP з неоднозначністю (зліва)
    p.append(fitbox(50, 68, 330, 32, "TCP: Неоднозначність повторів (Retransmission Ambiguity)", size=10.5, bold=True, fill="#fdecea", stroke=POS))

    p.append(fitbox(60, 110, 310, 42, "Спроба 1: Сегмент Seq = 1000, Len = 500\n[Надіслано о t = 0 мс] -> Втрачено", size=9.5, fill="#fdecea", stroke=POS))
    p.append(fitbox(60, 160, 310, 42, "Спроба 2: Сегмент Seq = 1000, Len = 500\n[Повтор о t = 200 мс після таймауту]", size=9.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(60, 210, 310, 52, "Приймач шле ACK = 1500 о t = 250 мс.\nПитання: Це підтвердження спроби 1 (RTT = 250 мс)\nчи спроби 2 (RTT = 50 мс)? TCP не знає без опцій!", size=9.5, fill="#fdecea", stroke=POS))

    # Секція QUIC без неоднозначності (справа)
    p.append(fitbox(440, 68, 330, 32, "QUIC: Суворе монотонне зростання номера пакета", size=10.5, bold=True, fill="#eef6ef", stroke=FIELD))

    p.append(fitbox(450, 110, 310, 42, "Спроба 1: Пакет PN = 42\n[Кадр STREAM: Offset = 1000, Len = 500] -> Втрачено", size=9.5, fill="#fdecea", stroke=POS))
    p.append(fitbox(450, 160, 310, 42, "Спроба 2: Пакет PN = 43 (НОВИЙ номер!)\n[Кадр STREAM: Offset = 1000, Len = 500]", size=9.5, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(450, 210, 310, 52, "Приймач шле кадр ACK: Largest Acknowledged = 43.\nПередавач точно знає: підтверджено пакет 43!\nРозрахунок RTT є кристально точним і однозначним.", size=9.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Пояснення внизу
    p.append(fitbox(50, 285, 720, 60, "Ключовий принцип QUIC:\n• Номер пакета (Packet Number) належить виключно транспортному пакету й НІКОЛИ не повторюється.\n• Зсув потоку (Stream Offset) належить прикладним даним і вказує точне місце байтів у файлі.", size=10.5, fill="#eef2f7", stroke=LINE))

    p.append(fitbox(50, 360, 720, 45, "Вигода для контролю перевантаження: точна оцінка RTT дозволяє алгоритмам BBR та CUBIC\nмиттєво реагувати на стан черг у маршрутизаторах без хибних таймаутів.", size=10.5, fill="#eef6ef", stroke=FIELD))

    render(os.path.join(OUT, "packet-number-vs-offset.svg"), W, H, *p,
           title="Усунення неоднозначності повторів у QUIC завдяки розділенню Packet Number та Offset")


# ── 6. quic-packet-headers: Структура пакетів Long Header та Short Header ───────
def fig_quic_packet_headers():
    W, H = 820, 450
    p = []

    # Заголовок
    p.append(fitbox(40, 15, 740, 32, "Двійкова структура пакетів QUIC: Long Header проти Short Header (1-RTT)", size=12.5, bold=True, fill="#eef2f7", stroke=LINE))

    # Секція 1: Long Header (для Handshake, Initial, Retry, 0-RTT)
    p.append(text(50, 68, "1. Long Header (Використовується під час встановлення з'єднання: Initial, Handshake, 0-RTT, Retry)", size=11, bold=True, color=INK, anchor="start"))

    # Поля Long Header
    p.append(fitbox(50, 80, 80, 46, "Прапорці\nHeader Form=1\nType (2 біти)", size=9.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(135, 80, 90, 46, "Версія\nQUIC v1 (4B)\n0x00000001", size=9.5, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(230, 80, 120, 46, "Dest Conn ID\n(0..20 байтів)\nDCIL + DCID", size=9.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(355, 80, 120, 46, "Src Conn ID\n(0..20 байтів)\nSCIL + SCID", size=9.5, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(480, 80, 85, 46, "Token\n(Varint len\n+ Token data)", size=9, fill="#fdecea", stroke=POS))
    p.append(fitbox(570, 80, 90, 46, "Довжина +\nНомер пакета\n(1..4 байти)", size=9.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(665, 80, 115, 46, "Захищений\nPayload\n(Кадри + AEAD)", size=9.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Секція 2: Short Header (1-RTT Data — робочий стан)
    p.append(text(50, 155, "2. Short Header 1-RTT (Мінімальний оверхед для передачі прикладних даних)", size=11, bold=True, color=INK, anchor="start"))

    # Поля Short Header
    p.append(fitbox(50, 170, 160, 48, "Прапорці (1 байт):\nForm=0, Spin, KeyPhase,\nPacket Number Length", size=9.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(215, 170, 190, 48, "Destination Connection ID\n(Узгоджена довжина, 0..20 байтів)", size=10, fill="#fff8e6", stroke="#d48800"))
    p.append(fitbox(410, 170, 140, 48, "Packet Number\n(1..4 байти, масковано\nчерез Header Protection)", size=9.5, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(555, 170, 225, 48, "Зашифроване корисне навантаження (Payload)\nКадри STREAM, ACK, MAX_DATA + Тег AEAD (16B)", size=9.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Секція 3: Механізм Header Protection (Захист заголовків від прослуховування)
    p.append(text(50, 245, "3. Механізм захисту заголовків (Header Protection) проти відстеження проміжними вузлами:", size=11, bold=True, color=INK, anchor="start"))

    p.append(fitbox(50, 260, 220, 60, "Вибірка з Payload (16B):\nБеруться перші 16 байтів\nзашифрованого навантаження", size=10, fill="#eef6ef", stroke=FIELD))

    p.append(arrow(275, 290, 315, 290, color=LINE, sw=1.8))

    p.append(fitbox(320, 260, 210, 60, "Криптографічна маска:\nAES-ECB / ChaCha20\nіз ключем hp_key", size=10, fill="#fdecea", stroke=POS))

    p.append(arrow(535, 290, 575, 290, color=LINE, sw=1.8))

    p.append(fitbox(580, 260, 200, 60, "Операція XOR:\nМаскування 4 бітів прапорців\nта 1..4 байтів Packet Number", size=10, fill="#fff8e6", stroke="#d48800"))

    # Висновок про безпеку
    p.append(fitbox(40, 345, 740, 65, "Результат захисту: Проміжні маршрутизатори та інспекційні пристрої (Middleboxes) бачать лише UDP-заголовок\nта фіксований Connection ID. Номери пакетів, ознака фази ключів, біти кадрування та вміст повністю приховані,\nщо унеможливлює маніпуляції з трафіком на магістралях інтернету.", size=10.5, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, "quic-packet-headers.svg"), W, H, *p,
           title="Формати двійкових заголовків QUIC Long Header та Short Header із механізмом Header Protection")


if __name__ == "__main__":
    fig_quic_vs_tcp_stack()
    fig_hol_blocking_streams()
    fig_quic_handshake_timeline()
    fig_connection_migration()
    fig_packet_number_vs_offset()
    fig_packet_headers = fig_quic_packet_headers
    fig_packet_headers()
    print("All figures generated successfully.")
