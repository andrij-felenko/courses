# -*- coding: utf-8 -*-
"""Фігури для статті «Втрати перемикання в силових ключах».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── overlap: під час переходу U і I перекриваються → спалах p = U·I ──────────────
# Серце теми. Поза переходом одне з двох нуль (тепла нема); у переході обидва
# відчутні заразом — їхній добуток дає трикутний спалах, площа якого = енергія.
def fig_overlap():
    W, H = 720, 400
    L, R = 80, 660
    T, B = 70, 300
    span = R - L

    def X(f): return L + f * span
    # часова вісь у частках: сталий ВКЛ [0..0.35], перехід [0.35..0.55], сталий ВИМК [0.55..1]
    t0, t1 = 0.35, 0.55
    hi, lo = T + 20, B          # рівні «повного» і «нуля»

    p = []
    # осі
    p.append(line(L, T, L, B, color=INK, sw=2))
    p.append(line(L, B, R + 10, B, color=INK, sw=2))
    p.append(text(R + 6, B + 22, "час →", size=12, color=INK, italic=True, anchor="end"))

    # струм I: повний до переходу, лінійно падає в переході, нуль після
    def I_at(f):
        if f <= t0: return 1.0
        if f >= t1: return 0.0
        return 1.0 - (f - t0) / (t1 - t0)
    # напруга U: нуль до переходу, лінійно росте в переході, повна після
    def U_at(f):
        if f <= t0: return 0.0
        if f >= t1: return 1.0
        return (f - t0) / (t1 - t0)

    def Y(v): return lo + v * (hi - lo)   # v∈[0..1] → від низу вгору

    # дискретизуємо
    fs = [i / 200.0 for i in range(0, 201)]

    # заштрихована зона спалаху p=U·I (полігон під добутком)
    poly = ["%.1f,%.1f" % (X(t0), Y(0))]
    for f in fs:
        if t0 <= f <= t1:
            poly.append("%.1f,%.1f" % (X(f), Y(U_at(f) * I_at(f))))
    poly.append("%.1f,%.1f" % (X(t1), Y(0)))
    p.append('<polygon points="%s" fill="#fbe9e7" stroke="none"/>' % " ".join(poly))

    # крива добутку p = U·I (гаряча)
    pts = ["%.1f,%.1f" % (X(f), Y(U_at(f) * I_at(f))) for f in fs]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    # струм (синій) і напруга (зелений)
    ip = ["%.1f,%.1f" % (X(f), Y(I_at(f))) for f in fs]
    up = ["%.1f,%.1f" % (X(f), Y(U_at(f))) for f in fs]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(ip), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(up), FIELD))

    # межі переходу — пунктир
    p.append(line(X(t0), T, X(t0), B, color=MUTED, sw=1.0, dash="4,4"))
    p.append(line(X(t1), T, X(t1), B, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text((X(t0) + X(t1)) / 2, T + 4, "перехід", size=11, color=MUTED))

    # підписи кривих
    p.append(text(X(0.16), Y(1.0) - 8, "струм I", size=12, color=NEG, bold=True))
    p.append(text(X(0.86), Y(1.0) - 8, "напруга U", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(text(X(0.45), Y(0.30) + 34, "p = U·I", size=12, color=POS, bold=True))

    # підписи станів
    p.append(text(X(0.17), B + 22, "ВКЛ: U≈0", size=11, color=MUTED))
    p.append(text(X(0.80), B + 22, "ВИМК: I=0", size=11, color=MUTED))

    render(os.path.join(OUT, "overlap.svg"), W, H, *p,
           title="Спалах потужності в мить переходу: U і I перекриваються")


# ── on-off: два різні спалахи за цикл — вимикання й вмикання ─────────────────────
# Ідея: за цикл ключ перемикається двічі; вмикання зазвичай гарячіше, бо до
# перекриття U·I додаються розряд Coss і зворотне відновлення діода.
def fig_on_off():
    W, H = 720, 360
    L, R = 80, 660
    base = 260
    span = R - L

    def X(f): return L + f * span
    p = []
    p.append(line(L, base, R + 10, base, color=INK, sw=2))
    p.append(text(R + 6, base + 22, "час →", size=12, color=INK, italic=True, anchor="end"))

    # два «горби» потужності: вимикання (менший) і вмикання (більший, з добавками)
    def hump(fc, w, h, color, fill):
        pts = []
        n = 40
        for i in range(n + 1):
            f = fc - w / 2 + w * i / n
            # трикутний горб
            d = abs(f - fc) / (w / 2)
            y = base - h * (1 - d)
            pts.append((X(f), y))
        poly = " ".join("%.1f,%.1f" % xy for xy in pts)
        poly = "%.1f,%.1f " % (X(fc - w / 2), base) + poly + " %.1f,%.1f" % (X(fc + w / 2), base)
        out = ['<polygon points="%s" fill="%s" stroke="none"/>' % (poly, fill)]
        line_pts = " ".join("%.1f,%.1f" % xy for xy in pts)
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (line_pts, color))
        return out

    # вимикання ~0.28, вмикання ~0.70 (вище)
    p += hump(0.28, 0.14, 90, POS, "#fbe9e7")
    p += hump(0.70, 0.16, 150, POS, "#fbe9e7")

    # підписи
    p.append(text(X(0.28), base - 90 - 14, "вимикання", size=12, color=INK, bold=True))
    p.append(text(X(0.28), base + 22, "перекриття U·I", size=10, color=MUTED))
    p.append(text(X(0.70), base - 150 - 14, "вмикання", size=12, color=INK, bold=True))
    p.append(text(X(0.70), base + 22, "U·I + розряд Coss + Qrr", size=10, color=MUTED))

    # позначки моментів на осі
    for fc, lab in [(0.28, "t₁"), (0.70, "t₂")]:
        p.append(line(X(fc), base, X(fc), base + 6, color=INK, sw=1.2))

    p.append(text(W / 2, H - 16, "площа обох горбів × частота = втрата перемикання",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "on-off.svg"), W, H, *p,
           title="Два спалахи за цикл: вимикання й (гарячіше) вмикання")


# ── coss: заряджена вихідна ємність розряджається в канал при вмиканні ──────────
# Ідея: вимкнений ключ тримає U → Coss заряджена до ½Coss·U²; при вмиканні цей
# запас губиться в каналі щоразу, незалежно від струму, квадратично з напругою.
def fig_coss():
    W, H = 720, 340
    p = []

    # ліворуч: ВИМКНЕНО — ємність заряджена
    lx = 175
    p.append(text(lx, 70, "ВИМКНЕНО", size=14, color=NEG, bold=True))
    # символ ключа (розрив) + паралельна ємність
    p.append(line(lx, 110, lx, 150, color=INK, sw=2.4))          # стік згори
    p.append(line(lx, 190, lx, 230, color=INK, sw=2.4))          # витік знизу
    p.append(line(lx - 22, 158, lx + 22, 158, color=INK, sw=2.4))  # розрив: верхня пластина ключа
    p.append(line(lx - 22, 182, lx + 22, 182, color=INK, sw=2.4))  # нижня
    p.append(text(lx + 34, 174, "ключ", size=11, color=MUTED, anchor="start"))
    # Coss збоку (дві пластини)
    cx = lx + 90
    p.append(line(cx, 110, cx, 152, color=INK, sw=2))
    p.append(line(cx - 18, 152, cx + 18, 152, color=INK, sw=3))
    p.append(line(cx - 18, 168, cx + 18, 168, color=INK, sw=3))
    p.append(line(cx, 168, cx, 230, color=INK, sw=2))
    p.append(line(lx, 110, cx, 110, color=INK, sw=2))
    p.append(line(lx, 230, cx, 230, color=INK, sw=2))
    p.append(plus(cx, 138))
    p.append(minus(cx, 182))
    p.append(text(cx + 26, 160, "Coss", size=12, color=INK, anchor="start", bold=True))
    e1 = fitbox(lx - 60, 250, 200, 46, "заряджена до\nE = ½·Coss·U²", size=12,
                fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    p.append(e1)

    # стрілка переходу
    p.append(arrow(360, 175, 430, 175, color=INK, sw=2.4))
    p.append(text(395, 160, "вмикання", size=11, color=INK, bold=True))

    # праворуч: УВІМКНЕНО — розряд у канал = тепло
    rx = 545
    p.append(text(rx, 70, "УВІМКНЕНО", size=14, color=POS, bold=True))
    # канал (суцільна лінія — замкнено)
    p.append(line(rx, 110, rx, 230, color=FIELD, sw=3))
    p.append(text(rx + 14, 174, "канал", size=11, color=FIELD, anchor="start", bold=True))
    # ємність поруч, стрілка розряду в канал
    cx2 = rx + 90
    p.append(line(cx2, 110, cx2, 152, color=INK, sw=2))
    p.append(line(cx2 - 18, 152, cx2 + 18, 152, color=INK, sw=3))
    p.append(line(cx2 - 18, 168, cx2 + 18, 168, color=INK, sw=3))
    p.append(line(cx2, 168, cx2, 230, color=INK, sw=2))
    p.append(line(rx, 110, cx2, 110, color=INK, sw=2))
    p.append(line(rx, 230, cx2, 230, color=INK, sw=2))
    p.append(arrow(cx2 - 4, 140, rx + 6, 140, color=POS, sw=2))
    e2 = fitbox(rx - 40, 250, 210, 46, "розряд у канал →\nтепло, щоразу", size=12,
                fill="#fbe9e7", stroke=POS, color=POS, bold=True)
    p.append(e2)

    render(os.path.join(OUT, "coss.svg"), W, H, *p,
           title="Вихідна ємність Coss: заряд губиться в каналі при вмиканні")


# ── loss-vs-freq: провідні рівні, перемиканнєві ростуть, сума має компроміс ─────
# Ідея: провідні втрати від частоти не залежать (горизонталь), перемиканнєві
# ростуть лінійно; сума мінімальна не там, де кожна, а на компромісі частоти.
def fig_loss_vs_freq():
    W, H = 720, 420
    L, R = 90, 640
    T, B = 70, 320

    def px(f): return L + f * (R - L)      # f∈[0..1] — нормована частота
    def py(v): return B - v * (B - T)      # v∈[0..1] — нормовані втрати

    p = []
    p.append(line(L, T, L, B, color=INK, sw=2))
    p.append(line(L, B, R, B, color=INK, sw=2))
    p.append(text((L + R) / 2, B + 30, "частота перемикання →", size=12, color=INK, italic=True))
    p.append(text(L - 12, T - 18, "втрати (тепло)", size=12, color=INK, italic=True, anchor="start"))

    # провідні: горизонталь на сталому рівні
    cond = 0.30
    p.append(line(px(0), py(cond), px(1), py(cond), color=FIELD, sw=2.6))
    p.append(text(px(1) - 6, py(cond) - 10, "провідні: I²·Rds(on)", size=12,
                  color=FIELD, bold=True, anchor="end"))

    # перемиканнєві: пряма з нуля вгору (∝ f)
    sw_at = lambda f: 0.85 * f
    p.append(line(px(0), py(0), px(1), py(sw_at(1)), color=POS, sw=2.6))
    p.append(text(px(0.86), py(sw_at(0.86)) + 4, "перемикання ∝ f", size=12,
                  color=POS, bold=True, anchor="end"))

    # сума
    fs = [i / 100.0 for i in range(0, 101)]
    sumpts = ["%.1f,%.1f" % (px(f), py(cond + sw_at(f))) for f in fs]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(sumpts), INK))
    p.append(text(px(0.5), py(cond + sw_at(0.5)) - 14, "сума", size=12, color=INK, bold=True))

    # точка перетину внесків (де перемиканнєві = провідні)
    fx = cond / 0.85
    p.append(line(px(fx), B, px(fx), py(cond), color=MUTED, sw=1.0, dash="4,4"))
    p.append(circle(px(fx), py(cond), 4, fill=INK, stroke=INK))
    p.append(text(px(fx), B + 48, "тут внески рівні:", size=10, color=MUTED))
    p.append(text(px(fx), B + 62, "нижче керує Rds(on), вище — перемикання", size=10, color=MUTED))

    render(os.path.join(OUT, "loss-vs-freq.svg"), W, H, *p,
           title="Провідні втрати проти втрат перемикання від частоти")


if __name__ == "__main__":
    fig_overlap()
    fig_on_off()
    fig_coss()
    fig_loss_vs_freq()
    print("OK: figures written to", OUT)
