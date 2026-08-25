# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Waveshare ESP32-C6-Zero».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що на платі: живлення й сигнали ────────────────────────────────────────
def fig_block():
    W, H = 900, 470
    f = [text(W / 2, 30, "Що на платі: від USB-C до кремнію", size=17, bold=True)]

    # USB-C роз'єм (ліворуч)
    ux, uy, uw, uh = 40, 210, 92, 70
    f.append(rect(ux, uy, uw, uh, fill=BG, stroke=INK, sw=1.8, rx=8))
    f.append(text(ux + uw / 2, uy + 26, "USB-C", size=13, bold=True))
    f.append(text(ux + uw / 2, uy + 46, "роз'єм", size=10.5, color=MUTED))

    # CC-резистори (підпис під USB)
    f.append(text(ux + uw / 2, uy + uh + 26, "CC1·CC2", size=10, color=MUTED))
    f.append(text(ux + uw / 2, uy + uh + 42, "5.1 кОм", size=10, color=MUTED))
    f.append(text(ux + uw / 2, uy + uh + 58, "«я — споживач»", size=9.5, color=MUTED))

    # LDO
    lx, ly, lw, lh = 210, 90, 150, 66
    b, bw, bh = textbox(lx + lw / 2, ly + lh / 2, "LDO ME6217\n5 В → 3.3 В",
                        size=12, fill="#eef7f0", stroke=FIELD, sw=1.8, min_w=lw)
    f.append(b)
    f.append(text(lx + lw / 2, ly - 12, "живлення", size=10.5, color=FIELD, bold=True))

    # ESP32-C6 модуль (центр-право, великий)
    ex, ey, ew, eh = 470, 96, 300, 258
    f.append(rect(ex, ey, ew, eh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(ex + ew / 2, ey + 26, "ESP32-C6FH8 (модуль)", size=13.5, bold=True))
    # внутрішні блоки
    def inner(iy, s, sub=None):
        ih = 34 if sub else 30
        f.append(rect(ex + 18, iy, ew - 36, ih, fill=BG, stroke=MUTED, sw=1.2, rx=6))
        f.append(text(ex + ew / 2, iy + (16 if sub else 19), s, size=11, bold=True))
        if sub:
            f.append(text(ex + ew / 2, iy + 28, sub, size=9, color=MUTED))
        return iy + ih + 12
    yy = ey + 40
    yy = inner(yy, "RISC-V HP  до 160 МГц  +  LP 20 МГц")
    yy = inner(yy, "Wi-Fi 6 · BT 5 · 802.15.4", "Zigbee / Thread")
    yy = inner(yy, "USB-Serial-JTAG (нативний)", "на IO13 = D+, IO12 = D−")
    yy = inner(yy, "8 МБ Flash · 512 КБ SRAM")

    # антена (праворуч від модуля)
    axx = ex + ew + 18
    f.append(text(axx + 24, ey + 90, "))", size=26, bold=True, color=NEG))
    f.append(text(axx + 24, ey + 120, "антена", size=10, color=MUTED))
    f.append(text(axx + 24, ey + 135, "2.4 ГГц", size=10, color=MUTED))

    # WS2812 (внизу під модулем)
    wx = 470
    b2, w2, h2 = textbox(wx + 70, 410, "WS2812B\nна IO8", size=11,
                         fill="#fdecea", stroke=POS, sw=1.6)
    f.append(b2)

    # кнопки
    b3, w3, h3 = textbox(wx + 235, 410, "BOOT (IO9)\nRESET (EN)", size=11,
                         fill=BG, stroke=INK, sw=1.5)
    f.append(b3)

    # стрілки живлення: USB → LDO → модуль
    f.append(arrow(ux + uw, uy + 12, lx - 6, ly + lh / 2, color=FIELD, sw=2.2))
    f.append(text((ux + uw + lx) / 2 + 4, uy + 2, "5 В (VBUS)", size=10, color=FIELD))
    f.append(arrow(lx + lw, ly + lh / 2, ex - 6, ey + 58, color=FIELD, sw=2.2))
    f.append(text((lx + lw + ex) / 2, ly + lh / 2 - 8, "3.3 В", size=10, color=FIELD))

    # стрілка даних: USB → модуль (нативний USB, повз LDO)
    f.append(arrow(ux + uw, uy + uh - 12, ex - 6, ey + 190, color=NEG, sw=2.2))
    f.append(text((ux + uw + ex) / 2 - 30, uy + uh + 4, "D+ / D−  (дані)", size=10, color=NEG))

    return render(os.path.join(IMG, "block.svg"), W, H, *f)


# ── 2. Розпіновка: два ряди контактів + приклад підключення ──────────────────
def fig_pinout():
    W, H = 940, 640
    f = [text(W / 2, 30, "Розпіновка контактних майданчиків", size=17, bold=True)]

    # центральний прямокутник плати
    bx, by, bw, bh = 360, 70, 220, 500
    f.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(bx + bw / 2, by + 30, "ESP32-C6", size=14, bold=True))
    f.append(text(bx + bw / 2, by + 50, "-Zero", size=14, bold=True))
    f.append(text(bx + bw / 2, by + 74, "23.5 × 17.8 мм", size=10, color=MUTED))
    # USB-C зверху
    f.append(rect(bx + bw / 2 - 34, by - 16, 68, 18, fill=BG, stroke=INK, sw=1.5, rx=4))
    f.append(text(bx + bw / 2, by - 3, "USB-C", size=9.5, bold=True))
    # антена внизу
    f.append(text(bx + bw / 2, by + bh - 14, ")) антена ((", size=11, color=NEG, bold=True))

    # опис контакту: (мітка, роль, колір-рамки, колір-обводки)
    PWR = ("#eef7f0", FIELD)
    STRAP = ("#fdecea", POS)
    USBP = ("#eaf0fd", NEG)
    PLAIN = (BG, INK)

    # лівий ряд згори вниз
    left = [
        ("5V",  "вхід 5 В", PWR),
        ("3V3", "вихід 3.3 В", PWR),
        ("GND", "земля", PLAIN),
        ("IO0", "ADC", PLAIN),
        ("IO1", "ADC", PLAIN),
        ("IO2", "ADC", PLAIN),
        ("IO3", "ADC", PLAIN),
        ("IO4", "strap · JTAG", STRAP),
        ("IO5", "strap · JTAG", STRAP),
        ("IO6", "JTAG", PLAIN),
        ("IO7", "JTAG", PLAIN),
        ("IO8", "strap · RGB", STRAP),
        ("IO9", "strap · BOOT", STRAP),
        ("IO14", "вільний", PLAIN),
    ]
    # правий ряд згори вниз
    right = [
        ("IO15", "strap · JTAG", STRAP),
        ("IO16", "TX (лог)", PLAIN),
        ("IO17", "RX (лог)", PLAIN),
        ("IO18", "вільний", PLAIN),
        ("IO20", "вільний", PLAIN),
        ("IO21", "вільний", PLAIN),
        ("IO22", "вільний", PLAIN),
        ("IO23", "вільний", PLAIN),
        ("IO13", "USB D+", USBP),
        ("IO12", "USB D−", USBP),
        ("GND", "земля", PLAIN),
    ]

    padw, padh = 150, 24
    gap = 6

    def col(items, x, anchor_right):
        n = len(items)
        y0 = by + 96
        step = padh + gap
        for i, (lbl, role, (fill, stroke)) in enumerate(items):
            yy = y0 + i * step
            f.append(rect(x, yy, padw, padh, fill=fill, stroke=stroke, sw=1.5, rx=5))
            # мітка контакту (жирна) ліворуч у майданчику, роль — праворуч
            f.append(text(x + 10, yy + padh / 2 + 4, lbl, size=11, bold=True, anchor="start"))
            f.append(text(x + padw - 10, yy + padh / 2 + 4, role, size=9.5,
                          color=MUTED, anchor="end"))
            # коротка риска до плати
            if anchor_right:
                f.append(line(x + padw, yy + padh / 2, bx, yy + padh / 2,
                              color=MUTED, sw=1))
            else:
                f.append(line(x, yy + padh / 2, bx + bw, yy + padh / 2,
                              color=MUTED, sw=1))

    col(left, bx - padw - 40, anchor_right=True)
    col(right, bx + bw + 40, anchor_right=False)

    # легенда (низ ліворуч)
    ly0 = 610
    def leg(lx, s, fill, stroke):
        f.append(rect(lx, ly0 - 12, 16, 16, fill=fill, stroke=stroke, sw=1.4, rx=3))
        f.append(text(lx + 22, ly0 + 1, s, size=10.5, anchor="start"))
    leg(40, "живлення", *PWR)
    leg(180, "strap — обережно при старті", *STRAP)
    leg(430, "нативний USB", *USBP)
    leg(590, "вільний вивід", *PLAIN)

    return render(os.path.join(IMG, "pinout.svg"), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_pinout()
    print("OK: block.svg, pinout.svg")
