# -*- coding: utf-8 -*-
"""Фігури для статті shchob-vyrib-zhyv-bez-nas («Щоб виріб жив без нас»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. local-first-resilience: Хмарозалежність проти Local-First ─────────────
def fig_local_first_resilience():
    W, H = 840, 420
    p = []

    # Загальний фон
    p.append(rect(10, 10, 820, 400, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))

    # Ліва колонка: Хмарозалежний пристрій (Cloud-Tethered Trap)
    p.append(rect(30, 35, 370, 360, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(215, 65, "Хмарозалежний виріб (Cloud-Tethered)", size=13, color=POS, bold=True, anchor="middle"))

    # Блоки всередині лівої колонки
    p.append(rect(50, 95, 330, 55, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 120, "Хмарний бекенд / Пропрієтарний сервер", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(215, 138, "TLS Endpoint, пропрієтарний протокол", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(215, 150, 215, 185, color=POS, sw=1.5))
    p.append(text(215, 172, "WAN Інтернет", size=10, color=POS, bold=True, anchor="middle"))

    p.append(rect(50, 185, 330, 80, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(215, 210, "Мікроконтролер: Тонкий клієнт", size=11, color=INK, bold=True, anchor="middle"))
    p.append(text(215, 230, "Вся логіка на сервері, локального API немає", size=10, color=MUTED, anchor="middle"))
    p.append(text(215, 248, "Опитування хмари (Long Polling / WebSockets)", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(215, 265, 215, 295, color=INK, sw=1.5))

    p.append(rect(50, 295, 330, 45, fill="#edf2f7", stroke=INK, sw=1.0, rx=4))
    p.append(text(215, 323, "Апаратна частина: Реле / Давачі", size=11, color=INK, bold=True, anchor="middle"))

    # Підсумок лівої колонки при EOL
    p.append(rect(50, 350, 330, 35, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    p.append(text(215, 372, "Вимкнення серверів -> ПРИСТРІЙ ПЕРЕТВОРЮЄТЬСЯ НА ЦЕГЛИНУ", size=9, color=POS, bold=True, anchor="middle"))

    # Права колонка: Local-First Resilient Architecture
    p.append(rect(430, 35, 380, 360, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(620, 65, "Автономна архітектура (Local-First)", size=13, color=FIELD, bold=True, anchor="middle"))

    # Локальні клієнти
    p.append(rect(450, 95, 340, 55, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(620, 118, "Локальні клієнти (Home Assistant, Додаток)", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text(620, 136, "mDNS / Local MQTT / HTTP REST / BLE GATT", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(620, 150, 620, 185, color=FIELD, sw=1.5))
    p.append(text(620, 172, "Локальна мережа (LAN / BLE)", size=10, color=FIELD, bold=True, anchor="middle"))

    # Мікроконтролер Local-First
    p.append(rect(450, 185, 340, 90, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(620, 208, "Мікроконтролер: Автономна система", size=11, color=INK, bold=True, anchor="middle"))
    p.append(text(620, 226, "Внутрішній автомат станів + розклад у Flash", size=10, color=MUTED, anchor="middle"))
    p.append(text(620, 244, "Локальний диспетчер відкритих протоколів", size=10, color=MUTED, anchor="middle"))
    p.append(text(620, 262, "Хмарний міст (опціональний шар поверх LAN)", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(620, 275, 620, 300, color=INK, sw=1.5))

    p.append(rect(450, 300, 340, 40, fill="#edf2f7", stroke=INK, sw=1.0, rx=4))
    p.append(text(620, 325, "Апаратна частина: Реле / Давачі", size=11, color=INK, bold=True, anchor="middle"))

    # Підсумок правої колонки при EOL
    p.append(rect(450, 350, 340, 35, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(620, 372, "Вимкнення серверів -> ПОВНА РОБОТОЗДАТНІСТЬ БЕЗ ЗМІН", size=9, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "local-first-resilience.svg"), W, H, *p)


# ── 2. eol-bootloader-unlock: Криптографічне розблокування завантажувача ────
def fig_eol_bootloader_unlock():
    W, H = 840, 440
    p = []

    p.append(rect(10, 10, 820, 420, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(420, 38, "Криптографічне розблокування завантажувача (Challenge-Response EOL Unlock)", size=13, color=INK, bold=True, anchor="middle"))

    # 3 Вертикальні смуги: Користувач/Інструмент, Завантажувач MCU, Сховище NVS/eFuse
    p.append(rect(40, 60, 220, 350, fill="#ffffff", stroke=INK, sw=1.4, rx=6))
    p.append(text(150, 85, "Користувач / EOL Утиліта", size=12, color=INK, bold=True, anchor="middle"))

    p.append(rect(310, 60, 230, 350, fill="#f0f4f8", stroke="#2b6cb0", sw=1.6, rx=6))
    p.append(text(425, 85, "Bootloader MCU (ROM/Flash)", size=12, color="#2b6cb0", bold=True, anchor="middle"))

    p.append(rect(590, 60, 210, 350, fill="#fff5f5", stroke=NEG, sw=1.4, rx=6))
    p.append(text(695, 85, "Сховище NVS / eFuse OTP", size=12, color=NEG, bold=True, anchor="middle"))

    # Крок 1: Запит Challenge
    p.append(arrow(170, 120, 410, 120, color=INK, sw=1.4))
    p.append(text(290, 112, "1. Запит розблокування", size=9, color=INK, bold=True, anchor="middle"))

    # Крок 2: Відповідь Nonce + Chip ID
    p.append(arrow(410, 160, 170, 160, color="#2b6cb0", sw=1.4))
    p.append(text(290, 152, "2. Nonce (TRNG) + Unique Chip ID", size=9, color="#2b6cb0", bold=True, anchor="middle"))

    # Крок 3: Підпис через Master EOL Key
    p.append(rect(55, 185, 190, 45, fill="#edf2f7", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(150, 203, "Генерація токена розблокування:", size=9, color=INK, bold=True, anchor="middle"))
    p.append(text(150, 219, "Sign(SK_master, Nonce || Chip_ID)", size=9, color="#2b6cb0", anchor="middle"))

    # Крок 4: Передача токена
    p.append(arrow(170, 250, 410, 250, color=INK, sw=1.4))
    p.append(text(290, 242, "3. Передача Unlock Token", size=9, color=INK, bold=True, anchor="middle"))

    # Крок 5: Верифікація відкритого ключа та Zeroization
    p.append(arrow(440, 275, 680, 275, color=NEG, sw=1.5))
    p.append(text(560, 267, "4. Верифікація PK_root", size=9, color=NEG, bold=True, anchor="middle"))

    p.append(arrow(440, 310, 680, 310, color=NEG, sw=1.5))
    p.append(text(560, 302, "5. Secure Zeroization (стирання NVS)", size=9, color=NEG, bold=True, anchor="middle"))

    # Крок 6: Зміна стану завантажувача
    p.append(rect(325, 335, 200, 35, fill="#f0fff4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(425, 357, "6. Стан: UNLOCKED (відкрито)", size=10, color=FIELD, bold=True, anchor="middle"))

    # Крок 7: Відкритий запис сторонньої прошивки
    p.append(arrow(170, 390, 410, 390, color=FIELD, sw=1.6))
    p.append(text(290, 382, "7. Запис кастомної прошивки (OpenWrt/ESPHome)", size=9, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "eol-bootloader-unlock.svg"), W, H, *p)


if __name__ == "__main__":
    fig_local_first_resilience()
    fig_eol_bootloader_unlock()
    print("All figures generated successfully.")
