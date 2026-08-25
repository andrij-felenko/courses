# -*- coding: utf-8 -*-
"""Фігури до теми «SOAP і веб-сервіси».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
BLUE  = "#2457d6"
GREEN = "#27ae60"
RED   = "#c0392b"
PURPLE = "#7b1fa2"


# ── 1. Анатомія конверта SOAP ────────────────────────────────────────────────
def fig_soap_envelope_structure():
    W, H = 840, 420
    f = [text(W / 2, 28, "Анатомія повідомлення SOAP (конверт, заголовок, тіло)", size=15, bold=True)]

    # Зовнішній прямокутник — Envelope
    ex, ey, ew, eh = 40, 50, 760, 340
    f.append(rect(ex, ey, ew, eh, fill="#f8fafd", stroke=BLUE, sw=2, rx=10))
    f.append(text(ex + 20, ey + 24, "<soap:Envelope>", size=12, color=BLUE, bold=True, anchor="start"))
    f.append(text(ex + ew - 20, ey + 24, "Простір імен: http://schemas.xmlsoap.org/soap/envelope/", size=10, color=MUTED, anchor="end"))

    # Внутрішній блок 1: Header (необов'язковий)
    hx, hy, hw, hh = 65, 85, 710, 115
    f.append(rect(hx, hy, hw, hh, fill="#fdfbf7", stroke=AMBER, sw=1.6, rx=8))
    f.append(text(hx + 15, hy + 22, "<soap:Header> (службові метадані, безпека, маршрутизація)", size=11.5, color=AMBER, bold=True, anchor="start"))

    # Елементи заголовка
    h_box1_x, h_box1_w = 80, 210
    h_box2_x, h_box2_w = 310, 220
    h_box3_x, h_box3_w = 550, 205
    box_h, box_y = 60, hy + 38

    f.append(rect(h_box1_x, box_y, h_box1_w, box_h, fill=BG, stroke=LINE, sw=1.1, rx=5))
    f.append(text(h_box1_x + h_box1_w / 2, box_y + 20, "<wsse:Security>", size=10.5, color=INK, bold=True))
    f.append(text(h_box1_x + h_box1_w / 2, box_y + 37, "Токен аутентифікації, підпис", size=9.5, color=MUTED))
    f.append(text(h_box1_x + h_box1_w / 2, box_y + 52, "mustUnderstand=\"1\"", size=9.5, color=RED, bold=True))

    f.append(rect(h_box2_x, box_y, h_box2_w, box_h, fill=BG, stroke=LINE, sw=1.1, rx=5))
    f.append(text(h_box2_x + h_box2_w / 2, box_y + 20, "<wsa:Action>", size=10.5, color=INK, bold=True))
    f.append(text(h_box2_x + h_box2_w / 2, box_y + 37, "Маршрутизація адресата", size=9.5, color=MUTED))
    f.append(text(h_box2_x + h_box2_w / 2, box_y + 52, "WS-Addressing URI", size=9.5, color=MUTED))

    f.append(rect(h_box3_x, box_y, h_box3_w, box_h, fill=BG, stroke=LINE, sw=1.1, rx=5))
    f.append(text(h_box3_x + h_box3_w / 2, box_y + 20, "<wstx:Coordination>", size=10.5, color=INK, bold=True))
    f.append(text(h_box3_x + h_box3_w / 2, box_y + 37, "Контекст розподіленої", size=9.5, color=MUTED))
    f.append(text(h_box3_x + h_box3_w / 2, box_y + 52, "транзакції 2PC", size=9.5, color=MUTED))

    # Внутрішній блок 2: Body (обов'язковий)
    bx, by, bw, bh = 65, 215, 710, 155
    f.append(rect(bx, by, bw, bh, fill="#f6fbf7", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(bx + 15, by + 22, "<soap:Body> (корисне навантаження або звіт про помилку)", size=11.5, color=GREEN, bold=True, anchor="start"))

    # Варіант 1: Корисне навантаження
    b_left_x, b_left_w = 80, 335
    f.append(rect(b_left_x, by + 36, b_left_w, 100, fill=BG, stroke=LINE, sw=1.1, rx=5))
    f.append(text(b_left_x + b_left_w / 2, by + 56, "Звичайний виклик або відповідь", size=11, color=GREEN, bold=True))
    f.append(text(b_left_x + 15, by + 78, "<m:ProcessPayment>", size=10.5, color=INK, anchor="start"))
    f.append(text(b_left_x + 30, by + 96, "<m:account>42918</m:account>", size=10, color=MUTED, anchor="start"))
    f.append(text(b_left_x + 30, by + 114, "<m:amount>150.00</m:amount>", size=10, color=MUTED, anchor="start"))
    f.append(text(b_left_x + 15, by + 130, "</m:ProcessPayment>", size=10.5, color=INK, anchor="start"))

    # Варіант 2: Fault
    b_right_x, b_right_w = 435, 325
    f.append(rect(b_right_x, by + 36, b_right_w, 100, fill="#fffaf9", stroke=RED, sw=1.1, rx=5))
    f.append(text(b_right_x + b_right_w / 2, by + 56, "Виняткова ситуація (<soap:Fault>)", size=11, color=RED, bold=True))
    f.append(text(b_right_x + 15, by + 78, "<faultcode>soap:Client</faultcode>", size=10, color=INK, anchor="start"))
    f.append(text(b_right_x + 15, by + 96, "<faultstring>Некоректний рахунок</faultstring>", size=10, color=INK, anchor="start"))
    f.append(text(b_right_x + 15, by + 114, "<detail><err:Code>ERR_402</err:Code></detail>", size=9.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, ey + eh + 20, "Обов'язковий конверт містить опційний заголовок метаданих та обов'язкове тіло виклику чи помилки", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "soap-envelope-structure.svg"), W, H, *f)


# ── 2. Шість рівнів WSDL ─────────────────────────────────────────────────────
def fig_wsdl_layers():
    W, H = 840, 440
    f = [text(W / 2, 28, "Шість рівнів специфікації WSDL 1.1", size=15, bold=True)]

    # Ліва колонка — абстрактний опис, права колонка — конкретне прив'язування
    lx, rx, bw, bh = 50, 450, 340, 52
    ys = [60, 125, 190, 255, 320, 385]

    layers = [
        ("<types>", "XSD-схеми: визначення типів даних і структур (елементи, поля)", GREEN, 0),
        ("<message>", "Логічні повідомлення: вхідні й вихідні параметри операцій", GREEN, 1),
        ("<portType>", "Абстрактний інтерфейс: набір операцій (Request-Response, One-Way)", GREEN, 2),
        ("<binding>", "Конкретний протокол: SOAP 1.1/1.2, стиль Document/Wrapped, транспорт HTTP", BLUE, 3),
        ("<port>", "Мережева адреса: фізична точка підключення (URL ендпоінта)", BLUE, 4),
        ("<service>", "Служба: логічне об'єднання споріднених портів у єдиний сервіс", BLUE, 5),
    ]

    for tag, desc, col, idx in layers:
        x = lx if idx < 3 else rx
        y = ys[idx if idx < 3 else idx - 3]
        f.append(rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=7))
        f.append(text(x + 14, y + 20, tag, size=12, color=col, bold=True, anchor="start"))
        f.append(text(x + 14, y + 38, desc, size=9.5, color=INK, anchor="start"))

    # Позначки груп
    f.append(text(lx + bw / 2, 45, "АБСТРАКТНИЙ РІВЕНЬ (ЩО робить сервіс)", size=11, color=GREEN, bold=True))
    f.append(text(rx + bw / 2, 45, "КОНКРЕТНИЙ РІВЕНЬ (ЯК і ДЕ викликати)", size=11, color=BLUE, bold=True))

    # Стрілки залежностей
    f.append(arrow(lx + bw / 2, ys[0] + bh, lx + bw / 2, ys[1] - 2, color=GRAY, sw=1.5))
    f.append(arrow(lx + bw / 2, ys[1] + bh, lx + bw / 2, ys[2] - 2, color=GRAY, sw=1.5))
    f.append(arrow(lx + bw, ys[2] + bh / 2, rx, ys[0] + bh / 2, color=PURPLE, sw=1.6))
    f.append(text((lx + bw + rx) / 2, (ys[2] + ys[0]) / 2 + 10, "реалізує", size=10, color=PURPLE, italic=True))
    f.append(arrow(rx + bw / 2, ys[0] + bh, rx + bw / 2, ys[1] - 2, color=GRAY, sw=1.5))
    f.append(arrow(rx + bw / 2, ys[1] + bh, rx + bw / 2, ys[2] - 2, color=GRAY, sw=1.5))

    # Підсумок унизу
    f.append(rect(lx, 260, bw, 80, fill="#fdfbf7", stroke=AMBER, sw=1.2, rx=6))
    f.append(text(lx + 12, 280, "Генерація коду (WSDL2Java / svcutil):", size=10.5, color=AMBER, bold=True, anchor="start"))
    f.append(text(lx + 12, 298, "• Клієнтський стаб (Stub/Proxy) генерується автоматично", size=9.5, color=INK, anchor="start"))
    f.append(text(lx + 12, 316, "• Сувора статична типізація під час компіляції", size=9.5, color=INK, anchor="start"))
    f.append(text(lx + 12, 334, "• Не потребує ручного парсингу XML", size=9.5, color=INK, anchor="start"))

    f.append(rect(rx, 260, bw, 80, fill="#f6fbf7", stroke=GREEN, sw=1.2, rx=6))
    f.append(text(rx + 12, 280, "WS-I Basic Profile 1.1:", size=10.5, color=GREEN, bold=True, anchor="start"))
    f.append(text(rx + 12, 298, "• Стандарт інтероперабельності між різними платформами", size=9.5, color=INK, anchor="start"))
    f.append(text(rx + 12, 316, "• Забороняє RPC/Encoded (секція 5 SOAP)", size=9.5, color=INK, anchor="start"))
    f.append(text(rx + 12, 334, "• Вимагає стиль Document/Literal Wrapped", size=9.5, color=INK, anchor="start"))

    f.append(text(W / 2, 420, "WSDL відділяє абстрактні типи й методи від деталей транспорту, протоколу та фізичної адреси", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "wsdl-layers.svg"), W, H, *f)


# ── 3. Стилі зв'язування WSDL ────────────────────────────────────────────────
def fig_doc_literal_wrapped():
    W, H = 860, 390
    f = [text(W / 2, 28, "Порівняння стилів повідомлень SOAP: RPC/Encoded vs Document/Literal Wrapped", size=15, bold=True)]

    col_w = 370
    col1_x = 45
    col2_x = 445
    box_h = 290
    top_y = 55

    # Ліва колонка: RPC/Encoded
    f.append(rect(col1_x, top_y, col_w, box_h, fill="#fffaf9", stroke=RED, sw=1.6, rx=8))
    f.append(text(col1_x + col_w / 2, top_y + 24, "RPC / Encoded (Застарілий підхід)", size=12.5, color=RED, bold=True))
    f.append(text(col1_x + 15, top_y + 48, "Особливості серіалізації:", size=10.5, color=INK, bold=True, anchor="start"))
    f.append(text(col1_x + 15, top_y + 66, "• Типи кодуються за секцією 5 SOAP (xsi:type у кожному вузлі)", size=9.5, color=MUTED, anchor="start"))
    f.append(text(col1_x + 15, top_y + 82, "• Тіло не можна валідувати стандартною XSD-схемою", size=9.5, color=MUTED, anchor="start"))
    f.append(text(col1_x + 15, top_y + 98, "• Платформи (.NET, Java Axis) кодували графі не сумісно", size=9.5, color=MUTED, anchor="start"))

    # Приклад коду RPC/Encoded
    code1_y = top_y + 115
    f.append(rect(col1_x + 12, code1_y, col_w - 24, 130, fill=BG, stroke=LINE, sw=1, rx=5))
    f.append(text(col1_x + 20, code1_y + 20, "<soap:Body>", size=10, color=BLUE, anchor="start"))
    f.append(text(col1_x + 30, code1_y + 38, "<m:GetBalance soap:encodingStyle=\"...\">", size=9.5, color=INK, anchor="start"))
    f.append(text(col1_x + 45, code1_y + 56, "<accNumber xsi:type=\"xsd:string\">4291</accNumber>", size=9.5, color=RED, anchor="start"))
    f.append(text(col1_x + 45, code1_y + 74, "<currency xsi:type=\"xsd:string\">USD</currency>", size=9.5, color=RED, anchor="start"))
    f.append(text(col1_x + 30, code1_y + 92, "</m:GetBalance>", size=9.5, color=INK, anchor="start"))
    f.append(text(col1_x + 20, code1_y + 110, "</soap:Body>", size=10, color=BLUE, anchor="start"))
    f.append(text(col1_x + col_w / 2, top_y + 270, "✖ Заборонено стандартом WS-I Basic Profile 1.1", size=10, color=RED, bold=True))

    # Права колонка: Document/Literal Wrapped
    f.append(rect(col2_x, top_y, col_w, box_h, fill="#f6fbf7", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(col2_x + col_w / 2, top_y + 24, "Document / Literal Wrapped (Галузевий канон)", size=12.5, color=GREEN, bold=True))
    f.append(text(col2_x + 15, top_y + 48, "Особливості серіалізації:", size=10.5, color=INK, bold=True, anchor="start"))
    f.append(text(col2_x + 15, top_y + 66, "• Тіло — це повноцінний XML-документ, валідований XSD", size=9.5, color=MUTED, anchor="start"))
    f.append(text(col2_x + 15, top_y + 82, "• Обгортка з назвою методу (<GetBalance>) спрощує диспетчеризацію", size=9.5, color=MUTED, anchor="start"))
    f.append(text(col2_x + 15, top_y + 98, "• Повна сумісність між усіма мовами програмування", size=9.5, color=MUTED, anchor="start"))

    # Приклад коду Doc/Lit Wrapped
    f.append(rect(col2_x + 12, code1_y, col_w - 24, 130, fill=BG, stroke=LINE, sw=1, rx=5))
    f.append(text(col2_x + 20, code1_y + 20, "<soap:Body>", size=10, color=BLUE, anchor="start"))
    f.append(text(col2_x + 30, code1_y + 38, "<m:GetBalance>  <!-- Обгортка операції -->", size=9.5, color=GREEN, bold=True, anchor="start"))
    f.append(text(col2_x + 45, code1_y + 56, "<m:accNumber>4291</m:accNumber>", size=9.5, color=INK, anchor="start"))
    f.append(text(col2_x + 45, code1_y + 74, "<m:currency>USD</m:currency>", size=9.5, color=INK, anchor="start"))
    f.append(text(col2_x + 30, code1_y + 92, "</m:GetBalance>", size=9.5, color=GREEN, bold=True, anchor="start"))
    f.append(text(col2_x + 20, code1_y + 110, "</soap:Body>", size=10, color=BLUE, anchor="start"))
    f.append(text(col2_x + col_w / 2, top_y + 270, "✓ Стандарт де-факто для всіх корпоративних SOAP-систем", size=10, color=GREEN, bold=True))

    f.append(text(W / 2, top_y + box_h + 24, "Document/Literal Wrapped поєднав сувору схему XSD із можливістю маршрутизації методу за кореневим тегом", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "doc-literal-wrapped.svg"), W, H, *f)


# ── 4. Безпека на рівні транспорту проти безпеки на рівні повідомлення ─────────
def fig_message_level_security():
    W, H = 860, 360
    f = [text(W / 2, 28, "Безпека транспорту (TLS) проти безпеки повідомлення (WS-Security)", size=15, bold=True)]

    # Секція 1: TLS / HTTPS (Hop-by-Hop)
    t_y = 55
    f.append(rect(40, t_y, 780, 115, fill="#fffaf9", stroke=RED, sw=1.4, rx=7))
    f.append(text(55, t_y + 22, "Рівень транспорту (TLS/HTTPS) — захист від вузла до вузла (Hop-by-Hop)", size=11.5, color=RED, bold=True, anchor="start"))

    # Клієнт -> Шлюз/ESB -> Кінцевий бекенд
    bx1, bx2, bx3 = 80, 370, 670
    bw_node = 110
    bh_node = 48
    node_y = t_y + 38

    f.append(rect(bx1, node_y, bw_node, bh_node, fill=BG, stroke=LINE, sw=1.2, rx=5))
    f.append(text(bx1 + bw_node / 2, node_y + 28, "Клієнт", size=11, bold=True))

    f.append(rect(bx2, node_y, bw_node + 20, bh_node, fill="#fdecea", stroke=RED, sw=1.4, rx=5))
    f.append(text(bx2 + (bw_node + 20) / 2, node_y + 20, "Шлюз / ESB", size=11, color=RED, bold=True))
    f.append(text(bx2 + (bw_node + 20) / 2, node_y + 36, "Розшифровує дані", size=9.5, color=RED))

    f.append(rect(bx3, node_y, bw_node, bh_node, fill=BG, stroke=LINE, sw=1.2, rx=5))
    f.append(text(bx3 + bw_node / 2, node_y + 28, "Бекенд", size=11, bold=True))

    # Стрілки з TLS
    f.append(arrow(bx1 + bw_node, node_y + bh_node / 2, bx2, node_y + bh_node / 2, color=GREEN, sw=1.6))
    f.append(text((bx1 + bw_node + bx2) / 2, node_y + bh_node / 2 - 8, "TLS плече 1", size=9.5, color=GREEN, bold=True))

    f.append(arrow(bx2 + bw_node + 20, node_y + bh_node / 2, bx3, node_y + bh_node / 2, color=GREEN, sw=1.6))
    f.append(text((bx2 + bw_node + 20 + bx3) / 2, node_y + bh_node / 2 - 8, "TLS плече 2", size=9.5, color=GREEN, bold=True))

    f.append(text(W / 2, t_y + 102, "⚠ Посередник (ESB, проксі, черга MQ) бачить незашифровані банківські реквізити та паролі у відкритому вигляді", size=10, color=RED))

    # Секція 2: WS-Security (End-to-End)
    w_y = 190
    f.append(rect(40, w_y, 780, 130, fill="#f6fbf7", stroke=GREEN, sw=1.4, rx=7))
    f.append(text(55, w_y + 22, "Рівень повідомлення (WS-Security) — наскрізний захист (End-to-End)", size=11.5, color=GREEN, bold=True, anchor="start"))

    node2_y = w_y + 38
    f.append(rect(bx1, node2_y, bw_node, bh_node, fill=BG, stroke=LINE, sw=1.2, rx=5))
    f.append(text(bx1 + bw_node / 2, node2_y + 20, "Клієнт", size=11, bold=True))
    f.append(text(bx1 + bw_node / 2, node2_y + 36, "Шифрує / Підписує", size=9.5, color=GREEN))

    f.append(rect(bx2, node2_y, bw_node + 20, bh_node, fill=BG, stroke=MUTED, sw=1.2, rx=5))
    f.append(text(bx2 + (bw_node + 20) / 2, node2_y + 20, "Шлюз / ESB", size=11, color=MUTED, bold=True))
    f.append(text(bx2 + (bw_node + 20) / 2, node2_y + 36, "Маршрутизує шифр", size=9.5, color=MUTED))

    f.append(rect(bx3, node2_y, bw_node, bh_node, fill=BG, stroke=LINE, sw=1.2, rx=5))
    f.append(text(bx3 + bw_node / 2, node2_y + 20, "Бекенд", size=11, bold=True))
    f.append(text(bx3 + bw_node / 2, node2_y + 36, "Перевіряє підпис", size=9.5, color=GREEN))

    # Стрілки
    f.append(arrow(bx1 + bw_node, node2_y + bh_node / 2, bx2, node2_y + bh_node / 2, color=BLUE, sw=1.6))
    f.append(arrow(bx2 + bw_node + 20, node2_y + bh_node / 2, bx3, node2_y + bh_node / 2, color=BLUE, sw=1.6))

    # Наскрізна дуга підпису/шифрування
    f.append(line(bx1 + bw_node / 2, node2_y + bh_node + 4, bx3 + bw_node / 2, node2_y + bh_node + 4, color=GREEN, sw=1.8, dash="4,4"))
    f.append(text(W / 2, node2_y + bh_node + 20, "Цифровий підпис (XML-Signature) і шифрування (XML-Encryption) зберігаються через черги та шлюзи", size=9.5, color=GREEN, bold=True))

    f.append(text(W / 2, 340, "WS-Security забезпечує неподільність і конфіденційність транзакцій незалежно від кількості проміжних брокерів", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "message-level-security.svg"), W, H, *f)


# ── 5. Конвеєр обробки SOAP-запиту та генерація Fault ────────────────────────
def fig_soap_fault_flow():
    W, H = 860, 420
    f = [text(W / 2, 28, "Конвеєр обробки SOAP-запиту: перевірка заголовків, схеми та генерація Fault", size=15, bold=True)]

    # Етапи по горизонталі
    step_w = 145
    step_h = 60
    xs = [40, 205, 370, 535, 700]
    top_y = 65

    steps = [
        ("1. HTTP POST", ["Перевірка Content-Type", "та SOAPAction"], INK),
        ("2. Заголовки", ["Аналіз mustUnderstand", "усіх блоків Header"], AMBER),
        ("3. Валідація", ["Перевірка Body за", "XSD-схемою WSDL"], BLUE),
        ("4. Виконання", ["Виклик сервісу та", "бізнес-правил"], PURPLE),
        ("5. Результат", ["200 OK з успішним", "<soap:Body>"], GREEN),
    ]

    for (title, lines, col), x in zip(steps, xs):
        f.append(rect(x, top_y, step_w, step_h, fill=BG, stroke=col, sw=1.6, rx=6))
        f.append(text(x + step_w / 2, top_y + 18, title, size=11, color=col, bold=True))
        f.append(text(x + step_w / 2, top_y + 35, lines[0], size=9.5, color=MUTED))
        f.append(text(x + step_w / 2, top_y + 49, lines[1], size=9.5, color=MUTED))

    # Стрілки прямого потоку (зелені/сині)
    for i in range(4):
        f.append(arrow(xs[i] + step_w, top_y + step_h / 2, xs[i+1], top_y + step_h / 2, color=GREEN, sw=1.6))

    # Блоки відхилень (Fault) унизу
    fault_y = 195
    fault_h = 130
    fault_w = 175

    # Fault 1: MustUnderstand
    f1_x = 190
    f.append(rect(f1_x, fault_y, fault_w, fault_h, fill="#fffaf9", stroke=RED, sw=1.4, rx=6))
    f.append(text(f1_x + fault_w / 2, fault_y + 20, "soap:MustUnderstand", size=11, color=RED, bold=True))
    f.append(text(f1_x + 10, fault_y + 40, "Невідомий заголовок з", size=9.5, color=INK, anchor="start"))
    f.append(text(f1_x + 10, fault_y + 55, "mustUnderstand=\"1\"", size=9.5, color=RED, bold=True, anchor="start"))
    f.append(text(f1_x + 10, fault_y + 75, "Сервер зобов'язаний", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f1_x + 10, fault_y + 90, "перервати обробку", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f1_x + 10, fault_y + 112, "HTTP 500 (1.1) / 500 (1.2)", size=9.5, color=RED, bold=True, anchor="start"))

    # Fault 2: Schema / Client Fault
    f2_x = 380
    f.append(rect(f2_x, fault_y, fault_w, fault_h, fill="#fffaf9", stroke=RED, sw=1.4, rx=6))
    f.append(text(f2_x + fault_w / 2, fault_y + 20, "soap:Client / Sender", size=11, color=RED, bold=True))
    f.append(text(f2_x + 10, fault_y + 40, "Помилка XSD-схеми або", size=9.5, color=INK, anchor="start"))
    f.append(text(f2_x + 10, fault_y + 55, "некоректні аргументи", size=9.5, color=INK, anchor="start"))
    f.append(text(f2_x + 10, fault_y + 75, "Клієнт надіслав хибні", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f2_x + 10, fault_y + 90, "дані запиту", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f2_x + 10, fault_y + 112, "HTTP 500 (1.1) / 400 (1.2)", size=9.5, color=RED, bold=True, anchor="start"))

    # Fault 3: Server / Receiver Fault
    f3_x = 570
    f.append(rect(f3_x, fault_y, fault_w, fault_h, fill="#fffaf9", stroke=RED, sw=1.4, rx=6))
    f.append(text(f3_x + fault_w / 2, fault_y + 20, "soap:Server / Receiver", size=11, color=RED, bold=True))
    f.append(text(f3_x + 10, fault_y + 40, "Внутрішній збій сервісу,", size=9.5, color=INK, anchor="start"))
    f.append(text(f3_x + 10, fault_y + 55, "бази даних чи мережі", size=9.5, color=INK, anchor="start"))
    f.append(text(f3_x + 10, fault_y + 75, "Помилка на стороні", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f3_x + 10, fault_y + 90, "сервера обробки", size=9.5, color=MUTED, anchor="start"))
    f.append(text(f3_x + 10, fault_y + 112, "HTTP 500 (1.1) / 500 (1.2)", size=9.5, color=RED, bold=True, anchor="start"))

    # Стрілки помилок від кроків до блоків Fault
    f.append(arrow(xs[1] + step_w / 2, top_y + step_h, f1_x + fault_w / 2, fault_y - 2, color=RED, sw=1.5))
    f.append(arrow(xs[2] + step_w / 2, top_y + step_h, f2_x + fault_w / 2, fault_y - 2, color=RED, sw=1.5))
    f.append(arrow(xs[3] + step_w / 2, top_y + step_h, f3_x + fault_w / 2, fault_y - 2, color=RED, sw=1.5))

    # Спільний блок відповіді Fault
    f.append(rect(190, 345, 555, 40, fill="#fdf2f0", stroke=RED, sw=1.2, rx=5))
    f.append(text(190 + 555 / 2, 368, "Формування уніфікованого XML <soap:Fault> з кодом, причиною та блоком <detail>", size=10, color=RED, bold=True))

    f.append(arrow(f1_x + fault_w / 2, fault_y + fault_h, f1_x + fault_w / 2, 343, color=RED, sw=1.2))
    f.append(arrow(f2_x + fault_w / 2, fault_y + fault_h, f2_x + fault_w / 2, 343, color=RED, sw=1.2))
    f.append(arrow(f3_x + fault_w / 2, fault_y + fault_h, f3_x + fault_w / 2, 343, color=RED, sw=1.2))

    f.append(text(W / 2, 405, "Будь-який збій на шляху обробки формує суворий стандартизований конверт Fault із деталями помилки", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "soap-fault-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_soap_envelope_structure()
    fig_wsdl_layers()
    fig_doc_literal_wrapped()
    fig_message_level_security()
    fig_soap_fault_flow()
    print("All SOAP figures generated successfully in", IMG)
