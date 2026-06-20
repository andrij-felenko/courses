# -*- coding: utf-8 -*-
"""Фігури об'єкта «LoRa-модуль» (catalog/connect/radio). Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині модуля — блок-схема ───────────────────────────────
# Модуль = трансивер (чип) + кварц + ланцюг узгодження + антена. MCU говорить
# із чипом по шині (SPI або UART), чип сам робить усю радіороботу.
def fig_block():
    W, H = 720, 360
    parts = []

    # MCU зліва
    mcu = fitbox(40, 150, 120, 70, "Ваш MCU\n(ESP32, STM32,\nAVR…)",
                 size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True)
    parts.append(mcu)

    # межа модуля — пунктирна рамка
    parts.append(rect(210, 60, 380, 240, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(400, 50, "модуль (одна плата)", 12, MUTED, "middle"))

    # чип-трансивер усередині
    chip = fitbox(240, 150, 150, 80, "Трансивер\nSX127x / SX126x\n(модем + PA + LNA)",
                  size=12, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True)
    parts.append(chip)

    # кварц
    parts.append(fitbox(250, 250, 120, 36, "кварц 32 МГц",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))
    parts.append(line(315, 230, 310, 250, color=MUTED, sw=1.2))

    # ланцюг узгодження
    matchx = 420
    parts.append(fitbox(matchx, 158, 90, 56, "ланцюг\nузгодження\n+ фільтр",
                        size=10, fill="#eef2f7", stroke=INK, sw=1.4, color=INK))
    parts.append(arrow(390, 186, matchx, 186, color=INK, sw=1.8))

    # антена (трикутник-символ праворуч за межею)
    ax = 640
    parts.append(arrow(matchx + 90, 186, ax - 20, 186, color=POS, sw=2.0))
    parts.append(line(ax, 120, ax, 200, color=POS, sw=2.4))
    parts.append(line(ax, 120, ax - 16, 100, color=POS, sw=2.4))
    parts.append(line(ax, 120, ax + 16, 100, color=POS, sw=2.4))
    parts.append(text(ax, 224, "антена", 12, POS, "middle", bold=True))

    # шина MCU↔чип (двобічна)
    parts.append(arrow(160, 178, 240, 178, color=NEG, sw=2.0))
    parts.append(arrow(240, 200, 160, 200, color=NEG, sw=2.0))
    parts.append(text(200, 168, "SPI або UART", 11, NEG, "middle", bold=True))
    parts.append(text(200, 224, "+ живлення 3.3 В", 10, MUTED, "middle"))

    render(os.path.join(IMG, "block.svg"), W, H, *parts,
           title="Що всередині LoRa-модуля: чип робить усю радіороботу")


# ── Фігура 2: типова розпіновка SPI-модуля (RFM95-подібний) ──────────────────
# Чотири лінії SPI + скидання + DIO0 (готовність). Зліва живлення/земля.
def fig_pinout():
    W, H = 700, 420
    parts = []
    # корпус модуля по центру
    bx, by, bw, bh = 290, 70, 120, 300
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(bx + bw / 2, by - 14, "LoRa-модуль (SPI)", 12, INK, "middle", bold=True))

    rows = [
        # (підпис ліворуч, колір, опис праворуч)
        ("3.3V", POS,  "живлення 3.3 В (не 5 В!)"),
        ("GND",  INK,  "спільна земля"),
        ("SCK",  NEG,  "такт SPI"),
        ("MOSI", NEG,  "дані в модуль"),
        ("MISO", NEG,  "дані з модуля"),
        ("NSS",  NEG,  "вибір кристала (CS)"),
        ("RST",  MUTED,"скидання чипа"),
        ("DIO0", FIELD,"переривання: «готово»"),
    ]
    n = len(rows)
    y0 = by + 26
    step = (bh - 44) / (n - 1)
    for i, (pin, col, desc) in enumerate(rows):
        y = y0 + i * step
        # вивід-лапка ліворуч
        parts.append(line(bx, y, bx - 18, y, color=col, sw=2.2))
        parts.append(circle(bx - 18, y, 3.5, fill=col, stroke=INK, sw=1))
        parts.append(text(bx + 8, y + 4, pin, 12, col, "start", bold=True))
        # опис праворуч
        parts.append(line(bx + bw, y, bx + bw + 18, y, color=MUTED, sw=1.2))
        parts.append(text(bx + bw + 24, y + 4, desc, 11, INK, "start"))

    # підказка про антену знизу
    parts.append(fitbox(bx - 200, by + bh + 8, 170, 40,
                        "ANT — вивід антени:\nзавжди підключений!",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    render(os.path.join(IMG, "pinout.svg"), W, H, *parts,
           title="Типова розпіновка SPI-модуля: 4 лінії шини + RST + DIO0")


# ── Фігура 3: підключення й живлення — пік струму на передачі ────────────────
# Головна пастка: на передачі модуль рве 100+ мА коротким піком; тонке живлення
# просідає → скидання MCU. Лікування: товстий конденсатор біля живлення модуля.
def fig_wiring():
    W, H = 720, 360
    parts = []
    # MCU/регулятор 3.3 В
    parts.append(fitbox(40, 140, 130, 70, "3.3 В\n(регулятор/MCU)",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
    # модуль
    parts.append(fitbox(470, 130, 160, 90, "LoRa-модуль\nпік TX ≈ 100–130 мА\n(коротко)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))
    # лінія живлення
    parts.append(line(170, 158, 470, 158, color=POS, sw=2.4))
    parts.append(text(320, 148, "+3.3 В", 11, POS, "middle", bold=True))
    # лінія землі
    parts.append(line(170, 200, 470, 200, color=INK, sw=2.0))
    parts.append(text(320, 214, "GND", 11, INK, "middle"))

    # конденсатор біля модуля (між + і GND)
    capx = 430
    parts.append(line(capx, 158, capx, 172, color=NEG, sw=2.0))
    parts.append(line(capx - 12, 172, capx + 12, 172, color=NEG, sw=2.6))  # верхня пластина
    parts.append(line(capx - 12, 180, capx + 12, 180, color=NEG, sw=2.6))  # нижня пластина
    parts.append(line(capx, 180, capx, 200, color=NEG, sw=2.0))
    parts.append(text(capx, 134, "C", 12, NEG, "middle", bold=True))

    parts.append(fitbox(330, 250, 290, 58,
                        "Лік: конденсатор 10–100 мкФ\nбіля живлення модуля тримає\n"
                        "напругу під час піку TX.",
                        size=12, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    # підпис-пастка
    parts.append(fitbox(40, 250, 270, 58,
                        "Пастка: тонке живлення / слабкий\nUSB → на піку TX напруга просідає,\n"
                        "модуль «зникає» або MCU скидається.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Живлення: пік струму на передачі — головна пастка")


fig_block()
fig_pinout()
fig_wiring()
print("Done. SVG in", IMG)
