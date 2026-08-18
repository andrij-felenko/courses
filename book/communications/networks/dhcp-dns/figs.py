# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми DHCP і DNS."""

import os
import sys

# Підключаємо svgkit із теки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_dhcp_dora():
    """Фігура 1: Повний 4-етапний обмін DHCP DORA між клієнтом і сервером."""
    w, h = 820, 480
    frags = []

    # Колони клієнта і сервера
    c_x, s_x = 160, 660

    # Вертикальні лінії життя
    frags.append(line(c_x, 70, c_x, 430, color="#888888", sw=2, dash="5,5"))
    frags.append(line(s_x, 70, s_x, 430, color="#888888", sw=2, dash="5,5"))

    # Блоки сутностей
    frags.append(fitbox(c_x - 110, 20, 220, 45, "Клієнт (0.0.0.0:68)\nMAC: aa:bb:cc:11:22:33", size=12, bold=True, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(s_x - 110, 20, 220, 45, "DHCP-сервер (192.168.1.1:67)\nПул: 192.168.1.100 - 200", size=12, bold=True, fill="#e8f8f0", stroke=FIELD))

    # 1. DISCOVER
    y1 = 110
    frags.append(arrow(c_x, y1, s_x, y1 + 30, color=POS, sw=2))
    frags.append(fitbox(240, y1 - 25, 340, 45, "1. DHCPDISCOVER (Broadcast)\nSrc: 0.0.0.0:68 -> Dst: 255.255.255.255:67\nТранзакція xid, запит параметрів (опція 55)", size=11, fill="#fff5f5", stroke=POS))

    # 2. OFFER
    y2 = 190
    frags.append(arrow(s_x, y2, c_x, y2 + 30, color=FIELD, sw=2))
    frags.append(fitbox(240, y2 - 25, 340, 50, "2. DHCPOFFER (Пропозиція)\nПропонує IP: 192.168.1.105 (yiaddr)\nОренда: 86400с, Маска: /24, Шлюз: .1, DNS: 1.1.1.1", size=11, fill="#f0faf4", stroke=FIELD))

    # 3. REQUEST
    y3 = 280
    frags.append(arrow(c_x, y3, s_x, y3 + 30, color=POS, sw=2))
    frags.append(fitbox(240, y3 - 25, 340, 50, "3. DHCPREQUEST (Broadcast!)\nSrc: 0.0.0.0:68 -> Dst: 255.255.255.255:67\nОбрано Server ID: 192.168.1.1, Запит IP: .105", size=11, fill="#fff5f5", stroke=POS))

    # 4. ACK
    y4 = 370
    frags.append(arrow(s_x, y4, c_x, y4 + 30, color=FIELD, sw=2))
    frags.append(fitbox(240, y4 - 25, 340, 50, "4. DHCPACK (Підтвердження оренди)\nФіксація оренди: IP 192.168.1.105, T1=43200с, T2=75600с\nКлієнт перевіряє IP через ARP probe і вмикає стек", size=11, fill="#f0faf4", stroke=FIELD))

    render(os.path.join(IMG_DIR, "dhcp-dora.svg"), w, h, *frags)


def fig_dhcp_lease_timers():
    """Фігура 2: Життєвий цикл оренди DHCP та таймери T1 (50%), T2 (87.5%), T (100%)."""
    w, h = 860, 370
    frags = []

    # Заголовок / фон
    frags.append(fitbox(30, 15, 800, 38, "Життєвий цикл оренди DHCP (Lease Time T = 24 години)", size=13, bold=True, fill="#f4f6f8", stroke="#444444"))

    # Часова шкала (горизонтальна)
    x_start = 70
    x_end = 790
    y_bar = 145
    bar_w = x_end - x_start  # 720

    # Базова смуга
    frags.append(rect(x_start, y_bar, bar_w, 24, fill="#e5e7eb", stroke="#9ca3af", rx=4))

    # Секції смуги: 0..50% (зелена - спокійна оренда)
    w_t1 = bar_w * 0.50  # 360 -> x_t1 = 430
    frags.append(rect(x_start, y_bar, w_t1, 24, fill="#d1fae5", stroke=FIELD, rx=4))

    # 50%..87.5% (жовта/помаранчева - продовження)
    w_t2 = bar_w * 0.375  # 270 -> x_t2 = 700
    frags.append(rect(x_start + w_t1, y_bar, w_t2, 24, fill="#fef3c7", stroke="#d97706", rx=4))

    # 87.5%..100% (червона - аварійне переприв'язування)
    w_exp = bar_w * 0.125  # 90 -> x_end = 790
    frags.append(rect(x_start + w_t1 + w_t2, y_bar, w_exp, 24, fill="#fee2e2", stroke=POS, rx=4))

    # Позначки точок
    # 0%
    frags.append(circle(x_start, y_bar + 12, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(fitbox(x_start - 45, y_bar - 65, 95, 45, "0% (Старт)\nОтримано ACK", size=10, bold=True, fill="#e8f8f0", stroke=FIELD))

    # T1 = 50%
    x_t1 = x_start + w_t1
    frags.append(circle(x_t1, y_bar + 12, 6, fill="#d97706", stroke=INK, sw=1.5))
    frags.append(fitbox(x_t1 - 70, y_bar - 65, 140, 45, "T1 = 50% (12 год)\nUnicast запит оновлення", size=10, bold=True, fill="#fef3c7", stroke="#d97706"))

    # T2 = 87.5%
    x_t2 = x_start + w_t1 + w_t2
    frags.append(circle(x_t2, y_bar + 12, 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(fitbox(x_t2 - 75, y_bar - 65, 135, 45, "T2 = 87.5% (21 год)\nBroadcast переприв'язка", size=10, bold=True, fill="#fee2e2", stroke=POS))

    # 100%
    frags.append(circle(x_end, y_bar + 12, 6, fill="#111827", stroke=INK, sw=1.5))
    frags.append(fitbox(x_end - 25, y_bar - 65, 90, 45, "100% (24 год)\nКінець оренди", size=10, bold=True, fill="#f3f4f6", stroke="#4b5563"))

    # Пояснювальні картки знизу
    frags.append(fitbox(30, y_bar + 55, 245, 115, "Звичайна робота (0 - 50%):\nКлієнт спокійно використовує IP.\nЖодних запитів до мережі не\nнадсилається.", size=11, fill="#f0faf4", stroke=FIELD))
    frags.append(fitbox(305, y_bar + 55, 250, 115, "Оновлення T1 (50 - 87.5%):\nUnicast DHCPREQUEST до свого сервера.\nЯкщо сервер відповів DHCPACK —\nтаймери скидаються на 100%.", size=11, fill="#fffbeb", stroke="#d97706"))
    frags.append(fitbox(585, y_bar + 55, 245, 115, "Аварія T2 (87.5 - 100%):\nСвій сервер мовчить.\nBroadcast DHCPREQUEST до будь-якого\nсервера. На 100% — негайне\nскидання IP і повний DORA.", size=11, fill="#fff5f5", stroke=POS))

    render(os.path.join(IMG_DIR, "dhcp-lease-timers.svg"), w, h, *frags)


def fig_dns_hierarchy():
    """Фігура 3: Ієрархічне дерево простору доменних імен DNS."""
    w, h = 820, 420
    frags = []

    # Корінь
    root_x, root_y = 410, 45
    frags.append(fitbox(root_x - 120, root_y - 20, 240, 40, "Корінь DNS: «.» (Root Zone)\n13 серверних кластерів (A - M)", size=12, bold=True, fill="#fee2e2", stroke=POS))

    # Рівень 1: TLD
    tld_y = 145
    tld_nodes = [
        (130, "gTLD: «.com»\nРеєстр VeriSign", "#eaf0fd", NEG),
        (310, "gTLD: «.org»\nРеєстр PIR", "#eaf0fd", NEG),
        (500, "ccTLD: «.ua»\nРеєстр Hostmaster", "#fef3c7", "#d97706"),
        (690, "Спеціальний: «.arpa»\nЗворотний резолвінг", "#f3e8ff", "#7c3aed"),
    ]

    for nx, label, fill_c, strk_c in tld_nodes:
        frags.append(line(root_x, root_y + 20, nx, tld_y - 20, color="#9ca3af", sw=1.5))
        frags.append(fitbox(nx - 85, tld_y - 20, 170, 45, label, size=11, bold=True, fill=fill_c, stroke=strk_c))

    # Рівень 2: Авторитетні зони 2-го рівня (SLD)
    sld_y = 250
    sld_nodes = [
        (90, 130, "«example.com»\nАвторитетні NS", "#f0faf4", FIELD),
        (240, 130, "«google.com»\nАвторитетні NS", "#f0faf4", FIELD),
        (380, 310, "«wikipedia.org»\nАвторитетні NS", "#f0faf4", FIELD),
        (530, 500, "«gov.ua»\nПублічний домен", "#fef9c3", "#ca8a04"),
        (710, 690, "«in-addr.arpa»\nЗворотні IP-дерева", "#ede9fe", "#6d28d9"),
    ]

    for nx, parent_x, label, fill_c, strk_c in sld_nodes:
        frags.append(line(parent_x, tld_y + 25, nx, sld_y - 20, color="#9ca3af", sw=1.5))
        frags.append(fitbox(nx - 70, sld_y - 20, 140, 45, label, size=11, bold=True, fill=fill_c, stroke=strk_c))

    # Рівень 3: Листові записи та піддомени
    leaf_y = 355
    leaf_nodes = [
        (90, 90, "www.example.com\nA: 93.184.216.34", "#ffffff", INK),
        (240, 240, "mail.google.com\nMX: 10 smtp...", "#ffffff", INK),
        (380, 380, "uk.wikipedia.org\nCNAME: dyna...", "#ffffff", INK),
        (530, 530, "diia.gov.ua\nAAAA: 2a02:...", "#ffffff", INK),
        (710, 710, "1.168.192.in-addr.arpa\nPTR: router.lan", "#ffffff", INK),
    ]

    for nx, parent_x, label, fill_c, strk_c in leaf_nodes:
        frags.append(line(parent_x, sld_y + 25, nx, leaf_y - 20, color="#9ca3af", sw=1.5, dash="3,3"))
        frags.append(fitbox(nx - 75, leaf_y - 20, 150, 45, label, size=10, fill=fill_c, stroke=strk_c))

    render(os.path.join(IMG_DIR, "dns-hierarchy.svg"), w, h, *frags)


def fig_dns_resolution_flow():
    """Фігура 4: Повний шлях резолвінгу DNS (рекурсивний запит клієнта + ітеративний обхід дерева)."""
    w, h = 840, 480
    frags = []

    # Сутності: Клієнт (ліворуч), Резолвер (посередині), Ієрархія серверів (праворуч)
    # Клієнт
    frags.append(fitbox(30, 200, 150, 60, "Клієнт (Stub Resolver)\nБраузер / ОС\n192.168.1.105", size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    # Рекурсивний резолвер
    frags.append(fitbox(250, 180, 180, 95, "Рекурсивний резолвер\n(ISP або 1.1.1.1 / 8.8.8.8)\n1. Перевіряє власний кеш\n2. Виконує ітерації\n3. Кешує результат", size=11, bold=True, fill="#fef3c7", stroke="#d97706"))

    # Сервери праворуч
    frags.append(fitbox(550, 30, 260, 55, "1. Root Server («.»)\n«Я не знаю адресу example.com,\nале запитай TLD сервер .com»", size=11, bold=True, fill="#fee2e2", stroke=POS))

    frags.append(fitbox(550, 175, 260, 55, "2. TLD Server («.com»)\n«Я не знаю IP самого сайту,\nале ось авторитетний NS ns1.example.com»", size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    frags.append(fitbox(550, 320, 260, 65, "3. Авторитетний NS (example.com)\n«Ось точна відповідь (AA):\nA = 93.184.216.34\nTTL = 3600 секунд»", size=11, bold=True, fill="#f0faf4", stroke=FIELD))

    # Стрілки клієнт <-> Резолвер (Рекурсивний запит)
    frags.append(arrow(180, 220, 250, 220, color=NEG, sw=2))
    frags.append(fitbox(182, 185, 66, 30, "Запит", size=10, bold=True, fill="#ffffff", stroke=NEG))

    frags.append(arrow(250, 250, 180, 250, color=FIELD, sw=2))
    frags.append(fitbox(182, 255, 66, 30, "IP-адреса", size=10, bold=True, fill="#ffffff", stroke=FIELD))

    # Ітеративні стрілки Резолвер <-> Сервери
    # До Root
    frags.append(arrow(430, 195, 550, 55, color="#d97706", sw=1.8))
    frags.append(arrow(550, 70, 430, 210, color="#9ca3af", sw=1.5))

    # До TLD
    frags.append(arrow(430, 225, 550, 195, color="#d97706", sw=1.8))
    frags.append(arrow(550, 210, 430, 240, color="#9ca3af", sw=1.5))

    # До Authoritative
    frags.append(arrow(430, 255, 550, 335, color="#d97706", sw=1.8))
    frags.append(arrow(550, 360, 430, 270, color=FIELD, sw=2))

    # Нижній пояснювальний блок
    frags.append(fitbox(30, 410, 780, 45, "Рекурсивний запит (ліворуч): «Знайди мені IP або поверни помилку».\nІтеративні запити (праворуч): «Я не знаю остаточної IP, але звернись за цією делегованою адресою».", size=11, fill="#f4f6f8", stroke="#4b5563"))

    render(os.path.join(IMG_DIR, "dns-resolution-flow.svg"), w, h, *frags)


def fig_reverse_dns_tree():
    """Фігура 5: Зворотний DNS-резолвінг та інверсія октетів у дереві in-addr.arpa."""
    w, h = 820, 380
    frags = []

    # Верхній блок порівняння: Прямий IP проти доменного запису
    frags.append(fitbox(40, 25, 360, 65, "Пряма IP-адреса хоста:\n198 . 51 . 100 . 42\n(Мережа -> Підмережа -> Вузол)", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    frags.append(fitbox(420, 25, 360, 65, "Зворотне доменне ім'я (FQDN PTR):\n42 . 100 . 51 . 198 . in-addr . arpa .\n(Вузол <- Підмережа <- Мережа <- Корінь)", size=12, bold=True, fill="#f0faf4", stroke=FIELD))

    # Дерево делегування PTR
    y_root = 130
    frags.append(fitbox(330, y_root, 160, 35, "Корінь DNS: «.»", size=11, bold=True, fill="#fee2e2", stroke=POS))

    y_arpa = 190
    frags.append(line(410, y_root + 35, 410, y_arpa, color="#9ca3af", sw=1.5))
    frags.append(fitbox(330, y_arpa, 160, 35, "домен «arpa.»", size=11, bold=True, fill="#f3e8ff", stroke="#7c3aed"))

    y_inaddr = 250
    frags.append(line(410, y_arpa + 35, 410, y_inaddr, color="#9ca3af", sw=1.5))
    frags.append(fitbox(310, y_inaddr, 200, 35, "зона «in-addr.arpa.»", size=11, bold=True, fill="#ede9fe", stroke="#6d28d9"))

    # Октети (розгалуження)
    y_net = 315
    octets = [
        (120, "«198.»\n(Клас / Регіон)", "#fef3c7", "#d97706"),
        (310, "«51.»\n(Провайдер)", "#fef3c7", "#d97706"),
        (510, "«100.»\n(Підмережа клієнта)", "#fef3c7", "#d97706"),
        (700, "«42» (PTR)\n-> host.example.com", "#f0faf4", FIELD),
    ]

    prev_x = 410
    frags.append(line(prev_x, y_inaddr + 35, 120, y_net - 15, color="#9ca3af", sw=1.5))
    frags.append(line(120, y_net + 30, 310, y_net - 15, color="#9ca3af", sw=1.5, dash="3,3"))
    frags.append(line(310, y_net + 30, 510, y_net - 15, color="#9ca3af", sw=1.5, dash="3,3"))
    frags.append(line(510, y_net + 30, 700, y_net - 15, color=FIELD, sw=2))

    for nx, label, fill_c, strk_c in octets:
        frags.append(fitbox(nx - 75, y_net - 15, 150, 45, label, size=10, bold=True, fill=fill_c, stroke=strk_c))

    render(os.path.join(IMG_DIR, "reverse-dns-tree.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_dhcp_dora()
    fig_dhcp_lease_timers()
    fig_dns_hierarchy()
    fig_dns_resolution_flow()
    fig_reverse_dns_tree()
    print("Всі фігури згенеровано успішно.")
