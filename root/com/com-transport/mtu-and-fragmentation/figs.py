# -*- coding: utf-8 -*-
"""Фігури до теми «MTU канального та мережевого рівнів: інкапсуляція, тунелі та MSS».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ієрархія розмірів кадру, MTU та TCP MSS ─────────────────────────────
def fig_mtu_mss_hierarchy():
    """Взаємозв'язок фізичного дроту, кадру L2, IP MTU та TCP MSS.
    Порівняння стандартного Ethernet (1500), Baby Giant (1600) та Jumbo Frames (9000)."""
    W, H = 880, 480
    f = [text(W / 2, 28, "Ієрархія розмірів: від фізичного кадру L2 до TCP MSS", size=16, bold=True)]

    # Рівень 1: Фізичний дріт (L1 + L2)
    f.append(rect(30, 55, 820, 95, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=6))
    f.append(text(45, 75, "Кадр на фізичному дроті (Wire Frame) — 1538 байтів загалом", size=11, bold=True, color=MUTED, anchor="start"))

    f.append(fitbox(40, 85, 75, 55, "IFG + Preamble\n+ SFD\n20 байтів (L1)", size=9, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(120, 85, 95, 55, "L2 Заголовок\n(Dst, Src, Type)\n14 байтів", size=9, fill="#eaf0fd", stroke=NEG, sw=1.2, bold=True))
    f.append(fitbox(220, 85, 550, 55, "Канальне корисне навантаження / Link MTU (IP-пакет)\n1500 байтів (максимальний неподільний L3 блок)", size=11, fill="#fffdf0", stroke="#d4ac0d", sw=1.4, bold=True))
    f.append(fitbox(775, 85, 65, 55, "FCS\nCRC-32\n4 байти", size=9, fill="#fdecea", stroke=POS, sw=1.1, bold=True))

    # Рівень 2: Мережевий рівень L3 (IP MTU)
    f.append(rect(220, 165, 550, 80, fill="#fffdf0", stroke="#d4ac0d", sw=1.5, rx=6))
    f.append(text(235, 183, "Мережевий рівень (IP MTU = 1500 байтів)", size=11, bold=True, color="#b7950b", anchor="start"))
    f.append(fitbox(230, 192, 110, 45, "IPv4 Header\n20 байтів\n(IPv6: 40 Б)", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(345, 192, 415, 45, "IP Payload (TCP сегмент або UDP датаграма)\n1480 байтів для IPv4 (1460 байтів для IPv6)", size=10, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # Рівень 3: Транспортний рівень L4 (TCP MSS)
    f.append(rect(345, 260, 415, 80, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(360, 278, "Транспортний рівень (TCP Segment)", size=11, bold=True, color=NEG, anchor="start"))
    f.append(fitbox(355, 287, 105, 45, "TCP Header\n20 байтів\n(без опцій)", size=9, fill="#fdecea", stroke=POS, sw=1.2, bold=True))
    f.append(fitbox(465, 287, 285, 45, "TCP MSS (Maximum Segment Size)\n1460 байтів (IPv4) / 1440 байтів (IPv6)\nЧисті дані прикладного рівня", size=10, fill="#ffffff", stroke=FIELD, sw=1.4, bold=True))

    # Нижня панель: Порівняння стандартів MTU
    f.append(rect(30, 355, 820, 110, fill=BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(45, 375, "Категорії розмірів MTU в сучасних мережах:", size=11, bold=True, color=INK, anchor="start"))

    f.append(fitbox(40, 385, 255, 70, "Стандартний Ethernet\nMTU = 1500 байтів\nL2 кадр: 1518 Б (1522 з VLAN)\nБазовий стандарт глобального інтернету", size=9, fill="#f4f6f8", stroke=LINE, sw=1.1))
    f.append(fitbox(305, 385, 260, 70, "Baby Giant / Mini-Jumbo\nMTU = 1508 – 1600 байтів\nL2 кадр: до 1618 Б\nЗапас під QinQ, MPLS, PPPoE у провайдерів", size=9, fill="#eefaf2", stroke=FIELD, sw=1.1))
    f.append(fitbox(575, 385, 265, 70, "Jumbo Frames (ЦОД / SAN / NAS)\nMTU = 9000 байтів\nL2 кадр: 9018 Б (MSS = 8960 Б)\nЗменшення переривань CPU у 6 разів", size=9, fill="#eaf0fd", stroke=NEG, sw=1.1))

    render(os.path.join(IMG, "mtu-mss-hierarchy.svg"), W, H, *f)


# ── 2. Накладні витрати тунелювання та оверлеїв ───────────────────────────
def fig_tunnel_overhead():
    """Порівняння структури пакетів та накладних витрат тунелювання.
    PPPoE, GRE, IPsec ESP, VXLAN та WireGuard на фоні стандартного MTU 1500."""
    W, H = 880, 500
    f = [text(W / 2, 28, "Накладні витрати тунелювання: стиснення корисного TCP MSS", size=16, bold=True)]

    y = 55
    row_h = 56
    gap = 14

    # 1. Native Ethernet IPv4
    f.append(text(35, y + 16, "Native IPv4 (Базовий)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 70, 36, "IP Hdr\n20 Б", size=8, fill="#eafaf0", stroke=FIELD, sw=1.1, bold=True))
    f.append(fitbox(252, y, 70, 36, "TCP Hdr\n20 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    f.append(fitbox(324, y, 360, 36, "TCP Payload (MSS = 1460 байтів)", size=10, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1500 | MSS: 1460\nOverhead: 0 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # 2. PPPoE
    y += row_h + gap
    f.append(text(35, y + 16, "PPPoE (Провайдери)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 50, 36, "PPPoE\n8 Б", size=8, fill="#fff3cd", stroke="#e67e22", sw=1.2, bold=True))
    f.append(fitbox(232, y, 65, 36, "IP Hdr\n20 Б", size=8, fill="#eafaf0", stroke=FIELD, sw=1.1))
    f.append(fitbox(299, y, 65, 36, "TCP Hdr\n20 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1))
    f.append(fitbox(366, y, 318, 36, "TCP Payload (MSS = 1452 байти)", size=10, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1492 | MSS: 1452\nOverhead: 8 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # 3. GRE
    y += row_h + gap
    f.append(text(35, y + 16, "GRE (IPv4 тунель)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 50, 36, "Out IP\n20 Б", size=8, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(232, y, 45, 36, "GRE\n4 Б", size=8, fill="#fff3cd", stroke="#e67e22", sw=1.2, bold=True))
    f.append(fitbox(279, y, 65, 36, "In IP\n20 Б", size=8, fill="#eafaf0", stroke=FIELD, sw=1.1))
    f.append(fitbox(346, y, 65, 36, "TCP Hdr\n20 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1))
    f.append(fitbox(413, y, 271, 36, "TCP Payload (MSS = 1436 Б)", size=10, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1476 | MSS: 1436\nOverhead: 24 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # 4. IPsec ESP
    y += row_h + gap
    f.append(text(35, y + 16, "IPsec ESP (AES-GCM)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 50, 36, "Out IP\n20 Б", size=8, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(232, y, 50, 36, "ESP Hdr\n+ IV 16Б", size=8, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    f.append(fitbox(284, y, 60, 36, "In IP\n20 Б", size=8, fill="#eafaf0", stroke=FIELD, sw=1.1))
    f.append(fitbox(346, y, 60, 36, "TCP Hdr\n20 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1))
    f.append(fitbox(408, y, 205, 36, "Payload (MSS ≈ 1412 Б)", size=10, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(615, y, 70, 36, "Trailer+ICV\n18-22 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1444-1420 | MSS: 1404\nOverhead: 56-80 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # 5. VXLAN (Overlay DC)
    y += row_h + gap
    f.append(text(35, y + 16, "VXLAN (ЦОД Оверлей)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 60, 36, "Out Eth\n14 Б", size=8, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(242, y, 50, 36, "Out IP\n20 Б", size=8, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(294, y, 45, 36, "UDP\n8 Б", size=8, fill="#fff3cd", stroke="#e67e22", sw=1.1))
    f.append(fitbox(341, y, 50, 36, "VXLAN\n8 Б", size=8, fill="#fff3cd", stroke="#e67e22", sw=1.2, bold=True))
    f.append(fitbox(393, y, 65, 36, "Inner Eth\n14 Б", size=8, fill="#eaf0fd", stroke=NEG, sw=1.1))
    f.append(fitbox(460, y, 224, 36, "Inner IP Frame (MTU 1450 Б / MSS 1410 Б)\nАбо Underlay MTU >= 1550 Б для повного 1500", size=8, fill="#ffffff", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1450 (або L2 >= 1550)\nOverhead: 50 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # 6. WireGuard
    y += row_h + gap
    f.append(text(35, y + 16, "WireGuard (UDP VPN)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y, 50, 36, "Out IP\n20 Б", size=8, fill="#eef2f7", stroke=MUTED, sw=1.1))
    f.append(fitbox(232, y, 45, 36, "UDP\n8 Б", size=8, fill="#fff3cd", stroke="#e67e22", sw=1.1))
    f.append(fitbox(279, y, 50, 36, "WG Hdr\n16 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    f.append(fitbox(331, y, 60, 36, "In IP\n20 Б", size=8, fill="#eafaf0", stroke=FIELD, sw=1.1))
    f.append(fitbox(393, y, 60, 36, "TCP Hdr\n20 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1))
    f.append(fitbox(455, y, 175, 36, "TCP Payload (MSS = 1380 Б)", size=9, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(632, y, 53, 36, "Poly1305\n16 Б", size=8, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    f.append(fitbox(690, y, 155, 36, "MTU: 1420 | MSS: 1380\nOverhead: 60-80 Б", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    render(os.path.join(IMG, "tunnel-encapsulation-overhead.svg"), W, H, *f)


# ── 3. Механізм фрагментації IPv4 ──────────────────────────────────────────
def fig_fragmentation_mechanism():
    """Як пакет IPv4 розміром 3000 байтів фрагментується для лінку з MTU 1500.
    Поля Identification, Flags (MF), Fragment Offset (блоки по 8 байтів)."""
    W, H = 880, 440
    f = [text(W / 2, 28, "Механізм фрагментації IPv4: поля заголовка та 8-байтові блоки", size=16, bold=True)]

    # Вихідний великий пакет
    f.append(rect(30, 55, 820, 75, fill="#fdfaf4", stroke="#e67e22", sw=1.4, rx=6))
    f.append(text(45, 75, "Вихідний пакет L3 (Total Length = 3000 байтів): ID = 0x4A21, DF = 0, MF = 0, Offset = 0", size=11, bold=True, color="#d35400", anchor="start"))
    f.append(fitbox(40, 85, 120, 35, "IP Hdr (20 Б)", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(165, 85, 675, 35, "IP Data Payload (2980 байтів даних прикладного або транспортного рівня: байти [0 ... 2979])", size=10, fill="#fffdf0", stroke="#d4ac0d", sw=1.2))

    # Стрілка вузького каналу
    f.append(fitbox(320, 140, 240, 30, "Маршрутизатор з MTU лінку = 1500 Б", size=10, fill="#fdecea", stroke=POS, sw=1.2, bold=True))
    f.append(arrow(440, 172, 440, 195, color=POS, sw=2))

    # Фрагмент 1
    y = 205
    f.append(rect(30, y, 820, 60, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(45, y + 16, "Фрагмент 1 (1500 Б)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y + 8, 175, 42, "IP Hdr (20 Б)\nID=0x4A21, MF=1, Offset=0", size=8.5, fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(360, y + 8, 480, 42, "Фрагмент даних: 1480 байтів (байти даних [0 ... 1479]) — кратне 8 (1480 = 185 × 8)", size=9.5, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # Фрагмент 2
    y += 70
    f.append(rect(30, y, 820, 60, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(45, y + 16, "Фрагмент 2 (1500 Б)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y + 8, 175, 42, "IP Hdr (20 Б)\nID=0x4A21, MF=1, Offset=185", size=8.5, fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(360, y + 8, 480, 42, "Фрагмент даних: 1480 байтів (байти даних [1480 ... 2959]) — Offset = 1480 / 8 = 185", size=9.5, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # Фрагмент 3
    y += 70
    f.append(rect(30, y, 820, 60, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(45, y + 16, "Фрагмент 3 (40 Б)", size=10, bold=True, color=INK, anchor="start"))
    f.append(fitbox(180, y + 8, 175, 42, "IP Hdr (20 Б)\nID=0x4A21, MF=0, Offset=370", size=8.5, fill="#fdecea", stroke=POS, sw=1.2, bold=True))
    f.append(fitbox(360, y + 8, 480, 42, "Залишок даних: 20 байтів (байти даних [2960 ... 2979]) — Offset = 2960 / 8 = 370, MF=0", size=9.5, fill="#fffdf0", stroke="#d4ac0d", sw=1.2))

    render(os.path.join(IMG, "fragmentation-mechanism.svg"), W, H, *f)


# ── 4. PMTUD, Black Hole та MSS Clamping ──────────────────────────────────
def fig_pmtud_and_mss_clamping():
    """Порівняння Path MTU Discovery (і проблеми Black Hole через блокування ICMP)
    та надійного рішення через MSS Clamping на транзитному шлюзі."""
    W, H = 880, 460
    f = [text(W / 2, 28, "PMTUD Black Hole проти апаратного MSS Clamping", size=16, bold=True)]

    # Ліва колонка: Проблема PMTU Black Hole
    f.append(rect(30, 55, 395, 385, fill="#fffaf9", stroke=POS, sw=1.4, rx=6))
    f.append(text(227, 78, "1. Проблема: Path MTU Black Hole", size=12, bold=True, color=POS, anchor="middle"))

    f.append(fitbox(45, 95, 105, 45, "Клієнт (Host A)\nMTU 1500\nDF = 1", size=9, fill=BG, stroke=LINE, sw=1.1))
    f.append(fitbox(175, 95, 105, 45, "Маршрутизатор R1\n(Тунель MTU 1420)", size=9, fill="#fdecea", stroke=POS, sw=1.1))
    f.append(fitbox(305, 95, 105, 45, "Сервер (Host B)\nMTU 1500", size=9, fill=BG, stroke=LINE, sw=1.1))

    f.append(fitbox(45, 155, 365, 55, "Пакет 1500 Б (DF=1) ──> R1 не може передати у тунель 1420 Б\nR1 відкидає пакет і надсилає назад ICMP Type 3 Code 4:\n«Fragmentation Needed, next-hop MTU = 1420»", size=9, fill="#fff3cd", stroke="#e67e22", sw=1.1))

    f.append(fitbox(45, 225, 365, 60, "⛔ Фаєрвол / Middlebox блокує всі ICMP пакети!\nКлієнт не отримує сповіщення про MTU 1420.\nКлієнт повторно надсилає 1500 Б (TCP Retransmission).\nСесія зависає назавжди (Path MTU Black Hole)!", size=9, fill="#fdecea", stroke=POS, sw=1.3, bold=True))

    f.append(fitbox(45, 300, 365, 125, "Наслідки Black Hole:\n• Малі пакети (TCP SYN, ACK, SSH keystrokes) проходять.\n• Великі пакети (HTTP відповіді, TLS сертифікати) губляться.\n• Користувач бачить «вічне завантаження сторінки».\n• TCP змушений чекати Retransmission Timeout (RTO).", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    # Права колонка: Рішення MSS Clamping
    f.append(rect(455, 55, 395, 385, fill="#f4fbf7", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(652, 78, "2. Рішення: MSS Clamping (ip tcp adjust-mss)", size=12, bold=True, color=FIELD, anchor="middle"))

    f.append(fitbox(470, 95, 105, 45, "Клієнт (Host A)\nПропонує MSS=1460", size=9, fill=BG, stroke=LINE, sw=1.1))
    f.append(fitbox(600, 95, 105, 45, "Шлюз R1 (MSS Clamp)\nadjust-mss 1380", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    f.append(fitbox(730, 95, 105, 45, "Сервер (Host B)\nОтримує MSS=1380", size=9, fill=BG, stroke=LINE, sw=1.1))

    f.append(fitbox(470, 155, 365, 55, "1. Під час TCP Handshake клієнт надсилає SYN із MSS=1460.\n2. Маршрутизатор R1 перехоплює SYN, бачить тунель MTU 1420,\n   і знає, що макс. безпечний MSS = 1420 - 20 - 20 = 1380 Б.", size=9, fill="#eafaf0", stroke=FIELD, sw=1.1))

    f.append(fitbox(470, 225, 365, 60, "✓ R1 перезаписує поле Option MSS: 1460 ──> 1380\n✓ R1 на льоту перераховує TCP Checksum (RFC 1624).\n✓ Сервер B відповідає SYN-ACK з урахуванням MSS=1380.\n✓ Обидві сторони одразу надсилають пакети <= 1420 Б!", size=9, fill="#eafaf0", stroke=FIELD, sw=1.3, bold=True))

    f.append(fitbox(470, 300, 365, 125, "Переваги MSS Clamping:\n• 100% захист від зависання веб-сайтів і TLS з'єднань.\n• Не залежить від працездатності чи фільтрації ICMP.\n• Нульова потреба змінювати MTU на мільйонах хостів.\n• Робота на рівні мережевого ядра без оверхеду проксі.", size=9, fill="#f4f6f8", stroke=MUTED, sw=1.1))

    render(os.path.join(IMG, "pmtud-and-mss-clamping.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mtu_mss_hierarchy()
    fig_tunnel_overhead()
    fig_fragmentation_mechanism()
    fig_pmtud_and_mss_clamping()
    print("All figures generated successfully.")
