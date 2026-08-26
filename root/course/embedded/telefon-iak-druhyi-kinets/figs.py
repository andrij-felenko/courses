# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Телефон як другий кінець»."""

import sys
import os

# Імпорт спільних утиліт svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)


def fig_gatt_hierarchy(path):
    """Фігура 1: Ієрархія GATT — Профіль, Сервіси, Характеристики, Дескриптори."""
    w, h = 880, 520
    frags = []

    # Загальний фон
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # 1. Profile Box (Контейнер профілю)
    frags.append(rect(20, 20, 840, 480, fill="#f8fafc", stroke="#64748b", sw=2, rx=10))
    frags.append(text(440, 48, "GATT Профіль: Телеметрія та керування пристроєм", size=16, bold=True, color="#0f172a"))
    frags.append(text(440, 68, "Логічне об'єднання служб, характеристик і дескрипторів у таблиці атрибутів ATT", size=12, color=MUTED))

    # 2. Service 1: Custom Telemetry Service (128-bit UUID)
    frags.append(rect(40, 95, 490, 385, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=8))
    frags.append(text(285, 122, "Служба телеметрії (Vendor Service: 128-bit UUID)", size=14, bold=True, color="#1e40af"))
    frags.append(text(285, 140, "UUID: 00000001-f1e2-4d3c-b5a6-9876543210ab  |  Handle: 0x0010", size=11, color="#1e3a8a"))

    # Characteristic 1.1: Telemetry Data
    frags.append(rect(55, 158, 460, 175, fill="#ffffff", stroke="#93c5fd", sw=1.4, rx=6))
    frags.append(text(285, 180, "Характеристика 1: Дані давачів (Telemetry Value)", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(285, 198, "UUID: 00000002-... | Handle: 0x0012 | Властивості: Read, Notify", size=11, color=MUTED))

    # Value & Descriptors inside Char 1.1
    frags.append(rect(70, 212, 430, 42, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(285, 230, "Значення (Value Attribute): [Температура (2B), Напруга (2B), Лічильник (4B)]", size=11, bold=True, color="#1e40af"))
    frags.append(text(285, 246, "Handle: 0x0013  |  Permissions: Read Only  |  Розмір: 8 байтів", size=10, color=MUTED))

    frags.append(rect(70, 262, 430, 60, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(285, 282, "Дескриптор конфігурації клієнта (CCCD, UUID: 0x2902)", size=11, bold=True, color="#b45309"))
    frags.append(text(285, 298, "Handle: 0x0014 | Біт 0 (0x0001): Notify | Біт 1 (0x0002): Indicate", size=10, color="#92400e"))
    frags.append(text(285, 314, "Стан підписки: 0x0000 (Вимкнено) або 0x0001 (Телефон підписався)", size=10, italic=True, color="#b45309"))

    # Characteristic 1.2: Control Command
    frags.append(rect(55, 345, 460, 120, fill="#ffffff", stroke="#93c5fd", sw=1.4, rx=6))
    frags.append(text(285, 368, "Характеристика 2: Команди (Control Command)", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(285, 386, "UUID: 00000003-... | Handle: 0x0016 | Властивості: Write, Write Without Response", size=11, color=MUTED))

    frags.append(rect(70, 400, 430, 52, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(285, 420, "Значення (Command Payload): [Код команди (1B), Параметр (4B)]", size=11, bold=True, color="#334155"))
    frags.append(text(285, 438, "Handle: 0x0017  |  Permissions: Write With Authentication  |  Розмір: 1..64B", size=10, color=MUTED))

    # 3. Service 2: Standard Battery Service (16-bit UUID)
    frags.append(rect(550, 95, 310, 385, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    frags.append(text(705, 122, "Служба батареї (SIG Standard)", size=14, bold=True, color="#15803d"))
    frags.append(text(705, 140, "UUID: 0x180F  |  Handle: 0x0020", size=11, color="#166534"))

    # Characteristic 2.1: Battery Level
    frags.append(rect(565, 158, 280, 200, fill="#ffffff", stroke="#86efac", sw=1.4, rx=6))
    frags.append(text(705, 180, "Характеристика: Рівень батареї", size=12, bold=True, color="#166534"))
    frags.append(text(705, 198, "UUID: 0x2A19 | Read, Notify", size=11, color=MUTED))

    frags.append(rect(575, 212, 260, 42, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    frags.append(text(705, 230, "Значення: Рівень у % (0..100)", size=11, bold=True, color="#14532d"))
    frags.append(text(705, 246, "Handle: 0x0022 | 1 байт uint8", size=10, color=MUTED))

    frags.append(rect(575, 262, 260, 84, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(705, 282, "CCCD (UUID: 0x2902)", size=11, bold=True, color="#b45309"))
    frags.append(text(705, 300, "Handle: 0x0023 | 2 байти", size=10, color="#92400e"))
    frags.append(text(705, 318, "Дозволяє телефону отримувати", size=10, color="#92400e"))
    frags.append(text(705, 334, "сповіщення про розряд", size=10, color="#92400e"))

    # Explanatory bottom note inside Service 2
    frags.append(rect(565, 372, 280, 93, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(705, 394, "Таблиця атрибутів ATT:", size=11, bold=True, color="#475569"))
    frags.append(text(705, 412, "Кожен елемент має Handle,", size=10, color="#475569"))
    frags.append(text(705, 430, "UUID, Permissions та Value.", size=10, color="#475569"))
    frags.append(text(705, 448, "Клієнт звертається за Handle.", size=10, color="#475569"))

    return render(path, w, h, *frags)


def fig_operations_sequence(path):
    """Фігура 2: Порівняння операцій ATT — Read/Write, Write Without Response, Notify, Indicate."""
    w, h = 900, 560
    frags = []

    # Загальний фон
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # Стовпчики: Смартфон (GATT Client) та Вбудований пристрій (GATT Server)
    frags.append(rect(50, 15, 220, 36, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(160, 38, "Смартфон (GATT Client)", size=13, bold=True, color="#1e40af"))

    frags.append(rect(630, 15, 220, 36, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(740, 38, "Пристрій (GATT Server)", size=13, bold=True, color="#15803d"))

    # Вертикальні лінії життя
    frags.append(line(160, 55, 160, 530, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(line(740, 55, 740, 530, color="#94a3b8", sw=1.5, dash="4,4"))

    # Секція 1: Читання та Запис із підтвердженням (Синхронний двосторонній обмін)
    frags.append(rect(230, 65, 440, 24, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    frags.append(text(450, 81, "1. Читання та Запис із квитанцією (ATT Request / Response)", size=11, bold=True, color="#475569"))

    # Read Request
    frags.append(arrow(160, 105, 735, 105, color="#2563eb", sw=1.8))
    frags.append(text(450, 100, "ATT_READ_REQ [Handle: 0x0013]", size=11, bold=True, color="#1d4ed8"))

    # Read Response
    frags.append(arrow(740, 135, 165, 135, color="#16a34a", sw=1.8))
    frags.append(text(450, 130, "ATT_READ_RSP [Value: 0x18, 0x0D, ...]", size=11, bold=True, color="#15803d"))
    frags.append(text(450, 148, "(Затримка: мінімум 1-2 інтервали з'єднання на кожне опитування)", size=10, italic=True, color=MUTED))

    # Секція 2: Швидкий запис без підтвердження (Write Without Response)
    frags.append(rect(230, 170, 440, 24, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    frags.append(text(450, 186, "2. Швидкий потік команд (ATT Write Without Response / Command)", size=11, bold=True, color="#475569"))

    frags.append(arrow(160, 210, 735, 210, color="#2563eb", sw=1.8))
    frags.append(text(450, 205, "ATT_WRITE_CMD [Handle: 0x0017, Value: CMD_START]", size=11, bold=True, color="#1d4ed8"))

    frags.append(arrow(160, 235, 735, 235, color="#2563eb", sw=1.8))
    frags.append(text(450, 230, "ATT_WRITE_CMD [Handle: 0x0017, Value: CMD_PARAM]", size=11, bold=True, color="#1d4ed8"))
    frags.append(text(450, 252, "(Немає квитанції ATT; повтори виконує канальний рівень Link Layer при помилці CRC)", size=10, italic=True, color=MUTED))

    # Секція 3: Асинхронне сповіщення (Notify) — основний канал телеметрії
    frags.append(rect(230, 275, 440, 24, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    frags.append(text(450, 291, "3. Асинхронне сповіщення сервера (ATT Handle Value Notification)", size=11, bold=True, color="#475569"))

    # Subscription step
    frags.append(arrow(160, 315, 735, 315, color="#d97706", sw=1.6))
    frags.append(text(450, 310, "ATT_WRITE_REQ [CCCD Handle: 0x0014, Value: 0x0001 (Підписка)]", size=10, bold=True, color="#b45309"))

    frags.append(arrow(740, 335, 165, 335, color="#d97706", sw=1.6))
    frags.append(text(450, 330, "ATT_WRITE_RSP [CCCD налаштовано]", size=10, color="#b45309"))

    # Fast Notifications
    frags.append(arrow(740, 365, 165, 365, color="#16a34a", sw=1.8))
    frags.append(text(450, 360, "ATT_HANDLE_VALUE_NTF [Handle: 0x0013, Data Pack 1]", size=11, bold=True, color="#15803d"))

    frags.append(arrow(740, 390, 165, 390, color="#16a34a", sw=1.8))
    frags.append(text(450, 385, "ATT_HANDLE_VALUE_NTF [Handle: 0x0013, Data Pack 2]", size=11, bold=True, color="#15803d"))
    frags.append(text(450, 408, "(Максимальна пропускна здатність: кілька пакетів за один інтервал з'єднання)", size=10, italic=True, color=MUTED))

    # Секція 4: Індикація з підтвердженням (Indicate)
    frags.append(rect(230, 430, 440, 24, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    frags.append(text(450, 446, "4. Критичне сповіщення з квитанцією (ATT Handle Value Indication)", size=11, bold=True, color="#475569"))

    frags.append(arrow(740, 470, 165, 470, color="#dc2626", sw=1.8))
    frags.append(text(450, 465, "ATT_HANDLE_VALUE_IND [Handle: 0x0013, Alarm / Event]", size=11, bold=True, color="#b91c1c"))

    frags.append(arrow(160, 500, 735, 500, color="#2563eb", sw=1.8))
    frags.append(text(450, 495, "ATT_HANDLE_VALUE_CFM (Підтвердження отримання клієнтом)", size=11, bold=True, color="#1d4ed8"))
    frags.append(text(450, 518, "(Сервер блокує наступні індикації, доки не отримає підтвердження CFM)", size=10, italic=True, color=MUTED))

    return render(path, w, h, *frags)


def fig_mtu_dle_throughput(path):
    """Фігура 3: Оптимізація MTU та DLE — спад накладних витрат та зростання корисної швидкості."""
    w, h = 880, 520
    frags = []

    # Загальний фон
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # Ліва половина: Спадщина Bluetooth 4.0/4.1 (За замовчуванням: MTU = 23, DLE = 27)
    frags.append(rect(30, 20, 390, 480, fill="#fff1f2", stroke="#f43f5e", sw=1.8, rx=8))
    frags.append(text(225, 48, "Стандартний режим (Bluetooth 4.0 / 4.1)", size=14, bold=True, color="#be123c"))
    frags.append(text(225, 68, "ATT MTU = 23 байти  |  Link Layer PDU = 27 байтів", size=11, color="#9f1239"))

    # ATT Packet breakdown (23 bytes)
    frags.append(rect(50, 95, 350, 95, fill="#ffffff", stroke="#fb7185", sw=1.4, rx=6))
    frags.append(text(225, 118, "Пакет ATT (Макс. 23 байти)", size=12, bold=True, color="#881337"))

    frags.append(rect(65, 130, 80, 45, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(105, 150, "Opcode", size=10, bold=True, color="#9a3412"))
    frags.append(text(105, 165, "1 байт", size=9, color="#7c2d12"))

    frags.append(rect(150, 130, 85, 45, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(192, 150, "Handle", size=10, bold=True, color="#9a3412"))
    frags.append(text(192, 165, "2 байти", size=9, color="#7c2d12"))

    frags.append(rect(240, 130, 145, 45, fill="#dcfce7", stroke="#16a34a", sw=1, rx=4))
    frags.append(text(312, 150, "Корисні дані (Payload)", size=10, bold=True, color="#15803d"))
    frags.append(text(312, 165, "Рівно 20 байтів!", size=9, bold=True, color="#166534"))

    # L2CAP & Link Layer encapsulation
    frags.append(rect(50, 205, 350, 110, fill="#ffffff", stroke="#fb7185", sw=1.4, rx=6))
    frags.append(text(225, 228, "Канальний рівень Link Layer (PDU = 27 байтів)", size=12, bold=True, color="#881337"))

    frags.append(rect(65, 242, 60, 42, fill="#e2e8f0", stroke="#64748b", sw=1, rx=4))
    frags.append(text(95, 258, "LL Hdr", size=10, color="#334155"))
    frags.append(text(95, 273, "2B", size=10, color=MUTED))

    frags.append(rect(130, 242, 65, 42, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(162, 258, "L2CAP Hdr", size=10, color="#9a3412"))
    frags.append(text(162, 273, "4B", size=10, color=MUTED))

    frags.append(rect(200, 242, 125, 42, fill="#fecdd3", stroke="#f43f5e", sw=1, rx=4))
    frags.append(text(262, 266, "ATT (23B)", size=10, color="#9f1239"))

    frags.append(rect(330, 242, 55, 42, fill="#e2e8f0", stroke="#64748b", sw=1, rx=4))
    frags.append(text(357, 258, "CRC", size=10, color="#334155"))
    frags.append(text(357, 273, "3B", size=10, color=MUTED))

    frags.append(text(225, 302, "Накладні витрати заголовків: 13 байтів на 20 байтів даних!", size=10, bold=True, color="#be123c"))

    # Metrics summary for 4.0
    frags.append(rect(50, 330, 350, 155, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    frags.append(text(225, 355, "Результат для потоку даних:", size=12, bold=True, color="#991b1b"))
    frags.append(text(225, 380, "• Максимальна швидкість: ~2–5 КБ/с", size=11, color="#7f1d1d"))
    frags.append(text(225, 402, "• Передача 1 КБ: 51 окремий ATT-пакет", size=11, color="#7f1d1d"))
    frags.append(text(225, 424, "• Радіоефір (Air Time): великий, батарея сідає", size=11, color="#7f1d1d"))
    frags.append(text(225, 446, "• Фрагментація L2CAP на рівні стека", size=11, color="#7f1d1d"))
    frags.append(text(225, 468, "• Фізичний рівень: 1M PHY (1 Мбіт/с)", size=11, color=MUTED))

    # Права половина: Оптимізований стек (Bluetooth 4.2 / 5.0+ з DLE та 2M PHY)
    frags.append(rect(460, 20, 390, 480, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    frags.append(text(655, 48, "Оптимізований режим (Bluetooth 4.2 / 5.0+)", size=14, bold=True, color="#15803d"))
    frags.append(text(655, 68, "ATT MTU = 247–512 B  |  DLE = 251 B  |  2M PHY", size=11, color="#166534"))

    # ATT Packet breakdown (247 bytes)
    frags.append(rect(480, 95, 350, 95, fill="#ffffff", stroke="#86efac", sw=1.4, rx=6))
    frags.append(text(655, 118, "Пакет ATT (Узгоджено MTU = 247 байтів)", size=12, bold=True, color="#14532d"))

    frags.append(rect(495, 130, 75, 45, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(532, 150, "Opcode", size=10, bold=True, color="#9a3412"))
    frags.append(text(532, 165, "1 байт", size=10, color="#7c2d12"))

    frags.append(rect(575, 130, 80, 45, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(615, 150, "Handle", size=10, bold=True, color="#9a3412"))
    frags.append(text(615, 165, "2 байти", size=10, color="#7c2d12"))

    frags.append(rect(660, 130, 155, 45, fill="#bbf7d0", stroke="#16a34a", sw=1.4, rx=4))
    frags.append(text(737, 150, "Корисні дані (Payload)", size=10, bold=True, color="#15803d"))
    frags.append(text(737, 165, "244 байти в одному пакеті!", size=10, bold=True, color="#14532d"))

    # Link Layer with DLE (251 bytes PDU)
    frags.append(rect(480, 205, 350, 110, fill="#ffffff", stroke="#86efac", sw=1.4, rx=6))
    frags.append(text(655, 228, "Data Length Extension (Link Layer PDU = 251 байт)", size=12, bold=True, color="#14532d"))

    frags.append(rect(495, 242, 50, 42, fill="#e2e8f0", stroke="#64748b", sw=1, rx=4))
    frags.append(text(520, 258, "LL Hdr", size=10, color="#334155"))
    frags.append(text(520, 273, "2B", size=10, color=MUTED))

    frags.append(rect(550, 242, 55, 42, fill="#fed7aa", stroke="#ea580c", sw=1, rx=4))
    frags.append(text(577, 258, "L2CAP", size=10, color="#9a3412"))
    frags.append(text(577, 273, "4B", size=10, color=MUTED))

    frags.append(rect(610, 242, 160, 42, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    frags.append(text(690, 266, "ATT (247B = 3B Hdr + 244B Data)", size=10, bold=True, color="#15803d"))

    frags.append(rect(775, 242, 45, 42, fill="#e2e8f0", stroke="#64748b", sw=1, rx=4))
    frags.append(text(797, 258, "CRC", size=10, color="#334155"))
    frags.append(text(797, 273, "3B", size=10, color=MUTED))

    frags.append(text(655, 302, "Накладні витрати: лише 13 байтів на 244 байти даних (~95% ККД)", size=10, bold=True, color="#15803d"))

    # Metrics summary for 5.0+
    frags.append(rect(480, 330, 350, 155, fill="#ffffff", stroke="#86efac", sw=1, rx=6))
    frags.append(text(655, 355, "Результат для потоку даних:", size=12, bold=True, color="#14532d"))
    frags.append(text(655, 380, "• Максимальна швидкість: ~60–140 КБ/с", size=11, bold=True, color="#15803d"))
    frags.append(text(655, 402, "• Передача 1 КБ: лише 5 пакетів замість 51", size=11, color="#166534"))
    frags.append(text(655, 424, "• Радіоефір скорочено в 10 разів -> економія струму", size=11, color="#166534"))
    frags.append(text(655, 446, "• Нульова фрагментація на канальному рівні", size=11, color="#166534"))
    frags.append(text(655, 468, "• Фізичний рівень 2M PHY: удвічі коротший біт", size=11, bold=True, color="#15803d"))

    return render(path, w, h, *frags)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    fig_gatt_hierarchy(os.path.join(out_dir, "gatt-hierarchy.svg"))
    fig_operations_sequence(os.path.join(out_dir, "operations-sequence.svg"))
    fig_mtu_dle_throughput(os.path.join(out_dir, "mtu-dle-throughput.svg"))
    print("Всі 3 фігури успішно згенеровано у", out_dir)
