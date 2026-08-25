# -*- coding: utf-8 -*-
"""Фігури до теми «ENUM: телефонний номер як ім'я в DNS»."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
GREEN_BG = "#eafaf1"
GRAY_BG = "#f8f9fa"


def box(cx, cy, s, size=13, fill=FILL, stroke=LINE, bold=False):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, stroke=stroke, bold=bold)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ієрархія доменного дерева e164.arpa та алгоритм трансформації номера
# ─────────────────────────────────────────────────────────────────────────────
def fig_enum_dns_hierarchy():
    W, H = 1000, 700
    f = []

    # Верхня панель: перетворення E.164 у доменне ім'я
    f.append(rect(30, 20, 940, 150, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=10))
    f.append(text(50, 48, "Алгоритм перетворення телефонного номера E.164 в доменне ім'я ENUM",
                  size=14, color=INK, anchor="start", bold=True))

    s1, s1w, s1h = box(150, 105, "Номер E.164:\n+380 44 123 4567", size=12, fill="#ffffff", stroke="#2457d6")
    s2, s2w, s2h = box(380, 105, "Лише цифри:\n380441234567", size=12, fill="#ffffff")
    s3, s3w, s3h = box(610, 105, "Реверс і крапки:\n7.6.5.4.3.2.1.4.4.0.8.3", size=12, fill="#ffffff")
    s4, s4w, s4h = box(850, 105, "Суфікс .e164.arpa:\n7.6...4.4.0.8.3.e164.arpa", size=12, fill="#ffffff", stroke="#27ae60")

    f += [s1, s2, s3, s4]
    f.append(arrow(150 + s1w, 105, 380 - s2w, 105))
    f.append(arrow(380 + s2w, 105, 610 - s3w, 105))
    f.append(arrow(610 + s3w, 105, 850 - s4w, 105))

    f.append(text(265, 90, "Очищення", size=11, color=MUTED))
    f.append(text(495, 90, "Інверсія", size=11, color=MUTED))
    f.append(text(730, 90, "Суфікс", size=11, color=MUTED))

    # Нижня панель: дерево DNS-делегації
    f.append(rect(30, 190, 940, 480, fill=GRAY_BG, stroke="#d1d5db", sw=1.2, rx=10))
    f.append(text(50, 220, "Дерево делегування зон у DNS-ієрархії e164.arpa",
                  size=14, color=INK, anchor="start", bold=True))

    # Вузли дерева
    root_node, rw, rh = box(500, 260, "Коренева зона DNS (.)\nIANA / ICANN", size=12, fill="#ffffff", bold=True)
    arpa_node, aw, ah = box(500, 335, "Інфраструктурна зона: arpa\nIAB / IETF", size=12, fill="#ffffff")
    enum_node, ew, eh = box(500, 410, "Зона ENUM: e164.arpa\nДелегування ITU-T / RIPE NCC (Tier 0)", size=12, fill=GREEN_BG, stroke="#27ae60", bold=True)

    # Національні зони (Tier 1)
    ukr_node, uw, uh = box(280, 505, "8.3.e164.arpa (+380 Україна)\nНаціональний регулятор / Tier 1", size=12, fill="#ffffff", stroke="#2457d6")
    other_node, ow, oh = box(720, 505, "1.e164.arpa (+1 Півн. Америка)\nNANPA / Neustar", size=12, fill="#ffffff")

    # Зона оператора / абонента (Tier 2)
    sub_node, sw, sh = box(280, 615, "7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa\nNAPTR-записи абонента (Tier 2 / SIP-оператор)", size=11, fill="#ffffff", stroke="#c0392b")

    f += [root_node, arpa_node, enum_node, ukr_node, other_node, sub_node]

    # Зв'язки між рівнями
    f.append(arrow(500, 260 + rh, 500, 335 - ah))
    f.append(arrow(500, 335 + ah, 500, 410 - eh))
    f.append(arrow(410, 410 + eh, 280, 505 - uh))
    f.append(arrow(590, 410 + eh, 720, 505 - oh))
    f.append(arrow(280, 505 + uh, 280, 615 - sh))

    f.append(text(330, 445, "Код країни 380", size=11, color=MUTED))
    f.append(text(670, 445, "Код країни 1", size=11, color=MUTED))
    f.append(text(350, 560, "Номер абонента", size=11, color=MUTED))

    render(os.path.join(OUT, "enum-dns-hierarchy.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Послідовність маршрутизації виклику через ENUM (SIP Softswitch <-> DNS)
# ─────────────────────────────────────────────────────────────────────────────
def fig_enum_routing_flow():
    W, H = 1000, 540
    f = []

    # Учасники процесу (стовпчики)
    p_phone, pw, ph = box(120, 60, "Абонент A\nSIP-телефон / PBX", size=13, fill=SOFT, stroke="#2457d6", bold=True)
    p_switch, sw, sh = box(380, 60, "Softswitch / SBC\nВихідний SIP-проксі", size=13, fill=WARM, stroke="#d97706", bold=True)
    p_dns, dw, dh = box(640, 60, "DNS Резолвер\nЗона e164.arpa", size=13, fill=GREEN_BG, stroke="#27ae60", bold=True)
    p_dest, bw, bh = box(880, 60, "Абонент B / Домен\nsip.operator.ua", size=13, fill=SOFT, stroke="#2457d6", bold=True)

    f += [p_phone, p_switch, p_dns, p_dest]

    # Вертикальні лінії життя (життя протоколу)
    f.append(line(120, 95, 120, 510, color="#9ca3af", sw=1.5, dash="4,4"))
    f.append(line(380, 95, 380, 510, color="#9ca3af", sw=1.5, dash="4,4"))
    f.append(line(640, 95, 640, 510, color="#9ca3af", sw=1.5, dash="4,4"))
    f.append(line(880, 95, 880, 510, color="#9ca3af", sw=1.5, dash="4,4"))

    # Крок 1: Набір номера
    f.append(arrow(120, 140, 380, 140, color="#2457d6", sw=1.8))
    f.append(text(250, 130, "1. INVITE sip:+380441234567@proxy", size=11, bold=True))

    # Крок 2: ENUM трансляція та DNS NAPTR запит
    f.append(arrow(380, 200, 640, 200, color="#27ae60", sw=1.8))
    f.append(text(510, 185, "2. DNS Query: NAPTR", size=11, bold=True))
    f.append(text(510, 215, "7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa", size=10, color=MUTED))

    # Крок 3: Відповідь DNS
    f.append(arrow(640, 270, 380, 270, color="#27ae60", sw=1.8))
    f.append(text(510, 255, "3. DNS Response: NAPTR (E2U+sip)", size=11, bold=True))
    f.append(text(510, 285, "!^.*$!sip:user@operator.ua!", size=10, color=MUTED))

    # Крок 4: Локальне перетворення URI
    c_box, cw, ch = box(380, 340, "4. Підстановка Regex:\n+380441234567 → sip:user@operator.ua", size=11, fill="#ffffff", stroke="#d97706")
    f.append(c_box)

    # Крок 5: Прямий SIP INVITE через IP-мережу
    f.append(arrow(380, 410, 880, 410, color="#2457d6", sw=2.0))
    f.append(text(630, 395, "5. INVITE sip:user@operator.ua (прямий IP-маршрут)", size=12, bold=True, color="#2457d6"))

    # Крок 6: Відповідь 200 OK
    f.append(arrow(880, 470, 380, 470, color="#2457d6", sw=1.5))
    f.append(arrow(380, 470, 120, 470, color="#2457d6", sw=1.5))
    f.append(text(500, 460, "6. 200 OK (Сеанс встановлено повз PSTN)", size=11, color=MUTED))

    render(os.path.join(OUT, "enum-routing-flow.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Анатомія ресурсного запису NAPTR у DNS
# ─────────────────────────────────────────────────────────────────────────────
def fig_naptr_record_structure():
    W, H = 1000, 520
    f = []

    # Верхній заголовок
    f.append(rect(30, 20, 940, 80, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(500, 48, "Анатомія ресурсного запису DNS NAPTR (RFC 3403 / RFC 6116)",
                  size=15, color=INK, anchor="middle", bold=True))
    f.append(text(500, 78, "7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa.  IN  NAPTR  100  10  \"u\"  \"E2U+sip\"  \"!^\\+38044(.*)$!sip:\\\\1@tel.example.ua!i\"  .",
                  size=12, color="#2457d6", anchor="middle"))

    # Блоки полів NAPTR
    # Поля: Order, Preference, Flags, Services, Regexp, Replacement
    b1, b1w, b1h = box(105, 170, "ORDER\n100", size=13, fill="#ffffff", stroke="#2457d6", bold=True)
    b2, b2w, b2h = box(235, 170, "PREFERENCE\n10", size=13, fill="#ffffff", stroke="#2457d6", bold=True)
    b3, b3w, b3h = box(365, 170, "FLAGS\n\"u\"", size=13, fill="#ffffff", stroke="#27ae60", bold=True)
    b4, b4w, b4h = box(515, 170, "SERVICES\n\"E2U+sip\"", size=13, fill="#ffffff", stroke="#d97706", bold=True)
    b5, b5w, b5h = box(745, 170, "REGEXP\n\"!^\\+38044(.*)$!sip:\\1@tel.example.ua!i\"", size=11, fill="#ffffff", stroke="#c0392b", bold=True)
    b6, b6w, b6h = box(930, 170, "REPLACEMENT\n\".\"", size=12, fill="#ffffff", stroke=LINE, bold=True)

    f += [b1, b2, b3, b4, b5, b6]

    # Пояснювальні картки для кожного поля
    p1, p1w, p1h = box(170, 310, "Порядок обробки (16 біт):\nМенше число виконується першим.\nРізні order обробляються суворо\nпо черзі, без паралелізму.", size=11, fill=GRAY_BG)
    p2, p2w, p2h = box(170, 440, "Пріоритет (16 біт):\nВага серед записів з однаковим order.\nДозволяє балансувати вибір\nміж кількома сервісами.", size=11, fill=GRAY_BG)

    p3, p3w, p3h = box(420, 310, "Прапорець переходу:\n\"u\" — термінальне правило (кінцевий URI);\n\"s\" — далі шукати SRV-запис;\n\"a\" — шукати A/AAAA запис;\n\"\" (порожній) — наступний NAPTR.", size=11, fill=GRAY_BG)
    p4, p4w, p4h = box(420, 440, "Специфікація послуги:\nПрефікс E2U (E.164 to URI) +\nідентифікатор протоколу (sip, email,\nvoice:sip, h323, tel, pres).", size=11, fill=GRAY_BG)

    p5, p5w, p5h = box(780, 310, "Регулярний вираз підстановки:\nФормат Sed: !шаблон!заміна!прапорці.\nВирізає вхідний номер E.164 і вставляє\nйого в цільовий URI протоколу.", size=11, fill=GRAY_BG)
    p6, p6w, p6h = box(780, 440, "Поле заміни (FQDN):\nДля прапорця \"u\" завжди містить \".\"\nЯкщо прапорець не термінальний,\nвказує наступне доменне ім'я для DDDS.", size=11, fill=GRAY_BG)

    f += [p1, p2, p3, p4, p5, p6]

    # Стрілки від блоків до карток
    f.append(line(105, 200, 105, 250, color=MUTED, sw=1.2))
    f.append(line(105, 250, 170, 250, color=MUTED, sw=1.2))
    f.append(arrow(170, 250, 170, 270, color=MUTED, sw=1.2))

    f.append(line(235, 200, 235, 380, color=MUTED, sw=1.2))
    f.append(line(235, 380, 170, 380, color=MUTED, sw=1.2))
    f.append(arrow(170, 380, 170, 395, color=MUTED, sw=1.2))

    f.append(arrow(365, 200, 365, 260, color=MUTED, sw=1.2))
    f.append(line(515, 200, 515, 380, color=MUTED, sw=1.2))
    f.append(line(515, 380, 420, 380, color=MUTED, sw=1.2))
    f.append(arrow(420, 380, 420, 395, color=MUTED, sw=1.2))

    f.append(arrow(745, 200, 745, 260, color=MUTED, sw=1.2))
    f.append(line(930, 200, 930, 380, color=MUTED, sw=1.2))
    f.append(line(930, 380, 780, 380, color=MUTED, sw=1.2))
    f.append(arrow(780, 380, 780, 395, color=MUTED, sw=1.2))

    render(os.path.join(OUT, "naptr-record-structure.svg"), W, H, *f)


if __name__ == "__main__":
    fig_enum_dns_hierarchy()
    fig_enum_routing_flow()
    fig_naptr_record_structure()
    print("Фігури успішно згенеровано.")
