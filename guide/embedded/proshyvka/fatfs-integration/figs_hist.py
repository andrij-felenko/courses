# -*- coding: utf-8 -*-
"""Фігура до вставки «hist-chan-fatfs» (історія FatFs та ChaN).
Окремий від figs.py теми, щоб не чіпати фігури статті-власника.
Запуск:  python figs_hist.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_timeline():
    """Дві паралельні нитки часу: угорі — патенти Microsoft на довгі імена
    (загроза, що згасла), унизу — життя FatFs (проєкт, що ріс)."""
    W, H = 780, 350
    x0, x1 = 60, 560            # осі коротші — праворуч місце для підписів ниток
    y_pat = 130
    y_ff = 232
    p = []

    def xpos(year):
        # 1990 ... 2018 → x0 ... x1 (запас зліва, щоб перша подія не клеїлась до краю)
        return x0 + (year - 1990) / (2018 - 1990) * (x1 - x0)

    # дві осі
    p.append(line(x0, y_pat, x1, y_pat, color=MUTED, sw=2.0))
    p.append(line(x0, y_ff, x1, y_ff, color=MUTED, sw=2.0))

    # роки-орієнтири під нижньою віссю
    for yr in (1995, 2000, 2006, 2013):
        x = xpos(yr)
        p.append(line(x, y_ff + 6, x, y_ff + 11, color=MUTED, sw=1.2))
        p.append(text(x, y_ff + 25, str(yr), size=10.5, color=MUTED))

    # підписи ниток — праворуч від осей, де немає рамок
    p.append(mtext(x1 + 16, y_pat - 4, ["Патенти Microsoft", "на довгі імена (LFN)"],
                   size=11.5, color=POS, anchor="start", bold=True))
    p.append(mtext(x1 + 16, y_ff - 4, ["FatFs — особистий", "проєкт ChaN"],
                   size=11.5, color=NEG, anchor="start", bold=True))

    # події нитки патентів (рамки вгору)
    def pat(year, lbl):
        x = xpos(year)
        p.append(line(x, y_pat - 7, x, y_pat - 24, color=POS, sw=1.2))
        box, _, _ = textbox(x, y_pat - 24 - 18, lbl, size=10.5, color=INK,
                            stroke=POS, fill="#fdecea", pad=6)
        p.append(box)
        p.append(circle(x, y_pat, 5, fill=POS, stroke=POS))

    pat(1993, "1993\nзаявка на LFN")
    pat(2013, "2013\nостанні згасли")

    # події нитки FatFs (рамки вниз)
    def ff(year, lbl):
        x = xpos(year)
        p.append(line(x, y_ff + 7, x, y_ff + 24, color=NEG, sw=1.2))
        box, _, _ = textbox(x, y_ff + 24 + 18, lbl, size=10.5, color=INK,
                            stroke=NEG, fill="#eef2fd", pad=6)
        p.append(box)
        p.append(circle(x, y_ff, 5, fill=NEG, stroke=NEG))

    ff(2006, "2006\nперший випуск\nR0.01")
    ff(2016, "2016\nдодано exFAT")

    render(os.path.join(OUT, "fatfs-timeline.svg"), W, H, *p,
           title="Дві нитки часу: загроза згасла, проєкт ріс")


if __name__ == "__main__":
    fig_timeline()
    print("OK: fatfs-timeline.svg written to", OUT)
