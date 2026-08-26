# -*- coding: utf-8 -*-
"""Фігури для статті shcho-trymaty-na-prystroi-a-shcho-na-serveri.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_data_partitioning_architecture():
    """Архітектурний розподіл даних між вузлом та сервером."""
    W, H = 880, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Архітектурний розподіл даних між вбудованим пристроєм та сервером", size=16, color=INK, bold=True))

    # Ліва колонка — Вбудований вузол (On-Device)
    p.append(rect(20, 50, 360, 445, fill="#f0f9ff", stroke="#0284c7", sw=1.8, rx=8))
    p.append(text(200, 78, "Вбудований вузол (Edge Device)", size=14, color="#0369a1", bold=True))
    p.append(text(200, 98, "SRAM: 128 КБ · NOR Flash: 4 МБ · FRAM: 32 КБ", size=11, color=MUTED))

    device_items = [
        ("Поточний операційний стан", "Уставки регулятора, стан FSM, статус реле", "#e0f2fe", "#0284c7"),
        ("Криптографічні матеріали", "Приватний ключ (eFuse), сертифікат CA, PSK", "#e0f2fe", "#0284c7"),
        ("Калібрувальні таблиці", "Зсув АЦП, термокомпенсація, нулі сенсорів", "#e0f2fe", "#0284c7"),
        ("Кільцевий буфер подій (1–7 днів)", "FIFO-буфер телеметрії при зникненні лінка", "#e0f2fe", "#0284c7"),
        ("Логи аварій та Black Box", "HardFault dump, причина перезапуску WDT", "#e0f2fe", "#0284c7"),
    ]

    for i, (title, desc, fcol, scol) in enumerate(device_items):
        y = 118 + i * 72
        p.append(rect(35, y, 330, 62, fill=fcol, stroke=scol, sw=1.2, rx=6))
        p.append(text(200, y + 24, title, size=12, color=scol, bold=True))
        p.append(text(200, y + 46, desc, size=10.5, color=INK))

    # Центральний канал зв'язку
    p.append(rect(400, 150, 80, 240, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(440, 180, "Канал", size=12, color="#b45309", bold=True))
    p.append(text(440, 200, "зв'язку", size=12, color="#b45309", bold=True))
    p.append(text(440, 230, "MQTT /", size=10, color=INK))
    p.append(text(440, 248, "CoAP", size=10, color=INK))
    p.append(text(440, 275, "LTE-M", size=9.5, color=MUTED))
    p.append(text(440, 292, "NB-IoT", size=9.5, color=MUTED))
    p.append(text(440, 310, "LoRa", size=9.5, color=MUTED))
    p.append(text(440, 340, "Дельти", size=9.5, color="#b45309", bold=True))
    p.append(text(440, 358, "і звіти", size=9.5, color="#b45309", bold=True))

    # Стрілки обміну
    p.append(arrow(365, 230, 400, 230, color="#0284c7", sw=1.8))
    p.append(arrow(480, 230, 500, 230, color="#0284c7", sw=1.8))
    p.append(arrow(500, 310, 480, 310, color="#7e22ce", sw=1.8))
    p.append(arrow(400, 310, 365, 310, color="#7e22ce", sw=1.8))

    # Права колонка — Серверна інфраструктура (Cloud Backend)
    p.append(rect(500, 50, 360, 445, fill="#faf5ff", stroke="#7e22ce", sw=1.8, rx=8))
    p.append(text(680, 78, "Серверне сховище (Cloud / Server)", size=14, color="#7e22ce", bold=True))
    p.append(text(680, 98, "Необмежений обсяг · Петабайти · Кластери", size=11, color=MUTED))

    server_items = [
        ("Цифрові двійники (Device Shadows)", "Стан desired/reported, черга дельт", "#f3e8fd", "#7e22ce"),
        ("Бази часових рядів (Time Series)", "ClickHouse / TimescaleDB, роки історії", "#f3e8fd", "#7e22ce"),
        ("Багаторівневе зріджування", "10с дані -> годинні avg/min/max -> роки", "#f3e8fd", "#7e22ce"),
        ("Аналітика парку та ML", "Предиктивне обслуговування, аномалії", "#f3e8fd", "#7e22ce"),
        ("Метадані користувачів та білінг", "PostgreSQL, ієрархія прав, акаунти", "#f3e8fd", "#7e22ce"),
    ]

    for i, (title, desc, fcol, scol) in enumerate(server_items):
        y = 118 + i * 72
        p.append(rect(515, y, 330, 62, fill=fcol, stroke=scol, sw=1.2, rx=6))
        p.append(text(680, y + 24, title, size=12, color=scol, bold=True))
        p.append(text(680, y + 46, desc, size=10.5, color=INK))

    render(os.path.join(OUT, "data-partitioning-architecture.svg"), W, H, *p)


def fig_device_shadow_sync_flow():
    """Синхронізація цифрового двійника: desired проти reported."""
    W, H = 880, 470
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Життєвий цикл узгодження цифрового двійника (Device Shadow)", size=16, color=INK, bold=True))

    # Стовпчики акторів
    actors = [
        ("Користувач / Хмарний API", 140),
        ("Серверний Device Shadow", 440),
        ("Вбудований вузол (MCU)", 740),
    ]

    for title, x in actors:
        p.append(rect(x - 110, 50, 220, 36, fill="#f8fafc", stroke="#475569", sw=1.5, rx=6))
        p.append(text(x, 73, title, size=12, color="#1e293b", bold=True))
        p.append(line(x, 86, x, 430, color="#94a3b8", sw=1.2, dash="4,4"))

    # Послідовність кроків
    steps = [
        (105, 140, 440, "1. Встановлення desired state {temp: 22, v: 42}", "#2563eb", "right"),
        (155, 440, 440, "2. Shadow фіксує delta (desired ≠ reported)", "#7c3aed", "self"),
        (205, 440, 740, "3. Доставка delta повідомлення на вузол", "#059669", "right"),
        (255, 740, 740, "4. Валідація діапазону + NVM Commit (Flash)", "#059669", "self"),
        (305, 740, 740, "5. Застосування до апаратури (Actuator Set)", "#059669", "self"),
        (355, 740, 440, "6. Публікація reported {temp: 22, v: 42}", "#2563eb", "left"),
        (405, 440, 140, "7. Синхронізовано: delta очищено, статус OK", "#16a34a", "left"),
    ]

    for y, x1, x2, msg, col, direction in steps:
        if direction == "right":
            p.append(arrow(x1, y, x2, y, color=col, sw=1.8))
            p.append(rect((x1 + x2) / 2 - 145, y - 20, 290, 18, fill="#ffffff", stroke="none"))
            p.append(text((x1 + x2) / 2, y - 6, msg, size=10.5, color=col, bold=True))
        elif direction == "left":
            p.append(arrow(x1, y, x2, y, color=col, sw=1.8))
            p.append(rect((x1 + x2) / 2 - 145, y - 20, 290, 18, fill="#ffffff", stroke="none"))
            p.append(text((x1 + x2) / 2, y - 6, msg, size=10.5, color=col, bold=True))
        elif direction == "self":
            p.append(line(x1, y - 10, x1 + 40, y - 10, color=col, sw=1.5))
            p.append(line(x1 + 40, y - 10, x1 + 40, y + 10, color=col, sw=1.5))
            p.append(arrow(x1 + 40, y + 10, x1, y + 10, color=col, sw=1.5))
            p.append(rect(x1 - 180, y - 6, 210, 18, fill="#ffffff", stroke="none"))
            p.append(text(x1 - 75, y + 6, msg, size=10.5, color=col, bold=True, anchor="middle"))

    render(os.path.join(OUT, "device-shadow-sync-flow.svg"), W, H, *p)


def fig_storage_hierarchy_tradeoffs():
    """Компроміси характеристик носіїв пам'яті."""
    W, H = 880, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Характеристики та компроміси носіїв інформації в IoT-системах", size=16, color=INK, bold=True))

    headers = [
        ("Тип носія", 120),
        ("Типовий обсяг", 270),
        ("Ресурс перезапису", 420),
        ("Гранулярність / Час", 590),
        ("Енергія / Вартість", 760),
    ]

    # Шапка таблиці
    p.append(rect(30, 45, 820, 32, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=4))
    for title, hx in headers:
        p.append(text(hx, 66, title, size=12, color="#0f172a", bold=True))

    rows = [
        ("SRAM MCU", "16 – 512 КБ", "Необмежений (∞)", "Байт / <5 нс", "0 мДж (волатильна)", "#f8fafc", "#475569"),
        ("FRAM", "8 – 256 КБ", "10¹⁴ циклів", "Байт / ~50 нс", "~1 нДж / $1.50 за чип", "#eff6ff", "#2563eb"),
        ("SPI EEPROM", "1 – 64 КБ", "10⁶ циклів", "Байт / сторінка (3 мс)", "~5 мкДж / $0.20", "#f0fdf4", "#16a34a"),
        ("SPI NOR Flash", "2 – 32 МБ", "10⁵ циклів", "Сектор 4 КБ (30–100 мс)", "~30 мкДж / $0.35", "#fefce8", "#ca8a04"),
        ("Хмарні БД (SQL/TS)", "Петабайти (∞)", "Необмежений (∞)", "Запит / 20–500 мс (RTT)", "$0.02/ГБ/міс + ефір", "#faf5ff", "#7c3aed"),
    ]

    for i, (name, cap, cycles, speed, cost, fcol, scol) in enumerate(rows):
        y = 85 + i * 74
        p.append(rect(30, y, 820, 66, fill=fcol, stroke=scol, sw=1.2, rx=6))
        p.append(text(120, y + 38, name, size=13, color=scol, bold=True))
        p.append(text(270, y + 38, cap, size=11.5, color=INK))
        p.append(text(420, y + 38, cycles, size=11.5, color=INK))
        p.append(text(590, y + 38, speed, size=11.5, color=INK))
        p.append(text(760, y + 38, cost, size=11.5, color=INK))

    render(os.path.join(OUT, "storage-hierarchy-tradeoffs.svg"), W, H, *p)


if __name__ == "__main__":
    fig_data_partitioning_architecture()
    fig_device_shadow_sync_flow()
    fig_storage_hierarchy_tradeoffs()
    print("All figures generated successfully.")
