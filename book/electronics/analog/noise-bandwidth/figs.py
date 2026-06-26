# -*- coding: utf-8 -*-
"""Фігури до статті «Шумова смуга» (noise-bandwidth).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AREA  = "#cfe8d6"   # світло-зелена заливка «площа під кривою»
AREA2 = "#d7e3fb"   # світло-синя заливка цеглини
CURVE = "#c0392b"   # реальна крива (червона)
BRICK = "#2457d6"   # ідеальна цеглина (синя)


# ── 1. Означення: реальна крива і цеглина рівної площі ──────────────────────
def fig_definition():
    W, H = 720, 380
    x0, y0 = 70, 300          # початок осей
    xr, yt = 660, 70          # праві/верхні межі
    plotw, ploth = xr - x0, y0 - yt

    fc = 150.0                # умовна частота зрізу в «одиницях частоти»
    fmax = 600.0
    def X(f): return x0 + plotw * (f / fmax)
    def Y(p): return y0 - ploth * p      # p — потужність 0..1

    # площа під реальною кривою |H|^2 = 1/(1+(f/fc)^2) дорівнює fc*pi/2
    enbw = fc * math.pi / 2.0            # 235.6 → ширина цеглини

    frags = []
    # осі
    frags.append(line(x0, y0, xr, y0, color=INK, sw=2))
    frags.append(line(x0, y0, x0, yt, color=INK, sw=2))
    frags.append(text(xr, y0 + 22, "частота f", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, yt - 4, "|H|²  (частка потужності, що проходить)",
                      size=12, color=MUTED, anchor="start"))

    # ── заливка площі під реальною кривою ──
    pts = ["%.1f,%.1f" % (X(0), Y(0))]
    f = 0.0
    while f <= fmax:
        p = 1.0 / (1.0 + (f / fc) ** 2)
        pts.append("%.1f,%.1f" % (X(f), Y(p)))
        f += 4
    pts.append("%.1f,%.1f" % (X(fmax), Y(0)))
    frags.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.85"/>'
                 % (" ".join(pts), AREA))

    # ── контур цеглини рівної площі (висота 1, ширина = enbw) ──
    bx2 = X(enbw)
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
                 'stroke="%s" stroke-width="2.4" stroke-dasharray="7 4"/>'
                 % (x0, Y(1.0), bx2 - x0, Y(0) - Y(1.0), BRICK))

    # ── сама реальна крива поверх заливки ──
    cpts = []
    f = 0.0
    while f <= fmax:
        p = 1.0 / (1.0 + (f / fc) ** 2)
        cpts.append("%.1f,%.1f" % (X(f), Y(p)))
        f += 4
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(cpts), CURVE))

    # рівень полиці 1.0 і 0.5 (−3 дБ)
    frags.append(line(x0, Y(1.0), bx2, Y(1.0), color=MUTED, sw=1, dash="2 3"))
    frags.append(line(x0, Y(0.5), X(fc), Y(0.5), color=MUTED, sw=1, dash="2 3"))
    frags.append(text(x0 - 8, Y(1.0) + 4, "1.0", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, Y(0.5) + 4, "0.5", size=12, color=MUTED, anchor="end"))

    # позначки частот
    frags.append(line(X(fc), y0, X(fc), y0 + 6, color=INK, sw=1.5))
    frags.append(text(X(fc), y0 + 22, "f₃dB", size=13, color=CURVE, anchor="middle"))
    frags.append(line(bx2, y0, bx2, y0 + 6, color=BRICK, sw=1.5))
    frags.append(text(bx2, y0 + 22, "B_n", size=13, color=BRICK, anchor="middle"))

    # підписи площ
    b1, w1, h1 = textbox(X(70), Y(0.30), "однакова\nплоща",
                         size=13, fill="#ffffff", stroke=MUTED, bold=True)
    frags.append(b1)
    b2, w2, h2 = textbox(X(360), Y(0.78), "ідеальний фільтр\n(цеглина)",
                         size=12, fill="#ffffff", stroke=BRICK, color=NEG)
    frags.append(b2)

    render(os.path.join(IMG, "enbw-def.svg"), W, H, *frags,
           title="Шумова смуга B_n: ширина цеглини рівної площі")


# ── 2. Чому π/2: шум тече за межу −3 дБ ─────────────────────────────────────
def fig_pi_over_2():
    W, H = 720, 360
    x0, y0 = 70, 285
    xr, yt = 660, 70
    plotw, ploth = xr - x0, y0 - yt

    fc = 130.0
    fmax = 620.0
    def X(f): return x0 + plotw * (f / fmax)
    def Y(p): return y0 - ploth * p
    enbw = fc * math.pi / 2.0

    frags = []
    frags.append(line(x0, y0, xr, y0, color=INK, sw=2))
    frags.append(line(x0, y0, x0, yt, color=INK, sw=2))
    frags.append(text(xr, y0 + 22, "частота f", size=13, color=MUTED, anchor="end"))

    # «хвіст» поза f3dB — окрема заливка, щоб показати витік шуму
    tail = ["%.1f,%.1f" % (X(fc), Y(0))]
    f = fc
    while f <= fmax:
        p = 1.0 / (1.0 + (f / fc) ** 2)
        tail.append("%.1f,%.1f" % (X(f), Y(p)))
        f += 4
    tail.append("%.1f,%.1f" % (X(fmax), Y(0)))
    frags.append('<polygon points="%s" fill="#f6d4cf" stroke="none" opacity="0.9"/>'
                 % " ".join(tail))

    # частина до f3dB
    head = ["%.1f,%.1f" % (X(0), Y(0))]
    f = 0.0
    while f <= fc:
        p = 1.0 / (1.0 + (f / fc) ** 2)
        head.append("%.1f,%.1f" % (X(f), Y(p)))
        f += 2
    head.append("%.1f,%.1f" % (X(fc), Y(0)))
    frags.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.85"/>'
                 % (" ".join(head), AREA))

    # крива
    cpts = []
    f = 0.0
    while f <= fmax:
        p = 1.0 / (1.0 + (f / fc) ** 2)
        cpts.append("%.1f,%.1f" % (X(f), Y(p)))
        f += 4
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(cpts), CURVE))

    # цеглина шумової смуги
    bx2 = X(enbw)
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2" stroke-dasharray="7 4"/>'
                 % (x0, Y(1.0), bx2 - x0, Y(0) - Y(1.0), BRICK))

    frags.append(line(x0, Y(0.5), X(fc), Y(0.5), color=MUTED, sw=1, dash="2 3"))
    frags.append(text(x0 - 8, Y(0.5) + 4, "0.5", size=12, color=MUTED, anchor="end"))
    frags.append(line(X(fc), y0, X(fc), Y(0.5), color=MUTED, sw=1, dash="2 3"))
    frags.append(text(X(fc), y0 + 22, "f₃dB", size=13, color=CURVE, anchor="middle"))
    frags.append(text(bx2, y0 + 22, "B_n = (π/2)·f₃dB", size=13, color=BRICK, anchor="middle"))

    b1, w1, h1 = textbox(X(305), Y(0.30), "шум тече\nі за межею",
                         size=12, fill="#ffffff", stroke=CURVE, color=POS, bold=True)
    frags.append(b1)

    render(os.path.join(IMG, "enbw-tail.svg"), W, H, *frags,
           title="Однополюсний спад: чому B_n на 57% ширша за f₃dB")


# ── 3. Множник B_n/f3dB за крутістю спаду ───────────────────────────────────
def fig_orders():
    W, H = 720, 340
    rows = [
        ("1-й (−20 дБ/дек)", 1.57),
        ("2-й (−40 дБ/дек)", 1.22),
        ("3-й (−60 дБ/дек)", 1.15),
        ("4-й (−80 дБ/дек)", 1.13),
        ("цеглина (∞)",      1.00),
    ]
    x0 = 230               # де починаються смужки
    barmaxw = 380          # довжина смужки для множника 1.57
    y = 70
    dy = 48
    scale = barmaxw / 1.57

    frags = []
    frags.append(text(x0 - 12, 50, "порядок фільтра / крутість спаду",
                      size=12, color=MUTED, anchor="end"))
    frags.append(text(x0, 50, "множник  B_n / f₃dB", size=12, color=MUTED, anchor="start"))

    # лінія «1.00» — куди прагне множник
    x_one = x0 + scale * 1.00
    frags.append(line(x_one, 62, x_one, y + dy * len(rows) - 8, color=MUTED, sw=1, dash="3 4"))
    frags.append(text(x_one, y + dy * len(rows) + 6, "1.00", size=11, color=MUTED, anchor="middle"))

    for label, k in rows:
        cy = y + 14
        frags.append(text(x0 - 12, cy + 5, label, size=13, color=INK, anchor="end"))
        col = BRICK if k == 1.00 else CURVE
        bw = scale * k
        frags.append(rect(x0, cy - 10, bw, 28, fill=AREA2 if k == 1.00 else AREA,
                          stroke=col, sw=1.8))
        frags.append(text(x0 + bw + 8, cy + 5, "×%.2f" % k, size=13, color=col,
                          anchor="start", bold=True))
        y += dy

    render(os.path.join(IMG, "enbw-orders.svg"), W, H, *frags,
           title="Що крутіший спад — то ближче шумова смуга до −3 дБ")


if __name__ == "__main__":
    fig_definition()
    fig_pi_over_2()
    fig_orders()
    print("OK: 3 figures written to", IMG)
