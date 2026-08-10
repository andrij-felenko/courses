# -*- coding: utf-8 -*-
"""Фігури до теми «Шина PCI в Linux: конфігураційний простір, BAR, драйвери»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG = "#eaf0fd"
GREEN_BG = "#e6f5ec"
WARM_BG = "#fff4e0"
GREY_BG = "#eef0f3"


# ── 1. Мапа заголовка Type 0: перші 64 байти ────────────────────────────────
def fig_config_space():
    W, H = 1080, 660

    OFF_X, OFF_W = 40, 92
    COL_X, COL_W = 140, 222
    ROW_H = 32
    TOP = 96

    def cx(i):
        return COL_X + i * COL_W

    def span(i0, i1):
        """x і ширина від колонки i0 до колонки i1 включно."""
        return cx(i0), (i1 - i0 + 1) * COL_W

    P = [text(W / 2, 44, "Кожен рядок — 32-бітне слово; ліворуч старші біти, праворуч молодші",
              size=14, color=MUTED)]

    # шапка таблиці
    P.append(fitbox(OFF_X, 60, OFF_W, ROW_H, "Зсув", size=13, bold=True, fill=GREY_BG))
    heads = ["Байт 3\nбіти 31–24", "Байт 2\nбіти 23–16", "Байт 1\nбіти 15–8", "Байт 0\nбіти 7–0"]
    for i, h in enumerate(heads):
        P.append(fitbox(cx(i), 60, COL_W, ROW_H, h, size=11, bold=True, fill=GREY_BG))

    # рядки: (зсув, [(i0, i1, напис, заливка), …])
    N, W_, G, B = None, WARM_BG, GREEN_BG, BLUE_BG
    rows = [
        ("0x00", [(0, 1, "Device ID", W_), (2, 3, "Vendor ID", W_)]),
        ("0x04", [(0, 1, "Status", B), (2, 3, "Command", B)]),
        ("0x08", [(0, 0, "Class Code", W_), (1, 1, "Subclass", W_),
                  (2, 2, "Prog IF", W_), (3, 3, "Revision ID", N)]),
        ("0x0C", [(0, 0, "BIST", N), (1, 1, "Header Type", N),
                  (2, 2, "Latency Timer", N), (3, 3, "Cache Line Size", N)]),
        ("0x10", [(0, 3, "Base Address Register 0  (BAR0)", G)]),
        ("0x14", [(0, 3, "Base Address Register 1  (BAR1)", G)]),
        ("0x18", [(0, 3, "Base Address Register 2  (BAR2)", G)]),
        ("0x1C", [(0, 3, "Base Address Register 3  (BAR3)", G)]),
        ("0x20", [(0, 3, "Base Address Register 4  (BAR4)", G)]),
        ("0x24", [(0, 3, "Base Address Register 5  (BAR5)", G)]),
        ("0x28", [(0, 3, "Cardbus CIS Pointer", N)]),
        ("0x2C", [(0, 1, "Subsystem ID", N), (2, 3, "Subsystem Vendor ID", N)]),
        ("0x30", [(0, 3, "Expansion ROM Base Address", N)]),
        ("0x34", [(0, 2, "зарезервовано", N), (3, 3, "Capabilities Ptr", N)]),
        ("0x38", [(0, 3, "зарезервовано", N)]),
        ("0x3C", [(0, 0, "Max Latency", N), (1, 1, "Min Grant", N),
                  (2, 2, "Interrupt Pin", N), (3, 3, "Interrupt Line", N)]),
    ]

    for r, (off, cells) in enumerate(rows):
        y = TOP + r * ROW_H
        P.append(fitbox(OFF_X, y, OFF_W, ROW_H, off, size=12, bold=True, fill=GREY_BG))
        for i0, i1, label, fill in cells:
            x, w = span(i0, i1)
            P.append(fitbox(x, y, w, ROW_H, label, size=12,
                            fill=fill if fill else "#ffffff"))

    return render(os.path.join(OUT, "pci-config-space.svg"), W, H, *P,
                  title="Заголовок Type 0: обов'язкові перші 64 байти")


# ── 2. Як BAR перетворюється на вікно у фізичній пам'яті ────────────────────
def fig_bar_mapping():
    W, H = 1240, 620

    P = [text(W / 2, 46, "BAR не зберігає адресу від виробника — він оголошує ЗАПИТ на розмір",
              size=15, color=MUTED)]

    LX, LW = 50, 620
    step_h = 96

    P.append(fitbox(LX, 80, LW, 34, "Що робить ядро під час перелічення",
                    size=14, bold=True, fill=GREY_BG, stroke=LINE, sw=2))

    steps = [
        ("1. Ядро записує в BAR0 усі одиниці",
         "0xFFFFFFFF → BAR0", BLUE_BG),
        ("2. Читає назад — пристрій повернув маску",
         "BAR0 → 0xFFFE0000    молодші 17 бітів нульові", WARM_BG),
        ("3. Обчислює розмір, шукає вільне місце й пише базу",
         "2¹⁷ байтів = 131072 = 128 КБ    →    0xE1200000 → BAR0", GREEN_BG),
    ]
    step_h = 128
    for i, (head, formula, fill) in enumerate(steps):
        y = 130 + i * step_h
        P.append(fitbox(LX, y, LW, 92, head + "\n" + formula, size=13, fill=fill))
        if i < len(steps) - 1:
            P.append(arrow(LX + LW / 2, y + 92, LX + LW / 2, y + step_h - 2))

    # фізичний адресний простір процесора
    RX, RW = 760, 430
    P.append(fitbox(RX, 80, RW, 34, "Фізичний адресний простір процесора",
                    size=14, bold=True, fill=GREY_BG, stroke=LINE, sw=2))
    P.append(fitbox(RX, 130, RW, 96, "0x00000000 – …\nоперативна пам'ять", size=13, fill=GREY_BG))
    P.append(fitbox(RX, 238, RW, 60, "дірка: не відповідає ніхто", size=13, fill="#ffffff"))
    P.append(fitbox(RX, 310, RW, 96,
                    "0xE1200000 – 0xE121FFFF\nвікно BAR0 цього пристрою (128 КБ)",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2.4))
    P.append(fitbox(RX, 418, RW, 60, "вікна інших пристроїв", size=13, fill="#ffffff"))

    P.append(arrow(LX + LW, 358, RX, 358, color=FIELD, sw=2.4))

    P.append(fitbox(RX - 60, 508, RW + 120, 72,
                    "Відтепер звертання процесора за цією адресою\n"
                    "контролер пам'яті направляє на шину PCI саме цьому пристрою",
                    size=13, fill=BLUE_BG))

    return render(os.path.join(OUT, "pci-bar-mapping.svg"), W, H, *P,
                  title="Від запиту в BAR до вікна у фізичній пам'яті")


if __name__ == "__main__":
    fig_config_space()
    fig_bar_mapping()
    print("ok")
