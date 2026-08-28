# -*- coding: utf-8 -*-
"""Фігури до теми «Технічне завдання на власний пристрій».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── 1. Ієрархія розділів апаратного ТЗ ──────────────────────────────────────────
def fig_spec_hierarchy():
    W, H = 820, 420
    f = [text(W / 2, 28, "Ієрархія розділів апаратного ТЗ (HRS)", size=16, bold=True)]

    layers = [
        ("4. Обчислювач і пам'ять", "Архітектура MCU (Arm/RISC-V), FPU, Flash/SRAM, таймінги реакції ISR", POS, 60),
        ("3. Інтерфейси та сенсори", "Аналогові/дискретні I/O, шини I2C/SPI/UART/CAN/RS-485, BLE/Wi-Fi/LoRa", "#e67e22", 130),
        ("2. Живлення, EMC та захисти", "Діапазон Vin, Power Budget, захист від переполюсовки, ESD/Surge, EMI", NEG, 200),
        ("1. Експлуатаційні обмеження", "Температура (-40..+85 °C), IP-захист корпусу, вологість, вібростійкість", FIELD, 270),
    ]

    for title, desc, col, y in layers:
        f.append(rect(60, y, 700, 54, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        f.append(rect(60, y, 220, 54, fill=col, stroke=col, sw=1.8, rx=6))
        f.append(text(170, y + 32, title, size=13, color="#ffffff", bold=True))
        f.append(text(480, y + 32, desc, size=11, color=INK))

    f.append(arrow(35, 310, 35, 75, color=LINE, sw=2))
    f.append(text(35, 345, "Фундамент", size=10, color=FIELD, bold=True))
    f.append(text(35, 50, "Вершина", size=10, color=POS, bold=True))

    f.append(fitbox(60, 345, 700, 50,
                    "Правило спадкоємності: експлуатація й живлення звужують вибір компонентів до вузького\nпереліку, після чого обираються захищені інтерфейси та оптимальний мікроконтролер.",
                    size=11, fill="#f8fafc", stroke=MUTED, sw=1))

    render(os.path.join(IMG, "spec-hierarchy-pyramid.svg"), W, H, *f)


# ── 2. Профіль струму та часовий розподіл фаз (Power Budget) ──────────────────
def fig_power_budget():
    W, H = 840, 440
    f = [text(W / 2, 28, "Профіль споживання енергії автономного пристрою", size=16, bold=True)]

    ox, oy = 80, 240
    f.append(line(ox, oy, ox + 680, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, 60, color=LINE, sw=1.5))
    f.append(text(ox - 10, 65, "I (мА)", size=11, color=INK, anchor="end", bold=True))
    f.append(text(ox + 695, oy + 4, "t (час)", size=11, color=INK, anchor="start", bold=True))

    # 1. Сон
    f.append(line(ox, oy - 2, ox + 200, oy - 2, color=NEG, sw=2.5))
    f.append(text(ox + 100, oy + 20, "Глибокий сон (Deep Sleep)\nI = 15 мкА, T = 58.85 с", size=10, color=NEG))

    # 2. Сенсори та обчислення
    f.append(line(ox + 200, oy - 2, ox + 200, oy - 45, color="#e67e22", sw=2))
    f.append(line(ox + 200, oy - 45, ox + 320, oy - 45, color="#e67e22", sw=2.5))
    f.append(line(ox + 320, oy - 45, ox + 320, oy - 2, color="#e67e22", sw=2))
    f.append(rect(ox + 200, oy - 45, 120, 43, fill="#fef5e7", stroke="none"))
    f.append(text(ox + 260, oy - 55, "Опитування сенсорів", size=10, color="#e67e22", bold=True))
    f.append(text(ox + 260, oy - 20, "15 мА, 100 мс", size=9.5, color="#e67e22"))

    # 3. Радіопередача
    f.append(line(ox + 320, oy - 2, ox + 320, oy - 150, color=POS, sw=2))
    f.append(line(ox + 320, oy - 150, ox + 420, oy - 150, color=POS, sw=2.5))
    f.append(line(ox + 420, oy - 150, ox + 420, oy - 2, color=POS, sw=2))
    f.append(rect(ox + 320, oy - 150, 100, 148, fill="#fdecea", stroke="none"))
    f.append(text(ox + 370, oy - 160, "TX Радіо (LoRa/BLE)", size=10, color=POS, bold=True))
    f.append(text(ox + 370, oy - 75, "120 мА\n50 мс", size=9.5, color=POS))

    # 4. Повернення в сон
    f.append(line(ox + 420, oy - 2, ox + 680, oy - 2, color=NEG, sw=2.5))
    f.append(text(ox + 550, oy + 20, "Наступний цикл сну...", size=10, color=NEG))

    # Пунктирна лінія середнього струму
    f.append(line(ox, oy - 12, ox + 680, oy - 12, color=FIELD, sw=1.8, dash="4 4"))
    f.append(text(ox + 695, oy - 12, "I_avg ≈ 132 мкА", size=10.5, color=FIELD, anchor="start", bold=True))

    # Розрахунковий підсумок
    f.append(rect(80, 280, 680, 130, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(420, 305, "Баланс споживання для батареї 1S LiSOCl2 (2600 мА·год, 3.6 В)", size=12, color=INK, bold=True))
    f.append(text(420, 332, "Середній струм:  I_avg = (120 мА · 0.05 с + 15 мА · 0.1 с + 0.015 мА · 58.85 с) / 60 с ≈ 0.132 мА", size=10.5, color=INK))
    f.append(text(420, 357, "З урахуванням 15% запасу ємності та 1.5% річного саморозряду: C_eff ≈ 2200 мА·год", size=10.5, color=MUTED))
    f.append(text(420, 385, "Розрахункова автономність: T = 2200 мА·год / (0.132 мА · 8760 год/рік) ≈ 1.90 року безперервної роботи", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "power-budget-breakdown.svg"), W, H, *f)


# ── 3. Зони захисту EMC / ESD ──────────────────────────────────────────────────
def fig_emc_esd_zones():
    W, H = 840, 380
    f = [text(W / 2, 26, "Ешелонований захист портів і ліній живлення (EMC / ESD)", size=16, bold=True)]

    f.append(rect(40, 55, 200, 240, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    f.append(text(140, 80, "Зовнішній порт", size=12, color=POS, bold=True))
    f.append(fitbox(55, 95, 170, 185,
                    "Джерела завад:\n• ESD (IEC 61000-4-2):\n  до ±15 кВ статики\n• Surge (IEC 61000-4-5):\n  до 2 кВ комутацій\n• Переполюсовка\n  (людський фактор)\n• Наведені шуми радіо",
                    size=10, fill="#ffffff", stroke=POS, sw=1))

    f.append(arrow(240, 175, 285, 175, color=LINE, sw=2))

    f.append(rect(290, 55, 260, 240, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    f.append(text(420, 80, "Рубіж захисту (Board Entry)", size=12, color="#ca8a04", bold=True))
    f.append(fitbox(305, 95, 230, 185,
                    "Компоненти захисту:\n1. Самоперезапускний PTC запобіжник\n2. MOV варистор / GDT розрядник\n3. Швидкі TVS-діоди (наносекунди)\n4. P-MOSFET від зворотної полярності\n5. Дросель синфазних завад (CMC)\n6. Гальванорозв'язка (ISO77xx)",
                    size=9.5, fill="#ffffff", stroke="#ca8a04", sw=1))

    f.append(arrow(550, 175, 595, 175, color=LINE, sw=2))

    f.append(rect(600, 55, 200, 240, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(700, 80, "Чутливе ядро", size=12, color=FIELD, bold=True))
    f.append(fitbox(615, 95, 170, 185,
                    "Захищена електроніка:\n• Стабілізатор (LDO/Buck)\n• Мікроконтролер (MCU)\n• Чутливі АЦП і сенсори\n• Flash-пам'ять\n• Радіотрансивер\n\nРівень завад: < 10 мВ",
                    size=10, fill="#ffffff", stroke=FIELD, sw=1))

    f.append(fitbox(40, 310, 760, 50,
                    "Принцип локалізації: жорсткі енергетичні завади гасяться на самому краю плати біля роз'єму,\nне маючи змоги проникнути в загальні полігони землі (GND) та внутрішні сигнальні траси.",
                    size=10.5, fill="#f8fafc", stroke=MUTED, sw=1))

    render(os.path.join(IMG, "emc-esd-zones.svg"), W, H, *f)


# ── 4. Компроміси складності (Feature Creep) ──────────────────────────────────
def fig_feature_creep():
    W, H = 840, 400
    f = [text(W / 2, 26, "Вплив надлишкових вимог (Feature Creep) на параметри проєкту", size=16, bold=True)]

    cols = [
        ("Базове ТЗ (Must Have)", "#2563eb", [
            ("Цільова функція", "Вимірювання t°/вологості + LoRa"),
            ("Площа PCB", "35 × 25 мм (2 шари)"),
            ("BOM вартість", "$6.80 за плату"),
            ("Струм сну", "12 мкА"),
            ("Термін розробки", "6 тижнів"),
            ("Ризик дефіциту", "Низький (4 ключові IC)"),
        ]),
        ("Роздуте ТЗ (+ Nice to Have)", POS, [
            ("Цільова функція", "+ OLED екран, RGB, Wi-Fi, IMU, SD-карта"),
            ("Площа PCB", "65 × 50 мм (4 шари)"),
            ("BOM вартість", "$18.40 за плату (+170%)"),
            ("Струм сну", "95 мкА (витоки з шин і IC)"),
            ("Термін розробки", "18 тижнів (+200%)"),
            ("Ризик дефіциту", "Високий (12 ключових IC)"),
        ])
    ]

    for idx, (title, color, rows) in enumerate(cols):
        x = 50 + idx * 380
        f.append(rect(x, 55, 360, 270, fill="#ffffff", stroke=color, sw=1.8, rx=6))
        f.append(rect(x, 55, 360, 36, fill=color, stroke=color, sw=1.8, rx=6))
        f.append(text(x + 180, 78, title, size=13, color="#ffffff", bold=True))

        for r_idx, (k, v) in enumerate(rows):
            ry = 105 + r_idx * 35
            f.append(text(x + 15, ry + 12, k + ":", size=10, color=MUTED, anchor="start", bold=True))
            f.append(text(x + 345, ry + 12, v, size=9.5, color=INK, anchor="end"))
            if r_idx < len(rows) - 1:
                f.append(line(x + 10, ry + 22, x + 350, ry + 22, color="#e5e7eb", sw=1))

    f.append(fitbox(50, 335, 740, 48,
                    "Золоте правило ТЗ: кожна другорядна функція подвоює простір можливих помилок і збільшує\nструми витоку в режимі сну. Опції «на майбутнє» мають відсікатися до стадії прототипування.",
                    size=10.5, fill="#f8fafc", stroke=MUTED, sw=1))

    render(os.path.join(IMG, "feature-creep-tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spec_hierarchy()
    fig_power_budget()
    fig_emc_esd_zones()
    fig_feature_creep()
    print("Всі фігури згенеровано успішно!")
