# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Родина Raspberry Pi».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Мапа серій: за яким принципом родина ділиться на лінійки ────────────────
def fig_series_map():
    W, H = 940, 560
    f = [text(W / 2, 30, "Одна родина — чотири серії за призначенням, не за «крутістю»",
              size=15, bold=True)]

    # чотири колонки-серії; кожна — заголовок + що визначає + приклади
    cols = [
        ("Flagship", NEG, "#eef2f8",
         "повний Linux,\nкредитна картка",
         ["Pi 1 · 2 · 3", "Pi 4 · Pi 5", "Pi 400/500", "(клавіатура)"]),
        ("Zero", FIELD, "#eef6ef",
         "той самий Linux,\nмалий і дешевий",
         ["Zero", "Zero W", "Zero 2 W", "низьке живл."]),
        ("Compute\nModule", "#8e44ad", "#f3ecf8",
         "Linux-модуль\nу свою плату",
         ["CM3 · CM4", "CM5", "SO-DIMM /", "роз'єми"]),
        ("Pico", POS, "#fdecea",
         "НЕ Linux —\nмікроконтролер",
         ["Pico", "Pico W", "Pico 2", "чип RP2040"]),
    ]

    n = len(cols)
    gap = 24
    cw = (W - 2 * 40 - (n - 1) * gap) / n
    x0 = 40
    top = 70
    ch = 340

    for i, (name, accent, fill, defn, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(rect(x, top, cw, ch, fill=fill, stroke=accent, sw=2.0, rx=12))
        # заголовок серії (може бути 2 рядки)
        f.append(mtext(x + cw / 2, top + 30, name, size=15, bold=True, color=accent, lh=1.15))
        f.append(line(x + 16, top + 66, x + cw - 16, top + 66, color=accent, sw=1.2))
        # що ВИЗНАЧАЄ серію
        f.append(mtext(x + cw / 2, top + 92, defn, size=10.5, color=INK, lh=1.35))
        # приклади моделей
        iy = top + 160
        for it in items:
            f.append(text(x + cw / 2, iy, it, size=10.5, color=MUTED))
            iy += 26

    # нижній підсумок про вісь вибору
    b, _, _ = textbox(W / 2, top + ch + 55,
                      "серію обирають за ЗАДАЧЕЮ (комп'ютер / малий комп'ютер / вбудований модуль / мікроконтролер),\n"
                      "а число всередині серії (2, 4, 5) — це вже покоління-швидкість",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "series-map.svg"), W, H, *f)


# ── 2. Часова смуга флагманів: як росли покоління (SoC, ядро, частота) ─────────
def fig_flagship_timeline():
    W, H = 960, 470
    f = [text(W / 2, 30, "Флагманська лінійка: кожне покоління — нове ядро й більше сили",
              size=15, bold=True)]

    # горизонтальна вісь років
    axis_y = 150
    x_lo, x_hi = 70, W - 70
    f.append(line(x_lo, axis_y, x_hi, axis_y, color=MUTED, sw=1.6))

    # п'ять флагманських віх; кожна — рік, назва, SoC/ядро, частота
    gens = [
        ("2012", "Pi 1",  "BCM2835",  "1×ARM11",       "700 МГц"),
        ("2015", "Pi 2",  "BCM2836",  "4×Cortex-A7",   "900 МГц"),
        ("2016", "Pi 3",  "BCM2837",  "4×Cortex-A53",  "1.2 ГГц"),
        ("2019", "Pi 4",  "BCM2711",  "4×Cortex-A72",  "1.5–1.8 ГГц"),
        ("2023", "Pi 5",  "BCM2712",  "4×Cortex-A76",  "2.4 ГГц"),
    ]
    n = len(gens)
    step = (x_hi - x_lo) / (n - 1)
    accents = [MUTED, FIELD, NEG, "#8e44ad", POS]

    for i, (yr, name, soc, core, clk) in enumerate(gens):
        cx = x_lo + i * step
        accent = accents[i]
        # точка на осі + рік під нею
        f.append(circle(cx, axis_y, 7, fill=accent, stroke=accent, sw=1.5))
        f.append(text(cx, axis_y + 26, yr, size=12, bold=True, color=accent))
        # картка над віссю: назва + SoC + ядро + частота
        bw, bh = 150, 78
        bx = cx - bw / 2
        by = axis_y - 20 - bh
        f.append(rect(bx, by, bw, bh, fill=BG, stroke=accent, sw=1.8, rx=9))
        f.append(text(cx, by + 20, name, size=13, bold=True, color=accent))
        f.append(text(cx, by + 38, soc, size=10, color=INK))
        f.append(text(cx, by + 54, core, size=10, color=INK))
        f.append(text(cx, by + 70, clk, size=10, color=MUTED))
        # з'єднати картку з віссю
        f.append(line(cx, by + bh, cx, axis_y - 7, color=accent, sw=1.2, dash="3,3"))

    # пояснення внизу: що НЕ змінюється, а що зростає
    b1, _, _ = textbox(280, 360,
                       "Спадкоємність: та сама 40-пін\n"
                       "гребінка й Raspberry Pi OS —\n"
                       "стара периферія й код живуть далі.",
                       size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    b2, _, _ = textbox(690, 360,
                       "Що росте з поколінням: ядра ARM\n"
                       "(11 → A7 → A53 → A72 → A76),\n"
                       "частота, пам'ять, швидкість портів.",
                       size=10.5, fill="#eef2f8", stroke=NEG)
    f.append(b2)
    render(os.path.join(IMG, "flagship-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_series_map()
    fig_flagship_timeline()
    print("OK: 2 figures ->", IMG)
