# -*- coding: utf-8 -*-
"""Фігури для теми «Скарга, яка не є звітом про помилку» (skarha-iaka-ne-ie-zvitom-pro-pomylku).
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
COLOR_COMPLAINT = "#b45309"  # теплий янтар / суб'єктивна скарга
COLOR_TELEMETRY = "#1d4ed8"  # синій / телеметрія й логи
COLOR_HARDWARE  = "#047857"  # зелений / апаратна ревізія, BOM
COLOR_RCA       = "#7c3aed"  # фіолетовий / коренева причина, RCA
COLOR_ALERT     = "#b91c1c"  # червоний / аномалія, збій
COLOR_BG_CARD   = "#ffffff"


def fig_complaint_to_rca_pipeline():
    """1. complaint-to-rca-pipeline.svg — Конвеєр перетворення скарги на інженерний факт."""
    W, H = 860, 490
    parts = []

    # Фон полотна
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Конвеєр перетворення скарги користувача на технічне рішення", size=16, color=INK, bold=True))

    # 4 послідовні етапи конвеєра
    stages = [
        {
            "num": "01",
            "title": "Суб'єктивна скарга",
            "subtitle": "«Воно зависає / гріється»",
            "color": COLOR_COMPLAINT,
            "bg": "#fef3c7",
            "items": [
                "• Емоційне сприйняття збою",
                "• Відсутність метрик і таймінгів",
                "• Невідомий стан живлення",
                "• Опис лише зовнішнього симптому"
            ]
        },
        {
            "num": "02",
            "title": "Емпіричний переклад",
            "subtitle": "Фізичні та логічні координати",
            "color": COLOR_TELEMETRY,
            "bg": "#dbeafe",
            "items": [
                "• Зчитування RCC_CSR та WDT",
                "• Снапшот регістрації помилок",
                "• Запис просідання шини VDD",
                "• Зафіксований таймаут I2C"
            ]
        },
        {
            "num": "03",
            "title": "Тріангуляція даних",
            "subtitle": "Синтез трьох джерел",
            "color": COLOR_HARDWARE,
            "bg": "#d1fae5",
            "items": [
                "• Логи Blackbox та Core Dump",
                "• Ревізія плати та партія BOM",
                "• Профіль живлення й температури",
                "• Кореляція з версією прошивки"
            ]
        },
        {
            "num": "04",
            "title": "Аналіз RCA та виправлення",
            "subtitle": "5 Whys + системне рішення",
            "color": COLOR_RCA,
            "bg": "#ede9fe",
            "items": [
                "• Відділення симптому від причини",
                "• Лабораторна репродукція збою",
                "• 9-SCL відновлення шини в драйвері",
                "• Запобігання у новій ревізії BOM"
            ]
        }
    ]

    card_w = 185
    card_h = 390
    start_x = 28
    gap = 24
    top_y = 65

    for i, st in enumerate(stages):
        cx = start_x + i * (card_w + gap)
        parts.append(rect(cx, top_y, card_w, card_h, fill=COLOR_BG_CARD, stroke=st["color"], sw=1.8, rx=8))
        parts.append(rect(cx, top_y, card_w, 54, fill=st["bg"], stroke=st["color"], sw=1.2, rx=8))
        parts.append(text(cx + card_w / 2, top_y + 20, f"КРОК {st['num']}", size=11, color=st["color"], bold=True))
        parts.append(text(cx + card_w / 2, top_y + 40, st["title"], size=12, color=INK, bold=True))

        parts.append(rect(cx + 8, top_y + 64, card_w - 16, 26, fill="#f1f5f9", stroke="#e2e8f0", sw=1, rx=4))
        parts.append(text(cx + card_w / 2, top_y + 81, st["subtitle"], size=9, color=st["color"], bold=True, italic=True))

        for j, item in enumerate(st["items"]):
            iy = top_y + 115 + j * 64
            parts.append(rect(cx + 8, iy - 14, card_w - 16, 52, fill="#fafafa", stroke="#e2e8f0", sw=1, rx=4))
            lines_item = item.split(" ")
            mid = len(lines_item) // 2
            l1 = " ".join(lines_item[:mid])
            l2 = " ".join(lines_item[mid:])
            parts.append(text(cx + 14, iy + 4, l1, size=10, color=INK, anchor="start", bold=True))
            parts.append(text(cx + 14, iy + 22, l2, size=10, color=MUTED, anchor="start"))

        if i < 3:
            arrow_x = cx + card_w + 3
            parts.append(arrow(arrow_x, top_y + card_h / 2, arrow_x + gap - 6, top_y + card_h / 2, color="#64748b", sw=2))

    render(out("complaint-to-rca-pipeline.svg"), W, H, *parts)


def fig_triangulation_three_pillars():
    """2. triangulation-three-pillars.svg — Тріангуляція інциденту з трьох джерел."""
    W, H = 840, 520
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Тріангуляція апаратного інциденту: три вектори фактів", size=16, color=INK, bold=True))

    p_w, p_h = 240, 240

    # Стовп 1: Бортові логи та діагностичні дампи
    p1_x, p1_y = 35, 70
    parts.append(rect(p1_x, p1_y, p_w, p_h, fill=COLOR_BG_CARD, stroke=COLOR_TELEMETRY, sw=2, rx=8))
    parts.append(rect(p1_x, p1_y, p_w, 36, fill="#dbeafe", stroke=COLOR_TELEMETRY, sw=1.2, rx=8))
    parts.append(text(p1_x + p_w / 2, p1_y + 23, "1. Бортовий Blackbox і логи", size=12, color=COLOR_TELEMETRY, bold=True))
    p1_items = [
        "• Прапори перезапуску (RCC_CSR)",
        "• Регістри CPU: PC, LR, CFSR",
        "• Водяні знаки стеків потоків RTOS",
        "• Лічильники I2C/SPI таймаутів",
        "• Кільцевий буфер подій перед збоєм"
    ]
    for k, it in enumerate(p1_items):
        parts.append(text(p1_x + 12, p1_y + 60 + k * 35, it, size=10, color=INK, anchor="start"))

    # Стовп 2: Родовід заліза та BOM
    p2_x, p2_y = 565, 70
    parts.append(rect(p2_x, p2_y, p_w, p_h, fill=COLOR_BG_CARD, stroke=COLOR_HARDWARE, sw=2, rx=8))
    parts.append(rect(p2_x, p2_y, p_w, 36, fill="#d1fae5", stroke=COLOR_HARDWARE, sw=1.2, rx=8))
    parts.append(text(p2_x + p_w / 2, p2_y + 23, "2. Ревізія заліза та BOM", size=12, color=COLOR_HARDWARE, bold=True))
    p2_items = [
        "• Ревізія друкованої плати (PCB rev)",
        "• Партія та датакод компонентів",
        "• Альтернативний вендор LDO / Flash",
        "• Номінали підтягуючих резисторів",
        "• Відомі кремнієві Errata процесора"
    ]
    for k, it in enumerate(p2_items):
        parts.append(text(p2_x + 12, p2_y + 60 + k * 35, it, size=10, color=INK, anchor="start"))

    # Стовп 3: Профіль флоту й телеметрія
    p3_x, p3_y = 300, 325
    parts.append(rect(p3_x, p3_y, p_w, 170, fill=COLOR_BG_CARD, stroke=COLOR_COMPLAINT, sw=2, rx=8))
    parts.append(rect(p3_x, p3_y, p_w, 36, fill="#fef3c7", stroke=COLOR_COMPLAINT, sw=1.2, rx=8))
    parts.append(text(p3_x + p_w / 2, p3_y + 23, "3. Телеметрія середовища", size=12, color=COLOR_COMPLAINT, bold=True))
    p3_items = [
        "• Гістограма просідань напруги батареї",
        "• Профіль температури кристала й плати",
        "• Рівень шуму RSSI та якість радіозв'язку",
        "• Історія циклів сну / пробудження"
    ]
    for k, it in enumerate(p3_items):
        parts.append(text(p3_x + 12, p3_y + 60 + k * 28, it, size=10, color=INK, anchor="start"))

    # Центральне ядро: Синтез і встановлення причини
    c_x, c_y, c_w, c_h = 300, 110, 240, 160
    parts.append(rect(c_x, c_y, c_w, c_h, fill="#ede9fe", stroke=COLOR_RCA, sw=2.5, rx=10))
    parts.append(text(c_x + c_w / 2, c_y + 30, "ВСТАНОВЛЕНИЙ ІНЖЕНЕРНИЙ ФАКТ", size=11, color=COLOR_RCA, bold=True))
    parts.append(line(c_x + 20, c_y + 44, c_x + c_w - 20, c_y + 44, color=COLOR_RCA, sw=1.2))
    parts.append(text(c_x + c_w / 2, c_y + 70, "Точний стан апарата під час збою:", size=10, color=INK, bold=True))
    parts.append(text(c_x + c_w / 2, c_y + 92, "V_bat=3.12V, T=+63°C, PCB rev B", size=10, color=COLOR_ALERT, bold=True))
    parts.append(text(c_x + c_w / 2, c_y + 114, "I2C SDA зависла через 10k pullup", size=10, color=INK))
    parts.append(text(c_x + c_w / 2, c_y + 136, "Повна відтворюваність на стенді", size=10, color=COLOR_HARDWARE, bold=True))

    # Стрілки збіжності
    parts.append(arrow(p1_x + p_w, p1_y + 90, c_x - 5, c_y + 50, color=COLOR_TELEMETRY, sw=2.2))
    parts.append(arrow(p2_x, p2_y + 90, c_x + c_w + 5, c_y + 50, color=COLOR_HARDWARE, sw=2.2))
    parts.append(arrow(p3_x + p_w / 2, p3_y - 5, c_x + c_w / 2, c_y + c_h + 5, color=COLOR_COMPLAINT, sw=2.2))

    render(out("triangulation-three-pillars.svg"), W, H, *parts)


def fig_five_whys_embedded_rca():
    """3. five-whys-embedded-rca.svg — Дерево аналізу кореневої причини (5 Whys) для embedded."""
    W, H = 840, 520
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Аналіз кореневої причини (5 Whys) у вбудованій системі", size=16, color=INK, bold=True))

    levels = [
        {
            "lvl": "Симптом (Скарга)",
            "q": "Що бачить користувач?",
            "ans": "«Пристрій зависає раз на 24 години і припиняє передавати телеметрію»",
            "color": COLOR_COMPLAINT,
            "bg": "#fef3c7"
        },
        {
            "lvl": "Чому №1 (Скидання)",
            "q": "Чому пристрій перестав відповідати?",
            "ans": "Сторожовий таймер (IWDG) перезавантажив MCU через блокування головного циклу",
            "color": COLOR_ALERT,
            "bg": "#fee2e2"
        },
        {
            "lvl": "Чому №2 (Блокування)",
            "q": "Чому головний цикл заблокувався?",
            "ans": "Драйвер датчика температури/вологості завис у циклі очікування біта RXNE на шині I2C",
            "color": COLOR_TELEMETRY,
            "bg": "#dbeafe"
        },
        {
            "lvl": "Чому №3 (Апаратна лінія)",
            "q": "Чому лінія шини I2C не відповіла?",
            "ans": "Лінія SDA залишилась затиснутою в '0' зовнішнім сенсором через скидання сенсора при передачі",
            "color": COLOR_HARDWARE,
            "bg": "#d1fae5"
        },
        {
            "lvl": "Чому №4 (Просадка й таймінг)",
            "q": "Чому сенсор збився, а MCU не відновив шину?",
            "ans": "Імпульс радіомодуля просадив лінію VDD_SENS, а в драйвері не було 9-SCL процедури розблокування",
            "color": COLOR_RCA,
            "bg": "#ede9fe"
        },
        {
            "lvl": "Чому №5 (Коренева причина)",
            "q": "У чому фундаментальна причина відмови?",
            "ans": "У ревізії B радіо і датчики об'єднали на один LDO без запасу ємності, а драйвер не мав таймаутів",
            "color": "#0f766e",
            "bg": "#ccfbf1"
        }
    ]

    card_h = 60
    start_y = 65
    gap_y = 15
    card_w = 780
    card_x = (W - card_w) / 2

    for i, lv in enumerate(levels):
        cy = start_y + i * (card_h + gap_y)
        parts.append(rect(card_x, cy, card_w, card_h, fill=lv["bg"], stroke=lv["color"], sw=1.8, rx=6))

        # Тег рівня зліва
        parts.append(rect(card_x + 8, cy + 8, 175, card_h - 16, fill=COLOR_BG_CARD, stroke=lv["color"], sw=1.2, rx=4))
        parts.append(text(card_x + 95, cy + 24, lv["lvl"], size=10, color=lv["color"], bold=True))
        parts.append(text(card_x + 95, cy + 42, lv["q"], size=9, color=MUTED, bold=True))

        # Відповідь справа
        parts.append(text(card_x + 198, cy + 34, lv["ans"], size=11, color=INK, anchor="start", bold=(i >= 4)))

        # Стрілочка вниз між картками
        if i < 5:
            arrow_y = cy + card_h
            parts.append(arrow(W / 2, arrow_y, W / 2, arrow_y + gap_y - 2, color="#64748b", sw=1.8))

    render(out("five-whys-embedded-rca.svg"), W, H, *parts)


def fig_incident_snapshot_frame():
    """4. incident-snapshot-frame.svg — Структура бінарного дампа діагностичного знімка."""
    W, H = 840, 480
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Структура енергонезалежного дампа інциденту (Incident Snapshot Frame)", size=16, color=INK, bold=True))

    fields = [
        ("0x00..0x03", "Magic Header (0xDEADBEEF)", "Сигнатура валідності кадру та версія формату протоколу", COLOR_ALERT, "#fee2e2"),
        ("0x04..0x0B", "RTC Epoch & Boot Counter", "Мітка часу збою (Unix timestamp) та номер циклу завантаження", COLOR_TELEMETRY, "#dbeafe"),
        ("0x0C..0x0F", "Reset Flags (RCC_CSR)", "Апаратна причина: IWDG, WWDG, Brown-Out (BOR), Soft Reset, PIN", COLOR_COMPLAINT, "#fef3c7"),
        ("0x10..0x1F", "CPU Crash Context", "Регістри HardFault: PC (адреса збою), LR, CFSR, HFSR, MMFAR, BFAR", COLOR_RCA, "#ede9fe"),
        ("0x20..0x2F", "RTOS & Task State", "Ідентифікатор активного потоку, залишок стека (Stack Watermark)", COLOR_HARDWARE, "#d1fae5"),
        ("0x30..0x3F", "Hardware & Bus Counters", "Лічильники I2C NACK, SPI таймаутів, UART Frame Errors, Flash CRC", "#0f766e", "#ccfbf1"),
        ("0x40..0x4B", "Environmental Metrics", "Напруга живлення VDD (мВ), температура кристала (°C), RSSI (дБм)", "#c2410c", "#ffedd5"),
        ("0x4C..0x4F", "Frame CRC32 Checksum", "Контрольна сума захисту цілісності даних при аварійному вимкненні", "#475569", "#f1f5f9")
    ]

    card_w = 780
    card_h = 42
    start_y = 65
    gap_y = 8
    card_x = (W - card_w) / 2

    for i, (addr, title, desc, col, bg) in enumerate(fields):
        cy = start_y + i * (card_h + gap_y)
        parts.append(rect(card_x, cy, card_w, card_h, fill=bg, stroke=col, sw=1.5, rx=5))

        parts.append(rect(card_x + 6, cy + 6, 110, card_h - 12, fill=COLOR_BG_CARD, stroke=col, sw=1, rx=3))
        parts.append(text(card_x + 61, cy + 26, addr, size=11, color=col, bold=True))

        parts.append(text(card_x + 130, cy + 26, title, size=11, color=INK, anchor="start", bold=True))
        parts.append(text(card_x + 360, cy + 26, desc, size=10, color=MUTED, anchor="start"))

    render(out("incident-snapshot-frame.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_complaint_to_rca_pipeline()
    fig_triangulation_three_pillars()
    fig_five_whys_embedded_rca()
    fig_incident_snapshot_frame()
    print("Усі 4 фігури успішно згенеровано.")
