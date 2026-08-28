# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми vidkryty-dzherela-naprykintsi-zhyttia.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
BG_OK     = "#eaf5ea"  # Світло-зелений (Успішне відкриття / Вільний код)
BORDER_OK = "#27ae60"
BG_WARN   = "#fff7ed"  # Світло-помаранчевий (Обмеження / Блоби / HAL)
BORDER_WARN = "#ea580c"
BG_ERR    = "#fef2f2"  # Світло-червоний (Заблоковане залізо / eFuses / Хмара)
BORDER_ERR  = "#dc2626"
BG_BLUE   = "#eef2ff"  # Світло-синій (Завантажувач / Перехідні механізми)
BORDER_BLUE = "#2563eb"
BG_PANEL  = "#f8fafc"  # Світло-сірий фон панелей
BORDER_PANEL = "#64748b"


def fig1_eol_open_sourcing_stages():
    """Фігура 1: Етапи відкриття джерел при EOL та чотири критичні бар'єри."""
    w, h = 960, 520
    parts = []

    parts.append(text(w / 2, 28, "Анатомія EOL-відкриття коду: що вирішує публікація і де виникають бар'єри", size=15, bold=True))

    # Стовпчик 1: Первинний вихідний код
    parts.append(rect(30, 60, 210, 430, fill=BG_PANEL, stroke=BORDER_PANEL, sw=1.8, rx=8))
    parts.append(text(135, 88, "1. Кодова база вендора", size=13, color=INK, bold=True))
    parts.append(text(135, 108, "(Внутрішній стан)", size=11, color=MUTED))
    parts.append(line(45, 120, 225, 120, color=BORDER_PANEL, sw=1, dash="2,2"))

    parts.append(fitbox(45, 135, 180, 75, "Власна бізнес-логіка:\n• Демони керування\n• WebUI / REST API\n• 10–20% коду", size=11, fill="#ffffff", stroke=BORDER_PANEL))
    parts.append(fitbox(45, 220, 180, 85, "Сторонній код SoC:\n• SDK чипмейкера\n• Wi-Fi / BLE стеки\n• DSP / NPU мікрокод\n• Закрито під NDA", size=11, fill=BG_WARN, stroke=BORDER_WARN))
    parts.append(fitbox(45, 315, 180, 75, "Хмарна прив'язка:\n• AWS / MQTT токени\n• Сертифікати mTLS\n• Жорсткий бекенд", size=11, fill=BG_ERR, stroke=BORDER_ERR))
    parts.append(fitbox(45, 400, 180, 75, "Secure Boot підпис:\n• Приватний RSA ключ\n• Прив'язка до eFuse\n• Тільки реліз-білди", size=11, fill=BG_ERR, stroke=BORDER_ERR))

    # Стрілка 1->2
    parts.append(arrow(245, 275, 275, 275, color=BORDER_WARN, sw=2))

    # Стовпчик 2: Юридичне очищення (IP Scrubbing)
    parts.append(rect(280, 60, 205, 430, fill=BG_WARN, stroke=BORDER_WARN, sw=1.8, rx=8))
    parts.append(text(382, 88, "2. IP Scrubbing", size=13, color=BORDER_WARN, bold=True))
    parts.append(text(382, 108, "(Юридична фільтрація)", size=11, color=MUTED))
    parts.append(line(295, 120, 470, 120, color=BORDER_WARN, sw=1, dash="2,2"))

    parts.append(fitbox(295, 135, 175, 75, "Видалення NDA коду:\n• Вирізання вихідників\n• Залишення .bin / .o\n• Втрата коментарів", size=11, fill="#ffffff", stroke=BORDER_WARN))
    parts.append(fitbox(295, 220, 175, 85, "Пастка бінарних блобів:\n• Прив'язка до ядра 4.4\n• Застарілий toolchain\n• Неможливість патчити\n  вразливості в HAL", size=11, fill=BG_ERR, stroke=BORDER_ERR))
    parts.append(fitbox(295, 315, 175, 75, "Ліцензійні ризики:\n• Порушення ліцензій\n  GPL при змішуванні\n• Ризик позовів IP", size=11, fill="#ffffff", stroke=BORDER_WARN))
    parts.append(fitbox(295, 400, 175, 75, "Результат тарболу:\nПублікація 10% коду\nта купа мертвих блобів", size=11, fill=BG_WARN, stroke=BORDER_WARN))

    # Стрілка 2->3
    parts.append(arrow(490, 275, 520, 275, color=BORDER_ERR, sw=2))

    # Стовпчик 3: Залізо та криптографічний глухий кут
    parts.append(rect(525, 60, 200, 430, fill=BG_ERR, stroke=BORDER_ERR, sw=1.8, rx=8))
    parts.append(text(625, 88, "3. Апаратний глухий кут", size=13, color=BORDER_ERR, bold=True))
    parts.append(text(625, 108, "(eFuses та Cloud)", size=11, color=MUTED))
    parts.append(line(540, 120, 710, 120, color=BORDER_ERR, sw=1, dash="2,2"))

    parts.append(fitbox(540, 135, 170, 85, "Блокування Secure Boot:\n• BootROM відхиляє\n  непідписані збірки\n• eFuses не скидаються\n• Залізо окирпічено", size=11, fill="#ffffff", stroke=BORDER_ERR))
    parts.append(fitbox(540, 230, 170, 85, "Вимкнення серверів:\n• DNS/NTP не відповідає\n• Хмара вендора офлайн\n• Помилка авторизації\n  і вічний перезапуск", size=11, fill="#ffffff", stroke=BORDER_ERR))
    parts.append(fitbox(540, 325, 170, 75, "Регуляторний блок:\n• Без радіо-блобів\n  Wi-Fi/BLE не працює\n• Порушення FCC/RED", size=11, fill="#ffffff", stroke=BORDER_ERR))
    parts.append(fitbox(540, 410, 170, 65, "Підсумок наївності:\nВідкритий код є,\nале пристрій — сміття", size=11, fill=BG_ERR, stroke=BORDER_ERR))

    # Стрілка 3->4
    parts.append(arrow(730, 275, 760, 275, color=BORDER_OK, sw=2))

    # Стовпчик 4: Повний інженерний EOL-пакет
    parts.append(rect(765, 60, 165, 430, fill=BG_OK, stroke=BORDER_OK, sw=1.8, rx=8))
    parts.append(text(847, 88, "4. Чесний EOL-пакет", size=13, color=BORDER_OK, bold=True))
    parts.append(text(847, 108, "(Життя у спільноті)", size=11, color=MUTED))
    parts.append(line(775, 120, 920, 120, color=BORDER_OK, sw=1, dash="2,2"))

    parts.append(fitbox(775, 135, 145, 80, "Unlock Bootloader:\nОфіційно підписаний\nU-Boot, що дозволяє\nзапуск будь-яких ядер", size=10, fill="#ffffff", stroke=BORDER_OK))
    parts.append(fitbox(775, 225, 145, 75, "Local-First бекенд:\nMQTT / Home Assistant\nfallback без хмари", size=10, fill="#ffffff", stroke=BORDER_OK))
    parts.append(fitbox(775, 310, 145, 80, "Відкриті HAL-драйвери:\nРегістрові карти та\nконтейнерний білд\nвідтворюваного образу", size=10, fill="#ffffff", stroke=BORDER_OK))
    parts.append(fitbox(775, 400, 145, 75, "Результат:\nПовноцінне друге\nжиття виробу [✓]", size=11, fill=BG_OK, stroke=BORDER_OK))

    render(os.path.join(OUT, "eol-open-sourcing-stages.svg"), w, h, *parts)


def fig2_secure_boot_unlock_architecture():
    """Фігура 2: Архітектура переходу від закритого Secure Boot до відкритого коду."""
    w, h = 940, 500
    parts = []

    parts.append(text(w / 2, 28, "Архітектура розблокування Secure Boot: перехідний завантажувач та обхід верифікації", size=15, bold=True))

    # Ліва частина: Заводський закритий режим
    parts.append(rect(40, 60, 410, 410, fill=BG_PANEL, stroke=BORDER_PANEL, sw=1.8, rx=8))
    parts.append(text(245, 88, "Заводський Secure Boot (Виробництво)", size=13, color=BORDER_ERR, bold=True))
    parts.append(line(55, 105, 435, 105, color=BORDER_PANEL, sw=1, dash="2,2"))

    parts.append(fitbox(60, 120, 370, 65, "1. Апаратний BootROM:\nЗчитує eFuses (SRK Hash) -> Перевіряє підпис SPL вендора", size=11, fill="#ffffff", stroke=BORDER_PANEL))
    parts.append(arrow(245, 185, 245, 205, color=BORDER_PANEL, sw=1.5))

    parts.append(fitbox(60, 205, 370, 65, "2. Заводський U-Boot (Підписаний RSA-2048/4096):\nІніціалізує DDR RAM -> Перевіряє RSA-підпис образу `fitImage`", size=11, fill="#ffffff", stroke=BORDER_PANEL))
    parts.append(arrow(245, 270, 245, 290, color=BORDER_ERR, sw=1.5))

    parts.append(fitbox(60, 290, 370, 75, "3. Перевірка ядра Linux та DTB:\nЯкщо геш або цифровий підпис не збігаються:\n`panic(\"Signature verification failed: CPU Halted\")`", size=11, fill=BG_ERR, stroke=BORDER_ERR))
    parts.append(arrow(245, 365, 245, 385, color=BORDER_ERR, sw=1.5))

    parts.append(fitbox(60, 385, 370, 65, "Результат спроби запуску модифікованого ядра:\nПроцесор зупиняється, сторонній код блокується [✗]", size=11, fill="#ffffff", stroke=BORDER_ERR))

    # Права частина: Перехідний завантажувач EOL
    parts.append(rect(490, 60, 410, 410, fill=BG_OK, stroke=BORDER_OK, sw=1.8, rx=8))
    parts.append(text(695, 88, "EOL Transition Bootloader (Розблокований режим)", size=13, color=BORDER_OK, bold=True))
    parts.append(line(505, 105, 885, 105, color=BORDER_OK, sw=1, dash="2,2"))

    parts.append(fitbox(510, 120, 370, 65, "1. Апаратний BootROM (Незмінний кремній):\nУспішно валідує підпис фінального перехідного SPL вендора [✓]", size=11, fill="#ffffff", stroke=BORDER_OK))
    parts.append(arrow(695, 185, 695, 205, color=BORDER_BLUE, sw=1.5))

    parts.append(fitbox(510, 205, 370, 75, "2. Перехідний U-Boot (Freedom Payload, підписаний вендором):\n• Деактивує прапорець перевірки `CONFIG_FIT_SIGNATURE`\n• Вмикає завантаження з SD-карти, eMMC або TFTP", size=11, fill=BG_BLUE, stroke=BORDER_BLUE))
    parts.append(arrow(695, 280, 695, 300, color=BORDER_OK, sw=1.5))

    parts.append(fitbox(510, 300, 370, 75, "3. Завантаження кастомного ядра спільноти:\n• Підтримка сучасних ядер Linux 6.x та OpenWrt/Yocto\n• Заміна хмарних демонів на локальні сервіси", size=11, fill="#ffffff", stroke=BORDER_OK))
    parts.append(arrow(695, 375, 695, 395, color=BORDER_OK, sw=1.5))

    parts.append(fitbox(510, 395, 370, 60, "Результат для власника пристрою:\nПовний контроль над залізом без порушення eFuses [✓]", size=11, fill=BG_OK, stroke=BORDER_OK))

    render(os.path.join(OUT, "secure-boot-unlock-architecture.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_eol_open_sourcing_stages()
    fig2_secure_boot_unlock_architecture()
    print("Векторні фігури успішно згенеровано у папці img/")
