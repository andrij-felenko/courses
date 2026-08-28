# -*- coding: utf-8 -*-
"""Фігури для теми «Чим виріб відрізняється від прототипу» (chym-vyrib-vidrizniaietsia-vid-prototypu).
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox, textbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Палітра теми
PROTO_COLOR = "#b45309"   # теплий янтар / прототип / макет
PROD_COLOR  = "#047857"   # смарагдовий / серійний виріб
WARN_COLOR  = "#b91c1c"   # червоний / відмова, загроза
BLUE_COLOR  = "#1d4ed8"   # синій / шини, тестовий стенд
CARD_BG     = "#ffffff"


def fig_prototype_vs_product_gap():
    """1. prototype-vs-product-gap.svg — Прірва між лабораторним прототипом і серійним виробом."""
    W, H = 840, 500
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Прірва між прототипом (N = 1) та серійним виробом (N = 10 000)", size=16, color=INK, bold=True))

    # Ліва колонка: Прототип
    lx, ly, lw, lh = 30, 65, 350, 410
    parts.append(rect(lx, ly, lw, lh, fill=CARD_BG, stroke=PROTO_COLOR, sw=2, rx=8))
    parts.append(rect(lx, ly, lw, 36, fill="#fef3c7", stroke=PROTO_COLOR, sw=1.5, rx=8))
    parts.append(text(lx + lw / 2, ly + 23, "Лабораторний прототип (Макет)", size=14, color=PROTO_COLOR, bold=True))

    proto_rows = [
        ("Умови середовища:", "+22°C, сухий стіл, без вібрацій та пилу"),
        ("Електроживлення:", "Лабораторний БЖ з чистим струмом (0.01% пульсацій)"),
        ("Варіативність (N=1):", "Підібраний авторкою єдиний «золотий» зразок"),
        ("Схемотехніка:", "Девборди, відкриті джемпери, без TVS/ESD захисту"),
        ("Прошивка:", "Лінійний код «happy path», delay(), SWD відкритий"),
        ("Виробництво:", "Ручне паяння, відсутність тестових точок (DFT)"),
        ("Обслуговування:", "Оновлення кабелем, нуль діагностики збоїв")
    ]

    for i, (hdr, val) in enumerate(proto_rows):
        cy = ly + 62 + i * 48
        parts.append(text(lx + 15, cy, "• " + hdr, size=11, color=PROTO_COLOR, anchor="start", bold=True))
        parts.append(text(lx + 25, cy + 18, val, size=11, color=INK, anchor="start"))

    # Права колонка: Серійний виріб
    rx, ry, rw, rh = 460, 65, 350, 410
    parts.append(rect(rx, ry, rw, rh, fill=CARD_BG, stroke=PROD_COLOR, sw=2, rx=8))
    parts.append(rect(rx, ry, rw, 36, fill="#d1fae5", stroke=PROD_COLOR, sw=1.5, rx=8))
    parts.append(text(rx + rw / 2, ry + 23, "Серійний виріб (Продукт)", size=14, color=PROD_COLOR, bold=True))

    prod_rows = [
        ("Умови середовища:", "Від -40°C до +85°C, конденсат, вібрації, удари"),
        ("Електроживлення:", "Імпульсні перешкоди, load dump до 40 В, просадки"),
        ("Варіативність (N=10k):", "Worst-case аналіз, кути кремнію (Process Corners)"),
        ("Схемотехніка:", "Власна PCB, TVS-діоди на портах, DFM/DFA норми"),
        ("Прошивка:", "Автомати станів, WDT, BOR, розблокування шин"),
        ("Виробництво:", "Автоматичний стенд (Bed-of-Nails), тестові точки"),
        ("Обслуговування:", "FOTA з двома банками (A/B), шифрування, логи")
    ]

    for i, (hdr, val) in enumerate(prod_rows):
        cy = ry + 62 + i * 48
        parts.append(text(rx + 15, cy, "✓ " + hdr, size=11, color=PROD_COLOR, anchor="start", bold=True))
        parts.append(text(rx + 25, cy + 18, val, size=11, color=INK, anchor="start"))

    # Центральна стрілка переходу
    parts.append(arrow(lx + lw + 6, ly + lh / 2 - 25, rx - 6, ry + rh / 2 - 25, color="#64748b", sw=2.5))
    parts.append(text(W / 2, ly + lh / 2, "ПЕРЕХІД ДО", size=10, color="#64748b", bold=True))
    parts.append(text(W / 2, ly + lh / 2 + 16, "СЕРІЇ", size=10, color="#64748b", bold=True))

    render(out("prototype-vs-product-gap.svg"), W, H, *parts)


def fig_worst_case_corners():
    """2. worst-case-corners.svg — Простір варіативності: кремнієві кути, живлення та температура."""
    W, H = 840, 480
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Простір варіативності: робочий конверт серійного виробу", size=16, color=INK, bold=True))

    # Центральний блок: Вісь координат і три виміри
    # Ліва частина: опис кутів напівпровідника
    bx, by, bw, bh = 30, 65, 370, 390
    parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke="#3b82f6", sw=1.5, rx=8))
    parts.append(rect(bx, by, bw, 32, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=8))
    parts.append(text(bx + bw / 2, by + 21, "1. Кремнієві кути (Process Corners)", size=13, color=BLUE_COLOR, bold=True))

    corners_info = [
        ("Fast-Fast (FF):", "Транзистори відкриваються надшвидко."),
        ("", "Ризик: гонки сигналів (Hold Time), великі струми витоку."),
        ("Slow-Slow (SS):", "Транзистори перемикаються із запізненням."),
        ("", "Ризик: порушення Setup Time, провал максимальної частоти."),
        ("Typical-Typical (TT):", "Номінальний зразок з лабораторії."),
        ("", "Працює на столі, але не гарантує роботу країв серії."),
        ("Cross (FS / SF):", "Різна швидкість P- та N-канальних польовиків."),
        ("", "Ризик: зміщення порогу логічних рівнів і тривалості фронтів.")
    ]
    for i, (hdr, val) in enumerate(corners_info):
        cy = by + 56 + i * 40
        if hdr:
            parts.append(text(bx + 15, cy, "• " + hdr, size=11, color=BLUE_COLOR, anchor="start", bold=True))
        if val:
            parts.append(text(bx + 25, cy + 18, val, size=10, color=INK, anchor="start"))

    # Права частина: Зовнішні фактори (Температура + Живлення + Пасивні компоненти)
    rx, ry, rw, rh = 430, 65, 380, 390
    parts.append(rect(rx, ry, rw, rh, fill=CARD_BG, stroke=WARN_COLOR, sw=1.5, rx=8))
    parts.append(rect(rx, ry, rw, 32, fill="#fee2e2", stroke=WARN_COLOR, sw=1.2, rx=8))
    parts.append(text(rx + rw / 2, ry + 21, "2. Зовнішній конверт і толеранси", size=13, color=WARN_COLOR, bold=True))

    env_info = [
        ("Температурний діапазон (-40°C .. +85°C):", "Зміна опору міді на 50%, падіння ємності MLCC,"),
        ("", "дрейф кварцового резонатора до ±50 ppm."),
        ("Нестабільність напруги (V_min .. V_max):", "Просідання шини під час радіопередачі,"),
        ("", "викиди індуктивності при комутації навантажень."),
        ("DC Bias ефект керамічних конденсаторів:", "Падіння реальної ємності на 40-70% під напругою,"),
        ("", "зростання пульсацій живлення втричі."),
        ("Worst-Case Analysis (WCA):", "Розрахунок схеми для найгіршої комбінації:"),
        ("", "SS кремній + V_min + T_max + толеранси R/C ±10%.")
    ]
    for i, (hdr, val) in enumerate(env_info):
        cy = ry + 56 + i * 40
        if hdr:
            parts.append(text(rx + 15, cy, "• " + hdr, size=11, color=WARN_COLOR, anchor="start", bold=True))
        if val:
            parts.append(text(rx + 25, cy + 18, val, size=10, color=INK, anchor="start"))

    render(out("worst-case-corners.svg"), W, H, *parts)


def fig_factory_test_jig_flow():
    """3. factory-test-jig-flow.svg — Автоматизований заводський тестовий стенд (Bed-of-Nails) та конвеєр прошивки."""
    W, H = 840, 460
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Заводський стенд прошивки й тестування (Bed-of-Nails / ICT)", size=16, color=INK, bold=True))

    # Схема кроків тестування (4 кроки зліва направо)
    steps = [
        ("1. Перевірка живлення", "#b91c1c", "#fee2e2", [
            "• Опір шин на GND",
            "• Тест на коротке замикання",
            "• Струм споживання у спокої",
            "• Захист від згоряння стенда"
        ]),
        ("2. SWD / Flashing", "#1d4ed8", "#dbeafe", [
            "• Підключення через SWD/JTAG",
            "• Запис Bootloader + Firmware",
            "• Верифікація контрольної суми",
            "• Запис серійного номера (UUID)"
        ]),
        ("3. Калібрування та ключі", "#047857", "#d1fae5", [
            "• Калібрування опори АЦП",
            "• Генерація унікальних ключів",
            "• Запис криптографічних eFuse",
            "• Тест радіочастотного тракту"
        ]),
        ("4. Логічний тест і фіксація", "#475569", "#f1f5f9", [
            "• Функціональний самотест",
            "• Замикання зневаджувача (RDP)",
            "• Формування заводського логу",
            "• Друк паспорта виробу"
        ])
    ]

    card_w = 180
    card_h = 240
    start_x = 28
    gap = 24
    card_y = 65

    for i, (title, strk, fill_hdr, items) in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        # Картка
        parts.append(rect(cx, card_y, card_w, card_h, fill=CARD_BG, stroke=strk, sw=1.5, rx=8))
        parts.append(rect(cx, card_y, card_w, 36, fill=fill_hdr, stroke=strk, sw=1.2, rx=8))
        parts.append(text(cx + card_w / 2, card_y + 23, title, size=11, color=strk, bold=True))

        for j, itm in enumerate(items):
            parts.append(text(cx + 10, card_y + 60 + j * 42, itm, size=10, color=INK, anchor="start"))

        # Стрілка до наступного кроку
        if i < len(steps) - 1:
            arr_x1 = cx + card_w + 3
            arr_x2 = cx + card_w + gap - 3
            arr_y = card_y + card_h / 2
            parts.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color="#64748b", sw=2))

    # Нижня плашка: Апаратні вимоги до друкованої плати (DFT)
    bot_x, bot_y, bot_w, bot_h = 28, 320, 784, 115
    parts.append(rect(bot_x, bot_y, bot_w, bot_h, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=8))
    parts.append(rect(bot_x, bot_y, bot_w, 28, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=8))
    parts.append(text(bot_x + bot_w / 2, bot_y + 19, "Вимоги проєктування для тестованості (DFT — Design for Testability)", size=12, color="#0369a1", bold=True))

    dft_notes = [
        "1. Тестові точки (Test Points) діаметром 1.0 мм розміщуються виключно на нижньому шарі друкованої плати.",
        "2. Крок між тестовими точками становить не менше 1.27 мм (рекомендовано 2.54 мм) для точності голчастих зондів.",
        "3. Обов'язкова наявність двох технологічних отворів позиціонування (Fiducial / Tooling Holes) без металізації.",
        "4. Загальний цикл тестування та первинної прошивки одного екземпляра не повинен перевищувати 15-30 секунд."
    ]
    for k, note in enumerate(dft_notes):
        parts.append(text(bot_x + 15, bot_y + 46 + k * 18, note, size=10, color=INK, anchor="start"))

    render(out("factory-test-jig-flow.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_prototype_vs_product_gap()
    fig_worst_case_corners()
    fig_factory_test_jig_flow()
    print("All figures generated successfully.")
