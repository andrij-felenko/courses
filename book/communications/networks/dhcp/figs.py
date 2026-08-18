# -*- coding: utf-8 -*-
"""Фігури до теми «DHCP: динамічне призначення IP-адрес».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Послідовність фаз DORA та прапорці адрес/портів ───────────────────────
def fig_dhcp_dora_flags():
    """Діаграма послідовності DORA (Discover, Offer, Request, Ack) з відображенням
    IP-адрес джерела/призначення, UDP-портів 67/68, ідентифікатора транзакції xid,
    запропонованої адреси yiaddr та прапорця Broadcast Flag."""
    W, H = 840, 520
    f = [text(W / 2, 26, "Чотириетапний діалог DHCP DORA та параметри кадрів", size=16, bold=True)]

    # Вертикальні лінії сутностей (клієнт та сервер)
    c_x, s_x = 160, 680

    # Блоки сутностей
    c_box, _, _ = textbox(c_x, 62, "DHCP Клієнт\n(MAC: 00:1A:2B:3C:4D:5E)", size=12, bold=True,
                          fill="#eef3ff", stroke=NEG, min_w=190)
    s_box, _, _ = textbox(s_x, 62, "DHCP Сервер\n(192.168.1.1 : 67)", size=12, bold=True,
                          fill="#eafaf0", stroke=FIELD, min_w=190)
    f.append(c_box)
    f.append(s_box)

    # Вертикальні направляючі ліній життя
    f.append(line(c_x, 92, c_x, 480, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(s_x, 92, s_x, 480, color=MUTED, sw=1.5, dash="4,4"))

    # 1. DHCPDISCOVER
    y1 = 140
    f.append(arrow(c_x + 10, y1, s_x - 10, y1, color=NEG, sw=2.0))
    p1, _, _ = textbox(W / 2, y1 - 12, "1. DHCPDISCOVER (Широкомовний Broadcast)\nSrc: 0.0.0.0:68 → Dst: 255.255.255.255:67 | xid: 0x39A4F2B1\nOption 53=1, Option 55=[1, 3, 6, 15], Flags: Broadcast/Unicast",
                       size=10, fill="#ffffff", stroke=NEG, pad=6, min_w=430)
    f.append(p1)

    # 2. DHCPOFFER
    y2 = 220
    f.append(arrow(s_x - 10, y2, c_x + 10, y2, color=FIELD, sw=2.0))
    p2, _, _ = textbox(W / 2, y2 - 12, "2. DHCPOFFER (Пропозиція конфігурації)\nSrc: 192.168.1.1:67 → Dst: 255.255.255.255:68 (або Unicast)\nyiaddr: 192.168.1.105, Option 54 (Server ID): 192.168.1.1, Lease: 86400s",
                       size=10, fill="#ffffff", stroke=FIELD, pad=6, min_w=430)
    f.append(p2)

    # 3. DHCPREQUEST
    y3 = 300
    f.append(arrow(c_x + 10, y3, s_x - 10, y3, color=NEG, sw=2.0))
    p3, _, _ = textbox(W / 2, y3 - 12, "3. DHCPREQUEST (Вибір сервера та запит оренди)\nSrc: 0.0.0.0:68 → Dst: 255.255.255.255:67 | xid: 0x39A4F2B1\nOption 50 (Req IP): 192.168.1.105, Option 54 (Server ID): 192.168.1.1",
                       size=10, fill="#ffffff", stroke=NEG, pad=6, min_w=430)
    f.append(p3)

    # 4. DHCPACK
    y4 = 380
    f.append(arrow(s_x - 10, y4, c_x + 10, y4, color=FIELD, sw=2.0))
    p4, _, _ = textbox(W / 2, y4 - 12, "4. DHCPACK (Підтвердження оренди та опції)\nSrc: 192.168.1.1:67 → Dst: 255.255.255.255:68 (або Unicast)\nyiaddr: 192.168.1.105, Mask: /24, Router: 192.168.1.1, DNS: 1.1.1.1",
                       size=10, fill="#ffffff", stroke=FIELD, pad=6, min_w=430)
    f.append(p4)

    # Завершальний крок: ARP Probe / Gratuitous ARP
    arp_box, _, _ = textbox(c_x + 120, 450, "Перевірка IP: ARP Probe / Gratuitous ARP\n(Якщо конфлікт → DHCPDECLINE; інакше → BOUND)",
                            size=10, fill="#fff8e7", stroke=POS, pad=6, min_w=310)
    f.append(arp_box)
    f.append(arrow(c_x, 435, c_x + 40, 450, color=POS, sw=1.5))

    render(os.path.join(IMG, "dhcp-dora-flags.svg"), W, H, *f)


# ── 2. Формат повідомлення DHCP та структура полів ───────────────────────────
def fig_dhcp_packet_format():
    """Схема структури пакета DHCP (RFC 2131) з 32-бітними рядками, фіксованим
    заголовком BOOTP (236 байтів), Magic Cookie (4 байти) та опціями TLV."""
    W, H = 840, 500
    f = [text(W / 2, 24, "Структура пакета DHCP / BOOTP (RFC 2131)", size=16, bold=True)]

    # Шкала бітів зверху
    f.append(rect(40, 45, 760, 22, fill="#eef2f7", stroke=LINE, sw=1.0, rx=3))
    f.append(text(85, 60, "0", size=10, color=MUTED, bold=True))
    f.append(text(230, 60, "7 8", size=10, color=MUTED, bold=True))
    f.append(text(420, 60, "15 16", size=10, color=MUTED, bold=True))
    f.append(text(610, 60, "23 24", size=10, color=MUTED, bold=True))
    f.append(text(785, 60, "31", size=10, color=MUTED, bold=True))

    # Рядки заголовка
    rows = [
        ("Рядок 1", [("OP (1B)\n1=Req, 2=Reply", 190), ("HTYPE (1B)\n1 = Ethernet", 190),
                    ("HLEN (1B)\n6 байтів", 190), ("HOPS (1B)\nК-ть ретрансляцій", 190)]),
        ("Рядок 2", [("XID — Transaction ID (4 байти, псевдовипадкове число клієнта)", 760)]),
        ("Рядок 3", [("SECS (2 байти)\nСекунди від старту", 380),
                    ("FLAGS (2 байти)\nБіт 0: Broadcast (B) | Біти 1-15: MBZ", 380)]),
        ("Рядок 4", [("CIADDR — Client IP Address (4 байти, заповнено лише при Renewing / Bound)", 760)]),
        ("Рядок 5", [("YIADDR — «Your» IP Address (4 байти, адреса, яку виділяє сервер клієнту)", 760)]),
        ("Рядок 6", [("SIADDR — Next Server IP Address (4 байти, адреса TFTP/PXE сервера)", 760)]),
        ("Рядок 7", [("GIADDR — Relay Agent IP Address (4 байти, IP-інтерфейс ретранслятора)", 760)]),
        ("Рядок 8", [("CHADDR — Client Hardware Address (16 байтів, перші 6 байтів = MAC клієнта)", 760)]),
        ("Рядок 9", [("SNAME — Server Host Name (64 байти, необов'язкове символьне ім'я сервера)", 760)]),
        ("Рядок 10", [("FILE — Boot File Name (128 байтів, шлях до завантажувального образу PXE)", 760)]),
        ("Cookie", [("DHCP MAGIC COOKIE (4 байти: 0x63, 0x82, 0x53, 0x63 = 99.130.83.99)", 760)]),
        ("Options", [("DHCP OPTIONS — Змінна довжина TLV (Type, Length, Value) ... Опція 255 (End)", 760)])
    ]

    cur_y = 72
    for rname, cols in rows:
        cur_x = 40
        h_cell = 28 if len(cols) == 1 and "\n" not in cols[0][0] else 32
        for title, w_col in cols:
            fill_c = "#ffffff"
            stroke_c = LINE
            txt_c = INK
            is_bold = False
            if "MAGIC COOKIE" in title:
                fill_c = "#fff8e7"
                stroke_c = POS
                is_bold = True
                txt_c = POS
            elif "DHCP OPTIONS" in title:
                fill_c = "#eafaf0"
                stroke_c = FIELD
                is_bold = True
                txt_c = FIELD
            elif "YIADDR" in title or "XID" in title:
                fill_c = "#f0f4fc"

            f.append(rect(cur_x, cur_y, w_col, h_cell, fill=fill_c, stroke=stroke_c, sw=1.2, rx=2))
            lines = title.split("\n")
            if len(lines) == 1:
                f.append(text(cur_x + w_col / 2, cur_y + h_cell / 2 + 4, lines[0],
                              size=10, color=txt_c, bold=is_bold))
            else:
                f.append(text(cur_x + w_col / 2, cur_y + 12, lines[0],
                              size=10, color=txt_c, bold=True))
                f.append(text(cur_x + w_col / 2, cur_y + 24, lines[1],
                              size=9, color=MUTED))
            cur_x += w_col
        cur_y += h_cell + 2

    render(os.path.join(IMG, "dhcp-packet-format.svg"), W, H, *f)


# ── 3. Скінченний автомат станів та життєвий цикл оренди ──────────────────────
def fig_dhcp_lease_lifecycle():
    """Скінченний автомат станів DHCP (FSM) та життєвий цикл оренди:
    INIT -> SELECTING -> REQUESTING -> BOUND -> RENEWING (T1=50%) ->
    REBINDING (T2=87.5%) -> EXPIRED -> INIT."""
    W, H = 840, 480
    f = [text(W / 2, 26, "Скінченний автомат станів DHCP та таймери оренди (RFC 2131)", size=16, bold=True)]

    # Стан 1: INIT
    s_init, _, _ = textbox(110, 90, "INIT\n(Старт, немає IP)", size=11, bold=True,
                           fill="#ffffff", stroke=LINE, min_w=140)
    f.append(s_init)

    # Стан 2: SELECTING
    s_sel, _, _ = textbox(360, 90, "SELECTING\n(Очікує DHCPOFFER)", size=11, bold=True,
                          fill="#ffffff", stroke=LINE, min_w=160)
    f.append(s_sel)

    # Стан 3: REQUESTING
    s_req, _, _ = textbox(680, 90, "REQUESTING\n(Надіслано REQUEST)", size=11, bold=True,
                          fill="#ffffff", stroke=LINE, min_w=160)
    f.append(s_req)

    # Стан 4: BOUND
    s_bound, _, _ = textbox(680, 260, "BOUND\n(Адресу призначено, оренда діє)", size=12, bold=True,
                            fill="#eafaf0", stroke=FIELD, sw=2.0, min_w=200)
    f.append(s_bound)

    # Стан 5: RENEWING
    s_ren, _, _ = textbox(360, 260, "RENEWING (T1 = 0.5 · Lease)\n(Unicast REQUEST до сервера)", size=11, bold=True,
                          fill="#eef3ff", stroke=NEG, min_w=210)
    f.append(s_ren)

    # Стан 6: REBINDING
    s_reb, _, _ = textbox(110, 260, "REBINDING (T2 = 0.875 · Lease)\n(Broadcast REQUEST усім)", size=11, bold=True,
                          fill="#fff8e7", stroke=POS, min_w=190)
    f.append(s_reb)

    # Стрілки переходів
    # INIT -> SELECTING
    f.append(arrow(180, 90, 275, 90, color=LINE, sw=1.5))
    f.append(text(227, 78, "Надсилає Discover", size=9, color=MUTED))

    # SELECTING -> REQUESTING
    f.append(arrow(445, 90, 595, 90, color=LINE, sw=1.5))
    f.append(text(520, 78, "Отримав Offer → Request", size=9, color=MUTED))

    # REQUESTING -> BOUND
    f.append(arrow(680, 125, 680, 220, color=FIELD, sw=2.0))
    f.append(text(755, 175, "Отримав DHCPACK\n(Запуск таймерів T1, T2)", size=9, color=FIELD, bold=True))

    # BOUND -> RENEWING (T1)
    f.append(arrow(575, 260, 470, 260, color=NEG, sw=1.8))
    f.append(text(522, 248, "Таймер T1 (50%)", size=9, color=NEG, bold=True))

    # RENEWING -> BOUND (ACK на поновлення)
    f.append(arrow(440, 285, 590, 285, color=FIELD, sw=1.5))
    f.append(text(515, 302, "Отримав ACK → Скидання T1/T2", size=9, color=FIELD))

    # RENEWING -> REBINDING (T2)
    f.append(arrow(250, 260, 210, 260, color=POS, sw=1.8))
    f.append(text(230, 248, "Таймер T2 (87.5%)", size=9, color=POS, bold=True))

    # REBINDING -> BOUND (ACK від будь-якого сервера)
    f.append(line(160, 290, 160, 350, color=FIELD, sw=1.5))
    f.append(line(160, 350, 680, 350, color=FIELD, sw=1.5))
    f.append(arrow(680, 350, 680, 295, color=FIELD, sw=1.5))
    f.append(text(420, 342, "Отримав ACK від будь-якого сервера → перехід у BOUND", size=9, color=FIELD, bold=True))

    # REBINDING -> INIT (Вичерпання оренди / Lease Expiration або NAK)
    f.append(line(60, 290, 60, 420, color=POS, sw=1.8))
    f.append(line(60, 420, 110, 420, color=POS, sw=1.8))
    f.append(line(110, 420, 110, 140, color=POS, sw=1.8))
    f.append(arrow(110, 140, 110, 125, color=POS, sw=1.8))
    f.append(text(75, 435, "Оренда вичерпана (Lease Expired) або DHCPNAK → Очищення IP та перехід в INIT",
                  size=10, color=POS, bold=True, anchor="start"))

    # BOUND -> INIT (DHCPRELEASE)
    f.append(line(780, 260, 810, 260, color=MUTED, sw=1.2))
    f.append(line(810, 260, 810, 450, color=MUTED, sw=1.2))
    f.append(line(810, 450, 20, 450, color=MUTED, sw=1.2))
    f.append(line(20, 450, 20, 90, color=MUTED, sw=1.2))
    f.append(arrow(20, 90, 35, 90, color=MUTED, sw=1.2))
    f.append(text(790, 465, "DHCPRELEASE (клієнт звільняє адресу добровільно)", size=9, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "dhcp-lease-lifecycle.svg"), W, H, *f)


# ── 4. Ретрансляція DHCP Relay Agent через маршрутизатор ─────────────────────
def fig_dhcp_relay_agent():
    """Схема ретрансляції DHCP через маршрутизатор (DHCP Relay Agent / GIADDR):
    Послідовний обмін повідомленнями між Клієнтом (Subnet A), Агентом ретрансляції (GIADDR)
    та віддаленим Центральним Сервером (Subnet B)."""
    W, H = 860, 500
    f = [text(W / 2, 26, "Ретрансляція DHCP через маршрутизатор (DHCP Relay Agent / GIADDR)", size=16, bold=True)]

    # 3 вертикальні колони сутностей
    c_x = 140
    r_x = 430
    s_x = 720

    # Шапки сутностей
    c_box, _, _ = textbox(c_x, 65, "DHCP Клієнт\n(VLAN 10: 192.168.10.0/24)\nIP: 0.0.0.0 : 68",
                          size=11, bold=True, fill="#eef3ff", stroke=NEG, min_w=190)
    r_box, _, _ = textbox(r_x, 65, "DHCP Relay Agent (Router)\neth0: 192.168.10.1 (GIADDR)\neth1: 10.0.0.1 (до ядра)",
                          size=11, bold=True, fill="#fff8e7", stroke=POS, min_w=220)
    s_box, _, _ = textbox(s_x, 65, "Центральний DHCP Сервер\n(Серверний сегмент 10.0.0.0/24)\nIP: 10.0.0.5 : 67",
                          size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=200)
    f.append(c_box)
    f.append(r_box)
    f.append(s_box)

    # Вертикальні направляючі ліній життя (з розривом для блоку модифікації в центрі)
    f.append(line(c_x, 105, c_x, 470, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(r_x, 105, r_x, 180, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(r_x, 248, r_x, 470, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(s_x, 105, s_x, 470, color=MUTED, sw=1.5, dash="4,4"))

    # Крок 1: Клієнт -> Relay Agent (Broadcast Discover)
    y1 = 145
    f.append(arrow(c_x + 10, y1, r_x - 10, y1, color=NEG, sw=2.0))
    p1, _, _ = textbox((c_x + r_x) / 2, y1 - 14, "1. DHCPDISCOVER (L2 Broadcast)\nSrc: 0.0.0.0:68 → Dst: 255.255.255.255:67 | GIADDR=0.0.0.0",
                       size=9, fill="#ffffff", stroke=NEG, pad=4, min_w=260)
    f.append(p1)

    # Блок обробки в Relay Agent
    y_mod = 214
    mod_box, _, _ = textbox(r_x, y_mod, "Relay Agent модифікує дейтаграму:\n• Записує GIADDR = 192.168.10.1 (IP вхідного інтерфейсу)\n• Збільшує HOPS (+1) та додає Option 82 (Circuit/Remote ID)",
                            size=9, bold=False, fill="#fffaf0", stroke=POS, pad=5, min_w=280)
    f.append(mod_box)

    # Крок 2: Relay Agent -> Центральний Сервер (Unicast Discover)
    y2 = 280
    f.append(arrow(r_x + 10, y2, s_x - 10, y2, color=POS, sw=2.0))
    p2, _, _ = textbox((r_x + s_x) / 2, y2 - 14, "2. DHCPDISCOVER (L3 Unicast Forward)\nSrc: 10.0.0.1:67 → Dst: 10.0.0.5:67 | GIADDR=192.168.10.1",
                       size=9, fill="#ffffff", stroke=POS, pad=4, min_w=260)
    f.append(p2)

    # Крок 3: Центральний Сервер -> Relay Agent (Unicast Offer)
    y3 = 355
    f.append(arrow(s_x - 10, y3, r_x + 10, y3, color=FIELD, sw=2.0))
    p3, _, _ = textbox((r_x + s_x) / 2, y3 - 14, "3. DHCPOFFER (L3 Unicast Reply)\nСервер обирає пул 192.168.10.0/24 за GIADDR\nSrc: 10.0.0.5:67 → Dst: 192.168.10.1:67 | yiaddr=192.168.10.105",
                       size=9, fill="#ffffff", stroke=FIELD, pad=4, min_w=260)
    f.append(p3)

    # Крок 4: Relay Agent -> Клієнт (L2 Delivery)
    y4 = 430
    f.append(arrow(r_x - 10, y4, c_x + 10, y4, color=FIELD, sw=2.0))
    p4, _, _ = textbox((c_x + r_x) / 2, y4 - 14, "4. DHCPOFFER (L2 Delivery до клієнта)\nRelay видаляє Option 82 і передає пакет на MAC клієнта\nDst: 255.255.255.255:68 або Unicast на chaddr",
                       size=9, fill="#ffffff", stroke=FIELD, pad=4, min_w=260)
    f.append(p4)

    render(os.path.join(IMG, "dhcp-relay-agent.svg"), W, H, *f)


# ── 5. Безпека канального рівня: DHCP Snooping ──────────────────────────────
def fig_dhcp_snooping_mitigation():
    """Схема роботи DHCP Snooping на L2-комутаторі:
    Розділення портів на Trusted (до сервера) та Untrusted (до клієнтів/зловмисників),
    блокування нелегітимного DHCPOFFER від Rogue DHCP Server та побудова
    динамічної таблиці прив'язок DHCP Snooping Binding Table."""
    W, H = 840, 460
    f = [text(W / 2, 26, "Захист мережі за допомогою DHCP Snooping на L2-комутаторі", size=16, bold=True)]

    # Комутатор у центрі
    sw_box, _, _ = textbox(W / 2, 175, "L2 Комутатор доступу з підтримкою DHCP Snooping\n(Аналіз повідомлень DHCP, фільтрація портів, ведення Binding Table)",
                           size=11, bold=True, fill="#f4f6f8", stroke=LINE, min_w=460)
    f.append(sw_box)

    # Лівий верхній кут: Легітимний DHCP сервер (Trusted Port)
    s_leg, _, _ = textbox(150, 75, "Легітимний DHCP Сервер\n(192.168.1.1)", size=11, bold=True,
                          fill="#eafaf0", stroke=FIELD, min_w=180)
    f.append(s_leg)
    f.append(arrow(150, 105, 230, 150, color=FIELD, sw=2.0))
    t_badge, _, _ = textbox(215, 120, "Port 1: TRUSTED", size=9, bold=True, fill="#eafaf0", stroke=FIELD, pad=3)
    f.append(t_badge)

    # Правий верхній кут: Фальшивий сервер Rogue DHCP (Untrusted Port)
    s_rogue, _, _ = textbox(690, 75, "Rogue DHCP Сервер (Атакуючий)\n(Спроба перехоплення шлюзу/DNS)", size=11, bold=True,
                            fill="#fff0f0", stroke=POS, min_w=220)
    f.append(s_rogue)
    f.append(line(690, 105, 610, 150, color=POS, sw=2.0))
    u_badge, _, _ = textbox(625, 120, "Port 24: UNTRUSTED", size=9, bold=True, fill="#fff0f0", stroke=POS, pad=3)
    f.append(u_badge)

    # Блокування Rogue Offer
    drop_box, _, _ = textbox(690, 155, "BLOCKED / DROPPED!\n(DHCPOFFER/ACK на Untrusted-порті заборонено)",
                             size=9, bold=True, fill="#ffe5e5", stroke=POS, pad=4)
    f.append(drop_box)

    # Нижні вузли: Легітимні клієнти (Untrusted Ports)
    c1, _, _ = textbox(180, 275, "Легітимний Клієнт A\nMAC: 00:11:22:33:44:55", size=10, fill="#ffffff", stroke=NEG)
    c2, _, _ = textbox(420, 275, "Легітимний Клієнт B\nMAC: 00:AA:BB:CC:DD:EE", size=10, fill="#ffffff", stroke=NEG)
    f.append(c1)
    f.append(c2)

    f.append(arrow(180, 245, 260, 200, color=NEG, sw=1.5))
    f.append(arrow(420, 245, 420, 200, color=NEG, sw=1.5))
    f.append(text(205, 220, "Port 2 (Untrusted)", size=9, color=MUTED))
    f.append(text(465, 220, "Port 3 (Untrusted)", size=9, color=MUTED))

    # Таблиця DHCP Snooping Binding Table внизу
    table_x, table_y = W / 2, 385
    tbl_title = "DHCP Snooping Binding Table (База динамічних прив'язок):"
    f.append(text(table_x, table_y - 35, tbl_title, size=11, bold=True, color=INK))

    headers = "MAC-адреса | IP-адреса | Оренда (с) | VLAN | Інтерфейс (Порт)"
    row1 = "00:11:22:33:44:55 | 192.168.1.101 | 86400 | VLAN 10 | FastEthernet 0/2"
    row2 = "00:AA:BB:CC:DD:EE | 192.168.1.102 | 86400 | VLAN 10 | FastEthernet 0/3"
    t_box, _, _ = textbox(table_x, table_y + 8, f"{headers}\n{row1}\n{row2}",
                          size=10, fill="#ffffff", stroke=LINE, pad=6, min_w=580)
    f.append(t_box)

    render(os.path.join(IMG, "dhcp-snooping-mitigation.svg"), W, H, *f)


def main():
    fig_dhcp_dora_flags()
    fig_dhcp_packet_format()
    fig_dhcp_lease_lifecycle()
    fig_dhcp_relay_agent()
    fig_dhcp_snooping_mitigation()
    print("Всі 5 фігур успішно згенеровано в img/")


if __name__ == "__main__":
    main()
