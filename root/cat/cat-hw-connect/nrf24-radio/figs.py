# -*- coding: utf-8 -*-
"""Фігури обʼєкта «Радіомодуль nRF24» (catalog/connect/radio). Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині модуля ────────────────────────────────────────────
# nRF24 = трансивер-чип (з апаратним протоколом ShockBurst усередині) + кварц
# + ланцюг узгодження + антена. MCU говорить по SPI + CE. Ключова відмінність
# від «сирого» радіо: чип сам збирає пакет, шле авто-ACK і перепитує.
def fig_block():
    W, H = 760, 400
    parts = []

    # MCU зліва
    parts.append(fitbox(30, 165, 120, 74, "Ваш MCU\n(ESP32, STM32,\nAVR…)",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))

    # межа модуля — пунктирна рамка
    parts.append(rect(210, 70, 420, 270, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(420, 58, "модуль (одна плата)", 12, MUTED, "middle"))

    # чип-трансивер усередині — окремо виділяємо апаратний протокол
    parts.append(fitbox(240, 130, 180, 96,
                        "Трансивер nRF24L01+\nмодем GFSK 2.4 ГГц\n+ PA · LNA\n"
                        "+ Enhanced ShockBurst\n(пакет · авто-ACK у залізі)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # кварц
    parts.append(fitbox(250, 262, 130, 40, "кварц 16 МГц",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))
    parts.append(line(320, 226, 315, 262, color=MUTED, sw=1.2))

    # ланцюг узгодження
    matchx = 448
    parts.append(fitbox(matchx, 150, 96, 56, "ланцюг\nузгодження\n+ фільтр",
                        size=10, fill="#eef2f7", stroke=INK, sw=1.4, color=INK))
    parts.append(arrow(420, 178, matchx, 178, color=INK, sw=1.8))

    # антена (символ праворуч за межею)
    ax = 690
    parts.append(arrow(matchx + 96, 178, ax - 22, 178, color=POS, sw=2.0))
    parts.append(line(ax, 118, ax, 200, color=POS, sw=2.4))
    parts.append(line(ax, 118, ax - 16, 96, color=POS, sw=2.4))
    parts.append(line(ax, 118, ax + 16, 96, color=POS, sw=2.4))
    parts.append(text(ax, 224, "антена 2.4 ГГц", 11, POS, "middle", bold=True))

    # шина MCU↔чип (двобічна SPI) + окрема лінія CE
    parts.append(arrow(150, 150, 240, 150, color=NEG, sw=2.0))
    parts.append(arrow(240, 172, 150, 172, color=NEG, sw=2.0))
    parts.append(text(195, 140, "SPI", 11, NEG, "middle", bold=True))
    parts.append(arrow(150, 200, 240, 200, color="#8e44ad", sw=2.0))
    parts.append(text(195, 216, "CE", 11, "#8e44ad", "middle", bold=True))
    parts.append(text(90, 250, "+ живлення 3.3 В", 10, MUTED, "middle"))

    render(os.path.join(IMG, "block.svg"), W, H, *parts,
           title="Що всередині nRF24: чип сам збирає пакет і підтверджує прийом")


# ── Фігура 2: фізична розводка 2×4-гребінця ──────────────────────────────────
# Головна пастка новачка — гребінець стоїть парами (2 ряди), а не в рядок.
# Ліва колонка: GND CE SCK MISO; права: VCC CSN MOSI IRQ.
def fig_pinout():
    W, H = 760, 470
    parts = []

    # корпус модуля
    bx, by, bw, bh = 300, 150, 160, 250
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(bx + bw / 2, by - 60, "nRF24L01+ — вигляд зверху", 13, INK, "middle", bold=True))
    parts.append(text(bx + bw / 2, by - 40, "(гребінець 2×4 — ДВА ряди, не в рядок)", 11, MUTED, "middle"))
    # позначка антени вгорі корпусу
    parts.append(fitbox(bx + 20, by + 8, bw - 40, 28, "антена / чип",
                        size=10, fill="#fdecea", stroke=POS, sw=1.0, color=INK))

    left = [  # (пін, колір, опис ліворуч)
        ("GND",  INK,   "земля"),
        ("CE",   "#8e44ad", "увімкнути радіо (RX/TX)"),
        ("SCK",  NEG,   "такт SPI"),
        ("MISO", NEG,   "дані з модуля"),
    ]
    right = [  # (пін, колір, опис праворуч)
        ("VCC",  POS,   "3.3 В (НЕ 5 В!)"),
        ("CSN",  NEG,   "вибір кристала (CS)"),
        ("MOSI", NEG,   "дані в модуль"),
        ("IRQ",  FIELD, "переривання «подія»"),
    ]

    n = 4
    y0 = by + 70
    step = (bh - 90) / (n - 1)
    lx = bx + 34          # ліва колонка контактів (усередині корпусу)
    rx = bx + bw - 34     # права колонка
    for i in range(n):
        y = y0 + i * step
        # ліва пара
        pin, col, desc = left[i]
        parts.append(circle(lx, y, 6, fill=col, stroke=INK, sw=1.2))
        parts.append(text(lx, y + 4, str(i * 2 + 1), 9, BG, "middle", bold=True))
        parts.append(line(lx, y, bx - 22, y, color=col, sw=2.0))
        parts.append(text(bx - 30, y + 4, pin, 12, col, "end", bold=True))
        parts.append(text(bx - 30, y + 19, desc, 10, MUTED, "end"))
        # права пара
        pin, col, desc = right[i]
        parts.append(circle(rx, y, 6, fill=col, stroke=INK, sw=1.2))
        parts.append(text(rx, y + 4, str(i * 2 + 2), 9, BG, "middle", bold=True))
        parts.append(line(rx, y, bx + bw + 22, y, color=col, sw=2.0))
        parts.append(text(bx + bw + 30, y + 4, pin, 12, col, "start", bold=True))
        parts.append(text(bx + bw + 30, y + 19, desc, 10, MUTED, "start"))

    render(os.path.join(IMG, "pinout.svg"), W, H, *parts,
           title="Розводка nRF24: 8 виводів двома рядами по 4")


# ── Фігура 3: підключення пін-у-пін + пастка живлення ────────────────────────
# SPI один-в-один; CE й CSN — на вільні GPIO. Головна пастка: пік струму на TX
# (PA+LNA до ~115 мА) просаджує тонке живлення → лік: конденсатор біля VCC.
def fig_wiring():
    W, H = 780, 430
    parts = []

    # MCU / регулятор 3.3 В зліва
    parts.append(fitbox(30, 90, 150, 210, "MCU 3.3 В\n\n3V3 →\nGND →\nSCK →\nMOSI →\nMISO →\n"
                        "GPIO → (CSN)\nGPIO → (CE)",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))

    # модуль справа
    parts.append(fitbox(560, 90, 190, 210, "nRF24-модуль\n\nVCC\nGND\nSCK\nMOSI\nMISO\n"
                        "CSN\nCE",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # сім ліній звʼязку — рівномірно, підписані рівнями по центру
    rows = [
        ("3V3 → VCC", POS),
        ("GND → GND", INK),
        ("SCK → SCK", NEG),
        ("MOSI → MOSI", NEG),
        ("MISO → MISO", NEG),
        ("GPIO → CSN", "#8e44ad"),
        ("GPIO → CE", "#8e44ad"),
    ]
    y0, dy = 128, 26
    for i, (lbl, col) in enumerate(rows):
        y = y0 + i * dy
        parts.append(line(180, y, 560, y, color=col, sw=1.8))
        parts.append(text(370, y - 5, lbl, 10, col, "middle", bold=True))

    # конденсатор біля VCC модуля (між VCC-лінією й GND-лінією)
    capx = 520
    yv, yg = 128, 154
    parts.append(line(capx, yv, capx, yv + 8, color="#c0392b", sw=1.8))
    parts.append(line(capx - 11, yv + 8, capx + 11, yv + 8, color="#c0392b", sw=2.6))
    parts.append(line(capx - 11, yv + 15, capx + 11, yv + 15, color="#c0392b", sw=2.6))
    parts.append(line(capx, yv + 15, capx, yg, color="#c0392b", sw=1.8))
    parts.append(text(capx + 26, yv + 4, "C 10 мкФ", 10, "#c0392b", "start", bold=True))

    # пастка / лік знизу двома рамками
    parts.append(fitbox(30, 330, 350, 78,
                        "Пастка: у момент передачі PA+LNA-версія\nрве до ~115 мА коротким піком. Тонке\n"
                        "живлення просідає → модуль «зникає»\nабо MCU скидається.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    parts.append(fitbox(400, 330, 350, 78,
                        "Лік: конденсатор 10 мкФ (а біля PA+LNA —\n100–220 мкФ) прямо на VCC/GND модуля\n"
                        "тримає напругу під час піку.\nЖивити від чистого 3.3 В.",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Підключення пін-у-пін: SPI + CE/CSN, і конденсатор на живленні")


# ── Фігура 4: дві версії — гола vs PA+LNA ────────────────────────────────────
# Гола плата з PCB-антеною: десятки метрів, ~12 мА. PA+LNA з підсилювачем і
# SMA-антеною: сотні метрів — кілометр, до ~115 мА пік. Виводи однакові.
def fig_variants():
    W, H = 780, 350
    parts = []

    # ── ліва: гола ──
    parts.append(rect(40, 70, 300, 230, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(190, 60, "Гола плата (PCB-антена)", 12, INK, "middle", bold=True))
    parts.append(fitbox(80, 100, 140, 70, "чип nRF24L01+\n+ доріжка-антена\nна платі",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK))
    # доріжка-меандр як символ
    parts.append(text(255, 120, "〰〰", 22, POS, "middle"))
    parts.append(fitbox(70, 200, 240, 80,
                        "дальність: десятки метрів\nпік TX: ~12 мА\nживлення: 10 мкФ вистачає\n"
                        "маленька, дешева",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.2, color=INK))

    # ── права: PA+LNA ──
    parts.append(rect(440, 70, 300, 230, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(590, 60, "PA+LNA (роз'єм SMA)", 12, INK, "middle", bold=True))
    parts.append(fitbox(470, 100, 150, 70, "чип + підсилювач\nPA/LNA (RFX2401C)\n+ роз'єм антени",
                        size=10, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK))
    # символ SMA-антени
    ax = 690
    parts.append(line(ax, 105, ax, 165, color=POS, sw=2.6))
    parts.append(line(ax, 105, ax - 14, 88, color=POS, sw=2.6))
    parts.append(line(ax, 105, ax + 14, 88, color=POS, sw=2.6))
    parts.append(text(ax, 182, "SMA", 10, POS, "middle", bold=True))
    parts.append(fitbox(462, 200, 256, 80,
                        "дальність: сотні метрів — км\nпік TX: до ~115 мА\nживлення: треба 100–220 мкФ!\n"
                        "більша, гріється сильніше",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))

    # спільне під низом
    parts.append(text(390, 320, "Виводи, SPI-керування й бібліотека — ті самі. Різниця лише в антені та апетиті струму.",
                      11, MUTED, "middle"))

    render(os.path.join(IMG, "variants.svg"), W, H, *parts,
           title="Дві версії nRF24: гола плата й PA+LNA з роз'ємом антени")


fig_block()
fig_pinout()
fig_wiring()
fig_variants()
print("Done. SVG in", IMG)
