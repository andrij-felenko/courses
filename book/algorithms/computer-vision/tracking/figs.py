# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = "#0f172a"   # темне тло «кадру»
BLOB = "#e08a1e"   # ціль (помаранчева пляма)


def _frame(x, y, w, h):
    return rect(x, y, w, h, fill=DARK, stroke=INK, sw=1.2, rx=8)


# ── detect-vs-track: детектор блимає й губить кадр; трекер веде неперервно ──────
# Ідея: детектор рахує кожен кадр з нуля (дорого, рамка блимає, на поганому кадрі
# зникає); трекер веде ту саму ціль і добудовує положення, коли кадр випав.

def fig_detect_vs_track():
    W, H = 820, 380
    p = []
    bw, bh = 124, 84
    xs = [40, 196, 352, 508, 664]
    cx = [x + bw / 2 for x in xs]

    # верхній ряд — ДЕТЕКТОР (кадр 3 губить ціль)
    yd = 78
    p.append(text(40, yd - 14, "ДЕТЕКТОР — кожен кадр з нуля",
                  size=11, color=POS, bold=True, anchor="start"))
    lost = 2  # індекс кадру, де детектор осліп
    for i in range(5):
        p.append(_frame(xs[i], yd, bw, bh))
        if i == lost:
            p.append(text(cx[i], yd + bh / 2 + 4, "✗", size=20, color=POS, bold=True))
            p.append(text(cx[i], yd + bh - 9, "зникла", size=9, color=POS))
        else:
            p.append(circle(cx[i], yd + bh / 2, 11, fill=BLOB, stroke="none", sw=0))
            p.append(rect(cx[i] - 16, yd + bh / 2 - 16, 32, 32,
                          fill="none", stroke=FIELD, sw=2, rx=3))
        p.append(text(cx[i], yd + bh + 15, "кадр %d" % (i + 1), size=9, color=MUTED))

    # нижній ряд — ТРЕКЕР (веде неперервно, кадр 3 — передбачено)
    yt = 222
    p.append(text(40, yt - 14, "ТРЕКЕР — веде вже знайдену ціль",
                  size=11, color=FIELD, bold=True, anchor="start"))
    track = [(cx[i], yt + bh / 2) for i in range(5)]
    p.append('<polyline points="%s" fill="none" stroke="#60a5fa" '
             'stroke-width="1.4" stroke-linejoin="round"/>'
             % " ".join("%.0f,%.0f" % q for q in track))
    for i in range(5):
        p.append(_frame(xs[i], yt, bw, bh))
        p.append(circle(cx[i], yt + bh / 2, 11, fill=BLOB, stroke="none", sw=0))
        if i == lost:
            p.append(rect(cx[i] - 16, yt + bh / 2 - 16, 32, 32, fill="none",
                          stroke=NEG, sw=2, rx=3))
            p.append('<rect x="%.0f" y="%.0f" width="32" height="32" rx="3" '
                     'fill="none" stroke="%s" stroke-width="2" '
                     'stroke-dasharray="4,3"/>' % (cx[i] - 16, yt + bh / 2 - 16, NEG))
            p.append(text(cx[i], yt + bh - 8, "прогноз", size=9, color=NEG, bold=True))
        else:
            p.append(rect(cx[i] - 16, yt + bh / 2 - 16, 32, 32,
                          fill="none", stroke=FIELD, sw=2, rx=3))

    p.append(text(W / 2, H - 22,
                  "Детектор дорогий і блимає; трекер веде ту саму ціль дешевше й неперервно,",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, H - 8,
                  "а коли кадр випав — добудовує положення з руху й не губить.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "detect-vs-track.svg"), W, H, *p,
           title="Виявлення проти трекінгу: знайти раз, далі вести")


# ── predict-search-match: передбачив → шукав у вікні → знайшов → оновив ─────────
# Ідея: трек тримає стан (де + швидкість), передбачає наступне положення, шукає
# ціль лише у малому вікні навколо прогнозу, прив'язує найкращу й оновлює стан.

def fig_predict_search_match():
    W, H = 820, 360
    p = []
    bw, bh = 188, 176
    ys = 92
    xs = [28, 244, 460]
    titles = ["1. ПЕРЕДБАЧИТИ", "2. ШУКАТИ у вікні", "3. ПРИВ'ЯЗАТИ й оновити"]
    cols = [NEG, "#d98a00", FIELD]

    for i in range(3):
        x = xs[i]
        p.append(text(x + bw / 2, ys - 10, titles[i], size=10.5, color=cols[i], bold=True))
        p.append(_frame(x, ys, bw, bh))

    # 1) попереднє положення + вектор швидкості → прогноз
    x = xs[0]
    px0, py0 = x + 44, ys + bh - 50
    ppx, ppy = x + bw - 52, ys + 54
    p.append(circle(px0, py0, 10, fill=BLOB, stroke="none", sw=0))
    p.append(text(px0, py0 + 24, "було", size=9, color="#cbd5e1"))
    p.append(arrow(px0 + 8, py0 - 6, ppx - 8, ppy + 8, color=NEG, sw=2))
    p.append('<circle cx="%.0f" cy="%.0f" r="11" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4,3"/>' % (ppx, ppy, NEG))
    p.append(text(ppx, ppy - 16, "прогноз", size=9, color=NEG, bold=True))
    p.append(text(x + bw / 2, ys + bh + 15, "стан: де + швидкість", size=9, color=MUTED))

    # 2) вікно пошуку навколо прогнозу, кілька кандидатів
    x = xs[1]
    wx, wy = x + bw - 52, ys + 54           # центр вікна = прогноз
    p.append(rect(wx - 38, wy - 34, 76, 68, fill="none", stroke="#d98a00",
                  sw=1.8, rx=4))
    p.append(text(wx, wy - 42, "вікно пошуку", size=9, color="#d98a00", bold=True))
    for dx, dy, r, col in [(-2, 4, 10, BLOB), (-26, -18, 6, "#64748b"),
                           (22, 20, 6, "#64748b")]:
        p.append(circle(wx + dx, wy + dy, r, fill=col, stroke="none", sw=0))
    p.append(text(x + bw / 2, ys + bh + 15, "лише малий клапоть, не весь кадр",
                  size=9, color=MUTED))

    # 3) найкращий збіг прив'язано, стан оновлено
    x = xs[2]
    mx, my = x + bw - 52, ys + 58
    p.append(circle(mx, my, 11, fill=BLOB, stroke="none", sw=0))
    p.append(rect(mx - 16, my - 16, 32, 32, fill="none", stroke=FIELD, sw=2.2, rx=3))
    p.append(line(mx - 7, my, mx + 7, my, color=POS, sw=2))
    p.append(line(mx, my - 7, mx, my + 7, color=POS, sw=2))
    p.append(text(mx, my + 30, "збіг = тут", size=9, color=FIELD, bold=True))
    p.append(text(x + bw / 2, ys + bh + 15, "оновити стан → наступний кадр",
                  size=9, color=MUTED))

    # стрілки між панелями
    for i in range(2):
        p.append(arrow(xs[i] + bw + 2, ys + bh / 2, xs[i + 1] - 4, ys + bh / 2,
                       color=INK, sw=1.7))

    # зворотна петля: оновлений стан годує наступне передбачення
    p.append(line(xs[2] + bw / 2, ys + bh + 26, xs[2] + bw / 2, ys + bh + 40, color=INK, sw=1.5))
    p.append(line(xs[2] + bw / 2, ys + bh + 40, xs[0] + bw / 2, ys + bh + 40, color=INK, sw=1.5))
    p.append(arrow(xs[0] + bw / 2, ys + bh + 40, xs[0] + bw / 2, ys + bh + 26, color=INK, sw=1.5))
    p.append(text(W / 2, ys + bh + 36, "наступний кадр", size=9, color=MUTED, bold=True))

    render(os.path.join(OUT, "predict-search-match.svg"), W, H, *p,
           title="Цикл трекінгу: передбачити → шукати у вікні → прив'язати")


# ── appearance-models: за чим трекер упізнає ту саму ціль ──────────────────────
# Ідея: щоб у вікні впізнати «ту саму» ціль, трекеру треба її образ — клапоть-
# шаблон, гістограма кольору або набір характерних точок (кутів).

def fig_appearance_models():
    W, H = 820, 360
    p = []
    ys = 96
    ph_ = 184
    pw = 244
    xs = [28, 288, 548]
    cols = [NEG, "#d98a00", FIELD]
    heads = ["ШАБЛОН (клапоть)", "ГІСТОГРАМА кольору", "ХАРАКТЕРНІ точки"]

    for i in range(3):
        p.append(rect(xs[i], ys, pw, ph_, fill="#fbfbfd", stroke=cols[i], sw=1.7, rx=12))
        p.append(text(xs[i] + pw / 2, ys + 22, heads[i], size=10.5, color=cols[i], bold=True))

    # 1) шаблон — збережений клапоть, який звіряють зсувами
    x = xs[0]
    ix, iy, iw, ih = x + 26, ys + 40, pw - 52, 96
    p.append(_frame(ix, iy, iw, ih))
    p.append(circle(ix + iw / 2, iy + ih / 2, 22, fill=BLOB, stroke="none", sw=0))
    p.append(rect(ix + iw / 2 - 26, iy + ih / 2 - 26, 52, 52,
                  fill="none", stroke=NEG, sw=2, rx=3))
    p.append(text(x + pw / 2, ys + ph_ - 12, "звіряємо зсувами: де найсхожіше",
                  size=9, color=MUTED))

    # 2) гістограма — стовпчики, пік на кольорі цілі
    x = xs[1]
    gx, gy, gw, gh = x + 30, ys + 52, pw - 60, 78
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.2))
    bars = [0.18, 0.30, 0.92, 0.62, 0.24, 0.14]
    bcols = ["#64748b", "#64748b", BLOB, "#d98a00", "#64748b", "#64748b"]
    bw_ = gw / len(bars) - 6
    for j, (v, c) in enumerate(zip(bars, bcols)):
        bx = gx + 4 + j * (bw_ + 6)
        p.append(rect(bx, gy + gh - v * gh, bw_, v * gh, fill=c, stroke="none", sw=0, rx=2))
    p.append(text(x + pw / 2, gy - 6, "розподіл кольору цілі", size=9, color=MUTED))
    p.append(text(x + pw / 2, ys + ph_ - 12, "шукаємо той самий колір (mean-shift)",
                  size=9, color=MUTED))

    # 3) характерні точки — кути об'єкта, що їх ведуть від кадру до кадру
    x = xs[2]
    ix, iy, iw, ih = x + 26, ys + 40, pw - 52, 96
    p.append(_frame(ix, iy, iw, ih))
    ocx, ocy = ix + iw / 2, iy + ih / 2
    poly = [(ocx - 28, ocy - 18), (ocx + 30, ocy - 22),
            (ocx + 26, ocy + 22), (ocx - 30, ocy + 18)]
    p.append('<polygon points="%s" fill="#1e293b" stroke="#475569" '
             'stroke-width="1.4"/>' % " ".join("%.0f,%.0f" % q for q in poly))
    for qx, qy in poly:
        p.append(circle(qx, qy, 4.5, fill=POS, stroke=BG, sw=1))
    p.append(text(x + pw / 2, ys + ph_ - 12, "ведемо кути потоком (KLT)",
                  size=9, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "Щоб упізнати «ту саму» ціль у вікні, трекеру потрібен її образ: "
                  "клапоть, колір або набір точок.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "appearance-models.svg"), W, H, *p,
           title="Образ цілі: за чим трекер упізнає її в наступному кадрі")


# ── loss-recapture: ціль зникла → вікно росте → детектор перезахоплює ──────────
# Ідея: коли збіг надто слабкий, трек «не певен»; кілька кадрів він тримається на
# чистому прогнозі (вікно росте), а як зайшло задалеко — кличе детектор заново.

def fig_loss_recapture():
    W, H = 820, 360
    p = []
    bw, bh = 150, 120
    ys = 96
    xs = [30, 222, 414, 606]
    cx = [x + bw / 2 for x in xs]
    heads = ["ведемо", "збіг слабкий", "тримаємось на прогнозі", "перезахопили"]
    hcol = [FIELD, "#d98a00", NEG, FIELD]

    for i in range(4):
        p.append(text(cx[i], ys - 10, heads[i], size=9.5, color=hcol[i], bold=True))
        p.append(_frame(xs[i], ys, bw, bh))

    # 1) звичайне ведення
    i = 0
    p.append(circle(cx[i], ys + bh / 2, 13, fill=BLOB, stroke="none", sw=0))
    p.append(rect(cx[i] - 18, ys + bh / 2 - 18, 36, 36, fill="none", stroke=FIELD, sw=2.2, rx=3))

    # 2) ціль за перешкодою — збіг слабкий, вікно трохи більше
    i = 1
    p.append(rect(cx[i] - 10, ys + 16, 32, bh - 32, fill="#334155", stroke="none", sw=0, rx=3))
    p.append(text(cx[i] + 6, ys + bh - 9, "перешкода", size=9, color="#94a3b8", anchor="start"))
    p.append('<rect x="%.0f" y="%.0f" width="48" height="48" rx="4" fill="none" '
             'stroke="%s" stroke-width="2" stroke-dasharray="5,3"/>'
             % (cx[i] - 24, ys + bh / 2 - 24, "#d98a00"))
    p.append(text(cx[i], ys + bh / 2 + 4, "?", size=18, color="#d98a00", bold=True))

    # 3) тримаємось на прогнозі — вікно росте
    i = 2
    p.append('<circle cx="%.0f" cy="%.0f" r="12" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4,3"/>' % (cx[i], ys + bh / 2, NEG))
    p.append('<rect x="%.0f" y="%.0f" width="92" height="80" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.8" stroke-dasharray="6,4"/>'
             % (cx[i] - 46, ys + bh / 2 - 40, NEG))
    p.append(text(cx[i], ys + bh - 8, "вікно росте", size=9, color=NEG, bold=True))

    # 4) детектор перезахопив — нова рамка
    i = 3
    p.append(circle(cx[i] + 18, ys + bh / 2 + 8, 13, fill=BLOB, stroke="none", sw=0))
    p.append(rect(cx[i] + 18 - 18, ys + bh / 2 + 8 - 18, 36, 36,
                  fill="none", stroke=FIELD, sw=2.4, rx=3))
    p.append(text(cx[i], ys + bh - 8, "детектор знайшов", size=9, color=FIELD, bold=True))

    for i in range(3):
        p.append(arrow(xs[i] + bw + 2, ys + bh / 2, xs[i + 1] - 4, ys + bh / 2,
                       color=INK, sw=1.7))

    p.append(fitbox(40, ys + bh + 34, W - 80, 70,
                    "Поки збіг певний — ведемо легко. Слабшає — кілька кадрів тримаємось на "
                    "прогнозі (вікно росте),\nа як зайшло задалеко — кличемо детектор і "
                    "перезахоплюємо. Так короткий зрив (перешкода, змаз) не\n"
                    "руйнує трек, а довга втрата не лишає його блукати наосліп.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "loss-recapture.svg"), W, H, *p,
           title="Втрата й перезахоплення: коли довіряти прогнозу, а коли шукати заново")


# ── cost-assignment: матриця вартості 1−IoU → оптимальне призначення ────────────
# Ідея: N треків × M детекцій; cost[i][j] = 1 − IoU(pred_i, det_j); вінгерський
# алгоритм добирає по одній парі на рядок/стовпець із найменшою сумарною вартістю.

def fig_cost_assignment():
    W, H = 820, 392
    p = []
    rows = ["трек A", "трек B", "трек C"]
    cols = ["det 1", "det 2", "det 3"]
    cost = [[0.10, 0.80, 0.95],
            [0.90, 0.20, 0.70],
            [0.85, 0.75, 0.15]]
    pick = {(0, 0), (1, 1), (2, 2)}   # оптимальне призначення (діагональ)

    # ── ліворуч: матриця вартості ──
    gx, gy = 96, 92
    cw, ch = 78, 52
    p.append(text(gx + 1.5 * cw, gy - 34, "Матриця вартості  cost = 1 − IoU",
                  size=12, color=INK, bold=True))
    for j, c in enumerate(cols):
        p.append(text(gx + j * cw + cw / 2, gy - 10, c, size=10, color=NEG, bold=True))
    for i, r in enumerate(rows):
        p.append(text(gx - 12, gy + i * ch + ch / 2 + 4, r, size=10, color=POS,
                      bold=True, anchor="end"))
        for j in range(3):
            sel = (i, j) in pick
            fill = "#e8f3ec" if sel else "#fbfbfd"
            stroke = FIELD if sel else "#cbd5e1"
            p.append(rect(gx + j * cw, gy + i * ch, cw - 6, ch - 6,
                          fill=fill, stroke=stroke, sw=2.2 if sel else 1.2, rx=5))
            col = INK if sel else MUTED
            p.append(text(gx + j * cw + (cw - 6) / 2, gy + i * ch + (ch - 6) / 2 + 5,
                          "%.2f" % cost[i][j], size=13, color=col,
                          bold=sel))
    p.append(text(gx + 1.5 * cw, gy + 3 * ch + 14,
                  "менше = краще (більша IoU)", size=9.5, color=MUTED))

    # ── стрілка ──
    p.append(arrow(gx + 3 * cw + 8, gy + 1.5 * ch, gx + 3 * cw + 70, gy + 1.5 * ch,
                   color=INK, sw=2))
    p.append(text(gx + 3 * cw + 39, gy + 1.5 * ch - 12, "Hungarian", size=10,
                  color=INK, bold=True))
    p.append(text(gx + 3 * cw + 39, gy + 1.5 * ch + 22, "min Σ", size=10, color=MUTED))

    # ── праворуч: двочастковий граф призначення ──
    lx = gx + 3 * cw + 110
    rxp = lx + 150
    ys0 = gy + 6
    dy = ch
    for i, r in enumerate(rows):
        p.append(circle(lx, ys0 + i * dy, 16, fill="#fdecec", stroke=POS, sw=1.8))
        p.append(text(lx, ys0 + i * dy + 4, r[-1], size=11, color=POS, bold=True))
    for j, c in enumerate(cols):
        p.append(circle(rxp, ys0 + j * dy, 16, fill="#eaf0fd", stroke=NEG, sw=1.8))
        p.append(text(rxp, ys0 + j * dy + 4, c[-1], size=11, color=NEG, bold=True))
    for (i, j) in sorted(pick):
        p.append(line(lx + 16, ys0 + i * dy, rxp - 16, ys0 + j * dy,
                      color=FIELD, sw=2.6))
        midx = (lx + rxp) / 2
        midy = (ys0 + i * dy + ys0 + j * dy) / 2
        p.append(text(midx, midy - 4, "%.2f" % cost[i][j], size=9, color=FIELD, bold=True))
    p.append(text((lx + rxp) / 2, gy - 10, "оптимальне призначення",
                  size=11, color=FIELD, bold=True))

    p.append(fitbox(40, gy + 3 * ch + 34, W - 80, 56,
                    "Вінгерський алгоритм добирає по одній парі трек↔детекція так, щоб СУМА "
                    "вартостей була найменшою —\nне жадібно (найкращу пару поспіль), а "
                    "глобально: тут діагональ (0.10+0.20+0.15=0.45) дешевша за будь-який інший набір.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "cost-assignment.svg"), W, H, *p,
           title="Прив'язка кількох цілей: матриця вартості → оптимальне призначення")


# ── id-switch: дві цілі перетнулись → треки переплутали номери ──────────────────
# Ідея: коли дві однакові цілі зближуються і їхні рамки сильно перекриваються,
# прив'язка за IoU може віддати детекцію не тому треку — і номери міняються.

def fig_id_switch():
    W, H = 820, 360
    p = []
    fx, fy, fw, fh = 40, 64, W - 80, 210
    p.append(_frame(fx, fy, fw, fh))

    cy = fy + fh / 2
    x0, x1 = fx + 40, fx + fw - 40
    cxm = (x0 + x1) / 2

    # дві траєкторії, що перетинаються в центрі (X)
    def seg(xa, ya, xb, yb, col, dash=None):
        return line(xa, ya, xb, yb, color=col, sw=2.4, dash=dash)

    # справжні шляхи: A йде з верх-ліво вниз-право; B з низ-ліво вгору-право
    p.append(seg(x0, cy - 70, cxm, cy, "#60a5fa"))
    p.append(seg(x0, cy + 70, cxm, cy, "#f59e0b"))
    # ПІСЛЯ перетину номери переплутались: продовження кольорів міняється
    p.append(seg(cxm, cy, x1, cy + 70, "#60a5fa", dash="6,4"))   # A «з'їхав» донизу
    p.append(seg(cxm, cy, x1, cy - 70, "#f59e0b", dash="6,4"))   # B «з'їхав» догори

    # точки-цілі на кінцях
    for (xx, yy, lab, col) in [(x0, cy - 70, "A", NEG), (x0, cy + 70, "B", "#d98a00")]:
        p.append(circle(xx, yy, 13, fill=BLOB, stroke="none", sw=0))
        p.append(text(xx - 22, yy + 4, lab, size=12, color=col, bold=True, anchor="end"))

    # зона зближення
    p.append('<circle cx="%.0f" cy="%.0f" r="40" fill="none" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="3,3"/>' % (cxm, cy, MUTED))
    p.append(text(cxm, cy - 50, "рамки майже збіглись", size=9.5, color=MUTED))

    # кінцеві мітки — номери помінялись
    p.append(circle(x1, cy + 70, 13, fill=BLOB, stroke="none", sw=0))
    p.append(text(x1 + 20, cy + 74, "тепер «A»?", size=10, color=NEG, bold=True, anchor="start"))
    p.append(circle(x1, cy - 70, 13, fill=BLOB, stroke="none", sw=0))
    p.append(text(x1 + 20, cy - 66, "тепер «B»?", size=10, color="#d98a00", bold=True, anchor="start"))

    p.append(text(fx + fw / 2, fy - 12, "ID switch: переплутані номери на перетині",
                  size=12, color=INK, bold=True))

    p.append(fitbox(40, fy + fh + 22, W - 80, 52,
                    "Дві однакові цілі зближуються — прогнози перекриваються так, що IoU не каже, "
                    "котра котра.\nПрив'язка віддає детекцію не тому треку, і після перетину номери "
                    "лишаються переставлені (пунктир).\nРятує лише ознака зовнішності (Re-ID), а не "
                    "сама геометрія.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "id-switch.svg"), W, H, *p,
           title="Пастка ідентичності: підміна номерів при перетині траєкторій")


# ── sort-deepsort: SORT (геометрія) vs DeepSORT (+ ознака зовнішності) ──────────
# Ідея: SORT прив'язує лише за IoU прогнозу й детекції; DeepSORT додає до вартості
# відстань між embedding-ознаками вигляду, тож переживає довгу оклюзію.

def fig_sort_deepsort():
    W, H = 820, 392
    p = []
    colA, colB = "#2457d6", "#16a34a"

    # ── верх: SORT ──
    bx, by, bw2, bh2 = 40, 70, W - 80, 118
    p.append(rect(bx, by, bw2, bh2, fill="#fbfbfd", stroke=colA, sw=1.8, rx=12))
    p.append(text(bx + 16, by + 22, "SORT — лише геометрія", size=12, color=colA,
                  bold=True, anchor="start"))
    steps = ["Калман:\nпрогноз боксів", "IoU(pred, det)\n→ матриця вартості",
             "Hungarian:\nпризначення", "оновити треки\nнародити / вбити"]
    n = len(steps)
    sw_ = (bw2 - 40) / n
    sy = by + 64
    for i, s in enumerate(steps):
        cx = bx + 20 + i * sw_ + sw_ / 2
        bb, ww, hh = textbox(cx, sy, s, size=9.5, fill="#eaf0fd", stroke=colA, sw=1.4,
                             color=INK, pad=8)
        p.append(bb)
        if i < n - 1:
            p.append(arrow(cx + ww / 2 + 2, sy, bx + 20 + (i + 1) * sw_ + sw_ / 2 - ww / 2 - 2,
                           sy, color=INK, sw=1.6))

    # ── низ: DeepSORT ──
    by2 = by + bh2 + 26
    p.append(rect(bx, by2, bw2, bh2, fill="#fbfbfd", stroke=colB, sw=1.8, rx=12))
    p.append(text(bx + 16, by2 + 22, "DeepSORT — геометрія + вигляд (Re-ID)",
                  size=12, color=colB, bold=True, anchor="start"))
    steps2 = ["Калман:\nпрогноз боксів", "+ ознака вигляду\n(embedding)",
              "вартість = відстань\nвигляду ⊕ IoU", "Hungarian +\nпам'ять вигляду"]
    sy2 = by2 + 64
    for i, s in enumerate(steps2):
        cx = bx + 20 + i * sw_ + sw_ / 2
        hot = (i == 1 or i == 2)
        bb, ww, hh = textbox(cx, sy2, s, size=9.5,
                             fill="#dcfce7" if hot else "#eef2f7",
                             stroke=colB if hot else "#94a3b8",
                             sw=1.6 if hot else 1.2, color=INK, pad=8)
        p.append(bb)
        if i < n - 1:
            p.append(arrow(cx + ww / 2 + 2, sy2, bx + 20 + (i + 1) * sw_ + sw_ / 2 - ww / 2 - 2,
                           sy2, color=INK, sw=1.6))

    p.append(fitbox(40, by2 + bh2 + 20, W - 80, 40,
                    "SORT — це Калман + Hungarian + IoU у двох сотнях рядків. DeepSORT додає лиш "
                    "одне: пам'ять про ТЕ, ЯК ціль виглядає,\nтож після довгої оклюзії впізнає її "
                    "за виглядом і повертає той самий номер — там, де гола IoU вже безсила.",
                    size=9.5, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "sort-deepsort.svg"), W, H, *p,
           title="SORT і DeepSORT: що додає ознака зовнішності")


# ── track-lifecycle: народження → проба → підтверджений → смерть ───────────────
# Ідея: трек не вічний; нова детекція родить tentative-трек, min_hits збігів роблять
# його confirmed, max_missed пропусків поспіль його вбивають.

def fig_track_lifecycle():
    W, H = 820, 300
    p = []
    ys = 120
    nodes = [("детекція\nбез пари", "#94a3b8", 110),
             ("проба\n(tentative)", "#d98a00", 300),
             ("підтверджений\n(confirmed)", FIELD, 510),
             ("вбитий\n(deleted)", POS, 712)]
    cxs = []
    for (lab, col, cx) in nodes:
        bb, ww, hh = textbox(cx, ys, lab, size=10.5, fill="#fbfbfd", stroke=col,
                             sw=2, color=INK, pad=11, bold=True)
        p.append(bb)
        cxs.append((cx, ww))

    def edge(a, b, lab, col, up=True):
        (xa, wa), (xb, wb) = cxs[a], cxs[b]
        x1 = xa + wa / 2 + 2
        x2 = xb - wb / 2 - 2
        out = arrow(x1, ys, x2, ys, color=col, sw=1.8)
        out += text((x1 + x2) / 2, ys - 16 if up else ys + 22,
                    lab, size=9, color=col, bold=True)
        return out

    p.append(edge(0, 1, "нова поява", INK))
    p.append(edge(1, 2, "min_hits збігів", FIELD))
    # tentative → deleted (вниз, дугою-міткою)
    (x1c, w1), (x3c, w3) = cxs[1], cxs[3]
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="1.7" stroke-dasharray="5,3" marker-end="url(#arrow)"/>'
             % (x1c, ys + 26, (x1c + x3c) / 2, ys + 96, x3c - 6, ys + 26, POS))
    p.append(text((x1c + x3c) / 2, ys + 92, "проба зірвалась (1 пропуск)",
                  size=9, color=POS, bold=True))
    # confirmed → deleted (вгору)
    (x2c, w2) = cxs[2]
    p.append(arrow(x2c + w2 / 2 + 2, ys - 4, x3c - w3 / 2 - 2, ys - 4, color=POS, sw=1.7))
    p.append(text((x2c + x3c) / 2, ys - 20, "max_missed пропусків", size=9, color=POS, bold=True))
    # confirmed self-loop: збіг продовжує
    p.append('<path d="M %.0f %.0f q 30 -38 60 0" fill="none" stroke="%s" '
             'stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (x2c - 16, ys - 18, FIELD))
    p.append(text(x2c + 18, ys - 44, "збіг → веде далі", size=9, color=FIELD, bold=True))

    p.append(fitbox(40, ys + 110, W - 80, 40,
                    "Детекція без пари родить ПРОБНИЙ трек. Витримав min_hits збігів поспіль — "
                    "стає ПІДТВЕРДЖЕНИМ і йде в вихід.\nПропустив ціль max_missed кадрів поспіль — "
                    "трек убивають. Пробний помирає від першого ж зриву — щоб шум не плодив фантомів.",
                    size=9.5, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "track-lifecycle.svg"), W, H, *p,
           title="Життя і смерть треку: народження → проба → підтвердження → смерть")


# ── kf-tracking-cycle: predict (росте невпевненість) ⇄ update (падає) ───────────
# Ідея: фільтр Калмана для бокс-трекера крутить два кроки — predict зсуває стан за
# моделлю руху й роздуває коваріацію P; update стягує її свіжим виміром.

def fig_kf_tracking_cycle():
    W, H = 760, 300
    p = []
    cyl, cyr = 250, 510
    yb = 118
    # дві коробки-кроки
    bb, w1, h1 = textbox(cyl, yb, "PREDICT\nx ← F·x\nP ← F·P·Fᵀ + Q",
                         size=11, fill="#eaf0fd", stroke=NEG, sw=2, color=INK, pad=14, bold=True)
    p.append(bb)
    bb, w2, h2 = textbox(cyr, yb, "UPDATE\nK = P·Hᵀ(H·P·Hᵀ+R)⁻¹\nx ← x + K(z − H·x)",
                         size=11, fill="#e8f3ec", stroke=FIELD, sw=2, color=INK, pad=14, bold=True)
    p.append(bb)
    # цикл-стрілки
    p.append(arrow(cyl + w1 / 2 + 2, yb - 8, cyr - w2 / 2 - 2, yb - 8, color=INK, sw=1.8))
    p.append(text((cyl + cyr) / 2, yb - 20, "є вимір z (детекція)", size=9.5, color=INK, bold=True))
    p.append(arrow(cyr - w2 / 2 - 2, yb + 8, cyl + w1 / 2 + 2, yb + 8, color=INK, sw=1.8))
    p.append(text((cyl + cyr) / 2, yb + 24, "наступний кадр", size=9.5, color=MUTED))
    # підписи невпевненості
    p.append(text(cyl, yb + h1 / 2 + 22, "невпевненість P росте", size=9.5, color=NEG, bold=True))
    p.append(text(cyr, yb + h2 / 2 + 22, "невпевненість P падає", size=9.5, color=FIELD, bold=True))
    # ліворуч — стан-вектор
    p.append(textbox(120, yb, "стан x =\n[x y vx vy\n w h vw vh]ᵀ",
                     size=10, fill="#fbfbfd", stroke=MUTED, sw=1.4, color=INK, pad=10)[0])
    p.append(arrow(120 + 56, yb, cyl - w1 / 2 - 2, yb, color=MUTED, sw=1.5))

    p.append(fitbox(40, yb + 78, W - 80, 52,
                    "Калман крутить два кроки. PREDICT зсуває бокс за моделлю руху (F) і роздуває "
                    "невпевненість P (+ шум Q).\nUPDATE, коли є детекція z, стягує оцінку до неї, "
                    "важачи прогноз і вимір за їхньою певністю (K, R).\nСліпий кадр — лише predict, "
                    "і P росте, аж доки ціль не виринула.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "kf-tracking-cycle.svg"), W, H, *p,
           title="Калман для бокс-трекера: predict ⇄ update")


# ── history-timeline: оптичний потік (1981) … CAMShift (1998) … SORT / DeepSORT ──
# Ідея: дві старі гілки (точки за рухом vs пляма за кольором) і їхнє злиття у
# сучасні «детектуй-і-веди» трекери.

def fig_history_timeline():
    W, H = 820, 330
    p = []
    y = 168
    x0, x1 = 70, W - 50
    p.append(line(x0, y, x1, y, color=INK, sw=2))
    p.append(arrow(x1 - 2, y, x1 + 0.1, y, color=INK, sw=2))

    marks = [
        (1981, "Лукас–Канаде\nоптичний потік", -1, NEG),
        (1991, "Томасі–Канаде\nякі точки вести (KLT)", 1, NEG),
        (1998, "Бредскі\nCAMShift (колір)", -1, "#d98a00"),
        (2016, "Bewley\nSORT (KF+IoU)", 1, FIELD),
        (2017, "Wojke\nDeepSORT (Re-ID)", -1, FIELD),
    ]
    span = marks[-1][0] - marks[0][0]
    for (yr, lab, side, col) in marks:
        x = x0 + (x1 - x0 - 30) * (yr - marks[0][0]) / span
        p.append(circle(x, y, 7, fill=col, stroke=BG, sw=2))
        p.append(text(x, y + (5 if side < 0 else -10), str(yr), size=11, color=INK,
                      bold=True))
        # підняти/опустити рамку, щоб не налазила на вісь
        ly = y - 50 if side < 0 else y + 52
        bb, ww, hh = textbox(x, ly, lab, size=9.5, fill="#fbfbfd",
                             stroke=col, sw=1.4, color=INK, pad=7)
        p.append(bb)

    # дві гілки-підписи
    p.append(text(x0 + 70, y - 96, "гілка точок: вести рух яскравості",
                  size=10, color=NEG, bold=True, anchor="start"))
    p.append(text(x0 + 70, y + 104, "гілка плями: вести колір",
                  size=10, color="#d98a00", bold=True, anchor="start"))

    p.append(fitbox(40, H - 52, W - 80, 38,
                    "Дві старі ідеї — вести ТОЧКИ за рухом яскравості (Лукас–Канаде) чи ПЛЯМУ "
                    "за кольором (CAMShift) — не зникли.\nSORT і DeepSORT вбудували їх у цикл "
                    "«детектуй зрідка, веди щокадру»: нейромережа дає бокси, Калман і Hungarian — тяглість.",
                    size=9.5, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "history-timeline.svg"), W, H, *p,
           title="Звідки трекінг: від оптичного потоку до SORT і DeepSORT")


if __name__ == "__main__":
    fig_detect_vs_track()
    fig_predict_search_match()
    fig_appearance_models()
    fig_loss_recapture()
    fig_cost_assignment()
    fig_id_switch()
    fig_sort_deepsort()
    fig_track_lifecycle()
    fig_kf_tracking_cycle()
    fig_history_timeline()
    print("OK: figures written to", OUT)
