#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фігури до теми «Каркас автентифікації SASL (RFC 4422)»."""

import os
import sys

# Шлях до scripts/ у корені репо (4 рівні вгору від book/communications/cryptographic-comm/sasl-framework/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. Архітектурна матриця SASL: розділення прикладних протоколів та криптографічних механізмів
def fig_sasl_architecture_matrix():
    W, H = 960, 460
    f = []

    f.append(text(W / 2.0, 28, "Архітектурне розділення SASL: усунення складності M × N", size=16, bold=True))

    # Верхній рівень: Прикладні протоколи
    f.append(rect(30, 55, 900, 95, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(480, 78, "Прикладні мережеві протоколи (Application Protocols)", size=13, bold=True, color=NEG))

    proto_names = [
        ("IMAP4rev1", "RFC 3501"),
        ("SMTP AUTH", "RFC 4954"),
        ("POP3", "RFC 5034"),
        ("LDAPv3", "RFC 4513"),
        ("XMPP Core", "RFC 6120"),
        ("Apache Kafka", "KIP-43 / SASL"),
        ("PostgreSQL", "Frontend v3"),
        ("AMQP 1.0", "OASIS / ISO"),
    ]
    for i, (name, rfc) in enumerate(proto_names):
        bx = 45 + i * 110
        f.append(fitbox(bx, 92, 102, 46, "%s\n%s" % (name, rfc), size=10, pad=3, fill="#ffffff", stroke=NEG))

    # Стрілки вниз до ядра SASL
    f.append(arrow(180, 150, 180, 185, color=LINE, sw=1.5))
    f.append(arrow(380, 150, 380, 185, color=LINE, sw=1.5))
    f.append(arrow(580, 150, 580, 185, color=LINE, sw=1.5))
    f.append(arrow(780, 150, 780, 185, color=LINE, sw=1.5))

    # Середній рівень: Універсальний каркас SASL (RFC 4422)
    f.append(rect(30, 185, 900, 110, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(text(480, 210, "Каркас SASL (Simple Authentication and Security Layer — RFC 4422)", size=14, bold=True, color=INK))

    f.append(fitbox(50, 225, 265, 58, "Протокольний профіль\n• Оголошення підтримуваних схем\n• Інкапсуляція викликів (Base64)\n• Сигналізація результату (OK / FAIL)", size=10, pad=5, fill="#ffffff", stroke=MUTED))
    f.append(fitbox(340, 225, 280, 58, "Абстрактний рушій стану\n• Вибір механізму клієнтом\n• Цикл «виклик-відповідь» (Loop)\n• Контекст автентифікації та Authzid", size=10, pad=5, fill="#ffffff", stroke=MUTED))
    f.append(fitbox(645, 225, 265, 58, "Рівень безпеки (Security Layer)\n• Узгодження QOP (auth, int, conf)\n• Обрамлення потоку (4-byte length)\n• Зв'язування з каналом (GS2 / Plus)", size=10, pad=5, fill="#ffffff", stroke=MUTED))

    # Стрілки вниз до механізмів
    f.append(arrow(180, 295, 180, 330, color=LINE, sw=1.5))
    f.append(arrow(380, 295, 380, 330, color=LINE, sw=1.5))
    f.append(arrow(580, 295, 580, 330, color=LINE, sw=1.5))
    f.append(arrow(780, 295, 780, 330, color=LINE, sw=1.5))

    # Нижній рівень: Криптографічні механізми
    f.append(rect(30, 330, 900, 110, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    f.append(text(480, 352, "Під'єднувані криптографічні механізми (Pluggable Authentication Mechanisms)", size=13, bold=True, color=POS))

    mechs = [
        ("PLAIN", "RFC 4616\nПароль у TLS"),
        ("EXTERNAL", "RFC 4422\nmTLS / IPsec / Unix"),
        ("SCRAM-SHA-256", "RFC 7677 / 5802\nСолений виклик"),
        ("GSSAPI (Kerberos)", "RFC 4752 / 4120\nКвитки KDC / SPN"),
        ("OAUTHBEARER", "RFC 7628 / 6750\nOAuth 2.0 токени"),
    ]
    for i, (name, desc) in enumerate(mechs):
        bx = 45 + i * 175
        f.append(fitbox(bx, 366, 165, 62, "%s\n%s" % (name, desc), size=10, pad=4, fill="#ffffff", stroke=POS))

    render(os.path.join(OUT, 'sasl-architecture-matrix.svg'), W, H, *f)


# 2. Життєвий цикл діалогу SASL: фази узгодження, циклу та завершення
def fig_sasl_state_machine():
    W, H = 960, 560
    f = []

    f.append(text(W / 2.0, 28, "Протокольний діалог SASL: етапи взаємодії та рушій станів", size=16, bold=True))

    # Стовпчик Клієнта
    f.append(rect(40, 55, 230, 485, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(155, 80, "Клієнт (Client Initiator)", size=13, bold=True, color=NEG))
    f.append(text(155, 98, "Застосунок + SASL Client Library", size=10, color=MUTED))

    # Стовпчик Сервера
    f.append(rect(690, 55, 230, 485, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(805, 80, "Сервер (Server Acceptor)", size=13, bold=True, color=POS))
    f.append(text(805, 98, "Служба + SASL Server Library", size=10, color=MUTED))

    # Лінії життя (пунктирні сегменти)
    f.append(line(155, 110, 155, 270, color=MUTED, sw=1, dash="4,4"))
    f.append(line(155, 340, 155, 520, color=MUTED, sw=1, dash="4,4"))

    f.append(line(805, 110, 805, 185, color=MUTED, sw=1, dash="4,4"))
    f.append(line(805, 245, 805, 410, color=MUTED, sw=1, dash="4,4"))
    f.append(line(805, 475, 805, 520, color=MUTED, sw=1, dash="4,4"))

    # Фаза 1: Оголошення можливостей
    f.append(arrow(805, 135, 160, 135, color=POS, sw=1.8))
    b1, _, _ = textbox(480, 125, "1. Capability / Mechanism List: AUTH=SCRAM-SHA-256 GSSAPI PLAIN", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(b1)
    f.append(text(480, 155, "Сервер передає перелік дозволених механізмів у прикладній команді", size=10, color=MUTED))

    # Фаза 2: Вибір механізму та початкова відповідь
    f.append(arrow(155, 195, 800, 195, color=NEG, sw=1.8))
    b2, _, _ = textbox(480, 185, "2. AUTH SCRAM-SHA-256 [biwsbj1hbGljZSxyPW5vbmNl...]", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b2)
    f.append(text(480, 215, "Клієнт обирає найстійкіший механізм і надсилає Initial Client Response (опційно)", size=10, color=MUTED))

    # Фаза 3: Цикл викликів та відповідей (Challenge-Response Loop)
    f.append(rect(290, 235, 380, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(480, 252, "Цикл обміну викликами (0..N ітерацій)", size=10, bold=True, color=MUTED))

    f.append(arrow(805, 280, 160, 280, color=POS, sw=1.8))
    b3, _, _ = textbox(480, 275, "+ cj1ub25jZTExc2FsdD1zYWx0LGl0ZXI9NDAxNg==", size=10, pad=5, fill="#fdecea", stroke=POS)
    f.append(b3)
    f.append(text(480, 302, "Серверний виклик (Challenge) у кодуванні Base64", size=9, color=MUTED))

    f.append(arrow(155, 335, 800, 335, color=NEG, sw=1.8))
    b4, _, _ = textbox(480, 330, "Yz1iaXdzLHI9bm9uY2UxMSxwPXByb29mNDI=", size=10, pad=5, fill="#eaf0fd", stroke=NEG)
    f.append(b4)
    f.append(text(480, 357, "Клієнтська відповідь (Response) із криптодоказом", size=9, color=MUTED))

    # Фаза 4: Фінальний результат
    f.append(arrow(805, 430, 160, 430, color=FIELD, sw=2))
    b5, _, _ = textbox(480, 420, "4. OK [v=dj1zZXJ2ZXJzaWduYXR1cmU=] / SASL Success", size=11, pad=6, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(b5)
    f.append(text(480, 450, "Сервер підтверджує автентифікацію (з додатковими даними підпису або без)", size=10, color=MUTED))

    # Фаза 5: Подальший стан
    f.append(fitbox(50, 475, 210, 52, "Встановлено контекст:\n• Автентифікований суб'єкт\n• Узгоджений рівень безпеки (QOP)", size=9, pad=4, fill="#ffffff", stroke=LINE))
    f.append(fitbox(700, 475, 210, 52, "Готовність до команд:\n• Перехід до прикладних запитів\n• Увімкнення Security Layer або TLS", size=9, pad=4, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, 'sasl-state-machine.svg'), W, H, *f)


# 3. Обрамлення рівня безпеки (Security Layer Framing)
def fig_sasl_security_layer_frame():
    W, H = 960, 460
    f = []

    f.append(text(W / 2.0, 28, "Обрамлення потоку даних рівнем безпеки SASL Security Layer", size=16, bold=True))

    # Верхній блок: Сирі прикладні дані
    f.append(rect(40, 55, 880, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(480, 80, "Вихідний прикладний потік (Application Stream PDU)", size=13, bold=True, color=INK))
    f.append(text(480, 100, "Текстові команди (IMAP, SMTP) або бінарні кадри (Kafka, LDAP)", size=11, color=MUTED))

    # Стрілка перетворення
    f.append(arrow(480, 115, 480, 150, color=LINE, sw=2))
    f.append(text(550, 135, "sasl_encode()", size=11, bold=True, color=NEG))

    # Середній блок: SASL-пакет із 4-байтовим префіксом довжини
    f.append(rect(40, 150, 880, 110, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    f.append(text(480, 172, "Кадр безпеки SASL (RFC 4422 Security Layer Frame)", size=13, bold=True, color=INK))

    # Поле 1: 4-байтовий префікс довжини
    f.append(fitbox(60, 185, 240, 60, "4 байти довжини (Big-Endian)\nuint32: розмір тіла N байтів", size=10, pad=5, fill="#eaf0fd", stroke=NEG))

    # Поле 2: Захищене тіло (N байтів)
    f.append(fitbox(320, 185, 580, 60, "Захищене корисне навантаження (N байтів)\nЗашифрований шифротекст або відкриті дані з підписом HMAC", size=10, pad=5, fill="#fdecea", stroke=POS))

    # Нижній блок: Рівні якості захисту (QOP)
    f.append(rect(40, 275, 880, 165, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    f.append(text(480, 298, "Режими якості захисту (Quality of Protection — QOP)", size=13, bold=True, color=INK))

    f.append(fitbox(60, 315, 270, 110, "auth (Автентифікація)\n\nПрефікс довжини відсутній.\nДані передаються відкритим сокетом\nбез додаткового обрамлення.", size=10, pad=5, fill="#ffffff", stroke=LINE))
    f.append(fitbox(345, 315, 270, 110, "auth-int (Цілісність)\n\nПакет із 4-байтовим префіксом.\nДані захищено підписом HMAC / MIC\nвід модифікацій та ін'єкцій.", size=10, pad=5, fill="#ffffff", stroke=LINE))
    f.append(fitbox(630, 315, 270, 110, "auth-conf (Конфіденційність)\n\nПакет із 4-байтовим префіксом.\nПовне симетричне шифрування\n+ автентифікація кожного кадру.", size=10, pad=5, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, 'sasl-security-layer-frame.svg'), W, H, *f)


# 4. Прив'язка до каналу (Channel Binding) та захист від MITM
def fig_sasl_channel_binding():
    W, H = 960, 480
    f = []

    f.append(text(W / 2.0, 28, "Прив'язка до каналу (Channel Binding): захист від підміни через TLS-проксі", size=16, bold=True))

    # Клієнт (x: 40..220)
    f.append(rect(40, 55, 180, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(130, 80, "Легітимний Клієнт", size=13, bold=True, color=NEG))
    f.append(fitbox(50, 100, 160, 80, "Встановлює TLS A:\nОбчислює відбиток\nCB_A = H(Cert_A)\nнаприклад SHA-256", size=10, pad=4, fill="#ffffff", stroke=NEG))

    # MITM Проксі (x: 390..570)
    f.append(rect(390, 55, 180, 340, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    f.append(text(480, 80, "MITM Проксі", size=13, bold=True, color=POS))
    f.append(fitbox(400, 100, 160, 80, "Розриває TLS:\nСесія A: власний Cert_A\nСесія B: серверний Cert_B\nПересилає SASL-доказ", size=10, pad=4, fill="#ffffff", stroke=POS))

    # Сервер (x: 740..920)
    f.append(rect(740, 55, 180, 340, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=8))
    f.append(text(830, 80, "Цільовий Сервер", size=13, bold=True, color=FIELD))
    f.append(fitbox(750, 100, 160, 80, "Приймає TLS B:\nВолодіє Cert_B\nОбчислює свій відбиток\nCB_B = H(Cert_B)", size=10, pad=4, fill="#ffffff", stroke=FIELD))

    # Тунель TLS A
    f.append(fitbox(230, 110, 150, 60, "Канал TLS A\n(Cert_A атакуючого)", size=10, pad=3, fill="#eaf0fd", stroke=NEG))

    # Тунель TLS B
    f.append(fitbox(580, 110, 150, 60, "Канал TLS B\n(Cert_B сервера)", size=10, pad=3, fill="#eafaf1", stroke=FIELD))

    # SASL повідомлення від клієнта
    f.append(arrow(220, 220, 390, 220, color=NEG, sw=2))
    f.append(fitbox(230, 235, 150, 65, "Client-First:\np=tls-server-end-point\nВкладено CB_A", size=9, pad=3, fill="#ffffff", stroke=NEG))

    # Форвардинг від MITM
    f.append(arrow(570, 220, 740, 220, color=POS, sw=2))
    f.append(fitbox(580, 235, 150, 65, "Форвардинг:\nПересилає Client-First\nз незмінним CB_A", size=9, pad=3, fill="#ffffff", stroke=POS))

    # Блок верифікації на сервері
    f.append(fitbox(750, 230, 160, 95, "Верифікація на сервері:\nCB_A (з токена) ≟ CB_B\nВідбитки не збіглися!\n\n→ ДОСТУП ВІДХИЛЕНО", size=10, pad=4, fill="#fdecea", stroke=POS, bold=True, color=POS))

    # Пояснення внизу
    f.append(fitbox(40, 410, 880, 50, "Захист Channel Binding: атакуючий не може підмінити CB_A на CB_B у Client-First без знання пароля клієнта,\nоскільки відбиток каналу криптографічно зв'язаний із підписом ClientProof (SCRAM-SHA-256-PLUS).", size=10, pad=4, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'sasl-channel-binding.svg'), W, H, *f)


if __name__ == "__main__":
    fig_sasl_architecture_matrix()
    fig_sasl_state_machine()
    fig_sasl_security_layer_frame()
    fig_sasl_channel_binding()
    print("Всі фігури SASL успішно згенеровано.")
