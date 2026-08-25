# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «ESP32-CAM (OV2640 + microSD)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Куди зникли виводи: бюджет GPIO ESP32-CAM ─────────────────────────────
def fig_gpio_budget():
    W, H = 860, 520
    f = [text(W / 2, 30, "Куди зникли виводи: майже всі GPIO зайняті камерою та карткою",
              size=15.5, bold=True)]

    # чотири колонки-споживачі + колонка «вільні»
    colY = 66
    colH = 356
    gap = 18
    cols = [
        ("Камера OV2640", POS, "#fdecea",
         ["XCLK  0", "PCLK  22", "VSYNC 25", "HREF  23",
          "SDA   26", "SCL   27", "PWDN  32",
          "D0..D7:", "5 18 19 21", "36 39 34 35"]),
        ("Картка SD-MMC", NEG, "#eaf0fd",
         ["CLK   14", "CMD   15", "DATA0  2", "DATA1  4",
          "DATA2 12", "DATA3 13", "", "(4 і 12/13 —", " лише в 4-біт", "  режимі)"]),
        ("Службове", MUTED, "#f1f3f5",
         ["UART TX 1", "UART RX 3", "BOOT   0", "PSRAM 16",
          "спалах 4", "черв.LED 33", "", "1/3 — прошивка", "0 — режим", "завантаження"]),
        ("Вільні на гребінці", FIELD, "#eaf7ee",
         ["GPIO 12", "GPIO 13", "GPIO 16*", "", "у 1-біт-режимі", "картка звільняє", "ці два виводи;", "16 — лише без", "PSRAM (*)", ""]),
    ]
    n = len(cols)
    cw = (W - 2 * 40 - (n - 1) * gap) / n
    x = 40
    for title, accent, fill, rows in cols:
        f.append(rect(x, colY, cw, colH, fill=fill, stroke=accent, sw=1.8, rx=10))
        f.append(text(x + cw / 2, colY + 24, title, size=12.5, bold=True, color=accent))
        f.append(line(x + 14, colY + 34, x + cw - 14, colY + 34, color=accent, sw=1.1))
        ry = colY + 58
        for r in rows:
            if r:
                mono = any(ch.isdigit() for ch in r) and ("режим" not in r and "лише" not in r and "PSRAM" not in r and "спалах" not in r and "прошивк" not in r and "завант" not in r and "звільня" not in r and "біт" not in r)
                f.append(text(x + cw / 2, ry, r, size=11.5 if mono else 10,
                              color=INK if mono else MUTED, bold=mono))
            ry += 27
        x += cw + gap

    # підсумкова стрічка
    b, _, _ = textbox(W / 2, colY + colH + 52,
                      "ESP32 має ~34 GPIO — камера з'їдає 16, картка ще 6; вільними на гребінці лишаються одиниці",
                      size=12, fill="#eaf7ee", stroke=FIELD, bold=False)
    f.append(b)
    render(os.path.join(IMG, "gpio-budget.svg"), W, H, *f)


# ── 2. Прошивка через USB-UART-перехідник: розводка пін-у-пін ─────────────────
def fig_program_wiring():
    W, H = 820, 470
    f = [text(W / 2, 30, "Прошивка: USB-UART-перехідник + перемичка GPIO0 на землю",
              size=15.5, bold=True)]

    # ── перехідник ліворуч ──
    ax, ay, aw, ah = 60, 92, 200, 250
    f.append(rect(ax, ay, aw, ah, fill="#eef2f8", stroke=NEG, sw=1.9, rx=12))
    f.append(text(ax + aw / 2, ay + 26, "USB-UART", size=13, bold=True, color=NEG))
    f.append(text(ax + aw / 2, ay + 44, "(CP2102 / CH340)", size=10, color=MUTED))
    f.append(text(ax + aw / 2, ay + 62, "джампер на 5 В !", size=10.5, bold=True, color=POS))

    # ── плата ESP32-CAM праворуч ──
    bx, by, bw, bh = W - 60 - 230, 92, 230, 250
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=INK, sw=1.9, rx=12))
    f.append(text(bx + bw / 2, by + 26, "ESP32-CAM", size=13, bold=True))
    f.append(text(bx + bw / 2, by + 44, "(AI-Thinker)", size=10, color=MUTED))

    # ряди контактів (від, до, колір, підпис-по-центру)
    rows = [
        ("5V",  "5V",  POS,  "живлення 5 В"),
        ("GND", "GND", INK,  "спільна земля"),
        ("TX",  "RX (U0R)", NEG, "перехр.: TX→RX"),
        ("RX",  "TX (U0T)", NEG, "перехр.: RX→TX"),
    ]
    ry0 = ay + 96
    dy = 42
    lax = ax + aw            # правий край перехідника
    lbx = bx                 # лівий край плати
    for i, (lp, rp, col, mid) in enumerate(rows):
        yy = ry0 + i * dy
        # пелюстки контактів
        f.append(circle(lax, yy, 5, fill=BG, stroke=col, sw=2))
        f.append(circle(lbx, yy, 5, fill=BG, stroke=col, sw=2))
        f.append(text(lax - 12, yy + 4, lp, size=10.5, color=col, bold=True, anchor="end"))
        f.append(text(lbx + 12, yy + 4, rp, size=10.5, color=col, bold=True, anchor="start"))
        # провід
        f.append(line(lax + 5, yy, lbx - 5, yy, color=col, sw=2.2))
        f.append(text((lax + lbx) / 2, yy - 8, mid, size=9.5, color=MUTED))

    # ── перемичка GPIO0 → GND (окремо, знизу плати) ──
    jy = by + bh + 30
    g0x = bx + 40
    gndx = bx + bw - 40
    f.append(circle(g0x, jy, 5, fill="#fdecea", stroke=POS, sw=2))
    f.append(circle(gndx, jy, 5, fill=BG, stroke=INK, sw=2))
    f.append(text(g0x, jy + 20, "GPIO0", size=10.5, bold=True, color=POS))
    f.append(text(gndx, jy + 20, "GND", size=10.5, bold=True, color=INK))
    f.append(line(g0x + 5, jy, gndx - 5, jy, color=POS, sw=2.4, dash="6,4"))
    f.append(text((g0x + gndx) / 2, jy - 10, "перемичка на час заливання", size=10, color=POS, bold=True))

    b, _, _ = textbox(W / 2, H - 24,
                      "GPIO0 на землю → режим завантаження; після заливання перемичку зняти й натиснути RST",
                      size=11.5, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "program-wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gpio_budget()
    fig_program_wiring()
    print("OK: 2 figures ->", IMG)
