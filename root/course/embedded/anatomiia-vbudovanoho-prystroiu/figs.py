# -*- coding: utf-8 -*-
"""Фігури для статті «Анатомія вбудованого пристрою» (anatomiia-vbudovanoho-prystroiu).
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Додаткові кольори для чіткого візуального кодування підсистем
PWR_COLOR = "#b91c1c"   # червоний / живлення
CORE_COLOR = "#1d4ed8"  # синій / обчислення
BUS_COLOR = "#047857"   # зелений / зв'язок
PHYS_COLOR = "#d97706"  # бурштиновий / фізичний світ
CARD_BG = "#ffffff"


def fig_four_pillars():
    """1. four-pillars.svg — Чотири стовпи апаратної архітектури."""
    W, H = 840, 520
    parts = []

    # Загальний фон і рамка системи
    parts.append(rect(15, 15, W - 30, H - 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 40, "Апаратна архітектура вбудованої системи", size=16, color=INK, bold=True))

    # 1. Підсистема живлення (зліва вгорі)
    bx, by, bw, bh = 35, 65, 365, 200
    parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke=PWR_COLOR, sw=2, rx=8))
    parts.append(rect(bx, by, bw, 32, fill="#fee2e2", stroke=PWR_COLOR, sw=1.5, rx=8))
    parts.append(text(bx + bw / 2, by + 21, "1. Підсистема живлення (Power)", size=13, color=PWR_COLOR, bold=True))

    pwr_items = [
        "• Джерела: Мережа AC/DC, Li-Ion, LiFePO4, Батарея",
        "• Перетворення: Імпульсні DC-DC (ККД 85-95%) та LDO",
        "• Захист: TVS-діоди від ESD, захист від переполюсовки",
        "• Розв'язка: Декаплінг 100 нФ + 10 мкФ біля VDD"
    ]
    for i, itm in enumerate(pwr_items):
        parts.append(text(bx + 15, by + 58 + i * 36, itm, size=11, color=INK, anchor="start"))

    # 2. Обчислювальне ядро (справа вгорі)
    bx, by, bw, bh = 440, 65, 365, 200
    parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke=CORE_COLOR, sw=2, rx=8))
    parts.append(rect(bx, by, bw, 32, fill="#dbeafe", stroke=CORE_COLOR, sw=1.5, rx=8))
    parts.append(text(bx + bw / 2, by + 21, "2. Обчислювальне ядро (Compute)", size=13, color=CORE_COLOR, bold=True))

    core_items = [
        "• Процесор: Ядро MCU (Cortex-M, RISC-V, AVR) або SoC",
        "• Пам'ять: Вбудована Flash (код) + швидка SRAM (дані)",
        "• Тактування: Кварцовий резонатор (HSE), RC, PLL",
        "• Надійність: Сторожовий таймер (WDT), скидання (BOD)"
    ]
    for i, itm in enumerate(core_items):
        parts.append(text(bx + 15, by + 58 + i * 36, itm, size=11, color=INK, anchor="start"))

    # 3. Периферія та інтерфейси зв'язку (зліва внизу)
    bx, by, bw, bh = 35, 285, 365, 200
    parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke=BUS_COLOR, sw=2, rx=8))
    parts.append(rect(bx, by, bw, 32, fill="#d1fae5", stroke=BUS_COLOR, sw=1.5, rx=8))
    parts.append(text(bx + bw / 2, by + 21, "3. Периферія та інтерфейси (Interconnect)", size=13, color=BUS_COLOR, bold=True))

    bus_items = [
        "• Базовий ввід/вивід: GPIO (Push-Pull, Open-Drain)",
        "• Платові шини: I2C (адресна, 2 дроти), SPI (швидка), UART",
        "• Промислові мережі: CAN-bus, RS-485, USB",
        "• Радіозв'язок: BLE, Wi-Fi, LoRa Sub-1GHz, Zigbee"
    ]
    for i, itm in enumerate(bus_items):
        parts.append(text(bx + 15, by + 58 + i * 36, itm, size=11, color=INK, anchor="start"))

    # 4. Взаємодія з фізичним світом (справа внизу)
    bx, by, bw, bh = 440, 285, 365, 200
    parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke=PHYS_COLOR, sw=2, rx=8))
    parts.append(rect(bx, by, bw, 32, fill="#fef3c7", stroke=PHYS_COLOR, sw=1.5, rx=8))
    parts.append(text(bx + bw / 2, by + 21, "4. Фізичний світ (Sensors & Actuators)", size=13, color=PHYS_COLOR, bold=True))

    phys_items = [
        "• Сенсори: Аналогові й цифрові МЕМС (тиск, темп., IMU)",
        "• Кондиціювання: Підсилювачі (Op-Amp), фільтри (AAF), АЦП",
        "• Актуатори: Двигуни (DC, BLDC, Stepper), реле, нагрів",
        "• Силові драйвери: MOSFET-ключі, H-мости, оптопари"
    ]
    for i, itm in enumerate(phys_items):
        parts.append(text(bx + 15, by + 58 + i * 36, itm, size=11, color=INK, anchor="start"))

    # Центральний зв'язок (хрестовина / взаємодія)
    parts.append(line(217, 265, 217, 285, color="#64748b", sw=2, dash="3,3"))
    parts.append(line(622, 265, 622, 285, color="#64748b", sw=2, dash="3,3"))
    parts.append(line(400, 165, 440, 165, color="#64748b", sw=2, dash="3,3"))
    parts.append(line(400, 385, 440, 385, color="#64748b", sw=2, dash="3,3"))

    return render(out("four-pillars.svg"), W, H, "".join(parts))


def fig_signal_lifecycle():
    """2. signal-lifecycle.svg — Життєвий цикл сигналу: від сенсора до актуатора."""
    W, H = 860, 380
    parts = []

    # Тіло діаграми
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Наскрізний потік даних та енергії: замкнений контур керування", size=15, color=INK, bold=True))

    # Блоки ланцюга
    blocks = [
        {"x": 30, "y": 70, "w": 105, "h": 120, "title": "Фізичне\nявище", "sub": "T, P, кут,\nструм, оберти", "bg": "#fef3c7", "bc": PHYS_COLOR},
        {"x": 165, "y": 70, "w": 115, "h": 120, "title": "Первинний\nсенсор", "sub": "Термопара,\nМЕМС, тензо", "bg": "#ffffff", "bc": "#d97706"},
        {"x": 310, "y": 70, "w": 125, "h": 120, "title": "Фільтр та\nАЦП (ADC)", "sub": "ОУ, anti-aliasing,\nдискретизація", "bg": "#ffffff", "bc": "#0284c7"},
        {"x": 465, "y": 60, "w": 140, "h": 140, "title": "Обчислення в МК", "sub": "Цифрова фільтрація\nРозрахунок помилки\nПІД-регулятор / FSM", "bg": "#dbeafe", "bc": CORE_COLOR},
        {"x": 635, "y": 70, "w": 125, "h": 120, "title": "ШІМ / ЦАП та\nДрайвер", "sub": "MOSFET-ключ,\nH-міст, оптопара", "bg": "#ffffff", "bc": "#dc2626"},
        {"x": 785, "y": 70, "w": 60, "h": 120, "title": "Актуа-\nтор", "sub": "Мотор,\nнагрів", "bg": "#fee2e2", "bc": PWR_COLOR},
    ]

    for b in blocks:
        parts.append(rect(b["x"], b["y"], b["w"], b["h"], fill=b["bg"], stroke=b["bc"], sw=1.8, rx=6))
        lines_t = b["title"].split("\n")
        for idx, lt in enumerate(lines_t):
            parts.append(text(b["x"] + b["w"] / 2, b["y"] + 24 + idx * 16, lt, size=12, color=INK, bold=True))
        lines_s = b["sub"].split("\n")
        for idx, ls in enumerate(lines_s):
            parts.append(text(b["x"] + b["w"] / 2, b["y"] + 68 + idx * 15, ls, size=10, color=MUTED))

    # Стрілки прямого шляху
    parts.append(arrow(135, 130, 165, 130, color=LINE, sw=1.8))
    parts.append(arrow(280, 130, 310, 130, color=LINE, sw=1.8))
    parts.append(arrow(435, 130, 465, 130, color=LINE, sw=1.8))
    parts.append(arrow(605, 130, 635, 130, color=LINE, sw=1.8))
    parts.append(arrow(760, 130, 785, 130, color=LINE, sw=1.8))

    # Текстові позначки над стрілками
    parts.append(text(150, 118, "сигнал", size=9, color=MUTED))
    parts.append(text(295, 118, "V(t)", size=9, color=MUTED))
    parts.append(text(450, 118, "код N", size=9, color=MUTED))
    parts.append(text(620, 118, "ШІМ", size=9, color=MUTED))
    parts.append(text(772, 118, "I, U", size=9, color=MUTED))

    # Зворотний зв'язок (нижня дуга)
    parts.append(line(815, 190, 815, 280, color=PHYS_COLOR, sw=2))
    parts.append(line(815, 280, 82, 280, color=PHYS_COLOR, sw=2))
    parts.append(arrow(82, 280, 82, 190, color=PHYS_COLOR, sw=2))

    parts.append(rect(330, 260, 240, 40, fill="#fffbeb", stroke=PHYS_COLOR, sw=1.5, rx=6))
    parts.append(text(450, 277, "Фізичний зворотний зв'язок", size=11, color=PHYS_COLOR, bold=True))
    parts.append(text(450, 292, "Зміна температури, швидкості, тиску", size=10, color=MUTED))

    # Блок опорної напруги та живлення
    parts.append(rect(270, 325, 360, 35, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(450, 347, "Інфраструктурна опора: стабільне живлення VDD та VREF", size=11, color=INK, bold=True))

    return render(out("signal-lifecycle.svg"), W, H, "".join(parts))


def fig_pcb_anatomy():
    """3. pcb-anatomy.svg — Анатомія друкованої плати та блокувальних конденсаторів."""
    W, H = 840, 440
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Фізична анатомія друкованої плати: стек шарів та декаплінг", size=15, color=INK, bold=True))

    # Ліва частина: Поперечний зріз 4-шарової друкованої плати (Stackup)
    lx, ly, lw, lh = 30, 60, 360, 350
    parts.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(lx + lw / 2, ly + 25, "Стек шарів 4-шарової PCB", size=13, color=INK, bold=True))

    # Шари
    layers = [
        {"name": "Топ-шар (Top Signal / Components)", "color": "#dc2626", "y": ly + 55, "h": 18},
        {"name": "Препрег / Діелектрик (FR-4)", "color": "#ca8a04", "y": ly + 73, "h": 40},
        {"name": "Внутрішній шар 1: Земля (GND Plane)", "color": "#2563eb", "y": ly + 113, "h": 18},
        {"name": "Сердечник (FR-4 Core)", "color": "#ca8a04", "y": ly + 131, "h": 75},
        {"name": "Внутрішній шар 2: Живлення (Power Plane)", "color": "#ea580c", "y": ly + 206, "h": 18},
        {"name": "Препрег / Діелектрик (FR-4)", "color": "#ca8a04", "y": ly + 224, "h": 40},
        {"name": "Нижній шар (Bottom Signal)", "color": "#dc2626", "y": ly + 264, "h": 18},
    ]

    for l_info in layers:
        parts.append(rect(lx + 20, l_info["y"], lw - 40, l_info["h"], fill=l_info["color"], stroke="#475569", sw=1, rx=2))
        parts.append(text(lx + 25, l_info["y"] + l_info["h"] / 2 + 4, l_info["name"], size=10, color="#ffffff" if l_info["color"] != "#ca8a04" else "#000000", anchor="start", bold=True))

    # Пояснення до лівої частини
    parts.append(text(lx + lw / 2, ly + 310, "Суцільний полігон GND екранує сигнали", size=10, color=MUTED))
    parts.append(text(lx + lw / 2, ly + 328, "і забезпечує мінімальну площу петлі струму", size=10, color=MUTED))

    # Права частина: Чому необхідний декаплінг (проблема індуктивності доріжки)
    rx_c, ry_c, rw, rh = 415, 60, 395, 350
    parts.append(rect(rx_c, ry_c, rw, rh, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(rx_c + rw / 2, ry_c + 25, "Паразитна індуктивність і декаплінг", size=13, color=INK, bold=True))

    # Блок джерела живлення
    parts.append(rect(rx_c + 20, ry_c + 60, 80, 50, fill="#fee2e2", stroke=PWR_COLOR, sw=1.5, rx=4))
    parts.append(text(rx_c + 60, ry_c + 85, "LDO / DCDC\n3.3 В", size=10, color=PWR_COLOR, bold=True))

    # Індуктивність доріжки (довгий провідник)
    parts.append(line(rx_c + 100, ry_c + 85, rx_c + 155, ry_c + 85, color=LINE, sw=2))
    # Малюнок котушки індуктивності L_trace
    parts.append(rect(rx_c + 155, ry_c + 75, 55, 20, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    parts.append(text(rx_c + 182, ry_c + 89, "L_trace", size=10, color="#9a3412", bold=True))
    parts.append(line(rx_c + 210, ry_c + 85, rx_c + 270, ry_c + 85, color=LINE, sw=2))

    # Декаплінг-конденсатор C_dec (100 нФ)
    parts.append(rect(rx_c + 245, ry_c + 120, 50, 45, fill="#dbeafe", stroke=CORE_COLOR, sw=1.5, rx=4))
    parts.append(text(rx_c + 270, ry_c + 140, "100 нФ\nMLCC", size=9, color=CORE_COLOR, bold=True))
    parts.append(line(rx_c + 270, ry_c + 85, rx_c + 270, ry_c + 120, color=LINE, sw=2))
    parts.append(line(rx_c + 270, ry_c + 165, rx_c + 270, ry_c + 195, color=LINE, sw=2))

    # Мікроконтролер (MCU)
    parts.append(rect(rx_c + 305, ry_c + 60, 75, 150, fill="#f1f5f9", stroke=CORE_COLOR, sw=2, rx=6))
    parts.append(text(rx_c + 342, ry_c + 95, "MCU", size=13, color=CORE_COLOR, bold=True))
    parts.append(text(rx_c + 342, ry_c + 115, "VDD", size=10, color=POS, bold=True))
    parts.append(text(rx_c + 342, ry_c + 185, "GND", size=10, color=NEG, bold=True))
    parts.append(line(rx_c + 270, ry_c + 85, rx_c + 305, ry_c + 85, color=LINE, sw=2))

    # Земляна лінія
    parts.append(line(rx_c + 60, ry_c + 195, rx_c + 305, ry_c + 195, color="#2563eb", sw=2.5))
    parts.append(text(rx_c + 160, ry_c + 210, "Суцільний полігон GND (низький Z)", size=10, color="#2563eb", bold=True))

    # Пояснювальний текст формули
    parts.append(rect(rx_c + 15, ry_c + 230, rw - 30, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    parts.append(text(rx_c + rw / 2, ry_c + 252, "Чому виникає просадка напруги:", size=11, color=INK, bold=True))
    parts.append(text(rx_c + rw / 2, ry_c + 272, "ΔV = L_trace · (di / dt)", size=12, color=POS, bold=True))
    parts.append(text(rx_c + rw / 2, ry_c + 294, "При перемиканні за 1 нс струм росте на 100 мА.", size=10, color=MUTED))
    parts.append(text(rx_c + rw / 2, ry_c + 312, "Конденсатор 100 нФ впритул до VDD миттєво віддає заряд.", size=10, color=FIELD, bold=True))

    return render(out("pcb-anatomy.svg"), W, H, "".join(parts))


def fig_power_profile():
    """4. power-profile.svg — Профіль споживання енергії автономного пристрою."""
    W, H = 840, 420
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Профіль енергоспоживання пристрою з живленням від батареї", size=15, color=INK, bold=True))

    # Вісь часу та струму
    ox, oy = 80, 330
    gw, gh = 710, 240

    # Сітка та осі
    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))  # вісь X
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))  # вісь Y

    # Підписи осей
    parts.append(text(ox + gw - 15, oy + 25, "Час t (мс / с)", size=11, color=INK, bold=True))
    parts.append(text(ox - 35, oy - gh + 15, "Струм I", size=11, color=INK, bold=True))

    # Рівні струму на осі Y
    levels = [
        {"y": oy - 15, "label": "2 мкА (Deep Sleep)"},
        {"y": oy - 90, "label": "5 мА (Пробудження & АЦП)"},
        {"y": oy - 150, "label": "15 мА (Обчислення MCU)"},
        {"y": oy - 220, "label": "80 мА (Передача RF / Wi-Fi)"}
    ]
    for lvl in levels:
        parts.append(line(ox - 5, lvl["y"], ox + gw, lvl["y"], color="#e2e8f0", sw=1, dash="4,4"))
        parts.append(text(ox - 8, lvl["y"] + 4, lvl["label"], size=9, color=MUTED, anchor="end"))

    # Графік струму (полігон)
    curve_pts = [
        (ox, oy - 15),
        (ox + 120, oy - 15),
        (ox + 125, oy - 90),
        (ox + 220, oy - 90),
        (ox + 225, oy - 150),
        (ox + 330, oy - 150),
        (ox + 335, oy - 220),
        (ox + 450, oy - 220),
        (ox + 455, oy - 15),
        (ox + gw, oy - 15)
    ]

    # Створюємо шлях
    poly_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in curve_pts)
    poly_fill_d = poly_d + f" L {ox + gw:.1f},{oy:.1f} L {ox:.1f},{oy:.1f} Z"

    parts.append(f'<path d="{poly_fill_d}" fill="#fee2e2" opacity="0.6"/>')
    parts.append(f'<path d="{poly_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначення фаз роботи
    phases = [
        {"x": ox + 60, "y": oy - 35, "t": "Deep Sleep (99.8% часу)", "c": MUTED},
        {"x": ox + 172, "y": oy - 110, "t": "Сенсор (2 мс)", "c": "#0369a1"},
        {"x": ox + 277, "y": oy - 170, "t": "Обробка (3 мс)", "c": CORE_COLOR},
        {"x": ox + 392, "y": oy - 235, "t": "Радіосплеск (10 мс)", "c": POS},
        {"x": ox + 570, "y": oy - 35, "t": "Deep Sleep (очікування наступного циклу)", "c": MUTED},
    ]

    for ph in phases:
        parts.append(text(ph["x"], ph["y"], ph["t"], size=10, color=ph["c"], bold=True))

    # Пояснювальний підсумок
    parts.append(rect(ox + 50, oy + 38, gw - 100, 32, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=6))
    parts.append(text(ox + gw / 2, oy + 58, "Середній струм I_avg = (I_актив · t_актив + I_сон · t_сон) / T_період ≈ одиниці мікроампер → роки від батарейки", size=11, color=INK, bold=True))

    return render(out("power-profile.svg"), W, H, "".join(parts))


def main():
    fig_four_pillars()
    fig_signal_lifecycle()
    fig_pcb_anatomy()
    fig_power_profile()
    print("Всі 4 фігури згенеровано успішно в img/")


if __name__ == "__main__":
    main()
