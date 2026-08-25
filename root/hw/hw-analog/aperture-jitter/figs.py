# -*- coding: utf-8 -*-
"""Фігури до теми «Апертурна невизначеність (jitter)» (цифрова електроніка / ЦОС).
Дві фігури:
  aperture-basic.svg — зсув моменту вибірки Δt на схилі сигналу дає помилку напруги ΔV
  snr-vs-freq.svg    — стеля SNR від джиттера: похилі прямі −20 дБ/декаду частоти
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: механізм Δt → ΔV на схилі синусоїди ───────────────────────────
def fig_basic():
    W, H = 720, 400
    # осі координат ділянки із сигналом
    x0, y0 = 70, 60          # верх-ліво робочої зони
    ax_w, ax_h = 560, 250
    baseline = y0 + ax_h     # низ (умовний нуль часу-осі не важливий)
    midy = y0 + ax_h / 2     # рівень нуля сигналу

    fr = []
    # осі
    fr.append(line(x0, y0 - 6, x0, baseline + 10, color=MUTED, sw=1.2))          # вісь напруги
    fr.append(line(x0 - 6, midy, x0 + ax_w + 10, midy, color=MUTED, sw=1.2))      # вісь часу (нуль сигналу)
    fr.append(text(x0 - 12, y0 + 4, "V", size=13, color=MUTED, anchor="end"))
    fr.append(text(x0 + ax_w + 8, midy - 8, "t", size=13, color=MUTED, anchor="start"))

    # синусоїда: ставимо крутий ВИСХІДНИЙ перехід через нуль рівно в центрі ділянки,
    # щоб ідеальний момент вибірки припав на найкрутіший схил (макс. крутість → макс. ΔV)
    amp = ax_h * 0.42
    px_ideal = ax_w * 0.42               # трохи лівіше центру — місце для дужки Δt праворуч
    k = 1.15 * math.pi / (ax_w * 0.5)    # кутова частота: ~1.15 періоду на ділянку
    def sig(px):
        return midy - amp * math.sin(k * (px - px_ideal))   # у px_ideal sin=0, схил висхідний
    pts = []
    for i in range(0, ax_w + 1, 4):
        pts.append("%.1f,%.1f" % (x0 + i, sig(i)))
    fr.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
              % (" ".join(pts), INK))

    # ідеальний момент вибірки — на найкрутішому висхідному схилі (тут sig = midy)
    xi = x0 + px_ideal
    yi = sig(px_ideal)
    # зсунутий момент Δt пізніше — сигнал за цей час помітно піднявся
    dpx = 44
    xj = xi + dpx
    yj = sig(px_ideal + dpx)

    # вертикалі моментів
    fr.append(line(xi, y0 - 4, xi, baseline + 6, color=MUTED, sw=1.2, dash="5,4"))
    fr.append(line(xj, y0 - 4, xj, baseline + 6, color=POS, sw=1.6, dash="5,4"))
    # горизонталі напруг
    fr.append(line(x0, yi, xi, yi, color=MUTED, sw=1.0, dash="4,4"))
    fr.append(line(x0, yj, xj, yj, color=POS, sw=1.2, dash="4,4"))

    # точки вибірки
    fr.append(circle(xi, yi, 5, fill=BG, stroke=MUTED, sw=2))
    fr.append(circle(xj, yj, 5, fill="#fdecea", stroke=POS, sw=2))

    # дужка Δt між моментами (зверху)
    ytop = y0 - 2
    fr.append(line(xi, ytop, xj, ytop, color=POS, sw=1.6))
    fr.append(line(xi, ytop - 4, xi, ytop + 4, color=POS, sw=1.6))
    fr.append(line(xj, ytop - 4, xj, ytop + 4, color=POS, sw=1.6))
    fr.append(text((xi + xj) / 2, ytop - 8, "Δt (джиттер)", size=13, color=POS, bold=True))

    # дужка ΔV зліва між напругами
    xleft = x0
    fr.append(line(xleft, yi, xleft, yj, color=POS, sw=2.2))
    fr.append(text(xleft - 10, (yi + yj) / 2 + 4, "ΔV", size=14, color=POS, bold=True, anchor="end"))

    # підписи моментів
    fr.append(text(xi, baseline + 22, "мав узяти тут", size=12, color=MUTED))
    fr.append(text(xj, baseline + 22, "узяв тут", size=12, color=POS, bold=True))

    # рамка-висновок унизу праворуч
    box, bw, bh = textbox(x0 + ax_w - 120, baseline + 40, "крутіший схил → більша ΔV",
                          size=12, fill="#eafaf0", stroke=FIELD, color=INK, pad=9)
    fr.append(box)

    render(os.path.join(IMG, "aperture-basic.svg"), W, H, *fr)


# ── Фігура 2: стеля SNR від джиттера, −20 дБ/декаду ─────────────────────────
def fig_snr():
    W, H = 720, 440
    # межі координат: X = log10(f), Y = SNR дБ
    fx0, fx1 = 3.0, 9.0          # 1 кГц .. 1 ГГц
    sy0, sy1 = 20.0, 120.0       # SNR
    L, R = 90, 660
    T, B = 60, 360
    def X(logf):  return L + (logf - fx0) / (fx1 - fx0) * (R - L)
    def Y(snr):   return B - (snr - sy0) / (sy1 - sy0) * (B - T)

    fr = []
    # рамка осей
    fr.append(line(L, T, L, B, color=MUTED, sw=1.3))
    fr.append(line(L, B, R, B, color=MUTED, sw=1.3))

    # сітка X (декади) з підписами частот
    labels = {3: "1 кГц", 4: "10 к", 5: "100 к", 6: "1 МГц", 7: "10 М", 8: "100 М", 9: "1 ГГц"}
    for d in range(3, 10):
        x = X(d)
        fr.append(line(x, T, x, B, color="#e6e9ee", sw=1.0))
        fr.append(text(x, B + 20, labels[d], size=11, color=MUTED))
    fr.append(text((L + R) / 2, B + 40, "частота сигналу f", size=13, color=INK))

    # сітка Y (SNR) з підписами й правою шкалою розрядів (ENOB ≈ (SNR−1.76)/6.02)
    for snr in range(20, 121, 20):
        y = Y(snr)
        fr.append(line(L, y, R, y, color="#eef1f4", sw=1.0))
        fr.append(text(L - 10, y + 4, "%d" % snr, size=11, color=MUTED, anchor="end"))
        enob = (snr - 1.76) / 6.02
        fr.append(text(R + 10, y + 4, "%.0f біт" % enob, size=10, color=FIELD, anchor="start"))
    fr.append(text(L - 46, (T + B) / 2, "SNR, дБ", size=13, color=INK, anchor="middle"))

    # похилі прямі стелі для кількох рівнів джиттера
    # SNR = -20 log10(2π f tj)  →  у координатах logf лінія з нахилом -20 дБ/декаду
    jitters = [(1e-13, "0.1 пс"), (1e-12, "1 пс"), (1e-11, "10 пс"), (1e-10, "100 пс")]
    for tj, lab in jitters:
        def snr_of(logf):
            f = 10 ** logf
            return -20.0 * math.log10(2 * math.pi * f * tj)
        # намалювати відрізок у межах видимого прямокутника
        pts = []
        for k in range(0, 121):
            lf = fx0 + (fx1 - fx0) * k / 120.0
            s = snr_of(lf)
            if sy0 - 5 <= s <= sy1 + 5:
                pts.append((X(lf), Y(max(sy0, min(sy1, s)))))
        if len(pts) >= 2:
            ptstr = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
            fr.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                      % (ptstr, INK))
            # підпис біля лівого кінця лінії
            px, py = pts[0]
            fr.append(text(px + 6, py - 6, "tj = " + lab, size=12, color=INK, bold=True, anchor="start"))

    # зелена стрілка «менше джиттера — вища стеля»
    fr.append(text(R - 8, T + 6, "менше джиттера ↑", size=11, color=FIELD, anchor="end"))
    # похила підказка нахилу
    box = fitbox(X(6.2), Y(46) - 6, 150, 26, "−20 дБ / декаду",
                 size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    fr.append(box)

    render(os.path.join(IMG, "snr-vs-freq.svg"), W, H, *fr)


# ── Фігура 3: три «апертури» на одному фронті (для hist-вставки) ─────────────
def fig_three_apertures():
    W, H = 720, 430
    L, R = 70, 660
    fr = []

    # Верхня доріжка: тактовий фронт (команда «зараз!»)
    clk_y = 70                      # рівень «доріжки такту»
    clk_edge = L + 150              # x, де фронт іде вгору
    fr.append(text(L - 8, clk_y - 22, "такт", size=12, color=MUTED, anchor="start"))
    # низький → високий фронт
    fr.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
              'fill="none" stroke="%s" stroke-width="2.2"/>'
              % (L, clk_y + 26, clk_edge, clk_y + 26, clk_edge, clk_y - 10,
                 R, clk_y - 10, NEG))
    fr.append(text(clk_edge, clk_y - 20, "фронт «зараз!»", size=12, color=NEG, bold=True))

    # Нижня доріжка: стан ключа вибірки (замкнений → розмикається)
    sw_top = 200                    # «замкнено» (стежить)
    sw_bot = 300                    # «розімкнено» (заморозив)
    open_start = clk_edge + 120     # реальне розмикання починається (після затримки)
    open_end = open_start + 46      # закінчується (кінець апертурного вікна)
    fr.append(text(L - 8, sw_top - 22, "ключ", size=12, color=MUTED, anchor="start"))
    # лінія стану: горизонталь угорі, спад-вікно, горизонталь унизу
    fr.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
              'fill="none" stroke="%s" stroke-width="2.4"/>'
              % (L, sw_top, open_start, sw_top, open_end, sw_bot, R, sw_bot, INK))
    fr.append(text(L + 6, sw_top - 8, "замкнений (стежить)", size=11, color=MUTED, anchor="start"))
    fr.append(text(R - 6, sw_bot + 20, "розімкнений (заморозив)", size=11, color=MUTED, anchor="end"))

    # вертикалі-орієнтири: фронт, початок розмикання, кінець вікна
    for xx, col in ((clk_edge, NEG), (open_start, INK), (open_end, INK)):
        fr.append(line(xx, clk_y - 10, xx, sw_bot + 8, color=col, sw=1.0, dash="4,4"))

    # (1) апертурна затримка te: фронт → початок розмикання (стала)
    yb1 = sw_top - 46
    fr.append(line(clk_edge, yb1, open_start, yb1, color=FIELD, sw=2.0))
    fr.append(line(clk_edge, yb1 - 4, clk_edge, yb1 + 4, color=FIELD, sw=2.0))
    fr.append(line(open_start, yb1 - 4, open_start, yb1 + 4, color=FIELD, sw=2.0))
    fr.append(text((clk_edge + open_start) / 2, yb1 - 8,
                   "t_e — затримка (стала)", size=12, color=FIELD, bold=True))

    # (2) апертурний час ta: ширина самого вікна розмикання
    yb2 = sw_bot + 40
    fr.append(line(open_start, yb2, open_end, yb2, color=NEG, sw=2.0))
    fr.append(line(open_start, yb2 - 4, open_start, yb2 + 4, color=NEG, sw=2.0))
    fr.append(line(open_end, yb2 - 4, open_end, yb2 + 4, color=NEG, sw=2.0))
    fr.append(text(open_end + 10, yb2 + 4,
                   "t_a — вікно хапання", size=12, color=NEG, bold=True, anchor="start"))

    # (3) апертурний джиттер tj: розкид миті розмикання від відліку до відліку
    jspread = 26
    # сіра «розмазка» навколо початку розмикання
    fr.append(rect(open_start - jspread / 2, sw_top, jspread, sw_bot - sw_top,
                   fill="#eceff3", stroke="none", sw=0, rx=2))
    # кілька примарних фронтів у смузі
    for off in (-jspread / 2, -jspread / 6, jspread / 6, jspread / 2):
        xs = open_start + off
        fr.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                  'fill="none" stroke="%s" stroke-width="1.2"/>'
                  % (xs - 10, sw_top, xs, sw_top, xs + 36, sw_bot, MUTED))
    # дужка джиттера
    yj = (sw_top + sw_bot) / 2
    fr.append(line(open_start - jspread / 2, yj, open_start + jspread / 2, yj, color=POS, sw=2.2))
    fr.append(text(open_start + jspread / 2 + 8, yj - 6,
                   "t_j — тремтіння", size=12, color=POS, bold=True, anchor="start"))
    fr.append(text(open_start + jspread / 2 + 8, yj + 12,
                   "(лише воно шкодить)", size=11, color=POS, anchor="start"))

    render(os.path.join(IMG, "three-apertures.svg"), W, H, *fr)


if __name__ == "__main__":
    fig_basic()
    fig_snr()
    fig_three_apertures()
    print("OK: aperture-basic.svg, snr-vs-freq.svg, three-apertures.svg")
