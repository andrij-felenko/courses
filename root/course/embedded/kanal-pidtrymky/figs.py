# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра кольорів
ACCENT = "#2563eb"
ACCENT_BG = "#eff6ff"
BORDER = "#cbd5e1"
TEXT_DARK = "#0f172a"
SUCCESS = "#16a34a"
SUCCESS_BG = "#f0fdf4"
DANGER = "#dc2626"
DANGER_BG = "#fef2f2"
WARN = "#d97706"
WARN_BG = "#fffbeb"
PURPLE = "#7c3aed"
PURPLE_BG = "#f5f3ff"


# ── 1. support-channel-architecture.svg ────────────────────────────────────
# Архітектура каналів технічної підтримки вбудованих пристроїв
def fig_support_channel_architecture():
    W, H = 940, 480
    p = []
    p.append(text(W / 2, 26, "Архітектура каналів технічної підтримки та маршрутизації інцидентів", size=15, bold=True))

    # Ліва колонка: Джерела збору даних та канали входу
    p.append(rect(25, 55, 270, 395, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(160, 78, "1. Канали входу та джерела", size=12, bold=True, color="#334155"))

    sources = [
        ("Автоматична телеметрія", "Crash Dump через MQTT/HTTPS", "#eff6ff", ACCENT),
        ("Локальний сервісний порт", "USB CDC / UART дамп через CLI", "#f0fdf4", SUCCESS),
        ("Клієнтський веб-портал", "Форма з обов'язковим S/N та логом", "#fffbeb", WARN),
        ("QR-код аварійного стану", "Сканування з екрана / консолі", "#f5f3ff", PURPLE)
    ]
    sy = 95
    for title, desc, bg, col in sources:
        p.append(rect(40, sy, 240, 68, fill=bg, stroke=col, sw=1.2, rx=6))
        p.append(text(52, sy + 22, title, size=11, bold=True, color=col, anchor="start"))
        p.append(text(52, sy + 42, desc, size=9.5, color=TEXT_DARK, anchor="start"))
        p.append(text(52, sy + 58, "Формат: Support Bundle + HW Rev", size=9.0, color="#64748b", anchor="start"))
        sy += 82

    # Центральна колонка: Автоматизований шлюз тріажу та валідації
    p.append(rect(335, 55, 270, 395, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(470, 78, "2. Серверний тріаж і валідація", size=12, bold=True, color="#334155"))

    triage_steps = [
        ("Парсер Support Bundle", "Перевірка Magic, CRC32, структури"),
        ("Звірка з паспортом виробу", "Перевірка S/N, партії, OTP-ключів"),
        ("Символізація та аналіз", "addr2line / ELF за git-хешем білда"),
        ("Класифікація критичності", "Присвоєння Sev-1..Sev-4 за матрицею")
    ]
    ty = 95
    for title, desc in triage_steps:
        p.append(rect(350, ty, 240, 68, fill="#ffffff", stroke=BORDER, sw=1.2, rx=6))
        p.append(text(362, ty + 22, title, size=11, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(362, ty + 42, desc, size=9.5, color="#475569", anchor="start"))
        p.append(text(362, ty + 58, "Автоматичне збагачення контекстом", size=9.0, color=ACCENT, anchor="start"))
        ty += 82

    # Права колонка: Рівні інженерної ескалації
    p.append(rect(645, 55, 270, 395, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(780, 78, "3. Рівні інженерної ескалації", size=12, bold=True, color="#334155"))

    tiers = [
        ("L1: Service Desk", "Чек-лист живлення, гарантія, KB", "#f8fafc", "#475569"),
        ("L2: Field Applications", "Аналіз логів, стенд з тією ж HW Rev", ACCENT_BG, ACCENT),
        ("L3: Embedded Firmware", "Аналіз FreeRTOS, патч, OTA-реліз", PURPLE_BG, PURPLE),
        ("L4: Hardware R&D / RMA", "Лабораторний аналіз плати, 8D звіт", DANGER_BG, DANGER)
    ]
    ey = 95
    for title, desc, bg, col in tiers:
        p.append(rect(660, ey, 240, 68, fill=bg, stroke=col, sw=1.2, rx=6))
        p.append(text(672, ey + 22, title, size=11, bold=True, color=col, anchor="start"))
        p.append(text(672, ey + 42, desc, size=9.5, color=TEXT_DARK, anchor="start"))
        p.append(text(672, ey + 58, "SLA: регламентований час реакції", size=9.0, color="#64748b", anchor="start"))
        ey += 82

    # Зв'язувальні стрілки між етапами
    p.append(arrow(295, 130, 335, 130, color=ACCENT, sw=2.0))
    p.append(arrow(295, 212, 335, 212, color=SUCCESS, sw=2.0))
    p.append(arrow(295, 294, 335, 294, color=WARN, sw=2.0))
    p.append(arrow(295, 376, 335, 376, color=PURPLE, sw=2.0))

    p.append(arrow(605, 130, 645, 130, color="#64748b", sw=2.0))
    p.append(arrow(605, 212, 645, 212, color=ACCENT, sw=2.0))
    p.append(arrow(605, 294, 645, 294, color=PURPLE, sw=2.0))
    p.append(arrow(605, 376, 645, 376, color=DANGER, sw=2.0))

    render(os.path.join(OUT, "support-channel-architecture.svg"), W, H, *p)


# ── 2. diagnostic-snapshot-structure.svg ───────────────────────────────────
# Структура діагностичного пакета (Support Bundle / Crash Snapshot)
def fig_diagnostic_snapshot_structure():
    W, H = 940, 470
    p = []
    p.append(text(W / 2, 26, "Анатомія діагностичного знімка (Support Bundle / Crash Snapshot)", size=15, bold=True))

    # Верхній блок: Заголовок пакета
    p.append(rect(30, 52, 880, 85, fill=ACCENT_BG, stroke=ACCENT, sw=1.6, rx=8))
    p.append(text(45, 74, "1. Заголовок пакета та цифрова ідентифікація (Header & System ID — 64 байти)", size=11.5, bold=True, color=ACCENT, anchor="start"))
    p.append(line(30, 84, 910, 84, color=BORDER, sw=1.0))

    hdr_fields = [
        ("Magic / Версія", "0x4442554E ('DBUN') v2"),
        ("S/N та HW Rev", "GW500-2026-0042 / Rev C"),
        ("Хеш прошивки", "Git: 7f89bc2 (Release)"),
        ("Uptime / Reset Reason", "42d 18h / 0x08 (Watchdog)")
    ]
    hx = 45
    for title, val in hdr_fields:
        p.append(rect(hx, 92, 200, 36, fill="#ffffff", stroke=BORDER, sw=1.0, rx=4))
        p.append(text(hx + 10, 106, title, size=9.5, bold=True, color="#475569", anchor="start"))
        p.append(text(hx + 10, 121, val, size=9.5, color=TEXT_DARK, anchor="start"))
        hx += 215

    # Середній ряд: 3 спеціалізовані блоки даних
    mid_y = 150
    mid_h = 185
    card_w = 280

    # Блок 2: Аварійні регістри ядра та стек
    p.append(rect(30, mid_y, card_w, mid_h, fill="#ffffff", stroke=DANGER, sw=1.4, rx=8))
    p.append(rect(30, mid_y, card_w, 32, fill=DANGER_BG, stroke=DANGER, sw=1.2, rx=8))
    p.append(text(30 + card_w / 2, mid_y + 20, "2. Аварійний стан ядра (Fault Context)", size=10.5, bold=True, color=DANGER))

    fault_items = [
        ("Регістри Cortex-M:", "CFSR, HFSR, MMFAR, BFAR"),
        ("Стек-фрейм винятку:", "PC, LR, SP, R0-R3, R12, xPSR"),
        ("Task Control Block:", "ID активної таски, ліміт стека"),
        ("Адреса виклику:", "addr2line -> drivers/i2c_bus.c:142")
    ]
    fy = mid_y + 42
    for k, v in fault_items:
        p.append(text(42, fy + 12, k, size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(42, fy + 26, v, size=9.0, color="#64748b", anchor="start"))
        fy += 34

    # Блок 3: Телеметрія живлення та середовища
    x_mid = 330
    p.append(rect(x_mid, mid_y, card_w, mid_h, fill="#ffffff", stroke=SUCCESS, sw=1.4, rx=8))
    p.append(rect(x_mid, mid_y, card_w, 32, fill=SUCCESS_BG, stroke=SUCCESS, sw=1.2, rx=8))
    p.append(text(x_mid + card_w / 2, mid_y + 20, "3. Живлення та середовище (Telemetry)", size=10.5, bold=True, color=SUCCESS))

    env_items = [
        ("Шини вхідної напруги:", "Vin = 23.8V, V33 = 3.29V"),
        ("Стан резервної батареї:", "Vbat = 3.92V, SoC = 88%"),
        ("Температурний профіль:", "MCU = +48°C, Плата = +39°C"),
        ("Лічильники живлення:", "Brownout: 0, Power cycles: 14")
    ]
    ey = mid_y + 42
    for k, v in env_items:
        p.append(text(x_mid + 12, ey + 12, k, size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(x_mid + 12, ey + 26, v, size=9.0, color="#64748b", anchor="start"))
        ey += 34

    # Блок 4: Статистика шин та периферії
    x_right = 630
    p.append(rect(x_right, mid_y, card_w, mid_h, fill="#ffffff", stroke=WARN, sw=1.4, rx=8))
    p.append(rect(x_right, mid_y, card_w, 32, fill=WARN_BG, stroke=WARN, sw=1.2, rx=8))
    p.append(text(x_right + card_w / 2, mid_y + 20, "4. Здоров'я периферії та шин", size=10.5, bold=True, color=WARN))

    bus_items = [
        ("I2C / SPI помилки:", "I2C NACK: 3, SPI Timeout: 0"),
        ("RS-485 / CAN лічильники:", "CAN Bus-Off: 0, CRC Err: 12"),
        ("Флеш-пам'ять / NVS:", "Flash Bad Blocks: 0, NVS: 42% free"),
        ("Радіоканал / Мережа:", "RSSI: -74 dBm, Reconnects: 2")
    ]
    by = mid_y + 42
    for k, v in bus_items:
        p.append(text(x_right + 12, by + 12, k, size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(x_right + 12, by + 26, v, size=9.0, color="#64748b", anchor="start"))
        by += 34

    # Нижній блок: Кільцевий буфер логів та контрольна сума
    bot_y = 350
    p.append(rect(30, bot_y, 880, 100, fill="#f8fafc", stroke=PURPLE, sw=1.6, rx=8))
    p.append(text(45, bot_y + 22, "5. Кільцевий буфер подій у FRAM/Flash та цілісність (Circular Event Log + CRC32)", size=11.5, bold=True, color=PURPLE, anchor="start"))

    log_samples = [
        ("[T-180s] SYS: Network link established (LTE Cat-M1)", "INFO"),
        ("[T-45s] SENS: Pressure sensor BMP390 read timeout (I2C1)", "WARN"),
        ("[T-2s] WDT: Task 'telemetry_tx' blocked for 5000ms", "ERROR"),
        ("[T-0s] FAULT: HardFault raised, saving crash snapshot to Flash", "CRITICAL")
    ]
    ly = bot_y + 36
    for log_line, level in log_samples:
        col = DANGER if level == "CRITICAL" else (WARN if level in ("WARN", "ERROR") else "#475569")
        p.append(text(45, ly + 11, log_line, size=9.0, color=col, anchor="start"))
        ly += 14

    p.append(text(890, bot_y + 88, "Контрольна сума всього пакета: CRC32 / SHA-256", size=9.5, bold=True, color=PURPLE, anchor="end"))

    render(os.path.join(OUT, "diagnostic-snapshot-structure.svg"), W, H, *p)


# ── 3. escalation-sla-matrix.svg ───────────────────────────────────────────
# Матриця ескалації, критичність інцидентів, часові рамки SLA та контур RMA
def fig_escalation_sla_matrix():
    W, H = 940, 480
    p = []
    p.append(text(W / 2, 26, "Матриця рівнів критичності (Severity), регламенти SLA та контур RMA", size=15, bold=True))

    # Ліва таблиця: 4 рівні Severity та часові рамки
    p.append(rect(25, 52, 570, 400, fill="#ffffff", stroke="#64748b", sw=1.6, rx=8))
    p.append(rect(25, 52, 570, 36, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=8))
    p.append(text(310, 75, "Матриця критичності інцидентів та гарантований час SLA", size=12, bold=True, color="#334155"))

    sev_rows = [
        ("Sev-1: Критичний (Critical)", "Повна відмова системи, ризик життю / майну, простій об'єкта", "< 1 год", "< 4 год", DANGER_BG, DANGER),
        ("Sev-2: Високий (Major)", "Втрата ключової функції без аварійної зупинки, немає обходу", "< 2 год", "< 12 год", WARN_BG, WARN),
        ("Sev-3: Середній (Minor)", "Частковий збій, деградація продуктивності, є обхідний шлях", "< 8 год", "< 48 год", ACCENT_BG, ACCENT),
        ("Sev-4: Низький (Cosmetic)", "Запитання, документація, косметичні дефекти інтерфейсу", "< 24 год", "Sprint release", "#f8fafc", "#64748b")
    ]
    ry = 98
    for name, desc, frt, fix, bg, col in sev_rows:
        p.append(rect(38, ry, 544, 78, fill=bg, stroke=col, sw=1.2, rx=6))
        p.append(text(50, ry + 22, name, size=11, bold=True, color=col, anchor="start"))
        p.append(text(50, ry + 42, desc, size=9.5, color=TEXT_DARK, anchor="start"))
        p.append(text(50, ry + 62, "Перша реакція (FRT): " + frt, size=9.0, bold=True, color="#475569", anchor="start"))
        p.append(text(340, ry + 62, "Тимчасове / повне усунення: " + fix, size=9.0, bold=True, color=col, anchor="start"))
        ry += 86

    # Права частина: Контур повернення та апаратного аналізу RMA
    p.append(rect(615, 52, 300, 400, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(rect(615, 52, 300, 36, fill=PURPLE_BG, stroke=PURPLE, sw=1.2, rx=8))
    p.append(text(765, 75, "Контур повернення заліза (RMA Flow)", size=12, bold=True, color=PURPLE))

    rma_steps = [
        ("1. Верифікація дефекту", "L2/L3 підтверджують апаратну несправність за дампом"),
        ("2. Видача номера RMA", "Клієнт отримує RMA ID та транспортну накладну"),
        ("3. Карантин і первинний тест", "Вхідний ESD-контроль, перевірка живлення на стенді"),
        ("4. Лабораторний аналіз R&D", "Рентген BGA, тепловізор, мікроскопія дефектів"),
        ("5. Звіт 8D / Заміна виробу", "Відправка заміни та внесення змін у BOM / прошивку")
    ]
    my = 98
    for step, detail in rma_steps:
        p.append(rect(628, my, 274, 62, fill="#ffffff", stroke=BORDER, sw=1.0, rx=5))
        p.append(text(640, my + 20, step, size=10.5, bold=True, color=PURPLE, anchor="start"))
        p.append(text(640, my + 38, detail, size=9.0, color="#475569", anchor="start"))
        p.append(text(640, my + 52, "Регламентний термін: 5–10 робочих днів", size=9.0, color="#94a3b8", anchor="start"))
        my += 70

    render(os.path.join(OUT, "escalation-sla-matrix.svg"), W, H, *p)


if __name__ == "__main__":
    fig_support_channel_architecture()
    fig_diagnostic_snapshot_structure()
    fig_escalation_sla_matrix()
    print("Figures generated successfully.")
