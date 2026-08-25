# -*- coding: utf-8 -*-
"""Фігури до теми «NAT: трансляція мережевих адрес».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Топологія трансляції: SNAT і DNAT ──────────────────────────────────────
def fig_topology_snat_dnat():
    """Топологія NAT: приватна мережа LAN підміняється на публічну IP маршрутизатора
    для вихідних сесій (SNAT/Masquerade), а вхідні запити до сервісів перенаправляються
    за фіксованими правилами (DNAT/Port Forwarding)."""
    W, H = 840, 430
    f = [text(W / 2, 28, "Архітектура трансляції: вихідний SNAT та вхідний DNAT", size=16, bold=True)]

    # Зони: Локальна мережа (LAN) і Глобальна мережа (WAN)
    f.append(rect(40, 55, 270, 315, fill="#f0f5ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(175, 80, "Приватна мережа (LAN)", size=13, bold=True, color=NEG))
    f.append(text(175, 98, "Діапазон RFC 1918: 192.168.1.0/24", size=10, color=MUTED))

    f.append(rect(530, 55, 270, 315, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(665, 80, "Публічний Інтернет (WAN)", size=13, bold=True, color=FIELD))
    f.append(text(665, 98, "Глобально маршрутизовані IP", size=10, color=MUTED))

    # Клієнт і Локальний сервер у LAN
    f.append(fitbox(55, 120, 240, 60, "Клієнт A (ноутбук)\nIP: 192.168.1.50\nВихідний сокет: :51234",
                    size=11, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(55, 240, 240, 60, "Локальний вебсервер\nIP: 192.168.1.10\nСлухає порт :80 (HTTP)",
                    size=11, fill="#ffffff", stroke=NEG, sw=1.3, bold=True))

    # Маршрутизатор NAT посередині
    f.append(rect(340, 95, 160, 235, fill="#fff8e8", stroke=POS, sw=1.8, rx=8))
    f.append(text(420, 122, "NAT-шлюз", size=14, bold=True, color=POS))
    f.append(text(420, 140, "LAN: 192.168.1.1", size=10, color=MUTED))
    f.append(text(420, 156, "WAN: 203.0.113.5", size=11, bold=True, color=POS))

    f.append(fitbox(350, 175, 140, 65, "SNAT (PAT)\n192.168.1.50:51234\n  ⇄ :40001",
                    size=10, fill="#ffffff", stroke=POS, sw=1.1))
    f.append(fitbox(350, 250, 140, 65, "DNAT (Forwarding)\n:8080 ➔\n192.168.1.10:80",
                    size=10, fill="#ffffff", stroke=POS, sw=1.1))

    # Зовнішні вузли у WAN
    f.append(fitbox(545, 120, 240, 60, "Вебсервер у хмарі\nIP: 93.184.216.34\nПорт: :80",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3, bold=True))
    f.append(fitbox(545, 240, 240, 60, "Зовнішній користувач\nIP: 198.51.100.77\nЗвертається на 203.0.113.5:8080",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3, bold=True))

    # Стрілки з'єднань
    f.append(arrow(295, 150, 340, 150, color=NEG, sw=1.6))
    f.append(arrow(500, 150, 545, 150, color=FIELD, sw=1.6))
    f.append(arrow(545, 270, 500, 270, color=FIELD, sw=1.6))
    f.append(arrow(340, 270, 295, 270, color=NEG, sw=1.6))

    # Пояснення внизу
    f.append(fitbox(60, 380, 720, 40,
                    "SNAT підміняє внутрішню адресу джерела на зовнішню IP:порт роутера для виходу в Інтернет.\nDNAT перенаправляє вхідний трафік на публічний порт до приватного хоста всередині LAN.",
                    size=11, fill=BG, stroke=LINE, sw=1.2))
    render(os.path.join(IMG, "nat-topology-snat-dnat.svg"), W, H, *f)


# ── 2. Класифікація типів NAT (Конуси та Симетричний NAT) ────────────────────
def fig_nat_types():
    """Чотири типи поведінки трансляції та фільтрації (RFC 3489 / RFC 4787):
    Full Cone, Restricted Cone, Port Restricted Cone та Symmetric NAT."""
    W, H = 840, 460
    f = [text(W / 2, 26, "Класифікація типів NAT за правилами фільтрації та мапінгу", size=16, bold=True)]

    types = [
        ("Full Cone NAT",
         "Повний конус (EIM / EIF)",
         "Мапінг прив'язаний лише до внутрішнього сокета.",
         "Будь-який зовнішній вузол може слати пакети на відкритий зовнішній порт.",
         "#eafaf0", FIELD),
        ("Restricted Cone NAT",
         "Обмежений за адресою (EIM / ADF)",
         "Зовнішній вузол може відповісти, лише якщо клієнт раніше надсилав пакет",
         "на його IP-адресу (порт відправника значення не має).",
         "#f0f5ff", NEG),
        ("Port Restricted Cone",
         "Обмежений за портом (EIM / APDF)",
         "Зовнішній вузол може відповісти, лише якщо клієнт раніше надсилав пакет",
         "на точну пару (IP_dest, Port_dest).",
         "#fff8e8", POS),
        ("Symmetric NAT",
         "Симетричний NAT (ADM / APDF)",
         "Для кожної нової зовнішньої адреси призначається НОВИЙ зовнішній порт.",
         "Прямий P2P-траверс неможливий — потрібен релей TURN.",
         "#fdecea", POS)
    ]

    bx, by, bw, bh = 40, 52, 365, 175
    for i, (title_, subtitle, l1, l2, fillc, col) in enumerate(types):
        col_idx = i % 2
        row_idx = i // 2
        x = bx + col_idx * (bw + 30)
        y = by + row_idx * (bh + 18)

        f.append(rect(x, y, bw, bh, fill=fillc, stroke=col, sw=1.5, rx=8))
        f.append(text(x + bw / 2, y + 24, title_, size=13, bold=True, color=col))
        f.append(text(x + bw / 2, y + 42, subtitle, size=10, color=MUTED, italic=True))

        f.append(fitbox(x + 12, y + 54, bw - 24, 105,
                        f"Правило пропуску:\n• {l1}\n• {l2}",
                        size=10, fill="#ffffff", stroke=col, sw=1.0))

    f.append(fitbox(60, 420, 720, 32,
                    "Cone NAT зберігає однаковий зовнішній порт для всіх цілей (EIM); Symmetric виділяє новий порт для кожної цілі.",
                    size=10, fill=BG, stroke=LINE, sw=1.1))
    render(os.path.join(IMG, "nat-types-cone-symmetric.svg"), W, H, *f)


# ── 3. Подолання NAT: STUN, TURN та ICE ──────────────────────────────────────
def fig_nat_traversal():
    """Протоколи подолання NAT (NAT Traversal): рефлексивне визначення адреси (STUN),
    релей трафіку при симетричному NAT (TURN) та координація кандидатів (ICE)."""
    W, H = 840, 440
    f = [text(W / 2, 26, "Механізми подолання NAT: архітектура STUN, TURN та ICE", size=16, bold=True)]

    # Клієнт A за NAT
    f.append(rect(40, 60, 200, 160, fill="#f0f5ff", stroke=NEG, sw=1.4, rx=6))
    f.append(text(140, 84, "Клієнт A (за NAT)", size=12, bold=True, color=NEG))
    f.append(fitbox(50, 96, 180, 110, "Локальний сокет:\n192.168.1.100:5000\n\nNAT мапінг:\n203.0.113.10:45000",
                    size=10, fill="#ffffff", stroke=NEG, sw=1.0))

    # Сервери STUN і TURN у центрі
    f.append(rect(320, 55, 200, 100, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(420, 78, "Сервер STUN", size=12, bold=True, color=FIELD))
    f.append(text(420, 96, "RFC 5389 / 8489", size=10, color=MUTED))
    f.append(fitbox(330, 106, 180, 40, "Повертає рефлексивну IP:порт\n(XOR-MAPPED-ADDRESS)",
                    size=9, fill="#ffffff", stroke=FIELD, sw=1.0))

    f.append(rect(320, 175, 200, 100, fill="#fff8e8", stroke=POS, sw=1.4, rx=6))
    f.append(text(420, 198, "Сервер TURN", size=12, bold=True, color=POS))
    f.append(text(420, 216, "RFC 5766 / 8656", size=10, color=MUTED))
    f.append(fitbox(330, 226, 180, 40, "Ретранслює медіа-трафік\n(якщо NAT симетричний)",
                    size=9, fill="#ffffff", stroke=POS, sw=1.0))

    # Клієнт B за NAT
    f.append(rect(600, 60, 200, 160, fill="#f0f5ff", stroke=NEG, sw=1.4, rx=6))
    f.append(text(700, 84, "Клієнт B (за NAT)", size=12, bold=True, color=NEG))
    f.append(fitbox(610, 96, 180, 110, "Локальний сокет:\n10.0.0.5:6000\n\nNAT мапінг:\n198.51.100.20:56000",
                    size=10, fill="#ffffff", stroke=NEG, sw=1.0))

    # Стрілки опитування STUN
    f.append(arrow(240, 100, 320, 100, color=FIELD, sw=1.4))
    f.append(arrow(600, 100, 520, 100, color=FIELD, sw=1.4))

    # Прямий P2P канал vs Релей через TURN
    f.append(arrow(240, 225, 320, 225, color=POS, sw=1.4))
    f.append(arrow(520, 225, 600, 225, color=POS, sw=1.4))

    # Нижня секція ICE
    f.append(rect(40, 290, 760, 135, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=8))
    f.append(text(420, 314, "Фреймворк ICE (Interactive Connectivity Establishment — RFC 8445)", size=13, bold=True))
    f.append(fitbox(55, 328, 730, 85,
                    "1. Збір кандидатів: Host (локальна IP) ➔ Server Reflexive (STUN IP) ➔ Relayed (TURN IP).\n"
                    "2. Обмін кандидатами через сигналізацію (SDP offer/answer).\n"
                    "3. STUN Connectivity Checks: перевірка зв'язності пар кандидатів і вибір найшвидшого прямого P2P шляху.",
                    size=10, fill="#ffffff", stroke=MUTED, sw=1.1))
    render(os.path.join(IMG, "nat-traversal-stun-turn-ice.svg"), W, H, *f)


# ── 4. Структура з'єднань conntrack у ядрі ───────────────────────────────────
def fig_conntrack_table():
    """Архітектура збереження сесій у підсистемі nf_conntrack ядра Linux:
    структура кортежу (5-tuple) у напрямках ORIGINAL та REPLY."""
    W, H = 840, 420
    f = [text(W / 2, 26, "Структура сесії conntrack: двонаправлені кортежі (5-tuple)", size=16, bold=True)]

    # Вхідний пакет створює сесію
    f.append(fitbox(40, 52, 760, 44,
                    "Клієнт 192.168.1.50:51234 надсилає TCP SYN на 93.184.216.34:80 через NAT (WAN IP: 203.0.113.5)",
                    size=11, fill="#eef3ff", stroke=NEG, sw=1.3, bold=True))

    # Картка запису struct nf_conn
    f.append(rect(40, 110, 760, 255, fill="#fffaf0", stroke=POS, sw=1.6, rx=8))
    f.append(text(420, 134, "Запис у хеш-таблиці ядра: struct nf_conn", size=14, bold=True, color=POS))
    f.append(text(420, 152, "Стан: TCP_CONNTRACK_ESTABLISHED · Таймер згасання: 432000s", size=10, color=MUTED))

    # Кортеж ORIGINAL
    f.append(rect(60, 168, 345, 140, fill="#ffffff", stroke=NEG, sw=1.3, rx=6))
    f.append(text(232, 190, "IP_CT_DIR_ORIGINAL (Прямий)", size=12, bold=True, color=NEG))
    f.append(fitbox(70, 202, 325, 95,
                    "• Протокол: IPPROTO_TCP (6)\n"
                    "• Джерело (src): 192.168.1.50 : 51234\n"
                    "• Призначення (dst): 93.184.216.34 : 80\n"
                    "Хеш-ключ: jhash(src, dst, ports, proto)",
                    size=10, fill="#f4f6f8", stroke=NEG, sw=1.0))

    # Кортеж REPLY
    f.append(rect(435, 168, 345, 140, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(607, 190, "IP_CT_DIR_REPLY (Зворотний)", size=12, bold=True, color=FIELD))
    f.append(fitbox(445, 202, 325, 95,
                    "• Протокол: IPPROTO_TCP (6)\n"
                    "• Джерело (src): 93.184.216.34 : 80\n"
                    "• Призначення (dst): 203.0.113.5 : 40001\n"
                    "Хеш-ключ: jhash(src, dst, ports, proto)",
                    size=10, fill="#f4f6f8", stroke=FIELD, sw=1.0))

    f.append(fitbox(60, 318, 720, 38,
                    "Зворотний пакет від сервера на 203.0.113.5:40001 шукається в хеш-таблиці за кортежем REPLY\nі миттєво транслюється назад у внутрішній сокет 192.168.1.50:51234.",
                    size=10, fill="#ffffff", stroke=MUTED, sw=1.0))

    f.append(fitbox(40, 375, 760, 35,
                    "При вичерпанні ліміту nf_conntrack_max ядро відкидає нові з'єднання (table full, dropping packet).",
                    size=10, fill=BG, stroke=LINE, sw=1.1))
    render(os.path.join(IMG, "conntrack-tuple-table.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology_snat_dnat()
    fig_nat_types()
    fig_nat_traversal()
    fig_conntrack_table()
    print("OK: 4 figures generated into", IMG)
