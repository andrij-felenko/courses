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


if __name__ == "__main__":
    fig_detect_vs_track()
    fig_predict_search_match()
    fig_appearance_models()
    fig_loss_recapture()
    print("OK: figures written to", OUT)
