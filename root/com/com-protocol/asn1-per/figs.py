# -*- coding: utf-8 -*-
"""Фігури до теми «ASN.1 і правила кодування PER»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eefaf1"
GRAY_BG = "#f8f9fa"
ACCENT_BLUE = "#1e50a2"
ACCENT_GREEN = "#1b813e"
ACCENT_ORANGE = "#d97706"
ACCENT_RED = "#c53030"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Анатомія невирівняного бітового потоку UPER для ASN.1 SEQUENCE
# ─────────────────────────────────────────────────────────────────────────────
def fig_per_bitstream_layout():
    W, H = 1060, 680
    f = []

    # Головна підкладка
    f.append(rect(20, 20, 1020, 640, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))

    f.append(text(40, 52, "Анатомія бітового потоку UPER (UNALIGNED PER)", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Кодування структури RRCConnectionRequest: поля упаковані без вирівнювання на межі байтів", size=12, color=MUTED, anchor="start"))

    # ASN.1 Схема ліворуч
    f.append(rect(40, 100, 360, 310, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(55, 126, "Вихідна схема ASN.1 (X.680)", size=13, color=ACCENT_BLUE, anchor="start", bold=True))

    schema_lines = [
        "RRCConnectionRequest ::= SEQUENCE {",
        "  criticalExtensions  CHOICE {",
        "    rrcConnectionRequest-r8  SEQUENCE {",
        "      ue-Identity       InitialUE-Identity,",
        "      establishmentCause EstablishmentCause,",
        "      spare             BIT STRING (SIZE (1))",
        "    },",
        "    criticalExtensionsFuture CHOICE { ... }",
        "  }",
        "}",
        "EstablishmentCause ::= ENUMERATED {",
        "  emergency, highPriorityAccess, mt-Access,",
        "  mo-Signalling, mo-Data, delayTolerant-v1020,",
        "  mo-VoiceCall-v1280, spare1 }  -- 8 значень"
    ]
    for i, line in enumerate(schema_lines):
        f.append(text(55, 150 + i * 18, line, size=11, color=INK, anchor="start"))

    # Пояснення праворуч (розрахунок бітів)
    f.append(rect(420, 100, 600, 310, fill=WARM, stroke="#f0c38c", sw=1.2, rx=8))
    f.append(text(435, 126, "Розподіл бітів у невирівняному потоці UPER", size=13, color=ACCENT_ORANGE, anchor="start", bold=True))

    fields_desc = [
        ("CHOICE index (criticalExtensions)", "1 біт", "значення 0 (rrcConnectionRequest-r8 з двох альтернатив)", ACCENT_BLUE),
        ("ue-Identity CHOICE tag", "1 біт", "значення 0 (s-TMSI проти randomValue)", ACCENT_GREEN),
        ("s-TMSI (MMEC + M-TMSI)", "40 бітів", "8 бітів MMEC + 32 біти M-TMSI (цілі фіксованої довжини)", INK),
        ("establishmentCause (ENUMERATED)", "3 біти", "ceil(log2(8)) = 3 біти для вибору 1 з 8 причин виклику", ACCENT_ORANGE),
        ("spare (BIT STRING SIZE(1))", "1 біт", "рівно 1 біт конфігурації, без префікса довжини", ACCENT_RED),
        ("Загальна довжина PDU", "46 бітів", "5 повних байтів + 6 бітів у шостому байті (хвіст доповнюється 2 нулями)", INK),
    ]

    for i, (name, bits, comment, col) in enumerate(fields_desc):
        y = 154 + i * 42
        f.append(fitbox(435, y, 220, 32, name, size=11, fill="#ffffff", stroke=col, bold=True))
        f.append(fitbox(665, y, 70, 32, bits, size=11, fill=col, color="#ffffff", bold=True))
        f.append(text(745, y + 20, comment, size=10, color=MUTED, anchor="start"))

    # Нижня частина: Бітова стрічка по байтах
    f.append(rect(40, 430, 980, 210, fill=GRAY_BG, stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(55, 455, "Розкладка бітів у 6 байтах корисного навантаження (46 бітів даних + 2 нульові біти вирівнювання PDU):", size=12, color=INK, anchor="start", bold=True))

    byte_x0 = 60
    byte_w = 140
    gap = 12

    bytes_data = [
        ("Байт 0 (0x3A)", [("C:0", 1, ACCENT_BLUE), ("U:0", 1, ACCENT_GREEN), ("M[39..34]", 6, INK)]),
        ("Байт 1 (0x8F)", [("M[33..26] (8 бітів)", 8, INK)]),
        ("Байт 2 (0x02)", [("M[25..18] (8 бітів)", 8, INK)]),
        ("Байт 3 (0x41)", [("M[17..10] (8 бітів)", 8, INK)]),
        ("Байт 4 (0x1C)", [("M[9..2] (8 бітів)", 8, INK)]),
        ("Байт 5 (0x94)", [("M[1..0]", 2, INK), ("Cause", 3, ACCENT_ORANGE), ("S:1", 1, ACCENT_RED), ("00", 2, MUTED)]),
    ]

    for b_idx, (b_title, subfields) in enumerate(bytes_data):
        bx = byte_x0 + b_idx * (byte_w + gap)
        by = 475
        f.append(rect(bx, by, byte_w, 140, fill="#ffffff", stroke="#c8d6ea", sw=1.2, rx=6))
        f.append(text(bx + byte_w / 2, by + 20, b_title, size=11, color=INK, bold=True))

        cur_x = bx + 6
        avail_w = byte_w - 12
        for sf_title, span, c in subfields:
            w_part = avail_w * (span / 8.0)
            f.append(rect(cur_x, by + 35, w_part, 60, fill=SOFT if c != MUTED else "#eeeeee", stroke=c, sw=1.2, rx=4))
            txt_size = 9 if w_part < 45 else 10
            f.append(text(cur_x + w_part / 2, by + 62, sf_title, size=txt_size, color=c, bold=True))
            f.append(text(cur_x + w_part / 2, by + 82, f"{span}б", size=9, color=MUTED))
            cur_x += w_part

        f.append(text(bx + byte_w / 2, by + 120, "Біти 7..0", size=9, color=MUTED))

    render(os.path.join(OUT, 'per-bitstream-layout.svg'), W, H, *f,
           title="Анатомія бітового потоку UPER для повідомлення ASN.1")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Порівняння вирівнювання UPER проти APER
# ─────────────────────────────────────────────────────────────────────────────
def fig_uper_vs_aper():
    W, H = 1060, 620
    f = []

    f.append(rect(20, 20, 1020, 580, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    f.append(text(40, 52, "Невирівняний (UPER) проти Вирівняного (APER) режимів кодування", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Як правила вирівнювання додають паддінг-біти до межі октету для полів розміром понад 2 байти", size=12, color=MUTED, anchor="start"))

    # Приклад структури ASN.1
    f.append(rect(40, 100, 980, 65, fill=GRAY_BG, stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(55, 122, "Тестова структура ASN.1:", size=11, color=MUTED, anchor="start", bold=True))
    f.append(text(55, 145, "Example ::= SEQUENCE { flag BOOLEAN, code INTEGER (0..7), tag INTEGER (0..65535), data OCTET STRING (SIZE(3)) }", size=11, color=INK, anchor="start"))

    # UPER Панель
    f.append(rect(40, 180, 980, 185, fill=COOL, stroke="#a3d9b1", sw=1.4, rx=8))
    f.append(text(55, 205, "UPER (UNALIGNED PER) — Пакування біт-у-біт без вирівнювання", size=13, color=ACCENT_GREEN, anchor="start", bold=True))
    f.append(text(55, 225, "Суцільний потік: 1 біт (flag) + 3 біти (code) + 16 бітів (tag) + 24 біти (data) = 44 біти (5.5 байтів)", size=11, color=MUTED, anchor="start"))

    uper_blocks = [
        ("flag\n(1 біт)", 80, ACCENT_BLUE),
        ("code\n(3 біти)", 100, ACCENT_ORANGE),
        ("tag: INTEGER (0..65535)\n(16 бітів)", 230, ACCENT_GREEN),
        ("data: OCTET STRING SIZE(3)\n(24 біти = 3 октети)", 340, INK),
        ("паддінг кадру\n(4 біти нулів)", 110, MUTED),
    ]

    ux = 55
    for title, w_box, col in uper_blocks:
        f.append(fitbox(ux, 245, w_box, 65, title, size=11, fill="#ffffff", stroke=col, bold=True))
        ux += w_box + 10

    f.append(text(55, 345, "Підсумок UPER: рівно 6 байтів у каналі (44 біти корисних + 4 біти фінального доповнення кадру)", size=11, color=ACCENT_GREEN, anchor="start", bold=True))

    # APER Панель
    f.append(rect(40, 380, 980, 200, fill=WARM, stroke="#f0c38c", sw=1.4, rx=8))
    f.append(text(55, 405, "APER (ALIGNED PER) — Обов'язкове вирівнювання перед полями довжиною > 2 байти та великими цілими", size=13, color=ACCENT_ORANGE, anchor="start", bold=True))
    f.append(text(55, 425, "Поля <= 255 не вирівнюються, але діапазон 65536 вимагає вирівнювання на межу октету перед записом значення", size=11, color=MUTED, anchor="start"))

    aper_blocks = [
        ("flag\n(1 біт)", 80, ACCENT_BLUE, False),
        ("code\n(3 біти)", 100, ACCENT_ORANGE, False),
        ("паддінг октету\n(4 біти до межі)", 120, ACCENT_RED, True),
        ("tag: INTEGER (0..65535)\n(16 бітів = 2 октети)", 230, ACCENT_GREEN, False),
        ("data: OCTET STRING SIZE(3)\n(24 біти = 3 октети)", 320, INK, False),
    ]

    ax = 55
    for title, w_box, col, is_pad in aper_blocks:
        bg = "#ffebeb" if is_pad else "#ffffff"
        f.append(fitbox(ax, 445, w_box, 65, title, size=11, fill=bg, stroke=col, bold=True))
        ax += w_box + 10

    f.append(text(55, 545, "Підсумок APER: 6 байтів, але структура чітко розбита по байтах: Байт 0 = [flag+code+pad], Байти 1-2 = tag, Байти 3-5 = data", size=11, color=ACCENT_ORANGE, anchor="start", bold=True))
    f.append(text(55, 565, "Перевага APER: швидший розбір процесором (пряме копіювання memcpy для октетних масивів), ціна — надлишкові біти паддінгу", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'uper-vs-aper-alignment.svg'), W, H, *f,
           title="Порівняння упакування бітів у UPER та APER")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Детермінанти довжини та фрагментація великих полів у PER
# ─────────────────────────────────────────────────────────────────────────────
def fig_length_fragmentation():
    W, H = 1060, 640
    f = []

    f.append(rect(20, 20, 1020, 600, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    f.append(text(40, 52, "Кодування довжини та механізм фрагментації у PER (ITU-T X.691)", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Три діапазони довжини: короткий (0..127), середній (128..16K-1) та фрагментований блоками (16K..64K)", size=12, color=MUTED, anchor="start"))

    # 1. Коротка форма
    f.append(rect(40, 100, 980, 120, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(55, 125, "1. Коротка форма (довжина n ∈ [0 .. 127]): 1 октет", size=13, color=ACCENT_BLUE, anchor="start", bold=True))
    f.append(fitbox(55, 145, 140, 55, "Біт 7 = 0\n(ознака короткої)", size=11, fill="#ffffff", stroke=ACCENT_BLUE, bold=True))
    f.append(fitbox(205, 145, 260, 55, "Біти 6..0 = n (7 бітів значення довжини)\nДіапазон: 0 .. 127 елементів", size=11, fill="#ffffff", stroke=ACCENT_BLUE))
    f.append(fitbox(475, 145, 525, 55, "Корисні дані: n елементів (символи, октети або елементи списку)", size=11, fill=COOL, stroke=ACCENT_GREEN))

    # 2. Середня форма
    f.append(rect(40, 235, 980, 120, fill=WARM, stroke="#f0c38c", sw=1.2, rx=8))
    f.append(text(55, 260, "2. Середня форма (довжина n ∈ [128 .. 16383]): 2 октети (14 бітів)", size=13, color=ACCENT_ORANGE, anchor="start", bold=True))
    f.append(fitbox(55, 280, 140, 55, "Біти 15..14 = 10₂\n(ознака 2 октетів)", size=11, fill="#ffffff", stroke=ACCENT_ORANGE, bold=True))
    f.append(fitbox(205, 280, 260, 55, "Біти 13..0 = n (14 бітів значення)\nДіапазон: 128 .. 16 383 елементів", size=11, fill="#ffffff", stroke=ACCENT_ORANGE))
    f.append(fitbox(475, 280, 525, 55, "Корисні дані: n елементів безпосередньо за заголовком", size=11, fill=COOL, stroke=ACCENT_GREEN))

    # 3. Фрагментована форма
    f.append(rect(40, 370, 980, 230, fill=GRAY_BG, stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(55, 395, "3. Фрагментована форма (довжина n ≥ 16384): блоками по 16K, 32K, 48K або 64K елементів", size=13, color=ACCENT_RED, anchor="start", bold=True))
    f.append(text(55, 415, "Префікс 11₂ + 6 бітів множника m ∈ {1, 2, 3, 4} задають блок розміром m × 16384 (16K..64K). Процес повторюється до залишку < 16K.", size=11, color=MUTED, anchor="start"))

    # Блок 1
    f.append(fitbox(55, 445, 150, 55, "Префікс 11000100₂\n(4 × 16K = 64K)", size=10, fill="#ffffff", stroke=ACCENT_RED, bold=True))
    f.append(fitbox(215, 445, 250, 55, "Фрагмент 1: 65 536 елементів\n(перший великий шматок)", size=10, fill=COOL, stroke=ACCENT_GREEN))

    # Стрілка між блоками
    f.append(arrow(475, 472, 505, 472, color=MUTED, sw=2))

    # Блок 2
    f.append(fitbox(515, 445, 150, 55, "Префікс 11000001₂\n(1 × 16K = 16K)", size=10, fill="#ffffff", stroke=ACCENT_RED, bold=True))
    f.append(fitbox(675, 445, 220, 55, "Фрагмент 2: 16 384 елементів\n(другий шматок)", size=10, fill=COOL, stroke=ACCENT_GREEN))

    # Стрілка до фіналу
    f.append(arrow(905, 472, 935, 472, color=MUTED, sw=2))

    # Блок 3 (фінальний залишок)
    f.append(fitbox(55, 520, 150, 55, "Залишок < 16K\n(наприклад, 0x1F = 31)", size=10, fill="#ffffff", stroke=ACCENT_BLUE, bold=True))
    f.append(fitbox(215, 520, 250, 55, "Фрагмент 3: 31 елемент\n(коротка форма 0..127)", size=10, fill=COOL, stroke=ACCENT_GREEN))
    f.append(fitbox(475, 520, 525, 55, "Кінець потоку: декодер зшиває фрагменти 64K + 16K + 31 = 81 951 елемент без виділення невідомого обсягу пам'яті наперед", size=10, fill=SOFT, stroke=ACCENT_BLUE))

    render(os.path.join(OUT, 'per-length-fragmentation.svg'), W, H, *f,
           title="Детермінанти довжини та фрагментація великих полів у PER")


if __name__ == "__main__":
    fig_per_bitstream_layout()
    fig_uper_vs_aper()
    fig_length_fragmentation()
    print("Всі фігури згенеровано успішно.")
