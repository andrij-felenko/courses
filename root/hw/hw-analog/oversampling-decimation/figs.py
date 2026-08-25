# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Та сама потужність шуму, але розмазана по ширшій смузі ────────────────
def fig_spread():
    W, H = 780, 360
    f = []
    baseY = H - 70
    axW = 300
    gap = 80
    x0L = 60
    x0R = x0L + axW + gap
    topH = 210  # висота області

    def panel(x0, fmax_label, band_frac, area_h, title):
        out = []
        out.append(line(x0, baseY, x0 + axW, baseY, color=INK, sw=2))
        out.append(line(x0, baseY, x0, baseY - topH, color=INK, sw=2))
        out.append(arrow(x0 + axW - 2, baseY, x0 + axW + 16, baseY, color=INK, sw=2))
        out.append(text(x0 + axW / 2, baseY + 34, "частота", size=13, color=MUTED))
        out.append(text(x0 + axW + 8, baseY + 20, fmax_label, size=12, color=MUTED, anchor="end"))
        # сіра пелена шуму на всю смугу — ОДНАКОВА ПЛОЩА (потужність) в обох
        noise_top = baseY - area_h
        out.append(rect(x0, noise_top, axW, area_h, fill="#e9edf2", stroke="#cfd6de", sw=1, rx=0))
        out.append(text(x0 + axW / 2, noise_top - 8, "та сама повна потужність шуму",
                        size=11, color=MUTED))
        # смуга корисного сигналу — зелена, ОДНАКОВОЇ ширини в px (бо смуга сигналу не змінюється)
        bw = axW * band_frac
        out.append(rect(x0, baseY - topH + 4, bw, topH - 4, fill="#eafaf1",
                        stroke=FIELD, sw=1.6, rx=0))
        out.append(line(x0 + bw, baseY, x0 + bw, baseY - topH, color=FIELD, sw=1.6, dash="4,4"))
        out.append(text(x0 + bw / 2, baseY - topH + 22, "смуга", size=12, color=FIELD, bold=True))
        out.append(text(x0 + bw / 2, baseY - topH + 38, "сигналу", size=12, color=FIELD, bold=True))
        out.append(text(x0 + axW / 2, baseY - topH - 14, title, size=14, color=INK, bold=True))
        return out, bw, noise_top

    pL, bwL, ntL = panel(x0L, "fs/2", 0.62, 150, "Знімаємо ледь-ледь швидше")
    pR, bwR, ntR = panel(x0R, "K·fs/2", 0.62 / 4, 150 / 4, "Знімаємо ×K частіше")
    f += pL + pR

    f.append(text(x0R + bwR / 2 + 6, H - 18,
                  "у смузі сигналу шуму поменшало в K разів", size=11, color=FIELD,
                  anchor="start"))
    render(os.path.join(IMG, "spread.svg"), W, H, *f)


# ── 2. Ланцюг: швидкий АЦП → фільтр НЧ → проріджування ÷K ────────────────────
def fig_chain():
    W, H = 800, 250
    f = []
    cy = 105
    boxes = [
        ("Швидкий АЦП\nK·fs знімків/с", FILL, INK),
        ("Цифровий\nфільтр НЧ\n(усереднення)", "#eafaf1", FIELD),
        ("Проріджування\n÷K\n(беремо 1 з K)", FILL, INK),
    ]
    xs = [140, 410, 670]
    bw = []
    for (x, (s, fill, col)) in zip(xs, boxes):
        b, w, h = textbox(x, cy, s, size=13, pad=12, fill=fill, stroke=col, sw=2.0, color=INK)
        bw.append((x, w))
        f.append(b)
    f.append(arrow(xs[0] + bw[0][1] / 2, cy, xs[1] - bw[1][1] / 2, cy, color=INK, sw=2))
    f.append(arrow(xs[1] + bw[1][1] / 2, cy, xs[2] - bw[2][1] / 2, cy, color=INK, sw=2))
    f.append(text((xs[0] + xs[1]) / 2, cy - 46, "багато сирих", size=11, color=MUTED))
    f.append(text((xs[0] + xs[1]) / 2, cy - 33, "відліків", size=11, color=MUTED))
    f.append(text((xs[1] + xs[2]) / 2, cy - 46, "шум поза", size=11, color=MUTED))
    f.append(text((xs[1] + xs[2]) / 2, cy - 33, "смугою зрізано", size=11, color=MUTED))
    f.append(arrow(46, cy, xs[0] - bw[0][1] / 2, cy, color=MUTED, sw=2))
    f.append(text(50, cy - 14, "аналог", size=11, color=MUTED, anchor="start"))
    f.append(arrow(xs[2] + bw[2][1] / 2, cy, W - 26, cy, color=MUTED, sw=2))
    f.append(text(W - 32, cy - 16, "чисті дані", size=11, color=MUTED, anchor="end"))
    f.append(text(W - 32, cy - 3, "на fs", size=11, color=MUTED, anchor="end"))
    f.append(text(W / 2, H - 20,
                  "Фільтр — ПЕРЕД проріджуванням: інакше відкинутий шум складеться назад у смугу (аліасинг)",
                  size=11, color=POS))
    render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── 3. Усереднення працює лише коли шум хитає сигнал через щабель ────────────
def fig_dither():
    W, H = 800, 360
    f = []
    x0, y0 = 80, 48
    plotW, plotH = 600, 230
    baseY = y0 + plotH
    levels = [0.0, 1.0, 2.0]
    lvlY = {v: baseY - (v + 0.4) / 2.8 * plotH for v in levels}
    for v in levels:
        yy = lvlY[v]
        f.append(line(x0, yy, x0 + plotW, yy, color="#cfd6de", sw=1.2, dash="3,4"))
        f.append(text(x0 - 12, yy + 4, "щабель %d" % int(v), size=11, color=MUTED, anchor="end"))
    # справжня напруга ≈ 1.33 щабля — між рівнями, не на щаблі
    true_v = 1.33
    trueY = baseY - (true_v + 0.4) / 2.8 * plotH
    f.append(line(x0, trueY, x0 + plotW, trueY, color=FIELD, sw=2.4))
    f.append(text(x0 + plotW + 8, trueY - 6, "справжня", size=12, color=FIELD,
                  anchor="start", bold=True))
    f.append(text(x0 + plotW + 8, trueY + 10, "напруга", size=12, color=FIELD,
                  anchor="start", bold=True))
    # 12 знімків: шум перекидає їх між щаблями 1 і 2; 8×1 + 4×2 → середнє = 1.33
    pattern = [1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1]
    N = len(pattern)
    sx = plotW / (N + 1)
    pts = []
    for i, p in enumerate(pattern):
        px = x0 + (i + 1) * sx
        py = lvlY[float(p)]
        pts.append((px, py))
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=NEG, sw=1.0, dash="2,3"))
    for (px, py) in pts:
        f.append(circle(px, py, 5, fill=NEG, stroke=NEG))
    f.append(line(x0, baseY, x0 + plotW, baseY, color=INK, sw=1.8))
    f.append(arrow(x0 + plotW, baseY, x0 + plotW + 16, baseY, color=INK, sw=1.8))
    f.append(text(x0 + plotW / 2, baseY + 28, "знімки в часі (×K частіше)", size=12, color=MUTED))
    f.append(fitbox(x0 + 24, y0 + 4, 330, 48,
                    "Середнє 12 знімків = 1.33 щабля — точніше за сам крок",
                    size=12, pad=8, fill="#eafaf1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "dither.svg"), W, H, *f)


# ── 4. Кільцевий буфер: ковзне вікно оновлюється за один рух ─────────────────
def fig_ring():
    W, H = 800, 470
    f = []
    cx, cy = 250, 250
    R = 128
    N = 8                      # 8 комірок кільця
    import math
    # позиції комірок по колу
    cells = []
    for i in range(N):
        a = -math.pi / 2 + i * 2 * math.pi / N
        px = cx + R * math.cos(a)
        py = cy + R * math.sin(a)
        cells.append((px, py, a))
    # значення у комірках (сирі 12-бітні відліки, умовно)
    vals = [2048, 2051, 2049, 2047, 2052, 2050, 2048, 2053]
    head = 0                   # куди пишемо новий; звідти ж «випадає» найстаріший
    for i, (px, py, a) in enumerate(cells):
        fill = "#fdecea" if i == head else FILL
        strk = POS if i == head else LINE
        f.append(circle(px, py, 26, fill=fill, stroke=strk, sw=2.2 if i == head else 1.6))
        f.append(text(px, py + 5, str(vals[i]), size=13, color=INK, bold=(i == head)))
        # індекс комірки назовні
        lx = cx + (R + 40) * math.cos(a)
        ly = cy + (R + 40) * math.sin(a) + 4
        f.append(text(lx, ly, "[%d]" % i, size=11, color=MUTED))
    # стрілка руху голови (за годинниковою)
    a0 = cells[head][2]
    f.append(text(cx, cy - 6, "running_sum", size=13, color=FIELD, bold=True))
    f.append(text(cx, cy + 14, "= Σ усіх 8", size=13, color=FIELD))
    # вхідна стрілка: новий відлік → у комірку head
    hx, hy, ha = cells[head]
    f.append(arrow(hx, hy - 90, hx, hy - 30, color=POS, sw=2.2))
    f.append(text(hx, hy - 98, "новий 2054", size=12, color=POS, bold=True))
    # права колонка — формула оновлення O(1)
    bx, by = 540, 120
    f.append(text(bx, by, "Один вхідний відлік — один рух:", size=13, color=INK,
                  bold=True, anchor="start"))
    steps = [
        ("running_sum −= buf[head]", NEG, "прибрати найстаріший (2048)"),
        ("running_sum += new",       POS, "додати новий (2054)"),
        ("buf[head] = new",          INK, "перезаписати комірку"),
        ("head = (head+1) & 7",      INK, "зсунути голову по колу"),
    ]
    yy = by + 34
    for code, col, note in steps:
        f.append(rect(bx, yy - 16, 230, 26, fill=FILL, stroke=col, sw=1.6, rx=4))
        f.append(text(bx + 8, yy + 2, code, size=12, color=col, anchor="start"))
        f.append(text(bx + 8, yy + 22, note, size=10.5, color=MUTED, anchor="start"))
        yy += 48
    f.append(fitbox(bx, yy + 2, 230, 50,
                    "Ціна оновлення НЕ залежить від K:\nзавжди 2 додавання, а не K",
                    size=12, pad=8, fill="#eafaf1", stroke=FIELD, color=INK))
    f.append(text(W / 2, H - 16,
                  "Кільце: голова біжить по колу, найстаріший відлік «випадає» саме там, де вписуємо новий",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "ring.svg"), W, H, *f)


# ── 5. Крива спадної віддачі: біти від кратності (вісь стиснута, log) ────────
def fig_gain_curve():
    W, H = 800, 400
    f = []
    x0, y0 = 78, 40
    plotW, plotH = 648, 288
    baseY = y0 + plotH
    kexp_max = 12          # 2^12 = 4096, вісь у степенях двійки (log2 K)
    bits_max = 6.0
    def X(kexp):  return x0 + kexp / kexp_max * plotW
    def Y(bits):  return baseY - bits / bits_max * plotH

    f.append(line(x0, baseY, x0 + plotW, baseY, color=INK, sw=2))
    f.append(line(x0, baseY, x0, y0, color=INK, sw=2))
    f.append(arrow(x0 + plotW - 2, baseY, x0 + plotW + 16, baseY, color=INK, sw=2))
    f.append(arrow(x0, y0 + 2, x0, y0 - 16, color=INK, sw=2))
    f.append(text(x0 + plotW / 2, baseY + 46,
                  "у скільки разів частіше знімаємо (K, вісь стиснута)", size=12, color=MUTED))

    for b in range(0, 7):
        yy = Y(b)
        f.append(line(x0, yy, x0 + plotW, yy, color="#eceff3", sw=1))
        f.append(text(x0 - 10, yy + 4, "+%d" % b, size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 20, y0 - 8, "додано біт", size=12, color=MUTED, anchor="start"))
    for kexp, lab in [(0, "1"), (2, "4"), (4, "16"), (6, "64"),
                      (8, "256"), (10, "1024"), (12, "4096")]:
        xx = X(kexp)
        f.append(line(xx, baseY, xx, baseY + 6, color=INK, sw=1.5))
        f.append(text(xx, baseY + 22, "×" + lab, size=11, color=MUTED))

    # ідеальна пряма на стиснутій осі: bits = 0.5·log2(K); нахил 0.5 по kexp
    pts = [(X(k), Y(k * 0.5)) for k in range(0, kexp_max + 1)]
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, FIELD))
    for kexp in (2, 4, 6, 8):
        f.append(circle(X(kexp), Y(kexp * 0.5), 4.5, fill=FIELD, stroke=FIELD))

    f.append(text(X(2.7), Y(1.15) + 2, "перший біт — ×4,", size=11, color=INK, anchor="start"))
    f.append(text(X(2.7), Y(1.15) + 17, "четвертий — аж ×256", size=11, color=INK, anchor="start"))
    f.append(fitbox(x0 + plotW - 250, y0 + 4, 246, 54,
                    "На стиснутій осі — пряма.\nЗа самим K це √K:\nвіддача спадна.",
                    size=12, pad=8, fill="#eafaf1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "gain-curve.svg"), W, H, *f)


# ── 6. Шумова підлога: кожне ×4 опускає її рівно на 6 дБ (= +1 біт) ──────────
def fig_floor():
    W, H = 800, 360
    f = []
    x0, y0 = 74, 44
    plotW, plotH = 606, 246
    baseY = y0 + plotH
    cols = [
        ("×1",  1.0,   "0 дБ",   0),
        ("×4",  0.5,   "−6 дБ",  1),
        ("×16", 0.25,  "−12 дБ", 2),
        ("×64", 0.125, "−18 дБ", 3),
    ]
    n = len(cols)
    slot = plotW / n
    barW = slot * 0.46
    topRef = plotH
    for i, (lab, h_frac, db, added) in enumerate(cols):
        cx = x0 + slot * (i + 0.5)
        bh = topRef * h_frac
        bx = cx - barW / 2
        by = baseY - bh
        f.append(rect(bx, by, barW, bh, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=3))
        f.append(text(cx, baseY + 22, lab, size=13, color=INK, bold=True))
        f.append(text(cx, baseY + 39, "частіше", size=10, color=MUTED))
        f.append(text(cx, by - 10, db, size=12, color=INK, bold=True))
        if added:
            word = "біт" if added == 1 else "біти"
            f.append(text(cx, by - 26, "+%d %s" % (added, word), size=11, color=FIELD, bold=True))
    f.append(line(x0, baseY, x0 + plotW, baseY, color=INK, sw=2))
    f.append(line(x0, baseY, x0, y0, color=INK, sw=2))
    f.append(arrow(x0, y0 + 2, x0, y0 - 16, color=INK, sw=2))
    f.append(text(x0 - 8, y0 - 8, "шум у смузі (діюче)", size=12, color=MUTED, anchor="start"))
    for i in range(n - 1):
        cx1 = x0 + slot * (i + 0.5)
        cx2 = x0 + slot * (i + 1.5)
        y1 = baseY - topRef * cols[i][1]
        y2 = baseY - topRef * cols[i + 1][1]
        f.append(line(cx1, y1, cx2, y1, color=MUTED, sw=1, dash="3,3"))
        f.append(line(cx2, y1, cx2, y2, color=POS, sw=1.4, dash="3,3"))
        f.append(text((cx1 + cx2) / 2 + 22, (y1 + y2) / 2, "÷2", size=11, color=POS, anchor="start"))
    f.append(text(W / 2, H - 14,
                  "Кожне ×4 частоти вдвічі знижує діючий шум у смузі — рівно −6 дБ = +1 біт",
                  size=11, color=INK))
    render(os.path.join(IMG, "floor.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spread()
    fig_chain()
    fig_dither()
    fig_ring()
    fig_gain_curve()
    fig_floor()
    print("figs done")
