# -*- coding: utf-8 -*-
"""Фігури до теми «Ролі: вузол, шлюз, брокер, служба, сховище, клієнт».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра для рівнів
C_NODE   = "#b8860b"  # польовий вузол (теплий/апаратний)
C_GW     = "#2457d6"  # шлюз (синій / зв'язок)
C_BROKER = "#8e44ad"  # брокер (фіолетовий / маршрутизація)
C_SVC    = "#16a085"  # бекенд-служба (морська хвиля / обробка)
C_DB     = "#d35400"  # сховище (помаранчевий / диски)
C_CLIENT = "#27ae60"  # клієнт (зелений / екран)


# ── 1. Панорамна архітектура 6 рівнів ──────────────────────────────────────────
def fig_iot_system_tiers():
    W, H = 880, 490
    f = [text(W / 2, 26, "Функціональна декомпозиція IoT: 6 ключових ролей від поля до екрана", 15, INK, "middle", bold=True)]

    # 6 колонок-карток
    cols = [
        ("Вузол", "Edge Node", C_NODE, "#fdf8ee", [
            "Cortex-M / 32 КБ RAM",
            "АЦП / GPIO / шини",
            "Батарея (мкА у сні)",
            "Сирий бінарний кадр",
            "LoRa / BLE / UART"
        ]),
        ("Шлюз", "Gateway", C_GW, "#eef3fc", [
            "Linux SoC / RTOS",
            "Міст LoRa→MQTT",
            "Буфер на Flash/RAM",
            "Deadband фільтрація",
            "Wi-Fi / 4G / Ethernet"
        ]),
        ("Брокер", "Message Broker", C_BROKER, "#f7f0fc", [
            "EMQX / Mosquitto",
            "Publish / Subscribe",
            "Розв'язка зв'язності",
            "Черги сесій QoS 1/2",
            "Топіки / LWT / Retain"
        ]),
        ("Служба", "Backend Services", C_SVC, "#eef9f6", [
            "Ingest Worker / API",
            "Валідація схеми",
            "Двигун правил / тривог",
            "Reported vs Desired",
            "Масштабування (K8s)"
        ]),
        ("Сховище", "Storage Tier", C_DB, "#fdf3eb", [
            "Timescale / InfluxDB",
            "Чанкування часу",
            "Стиск Gorilla / Delta",
            "Downsampling / TTL",
            "RDBMS для парку"
        ]),
        ("Клієнт", "Client App", C_CLIENT, "#edf8f1", [
            "Web / Mobile UI",
            "WebSocket / REST",
            "Реалтайм графіки",
            "Надсилання команд",
            "RBAC / Авторизація"
        ]),
    ]

    margin = 20
    bw = 126
    gap = 16
    by = 56
    bh = 270

    for i, (title_ua, title_en, col, fill_col, items) in enumerate(cols):
        bx = margin + i * (bw + gap)
        # Картка рівня
        f.append(rect(bx, by, bw, bh, fill=fill_col, stroke=col, sw=1.8, rx=6))
        # Заголовок
        f.append(text(bx + bw / 2, by + 22, title_ua, 13, col, "middle", bold=True))
        f.append(text(bx + bw / 2, by + 38, title_en, 9.5, MUTED, "middle", italic=True))
        f.append(line(bx + 10, by + 46, bx + bw - 10, by + 46, color=col, sw=1))

        # Пункти
        for j, itm in enumerate(items):
            iy = by + 68 + j * 38
            f.append(circle(bx + 12, iy - 4, 3, fill=col, stroke=col))
            f.append(mtext(bx + 20, iy, itm, size=9.5, color=INK, anchor="start"))

        # Стрілка переходу до наступного
        if i < len(cols) - 1:
            ax = bx + bw
            ay = by + bh / 2
            f.append(line(ax + 2, ay - 14, ax + gap - 4, ay - 14, color=FIELD, sw=2))
            f.append(arrow(ax + gap - 8, ay - 14, ax + gap - 1, ay - 14, color=FIELD, sw=2))
            f.append(line(ax + gap - 2, ay + 14, ax + 4, ay + 14, color=POS, sw=2))
            f.append(arrow(ax + 8, ay + 14, ax + 1, ay + 14, color=POS, sw=2))

    # Нижній пояс: потоки телеметрії та керування
    f.append(rect(margin, 344, W - 2 * margin, 58, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=6))
    f.append(line(margin + 20, 362, W - margin - 20, 362, color=FIELD, sw=2.5))
    f.append(arrow(W - margin - 26, 362, W - margin - 16, 362, color=FIELD, sw=2.5))
    f.append(text(W / 2, 357, "ПОТІК ТЕЛЕМЕТРІЇ (Upstream): збір вимірів → бінарний кадр → переклад в JSON → брокер → TSDB → екран", 10.5, FIELD, "middle", bold=True))

    f.append(line(W - margin - 20, 386, margin + 20, 386, color=POS, sw=2.5))
    f.append(arrow(margin + 26, 386, margin + 16, 386, color=POS, sw=2.5))
    f.append(text(W / 2, 393, "ПОТІК КОМАНД (Downstream): дія в UI → REST/RPC → топік брокера → шлюз → радіоканал → виконання на ніжці МК", 10.5, POS, "middle", bold=True))

    # Блок висновку
    f.append(fitbox(margin, 414, W - 2 * margin, 58,
                    "Жоден рівень не робить чужої роботи: Вузол не знає про TCP і бази даних; Шлюз рятує від розривів мережі;\n"
                    "Брокер усуває зв'язність «усі з усіма»; Служба рахує бізнес-правила; Сховище стискає терабайти; Клієнт показує зріз.",
                    size=10.5, fill="#ffffff", stroke="#ccd5e0", color=INK))

    render(os.path.join(IMG, "iot-system-tiers.svg"), W, H, *f)


# ── 2. Розв'язка через Publish/Subscribe ──────────────────────────────────────
def fig_pubsub_decoupling():
    W, H = 780, 420
    f = [text(W / 2, 26, "Три виміри розв'язки (Decoupling) у патерні Publish / Subscribe", 15, INK, "middle", bold=True)]

    # 3 картки для 3 вимірів
    panels = [
        ("1. Просторова (Spatial)", C_GW, [
            "Видавець НЕ знає адреси",
            "й кількості підписників.",
            "",
            "Шлюз публікує в топік:",
            "  telemetry/site1/temp",
            "Хто слухає — визначає",
            "лише конфігурація брокера."
        ]),
        ("2. Часова (Temporal)", C_BROKER, [
            "Відправник і отримувач",
            "НЕ мусять бути онлайн разом.",
            "",
            "Служба бекенду на рестарті;",
            "Брокер тримає чергу сесії.",
            "Служба піднялася — отримала",
            "всі накопичені пакети (QoS 1)."
        ]),
        ("3. Синхронізаційна", C_SVC, [
            "Відправка НЕ блокує процес",
            "довгим очікуванням диска.",
            "",
            "Шлюз віддав пакет брокеру",
            "й миттєво вільний опитувати",
            "наступний польовий датчик,",
            "поки база пише на SSD."
        ]),
    ]

    pw = 230
    ph = 190
    py = 52
    for k, (phead, pcol, plines) in enumerate(panels):
        px = 30 + k * (pw + 25)
        f.append(rect(px, py, pw, ph, fill="#fbfcfd", stroke=pcol, sw=1.6, rx=6))
        f.append(text(px + pw / 2, py + 22, phead, 12, pcol, "middle", bold=True))
        f.append(line(px + 10, py + 32, px + pw - 10, py + 32, color=pcol, sw=1))
        for li, line_txt in enumerate(plines):
            if not line_txt:
                continue
            is_code = line_txt.startswith("  ")
            c_size = 9.2 if is_code else 10
            c_font_col = C_GW if is_code else INK
            f.append(text(px + 14, py + 52 + li * 19, line_txt, c_size, c_font_col, "start", bold=is_code))

    # Нижня частина: схема потоку від N видавців через брокер до M підписників
    sy = 260
    f.append(rect(30, sy, 720, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))

    # Видавці ліворуч
    f.append(rect(50, sy + 20, 130, 42, fill="#eef3fc", stroke=C_GW, sw=1.5))
    f.append(text(115, sy + 38, "Шлюз A (LoRa)", 11, INK, "middle", bold=True))
    f.append(text(115, sy + 52, "pub: site1/sensor", 9, MUTED, "middle"))

    f.append(rect(50, sy + 76, 130, 42, fill="#eef3fc", stroke=C_GW, sw=1.5))
    f.append(text(115, sy + 94, "Шлюз B (BLE)", 11, INK, "middle", bold=True))
    f.append(text(115, sy + 108, "pub: site2/sensor", 9, MUTED, "middle"))

    # Брокер у центрі
    f.append(rect(290, sy + 18, 180, 102, fill="#f7f0fc", stroke=C_BROKER, sw=2.2))
    f.append(text(380, sy + 44, "MQTT БРОКЕР", 13, C_BROKER, "middle", bold=True))
    f.append(text(380, sy + 64, "Дерево тем (Topics)", 10, INK, "middle"))
    f.append(text(380, sy + 82, "Черги клієнтів QoS 1", 9.5, MUTED, "middle"))
    f.append(text(380, sy + 100, "Маршрутизація пакета", 9.5, MUTED, "middle"))

    # Стрілки вхід
    f.append(line(180, sy + 41, 286, sy + 55, color=C_GW, sw=1.8))
    f.append(arrow(276, sy + 54, 288, sy + 56, color=C_GW, sw=1.8))

    f.append(line(180, sy + 97, 286, sy + 80, color=C_GW, sw=1.8))
    f.append(arrow(276, sy + 82, 288, sy + 79, color=C_GW, sw=1.8))

    # Підписники праворуч
    f.append(rect(580, sy + 12, 150, 34, fill="#eef9f6", stroke=C_SVC, sw=1.5))
    f.append(text(655, sy + 30, "Служба запису в TSDB", 10.5, INK, "middle", bold=True))

    f.append(rect(580, sy + 54, 150, 34, fill="#eef9f6", stroke=C_SVC, sw=1.5))
    f.append(text(655, sy + 72, "Служба тривог (Alerts)", 10.5, INK, "middle", bold=True))

    f.append(rect(580, sy + 96, 150, 34, fill="#edf8f1", stroke=C_CLIENT, sw=1.5))
    f.append(text(655, sy + 114, "Web Live Dashboard", 10.5, INK, "middle", bold=True))

    # Стрілки вихід
    f.append(line(470, sy + 50, 576, sy + 29, color=C_BROKER, sw=1.8))
    f.append(arrow(566, sy + 31, 578, sy + 28, color=C_BROKER, sw=1.8))

    f.append(line(470, sy + 70, 576, sy + 71, color=C_BROKER, sw=1.8))
    f.append(arrow(566, sy + 71, 578, sy + 71, color=C_BROKER, sw=1.8))

    f.append(line(470, sy + 88, 576, sy + 112, color=C_BROKER, sw=1.8))
    f.append(arrow(566, sy + 110, 578, sy + 113, color=C_BROKER, sw=1.8))

    render(os.path.join(IMG, "pubsub-decoupling.svg"), W, H, *f)


# ── 3. Наскрізні потоки телеметрії та команд ─────────────────────────────────
def fig_telemetry_and_command_flow():
    W, H = 820, 460
    f = [text(W / 2, 26, "Наскрізні потоки: телеметрія вгору та замкнений цикл команд (ACK Loop)", 15, INK, "middle", bold=True)]

    # 4 вертикальні доріжки компонентів
    lanes = [
        ("Вузол (MCU)", 90, C_NODE),
        ("Шлюз (Gateway)", 300, C_GW),
        ("Брокер / Бекенд", 520, C_BROKER),
        ("Клієнт / Дашборд", 730, C_CLIENT),
    ]

    for name, lx, lcol in lanes:
        f.append(rect(lx - 65, 48, 130, 32, fill="#f8fafc", stroke=lcol, sw=1.8, rx=5))
        f.append(text(lx, 68, name, 11.5, lcol, "middle", bold=True))
        f.append(line(lx, 80, lx, 440, color="#cbd5e1", sw=1.4, dash="4 4"))

    # Потік 1: Телеметрія (зверху)
    f.append(text(30, 104, "А. Телеметрія", 11, FIELD, "start", bold=True))

    # Вузол заміряв АЦП
    f.append(rect(35, 114, 110, 26, fill="#fdf8ee", stroke=C_NODE, sw=1.2, rx=4))
    f.append(text(90, 130, "1. Зчитав датчик", 9.5, INK, "middle"))

    # Вузол -> Шлюз (Радіокадр)
    f.append(line(90, 150, 296, 150, color=FIELD, sw=2))
    f.append(arrow(288, 150, 298, 150, color=FIELD, sw=2))
    f.append(text(195, 143, "Кадр LoRa (12 байтів + CRC)", 9.5, FIELD, "middle", bold=True))

    # Шлюз: валідація, таймстемп, пакування JSON
    f.append(rect(245, 160, 110, 32, fill="#eef3fc", stroke=C_GW, sw=1.2, rx=4))
    f.append(text(300, 175, "2. Перевірка CRC", 9, INK, "middle"))
    f.append(text(300, 187, "і збагачення NTP", 9, INK, "middle"))

    # Шлюз -> Брокер (MQTT Publish)
    f.append(line(300, 202, 516, 202, color=FIELD, sw=2))
    f.append(arrow(508, 202, 518, 202, color=FIELD, sw=2))
    f.append(text(410, 195, "MQTT PUB: telemetry/... (JSON)", 9.5, FIELD, "middle", bold=True))

    # Бекенд пише в TSDB і шле клієнту
    f.append(line(520, 218, 726, 218, color=FIELD, sw=2))
    f.append(arrow(718, 218, 728, 218, color=FIELD, sw=2))
    f.append(text(625, 211, "WebSocket push у UI", 9.5, FIELD, "middle", bold=True))

    f.append(rect(675, 226, 110, 26, fill="#edf8f1", stroke=C_CLIENT, sw=1.2, rx=4))
    f.append(text(730, 242, "3. Оновлення графіка", 9.5, INK, "middle"))

    # Розділювач
    f.append(line(20, 262, W - 20, 262, color="#e2e8f0", sw=1.5))

    # Потік 2: Команда та підтвердження (знизу)
    f.append(text(30, 280, "Б. Команда керування та зворотне підтвердження (ACK)", 11, POS, "start", bold=True))

    # Клієнт тисне кнопку
    f.append(rect(675, 290, 110, 26, fill="#edf8f1", stroke=C_CLIENT, sw=1.2, rx=4))
    f.append(text(730, 306, "1. Клік «Увімкнути»", 9.5, INK, "middle"))

    # Клієнт -> Брокер
    f.append(line(730, 326, 524, 326, color=POS, sw=2))
    f.append(arrow(532, 326, 522, 326, color=POS, sw=2))
    f.append(text(625, 319, "POST /api/v1/relay (cmd)", 9.5, POS, "middle", bold=True))

    # Брокер -> Шлюз
    f.append(line(520, 344, 304, 344, color=POS, sw=2))
    f.append(arrow(312, 344, 302, 344, color=POS, sw=2))
    f.append(text(410, 337, "MQTT SUB: cmd/node42/set", 9.5, POS, "middle", bold=True))

    # Шлюз -> Вузол (Downlink)
    f.append(line(300, 362, 94, 362, color=POS, sw=2))
    f.append(arrow(102, 362, 92, 362, color=POS, sw=2))
    f.append(text(195, 355, "Пакет команди (Opcode 0x05)", 9.5, POS, "middle", bold=True))

    # Вузол увімкнув реле і шле ACK назад
    f.append(rect(35, 372, 110, 26, fill="#fdf8ee", stroke=C_NODE, sw=1.2, rx=4))
    f.append(text(90, 388, "2. Перемкнув пін GPIO", 9.5, INK, "middle"))

    # Вузол -> Шлюз (ACK)
    f.append(line(90, 408, 296, 408, color="#2563eb", sw=1.8, dash="3 3"))
    f.append(arrow(288, 408, 298, 408, color="#2563eb", sw=1.8))
    f.append(text(195, 402, "Звіт статусу (ACK: ON)", 9, "#2563eb", "middle"))

    # Шлюз -> Брокер -> Клієнт (ACK)
    f.append(line(300, 420, 726, 420, color="#2563eb", sw=1.8, dash="3 3"))
    f.append(arrow(718, 420, 728, 420, color="#2563eb", sw=1.8))
    f.append(text(510, 414, "state/node42/relay = ON  →  Клієнт бачить підтверджений зелений стан", 9.5, "#2563eb", "middle", bold=True))

    render(os.path.join(IMG, "telemetry-and-command-flow.svg"), W, H, *f)


# ── 4. Сховище часових рядів: чанкування і компресія ────────────────────────
def fig_time_series_storage_chunking():
    W, H = 780, 380
    f = [text(W / 2, 26, "Організація Time-Series DB: партиціювання на чанки та стиснення метрик", 15, INK, "middle", bold=True)]

    # Вхідний потік записів ліворуч
    f.append(rect(30, 60, 150, 190, fill="#f8fafc", stroke=C_SVC, sw=1.6, rx=6))
    f.append(text(105, 84, "Потік вимірів", 12, C_SVC, "middle", bold=True))
    f.append(text(105, 100, "(Append-Only)", 9.5, MUTED, "middle", italic=True))
    f.append(line(45, 108, 165, 108, color=C_SVC, sw=1))

    sample_rows = [
        "10:00:01  t=22.4  v=3.31",
        "10:00:02  t=22.4  v=3.30",
        "10:00:03  t=22.5  v=3.30",
        "10:00:04  t=22.5  v=3.29",
        "..."
    ]
    for idx, rtxt in enumerate(sample_rows):
        f.append(text(42, 130 + idx * 22, rtxt, 9, INK, "start"))

    f.append(line(180, 155, 226, 155, color=C_SVC, sw=2))
    f.append(arrow(218, 155, 228, 155, color=C_SVC, sw=2))

    # Схема чанків (Сьогодні, Вчора, Тиждень тому)
    f.append(rect(230, 52, 520, 210, fill="#fdfbf9", stroke=C_DB, sw=1.8, rx=6))
    f.append(text(490, 74, "Гіпертаблиця (TimescaleDB / InfluxDB): Партиції за часом", 12.5, C_DB, "middle", bold=True))

    # Чанк 1: Сьогодні (активний, у RAM/WAL)
    f.append(rect(250, 92, 145, 150, fill="#ffffff", stroke=POS, sw=1.8, rx=5))
    f.append(text(322, 114, "Сьогодні (День 0)", 11, POS, "middle", bold=True))
    f.append(text(322, 130, "АКТИВНИЙ ЧАНК", 9, MUTED, "middle"))
    f.append(line(260, 138, 385, 138, color=POS, sw=1))
    f.append(text(260, 158, "• Пишеться в RAM", 9.5, INK, "start"))
    f.append(text(260, 176, "• WAL на диску", 9.5, INK, "start"))
    f.append(text(260, 194, "• Сирі дані (100%)", 9.5, INK, "start"))
    f.append(text(260, 212, "• Швидкий Insert", 9.5, INK, "start"))
    f.append(text(260, 230, "• Без компресії", 9.5, MUTED, "start"))

    # Чанк 2: Вчора (закритий, стиснений)
    f.append(rect(415, 92, 145, 150, fill="#fdf3eb", stroke=C_DB, sw=1.5, rx=5))
    f.append(text(487, 114, "Вчора (День −1)", 11, C_DB, "middle", bold=True))
    f.append(text(487, 130, "СТИСНЕНИЙ ЧАНК", 9, MUTED, "middle"))
    f.append(line(425, 138, 550, 138, color=C_DB, sw=1))
    f.append(text(425, 158, "• Read-Only сегмент", 9.5, INK, "start"))
    f.append(text(425, 176, "• Gorilla / Delta-of-Δ", 9.5, INK, "start"))
    f.append(text(425, 194, "• Обсяг: 8–10% від сирого", 9.5, C_DB, "start", bold=True))
    f.append(text(425, 212, "• Колоночний формат", 9.5, INK, "start"))
    f.append(text(425, 230, "• Швидкі агрегати", 9.5, INK, "start"))

    # Чанк 3: Минулий місяць (зріджений, даунсемплінг)
    f.append(rect(580, 92, 150, 150, fill="#f0f4f8", stroke="#475569", sw=1.5, rx=5))
    f.append(text(655, 114, "Місяць тому (День −30)", 10.5, "#475569", "middle", bold=True))
    f.append(text(655, 130, "ДАУНСЕМПЛІНГ", 9, MUTED, "middle"))
    f.append(line(590, 138, 720, 138, color="#475569", sw=1))
    f.append(text(590, 158, "• 1-хв середні/мін/макс", 9.5, INK, "start"))
    f.append(text(590, 176, "• Сирі секунди вилучені", 9.5, INK, "start"))
    f.append(text(590, 194, "• Довготривалий архів", 9.5, INK, "start"))
    f.append(text(590, 212, "• Збереження 2 роки", 9.5, INK, "start"))
    f.append(text(590, 230, "• Економія диска 98%", 9.5, FIELD, "start", bold=True))

    # Нижній блок: порівняння з класичною RDBMS
    f.append(fitbox(30, 276, 720, 84,
                    "Чому не класичний PostgreSQL B-Tree для всього потоку? При мільйонах рядків B-дерево перестає вміщатися в RAM,\n"
                    "кожен INSERT спричиняє довільне читання/запис блоків на диск (Write Amplification) і блокування індексу.\n"
                    "Time-Series DB ділить час на чанки: запис іде послідовно лише в Активний чанк, а старі чанки пакуються в колумнарний архів.",
                    size=10.5, fill="#ffffff", stroke="#cbd5e1", color=INK))

    render(os.path.join(IMG, "time-series-storage-chunking.svg"), W, H, *f)


if __name__ == "__main__":
    fig_iot_system_tiers()
    fig_pubsub_decoupling()
    fig_telemetry_and_command_flow()
    fig_time_series_storage_chunking()
    print("OK: all figures rendered into", IMG)
