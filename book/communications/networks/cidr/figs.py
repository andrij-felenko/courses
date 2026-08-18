# -*- coding: utf-8 -*-
"""Фігури до теми «CIDR і префікси».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Класова адресація проти безкласової (CIDR) ────────────────────────────
def fig_classful_vs_cidr():
    W, H = 820, 440
    f = [text(W / 2, 28, "Класова адресація (Classful) проти безкласової (CIDR)", size=16, bold=True)]

    # Top Section: Classful addressing
    f.append(rect(40, 50, 740, 165, fill="#fff8f8", stroke=POS, sw=1.5, rx=8))
    f.append(text(60, 75, "Класова модель (RFC 791, 1981): фіксовані жорсткі межі", size=13, bold=True, color=POS, anchor="start"))

    # Class A
    f.append(rect(60, 95, 220, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(170, 118, "Клас A (/8)", size=12, bold=True))
    f.append(text(170, 138, "16 777 216 адрес", size=11, color=MUTED))

    # Class B
    f.append(rect(300, 95, 220, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(410, 118, "Клас B (/16)", size=12, bold=True))
    f.append(text(410, 138, "65 536 адрес", size=11, color=MUTED))

    # Class C
    f.append(rect(540, 95, 220, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(650, 118, "Клас C (/24)", size=12, bold=True))
    f.append(text(650, 138, "256 адрес", size=11, color=MUTED))

    # Classful problem annotation
    f.append(text(410, 185, "Потрібно 1000 адрес? Отримуй Клас B (65 536) → 98.5% адрес змарновано назавжди!", size=11, color=POS, bold=True))

    # Bottom Section: CIDR addressing
    f.append(rect(40, 235, 740, 180, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(60, 260, "Безкласова модель CIDR (RFC 1519 / RFC 4632): довільна довжина префікса", size=13, bold=True, color=FIELD, anchor="start"))

    # Variable blocks
    blocks = [
        (60, 280, 135, 60, "/22 (1024 IP)", "Точно під 1000 ПК", "#eafaf0"),
        (210, 280, 135, 60, "/20 (4096 IP)", "Для кампусу", "#eafaf0"),
        (360, 280, 135, 60, "/26 (64 IP)", "Окремий відділ", "#eafaf0"),
        (510, 280, 110, 60, "/29 (8 IP)", "Кластер БД", "#eafaf0"),
        (635, 280, 125, 60, "/31 (2 IP)", "Точка-точка (P2P)", "#eafaf0"),
    ]
    for bx, by, bw, bh, btitle, bdesc, bfill in blocks:
        f.append(rect(bx, by, bw, bh, fill=bfill, stroke=FIELD, sw=1.2, rx=4))
        f.append(text(bx + bw / 2, by + 24, btitle, size=12, bold=True, color=FIELD))
        f.append(text(bx + bw / 2, by + 44, bdesc, size=10, color=INK))

    f.append(text(410, 375, "Будь-яка межа від /0 до /32. Розмір блоку обирається точно під потребу мережі.", size=11, color=INK, bold=True))
    f.append(text(410, 395, "Економія адресного простору та ліквідація штучного поділу на класи.", size=10, color=MUTED))

    render(os.path.join(IMG, "classful-vs-cidr.svg"), W, H, *f)


# ── 2. Анатомія CIDR-префікса та скісна нотація ──────────────────────────────
def fig_cidr_prefix_anatomy():
    W, H = 820, 390
    f = [text(W / 2, 28, "Анатомія IPv4-адреси в CIDR-нотації: 198.51.100.45/26", size=16, bold=True)]

    # 32-bit bar container
    f.append(rect(50, 60, 720, 85, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))

    # Network prefix portion (26 bits -> width ~ 585px)
    f.append(rect(50, 60, 585, 85, fill="#eaf3ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(342, 92, "Префікс мережі (Network Prefix) — 26 бітів", size=14, bold=True, color=NEG))
    f.append(text(342, 118, "Маска: 11111111.11111111.11111111.11000000 (255.255.255.192)", size=11, color=MUTED))

    # Host identifier portion (6 bits -> width ~ 135px)
    f.append(rect(635, 60, 135, 85, fill="#fff7e6", stroke=POS, sw=1.8, rx=6))
    f.append(text(702, 92, "Хост (Host ID)", size=12, bold=True, color=POS))
    f.append(text(702, 118, "6 бітів (64 IP)", size=11, color=MUTED))

    # Breakdown details below
    rows = [
        (50, 175, 720, 36, "Адреса мережі (Network ID):", "198.51.100.0", "Хостові біти — всі 0 (11000000.00110011.01100100.00 000000)"),
        (50, 218, 720, 36, "Перший робочий хост (First IP):", "198.51.100.1", "Хостові біти: 000001 (початок корисного діапазону)"),
        (50, 261, 720, 36, "Останній робочий хост (Last IP):", "198.51.100.62", "Хостові біти: 111110 (кінець корисного діапазону)"),
        (50, 304, 720, 36, "Широкомовна адреса (Broadcast):", "198.51.100.63", "Хостові біти — всі 1 (11000000.00110011.01100100.00 111111)"),
    ]

    for rx, ry, rw, rh, rtitle, rip, rnote in rows:
        f.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1, rx=4))
        f.append(text(rx + 15, ry + 22, rtitle, size=11, bold=True, anchor="start"))
        f.append(text(rx + 280, ry + 22, rip, size=12, bold=True, color=NEG, anchor="start"))
        f.append(text(rx + 410, ry + 22, rnote, size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, 365, "Кількість корисних хостів = 2^(32 - 26) - 2 = 2^6 - 2 = 64 - 2 = 62 робочі адреси.", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "cidr-prefix-anatomy.svg"), W, H, *f)


# ── 3. Ієрархічний поділ підмереж (VLSM) ──────────────────────────────────────
def fig_vlsm_hierarchy():
    W, H = 820, 430
    f = [text(W / 2, 28, "Ієрархічний поділ простору IP-адрес: механізм VLSM", size=16, bold=True)]

    # Root block
    f.append(rect(50, 55, 720, 50, fill="#eaf3ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(410, 78, "Батьківський блок компанії: 192.0.2.0/24 (всього 256 адрес)", size=13, bold=True, color=NEG))
    f.append(text(410, 95, "Маска /24: 255.255.255.0", size=10, color=MUTED))

    # Level 1 Split
    f.append(arrow(230, 105, 230, 135, color=LINE, sw=1.5))
    f.append(arrow(590, 105, 590, 135, color=LINE, sw=1.5))

    # Subnet A (/25)
    f.append(rect(50, 135, 350, 70, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(225, 160, "Відділ розробки (128 IP)", size=12, bold=True, color=FIELD))
    f.append(text(225, 180, "192.0.2.0/25 (Діапазон .1 – .126)", size=11, bold=True))
    f.append(text(225, 195, "Маска: 255.255.255.128", size=9, color=MUTED))

    # Right block ready for further split (/25)
    f.append(rect(420, 135, 350, 70, fill="#fdfaf0", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(595, 160, "Резервний блок під поділ: 192.0.2.128/25", size=12, bold=True, color=MUTED))
    f.append(text(595, 182, "128 адрес (розбиваємо на менші частини)", size=10, color=MUTED))

    # Level 2 Split
    f.append(arrow(500, 205, 500, 235, color=LINE, sw=1.5))
    f.append(arrow(690, 205, 690, 235, color=LINE, sw=1.5))

    # Subnet B (/26)
    f.append(rect(420, 235, 165, 75, fill="#fff2e6", stroke=POS, sw=1.4, rx=6))
    f.append(text(502, 258, "Сервери (64 IP)", size=11, bold=True, color=POS))
    f.append(text(502, 276, "192.0.2.128/26", size=10, bold=True))
    f.append(text(502, 292, "Хости: .129 – .190", size=9, color=MUTED))

    # Subnet C (/27)
    f.append(rect(605, 235, 165, 75, fill="#f0f5ff", stroke=NEG, sw=1.4, rx=6))
    f.append(text(687, 258, "Офіс (32 IP)", size=11, bold=True, color=NEG))
    f.append(text(687, 276, "192.0.2.192/27", size=10, bold=True))
    f.append(text(687, 292, "Хости: .193 – .222", size=9, color=MUTED))

    # Level 3 Split for router links (/30 or /31)
    f.append(arrow(687, 310, 687, 335, color=LINE, sw=1.5))
    f.append(rect(420, 335, 350, 55, fill="#fdf2f8", stroke="#8e44ad", sw=1.4, rx=6))
    f.append(text(595, 356, "Міжмаршрутизаторні лінки P2P (/30 та /31)", size=11, bold=True, color="#8e44ad"))
    f.append(text(595, 375, "192.0.2.224/30 (лінковий шлюз) та 192.0.2.228/31 (RFC 3021)", size=10, color=INK))

    f.append(text(410, 415, "VLSM дозволяє призначати різну довжину маски під конкретну потребу кожної підмережі без марнування.", size=11, italic=True))

    render(os.path.join(IMG, "vlsm-hierarchy.svg"), W, H, *f)


# ── 4. Агрегація маршрутів (Supernetting / Route Summarization) ───────────────
def fig_route_aggregation():
    W, H = 820, 410
    f = [text(W / 2, 28, "Агрегація маршрутів (Supernetting) та зменшення таблиць BGP", size=16, bold=True)]

    # Left box: 4 individual /24 networks
    f.append(rect(40, 60, 290, 250, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(185, 88, "4 окремі локальні мережі клієнта", size=12, bold=True))

    nets = [
        (185, 120, "198.51.100.0/24", "11000110.00110011.011001 00.0"),
        (185, 170, "198.51.101.0/24", "11000110.00110011.011001 01.0"),
        (185, 220, "198.51.102.0/24", "11000110.00110011.011001 10.0"),
        (185, 270, "198.51.103.0/24", "11000110.00110011.011001 11.0"),
    ]
    for cx, cy, nname, nbin in nets:
        f.append(rect(60, cy - 18, 250, 36, fill=FILL, stroke=MUTED, sw=1, rx=4))
        f.append(text(185, cy, nname, size=11, bold=True, color=NEG))
        f.append(text(185, cy + 12, nbin, size=9, color=MUTED))

    # Aggregating Router (Border router)
    f.append(arrow(330, 185, 410, 185, color=INK, sw=2))
    f.append(text(370, 170, "Агрегація", size=10, bold=True))

    f.append(rect(410, 135, 120, 100, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    f.append(text(470, 175, "Межовий", size=12, bold=True, color=FIELD))
    f.append(text(470, 195, "роутер ISP", size=12, bold=True, color=FIELD))
    f.append(text(470, 215, "(BGP)", size=10, color=MUTED))

    # Right box: 1 aggregated supernet
    f.append(arrow(530, 185, 600, 185, color=FIELD, sw=2.5))
    f.append(rect(600, 110, 180, 150, fill="#eef6ff", stroke=NEG, sw=2, rx=8))
    f.append(text(690, 140, "Єдиний анонс у BGP:", size=11, bold=True))
    f.append(text(690, 175, "198.51.100.0/22", size=14, bold=True, color=NEG))
    f.append(text(690, 205, "Маска: 255.255.252.0", size=10, color=MUTED))
    f.append(text(690, 230, "4 записи → 1 запис!", size=11, bold=True, color=FIELD))

    # Summary bar at bottom
    f.append(fitbox(50, 330, 720, 55,
                    "Правило агрегації: адреси мусять бути суміжними, їхня кількість — степенем двійки,\n"
                    "а спільний префікс — вирівняним по двійковій межі. Глобальний BGP бачить 1 маршрут замість 4.",
                    size=11, fill=BG, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "route-aggregation.svg"), W, H, *f)


# ── 5. Алгоритм вибору найдовшого префікса (Longest Prefix Match) ─────────────
def fig_longest_prefix_match_trie():
    W, H = 820, 440
    f = [text(W / 2, 28, "Алгоритм Longest Prefix Match (LPM) у таблиці маршрутизації", size=16, bold=True)]

    # Incoming Packet
    f.append(rect(40, 60, 740, 50, fill="#fff2e6", stroke=POS, sw=1.8, rx=6))
    f.append(text(410, 82, "Вхідний IP-пакет: адреса призначення = 198.51.100.45", size=13, bold=True, color=POS))
    f.append(text(410, 98, "Двійковий вигляд: 11000110 . 00110011 . 01100100 . 00101101", size=10, color=MUTED))

    # Routing Table matching candidates
    table_rows = [
        (40, 130, 740, 48, "0.0.0.0/0 (Default Route)", "Збіг: 0 бітів", "Шлюз за замовчуванням (Next-hop: 203.0.113.1)", MUTED, False),
        (40, 185, 740, 48, "198.51.0.0/16 (ISP Регіон)", "Збіг: 16 бітів", "Магістральний інтерфейс eth0 (Next-hop: 10.0.0.1)", MUTED, False),
        (40, 240, 740, 48, "198.51.100.0/22 (Дата-центр)", "Збіг: 22 біти", "Агрегований канал агрегації eth1 (Next-hop: 10.0.1.1)", MUTED, False),
        (40, 295, 740, 54, "198.51.100.32/27 (Серверний кластер)", "Збіг: 27 бітів", "ПЕРЕМОЖЕЦЬ: найдовший префікс /27 → Інтерфейс eth2", FIELD, True),
    ]

    for rx, ry, rw, rh, rpref, rmatch, rdesc, rcol, rwin in table_rows:
        f.append(rect(rx, ry, rw, rh, fill="#eafaf0" if rwin else "#ffffff", stroke=rcol, sw=2 if rwin else 1.2, rx=6))
        f.append(text(rx + 20, ry + 24, rpref, size=12, bold=True, color=rcol, anchor="start"))
        f.append(text(rx + 330, ry + 24, rmatch, size=11, bold=True, color=rcol, anchor="start"))
        f.append(text(rx + 20, ry + 42, rdesc, size=10, color=INK if rwin else MUTED, anchor="start", bold=rwin))

    f.append(text(W / 2, 385, "Чому перемагає /27: правило LPM обирає маршрут із максимальною кількістю співпалих бітів префікса.", size=11, bold=True, color=INK))
    f.append(text(W / 2, 405, "Це дозволяє мати загальний маршрут для регіону (/16) і точкові винятки (/27) без конфліктів.", size=10, color=MUTED))

    render(os.path.join(IMG, "longest-prefix-match-trie.svg"), W, H, *f)


# ── 6. Програмний Radix Trie проти апаратного TCAM ───────────────────────────
def fig_tcam_vs_trie():
    W, H = 820, 430
    f = [text(W / 2, 28, "Реалізація LPM: програмний Radix Trie проти апаратного TCAM", size=16, bold=True)]

    # Left: Software Radix Trie
    f.append(rect(40, 55, 350, 310, fill="#f8fafc", stroke=NEG, sw=1.6, rx=8))
    f.append(text(215, 80, "Програмний пошук: Radix / Patricia Trie", size=13, bold=True, color=NEG))

    # Trie nodes
    f.append(circle(215, 120, 18, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(215, 124, "Корінь", size=9, bold=True))

    f.append(line(205, 134, 155, 165, color=LINE, sw=1.5))
    f.append(line(225, 134, 275, 165, color=LINE, sw=1.5))
    f.append(text(170, 145, "0", size=10, bold=True))
    f.append(text(260, 145, "1", size=10, bold=True))

    f.append(circle(155, 175, 15, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(circle(275, 175, 15, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(275, 179, "/16", size=10, bold=True, color=FIELD))

    f.append(line(275, 190, 275, 225, color=LINE, sw=1.5))
    f.append(circle(275, 235, 15, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(275, 239, "/24", size=10, bold=True, color=FIELD))

    f.append(text(215, 280, "Покроковий спуск по бітах адреси", size=10, bold=True))
    f.append(text(215, 300, "Складність: O(W) звернень до пам'яті (W = 32 біти)", size=9, color=MUTED))
    f.append(text(215, 320, "Затримка: 30–100 нс на пошук у DRAM", size=9, color=MUTED))
    f.append(text(215, 345, "Гнучко, дешево, оновлення без перебоїв", size=10, bold=True, color=NEG))

    # Right: Hardware TCAM
    f.append(rect(430, 55, 350, 310, fill="#fffaf5", stroke=POS, sw=1.6, rx=8))
    f.append(text(605, 80, "Апаратний пошук: TCAM (ASIC / NPU)", size=13, bold=True, color=POS))

    # TCAM cells (0, 1, X)
    tcam_rows = [
        (450, 110, "198.51.0.0 /16", "11000110.00110011 . XXXXXXXX.XXXXXXXX"),
        (450, 150, "198.51.100.0 /22", "11000110.00110011 . 011001XX.XXXXXXXX"),
        (450, 190, "198.51.100.32 /27", "11000110.00110011 . 01100100.001XXXXX"),
    ]
    for tx, ty, tlabel, tbits in tcam_rows:
        f.append(rect(tx, ty, 310, 34, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        f.append(text(tx + 10, ty + 15, tlabel, size=10, bold=True, color=POS, anchor="start"))
        f.append(text(tx + 10, ty + 28, tbits, size=9, color=MUTED, anchor="start"))

    f.append(text(605, 250, "Паралельне порівняння всіх рядків за 1 такт!", size=10, bold=True, color=POS))
    f.append(text(605, 275, "Трійкова комірка пам'яті: 0, 1 або X (Don't care)", size=9, color=INK))
    f.append(text(605, 295, "Priority Encoder миттєво віддає найдовший префікс", size=9, color=MUTED))
    f.append(text(605, 320, "Швидкість: 1–2 нс (до мільярдів пакетів/с)", size=9, bold=True, color=FIELD))
    f.append(text(605, 345, "Висока ціна, високе енергоспоживання (15–30 Вт)", size=9, color=POS))

    f.append(text(W / 2, 400, "Програмні роутери (Linux kernel / VPP) використовують дерева; магістральні чіпи (Broadcom, Cisco) — TCAM.", size=11, italic=True))

    render(os.path.join(IMG, "tcam-vs-trie.svg"), W, H, *f)


if __name__ == "__main__":
    fig_classful_vs_cidr()
    fig_cidr_prefix_anatomy()
    fig_vlsm_hierarchy()
    fig_route_aggregation()
    fig_longest_prefix_match_trie()
    fig_tcam_vs_trie()
    print("Всі фігури CIDR успішно згенеровано.")
