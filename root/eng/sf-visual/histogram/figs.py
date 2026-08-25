# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── cdf-lut-mapping: вхідна гістограма зі скупченням → S-крива CDF → рівний вихід ──
# Ідея: круту ділянку CDF (де тонів багато) проходять кілька рівнів — вони
# розтягуються на широкий шмат вихідної шкали; пласку ділянку (тонів мало) — стискають.
# Стрілки ведуть вхід 80,120,200 через криву на розтягнуті виходи.

def _hist_shape(t):
    """нормована форма вхідної гістограми: скупчення посередині (t∈[0,1])."""
    g = math.exp(-((t - 0.45) ** 2) / (2 * 0.085 ** 2))      # головний пік
    g += 0.18 * math.exp(-((t - 0.80) ** 2) / (2 * 0.05 ** 2))  # рідкі світлі тони
    return g


def fig_cdf_lut_mapping():
    W, H = 880, 420
    p = []

    # три панелі: ліворуч вхідна гістограма, центр CDF, праворуч вихід
    panel_y, panel_h = 70, 250
    base = panel_y + panel_h

    # --- precompute CDF ---
    NS = 256
    pdf = [_hist_shape(i / float(NS - 1)) for i in range(NS)]
    s = sum(pdf)
    pdf = [x / s for x in pdf]
    cdf = []
    acc = 0.0
    for x in pdf:
        acc += x
        cdf.append(acc)                                       # 0..1, монотонна

    # ── ліва панель: вхідна гістограма ──
    lx, lw = 40, 190
    p.append(text(lx + lw / 2, panel_y - 16, "вхідна гістограма", size=13, bold=True))
    p.append(text(lx + lw / 2, panel_y - 2, "тони скупчені", size=10, color=MUTED))
    p.append(line(lx, base, lx + lw, base, color=INK, sw=1.4))
    mx = max(pdf)
    nb = 64
    for i in range(nb):
        t = i / float(nb - 1)
        hh = pdf[int(t * (NS - 1))] / mx * (panel_h - 16)
        bx = lx + 4 + t * (lw - 8)
        p.append(rect(bx, base - hh, (lw - 8) / nb - 0.5, hh, fill="#94a3b8", stroke="none", sw=0, rx=1))
    p.append(text(lx, base + 16, "0", size=10, color=MUTED, anchor="start"))
    p.append(text(lx + lw, base + 16, "255", size=10, color=MUTED, anchor="end"))

    # ── центральна панель: крива CDF ──
    cx0, cw = 300, 230
    p.append(text(cx0 + cw / 2, panel_y - 16, "крива CDF", size=13, bold=True))
    p.append(text(cx0 + cw / 2, panel_y - 2, "крута там, де тонів багато", size=10, color=MUTED))
    # осі
    p.append(line(cx0, base, cx0 + cw, base, color=INK, sw=1.2))
    p.append(line(cx0, base, cx0, panel_y, color=INK, sw=1.2))
    p.append(text(cx0 + cw / 2, base + 16, "вхід v →", size=10, color=MUTED))
    # пунктир діагоналі (рівномірна CDF для орієнтиру)
    p.append(line(cx0, base, cx0 + cw, panel_y, color=MUTED, sw=1.0, dash="4 4"))
    # сама CDF як ламана
    pts = []
    for i in range(0, NS, 3):
        t = i / float(NS - 1)
        px = cx0 + t * cw
        py = base - cdf[i] * panel_h
        pts.append((px, py))
    poly = " ".join("%.1f,%.1f" % (a, b) for a, b in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, POS))

    # ── права панель: рівний вихід ──
    rx, rw = 600, 190
    rbase = base
    p.append(text(rx + rw / 2, panel_y - 16, "вихід ≈ рівний", size=13, bold=True))
    p.append(text(rx + rw / 2, panel_y - 2, "тони розсунуто", size=10, color=MUTED))
    p.append(line(rx, rbase, rx + rw, rbase, color=INK, sw=1.4))
    nb2 = 64
    for i in range(nb2):
        t = i / float(nb2 - 1)
        # майже рівний з легким частоколом (дискретний дефект)
        jitter = 0.82 + 0.18 * (1 if i % 4 else 0.4)
        hh = jitter * (panel_h - 70)
        bx = rx + 4 + t * (rw - 8)
        p.append(rect(bx, rbase - hh, (rw - 8) / nb2 - 0.5, hh, fill=FIELD, stroke="none", sw=0, rx=1))
    p.append(text(rx, rbase + 16, "0", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + rw, rbase + 16, "255", size=10, color=MUTED, anchor="end"))

    # ── стрілки відображення через CDF: вхід 80,120,200 → вихід ──
    def vmark(v, col):
        t = v / 255.0
        # точка на вході (по осі х лівої панелі)
        ix = lx + 4 + t * (lw - 8)
        # точка на кривій CDF
        cxp = cx0 + t * cw
        cyp = base - cdf[int(t * (NS - 1))] * panel_h
        # вихідне значення = cdf*255 → позиція на правій панелі
        outv = cdf[int(t * (NS - 1))]
        oxp = rx + 4 + outv * (rw - 8)
        # вертикаль входу до кривої, горизонталь кривої до виходу-осі
        p.append(line(cxp, base, cxp, cyp, color=col, sw=1.4, dash="3 3"))
        p.append(line(cxp, cyp, cx0 + cw, cyp, color=col, sw=1.4, dash="3 3"))
        # маркер на кривій
        p.append(circle(cxp, cyp, 3.5, fill=col, stroke="none", sw=0))
        # підпис входу під лівою панеллю
        p.append(text(ix, base + 30, str(v), size=10, color=col, bold=True))
        # стрілка від кривої-виходу до стовпчика правої панелі
        p.append(arrow(cx0 + cw + 4, cyp, rx + outv * (rw - 8) - 2, rbase - 60, color=col, sw=1.6))
        return outv

    vmark(80, POS)
    vmark(120, NEG)
    vmark(200, "#9333ea")

    # підпис формули
    p.append(text(W / 2, H - 12, "H_new(v) = round( CDF(v) · 255 )", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "cdf-lut-mapping.svg"), W, H, *p)


# ── clahe-tiles: сітка тайлів, локальні гістограми з clipLimit, білінійне зшивання ──
# Ідея: кадр ділять на тайли, у кожному своя гістограма; пік над clipLimit зрізають;
# піксель біля межі бере суміш CDF чотирьох сусідніх тайлів (білінійно).

def fig_clahe_tiles():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 26, "CLAHE: тайли · обрізання піку · білінійне зшивання", size=15, bold=True))

    # ── кадр із сіткою тайлів ──
    fx, fy, fw, fh = 40, 60, 330, 330
    cols, rows = 4, 4
    p.append(rect(fx, fy, fw, fh, fill="#eef2f7", stroke=INK, sw=1.6, rx=8))
    tw, th = fw / cols, fh / rows
    for c in range(1, cols):
        p.append(line(fx + c * tw, fy, fx + c * tw, fy + fh, color=MUTED, sw=1.0))
    for r in range(1, rows):
        p.append(line(fx, fy + r * th, fx + fw, fy + r * th, color=MUTED, sw=1.0))
    p.append(text(fx + fw / 2, fy - 12, "кадр поділено на тайли (сітка)", size=11, bold=True))

    # точка-піксель біля стику чотирьох центральних тайлів
    px, py = fx + 2 * tw, fy + 2 * th
    p.append(circle(px, py, 5, fill=POS, stroke=BG, sw=1.5))
    p.append(text(px + 8, py - 8, "піксель", size=10, color=POS, bold=True, anchor="start"))

    # центри 4 сусідніх тайлів навколо пікселя + стрілки (білінійне змішування)
    centers = [(fx + 1.5 * tw, fy + 1.5 * th), (fx + 2.5 * tw, fy + 1.5 * th),
               (fx + 1.5 * tw, fy + 2.5 * th), (fx + 2.5 * tw, fy + 2.5 * th)]
    for cxp, cyp in centers:
        p.append(circle(cxp, cyp, 3, fill=NEG, stroke="none", sw=0))
        p.append(arrow(cxp, cyp, px, py, color=NEG, sw=1.3))
    p.append(text(fx + fw / 2, fy + fh + 20, "піксель = білінійна суміш CDF 4 сусідніх тайлів",
                  size=10, color=NEG))

    # ── праворуч: локальна гістограма тайла з clipLimit ──
    gx, gy, gw, gh = 470, 90, 330, 150
    base = gy + gh
    p.append(text(gx + gw / 2, gy - 14, "локальна гістограма тайла", size=12, bold=True))
    p.append(line(gx, base, gx + gw, base, color=INK, sw=1.3))
    # вузький пік (однорідний тайл) + хвіст
    nb = 48
    clip = gh * 0.5                                           # рівень clipLimit
    peaks = []
    for i in range(nb):
        t = i / float(nb - 1)
        raw = math.exp(-((t - 0.5) ** 2) / (2 * 0.07 ** 2)) * gh * 0.92
        raw += 0.12 * gh
        peaks.append(raw)
    # намалювати зрізану частину (пунктир над clip) і власне стовпчики до clip
    for i in range(nb):
        t = i / float(nb - 1)
        bx = gx + 3 + t * (gw - 6)
        bw = (gw - 6) / nb - 0.5
        raw = peaks[i]
        drawn = min(raw, clip)
        p.append(rect(bx, base - drawn, bw, drawn, fill="#94a3b8", stroke="none", sw=0, rx=1))
        if raw > clip:                                        # зрізана «шапка» — пунктирний контур
            p.append(rect(bx, base - raw, bw, raw - clip, fill="none", stroke=POS, sw=0.8, rx=1))
    # лінія clipLimit
    p.append(line(gx, base - clip, gx + gw, base - clip, color=POS, sw=1.6, dash="6 4"))
    p.append(text(gx + gw, base - clip - 6, "clipLimit", size=10, color=POS, anchor="end", bold=True))
    p.append(text(gx + gw / 2, base + 18, "пік над межею зрізають → розкладають по кошиках",
                  size=10, color=MUTED))

    # ── праворуч-низ: підсумкова думка ──
    by = 300
    box = fitbox(470, by, 330, 120,
                 "Обрізаний пік = стеля крутості CDF\n= стеля підсилення контрасту й шуму.\n"
                 "Тому рівні зони (небо, тло) не «закипають»,\nа локальні деталі все одно проявляються.",
                 size=11, pad=12, fill="#f0f9f4", stroke=FIELD, sw=1.5)
    p.append(box)

    render(os.path.join(OUT, "clahe-tiles.svg"), W, H, *p)


if __name__ == "__main__":
    fig_cdf_lut_mapping()
    fig_clahe_tiles()
    print("figs: cdf-lut-mapping.svg, clahe-tiles.svg")
