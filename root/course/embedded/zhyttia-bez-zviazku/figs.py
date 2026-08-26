# -*- coding: utf-8 -*-
"""Фігури для статті «Життя без зв'язку: що пристрій вирішує сам» (zhyttia-bez-zviazku).
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

# Кольори підсистем
PWR_COLOR   = "#b91c1c"  # Червоний: аварії / живлення
CORE_COLOR  = "#1d4ed8"  # Синій: локальний контур керування
SYNC_COLOR  = "#047857"  # Зелений: агент синхронізації та мережа
STORAGE_CLR = "#b45309"  # Бурштиновий: енергонезалежна пам'ять
CARD_BG     = "#ffffff"


def fig_offline_architecture():
    """1. offline-architecture.svg — Архітектура суверенного автономного вузла."""
    W, H = 860, 520
    parts = []

    # Загальна підкладка
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Архітектура суверенного автономного вузла (Offline-First)", size=16, color=INK, bold=True))

    # Зона 1: Фізичний світ та локальний контур (Зліва)
    bx1, by1, bw1, bh1 = 25, 60, 510, 435
    parts.append(rect(bx1, by1, bw1, bh1, fill="#f1f5f9", stroke=CORE_COLOR, sw=2, rx=8))
    parts.append(rect(bx1, by1, bw1, 32, fill="#dbeafe", stroke=CORE_COLOR, sw=1.5, rx=8))
    parts.append(text(bx1 + bw1 / 2, by1 + 21, "Локальний суверенний контур керування (10-100 Гц, Hard/Soft RT)", size=13, color=CORE_COLOR, bold=True))

    # Сенсори (вхід)
    parts.append(fitbox(45, 110, 130, 60, "Сенсори\n(темп, тиск, АЦП)", size=12, fill=CARD_BG, stroke="#64748b", bold=True))
    # Актуатори (вихід)
    parts.append(fitbox(45, 230, 130, 60, "Актуатори\n(реле, клапани, ШІМ)", size=12, fill=CARD_BG, stroke="#64748b", bold=True))

    # Центральний блок: Автономний рушій правил (Local Decision Engine)
    parts.append(rect(225, 110, 170, 180, fill=CARD_BG, stroke=CORE_COLOR, sw=2, rx=6))
    parts.append(rect(225, 110, 170, 28, fill="#eff6ff", stroke=CORE_COLOR, sw=1.2, rx=6))
    parts.append(text(310, 128, "Локальний рушій правил", size=11, color=CORE_COLOR, bold=True))
    engine_desc = [
        "• Розклади (RTC)",
        "• Гістерезис / PID",
        "• Таблиця правил ACL",
        "• Захисні блокування",
        "• Безпечний стан (Fail-safe)"
    ]
    for i, line_str in enumerate(engine_desc):
        parts.append(text(235, 155 + i * 24, line_str, size=10, color=INK, anchor="start"))

    # Сховище NVM (внизу лівої зони)
    parts.append(rect(45, 330, 470, 145, fill=CARD_BG, stroke=STORAGE_CLR, sw=1.8, rx=6))
    parts.append(rect(45, 330, 470, 26, fill="#fef3c7", stroke=STORAGE_CLR, sw=1.2, rx=6))
    parts.append(text(280, 347, "Енергонезалежна пам'ять (Flash / FRAM / EEPROM)", size=11, color=STORAGE_CLR, bold=True))

    # Блоки всередині NVM
    parts.append(fitbox(55, 365, 130, 95, "Конфігурація A/B\n(Розклади, уставки,\nключі доступу,\nCRC32-захист)", size=10, fill="#fffbeb", stroke=STORAGE_CLR))
    parts.append(fitbox(195, 365, 150, 95, "Критичний буфер\n(Аварії, E-Stop,\nпорушення безпеки,\nHard Ring Buffer)", size=10, fill="#fee2e2", stroke=PWR_COLOR))
    parts.append(fitbox(355, 365, 150, 95, "Буфер телеметрії\n(Поточні виміри,\nпроріджування,\nDeadband / Compaction)", size=10, fill="#ecfdf5", stroke=SYNC_COLOR))

    # Стрілки в лівій зоні
    parts.append(arrow(175, 140, 225, 140, color="#475569", sw=1.5))
    parts.append(arrow(225, 260, 175, 260, color="#475569", sw=1.5))
    parts.append(arrow(310, 290, 310, 330, color=STORAGE_CLR, sw=1.5))

    # Зона 2: Фонова синхронізація та зв'язок (Справа)
    bx2, by2, bw2, bh2 = 555, 60, 280, 435
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f0fdf4", stroke=SYNC_COLOR, sw=2, rx=8))
    parts.append(rect(bx2, by2, bw2, 32, fill="#dcfce7", stroke=SYNC_COLOR, sw=1.5, rx=8))
    parts.append(text(bx2 + bw2 / 2, by2 + 21, "Фоновий агент синхронізації", size=13, color=SYNC_COLOR, bold=True))

    # Стан лінка
    parts.append(fitbox(575, 110, 240, 65, "Детектор лінка\n(Ping / Keep-alive / Backoff)\nOffline ⟷ Online", size=11, fill=CARD_BG, stroke=SYNC_COLOR, bold=True))

    # Рушій реконсиліації
    parts.append(fitbox(575, 195, 240, 85, "Рушій реконсиліації\n(State Reconciliation)\n• Дренаж аварійних черг\n• Злиття дельт стану\n• Оновлення конфігурації A/B", size=10, fill=CARD_BG, stroke=SYNC_COLOR))

    # Хмара / Бекенд
    parts.append(fitbox(575, 330, 240, 145, "Хмарний брокер / Бекенд\n(MQTT / HTTPS / CoAP)\n\n• Зберігання Desired State\n• Довготривала аналітика\n• Оновлення розкладів", size=11, fill="#e0f2fe", stroke="#0284c7", bold=True))

    # Міжзональні зв'язки
    parts.append(arrow(415, 180, 575, 230, color=SYNC_COLOR, sw=1.5))
    parts.append(arrow(575, 250, 470, 365, color=SYNC_COLOR, sw=1.5))
    parts.append(arrow(695, 280, 695, 330, color=SYNC_COLOR, sw=1.8))

    return render(out("offline-architecture.svg"), W, H, *parts)


def fig_priority_flash_buffer():
    """2. priority-flash-buffer.svg — Структура пріоритезованого буфера на Flash-пам'яті."""
    W, H = 860, 460
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Пріоритезація збереження даних у Flash під час тривалого офлайну", size=16, color=INK, bold=True))

    # Сектори пам'яті (Flash Layout)
    col_w = 255
    # Сектор 0: Критичні аварії
    parts.append(rect(30, 65, col_w, 370, fill="#fff5f5", stroke=PWR_COLOR, sw=2, rx=8))
    parts.append(rect(30, 65, col_w, 34, fill="#fee2e2", stroke=PWR_COLOR, sw=1.5, rx=8))
    parts.append(text(30 + col_w / 2, 87, "Рівень 0: Критичні аварії", size=12, color=PWR_COLOR, bold=True))

    desc_p0 = [
        "• Пожежа, витік, E-Stop",
        "• Відмова датчиків безпеки",
        "• Спрацювання тампера",
        "──────────────────────",
        "Політика переповнення:",
        "ЖОРСТКЕ ЗБЕРЕЖЕННЯ.",
        "Ніколи не перезаписується",
        "іншими типами даних.",
        "Виділений резервний сектор.",
        "Передача ПЕРШОЮ чергою",
        "після відновлення лінка."
    ]
    for i, l in enumerate(desc_p0):
        parts.append(text(45, 125 + i * 25, l, size=11, color=INK, anchor="start"))

    # Сектор 1: Аудит і зміна станів
    parts.append(rect(305, 65, col_w, 370, fill="#fefce8", stroke=STORAGE_CLR, sw=2, rx=8))
    parts.append(rect(305, 65, col_w, 34, fill="#fef08a", stroke=STORAGE_CLR, sw=1.5, rx=8))
    parts.append(text(305 + col_w / 2, 87, "Рівень 1: Журнал аудиту", size=12, color=STORAGE_CLR, bold=True))

    desc_p1 = [
        "• Прохід за RFID-ключем",
        "• Зміна режиму (Auto→Manual)",
        "• Увімкнення/вимкнення реле",
        "──────────────────────",
        "Політика переповнення:",
        "Кільцевий буфер (Ring Buffer).",
        "При нестачі місця старі записи",
        "витісняються за принципом",
        "FIFO з обов'язковою фіксацією",
        "кількості втрачених записів",
        "(Drop Counter)."
    ]
    for i, l in enumerate(desc_p1):
        parts.append(text(320, 125 + i * 25, l, size=11, color=INK, anchor="start"))

    # Сектор 2: Періодична телеметрія
    parts.append(rect(580, 65, col_w, 370, fill="#f0fdf4", stroke=SYNC_COLOR, sw=2, rx=8))
    parts.append(rect(580, 65, col_w, 34, fill="#bbf7d0", stroke=SYNC_COLOR, sw=1.5, rx=8))
    parts.append(text(580 + col_w / 2, 87, "Рівень 2: Телеметрія", size=12, color=SYNC_COLOR, bold=True))

    desc_p2 = [
        "• Температура, тиск, напруга",
        "• Періодичний зріз раз на N с",
        "• Статистика споживання",
        "──────────────────────",
        "Політика переповнення:",
        "ДИНАМІЧНА ДЕГРАДАЦІЯ:",
        "1. Фільтрація Deadband (Δ > ε)",
        "2. Агрегація (min / max / avg)",
        "3. Збільшення інтервалу (5с→1хв)",
        "4. Агресивне скидання найстаріших",
        "точок заради збереження P0/P1."
    ]
    for i, l in enumerate(desc_p2):
        parts.append(text(595, 125 + i * 25, l, size=11, color=INK, anchor="start"))

    return render(out("priority-flash-buffer.svg"), W, H, *parts)


def fig_state_reconciliation():
    """3. state-reconciliation.svg — Процедура реконсиліації стану після відновлення зв'язку."""
    W, H = 860, 500
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Процедура реконсиліації та злиття станів (Link Recovery)", size=16, color=INK, bold=True))

    # 4 горизонтальні кроки
    steps = [
        ("Крок 1: Відновлення лінка та джитер", [
            "• Детекція мережі (TCP/TLS handshake)",
            "• Випадкова затримка (Jitter 0..30 с) для запобігання Thundering Herd на сервер",
            "• Отримання точного часу через NTP / TLS"
        ], CORE_COLOR, "#eff6ff"),
        ("Крок 2: Обмін поколіннями (Generation Handshake)", [
            "• Пристрій надсилає локальну версію стану V_local",
            "• Сервер надсилає Desired State версії V_cloud",
            "• Виявлення розбіжностей у конфігураціях і уставках"
        ], STORAGE_CLR, "#fffbeb"),
        ("Крок 3: Семантичне злиття та вирішення конфліктів", [
            "• ПРАВИЛО БЕЗПЕКИ: Локальний аварійний стан (E-Stop, Fault) завжди блокує дистанційне увімкнення",
            "• ПРАВИЛО УСТАВОК: Нові розклади з хмари оновлюють NVM-слот A/B транзакційно"
        ], PWR_COLOR, "#fff5f5"),
        ("Крок 4: Дренаж черг і підтвердження (ACK Drain)", [
            "• Вивантаження буфера P0 (Аварії) → P1 → P2",
            "• Отримання підтвердження від бекенду (ACK id)",
            "• Атомарне зсунення хвоста черги у Flash і перехід у штатний синхронний режим"
        ], SYNC_COLOR, "#f0fdf4")
    ]

    box_y = 65
    box_h = 95
    for i, (title_str, lines_arr, border_clr, bg_clr) in enumerate(steps):
        by = box_y + i * 105
        parts.append(rect(35, by, 790, box_h, fill=bg_clr, stroke=border_clr, sw=1.8, rx=6))
        parts.append(rect(35, by, 790, 26, fill=CARD_BG, stroke=border_clr, sw=1.2, rx=6))
        parts.append(text(50, by + 18, title_str, size=12, color=border_clr, bold=True, anchor="start"))

        for j, line_txt in enumerate(lines_arr):
            parts.append(text(50, by + 45 + j * 20, line_txt, size=11, color=INK, anchor="start"))

        if i < 3:
            # Стрілка переходу вниз
            parts.append(arrow(430, by + box_h, 430, by + box_h + 10, color="#64748b", sw=1.8))

    return render(out("state-reconciliation.svg"), W, H, *parts)


def main():
    fig_offline_architecture()
    print("Generated offline-architecture.svg")

    fig_priority_flash_buffer()
    print("Generated priority-flash-buffer.svg")

    fig_state_reconciliation()
    print("Generated state-reconciliation.svg")


if __name__ == "__main__":
    main()
