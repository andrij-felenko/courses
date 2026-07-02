# -*- coding: utf-8 -*-
"""Фігури до теми «Адресна дешифрація шини».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Адреса розпадається: старші біти-вибір + молодші біти-комірка ──────────
# Ідея: показати 16 бітів адреси, розрізаних на дві ролі. Старші → дешифратор →
# один ~CS; молодші → прямо в обрану мікросхему. Конкретно: 0x4002.
def fig_address_split():
    W, H = 760, 430
    f = []

    f.append(text(W / 2, 30, "Адреса 0x4002 = 0100 0000 0000 0010", size=18, bold=True))

    # ── рядок бітів ──
    bits = "0100000000000010"          # 0x4002
    n = len(bits)
    bx, by, bw, bh = 70, 60, 38, 40
    for i, b in enumerate(bits):
        x = bx + i * bw
        sel = i < 2                     # A15,A14 — старші два
        fill = "#fde9e7" if sel else "#eaf0fd"
        stroke = POS if sel else NEG
        f.append(rect(x, by, bw, bh, fill=fill, stroke=stroke, sw=2, rx=4))
        f.append(text(x + bw / 2, by + 27, b, size=18, bold=True,
                      color=(POS if sel else NEG)))
        # підпис імені біта (Ak), дрібно, через один
        an = 15 - i
        if i % 2 == 0 or i >= n - 1:
            f.append(text(x + bw / 2, by + bh + 14, "A%d" % an, size=10, color=MUTED))

    # дужки-групи під бітами
    sel_x0, sel_x1 = bx, bx + 2 * bw
    cell_x0, cell_x1 = bx + 2 * bw, bx + n * bw
    yb = by + bh + 26
    f.append(line(sel_x0 + 4, yb, sel_x1 - 4, yb, color=POS, sw=2))
    f.append(line(cell_x0 + 4, yb, cell_x1 - 4, yb, color=NEG, sw=2))
    f.append(text((sel_x0 + sel_x1) / 2, yb + 18, "вибір мікросхеми", size=12,
                  bold=True, color=POS))
    f.append(text((cell_x0 + cell_x1) / 2, yb + 18, "адреса комірки (зміщення 2)",
                  size=12, bold=True, color=NEG))

    # ── гілка «вибір» → дешифратор → ~CS ──
    decx, decy = 120, 250
    bx_sel = (sel_x0 + sel_x1) / 2
    f.append(line(bx_sel, yb + 26, bx_sel, decy - 6, color=POS, sw=2))
    db = fitbox(decx, decy, 150, 60, "дешифратор\nстарших бітів", size=13,
                fill="#fde9e7", stroke=POS, sw=2)
    f.append(db)
    # чотири ~CS виходи, активний — другий (01 = 1)
    cs_x = decx + 150
    for k in range(4):
        cy = decy + 8 + k * 15
        active = (k == 1)
        f.append(line(cs_x, cy, cs_x + 40, cy,
                      color=(FIELD if active else MUTED), sw=(2.4 if active else 1.2)))
        lbl = "~CS%d" % k + (" = 0 (обрано)" if active else "")
        f.append(text(cs_x + 46, cy + 4, lbl, size=11, anchor="start",
                      color=(FIELD if active else MUTED),
                      bold=active))

    # ── гілка «комірка» → у мікросхему ──
    chipx, chipy = 470, 250
    bx_cell = (cell_x0 + cell_x1) / 2
    f.append(line(bx_cell, yb + 26, bx_cell, chipy - 6, color=NEG, sw=2))
    cb = fitbox(chipx, chipy, 220, 90, "обрана мікросхема (01)\n"
                "молодші біти -> комірка\nусередині неї", size=12,
                fill="#eaf0fd", stroke=NEG, sw=2)
    f.append(cb)
    # стрілка ~CS1 у мікросхему
    f.append(arrow(cs_x + 40, decy + 8 + 1 * 15, chipx - 2, chipy + 20, color=FIELD, sw=2))

    f.append(text(W / 2, H - 16,
                  "Старші біти піднімають один ~CS; молодші вибирають комірку в обраній деталі.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "address-split.svg"), W, H, *f)


# ── 2. Повна vs неповна дешифрація: чесна мапа проти тіней ────────────────────
# Ідея: дві колонки адресного простору. Зліва — повна: кожна деталь у своєму
# вікні. Справа — неповна (ігнор старшого біта): мала деталь повторюється тінню.
def fig_foldback():
    W, H = 760, 470
    f = []

    f.append(text(W / 2, 30, "Чесна мапа vs тіні від неповної дешифрації", size=18, bold=True))

    top, bottom = 70, 420
    colw = 150

    def mapcol(x, title, blocks):
        f.append(text(x + colw / 2, top - 14, title, size=14, bold=True))
        # вертикальна шкала адрес
        f.append(line(x - 14, top, x - 14, bottom, color=MUTED, sw=1.2))
        f.append(text(x - 20, top + 6, "0xFFFF", size=9, color=MUTED, anchor="end"))
        f.append(text(x - 20, bottom, "0x0000", size=9, color=MUTED, anchor="end"))
        span = bottom - top
        for (a0, a1, label, fill, stroke, ghost) in blocks:
            # a0,a1 — частки 0..1 знизу простору
            yb = bottom - a1 * span
            yt = bottom - a1 * span  # placeholder
            y_hi = bottom - a1 * span
            y_lo = bottom - a0 * span
            h = y_lo - y_hi
            dash = "5,4" if ghost else None
            f.append(rect(x, y_hi, colw, h, fill=fill, stroke=stroke, sw=2, rx=4))
            sub = mtext(x + colw / 2, (y_hi + y_lo) / 2 + 4, label, size=11,
                        bold=not ghost, color=(MUTED if ghost else INK))
            f.append(sub)

    # ЛІВО — повна дешифрація: 4 чесні вікна, що покривають усе
    left = 90
    mapcol(left, "повна дешифрація", [
        (0.75, 1.00, "мікр. 3", "#eaf0fd", NEG, False),
        (0.50, 0.75, "мікр. 2", "#e7f6ee", FIELD, False),
        (0.25, 0.50, "мікр. 1", "#fdf4e3", "#b9770e", False),
        (0.00, 0.25, "ПЗП",     "#f0eafd", "#6c3fb5", False),
    ])
    f.append(text(left + colw / 2, bottom + 24,
                  "кожна адреса -> рівно одна комірка", size=11, color=MUTED))

    # ПРАВО — неповна: ігноровано старший біт. Мала деталь унизу + її тінь угорі.
    right = 470
    mapcol(right, "неповна (ігнор A15)", [
        (0.50, 1.00, "ТІНЬ тієї самої\nдеталі", "#fdecea", POS, True),
        (0.06, 0.50, "вільно / тіні", "#f7f7f8", MUTED, True),
        (0.00, 0.06, "мікр. (256 Б)", "#fde9e7", POS, False),
    ])
    # стрілка: оригінал -> тінь
    oy = bottom - 0.03 * (bottom - top)
    ty = bottom - 0.75 * (bottom - top)
    f.append(arrow(right + colw + 6, oy, right + colw + 6, ty + 4, color=POS, sw=2))
    f.append(text(right + colw + 14, (oy + ty) / 2, "та сама", size=10,
                  anchor="start", color=POS))
    f.append(text(right + colw + 14, (oy + ty) / 2 + 14, "фізична", size=10,
                  anchor="start", color=POS))
    f.append(text(right + colw + 14, (oy + ty) / 2 + 28, "пам'ять", size=10,
                  anchor="start", color=POS))
    f.append(text(right + colw / 2, bottom + 24,
                  "одна комірка -> багато адрес", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "foldback.svg"), W, H, *f)


if __name__ == "__main__":
    fig_address_split()
    fig_foldback()
    print("OK: figures written to", IMG)
