# -*- coding: utf-8 -*-
"""Генератор архітектурних схем для теми rozbir-rishen (ADR цієї системи)."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_adr_dependency_graph():
    """Фігура 1: Граф залежностей між архітектурними рішеннями (ADR-0001..ADR-0005) та драйверами."""
    w, h = 920, 520
    frags = []

    # Верхній рівень: Архітектурні драйвери (контекст сил)
    frags.append(fitbox(40, 40, 260, 60, "Апаратні ліміти MCU\n(16–64 КБ SRAM, Flash wear)", size=12, bold=True, fill="#fff3e0", stroke="#e67e22"))
    frags.append(fitbox(330, 40, 260, 60, "Ненадійний радіоканал\n(обриви, ліміти MTU, тарифи)", size=12, bold=True, fill="#fff3e0", stroke="#e67e22"))
    frags.append(fitbox(620, 40, 260, 60, "Вимога локальної автономії\n(робота без доступу до хмари)", size=12, bold=True, fill="#fff3e0", stroke="#e67e22"))

    # Центральний рівень: ADR-0001, ADR-0002, ADR-0005
    frags.append(fitbox(40, 160, 260, 85, "ADR-0001: Формат даних\nCBOR + CDDL-схема\n(Zero-heap, компактність)", size=12, bold=True, fill="#e8f8f5", stroke=FIELD, sw=2))
    frags.append(fitbox(330, 160, 260, 85, "ADR-0002: Топологія шлюзу\nРозумний Edge Gateway\n(Локальний брокер + кеш)", size=12, bold=True, fill="#e8f8f5", stroke=FIELD, sw=2))
    frags.append(fitbox(620, 160, 260, 85, "ADR-0005: Синхронізація часу\nRTC + SNTP + дельта-зсув\n(Офлайн-буфер на Flash)", size=12, bold=True, fill="#e8f8f5", stroke=FIELD, sw=2))

    # Нижній рівень: ADR-0004, ADR-0003
    frags.append(fitbox(185, 310, 260, 85, "ADR-0004: Протокол зв'язку\nMQTT Topic Tree + Retain + LWT\n(QoS 1, ідемпотентність)", size=12, bold=True, fill="#eaf2f8", stroke=NEG, sw=2))
    frags.append(fitbox(475, 310, 260, 85, "ADR-0003: Сховище телеметрії\nTimescaleDB (PostgreSQL)\n(Гіпертаблиці + агрегати)", size=12, bold=True, fill="#eaf2f8", stroke=NEG, sw=2))

    # Підсумковий результат: Системні атрибути якості
    frags.append(fitbox(185, 440, 550, 50, "Результат: 100% локальна живучість + стиснення трафіку на 85% + детермінізм пам'яті", size=13, bold=True, fill="#f4f6f8", stroke=LINE))

    # Зв'язки (стрілки від драйверів до ADR)
    frags.append(arrow(170, 100, 170, 160, color=MUTED))
    frags.append(arrow(460, 100, 460, 160, color=MUTED))
    frags.append(arrow(750, 100, 750, 160, color=MUTED))

    # Перехресні зв'язки між ADR
    frags.append(arrow(300, 202, 330, 202, color=LINE, sw=1.6))  # ADR-0001 -> ADR-0002
    frags.append(arrow(590, 202, 620, 202, color=LINE, sw=1.6))  # ADR-0002 -> ADR-0005

    frags.append(arrow(170, 245, 270, 310, color=LINE, sw=1.6))  # ADR-0001 -> ADR-0004
    frags.append(arrow(460, 245, 350, 310, color=LINE, sw=1.6))  # ADR-0002 -> ADR-0004
    frags.append(arrow(460, 245, 560, 310, color=LINE, sw=1.6))  # ADR-0002 -> ADR-0003
    frags.append(arrow(750, 245, 650, 310, color=LINE, sw=1.6))  # ADR-0005 -> ADR-0003

    # Стрілки до підсумку
    frags.append(arrow(315, 395, 410, 440, color=LINE, sw=1.6))
    frags.append(arrow(605, 395, 510, 440, color=LINE, sw=1.6))

    render(os.path.join(OUT_DIR, "adr-dependency-graph.svg"), w, h, *frags)


def fig_tradeoff_matrix():
    """Фігура 2: Порівняння форматів серіалізації за ключовими критеріями."""
    w, h = 880, 420
    frags = []

    # Заголовки таблиці
    col_x = [40, 200, 340, 480, 620, 760]
    headers = ["Формат", "Розмір кадру", "Пам'ять (RAM)", "Flash парсера", "Еволюція схеми", "Інспекція"]
    
    for i, h_text in enumerate(headers):
        frags.append(fitbox(col_x[i], 30, 130, 45, h_text, size=11, bold=True, fill="#2c3e50", stroke="#2c3e50", color="#ffffff"))

    rows = [
        ("JSON (текст)", "142 байти\n(оверхед 700%)", "Висока (купа,\nдинамічний парсер)", "8–14 КБ\n(cJSON/ArduinoJson)", "Гнучка\n(рядкові ключі)", "Відмінна\n(людиночитаний)", "#fdecea"),
        ("Raw C-Struct", "18 байтів\n(мінімум)", "Нульова\n(in-place каст)", "0 КБ\n(без парсера)", "Жорстка (ламає\nвирівнювання/ABI)", "Жодна\n(сирий бінарник)", "#fdecea"),
        ("Protocol Buffers", "32 байти\n(теги varint)", "Низька\n(статична арена)", "5–9 КБ\n(nanopb runtime)", "Сувора\n(кодогенерація)", "Посередня\n(потрібен .proto)", "#fffde7"),
        ("CBOR (обрано)", "22 байти\n(цілочисельні мапи)", "Мінімальна\n(zero-alloc потоковий)", "2.5–4 КБ\n(tinycbor)", "Гнучка\n(CDDL/числові теги)", "Добра\n(hex/cbor-cli)", "#e8f8f5"),
    ]

    y = 85
    for fmt, size_f, ram, fl, evol, insp, bg_col in rows:
        frags.append(fitbox(col_x[0], y, 130, 65, fmt, size=11, bold=True, fill=bg_col, stroke=LINE))
        frags.append(fitbox(col_x[1], y, 130, 65, size_f, size=10, fill=bg_col, stroke=LINE))
        frags.append(fitbox(col_x[2], y, 130, 65, ram, size=10, fill=bg_col, stroke=LINE))
        frags.append(fitbox(col_x[3], y, 130, 65, fl, size=10, fill=bg_col, stroke=LINE))
        frags.append(fitbox(col_x[4], y, 130, 65, evol, size=10, fill=bg_col, stroke=LINE))
        frags.append(fitbox(col_x[5], y, 130, 65, insp, size=10, fill=bg_col, stroke=LINE))
        y += 75

    render(os.path.join(OUT_DIR, "tradeoff-matrix.svg"), w, h, *frags)


def fig_edge_cloud_boundary():
    """Фігура 3: Архітектурні межі та фізичний розподіл рішень між вузлом, шлюзом і бекендом."""
    w, h = 940, 460
    frags = []

    # Секція 1: Вузол (MCU)
    frags.append(fitbox(30, 30, 270, 390, "", fill="#fdfefe", stroke=FIELD, sw=2))
    frags.append(text(165, 55, "Вузол (Cortex-M4 / ESP32)", size=14, bold=True, color=FIELD))
    frags.append(fitbox(50, 75, 230, 55, "Драйвери давачів\n(Апаратний таймер + I2C/SPI)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(50, 140, 230, 65, "Автономна логіка керування\n(Гістерезис, захисні таймери,\nнуль мережевих очікувань)", size=11, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(50, 215, 230, 55, "Буфер у Flash-пам'яті\n(Кільцевий журнал дельт)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(50, 280, 230, 55, "CBOR-кодувальник\n(Zero-alloc, статичний буфер)", size=11, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(50, 345, 230, 55, "Клієнт зв'язку\n(ESP-NOW / BLE / Wi-Fi)", size=11, fill="#f4f6f8", stroke=LINE))

    # Секція 2: Розумний Edge-шлюз
    frags.append(fitbox(335, 30, 270, 390, "", fill="#fdfefe", stroke=NEG, sw=2))
    frags.append(text(470, 55, "Edge-шлюз (Linux SBC)", size=14, bold=True, color=NEG))
    frags.append(fitbox(355, 75, 230, 55, "Мости радіоінтерфейсів\n(BLE-GATT, ESP-NOW -> IP)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(355, 140, 230, 65, "Локальний MQTT-брокер\n(Mosquitto, QoS 1, Retain,\nLWT-моніторинг стану)", size=11, fill="#eaf2f8", stroke=NEG))
    frags.append(fitbox(355, 215, 230, 55, "Локальний буфер SQLite\n(Спулер при падінні WAN)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(355, 280, 230, 55, "Служба валідації та агрегації\n(Перевірка діапазонів, CDDL)", size=11, fill="#eaf2f8", stroke=NEG))
    frags.append(fitbox(355, 345, 230, 55, "Агент синхронізації з хмарою\n(Пакетна вивантаження по TLS)", size=11, fill="#f4f6f8", stroke=LINE))

    # Секція 3: Хмара / Серверна інфраструктура
    frags.append(fitbox(640, 30, 270, 390, "", fill="#fdfefe", stroke="#8e44ad", sw=2))
    frags.append(text(775, 55, "Хмара / Сервер", size=14, bold=True, color="#8e44ad"))
    frags.append(fitbox(660, 75, 230, 55, "Шлюз API / MQTT Ingest\n(Термінація TLS, Auth, ACL)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(660, 140, 230, 65, "TimescaleDB (PostgreSQL)\n(Гіпертаблиці телеметрії,\nреляційний реєстр пристроїв)", size=11, fill="#f5eef8", stroke="#8e44ad"))
    frags.append(fitbox(660, 215, 230, 55, "Фоновий робітник / Агрегатор\n(Політики Retention, компресія)", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(660, 280, 230, 55, "Сервіс команд та OTA\n(Версіонування, rollout)", size=11, fill="#f5eef8", stroke="#8e44ad"))
    frags.append(fitbox(660, 345, 230, 55, "Панель керування (Dashboard)\n(Grafana / Web App)", size=11, fill="#f4f6f8", stroke=LINE))

    # З'єднувальні канали між секціями
    frags.append(arrow(300, 372, 335, 372, color=FIELD, sw=2))
    frags.append(arrow(605, 372, 640, 372, color=NEG, sw=2))

    # Підписи меж
    frags.append(fitbox(275, 428, 70, 26, "LAN / PAN", size=10, bold=True, fill="#fff", stroke=FIELD))
    frags.append(fitbox(580, 428, 70, 26, "WAN / TLS", size=10, bold=True, fill="#fff", stroke=NEG))

    render(os.path.join(OUT_DIR, "edge-cloud-boundary.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_adr_dependency_graph()
    fig_tradeoff_matrix()
    fig_edge_cloud_boundary()
    print("All figures generated successfully.")
