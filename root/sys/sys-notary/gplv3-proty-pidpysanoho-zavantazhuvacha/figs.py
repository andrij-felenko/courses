# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми gplv3-proty-pidpysanoho-zavantazhuvacha.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для діаграм теми
BG_GPL2   = "#eef2ff"  # Світло-синій (GPLv2)
BORDER_GPL2 = "#2563eb"
BG_GPL3   = "#fff7ed"  # Світло-помаранчевий (GPLv3)
BORDER_GPL3 = "#ea580c"
BG_STRONG = "#fff7ed"  # Світло-помаранчевий (Strong Copyleft / GPLv3)
BORDER_STRONG = "#ea580c"
BG_LOCK   = "#fef2f2"  # Світло-червоний (Заблоковане залізо / Порушення)
BORDER_LOCK = "#dc2626"
BG_PASS   = "#eaf5ea"  # Світло-зелений (Дозволено / Відкритий ключ)
BORDER_PASS = "#27ae60"
BG_PANEL  = "#f8fafc"  # Світло-сірий фон панелей
BORDER_PANEL = "#64748b"


def fig1_tivoization_mechanism():
    """Фігура 1: Механіка тайвоізації — розрив між свободою коду та апаратним контролем."""
    w, h = 920, 480
    parts = []

    parts.append(text(w / 2, 28, "Феномен тайвоізації: легальна відкритість коду проти апаратного блокування запуску", size=15, bold=True))

    # Ліва колонка: Юридичний рівень вихідного коду (GPLv2 дотримана)
    parts.append(rect(40, 60, 260, 390, fill=BG_GPL2, stroke=BORDER_GPL2, sw=1.8, rx=8))
    parts.append(text(170, 88, "Рівень вихідного коду", size=13, color=BORDER_GPL2, bold=True))
    parts.append(text(170, 108, "(GPLv2 формально дотримана)", size=11, color=MUTED, bold=False))
    parts.append(line(55, 120, 285, 120, color=BORDER_GPL2, sw=1, dash="2,2"))

    parts.append(fitbox(55, 135, 230, 65, "Вендор публікує повний код:\n• Ядро Linux під GPLv2\n• Скрипти збирання образу", size=11, fill="#ffffff", stroke=BORDER_GPL2))
    parts.append(arrow(170, 205, 170, 230, color=BORDER_GPL2, sw=1.5))

    parts.append(fitbox(55, 235, 230, 75, "Користувач / Інженер:\n• Читає та модифікує код\n• Успішно компілює бінарник\n• Записує образ у флеш-пам'ять", size=11, fill="#ffffff", stroke=BORDER_GPL2))
    parts.append(arrow(170, 315, 170, 340, color=BORDER_GPL2, sw=1.5))

    parts.append(fitbox(55, 345, 230, 85, "Результат компіляції:\n`vmlinux.bin` готовий,\nале НЕ підписаний приватним\nключем виробника", size=11, fill=BG_PANEL, stroke=BORDER_PANEL))

    # Центральна колонка: Апаратний контроль та перевірка підпису в BootROM
    parts.append(rect(330, 60, 260, 390, fill=BG_PANEL, stroke=BORDER_PANEL, sw=1.8, rx=8))
    parts.append(text(460, 88, "Апаратний рівень (SoC / ROM)", size=13, color=INK, bold=True))
    parts.append(text(460, 108, "(Root of Trust у кремнії)", size=11, color=MUTED, bold=False))
    parts.append(line(345, 120, 575, 120, color=BORDER_PANEL, sw=1, dash="2,2"))

    parts.append(fitbox(345, 135, 230, 75, "Захищений кремній (SoC):\n• Публічний ключ у eFuses\n• Незмінний BootROM\n• Криптографічний акселератор", size=11, fill="#ffffff", stroke=BORDER_PANEL))
    parts.append(arrow(460, 215, 460, 240, color=BORDER_PANEL, sw=1.5))

    parts.append(fitbox(345, 245, 230, 75, "Алгоритм перевірки цілісності:\n`RSA_Verify(pub_key, hash, sig)`\nПеревірка цифрового підпису\nперед передачею керування", size=11, fill="#ffffff", stroke=BORDER_PANEL))
    parts.append(arrow(460, 325, 460, 350, color=BORDER_PANEL, sw=1.5))

    parts.append(fitbox(345, 355, 230, 75, "Криптографічний ключ:\nПриватний ключ RSA/ECDSA\nзнаходиться виключно на\nзахищеному сервері вендора", size=11, fill="#ffffff", stroke=POS))

    # Стрілка переходу від коду до процесора
    parts.append(arrow(290, 275, 325, 275, color=BORDER_GPL2, sw=1.8))

    # Права колонка: Наслідки та розрив свободи
    parts.append(rect(620, 60, 260, 390, fill=BG_LOCK, stroke=BORDER_LOCK, sw=1.8, rx=8))
    parts.append(text(750, 88, "Статус виконання на платі", size=13, color=BORDER_LOCK, bold=True))
    parts.append(text(750, 108, "(Практичний підсумок)", size=11, color=MUTED, bold=False))
    parts.append(line(635, 120, 865, 120, color=BORDER_LOCK, sw=1, dash="2,2"))

    parts.append(fitbox(635, 135, 230, 80, "Офіційна прошивка вендора:\n• Має дійсний RSA-підпис\n• BootROM верифікує хеш\n• Пристрій завантажується [✓]", size=11, fill=BG_PASS, stroke=BORDER_PASS))

    parts.append(arrow(460, 395, 630, 315, color=BORDER_LOCK, sw=1.8))

    parts.append(fitbox(635, 245, 230, 95, "Модифікована користувачем:\n• Підпис відсутній або чужий\n• BootROM фіксує помилку\n• SoC блокує шину пам'яті\n• Плата переходить у reset [✗]", size=11, fill="#ffffff", stroke=BORDER_LOCK))

    parts.append(fitbox(635, 355, 230, 80, "Парадокс тайвоізації:\nКористувач володіє кодом,\nале позбавлений права\nзапустити його на своєму залізі", size=10, fill=BG_STRONG, stroke=BORDER_STRONG))

    render(os.path.join(OUT, "tivoization-mechanism.svg"), w, h, *parts)


def fig2_secure_boot_trust_chain():
    """Фігура 2: Ланцюг Secure Boot і дилема Installation Information для GRUB 2."""
    w, h = 940, 490
    parts = []

    parts.append(text(w / 2, 28, "Ланцюг довіри Secure Boot: дотримання GPLv3 на ПК проти блокування у Smart-пристроях", size=15, bold=True))

    # Сходинки ланцюга довіри
    stages = [
        ("1. Hardware Root of Trust", "UEFI SPI Flash / eFuses\nЗберігає сертифікати PK, KEK,\nбазу дозволених ключів `db`", 40, 70, 200, 90, BG_PANEL, BORDER_PANEL),
        ("2. Shim Loader (BSD-2)", "Підписаний Microsoft UEFI CA.\nМістить власний ключ вендора та\nінтерфейс MokManager (MOK)", 270, 70, 200, 90, BG_PASS, BORDER_PASS),
        ("3. GRUB 2 (GPLv3)", "Підписаний дистрибутивним ключем.\nЗавантажує меню та передає\nкерування ядру операційної системи", 500, 70, 200, 90, BG_GPL3, BORDER_GPL3),
        ("4. Linux Kernel (GPLv2)", "Перевіряє сигнатури модулів.\nАктивує Kernel Lockdown Mode\nдля захисту пам'яті ядра", 730, 70, 180, 90, BG_GPL2, BORDER_GPL2),
    ]

    for title, desc, x, y, bw, bh, bg_c, brd_c in stages:
        parts.append(rect(x, y, bw, bh, fill=bg_c, stroke=brd_c, sw=1.5, rx=6))
        parts.append(text(x + bw / 2, y + 20, title, size=11, bold=True))
        parts.append(mtext(x + bw / 2, y + 42, desc, size=10, color=INK, bold=False, lh=1.2))

    parts.append(arrow(245, 115, 265, 115, color=LINE, sw=1.8))
    parts.append(arrow(475, 115, 495, 115, color=LINE, sw=1.8))
    parts.append(arrow(705, 115, 725, 115, color=LINE, sw=1.8))

    # Нижня частина: Розгалуження ПК проти Закритого IoT
    # Ліва гілка: Відкрита ПК-платформа
    parts.append(rect(40, 200, 420, 260, fill=BG_PASS, stroke=BORDER_PASS, sw=1.8, rx=8))
    parts.append(text(250, 226, "Відкрита ПК-платформа (x86 Desktop / Server)", size=13, color=BORDER_PASS, bold=True))
    parts.append(line(55, 240, 445, 240, color=BORDER_PASS, sw=1, dash="2,2"))

    parts.append(fitbox(55, 252, 390, 55, "Механізми контролю користувача:\n• Можливість повністю вимкнути Secure Boot в UEFI Setup\n• Генерація та імпорт власного сертифіката через `mokutil`", size=10, fill="#ffffff", stroke=BORDER_PASS))

    parts.append(fitbox(55, 317, 390, 60, "Статус ліцензійної відповідності:\n• Користувач може замінити бінарник `grubx64.efi` і підписати його MOK\n• Вимога «Installation Information» статті 6 GPLv3 повністю виконана", size=10, fill="#ffffff", stroke=BORDER_PASS))

    parts.append(fitbox(55, 387, 390, 55, "Підсумок:\nВикористання GRUB 2 під GPLv3 у дистрибутивах\n(Ubuntu, Fedora, Debian) є абсолютно законним [✓]", size=10, fill=BG_PASS, stroke=BORDER_PASS, bold=True))

    # Права гілка: Заблоковані споживчі пристрої (Smart TV, автомобілі, модеми)
    parts.append(rect(480, 200, 430, 260, fill=BG_LOCK, stroke=BORDER_LOCK, sw=1.8, rx=8))
    parts.append(text(695, 226, "Заблокований споживчий пристрій (User Product)", size=13, color=BORDER_LOCK, bold=True))
    parts.append(line(495, 240, 895, 240, color=BORDER_LOCK, sw=1, dash="2,2"))

    parts.append(fitbox(495, 252, 400, 55, "Обмеження прошивки та заліза:\n• UEFI Setup / BIOS Setup відсутній або заблокований паролем\n• Меню MOK недоступне, eFuses зашиті єдиним OEM-ключем", size=10, fill="#ffffff", stroke=BORDER_LOCK))

    parts.append(fitbox(495, 317, 400, 60, "Юридичний конфлікт:\n• Модифікований GRUB 2 не може запуститися без закритого ключа\n• Вендор відмовляється надати приватний ключ або механізм підпису", size=10, fill="#ffffff", stroke=BORDER_LOCK))

    parts.append(fitbox(495, 387, 400, 55, "Підсумок:\nПряме порушення статті 6 GPLv3! Вендор зобов'язаний\nнадати ключі або вилучити компоненти GPLv3 [✗]", size=10, fill=BG_LOCK, stroke=BORDER_LOCK, bold=True))

    render(os.path.join(OUT, "secure-boot-trust-chain.svg"), w, h, *parts)


def fig3_gplv2_vs_gplv3_split():
    """Фігура 3: Розкол екосистеми на табори GPLv2 та GPLv3."""
    w, h = 920, 460
    parts = []

    parts.append(text(w / 2, 28, "Великий ліцензійний розкол: компоненти GPLv2 проти GPLv3 у прошивках", size=15, bold=True))

    # Лівий блок: Табір GPLv2 (Орієнтація на програмний копілефт)
    parts.append(rect(40, 60, 400, 370, fill=BG_GPL2, stroke=BORDER_GPL2, sw=1.8, rx=8))
    parts.append(text(240, 88, "Табір GPLv2: Програмний копілефт", size=13, color=BORDER_GPL2, bold=True))
    parts.append(text(240, 108, "Філософія Лінуса Торвальдса: захист коду, а не контроль заліза", size=10, color=MUTED, bold=False))
    parts.append(line(55, 120, 425, 120, color=BORDER_GPL2, sw=1, dash="2,2"))

    gpl2_items = [
        ("Ядро Linux (GPL-2.0-only)", "Головна системна основа. Вендори можуть підписувати\nобрази власним ключем без розкриття самого ключа."),
        ("U-Boot / Barebox (GPL-2.0)", "Завантажувачі вбудованих систем. Зберігають GPLv2\nдля сумісності з криптографічними BootROM виробників."),
        ("BusyBox (GPL-2.0-only)", "Компактний набір утиліт командного рядка для IoT,\nактивно судиться за розкриття коду, але не за ключі."),
    ]
    for i, (title, desc) in enumerate(gpl2_items):
        parts.append(fitbox(55, 132 + i * 95, 370, 85, "%s\n%s" % (title, desc), size=11, fill="#ffffff", stroke=BORDER_GPL2, bold=False))

    # Правий блок: Табір GPLv3 (Орієнтація на захист прав кінцевого користувача)
    parts.append(rect(480, 60, 400, 370, fill=BG_GPL3, stroke=BORDER_GPL3, sw=1.8, rx=8))
    parts.append(text(680, 88, "Табір GPLv3: Антитайвоізація", size=13, color=BORDER_GPL3, bold=True))
    parts.append(text(680, 108, "Філософія FSF / Річарда Столмана: свобода виконання на залізі", size=10, color=MUTED, bold=False))
    parts.append(line(495, 120, 865, 120, color=BORDER_GPL3, sw=1, dash="2,2"))

    gpl3_items = [
        ("GRUB 2 (GPL-3.0-or-later)", "Універсальний завантажувач. Вимагає Installation Info,\nчерез що вендори IoT уникають його у закритих платах."),
        ("GCC Toolchain & GDB (GPL-3.0)", "Компілятор і дебагер. GCC Runtime Library Exception\nдозволяє поширювати бінарники без копілефту рантайму."),
        ("GNU Coreutils, Bash (GPL-3.0)", "Базовий системний стек. Apple повністю відмовилася\nвід оновлення Bash у macOS через перехід на GPLv3."),
    ]
    for i, (title, desc) in enumerate(gpl3_items):
        parts.append(fitbox(495, 132 + i * 95, 370, 85, "%s\n%s" % (title, desc), size=11, fill="#ffffff", stroke=BORDER_GPL3, bold=False))

    render(os.path.join(OUT, "gplv2-vs-gplv3-split.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_tivoization_mechanism()
    fig2_secure_boot_trust_chain()
    fig3_gplv2_vs_gplv3_split()
    print("Всі 3 фігури успішно згенеровано у %s" % OUT)
