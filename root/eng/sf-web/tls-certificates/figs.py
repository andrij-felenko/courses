# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_chain_of_trust():
    """Ієрархія довіри X.509: від кореневого сертифіката через проміжний до кінцевого."""
    W, H = 940, 520
    frags = []
    frags.append(text(W / 2, 28, "Ієрархія довіри X.509: від локального якоря до кінцевого сервера",
                      size=16, bold=True))

    # 1. Root CA
    frags.append(rect(40, 55, 520, 125, fill="#edf7ed", stroke="#2e7d32", sw=1.8, rx=8))
    frags.append(text(300, 80, "Кореневий центр сертифікації (Root CA)", size=14, bold=True, color="#1e4620"))
    frags.append(text(300, 102, "Subject: CN = GlobalTrust Root CA  |  Issuer: CN = GlobalTrust Root CA (Self-signed)", size=11, color=INK))
    frags.append(text(300, 122, "Розширення: Basic Constraints (CA: TRUE, pathLen: 1), Key Usage: keyCertSign", size=10.5, color=MUTED))
    frags.append(text(300, 142, "Відкритий ключ Root CA використовується для перевірки підпису Intermediate CA", size=10.5, color="#2e7d32", bold=True))
    frags.append(text(300, 162, "Приватний ключ Root CA зберігається у вимкненому апаратному модулі (Offline HSM)", size=10, color=MUTED, italic=True))

    # Right side note for Root CA
    box_r, _, _ = textbox(740, 117, "Локальне сховище довіри\n(Trust Store ОС / Браузера)\nПопередньо встановлені сертифікати,\nяким клієнт безумовно довіряє",
                          size=11, min_w=300, fill="#f4f6f8", stroke="#2e7d32")
    frags.append(box_r)
    frags.append(line(560, 117, 590, 117, color="#2e7d32", sw=1.5, dash="4,3"))

    # Arrow 1: Root signs Intermediate
    frags.append(arrow(300, 180, 300, 215, color="#2e7d32", sw=2.2))
    frags.append(text(315, 202, "Підпис Root CA (SHA-256 з RSA/ECDSA)", size=10.5, color="#1e4620", bold=True, anchor="start"))

    # 2. Intermediate CA
    frags.append(rect(40, 220, 520, 125, fill="#e8f4fd", stroke="#1976d2", sw=1.8, rx=8))
    frags.append(text(300, 245, "Проміжний центр сертифікації (Intermediate CA)", size=14, bold=True, color="#0d47a1"))
    frags.append(text(300, 267, "Subject: CN = GlobalTrust Server CA G2  |  Issuer: CN = GlobalTrust Root CA", size=11, color=INK))
    frags.append(text(300, 287, "Розширення: Basic Constraints (CA: TRUE, pathLen: 0), Key Usage: keyCertSign", size=10.5, color=MUTED))
    frags.append(text(300, 307, "Відкритий ключ Intermediate CA використовується для перевірки підпису Leaf", size=10.5, color="#1976d2", bold=True))
    frags.append(text(300, 327, "Працює онлайн для автоматичного щоденного випуску кінцевих сертифікатів", size=10, color=MUTED, italic=True))

    # Right side note for Intermediate
    box_i, _, _ = textbox(740, 282, "Передається сервером у TLS\nСервер зобов'язаний надіслати\nIntermediate разом зі своїм сертифікатом\nу повідомленні Certificate",
                          size=11, min_w=300, fill="#f4f6f8", stroke="#1976d2")
    frags.append(box_i)
    frags.append(line(560, 282, 590, 282, color="#1976d2", sw=1.5, dash="4,3"))

    # Arrow 2: Intermediate signs Leaf
    frags.append(arrow(300, 345, 300, 380, color="#1976d2", sw=2.2))
    frags.append(text(315, 367, "Підпис Intermediate CA", size=10.5, color="#0d47a1", bold=True, anchor="start"))

    # 3. Leaf Certificate
    frags.append(rect(40, 385, 520, 120, fill="#fff8e1", stroke="#f57c00", sw=1.8, rx=8))
    frags.append(text(300, 410, "Кінцевий сертифікат сервера (Leaf / End-Entity)", size=14, bold=True, color="#e65100"))
    frags.append(text(300, 432, "Subject: CN = api.example.com  |  Issuer: CN = GlobalTrust Server CA G2", size=11, color=INK))
    frags.append(text(300, 452, "SAN: DNS:api.example.com, DNS:example.com  |  EKU: id-kp-serverAuth", size=10.5, color=INK))
    frags.append(text(300, 472, "Basic Constraints: CA: FALSE (заборона випускати підлеглі сертифікати)", size=10.5, color="#c0392b", bold=True))
    frags.append(text(300, 492, "Приватний ключ належить веб-серверу (використовується в TLS Handshake)", size=10, color=MUTED, italic=True))

    # Right side note for Leaf
    box_l, _, _ = textbox(740, 445, "Валідація клієнтом\n1. Перевірка підписів знизу вгору\n2. Перевірка дат notBefore..notAfter\n3. Перевірка збігу SAN з URL хоста",
                          size=11, min_w=300, fill="#f4f6f8", stroke="#f57c00")
    frags.append(box_l)
    frags.append(line(560, 445, 590, 445, color="#f57c00", sw=1.5, dash="4,3"))

    render(os.path.join(IMG, "chain-of-trust.svg"), W, H, *frags)


def fig_san_hostname_validation():
    """Алгоритм перевірки доменного імені за розширенням SAN."""
    W, H = 940, 460
    frags = []
    frags.append(text(W / 2, 28, "Алгоритм перевірки імені хоста клієнтом (SAN / RFC 6125)",
                      size=16, bold=True))

    # Left: Requested URL Host
    b_req, _, _ = textbox(160, 95, "Цільовий запит клієнта\nURL: https://api.prod.example.com/v1\nХост для перевірки: api.prod.example.com",
                          size=11.5, min_w=260, fill="#edf7ed", stroke="#2e7d32", bold=True)
    frags.append(b_req)

    # Middle: Certificate SAN entries
    b_san, _, _ = textbox(520, 95, "Кінцевий сертифікат сервера (Leaf)\nSubject Alternative Name (SAN):\n1. DNS:api.prod.example.com\n2. DNS:*.example.com\n3. DNS:example.com",
                          size=11, min_w=320, fill="#fff8e1", stroke="#f57c00")
    frags.append(b_san)

    frags.append(arrow(290, 95, 360, 95, color=INK, sw=2))

    # Decision Matrix / Rules
    frags.append(rect(40, 175, 860, 265, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 202, "Правила зіставлення та критерії прийняття рішення", size=13.5, bold=True))

    rules = [
        ("Сценарій 1: Точний збіг у SAN", "DNS:api.prod.example.com збігається з хостом api.prod.example.com", "УСПІХ: ідентичність підтверджена", "#27ae60", True),
        ("Сценарій 2: Wildcard на рівень вище (*.example.com)", "Шаблон *.example.com покриває ТІЛЬКИ один рівень (app.example.com), але НЕ api.prod", "ВІДХИЛЕНО: зірочка не покриває крапку", "#c0392b", False),
        ("Сценарій 3: Запит за IP-адресою (https://192.0.2.1)", "Потрібен запис типу iPAddress:192.0.2.1 у SAN, запис dNSName не підходить", "УМОВНИЙ: залежить від типу SAN", "#2457d6", True),
        ("Сценарій 4: Відсутній SAN, але присутній Subject CN", "Застарілий підхід (RFC 2818). Сучасні клієнти (RFC 6125, Chrome, Python 3.7+) ігнорують CN", "ВІДХИЛЕНО: CN застарів і відкинутий", "#c0392b", False),
    ]

    y_pos = 238
    for title, desc, verdict, color, is_ok in rules:
        frags.append(rect(55, y_pos - 18, 510, 42, fill=FILL, stroke="#d1d5db", sw=1, rx=5))
        frags.append(text(65, y_pos - 2, title, size=10.5, bold=True, anchor="start", color=INK))
        frags.append(text(65, y_pos + 14, desc, size=9.5, color=MUTED, anchor="start"))

        frags.append(rect(580, y_pos - 18, 305, 42, fill="#fdecea" if not is_ok else ("#eafaf1" if color=="#27ae60" else "#eaf0fd"),
                          stroke=color, sw=1.3, rx=5))
        frags.append(text(732, y_pos + 7, verdict, size=10, bold=True, color=color))
        y_pos += 52

    render(os.path.join(IMG, "san-hostname-validation.svg"), W, H, *frags)


def fig_mtls_handshake_flow():
    """Послідовність повідомлень TLS 1.3 під час взаємної автентифікації (mTLS)."""
    W, H = 940, 520
    frags = []
    frags.append(text(W / 2, 28, "Взаємна автентифікація mTLS у протоколі TLS 1.3 (RFC 8446)",
                      size=16, bold=True))

    # Left Column: Client
    frags.append(rect(60, 55, 230, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(175, 82, "Клієнт (Client)", size=14, bold=True))
    frags.append(text(175, 102, "Має свій сертифікат і ключ", size=10.5, color=MUTED))

    # Right Column: Server
    frags.append(rect(650, 55, 230, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(765, 82, "Сервер (Server)", size=14, bold=True))
    frags.append(text(765, 102, "Вимагає перевірку клієнта", size=10.5, color=MUTED))

    # Handshake Timeline
    # 1. ClientHello
    frags.append(arrow(290, 140, 650, 140, color=INK, sw=2))
    frags.append(text(470, 130, "1. ClientHello: SupportedGroups, KeyShare (ECDH), SNI", size=10.5, bold=True, color=INK))

    # 2. ServerHello & Encrypted params
    frags.append(arrow(650, 190, 290, 190, color="#1976d2", sw=2))
    frags.append(text(470, 178, "2. ServerHello + KeyShare (ECDH) [Відтепер трафік зашифровано]", size=10.5, bold=True, color="#1976d2"))
    frags.append(text(470, 202, "{EncryptedExtensions, CertificateRequest, Certificate, CertificateVerify, Finished}", size=9.5, color="#0d47a1"))

    # Server Note on CertificateRequest
    b_sr, _, _ = textbox(765, 245, "CertificateRequest:\nСервер вказує допустимі CA\nта алгоритми підпису",
                         size=10, min_w=200, fill="#fff8e1", stroke="#f57c00")
    frags.append(b_sr)

    # Client Note on verification
    b_cv, _, _ = textbox(175, 245, "Клієнт валідує сервер:\n1. Ланцюг сертифіката сервера\n2. Збіг імені в розширенні SAN",
                         size=10, min_w=200, fill="#edf7ed", stroke="#2e7d32")
    frags.append(b_cv)

    # 3. Client Response with Certificate & Verify
    frags.append(arrow(290, 315, 650, 315, color="#2e7d32", sw=2))
    frags.append(text(470, 305, "3. {Certificate, CertificateVerify, Finished}", size=10.5, bold=True, color="#2e7d32"))
    frags.append(text(470, 327, "Клієнт надсилає свій сертифікат і цифровий підпис транскрипту", size=9.5, color="#1e4620"))

    # Server verifies client
    b_scv, _, _ = textbox(765, 375, "Сервер валідує клієнта:\n1. Підпис CertificateVerify\n2. Ланцюг довіри клієнтського CA\n3. Видобуває ID клієнта",
                          size=10, min_w=200, fill="#edf7ed", stroke="#2e7d32")
    frags.append(b_scv)

    # 4. Mutual Application Data
    frags.append(arrow(290, 440, 650, 440, color="#27ae60", sw=2.5))
    frags.append(arrow(650, 465, 290, 465, color="#27ae60", sw=2.5))
    frags.append(text(470, 432, "4. Двосторонній захищений прикладний потік (HTTP/2, REST, gRPC)", size=11, bold=True, color="#27ae60"))
    frags.append(text(470, 455, "Сервер авторизує клієнта безпосередньо за його X.509 ідентичністю", size=10, color=MUTED))

    render(os.path.join(IMG, "mtls-handshake-flow.svg"), W, H, *frags)


def fig_ocsp_stapling_flow():
    """Порівняння прямого опитування OCSP та механізму OCSP Stapling."""
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 28, "Перевірка статусу відкликання: прямий OCSP проти OCSP Stapling",
                      size=16, bold=True))

    # Left Side: Direct OCSP
    frags.append(rect(40, 55, 410, 350, fill="#fff5f5", stroke="#c0392b", sw=1.5, rx=8))
    frags.append(text(245, 82, "Традиційний прямий OCSP", size=13.5, bold=True, color="#c0392b"))
    frags.append(text(245, 102, "Клієнт самостійно запитує сервер CA", size=10.5, color=MUTED))

    frags.append(rect(60, 125, 110, 45, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    frags.append(text(115, 152, "Клієнт", size=11, bold=True))

    frags.append(rect(320, 125, 110, 45, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    frags.append(text(375, 152, "Веб-сервер", size=11, bold=True))

    frags.append(rect(190, 205, 120, 45, fill="#fdecea", stroke="#c0392b", sw=1.2, rx=5))
    frags.append(text(250, 232, "OCSP Responder (CA)", size=10, bold=True, color="#c0392b"))

    frags.append(arrow(170, 140, 320, 140, color=INK, sw=1.5))
    frags.append(text(245, 132, "1. TLS Handshake", size=9.5, color=INK))

    frags.append(arrow(115, 170, 210, 205, color="#c0392b", sw=1.5))
    frags.append(text(130, 195, "2. OCSP Запит", size=9.5, bold=True, color="#c0392b"))

    frags.append(arrow(270, 205, 150, 170, color="#c0392b", sw=1.5))
    frags.append(text(235, 185, "3. OCSP Відповідь", size=9.5, bold=True, color="#c0392b"))

    b_ocsp_bad, _, _ = textbox(245, 310, "Вади:\n• Затримка: +1 додатковий RTT до CA\n• Приватність: CA бачить відвідувані сайти користувача\n• Soft-fail: якщо CA лежить, браузер пропускає перевірку",
                               size=10, min_w=370, fill="#ffffff", stroke="#c0392b")
    frags.append(b_ocsp_bad)

    # Right Side: OCSP Stapling
    frags.append(rect(490, 55, 410, 350, fill="#f0fdf4", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(695, 82, "OCSP Stapling (RFC 6066)", size=13.5, bold=True, color="#27ae60"))
    frags.append(text(695, 102, "Сервер кешує підписану відповідь від CA", size=10.5, color=MUTED))

    frags.append(rect(510, 125, 110, 45, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    frags.append(text(565, 152, "Клієнт", size=11, bold=True))

    frags.append(rect(770, 125, 110, 45, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    frags.append(text(825, 152, "Веб-сервер", size=11, bold=True))

    frags.append(rect(765, 205, 120, 45, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=5))
    frags.append(text(825, 232, "OCSP Responder (CA)", size=10, bold=True, color="#27ae60"))

    # Server periodically fetches from CA
    frags.append(arrow(825, 170, 825, 205, color=MUTED, sw=1.2))
    frags.append(arrow(835, 205, 835, 170, color="#27ae60", sw=1.5))
    frags.append(text(875, 190, "Фонове\nоновлення", size=9.5, color=MUTED))

    # Handshake with stapled response
    frags.append(arrow(620, 140, 770, 140, color=INK, sw=1.5))
    frags.append(arrow(770, 155, 620, 155, color="#27ae60", sw=2))
    frags.append(text(695, 132, "1. TLS Handshake + status_request", size=9.5, color=INK))
    frags.append(text(695, 170, "2. Сервер надсилає вкладений OCSP підпис", size=9.5, bold=True, color="#27ae60"))

    b_ocsp_good, _, _ = textbox(695, 310, "Переваги:\n• Нульова затримка: клієнт не робить запитів до CA\n• Повна приватність: CA не знає, хто відвідує сервер\n• Hard-fail захист: прикріплений штамп часу від CA",
                                size=10, min_w=370, fill="#ffffff", stroke="#27ae60")
    frags.append(b_ocsp_good)

    render(os.path.join(IMG, "ocsp-stapling-flow.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_chain_of_trust()
    fig_san_hostname_validation()
    fig_mtls_handshake_flow()
    fig_ocsp_stapling_flow()
    print("All figures generated successfully.")
