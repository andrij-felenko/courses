# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми shcho-same-ty-zoboviazanyi-viddaty-z-korobkoiu.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
BG_BOX     = "#f8fafc"
BORDER_BOX = "#334155"
BG_LEGAL   = "#eff6ff"
BORDER_LEGAL = "#2563eb"
BG_SRC     = "#f0fdf4"
BORDER_SRC = "#16a34a"
BG_WARN    = "#fef2f2"
BORDER_WARN = "#dc2626"
BG_TOOL    = "#fffbeb"
BORDER_TOOL = "#d97706"


def fig1_box_compliance_bundle():
    """Фігура 1: Повний комплект юридичних артефактів, що супроводжують фізичний пристрій."""
    w, h = 980, 520
    parts = []

    # Заголовок фігури
    parts.append(text(w / 2, 28, "Анатомія ліцензійного комплекту: що постачається з фізичним пристроєм", size=15, bold=True))

    # Ліва колонка: Фізична коробка виробу
    parts.append(rect(40, 60, 420, 430, fill=BG_BOX, stroke=BORDER_BOX, sw=2, rx=8))
    parts.append(text(250, 88, "📦 ФІЗИЧНА КОРОБКА ПРИСТРОЮ", size=13, color=INK, bold=True))
    parts.append(line(55, 104, 445, 104, color=BORDER_BOX, sw=1, dash="3,3"))

    # Блок 1.1: Залізо з прошивкою
    parts.append(rect(60, 118, 380, 72, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    parts.append(text(250, 138, "Апаратний пристрій (Flash / ROM)", size=12, bold=True))
    parts.append(text(250, 156, "• Бінарні образи: Kernel, U-Boot, BusyBox, glibc", size=10, color=MUTED))
    parts.append(text(250, 172, "• Пропрієтарні керуючі демони та конфігурація", size=10, color=MUTED))

    # Блок 1.2: Ліцензійний буклет (Notices)
    parts.append(rect(60, 202, 380, 110, fill=BG_LEGAL, stroke=BORDER_LEGAL, sw=1.5, rx=6))
    parts.append(text(250, 222, "📄 Буклет атрибуції (Open Source Notices)", size=12, color=BORDER_LEGAL, bold=True))
    parts.append(text(250, 242, "• Усі повідомлення про копірайти авторів (MIT, BSD, Apache)", size=10, color=INK))
    parts.append(text(250, 258, "• Повні незмінні тексти ліцензій (GPL, LGPL, Apache, MIT)", size=10, color=INK))
    parts.append(text(250, 274, "• Застереження про відмову від гарантій (Warranty Disclaimer)", size=10, color=INK))
    parts.append(text(250, 292, "• Вміст файлів NOTICE для компонентів під Apache-2.0", size=10, color=MUTED))

    # Блок 1.3: Письмова пропозиція (Written Offer)
    parts.append(rect(60, 324, 380, 150, fill=BG_TOOL, stroke=BORDER_TOOL, sw=1.5, rx=6))
    parts.append(text(250, 344, "✉️ Письмова оферта (Written Offer за GPLv2 §3b)", size=12, color=BORDER_TOOL, bold=True))
    parts.append(text(250, 364, "• Чинна щонайменше 3 роки від дати дистрибуції", size=10, color=INK))
    parts.append(text(250, 380, "• Надається будь-якій третій особі (GPLv2 §3b)", size=10, color=INK))
    parts.append(text(250, 396, "• Чітка контактна адреса (пошта, email, веб-портал)", size=10, color=INK))
    parts.append(text(250, 412, "• Зобов'язання надати повний відповідний вихідний код", size=10, color=INK))
    parts.append(text(250, 430, "• Ціна не вища за собівартість фізичного носія", size=10, color=MUTED))
    parts.append(text(250, 448, "• Пряме посилання на архів для завантаження", size=10, color=MUTED))

    # Стрілка запиту
    parts.append(arrow(460, 385, 515, 385, color=BORDER_TOOL, sw=2))
    parts.append(text(488, 372, "Запит", size=10, color=BORDER_TOOL, bold=True))

    # Права колонка: Повний відповідний вихідний код (Source Distribution Bundle)
    parts.append(rect(520, 60, 420, 430, fill=BG_SRC, stroke=BORDER_SRC, sw=2, rx=8))
    parts.append(text(730, 88, "💻 ПОВНИЙ ВІДПОВІДНИЙ ВИХІДНИЙ КОД", size=13, color=BORDER_SRC, bold=True))
    parts.append(line(535, 104, 925, 104, color=BORDER_SRC, sw=1, dash="3,3"))

    # Блок 2.1: Джерела з патчами
    parts.append(rect(540, 118, 380, 80, fill=BG, stroke=LINE, sw=1.2, rx=6))
    parts.append(text(730, 138, "Модифіковані вихідні тексти (Source Trees)", size=12, bold=True))
    parts.append(text(730, 156, "• Точні версії ядра Linux, U-Boot, BusyBox", size=10, color=INK))
    parts.append(text(730, 172, "• Усі вендорські патчі та драйвери під копілефтом", size=10, color=INK))
    parts.append(text(730, 188, "• Файли опису апаратури (Device Tree: .dts / .dtsi)", size=10, color=MUTED))

    # Блок 2.2: Конфігурація та дефініції
    parts.append(rect(540, 210, 380, 72, fill=BG, stroke=LINE, sw=1.2, rx=6))
    parts.append(text(730, 230, "Конфігураційні файли збірки", size=12, bold=True))
    parts.append(text(730, 248, "• Робочий .config / defconfig для ядра та BusyBox", size=10, color=INK))
    parts.append(text(730, 264, "• Файли дефініцій інтерфейсів (IDL, UAPI заголовки)", size=10, color=MUTED))

    # Блок 2.3: Скрипти компіляції та керування
    parts.append(rect(540, 294, 380, 92, fill=BG, stroke=LINE, sw=1.2, rx=6))
    parts.append(text(730, 314, "Скрипти збірки (Scripts to control compilation)", size=12, color=BORDER_SRC, bold=True))
    parts.append(text(730, 332, "• Makefiles, CMakeLists.txt, складальні скрипти", size=10, color=INK))
    parts.append(text(730, 348, "• Рецепти Yocto / Buildroot для відтворення середовища", size=10, color=INK))
    parts.append(text(730, 364, "• Точні версії тулчейна (GCC/Clang, binutils, libc)", size=10, color=MUTED))

    # Блок 2.4: Інформація про встановлення (Installation Info)
    parts.append(rect(540, 398, 380, 76, fill=BG_LEGAL, stroke=BORDER_LEGAL, sw=1.2, rx=6))
    parts.append(text(730, 418, "Інформація про встановлення (GPLv3 §6)", size=12, color=BORDER_LEGAL, bold=True))
    parts.append(text(730, 436, "• Інструкції з прошивання модифікованого бінарника", size=10, color=INK))
    parts.append(text(730, 452, "• Ключі верифікації / розблокування (для User Products)", size=10, color=MUTED))

    render(os.path.join(OUT, "box-compliance-bundle.svg"), w, h, *parts)


def fig2_written_offer_lifecycle():
    """Фігура 2: Життєвий цикл та часові межі письмової пропозиції (Written Offer)."""
    w, h = 960, 440
    parts = []

    # Заголовок
    parts.append(text(w / 2, 28, "Життєвий цикл письмової пропозиції вихідного коду (GPLv2 §3b)", size=15, bold=True))

    # Часова шкала
    parts.append(line(80, 80, 880, 80, color=LINE, sw=2))
    parts.append(arrow(870, 80, 890, 80, color=LINE, sw=2))
    parts.append(text(890, 98, "Час", size=11, color=MUTED, bold=True))

    # Віхи на часовій шкалі
    milestones = [
        (120, "T0: Збірка образу", "Фіксація комітів,\nSBOM та конфігу"),
        (340, "T1: Продаж екземпляра", "Відвантаження заліза\nв коробці клієнту"),
        (620, "T2: Запит коду", "Звернення від будь-якої\nтретьої особи"),
        (820, "T1 + 3 роки", "Закінчення обов'язку\nдля ЦЬОГО екземпляра"),
    ]

    for x, title, desc in milestones:
        parts.append(circle(x, 80, 5, fill=BORDER_LEGAL, stroke=LINE, sw=1.5))
        parts.append(line(x, 85, x, 120, color=BORDER_LEGAL, sw=1.2, dash="2,2"))
        parts.append(text(x, 136, title, size=11, color=INK, bold=True))
        parts.append(mtext(x, 154, desc, size=10, color=MUTED, lh=1.2))

    # Період 3-річного зобов'язання (дужка/прямокутник)
    parts.append(rect(340, 195, 480, 36, fill=BG_TOOL, stroke=BORDER_TOOL, sw=1.5, rx=6))
    parts.append(text(580, 218, "⏳ Період дії оферти: щонайменше 3 роки від дати передачі екземпляра", size=11, color=BORDER_TOOL, bold=True))

    # Два сценарії відповіді на запит
    # Сценарій А: Належне виконання (зелений)
    parts.append(rect(60, 260, 400, 155, fill=BG_SRC, stroke=BORDER_SRC, sw=1.5, rx=8))
    parts.append(text(260, 284, "✅ НАЛЕЖНЕ ВИКОНАННЯ ЗОБОВ'ЯЗАННЯ", size=12, color=BORDER_SRC, bold=True))
    parts.append(line(75, 298, 445, 298, color=BORDER_SRC, sw=1, dash="2,2"))
    parts.append(text(260, 318, "• Надано повний тарбол вихідних кодів із патчами", size=10, color=INK))
    parts.append(text(260, 334, "• Надано робочі Makefiles/скрипти та робочий .config", size=10, color=INK))
    parts.append(text(260, 350, "• Інженер третьої сторони успішно збирає образ", size=10, color=INK))
    parts.append(text(260, 370, "• Правовий статус: ЛІЦЕНЗІЯ ДІЄ, ПРИСТРІЙ ЛЕГАЛЬНИЙ", size=10, color=BORDER_SRC, bold=True))

    # Сценарій Б: Порушення та наслідки (червоний)
    parts.append(rect(500, 260, 400, 155, fill=BG_WARN, stroke=BORDER_WARN, sw=1.5, rx=8))
    parts.append(text(700, 284, "❌ ДЕФЕКТ ОФЕРТИ ТА ПРАВОВІ НАСЛІДКИ", size=12, color=BORDER_WARN, bold=True))
    parts.append(line(515, 298, 885, 298, color=BORDER_WARN, sw=1, dash="2,2"))
    parts.append(text(700, 318, "• Посилання на мертвий URL або «чужий GitHub»", size=10, color=INK))
    parts.append(text(700, 334, "• Відсутність вендорських патчів або робочого .config", size=10, color=INK))
    parts.append(text(700, 350, "• Автоматичне анулювання ліцензії (GPLv2 §4)", size=10, color=BORDER_WARN, bold=True))
    parts.append(text(700, 370, "• Судова заборона продажу, блокування митницею, збитки", size=10, color=BORDER_WARN, bold=True))

    render(os.path.join(OUT, "written-offer-lifecycle.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_box_compliance_bundle()
    fig2_written_offer_lifecycle()
    print("Фігури успішно згенеровано у ./img/")
