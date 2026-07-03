# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Arduino Nano (ATmega, USB-C)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Блок-схема плати: USB-C → CH340C → ATmega328P, живлення й авто-скид ─────
def fig_block():
    W, H = 880, 520
    f = [text(W / 2, 30, "Що на платі: USB-C годує міст CH340, міст говорить із ATmega",
              size=15, bold=True)]

    def blk(x, y, w, h, title, sub, accent, fill):
        f.append(rect(x, y, w, h, fill=fill, stroke=accent, sw=1.8, rx=10))
        f.append(text(x + w / 2, y + 24, title, size=12.5, bold=True, color=accent))
        if sub:
            f.append(text(x + w / 2, y + 42, sub, size=9.5, color=MUTED))

    # ── ряд ДАНИХ (згори) ──
    yb = 70
    hb = 74
    usb = (70, yb, 130, hb)
    ch = (300, yb, 150, hb)
    mcu = (560, yb, 180, hb)
    blk(*usb, "USB-C", "гніздо + кабель", INK, "#eef2f8")
    blk(*ch, "CH340C", "USB ↔ UART міст", NEG, "#eaf0fd")
    blk(*mcu, "ATmega328P", "ядро AVR, 16 МГц", FIELD, "#eef6ef")

    # дані туди-назад між USB і мостом
    f.append(arrow(usb[0] + usb[2], yb + 26, ch[0], yb + 26, color=INK, sw=2.0))
    f.append(arrow(ch[0], yb + 50, usb[0] + usb[2], yb + 50, color=INK, sw=2.0))
    f.append(text((usb[0] + usb[2] + ch[0]) / 2, yb + 16, "D+ / D−", size=9, color=MUTED))

    # UART між мостом і МК
    f.append(arrow(ch[0] + ch[2], yb + 26, mcu[0], yb + 26, color=NEG, sw=2.0))
    f.append(text((ch[0] + ch[2] + mcu[0]) / 2, yb + 16, "TX→RX", size=9, color=NEG, bold=True))
    f.append(arrow(mcu[0], yb + 50, ch[0] + ch[2], yb + 50, color=NEG, sw=2.0))
    f.append(text((ch[0] + ch[2] + mcu[0]) / 2, yb + 66, "RX←TX", size=9, color=NEG, bold=True))

    # авто-скид: DTR (низ CH340) через конденсатор на RESET (низ МК) — власна смуга під рядом
    dy = yb + hb + 30
    dtx = ch[0] + 24
    rsx = mcu[0] + 24
    f.append(line(dtx, yb + hb, dtx, dy, color=POS, sw=1.8))
    f.append(line(dtx, dy, rsx, dy, color=POS, sw=1.8))
    f.append(line(rsx, dy, rsx, yb + hb, color=POS, sw=1.8))
    f.append(text(dtx + 6, yb + hb + 18, "DTR", size=9, color=POS, anchor="start", bold=True))
    f.append(text(rsx - 6, yb + hb + 18, "RESET", size=9, color=POS, anchor="end", bold=True))
    f.append(text((dtx + rsx) / 2, dy - 6, "конденсатор — авто-скид перед заливкою", size=9.5, color=POS))

    # ── ряд ЖИВЛЕННЯ (знизу) ──
    py = 300
    ph = 72
    ext = (70, py, 130, ph)
    reg = (300, py, 150, ph)
    rail = (560, py, 180, ph)
    blk(*ext, "VIN 7–12 В", "або USB 5 В", POS, "#fdecea")
    blk(*reg, "AMS1117-5.0", "лінійний → 5 В", POS, "#fdecea")
    f.append(rect(*rail, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rail[0] + rail[2] / 2, py + 26, "Шина 5 В", size=12.5, bold=True, color=FIELD))
    f.append(text(rail[0] + rail[2] / 2, py + 46, "живить ATmega й піни", size=9.5, color=MUTED))

    f.append(arrow(ext[0] + ext[2], py + ph / 2, reg[0], py + ph / 2, color=POS, sw=2.0))
    f.append(arrow(reg[0] + reg[2], py + ph / 2, rail[0], py + ph / 2, color=POS, sw=2.0))

    # USB 5 В теж живить вхід (пунктир з лівого краю USB униз до входу живлення)
    ux = usb[0] + 18
    f.append(line(ux, yb + hb, ux, py + ph / 2, color=POS, sw=1.6, dash="4,3"))
    f.append(line(ux, py + ph / 2, ext[0], py + ph / 2, color=POS, sw=1.6, dash="4,3"))

    # 5В шина живить МК вгору — прямо під центром МК, у порожній колонці
    upx = mcu[0] + mcu[2] / 2
    f.append(arrow(upx, py, upx, yb + hb, color=FIELD, sw=2.0))
    f.append(text(upx + 16, (py + yb + hb) / 2, "5 В", size=10, color=FIELD, bold=True, anchor="start"))

    # 3V3-пастка: підпис виводу на самому блоці CH340 + рамка-пояснення внизу (без лінії-різака)
    f.append(text(ch[0] + ch[2] - 8, yb + hb - 8, "3V3 →", size=9, color=MUTED, anchor="end", bold=True))
    b2, _, _ = textbox(268, 470,
                       "пін 3V3 — кволе джерело від CH340 (лічені мА);\nокремого регулятора 3.3 В тут НЕМА",
                       size=10, fill=FILL, stroke=MUTED)
    f.append(b2)

    b3, _, _ = textbox(680, 470,
                       "порт лише везе дані й живлення;\nсама програма — в ATmega328P",
                       size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b3)
    render(os.path.join(IMG, "board-block.svg"), W, H, *f)


# ── 2. Розпіновка: два ряди по 15, підключення пін-у-пін ──────────────────────
def fig_pinout():
    W, H = 900, 560
    f = [text(W / 2, 30, "Розпіновка Nano: два ряди по 15; те, що треба знати, щоб під'єднати",
              size=15, bold=True)]

    # тіло плати
    bx, by, bw, bh = 300, 70, 300, 430
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=14))
    # USB-C зверху
    f.append(rect(bx + bw / 2 - 34, by - 20, 68, 26, fill="#e6ebf2", stroke=INK, sw=1.6, rx=6))
    f.append(text(bx + bw / 2, by - 3, "USB-C", size=10, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 - 8, "ATmega328P", size=13, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, by + bh / 2 + 12, "16 МГц · CH340C", size=10, color=MUTED))

    rows = 15
    pitch = (bh - 30) / (rows - 1)
    y0 = by + 15

    # (підпис, колір) — ліва колонка згори вниз (біля USB), правий ряд теж
    left = [
        ("D13 / SCK", NEG), ("3V3", MUTED), ("REF", MUTED), ("A0", FIELD), ("A1", FIELD),
        ("A2", FIELD), ("A3", FIELD), ("A4 / SDA", POS), ("A5 / SCL", POS), ("A6*", FIELD),
        ("A7*", FIELD), ("5V", POS), ("RST", INK), ("GND", INK), ("VIN", POS),
    ]
    right = [
        ("D12 / MISO", NEG), ("D11 / MOSI ~", NEG), ("D10 / SS ~", NEG), ("D9 ~", INK),
        ("D8", INK), ("D7", INK), ("D6 ~", INK), ("D5 ~", INK), ("D4", INK),
        ("D3 ~ / INT1", INK), ("D2 / INT0", INK), ("GND", INK), ("RST", INK),
        ("D0 / RX", NEG), ("D1 / TX", NEG),
    ]

    def pinrow(items, side):
        for i, (lbl, col) in enumerate(items):
            y = y0 + i * pitch
            if side == "L":
                px = bx
                f.append(circle(px, y, 4.5, fill=col, stroke=INK, sw=1.0))
                f.append(text(px - 12, y + 4, lbl, size=10, color=col, anchor="end", bold=True))
            else:
                px = bx + bw
                f.append(circle(px, y, 4.5, fill=col, stroke=INK, sw=1.0))
                f.append(text(px + 12, y + 4, lbl, size=10, color=col, anchor="start", bold=True))

    pinrow(left, "L")
    pinrow(right, "R")

    # легенда праворуч
    lx = 690
    ly = 90
    leg = [
        ("живлення / VIN / 5V", POS),
        ("земля · RESET · цифрові", INK),
        ("SPI / UART (D13,12,11,10, D0,D1)", NEG),
        ("аналогові A0–A7 (тільки вхід у A6/A7)", FIELD),
        ("~ = вивід з апаратним PWM", INK),
    ]
    f.append(text(lx, ly - 14, "Як читати піни", size=12, bold=True, anchor="start"))
    for i, (t, c) in enumerate(leg):
        yy = ly + i * 30
        f.append(circle(lx + 8, yy - 4, 5, fill=c, stroke=INK, sw=1.0))
        f.append(text(lx + 22, yy, t, size=10, color=INK, anchor="start"))

    # примітка про A6/A7 і I2C/SPI
    b, _, _ = textbox(lx + 92, ly + 190,
                      "A4/A5 = I²C (SDA/SCL)\nD11/D12/D13 = SPI\nD0/D1 = апаратний UART\n(зайняті під час заливки)",
                      size=10, fill=FILL, stroke=MUTED)
    f.append(b)

    # ліва пояснювальна рамка
    b2, _, _ = textbox(150, ly + 120,
                       "* A6 і A7 —\nтільки аналоговий вхід:\nцифрою керувати\nними НЕ можна",
                       size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b2)

    b3, _, _ = textbox(W / 2, 535,
                       "піни симетричні; типове підключення — живлення на 5V/GND, датчики на A0–A7, шини на своїх лініях",
                       size=11, fill="#eef2f8", stroke=NEG)
    f.append(b3)
    render(os.path.join(IMG, "pinout.svg"), W, H, *f)


# ── 3. Бюджет флеш-пам'яті: старий проти нового завантажувача ──────────────────
def fig_flash():
    W, H = 820, 300
    f = [text(W / 2, 30, "32 КБ флешу: скільки з'їдає завантажувач і що лишається скетчу",
              size=15, bold=True)]

    total = 32768
    barx, barw = 70, 680
    scale = barw / total

    def bar(y, boot_bytes, boot_lbl, sketch_lbl, title):
        f.append(text(barx, y - 12, title, size=11.5, bold=True, anchor="start"))
        # рамка всієї флеш
        f.append(rect(barx, y, barw, 46, fill=BG, stroke=INK, sw=1.6, rx=6))
        bw = boot_bytes * scale
        # завантажувач
        f.append(rect(barx, y, bw, 46, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
        f.append(text(barx + bw / 2, y + 28, boot_lbl, size=9, color=POS, bold=True))
        # скетч
        sx = barx + bw
        f.append(text(sx + (barx + barw - sx) / 2, y + 28, sketch_lbl, size=11, color=FIELD, bold=True))

    bar(80, 2048, "ATmegaBOOT\n2 КБ", "скетчу: 30 720 байтів", "Старий завантажувач (57600 бод)")
    bar(180, 512, "optiboot\n0.5 КБ", "скетчу: 32 256 байтів", "Новий завантажувач (115200 бод)")

    # шкала
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        xx = barx + barw * frac
        f.append(line(xx, 236, xx, 244, color=MUTED, sw=1.2))
        f.append(text(xx, 258, "%d КБ" % round(total * frac / 1024), size=9, color=MUTED))

    b, _, _ = textbox(W / 2, 285,
                      "розмір «Maximum» у консолі підказує ваш варіант: 30720 → старий, 32256 → optiboot",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "flash-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_pinout()
    fig_flash()
    print("OK: 3 figures ->", IMG)
