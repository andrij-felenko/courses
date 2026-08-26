#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми shcho-take-zviazana-systema-i-chym-vona
(Що таке зв'язана система і чим вона відрізняється від пристрою).
"""

import sys
import os

# 4 рівні вгору від root/course/embedded/shcho-take-zviazana-systema-i-chym-vona до repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def make_standalone_vs_connected():
    """Фігура 1: Порівняння автономного пристрою та зв'язаної системи."""
    w, h = 880, 480
    frags = []

    # Заголовок зверху
    frags.append(text(440, 28, "Порівняння архітектурних парадигм: пристрій проти системи", size=16, bold=True))

    # Ліва колонка: Автономний пристрій (Standalone Embedded Node)
    frags.append(rect(30, 55, 390, 395, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(30, 55, 390, 38, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 80, "АВТОНОМНИЙ ПРИСТРІЙ (STANDALONE)", size=13, bold=True, color="#1e293b"))

    # Блоки всередині автономного
    b1 = fitbox(50, 110, 350, 50, "Фізичний об'єкт (Сенсори та Актуатори)\nТермопара, мотор, клапан, реле", size=12, fill="#ffffff", stroke="#94a3b8")
    b2 = fitbox(50, 195, 350, 60, "Мікроконтролер (MCU / RTOS)\nЖорсткий реальний час, PID-регулятор, таймери\nЛокальний стан у SRAM / Flash", size=12, fill="#ffffff", stroke="#2563eb", bold=False)
    b3 = fitbox(50, 290, 350, 45, "Локальний інтерфейс користувача\nКнопки, енкодер, світлодіоди, LCD-екран", size=12, fill="#ffffff", stroke="#94a3b8")

    frags.extend([b1, b2, b3])

    # Стрілки локального циклу
    frags.append(arrow(150, 160, 150, 195, color="#2563eb", sw=2))
    frags.append(text(120, 180, "АЦП (мкс)", size=10, color="#2563eb", anchor="end"))
    frags.append(arrow(300, 195, 300, 160, color="#dc2626", sw=2))
    frags.append(text(330, 180, "ШІМ / ЦАП", size=10, color="#dc2626", anchor="start"))

    frags.append(arrow(225, 290, 225, 255, color="#475569", sw=1.5))
    frags.append(text(235, 275, "Ввід", size=10, color="#475569", anchor="start"))

    # Підсумок характеристик автономного
    frags.append(rect(50, 355, 350, 80, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(60, 375, "• Детермінована затримка: < 10–100 мкс", size=11, color="#334155", anchor="start"))
    frags.append(text(60, 395, "• 100% стану зосереджено в одному чипі", size=11, color="#334155", anchor="start"))
    frags.append(text(60, 415, "• Відмова: або працює все, або вимкнено (All-or-Nothing)", size=11, color="#334155", anchor="start"))

    # Права колонка: Зв'язана система (Connected IoT Ecosystem)
    frags.append(rect(460, 55, 390, 395, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(rect(460, 55, 390, 38, fill="#dcfce7", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(655, 80, "ЗВ'ЯЗАНА СИСТЕМА (CONNECTED IOT)", size=13, bold=True, color="#14532d"))

    # Блоки зв'язаної системи
    c1 = fitbox(480, 105, 350, 48, "Кінцевий вузол (Edge MCU)\nЛокальний захист + буфер офлайну + агент стану", size=11, fill="#ffffff", stroke="#16a34a")
    c2 = fitbox(480, 185, 350, 45, "Ненадійний мережевий транспорт\nWi-Fi / BLE / Cellular / LoRaWAN (втрати, затримки)", size=11, fill="#fffbeb", stroke="#d97706")
    c3 = fitbox(480, 260, 350, 48, "Хмарний бекенд і цифровий двійник\nDevice Shadow (Desired/Reported), брокер MQTT, БД", size=11, fill="#ffffff", stroke="#0284c7")
    c4 = fitbox(480, 335, 350, 40, "Зовнішні клієнти (Web / Mobile App / API)\nАсинхронний моніторинг і надсилання уставок", size=11, fill="#ffffff", stroke="#64748b")

    frags.extend([c1, c2, c3, c4])

    # Зв'язки
    frags.append(arrow(655, 153, 655, 185, color="#d97706", sw=1.8))
    frags.append(arrow(655, 185, 655, 153, color="#d97706", sw=1.8))
    frags.append(arrow(655, 230, 655, 260, color="#0284c7", sw=1.8))
    frags.append(arrow(655, 260, 655, 230, color="#0284c7", sw=1.8))
    frags.append(arrow(655, 308, 655, 335, color="#64748b", sw=1.8))
    frags.append(arrow(655, 335, 655, 308, color="#64748b", sw=1.8))

    # Підсумок характеристик зв'язаної
    frags.append(rect(480, 388, 350, 50, fill="#f0fdf4", stroke="#86efac", sw=1, rx=4))
    frags.append(text(490, 406, "• Розподілений стан і несинхронні годинники", size=11, color="#166534", anchor="start"))
    frags.append(text(490, 424, "• Часткові відмови — штатний режим (CAP / Eventual Consistency)", size=11, color="#166534", anchor="start"))

    render(os.path.join(IMG_DIR, "standalone-vs-connected.svg"), w, h, *frags)


def make_device_shadow_delta():
    """Фігура 2: Патерн Device Shadow: Desired, Reported і узгодження дельти."""
    w, h = 880, 440
    frags = []

    frags.append(text(440, 26, "Синхронізація стану через цифровий двійник (Device Shadow)", size=16, bold=True))

    # Ліва частина: Мобільний клієнт / Користувач
    frags.append(rect(30, 60, 200, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(130, 85, "КЛІЄНТ / APP", size=13, bold=True, color="#1e293b"))
    f_app1 = fitbox(45, 110, 170, 70, "1. Користувач змінює уставку:\nTarget = 24.5 °C\n(Вузол може бути офлайн)", size=11, fill="#ffffff", stroke="#3b82f6")
    f_app2 = fitbox(45, 290, 170, 85, "4. Відображення:\nЦіль: 24.5 °C (Desired)\nФакт: 21.0 → 24.5 °C\n(Синхронізовано)", size=11, fill="#ffffff", stroke="#10b981")
    frags.extend([f_app1, f_app2])

    # Центральна частина: Хмарний сервіс тіні (Cloud Shadow Service)
    frags.append(rect(260, 60, 360, 340, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(440, 85, "ХМАРНА ТІНЬ (DEVICE SHADOW)", size=13, bold=True, color="#0369a1"))

    # Документ тіні
    sh_box = rect(280, 105, 320, 195, fill="#ffffff", stroke="#38bdf8", sw=1.5, rx=6)
    frags.append(sh_box)
    frags.append(text(295, 128, "JSON Document (Версія v=42):", size=11, bold=True, color="#0369a1", anchor="start"))
    frags.append(text(295, 150, "state: {", size=11, color="#334155", anchor="start"))
    frags.append(text(310, 170, "desired:  { target_temp: 24.5 },", size=11, bold=True, color="#2563eb", anchor="start"))
    frags.append(text(310, 190, "reported: { target_temp: 21.0, cur: 21.0 }", size=11, color="#475569", anchor="start"))
    frags.append(text(295, 210, "},", size=11, color="#334155", anchor="start"))
    frags.append(text(295, 230, "metadata: { v: 42, timestamp: 1714567890 }", size=11, color="#64748b", anchor="start"))

    delta_box = fitbox(280, 315, 320, 65, "Обчислення дельти (Reconciliation):\nDelta = Desired \\ Reported\n=> { target_temp: 24.5 }", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(delta_box)

    # Права частина: Фізичний вузол (Edge Device)
    frags.append(rect(650, 60, 200, 340, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(750, 85, "EDGE MCU ВУЗОЛ", size=13, bold=True, color="#15803d"))
    f_dev1 = fitbox(665, 150, 170, 85, "2. Отримання дельти:\nПідписка на топік /delta\nПрийом уставки v=42\nЗапис у PID-регулятор", size=11, fill="#ffffff", stroke="#d97706")
    f_dev2 = fitbox(665, 270, 170, 85, "3. Звіт виконання:\nПублікація в /update:\nreported: { target: 24.5 }\nПідтвердження v=42", size=11, fill="#ffffff", stroke="#16a34a")
    frags.extend([f_dev1, f_dev2])

    # Стрілки між компонентами
    # App -> Cloud
    frags.append(arrow(215, 145, 280, 145, color="#2563eb", sw=2))
    frags.append(text(247, 137, "POST desired", size=9, color="#2563eb"))

    # Cloud -> Device (Delta)
    frags.append(arrow(600, 345, 665, 192, color="#d97706", sw=2))
    frags.append(text(632, 280, "MQTT Delta", size=9, color="#d97706"))

    # Device -> Cloud (Reported)
    frags.append(arrow(665, 312, 600, 250, color="#16a34a", sw=2))
    frags.append(text(635, 240, "MQTT update", size=9, color="#16a34a"))

    # Cloud -> App
    frags.append(arrow(280, 260, 215, 332, color="#10b981", sw=2))
    frags.append(text(247, 310, "SSE / Push", size=9, color="#10b981"))

    render(os.path.join(IMG_DIR, "device-shadow-delta.svg"), w, h, *frags)


def make_edge_cloud_split():
    """Фігура 3: Розподіл обчислень між Edge та Cloud."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 26, "Розподіл обчислень: спектр від фізичного краю до хмари", size=16, bold=True))

    # 4 рівні ієрархії
    levels = [
        ("ФІЗИЧНИЙ ДАТЧИК", "Сенсорний елемент\n(АЦП, тензорезистор, мікрофон)", "Сирі аналогові вибірки\n10–50 кГц (високий потік)", "#f8fafc", "#94a3b8", 40),
        ("КРАЙОВИЙ ВУЗОЛ (EDGE MCU)", "Cortex-M4 / ESP32 (SRAM 320 KB)\nФільтрація, БПФ, TinyML, PID", "Очищені фічі, RMS, детекція аварій\nРеакція: 0.1–10 мс", "#f0fdf4", "#16a34a", 240),
        ("ПОЛЬОВИЙ ШЛЮЗ (GATEWAY)", "Embedded Linux / Raspberry Pi\nАгрегація, протокольний міст, TLS", "Пакетні звіти, стиснення zstd\nБуфер офлайну на 7 діб", "#f0f9ff", "#0284c7", 440),
        ("ХМАРНИЙ ЦЕНТР (CLOUD)", "Кластери серверів, Time-Series DB\nFleet Management, Big Data ML", "Глобальна аналітика, оновлення OTA\nРеакція: 0.5–5 с", "#faf5ff", "#9333ea", 640),
    ]

    for title, desc, perf, bg_col, br_col, x_pos in levels:
        frags.append(rect(x_pos, 65, 195, 230, fill=bg_col, stroke=br_col, sw=1.5, rx=6))
        frags.append(rect(x_pos, 65, 195, 30, fill=bg_col, stroke=br_col, sw=1.5, rx=6))
        frags.append(text(x_pos + 97, 85, title, size=10, bold=True, color="#1e293b"))
        frags.append(mtext(x_pos + 97, 125, desc, size=10, color="#334155", lh=1.35))
        frags.append(line(x_pos + 15, 175, x_pos + 180, 175, color=br_col, sw=1, dash="3,3"))
        frags.append(mtext(x_pos + 97, 205, perf, size=10, color="#475569", lh=1.35, bold=True))

    # Стрілки між рівнями
    frags.append(arrow(235, 150, 240, 150, color="#16a34a", sw=2))
    frags.append(arrow(435, 150, 440, 150, color="#0284c7", sw=2))
    frags.append(arrow(635, 150, 640, 150, color="#9333ea", sw=2))

    # Градієнтні осі внизу
    frags.append(rect(40, 315, 800, 90, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))

    # Вісь об'єму даних
    frags.append(text(55, 345, "Об'єм даних:", size=11, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(145, 345, "1.7 ГБ / доба (сирі вибірки 10 кГц)", size=11, color="#b91c1c", anchor="start"))
    frags.append(arrow(385, 341, 480, 341, color="#b91c1c", sw=1.5))
    frags.append(text(500, 345, "34 КБ / доба (агреговані метрики)", size=11, color="#15803d", anchor="start"))

    # Вісь затримки реакції
    frags.append(text(55, 380, "Критичність затримки:", size=11, bold=True, color="#2563eb", anchor="start"))
    frags.append(text(205, 380, "< 10 мкс (захист по струму)", size=11, color="#2563eb", anchor="start"))
    frags.append(arrow(385, 376, 480, 376, color="#2563eb", sw=1.5))
    frags.append(text(500, 380, "Секунди / доби (стратегічний моніторинг)", size=11, color="#6b21a8", anchor="start"))

    render(os.path.join(IMG_DIR, "edge-cloud-split.svg"), w, h, *frags)


if __name__ == "__main__":
    make_standalone_vs_connected()
    make_device_shadow_delta()
    make_edge_cloud_split()
    print("Згенеровано 3 фігури у", IMG_DIR)
