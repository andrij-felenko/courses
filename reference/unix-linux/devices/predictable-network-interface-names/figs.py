#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схем для статті про передбачувані імена мережевих інтерфейсів."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_race_condition():
    """Схема 1: Стан гонитви під час асинхронної ініціалізації мережевих інтерфейсів."""
    w, h = 880, 430
    frags = []

    # Заголовок секції
    frags.append(text(w / 2, 28, "Стан гонитви при паралельній реєстрації eth0 / eth1", size=16, bold=True))

    # Стовпчик 1: Завантаження A
    frags.append(rect(30, 55, 390, 345, fill="#f9fbfd", stroke="#b0c4de", sw=1.2, rx=8))
    frags.append(text(225, 80, "Завантаження №1 (порядок A)", size=14, bold=True, color="#1e3a8a"))

    # Карта 1
    frags.append(fitbox(50, 105, 160, 48, "NIC 1 (Слот PCI 1)\nЗовнішня мережа (WAN)", size=11, fill="#e8f4fd", stroke="#3b82f6"))
    # Карта 2
    frags.append(fitbox(240, 105, 160, 48, "NIC 2 (Слот PCI 2)\nЛокальна мережа (LAN)", size=11, fill="#fef3c7", stroke="#d97706"))

    # Потоки ядра
    frags.append(fitbox(50, 180, 160, 42, "Потік ядра 1: probe()\nЗавершився за 12 мс", size=11, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(240, 180, 160, 42, "Потік ядра 2: probe()\nЗавершився за 19 мс", size=11, fill="#ffffff", stroke="#94a3b8"))
    frags.append(arrow(130, 153, 130, 180, color="#3b82f6"))
    frags.append(arrow(320, 153, 320, 180, color="#d97706"))

    # Реєстрація імен
    frags.append(fitbox(50, 245, 160, 45, "register_netdevice()\nОтримує: eth0", size=12, bold=True, fill="#dcfce7", stroke="#16a34a"))
    frags.append(fitbox(240, 245, 160, 45, "register_netdevice()\nОтримує: eth1", size=12, bold=True, fill="#fee2e2", stroke="#dc2626"))
    frags.append(arrow(130, 222, 130, 245, color="#16a34a"))
    frags.append(arrow(320, 222, 320, 245, color="#dc2626"))

    # Наслідок для фаєрвола
    frags.append(fitbox(50, 310, 350, 70, "Правило: iptables -A FORWARD -i eth0 -j DROP\nРезультат: Захищено! Зовнішній WAN (eth0) фільтрується,\nлокальний LAN (eth1) передає дані.", size=11, fill="#f0fdf4", stroke="#22c55e"))


    # Стовпчик 2: Завантаження B
    frags.append(rect(460, 55, 390, 345, fill="#fdfaf6", stroke="#fed7aa", sw=1.2, rx=8))
    frags.append(text(655, 80, "Завантаження №2 (порядок B — збій)", size=14, bold=True, color="#9a3412"))

    # Карта 1
    frags.append(fitbox(480, 105, 160, 48, "NIC 1 (Слот PCI 1)\nЗовнішня мережа (WAN)", size=11, fill="#e8f4fd", stroke="#3b82f6"))
    # Карта 2
    frags.append(fitbox(670, 105, 160, 48, "NIC 2 (Слот PCI 2)\nЛокальна мережа (LAN)", size=11, fill="#fef3c7", stroke="#d97706"))

    # Потоки ядра
    frags.append(fitbox(480, 180, 160, 42, "Потік ядра 1: probe()\nЗатримався (21 мс)", size=11, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(670, 180, 160, 42, "Потік ядра 2: probe()\nФінішував першим (11 мс)", size=11, fill="#ffffff", stroke="#94a3b8"))
    frags.append(arrow(560, 153, 560, 180, color="#3b82f6"))
    frags.append(arrow(750, 153, 750, 180, color="#d97706"))

    # Реєстрація імен переплутана
    frags.append(fitbox(480, 245, 160, 45, "register_netdevice()\nОтримує: eth1", size=12, bold=True, fill="#fee2e2", stroke="#dc2626"))
    frags.append(fitbox(670, 245, 160, 45, "register_netdevice()\nОтримує: eth0", size=12, bold=True, fill="#dcfce7", stroke="#16a34a"))
    frags.append(arrow(560, 222, 560, 245, color="#dc2626"))
    frags.append(arrow(750, 222, 750, 245, color="#16a34a"))

    # Наслідок аварії
    frags.append(fitbox(480, 310, 350, 70, "Правило: iptables -A FORWARD -i eth0 -j DROP\nАварія: Заблоковано локальний LAN (став eth0)!\nЗовнішній WAN (став eth1) відкритий без захисту.", size=11, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    render(os.path.join(OUT_DIR, "race-condition-probing.svg"), w, h, *frags)


def fig_naming_pipeline():
    """Схема 2: Пайплайн роботи udev та systemd для призначення передбачуваного імені."""
    w, h = 900, 440
    frags = []

    frags.append(text(w / 2, 28, "Пайплайн призначення імені мережевого інтерфейсу в udev", size=16, bold=True))

    # Крок 1: Ядро
    frags.append(fitbox(30, 60, 240, 100, "1. Простір ядра (Linux Kernel)\n• Драйвер виявляє контролер\n• Реєстрація: alloc_netdev_mqs()\n• Тимчасове ім'я ядра: eth0\n• Подія uevent (ACTION=add)", size=11, fill="#e0f2fe", stroke="#0284c7"))

    # Стрілка 1 -> 2
    frags.append(arrow(270, 110, 330, 110, color="#0284c7"))
    frags.append(text(300, 100, "netlink", size=10, color="#0369a1"))

    # Крок 2: systemd-udevd та net_id
    frags.append(fitbox(330, 60, 260, 130, "2. udev: правило 80-net-setup-link\n• IMPORT{builtin}=\"net_id\"\n• Зчитування топології з sysfs:\n  - DMI/SMBIOS: ID_NET_NAME_ONBOARD=eno1\n  - PCI Slot: ID_NET_NAME_SLOT=ens1\n  - PCI Path: ID_NET_NAME_PATH=enp3s0\n  - MAC: ID_NET_NAME_MAC=enx78e7d1...", size=10, fill="#fef9c3", stroke="#ca8a04"))

    # Крок 3: Політика .link
    frags.append(fitbox(640, 60, 230, 130, "3. Обробка політик (.link)\n• IMPORT{builtin}=\"net_setup_link\"\n• 99-default.link:\n  NamePolicy=onboard slot path mac\n• Вибір першого валідного кандидата:\n  ID_NET_NAME=\"enp3s0\"", size=10, fill="#f3e8ff", stroke="#9333ea"))

    # Стрілка 2 -> 3
    frags.append(arrow(590, 120, 640, 120, color="#ca8a04"))

    # Стрілка 3 -> 4 вниз
    frags.append(arrow(755, 190, 755, 235, color="#9333ea"))
    frags.append(text(760, 215, "Вибір: enp3s0", size=10, anchor="start", color="#7e22ce"))

    # Крок 4: Перейменування в ядрі через RTNetlink
    frags.append(fitbox(490, 235, 380, 85, "4. Виконання перейменування (udev daemon)\n• Перевірка: інтерфейс перебуває в стані DOWN\n• Системний виклик: RTM_SETLINK (IFLA_IFNAME=\"enp3s0\")\n• Ядро надсилає у відповідь: uevent (ACTION=move, DEVPATH=...)\n• Створення альтернативних імен (IFLA_ALT_IFNAME)", size=10, fill="#ecfdf5", stroke="#059669"))

    # Стрілка 4 -> 5 вліво
    frags.append(arrow(490, 277, 410, 277, color="#059669"))

    # Крок 5: Диспетчери мережі
    frags.append(fitbox(30, 235, 380, 85, "5. Готовий інтерфейс для конфігурації\n• NetworkManager / systemd-networkd / ifupdown\n• Застосування IP, маршрутів та правил фаєрвола\n• Переведення інтерфейсу в стан UP (IFF_UP)\n• Фіксація сталого імені enp3s0 між перезавантаженнями", size=10, fill="#f8fafc", stroke="#475569"))

    # Примітка внизу
    frags.append(rect(30, 345, 840, 70, fill="#fffbeb", stroke="#f59e0b", sw=1, rx=6))
    frags.append(text(450, 368, "Ключова вимога: перейменування виконується ДО активації інтерфейсу (стан DOWN)", size=12, bold=True, color="#b45309"))
    frags.append(text(450, 393, "Якщо інтерфейс уже піднятий (UP), ядро повертає помилку -EBUSY на запит RTM_SETLINK", size=11, color="#78350f"))

    render(os.path.join(OUT_DIR, "naming-pipeline-udev.svg"), w, h, *frags)


def fig_name_structure():
    """Схема 3: Анатомія та розбір складових частин передбачуваних імен."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Анатомія та структури передбачуваних імен мережевих інтерфейсів", size=16, bold=True))

    # Схема 1: eno1
    frags.append(rect(30, 55, 395, 100, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(45, 78, "1. Вбудований контролер (Onboard Index / ACPI / DMI Type 41):", size=11, bold=True, anchor="start", color="#166534"))
    frags.append(fitbox(45, 92, 55, 45, "en\nEthernet", size=11, fill="#dcfce7", stroke="#22c55e", bold=True))
    frags.append(fitbox(108, 92, 45, 45, "o\nonboard", size=11, fill="#dcfce7", stroke="#22c55e", bold=True))
    frags.append(fitbox(161, 92, 45, 45, "1\nіндекс", size=11, fill="#dcfce7", stroke="#22c55e", bold=True))
    frags.append(text(220, 115, "→ eno1 (порт 1 на материнській платі)", size=11, anchor="start", color="#14532d"))

    # Схема 2: ens1f0
    frags.append(rect(455, 55, 395, 100, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(470, 78, "2. Слот розширення PCI Express Hotplug (PCIe Slot):", size=11, bold=True, anchor="start", color="#1e40af"))
    frags.append(fitbox(470, 92, 45, 45, "en\nEth", size=10, fill="#dbeafe", stroke="#3b82f6", bold=True))
    frags.append(fitbox(520, 92, 40, 45, "s\nslot", size=10, fill="#dbeafe", stroke="#3b82f6", bold=True))
    frags.append(fitbox(565, 92, 40, 45, "1\nслот 1", size=10, fill="#dbeafe", stroke="#3b82f6", bold=True))
    frags.append(fitbox(610, 92, 50, 45, "f0\nфункція", size=10, fill="#dbeafe", stroke="#3b82f6", bold=True))
    frags.append(text(670, 115, "→ ens1f0 (фізичний слот 1, порт 0)", size=11, anchor="start", color="#1e3a8a"))

    # Схема 3: enp3s0
    frags.append(rect(30, 170, 395, 105, fill="#fdf4ff", stroke="#f0abfc", sw=1.2, rx=6))
    frags.append(text(45, 193, "3. Топологічне розташування на шині PCI (PCI Bus Path):", size=11, bold=True, anchor="start", color="#86198f"))
    frags.append(fitbox(45, 207, 45, 45, "en\nEth", size=10, fill="#fae8ff", stroke="#d946ef", bold=True))
    frags.append(fitbox(95, 207, 45, 45, "p3\nшина 3", size=10, fill="#fae8ff", stroke="#d946ef", bold=True))
    frags.append(fitbox(145, 207, 45, 45, "s0\nслот 0", size=10, fill="#fae8ff", stroke="#d946ef", bold=True))
    frags.append(fitbox(195, 207, 45, 45, "f0\nфункц.", size=10, fill="#fae8ff", stroke="#d946ef", bold=True))
    frags.append(text(250, 230, "→ enp3s0 (шина 03:00.0)", size=11, anchor="start", color="#701a75"))

    # Схема 4: enp0s20f0u1c2
    frags.append(rect(455, 170, 395, 105, fill="#fff7ed", stroke="#fdba74", sw=1.2, rx=6))
    frags.append(text(470, 193, "4. Топологія USB-адаптера (USB Port Chain):", size=11, bold=True, anchor="start", color="#9a3412"))
    frags.append(fitbox(470, 207, 50, 45, "en\nEth", size=10, fill="#ffedd5", stroke="#f97316", bold=True))
    frags.append(fitbox(525, 207, 75, 45, "p0s20f0\nUSB-хост", size=9, fill="#ffedd5", stroke="#f97316", bold=True))
    frags.append(fitbox(605, 207, 45, 45, "u1\nпорт 1", size=10, fill="#ffedd5", stroke="#f97316", bold=True))
    frags.append(fitbox(655, 207, 45, 45, "c2\nконфіг", size=10, fill="#ffedd5", stroke="#f97316", bold=True))
    frags.append(text(710, 230, "→ enp0s20f0u1c2", size=11, anchor="start", color="#7c2d12"))

    # Схема 5: enx78e7d1ea46da
    frags.append(rect(30, 290, 820, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(45, 313, "5. Іменування за MAC-адресою (Globally Administered MAC Address):", size=11, bold=True, anchor="start", color="#334155"))
    frags.append(fitbox(45, 327, 60, 48, "en\nEthernet", size=11, fill="#f1f5f9", stroke="#64748b", bold=True))
    frags.append(fitbox(115, 327, 45, 48, "x\nMAC", size=11, fill="#f1f5f9", stroke="#64748b", bold=True))
    frags.append(fitbox(170, 327, 240, 48, "78e7d1ea46da\nШість байтів MAC (78:e7:d1:ea:46:da)", size=11, fill="#f1f5f9", stroke="#64748b", bold=True))
    frags.append(text(430, 352, "→ enx78e7d1ea46da (жорстка прив'язка до чіпа, зручно для знімних адаптерів)", size=11, anchor="start", color="#1e293b"))

    render(os.path.join(OUT_DIR, "name-structure-breakdown.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_race_condition()
    fig_naming_pipeline()
    fig_name_structure()
    print("Усі фігури успішно згенеровано.")
