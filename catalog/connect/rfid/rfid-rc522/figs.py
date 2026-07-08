# -*- coding: utf-8 -*-
"""Фігури об'єкта «RFID-RC522» (catalog/connect/rfid). Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: як воно працює — поле живить мітку, мітка відповідає навантаженням ─
# Зчитувач гонить 13.56 МГц у котушку → поле наводить струм у котушці мітки
# (живить її чип). Мітка відповідає, підмикаючи/відмикаючи навантаження —
# «навантажувальна модуляція», яку зчитувач ловить як хитання власного струму.
def fig_principle():
    W, H = 760, 380
    parts = []

    # ліворуч: RC522 як джерело поля
    parts.append(fitbox(40, 150, 150, 90, "RC522\n(зчитувач)\nгонить 13.56 МГц",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.8, color=INK, bold=True))
    # котушка зчитувача (символ — кілька дуг)
    cxr = 235
    for i, r in enumerate((26, 34, 42)):
        parts.append(circle(cxr, 195, r, fill="none", stroke=NEG, sw=2.0))
    parts.append(text(cxr, 258, "котушка-антена", 11, NEG, "middle", bold=True))

    # поле між котушками — хвилясті стрілки праворуч
    fy = 150
    parts.append(arrow(285, fy, 470, fy, color=POS, sw=2.2))
    parts.append(text(377, 138, "магнітне поле 13.56 МГц", 12, POS, "middle", bold=True))
    parts.append(text(377, fy + 22, "живить мітку (енергія)", 10, MUTED, "middle"))

    # відповідь мітки — стрілка назад
    parts.append(arrow(470, 235, 285, 235, color=FIELD, sw=2.2))
    parts.append(text(377, 254, "відповідь: навантажувальна", 11, FIELD, "middle", bold=True))
    parts.append(text(377, 270, "модуляція (мітка «хитає» поле)", 10, MUTED, "middle"))

    # праворуч: мітка (котушка + крихітний чип, БЕЗ живлення)
    cxt = 520
    for i, r in enumerate((26, 34, 42)):
        parts.append(circle(cxt, 195, r, fill="none", stroke=FIELD, sw=2.0))
    parts.append(fitbox(590, 165, 130, 60, "мітка/брелок\n(котушка + чип,\nбез батарейки)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK))
    parts.append(line(562, 195, 590, 195, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "principle.svg"), W, H, *parts,
           title="Як працює RC522: поле живить мітку, мітка відповідає модуляцією")


# ── Фігура 2: що на платі — MFRC522 + кварц 27.12 МГц + котушка + вибір шини ────
# Серце — чип MFRC522. Від кварцу 27.12 МГц ділиться 13.56 МГц. Чип сам робить
# радіо (котушка на платі) і виставляє назовні хост-шину (типово SPI).
def fig_block():
    W, H = 780, 400
    parts = []

    # межа плати — пунктирна рамка
    parts.append(rect(190, 70, 470, 280, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(425, 60, "плата RC522 (одна плата)", 12, MUTED, "middle"))

    # MCU ліворуч, поза платою
    parts.append(fitbox(30, 175, 130, 70, "Ваш MCU\n(ESP32, STM32,\nAVR…)",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))

    # чип MFRC522 у центрі
    parts.append(fitbox(300, 165, 150, 80, "MFRC522\n(радіочастотний\nфронтенд NXP)",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # кварц 27.12 МГц знизу під чипом
    parts.append(fitbox(300, 285, 150, 40, "кварц 27.12 МГц  ÷2 → 13.56",
                        size=10, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))
    parts.append(line(375, 245, 375, 285, color=MUTED, sw=1.2))

    # котушка-антена праворуч на платі
    axc = 585
    for r in (20, 27, 34):
        parts.append(circle(axc, 205, r, fill="none", stroke=POS, sw=1.8))
    parts.append(text(axc, 258, "котушка на платі", 10, POS, "middle", bold=True))
    parts.append(arrow(450, 205, axc - 40, 205, color=POS, sw=2.0))
    parts.append(text(510, 195, "радіо", 10, POS, "middle"))

    # хост-шина MCU↔чип (двобічна) + напис вибору шини
    parts.append(arrow(160, 195, 300, 195, color=NEG, sw=2.0))
    parts.append(arrow(300, 218, 160, 218, color=NEG, sw=2.0))
    parts.append(text(230, 185, "SPI (типово)", 11, NEG, "middle", bold=True))
    parts.append(text(230, 238, "+ живлення 3.3 В", 10, MUTED, "middle"))

    render(os.path.join(IMG, "block.svg"), W, H, *parts,
           title="Що на платі RC522: чип MFRC522 робить усю радіороботу")


# ── Фігура 3: розводка пін-у-пін RC522 → MCU (SPI) ────────────────────────────
# 8 виводів: 3.3V, RST, GND, IRQ, MISO, MOSI, SCK, SDA(=SS). SDA — це chip-select.
def fig_wiring():
    W, H = 780, 470
    parts = []
    # корпус модуля
    bx, by, bw, bh = 250, 80, 140, 330
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(bx + bw / 2, by - 14, "RC522 (SPI)", 12, INK, "middle", bold=True))

    rows = [
        # (пін на платі, колір, куди на MCU / роль)
        ("3.3V", POS,   "3.3 В  (НЕ 5 В!)"),
        ("RST",  MUTED, "будь-який GPIO"),
        ("GND",  INK,   "спільна земля"),
        ("IRQ",  FIELD, "GPIO з перериванням (необов'язково)"),
        ("MISO", NEG,   "MISO апаратного SPI"),
        ("MOSI", NEG,   "MOSI"),
        ("SCK",  NEG,   "SCK"),
        ("SDA",  NEG,   "= SS (chip-select) → будь-який GPIO"),
    ]
    n = len(rows)
    y0 = by + 30
    step = (bh - 52) / (n - 1)
    for i, (pin, col, desc) in enumerate(rows):
        y = y0 + i * step
        # вивід-лапка ліворуч від модуля
        parts.append(line(bx, y, bx - 18, y, color=col, sw=2.2))
        parts.append(circle(bx - 18, y, 3.5, fill=col, stroke=INK, sw=1))
        parts.append(text(bx - 26, y + 4, pin, 12, col, "end", bold=True))
        # опис праворуч від модуля
        parts.append(line(bx + bw, y, bx + bw + 18, y, color=MUTED, sw=1.2))
        parts.append(text(bx + bw + 24, y + 4, desc, 11, INK, "start"))

    # застереження про SDA=SS знизу ліворуч (з запасом, не перетинає виводи)
    parts.append(fitbox(20, by + bh + 6, 300, 44,
                        "SDA тут — це НЕ I2C-дані, а вибір\nкристала SPI (SS/CS). Назва збиває.",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))
    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Розводка RC522 → MCU по SPI (8 виводів)")


# ── Фігура 4: карта пам'яті MIFARE Classic 1K — сектори, блоки, трейлер ─────────
# 16 секторів × 4 блоки × 16 байтів. Блок 0 сектора 0 — заводський (UID).
# Останній блок кожного сектора — трейлер: KeyA | AccessBits | KeyB.
def fig_mifare_map():
    W, H = 820, 470
    parts = []

    # ── ліворуч: стос секторів (схематично 0..15) ──
    sx, sy, sw = 60, 70, 150
    rowh = 20
    parts.append(text(sx + sw / 2, sy - 16, "MIFARE Classic 1K", 13, INK, "middle", bold=True))
    parts.append(text(sx + sw / 2, sy + 2, "16 секторів × 4 блоки × 16 Б", 10, MUTED, "middle"))

    # сектор 0 (розкриваємо блоки), далі згорнуті сектори
    y = sy + 16
    labels = [
        ("блок 0 — UID (заводський)", POS, "#fdecea"),
        ("блок 1 — дані", INK, "#eef2f7"),
        ("блок 2 — дані", INK, "#eef2f7"),
        ("блок 3 — ТРЕЙЛЕР (ключі)", FIELD, "#eafaf1"),
    ]
    for txt, col, bg in labels:
        parts.append(rect(sx, y, sw, rowh, fill=bg, stroke=col, sw=1.4, rx=2))
        parts.append(text(sx + 6, y + 14, txt, 9, col, "start", bold=(col != INK)))
        y += rowh
    parts.append(text(sx + sw / 2, y + 12, "сектор 0", 10, MUTED, "middle", bold=True))

    # згорнуті сектори 1..15
    y2 = y + 26
    for i in range(3):
        parts.append(rect(sx, y2, sw, rowh - 4, fill="#f4f6f9", stroke=MUTED, sw=1.0, rx=2))
        y2 += rowh - 4
    parts.append(text(sx + sw / 2, y2 + 12, "…сектори 1…15 (так само)", 9, MUTED, "middle"))

    # стрілка від трейлера сектора 0 до розкладу праворуч
    ty = sy + 16 + 3 * rowh + rowh / 2
    parts.append(arrow(sx + sw, ty, 330, 150, color=FIELD, sw=2.0))
    parts.append(text((sx + sw + 330) / 2, ty - 10, "розклад", 9, FIELD, "middle"))

    # ── праворуч: 16 байтів трейлер-блоку ──
    bx, by = 340, 110
    cellw, cellh = 27, 46
    parts.append(text(bx + 8 * cellw, by - 18, "Трейлер-блок: 16 байтів", 12, INK, "middle", bold=True))
    # три зони
    zones = [
        (0, 6, "Key A (6 Б)", POS, "#fdecea"),
        (6, 3, "Access\nbits (3)", "#f0b429", "#fff8e1"),
        (9, 1, "u", MUTED, "#f4f6f9"),
        (10, 6, "Key B (6 Б)", NEG, "#eaf0ff"),
    ]
    for start, span, lbl, col, bg in zones:
        zx = bx + start * cellw
        parts.append(rect(zx, by, span * cellw, cellh, fill=bg, stroke=col, sw=1.6, rx=3))
        parts.append(fitbox(zx, by + cellh + 4, span * cellw, 30, lbl,
                            size=9, fill="none", stroke="none", color=col))
    # номери байтів 0..15
    for i in range(16):
        parts.append(text(bx + i * cellw + cellw / 2, by + cellh + 40, str(i), 8, MUTED, "middle"))
        if 0 < i < 16:
            parts.append(line(bx + i * cellw, by, bx + i * cellw, by + cellh, color="#ffffff", sw=0.8))

    # пояснення знизу
    parts.append(fitbox(bx, by + 110, 16 * cellw, 96,
                        "Автентифікація сектора = довести знання Key A АБО Key B.\n"
                        "Access-байти (6…8) вирішують, що кожен ключ може: читати,\n"
                        "писати дані, міняти самі ключі. Key A з картки НІКОЛИ не\n"
                        "читається (повертає нулі). Зіпсуєте трейлер — сектор мертвий.",
                        size=10, pad=10, fill="#fbfcfd", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(IMG, "mifare-map.svg"), W, H, *parts,
           title="Карта пам'яті MIFARE Classic 1K: сектори, блоки, трейлер-блок")


fig_principle()
fig_block()
fig_wiring()
fig_mifare_map()
print("Done. SVG in", IMG)
