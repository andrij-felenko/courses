# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «ESP32-S3 SuperMini».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що на платі: модуль, антена, USB-C, LDO, RGB-світлодіод, кнопки ────────
def fig_anatomy():
    W, H = 820, 470
    f = [text(W / 2, 30, "Що вміщує платка завбільшки з ніготь", size=16, bold=True)]

    # межа плати
    bx, by, bw, bh = 150, 66, 520, 320
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=16))
    f.append(text(bx + bw / 2, by + bh + 24, "22.5 × 18 мм — менше за монету", size=11, color=MUTED, italic=True))

    # PCB-антена (зубчаста доріжка) — верхній край
    ax, ay = bx + bw - 92, by + 20
    f.append(rect(ax, ay, 74, 40, fill="#fff7e6", stroke="#b8860b", sw=1.6, rx=6))
    f.append(text(ax + 37, ay + 17, "PCB-", size=9.5, bold=True, color="#8a6d00"))
    f.append(text(ax + 37, ay + 31, "антена", size=9.5, bold=True, color="#8a6d00"))

    # екранований модуль ESP32-S3 (метал) у центрі
    mx, my, mw, mh = bx + 150, by + 90, 210, 130
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=2.0, rx=10))
    f.append(text(mx + mw / 2, my + 32, "чип ESP32-S3", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 55, "2 ядра LX7 · 240 МГц", size=10, color=INK))
    f.append(text(mx + mw / 2, my + 75, "512 КБ SRAM · без PSRAM", size=10, color=INK))
    f.append(text(mx + mw / 2, my + 95, "4 МБ Flash · Wi-Fi + BLE 5", size=10, color=INK))

    # від антени до модуля
    f.append(line(ax + 20, ay + 40, mx + mw - 30, my, color="#b8860b", sw=1.8))

    # USB-C знизу
    ux, uy = bx + 30, by + bh - 46
    f.append(rect(ux, uy, 96, 34, fill="#eaf0fd", stroke=NEG, sw=1.7, rx=10))
    f.append(text(ux + 48, uy + 21, "USB-C", size=12, bold=True, color=NEG))
    f.append(text(ux + 48, uy + 52, "живлення + прошивка", size=9, color=MUTED))
    # USB → модуль (нативний, без перехідника)
    f.append(line(ux + 48, uy, mx + 40, my + mh, color=NEG, sw=2.0))
    f.append(text(ux + 150, uy - 6, "D+/D− нативно", size=9, color=NEG, bold=True, anchor="start"))

    # LDO ME6211
    lx, ly = bx + 40, by + 60
    f.append(rect(lx, ly, 92, 46, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(lx + 46, ly + 19, "ME6211", size=11, bold=True, color=POS))
    f.append(text(lx + 46, ly + 36, "5 В → 3.3 В", size=9.5, color=INK))
    f.append(line(lx + 92, ly + 23, mx, my + 30, color=POS, sw=1.8))

    # RGB-світлодіод (WS2812) справа знизу
    gx, gy = bx + bw - 96, by + bh - 58
    f.append(circle(gx, gy, 14, fill="#f0e6ff", stroke="#7a3fb0", sw=2))
    f.append(text(gx, gy + 32, "WS2812 · GPIO48", size=9, color="#7a3fb0"))
    f.append(line(gx, gy - 14, mx + mw - 18, my + mh, color="#7a3fb0", sw=1.6))

    # кнопки BOOT і RESET
    for i, (nm, cx) in enumerate((("BOOT", bx + 200), ("RST", bx + 255))):
        f.append(rect(cx, by + bh - 40, 40, 26, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
        f.append(text(cx + 20, by + bh - 23, nm, size=9.5, bold=True, color=FIELD))

    # два ряди контактів по боках (гребінки)
    for row_x in (bx + 6, bx + bw - 6):
        for k in range(10):
            yy = by + 40 + k * 26
            f.append(circle(row_x, yy, 4.5, fill="#d9dde3", stroke=MUTED, sw=1.2))
    f.append(text(bx + bw / 2, by + bh - 6, "по 10–12 контактів з кожного боку", size=9, color=MUTED))

    b, _, _ = textbox(W / 2, 452,
                      "нативний USB у самому чипі — прошивка йде прямо кабелем, окремий перехідник не потрібен",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Мапа виводів: безпечні · застережні · живлення ────────────────────────
def fig_pinmap():
    W, H = 900, 560
    f = [text(W / 2, 30, "Виводи за характером: що бери вільно, а що з осторогою", size=16, bold=True)]

    colW = 254
    gap = 30
    x1 = 30
    x2 = x1 + colW + gap
    x3 = x2 + colW + gap
    topY = 62
    rowH = 30

    def column(px, title, accent, fill, rows, note):
        n = len(rows)
        boxH = 48 + n * rowH + 30
        f.append(rect(px, topY, colW, boxH, fill=fill, stroke=accent, sw=1.8, rx=12))
        f.append(text(px + colW / 2, topY + 26, title, size=12.5, bold=True, color=accent))
        for i, (pin, what) in enumerate(rows):
            ry = topY + 48 + i * rowH
            f.append(rect(px + 12, ry, 62, 22, fill=BG, stroke=accent, sw=1.3, rx=5))
            f.append(text(px + 43, ry + 16, pin, size=10.5, bold=True, color=accent))
            f.append(text(px + 84, ry + 16, what, size=9.5, color=INK, anchor="start"))
        b, _, _ = textbox(px + colW / 2, topY + boxH - 15, note, size=9.5,
                          fill=BG, stroke=accent, min_w=colW - 24)
        f.append(b)

    column(x1, "Вільні GPIO", FIELD, "#eef6ef",
           [("1  2  3", "загальні"),
            ("4  5  6", "загальні"),
            ("7  8  9", "8/9 — типова I²C"),
            ("10 11 12", "загальні"),
            ("13 21", "загальні / ADC1")],
           "будь-що: вхід, вихід, ШІМ, ADC")

    column(x2, "З осторогою", POS, "#fdecea",
           [("0", "BOOT — старт із кнопки"),
            ("45", "напруга Flash при старті"),
            ("46", "лише вхід, режим старту"),
            ("48", "зайнятий RGB-діодом"),
            ("35 36 37", "усередині Flash/PSRAM"),
            ("19 20", "лінії USB (D− / D+)")],
           "не чіпай або знай наслідок")

    column(x3, "Живлення", NEG, "#eaf0fd",
           [("5V", "вхід або вихід VBUS"),
            ("3V3", "вихід LDO ≤ 0.5 А"),
            ("GND", "спільна земля")],
           "5V ↔ USB напряму; 3V3 — з ME6211")

    b, _, _ = textbox(W / 2, 542,
                      "ADC є лише на GPIO1–10 (ADC1) — з увімкненим Wi-Fi беруть саме ADC1, бо ADC2 конфліктує з радіо",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "pinmap.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: давач по I²C ───────────────────────────────────
def fig_wiring():
    W, H = 800, 430
    f = [text(W / 2, 30, "Підключення пін-у-пін: давач по шині I²C", size=16, bold=True)]

    # плата зліва
    bx, by, bw, bh = 70, 70, 210, 250
    f.append(rect(bx, by, bw, bh, fill="#eef2f8", stroke=INK, sw=1.9, rx=12))
    f.append(text(bx + bw / 2, by + 26, "ESP32-S3 SuperMini", size=12, bold=True))
    left_pins = [("3V3", FIELD), ("GND", INK), ("GPIO8", NEG), ("GPIO9", NEG)]
    for i, (nm, col) in enumerate(left_pins):
        yy = by + 70 + i * 46
        f.append(circle(bx + bw - 14, yy, 6, fill=BG, stroke=col, sw=1.8))
        f.append(text(bx + bw - 34, yy + 5, nm, size=11, bold=True, color=col, anchor="end"))

    # давач справа
    sx, sy, sw_, sh = 540, 90, 190, 210
    f.append(rect(sx, sy, sw_, sh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=12))
    f.append(text(sx + sw_ / 2, sy + 26, "Давач (I²C)", size=12, bold=True, color=FIELD))
    f.append(text(sx + sw_ / 2, sy + 44, "напр. BMP280 / OLED", size=9.5, color=MUTED))
    right_pins = [("VCC", FIELD), ("GND", INK), ("SDA", NEG), ("SCL", NEG)]
    for i, (nm, col) in enumerate(right_pins):
        yy = sy + 78 + i * 40
        f.append(circle(sx + 14, yy, 6, fill=BG, stroke=col, sw=1.8))
        f.append(text(sx + 30, yy + 5, nm, size=11, bold=True, color=col, anchor="start"))

    # зʼєднання
    pairs = [(0, 0, FIELD, "3.3 В"), (1, 1, INK, "земля"),
             (2, 2, NEG, "SDA ↔ GPIO8"), (3, 3, NEG, "SCL ↔ GPIO9")]
    for li, ri, col, lbl in pairs:
        ly = by + 70 + li * 46
        ry = sy + 78 + ri * 40
        midx = (bx + bw + sx) / 2
        f.append(line(bx + bw - 8, ly, midx, ly, color=col, sw=2.0))
        f.append(line(midx, ly, midx, ry, color=col, sw=2.0))
        f.append(line(midx, ry, sx + 8, ry, color=col, sw=2.0))
        f.append(text(midx + 6, (ly + ry) / 2 - 4, lbl, size=9.5, color=col, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 408,
                      "живимо давач із 3V3 (не з 5V!); дві лінії I²C потребують підтяжок до 3.3 В — часто вони вже на модулі давача",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Механіка сканера I²C: перебір адрес, ACK (0) vs NACK (лінія висока) ────
def fig_i2c_scan():
    W, H = 860, 470
    f = [text(W / 2, 30, "Як сканер знаходить давача на шині I²C", size=16, bold=True)]

    # ведучий (ESP32) зліва
    mx, my, mw, mh = 40, 150, 150, 120
    f.append(rect(mx, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=1.9, rx=12))
    f.append(text(mx + mw / 2, my + 34, "Ведучий", size=13, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 54, "(ESP32-S3)", size=10.5, color=MUTED))
    f.append(text(mx + mw / 2, my + 82, "по черзі кидає", size=10, color=INK))
    f.append(text(mx + mw / 2, my + 98, "кожну адресу →", size=10, color=INK))

    # колонка спроб (адреса → вердикт)
    col_x = 300
    rows = [
        ("0x08", False), ("0x09", False), ("…", None),
        ("0x3C", False), ("…", None),
        ("0x76", True),  ("0x77", False),
    ]
    top = 78
    step = 46
    for i, (addr, hit) in enumerate(rows):
        yy = top + i * step
        if addr == "…":
            f.append(text(col_x + 70, yy + 4, "⋮", size=18, color=MUTED))
            continue
        # рамка адреси
        if hit:
            aw, ah = 88, 34
            f.append(rect(col_x, yy - ah / 2, aw, ah, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=8))
            f.append(text(col_x + aw / 2, yy + 5, addr, size=13, bold=True, color=FIELD))
        else:
            aw, ah = 88, 30
            f.append(rect(col_x, yy - ah / 2, aw, ah, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
            f.append(text(col_x + aw / 2, yy + 4, addr, size=12, color=MUTED))

        # стрілка від ведучого до першого рядка (лише орієнтир на верх колонки)
        # вердикт справа
        vx = col_x + 150
        if hit:
            f.append(text(vx, yy + 5, "давач тягне лінію до 0", size=12, bold=True,
                          color=FIELD, anchor="start"))
            f.append(text(vx + 250, yy + 5, "→ ACK", size=12.5, bold=True,
                          color=FIELD, anchor="start"))
        else:
            f.append(text(vx, yy + 4, "ніхто не тягне — лінія висока", size=11,
                          color=MUTED, anchor="start"))
            f.append(text(vx + 250, yy + 4, "→ NACK", size=11.5, bold=True,
                          color=POS, anchor="start"))

    # стрілка «перебирає» від ведучого до колонки
    f.append(arrow(mx + mw + 6, my + 20, col_x - 10, top + 4, color=NEG, sw=1.8))

    # підсумок унизу
    b, _, _ = textbox(W / 2, 432,
                      "адресу з ACK сканер друкує (тут 0x76); на решту адрес лінію ніхто не тягне (NACK) — перебір іде далі",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "i2c-scan.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_pinmap()
    fig_wiring()
    fig_i2c_scan()
    print("OK: 4 figures ->", IMG)
