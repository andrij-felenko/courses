# -*- coding: utf-8 -*-
"""Фігури до теми «Режими сну».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори щаблів (від «легкого» до «глибокого»), узгоджені з палітрою svgkit
ACT = ("#fdecea", "#c0392b")   # active — гаряче
MOD = ("#fdf2e9", "#e67e22")   # modem
LGT = ("#e8f8f7", "#1a7a73")   # light
DEP = ("#d6eaf8", "#2457d6")   # deep
HIB = ("#f5eef8", "#8e44ad")   # hibernation


# ── Драбина сну: що глибше, то менший струм, але дорожче прокидання ───────────
def fig_sleep_ladder():
    W, H = 820, 430
    title = "Драбина сну ESP32: глибше = менший струм, але дорожче прокидання"

    rows = [
        ("ACTIVE",      "струм: ~95–240 мА", "живе: всі ядра + радіо + SRAM",         ACT, "повний",        FIELD),
        ("MODEM-SLEEP", "струм: ~20–68 мА",  "живе: ядра + SRAM; радіо спить між TX",  MOD, "повний",        FIELD),
        ("LIGHT-SLEEP", "струм: ~0.8 мА",    "живе: SRAM ціла; такти ядер стоять; RTC", LGT, "зберігається", FIELD),
        ("DEEP-SLEEP",  "струм: ~6–10 мкА",  "живе: лише RTC-домен + ULP",             DEP, "перезапуск!",   POS),
        ("HIBERNATION", "струм: ~5 мкА",     "живе: тільки RTC-таймер",                HIB, "перезапуск!",   POS),
    ]

    f = [text(W / 2, 26, title, size=17, bold=True)]
    # сходинки зі зростаючим відступом ліворуч (драбина вглиб)
    top = 55
    rh = 62
    gap = 0
    full_w = 600
    for i, (name, cur, live, (fill, stroke), tag, tagc) in enumerate(rows):
        x = 100 + i * 18
        w = full_w - i * 18
        y = top + i * (rh + gap)
        f.append(rect(x, y, w, rh, fill=fill, stroke=stroke, sw=2.5))
        f.append(text(x + 12, y + 22, name, size=14, color=stroke, anchor="start", bold=True))
        f.append(text(x + 12, y + 40, cur, size=11, color=INK, anchor="start"))
        f.append(text(x + 12, y + 54, live, size=10, color=MUTED, anchor="start"))
        f.append(text(688, y + 34, tag, size=12, color=tagc, anchor="end", bold=True))

    # стрілка «менший струм» вниз уздовж драбини
    ax = 215
    f.append(line(ax, top, ax, top + len(rows) * rh - 8, color=MUTED, sw=2.0))
    f.append(arrow(ax, top, ax, top + len(rows) * rh - 8, color=MUTED, sw=2.0))
    f.append(mtext(ax + 12, top + (len(rows) * rh) / 2 - 6, "менший\nструм", size=11, color=MUTED, anchor="start"))

    box, bw, bh = textbox(W / 2, top + len(rows) * rh + 16,
                          "Що глибше — то менший струм, але то більше вимкнено і то дорожче прокидання",
                          size=11, fill="#f0f0f0", stroke=MUTED, sw=1.2, pad=8)
    f.append(box)
    render(os.path.join(IMG, "sleep-ladder.svg"), W, H, *f)


# ── Порівняння режимів: струм, що живе, час і характер прокидання ─────────────
def fig_sleep_compare():
    W, H = 800, 300
    title = "Порівняння режимів сну: струм, що живе, прокидання"

    cols = [("Режим", 20, 140), ("Струм", 164, 110), ("Що живе", 278, 200),
            ("Час прокидання", 482, 140), ("Характер старту", 626, 165)]

    rows = [
        ("MODEM-\nSLEEP", "~20–68 мА",  "ядра + SRAM\nрадіо спить",  "мікросекунди", "продовження",            MOD, False),
        ("LIGHT-\nSLEEP", "~0.8 мА",    "SRAM + RTC\nтакти стоять",  "мікросекунди", "продовження\n(«пауза»)", LGT, False),
        ("DEEP-\nSLEEP",  "~6–10 мкА",  "RTC-домен\n+ ULP",          "мс (boot)",    "ПЕРЕЗАПУСК\nз app_main()", DEP, True),
        ("HIBER-\nNATION","~5 мкА",     "RTC-таймер\n(мінімум)",     "мс (boot)",    "ПЕРЕЗАПУСК\nз app_main()", HIB, True),
    ]

    f = [text(W / 2, 26, title, size=17, bold=True)]
    # шапка
    hy = 40
    for label, x, w in cols:
        f.append(fitbox(x, hy, w, 32, label, size=13, bold=True, fill="#f0f0f0", stroke=MUTED, sw=1.5))

    # рядки впритул під шапкою
    ry = hy + 36
    rh = 56
    for ri, (name, cur, live, t, start, (fill, stroke), restart) in enumerate(rows):
        y = ry + ri * rh
        cells = [(name, stroke, True), (cur, INK, False), (live, INK, False), (t, INK, False)]
        for (txt, col, bold), (_, cx, cw) in zip(cells, cols[:4]):
            f.append(fitbox(cx, y, cw, rh, txt, size=11, color=col, bold=bold, fill=fill, stroke=stroke, sw=1.8))
        # остання колонка — перезапуск підсвічуємо червоним
        sf, ss = (ACT if restart else (fill, stroke))
        scol = POS if restart else INK
        f.append(fitbox(cols[4][1], y, cols[4][2], rh, start, size=11, color=scol, bold=restart,
                        fill=sf, stroke=ss, sw=1.8))

    render(os.path.join(IMG, "sleep-compare.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sleep_ladder()
    fig_sleep_compare()
    print("OK: sleep-ladder.svg, sleep-compare.svg")
