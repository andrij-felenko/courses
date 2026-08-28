# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
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


# ── 1. box-layers-and-kit.svg ──────────────────────────────────────────────
# Анатомія пакувального комплекту: шари захисту, пристрій, аксесуари та папери
def fig_box_layers_and_kit():
    W, H = 900, 440
    p = []
    p.append(text(W / 2, 26, "Анатомія комплекту постачання вбудованого виробу", size=15, bold=True))

    # Зовнішня коробка
    p.append(rect(25, 52, 850, 370, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=10))
    p.append(text(45, 74, "Транспортувальна / роздрібна коробка (маркований гофрокартон + захисна пломба VOID)", size=11, bold=True, color="#475569", anchor="start"))

    card_y = 90
    card_h = 315
    w_main = 270
    w_acc = 265
    w_doc = 275

    # 1. Головний пристрій та захист
    x1 = 45
    p.append(rect(x1, card_y, w_main, card_h, fill="#ffffff", stroke=ACCENT, sw=1.6, rx=8))
    p.append(rect(x1, card_y, w_main, 34, fill=ACCENT_BG, stroke=ACCENT, sw=1.2, rx=8))
    p.append(text(x1 + w_main / 2, card_y + 22, "1. Головний пристрій (Device)", size=11.5, bold=True, color=ACCENT))

    items1 = [
        ("Корпус виробу з шильдиком", "Алюміній/ABS, клас IP67 або IP20"),
        ("Екранований ESD-пакет", "Захист від статики ANSI/ESD S541"),
        ("Пакетик із силікагелем", "Контроль вологи (десикант MSL)"),
        ("Вирізаний ложемент", "EVA/EPE піна для поглинання ударів"),
        ("Пломба першого розтину", "Контроль несанкціонованого доступу")
    ]
    ly = card_y + 54
    for title, desc in items1:
        p.append(rect(x1 + 10, ly, w_main - 20, 46, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=5))
        p.append(text(x1 + 18, ly + 18, title, size=10, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(x1 + 18, ly + 34, desc, size=9.5, color="#64748b", anchor="start"))
        ly += 52

    # 2. Апаратні аксесуари
    x2 = 325
    p.append(rect(x2, card_y, w_acc, card_h, fill="#ffffff", stroke=FIELD, sw=1.6, rx=8))
    p.append(rect(x2, card_y, w_acc, 34, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(x2 + w_acc / 2, card_y + 22, "2. Апаратні аксесуари (Kit)", size=11.5, bold=True, color=FIELD))

    items2 = [
        ("Узгоджена антена", "Сертифікована в парі з модулем"),
        ("Кабель живлення / адаптер", "Відповідний переріз та роз'єм"),
        ("Клемники / термінатори", "Phoenix Contact, 120 Ом RS-485"),
        ("Монтажне кріплення", "Кронштейн DIN-рейки або VESA"),
        ("Монтажні гвинти та дюбелі", "Комплект швидкого закріплення")
    ]
    ly = card_y + 54
    for title, desc in items2:
        p.append(rect(x2 + 10, ly, w_acc - 20, 46, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=5))
        p.append(text(x2 + 18, ly + 18, title, size=10, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(x2 + 18, ly + 34, desc, size=9.5, color="#64748b", anchor="start"))
        ly += 52

    # 3. Документація та вкладиші
    x3 = 600
    p.append(rect(x3, card_y, w_doc, card_h, fill="#ffffff", stroke=PURPLE, sw=1.6, rx=8))
    p.append(rect(x3, card_y, w_doc, 34, fill=PURPLE_BG, stroke=PURPLE, sw=1.2, rx=8))
    p.append(text(x3 + w_doc / 2, card_y + 22, "3. Папери та ідентифікація", size=11.5, bold=True, color=PURPLE))

    items3 = [
        ("Quick Start Guide (QSG)", "Буклет швидкого старту (1 аркуш)"),
        ("Safety & Compliance Card", "Декларація CE/FCC, WEEE, безпека"),
        ("Гарантійний вкладиш", "Умови сервісу, контакти підтримки"),
        ("Open Source Notice", "FOSS ліцензії, оферта на вихідний код"),
        ("Липкі наліпки з S/N і MAC", "Для монтажного журналу та щита")
    ]
    ly = card_y + 54
    for title, desc in items3:
        p.append(rect(x3 + 10, ly, w_doc - 20, 46, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=5))
        p.append(text(x3 + 18, ly + 18, title, size=10, bold=True, color=TEXT_DARK, anchor="start"))
        p.append(text(x3 + 18, ly + 34, desc, size=9.5, color="#64748b", anchor="start"))
        ly += 52

    render(os.path.join(OUT, "box-layers-and-kit.svg"), W, H, *p)


# ── 2. device-and-box-labels.svg ───────────────────────────────────────────
# Топологія та анатомія шильдика пристрою проти етикетки на коробці
def fig_device_and_box_labels():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 26, "Анатомія шильдика пристрою (Rating Plate) та коробкової наліпки", size=15, bold=True))

    col_w = 400
    card_h = 365
    y0 = 55

    # Ліва колонка: Шильдик на корпусі пристрою
    x_dev = 30
    p.append(rect(x_dev, y0, col_w, card_h, fill="#ffffff", stroke="#334155", sw=1.8, rx=8))
    p.append(rect(x_dev, y0, col_w, 34, fill="#f1f5f9", stroke="#334155", sw=1.2, rx=8))
    p.append(text(x_dev + col_w / 2, y0 + 22, "Шильдик на корпусі виробу (Зносостійкий поліестер)", size=11.5, bold=True, color="#1e293b"))

    # Вміст шильдика
    p.append(text(x_dev + 18, y0 + 58, "PRO-GATEWAY INDUSTRIAL NODE", size=12, bold=True, color=ACCENT, anchor="start"))
    p.append(text(x_dev + 18, y0 + 76, "Model: GW-500-ETH-LTE   |   P/N: 902-00412-01", size=9.5, color=TEXT_DARK, anchor="start"))
    p.append(line(x_dev + 15, y0 + 86, x_dev + col_w - 15, y0 + 86, color="#cbd5e1", sw=1.0))

    # Електричні параметри та безпека
    p.append(text(x_dev + 18, y0 + 104, "Power: 9–36 V DC, 1.5 A max  (Vin + / GND / Earth)", size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
    p.append(text(x_dev + 18, y0 + 120, "Operating Temp: -40°C to +85°C   |   Ingress: IP67", size=9.5, color="#475569", anchor="start"))

    # Сертифікаційні номери
    p.append(rect(x_dev + 15, y0 + 132, col_w - 30, 48, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(x_dev + 25, y0 + 150, "FCC ID: 2ABCD-GW500LTE   |   IC: 12345A-GW500", size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
    p.append(text(x_dev + 25, y0 + 168, "Contains FCC ID: XPYUBX1901 (LTE Cellular Module)", size=9.5, color="#64748b", anchor="start"))

    # Ідентифікатори та штрихкоди
    p.append(text(x_dev + 18, y0 + 198, "S/N: SN202608450123", size=10, bold=True, color=TEXT_DARK, anchor="start"))
    p.append(text(x_dev + 18, y0 + 214, "MAC: 00:1A:22:3B:4C:5D", size=10, bold=True, color=TEXT_DARK, anchor="start"))
    p.append(text(x_dev + 18, y0 + 230, "HW Rev: 2.1   |   FW: v1.4.0", size=9.5, color="#475569", anchor="start"))

    # Імітація 2D DataMatrix та знаків відповідності
    p.append(rect(x_dev + col_w - 95, y0 + 188, 75, 75, fill="#f1f5f9", stroke="#475569", sw=1.4, rx=4))
    p.append(text(x_dev + col_w - 58, y0 + 224, "2D Data", size=10, bold=True, color="#334155"))
    p.append(text(x_dev + col_w - 58, y0 + 240, "Matrix", size=10, bold=True, color="#334155"))

    # Нижній блок регуляторних знаків
    p.append(line(x_dev + 15, y0 + 272, x_dev + col_w - 15, y0 + 272, color="#cbd5e1", sw=1.0))
    p.append(rect(x_dev + 18, y0 + 284, 46, 28, fill="#ffffff", stroke="#0f172a", sw=1.2, rx=4))
    p.append(text(x_dev + 41, y0 + 302, "CE", size=13, bold=True, color="#0f172a"))

    p.append(rect(x_dev + 72, y0 + 284, 56, 28, fill="#ffffff", stroke="#0f172a", sw=1.2, rx=4))
    p.append(text(x_dev + 100, y0 + 302, "UKCA", size=10.5, bold=True, color="#0f172a"))

    p.append(rect(x_dev + 136, y0 + 284, 52, 28, fill="#ffffff", stroke="#0f172a", sw=1.2, rx=4))
    p.append(text(x_dev + 162, y0 + 302, "FCC", size=10.5, bold=True, color="#0f172a"))

    p.append(rect(x_dev + 196, y0 + 284, 52, 28, fill="#ffffff", stroke="#0f172a", sw=1.2, rx=4))
    p.append(text(x_dev + 222, y0 + 302, "WEEE", size=9.5, bold=True, color="#0f172a"))

    p.append(rect(x_dev + 256, y0 + 284, 52, 28, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(x_dev + 282, y0 + 302, "RoHS", size=9.5, bold=True, color="#16a34a"))

    p.append(text(x_dev + col_w / 2, y0 + 342, "Made in Ukraine   |   ACME IoT Technologies Ltd", size=9.5, color="#64748b"))

    # Права колонка: Етикетка на зовнішній коробці
    x_box = 450
    p.append(rect(x_box, y0, col_w, card_h, fill="#ffffff", stroke="#2563eb", sw=1.8, rx=8))
    p.append(rect(x_box, y0, col_w, 34, fill=ACCENT_BG, stroke="#2563eb", sw=1.2, rx=8))
    p.append(text(x_box + col_w / 2, y0 + 22, "Складська етикетка на коробці (Logistics Label)", size=11.5, bold=True, color=ACCENT))

    # Вміст коробкової наліпки
    p.append(text(x_box + 18, y0 + 58, "PRO-GATEWAY INDUSTRIAL NODE KIT", size=12, bold=True, color=ACCENT, anchor="start"))
    p.append(text(x_box + 18, y0 + 76, "SKU: GW-500-ETH-LTE-EU   |   Qty: 1 PC", size=9.5, bold=True, color=TEXT_DARK, anchor="start"))
    p.append(line(x_box + 15, y0 + 86, x_box + col_w - 15, y0 + 86, color="#cbd5e1", sw=1.0))

    # Штрихкоди Code128 для сканера
    p.append(text(x_box + 18, y0 + 104, "Serial Number (1D Code 128):", size=9.5, color="#475569", anchor="start"))
    p.append(rect(x_box + 18, y0 + 112, 230, 24, fill="#f8fafc", stroke="#0f172a", sw=1.0, rx=3))
    p.append(text(x_box + 133, y0 + 128, "||| | ||||| || |||| || ||||| | |||", size=12, color=TEXT_DARK))
    p.append(text(x_box + 133, y0 + 148, "*SN202608450123*", size=9.5, bold=True, color=TEXT_DARK))

    p.append(text(x_box + 18, y0 + 168, "Ethernet MAC Address:", size=9.5, color="#475569", anchor="start"))
    p.append(rect(x_box + 18, y0 + 176, 230, 24, fill="#f8fafc", stroke="#0f172a", sw=1.0, rx=3))
    p.append(text(x_box + 133, y0 + 192, "|| |||| | ||| |||| | || |||| || |||", size=12, color=TEXT_DARK))
    p.append(text(x_box + 133, y0 + 212, "*001A223B4C5D*", size=9.5, bold=True, color=TEXT_DARK))

    # 2D QR для мобільного онбордингу
    p.append(rect(x_box + col_w - 115, y0 + 112, 95, 95, fill="#eff6ff", stroke=ACCENT, sw=1.4, rx=6))
    p.append(text(x_box + col_w - 68, y0 + 152, "QR-код", size=11, bold=True, color=ACCENT))
    p.append(text(x_box + col_w - 68, y0 + 168, "онбордингу", size=9.5, bold=True, color=ACCENT))
    p.append(text(x_box + col_w - 68, y0 + 184, "та зв'язки", size=9.5, color="#1e40af"))

    # Складська інформація та зв'язка з заводом
    p.append(line(x_box + 15, y0 + 232, x_box + col_w - 15, y0 + 232, color="#cbd5e1", sw=1.0))
    p.append(text(x_box + 18, y0 + 252, "Batch / Lot: 2026-W34   |   Date: 2026-08-25", size=9.5, color=TEXT_DARK, anchor="start"))
    p.append(text(x_box + 18, y0 + 270, "Factory Test ID: QA-PASS-884   |   Weight: 485 g", size=9.5, color=TEXT_DARK, anchor="start"))
    p.append(text(x_box + 18, y0 + 288, "Provisioning Hash: a4f8...9b12 (Signed Ed25519)", size=9.5, color="#64748b", anchor="start"))

    # Індикатори та попередження
    p.append(rect(x_box + 18, y0 + 304, col_w - 36, 42, fill="#fffbeb", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(x_box + 26, y0 + 320, "ВАЖЛИВО: S/N та MAC на коробці мусять строго збігатися", size=9.5, bold=True, color="#b45309", anchor="start"))
    p.append(text(x_box + 26, y0 + 336, "із внутрішнім шильдиком та OTP пам'яттю мікроконтролера", size=9.5, color="#92400e", anchor="start"))

    render(os.path.join(OUT, "device-and-box-labels.svg"), W, H, *p)


# ── 3. quickstart-flow-architecture.svg ────────────────────────────────────
# Покроковий сценарій Quick Start Guide: 5 кроків від коробки до телеметрії
def fig_quickstart_flow_architecture():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 26, "Архітектура 5-хвилинного сценарію швидкого старту (Quick Start Flow)", size=15, bold=True))

    steps = [
        ("1. Звірка комплекту", ACCENT, ACCENT_BG, [
            "• Візуальна перевірка",
            "• Наявність антени",
            "• Звірка клемника",
            "• Маркери S/N у щит"
        ]),
        ("2. Монтаж і дроти", WARN, WARN_BG, [
            "• Антена ДО струму!",
            "• Полярність (Vin/GND)",
            "• Заземлити контакт",
            "• Монтаж на DIN-рейку"
        ]),
        ("3. Подача струму", PURPLE, PURPLE_BG, [
            "• Діод POWER (зелений)",
            "• Тест STATUS (миготіння)",
            "• Завантаження: <10 с",
            "• Червоний = поламка"
        ]),
        ("4. Перший контакт", FIELD, "#f0fdf4", [
            "• Точка Captive Portal",
            "• BLE-пошук у додатку",
            "• Дефолт: 192.168.1.1",
            "• Зміна пароля доступу"
        ]),
        ("5. Хмара / Робота", SUCCESS, SUCCESS_BG, [
            "• Сканування QR-коду",
            "• Реєстрація у брокері",
            "• Телеметрія (Ping)",
            "• Повна веб-довідка"
        ])
    ]

    card_w = 154
    card_h = 240
    gap = 18
    x0 = 25
    y0 = 65

    for i, (title, stroke_c, fill_c, lines) in enumerate(steps):
        cx = x0 + i * (card_w + gap)
        p.append(rect(cx, y0, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(rect(cx, y0, card_w, 32, fill=stroke_c, stroke=stroke_c, sw=1.0, rx=6))
        p.append(text(cx + card_w / 2, y0 + 21, title, size=10.5, bold=True, color="#ffffff"))

        ly = y0 + 58
        for ln in lines:
            p.append(text(cx + 10, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 26

        # Стрілка між кроками
        if i < len(steps) - 1:
            arr_x1 = cx + card_w + 2
            arr_x2 = cx + card_w + gap - 2
            arr_y = y0 + card_h / 2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color="#94a3b8", sw=1.6))

    # Нижній аналітичний блок: Чому QSG замінює повний мануал у перші 5 хвилин
    y_bot = 325
    p.append(rect(25, y_bot, 830, 75, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    p.append(text(45, y_bot + 22, "Головний принцип Quick Start Guide: мінімізація часу до «першого подиху» пристрою (Time to First Blink)", size=10.5, bold=True, color=ACCENT, anchor="start"))
    p.append(text(45, y_bot + 42, "• Жодних складних таблиць конфігурацій регістрів у друкованому буклеті — лише критичний шлях увімкнення та техніка безпеки.", size=9.5, color=TEXT_DARK, anchor="start"))
    p.append(text(45, y_bot + 60, "• Усі глибокі протоколи, REST/MQTT API, схеми оновлення та виправлення несправностей — за динамічним QR-посиланням на живу веб-базу.", size=9.5, color="#475569", anchor="start"))

    render(os.path.join(OUT, "quickstart-flow-architecture.svg"), W, H, *p)


if __name__ == "__main__":
    fig_box_layers_and_kit()
    fig_device_and_box_labels()
    fig_quickstart_flow_architecture()
    print("All 3 figures generated successfully in", OUT)
