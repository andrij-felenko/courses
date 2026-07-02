# -*- coding: utf-8 -*-
"""Фігури до теми «Рівні комірки NAND (SLC/MLC/TLC/QLC)» (цифрова електроніка).
Фігури теми:
  levels-ladder.svg — одне вікно порогової напруги, поділене на 2/4/8/16 рівнів;
                      видно, як звужуються захисні проміжки від SLC до QLC.
  gray-pages.svg    — TLC: 8 станів у коді Ґрея; читання LSB/CSB/MSB потребує 1/2/4
                      опорних напруг; сусідні стани різняться одним бітом.
  tradeoff-bars.svg — та сама площа кристала: ємність росте (1→4 біти), а витривалість
                      і швидкість падають (P/E-цикли, кроки програмування).
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def levels_ladder():
    """Чотири однакові вертикальні смуги — одне й те саме вікно Vt.
    Смугу ділять 2/4/8/16 станів; що більше станів, то тонший проміжок між ними."""
    W, H = 720, 470
    p = []

    configs = [("SLC", 2, "1 біт"), ("MLC", 4, "2 біти"),
               ("TLC", 8, "3 біти"), ("QLC", 16, "4 біти")]

    bx0 = 70          # ліва межа першої смуги
    gap = 165         # крок між смугами
    bw = 74           # ширина смуги
    bt = 70           # верх смуги (менший заряд угорі — вища напруга)
    bb = 400          # низ смуги
    span = bb - bt

    p.append(text(W / 2, 34, "Одне вікно порогової напруги Vt — різна кількість рівнів",
                  size=15, bold=True))

    for i, (name, n, bits) in enumerate(configs):
        cx = bx0 + i * gap + bw / 2
        x = bx0 + i * gap
        # рамка вікна
        p.append(rect(x, bt, bw, span, fill="#f9fafb", stroke=INK, sw=1.6))
        # рівні всередині: n станів → n смужок, між ними n-1 проміжків
        band_h = span / n
        for k in range(n):
            yy = bt + k * band_h
            # заряд наростає донизу: верхній стан «стертий» (світлий), нижні темніші
            shade = int(240 - (k / max(1, n - 1)) * 150)
            fill = "#%02x%02x%02x" % (shade, shade, min(255, shade + 8))
            p.append(rect(x + 3, yy + 1.2, bw - 6, band_h - 2.4, fill=fill,
                          stroke="#9aa3ad", sw=0.7, rx=2))
        # підпис зверху
        word = "стани" if n in (2, 4) else "станів"
        p.append(text(cx, bt - 26, name, size=15, bold=True, color=POS if n >= 8 else INK))
        p.append(text(cx, bt - 10, "%d %s · %s" % (n, word, bits), size=11, color=MUTED))
        # позначка проміжку між станами
        margin_px = band_h
        p.append(text(cx, bb + 22, "проміжок", size=10, color=MUTED))
        p.append(text(cx, bb + 37, "%.0f%%" % (100.0 / n), size=11, bold=True,
                      color=POS if n >= 8 else INK))

    # вісь напруги ліворуч
    p.append(line(bx0 - 24, bt, bx0 - 24, bb, color=INK, sw=1.4))
    p.append(text(bx0 - 40, bt + 6, "стерто", size=10, color=MUTED, anchor="end"))
    p.append(text(bx0 - 40, bb, "заряд↑", size=10, color=MUTED, anchor="end"))
    p.append(text(bx0 - 52, (bt + bb) / 2, "Vt", size=13, bold=True, color=MUTED, anchor="end"))

    box, bwd, bhd = textbox(W / 2, 448,
                            "Однакова висота вікна ділиться на все більше рівнів — margin тане",
                            size=11, color=INK, fill="#fff8e6", stroke="#e0b400")
    p.append(box)

    render(os.path.join(OUT, "levels-ladder.svg"), W, H, *p)


def gray_pages():
    """TLC: 8 станів по осі Vt, підписані кодом Ґрея (сусіди різняться 1 бітом).
    Три рядки читання: LSB (1 опорна), CSB (2 опорні), MSB (4 опорні)."""
    W, H = 720, 500
    p = []

    # відбитий код Ґрея g(i)=i^(i>>1) для станів 0..7 (сусіди різняться 1 бітом).
    # У ньому лівий біт перемикається 1 раз (1 опорна), середній — 2 рази, правий — 4 рази.
    codes = ["000", "001", "011", "010", "110", "111", "101", "100"]
    labels = ["E", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]

    x0 = 70
    x1 = 650
    axis_y = 120
    n = 8
    dx = (x1 - x0) / n

    p.append(text(W / 2, 32, "TLC: 8 рівнів заряду = 3 біти (код Ґрея)", size=15, bold=True))

    # вісь Vt
    p.append(line(x0, axis_y, x1 + 10, axis_y, color=INK, sw=1.6))
    p.append(text(x1 + 8, axis_y + 20, "Vt →", size=12, color=MUTED, anchor="end"))

    # «горби» станів + підписи
    peak = 46
    for k in range(n):
        cx = x0 + (k + 0.5) * dx
        # схематичний дзвін розподілу
        pts = []
        for t in range(-14, 15):
            xx = cx + t * (dx * 0.34) / 14
            yy = axis_y - peak * math.exp(-(t / 6.0) ** 2)
            pts.append("%.1f,%.1f" % (xx, yy))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (" ".join(pts), NEG if k == 0 else INK))
        p.append(text(cx, axis_y - peak - 8, codes[k], size=12, bold=True,
                      color=NEG if k == 0 else INK))
        p.append(text(cx, axis_y + 18, labels[k], size=11, color=MUTED))

    # опорні напруги між сусідніми станами (7 границь)
    for k in range(1, n):
        xb = x0 + k * dx
        p.append(line(xb, axis_y - peak - 22, xb, axis_y + 6, color="#c9ccd1",
                      sw=0.9, dash="3 3"))

    # три рядки читання сторінок
    def read_row(y, title, ref_indices, color):
        p.append(text(x0 - 8, y, title, size=12, bold=True, color=color, anchor="end"))
        p.append(line(x0, y, x1, y, color="#dfe3e8", sw=1.0))
        for idx in ref_indices:
            xb = x0 + idx * dx
            p.append(line(xb, y - 12, xb, y + 12, color=color, sw=2.4))
            p.append(circle(xb, y, 3.2, fill=color, stroke=color, sw=1))

    read_row(230, "сторінка A", [4], POS)
    read_row(300, "сторінка B", [2, 6], FIELD)
    read_row(370, "сторінка C", [1, 3, 5, 7], NEG)

    p.append(text(x1, 230 - 26, "1 опорна напруга", size=11, color=POS, anchor="end"))
    p.append(text(x1, 300 - 26, "2 опорні напруги", size=11, color=FIELD, anchor="end"))
    p.append(text(x1, 370 - 26, "4 опорні напруги", size=11, color=NEG, anchor="end"))

    box, bwd, bhd = textbox(W / 2, 452,
                            "Сусіди різняться 1 бітом → похибка на одну сходинку псує лише 1 біт",
                            size=11, color=INK, fill="#eef7ef", stroke=FIELD)
    p.append(box)

    render(os.path.join(OUT, "gray-pages.svg"), W, H, *p)


def tradeoff_bars():
    """Три пари стовпчиків: ємність (біти/комірку) вгору, витривалість (P/E) і
    кроки програмування — вниз/умовно. Показує компроміс щільність↔надійність."""
    W, H = 720, 430
    p = []

    names = ["SLC", "MLC", "TLC", "QLC"]
    bits = [1, 2, 3, 4]
    pe = [100000, 10000, 3000, 1000]      # типові P/E-цикли (порядок величини)

    p.append(text(W / 2, 32, "Той самий кристал: більше бітів — менше циклів", size=15, bold=True))

    # ── ліва панель: біти на комірку ──
    lx = 70
    base_y = 330
    col_w = 46
    step = 82
    maxbits = 4
    hpx = 210
    p.append(text(lx + 1.5 * step, 66, "ємність (біти / комірку)", size=12, bold=True, color=FIELD))
    p.append(line(lx - 14, base_y, lx + 3 * step + col_w + 14, base_y, color=INK, sw=1.4))
    for i, (nm, b) in enumerate(zip(names, bits)):
        x = lx + i * step
        h = hpx * b / maxbits
        p.append(rect(x, base_y - h, col_w, h, fill="#dff3e6", stroke=FIELD, sw=1.6))
        p.append(text(x + col_w / 2, base_y - h - 8, "%d" % b, size=13, bold=True, color=FIELD))
        p.append(text(x + col_w / 2, base_y + 18, nm, size=12, bold=True))

    # ── права панель: P/E-цикли (лог-шкала) ──
    rx = 400
    p.append(text(rx + 1.5 * step, 66, "витривалість (P/E, лог)", size=12, bold=True, color=POS))
    p.append(line(rx - 14, base_y, rx + 3 * step + col_w + 14, base_y, color=INK, sw=1.4))
    # лог-масштаб: log10(pe) від 3..5 → висота
    for i, (nm, cyc) in enumerate(zip(names, pe)):
        x = rx + i * step
        h = hpx * (math.log10(cyc) - 2.5) / (5.0 - 2.5)
        p.append(rect(x, base_y - h, col_w, h, fill="#fde6e2", stroke=POS, sw=1.6))
        lbl = "%dk" % (cyc // 1000) if cyc >= 1000 else "%d" % cyc
        p.append(text(x + col_w / 2, base_y - h - 8, lbl, size=12, bold=True, color=POS))
        p.append(text(x + col_w / 2, base_y + 18, nm, size=12, bold=True))

    box, bwd, bhd = textbox(W / 2, 392,
                            "Щільність і надійність тягнуть у різні боки — тому й співіснують усі чотири",
                            size=11, color=INK, fill="#fff8e6", stroke="#e0b400")
    p.append(box)

    render(os.path.join(OUT, "tradeoff-bars.svg"), W, H, *p)


if __name__ == "__main__":
    levels_ladder()
    gray_pages()
    tradeoff_bars()
    print("OK: figs written to", OUT)
