# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми software-patents-and-pools.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для теми патентів та ліцензій
BG_PERM     = "#eaf5ea"  # Світло-зелений (Авторське право / Відкритий код)
BORDER_PERM = "#27ae60"
BG_PAT      = "#fff7ed"  # Світло-помаранчевий (Патентна монополія)
BORDER_PAT  = "#ea580c"
BG_RISK     = "#fef2f2"  # Світло-червоний (Судовий ризик / Порушення)
BORDER_RISK = "#dc2626"
BG_POOL     = "#eef2ff"  # Світло-синій (Патентний пул / Адміністратор)
BORDER_POOL = "#2563eb"
BG_NEUTRAL  = "#f8fafc"  # Нейтральний сірий
BORDER_GRAY = "#64748b"


def fig1_copyright_vs_patent():
    """Фігура 1: Фундаментальна різниця між Авторським правом (Copyright) та Патентом на ПЗ."""
    w, h = 940, 470
    parts = []

    parts.append(text(w / 2, 28, "Авторське право (Copyright) проти Патенту на програмне забезпечення", size=15, bold=True))

    # Ліва колонка: Авторське право
    col1_x = 40
    col1_w = 410
    parts.append(rect(col1_x, 56, col1_w, 390, fill=BG_PERM, stroke=BORDER_PERM, sw=1.8, rx=8))
    parts.append(text(col1_x + col1_w / 2, 82, "Авторське право (Copyright)", size=14, color=BORDER_PERM, bold=True))
    parts.append(line(col1_x + 15, 96, col1_x + col1_w - 15, 96, color=BORDER_PERM, sw=1, dash="3,3"))

    c1_items = [
        ("Об'єкт захисту:", "Конкретне текстове вираження: текст коду, двійковий бінарник, структура файлу."),
        ("Що НЕ захищається:", "Ідеї, математичні алгоритми, протоколи, формати даних, архітектурні принципи."),
        ("Чиста кімната (Clean-room):", "Повна легальність! Написання власного коду за специфікацією з нуля НЕ є порушенням."),
        ("Дія відкритих ліцензій:", "MIT, BSD, GPL повністю знімають претензії автора тексту коду."),
        ("Правовий наслідок:", "Якщо код написаний власноруч без копіювання чужих рядків — ризик копірайту дорівнює нулю.")
    ]

    y = 115
    for label, desc in c1_items:
        parts.append(text(col1_x + 16, y, label, size=11, color=INK, anchor="start", bold=True))
        y += 18
        parts.append(mtext(col1_x + 16, y, desc, size=10, color=MUTED, anchor="start", lh=1.25))
        y += 38
        if y < 420:
            parts.append(line(col1_x + 20, y - 10, col1_x + col1_w - 20, y - 10, color="#d1d5db", sw=0.8))

    # Права колонка: Патенти на ПЗ
    col2_x = 490
    col2_w = 410
    parts.append(rect(col2_x, 56, col2_w, 390, fill=BG_PAT, stroke=BORDER_PAT, sw=1.8, rx=8))
    parts.append(text(col2_x + col2_w / 2, 82, "Патент на винахід / алгоритм (Software Patent)", size=14, color=BORDER_PAT, bold=True))
    parts.append(line(col2_x + 15, 96, col2_x + col2_w - 15, 96, color=BORDER_PAT, sw=1, dash="3,3"))

    c2_items = [
        ("Об'єкт захисту:", "Метод, послідовність кроків алгоритму, математична трансформація даних."),
        ("Що НЕ захищається:", "Текст коду (патенту байдуже, якою мовою і якими іменами змінних записано суть)."),
        ("Чиста кімната (Clean-room):", "БЕЗСИЛА. Навіть якщо алгоритм винайдено незалежно, реалізація порушує патент."),
        ("Дія відкритих ліцензій:", "MIT / GPLv2 не дають захисту від сторонніх власників патентів (Third-party SEPs)."),
        ("Правовий наслідок:", "Будь-який працюючий декодер чи кодер порушує пункт формули патенту (Patent Claim).")
    ]

    y = 115
    for label, desc in c2_items:
        parts.append(text(col2_x + 16, y, label, size=11, color=INK, anchor="start", bold=True))
        y += 18
        parts.append(mtext(col2_x + 16, y, desc, size=10, color=MUTED, anchor="start", lh=1.25))
        y += 38
        if y < 420:
            parts.append(line(col2_x + 20, y - 10, col2_x + col2_w - 20, y - 10, color="#d1d5db", sw=0.8))

    render(os.path.join(OUT, "copyright-vs-patent.svg"), w, h, *parts)


def fig2_patent_pool_structure():
    """Фігура 2: Структура патентного пулу, збір роялті та ліцензування апаратних виробників."""
    w, h = 940, 490
    parts = []

    parts.append(text(w / 2, 28, "Архітектура патентного пулу: консолідація стандартних патентів (SEP)", size=15, bold=True))

    # Верхній ярус: Патентовласники (Licensors)
    parts.append(text(w / 2, 60, "Патентовласники обов'язкових патентів стандарту (SEP Licensors)", size=12, color=MUTED, bold=True))
    lic_boxes = [
        (40, "Корпорація A\n(Sony, Apple)\n• 150 патентів", BG_NEUTRAL),
        (220, "Корпорація B\n(Samsung, LG)\n• 230 патентів", BG_NEUTRAL),
        (400, "НДІ / Лабораторії\n(Fraunhofer, Dolby)\n• 90 патентів", BG_NEUTRAL),
        (580, "Телеком-гіганти\n(Ericsson, Nokia)\n• 180 патентів", BG_NEUTRAL),
        (760, "Інші SEP-холдери\n(Panasonic, Philips)\n• 110 патентів", BG_NEUTRAL),
    ]

    for bx, btitle, bbg in lic_boxes:
        parts.append(rect(bx, 76, 140, 64, fill=bbg, stroke=BORDER_GRAY, sw=1.2, rx=6))
        parts.append(mtext(bx + 70, 95, btitle, size=10, color=INK, bold=False, lh=1.2))
        # Стрілка вниз до пулу
        parts.append(line(bx + 70, 140, bx + 70, 180, color=BORDER_POOL, sw=1.5))
        parts.append(arrow(bx + 70, 175, bx + 70, 182, color=BORDER_POOL, sw=1.5))

    # Середній ярус: Патентний пул (Licensing Administrator)
    pool_x, pool_y, pool_w, pool_h = 160, 185, 620, 130
    parts.append(rect(pool_x, pool_y, pool_w, pool_h, fill=BG_POOL, stroke=BORDER_POOL, sw=2, rx=10))
    parts.append(text(pool_x + pool_w / 2, pool_y + 25, "Адміністратор патентного пулу (наприклад, MPEG LA / Via LA / Access Advance)", size=13, color=BORDER_POOL, bold=True))
    parts.append(line(pool_x + 20, pool_y + 36, pool_x + pool_w - 20, pool_y + 36, color=BORDER_POOL, sw=1, dash="3,3"))

    parts.append(mtext(pool_x + pool_w / 2, pool_y + 55,
                       "1. Оцінка суттєвості (Essentiality Evaluation) незалежними експертами\n"
                       "2. Єдиний пакетний ліцензійний договір для всієї індустрії (Standard Agreement)\n"
                       "3. Розрахунок порогів, щорічних лімітів (Caps) та збір фіксованих роялті ($/шт)\n"
                       "4. Пропорційний розподіл ліцензійних доходів між патентовласниками",
                       size=11, color=INK, bold=False, lh=1.3))

    # Стрілки вниз до ліцензіатів
    for ax in [160, 470, 780]:
        parts.append(line(ax, 315, ax, 365, color=BORDER_PAT, sw=1.8))
        parts.append(arrow(ax, 360, ax, 368, color=BORDER_PAT, sw=1.8))

    # Нижній ярус: Ліцензіати (Licensees / Device OEMs)
    parts.append(text(w / 2, 355, "Ліцензіати: виробники кінцевих пристроїв та дистриб'ютори ПЗ", size=12, color=MUTED, bold=True))

    oem_boxes = [
        (40, "Виробник камер / дронів\n(Апаратний H.264/H.265 SoC)\n• Роялті за кожен екземпляр", BG_RISK, BORDER_RISK),
        (350, "Розробник ОС / Браузера\n(Програмний декодер)\n• Потребує ліцензії або OpenH264", BG_PAT, BORDER_PAT),
        (660, "Стрімінговий сервіс\n(Контент та транскодування)\n• Ліцензування кодерів / Title Fee", BG_NEUTRAL, BORDER_GRAY),
    ]

    for ox, otitle, obg, obrd in oem_boxes:
        parts.append(rect(ox, 375, 240, 75, fill=obg, stroke=obrd, sw=1.5, rx=6))
        parts.append(mtext(ox + 120, 398, otitle, size=11, color=INK, bold=False, lh=1.25))

    render(os.path.join(OUT, "patent-pool-structure.svg"), w, h, *parts)


def fig3_hevc_fragmentation():
    """Фігура 3: Порівняння монолітного пулу H.264 та фрагментації пулів H.265/HEVC."""
    w, h = 940, 480
    parts = []

    parts.append(text(w / 2, 28, "Фрагментація ліцензування: успіх H.264 проти кризи H.265 (HEVC)", size=15, bold=True))

    # Ліва половина: H.264 / AVC
    h264_x = 40
    h264_w = 410
    parts.append(rect(h264_x, 56, h264_w, 400, fill=BG_PERM, stroke=BORDER_PERM, sw=1.8, rx=8))
    parts.append(text(h264_x + h264_w / 2, 82, "H.264 / AVC (Єдиний монолітний пул)", size=14, color=BORDER_PERM, bold=True))
    parts.append(line(h264_x + 15, 96, h264_x + h264_w - 15, 96, color=BORDER_PERM, sw=1, dash="3,3"))

    # Схема H.264
    parts.append(rect(h264_x + 45, 115, 320, 70, fill=BG_POOL, stroke=BORDER_POOL, sw=1.4, rx=6))
    parts.append(text(h264_x + 205, 142, "Єдиний адміністратор: MPEG LA", size=12, color=BORDER_POOL, bold=True))
    parts.append(text(h264_x + 205, 162, "Охоплює >90% обов'язкових патентів", size=10, color=MUTED))

    h264_desc = (
        "• Передбачувана вартість: ~$0.20 за пристрій\n"
        "• Перші 100 000 екземплярів щороку — БЕЗОПЛАТНО\n"
        "• Жорсткий річний ліміт виплат (Cap: $9.75M)\n"
        "• Безкоштовний некомерційний інтернет-стрімінг\n"
        "• Результат: тотальне впровадження у всьому світі,\n"
        "  апаратна підтримка в кожному процесорі."
    )
    parts.append(rect(h264_x + 20, 205, 370, 140, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(mtext(h264_x + 35, 230, h264_desc, size=11, color=INK, anchor="start", lh=1.35))

    parts.append(rect(h264_x + 45, 365, 320, 70, fill=BG_PERM, stroke=BORDER_PERM, sw=1.2, rx=6))
    parts.append(text(h264_x + 205, 392, "Результат для індустрії:", size=11, color=BORDER_PERM, bold=True))
    parts.append(text(h264_x + 205, 414, "Світовий стандарт на 20+ років", size=12, color=INK, bold=True))

    # Права половина: H.265 / HEVC
    hevc_x = 490
    hevc_w = 410
    parts.append(rect(hevc_x, 56, hevc_w, 400, fill=BG_RISK, stroke=BORDER_RISK, sw=1.8, rx=8))
    parts.append(text(hevc_x + hevc_w / 2, 82, "H.265 / HEVC (Війна кількох пулів)", size=14, color=BORDER_RISK, bold=True))
    parts.append(line(hevc_x + 15, 96, hevc_x + hevc_w - 15, 96, color=BORDER_RISK, sw=1, dash="3,3"))

    # 3 пули + незалежні
    parts.append(rect(hevc_x + 20, 110, 110, 50, fill=BG_POOL, stroke=BORDER_POOL, sw=1, rx=4))
    parts.append(mtext(hevc_x + 75, 128, "MPEG LA\n(Pool 1)", size=10, color=BORDER_POOL, bold=True, lh=1.15))

    parts.append(rect(hevc_x + 150, 110, 110, 50, fill=BG_POOL, stroke=BORDER_POOL, sw=1, rx=4))
    parts.append(mtext(hevc_x + 205, 128, "HEVC Advance\n(Pool 2)", size=10, color=BORDER_POOL, bold=True, lh=1.15))

    parts.append(rect(hevc_x + 280, 110, 110, 50, fill=BG_POOL, stroke=BORDER_POOL, sw=1, rx=4))
    parts.append(mtext(hevc_x + 335, 128, "Velos Media\n(Pool 3)", size=10, color=BORDER_POOL, bold=True, lh=1.15))

    parts.append(text(hevc_x + hevc_w / 2, 180, "+ Десятки незалежних компаній (Qualcomm, Technicolor...)", size=10, color=POS, bold=True))

    hevc_desc = (
        "• Сумарна ціна за пристрій: $2.00–$4.50+\n"
        "• Відсутність єдиного річного ліміту (кожен пул має свій)\n"
        "• Спроба збирати відсоток від доходів за трансляцію контенту\n"
        "• Невизначеність: ліцензія на 3 пули НЕ захищає від інших\n"
        "• Наслідок: браузери відмовились від HEVC, а ринок створив\n"
        "  відкритий альянс AOMedia для розробки AV1."
    )
    parts.append(rect(hevc_x + 20, 205, 370, 140, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(mtext(hevc_x + 35, 230, hevc_desc, size=11, color=INK, anchor="start", lh=1.35))

    parts.append(rect(hevc_x + 45, 365, 320, 70, fill=BG_RISK, stroke=BORDER_RISK, sw=1.2, rx=6))
    parts.append(text(hevc_x + 205, 392, "Наслідок для індустрії:", size=11, color=BORDER_RISK, bold=True))
    parts.append(text(hevc_x + 205, 414, "Створення відкритого кодека AV1", size=12, color=BORDER_RISK, bold=True))

    render(os.path.join(OUT, "hevc-fragmentation.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_copyright_vs_patent()
    fig2_patent_pool_structure()
    fig3_hevc_fragmentation()
    print("Всі 3 фігури успішно згенеровано у:", OUT)
