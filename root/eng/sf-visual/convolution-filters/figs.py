# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── freq-response: амплітудна характеристика чотирьох ядер ────────────────────
# Ідея: ядро діє на кожну частоту як множник. Гаус/коробка тиснуть високі (ФНЧ),
# Лапласіан їх задирає (ФВЧ), різкість лишає низькі цілими й підсилює високі.
def fig_freq_response():
    W, H = 760, 440
    p = []
    # осі
    ox, oy = 80, 70                 # початок (лівий-верхній кут поля)
    pw, ph = 600, 280              # поле графіка
    base = oy + ph                 # вісь частоти (низ)
    p.append(line(ox, base, ox + pw, base, color=INK, sw=1.6))           # вісь X
    p.append(line(ox, oy - 6, ox, base, color=INK, sw=1.6))              # вісь Y
    # рівень 1.0 (пунктир)
    one_y = base - 0.5 * ph        # 1.0 на половині висоти (шкала 0..2)
    p.append(line(ox, one_y, ox + pw, one_y, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text(ox - 10, one_y + 4, "1", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, base + 4, "0", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy + 4, "2", size=11, color=MUTED, anchor="end"))
    # підписи осей
    p.append(text(ox + pw / 2, base + 30, "просторова частота  (плавне → дрібне)",
                  size=12, color=INK))
    p.append(text(ox + 6, oy - 14, "коеф. пропускання |H|", size=12, color=INK, anchor="start"))

    N = 80
    def curve(fn, color, sw=2.4, dash=None):
        pts = []
        for i in range(N + 1):
            f = i / float(N)                       # частота 0..1
            v = fn(f)
            if v < 0: v = 0.0
            if v > 2.0: v = 2.0
            x = ox + f * pw
            y = base - (v / 2.0) * ph
            pts.append("%.1f,%.1f" % (x, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                 % (" ".join(pts), color, sw, d))

    # криві (схематичні характеристики)
    curve(lambda f: math.exp(-((f / 0.38) ** 2)), FIELD)                  # гаус: гладкий спад
    curve(lambda f: abs(math.sin(math.pi * 2.4 * f) /
                        (math.pi * 2.4 * f)) if f > 1e-6 else 1.0,
          NEG, sw=2.0)                                                    # коробка: sinc із хвилями
    curve(lambda f: 2.0 * (math.sin(math.pi * f / 2) ** 2), POS)         # лапласіан: 0 у нулі, ріст
    curve(lambda f: 1.0 + 0.95 * (math.sin(math.pi * f / 2) ** 2),
          "#8e44ad")                                                      # різкість: 1 + лапласіан

    # легенда (праворуч угорі, у полі)
    lx, ly = ox + pw - 196, oy + 6
    items = [(FIELD, "гаус — ФНЧ (Σ=1)"),
             (NEG,   "коробка — ФНЧ із Гіббсом"),
             (POS,   "Лапласіан — ФВЧ (Σ=0)"),
             ("#8e44ad", "різкість — підсилення (Σ=1)")]
    p.append(rect(lx - 10, ly - 6, 200, 4 + len(items) * 22, fill="#ffffff",
                  stroke=MUTED, sw=1.0, rx=6))
    for i, (c, s) in enumerate(items):
        yy = ly + 12 + i * 22
        p.append(line(lx, yy - 4, lx + 22, yy - 4, color=c, sw=3))
        p.append(text(lx + 30, yy, s, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "freq-response.svg"), W, H, *p,
           title="Ядро як фільтр частот: сума ваг = тип фільтра")


# ── boundary: профілі яскравості біля краю за чотирьох граничних умов ──────────
# Ідея: zero-padding → провал (темна рамка); edge-clamp → поличка; mirror →
# симетричне продовження; wrap → стрибок на чуже значення з протилежного краю.
def fig_boundary():
    W, H = 780, 470
    p = []
    # дані: «справжній» рядок праворуч від краю — плавний підйом ~120..210;
    # ліворуч від краю кожна стратегія підставляє своє.
    edge = 6                       # індекс краю в нашій сітці
    real = [125, 140, 158, 176, 192, 205, 210, 211]   # пікселі від краю вправо
    def real_at(i):                # i>=0
        return real[i] if i < len(real) else real[-1]

    # чотири панелі 2x2
    pw, ph = 330, 150
    gx, gy = 50, 60
    gap_x, gap_y = 60, 70
    cells = [
        ("доповнення нулями", "темна рамка", lambda i: 0 if i < 0 else real_at(i)),
        ("повтор краю", "поличка, лише розмаз", lambda i: real_at(0) if i < 0 else real_at(i)),
        ("дзеркало", "симетричне продовження", lambda i: real_at(-i) if i < 0 else real_at(i)),
        ("загортання", "стрибок на чуже", lambda i: real[len(real) + i] if i < 0 else real_at(i)),
    ]
    cols = ["", ""]
    colors = [POS, FIELD, NEG, "#8e44ad"]

    span = 6                        # скільки відліків ліворуч і праворуч від краю малюємо
    for idx, (name, note, fn) in enumerate(cells):
        r, c = idx // 2, idx % 2
        x0 = gx + c * (pw + gap_x)
        y0 = gy + r * (ph + gap_y)
        col = colors[idx]
        # рамка панелі
        p.append(rect(x0, y0, pw, ph, fill="#fbfbfd", stroke=MUTED, sw=1.0, rx=8))
        p.append(text(x0 + pw / 2, y0 - 8, name, size=12, color=col, bold=True))
        base = y0 + ph - 22
        top = y0 + 14
        # вісь
        p.append(line(x0 + 14, base, x0 + pw - 14, base, color=INK, sw=1.2))
        # вертикаль краю
        ex = x0 + 14 + (span) / (2.0 * span) * (pw - 28)
        p.append(line(ex, top, ex, base + 4, color=INK, sw=1.4, dash="3,3"))
        p.append(text(ex, base + 16, "край", size=9, color=INK))
        # профіль
        def sy(v):  # яскравість 0..255 → y
            return base - (v / 255.0) * (base - top)
        pts = []
        for k in range(-span, span + 1):
            i = k                                  # k<0 ліворуч краю, k>=0 праворуч
            v = fn(i)
            x = x0 + 14 + (k + span) / (2.0 * span) * (pw - 28)
            pts.append("%.1f,%.1f" % (x, sy(v)))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), col))
        # точки-маркери
        for k in range(-span, span + 1):
            v = fn(k)
            x = x0 + 14 + (k + span) / (2.0 * span) * (pw - 28)
            p.append(circle(x, sy(v), 2.4, fill=col, stroke="none", sw=0))
        p.append(text(x0 + pw / 2, y0 + ph + 16, note, size=10, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Що кожна стратегія підставляє ліворуч від краю — і як це псує (чи ні) розмитий профіль. "
                  "Для розмиття беруть дзеркало або повтор краю.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "boundary.svg"), W, H, *p,
           title="Граничні умови: чим заповнити за краєм кадру")


# ── median-vs-gauss: сольовий шум — гаус мастить, медіана прибирає ─────────────
# Ідея: лінійне розмиття усереднює викид у бліду пляму й мастить межу; медіана
# сортує окіл і викидає викид як крайній елемент — цятки геть, межа ціла.
def fig_median_vs_gauss():
    W, H = 820, 380
    p = []
    bw, bh = 200, 200
    ys = 70
    xs = [40, 310, 580]
    labels = ["зашумлений вхід", "гаусове розмиття", "медіанний фільтр"]
    cols = [INK, NEG, FIELD]

    # детермінований «шум» (без random — стабільний SVG)
    def specks(seed):
        out = []
        v = seed
        for _ in range(26):
            v = (v * 1103515245 + 12345) & 0x7fffffff
            gx = (v >> 4) % 100
            gy = (v >> 11) % 100
            white = ((v >> 18) & 1) == 0
            out.append((gx / 100.0, gy / 100.0, white))
        return out

    sp = specks(7)

    def frame(x, kind):
        # ліва половина світло-сіра, права темно-сіра — різка межа посередині
        p.append(rect(x, ys, bw, bh, fill="#9aa3ad", stroke=INK, sw=1.2, rx=8))
        p.append(rect(x + bw / 2, ys, bw / 2, bh, fill="#3c4450", stroke="none", sw=0))
        # відновити прямий правий кут зрізаного rx справа (косметика)
        if kind == "input":
            for (gx, gy, white) in sp:
                cx = x + 6 + gx * (bw - 12)
                cy = ys + 6 + gy * (bh - 12)
                col = "#ffffff" if white else "#000000"
                p.append(rect(cx, cy, 4, 4, fill=col, stroke="none", sw=0, rx=1))
        elif kind == "gauss":
            # викиди стали блідими плямами (розмазані), межа трохи розмита
            for (gx, gy, white) in sp:
                cx = x + 6 + gx * (bw - 12)
                cy = ys + 6 + gy * (bh - 12)
                col = "#d7dadd" if white else "#5b626c"
                p.append(circle(cx, cy, 4.5, fill=col, stroke="none", sw=0))
            # розмита межа: вузька градієнтна смуга
            for k in range(6):
                t = k / 5.0
                vv = int(0x9a - t * (0x9a - 0x3c))
                p.append(rect(x + bw / 2 - 12 + k * 4, ys, 4, bh,
                              fill="rgb(%d,%d,%d)" % (vv, vv + 6, vv + 14),
                              stroke="none", sw=0))
        elif kind == "median":
            # чисто: викиди зникли, межа різка (нічого не домальовуємо — фон уже чистий)
            pass
        # підпис під кадром
        i = {"input": 0, "gauss": 1, "median": 2}[kind]
        p.append(text(x + bw / 2, ys - 10, labels[i], size=12, color=cols[i], bold=True))

    frame(xs[0], "input")
    frame(xs[1], "gauss")
    frame(xs[2], "median")
    p.append(arrow(xs[0] + bw + 6, ys + bh / 2, xs[1] - 6, ys + bh / 2, color=NEG, sw=1.8))
    p.append(arrow(xs[0] + bw + 6, ys + bh / 2 + 0.1, xs[1] - 6, ys + bh / 2 + 0.1, color=NEG, sw=0.1))
    p.append(arrow(xs[1] + bw + 6, ys + bh / 2, xs[2] - 6, ys + bh / 2, color=FIELD, sw=1.8))

    p.append(text(xs[1] + bw / 2, ys + bh + 18, "цятки бліднуть, та лишаються; межа маститься",
                  size=10, color=MUTED))
    p.append(text(xs[2] + bw / 2, ys + bh + 18, "цятки геть; межа лишається різкою",
                  size=10, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Лінійний фільтр викид розмазує в бліду пляму; нелінійний (медіана) сортує окіл "
                  "і викид просто відкидає.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "median-vs-gauss.svg"), W, H, *p,
           title="Сольовий шум: розмазати чи викинути")


if __name__ == "__main__":
    fig_freq_response()
    fig_boundary()
    fig_median_vs_gauss()
    print("OK: figures written to", OUT)
