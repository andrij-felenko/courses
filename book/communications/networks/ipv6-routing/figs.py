# -*- coding: utf-8 -*-
"""Фігури до теми «Маршрутизація IPv6».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія 128-бітної адреси та Solicited-Node Multicast ────────────────
def fig_address_anatomy():
    W, H = 820, 390
    f = [text(W / 2, 28, "Анатомія адреси IPv6 та формування Solicited-Node Multicast", size=16, bold=True)]

    # Верхній блок: Unicast адреса 128 біт
    f.append(text(60, 62, "Global Unicast (128 біт):", size=13, bold=True, anchor="start"))
    
    # 3 блоки адреси: Global Prefix (48), Subnet ID (16), Interface ID (64)
    # /64 межа на x = 460
    # Блок 1: Global Routing Prefix (0..48 біт)
    f.append(rect(60, 78, 230, 52, fill="#eaf2fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(175, 100, "2001 : 0db8 : 0001", size=14, bold=True, color=NEG))
    f.append(text(175, 120, "Global Routing Prefix (48 біт)", size=11, color=MUTED))

    # Блок 2: Subnet ID (48..64 біт)
    f.append(rect(295, 78, 140, 52, fill="#fdf6e7", stroke="#d97706", sw=1.8, rx=4))
    f.append(text(365, 100, "004a", size=14, bold=True, color="#b45309"))
    f.append(text(365, 120, "Subnet ID (16 біт)", size=11, color=MUTED))

    # Блок 3: Interface ID (64..128 біт)
    f.append(rect(440, 78, 320, 52, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(600, 100, "0211 : 22ff : fe33 : 4455", size=14, bold=True, color=FIELD))
    f.append(text(600, 120, "Interface ID (64 біти)", size=11, color=MUTED))

    # Риска розділу /64
    f.append(line(437, 68, 437, 142, color=POS, sw=2, dash="4,3"))
    f.append(text(437, 156, "стандартна межа /64 для SLAAC", size=11, color=POS, bold=True))

    # Стрілка вниз до формування Solicited-Node Multicast
    # Виділяємо молодші 24 біти: 33 : 4455
    f.append(rect(635, 83, 120, 42, fill="none", stroke=POS, sw=2, rx=3))
    f.append(text(695, 62, "молодші 24 біти", size=11, color=POS, bold=True))

    f.append(arrow(695, 134, 695, 195, color=POS, sw=2))

    # Нижній блок: Solicited-Node Multicast
    f.append(text(60, 205, "Solicited-Node Multicast (ff02::1:ff00:0/104):", size=13, bold=True, anchor="start"))

    f.append(rect(60, 220, 440, 52, fill="#f5f3ff", stroke="#7c3aed", sw=1.8, rx=4))
    f.append(text(280, 242, "ff02 : 0000 : 0000 : 0000 : 0000 : 0001 : ff", size=13, bold=True, color="#6d28d9"))
    f.append(text(280, 262, "Фіксований префікс групи (104 біти)", size=11, color=MUTED))

    f.append(rect(505, 220, 255, 52, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(632, 242, "33 : 4455", size=14, bold=True, color=POS))
    f.append(text(632, 262, "24 біти з Unicast адреси", size=11, color=POS))

    # Стрілка до MAC-адреси
    f.append(arrow(632, 276, 632, 310, color=INK, sw=1.8))
    f.append(rect(470, 314, 325, 42, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(632, 332, "Ethernet Multicast MAC:  33 : 33 : ff : 33 : 44 : 55", size=12, bold=True, color=INK))
    f.append(text(632, 348, "апаратна фільтрація мережевою картою (NIC)", size=10, color=MUTED))

    f.append(fitbox(60, 290, 380, 68,
                    "Solicited-Node група дозволяє звертатися до конкретного вузла\n"
                    "без broadcast-штормів: мережеві карти інших вузлів фільтрують\n"
                    "кадр на рівні кремнію за хешем MAC 33:33:xx:xx:xx:xx.",
                    size=11, fill=BG, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "ipv6-address-anatomy.svg"), W, H, *f)


# ── 2. Протокол NDP замість ARP: розв'язання адрес без broadcast ─────────────
def fig_ndp_resolution():
    W, H = 820, 390
    f = [text(W / 2, 28, "Розв'язання L2-адреси в IPv6 (NDP) замість широкомовного ARP", size=16, bold=True)]

    # Вузол A (Джерело)
    f.append(rect(50, 70, 160, 90, fill="#eaf2fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(130, 95, "Вузол A", size=14, bold=True, color=NEG))
    f.append(text(130, 118, "2001:db8::10", size=11, color=INK))
    f.append(text(130, 138, "MAC: 00:11:22:33:44:aa", size=10, color=MUTED))

    # Вузол B (Ціль)
    f.append(rect(610, 70, 160, 90, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(690, 95, "Вузол B (Ціль)", size=14, bold=True, color=FIELD))
    f.append(text(690, 118, "2001:db8::20", size=11, color=INK))
    f.append(text(690, 138, "MAC: 00:11:22:33:44:bb", size=10, color=MUTED))

    # Вузол C (Сторонній сусід)
    f.append(rect(330, 255, 160, 75, fill="#fdf2f2", stroke="#9ca3af", sw=1.5, rx=6))
    f.append(text(410, 278, "Вузол C (Сусід)", size=13, bold=True, color="#4b5563"))
    f.append(text(410, 298, "2001:db8::99", size=11, color=MUTED))
    f.append(text(410, 315, "NIC відкидає кадр", size=10, color=POS, bold=True))

    # Стрілка 1: Neighbor Solicitation (NS)
    f.append(arrow(215, 88, 605, 88, color=NEG, sw=2))
    f.append(rect(235, 58, 350, 24, fill="#ffffff", stroke=NEG, sw=1.2, rx=3))
    f.append(text(410, 74, "1. ICMPv6 NS → ff02::1:ff00:20 (MAC 33:33:ff:00:00:20)", size=10, bold=True, color=NEG))

    # Стрілка відгалуження до вузла C (пунктир з хрестиком)
    f.append(line(410, 88, 410, 250, color="#9ca3af", sw=1.5, dash="4,4"))
    f.append(circle(410, 175, 12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(410, 180, "✕", size=13, bold=True, color=POS))

    # Стрілка 2: Neighbor Advertisement (NA)
    f.append(arrow(605, 142, 215, 142, color=FIELD, sw=2))
    f.append(rect(235, 112, 350, 24, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(410, 128, "2. ICMPv6 NA (Unicast) → Вузол A з MAC 00:11:22:33:44:bb", size=10, bold=True, color=FIELD))

    # Пояснювальний блок унизу
    f.append(fitbox(50, 235, 260, 125,
                    "IPv4 (ARP): запит слався на\n"
                    "FF:FF:FF:FF:FF:FF (broadcast) —\n"
                    "кожен комп'ютер у мережі мусив\n"
                    "переривати CPU і читати пакет.\n"
                    "У великих сегментах це створювало\n"
                    "шторми широкомовлення.",
                    size=10, fill="#fff7e6", stroke="#d97706", sw=1.2))

    f.append(fitbox(510, 235, 260, 125,
                    "IPv6 (NDP): запит надсилається на\n"
                    "вузьку групу Solicited-Node Multicast.\n"
                    "Сторонні вузли не чують запиту:\n"
                    "апаратний фільтр мережевої карти\n"
                    "відкидає кадр до передачі в OS.\n"
                    "Відповідь NA повертається unicast.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, "ndp-resolution-flow.svg"), W, H, *f)


# ── 3. Життєвий цикл SLAAC та DAD ────────────────────────────────────────────
def fig_slaac_dad_lifecycle():
    W, H = 820, 390
    f = [text(W / 2, 28, "Автоконфігурація SLAAC та перевірка унікальності DAD", size=16, bold=True)]

    # 4 етапи послідовності
    # Етап 1: Link-Local + DAD
    f.append(rect(40, 65, 170, 215, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=5))
    f.append(text(125, 88, "1. Link-Local", size=13, bold=True, color=INK))
    f.append(fitbox(48, 102, 154, 168,
                    "Генерація Link-Local:\n"
                    "fe80:: + Interface ID.\n\n"
                    "Стан: TENTATIVE\n"
                    "(тимчасова, не активна).\n\n"
                    "DAD: надсилання NS на\n"
                    "власну solicited-node\n"
                    "адресу. Якщо 1 с тиша —\n"
                    "адреса активна.",
                    size=10, fill="#ffffff", stroke="#d1d5db", sw=1.0))

    f.append(arrow(215, 170, 235, 170, color=INK, sw=1.8))

    # Етап 2: Router Solicitation / Advertisement
    f.append(rect(240, 65, 170, 215, fill="#eaf2fd", stroke=NEG, sw=1.5, rx=5))
    f.append(text(325, 88, "2. Запит шлюзу", size=13, bold=True, color=NEG))
    f.append(fitbox(248, 102, 154, 168,
                    "Вузол шле RS на ff02::2\n"
                    "(усі маршрутизатори).\n\n"
                    "Маршрутизатор вертає RA\n"
                    "(періодично або у відповідь):\n"
                    "• Префікс мережі (/64)\n"
                    "• Прапорець A=1 (SLAAC)\n"
                    "• Прапорці M/O (DHCPv6)\n"
                    "• Lifetime та RDNSS DNS.",
                    size=10, fill="#ffffff", stroke="#93c5fd", sw=1.0))

    f.append(arrow(415, 170, 435, 170, color=INK, sw=1.8))

    # Етап 3: Формування GUA та повторний DAD
    f.append(rect(440, 65, 170, 215, fill="#fdf6e7", stroke="#d97706", sw=1.5, rx=5))
    f.append(text(525, 88, "3. Збірка GUA", size=13, bold=True, color="#b45309"))
    f.append(fitbox(448, 102, 154, 168,
                    "Вузол склеює:\n"
                    "Префікс з RA (/64)\n"
                    "+ Interface ID (/64)\n"
                    "= Global Unicast (GUA).\n\n"
                    "Нова адреса знову входить\n"
                    "у стан TENTATIVE.\n\n"
                    "Запуск DAD для GUA.",
                    size=10, fill="#ffffff", stroke="#fcd34d", sw=1.0))

    f.append(arrow(615, 170, 635, 170, color=INK, sw=1.8))

    # Етап 4: Робочий стан
    f.append(rect(640, 65, 140, 215, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=5))
    f.append(text(710, 88, "4. Готово", size=13, bold=True, color=FIELD))
    f.append(fitbox(648, 102, 124, 168,
                    "Адреса валідна!\n\n"
                    "Вузол додає:\n"
                    "• GUA адресу на IF\n"
                    "• Дефолтний маршрут\n"
                    "  ::/0 через link-local\n"
                    "  адресу роутера\n"
                    "• DNS сервери.",
                    size=10, fill="#ffffff", stroke="#86efac", sw=1.0))

    # Підсумок у плашці внизу
    f.append(fitbox(40, 295, 740, 70,
                    "SLAAC (RFC 4862) дає повну автоконфігурацію без централізованого сервера DHCP.\n"
                    "DAD (Duplicate Address Detection) гарантує відсутність колізій IP: адреса не обслуговує трафік,\n"
                    "доки вузол не переконається, що на запит NS ніхто в сегменті не відповів NA.",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.3))

    render(os.path.join(IMG, "slaac-dad-lifecycle.svg"), W, H, *f)


# ── 4. Next-Hop на базі Link-Local адреси в таблиці маршрутів ─────────────────
def fig_routing_nexthop():
    W, H = 820, 370
    f = [text(W / 2, 28, "Прив'язка Next-Hop до Link-Local адреси та інтерфейсу в IPv6", size=16, bold=True)]

    # Маршрутизатор 1 (R1)
    f.append(rect(60, 80, 180, 95, fill="#eaf2fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(150, 105, "Маршрутизатор R1", size=14, bold=True, color=NEG))
    f.append(text(150, 128, "eth0: fe80::1", size=11, bold=True, color=INK))
    f.append(text(150, 148, "GUA: 2001:db8:1::1/64", size=10, color=MUTED))

    # Маршрутизатор 2 (R2)
    f.append(rect(580, 80, 180, 95, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(670, 105, "Маршрутизатор R2", size=14, bold=True, color=FIELD))
    f.append(text(670, 128, "eth1: fe80::2", size=11, bold=True, color=INK))
    f.append(text(670, 148, "GUA: 2001:db8:2::1/64", size=10, color=MUTED))

    # З'єднувальна лінія каналу
    f.append(line(245, 125, 575, 125, color=LINE, sw=2))
    f.append(rect(340, 105, 140, 38, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(410, 120, "Канал зв'язку (L2)", size=11, bold=True))
    f.append(text(410, 134, "спільний link-local scope", size=9, color=MUTED))

    # Таблиця маршрутизації R1
    f.append(rect(60, 205, 340, 140, fill="#fdf6e7", stroke="#d97706", sw=1.5, rx=5))
    f.append(text(230, 228, "Таблиця маршрутів R1 (FIB)", size=12, bold=True, color="#b45309"))
    f.append(line(70, 238, 390, 238, color="#d97706", sw=1.0))
    f.append(text(75, 258, "Призначення", size=10, bold=True, anchor="start"))
    f.append(text(190, 258, "Next Hop", size=10, bold=True, anchor="start"))
    f.append(text(320, 258, "Інтерфейс", size=10, bold=True, anchor="start"))
    f.append(line(70, 266, 390, 266, color="#e5e7eb", sw=1.0))

    f.append(text(75, 288, "2001:db8:2::/64", size=10, anchor="start"))
    f.append(text(190, 288, "fe80::2", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(320, 288, "eth0", size=10, bold=True, color=NEG, anchor="start"))

    f.append(text(75, 312, "::/0 (дефолт)", size=10, anchor="start"))
    f.append(text(190, 312, "fe80::2", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(320, 312, "eth0", size=10, bold=True, color=NEG, anchor="start"))

    # Переваги такої схеми
    f.append(fitbox(430, 205, 330, 140,
                    "Чому Next Hop — це Link-Local (fe80::2%eth0):\n\n"
                    "1. Незалежність від зміни ISP (Renumbering):\n"
                    "   якщо провайдер змінить глобальний префікс з\n"
                    "   2001:db8:: на 2001:cafe::, внутрішня таблиця\n"
                    "   маршрутизації та OSPF/IS-IS сусідства не падають.\n"
                    "2. Економія адрес: інтерфейси роутерів не потребують\n"
                    "   глобальних підмереж на transit-лінках.",
                    size=10, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "ipv6-routing-nexthop.svg"), W, H, *f)


# ── 5. Перехідні механізми: NAT64 та DNS64 ───────────────────────────────────
def fig_nat64_dns64():
    W, H = 820, 380
    f = [text(W / 2, 28, "Взаємодія IPv6-клієнта з IPv4-сервером через DNS64 та NAT64", size=16, bold=True)]

    # 1. IPv6 Клієнт
    f.append(rect(40, 75, 140, 80, fill="#eaf2fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(110, 102, "IPv6 Клієнт", size=13, bold=True, color=NEG))
    f.append(text(110, 122, "2001:db8::100", size=10, color=INK))
    f.append(text(110, 138, "не має адреси IPv4", size=9, color=POS))

    # 2. DNS64 Сервер
    f.append(rect(240, 75, 160, 80, fill="#fdf6e7", stroke="#d97706", sw=1.8, rx=6))
    f.append(text(320, 102, "DNS64 Сервер", size=13, bold=True, color="#b45309"))
    f.append(text(320, 122, "Синтез AAAA запису", size=10, color=INK))
    f.append(text(320, 138, "64:ff9b:: + IPv4", size=9, color=MUTED))

    # 3. NAT64 Шлюз
    f.append(rect(460, 75, 150, 80, fill="#f5f3ff", stroke="#7c3aed", sw=1.8, rx=6))
    f.append(text(535, 102, "NAT64 Шлюз", size=13, bold=True, color="#6d28d9"))
    f.append(text(535, 122, "Трансляція заголовків", size=10, color=INK))
    f.append(text(535, 138, "Stateful L4 Translation", size=9, color=MUTED))

    # 4. IPv4 Сервер
    f.append(rect(660, 75, 120, 80, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(720, 102, "IPv4 Сервер", size=13, bold=True, color=INK))
    f.append(text(720, 122, "198.51.100.42", size=10, bold=True, color=POS))
    f.append(text(720, 138, "тільки IPv4", size=9, color=MUTED))

    # Покроковий потік (стрілки)
    # Крок 1: Запит DNS
    f.append(arrow(185, 95, 235, 95, color=NEG, sw=1.5))
    f.append(text(210, 88, "1. AAAA?", size=9, color=NEG, bold=True))

    # Крок 2: Відповідь DNS64
    f.append(arrow(235, 125, 185, 125, color="#d97706", sw=1.5))
    f.append(text(210, 140, "2. AAAA", size=9, color="#d97706", bold=True))

    # Крок 3: Пакет IPv6 до NAT64
    f.append(arrow(110, 160, 500, 160, color=NEG, sw=1.8))
    f.append(text(300, 175, "3. IPv6 Пакет: Src=2001:db8::100, Dst=64:ff9b::c633:642a", size=10, bold=True, color=NEG))

    # Крок 4: Пакет IPv4 від NAT64 до Сервера
    f.append(arrow(615, 115, 655, 115, color=POS, sw=2))
    f.append(text(635, 105, "4. IPv4", size=9, bold=True, color=POS))

    # Детальний опис кроків у таблиці унизу
    f.append(fitbox(40, 205, 740, 150,
                    "Порядок роботи зв'язки DNS64 + NAT64:\n\n"
                    "1. Клієнт запитує AAAA (IPv6) для web.example.com. Сервер має лише A-запис (198.51.100.42).\n"
                    "2. DNS64 бере IPv4-адресу (198.51.100.42 = 0xc6.0x33.0x64.0x2a) і склеює її з префіксом Well-Known\n"
                    "   (64:ff9b::/96) → синтезує фіктивну IPv6-адресу 64:ff9b::c633:642a і повертає клієнту.\n"
                    "3. Клієнт надсилає IPv6-пакет на адресу 64:ff9b::c633:642a. Маршрутизатор направляє цей префікс до NAT64.\n"
                    "4. NAT64 вилучає IPv4-адресу з молодших 32 бітів Dst IPv6, замінює IPv6-заголовок на IPv4, призначає\n"
                    "   публічну IPv4-адресу та динамічний порт джерела (PAT) і відправляє у чисту мережу IPv4.",
                    size=10, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "nat64-dns64-transition.svg"), W, H, *f)


def main():
    fig_address_anatomy()
    fig_ndp_resolution()
    fig_slaac_dad_lifecycle()
    fig_routing_nexthop()
    fig_nat64_dns64()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
