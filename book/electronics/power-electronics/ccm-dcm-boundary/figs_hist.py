# -*- coding: utf-8 -*-
"""Фігури до історичної вставки hist-boundary-mode.md
(«Історія ідеї вмикатися рівно в нулі струму котушки»).
Окремий генератор поруч із figs.py — виводить у ту саму теку ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1 (історія). Чому «вмикатися в нулі струму» вбиває відновлення ────
def fig_reverse_recovery():
    """Дві турботи на вмиканні ключа: жорстко (діод ще проводить → сплеск
    зворотного відновлення) проти межового (діод уже в нулі → чисто)."""
    W, H = 760, 420
    f = []
    panels = [
        (40, "Жорстке вмикання (у CCM)", True),
        (410, "Вмикання рівно в нулі (межа)", False),
    ]
    pw = 310
    base = 250          # рівень нуля струму діода
    top = 90
    for x0, ttl, hard in panels:
        x1 = x0 + pw
        f.append(text(x0 + pw / 2, top - 24, ttl, size=14, bold=True))
        # осі
        f.append(line(x0, base, x1, base, color=INK, sw=1.6))
        f.append(text(x0 - 6, base + 4, "0", size=11, color=MUTED, anchor="end"))
        f.append(text(x0 + 4, top - 4, "струм діода", size=11, color=MUTED, anchor="start"))
        xsw = x0 + pw * 0.50     # мить, коли вмикають ключ
        f.append(line(xsw, top + 6, xsw, base + 74, color=MUTED, sw=1.1, dash="4 4"))
        f.append(text(xsw, top + 2, "ключ вмикається", size=10, color=MUTED))
        if hard:
            # струм діода на вмиканні ще ЧИМАЛИЙ → різкий обрив, провал під нуль,
            # зворотний сплеск (Q_rr) і згасальний дзвін
            y_at = base - 92
            f.append(line(x0 + 6, base - 70, xsw, y_at, color=NEG, sw=2.6))
            dip = base + 58
            f.append(line(xsw, y_at, xsw + 9, dip, color=POS, sw=2.8))
            pts = [(xsw + 9, dip)]
            for k in range(1, 50):
                t = k / 49.0
                xx = xsw + 9 + t * (x1 - (xsw + 9))
                yy = base - 24 * math.exp(-4.2 * t) * math.sin(9.5 * t)
                pts.append((xx, yy))
            d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, POS))
            f.append(circle(xsw + 9, dip, 4, fill=POS, stroke=POS))
            b, bw, bh = textbox(x0 + pw / 2, dip + 30, "сплеск Q_rr + дзвін = втрати й завади",
                                size=11, fill="#fdecea", stroke=POS, color="#a5281b")
            f.append(b)
        else:
            # струм діода вже дійшов нуля ДО вмикання → відновлювати нічого
            f.append(line(x0 + 6, base - 82, xsw, base, color=NEG, sw=2.6))
            f.append(circle(xsw, base, 4.5, fill=FIELD, stroke=FIELD))
            f.append(line(xsw, base, x1, base, color=FIELD, sw=2.6))
            b, bw, bh = textbox(x0 + pw / 2, base - 44,
                                ["діод уже в нулі —", "відновлювати нічого"],
                                size=11, fill="#eaf7ef", stroke=FIELD, color="#1e7a43")
            f.append(b)
    render(os.path.join(IMG, 'reverse-recovery.svg'), W, H, *f,
           title="Навіщо вмикатися в нулі струму: діод не встигає «відновитися»")


# ── Фігура 2 (історія). Родовід ідеї «межі» — від Ройєра до валі-світчингу ───
def fig_lineage():
    """Часова нитка однієї думки: самоколивний перетворювач → RCC-flyback на
    межі → контролери CrM/TM PFC → мандат EN 61000-3-2 → квазірезонанс."""
    W, H = 820, 440
    f = []
    ox = 60
    axy = 78
    axx1 = W - 40
    f.append(arrow(ox, axy, axx1, axy, color=INK, sw=2))
    f.append(text(axx1 - 4, axy - 14, "час →", size=13, anchor="end", color=MUTED))
    stops = [
        (0.05, "1954", ["Ройєр і Брайт:", "самоколивний", "перетворювач"], NEG),
        (0.27, "1970-ті", ["RCC — самоколивний", "flyback; сам сидить", "на межі CCM/DCM"], NEG),
        (0.51, "1990-ті", ["контролери CrM / TM:", "MC3426x, L6560/L6561;", "«вмик. у нулі струму»"], POS),
        (0.73, "2001", ["EN 61000-3-2", "робить корекцію PF", "обов'язковою в ЄС"], FIELD),
        (0.93, "далі", ["квазірезонанс:", "валі-світчинг", "у flyback"], POS),
    ]
    for frac, yr, lines, col in stops:
        x = ox + (axx1 - ox - 20) * frac
        f.append(circle(x, axy, 6, fill=col, stroke=col))
        f.append(line(x, axy, x, axy + 30, color=MUTED, sw=1.2, dash="3 3"))
        f.append(text(x, axy - 16, yr, size=12, bold=True, color=col))
        b, bw, bh = textbox(x, axy + 30 + 30, lines, size=10.5,
                            fill=FILL, stroke=col, color=INK)
        f.append(b)
    b, bw, bh = textbox(W / 2, H - 40,
                        ["Наскрізна нитка: щоразу ключ ЧЕКАЄ, поки струм котушки сам дійде нуля,",
                         "і аж тоді вмикається — байдуже, дискретна це схема 1970-х чи мікросхема."],
                        size=12, fill="#fff7ed", stroke="#b45309", color=INK)
    f.append(b)
    render(os.path.join(IMG, 'lineage.svg'), W, H, *f,
           title="Родовід ідеї «межі»: одна думка крізь сім десятиліть")


if __name__ == '__main__':
    fig_reverse_recovery()
    fig_lineage()
    print("history figures written to", IMG)
