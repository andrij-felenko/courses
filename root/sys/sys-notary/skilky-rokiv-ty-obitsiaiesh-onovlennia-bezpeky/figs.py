#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми: Скільки років ти обіцяєш оновлення безпеки."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від кореня теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_cra_lifecycle_compliance():
    """Діаграма життєвого циклу пристрою, строків підтримки CRA/PSTI та процесу зняття з експлуатації."""
    w, h = 980, 480
    frags = []

    # Заголовок блоків таймлайну
    frags.append(text(w / 2, 28, "Хронологія життєвого циклу цифрового виробу за вимогами CRA та UK PSTI", size=15, bold=True))

    # Стрічка часу (головна вісь)
    axis_y = 90
    frags.append(line(40, axis_y, 940, axis_y, color=LINE, sw=2))
    frags.append(arrow(930, axis_y, 955, axis_y, color=LINE, sw=2))
    frags.append(text(950, axis_y - 12, "Час (роки)", size=11, color=MUTED, anchor="end"))

    # Ключові часові мітки на осі
    milestones = [
        (60, "T0: Старт розробки", "Security by Design"),
        (230, "T1: Перший продаж (PoS)", "Декларація PSTI SoC"),
        (460, "T2: Зняття з виробництва", "End-of-Sale (EoS)"),
        (720, "T3: Кінець оновлень (EoS)", "Мінімум 5 років від T1"),
        (910, "T4: Повний End-of-Life", "Виведення з обігу")
    ]
    for mx, title, sub in milestones:
        frags.append(circle(mx, axis_y, 5, fill=NEG, stroke="#ffffff", sw=1.5))
        frags.append(line(mx, axis_y - 8, mx, axis_y + 8, color=NEG, sw=1.5))
        frags.append(text(mx, axis_y - 14, title, size=11, bold=True, color=INK))
        frags.append(text(mx, axis_y + 20, sub, size=9.5, color=MUTED))

    # 3 основні фази (кольорові блоки внизу)
    # Фаза 1: Активний продаж та розробка
    p1_x, p1_y, p1_w, p1_h = 40, 140, 270, 310
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f0f9ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "Фаза 1: Активний випуск", size=13.5, bold=True, color=NEG))
    frags.append(text(p1_x + p1_w / 2, p1_y + 42, "Виробництво та комерціалізація", size=10.5, color=MUTED, italic=True))
    frags.append(line(p1_x + 12, p1_y + 52, p1_x + p1_w - 12, p1_y + 52, color=NEG, sw=1))

    items1 = [
        "Обов'язки виробника:",
        " • Публікація Defined Support Period",
        " • Реєстрація security.txt (RFC 9116)",
        " • Генерація SBOM (SPDX/CycloneDX)",
        " • Неперервний моніторинг CVE/NVD",
        " • Випуск feature + security патчів",
        " • Канал зв'язку VDP / CVD",
        "Юридична рамка:",
        " • UK PSTI: фіксація дати підтримки",
        " • CRA: оцінка ризиків перед ринком"
    ]
    for i, itm in enumerate(items1):
        bold = (i in [0, 7])
        col = NEG if bold else INK
        frags.append(text(p1_x + 12, p1_y + 74 + i * 23, itm, size=10.5, anchor="start", bold=bold, color=col))

    # Фаза 2: Гарантована підтримка після зняття з продажу (EoS Maintenance)
    p2_x, p2_y, p2_w, p2_h = 330, 140, 320, 310
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "Фаза 2: Підтримка безпеки", size=13.5, bold=True, color=FIELD))
    frags.append(text(p2_x + p2_w / 2, p2_y + 42, "Пристрій знято з продажу, але на ринку", size=10.5, color=MUTED, italic=True))
    frags.append(line(p2_x + 12, p2_y + 52, p2_x + p2_w - 12, p2_y + 52, color=FIELD, sw=1))

    items2 = [
        "Обов'язки виробника:",
        " • Підтримка герметичних збірок (Toolchains)",
        " • Бекпортування патчів на старі ядра/RTOS",
        " • Розділення: суворо Security Patches Only",
        " • Безоплатне постачання оновлень (OTA)",
        " • SLA: Critical <= 72 год, High <= 30 діб",
        " • Публікація VEX-звітів (OpenVEX/CSAF)",
        "Вимоги CRA (Regulation 2024/2847):",
        " • Сповіщення ENISA про 0-day за 24 год",
        " • Заборона скорочувати заявлений строк",
        " • Підтримка мінімум 5 років від старту"
    ]
    for i, itm in enumerate(items2):
        bold = (i in [0, 6])
        col = FIELD if bold else INK
        frags.append(text(p2_x + 12, p2_y + 74 + i * 23, itm, size=10.5, anchor="start", bold=bold, color=col))

    # Фаза 3: Завершення підтримки та виведення з експлуатації (End-of-Life)
    p3_x, p3_y, p3_w, p3_h = 670, 140, 270, 310
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#fff1f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(p3_x + p3_w / 2, p3_y + 24, "Фаза 3: End-of-Life (EoL)", size=13.5, bold=True, color=POS))
    frags.append(text(p3_x + p3_w / 2, p3_y + 42, "Остаточне припинення оновлень", size=10.5, color=MUTED, italic=True))
    frags.append(line(p3_x + 12, p3_y + 52, p3_x + p3_w - 12, p3_y + 52, color=POS, sw=1))

    items3 = [
        "Обов'язки виробника:",
        " • Попередження клієнтів за 6-12 місяців",
        " • Публікація фінального бюлетеня безпеки",
        " • Безпечне скидання даних (Factory Reset)",
        " • Відключення хмарних бекендів / релеїв",
        " • Опція: відкриття коду (Right to Repair)",
        "Наслідки порушення строків:",
        " • Штрафи ЄС: до 15 млн € або 2.5% виручки",
        " • Санкції UK OPSS: вилучення з ринку",
        " • Цивільні позови за незакриті 0-day"
    ]
    for i, itm in enumerate(items3):
        bold = (i in [0, 5])
        col = POS if bold else INK
        frags.append(text(p3_x + 12, p3_y + 74 + i * 23, itm, size=10.5, anchor="start", bold=bold, color=col))

    path = os.path.join(OUT_DIR, "cra-lifecycle-compliance.svg")
    render(path, w, h, *frags, title="Вимоги CRA та PSTI до життєвого циклу оновлень безпеки")
    print(f"Згенеровано: {path}")


def fig_sbom_vulnerability_triage_pipeline():
    """Архітектура конвеєра прийому CVE, аналізу SBOM, фільтрації через VEX та розрахунку дедлайнів."""
    w, h = 980, 440
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр аналізу вразливостей (CVE), звірки з SBOM та генерації VEX-звітів", size=15, bold=True))

    # 4 кроки пайплайну
    steps = [
        ("1. Вхідні джерела", 30, 60, 205, 350, "#f8fafc", "#475569", [
            "Джерела даних:",
            " • NVD API (CPE 2.3)",
            " • GitHub Advisories",
            " • OSV.dev (PURL)",
            " • CISA KEV (Known Exploits)",
            " • Звіти VDP (security.txt)",
            "Артефакти збірки:",
            " • SPDX 3.0 / CycloneDX",
            " • Binary Hashes (SHA-256)",
            " • Ревізії апаратного заліза"
        ]),
        ("2. Зіставлення й скоринг", 265, 60, 215, 350, "#f0f9ff", NEG, [
            "Алгоритми аналізу:",
            " • Звірка PURL та діапазонів",
            " • Базовий скор CVSS v3.1/v4.0",
            " • Ймовірність атаки EPSS",
            " • Перевірка KEV каталогу",
            "Контекст прошивки:",
            " • Чи зібрано з LTO / gc-sec",
            " • Чи активна вразлива конфігурація",
            " • Чи є захист seccomp/MPU"
        ]),
        ("3. VEX Тріаж та статус", 510, 60, 215, 350, "#fefce8", "#ca8a04", [
            "Машиночитний вердикт:",
            " • affected (потрібен патч)",
            " • not_affected (обґрунтовано):",
            "   - code_not_reachable",
            "   - configuration_prevents",
            "   - inline_mitigation_exists",
            " • under_investigation",
            "Формати артефактів:",
            " • OpenVEX JSON-LD",
            " • CSAF 2.0 Advisory"
        ]),
        ("4. Виконання SLA та OTA", 755, 60, 195, 350, "#f0fdf4", FIELD, [
            "Дедлайни та дії:",
            " • Critical (CVSS >= 9.0):",
            "   SLA <= 72 год (hotfix)",
            " • High (CVSS 7.0-8.9):",
            "   SLA <= 30 діб",
            " • Перевірка Flash Memory ROM",
            " • Бекпорт на legacy гілки",
            " • Криптографічний підпис",
            " • Автоматична OTA роздача"
        ])
    ]

    for title, sx, sy, sw, sh, bg_col, border_col, items in steps:
        frags.append(rect(sx, sy, sw, sh, fill=bg_col, stroke=border_col, sw=1.5, rx=8))
        frags.append(text(sx + sw / 2, sy + 24, title, size=13, bold=True, color=border_col))
        frags.append(line(sx + 10, sy + 40, sx + sw - 10, sy + 40, color=border_col, sw=1))
        for i, itm in enumerate(items):
            bold = (i in [0, 5] or "SLA" in itm or "affected" in itm)
            col = border_col if bold else INK
            frags.append(text(sx + 10, sy + 62 + i * 22, itm, size=10, anchor="start", bold=bold, color=col))

    # Стрілки між етапами
    frags.append(arrow(235, 235, 265, 235, color=LINE, sw=2))
    frags.append(arrow(480, 235, 510, 235, color=LINE, sw=2))
    frags.append(arrow(725, 235, 755, 235, color=LINE, sw=2))

    path = os.path.join(OUT_DIR, "sbom-vulnerability-triage-pipeline.svg")
    render(path, w, h, *frags, title="Конвеєр обробки CVE, зіставлення з SBOM та генерації VEX-звітів")
    print(f"Згенеровано: {path}")


if __name__ == '__main__':
    fig_cra_lifecycle_compliance()
    fig_sbom_vulnerability_triage_pipeline()
