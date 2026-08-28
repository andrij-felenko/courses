# -*- coding: utf-8 -*-
"""Фігури для теми «Даташит очима програміста» (datashyt-ochyma-prohramista).
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
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG, FONT
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Кольорова палітра для апаратних блоків і типів регістрів
COLOR_RW = "#2563eb"    # синій: Read/Write
COLOR_RO = "#059669"    # зелений: Read Only
COLOR_W1C = "#d97706"   # бурштиновий: Write 1 to Clear
COLOR_COR = "#dc2626"   # червоний: Clear on Read
COLOR_BUS = "#475569"   # сланцевий: шинні сигнали
COLOR_PANEL = "#f8fafc" # світлий фон панелей
COLOR_BORDER = "#cbd5e1"


def fig_register_access_types():
    """1. register-access-types.svg — Спектр типів доступу до регістрів і пастки обробки."""
    W, H = 840, 490
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    parts.append(text(W / 2, 36, "Типи доступу до регістрів та поведінка бітів при зверненні", size=15, color=INK, bold=True))

    cards = [
        {
            "x": 25, "y": 60, "w": 380, "h": 190,
            "title": "R/W (Read / Write) — Конфігурація",
            "color": COLOR_RW, "bg": "#eff6ff",
            "lines": [
                "• Запис: зберігає значення у внутрішньому тригері.",
                "• Читання: повертає раніше записане значення.",
                "• Безпечний патерн: Read-Modify-Write (RMW).",
                "• Приклад: вибір діапазону FSR, частоти ODR, осей."
            ],
            "trap": "Пастка: не затирати біти сусідніх конфігурацій сліпим записом!"
        },
        {
            "x": 435, "y": 60, "w": 380, "h": 190,
            "title": "RO (Read Only) — Дані сенсора",
            "color": COLOR_RO, "bg": "#ecfdf5",
            "lines": [
                "• Запис: ігнорується кремнієм або викликає Bus Error.",
                "• Читання: повертає поточний вимір АЦП або лічильник.",
                "• Особливість: значення оновлюється незалежно від MCU.",
                "• Приклад: OUT_X_L, OUT_X_H, STATUS, WHO_AM_I."
            ],
            "trap": "Пастка: без блокування (BDU) байти X_L і X_H роз'їжджаються."
        },
        {
            "x": 25, "y": 270, "w": 380, "h": 195,
            "title": "W1C (Write 1 to Clear) — Прапорці",
            "color": COLOR_W1C, "bg": "#fffbeb",
            "lines": [
                "• Запис '1': скидає прапорець переривання в 0.",
                "• Запис '0': залишає стан прапорця без змін.",
                "• Читання: показує поточний активний статус.",
                "• Правильний запис: write_reg(STATUS, FLAG_BIT);"
            ],
            "trap": "Критична пастка: reg &= ~FLAG стирає інші активні події!"
        },
        {
            "x": 435, "y": 270, "w": 380, "h": 195,
            "title": "COR (Clear on Read) — Автоскидання",
            "color": COLOR_COR, "bg": "#fef2f2",
            "lines": [
                "• Читання: апаратно скидає прапорець у момент транзакції.",
                "• Запис: зазвичай не має сенсу або заборонений.",
                "• Небезпека: одне читання знищує факт події.",
                "• Приклад: лічильники помилок, FIFO Watermark."
            ],
            "trap": "Пастка: вікно Watch у дебагері вичитує регістр і «краде» подію."
        }
    ]

    for c in cards:
        parts.append(rect(c["x"], c["y"], c["w"], c["h"], fill="#ffffff", stroke=c["color"], sw=1.5, rx=6))
        parts.append(rect(c["x"], c["y"], c["w"], 30, fill=c["bg"], stroke=c["color"], sw=1.2, rx=6))
        parts.append(text(c["x"] + c["w"] / 2, c["y"] + 20, c["title"], size=12, color=c["color"], bold=True))

        for idx, ln in enumerate(c["lines"]):
            parts.append(text(c["x"] + 12, c["y"] + 54 + idx * 22, ln, size=11, color=INK, anchor="start"))

        # Рамка пастки
        ty = c["y"] + 145
        parts.append(rect(c["x"] + 8, ty, c["w"] - 16, 40, fill=c["bg"], stroke=c["color"], sw=1, rx=4))
        parts.append(text(c["x"] + c["w"] / 2, ty + 24, c["trap"], size=10, color=c["color"], bold=True))

    render(out("register-access-types.svg"), W, H, *parts)


def fig_i2c_spi_transaction_anatomy():
    """2. i2c-spi-transaction-anatomy.svg — Анатомія транзакцій I2C та SPI з автоінкрементом."""
    W, H = 840, 500
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Формат транзакцій передачі та читання даних (I2C vs SPI)", size=15, color=INK, bold=True))

    # Секція I2C (вгорі)
    parts.append(text(30, 64, "1. Протокол I2C: 7-бітна адреса пристрою + суб-адреса з бітом автоінкременту", size=12, color=COLOR_RW, bold=True, anchor="start"))

    # Блоки I2C
    i2c_y = 80
    blocks_i2c = [
        {"x": 30, "w": 40, "txt": "START", "fill": "#fde047", "stroke": "#ca8a04", "sub": "S"},
        {"x": 75, "w": 120, "txt": "Device Addr [7:1]", "fill": "#dbeafe", "stroke": "#2563eb", "sub": "7 біт адреси чипа"},
        {"x": 200, "w": 35, "txt": "W", "fill": "#fee2e2", "stroke": "#dc2626", "sub": "0 (W)"},
        {"x": 240, "w": 35, "txt": "ACK", "fill": "#dcfce7", "stroke": "#16a34a", "sub": "0 від чипа"},
        {"x": 280, "w": 160, "txt": "Reg Addr | AutoInc", "fill": "#ffedd5", "stroke": "#ea580c", "sub": "Біт 7 = 1 (автоінкремент)"},
        {"x": 445, "w": 35, "txt": "ACK", "fill": "#dcfce7", "stroke": "#16a34a", "sub": "0 від чипа"},
        {"x": 485, "w": 40, "txt": "RESTART", "fill": "#fde047", "stroke": "#ca8a04", "sub": "Sr"},
        {"x": 530, "w": 120, "txt": "Device Addr [7:1]", "fill": "#dbeafe", "stroke": "#2563eb", "sub": "7 біт адреси чипа"},
        {"x": 655, "w": 35, "txt": "R", "fill": "#dbeafe", "stroke": "#2563eb", "sub": "1 (R)"},
        {"x": 695, "w": 35, "txt": "ACK", "fill": "#dcfce7", "stroke": "#16a34a", "sub": "0 від чипа"},
        {"x": 735, "w": 75, "txt": "Data L / H...", "fill": "#f3e8ff", "stroke": "#9333ea", "sub": "Burst потік"}
    ]

    for b in blocks_i2c:
        parts.append(rect(b["x"], i2c_y, b["w"], 38, fill=b["fill"], stroke=b["stroke"], sw=1.2, rx=4))
        parts.append(text(b["x"] + b["w"] / 2, i2c_y + 22, b["txt"], size=10, color=INK, bold=True))
        parts.append(text(b["x"] + b["w"] / 2, i2c_y + 54, b["sub"], size=9, color=MUTED))

    # Секція SPI (посередині)
    spi_y = 175
    parts.append(text(30, spi_y - 12, "2. Протокол SPI: повнодуплексний обмін з активним рівнем CS = LOW", size=12, color=COLOR_RO, bold=True, anchor="start"))

    # Лінії SPI сигналів
    signals = [
        {"name": "CS (NSS)", "y": spi_y + 10, "desc": "Активний низький рівень на весь час транзакції"},
        {"name": "SCK", "y": spi_y + 55, "desc": "Тактовий сигнал: режим CPOL=1/CPHA=1 або CPOL=0/CPHA=0"},
        {"name": "MOSI (SDI)", "y": spi_y + 100, "desc": "Командний байт: [R/W bit] | [AutoInc bit] | [Reg Addr 6:0]"},
        {"name": "MISO (SDO)", "y": spi_y + 145, "desc": "Вихід даних: Dummy byte під час адреси → Data Byte 0 → Data Byte 1..."}
    ]

    for s in signals:
        parts.append(rect(30, s["y"], 110, 32, fill="#f1f5f9", stroke=COLOR_BUS, sw=1.2, rx=4))
        parts.append(text(85, s["y"] + 20, s["name"], size=11, color=INK, bold=True))

        # Траса сигналу
        parts.append(rect(150, s["y"], 660, 32, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
        parts.append(text(165, s["y"] + 20, s["desc"], size=10, color=INK, anchor="start"))

    # Підсумкова виноска
    parts.append(rect(30, 375, 780, 95, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(text(420, 398, "Ключові правила читання діаграм у даташиті:", size=11, color="#0369a1", bold=True))
    rules = [
        "1. Перевіряйте, як даташит вказує I2C адресу: 7 біт (0x68) чи готовий 8-бітний байт запису (0xD0).",
        "2. Для пакетного читання (Burst Read) дізнайтеся формат біта автоінкременту (MSB=1 у ST чи окремий прапорець).",
        "3. Звірте полярність та фазу SPI (CPOL, CPHA): неправильний режим зсуває всі біти рівно на 1 такт!"
    ]
    for idx, r_txt in enumerate(rules):
        parts.append(text(45, 422 + idx * 18, r_txt, size=10, color=INK, anchor="start"))

    render(out("i2c-spi-transaction-anatomy.svg"), W, H, *parts)


def fig_endianness_and_sensor_fusion():
    """3. endianness-and-sensor-fusion.svg — Збирання 16-бітного виміру з двох регістрів та масштабування."""
    W, H = 840, 480
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Трансформація: від двох 8-бітних регістрів до фізичної величини у SI", size=15, color=INK, bold=True))

    # Крок 1: Байтові регістри на шині
    parts.append(rect(30, 65, 230, 220, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(rect(30, 65, 230, 30, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=6))
    parts.append(text(145, 85, "1. Сирі регістри чипа", size=12, color="#0369a1", bold=True))

    parts.append(rect(45, 110, 200, 38, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(145, 126, "OUT_X_L (Addr: 0x28)", size=10, color=INK, bold=True))
    parts.append(text(145, 140, "Молодший байт [7:0] = 0x5C", size=9, color=MUTED))

    parts.append(rect(45, 160, 200, 38, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(145, 176, "OUT_X_H (Addr: 0x29)", size=10, color=INK, bold=True))
    parts.append(text(145, 190, "Старший байт [15:8] = 0xFE", size=9, color=MUTED))

    parts.append(text(145, 225, "Зчитування: Burst Read", size=10, color=COLOR_RO, bold=True))
    parts.append(text(145, 245, "BDU = 1 блокує оновлення", size=9, color=MUTED))
    parts.append(text(145, 265, "поки не вичитано обидва байти", size=9, color=MUTED))

    # Стрілка 1 -> 2
    parts.append(arrow(265, 175, 305, 175, color=COLOR_BUS, sw=2))

    # Крок 2: Склеювання у 16-бітний signed int (Two's Complement)
    parts.append(rect(310, 65, 250, 220, fill="#ffffff", stroke="#7c3aed", sw=1.5, rx=6))
    parts.append(rect(310, 65, 250, 30, fill="#ede9fe", stroke="#7c3aed", sw=1.2, rx=6))
    parts.append(text(435, 85, "2. Склеювання Little-Endian", size=12, color="#6d28d9", bold=True))

    parts.append(rect(325, 110, 220, 50, fill="#f5f3ff", stroke="#8b5cf6", sw=1, rx=4))
    parts.append(text(435, 128, "int16_t raw_x = (int16_t)", size=10, color=INK, bold=True))
    parts.append(text(435, 146, "((high << 8) | low);", size=10, color=INK, bold=True))

    parts.append(text(435, 180, "Результат: 0xFE5C", size=11, color=COLOR_RW, bold=True))
    parts.append(text(435, 205, "Старший біт (біт 15) = 1", size=10, color=POS, bold=True))
    parts.append(text(435, 225, "Число від'ємне (доповняльний код)", size=9, color=MUTED))
    parts.append(text(435, 245, "Десяткове raw_x = -420 LSB", size=10, color=INK, bold=True))

    # Стрілка 2 -> 3
    parts.append(arrow(565, 175, 605, 175, color=COLOR_BUS, sw=2))

    # Крок 3: Масштабування чутливості за FSR у фізичну величину SI
    parts.append(rect(610, 65, 200, 220, fill="#ffffff", stroke="#059669", sw=1.5, rx=6))
    parts.append(rect(610, 65, 200, 30, fill="#d1fae5", stroke="#059669", sw=1.2, rx=6))
    parts.append(text(710, 85, "3. Фізичне значення (SI)", size=12, color="#047857", bold=True))

    parts.append(text(710, 118, "Full Scale: ±2g", size=10, color=INK, bold=True))
    parts.append(text(710, 138, "Чутливість (Sensitivity):", size=9, color=MUTED))
    parts.append(text(710, 155, "S = 0.061 мг/LSB", size=10, color="#047857", bold=True))

    parts.append(rect(622, 175, 176, 45, fill="#ecfdf5", stroke="#10b981", sw=1, rx=4))
    parts.append(text(710, 192, "a_x = raw_x · S · 9.80665", size=9, color=INK, bold=True))
    parts.append(text(710, 210, "a_x = -0.251 м/с²", size=11, color="#047857", bold=True))

    parts.append(text(710, 245, "Значення готове для", size=9, color=MUTED))
    parts.append(text(710, 265, "фільтрації та одометрії", size=9, color=MUTED))

    # Нижній пояснювальний блок: вирівнювання розрядності
    parts.append(rect(30, 305, 780, 150, fill="#ffffff", stroke=COLOR_BORDER, sw=1.5, rx=6))
    parts.append(text(420, 328, "Пастка вирівнювання розрядності: 12-бітні та 14-бітні давачі", size=12, color=INK, bold=True))

    parts.append(text(45, 355, "• Left-justified (вирівняно ліворуч): 12 біт лежать у бітах [15:4], молодші [3:0] — нулі. Зсув: raw = (raw_16 >> 4).", size=10, color=INK, anchor="start"))
    parts.append(text(45, 380, "• Right-justified (вирівняно праворуч): 12 біт лежать у [11:0]. Увага: пряме приведення до int16_t НЕ розширить знак!", size=10, color=POS, bold=True, anchor="start"))
    parts.append(text(45, 405, "• Правильне знакове розширення (Sign Extension): if (raw & 0x0800) raw |= 0xF000; або арифм. зсув (int16_t)(raw << 4) >> 4.", size=10, color=INK, anchor="start"))
    parts.append(text(45, 430, "• Звіряйте таблицю бітової структури (Bit Alignment) у даташиті перед написанням математики драйвера.", size=10, color=MUTED, anchor="start"))

    render(out("endianness-and-sensor-fusion.svg"), W, H, *parts)


def fig_errata_workaround_flow():
    """4. errata-workaround-flow.svg — Життєвий цикл обробки Errata та перевірка ревізії кремнію."""
    W, H = 840, 480
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Життєвий цикл апаратного дефекту: від Errata Sheet до коду драйвера", size=15, color=INK, bold=True))

    steps = [
        {
            "x": 25, "y": 65, "w": 180, "h": 260,
            "num": "Крок 1", "title": "Апаратний баг", "color": COLOR_COR, "bg": "#fef2f2",
            "items": [
                "Кремній містить дефект",
                "проєктування логіки:",
                "• I2C автомат зависає",
                "при втраті такту SCL.",
                "• DMA пропускає",
                "останній байт у burst.",
                "• Помилковий тригер",
                "переривання у сні."
            ]
        },
        {
            "x": 225, "y": 65, "w": 180, "h": 260,
            "num": "Крок 2", "title": "Errata Sheet", "color": COLOR_W1C, "bg": "#fffbeb",
            "items": [
                "Виробник публікує опис:",
                "• Bug ID: ES-042.",
                "• Уражені ревізії:",
                "Silicon Rev A, Rev B.",
                "• Умови виникнення.",
                "• Офіційний програмний",
                "обхідний шлях",
                "(Workaround)."
            ]
        },
        {
            "x": 425, "y": 65, "w": 185, "h": 260,
            "num": "Крок 3", "title": "Probe & Revision ID", "color": COLOR_RW, "bg": "#eff6ff",
            "items": [
                "Драйвер перевіряє залізо:",
                "• Зчитує WHO_AM_I.",
                "• Зчитує REV_ID чипа.",
                "• Фіксує номер партії.",
                "• Якщо ревізія з багом —",
                "активує прапорець",
                "need_workaround у",
                "структурі дескриптора."
            ]
        },
        {
            "x": 630, "y": 65, "w": 185, "h": 260,
            "num": "Крок 4", "title": "Обхідний код", "color": COLOR_RO, "bg": "#ecfdf5",
            "items": [
                "Виконання в рантаймі:",
                "• Генерація 9 тактів SCL",
                "при старті для розблоку.",
                "• Dummy Read перед DMA.",
                "• Додаткова затримка",
                "t_recovery між кадрами.",
                "• Захист від гонок",
                "статусних регістрів."
            ]
        }
    ]

    for s in steps:
        parts.append(rect(s["x"], s["y"], s["w"], s["h"], fill="#ffffff", stroke=s["color"], sw=1.5, rx=6))
        parts.append(rect(s["x"], s["y"], s["w"], 32, fill=s["bg"], stroke=s["color"], sw=1.2, rx=6))
        parts.append(text(s["x"] + s["w"] / 2, s["y"] + 20, f"{s['num']}: {s['title']}", size=11, color=s["color"], bold=True))

        for idx, itm in enumerate(s["items"]):
            parts.append(text(s["x"] + 12, s["y"] + 54 + idx * 24, itm, size=10, color=INK, anchor="start"))

    # Стрілки між кроками
    parts.append(arrow(207, 195, 223, 195, color=COLOR_BUS, sw=2))
    parts.append(arrow(407, 195, 423, 195, color=COLOR_BUS, sw=2))
    parts.append(arrow(612, 195, 628, 195, color=COLOR_BUS, sw=2))

    # Нижній висновок
    parts.append(rect(25, 345, 790, 110, fill="#f8fafc", stroke="#334155", sw=1.5, rx=6))
    parts.append(text(420, 368, "Золоте правило розробника драйверів:", size=12, color=INK, bold=True))
    parts.append(text(45, 395, "1. Ніколи не починайте писати код драйвера без вивчення Errata Sheet для вашої ревізії чипа.", size=10, color=INK, anchor="start"))
    parts.append(text(45, 418, "2. Якщо чип поводиться не за даташитом (пропускає переривання або зависає) — перевірте розділ помилок перед переписуванням коду.", size=10, color=INK, anchor="start"))
    parts.append(text(45, 440, "3. Оформлюйте всі workarounds окремими коментованими функціями з посиланням на номер пункту Errata виробника.", size=10, color=MUTED, anchor="start"))

    render(out("errata-workaround-flow.svg"), W, H, *parts)


def main():
    fig_register_access_types()
    fig_i2c_spi_transaction_anatomy()
    fig_endianness_and_sensor_fusion()
    fig_errata_workaround_flow()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
