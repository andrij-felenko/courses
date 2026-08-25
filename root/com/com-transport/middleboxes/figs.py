# -*- coding: utf-8 -*-
"""Фігури до теми «Проміжні коробки (Middlebox): фаєрволи, проксі, кеші та транслятори».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Наскрізний принцип проти реальності Middlebox ─────────────────────────
def fig_middlebox_architecture():
    """Порівняння класичної наскрізної моделі (End-to-End) та сучасної мережі,
    насиченої проміжними пристроями (L3/L4/L7 Middleboxes)."""
    W, H = 840, 500
    f = [text(W / 2, 26, "Наскрізний принцип (End-to-End) проти реальності Middlebox", size=15, bold=True)]

    # ── Блок 1: Класична модель (End-to-End) ──
    f.append(rect(30, 48, 780, 155, fill="#f8fafc", stroke=FIELD, sw=1.4))
    f.append(text(50, 72, "Класична наскрізна архітектура (RFC 1958): «розумні кінці, проста мережа»", size=12, bold=True, color=FIELD, anchor="start"))

    # Клієнт L7..L1
    f.append(fitbox(45, 88, 120, 95, "Клієнт (Host A)\n[L7] Застосунок\n[L4] TCP/UDP стан\n[L3] IP адресація", size=10, fill="#ffffff", stroke=NEG, sw=1.2))

    # Роутери ядра L3
    f.append(fitbox(235, 105, 150, 62, "Маршрутизатор R1\nТільки L3 (IP routing)\nБез стану сесій", size=10, fill="#ffffff", stroke=LINE, sw=1.0))
    f.append(fitbox(455, 105, 150, 62, "Маршрутизатор R2\nТільки L3 (IP routing)\nБез стану сесій", size=10, fill="#ffffff", stroke=LINE, sw=1.0))

    # Сервер L7..L1
    f.append(fitbox(675, 88, 120, 95, "Сервер (Host B)\n[L7] Застосунок\n[L4] TCP/UDP стан\n[L3] IP адресація", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Стрілки крізь ядро
    f.append(arrow(165, 136, 235, 136, color=MUTED, sw=1.5))
    f.append(arrow(385, 136, 455, 136, color=MUTED, sw=1.5))
    f.append(arrow(605, 136, 675, 136, color=MUTED, sw=1.5))
    f.append(text(420, 188, "Наскрізний семантичний зв'язок: транспортний стан тримають виключно хости A і B", size=10, italic=True, color=FIELD))

    # ── Блок 2: Реальність з Middleboxes ──
    f.append(rect(30, 220, 780, 260, fill="#fffaf9", stroke=POS, sw=1.4))
    f.append(text(50, 244, "Реальність Інтернету: проміжні пристрої (Middleboxes) розривають шари моделі OSI", size=12, bold=True, color=POS, anchor="start"))

    # Клієнт
    f.append(fitbox(45, 262, 105, 185, "Клієнт A\n192.168.1.10\n\nTCP SYN\n(Seq=1000,\nOpt=TFO,MPTCP)", size=9.5, fill="#ffffff", stroke=NEG, sw=1.2))

    # NAT / CGNAT (L3/L4)
    f.append(fitbox(170, 262, 125, 85, "NAT / CGNAT (L3/L4)\nЗміна IP та портів\nТаблиця трансляції\nТаймаути сесій", size=9, fill="#ffffff", stroke=POS, sw=1.1))
    f.append(fitbox(170, 355, 125, 92, "Stateful Firewall\nВідстеження 5-tuple\nTCP state machine\nДроп поза вікном", size=9, fill="#ffffff", stroke=POS, sw=1.1))

    # WAN Optimizer / TCP Proxy (L4)
    f.append(fitbox(325, 262, 160, 185, "WAN Optimizer / PEP (L4)\nTCP Split-Connection\n• Підміна ACK клієнту\n• Власний буфер TCP\n• Вирізання невідомих опцій\n• Clamping MSS", size=9.5, fill="#ffffff", stroke=POS, sw=1.2))

    # L7 DPI / Reverse Proxy
    f.append(fitbox(515, 262, 135, 185, "L7 Proxy / DPI / WAF\n• TLS MITM термінація\n• Інспекція корисного навантаження\n• Кешування контенту\n• Фільтрація за SNI/URL", size=9, fill="#ffffff", stroke=POS, sw=1.1))

    # Сервер
    f.append(fitbox(675, 262, 120, 185, "Сервер B\n203.0.113.80\n\nОтримує змінений\nпотік: інший IP,\nнові Seq/Ack,\nопції вирізано", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))

    # З'єднувальні стрілки
    f.append(arrow(150, 310, 170, 310, color=POS, sw=1.4))
    f.append(arrow(295, 310, 325, 310, color=POS, sw=1.4))
    f.append(arrow(485, 355, 515, 355, color=POS, sw=1.4))
    f.append(arrow(650, 355, 675, 355, color=POS, sw=1.4))

    f.append(text(420, 468, "Порушення прозорості: стан розподілено між 4 коробками; вихід однієї з ладу рве сесію", size=10, italic=True, color=POS))

    render(os.path.join(IMG, "middlebox-architecture-taxonomy.svg"), W, H, *f)


# ── 2. Механіка та збої костеніння протоколів (Ossification) ─────────────────
def fig_protocol_ossification():
    """Схема прояву костеніння протоколів (Protocol Ossification):
    блокування невідомих протоколів, вирізання TCP-опцій та розрив семантики ACK."""
    W, H = 840, 490
    f = [text(W / 2, 26, "Патології костеніння протоколів (Protocol Ossification)", size=15, bold=True)]

    # Сценарій 1: Блокування невідомого IP Protocol
    f.append(rect(30, 48, 780, 125, fill="#f8fafc", stroke=LINE, sw=1.2))
    f.append(text(45, 68, "Сценарій А: Блокування невідомих номерів IP-протоколів (SCTP, DCCP)", size=11, bold=True, color=INK, anchor="start"))
    f.append(fitbox(45, 80, 170, 78, "Хост-відправник\nIP Proto = 132 (SCTP)\nНовий надійний\nмультипотоковий транспорт", size=9.5, fill="#ffffff", stroke=NEG, sw=1.0))
    f.append(arrow(215, 119, 310, 119, color=NEG, sw=1.5))
    f.append(fitbox(310, 80, 220, 78, "Enterprise Firewall / ISP NAT\nПарсер: if (proto != 6 && proto != 17)\n→ DROP (Тихе скидання)\nНемає парсера L4 портів для SCTP", size=9, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(line(530, 119, 570, 119, color=POS, sw=1.5, dash="4,3"))
    f.append(text(590, 119, "✖ Пакет знищено", size=10, bold=True, color=POS, anchor="start"))
    f.append(fitbox(660, 80, 135, 78, "Хост-одержувач\nОчікує з'єднання\n(Таймаут 3000 мс,\nтрафік не дійшов)", size=9.5, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Сценарій 2: Вирізання невідомих TCP Options (MPTCP, TFO)
    f.append(rect(30, 185, 780, 135, fill="#f8fafc", stroke=LINE, sw=1.2))
    f.append(text(45, 205, "Сценарій Б: Вирізання невідомих TCP-опцій (MPTCP Subflow, Fast Open Cookie)", size=11, bold=True, color=INK, anchor="start"))
    f.append(fitbox(45, 218, 170, 88, "Клієнт (SYN + Opt 30)\nTCP Header (40 байт)\n• Option 30 (MPTCP)\n• Option 34 (TFO Cookie)\nРозмір заголовка = 10 слів", size=9, fill="#ffffff", stroke=NEG, sw=1.0))
    f.append(arrow(215, 262, 310, 262, color=NEG, sw=1.5))
    f.append(fitbox(310, 218, 220, 88, "Middlebox (Scrubber / Optimizer)\n• Не знає Kind=30 / Kind=34\n• Затирає опції нулями (NOP)\n• АБО зменшує Data Offset\n• АБО ламає TCP Checksum", size=9, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(arrow(530, 262, 630, 262, color=POS, sw=1.5))
    f.append(fitbox(630, 218, 165, 88, "Сервер (Отримує SYN)\nОпції відсутні!\nЗ'єднання переходить у\nзвичайний однопотоковий\nTCP без оптимізацій", size=9, fill="#ffffff", stroke=FIELD, sw=1.0))

    # Сценарій 3: Розрив семантики ACK у TCP Split-Proxy
    f.append(rect(30, 332, 780, 142, fill="#f8fafc", stroke=LINE, sw=1.2))
    f.append(text(45, 350, "Сценарій В: Передчасне підтвердження (ACK Spoofing) у Performance Enhancing Proxy", size=11, bold=True, color=INK, anchor="start"))

    f.append(fitbox(45, 362, 160, 98, "Клієнт\n1. Шле Data (Seq=1..1000)\n3. Отримує ACK=1001!\n(Вважає, що дані надійно\nзаписані на сервері)", size=9, fill="#ffffff", stroke=NEG, sw=1.0))

    f.append(arrow(205, 385, 290, 385, color=NEG, sw=1.5))
    f.append(arrow(290, 425, 205, 425, color=POS, sw=1.5))

    f.append(fitbox(290, 362, 230, 98, "TCP Split-Proxy (Супутниковий PEP)\n2. Швидкий ACK клієнту\nБуферизує 1000 байт у пам'яті\n4. ПОВІЛЬНА передача на сервер\n💥 Падіння живлення проксі!", size=9, fill="#fdecea", stroke=POS, sw=1.2))

    f.append(line(520, 395, 620, 395, color=POS, sw=1.5, dash="4,3"))
    f.append(text(570, 385, "Дані втрачено", size=9, bold=True, color=POS))

    f.append(fitbox(630, 362, 165, 98, "Сервер\nНе отримав даних.\nКлієнт не повторює, бо\nвже отримав ACK.\nТихе пошкодження сесії!", size=9, fill="#ffffff", stroke=POS, sw=1.0))

    render(os.path.join(IMG, "protocol-ossification-failures.svg"), W, H, *f)


# ── 3. Криптографічний захист: TCP/TLS 1.2 проти QUIC/TLS 1.3 ─────────────────
def fig_quic_tls13_defense():
    """Порівняння відкритості стеків TCP+TLS 1.2 та QUIC+TLS 1.3:
    повне шифрування транспортних заголовків та інкапсуляція в UDP."""
    W, H = 840, 490
    f = [text(W / 2, 26, "Криптографічний захист від Middlebox: TCP/TLS 1.2 проти QUIC/TLS 1.3", size=15, bold=True)]

    # Ліва колонка: Вразливий стек TCP + TLS 1.2
    f.append(rect(30, 48, 375, 420, fill="#fffaf9", stroke=POS, sw=1.4))
    f.append(text(217, 72, "Стек TCP + TLS 1.2 (Прозорий для Middlebox)", size=12, bold=True, color=POS))

    f.append(fitbox(45, 92, 345, 46, "IP Header (L3): Відкритий\nsrc IP, dst IP, TTL, Don't Fragment flag", size=9.5, fill="#f4f6f8", stroke=LINE, sw=1.0))

    f.append(fitbox(45, 144, 345, 82, "TCP Header (L4): ПОВНІСТЮ ВІДКРИТИЙ\n• Порти: 443 / 52140\n• Seq/Ack номери (підміна, desync)\n• Прапорці: SYN, ACK, FIN, RST (фальшиві скидання)\n• Опції: WScale, SACK, Timestamps (вирізання)", size=9, fill="#fdecea", stroke=POS, sw=1.2))

    f.append(fitbox(45, 232, 345, 82, "TLS 1.2 Record Header & Handshake: ВІДКРИТИЙ\n• Content Type, Version (0x0303)\n• ClientHello: SNI домен, Cipher Suites, Extensions\n• ServerHello, Server Certificate (сертифікат у відкритому вигляді!)\n• Можливість вибіркового блокування та підміни", size=9, fill="#fdecea", stroke=POS, sw=1.2))

    f.append(fitbox(45, 320, 345, 48, "TLS 1.2 Application Data: Зашифровано\nЗашифрований корисний потік (HTTP/1.1 або HTTP/2)", size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.0))

    f.append(fitbox(45, 380, 345, 75, "Вразливість до втручання:\n✔ Блокування нових TCP-опцій\n✔ Маніпуляція номерами послідовності\n✔ Фільтрація та підміна за SNI/Сертифікатом", size=9, fill="#ffffff", stroke=POS, sw=1.1))

    # Права колонка: Захищений стек QUIC + TLS 1.3
    f.append(rect(435, 48, 375, 420, fill="#f8fafc", stroke=FIELD, sw=1.4))
    f.append(text(622, 72, "Стек QUIC + TLS 1.3 (Криптографічна броня)", size=12, bold=True, color=FIELD))

    f.append(fitbox(450, 92, 345, 46, "IP Header (L3): Відкритий\nsrc IP, dst IP (стандартний маршрут)", size=9.5, fill="#f4f6f8", stroke=LINE, sw=1.0))

    f.append(fitbox(450, 144, 345, 46, "UDP Header (L4): Стандартний\nsrc Port, dst Port = 443 (Універсальний пропуск через NAT)", size=9.5, fill="#f4f6f8", stroke=LINE, sw=1.0))

    f.append(fitbox(450, 196, 345, 52, "QUIC Short/Long Header: Мінімальний відкритий\n• 1-біт Spin Bit (вимір RTT)\n• Destination Connection ID (не прив'язаний до IP/порту)", size=9, fill="#eaf0fd", stroke=NEG, sw=1.0))

    f.append(fitbox(450, 254, 345, 114, "ЗАШИФРОВАНО ТА АВТЕНТИФІКОВАНО (AEAD):\n• Номери пакетів (Packet Numbers захищені від інспекції)\n• Увесь транспортний стан: ACK frames, Stream frames\n• TLS 1.3 Handshake: сертифікати, розширення, ALPN\n• Flow Control, Congestion Signals, Connection Close\n• Будь-яка зміна біта middlebox → відкидання пакета!", size=9, fill="#eafaf0", stroke=FIELD, sw=1.3))

    f.append(fitbox(450, 380, 345, 75, "Результат для еволюції мережі:\n✔ Неможливо підробити Seq/Ack чи скинути сесію\n✔ Неможливо вирізати нові транспортні розширення\n✔ Захист від цензури та відновлення швидкості оновлень", size=9, fill="#ffffff", stroke=FIELD, sw=1.1))

    render(os.path.join(IMG, "quic-tls13-middlebox-defense.svg"), W, H, *f)


if __name__ == "__main__":
    fig_middlebox_architecture()
    fig_protocol_ossification()
    fig_quic_tls13_defense()
    print("Всі 3 фігури успішно згенеровано.")
