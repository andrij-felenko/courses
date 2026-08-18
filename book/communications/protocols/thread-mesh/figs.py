# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми thread-mesh (Thread: IPv6-mesh протокол для IoT на основі IEEE 802.15.4)."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. thread-stack: Стек протоколів Thread ───────────────────────────────────
def fig_thread_stack():
    W, H = 780, 440
    p = []

    # Заголовок блоку застосунку
    app_b, _, _ = textbox(390, 40, "Рівень застосунків: Matter / CHIP, CoAP, MQTT-SN, кастомні IPv6-сервіси",
                          size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.5, bold=True, min_w=700)
    p.append(app_b)

    # Транспортний рівень і безпека
    p.append(rect(40, 75, 700, 75, fill="#f0f4f8", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(55, 95, "Транспорт і керування мережею", size=11, color=MUTED, bold=True, anchor="start"))

    udp_b, _, _ = textbox(165, 120, "UDP (User Datagram)\nПорти застосунку та MLE", size=10, pad=6,
                          fill="#eef4ff", stroke=NEG, sw=1.4, min_w=210)
    dtls_b, _, _ = textbox(390, 120, "DTLS / ECJPAKE\nБезпечне комісіонування", size=10, pad=6,
                           fill="#fdecea", stroke=POS, sw=1.4, min_w=200)
    mle_b, _, _ = textbox(615, 120, "MLE (Mesh Link Est.)\nСусідство та RIPng-маршрут", size=10, pad=6,
                          fill="#eafaf0", stroke=FIELD, sw=1.4, min_w=210)
    p.extend([udp_b, dtls_b, mle_b])

    # Мережевий рівень IPv6
    p.append(rect(40, 160, 700, 55, fill="#eef4ff", stroke=NEG, sw=1.4, rx=8))
    p.append(text(390, 182, "Мережевий рівень: IPv6 (ICMPv6, SLAAC, Unicast / Multicast ff02:: / ff03::)",
                  size=11, color=NEG, bold=True))
    p.append(text(390, 202, "Адресація: Link-Local (fe80::/64), Mesh-Local (fd00::/64), Global Unicast (GUA)",
                  size=10, color=INK))

    # Адаптаційний рівень 6LoWPAN
    p.append(rect(40, 225, 700, 70, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, rx=8))
    p.append(text(390, 248, "Адаптаційний рівень 6LoWPAN (RFC 4944, RFC 6282)",
                  size=12, color="#7d6608", bold=True))
    p.append(text(390, 268, "• Компресія заголовків IPHC / NHC (IPv6 40 Б + UDP 8 Б → 4..7 Б)",
                  size=10, color=INK))
    p.append(text(390, 284, "• Фрагментація та зворотне збирання: IPv6 MTU 1280 Б ↔ 802.15.4 PSDU 127 Б",
                  size=10, color=INK))

    # Рівень MAC IEEE 802.15.4
    p.append(rect(40, 305, 700, 60, fill="#fdf2e9", stroke=POS, sw=1.4, rx=8))
    p.append(text(390, 326, "Канальний рівень MAC IEEE 802.15.4 (2006)", size=11, color=POS, bold=True))
    p.append(text(390, 344, "CSMA/CA без слотів, кадри даних/ACK, 16-бітні та 64-бітні адреси, захист AES-128 CCM",
                  size=10, color=INK))

    # Фізичний рівень PHY IEEE 802.15.4
    p.append(rect(40, 375, 700, 48, fill="#f5eef8", stroke="#8e44ad", sw=1.4, rx=8))
    p.append(text(390, 395, "Фізичний рівень PHY 2.4 ГГц ISM (канали 11..26 з кроком 5 МГц)",
                  size=11, color="#5b2c6f", bold=True))
    p.append(text(390, 412, "Модуляція O-QPSK з DSSS (32 чіпи/символ), швидкість передачі 250 кбіт/с",
                  size=10, color=INK))

    render(os.path.join(OUT, "thread-stack.svg"), W, H, *p,
           title="Стек протоколів мережі Thread")


# ── 2. mesh-topology-roles: Топологія та ролі вузлів у Thread ─────────────────
def fig_mesh_topology_roles():
    W, H = 820, 460
    p = []

    # Зовнішня мережа (Internet / Wi-Fi / Ethernet)
    p.append(rect(40, 30, 220, 80, fill="#f0f4f8", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(150, 55, "Зовнішня IPv6 мережа", size=11, color=MUTED, bold=True))
    p.append(text(150, 75, "Ethernet / Wi-Fi / Інтернет", size=10, color=INK))
    p.append(text(150, 92, "IPv6 префікс: 2001:db8::/64", size=9, color=MUTED, italic=True))

    # Зв'язок WAN -> Border Router
    p.append(arrow(260, 70, 340, 70, color=NEG, sw=2.0))
    p.append(arrow(340, 70, 260, 70, color=NEG, sw=2.0))
    p.append(text(300, 60, "IPv6 Native", size=9, color=NEG, bold=True))

    # Border Router
    br_b, _, _ = textbox(440, 70, "Border Router (OTBR)\nШлюз Thread ↔ WAN\nМаршрутизація IPv6/NAT64",
                         size=10, pad=8, fill="#eafaf0", stroke=FIELD, sw=2.0, min_w=180)
    p.append(br_b)

    # Leader
    lead_b, _, _ = textbox(440, 185, "Leader (FTD / Router)\nКоординатор мережі Thread\nПризначає Router ID (0..31)\nРозподіляє Network Data",
                           size=10, pad=8, fill="#fdecea", stroke=POS, sw=2.0, min_w=190)
    p.append(lead_b)

    # Routers
    r1_b, _, _ = textbox(190, 185, "Router R1 (FTD)\nМаршрутизація каскаду\nБатьківський вузол",
                         size=10, pad=6, fill="#eef4ff", stroke=NEG, sw=1.6, min_w=160)
    r2_b, _, _ = textbox(690, 185, "Router R2 (FTD)\nМаршрутизація каскаду\nБатьківський вузол",
                         size=10, pad=6, fill="#eef4ff", stroke=NEG, sw=1.6, min_w=160)
    p.extend([r1_b, r2_b])

    # Зв'язки Mesh між Routers і Leader
    p.append(line(350, 70, 440, 145, color=FIELD, sw=1.8, dash="4,4"))
    p.append(line(270, 185, 345, 185, color=LINE, sw=1.8))
    p.append(line(535, 185, 610, 185, color=LINE, sw=1.8))
    p.append(line(440, 105, 440, 145, color=LINE, sw=2.0))
    p.append(text(307, 175, "Mesh лінк", size=9, color=MUTED))
    p.append(text(572, 175, "Mesh лінк", size=9, color=MUTED))

    # Нижній рівень: Кінцеві пристрої (End Devices)
    # REED
    reed_b, _, _ = textbox(160, 315, "REED (Router-Eligible)\nFTD-вузол у ролі Child\nМоже стати Router за потреби",
                           size=9, pad=6, fill="#fafbfc", stroke=MUTED, sw=1.4, min_w=170)
    # MED / FED
    fed_b, _, _ = textbox(360, 315, "FED / MED (End Device)\nПостійно увімкнений Rx\nНе маршрутизує пакети",
                          size=9, pad=6, fill="#fafbfc", stroke=MUTED, sw=1.4, min_w=160)
    # SED
    sed1_b, _, _ = textbox(550, 315, "SED (Sleepy End Device)\nБатарейне живлення (сон)\nНепряме опитування (Poll)",
                           size=9, pad=6, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, min_w=170)
    sed2_b, _, _ = textbox(720, 315, "SSED (Thread 1.2+)\nСинхронний сон (CSL)\nБез частих Poll-кадрів",
                           size=9, pad=6, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, min_w=140)
    p.extend([reed_b, fed_b, sed1_b, sed2_b])

    # Зв'язки Parent ↔ Child
    p.append(arrow(160, 275, 180, 220, color=MUTED, sw=1.4))
    p.append(arrow(360, 275, 420, 225, color=MUTED, sw=1.4))
    p.append(arrow(550, 275, 460, 225, color="#d4ac0d", sw=1.6))
    p.append(arrow(710, 275, 690, 220, color="#d4ac0d", sw=1.6))

    p.append(text(220, 255, "Child лінк", size=9, color=MUTED, italic=True))
    p.append(text(540, 255, "Data Poll", size=9, color="#b7950b", bold=True))

    # Легенда
    p.append(rect(40, 390, 740, 50, fill="#ffffff", stroke=MUTED, sw=1.0, rx=6))
    p.append(text(60, 412, "Легенда ролей:", size=10, color=INK, bold=True, anchor="start"))
    p.append(rect(160, 403, 14, 14, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
    p.append(text(180, 414, "Leader (1 на мережу)", size=9, color=INK, anchor="start"))
    p.append(rect(310, 403, 14, 14, fill="#eef4ff", stroke=NEG, sw=1.2, rx=2))
    p.append(text(330, 414, "Routers (до 32 активних)", size=9, color=INK, anchor="start"))
    p.append(rect(480, 403, 14, 14, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=2))
    p.append(text(500, 414, "REED / FED / MED (Child)", size=9, color=INK, anchor="start"))
    p.append(rect(640, 403, 14, 14, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=2))
    p.append(text(660, 414, "SED / SSED (Сплячі)", size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "mesh-topology-roles.svg"), W, H, *p,
           title="Топологія мережі Thread та ролі вузлів")


# ── 3. lowpan-compression-frame: Компресія заголовків 6LoWPAN IPHC ───────────
def fig_lowpan_compression_frame():
    W, H = 820, 390
    p = []

    # Верхній блок: Нестиснений пакет IPv6 + UDP
    p.append(rect(40, 40, 740, 95, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(55, 60, "Стандартний пакет IPv6 / UDP без компресії (Заголовки: 48 байтів)",
                  size=11, color=MUTED, bold=True, anchor="start"))

    p.append(rect(60, 75, 270, 45, fill="#eef4ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(195, 95, "Базовий заголовок IPv6", size=10, color=NEG, bold=True))
    p.append(text(195, 110, "40 байтів (Src/Dst IPv6, HopLimit, NextHdr)", size=9, color=INK))

    p.append(rect(335, 75, 140, 45, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(405, 95, "UDP заголовок", size=10, color=POS, bold=True))
    p.append(text(405, 110, "8 Б (Порти, CRC)", size=9, color=INK))

    p.append(rect(480, 75, 290, 45, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(625, 95, "Корисне навантаження (Payload)", size=10, color=FIELD, bold=True))
    p.append(text(625, 110, "Дані датчика, CoAP, Matter тощо", size=9, color=INK))

    # Стрілка компресії
    p.append(arrow(410, 135, 410, 170, color=FIELD, sw=2.2))
    p.append(text(410, 155, "Компресія 6LoWPAN IPHC / NHC (RFC 6282)", size=10, color=FIELD, bold=True))

    # Нижній блок: Стиснений кадр IEEE 802.15.4
    p.append(rect(40, 180, 740, 180, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    p.append(text(55, 200, "Фізичний кадр IEEE 802.15.4 (Максимальний розмір PSDU = 127 байтів)",
                  size=11, color=INK, bold=True, anchor="start"))

    # Складові 802.15.4 кадру
    x_mac = 55
    w_mac = 135
    p.append(rect(x_mac, 215, w_mac, 55, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(x_mac + w_mac/2, 235, "MAC Header (MHR)", size=9, color=MUTED, bold=True))
    p.append(text(x_mac + w_mac/2, 250, "FCF, PAN ID, Адреси", size=9, color=INK))
    p.append(text(x_mac + w_mac/2, 263, "~15..23 байти", size=9, color=MUTED))

    x_sec = x_mac + w_mac + 6
    w_sec = 85
    p.append(rect(x_sec, 215, w_sec, 55, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_sec + w_sec/2, 235, "Aux Security", size=9, color=POS, bold=True))
    p.append(text(x_sec + w_sec/2, 250, "5 байтів", size=9, color=INK))
    p.append(text(x_sec + w_sec/2, 263, "KeyID, Frame Ctr", size=9, color=POS))

    x_iphc = x_sec + w_sec + 6
    w_iphc = 100
    p.append(rect(x_iphc, 215, w_iphc, 55, fill="#eef4ff", stroke=NEG, sw=1.6, rx=4))
    p.append(text(x_iphc + w_iphc/2, 235, "IPHC Header", size=9, color=NEG, bold=True))
    p.append(text(x_iphc + w_iphc/2, 250, "2..3 байти", size=9, color=INK))
    p.append(text(x_iphc + w_iphc/2, 263, "Контекст IPv6", size=9, color=NEG))

    x_nhc = x_iphc + w_iphc + 6
    w_nhc = 95
    p.append(rect(x_nhc, 215, w_nhc, 55, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, rx=4))
    p.append(text(x_nhc + w_nhc/2, 235, "NHC UDP Hdr", size=9, color="#7d6608", bold=True))
    p.append(text(x_nhc + w_nhc/2, 250, "1..4 байти", size=9, color=INK))
    p.append(text(x_nhc + w_nhc/2, 263, "Стиснені порти", size=9, color="#7d6608"))

    x_pay = x_nhc + w_nhc + 6
    w_pay = 185
    p.append(rect(x_pay, 215, w_pay, 55, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(x_pay + w_pay/2, 235, "Корисне навантаження", size=9, color=FIELD, bold=True))
    p.append(text(x_pay + w_pay/2, 250, "70..85 байтів пейлоаду", size=9, color=INK))
    p.append(text(x_pay + w_pay/2, 263, "Чисті прикладні дані", size=9, color=FIELD))

    x_mic = x_pay + w_pay + 6
    w_mic = 85
    p.append(rect(x_mic, 215, w_mic, 55, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_mic + w_mic/2, 235, "MIC / FCS", size=9, color=POS, bold=True))
    p.append(text(x_mic + w_mic/2, 250, "4 Б + 2 Б", size=9, color=INK))
    p.append(text(x_mic + w_mic/2, 263, "Цілісність / CRC", size=9, color=POS))

    # Пояснювальний рядок внизу
    p.append(text(410, 305, "Економія: 48 байтів IPv6+UDP заголовків стискаються у 4..7 байтів 6LoWPAN",
                  size=10, color=FIELD, bold=True))
    p.append(text(410, 325, "При перевищенні 127 байтів активується фрагментація 6LoWPAN (FRAG1: 4 Б, FRAGN: 5 Б)",
                  size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "lowpan-compression-frame.svg"), W, H, *p,
           title="Компресія заголовків 6LoWPAN та структура кадру 802.15.4")


# ── 4. mle-handshake-routing: Протокол MLE та розрахунок маршрутів ────────────
def fig_mle_handshake_routing():
    W, H = 800, 420
    p = []

    # Ліва колонка: Рукостискання встановлення зв'язку MLE (Neighbor Discovery)
    p.append(rect(30, 40, 355, 355, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(207, 65, "Рукостискання лінку MLE (Link Est.)", size=11, color=MUTED, bold=True))

    # Вузли Router A та Router B
    p.append(rect(60, 85, 90, 30, fill="#eef4ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(105, 104, "Router A", size=10, color=NEG, bold=True))

    p.append(rect(260, 85, 90, 30, fill="#eef4ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(305, 104, "Router B", size=10, color=NEG, bold=True))

    # Вертикальні часові лінії
    p.append(line(105, 115, 105, 340, color=MUTED, sw=1.2, dash="4,4"))
    p.append(line(305, 115, 305, 340, color=MUTED, sw=1.2, dash="4,4"))

    # Стрілка 1: Link Request
    p.append(arrow(105, 150, 305, 170, color=FIELD, sw=1.8))
    p.append(text(205, 148, "MLE Link Request", size=9, color=FIELD, bold=True))
    p.append(text(205, 162, "TLV: Challenge, Mode, ScanMask", size=9, color=INK))

    # Стрілка 2: Link Accept and Request
    p.append(arrow(305, 205, 105, 225, color=POS, sw=1.8))
    p.append(text(205, 203, "MLE Link Accept and Request", size=9, color=POS, bold=True))
    p.append(text(205, 217, "TLV: Response, Challenge, Link Margin", size=9, color=INK))

    # Стрілка 3: Link Accept
    p.append(arrow(105, 260, 305, 280, color=NEG, sw=1.8))
    p.append(text(205, 258, "MLE Link Accept", size=9, color=NEG, bold=True))
    p.append(text(205, 272, "TLV: Response, Link Margin, Route64", size=9, color=INK))

    # Підсумок лівої колонки
    p.append(text(207, 318, "Двосторонній зв'язок підтверджено", size=9, color=FIELD, bold=True))
    p.append(text(207, 333, "Оцінено RSSI та якість лінку (Link Quality In/Out)", size=9, color=MUTED))
    p.append(text(207, 348, "Обміняно 16-бітними адресами RLOC16", size=9, color=MUTED))

    # Права колонка: Обмін таблицями маршрутизації (Route64 TLV / Distance Vector)
    p.append(rect(415, 40, 355, 355, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(592, 65, "Маршрутизація Distance Vector (RIPng)", size=11, color=MUTED, bold=True))

    # Періодичний анонс
    p.append(rect(435, 90, 315, 60, fill="#fef9e7", stroke="#d4ac0d", sw=1.4, rx=6))
    p.append(text(592, 110, "MLE Advertisement (Мультикаст ff02::1)", size=10, color="#7d6608", bold=True))
    p.append(text(592, 126, "Таймер Trickle: інтервал від 1 с до 32 с", size=9, color=INK))
    p.append(text(592, 140, "Містить Route64 TLV (вартість до всіх Router ID)", size=9, color=INK))

    # Формула вартості
    p.append(rect(435, 165, 315, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(592, 185, "Розрахунок вартості шляху (Path Cost):", size=10, color=INK, bold=True))
    p.append(text(592, 205, "Cost(Hop) = LinkQualityCost(In, Out)", size=9, color=NEG, bold=True))
    p.append(text(592, 222, "• Link Margin > 20 dB → LQ = 3 (Cost = 1)", size=9, color=INK))
    p.append(text(592, 236, "• Link Margin 10..20 dB → LQ = 2 (Cost = 2)", size=9, color=INK))
    p.append(text(592, 250, "• Link Margin 2..10 dB → LQ = 1 (Cost = 4)", size=9, color=INK))
    p.append(text(592, 264, "• Link Margin < 2 dB → LQ = 0 (Непридатний, ∞)", size=9, color=POS))

    # Вибір найкращого маршруту
    p.append(rect(435, 290, 315, 85, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(592, 310, "Вибір наступного стрибка (Next Hop):", size=10, color=FIELD, bold=True))
    p.append(text(592, 328, "Router обирає шлях з мінімальною сумою Cost", size=9, color=INK))
    p.append(text(592, 344, "При відмові лінку вартість зростає до 16 (Infinity)", size=9, color=POS))
    p.append(text(592, 360, "Мережа самовідновлюється за 1..3 секунди", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "mle-handshake-routing.svg"), W, H, *p,
           title="Встановлення сусідства MLE та розрахунок вартості шляхів RIPng")


# ── 5. thread-commissioning-security: Безпека та комісіонування ───────────────
def fig_thread_commissioning_security():
    W, H = 820, 430
    p = []

    # Верхні блоки трьох сутностей
    # Joiner
    p.append(rect(50, 40, 190, 60, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, rx=6))
    p.append(text(145, 63, "Joiner (Новий вузол)", size=10, color="#7d6608", bold=True))
    p.append(text(145, 80, "Знає лише PSKd (пароль)", size=9, color=INK))
    p.append(text(145, 93, "Не має мережевих ключів", size=9, color=MUTED, italic=True))

    # Joiner Router
    p.append(rect(315, 40, 190, 60, fill="#eef4ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(410, 63, "Joiner Router (Relay)", size=10, color=NEG, bold=True))
    p.append(text(410, 80, "Маршрутизатор Thread", size=9, color=INK))
    p.append(text(410, 93, "Транслює трафік Joiner UDP", size=9, color=MUTED, italic=True))

    # Commissioner
    p.append(rect(580, 40, 190, 60, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(675, 63, "Commissioner (Смартфон/OTBR)", size=10, color=FIELD, bold=True))
    p.append(text(675, 80, "Авторизує нові пристрої", size=9, color=INK))
    p.append(text(675, 93, "Вводить PSKd користувача", size=9, color=MUTED, italic=True))

    # Вертикальні лінії
    p.append(line(145, 100, 145, 340, color=MUTED, sw=1.2, dash="4,4"))
    p.append(line(410, 100, 410, 340, color=MUTED, sw=1.2, dash="4,4"))
    p.append(line(675, 100, 675, 340, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: Discovery Request
    p.append(arrow(145, 125, 410, 140, color=MUTED, sw=1.4))
    p.append(text(277, 125, "1. Discovery Request (Нешифрований)", size=9, color=MUTED))

    # Крок 2: Discovery Response
    p.append(arrow(410, 155, 145, 170, color=MUTED, sw=1.4))
    p.append(text(277, 155, "2. Discovery Response (Підтримка Joiner)", size=9, color=MUTED))

    # Крок 3: DTLS Handshake з ECJPAKE (проходить крізь Relay до Commissioner)
    p.append(arrow(145, 190, 410, 195, color=POS, sw=1.8))
    p.append(arrow(410, 195, 675, 200, color=POS, sw=1.8))
    p.append(text(410, 185, "3. DTLS ClientHello + ECJPAKE обмін (Автентифікація через PSKd)",
                  size=9, color=POS, bold=True))

    # Крок 4: DTLS Finished + Захищений канал
    p.append(arrow(675, 225, 410, 230, color=FIELD, sw=1.8))
    p.append(arrow(410, 230, 145, 235, color=FIELD, sw=1.8))
    p.append(text(410, 220, "4. DTLS ServerHello / Finished → Встановлено сесійний ключ KEK",
                  size=9, color=FIELD, bold=True))

    # Крок 5: Передача Network Master Key
    p.append(arrow(675, 255, 145, 270, color=NEG, sw=2.0))
    p.append(text(410, 255, "5. Передача конфігурації: Network Master Key, PAN ID, Extended PAN, Prefix",
                  size=9, color=NEG, bold=True))

    # Підсумок у Joiner
    p.append(rect(60, 290, 170, 45, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(145, 308, "Мережевий ключ отримано", size=9, color=POS, bold=True))
    p.append(text(145, 323, "Вузол готовий до Mesh", size=9, color=INK))

    # Нижній блок: Захист даних на рівні MAC
    p.append(rect(50, 360, 720, 55, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(410, 380, "Подальший захист усього трафіку в Thread Mesh:",
                  size=10, color=INK, bold=True))
    p.append(text(410, 398, "Шифрування та аутентифікація AES-128 CCM (MAC Payload + MIC-32/64) + Frame Counter проти Replay-атак",
                  size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "thread-commissioning-security.svg"), W, H, *p,
           title="Процес безпечного комісіонування вузла у мережу Thread")


if __name__ == "__main__":
    fig_thread_stack()
    fig_mesh_topology_roles()
    fig_lowpan_compression_frame()
    fig_mle_handshake_routing()
    fig_thread_commissioning_security()
    print("Всі фігури для thread-mesh згенеровано успішно.")
