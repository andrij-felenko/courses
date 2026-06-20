# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def poisson_pmf(k, lam):
    """P(k) = e^(-lam) * lam^k / k!  — стійко до великих факторіалів через логарифми."""
    if k < 0:
        return 0.0
    log_p = -lam + k * math.log(lam) - math.lgamma(k + 1)
    return math.exp(log_p)


# ── Фігура 1: форма розподілу Пуассона для трьох λ ───────────────────────────

def fig_shapes():
    """Три панелі: малий, середній, великий λ — як горб відходить від нуля й вирівнюється."""
    W, H = 760, 600
    panels = [("λ = 1", 1.0, 8), ("λ = 4", 4.0, 14), ("λ = 10", 10.0, 22)]
    # геометрія панелі
    left = 70
    plot_w = W - left - 30
    ph = 150            # висота області стовпчиків
    gap = 40           # проміжок між панелями (під підпис осі k)
    top0 = 52

    p = []
    for idx, (label, lam, kmax) in enumerate(panels):
        top = top0 + idx * (ph + gap)
        base = top + ph                       # рівень осі k (низ стовпчиків)
        # найбільша ймовірність у панелі — для масштабу висоти
        pmax = max(poisson_pmf(k, lam) for k in range(kmax + 1))
        bw = plot_w / (kmax + 1)              # крок між стовпчиками
        barw = bw * 0.62                      # ширина стовпчика

        # вісь k
        p.append(line(left, base, left + plot_w, base, color=MUTED, sw=1.4))
        # стовпчики
        for k in range(kmax + 1):
            pk = poisson_pmf(k, lam)
            h = pk / pmax * (ph - 10)
            cx = left + (k + 0.5) * bw
            x = cx - barw / 2
            # стовпчик, що сидить на k ≈ λ, виділяємо зеленим
            col = FIELD if abs(k - round(lam)) < 0.5 else NEG
            fillc = "#eafaf1" if col == FIELD else "#eaf0fd"
            p.append(rect(x, base - h, barw, h, fill=fillc, stroke=col, sw=1.4, rx=2))
            # позначки k під віссю — лише парні (щоб не злипались за великого kmax)
            if kmax <= 14 or k % 2 == 0:
                p.append(text(cx, base + 15, str(k), size=10, color=MUTED))

        # підпис панелі (значення λ) у рамці вгорі праворуч — там завжди порожньо
        b, bw2, bh2 = textbox(left + plot_w - 54, top + 14, label, size=13, color=INK, bold=True,
                              fill=BG, stroke=MUTED)
        p.append(b)
        # вертикальна пунктирна риска на середньому k = λ
        cxl = left + (lam + 0.5) * bw
        p.append(line(cxl, base, cxl, top + 4, color=FIELD, sw=1.4, dash="4 4"))
        # підпис осі k праворуч
        p.append(text(left + plot_w + 14, base + 4, "k", size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "poisson-shapes.svg"), W, H, *p,
           title="Один параметр λ задає всю форму: горб стоїть біля k ≈ λ")


# ── Фігура 2: відносна похибка 1/√N спадає зі зростанням N ────────────────────

def fig_sqrt_n_band():
    """Крива відносної похибки 1/√N від числа N (вісь N логарифмічна, щоб декади
    лягли рівно). Три worked-точки: N=100→10 %, 10⁴→1 %, 10⁶→0.1 %.
    Несе головну думку: щоб удесятеро збити похибку, треба устократ більше подій."""
    W, H = 720, 440
    ox, oy = 88, 360          # початок осей (низ-ліво)
    Ax = 560                  # ширина по осі N (лог)
    Ay = 296                  # висота під відносну похибку
    lo_e, hi_e = 1, 7         # межі логарифмічної осі N: 10^1 .. 10^7
    err_top = 32.0            # верх осі похибки у %  (1/√10 ≈ 31.6 %)

    def sx(N):                # N -> екранний x (логарифмічна вісь)
        return ox + (math.log10(N) - lo_e) / (hi_e - lo_e) * Ax

    def sy(err):              # відносна похибка (%) -> екранний y
        return oy - (err / err_top) * Ay

    p = []
    # осі
    p.append(line(ox, oy, ox + Ax + 30, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 12, oy, ox + Ax + 32, oy, color=MUTED, sw=1.4))
    p.append(line(ox, oy + 6, ox, oy - Ay - 22, color=MUTED, sw=1.4))
    p.append(arrow(ox, oy - Ay - 4, ox, oy - Ay - 24, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 30, oy + 22, "N (число подій, лог. шкала)", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - Ay - 10, "відносна похибка 1/√N", size=12, color=MUTED, anchor="start"))

    # сітка декад по осі N з підписами 10², 10⁴, 10⁶ …
    sup = {2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷"}
    for e in range(lo_e, hi_e + 1):
        x = sx(10 ** e)
        p.append(line(x, oy, x, oy - Ay, color="#e8eaed", sw=1.0))
        p.append(line(x, oy - 4, x, oy + 4, color=MUTED, sw=1.2))
        lbl = "10" + sup.get(e, "")
        p.append(text(x, oy + 20, lbl, size=11, color=MUTED))

    # горизонтальні рівні похибки 30/10/3/1/0.3 % з підписами
    for err in [30, 10, 3, 1]:
        y = sy(err)
        p.append(line(ox, y, ox + Ax, y, color="#f0f1f3", sw=1.0))
        p.append(text(ox - 10, y + 4, "%d%%" % err, size=10, color=MUTED, anchor="end"))

    # крива 1/√N у відсотках
    pts = []
    steps = 220
    for i in range(steps + 1):
        e = lo_e + (hi_e - lo_e) * i / steps
        N = 10 ** e
        err = 100.0 / math.sqrt(N)
        pts.append("%.2f,%.2f" % (sx(N), sy(min(err, err_top))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), NEG))

    # три worked-точки з підписами (з тексту статті)
    marks = [(100.0, "10 %", "N=100 → 10 %"),
             (10000.0, "1 %", "N=10⁴ → 1 %"),
             (1000000.0, "0.1 %", "N=10⁶ → 0.1 %")]
    for N, _short, lbl in marks:
        err = 100.0 / math.sqrt(N)
        x, y = sx(N), sy(err)
        # вертикальна пунктирна вниз до осі N
        p.append(line(x, y, x, oy, color=POS, sw=1.2, dash="4 4"))
        p.append(circle(x, y, 4.5, fill="#fdecea", stroke=POS, sw=2.2))

    # підписи-рамки до точок (рознесені по висоті, щоб не налазили один на одного)
    # N=100 — праворуч-угору від точки (точка високо, місця вистачає)
    b1, w1, h1 = textbox(sx(100.0) + 76, sy(10) - 4, "N=100 → 10 %",
                         size=12, color=INK, bold=True, fill=BG, stroke=POS)
    p.append(b1)
    # N=10⁴ — точка коло осі; рамку піднімаємо вище й ведемо тонку лінію-поводок
    bx2, by2 = sx(10000.0), sy(3) - 6
    p.append(line(sx(10000.0), sy(1.0), bx2, by2 + 14, color=POS, sw=1.0, dash="3 3"))
    b2, w2, h2 = textbox(bx2, by2, "N=10⁴ → 1 %",
                         size=12, color=INK, bold=True, fill=BG, stroke=POS)
    p.append(b2)
    # N=10⁶ — точка майже на осі праворуч; рамку — у верхній правий кут із поводком
    bx3, by3 = sx(1000000.0), sy(20)
    p.append(line(sx(1000000.0), sy(0.1), bx3, by3 + 14, color=POS, sw=1.0, dash="3 3"))
    b3, w3, h3 = textbox(bx3, by3, "N=10⁶ → 0.1 %",
                         size=12, color=INK, bold=True, fill=BG, stroke=POS)
    p.append(b3)

    # підказка про квадратичну ціну точності
    b4, w4, h4 = textbox(ox + Ax * 0.5, oy - Ay + 22,
                         "×100 подій  →  ÷10 похибки", size=13, color=NEG, bold=True,
                         fill="#eaf0fd", stroke=NEG)
    p.append(b4)

    render(os.path.join(OUT, "sqrt-n-band.svg"), W, H, *p,
           title="Відносна похибка 1/√N: більше подій — точніше, але ціна квадратична")


if __name__ == "__main__":
    fig_shapes()
    fig_sqrt_n_band()
    print("OK: figures written to", OUT)
